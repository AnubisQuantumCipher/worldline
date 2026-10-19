"""Derive the two existing C transport pins only after exact-source review.

This is a source identity update, not proof or Phase One acceptance. The review
is checked against current bytes; it is not a cryptographic reviewer attestation.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from refresh_contract_pins import _pin_normalizer

TARGET = 'core/worldline-c_api.adb'
TABLES = ('_TYPED_EXPORT_NORMALIZED_UNIT_PINS', '_TYPED_EXPORT_RAW_UNIT_PINS')


def accepted_source(review):
    if (review.get('verdict') != 'CONCUR' or
            review.get('complete_unit_read') is not True or
            review.get('blocking_findings') != []):
        raise ValueError('complete-unit review has not concurred')
    sources = review.get('source_sha256', {})
    if TARGET not in sources:
        raise ValueError('review does not bind the changed complete unit')
    for name, expected in sources.items():
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file():
            raise ValueError('review source is outside this worktree or missing')
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('review source changed: ' + name)
    return sources[TARGET]


def rewrite(review_path, write):
    raw = accepted_source(json.loads(review_path.read_text()))
    path = ROOT / 'runtime/worldline/proof_manifest.py'
    original = path.read_bytes()
    tree = ast.parse(original)
    pin, _ = _pin_normalizer(tree, path)
    desired = (pin(ROOT, TARGET), raw)
    lines = original.splitlines(keepends=True)
    replacements, changes = [], []
    for table_name, digest in zip(TABLES, desired):
        matches = [n.value for n in tree.body if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == table_name for t in n.targets)]
        if len(matches) != 1 or not isinstance(matches[0], ast.Dict):
            raise ValueError('pin table shape changed')
        entries = [(k, v) for k, v in zip(matches[0].keys, matches[0].values)
                   if isinstance(k, ast.Constant) and k.value == TARGET]
        if len(entries) != 1 or not isinstance(entries[0][1], ast.Constant):
            raise ValueError('pin target is missing or ambiguous')
        value = entries[0][1]
        start = sum(map(len, lines[:value.lineno - 1])) + value.col_offset
        end = sum(map(len, lines[:value.end_lineno - 1])) + value.end_col_offset
        if value.value != digest:
            changes.append({'table': table_name, 'before': value.value, 'after': digest})
            replacements.append((start, end, repr(digest).encode()))
    updated = original
    for start, end, replacement in sorted(replacements, reverse=True):
        updated = updated[:start] + replacement + updated[end:]
    if write:
        path.write_bytes(updated)
    return {'kind': 'review-bound-source-pin-derivation', 'target': TARGET,
            'review_sha256': hashlib.sha256(review_path.read_bytes()).hexdigest(),
            'source_sha256': raw, 'changes': changes,
            'mode': 'write' if write else 'check', 'proof_or_acceptance': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--review', required=True, type=Path)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = rewrite(args.review.resolve(), args.write)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if args.write or not result['changes'] else 1)
