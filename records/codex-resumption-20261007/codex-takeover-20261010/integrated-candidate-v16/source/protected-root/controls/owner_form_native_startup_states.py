"""Form native startup specimens using real original operation and fault paths.

This source-selected producer runs today. It does not supply native states,
rewrite SQL/history, reset a journal, or replace the unchanged original controls.
Every fixture needs prior genuine complete owner journal admission. The one
surviving-intent pause is before an actual EFFECT_INTENT following RESERVED.
"""
from __future__ import annotations
import sys
_approved = sys.modules.get('_worldline_approved_source_loader')
if _approved is None:
    raise SystemExit('NATIVE_STATE_FORMATION_EARLY_SOURCE_REQUIRED')
_source = _approved.current()
if type(_source) is not _approved.ApprovedSourceLease:
    raise SystemExit('NATIVE_STATE_FORMATION_ACTUAL_SOURCE_LEASE_REQUIRED')
_source.check()
import argparse
import asyncio
import dataclasses
import hashlib
import json
import math
import os
from pathlib import Path
import select
import signal
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
from live_campaign import Campaign, fault_arm, selected_json, private_directory
_lease = _source  # exact same current pinned loader lease used by original Campaign

SCHEMA = 'worldline.original-native-startup-state-formation-v1'
CASES = ('FULL_ROSTER', 'RETAIN_UNKNOWN', 'SURVIVING_NEXT_INTENT')
ROOT_NAMES = {
    'FULL_ROSTER': 'cosmogony-canonical-v1.control-p1-native-startup-full-roster-816aefa4',
    'RETAIN_UNKNOWN': 'cosmogony-canonical-v1.control-p1-native-startup-retain-unknown-80b34903',
    'SURVIVING_NEXT_INTENT': 'cosmogony-canonical-v1.control-p1-native-startup-surviving-next-intent-daf0a504',
}


def require(value, reason):
    if not value:
        raise RuntimeError(reason)


def error(value):
    return {'module': type(value).__module__, 'type': type(value).__qualname__,
            'message': str(value), 'repr': repr(value), 'errno': getattr(value, 'errno', None),
            'notes': list(getattr(value, '__notes__', ()))}


def lossless(value):
    """Retain raw actual fields without importing a class named by a record."""
    kind = type(value)
    if kind is bytes:
        return {'bytes_hex': value.hex()}
    if kind in (tuple, list):
        return [lossless(item) for item in value]
    if kind is dict:
        require(all(type(key) is str for key in value), 'NATIVE_STATE_JSON_KEY_TYPE')
        return {key: lossless(item) for key, item in value.items()}
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {'actual_type': kind.__module__ + '.' + kind.__qualname__,
                'fields': {field.name: lossless(getattr(value, field.name))
                           for field in dataclasses.fields(value)}}
    require(value is None or kind in (str, int, float, bool), 'NATIVE_STATE_RAW_FIELD_TYPE')
    return value


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def private_stream(path):
    return os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
        os.O_NOFOLLOW | os.O_CLOEXEC, 0o600), 'wb')


def publish(path, value):
    """Exclusive durable observations only; publication cannot settle a deficit."""
    raw = F.canonical(lossless(value)) + b'\n'
    path = Path(path)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    require(path.read_bytes() == raw, 'NATIVE_STATE_RETAINED_READBACK_CHANGED')
    parent = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        os.fsync(parent)
    finally:
        os.close(parent)
    return {'path': str(path), 'sha256': sha(raw), 'bytes': len(raw)}


def selected_plan(path, *, child=False):
    require(os.geteuid() == 0 and sys.flags.isolated and sys.flags.no_site
            and sys.dont_write_bytecode, 'NATIVE_STATE_ROOT_I_S_B_REQUIRED')
    raw = _source.file(str(path), ('DATA',))
    plan = F.exact(raw)
    require(type(plan) is dict and set(plan) == {
        'schema', 'case', 'startup_descriptor', 'capture_source_root', 'result_directory',
        'observer', 'client', 'fault_operator', 'child_entry', 'child_envelope',
        'timeout', 'injector_timeout'}, 'NATIVE_STATE_COMPLETE_PLAN_REQUIRED')
    require(plan['schema'] == SCHEMA and plan['case'] in CASES, 'NATIVE_STATE_CASE_REQUIRED')
    for name, expected in (('timeout', 600), ('injector_timeout', 120)):
        value = plan[name]
        require(type(value) in (int, float) and math.isfinite(value) and value == expected,
                'NATIVE_STATE_ORIGINAL_FINITE_CAP_REQUIRED')
    require(plan['child_entry'] == str(Path(__file__).absolute()), 'NATIVE_STATE_CHILD_ENTRY_SPLIT')
    _source.file(plan['child_entry'], ('SOURCE', 'ENTRY'))
    require(type(child) is bool, 'NATIVE_STATE_EXACT_CALLER_CHILD_ROUTE_REQUIRED')
    if child:
        # This is the already-held envelope of this actual approved child. Its
        # bytes are authenticated by the original lease check, not recursively
        # embedded as a FILE member of itself. Parent still selects it as DATA.
        actual = _source.check()
        require(plan['child_envelope'] == _source.envelope_path
                and actual['envelope_path'] == plan['child_envelope']
                and actual['envelope_bytes_hex'] == _source.envelope.hex(),
                'NATIVE_STATE_ACTUAL_HELD_CHILD_ENVELOPE_SPLIT')
    else:
        _source.file(plan['child_envelope'], ('DATA',))
    _source.file(plan['observer'], ('DATA',))
    # Preserve the original Campaign.fault selected DATA role. The actual
    # original installed tracer still needs execute eligibility and ownership.
    _source.file(plan['fault_operator'], ('DATA',))
    require(F.protected(Path(plan['fault_operator'])).lstat().st_mode & 0o111,
            'NATIVE_STATE_ACTUAL_INJECTOR_EXECUTE_ELIGIBILITY_REQUIRED')
    descriptor = F.exact(_source.file(plan['startup_descriptor'], ('DATA',)))
    root = Path(descriptor['paths']['authority_root'])
    require(root == Path('/srv') / ROOT_NAMES[plan['case']], 'NATIVE_STATE_EXACT_ORIGINAL_ROOT_REQUIRED')
    require(type(descriptor.get('root_worker')) is dict, 'NATIVE_STATE_COMPLETE_ROOT_WORKER_REQUIRED')
    _source.directory_or_absent(plan['capture_source_root'])
    require(Path(plan['capture_source_root']) == Path(descriptor['runtime']['worldline_source']),
            'NATIVE_STATE_CAPTURE_SOURCE_SPLIT')
    _source.directory_or_absent(str(Path(descriptor['runtime']['worldline_source']) / 'runtime'))
    output = F.protected(Path(plan['result_directory']), True)
    require(not output.lstat().st_mode & 0o077 and output != root and not output.is_relative_to(root),
            'NATIVE_STATE_EXTERNAL_PRIVATE_RETENTION_REQUIRED')
    client = plan['client']
    require(type(client) is dict and set(client) == {'request', 'early_envelope', 'environment', 'timeout'},
            'NATIVE_STATE_COMPLETE_ORIGINAL_CLIENT_REQUIRED')
    require(type(client['timeout']) in (int, float) and client['timeout'] == 600,
            'NATIVE_STATE_ORIGINAL_SOURCE_OWNER_CAP_REQUIRED')
    selected = F.exact(_source.file(client['request'], ('DATA',)))
    require(selected['endpoint'] == descriptor['endpoint']['path']
            and selected['uid'] == descriptor['endpoint']['requester_uid']
            and selected['gid'] == descriptor['endpoint']['requester_gid'],
            'NATIVE_STATE_ACTUAL_ORIGINAL_CLIENT_DOMAIN_REQUIRED')
    _source.check()
    return plan, raw, descriptor


def read_owner_state(descriptor):
    """Read retained actual SQL and journal bytes; never write or reconcile."""
    root = Path(descriptor['paths']['authority_root'])
    state = root / 'authority/issuer/state'
    head = state / 'worldline-operation-head.sqlite'
    journal = state / 'worldline-operations.json'
    result = {'head_database': str(head), 'journal': str(journal)}
    if head.is_file():
        F.protected(head)
        with sqlite3.connect(head.as_uri() + '?mode=ro', uri=True) as db:
            require(db.execute('PRAGMA quick_check').fetchall() == [('ok',)],
                    'NATIVE_STATE_ACTUAL_HEAD_CORRUPT')
            result['head_columns'] = [row[1] for row in db.execute('PRAGMA table_info(canonical_operation_head)')]
            result['head_rows'] = db.execute('SELECT * FROM canonical_operation_head ORDER BY name').fetchall()
    else:
        result['head_rows'] = None
    if os.path.lexists(journal):
        held = F.protected(journal).lstat()
        result['journal_raw'] = journal.read_bytes()
        result['journal_identity'] = {'device': held.st_dev, 'inode': held.st_ino,
            'mode': held.st_mode, 'uid': held.st_uid, 'gid': held.st_gid}
    else:
        result['journal_raw'] = None
    return result


class NativeCampaign(Campaign):
    """Reuse genuine original client/injector ownership, with a closed new plan."""
    def __init__(self, path, *, child=False):
        self.plan, self.plan_raw, self.original_descriptor = selected_plan(path, child=child)
        self.plan_path = str(path)
        self.name = self.plan['case']
        self.spec = {'startup_descriptor': self.plan['startup_descriptor'],
                     'result_directory': self.plan['result_directory'], 'timeout': self.plan['timeout']}
        self.out = Path(self.spec['result_directory'])
        self.records = []; self.source_owners = []; self.children = []
        self.tasks = []; self.fault_tasks = []; self.leases = []
        self.server = None; self.router = None; self.endpoint_identity = None
        self.boundary_seen = False
        self.native_records = []
        self.absolute_deadline = time.monotonic() + self.plan['timeout']

    async def client(self, action):
        selected = selected_json(action['request'])
        require(selected['endpoint'] == self.original_descriptor['endpoint']['path'],
                'CAMPAIGN_ORIGINAL_ENDPOINT_SPLIT')
        require(selected['uid'] == self.original_descriptor['endpoint']['requester_uid']
                and selected['gid'] == self.original_descriptor['endpoint']['requester_gid'],
                'CAMPAIGN_ORIGINAL_ACTOR_DOMAIN_CHANGED')
        entry = str(Path(__file__).with_name('original_client.py'))
        owner_path = action['request'] + '.source-owner.json'
        owner = selected_json(owner_path)
        require(owner['schema'] == 'worldline.fixed-original-client-source-owner-v1'
                and owner['request'] == action['request'] and owner['entry'] == entry
                and owner['descriptor'] == self.spec['startup_descriptor']
                and owner['timeout'] == action['timeout'],
                'CAMPAIGN_FIXED_SOURCE_OWNER_ORIGINAL_BINDING_REQUIRED')
        owner_output = private_directory(owner['retention_directory'])
        require(not any(owner_output.iterdir()), 'CAMPAIGN_SOURCE_OWNER_OUTPUT_ALREADY_USED')
        _lease.file(entry, ('ENTRY',))
        _lease.file(action['early_envelope'], ('DATA',))
        command = [_lease.interpreter, '-I', '-S', '-B', _lease.helper_path,
                   '--bootstrap-envelope', action['early_envelope'], '--entry', entry,
                   '--request', action['request']]
        index = len(self.children)
        stdout = self.out / ('client-' + str(index) + '.stdout')
        stderr = self.out / ('client-' + str(index) + '.stderr')
        with stdout.open('xb') as out, stderr.open('xb') as err:
            child = subprocess.Popen(command, env=action['environment'], stdout=out, stderr=err)
            self.children.append(child)
            ownership = {'action': action, 'argv': command, 'pid': child.pid, 'actual_wait': None,
                         'owner_birth': None, 'stdout': str(stdout), 'stderr': str(stderr),
                         'source_owner_selection': owner_path, 'source_owner_retention': str(owner_output),
                         'actual_actor_custody': 'INNER_ARCHIVE_AND_MAIN_COLLECTOR_REQUIRED'}
            self.source_owners.append(ownership)
            wait = await self.wait_original_client(child, ownership, out, err, stdout, stderr, action)
        row = {**ownership, 'stdout_sha256': sha(stdout.read_bytes()), 'stderr_sha256': sha(stderr.read_bytes()),
               'source_owner_archive_sha256': sha((owner_output / 'source-owner.archive').read_bytes())}
        row['source_owner_retained_files'] = [
            {'path': str(path), 'sha256': sha(path.read_bytes()),
             'stat': {'device': path.stat(follow_symlinks=False).st_dev,
                      'inode': path.stat(follow_symlinks=False).st_ino,
                      'mode': path.stat(follow_symlinks=False).st_mode,
                      'uid': path.stat(follow_symlinks=False).st_uid,
                      'gid': path.stat(follow_symlinks=False).st_gid,
                     'size': path.stat(follow_symlinks=False).st_size},
             'bytes': path.stat(follow_symlinks=False).st_size,
             'mode': stat.S_IMODE(path.stat(follow_symlinks=False).st_mode)}
            for path in sorted(owner_output.iterdir())]
        self.records.append(row)
        footer_marker = b'SOURCE_OWNER_FINAL_CLOSE '
        owner_stderr = stderr.read_bytes()
        marker = owner_stderr.rfind(footer_marker)
        require(marker >= 0 and owner_stderr[marker:].count(footer_marker) == 1,
                'CAMPAIGN_ACTUAL_SOURCE_OWNER_FINAL_CLOSE_MISSING')
        row['source_owner_final_close'] = json.loads(owner_stderr[marker + len(footer_marker):].split(b'\n', 1)[0])
        ownership['source_owner_final_close'] = row['source_owner_final_close']
        if 'expected_error' in action:
            require(wait == 1 and ('RuntimeError: ' + action['expected_error']).encode() in stderr.read_bytes(),
                    'CAMPAIGN_ORIGINAL_TRANSPORT_EOF_REFUSAL_CHANGED')
        else:
            require(wait == 0, 'CAMPAIGN_ACTUAL_ORIGINAL_CLIENT_FAILED')
        return row

    async def wait_original_client(self, child, ownership, out, err, stdout, stderr, action):
        """Retain actual source-owner cleanup; never kill its uncollected actor."""
        pidfd = None; primary = None; failures = []
        deadline = min(self.absolute_deadline, time.monotonic() + action['timeout'])
        ownership['cleanup'] = {'signal': None, 'actual_wait': None, 'errors': [],
                                'inner_actor_completion': 'ACTUAL_OWNER_ARCHIVE_AND_MAIN_REQUIRED'}
        try:
            pidfd = os.pidfd_open(child.pid)
            ownership['held_pidfd_info'] = Path('/proc/self/fdinfo/' + str(pidfd)).read_text()
            ownership['owner_birth'] = _approved.process_facts(child.pid)
            wait = await wait_actual(child, deadline)
            ownership['actual_wait'] = wait
            return wait
        except BaseException as failure:
            primary = failure
            ownership['failure'] = error(failure)
            raise
        finally:
            # SIGINT raises the original Python owner's BaseException path:
            # OriginalClientSourceOwner.stop_owned_actor and owner_completion
            # retain the real inner actor stop/wait/raw archive. SIGKILL here
            # would destroy that owner while its excluded child may be live.
            if child.returncode is None:
                try:
                    _source.check()
                    if pidfd is not None:
                        actual = signal.pidfd_send_signal(pidfd, signal.SIGINT)
                        ownership['cleanup']['signal'] = {'call': 'pidfd_send_signal',
                            'pidfd': pidfd, 'signal': signal.SIGINT, 'return': actual}
                    else:
                        probe = os.waitpid(child.pid, os.WNOHANG)
                        ownership['cleanup']['probe_waitpid'] = probe
                        if probe[0] == child.pid:
                            child.returncode = os.waitstatus_to_exitcode(probe[1])
                        else:
                            require(probe == (0, 0), 'NATIVE_STATE_DIRECT_CLIENT_WAIT_UNKNOWN')
                            actual = os.kill(child.pid, signal.SIGINT)
                            ownership['cleanup']['signal'] = {'call': 'kill', 'pid': child.pid,
                                'signal': signal.SIGINT, 'actual_unreaped_direct_child': probe,
                                'return': actual}
                except BaseException as failure:
                    failures.append(failure)
                    ownership['cleanup']['errors'].append(error(failure))
                try:
                    ownership['cleanup']['actual_wait'] = await wait_actual(child, deadline)
                except BaseException as failure:
                    failures.append(failure)
                    ownership['cleanup']['errors'].append(error(failure))
            # Every stage is independent: a failed stream export cannot skip
            # the actual owned signal/wait, descriptor close, or other stream.
            for stream, path, label in ((out, stdout, 'stdout'), (err, stderr, 'stderr')):
                try:
                    stream.flush(); os.fsync(stream.fileno())
                except BaseException as failure:
                    failures.append(failure); ownership['cleanup']['errors'].append(error(failure))
                try:
                    raw = path.read_bytes()
                    ownership[label + '_partial_raw'] = raw
                    ownership[label + '_partial_sha256'] = sha(raw)
                except BaseException as failure:
                    failures.append(failure); ownership['cleanup']['errors'].append(error(failure))
            try:
                retained = Path(ownership['source_owner_retention'])
                ownership['actual_partial_owner_files'] = [
                    {'path': str(path), 'raw': path.read_bytes(),
                     'mode': stat.S_IMODE(path.lstat().st_mode)}
                    for path in sorted(retained.iterdir()) if path.is_file() and not path.is_symlink()]
            except BaseException as failure:
                failures.append(failure); ownership['cleanup']['errors'].append(error(failure))
            if pidfd is not None:
                attempt = {'fd': pidfd, 'return': None}
                ownership['cleanup']['pidfd_close'] = attempt
                try:
                    attempt['return'] = os.close(pidfd)
                except BaseException as failure:
                    attempt['error'] = error(failure)
                    failures.append(failure); ownership['cleanup']['errors'].append(error(failure))
            ownership['still_owned_client'] = child.pid if child.returncode is None else None
            if failures:
                if primary is None: raise failures[0]
                for failure in failures:
                    primary.add_note('Actual original-client cleanup/retention failed: ' + repr(failure))


    async def fault(self, action, armed=None):
        loop = asyncio.get_running_loop()
        deadline = None
        launch_deadline = None
        terminal = None
        child = None
        child_pidfd = None
        target_pidfd = None
        row = None
        out = None
        err = None
        primary = None
        try:
            target = action['target']
            require(target in ('front', 'worker'), 'CAMPAIGN_REAL_FAULT_TARGET_REQUIRED')
            slot = None if target == 'front' else await self.live_slot(action['timeout'])
            pid = os.getpid() if slot is None else slot.owned.worker_host_pid
            injector = action['injector']
            raw = _lease.file(injector, ('DATA',))
            require(sha(raw) == action['injector_sha256'], 'CAMPAIGN_REAL_SYSCALL_INJECTOR_CHANGED')
            path = Path(action['path'])
            root = Path(self.original_descriptor['paths']['authority_root'])
            require(path.is_relative_to(root), 'CAMPAIGN_FAULT_MUST_TARGET_DISPOSABLE_ARTIFACT')
            target_pidfd = os.pidfd_open(pid) if slot is None else os.dup(slot.owned.worker_pidfd)
            command = [injector, str(pid), str(target_pidfd), action['syscall'],
                       str(path), str(action['occurrence']), action['effect']]
            index = len(self.children)
            stdout = self.out / ('fault-' + str(index) + '.stdout')
            stderr = self.out / ('fault-' + str(index) + '.stderr')
            row = {'action': action, 'original_operation': None if slot is None else slot.operation,
                   'argv': command, 'pid': None, 'owner_birth': None, 'owned_pidfd_info': None,
                   'actual_wait': None, 'native_arm': None, 'failure': None,
                   'stdout': str(stdout), 'stderr': str(stderr), 'cleanup': None}
            self.records.append(row)
            out = stdout.open('xb')
            err = stderr.open('xb')
            child = subprocess.Popen(command, env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'},
                                     pass_fds=(target_pidfd,), stdout=out, stderr=err)
            self.children.append(child)
            launch_deadline = loop.time() + action['timeout']
            row['pid'] = child.pid
            child_pidfd = os.pidfd_open(child.pid)
            row['owned_pidfd_info'] = Path('/proc/self/fdinfo/' + str(child_pidfd)).read_text()
            require(('\nPid:\t' + str(child.pid) + '\n') in ('\n' + row['owned_pidfd_info']),
                    'CAMPAIGN_INJECTOR_HELD_PIDFD_PID_CHANGED')
            row['owner_birth'] = _approved.process_facts(child.pid)
            # Original full slot selection precedes this original full child window.
            # No ARM delay renews the terminal timeout or narrows the prior slot timeout.
            deadline = loop.time() + action['timeout']
            if armed is None:
                # Preserve wait:true's direct complete original terminal wait.
                wait = await wait_actual(child, min(self.absolute_deadline, time.monotonic() + action['timeout']))
            else:
                terminal = asyncio.create_task(wait_actual(child,
                    min(self.absolute_deadline, time.monotonic() + action['timeout'])))
                while True:
                    native_arm = fault_arm(stderr.read_bytes(), command)
                    if native_arm is not None:
                        row['native_arm'] = native_arm
                        if not armed.done(): armed.set_result(native_arm)
                        break
                    if terminal.done():
                        row['actual_wait'] = await terminal
                        raise RuntimeError('CAMPAIGN_NATIVE_FAULT_ARM_MISSING')
                    require(loop.time() < deadline, 'CAMPAIGN_NATIVE_FAULT_ARM_DEADLINE')
                    await asyncio.sleep(0.001)
                wait = await terminal
            row['actual_wait'] = wait
            actual_stderr = stderr.read_bytes()
            observed_arm = fault_arm(actual_stderr, command)
            require(observed_arm is not None, 'CAMPAIGN_NATIVE_FAULT_ARM_MISSING')
            if row['native_arm'] is None: row['native_arm'] = observed_arm
            require(observed_arm == row['native_arm'],
                    'CAMPAIGN_NATIVE_FAULT_ARM_TERMINAL_SPLIT')
            require(wait == 0 and b'ACTUAL_SYSCALL_FAULT_APPLIED' in actual_stderr,
                    'CAMPAIGN_GENUINE_FILE_IO_OR_CRASH_INJECTION_NOT_EXERCISED')
            return row
        except BaseException as error:
            primary = error
            if row is not None:
                row['failure'] = {'type': type(error).__name__, 'reason': str(error)}
            if armed is not None and not armed.done():
                armed.set_exception(error)
            raise
        finally:
            errors = []
            if child is not None and child.returncode is None:
                cleanup = {'signal': None, 'actual_wait': None, 'failure': None}
                row['cleanup'] = cleanup
                try:
                    # Signal only the actually held injector; never its target/front/worker.
                    require(child_pidfd is not None, 'CAMPAIGN_INJECTOR_CLEANUP_HELD_PIDFD_REQUIRED')
                    actual_return = signal.pidfd_send_signal(child_pidfd, signal.SIGKILL)
                    cleanup['signal'] = {'call': 'pidfd_send_signal', 'pidfd': child_pidfd,
                                         'signal': signal.SIGKILL, 'return': actual_return}
                except ProcessLookupError:
                    cleanup['signal'] = {'call': 'pidfd_send_signal', 'pidfd': child_pidfd,
                                         'signal': signal.SIGKILL, 'error': 'ProcessLookupError'}
                except BaseException as error:
                    errors.append(error)
                try:
                    # Cleanup cannot borrow a fresh timeout or extend the selected action deadline.
                    cleanup['actual_wait'] = await wait_actual(child, min(self.absolute_deadline, time.monotonic() +
                        max(0, (deadline if deadline is not None else launch_deadline) - loop.time())))
                except BaseException as error:
                    cleanup['failure'] = {'type': type(error).__name__, 'reason': str(error)}
                    errors.append(error)
            if terminal is not None:
                if not terminal.done(): terminal.cancel()
                retained_terminal = (await asyncio.gather(terminal, return_exceptions=True))[0]
                row['terminal_task_cleanup'] = (
                    {'type': type(retained_terminal).__name__, 'reason': str(retained_terminal)}
                    if isinstance(retained_terminal, BaseException) else {'actual_wait': retained_terminal})
            for stream, name in ((out, 'stdout'), (err, 'stderr')):
                if stream is not None:
                    try:
                        stream.flush(); os.fsync(stream.fileno()); stream.close()
                        row[name + '_sha256'] = sha(Path(row[name]).read_bytes())
                    except BaseException as error:
                        errors.append(error)
            for fd in (child_pidfd, target_pidfd):
                if fd is not None:
                    try:
                        os.close(fd)
                    except BaseException as error:
                        errors.append(error)
            if errors:
                if primary is None:
                    raise errors[0]
                for error in errors:
                    primary.add_note('Actual injector cleanup/retention failed: ' + repr(error))


    def retain_operation_native(self, record):
        require(type(record) is dict and record['phase'] in ('START', 'RESULT', 'EXCEPTION'),
                'NATIVE_STATE_ACTUAL_NATIVE_RECORDER_PHASE_REQUIRED')
        # This callback executes synchronously before the real call, and again
        # before any status/refusal guard. Secret-bearing full inputs go only
        # to root-owned private retained files, never generic stderr.
        _source.check()
        path = self.out / ('operation-native-' + str(len(self.native_records)) + '.json')
        self.native_records.append({'path': str(path), 'phase': record['phase'], 'retained': None})
        self.native_records[-1]['retained'] = publish(path, record)
        _source.check()
        return None

    def source_append_control(self, journal, operation, cause, capture, snapshot, native, boundaries):
        if cause != 'EFFECT_INTENT':
            return None
        require(not self.boundary_seen, 'NATIVE_STATE_DUPLICATE_SELECTED_APPEND_BOUNDARY')
        row = journal.rows.get(operation)
        require(type(row) is dict and row['state'] == 'RESERVED',
                'NATIVE_STATE_ACTUAL_RESERVED_BEFORE_LATER_APPEND_REQUIRED')
        journal.p.intact()
        from worldline.root_worker_codec import raw_archive
        actual = {'operation': operation, 'cause': cause, 'row': row,
            'capture': capture, 'snapshot': snapshot, 'native': native, 'boundaries': boundaries,
            'prior_journal': journal.raw, 'prior_head': journal.head_row()}
        archive = raw_archive(actual)
        before_row = raw_archive(row)
        path = self.out / 'actual-reserved-before-effect-intent.archive'
        with private_stream(path) as stream:
            stream.write(archive); stream.flush(); os.fsync(stream.fileno())
        require(path.read_bytes() == archive, 'NATIVE_STATE_BOUNDARY_ARCHIVE_READBACK_CHANGED')
        self.boundary_seen = True
        observed = {'kind': 'ACTUAL_RESERVED_BEFORE_EFFECT_INTENT', 'operation': operation,
                    'cause': cause, 'archive': str(path), 'sha256': sha(archive),
                    'source': _source.check()}
        print('NATIVE_STATE_APPEND_BOUNDARY ' + F.canonical(observed).decode('utf-8'), flush=True)
        os.fsync(sys.stdout.fileno())
        require(sys.stdin.buffer.readline() == b'APPEND_GO\n', 'NATIVE_STATE_REAL_ARM_HANDOFF_REQUIRED')
        require(journal.raw == actual['prior_journal'] and journal.head_row() == actual['prior_head']
                and raw_archive(journal.rows[operation]) == before_row,
                'NATIVE_STATE_CALLBACK_MUST_NOT_CHANGE_JOURNAL_OR_HEAD')
        journal.p.intact(); _source.check()
        return None

    async def run_native(self):
        from worldline.custody_control_registration import register_from_source, publish_source_observers
        from worldline.protected_startup import StartupLease
        from worldline.protected_root_worker import RootWorkerFront
        from worldline.daemon import WorldlineDaemon, _MAX_REQUEST_BYTES
        from worldline.status import StatusPublisher
        from worldline.root_worker_endpoint_router import RootEndpointRouter
        register_from_source(self.plan['observer'])
        lease = StartupLease(self.spec['startup_descriptor'])
        self.leases.append(lease)
        primary = None; cleanup_errors = []
        try:
            lease.set_operation_native_recorder(self.retain_operation_native)
            lease.construct(); lease.require_front_startup()
            principal = lease.canonical_operation_principal
            if self.name == 'SURVIVING_NEXT_INTENT':
                # The separately reviewed owner bridge verifies this callable's
                # executed source and immutable journal before/after the pause.
                principal.journal.set_source_append_control(self.source_append_control)
            daemon = WorldlineDaemon(lease.controller.paths, lease.store,
                                     StatusPublisher(lease.controller.paths, lease.store))
            lease.controller.register(daemon)
            front = RootWorkerFront(principal, lease.spec['root_worker']['owner_plan'])
            front.daemon = daemon
            self.router = RootEndpointRouter(front, daemon)
            path = Path(lease.spec['endpoint']['path'])
            require(not os.path.lexists(path), 'NATIVE_STATE_ENDPOINT_MUST_BE_EXCLUSIVE')
            self.server = await asyncio.start_unix_server(daemon._handle_client, path=str(path),
                                                        limit=_MAX_REQUEST_BYTES + 1)
            os.chown(path, 0, lease.spec['endpoint']['requester_gid']); os.chmod(path, 0o660)
            named = path.stat(); self.endpoint_identity = (named.st_dev, named.st_ino)
            principal.endpoint_identity = self.endpoint_identity
            lease.intact(); lease.loaded()
            print('NATIVE_STATE_CHILD_READY ' + F.canonical({'pid': os.getpid(),
                'endpoint': str(path), 'endpoint_device': named.st_dev, 'endpoint_inode': named.st_ino,
                'case': self.name, 'source': _source.check()}).decode('utf-8'), flush=True)
            os.fsync(sys.stdout.fileno())
            require(sys.stdin.buffer.readline() == b'GO\n', 'NATIVE_STATE_PARENT_GO_REQUIRED')
            if self.name == 'SURVIVING_NEXT_INTENT':
                # Parent owns the genuine client so killing this front cannot
                # discard an internally orphaned source-owner client wait.
                await self.server.serve_forever()
                raise RuntimeError('NATIVE_STATE_SURVIVING_CHILD_RETURNED_WITHOUT_REAL_FAULT')
            task = asyncio.create_task(self.client(self.plan['client']))
            self.tasks.append(task)
            if self.name == 'RETAIN_UNKNOWN':
                injector_raw = _source.file(self.plan['fault_operator'], ('DATA',))
                fault = {'target': 'worker', 'injector': self.plan['fault_operator'],
                    'injector_sha256': sha(injector_raw), 'syscall': 'fsync', 'occurrence': 1,
                    'path': str(Path(lease.spec['paths']['authority_root']) /
                                'authority/issuer/state/root-custody-v2.sqlite'),
                    'effect': 'kill-entry', 'timeout': self.plan['injector_timeout']}
                fault_task = asyncio.create_task(self.fault(fault, None))
                self.fault_tasks.append(fault_task); self.tasks.append(fault_task)
            await asyncio.gather(*self.tasks)
            # The real invoke/collector can still be finishing after the client
            # wait. Await its actual task; an empty task list is not closure.
            while self.router.front.phase not in ('RECONSTRUCTED_CLOSED', 'UNKNOWN_WORKER_OWNERSHIP'):
                collectors = tuple(self.router.front.collectors.values())
                if collectors:
                    await asyncio.gather(*collectors)
                else:
                    await asyncio.sleep(0.001)
            collectors = tuple(self.router.front.collectors.values())
            if collectors:
                await asyncio.gather(*collectors)
            if self.name == 'FULL_ROSTER':
                require(front.phase == 'RECONSTRUCTED_CLOSED' and front.fresh_front is not None,
                        'NATIVE_STATE_REAL_FULL_CLOSED_RECONSTRUCTION_REQUIRED')
                current = front.fresh_front.principal
                self.leases.append(current.lease)
                resources = current.resources
                from worldline.custody_startup_capture import capture as startup_capture
                with resources.gate.mutex, resources.order:
                    snapshot = resources.current_snapshot()
                    require(snapshot.rows, 'NATIVE_STATE_GENUINE_NONEMPTY_SCOPED_HISTORY_REQUIRED')
                    actual_capture = startup_capture(resources)
                from worldline.root_worker_codec import raw_archive
                path = self.out / 'actual-full-scoped-startup-capture.archive'
                raw = raw_archive(actual_capture)
                with private_stream(path) as stream:
                    stream.write(raw); stream.flush(); os.fsync(stream.fileno())
                self.records.append({'actual_complete_scoped_capture': str(path), 'sha256': sha(raw)})
            else:
                observed = lease.recovery_startup_action(principal)
                self.records.append({'actual_startup_action': lossless(observed),
                    'original_front_phase': front.phase})
                require(observed.state == 'RetainUnknown', 'NATIVE_STATE_ACTUAL_RETAIN_UNKNOWN_REQUIRED')
            require(all(child.returncode is not None for child in self.children),
                    'NATIVE_STATE_INNER_CHILD_WAIT_UNKNOWN')
        except BaseException as failure:
            primary = failure
            raise
        finally:
            if self.server is not None:
                try:
                    self.server.close(); await self.server.wait_closed()
                except BaseException as failure:
                    cleanup_errors.append(failure)
            for task in self.fault_tasks:
                if not task.done(): task.cancel()
            if self.fault_tasks:
                settled = await asyncio.gather(*self.fault_tasks, return_exceptions=True)
                self.records.append({'actual_fault_task_cleanup': [error(item) if isinstance(item, BaseException)
                    else item for item in settled]})
            client_tasks = [task for task in self.tasks if task not in self.fault_tasks]
            for task in client_tasks:
                if not task.done(): task.cancel()
            if client_tasks:
                settled = await asyncio.gather(*client_tasks, return_exceptions=True)
                self.records.append({'actual_client_task_cleanup': [error(item) if isinstance(item, BaseException)
                    else item for item in settled]})
            try:
                publish_source_observers()
            except BaseException as failure:
                cleanup_errors.append(failure)
            # Front ownership is not inferred from a stopped socket. Original
            # owner close predicates and failed-close custody remain effective.
            for owned in reversed(self.leases):
                try:
                    owned.close()
                    self.records.append({'actual_lease_close': str(owned.descriptor_path), 'return': None})
                except BaseException as failure:
                    self.records.append({'actual_lease_close': str(owned.descriptor_path),
                        'error': error(failure), 'ownership': 'UNKNOWN_RETAINED'})
                    cleanup_errors.append(failure)
            if cleanup_errors:
                if primary is None:
                    raise cleanup_errors[0]
                for failure in cleanup_errors:
                    primary.add_note('Actual native-state cleanup failed: ' + repr(failure))


def child_main(path):
    campaign = NativeCampaign(path, child=True)
    primary = None
    try:
        asyncio.run(asyncio.wait_for(campaign.run_native(), timeout=campaign.plan['timeout']))
    except BaseException as failure:
        primary = failure
        raise
    finally:
        observations = {'schema': SCHEMA + '.child-observation', 'case': campaign.name,
            'records': campaign.records, 'source_owners': campaign.source_owners,
            'operation_native_records': campaign.native_records,
            'still_owned_children': [child.pid for child in campaign.children if child.returncode is None],
            'failure': None if primary is None else error(primary), 'source': None,
            'phase_acceptance': False, 'endpoint_identity': campaign.endpoint_identity}
        try:
            observations['source'] = _source.check()
            publish(campaign.out / 'child-observation.json', observations)
        except BaseException as failure:
            if primary is None: raise
            primary.add_note('Actual child observation retention failed: ' + repr(failure))


async def wait_line(path, marker, child, deadline):
    while time.monotonic() < deadline:
        raw = path.read_bytes()
        lines = [line for line in raw.splitlines(keepends=True) if line.startswith(marker)]
        require(len(lines) <= 1, 'NATIVE_STATE_DUPLICATE_ACTUAL_HANDSHAKE')
        if lines and lines[0].endswith(b'\n'):
            return F.exact(lines[0][len(marker):])
        require(child.poll() is None, 'NATIVE_STATE_CHILD_ENDED_BEFORE_HANDSHAKE')
        await asyncio.sleep(0.001)
    raise RuntimeError('NATIVE_STATE_ORIGINAL_HANDSHAKE_DEADLINE')


async def wait_actual(child, deadline):
    # poll() performs real waitpid; the same Popen retains its actual result.
    # No executor waiter can silently outlive/renew the selected whole deadline.
    while child.poll() is None:
        if time.monotonic() >= deadline:
            raise subprocess.TimeoutExpired(child.args, 0)
        await asyncio.sleep(0.001)
    return child.wait(timeout=0)


def remaining(deadline):
    return max(0, deadline - time.monotonic())


async def parent_main(path):
    plan, raw, descriptor = selected_plan(path)
    out = Path(plan['result_directory'])
    require(not any(out.iterdir()), 'NATIVE_STATE_OUTPUT_ALREADY_USED')
    deadline = time.monotonic() + plan['timeout']
    observations = {'schema': SCHEMA + '.parent-observation', 'case': plan['case'],
        'plan': str(path), 'plan_raw': raw, 'child': None, 'injector': None,
        'source_owner_client': None, 'actual_before': read_owner_state(descriptor),
        'actual_after': None, 'source': None, 'failure': None, 'cleanup': [],
        'phase_acceptance': False, 'original_controls_still_required': True}
    child = None; child_fd = None; injector = None; injector_fd = None
    streams = []; primary = None; client_task = None; client_campaign = None
    try:
        _source.check()
        stdout = out / 'child.stdout'; stderr = out / 'child.stderr'
        child_out = private_stream(stdout); streams.append(child_out)
        child_err = private_stream(stderr); streams.append(child_err)
        command = [_source.interpreter, '-I', '-S', '-B', _source.helper_path,
            '--bootstrap-envelope', plan['child_envelope'], '--entry', plan['child_entry'],
            '--child', '--plan', str(path)]
        observations['child'] = {'argv': command, 'pid': None, 'birth': None, 'actual_wait': None,
            'stdout': str(stdout), 'stderr': str(stderr), 'cleanup_wait': None, 'signal': None}
        child = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=child_out, stderr=child_err,
            env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'})
        observations['child']['pid'] = child.pid
        child_fd = os.pidfd_open(child.pid)
        observations['child']['birth'] = _approved.process_facts(child.pid)
        ready = await wait_line(stdout, b'NATIVE_STATE_CHILD_READY ', child, deadline)
        require(ready['pid'] == child.pid and ready['case'] == plan['case']
                and ready['endpoint'] == descriptor['endpoint']['path'],
                'NATIVE_STATE_ACTUAL_CHILD_READY_BINDING_SPLIT')
        observations['child']['actual_ready'] = ready
        child.stdin.write(b'GO\n'); child.stdin.flush()
        if plan['case'] == 'SURVIVING_NEXT_INTENT':
            # The parent owns the actual original client and waits it, including
            # its original inner archive. No preformed request/result is used.
            client_campaign = NativeCampaign(path)
            action = {**plan['client'], 'expected_error': 'CLIENT_ORIGINAL_RESPONSE_EOF_WITHOUT_RESULT'}
            client_campaign.absolute_deadline = deadline
            client_task = asyncio.create_task(client_campaign.client(action))
            boundary = await wait_line(stdout, b'NATIVE_STATE_APPEND_BOUNDARY ', child, deadline)
            require(boundary['kind'] == 'ACTUAL_RESERVED_BEFORE_EFFECT_INTENT'
                    and boundary['cause'] == 'EFFECT_INTENT', 'NATIVE_STATE_GENUINE_BOUNDARY_REQUIRED')
            observed_path = out / 'actual-reserved-before-effect-intent.archive'
            require(boundary['archive'] == str(observed_path)
                    and sha(observed_path.read_bytes()) == boundary['sha256'],
                    'NATIVE_STATE_ACTUAL_BOUNDARY_ARCHIVE_SPLIT')
            observations['child']['actual_append_boundary'] = boundary
            fault_stdout = out / 'injector.stdout'; fault_stderr = out / 'injector.stderr'
            fault_out = private_stream(fault_stdout); streams.append(fault_out)
            fault_err = private_stream(fault_stderr); streams.append(fault_err)
            fault_path = Path(descriptor['paths']['authority_root']) / 'authority/issuer/state/worldline-operations.json'
            fault_command = [plan['fault_operator'], str(child.pid), str(child_fd), 'fsync',
                             str(fault_path), '1', 'kill-exit']
            observations['injector'] = {'argv': fault_command, 'pid': None, 'birth': None,
                'actual_wait': None, 'actual_arm': None, 'stdout': str(fault_stdout),
                'stderr': str(fault_stderr), 'signal': None, 'cleanup_wait': None}
            injector = subprocess.Popen(fault_command, pass_fds=(child_fd,), stdout=fault_out, stderr=fault_err,
                env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'})
            observations['injector']['pid'] = injector.pid
            injector_fd = os.pidfd_open(injector.pid)
            observations['injector']['birth'] = _approved.process_facts(injector.pid)
            fault_deadline = min(deadline, time.monotonic() + plan['injector_timeout'])
            while remaining(fault_deadline):
                arm = fault_arm(fault_stderr.read_bytes(), fault_command)
                if arm is not None: break
                require(injector.poll() is None, 'NATIVE_STATE_INJECTOR_ENDED_BEFORE_ARM')
                await asyncio.sleep(0.001)
            else:
                raise RuntimeError('NATIVE_STATE_GENUINE_ARM_DEADLINE')
            observations['injector']['actual_arm'] = arm
            _source.check()
            child.stdin.write(b'APPEND_GO\n'); child.stdin.flush()
            observations['injector']['actual_wait'] = await wait_actual(injector, fault_deadline)
            require(observations['injector']['actual_wait'] == 0
                    and b'ACTUAL_SYSCALL_FAULT_APPLIED' in fault_stderr.read_bytes(),
                    'NATIVE_STATE_REAL_APPEND_FAULT_NOT_APPLIED')
        observations['child']['actual_wait'] = await wait_actual(child, deadline)
        if plan['case'] == 'SURVIVING_NEXT_INTENT':
            require(observations['child']['actual_wait'] == -signal.SIGKILL,
                    'NATIVE_STATE_ACTUAL_SELECTED_CRASH_WAIT_REQUIRED')
            observations['source_owner_client'] = await asyncio.wait_for(client_task, timeout=remaining(deadline))
            after = read_owner_state(descriptor)
            require(after['head_rows'] is not None, 'NATIVE_STATE_ACTUAL_SURVIVING_HEAD_REQUIRED')
            columns = after['head_columns']; rows = [dict(zip(columns, row)) for row in after['head_rows']]
            matched = [row for row in rows if row['name'] == 'worldline-operations']
            require(len(matched) == 1 and matched[0]['state'] == 'INTENT'
                    and matched[0]['head'] == sha(matched[0]['prior_envelope'])
                    and matched[0]['next_envelope'] == after['journal_raw'],
                    'NATIVE_STATE_ACTUAL_INTENT_NEXT_BYTES_REQUIRED')
            observations['actual_after'] = after
        else:
            require(observations['child']['actual_wait'] == 0, 'NATIVE_STATE_GENUINE_FORMATION_CHILD_FAILED')
            child_observation = F.exact((out / 'child-observation.json').read_bytes())
            require(child_observation['case'] == plan['case'] and not child_observation['still_owned_children'],
                    'NATIVE_STATE_ACTUAL_INNER_CHILD_WAIT_MISSING')
            observations['actual_child_observation'] = child_observation
            observations['actual_after'] = read_owner_state(descriptor)
        _source.check()
    except BaseException as failure:
        primary = failure; observations['failure'] = error(failure)
        raise
    finally:
        failures = []
        # Only these directly owned producer/injector children may be signalled.
        # Missing terminal waits remain UNKNOWN and receive no success credit.
        for process, pidfd, name in ((injector, injector_fd, 'injector'), (child, child_fd, 'child')):
            if process is not None and process.returncode is None:
                row = observations[name]
                try:
                    require(pidfd is not None, 'NATIVE_STATE_CLEANUP_HELD_PIDFD_REQUIRED')
                    row['signal'] = {'call': 'pidfd_send_signal', 'signal': signal.SIGKILL,
                                     'return': signal.pidfd_send_signal(pidfd, signal.SIGKILL)}
                except BaseException as failure:
                    failures.append(failure); observations['cleanup'].append(error(failure))
                try:
                    row['cleanup_wait'] = await wait_actual(process, deadline)
                except BaseException as failure:
                    failures.append(failure); observations['cleanup'].append(error(failure))
        if child is not None and child.stdin is not None:
            try:
                child.stdin.close()
            except BaseException as failure:
                failures.append(failure); observations['cleanup'].append(error(failure))
        if client_task is not None:
            observations['actual_client_task_done'] = client_task.done()
            observations['actual_parent_source_owners'] = client_campaign.source_owners
            observations['actual_parent_client_records'] = client_campaign.records
            if not client_task.done():
                client_task.cancel()
            result = (await asyncio.gather(client_task, return_exceptions=True))[0]
            observations['actual_client_task_cleanup'] = (error(result) if isinstance(result, BaseException) else result)
        for stream in streams:
            try:
                stream.flush(); os.fsync(stream.fileno()); stream.close()
            except BaseException as failure:
                failures.append(failure); observations['cleanup'].append(error(failure))
        for pidfd in (injector_fd, child_fd):
            if pidfd is not None:
                try:
                    os.close(pidfd)
                except BaseException as failure:
                    failures.append(failure); observations['cleanup'].append(error(failure))
        for name in ('child', 'injector'):
            row = observations[name]
            if row is not None:
                for stream_name in ('stdout', 'stderr'):
                    try:
                        data = Path(row[stream_name]).read_bytes()
                        row[stream_name + '_raw'] = data
                        row[stream_name + '_sha256'] = sha(data)
                    except BaseException as failure:
                        failures.append(failure); observations['cleanup'].append(error(failure))
        try:
            if observations['actual_after'] is None:
                observations['actual_after'] = read_owner_state(descriptor)
        except BaseException as failure:
            failures.append(failure); observations['cleanup'].append(error(failure))
        try:
            observations['source'] = _source.check()
        except BaseException as failure:
            failures.append(failure); observations['cleanup'].append(error(failure))
        try:
            publish(out / 'formation-observation.json', observations)
        except BaseException as failure:
            failures.append(failure)
        if failures:
            if primary is None: raise failures[0]
            for failure in failures:
                primary.add_note('Actual formation cleanup/retention failed: ' + repr(failure))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--child', action='store_true')
    parser.add_argument('--plan', required=True)
    args = parser.parse_args()
    if args.child:
        child_main(args.plan)
    else:
        asyncio.run(parent_main(args.plan))


if __name__ == '__main__':
    main()
