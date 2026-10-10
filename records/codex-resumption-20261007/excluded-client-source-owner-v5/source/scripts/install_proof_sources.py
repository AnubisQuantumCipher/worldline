#!/usr/bin/env python3
"""Copy the proof sources beside an installed library (1.9.2, OB-084).

    install_proof_sources.py SOURCE_TREE DESTINATION

The runtime recomputes the contract pins and the source hashes from these files at every
receipt (proof.ProofStatus), instead of trusting what the manifest says about them. The set is
exactly what the proof gate reads: proof_manifest.proof_source_files. Files are made read-only
(0444); the directories stay owner-writable so a later install, rollback or backup prune can
remove them. Read-only is a guard against accidents, not against this account (OB-039).
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import sys


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    root, destination = Path(sys.argv[1]).resolve(), Path(sys.argv[2])
    sys.path.insert(0, str(root / "runtime"))
    from worldline.proof_manifest import proof_source_files

    if destination.exists():
        print(f"install_proof_sources: {destination} already exists", file=sys.stderr)
        return 2
    for relative in proof_source_files(root):
        source = root / relative
        if not source.is_file() or source.is_symlink():
            print(f"install_proof_sources: not a regular file: {source}", file=sys.stderr)
            return 1
        target = destination / relative
        target.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        os.chmod(target, 0o444)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
