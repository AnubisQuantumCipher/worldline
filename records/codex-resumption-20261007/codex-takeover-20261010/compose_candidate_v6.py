"""Compose the retained compile repair without changing its predecessor source."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import stat
import subprocess

T = Path(__file__).resolve().parent
P = T / 'integrated-candidate-v5'
C = T / 'integrated-candidate-v6'
F = T.parent / 'phase1-integrated-v67-draft'

def pin(path):
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode) and not path.is_symlink()
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    after = path.lstat()
    assert (before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
    return {'path': str(path), 'sha256': digest, 'bytes': after.st_size,
            'mode': stat.S_IMODE(after.st_mode)}

def load(path):
    return json.loads(path.read_text())

def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')

def snapshot(root):
    result = {}
    for path in [root, *sorted(root.rglob('*'))]:
        info = path.lstat()
        assert not path.is_symlink()
        row = {'kind': 'directory' if stat.S_ISDIR(info.st_mode) else 'file',
               'mode': stat.S_IMODE(info.st_mode)}
        if row['kind'] == 'file':
            row.update({k: v for k, v in pin(path).items() if k in ('sha256', 'bytes')})
        result[str(path.relative_to(root))] = row
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--donor', type=Path, required=True)
    parser.add_argument('--review', type=Path, required=True)
    args = parser.parse_args()
    donor = args.donor.resolve(strict=True)
    review_pin = pin(args.review.resolve(strict=True))
    assert __debug__ and not C.exists()
    before = snapshot(P / 'source')
    assert before == load(P / 'stable-source-inventory.json')
    names = sorted(str(p.relative_to(donor / 'source')) for p in (donor / 'source').rglob('*') if p.is_file())
    permitted = {'core/worldline-excluded_source_owner.adb'}
    assert names and set(names) <= permitted
    assert set(names) == permitted
    donor_rows = {}
    for name in names:
        preimage = donor / 'preimages' / name
        assert pin(preimage)['sha256'] == pin(P / 'source' / name)['sha256']
        donor_rows[name] = {'preimage': pin(preimage), 'postimage': pin(donor / 'source' / name)}
    shutil.copytree(P / 'source', C / 'source')
    assert snapshot(C / 'source') == before
    for name in names:
        shutil.copy2(donor / 'source' / name, C / 'source' / name)
        assert pin(C / 'source' / name)['sha256'] == donor_rows[name]['postimage']['sha256']
    for mode, report in [('write', 'pin-refresh-source-observation.json'), ('check', 'pin-check-source-observation.json')]:
        argv = ['/usr/bin/python3', '-B', str(C / 'source/refresh_contract_pins.py'), '--' + mode,
                '--root', str(C / 'source'), '--report', str(C / report)]
        result = subprocess.run(argv, capture_output=True)
        (C / ('pin-' + mode + '.stdout')).write_bytes(result.stdout)
        (C / ('pin-' + mode + '.stderr')).write_bytes(result.stderr)
        save(C / ('pin-' + mode + '-command.json'), {'argv': argv, 'returncode': result.returncode, 'target_execution': False})
        assert result.returncode == 0
    registration = C / 'source/protected-root/controls/source_registration.json'
    reg = load(registration)
    mapping = reg['fixed_excluded_source_owner']['affected_source_sha256']
    changed = {name: {'before': old, 'after': pin(C / 'source' / name)['sha256']}
               for name, old in mapping.items() if old != pin(C / 'source' / name)['sha256']}
    assert set(changed) <= permitted | {'runtime/worldline/proof_manifest.py'}
    for name, row in changed.items():
        mapping[name] = row['after']
    reg['codex_excluded_owner_compile_repair_binding'] = {'source_only': True, 'preimage_registration': pin(P / 'source/protected-root/controls/source_registration.json'),
        'changes': changed, 'proof_runtime_or_phase_acceptance': False}
    registration.write_text(json.dumps(reg, indent=2) + '\n')
    argv = ['/usr/bin/python3', '-B', str(C / 'source/refresh_contract_pins.py'), '--check',
            '--root', str(C / 'source'), '--report', str(C / 'pin-check-final-source-observation.json')]
    checked = subprocess.run(argv, capture_output=True)
    (C / 'pin-check-final.stdout').write_bytes(checked.stdout)
    (C / 'pin-check-final.stderr').write_bytes(checked.stderr)
    save(C / 'pin-check-final-command.json', {'argv': argv, 'returncode': checked.returncode, 'target_execution': False})
    assert checked.returncode == 0
    after = snapshot(C / 'source')
    assert set(before) == set(after)
    changed_names = {n for n in before if before[n] != after[n]}
    assert changed_names <= permitted | {'runtime/worldline/proof_manifest.py', 'protected-root/controls/source_registration.json'}
    base = load(F / 'stable-source-inventory.json')
    delta = [{'path': n, 'before': base.get(n), 'after': after.get(n)} for n in sorted(set(base) | set(after)) if base.get(n) != after.get(n)]
    save(C / 'stable-source-inventory.json', after)
    save(C / 'source-inventory.json', {n: {k: v for k, v in row.items() if k != 'bytes'} for n, row in after.items()})
    save(C / 'source-changes.json', delta)
    save(C / 'compile-repair-integration.json', {'donors': donor_rows, 'affected_donor_review': review_pin,
        'predecessor_selection': pin(P / 'source-selection.json'), 'current_registration_changes': changed,
        'preimage_registration': pin(P / 'source/protected-root/controls/source_registration.json'),
        'postimage_registration': pin(registration),
        'changed_paths': sorted(changed_names), 'target_execution': False, 'phase_acceptance': False})
    selection = load(P / 'source-selection.json')
    for name in ('source_only_enrollment', 'enrollment_collection_invocation', 'enrollment_source_delta', 'complete_original_f67_to_current_delta'):
        selection.pop(name, None)
    selection.update(source=str(C / 'source'), source_inventory=pin(C / 'source-inventory.json'),
        stable_source_inventory=pin(C / 'stable-source-inventory.json'), source_changes=pin(C / 'source-changes.json'),
        compile_repair_integration=pin(C / 'compile-repair-integration.json'), preserved_compile_failure_candidate=pin(P / 'source-selection.json'),
        registration_binding_change=pin(C / 'compile-repair-integration.json'),
        pin_check_source_observation=pin(C / 'pin-check-final-source-observation.json'), all_literal_pin_check=pin(C / 'pin-check-final-source-observation.json'),
        pin_refresh_source_observation=pin(C / 'pin-refresh-source-observation.json'), all_literal_pin_refresh=pin(C / 'pin-refresh-source-observation.json'),
        reviews='Retained donor opinions remain limited to their exact scope. This composed source needs affected integrated review and original matching-source execution.')
    save(C / 'source-selection.json', selection)
    assert snapshot(P / 'source') == before
    assert pin(args.review.resolve()) == review_pin
    print(json.dumps({'selection': pin(C / 'source-selection.json'), 'changed_paths': sorted(changed_names),
                      'target_execution': False, 'phase_acceptance': False}, sort_keys=True))

if __name__ == '__main__':
    main()
