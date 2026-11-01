#!/usr/bin/python3
"""Bounded synthetic composition only. No operational guard/entry is executed."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

BASE = Path(__file__).resolve().parent
SOURCE = BASE / "launch.sh"
SOURCES = ("launch.sh", "entry.sh", "fault.c", "tee-fixture.sh", "run_tests.py")
FIXED_ROOT = "/home/sicarii/Work/worldline-phase1-direct-20261019/records/phase1-direct/factory-20261101/o1-xgen-root-control-v2"
BEGIN = "    # BEGIN FIXED GUARD -- tests replace this body, never execute it.\n"
END = "    # END FIXED GUARD"
ENV = {"PATH": "/usr/bin", "LC_ALL": "C", "TZ": "UTC"}
START = time.monotonic()
RESULTS = []


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def execute(command, env=ENV, deadline=7):
    if time.monotonic() - START > 100:
        raise RuntimeError("aggregate test guard: 100s reached")
    begin = time.monotonic()
    run = subprocess.run(command, env=env, capture_output=True, timeout=deadline,
                         check=False, cwd=BASE)
    if len(run.stdout) + len(run.stderr) > 65536:
        raise RuntimeError("unexpected fixture diagnostic growth")
    return {"argv": command, "environment": env, "returncode": run.returncode,
            "stdout": run.stdout.decode("utf-8", "backslashreplace"),
            "stderr": run.stderr.decode("utf-8", "backslashreplace"),
            "seconds": time.monotonic() - begin}


def variant(folder, body):
    source = SOURCE.read_text()
    old_body = source.split(BEGIN)[1].split(END)[0]
    changes = [(FIXED_ROOT, str(folder)), ("IO_DEADLINE=1650s", "IO_DEADLINE=0.4s"),
               ("KILL_GRACE=5s", "KILL_GRACE=0.1s"), (old_body, body + "\n"),
               ("/usr/bin/tee --output-error=exit",
                f"/usr/bin/bash {BASE}/tee-fixture.sh --output-error=exit")]
    for old, new in changes:
        assert source.count(old) in (1, 2), (old, source.count(old))
        source = source.replace(old, new)
    path = folder / "fixture.sh"
    path.write_text(source)
    return path, [{"old": old, "new": new} for old, new in changes]


def files(folder):
    result = {}
    for name in ("stdout", "stderr", "stdout-consumer.stderr", "stderr-consumer.stderr", "status"):
        path = folder / name
        if path.is_symlink():
            result[name] = {"symlink": os.readlink(path)}
        elif path.is_file():
            result[name] = {"bytes": path.stat().st_size, "sha256": digest(path)}
            if path.stat().st_size <= 4096:
                result[name]["text"] = path.read_text(errors="backslashreplace")
        elif path.exists():
            result[name] = {"type": "nonregular"}
        else:
            result[name] = {"absent": True}
    return result


def one_case(index, name, body, expected, fault=None, setup=None):
    folder = BASE / f"case-{index:02d}-{name}"
    folder.mkdir(mode=0o700)
    script, replacements = variant(folder, body)
    if setup == "existing":
        (folder / "stdout").write_text("do not replace")
    elif setup == "special":
        os.mkfifo(folder / "stdout", 0o600)
    elif setup == "symlink":
        (folder / "stdout").symlink_to("/dev/full")
    elif setup == "status_exists":
        (folder / "status").write_text("existing status")
    elif setup == "bad_mode":
        folder.chmod(0o755)
    env = dict(ENV)
    if fault:
        env.update(FIXTURE_FAULT_TARGET=fault[0], FIXTURE_FAULT_MODE=fault[1])
    run = execute(["/usr/bin/bash", "--noprofile", "--norc", str(script)], env)
    record = {"case": name, "fixture_sha256": digest(script), "replacements": replacements,
              "command": run, "files": files(folder), "expected_zero": expected}
    record["passed"] = (run["returncode"] == 0) == expected
    RESULTS.append(record)
    print(f'{name}: {"PASS" if record["passed"] else "FAIL"} rc={run["returncode"]}', flush=True)


def check_semantics():
    by_name = {row["case"]: row for row in RESULTS}
    for name in ("first-eio", "first-enospc", "lost-diag"):
        assert by_name[name]["files"]["stdout"]["bytes"] == 0
        assert "stdout_consumer=WAIT_STATUS:1" in by_name[name]["files"]["status"]["text"]
    assert by_name["partial"]["files"]["stdout"]["bytes"] == 1
    for name in ("cap", "cap-exact"):
        assert by_name[name]["files"]["stdout"]["bytes"] == 8388608
    for row in RESULTS:
        if row["case"] not in ("status-exists", "bad-mode"):
            assert "guard=" in row["files"]["status"].get("text", "") or row["case"].startswith("receipt-")
    for name in ("first-eio", "first-enospc", "partial", "close-empty", "lost-diag"):
        assert "guard=WAIT_STATUS:0" in by_name[name]["files"]["status"]["text"]
    assert by_name["lost-diag"]["files"]["stdout-consumer.stderr"]["bytes"] == 0
    assert "stderr_consumer=WAIT_STATUS:0" in by_name["consumer-death"]["files"]["status"]["text"]
    assert "stdout_consumer=WAIT_STATUS:124" in by_name["delayed-eof"]["files"]["status"]["text"]


def cases():
    return [
        ("empty", "    :", True, None, None),
        ("output", "    printf 'output'", False, None, None),
        ("stderr", "    printf 'error' >&2", False, None, None),
        ("guard-nonzero", "    exit 7", False, None, None),
        ("guard-signal", "    /usr/bin/kill -TERM \"$BASHPID\"", False, None, None),
        ("first-eio", "    printf 'ignored-output' || :", False, ("stdout", "first_eio"), None),
        ("first-enospc", "    printf 'ignored-output' || :", False, ("stdout", "first_enospc"), None),
        ("partial", "    printf 'abcdef' || :", False, ("stdout", "partial"), None),
        ("close-empty", "    :", False, ("stdout", "close"), None),
        ("close-stderr", "    :", False, ("stderr", "close"), None),
        ("lost-diag", "    printf 'lost' || :", False, ("stdout", "lost_diag"), None),
        ("cap", "    /usr/bin/head -c 8388609 /dev/zero || :", False, None, None),
        ("cap-exact", "    /usr/bin/head -c 8388608 /dev/zero || :", False, None, None),
        ("consumer-death", "    /usr/bin/kill -KILL \"$P_OUT_PID\"; :", False, None, None),
        ("delayed-eof", "    /usr/bin/sleep 0.7 &\n    :", False, None, None),
        ("receipt-first", "    :", False, ("status", "first_eio"), None),
        ("receipt-partial", "    :", False, ("status", "partial"), None),
        ("receipt-close", "    :", False, ("status", "close"), None),
        ("existing", "    printf 'must-not-launch'", False, None, "existing"),
        ("special", "    printf 'must-not-launch'", False, None, "special"),
        ("symlink", "    printf 'must-not-launch'", False, None, "symlink"),
        ("status-exists", "    printf 'must-not-launch'", False, None, "status_exists"),
        ("bad-mode", "    printf 'must-not-launch'", False, None, "bad_mode"),
        ("guard-fds", "    [[ $(ulimit -H -f) == unlimited && $(ulimit -S -f) == 8192 ]] || exit 17\n    for fd in \"$P_OUT\" \"$P_ERR\" \"$OUT_F\" \"$ERR_F\" \"$OUT_DIAG_F\" \"$ERR_DIAG_F\" \"$STATUS_F\"; do\n        [[ ! -e /proc/$BASHPID/fd/$fd ]] || exit 18\n    done", True, None, None),
    ]


def main():
    before = {name: digest(BASE / name) for name in SOURCES}
    write_json(BASE / "test-source-at-execution.json", before)
    commands = []
    commands.append(execute(["/usr/bin/gcc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                             "-Wpedantic", "-Wconversion", "-Wshadow", "-Wformat=2", "-O2",
                             "-fPIC", "-shared", "-o", str(BASE / "fault.so"),
                             str(BASE / "fault.c"), "-ldl"]))
    write_json(BASE / "compile-command.json", commands)
    assert commands[-1]["returncode"] == 0
    syntax = execute(["/usr/bin/bash", "-n", str(SOURCE)])
    write_json(BASE / "syntax-command.json", syntax)
    assert syntax["returncode"] == 0
    error = None
    try:
        for index, args in enumerate(cases()):
            one_case(index, *args)
        check_semantics()
        assert all(row["passed"] for row in RESULTS)
        assert before == {name: digest(BASE / name) for name in SOURCES}
    except Exception as problem:
        error = repr(problem)
        raise
    finally:
        write_json(BASE / "test-results.json", {"results": RESULTS, "error": error,
                   "seconds": time.monotonic() - START, "source_pins": before,
                   "synthetic_only": True, "operational_guard": "UNRUN"})


if __name__ == "__main__":
    main()
