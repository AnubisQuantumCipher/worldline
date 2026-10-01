"""Bounded private Python evaluator, with candidate execution under a subordinate uid.

This is an execution backend, not an admission decision. The caller supplies frozen input
trees, trusted verifier bytes and an invocation-bound private report directory. Python
examiners may ``import candidate`` and call ``candidate.run(argv, cwd=None, timeout=30)``.
They write their report to /run/worldline-report/report. Only the examiner sees the broker
socket and report mount. Worker copies are disposable and never become candidate payloads.

The initial filesystem contract deliberately accepts only ordinary directories and singly
linked regular files, with ordinary permission bits and no xattrs. Ownership is normalized
in copies; timestamps and permission bits are retained. Links, special files and metadata
outside this contract are refused. Host writers must already have been stopped by the
caller: copying with change detection is not a mechanism for freezing a live source tree.

The script entry points use only stdlib, with -I -S. The bootstrap retains mapping authority
to create sandboxes; all examiner and worker code runs after setpriv drops capabilities and
sets no-new-privileges. Trust includes the host kernel, installed /usr tools and trusted
examiner logic. This module does not attest toolchain packages or provide a proof of isolation.
"""
from __future__ import annotations

import base64
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import runpy
import selectors
import shutil
import signal
import socket
import stat
import struct
import subprocess
import sys
import threading
import time
import types
from typing import Any, Mapping, Sequence
import uuid

if __package__:
    from ..trusted import TRUSTED_INTERPRETER, trusted_script
else:
    # The engine stages this exact policy beside this helper and mounts it read-only.
    _startup_policy = runpy.run_path(str(Path(__file__).with_name("trusted.py")))
    TRUSTED_INTERPRETER = _startup_policy["TRUSTED_INTERPRETER"]
    trusted_script = _startup_policy["trusted_script"]

PROFILE_ID = "private-evaluator-v1"
VERIFIER_MOUNT = "/run/worldline-verifiers"
REPORT_MOUNT = "/run/worldline-report"
BROKER_MOUNT = "/run/worldline-broker.sock"
WORKER_BROKER_MOUNT = "/run/worldline-worker-broker.sock"
HELPER_MOUNT = "/run/worldline-evaluator.py"
MAX_TREE_BYTES = 268_435_456
MAX_TREE_ENTRIES = 100_000
# The mapped bootstrap handshake is fail-closed, so its window only has to cover a loaded host:
# on 2026-09-28 a bootstrap under a load average near 110 became ready after 19.86 s.
BOOTSTRAP_HANDSHAKE_SECONDS = 60
MAX_OUTPUT_BYTES = 1_048_576
MAX_REQUEST_BYTES = 65_536
MAX_REQUESTS = 32
MAX_CASE_REQUESTS = 50_000
MAX_CASE_LEASES = 256
MAX_CASE_WAIT_MS = 2000
# Only interpreter-determinism variables may be set for candidate processes.
CANDIDATE_ENV_ALLOWED = {"PYTHONHASHSEED": r"[0-9]{1,10}", "PYTHONDONTWRITEBYTECODE": r"1"}
MAX_CASE_STDIN_BYTES = 2048
MAX_WORKER_SECONDS = 120
MAX_EVALUATOR_SECONDS = 600
TOOLCHAIN_MOUNT = "/opt/worldline-gnat"
_ARCH = platform.machine()
_TOOLCHAIN_EXECUTABLES = (
    f"gnat-{_ARCH}-linux-16.1.0-1/bin/gcc",
    f"gprbuild-{_ARCH}-linux-26.0.0-1/bin/gprbuild",
    f"gnatprove-{_ARCH}-linux-16.1.0-1/bin/gnatprove",
    f"gnatprove-{_ARCH}-linux-16.1.0-1/libexec/spark/bin/why3",
    f"gnatprove-{_ARCH}-linux-16.1.0-1/libexec/spark/bin/alt-ergo",
    f"gnatprove-{_ARCH}-linux-16.1.0-1/libexec/spark/bin/cvc5",
    f"gnatprove-{_ARCH}-linux-16.1.0-1/libexec/spark/bin/z3",
)
_DIR_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
_FILE_FLAGS = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK
_RESERVED = ("/usr", "/bin", "/sbin", "/lib", "/lib64", "/etc", "/dev", "/proc", "/run", "/tmp")


class BackendFailure(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _refuse(message: str, code: str = "PRIVATE_EVALUATOR_INVALID") -> None:
    raise BackendFailure(code, message)


def _absolute(value: str) -> str:
    if (not isinstance(value, str) or not value.startswith("/") or "\0" in value
            or str(PurePosixPath(value)) != value or ".." in PurePosixPath(value).parts):
        _refuse("path must be an absolute normalized path")
    return value


def _inside(path: str, parent: str) -> bool:
    return path == parent or path.startswith(parent.rstrip("/") + "/")


def _open_directory(path: Path) -> int:
    _absolute(str(path))
    descriptor = os.open("/", _DIR_FLAGS)
    try:
        for part in path.parts[1:]:
            next_descriptor = os.open(part, _DIR_FLAGS, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = next_descriptor
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def _signature(info: os.stat_result) -> tuple[int, ...]:
    return (info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns, info.st_nlink)


def copy_frozen_tree(source: Path, destination: Path) -> str:
    """Descriptor-relative bounded copy. Refuse links, mounts, xattrs and changing entries.

    Return a digest of paths, kinds, modes and regular-file bytes. It is a backend input
    identity, not WORLDLINE's candidate root identity. The destination must not exist.
    """
    source_fd = _open_directory(source)
    records: list[dict[str, Any]] = []
    budget = {"bytes": 0, "entries": 0}
    source_device = os.fstat(source_fd).st_dev

    def copy_entry(src: int, dst: Path, relative: str, depth: int) -> None:
        before = os.fstat(src)
        budget["entries"] += 1
        if budget["entries"] > MAX_TREE_ENTRIES or depth > 128:
            _refuse("input tree exceeds entry/depth limit", "PRIVATE_TREE_LIMIT")
        if before.st_dev != source_device or before.st_mode & 0o7000:
            _refuse("mounted filesystem or special permission bits in input", "PRIVATE_TREE_UNSUPPORTED")
        if os.listxattr(src):
            _refuse("extended attributes are outside the private evaluator tree contract", "PRIVATE_TREE_UNSUPPORTED")
        mode = stat.S_IMODE(before.st_mode)
        if stat.S_ISDIR(before.st_mode):
            dst.mkdir(mode=0o700)
            names = sorted(os.listdir(src))
            for name in names:
                info = os.stat(name, dir_fd=src, follow_symlinks=False)
                if not (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)):
                    _refuse("input contains a link or special object", "PRIVATE_TREE_UNSUPPORTED")
                descriptor = os.open(name, _DIR_FLAGS if stat.S_ISDIR(info.st_mode) else _FILE_FLAGS,
                                     dir_fd=src)
                try:
                    if _signature(info) != _signature(os.fstat(descriptor)):
                        _refuse("input changed while opening", "PRIVATE_TREE_CHANGED")
                    copy_entry(descriptor, dst / name, relative + "/" + name, depth + 1)
                finally:
                    os.close(descriptor)
            records.append({"path": relative, "kind": "directory", "mode": mode})
        elif stat.S_ISREG(before.st_mode) and before.st_nlink == 1:
            budget["bytes"] += before.st_size
            if budget["bytes"] > MAX_TREE_BYTES:
                _refuse("input tree exceeds byte limit", "PRIVATE_TREE_LIMIT")
            digest = hashlib.sha256()
            count = 0
            with dst.open("xb") as output:
                while True:
                    chunk = os.read(src, 65536)
                    if not chunk:
                        break
                    count += len(chunk)
                    if count > before.st_size:
                        _refuse("input grew during copying", "PRIVATE_TREE_CHANGED")
                    digest.update(chunk)
                    output.write(chunk)
            if count != before.st_size:
                _refuse("input size changed during copying", "PRIVATE_TREE_CHANGED")
            records.append({"path": relative, "kind": "file", "mode": mode,
                            "sha256": digest.hexdigest()})
        else:
            _refuse("input is not an ordinary singly linked file", "PRIVATE_TREE_UNSUPPORTED")
        if _signature(before) != _signature(os.fstat(src)):
            _refuse("input changed during copying", "PRIVATE_TREE_CHANGED")
        os.chmod(dst, mode, follow_symlinks=False)
        os.utime(dst, ns=(before.st_atime_ns, before.st_mtime_ns), follow_symlinks=False)

    try:
        if destination == source or source in destination.parents:
            _refuse("copy destination is inside source")
        copy_entry(source_fd, destination, ".", 0)
    finally:
        os.close(source_fd)
    return hashlib.sha256(json.dumps(records, sort_keys=True, ensure_ascii=True).encode()).hexdigest()


@dataclass(frozen=True)
class PrivateEvaluationSpec:
    run_id: str
    roots: Mapping[str, Path]
    verifier_directory: Path
    argv: tuple[str, ...]
    cwd: str
    report_directory: Path
    runtime: Path
    timeout_seconds: int = MAX_EVALUATOR_SECONDS
    bubblewrap_executable: Path | None = None


def _validate_spec(spec: PrivateEvaluationSpec) -> None:
    if (not spec.roots or len(spec.roots) > 16 or isinstance(spec.timeout_seconds, bool)
            or not isinstance(spec.timeout_seconds, int)
            or not 1 <= spec.timeout_seconds <= MAX_EVALUATOR_SECONDS):
        _refuse("invalid roots or evaluator timeout")
    targets = list(spec.roots)
    for target in targets:
        _absolute(target)
        if target == "/" or any(_inside(target, p) or _inside(p, target) for p in (*_RESERVED, TOOLCHAIN_MOUNT)):
            _refuse("candidate target overlaps evaluator/system mounts")
        if any(target != other and (_inside(target, other) or _inside(other, target)) for other in targets):
            _refuse("candidate targets overlap")
    _absolute(spec.cwd)
    if not any(_inside(spec.cwd, target) for target in targets):
        _refuse("examiner cwd is outside candidate roots")
    if (len(spec.argv) < 2 or spec.argv[0] != TRUSTED_INTERPRETER
            or not all(isinstance(v, str) and "\0" not in v for v in spec.argv)):
        _refuse("private evaluator requires /usr/bin/python3 followed by a staged script")
    script = _absolute(spec.argv[1])
    if not _inside(script, VERIFIER_MOUNT) or script == VERIFIER_MOUNT:
        _refuse("examiner script is outside the trusted verifier mount")
    for directory in (spec.report_directory, spec.runtime.parent):
        descriptor = _open_directory(directory)
        try:
            info = os.fstat(descriptor)
            if info.st_uid != os.getuid() or info.st_mode & 0o077:
                _refuse("report/runtime parent must be owned by the daemon and owner-only")
        finally:
            os.close(descriptor)
    for directory in (*spec.roots.values(), spec.verifier_directory):
        if directory == spec.runtime or directory in spec.runtime.parents:
            _refuse("backend runtime must be outside input trees")


def _bubblewrap_identity(requested: Path | None) -> dict[str, str]:
    selected = str(requested) if requested is not None else shutil.which("bwrap")
    if not selected:
        _refuse("bubblewrap is unavailable for private roles", "PRIVATE_EVALUATOR_UNAVAILABLE")
    try:
        path = Path(selected).resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        _refuse(f"bubblewrap executable cannot be resolved: {exc}", "PRIVATE_EVALUATOR_INVALID")
    info = path.stat()
    if (not path.is_absolute() or not stat.S_ISREG(info.st_mode)
            or info.st_uid not in (0, os.getuid()) or info.st_mode & 0o7022
            or not os.access(path, os.X_OK)):
        _refuse("bubblewrap executable is not an approved regular file", "PRIVATE_EVALUATOR_INVALID")
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    return {"path": str(path), "sha256": digest}


class _PrivateAcquisitions:
    """Invocation-local observations, never report or boundary admission."""
    def __init__(self, spec, process, observer):
        self.spec = spec
        self.process = process
        self.observer = observer
        self.next_occurrence = 0

    def _start(self, kind, site):
        occurrence = self.next_occurrence
        self.next_occurrence += 1
        return (lambda record: self.observer(kind, occurrence, record)), {
            'schemaVersion': 1, 'runId': self.spec.run_id,
            'unit': self.process.unit, 'site': site,
            'occurrence': occurrence,
        }

    def communicate(self, timeout, *, site):
        from ..raw_observation import (
            optional_bytes, retain_observation, exception_observation,
        )
        observe, details = self._start('private-communicate-acquisition', site)
        try:
            stdout, stderr = self.process.launcher.communicate(timeout=timeout)
        except BaseException as primary:
            # Available exception output is distinct from an actual return.
            # Preserve this primary even if the retention callback also fails.
            try:
                retain_observation(observe, {
                    **details, 'communicateReturned': False,
                    'stdout': optional_bytes(getattr(primary, 'output', None)),
                    'stderr': optional_bytes(getattr(primary, 'stderr', None)),
                    'launcherReturncode': self.process.launcher.returncode,
                    'exception': exception_observation(primary),
                })
            except BaseException as secondary:
                primary.add_note('available private communication retention also failed: ' +
                                 type(secondary).__qualname__ + ': ' + str(secondary))
                primary._worldline_retention_failed = True
            raise
        # This callback precedes supervision, parsing and the resource-guard exit.
        retain_observation(observe, {
            **details, 'communicateReturned': True,
            'stdout': optional_bytes(stdout), 'stderr': optional_bytes(stderr),
            'launcherReturncode': self.process.launcher.returncode,
            'exception': None,
        })
        return stdout, stderr

    def cleanup_communicate(self, timeout, *, site):
        from ..raw_observation import retention_failed
        primary = sys.exception()
        try:
            return self.communicate(timeout, site=site)
        except BaseException as secondary:
            if primary is None:
                raise
            primary.add_note('private communication cleanup also failed: ' +
                             type(secondary).__qualname__ + ': ' + str(secondary))
            if retention_failed(secondary):
                primary._worldline_retention_failed = True

    def boundary_bytes(self, path):
        from ..raw_observation import (
            optional_bytes, retain_observation, exception_observation, cleanup_call,
        )
        observe, details = self._start('private-boundary-acquisition', 'boundary-read')
        details['pathBytes'] = optional_bytes(os.fsencode(path))
        stream = None
        content = None
        try:
            try:
                stream = path.open('rb')
                content = bytearray()
                while True:
                    chunk = stream.read(65536)
                    if not chunk:
                        break
                    content.extend(chunk)
            except BaseException as primary:
                try:
                    retain_observation(observe, {
                        **details, 'readReturned': False, 'readReachedEof': False,
                        'bytes': optional_bytes(content),
                        'exception': exception_observation(primary),
                    })
                except BaseException as secondary:
                    primary.add_note('available private boundary retention also failed: ' +
                                     type(secondary).__qualname__ + ': ' + str(secondary))
                    primary._worldline_retention_failed = True
                raise
            # Retain the original file bytes before any text decoding or JSON use.
            payload = bytes(content)
            retain_observation(observe, {
                **details, 'readReturned': True, 'readReachedEof': True,
                'bytes': optional_bytes(payload), 'exception': None,
            })
            return payload
        finally:
            if stream is not None:
                cleanup_call(stream.close)


class PrivateEvaluator:
    def __init__(self, systemd: Any):
        self.systemd = systemd

    def run(self, spec: PrivateEvaluationSpec, *, resource_properties: Sequence[str] = (), _supervision_observer=None, _acquisition_observer=None) -> dict[str, Any]:
        """Run a trusted Python examiner. Never interpret or admit its report here."""
        from ..errors import WorldlineError
        try:
            return self._run(spec, resource_properties, **({} if _supervision_observer is None else {'_supervision_observer': _supervision_observer}),
                **({} if _acquisition_observer is None else {'_acquisition_observer': _acquisition_observer}))
        except (BackendFailure, OSError, ValueError) as exc:
            if _supervision_observer is not None or _acquisition_observer is not None:
                from ..raw_observation import retention_failed
                if retention_failed(exc): raise
            raise WorldlineError(getattr(exc, "code", "PRIVATE_EVALUATOR_FAILED"), str(exc)) from exc

    def _run(self, spec: PrivateEvaluationSpec, resource_properties: Sequence[str], *, _supervision_observer=None, _acquisition_observer=None) -> dict[str, Any]:
        _validate_spec(spec)
        bubblewrap = _bubblewrap_identity(spec.bubblewrap_executable)
        spec.runtime.mkdir(mode=0o700)
        (spec.runtime / "frozen").mkdir(mode=0o700)
        (spec.runtime / "workers").mkdir(mode=0o700)
        roots = []
        for index, (target, source) in enumerate(sorted(spec.roots.items())):
            frozen = spec.runtime / "frozen" / str(index)
            identity = copy_frozen_tree(source, frozen)
            roots.append({"target": target, "frozen": str(frozen), "identity": identity})
        verifier = spec.runtime / "verifiers"
        verifier_identity = copy_frozen_tree(spec.verifier_directory, verifier)
        helper = spec.runtime / "helper.py"
        helper.write_bytes(Path(__file__).read_bytes())
        helper.chmod(0o444)
        case_copier = spec.runtime / "case-copy.py"
        case_copier.write_bytes(Path(__file__).with_name("private_case_copy.py").read_bytes())
        case_copier.chmod(0o444)
        startup_policy = spec.runtime / "trusted.py"
        startup_policy.write_bytes(Path(__file__).parents[1].joinpath("trusted.py").read_bytes())
        startup_policy.chmod(0o444)
        plan = {"profileId": PROFILE_ID, "runId": spec.run_id, "roots": roots,
                "bubblewrap": bubblewrap,
                "verifier": str(verifier), "verifierIdentity": verifier_identity,
                "argv": list(spec.argv), "cwd": spec.cwd, "runtime": str(spec.runtime),
                "report": str(spec.report_directory), "helper": str(helper),
                "caseCopier": str(case_copier),
                "caseCopierSha256": hashlib.sha256(case_copier.read_bytes()).hexdigest(),
                "startupPolicy": str(startup_policy),
                "bootstrapSha256": hashlib.sha256(helper.read_bytes()).hexdigest(),
                "startupPolicySha256": hashlib.sha256(startup_policy.read_bytes()).hexdigest(),
                "timeout": spec.timeout_seconds, "operatorUid": os.getuid(), "operatorGid": os.getgid()}
        # Fixed operator installations on the reference host and the hosted assurance runner.
        # The candidate and project policy cannot supply this path.
        toolchain = next((root for root in (Path.home() / "opt" / "gnat", Path.home() / "gnat")
                          if root.is_dir() and (root / _TOOLCHAIN_EXECUTABLES[2]).is_file()), None)
        if toolchain is not None:
            descriptor = _open_directory(toolchain)
            os.close(descriptor)
            identities = {}
            for relative in _TOOLCHAIN_EXECUTABLES:
                path = toolchain / relative
                if path.is_file():
                    with path.open("rb") as stream:
                        identities[relative] = hashlib.file_digest(stream, "sha256").hexdigest()
            plan["toolchain"] = {"source": str(toolchain), "target": TOOLCHAIN_MOUNT,
                                 "executables": identities,
                                 "identityScope": "listed executable bytes; not a complete installation attestation"}
        plan_path = spec.runtime / "plan.json"
        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        plan_path.chmod(0o600)
        process = self.systemd.launch_private_evaluator(
            spec.run_id, plan_path, helper, resource_properties=resource_properties)
        if _acquisition_observer is not None:
            return self._collect_observed(spec, process, _acquisition_observer,
                                          _supervision_observer=_supervision_observer)
        try:
            deadline = time.monotonic() + BOOTSTRAP_HANDSHAKE_SECONDS
            while not (spec.runtime / "bootstrap-ready").exists():
                if process.launcher.poll() is not None or time.monotonic() >= deadline:
                    _refuse("mapped bootstrap did not become ready", "PRIVATE_EVALUATOR_UNAVAILABLE")
                time.sleep(0.02)
            unit_properties = self.systemd._show(process.unit, ("NoNewPrivileges", "MainPID"))
            if not unit_properties or unit_properties.get("NoNewPrivileges") != "no":
                _refuse("manager did not confirm mapping bootstrap NoNewPrivileges=no")
            (spec.runtime / "bootstrap-go").write_text("GO\n")
            stdout, stderr = process.launcher.communicate(timeout=spec.timeout_seconds + 20)
        except subprocess.TimeoutExpired:
            self.systemd.stop(process.unit)
            process.launcher.communicate(timeout=20)
            _refuse("supervised private evaluator exceeded its deadline", "PRIVATE_EVALUATOR_TIMEOUT")
        except BaseException:
            self.systemd.stop(process.unit)
            process.launcher.communicate(timeout=20)
            raise
        supervision = self.systemd.outcome(process, process.launcher.returncode,
            **({} if _supervision_observer is None else {'_raw_observer': _supervision_observer}))
        evidence_path = spec.runtime / "boundary.json"
        if not evidence_path.is_file():
            _refuse("private bootstrap produced no boundary evidence: " + stderr.decode("utf-8", "replace")[-2000:],
                    "PRIVATE_EVALUATOR_UNAVAILABLE")
        boundary = json.loads(evidence_path.read_text(encoding="utf-8"))
        if boundary.get("error"):
            _refuse(str(boundary["error"]), "PRIVATE_EVALUATOR_BOUNDARY_FAILED")
        boundary["managerBootstrapProperties"] = unit_properties
        boundary["bootstrapExitCode"] = process.launcher.returncode
        return {"profileId": PROFILE_ID, "stdout": stdout, "stderr": stderr,
                "exitCode": process.launcher.returncode, "supervision": supervision,
                "boundary": boundary, "reportDirectory": spec.report_directory}

    def _collect_observed(self, spec, process, observer, *, _supervision_observer=None):
        from ..raw_observation import cleanup_call, retention_failed
        acquisition = _PrivateAcquisitions(spec, process, observer)
        try:
            deadline = time.monotonic() + BOOTSTRAP_HANDSHAKE_SECONDS
            while not (spec.runtime / "bootstrap-ready").exists():
                if process.launcher.poll() is not None or time.monotonic() >= deadline:
                    _refuse("mapped bootstrap did not become ready", "PRIVATE_EVALUATOR_UNAVAILABLE")
                time.sleep(0.02)
            unit_properties = self.systemd._show(process.unit, ("NoNewPrivileges", "MainPID"))
            if not unit_properties or unit_properties.get("NoNewPrivileges") != "no":
                _refuse("manager did not confirm mapping bootstrap NoNewPrivileges=no")
            (spec.runtime / "bootstrap-go").write_text("GO\n")
            stdout, stderr = acquisition.communicate(spec.timeout_seconds + 20,
                                                     site='examiner-wait')
        except subprocess.TimeoutExpired as primary:
            cleanup_call(lambda: self.systemd.stop(process.unit))
            acquisition.cleanup_communicate(20, site='timeout-cleanup')
            if retention_failed(primary):
                raise
            _refuse("supervised private evaluator exceeded its deadline", "PRIVATE_EVALUATOR_TIMEOUT")
        except BaseException:
            cleanup_call(lambda: self.systemd.stop(process.unit))
            acquisition.cleanup_communicate(20, site='exception-cleanup')
            raise
        supervision = self.systemd.outcome(process, process.launcher.returncode,
            **({} if _supervision_observer is None else {'_raw_observer': _supervision_observer}))
        evidence_path = spec.runtime / "boundary.json"
        if not evidence_path.is_file():
            _refuse("private bootstrap produced no boundary evidence: " + stderr.decode("utf-8", "replace")[-2000:],
                    "PRIVATE_EVALUATOR_UNAVAILABLE")
        payload = acquisition.boundary_bytes(evidence_path)
        # Match Path.read_text's UTF-8 and universal-newline behavior while
        # decoding only the owned, already retained bytes.
        import io
        with io.TextIOWrapper(io.BytesIO(payload), encoding='utf-8') as text_stream:
            boundary = json.loads(text_stream.read())
        if boundary.get("error"):
            _refuse(str(boundary["error"]), "PRIVATE_EVALUATOR_BOUNDARY_FAILED")
        boundary["managerBootstrapProperties"] = unit_properties
        boundary["bootstrapExitCode"] = process.launcher.returncode
        return {"profileId": PROFILE_ID, "stdout": stdout, "stderr": stderr,
                "exitCode": process.launcher.returncode, "supervision": supervision,
                "boundary": boundary, "reportDirectory": spec.report_directory}


def _observations(role: str) -> dict[str, Any]:
    status = {}
    for line in Path("/proc/self/status").read_text().splitlines():
        key, _, value = line.partition(":")
        if key in ("Uid", "Gid", "Groups", "NoNewPrivs", "CapEff", "CapPrm", "CapBnd", "CapAmb"):
            status[key] = value.strip()
    return {"role": role, "uid": os.getuid(), "gid": os.getgid(), "status": status,
            "uidMap": Path("/proc/self/uid_map").read_text(),
            "gidMap": Path("/proc/self/gid_map").read_text(),
            "namespaces": {name: os.readlink("/proc/self/ns/" + name) for name in ("pid", "mnt", "user", "net")},
            "reportMounted": os.path.isdir(REPORT_MOUNT),
            "brokerMounted": os.path.exists(BROKER_MOUNT),
            "workerBrokerMounted": os.path.exists(WORKER_BROKER_MOUNT),
            "toolchainMounted": os.path.isdir(TOOLCHAIN_MOUNT)}


def _validate_observation(observation: Mapping[str, Any], role: str) -> None:
    expected = {"examiner": 0, "worker": 1, "candidate": 2}.get(role)
    if expected is None:
        _refuse("unknown private role", "PRIVATE_ROLE_INVALID")
    status = observation.get("status", {})
    if (observation.get("role") != role or observation.get("uid") != expected
            or observation.get("gid") != expected or status.get("NoNewPrivs") != "1"
            or status.get("Uid", "").split() != [str(expected)] * 4
            or status.get("Gid", "").split() != [str(expected)] * 4
            or any(int(status.get(key, "1"), 16) != 0 for key in ("CapEff", "CapPrm", "CapBnd", "CapAmb"))
            or status.get("Groups") != ""
            or observation.get("reportMounted") != (role == "examiner")
            or observation.get("brokerMounted") != (role == "examiner")
            or observation.get("workerBrokerMounted") != (role == "worker")):
        _refuse("role privilege or mount observation differs from required boundary", "PRIVATE_ROLE_INVALID")


def _mapped_identity(mapping: str, identity: int) -> int:
    rows = [tuple(map(int, row.split())) for row in mapping.splitlines()]
    matches = [host + identity - start for start, host, count in rows if start <= identity < start + count]
    if len(matches) != 1:
        _refuse("UID/GID map does not uniquely map the required identity")
    return matches[0]


def _sandbox(plan: Mapping[str, Any], role: str, roots: Sequence[Mapping[str, Any]],
             payload: Sequence[str], cwd: str,
             case_bind: Mapping[str, str] | None = None,
             environment: Mapping[str, str] | None = None) -> list[str]:
    # No --unshare-user here: the bootstrap already owns the subordinate-ID user namespace.
    command = [plan["bubblewrap"]["path"], "--unshare-pid", "--unshare-ipc", "--unshare-uts", "--unshare-net",
               "--die-with-parent", "--new-session", "--clearenv", "--setenv", "PATH", "/usr/bin",
               "--setenv", "HOME", "/tmp", "--ro-bind", "/usr", "/usr", "--ro-bind", "/etc", "/etc"]
    if environment:
        if role != "candidate":
            _refuse("environment overrides are restricted to candidate role")
        for key, value in sorted(environment.items()):
            command.extend(("--setenv", key, value))
    for path in ("/bin", "/sbin", "/lib", "/lib64"):
        if Path(path).is_symlink():
            command.extend(("--symlink", os.readlink(path), path))
        elif Path(path).exists():
            command.extend(("--ro-bind", path, path))
    command.extend(("--dev", "/dev", "--proc", "/proc", "--tmpfs", "/tmp", "--tmpfs", "/run",
                    "--ro-bind", plan["helper"], HELPER_MOUNT,
                    "--ro-bind", plan["startupPolicy"], "/run/trusted.py"))
    # bwrap's implicitly created ancestors can be owner-only. The worker needs traversal
    # through these empty mountpoint scaffolds, without changing any source-tree mode bits.
    ancestors = sorted({str(parent) for root in roots for parent in Path(root["target"]).parents
                        if str(parent) != "/"}, key=lambda value: (len(Path(value).parts), value))
    for ancestor in ancestors:
        command.extend(("--dir", ancestor, "--chmod", "0755", ancestor))
    for root in roots:
        command.extend(("--ro-bind" if role == "examiner" else "--bind", root["source"], root["target"]))
    if case_bind is not None:
        if role != "candidate":
            _refuse("case mount is restricted to candidate role")
        command.extend(("--bind", case_bind["source"], case_bind["target"]))
    if role == "examiner":
        command.extend(("--ro-bind", plan["verifier"], VERIFIER_MOUNT,
                        "--bind", plan["report"], REPORT_MOUNT,
                        "--bind", plan["socket"], BROKER_MOUNT))
        if plan.get("toolchain"):
            command.extend(("--ro-bind", plan["toolchain"]["source"], TOOLCHAIN_MOUNT))
    elif role == "worker":
        command.extend(("--bind", plan["workerSocket"], WORKER_BROKER_MOUNT))
    uid = {"examiner": "0", "worker": "1", "candidate": "2"}[role]
    command.extend(("--chdir", cwd, "--", "/usr/bin/setpriv", "--no-new-privs", "--reuid", uid,
                    "--regid", uid, "--clear-groups", "--bounding-set=-all", "--inh-caps=-all",
                    "--ambient-caps=-all", "--", *trusted_script(HELPER_MOUNT,
                    "--role", role, json.dumps(list(payload)))))
    return command


def _run_role(command: Sequence[str], role: str, timeout: int, *,
              on_process: Any = None, on_observed: Any = None,
              on_output: Any = None, stdin_bytes: bytes | None = None) -> dict[str, Any]:
    """Consume only the fixed helper's startup frame, then permit workload execution.

    Workload bytes after the handshake are data, never observations. Both streams and the
    startup deadline are bounded. No report descriptor or broker socket is inherited.
    """
    started = time.monotonic_ns()
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, close_fds=True, start_new_session=True)
    if on_process is not None:
        on_process(process)
    output = {"stdout": bytearray(), "stderr": bytearray()}
    observation = None
    deadline = time.monotonic() + timeout
    selector = selectors.DefaultSelector()
    assert process.stdout is not None and process.stderr is not None and process.stdin is not None
    selector.register(process.stdout, selectors.EVENT_READ, "stdout")
    selector.register(process.stderr, selectors.EVENT_READ, "stderr")
    try:
        while selector.get_map():
            if time.monotonic() >= deadline:
                _refuse(role + " exceeded its deadline", "PRIVATE_EVALUATOR_TIMEOUT")
            for key, _ in selector.select(timeout=0.1):
                chunk = os.read(key.fileobj.fileno(), 65536)
                if not chunk:
                    selector.unregister(key.fileobj)
                    continue
                output[key.data].extend(chunk)
                if len(output[key.data]) > MAX_OUTPUT_BYTES:
                    _refuse(role + " exceeded output limit", "PRIVATE_EVALUATOR_OUTPUT_LIMIT")
                if key.data == "stdout" and observation is None and b"\n" in output["stdout"]:
                    frame, _, rest = output["stdout"].partition(b"\n")
                    if len(frame) > MAX_REQUEST_BYTES or rest:
                        _refuse("invalid helper startup frame")
                    observation = json.loads(frame)
                    _validate_observation(observation, role)
                    if on_observed is not None:
                        on_observed(observation)
                    output["stdout"].clear()
                    process.stdin.write(b"GO\n")
                    if stdin_bytes:
                        if role != "candidate" or len(stdin_bytes) > MAX_CASE_STDIN_BYTES:
                            _refuse("candidate stdin exceeds the bounded case contract")
                        process.stdin.write(stdin_bytes)
                    process.stdin.close()
                    process.stdin = None
                elif observation is not None and on_output is not None:
                    on_output(key.data, chunk)
        process.wait(timeout=max(0.1, deadline - time.monotonic()))
        if observation is None:
            _refuse(role + " did not establish its boundary: " + output["stderr"].decode("utf-8", "replace"),
                    "PRIVATE_EVALUATOR_UNAVAILABLE")
        return {"returncode": process.returncode, "stdout": bytes(output["stdout"]),
                "stderr": bytes(output["stderr"]), "observation": observation,
                "duration_ns": time.monotonic_ns() - started}
    finally:
        selector.close()
        if process.poll() is None:
            process.kill()
        try:
            process.wait(timeout=10)
        finally:
            for stream in (process.stdin, process.stdout, process.stderr):
                if stream is not None:
                    stream.close()


def _request(value: Any, roots: Sequence[Mapping[str, Any]], default_cwd: str) -> tuple[list[str], str, int, str]:
    if (not isinstance(value, dict) or
            set(value) not in ({"argv", "cwd", "timeout"},
                               {"argv", "cwd", "timeout", "principal"})):
        _refuse("candidate.run accepts only argv, cwd and timeout")
    principal = value.get("principal", "worker")
    if principal not in ("worker", "candidate"):
        _refuse("unknown candidate process principal")
    argv, cwd, timeout = value["argv"], value["cwd"], value["timeout"]
    if (not isinstance(argv, list) or not argv or len(argv) > 256
            or not all(isinstance(v, str) and "\0" not in v and len(v) <= 8192 for v in argv)):
        _refuse("invalid worker argv")
    executable = _absolute(argv[0])
    if not any(_inside(executable, root["target"]) for root in roots) and not any(
            _inside(executable, prefix) for prefix in ("/usr/bin", "/bin")):
        _refuse("worker executable is outside system binaries/candidate roots")
    cwd = default_cwd if cwd is None else _absolute(cwd)
    if not any(_inside(cwd, root["target"]) for root in roots):
        _refuse("worker cwd is outside candidate roots")
    if isinstance(timeout, bool) or not isinstance(timeout, int) or not 1 <= timeout <= MAX_WORKER_SECONDS:
        _refuse("invalid worker timeout")
    return argv, cwd, timeout, principal


def _read_message(connection: socket.socket, maximum: int) -> Any:
    chunks = bytearray()
    while b"\n" not in chunks:
        chunk = connection.recv(min(65536, maximum + 1 - len(chunks)))
        if not chunk:
            _refuse("incomplete broker message")
        chunks.extend(chunk)
        if len(chunks) > maximum:
            _refuse("broker message exceeds limit")
    frame, _, rest = chunks.partition(b"\n")
    if rest:
        _refuse("trailing broker message bytes")
    return json.loads(frame)


def _own_tree(directory: Path, uid: int) -> None:
    # Called only on newly copied, validated trees before any worker exists.
    for parent, directories, files in os.walk(directory, followlinks=False):
        for name in directories:
            path = Path(parent) / name
            if path.is_symlink():
                os.chown(path, uid, uid, follow_symlinks=False)
        for name in files:
            os.chown(Path(parent) / name, uid, uid, follow_symlinks=False)
        os.chown(parent, uid, uid, follow_symlinks=False)


def _reclaim_tree(directory: Path) -> None:
    """Restore operator ownership after the worker's namespace has exited; never follow links."""
    def visit(descriptor: int) -> None:
        os.fchown(descriptor, 0, 0)
        os.fchmod(descriptor, stat.S_IMODE(os.fstat(descriptor).st_mode) | 0o700)
        for name in os.listdir(descriptor):
            info = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
            if stat.S_ISDIR(info.st_mode):
                child = os.open(name, _DIR_FLAGS, dir_fd=descriptor)
                try:
                    visit(child)
                finally:
                    os.close(child)
            else:
                os.chown(name, 0, 0, dir_fd=descriptor, follow_symlinks=False)
    descriptor = _open_directory(directory)
    try:
        visit(descriptor)
    finally:
        os.close(descriptor)


def _bootstrap(plan_path: str) -> int:
    plan = json.loads(Path(plan_path).read_text())
    runtime = Path(plan["runtime"])
    evidence: dict[str, Any] = {"profileId": PROFILE_ID, "runId": plan["runId"],
                              "bootstrapSha256": plan["bootstrapSha256"], "workers": [],
                              "startupPolicySha256": plan["startupPolicySha256"],
                              "inputs": plan["roots"], "verifierIdentity": plan["verifierIdentity"],
                              "toolchain": plan.get("toolchain"),
                              "bubblewrap": plan.get("bubblewrap"),
                              "nonClaims": ["Role isolation does not establish examiner logic correctness.",
                                            "Kernel, system tools and trusted examiner are part of the trust base.",
                                            "Nested user namespace creation is not disabled by this backend."]}
    stop = threading.Event()
    errors: list[str] = []
    socket_path = runtime / "broker.sock"
    worker_socket_path = runtime / "worker-broker.sock"
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    worker_server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        if os.getuid() != 0 or os.getgid() != 0:
            _refuse("bootstrap did not enter its mapped root identity")
        executable = plan.get("bubblewrap")
        if (not isinstance(executable, dict) or not isinstance(executable.get("path"), str)
                or not isinstance(executable.get("sha256"), str)):
            _refuse("bubblewrap executable identity is absent")
        with Path(executable["path"]).open("rb") as stream:
            if hashlib.file_digest(stream, "sha256").hexdigest() != executable["sha256"]:
                _refuse("bubblewrap executable changed before private roles ran")
        case_copier = Path(plan["caseCopier"])
        if hashlib.sha256(case_copier.read_bytes()).hexdigest() != plan["caseCopierSha256"]:
            _refuse("scoped case copier changed before private roles ran")
        copy_case_tree = runpy.run_path(str(case_copier))["copy_case_tree"]
        evidence["bootstrap"] = _observations("bootstrap")
        for name, expected in (("uidMap", plan["operatorUid"]), ("gidMap", plan["operatorGid"])):
            mapping = evidence["bootstrap"][name]
            if (_mapped_identity(mapping, 0) != expected
                    or _mapped_identity(mapping, 1) in (0, expected)
                    or _mapped_identity(mapping, 2) in (0, expected, _mapped_identity(mapping, 1))):
                _refuse("subordinate UID/GID mapping is unavailable")
        (runtime / "bootstrap-ready").write_text("ready\n")
        deadline = time.monotonic() + BOOTSTRAP_HANDSHAKE_SECONDS
        while not (runtime / "bootstrap-go").exists():
            if time.monotonic() >= deadline:
                _refuse("daemon did not acknowledge bootstrap manager properties")
            time.sleep(0.02)
        # A relative bind avoids AF_UNIX's pathname-length limit for deep runtime directories.
        os.chdir(runtime)
        server.bind("broker.sock")
        socket_path.chmod(0o600)
        server.listen(1)
        server.settimeout(0.1)
        plan["socket"] = str(socket_path)
        worker_server.bind("worker-broker.sock")
        os.chown(worker_socket_path, 0, 1)
        worker_socket_path.chmod(0o660)
        worker_server.listen(1)
        worker_server.settimeout(0.1)
        plan["workerSocket"] = str(worker_socket_path)
        sessions: dict[str, dict[str, Any]] = {}
        sessions_lock = threading.Lock()
        active_worker = threading.Event()
        active_worker_roots: dict[str, Any] = {"roots": []}
        cases: dict[str, dict[str, Any]] = {}
        opened_cases = {"count": 0}
        evidence["workerBrokerCalls"] = []
        evidence["caseLeases"] = []

        def copied_roots(call_number: int | str, principal: str) -> tuple[Path, list[dict[str, str]]]:
            work = runtime / "workers" / str(call_number)
            work.mkdir(mode=0o700)
            roots = []
            for index, root in enumerate(plan["roots"]):
                copy = work / str(index)
                digest = copy_frozen_tree(Path(root["frozen"]), copy)
                if digest != root["identity"]:
                    _refuse("frozen worker input identity changed")
                _own_tree(copy, 1 if principal == "worker" else 2)
                roots.append({"source": str(copy), "target": root["target"]})
            return work, roots

        def case_by_handle(value: Any) -> dict[str, Any]:
            if not isinstance(value, str) or value not in cases:
                _refuse("unknown scoped case lease")
            return cases[value]

        def remove_private_tree(path: Path) -> None:
            if path.exists():
                _reclaim_tree(path)
                shutil.rmtree(path)

        def worker_generation(case: Mapping[str, Any]) -> dict[str, Any]:
            scratch = case["work"] / ("guard-" + uuid.uuid4().hex)
            try:
                return copy_case_tree(case["workerPath"], scratch,
                                      logical_root=case["logicalRoot"])
            finally:
                remove_private_tree(scratch)

        def require_worker_generation(case: Mapping[str, Any]) -> None:
            observed = worker_generation(case)
            if observed != case["generation"]:
                _refuse("worker case view changed without a scoped copy-in")

        def open_case(request: Mapping[str, Any], peer_pid: int) -> dict[str, Any]:
            if set(request) != {"op", "caseRoot"}:
                _refuse("scoped case open has wrong shape")
            logical = _absolute(request["caseRoot"])
            selected = None
            relative = None
            for root in active_worker_roots["roots"]:
                if logical != root["target"] and _inside(logical, root["target"]):
                    selected = root
                    relative = Path(logical).relative_to(root["target"])
                    break
            if selected is None or relative is None or not relative.parts:
                _refuse("scoped case root is not strictly inside the active worker copy")
            if len(cases) >= MAX_CASE_LEASES or opened_cases["count"] >= MAX_CASE_LEASES:
                _refuse("scoped case lease limit reached")
            worker_path = Path(selected["source"]) / relative
            info = os.lstat(worker_path)
            if not stat.S_ISDIR(info.st_mode):
                _refuse("scoped case root is not a real directory in the worker copy")
            for item in cases.values():
                if (_inside(logical, item["logicalRoot"]) or _inside(item["logicalRoot"], logical)):
                    _refuse("scoped case root overlaps an active lease")
            opened_cases["count"] += 1
            handle = uuid.uuid4().hex
            work, roots = copied_roots("case-" + handle, "candidate")
            view = work / "candidate-view"
            try:
                generation = copy_case_tree(worker_path, view, logical_root=logical)
                _own_tree(view, 2)
                matching = next(root for root in roots if root["target"] == selected["target"])
                mountpoint = Path(matching["source"]) / relative
                try:
                    mountpoint.mkdir(parents=True, exist_ok=False)
                except FileExistsError:
                    # A leased directory the candidate input already contains is hidden by the
                    # case bind mount; any other kind of entry there is refused.
                    if not stat.S_ISDIR(os.lstat(mountpoint).st_mode):
                        _refuse("scoped case mountpoint is not a real directory in the candidate copy")
            except BaseException:
                remove_private_tree(work)
                raise
            record = {"handle": handle, "logicalRoot": logical,
                      "workerPeerPid": peer_pid, "workerPeerUid": 1,
                      "candidateUid": 2, "copyIn": generation,
                      "events": ["open", "copy-in"]}
            case = {"handle": handle, "logicalRoot": logical,
                    "workerPath": worker_path, "view": view, "work": work,
                    "roots": roots, "generation": generation,
                    "handles": set(), "dirty": False, "record": record}
            cases[handle] = case
            evidence["caseLeases"].append(record)
            return {"caseHandle": handle, "generation": generation}

        def copy_out_case(case: dict[str, Any]) -> dict[str, Any]:
            if case["handles"]:
                _refuse("scoped case copy-out requires torn-down candidate handles")
            if not case["dirty"]:
                _refuse("scoped case has no candidate output to copy")
            require_worker_generation(case)
            stage = case["work"] / ("copy-out-" + uuid.uuid4().hex)
            old = case["work"] / ("old-worker-" + uuid.uuid4().hex)
            output = copy_case_tree(case["view"], stage,
                                    logical_root=case["logicalRoot"])
            _own_tree(stage, 1)
            os.rename(case["workerPath"], old)
            try:
                os.rename(stage, case["workerPath"])
            except BaseException:
                os.rename(old, case["workerPath"])
                raise
            remove_private_tree(old)
            case["generation"] = output
            case["dirty"] = False
            case["record"]["copyOut"] = output
            case["record"]["events"].append("copy-out")
            return {"generation": output}

        def sync_in_case(case: dict[str, Any], expected: Any) -> dict[str, Any]:
            if case["handles"] or case["dirty"] or expected != case["generation"]:
                _refuse("scoped case copy-in requires a quiescent matching generation")
            stage = case["work"] / ("copy-in-" + uuid.uuid4().hex)
            old = case["work"] / ("old-candidate-" + uuid.uuid4().hex)
            incoming = copy_case_tree(case["workerPath"], stage,
                                      logical_root=case["logicalRoot"])
            _own_tree(stage, 2)
            os.rename(case["view"], old)
            try:
                os.rename(stage, case["view"])
            except BaseException:
                os.rename(old, case["view"])
                raise
            remove_private_tree(old)
            case["generation"] = incoming
            case["record"]["events"].append("copy-in")
            return {"generation": incoming}

        def close_case(case: dict[str, Any]) -> dict[str, Any]:
            if case["handles"] or case["dirty"]:
                _refuse("scoped case close requires copy-out and torn-down handles")
            require_worker_generation(case)
            remove_private_tree(case["work"])
            case["record"]["events"].append("close")
            cases.pop(case["handle"])
            return {"closed": True}

        def worker_broker() -> None:
            calls = 0
            requests = 0
            while not stop.is_set():
                try:
                    connection, _ = worker_server.accept()
                except socket.timeout:
                    continue
                with connection:
                    connection.settimeout(MAX_WORKER_SECONDS + 10)
                    try:
                        peer_pid, peer_uid, peer_gid = struct.unpack(
                            "3i", connection.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
                        if not active_worker.is_set() or peer_uid != 1 or peer_gid != 1:
                            _refuse("worker broker peer refused")
                        request = _read_message(connection, MAX_REQUEST_BYTES)
                        requests += 1
                        if requests > MAX_CASE_REQUESTS or not isinstance(request, dict):
                            _refuse("worker broker request bound or shape refused")
                        operation = request.get("op")
                        if operation == "case_open":
                            response = open_case(request, peer_pid)
                        elif operation in ("case_start", "case_stream", "case_wait",
                                           "case_signal", "case_teardown", "case_copy_out",
                                           "case_sync_in", "case_close", "case_status"):
                            case = case_by_handle(request.get("caseHandle"))
                            if operation == "case_start":
                                if set(request) not in ({"op", "caseHandle", "argv", "cwd",
                                                         "timeout", "stdinB64"},
                                                        {"op", "caseHandle", "argv", "cwd",
                                                         "timeout", "stdinB64", "env"}):
                                    _refuse("scoped case start has wrong shape")
                                response = start_candidate(
                                    {key: value for key, value in request.items()
                                     if key != "caseHandle"}, requests, case=case)
                            elif operation in ("case_stream", "case_wait", "case_signal",
                                               "case_teardown"):
                                if (not isinstance(request.get("handle"), str) or
                                        request["handle"] not in case["handles"] or
                                        sessions[request["handle"]]["caseHandle"] !=
                                        case["handle"]):
                                    _refuse("candidate process handle is outside scoped case")
                                inner_op = operation.removeprefix("case_")
                                inner = {key: value for key, value in request.items()
                                         if key != "caseHandle"}
                                inner["op"] = inner_op
                                response = session_request(inner)
                                case["record"]["events"].append(inner_op)
                                if operation == "case_teardown":
                                    case["handles"].remove(request["handle"])
                            elif operation == "case_status":
                                if set(request) != {"op", "caseHandle"}:
                                    _refuse("scoped status has wrong shape")
                                response = {"handles": len(case["handles"]),
                                            "dirty": case["dirty"],
                                            "workerChanged": (worker_generation(case) != case["generation"]
                                                              if not case["handles"] else None),
                                            "generation": case["generation"]}
                            elif operation == "case_copy_out":
                                if set(request) != {"op", "caseHandle"}:
                                    _refuse("scoped copy-out has wrong shape")
                                response = copy_out_case(case)
                            elif operation == "case_sync_in":
                                if set(request) != {"op", "caseHandle", "expectedGeneration"}:
                                    _refuse("scoped copy-in has wrong shape")
                                response = sync_in_case(case, request["expectedGeneration"])
                            else:
                                if set(request) != {"op", "caseHandle"}:
                                    _refuse("scoped close has wrong shape")
                                response = close_case(case)
                        elif operation == "run_unstateful":
                            if (set(request) != {"op", "argv", "cwd", "timeout"}
                                    or calls >= MAX_REQUESTS):
                                _refuse("worker broker accepts only bounded unstateful runs")
                            argv, cwd, timeout, principal = _request(
                                {"argv": request["argv"], "cwd": request["cwd"],
                                 "timeout": request["timeout"], "principal": "candidate"},
                                plan["roots"], plan["cwd"])
                            calls += 1
                            work, roots = copied_roots("from-worker-" + str(calls), principal)
                            command = _sandbox(plan, principal, roots, argv, cwd)
                            try:
                                result = _run_role(command, principal, timeout)
                            finally:
                                _reclaim_tree(work)
                            observation = result.pop("observation")
                            evidence["workers"].append({
                                "argv": argv, "cwd": cwd, "principal": principal,
                                "origin": "worker-broker", "observation": observation,
                                "returncode": result["returncode"],
                                "stdoutSha256": hashlib.sha256(result["stdout"]).hexdigest(),
                                "stderrSha256": hashlib.sha256(result["stderr"]).hexdigest(),
                                "duration_ns": result["duration_ns"]})
                            evidence["workerBrokerCalls"].append({
                                "peerPid": peer_pid, "peerUid": peer_uid, "peerGid": peer_gid,
                                "candidateUid": observation["uid"],
                                "candidateGid": observation["gid"],
                                "candidatePidNamespace": observation["namespaces"]["pid"],
                                "argvSha256": hashlib.sha256(json.dumps(argv).encode()).hexdigest()})
                            result["stdout"] = base64.b64encode(result["stdout"]).decode("ascii")
                            result["stderr"] = base64.b64encode(result["stderr"]).decode("ascii")
                            result["observation"] = observation
                            response = result
                        else:
                            _refuse("worker broker operation is unsupported")
                        connection.sendall(json.dumps(response).encode() + b"\n")
                    except Exception as exc:
                        errors.append(str(exc))
                        try:
                            connection.sendall(json.dumps({"error": str(exc)}).encode() + b"\n")
                        except OSError:
                            pass
                        stop.set()
                        worker_server.close()

        def start_candidate(request: Mapping[str, Any], call_number: int,
                            case: dict[str, Any] | None = None) -> dict[str, Any]:
            expected = ({"op", "argv", "cwd", "timeout", "stdinB64"} if case is not None
                        else {"op", "argv", "cwd", "timeout"})
            if case is not None and set(request) == expected | {"env"}:
                expected = expected | {"env"}
            if set(request) != expected:
                _refuse("isolated start request has wrong shape")
            environment = request.get("env", {})
            if (not isinstance(environment, dict) or
                    any(key not in CANDIDATE_ENV_ALLOWED or not isinstance(value, str)
                        or re.fullmatch(CANDIDATE_ENV_ALLOWED[key], value) is None
                        for key, value in environment.items())):
                _refuse("candidate environment is outside the determinism allowlist")
            argv, cwd, timeout, principal = _request(
                {"argv": request["argv"], "cwd": request["cwd"],
                 "timeout": request["timeout"], "principal": "candidate"},
                plan["roots"], plan["cwd"])
            stdin_bytes = None
            if case is not None:
                if not isinstance(request["stdinB64"], str):
                    _refuse("scoped case stdin is not base64 text")
                stdin_bytes = base64.b64decode(request["stdinB64"], validate=True)
                if len(stdin_bytes) > MAX_CASE_STDIN_BYTES:
                    _refuse("scoped case stdin exceeds limit")
                require_worker_generation(case)
                work, roots = None, case["roots"]
                case_bind = {"source": str(case["view"]),
                             "target": case["logicalRoot"]}
            else:
                work, roots = copied_roots(call_number, principal)
                case_bind = None
            command = _sandbox(plan, principal, roots, argv, cwd, case_bind=case_bind,
                               environment=environment)
            handle = uuid.uuid4().hex
            session: dict[str, Any] = {
                "argv": argv, "cwd": cwd, "work": work,
                "ready": threading.Event(), "done": threading.Event(),
                "process": None, "observation": None, "result": None,
                "error": None, "stdout": bytearray(), "stderr": bytearray(),
                "closed": False, "events": ["start"],
                "caseHandle": case["handle"] if case is not None else None,
            }
            sessions[handle] = session
            if case is not None:
                case["handles"].add(handle)
                case["dirty"] = True
                case["record"]["events"].append("start")

            def on_process(process: subprocess.Popen[bytes]) -> None:
                session["process"] = process

            def on_observed(observation: dict[str, Any]) -> None:
                session["observation"] = observation
                session["ready"].set()

            def on_output(stream: str, chunk: bytes) -> None:
                with sessions_lock:
                    session[stream].extend(chunk)

            def execute() -> None:
                try:
                    result = _run_role(command, principal, timeout, on_process=on_process,
                                       on_observed=on_observed, on_output=on_output,
                                       stdin_bytes=stdin_bytes)
                    session["result"] = result
                    evidence["workers"].append({
                        "argv": argv, "cwd": cwd, "principal": principal,
                        "observation": result["observation"],
                        "returncode": result["returncode"],
                        "stdoutSha256": hashlib.sha256(result["stdout"]).hexdigest(),
                        "stderrSha256": hashlib.sha256(result["stderr"]).hexdigest(),
                        "duration_ns": result["duration_ns"],
                        "asyncEvents": session["events"],
                        "caseHandle": session["caseHandle"],
                    })
                except Exception as exc:
                    session["error"] = type(exc).__name__ + ": " + str(exc)
                    errors.append(session["error"])
                finally:
                    if work is not None:
                        try:
                            _reclaim_tree(work)
                        except Exception as exc:
                            session["error"] = "reclaim: " + type(exc).__name__ + ": " + str(exc)
                            errors.append(session["error"])
                    session["ready"].set()
                    session["done"].set()

            runner = threading.Thread(target=execute, daemon=True)
            session["thread"] = runner
            runner.start()
            if not session["ready"].wait(timeout=15) or session["observation"] is None:
                _refuse("isolated candidate did not establish its role boundary")
            return {"handle": handle, "observation": session["observation"]}

        def session_request(request: Mapping[str, Any]) -> dict[str, Any]:
            if (set(request) not in ({"op", "handle"}, {"op", "handle", "waitMs"},
                                     {"op", "handle", "stdoutOffset", "stderrOffset"},
                                     {"op", "handle", "signal"})
                    or not isinstance(request.get("handle"), str)):
                _refuse("isolated candidate session request has wrong shape")
            session = sessions.get(request["handle"])
            if session is None or session["closed"]:
                _refuse("unknown or closed isolated candidate handle")
            op = request["op"]
            if op == "stream":
                if set(request) != {"op", "handle", "stdoutOffset", "stderrOffset"}:
                    _refuse("stream request has wrong shape")
                offsets = (request["stdoutOffset"], request["stderrOffset"])
                if any(type(value) is not int or value < 0 for value in offsets):
                    _refuse("stream offsets must be nonnegative integers")
                with sessions_lock:
                    stdout = bytes(session["stdout"])
                    stderr = bytes(session["stderr"])
                if offsets[0] > len(stdout) or offsets[1] > len(stderr):
                    _refuse("stream offset exceeds observed output")
                session["events"].append("stream")
                out = stdout[offsets[0]:offsets[0] + 65536]
                err = stderr[offsets[1]:offsets[1] + 65536]
                return {"done": session["done"].is_set(),
                        "stdoutB64": base64.b64encode(out).decode("ascii"),
                        "stderrB64": base64.b64encode(err).decode("ascii"),
                        "stdoutNext": offsets[0] + len(out),
                        "stderrNext": offsets[1] + len(err)}
            if op == "wait" and set(request) in ({"op", "handle"}, {"op", "handle", "waitMs"}):
                wait_ms = request.get("waitMs", 0)
                if type(wait_ms) is not int or not 0 <= wait_ms <= MAX_CASE_WAIT_MS:
                    _refuse("wait budget is outside the allowed range")
                session["events"].append("wait")
                if wait_ms:
                    session["done"].wait(timeout=wait_ms / 1000)
                if not session["done"].is_set():
                    return {"done": False}
                if session["error"] is not None or session["result"] is None:
                    _refuse("isolated candidate failed: " + str(session["error"]))
                result = session["result"]
                return {"done": True, "returncode": result["returncode"],
                        "stdoutB64": base64.b64encode(result["stdout"]).decode("ascii"),
                        "stderrB64": base64.b64encode(result["stderr"]).decode("ascii")}
            if op == "signal" and set(request) == {"op", "handle", "signal"}:
                selected = {"SIGKILL": signal.SIGKILL,
                            "SIGTERM": signal.SIGTERM}.get(request["signal"])
                if selected is None:
                    _refuse("isolated candidate signal is not allowed")
                process = session["process"]
                delivered = bool(process is not None and process.poll() is None)
                if delivered:
                    try:
                        os.killpg(process.pid, selected)
                    except ProcessLookupError:
                        delivered = False
                session["events"].append("signal:" + request["signal"])
                return {"delivered": delivered}
            if op == "teardown" and set(request) == {"op", "handle"}:
                process = session["process"]
                if process is not None and process.poll() is None:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                session["thread"].join(timeout=10)
                if session["thread"].is_alive() or not session["done"].is_set():
                    _refuse("isolated candidate teardown did not finish")
                session["events"].append("teardown")
                session["closed"] = True
                return {"closed": True, "done": True}
            _refuse("unknown isolated candidate session operation")

        def broker() -> None:
            calls = 0
            while not stop.is_set():
                try:
                    connection, _ = server.accept()
                except socket.timeout:
                    continue
                with connection:
                    connection.settimeout(MAX_WORKER_SECONDS + 10)
                    try:
                        _pid, uid, gid = struct.unpack("3i", connection.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
                        if uid != 0 or gid != 0:
                            _refuse("broker peer refused")
                        request = _read_message(connection, MAX_REQUEST_BYTES)
                        if isinstance(request, dict) and request.get("op") == "start":
                            if calls >= MAX_REQUESTS:
                                _refuse("isolated launch limit refused")
                            calls += 1
                            response = start_candidate(request, calls)
                            connection.sendall(json.dumps(response).encode() + b"\n")
                            continue
                        if isinstance(request, dict) and "op" in request:
                            response = session_request(request)
                            connection.sendall(json.dumps(response).encode() + b"\n")
                            continue
                        if calls >= MAX_REQUESTS:
                            _refuse("legacy launch limit refused")
                        argv, cwd, timeout, principal = _request(request, plan["roots"], plan["cwd"])
                        calls += 1
                        work, roots = copied_roots(calls, principal)
                        command = _sandbox(plan, principal, roots, argv, cwd)
                        try:
                            if principal == "worker":
                                active_worker_roots["roots"] = roots
                                active_worker.set()
                            result = _run_role(command, principal, timeout)
                        finally:
                            if principal == "worker":
                                active_worker.clear()
                                active_worker_roots["roots"] = []
                            _reclaim_tree(work)
                        evidence["workers"].append({"argv": argv, "cwd": cwd,
                                                    "principal": principal,
                                                    "observation": result.pop("observation"),
                                                    "returncode": result["returncode"],
                                                    "stdoutSha256": hashlib.sha256(result["stdout"]).hexdigest(),
                                                    "stderrSha256": hashlib.sha256(result["stderr"]).hexdigest(),
                                                    "duration_ns": result["duration_ns"]})
                        result["stdout"] = base64.b64encode(result["stdout"]).decode("ascii")
                        result["stderr"] = base64.b64encode(result["stderr"]).decode("ascii")
                        if principal == "candidate":
                            # SO_PEERCRED is observed by the mapped bootstrap
                            # outside the candidate's PID namespace. Expose it
                            # only to the trusted examiner for a signal probe.
                            result["examinerPeerPid"] = _pid
                        connection.sendall(json.dumps(result).encode() + b"\n")
                    except Exception as exc:
                        errors.append(str(exc))
                        try:
                            connection.sendall(json.dumps({"error": str(exc)}).encode() + b"\n")
                        except OSError:
                            pass
                        stop.set()
                        server.close()

        thread = threading.Thread(target=broker, daemon=True)
        worker_thread = threading.Thread(target=worker_broker, daemon=True)
        worker_thread.start()
        thread.start()
        examiner_roots = [{"source": root["frozen"], "target": root["target"]} for root in plan["roots"]]
        command = _sandbox(plan, "examiner", examiner_roots, plan["argv"], plan["cwd"])
        evidence["examinerCommand"] = command
        examiner = _run_role(command, "examiner", plan["timeout"])
        stop.set()
        thread.join(timeout=MAX_WORKER_SECONDS + 15)
        worker_thread.join(timeout=MAX_WORKER_SECONDS + 15)
        for session in sessions.values():
            process = session["process"]
            if process is not None and process.poll() is None:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            session["thread"].join(timeout=10)
            if not session["closed"] or session["thread"].is_alive():
                errors.append("isolated candidate session was not torn down")
        for case in list(cases.values()):
            errors.append("scoped candidate case lease was not closed")
            try:
                remove_private_tree(case["work"])
            except Exception as exc:
                errors.append("scoped case reclaim failed: " + str(exc))
        if thread.is_alive() or worker_thread.is_alive() or errors:
            _refuse("broker failed or did not become quiescent: " + "; ".join(errors))
        evidence["examiner"] = examiner["observation"]
        evidence["examinerReturnCode"] = examiner["returncode"]
        for observation in [evidence["examiner"], *[worker["observation"] for worker in evidence["workers"]]]:
            for name in ("uidMap", "gidMap"):
                if observation[name] != evidence["bootstrap"][name]:
                    _refuse("role mapping differs from bootstrap mapping")
        for worker in evidence["workers"]:
            for namespace in ("pid", "mnt"):
                if worker["observation"]["namespaces"][namespace] == evidence["examiner"]["namespaces"][namespace]:
                    _refuse("worker and examiner namespace observations coincide")
        evidence["reportMountExclusive"] = True
        evidence["rolesCompleted"] = True
        sys.stdout.buffer.write(examiner["stdout"])
        sys.stderr.buffer.write(examiner["stderr"])
        return examiner["returncode"] if examiner["returncode"] >= 0 else 1
    except Exception as exc:
        evidence["error"] = str(exc)
        return 1
    finally:
        stop.set()
        server.close()
        worker_server.close()
        (runtime / "boundary.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")


def _candidate_request(request: Mapping[str, Any]) -> dict[str, Any]:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(MAX_WORKER_SECONDS + 15)
        connection.connect(BROKER_MOUNT)
        connection.sendall(json.dumps(request).encode() + b"\n")
        result = _read_message(connection, MAX_OUTPUT_BYTES * 4)
    if "error" in result:
        raise RuntimeError(result["error"])
    return result


def _candidate_run(argv: Sequence[str], *, cwd: str | None = None, timeout: int = 30,
                   principal: str = "worker") -> Any:
    result = _candidate_request({"argv": list(argv), "cwd": cwd,
                                 "timeout": timeout, "principal": principal})
    result["stdout"] = base64.b64decode(result["stdout"], validate=True)
    result["stderr"] = base64.b64decode(result["stderr"], validate=True)
    return types.SimpleNamespace(**result)


def _candidate_start_isolated(argv: Sequence[str], *, cwd: str | None = None,
                              timeout: int = 30) -> Any:
    result = _candidate_request({"op": "start", "argv": list(argv),
                                 "cwd": cwd, "timeout": timeout})
    return types.SimpleNamespace(**result)


def _candidate_stream_isolated(handle: str, *, stdout_offset: int = 0,
                               stderr_offset: int = 0) -> Any:
    result = _candidate_request({"op": "stream", "handle": handle,
                                 "stdoutOffset": stdout_offset,
                                 "stderrOffset": stderr_offset})
    result["stdout"] = base64.b64decode(result.pop("stdoutB64"), validate=True)
    result["stderr"] = base64.b64decode(result.pop("stderrB64"), validate=True)
    return types.SimpleNamespace(**result)


def _candidate_wait_isolated(handle: str, *, timeout: float = MAX_WORKER_SECONDS) -> Any:
    deadline = time.monotonic() + timeout
    while True:
        result = _candidate_request({"op": "wait", "handle": handle})
        if result["done"]:
            result["stdout"] = base64.b64decode(result.pop("stdoutB64"), validate=True)
            result["stderr"] = base64.b64decode(result.pop("stderrB64"), validate=True)
            return types.SimpleNamespace(**result)
        if time.monotonic() >= deadline:
            raise TimeoutError("isolated candidate wait exceeded caller deadline")
        time.sleep(0.02)


def _candidate_signal_isolated(handle: str, selected: str) -> bool:
    return bool(_candidate_request({"op": "signal", "handle": handle,
                                    "signal": selected})["delivered"])


def _candidate_teardown_isolated(handle: str) -> bool:
    return bool(_candidate_request({"op": "teardown", "handle": handle})["closed"])


def _role(role: str, payload: Sequence[str]) -> None:
    # No workload code executes before this fixed helper emits its observation and receives
    # acknowledgement. The parent consumes exactly that frame and treats later stdout as data.
    print(json.dumps(_observations(role)), flush=True)
    # Read exactly the three acknowledgement bytes. Candidate stdin follows them on the
    # same pipe, and a larger read would consume the first byte of that payload.
    acknowledgement = b""
    while len(acknowledgement) < 3:
        chunk = os.read(0, 3 - len(acknowledgement))
        if not chunk:
            break
        acknowledgement += chunk
    if acknowledgement != b"GO\n":
        _refuse("supervisor did not acknowledge role boundary")
    if role != "candidate":
        descriptor = os.open("/dev/null", os.O_RDONLY)
        os.dup2(descriptor, 0)
        os.close(descriptor)
    if role == "worker":
        os.execv(payload[0], list(payload))
    if role == "candidate":
        os.execv(payload[0], list(payload))
    candidate = types.ModuleType("candidate")
    candidate.run = _candidate_run
    candidate.run_isolated = lambda argv, *, cwd=None, timeout=30: _candidate_run(
        argv, cwd=cwd, timeout=timeout, principal="candidate")
    candidate.start_isolated = _candidate_start_isolated
    candidate.stream_isolated = _candidate_stream_isolated
    candidate.wait_isolated = _candidate_wait_isolated
    candidate.signal_isolated = _candidate_signal_isolated
    candidate.teardown_isolated = _candidate_teardown_isolated
    sys.modules["candidate"] = candidate
    # Only identified verifier helpers enter Python's search path. Candidate cwd stays out.
    sys.path.insert(0, str(Path(payload[1]).parent))
    sys.path.insert(0, VERIFIER_MOUNT)
    sys.argv = list(payload[1:])
    runpy.run_path(payload[1], run_name="__main__")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--bootstrap":
        raise SystemExit(_bootstrap(sys.argv[2]))
    if len(sys.argv) == 4 and sys.argv[1] == "--role" and sys.argv[2] in ("examiner", "worker", "candidate"):
        _role(sys.argv[2], json.loads(sys.argv[3]))
    else:
        raise SystemExit("invalid private evaluator invocation")
