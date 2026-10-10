"""Compose reviewed source donors; never execute a WORLDLINE target."""
from pathlib import Path
import ast
import hashlib
import json
import os
import shutil
import stat
import subprocess

T = Path(__file__).resolve().parent
P = T / 'integrated-candidate-v8'
C = T / 'integrated-candidate-v9'
MANIFEST = 'runtime/worldline/proof_manifest.py'
REGISTRATION = 'protected-root/controls/source_registration.json'
DONORS = [
    ('compiler-reference-no-inline-donor-ultra-v1', 'source-author-packet-v1.json',
     'QUALIFIED_EXACT_COMPILER_ONLY_REFERENCE_NO_INLINE_COST_DONOR_SOURCE_ONLY'),
    ('compress-explicit-contract-cost-donor-ultra-v1', 'source-author-packet-v1.json',
     'QUALIFIED_EXACT_PRESERVED_BODY_COMPRESS_CONTRACT_COST_DONOR_SOURCE_ONLY'),
    ('authentic-original-prefix-sha-donor-ultra-v1', 'AUTHOR-PACKET.json',
     'QUALIFIED_EXACT_AUTHENTIC_ORIGINAL_PREFIX_SHA_PRODUCER_BINDING_SOURCE_ONLY'),
    ('authentic-front-eio-arm-donor-ultra-v2', 'AUTHOR-PACKET.json',
     'QUALIFIED_EXACT_AUTHENTIC_NATIVE_FAULT_ARM_AND_TERMINAL_SOURCE_ONLY'),
]


def load(p):
    return json.loads(Path(p).read_text())


def pin(p):
    p = Path(p)
    a = p.lstat()
    assert stat.S_ISREG(a.st_mode) and not p.is_symlink()
    data = p.read_bytes()
    b = p.lstat()
    identity = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    assert identity(a) == identity(b)
    return {'path': str(p), 'sha256': hashlib.sha256(data).hexdigest(),
            'bytes': b.st_size, 'mode': stat.S_IMODE(b.st_mode)}


def verify_pins(v):
    if isinstance(v, dict):
        if set(('path', 'sha256', 'bytes', 'mode')) <= set(v):
            actual = pin(v['path'])
            assert all(actual[k] == v[k] for k in actual), v['path']
        else:
            for child in v.values():
                verify_pins(child)
    elif isinstance(v, list):
        for child in v:
            verify_pins(child)


def save(p, v):
    with Path(p).open('x') as f:
        json.dump(v, f, indent=2, sort_keys=True)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())


def snapshot(root):
    out = {}
    for p in [root, *sorted(root.rglob('*'))]:
        s = p.lstat()
        assert not p.is_symlink()
        assert stat.S_ISREG(s.st_mode) or stat.S_ISDIR(s.st_mode)
        row = {'kind': 'directory' if p.is_dir() else 'file', 'mode': stat.S_IMODE(s.st_mode)}
        if row['kind'] == 'file':
            row.update({k: v for k, v in pin(p).items() if k in ('sha256', 'bytes')})
        out[str(p.relative_to(root))] = row
    return out


def donor_files(directory, packet):
    if 'preimages' in packet and 'postimages' in packet:
        pre, post = packet['preimages'], packet['postimages']
        names = packet.get('permitted_names', sorted(post))
        assert set(pre) == set(post) == set(names)
        return {name: (Path(pre[name]['path']), Path(post[name]['path'])) for name in names}
    names = packet['permitted_names']
    return {name: (directory / 'preimage' / name, directory / 'source' / name) for name in names}


def roster(root):
    tree = ast.parse((root / MANIFEST).read_text())
    namespace = {}
    for stmt in tree.body:
        if isinstance(stmt, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'REQUIRED_PROVED' for t in stmt.targets):
            namespace['REQUIRED_PROVED'] = ast.literal_eval(stmt.value)
        elif isinstance(stmt, ast.AugAssign) and isinstance(stmt.target, ast.Name) and stmt.target.id == 'REQUIRED_PROVED':
            assert isinstance(stmt.op, ast.Add)
            namespace['REQUIRED_PROVED'] += ast.literal_eval(stmt.value)
    return list(namespace['REQUIRED_PROVED'])


def main():
    assert __debug__ and not C.exists()
    before = snapshot(P / 'source')
    assert before == load(P / 'stable-source-inventory.json')
    source_review = T / 'frame-review-draft/integrated-v8-independent-source-review.json'
    assert load(source_review)['disposition'] == 'QUALIFIED_COHERENT_INTEGRATED_SOURCE_FOR_ORIGINAL_DIAGNOSTIC_PREPARATION_ONLY'
    qualified = []
    changes = {}
    for directory_name, packet_name, disposition in DONORS:
        directory = T / directory_name
        packet_path = directory / packet_name
        opinion_path = directory / 'independent-source-review.json'
        packet, opinion = load(packet_path), load(opinion_path)
        expected_disposition = disposition or packet['requested_disposition']
        assert opinion['disposition'] == expected_disposition
        assert opinion.get('blocking_findings', []) == []
        packet_binding = opinion.get('source_author_packet', opinion.get('author_packet'))
        assert packet_binding == pin(packet_path)
        verify_pins(packet)
        if 'author_freeze' in packet:
            verify_pins(load(packet['author_freeze']['path']))
        files = donor_files(directory, packet)
        for name, (pre, post) in files.items():
            assert all(pin(pre)[k] == pin(P / 'source' / name)[k] for k in ('sha256', 'bytes', 'mode')), name
            assert pin(pre)['mode'] == pin(post)['mode']
            if name == MANIFEST:
                # Both donors share an exact S8 manifest preimage. The Compress
                # postimage retains the explicit additive helper enrollment;
                # original normalizer refreshes the union of digest literals.
                if directory_name == 'compress-explicit-contract-cost-donor-ultra-v1':
                    changes[name] = post
            else:
                assert name not in changes, name
                changes[name] = post
        qualified.append({'packet': pin(packet_path), 'opinion': pin(opinion_path),
                          'files': {n: {'preimage': pin(a), 'postimage': pin(b)} for n, (a, b) in files.items()}})
    assert MANIFEST in changes
    old_roster = roster(P / 'source')
    shutil.copytree(P / 'source', C / 'source')
    assert snapshot(C / 'source') == before
    for name, post in changes.items():
        shutil.copy2(post, C / 'source' / name)
    for mode, report in [('write', 'pin-refresh-source-observation.json'), ('check', 'pin-check-source-observation.json')]:
        argv = ['/usr/bin/python3', '-B', str(C / 'source/refresh_contract_pins.py'),
                '--' + mode, '--root', str(C / 'source'), '--report', str(C / report)]
        r = subprocess.run(argv, capture_output=True)
        (C / ('pin-' + mode + '.stdout')).write_bytes(r.stdout)
        (C / ('pin-' + mode + '.stderr')).write_bytes(r.stderr)
        save(C / ('pin-' + mode + '-command.json'), {'argv': argv, 'returncode': r.returncode, 'target_execution': False})
        assert r.returncode == 0
        refreshed = load(C / report)['changed']
        assert (all(row['path'].partition('#')[0] in changes for row in refreshed) if mode == 'write' else refreshed == [])
    added = ['Attest.SHA256.Compress', 'Attest.Custody_SHA256.Compress']
    assert roster(C / 'source') == old_roster + added
    registration = C / 'source' / REGISTRATION
    reg = load(registration)
    mapping = reg['fixed_excluded_source_owner']['affected_source_sha256']
    reg_changes = {n: {'before': old, 'after': pin(C / 'source' / n)['sha256']}
                   for n, old in mapping.items() if old != pin(C / 'source' / n)['sha256']}
    assert set(reg_changes) <= set(changes)
    for name, row in reg_changes.items():
        mapping[name] = row['after']
    reg['codex_source9_reviewed_cost_and_authentic_fixture_source_binding'] = {
        'source_only': True, 'preimage_registration': pin(P / 'source' / REGISTRATION),
        'changes': reg_changes, 'qualified_donors': qualified,
        'proof_runtime_or_phase_acceptance': False,
        'actual_operator_policy_recovery_symbol_selection': None}
    registration.write_text(json.dumps(reg, indent=2) + '\n')
    after = snapshot(C / 'source')
    changed = {n for n in set(before) | set(after) if before.get(n) != after.get(n)}
    assert changed == set(changes) | {REGISTRATION}
    direct = [{'path': n, 'before': before.get(n), 'after': after.get(n)} for n in sorted(changed)]
    base = load(T.parent / 'phase1-integrated-v67-draft/stable-source-inventory.json')
    delta = [{'path': n, 'before': base.get(n), 'after': after.get(n)}
             for n in sorted(set(base) | set(after)) if base.get(n) != after.get(n)]
    save(C / 'stable-source-inventory.json', after)
    save(C / 'source-inventory.json', {n: {k: v for k, v in row.items() if k != 'bytes'} for n, row in after.items()})
    save(C / 'source-changes.json', delta)
    save(C / 'source8-to-source9-delta.json', direct)
    save(C / 'coherent-cost-and-fixture-source-integration.json', {
        'schema': 'worldline-exact-qualified-source9-composition-v1',
        'predecessor_selection': pin(P / 'source-selection.json'),
        'predecessor_review': pin(source_review), 'qualified_donors': qualified,
        'complete_direct_delta': pin(C / 'source8-to-source9-delta.json'),
        'registration_changes': reg_changes, 'preimage_registration': pin(P / 'source' / REGISTRATION),
        'postimage_registration': pin(registration), 'original_required_proved': old_roster,
        'added_complete_private_helpers': added,
        'scope': 'Compiler-only No_Inline, explicit unchanged-body private helper contracts with complete additive proof enrollment, authentic prefix hash producer binding and authentic native fault arming/deferred terminal observation. Original source contracts, accepted domains, full callers, proof floor, sole C API boundary, runtime cases/order/caps and fault outcomes remain mandatory. Effectiveness and all matching-source execution/acceptance remain open.',
        'target_execution': False, 'proof_acceptance': False, 'runtime_acceptance': False, 'phase_acceptance': False})
    argv = ['/usr/bin/python3', '-B', str(T.parent / 'proof-enrollment-repair-v49/collect_enrollment_report.py'),
            '--root', str(C / 'source'), '--output', str(C / 'enrollment-report.json'),
            '--pin-refresh-report', str(C / 'pin-refresh-source-observation.json')]
    r = subprocess.run(argv, capture_output=True)
    (C / 'enrollment.stdout').write_bytes(r.stdout)
    (C / 'enrollment.stderr').write_bytes(r.stderr)
    save(C / 'enrollment-collection-invocation.json', {'schema': 'worldline-original-source-only-enrollment-collector-invocation-v1',
        'argv': argv, 'returncode': r.returncode, 'stdout': pin(C / 'enrollment.stdout'), 'stderr': pin(C / 'enrollment.stderr'),
        'source_mutated': False, 'target_execution': False, 'proof_acceptance': False, 'phase_acceptance': False, 'collector_guard_unchanged': True})
    assert r.returncode == 0 and snapshot(C / 'source') == after
    selection = load(P / 'source-selection.json')
    selection.update(source=str(C / 'source'), source_inventory=pin(C / 'source-inventory.json'),
        stable_source_inventory=pin(C / 'stable-source-inventory.json'), source_changes=pin(C / 'source-changes.json'),
        complete_original_f67_to_current_delta=pin(C / 'source-changes.json'), source8_to_source9_delta=pin(C / 'source8-to-source9-delta.json'),
        coherent_cost_and_fixture_source_integration=pin(C / 'coherent-cost-and-fixture-source-integration.json'),
        preserved_full_strict_timeout_source_selection=pin(P / 'source-selection.json'),
        pin_check_source_observation=pin(C / 'pin-check-source-observation.json'), all_literal_pin_check=pin(C / 'pin-check-source-observation.json'),
        pin_refresh_source_observation=pin(C / 'pin-refresh-source-observation.json'), all_literal_pin_refresh=pin(C / 'pin-refresh-source-observation.json'),
        source_only_enrollment=pin(C / 'enrollment-report.json'), enrollment_collection_invocation=pin(C / 'enrollment-collection-invocation.json'),
        enrollment_source_delta=pin(C / 'enrollment-report.source.patch'),
        reviews='Predecessor coherent source and every selected donor have independent source-only opinions. Complete coherent composition and all matching-source execution and final acceptance remain mandatory.',
        proof_acceptance=False, runtime_acceptance=False, phase_acceptance=False)
    save(C / 'source-selection.json', selection)
    assert snapshot(P / 'source') == before
    print(json.dumps({'selection': pin(C / 'source-selection.json'), 'direct_delta': pin(C / 'source8-to-source9-delta.json'),
        'enrollment': pin(C / 'enrollment-report.json'), 'changed_paths': sorted(changed),
        'target_execution': False, 'proof_acceptance': False, 'runtime_acceptance': False, 'phase_acceptance': False}))


if __name__ == '__main__':
    main()
