#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
cd "$ROOT"
# shellcheck disable=SC1090
source "${GNAT_ENV:-$HOME/opt/gnat/env.sh}"

OUT="obj/core-library/gnatprove/gnatprove.out"
LIB="lib/libworldline_core.so"
OPTIONS=("-P" "core/worldline_core.gpr" "-U" "--level=3" "--report=fail" "-j0")

echo "== build libworldline_core.so =="
gprbuild -q -P worldline.gpr

echo "== prove every Worldline core unit =="
gnatprove "${OPTIONS[@]}" || true
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
    "attest/attest.ads": root.parent / "attest/src/attest.ads",
    "attest/attest-sha256.ads": root.parent / "attest/src/attest-sha256.ads",
    "attest/attest-sha256.adb": root.parent / "attest/src/attest-sha256.adb",
}
for pattern in ("*.ads", "*.adb", "*.gpr", "*.h"):
    for path in sorted((root / "core").glob(pattern)):
        sources[f"core/{path.name}"] = path

missing = [key for key, path in sources.items() if not path.is_file()]
if missing:
    raise SystemExit("prove: proof source missing: " + ", ".join(missing))

assumes = sum(path.read_bytes().count(b"pragma Assume") for path in sources.values())
print(f"checks total   {total}")
print(f"justified      {justified}")
print(f"unproved       {unproved}")
print(f"pragma Assume  {assumes}")
if unproved or justified or assumes:
    raise SystemExit("PROOF GATE FAILED")

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
