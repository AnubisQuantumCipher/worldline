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
OUT = Path(__file__).resolve().parent / "projection-proof-v3"
SOURCE = ROOT / "core/worldline-custody_v2_load_input.adb"
EXPECTED = "fbf8962f74eb923bd67e9fb94f9e2cd17309ccf83cb1d61ed0822937d0f1f9e4"
TARGETS = (('project_events', 499), ('project_roots', 523), ('project_subjects', 553), ('project_alternatives', 576), ('digest', 479))
BASE = ["gnatprove", "-P", "core/worldline_core_sources.gpr", "-u",
        "worldline-custody_v2_load_input.adb", "--no-inlining", "--mode=all",
        "--level=3", "--report=all", "--checks-as-errors=on",
        "--proof-warnings=on", "--warnings=error", "--memlimit=1024",
        "--timeout=5", "-j2", "--subdirs=completion-20261026-projection-v1",
        "-XWORLDLINE_BUILD=checks", "-XSPARKLIB_MODE=full",
        "-XSPARKLIB_BUILD=Production", "-XSPARKLIB_LIBRARY_TYPE=static",
        "-XSPARKLIB_INSTALLED=True"]


def stamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def run_one(name, line):
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED:
        raise RuntimeError("source identity changed")
    argv = BASE + [f"--limit-subp=worldline-custody_v2_load_input.adb:{line}"]
    item = {"name": name, "argv": argv, "cwd": str(ROOT), "start": stamp(),
            "status": "STARTED", "source_sha256": EXPECTED}
    result_path = OUT / (name + ".json")
    result_path.write_text(json.dumps(item, indent=2) + "\n")
    stdout_path, stderr_path = OUT / (name + ".stdout"), OUT / (name + ".stderr")
    timed_out = False
    with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
        try:
            result = subprocess.run(argv, cwd=ROOT, stdout=stdout, stderr=stderr,
                                    timeout=120, check=False)
            code = result.returncode
        except subprocess.TimeoutExpired:
            timed_out, code = True, None
    match = re.search(r"Summary logged in (.+)", stdout_path.read_text())
    if match:
        report = Path(match.group(1).strip())
        if not report.is_absolute():
            report = ROOT / report
        shutil.copyfile(report, OUT / (name + ".gnatprove.out"))
    unchanged = hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED
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
    outcomes = [run_one(name, line) for name, line in TARGETS]
    return 0 if all(outcomes) else 1


if __name__ == "__main__":
    sys.exit(main())
