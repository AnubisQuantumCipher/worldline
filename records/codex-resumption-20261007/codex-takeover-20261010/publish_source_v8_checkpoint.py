"""Preserve complete reviewed S8 and actual failure/custody records; no acceptance."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import stat
import subprocess

T = Path(__file__).resolve().parent
C = T.parents[4] / 'worldline-checkpoint-20261010-f67/checkout'
PREFIX = Path('records/codex-resumption-20261007/codex-takeover-20261010')
V = T / 'integrated-candidate-v8'


def pin(path):
    a = path.lstat()
    assert stat.S_ISREG(a.st_mode) and not path.is_symlink(), str(path)
    raw = path.read_bytes()
    b = path.lstat()
    assert (a.st_dev, a.st_ino, a.st_mode, a.st_size, a.st_mtime_ns, a.st_ctime_ns) == (b.st_dev, b.st_ino, b.st_mode, b.st_size, b.st_mtime_ns, b.st_ctime_ns)
    return {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': b.st_size, 'mode': stat.S_IMODE(b.st_mode)}


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())


def verify_source(root):
    expected = json.loads((V / 'stable-source-inventory.json').read_text())
    actual = {str(p.relative_to(root)) for p in [root, *root.rglob('*')]}
    assert actual == set(expected)
    for name, row in expected.items():
        p = root / name
        assert not p.is_symlink() and stat.S_IMODE(p.stat().st_mode) == row['mode']
        if row['kind'] == 'file':
            assert pin(p) == {k: value for k, value in row.items() if k != 'kind'}


assert subprocess.check_output(['git', 'status', '--porcelain'], cwd=C) == b''
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=C, text=True).strip()
assert head == '0a831eae5664d8dc31e9d66d7e6056250a87f91a'
assert pin(V / 'source-selection.json')['sha256'] == 'b29feb3e7739f00e4daf37c9bcf45d977f859577f8d79f8b9ff222db646c692d'
opinion = T / 'frame-review-draft/integrated-v8-independent-source-review.json'
assert pin(opinion)['sha256'] == '6a6611a3d4203c407350b6ba0bfbaea9daef894356d31b768e34a929026e288c'
verify_source(V / 'source')
files = sorted(p for p in V.rglob('*') if p.is_file())
files += sorted(p for p in (T / 'compiler-debug-tracking-cost-donor-ultra-v1').rglob('*') if p.is_file())
files += [opinion, T / 'acceptance-ultra-review-draft/integrated-v8-independent-complete-source-readback-v1.json', T / 'compose_candidate_v8.py', Path(__file__).resolve()]
K = T / 'native-v7-prefix-custody-recovery-v3-draft/Main-owned-collections/actual-root-custody-collect-v1'
files += [K / 'custody-only-partial-ownership-collection.json', K / 'coordination-custody-only-release.json', T / 'acceptance-ultra-review-draft/native-v7-prefix-custody-terminal-independent-review.json', T / 'runtime-frame-successor-v7-ultra-v3-draft/candidate/evidence/Main-original-qualified-prefix-execution-v1/Main-complete-owned-prefix-observation.json', T / 'formal-frame-successor-v8-draft/review/root-terminal-v1/actual-results-and-window-release.json', T / 'acceptance-ultra-review-draft/formal-v8-actual-deadline-terminal-release-independent-observation-v1.json']
rows = []
for src in files:
    before = pin(src)
    dst = C / PREFIX / src.relative_to(T)
    if dst.exists():
        assert pin(dst) == before, str(dst)
        continue
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    assert pin(src) == before == pin(dst), str(src)
    rows.append({'path': str(dst.relative_to(C)), **before})
published = C / PREFIX / 'integrated-candidate-v8/source'
for name, row in json.loads((V / 'stable-source-inventory.json').read_text()).items():
    if row['kind'] == 'directory':
        (published / name).chmod(row['mode'])
verify_source(published)
verify_source(V / 'source')
manifest = {
    'schema': 'worldline-reviewed-source-v8-and-actual-failure-checkpoint-v1',
    'previous_public_commit': head, 'copied_files': rows,
    'source_selection_sha256': pin(V / 'source-selection.json')['sha256'],
    'complete_published_source_keyset_bytes_modes_exact': True,
    'scope': 'Complete reviewed S8 source, debug-assignment-tracking donor and source-only reviews/enrollment; S7 actual proof/native failures and custody-only release. Not a portable execution frame or accepted result.',
    'source_change': 'Append -fno-var-tracking-assignments while preserving -O2/-g/-gnata and all compiler checks. Refresh only original affected GPR literal pins and source registration binding. Every executable source body, public contract, input domain and original proof/runtime obligation remains unchanged.',
    'actual_prior_proof': 'D8 original full strict target reached its unchanged child600 deadline and returned -15; original collector retained and released. No complete proof result or acceptance.',
    'actual_prior_native': 'N7 guard build, full144 native component tests and pending build passed. Main1000 expired during complete core build. Missing core child/scope/handshake waits remain UNKNOWN. Qualified custody receiver retained all source/private/generated evidence and actual cleanup, then released; no full build/runtime acceptance.',
    'current_source8_execution': 'D9 original full strict command launched on S8. At checkpoint preparation no terminal result was consumed; no proof pass is claimed. N8 matching full native/runtime campaign remains unrun.',
    'required_command_and_full_roster': 'Original full strict -U mode=all level3 report=all checks-as-errors/proof-warnings j2; all116 original ordered runtime actions and all required additions, current full127 modes and original authentic fixtures remain required on matching final source.',
    'full_strict_proof_acceptance': False, 'complete_original_runtime_acceptance': False,
    'protected_fixture_acceptance': False, 'ownership_acceptance': False, 'phase_one_complete': False,
    'remaining': ['Complete final native build', 'Full original strict proof with required body/caller coverage and no required unproved/justified/Assume', 'Complete original matching-source runtime and all additions', 'Ownership/reclamation and authentic protected/world actor fixtures', 'Independent final acceptance and accepted publication']}
mp = C / 'PHASE1-SOURCE-V8-CHECKPOINT-20261010-CODEX.json'
save(mp, manifest)
save(T / 'source-v8-checkpoint-staged-paths.json', [row['path'] for row in rows] + [mp.name])
print(json.dumps({'manifest': pin(mp), 'copied_files_observed': len(rows), 'phase_one_complete': False}))
