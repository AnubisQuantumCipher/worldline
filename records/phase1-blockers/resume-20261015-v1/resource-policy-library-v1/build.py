"""Build the unchanged complete aggregate into fresh suffixed output directories."""
import datetime
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parent
OUT = BASE / "build-results"
SUBDIR = "phase1-resource-policy-candidate-v1"
DIRECTORIES = [ROOT / "obj" / name / SUBDIR for name in ("core-library", "core", "attest-sha256", "full-physical")]
DIRECTORIES.append(ROOT / "lib" / SUBDIR)
PRIVATE = ROOT / "scratch/old-analysis/private-sparklib-experiment/lib/gnat"

def stamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

reference = ROOT / "scratch/old-analysis/sparklib-standalone-final-v5/result.json"
source_manifest = ROOT / "scratch/old-analysis/evidence/private-sparklib-experiment-source-v1.json"
if digest(reference) != "9e2db83e321d936a3eca04f82f185403ed39a3893e295ac3936bce774ca311af":
    raise SystemExit("Unexpected original dependency verification receipt")
verified = json.loads(reference.read_text())
if digest(source_manifest) != verified["source_manifest_sha256"]:
    raise SystemExit("Original private source manifest identity changed")
private_sources = json.loads(source_manifest.read_text())
for relative, expected in private_sources["source_hashes"].items():
    if digest(PRIVATE.parent.parent / relative) != expected:
        raise SystemExit("Private source/project bytes changed: " + relative)
for relative, expected in verified["dependency_artifacts"].items():
    if digest(ROOT / relative) != expected:
        raise SystemExit("Private object/ALI/archive changed: " + relative)
if verified["exit_code"] != 0 or verified["artifact_completeness"]["status"] != "TESTED complete GPR/ALI/source/archive correspondence":
    raise SystemExit("Original complete dependency validation absent")

if digest(ROOT / "core/resource_quantities.adb") != "23e67ed2f9fbb65741e5ddfab10fbde101a719feeb649a2bf1c9ae8052421a1a":
    raise SystemExit("Unexpected reviewed core source")
for path in [OUT, *DIRECTORIES]:
    if path.exists() or path.is_symlink():
        raise SystemExit("Refuse nonfresh output: " + str(path))
    ancestor = path.parent
    while ancestor != ROOT:
        if ancestor.is_symlink():
            raise SystemExit("Refuse symlink output ancestry")
        ancestor = ancestor.parent
for path in [OUT, *DIRECTORIES]:
    path.mkdir(parents=True, exist_ok=False)
for name in ("tmp", "cache"):
    (OUT / name).mkdir()

watched = {ROOT / "lib/libworldline_core.so"}
watched.update(PRIVATE.parent.parent / relative for relative in private_sources["source_hashes"])
watched.update((reference, source_manifest))
for directory in [p.parent for p in DIRECTORIES[:-1]]:
    watched.update(p for p in directory.iterdir() if p.is_file() and p.suffix in (".o", ".ali", ".a", ".so"))
for name in ("sparklib_obj", "sparklib_lib"):
    watched.update(p for p in (PRIVATE / name).rglob("*") if p.is_file())
if not (PRIVATE / "sparklib.gpr").is_file() or not any(p.suffix == ".a" for p in watched):
    raise SystemExit("Missing original private prebuilt dependency")

def identities():
    return {str(p.relative_to(ROOT)): digest(p) for p in sorted(watched) if p.is_file()}

env = dict(os.environ)
env.update(GPR_PROJECT_PATH=str(PRIVATE), WORLDLINE_BUILD="checks", TMPDIR=str(OUT / "tmp"),
           XDG_CACHE_HOME=str(OUT / "cache"), PYTHONDONTWRITEBYTECODE="1")
env.pop("GPR_TOOL", None)
command = ["gprbuild", "-p", "-P", "core/worldline_core.gpr", "-j2", "--subdirs=" + SUBDIR,
           "-XWORLDLINE_BUILD=checks", "-XSPARKLIB_MODE=full", "-XSPARKLIB_BUILD=Production",
           "-XSPARKLIB_LIBRARY_TYPE=static", "-XSPARKLIB_INSTALLED=True",
           "-XWORLDLINE_PRIVATE_SPARKLIB_PREBUILT=True", "-cargs:Ada", "-fPIC"]
argv = ["bwrap", "--die-with-parent", "--ro-bind", "/", "/", "--dev", "/dev", "--proc", "/proc",
        "--bind", str(OUT), str(OUT), "--bind", str(OUT / "tmp"), "/tmp"]
for directory in DIRECTORIES:
    argv += ["--bind", str(directory), str(directory)]
argv += ["--chdir", str(ROOT), *command]
receipt = {"started_utc": stamp(), "cwd": str(ROOT), "argv": argv, "gpr_argv": command,
           "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
           "core_source_sha256": digest(ROOT / "core/resource_quantities.adb"), "method_sha256": digest(Path(__file__)),
           "watched_before": identities(), "environment": {key: env.get(key) for key in ("PATH", "GPR_PROJECT_PATH", "GPR_TOOL", "WORLDLINE_BUILD", "TMPDIR", "XDG_CACHE_HOME")},
           "scope": "Complete original production aggregate build in fresh outputs; not complete proof or final freeze"}
receipt["original_private_dependency"] = {"receipt_sha256": digest(reference), "source_manifest_sha256": digest(source_manifest), "all_pinned_sources_and_artifacts_match": True}
for tool in ("gnatls", "gprbuild", "gcc"):
    path = Path(shutil.which(tool)).resolve()
    result = subprocess.run([str(path), "--version"], capture_output=True, text=True, env=env)
    receipt[tool] = {"path": str(path), "sha256": digest(path), "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
    if result.returncode:
        raise SystemExit("Version query failed")
(OUT / "launch.json").write_text(json.dumps(receipt, indent=2) + "\n")
with (OUT / "stdout").open("xb") as stdout, (OUT / "stderr").open("xb") as stderr:
    result = subprocess.run(argv, cwd=ROOT, env=env, stdout=stdout, stderr=stderr)
receipt.update(ended_utc=stamp(), exit_code=result.returncode, watched_after=identities(),
               core_source_sha256_after=digest(ROOT / "core/resource_quantities.adb"),
               stdout_sha256=digest(OUT / "stdout"), stderr_sha256=digest(OUT / "stderr"))
library = ROOT / "lib" / SUBDIR / "libworldline_core.so"
receipt["library"] = {"path": str(library), "sha256": digest(library)} if library.is_file() and not library.is_symlink() else None
receipt["assertion_alis"] = {}
for name in ("resource_quantities.ali", "worldline-resource_policy_c_api.ali"):
    path = ROOT / "obj/core" / SUBDIR / name
    receipt["assertion_alis"][name] = {"path": str(path), "sha256": digest(path), "gnata": "A -gnata" in path.read_text().splitlines()} if path.is_file() else None
receipt["watched_unchanged"] = receipt["watched_before"] == receipt["watched_after"]
receipt["validation_passed"] = result.returncode == 0 and receipt["library"] is not None and receipt["watched_unchanged"] and receipt["core_source_sha256"] == receipt["core_source_sha256_after"] and all(value and value["gnata"] for value in receipt["assertion_alis"].values())
(OUT / "result.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps({"result": str(OUT / "result.json"), "exit_code": result.returncode,
                  "validation_passed": receipt["validation_passed"], "library": receipt["library"]}))
raise SystemExit(0 if receipt["validation_passed"] else result.returncode or 125)
