#!/usr/bin/env python3
"""Check retained bytes and source identities; does not build or execute WORLDLINE."""
from pathlib import Path
import gzip
import hashlib
import json
import os
import stat
import io


class JoinedParts(io.RawIOBase):
    def __init__(self, paths):
        self.paths = iter(paths)
        self.current = None

    def readable(self):
        return True

    def readinto(self, buffer):
        while True:
            if self.current is None:
                path = next(self.paths, None)
                if path is None:
                    return 0
                self.current = path.open('rb')
            size = self.current.readinto(buffer)
            if size:
                return size
            self.current.close()
            self.current = None

    def close(self):
        if self.current is not None:
            self.current.close()
        super().close()

ROOT = Path(__file__).resolve().parent
manifest = json.loads((ROOT / 'files.sha256.json').read_text())
expected = {item['path'] for item in manifest['files']}
actual = {
    p.relative_to(ROOT).as_posix()
    for p in ROOT.rglob('*') if p.is_file() or p.is_symlink()
} - {'files.sha256.json'}
assert expected == actual, {'missing': sorted(expected-actual), 'unexpected': sorted(actual-expected)}
for item in manifest['files']:
    p = ROOT / item['path']
    data = os.readlink(p).encode() if p.is_symlink() else p.read_bytes()
    assert hashlib.sha256(data).hexdigest() == item['sha256'], item['path']
    assert len(data) == item['bytes'], item['path']
source = json.loads((ROOT / 'source-inventory.json').read_text())
for item in source['files']:
    p = ROOT / 'source' / item['path']
    data = os.readlink(p).encode() if p.is_symlink() else p.read_bytes()
    oid = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    assert oid == item['git_blob'], item['path']
    if item['git_mode'] == '120000':
        assert p.is_symlink(), item['path']
    else:
        assert stat.S_ISREG(p.stat().st_mode), item['path']
        assert bool(p.stat().st_mode & 0o111) == (item['git_mode'] == '100755'), item['path']
receipts = json.loads((ROOT / 'copy-receipts.json').read_text())
for item in receipts['files']:
    if item.get('encoding') != 'gzip':
        continue
    h = hashlib.sha256()
    size = 0
    parts = [ROOT / p['path'] for p in item['stored_parts']] if 'stored_parts' in item else [ROOT / item['stored']]
    compressed_hash = hashlib.sha256()
    for part in parts:
        with part.open('rb') as f:
            while block := f.read(1024*1024):
                compressed_hash.update(block)
    assert compressed_hash.hexdigest() == item['sha256'], parts
    with io.BufferedReader(JoinedParts(parts)) as joined, gzip.GzipFile(fileobj=joined, mode='rb') as stream:
        while block := stream.read(1024*1024):
            h.update(block)
            size += len(block)
    assert h.hexdigest() == item['original_sha256'] and size == item['original_bytes'], parts
print(json.dumps({'status': 'PASS', 'claim': 'checkpoint byte integrity only', 'source_commit': source['commit'], 'files_verified': len(expected), 'phase_one_complete': False}, indent=2))
