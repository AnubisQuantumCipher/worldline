"""Preserve complete reviewed S9 and its actual failed build as an unaccepted checkpoint.

This copies selected source and evidence to the isolated publication checkout.
It does not stage, commit, push, install, release or claim Phase One completion.
Complete raw campaign evidence remains in the original local owned candidate.
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
V = T / 'integrated-candidate-v9'
N = T / 'runtime-frame-successor-v9-ultra-v1-draft/candidate'


def pin(path):
    path = Path(path)
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


def verify_source(root):
    expected = json.loads((V / 'stable-source-inventory.json').read_text())
    assert {str(path.relative_to(root)) for path in [root, *root.rglob('*')]} == set(expected)
    for name, row in expected.items():
        path = root / name
        assert not path.is_symlink() and stat.S_IMODE(path.stat().st_mode) == row['mode']
        if row['kind'] == 'file':
            assert pin(path) == {key: value for key, value in row.items() if key != 'kind'}


assert __debug__
assert subprocess.check_output(['git', 'status', '--porcelain'], cwd=C) == b''
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=C, text=True).strip()
assert head == 'c65b8482672b78cb00f70f927006f98d49df10f9'
assert pin(V / 'source-selection.json')['sha256'] == '6856fcd0b0e2a8eb7a43d6893c744521f56412927ee0b6b1af1b2e8808cbe8a1'
review = T / 'frame-review-draft/integrated-v9-independent-source-review.json'
assert pin(review)['sha256'] == 'b7e423dac48b6c611f288625cb88f27b8ca4fccc4d67f7f9042a245d8760d9de'
terminal_path = N / 'review/root-batch-terminal-v1/actual-results-and-window-release.json'
terminal = json.loads(terminal_path.read_text())
assert terminal['all_required_actual_pass'] is False
build = json.loads((N / 'evidence/build-v1/result.json').read_text())
assert build['scope_wait'] == 4 and build['child_wait']['returncode'] == 4
assert build['inputs_unchanged'] is True
verify_source(V / 'source')
files = sorted(path for path in V.rglob('*') if path.is_file())
for name in ['compiler-reference-no-inline-donor-ultra-v1',
             'compress-explicit-contract-cost-donor-ultra-v1',
             'authentic-original-prefix-sha-donor-ultra-v1',
             'authentic-front-eio-arm-donor-ultra-v2']:
    files += sorted(path for path in (T / name).rglob('*') if path.is_file())
files += [review, T / 'compose_candidate_v9.py', Path(__file__).resolve(),
          T / 'acceptance-ultra-review-draft/source9-original-drain-registration-independent-gap-v1.json',
          T / 'acceptance-ultra-review-draft/native-v9-tail-current-binding-operand-independent-HOLD-v1.json',
          T / 'acceptance-ultra-review-draft/original-phase-one-matrix-v4-source9-current-preparation-supplement-v1.json']
for name in ['evidence/Main-original-qualified-prefix-execution-v1/Main-complete-owned-prefix-observation.json',
             'evidence/build-v1/result.json', 'evidence/build-v1/child-wait.json',
             'evidence/build-v1/child.stderr', 'evidence/build-v1/child.stdout',
             'evidence/native-build-v1/result.json',
             'evidence/native-component-tests-v1/result.json',
             'evidence/native-component-tests-v1/child.stderr',
             'evidence/pending-build-v1/result.json',
             'review/root-batch-terminal-v1/actual-results-and-window-release.json',
             'review/root-batch-terminal-v1/coordination-release.json',
             'review/root-batch-terminal-v1/outer-capture-observations.json',
             'review/root-batch-terminal-v1/owned-terminal-observations.json',
             'review/root-batch-terminal-v1/complete-source-readback.json',
             'review/root-batch-terminal-v1/private-source-dependency-readback.json',
             'review/root-batch-terminal-v1/retained-artifacts.json']:
    files.append(N / name)
files = sorted(set(files))
rows = []
for source in files:
    before = pin(source)
    destination = C / PREFIX / source.relative_to(T)
    if destination.exists():
        assert pin(destination) == before, str(destination)
        continue
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    assert pin(source) == before == pin(destination), str(source)
    rows.append({'path': str(destination.relative_to(C)), **before})
published = C / PREFIX / 'integrated-candidate-v9/source'
for name, row in json.loads((V / 'stable-source-inventory.json').read_text()).items():
    if row['kind'] == 'directory':
        (published / name).chmod(row['mode'])
verify_source(published)
verify_source(V / 'source')
manifest = {
    'schema': 'worldline-reviewed-source9-actual-failed-build-checkpoint-v1',
    'previous_public_commit': head, 'copied_files': rows,
    'complete_local_and_copied_source_keyset_bytes_modes_exact': True,
    'scope': 'Complete source-only reviewed S9, selected cost and authentic-fixture source donors, original N9 failed complete build and exact collector/release records. Unaccepted engineering checkpoint; no portable execution frame or complete backup claim.',
    'actual_core_build': 'Original gprbuild child/scope/outer returned4. evaluation_finalization.ads408 mixes ghost/non-ghost No_Inline operands; ghost operand errors409/410. The build did not reach the earlier stall.',
    'actual_partial_prefix': 'Original native guard build, full144 native component tests and pending-entry build passed with actual child/scope/outer0. All dependent remaining original actions are unrun and retained.',
    'cost_repair_efficacy': 'UNPROVEN: compiler failure precedes original stalled code.',
    'complete_original_action_roster': 'All116 original ordered actions and all required additions, current complete127; original accepted/refusal/fault controls, strict full-U proof floor/body/callers and authentic actor/fixture obligations remain unchanged.',
    'actual_original_terminal': terminal['status'],
    'actual_original_unknown_labels': terminal['unknown'],
    'source9_front_reader_gap': 'Original subject-reader registration lacks an evidenced current producer caller; authentic transfer/drain/reclamation remain open.',
    'source9_tail_wrapper': 'Original unrun NT9 wrapper selects pending bindings and is independently HOLD. Disjoint corrected wrapper requires its own exact emitted qualification; failed prefix gives no compiled continuation.',
    'git_mode_boundary': 'Copy comparison preserves local source file modes. Git records regular versus executable blobs, not all POSIX permissions; no private-file mode claim is made about Git.',
    'full_raw_evidence_boundary': 'Original raw source/private/generated/compiler/native/control evidence remains retained locally in the owned candidate. Selected failure and summary records are copied here; absolute historical paths are provenance, not portable executable authority.',
    'full_strict_proof_acceptance': False, 'complete_original_runtime_acceptance': False,
    'protected_fixture_acceptance': False, 'ownership_acceptance': False,
    'independent_final_acceptance': False, 'phase_one_complete': False,
    'remaining': ['Successful complete final source build', 'Full original strict proof',
                  'Complete original matching-source runtime and additions',
                  'Ownership/reclamation and authentic protected fixtures',
                  'Independent final acceptance and accepted publication']}
manifest_path = C / 'PHASE1-SOURCE-V9-FAILED-BUILD-CHECKPOINT-20261010-CODEX.json'
save(manifest_path, manifest)
save(T / 'source-v9-failed-build-checkpoint-staged-paths.json',
     [row['path'] for row in rows] + [manifest_path.name])
print(json.dumps({'manifest': pin(manifest_path), 'copied_files_observed': len(rows),
                  'phase_one_complete': False}, sort_keys=True))
