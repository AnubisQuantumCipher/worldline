"""Run the qualified original prefix, real JACKAL challenges, original outer/collector.

Only Main's declared mutable observation/adoption data is written. Frozen receiver,
source, commands, policy and original finite handshake remain unchanged.
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
C = Path(__file__).resolve().parent / 'candidate'
G = C / 'review/root-live-lane-v1'
A = C / 'review/root-source-binding-adoption-v1/adoption.json'
OUT = C / 'evidence/Main-original-qualified-prefix-execution-v1'
AID = BASE.parent.parent / 'omp-session-monitor-v1/omp-crash-recovery-20261010T114220Z/safe_json.py'
assert hashlib.sha256(AID.read_bytes()).hexdigest() == 'd55a16651d6474886accdd11b34a9c32f834d44150249e5f2833eaa57fedbc5d'
spec = importlib.util.spec_from_file_location('owned_execution_metadata', AID)
metadata = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metadata)
OUT.mkdir(mode=0o700, parents=True, exist_ok=False)
ENV = dict(os.environ, XDG_RUNTIME_DIR='/run/user/1000', DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/1000/bus')
MODES = ['native-build', 'native-component-tests', 'pending-build', 'build', 'entry-component-tests']
proposal, proposal_pin = metadata.load(str(C / 'reviewed-launch-proposal.json'))
assert proposal_pin['sha256'] == json.loads((C / 'author-freeze.json').read_text())['bindings']['proposal_sha256']
assert proposal['immediate_execution_ceiling'] == MODES
adoption, prior_adoption_pin = metadata.load(str(A))
metadata.save_new(str(OUT / 'prior-adoption.json'), adoption)
# Main supplies actual retained native get_goal and clock records for each stage.
# This wrapper never authors, relabels or copies an old ready read into a new stage.
for stage in ['dispatch:' + mode for mode in MODES] + ['collect']:
    assert stage in adoption['fresh_goal_observations'], 'Actual fresh Main stage observation missing: ' + stage
wrapper_pin = metadata.snapshot(str(Path(__file__).resolve()))[1]
assert adoption['main_prefix_wrapper'] == wrapper_pin
full_review, full_review_pin = metadata.load(adoption['independent_review']['path'])
assert full_review_pin == adoption['independent_review']
assert full_review['main_prefix_wrapper'] == wrapper_pin
GATE = metadata.snapshot(str(G / 'inputs.json'))[1]['sha256']
results = []
errors = []
active = None
active_action = None
LIMIT = 1000

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def raw_file(path):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    return os.fdopen(fd, 'wb')

def remaining():
    value = LIMIT - (time.monotonic() - START)
    if value <= 0:
        raise TimeoutError('Main finite prefix observation deadline, not a domain limit')
    return value

def complete_json_lines(path):
    if not path.exists():
        return []
    # Actual in-progress owned stream; trailing incomplete record is not corruption.
    data = path.read_bytes()
    return [json.loads(line) for line in data.splitlines(keepends=True)
            if line.endswith(b'\n') and line.strip()]

try:
    for mode in MODES:
        remaining()
        active_action = next(row for row in proposal['launches'] if row['mode'] == mode)
        lane = OUT / mode
        lane.mkdir(mode=0o700)
        argv = ['/usr/bin/python3', '-B', str(C / 'outer_capture.py'), mode, GATE]
        responded = set()
        outer = None
        with raw_file(lane / 'Main-outer.stdout') as stdout, raw_file(lane / 'Main-outer.stderr') as stderr:
            active = subprocess.Popen(argv, cwd=BASE, env=ENV, stdin=subprocess.PIPE,
                                      stdout=stdout, stderr=stderr, start_new_session=True)
            metadata.save_new(str(lane / 'Main-actual-outer-start.json'), {
                'at': now(), 'pid': active.pid, 'argv': argv, 'original_proposal': proposal_pin,
                'actual_gate_sha256': GATE, 'observer': 'Main', 'target_outcome_credit': False})
            while active.poll() is None:
                remaining()
                if outer is None:
                    starts = [row for row in complete_json_lines(lane / 'Main-outer.stdout')
                              if row.get('kind') == 'PRIVATE_OUTER_CAPTURE_STARTED']
                    if starts:
                        assert len(starts) == 1
                        outer = Path(starts[0]['path'])
                        assert outer.parent == C / 'review/root-outer-capture-v1'
                if outer is not None:
                    for row in complete_json_lines(outer / 'handshake.stdout'):
                        if row.get('kind') != 'ORDINARY_FIXED_CONSERVATIVE_MEMORY_CHALLENGE':
                            continue
                        path = row['challenge_path']
                        if path in responded:
                            continue
                        challenge, challenge_pin = metadata.load(path)
                        assert challenge_pin['sha256'] == row['challenge_sha256']
                        assert challenge['mode'] == mode and challenge['no_target_launch_executed'] is True
                        assert challenge['memory_expression'] == row['memory_expression']
                        number = challenge['challenge_number']
                        expression_path = lane / ('memory-expression-' + str(number) + '.json')
                        expression_pin = metadata.save_new(str(expression_path), {'expression': challenge['memory_expression']})
                        metadata.save_new(str(lane / ('original-challenge-expression-join-' + str(number) + '.json')), {
                            'original_challenge': challenge_pin, 'actual_original_challenge_record': challenge,
                            'separate_transport_expression_input': expression_pin,
                            'expression_copied_exactly_without_relabeling_original_challenge': True,
                            'formal_proof': False, 'phase_acceptance': False})
                        receipt_path = lane / ('actual-JACKAL-receipt-' + str(number) + '.json')
                        transaction_path = lane / ('actual-JACKAL-transaction-' + str(number) + '.json')
                        transport_argv = ['/usr/bin/python3', '-B', str(J / 'finite_native_memory_mcp_transport.py'),
                                          str(expression_path), str(receipt_path), str(transaction_path)]
                        with raw_file(lane / ('MCP-transport-' + str(number) + '.stdout')) as mo, raw_file(lane / ('MCP-transport-' + str(number) + '.stderr')) as me:
                            actual = subprocess.run(transport_argv, cwd=BASE, env=ENV, stdout=mo, stderr=me,
                                                    timeout=min(60, remaining()), check=False)
                        assert actual.returncode == 0, 'Real unchanged MCP transport refused'
                        receipt_pin = metadata.snapshot(str(receipt_path))[1]
                        answer = {'challenge_sha256': challenge_pin['sha256'],
                                  'receipt_path': str(receipt_path), 'receipt_sha256': receipt_pin['sha256']}
                        active.stdin.write((json.dumps(answer, sort_keys=True) + '\n').encode())
                        active.stdin.flush()
                        responded.add(path)
                time.sleep(0.1)
            code = active.wait(timeout=min(10, remaining()))
            active.stdin.close()
            stdout.flush(); os.fsync(stdout.fileno())
            stderr.flush(); os.fsync(stderr.fileno())
        entry = {'mode': mode, 'actual_outer_Popen_wait': code, 'actual_outer_pid': active.pid,
                 'actual_outer_argv': argv, 'responded_original_challenges': sorted(responded),
                 'actual_outer_directory': str(outer) if outer is not None else None,
                 'at': now(), 'elapsed_seconds_since_Main_start': time.monotonic() - START}
        metadata.save_new(str(lane / 'Main-actual-outer-wait.json'), entry)
        results.append(entry)
        active = None
        assert code == 0, 'Original outer/handshake refused or target failed; fail-stop'
        result, result_pin = metadata.load(str(Path(active_action['receipt']) / 'result.json'))
        assert result['scope_wait'] == 0 and result['child_wait']['returncode'] == 0 and result['inputs_unchanged'] is True
        print(json.dumps({'mode': mode, 'actual_outer_wait': code, 'actual_scope_wait': result['scope_wait'],
                          'actual_child_wait': result['child_wait']['returncode'], 'actual_result': result_pin,
                          'phase_acceptance': False}), flush=True)
except BaseException as error:
    errors.append({'type': type(error).__name__, 'message': str(error), 'at': now()})
finally:
    if active is not None:
        # Only this newly owned process group and its declared exact scope can be stopped.
        unit = active_action['scope_unit']
        observed = subprocess.run(['/usr/bin/systemctl', '--user', 'show', unit, '-p', 'ActiveState'],
                                  env=ENV, capture_output=True, text=True, timeout=30, check=False)
        if 'ActiveState=active' in observed.stdout or 'ActiveState=activating' in observed.stdout:
            stopped = subprocess.run(['/usr/bin/systemctl', '--user', 'stop', unit], env=ENV,
                                     capture_output=True, text=True, timeout=30, check=False)
            errors.append({'cleanup_owned_unit': unit, 'actual_stop_returncode': stopped.returncode,
                           'actual_stdout': stopped.stdout, 'actual_stderr': stopped.stderr})
        if active.poll() is None:
            os.killpg(active.pid, signal.SIGTERM)
            try:
                cleanup_code = active.wait(timeout=35)
            except subprocess.TimeoutExpired:
                os.killpg(active.pid, signal.SIGKILL)
                cleanup_code = active.wait(timeout=5)
        else:
            cleanup_code = active.wait(timeout=5)
        errors.append({'cleanup_owned_outer_pid': active.pid, 'actual_cleanup_Popen_wait': cleanup_code,
                       'unknown_or_failed_target_not_promoted': True})
    terminal = metadata.save_new(str(OUT / 'Main-complete-owned-prefix-observation.json'), {
        'at': now(), 'original_proposal': proposal_pin, 'prior_mutable_adoption': prior_adoption_pin,
        'requested_qualified_original_prefix': MODES, 'actual_completed_outer_waits': results,
        'errors': errors, 'actual_elapsed_seconds': time.monotonic() - START,
        'Main_observation_seconds': LIMIT, 'no_domain_limit_or_gate_changed': True,
        'phase_acceptance': False})
print(json.dumps({'complete_Main_observation': terminal, 'completed_modes': [row['mode'] for row in results],
                  'errors': errors, 'original_collector_and_release_still_required': True,
                  'phase_acceptance': False}), flush=True)
raise SystemExit(1 if errors else 0)
