"""One retained, bounded capacity monitor for the exact Chunk diagnostic."""
from pathlib import Path
import datetime
import json
import os
import re
import signal
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
JOB = HERE / "chunk-proof-job-v1"
INNER = ROOT / "records/phase1-direct/completion-20261026"
LOG = HERE / "chunk-capacity-guard-v1.jsonl"
RESERVE = 10_000_000_000


def record(stream, event):
    event["utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    data = json.dumps(event, sort_keys=True) + "\n"
    if len(data) > 16384 or stream.tell() + len(data) > 512 * 1024:
        raise RuntimeError("monitor receipt budget exceeded")
    if stream.write(data) != len(data):
        raise RuntimeError("short monitor write")
    stream.flush()


def metadata_bytes():
    pending, count, total = [JOB], 0, 0
    for _ in range(2048):
        if not pending:
            return total
        parent = pending.pop()
        if not parent.exists():
            continue
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


def stop_owned(process, stream, reason):
    path = JOB / "scope.jsonl"
    if path.exists():
        if path.stat().st_size > 4096:
            raise RuntimeError("scope receipt exceeds bound")
        rows = path.read_text().splitlines()
        if len(rows) != 1:
            raise RuntimeError("not exactly one owned scope")
        unit = json.loads(rows[0])["unit"]
        if re.fullmatch(r"wl-phase1-[0-9a-f]{32}\.scope", unit) is None:
            raise RuntimeError("invalid owned scope")
        result = subprocess.run(
            ["systemctl", "--user", "stop", "--no-block", unit],
            capture_output=True, text=True, timeout=5, check=False)
        record(stream, {"stop_reason": reason, "unit": unit,
                        "stop_returncode": result.returncode,
                        "stderr": result.stderr[:1024]})
        if result.returncode != 0:
            raise RuntimeError("owned scope stop failed; require readback")
    else:
        # This fresh process group contains only our wrapper and its lock waiter.
        os.killpg(process.pid, signal.SIGTERM)
        record(stream, {"stop_reason": reason, "owned_process_group": process.pid})


def run(stream):
    if JOB.exists() or (INNER / "ram-qualification-chunk-v2").exists():
        raise RuntimeError("fresh output paths required")
    fs = os.statvfs(ROOT)
    if fs.f_bavail * fs.f_frsize < RESERVE + 60_000_000:
        raise RuntimeError("startup reserve plus margin unavailable")
    if os.environ.get("PYTHONOPTIMIZE") != "0" or sys.flags.optimize != 0:
        raise RuntimeError("Python assertions must be enabled")
    argv = [sys.executable, str(ROOT / "scripts/phase1_heavy.py"),
            "--out", str(JOB), "--timeout", "240s", "--swap-max", "0", "--",
            sys.executable, str(INNER / "ram_qualification_v2.py"), "chunk"]
    process = subprocess.Popen(argv, start_new_session=True)
    record(stream, {"argv": argv, "pid": process.pid,
                    "python_optimize": sys.flags.optimize, "poll_seconds": 1})
    reason = None
    try:
        for sample in range(270):
            fs = os.statvfs(ROOT)
            free, size = fs.f_bavail * fs.f_frsize, metadata_bytes()
            code = process.poll()
            record(stream, {"sample": sample, "free_bytes": free,
                            "outer_metadata_bytes": size, "outer_exit": code})
            if code is not None:
                return code
            marker = JOB / "admitted.json"
            if marker.exists() and json.loads(marker.read_text()) == {"admitted": False}:
                reason = "first memory admission refusal; retry prohibited"
            if free < RESERVE + 30_000_000 or size > 4 * 1024**2:
                reason = "capacity stop margin or outer metadata budget"
            if reason is not None:
                break
            time.sleep(1)
        reason = reason or "270 sample monitor bound; require terminal readback"
    except BaseException as error:
        reason = "monitor error: " + type(error).__name__
        record(stream, {"error": str(error)[:2048]})
    stop_owned(process, stream, reason)
    try:
        code = process.wait(timeout=15)
    except subprocess.TimeoutExpired:
        record(stream, {"outer_exit": None, "terminal": "UNVERIFIED", "reason": reason})
        return 125
    record(stream, {"outer_exit": code, "reason": reason, "stopped": True})
    return 125


if __name__ == "__main__":
    os.environ.setdefault("XDG_RUNTIME_DIR", "/run/user/" + str(os.getuid()))
    os.environ.setdefault("DBUS_SESSION_BUS_ADDRESS", "unix:path=" + os.environ["XDG_RUNTIME_DIR"] + "/bus")
    with LOG.open("x", encoding="ascii") as receipt:
        raise SystemExit(run(receipt))
