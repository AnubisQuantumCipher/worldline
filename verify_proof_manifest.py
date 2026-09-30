#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


# Pinned here and imported by prove.sh, so the gate and this verifier cannot disagree, and a
# manifest cannot vouch for itself by shrinking what it claims.
# Floor for the total proved-check count. Lower it only as a deliberate edit.
MINIMUM_CHECKS = 251
# Subprograms whose proof is a claim of this release.
REQUIRED_PROVED = [
    "Worldline.Collapse.Decide",
    "Worldline.Collapse_Wire.Decide_Wire",
    "Worldline.Collapse_Wire.Decode",
    "Worldline.Evaluation.Admissible",
    "Worldline.Evaluation.Advance",
    "Worldline.Evaluation.Classify",
    "Worldline.Evaluation.Roster_Complete",
    "Worldline.Evaluation.Transition_Allowed",
    "Worldline.Transitions.Advance",
    "Worldline.Transitions.Transaction_Allowed",
]
# The one unit not analyzed on purpose: the C ABI entry points (SPARK_Mode => Off) -- pointer
# dereference, exception handlers, file and byte hashing marshalling, and the decoding and
# validation of evaluation observations, classifications and presence records. From 1.9.0 the
# collapse request is not here: Worldline.Collapse_Wire decodes and validates it, and is proved.
UNANALYZED_BOUNDARY = {"worldline-c_api"}


# The contracts this release claims, pinned by digest (1.9.0; review of a23c265). The check
# floor cannot see a postcondition clause deleted -- GNATprove counts a whole Post as one check --
# and the C boundary is exempt from the SPARK_Mode screen, so neither the count nor the coverage
# parse notices a weakened Decide or a policy shortcut in Collapse_Decide. Each pin covers a
# specification's text with comments and layout removed, or one C-boundary subprogram's body.
# Changing a pinned contract is a deliberate edit of this table; derive the values with
# `python3 verify_proof_manifest.py --print-contract-pins`, never by hand.
CONTRACT_PINS = {
    "core/worldline-collapse.ads": "6bf3d3bdf08e75fa9114100dc7459c2ba7c37de21ae83e3acf8357244ed39b69",
    "core/worldline-collapse_wire.ads": "223bedbbe60ed2480ff4a1ad267122e1582f161daa4f8e661e1ad1a7600de3b5",
    "core/worldline-identities.ads": "ceed7b08935c05d52014b8f7e8d68f8b8876214428be145aa88bf2878cabca21",
    "core/worldline-evaluation.ads": "06f281db13982fa57cb96391c54e4d53268577b52422d5f6e640804a016c3b9e",
    "core/worldline-transitions.ads": "1b332423aa2136df53ac2feb3ee8dd4c0aeea1bf0c372cde9b1d614079d7bfd1",
    "core/worldline-c_api.adb#Collapse_Decide": "ac2e8ef5029d2c1dc201d5cfa4881ab836110f8fa67a507d268662ffa452b77f",
}


def normalized_ada(text: str) -> str:
    """Ada source with `--` comments removed (outside string literals) and all layout
    collapsed to single spaces, so a pin changes only when the code does."""
    lines = []
    for line in text.splitlines():
        in_string = False
        cut = len(line)
        for index, char in enumerate(line):
            if char == '"':
                in_string = not in_string
            elif not in_string and line.startswith("--", index):
                cut = index
                break
        lines.append(line[:cut])
    return " ".join(" ".join(lines).split())


def contract_text(root: Path, key: str) -> str:
    relative, _, subprogram = key.partition("#")
    text = normalized_ada((root / relative).read_text(encoding="utf-8"))
    if not subprogram:
        return text
    start = text.find(f"function {subprogram} ")
    end = text.find(f"end {subprogram};", start)
    if start < 0 or end < 0 or text.find(f"function {subprogram} ", start + 1) >= 0:
        raise ValueError(f"cannot isolate {key}")
    return text[start:end + len(f"end {subprogram};")]


def contract_pin(root: Path, key: str) -> str:
    return hashlib.sha256(contract_text(root, key).encode("utf-8")).hexdigest()


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
    if "--print-contract-pins" in sys.argv[1:]:
        for key in CONTRACT_PINS:
            print(f'    "{key}": "{contract_pin(root, key)}",')
        return 0
    for key, pinned in CONTRACT_PINS.items():
        try:
            actual = contract_pin(root, key)
        except (OSError, ValueError) as exc:
            print(f"pinned contract unreadable: {key}: {exc}", file=sys.stderr)
            return 1
        if actual != pinned:
            print(f"pinned contract changed: {key} (a deliberate change updates CONTRACT_PINS)", file=sys.stderr)
            return 1
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
