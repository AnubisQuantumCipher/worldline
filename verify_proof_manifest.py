#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


def source_paths(root: Path) -> dict[str, Path]:
    result: dict[str, Path] = {
        "worldline.gpr": root / "worldline.gpr",
        "attest/attest.ads": root.parent / "attest/src/attest.ads",
        "attest/attest-sha256.ads": root.parent / "attest/src/attest-sha256.ads",
        "attest/attest-sha256.adb": root.parent / "attest/src/attest-sha256.adb",
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

    paths = source_paths(root)
    recorded = manifest.get("sourceHashes")
    if not isinstance(recorded, dict) or set(recorded) != set(paths):
        print("proof source set changed after proof", file=sys.stderr)
        return 1
    for key, path in paths.items():
        if not path.is_file() or recorded[key] != digest(path):
            print(f"proof source changed after proof: {key}", file=sys.stderr)
            return 1

    library = manifest.get("library", {})
    library_path = root / str(library.get("path", ""))
    if not library_path.is_file() or library.get("sha256") != digest(library_path):
        print("proved library changed after proof", file=sys.stderr)
        return 1

    print("proof manifest verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
