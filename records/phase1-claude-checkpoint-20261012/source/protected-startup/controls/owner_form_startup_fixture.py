"""Create original disposable startup states through genuine owner effects.

This new control producer runs today. It never writes journal_intents/history,
supplies a native decision, resets prior history, or reports a simulated wait.
Fault cases interrupt the actual StartupLease.open_journal transaction. The
unchanged original controls subsequently inspect the retained result.
"""
from __future__ import annotations
import sys
_approved = sys.modules.get('_worldline_approved_source_loader')
if _approved is None:
    raise SystemExit('STARTUP_FORMATION_EARLY_SOURCE_REQUIRED')
_source = _approved.current()
if type(_source) is not _approved.ApprovedSourceLease:
    raise SystemExit('STARTUP_FORMATION_ACTUAL_SOURCE_LEASE_REQUIRED')
_source.check()
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import select
import signal
import socket
import sqlite3
import stat
import subprocess
import time
# -I -S supplies no fixture or runtime search path. Select only the actual
# authenticated shared directories before their first product import.
for directory in (Path(__file__).parents[2] / 'protected-root/controls',
                  Path(__file__).parents[2] / 'runtime'):
    _source.directory_or_absent(str(directory))
    sys.path.insert(0, str(directory))
import fixture_builder as F

SCHEMA = 'worldline.original-startup-control-formation-v1'
FAULT_CASES = ('INTENT_MISSING', 'INTENT_PRESENT', 'INTENT_CHANGED', 'SYMLINK', 'MULTILINK')
CASES = FAULT_CASES + ('EMPTY_GENESIS', 'MISSING_LOCK', 'LEGACY_ENDPOINT',
                     'CONSUMED_MISSING', 'PRESENT_UNUSED', 'COMPOSED_NATIVE_PROOF',
                     'CAPABILITY_PRESENT', 'CAPABILITY_MISSING', 'CAPABILITY_UNSAFE', 'ZERO_UID')


def require(value, reason):
    if not value:
        raise RuntimeError(reason)


def error(value):
    return {'module': type(value).__module__, 'type': type(value).__qualname__,
            'message': str(value), 'repr': repr(value), 'errno': getattr(value, 'errno', None)}


def selected_plan(path, *, child=False):
    raw = _source.file(str(path), ('DATA',))
    plan = F.exact(raw)
    require(type(plan) is dict and set(plan) == {
        'schema', 'case', 'startup_descriptor', 'journal_name', 'capability_member',
        'child_entry', 'child_envelope', 'fault_operator', 'result_directory',
        'timeout', 'injector_timeout'}, 'STARTUP_FORMATION_COMPLETE_PLAN_REQUIRED')
    require(plan['schema'] == SCHEMA and plan['case'] in CASES,
            'STARTUP_FORMATION_ORIGINAL_CASE_REQUIRED')
    for name, expected in (('timeout', 600), ('injector_timeout', 120)):
        value = plan[name]
        require(type(value) in (int, float) and math.isfinite(value) and value == expected,
                'STARTUP_FORMATION_ORIGINAL_FINITE_CAP_REQUIRED')
    require(plan['child_entry'] == str(Path(__file__).absolute()),
            'STARTUP_FORMATION_EXACT_SELECTED_CHILD_ENTRY_REQUIRED')
    _source.file(plan['child_entry'], ('SOURCE', 'ENTRY'))
    require(type(child) is bool, 'STARTUP_FORMATION_EXACT_CALLER_CHILD_ROUTE_REQUIRED')
    if child:
        # This is the already-held envelope of this actual approved child. Its
        # bytes are authenticated by the original lease check, not recursively
        # embedded as a FILE member of itself. Parent still selects it as DATA.
        actual = _source.check()
        require(plan['child_envelope'] == _source.envelope_path
                and actual['envelope_path'] == plan['child_envelope']
                and actual['envelope_bytes_hex'] == _source.envelope.hex(),
                'STARTUP_FORMATION_ACTUAL_HELD_CHILD_ENVELOPE_SPLIT')
    else:
        _source.file(plan['child_envelope'], ('DATA',))
    if plan['case'] in FAULT_CASES:
        _source.file(plan['fault_operator'], ('EXECUTABLE',))
    descriptor_raw = _source.file(plan['startup_descriptor'], ('DATA',))
    descriptor = F.exact(descriptor_raw)
    root = Path(descriptor['paths']['authority_root'])
    require(root.parent == Path('/srv') and root.name.startswith('cosmogony-canonical-v1.'),
            'STARTUP_FORMATION_EXACT_ORIGINAL_DISPOSABLE_ROOT_REQUIRED')
    output = F.protected(Path(plan['result_directory']), True)
    require(not output.lstat().st_mode & 0o077 and output != root
            and not output.is_relative_to(root),
            'STARTUP_FORMATION_EXTERNAL_PRIVATE_RETENTION_REQUIRED')
    _source.check()
    return plan, raw, descriptor


def process(child):
    raw = (Path('/proc') / str(child.pid) / 'stat').read_bytes()
    tail = raw[raw.rfind(b')') + 2:].split()
    return {'pid': child.pid, 'stat_hex': raw.hex(), 'starttime': tail[19].decode('ascii'),
            'cmdline_hex': (Path('/proc') / str(child.pid) / 'cmdline').read_bytes().hex()}


def private_snapshot(descriptor):
    from worldline.protected_startup import private_bytes
    genesis = F.exact(private_bytes(Path(descriptor['genesis'])))
    database = Path(descriptor['bootstrap_ledger'])
    F.protected(database)
    with sqlite3.connect('file:' + str(database) + '?mode=ro', uri=True) as db:
        require(db.execute('PRAGMA quick_check').fetchall() == [('ok',)],
                'STARTUP_FORMATION_ACTUAL_LEDGER_CORRUPT')
        intents = db.execute('SELECT * FROM journal_intents ORDER BY name').fetchall()
        history = db.execute('SELECT * FROM journal_history ORDER BY ordinal').fetchall()
    def archive(value):
        if type(value) is bytes:
            return {'bytes_hex': value.hex()}
        if type(value) in (list, tuple):
            return [archive(item) for item in value]
        return value
    return {'database': str(database), 'intents': archive(intents),
            'history': archive(history)}, genesis


def require_fresh(lease):
    require(lease.db.execute('SELECT * FROM journal_history ORDER BY ordinal').fetchall() == [],
            'STARTUP_FORMATION_ORIGINAL_UNUSED_OWNER_REQUIRED')
    rows = lease.db.execute('SELECT name,state FROM journal_intents ORDER BY name').fetchall()
    require({name for name, _state in rows} == set(lease.genesis['journals'])
            and all(state == 'UNUSED' for _name, state in rows),
            'STARTUP_FORMATION_NO_PRIOR_ADMISSION_REQUIRED')
    require(all(not os.path.lexists(item['path']) for item in lease.genesis['journals'].values()),
            'STARTUP_FORMATION_NO_PRIOR_JOURNAL_REQUIRED')


class FrontierAdmissionCapture:
    """Retain actual inputs/results/effects; never return an admission verdict."""
    def __init__(self, name):
        self.name = name.encode('utf-8')

    @staticmethod
    def admission(result):
        return {'status': result.status, 'position': result.position,
                'envelope_hex': result.envelope.hex(), 'name_hex': result.name.hex()}

    @staticmethod
    def archive(value):
        """Preserve every actual SQLite BLOB byte and nested callback field."""
        if type(value) is bytes:
            return {'bytes_hex': value.hex()}
        if type(value) in (list, tuple):
            return [FrontierAdmissionCapture.archive(item) for item in value]
        if type(value) is dict:
            return {key: FrontierAdmissionCapture.archive(item) for key, item in value.items()}
        return value

    def retain(self, kind, detail):
        print(F.canonical({'schema': 'worldline.original-startup-frontier-native-observation-v1',
            'journal_name_hex': self.name.hex(), 'kind': kind, 'actual': self.archive(detail)}).decode('utf-8'), flush=True)
        # stdout is the actual exclusive parent-held raw file, never a discarded
        # PIPE. Every completed input/effect observation is synchronized before
        # the native callback resumes; any partial write remains raw evidence.
        os.fsync(sys.stdout.fileno())

    def input(self, envelope, word):
        self.retain('native-input', {'envelope_hex': envelope.hex(), 'name_hex': word.hex()})

    def decision(self, result):
        self.retain('native-decision', self.admission(result))

    def transition(self, result):
        self.retain('native-transition', {'status': result.status, 'position': result.position,
            'before': self.admission(result.before), 'after': self.admission(result.after)})

    def effect(self, *, operation, boundary, detail_raw, exception):
        self.retain('actual-owner-effect', {'operation': operation, 'boundary': boundary,
            'detail_raw_hex': detail_raw.hex(), 'exception': error(exception) if exception is not None else None})


def child_action(plan_path):
    plan, _raw, _descriptor = selected_plan(plan_path, child=True)
    from worldline.protected_startup import StartupLease
    lease = StartupLease(Path(plan['startup_descriptor']))
    primary = None
    try:
        # This original offline owner call precedes construct(), so authenticate
        # the exact descriptor/lease-selected Gate import roots here as well.
        gate_source = lease.spec['runtime']['gate_source']
        _source.file(gate_source, ('SOURCE',))
        for directory in reversed((str(Path(gate_source).parent), *(lease.shared_import_roots if lease.shared_source is not None else ()))):
            _source.directory_or_absent(directory)
            if directory not in sys.path:
                sys.path.insert(0, directory)
        _source.check()
        import intent_gate
        require(Path(intent_gate.__file__) == Path(gate_source),
                'STARTUP_FORMATION_ACTUAL_SELECTED_GATE_SOURCE_SPLIT')
        require_fresh(lease)
        lease.gate = lease._construct_gate(intent_gate)
        name = plan['journal_name']
        require(name in lease.genesis['journals'], 'STARTUP_FORMATION_ORIGINAL_JOURNAL_REQUIRED')
        record = lease.genesis['journals'][name]
        from worldline.protected_startup import canonical
        ready = {'schema': 'worldline.original-startup-formation-ready-v1',
                 'pid': os.getpid(), 'journal_name': name, 'journal_path': record['path'],
                 'expected_sha256': hashlib.sha256(canonical(record['initial_envelope']) + b'\n').hexdigest()}
        print(F.canonical(ready).decode('utf-8'), flush=True)
        require(sys.stdin.buffer.read(1) == b'G', 'STARTUP_FORMATION_ACTUAL_PARENT_GO_REQUIRED')
        _source.check()
        if plan['case'] == 'COMPOSED_NATIVE_PROOF':
            from worldline.protected_startup import private_bytes
            for actual_name, actual_record in lease.genesis['journals'].items():
                capture = FrontierAdmissionCapture(actual_name)
                lease._startup_control_capture = capture
                capture.retain('before-original-native-owner-admission', {
                    'journal_path': actual_record['path'],
                    'initial_envelope_hex': (canonical(actual_record['initial_envelope']) + b'\n').hex(),
                    'actual_history': lease.db.execute('SELECT * FROM journal_history ORDER BY ordinal').fetchall()})
                lease.open_journal(lease.gate, actual_name, Path(actual_record['path']),
                                   actual_record['initial_envelope'])
                decision = lease.journal_admission_decisions[actual_name][-1]
                actual_raw = private_bytes(actual_record['path'])
                actual_rows = lease.db.execute('SELECT * FROM journal_intents WHERE name=?', (actual_name,)).fetchall()
                capture.retain('after-original-native-owner-admission', {
                    'native_admission': capture.admission(decision), 'journal_path': actual_record['path'],
                    'actual_journal_hex': actual_raw.hex(), 'actual_intent_rows': actual_rows,
                    'actual_history': lease.db.execute('SELECT * FROM journal_history ORDER BY ordinal').fetchall()})
                require(decision.state == 'AlreadyConsumed' and
                        actual_raw == canonical(actual_record['initial_envelope']) + b'\n' and
                        lease.db.execute('SELECT state FROM journal_intents WHERE name=?', (actual_name,)).fetchone() == ('CONSUMED',),
                        'STARTUP_FORMATION_COMPLETE_NATIVE_FRONTIER_JOURNAL_REQUIRED')
        else:
            lease.open_journal(lease.gate, name, Path(record['path']), record['initial_envelope'])
            decision = lease.journal_admission_decisions[name][-1]
            print(F.canonical({'schema': 'worldline.original-startup-formation-return-v1',
                'native_admission': {'status': decision.status, 'position': decision.position,
                    'envelope_hex': decision.envelope.hex(), 'name_hex': decision.name.hex()},
                'actual_history': lease.db.execute('SELECT * FROM journal_history ORDER BY ordinal').fetchall()
            }).decode('utf-8'), flush=True)
    except BaseException as caught:
        primary = caught
        raise
    finally:
        try:
            lease.close()
        except BaseException as close_error:
            if primary is None:
                raise
            primary.add_note('Actual startup lease close failed: ' + repr(close_error))


def receive_line(stream, child, deadline, retained, field='received_hex'):
    # Child/operator writes go directly to this exclusive raw retention file.
    # Reading a READY/ARM prefix never owns or discards subsequent bytes.
    while True:
        raw = os.pread(stream.fileno(), os.fstat(stream.fileno()).st_size, 0)
        retained[field] = raw.hex()
        line, separator, _rest = raw.partition(b'\n')
        if separator:
            require(child.poll() is None, 'STARTUP_FORMATION_CHILD_ENDED_BEFORE_GO')
            return line + separator
        require(child.poll() is None, 'STARTUP_FORMATION_ACTUAL_READY_EOF')
        left = deadline - time.monotonic()
        require(left > 0, 'STARTUP_FORMATION_ACTUAL_READY_TIMEOUT')
        time.sleep(min(left, 0.01))


def execute_child(plan_path, plan, output, journal_path, observed):
    child = injector = None
    pidfd = None
    handles = []
    primary = None
    record = {'argv': None, 'pid': None, 'birth': None, 'ready': None, 'received_hex': '',
              'pidfd': None, 'fault': None, 'child_wait': None, 'cleanup': [], 'error': None}
    observed['child'] = record
    out = err = fault_out = fault_err = None
    deadline = time.monotonic() + plan['timeout']
    try:
        err = (output / 'child.stderr').open('x+b'); handles.append(err)
        out = (output / 'child.stdout').open('x+b'); handles.append(out)
        os.fchmod(err.fileno(), 0o600); os.fchmod(out.fileno(), 0o600)
        argv = [_source.interpreter, '-I', '-S', '-B', _source.helper_path,
                '--bootstrap-envelope', plan['child_envelope'], '--entry', plan['child_entry'],
                '--child', '--plan', str(plan_path)]
        record['argv'] = argv
        child = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=out,
                                 stderr=err, env={'PATH': '/usr/bin:/bin', 'LANG': 'C'})
        record['pid'] = child.pid
        pidfd = os.pidfd_open(child.pid); record['pidfd'] = pidfd
        record['birth'] = process(child)
        raw = receive_line(out, child, deadline, record)
        ready = F.exact(raw)
        require(set(ready) == {'schema', 'pid', 'journal_name', 'journal_path', 'expected_sha256'}
                and ready['schema'] == 'worldline.original-startup-formation-ready-v1'
                and ready['pid'] == child.pid and ready['journal_name'] == plan['journal_name']
                and ready['journal_path'] == str(journal_path),
                'STARTUP_FORMATION_ACTUAL_CHILD_READY_JOIN_REQUIRED')
        record['ready'] = ready
        if plan['case'] in FAULT_CASES:
            fault_out = (output / 'injector.stdout').open('x+b'); handles.append(fault_out)
            fault_err = (output / 'injector.stderr').open('x+b'); handles.append(fault_err)
            os.fchmod(fault_out.fileno(), 0o600); os.fchmod(fault_err.fileno(), 0o600)
            kind = 'openat-create' if plan['case'] == 'INTENT_MISSING' else 'fsync'
            effect = 'kill-entry' if kind == 'openat-create' else 'kill-exit'
            command = [plan['fault_operator'], str(child.pid), str(pidfd), kind,
                       str(journal_path), '1', effect]
            fault = {'argv': command, 'pid': None, 'birth': None, 'arm_received_hex': '',
                     'actual_wait': None, 'raw_after_arm_hex': ''}
            record['fault'] = fault
            injector = subprocess.Popen(command, stdout=fault_out, stderr=fault_err,
                                         pass_fds=(pidfd,), env={'PATH': '/usr/bin:/bin', 'LANG': 'C'})
            fault['pid'] = injector.pid; fault['birth'] = process(injector)
            arm_deadline = min(deadline, time.monotonic() + plan['injector_timeout'])
            # The C operator writes its genuine ARM and every later byte
            # straight to retained storage, even if a deadline interrupts wait.
            arm = receive_line(fault_err, injector, arm_deadline, fault,
                               'arm_received_hex')
            expected = ('ACTUAL_SYSCALL_FAULT_ARMED pid=' + str(child.pid) + ' pidfd=' + str(pidfd)
                        + ' syscall=' + kind + ' occurrence=1 effect=' + effect
                        + ' path_hex=' + os.fsencode(journal_path).hex() + '\n').encode('ascii')
            require(bytes(arm) == expected and injector.poll() is None,
                    'STARTUP_FORMATION_ACTUAL_NATIVE_ARM_REQUIRED')
        _source.check()
        require(process(child)['starttime'] == record['birth']['starttime'] and child.poll() is None,
                'STARTUP_FORMATION_ACTUAL_OWNED_CHILD_CHANGED')
        child.stdin.write(b'G'); child.stdin.flush(); child.stdin.close()
        if injector is not None:
            remaining = min(plan['injector_timeout'], deadline - time.monotonic())
            require(remaining > 0, 'STARTUP_FORMATION_ORIGINAL_DEADLINE')
            record['fault']['actual_wait'] = injector.wait(timeout=remaining)
            raw_fault = os.pread(fault_err.fileno(), os.fstat(fault_err.fileno()).st_size, 0)
            require(raw_fault.startswith(arm), 'STARTUP_FORMATION_ACTUAL_ARM_PREFIX_CHANGED')
            after = raw_fault[len(arm):]
            record['fault']['raw_after_arm_hex'] = after.hex()
            require(record['fault']['actual_wait'] == 0 and b'ACTUAL_SYSCALL_FAULT_APPLIED' in after,
                    'STARTUP_FORMATION_ACTUAL_NATIVE_FAULT_NOT_COMPLETED')
        remaining = deadline - time.monotonic()
        require(remaining > 0, 'STARTUP_FORMATION_ORIGINAL_DEADLINE')
        record['child_wait'] = child.wait(timeout=remaining)
        expected_wait = -signal.SIGKILL if injector is not None else 0
        require(record['child_wait'] == expected_wait, 'STARTUP_FORMATION_ACTUAL_CHILD_RESULT_REQUIRED')
    except BaseException as caught:
        primary = caught; record['error'] = error(caught)
        raise
    finally:
        # Direct, unreaped Popen ownership remains valid if later /proc capture
        # or pidfd acquisition fails. No numeric PID is rediscovered and killed.
        for label, owned in (('injector', injector), ('child', child)):
            if owned is None:
                continue
            cleanup = {'owner': label, 'signal': None, 'wait': None, 'error': None}
            record['cleanup'].append(cleanup)
            try:
                if owned.poll() is None:
                    if label == 'child' and pidfd is not None:
                        signal.pidfd_send_signal(pidfd, signal.SIGKILL)
                    else:
                        owned.kill()
                    cleanup['signal'] = 'SIGKILL_ACTUAL_UNREAPED_OWNER'
                cleanup['wait'] = owned.wait(timeout=plan['injector_timeout'])
            except BaseException as close_error:
                cleanup['error'] = error(close_error)
                if primary is not None:
                    primary.add_note('Actual ' + label + ' cleanup failed: ' + repr(close_error))
                else:
                    primary = close_error
        # Capture every actual fragment still present after owned cleanup.
        # The files already retain post-READY/ARM output without pipe draining.
        # A failed cleanup/wait remains UNKNOWN; this is no fabricated stream end.
        record['raw_streams'] = {}
        for name, handle in (('child.stdout', out), ('child.stderr', err),
                             ('injector.stdout', fault_out), ('injector.stderr', fault_err)):
            if handle is None:
                continue
            try:
                raw = os.pread(handle.fileno(), os.fstat(handle.fileno()).st_size, 0)
                record['raw_streams'][name] = {'path': str(output / name),
                    'actual_read_hex': raw.hex(), 'sha256': hashlib.sha256(raw).hexdigest(),
                    'stream_end': None}
            except BaseException as retain_error:
                record['raw_streams'][name] = {'path': str(output / name),
                    'actual_read_hex': None, 'sha256': None, 'stream_end': None,
                    'error': error(retain_error)}
                if primary is not None:
                    primary.add_note('Actual raw stream readback failed: ' + repr(retain_error))
                else:
                    primary = retain_error
        if pidfd is not None:
            try:
                os.close(pidfd)
            except BaseException as close_error:
                record['cleanup'].append({'owner': 'held-pidfd', 'error': error(close_error)})
                if primary is not None:
                    primary.add_note('Actual held pidfd close failed: ' + repr(close_error))
                else:
                    primary = close_error
        for handle in handles:
            try:
                handle.flush(); os.fsync(handle.fileno()); handle.close()
            except BaseException as close_error:
                record['cleanup'].append({'owner': 'retained-stream', 'error': error(close_error)})
                if primary is not None:
                    primary.add_note('Actual stream close failed: ' + repr(close_error))
                else:
                    primary = close_error
        for owned in (child, injector):
            if owned is not None:
                for stream in (owned.stdin, owned.stdout, owned.stderr):
                    if stream is not None and not stream.closed:
                        try:
                            stream.close()
                        except BaseException as close_error:
                            record['cleanup'].append({'owner': 'owned-process-stream', 'error': error(close_error)})
                            if primary is not None:
                                primary.add_note('Actual process stream close failed: ' + repr(close_error))
                            else:
                                primary = close_error
        if primary is not None and sys.exc_info()[1] is None:
            raise primary


def withdraw(path, output, label, observed):
    require(os.path.lexists(path), 'STARTUP_FORMATION_REAL_OWNER_PREIMAGE_REQUIRED')
    before = path.lstat()
    record = {'path': str(path), 'device': before.st_dev, 'inode': before.st_ino,
              'mode': stat.S_IMODE(before.st_mode), 'links': before.st_nlink,
              'sha256': hashlib.sha256(path.read_bytes()).hexdigest() if stat.S_ISREG(before.st_mode) else None,
              'retained': str(output / label), 'rename_completed': False}
    observed['owner_interventions'].append(record)
    require(not os.path.lexists(output / label), 'STARTUP_FORMATION_EXCLUSIVE_PREIMAGE_RETENTION_REQUIRED')
    os.rename(path, output / label); record['rename_completed'] = True
    F.sync(path.parent); F.sync(output)
    after = (output / label).lstat()
    require((before.st_dev, before.st_ino) == (after.st_dev, after.st_ino),
            'STARTUP_FORMATION_WITHDRAWAL_IDENTITY_CHANGED')
    return output / label


def form(plan_path):
    plan, raw, descriptor = selected_plan(plan_path)
    require(os.geteuid() == 0, 'STARTUP_FORMATION_ROOT_OWNER_REQUIRED')
    output = Path(plan['result_directory'])
    observed = {'schema': 'worldline.original-startup-formation-observation-v1',
                'plan_raw_hex': raw.hex(), 'plan_sha256': hashlib.sha256(raw).hexdigest(),
                'case': plan['case'], 'before': None, 'after': None, 'child': None,
                'owner_interventions': [], 'error': None, 'phase_one_acceptance': False}
    primary = None
    try:
        from worldline.protected_startup import StartupLease, canonical
        validation_lease = StartupLease(Path(plan['startup_descriptor']))
        validation_primary = None
        try:
            require_fresh(validation_lease)
        except BaseException as caught:
            validation_primary = caught
            raise
        finally:
            try:
                validation_lease.close()
            except BaseException as close_error:
                if validation_primary is None:
                    raise
                validation_primary.add_note('Actual initial validation lease close failed: ' + repr(close_error))
        before, genesis = private_snapshot(descriptor); observed['before'] = before
        require(before['history'] == [] and all(row[3] == 'UNUSED' for row in before['intents']),
                'STARTUP_FORMATION_NEVER_RESET_EXISTING_ADMISSION')
        name = plan['journal_name']
        require(name in genesis['journals'], 'STARTUP_FORMATION_ORIGINAL_JOURNAL_NAME_REQUIRED')
        item = genesis['journals'][name]; path = Path(item['path'])
        require(all(not os.path.lexists(record['path']) for record in genesis['journals'].values()),
                'STARTUP_FORMATION_NEW_UNUSED_ORIGINAL_JOURNALS_REQUIRED')
        case = plan['case']
        if case in FAULT_CASES or case in ('CONSUMED_MISSING', 'COMPOSED_NATIVE_PROOF'):
            execute_child(plan_path, plan, output, path, observed)
        if case == 'CONSUMED_MISSING':
            withdraw(path, output, 'retained-consumed-journal', observed)
        elif case in ('INTENT_CHANGED', 'SYMLINK', 'MULTILINK'):
            kept = withdraw(path, output, 'retained-intent-journal', observed)
            if case == 'INTENT_CHANGED':
                F.create(path, kept.read_bytes() + b'owner-negative-control\n')
            elif case == 'SYMLINK':
                os.symlink(kept, path); F.sync(path.parent)
            else:
                os.link(kept, path, follow_symlinks=False); F.sync(path.parent)
        elif case == 'PRESENT_UNUSED':
            from worldline.protected_startup import canonical
            F.create(path, canonical(item['initial_envelope']) + b'\n')
        elif case == 'MISSING_LOCK':
            withdraw(Path(descriptor['paths']['state']) / 'worldline-store.lock', output,
                     'retained-original-store-lock', observed)
        elif case == 'LEGACY_ENDPOINT':
            endpoint = Path(descriptor['paths']['runtime']) / 'worldlined.sock'
            require(not os.path.lexists(endpoint), 'STARTUP_FORMATION_LEGACY_ENDPOINT_ALREADY_PRESENT')
            with socket.socket(socket.AF_UNIX) as legacy:
                legacy.bind(str(endpoint))
            F.sync(endpoint.parent)
            info = endpoint.lstat()
            require(stat.S_ISSOCK(info.st_mode), 'STARTUP_FORMATION_REAL_LEGACY_SOCKET_REQUIRED')
            observed['owner_interventions'].append({'socket': str(endpoint), 'device': info.st_dev,
                                                    'inode': info.st_ino, 'actual_bind': True})
        elif case == 'CAPABILITY_MISSING':
            withdraw(Path(plan['capability_member']), output, 'retained-capability-member', observed)
        elif case == 'CAPABILITY_UNSAFE':
            member = F.protected(Path(plan['capability_member']), directory=True)
            info = member.lstat(); os.chmod(member, stat.S_IMODE(info.st_mode) | stat.S_IWOTH)
            observed['owner_interventions'].append({'path': str(member), 'prior_mode': stat.S_IMODE(info.st_mode),
                                                    'actual_mode': stat.S_IMODE(member.lstat().st_mode)})
        after, _genesis = private_snapshot(descriptor); observed['after'] = after
        chosen = [row for row in after['intents'] if row[0] == name]
        require(len(chosen) == 1, 'STARTUP_FORMATION_COMPLETE_SELECTED_LEDGER_ROW_REQUIRED')
        expected_state = ('INTENT' if case in FAULT_CASES else
                          'CONSUMED' if case in ('CONSUMED_MISSING', 'COMPOSED_NATIVE_PROOF') else 'UNUSED')
        require(chosen[0][3] == expected_state,
                'STARTUP_FORMATION_ACTUAL_ORIGINAL_STATE_NOT_ESTABLISHED')
        if case == 'COMPOSED_NATIVE_PROOF':
            from worldline.protected_startup import private_bytes
            require({row[0]: row[3] for row in after['intents']} ==
                    {actual_name: 'CONSUMED' for actual_name in genesis['journals']},
                    'STARTUP_FORMATION_COMPLETE_CONSUMED_FRONTIER_ROSTER_REQUIRED')
            observed['complete_frontier_journal_readback'] = []
            for actual_name, actual_record in genesis['journals'].items():
                actual_path = Path(actual_record['path'])
                actual_raw = private_bytes(actual_path)
                info = actual_path.lstat()
                observed['complete_frontier_journal_readback'].append({'name': actual_name,
                    'path': str(actual_path), 'actual_raw_hex': actual_raw.hex(),
                    'device': info.st_dev, 'inode': info.st_ino, 'mode': stat.S_IMODE(info.st_mode),
                    'links': info.st_nlink})
                require(actual_raw == canonical(actual_record['initial_envelope']) + b'\n',
                        'STARTUP_FORMATION_EXACT_COMPLETE_FRONTIER_JOURNAL_REQUIRED')
        if case == 'INTENT_MISSING' or case == 'CONSUMED_MISSING':
            require(not os.path.lexists(path), 'STARTUP_FORMATION_MISSING_CASE_NOT_ESTABLISHED')
        elif case in ('INTENT_PRESENT', 'PRESENT_UNUSED'):
            require(path.read_bytes() == canonical(item['initial_envelope']) + b'\n',
                    'STARTUP_FORMATION_EXACT_PRESENT_CASE_NOT_ESTABLISHED')
        fixture = {'startup_descriptor': plan['startup_descriptor'], 'journal_name': name,
                   'capability_member': plan['capability_member']}
        F.create(output / 'additional-startup-fixture.json', F.canonical(fixture) + b'\n')
        return observed
    except BaseException as caught:
        primary = caught; observed['error'] = error(caught)
        raise
    finally:
        try:
            F.create(output / 'formation-observation.json', F.canonical(observed) + b'\n')
        except BaseException as retained_error:
            if primary is None:
                raise
            primary.add_note('Actual partial formation retention failed: ' + repr(retained_error))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--child', action='store_true')
    args = parser.parse_args()
    if args.child:
        child_action(args.plan)
    else:
        print(F.canonical(form(args.plan)).decode('utf-8'))


if __name__ == '__main__':
    main()
