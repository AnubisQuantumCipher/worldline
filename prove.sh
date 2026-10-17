#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
cd "$ROOT"
# shellcheck disable=SC1090
# The reference machine keeps GNAT FSF under ~/opt/gnat; elsewhere (CI, packaging) the
# toolchain is already on PATH.
if [[ -f "${GNAT_ENV:-$HOME/opt/gnat/env.sh}" ]]; then source "${GNAT_ENV:-$HOME/opt/gnat/env.sh}"; fi

PRIVATE_SPARKLIB="$ROOT/scratch/coordinator/private-sparklib/lib/gnat"
if [[ ! -f "$PRIVATE_SPARKLIB/sparklib.gpr" ]]; then
  echo "prove: private SPARKlib project missing: $PRIVATE_SPARKLIB/sparklib.gpr" >&2
  exit 2
fi
# env.sh replaces GPR_PROJECT_PATH. Restore the reviewed private library after it,
# and do not rebuild that archive as part of the aggregate.
export GPR_PROJECT_PATH="$PRIVATE_SPARKLIB${GPR_PROJECT_PATH:+:$GPR_PROJECT_PATH}"
export WORLDLINE_PRIVATE_SPARKLIB_PREBUILT=True

# Bind both commands to the reviewed checks build and installed private library,
# rather than inheriting scenario values from an operator's environment.
SCENARIOS=("-XWORLDLINE_BUILD=checks" "-XWORLDLINE_PRIVATE_SPARKLIB_PREBUILT=True" "-XSPARKLIB_MODE=full" "-XSPARKLIB_BUILD=Production" "-XSPARKLIB_LIBRARY_TYPE=static" "-XSPARKLIB_INSTALLED=True")
# This gate consumes externally built SPARKlib. The complete F2 campaign also
# needs the separate imported-source proof driver; -U cannot override that boundary.

OUT="obj/core-library/gnatprove/gnatprove.out"
LIB="lib/libworldline_core.so"
OPTIONS=("-P" "core/worldline_core.gpr" "-U" "--mode=all" "--level=3" "--report=all" "--checks-as-errors=on" "--proof-warnings=on" "--warnings=error" "--memlimit=1024" "--timeout=60" "-j2")

echo "== build libworldline_core.so =="
gprbuild -p -q -j2 -P worldline.gpr "${SCENARIOS[@]}"

echo "== prove every Worldline core unit =="
# Remove any previous summary first: without this, a gnatprove run that fails or aborts can
# leave the PREVIOUS run's summary in place to be read as this run's result, while the manifest
# is regenerated over today's (unproved) sources. Also stop discarding gnatprove's exit status.
rm -f "$OUT"
if ! gnatprove "${OPTIONS[@]}" "${SCENARIOS[@]}"; then
  echo "prove: gnatprove exited non-zero" >&2
  exit 2
fi
[[ -f "$OUT" ]] || { echo "prove: gnatprove produced no summary"; exit 2; }
[[ -f "$LIB" ]] || { echo "prove: shared library is missing"; exit 2; }

python3 - "$ROOT" "$OUT" "$LIB" "${OPTIONS[@]:2}" "${SCENARIOS[@]}" <<'PY'
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

root = Path(sys.argv[1]).resolve()
# The floor, the required subprograms and the declared boundary are pinned in the verifier, so
# the gate that writes the manifest and the check that reads it cannot disagree.
sys.dont_write_bytecode = True
sys.path.insert(0, str(root))
from verify_proof_manifest import MINIMUM_CHECKS, REQUIRED_PROVED, UNANALYZED_BOUNDARY, SummaryError, contract_problems, parse_summary, source_paths  # noqa: E402
from worldline.proof_manifest import ada_identifier_key, ada_tokens, source_profile_problems
# The pinned contracts are checked before the manifest is written, so the gate never prints
# PASSED for a tree whose contracts changed (review of 0ee1112).
if contract_problems(root):
    raise SystemExit("PROOF GATE FAILED: " + "; ".join(contract_problems(root)))
out_path = (root / sys.argv[2]).resolve()
lib_path = (root / sys.argv[3]).resolve()
summary = out_path.read_text(encoding="utf-8")

# 1.9.2 (OB-085): the whole summary is parsed fail-closed -- every section and line recognized,
# exactly one Total row, the categories summing to it column by column -- by the parser the
# manifest verifier and the runtime share. A line it has never seen refuses the gate.
try:
    parsed = parse_summary(summary)
except SummaryError as exc:
    raise SystemExit(f"PROOF GATE FAILED: the gnatprove summary is not recognized: {exc}")
total = parsed["total"]
justified = parsed["justified"]
unproved = parsed["unproved"]

sources = source_paths(root)

missing = [key for key, path in sources.items() if not path.is_file()]
if missing:
    raise SystemExit("prove: proof source missing: " + ", ".join(missing))
profile_problems = source_profile_problems(root, sources.values())
if profile_problems:
    raise SystemExit("PROOF GATE FAILED: " + "; ".join(profile_problems))

# Screen Ada syntax, not comments or literal payloads. Only Inline_For_Proof is
# admitted: GNATprove checks its regular-function equivalence against the body;
# expression functions use their definition directly. It does not justify a
# check or skip a body. Full coverage and the zero-exception gates below still
# apply. Every other GNATprove annotation, including unknown future tags, refuses.
# Policy: SPARK User's Guide, "Annotation for Inlining Functions for Proof":
# https://docs.adacore.com/spark2014-docs/html/ug/en/appendix/additional_annotate_pragmas.html#annotation-for-inlining-functions-for-proof
_OPERATOR = re.compile(r'"(?:\*\*|<=|>=|/=|[+\-*/=&<>]|and|or|xor|mod|rem|abs|not)"', re.I)


def spelling(token):
    kind, value = token
    if kind == "identifier":
        return ada_identifier_key(value)
    return value if kind == "symbol" else "<literal>"


def code_only(path):
    """Use the same encoding and token boundaries as the contract normalizer."""
    try:
        return [token for token in ada_tokens(path.read_bytes(), canonical_pragmas=True)
                if token[0] != "layout"]
    except (UnicodeError, ValueError) as exc:
        raise SystemExit(f"PROOF GATE FAILED: {path}: {exc}") from exc


def entity_name(tokens):
    """A selected Ada name, optionally ending in a quoted operator."""
    if not tokens or len(tokens) % 2 == 0:
        return False
    for index, token in enumerate(tokens):
        kind, value = token
        if index % 2:
            if token != ("symbol", "."):
                return False
        elif kind != "identifier":
            operator = '"' + value[1:-1] + '"'
            if index != len(tokens) - 1 or kind != "string" or not _OPERATOR.fullmatch(operator):
                return False
    return True


def unsupported_annotations(tokens, *, allow_inline):
    """Validate complete token lists, never a tag prefix or a name substring."""
    words = [spelling(token) for token in tokens]
    problems = []
    for index, word in enumerate(words):
        if words[index:index + 2] == ["PRAGMA", "ANNOTATE"]:
            pragma = True
            start = index + 2
        elif word == "ANNOTATE" and words[index + 1:index + 3] == ["=", ">"]:
            pragma = False
            start = index + 3
        else:
            continue
        if words[start:start + 1] != ["("]:
            problems.append("malformed Annotate arguments")
            continue
        depth = 0
        for end in range(start, len(words)):
            if words[end] == "(":
                depth += 1
            elif words[end] == ")":
                depth -= 1
                if depth == 0:
                    break
        else:
            problems.append("unterminated Annotate arguments")
            continue
        arguments = words[start:end + 1]
        if "GNATPROVE" not in arguments:
            continue
        if pragma:
            supported = (
                arguments[:8] ==
                ["(", "GNATPROVE", ",", "INLINE_FOR_PROOF", ",", "ENTITY", "=", ">"]
                and arguments[-1:] == [")"]
                and entity_name(tokens[start + 8:end])
                and words[end + 1:end + 2] == [";"])
        else:
            supported = (
                arguments == ["(", "GNATPROVE", ",", "INLINE_FOR_PROOF", ")"]
                and words[end + 1:end + 2] in ([","], [";"], ["IS"]))
        if not allow_inline or not supported:
            original = " ".join(value for _, value in tokens[start:end + 1])
            problems.append("unsupported GNATprove annotation: " + original)
    return problems


code = {key: code_only(path) for key, path in sources.items()}
spellings = {key: [spelling(token) for token in tokens] for key, tokens in code.items()}
assumes = sum(
    words[index:index + 2] == ["PRAGMA", "ASSUME"]
    for words in spellings.values() for index in range(len(words)))
# Only the exact core spec/body paths for the contract's declared unit may
# leave SPARK. Neither another *_c_api unit nor a same-named nested source is
# that boundary. Do not admit proof annotations on its unanalyzed implementation.
boundary_sources = {f"core/{unit}{suffix}" for unit in UNANALYZED_BOUNDARY for suffix in (".ads", ".adb")}
annotation_problems = [
    f"{key}: {problem}"
    for key, text in code.items()
    for problem in unsupported_annotations(text, allow_inline=key not in boundary_sources)
]
spark_off = sorted(
    key for key, words in spellings.items()
    if key not in boundary_sources and any(
        word == "SPARK_MODE" and
        (words[index + 1:index + 4] == ["=", ">", "OFF"] or
         words[index + 1:index + 3] == ["(", "OFF"])
        for index, word in enumerate(words))
)
print(f"checks total   {total}")
print(f"justified      {justified}")
print(f"unproved       {unproved}")
print(f"pragma Assume  {assumes}")
print(f"forbidden annotations {len(annotation_problems)}")
if unproved or justified or assumes:
    raise SystemExit("PROOF GATE FAILED")
if annotation_problems:
    raise SystemExit("PROOF GATE FAILED: " + "; ".join(annotation_problems))
if spark_off:
    raise SystemExit("PROOF GATE FAILED: SPARK_Mode => Off outside the declared boundary: "
                     + ", ".join(spark_off))
# A floor is what makes "all checks proved" mean anything: with none, a run that analyzed
# nothing (every body excluded from SPARK, or a summary of all dots) reports
# "0 checks, all proved, nothing assumed" and passes. The library must not silently shrink.
if total < MINIMUM_CHECKS:
    raise SystemExit(
        f"PROOF GATE FAILED: only {total} checks proved, expected at least {MINIMUM_CHECKS}; "
        "retain the pinned proof floor and required coverage; investigate missing analysis and "
        "restore the implementation and proof obligations before retrying"
    )

# Per-subprogram coverage, read from the same summary the counts came from. The parser is fail
# closed: inside the per-unit section every indented line must be the one proved form, and each
# unit must list exactly as many proved subprograms as it says it analyzed. What remains here is
# what the parse cannot know: units analyzed only in part, units with nothing analyzed, the
# required subprograms and the declared boundary.
units: dict[str, dict[str, int]] = parsed["units"]
subprograms: dict[str, dict[str, object]] = parsed["subprograms"]
coverage_problems: list[str] = []
for unit, counts in units.items():
    if counts["analyzed"] != counts["available"]:
        coverage_problems.append(f"unit {unit}: {counts['analyzed']} of {counts['available']} analyzed")
    if unit not in UNANALYZED_BOUNDARY and counts["available"] == 0:
        coverage_problems.append(f"unit {unit}: nothing analyzed")
for name in REQUIRED_PROVED:
    if name not in subprograms:
        coverage_problems.append(f"{name}: absent from the proof summary")
if not units or not subprograms:
    coverage_problems.append("no per-subprogram lines in the proof summary")
for unit in sorted(UNANALYZED_BOUNDARY):
    if unit not in units:
        coverage_problems.append(f"declared boundary unit {unit} missing from the summary")
print(f"subprograms    {len(subprograms)} proved in {len(units)} units")
if coverage_problems:
    raise SystemExit("PROOF GATE FAILED: coverage: " + "; ".join(coverage_problems))

sha256 = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
first_line = lambda argv: subprocess.run(
    argv, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
).stdout.splitlines()[0]
manifest = {
    "schemaVersion": 1,
    "claim": "all checks proved, nothing assumed",
    "project": "core/worldline_core.gpr",
    "options": sys.argv[4:],
    "proof": {
        "total": total,
        "justified": justified,
        "unproved": unproved,
        "pragmaAssume": assumes,
        "minimumChecks": MINIMUM_CHECKS,
        # Bind the recorded counts to the artifact they were read from, so a later reader can
        # tell that this manifest describes a real summary rather than a stale or absent one.
        "summarySha256": sha256(out_path),
    },
    "toolchain": {
        "gnatprove": first_line(["gnatprove", "--version"]),
        "gprbuild": first_line(["gprbuild", "--version"]),
    },
    "sourceHashes": {key: sha256(path) for key, path in sorted(sources.items())},
    "library": {
        "path": "lib/libworldline_core.so",
        "sha256": sha256(lib_path),
    },
    "coverage": {
        "requiredProved": REQUIRED_PROVED,
        "unanalyzedBoundary": sorted(UNANALYZED_BOUNDARY),
        "units": units,
        "subprograms": subprograms,
    },
    "boundary": {
        "proved": ["Worldline SPARK policy units", "Attest.SHA256 absence of runtime error"],
        "notProved": [
            "C/Python/QML boundary: the C ABI entry points in worldline-c_api (SPARK_Mode Off:"
            " pointer dereference, exception handlers, file and byte hashing marshalling, and the"
            " decoding and validation of evaluation observations, classifications and presence"
            " records) and the Python mapping of observations to the kernel's finite categories;"
            " the collapse request's decode and validation are proved (Worldline.Collapse_Wire)",
            "OS syscalls and filesystem behavior",
        ],
        "assumptions": [
            "SHA-256 is functionally correct (tested against published vectors, not proved) and"
            " collision-resistant; every identity equality the kernel proves is an equality of"
            " digests",
            "the runtime supplies authentic observations and computes each Decide input from the"
            " independent source its comment names; a value passed to both sides of an equality"
            " proves nothing",
            "the C header's wl_collapse_request layout equals Collapse_Wire.Raw_Request: checked"
            " by name-keyed offsets at load and by the test suite, not proved",
            "the prepared transaction record read back at commit is the one prepare wrote (store"
            " integrity, not proved)",
        ],
    },
}
manifest_path = root / "proof-manifest.json"
manifest_path.write_text(
    json.dumps(manifest, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
    encoding="utf-8",
)
print(f"PROOF GATE PASSED — {total} checks, all proved, nothing assumed.")
print(f"manifest        {manifest_path}")
PY

# The summary is re-read and re-derived, and its digest checked against the manifest just
# written (1.9.2, OB-085): the manifest cannot describe a summary other than this one.
python3 "$ROOT/verify_proof_manifest.py" --require-summary "$OUT"
