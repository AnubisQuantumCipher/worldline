from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .core import Core, hash_id


class ProofStatus:
    @staticmethod
    def inspect(core: Core | None = None) -> dict[str, Any]:
        verifier = core or Core.shared()
        library = verifier.library_path
        project_root = Path(__file__).resolve().parents[2]
        candidates = (library.parent / "proof-manifest.json", project_root / "proof-manifest.json")
        manifest_path = next((path for path in candidates if path.is_file()), None)
        if manifest_path is None:
            return {"state": "UNVERIFIED", "reason": "proof-manifest.json is missing", "manifest": None}
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            proof = manifest["proof"]
            recorded_library = manifest["library"]["sha256"]
        except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
            return {"state": "UNVERIFIED", "reason": f"proof manifest is invalid: {exc}", "manifest": str(manifest_path)}
        actual_library = hashlib.sha256(library.read_bytes()).hexdigest()
        if recorded_library != actual_library:
            return {"state": "UNVERIFIED", "reason": "library hash differs from proof manifest", "manifest": str(manifest_path)}
        if any(proof.get(key) != 0 for key in ("unproved", "justified", "pragmaAssume")):
            return {"state": "UNVERIFIED", "reason": "proof manifest records an exception", "manifest": str(manifest_path)}
        return {
            "state": "PROVED",
            "manifest": str(manifest_path),
            "manifestHash": hash_id(verifier.hash_file(manifest_path)),
            "checks": proof.get("total"),
            "boundary": manifest.get("boundary"),
        }
