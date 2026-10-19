from pathlib import Path
import json
import re
import shutil
import subprocess

out = Path(__file__).resolve().parent
base = ["gnatprove", "-P", "core/worldline_core_sources.gpr", "-u",
        "worldline-custody_v2_load_input.adb", "--no-inlining", "--mode=all",
        "--level=3", "--report=all", "--checks-as-errors=on", "--proof-warnings=on",
        "--warnings=error", "--memlimit=1024", "--timeout=5", "-j2",
        "--subdirs=direct-proof-custody-next-line", "-XWORLDLINE_BUILD=checks",
        "-XSPARKLIB_MODE=full", "-XSPARKLIB_BUILD=Production",
        "-XSPARKLIB_LIBRARY_TYPE=static", "-XSPARKLIB_INSTALLED=True"]
results = []
for name, location in [('extra', 'worldline-custody_v2_load_input.adb:181'), ('event-extras', 'worldline-custody_v2_load_input.adb:174'), ('initialize', 'worldline-custody_v2_load_input.adb:455'), ('decode-into', 'worldline-custody_v2_load_input.adb:499')]:
    argv = base + ["--limit-subp=" + location]
    result = subprocess.run(argv, capture_output=True, text=True)
    (out / (name + ".stdout")).write_text(result.stdout)
    (out / (name + ".stderr")).write_text(result.stderr)
    report = re.search(r"Summary logged in (.+)", result.stdout)
    if report:
        shutil.copyfile(report.group(1).strip(), out / (name + ".gnatprove.out"))
    results.append({"name": name, "argv": argv, "exit_code": result.returncode,
                    "fresh_summary": bool(report)})
    (out / "result.json").write_text(json.dumps(results, indent=2) + "\n")
    print(name, result.returncode, flush=True)
raise SystemExit(0 if all(r["exit_code"] == 0 and r["fresh_summary"] for r in results) else 1)
