"""Exact native lifetime wire data; never a confinement or custody predicate.

The daemon owns the transport, object reads, kernel joins and retention. This
module only parses their already acquired bytes. No target code is imported or
deserialized. Native integer payloads are signed little-endian two's complement;
Unicode payloads are little-endian code points, preserving lone surrogates.
"""
from __future__ import annotations

from dataclasses import dataclass
import struct


PACKET_MAGIC = b'WLNLv001'
ACK_MAGIC = b'WLAKv001'
TOKEN_BYTES = 32
HEADER = struct.Struct('<8sQQQ32s')
ACK = struct.Struct('<8sQQQ32s32s')
HELLO, ATTEMPT, RESULT, ACTIVATION, TERMINAL = range(1, 6)
NONE, FALSE, TRUE, INTEGER, TEXT, BYTES, TUPLE, UNAVAILABLE = range(8)
_U64 = struct.Struct('<Q')
_U32 = struct.Struct('<I')


class NativeLifetimeFormatError(ValueError):
    pass


@dataclass(frozen=True)
class UnavailableValue:
    """Only a copied native type name, explicitly not the object's contents."""
    native_type_name: bytes


def decode_record(payload: bytes, *, _check=lambda: None):
    """Consume one complete exact record without recursion or arbitrary hooks."""
    if type(payload) is not bytes:
        raise NativeLifetimeFormatError('native record must be exact bytes')
    cursor = 0
    stack = []

    def take(size):
        nonlocal cursor
        _check()
        if size < 0 or size > len(payload) - cursor:
            raise NativeLifetimeFormatError('native record length exceeds acquired bytes')
        data = payload[cursor:cursor + size]
        cursor += size
        return data

    while True:
        _check()
        tag = take(1)[0]
        if tag == NONE:
            value = None
        elif tag == FALSE:
            value = False
        elif tag == TRUE:
            value = True
        elif tag in (INTEGER, TEXT, BYTES, UNAVAILABLE):
            extent = _U64.unpack(take(_U64.size))[0]
            raw = take(extent)
            if tag == INTEGER:
                if not raw:
                    raise NativeLifetimeFormatError('empty native integer')
                if len(raw) > 1 and ((raw[-1] == 0 and not raw[-2] & 0x80)
                                     or (raw[-1] == 0xff and raw[-2] & 0x80)):
                    raise NativeLifetimeFormatError('noncanonical native integer')
                value = int.from_bytes(raw, 'little', signed=True)
            elif tag == TEXT:
                if extent % _U32.size:
                    raise NativeLifetimeFormatError('partial native Unicode code point')
                pieces = []
                try:
                    for start in range(0, len(raw), 65536):
                        _check()
                        pieces.append(raw[start:start + 65536].decode('utf-32-le', 'surrogatepass'))
                except UnicodeDecodeError as error:
                    raise NativeLifetimeFormatError('native Unicode code point out of range') from error
                _check()
                value = ''.join(pieces)
            elif tag == UNAVAILABLE:
                value = UnavailableValue(raw)
            else:
                value = raw
        elif tag == TUPLE:
            count = _U64.unpack(take(_U64.size))[0]
            # Every child needs at least a tag. Check against the actual acquired
            # extent before any count-dependent allocation; no new input cap.
            if count > len(payload) - cursor:
                raise NativeLifetimeFormatError('native tuple count exceeds acquired bytes')
            if count:
                stack.append([count, []])
                continue
            value = ()
        else:
            raise NativeLifetimeFormatError('unknown native record tag')
        while stack:
            _check()
            top = stack[-1]
            top[1].append(value)
            top[0] -= 1
            if top[0]:
                break
            value = tuple(top[1])
            stack.pop()
        else:
            if cursor != len(payload):
                raise NativeLifetimeFormatError('trailing native record bytes')
            _check()
            return value


def parse_header(payload: bytes):
    if type(payload) is not bytes or len(payload) != HEADER.size:
        raise NativeLifetimeFormatError('native packet size differs')
    magic, kind, sequence, extent, previous = HEADER.unpack(payload)
    if magic != PACKET_MAGIC or kind not in (HELLO, ATTEMPT, RESULT, ACTIVATION, TERMINAL):
        raise NativeLifetimeFormatError('native packet version or kind differs')
    return kind, sequence, extent, previous


def acknowledgement(kind, sequence, deadline_ns, previous, token):
    if (type(kind) is not int or kind not in (HELLO, ATTEMPT, RESULT, ACTIVATION, TERMINAL)
            or type(sequence) is not int or type(deadline_ns) is not int
            or type(previous) is not bytes or len(previous) != TOKEN_BYTES
            or type(token) is not bytes or len(token) != TOKEN_BYTES):
        raise NativeLifetimeFormatError('native acknowledgement fields differ')
    return ACK.pack(ACK_MAGIC, kind, sequence, deadline_ns, previous, token)


def observation_value(value, *, _check=lambda: None):
    """Flat typed diagnostic index into the separately retained complete bytes.

    Byte values have length/hash references, avoiding another full base64 copy.
    This index is not a replacement for the complete retained wire object.
    """
    import base64
    import hashlib
    rows = []
    pending = [(value, None, None)]
    while pending:
        _check()
        current, parent, position = pending.pop()
        row = {'parent': parent, 'position': position}
        index = len(rows)
        rows.append(row)
        if type(current) is tuple:
            row.update(type='tuple', items=len(current))
            for i in reversed(range(len(current))):
                _check()
                pending.append((current[i], index, i))
        elif type(current) is bytes:
            row.update(type='bytes', bytes=len(current), sha256=hashlib.sha256(current).hexdigest())
        elif type(current) is UnavailableValue:
            row.update(type='unavailable', nativeTypeNameBase64=
                       base64.b64encode(current.native_type_name).decode('ascii'))
        elif current is None or type(current) in (bool, str):
            row.update(type=type(current).__name__, value=current)
        elif type(current) is int:
            # Hex avoids CPython's decimal conversion digit cap; it remains an
            # exact tagged integer, distinct from original source bytes.
            row.update(type='int', hex=hex(current))
        else:
            raise NativeLifetimeFormatError('unexpected decoded native value')
    _check()
    return rows


def exact_context(actual, expected):
    """Do not let bool/int equality substitute for the expected wire types."""
    pending = [(actual, expected)]
    while pending:
        left, right = pending.pop()
        if type(left) is not type(right):
            return False
        if type(right) is tuple:
            if len(left) != len(right):
                return False
            pending.extend(zip(left, right))
        elif right is None or type(right) in (bool, int, str, bytes):
            if left != right:
                return False
        else:
            return False
    return True


def _unavailable(value, check):
    pending = [value]
    while pending:
        check()
        item = pending.pop()
        if type(item) is UnavailableValue:
            return True
        if type(item) is tuple:
            pending.extend(item)
    return False


def _exception_shape(value, complete, check):
    def optional(item):
        return (type(item) is tuple and len(item) == 2 and type(item[0]) is bool
                and (item[0] or item[1] is None))
    if (type(value) is not tuple or len(value) != 4 or type(value[0]) is not bytes
            or not value[0] or value[1] != 'native-boundary-before-return'
            or type(value[2]) is not tuple or len(value[2]) != 7
            or not all(optional(item) for item in value[2][:-1])
            or type(value[2][-1]) is not bool):
        return False
    if complete and (value[2][0][0] is not True or type(value[2][0][1]) is not tuple):
        return False
    detail = value[3]
    if detail == 'base-fields-only-not-a-subclass-object-snapshot':
        return not complete
    if type(detail) is not tuple or not detail or type(detail[0]) is not str:
        return False
    sizes = {'ImportError': 5, 'SyntaxError': 10, 'OSError': 6}
    if detail[0] not in sizes or len(detail) != sizes[detail[0]]:
        return False
    fields = detail[1:-1] if detail[0] == 'OSError' else detail[1:]
    if not all(optional(item) for item in fields):
        return False
    if detail[0] == 'OSError' and type(detail[-1]) is not int:
        return False
    return not complete or not _unavailable(value, check)


def _cached_shape(value, codes):
    return (value is None or (type(value) is tuple and len(value) == 7
        and value[0] == 'held-cached-origin'
        and type(value[1]) is str and type(value[2]) is str
        and type(value[3]) is int and 0 < value[3] <= codes
        and all(type(item) is int and item > 0 for item in value[4:])))


def _tree_shape(value, codes, check):
    if (type(value) is not tuple or len(value) != 3 or value[0] != 'owned-code-tree'
            or type(value[1]) is not int or not 0 < value[1] <= codes
            or type(value[2]) is not tuple or not value[2]):
        return False
    nodes = {}
    for node in value[2]:
        check()
        if (type(node) is not tuple or len(node) != 6 or type(node[0]) is not int
                or not 0 < node[0] <= codes or node[0] in nodes
                or type(node[1]) is not str or not _cached_shape(node[2], codes)
                or type(node[3]) is not str or type(node[4]) is not int or node[4] < 0
                or type(node[5]) is not tuple):
            return False
        last = -1
        for edge in node[5]:
            check()
            if (type(edge) is not tuple or len(edge) != 2
                    or type(edge[0]) is not int or not last < edge[0] < node[4]
                    or type(edge[1]) is not int or not 0 < edge[1] <= codes):
                return False
            last = edge[0]
        nodes[node[0]] = node
    pending, seen = [value[1]], set()
    while pending:
        check()
        identity = pending.pop()
        if identity not in nodes:
            return False
        if identity in seen:
            continue
        seen.add(identity)
        for edge in nodes[identity][5]:
            check()
            pending.append(edge[1])
    return len(seen) == len(nodes)


def _route_shape(value, codes, check):
    return (type(value) is tuple and len(value) == 7 and value[0] == 'held-generator-binding'
        and type(value[1]) is str and type(value[2]) is str and type(value[3]) is bytes
        and type(value[4]) is int and value[4] > 0 and _cached_shape(value[5], codes)
        and _tree_shape(value[6], codes, check)
        and (value[5] is None or (value[5][1:3] == value[1:3]
             and value[5][3] == value[6][1] and value[5][5] == value[4])))


def invocation_context(run_id, startup_record, native, ready_record, deadline_ns):
    return (run_id, startup_record,
            tuple(native[key] for key in ('schema', 'runId', 'path', 'byteCount',
                                         'sha256', 'sourceRecordId', 'buildReceiptSha256')),
            ready_record, deadline_ns)


class OperationRoster:
    """Exact per-thread nesting; a clean terminal is only provisional retention."""
    def __init__(self, *, _check=lambda: None):
        self.check = _check
        self.pending = {}
        self.threads = {}
        self.activated = False
        self.any_violation = False
        self.incomplete_failure_facts = False
        self.code_count = 0
        self.phase = None
        self.first_failure = None
        self.incomplete_inputs = False

    @staticmethod
    def _require(condition, message):
        if not condition:
            raise NativeLifetimeFormatError(message)

    def accept(self, kind, sequence, value):
        self.check()
        require = self._require
        if kind == ATTEMPT:
            require(type(value) is tuple and len(value) == 9, 'native attempt shape differs')
            name, phase, thread, parent, inputs, path, source, options, codes = value
            require(type(name) is str and name in (
                'source-compile', 'frozen-metadata', 'frozen-code', 'ast-parse', 'ast-compiler',
                'bind-generator', 'bind-cached-generator', 'validated-generator-source', 'activate'),
                'native attempt operation differs')
            require(type(phase) is int and phase in range(5)
                    and type(thread) is int and thread > 0
                    and (parent is None or type(parent) is int)
                    and type(inputs) is tuple and type(options) is tuple
                    and (path is None or type(path) is str)
                    and (source is None or type(source) is bytes)
                    and (path is None) == (source is None)
                    and type(codes) is int and codes >= self.code_count,
                    'native attempt typed fields differ')
            shapes = {'source-compile': (0, 4), 'frozen-metadata': (1, 0),
                      'frozen-code': (1, 0), 'ast-parse': (2, 0), 'ast-compiler': (0, 4),
                      'bind-generator': (1, 0), 'bind-cached-generator': (1, 0),
                      'validated-generator-source': (2, 1), 'activate': (0, 0)}
            require((len(inputs), len(options)) == shapes[name]
                    and all(type(item) is int for item in options),
                    'native operation field counts or option types differ')
            if name in ('source-compile', 'ast-compiler', 'validated-generator-source'):
                require(type(path) is str and type(source) is bytes,
                        'native compiler/generator input has no owned source')
            if name == 'validated-generator-source':
                require(type(inputs[0]) is str and _route_shape(inputs[1], codes, self.check)
                        and inputs[1][2] == path and inputs[1][3] == source,
                        'native generated source has no exact held producer binding')
            if name == 'ast-compiler':
                require(parent in self.pending and self.pending[parent][1] == 'ast-parse',
                        'native AST compiler lacks its outer argument attempt')
            self.incomplete_inputs |= _unavailable(inputs, self.check)
            stack = self.threads.setdefault(thread, [])
            require(self.phase is None or phase == self.phase, 'native attempt changes phase without transition')
            require(sequence not in self.pending and parent == (stack[-1] if stack else None),
                    'native attempt parent or identity differs')
            self.pending[sequence] = (thread, name, codes, phase, inputs)
            stack.append(sequence)
            self.code_count = codes
            self.phase = phase
        elif kind == RESULT:
            require(type(value) is tuple and len(value) == 9, 'native result shape differs')
            identity, returned, phase, codes, _result, primary, complete, violated, first = value
            require(type(identity) is int and identity in self.pending
                    and type(returned) is bool and type(phase) is int and phase in range(5)
                    and type(codes) is int and codes >= self.code_count
                    and type(complete) is bool and type(violated) is bool
                    and (first is None or type(first) is str)
                    and ((primary is None) if returned else _exception_shape(primary, complete, self.check)),
                    'native result typed fields or exception presence differ')
            thread, name, _before, began_phase, inputs = self.pending[identity]
            require(violated == (type(first) is str and bool(first))
                    and (not self.any_violation or violated)
                    and (self.first_failure is None or first == self.first_failure),
                    'native sticky failure fields contradict retained history')
            if returned:
                allowed = (2,) if name in ('bind-generator', 'bind-cached-generator', 'activate') else (2, 3)
                require(began_phase in allowed and phase == (3 if name == 'activate' else began_phase)
                        and not violated and not self.any_violation and complete,
                        'successful native operation has invalid phase, sticky violation or incomplete facts')
                if name in ('source-compile', 'frozen-code', 'validated-generator-source'):
                    require(complete and _tree_shape(_result, codes, self.check),
                            'native code result lacks its complete owned tree')
                elif name in ('bind-generator', 'bind-cached-generator'):
                    require(complete and _route_shape(_result, codes, self.check),
                            'native generator result lacks its held binding')
                    label = inputs[0][0] if name == 'bind-generator' and type(inputs[0]) is tuple and inputs[0] else inputs[0]
                    require(type(label) is str and _result[1] == label,
                            'native generator binding differs from requested route')
                    require(name != 'bind-cached-generator' or _result[5] is not None,
                            'native cached binding lacks its actual cached origin')
                elif name == 'frozen-metadata' and _result is not None:
                    require(type(_result) is tuple and len(_result) == 2
                            and _result[0] == 'exact-dict-entries' and type(_result[1]) is tuple,
                            'native metadata result is not exact entries')
                    entries = _result[1]
                    require(all(type(row) is tuple and len(row) == 2 and type(row[0]) is str for row in entries)
                            and len(entries) == 3 and len({row[0] for row in entries}) == 3,
                            'native metadata keys are malformed or duplicated')
                    fields = dict(entries)
                    require(set(fields) == {'name', 'isPackage', 'originalName'}
                            and len(inputs) == 1 and type(inputs[0]) is str
                            and type(fields['name']) is str and fields['name'] == inputs[0]
                            and type(fields['isPackage']) is bool
                            and (fields['originalName'] is None or type(fields['originalName']) is str),
                            'native metadata values differ from their exact types/selector')
                elif name in ('ast-parse', 'ast-compiler'):
                    require(type(_result) is tuple and len(_result) == 2
                            and _result[0] == 'non-executable-result-not-snapshotted'
                            and type(_result[1]) is bytes and bool(_result[1]),
                            'native AST result descriptor differs')
                else:
                    require(_result is None, 'native non-value operation returned data')
            else:
                require(_result is None and phase == began_phase,
                        'native failed operation has data or changed phase')
            require(self.threads[thread][-1] == identity, 'native result nesting differs')
            self.threads[thread].pop()
            del self.pending[identity]
            self.code_count = codes
            self.any_violation |= violated
            if violated:
                self.first_failure = first
            self.phase = phase
            self.incomplete_failure_facts |= primary is not None and not complete
            if name == 'activate' and returned:
                require(not self.activated and phase == 3 and not violated,
                        'native activation is repeated or unclean')
                self.activated = True
        elif kind == TERMINAL:
            require(type(value) is tuple and len(value) == 7, 'native terminal shape differs')
            name, phase, violated, first, pending, codes, sent = value
            require(name == 'native-finalized' and type(phase) is int and phase in range(5)
                    and type(violated) is bool and (first is None or type(first) is str)
                    and type(pending) is int and pending == len(self.pending)
                    and type(codes) is int and codes == self.code_count
                    and type(sent) is int and sent == sequence,
                    'native terminal differs from the retained operation roster')
            require((self.phase is None or phase == self.phase)
                    and violated == (type(first) is str and bool(first))
                    and (not self.any_violation or violated)
                    and (self.first_failure is None or first == self.first_failure),
                    'native terminal contradicts phase/sticky history')
            return {'retainedToNativeFinalization': True, 'activated': self.activated,
                    'pendingOperations': pending,
                    'cleanReportedTerminal': (self.activated and phase == 3 and not violated
                        and not self.any_violation and not self.pending
                        and not self.incomplete_failure_facts and not self.incomplete_inputs),
                    'incompleteFailureFacts': self.incomplete_failure_facts,
                    'incompleteAcquisitionInputs': self.incomplete_inputs,
                    'actualProcessWaitAndCloseStillRequired': True,
                    'primaryWorkloadFailurePreservationEstablished': False,
                    'protectedCustody': False, 'confinementEstablished': False}
        else:
            raise NativeLifetimeFormatError('unexpected native operation event kind')
        return None


def receive(observer, connection):
    """Daemon-owned acquisition, using the existing held-subject/retention code."""
    import hashlib
    import json
    import os
    import socket
    import time
    from ..raw_observation import exception_observation, optional_bytes
    from .kernel_role_observer import (
        _Capture, _DescriptorOwner, _Subject, _require, _same_object,
        SO_PEERPIDFD, native_filter_fields,
    )

    record = observer._record('native-lifetime-open')
    record['scope'] = 'process-attributed-native-lifetime-retention-not-protected-custody'
    cleanup = observer._record('native-lifetime-held-descriptor-cleanup')
    capture = _Capture(record, observer.maximum_bytes,
                       time.monotonic() + observer.handshake_seconds, observer.stop)
    primary = None
    sequence, previous = 0, bytes(TOKEN_BYTES)

    def send(payload, capture):
        while True:
            capture.check()
            try:
                _require(connection.send(payload) == len(payload), 'native lifetime send incomplete')
                return
            except TimeoutError:
                continue

    try:
        with _DescriptorOwner(cleanup) as held:
            credentials = connection.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED,
                                                struct.calcsize('=iII'))
            peer = struct.unpack('=iII', credentials)
            record.update(peerCredentialsBytes=optional_bytes(credentials), peerCredentials=list(peer))
            pidfd = connection.getsockopt(socket.SOL_SOCKET, SO_PEERPIDFD)
            subject = _Subject(peer[0], pidfd, capture, held)
            if observer.bootstrap is not None and peer[0] == observer.bootstrap.pid:
                _require(subject.identity == observer.bootstrap.identity
                         and subject.cgroup == observer.bootstrap.cgroup,
                         'native budget sender differs from held bootstrap')
                with _DescriptorOwner(record) as objects:
                    payload, descriptors = observer._packet(connection, capture, objects, peer)
                    _require(not descriptors, 'native budget cannot transfer descriptors')
                    request = observer._native_json(payload)
                    record['request'] = request
                    with observer.lock:
                        startup = observer.native_startup
                        _require(startup is not None and observer.lifetime_budget is None,
                                 'native budget lacks a fresh examiner startup')
                        _require(type(request) is dict and set(request) == {
                            'schemaVersion', 'operation', 'runId', 'startupRecordId', 'deadlineNs'}
                            and type(request['schemaVersion']) is int and request['schemaVersion'] == 1
                            and request['operation'] == 'native-lifetime-budget'
                            and request['runId'] == observer.plan['runId']
                            and request['startupRecordId'] == startup['recordId']
                            and type(request['deadlineNs']) is int
                            and time.monotonic_ns() < request['deadlineNs']
                            <= time.monotonic_ns() + observer.plan['timeout'] * 1_000_000_000,
                            'native budget does not identify the running original role deadline')
                    capture.deadline = request['deadlineNs'] / 1_000_000_000
                    final, extra = observer._packet(connection, capture, objects, peer, allow_eof=True)
                    _require(final == b'' and not extra, 'native budget lacks true EOF')
                    subject.recheck()
                record.update(kind='native-lifetime-budget', trueEof=True,
                              identity=subject.identity, actualRoleDeadlineClaim=request['deadlineNs'])
                reply = {**request, 'operation': 'native-lifetime-budget-retained',
                         'recordId': record['recordId']}
                encoded = json.dumps(reply, sort_keys=True, separators=(',', ':')).encode()
                record['acknowledgementBytes'] = optional_bytes(encoded)
                observer._retain(record)
                with observer.lock:
                    observer.lifetime_budget = dict(request)
                send(encoded, capture)
                observer._retain({**observer._record('native-lifetime-budget-acknowledgement'),
                    'retainedRecordId': record['recordId'], 'sent': True, 'bytes': optional_bytes(encoded)})
                return

            with observer.lock:
                startup, budget = observer.native_startup, observer.lifetime_budget
                _require(startup is not None and budget is not None and not observer.lifetime_started,
                         'native lifetime startup/budget is absent or already consumed')
                _require(peer == startup['peer'] and subject.identity == startup['identity']
                         and subject.cgroup == startup['cgroup'],
                         'native lifetime subject differs from held examiner startup')
                _require(all(_same_object(subject.namespaces[name]['object'], identity)
                             for name, identity in startup['namespaces'].items())
                         and all(subject.status.get(key) == value
                                 for key, value in startup['credentialFields'].items()),
                         'native lifetime namespaces or credentials differ')
                observer.lifetime_started = True
            deadline_ns = budget['deadlineNs']
            capture.deadline = deadline_ns / 1_000_000_000
            subject.recheck()
            record.update(startupRecordId=startup['recordId'], identity=subject.identity,
                          nativeKernelFilter=native_filter_fields(subject.status),
                          nativeGuard=observer.plan['nativeGuardBinding'])
            _require(record['nativeKernelFilter'] == startup['nativeKernelFilter'],
                     'native lifetime kernel filter sample differs')
            ready = {'schemaVersion': 1, 'operation': 'native-lifetime-ready',
                     'runId': observer.plan['runId'], 'startupRecordId': startup['recordId'],
                     'nativeGuard': observer.plan['nativeGuardBinding'],
                     'deadlineNs': deadline_ns, 'recordId': record['recordId']}
            encoded = json.dumps(ready, sort_keys=True, separators=(',', ':')).encode()
            record['acknowledgementBytes'] = optional_bytes(encoded)
            observer._retain(record)
            send(encoded, capture)
            observer._retain({**observer._record('native-lifetime-ready-sent'),
                'retainedRecordId': record['recordId'], 'sent': True, 'bytes': optional_bytes(encoded)})
            context = invocation_context(observer.plan['runId'], startup['recordId'],
                                         observer.plan['nativeGuardBinding'], record['recordId'], deadline_ns)
            roster = OperationRoster(_check=capture.check)
            while True:
                item = observer._record('native-lifetime-receive')
                item.update(scope=record['scope'], startupRecordId=startup['recordId'],
                            sequence=sequence, previousReceiptSha256=previous.hex())
                current = _Capture(item, observer.maximum_bytes, capture.deadline, observer.stop)
                subject.capture = current
                terminal = None
                try:
                    with _DescriptorOwner(item) as objects:
                        packet, descriptors = observer._packet(connection, current, objects, peer)
                        kind, actual_sequence, extent, actual_previous = parse_header(packet)
                        _require(actual_sequence == sequence and actual_previous == previous
                                 and len(descriptors) == 1, 'native event sequence/token/objects differ')
                        subject.recheck()
                        # The original tree-byte bound is not a new generated-input
                        # bound. Exact fstat extent, seals, EOF and original owned
                        # process/resource deadlines remain mandatory.
                        raw = observer._entry_object_bytes(descriptors[0], 'native-record', extent,
                                                          max(observer.maximum_bytes, extent), current)
                        value = decode_record(raw, _check=current.check)
                        item.update(eventKind=kind, decodedIndex=observation_value(value, _check=current.check))
                        if sequence == 0:
                            _require(kind == HELLO and type(value) is tuple and len(value) == 3
                                     and value[0] == 'native-lifetime-open' and exact_context(value[1], context)
                                     and type(value[2]) is tuple and len(value[2]) == 3
                                     and all(type(number) is int and number >= 0 for number in value[2]),
                                     'native HELLO does not join this startup/artifact/ready/deadline')
                            item['nativePeerView'] = value[2]
                        else:
                            terminal = roster.accept(kind, sequence, value)
                        if terminal is not None:
                            final, extra = observer._packet(connection, current, objects, peer, allow_eof=True)
                            _require(final == b'' and not extra, 'native terminal lacks true EOF')
                            item.update(kind='native-lifetime-terminal', trueEof=True, terminal=terminal)
                        subject.recheck()
                        token = hashlib.sha256(previous + packet + raw + item['recordId'].encode('ascii')).digest()
                        reply = acknowledgement(kind, sequence, deadline_ns, previous, token)
                    item['transferDescriptorsClosed'] = True
                    item['acknowledgementBytes'] = optional_bytes(reply)
                    observer._retain(item)
                    send(reply, current)
                    observer._retain({**observer._record('native-lifetime-acknowledgement'),
                        'startupRecordId': startup['recordId'], 'retainedRecordId': item['recordId'],
                        'sent': True, 'bytes': optional_bytes(reply),
                        'meaning': 'identified retention only; process wait/close and protected custody remain separate'})
                    previous = token
                    sequence += 1
                    if terminal is not None:
                        with observer.lock:
                            observer.lifetime_completions[startup['recordId']] = {
                                **terminal, 'recordId': item['recordId'], 'receiptSha256': token.hex(),
                                'acknowledgedPackets': sequence}
                        return
                except BaseException as error:
                    item['exception'] = exception_observation(error)
                    try:
                        observer._retain(item)
                    except BaseException as secondary:
                        error.add_note('native event failure retention also failed: ' + str(secondary))
                        error._worldline_retention_failed = True
                    raise
    except BaseException as error:
        primary = error
        failed = observer._record('native-lifetime-failure')
        failed.update(sequence=sequence, previousReceiptSha256=previous.hex(),
                      exception=exception_observation(error), openObservation=record)
        try:
            observer._retain(failed)
        except BaseException as secondary:
            error.add_note('native lifetime failure retention also failed: ' + str(secondary))
            error._worldline_retention_failed = True
        raise
    finally:
        try:
            observer._retain(cleanup)
        except BaseException as error:
            if primary is None:
                raise
            primary.add_note('native lifetime held cleanup retention also failed: ' + str(error))
            primary._worldline_retention_failed = True
