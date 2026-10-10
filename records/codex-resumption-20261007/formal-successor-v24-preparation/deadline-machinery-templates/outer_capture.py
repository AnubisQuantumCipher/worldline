"""Future independently reviewed private outer capture; no display authority.

Preserves the unchanged complete handshake/runner failure tails as raw bytes.
Root reads separately retained challenge.json, supplies the real MCP receipt
through the unchanged stdin, and collects actual waits/nonlive ownership.
"""
from pathlib import Path
import datetime
import hashlib
import json
import os
import stat
import subprocess
import sys
import uuid
import time

sys.dont_write_bytecode = True
import authorization
import successor_support
MAIN_DEADLINE = time.monotonic() + 1000

D = Path(__file__).resolve().parent
G = D / 'review/root-live-lane-v1'
assert len(sys.argv) == 3 and sys.argv[1] == authorization.MODE
authorization.check('dispatch')
assert authorization.pin(G / 'inputs.json')['sha256'] == sys.argv[2]
out = D / 'review/root-outer-capture-v1' / uuid.uuid4().hex
out.mkdir(parents=True, mode=0o700, exist_ok=False)


def save(name, value):
    fd = os.open(out / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'w') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())


def open_raw(name):
    fd = os.open(out / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    return os.fdopen(fd, 'wb')


argv = ['/usr/bin/python3', '-B', str(G / 'handshake.py'), sys.argv[1], sys.argv[2]]
before = {str(G / name): authorization.pin(G / name) for name in ('handshake.py', 'inputs.json')}
errors = []
child = None
code = None
raw_files = []
streams = []


def failure(stage, error):
    errors.append({'stage': stage, 'type': type(error).__name__, 'message': str(error)})


def attempt(stage, function):
    try:
        return function()
    except BaseException as error:
        failure(stage, error)
        return None


with successor_support.owner_signals(MAIN_DEADLINE):
    try:
        streams.append(open_raw('handshake.stdout'))
        streams.append(open_raw('handshake.stderr'))
        environment = dict(os.environ)
        environment[successor_support.MAIN_DEADLINE_ENV] = str(MAIN_DEADLINE)
        child = subprocess.Popen(argv, stdin=sys.stdin, stdout=streams[0], stderr=streams[1],
                                 env=environment, start_new_session=True)
        attempt('start_artifact', lambda: save('outer-child-start.json', {
            'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'pid': child.pid, 'wrapper_pid': os.getpid(), 'argv': argv, 'inputs': before,
            'raw_stdout': str(out / 'handshake.stdout'), 'raw_stderr': str(out / 'handshake.stderr'),
            'challenge_discovery': str(G / 'attempts' / sys.argv[1]),
            'target_wait_or_acceptance': False}))
        attempt('start_display', lambda: print(json.dumps({
            'kind': 'PRIVATE_OUTER_CAPTURE_STARTED', 'path': str(out), 'pid': child.pid,
            'challenge_discovery': str(G / 'attempts' / sys.argv[1]),
            'no_target_outcome_credit': True}), flush=True))
    except BaseException as error:
        failure('open_or_spawn', error)
    finally:
        # Original1000 includes40 seconds of bounded nested cleanup and final retention.
        owner_control = None
        if child is not None:
            owner_control = successor_support.wait_owned(
                child, 1000, deadline=MAIN_DEADLINE - 45, hard_deadline=MAIN_DEADLINE,
                term_seconds=35, kill_seconds=5,
                stop=RuntimeError('outer start/retention failed') if errors else None)
            code = owner_control['returncode']
            errors.extend(owner_control['errors'])
        for index, stream in enumerate(streams):
            attempt('raw_flush_' + str(index), stream.flush)
            attempt('raw_fsync_' + str(index), lambda stream=stream: os.fsync(stream.fileno()))
            attempt('raw_close_' + str(index), stream.close)

with successor_support.owner_signals(MAIN_DEADLINE):
    after = attempt('control_readback', lambda: {path: authorization.pin(path) for path in before})
    if after != before:
        failure('control_drift', RuntimeError('outer handshake or gate identity changed'))
    for name in ('handshake.stdout', 'handshake.stderr'):
        row = attempt('raw_identity_' + name, lambda name=name: authorization.pin(out / name))
        if row is not None:
            raw_files.append(row)
    terminal = {
        'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'pid': child.pid if child is not None else None, 'wrapper_pid': os.getpid(), 'argv': argv,
        'actual_handshake_Popen_wait_returncode': code, 'owner_control': owner_control,
        'inputs_unchanged': before == after,
        'raw_files': raw_files, 'retention_errors': list(errors),
        'retention_success': not errors and code is not None,
        'truth_boundary': 'Actual outer handshake-child wait only when observed. Raw retention success requires every flush/fsync/close/hash. Unknown waits and retention failures require Root ownership collection. No target/scope wait, admission, recovered child outcome, exhaustive custody or acceptance.'}
    attempt('terminal_artifact', lambda: save('outer-child-wait.json', terminal))
    attempt('terminal_display', lambda: print(json.dumps({
        'kind': 'PRIVATE_OUTER_CAPTURE_TERMINAL', 'path': str(out),
        'actual_handshake_wait': code, 'retention_success_before_display': not errors and code is not None,
        'retention_errors': list(errors), 'no_target_or_phase_acceptance': True}), flush=True))
    if errors:
        attempt('failure_artifact', lambda: save('outer-retention-refusal.json', {
            'pid': child.pid if child is not None else None, 'actual_handshake_wait': code,
            'errors': list(errors), 'retention_success': False, 'root_collection_required': True}))
    # Preserve a nonzero original handshake status. A successful handshake with failed
    # retention/display is separately refused; no failure is promoted to success.
    raise SystemExit(1 if errors or owner_control is None else successor_support.owner_exit_code(owner_control))
