"""Copy reviewed source and selected actual failed-campaign evidence for publication.

This is an unaccepted checkpoint. It does not stage, commit, push, install,
release, execute a target, or claim a portable execution frame/full backup.
"""
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
N = T / 'runtime-frame-successor-v10-ultra-v1-draft/candidate'
D = T / 'formal-frame-successor-v11-draft'


def pin(path):
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode) and not path.is_symlink(), str(path)
    with path.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    after = path.lstat()
    identity = lambda row: (row.st_dev, row.st_ino, row.st_mode, row.st_size,
                            row.st_mtime_ns, row.st_ctime_ns)
    assert identity(before) == identity(after), str(path)
    return {'sha256': digest, 'bytes': after.st_size,
            'mode': stat.S_IMODE(after.st_mode)}


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())


def verify_source(root, inventory):
    assert {str(path.relative_to(root)) for path in [root, *root.rglob('*')]} == set(inventory)
    for name, row in inventory.items():
        path = root / name
        assert not path.is_symlink() and stat.S_IMODE(path.stat().st_mode) == row['mode']
        if row['kind'] == 'file':
            assert pin(path) == {key: value for key, value in row.items() if key != 'kind'}
        else:
            assert row['kind'] == 'directory' and path.is_dir()


assert __debug__
assert subprocess.check_output(['git', 'status', '--porcelain'], cwd=C) == b''
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=C, text=True).strip()
assert head == 'c3f43d7bb0b69da79f96ba1c7b4b2cd9d13f8084'
fixed_reviews = {
    'frame-review-draft/integrated-v10-independent-source-review.json': '80203cf6170cf998fb37858bd1eef6a34478b2e9797ce1c28f4d74f18fad76f9',
    'frame-review-draft/integrated-v11-independent-source-review.json': '72d2d25ab33456875019d9491f7d7df3115054d0a854ae068111a2499f24d729',
    'protected-ultra-review-draft/native-v10-actual-failed-entry-suite-terminal-release-independent-observation-v1.json': 'e6408e8f6232595e171ee753d9f8e77d2c7a22f001b7165520deaf4b0f65cdba',
    'acceptance-ultra-review-draft/formal-v11-actual-deadline-terminal-release-independent-observation-v1.json': '5c400f9de5ec2821e9c5efb47a5a0d78ccf2d3429432bfdbabf05747e24bab1f',
    'acceptance-ultra-review-draft/original-phase-one-matrix-current-annotations-v6-source11.json': '839ddf9476a464597569193aa2471f30f341f58db98ef41358759a67ff2801f0',
    'actual-formal11-terminal-source11-qualified-root-routing-v1.json': '94bc6a16b8b8c9cfc92c9f88f37a0f607bd09de1245d34d6e955716a13dd7677',
}
files = []
inventories = {}
for version, expected in [('integrated-candidate-v10', '28a0371577f09805c70c10d05d2231c6d716f2ef42c5d536d5fffb9d84538e28'),
                          ('integrated-candidate-v11', 'baac9509488f0ad7f76b5b4130d21f53e46439f9c30311a6eb0303761a5ca60e')]:
    V = T / version
    assert pin(V / 'source-selection.json')['sha256'] == expected
    inventory = json.loads((V / 'stable-source-inventory.json').read_text())
    verify_source(V / 'source', inventory)
    inventories[version] = inventory
    files += sorted(path for path in V.rglob('*') if path.is_file())
for name, expected in fixed_reviews.items():
    path = T / name
    actual = pin(path)
    if expected is not None:
        assert actual['sha256'] == expected, str(path)
    files.append(path)
for label in ['native-build-v1', 'native-component-tests-v1', 'pending-build-v1', 'build-v1', 'entry-component-tests-v1']:
    for leaf in ['result.json', 'child-wait.json', 'child.stdout', 'child.stderr']:
        files.append(N / 'evidence' / label / leaf)
for base, main, terminal_dir in [
        (N, 'Main-original-qualified-prefix-execution-v1/Main-complete-owned-prefix-observation.json', 'root-batch-terminal-v1'),
        (D, 'Main-owned-formal-observation-v1/Main-complete-owned-formal-observation.json', 'root-terminal-v1')]:
    files.append(base / 'evidence' / main)
    for leaf in ['actual-results-and-window-release.json', 'coordination-release.json']:
        files.append(base / 'review' / terminal_dir / leaf)
for leaf in ['result.json', 'child-wait.json', 'child.stdout', 'child.stderr']:
    files.append(D / 'evidence/full-strict-formal-diagnostic-v1' / leaf)
files.append(Path(__file__).resolve())
native_terminal = json.loads((N / 'review/root-batch-terminal-v1/actual-results-and-window-release.json').read_text())
formal_terminal = json.loads((D / 'review/root-terminal-v1/actual-results-and-window-release.json').read_text())
assert native_terminal['all_required_actual_pass'] is False
assert formal_terminal['all_required_actual_pass'] is False
assert formal_terminal['failed'] == ['full-strict-formal-diagnostic']
build = json.loads((N / 'evidence/build-v1/result.json').read_text())
assert build['child_wait']['returncode'] == 0 and build['scope_wait'] == 0 and build['inputs_unchanged'] is True
entry = json.loads((N / 'evidence/entry-component-tests-v1/result.json').read_text())
assert entry['child_wait']['returncode'] == 1 and entry['scope_wait'] == 1 and entry['inputs_unchanged'] is True
strict_wait = json.loads((D / 'evidence/full-strict-formal-diagnostic-v1/child-wait.json').read_text())
assert strict_wait['returncode'] == -15 and strict_wait['timeout'] is True and strict_wait['stop_reason'] == 'deadline'
rows = []
for source in sorted(set(files)):
    before = pin(source)
    destination = C / PREFIX / source.relative_to(T)
    if destination.exists():
        assert pin(destination) == before, str(destination)
        continue
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    assert pin(source) == before == pin(destination), str(source)
    rows.append({'path': str(destination.relative_to(C)), **before})
for version, inventory in inventories.items():
    copied = C / PREFIX / version / 'source'
    for name, row in inventory.items():
        if row['kind'] == 'directory':
            (copied / name).chmod(row['mode'])
    verify_source(copied, inventory)
    verify_source(T / version / 'source', inventory)
manifest = {
    'schema': 'worldline-source11-actual-original-campaign-failures-checkpoint-v1',
    'previous_public_commit': head, 'copied_files': rows,
    'complete_selected_source_keysets_bytes_modes_exact': True,
    'scope': 'Complete source-only reviewed S10/S11 and selected actual N10/D11 failures plus exact independent terminal reviews. Unaccepted engineering checkpoint; no portable execution frame or complete backup claim.',
    'actual_source10_build': 'Original core gprbuild completed with child/scope/outer0. The original native guard build, native component suite and pending build also completed. Other project builds and final changed source are not accepted.',
    'actual_source10_entry_suite': 'Original entry suite ran202 tests and failed with7 failures and6 errors; child/scope/outer1. Complete original remaining action list stays UNRUN. Every original failure and collector label is retained.',
    'actual_source10_full_strict_proof': 'Original full-U strict command reached proof, then hit the original deadline: actual child-15/timeout, failed outer and released window. Complete gnatprove.out absent; whole-project proved/unproved/unknown/assumed/justified/suppressed counts UNKNOWN.',
    'source11_status': 'Managed, composed ledger, canonical owner and subject-reader source repairs independently reviewed and coherently integrated only. Actual matching-source build/proof/runtime/protected/ownership acceptance remains OPEN.',
    'native_unknown_labels': native_terminal['unknown'],
    'native_unrun': native_terminal['unrun'],
    'formal_failed': formal_terminal['failed'], 'formal_unknown': formal_terminal['unknown'],
    'matrix': 'All original seven Phase One areas remain OPEN with unchanged original requirements.',
    'git_mode_boundary': 'Local copy comparison preserves source POSIX modes. Git preserves regular/executable blob distinction, not all POSIX permissions; no private-file mode claim is made about Git.',
    'raw_evidence_boundary': 'Complete original raw source/private/generated/native/compiler/control artifacts remain retained locally. Selected exact outcomes and full independent failure reviews are copied; historical absolute paths are provenance, not portable executable authority.',
    'full_strict_proof_acceptance': False, 'complete_original_runtime_acceptance': False,
    'protected_fixture_acceptance': False, 'ownership_acceptance': False,
    'independent_final_acceptance': False, 'phase_one_complete': False,
    'remaining': ['Successful complete final source build', 'Full original strict proof',
                  'Complete original matching-source runtime and additions',
                  'Ownership/reclamation and authentic protected fixtures',
                  'Independent final acceptance and accepted publication'],
}
manifest_path = C / 'PHASE1-SOURCE11-ACTUAL-FAILURES-CHECKPOINT-20261010-CODEX.json'
save(manifest_path, manifest)
save(T / 'source11-actual-failures-checkpoint-staged-paths.json',
     [row['path'] for row in rows] + [manifest_path.name])
print(json.dumps({'manifest': pin(manifest_path), 'copied_files_observed': len(rows),
                  'phase_one_complete': False}, sort_keys=True))
