"""The proof-manifest checks, shared by the proof gate and the runtime (1.9.2, OB-084/OB-085).

verify_proof_manifest.py (the build and install gate) and proof.ProofStatus (what a receipt's
`invariantPreservation` says) both import this module, so the gate and the runtime cannot
disagree about what a manifest must show. It imports nothing that loads the kernel.

Pinned here: the check floor, the subprograms whose proof is a claim of this release, the one
unit left unanalyzed on purpose, and the contracts the claim depends on (CONTRACT_PINS).
Changing any of them is a deliberate edit of this file; derive pin values with
`python3 verify_proof_manifest.py --print-contract-pins`, never by hand.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping

# Accepted minimum for this proof scope. Keep or raise it; restore proof coverage
# when analysis falls below it. A candidate cannot lower its own acceptance bar.
MINIMUM_CHECKS = 251
# Subprograms whose proof is a claim of this release. 1.9.2 adds the chain links and appends the
# receipt and causal chains are built from, so dropping them from the proof refuses (OB-085).
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
    "Worldline.Receipts.Append",
    "Worldline.Receipts.Link",
    "Worldline.Causal_Graph.Append",
    "Worldline.Causal_Graph.Link",
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
# 1.9.2 (OB-085): the receipt and causal chains, the world identity and the ancestry claim are
# pinned too. Receipts.Link and Causal_Graph.Link carry no postcondition (Global => null only),
# so the value they return is set by their BODIES, which are pinned as well.
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
    "core/worldline-receipts.ads": "45e8c276cf73d8d0311f247a1c87e9bf88614d46fde2bfe6c5f858ee2d20827b",
    "core/worldline-receipts.adb": "1ee34566208a835951d21d79be1bc6ffd287b3c61b43bad76210a7a546b156bb",
    "core/worldline-causal_graph.ads": "1f5271eed9dc2bdacf2642a9647bab7a2b29a707c7749664ba09f7fac79ce14f",
    "core/worldline-causal_graph.adb": "a7e80ad0b061be82ce2727e5aeabd6fa27335807d66445ad01dc3fb3931dfab5",
    "core/worldline-world.ads": "3e64007aa82d309185c9e3b1f2abf870e5de7123d35ebc5e6eadca9cd2121ef5",
    "core/worldline-ancestry.ads": "718cb0a45fe3bfa5b4d1b29696ec544b827b0d9cca74b59f836b08b01c1485db",
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


# Fixed source inventory of the reviewed Phase 1 core. Adding or removing a unit requires
# an explicit reviewed change here; discovering a file must never grant it permission.
# Membership is not proof: every existing contract pin, source digest, expected-unit,
# per-subprogram coverage and proof-floor check remains independently required.
DECLARED_CORE_ADA_SOURCES = frozenset({
    'core/attest/attest-sha256.adb',
    'core/attest/attest-sha256.ads',
    'core/attest/attest.ads',
    'core/evaluation_completion.adb',
    'core/evaluation_completion.ads',
    'core/evaluation_completion_c.adb',
    'core/evaluation_completion_c.ads',
    'core/evaluation_completion_roster.adb',
    'core/evaluation_completion_roster.ads',
    'core/evaluation_epoch.adb',
    'core/evaluation_epoch.ads',
    'core/evaluation_history.adb',
    'core/evaluation_history.ads',
    'core/evaluation_pending.adb',
    'core/evaluation_pending.ads',
    'core/evaluation_pending_c.adb',
    'core/evaluation_pending_c.ads',
    'core/evaluation_pending_v2.adb',
    'core/evaluation_pending_v2.ads',
    'core/evaluation_pending_v2_c.adb',
    'core/evaluation_pending_v2_c.ads',
    'core/resource_admission.adb',
    'core/resource_admission.ads',
    'core/resource_ledger.adb',
    'core/resource_ledger.ads',
    'core/resource_quantities.adb',
    'core/resource_quantities.ads',
    'core/resource_reservation_lifecycle.adb',
    'core/resource_reservation_lifecycle.ads',
    'core/resource_reservation_transition.adb',
    'core/resource_reservation_transition.ads',
    'core/spark-big_integers.ads',
    'core/spark.ads',
    'core/worldline-ancestry.adb',
    'core/worldline-ancestry.ads',
    'core/worldline-c_api.adb',
    'core/worldline-c_api.ads',
    'core/worldline-causal_graph.adb',
    'core/worldline-causal_graph.ads',
    'core/worldline-collapse.adb',
    'core/worldline-collapse.ads',
    'core/worldline-collapse_wire.adb',
    'core/worldline-collapse_wire.ads',
    'core/worldline-evaluation.adb',
    'core/worldline-evaluation.ads',
    'core/worldline-evaluation_history_c_api.adb',
    'core/worldline-evaluation_history_c_api.ads',
    'core/worldline-evaluation_report_facts.adb',
    'core/worldline-evaluation_report_facts.ads',
    'core/worldline-evaluation_report_wire.adb',
    'core/worldline-evaluation_report_wire.ads',
    'core/worldline-identities.ads',
    'core/worldline-receipts.adb',
    'core/worldline-receipts.ads',
    'core/worldline-recovery.adb',
    'core/worldline-recovery.ads',
    'core/worldline-recovery_c_api.adb',
    'core/worldline-recovery_c_api.ads',
    'core/worldline-reservation_lifecycle_c_api.adb',
    'core/worldline-reservation_lifecycle_c_api.ads',
    'core/worldline-resource_ledger_c_api.adb',
    'core/worldline-resource_ledger_c_api.ads',
    'core/worldline-resource_policy_c_api.adb',
    'core/worldline-resource_policy_c_api.ads',
    'core/worldline-resource_wire.adb',
    'core/worldline-resource_wire.ads',
    'core/worldline-resources.adb',
    'core/worldline-resources.ads',
    'core/worldline-resources_c_api.adb',
    'core/worldline-resources_c_api.ads',
    'core/worldline-transitions.adb',
    'core/worldline-transitions.ads',
    'core/worldline-world.adb',
    'core/worldline-world.ads',
    'core/worldline.ads',
})


def stray_sources(root: Path) -> list[str]:
    """Ada files under core/ that are absent from the fixed reviewed inventory."""
    found = {path.relative_to(root).as_posix() for path in (root / "core").rglob("*.ad[bs]")}
    return sorted(found - DECLARED_CORE_ADA_SOURCES)


def missing_sources(root: Path) -> list[str]:
    """Required core units cannot disappear when a fresh manifest is generated."""
    return sorted(path for path in DECLARED_CORE_ADA_SOURCES if not (root / path).is_file())


def contract_problems(root: Path) -> list[str]:
    try:
        problems = export_problems(root)
    except OSError as exc:
        return [f"pinned contract unreadable: core/worldline-c_api.ads: {exc}"]
    problems += [f"an Ada source outside the pinned set could be compiled into the core: {path}" for path in stray_sources(root)]
    problems += [f"a required reviewed Ada source is missing: {path}" for path in missing_sources(root)]
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


def proof_source_files(root: Path) -> list[str]:
    """Every file the proof sources, the contract pins and the coverage expectation read, as
    paths relative to the tree: what an install copies beside the library (OB-084)."""
    files = {path.relative_to(root).as_posix() for path in source_paths(root).values()}
    files |= {key.partition("#")[0] for key in CONTRACT_PINS}
    return sorted(files)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ----- the GNATprove summary, parsed as a whole and fail-closed (1.9.2, OB-085) ------------------

class SummaryError(ValueError):
    """A summary line or structure this parser does not recognize. Never skipped."""


_CATEGORIES = ("Data Dependencies", "Flow Dependencies", "Initialization", "Non-Aliasing", "Run-time Checks",
               "Assertions", "Functional Contracts", "LSP Verification", "Termination", "Concurrency")
_COLUMNS = ("total", "flow", "provers", "justified", "unproved")
_COL = r"\.|\d+(?: \([^()]*\))?"
_ROW = re.compile(rf"^(?P<label>[A-Za-z][A-Za-z -]*?)\s+(?P<total>{_COL})\s+(?P<flow>{_COL})\s+"
                  rf"(?P<provers>{_COL})\s+(?P<justified>{_COL})\s+(?P<unproved>{_COL})\s*$")
_HEADER = re.compile(r"^SPARK Analysis results\s+Total\s+Flow\s+Provers\s+Justified\s+Unproved\s*$")
_RULE = re.compile(r"^-{20,}\s*$")
_BANNER = re.compile(r"^={10,}\s*$")
_MAX_STEPS = re.compile(r"^max steps used for successful proof: \d+\s*$")
_NO_DIFFICULT = re.compile(r"^No check found with max time greater than \d+ seconds?\s*$")
_DIFFICULT = re.compile(r"^\S+:\d+:\d+: .+ proved in max \d+ seconds?\s*$")
_ANALYZED = re.compile(r"^Analyzed (\d+) units?\s*$")
_UNIT = re.compile(r"^in unit (\S+), (\d+) subprograms and packages out of (\d+) analyzed$")
_SUBPROGRAM = re.compile(
    r"^  (\S+) at (\S+) flow analyzed \(0 errors, \d+ checks, \d+ warnings and "
    r"0 pragma Assume statements\) and proved \((\d+) checks\)$")
_TITLES = {"Summary of SPARK analysis": "summary", "Most difficult proved checks": "difficult",
           "Detailed analysis report": "detailed"}


def _count(value: str) -> int:
    return 0 if value == "." else int(value.split(" ", 1)[0])


def parse_summary(text: str) -> dict[str, Any]:
    """Every line of a gnatprove.out summary must be recognized: the titled sections, the
    results table (each known category at most once, exactly one Total row, the categories
    summing to it column by column, and Total = Flow + Provers + Justified + Unproved), the
    difficult-checks list and the per-unit report (only fully proved subprograms). Anything
    else raises SummaryError."""
    lines = text.splitlines()
    section: str | None = None
    seen: dict[str, int] = {}
    header = 0
    categories: dict[str, dict[str, int]] = {}
    total: dict[str, int] | None = None
    analyzed_units: int | None = None
    units: dict[str, dict[str, int]] = {}
    subprograms: dict[str, dict[str, Any]] = {}
    listed: dict[str, int] = {}
    current_unit: str | None = None
    index = 0
    while index < len(lines):
        line = lines[index].rstrip("\r")
        if not line.strip():
            index += 1
            continue
        if _BANNER.match(line) and index + 2 < len(lines) and _BANNER.match(lines[index + 2]):
            title = lines[index + 1].strip()
            if title not in _TITLES:
                raise SummaryError(f"unknown section: {title!r}")
            section = _TITLES[title]
            seen[section] = seen.get(section, 0) + 1
            if seen[section] > 1:
                raise SummaryError(f"section repeated: {title!r}")
            current_unit = None
            index += 3
            continue
        if section is None:
            raise SummaryError(f"line outside every section: {line!r}")
        if section == "summary":
            if _RULE.match(line):
                pass
            elif _HEADER.match(line):
                header += 1
            elif _MAX_STEPS.match(line):
                pass
            else:
                row = _ROW.match(line)
                if row is None:
                    raise SummaryError(f"unrecognized results line: {line!r}")
                label = row.group("label").strip()
                counts = {column: _count(row.group(column)) for column in _COLUMNS}
                if label == "Total":
                    if total is not None:
                        raise SummaryError("more than one Total row")
                    total = counts
                elif label in _CATEGORIES:
                    if label in categories:
                        raise SummaryError(f"category repeated: {label}")
                    if total is not None:
                        raise SummaryError(f"category after the Total row: {label}")
                    categories[label] = counts
                else:
                    raise SummaryError(f"unknown results category: {label!r}")
        elif section == "difficult":
            if not (_NO_DIFFICULT.match(line) or _DIFFICULT.match(line)):
                raise SummaryError(f"unrecognized difficult-checks line: {line!r}")
        else:
            analyzed = _ANALYZED.match(line)
            unit = _UNIT.match(line)
            if analyzed is not None:
                if analyzed_units is not None or units:
                    raise SummaryError("the analyzed-units count is repeated or misplaced")
                analyzed_units = int(analyzed.group(1))
            elif unit is not None:
                current_unit = unit.group(1)
                if current_unit in units:
                    raise SummaryError(f"unit repeated: {current_unit}")
                units[current_unit] = {"analyzed": int(unit.group(2)), "available": int(unit.group(3))}
                listed[current_unit] = 0
            elif line.startswith("  ") and current_unit is not None:
                sub = _SUBPROGRAM.match(line)
                if sub is None:
                    raise SummaryError(f"unit {current_unit}: not a proved subprogram: {line.strip()}")
                name, where, checks = sub.groups()
                # Overloads share a name; the manifest keys coverage by name, last one kept (as
                # the gate always recorded it). Each is still counted against its unit.
                subprograms[name] = {"at": where, "checks": int(checks), "proved": True}
                listed[current_unit] += 1
            else:
                raise SummaryError(f"unrecognized report line: {line!r}")
        index += 1
    for required in ("summary", "detailed"):
        if required not in seen:
            raise SummaryError(f"the {required} section is missing")
    if header != 1:
        raise SummaryError(f"the results table has {header} header rows")
    if total is None:
        raise SummaryError("the Total row is missing")
    for column in _COLUMNS:
        if sum(counts[column] for counts in categories.values()) != total[column]:
            raise SummaryError(f"the categories do not sum to the Total row in column {column}")
    if total["total"] != total["flow"] + total["provers"] + total["justified"] + total["unproved"]:
        raise SummaryError("the Total row's columns do not add up to its total")
    if analyzed_units is None or analyzed_units != len(units):
        raise SummaryError(f"the report lists {len(units)} units but says {analyzed_units} were analyzed")
    for unit_name, counts in units.items():
        if listed[unit_name] != counts["analyzed"]:
            raise SummaryError(f"unit {unit_name}: {counts['analyzed']} analyzed but {listed[unit_name]} listed as proved")
    return {**total, "categories": categories, "units": units, "subprograms": subprograms}


# ----- the manifest checks --------------------------------------------------------------------

CHECK_NAMES = ("manifest", "contract-pins", "zero-exceptions", "floor", "summary-digest-recorded", "coverage",
               "source-hashes", "library-hash", "summary")


def manifest_findings(manifest: Any, root: Path, *, library: Path | None = None, library_sha256: str | None = None,
                      summary: bytes | None = None, require_summary: bool = False) -> list[tuple[str, str]]:
    """Every check the gate applies to a manifest against the proof sources under `root`, as
    (check name, problem) in order; empty when all pass. `library` (or its already computed
    digest) is compared with the recorded library hash; `summary`, when given or required, is
    the gnatprove.out the manifest must have been written from."""
    if not isinstance(manifest, Mapping):
        return [("manifest", "the proof manifest is not a JSON object")]
    findings: list[tuple[str, str]] = [("contract-pins", text) for text in contract_problems(root)]
    proof = manifest.get("proof")
    if not isinstance(proof, Mapping):
        return findings + [("manifest", "the proof manifest records no proof counts")]
    if any(type(proof.get(key)) is not int or proof.get(key) != 0 for key in ("justified", "unproved", "pragmaAssume")):
        findings.append(("zero-exceptions", "proof manifest does not record a zero-exception proof"))
    total = proof.get("total")
    if (type(total) is not int or type(proof.get("minimumChecks")) is not int
            or proof.get("minimumChecks") != MINIMUM_CHECKS or total < MINIMUM_CHECKS):
        findings.append(("floor", f"proof manifest records {total!r} checks against a floor of {MINIMUM_CHECKS}"))
    recorded_summary = proof.get("summarySha256")
    if not isinstance(recorded_summary, str) or not re.fullmatch(r"[0-9a-f]{64}", recorded_summary):
        findings.append(("summary-digest-recorded", "proof manifest records no summarySha256"))
    coverage = manifest.get("coverage")
    if not isinstance(coverage, Mapping):
        return findings + [("coverage", "proof manifest records no per-subprogram coverage")]
    subprograms = coverage.get("subprograms")
    units = coverage.get("units")
    boundary = coverage.get("unanalyzedBoundary")
    boundary_valid = (isinstance(boundary, list) and all(isinstance(name, str) for name in boundary)
                      and len(boundary) == len(set(boundary)) and set(boundary) == UNANALYZED_BOUNDARY)
    if coverage.get("requiredProved") != REQUIRED_PROVED or not boundary_valid:
        findings.append(("coverage", "proof manifest does not claim the pinned required subprograms and boundary"))
    if not isinstance(subprograms, Mapping) or not subprograms or not isinstance(units, Mapping):
        return findings + [("coverage", "proof manifest coverage is empty")]
    if any(not (isinstance(value, Mapping) and value.get("proved") is True
                and type(value.get("checks")) is int and value["checks"] >= 0)
           for value in subprograms.values()):
        findings.append(("coverage", "proof manifest records an unproved subprogram"))
    unproved_required = [name for name in REQUIRED_PROVED if name not in subprograms]
    if unproved_required:
        findings.append(("coverage", "required subprograms not proved: " + ", ".join(unproved_required)))
    missing_units = sorted(expected_units(root) - set(units))
    if missing_units:
        findings.append(("coverage", "proof manifest does not cover units: " + ", ".join(missing_units)))
    for unit, counts in units.items():
        if (not isinstance(counts, Mapping) or type(counts.get("analyzed")) is not int
                or type(counts.get("available")) is not int or counts["analyzed"] < 0
                or counts.get("analyzed") != counts.get("available") or (
                unit not in UNANALYZED_BOUNDARY and not counts.get("available"))):
            findings.append(("coverage", f"proof manifest records an unanalyzed unit: {unit}"))
            break
    paths = source_paths(root)
    recorded = manifest.get("sourceHashes")
    if not isinstance(recorded, Mapping) or set(recorded) != set(paths):
        findings.append(("source-hashes", "proof source set changed after proof"))
    else:
        for key, path in paths.items():
            if not path.is_file() or recorded[key] != digest(path):
                findings.append(("source-hashes", f"proof source changed after proof: {key}"))
                break
    if library is not None or library_sha256 is not None:
        recorded_library = (manifest.get("library") or {}).get("sha256") if isinstance(manifest.get("library"), Mapping) else None
        actual = library_sha256
        if actual is None and library is not None:
            actual = digest(library) if library.is_file() else None
        if actual is None or recorded_library != actual:
            findings.append(("library-hash", "proved library changed after proof"))
    if summary is None:
        if require_summary:
            findings.append(("summary", "the proof summary is missing, so the recorded counts cannot be re-derived"))
    else:
        findings += [("summary", text) for text in summary_problems(manifest, summary)]
    return findings


def manifest_problems(manifest: Any, root: Path, **options: Any) -> list[str]:
    return [text for _name, text in manifest_findings(manifest, root, **options)]


def summary_problems(manifest: Mapping[str, Any], summary: bytes) -> list[str]:
    """The summary the manifest names: its digest, and the counts and coverage re-derived from
    it, must equal what the manifest records (OB-085)."""
    proof = manifest.get("proof") if isinstance(manifest.get("proof"), Mapping) else {}
    coverage = manifest.get("coverage") if isinstance(manifest.get("coverage"), Mapping) else {}
    problems: list[str] = []
    if hashlib.sha256(summary).hexdigest() != proof.get("summarySha256"):
        problems.append("the proof summary's digest differs from the manifest's summarySha256")
    try:
        parsed = parse_summary(summary.decode("utf-8"))
    except UnicodeDecodeError as exc:
        return problems + [f"the proof summary is not UTF-8: {exc}"]
    except SummaryError as exc:
        return problems + [f"the proof summary is not recognized: {exc}"]
    for key in ("total", "justified", "unproved"):
        if parsed[key] != proof.get(key):
            problems.append(f"the proof summary records {key} {parsed[key]}, the manifest {proof.get(key)!r}")
    if parsed["units"] != coverage.get("units") or parsed["subprograms"] != coverage.get("subprograms"):
        problems.append("the proof summary's per-unit coverage differs from the manifest's")
    return problems


def load_manifest(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))
