"""Retain corrected source and actual failed strict diagnostic; no acceptance."""
from pathlib import Path
import hashlib
import json
import shutil
import stat
import subprocess

T = Path(__file__).resolve().parent
C = T.parents[4] / 'worldline-checkpoint-20261010-f67/checkout'
PREFIX = Path('records/codex-resumption-20261007/codex-takeover-20261010')
V = T / 'integrated-candidate-v7'
D = T / 'formal-frame-successor-v7-draft'

def pin(path):
    assert path.is_file() and not path.is_symlink(), str(path)
    return {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'bytes': path.stat().st_size, 'mode': stat.S_IMODE(path.stat().st_mode)}

def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')

def verify_source():
    rows = json.loads((V / 'stable-source-inventory.json').read_text())
    actual = {str(p.relative_to(V / 'source')) for p in [V / 'source', *(V / 'source').rglob('*')]}
    assert actual == set(rows)
    for name, row in rows.items():
        p = V / 'source' / name
        assert not p.is_symlink() and stat.S_IMODE(p.stat().st_mode) == row['mode']
        if row['kind'] == 'file':
            assert pin(p) == {k: value for k, value in row.items() if k != 'kind'}

assert str(C) == '/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/worldline-checkpoint-20261010-f67/checkout'
assert subprocess.check_output(['git', 'status', '--porcelain'], cwd=C) == b''
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=C, text=True).strip()
assert head == 'd8c301dfa5fff06bf18e869f049fe9ae813ddb27'
review=json.loads((T/'frame-review-draft/integrated-v7-independent-source-review.json').read_text())
assert review['disposition']=='QUALIFIED_COHERENT_INTEGRATED_SOURCE_FOR_ORIGINAL_DIAGNOSTIC_PREPARATION_ONLY'
assert review['reviewer_agent']=='/root/acceptance_ultra'
assert review['artifacts']['source-selection.json']['sha256']==pin(V/'source-selection.json')['sha256']
verify_source()
files = sorted(p for p in V.rglob('*') if p.is_file())
for donor_name in ('physical-completion-integration-main-v3','canonical-exchange-owner-abi-donor-ultra-v1','excluded-owner-function-termination-legality-ultra-v1','excluded-owner-termination-progress-ultra-v1','original-physical-additive-proof-enrollment-ultra-v1'):
    files += sorted(p for p in (T/donor_name).rglob('*') if p.is_file())
files += [T/'frame-review-draft/integrated-v7-independent-source-review.json',T/'compose_candidate_v7.py',Path(__file__),T/'prepare_original_physical_restoration_main_v3.py',T/'freeze_original_physical_restoration_main_v3.py']
for folder in (D/'review/root-terminal-v1',D/'evidence/Main-owned-formal-observation-v1'):
    files += sorted(p for p in folder.rglob('*') if p.is_file())
for folder in sorted((D/'evidence').iterdir()):
    if not folder.is_dir() or folder.name=='Main-owned-formal-observation-v1':continue
    files += [p for p in folder.rglob('*') if p.is_file() and p.suffix in ('.json','.stdout','.stderr')]
files += [D/'source/obj/core/gnatprove/data_representation_generation.log',T/'acceptance-ultra-review-draft/excluded-owner-function-termination-valid-encoding-reference-v1.json']
files=sorted(set(files))
rows = []
for src in files:
    before = pin(src)
    dst = C / PREFIX / src.relative_to(T)
    assert not dst.exists(), str(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    assert pin(src) == before == pin(dst), str(src)
    rows.append({'path': str(dst.relative_to(C)), **before})
# Preserve and verify the complete published source directory modes as well.
expected = json.loads((V / 'stable-source-inventory.json').read_text())
published = C / PREFIX / 'integrated-candidate-v7/source'
for name, row in expected.items():
    if row['kind'] == 'directory':
        (published / name).chmod(row['mode'])
assert {str(p.relative_to(published)) for p in [published, *published.rglob('*')]} == set(expected)
for name, row in expected.items():
    p = published / name
    assert not p.is_symlink() and stat.S_IMODE(p.stat().st_mode) == row['mode']
    if row['kind'] == 'file':
        assert pin(p) == {k: value for k, value in row.items() if k != 'kind'}
verify_source()
manifest = {
    'schema': 'worldline-reviewed-source-v7-original-restoration-checkpoint-v1',
    'previous_public_commit': head, 'copied_files': rows,
    'source_selection_sha256': pin(V / 'source-selection.json')['sha256'],
    'complete_locally_staged_source_keyset_bytes_modes_exact': True,
    'git_mode_scope': 'Git records file blobs and its executable-file mode; recorded directory and other permission modes require the retained inventory and explicit reconstruction. This checkpoint is not an installed source custody or portable executable frame.',
    'scope': 'Complete reviewed integrated-v7 source, original physical/canonical/mapping/control/termination restoration donors and source-only enrollment/review records; unbuilt, unproved and unaccepted. Selected exact D7 failure/control/terminal records are retained; generated proof artifacts are not fully published and this is not a portable executable frame.',
    'source_change': 'Restore missing original complete physical exchange/recovery/durability implementation, canonical exchange/owner exports and mapping joins, original public header/control closure; preserve current per-call transaction and diagnostic guard, effect-material evidence and recovery witnesses. Correct ordinary function aspect legality without losing mandatory termination, add loop progress annotations, and enroll restored SPARK units additively. All original accepted domains, controls, contracts and proof gates remain required.',
    'prior_actual_failure': 'D7 original full strict command child1 without timeout, Main1; E0016 illegal explicit Always_Terminates on ordinary function; full body proof not reached. Original collector actual0 retained known failed terminal result and released ended owned scopes/window. N6 was held UNRUN after discovering omitted required original ABI/physical/control joins. Prior failures/checkpoints remain preserved.',
    'required_command_and_full_roster': 'Unchanged original full strict -U level3/checks-as-errors/proof-warnings/j2 proof and original ordered runtime116 plus2 additions, restored original physical/canonical semantic/ABI/mapping/syscall controls and complete original runtime/actor campaign remain required on matching source.',
    'full_strict_proof_acceptance': False, 'complete_original_runtime_acceptance': False,
    'protected_fixture_acceptance': False, 'phase_one_complete': False,
    'remaining': ['Complete matching-source native build and original runtime plus all required restored original controls', 'Full original strict proof', 'Authentic protected and actor fixtures', 'Final independent acceptance and publication']}
mp = C / 'PHASE1-SOURCE-V7-CHECKPOINT-20261010-CODEX.json'
save(mp, manifest)
save(T / 'source-v7-checkpoint-staged-paths.json', [row['path'] for row in rows] + [mp.name])
print(json.dumps({'manifest': pin(mp), 'copied_files': len(rows), 'phase_one_complete': False}))
