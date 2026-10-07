#!/usr/bin/env python3
"""Derive existing contract pins from source, without changing proof policy.

The default/check mode refuses stale values. --write replaces only existing
CONTRACT_PINS digest literals and records every changed pin. It does not establish
source acceptance or proof; independently review intentional semantic changes.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys


def refresh(root: Path, *, write: bool) -> dict:
    path = root / "runtime/worldline/proof_manifest.py"
    original = path.read_text(encoding="utf-8")
    tree = ast.parse(original, filename=str(path))
    assignments = [node for node in tree.body if isinstance(node, ast.Assign)
                   and any(isinstance(target, ast.Name) and target.id == "CONTRACT_PINS"
                           for target in node.targets)]
    if len(assignments) != 1 or not isinstance(assignments[0].value, ast.Dict):
        raise ValueError("expected one literal CONTRACT_PINS dictionary")
    node = assignments[0].value
    stored = ast.literal_eval(node)
    if not all(isinstance(k, str) and isinstance(v, str) for k, v in stored.items()):
        raise ValueError("CONTRACT_PINS keys and values must be strings")
    specification = importlib.util.spec_from_file_location("worldline_contract_pin_source", path)
    if specification is None or specification.loader is None:
        raise ValueError("cannot load the source pin normalizer")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    derived = {key: module.contract_pin(root, key) for key in stored}
    changes = [{"path": key, "stored": stored[key], "derived": derived[key],
                "sourceSha256": hashlib.sha256((root / key.partition("#")[0]).read_bytes()).hexdigest()}
               for key in stored if stored[key] != derived[key]]
    lines = original.splitlines(keepends=True)
    start = sum(len(line) for line in lines[:node.lineno - 1]) + node.col_offset
    end = sum(len(line) for line in lines[:node.end_lineno - 1]) + node.end_col_offset
    table = original[start:end]
    replacement = table
    for key in stored:
        pattern = r"(?P<key>['\"]" + re.escape(key) + r"['\"]\s*:\s*)(?P<quote>['\"])(?P<digest>[0-9a-f]{64})(?P=quote)"
        replacement, found = re.subn(pattern, lambda match: match.group("key") + match.group("quote") + derived[key] + match.group("quote"), replacement)
        if found != 1:
            raise ValueError("cannot isolate existing pin literal: " + key)
    rewritten = original[:start] + replacement + original[end:]
    # Structural assertion: no code, key, policy constant, expected unit, required
    # subprogram, coverage requirement or floor changes during pin regeneration.
    updated_tree = ast.parse(rewritten, filename=str(path))
    for source_tree in (tree, updated_tree):
        assignment = next(n for n in source_tree.body if isinstance(n, ast.Assign)
                          and any(isinstance(t, ast.Name) and t.id == "CONTRACT_PINS" for t in n.targets))
        assignment.value = ast.Dict(keys=[ast.Constant(k) for k in stored],
                                    values=[ast.Constant("PIN") for _ in stored])
    if ast.dump(tree) != ast.dump(updated_tree):
        raise ValueError("pin refresh changed source outside the existing digest values")
    if write and rewritten != original:
        path.write_text(rewritten, encoding="utf-8")
    return {"kind": "source-only-contract-pin-derivation", "root": str(root),
            "normalizer": "worldline.proof_manifest.contract_pin",
            "mode": "write" if write else "check", "changed": changes,
            "proofPolicyUnchanged": True, "proofRun": False,
            "independentAcceptanceReview": False,
            "status": "pins-refreshed" if write else ("pins-current" if not changes else "stale-pins")}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="refuse any stale existing digest (default)")
    mode.add_argument("--write", action="store_true", help="replace existing digest literals from exact source")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--report", type=Path, help="save the source-only derivation record")
    args = parser.parse_args()
    report = refresh(args.root.resolve(), write=args.write)
    output = json.dumps(report, indent=2) + "\n"
    if args.report:
        args.report.write_text(output, encoding="utf-8")
    print(output, end="")
    return 0 if args.write or not report["changed"] else 1


if __name__ == "__main__":
    sys.exit(main())
