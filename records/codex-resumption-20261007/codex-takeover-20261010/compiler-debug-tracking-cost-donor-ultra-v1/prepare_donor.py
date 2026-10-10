#!/usr/bin/env python3
"""Data-only one-GPR donor. No subprocess, tool invocation, target or gate."""
from pathlib import Path
import hashlib
import json
import difflib

T = Path(__file__).resolve().parent
D = T / "compiler-debug-tracking-cost-donor-ultra-v1"
S = T / "integrated-candidate-v7/source"
name = "core/worldline_core_sources.gpr"
before_path = S / name
old = '"-O2", "-g", "-fPIC");'
new = '"-O2", "-g", "-fPIC", "-fno-var-tracking-assignments");'
before = before_path.read_bytes()
assert before.count(old.encode()) == 1
after = before.replace(old.encode(), new.encode())
assert after.replace(new.encode(), old.encode()) == before
assert not D.exists(), "Never overwrite a prior donor or freeze"
D.mkdir()

def pin(p):
    b = p.read_bytes()
    return {"path": str(p.resolve()), "sha256": hashlib.sha256(b).hexdigest(),
            "bytes": len(b), "mode": p.stat().st_mode & 0o777}

def write(rel, b):
    p = D / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    assert not p.exists()
    p.write_bytes(b if isinstance(b, bytes) else b.encode())
    p.chmod(0o644)
    return pin(p)

def doc(rel, value):
    return write(rel, json.dumps(value, indent=2, sort_keys=True) + "\n")

source_pin = write("source/" + name, after)
preimage_pin = write("preimages/" + name, before)
author = write("author-model-provenance.json",
               (T / "proof_ultra-actual-launch-provenance.json").read_bytes())
write("prepare_donor.py", Path(__file__).read_bytes())
write("repair.patch", "".join(difflib.unified_diff(
    before.decode().splitlines(True), after.decode().splitlines(True),
    fromfile="a/" + name, tofile="b/" + name)))
write("inverse.patch", "".join(difflib.unified_diff(
    after.decode().splitlines(True), before.decode().splitlines(True),
    fromfile="a/" + name, tofile="b/" + name)))
write("source-only-comparison.json",
      (T / "compiler-cost-source-only-comparison-ultra-v1.json").read_bytes())
write("passive-compiler-expansion-observation.json",
      (T / "formal-v8-passive-compiler-expansion-observation-v1.json").read_bytes())
E = T / "formal-frame-successor-v8-draft/evidence/full-strict-formal-diagnostic-v1"
actual = {}
for n in ["result.json", "child-wait.json", "child.stdout", "child.stderr"]:
    p = E / n
    if p.exists():
        copied = write("actual-d8-observations/" + n, p.read_bytes())
        actual[n] = {"original_pin_at_copy": pin(p), "retained_copy": copied}
result = json.loads((E / "result.json").read_text())
assert result["child_wait"]["timeout"] is True
assert result["inputs_unchanged"] is True
log = T / "formal-frame-successor-v8-draft/source/obj/core/gnatprove/data_representation_generation.log"
actual["data_representation_generation.log"] = {
    "original_pin_at_copy": pin(log),
    "retained_copy": write("actual-d8-observations/data_representation_generation.log", log.read_bytes())}
doc("references.json", {
    "schema": "worldline-source-only-primary-reference-description-v1",
    "primary_url": "https://gcc.gnu.org/onlinedocs/gcc-16.1.0/gcc/Debugging-Options.html",
    "revision": "GCC 16.1.0",
    "description": "Assignment tracking annotates user-variable assignments during optimization to improve debugging location information. This proposal retains -g and other compiler/check flags while omitting those assignment annotations.",
    "evidence_limit": "Documentation and actual fallback notes support a mechanism hypothesis; neither establishes deadline performance or proof correctness."})
identity = doc("SOURCE-IDENTITY.json", {
    "schema": "worldline-source-only-donor-identity-v1",
    "author": "CodexCompilerDebugTrackingCostUltraAuthor",
    "author_agent": "/root/proof_ultra",
    "author_model": "openai-codex/gpt-6.1-sol:ultra",
    "actual_author_launch": author,
    "source_selection": pin(T / "integrated-candidate-v7/source-selection.json"),
    "current_source_opinion": pin(T / "frame-review-draft/integrated-v7-independent-source-review.json"),
    "source_inputs": {name: pin(before_path)},
    "permitted_names": [name],
    "source_only": True, "target_execution": False, "phase_acceptance": False})
delta = doc("source-delta.json", {
    "schema": "worldline-exact-source-delta-v1",
    "changes": [{"name": name, "before": pin(before_path), "after": source_pin}],
    "source_only": True, "target_execution": False, "phase_acceptance": False})
transform = doc("exact-transformations.json", {
    "schema": "worldline-compiler-debug-assignment-tracking-delta-v1",
    "sole_permitted_difference": "Append one nonsemantic compiler debug-assignment-tracking option to the original Common Ada switch list.",
    "before": old, "after": new, "forward_inverse_exact": True,
    "preimage_copy": preimage_pin, "actual_d8_observations": actual,
    "actual_child_wait": result["child_wait"],
    "retained_guarantees": [
        "Original -gnat2022/-gnatwa/-gnatVa/-gnatf/-O2/-g/-fPIC switch prefix remains byte-identical and ordered.",
        "Checks mode still adds -gnata; no assertion, ghost check, runtime check, warning, validity check or optimization level is disabled.",
        "All Ada source, expressions, accepted domains, contracts, proof enrollment and external ABI declarations are unchanged.",
        "Original source directories/exclusions, output topology, C switches, proof switches and direct full strict -U command are byte-identical.",
        "Original child/scope/Main deadlines, memory/swap/core caps, original fixtures/controls/rosters and full same-final-source acceptance obligations remain mandatory."],
    "material_limitations": [
        "Detailed DWARF variable-assignment location history can be reduced; -g continues to request debug symbols/line/type data.",
        "This cannot establish proof correctness or resolution of the deadline failure; actual full strict proof and complete native/runtime actions remain OPEN.",
        "No target executed with this postimage; exact compiler/source/full-frame review and real original-bound validation remain required."],
    "source_only": True, "target_execution": False, "phase_acceptance": False})
write("CHANGE.md", "Append only `-fno-var-tracking-assignments` to the existing Ada Common compiler switches. The actual D8 compiler recorded assignment-tracking size-limit retries and its child later timed out after reaching flow/proof. This proposal avoids that debug bookkeeping; no effectiveness claim is made. All original compiler/check switches, complete Ada sources/contracts/domains, proof command/scope/deadlines, ABI and runtime obligations remain fixed. Detailed variable-assignment debugger location history may be reduced. Full build/proof/runtime success is still OPEN.\n")
freeze = doc("author-freeze.json", {
    "schema": "worldline-source-only-donor-author-freeze-v1",
    "author_agent": "/root/proof_ultra",
    "author_model": "openai-codex/gpt-6.1-sol:ultra",
    "files": {str(p.relative_to(D)): pin(p) for p in sorted(D.rglob("*")) if p.is_file()},
    "source_only": True, "target_execution": False, "phase_acceptance": False})
packet = doc("source-author-packet-v1.json", {
    "schema": "worldline-source-only-donor-author-packet-v1",
    "actual_author_launch": author, "author_freeze": freeze,
    "source_identity": identity, "source_delta": delta,
    "exact_transformations": transform, "permitted_names": [name],
    "requested_disposition": "QUALIFIED_EXACT_COMPILER_DEBUG_ASSIGNMENT_TRACKING_COST_REPAIR_SOURCE_ONLY",
    "review_destination": str(D / "independent-source-review.json"),
    "source_only": True, "target_execution": False, "phase_acceptance": False})
assert before_path.read_bytes() == before
print(json.dumps({"packet": packet, "freeze": freeze, "source": source_pin,
                  "original_preimage": pin(before_path),
                  "source_only": True, "target_execution": False,
                  "full_guarantee": "OPEN"}, indent=2))
