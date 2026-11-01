"""Bounded author test driver only; never calls an operational main."""
from pathlib import Path
import hashlib
import json
import os
import resource
import subprocess
import time

HERE = Path(__file__).resolve().parent
NAMES = ("xgen_common.py", "xgen_guard.py", "xgen_worker.py", "xgen_recovery.py",
         "source_tests.py", "run_author_tests.py")


def identity(path):
    raw = path.read_bytes()
    if len(raw) > 2 * 1024**2:
        raise RuntimeError("test artifact limit")
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def limits():
    resource.setrlimit(resource.RLIMIT_FSIZE, (1024**2, 1024**2))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def main():
    result = {"author_only": True, "operational_mains_run": False,
              "sources_before": {n: identity(HERE / n) for n in NAMES}, "attempts": []}
    started = time.monotonic()
    for label, readonly in (("test-final2-full", False), ("test-final2-readonly", True)):
        env = {"PATH": "/usr/bin", "LC_ALL": "C", "PYTHONOPTIMIZE": "0",
               "PYTHONDONTWRITEBYTECODE": "1"}
        if readonly:
            env["XGEN_READ_ONLY_TESTS"] = "1"
        argv = ["/usr/bin/python3", "-B", "-W", "error", str(HERE / "source_tests.py")]
        begin = time.monotonic()
        with (HERE / (label + ".stdout")).open("xb") as out:
            with (HERE / (label + ".stderr")).open("xb") as err:
                completed = subprocess.run(argv, cwd=HERE, env=env, stdin=subprocess.DEVNULL,
                    stdout=out, stderr=err, timeout=30, check=False, preexec_fn=limits)
        result["attempts"].append({"command": argv, "environment": env,
            "timeout_seconds": 30, "exit": completed.returncode,
            "elapsed_seconds": time.monotonic()-begin,
            "stdout": identity(HERE / (label + ".stdout")),
            "stderr": identity(HERE / (label + ".stderr"))})
    result["elapsed_seconds"] = time.monotonic()-started
    result["sources_after"] = {n: identity(HERE / n) for n in NAMES}
    result["sources_unchanged"] = result["sources_before"] == result["sources_after"]
    with (HERE / "test-final2-results.json").open("x") as stream:
        json.dump(result, stream, sort_keys=True, indent=2)
        stream.write("\n")
    return 0 if result["sources_unchanged"] and all(x["exit"] == 0 for x in result["attempts"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
