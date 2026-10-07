from __future__ import annotations

import base64
import json
import os
from pathlib import Path
import shutil
import sqlite3
import time
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
from .admission import Gate
from .validation import resolve_verifiers
from .linux.systemd import SystemdAdapter, SystemdProcess
from .manifest import path_b64
from .model import World, WorldState
from .paths import WorldlinePaths, secure_directory
from .services import ServiceManager
from .project import ProjectConfig
from .store import StateStore, reserved_event_claim


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


# Keys only WORLDLINE sets on an agent's event; the agent's own line cannot supply them.
_WORLDLINE_EVENT_KEYS = ("schemaVersion", "worldInstance", "rawLineHash", "origin", "adapter")


def build_agent_event(piece: dict[str, Any], *, world_instance: str, adapter_name: str, raw_hash: str) -> tuple[dict[str, Any], bool]:
    """One causal event from one parsed piece of an agent's stdout (1.9.2, OB-091).

    WORLDLINE's own keys are set AFTER the agent's fields, so the agent cannot supply or override
    them: `origin: "agent"` and the adapter's name mark every field of the event as the agent's
    claim. A piece claiming a reserved actor (worldline, system, user) or a kind only WORLDLINE
    writes is not appended as claimed; the returned event is instead WORLDLINE's record of the
    refusal (second value True), carrying the raw line's hash and what was claimed."""
    piece = dict(piece)
    kind = piece.pop("kind", "agent-event")
    actor = piece.pop("actor", adapter_name)
    for key in _WORLDLINE_EVENT_KEYS:
        piece.pop(key, None)
    event = {"kind": kind, "actor": actor, **piece, "schemaVersion": SCHEMA_VERSION, "worldInstance": world_instance,
             "rawLineHash": raw_hash, "origin": "agent", "adapter": adapter_name}
    refused = reserved_event_claim(event)
    if refused is None:
        return event, False
    return {
        "schemaVersion": SCHEMA_VERSION, "worldInstance": world_instance, "kind": "agent-claim-refused",
        "actor": "worldline", "adapter": adapter_name, "rawLineHash": raw_hash, "reason": refused,
        "claimedActor": actor if isinstance(actor, str) else repr(actor)[:200],
        "claimedKind": kind if isinstance(kind, str) else repr(kind)[:200],
    }, True


class _AgentAcquisition:
    """One primary-preserving cleanup path for this runner's owned workload."""
    def __init__(self, runner, writer, subject):
        self.runner, self.writer, self.subject = runner, writer, subject
        self.proxy = self.guard = self.unit = self.sampling = self.sampler = self.timer = None
        self.proxy_started = self.wait_observed = self.finished = False
        self.exit_code = self.supervision = None
        self.job_id = None
        self.threads = []
        self.thread_errors = []
        self.cleanup_started = False
        self.proxy_closed = False
        self.guard_released = False
        self._sampler_join_attempted = False
        self._stream_joins_attempted = set()
        self._manager_attempted = False
        self._launcher_cleanup_attempted = False
        self._proxy_cleanup_attempted = False
        self._guard_release_attempted = False
        self._ownership_lock = threading.RLock()
        self._unclosed_commands = []
        self._controller_calls = {}
        self._stream_eof = None
        self._streams_closed = False
        self._tail_threads = []
        self._tail_drains_attempted = set()
        self._tail_join_attempted = False
        self._tail_errors = []
        self._tail_observations = []

        # Real writer registration happens before any producer is started.
        # Legacy injected cleanup fixtures keep their original callback API.
        from .finalization_writer import EngineFinalizationWriter
        if isinstance(writer, EngineFinalizationWriter):
            writer._register_agent_acquisition(self)

    def _observe_stream_eof(self, name):
        with self._ownership_lock:
            if self._stream_eof is not None:
                self._stream_eof[name] = True

    def _drain_stream_tail(self, name, stream):
        """Drain the original handle after its reader and outcome callback ended.

        Parsing/progress callbacks are not replayed. Persistence failure is
        sticky in the writer, but must not prevent a finite owned pipe from
        reaching EOF. Available bytes remain owned even if persistence fails.
        """
        from .raw_observation import optional_bytes, exception_observation
        occurrence = 0
        while True:
            try:
                chunk = stream.read(shutil.COPY_BUFSIZE)
            except BaseException as failure:
                with self._ownership_lock:
                    self._tail_errors.append(failure)
                record = {'stream': name, 'readReturned': False,
                    'readReachedEof': False, 'bytes': None,
                    'exception': exception_observation(failure)}
                ended = True
            else:
                ended = chunk == b''
                if ended:
                    self._observe_stream_eof(name)
                record = {'stream': name, 'readReturned': True,
                    'readReachedEof': ended, 'bytes': optional_bytes(chunk),
                    'exception': None}
            with self._ownership_lock:
                self._tail_observations.append(record)
            try:
                self.writer.invocation_raw(world_instance=self.subject,
                    check='agent', kind='agent-stream-tail-read',
                    occurrence=occurrence, observed=record)
            except BaseException as failure:
                with self._ownership_lock:
                    self._tail_errors.append(failure)
            occurrence += 1
            if ended:
                return

    def systemd_call(self, action, *args, cancel_event=None, **kwargs):
        if isinstance(self.runner.systemd, SystemdAdapter):
            def owned(value):
                if value.get('processCreatedObserved') is True and (
                        value.get('processWaitReturnObserved') is not True
                        or value.get('stdoutReachedEof') is not True
                        or value.get('stderrReachedEof') is not True):
                    # A helper's exception return is not proof that its child
                    # and pipe producers ended. Keep the exact identity/facts;
                    # its full output is retained through the raw callback.
                    with self._ownership_lock:
                        self._unclosed_commands.append({key: value.get(key) for key in (
                            'site', 'argv', 'processPidObserved', 'processWaitReturnObserved',
                            'processWaitReturncode', 'stdoutReachedEof', 'stderrReachedEof')})
            def observed(value):
                self.writer.invocation_raw(world_instance=self.subject, check='agent',
                    kind='agent-control-acquisition', observed=value)
            with SystemdAdapter.acquisition_scope(self.runner.systemd, observed,
                    cancel_event=cancel_event, _ownership_observer=owned):
                return action(*args, **kwargs)
        # Preserve an arbitrary injected provider's invocation and side effects.
        # Such a callback is not claimed to be cancellable by the built-in helper.
        return action(*args, **kwargs)

    def controller_call(self, action, unit):
        """Register an active-generation controller query before invoking it.

        No provider is replaced and no controller argument is coerced. Calls
        arriving after capture closure retain their former external semantics;
        their separate lifecycle/serialization obligation remains open.
        """
        from .finalization_writer import EngineFinalizationWriter
        token = None
        if isinstance(self.writer, EngineFinalizationWriter):
            with self.writer.journal.lock:
                if self.writer._acquisition_generation is None:
                    token = str(uuid.uuid4())
                    with self._ownership_lock:
                        self._controller_calls[token] = {'unit': unit, 'kind': 'controller-stop'}
        if token is None:
            return action(unit)
        try:
            return self.systemd_call(action, unit)
        finally:
            with self._ownership_lock:
                self._controller_calls.pop(token)

    def quiescence_observation(self):
        proxy = (self.proxy.quiescence_observation()
                 if isinstance(self.proxy, AllowlistProxy) else None)
        with self._ownership_lock:
            unclosed = list(self._unclosed_commands)
            controllers = list(self._controller_calls.items())
            eof = None if self._stream_eof is None else dict(self._stream_eof)
            tail_errors = [repr(item) for item in self._tail_errors]
        return {'cleanupStarted': self.cleanup_started, 'unclosedCommands': unclosed,
            'activeControllerCalls': controllers,
            'streamEofObserved': eof, 'launcherStreamsClosed': self._streams_closed,
            'launcherWaitObserved': self.wait_observed,
            'launcherPresent': self.unit is not None,
            'timerAlive': self.timer is not None and self.timer.is_alive(),
            'samplerAlive': self.sampler is not None and self.sampler.is_alive(),
            'streams': [{'name': item.name, 'ident': item.ident, 'alive': item.is_alive()}
                        for item in self.threads],
            'tailDrains': [{'name': item.name, 'ident': item.ident, 'alive': item.is_alive()}
                           for item in self._tail_threads],
            'tailErrors': tail_errors,
            'proxyPresent': self.proxy is not None, 'proxyClosed': self.proxy_closed,
            'proxy': proxy, 'guardReleased': self.guard_released}

    def quiescent(self):
        with self._ownership_lock:
            commands_closed = not self._unclosed_commands and not self._controller_calls
            streams_complete = self._stream_eof is None or all(self._stream_eof.values())
        return (commands_closed and self.cleanup_started and (self.unit is None or self.wait_observed)
                and (self.timer is None or not self.timer.is_alive())
                and (self.sampler is None or not self.sampler.is_alive())
                and all(not item.is_alive() for item in self.threads)
                and all(not item.is_alive() for item in self._tail_threads)
                and streams_complete and (self.unit is None or self._streams_closed)
                and (self.proxy is None or
                     (self.proxy_closed and (not isinstance(self.proxy, AllowlistProxy)
                                            or self.proxy.quiescent()))))

    def wait(self):
        result = self.unit.launcher.wait()
        # Own the actual return before persistence can fail. None never stands
        # in for an unobserved process exit.
        self.exit_code, self.wait_observed = result, True
        self.writer.invocation_raw(world_instance=self.subject, check='agent',
            kind='agent-launcher-wait', observed={'unit': self.unit.unit,
                'returncode': result, 'waitReturnObserved': True})
        return result

    def cancel_timer(self):
        if self.timer is not None:
            self.timer.cancel()
            if self.timer.ident is not None:
                self.timer.join()
            self.timer = None

    def finish(self, original=None, *, stopped=False):
        if self.finished and self.quiescent():
            return self.supervision
        self.cleanup_started = True
        error = original
        def record_failure(failure, label):
            nonlocal error
            if error is None:
                error = failure
            elif failure is not error:
                error.add_note(label + ' also failed: ' + repr(failure))
        def attempt(action, label):
            try:
                return action()
            except BaseException as failure:
                record_failure(failure, label)
                return None
        attempt(self.cancel_timer, 'owned timer cleanup')
        if self.unit is not None and not self.wait_observed and not self._launcher_cleanup_attempted:
            self._launcher_cleanup_attempted = True
            attempt(lambda: self.systemd_call(self.runner.systemd.stop, self.unit.unit), 'owned workload stop')
            attempt(self.wait, 'owned launcher wait/acquisition retention')
            stopped = True
        if self.sampling is not None:
            self.sampling.set()
        if self.sampler is not None:
            if not self._sampler_join_attempted:
                self._sampler_join_attempted = True
                attempt(lambda: self.sampler.join(timeout=5), 'owned resource sampler join')
            if self.sampler.is_alive():
                record_failure(WorldlineError('AGENT_ACQUISITION_NOT_QUIESCENT',
                    'the owned sampler remains live after its original bounded join'),
                    'owned resource sampler quiescence')
        for thread in self.threads:
            if thread in self._stream_joins_attempted:
                continue
            self._stream_joins_attempted.add(thread)
            if self.wait_observed:
                attempt(thread.join, 'owned acquisition thread join')
            else:
                attempt(lambda thread=thread: thread.join(timeout=5), 'owned acquisition thread join')
                if thread.is_alive():
                    record_failure(WorldlineError(
                        'AGENT_ACQUISITION_NOT_QUIESCENT',
                        'an owned acquisition thread remains live after an unobserved wait'),
                        'owned acquisition quiescence')
        for failure in self.thread_errors:
            record_failure(failure, 'owned acquisition')
        if self.unit is not None and self.wait_observed and not self._manager_attempted:
            self._manager_attempted = True
            self.supervision = attempt(lambda: self.systemd_call(self.runner.systemd.outcome,
                self.unit, self.exit_code, stopped=stopped,
                _raw_observer=lambda occurrence, record: self.writer.invocation_raw(
                    world_instance=self.subject, check='agent',
                    kind='agent-supervision-acquisition', occurrence=occurrence, observed=record)),
                'manager acquisition')
        if self.unit is not None and self.wait_observed and all(not item.is_alive() for item in self.threads):
            # Outcome above retains its original opportunity to read stderr,
            # through the original stream. Only afterward can recovery consume
            # the remaining tail. A dead reader is never taken as EOF.
            with self._ownership_lock:
                missing_eof = (() if self._stream_eof is None else
                    tuple(name for name, reached in self._stream_eof.items() if not reached))
            for name in missing_eof:
                if name in self._tail_drains_attempted:
                    continue
                self._tail_drains_attempted.add(name)
                stream = getattr(self.unit.launcher, name, None)
                if stream is None:
                    record_failure(WorldlineError('AGENT_ACQUISITION_NOT_QUIESCENT',
                        'the owned stream is absent without an EOF observation', {'stream': name}),
                        'owned stream tail')
                    continue
                thread = threading.Thread(target=self._drain_stream_tail,
                    args=(name, stream), name='worldline-agent-' + name + '-tail', daemon=True)
                self._tail_threads.append(thread)
                attempt(thread.start, 'owned stream tail start')
            if self._tail_threads and not self._tail_join_attempted:
                self._tail_join_attempted = True
                # This bounded recovery grace is separate from, and never
                # extends/repeats, the original sampler join. An OS/descendant
                # pipe which remains blocked stays registered and nonquiescent.
                tail_deadline = time.monotonic() + 5
                for thread in self._tail_threads:
                    if thread.ident is not None:
                        attempt(lambda thread=thread: thread.join(
                            timeout=max(0, tail_deadline - time.monotonic())),
                            'owned stream tail join')
            with self._ownership_lock:
                tail_errors = tuple(self._tail_errors)
            for failure in tail_errors:
                record_failure(failure, 'owned stream tail acquisition')
            with self._ownership_lock:
                eof = self._stream_eof is None or all(self._stream_eof.values())
            if eof and all(not item.is_alive() for item in self._tail_threads):
                # Outcome's last stderr observation happens above. Only ended
                # readers with their actual EOF observation reach this close;
                # closing a live/incomplete producer is not used to invent EOF.
                streams = tuple(getattr(self.unit.launcher, name, None)
                                for name in ('stdin', 'stdout', 'stderr'))
                for stream in streams:
                    if stream is not None:
                        attempt(stream.close, 'owned launcher stream close')
                self._streams_closed = all(stream is None or stream.closed for stream in streams)
        if self.proxy is not None:
            def close_proxy():
                if self.proxy_started or isinstance(self.proxy, AllowlistProxy):
                    self.proxy.stop()
                else:
                    self.proxy.server_close()
                    try:
                        self.proxy.socket_path.unlink()
                    except FileNotFoundError:
                        pass
                self.proxy_closed = True
            if not self._proxy_cleanup_attempted:
                self._proxy_cleanup_attempted = True
                attempt(close_proxy, 'owned proxy cleanup')
            elif isinstance(self.proxy, AllowlistProxy) and self.proxy.quiescent():
                # A previously blocked handler may have actually ended since
                # the retained refusal. Do not repeat the bounded grace or an
                # arbitrary caller's cleanup callback merely because of nesting.
                self.proxy_closed = True
            if isinstance(self.proxy, AllowlistProxy):
                # Retain live/non-live observations even when stop itself
                # refused. No final network result is made from a live handler.
                attempt(lambda: self.writer.invocation_raw(world_instance=self.subject,
                    check='agent', kind='agent-proxy-cleanup',
                    observed=self.proxy.quiescence_observation()), 'owned proxy observation')
        if self.guard is not None:
            if self.quiescent():
                def release_guard():
                    self.guard.release()
                    self.guard_released = True
                if not self.guard_released and not self._guard_release_attempted:
                    self._guard_release_attempted = True
                    attempt(release_guard, 'owned admission release')
            elif error is not None:
                error.add_note('owned admission retained because acquisition is not quiescent')
        self.finished = self.quiescent() and (self.guard is None or self.guard_released)
        if not self.finished and error is None:
            record_failure(WorldlineError('AGENT_ACQUISITION_NOT_QUIESCENT',
                'owned acquisition cleanup remains incomplete', self.quiescence_observation()),
                'owned acquisition quiescence')
        if error is not None:
            raise error
        return self.supervision


class AgentRunner:
    def __init__(
        self,
        paths: WorldlinePaths,
        store: StateStore,
        config: GlobalConfig,
        sandbox: BubblewrapSandbox,
        systemd: SystemdAdapter,
        gate: "Gate",
        *,
        core: Core | None = None,
    ) -> None:
        self.paths = paths
        self.store = store
        self.config = config
        self.sandbox = sandbox
        self.systemd = systemd
        self.core = core or Core.shared()
        self.gate = gate
        self.checks = CheckRunner(paths, sandbox, systemd, gate)
        self.finalizer = Finalizer(paths, store, sandbox, core=self.core)
        self.services = ServiceManager(paths, store, sandbox, systemd, gate)
        # Job ids the operator asked to cancel. Consulted right after launch (a cancel that
        # arrives while the job is still STARTING has no unit to stop yet) and after the unit
        # exits, so the evidence records USER_CANCELLED instead of an unexplained failure.
        self._cancelled: set[str] = set()
        self._timed_out: set[str] = set()
        self._cancel_lock = threading.Lock()
        self._acquisitions_by_job = {}

    def cancel(self, job_id: str, unit: str | None) -> None:
        with self._cancel_lock:
            self._cancelled.add(job_id)
            owner = self._acquisitions_by_job.get(job_id) if type(job_id) is str else None
        if unit:
            # Do not add equality calls to custom identity objects. The owned
            # default job/unit pair is an exact built-in string observation.
            if (owner is not None and type(owner.unit) is SystemdProcess
                    and type(unit) is str and type(owner.unit.unit) is str
                    and owner.unit.unit == unit):
                owner.controller_call(self.systemd.stop, unit)
            else:
                self.systemd.stop(unit)

    def _was_cancelled(self, job_id: str) -> bool:
        with self._cancel_lock:
            return job_id in self._cancelled

    def _forget_cancel(self, job_id: str) -> None:
        with self._cancel_lock:
            self._cancelled.discard(job_id)

    def run(
        self, world_value: str, adapter: AgentAdapter, mission: str,
        project: ProjectConfig, *, progress=None, low_priority=False, timeout=None,
    ) -> World:
        from .finalization_writer import EngineFinalizationWriter
        from .manifest import Manifest
        from .validation import requirements
        world = self.store.world(world_value)
        if world.state is WorldState.FINALIZING:
            journal = self.store.ensure_finalization_journal()
            return journal.recover(self.store, world.instance_id)
        if world.state in (WorldState.VALID, WorldState.DEGRADED):
            journal = self.store.ensure_finalization_journal()
            if journal.publication_pending(world.instance_id):
                return journal.recover(self.store, world.instance_id)
        if world.state is not WorldState.MUTABLE:
            raise WorldlineError('INVALID_TRANSITION', 'agent execution requires a MUTABLE world')
        roots = self.store.roots()
        if not roots:
            raise WorldlineError("NO_PRIME", "agent execution requires registered roots")
        self._evaluation_phases(project)
        base_sources = {root['root_key']: Path(world.base_payload_path) / root['root_key']
                        for root in roots}
        requirement = requirements(project, roots, base_sources, self.config,
                                   project.source_sha256, self.core)
        base_manifests = self.finalizer._capture_candidate_manifests(
            Path(world.base_payload_path), roots)
        writer = EngineFinalizationWriter(self.store.ensure_finalization_journal(), self.core)
        writer.begin(world=world, roots=roots, requirement=requirement,
            known_components=Manifest.component_roots(base_manifests.values(), self.core),
            required_checks=('agent', *(check.id for check in project.checks if check.required)))
        try:
            return self._run(world_value, adapter, mission, project, progress=progress,
                low_priority=low_priority, timeout=timeout,
                _finalization_writer=writer, _frozen_requirement=requirement)
        except BaseException as original:
            try:
                writer.interrupted(original)
            except BaseException as retention_error:
                original.add_note('finalization interruption retention also failed: ' + repr(retention_error))
            raise

    def _run(
        self, world_value, adapter, mission, project, *, progress=None,
        low_priority=False, timeout=None, _finalization_writer, _frozen_requirement,
    ) -> World:
        owned = _AgentAcquisition(self, _finalization_writer,
                                  self.store.world(world_value).instance_id)
        try:
            result = self._run_owned(world_value, adapter, mission, project,
                progress=progress, low_priority=low_priority, timeout=timeout,
                _finalization_writer=_finalization_writer,
                _frozen_requirement=_frozen_requirement, _owned_agent=owned)
        except BaseException as original:
            try:
                owned.finish(original)
            except BaseException as cleanup:
                if cleanup is not original:
                    original.add_note('owned acquisition cleanup also failed: ' + repr(cleanup))
            if owned.thread_errors:
                # Preserve the original stream-error lifecycle behavior, while
                # keeping a later store write from replacing the primary error.
                try:
                    world = self.store.world(world_value)
                    if world.state is WorldState.MUTABLE:
                        world.transition(WorldState.DEAD, self.core)
                        self.store.save_world(world)
                except BaseException as persistence_error:
                    original.add_note('owned stream-error world update also failed: ' + repr(persistence_error))
                try:
                    self.store.update_job(owned.job_id, state="DEAD",
                        error={"type": type(original).__name__, "message": str(original)}, ended=True)
                except BaseException as persistence_error:
                    original.add_note('owned stream-error job update also failed: ' + repr(persistence_error))
            raise
        finally:
            if owned.finished and owned.job_id is not None:
                with self._cancel_lock:
                    if self._acquisitions_by_job.get(owned.job_id) is owned:
                        self._acquisitions_by_job.pop(owned.job_id)
        owned.finish()
        return result

    def _run_owned(
        self,
        world_value: str,
        adapter: AgentAdapter,
        mission: str,
        project: ProjectConfig,
        *,
        progress: Callable[[str, dict[str, Any]], None] | None = None,
        low_priority: bool = False,
        timeout: float | None = None,
        _finalization_writer,
        _frozen_requirement,
        _owned_agent,
    ) -> World:
        world = self.store.world(world_value)
        registered = self.store.roots()
        if not registered:
            raise WorldlineError("NO_PRIME", "agent execution requires registered roots")
        # Legacy preparation may produce build outputs. Private evaluation starts only after
        # those writes are complete and gets a fixed input snapshot. Never reorder a policy or
        # run another legacy writer after a private result has named that snapshot.
        legacy_checks, private_checks = self._evaluation_phases(project)
        base = Path(world.base_payload_path)
        overlay_inputs = [
            (root["root_key"], base / root["root_key"], Path(os.fsdecode(bytes(root["path"]))))
            for root in registered
        ]
        _finalization_writer.invocation_started(world_instance=world.instance_id,
            check='agent', invocation=str(uuid.uuid4()), candidate_snapshot=None,
            verifier_entries=())
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
            _owned_agent.proxy = proxy
            write_forwarder(runtime)
            proxy.start()
            _owned_agent.proxy_started = True
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
        _owned_agent.job_id = job_id
        with self._cancel_lock:
            self._acquisitions_by_job[job_id] = _owned_agent
        self.store.append_causal_event(
            {
                "schemaVersion": SCHEMA_VERSION,
                "worldInstance": world.instance_id,
                "kind": "mission",
                "actor": "user",
                "mission": mission,
                "missionHash": world.mission_hash,
            },
            worldline_authored=True,
        )
        self.store.append_causal_event(
            {
                "schemaVersion": SCHEMA_VERSION,
                "worldInstance": world.instance_id,
                "kind": "agent-invocation",
                "actor": adapter.name,
                "argv": list(argv),
            },
            worldline_authored=True,
        )
        # Nothing is spawned without a reservation. The gate refuses with a named outcome and
        # the arithmetic behind it, so a world that cannot be supervised is never started rather
        # than started and starved.
        guard = self.gate.guard(f"world:{world.alias}/{adapter.name}")
        _owned_agent.guard = guard
        guard.__enter__()
        unit = _owned_agent.systemd_call(self.systemd.launch,
                world.instance_id,
                self.sandbox.build_argv(spec),
                description=f"WORLDLINE {world.alias} / {adapter.name}",
                nice=10 if low_priority else None,
                resource_properties=self.gate.unit_properties(),
            )
        _owned_agent.unit = unit
        with _owned_agent._ownership_lock:
            _owned_agent._stream_eof = {'stdout': False, 'stderr': False}
        guard.attach_unit(unit.unit)

        # What the kernel ACTUALLY took, read back rather than assumed, and what the workload
        # actually used. Both are sampled while the unit lives: `--collect` removes a finished
        # unit along with its cgroup, so a reading taken afterwards measures nothing at all.
        resources: dict[str, Any] = {
            "requested": self.gate.policy.canonical(),
            "effective": {"state": "UNAVAILABLE", "reason": "not sampled"},
            "observed": {"state": "UNAVAILABLE", "reason": "not sampled"},
            "accounted": bool(guard.decision and guard.decision.arithmetic.get("accounted")),
        }
        sampling = threading.Event()
        _owned_agent.sampling = sampling

        def guarded(target: Callable[[], None]) -> Callable[[], None]:
            def run_guarded() -> None:
                try:
                    target()
                except BaseException as exc:
                    with _finalization_writer.journal.lock:
                        _owned_agent.thread_errors.append(exc)
                    from .raw_observation import exception_observation
                    try:
                        _finalization_writer.invocation_raw(world_instance=world.instance_id,
                            check='agent', kind='agent-stream-exception',
                            observed={'stream': target.__name__, 'exception': exception_observation(exc)})
                    except BaseException as retention_error:
                        exc.add_note('agent stream exception retention also failed: ' + repr(retention_error))
                    # A dead reader can otherwise leave this owned workload
                    # blocked on its pipe while the launcher wait never returns.
                    try:
                        _owned_agent.systemd_call(self.systemd.stop, unit.unit)
                    except BaseException as cleanup_error:
                        exc.add_note('owned workload stop also failed: ' + repr(cleanup_error))
            return run_guarded

        def sample_resources() -> None:
            from .raw_observation import ProcessAcquisitionCancelled, retention_failed
            def reading_from(provider):
                return _owned_agent.systemd_call(provider, unit.unit, cancel_event=sampling)
            def cancelled(error):
                # The real helper has retained the complete wait/drain record.
                # A retention failure is not converted into an optional cancel.
                if (not sampling.is_set() or retention_failed(error)
                        or getattr(error, '_worldline_systemd_cancel_event', None) is not sampling
                        or getattr(error, '_worldline_systemd_cancel_complete', False) is not True):
                    raise error
                _finalization_writer.invocation_raw(world_instance=world.instance_id,
                    check='agent', kind='agent-resource-poll-cancelled',
                    observed={'unit': unit.unit, 'samplingStopObserved': True})
            occurrence = 0
            deadline = time.monotonic() + 30
            while not sampling.is_set() and time.monotonic() < deadline:
                try:
                    reading = reading_from(self.systemd.effective_limits)
                except ProcessAcquisitionCancelled as error:
                    cancelled(error)
                    return
                _finalization_writer.invocation_raw(world_instance=world.instance_id,
                    check='agent', kind='agent-resource-limits-acquisition', occurrence=occurrence,
                    observed={'unit': unit.unit, 'reading': reading})
                occurrence += 1
                if reading.get("cgroupReadable"):
                    resources["effective"] = reading
                    break
                sampling.wait(0.2)
            # 100 ms, not a second. A workload killed at its ceiling leaves a truthful window
            # only tens of milliseconds wide before `--collect` takes the unit and its cgroup
            # away; sampling once a second recorded an OOM-killed run as a clean one. The peak
            # is kept as a maximum rather than a last-value, so a late empty reading cannot
            # erase what was already measured.
            while not sampling.is_set():
                try:
                    reading = reading_from(self.systemd.resource_telemetry)
                except ProcessAcquisitionCancelled as error:
                    cancelled(error)
                    return
                _finalization_writer.invocation_raw(world_instance=world.instance_id,
                    check='agent', kind='agent-resource-telemetry-acquisition', occurrence=occurrence,
                    observed={'unit': unit.unit, 'reading': reading})
                occurrence += 1
                if reading.get("state") == "OBSERVED":
                    previous = resources["observed"]
                    if isinstance(previous, dict) and previous.get("state") == "OBSERVED":
                        for key in ("peakMemoryBytes", "peakSwapBytes", "cpuTimeNanoseconds", "tasksCurrent"):
                            if (previous.get(key) or 0) > (reading.get(key) or 0):
                                reading[key] = previous[key]
                        if previous.get("hitMemoryCeiling"):
                            reading["hitMemoryCeiling"] = True
                        if previous.get("oomKilled"):
                            reading["oomKilled"] = True
                    resources["observed"] = reading
                sampling.wait(0.1)

        sampler = threading.Thread(target=guarded(sample_resources), name="worldline-resource-sampler", daemon=True)
        _owned_agent.sampler = sampler
        sampler.start()
        main_pid = _owned_agent.systemd_call(lambda: unit.pid)
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
                    _owned_agent.systemd_call(self.systemd.stop, unit.unit)
                except WorldlineError:
                    pass
            timer = threading.Timer(timeout, expire)
            _owned_agent.timer = timer
            timer.daemon = True
            timer.start()
        if self._was_cancelled(job_id):
            # Cancelled between create_job and launch: the unit exists now, stop it ourselves.
            try:
                _owned_agent.systemd_call(self.systemd.stop, unit.unit)
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
                occurrence = 0
                for line in unit.launcher.stdout:
                    from .raw_observation import optional_bytes
                    _finalization_writer.invocation_raw(world_instance=world.instance_id,
                        check='agent', kind='agent-stdout-read', occurrence=occurrence,
                        observed={'unit': unit.unit, 'bytes': optional_bytes(line)})
                    occurrence += 1
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
                        event, refused = build_agent_event(piece, world_instance=world.instance_id,
                                                           adapter_name=adapter.name, raw_hash=raw_hash)
                        if not refused:
                            self._normalize_path(event, registered, primary)
                        # A refused claim is recorded as WORLDLINE's own record of the refusal.
                        self.store.append_causal_event(event, worldline_authored=refused)
                        parsed_events += 1
                        supplied_session = event.get("sessionReference")
                        if isinstance(supplied_session, str):
                            session_reference = supplied_session
                        if progress is not None:
                            progress("agent-event", {"world": world.alias, "event": event})
                _owned_agent._observe_stream_eof('stdout')
                _finalization_writer.invocation_raw(world_instance=world.instance_id,
                    check='agent', kind='agent-stdout-iterator-return',
                    observed={'unit': unit.unit, 'endOfIteratorObserved': True})
                raw_stream.flush()
                os.fsync(raw_stream.fileno())

        def read_stderr() -> None:
            assert unit.launcher.stderr is not None
            with open(stderr_path, "xb", buffering=0) as destination:
                from .raw_observation import optional_bytes
                occurrence = 0
                while True:
                    chunk = unit.launcher.stderr.read(shutil.COPY_BUFSIZE)
                    if not chunk:
                        _owned_agent._observe_stream_eof('stderr')
                    _finalization_writer.invocation_raw(world_instance=world.instance_id,
                        check='agent', kind='agent-stderr-read', occurrence=occurrence,
                        observed={'unit': unit.unit, 'bytes': optional_bytes(chunk)})
                    occurrence += 1
                    if not chunk:
                        break
                    destination.write(chunk)
                destination.flush()
                os.fsync(destination.fileno())

        stdout_thread = threading.Thread(target=guarded(read_stdout), name=f"worldline-{world.alias}-stdout")
        stderr_thread = threading.Thread(target=guarded(read_stderr), name=f"worldline-{world.alias}-stderr")
        _owned_agent.threads.append(stdout_thread)
        stdout_thread.start()
        _owned_agent.threads.append(stderr_thread)
        stderr_thread.start()
        assert unit.launcher.stdin is not None
        if adapter.mission_via_stdin:
            unit.launcher.stdin.write(mission.encode("utf-8", "strict"))
        unit.launcher.stdin.close()
        exit_code = _owned_agent.wait()
        _owned_agent.cancel_timer()
        cancelled = self._was_cancelled(job_id)
        with self._cancel_lock:
            timed_out = job_id in self._timed_out
            self._timed_out.discard(job_id)
        self._forget_cancel(job_id)
        stopped = cancelled or timed_out
        supervision = _owned_agent.finish(stopped=stopped)
        if parsed_events == 0:
            self.store.append_causal_event(
                {
                    "schemaVersion": SCHEMA_VERSION,
                    "worldInstance": world.instance_id,
                    "kind": "agent-invocation-result",
                    "actor": adapter.name,
                    "exitCode": exit_code,
                    "reason": None,
                },
                worldline_authored=True,
            )
        # What the manager says happened to the unit: structured, bounded, and the only basis
        # for telling a launcher that never got a unit from a workload that ran and failed.
        # Durable evidence, for the case sampling missed. The manager's own record of why the
        # unit ended outlives the unit, so a ceiling that fired is still provable after the
        # cgroup is gone.
        observed = resources.get("observed") if isinstance(resources.get("observed"), dict) else {}
        manager_result = supervision.get("result") if isinstance(supervision, dict) else None
        resources["ceilingFired"] = (
            True if observed.get("hitMemoryCeiling") or observed.get("oomKilled") or manager_result == "oom-kill"
            else (None if observed.get("state") != "OBSERVED" and manager_result is None else False))
        resources["ceilingEvidence"] = (
            "cgroup memory.events sampled during the run" if observed.get("hitMemoryCeiling") else
            ("the service manager recorded Result=oom-kill" if manager_result == "oom-kill" else
             ("nothing was measured" if resources["ceilingFired"] is None else "no ceiling event was recorded")))
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
            # Trusted via the supervisor's own outcome for this unit, not via a result channel:
            # the agent writes no framed record, its verdict IS the exit status the manager
            # observed. Stated explicitly so evaluation_record does not have to infer it.
            "origin": "agent",
            "status": "FAIL" if stopped or supervision["kind"] != "SUPERVISED" else ("PASS" if exit_code == 0 else "FAIL"),
            "rawEventHash": hash_id(self.core.hash_file(raw_path)),
            "stderrHash": hash_id(self.core.hash_file(stderr_path)),
            "network": proxy.summary() if proxy is not None else {"policy": policy},
            "supervision": supervision,
            # Measurement, not identity. Telemetry is recorded on the evidence and never hashed,
            # so an otherwise identical verification is not invalidated because this run happened
            # to peak 40 MiB higher than the last one.
            "resources": resources,
        }
        if cancelled:
            agent_result["reason"] = "USER_CANCELLED: the operator stopped this world before the agent finished"
        elif timed_out:
            agent_result["reason"] = f"TIMEOUT: the agent exceeded the {timeout:g} s limit and was stopped"
        elif resources.get("ceilingFired"):
            agent_result["reason"] = (
                f"RESOURCE_LIMIT_EXCEEDED: the workload reached a resource ceiling this policy set"
                f" ({resources['ceilingEvidence']})")
        elif supervision["kind"] == "INDETERMINATE":
            agent_result["reason"] = f"SUPERVISION_INDETERMINATE: the manager's journal did not establish that {unit.unit} ran ({supervision['source']})"
        check_results = [agent_result]
        _finalization_writer.invocation_raw(world_instance=world.instance_id, check='agent',
            kind='manager-return', observed={'unit': unit.unit, 'exitCode': exit_code,
                                           'supervision': supervision, 'resources': resources})
        _finalization_writer.invocation_result(world_instance=world.instance_id,
                                               check='agent', result=agent_result)
        candidate_snapshot = None
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
                    "profile": check.profile,
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
            # Membership computed from the same PRIME bytes the examiner is staged from, so the
            # set that is identified and the set that runs are one thing.
            verifier_roots = [{"root_key": r.root_key, "path": str(r.target),
                               "primary": str(r.target) == str(primary_target)} for r in overlays]
            # The trusted evaluator snapshot for a fork is the overlay LOWER, which is PRIME as
            # the world was forked from it. Named here and passed explicitly; the check runner
            # does not infer it.
            verifier_sources = {r.root_key: r.lower for r in overlays}
            prime_verifiers = resolve_verifiers(project, verifier_roots, verifier_sources)
            logical_roots = {r.root_key: str(r.target) for r in overlays}
            if legacy_checks:
                check_results.extend(self.checks.run(
                    world_instance=world.instance_id,
                    overlays=overlays,
                    primary_target=primary_target,
                    checks=legacy_checks,
                    verifier_sources=verifier_sources,
                    verifiers=prime_verifiers,
                    logical_roots=logical_roots,
                    _observation_writer=_finalization_writer,
                ))
            if private_checks:
                candidate_snapshot = self.finalizer.capture_candidate(world.instance_id, overlays)
                _finalization_writer.record_input(candidate_snapshot)
                check_overlays = self.finalizer.candidate_overlays(candidate_snapshot)
                evaluated = self.checks.run(
                    world_instance=world.instance_id,
                    overlays=check_overlays,
                    primary_target=primary_target,
                    checks=private_checks,
                    candidate_snapshot=candidate_snapshot.binding(),
                    verifier_sources=verifier_sources,
                    verifiers=prime_verifiers,
                    logical_roots=logical_roots,
                    _observation_writer=_finalization_writer,
                )
                for result in evaluated:
                    result["candidateSnapshot"] = candidate_snapshot.binding()
                check_results.extend(evaluated)
        # Evidence freshness (1.3.0): what this evaluation was bound to. The requirement half is
        # computed from the bytes the world was forked from (its base payload), which is what
        # the checks were defined against; finalize adds the candidate-side verifier hashes.
        roots = self.store.roots()
        requirement = _frozen_requirement
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
            candidate_snapshot=candidate_snapshot,
            _finalization_writer=_finalization_writer,
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
    def _evaluation_phases(project: ProjectConfig) -> tuple[list[Any], list[Any]]:
        legacy: list[Any] = []
        private: list[Any] = []
        for check in project.checks:
            if check.profile == "private-evaluator-v1":
                private.append(check)
            elif private:
                raise WorldlineError(
                    "CHECK_PROFILE_ORDER_INVALID",
                    "legacy preparation checks must precede private evaluator checks",
                    {"checkId": check.id},
                )
            else:
                legacy.append(check)
        return legacy, private

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
