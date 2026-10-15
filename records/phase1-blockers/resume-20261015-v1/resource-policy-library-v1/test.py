"""Run the complete original finite resource-policy module against the new library."""
import ast
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parent
OUT = BASE / "test-results"
BUILD = BASE / "build-results/result.json"

def stamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

build = json.loads(BUILD.read_text())
if not build.get("validation_passed") or build.get("exit_code") != 0:
    raise SystemExit("No successful complete production aggregate build")
if os.environ.get("PYTHONOPTIMIZE") not in (None, "", "0"):
    raise SystemExit("Refuse optimized-away fixture assertions")
library = Path(build["library"]["path"])
if library != ROOT / "lib/phase1-resource-policy-candidate-v1/libworldline_core.so" or library.is_symlink() or not library.is_file() or digest(library) != build["library"]["sha256"]:
    raise SystemExit("Unexpected new production library identity")
commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
if commit != build["commit"] or digest(ROOT / "core/resource_quantities.adb") != build["core_source_sha256"]:
    raise SystemExit("Build/source epoch differs")
OUT.mkdir(exist_ok=False)
for name in ("tmp", "cache"):
    (OUT / name).mkdir()
env = dict(os.environ)
env.update(WORLDLINE_CORE_LIB=str(library), PYTHONPATH=str(ROOT / "runtime"),
           PYTHONDONTWRITEBYTECODE="1", PYTHONNOUSERSITE="1", TMPDIR=str(OUT / "tmp"), XDG_CACHE_HOME=str(OUT / "cache"))
module = ROOT / "tests/test_resource_policy.py"
tree = ast.parse(module.read_text())
roster = [node.name for cls in tree.body if isinstance(cls, ast.ClassDef)
          for node in cls.body if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")]
if not roster:
    raise SystemExit("Missing original test roster")
command = [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-p", "test_resource_policy.py", "-v"]
argv = ["bwrap", "--die-with-parent", "--ro-bind", "/", "/", "--dev", "/dev", "--proc", "/proc",
        "--bind", str(OUT), str(OUT), "--bind", str(OUT / "tmp"), "/tmp", "--chdir", str(ROOT), *command]
watched = {ROOT / relative: expected for relative, expected in build["watched_after"].items()}

def identities():
    return {str(p.relative_to(ROOT)): digest(p) for p in watched}

before = identities()
if before != build["watched_after"]:
    raise SystemExit("Pinned original/private artifact changed before test")
receipt = {"started_utc": stamp(), "commit": commit, "cwd": str(ROOT), "argv": argv,
           "module_sha256": digest(module), "roster": roster, "library": build["library"],
           "build_result_sha256": digest(BUILD), "method_sha256": digest(Path(__file__)),
           "python_path": sys.executable, "python_sha256": digest(Path(sys.executable).resolve()), "python_version": sys.version,
           "watched_before": before, "environment": {key: env.get(key) for key in ("PATH", "LANG", "LD_LIBRARY_PATH", "WORLDLINE_CORE_LIB", "PYTHONPATH", "PYTHONOPTIMIZE", "PYTHONNOUSERSITE", "TMPDIR", "XDG_CACHE_HOME")},
           "scope": "Complete unchanged original finite resource-policy module, real explicit newly built production library; not protected/full runtime/full-domain acceptance"}
(OUT / "launch.json").write_text(json.dumps(receipt, indent=2) + "\n")
with (OUT / "stdout").open("xb") as stdout, (OUT / "stderr").open("xb") as stderr:
    result = subprocess.run(argv, cwd=ROOT, env=env, stdout=stdout, stderr=stderr)
stderr = (OUT / "stderr").read_text()
count = re.search(r"^Ran (\d+) tests? in .+$", stderr, re.MULTILINE)
reported = int(count.group(1)) if count else None
receipt.update(ended_utc=stamp(), exit_code=result.returncode, reported_tests=reported,
               final_ok=bool(re.search(r"^OK$", stderr, re.MULTILINE)),
               skipped_reported=bool(re.search(r"\bskipped\b", stderr)),
               library_sha256_after=digest(library), module_sha256_after=digest(module),
               watched_after=identities(), stdout_sha256=digest(OUT / "stdout"), stderr_sha256=digest(OUT / "stderr"))
receipt["validation_passed"] = (result.returncode == 0 and reported == len(roster) and receipt["final_ok"]
    and not receipt["skipped_reported"] and receipt["library_sha256_after"] == build["library"]["sha256"]
    and receipt["module_sha256_after"] == receipt["module_sha256"] and receipt["watched_after"] == before)
(OUT / "result.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps({"result": str(OUT / "result.json"), "exit_code": result.returncode, "reported_tests": reported, "validation_passed": receipt["validation_passed"]}))
raise SystemExit(0 if receipt["validation_passed"] else result.returncode or 125)
