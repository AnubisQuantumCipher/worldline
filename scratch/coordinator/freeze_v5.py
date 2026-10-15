"""Coordinator-only immutable snapshot; invoke after the reviewed source commit."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import tarfile

root = Path.cwd()
out = root / 'records/phase1-blockers/freeze-v5'
frame = root / 'scratch/coordinator/final-frame-v5/source'
assert not out.exists() and not frame.exists()
dirty = subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'], text=True)
assert not dirty, dirty
commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
tree = subprocess.check_output(['git', 'rev-parse', 'HEAD^{tree}'], text=True).strip()
names = subprocess.check_output(['git', 'ls-files', '-z']).decode().split('\0')
def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()
hashes = {name: sha(root / name) for name in names if name}
out.mkdir()
archive = out / 'source.tar'
with archive.open('xb') as stream:
    subprocess.run(['git', 'archive', '--format=tar', commit], stdout=stream, check=True)
frame.mkdir(parents=True)
with tarfile.open(archive) as source:
    source.extractall(frame, filter='data')
assert all(sha(frame / name) == digest for name, digest in hashes.items())
source_record = {'classification': 'MEASURED', 'commit': commit, 'tree': tree,
                 'tracked_dirty': dirty,
                 'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 'command': ['python3', '-B', 'scratch/coordinator/freeze_v5.py'],
                 'source_hashes': hashes}
(out / 'source.json').open('x').write(json.dumps(source_record, indent=2) + '\n')
(out / 'snapshot.json').open('x').write(json.dumps({
    'source_commit': commit, 'frame': str(frame), 'all_tracked_hashes_match': True,
    'archive_sha256': sha(archive), 'driver_sha256': sha(Path(__file__))}, indent=2) + '\n')
print(json.dumps({'source_commit': commit, 'frame': str(frame), 'all_tracked_hashes_match': True}))
