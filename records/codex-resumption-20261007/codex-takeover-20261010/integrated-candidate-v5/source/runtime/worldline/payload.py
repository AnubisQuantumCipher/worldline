from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Sequence

from .core import Core
from .errors import WorldlineError
from .manifest import Manifest


def materialize_payload_view(
    payload: Path,
    roots: Sequence[dict[str, Any]],
    destination: Path,
    core: Core | None = None,
) -> Path:
    verifier = core or Core.shared()
    if destination.exists():
        raise WorldlineError("DESTINATION_EXISTS", f"world view destination exists: {destination}")
    destination.mkdir(mode=0o700, parents=True)
    for root in roots:
        root_key = root["root_key"]
        source = payload / root_key
        manifest_path = payload / "manifests" / f"{root_key}.json"
        if not source.is_dir() or not manifest_path.is_file():
            raise WorldlineError(
                "PAYLOAD_INTEGRITY_FAILED",
                f"world payload lacks root or manifest: {root_key}",
            )
        manifest = Manifest.load(manifest_path, verifier)
        Manifest.verify_content(manifest, source, verifier)
        Manifest.materialize(
            manifest,
            source,
            destination / root_key,
            core=verifier,
        )
    return destination
