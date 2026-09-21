from __future__ import annotations

import time

import os
from pathlib import Path
import shutil
import stat
import subprocess
from typing import Any, Mapping, Sequence

from .canonical import atomic_write_json
from .core import Core
from .delta import Delta
from .environment import EnvironmentCapture, OwnedProcess, capture_dependencies, evidence_manifest
from .project import protected_matches
from .model import utc_now
from .errors import WorldlineError
from .linux.docker import DockerAdapter
from .linux.git import GitAdapter
from .linux.namespaces import BubblewrapSandbox, OverlayRoot, SandboxSpec
from .manifest import CapturedManifest, Manifest
from .model import World, WorldState
from .paths import WorldlinePaths, secure_directory
from .store import StateStore

_COPY_SCRIPT = """
import os
import subprocess
import shutil
import sys
for index in range(1, len(sys.argv), 2):
    source = sys.argv[index]
    destination = sys.argv[index + 1]
    os.makedirs(destination, mode=0o700, exist_ok=False)
    subprocess.run(['/usr/bin/cp', '--archive', '--reflink=auto', source + '/.', destination], check=True)
    shutil.copystat(source, destination, follow_symlinks=False)
""".strip()


class Finalizer:
    def __init__(
        self,
        paths: WorldlinePaths,
        store: StateStore,
        sandbox: BubblewrapSandbox,
        *,
        core: Core | None = None,
        toolchains: Sequence[str] = (),
    ) -> None:
        self.paths = paths
        self.store = store
        self.sandbox = sandbox
        self.core = core or Core.shared()
        self.toolchains = tuple(toolchains)
        self.environment = EnvironmentCapture(self.core)
        self.git = GitAdapter(self.core)

    def _verify_base(self, manifest: CapturedManifest, source: Path, root_key: str) -> None:
        # The base checkpoint is shared by every sibling and read by several finalizations at
        # once; a transient read failure here used to surface as a bare CORE_IO and kill the
        # world. Retry briefly, then fail by name with the root that could not be verified.
        last: WorldlineError | None = None
        for attempt in range(3):
            try:
                Manifest.verify_content(manifest, source, self.core)
                return
            except WorldlineError as exc:
                last = exc
                if not exc.code.startswith("CORE_"):
                    break
                time.sleep(0.5 * (attempt + 1))
        assert last is not None
        raise WorldlineError(
            "BASE_CHECKPOINT_UNVERIFIED",
            f"the checkpoint this world was forked from could not be verified for root {root_key}: {last.message}",
            {"rootKey": root_key, "base": str(source), "cause": last.as_dict()},
        )

    def finalize(
        self,
        world_value: str,
        overlays: Sequence[OverlayRoot],
        *,
        check_results: Sequence[dict[str, Any]],
        protected: Sequence[str] = (),
        validation: Mapping[str, Any] | None = None,
        required_checks: Sequence[str],
        agent_manifest: dict[str, Any],
    ) -> World:
        world = self.store.world(world_value)
        if world.state is not WorldState.MUTABLE:
            raise WorldlineError("INVALID_TRANSITION", f"finalization requires MUTABLE world, got {world.state.value}")
        world.transition(WorldState.FINALIZING, self.core)
        self.store.save_world(world)
        runtime = self.paths.overlays / world.instance_id / "materializer-runtime"
        secure_directory(runtime)
        materialized = runtime / "materialized"
        if materialized.exists():
            shutil.rmtree(materialized)
        materialized.mkdir(mode=0o700)

        try:
            roots_by_key = {root.root_key: root for root in overlays}
            registered = self.store.roots()
            if set(roots_by_key) != {root["root_key"] for root in registered}:
                raise WorldlineError("ROOT_SET_MISMATCH", "overlay roots do not match registered roots")
            primary = next((root for root in registered if root["primary_root"]), registered[0])
            copy_arguments: list[str] = []
            for root in registered:
                overlay = roots_by_key[root["root_key"]]
                copy_arguments.extend(
                    (
                        str(overlay.target),
                        f"/run/worldline-runtime/materialized/{root['root_key']}",
                    )
                )
            spec = SandboxSpec(
                instance_id=world.instance_id,
                argv=("/usr/bin/python3", "-c", _COPY_SCRIPT, *copy_arguments),
                cwd=roots_by_key[primary["root_key"]].target,
                environment={"PATH": "/usr/bin"},
                roots=tuple(overlays),
                runtime=runtime,
            )
            process = self.sandbox.launch_world(spec)
            _stdout, stderr = process.process.communicate(timeout=300)
            if process.process.returncode != 0:
                raise WorldlineError(
                    "MATERIALIZATION_FAILED",
                    stderr.decode("utf-8", "replace").strip() or f"materializer exited {process.process.returncode}",
                )

            payload = Path(world.payload_path)
            if payload.exists():
                raise WorldlineError("PAYLOAD_EXISTS", f"candidate payload already exists: {payload}")
            payload.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            os.rename(materialized, payload)
            manifests_directory = payload / "manifests"
            manifests_directory.mkdir(mode=0o700)
            candidate_manifests: dict[str, CapturedManifest] = {}
            base_manifests: dict[str, CapturedManifest] = {}
            dependency_roots: list[tuple[str, Path]] = []
            for root in registered:
                root_key = root["root_key"]
                logical = bytes(root["path"])
                candidate_source = payload / root_key
                base_source = Path(world.base_payload_path) / root_key
                repository = self.git.capture(candidate_source) if root["kind"] == "repo" else None
                candidate_manifest = Manifest.capture(
                    candidate_source,
                    logical_root=logical,
                    root_key=root_key,
                    kind=root["kind"],
                    core=self.core,
                    repository=repository,
                )
                base_manifest_path = Path(world.base_payload_path) / "manifests" / f"{root_key}.json"
                if base_manifest_path.is_file():
                    base_manifest = Manifest.load(base_manifest_path, self.core)
                    self._verify_base(base_manifest, base_source, root_key)
                else:
                    base_repository = self.git.capture(base_source) if root["kind"] == "repo" else None
                    base_manifest = Manifest.capture(
                        base_source,
                        logical_root=logical,
                        root_key=root_key,
                        kind=root["kind"],
                        core=self.core,
                        repository=base_repository,
                    )
                candidate_manifest.save(manifests_directory / f"{root_key}.json")
                candidate_manifests[root_key] = candidate_manifest
                base_manifests[root_key] = base_manifest
                dependency_roots.append((root_key, candidate_source))

            base_root = Manifest.root_set_hash(base_manifests.values(), self.core)
            if base_root != world.base_root:
                raise WorldlineError(
                    "BASE_ROOT_MISMATCH",
                    "candidate base checkpoint differs from its claimed base",
                    {"claimed": world.base_root, "actual": base_root},
                )
            delta = Delta.compute_all(base_manifests, candidate_manifests, self.core)
            check_results = list(check_results)
            required_checks = list(required_checks)
            if protected:
                # Engine-enforced: PRIME's policy names the paths and the engine's own delta says
                # whether the candidate changed them; neither is the candidate's to rewrite. The
                # synthetic check is part of the evidence manifest like any other check.
                touched = sorted({op["pathDisplay"] for op in delta.value["operations"] if protected_matches(tuple(protected), op["pathDisplay"])})
                check_results.append(
                    {
                        "id": "protected-paths",
                        "kind": "policy",
                        "required": True,
                        "format": "engine",
                        "covers": list(protected),
                        "status": "FAIL" if touched else "PASS",
                        "touched": touched,
                        "reason": ("the candidate changed protected paths: " + ", ".join(touched)) if touched else "no protected path changed",
                    }
                )
                required_checks.append("protected-paths")
            dependencies = capture_dependencies(dependency_roots, self.core)
            dependency_counts = [item["count"] for item in dependencies]
            dependency_count = (
                sum(dependency_counts)
                if all(isinstance(value, int) for value in dependency_counts)
                else None
            )
            context = None
            if validation is not None:
                # Verifier bytes as they were INSIDE the candidate's tree: a candidate that
                # rewrote its examiner is named here (and refused at prepare) even when the
                # path was not listed as protected.
                from .validation import build_context, resolve_verifiers
                project = validation["project"]
                sources = {root_key: payload / root_key for root_key in [r["root_key"] for r in validation["roots"]]}
                context = build_context(
                    requirement=validation["requirement"],
                    candidate={"instanceId": world.instance_id, "alias": world.alias, "baseRoot": world.base_root, "rootSetHash": world.root_set_hash, "missionHash": world.mission_hash},
                    prime_at_fork=validation["primeAtFork"],
                    roots=validation["roots"],
                    results=check_results,
                    candidate_verifiers=resolve_verifiers(project, validation["roots"], sources),
                    adapter=validation["adapter"],
                    evaluated_at=utc_now(),
                    core=self.core,
                )
            evidence = evidence_manifest(
                check_results,
                self.core,
                validation=context,
                metrics={
                    "dependencyCount": dependency_count,
                    "nonblankSourceLines": self._source_lines(candidate_manifests, payload),
                    "dependencyRecords": dependencies,
                    "generatedClassifiers": agent_manifest.get("generatedClassifiers", []),
                },
            )
            try:
                containers = DockerAdapter(self.core).capture(
                    world.instance_id,
                    world_roots={
                        root_key: source
                        for root_key, source in dependency_roots
                    },
                )
            except WorldlineError as exc:
                containers = [
                    {
                        "state": "UNAVAILABLE",
                        "reason": exc.message,
                    }
                ]
            environment = self.environment.capture(
                processes=[
                    OwnedProcess(
                        pid=agent_manifest.get("mainPid") if isinstance(agent_manifest.get("mainPid"), int) else None,
                        world_instance=world.instance_id,
                        systemd_unit=agent_manifest.get("systemdUnit"),
                        role="agent",
                        argv=tuple(agent_manifest.get("argv", [])),
                        cwd=os.fsencode(agent_manifest.get("cwd", "")),
                    )
                ],
                toolchains=self.toolchains,
                dependency_roots=dependency_roots,
                agent=agent_manifest,
                evidence=evidence,
                workspace=world.workspace,
                containers=containers,
            )
            environment.save(manifests_directory / "environment.json")
            atomic_write_json(manifests_directory / "evidence.json", evidence)
            atomic_write_json(manifests_directory / "agent.json", agent_manifest)
            world.components = {
                **Manifest.component_roots(candidate_manifests.values(), self.core),
                "environment": environment.root_hash,
                "evidence": evidence["root"],
            }
            ghost_objective = world.evidence.get("ghostObjective")
            if isinstance(ghost_objective, str):
                evidence["ghostObjective"] = ghost_objective
            world.evidence = evidence
            world.agent_reference = agent_manifest.get("sessionReference")
            world.delta_hash = delta.delta_hash
            world.delta = {**delta.value["summary"], "files": delta.value["operations"]}
            world.establish_identity(self.core)
            results_by_id = {item.get("id"): item for item in check_results}
            failed_required = [
                check_id
                for check_id in required_checks
                if check_id not in results_by_id or results_by_id[check_id].get("status") != "PASS"
            ]
            world.risk = "HIGH" if failed_required else "MEDIUM"
            world.transition(WorldState.DEGRADED if failed_required else WorldState.VALID, self.core)
            self.store.save_world(world)
            self._make_readonly(payload)
            return world
        except BaseException as exc:
            if world.state is WorldState.FINALIZING:
                error = exc.as_dict() if isinstance(exc, WorldlineError) else {
                    "code": "FINALIZATION_FAILED",
                    "message": f"{type(exc).__name__}: {exc}",
                    "details": {},
                }
                world.evidence = {
                    "summary": "FAIL",
                    "checks": list(check_results),
                    "materializationError": {"type": type(exc).__name__, "message": str(exc)},
                    # One place every surface reads the reason a world is DEAD from.
                    "supervision": error,
                }
                world.transition(WorldState.DEAD, self.core)
                self.store.save_world(world)
            raise

    @staticmethod
    def _source_lines(manifests: Mapping[str, CapturedManifest], payload: Path) -> int:
        extensions = {
            b".adb", b".ads", b".c", b".cc", b".cpp", b".go", b".h", b".hpp",
            b".java", b".js", b".jsx", b".kt", b".py", b".rb", b".rs", b".ts",
            b".tsx",
        }
        count = 0
        for root_key, manifest in manifests.items():
            for relative, entry in manifest.entry_map().items():
                if entry["type"] != "file" or os.path.splitext(relative)[1].lower() not in extensions:
                    continue
                try:
                    text = (payload / root_key / os.fsdecode(relative)).read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    continue
                count += sum(bool(line.strip()) for line in text.splitlines())
        return count

    @staticmethod
    def _make_readonly(payload: Path) -> None:
        for current, directories, files in os.walk(payload, topdown=False, followlinks=False):
            current_path = Path(current)
            for name in files:
                path = current_path / name
                if path.is_symlink():
                    continue
                os.chmod(path, stat.S_IMODE(path.stat().st_mode) & ~0o222)
            for name in directories:
                path = current_path / name
                if path.is_symlink():
                    continue
                os.chmod(path, stat.S_IMODE(path.stat().st_mode) & ~0o222)
        os.chmod(payload, stat.S_IMODE(payload.stat().st_mode) & ~0o222)
