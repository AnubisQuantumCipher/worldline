"""Bounded diagnostic proof driver; no whole-project acceptance authority."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
CANDIDATE = BASE / "bignum-padding/numeric-qualification-candidate-v1"
OUT = BASE / "numeric-isolated-v1"
RESERVE = 10_000_000_000
RECIPE_HASH = "1c6298ecb45c3158ce6d959e59ee8c3396b4cf1b45213e71e8c4b6937f501b46"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def validate(recipe, manifest):
    pins = dict(recipe["product_sources_sha256"])
    pins[recipe["private_import_absolute"]] = recipe["private_import_sha256"]
    pins.update({item["path"]: item["sha256"] for item in manifest})
    if len(manifest) != 134 or len(pins) != 139:
        raise RuntimeError("unexpected source set")
    for name, expected in pins.items():
        if digest(ROOT / name) != expected:
            raise RuntimeError("source identity mismatch: " + name)
    if digest(CANDIDATE / "numeric_qualification.gpr") != recipe["project_sha256"]:
        raise RuntimeError("diagnostic project changed")


def invoke(argv, stdout, stderr, samples):
    if shutil.disk_usage(ROOT).free < RESERVE + 60_000_000:
        raise RuntimeError("insufficient diagnostic disk admission")
    process = subprocess.Popen(argv, cwd=ROOT, stdout=stdout, stderr=stderr)
    for _ in range(180):
        free = shutil.disk_usage(ROOT).free
        samples.append({"utc": stamp(), "free_bytes": free})
        if process.poll() is not None:
            return process.returncode, None
        if free < RESERVE + 30_000_000:
            process.terminate()
            return None, "disk safety stop; outer scope cleans descendants"
        time.sleep(1)
    process.terminate()
    return None, "180s deadline; outer scope cleans descendants"


def target(recipe, manifest, item):
    validate(recipe, manifest)
    name = item["name"]
    record = dict(item, start=stamp(), disk_samples=[], phase_acceptance=False)
    output = OUT / (name + ".json")
    output.write_text(json.dumps(record, indent=2) + "\n")
    stdout_path = OUT / (name + ".stdout")
    with stdout_path.open("xb") as stdout, (OUT / (name + ".stderr")).open("xb") as stderr:
        code, stop = invoke(item["argv"], stdout, stderr, record["disk_samples"])
    match = re.search(r"Summary logged in (.+)", stdout_path.read_text())
    report_ok = False
    if match and stop is None:
        report = ROOT / match.group(1).strip()
        report_ok = report.is_file() and report.stat().st_mtime >= datetime.datetime.fromisoformat(record["start"]).timestamp()
        if report_ok:
            shutil.copyfile(report, OUT / (name + ".gnatprove.out"))
    validate(recipe, manifest)
    record.update(end=stamp(), exit_code=code, stop=stop, fresh_report=report_ok)
    output.write_text(json.dumps(record, indent=2) + "\n")
    print(name, code, "fresh_report", report_ok, "stop", stop, flush=True)
    return code == 0 and report_ok, stop is not None or not report_ok


def main():
    recipe_path = CANDIDATE / "recipe.json"
    if digest(recipe_path) != RECIPE_HASH:
        raise RuntimeError("reviewed recipe changed")
    recipe = json.loads(recipe_path.read_text())
    manifest_path = CANDIDATE / "private-dependency-sources.json"
    if digest(manifest_path) != recipe["private_dependency_manifest_sha256"]:
        raise RuntimeError("dependency manifest changed")
    manifest = json.loads(manifest_path.read_text())
    validate(recipe, manifest)
    if len(recipe["targets"]) != 6:
        raise RuntimeError("unexpected target count")
    OUT.mkdir(exist_ok=False)
    success = True
    for item in recipe["targets"]:
        passed, stop = target(recipe, manifest, item)
        success = passed and success
        if stop:
            return 1
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
