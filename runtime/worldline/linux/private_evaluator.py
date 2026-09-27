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
import runpy
import selectors
import socket
import stat
import struct
import subprocess
import sys
import threading
import time
import types
from typing import Any, Mapping, Sequence

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
HELPER_MOUNT = "/run/worldline-evaluator.py"
MAX_TREE_BYTES = 268_435_456
MAX_TREE_ENTRIES = 100_000
MAX_OUTPUT_BYTES = 1_048_576
MAX_REQUEST_BYTES = 65_536
MAX_REQUESTS = 32
MAX_WORKER_SECONDS = 120
MAX_EVALUATOR_SECONDS = 600
TOOLCHAIN_MOUNT = "/opt/worldline-gnat"
_TOOLCHAIN_EXECUTABLES = (
    "gnat-aarch64-linux-16.1.0-1/bin/gcc",
    "gprbuild-aarch64-linux-26.0.0-1/bin/gprbuild",
    "gnatprove-aarch64-linux-16.1.0-1/bin/gnatprove",
    "gnatprove-aarch64-linux-16.1.0-1/libexec/spark/bin/why3",
    "gnatprove-aarch64-linux-16.1.0-1/libexec/spark/bin/alt-ergo",
    "gnatprove-aarch64-linux-16.1.0-1/libexec/spark/bin/cvc5",
    "gnatprove-aarch64-linux-16.1.0-1/libexec/spark/bin/z3",
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


class PrivateEvaluator:
    def __init__(self, systemd: Any):
        self.systemd = systemd

    def run(self, spec: PrivateEvaluationSpec, *, resource_properties: Sequence[str] = ()) -> dict[str, Any]:
        """Run a trusted Python examiner. Never interpret or admit its report here."""
        from ..errors import WorldlineError
        try:
            return self._run(spec, resource_properties)
        except (BackendFailure, OSError, ValueError) as exc:
            raise WorldlineError(getattr(exc, "code", "PRIVATE_EVALUATOR_FAILED"), str(exc)) from exc

    def _run(self, spec: PrivateEvaluationSpec, resource_properties: Sequence[str]) -> dict[str, Any]:
        _validate_spec(spec)
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
        startup_policy = spec.runtime / "trusted.py"
        startup_policy.write_bytes(Path(__file__).parents[1].joinpath("trusted.py").read_bytes())
        startup_policy.chmod(0o444)
        plan = {"profileId": PROFILE_ID, "runId": spec.run_id, "roots": roots,
                "verifier": str(verifier), "verifierIdentity": verifier_identity,
                "argv": list(spec.argv), "cwd": spec.cwd, "runtime": str(spec.runtime),
                "report": str(spec.report_directory), "helper": str(helper),
                "startupPolicy": str(startup_policy),
                "bootstrapSha256": hashlib.sha256(helper.read_bytes()).hexdigest(),
                "startupPolicySha256": hashlib.sha256(startup_policy.read_bytes()).hexdigest(),
                "timeout": spec.timeout_seconds, "operatorUid": os.getuid(), "operatorGid": os.getgid()}
        toolchain = Path.home() / "opt" / "gnat"
        # Fixed operator installation, never a path chosen by the candidate or project policy.
        if toolchain.exists():
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
        try:
            deadline = time.monotonic() + 15
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
        supervision = self.systemd.outcome(process, process.launcher.returncode)
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
            "toolchainMounted": os.path.isdir(TOOLCHAIN_MOUNT)}


def _validate_observation(observation: Mapping[str, Any], role: str) -> None:
    expected = 0 if role == "examiner" else 1
    status = observation.get("status", {})
    if (observation.get("role") != role or observation.get("uid") != expected
            or observation.get("gid") != expected or status.get("NoNewPrivs") != "1"
            or status.get("Uid", "").split() != [str(expected)] * 4
            or status.get("Gid", "").split() != [str(expected)] * 4
            or any(int(status.get(key, "1"), 16) != 0 for key in ("CapEff", "CapPrm", "CapBnd", "CapAmb"))
            or status.get("Groups") != ""
            or observation.get("reportMounted") != (role == "examiner")
            or observation.get("brokerMounted") != (role == "examiner")):
        _refuse("role privilege or mount observation differs from required boundary", "PRIVATE_ROLE_INVALID")


def _mapped_identity(mapping: str, identity: int) -> int:
    rows = [tuple(map(int, row.split())) for row in mapping.splitlines()]
    matches = [host + identity - start for start, host, count in rows if start <= identity < start + count]
    if len(matches) != 1:
        _refuse("UID/GID map does not uniquely map the required identity")
    return matches[0]


def _sandbox(plan: Mapping[str, Any], role: str, roots: Sequence[Mapping[str, Any]],
             payload: Sequence[str], cwd: str) -> list[str]:
    # No --unshare-user here: the bootstrap already owns the subordinate-ID user namespace.
    command = ["/usr/bin/bwrap", "--unshare-pid", "--unshare-ipc", "--unshare-uts", "--unshare-net",
               "--die-with-parent", "--new-session", "--clearenv", "--setenv", "PATH", "/usr/bin",
               "--setenv", "HOME", "/tmp", "--ro-bind", "/usr", "/usr", "--ro-bind", "/etc", "/etc"]
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
    if role == "examiner":
        command.extend(("--ro-bind", plan["verifier"], VERIFIER_MOUNT,
                        "--bind", plan["report"], REPORT_MOUNT,
                        "--bind", plan["socket"], BROKER_MOUNT))
        if plan.get("toolchain"):
            command.extend(("--ro-bind", plan["toolchain"]["source"], TOOLCHAIN_MOUNT))
    uid = "0" if role == "examiner" else "1"
    command.extend(("--chdir", cwd, "--", "/usr/bin/setpriv", "--no-new-privs", "--reuid", uid,
                    "--regid", uid, "--clear-groups", "--bounding-set=-all", "--inh-caps=-all",
                    "--ambient-caps=-all", "--", *trusted_script(HELPER_MOUNT,
                    "--role", role, json.dumps(list(payload)))))
    return command


def _run_role(command: Sequence[str], role: str, timeout: int) -> dict[str, Any]:
    """Consume only the fixed helper's startup frame, then permit workload execution.

    Workload bytes after the handshake are data, never observations. Both streams and the
    startup deadline are bounded. No report descriptor or broker socket is inherited.
    """
    started = time.monotonic_ns()
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, close_fds=True, start_new_session=True)
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
                    output["stdout"].clear()
                    process.stdin.write(b"GO\n")
                    process.stdin.close()
                    process.stdin = None
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


def _request(value: Any, roots: Sequence[Mapping[str, Any]], default_cwd: str) -> tuple[list[str], str, int]:
    if not isinstance(value, dict) or set(value) != {"argv", "cwd", "timeout"}:
        _refuse("candidate.run accepts only argv, cwd and timeout")
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
    return argv, cwd, timeout


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
                              "nonClaims": ["Role isolation does not establish examiner logic correctness.",
                                            "Kernel, system tools and trusted examiner are part of the trust base.",
                                            "Nested user namespace creation is not disabled by this backend."]}
    stop = threading.Event()
    errors: list[str] = []
    socket_path = runtime / "broker.sock"
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        if os.getuid() != 0 or os.getgid() != 0:
            _refuse("bootstrap did not enter its mapped root identity")
        evidence["bootstrap"] = _observations("bootstrap")
        for name, expected in (("uidMap", plan["operatorUid"]), ("gidMap", plan["operatorGid"])):
            mapping = evidence["bootstrap"][name]
            if (_mapped_identity(mapping, 0) != expected
                    or _mapped_identity(mapping, 1) in (0, expected)):
                _refuse("subordinate UID/GID mapping is unavailable")
        (runtime / "bootstrap-ready").write_text("ready\n")
        deadline = time.monotonic() + 15
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
                        if uid != 0 or gid != 0 or calls >= MAX_REQUESTS:
                            _refuse("broker peer or call limit refused")
                        request = _read_message(connection, MAX_REQUEST_BYTES)
                        argv, cwd, timeout = _request(request, plan["roots"], plan["cwd"])
                        calls += 1
                        work = runtime / "workers" / str(calls)
                        work.mkdir(mode=0o700)
                        roots = []
                        for index, root in enumerate(plan["roots"]):
                            copy = work / str(index)
                            digest = copy_frozen_tree(Path(root["frozen"]), copy)
                            if digest != root["identity"]:
                                _refuse("frozen worker input identity changed")
                            _own_tree(copy, 1)
                            roots.append({"source": str(copy), "target": root["target"]})
                        command = _sandbox(plan, "worker", roots, argv, cwd)
                        try:
                            result = _run_role(command, "worker", timeout)
                        finally:
                            _reclaim_tree(work)
                        evidence["workers"].append({"argv": argv, "cwd": cwd,
                                                    "observation": result.pop("observation"),
                                                    "returncode": result["returncode"],
                                                    "stdoutSha256": hashlib.sha256(result["stdout"]).hexdigest(),
                                                    "stderrSha256": hashlib.sha256(result["stderr"]).hexdigest(),
                                                    "duration_ns": result["duration_ns"]})
                        result["stdout"] = base64.b64encode(result["stdout"]).decode("ascii")
                        result["stderr"] = base64.b64encode(result["stderr"]).decode("ascii")
                        connection.sendall(json.dumps(result).encode() + b"\n")
                    except Exception as exc:
                        errors.append(str(exc))
                        try:
                            connection.sendall(json.dumps({"error": str(exc)}).encode() + b"\n")
                        except OSError:
                            pass
                        stop.set()

        thread = threading.Thread(target=broker, daemon=True)
        thread.start()
        examiner_roots = [{"source": root["frozen"], "target": root["target"]} for root in plan["roots"]]
        command = _sandbox(plan, "examiner", examiner_roots, plan["argv"], plan["cwd"])
        evidence["examinerCommand"] = command
        examiner = _run_role(command, "examiner", plan["timeout"])
        stop.set()
        thread.join(timeout=MAX_WORKER_SECONDS + 15)
        if thread.is_alive() or errors:
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
        (runtime / "boundary.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")


def _candidate_run(argv: Sequence[str], *, cwd: str | None = None, timeout: int = 30) -> Any:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(MAX_WORKER_SECONDS + 15)
        connection.connect(BROKER_MOUNT)
        connection.sendall(json.dumps({"argv": list(argv), "cwd": cwd, "timeout": timeout}).encode() + b"\n")
        result = _read_message(connection, MAX_OUTPUT_BYTES * 4)
    if "error" in result:
        raise RuntimeError(result["error"])
    result["stdout"] = base64.b64decode(result["stdout"], validate=True)
    result["stderr"] = base64.b64decode(result["stderr"], validate=True)
    return types.SimpleNamespace(**result)


def _role(role: str, payload: Sequence[str]) -> None:
    # No workload code executes before this fixed helper emits its observation and receives
    # acknowledgement. The parent consumes exactly that frame and treats later stdout as data.
    print(json.dumps(_observations(role)), flush=True)
    if sys.stdin.buffer.readline(4) != b"GO\n":
        _refuse("supervisor did not acknowledge role boundary")
    descriptor = os.open("/dev/null", os.O_RDONLY)
    os.dup2(descriptor, 0)
    os.close(descriptor)
    if role == "worker":
        os.execv(payload[0], list(payload))
    candidate = types.ModuleType("candidate")
    candidate.run = _candidate_run
    sys.modules["candidate"] = candidate
    # Only identified verifier helpers enter Python's search path. Candidate cwd stays out.
    sys.path.insert(0, str(Path(payload[1]).parent))
    sys.path.insert(0, VERIFIER_MOUNT)
    sys.argv = list(payload[1:])
    runpy.run_path(payload[1], run_name="__main__")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--bootstrap":
        raise SystemExit(_bootstrap(sys.argv[2]))
    if len(sys.argv) == 4 and sys.argv[1] == "--role" and sys.argv[2] in ("examiner", "worker"):
        _role(sys.argv[2], json.loads(sys.argv[3]))
    else:
        raise SystemExit("invalid private evaluator invocation")
