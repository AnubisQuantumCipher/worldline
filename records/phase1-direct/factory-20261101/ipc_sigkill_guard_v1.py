"""One fixed bounded monitor for the new private IPC child-SIGKILL control.

Sampling detects capacity loss; it is not a filesystem quota. A failed or
incomplete cleanup is UNVERIFIED and cannot authorize a successor diagnostic.
"""
from pathlib import Path
import datetime
import json
import os
import re
import resource
import signal
import stat
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
JOB = HERE / "private-ipc-sigkill-job-v1"
INNER = ROOT / "records/phase1-direct/completion-20261026"
LOG = HERE / "ipc_sigkill_guard_v1.jsonl"
RESERVE = 10_000_000_000
UNIT_PATTERN = r"wl-phase1-[0-9a-f]{32}\.scope"


def record(stream, event):
    event = dict(event, utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    data = json.dumps(event, sort_keys=True) + "\n"
    if len(data) > 16384 or stream.tell() + len(data) > 512 * 1024:
        raise RuntimeError("monitor receipt budget exceeded")
    if stream.write(data) != len(data):
        raise RuntimeError("short monitor write")
    stream.flush()


def best_effort_record(stream, event):
    try:
        record(stream, event)
        return True
    except BaseException:
        # Cleanup never depends on the receipt device remaining writable.
        return False


def read_small(path, limit):
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_size > limit:
            raise RuntimeError("nonregular or oversized control receipt")
        raw = os.read(descriptor, limit + 1)
        if len(raw) > limit:
            raise RuntimeError("control receipt grew beyond bound")
        return raw
    finally:
        os.close(descriptor)


def metadata_bytes():
    pending, count, total = [JOB], 0, 0
    for _ in range(2048):
        if not pending:
            return total
        parent = pending.pop()
        if not os.path.lexists(parent):
            continue
        if parent.is_symlink():
            raise RuntimeError("outer metadata directory symlink")
        with os.scandir(parent) as entries:
            for entry in entries:
                count += 1
                if count > 2048 or entry.is_symlink():
                    raise RuntimeError("outer metadata entry bound or symlink")
                if entry.is_dir(follow_symlinks=False):
                    pending.append(Path(entry.path))
                elif entry.is_file(follow_symlinks=False):
                    total += entry.stat(follow_symlinks=False).st_size
                else:
                    raise RuntimeError("unsupported outer metadata entry")
    raise RuntimeError("outer metadata directory bound")


def command_limits():
    resource.setrlimit(resource.RLIMIT_FSIZE, (8192, 8192))


def systemctl(arguments, deadline):
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError("cleanup deadline")
    # Anonymous RAM files plus child RLIMIT_FSIZE bound even unexpected output.
    with tempfile.TemporaryFile(dir="/dev/shm") as out:
        with tempfile.TemporaryFile(dir="/dev/shm") as err:
            result = subprocess.run(
                ["/usr/bin/systemctl", "--user", *arguments],
                stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                timeout=min(2, remaining), check=False, preexec_fn=command_limits)
            out.seek(0)
            err.seek(0)
            stdout, stderr = out.read(8193), err.read(8193)
    if len(stdout) > 8192 or len(stderr) > 8192:
        raise RuntimeError("systemctl output exceeded bound")
    return result.returncode, stdout.decode("utf-8", "strict"), stderr.decode("utf-8", "replace")


def cancel_launch_group(process, stream):
    # returncode None means this direct child has not been reaped. Its PID
    # cannot be reused while signals target its fresh session/process group.
    if process.returncode is not None:
        return {"reaped_outer_exit": process.returncode, "group_signal": "NOT_SENT"}
    errors = []
    for action in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(process.pid, action)
        except ProcessLookupError:
            pass
        except OSError as error:
            errors.append(type(error).__name__ + ": " + str(error)[:512])
        if action == signal.SIGTERM:
            time.sleep(0.2)
    try:
        code = process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        code = None
        errors.append("outer wait exceeded 5 seconds")
    result = {"owned_process_group": process.pid, "outer_exit": code,
              "group_signals": ["TERM", "KILL"], "errors": errors}
    best_effort_record(stream, {"launch_cancellation": result})
    return result


def owned_scope():
    try:
        raw = read_small(JOB / "scope.jsonl", 4096)
    except FileNotFoundError:
        return None
    rows = raw.splitlines()
    if len(rows) != 1:
        raise RuntimeError("not exactly one complete owned scope receipt")
    item = json.loads(rows[0])
    unit = item.get("unit")
    if not isinstance(unit, str) or re.fullmatch(UNIT_PATTERN, unit) is None:
        raise RuntimeError("invalid owned scope receipt")
    return unit


def scope_observation(unit, deadline):
    code, stdout, stderr = systemctl(
        ["show", unit, "-p", "LoadState", "-p", "ActiveState", "-p", "ControlGroup"], deadline)
    values = dict(line.split("=", 1) for line in stdout.splitlines() if "=" in line)
    populated = None
    group = values.get("ControlGroup")
    if group:
        path = Path("/sys/fs/cgroup") / group.lstrip("/")
        if ".." in path.parts or path.name != unit:
            raise RuntimeError("unexpected owned scope cgroup path")
        try:
            populated = "populated 1" in read_small(path / "cgroup.events", 4096).decode("ascii")
        except FileNotFoundError:
            populated = False
    terminal = (code == 0 and values.get("ActiveState") in ("inactive", "failed")
                and (not group or populated is False))
    return {"systemctl_exit": code, "unit": unit, "values": values,
            "populated": populated, "terminal": terminal, "stderr": stderr[:1024]}


def stop_scope(unit, stream):
    deadline = time.monotonic() + 20
    last = {"unit": unit, "terminal": False}
    for attempt in range(20):
        try:
            code, _, error = systemctl(["stop", "--no-block", unit], deadline)
            best_effort_record(stream, {"stop_attempt": attempt, "unit": unit,
                                       "stop_exit": code, "stderr": error[:1024]})
            last = scope_observation(unit, deadline)
            best_effort_record(stream, {"scope_readback": last})
            if last["terminal"]:
                return last
            if last["values"].get("ActiveState") not in ("inactive", "failed"):
                systemctl(["kill", "--signal=KILL", "--kill-whom=all", unit], deadline)
        except BaseException as error:
            last = {"unit": unit, "terminal": False, "error": str(error)[:1024]}
            best_effort_record(stream, {"scope_cleanup_error": last})
        if time.monotonic() >= deadline:
            break
        time.sleep(min(0.2, max(0, deadline - time.monotonic())))
    return last


def cleanup_owned(process, stream):
    # Cancel the complete launcher group BEFORE reading its receipt. A valid
    # heavy-wrapper receipt is closed before systemd-run is launched. Killing
    # the launch group prevents a writer/launcher from starting later; a scope
    # unit itself only contains processes and cannot spawn a future worker.
    try:
        cancelled = cancel_launch_group(process, stream)
    except BaseException as error:
        cancelled = {"outer_exit": None, "errors": [str(error)[:1024]]}
    quiescent = (cancelled.get("outer_exit") is not None and
                 not cancelled.get("errors", []))
    try:
        unit = owned_scope()
        if unit is None:
            result = {"scope": "NO_RECEIPT", "terminal": False,
                      "launch_cancellation": cancelled}
        else:
            result = stop_scope(unit, stream)
            result["scope_terminal_observed"] = result["terminal"]
            result["launcher_quiescence_confirmed"] = quiescent
            result["terminal"] = result["terminal"] and quiescent
            result["launch_cancellation"] = cancelled
    except BaseException as error:
        result = {"terminal": False, "error": str(error)[:1024],
                  "launch_cancellation": cancelled}
    best_effort_record(stream, {"cleanup": result})
    return result


def preflight():
    if os.path.lexists(JOB) or os.path.lexists(INNER / "ram-qualification-ipc-sigkill-v4"):
        raise RuntimeError("fresh exact output paths required")
    fs = os.statvfs(ROOT)
    if fs.f_bavail * fs.f_frsize < RESERVE + 60_000_000:
        raise RuntimeError("startup reserve plus margin unavailable")
    if os.environ.get("PYTHONOPTIMIZE") != "0" or sys.flags.optimize != 0:
        raise RuntimeError("Python assertions must be enabled")
    return [sys.executable, str(ROOT / "scripts/phase1_heavy.py"),
            "--out", str(JOB), "--timeout", "240s", "--swap-max", "0", "--",
            sys.executable, str(INNER / "ram_qualification_v4.py"), "ipc-sigkill"]


def wrapper_terminal(stream):
    unit = owned_scope()
    if unit is None:
        raise RuntimeError("outer exited without exact owned scope receipt")
    rows = read_small(JOB / "terminal-scope.jsonl", 16384).splitlines()
    if len(rows) != 1:
        raise RuntimeError("one fresh terminal scope receipt required")
    item = json.loads(rows[0])
    state = item.get("scope_state", {})
    if item.get("populated") is not False or state.get("ActiveState") not in ("inactive", "failed"):
        raise RuntimeError("wrapper terminal receipt is not unpopulated/inactive")
    observed = scope_observation(unit, time.monotonic() + 5)
    record(stream, {"normal_terminal_readback": observed})
    if observed["terminal"] is not True:
        raise RuntimeError("fresh owned scope is not terminal")


def monitor(process, stream):
    deadline = time.monotonic() + 270
    for sample in range(270):
        fs = os.statvfs(ROOT)
        free, size = fs.f_bavail * fs.f_frsize, metadata_bytes()
        code = process.poll()
        record(stream, {"sample": sample, "free_bytes": free,
                        "outer_metadata_bytes": size, "outer_exit": code})
        if code is not None:
            wrapper_terminal(stream)
            return code, None
        try:
            admitted = json.loads(read_small(JOB / "admitted.json", 4096))
        except FileNotFoundError:
            admitted = None
        if admitted == {"admitted": False}:
            return 125, "first memory admission refusal; retry prohibited"
        if free < RESERVE + 30_000_000 or size > 4 * 1024**2:
            return 125, "capacity stop margin or outer metadata budget"
        if time.monotonic() >= deadline:
            break
        time.sleep(min(1, max(0, deadline - time.monotonic())))
    return 125, "270 second/sample monitor bound"


def run(stream):
    argv = preflight()
    process, normal, code = None, False, 125
    reason = "launch or monitor did not finish"
    try:
        process = subprocess.Popen(argv, start_new_session=True)
        record(stream, {"argv": argv, "pid": process.pid,
                        "python_optimize": sys.flags.optimize,
                        "nominal_poll_seconds": 1, "sampling_is_not_a_quota": True})
        code, reason = monitor(process, stream)
        normal = reason is None
    except BaseException as error:
        reason = "monitor error: " + type(error).__name__
        best_effort_record(stream, {"error": str(error)[:2048]})
    finally:
        if process is not None and not normal:
            try:
                cleanup_owned(process, stream)
            except BaseException as error:
                best_effort_record(stream, {"cleanup": "UNVERIFIED", "error": str(error)[:2048]})
        best_effort_record(stream, {"outer_exit": code if normal else None,
                                   "normal_wrapper_exit": normal, "reason": reason,
                                   "acceptance_credit": False})
    return code if normal else 125


if __name__ == "__main__":
    os.environ.setdefault("XDG_RUNTIME_DIR", "/run/user/" + str(os.getuid()))
    os.environ.setdefault("DBUS_SESSION_BUS_ADDRESS", "unix:path=" + os.environ["XDG_RUNTIME_DIR"] + "/bus")
    with LOG.open("x", encoding="ascii") as receipt:
        raise SystemExit(run(receipt))
