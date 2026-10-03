"""Daemon-owned kernel observations of a private role before its workload starts.

This is a startup observation producer, not a confinement or admission predicate.
The socket's kernel peer identity selects proc objects; message labels never do.
All successful and failed reads remain in the invocation's owned observations.
Namespace lifetime restrictions, input provenance and protected report custody
are separate requirements. No authority fact is upgraded by this module.
"""
from __future__ import annotations

from contextlib import ExitStack
import array
import base64
import errno
import fcntl
import hashlib
import json
import math
import os
from pathlib import PurePosixPath
import re
import select
import socket
import stat
import struct
import subprocess
import sys
import threading
import time
import uuid

from ..raw_observation import (
    exception_observation, optional_bytes, retain_observation, retention_failed,
)
from ..trusted import trusted_script
from . import namespace_lifetime as namespace_policy

# Linux UAPI, asm-generic/socket.h and linux/nsfs.h. The _IO(NSIO,n)
# values use asm-generic/ioctl.h (also used on the supported aarch64 host).
# Availability is checked by the real operation; there is no weaker fallback.
SO_PEERPIDFD = 77
NS_GET_USERNS = 46849
NS_GET_PARENT = 46850
NS_GET_OWNER_UID = 46852
OBSERVER_MOUNT = '/run/worldline-role-observer.sock'
NATIVE_MOUNT = '/run/worldline-examiner-guard.so'
NATIVE_PREPARATION_MOUNT = '/run/worldline-native-preparation.sock'
NATIVE_LIFETIME_MOUNT = '/run/worldline-native-lifetime.sock'
_NAMESPACES = ('user', 'pid', 'mnt', 'net', 'ipc', 'uts')
_CAPABILITIES = ('CapInh', 'CapPrm', 'CapEff', 'CapBnd', 'CapAmb')
_DIR_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW
_READ_FLAGS = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK


class RoleObservationFailure(ValueError):
    code = 'PRIVATE_ROLE_OBSERVATION_FAILED'


class _DescriptorOwner:
    """Attempt every owned close once, retaining the original primary failure."""
    def __init__(self, record):
        self.events = record.setdefault('descriptorCloses', [])
        self.callbacks = []

    def callback(self, procedure, descriptor):
        event = {'descriptor': descriptor, 'closed': False, 'exception': None}
        self.events.append(event)
        self.callbacks.append((procedure, descriptor, event))

    def __enter__(self):
        return self

    def __exit__(self, _kind, primary, _traceback):
        failure = None
        for procedure, descriptor, event in reversed(self.callbacks):
            try:
                procedure(descriptor)
                event['closed'] = True
            except BaseException as error:
                event['exception'] = exception_observation(error)
                if primary is not None:
                    primary.add_note('owned descriptor cleanup also failed: ' + str(error))
                elif failure is None:
                    failure = error
                else:
                    failure.add_note('owned descriptor cleanup also failed: ' + str(error))
        self.callbacks.clear()
        if failure is not None:
            raise failure
        return False


def _require(condition, message):
    if not condition:
        raise RoleObservationFailure(message)


def _fields(payload):
    result = {}
    for line in payload.splitlines():
        key, separator, value = line.partition(b':')
        _require(separator and key and key not in result, 'malformed or duplicate proc field')
        result[key] = value.strip()
    return result


def native_filter_fields(fields):
    """Validate a held-proc sample, never infer the installed filter program."""
    _require(fields.get(b'NoNewPrivs') == b'1' and fields.get(b'Seccomp') == b'2',
             'native examiner kernel privilege or filter mode is absent or different')
    count = fields.get(b'Seccomp_filters')
    _require(type(count) is bytes and re.fullmatch(rb'[1-9][0-9]*', count) is not None,
             'native examiner kernel filter count is absent or malformed')
    return {'scope': 'held-proc-status-sample-only',
            'NoNewPrivs': fields[b'NoNewPrivs'].decode('ascii'),
            'Seccomp': fields[b'Seccomp'].decode('ascii'),
            'Seccomp_filters': count.decode('ascii'),
            'independentKernelProgramObservation': False}


def native_mapping_rows(payload):
    """Parse retained kernel maps; path text is never object identity."""
    result = []
    for line in payload.splitlines():
        fields = line.split(None, 5)
        _require(len(fields) in (5, 6)
                 and re.fullmatch(rb'[0-9a-f]+-[0-9a-f]+', fields[0])
                 and re.fullmatch(rb'[r-][w-][x-][ps]', fields[1])
                 and re.fullmatch(rb'[0-9a-f]+', fields[2])
                 and re.fullmatch(rb'[0-9a-f]+:[0-9a-f]+', fields[3])
                 and fields[4].isdigit(), 'malformed native mapping observation')
        start, end = (int(value, 16) for value in fields[0].split(b'-'))
        major, minor = (int(value, 16) for value in fields[3].split(b':'))
        _require(start < end, 'empty native mapping observation')
        result.append({'start': start, 'end': end, 'permissions': fields[1].decode('ascii'),
                       'offset': int(fields[2], 16), 'deviceMajor': major, 'deviceMinor': minor,
                       'inode': int(fields[4]),
                       'pathBytes': optional_bytes(fields[5] if len(fields) == 6 else None)})
    _require(bool(result), 'empty process mapping observation')
    return result


def process_identity(payload):
    """Parse only kernel stat's PID, PPID and starttime; comm may contain ')'."""
    leader, marker, tail = payload.rpartition(b') ')
    pid, opening, _comm = leader.partition(b' (')
    fields = tail.split()
    _require(marker and opening and pid.isdigit() and len(fields) >= 20,
             'incomplete process stat')
    _require(fields[1].isdigit() and fields[19].isdigit(), 'invalid process stat identity')
    return {'pid': int(pid), 'ppid': int(fields[1]), 'starttime': int(fields[19])}


def identity_map(payload):
    rows = []
    for line in payload.splitlines():
        fields = line.split()
        _require(len(fields) == 3 and all(item.isdigit() for item in fields),
                 'invalid namespace ID map')
        start, outside, count = map(int, fields)
        _require(count > 0, 'empty namespace ID range')
        for old_start, old_outside, old_count in rows:
            _require(start + count <= old_start or old_start + old_count <= start,
                     'overlapping namespace ID map')
            _require(outside + count <= old_outside or old_outside + old_count <= outside,
                     'overlapping outside namespace ID map')
        rows.append((start, outside, count))
    _require(rows, 'missing namespace ID map')
    return tuple(rows)


def mapped_identity(rows, inside):
    values = [outside + inside - start for start, outside, count in rows
              if start <= inside < start + count]
    _require(len(values) == 1, 'required identity is not uniquely mapped')
    return values[0]


def _mount_path(value):
    escapes = {b'040': b' ', b'011': b'\t', b'012': b'\n', b'134': b'\\'}
    def replace(match):
        _require(match[1] in escapes, 'unknown mountinfo path escape')
        return escapes[match[1]]
    # A literal backslash in a kernel path is itself escaped.
    _require(re.search(rb'\\(?![0-7]{3})', value) is None, 'malformed mountinfo path escape')
    return os.fsdecode(re.sub(rb'\\([0-7]{3})', replace, value))


def mount_table(payload):
    rows, seen = [], set()
    for line in payload.splitlines():
        before, marker, after = line.partition(b' - ')
        fields, filesystem = before.split(), after.split()
        _require(marker and len(fields) >= 6 and len(filesystem) == 3,
                 'incomplete mountinfo row')
        _require(fields[0].isdigit() and fields[1].isdigit()
                 and re.fullmatch(rb'[0-9]+:[0-9]+', fields[2]), 'invalid mountinfo identity')
        mount_id = int(fields[0])
        _require(mount_id not in seen, 'duplicate mount ID')
        seen.add(mount_id)
        rows.append({'id': mount_id, 'parent': int(fields[1]),
                     'device': fields[2].decode('ascii'), 'root': _mount_path(fields[3]),
                     'target': _mount_path(fields[4]),
                     'options': fields[5].decode('ascii').split(','),
                     'optional': [item.decode('ascii') for item in fields[6:]],
                     'filesystem': filesystem[0].decode('ascii'),
                     'source': _mount_path(filesystem[1]),
                     'superOptions': filesystem[2].decode('ascii').split(',')})
    _require(rows, 'missing mountinfo')
    return rows


def _object(info):
    return {'device': info.st_dev, 'inode': info.st_ino, 'mode': info.st_mode,
            'uid': info.st_uid, 'gid': info.st_gid, 'size': info.st_size,
            'mtime_ns': info.st_mtime_ns, 'ctime_ns': info.st_ctime_ns}


def _same_object(left, right):
    return (left['device'], left['inode'], stat.S_IFMT(left['mode'])) == (
        right['device'], right['inode'], stat.S_IFMT(right['mode']))


def _mount_root_statx(descriptor, observed):
    """Query the received object, with the full Linux UAPI statx buffer.

    Mount-root support is an attribute-mask bit, not a requested field mask.
    Classic STATX_MNT_ID is used for the mountinfo join, never MNT_ID_UNIQUE.
    """
    import ctypes
    class Timestamp(ctypes.Structure):
        _fields_ = [('sec', ctypes.c_int64), ('nsec', ctypes.c_uint32), ('reserved', ctypes.c_int32)]
    class Statx(ctypes.Structure):
        _fields_ = [
            ('mask', ctypes.c_uint32), ('blksize', ctypes.c_uint32),
            ('attributes', ctypes.c_uint64), ('nlink', ctypes.c_uint32),
            ('uid', ctypes.c_uint32), ('gid', ctypes.c_uint32),
            ('mode', ctypes.c_uint16), ('spare0', ctypes.c_uint16),
            ('ino', ctypes.c_uint64), ('size', ctypes.c_uint64), ('blocks', ctypes.c_uint64),
            ('attributes_mask', ctypes.c_uint64), ('atime', Timestamp), ('btime', Timestamp),
            ('ctime', Timestamp), ('mtime', Timestamp), ('rdev_major', ctypes.c_uint32),
            ('rdev_minor', ctypes.c_uint32), ('dev_major', ctypes.c_uint32), ('dev_minor', ctypes.c_uint32),
            ('mnt_id', ctypes.c_uint64), ('dio_mem_align', ctypes.c_uint32),
            ('dio_offset_align', ctypes.c_uint32), ('subvol', ctypes.c_uint64),
            ('atomic_write_unit_min', ctypes.c_uint32), ('atomic_write_unit_max', ctypes.c_uint32),
            ('atomic_write_segments_max', ctypes.c_uint32), ('dio_read_offset_align', ctypes.c_uint32),
            ('atomic_write_unit_max_opt', ctypes.c_uint32), ('spare2', ctypes.c_uint32),
            ('spare3', ctypes.c_uint64 * 8),
        ]
    _require(ctypes.sizeof(Statx) == 0x100 and Statx.nlink.offset == 0x10
             and Statx.ino.offset == 0x20 and Statx.atime.offset == 0x40
             and Statx.rdev_major.offset == 0x80 and Statx.mnt_id.offset == 0x90
             and Statx.subvol.offset == 0xa0 and Statx.atomic_write_segments_max.offset == 0xb0
             and Statx.spare3.offset == 0xc0, 'statx UAPI layout is unsupported')
    result = Statx()
    function = ctypes.CDLL(None, use_errno=True).statx
    function.argtypes = (ctypes.c_int, ctypes.c_char_p, ctypes.c_int,
                        ctypes.c_uint, ctypes.POINTER(Statx))
    function.restype = ctypes.c_int
    ctypes.set_errno(0)
    returned = function(descriptor, b'', 0x1000 | 0x800, 0x000007ff | 0x00001000,
                        ctypes.byref(result))
    actual_errno = ctypes.get_errno()
    observed.update({'return': returned, 'errno': actual_errno,
                     'bytes': optional_bytes(bytes(result)), 'mask': result.mask,
                     'attributes': result.attributes, 'attributesMask': result.attributes_mask,
                     'mountId': result.mnt_id, 'inode': result.ino, 'mode': result.mode,
                     'deviceMajor': result.dev_major, 'deviceMinor': result.dev_minor})
    if returned != 0:
        raise OSError(actual_errno, os.strerror(actual_errno))
    required = 0x00001000 | 0x00000100 | 0x00000001 | 0x00000002
    _require(result.mask & required == required and result.attributes_mask & 0x00002000
             and result.attributes & 0x00002000, 'received object is not an observed mount root')
    return result.mnt_id


class _Capture:
    def __init__(self, record, maximum, deadline, cancelled):
        self.record, self.maximum = record, maximum
        self.deadline, self.cancelled = deadline, cancelled
        self.used = 0

    def check(self):
        _require(not self.cancelled.is_set(), 'kernel observation cancelled')
        _require(time.monotonic() < self.deadline, 'kernel observation deadline reached')

    def read(self, parent, name, subject):
        item = {'subject': subject, 'name': name, 'started_ns': time.monotonic_ns(),
                'descriptor': None, 'returned': False, 'eof': False, 'exception': None}
        self.record['reads'].append(item)
        content, descriptor = bytearray(), None
        try:
            self.check()
            descriptor = os.open(name, _READ_FLAGS, dir_fd=parent)
            item['descriptor'] = _object(os.fstat(descriptor))
            while True:
                self.check()
                chunk = os.read(descriptor, min(65536, self.maximum - self.used + 1))
                content.extend(chunk)
                self.used += len(chunk)
                _require(self.used <= self.maximum, 'kernel observation exceeds capture limit')
                if not chunk:
                    item['eof'] = True
                    break
            item['returned'] = True
            return bytes(content)
        except BaseException as error:
            item['exception'] = exception_observation(error)
            item['errno'] = getattr(error, 'errno', None)
            raise
        finally:
            item['bytes'] = optional_bytes(content)
            item['finished_ns'] = time.monotonic_ns()
            if descriptor is not None:
                os.close(descriptor)

    def namespace(self, process_fd, name, stack, subject):
        item = {'subject': subject, 'name': name, 'returned': False, 'exception': None}
        self.record['namespaces'].append(item)
        try:
            self.check()
            descriptor = os.open('ns/' + name, os.O_RDONLY | os.O_CLOEXEC, dir_fd=process_fd)
            stack.callback(os.close, descriptor)
            item['object'] = _object(os.fstat(descriptor))
            if name == 'user':
                owner = bytearray(struct.calcsize('=I'))
                fcntl.ioctl(descriptor, NS_GET_OWNER_UID, owner, True)
                item['ownerUid'] = struct.unpack('=I', owner)[0]
                related = fcntl.ioctl(descriptor, NS_GET_PARENT)
                relation = 'parent'
            else:
                related = fcntl.ioctl(descriptor, NS_GET_USERNS)
                relation = 'owner'
            try:
                item[relation] = _object(os.fstat(related))
            finally:
                os.close(related)
            item['returned'] = True
            return item
        except BaseException as error:
            item['exception'] = exception_observation(error)
            item['errno'] = getattr(error, 'errno', None)
            raise


class _Subject:
    def __init__(self, pid, pidfd, capture, stack):
        self.pid, self.pidfd, self.capture = pid, pidfd, capture
        stack.callback(os.close, pidfd)
        os.set_inheritable(pidfd, False)
        self.proc = os.open('/proc/' + str(pid), _DIR_FLAGS)
        stack.callback(os.close, self.proc)
        self.identity = None
        self.namespaces = {}
        self.live()
        self.identity = process_identity(capture.read(self.proc, 'stat', pid))
        _require(self.identity['pid'] == pid, 'proc stat is from a different subject')
        self.status = _fields(capture.read(self.proc, 'status', pid))
        _require(self.status.get(b'Pid') == str(pid).encode()
                 and self.status.get(b'Tgid') == str(pid).encode(), 'proc PID view differs from receiver')
        self.uid_map = identity_map(capture.read(self.proc, 'uid_map', pid))
        self.gid_map = identity_map(capture.read(self.proc, 'gid_map', pid))
        self.cgroup = capture.read(self.proc, 'cgroup', pid)
        self.cmdline = capture.read(self.proc, 'cmdline', pid)
        self.mounts = mount_table(capture.read(self.proc, 'mountinfo', pid))
        for name in _NAMESPACES:
            self.namespaces[name] = capture.namespace(self.proc, name, stack, pid)
        self.recheck()

    def live(self):
        self.capture.check()
        ready = bool(select.select([self.pidfd], [], [], 0)[0])
        self.capture.record.setdefault('liveness', []).append(
            {'pid': self.pid, 'observed_ns': time.monotonic_ns(), 'pidfdReady': ready})
        _require(not ready, 'observed process has exited')
        info = _fields(self.capture.read(None, '/proc/self/fdinfo/' + str(self.pidfd), 'receiver-pidfd'))
        _require(info.get(b'Pid') == str(self.pid).encode(), 'pidfd subject is missing or changed')
        ns_pids = info.get(b'NSpid', b'').split()
        _require(ns_pids and ns_pids[0] == str(self.pid).encode(), 'pidfd PID namespace view is missing')

    def recheck(self):
        self.live()
        actual = process_identity(self.capture.read(self.proc, 'stat', self.pid))
        _require(actual == self.identity, 'process identity or ancestry changed during capture')
        for name, expected in self.namespaces.items():
            descriptor = os.open('ns/' + name, os.O_RDONLY | os.O_CLOEXEC, dir_fd=self.proc)
            try:
                _require(_same_object(_object(os.fstat(descriptor)), expected['object']),
                         'process namespace changed during capture')
            finally:
                os.close(descriptor)


class KernelRoleObserver:
    """One listener, bootstrap anchor and raw record sequence per evaluation."""
    def __init__(self, plan, *, maximum_bytes, maximum_request, handshake_seconds, observer=None):
        self.plan = plan
        self.maximum_bytes, self.maximum_request = maximum_bytes, maximum_request
        self.handshake_seconds, self.observer = handshake_seconds, observer
        self.path = os.path.join(plan['runtime'], 'role-observer.sock')
        self.records, self.roles, self.seen = [], {}, set()
        self.failure = None
        self.stop = threading.Event()
        self.lock = threading.Lock()
        self.records_lock = threading.RLock()
        self.active = None
        self.stack = ExitStack()
        self.thread = None
        self.bootstrap = None
        self.role_user_namespace = None
        self.role_user_namespace_fd = None
        self.role_namespace_number = None
        self.sources = {}
        self.cleanup_deferred = False
        self.cleanup_claimed = False
        self.service_done = False
        self.join_incomplete = False
        self.native_listener = None
        self.native_thread = None
        self.native_active = None
        self.native_service_done = True
        self.native_startup = None
        self.native_started = False
        self.native_completions = {}
        self.native_finished = threading.Event()
        self.lifetime_listener = None
        self.lifetime_thread = None
        self.lifetime_active = None
        self.lifetime_service_done = True
        self.lifetime_started = False
        self.lifetime_budget = None
        self.lifetime_completions = {}

    def _record(self, kind):
        return {'schemaVersion': 1, 'kind': kind, 'runId': self.plan['runId'],
                'recordId': str(uuid.uuid4()), 'producer': 'daemon-kernel-reader',
                'readerPid': os.getpid(), 'readerUid': os.geteuid(), 'readerGid': os.getegid(),
                'readerUserNamespace': _object(os.stat('/proc/self/ns/user')),
                'readerPidNamespace': _object(os.stat('/proc/self/ns/pid')),
                'reads': [], 'namespaces': [], 'exception': None,
                'scope': 'startup-snapshot-only', 'confinementEstablished': False}

    def _retain(self, record):
        # Own the exact pre-ACK value; later cleanup cannot mutate an earlier record.
        owned = json.loads(json.dumps(record))
        with self.records_lock:
            if self.observer is not None:
                retain_observation(lambda value: self.observer(
                    'private-kernel-role-observation', len(self.records), value), owned)
            self.records.append(owned)

    def __enter__(self):
        try:
            self.listener = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
            self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_PASSCRED, 1)
            self.stack.callback(self.listener.close)
            runtime = os.open(self.plan['runtime'], _DIR_FLAGS)
            self.stack.callback(os.close, runtime)
            # Bind relative to an owned descriptor without changing process cwd.
            self.listener.bind('/proc/self/fd/' + str(runtime) + '/role-observer.sock')
            os.chmod('role-observer.sock', 0o666, dir_fd=runtime, follow_symlinks=False)
            self.listener.listen()
            self.listener.settimeout(0.1)
            if 'nativeGuard' in self.plan:
                self.native_listener = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
                self.native_listener.setsockopt(socket.SOL_SOCKET, socket.SO_PASSCRED, 1)
                self.stack.callback(self.native_listener.close)
                self.native_listener.bind('/proc/self/fd/' + str(runtime) + '/native-preparation.sock')
                os.chmod('native-preparation.sock', 0o666, dir_fd=runtime, follow_symlinks=False)
                self.native_listener.listen()
                self.native_listener.settimeout(0.1)
                self.plan['nativePreparationSocket'] = os.path.join(
                    self.plan['runtime'], 'native-preparation.sock')
                self.lifetime_listener = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
                self.lifetime_listener.setsockopt(socket.SOL_SOCKET, socket.SO_PASSCRED, 1)
                self.stack.callback(self.lifetime_listener.close)
                self.lifetime_listener.bind('/proc/self/fd/' + str(runtime) + '/native-lifetime.sock')
                os.chmod('native-lifetime.sock', 0o666, dir_fd=runtime, follow_symlinks=False)
                self.lifetime_listener.listen()
                self.lifetime_listener.settimeout(0.1)
                self.plan['nativeLifetimeSocket'] = os.path.join(self.plan['runtime'], 'native-lifetime.sock')
            sources = [self.plan['helper'], self.plan['startupPolicy'], self.plan['namespacePolicy'], self.path,
                       self.plan['verifier'], self.plan['report']]
            if 'loaderPolicy' in self.plan:
                sources.extend((self.plan['loaderPolicy'], self.plan['loaderHelper']))
            if 'nativeGuard' in self.plan:
                sources.extend((self.plan['nativeGuard'], self.plan['nativePreparationSocket'],
                                self.plan['nativeLifetimeSocket']))
            sources.extend(root['frozen'] for root in self.plan['roots'])
            if self.plan.get('toolchain'):
                sources.append(self.plan['toolchain']['source'])
            for source in sources:
                descriptor = os.open(source, os.O_PATH | os.O_CLOEXEC | os.O_NOFOLLOW)
                self.stack.callback(os.close, descriptor)
                self.sources[source] = (descriptor, _object(os.fstat(descriptor)))
            self.thread = threading.Thread(target=self._serve, name='worldline-kernel-role-observer')
            try:
                self.thread.start()
            except BaseException:
                self.thread = None
                self.service_done = True
                raise
            if self.native_listener is not None:
                self.native_service_done = False
                self.native_thread = threading.Thread(target=self._serve_native,
                    name='worldline-native-preparation-observer')
                try:
                    self.native_thread.start()
                except BaseException:
                    self.native_thread = None
                    self.native_service_done = True
                    raise
            if self.lifetime_listener is not None:
                self.lifetime_service_done = False
                self.lifetime_thread = threading.Thread(target=self._serve_lifetime,
                    name='worldline-native-lifetime-observer')
                try:
                    self.lifetime_thread.start()
                except BaseException:
                    self.lifetime_thread = None
                    self.lifetime_service_done = True
                    raise
            return self
        except BaseException as error:
            try:
                self._close()
            except BaseException as secondary:
                error.add_note('observer startup cleanup also failed: ' + str(secondary))
            raise

    def arm(self, manager):
        record = self._record('bootstrap-anchor')
        record['manager'] = dict(manager)
        try:
            raw_pid, group = manager.get('MainPID'), manager.get('ControlGroup')
            _require(isinstance(raw_pid, str) and raw_pid.isdecimal() and int(raw_pid) > 0,
                     'manager bootstrap PID is missing')
            _require(isinstance(group, str) and group.startswith('/') and '\n' not in group
                     and str(PurePosixPath(group)) == group and '..' not in PurePosixPath(group).parts,
                     'manager bootstrap cgroup is missing or malformed')
            self.group = group
            capture = _Capture(record, self.maximum_bytes,
                               self.plan['bootstrapDeadlineMonotonic'], self.stop)
            subject = _Subject(int(raw_pid), os.pidfd_open(int(raw_pid)), capture, self.stack)
            own_user = _object(os.stat('/proc/self/ns/user'))
            user = subject.namespaces['user']
            _require(_same_object(user['parent'], own_user)
                     and user['ownerUid'] == os.geteuid(), 'bootstrap namespace is not owned by receiver')
            _require(subject.cgroup == ('0::' + group + '\n').encode(), 'bootstrap is outside manager cgroup')
            for mapping, expected in ((subject.uid_map, self.plan['operatorUid']),
                                      (subject.gid_map, self.plan['operatorGid'])):
                values = tuple(mapped_identity(mapping, value) for value in (0, 1, 2))
                _require(values[0] == expected and len(set(values)) == 3 and 0 not in values[1:],
                         'bootstrap subordinate identities are not separated')
            record['identity'] = subject.identity
            record['procDirectory'] = _object(os.fstat(subject.proc))
            subject.recheck()
            self._namespace_anchor(subject, capture, record)
            subject.recheck()
            self._retain(record)
            self.bootstrap = subject
        except BaseException as error:
            record['exception'] = exception_observation(error)
            try:
                self._retain(record)
            except BaseException as secondary:
                error.add_note('bootstrap observation retention also failed: ' + str(secondary))
                error._worldline_retention_failed = True
            raise

    def _namespace_anchor(self, bootstrap, capture, record):
        ready_bytes = capture.read(None, os.path.join(self.plan['runtime'], 'namespace-ready.json'),
                                   'bootstrap-namespace-locator')
        def unique(pairs):
            result = {}
            for key, value in pairs:
                _require(key not in result, 'duplicate namespace locator field')
                result[key] = value
            return result
        ready = json.loads(ready_bytes, object_pairs_hook=unique)
        _require(isinstance(ready, dict)
                 and set(ready) == {'schemaVersion', 'runId', 'descriptor', 'setup'}
                 and type(ready['schemaVersion']) is int and ready['schemaVersion'] == 1
                 and ready['runId'] == self.plan['runId']
                 and type(ready['descriptor']) is int and ready['descriptor'] > 2,
                 'invalid namespace locator')
        descriptor = os.open('fd/' + str(ready['descriptor']), os.O_RDONLY | os.O_CLOEXEC,
                             dir_fd=bootstrap.proc)
        self.stack.callback(os.close, descriptor)
        kind = fcntl.ioctl(descriptor, namespace_policy.NS_GET_NSTYPE)
        _require(kind == namespace_policy.CLONE_NEWUSER, 'role namespace descriptor is another type')
        actual = _object(os.fstat(descriptor))
        parent = fcntl.ioctl(descriptor, NS_GET_PARENT)
        self.stack.callback(os.close, parent)
        owner = bytearray(struct.calcsize('=I'))
        fcntl.ioctl(descriptor, NS_GET_OWNER_UID, owner, True)
        owner_uid = struct.unpack('=I', owner)[0]
        _require(_same_object(_object(os.fstat(parent)), bootstrap.namespaces['user']['object'])
                 and owner_uid == self.plan['operatorUid'], 'role namespace has another parent or owner')
        _require(not _same_object(actual, bootstrap.namespaces['user']['object']),
                 'role namespace retained bootstrap authority')
        record['roleNamespace'] = {'object': actual, 'parent': _object(os.fstat(parent)),
                                   'type': kind, 'ownerUid': owner_uid,
                                   'bootstrapDescriptorNumber': ready['descriptor']}
        self._observe_quota(parent, bootstrap)
        self.role_user_namespace = actual
        self.role_user_namespace_fd = descriptor
        self.role_namespace_number = ready['descriptor']

    def _observe_quota(self, parent_fd, bootstrap):
        record = self._record('namespace-quota-reader')
        record['producer'] = 'daemon-owned-kernel-reader-subprocess'
        deadline = self.plan['bootstrapDeadlineMonotonic']
        capture = _Capture(record, self.maximum_bytes, deadline, self.stop)
        process = None
        channel = peer = None
        try:
            with ExitStack() as owned:
                source = capture.read(None, self.plan['namespacePolicy'], 'quota-reader-source')
                record['sourceSha256'] = hashlib.sha256(source).hexdigest()
                _require(record['sourceSha256'] == self.plan['namespacePolicySha256'],
                         'quota reader policy source differs from staged identity')
                channel, peer = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
                arguments = trusted_script(self.plan['namespacePolicy'], '--quota-reader',
                                           str(peer.fileno()), str(parent_fd), str(deadline),
                                           str(self.maximum_request), str(self.maximum_bytes))
                record['command'] = list(arguments)
                process = subprocess.Popen(arguments, close_fds=True,
                                           pass_fds=(peer.fileno(), parent_fd),
                                           stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)
                peer.close()
                peer = None
                record['pid'] = process.pid
                reply = namespace_policy.receive_packet(channel, deadline, self.maximum_request, record)
                _require(isinstance(reply, dict) and set(reply) == {'state', 'observation'}
                         and reply['state'] == 'observed', 'quota reader did not return its observation')
                subject = _Subject(process.pid, os.pidfd_open(process.pid), capture, owned)
                record['identity'] = subject.identity
                _require(subject.identity['ppid'] == os.getpid(), 'quota reader has another parent')
                _require(_same_object(subject.namespaces['user']['object'],
                                      bootstrap.namespaces['user']['object']),
                         'quota reader did not enter the anchored bootstrap namespace')
                _require(subject.cmdline == b'\0'.join(os.fsencode(item) for item in arguments) + b'\0',
                         'quota reader command differs from trusted invocation')
                receiver_group = capture.read(None, '/proc/self/cgroup', 'quota-reader-parent')
                _require(subject.cgroup == receiver_group, 'quota reader left the daemon cgroup')
                _require(subject.status.get(b'Uid', b'').split() ==
                         [str(self.plan['operatorUid']).encode()] * 4
                         and subject.status.get(b'Gid', b'').split() ==
                         [str(self.plan['operatorGid']).encode()] * 4,
                         'quota reader credentials changed')
                observation = reply['observation']
                _require(isinstance(observation, dict)
                         and observation.get('producer') == 'daemon-owned-namespace-quota-reader'
                         and observation.get('exception') is None, 'quota reader observation failed')
                for key in ('readerNamespace', 'requestedNamespace', 'afterNamespace'):
                    _require(_same_object(observation[key], bootstrap.namespaces['user']['object']),
                             'quota reader reported another namespace context')
                quota_bytes = observation['quotaBytes']
                _require(isinstance(quota_bytes, dict) and set(quota_bytes) == {'encoding', 'payload'}
                         and quota_bytes['encoding'] == 'base64', 'quota read bytes are absent')
                quota = base64.b64decode(quota_bytes['payload'], validate=True)
                _require(quota.strip() == b'0', 'bootstrap namespace quota is not zero')
                reads = observation.get('reads')
                _require(isinstance(reads, list) and reads
                         and all(item.get('returned') is True and item.get('eof') is True
                                 and item.get('exception') is None for item in reads),
                         'quota reader has incomplete kernel reads')
                _require(len([item for item in reads if item.get('path') == namespace_policy._QUOTA
                              and item.get('bytes') == quota_bytes]) == 1,
                         'quota result is not bound to its retained raw read')
                record['observation'] = observation
                subject.recheck()
                self._retain(record)
                namespace_policy.send_packet(channel, {'state': 'retained'}, deadline,
                                             self.maximum_request, record)
                returned = namespace_policy.finish_process(process, record, deadline,
                                                           maximum_output=self.plan['maximumOutputBytes'])
                process = None
                _require(returned == 0, 'quota reader did not complete successfully')
        except BaseException as error:
            record['exception'] = exception_observation(error)
            raise
        finally:
            primary = sys.exception()
            if process is not None:
                try:
                    namespace_policy.finish_process(process, record, deadline, kill=True,
                                                    maximum_output=self.plan['maximumOutputBytes'])
                except BaseException as error:
                    record['cleanupException'] = exception_observation(error)
                    if primary is not None:
                        primary.add_note('quota reader cleanup also failed: ' + str(error))
                    else:
                        raise
            for endpoint in (channel, peer):
                if endpoint is not None:
                    endpoint.close()
            completion = {**record, 'kind': 'namespace-quota-reader-completion'}
            try:
                self._retain(completion)
            except BaseException as error:
                if primary is not None:
                    primary.add_note('quota reader completion retention also failed: ' + str(error))
                    primary._worldline_retention_failed = True
                else:
                    raise

    def _descriptor_inventory(self, subject, role_record):
        """A daemon-owned N2 reader supplies kernel bytes, never workload claims."""
        record = self._record('role-descriptor-reader')
        record['producer'] = 'daemon-owned-kernel-reader-subprocess'
        record['targetIdentity'] = dict(subject.identity)
        role_record['descriptorReader'] = record
        deadline = subject.capture.deadline
        capture = None
        charged = False
        process = channel = peer = None
        try:
            with ExitStack() as owned:
                subject.live()
                capture = _Capture(record, subject.capture.maximum - subject.capture.used,
                                   deadline, self.stop)
                source = capture.read(None, self.plan['namespacePolicy'], 'descriptor-reader-source')
                record['sourceSha256'] = hashlib.sha256(source).hexdigest()
                _require(record['sourceSha256'] == self.plan['namespacePolicySha256'],
                         'descriptor reader source differs from staged policy')
                _require(self.role_user_namespace_fd is not None, 'role namespace is not held')
                channel, peer = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
                helper_budget = capture.maximum - capture.used
                arguments = trusted_script(self.plan['namespacePolicy'], '--descriptor-reader',
                    str(peer.fileno()), str(self.role_user_namespace_fd), str(subject.proc),
                    str(subject.pidfd), str(deadline), str(self.maximum_request), str(helper_budget))
                record['command'] = list(arguments)
                process = subprocess.Popen(arguments, close_fds=True,
                    pass_fds=(peer.fileno(), self.role_user_namespace_fd, subject.proc, subject.pidfd),
                    stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                peer.close()
                peer = None
                record['pid'] = process.pid
                begin = namespace_policy.receive_packet(channel, deadline, self.maximum_request, record)
                _require(type(begin) is dict and set(begin) == {'state', 'observation'}
                         and begin['state'] == 'begin', 'descriptor reader did not begin its inventory')
                first = begin['observation']
                record['beginObservation'] = first
                _require(type(first) is dict and first.get('producer') == 'daemon-owned-descriptor-reader'
                         and first.get('exception') is None and first.get('enumerationReturned') is True,
                         'descriptor reader failed before enumeration')
                inventory = namespace_policy.DescriptorInventory(first.get('entryCount'), helper_budget)
                while True:
                    packet = namespace_policy.receive_packet(channel, deadline, self.maximum_request, record)
                    if type(packet) is dict and packet.get('state') == 'entry':
                        inventory.append(packet)
                        continue
                    _require(type(packet) is dict and set(packet) == {'state', 'observation'}
                             and packet['state'] == 'observed', 'descriptor inventory ended with refusal')
                    observation = packet['observation']
                    record['observation'] = observation
                    _require(type(observation) is dict and observation.get('exception') is None
                             and observation.get('producer') == 'daemon-owned-descriptor-reader'
                             and observation.get('enumerationReturned') is True
                             and observation.get('inventoryComplete') is True,
                             'descriptor reader did not complete its inventory')
                    inventory.finish(observation.get('entryCount'))
                    break
                raw_used = namespace_policy.validate_descriptor_observation(
                    first, observation, inventory, identity=subject.identity,
                    process_object=_object(os.fstat(subject.proc)),
                    pidfd_object=_object(os.fstat(subject.pidfd)), pidfd=subject.pidfd,
                    before_namespace=record['readerUserNamespace'],
                    namespace=self.role_user_namespace, maximum=helper_budget)
                capture.used += raw_used
                reader = _Subject(process.pid, os.pidfd_open(process.pid), capture, owned)
                record['readerIdentity'] = reader.identity
                _require(reader.identity['ppid'] == os.getpid()
                         and _same_object(reader.namespaces['user']['object'], self.role_user_namespace),
                         'descriptor reader process ancestry or namespace differs')
                _require(reader.cmdline == b'\0'.join(os.fsencode(item) for item in arguments) + b'\0',
                         'descriptor reader command differs from owned invocation')
                _require(reader.uid_map == subject.uid_map and reader.gid_map == subject.gid_map,
                         'descriptor reader lost the complete role ID map')
                _require(reader.cgroup == capture.read(None, '/proc/self/cgroup', 'descriptor-reader-parent'),
                         'descriptor reader left the daemon cgroup')
                _require(reader.status.get(b'Uid', b'').split() ==
                         [str(self.plan['operatorUid']).encode()] * 4
                         and reader.status.get(b'Gid', b'').split() ==
                         [str(self.plan['operatorGid']).encode()] * 4,
                         'descriptor reader global credentials changed')
                capabilities = reader.status.get(b'CapEff', b'')
                _require(re.fullmatch(rb'[0-9a-fA-F]+', capabilities)
                         and int(capabilities, 16) & (1 << 2),
                         'descriptor reader lacks observed namespace DAC capability')
                role_record['inheritedDescriptorInventory'] = inventory.entries
                for entry in inventory.entries:
                    link = namespace_policy.decode_raw(entry['linkBytes'])
                    _require(re.fullmatch(rb'(user|pid|mnt|net|ipc|uts|cgroup|time):\[[0-9]+\]', link) is None,
                             'role inherited a namespace descriptor')
                reader.recheck()
                # The nested capture owns the remaining original budget while
                # active. Transfer it once before the outer subject reads again.
                subject.capture.used += capture.used
                charged = True
                subject.recheck()
                record['inventoryComplete'] = True
                self._retain(record)
                namespace_policy.send_packet(channel, {'state': 'retained'}, deadline,
                                             self.maximum_request, record)
                returned = namespace_policy.finish_process(process, record, deadline,
                    maximum_output=self.plan['maximumOutputBytes'])
                process = None
                _require(returned == 0, 'descriptor reader did not exit successfully')
        except BaseException as error:
            record['exception'] = exception_observation(error)
            raise
        finally:
            primary = sys.exception()
            if process is not None:
                try:
                    namespace_policy.finish_process(process, record, deadline, kill=True,
                        maximum_output=self.plan['maximumOutputBytes'])
                except BaseException as error:
                    record['cleanupException'] = exception_observation(error)
                    if primary is not None:
                        primary.add_note('descriptor reader cleanup also failed: ' + str(error))
                    else:
                        raise
            for endpoint in (channel, peer):
                if endpoint is not None:
                    endpoint.close()
            if capture is not None and not charged:
                subject.capture.used += capture.used
            completion = {**record, 'kind': 'role-descriptor-reader-completion'}
            try:
                self._retain(completion)
            except BaseException as error:
                if primary is not None:
                    primary.add_note('descriptor reader completion retention also failed: ' + str(error))
                    primary._worldline_retention_failed = True
                else:
                    raise

    def _ancestry(self, subject, capture, stack):
        result, current, seen, held = [], subject.identity, set(), []
        while current['pid'] != self.bootstrap.pid:
            capture.check()
            _require(current['pid'] not in seen and current['ppid'] > 0,
                     'role ancestry does not reach the bootstrap')
            seen.add(current['pid'])
            result.append(current)
            parent = os.open('/proc/' + str(current['ppid']), _DIR_FLAGS)
            stack.callback(os.close, parent)
            next_identity = process_identity(capture.read(parent, 'stat', current['ppid']))
            _require(next_identity['pid'] == current['ppid'], 'ancestor PID view changed')
            held.append((parent, next_identity))
            current = next_identity
        _require(current == self.bootstrap.identity, 'bootstrap ancestor instance changed')
        result.append(current)
        return result, held

    def _packet(self, connection, capture, owned, peer, *, allow_eof=False):
        packet = {'bytes': None, 'flags': None, 'ancillary': [], 'exception': None}
        capture.record.setdefault('packets', []).append(packet)
        try:
            while True:
                capture.check()
                try:
                    payload, ancillary, flags, _address = connection.recvmsg(
                        self.maximum_request + 1, self.maximum_request, socket.MSG_CMSG_CLOEXEC)
                    break
                except TimeoutError:
                    continue
            packet['bytes'], packet['flags'] = optional_bytes(payload), flags
            descriptors, credentials, malformed = [], [], False
            for level, kind, data in ancillary:
                packet['ancillary'].append({'level': level, 'kind': kind, 'bytes': optional_bytes(data)})
                if level == socket.SOL_SOCKET and kind == socket.SCM_RIGHTS:
                    numbers = array.array('i')
                    complete = len(data) - len(data) % numbers.itemsize
                    numbers.frombytes(data[:complete])
                    for descriptor in numbers:
                        owned.callback(os.close, descriptor)
                        descriptors.append(descriptor)
                    malformed |= complete != len(data)
                elif level == socket.SOL_SOCKET and kind == socket.SCM_CREDENTIALS:
                    if len(data) != struct.calcsize('=iII'):
                        malformed = True
                    else:
                        credentials.append(struct.unpack('=iII', data))
                else:
                    malformed = True
            # Register every delivered FD before any rejection of the packet.
            _require(not malformed and not (flags & ~(socket.MSG_EOR | socket.MSG_CMSG_CLOEXEC))
                     and len(payload) <= self.maximum_request,
                     'malformed, truncated or empty role packet')
            if not payload:
                _require(allow_eof and not descriptors and not ancillary,
                         'unexpected role channel EOF or descriptors at EOF')
                return payload, descriptors
            _require(credentials == [peer], 'packet credentials differ from connected role')
            return payload, descriptors
        except BaseException as error:
            packet['exception'], packet['errno'] = exception_observation(error), getattr(error, 'errno', None)
            raise

    def _mount_handle(self, connection, subject, row, peer, record):
        item = {'mount': row, 'effective': None, 'fdinfoMountId': None,
                'statx': {}, 'fdLinkBytes': None, 'exception': None}
        record.setdefault('mountHandles', []).append(item)
        try:
            request = json.dumps({'operation': 'mount-handle', 'target': row['target']}).encode()
            _require(len(request) <= self.maximum_request, 'mount request exceeds original request cap')
            _require(connection.send(request) == len(request), 'mount handle request was incomplete')
            with ExitStack() as owned:
                payload, descriptors = self._packet(connection, subject.capture, owned, peer)
                _require(payload == b'MOUNT\n' and len(descriptors) == 1,
                         'mount response must contain exactly one handle')
                descriptor = descriptors[0]
                flags = fcntl.fcntl(descriptor, fcntl.F_GETFL)
                item['descriptorFlags'] = flags
                _require(flags & os.O_PATH, 'mount handle is not O_PATH')
                fields = _fields(subject.capture.read(
                    None, '/proc/self/fdinfo/' + str(descriptor), 'receiver-mount-handle'))
                mount_id = fields.get(b'mnt_id', b'')
                _require(mount_id.isdigit(), 'mount handle ID is missing')
                item['fdinfoMountId'] = int(mount_id)
                item['effective'] = _object(os.fstat(descriptor))
                item['fdLinkBytes'] = optional_bytes(os.readlink(os.fsencode('/proc/self/fd/' + str(descriptor))))
                kernel_mount_id = _mount_root_statx(descriptor, item['statx'])
                _require(kernel_mount_id == item['fdinfoMountId'] == row['id'],
                         'handle is not the independently observed mount root')
                _require(item['statx']['inode'] == item['effective']['inode']
                         and item['statx']['mode'] == item['effective']['mode']
                         and item['statx']['deviceMajor'] == os.major(item['effective']['device'])
                         and item['statx']['deviceMinor'] == os.minor(item['effective']['device']),
                         'statx and fstat object identities differ')
            return item
        except BaseException as error:
            item['exception'], item['errno'] = exception_observation(error), getattr(error, 'errno', None)
            raise

    def _mounts(self, subject, role, record, connection, peer):
        plan = self.plan
        expected = [('/run/worldline-evaluator.py', plan['helper'], True),
                    ('/run/trusted.py', plan['startupPolicy'], True),
                    ('/run/namespace_lifetime.py', plan['namespacePolicy'], True),
                    (OBSERVER_MOUNT, self.path, True)]
        forbidden = ['/run/worldline-report', '/run/worldline-broker.sock',
                     '/run/worldline-worker-broker.sock', '/run/worldline-verifiers',
                     '/opt/worldline-gnat', '/run/worldline-loader-policy.json',
                     '/run/worldline-examiner-loader.py', NATIVE_MOUNT, NATIVE_PREPARATION_MOUNT,
                     NATIVE_LIFETIME_MOUNT]
        if role == 'examiner':
            expected.extend((('/run/worldline-verifiers', plan['verifier'], True),
                             ('/run/worldline-report', plan['report'], False),
                             ('/run/worldline-broker.sock', os.path.join(plan['runtime'], 'broker.sock'), False)))
            expected.extend((root['target'], root['frozen'], True) for root in plan['roots'])
            if 'loaderPolicy' in plan:
                expected.extend((('/run/worldline-loader-policy.json', plan['loaderPolicy'], True),
                                 ('/run/worldline-examiner-loader.py', plan['loaderHelper'], True)))
            if 'nativeGuard' in plan:
                expected.extend(((NATIVE_MOUNT, plan['nativeGuard'], True),
                                 (NATIVE_PREPARATION_MOUNT, plan['nativePreparationSocket'], True),
                                 (NATIVE_LIFETIME_MOUNT, plan['nativeLifetimeSocket'], True)))
            if plan.get('toolchain'):
                expected.append(('/opt/worldline-gnat', plan['toolchain']['source'], True))
        elif role == 'worker':
            expected.append(('/run/worldline-worker-broker.sock',
                             os.path.join(plan['runtime'], 'worker-broker.sock'), False))
        # The role opens handles using its unchanged mapped credentials. All
        # facts below are read by the daemon from the received kernel objects.
        # statx proves each handle is the root of the independently listed mount;
        # serialized helper paths or stat dictionaries are never evidence.
        handles = [self._mount_handle(connection, subject, row, peer, record) for row in subject.mounts]
        record['mountObjects'] = []
        for target, source, readonly in expected:
            subject.capture.check()
            item = {'target': target, 'plannedSource': source, 'plannedReadOnly': readonly,
                    'source': None, 'effective': None, 'mount': None}
            record['mountObjects'].append(item)
            held = self.sources.get(source)
            # Broker sockets are created by the existing mapped bootstrap after
            # bootstrap GO. Their object join is recorded at role startup, not
            # mislabeled as a daemon-created or pre-launch-pinned broker.
            source_fd = held[0] if held is not None else os.open(
                source, os.O_PATH | os.O_CLOEXEC | os.O_NOFOLLOW)
            try:
                item['source'] = _object(os.fstat(source_fd))
                item['sourceHeldBeforeLaunch'] = held is not None
                item['sourceBeforeLaunch'] = None if held is None else held[1]
                if held is not None:
                    _require(_same_object(item['source'], held[1]), 'held source object changed')
                    if stat.S_ISREG(item['source']['mode']):
                        _require(item['source'] == held[1], 'held source file metadata changed')
                rows = [handle for handle in handles if handle['mount']['target'] == target]
                _require(len(rows) == 1, 'planned mount is missing or ambiguous')
                item['effective'], item['mount'] = rows[0]['effective'], rows[0]['mount']
                _require(_same_object(item['source'], item['effective']), 'effective mount object differs')
                _require(('ro' in item['mount']['options']) == readonly
                         and ('rw' in item['mount']['options']) != readonly, 'mount access mode differs')
            finally:
                if held is None:
                    os.close(source_fd)
        record['absentPaths'] = []
        required_targets = {row[0] for row in expected}
        for target in forbidden:
            if target in required_targets:
                continue
            item = {'target': target, 'observedErrno': None}
            record['absentPaths'].append(item)
            try:
                os.stat('root' + target, dir_fd=subject.proc, follow_symlinks=False)
            except OSError as error:
                item['observedErrno'] = error.errno
                _require(error.errno == errno.ENOENT, 'absence was not observed')
            else:
                raise RoleObservationFailure('private role exposes an unexpected reserved path')
        _report_fd, report_identity = self.sources[plan['report']]
        aliases = [item['mount']['target'] for item in handles
                   if _same_object(report_identity, item['effective'])]
        record['reportDirectoryMountRootsAtStartup'] = aliases
        _require(aliases == (['/run/worldline-report'] if role == 'examiner' else []),
                 'unexpected report-directory mount root')
        after = mount_table(subject.capture.read(subject.proc, 'mountinfo', subject.pid))
        _require(after == subject.mounts, 'role mount topology changed during object inspection')

    def _native_mapping(self, subject, record):
        source, identity = self.sources[self.plan['nativeGuard']]
        _require(_object(os.fstat(source)) == identity, 'native source object changed before mapping observation')
        rows = native_mapping_rows(subject.capture.read(subject.proc, 'maps', subject.pid))
        selected = [row for row in rows if row['inode'] == identity['inode']
                    and row['deviceMajor'] == os.major(identity['device'])
                    and row['deviceMinor'] == os.minor(identity['device'])]
        record['nativeArtifactMapping'] = {
            'binding': self.plan['nativeGuardBinding'], 'heldSource': identity, 'mappings': selected,
            'scope': 'held object in sampled kernel mappings; no constructor or lifetime acceptance'}
        _require(selected and any('x' in row['permissions'] for row in selected),
                 'native artifact has no observed executable mapping')
        _require(all(not ('w' in row['permissions'] and 'x' in row['permissions']) for row in selected),
                 'native artifact has a writable executable mapping')

    def _acknowledgement(self, role, record):
        response = {'recordId': record['recordId']}
        if role == 'examiner':
            from .private_evaluator import _validate_entry_binding
            binding = _validate_entry_binding(self.plan.get('examinerEntryBinding'),
                                              self.plan['runId'], self.plan['argv'][1])
            record['examinerEntryBinding'] = binding
            response['entrySource'] = binding
            if 'loaderPolicy' in self.plan:
                from .examiner_loader import validate_binding
                loader_binding = validate_binding(self.plan.get('examinerLoaderBinding'),
                                                   self.plan['runId'], maximum_bytes=self.maximum_bytes)
                record['examinerLoaderBinding'] = loader_binding
                response['loaderPolicy'] = loader_binding
            if 'nativeGuard' in self.plan:
                from .private_evaluator import _validate_native_binding
                native_binding = _validate_native_binding(self.plan['nativeGuardBinding'], self.plan['runId'])
                record['examinerNativeBinding'] = native_binding
                response['nativeGuard'] = native_binding
        payload = json.dumps(response).encode()
        _require(len(payload) <= self.maximum_request, 'role acknowledgement exceeds original bound')
        return payload

    def _entry_object_bytes(self, descriptor, name, extent, maximum, capture):
        item = {'name': name, 'announcedBytes': extent, 'before': None, 'after': None,
                'sealsBefore': None, 'sealsAfter': None, 'bytes': None,
                'eof': False, 'returned': False, 'exception': None}
        capture.record.setdefault('transferObjects', []).append(item)
        content = bytearray()
        try:
            capture.check()
            _require(type(extent) is int and 0 <= extent <= maximum,
                     'entry object announced length is outside its capture bound')
            info = os.fstat(descriptor)
            item['before'] = _object(info)
            item['sealsBefore'] = fcntl.fcntl(descriptor, fcntl.F_GET_SEALS)
            required = fcntl.F_SEAL_WRITE | fcntl.F_SEAL_SHRINK | fcntl.F_SEAL_GROW | fcntl.F_SEAL_SEAL
            _require(stat.S_ISREG(info.st_mode) and info.st_size == extent
                     and item['sealsBefore'] & required == required,
                     'entry object type, extent or required seals differ')
            while True:
                capture.check()
                chunk = os.pread(descriptor, min(65536, extent - len(content) + 1), len(content))
                content.extend(chunk)
                _require(len(content) <= extent, 'entry object exceeded announced extent')
                if not chunk:
                    item['eof'] = True
                    break
            item['after'] = _object(os.fstat(descriptor))
            item['sealsAfter'] = fcntl.fcntl(descriptor, fcntl.F_GET_SEALS)
            _require(item['after'] == item['before'] and item['sealsAfter'] == item['sealsBefore']
                     and len(content) == extent, 'entry object changed or ended early')
            item['returned'] = True
            return bytes(content)
        except BaseException as error:
            item['exception'] = exception_observation(error)
            item['errno'] = getattr(error, 'errno', None)
            raise
        finally:
            item['bytes'] = optional_bytes(content)

    @staticmethod
    def _native_json(payload):
        def unique(pairs):
            value = {}
            for key, item in pairs:
                _require(key not in value, 'duplicate native preparation field')
                value[key] = item
            return value
        def invalid(value):
            raise RoleObservationFailure('nonfinite native preparation number: ' + value)
        def finite(value):
            result = float(value)
            _require(math.isfinite(result), 'native preparation number overflows to nonfinite')
            return result
        return json.loads(payload, object_pairs_hook=unique, parse_constant=invalid, parse_float=finite)

    def _native_reply(self, connection, capture, record, value):
        """Retain the full read and exact proposed receipt before sending it."""
        encoded = json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
        _require(len(encoded) <= self.maximum_request, 'native acknowledgement exceeds original bound')
        record['acknowledgementBytes'] = optional_bytes(encoded)
        self._retain(record)
        while True:
            capture.check()
            try:
                _require(connection.send(encoded) == len(encoded), 'native acknowledgement was incomplete')
                break
            except TimeoutError:
                continue
        self._retain({**self._record('native-preparation-acknowledgement'),
                      'startupRecordId': value['startupRecordId'],
                      'retainedRecordId': value['recordId'], 'sent': True,
                      'bytes': optional_bytes(encoded), 'meaning': 'retention only; no confinement authority'})
        return hashlib.sha256(encoded).hexdigest()

    def _native_preparation(self, connection):
        record = self._record('native-preparation-open')
        record['scope'] = 'post-GO-source-preparation-retention-only'
        cleanup = self._record('native-preparation-held-descriptor-cleanup')
        deadline = time.monotonic() + self.plan['timeout']
        capture = _Capture(record, self.maximum_bytes, deadline, self.stop)
        sequence, previous, primary = 0, None, None
        context = None
        try:
            with _DescriptorOwner(cleanup) as held:
                credentials = connection.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED,
                    struct.calcsize('=iII'))
                peer = struct.unpack('=iII', credentials)
                record['peerCredentialsBytes'] = optional_bytes(credentials)
                record['peerCredentials'] = list(peer)
                pidfd = connection.getsockopt(socket.SOL_SOCKET, SO_PEERPIDFD)
                subject = _Subject(peer[0], pidfd, capture, held)
                with _DescriptorOwner(record) as objects:
                    payload, descriptors = self._packet(connection, capture, objects, peer)
                    _require(not descriptors, 'native preparation open cannot pass objects')
                request = self._native_json(payload)
                record['request'] = request
                with self.lock:
                    startup = self.native_startup
                    _require(startup is not None and not self.native_started,
                             'native preparation startup is absent or already consumed')
                    context = {'schemaVersion': 1, 'runId': self.plan['runId'],
                               'startupRecordId': startup['recordId']}
                    expected = {**context, 'operation': 'native-preparation-open',
                                'nativeGuard': self.plan['nativeGuardBinding'],
                                'loaderPolicy': self.plan['examinerLoaderBinding']}
                    _require(type(request) is dict and set(request) == set(expected)
                             and type(request['schemaVersion']) is int and request == expected,
                             'native preparation does not identify this startup and artifacts')
                    _require(peer == startup['peer'] and subject.identity == startup['identity']
                             and subject.cgroup == startup['cgroup'],
                             'native preparation kernel subject differs from examiner startup')
                    _require(all(_same_object(subject.namespaces[name]['object'], identity)
                                 for name, identity in startup['namespaces'].items())
                             and all(subject.status.get(key) == value
                                     for key, value in startup['credentialFields'].items()),
                             'native preparation credentials or namespaces changed')
                    self.native_started = True
                subject.recheck()
                record['startupRecordId'] = startup['recordId']
                record['identity'] = subject.identity
                if 'nativeKernelFilter' in startup:
                    # Exact startup sample is an additional join, never a claim
                    # that a mode/count observation identifies BPF instructions.
                    record['nativeKernelFilter'] = native_filter_fields(subject.status)
                    _require(record['nativeKernelFilter'] == startup['nativeKernelFilter'],
                             'native examiner kernel filter sample changed since startup')
                ready = {**context, 'operation': 'native-preparation-ready',
                         'nativeGuard': self.plan['nativeGuardBinding'],
                         'loaderPolicy': self.plan['examinerLoaderBinding'],
                         'timeoutSeconds': self.plan['timeout'], 'recordId': record['recordId']}
                previous = self._native_reply(connection, capture, record, ready)
                roster = self.plan['nativeSourceRoster']
                # Separate existing tree domains; the actual entry is transferred
                # on the original channel and is accounted here only as declared.
                tree_bytes = {'verifier': self.plan['examinerEntryBinding']['byteCount'], 'stdlib': 0}
                tree_counts = {'verifier': 1, 'stdlib': 0}
                from .private_evaluator import MAX_TREE_ENTRIES
                for row in roster:
                    if row['kind'] == 'source':
                        origin = row['binding']['origin']
                        _require(origin in tree_bytes, 'native source has unknown tree domain')
                        tree_bytes[origin] += row['binding']['byteCount']
                        tree_counts[origin] += 1
                _require(all(size <= self.maximum_bytes for size in tree_bytes.values())
                         and all(count <= MAX_TREE_ENTRIES for count in tree_counts.values()),
                         'native source roster exceeds its original independent tree domain')
                read_failed = False
                while True:
                    row_record = self._record('native-preparation-receive')
                    row_record.update(startupRecordId=startup['recordId'], sequence=sequence,
                                      previousReceiptSha256=previous, scope='helper-read-retention-only')
                    row_capture = _Capture(row_record, self.maximum_bytes, deadline, self.stop)
                    subject.capture = row_capture
                    terminal = False
                    try:
                        with _DescriptorOwner(row_record) as objects:
                            payload, descriptors = self._packet(connection, row_capture, objects, peer)
                            packet = self._native_json(payload)
                            row_record['request'] = packet
                            _require(type(packet) is dict and type(packet.get('schemaVersion')) is int
                                     and type(packet.get('sequence')) is int
                                     and all(packet.get(key) == value for key, value in context.items())
                                     and packet.get('sequence') == sequence
                                     and packet.get('previousReceiptSha256') == previous,
                                     'native sequence or invocation join differs')
                            if packet.get('operation') == 'native-preparation-terminal':
                                terminal = True
                                _require(set(packet) == set(context) | {
                                    'operation', 'sequence', 'previousReceiptSha256', 'exception', 'nativeStatus'}
                                    and not descriptors, 'native terminal fields or descriptors differ')
                                failed = packet['exception'] is not None
                                _require(not failed or type(packet['exception']) is dict,
                                         'native terminal exception is malformed')
                                if not failed:
                                    state = packet['nativeStatus']
                                    _require(sequence == len(roster) and not read_failed
                                             and type(state) is dict and state.get('runId') == self.plan['runId']
                                             and state.get('phase') == 'configured'
                                             and state.get('preinitializationInstalled') is True
                                             and state.get('violated') is False
                                             and state.get('permitActive') is False,
                                             'successful native preparation lacks a complete clean helper report')
                                final, extra = self._packet(connection, row_capture, objects, peer, allow_eof=True)
                                _require(final == b'' and not extra, 'extra native preparation transfer')
                                subject.recheck()
                                row_record.update(kind='native-preparation-terminal', failed=failed,
                                    treeDeclaredBytes=tree_bytes, treeDeclaredCounts=tree_counts,
                                    originalEntryTransferStillRequired=True, trueEof=True)
                                reply = {**context, 'operation': 'native-preparation-complete',
                                         'sequence': sequence, 'previousReceiptSha256': previous,
                                         'failed': failed, 'recordId': row_record['recordId']}
                            else:
                                _require(sequence < len(roster) and not read_failed,
                                         'native preparation has an extra or post-failure source')
                                expected_row = roster[sequence]
                                binding = expected_row['binding']
                                _require(set(packet) == set(context) | {
                                    'operation', 'sequence', 'previousReceiptSha256', 'kind', 'selector',
                                    'transferId', 'metadataBytes', 'sourcePresent', 'sourceBytes'}
                                    and packet['operation'] == 'native-preparation-read'
                                    and packet['kind'] == expected_row['kind']
                                    and packet['selector'] == binding['path']
                                    and type(packet['sourcePresent']) is bool
                                    and type(packet['transferId']) is str
                                    and str(uuid.UUID(packet['transferId'])) == packet['transferId']
                                    and len(descriptors) == 2, 'native read differs from expected ordered roster')
                                subject.recheck()
                                metadata = self._entry_object_bytes(descriptors[0], 'metadata',
                                    packet['metadataBytes'], self.maximum_bytes, row_capture)
                                source = self._entry_object_bytes(descriptors[1], 'source',
                                    packet['sourceBytes'], self.maximum_bytes + 1, row_capture)
                                transferred = row_record['transferObjects']
                                _require(not _same_object(transferred[0]['before'], transferred[1]['before']),
                                         'native preparation objects alias')
                                _require(packet['sourcePresent'] or not source,
                                         'absent native read cannot carry bytes')
                                read = self._native_json(metadata)
                                row_record['helperRead'] = read
                                _require(type(read) is dict and set(read) == {
                                    'path', 'directories', 'file', 'readReachedEof', 'readReturned', 'exception'}
                                    and read['path'] == binding['path']
                                    and type(read['readReachedEof']) is bool and type(read['readReturned']) is bool
                                    and type(read['directories']) is list,
                                    'native read metadata is malformed')
                                read['bytes'] = optional_bytes(source if packet['sourcePresent'] else None)
                                if read['readReturned']:
                                    _require(read['readReachedEof'] and read['exception'] is None
                                             and packet['sourcePresent'] and len(source) == binding['byteCount']
                                             and hashlib.sha256(source).hexdigest() == binding['sha256'],
                                             'completed native read differs from daemon source binding')
                                else:
                                    _require(type(read['exception']) is dict,
                                             'failed native read has no retained exception')
                                    read_failed = True
                                subject.recheck()
                                reply = {**context, 'operation': 'native-preparation-retained',
                                    'sequence': sequence, 'previousReceiptSha256': previous,
                                    'kind': packet['kind'], 'selector': packet['selector'],
                                    'transferId': packet['transferId'],
                                    'metadataSha256': hashlib.sha256(metadata).hexdigest(),
                                    'sourcePresent': packet['sourcePresent'],
                                    'sourceSha256': hashlib.sha256(source).hexdigest(),
                                    'recordId': row_record['recordId']}
                        row_record['transferDescriptorsClosed'] = True
                        previous = self._native_reply(connection, row_capture, row_record, reply)
                        if terminal:
                            with self.lock:
                                self.native_completions[startup['recordId']] = {
                                    'recordId': row_record['recordId'], 'failed': failed,
                                    'sequence': sequence, 'receiptSha256': previous}
                            return
                        sequence += 1
                    except BaseException as error:
                        row_record['exception'] = exception_observation(error)
                        try:
                            self._retain(row_record)
                        except BaseException as secondary:
                            error.add_note('native receive failure retention also failed: ' + str(secondary))
                            error._worldline_retention_failed = True
                        raise
        except BaseException as error:
            primary = error
            failed = self._record('native-preparation-failure')
            failed.update(startupContext=context, sequence=sequence, previousReceiptSha256=previous,
                          exception=exception_observation(error), openObservation=record)
            try:
                self._retain(failed)
            except BaseException as secondary:
                error.add_note('native preparation failure retention also failed: ' + str(secondary))
                error._worldline_retention_failed = True
            raise
        finally:
            try:
                self._retain(cleanup)
            except BaseException as error:
                if primary is None:
                    raise
                primary.add_note('native descriptor cleanup retention also failed: ' + str(error))
                primary._worldline_retention_failed = True

    def _entry_preparation(self, connection, subject, peer, startup):
        """Retain a separate post-startup exchange, without upgrading authority."""
        from .private_evaluator import _validate_entry_binding
        record = self._record('examiner-entry-preparation-receive')
        record.update(scope='post-GO-entry-preparation-receive-only',
                      startupRecordId=startup['recordId'], helperReport=None,
                      transferDescriptorsClosed=False)
        capture = _Capture(record, self.maximum_bytes,
                           time.monotonic() + self.plan['timeout'], self.stop)
        original_capture = subject.capture
        subject.capture = capture
        def unique_fields(pairs):
            result = {}
            for key, value in pairs:
                _require(key not in result, 'duplicate entry observation field')
                result[key] = value
            return result
        def invalid_constant(value):
            raise RoleObservationFailure('nonfinite entry observation number: ' + value)
        def finite_float(value):
            result = float(value)
            _require(math.isfinite(result), 'entry observation number overflows to nonfinite')
            return result
        try:
            with _DescriptorOwner(record) as handles:
                payload, descriptors = self._packet(connection, capture, handles, peer)
                request = json.loads(payload, object_pairs_hook=unique_fields,
                                     parse_constant=invalid_constant, parse_float=finite_float)
                keys = {'schemaVersion', 'operation', 'runId', 'startupRecordId',
                        'transferId', 'metadataBytes', 'sourcePresent', 'sourceBytes'}
                _require(type(request) is dict and set(request) == keys
                         and type(request['schemaVersion']) is int and request['schemaVersion'] == 1
                         and request['operation'] == 'examiner-entry-prepared'
                         and request['runId'] == self.plan['runId']
                         and request['startupRecordId'] == startup['recordId']
                         and type(request['transferId']) is str
                         and str(uuid.UUID(request['transferId'])) == request['transferId']
                         and type(request['sourcePresent']) is bool,
                         'entry preparation packet differs from current startup')
                record['request'] = request
                _require(len(descriptors) == 2, 'entry preparation needs exactly two owned objects')
                subject.recheck()
                metadata = self._entry_object_bytes(descriptors[0], 'metadata',
                    request['metadataBytes'], self.maximum_bytes, capture)
                source = self._entry_object_bytes(descriptors[1], 'source',
                    request['sourceBytes'], self.maximum_bytes + 1, capture)
                objects = record['transferObjects']
                _require(not _same_object(objects[0]['before'], objects[1]['before']),
                         'entry preparation objects alias')
                _require(request['sourcePresent'] or not source,
                         'absent source may not carry bytes')
                report = json.loads(metadata, object_pairs_hook=unique_fields,
                                    parse_constant=invalid_constant, parse_float=finite_float)
                record['helperReport'] = report
                _require(type(report) is dict and set(report) == {
                    'schemaVersion', 'kind', 'runId', 'producer', 'binding', 'read', 'compile', 'exception'}
                    and type(report['schemaVersion']) is int and report['schemaVersion'] == 1
                    and report['kind'] == 'examiner-entry-preparation'
                    and report['producer'] == 'pre-entry-helper-report'
                    and report['runId'] == self.plan['runId'], 'invalid helper preparation envelope')
                binding = _validate_entry_binding(report['binding'], self.plan['runId'], self.plan['argv'][1])
                _require(binding == self.plan['examinerEntryBinding'], 'entry preparation source binding differs')
                read, compiled = report['read'], report['compile']
                _require(type(read) is dict and set(read) == {
                    'path', 'directories', 'file', 'readReachedEof', 'readReturned', 'exception'}
                    and read['path'] == binding['path']
                    and type(read['readReachedEof']) is bool and type(read['readReturned']) is bool
                    and type(read['directories']) is list,
                    'entry preparation read fields are malformed')
                read['bytes'] = optional_bytes(source if request['sourcePresent'] else None)
                _require(type(compiled) is dict and set(compiled) == {'started', 'returned', 'exception'}
                         and type(compiled['started']) is bool and type(compiled['returned']) is bool,
                         'entry preparation compile fields are malformed')
                if report['exception'] is None:
                    _require(read['readReturned'] and read['readReachedEof'] and read['exception'] is None
                             and compiled['started'] and compiled['returned'] and compiled['exception'] is None
                             and request['sourcePresent'] and len(source) == binding['byteCount']
                             and hashlib.sha256(source).hexdigest() == binding['sha256'],
                             'successful entry preparation differs from actual bound source')
                    if 'nativeGuard' in self.plan:
                        # The separate stream's reply can reach the child just
                        # before its final daemon bookkeeping/owned closes. Wait
                        # under this existing deadline, never infer completion.
                        while not self.native_finished.wait(0.1):
                            capture.check()
                        with self.lock:
                            completed = self.native_completions.get(startup['recordId'])
                            _require(self.failure is None and completed is not None
                                     and completed['failed'] is False,
                                     'successful entry lacks complete retained native preparation')
                            record['nativePreparation'] = dict(completed)
                else:
                    _require(type(report['exception']) is dict and not compiled['returned'],
                             'failed entry preparation has inconsistent completion fields')
                # The sender half-closes after its single packet. Extra packets or
                # handles are rejected and cleaned before any retention ACK.
                final, extra = self._packet(connection, capture, handles, peer, allow_eof=True)
                _require(final == b'' and not extra, 'extra entry preparation transfer')
                subject.recheck()
            record['transferDescriptorsClosed'] = True
            self._retain(record)
            # Do not perform new proc reads after the complete record has been
            # retained. The held pidfd alone checks liveness before the ACK.
            ready = bool(select.select([subject.pidfd], [], [], 0)[0])
            _require(not ready, 'examiner exited before entry retention acknowledgement')
            response = {'schemaVersion': 1, 'operation': 'examiner-entry-retained',
                'runId': self.plan['runId'], 'startupRecordId': startup['recordId'],
                'transferId': request['transferId'], 'recordId': record['recordId'],
                'entrySource': binding, 'metadataSha256': hashlib.sha256(metadata).hexdigest(),
                'sourceSha256': hashlib.sha256(source).hexdigest(),
                'sourcePresent': request['sourcePresent']}
            encoded = json.dumps(response).encode('utf8')
            _require(len(encoded) <= self.maximum_request and connection.send(encoded) == len(encoded),
                     'entry retention acknowledgement was incomplete')
            self._retain({'schemaVersion': 1, 'kind': 'examiner-entry-retention-acknowledgement',
                'runId': self.plan['runId'], 'recordId': record['recordId'],
                'startupRecordId': startup['recordId'], 'sent': True,
                'preSendPidfdReady': ready,
                'bytes': optional_bytes(encoded), 'meaning': 'retention-only; not compile or confinement authority'})
        except BaseException as error:
            record['exception'] = exception_observation(error)
            record['errno'] = getattr(error, 'errno', None)
            try:
                self._retain(record)
            except BaseException as secondary:
                error.add_note('entry receive retention also failed: ' + str(secondary))
                error._worldline_retention_failed = True
            raise
        finally:
            subject.capture = original_capture

    def _observe(self, connection):
        record = self._record('role-startup')
        startup_completed = False
        primary = None
        cleanup = self._record('role-held-descriptor-cleanup')
        cleanup['startupRecordId'] = record['recordId']
        try:
            with _DescriptorOwner(cleanup) as stack:
                capture = _Capture(record, self.maximum_bytes,
                                   time.monotonic() + self.handshake_seconds, self.stop)
                credentials = connection.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED,
                                                   struct.calcsize('=iII'))
                record['peerCredentialsBytes'] = optional_bytes(credentials)
                pid, uid, gid = struct.unpack('=iII', credentials)
                record['peerCredentials'] = {'pid': pid, 'uid': uid, 'gid': gid}
                # A kernel reference to THIS connection's process, never pidfd_open(pid).
                pidfd = connection.getsockopt(socket.SOL_SOCKET, SO_PEERPIDFD)
                subject = _Subject(pid, pidfd, capture, stack)
                with ExitStack() as packet_handles:
                    payload, descriptors = self._packet(connection, capture, packet_handles, (pid, uid, gid))
                    _require(not descriptors, 'initial role packet may not pass descriptors')
                record['requestBytes'] = optional_bytes(payload)
                def unique_fields(pairs):
                    value = {}
                    for key, item in pairs:
                        _require(key not in value, 'duplicate startup request field')
                        value[key] = item
                    return value
                request = json.loads(payload, object_pairs_hook=unique_fields)
                _require(isinstance(request, dict) and set(request) == {'schemaVersion', 'runId', 'role'}
                         and type(request['schemaVersion']) is int and request['schemaVersion'] == 1
                         and request['runId'] == self.plan['runId'], 'invalid role startup request')
                role = request['role']
                _require(role in ('examiner', 'worker', 'candidate'), 'unknown requested role')
                _require(self.bootstrap is not None, 'bootstrap has not been anchored')
                record['roleClaim'] = role
                inside = {'examiner': 0, 'worker': 1, 'candidate': 2}[role]
                expected_uid = mapped_identity(self.bootstrap.uid_map, inside)
                expected_gid = mapped_identity(self.bootstrap.gid_map, inside)
                _require((uid, gid) == (expected_uid, expected_gid), 'peer credentials do not match mapped role')
                fields = subject.status
                _require(fields.get(b'Uid', b'').split() == [str(expected_uid).encode()] * 4
                         and fields.get(b'Gid', b'').split() == [str(expected_gid).encode()] * 4
                         and fields.get(b'Groups') == b'' and fields.get(b'NoNewPrivs') == b'1',
                         'kernel role credentials or privileges differ')
                for name in _CAPABILITIES:
                    value = fields.get(name.encode(), b'')
                    _require(re.fullmatch(rb'[0-9a-fA-F]+', value) and int(value, 16) == 0,
                             'kernel role capability field is missing or nonzero')
                _require(subject.uid_map == self.bootstrap.uid_map and subject.gid_map == self.bootstrap.gid_map,
                         'role ID maps differ from observed bootstrap')
                _require(subject.cgroup == self.bootstrap.cgroup, 'role left the observed managed cgroup')
                command = subject.cmdline.split(b'\0')
                prefix = [os.fsencode(item) for item in trusted_script(
                    '/run/worldline-evaluator.py', '--role', role)]
                suffix = command[len(prefix):]
                _require(command[:len(prefix)] == prefix and len(suffix) == 4
                         and suffix[-1] == b'' and suffix[-3] == os.fsencode(self.plan['runId'])
                         and suffix[-2] == str(self.role_namespace_number).encode(),
                         'role command does not match the fixed startup interface')
                payload = json.loads(suffix[0])
                _require(isinstance(payload, list) and payload
                         and all(isinstance(item, str) for item in payload), 'role command payload is malformed')
                if role == 'examiner':
                    _require(payload == self.plan['argv'], 'examiner command differs from daemon plan')
                user = subject.namespaces['user']
                _require(self.role_user_namespace is not None
                         and _same_object(user['object'], self.role_user_namespace)
                         and _same_object(user['parent'], self.bootstrap.namespaces['user']['object'])
                         and user['ownerUid'] == os.geteuid(), 'role user namespace does not match held child')
                record['inheritedDescriptorInventory'] = []
                self._descriptor_inventory(subject, record)
                for name in _NAMESPACES[1:]:
                    entry = subject.namespaces[name]
                    _require(_same_object(entry['owner'], user['object']), 'role namespace has another owner')
                    _require(not _same_object(entry['object'], self.bootstrap.namespaces[name]['object']),
                             'role retained a bootstrap namespace')
                record['ancestry'], ancestors = self._ancestry(subject, capture, stack)
                record['identity'] = subject.identity
                record['procDirectory'] = _object(os.fstat(subject.proc))
                key = (pid, subject.identity['starttime'])
                _require(key not in self.seen, 'role process already rendezvoused')
                self._mounts(subject, role, record, connection, (pid, uid, gid))
                if role == 'examiner' and 'nativeGuard' in self.plan:
                    self._native_mapping(subject, record)
                    record['nativeKernelFilter'] = native_filter_fields(subject.status)
                subject.recheck()
                for descriptor, expected in ancestors:
                    actual = process_identity(capture.read(descriptor, 'stat', expected['pid']))
                    _require(actual == expected, 'ancestor instance or parent changed during capture')
                # Bootstrap liveness uses this capture's fresh deadline and retention.
                original = self.bootstrap.capture
                self.bootstrap.capture = capture
                try:
                    self.bootstrap.recheck()
                finally:
                    self.bootstrap.capture = original
                subject.live()
                response = self._acknowledgement(role, record)
                self._retain(record)
                if role == 'examiner' and 'nativeGuard' in self.plan:
                    with self.lock:
                        _require(self.native_startup is None, 'native examiner startup already published')
                        self.native_startup = {
                            'recordId': record['recordId'], 'peer': (pid, uid, gid),
                            'nativeKernelFilter': record['nativeKernelFilter'],
                            'identity': dict(subject.identity), 'cgroup': subject.cgroup,
                            'namespaces': {name: dict(row['object'])
                                           for name, row in subject.namespaces.items()},
                            'credentialFields': {key: subject.status.get(key) for key in
                                [b'Uid', b'Gid', b'Groups', b'NoNewPrivs',
                                 *(name.encode() for name in _CAPABILITIES)]}}
                # Retained complete proc reads precede the permission to
                # proceed. Check the still-held process handle again without
                # reopening a numeric PID after the retention callback.
                ready = bool(select.select([subject.pidfd], [], [], 0)[0])
                _require(not ready, 'role exited before acknowledgement')
                self.seen.add(key)
                self.roles[record['recordId']] = role
                _require(connection.send(response) == len(response), 'role acknowledgement was incomplete')
                self._retain({'schemaVersion': 1, 'kind': 'role-startup-acknowledgement',
                              'runId': self.plan['runId'], 'recordId': record['recordId'],
                              'preSendPidfdReady': ready, 'sent': True,
                              'bytes': optional_bytes(response)})
                startup_completed = True
                if role == 'examiner':
                    self._entry_preparation(connection, subject, (pid, uid, gid), record)
        except BaseException as error:
            primary = error
            if startup_completed:
                # A preparation failure has its own complete receive record. It
                # cannot rewrite the already retained startup or role roster.
                raise
            record['exception'] = exception_observation(error)
            record['errno'] = getattr(error, 'errno', None)
            try:
                self._retain(record)
            except BaseException as secondary:
                error.add_note('kernel role observation retention also failed: ' + str(secondary))
                error._worldline_retention_failed = True
            raise

        finally:
            try:
                self._retain(cleanup)
            except BaseException as error:
                if primary is None:
                    raise
                primary.add_note('held descriptor cleanup retention also failed: ' + str(error))
                primary._worldline_retention_failed = True

    def _serve(self):
        try:
            while not self.stop.is_set():
                try:
                    connection, _address = self.listener.accept()
                except TimeoutError:
                    continue
                except OSError:
                    if self.stop.is_set():
                        return
                    raise
                with connection:
                    with self.lock:
                        self.active = connection
                    connection.settimeout(0.1)
                    try:
                        self._observe(connection)
                    finally:
                        with self.lock:
                            self.active = None
        except BaseException as error:
            self._remember_failure(error)
        finally:
            self._service_complete(native=False)

    def _remember_failure(self, error):
        with self.lock:
            if self.failure is None:
                self.failure = error
            elif self.failure is not error:
                self.failure.add_note('another owned observer failure: ' + str(error))
                if retention_failed(error):
                    self.failure._worldline_retention_failed = True

    def _service_complete(self, *, native):
        # Neither service may close shared invocation state under the other.
        with self.lock:
            if native == 'lifetime':
                self.lifetime_service_done = True
            elif native:
                self.native_service_done = True
            else:
                self.service_done = True
            cleanup = (self.cleanup_deferred and self.service_done and self.native_service_done
                       and self.lifetime_service_done
                       and not self.cleanup_claimed)
            if cleanup:
                self.cleanup_claimed = True
        if cleanup:
            try:
                self._cleanup_stack('observer-thread')
            except BaseException as error:
                self._remember_failure(error)

    def _serve_native(self):
        try:
            while not self.stop.is_set():
                try:
                    connection, _address = self.native_listener.accept()
                except TimeoutError:
                    continue
                except OSError:
                    if self.stop.is_set():
                        return
                    raise
                with connection:
                    with self.lock:
                        self.native_active = connection
                    connection.settimeout(0.1)
                    try:
                        self._native_preparation(connection)
                        self.native_finished.set()
                    finally:
                        with self.lock:
                            self.native_active = None
        except BaseException as error:
            self._remember_failure(error)
        finally:
            self.native_finished.set()
            self._service_complete(native=True)

    def _serve_lifetime(self):
        from .native_lifetime import receive
        try:
            while not self.stop.is_set():
                try:
                    connection, _address = self.lifetime_listener.accept()
                except TimeoutError:
                    continue
                except OSError:
                    if self.stop.is_set():
                        return
                    raise
                with connection:
                    with self.lock:
                        self.lifetime_active = connection
                    connection.settimeout(0.1)
                    try:
                        receive(self, connection)
                    finally:
                        with self.lock:
                            self.lifetime_active = None
        except BaseException as error:
            self._remember_failure(error)
        finally:
            self._service_complete(native='lifetime')

    def finish(self, boundary):
        self._close()
        claimed = [boundary.get('examiner')]
        workers = boundary.get('workers')
        _require(isinstance(workers, list), 'worker startup roster is missing')
        claimed.extend(item.get('observation') for item in workers if isinstance(item, dict))
        _require(len(claimed) == len(workers) + 1, 'worker startup roster is malformed')
        ids = []
        for observation in claimed:
            _require(isinstance(observation, dict), 'role compatibility observation is missing')
            record_id = observation.get('kernelObservationId')
            _require(isinstance(record_id, str) and record_id in self.roles
                     and self.roles[record_id] == observation.get('role'),
                     'role compatibility frame is not bound to a kernel observation')
            ids.append(record_id)
        _require(len(set(ids)) == len(ids) and set(ids) == set(self.roles),
                 'kernel role startup roster is incomplete or duplicated')
        if 'nativeGuard' in self.plan:
            startup = self.native_startup
            completed = None if startup is None else self.lifetime_completions.get(startup['recordId'])
            _require(completed is not None and completed['retainedToNativeFinalization'] is True,
                     'examiner lacks complete ordered native lifetime termination')
            outcome = self._record('native-lifetime-process-outcome')
            outcome.update(scope='retained-native-terminal-and-existing-process-wait-join',
                startupRecordId=startup['recordId'], nativeTerminal=completed,
                fixedBootstrapExaminerWait=boundary.get('examinerReturnCode'),
                actualBootstrapWait=boundary.get('bootstrapExitCode'),
                observerServicesJoined=True, protectedCustody=False,
                cleanReportedProcess=(completed['cleanReportedTerminal']
                    and type(boundary.get('examinerReturnCode')) is int
                    and boundary['examinerReturnCode'] == 0
                    and type(boundary.get('bootstrapExitCode')) is int
                    and boundary['bootstrapExitCode'] == 0))
            self._retain(outcome)
        return self.records

    def _close(self):
        with self.lock:
            _require(not self.join_incomplete, 'kernel observer thread join was incomplete')
            channels = [('listener', getattr(self, 'listener', None)),
                        ('native-listener', self.native_listener),
                        ('lifetime-listener', self.lifetime_listener),
                        ('active-role', self.active), ('active-native', self.native_active),
                        ('active-lifetime', self.lifetime_active)]
            threads = [('role', self.thread), ('native', self.native_thread),
                       ('lifetime', self.lifetime_thread)]
        self.stop.set()
        closure = {'schemaVersion': 1, 'kind': 'observer-channel-cleanup',
                   'runId': self.plan['runId'], 'closes': [], 'joins': []}
        # A close or join failure cannot abandon the other service or leave
        # ownership unset. Do not hold the service lock across close callbacks.
        for name, channel in channels:
            if channel is None:
                continue
            event = {'channel': name, 'returned': False, 'exception': None}
            closure['closes'].append(event)
            try:
                channel.close()
                event['returned'] = True
            except BaseException as error:
                event['exception'] = exception_observation(error)
                self._remember_failure(error)
        join_deadline = time.monotonic() + 10
        pending = False
        for name, thread in threads:
            if thread is None:
                continue
            event = {'service': name, 'joinReturned': False, 'joinException': None,
                     'alive': None, 'aliveException': None}
            closure['joins'].append(event)
            try:
                thread.join(timeout=max(0, join_deadline - time.monotonic()))
                event['joinReturned'] = True
            except BaseException as error:
                event['joinException'] = exception_observation(error)
                self._remember_failure(error)
            try:
                event['alive'] = thread.is_alive()
                pending = pending or event['alive']
            except BaseException as error:
                event['aliveException'] = exception_observation(error)
                self._remember_failure(error)
                pending = True
        with self.lock:
            if pending:
                self.join_incomplete = True
                self.cleanup_deferred = not (self.service_done and self.native_service_done
                                             and self.lifetime_service_done)
            else:
                self.thread = None
                self.native_thread = None
                self.lifetime_thread = None
            cleanup = not self.cleanup_deferred and not self.cleanup_claimed
            if cleanup:
                self.cleanup_claimed = True
        if closure['closes'] or closure['joins']:
            try:
                self._retain(closure)
            except BaseException as error:
                self._remember_failure(error)
        if cleanup:
            try:
                self._cleanup_stack('caller')
            except BaseException as error:
                self._remember_failure(error)
        if pending:
            self._remember_failure(RoleObservationFailure('kernel observer thread did not terminate'))
            try:
                self._retain({'schemaVersion': 1, 'kind': 'observer-join-incomplete',
                              'runId': self.plan['runId'], 'threadJoined': False,
                              'owner': 'observer-thread' if self.cleanup_deferred else 'caller',
                              'cleanupDeferred': self.cleanup_deferred,
                              'observed_ns': time.monotonic_ns()})
            except BaseException as error:
                self._remember_failure(error)
        with self.lock:
            failure = self.failure
        if failure is not None:
            raise failure

    def _cleanup_stack(self, owner):
        record = {'schemaVersion': 1, 'kind': 'observer-cleanup', 'runId': self.plan['runId'],
                  'owner': owner, 'returned': False, 'exception': None}
        try:
            self.stack.close()
            record['returned'] = True
        except BaseException as error:
            record['exception'] = exception_observation(error)
            try:
                self._retain(record)
            except BaseException as secondary:
                error.add_note('observer cleanup retention also failed: ' + str(secondary))
                error._worldline_retention_failed = True
            raise
        self._retain(record)

    def __exit__(self, _type, error, _traceback):
        try:
            self._close()
        except BaseException as secondary:
            secondary.kernel_role_observations = self.records
            if error is None:
                raise
            error.add_note('kernel role observer cleanup also failed: ' + str(secondary))
            if retention_failed(secondary):
                error._worldline_retention_failed = True
        finally:
            if error is not None:
                error.kernel_role_observations = self.records
