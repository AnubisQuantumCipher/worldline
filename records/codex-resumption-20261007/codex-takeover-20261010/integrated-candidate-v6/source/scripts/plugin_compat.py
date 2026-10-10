#!/usr/bin/env python3
"""The plugin this engine release is compatible with (1.9.2, OB-195).

    plugin_compat.py --named-commit FILE
        print the plugin commit FILE names, "none" when it names none yet, or
        "invalid:<reason>" when FILE is not a compatibility record (install.sh reads this)
    plugin_compat.py --plugin-repo PATH --ref REF [--write]
        resolve REF in the plugin repository, digest `git archive` of that commit, and (with
        --write) record tag, commit, archive digest and this engine's code-set digest in
        plugin-compatibility.json

plugin-compatibility.json is in-tree because release-manifest.json is written only by CI; the
release gate copies it into the manifest as `pluginCompatibility` and refuses a release whose
record names no commit. install.sh installs only the named commit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "worldline-plugin-compatibility-v1"
RECORD = ROOT / "plugin-compatibility.json"


def validate(value: object) -> list[str]:
    problems: list[str] = []
    if not isinstance(value, dict) or value.get("schema") != SCHEMA:
        return [f"not a {SCHEMA} record"]
    plugin = value.get("plugin")
    if not isinstance(plugin, dict):
        return ["no plugin object"]
    commit, archive, tag = plugin.get("commit"), plugin.get("archiveSha256"), plugin.get("tag")
    if not (isinstance(commit, str) and re.fullmatch(r"[0-9a-f]{40}", commit)):
        problems.append("the record names no plugin commit")
    if not (isinstance(archive, str) and re.fullmatch(r"[0-9a-f]{64}", archive)):
        problems.append("the record names no plugin archive digest")
    if not (isinstance(tag, str) and re.fullmatch(r"v\d+\.\d+\.\d+", tag)):
        problems.append("the record names no plugin release tag")
    code_set = value.get("codeSetSha256")
    if not (isinstance(code_set, str) and re.fullmatch(r"[0-9a-f]{64}", code_set)):
        problems.append("the record names no code-set digest")
    return problems


def named_commit(path: Path) -> str:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return f"invalid:{type(exc).__name__}"
    if not isinstance(value, dict) or value.get("schema") != SCHEMA or not isinstance(value.get("plugin"), dict):
        return "invalid:not-a-compatibility-record"
    commit = value["plugin"].get("commit")
    return commit if isinstance(commit, str) and re.fullmatch(r"[0-9a-f]{40}", commit) else "none"


def archive_digest(repository: Path, commit: str) -> str:
    completed = subprocess.run(["git", "-C", str(repository), "archive", "--format=tar", commit],
                               stdout=subprocess.PIPE, check=True)
    return hashlib.sha256(completed.stdout).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--named-commit", metavar="FILE")
    parser.add_argument("--plugin-repo")
    parser.add_argument("--ref")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.named_commit:
        print(named_commit(Path(args.named_commit)))
        return 0
    if not args.plugin_repo or not args.ref:
        parser.error("--plugin-repo and --ref are required")
    repository = Path(args.plugin_repo)
    commit = subprocess.run(["git", "-C", str(repository), "rev-parse", f"{args.ref}^{{commit}}"],
                            stdout=subprocess.PIPE, text=True, check=True).stdout.strip()
    sys.path.insert(0, str(ROOT / "runtime"))
    from worldline.engine_codes import CODE_SET_SHA256
    record = json.loads(RECORD.read_text(encoding="utf-8")) if RECORD.is_file() else {"schema": SCHEMA}
    record["plugin"] = {**(record.get("plugin") or {}), "repository": "worldline-omarchy", "tag": args.ref,
                        "commit": commit, "archiveSha256": archive_digest(repository, commit)}
    record["codeSetSha256"] = CODE_SET_SHA256
    text = json.dumps(record, indent=2, sort_keys=True) + "\n"
    if args.write:
        RECORD.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
