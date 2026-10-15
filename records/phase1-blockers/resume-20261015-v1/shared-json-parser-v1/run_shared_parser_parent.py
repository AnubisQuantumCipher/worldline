"""UNEXECUTED parent proposal: reviewed shared heavy wrapper, bounded candidate.

Copy beside run_shared_parser.py and the unchanged controls bundle. Run with -B.
This file does not release pins, archive evidence or modify storage policy.
"""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time
import traceback

sys.dont_write_bytecode = True
import run_shared_parser as driver

ROOT = driver.ROOT
MINIMUM_RESERVE = 10000000000
EARLY_STOP = 20000000000


def tracked_sources():
    names = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).split(b"\0")
    result = {}
    for raw in names:
        if not raw:
            continue
        name = os.fsdecode(raw)
        path = ROOT / name
        if path.is_symlink():
            result[name] = {"type": "symlink", "target": os.readlink(path)}
        elif path.is_file():
            result[name] = {"type": "file", "sha256": driver.digest(path)}
        elif path.exists():
            result[name] = {"type": "other"}
        else:
            result[name] = {"type": "missing"}
    return result


def last_json(path):
    if not path.is_file():
        return None
    last = None
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                last = json.loads(line)
    return last


def main():
    candidate = Path(__file__).resolve().parent
    if candidate != driver.DESTINATION:
        raise SystemExit("Execute only the reviewed fresh records copy")
    driver.no_symlink(candidate)
    out, scope = candidate / "parent", candidate / "scope"
    for name in driver.OUTPUT_NAMES:
        path = candidate / name
        driver.no_symlink(path)
        if path.exists():
            raise SystemExit("Refuse stale candidate/parent/carrier output: " + str(path))
    out.mkdir()
    receipt = {"started_utc": driver.stamp(), "source_epoch": driver.EPOCH,
               "scope": "Complete shared-parser candidate only; not full WORLDLINE or acceptance",
               "errors": [], "minimum_reserve_bytes": MINIMUM_RESERVE, "early_stop_bytes": EARLY_STOP,
               "timeout": "45m", "MemoryMax": "8G", "MemorySwapMax": "0",
               "lock": "/home/sicarii/.worldline-heavy.lock"}
    driver.write_json(out / "started.json", receipt)
    process = None
    code = None
    refused_for_disk = False

    def stop_owned(reason):
        # Scope identity is read only from the fresh carrier this parent owns.
        state = last_json(scope / "scope.jsonl")
        if state is not None:
            unit = state["unit"]
            if not re.fullmatch(r"wl-phase1-[0-9a-f]{32}\.scope", unit):
                raise RuntimeError("Unexpected own scope identity")
            with (out / "scope-stop.stdout").open("ab") as stdout, (out / "scope-stop.stderr").open("ab") as stderr:
                result = subprocess.run(["systemctl", "--user", "stop", "--no-block", unit], stdout=stdout, stderr=stderr)
            driver.event(out / "cleanup.jsonl", {"action": "stop own scope", "reason": reason,
                                                "unit": unit, "exit_code": result.returncode})
        # A queued heavy wrapper with no scope is still this parent's process
        # group. Once a scope exists, its heavy supervisor retains cleanup.
        elif process is not None and process.poll() is None:
            os.killpg(process.pid, signal.SIGTERM)
            driver.event(out / "cleanup.jsonl", {"action": "terminate own queued process group", "reason": reason,
                                                "process_group": process.pid})

    try:
        receipt["observed_head"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        if receipt["observed_head"] != driver.EPOCH:
            raise RuntimeError("Source epoch changed; require explicit new review")
        driver.verify_bundle(candidate)
        receipt["candidate_before"] = driver.candidate_identity(candidate)
        receipt["private_before"] = driver.private_identity(candidate)
        receipt["tracked_before"] = tracked_sources()
        driver.write_json(out / "source-before.json", receipt["tracked_before"])
        with (out / "source.diff").open("xb") as stream:
            stream.write(subprocess.check_output(["git", "diff", "HEAD", "--binary", "--"], cwd=ROOT))
        receipt["source_diff_sha256"] = driver.digest(out / "source.diff")
        status_script = Path("/home/sicarii/.codex/skills/project-vault/scripts/storage_status.py")
        preflight = [sys.executable, "-B", str(status_script)]
        receipt["storage_preflight"] = {"argv": preflight, "script_sha256": driver.digest(status_script)}
        with (out / "storage-preflight.stdout").open("xb") as stdout, (out / "storage-preflight.stderr").open("xb") as stderr:
            result = subprocess.run(preflight, cwd=ROOT, stdout=stdout, stderr=stderr)
        receipt["storage_preflight"].update(exit_code=result.returncode,
                                          stdout_sha256=driver.digest(out / "storage-preflight.stdout"),
                                          stderr_sha256=driver.digest(out / "storage-preflight.stderr"),
                                          observed_free_bytes=shutil.disk_usage(ROOT).free)
        if result.returncode != 0 or receipt["storage_preflight"]["observed_free_bytes"] < EARLY_STOP:
            raise RuntimeError("Storage admission refused")
        method = ROOT / "scripts/phase1_heavy.py"
        if driver.digest(method) != "c3c7fcc84bb509668d0136606449486d1179d67d7c89bf68f6f5db79a4ece61a":
            raise RuntimeError("Reviewed shared-heavy method identity changed")
        gnat_env = Path("/home/sicarii/opt/gnat/env.sh")
        command = [sys.executable, "-B", str(method), "--timeout", "45m", "--swap-max", "0",
                   "--out", str(scope), "--", "bash", "-c",
                   'set -e; source /home/sicarii/opt/gnat/env.sh; unset PYTHONOPTIMIZE; exec python3 -B "$1"',
                   "phase1-shared-json-parser", str(candidate / "run_shared_parser.py")]
        receipt.update(argv=command, cwd=str(ROOT), python_version=sys.version,
                       python_path=sys.executable, python_sha256=driver.digest(Path(sys.executable).resolve()),
                       parent_sha256=driver.digest(Path(__file__)), driver_sha256=driver.digest(candidate / "run_shared_parser.py"),
                       heavy_method_sha256=driver.digest(method), gnat_env_sha256=driver.digest(gnat_env),
                       environment={name: os.environ.get(name) for name in
                                    ("PATH", "LANG", "LC_ALL", "GPR_PROJECT_PATH", "LD_LIBRARY_PATH", "PYTHONOPTIMIZE")},
                       explicit_environment={"TMPDIR": str(scope / "tmp"), "XDG_CACHE_HOME": str(scope / "cache"),
                                             "PYTHONDONTWRITEBYTECODE": "1", "PYTHONOPTIMIZE": None})
        driver.write_json(out / "launch.json", receipt)
        with (out / "stdout").open("xb") as stdout, (out / "stderr").open("xb") as stderr:
            process = subprocess.Popen(command, cwd=ROOT, stdout=stdout, stderr=stderr, start_new_session=True)
            while True:
                code = process.poll()
                free = shutil.disk_usage(ROOT).free
                driver.event(out / "disk.jsonl", {"free_bytes": free, "minimum_reserve_bytes": MINIMUM_RESERVE,
                                                  "early_stop_bytes": EARLY_STOP, "process_exit": code})
                if code is not None:
                    break
                if free < EARLY_STOP and not refused_for_disk:
                    refused_for_disk = True
                    stop_owned("D32 early-stop threshold reached")
                time.sleep(5)
        receipt["heavy_exit"] = code
    except BaseException as error:
        receipt["errors"].append({"type": type(error).__name__, "message": str(error), "traceback": traceback.format_exc()})
        if process is not None and process.poll() is None:
            try:
                stop_owned("parent exception")
                process.wait()
            except BaseException as cleanup_error:
                receipt["errors"].append({"phase": "cleanup", "message": str(cleanup_error)})
    finally:
        for label, function in (("candidate_after", lambda: driver.candidate_identity(candidate)),
                                ("private_after", lambda: driver.private_identity(candidate)), ("tracked_after", tracked_sources)):
            try:
                receipt[label] = function()
            except BaseException as error:
                receipt[label] = None
                receipt["errors"].append({"phase": label, "type": type(error).__name__, "message": str(error)})
        receipt["candidate_unchanged"] = receipt.get("candidate_before") is not None and receipt.get("candidate_before") == receipt["candidate_after"]
        receipt["private_unchanged"] = receipt.get("private_before") is not None and receipt.get("private_before") == receipt["private_after"]
        receipt["tracked_unchanged"] = receipt.get("tracked_before") is not None and receipt.get("tracked_before") == receipt["tracked_after"]
        driver.write_json(out / "source-after.json", receipt["tracked_after"])
        receipt["terminal_scope"] = last_json(scope / "terminal-scope.jsonl")
        terminal = receipt["terminal_scope"]
        receipt["own_scope_terminal"] = (terminal is not None and terminal.get("populated") is False
                                          and terminal.get("scope_state", {}).get("ActiveState") in ("inactive", "failed"))
        result_path = candidate / "results/result.json"
        receipt["driver_result"] = ({"path": str(result_path), "sha256": driver.digest(result_path),
                                     "value": json.loads(result_path.read_text())} if result_path.is_file() else None)
        # Incomplete terminal output never becomes an empty successful phase.
        receipt["driver_terminal_present"] = receipt["driver_result"] is not None
        receipt["phase_event_log"] = ({"path": str(candidate / "results/events.jsonl"),
                                       "sha256": driver.digest(candidate / "results/events.jsonl")}
                                      if (candidate / "results/events.jsonl").is_file() else None)
        receipt["disk_early_stop"] = refused_for_disk
        receipt["retained_carrier_files"] = {name: driver.digest(scope / name)
                                             for name in ("admission.jsonl", "scope.jsonl", "cgroup.jsonl", "supervisor.jsonl",
                                                          "terminal-scope.jsonl", "scope-journal.txt", "result.jsonl", "rusage.json", "worker-result.json")
                                             if (scope / name).is_file()}
        okay = (code == 0 and not refused_for_disk and not receipt["errors"]
                and receipt["candidate_unchanged"] and receipt["private_unchanged"] and receipt["tracked_unchanged"]
                and receipt["own_scope_terminal"] and receipt["driver_terminal_present"]
                and receipt["driver_result"]["value"].get("mechanically_complete") is True)
        receipt.update(ended_utc=driver.stamp(), mechanically_complete=okay,
                       status="RECORDED; complete raw proof review required" if okay else "FAILED-OPEN candidate execution")
        driver.write_json(out / "result.json", receipt)
    print(json.dumps({"result": str(out / "result.json"), "mechanically_complete": okay}))
    return 0 if okay else 1


if __name__ == "__main__":
    raise SystemExit(main())
