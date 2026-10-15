#!/usr/bin/env python3
"""Exclusive source snapshot/identity formation; never imports candidate code.

This is not a test, compiler, prover or semantic-equivalence check. It reads
only the listed application sources and the configured toolchain/library source
directories, then writes only this fresh assigned scratch directory.
"""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
PROPOSAL = OUT.parent / "shared-json-parser-candidate-v1"
CURSOR = OUT.parent / "decoder-cursor-candidate-v1"
D56 = ROOT / "records/phase1-blockers/resume-20261015-v1/decoder-cursor-v2"
PRIVATE = ROOT / "scratch/old-analysis/private-sparklib-experiment"
RUNTIME = Path("/home/sicarii/opt/gnat/gnat-aarch64-linux-16.1.0-1/lib/gcc/aarch64-linux-gnu/16.1.0/adainclude")
EXPECTED_PROPOSAL_RECEIPT = "4a78d4fd3fe9233bfbeb71d6a85e4ecab7dc97d7452a38a6d60b9f8e8dc449df"
EXPECTED_CURSOR_RECEIPT = "ae98d9b6951f97634b255fb149aa931fc8dc411974071c477e4d6b8338efd4ac"
EXPECTED_ORIGINAL_RESOURCE = "127aea76bb983d83506beb20954ab83264f7b8185b2a2e74ecca8684ce47635d"
EXPECTED_D56_RESOURCE = "23e67ed2f9fbb65741e5ddfab10fbde101a719feeb649a2bf1c9ae8052421a1a"
EXPECTED_SOURCE_EPOCH = "4ff3bf48b4323c051ffa8cf04ba4787982111f6d"


def digest(data):
    return sha256(data).hexdigest()


def identified(path):
    data = path.read_bytes()
    return {"path": str(path), "size_bytes": len(data), "sha256": digest(data)}


def exclusive_json(path, obj):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(obj, stream, indent=2, sort_keys=True)
        stream.write("\n")


def check_receipt(path, expected):
    data = path.read_bytes()
    if digest(data) != expected:
        raise RuntimeError("immutable receipt mismatch: " + str(path))
    return json.loads(data)


def context_imports(data):
    # Deliberately a source inventory, not an Ada parser. Limit to the actual
    # context prefix, excluding generic formal 'with function' declarations.
    text = data.decode("utf-8")
    text = re.sub(r'"(?:[^"\n]|"")*"|--[^\n]*', lambda m: " " * len(m[0]), text)
    top = re.search(r"(?im)^(?:generic\b|(?:private\s+)?package\b|procedure\b|function\b)", text)
    prefix = text[:top.start()] if top else text
    result = []
    for match in re.finditer(r"(?im)^\s*(?:(?:limited|private)\s+)*with\s+([^;]+);", prefix):
        for unit in match[1].split(","):
            unit = unit.strip().lower()
            if not re.fullmatch(r"[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)*", unit):
                raise RuntimeError("context inventory cannot parse: " + unit)
            result.append(unit)
    return sorted(set(result))


def source_unit(path):
    return path.stem.replace("-", ".").lower()


proposal_receipt = check_receipt(PROPOSAL / "preparation-receipt.json", EXPECTED_PROPOSAL_RECEIPT)
cursor_receipt = check_receipt(CURSOR / "preparation-receipt.json", EXPECTED_CURSOR_RECEIPT)
proposal_pins = {row["path"]: row["sha256"] for row in proposal_receipt["artifacts"]}
cursor_dependency_pins = {row["snapshot"]: row["sha256"] for row in cursor_receipt["source_snapshots"]}
head_before = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
if head_before != EXPECTED_SOURCE_EPOCH:
    raise RuntimeError("coordinator-specified current source epoch changed before formation")
snapshots = []


def snapshot(source, relative_destination, category, expected=None):
    data = source.read_bytes()
    before = digest(data)
    if expected is not None and before != expected:
        raise RuntimeError("source identity mismatch: " + str(source))
    epoch_match = None
    if source.is_relative_to(ROOT / "core"):
        committed = subprocess.check_output(["git", "-C", str(ROOT), "show",
                                             EXPECTED_SOURCE_EPOCH + ":" + str(source.relative_to(ROOT))])
        epoch_match = committed == data
        if not epoch_match:
            raise RuntimeError("current core bytes differ from specified source epoch: " + str(source))
    destination = OUT / relative_destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as stream:
        stream.write(data)
    if digest(source.read_bytes()) != before:
        raise RuntimeError("source changed during snapshot: " + str(source))
    snapshots.append({"unit": source_unit(source), "source": str(source),
                      "destination": relative_destination, "category": category,
                      "size_bytes": len(data), "sha256": before,
                      "explicit_context_units": context_imports(data),
                      "equals_specified_current_commit": epoch_match,
                      "source_stable_during_copy": True})


for name in ["worldline-json_syntax_types.ads", "worldline-generic_json_syntax.ads",
             "worldline-generic_json_syntax.adb", "worldline-producer_values.ads",
             "worldline-producer_values.adb", "worldline-raw_json_syntax.ads",
             "worldline-raw_json_syntax.adb"]:
    snapshot(PROPOSAL / name, "src/" + name, "immutable_unapplied_shared_parser", proposal_pins[name])
for suffix in ["ads", "adb"]:
    name = "worldline-json_source_cursor." + suffix
    snapshot(PROPOSAL / "cursor-dependency" / name, "src/" + name,
             "immutable_cursor_dependency", proposal_pins["cursor-dependency/" + name])

# Explicit coordinator-directed current epoch; unchanged units must still match
# their historical candidate pins. This is not an unnoticed dependency repin.
for name in ["worldline.ads", "attest.ads", "attest-sha256.ads", "attest-sha256.adb",
             "resource_quantities.ads", "worldline-archive_text.ads", "worldline-archive_text.adb"]:
    source_dir = ROOT / "core/attest" if name.startswith("attest") else ROOT / "core"
    snapshot(source_dir / name, "src/" + name, "current_core_dependency_matches_original",
             cursor_dependency_pins["dependencies/" + name])
snapshot(ROOT / "core/resource_quantities.adb", "resource-current-D56/resource_quantities.adb",
         "default_current_core_D56_body", EXPECTED_D56_RESOURCE)
snapshot(CURSOR / "dependencies/resource_quantities.adb", "resource-historical-original/resource_quantities.adb",
         "optional_historical_comparison_only_not_proposed_for_execution", EXPECTED_ORIGINAL_RESOURCE)

# Actual transitive numeric/render bodies. No executable substitutes or stubs.
for stem in ["evaluation_pending", "evaluation_epoch", "exact_decimal", "decimal_binary64",
             "worldline-producer_render"]:
    for suffix in ["ads", "adb"]:
        name = stem + "." + suffix
        snapshot(ROOT / "core" / name, "src/" + name, "unchanged_core_dependency")
snapshot(ROOT / "core/worldline-producer_unicode.ads", "src/worldline-producer_unicode.ads",
         "unchanged_core_dependency_bodyless_expression_unit")

app_units = {row["unit"] for row in snapshots}
app_imports = {unit for row in snapshots for unit in row["explicit_context_units"]}
for unit in app_units:
    while "." in unit:
        unit = unit.rsplit(".", 1)[0]
        app_imports.add(unit)
external_imports = sorted(app_imports - app_units)
if external_imports != ["interfaces", "spark.big_integers"]:
    raise RuntimeError("unexpected application dependency frontier: " + repr(external_imports))

# An inclusive identity inventory of the configured external source universes.
# This deliberately avoids guessing which runtime helper the binder selects.
# It is NOT a claim that GNATprove analyzes externally-built runtime bodies.
runtime_inventory = [identified(path) for path in sorted(RUNTIME.iterdir())
                     if path.is_file() and path.suffix in {".ads", ".adb"}]
spark_root = PRIVATE / "include/spark"
spark_inventory = [identified(path) for directory in [spark_root, spark_root / "full"]
                   for path in sorted(directory.iterdir())
                   if path.is_file() and path.suffix in {".ads", ".adb"}]
external_identity = {
    "evidence_class": "MEASURED",
    "meaning": "Raw source-file inventory, not compiler-selected or proved closure",
    "runtime_source_root": str(RUNTIME), "runtime_source_universe": runtime_inventory,
    "private_full_sparklib_source_universe": spark_inventory,
    "project_files": [identified(PRIVATE / "lib/gnat" / name)
                      for name in ["sparklib.gpr", "sparklib_common.gpr"]],
    "prebuilt_archive": identified(PRIVATE / "lib/gnat/sparklib_lib/libsparklib.a"),
    "toolchain_environment": identified(Path("/home/sicarii/opt/gnat/env.sh")),
    "explicit_boundary": [
        "SPARK.Big_Integers is the existing full-library rename of Ada.Numerics.Big_Numbers.Big_Integers",
        "Existing private sparklib.gpr marks that library externally built for gnatprove",
        "Actual GNAT runtime specs/bodies are inventoried, not replaced, copied into project or represented by new stubs",
        "No compiler, binder, linker or prover has resolved this project; selected runtime closure is UNVERIFIED",
        "Implicit compiler support, C/GMP/system runtime object closure is not established by Ada-source inventory"
    ]}
exclusive_json(OUT / "external-source-identities.json", external_identity)

manifest = {
    "evidence_class": "MEASURED",
    "scope": "Source-inventoried complete explicit application context/body closure for this candidate",
    "compiler_resolved_closure": "UNVERIFIED",
    "application_sources": snapshots,
    "bodyless_application_units": ["worldline", "attest", "worldline.json_syntax_types", "worldline.producer_unicode"],
    "external_context_frontier": external_imports,
    "external_identity_manifest": "external-source-identities.json",
    "main_sources": [identified(OUT / "string_parser_controls.adb"), identified(OUT / "wide_parser_controls.adb")],
    "main_contexts": {name: context_imports((OUT / name).read_bytes())
                      for name in ["string_parser_controls.adb", "wide_parser_controls.adb"]},
    "explicit_current_source_epoch": EXPECTED_SOURCE_EPOCH,
    "default_scenario": "current_D56",
    "default_resource_body": {"sha256": EXPECTED_D56_RESOURCE,
                              "status_at_preparation": "Retained D56 cursor-context proof; this shared-parser closure UNVERIFIED",
                              "formation_source": identified(D56 / "v2-formation.json")},
    "optional_scenario": {"name": "historical_original", "enabled_by_default": False,
                          "status_at_preparation": "Historical comparison only; no unchanged known-failure run proposed",
                          "only_selected_source_difference": "resource_quantities.adb",
                          "expected_sha256": EXPECTED_ORIGINAL_RESOURCE},
    "unchanged_public_spec": {"source": str(PROPOSAL / "worldline-producer_values.ads"),
                              "sha256": proposal_pins["worldline-producer_values.ads"]},
    "limitations": [
        "No full WORLDLINE scope claim; original complete projects remain mandatory",
        "Textual context inventory is not Ada legality or compiler dependency resolution",
        "Generic formal contracts, discriminated-result uses and actual interface compatibility have not compiled",
        "Spec-only application units are identified from inspected source, not a compiler body-requirement check",
        "Resource_Quantities and all numeric/render application bodies are in the project, not excluded",
        "Per-fixture assertions are not universal semantic equivalence or full-value authority proof",
        "Weak existing public contracts may require truthful proof work to establish fixture assertions; none were changed"
    ]}
exclusive_json(OUT / "dependency-manifest.json", manifest)
head = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
if head != head_before:
    raise RuntimeError("source epoch changed during formation; preserve partial snapshots for review")
artifacts = [{"path": str(path.relative_to(OUT)), "sha256": digest(path.read_bytes()),
              "size_bytes": path.stat().st_size}
             for path in sorted(OUT.rglob("*")) if path.is_file()]
receipt = {
    "schema": "worldline-shared-parser-controls-source-only-v1",
    "formed_utc": datetime.now(timezone.utc).isoformat(), "evidence_class": "MEASURED",
    "command": "python3 -B scratch/acquisition2/resume-20261015-v1/shared-json-parser-controls-v1/prepare_receipt.py",
    "observed_head": head, "head_is_freeze": False,
    "explicit_current_source_epoch": EXPECTED_SOURCE_EPOCH,
    "engineering_status": "UNAPPLIED / UNVERIFIED / NOT COMPILED / NOT TESTED / NOT PROVED",
    "immutable_proposal_receipt": {"path": str(PROPOSAL / "preparation-receipt.json"),
                                    "sha256": EXPECTED_PROPOSAL_RECEIPT},
    "immutable_cursor_receipt": {"path": str(CURSOR / "preparation-receipt.json"),
                                  "sha256": EXPECTED_CURSOR_RECEIPT},
    "artifacts": artifacts, "candidate_imports_or_payloads_executed": [],
    "non_claims": ["Formation is source copying/hashing only", "No original tests or product edited",
                   "No new heavy job or isolated positive acquisition diagnostic",
                   "No full source equivalence, proof closure, acquisition classification or acceptance claimed"]}
exclusive_json(OUT / "preparation-receipt.json", receipt)
print(json.dumps({"receipt": str(OUT / "preparation-receipt.json"),
                  "sha256": digest((OUT / "preparation-receipt.json").read_bytes()),
                  "status": receipt["engineering_status"]}, sort_keys=True))
