from __future__ import annotations

import base64
import json
import os
from pathlib import Path
import shutil
import sqlite3
import threading
from typing import Any, Callable
import uuid

from . import SCHEMA_VERSION
from .agents.base import AgentAdapter, AgentContext
from .canonical import atomic_write_json
from .checks import CheckRunner
from .causal import CausalIndexer
from .config import GlobalConfig
from .core import Core, hash_id
from .environment import safe_environment
from .errors import WorldlineError
from .finalize import Finalizer
from .linux.namespaces import BubblewrapSandbox, CredentialProjection, SandboxSpec
from .linux.netguard import AllowlistProxy, write_forwarder
from .linux.systemd import SystemdAdapter
from .manifest import path_b64
from .model import World, WorldState
from .paths import WorldlinePaths, secure_directory
from .services import ServiceManager
from .project import ProjectConfig
from .store import StateStore


def materialize_private_copies(
    projections: tuple[CredentialProjection, ...], directory: Path
) -> tuple[CredentialProjection, ...]:
    """Replace every private-copy projection with a per-world duplicate under ``directory``.

    The copy is what the sandbox binds writable; the host file is never mounted. SQLite files
    are copied through the backup API so a live WAL is folded into a consistent snapshot.
    """
    if not any(item.private_copy for item in projections):
        return projections
    secure_directory(directory)
    result: list[CredentialProjection] = []
    for index, item in enumerate(projections):
        if not item.private_copy:
            result.append(item)
            continue
        copy = directory / f"{index}-{item.source.name}"
        if copy.exists():
            copy.unlink()
        if _is_sqlite(item.source):
            origin = sqlite3.connect(f"file:{item.source}?mode=ro", uri=True)
            try:
                target = sqlite3.connect(copy)
                try:
                    origin.backup(target)
                finally:
                    target.close()
            finally:
                origin.close()
        else:
            shutil.copyfile(item.source, copy)
        os.chmod(copy, 0o600)
        result.append(CredentialProjection(copy, item.target, private_copy=True))
    return tuple(result)


def _is_sqlite(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            return handle.read(16) == b"SQLite format 3\x00"
    except OSError:
        return False


class AgentRunner:
    def __init__(
        self,
        paths: WorldlinePaths,
        store: StateStore,
        config: GlobalConfig,
        sandbox: BubblewrapSandbox,
        systemd: SystemdAdapter,
        *,
        core: Core | None = None,
    ) -> None:
        self.paths = paths
        self.store = store
        self.config = config
        self.sandbox = sandbox
        self.systemd = systemd
        self.core = core or Core.shared()
        self.checks = CheckRunner(paths, sandbox, systemd)
        self.finalizer = Finalizer(paths, store, sandbox, core=self.core)
        self.services = ServiceManager(paths, store, sandbox, systemd)
        # Job ids the operator asked to cancel. Consulted right after launch (a cancel that
        # arrives while the job is still STARTING has no unit to stop yet) and after the unit
        # exits, so the evidence records USER_CANCELLED instead of an unexplained failure.
        self._cancelled: set[str] = set()
        self._timed_out: set[str] = set()
        self._cancel_lock = threading.Lock()

    def cancel(self, job_id: str, unit: str | None) -> None:
        with self._cancel_lock:
            self._cancelled.add(job_id)
        if unit:
            self.systemd.stop(unit)

    def _was_cancelled(self, job_id: str) -> bool:
        with self._cancel_lock:
            return job_id in self._cancelled

    def _forget_cancel(self, job_id: str) -> None:
        with self._cancel_lock:
            self._cancelled.discard(job_id)

    def run(
        self,
        world_value: str,
        adapter: AgentAdapter,
        mission: str,
        project: ProjectConfig,
        *,
        progress: Callable[[str, dict[str, Any]], None] | None = None,
        low_priority: bool = False,
        timeout: float | None = None,
    ) -> World:
        world = self.store.world(world_value)
        registered = self.store.roots()
        if not registered:
            raise WorldlineError("NO_PRIME", "agent execution requires registered roots")
        base = Path(world.base_payload_path)
        overlay_inputs = [
            (root["root_key"], base / root["root_key"], Path(os.fsdecode(bytes(root["path"]))))
            for root in registered
        ]
        overlays = self.sandbox.overlay_roots(world.instance_id, overlay_inputs)
        primary = next(root for root in registered if root["primary_root"])
        primary_target = Path(os.fsdecode(bytes(primary["path"])))
        runtime = self.paths.overlays / world.instance_id / "agent-runtime"
        secure_directory(runtime)
        mission_path = runtime / "mission.txt"
        mission_path.write_text(mission, encoding="utf-8")
        os.chmod(mission_path, 0o600)
        world_state_path = runtime / "world.json"
        atomic_write_json(world_state_path, world.record())
        context = AgentContext(
            primary_root=primary_target,
            workspace=primary_target,
            mission_file=Path("/run/worldline-runtime/mission.txt"),
            world_state=Path("/run/worldline-runtime/world.json"),
            home=self.paths.home,
            is_git_root=primary["kind"] == "repo",
        )
        argv = adapter.build_argv(context, mission)
        credentials = materialize_private_copies(adapter.credential_mounts(context), runtime / "private-credentials")
        policy = self.config.network_policy
        proxy: AllowlistProxy | None = None
        if policy == "allowlist":
            guard_directory = self.paths.socket.parent / "netguard"
            secure_directory(guard_directory)
            proxy = AllowlistProxy(guard_directory / f"{world.instance_id[:8]}.sock", (*adapter.network_hosts(), *self.config.network_allow))
            write_forwarder(runtime)
            proxy.start()
        spec = SandboxSpec(
            instance_id=world.instance_id,
            argv=argv,
            cwd=primary_target,
            environment=safe_environment(),
            roots=overlays,
            runtime=runtime,
            readonly_home_paths=self.config.readonly_home_paths,
            credential_mounts=credentials,
            operator_home=self.paths.home,
            network=policy,
            netguard_source=None if proxy is None else proxy.socket_path,
        )
        raw_path = self.paths.logs / f"{world.instance_id}.agent.jsonl"
        stderr_path = self.paths.logs / f"{world.instance_id}.agent.stderr"
        job_id = str(uuid.uuid4())
        self.store.create_job(
            job_id=job_id,
            world_instance=world.instance_id,
            state="STARTING",
            raw_event_path=raw_path,
            sandbox={"backend": "overlayfs+bubblewrap", "adapter": adapter.name},
        )
        self.store.append_causal_event(
            {
                "schemaVersion": SCHEMA_VERSION,
                "worldInstance": world.instance_id,
                "kind": "mission",
                "actor": "user",
                "mission": mission,
                "missionHash": world.mission_hash,
            }
        )
        self.store.append_causal_event(
            {
                "schemaVersion": SCHEMA_VERSION,
                "worldInstance": world.instance_id,
                "kind": "agent-invocation",
                "actor": adapter.name,
                "argv": list(argv),
            }
        )
        unit = self.systemd.launch(
            world.instance_id,
            self.sandbox.build_argv(spec),
            description=f"WORLDLINE {world.alias} / {adapter.name}",
            nice=10 if low_priority else None,
        )
        main_pid = unit.pid
        self.store.update_job(
            job_id,
            state="RUNNING",
            systemd_unit=unit.unit,
            pid=main_pid,
        )
        timer: threading.Timer | None = None
        if timeout is not None and timeout > 0:
            def expire() -> None:
                with self._cancel_lock:
                    self._timed_out.add(job_id)
                try:
                    self.systemd.stop(unit.unit)
                except WorldlineError:
                    pass
            timer = threading.Timer(timeout, expire)
            timer.daemon = True
            timer.start()
        if self._was_cancelled(job_id):
            # Cancelled between create_job and launch: the unit exists now, stop it ourselves.
            try:
                self.systemd.stop(unit.unit)
            except WorldlineError:
                pass
        if progress is not None:
            progress("job-started", {"world": world.alias, "jobId": job_id, "unit": unit.unit})
        session_reference: str | None = None
        parsed_events = 0

        def read_stdout() -> None:
            nonlocal session_reference, parsed_events
            assert unit.launcher.stdout is not None
            with open(raw_path, "xb", buffering=0) as raw_stream:
                for line in unit.launcher.stdout:
                    raw_stream.write(line)
                    stripped = line.rstrip(b"\r\n")
                    if not stripped:
                        continue
                    raw_hash = hash_id(self.core.hash_bytes(stripped))
                    try:
                        value = json.loads(stripped.decode("utf-8", "strict"))
                    except (UnicodeError, json.JSONDecodeError):
                        continue
                    if not isinstance(value, dict):
                        continue
                    parsed = adapter.parse_event(value)
                    expansion = parsed.pop("expand", None)
                    pieces = list(expansion) if isinstance(expansion, list) and expansion else [parsed]
                    for piece in pieces:
                        event = {
                            "schemaVersion": SCHEMA_VERSION,
                            "worldInstance": world.instance_id,
                            "kind": piece.pop("kind", "agent-event"),
                            "actor": piece.pop("actor", adapter.name),
                            "rawLineHash": raw_hash,
                            **piece,
                        }
                        self._normalize_path(event, registered, primary)
                        self.store.append_causal_event(event)
                        parsed_events += 1
                        supplied_session = event.get("sessionReference")
                        if isinstance(supplied_session, str):
                            session_reference = supplied_session
                        if progress is not None:
                            progress("agent-event", {"world": world.alias, "event": event})
                raw_stream.flush()
                os.fsync(raw_stream.fileno())

        def read_stderr() -> None:
            assert unit.launcher.stderr is not None
            with open(stderr_path, "xb", buffering=0) as destination:
                shutil.copyfileobj(unit.launcher.stderr, destination)
                destination.flush()
                os.fsync(destination.fileno())

        thread_errors: list[BaseException] = []

        def guarded(target: Callable[[], None]) -> Callable[[], None]:
            def run_guarded() -> None:
                try:
                    target()
                except BaseException as exc:
                    thread_errors.append(exc)
            return run_guarded

        stdout_thread = threading.Thread(target=guarded(read_stdout), name=f"worldline-{world.alias}-stdout")
        stderr_thread = threading.Thread(target=guarded(read_stderr), name=f"worldline-{world.alias}-stderr")
        stdout_thread.start()
        stderr_thread.start()
        assert unit.launcher.stdin is not None
        if adapter.mission_via_stdin:
            unit.launcher.stdin.write(mission.encode("utf-8", "strict"))
        unit.launcher.stdin.close()
        exit_code = unit.launcher.wait()
        stdout_thread.join()
        stderr_thread.join()
        if timer is not None:
            timer.cancel()
        if proxy is not None:
            proxy.stop()
        cancelled = self._was_cancelled(job_id)
        with self._cancel_lock:
            timed_out = job_id in self._timed_out
            self._timed_out.discard(job_id)
        self._forget_cancel(job_id)
        stopped = cancelled or timed_out
        if thread_errors:
            if world.state is WorldState.MUTABLE:
                world.transition(WorldState.DEAD, self.core)
                self.store.save_world(world)
            self.store.update_job(
                job_id,
                state="DEAD",
                error={"type": type(thread_errors[0]).__name__, "message": str(thread_errors[0])},
                ended=True,
            )
            raise thread_errors[0]
        if parsed_events == 0:
            self.store.append_causal_event(
                {
                    "schemaVersion": SCHEMA_VERSION,
                    "worldInstance": world.instance_id,
                    "kind": "agent-invocation-result",
                    "actor": adapter.name,
                    "exitCode": exit_code,
                    "reason": None,
                }
            )
        # What the manager says happened to the unit: structured, bounded, and the only basis
        # for telling a launcher that never got a unit from a workload that ran and failed.
        supervision = self.systemd.outcome(unit, exit_code, stopped=stopped)
        if supervision["kind"] == "LAUNCH_FAILED":
            first = (supervision.get("launcherStderr") or "").strip().splitlines()
            raise WorldlineError(
                "UNIT_LAUNCH_FAILED",
                "the user manager never started the transient unit" + (f": {first[0]}" if first else ""),
                {"unit": unit.unit, "launcherExit": exit_code, "supervision": supervision},
            )
        agent_result = {
            "id": "agent",
            "kind": "build",
            "required": True,
            "format": "exit",
            "covers": [],
            "argv": list(argv),
            "exitCode": exit_code,
            "status": "FAIL" if stopped or supervision["kind"] != "SUPERVISED" else ("PASS" if exit_code == 0 else "FAIL"),
            "rawEventHash": hash_id(self.core.hash_file(raw_path)),
            "stderrHash": hash_id(self.core.hash_file(stderr_path)),
            "network": proxy.summary() if proxy is not None else {"policy": policy},
            "supervision": supervision,
        }
        if cancelled:
            agent_result["reason"] = "USER_CANCELLED: the operator stopped this world before the agent finished"
        elif timed_out:
            agent_result["reason"] = f"TIMEOUT: the agent exceeded the {timeout:g} s limit and was stopped"
        elif supervision["kind"] == "INDETERMINATE":
            agent_result["reason"] = f"SUPERVISION_INDETERMINATE: the manager's journal did not establish that {unit.unit} ran ({supervision['source']})"
        check_results = [agent_result]
        if stopped:
            # The partial work is still materialized so it can be inspected, but running the
            # project's checks against a half-finished tree would manufacture evidence about
            # code nobody claims is done. Report them as not assessed, with the reason.
            check_results.extend(
                {
                    "id": check.id,
                    "kind": check.kind,
                    "required": check.required,
                    "format": check.format,
                    "covers": list(check.covers),
                    "status": "UNASSESSED",
                    "reason": (
                        "not run: world cancelled by the operator before checks"
                        if cancelled else "not run: world timed out before checks"
                    ),
                }
                for check in project.checks
            )
        else:
            check_results.extend(
                self.checks.run(
                    world_instance=world.instance_id,
                    overlays=overlays,
                    primary_target=primary_target,
                    checks=project.checks,
                )
            )
        # Evidence freshness (1.3.0): what this evaluation was bound to. The requirement half is
        # computed from the bytes the world was forked from (its base payload), which is what
        # the checks were defined against; finalize adds the candidate-side verifier hashes.
        from .validation import requirements
        roots = self.store.roots()
        base_sources = {root["root_key"]: Path(world.base_payload_path) / root["root_key"] for root in roots}
        requirement = requirements(project, roots, base_sources, self.config, project.source_sha256, self.core)
        parent = self.store.world(world.parent_instance) if world.parent_instance else None
        validation = {
            "project": project,
            "roots": roots,
            "requirement": requirement,
            "primeAtFork": {"instanceId": world.parent_instance, "contentId": world.parent_content, "generation": self.store.get_meta("primeGeneration") if parent is None else parent.instance_id},
            "adapter": {"name": adapter.name, "argv": list(argv), "sessionReference": session_reference, "supervision": supervision.get("kind") if isinstance(supervision, dict) else None},
        }
        finalized = self.finalizer.finalize(
            world.instance_id,
            overlays,
            check_results=check_results,
            protected=project.protected,
            validation=validation,
            required_checks=("agent", *(check.id for check in project.checks if check.required)),
            agent_manifest={
                "adapter": adapter.name,
                "missionHash": world.mission_hash,
                "sessionReference": session_reference,
                "rawEventHash": agent_result["rawEventHash"],
                "argv": list(argv),
                "systemdUnit": unit.unit,
                "mainPid": main_pid,
                "supervision": supervision,
                "cwd": str(primary_target),
                "generatedClassifiers": [
                    {"root": item.root_key, "glob": item.glob}
                    for item in project.generated
                ],
            },
        )
        if finalized.state is WorldState.VALID:
            self.services.start_declared(finalized, project)
        CausalIndexer(self.store).index(finalized, project)
        self.store.update_job(
            job_id,
            state="CANCELLED" if cancelled else ("TIMED_OUT" if timed_out else finalized.state.value),
            error=(
                {"code": "USER_CANCELLED", "message": "stopped by the operator"} if cancelled
                else {"code": "TIMEOUT", "message": f"exceeded {timeout:g} s", "seconds": int(timeout)} if timed_out
                else None
            ),
            ended=True,
        )
        if progress is not None:
            progress("job-finished", {"world": world.alias, "state": finalized.state.value, "cancelled": cancelled, "timedOut": timed_out})
        return finalized

    @staticmethod
    def _normalize_path(
        event: dict[str, Any],
        roots: list[dict[str, Any]],
        primary: dict[str, Any],
    ) -> None:
        supplied = event.pop("path", None)
        if not isinstance(supplied, str):
            return
        path = Path(supplied)
        if not path.is_absolute():
            path = Path(os.fsdecode(bytes(primary["path"]))) / path
        absolute = path.absolute()
        for root in roots:
            logical = Path(os.fsdecode(bytes(root["path"]))).absolute()
            try:
                relative = absolute.relative_to(logical)
            except ValueError:
                continue
            raw = os.fsencode(relative)
            event["rootKey"] = root["root_key"]
            event["pathB64"] = path_b64(raw)
            event["pathDisplay"] = raw.decode("utf-8", "replace")
            if "line" in event:
                event["lineStart"] = event["line"]
                event["lineEnd"] = event.pop("line")
            return
