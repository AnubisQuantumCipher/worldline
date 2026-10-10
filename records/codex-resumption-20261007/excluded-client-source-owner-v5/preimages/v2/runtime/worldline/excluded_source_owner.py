"""Fixed original-client clean-exec owner; Python acquires, native decides.

This is not RootWorker enrollment or a private read RPC. Only the fixed sealed
projection crosses exec. Target socket creation belongs solely to the dropped
actor. The original helper owns both actual process-local final checks.
"""
from __future__ import annotations
import ctypes as C
import fcntl
import json
import os
from pathlib import Path
import select
import selectors
import socket
import stat
import signal
import subprocess
import sys
import time
from .root_worker_custody import _memfd, _send_fd, _receive_fd, channel_source, SEALS
from .custody_subject_capture import fd_identity, socket_capture, socket_document, kcmp, close_descriptor
from .root_worker_codec import archive
from .errors import CoreUnavailable
from .protected_startup import require

SCHEMA = 'worldline.fixed-original-client-source-owner-v1'
KEYS = {'schema', 'request', 'entry', 'descriptor', 'import_roots', 'actor_closure',
        'retention_directory', 'timeout'}


def _exact(raw):
    def pairs(rows):
        result = {}
        for key, value in rows:
            require(key not in result, 'SOURCE_OWNER_DUPLICATE_SELECTION')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs)


def _identity(info):
    return {'device': info.st_dev, 'inode': info.st_ino, 'mode': info.st_mode,
            'uid': info.st_uid, 'gid': info.st_gid, 'nlink': info.st_nlink,
            'size': info.st_size, 'mtime_ns': info.st_mtime_ns, 'ctime_ns': info.st_ctime_ns}


def _write(fd, raw):
    position = 0
    while position < len(raw):
        count = os.write(fd, raw[position:])
        require(count > 0, 'SOURCE_OWNER_RETENTION_WRITE_UNKNOWN')
        position += count


def _poll(fd):
    poll = select.poll(); poll.register(fd, 25)
    rows = poll.poll(0)
    return {'call': 'poll', 'args': {'fd': fd, 'events': 25, 'timeout': 0},
            'result': len(rows), 'errno': 0, 'revents': 0 if not rows else rows[0][1]}


def _error(error):
    return {'type': type(error).__name__, 'message': str(error),
            'errno': getattr(error, 'errno', None), 'notes': list(getattr(error, '__notes__', ())) }


class OriginalClientSourceOwner:
    def __init__(self, lease, approved, request_path, entry):
        require(type(lease) is approved.ApprovedSourceLease and not lease.excluded_actor(),
                'SOURCE_OWNER_REAL_EARLY_ROOT_LEASE_REQUIRED')
        require(os.geteuid() == 0, 'SOURCE_OWNER_REAL_ROOT_CREDENTIALS_REQUIRED')
        self.lease, self.approved = lease, approved
        self.plan_path = approved._path(request_path + '.source-owner.json')
        self.plan_raw = lease.file(self.plan_path, ('DATA',)); self.plan = _exact(self.plan_raw)
        require(set(self.plan) == KEYS and self.plan['schema'] == SCHEMA and
                self.plan['request'] == request_path and self.plan['entry'] == entry,
                'SOURCE_OWNER_FIXED_ORIGINAL_INVOCATION_REQUIRED')
        self.request_raw = lease.file(request_path, ('DATA',)); self.request = json.loads(self.request_raw)
        self.descriptor_raw = lease.file(self.plan['descriptor'], ('DATA',))
        self.installation = _exact(self.descriptor_raw)
        self.fds = []; self.child = None; self.pidfd = None; self.pidfd_duplicate = None; self.channel = None
        self.actor_channel = None
        self.failure = None; self.frame = None; self.native = None; self.last_native_call = None
        self.streams = {}; self.retention = None; self.log = None; self.watch_parts = []
        self.stop_receipts = []; self.cleanup_receipts = []
        self.started = time.monotonic(); self.deadline = self.started + self.plan['timeout']
        self.owner = None
        lease.owner_completion(self.complete)
        for root in self.plan['import_roots']: lease.directory_or_absent(root)
        require(self.plan['import_roots'] == [str(Path(__file__).parents[1])],
                'SOURCE_OWNER_SAME_SELECTED_RUNTIME_REQUIRED')
        directory = approved._path(self.plan['retention_directory'])
        approved._protected(directory, directory=True, private=True)
        self.retention = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW)
        self.fds.append(self.retention)
        self.log = os.open('source-owner.archive', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW,
                           0o600, dir_fd=self.retention)
        self.fds.append(self.log); os.fsync(self.retention)
        self.owner = approved.process_facts()
        self.owner_identity = {name: self.owner[name] for name in
                              ('pid', 'boot_hex', 'start_tick', 'namespaces', 'real_uid', 'real_gid')}
        self.retain('OWNER_INITIAL', {'plan_path': self.plan_path, 'plan_raw': self.plan_raw,
            'request_raw': self.request_raw, 'descriptor_raw': self.descriptor_raw,
            'owner': self.owner, 'source': self.lease.check(),
            'argv': list(sys.orig_argv), 'environment': dict(os.environ)})
        self.prctl_library = C.CDLL(None, use_errno=True)
        self.prctl = self.prctl_library.prctl
        self.prctl.argtypes = [C.c_int, C.c_ulong, C.c_ulong, C.c_ulong, C.c_ulong]
        self.prctl.restype = C.c_int
        self.memory_set = self.memory_receipt(4)
        self.retain('ACTUAL_OWNER_MEMORY_EXCLUSION', self.memory_set)

    def memory_receipt(self, option):
        source = self.lease.check()
        caller = self.approved.process_facts()
        C.set_errno(0); result = self.prctl(option, 0, 0, 0, 0)
        return {'call': 'prctl', 'args': {'option': option, 'arg2': 0, 'arg3': 0, 'arg4': 0, 'arg5': 0},
                'result': result, 'errno': C.get_errno() if result < 0 else 0,
                'caller': caller, 'caller_stat': bytes.fromhex(caller['stat_hex']), 'source': source}

    def prepare_outputs(self):
        libc = C.CDLL(None, use_errno=True)
        init = libc.inotify_init1; init.argtypes = [C.c_int]; init.restype = C.c_int
        add = libc.inotify_add_watch; add.argtypes = [C.c_int, C.c_char_p, C.c_uint32]; add.restype = C.c_int
        C.set_errno(0); self.watch = init(os.O_NONBLOCK | os.O_CLOEXEC)
        watch_errno = C.get_errno() if self.watch < 0 else 0
        if self.watch >= 0: self.fds.append(self.watch)
        self.watch_origin = {'call': 'inotify_init1', 'args': {'flags': os.O_NONBLOCK | os.O_CLOEXEC},
            'result': self.watch, 'errno': watch_errno, 'source': self.lease.check(),
            'descriptor': None if self.watch < 0 else {**fd_identity(self.watch), 'fd': self.watch}}
        require(self.watch >= 0, 'SOURCE_OWNER_INOTIFY_UNAVAILABLE:' + str(C.get_errno()))
        self.watch_parts = []
        for index, name in enumerate(('stdout', 'stderr'), 1):
            writer = os.open('actor.' + name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                             0o600, dir_fd=self.retention)
            self.fds.append(writer)
            reader = os.open('actor.' + name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=self.retention)
            self.fds.append(reader)
            self.streams[name] = {'fd': reader, 'writer': writer, 'parts': [], 'eof': None,
                                 'actor_fd': index, 'writer_close': None}
            path = ('/proc/self/fd/' + str(reader)).encode('ascii')
            C.set_errno(0); wd = add(self.watch, path, 0x00000002 | 0x00000008 | 0x00000400 | 0x00000800)
            require(wd >= 0, 'SOURCE_OWNER_OUTPUT_WATCH_UNAVAILABLE:' + str(C.get_errno()))
            self.streams[name].update(
                origin={**fd_identity(writer), 'fd': writer},
                reader_origin={**fd_identity(reader), 'fd': reader},
                watch={'call': 'inotify_add_watch', 'fd': self.watch,
                    'path': path, 'mask': 0x00000002 | 0x00000008 | 0x00000400 | 0x00000800,
                    'result': wd, 'errno': 0, 'source': self.lease.check(),
                    'descriptor': {**fd_identity(self.watch), 'fd': self.watch}})
        os.fsync(self.retention)
        self.retain('OUTPUTS_PREPARED', {name: {key: value for key, value in stream.items() if key != 'parts'}
                                       for name, stream in self.streams.items()})

    def emit_outputs(self):
        source = self.lease.check()
        for name, stream in self.streams.items():
            while True:
                receipt = {'call': 'read', 'args': {'fd': stream['fd'], 'count': 65536},
                           'source': source, 'descriptor': {**fd_identity(stream['fd']), 'fd': stream['fd']}}
                try: chunk = os.read(stream['fd'], 65536)
                except OSError as error:
                    receipt.update(raw=b'', result=-1, errno=error.errno)
                    stream['parts'].append(receipt); raise
                receipt.update(raw=chunk, result=len(chunk), errno=0)
                stream['parts'].append(receipt)
                if not chunk: break
                _write(1 if name == 'stdout' else 2, chunk)

    def drain_watch(self):
        source = self.lease.check()
        while True:
            receipt = {'call': 'read', 'args': {'fd': self.watch, 'count': 65536}, 'source': source,
                       'descriptor': {**fd_identity(self.watch), 'fd': self.watch}}
            try: raw = os.read(self.watch, 65536)
            except BlockingIOError as error:
                receipt.update(raw=b'', result=-1, errno=error.errno)
                self.watch_parts.append(receipt)
                self.retain('ACTUAL_OUTPUT_WATCH', receipt)
                return
            except OSError as error:
                receipt.update(raw=b'', result=-1, errno=error.errno)
                self.watch_parts.append(receipt)
                self.retain('ACTUAL_OUTPUT_WATCH', receipt)
                raise
            receipt.update(raw=raw, result=len(raw), errno=0)
            self.watch_parts.append(receipt)
            self.retain('ACTUAL_OUTPUT_WATCH', receipt)
            require(raw, 'SOURCE_OWNER_WATCH_EOF_UNKNOWN')

    def pidfd_ofd(self, source):
        return {'origin': self.frame['pidfd'], 'current': {**fd_identity(self.pidfd), 'fd': self.pidfd},
                'duplicate_origin': self.frame['pidfd_duplicate'],
                'duplicate_current': {**fd_identity(self.pidfd_duplicate), 'fd': self.pidfd_duplicate},
                'kcmp': kcmp(os.getpid(), os.getpid(), self.pidfd, self.pidfd_duplicate, source),
                'source': source}

    def retain_stream(self, stream, source):
        before = {**fd_identity(stream['fd']), 'fd': stream['fd']}
        receipt = {'call': 'fsync', 'args': {'fd': stream['fd']}, 'source': source}
        errors = []
        try: os.fsync(stream['fd'])
        except OSError as error:
            receipt.update(result=-1, errno=error.errno)
            stream['fsync_failure'] = receipt; errors.append(_error(error))
        else: receipt.update(result=0, errno=0)
        values = []; reads = []
        for _ in range(2):
            read = {'call': 'pread', 'args': {'fd': stream['fd'], 'count': before['size'], 'offset': 0}, 'source': source}
            try: value = os.pread(stream['fd'], before['size'], 0)
            except OSError as error:
                value = None; read.update(raw=None, result=-1, errno=error.errno); errors.append(_error(error))
            else: read.update(raw=value, result=len(value), errno=0)
            values.append(value); reads.append(read)
        after = {**fd_identity(stream['fd']), 'fd': stream['fd']}
        return {'raw': values[0], 'readback': values[1], 'parts': stream['parts'], 'identity': after,
                'eof': stream['parts'][-1]['result'] if stream['parts'] else None,
                'fsync': receipt, 'before': before, 'reads': reads, 'errors': errors}

    def stop_owned_actor(self, primary):
        if self.child is None or self.child.returncode is not None: return
        receipt = {'owner_pid': os.getpid(), 'child_pid': self.child.pid,
                   'deadline': self.deadline, 'reason': None if primary is None else _error(primary)}
        self.stop_receipts.append(receipt)
        try:
            if self.pidfd is not None:
                receipt['signal'] = {'call': 'pidfd_send_signal',
                    'args': {'pidfd': self.pidfd, 'signal': signal.SIGKILL, 'siginfo': None, 'flags': 0}}
                try: signal.pidfd_send_signal(self.pidfd, signal.SIGKILL, None, 0)
                except OSError as error:
                    receipt['signal'].update(result=-1, errno=error.errno)
                    if error.errno != 3: raise
                else: receipt['signal'].update(result=0, errno=0)
            else:
                # The direct Popen child cannot recycle its PID until this
                # owner actually reaps it. WNOHANG first preserves that fact.
                result = os.waitpid(self.child.pid, os.WNOHANG)
                receipt['probe_waitpid'] = {'call': 'waitpid', 'args': {'pid': self.child.pid, 'options': os.WNOHANG},
                                          'api_result': result, 'errno': 0}
                if result[0] == self.child.pid:
                    self.child.returncode = os.waitstatus_to_exitcode(result[1])
                    receipt['actual_wait'] = self.child.returncode
                    return
                require(result == (0, 0), 'SOURCE_OWNER_DIRECT_CHILD_WAIT_UNKNOWN')
                receipt['signal'] = {'call': 'kill', 'args': {'pid': self.child.pid, 'signal': signal.SIGKILL},
                                     'owned_unreaped_child': receipt['probe_waitpid']}
                try: os.kill(self.child.pid, signal.SIGKILL)
                except OSError as error:
                    receipt['signal'].update(result=-1, errno=error.errno)
                    if error.errno != 3: raise
                else: receipt['signal'].update(result=0, errno=0)
            remaining = max(0, self.deadline - time.monotonic())
            if self.pidfd is not None:
                poller = select.poll(); poller.register(self.pidfd, 25)
                receipt['poll'] = {'call': 'poll', 'args': {'fd': self.pidfd, 'events': 25,
                    'timeout': int(remaining * 1000)}, 'api_result': poller.poll(int(remaining * 1000)), 'errno': 0}
            result = os.waitpid(self.child.pid, os.WNOHANG)
            receipt['waitpid'] = {'call': 'waitpid', 'args': {'pid': self.child.pid, 'options': os.WNOHANG},
                                  'api_result': result, 'errno': 0}
            if result[0] == self.child.pid:
                self.child.returncode = os.waitstatus_to_exitcode(result[1])
                receipt['actual_wait'] = self.child.returncode
            else:
                receipt['actual_wait'] = None
                receipt['unknown_owned_child'] = self.child.pid
        except BaseException as error:
            receipt['failure'] = _error(error)
            if primary is not None: primary.add_note('actual owned-actor stop/wait failed: ' + repr(error))
        finally:
            if self.log is not None:
                try: self.retain('ACTUAL_FAILURE_STOP_WAIT', receipt)
                except BaseException as retention_error:
                    receipt['retention_failure'] = _error(retention_error)
                    if primary is None: raise
                    primary.add_note('owned-actor stop/wait retention failed: ' + repr(retention_error))


    def retain(self, kind, value):
        raw = archive({'kind': kind, 'value': value})
        _write(self.log, str(len(raw)).encode('ascii') + b'\n' + raw)
        os.fsync(self.log)

    def mapped(self):
        path = self.approved._path(self.installation['runtime']['native_library'])
        role = self.lease.files[path][0]
        raw = self.lease.file(path, (role,)); named = os.stat(path, follow_symlinks=False)
        observations = []; executable = []
        for line in Path('/proc/self/maps').read_text().splitlines():
            fields = line.split(maxsplit=5)
            if len(fields) != 6 or fields[5] != path: continue
            bounds, permissions = fields[:2]
            offset = int(fields[2], 16)
            major, minor = (int(word, 16) for word in fields[3].split(':'))
            inode = int(fields[4], 10)
            fd = os.open('/proc/self/map_files/' + bounds, os.O_RDONLY | os.O_CLOEXEC)
            try:
                info = os.fstat(fd)
                with os.fdopen(os.dup(fd), 'rb') as stream: held = stream.read()
                require((info.st_dev, info.st_ino) == (named.st_dev, named.st_ino) and held == raw,
                        'SOURCE_OWNER_MAPPED_NATIVE_DIFFERS')
                observations.append({'bounds': bounds, 'permissions': permissions,
                    'offset': offset, 'device_major': major, 'device_minor': minor, 'inode': inode,
                    'proc_raw': line.encode('utf-8') + b'\n', 'identity': _identity(info), 'raw': held})
            finally: os.close(fd)
            if 'x' in permissions: executable.append(tuple(int(word, 16) for word in bounds.split('-')))
        address = C.cast(self.native, C.c_void_p).value
        require(address is not None and any(first <= address < last for first, last in executable),
                'SOURCE_OWNER_SYMBOL_OUTSIDE_SELECTED_NATIVE')
        return {'path': path, 'raw': raw, 'named': _identity(named), 'maps': observations, 'symbol': address}

    def private_source_topology(self):
        public_data = {self.plan['request'], *self.request['requests']}
        paths = [self.lease.envelope_path, *(path for path, selected in self.lease.files.items()
                  if selected[0] == 'DATA' and path not in public_data)]
        return [{'path': path, 'identity': _identity(os.stat(path, follow_symlinks=False)),
                 'components': [{'path': str(parent), 'identity': _identity(parent.lstat())}
                                for parent in reversed(Path(path).parents)]} for path in paths]

    def decide(self, phase):
        self.frame['phase'] = phase
        if self.pidfd is not None and self.pidfd_duplicate is not None:
            self.frame['pidfd_ofd_current'] = self.pidfd_ofd(self.lease.check())
        self.frame['owner_source'] = self.lease.check()
        self.frame['private_source_topology'] = self.private_source_topology()
        self.frame['owner_memory_set'] = self.memory_set
        self.frame['owner_memory_get'] = self.memory_receipt(3)
        self.frame['owner_current'] = self.approved.process_facts()
        self.frame['owner_status'] = bytes.fromhex(self.frame['owner_current']['status_hex'])
        self.frame['owner_stat'] = bytes.fromhex(self.frame['owner_current']['stat_hex'])
        self.frame['projection_current_readback'] = self.approved.held_projection_facts(
            self.frame['projection']['fd'], lambda: fcntl.fcntl(self.frame['projection']['fd'], fcntl.F_GET_SEALS))
        self.frame['owner_channel_capture'] = socket_capture(self.channel.fileno(), self.frame['owner_source'])
        self.frame['endpoint_parent_current'] = _identity(os.stat(self.frame['endpoint_parent_path'], follow_symlinks=False))
        self.frame['endpoint_current'] = _identity(os.stat(self.request['endpoint'], follow_symlinks=False))
        self.frame['endpoint_held_current'] = fd_identity(self.frame['endpoint_parent']['fd'])
        self.frame['native_mapping'] = self.mapped()
        self.frame['observed_at_ns'] = time.monotonic_ns()
        envelope = archive(self.frame)
        require(C.c_size_t(len(envelope)).value == len(envelope), 'SOURCE_OWNER_NATIVE_OWNED_EXTENT')
        data = (C.c_ubyte * len(envelope)).from_buffer_copy(envelope); status = C.c_uint64()
        self.retain('NATIVE_INPUT', {'phase': phase, 'raw': envelope})
        code = self.native(data, len(envelope), C.byref(status))
        self.retain('NATIVE_RESULT', {'phase': phase, 'transport': code, 'action': status.value, 'raw': envelope})
        post_mapping = self.mapped(); post_source = self.lease.check()
        self.last_native_call = {'phase': phase, 'transport': code, 'action': status.value, 'raw': envelope,
                                 'post_mapping': post_mapping, 'post_source': post_source}
        require(code == 0, 'SOURCE_OWNER_NATIVE_TRANSPORT_REFUSED')
        return status.value

    def project(self):
        closure = self.plan['actor_closure']
        require(type(closure) is dict and set(closure) == {'files', 'directories', 'absent', 'builtins', 'frozen'},
                'SOURCE_OWNER_COMPLETE_FIXED_ACTOR_CLOSURE_REQUIRED')
        for rows in closure.values():
            require(type(rows) is list and all(type(row) is str for row in rows) and len(rows) == len(set(rows)),
                    'SOURCE_OWNER_EXACT_CLOSURE_SELECTION_REQUIRED')
        selected = {name: set(rows) for name, rows in closure.items()}
        data = {self.plan['request'], *self.request['requests']}
        require({path for path in selected['files'] if self.lease.files[path][0] == 'DATA'} == data,
                'SOURCE_OWNER_PRIVATE_DATA_NOT_ACTOR_INPUT')
        require(self.plan['entry'] in selected['files'] and self.lease.helper_path in selected['files'] and
                self.lease.interpreter in selected['files'], 'SOURCE_OWNER_ACTUAL_CLIENT_IMAGES_REQUIRED')
        parts = [self.approved._HEADER]
        for raw in self.lease.envelope[len(self.approved._HEADER):].splitlines(keepends=True):
            fields = raw.rstrip(b'\n').split(b'\t'); kind = fields[0]
            if kind == b'FILE': include = self.approved._text(fields[2]) in selected['files']
            elif kind == b'DIRECTORY': include = self.approved._text(fields[1]) in selected['directories']
            elif kind == b'ABSENT': include = self.approved._text(fields[1]) in selected['absent']
            elif kind == b'BUILTIN': include = self.approved._text(fields[1]) in selected['builtins']
            elif kind == b'FROZEN': include = self.approved._text(fields[1]) in selected['frozen']
            else: include = kind == b'FLAG'
            if include: parts.append(raw)
        return b''.join(parts)

    def launch(self):
        try:
            self.lease.check()
            raw = self.project(); projection = _memfd(raw); self.fds.append(projection)
            endpoint = Path(self.request['endpoint']); base = self.installation['paths']['authority_root']
            require(str(endpoint) == base + '/authority/protected-runtime/intent.sock' and
                    self.installation['endpoint']['path'] == str(endpoint), 'SOURCE_OWNER_ORIGINAL_ENDPOINT_REQUIRED')
            self.approved._protected(str(endpoint.parent), directory=True)
            parent = os.open(endpoint.parent, os.O_PATH | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
            self.fds.append(parent)
            owner_channel, actor_channel = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)
            self.channel = owner_channel
            self.actor_channel = actor_channel
            owner_channel.setsockopt(socket.SOL_SOCKET, socket.SO_PASSCRED, 1)
            actor_channel.setsockopt(socket.SOL_SOCKET, socket.SO_PASSCRED, 1)
            # Only actual original selected library; a missing symbol refuses
            # before child launch, never falls back to a Python permission.
            library = self.installation['runtime']['native_library']
            self.lease.file(library, (self.lease.files[library][0],))
            self.library = C.CDLL(library, use_errno=True)
            try: self.native = self.library.wl_excluded_source_owner_decide_v1
            except AttributeError as error: raise CoreUnavailable('fixed native source-owner decision unavailable') from error
            self.native.argtypes = [C.c_void_p, C.c_size_t, C.POINTER(C.c_uint64)]
            self.native.restype = C.c_int
            deadline = self.deadline
            optimize = [] if not sys.flags.optimize else ['-' + 'O' * sys.flags.optimize]
            argv = [self.lease.interpreter, '-I', '-S', '-B', *optimize, self.lease.helper_path,
                    '--actor-source-owner', str(actor_channel.fileno()), str(projection), str(parent),
                    '--deadline', repr(deadline), '--entry', self.plan['entry'], '--request', self.plan['request']]
            self.frame = {'schema': 'worldline.fixed-original-client-source-custody-v1', 'phase': 'LAUNCH',
                'plan_path': self.plan_path, 'plan_raw': self.plan_raw, 'plan': self.plan,
                'request_raw': self.request_raw, 'request': self.request,
                'descriptor_raw': self.descriptor_raw, 'installation': self.installation,
                'owner_source': self.lease.check(), 'owner': self.owner,
                'owner_origin_stat': bytes.fromhex(self.owner['stat_hex']),
                'original_argv_raw': bytes.fromhex(self.owner['cmdline_hex']),
                'original_argv': list(sys.orig_argv),
                'actor_argv': argv, 'actor_argv_raw': b''.join(word.encode('utf-8') + b'\0' for word in argv),
                'deadline': deadline, 'deadline_word': repr(deadline), 'projected_source': {'envelope_bytes_hex': raw.hex()},
                'deadline_raw': repr(deadline).encode('ascii'),
                'deadline_ns': int(deadline * 1_000_000_000),
                'projection': {**fd_identity(projection), 'fd': projection, 'seals': fcntl.fcntl(projection, fcntl.F_GET_SEALS)},
                'projection_readback': self.approved.held_projection_facts(
                    projection, lambda: fcntl.fcntl(projection, fcntl.F_GET_SEALS)),
                'endpoint_parent_path': str(endpoint.parent), 'endpoint_parent': {**fd_identity(parent), 'fd': parent},
                'endpoint_parent_named': _identity(endpoint.parent.lstat()), 'endpoint_named': _identity(endpoint.lstat()),
                'actor_channel_origin': {**fd_identity(actor_channel.fileno()), 'fd': actor_channel.fileno()},
                'owner_channel': channel_source(owner_channel), 'messages': [], 'error': None,
                'requests': [{'path': path, 'raw': self.lease.file(path, ('DATA',))} for path in self.request['requests']],
                'child_pid': None, 'pidfd': None, 'terminal': None, 'owner_final_source': None, 'target': None}
            self.prepare_outputs()
            self.frame['output_watch_origin'] = self.watch_origin
            self.frame['output_origins'] = {name: {'origin': stream['origin'], 'actor_fd': stream['actor_fd'],
                'watch': stream['watch'], 'reader_origin': stream['reader_origin'],
                'writer_close': None} for name, stream in self.streams.items()}
            require(self.decide('LAUNCH') == 1, 'SOURCE_OWNER_NATIVE_LAUNCH_REFUSED')
            self.child = subprocess.Popen(argv, close_fds=True, pass_fds=(actor_channel.fileno(), projection, parent),
                                          stdin=subprocess.DEVNULL, stdout=self.streams['stdout']['writer'],
                                          stderr=self.streams['stderr']['writer'],
                                          env=dict(os.environ))
            self.frame['child_pid'] = self.child.pid
            self.pidfd = os.pidfd_open(self.child.pid, 0); self.fds.append(self.pidfd)
            self.frame['pidfd'] = {**fd_identity(self.pidfd), 'fd': self.pidfd}
            self.frame['pidfd_open'] = {'call': 'pidfd_open', 'args': {'pid': self.child.pid, 'flags': 0},
                                        'result': self.pidfd, 'errno': 0}
            self.pidfd_duplicate = os.dup(self.pidfd); self.fds.append(self.pidfd_duplicate)
            self.frame['pidfd_duplicate'] = {**fd_identity(self.pidfd_duplicate), 'fd': self.pidfd_duplicate}
            self.frame['pidfd_dup'] = {'call': 'dup', 'args': {'fd': self.pidfd},
                                      'result': self.pidfd_duplicate, 'errno': 0, 'source': self.lease.check()}
            actor_fd = actor_channel.detach(); self.actor_channel = None; self.fds.append(actor_fd)
            try:
                actor_close = close_descriptor(actor_fd, self.lease.check())
                self.retain('ACTUAL_OWNER_ACTOR_CARRIER_CLOSE', actor_close)
                require(actor_close['result'] == 0 and actor_close['readback'].get('errno') == 9,
                        'SOURCE_OWNER_ACTOR_CARRIER_CLOSE_UNKNOWN')
            finally: self.fds.remove(actor_fd)
            for name, stream in self.streams.items():
                stream['writer_close'] = close_descriptor(stream['writer'], self.lease.check())
                self.frame['output_origins'][name]['writer_close'] = stream['writer_close']
                self.fds.remove(stream['writer'])
            self.run(deadline, projection, parent)
            return self.child.returncode
        except BaseException as error:
            self.failure = error
            if self.frame is not None: self.frame['error'] = _error(error)
            self.stop_owned_actor(error)
            self.retain('FAILURE', {'error': _error(error), 'frame': self.frame})
            raise

    def receive(self, deadline, projection, parent):
        self.channel.settimeout(max(0, deadline - time.monotonic()))
        receipts = []; source = self.lease.check()
        fd = None; target_fd = None; identity = None; raw = None; target_receipts = []
        try:
            fd, sender = _receive_fd(self.channel, receipts, source)
            identity = {**fd_identity(fd), 'fd': fd}; seals = fcntl.fcntl(fd, fcntl.F_GET_SEALS)
            require(stat.S_ISREG(identity['mode']) and seals & SEALS == SEALS,
                    'SOURCE_OWNER_ACTUAL_SEALED_MESSAGE_REQUIRED')
            raw = self.approved._held_bytes(fd); message = _exact(raw)
            kernel = self.approved.process_facts(self.child.pid)
            row = {'message_raw': raw, 'message': message, 'receive': receipts[-1],
                   'message_descriptor': identity, 'message_seals': seals,
                   'owner_source': source, 'kernel': kernel, 'poll': _poll(self.pidfd),
                   'actor_stat': bytes.fromhex(message['actor']['stat_hex']),
                   'kernel_stat': bytes.fromhex(kernel['stat_hex']),
                   'actor_status': bytes.fromhex(message['actor']['status_hex']),
                   'kernel_status': bytes.fromhex(kernel['status_hex']),
                   'channel_current': _identity(os.stat('/proc/' + str(self.child.pid) + '/fd/' + str(self.frame['actor_channel_origin']['fd']))),
                   'projection_current': _identity(os.stat('/proc/' + str(self.child.pid) + '/fd/' + str(projection))),
                   'parent_current': _identity(os.stat('/proc/' + str(self.child.pid) + '/fd/' + str(parent)))}
            row['output_current'] = {name: _identity(os.stat('/proc/' + str(self.child.pid) + '/fd/' + str(stream['actor_fd'])))
                                     for name, stream in self.streams.items()}
            row['owner_current'] = self.approved.process_facts()
            row['owner_status'] = bytes.fromhex(row['owner_current']['status_hex'])
            row['owner_stat'] = bytes.fromhex(row['owner_current']['stat_hex'])
            row['observed_at'] = time.monotonic()
            row['observed_at_ns'] = time.monotonic_ns()
            self.frame['messages'].append(row)
            if message['target'] is not None and self.frame['target'] is None:
                target_fd, target_sender = _receive_fd(self.channel, target_receipts, source)
                actor_fd = message['target']['descriptor']['fd']
                target_capture = socket_capture(target_fd, source)
                self.frame['target'] = {'message': message['target'], 'sequence': message['sequence'],
                    'receive': target_receipts[-1], 'sender': target_sender,
                    'capture': target_capture, 'peer': socket_document(target_capture)['peer'],
                    'descriptor': {**fd_identity(target_fd), 'fd': target_fd},
                    'kernel_descriptor': _identity(os.stat('/proc/' + str(self.child.pid) + '/fd/' + str(actor_fd))),
                    'kcmp': kcmp(os.getpid(), self.child.pid, target_fd, actor_fd, source),
                    'close': None}
            action = self.decide('ACQUIRE')
            require(action in (1, 2), 'SOURCE_OWNER_NATIVE_ACQUISITION_REFUSED')
            if target_fd is not None:
                self.frame['target']['close'] = close_descriptor(target_fd, source)
                require(self.frame['target']['close']['result'] == 0, 'SOURCE_OWNER_TARGET_DUPLICATE_CLOSE_UNKNOWN')
                target_fd = None
                self.retain('ACTUAL_TARGET_DUPLICATE_CLOSED', self.frame['target'])
                require(self.decide('ACQUIRE') == 2, 'SOURCE_OWNER_TARGET_CLOSED_CUSTODY_REFUSED')
            reply = {'schema': 'worldline.fixed-source-owner-reply-v1', 'sequence': message['sequence'],
                     'projection_hex': self.frame['projected_source']['envelope_bytes_hex'],
                     'owner': self.owner_identity, 'native_action': action}
            reply_fd = _memfd(json.dumps(reply, ensure_ascii=True, separators=(',', ':'), allow_nan=False).encode('ascii'))
            try:
                sent = []; _send_fd(self.channel, reply_fd, sent, self.lease.check())
                self.retain('REPLY', {'send': sent, 'raw': self.approved._held_bytes(reply_fd)})
            finally: os.close(reply_fd)
            return message['kind'] == 'COMPLETE'
        except BaseException as error:
            self.retain('MESSAGE_FAILURE', {'error': _error(error), 'receive': receipts,
                                           'target_receive': target_receipts, 'descriptor': identity, 'raw': raw})
            raise
        finally:
            if fd is not None: os.close(fd)
            if target_fd is not None:
                closed = close_descriptor(target_fd, source)
                self.retain('FAILED_TARGET_DUPLICATE_CLOSE', closed)

    def run(self, deadline, projection, parent):
        selector = selectors.DefaultSelector()
        completed = False
        try:
            selector.register(self.channel, selectors.EVENT_READ, 'channel')
            selector.register(self.watch, selectors.EVENT_READ, 'output')
            while not completed:
                self.emit_outputs()
                remaining = deadline - time.monotonic()
                require(remaining > 0, 'SOURCE_OWNER_ORIGINAL_ACTION_DEADLINE_EXCEEDED')
                events = selector.select(remaining)
                require(events, 'SOURCE_OWNER_ORIGINAL_ACTION_TIMEOUT')
                for key, _ in events:
                    if key.data == 'channel':
                        if self.receive(deadline, projection, parent):
                            require(not completed, 'SOURCE_OWNER_ACTOR_COMPLETION_REPLAY')
                            completed = True; selector.unregister(self.channel)
                    else:
                        self.drain_watch()
                        self.emit_outputs()
            # Observe the same held OFD before reaping. A post-reap pidfd may
            # legitimately report Pid:-1; it is never a live-PID substitute.
            poller = select.poll(); poller.register(self.pidfd, 25)
            require(poller.poll(max(0, int((deadline - time.monotonic()) * 1000))),
                    'SOURCE_OWNER_ACTOR_TERMINAL_UNKNOWN')
            source = self.lease.check()
            raw_stat = Path('/proc/' + str(self.child.pid) + '/stat').read_bytes()
            raw_status = Path('/proc/' + str(self.child.pid) + '/status').read_bytes()
            before = {'pidfd': {**fd_identity(self.pidfd), 'fd': self.pidfd},
                'kernel': {'pid': self.child.pid, 'start_tick': int(raw_stat[raw_stat.rfind(b')') + 2:].split()[19]),
                           'stat_hex': raw_stat.hex()}, 'kernel_stat': raw_stat, 'kernel_status': raw_status,
                'ofd': self.pidfd_ofd(source), 'source': source}
            wait_receipt = {'call': 'waitid', 'args': {'idtype': os.P_PIDFD, 'id': self.pidfd,
                'options': os.WEXITED | os.WNOWAIT}, 'source': source, 'before_reap': before}
            self.frame['terminal'] = {'waitid_receipt': wait_receipt}
            try: waitid = os.waitid(os.P_PIDFD, self.pidfd, os.WEXITED | os.WNOWAIT)
            except OSError as error:
                wait_receipt.update(result=-1, errno=error.errno); raise
            wait_receipt.update(result=0 if waitid is not None else None, errno=0,
                api_result=None if waitid is None else {name: getattr(waitid, name)
                    for name in ('si_pid', 'si_uid', 'si_signo', 'si_status', 'si_code')})
            require(waitid is not None, 'SOURCE_OWNER_ACTUAL_WAITID_UNKNOWN')
            terminal = {'waitid': wait_receipt['api_result'], 'waitid_receipt': wait_receipt,
                        'poll': _poll(self.pidfd), 'wait': None, 'watch_parts': self.watch_parts}
            self.frame['terminal'] = terminal
            self.retain('ACTUAL_WAITID_BEFORE_REAP', terminal)
            reap = os.waitpid(self.child.pid, 0)
            terminal['reap'] = {'call': 'waitpid', 'args': {'pid': self.child.pid, 'options': 0},
                                'api_result': reap, 'result': reap[0], 'errno': 0, 'source': self.lease.check()}
            require(reap[0] == self.child.pid, 'SOURCE_OWNER_ACTUAL_REAP_PID_CHANGED')
            terminal['wait'] = os.waitstatus_to_exitcode(reap[1]); self.child.returncode = terminal['wait']
            terminal['pidfd_current'] = {**fd_identity(self.pidfd), 'fd': self.pidfd}
            terminal['post_reap_ofd'] = self.pidfd_ofd(self.lease.check())
            self.drain_watch(); self.emit_outputs()
            for name, stream in self.streams.items():
                terminal[name] = self.retain_stream(stream, self.lease.check())
                stream['eof'] = terminal[name]['eof']
            self.retain('ACTUAL_TERMINAL', terminal)
        finally: selector.close()

    def complete(self, source, error):
        # The original root helper has already run its genuine finally/check.
        # Every branch owns cleanup, even source failure, read/fsync failure or
        # an acquisition failure after Popen but before pidfd acquisition.
        primary = self.failure or (error if error is not None and type(error) is not SystemExit else None)
        failures = []
        completed = False
        try:
            self.stop_owned_actor(primary)
            partial = {}
            for name, stream in self.streams.items():
                try:
                    partial[name] = self.retain_stream(stream, source)
                    if partial[name]['errors']:
                        failures.append(CoreUnavailable('SOURCE_OWNER_COMPLETE_STREAM_RETENTION_FAILED:' + name))
                except BaseException as failure:
                    partial[name] = {'failure': _error(failure), 'parts': stream['parts'],
                                     'fsync_failure': stream.get('fsync_failure')}
                    failures.append(failure)
            if self.log is not None: self.retain('ALL_STREAM_RETENTION', partial)
            if source is None or primary is not None or failures or self.frame is None:
                if self.log is not None:
                    self.retain('OWNER_FINAL_FAILURE', {'source': source,
                        'error': None if primary is None else _error(primary),
                        'retention_errors': [_error(value) for value in failures],
                        'child_pid': None if self.child is None else self.child.pid,
                        'actual_wait': None if self.child is None else self.child.returncode, 'frame': self.frame})
            else:
                self.frame['owner_final_source'] = source
                require(self.decide('COMPLETE') == 3, 'SOURCE_OWNER_NATIVE_COMPLETION_REFUSED')
                completed = True
        except BaseException as failure:
            failures.append(failure)
            if self.log is not None:
                try: self.retain('OWNER_FINAL_NATIVE_FAILURE', {'error': _error(failure), 'frame': self.frame})
                except BaseException as retention_error: failures.append(retention_error)
        finally:
            for channel_name in ('actor_channel', 'channel'):
                channel = getattr(self, channel_name)
                if channel is None: continue
                try:
                    fd = channel.detach()
                    if fd >= 0: self.fds.append(fd)
                except BaseException as failure:
                    failures.append(failure)
                    try: channel.close()
                    except BaseException as close_error: failures.append(close_error)
                finally: setattr(self, channel_name, None)
            for fd in reversed(tuple(self.fds)):
                if fd in (self.log, self.retention): continue
                try:
                    receipt = close_descriptor(fd, source)
                    self.cleanup_receipts.append(receipt)
                    require(receipt['result'] == 0 and receipt['readback'].get('errno') == 9,
                            'SOURCE_OWNER_ACTUAL_DESCRIPTOR_CLOSE_UNKNOWN')
                except BaseException as failure: failures.append(failure)
                finally: self.fds.remove(fd)
            if self.log is not None:
                try:
                    self.retain('OWNER_CLEANUP', {'closes': self.cleanup_receipts,
                        'stop_wait': self.stop_receipts, 'errors': [_error(value) for value in failures]})
                    if completed and not failures:
                        self.retain('OWNER_ACTOR_COMPLETED', {'frame': self.frame,
                            'native_call': self.last_native_call, 'owner_final_source': source,
                            'cleanup': self.cleanup_receipts, 'stop_wait': self.stop_receipts})
                except BaseException as failure: failures.append(failure)
            # These final actual closes are observed outside the now-closed
            # private archive, on the original root-owner stderr. They never
            # assert child execution or outer scope/collector release.
            final_closes = []
            for fd in (self.log, self.retention):
                if fd is None: continue
                try:
                    receipt = close_descriptor(fd, None)
                    final_closes.append(receipt)
                    require(receipt['result'] == 0 and receipt['readback'].get('errno') == 9,
                            'SOURCE_OWNER_FINAL_RETENTION_CLOSE_UNKNOWN')
                except BaseException as failure: failures.append(failure)
                finally:
                    if fd in self.fds: self.fds.remove(fd)
            self.log = None; self.retention = None
            footer = {'schema': 'worldline.fixed-source-owner-final-close-v1',
                'owner_pid': os.getpid(), 'child_pid': None if self.child is None else self.child.pid,
                'actual_child_wait': None if self.child is None else self.child.returncode,
                'closes': final_closes, 'errors': [_error(value) for value in failures],
                'inner_completed': completed and not failures, 'outer_collector_custody': 'MAIN_REQUIRED'}
            _write(2, b'SOURCE_OWNER_FINAL_CLOSE ' +
                   json.dumps(footer, ensure_ascii=True, separators=(',', ':'), allow_nan=False).encode('ascii') + b'\n')
        if failures:
            if primary is not None:
                for failure in failures: primary.add_note('source-owner final cleanup failed: ' + repr(failure))
            else: raise failures[0]


def run_original_client_owner(lease, approved, request_path, entry):
    return OriginalClientSourceOwner(lease, approved, request_path, entry).launch()
