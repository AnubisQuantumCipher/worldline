from __future__ import annotations

import base64
import json
import os
from pathlib import Path
import stat
import subprocess
import time
from typing import Any, Sequence
import uuid

from . import SCHEMA_VERSION
from .canonical import atomic_write_json, canonical_bytes
from .core import Core, hash_id
from .environment import evidence_manifest, safe_environment
from .errors import WorldlineError
from .linux.namespaces import BubblewrapSandbox, OverlayRoot, SandboxSpec
from .linux.systemd import SystemdAdapter
from .manifest import Manifest, display_path, path_b64
from .model import World, WorldState
from .paths import WorldlinePaths, secure_directory
from .prime import PrimeManager
from .store import StateStore

_SYSTEM_ROOTS = (Path("/usr"), Path("/etc"), Path("/var"), Path("/opt"), Path("/boot"))
_RUNNER = """
import base64
import json
from pathlib import Path
import subprocess
import sys
import time
specification = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
results = []
for command in specification['commands']:
    started = time.monotonic_ns()
    completed = subprocess.run(command['argv'], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    results.append({
        'id': command['id'],
        'kind': command['kind'],
        'required': command['required'],
        'argv': command['argv'],
        'exitCode': completed.returncode,
        'status': 'PASS' if completed.returncode == 0 else 'FAIL',
        'durationNs': time.monotonic_ns() - started,
        'stdoutB64': base64.b64encode(completed.stdout).decode('ascii'),
        'stderrB64': base64.b64encode(completed.stderr).decode('ascii'),
    })
Path(sys.argv[2]).write_text(json.dumps({'schemaVersion': 1, 'results': results}, sort_keys=True, separators=(',', ':')) + '\\n', encoding='utf-8')
""".strip()


class SystemSimulation:
    def __init__(
        self,
        paths: WorldlinePaths,
        store: StateStore,
        sandbox: BubblewrapSandbox,
        systemd: SystemdAdapter,
        *,
        core: Core | None = None,
    ) -> None:
        self.paths = paths
        self.store = store
        self.sandbox = sandbox
        self.systemd = systemd
        self.core = core or Core.shared()
        self.prime = PrimeManager(paths, store, self.core)

    def run(
        self,
        argv: Sequence[str],
        *,
        health_checks: Sequence[dict[str, Any]] = (),
        alias: str | None = None,
        timeout: int = 1800,
    ) -> World:
        if not argv or any(not isinstance(item, str) or not item for item in argv):
            raise WorldlineError("INVALID_SIMULATION_COMMAND", "simulate requires an exact nonempty argv")
        parent = self.store.prime()
        if parent is None or parent.content_id is None:
            raise WorldlineError("NO_PRIME", "simulate requires an initialized PRIME")
        identifier = str(uuid.uuid4())
        selected_alias = alias or f"future-{identifier[:8]}"
        base = self.paths.worlds / identifier / "base"
        base.mkdir(mode=0o700, parents=True)
        manifests_directory = base / "manifests"
        manifests_directory.mkdir(mode=0o700)
        registered = self.store.roots()
        managed_manifests = []
        managed_overlay_inputs: list[tuple[str, Path, Path]] = []
        for root in registered:
            root_key = root["root_key"]
            logical = bytes(root["path"])
            source = Path(os.fsdecode(os.path.realpath(logical)))
            repository = None
            manifest = Manifest.capture(
                source,
                logical_root=logical,
                root_key=root_key,
                kind=root["kind"],
                core=self.core,
                repository=repository,
            )
            Manifest.materialize(manifest, source, base / root_key, core=self.core)
            manifest.save(manifests_directory / f"{root_key}.json")
            managed_manifests.append(manifest)
            managed_overlay_inputs.append((root_key, base / root_key, Path(os.fsdecode(logical))))
        base_root = Manifest.root_set_hash(managed_manifests, self.core)
        mission_hash = hash_id(self.core.hash_bytes(b"worldline-simulate-v1" + canonical_bytes(list(argv))))
        world = World.create(
            alias=selected_alias,
            parent_instance=parent.instance_id,
            parent_content=parent.content_id,
            cause="Counterfactual execution: " + " ".join(argv),
            actor="system",
            payload_path=self.paths.overlays / identifier,
            base_payload_path=base,
            base_root=base_root,
            root_set_hash=parent.root_set_hash,
            mission_hash=mission_hash,
            world_kind="system",
        )
        world.instance_id = identifier
        self.store.insert_world(world)

        system_inputs = [
            (f"system-{path.name or 'root'}", path, path)
            for path in _SYSTEM_ROOTS
            if path.is_dir()
        ]
        overlays = self.sandbox.overlay_roots(
            identifier,
            [*system_inputs, *managed_overlay_inputs],
            allow_system_roots=True,
        )
        runtime = self.paths.overlays / identifier / "simulation-runtime"
        secure_directory(runtime)
        executable_checks: list[dict[str, Any]] = [
            {"id": "command", "kind": "simulation", "required": True, "argv": list(argv)}
        ]
        unavailable_checks: list[dict[str, Any]] = []
        for check in health_checks:
            if check.get("kind") == "boot":
                unavailable_checks.append(
                    {
                        "id": check["id"],
                        "kind": "boot",
                        "required": bool(check.get("required", False)),
                        "argv": check.get("argv", []),
                        "status": "UNAVAILABLE",
                        "reason": "no configured VM or container backend booted this future",
                    }
                )
            else:
                command = check.get("argv")
                if not isinstance(command, list) or not command or not all(isinstance(item, str) and item for item in command):
                    raise WorldlineError("INVALID_HEALTH_CHECK", f"health check has invalid argv: {check.get('id')}")
                executable_checks.append(
                    {
                        "id": check["id"],
                        "kind": "health",
                        "required": bool(check.get("required", False)),
                        "argv": command,
                    }
                )
        specification_path = runtime / "commands.json"
        result_path = runtime / "results.json"
        atomic_write_json(specification_path, {"schemaVersion": SCHEMA_VERSION, "commands": executable_checks})
        primary = next((root for root in registered if root["primary_root"]), registered[0])
        overlay_by_key = {root.root_key: root for root in overlays}
        spec = SandboxSpec(
            instance_id=identifier,
            argv=(
                "/usr/bin/python3",
                "-c",
                _RUNNER,
                "/run/worldline-runtime/commands.json",
                "/run/worldline-runtime/results.json",
            ),
            cwd=overlay_by_key[primary["root_key"]].target,
            environment=safe_environment(),
            roots=overlays,
            runtime=runtime,
        )
        job_id = str(uuid.uuid4())
        self.store.create_job(
            job_id=job_id,
            world_instance=world.instance_id,
            state="STARTING",
            raw_event_path=result_path,
            sandbox={"backend": "overlayfs+bubblewrap", "kind": "system"},
        )
        unit_process = self.systemd.launch(
            identifier,
            self.sandbox.build_argv(spec),
            description=f"WORLDLINE system future {selected_alias}",
        )
        self.store.update_job(
            job_id,
            state="RUNNING",
            systemd_unit=unit_process.unit,
            pid=unit_process.pid,
        )
        try:
            _stdout, stderr = unit_process.launcher.communicate(timeout=timeout)
            if unit_process.launcher.returncode != 0 or not result_path.is_file():
                raise WorldlineError(
                    "SIMULATION_FAILED",
                    stderr.decode("utf-8", "replace").strip() or f"system future exited {unit_process.launcher.returncode}",
                )
            result = json.loads(result_path.read_text(encoding="utf-8"))
            results = result["results"] + unavailable_checks
            for item in results:
                if "stdoutB64" in item:
                    stdout = base64.b64decode(item["stdoutB64"].encode("ascii"), validate=True)
                    stderr_bytes = base64.b64decode(item["stderrB64"].encode("ascii"), validate=True)
                    item["stdoutHash"] = hash_id(self.core.hash_bytes(stdout))
                    item["stderrHash"] = hash_id(self.core.hash_bytes(stderr_bytes))
            upper_records = [self._upper_record(root) for root in overlays]
            system_delta_root = hash_id(
                self.core.hash_bytes(b"worldline-system-delta-v1" + canonical_bytes(upper_records))
            )
            evidence = evidence_manifest(results, self.core)
            environment_value = {
                "schemaVersion": SCHEMA_VERSION,
                "command": list(argv),
                "results": results,
                "upperRoots": upper_records,
            }
            environment_root = hash_id(
                self.core.hash_bytes(
                    b"worldline-system-environment-v1"
                    + canonical_bytes(environment_value)
                )
            )
            state_directory = Path(world.payload_path) / "manifests"
            state_directory.mkdir(mode=0o700, parents=True, exist_ok=True)
            atomic_write_json(state_directory / "environment.json", environment_value)
            atomic_write_json(state_directory / "evidence.json", evidence)
            atomic_write_json(
                state_directory / "agent.json",
                {"adapter": "system", "argv": list(argv), "sessionReference": None},
            )
            world.components = {
                "filesystem": hash_id(
                    self.core.hash_bytes(
                        b"worldline-system-filesystem-v1"
                        + hash_bytes(parent.components["filesystem"])
                        + hash_bytes(system_delta_root)
                    )
                ),
                "config": parent.components["config"],
                "repository": parent.components["repository"],
                "environment": environment_root,
                "evidence": evidence["root"],
            }
            world.evidence = evidence
            world.delta_hash = system_delta_root
            changed_entries = [
                {"rootKey": record["rootKey"], "path": entry["path"], "op": "SYSTEM_OVERLAY"}
                for record in upper_records
                for entry in record["entries"]
            ]
            world.delta = {
                "added": len(changed_entries),
                "modified": 0,
                "deleted": 0,
                "files": changed_entries,
            }
            world.transition(WorldState.FINALIZING, self.core)
            world.establish_identity(self.core)
            failed = any(item.get("required") and item.get("status") != "PASS" for item in results)
            world.transition(WorldState.DEGRADED if failed else WorldState.VALID, self.core)
            world.risk = "HIGH" if failed else "MEDIUM"
            self.store.save_world(world)
            self.store.update_job(job_id, state=world.state.value, ended=True)
            return world
        except BaseException as exc:
            if world.state is WorldState.MUTABLE:
                world.transition(WorldState.DEAD, self.core)
                world.evidence = {"summary": "FAIL", "checks": [], "error": str(exc)}
                self.store.save_world(world)
            self.store.update_job(
                job_id,
                state="DEAD",
                error={"type": type(exc).__name__, "message": str(exc)},
                ended=True,
            )
            raise

    def _upper_record(self, root: OverlayRoot) -> dict[str, Any]:
        entries: list[dict[str, Any]] = []
        for current, directories, files in os.walk(root.upper, followlinks=False):
            current_path = Path(current)
            for name in sorted([*directories, *files]):
                path = current_path / name
                relative = os.fsencode(path.relative_to(root.upper))
                info = path.lstat()
                entry: dict[str, Any] = {
                    "path": display_path(relative),
                    "pathB64": path_b64(relative),
                    "mode": stat.S_IMODE(info.st_mode),
                }
                if stat.S_ISREG(info.st_mode):
                    entry.update({"type": "file", "hash": hash_id(self.core.hash_file(path))})
                elif stat.S_ISDIR(info.st_mode):
                    entry["type"] = "directory"
                elif stat.S_ISLNK(info.st_mode):
                    entry.update({"type": "symlink", "targetB64": path_b64(os.fsencode(os.readlink(path)))})
                else:
                    entry.update({"type": "overlay-special", "device": info.st_rdev})
                entries.append(entry)
            directories[:] = [name for name in directories if not (current_path / name).is_symlink()]
        entries.sort(key=lambda item: item["pathB64"])
        return {"rootKey": root.root_key, "target": str(root.target), "entries": entries}


def hash_bytes(value: str) -> bytes:
    from .core import hash_bytes_from_id

    return hash_bytes_from_id(value)
