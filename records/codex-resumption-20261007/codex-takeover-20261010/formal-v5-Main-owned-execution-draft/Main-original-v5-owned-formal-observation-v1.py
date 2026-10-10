"""Observe the original C28 formal action with genuine memory receipts and waits.

Main's original1000 seconds starts before imports/preflight; cleanup uses only
that allowance. Frozen C28 controls/source/proposal/collector are never edited.
"""
import time
START = time.monotonic()
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess

BASE = Path('/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1')
R = BASE / 'records/codex-resumption-20261007'
J = R / 'native-owner-join-v59'
C = R / 'codex-takeover-20261010/formal-frame-successor-v5-draft'
G = C / 'review/root-live-lane-v1'
OUT = C / 'evidence/Main-owned-formal-observation-v1'
MODE = 'full-strict-formal-diagnostic'
LIMIT = 1000
DEADLINE = START + LIMIT
ENV = dict(os.environ, XDG_RUNTIME_DIR='/run/user/1000', DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/1000/bus')
M = BASE.parent.parent / 'omp-session-monitor-v1'
AID = M / 'omp-crash-recovery-20261010T114220Z/safe_json.py'
assert hashlib.sha256(AID.read_bytes()).hexdigest() == 'd55a16651d6474886accdd11b34a9c32f834d44150249e5f2833eaa57fedbc5d'
spec = importlib.util.spec_from_file_location('formal_owned_observation_metadata', AID)
metadata = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metadata)


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def remaining(reserve=0):
    value = DEADLINE - time.monotonic() - reserve
    if value <= 0:
        raise TimeoutError('Original finite Main observer allowance exhausted')
    return value


def raw_file(path):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    return os.fdopen(fd, 'wb')


def compact_protocol(data, kind, keys):
    def unique(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError('duplicate protocol member')
            value[key] = item
        return value
    def nonfinite(value):
        raise ValueError('nonfinite protocol number')
    values = []
    for line in data.splitlines(keepends=True):
        if not line.endswith(b'\n') or kind.encode('ascii') not in line:
            continue
        value = json.loads(line, object_pairs_hook=unique, parse_constant=nonfinite)
        if not isinstance(value, dict) or value.get('kind') != kind or set(value) != keys:
            raise ValueError('invalid complete protocol emission')
        values.append(value)
    return values


# This is a Main observer source, not an authorized C28 frozen file addition.
# The original frame permits only specifically declared mutable output roots.
OUT.mkdir(mode=0o700, parents=True, exist_ok=False)
proposal, proposal_pin = metadata.load(str(C / 'reviewed-launch-proposal.json'))
gate_pin = metadata.snapshot(str(G / 'inputs.json'))[1]
action = next(row for row in proposal['launches'] if row['mode'] == MODE)
assert proposal_pin['sha256'] == '9cc68ea71f3e313305e722726cae2a2b3f03f6b1091e63f5530d6264c3a3b749'
assert gate_pin['sha256'] == '694a6b1acbcc6c472885dd484eb242787ff9db172d1fda36c0fc6768185bdff8'
argv = ['/usr/bin/python3', '-B', str(C / 'outer_capture.py'), MODE, gate_pin['sha256']]
active = None
outer = None
actual_code = None
responded = set()
errors = []
try:
    remaining(45)
    with raw_file(OUT / 'Main-outer.stdout') as stdout, raw_file(OUT / 'Main-outer.stderr') as stderr:
        active = subprocess.Popen(argv, cwd=BASE, env=ENV, stdin=subprocess.PIPE,
                                  stdout=stdout, stderr=stderr, start_new_session=True)
        metadata.save_new(str(OUT / 'Main-actual-outer-start.json'), {
            'at': now(), 'pid': active.pid, 'argv': argv, 'original_proposal': proposal_pin,
            'actual_gate': gate_pin, 'observer': 'Main', 'target_outcome_credit': False})
        while active.poll() is None:
            remaining(45)
            if outer is None:
                starts = compact_protocol((OUT / 'Main-outer.stdout').read_bytes(),
                    'PRIVATE_OUTER_CAPTURE_STARTED', {'kind', 'path', 'pid', 'challenge_discovery', 'no_target_outcome_credit'})
                if starts:
                    assert len(starts) == 1
                    outer = Path(starts[0]['path'])
                    assert outer.parent == C / 'review/root-outer-capture-v1'
                    assert outer.resolve(strict=True) == outer and outer.is_dir()
            if outer is not None:
                rows = compact_protocol((outer / 'handshake.stdout').read_bytes(),
                    'ORDINARY_FIXED_CONSERVATIVE_MEMORY_CHALLENGE',
                    {'kind', 'challenge_path', 'challenge_sha256', 'memory_expression', 'reply_fields'})
                for row in rows:
                    path = row['challenge_path']
                    assert isinstance(path, str) and Path(path).is_absolute()
                    digest = row['challenge_sha256']
                    assert isinstance(digest, str) and len(digest) == 64 and all(value in '0123456789abcdef' for value in digest)
                    assert isinstance(row['memory_expression'], str) and row['memory_expression']
                    assert row['reply_fields'] == ['challenge_sha256', 'receipt_path', 'receipt_sha256']
                    if path in responded:
                        continue
                    challenge, challenge_pin = metadata.load(path)
                    assert challenge_pin['sha256'] == digest
                    assert Path(path).is_relative_to(G / 'attempts' / MODE)
                    assert challenge['mode'] == MODE and challenge['no_target_launch_executed'] is True
                    assert challenge['memory_expression'] == row['memory_expression']
                    number = challenge['challenge_number']
                    expression_path = OUT / ('memory-expression-' + str(number) + '.json')
                    expression_pin = metadata.save_new(str(expression_path), {'expression': challenge['memory_expression']})
                    metadata.save_new(str(OUT / ('original-challenge-expression-join-' + str(number) + '.json')), {
                        'original_challenge': challenge_pin, 'actual_original_challenge_record': challenge,
                        'separate_transport_expression_input': expression_pin,
                        'expression_copied_exactly_without_relabeling_original_challenge': True,
                        'formal_proof': False, 'phase_acceptance': False})
                    receipt_path = OUT / ('actual-JACKAL-receipt-' + str(number) + '.json')
                    transaction_path = OUT / ('actual-JACKAL-transaction-' + str(number) + '.json')
                    transport_argv = ['/usr/bin/python3', '-B', str(J / 'finite_native_memory_mcp_transport.py'),
                                      str(expression_path), str(receipt_path), str(transaction_path)]
                    with raw_file(OUT / ('MCP-transport-' + str(number) + '.stdout')) as mo, raw_file(OUT / ('MCP-transport-' + str(number) + '.stderr')) as me:
                        actual = subprocess.run(transport_argv, cwd=BASE, env=ENV, stdout=mo, stderr=me,
                                                timeout=min(60, remaining(45)), check=False)
                    assert actual.returncode == 0, 'Real original MCP transport refused'
                    receipt_pin = metadata.snapshot(str(receipt_path))[1]
                    answer = {'challenge_sha256': challenge_pin['sha256'],
                              'receipt_path': str(receipt_path), 'receipt_sha256': receipt_pin['sha256']}
                    active.stdin.write((json.dumps(answer, sort_keys=True) + '\n').encode())
                    active.stdin.flush()
                    responded.add(path)
            time.sleep(0.1)
        actual_code = active.wait(timeout=min(5, remaining()))
        active.stdin.close()
        stdout.flush(); os.fsync(stdout.fileno())
        stderr.flush(); os.fsync(stderr.fileno())
    metadata.save_new(str(OUT / 'Main-actual-outer-wait.json'), {
        'at': now(), 'actual_outer_Popen_wait': actual_code, 'pid': active.pid, 'argv': argv,
        'actual_outer_directory': str(outer) if outer is not None else None,
        'responded_original_challenges': sorted(responded), 'outcome_inferred': False})
    assert actual_code == 0, 'Original formal outer/handshake refused or target failed'
    result, result_pin = metadata.load(str(Path(action['receipt']) / 'result.json'))
    assert result['scope_wait'] == 0 and result['child_wait']['returncode'] == 0 and result['inputs_unchanged'] is True
    print(json.dumps({'actual_original_formal_result': result_pin, 'actual_Main_outer_wait': actual_code,
        'actual_scope_wait': result['scope_wait'], 'actual_child_wait': result['child_wait']['returncode'],
        'original_collector_release_and_full_report_checks_still_required': True, 'phase_acceptance': False}), flush=True)
except BaseException as error:
    errors.append({'at': now(), 'type': type(error).__name__, 'message': str(error)})
finally:
    if active is not None and actual_code is None:
        try:
            if active.poll() is None:
                observed = subprocess.run(['/usr/bin/systemctl', '--user', 'show', action['scope_unit'], '-p', 'ActiveState'],
                                          env=ENV, capture_output=True, text=True, timeout=min(30, remaining(10)))
                metadata.save_new(str(OUT / 'Main-owned-scope-cleanup-observation.json'), {
                    'unit': action['scope_unit'], 'actual_returncode': observed.returncode,
                    'actual_stdout': observed.stdout, 'actual_stderr': observed.stderr})
                if 'ActiveState=active' in observed.stdout or 'ActiveState=activating' in observed.stdout:
                    stopped = subprocess.run(['/usr/bin/systemctl', '--user', 'stop', action['scope_unit']], env=ENV,
                                             capture_output=True, text=True, timeout=min(30, remaining(10)))
                    metadata.save_new(str(OUT / 'Main-owned-scope-stop.json'), {
                        'unit': action['scope_unit'], 'actual_returncode': stopped.returncode,
                        'actual_stdout': stopped.stdout, 'actual_stderr': stopped.stderr})
                if active.stdin is not None and not active.stdin.closed:
                    # Closing an already-owned raw pipe cannot flush unanswered protocol.
                    active.stdin.raw.close()
                    active.stdin.close()
                try:
                    actual_code = active.wait(timeout=min(5, remaining(5)))
                except subprocess.TimeoutExpired:
                    # Signal only the still-owned unreaped Popen process group.
                    os.killpg(active.pid, signal.SIGTERM)
                    try:
                        actual_code = active.wait(timeout=min(35, remaining(5)))
                    except subprocess.TimeoutExpired:
                        os.killpg(active.pid, signal.SIGKILL)
                        actual_code = active.wait(timeout=min(5, remaining()))
            else:
                # This is still our actual Popen handle, not a reconstructed wait.
                actual_code = active.wait(timeout=min(5, remaining()))
        except BaseException as error:
            errors.append({'stage': 'owned_cleanup', 'type': type(error).__name__, 'message': str(error),
                           'actual_outer_wait': actual_code, 'owned_identity_unresolved': actual_code is None})
        errors.append({'cleanup_owned_outer_pid': active.pid, 'actual_cleanup_Popen_wait': actual_code,
                       'unknown_or_failed_target_not_promoted': True})
    terminal = metadata.save_new(str(OUT / 'Main-complete-owned-formal-observation.json'), {
        'at': now(), 'original_proposal': proposal_pin, 'actual_outer_argv': argv,
        'actual_Main_outer_Popen_wait': actual_code, 'actual_outer_directory': str(outer) if outer is not None else None,
        'responded_original_challenges': sorted(responded), 'errors': errors,
        'actual_elapsed_seconds': time.monotonic() - START, 'Main_observation_seconds': LIMIT,
        'no_domain_limit_or_gate_changed': True, 'original_collector_and_release_still_required': True,
        'phase_acceptance': False})
print(json.dumps({'complete_Main_observation': terminal, 'errors': errors, 'phase_acceptance': False}), flush=True)
raise SystemExit(1 if errors else 0)
