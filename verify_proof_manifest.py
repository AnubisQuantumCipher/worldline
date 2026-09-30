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
# specification's text with comments and layout removed, or the whole unproved C boundary body
# (a pin on Collapse_Decide's text alone could be sidestepped by a declaration elsewhere in the
# file that its unqualified names resolve to; review of 19d0297).
# Changing a pinned contract is a deliberate edit of this table; derive the values with
# `python3 verify_proof_manifest.py --print-contract-pins`, never by hand.
CONTRACT_PINS = {
    # The project files decide which file is compiled as each unit; a pin on a source's text
    # binds nothing if they may redirect it (review of ab1d4bb).
    "worldline.gpr": "edc9682fe5cb62ab041cc586de03c59e1d30cd0de7d8dcc7646ebe50ce6c0021",
    "core/worldline_core.gpr": "0e1b7c0bf5bbcab516e544c63aa29302d1bc2602886e7ee3e0a535d977c4cebf",
    "core/worldline_core_sources.gpr": "fc7be69ee1d21269d12f600a3dab22b53c21362d178280d5f8ddcacf5c09802c",
    "core/attest_sha256.gpr": "5d75d10379e9397a9e08517d56728b2f53479fd7c0e9dff3b5dccaa8e8c0f9ee",
    "tests/worldline_tests.gpr": "d452b39691f23078635cb829b0ef94040342cefec9288cd4cccb821a51ca6a82",
    "core/worldline.ads": "4e08ff1dedc1f28b526a19b37c343b2d71f5f1e35409abda2afdbd92a73ab866",
    "core/attest/attest.ads": "bb777936dfaf882e68b399dd2fdfc531e5edd0d24b5b01a6d0906161aa89e587",
    "core/attest/attest-sha256.ads": "1d38534d6bcaa9a6646225db8f26f0a7b940444cda3ed0d109816119d51bff05",
    "core/worldline-c_api.ads": "4ae114451090e2331041acdf183d5d129b8cfe116f71727d0c5fea10cecc1afa",
    "core/worldline-collapse.ads": "6bf3d3bdf08e75fa9114100dc7459c2ba7c37de21ae83e3acf8357244ed39b69",
    "core/worldline-collapse_wire.ads": "223bedbbe60ed2480ff4a1ad267122e1582f161daa4f8e661e1ad1a7600de3b5",
    "core/worldline-identities.ads": "ceed7b08935c05d52014b8f7e8d68f8b8876214428be145aa88bf2878cabca21",
    "core/worldline-evaluation.ads": "06f281db13982fa57cb96391c54e4d53268577b52422d5f6e640804a016c3b9e",
    "core/worldline-transitions.ads": "1b332423aa2136df53ac2feb3ee8dd4c0aeea1bf0c372cde9b1d614079d7bfd1",
    "core/worldline-c_api.adb": "ad9eb91aa00ce9165166057bca7562fd268bf16d94f0b8c42a4fc696a707b0e3",
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


def export_problems(root: Path) -> list[str]:
    """The C symbol the runtime calls for the collapse decision must be bound exactly once, to
    Collapse_Decide, whose body is pinned (review of 0ee1112: moving the binding to another
    function left every pin intact)."""
    text = normalized_ada((root / "core/worldline-c_api.ads").read_text(encoding="utf-8"))
    bindings = text.count('External_Name => "wl_collapse_decide"')
    declared = ('function Collapse_Decide (Request : C_Collapse_Request_Access) return Interfaces.Unsigned_8 '
                'with Export, Convention => C, External_Name => "wl_collapse_decide";')
    problems = []
    if bindings != 1:
        problems.append(f"wl_collapse_decide is bound {bindings} times")
    if declared not in text:
        problems.append("wl_collapse_decide is not bound to Collapse_Decide")
    return problems


# The only Ada sources the core library may be built from. Anything else under core/, at any
# depth, could be selected by a project file instead of a pinned unit.
def stray_sources(root: Path) -> list[str]:
    allowed = {f"core/{path.name}" for path in (root / "core").glob("*.ad[bs]")}
    allowed |= {"core/attest/attest.ads", "core/attest/attest-sha256.ads", "core/attest/attest-sha256.adb"}
    found = {path.relative_to(root).as_posix() for path in (root / "core").rglob("*.ad[bs]")}
    return sorted(found - allowed)


def contract_problems(root: Path) -> list[str]:
    problems = export_problems(root)
    problems += [f"an Ada source outside the pinned set could be compiled into the core: {path}" for path in stray_sources(root)]
    for key, pinned in CONTRACT_PINS.items():
        try:
            actual = contract_pin(root, key)
        except (OSError, ValueError) as exc:
            problems.append(f"pinned contract unreadable: {key}: {exc}")
            continue
        if actual != pinned:
            problems.append(f"pinned contract changed: {key} (a deliberate change updates CONTRACT_PINS)")
    return problems


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
    problems = contract_problems(root)
    if problems:
        print("; ".join(problems), file=sys.stderr)
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
