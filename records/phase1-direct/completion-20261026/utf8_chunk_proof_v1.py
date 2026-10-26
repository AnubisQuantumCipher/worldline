"""Qualify the complete outside-production Chunk unit, with actual dependencies."""
from pathlib import Path
import json
import re
import shutil
import sys
import numeric_isolated_v1 as common

BASE = common.BASE / "utf8-budgeted-chunks-v1/qualification-v2"
OUT = common.BASE / "utf8-chunk-proof-v1"
PROJECT = BASE / "utf8_chunk_qualification.gpr"
RECIPE = BASE / "project-source-recipe-v2.json"


def source_pins(recipe):
    paths = {PROJECT, RECIPE}
    for name in re.findall(r'"([a-z_][a-z0-9_-]*\.ad[bs])"', PROJECT.read_text()):
        candidates = [p for p in (BASE / name, common.ROOT / "core" / name) if p.is_file()]
        if len(candidates) != 1:
            raise RuntimeError("ambiguous source binding: " + name)
        paths.add(candidates[0])
    for name in ("attest_sha256.gpr", "attest/attest.ads", "attest/attest-sha256.ads", "attest/attest-sha256.adb"):
        paths.add(common.ROOT / "core" / name)
    private = common.CANDIDATE / "private-dependency-sources.json"
    paths.update(common.ROOT / item["path"] for item in json.loads(private.read_text()))
    for name, expected in recipe["root_source_expected_sha256"].items():
        if common.digest(BASE / name) != expected:
            raise RuntimeError("reviewed proposal changed")
    return {str(p): common.digest(p) for p in sorted(paths)}


def main():
    if common.digest(RECIPE) != "5d90602c325807316bcad906e104699c40db196a1a930a716deb354907e30fe7":
        raise RuntimeError("reviewed recipe changed")
    recipe = json.loads(RECIPE.read_text())
    if common.digest(PROJECT) != recipe["project_sha256"]:
        raise RuntimeError("reviewed project changed")
    pins = source_pins(recipe)
    OUT.mkdir(exist_ok=False)
    argv = ["gnatprove", "-P", str(PROJECT), "--no-inlining", "--mode=all",
            "--level=3", "--report=all", "--checks-as-errors=on", "--proof-warnings=on",
            "--warnings=error", "--memlimit=1024", "--timeout=5", "-j2",
            "-XWORLDLINE_BUILD=checks", "-XSPARKLIB_MODE=full", "-XSPARKLIB_BUILD=Production",
            "-XSPARKLIB_LIBRARY_TYPE=static", "-XSPARKLIB_INSTALLED=True", "-u", "utf8_chunk_proposal.adb"]
    record = {"start": common.stamp(), "argv": argv, "source_sha256": pins,
              "disk_samples": [], "phase_acceptance": False, "whole_unit": True}
    result = OUT / "result.json"
    result.write_text(json.dumps(record, indent=2) + "\n")
    with (OUT / "stdout").open("xb") as stdout, (OUT / "stderr").open("xb") as stderr:
        code, stop = common.invoke(argv, stdout, stderr, record["disk_samples"])
    fresh = False
    match = re.search(r"Summary logged in (.+)", (OUT / "stdout").read_text())
    if match and stop is None:
        report = common.ROOT / match.group(1).strip()
        fresh = report.is_file() and report.stat().st_mtime >= common.datetime.datetime.fromisoformat(record["start"]).timestamp()
        if fresh:
            shutil.copyfile(report, OUT / "gnatprove.out")
    unchanged = all(common.digest(Path(p)) == h for p, h in pins.items())
    record.update(end=common.stamp(), exit_code=code, stop=stop, fresh_report=fresh, source_unchanged=unchanged)
    result.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({k: record[k] for k in ("exit_code", "stop", "fresh_report", "source_unchanged")}))
    return 0 if code == 0 and fresh and unchanged else 1


if __name__ == "__main__":
    sys.exit(main())
