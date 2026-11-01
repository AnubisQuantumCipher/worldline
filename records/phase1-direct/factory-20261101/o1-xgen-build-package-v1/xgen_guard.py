"""Source derivative for the future UNADMITTED fixed disk xtree build.

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

from xgen_common import (WORK, LIVE_ROOT, FILE, ARCHIVE, TOTAL, inventory,
                         verify_packet, verify_pins, load_json, reject_pairs, reject_number)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
JOB = HERE.parent / "o1-xgen-build-job-v1"
INNER = ROOT / "records/phase1-direct/completion-20261026"
LOG = WORK / "control/guard.jsonl"
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


def class_bytes(path, byte_limit, file_limit, entries=8192):
    if not os.path.lexists(path):
        return 0
    return inventory(path, byte_limit, file_limit, entries)[1]


def metadata_bytes():
    total = class_bytes(JOB, 8 * 1024**2, 8 * 1024**2)
    total += class_bytes(WORK / "control", 8 * 1024**2, 8 * 1024**2)
    if total > 8 * 1024**2:
        raise RuntimeError("combined outer metadata limit")
    return total


def capacity_classes():
    live = class_bytes(LIVE_ROOT, 4 * 1024**3, FILE)
    archive = class_bytes(WORK / "archive", ARCHIVE, ARCHIVE, 1)
    restore = class_bytes(WORK / "restore", 4 * 1024**3, FILE)
    if WORK.is_symlink() or not WORK.is_dir():
        raise RuntimeError("invalid owned work root")
    with os.scandir(WORK) as rows:
        for count, row in enumerate(rows):
            if count >= 4 or row.name not in ("live", "archive", "restore", "control"):
                raise RuntimeError("unregistered work budget class")
    return {"live": live, "archive": archive, "restore": restore,
            "outer_metadata": metadata_bytes()}


def command_limits():
    resource.setrlimit(resource.RLIMIT_FSIZE, (8192, 8192))


def systemctl(arguments, deadline):
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError("cleanup deadline")
    # Anonymous RAM files plus child RLIMIT_FSIZE bound even unexpected output.
    with tempfile.TemporaryFile(dir=WORK / "control") as out:
        with tempfile.TemporaryFile(dir=WORK / "control") as err:
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
    item = json.loads(rows[0], object_pairs_hook=reject_pairs,
                      parse_float=reject_number, parse_constant=reject_number)
    unit = item.get("unit")
    if not isinstance(unit, str) or re.fullmatch(UNIT_PATTERN, unit) is None:
        raise RuntimeError("invalid owned scope receipt")
    return unit


def scope_observation(unit, deadline):
    code, stdout, stderr = systemctl(
        ["show", unit, "-p", "Id", "-p", "LoadState", "-p", "ActiveState", "-p", "ControlGroup"], deadline)
    values = dict(line.split("=", 1) for line in stdout.splitlines() if "=" in line)
    populated = None
    group = values.get("ControlGroup")
    if group:
        path = Path("/sys/fs/cgroup") / group.lstrip("/")
        if ".." in path.parts or path.name != unit:
            raise RuntimeError("unexpected owned scope cgroup path")
        try:
            populated = population(read_small(path / "cgroup.events", 4096))
        except FileNotFoundError:
            populated = None
    terminal = (code == 0 and values.get("Id") == unit
                and values.get("ActiveState") in ("inactive", "failed")
                and populated is False)
    collected = (code == 0 and values.get("Id") == unit
                 and values.get("LoadState") == "not-found"
                 and values.get("ActiveState") == "inactive"
                 and values.get("ControlGroup") == "")
    return {"systemctl_exit": code, "unit": unit, "values": values,
            "populated": populated, "terminal": terminal,
            "collected_scope": collected, "stderr": stderr[:1024]}


def population(raw):
    if not isinstance(raw, bytes) or len(raw) > 4096:
        return None
    try:
        rows = [line.split() for line in raw.decode("ascii", "strict").splitlines()]
    except UnicodeDecodeError:
        return None
    if not rows or any(len(row) != 2 for row in rows):
        return None
    names = [row[0] for row in rows]
    if len(set(names)) != len(names) or names.count("populated") != 1:
        return None
    value = dict(rows)["populated"]
    if value not in ("0", "1"):
        return None
    return value == "1"


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
    if os.path.lexists(JOB) or os.path.lexists(WORK):
        raise RuntimeError("fresh exact output paths required")
    verify_packet()
    verify_pins(load_json(HERE / "tool-runtime-pins.json"))
    verify_pins(load_json(HERE / "input-pins.json"))
    fs = os.statvfs(ROOT)
    if fs.f_bavail * fs.f_frsize < RESERVE + TOTAL:
        raise RuntimeError("complete overlap reserve unavailable")
    if os.environ.get("PYTHONOPTIMIZE") != "0" or sys.flags.optimize != 0:
        raise RuntimeError("Python assertions must be enabled")
    if Path(sys.executable).resolve() != Path("/usr/bin/python3").resolve():
        raise RuntimeError("unregistered Python interpreter")
    WORK.mkdir()
    (WORK / "control").mkdir()
    return [sys.executable, "-B", "-W", "error", str(ROOT / "scripts/phase1_heavy.py"),
            "--out", str(JOB), "--timeout", "1500s", "--swap-max", "0", "--",
            sys.executable, "-B", "-W", "error", str(HERE / "xgen_worker.py")]


def launch_environment():
    runtime = "/run/user/" + str(os.getuid())
    return {"PATH": "/usr/bin", "LC_ALL": "C", "TZ": "UTC",
            "HOME": str(WORK / "control"), "PYTHONOPTIMIZE": "0",
            "PYTHONDONTWRITEBYTECODE": "1", "XDG_RUNTIME_DIR": runtime,
            "DBUS_SESSION_BUS_ADDRESS": "unix:path=" + runtime + "/bus"}


def admission_value(path):
    try:
        value = load_json(path, 4096)
    except FileNotFoundError:
        return None
    if (not isinstance(value, dict) or set(value) != {"admitted"}
            or type(value["admitted"]) is not bool):
        raise RuntimeError("admission receipt schema/type")
    return value["admitted"]


def wrapper_terminal(stream, launcher_exit=None):
    if type(launcher_exit) is not int:
        raise RuntimeError("type-checked reaped launcher exit required")
    unit = owned_scope()
    if unit is None:
        raise RuntimeError("outer exited without exact owned scope receipt")
    rows = read_small(JOB / "terminal-scope.jsonl", 16384).splitlines()
    if len(rows) != 1:
        raise RuntimeError("one fresh terminal scope receipt required")
    item = json.loads(rows[0], object_pairs_hook=reject_pairs,
                      parse_float=reject_number, parse_constant=reject_number)
    state = item.get("scope_state", {})
    if (not isinstance(state, dict) or item.get("populated") is not False
            or state.get("ActiveState") not in ("inactive", "failed")):
        raise RuntimeError("wrapper terminal receipt is not unpopulated/inactive")
    group = state.get("ControlGroup")
    if not isinstance(group, str) or state.get("Id", unit) != unit:
        raise RuntimeError("terminal receipt unit/control-group binding")
    if group and (".." in Path(group).parts or Path(group).name != unit):
        raise RuntimeError("terminal receipt belongs to another cgroup")
    record(stream, {"owned_scope": unit, "complete_wrapper_terminal_receipt": item})
    observed = scope_observation(unit, time.monotonic() + 5)
    record(stream, {"normal_terminal_readback": observed, "launcher_exit": launcher_exit})
    if observed["terminal"] is not True and observed.get("collected_scope") is not True:
        raise RuntimeError("fresh owned scope is not terminal")


def monitor(process, stream):
    started = time.monotonic()
    deadline = started + 1590
    for sample in range(1590):
        fs = os.statvfs(ROOT)
        free, sizes = fs.f_bavail * fs.f_frsize, capacity_classes()
        code = process.poll()
        record(stream, {"sample": sample, "free_bytes": free,
                        "class_bytes": sizes, "outer_exit": code})
        if code is not None:
            wrapper_terminal(stream, code)
            return code, None
        if admission_value(JOB / "admitted.json") is False:
            return 125, "first memory admission refusal; retry prohibited"
        if time.monotonic() - started >= 60 and owned_scope() is None:
            return 125, "60 second admission/lock bound"
        if free < RESERVE + 1024**3:
            return 125, "reserve plus shutdown/growth margin stop"
        if time.monotonic() >= deadline:
            break
        time.sleep(min(1, max(0, deadline - time.monotonic())))
    return 125, "1590 second/sample monitor bound"


def run(stream, argv):
    process, normal, code = None, False, 125
    reason = "launch or monitor did not finish"
    try:
        process = subprocess.Popen(argv, start_new_session=True, env=launch_environment())
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
    arguments = preflight()
    with LOG.open("x", encoding="ascii") as receipt:
        raise SystemExit(run(receipt, arguments))
