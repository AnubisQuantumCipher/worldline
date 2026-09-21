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

# Floor for the total proved-check count. The gate is "all checks proved"; without a floor,
# a run that analyzed nothing satisfies it vacuously. Lower this only as a deliberate edit.
MINIMUM_CHECKS = 130

root = Path(sys.argv[1]).resolve()
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
_JUSTIFY = re.compile(rb"(?is)\bpragma\s+annotate\s*\(\s*gnatprove\s*,\s*(false_positive|intentional)")
_SPARK_OFF = re.compile(rb"(?is)\bspark_mode\s*=>\s*off\b")


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
        "if this reduction is intentional, lower MINIMUM_CHECKS deliberately in prove.sh"
    )

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
    "boundary": {
        "proved": ["Worldline SPARK policy units", "Attest.SHA256 absence of runtime error"],
        "notProved": ["C/Python/QML boundary", "OS syscalls and filesystem behavior"],
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
