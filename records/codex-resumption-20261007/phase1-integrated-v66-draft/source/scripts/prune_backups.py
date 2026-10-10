#!/usr/bin/env python3
"""Keep the most recent install backups and remove the rest, saying exactly what was removed.

Every install writes a backup holding the previous runtime, launchers, unit, desktop config and
the whole state directory. That is what makes an install reversible, and it is also why the area
grows without bound: on this machine the state copy alone is tens of megabytes per install, so a
few upgrades quietly cost more disk than the engine itself. An installer that never prunes
eventually fills the disk, and a full disk is a worse failure than the one the backup insures
against.

    prune_backups.py <backups-dir> --keep 5 [--apply] [--json]

Without --apply nothing is removed and the report says what would be. Directories are ordered by
their UTC stamp, so "most recent" is read from the name rather than from mtime, which a restore
or a copy would have rewritten.

Refuses to remove anything that is not recognisably one of this installer's own backups: the name
must match <stamp>-<pid>, it must be a direct child of the given directory, and it must not be a
symlink. Deleting the wrong tree here would destroy the recovery path it exists to protect.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

NAME = re.compile(r"^\d{8}T\d{6}Z-\d+$")


def directory_size(path: Path) -> int:
    total = 0
    for item in path.rglob("*"):
        try:
            if item.is_file() and not item.is_symlink():
                total += item.stat().st_size
        except OSError:
            continue
    return total


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("backups", help="the install-backups directory")
    parser.add_argument("--keep", type=int, default=5, help="how many of the most recent backups to keep (0 disables pruning)")
    parser.add_argument("--apply", action="store_true", help="actually remove them; without this nothing is removed")
    parser.add_argument("--json", action="store_true", help="print the report as JSON")
    args = parser.parse_args(argv[1:])

    root = Path(args.backups)
    if args.keep < 0:
        print("prune-backups: --keep cannot be negative", file=sys.stderr)
        return 2
    report: dict = {"directory": str(root), "keep": args.keep, "applied": bool(args.apply),
                    "kept": [], "removed": [], "skipped": [], "freedBytes": 0}
    if args.keep == 0:
        report["note"] = "pruning is disabled (--keep 0); every backup is kept"
    if not root.is_dir():
        report["note"] = "there is no backup directory yet"
        print(json.dumps(report, indent=2) if args.json else f"prune-backups: {root} does not exist; nothing to do")
        return 0

    candidates, skipped = [], []
    for child in sorted(root.iterdir()):
        if child.is_symlink() or not child.is_dir() or not NAME.match(child.name):
            skipped.append({"name": child.name, "why": "not one of this installer's backups"})
            continue
        candidates.append(child)
    candidates.sort(key=lambda p: p.name, reverse=True)
    report["skipped"] = skipped

    keep = candidates if args.keep == 0 else candidates[: args.keep]
    drop = [] if args.keep == 0 else candidates[args.keep:]
    report["kept"] = [p.name for p in keep]

    for target in drop:
        size = directory_size(target)
        entry = {"name": target.name, "bytes": size}
        if args.apply:
            try:
                shutil.rmtree(target)
            except OSError as exc:
                entry["error"] = str(exc)[:200]
                report["skipped"].append({"name": target.name, "why": entry["error"]})
                continue
        report["removed"].append(entry)
        report["freedBytes"] += size

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        verb = "removed" if args.apply else "would remove"
        if report["removed"]:
            freed = report["freedBytes"] / (1024 * 1024)
            print(f"prune-backups: {verb} {len(report['removed'])} backup(s), {freed:.0f} MiB: "
                  + ", ".join(e["name"] for e in report["removed"]))
        print(f"prune-backups: keeping {len(report['kept'])} most recent"
              + (f" ({', '.join(report['kept'])})" if report["kept"] else ""))
        for item in report["skipped"]:
            print(f"prune-backups: left alone: {item['name']} — {item['why']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
