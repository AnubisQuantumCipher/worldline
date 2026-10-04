"""Self-test of w1proto.py (ENGINEERING_ONLY; same-user simulation; no privileges, no WORLDLINE code, no prover or
compiler, no systemd-run). Usage: selftest_w1proto.py NEW_OUTPUT_DIR"""
import base64, hashlib, io, json, os, subprocess, sys, textwrap
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import w1proto as P   # noqa: E402

SC = Path(sys.argv[1])
assert not SC.exists()
SC.mkdir(parents=True)
os.umask(0o077)
results, failures = {}, []


def expect(label, fn, refused=False, want=None):
    try:
        value = fn()
    except P.Refused as caught:
        results[label] = 'refused: %s: %s' % (type(caught).__name__, caught)
        if not refused:
            failures.append(label)
        return None
    except BaseException as caught:
        results[label] = 'ERROR: %s: %s' % (type(caught).__name__, caught)
        failures.append(label)
        return None
    if refused:
        results[label] = 'NOT REFUSED: %r' % (value,)
        failures.append(label)
        return value
    results[label] = 'ok' if want is None else value
    if want is not None and value != want:
        results[label] = {'UNEXPECTED': value, 'wanted': want}
        failures.append(label)
    return value


# ---------------------------------------------------------------- lease
lease_dir = SC / 'lease'
lease_dir.mkdir(mode=0o700)
(lease_dir / 'writer.lock').write_bytes(b'')
os.chmod(lease_dir / 'writer.lock', 0o600)
dfd = os.open(lease_dir, os.O_RDONLY | os.O_DIRECTORY)
held = expect('lease_first_acquire', lambda: P.acquire_lease(dfd))
child = textwrap.dedent('''
    import os, sys
    sys.path.insert(0, %r)
    import w1proto as P
    fd = os.open(%r, os.O_RDONLY | os.O_DIRECTORY)
    try:
        P.acquire_lease(fd)
        print('ACQUIRED')
    except P.LeaseHeld as caught:
        print('HELD', caught)
''') % (str(HERE), str(lease_dir))
second = subprocess.run([sys.executable, '-B', '-c', child], capture_output=True, text=True, timeout=60)
results['lease_second_process_refused_while_held'] = second.stdout.strip()
if not second.stdout.startswith('HELD'):
    failures.append('lease_second_process_refused_while_held')
os.close(held)
third = subprocess.run([sys.executable, '-B', '-c', child], capture_output=True, text=True, timeout=60)
results['lease_reacquired_after_release'] = third.stdout.strip()
if third.stdout.strip() != 'ACQUIRED':
    failures.append('lease_reacquired_after_release')
os.chmod(lease_dir / 'writer.lock', 0o644)
expect('lease_wrong_mode', lambda: P.acquire_lease(dfd), refused=True)
os.chmod(lease_dir / 'writer.lock', 0o600)
os.link(lease_dir / 'writer.lock', lease_dir / 'second-name')
expect('lease_hardlinked', lambda: P.acquire_lease(dfd), refused=True)
os.unlink(lease_dir / 'second-name')
os.rename(lease_dir / 'writer.lock', lease_dir / 'real.lock')
os.symlink('real.lock', lease_dir / 'writer.lock')
expect('lease_symlink', lambda: P.acquire_lease(dfd), refused=True)
os.unlink(lease_dir / 'writer.lock')
expect('lease_absent_is_not_created', lambda: P.acquire_lease(dfd), refused=True)
results['lease_absent_left_absent'] = not (lease_dir / 'writer.lock').exists()
if not results['lease_absent_left_absent']:
    failures.append('lease_absent_left_absent')
os.close(dfd)

# ---------------------------------------------------------------- framing


def frames(*bodies):
    chain, out = P.ZERO_CHAIN, b''
    for seq, body in enumerate(bodies):
        data, chain = P.encode_message(seq, chain, body)
        out += data
    return out, chain


def read_all(data, count):
    stream, chain, bodies = io.BytesIO(data), P.ZERO_CHAIN, []
    for seq in range(count):
        body, chain = P.decode_message(stream, seq, chain)
        bodies.append(body)
    return bodies, chain


good, good_chain = frames({'verb': 'admit'}, {'n': 1}, {'n': 2})
expect('framing_roundtrip', lambda: read_all(good, 3), want=([{'verb': 'admit'}, {'n': 1}, {'n': 2}], good_chain))


def tamper(data, old, new):
    assert old in data
    return data.replace(old, new, 1)


expect('framing_body_tampered_next_frame_refused', lambda: read_all(tamper(good, b'{"n":1}', b'{"n":7}'), 3), refused=True)
first_len = int.from_bytes(good[:8], 'big')
swapped = good[:8 + first_len]
second_start = 8 + first_len
second_len = int.from_bytes(good[second_start:second_start + 8], 'big')
third = good[second_start + 8 + second_len:]
expect('framing_reordered_refused', lambda: read_all(swapped + third + good[second_start:second_start + 8 + second_len], 3), refused=True)
expect('framing_truncated_refused', lambda: read_all(good[:-3], 3), refused=True)
noncanon = json.dumps({'seq': 0, 'prev': P.ZERO_CHAIN, 'body': {'a': 1}}, indent=1).encode()
expect('framing_noncanonical_refused', lambda: read_all(len(noncanon).to_bytes(8, 'big') + noncanon, 1), refused=True)
extra = P.canonical({'seq': 0, 'prev': P.ZERO_CHAIN, 'body': {}, 'x': 1})
expect('framing_extra_field_refused', lambda: read_all(len(extra).to_bytes(8, 'big') + extra, 1), refused=True)
expect('framing_oversize_header_refused', lambda: read_all((P.MAX_MESSAGE + 1).to_bytes(8, 'big'), 1), refused=True)
expect('framing_wrong_start_seq_refused', lambda: P.decode_message(io.BytesIO(good), 1, P.ZERO_CHAIN), refused=True)

# ---------------------------------------------------------------- streamed inputs
blob_a, blob_b, blob_obs = b'package A is end A;\n', b'with A; procedure B is begin null; end B;\n', b'{"window":"snapshot"}'


def entry(path, data, mode=0o644, sha=None, size=None):
    return {'path': path, 'size': len(data) if size is None else size, 'mode': mode,
            'sha256': sha or hashlib.sha256(data).hexdigest(), 'data_b64': base64.b64encode(data).decode()}


pins = {'core/a.ads': hashlib.sha256(blob_a).hexdigest(), 'core/b.adb': hashlib.sha256(blob_b).hexdigest()}
obs = ('observations/window.json',)
ok_entries = [entry('core/a.ads', blob_a), entry('core/b.adb', blob_b), entry('observations/window.json', blob_obs, 0o600)]
expect('inputs_accepted', lambda: sorted(P.verify_inputs(ok_entries, pins, obs)), want=['core/a.ads', 'core/b.adb', 'observations/window.json'])
expect('inputs_pinned_mismatch_refused', lambda: P.verify_inputs([entry('core/a.ads', blob_a + b'--'), ok_entries[1]], pins, obs), refused=True)
expect('inputs_declared_digest_lie_refused', lambda: P.verify_inputs([entry('core/a.ads', blob_a, sha=pins['core/b.adb']), ok_entries[1]], pins, obs), refused=True)
expect('inputs_size_lie_refused', lambda: P.verify_inputs([entry('core/a.ads', blob_a, size=1), ok_entries[1]], pins, obs), refused=True)
expect('inputs_unknown_path_refused', lambda: P.verify_inputs(ok_entries + [entry('core/c.adb', b'x')], pins, obs), refused=True)
expect('inputs_traversal_refused', lambda: P.verify_inputs(ok_entries + [entry('core/../x', b'x')], pins, obs + ('core/../x',)), refused=True)
expect('inputs_absolute_refused', lambda: P.verify_inputs(ok_entries + [entry('/etc/x', b'x')], pins, obs + ('/etc/x',)), refused=True)
expect('inputs_duplicate_refused', lambda: P.verify_inputs(ok_entries + [ok_entries[0]], pins, obs), refused=True)
expect('inputs_missing_pinned_refused', lambda: P.verify_inputs([ok_entries[0]], pins, obs), refused=True)
expect('inputs_bad_mode_refused', lambda: P.verify_inputs([entry('core/a.ads', blob_a, mode=0o4755), ok_entries[1]], pins, obs), refused=True)

# ---------------------------------------------------------------- hardening (in a child, so this process stays dumpable)
probe = textwrap.dedent('''
    import json, sys
    sys.path.insert(0, %r)
    import w1proto as P
    print(json.dumps(P.set_nondumpable()))
''') % str(HERE)
hard = subprocess.run([sys.executable, '-B', '-c', probe], capture_output=True, text=True, timeout=60)
try:
    evidence = json.loads(hard.stdout)
    results['nondumpable_readback'] = evidence
    if not (evidence['pr_get_dumpable'] == 0 and evidence['proc_self_fd_owner_uid'] == 0):
        failures.append('nondumpable_readback')
except ValueError:
    results['nondumpable_readback'] = 'ERROR: ' + hard.stdout + hard.stderr
    failures.append('nondumpable_readback')

summary = {'schema': 'w1proto-selftest-v1', 'module_sha256': hashlib.sha256((HERE / 'w1proto.py').read_bytes()).hexdigest(),
           'selftest_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'cases': len(results),
           'failures': failures, 'results': results, 'output_dir': str(SC),
           'boundary': 'same-user simulation of writer-side mechanisms; the separate-account kernel boundary is NOT tested',
           'truth_boundary': 'ENGINEERING_ONLY: never proof, review, admission or acceptance evidence. Original guarantees OPEN_UNCHANGED.'}
print(json.dumps(summary, indent=1, sort_keys=True, default=str))
sys.exit(1 if failures else 0)
