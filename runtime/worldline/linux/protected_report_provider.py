"""Daemon-owned protected-report acquisition; admission belongs to the native core.

No process label is evidence. Kernel peer pidfds and namespace objects are borrowed
only long enough to duplicate them. Linux read leases exclude source writers; held
no-follow directory edges also expose moves/unlinks which leases do not prevent.
A lease break is retained even when the kernel subsequently forces the lease away.
The original report collector and its error precedence remain authoritative for I/O.
"""
from __future__ import annotations

import base64
import copy
import errno
import hashlib
import fcntl
import json
import os
from pathlib import Path
import select
import signal
import stat
import struct
import threading

from ..raw_observation import exception_observation, optional_bytes, retain_observation
from ..report import MAX_REPORT_BYTES

SCHEMA = 'worldline-protected-report-capture-v1'
_DIR = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
_FILE = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK
_SEALS = fcntl.F_SEAL_WRITE | fcntl.F_SEAL_GROW | fcntl.F_SEAL_SHRINK | fcntl.F_SEAL_SEAL


def object_stat(value, *, complete=True):
    fields = {'device': value.st_dev, 'inode': value.st_ino, 'mode': value.st_mode,
              'uid': value.st_uid, 'gid': value.st_gid}
    if complete:
        fields.update(size=value.st_size, mtime_ns=value.st_mtime_ns,
                      ctime_ns=value.st_ctime_ns, nlink=value.st_nlink)
    return fields


def reference_program():
    """Exact successor of the installed C reference, not a caller's expected filter."""
    deny = 0x00050001
    rows = [(0x20, 0, 0, 4), (0x15, 1, 0, 0xc00000b7), (6, 0, 0, 0x80000000),
            (0x20, 0, 0, 0)]
    for nr, result in ((221, deny), (281, deny), (435, 0x00050026),
                       (117, deny), (268, deny)):
        rows.extend(((0x15, 0, 1, nr), (6, 0, 0, result)))
    # Exact native constructor branch: user namespaces retain ENOSPC, every
    # other unshare call retains EPERM. Observed bytes still come from the
    # producer's immutable syscall input, never from this expected projection.
    rows.extend(((0x15, 0, 4, 97), (0x20, 0, 0, 16),
                 (0x45, 1, 0, 0x10000000), (6, 0, 0, deny),
                 (6, 0, 0, 0x0005001c)))
    rows.extend(((0x15, 1, 0, 220), (6, 0, 0, 0x7fff0000),
                 (0x20, 0, 0, 16), (0x54, 0, 0, 0x109ff),
                 (0x15, 1, 0, 0x10900), (6, 0, 0, deny),
                 (6, 0, 0, 0x7fff0000)))
    return base64.b64encode(b''.join(struct.pack('<HBBI', *row) for row in rows)).decode('ascii')


class ProtectedReportProvider:
    def __init__(self, spec, plan, audit_before, observer=None):
        self.spec, self.plan, self.observer = spec, plan, observer
        self.handles = []
        self.source_handles = []
        self.directory_handles = []
        self.role_handles = {}
        self.channel_handles = {}
        self.lock = threading.RLock()
        self.lease_stop = threading.Event()
        self.lease_thread = None
        self.report_channel = None
        self.lease_ready = threading.Event()
        self.lease_tid = None
        self.signal_mask = None
        self.signal_number = signal.SIGRTMIN + 3
        self.record = {'schema': SCHEMA, 'expected': {
            'invocation': copy.deepcopy(spec.protected_invocation),
            'sourceRoster': copy.deepcopy(audit_before['files']),
            'executedSourceRoster': copy.deepcopy(plan['nativeSourceRoster']),
            'filterProgramB64': reference_program(), 'reportDirectory': None},
            'observed': {}, 'report': {'reads': [], 'sealed': {}}, 'roles': [],
            'operations': [], 'sourceLeases': [], 'sourceDirectories': [],
            'stdlibOriginalReads': [], 'sourceLeaseBreaks': [],
            'lifetime': {'waits': [], 'channelReads': [], 'channelCloses': [],
            'shutdowns': [], 'closes': [], 'pendingOperations': [], 'failures': [],
            'deathPolls': []}}
        self.closed = False

    def _additional_source_files(self):
        return ()

    def _report_maximum(self, observed_size):
        # The ordinary evaluation-report domain never changes. A separate
        # internal readonly syntax provider captures data, not admitted reports.
        return MAX_REPORT_BYTES

    def _failure(self, stage, error):
        self.record['lifetime']['failures'].append(
            {'stage': stage, 'exception': exception_observation(error)})

    def _own(self, fd):
        self.handles.append(fd)
        return fd

    def _operation(self, name, fd, procedure, *, opened=False):
        row = {'operation': name, 'fd': fd, 'return': None, 'errno': 0}
        self.record['operations'].append(row)
        try:
            value = procedure()
            row['return'] = value if type(value) is int else 0
            if opened:
                row['fd'] = value
            return value
        except BaseException as error:
            row['return'] = -1
            row['errno'] = getattr(error, 'errno', None)
            row['exception'] = exception_observation(error)
            raise

    def _stat(self, fd, component=None, *, complete=True):
        row = {'operation': 'fstat' if component is None else 'statEdge',
               'api': 'os.fstat' if component is None else 'os.stat',
               'fd': fd, 'component': component, 'return': None,
               'errno': 0, 'apiReturn': None}
        self.record['operations'].append(row)
        try:
            value = (os.fstat(fd) if component is None else
                     os.stat(component, dir_fd=fd, follow_symlinks=False))
            result = object_stat(value, complete=complete)
            row.update({'return': 0, 'apiReturn': result})
            return result
        except BaseException as error:
            row.update({'return': -1, 'errno': getattr(error, 'errno', None),
                        'exception': exception_observation(error)})
            raise

    def _directory(self, path, *, operation=None):
        """Keep each ancestor until final pathname recheck and cleanup."""
        path = Path(path)
        if not path.is_absolute() or '..' in path.parts:
            raise ValueError('protected source path is not absolute')
        parent = None
        components = ('/', *path.parts[1:])
        for index, name in enumerate(components):
            opener = lambda: os.open(name, _DIR, dir_fd=parent)
            fd = self._own(self._operation(operation, None, opener, opened=True)
                           if operation is not None and index == len(components) - 1
                           else opener())
            row = {'path': str(path), 'component': name, 'fd': fd,
                   'parentFd': parent, 'openReturn': fd, 'openErrno': 0,
                   'before': self._stat(fd, complete=False),
                   'after': None, 'edgeAfter': None}
            self.directory_handles.append((fd, parent, name, row))
            self.record['sourceDirectories'].append(row)
            parent = fd
        return parent

    def _reads(self, fd, rows, maximum):
        content = bytearray()
        while True:
            row = {'fd': fd, 'offset': len(content), 'return': None,
                   'errno': 0, 'bytes': optional_bytes(None)}
            rows.append(row)
            try:
                chunk = os.read(fd, min(65536, maximum + 1 - len(content)))
                row.update({'return': len(chunk), 'bytes': optional_bytes(chunk)})
            except BaseException as error:
                row.update({'return': -1, 'errno': getattr(error, 'errno', None),
                            'exception': exception_observation(error)})
                raise
            content.extend(chunk)
            if len(content) > maximum:
                raise ValueError('protected acquisition exceeds original byte domain')
            if not chunk:
                return bytes(content)

    def _watch_leases(self):
        self.lease_tid = threading.get_native_id()
        self.lease_ready.set()
        try:
            while True:
                event = signal.sigtimedwait({self.signal_number},
                                           0 if self.lease_stop.is_set() else 0.1)
                if event is not None:
                    with self.lock:
                        self.record['sourceLeaseBreaks'].append({
                            'signal': event.si_signo, 'code': event.si_code,
                            'pid': event.si_pid, 'uid': event.si_uid,
                            'status': event.si_status, 'band': event.si_band})
                elif self.lease_stop.is_set():
                    break
        except BaseException as error:
            self._failure('source-lease-monitor', error)

    def __enter__(self):
        try:
            self.signal_mask = signal.pthread_sigmask(signal.SIG_BLOCK, {self.signal_number})
            self.lease_thread = threading.Thread(target=self._watch_leases,
                                                 name='worldline-source-lease-breaks')
            self.lease_thread.start()
            self.lease_ready.wait()
            directory = self._directory(self.spec.report_directory, operation='openReportDirectory')
            report = self.record['report']
            report['directoryFd'] = directory
            self.record['expected']['reportDirectory'] = self._stat(directory, complete=False)
            self._operation('acquireLease', directory,
                            lambda: fcntl.flock(directory, fcntl.LOCK_EX | fcntl.LOCK_NB))
            bindings = {row['binding']['path']: row['binding']
                        for row in self.plan['nativeSourceRoster']}
            sources = [(str(Path(self.plan['verifier']) / row['path']), row['path'],
                        copy.deepcopy(bindings.get('/run/worldline-verifiers/' + row['path'])))
                       for row in self.record['expected']['sourceRoster']]
            for key in ('helper', 'startupPolicy', 'namespacePolicy', 'caseCopier',
                        'nativeGuard', 'loaderPolicy', 'loaderHelper'):
                logical = {'nativeGuard': '/run/worldline-examiner-guard.so',
                           'loaderPolicy': '/run/worldline-loader-policy.json',
                           'loaderHelper': '/run/worldline-examiner-loader.py'}.get(key)
                sources.append((self.plan[key], None, copy.deepcopy(bindings.get(logical))))
            stage = Path(self.plan['runtime']) / 'protected-stdlib'
            stage.mkdir(mode=0o700)
            self.plan['protectedSourceMounts'] = []
            from .private_evaluator import _read_examiner_source
            for index, row in enumerate(self.plan['nativeSourceRoster']):
                binding = row['binding']
                if row['kind'] == 'source' and binding.get('origin') == 'stdlib':
                    read = {}
                    content = _read_examiner_source(Path(binding['path']), read)
                    if (len(content) != binding['byteCount'] or
                            hashlib.sha256(content).hexdigest() != binding['sha256']):
                        raise ValueError('protected stdlib copy differs from original source binding')
                    target = stage / str(index)
                    write_fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                                       os.O_NOFOLLOW | os.O_CLOEXEC, 0o444)
                    try:
                        offset = 0
                        while offset < len(content):
                            count = os.write(write_fd, content[offset:])
                            if count <= 0:
                                raise OSError(errno.EIO, 'incomplete protected stdlib copy')
                            offset += count
                        os.fsync(write_fd)
                    finally:
                        os.close(write_fd)
                    self.plan['protectedSourceMounts'].append({
                        'source': str(target), 'target': binding['path'],
                        'binding': copy.deepcopy(binding)})
                    self.record['stdlibOriginalReads'].append({
                        'binding': copy.deepcopy(binding), 'read': read})
                    sources.append((str(target), None, copy.deepcopy(binding)))
            sources.extend(self._additional_source_files())
            for path, member, binding in sources:
                parent = self._directory(Path(path).parent)
                fd = self._own(self._operation('openSource', None,
                    lambda: os.open(Path(path).name, _FILE, dir_fd=parent), opened=True))
                row = {'path': path, 'member': member, 'binding': binding, 'fd': fd,
                       'parentFd': parent, 'openReturn': fd, 'openErrno': 0,
                       'before': self._stat(fd), 'after': None,
                       'edgeAfter': None, 'reads': [], 'bytes': None,
                       'acquireReturn': None, 'acquireErrno': 0,
                       'getReturn': None, 'getErrno': 0,
                       'releaseReturn': None, 'releaseErrno': 0}
                self.record['sourceLeases'].append(row)
                self.source_handles.append((fd, parent, Path(path).name, row))
                # Target the blocked monitor thread, never an existing daemon
                # thread whose signal mask is outside this provider's ownership.
                fcntl.fcntl(fd, getattr(fcntl, 'F_SETOWN_EX', 15),
                            struct.pack('ii', 0, self.lease_tid))
                fcntl.fcntl(fd, fcntl.F_SETSIG, self.signal_number)
                try:
                    row['acquireReturn'] = fcntl.fcntl(fd, fcntl.F_SETLEASE, fcntl.F_RDLCK)
                except OSError as error:
                    row['acquireReturn'], row['acquireErrno'] = -1, error.errno
                    raise
                row['bytes'] = optional_bytes(self._reads(fd, row['reads'], 268435456))
            expectation = Path(self.plan['runtime']) / 'protected-expectation.json'
            raw = json.dumps(self.record['expected'], sort_keys=True,
                             separators=(',', ':'), allow_nan=False).encode('utf-8')
            fd = self._own(os.open(expectation, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                                   os.O_NOFOLLOW | os.O_CLOEXEC, 0o400))
            offset = 0
            while offset < len(raw):
                written = os.write(fd, raw[offset:])
                if written <= 0:
                    raise OSError(errno.EIO, 'incomplete protected expectation write')
                offset += written
            os.fsync(fd)
            self.expectation = expectation
            from .protected_report_channel import ProtectedReportChannel
            self.report_channel = ProtectedReportChannel(self)
            self.report_channel.start()
            return self
        except BaseException as primary:
            self._failure('provider-start', primary)
            primary.protected_provider_capture = self.record
            self.close(primary)
            raise

    def role_started(self, record, pidfd, namespaces):
        with self.lock:
            row = copy.deepcopy(record)
            row['startup'] = copy.deepcopy(record)
            row['pidfd'] = self._own(self._operation('duplicateRolePidfd', None,
                                                    lambda: os.dup(pidfd), opened=True))
            row['pidfdSource'] = pidfd
            row['pidfdSourceObject'] = self._stat(pidfd)
            row['pidfdObject'] = self._stat(row['pidfd'])
            info_fd = self._own(self._operation('openRolePidfdInfo', None,
                lambda: os.open('/proc/self/fdinfo/' + str(row['pidfd']), _FILE), opened=True))
            info = {'fd': info_fd, 'subjectFd': row['pidfd'], 'reads': []}
            row['pidfdInfo'] = info
            info['bytes'] = optional_bytes(self._reads(info_fd, info['reads'], 65536))
            row['namespaceFds'] = []
            for name, borrowed in namespaces.items():
                fd = self._own(self._operation('duplicateRoleNamespace', None,
                                               lambda: os.dup(borrowed), opened=True))
                row['namespaceFds'].append({'name': name, 'fd': fd,
                    'before': self._stat(fd), 'after': None,
                    'closeReturn': None, 'closeErrno': 0})
            self.role_handles[row['recordId']] = row
            self.record['roles'].append(row)

    def role_waits(self, rows):
        with self.lock:
            for row in rows:
                role = self.role_handles.get(row.get('kernelObservationId'))
                if role is None:
                    self.record['lifetime']['pendingOperations'].append(copy.deepcopy(row))
                    continue
                wait = copy.deepcopy(row)
                wait['originalBorrow'] = copy.deepcopy(row)
                wait['originalBorrow'].pop('recordId', None)
                wait['originalBorrow'].pop('kernelRole', None)
                wait['pidfd'] = role['pidfd']
                attempts = [item for item in wait.get('waitAttempts', [])
                            if item.get('returned') is True and item.get('returnedPid') == wait.get('pid')
                            and item.get('rawStatus') == wait.get('rawWaitStatus')]
                wait['return'] = (attempts[-1]['returnedPid'] if attempts else None)
                wait['errno'] = (0 if attempts and attempts[-1].get('errno') in (None, 0) else None)
                self.record['lifetime']['waits'].append(wait)
                if role.get('roleClaim') == 'examiner':
                    self.record['operations'].append({'operation': 'waitWriter',
                        'fd': role['pidfd'], 'return': wait.get('return'),
                        'errno': wait.get('errno')})

    def lifecycle_channel(self, event):
        with self.lock:
            name = event['operation']
            identity = event['channelId']
            if name == 'acquire':
                original = event['fd']
                held = self._own(self._operation('duplicateChannel', None,
                                                 lambda: os.dup(original), opened=True))
                self.record['operations'][-1].update(originalFd=original, channelId=identity)
                self.channel_handles[identity] = held
                return
            key = {'read': 'channelReads', 'shutdown': 'shutdowns',
                   'close': 'channelCloses'}[name]
            row = copy.deepcopy(event)
            row['originalFd'] = row['fd']
            row['fd'] = self.channel_handles[identity]
            if row.get('returned') is True:
                row['errno'] = 0
                if name in ('close', 'shutdown') and row.get('return') is None:
                    row['apiReturn'] = None
                    row['return'] = 0
            self.record['lifetime'][key].append(row)

    def collect(self, result, role_observer):
        """Called only after original executor wait/observer finish, before return."""
        try:
            self.report_channel.finish()
            fd = self._own(os.open(self.expectation, _FILE))
            observed = json.loads(self._reads(fd, [], 268435456))
            # This independent roster is assembled from the examiner's actual
            # pre-workload read receipts, not copied from planned source bindings.
            observed['executedSourceRoster'] = []
            observed['sourceRoster'] = copy.deepcopy(result['examinerAudit']['after']['files'])
            observed['reportDirectory'] = self._stat(self.record['report']['directoryFd'], complete=False)
            self.record['observed'] = observed
            for row in self.record['roles']:
                poll = select.poll()
                poll.register(row['pidfd'], select.POLLIN)
                events = poll.poll(0)
                self.record['lifetime']['deathPolls'].append({
                    'pidfd': row['pidfd'], 'return': len(events), 'errno': 0,
                    'events': [{'fd': fd, 'revents': flags} for fd, flags in events]})
                if not events:
                    raise OSError(errno.EBUSY, 'role kernel peer still alive after executor wait')
            for record in role_observer.records:
                request = record.get('request') or {}
                if request.get('operation') == 'native-preparation-read':
                    observed['executedSourceRoster'].append({
                        'kind': request.get('kind'), 'logicalPath': request.get('selector'),
                        'bytes': copy.deepcopy((record.get('helperRead') or {}).get('bytes'))})
                if request.get('operation') == 'native-preparation-terminal':
                    policy = (request.get('nativeStatus') or {}).get('syscallPolicy') or {}
                    observed['filterProgramB64'] = policy.get('programB64')
                    self.record['filterInstallation'] = copy.deepcopy(policy)
                    examiner = role_observer.native_startup
                    role = self.role_handles.get(examiner['recordId'])
                    if role is not None:
                        self.record['operations'].append({'operation': 'installFilter',
                            'fd': role['pidfd'], 'return': policy.get('seccompResult'),
                            'errno': policy.get('seccompErrno')})
            report = self.record['report']
            transfer = self.record['reportTransfer']
            report_fd = transfer['fd']
            if report_fd is None:
                raise OSError(errno.ENODATA, 'no native original report descriptor was acquired')
            self.record['operations'].append({'operation': 'openReport', 'fd': report_fd,
                'nativeFd': transfer.get('nativeOpenReturn'), 'return': transfer.get('nativeOpenReturn'),
                'errno': transfer.get('nativeOpenErrno'), 'source': 'native-original-report-open'})
            report['fd'] = report_fd
            report['before'] = self._stat(report_fd)
            if not stat.S_ISREG(report['before']['mode']) or report['before']['nlink'] != 1:
                raise ValueError('original report is not singly linked regular file')
            lease = {'path': str(self.spec.report_directory / 'report'), 'member': None,
                     'binding': None, 'fd': report_fd, 'parentFd': report['directoryFd'],
                     'before': copy.deepcopy(report['before']),
                     'after': None, 'edgeAfter': None, 'reads': report['reads'], 'bytes': None,
                     'acquireReturn': None, 'acquireErrno': 0, 'getReturn': None, 'getErrno': 0,
                     'releaseReturn': None, 'releaseErrno': 0}
            report['writerLease'] = lease
            self.source_handles.append((report_fd, report['directoryFd'], 'report', lease))
            fcntl.fcntl(report_fd, getattr(fcntl, 'F_SETOWN_EX', 15),
                        struct.pack('ii', 0, self.lease_tid))
            fcntl.fcntl(report_fd, fcntl.F_SETSIG, self.signal_number)
            try:
                lease['acquireReturn'] = self._operation('acquireWriterLease', report_fd,
                    lambda: fcntl.fcntl(report_fd, fcntl.F_SETLEASE, fcntl.F_RDLCK))
            except OSError as error:
                lease['acquireReturn'], lease['acquireErrno'] = -1, error.errno
                raise
            maximum = self._report_maximum(report['before']['size'])
            payload = self._reads(report_fd, report['reads'], maximum)
            lease['bytes'] = optional_bytes(payload)
            report['after'] = self._stat(report_fd)
            report['edgeAfter'] = self._stat(report['directoryFd'], 'report')
            sealed = report['sealed']
            memfd = self._own(os.memfd_create('worldline-protected-report',
                             os.MFD_CLOEXEC | os.MFD_ALLOW_SEALING))
            sealed['fd'] = memfd
            offset = 0
            while offset < len(payload):
                count = os.write(memfd, payload[offset:])
                if count <= 0:
                    raise OSError(errno.EIO, 'incomplete protected memfd write')
                offset += count
            try:
                sealed['addSealReturn'] = self._operation('sealReport', memfd,
                    lambda: fcntl.fcntl(memfd, fcntl.F_ADD_SEALS, _SEALS))
                sealed['addSealErrno'] = 0
            except OSError as error:
                sealed['addSealReturn'], sealed['addSealErrno'] = -1, error.errno
                raise
            try:
                sealed['sealGetReturn'] = fcntl.fcntl(memfd, fcntl.F_GET_SEALS)
                sealed['sealErrno'] = 0
            except OSError as error:
                sealed['sealGetReturn'], sealed['sealErrno'] = -1, error.errno
                raise
            sealed['before'] = self._stat(memfd)
            os.lseek(memfd, 0, os.SEEK_SET)
            sealed['reads'] = []
            sealed['bytes'] = optional_bytes(self._reads(memfd, sealed['reads'], maximum))
            sealed['after'] = self._stat(memfd)
        except BaseException as error:
            self._failure('provider-collect', error)
            # Original caller report collection still runs and retains its original
            # error code/precedence. Native sees every protected acquisition failure.
        return self.record

    def close(self, primary=None):
        if self.closed:
            return
        self.closed = True
        failure = None
        if self.report_channel is not None:
            self.report_channel.close()
        for fd, parent, name, row in self.source_handles:
            for stage, procedure, value_key, errno_key in (
                ('source-lease-fstat', lambda: self._stat(fd), 'after', None),
                ('source-lease-edge', lambda: self._stat(parent, name), 'edgeAfter', None),
                ('source-lease-query', lambda: fcntl.fcntl(fd, fcntl.F_GETLEASE), 'getReturn', 'getErrno'),
                ('source-lease-release', lambda: fcntl.fcntl(fd, fcntl.F_SETLEASE,
                    fcntl.F_UNLCK), 'releaseReturn', 'releaseErrno')):
                try:
                    row[value_key] = procedure()
                except BaseException as error:
                    self._failure(stage, error)
                    if errno_key is not None:
                        row[value_key], row[errno_key] = -1, getattr(error, 'errno', None)
                    failure = failure or error
        for fd, parent, name, row in self.directory_handles:
            try:
                row['after'] = self._stat(fd, complete=False)
                row['edgeAfter'] = (None if parent is None else
                                   self._stat(parent, name, complete=False))
            except BaseException as error:
                self._failure('source-directory-recheck', error)
                failure = failure or error
        self.lease_stop.set()
        for role in self.record['roles']:
            for namespace in role['namespaceFds']:
                try:
                    namespace['after'] = self._stat(namespace['fd'])
                except BaseException as error:
                    self._failure('role-namespace-fstat', error)
                    failure = failure or error
        if self.lease_thread is not None:
            self.lease_thread.join()
        for fd in reversed(self.handles):
            row = {'fd': fd, 'return': None, 'errno': 0}
            self.record['lifetime']['closes'].append(row)
            try:
                os.close(fd)
                row['return'] = 0
            except BaseException as error:
                row.update({'return': -1, 'errno': getattr(error, 'errno', None)})
                self._failure('provider-close', error)
                failure = failure or error
            for role in self.record['roles']:
                for namespace in role['namespaceFds']:
                    if namespace['fd'] == fd:
                        namespace['closeReturn'] = row['return']
                        namespace['closeErrno'] = row['errno']
        self.handles.clear()
        if self.signal_mask is not None:
            signal.pthread_sigmask(signal.SIG_SETMASK, self.signal_mask)
        try:
            if self.observer is not None:
                retain_observation(lambda value: self.observer(
                    'private-protected-provider-capture', 0, value), copy.deepcopy(self.record))
        except BaseException as error:
            self._failure('provider-retention', error)
            failure = failure or error
            if primary is not None:
                primary._worldline_retention_failed = True
        if failure is not None:
            if primary is not None:
                primary.add_note('protected provider cleanup also failed: ' + str(failure))
            else:
                raise failure

    def __exit__(self, _kind, primary, _traceback):
        if primary is not None:
            self._failure('executor-or-observer', primary)
            primary.protected_provider_capture = self.record
        self.close(primary)
        return False
