"""Verify this source archive's bytes and Git executable modes, not engineering correctness."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', required=True)
    parser.parse_args()
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / 'PHASE1-SOURCE-CHECKPOINT-20261010-F66.json').read_text())
    failures = []
    for row in manifest['copied_files']:
        relative = Path(row['path'])
        if relative.is_absolute() or '..' in relative.parts:
            failures.append({'path': row['path'], 'reason': 'unsafe manifest path'})
            continue
        path = root / relative
        if path.is_symlink() or not path.is_file():
            failures.append({'path': row['path'], 'reason': 'missing or nonregular file'})
            continue
        data = path.read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        actual_mode = '100755' if path.stat().st_mode & 0o111 else '100644'
        if (hashlib.sha256(data).hexdigest(), len(data), blob, actual_mode) != (
                row['sha256'], row['bytes'], row['git_blob'], row['git_mode']):
            failures.append({'path': row['path'], 'reason': 'content or executable-mode mismatch'})
    print(json.dumps({'checked_files': len(manifest['copied_files']), 'failures': failures,
                      'phase_one_acceptance': False}, indent=2))
    raise SystemExit(bool(failures))


if __name__ == '__main__':
    main()
