"""Record bounded focused proof attempts; this never grants acceptance."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "numeric-proof-v1"
SOURCES = {"core/resource_quantities.ads": "603a4bc3e1c26a6f96807ca3243de1fbe2c7ca43a6cf27f0170a0cdcfe1c9e39",
           "core/resource_reservation_transition.adb": "c0749aa889ffb6c20645c96b4746b94fe0e1b5c4f24d2b36ded1cb0e3abbf484"}
TARGETS = (("prefix_value", "resource_quantities.adb", "resource_quantities.ads", 79),
           ("equal_prefix", "resource_reservation_transition.adb", "resource_reservation_transition.adb", 572),
           ("trimmed_view", "resource_reservation_transition.adb", "resource_reservation_transition.adb", 617),
           ("successor_columns", "resource_reservation_transition.adb", "resource_reservation_transition.adb", 670),
           ("is_successor", "resource_reservation_transition.adb", "resource_reservation_transition.adb", 713))
BASE = ["gnatprove", "-P", "core/worldline_core_sources.gpr", "--no-inlining", "--mode=all",
        "--level=3", "--report=all", "--checks-as-errors=on",
        "--proof-warnings=on", "--warnings=error", "--memlimit=1024",
        "--timeout=5", "-j2", "--subdirs=completion-20261026-projection-v1",
        "-XWORLDLINE_BUILD=checks", "-XSPARKLIB_MODE=full",
        "-XSPARKLIB_BUILD=Production", "-XSPARKLIB_LIBRARY_TYPE=static",
        "-XSPARKLIB_INSTALLED=True"]


def stamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def source_matches():
    return all(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest
               for path, digest in SOURCES.items())


def run_one(name, unit, scope, line):
    if not source_matches():
        raise RuntimeError("source identity changed")
    argv = BASE + ["-u", unit, f"--limit-subp={scope}:{line}"]
    item = {"name": name, "argv": argv, "cwd": str(ROOT), "start": stamp(),
            "status": "STARTED", "source_sha256": SOURCES}
    result_path = OUT / (name + ".json")
    result_path.write_text(json.dumps(item, indent=2) + "\n")
    stdout_path, stderr_path = OUT / (name + ".stdout"), OUT / (name + ".stderr")
    timed_out = False
    with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
        try:
            result = subprocess.run(argv, cwd=ROOT, stdout=stdout, stderr=stderr,
                                    timeout=180, check=False)
            code = result.returncode
        except subprocess.TimeoutExpired:
            timed_out, code = True, None
    match = re.search(r"Summary logged in (.+)", stdout_path.read_text())
    if match:
        report = Path(match.group(1).strip())
        if not report.is_absolute():
            report = ROOT / report
        shutil.copyfile(report, OUT / (name + ".gnatprove.out"))
    unchanged = source_matches()
    item.update(end=stamp(), exit_code=code, timed_out=timed_out,
                fresh_summary=bool(match), source_unchanged=unchanged,
                status="TERMINATED", phase_acceptance=False)
    result_path.write_text(json.dumps(item, indent=2) + "\n")
    print(name, code, "fresh_summary", bool(match), flush=True)
    if timed_out:
        raise TimeoutError("focused prover deadline; outer scope must clean up")
    return code == 0 and bool(match) and unchanged


def main():
    OUT.mkdir(exist_ok=False)
    outcomes = [run_one(*target) for target in TARGETS]
    return 0 if all(outcomes) else 1


if __name__ == "__main__":
    sys.exit(main())
