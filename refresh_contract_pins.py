#!/usr/bin/env python3
"""Derive existing contract pins from source, without changing proof policy.

The default/check mode refuses stale values in the initial dictionary and every
literal CONTRACT_PINS.update block. --write replaces only their existing digest
literals. This does not establish source acceptance or proof.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import sys
import unicodedata


def _pin_tables(tree: ast.Module) -> list[ast.Dict]:
    assignments = [node for node in ast.walk(tree) if isinstance(node, ast.Assign)
                   and any(isinstance(target, ast.Name) and target.id == "CONTRACT_PINS"
                           for target in node.targets)]
    if (len(assignments) != 1 or assignments[0] not in tree.body
            or not isinstance(assignments[0].value, ast.Dict)):
        raise ValueError("expected one top-level literal CONTRACT_PINS dictionary")
    assignment = assignments[0]
    tables = [assignment.value]
    updates = []
    for statement in tree.body:
        if not isinstance(statement, ast.Expr) or not isinstance(statement.value, ast.Call):
            continue
        call = statement.value
        if (isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Name)
                and call.func.value.id == "CONTRACT_PINS" and call.func.attr == "update"):
            if (statement.lineno < assignment.lineno or len(call.args) != 1
                    or call.keywords or not isinstance(call.args[0], ast.Dict)):
                raise ValueError("expected a literal CONTRACT_PINS.update dictionary after its declaration")
            updates.append(call)
            tables.append(call.args[0])
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name) and node.func.value.id == "CONTRACT_PINS"
                and node.func.attr not in {"items", "keys", "values", "get", "copy"}
                and node not in updates):
            raise ValueError("unsupported CONTRACT_PINS mutation")
        target = node.target if isinstance(node, (ast.AugAssign, ast.AnnAssign)) else None
        if isinstance(target, ast.Name) and target.id == "CONTRACT_PINS":
            raise ValueError("unsupported CONTRACT_PINS assignment")
        targets = node.targets if isinstance(node, (ast.Assign, ast.Delete)) else [target]
        if any(isinstance(item, ast.Subscript) and isinstance(item.value, ast.Name)
               and item.value.id == "CONTRACT_PINS" for item in targets):
            raise ValueError("unsupported CONTRACT_PINS item mutation")
    for table in tables:
        keys = []
        for key, value in zip(table.keys, table.values):
            if (not isinstance(key, ast.Constant) or not isinstance(key.value, str)
                    or not isinstance(value, ast.Constant) or not isinstance(value.value, str)
                    or not re.fullmatch(r"[0-9a-f]{64}", value.value)):
                raise ValueError("CONTRACT_PINS keys must be strings and values must be digest literals")
            keys.append(key.value)
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate CONTRACT_PINS key within a literal dictionary")
    return tables


def _pin_normalizer(tree: ast.Module, path: Path):
    names = ("ada_source_text", "ada_identifier_key", "ada_tokens", "normalized_ada",
             "source_profile_problems", "contract_text", "contract_pin")
    definitions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    if len(definitions) != len(names) or {node.name for node in definitions} != set(names):
        raise ValueError("cannot isolate the existing source pin normalizer")
    # Execute only the actual normalizer definitions, never the target module's
    # imports, policy updates or any native-loading entry point.
    normalizer_tree = ast.Module(body=[
        ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0),
        *definitions,
    ], type_ignores=[])
    namespace = {"Path": Path, "hashlib": hashlib, "re": re, "unicodedata": unicodedata}
    exec(compile(ast.fix_missing_locations(normalizer_tree), str(path), "exec"), namespace)
    return namespace["contract_pin"], namespace["source_profile_problems"]


def refresh(root: Path, *, write: bool) -> dict:
    path = root / "runtime/worldline/proof_manifest.py"
    original = path.read_text(encoding="utf-8")
    tree = ast.parse(original, filename=str(path))
    tables = _pin_tables(tree)
    stored = {}
    for table in tables:
        stored.update(ast.literal_eval(table))
    contract_pin, source_profile_problems = _pin_normalizer(tree, path)
    profile_problems = source_profile_problems(
        root, (root / relative for relative in dict.fromkeys(key.partition("#")[0] for key in stored)))
    if profile_problems:
        raise ValueError("; ".join(profile_problems))
    derived = {key: contract_pin(root, key) for key in stored}
    source_hashes = {
        relative: hashlib.sha256((root / relative).read_bytes()).hexdigest()
        for relative in dict.fromkeys(key.partition("#")[0] for key in stored)
    }
    encoded = original.encode("utf-8")
    lines = encoded.splitlines(keepends=True)
    changes = []
    replacements = []
    for table in tables:
        for key_node, value_node in zip(table.keys, table.values):
            key, value = key_node.value, value_node.value
            if value == derived[key]:
                continue
            start = sum(len(line) for line in lines[:value_node.lineno - 1]) + value_node.col_offset
            end = sum(len(line) for line in lines[:value_node.end_lineno - 1]) + value_node.end_col_offset
            literal = encoded[start:end].decode("utf-8")
            match = re.fullmatch(r"(?P<quote>['\"])[0-9a-f]{64}(?P=quote)", literal)
            if match is None:
                raise ValueError("cannot isolate existing pin literal: " + key)
            replacement = (match.group("quote") + derived[key] + match.group("quote")).encode("utf-8")
            replacements.append((start, end, replacement))
            changes.append({"path": key, "stored": value, "derived": derived[key],
                            "effectiveStored": stored[key], "tableLine": table.lineno,
                            "literalLine": value_node.lineno,
                            "sourceSha256": source_hashes[key.partition("#")[0]]})
    rewritten = encoded
    for start, end, replacement in reversed(replacements):
        rewritten = rewritten[:start] + replacement + rewritten[end:]
    updated_tree = ast.parse(rewritten.decode("utf-8"), filename=str(path))
    # Keep every table, key, statement and policy requirement unchanged. Only
    # digest values are masked for this structural assertion.
    for source_tree in (tree, updated_tree):
        for table in _pin_tables(source_tree):
            for value in table.values:
                value.value = "PIN"
    if ast.dump(tree) != ast.dump(updated_tree):
        raise ValueError("pin refresh changed source outside the existing digest values")
    if write and rewritten != encoded:
        path.write_bytes(rewritten)
    return {"kind": "source-only-contract-pin-derivation", "root": str(root),
            "normalizer": "worldline.proof_manifest.contract_pin",
            "normalizerLoading": "AST-selected existing definitions; no target module import",
            "manifestSha256Before": hashlib.sha256(encoded).hexdigest(),
            "manifestSha256After": hashlib.sha256(rewritten if write else encoded).hexdigest(),
            "refreshScriptSha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "effectivePinCount": len(stored),
            "literalPinCount": sum(len(table.keys) for table in tables),
            "literalTableLines": [table.lineno for table in tables],
            "sourceIdentities": source_hashes,
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
    report["invocation"] = list(sys.orig_argv)
    output = json.dumps(report, indent=2) + "\n"
    if args.report:
        args.report.write_text(output, encoding="utf-8")
    print(output, end="")
    return 0 if args.write or not report["changed"] else 1


if __name__ == "__main__":
    sys.exit(main())
