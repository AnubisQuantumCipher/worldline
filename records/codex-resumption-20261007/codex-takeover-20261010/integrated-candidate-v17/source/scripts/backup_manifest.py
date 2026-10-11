#!/usr/bin/env python3
"""Write a manifest of what an install backup actually holds.

Without it, a file missing from a backup is indistinguishable from a file that never existed on
this machine, and "restore it" silently becomes "skip it". Every item therefore records both
whether the source existed and whether it was captured.

    backup_manifest.py <backup-dir> <dest-lib> <worldline> <worldlined> <unit> <shell.json> <bindings.lua>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    backup = Path(argv[1])
    names = {
        "lib-worldline": argv[2],
        "worldline": argv[3],
        "worldlined": argv[4],
        "worldlined.service": argv[5],
        "shell.json": argv[6],
        "bindings.lua": argv[7],
    }
    items = []
    for stored, source in names.items():
        source_path = Path(source)
        items.append({
            "item": stored,
            "source": source,
            "sourceExisted": source_path.exists(),
            "sourceWasSymlink": source_path.is_symlink(),
            "captured": (backup / stored).exists(),
        })
    manifest = {
        "schemaVersion": 1,
        "items": items,
        "uncaptured": [i["item"] for i in items if i["sourceExisted"] and not i["captured"]],
        "absentOnThisMachine": [i["item"] for i in items if not i["sourceExisted"]],
        "state": {
            "captured": (backup / "state/worldline").is_dir(),
            "excludes": ["install-backups"],
            "note": "store, receipts, transactions and events, taken with the daemon stopped",
        },
        "payloads": {
            "captured": (backup / "share").is_dir(),
            "note": "payload data under ~/.local/share/worldline is inventoried in "
                    "payload-inventory.txt unless the install ran with WORLDLINE_BACKUP_PAYLOADS=1",
        },
    }
    (backup / "backup-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    if manifest["uncaptured"]:
        print("backup-manifest: NOT captured although present: " + ", ".join(manifest["uncaptured"]), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
