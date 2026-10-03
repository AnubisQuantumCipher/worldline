"""Bounded private Python evaluator, with candidate execution under a subordinate uid.

This is an execution backend, not an admission decision. The caller supplies frozen input
trees, trusted verifier bytes and an invocation-bound private report directory. Python
examiners may ``import candidate`` and call ``candidate.run(argv, cwd=None, timeout=30)``.
They write their report to /run/worldline-report/report. Only the examiner sees the broker
socket and report mount. Worker copies are disposable and never become candidate payloads.

The initial filesystem contract deliberately accepts only ordinary directories and singly
linked regular files, with ordinary permission bits and no xattrs. Ownership is normalized
in copies; timestamps and permission bits are retained. Links, special files and metadata
outside this contract are refused. Host writers must already have been stopped by the
caller: copying with change detection is not a mechanism for freezing a live source tree.

The script entry points use only stdlib, with -I -S. The bootstrap retains mapping authority
to create sandboxes; all examiner and worker code runs after setpriv drops capabilities and
sets no-new-privileges. Trust includes the host kernel, installed /usr tools and trusted
examiner logic. This module does not attest toolchain packages or provide a proof of isolation.
"""
from __future__ import annotations

import base64
import array
from dataclasses import dataclass
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import runpy
import selectors
import shutil
import signal
import socket
import stat
import struct
import subprocess
import sys
import threading
import time
import types
from typing import Any, Mapping, Sequence
import uuid

if __package__:
    from ..trusted import TRUSTED_INTERPRETER, trusted_script
    from .namespace_lifetime import NamespaceLease, close_role_descriptor, identity_projection, map_rows
else:
    # The engine stages this exact policy beside this helper and mounts it read-only.
    _startup_policy = runpy.run_path(str(Path(__file__).with_name("trusted.py")))
    TRUSTED_INTERPRETER = _startup_policy["TRUSTED_INTERPRETER"]
    trusted_script = _startup_policy["trusted_script"]
    _namespace_policy = runpy.run_path(str(Path(__file__).with_name("namespace_lifetime.py")))
    NamespaceLease = _namespace_policy['NamespaceLease']
    close_role_descriptor = _namespace_policy['close_role_descriptor']
    identity_projection = _namespace_policy['identity_projection']
    map_rows = _namespace_policy['map_rows']

PROFILE_ID = "private-evaluator-v1"
VERIFIER_MOUNT = "/run/worldline-verifiers"
REPORT_MOUNT = "/run/worldline-report"
BROKER_MOUNT = "/run/worldline-broker.sock"
WORKER_BROKER_MOUNT = "/run/worldline-worker-broker.sock"
HELPER_MOUNT = "/run/worldline-evaluator.py"
ROLE_OBSERVER_MOUNT = "/run/worldline-role-observer.sock"
LOADER_POLICY_MOUNT = "/run/worldline-loader-policy.json"
LOADER_HELPER_MOUNT = "/run/worldline-examiner-loader.py"
NATIVE_GUARD_MOUNT = "/run/worldline-examiner-guard.so"
NATIVE_PREPARATION_MOUNT = "/run/worldline-native-preparation.sock"
NATIVE_LIFETIME_MOUNT = "/run/worldline-native-lifetime.sock"
MAX_TREE_BYTES = 268_435_456
MAX_TREE_ENTRIES = 100_000
# The mapped bootstrap handshake is fail-closed, so its window only has to cover a loaded host:
# on 2026-09-28 a bootstrap under a load average near 110 became ready after 19.86 s.
BOOTSTRAP_HANDSHAKE_SECONDS = 60
MAX_OUTPUT_BYTES = 1_048_576
MAX_REQUEST_BYTES = 65_536
MAX_REQUESTS = 32
MAX_CASE_REQUESTS = 50_000
MAX_CASE_LEASES = 256
MAX_CASE_WAIT_MS = 2000
# Only interpreter-determinism variables may be set for candidate processes.
CANDIDATE_ENV_ALLOWED = {"PYTHONHASHSEED": r"[0-9]{1,10}", "PYTHONDONTWRITEBYTECODE": r"1"}
MAX_CASE_STDIN_BYTES = 2048
MAX_WORKER_SECONDS = 120
MAX_EVALUATOR_SECONDS = 600
TOOLCHAIN_MOUNT = "/opt/worldline-gnat"
_ARCH = platform.machine()
_TOOLCHAIN_EXECUTABLES = (
    f"gnat-{_ARCH}-linux-16.1.0-1/bin/gcc",
    f"gprbuild-{_ARCH}-linux-26.0.0-1/bin/gprbuild",
    f"gnatprove-{_ARCH}-linux-16.1.0-1/bin/gnatprove",
    f"gnatprove-{_ARCH}-linux-16.1.0-1/libexec/spark/bin/why3",
    f"gnatprove-{_ARCH}-linux-16.1.0-1/libexec/spark/bin/alt-ergo",
    f"gnatprove-{_ARCH}-linux-16.1.0-1/libexec/spark/bin/cvc5",
    f"gnatprove-{_ARCH}-linux-16.1.0-1/libexec/spark/bin/z3",
)
_DIR_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
_FILE_FLAGS = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK
_RESERVED = ("/usr", "/bin", "/sbin", "/lib", "/lib64", "/etc", "/dev", "/proc", "/run", "/tmp")


class BackendFailure(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _refuse(message: str, code: str = "PRIVATE_EVALUATOR_INVALID") -> None:
    raise BackendFailure(code, message)


def _absolute(value: str) -> str:
    if (not isinstance(value, str) or not value.startswith("/") or "\0" in value
            or str(PurePosixPath(value)) != value or ".." in PurePosixPath(value).parts):
        _refuse("path must be an absolute normalized path")
    return value


def _inside(path: str, parent: str) -> bool:
    return path == parent or path.startswith(parent.rstrip("/") + "/")


def _open_directory(path: Path) -> int:
    _absolute(str(path))
    descriptor = os.open("/", _DIR_FLAGS)
    try:
        for part in path.parts[1:]:
            next_descriptor = os.open(part, _DIR_FLAGS, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = next_descriptor
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def _signature(info: os.stat_result) -> tuple[int, ...]:
    return (info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns, info.st_nlink)


def _entry_object(info):
    # Ancestor timestamps/size/link count may change because of unrelated children.
    return {'device': info.st_dev, 'inode': info.st_ino, 'mode': info.st_mode,
            'uid': info.st_uid, 'gid': info.st_gid}


def _entry_exception(error):
    return {'type': type(error).__module__ + '.' + type(error).__qualname__,
            'message': str(error), 'errno': getattr(error, 'errno', None)}


def _read_examiner_source(path, record):
    """Read actual source through held no-follow objects; never load a bytecode cache.

    The caller owns and retains record, including when this function raises.
    These file observations do not establish global code-execution confinement.
    """
    record.update(path=str(path), directories=[], file=None, bytes=None,
                  readReachedEof=False, readReturned=False, exception=None)
    handles = []
    content = None

    def read():
        nonlocal content
        primary = None
        try:
            normalized = Path(_absolute(str(path)))
            parent = None
            for component in ('/', *normalized.parts[1:-1]):
                descriptor = os.open(component, _DIR_FLAGS, dir_fd=parent)
                row = {'component': component, 'descriptor': descriptor,
                       'before': None, 'after': None, 'edgeAfter': None,
                       'closed': False, 'closeException': None}
                handles.append((descriptor, parent, row))
                record['directories'].append(row)
                row['before'] = _entry_object(os.fstat(descriptor))
                parent = descriptor
            descriptor = os.open(normalized.name, _FILE_FLAGS, dir_fd=parent)
            row = {'component': normalized.name, 'descriptor': descriptor,
                   'before': None, 'after': None, 'edgeAfter': None,
                   'closed': False, 'closeException': None}
            handles.append((descriptor, parent, row))
            record['file'] = row
            content = bytearray()
            before = os.fstat(descriptor)
            row['before'] = list(_signature(before))
            if (not stat.S_ISREG(before.st_mode) or before.st_nlink != 1
                    or before.st_size > MAX_TREE_BYTES):
                _refuse('examiner entry is not bounded singly-linked regular source',
                        'PRIVATE_EXAMINER_ENTRY_INVALID')
            while True:
                chunk = os.read(descriptor, min(65536, MAX_TREE_BYTES - len(content) + 1))
                if not chunk:
                    record['readReachedEof'] = True
                    break
                content.extend(chunk)
                if len(content) > MAX_TREE_BYTES:
                    _refuse('examiner entry exceeds original tree byte bound',
                            'PRIVATE_EXAMINER_ENTRY_INVALID')
            row['after'] = list(_signature(os.fstat(descriptor)))
            row['edgeAfter'] = list(_signature(os.stat(
                normalized.name, dir_fd=parent, follow_symlinks=False)))
            if (row['before'] != row['after'] or row['before'] != row['edgeAfter']
                    or len(content) != before.st_size):
                _refuse('examiner entry changed during source acquisition',
                        'PRIVATE_EXAMINER_ENTRY_INVALID')
            for held, ancestor, directory in handles[:-1]:
                directory['after'] = _entry_object(os.fstat(held))
                if ancestor is not None:
                    directory['edgeAfter'] = _entry_object(os.stat(
                        directory['component'], dir_fd=ancestor, follow_symlinks=False))
                if (directory['after'] != directory['before'] or
                        (ancestor is not None and directory['edgeAfter'] != directory['before'])):
                    _refuse('examiner entry ancestor binding changed',
                            'PRIVATE_EXAMINER_ENTRY_INVALID')
            return bytes(content)
        except BaseException as error:
            primary = error
            raise
        finally:
            cleanup_error = None
            for descriptor, _parent, row in reversed(handles):
                try:
                    os.close(descriptor)
                    row['closed'] = True
                except BaseException as error:
                    row['closeException'] = _entry_exception(error)
                    if primary is not None:
                        primary.add_note('entry descriptor cleanup also failed: ' + str(error))
                    elif cleanup_error is None:
                        cleanup_error = error
                    else:
                        cleanup_error.add_note('another entry descriptor cleanup failed: ' + str(error))
            if cleanup_error is not None:
                raise cleanup_error

    try:
        result = read()
        record['readReturned'] = True
        return result
    except BaseException as error:
        record['exception'] = _entry_exception(error)
        raise
    finally:
        if content is not None:
            record['bytes'] = {'encoding': 'base64',
                               'payload': base64.b64encode(content).decode('ascii')}


def _validate_entry_binding(binding, run_id, path):
    keys = {'schemaVersion', 'runId', 'sourceRecordId', 'path', 'sha256', 'byteCount'}
    if (type(binding) is not dict or set(binding) != keys
            or type(binding['schemaVersion']) is not int or binding['schemaVersion'] != 1
            or type(binding['runId']) is not str or not binding['runId'] or binding['runId'] != run_id
            or type(binding['sourceRecordId']) is not str or not binding['sourceRecordId']
            or type(binding['path']) is not str or binding['path'] != path
            or type(binding['sha256']) is not str or not re.fullmatch('[0-9a-f]{64}', binding['sha256'])
            or type(binding['byteCount']) is not int or not 0 <= binding['byteCount'] <= MAX_TREE_BYTES):
        _refuse('invalid daemon examiner entry binding', 'PRIVATE_EXAMINER_ENTRY_INVALID')
    _absolute(path)
    if not _inside(path, VERIFIER_MOUNT) or path == VERIFIER_MOUNT:
        _refuse('entry binding lies outside verifier mount', 'PRIVATE_EXAMINER_ENTRY_INVALID')
    return dict(binding)


def _validate_native_binding(binding, run_id):
    if (type(binding) is not dict or set(binding) != {
            'schema', 'runId', 'path', 'byteCount', 'sha256', 'sourceRecordId',
            'buildReceiptSha256'}
            or binding['schema'] != 'worldline-examiner-native-v1'
            or type(run_id) is not str or not run_id or binding['runId'] != run_id
            or binding['path'] != NATIVE_GUARD_MOUNT
            or type(binding['byteCount']) is not int
            or not 0 < binding['byteCount'] <= MAX_TREE_BYTES
            or type(binding['sourceRecordId']) is not str or not binding['sourceRecordId']
            or any(type(binding[key]) is not str or not re.fullmatch('[0-9a-f]{64}', binding[key])
                   for key in ('sha256', 'buildReceiptSha256'))):
        _refuse('invalid daemon native artifact binding', 'PRIVATE_EXAMINER_NATIVE_INVALID')
    return dict(binding)


def _role_acknowledgement(receipt, role, payload, run_id, *, require_loader=False,
                          require_native=False):
    keys = {'recordId', 'entrySource'} if role == 'examiner' else {'recordId'}
    if role == 'examiner' and require_loader:
        keys = keys | {'loaderPolicy'}
    if role == 'examiner' and require_native:
        keys = keys | {'nativeGuard'}
    if (type(receipt) is not dict or set(receipt) != keys
            or type(receipt['recordId']) is not str or not receipt['recordId']):
        _refuse('invalid kernel role acknowledgement')
    if role == 'examiner':
        if require_native:
            _validate_native_binding(receipt['nativeGuard'], run_id)
        if require_loader:
            binding = receipt['loaderPolicy']
            if (type(binding) is not dict or set(binding) !=
                    {'schema', 'runId', 'path', 'byteCount', 'sha256'}
                    or binding['schema'] != 'worldline-examiner-loader-v1'
                    or binding['runId'] != run_id or binding['path'] != LOADER_POLICY_MOUNT
                    or type(binding['byteCount']) is not int
                    or not 0 <= binding['byteCount'] <= MAX_TREE_BYTES
                    or type(binding['sha256']) is not str
                    or not re.fullmatch('[0-9a-f]{64}', binding['sha256'])):
                _refuse('invalid daemon examiner loader binding', 'PRIVATE_EXAMINER_LOADER_INVALID')
        return _validate_entry_binding(receipt['entrySource'], run_id, payload[1])
    return None


def _unique_role_fields(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            _refuse('duplicate kernel role response field')
        result[key] = value
    return result


class _RegisteredExaminerCode:
    """Actual compiled identities, held through execution; not a native guard."""
    def __init__(self):
        self._codes = {}

    def contains(self, code):
        retained = self._codes.get(id(code))
        return retained is not None and retained[0] is code

    def compile_entry(self, source, binding):
        if type(binding) is not dict:
            _refuse('invalid daemon examiner entry binding', 'PRIVATE_EXAMINER_ENTRY_INVALID')
        binding = _validate_entry_binding(binding, binding.get('runId'), binding.get('path'))
        if (type(source) is not bytes or len(source) != binding['byteCount']
                or hashlib.sha256(source).hexdigest() != binding['sha256']):
            _refuse('examiner entry bytes differ from daemon binding', 'PRIVATE_EXAMINER_ENTRY_INVALID')
        # Do not inherit this helper's future-annotations flag. Source-declared
        # futures and encoding cookies are interpreted by this exact compile.
        code = compile(source, binding['path'], 'exec', dont_inherit=True)
        return self.register(code, binding)

    def register(self, code, binding):
        if type(code) is not types.CodeType or type(binding) is not dict:
            _refuse('invalid actual compiler result', 'PRIVATE_EXAMINER_LOADER_INVALID')
        pending = [code]
        provenance = tuple(binding.items())
        while pending:
            item = pending.pop()
            if self.contains(item):
                continue
            self._codes[id(item)] = (item, provenance)
            pending.extend(value for value in item.co_consts if type(value) is types.CodeType)
        return code

    def compile_source(self, source, binding):
        if (type(binding) is not dict or binding.get('kind') != 'source'
                or type(binding.get('path')) is not str
                or type(source) is not bytes
                or type(binding.get('byteCount')) is not int
                or len(source) != binding['byteCount']
                or hashlib.sha256(source).hexdigest() != binding.get('sha256')):
            _refuse('import source differs from its byte binding', 'PRIVATE_EXAMINER_LOADER_INVALID')
        _absolute(binding['path'])
        return self.register(compile(source, binding['path'], 'exec', dont_inherit=True), binding)

    def run_main(self, code, path):
        if not self.contains(code) or dict(self._codes[id(code)][1])['path'] != path:
            _refuse('examiner entry code was not registered for this path',
                    'PRIVATE_EXAMINER_ENTRY_INVALID')
        module = types.ModuleType('__main__')
        namespace = module.__dict__
        namespace.update(__name__='__main__', __file__=path, __cached__=None,
                         __doc__=None, __loader__=None, __package__='', __spec__=None)
        absent = object()
        previous = sys.modules.get('__main__', absent)
        argv0 = sys.argv[0]
        sys.modules['__main__'] = module
        try:
            sys.argv[0] = path
            exec(code, namespace)
        finally:
            # Restore the module even if the examiner replaced/emptied argv.
            try:
                sys.argv[0] = argv0
            finally:
                if previous is absent:
                    sys.modules.pop('__main__', None)
                else:
                    sys.modules['__main__'] = previous
        return namespace.copy()


def _prepare_examiner_entry(path, run_id, binding, record, *, registry=None):
    """Own the actual read and compile result without executing the entry."""
    binding = _validate_entry_binding(binding, run_id, path)
    record.update(schemaVersion=1, kind='examiner-entry-preparation', runId=run_id,
                  producer='pre-entry-helper-report', binding=binding, read={},
                  compile={'started': False, 'returned': False, 'exception': None},
                  exception=None)
    try:
        source = _read_examiner_source(Path(path), record['read'])
        registry = _RegisteredExaminerCode() if registry is None else registry
        record['compile']['started'] = True
        try:
            code = registry.compile_entry(source, binding)
        except BaseException as error:
            record['compile']['exception'] = _entry_exception(error)
            raise
        record['compile']['returned'] = True
        return registry, code
    except BaseException as error:
        record['exception'] = _entry_exception(error)
        raise


def _sealed_entry_object(name, content):
    descriptor = os.memfd_create(name, os.MFD_CLOEXEC | os.MFD_ALLOW_SEALING)
    try:
        offset = 0
        while offset < len(content):
            written = os.write(descriptor, memoryview(content)[offset:])
            if written <= 0:
                raise OSError('entry observation object write made no progress')
            offset += written
        required = fcntl.F_SEAL_WRITE | fcntl.F_SEAL_SHRINK | fcntl.F_SEAL_GROW | fcntl.F_SEAL_SEAL
        fcntl.fcntl(descriptor, fcntl.F_ADD_SEALS, required)
        actual = os.fstat(descriptor)
        if (not stat.S_ISREG(actual.st_mode) or actual.st_size != len(content)
                or fcntl.fcntl(descriptor, fcntl.F_GET_SEALS) & required != required):
            _refuse('entry observation object was not completely sealed')
        return descriptor
    except BaseException as error:
        try:
            os.close(descriptor)
        except BaseException as secondary:
            error.add_note('entry object cleanup also failed: ' + str(secondary))
        raise


def _send_entry_preparation(connection, startup_id, binding, record):
    """Transfer complete observations; an ACK acknowledges retention only."""
    metadata = json.loads(json.dumps(record, allow_nan=False))
    source_value = metadata['read'].pop('bytes')
    present = source_value is not None
    if present:
        if type(source_value) is not dict or set(source_value) != {'encoding', 'payload'} or source_value['encoding'] != 'base64':
            _refuse('entry source observation bytes are malformed')
        source = base64.b64decode(source_value['payload'], validate=True)
    else:
        source = b''
    encoded = json.dumps(metadata, allow_nan=False, separators=(',', ':')).encode('utf8')
    if len(encoded) > MAX_TREE_BYTES or len(source) > MAX_TREE_BYTES + 1:
        _refuse('entry observation exceeds its original capture bounds')
    transfer_id = str(uuid.uuid4())
    request = {'schemaVersion': 1, 'operation': 'examiner-entry-prepared',
               'runId': binding['runId'], 'startupRecordId': startup_id,
               'transferId': transfer_id, 'metadataBytes': len(encoded),
               'sourcePresent': present, 'sourceBytes': len(source)}
    packet = json.dumps(request).encode('utf8')
    if len(packet) > MAX_REQUEST_BYTES:
        _refuse('entry observation request exceeds the original packet bound')
    expected = {'schemaVersion': 1, 'operation': 'examiner-entry-retained',
                'runId': binding['runId'], 'startupRecordId': startup_id,
                'transferId': transfer_id, 'entrySource': binding,
                'metadataSha256': hashlib.sha256(encoded).hexdigest(),
                'sourceSha256': hashlib.sha256(source).hexdigest(),
                'sourcePresent': present}
    descriptors = []
    primary = None
    try:
        descriptors.append(_sealed_entry_object('worldline-entry-metadata', encoded))
        descriptors.append(_sealed_entry_object('worldline-entry-source', source))
        if connection.sendmsg([packet], [(socket.SOL_SOCKET, socket.SCM_RIGHTS,
                                         array.array('i', descriptors))]) != len(packet):
            _refuse('entry observation transfer was incomplete')
        # There is exactly one preparation exchange. EOF lets the receiver reject
        # extra packets before acknowledging retention; reads remain available.
        connection.shutdown(socket.SHUT_WR)
        response, ancillary, flags, _address = connection.recvmsg(
            MAX_REQUEST_BYTES + 1, MAX_REQUEST_BYTES, socket.MSG_CMSG_CLOEXEC)
        for level, kind, data in ancillary:
            if level == socket.SOL_SOCKET and kind == socket.SCM_RIGHTS:
                numbers = array.array('i')
                numbers.frombytes(data[:len(data) - len(data) % numbers.itemsize])
                descriptors.extend(numbers)
        if ancillary or flags & ~(socket.MSG_EOR | socket.MSG_CMSG_CLOEXEC) or not response or len(response) > MAX_REQUEST_BYTES:
            _refuse('entry retention acknowledgement is malformed')
        receipt = json.loads(response, object_pairs_hook=_unique_role_fields)
        if (type(receipt) is not dict or set(receipt) != set(expected) | {'recordId'}
                or type(receipt['schemaVersion']) is not int
                or type(receipt['sourcePresent']) is not bool
                or type(receipt['recordId']) is not str or not receipt['recordId']
                or _validate_entry_binding(receipt['entrySource'], binding['runId'], binding['path']) != binding
                or any(receipt[key] != value for key, value in expected.items())):
            _refuse('entry retention acknowledgement differs from this exchange')
        return receipt
    except BaseException as error:
        primary = error
        raise
    finally:
        cleanup = None
        for descriptor in reversed(descriptors):
            try:
                os.close(descriptor)
            except BaseException as error:
                if primary is not None:
                    primary.add_note('entry transfer descriptor cleanup also failed: ' + str(error))
                elif cleanup is None:
                    cleanup = error
                else:
                    cleanup.add_note('entry transfer descriptor cleanup also failed: ' + str(error))
        if cleanup is not None:
            raise cleanup


def _prepare_retained_entry(path, run_id, binding, connection, startup_id, *, registry=None):
    record = {}
    try:
        prepared = _prepare_examiner_entry(path, run_id, binding, record,
            **({} if registry is None else {'registry': registry}))
    except BaseException as error:
        try:
            _send_entry_preparation(connection, startup_id, binding, record)
        except BaseException as secondary:
            error.add_note('entry preparation retention also failed: ' + str(secondary))
        raise
    _send_entry_preparation(connection, startup_id, binding, record)
    return prepared


@contextmanager
def _owned_role_channel():
    connection = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
    primary = None
    try:
        yield connection
    except BaseException as error:
        primary = error
        raise
    finally:
        try:
            connection.close()
        except BaseException as error:
            if primary is None:
                raise
            primary.add_note('role channel cleanup also failed: ' + str(error))


def _run_examiner_entry(path, run_id, binding):
    # Direct utility interface; the actual role uses _prepare_retained_entry.
    registry, code = _prepare_examiner_entry(path, run_id, binding, {})
    # The registry keeps the compiler's actual objects alive until execution ends.
    return registry.run_main(code, path)


class _NativePreparationChannel:
    """Separate full-read retention; never extends the evaluator's deadline."""
    def __init__(self, run_id, startup):
        self.run_id, self.startup = run_id, startup
        self.connection = None
        self.started = time.monotonic()
        self.deadline = self.started + MAX_EVALUATOR_SECONDS
        self.sequence = 0
        self.previous = None
        self.native_status = None

    def _remaining(self):
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            _refuse('native preparation deadline reached', 'PRIVATE_EXAMINER_NATIVE_INVALID')
        self.connection.settimeout(remaining)

    def _send(self, value, descriptors=()):
        self._remaining()
        payload = json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
        if len(payload) > MAX_REQUEST_BYTES:
            _refuse('native preparation packet exceeds original bound')
        ancillary = ([(socket.SOL_SOCKET, socket.SCM_RIGHTS, array.array('i', descriptors))]
                     if descriptors else [])
        if self.connection.sendmsg([payload], ancillary) != len(payload):
            _refuse('native preparation packet was incomplete')

    def _receive(self):
        self._remaining()
        payload, ancillary, flags, _ = self.connection.recvmsg(
            MAX_REQUEST_BYTES + 1, MAX_REQUEST_BYTES, socket.MSG_CMSG_CLOEXEC)
        delivered = []
        primary = None
        try:
            for level, kind, data in ancillary:
                if level == socket.SOL_SOCKET and kind == socket.SCM_RIGHTS:
                    numbers = array.array('i')
                    numbers.frombytes(data[:len(data) - len(data) % numbers.itemsize])
                    delivered.extend(numbers)
            if (ancillary or flags & ~(socket.MSG_EOR | socket.MSG_CMSG_CLOEXEC)
                    or not payload or len(payload) > MAX_REQUEST_BYTES):
                _refuse('native preparation acknowledgement is malformed')
            value = json.loads(payload, object_pairs_hook=_unique_role_fields)
            if type(value) is not dict:
                _refuse('native preparation acknowledgement is not an object')
            return value, hashlib.sha256(payload).hexdigest()
        except BaseException as error:
            primary = error
            raise
        finally:
            failure = None
            for descriptor in reversed(delivered):
                try:
                    os.close(descriptor)
                except BaseException as error:
                    if primary is not None:
                        primary.add_note('unexpected native descriptor cleanup also failed: ' + str(error))
                    elif failure is None:
                        failure = error
                    else:
                        failure.add_note('another unexpected native descriptor cleanup failed: ' + str(error))
            if failure is not None:
                raise failure

    def _context(self):
        return {'schemaVersion': 1, 'runId': self.run_id,
                'startupRecordId': self.startup['recordId']}

    def __enter__(self):
        self.connection = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        try:
            self._remaining()
            self.connection.connect(NATIVE_PREPARATION_MOUNT)
            request = {**self._context(), 'operation': 'native-preparation-open',
                       'nativeGuard': self.startup['nativeGuard'],
                       'loaderPolicy': self.startup['loaderPolicy']}
            self._send(request)
            response, digest = self._receive()
            expected = {**self._context(), 'operation': 'native-preparation-ready',
                        'nativeGuard': self.startup['nativeGuard'],
                        'loaderPolicy': self.startup['loaderPolicy']}
            if (set(response) != set(expected) | {'timeoutSeconds', 'recordId'}
                    or any(response[key] != value for key, value in expected.items())
                    or type(response['schemaVersion']) is not int
                    or type(response['timeoutSeconds']) is not int
                    or not 1 <= response['timeoutSeconds'] <= MAX_EVALUATOR_SECONDS
                    or type(response['recordId']) is not str or not response['recordId']):
                _refuse('native preparation ready response differs from this invocation')
            # This is one sub-deadline; the original controller still enforces
            # its already-running cumulative evaluator deadline.
            self.deadline = self.started + response['timeoutSeconds']
            self.previous = digest
            self._remaining()
            return self
        except BaseException as error:
            try:
                self.connection.close()
            except BaseException as secondary:
                error.add_note('native preparation connect cleanup also failed: ' + str(secondary))
            raise

    def retain_read(self, kind, selector, read):
        metadata = dict(read)
        encoded_source = metadata.pop('bytes')
        present = encoded_source is not None
        if present:
            if (type(encoded_source) is not dict or set(encoded_source) != {'encoding', 'payload'}
                    or encoded_source['encoding'] != 'base64'):
                _refuse('native preparation source bytes are malformed')
            source = base64.b64decode(encoded_source['payload'], validate=True)
        else:
            source = b''
        encoded = json.dumps(metadata, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
        if len(encoded) > MAX_TREE_BYTES or len(source) > MAX_TREE_BYTES + 1:
            _refuse('native preparation object exceeds its original read bound')
        transfer = str(uuid.uuid4())
        request = {**self._context(), 'operation': 'native-preparation-read',
                   'sequence': self.sequence, 'previousReceiptSha256': self.previous,
                   'kind': kind, 'selector': selector, 'transferId': transfer,
                   'metadataBytes': len(encoded), 'sourcePresent': present,
                   'sourceBytes': len(source)}
        expected = {**self._context(), 'operation': 'native-preparation-retained',
                    'sequence': self.sequence, 'previousReceiptSha256': self.previous,
                    'kind': kind, 'selector': selector, 'transferId': transfer,
                    'metadataSha256': hashlib.sha256(encoded).hexdigest(),
                    'sourcePresent': present, 'sourceSha256': hashlib.sha256(source).hexdigest()}
        descriptors, primary = [], None
        try:
            descriptors.append(_sealed_entry_object('worldline-native-metadata', encoded))
            descriptors.append(_sealed_entry_object('worldline-native-source', source))
            self._send(request, descriptors)
            response, digest = self._receive()
            if (set(response) != set(expected) | {'recordId'}
                    or type(response['schemaVersion']) is not int
                    or type(response['sequence']) is not int
                    or type(response['sourcePresent']) is not bool
                    or type(response['recordId']) is not str or not response['recordId']
                    or any(response[key] != value for key, value in expected.items())):
                _refuse('native preparation read acknowledgement differs')
            self.previous = digest
            self.sequence += 1
        except BaseException as error:
            primary = error
            raise
        finally:
            failure = None
            for descriptor in reversed(descriptors):
                try:
                    os.close(descriptor)
                except BaseException as error:
                    if primary is not None:
                        primary.add_note('native preparation descriptor cleanup also failed: ' + str(error))
                    elif failure is None:
                        failure = error
                    else:
                        failure.add_note('another native preparation descriptor cleanup failed: ' + str(error))
            if failure is not None:
                raise failure

    def __exit__(self, kind, primary, traceback):
        failure = None
        try:
            state = None if self.native_status is None else self.native_status()
            request = {**self._context(), 'operation': 'native-preparation-terminal',
                       'sequence': self.sequence, 'previousReceiptSha256': self.previous,
                       'exception': None if primary is None else _entry_exception(primary),
                       'nativeStatus': state}
            self._send(request)
            self.connection.shutdown(socket.SHUT_WR)
            response, _digest = self._receive()
            expected = {**self._context(), 'operation': 'native-preparation-complete',
                        'sequence': self.sequence, 'previousReceiptSha256': self.previous,
                        'failed': primary is not None}
            if (set(response) != set(expected) | {'recordId'}
                    or type(response['schemaVersion']) is not int
                    or type(response['sequence']) is not int or type(response['failed']) is not bool
                    or type(response['recordId']) is not str or not response['recordId']
                    or any(response[key] != value for key, value in expected.items())):
                _refuse('native preparation terminal acknowledgement differs')
        except BaseException as error:
            failure = error
        finally:
            try:
                self.connection.close()
            except BaseException as error:
                if failure is None:
                    failure = error
                else:
                    failure.add_note('native preparation channel cleanup also failed: ' + str(error))
        if failure is not None:
            if primary is None:
                raise failure
            primary.add_note('native preparation retention also failed: ' + str(failure))
        return False


class _NativeExaminerCode(_RegisteredExaminerCode):
    """Live native operations; Python provenance metadata cannot register code."""
    _GENERATORS = ('collections.namedtuple',
                   'dataclasses._FuncBuilder.add_fns_to_class', 'ast.parse')

    def __init__(self, run_id, startup):
        super().__init__()
        self.run_id, self.startup = run_id, startup
        self.guard = None
        self.sources = {}
        self.loader_support = None
        self.loader_policy = None
        self.generators_bound = False

    @staticmethod
    def _acquire(channel, kind, binding):
        read, primary = {}, None
        try:
            content = _read_examiner_source(Path(binding['path']), read)
            if (type(binding['byteCount']) is not int or len(content) != binding['byteCount']
                    or hashlib.sha256(content).hexdigest() != binding['sha256']):
                _refuse('native source acquisition differs from daemon binding',
                        'PRIVATE_EXAMINER_NATIVE_INVALID')
            return content
        except BaseException as error:
            primary = error
            raise
        finally:
            try:
                channel.retain_read(kind, binding['path'], read)
            except BaseException as error:
                if primary is None:
                    raise
                primary.add_note('native source read retention also failed: ' + str(error))

    def compile_entry(self, source, binding):
        binding = _validate_entry_binding(binding, self.run_id, binding.get('path'))
        if (type(source) is not bytes or len(source) != binding['byteCount']
                or hashlib.sha256(source).hexdigest() != binding['sha256']):
            _refuse('native entry differs from daemon binding', 'PRIVATE_EXAMINER_ENTRY_INVALID')
        with _NativePreparationChannel(self.run_id, self.startup) as channel:
            policy_bytes = self._acquire(channel, 'policy', self.startup['loaderPolicy'])
            envelope = json.loads(policy_bytes, object_pairs_hook=_unique_role_fields)
            if type(envelope) is not dict or type(envelope.get('support')) is not dict:
                _refuse('native loader support binding is absent', 'PRIVATE_EXAMINER_LOADER_INVALID')
            support = envelope['support']
            if (set(support) != {'path', 'byteCount', 'sha256', 'sourceRecordId'}
                    or support['path'] != LOADER_HELPER_MOUNT
                    or type(support['byteCount']) is not int
                    or not 0 <= support['byteCount'] <= MAX_TREE_BYTES
                    or type(support['sha256']) is not str
                    or not re.fullmatch('[0-9a-f]{64}', support['sha256'])
                    or type(support['sourceRecordId']) is not str or not support['sourceRecordId']):
                _refuse('native loader support binding is invalid', 'PRIVATE_EXAMINER_LOADER_INVALID')
            support_bytes = self._acquire(channel, 'support', support)
            # This is the fixed byte-bound bootstrap decoder, before native
            # configuration. It is never mislabeled as registered workload code.
            namespace = {'__name__': '_worldline_loader_support', '__file__': LOADER_HELPER_MOUNT,
                         '__package__': '', '__spec__': None}
            exec(compile(support_bytes, LOADER_HELPER_MOUNT, 'exec', dont_inherit=True), namespace)
            policy = namespace['decode_policy'](policy_bytes, self.startup['loaderPolicy'], binding,
                maximum_bytes=MAX_TREE_BYTES, maximum_entries=MAX_TREE_ENTRIES)
            native = _validate_native_binding(policy.get('nativeGuard'), self.run_id)
            if native != self.startup['nativeGuard']:
                _refuse('native policy binding differs from observed role', 'PRIVATE_EXAMINER_NATIVE_INVALID')
            self._acquire(channel, 'artifact', native)
            # Only the preinstalled builtin is eligible: a same-named source
            # module on a verifier search path cannot be a fallback.
            machinery, utilities = namespace['importlib'].machinery, namespace['importlib'].util
            spec = machinery.BuiltinImporter.find_spec('_worldline_examiner_guard')
            if spec is None or spec.origin != 'built-in':
                _refuse('preinitialized native examiner guard is absent', 'PRIVATE_EXAMINER_NATIVE_INVALID')
            guard = utilities.module_from_spec(spec)
            spec.loader.exec_module(guard)
            sys.modules['_worldline_examiner_guard'] = guard
            self.guard, channel.native_status = guard, guard.status
            initial = guard.status()
            if (initial['phase'] != 'bootstrap' or not initial['preinitializationInstalled']
                    or initial['violated']):
                _refuse('native examiner guard is not in clean bootstrap', 'PRIVATE_EXAMINER_NATIVE_INVALID')
            self.sources = {binding['path']: source, support['path']: support_bytes}
            for item in policy['files']:
                if item['kind'] == 'source' and item['path'] != binding['path']:
                    self.sources[item['path']] = self._acquire(channel, 'source', item)
            self._attach_lifetime(channel, guard)
            guard.configure(self.run_id, tuple(self.sources.items()))
            for label in self._GENERATORS:
                guard.bind_cached_generator(label)
            self.generators_bound = True
            code = guard.compile_source(binding['path'])
            self._codes[id(code)] = (code, tuple(binding.items()))
            self.loader_support, self.loader_policy = namespace, policy
            return code

    def _attach_lifetime(self, preparation, guard):
        # Dedicated connection: preparation and entry still close under their
        # original protocols. Native code alone owns the duplicated lifetime fd.
        transport = _NativePreparationChannel(self.run_id, self.startup)
        transport.deadline = preparation.deadline
        with _owned_role_channel() as connection:
            transport.connection = connection
            transport._remaining()
            connection.connect(NATIVE_LIFETIME_MOUNT)
            ready, _digest = transport._receive()
            expected = {**transport._context(), 'operation': 'native-lifetime-ready',
                        'nativeGuard': self.startup['nativeGuard']}
            if (set(ready) != set(expected) | {'recordId', 'deadlineNs'}
                    or type(ready['schemaVersion']) is not int
                    or any(ready[key] != value for key, value in expected.items())
                    or type(ready['recordId']) is not str or not ready['recordId']
                    or type(ready['deadlineNs']) is not int
                    or not time.monotonic_ns() < ready['deadlineNs']
                        <= int(preparation.deadline * 1_000_000_000)):
                _refuse('native lifetime ready does not join the running invocation')
            native = self.startup['nativeGuard']
            context = (self.run_id, self.startup['recordId'],
                tuple(native[key] for key in ('schema', 'runId', 'path', 'byteCount',
                                              'sha256', 'sourceRecordId', 'buildReceiptSha256')),
                ready['recordId'], ready['deadlineNs'])
            guard.attach_lifetime(connection.fileno(), context, ready['deadlineNs'])
        if guard.status()['nativeLifetime']['attached'] is not True:
            _refuse('live native lifetime stream was not attached')

    def contains(self, code):
        return self.guard is not None and self.guard.contains(code)

    def register(self, code, binding):
        _refuse('Python cannot register native examiner code', 'PRIVATE_EXAMINER_NATIVE_INVALID')

    def compile_source(self, source, binding):
        if (type(binding) is not dict or binding.get('kind') != 'source'
                or type(binding.get('path')) is not str or type(source) is not bytes
                or type(binding.get('byteCount')) is not int
                or len(source) != binding['byteCount']
                or hashlib.sha256(source).hexdigest() != binding.get('sha256')
                or self.sources.get(binding['path']) != source):
            _refuse('import differs from configured native source', 'PRIVATE_EXAMINER_NATIVE_INVALID')
        return self.guard.compile_source(binding['path'])

    def acquire_frozen(self, fullname):
        return self.guard.frozen_code(fullname)

    def frozen_metadata(self, fullname):
        return self.guard.frozen_metadata(fullname)

    def bind_native_generators(self):
        state = self.guard.status()
        if (not self.generators_bound or state['phase'] != 'configured' or state['violated']
                or state['cachedBindingReturns'] != len(self._GENERATORS)):
            _refuse('native generator preparation is incomplete', 'PRIVATE_EXAMINER_NATIVE_INVALID')

    def activate(self):
        self.guard.activate()


def copy_frozen_tree(source: Path, destination: Path) -> str:
    """Descriptor-relative bounded copy. Refuse links, mounts, xattrs and changing entries.

    Return a digest of paths, kinds, modes and regular-file bytes. It is a backend input
    identity, not WORLDLINE's candidate root identity. The destination must not exist.
    """
    source_fd = _open_directory(source)
    records: list[dict[str, Any]] = []
    budget = {"bytes": 0, "entries": 0}
    source_device = os.fstat(source_fd).st_dev

    def copy_entry(src: int, dst: Path, relative: str, depth: int) -> None:
        before = os.fstat(src)
        budget["entries"] += 1
        if budget["entries"] > MAX_TREE_ENTRIES or depth > 128:
            _refuse("input tree exceeds entry/depth limit", "PRIVATE_TREE_LIMIT")
        if before.st_dev != source_device or before.st_mode & 0o7000:
            _refuse("mounted filesystem or special permission bits in input", "PRIVATE_TREE_UNSUPPORTED")
        if os.listxattr(src):
            _refuse("extended attributes are outside the private evaluator tree contract", "PRIVATE_TREE_UNSUPPORTED")
        mode = stat.S_IMODE(before.st_mode)
        if stat.S_ISDIR(before.st_mode):
            dst.mkdir(mode=0o700)
            names = sorted(os.listdir(src))
            for name in names:
                info = os.stat(name, dir_fd=src, follow_symlinks=False)
                if not (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)):
                    _refuse("input contains a link or special object", "PRIVATE_TREE_UNSUPPORTED")
                descriptor = os.open(name, _DIR_FLAGS if stat.S_ISDIR(info.st_mode) else _FILE_FLAGS,
                                     dir_fd=src)
                try:
                    if _signature(info) != _signature(os.fstat(descriptor)):
                        _refuse("input changed while opening", "PRIVATE_TREE_CHANGED")
                    copy_entry(descriptor, dst / name, relative + "/" + name, depth + 1)
                finally:
                    os.close(descriptor)
            records.append({"path": relative, "kind": "directory", "mode": mode})
        elif stat.S_ISREG(before.st_mode) and before.st_nlink == 1:
            budget["bytes"] += before.st_size
            if budget["bytes"] > MAX_TREE_BYTES:
                _refuse("input tree exceeds byte limit", "PRIVATE_TREE_LIMIT")
            digest = hashlib.sha256()
            count = 0
            with dst.open("xb") as output:
                while True:
                    chunk = os.read(src, 65536)
                    if not chunk:
                        break
                    count += len(chunk)
                    if count > before.st_size:
                        _refuse("input grew during copying", "PRIVATE_TREE_CHANGED")
                    digest.update(chunk)
                    output.write(chunk)
            if count != before.st_size:
                _refuse("input size changed during copying", "PRIVATE_TREE_CHANGED")
            records.append({"path": relative, "kind": "file", "mode": mode,
                            "sha256": digest.hexdigest()})
        else:
            _refuse("input is not an ordinary singly linked file", "PRIVATE_TREE_UNSUPPORTED")
        if _signature(before) != _signature(os.fstat(src)):
            _refuse("input changed during copying", "PRIVATE_TREE_CHANGED")
        os.chmod(dst, mode, follow_symlinks=False)
        os.utime(dst, ns=(before.st_atime_ns, before.st_mtime_ns), follow_symlinks=False)

    try:
        if destination == source or source in destination.parents:
            _refuse("copy destination is inside source")
        copy_entry(source_fd, destination, ".", 0)
    finally:
        os.close(source_fd)
    return hashlib.sha256(json.dumps(records, sort_keys=True, ensure_ascii=True).encode()).hexdigest()


@dataclass(frozen=True)
class PrivateEvaluationSpec:
    run_id: str
    roots: Mapping[str, Path]
    verifier_directory: Path
    argv: tuple[str, ...]
    cwd: str
    report_directory: Path
    runtime: Path
    timeout_seconds: int = MAX_EVALUATOR_SECONDS
    bubblewrap_executable: Path | None = None
    # Independently supplied held-descriptor identities, never a clean flag.
    verifier_digests: Mapping[str, str] | None = None


def _validate_spec(spec: PrivateEvaluationSpec) -> None:
    if (not spec.roots or len(spec.roots) > 16 or isinstance(spec.timeout_seconds, bool)
            or not isinstance(spec.timeout_seconds, int)
            or not 1 <= spec.timeout_seconds <= MAX_EVALUATOR_SECONDS):
        _refuse("invalid roots or evaluator timeout")
    targets = list(spec.roots)
    for target in targets:
        _absolute(target)
        if target == "/" or any(_inside(target, p) or _inside(p, target) for p in (*_RESERVED, TOOLCHAIN_MOUNT)):
            _refuse("candidate target overlaps evaluator/system mounts")
        if any(target != other and (_inside(target, other) or _inside(other, target)) for other in targets):
            _refuse("candidate targets overlap")
    _absolute(spec.cwd)
    if not any(_inside(spec.cwd, target) for target in targets):
        _refuse("examiner cwd is outside candidate roots")
    if (len(spec.argv) < 2 or spec.argv[0] != TRUSTED_INTERPRETER
            or not all(isinstance(v, str) and "\0" not in v for v in spec.argv)):
        _refuse("private evaluator requires /usr/bin/python3 followed by a staged script")
    script = _absolute(spec.argv[1])
    if not _inside(script, VERIFIER_MOUNT) or script == VERIFIER_MOUNT:
        _refuse("examiner script is outside the trusted verifier mount")
    for directory in (spec.report_directory, spec.runtime.parent):
        descriptor = _open_directory(directory)
        try:
            info = os.fstat(descriptor)
            if info.st_uid != os.getuid() or info.st_mode & 0o077:
                _refuse("report/runtime parent must be owned by the daemon and owner-only")
        finally:
            os.close(descriptor)
    for directory in (*spec.roots.values(), spec.verifier_directory):
        if directory == spec.runtime or directory in spec.runtime.parents:
            _refuse("backend runtime must be outside input trees")


def _bubblewrap_identity(requested: Path | None) -> dict[str, str]:
    selected = str(requested) if requested is not None else shutil.which("bwrap")
    if not selected:
        _refuse("bubblewrap is unavailable for private roles", "PRIVATE_EVALUATOR_UNAVAILABLE")
    try:
        path = Path(selected).resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        _refuse(f"bubblewrap executable cannot be resolved: {exc}", "PRIVATE_EVALUATOR_INVALID")
    info = path.stat()
    if (not path.is_absolute() or not stat.S_ISREG(info.st_mode)
            or info.st_uid not in (0, os.getuid()) or info.st_mode & 0o7022
            or not os.access(path, os.X_OK)):
        _refuse("bubblewrap executable is not an approved regular file", "PRIVATE_EVALUATOR_INVALID")
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    return {"path": str(path), "sha256": digest}


class _PrivateAcquisitions:
    """Invocation-local observations, never report or boundary admission."""
    def __init__(self, spec, process, observer):
        self.spec = spec
        self.process = process
        self.observer = observer
        self.next_occurrence = 0

    def _start(self, kind, site):
        occurrence = self.next_occurrence
        self.next_occurrence += 1
        return (lambda record: self.observer(kind, occurrence, record)), {
            'schemaVersion': 1, 'runId': self.spec.run_id,
            'unit': self.process.unit, 'site': site,
            'occurrence': occurrence,
        }

    def communicate(self, timeout, *, site):
        from ..raw_observation import (
            optional_bytes, retain_observation, exception_observation,
        )
        observe, details = self._start('private-communicate-acquisition', site)
        try:
            stdout, stderr = self.process.launcher.communicate(timeout=timeout)
        except BaseException as primary:
            # Available exception output is distinct from an actual return.
            # Preserve this primary even if the retention callback also fails.
            try:
                retain_observation(observe, {
                    **details, 'communicateReturned': False,
                    'stdout': optional_bytes(getattr(primary, 'output', None)),
                    'stderr': optional_bytes(getattr(primary, 'stderr', None)),
                    'launcherReturncode': self.process.launcher.returncode,
                    'exception': exception_observation(primary),
                })
            except BaseException as secondary:
                primary.add_note('available private communication retention also failed: ' +
                                 type(secondary).__qualname__ + ': ' + str(secondary))
                primary._worldline_retention_failed = True
            raise
        # This callback precedes supervision, parsing and the resource-guard exit.
        retain_observation(observe, {
            **details, 'communicateReturned': True,
            'stdout': optional_bytes(stdout), 'stderr': optional_bytes(stderr),
            'launcherReturncode': self.process.launcher.returncode,
            'exception': None,
        })
        return stdout, stderr

    def cleanup_communicate(self, timeout, *, site):
        from ..raw_observation import retention_failed
        primary = sys.exception()
        try:
            return self.communicate(timeout, site=site)
        except BaseException as secondary:
            if primary is None:
                raise
            primary.add_note('private communication cleanup also failed: ' +
                             type(secondary).__qualname__ + ': ' + str(secondary))
            if retention_failed(secondary):
                primary._worldline_retention_failed = True

    def boundary_bytes(self, path):
        from ..raw_observation import (
            optional_bytes, retain_observation, exception_observation, cleanup_call,
        )
        observe, details = self._start('private-boundary-acquisition', 'boundary-read')
        details['pathBytes'] = optional_bytes(os.fsencode(path))
        stream = None
        content = None
        try:
            try:
                stream = path.open('rb')
                content = bytearray()
                while True:
                    chunk = stream.read(65536)
                    if not chunk:
                        break
                    content.extend(chunk)
            except BaseException as primary:
                try:
                    retain_observation(observe, {
                        **details, 'readReturned': False, 'readReachedEof': False,
                        'bytes': optional_bytes(content),
                        'exception': exception_observation(primary),
                    })
                except BaseException as secondary:
                    primary.add_note('available private boundary retention also failed: ' +
                                     type(secondary).__qualname__ + ': ' + str(secondary))
                    primary._worldline_retention_failed = True
                raise
            # Retain the original file bytes before any text decoding or JSON use.
            payload = bytes(content)
            retain_observation(observe, {
                **details, 'readReturned': True, 'readReachedEof': True,
                'bytes': optional_bytes(payload), 'exception': None,
            })
            return payload
        finally:
            if stream is not None:
                cleanup_call(stream.close)


def _write_loader_artifact(path, content, record):
    """Own the new artifact stream, preserving a write primary across cleanup."""
    record.update(openReturned=False, writeReturned=False, writeCount=None,
                  writeException=None, closeAttempted=False, closeReturned=False,
                  closeException=None, chmodReturned=False)
    stream, primary = None, None
    try:
        stream = path.open('xb')
        record['openReturned'] = True
        record['writeCount'] = stream.write(content)
        record['writeReturned'] = True
        if record['writeCount'] != len(content):
            _refuse('loader artifact write was incomplete', 'PRIVATE_EXAMINER_LOADER_INVALID')
    except BaseException as error:
        primary = error
        record['writeException'] = _entry_exception(error)
        raise
    finally:
        if stream is not None:
            record['closeAttempted'] = True
            try:
                stream.close()
                record['closeReturned'] = True
            except BaseException as error:
                record['closeException'] = _entry_exception(error)
                if primary is None:
                    raise
                primary.add_note('loader artifact close also failed: ' + str(error))
    path.chmod(0o444)
    record['chmodReturned'] = True


class PrivateEvaluator:
    def __init__(self, systemd: Any):
        self.systemd = systemd

    @staticmethod
    def _native_artifact(spec, observer):
        """Acquire daemon-selected build bytes; the launch controls bind the build."""
        from ..raw_observation import retain_observation
        package = Path(__file__).resolve().parents[3]
        installed = (package / 'libworldline_core.so').is_file()
        artifact = (package / 'libworldline_examiner_guard.so' if installed else
                    package.parent / 'native-artifacts/libworldline_examiner_guard.so')
        receipt = (package / 'native-build.json' if installed else artifact.parent / 'build.json')
        record = {'schemaVersion': 1, 'kind': 'examiner-native-artifact',
                  'runId': spec.run_id, 'recordId': str(uuid.uuid4()),
                  'selection': 'installed-package' if installed else 'reviewed-development-frame',
                  'artifactRead': {}, 'buildReceiptRead': {}, 'buildReceipt': None,
                  'binding': None, 'readback': {}, 'exception': None, 'returned': False}
        primary = None
        try:
            content = _read_examiner_source(artifact, record['artifactRead'])
            receipt_bytes = _read_examiner_source(receipt, record['buildReceiptRead'])
            for read in (record['artifactRead'], record['buildReceiptRead']):
                info = read['file']['before']
                if info[3] not in (0, os.geteuid()) or info[2] & 0o7022:
                    _refuse('native build input ownership or mode differs', 'PRIVATE_EXAMINER_NATIVE_INVALID')
            build = json.loads(receipt_bytes, object_pairs_hook=_unique_role_fields)
            record['buildReceipt'] = build
            if (type(build) is not dict or set(build) != {
                    'artifact', 'bytes', 'sha256', 'compilerReturncode',
                    'confinementAcceptance', 'phaseAcceptance'}
                    or type(build['artifact']) is not str
                    or not Path(build['artifact']).is_absolute()
                    or (not installed and build['artifact'] != str(artifact))
                    or type(build['bytes']) is not int or build['bytes'] != len(content)
                    or type(build['compilerReturncode']) is not int or build['compilerReturncode'] != 0
                    or build['sha256'] != hashlib.sha256(content).hexdigest()
                    or build['confinementAcceptance'] is not False or build['phaseAcceptance'] is not False):
                _refuse('native bytes differ from build metadata', 'PRIVATE_EXAMINER_NATIVE_INVALID')
            binding = _validate_native_binding({
                'schema': 'worldline-examiner-native-v1', 'runId': spec.run_id,
                'path': NATIVE_GUARD_MOUNT, 'byteCount': len(content),
                'sha256': hashlib.sha256(content).hexdigest(),
                'sourceRecordId': record['recordId'],
                'buildReceiptSha256': hashlib.sha256(receipt_bytes).hexdigest()}, spec.run_id)
            record['binding'] = binding
            copied = spec.runtime / 'examiner-guard.so'
            _write_loader_artifact(copied, content, record)
            if _read_examiner_source(copied, record['readback']) != content:
                _refuse('native artifact copy differs', 'PRIVATE_EXAMINER_NATIVE_INVALID')
            record['returned'] = True
            return str(copied), binding, record
        except BaseException as error:
            primary = error
            record['exception'] = _entry_exception(error)
            error.examiner_native_observations = [record]
            raise
        finally:
            if observer is not None:
                try:
                    retain_observation(lambda value: observer(
                        'private-examiner-native-artifact', 0, value), record)
                except BaseException as error:
                    if primary is None:
                        error.examiner_native_observations = [record]
                        raise
                    primary.add_note('native artifact retention also failed: ' + str(error))
                    primary._worldline_retention_failed = True

    @staticmethod
    def _audit_copy(spec, phase, observer):
        from ..examiner_audit import audit
        entry = str(PurePosixPath(spec.argv[1]).relative_to(VERIFIER_MOUNT))
        observation = audit(spec.runtime / "verifiers", entry, spec.verifier_digests)
        if observer is not None:
            from ..raw_observation import retain_observation
            retain_observation(lambda record: observer(
                'private-examiner-audit', phase, record), observation)
        return observation

    @staticmethod
    def _entry_source(spec, observer):
        from ..raw_observation import retain_observation
        entry = str(PurePosixPath(spec.argv[1]).relative_to(VERIFIER_MOUNT))
        observation = {'schemaVersion': 1, 'kind': 'examiner-entry-source',
                       'runId': spec.run_id, 'recordId': str(uuid.uuid4()),
                       'producer': 'daemon-source-reader', 'logicalPath': spec.argv[1],
                       'binding': None}

        def retain():
            if observer is not None:
                retain_observation(lambda record: observer(
                    'private-examiner-entry-source', 0, record), observation)

        try:
            source = _read_examiner_source(spec.runtime / 'verifiers' / entry, observation)
            binding = _validate_entry_binding({
                'schemaVersion': 1, 'runId': spec.run_id,
                'sourceRecordId': observation['recordId'], 'path': spec.argv[1],
                'sha256': hashlib.sha256(source).hexdigest(), 'byteCount': len(source),
            }, spec.run_id, spec.argv[1])
            observation['binding'] = binding
        except BaseException as primary:
            observation['exception'] = _entry_exception(primary)
            primary.examiner_entry_observation = observation
            try:
                retain()
            except BaseException as secondary:
                primary.add_note('examiner entry source retention also failed: ' + str(secondary))
                primary._worldline_retention_failed = True
            raise
        try:
            retain()
        except BaseException as error:
            error.examiner_entry_observation = observation
            raise
        return binding, observation

    @staticmethod
    def _loader_policy(spec, entry_binding, observer, *, native_guard=None):
        from .examiner_loader import capture_policy, SCHEMA, validate_binding
        from ..raw_observation import retain_observation

        def retain(index, observation):
            if observer is not None:
                retain_observation(lambda record: observer(
                    'private-examiner-loader-source', index, record), observation)

        policy, observations = capture_policy(
            spec.runtime / 'verifiers', spec.run_id, entry_binding, _read_examiner_source,
            maximum_bytes=MAX_TREE_BYTES, maximum_entries=MAX_TREE_ENTRIES, retain=retain)
        if native_guard is not None:
            policy['nativeGuard'] = _validate_native_binding(native_guard, spec.run_id)
        support_record = {'schemaVersion': 1, 'kind': 'examiner-loader-support',
                          'runId': spec.run_id, 'recordId': str(uuid.uuid4()),
                          'read': {}, 'exception': None, 'binding': None,
                          'writeReturned': False}
        support_primary = None
        try:
            support_bytes = _read_examiner_source(
                Path(__file__).with_name('examiner_loader.py'), support_record['read'])
            policy['support'] = {
                'path': LOADER_HELPER_MOUNT, 'byteCount': len(support_bytes),
                'sha256': hashlib.sha256(support_bytes).hexdigest(),
                'sourceRecordId': support_record['recordId']}
            support_record['binding'] = policy['support']
            _write_loader_artifact(spec.runtime / 'examiner_loader.py', support_bytes, support_record)
        except BaseException as error:
            support_primary = error
            support_record['exception'] = _entry_exception(error)
            error.examiner_loader_observations = [*observations, support_record]
            raise
        finally:
            observations.append(support_record)
            if observer is not None:
                try:
                    retain_observation(lambda record: observer(
                        'private-examiner-loader-support', 0, record), support_record)
                except BaseException as error:
                    if support_primary is None:
                        error.examiner_loader_observations = observations
                        raise
                    support_primary.add_note('loader support retention also failed: ' + str(error))
                    support_primary._worldline_retention_failed = True
        path = spec.runtime / 'loader-policy.json'
        record = {'schemaVersion': 1, 'kind': 'examiner-loader-policy', 'runId': spec.run_id,
                  'binding': None, 'serializationReturned': False,
                  'writeReturned': False, 'readback': {}, 'exception': None}
        primary = None
        try:
            content = json.dumps(policy, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')
            record['serializationReturned'] = True
            binding = validate_binding({
                'schema': SCHEMA, 'runId': spec.run_id, 'path': LOADER_POLICY_MOUNT,
                'sha256': hashlib.sha256(content).hexdigest(), 'byteCount': len(content)},
                spec.run_id, maximum_bytes=MAX_TREE_BYTES)
            record['binding'] = binding
            _write_loader_artifact(path, content, record)
            readback = _read_examiner_source(path, record['readback'])
            if readback != content:
                _refuse('loader policy readback differed', 'PRIVATE_EXAMINER_LOADER_INVALID')
        except BaseException as error:
            primary = error
            record['exception'] = _entry_exception(error)
            error.examiner_loader_observations = [*observations, record]
            raise
        finally:
            observations.append(record)
            if observer is not None:
                try:
                    retain_observation(lambda observation: observer(
                        'private-examiner-loader-policy', 0, observation), record)
                except BaseException as error:
                    if primary is None:
                        error.examiner_loader_observations = observations
                        raise
                    primary.add_note('loader policy retention also failed: ' + str(error))
                    primary._worldline_retention_failed = True
        return str(path), binding, observations

    def run(self, spec: PrivateEvaluationSpec, *, resource_properties: Sequence[str] = (), _supervision_observer=None, _acquisition_observer=None) -> dict[str, Any]:
        """Run a trusted Python examiner. Never interpret or admit its report here."""
        from ..errors import WorldlineError
        try:
            return self._run(spec, resource_properties, **({} if _supervision_observer is None else {'_supervision_observer': _supervision_observer}),
                **({} if _acquisition_observer is None else {'_acquisition_observer': _acquisition_observer}))
        except (BackendFailure, OSError, ValueError, ImportError) as exc:
            if _supervision_observer is not None or _acquisition_observer is not None:
                from ..raw_observation import retention_failed
                if retention_failed(exc): raise
            details = {}
            if hasattr(exc, 'kernel_role_observations'):
                details['kernelRoleObservations'] = exc.kernel_role_observations
            if hasattr(exc, 'examiner_entry_observation'):
                details['examinerEntrySource'] = exc.examiner_entry_observation
            if hasattr(exc, 'examiner_loader_observations'):
                details['examinerLoaderObservations'] = exc.examiner_loader_observations
            if hasattr(exc, 'examiner_native_observations'):
                details['examinerNativeObservations'] = exc.examiner_native_observations
            raise WorldlineError(getattr(exc, "code", "PRIVATE_EVALUATOR_FAILED"), str(exc), details) from exc

    def _run(self, spec: PrivateEvaluationSpec, resource_properties: Sequence[str], *, _supervision_observer=None, _acquisition_observer=None) -> dict[str, Any]:
        _validate_spec(spec)
        bubblewrap = _bubblewrap_identity(spec.bubblewrap_executable)
        spec.runtime.mkdir(mode=0o700)
        (spec.runtime / "frozen").mkdir(mode=0o700)
        (spec.runtime / "workers").mkdir(mode=0o700)
        roots = []
        for index, (target, source) in enumerate(sorted(spec.roots.items())):
            frozen = spec.runtime / "frozen" / str(index)
            identity = copy_frozen_tree(source, frozen)
            roots.append({"target": target, "frozen": str(frozen), "identity": identity})
        verifier = spec.runtime / "verifiers"
        verifier_identity = copy_frozen_tree(spec.verifier_directory, verifier)
        # Audit the second copy actually mounted for the examiner, against the
        # identities the caller read from its original held descriptors.
        audit_before = self._audit_copy(spec, 'before', _acquisition_observer)
        entry_binding, entry_observation = self._entry_source(spec, _acquisition_observer)
        loader_observations = None
        native_observation = None
        try:
            native_path, native_binding, native_observation = self._native_artifact(
                spec, _acquisition_observer)
            loader_path, loader_binding, loader_observations = self._loader_policy(
                spec, entry_binding, _acquisition_observer, native_guard=native_binding)
            from .examiner_loader import decode_policy
            loader_policy = decode_policy(
                base64.b64decode(loader_observations[-1]['readback']['bytes']['payload'], validate=True),
                loader_binding, entry_binding, maximum_bytes=MAX_TREE_BYTES,
                maximum_entries=MAX_TREE_ENTRIES)
            helper = spec.runtime / "helper.py"
            helper.write_bytes(Path(__file__).read_bytes())
            helper.chmod(0o444)
            case_copier = spec.runtime / "case-copy.py"
            case_copier.write_bytes(Path(__file__).with_name("private_case_copy.py").read_bytes())
            case_copier.chmod(0o444)
            startup_policy = spec.runtime / "trusted.py"
            startup_policy.write_bytes(Path(__file__).parents[1].joinpath("trusted.py").read_bytes())
            startup_policy.chmod(0o444)
            namespace_policy = spec.runtime / "namespace_lifetime.py"
            namespace_policy.write_bytes(Path(__file__).with_name("namespace_lifetime.py").read_bytes())
            namespace_policy.chmod(0o444)
            loader_helper = spec.runtime / 'examiner_loader.py'
            daemon_namespace = os.stat('/proc/self/ns/user')
            plan = {"profileId": PROFILE_ID, "runId": spec.run_id, "roots": roots,
                    "bubblewrap": bubblewrap,
                    "verifier": str(verifier), "verifierIdentity": verifier_identity,
                    "examinerEntryBinding": entry_binding,
                    "examinerLoaderBinding": loader_binding, "loaderPolicy": loader_path,
                    "nativeGuard": native_path, "nativeGuardBinding": native_binding,
                    "nativeSourceRoster": [
                        {'kind': 'policy', 'binding': loader_binding},
                        {'kind': 'support', 'binding': loader_policy['support']},
                        {'kind': 'artifact', 'binding': native_binding},
                        *({'kind': 'source', 'binding': row} for row in loader_policy['files']
                          if row['kind'] == 'source' and row['path'] != entry_binding['path'])],
                    "loaderHelper": str(loader_helper),
                    "loaderHelperSha256": hashlib.sha256(loader_helper.read_bytes()).hexdigest(),
                    "argv": list(spec.argv), "cwd": spec.cwd, "runtime": str(spec.runtime),
                    "report": str(spec.report_directory), "helper": str(helper),
                    "caseCopier": str(case_copier),
                    "caseCopierSha256": hashlib.sha256(case_copier.read_bytes()).hexdigest(),
                    "startupPolicy": str(startup_policy),
                    "namespacePolicy": str(namespace_policy),
                    "namespacePolicySha256": hashlib.sha256(namespace_policy.read_bytes()).hexdigest(),
                    "daemonUserNamespace": {"device": daemon_namespace.st_dev,
                                            "inode": daemon_namespace.st_ino,
                                            "mode": daemon_namespace.st_mode},
                    "maximumOutputBytes": MAX_OUTPUT_BYTES,
                    "bootstrapSha256": hashlib.sha256(helper.read_bytes()).hexdigest(),
                    "startupPolicySha256": hashlib.sha256(startup_policy.read_bytes()).hexdigest(),
                    "timeout": spec.timeout_seconds, "operatorUid": os.getuid(), "operatorGid": os.getgid()}
            # Fixed operator installations on the reference host and the hosted assurance runner.
            # The candidate and project policy cannot supply this path.
            toolchain = next((root for root in (Path.home() / "opt" / "gnat", Path.home() / "gnat")
                              if root.is_dir() and (root / _TOOLCHAIN_EXECUTABLES[2]).is_file()), None)
            if toolchain is not None:
                descriptor = _open_directory(toolchain)
                os.close(descriptor)
                identities = {}
                for relative in _TOOLCHAIN_EXECUTABLES:
                    path = toolchain / relative
                    if path.is_file():
                        with path.open("rb") as stream:
                            identities[relative] = hashlib.file_digest(stream, "sha256").hexdigest()
                plan["toolchain"] = {"source": str(toolchain), "target": TOOLCHAIN_MOUNT,
                                     "executables": identities,
                                     "identityScope": "listed executable bytes; not a complete installation attestation"}
            from .kernel_role_observer import KernelRoleObserver
            with KernelRoleObserver(plan, maximum_bytes=MAX_TREE_BYTES,
                                    maximum_request=MAX_REQUEST_BYTES,
                                    handshake_seconds=BOOTSTRAP_HANDSHAKE_SECONDS,
                                    observer=_acquisition_observer) as role_observer:
                plan['roleObservationSocket'] = role_observer.path
                result = self._launch_and_collect(
                    spec, plan, resource_properties, role_observer, audit_before,
                    _supervision_observer=_supervision_observer,
                    _acquisition_observer=_acquisition_observer)
                result['boundary']['daemonExaminerEntrySource'] = entry_observation
                result['boundary']['daemonExaminerLoaderObservations'] = loader_observations
                result['boundary']['daemonExaminerNativeObservations'] = [native_observation]
                return result
        except BaseException as error:
            error.examiner_entry_observation = entry_observation
            if loader_observations is not None:
                error.examiner_loader_observations = loader_observations
            if native_observation is not None:
                error.examiner_native_observations = [native_observation]
            raise

    def _launch_and_collect(self, spec, plan, resource_properties, role_observer, audit_before,
                            *, _supervision_observer=None, _acquisition_observer=None):
        helper = Path(plan['helper'])
        plan['bootstrapDeadlineMonotonic'] = time.monotonic() + BOOTSTRAP_HANDSHAKE_SECONDS
        plan_path = spec.runtime / "plan.json"
        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        plan_path.chmod(0o600)
        process = self.systemd.launch_private_evaluator(
            spec.run_id, plan_path, helper, resource_properties=resource_properties)
        if _acquisition_observer is not None:
            return self._collect_observed(spec, process, _acquisition_observer,
                                          _supervision_observer=_supervision_observer,
                                          _audit_before=audit_before,
                                          _role_observer=role_observer)
        try:
            deadline = role_observer.plan['bootstrapDeadlineMonotonic']
            while not (spec.runtime / "bootstrap-ready").exists():
                if process.launcher.poll() is not None or time.monotonic() >= deadline:
                    _refuse("mapped bootstrap did not become ready", "PRIVATE_EVALUATOR_UNAVAILABLE")
                time.sleep(0.02)
            unit_properties = self.systemd._show(process.unit, ("NoNewPrivileges", "MainPID", "ControlGroup"))
            if not unit_properties or unit_properties.get("NoNewPrivileges") != "no":
                _refuse("manager did not confirm mapping bootstrap NoNewPrivileges=no")
            role_observer.arm(unit_properties)
            (spec.runtime / "bootstrap-go").write_text("GO\n")
            stdout, stderr = process.launcher.communicate(timeout=spec.timeout_seconds + 20)
        except subprocess.TimeoutExpired:
            self.systemd.stop(process.unit)
            process.launcher.communicate(timeout=20)
            _refuse("supervised private evaluator exceeded its deadline", "PRIVATE_EVALUATOR_TIMEOUT")
        except BaseException:
            self.systemd.stop(process.unit)
            process.launcher.communicate(timeout=20)
            raise
        supervision = self.systemd.outcome(process, process.launcher.returncode,
            **({} if _supervision_observer is None else {'_raw_observer': _supervision_observer}))
        evidence_path = spec.runtime / "boundary.json"
        if not evidence_path.is_file():
            _refuse("private bootstrap produced no boundary evidence: " + stderr.decode("utf-8", "replace")[-2000:],
                    "PRIVATE_EVALUATOR_UNAVAILABLE")
        boundary = json.loads(evidence_path.read_text(encoding="utf-8"))
        if boundary.get("error"):
            _refuse(str(boundary["error"]), "PRIVATE_EVALUATOR_BOUNDARY_FAILED")
        boundary["managerBootstrapProperties"] = unit_properties
        boundary["bootstrapExitCode"] = process.launcher.returncode
        boundary['daemonRoleObservations'] = role_observer.finish(boundary)
        return {"profileId": PROFILE_ID, "stdout": stdout, "stderr": stderr,
                "exitCode": process.launcher.returncode, "supervision": supervision,
                "boundary": boundary, "reportDirectory": spec.report_directory,
                "examinerAudit": {"before": audit_before,
                                  "after": self._audit_copy(spec, 'after', None),
                                  "mount": VERIFIER_MOUNT}}

    def _collect_observed(self, spec, process, observer, *, _supervision_observer=None,
                          _audit_before=None, _role_observer=None):
        from ..raw_observation import cleanup_call, retention_failed
        acquisition = _PrivateAcquisitions(spec, process, observer)
        try:
            # Direct acquisition-only callers retain their original interface.
            # Every real _run launch supplies its cumulative observer deadline.
            deadline = (time.monotonic() + BOOTSTRAP_HANDSHAKE_SECONDS if _role_observer is None
                        else _role_observer.plan['bootstrapDeadlineMonotonic'])
            while not (spec.runtime / "bootstrap-ready").exists():
                if process.launcher.poll() is not None or time.monotonic() >= deadline:
                    _refuse("mapped bootstrap did not become ready", "PRIVATE_EVALUATOR_UNAVAILABLE")
                time.sleep(0.02)
            unit_properties = self.systemd._show(process.unit, ("NoNewPrivileges", "MainPID", "ControlGroup"))
            if not unit_properties or unit_properties.get("NoNewPrivileges") != "no":
                _refuse("manager did not confirm mapping bootstrap NoNewPrivileges=no")
            if _role_observer is not None:
                _role_observer.arm(unit_properties)
            (spec.runtime / "bootstrap-go").write_text("GO\n")
            stdout, stderr = acquisition.communicate(spec.timeout_seconds + 20,
                                                     site='examiner-wait')
        except subprocess.TimeoutExpired as primary:
            cleanup_call(lambda: self.systemd.stop(process.unit))
            acquisition.cleanup_communicate(20, site='timeout-cleanup')
            if retention_failed(primary):
                raise
            _refuse("supervised private evaluator exceeded its deadline", "PRIVATE_EVALUATOR_TIMEOUT")
        except BaseException:
            cleanup_call(lambda: self.systemd.stop(process.unit))
            acquisition.cleanup_communicate(20, site='exception-cleanup')
            raise
        supervision = self.systemd.outcome(process, process.launcher.returncode,
            **({} if _supervision_observer is None else {'_raw_observer': _supervision_observer}))
        evidence_path = spec.runtime / "boundary.json"
        if not evidence_path.is_file():
            _refuse("private bootstrap produced no boundary evidence: " + stderr.decode("utf-8", "replace")[-2000:],
                    "PRIVATE_EVALUATOR_UNAVAILABLE")
        payload = acquisition.boundary_bytes(evidence_path)
        # Match Path.read_text's UTF-8 and universal-newline behavior while
        # decoding only the owned, already retained bytes.
        import io
        with io.TextIOWrapper(io.BytesIO(payload), encoding='utf-8') as text_stream:
            boundary = json.loads(text_stream.read())
        if boundary.get("error"):
            _refuse(str(boundary["error"]), "PRIVATE_EVALUATOR_BOUNDARY_FAILED")
        boundary["managerBootstrapProperties"] = unit_properties
        boundary["bootstrapExitCode"] = process.launcher.returncode
        if _role_observer is not None:
            boundary['daemonRoleObservations'] = _role_observer.finish(boundary)
        return {"profileId": PROFILE_ID, "stdout": stdout, "stderr": stderr,
                "exitCode": process.launcher.returncode, "supervision": supervision,
                "boundary": boundary, "reportDirectory": spec.report_directory,
                "examinerAudit": {"before": _audit_before,
                                  # Acquisition-only callers do not own a verifier
                                  # audit lifecycle. Every real _run supplies before.
                                  "after": (None if _audit_before is None else
                                            self._audit_copy(spec, 'after', observer)),
                                  "mount": VERIFIER_MOUNT}}


def _observations(role: str) -> dict[str, Any]:
    status = {}
    for line in Path("/proc/self/status").read_text().splitlines():
        key, _, value = line.partition(":")
        if key in ("Uid", "Gid", "Groups", "NoNewPrivs", "CapEff", "CapPrm", "CapBnd", "CapAmb"):
            status[key] = value.strip()
    return {"role": role, "uid": os.getuid(), "gid": os.getgid(), "status": status,
            "uidMap": Path("/proc/self/uid_map").read_text(),
            "gidMap": Path("/proc/self/gid_map").read_text(),
            "namespaces": {name: os.readlink("/proc/self/ns/" + name) for name in ("pid", "mnt", "user", "net")},
            "reportMounted": os.path.isdir(REPORT_MOUNT),
            "brokerMounted": os.path.exists(BROKER_MOUNT),
            "workerBrokerMounted": os.path.exists(WORKER_BROKER_MOUNT),
            "toolchainMounted": os.path.isdir(TOOLCHAIN_MOUNT)}


def _validate_observation(observation: Mapping[str, Any], role: str) -> None:
    expected = {"examiner": 0, "worker": 1, "candidate": 2}.get(role)
    if expected is None:
        _refuse("unknown private role", "PRIVATE_ROLE_INVALID")
    status = observation.get("status", {})
    if (observation.get("role") != role or observation.get("uid") != expected
            or observation.get("gid") != expected or status.get("NoNewPrivs") != "1"
            or status.get("Uid", "").split() != [str(expected)] * 4
            or status.get("Gid", "").split() != [str(expected)] * 4
            or any(int(status.get(key, "1"), 16) != 0 for key in ("CapEff", "CapPrm", "CapBnd", "CapAmb"))
            or status.get("Groups") != ""
            or observation.get("reportMounted") != (role == "examiner")
            or observation.get("brokerMounted") != (role == "examiner")
            or observation.get("workerBrokerMounted") != (role == "worker")):
        _refuse("role privilege or mount observation differs from required boundary", "PRIVATE_ROLE_INVALID")


def _mapped_identity(mapping: str, identity: int) -> int:
    rows = [tuple(map(int, row.split())) for row in mapping.splitlines()]
    matches = [host + identity - start for start, host, count in rows if start <= identity < start + count]
    if len(matches) != 1:
        _refuse("UID/GID map does not uniquely map the required identity")
    return matches[0]


def _sandbox(plan: Mapping[str, Any], role: str, roots: Sequence[Mapping[str, Any]],
             payload: Sequence[str], cwd: str,
             case_bind: Mapping[str, str] | None = None,
             environment: Mapping[str, str] | None = None) -> list[str]:
    # Join the complete mapped child; its disposable parent forbids further user namespaces.
    command = [plan["bubblewrap"]["path"], "--userns", str(plan['roleNamespaceFd']),
               "--assert-userns-disabled", "--unshare-pid", "--unshare-ipc", "--unshare-uts", "--unshare-net",
               "--die-with-parent", "--new-session", "--clearenv", "--setenv", "PATH", "/usr/bin",
               "--setenv", "HOME", "/tmp", "--ro-bind", "/usr", "/usr", "--ro-bind", "/etc", "/etc"]
    if environment:
        if role != "candidate":
            _refuse("environment overrides are restricted to candidate role")
        for key, value in sorted(environment.items()):
            command.extend(("--setenv", key, value))
    for path in ("/bin", "/sbin", "/lib", "/lib64"):
        if Path(path).is_symlink():
            command.extend(("--symlink", os.readlink(path), path))
        elif Path(path).exists():
            command.extend(("--ro-bind", path, path))
    command.extend(("--dev", "/dev", "--proc", "/proc", "--tmpfs", "/tmp", "--tmpfs", "/run",
                    "--ro-bind", plan["helper"], HELPER_MOUNT,
                    "--ro-bind", plan["startupPolicy"], "/run/trusted.py",
                    "--ro-bind", plan["namespacePolicy"], "/run/namespace_lifetime.py",
                    "--ro-bind", plan["roleObservationSocket"], ROLE_OBSERVER_MOUNT))
    # bwrap's implicitly created ancestors can be owner-only. The worker needs traversal
    # through these empty mountpoint scaffolds, without changing any source-tree mode bits.
    ancestors = sorted({str(parent) for root in roots for parent in Path(root["target"]).parents
                        if str(parent) != "/"}, key=lambda value: (len(Path(value).parts), value))
    for ancestor in ancestors:
        command.extend(("--dir", ancestor, "--chmod", "0755", ancestor))
    for root in roots:
        command.extend(("--ro-bind" if role == "examiner" else "--bind", root["source"], root["target"]))
    if case_bind is not None:
        if role != "candidate":
            _refuse("case mount is restricted to candidate role")
        command.extend(("--bind", case_bind["source"], case_bind["target"]))
    if role == "examiner":
        command.extend(("--ro-bind", plan["verifier"], VERIFIER_MOUNT,
                        "--bind", plan["report"], REPORT_MOUNT,
                        "--bind", plan["socket"], BROKER_MOUNT))
        if 'loaderPolicy' in plan:
            command.extend(('--ro-bind', plan['loaderPolicy'], LOADER_POLICY_MOUNT,
                            '--ro-bind', plan['loaderHelper'], LOADER_HELPER_MOUNT))
        if 'nativeGuard' in plan:
            command.extend(('--ro-bind', plan['nativeGuard'], NATIVE_GUARD_MOUNT,
                            '--ro-bind', plan['nativePreparationSocket'], NATIVE_PREPARATION_MOUNT,
                            '--ro-bind', plan['nativeLifetimeSocket'], NATIVE_LIFETIME_MOUNT))
        if plan.get("toolchain"):
            command.extend(("--ro-bind", plan["toolchain"]["source"], TOOLCHAIN_MOUNT))
    elif role == "worker":
        command.extend(("--bind", plan["workerSocket"], WORKER_BROKER_MOUNT))
    uid = {"examiner": "0", "worker": "1", "candidate": "2"}[role]
    native_environment = (('/usr/bin/env', 'LD_PRELOAD=' + NATIVE_GUARD_MOUNT)
                          if role == 'examiner' and 'nativeGuard' in plan else ())
    command.extend(("--chdir", cwd, "--", "/usr/bin/setpriv", "--no-new-privs", "--reuid", uid,
                    "--regid", uid, "--clear-groups", "--bounding-set=-all", "--inh-caps=-all",
                    "--ambient-caps=-all", "--", *native_environment, *trusted_script(HELPER_MOUNT,
                    "--role", role, json.dumps(list(payload)), plan['runId'],
                    str(plan['roleNamespaceFd']))))
    return command


def _retain_native_role_deadline(plan, observation, deadline):
    """Retain the actual already-running supervisor deadline before original GO."""
    transport = _NativePreparationChannel(plan['runId'],
                                          {'recordId': observation['kernelObservationId']})
    transport.deadline = deadline
    socket_path = Path(plan['nativeLifetimeSocket'])
    directory = _open_directory(socket_path.parent)
    primary = None
    try:
        with _owned_role_channel() as connection:
            transport.connection = connection
            transport._remaining()
            # Like the daemon's bind, address the socket through a held parent.
            # Runtime paths may exceed AF_UNIX's address limit even though they
            # are valid filesystem paths. Keep cwd and the actual endpoint intact.
            connection.connect('/proc/self/fd/' + str(directory) + '/' + socket_path.name)
            request = {**transport._context(), 'operation': 'native-lifetime-budget',
                       'deadlineNs': int(deadline * 1_000_000_000)}
            transport._send(request)
            connection.shutdown(socket.SHUT_WR)
            response, _digest = transport._receive()
            expected = {**request, 'operation': 'native-lifetime-budget-retained'}
            if (set(response) != set(expected) | {'recordId'}
                    or type(response['schemaVersion']) is not int
                    or type(response['deadlineNs']) is not int
                    or type(response['recordId']) is not str or not response['recordId']
                    or any(response[key] != value for key, value in expected.items())):
                _refuse('native lifetime budget receipt differs from actual role deadline')
    except BaseException as error:
        primary = error
        raise
    finally:
        try:
            os.close(directory)
        except BaseException as error:
            if primary is None:
                raise
            primary.add_note('native lifetime socket directory cleanup also failed: ' + str(error))


def _run_role(command: Sequence[str], role: str, timeout: int, *,
              namespace_lease: Any,
              on_process: Any = None, on_observed: Any = None,
              on_output: Any = None, stdin_bytes: bytes | None = None,
              native_lifetime_plan: Any = None) -> dict[str, Any]:
    """Consume only the fixed helper's startup frame, then permit workload execution.

    Workload bytes after the handshake are data, never observations. Both streams and the
    startup deadline are bounded. No report descriptor or broker socket is inherited.
    """
    started = time.monotonic_ns()
    process = namespace_lease.spawn_role(command, deadline=time.monotonic() + timeout,
                                         stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE, start_new_session=True)
    if on_process is not None:
        on_process(process)
    output = {"stdout": bytearray(), "stderr": bytearray()}
    observation = None
    deadline = time.monotonic() + timeout
    selector = selectors.DefaultSelector()
    assert process.stdout is not None and process.stderr is not None and process.stdin is not None
    selector.register(process.stdout, selectors.EVENT_READ, "stdout")
    selector.register(process.stderr, selectors.EVENT_READ, "stderr")
    try:
        while selector.get_map():
            if time.monotonic() >= deadline:
                _refuse(role + " exceeded its deadline", "PRIVATE_EVALUATOR_TIMEOUT")
            for key, _ in selector.select(timeout=0.1):
                chunk = os.read(key.fileobj.fileno(), 65536)
                if not chunk:
                    selector.unregister(key.fileobj)
                    continue
                output[key.data].extend(chunk)
                if len(output[key.data]) > MAX_OUTPUT_BYTES:
                    _refuse(role + " exceeded output limit", "PRIVATE_EVALUATOR_OUTPUT_LIMIT")
                if key.data == "stdout" and observation is None and b"\n" in output["stdout"]:
                    frame, _, rest = output["stdout"].partition(b"\n")
                    if len(frame) > MAX_REQUEST_BYTES or rest:
                        _refuse("invalid helper startup frame")
                    observation = json.loads(frame)
                    _validate_observation(observation, role)
                    if on_observed is not None:
                        on_observed(observation)
                    if native_lifetime_plan is not None:
                        if role != 'examiner':
                            _refuse('native lifetime budget is examiner-only')
                        _retain_native_role_deadline(native_lifetime_plan, observation, deadline)
                    output["stdout"].clear()
                    process.stdin.write(b"GO\n")
                    if stdin_bytes:
                        if role != "candidate" or len(stdin_bytes) > MAX_CASE_STDIN_BYTES:
                            _refuse("candidate stdin exceeds the bounded case contract")
                        process.stdin.write(stdin_bytes)
                    process.stdin.close()
                    process.stdin = None
                elif observation is not None and on_output is not None:
                    on_output(key.data, chunk)
        process.wait(timeout=max(0.1, deadline - time.monotonic()))
        if observation is None:
            _refuse(role + " did not establish its boundary: " + output["stderr"].decode("utf-8", "replace"),
                    "PRIVATE_EVALUATOR_UNAVAILABLE")
        return {"returncode": process.returncode, "stdout": bytes(output["stdout"]),
                "stderr": bytes(output["stderr"]), "observation": observation,
                "duration_ns": time.monotonic_ns() - started}
    finally:
        selector.close()
        if process.poll() is None:
            process.kill()
        try:
            process.wait(timeout=10)
        finally:
            for stream in (process.stdin, process.stdout, process.stderr):
                if stream is not None:
                    stream.close()


def _request(value: Any, roots: Sequence[Mapping[str, Any]], default_cwd: str) -> tuple[list[str], str, int, str]:
    if (not isinstance(value, dict) or
            set(value) not in ({"argv", "cwd", "timeout"},
                               {"argv", "cwd", "timeout", "principal"})):
        _refuse("candidate.run accepts only argv, cwd and timeout")
    principal = value.get("principal", "worker")
    if principal not in ("worker", "candidate"):
        _refuse("unknown candidate process principal")
    argv, cwd, timeout = value["argv"], value["cwd"], value["timeout"]
    if (not isinstance(argv, list) or not argv or len(argv) > 256
            or not all(isinstance(v, str) and "\0" not in v and len(v) <= 8192 for v in argv)):
        _refuse("invalid worker argv")
    executable = _absolute(argv[0])
    if not any(_inside(executable, root["target"]) for root in roots) and not any(
            _inside(executable, prefix) for prefix in ("/usr/bin", "/bin")):
        _refuse("worker executable is outside system binaries/candidate roots")
    cwd = default_cwd if cwd is None else _absolute(cwd)
    if not any(_inside(cwd, root["target"]) for root in roots):
        _refuse("worker cwd is outside candidate roots")
    if isinstance(timeout, bool) or not isinstance(timeout, int) or not 1 <= timeout <= MAX_WORKER_SECONDS:
        _refuse("invalid worker timeout")
    return argv, cwd, timeout, principal


def _read_message(connection: socket.socket, maximum: int) -> Any:
    chunks = bytearray()
    while b"\n" not in chunks:
        chunk = connection.recv(min(65536, maximum + 1 - len(chunks)))
        if not chunk:
            _refuse("incomplete broker message")
        chunks.extend(chunk)
        if len(chunks) > maximum:
            _refuse("broker message exceeds limit")
    frame, _, rest = chunks.partition(b"\n")
    if rest:
        _refuse("trailing broker message bytes")
    return json.loads(frame)


def _own_tree(directory: Path, uid: int) -> None:
    # Called only on newly copied, validated trees before any worker exists.
    for parent, directories, files in os.walk(directory, followlinks=False):
        for name in directories:
            path = Path(parent) / name
            if path.is_symlink():
                os.chown(path, uid, uid, follow_symlinks=False)
        for name in files:
            os.chown(Path(parent) / name, uid, uid, follow_symlinks=False)
        os.chown(parent, uid, uid, follow_symlinks=False)


def _reclaim_tree(directory: Path) -> None:
    """Restore operator ownership after the worker's namespace has exited; never follow links."""
    def visit(descriptor: int) -> None:
        os.fchown(descriptor, 0, 0)
        os.fchmod(descriptor, stat.S_IMODE(os.fstat(descriptor).st_mode) | 0o700)
        for name in os.listdir(descriptor):
            info = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
            if stat.S_ISDIR(info.st_mode):
                child = os.open(name, _DIR_FLAGS, dir_fd=descriptor)
                try:
                    visit(child)
                finally:
                    os.close(child)
            else:
                os.chown(name, 0, 0, dir_fd=descriptor, follow_symlinks=False)
    descriptor = _open_directory(directory)
    try:
        visit(descriptor)
    finally:
        os.close(descriptor)


def _bootstrap(plan_path: str) -> int:
    plan = json.loads(Path(plan_path).read_text())
    runtime = Path(plan["runtime"])
    evidence: dict[str, Any] = {"profileId": PROFILE_ID, "runId": plan["runId"],
                              "bootstrapSha256": plan["bootstrapSha256"], "workers": [],
                              "startupPolicySha256": plan["startupPolicySha256"],
                              "inputs": plan["roots"], "verifierIdentity": plan["verifierIdentity"],
                              "toolchain": plan.get("toolchain"),
                              "bubblewrap": plan.get("bubblewrap"),
                              "nonClaims": ["Role isolation does not establish examiner logic correctness.",
                                            "Kernel, system tools and trusted examiner are part of the trust base.",
                                            "Namespace restriction alone does not establish complete confinement."]}
    namespace_lease = None
    stop = threading.Event()
    errors: list[str] = []
    socket_path = runtime / "broker.sock"
    worker_socket_path = runtime / "worker-broker.sock"
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    worker_server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        if os.getuid() != 0 or os.getgid() != 0:
            _refuse("bootstrap did not enter its mapped root identity")
        executable = plan.get("bubblewrap")
        if (not isinstance(executable, dict) or not isinstance(executable.get("path"), str)
                or not isinstance(executable.get("sha256"), str)):
            _refuse("bubblewrap executable identity is absent")
        with Path(executable["path"]).open("rb") as stream:
            if hashlib.file_digest(stream, "sha256").hexdigest() != executable["sha256"]:
                _refuse("bubblewrap executable changed before private roles ran")
        case_copier = Path(plan["caseCopier"])
        if hashlib.sha256(case_copier.read_bytes()).hexdigest() != plan["caseCopierSha256"]:
            _refuse("scoped case copier changed before private roles ran")
        copy_case_tree = runpy.run_path(str(case_copier))["copy_case_tree"]
        namespace_policy = Path(plan['namespacePolicy'])
        if hashlib.sha256(namespace_policy.read_bytes()).hexdigest() != plan['namespacePolicySha256']:
            _refuse('namespace restriction policy changed before bootstrap setup')
        evidence["bootstrap"] = _observations("bootstrap")
        for name, expected in (("uidMap", plan["operatorUid"]), ("gidMap", plan["operatorGid"])):
            mapping = evidence["bootstrap"][name]
            if (_mapped_identity(mapping, 0) != expected
                    or _mapped_identity(mapping, 1) in (0, expected)
                    or _mapped_identity(mapping, 2) in (0, expected, _mapped_identity(mapping, 1))):
                _refuse("subordinate UID/GID mapping is unavailable")
        namespace_lease = NamespaceLease(
            argv=trusted_script(str(namespace_policy)), run_id=plan['runId'],
            expected_parent=plan['daemonUserNamespace'],
            deadline=plan['bootstrapDeadlineMonotonic'], maximum=MAX_TREE_BYTES,
            maximum_request=MAX_REQUEST_BYTES, maximum_output=MAX_OUTPUT_BYTES)
        evidence['namespaceLifetimeSetup'] = namespace_lease.record
        plan['roleNamespaceFd'] = namespace_lease.create()
        (runtime / 'namespace-ready.json').write_text(json.dumps({
            'schemaVersion': 1, 'runId': plan['runId'], 'descriptor': plan['roleNamespaceFd'],
            'setup': namespace_lease.record}), encoding='utf-8')
        (runtime / "bootstrap-ready").write_text("ready\n")
        deadline = plan['bootstrapDeadlineMonotonic']
        while not (runtime / "bootstrap-go").exists():
            if time.monotonic() >= deadline:
                _refuse("daemon did not acknowledge bootstrap manager properties")
            time.sleep(0.02)
        # A relative bind avoids AF_UNIX's pathname-length limit for deep runtime directories.
        os.chdir(runtime)
        server.bind("broker.sock")
        socket_path.chmod(0o600)
        server.listen(1)
        server.settimeout(0.1)
        plan["socket"] = str(socket_path)
        worker_server.bind("worker-broker.sock")
        os.chown(worker_socket_path, 0, 1)
        worker_socket_path.chmod(0o660)
        worker_server.listen(1)
        worker_server.settimeout(0.1)
        plan["workerSocket"] = str(worker_socket_path)
        sessions: dict[str, dict[str, Any]] = {}
        sessions_lock = threading.Lock()
        active_worker = threading.Event()
        active_worker_roots: dict[str, Any] = {"roots": []}
        cases: dict[str, dict[str, Any]] = {}
        opened_cases = {"count": 0}
        evidence["workerBrokerCalls"] = []
        evidence["caseLeases"] = []

        def copied_roots(call_number: int | str, principal: str) -> tuple[Path, list[dict[str, str]]]:
            work = runtime / "workers" / str(call_number)
            work.mkdir(mode=0o700)
            roots = []
            for index, root in enumerate(plan["roots"]):
                copy = work / str(index)
                digest = copy_frozen_tree(Path(root["frozen"]), copy)
                if digest != root["identity"]:
                    _refuse("frozen worker input identity changed")
                _own_tree(copy, 1 if principal == "worker" else 2)
                roots.append({"source": str(copy), "target": root["target"]})
            return work, roots

        def case_by_handle(value: Any) -> dict[str, Any]:
            if not isinstance(value, str) or value not in cases:
                _refuse("unknown scoped case lease")
            return cases[value]

        def remove_private_tree(path: Path) -> None:
            if path.exists():
                _reclaim_tree(path)
                shutil.rmtree(path)

        def worker_generation(case: Mapping[str, Any]) -> dict[str, Any]:
            scratch = case["work"] / ("guard-" + uuid.uuid4().hex)
            try:
                return copy_case_tree(case["workerPath"], scratch,
                                      logical_root=case["logicalRoot"])
            finally:
                remove_private_tree(scratch)

        def require_worker_generation(case: Mapping[str, Any]) -> None:
            observed = worker_generation(case)
            if observed != case["generation"]:
                _refuse("worker case view changed without a scoped copy-in")

        def open_case(request: Mapping[str, Any], peer_pid: int) -> dict[str, Any]:
            if set(request) != {"op", "caseRoot"}:
                _refuse("scoped case open has wrong shape")
            logical = _absolute(request["caseRoot"])
            selected = None
            relative = None
            for root in active_worker_roots["roots"]:
                if logical != root["target"] and _inside(logical, root["target"]):
                    selected = root
                    relative = Path(logical).relative_to(root["target"])
                    break
            if selected is None or relative is None or not relative.parts:
                _refuse("scoped case root is not strictly inside the active worker copy")
            if len(cases) >= MAX_CASE_LEASES or opened_cases["count"] >= MAX_CASE_LEASES:
                _refuse("scoped case lease limit reached")
            worker_path = Path(selected["source"]) / relative
            info = os.lstat(worker_path)
            if not stat.S_ISDIR(info.st_mode):
                _refuse("scoped case root is not a real directory in the worker copy")
            for item in cases.values():
                if (_inside(logical, item["logicalRoot"]) or _inside(item["logicalRoot"], logical)):
                    _refuse("scoped case root overlaps an active lease")
            opened_cases["count"] += 1
            handle = uuid.uuid4().hex
            work, roots = copied_roots("case-" + handle, "candidate")
            view = work / "candidate-view"
            try:
                generation = copy_case_tree(worker_path, view, logical_root=logical)
                _own_tree(view, 2)
                matching = next(root for root in roots if root["target"] == selected["target"])
                mountpoint = Path(matching["source"]) / relative
                try:
                    mountpoint.mkdir(parents=True, exist_ok=False)
                except FileExistsError:
                    # A leased directory the candidate input already contains is hidden by the
                    # case bind mount; any other kind of entry there is refused.
                    if not stat.S_ISDIR(os.lstat(mountpoint).st_mode):
                        _refuse("scoped case mountpoint is not a real directory in the candidate copy")
            except BaseException:
                remove_private_tree(work)
                raise
            record = {"handle": handle, "logicalRoot": logical,
                      "workerPeerPid": peer_pid, "workerPeerUid": 1,
                      "candidateUid": 2, "copyIn": generation,
                      "events": ["open", "copy-in"]}
            case = {"handle": handle, "logicalRoot": logical,
                    "workerPath": worker_path, "view": view, "work": work,
                    "roots": roots, "generation": generation,
                    "handles": set(), "dirty": False, "record": record}
            cases[handle] = case
            evidence["caseLeases"].append(record)
            return {"caseHandle": handle, "generation": generation}

        def copy_out_case(case: dict[str, Any]) -> dict[str, Any]:
            if case["handles"]:
                _refuse("scoped case copy-out requires torn-down candidate handles")
            if not case["dirty"]:
                _refuse("scoped case has no candidate output to copy")
            require_worker_generation(case)
            stage = case["work"] / ("copy-out-" + uuid.uuid4().hex)
            old = case["work"] / ("old-worker-" + uuid.uuid4().hex)
            output = copy_case_tree(case["view"], stage,
                                    logical_root=case["logicalRoot"])
            _own_tree(stage, 1)
            os.rename(case["workerPath"], old)
            try:
                os.rename(stage, case["workerPath"])
            except BaseException:
                os.rename(old, case["workerPath"])
                raise
            remove_private_tree(old)
            case["generation"] = output
            case["dirty"] = False
            case["record"]["copyOut"] = output
            case["record"]["events"].append("copy-out")
            return {"generation": output}

        def sync_in_case(case: dict[str, Any], expected: Any) -> dict[str, Any]:
            if case["handles"] or case["dirty"] or expected != case["generation"]:
                _refuse("scoped case copy-in requires a quiescent matching generation")
            stage = case["work"] / ("copy-in-" + uuid.uuid4().hex)
            old = case["work"] / ("old-candidate-" + uuid.uuid4().hex)
            incoming = copy_case_tree(case["workerPath"], stage,
                                      logical_root=case["logicalRoot"])
            _own_tree(stage, 2)
            os.rename(case["view"], old)
            try:
                os.rename(stage, case["view"])
            except BaseException:
                os.rename(old, case["view"])
                raise
            remove_private_tree(old)
            case["generation"] = incoming
            case["record"]["events"].append("copy-in")
            return {"generation": incoming}

        def close_case(case: dict[str, Any]) -> dict[str, Any]:
            if case["handles"] or case["dirty"]:
                _refuse("scoped case close requires copy-out and torn-down handles")
            require_worker_generation(case)
            remove_private_tree(case["work"])
            case["record"]["events"].append("close")
            cases.pop(case["handle"])
            return {"closed": True}

        def worker_broker() -> None:
            calls = 0
            requests = 0
            while not stop.is_set():
                try:
                    connection, _ = worker_server.accept()
                except socket.timeout:
                    continue
                with connection:
                    connection.settimeout(MAX_WORKER_SECONDS + 10)
                    try:
                        peer_pid, peer_uid, peer_gid = struct.unpack(
                            "3i", connection.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
                        if not active_worker.is_set() or peer_uid != 1 or peer_gid != 1:
                            _refuse("worker broker peer refused")
                        request = _read_message(connection, MAX_REQUEST_BYTES)
                        requests += 1
                        if requests > MAX_CASE_REQUESTS or not isinstance(request, dict):
                            _refuse("worker broker request bound or shape refused")
                        operation = request.get("op")
                        if operation == "case_open":
                            response = open_case(request, peer_pid)
                        elif operation in ("case_start", "case_stream", "case_wait",
                                           "case_signal", "case_teardown", "case_copy_out",
                                           "case_sync_in", "case_close", "case_status"):
                            case = case_by_handle(request.get("caseHandle"))
                            if operation == "case_start":
                                if set(request) not in ({"op", "caseHandle", "argv", "cwd",
                                                         "timeout", "stdinB64"},
                                                        {"op", "caseHandle", "argv", "cwd",
                                                         "timeout", "stdinB64", "env"}):
                                    _refuse("scoped case start has wrong shape")
                                response = start_candidate(
                                    {key: value for key, value in request.items()
                                     if key != "caseHandle"}, requests, case=case)
                            elif operation in ("case_stream", "case_wait", "case_signal",
                                               "case_teardown"):
                                if (not isinstance(request.get("handle"), str) or
                                        request["handle"] not in case["handles"] or
                                        sessions[request["handle"]]["caseHandle"] !=
                                        case["handle"]):
                                    _refuse("candidate process handle is outside scoped case")
                                inner_op = operation.removeprefix("case_")
                                inner = {key: value for key, value in request.items()
                                         if key != "caseHandle"}
                                inner["op"] = inner_op
                                response = session_request(inner)
                                case["record"]["events"].append(inner_op)
                                if operation == "case_teardown":
                                    case["handles"].remove(request["handle"])
                            elif operation == "case_status":
                                if set(request) != {"op", "caseHandle"}:
                                    _refuse("scoped status has wrong shape")
                                response = {"handles": len(case["handles"]),
                                            "dirty": case["dirty"],
                                            "workerChanged": (worker_generation(case) != case["generation"]
                                                              if not case["handles"] else None),
                                            "generation": case["generation"]}
                            elif operation == "case_copy_out":
                                if set(request) != {"op", "caseHandle"}:
                                    _refuse("scoped copy-out has wrong shape")
                                response = copy_out_case(case)
                            elif operation == "case_sync_in":
                                if set(request) != {"op", "caseHandle", "expectedGeneration"}:
                                    _refuse("scoped copy-in has wrong shape")
                                response = sync_in_case(case, request["expectedGeneration"])
                            else:
                                if set(request) != {"op", "caseHandle"}:
                                    _refuse("scoped close has wrong shape")
                                response = close_case(case)
                        elif operation == "run_unstateful":
                            if (set(request) != {"op", "argv", "cwd", "timeout"}
                                    or calls >= MAX_REQUESTS):
                                _refuse("worker broker accepts only bounded unstateful runs")
                            argv, cwd, timeout, principal = _request(
                                {"argv": request["argv"], "cwd": request["cwd"],
                                 "timeout": request["timeout"], "principal": "candidate"},
                                plan["roots"], plan["cwd"])
                            calls += 1
                            work, roots = copied_roots("from-worker-" + str(calls), principal)
                            command = _sandbox(plan, principal, roots, argv, cwd)
                            try:
                                result = _run_role(command, principal, timeout,
                                                   namespace_lease=namespace_lease)
                            finally:
                                _reclaim_tree(work)
                            observation = result.pop("observation")
                            evidence["workers"].append({
                                "argv": argv, "cwd": cwd, "principal": principal,
                                "origin": "worker-broker", "observation": observation,
                                "returncode": result["returncode"],
                                "stdoutSha256": hashlib.sha256(result["stdout"]).hexdigest(),
                                "stderrSha256": hashlib.sha256(result["stderr"]).hexdigest(),
                                "duration_ns": result["duration_ns"]})
                            evidence["workerBrokerCalls"].append({
                                "peerPid": peer_pid, "peerUid": peer_uid, "peerGid": peer_gid,
                                "candidateUid": observation["uid"],
                                "candidateGid": observation["gid"],
                                "candidatePidNamespace": observation["namespaces"]["pid"],
                                "argvSha256": hashlib.sha256(json.dumps(argv).encode()).hexdigest()})
                            result["stdout"] = base64.b64encode(result["stdout"]).decode("ascii")
                            result["stderr"] = base64.b64encode(result["stderr"]).decode("ascii")
                            result["observation"] = observation
                            response = result
                        else:
                            _refuse("worker broker operation is unsupported")
                        connection.sendall(json.dumps(response).encode() + b"\n")
                    except Exception as exc:
                        errors.append(str(exc))
                        try:
                            connection.sendall(json.dumps({"error": str(exc)}).encode() + b"\n")
                        except OSError:
                            pass
                        stop.set()
                        worker_server.close()

        def start_candidate(request: Mapping[str, Any], call_number: int,
                            case: dict[str, Any] | None = None) -> dict[str, Any]:
            expected = ({"op", "argv", "cwd", "timeout", "stdinB64"} if case is not None
                        else {"op", "argv", "cwd", "timeout"})
            if case is not None and set(request) == expected | {"env"}:
                expected = expected | {"env"}
            if set(request) != expected:
                _refuse("isolated start request has wrong shape")
            environment = request.get("env", {})
            if (not isinstance(environment, dict) or
                    any(key not in CANDIDATE_ENV_ALLOWED or not isinstance(value, str)
                        or re.fullmatch(CANDIDATE_ENV_ALLOWED[key], value) is None
                        for key, value in environment.items())):
                _refuse("candidate environment is outside the determinism allowlist")
            argv, cwd, timeout, principal = _request(
                {"argv": request["argv"], "cwd": request["cwd"],
                 "timeout": request["timeout"], "principal": "candidate"},
                plan["roots"], plan["cwd"])
            stdin_bytes = None
            if case is not None:
                if not isinstance(request["stdinB64"], str):
                    _refuse("scoped case stdin is not base64 text")
                stdin_bytes = base64.b64decode(request["stdinB64"], validate=True)
                if len(stdin_bytes) > MAX_CASE_STDIN_BYTES:
                    _refuse("scoped case stdin exceeds limit")
                require_worker_generation(case)
                work, roots = None, case["roots"]
                case_bind = {"source": str(case["view"]),
                             "target": case["logicalRoot"]}
            else:
                work, roots = copied_roots(call_number, principal)
                case_bind = None
            command = _sandbox(plan, principal, roots, argv, cwd, case_bind=case_bind,
                               environment=environment)
            handle = uuid.uuid4().hex
            session: dict[str, Any] = {
                "argv": argv, "cwd": cwd, "work": work,
                "ready": threading.Event(), "done": threading.Event(),
                "process": None, "observation": None, "result": None,
                "error": None, "stdout": bytearray(), "stderr": bytearray(),
                "closed": False, "events": ["start"],
                "caseHandle": case["handle"] if case is not None else None,
            }
            sessions[handle] = session
            if case is not None:
                case["handles"].add(handle)
                case["dirty"] = True
                case["record"]["events"].append("start")

            def on_process(process: subprocess.Popen[bytes]) -> None:
                session["process"] = process

            def on_observed(observation: dict[str, Any]) -> None:
                session["observation"] = observation
                session["ready"].set()

            def on_output(stream: str, chunk: bytes) -> None:
                with sessions_lock:
                    session[stream].extend(chunk)

            def execute() -> None:
                try:
                    result = _run_role(command, principal, timeout, on_process=on_process,
                                       on_observed=on_observed, on_output=on_output,
                                       namespace_lease=namespace_lease,
                                       stdin_bytes=stdin_bytes)
                    session["result"] = result
                    evidence["workers"].append({
                        "argv": argv, "cwd": cwd, "principal": principal,
                        "observation": result["observation"],
                        "returncode": result["returncode"],
                        "stdoutSha256": hashlib.sha256(result["stdout"]).hexdigest(),
                        "stderrSha256": hashlib.sha256(result["stderr"]).hexdigest(),
                        "duration_ns": result["duration_ns"],
                        "asyncEvents": session["events"],
                        "caseHandle": session["caseHandle"],
                    })
                except Exception as exc:
                    session["error"] = type(exc).__name__ + ": " + str(exc)
                    errors.append(session["error"])
                finally:
                    if work is not None:
                        try:
                            _reclaim_tree(work)
                        except Exception as exc:
                            session["error"] = "reclaim: " + type(exc).__name__ + ": " + str(exc)
                            errors.append(session["error"])
                    session["ready"].set()
                    session["done"].set()

            runner = threading.Thread(target=execute, daemon=True)
            session["thread"] = runner
            runner.start()
            if not session["ready"].wait(timeout=15) or session["observation"] is None:
                _refuse("isolated candidate did not establish its role boundary")
            return {"handle": handle, "observation": session["observation"]}

        def session_request(request: Mapping[str, Any]) -> dict[str, Any]:
            if (set(request) not in ({"op", "handle"}, {"op", "handle", "waitMs"},
                                     {"op", "handle", "stdoutOffset", "stderrOffset"},
                                     {"op", "handle", "signal"})
                    or not isinstance(request.get("handle"), str)):
                _refuse("isolated candidate session request has wrong shape")
            session = sessions.get(request["handle"])
            if session is None or session["closed"]:
                _refuse("unknown or closed isolated candidate handle")
            op = request["op"]
            if op == "stream":
                if set(request) != {"op", "handle", "stdoutOffset", "stderrOffset"}:
                    _refuse("stream request has wrong shape")
                offsets = (request["stdoutOffset"], request["stderrOffset"])
                if any(type(value) is not int or value < 0 for value in offsets):
                    _refuse("stream offsets must be nonnegative integers")
                with sessions_lock:
                    stdout = bytes(session["stdout"])
                    stderr = bytes(session["stderr"])
                if offsets[0] > len(stdout) or offsets[1] > len(stderr):
                    _refuse("stream offset exceeds observed output")
                session["events"].append("stream")
                out = stdout[offsets[0]:offsets[0] + 65536]
                err = stderr[offsets[1]:offsets[1] + 65536]
                return {"done": session["done"].is_set(),
                        "stdoutB64": base64.b64encode(out).decode("ascii"),
                        "stderrB64": base64.b64encode(err).decode("ascii"),
                        "stdoutNext": offsets[0] + len(out),
                        "stderrNext": offsets[1] + len(err)}
            if op == "wait" and set(request) in ({"op", "handle"}, {"op", "handle", "waitMs"}):
                wait_ms = request.get("waitMs", 0)
                if type(wait_ms) is not int or not 0 <= wait_ms <= MAX_CASE_WAIT_MS:
                    _refuse("wait budget is outside the allowed range")
                session["events"].append("wait")
                if wait_ms:
                    session["done"].wait(timeout=wait_ms / 1000)
                if not session["done"].is_set():
                    return {"done": False}
                if session["error"] is not None or session["result"] is None:
                    _refuse("isolated candidate failed: " + str(session["error"]))
                result = session["result"]
                return {"done": True, "returncode": result["returncode"],
                        "stdoutB64": base64.b64encode(result["stdout"]).decode("ascii"),
                        "stderrB64": base64.b64encode(result["stderr"]).decode("ascii")}
            if op == "signal" and set(request) == {"op", "handle", "signal"}:
                selected = {"SIGKILL": signal.SIGKILL,
                            "SIGTERM": signal.SIGTERM}.get(request["signal"])
                if selected is None:
                    _refuse("isolated candidate signal is not allowed")
                process = session["process"]
                delivered = bool(process is not None and process.poll() is None)
                if delivered:
                    try:
                        os.killpg(process.pid, selected)
                    except ProcessLookupError:
                        delivered = False
                session["events"].append("signal:" + request["signal"])
                return {"delivered": delivered}
            if op == "teardown" and set(request) == {"op", "handle"}:
                process = session["process"]
                if process is not None and process.poll() is None:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                session["thread"].join(timeout=10)
                if session["thread"].is_alive() or not session["done"].is_set():
                    _refuse("isolated candidate teardown did not finish")
                session["events"].append("teardown")
                session["closed"] = True
                return {"closed": True, "done": True}
            _refuse("unknown isolated candidate session operation")

        def broker() -> None:
            calls = 0
            while not stop.is_set():
                try:
                    connection, _ = server.accept()
                except socket.timeout:
                    continue
                with connection:
                    connection.settimeout(MAX_WORKER_SECONDS + 10)
                    try:
                        _pid, uid, gid = struct.unpack("3i", connection.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
                        if uid != 0 or gid != 0:
                            _refuse("broker peer refused")
                        request = _read_message(connection, MAX_REQUEST_BYTES)
                        if isinstance(request, dict) and request.get("op") == "start":
                            if calls >= MAX_REQUESTS:
                                _refuse("isolated launch limit refused")
                            calls += 1
                            response = start_candidate(request, calls)
                            connection.sendall(json.dumps(response).encode() + b"\n")
                            continue
                        if isinstance(request, dict) and "op" in request:
                            response = session_request(request)
                            connection.sendall(json.dumps(response).encode() + b"\n")
                            continue
                        if calls >= MAX_REQUESTS:
                            _refuse("legacy launch limit refused")
                        argv, cwd, timeout, principal = _request(request, plan["roots"], plan["cwd"])
                        calls += 1
                        work, roots = copied_roots(calls, principal)
                        command = _sandbox(plan, principal, roots, argv, cwd)
                        try:
                            if principal == "worker":
                                active_worker_roots["roots"] = roots
                                active_worker.set()
                            result = _run_role(command, principal, timeout,
                                               namespace_lease=namespace_lease)
                        finally:
                            if principal == "worker":
                                active_worker.clear()
                                active_worker_roots["roots"] = []
                            _reclaim_tree(work)
                        evidence["workers"].append({"argv": argv, "cwd": cwd,
                                                    "principal": principal,
                                                    "observation": result.pop("observation"),
                                                    "returncode": result["returncode"],
                                                    "stdoutSha256": hashlib.sha256(result["stdout"]).hexdigest(),
                                                    "stderrSha256": hashlib.sha256(result["stderr"]).hexdigest(),
                                                    "duration_ns": result["duration_ns"]})
                        result["stdout"] = base64.b64encode(result["stdout"]).decode("ascii")
                        result["stderr"] = base64.b64encode(result["stderr"]).decode("ascii")
                        if principal == "candidate":
                            # SO_PEERCRED is observed by the mapped bootstrap
                            # outside the candidate's PID namespace. Expose it
                            # only to the trusted examiner for a signal probe.
                            result["examinerPeerPid"] = _pid
                        connection.sendall(json.dumps(result).encode() + b"\n")
                    except Exception as exc:
                        errors.append(str(exc))
                        try:
                            connection.sendall(json.dumps({"error": str(exc)}).encode() + b"\n")
                        except OSError:
                            pass
                        stop.set()
                        server.close()

        thread = threading.Thread(target=broker, daemon=True)
        worker_thread = threading.Thread(target=worker_broker, daemon=True)
        worker_thread.start()
        thread.start()
        examiner_roots = [{"source": root["frozen"], "target": root["target"]} for root in plan["roots"]]
        command = _sandbox(plan, "examiner", examiner_roots, plan["argv"], plan["cwd"])
        evidence["examinerCommand"] = command
        examiner = _run_role(command, "examiner", plan["timeout"],
                             namespace_lease=namespace_lease,
                             native_lifetime_plan=plan if 'nativeGuard' in plan else None)
        stop.set()
        thread.join(timeout=MAX_WORKER_SECONDS + 15)
        worker_thread.join(timeout=MAX_WORKER_SECONDS + 15)
        for session in sessions.values():
            process = session["process"]
            if process is not None and process.poll() is None:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            session["thread"].join(timeout=10)
            if not session["closed"] or session["thread"].is_alive():
                errors.append("isolated candidate session was not torn down")
        for case in list(cases.values()):
            errors.append("scoped candidate case lease was not closed")
            try:
                remove_private_tree(case["work"])
            except Exception as exc:
                errors.append("scoped case reclaim failed: " + str(exc))
        if thread.is_alive() or worker_thread.is_alive() or errors:
            _refuse("broker failed or did not become quiescent: " + "; ".join(errors))
        evidence["examiner"] = examiner["observation"]
        evidence["examinerReturnCode"] = examiner["returncode"]
        for observation in [evidence["examiner"], *[worker["observation"] for worker in evidence["workers"]]]:
            for name in ("uidMap", "gidMap"):
                expected = identity_projection(evidence['bootstrap'][name].encode('ascii'))
                if map_rows(observation[name].encode('ascii')) != map_rows(expected):
                    _refuse("complete role self-view mapping differs from bootstrap identity projection")
        for worker in evidence["workers"]:
            for namespace in ("pid", "mnt"):
                if worker["observation"]["namespaces"][namespace] == evidence["examiner"]["namespaces"][namespace]:
                    _refuse("worker and examiner namespace observations coincide")
        evidence["reportMountExclusive"] = True
        evidence["rolesCompleted"] = True
        sys.stdout.buffer.write(examiner["stdout"])
        sys.stderr.buffer.write(examiner["stderr"])
        return examiner["returncode"] if examiner["returncode"] >= 0 else 1
    except Exception as exc:
        evidence["error"] = str(exc)
        return 1
    finally:
        stop.set()
        server.close()
        worker_server.close()
        if namespace_lease is not None:
            try:
                namespace_lease.close()
            except Exception as exc:
                evidence['error'] = 'namespace descriptor cleanup failed: ' + str(exc)
        (runtime / "boundary.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")


def _candidate_request(request: Mapping[str, Any]) -> dict[str, Any]:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(MAX_WORKER_SECONDS + 15)
        connection.connect(BROKER_MOUNT)
        connection.sendall(json.dumps(request).encode() + b"\n")
        result = _read_message(connection, MAX_OUTPUT_BYTES * 4)
    if "error" in result:
        raise RuntimeError(result["error"])
    return result


def _candidate_run(argv: Sequence[str], *, cwd: str | None = None, timeout: int = 30,
                   principal: str = "worker") -> Any:
    result = _candidate_request({"argv": list(argv), "cwd": cwd,
                                 "timeout": timeout, "principal": principal})
    result["stdout"] = base64.b64decode(result["stdout"], validate=True)
    result["stderr"] = base64.b64decode(result["stderr"], validate=True)
    return types.SimpleNamespace(**result)


def _candidate_start_isolated(argv: Sequence[str], *, cwd: str | None = None,
                              timeout: int = 30) -> Any:
    result = _candidate_request({"op": "start", "argv": list(argv),
                                 "cwd": cwd, "timeout": timeout})
    return types.SimpleNamespace(**result)


def _candidate_stream_isolated(handle: str, *, stdout_offset: int = 0,
                               stderr_offset: int = 0) -> Any:
    result = _candidate_request({"op": "stream", "handle": handle,
                                 "stdoutOffset": stdout_offset,
                                 "stderrOffset": stderr_offset})
    result["stdout"] = base64.b64decode(result.pop("stdoutB64"), validate=True)
    result["stderr"] = base64.b64decode(result.pop("stderrB64"), validate=True)
    return types.SimpleNamespace(**result)


def _candidate_wait_isolated(handle: str, *, timeout: float = MAX_WORKER_SECONDS) -> Any:
    deadline = time.monotonic() + timeout
    while True:
        result = _candidate_request({"op": "wait", "handle": handle})
        if result["done"]:
            result["stdout"] = base64.b64decode(result.pop("stdoutB64"), validate=True)
            result["stderr"] = base64.b64decode(result.pop("stderrB64"), validate=True)
            return types.SimpleNamespace(**result)
        if time.monotonic() >= deadline:
            raise TimeoutError("isolated candidate wait exceeded caller deadline")
        time.sleep(0.02)


def _candidate_signal_isolated(handle: str, selected: str) -> bool:
    return bool(_candidate_request({"op": "signal", "handle": handle,
                                    "signal": selected})["delivered"])


def _candidate_teardown_isolated(handle: str) -> bool:
    return bool(_candidate_request({"op": "teardown", "handle": handle})["closed"])


def _role(role: str, payload: Sequence[str], run_id: str, namespace_fd: int) -> None:
    # Bubblewrap passes arbitrary --userns descriptors through its exec child.
    # Consume this exact trusted handle before any observation channel/workload.
    close_role_descriptor(namespace_fd)
    # Connect only after setpriv has established this role. No observer channel
    # or proc/namespace handle is inherited by examiner or candidate code.
    with _owned_role_channel() as observer:
        deadline = time.monotonic() + BOOTSTRAP_HANDSHAKE_SECONDS
        observer.settimeout(BOOTSTRAP_HANDSHAKE_SECONDS)
        observer.connect(ROLE_OBSERVER_MOUNT)
        request = json.dumps({'schemaVersion': 1, 'runId': run_id, 'role': role}).encode()
        if len(request) > MAX_REQUEST_BYTES or observer.send(request) != len(request):
            _refuse('role kernel-observer request was incomplete')
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                _refuse('kernel role observation exceeded its original startup deadline')
            observer.settimeout(remaining)
            response, ancillary, flags, _address = observer.recvmsg(MAX_REQUEST_BYTES + 1)
            if ancillary or flags & ~socket.MSG_EOR or not response or len(response) > MAX_REQUEST_BYTES:
                _refuse('daemon did not acknowledge kernel role observation')
            receipt = json.loads(response, object_pairs_hook=_unique_role_fields)
            if isinstance(receipt, dict) and 'recordId' in receipt:
                entry_binding = _role_acknowledgement(
                    receipt, role, payload, run_id, require_loader=(role == 'examiner'),
                    require_native=(role == 'examiner'))
                break
            if (not isinstance(receipt, dict) or set(receipt) != {'operation', 'target'}
                    or receipt['operation'] != 'mount-handle'):
                _refuse('invalid kernel role observation request')
            target = _absolute(receipt['target'])
            descriptor = os.open(target, os.O_PATH | os.O_CLOEXEC | os.O_NOFOLLOW)
            try:
                sent = observer.sendmsg([b'MOUNT\n'], [
                    (socket.SOL_SOCKET, socket.SCM_RIGHTS, array.array('i', [descriptor]))])
                if sent != len(b'MOUNT\n'):
                    _refuse('kernel mount handle response was incomplete')
            finally:
                os.close(descriptor)
        if role != "examiner":
            observer.close()
        # No workload code executes before this fixed helper emits its observation and receives
        # acknowledgement. The parent consumes exactly that frame and treats later stdout as data.
        print(json.dumps({**_observations(role), 'kernelObservationId': receipt['recordId']}), flush=True)
        # Read exactly the three acknowledgement bytes. Candidate stdin follows them on the
        # same pipe, and a larger read would consume the first byte of that payload.
        acknowledgement = b""
        while len(acknowledgement) < 3:
            chunk = os.read(0, 3 - len(acknowledgement))
            if not chunk:
                break
            acknowledgement += chunk
        if acknowledgement != b"GO\n":
            _refuse("supervisor did not acknowledge role boundary")
        if role != "candidate":
            descriptor = os.open("/dev/null", os.O_RDONLY)
            os.dup2(descriptor, 0)
            os.close(descriptor)
        if role == "examiner":
            candidate = types.ModuleType("candidate")
            candidate.run = _candidate_run
            candidate.run_isolated = lambda argv, *, cwd=None, timeout=30: _candidate_run(
                argv, cwd=cwd, timeout=timeout, principal="candidate")
            candidate.start_isolated = _candidate_start_isolated
            candidate.stream_isolated = _candidate_stream_isolated
            candidate.wait_isolated = _candidate_wait_isolated
            candidate.signal_isolated = _candidate_signal_isolated
            candidate.teardown_isolated = _candidate_teardown_isolated
            sys.modules["candidate"] = candidate
            # Only identified verifier helpers enter Python's search path. Candidate cwd stays out.
            sys.path.insert(0, str(Path(payload[1]).parent))
            sys.path.insert(0, VERIFIER_MOUNT)
            sys.argv = list(payload[1:])
            observer.settimeout(None)
            native_registry = _NativeExaminerCode(run_id, receipt)
            registry, code = _prepare_retained_entry(
                payload[1], run_id, entry_binding, observer, receipt['recordId'],
                registry=native_registry)
    if role != "examiner":
        os.execv(payload[0], list(payload))
    # The observation connection and every transfer descriptor are closed before entry code.
    with registry.loader_support['BoundImports'](registry.loader_policy, registry, _read_examiner_source):
        registry.activate()
        registry.run_main(code, payload[1])


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--bootstrap":
        raise SystemExit(_bootstrap(sys.argv[2]))
    if len(sys.argv) == 6 and sys.argv[1] == "--role" and sys.argv[2] in ("examiner", "worker", "candidate"):
        _role(sys.argv[2], json.loads(sys.argv[3]), sys.argv[4], int(sys.argv[5]))
    else:
        raise SystemExit("invalid private evaluator invocation")
