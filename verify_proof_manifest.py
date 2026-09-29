#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


# Pinned here and imported by prove.sh, so the gate and this verifier cannot disagree, and a
# manifest cannot vouch for itself by shrinking what it claims.
# Floor for the total proved-check count. Lower it only as a deliberate edit.
MINIMUM_CHECKS = 156
# Subprograms whose proof is a claim of this release.
REQUIRED_PROVED = [
    "Worldline.Collapse.Decide",
    "Worldline.Evaluation.Admissible",
    "Worldline.Evaluation.Advance",
    "Worldline.Evaluation.Classify",
    "Worldline.Evaluation.Roster_Complete",
    "Worldline.Evaluation.Transition_Allowed",
    "Worldline.Transitions.Advance",
    "Worldline.Transitions.Transaction_Allowed",
]
# The one unit not analyzed on purpose: the C ABI decode (SPARK_Mode => Off).
UNANALYZED_BOUNDARY = {"worldline-c_api"}


def expected_units(root: Path) -> set[str]:
    """Every SPARK unit the proof must cover: one per core specification, plus Attest."""
    units = {path.stem for path in (root / "core").glob("*.ads")}
    units |= {path.stem for path in (root / "core" / "attest").glob("*.ads")}
    return units


def source_paths(root: Path) -> dict[str, Path]:
    result: dict[str, Path] = {
        "worldline.gpr": root / "worldline.gpr",
        "attest/attest.ads": root / "core/attest/attest.ads",
        "attest/attest-sha256.ads": root / "core/attest/attest-sha256.ads",
        "attest/attest-sha256.adb": root / "core/attest/attest-sha256.adb",
    }
    for pattern in ("*.ads", "*.adb", "*.gpr", "*.h"):
        for path in sorted((root / "core").glob(pattern)):
            result[f"core/{path.name}"] = path
    return result


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parent
    manifest_path = root / "proof-manifest.json"
    if not manifest_path.is_file():
        print("proof manifest missing", file=sys.stderr)
        return 1
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"invalid proof manifest: {exc}", file=sys.stderr)
        return 1

    proof = manifest.get("proof", {})
    if any(proof.get(key) != 0 for key in ("justified", "unproved", "pragmaAssume")):
        print("proof manifest does not record a zero-exception proof", file=sys.stderr)
        return 1

    total = proof.get("total")
    if type(total) is not int or proof.get("minimumChecks") != MINIMUM_CHECKS or total < MINIMUM_CHECKS:
        print(f"proof manifest records {total!r} checks against a floor of {MINIMUM_CHECKS}", file=sys.stderr)
        return 1
    coverage = manifest.get("coverage")
    if not isinstance(coverage, dict):
        print("proof manifest records no per-subprogram coverage", file=sys.stderr)
        return 1
    subprograms = coverage.get("subprograms")
    units = coverage.get("units")
    if coverage.get("requiredProved") != REQUIRED_PROVED or set(coverage.get("unanalyzedBoundary") or []) != UNANALYZED_BOUNDARY:
        print("proof manifest does not claim the pinned required subprograms and boundary", file=sys.stderr)
        return 1
    if not isinstance(subprograms, dict) or not subprograms or not isinstance(units, dict):
        print("proof manifest coverage is empty", file=sys.stderr)
        return 1
    if any(not (isinstance(value, dict) and value.get("proved") is True and type(value.get("checks")) is int)
           for value in subprograms.values()):
        print("proof manifest records an unproved subprogram", file=sys.stderr)
        return 1
    unproved_required = [name for name in REQUIRED_PROVED if name not in subprograms]
    if unproved_required:
        print("required subprograms not proved: " + ", ".join(unproved_required), file=sys.stderr)
        return 1
    missing_units = sorted(expected_units(root) - set(units))
    if missing_units:
        print("proof manifest does not cover units: " + ", ".join(missing_units), file=sys.stderr)
        return 1
    for unit, counts in units.items():
        if not isinstance(counts, dict) or counts.get("analyzed") != counts.get("available") or (
                unit not in UNANALYZED_BOUNDARY and not counts.get("available")):
            print(f"proof manifest records an unanalyzed unit: {unit}", file=sys.stderr)
            return 1

    paths = source_paths(root)
    recorded = manifest.get("sourceHashes")
    if not isinstance(recorded, dict) or set(recorded) != set(paths):
        print("proof source set changed after proof", file=sys.stderr)
        return 1
    for key, path in paths.items():
        if not path.is_file() or recorded[key] != digest(path):
            print(f"proof source changed after proof: {key}", file=sys.stderr)
            return 1

    if "--sources-only" in sys.argv[1:]:
        # A source release carries no built library; the manifest still records the hash of
        # the library the proof ran against, for anyone who builds and compares.
        print("proof manifest verified (sources; library not checked)")
        return 0
    library = manifest.get("library", {})
    library_path = root / str(library.get("path", ""))
    if not library_path.is_file() or library.get("sha256") != digest(library_path):
        print("proved library changed after proof", file=sys.stderr)
        return 1

    print("proof manifest verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
