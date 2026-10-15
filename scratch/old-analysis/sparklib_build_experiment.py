#!/usr/bin/env python3
"""Coordinator-invoked experiment; run each phase through phase1_heavy.py.

This script does not acquire the shared lock itself. It refuses an absent
worktree-local TMPDIR and uses a read-only-root bubblewrap mount for compilation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
from collections import Counter
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[2]
PRIVATE = ROOT / "scratch/old-analysis/private-sparklib-experiment"
PROJECT = PRIVATE / "lib/gnat/sparklib.gpr"
ARCHIVE = PRIVATE / "lib/gnat/sparklib_lib/libsparklib.a"
SOURCE_MANIFEST = ROOT / "scratch/old-analysis/evidence/private-sparklib-experiment-source-v1.json"
SCENARIO = ["-XSPARKLIB_MODE=full", "-XSPARKLIB_BUILD=Production",
            "-XSPARKLIB_LIBRARY_TYPE=static", "-XSPARKLIB_INSTALLED=True"]


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def output_artifacts() -> dict[str, str]:
    candidates = [ARCHIVE]
    for folder in (PRIVATE / "lib/gnat/sparklib_obj", PRIVATE / "lib/gnat/sparklib_lib"):
        for pattern in ("*.o", "*.ali"):
            candidates.extend(folder.glob(pattern))
    return {str(p.relative_to(ROOT)): digest(p) for p in sorted(set(candidates)) if p.is_file()}


def verify_dependency(out: Path, env: dict[str, str], source: dict) -> dict:
    """GPR-selected compilation units + ALI source units, never one object per spec."""
    observed = {}
    for kind, flag in (("sources", "-s"), ("objects", "-o")):
        command = ["gprls", "-P" + str(PROJECT), "-U", flag, *SCENARIO,
                   "-XWORLDLINE_PRIVATE_SPARKLIB_PREBUILT=False"]
        proc = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True)
        (out / ("gprls-" + kind + ".stdout")).write_text(proc.stdout)
        (out / ("gprls-" + kind + ".stderr")).write_text(proc.stderr)
        if proc.returncode != 0:
            raise RuntimeError("gprls could not establish complete " + kind + " roster")
        paths = [Path(line.strip()) for line in proc.stdout.splitlines() if line.strip()]
        if not paths or any(not p.is_absolute() or not p.is_relative_to(PRIVATE) or not p.is_file() for p in paths):
            raise RuntimeError("gprls emitted missing or out-of-private " + kind + " artifact")
        observed[kind] = paths
    # GPR selects a body where present, otherwise a compilable spec. The .ali U
    # records cover both spec and body, including generic compilation units.
    expected_objects = {p.with_suffix(".o").name for p in observed["sources"]}
    if expected_objects != {p.name for p in observed["objects"]}:
        raise RuntimeError("GPR source-to-object roster mismatch")
    # This shipped alternative is expressly a replacement for testing body mode,
    # not a unit selected by this full-mode project. Pin the sole exception to
    # exact bytes, and require GPR to select the real full-mode SPARK spec.
    alternative = "include/spark/spark__exec.ads"
    alternative_sha256 = "63ad0b8c94c229a16813cf8583b3e9872606456a1e1c4d7cda99c7d831a1a286"
    if (source["source_hashes"].get(alternative) != alternative_sha256
            or digest(PRIVATE / alternative) != alternative_sha256
            or PRIVATE / "include/spark/full/spark.ads" not in observed["sources"]):
        raise RuntimeError("SPARK full-mode selection or pinned alternate identity changed")
    active_sources = {Path(rel).name for rel in source["source_hashes"]
                      if rel != alternative and Path(rel).suffix in (".ads", ".adb") and Path(rel).parent in
                      (Path("include/spark"), Path("include/spark/full"))}
    represented_sources = set()
    mapping = []
    for obj in observed["objects"]:
        ali = obj.with_suffix(".ali")
        if not ali.is_file():
            raise RuntimeError("Expected ALI missing: " + str(ali))
        lines = ali.read_text().splitlines()
        units = [line.split() for line in lines if line.startswith("U ")]
        if not units or "A -fPIC" not in lines:
            raise RuntimeError("ALI unit/PIC compilation identity absent: " + str(ali))
        represented_sources.update(unit[2] for unit in units)
        mapping.append({"object": str(obj.relative_to(ROOT)), "ali": str(ali.relative_to(ROOT)),
                        "source_units": units, "object_sha256": digest(obj), "ali_sha256": digest(ali)})
    if represented_sources != active_sources:
        raise RuntimeError("ALI source closure mismatch: missing=" + repr(sorted(active_sources - represented_sources))
                           + " unexpected=" + repr(sorted(represented_sources - active_sources)))
    listing = subprocess.run(["ar", "t", str(ARCHIVE)], cwd=ROOT, env=env, capture_output=True, text=True)
    (out / "archive-members.stdout").write_text(listing.stdout)
    (out / "archive-members.stderr").write_text(listing.stderr)
    members = listing.stdout.splitlines()
    if listing.returncode != 0 or Counter(members) != Counter(expected_objects):
        raise RuntimeError("Archive membership does not equal the complete GPR object roster")
    for obj in observed["objects"]:
        proc = subprocess.Popen(["ar", "p", str(ARCHIVE), obj.name], cwd=ROOT, env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        h = hashlib.sha256()
        assert proc.stdout is not None
        for chunk in iter(lambda: proc.stdout.read(1024 * 1024), b""):
            h.update(chunk)
        if proc.wait() != 0 or h.hexdigest() != digest(obj):
            raise RuntimeError("Archived member differs from compiled object: " + obj.name)
    return {"status": "TESTED complete GPR/ALI/source/archive correspondence", "mapping": mapping,
            "active_sources": sorted(active_sources),
            "nonselected_alternative": {"path": alternative, "sha256": alternative_sha256,
                "reason": "shipped body-mode replacement; GPR selects full/spark.ads"},
            "archive_members": members,
            "archive_sha256": digest(ARCHIVE)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("standalone", "full"))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--standalone-receipt", type=Path)
    args = parser.parse_args()
    out = args.out.resolve()
    if not out.is_relative_to(ROOT / "scratch/old-analysis"):
        raise SystemExit("Output must stay in owned scratch")
    tmp = Path(os.environ.get("TMPDIR", "")).resolve()
    if not os.environ.get("TMPDIR") or not tmp.is_relative_to(ROOT) or not tmp.is_dir():
        raise SystemExit("Use the admitted heavy runner and its worktree-local TMPDIR")
    out.mkdir(parents=True, exist_ok=False)
    source = json.loads(SOURCE_MANIFEST.read_text())
    for relative, expected in source["source_hashes"].items():
        if digest(PRIVATE / relative) != expected:
            raise SystemExit("Private dependency source changed: " + relative)
    if digest(PROJECT) != source["modified_project_sha256"]:
        raise SystemExit("Private project changed after review")
    before_artifacts = output_artifacts()
    if args.phase == "full":
        if args.standalone_receipt is None:
            raise SystemExit("Full phase requires successful standalone receipt")
        receipt = json.loads(args.standalone_receipt.read_text())
        if receipt.get("phase") != "standalone" or receipt.get("exit_code") != 0:
            raise SystemExit("Standalone build did not succeed")
        if receipt.get("source_manifest_sha256") != digest(SOURCE_MANIFEST):
            raise SystemExit("Source manifest differs from standalone build")
        if receipt.get("dependency_artifacts") != output_artifacts():
            raise SystemExit("Dependency artifacts differ from standalone build")
        if not receipt.get("archive_members"):
            raise SystemExit("Standalone archive has no recorded members")
        if not receipt.get("artifact_completeness") or receipt.get("verification_error"):
            raise SystemExit("Standalone artifact completeness was not verified")

    env = dict(os.environ)
    env["GPR_PROJECT_PATH"] = str(PROJECT.parent) + ":" + env.get("GPR_PROJECT_PATH", "")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    # GPR_TOOL is owned by the actual GPR executable, never spoofed here.
    env.pop("GPR_TOOL", None)
    scenario = [*SCENARIO,
                "-XWORLDLINE_PRIVATE_SPARKLIB_PREBUILT=" + ("False" if args.phase == "standalone" else "True")]
    target = str(PROJECT) if args.phase == "standalone" else "worldline.gpr"
    command = ["gprbuild", "-p", "-P", target, "-j2", *scenario, "-cargs:Ada", "-fPIC"]
    isolated = ["bwrap", "--die-with-parent", "--ro-bind", "/", "/", "--dev", "/dev",
                "--proc", "/proc", "--bind", str(ROOT), str(ROOT), "--bind", str(tmp), "/tmp",
                "--chdir", str(ROOT), *command]
    metadata = {"utc": datetime.now(timezone.utc).isoformat(), "phase": args.phase,
                "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "argv": isolated, "gpr_argv": command, "cwd": str(ROOT),
                "source_manifest_sha256": digest(SOURCE_MANIFEST), "scope": "build only, never proof or acceptance"}
    (out / "launch.json").write_text(json.dumps(metadata, indent=2) + "\n")
    versions = {}
    for tool in ("gnat", "gprbuild"):
        proc = subprocess.run([tool, "--version"], cwd=ROOT, env=env, capture_output=True, text=True)
        versions[tool] = {"exit_code": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}
    (out / "versions.json").write_text(json.dumps(versions, indent=2) + "\n")
    with (out / "stdout").open("wb") as stdout, (out / "stderr").open("wb") as stderr:
        result = subprocess.run(isolated, cwd=ROOT, env=env, stdout=stdout, stderr=stderr)
    metadata["exit_code"] = result.returncode
    metadata["dependency_artifacts"] = output_artifacts()
    metadata["archive_members"] = []
    if ARCHIVE.is_file():
        listing = subprocess.run(["ar", "t", str(ARCHIVE)], cwd=ROOT, env=env, capture_output=True, text=True)
        (out / "archive-members.stdout").write_text(listing.stdout)
        (out / "archive-members.stderr").write_text(listing.stderr)
        metadata["archive_listing_exit_code"] = listing.returncode
        metadata["archive_members"] = listing.stdout.splitlines()
    metadata["source_unchanged"] = all(digest(PRIVATE / rel) == expected for rel, expected in source["source_hashes"].items())
    metadata["dependency_unchanged_during_full"] = args.phase != "full" or before_artifacts == output_artifacts()
    try:
        if result.returncode == 0:
            metadata["artifact_completeness"] = verify_dependency(out, env, source)
        if result.returncode == 0 and args.phase == "full":
            expected = [ROOT / "lib/libworldline_core.so", ROOT / "bin/worldline_core_tests",
                        ROOT / "bin/worldline_core_fuzz"]
            if any(not path.is_file() or path.stat().st_size == 0 for path in expected):
                raise RuntimeError("Full aggregate is missing a declared library or main executable")
            metadata["declared_build_outputs"] = {str(path.relative_to(ROOT)): digest(path) for path in expected}
        if args.phase == "full" and not metadata["dependency_unchanged_during_full"]:
            raise RuntimeError("Dependency object/ALI/archive bytes changed during full build")
    except (OSError, RuntimeError) as exc:
        metadata["verification_error"] = str(exc)
    metadata["completed_utc"] = datetime.now(timezone.utc).isoformat()
    (out / "result.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps({"phase": args.phase, "exit_code": result.returncode, "out": str(out)}))
    if not metadata["source_unchanged"]:
        raise SystemExit("Source changed during build")
    if metadata.get("verification_error"):
        raise SystemExit(metadata["verification_error"])
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
