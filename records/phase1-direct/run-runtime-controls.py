"""Run original direct-lane runtime controls with exact library custody."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

root = Path(__file__).resolve().parents[2]
out = root / "records/phase1-direct/runtime-controls"
out.mkdir(exist_ok=False)
lib = root / "lib/libworldline_core.so"
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

env = dict(os.environ)
env["PYTHONPATH"] = str(root / "runtime") + ":" + str(root / "tests")
env["WORLDLINE_CORE_LIB"] = str(lib)
env["PYTHONDONTWRITEBYTECODE"] = "1"
steps = [
    ("ada-tests", [str(root / "bin/worldline_core_tests")]),
    ("ada-fuzz", [str(root / "bin/worldline_core_fuzz")]),
    ("native-evaluation-controls", [sys.executable, "-B", "-m", "unittest", "-v",
     "test_evaluation_acquisition_raw_producer", "test_finalization_agent_binding",
     "test_finalization_agent_binding_additional", "test_manager_resource_lifecycle_native"]),
]
record = {"claim": "TESTED selected original controls only; not complete runtime acceptance",
          "library": str(lib), "library_before": digest(lib), "steps": []}
failed = False
for name, argv in steps:
    row = {"name": name, "argv": argv, "cwd": str(root),
           "started": datetime.now(timezone.utc).isoformat()}
    with (out / (name + ".stdout")).open("xb") as stdout, (out / (name + ".stderr")).open("xb") as stderr:
        try:
            result = subprocess.run(argv, cwd=root, env=env, stdout=stdout, stderr=stderr, timeout=180)
            row["exit_code"] = result.returncode
        except subprocess.TimeoutExpired:
            row["exit_code"] = None
            row["timed_out"] = True
    row["finished"] = datetime.now(timezone.utc).isoformat()
    row["artifacts"] = {suffix: digest(out / (name + "." + suffix)) for suffix in ("stdout", "stderr")}
    failed = failed or row["exit_code"] != 0
    record["steps"].append(row)
    (out / "result.json").write_text(json.dumps(record, indent=2) + "\n")
record["library_after"] = digest(lib)
record["library_unchanged"] = record["library_before"] == record["library_after"]
record["environment"] = {k: env[k] for k in ("PYTHONPATH", "WORLDLINE_CORE_LIB", "PYTHONDONTWRITEBYTECODE")}
record["success"] = not failed and record["library_unchanged"]
(out / "result.json").write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps(record))
sys.exit(0 if record["success"] else 1)
