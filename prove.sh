#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
cd "$ROOT"
# shellcheck disable=SC1090
# The reference machine keeps GNAT FSF under ~/opt/gnat; elsewhere (CI, packaging) the
# toolchain is already on PATH.
if [[ -f "${GNAT_ENV:-$HOME/opt/gnat/env.sh}" ]]; then source "${GNAT_ENV:-$HOME/opt/gnat/env.sh}"; fi

OUT="obj/core-library/gnatprove/gnatprove.out"
LIB="lib/libworldline_core.so"
OPTIONS=("-P" "core/worldline_core.gpr" "-U" "--level=3" "--report=fail" "-j0")

echo "== build libworldline_core.so =="
gprbuild -q -P worldline.gpr

echo "== prove every Worldline core unit =="
# Remove any previous summary first: without this, a gnatprove run that fails or aborts can
# leave the PREVIOUS run's summary in place to be read as this run's result, while the manifest
# is regenerated over today's (unproved) sources. Also stop discarding gnatprove's exit status.
rm -f "$OUT"
if ! gnatprove "${OPTIONS[@]}"; then
  echo "prove: gnatprove exited non-zero" >&2
  exit 2
fi
[[ -f "$OUT" ]] || { echo "prove: gnatprove produced no summary"; exit 2; }
[[ -f "$LIB" ]] || { echo "prove: shared library is missing"; exit 2; }

python3 - "$ROOT" "$OUT" "$LIB" <<'PY'
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
from verify_proof_manifest import MINIMUM_CHECKS, REQUIRED_PROVED, UNANALYZED_BOUNDARY  # noqa: E402
out_path = (root / sys.argv[2]).resolve()
lib_path = (root / sys.argv[3]).resolve()
summary = out_path.read_text(encoding="utf-8")

total_line = next((line for line in summary.splitlines() if line.startswith("Total")), None)
if total_line is None:
    raise SystemExit("prove: Total row missing from gnatprove summary")
clean = re.sub(r"\([0-9]+%\)", "", total_line)
fields = clean.split()
if len(fields) != 6:
    raise SystemExit(f"prove: cannot parse Total row: {total_line}")
_, total_text, flow_text, prover_text, justified_text, unproved_text = fields
parse_count = lambda value: 0 if value == "." else int(value)
total = parse_count(total_text)
justified = parse_count(justified_text)
unproved = parse_count(unproved_text)

sources: dict[str, Path] = {
    "worldline.gpr": root / "worldline.gpr",
    "attest/attest.ads": root / "core/attest/attest.ads",
    "attest/attest-sha256.ads": root / "core/attest/attest-sha256.ads",
    "attest/attest-sha256.adb": root / "core/attest/attest-sha256.adb",
}
for pattern in ("*.ads", "*.adb", "*.gpr", "*.h"):
    for path in sorted((root / "core").glob(pattern)):
        sources[f"core/{path.name}"] = path

missing = [key for key, path in sources.items() if not path.is_file()]
if missing:
    raise SystemExit("prove: proof source missing: " + ", ".join(missing))

# `pragma Assume` screening must be case-insensitive and whitespace-tolerant: Ada accepts
# "pragma  assume" and "pragma\nAssume", which a raw byte count silently scores as zero. Also
# screen for justification pragmas and for a body quietly leaving SPARK analysis entirely.
_ASSUME = re.compile(rb"(?is)\bpragma\s+assume\b")
# Any GNATprove annotation, in pragma or aspect form: justifications (False_Positive,
# Intentional) and exclusions (Skip_Proof, Skip_Flow_And_Proof) alike. None is allowed.
_JUSTIFY = re.compile(rb"(?is)\b(pragma\s+annotate\s*\(|annotate\s*=>\s*\()\s*gnatprove\b")
_SPARK_OFF = re.compile(rb"(?is)\bspark_mode\s*(=>|\()\s*off\b")


def code_only(path):
    """Source with Ada comments removed, so prose about these constructs is not screened.

    An `--` inside a string literal is not a comment, so quote state is tracked; screening
    comments would otherwise flag a header that merely *describes* where SPARK is disabled.
    """
    stripped = []
    for line in path.read_bytes().splitlines():
        in_string = False
        cut = len(line)
        index = 0
        while index < len(line):
            character = line[index : index + 1]
            if not in_string and character == b"'":
                # After an identifier or ')' this is an attribute tick (Character'( ... ));
                # otherwise 'x' is a character literal, and '"' or '-' inside it is neither a
                # string delimiter nor a comment.
                previous = line[:index].rstrip()[-1:]
                if not (previous.isalnum() or previous in (b"_", b")")) and line[index + 2 : index + 3] == b"'":
                    index += 3
                    continue
            if character == b'"':
                in_string = not in_string
            elif not in_string and line[index : index + 2] == b"--":
                cut = index
                break
            index += 1
        stripped.append(line[:cut])
    return b"\n".join(stripped)


code = {key: code_only(path) for key, path in sources.items()}
assumes = sum(len(_ASSUME.findall(text)) for text in code.values())
justifications = sum(len(_JUSTIFY.findall(text)) for text in code.values())
# worldline-c_api is the one declared, documented exception: it is the unproved C/Python
# boundary named in the manifest's own boundary.notProved list.
spark_off = sorted(
    key for key, text in code.items()
    if _SPARK_OFF.search(text) and "c_api" not in key
)
print(f"checks total   {total}")
print(f"justified      {justified}")
print(f"unproved       {unproved}")
print(f"pragma Assume  {assumes}")
print(f"justify pragma {justifications}")
if unproved or justified or assumes or justifications:
    raise SystemExit("PROOF GATE FAILED")
if spark_off:
    raise SystemExit("PROOF GATE FAILED: SPARK_Mode => Off outside the declared boundary: "
                     + ", ".join(spark_off))
# A floor is what makes "all checks proved" mean anything: with none, a run that analyzed
# nothing (every body excluded from SPARK, or a summary of all dots) reports
# "0 checks, all proved, nothing assumed" and passes. The library must not silently shrink.
if total < MINIMUM_CHECKS:
    raise SystemExit(
        f"PROOF GATE FAILED: only {total} checks proved, expected at least {MINIMUM_CHECKS}; "
        "if this reduction is intentional, lower MINIMUM_CHECKS deliberately in verify_proof_manifest.py"
    )

# Per-subprogram coverage, read from the same summary the counts came from. Fail closed: inside
# the per-unit section every indented line must be the one proved form. Anything else --
# "proof skipped", "not analyzed", a skipped flow analysis, a format this parser has never seen
# -- is a coverage problem, never a line to ignore.
_UNIT = re.compile(r"^in unit (\S+), (\d+) subprograms and packages out of (\d+) analyzed$")
_SUBPROGRAM = re.compile(
    r"^  (\S+) at (\S+) flow analyzed \(0 errors, \d+ checks, \d+ warnings and "
    r"0 pragma Assume statements\) and proved \((\d+) checks\)$")
units: dict[str, dict[str, int]] = {}
subprograms: dict[str, dict[str, object]] = {}
listed: dict[str, int] = {}
coverage_problems: list[str] = []
current_unit: str | None = None
for line in summary.splitlines():
    unit_match = _UNIT.match(line)
    if unit_match:
        current_unit = unit_match.group(1)
        analyzed, available = int(unit_match.group(2)), int(unit_match.group(3))
        units[current_unit] = {"analyzed": analyzed, "available": available}
        listed[current_unit] = 0
        if analyzed != available:
            coverage_problems.append(f"unit {current_unit}: {analyzed} of {available} analyzed")
        if current_unit not in UNANALYZED_BOUNDARY and available == 0:
            coverage_problems.append(f"unit {current_unit}: nothing analyzed")
        continue
    if current_unit is None:
        continue
    if not line.startswith("  "):
        current_unit = None
        continue
    sub_match = _SUBPROGRAM.match(line)
    if sub_match is None:
        coverage_problems.append(f"unit {current_unit}: not a proved subprogram: {line.strip()}")
        continue
    name, where, checks = sub_match.groups()
    subprograms[name] = {"at": where, "checks": int(checks), "proved": True}
    listed[current_unit] += 1
for unit, counts in units.items():
    if listed.get(unit, 0) != counts["analyzed"]:
        coverage_problems.append(f"unit {unit}: {counts['analyzed']} analyzed but {listed.get(unit, 0)} listed as proved")
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
    "options": ["-U", "--level=3", "--report=fail", "-j0"],
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

python3 "$ROOT/verify_proof_manifest.py"
