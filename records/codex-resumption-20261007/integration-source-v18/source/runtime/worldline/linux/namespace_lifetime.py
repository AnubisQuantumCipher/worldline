"""Invocation-owned namespace restriction and trusted quota reader.

This stdlib-only policy is staged beside the private bootstrap and launched using
worldline.trusted. It supplies a bounded confinement dependency, not admission or
proof. Raw reads, writes, failures and owned process cleanup remain observations.
"""
from __future__ import annotations

import base64
import fcntl
import json
import os
import select
import selectors
import socket
import stat
import subprocess
import sys
import threading
import time

# linux/nsfs.h, asm-generic/ioctl.h; supported Linux UAPI, no fallback.
NS_GET_PARENT = 46850
NS_GET_NSTYPE = 46851
CLONE_NEWUSER = 0x10000000
_READ = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK
_DIR = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_DIRECTORY
_QUOTA = '/proc/sys/user/max_user_namespaces'


class NamespaceRestrictionFailure(ValueError):
    code = 'PRIVATE_NAMESPACE_RESTRICTION_FAILED'


def require(condition, message):
    if not condition:
        raise NamespaceRestrictionFailure(message)


def raw(value):
    return None if value is None else {
        'encoding': 'base64', 'payload': base64.b64encode(value).decode('ascii')}


def failure(error):
    pending, indexes, nodes = [error], {id(error): 0}, []
    for item in pending:
        links = {}
        for name in ('__cause__', '__context__'):
            linked = getattr(item, name, None)
            if linked is not None and id(linked) not in indexes:
                indexes[id(linked)] = len(pending)
                pending.append(linked)
            links[name] = None if linked is None else indexes[id(linked)]
        nodes.append({'type': type(item).__qualname__, 'message': str(item),
                      'errno': getattr(item, 'errno', None),
                      'notes': list(getattr(item, '__notes__', ())),
                      'suppressContext': bool(item.__suppress_context__), **links})
    return {'root': 0, 'nodes': nodes}


def object_identity(info):
    return {'device': info.st_dev, 'inode': info.st_ino, 'mode': info.st_mode,
            'uid': info.st_uid, 'gid': info.st_gid, 'size': info.st_size}


def same_object(left, right):
    return (left['device'], left['inode'], stat.S_IFMT(left['mode'])) == (
        right['device'], right['inode'], stat.S_IFMT(right['mode']))


def remaining(deadline):
    value = deadline - time.monotonic()
    require(value > 0, 'original namespace startup deadline elapsed')
    return value


def map_rows(payload):
    """Complete, nonoverlapping kernel ID-map intervals; no role-only subset."""
    rows = []
    for line in payload.splitlines():
        fields = line.split()
        require(len(fields) == 3 and all(field.isdigit() for field in fields),
                'malformed namespace ID map')
        inside, outside, count = map(int, fields)
        # (uid_t)-1 cannot be mapped. This is a UAPI boundary, not a new quota.
        require(count > 0 and inside + count <= 0xffffffff
                and outside + count <= 0xffffffff, 'invalid namespace ID range')
        for old_inside, old_outside, old_count in rows:
            require(inside + count <= old_inside or old_inside + old_count <= inside,
                    'overlapping inside namespace ID ranges')
            require(outside + count <= old_outside or old_outside + old_count <= outside,
                    'overlapping outside namespace ID ranges')
        rows.append((inside, outside, count))
    require(rows, 'empty namespace ID map')
    return tuple(sorted(rows))


def identity_projection(payload):
    return ''.join(f'{inside} {inside} {count}\n'
                   for inside, _outside, count in map_rows(payload)).encode('ascii')


def parse_fields(payload):
    fields = {}
    for line in payload.splitlines():
        key, separator, value = line.partition(b':')
        require(separator and key and key not in fields, 'malformed proc status')
        fields[key] = value.strip()
    return fields


def process_identity(payload):
    head, separator, tail = payload.rpartition(b') ')
    pid, opening, _comm = head.partition(b' (')
    fields = tail.split()
    require(separator and opening and pid.isdigit() and len(fields) >= 20
            and fields[1].isdigit() and fields[19].isdigit(), 'malformed proc stat')
    return {'pid': int(pid), 'ppid': int(fields[1]), 'starttime': int(fields[19])}


class Capture:
    def __init__(self, record, deadline, maximum):
        self.record, self.deadline, self.maximum = record, deadline, maximum
        self.used = 0

    def read(self, name, *, parent=None):
        row = {'path': name, 'descriptor': None, 'bytes': None, 'eof': False,
               'returned': False, 'exception': None}
        self.record.setdefault('reads', []).append(row)
        descriptor, payload = None, bytearray()
        try:
            remaining(self.deadline)
            descriptor = os.open(name, _READ, dir_fd=parent)
            row['descriptor'] = object_identity(os.fstat(descriptor))
            while True:
                remaining(self.deadline)
                chunk = os.read(descriptor, min(65536, self.maximum - self.used + 1))
                payload.extend(chunk)
                self.used += len(chunk)
                require(self.used <= self.maximum, 'namespace read capture limit exceeded')
                if not chunk:
                    row['eof'] = True
                    break
            row['returned'] = True
            return bytes(payload)
        except BaseException as error:
            row['exception'] = failure(error)
            raise
        finally:
            row['bytes'] = raw(payload)
            if descriptor is not None:
                os.close(descriptor)

    def write(self, name, payload, *, parent=None):
        row = {'path': name, 'bytes': raw(payload), 'descriptor': None,
               'return': None, 'exception': None}
        self.record.setdefault('writes', []).append(row)
        descriptor = None
        try:
            remaining(self.deadline)
            descriptor = os.open(name, os.O_WRONLY | os.O_CLOEXEC | os.O_NOFOLLOW,
                                 dir_fd=parent)
            row['descriptor'] = object_identity(os.fstat(descriptor))
            row['return'] = os.write(descriptor, payload)
            require(row['return'] == len(payload), 'namespace write was incomplete')
        except BaseException as error:
            row['exception'] = failure(error)
            raise
        finally:
            if descriptor is not None:
                os.close(descriptor)


def send_packet(channel, value, deadline, maximum, record):
    payload = json.dumps(value, sort_keys=True).encode('utf-8')
    row = {'direction': 'send', 'bytes': raw(payload), 'return': None, 'exception': None}
    record.setdefault('packets', []).append(row)
    try:
        require(len(payload) <= maximum, 'namespace control output exceeds original limit')
        channel.settimeout(remaining(deadline))
        row['return'] = channel.send(payload)
        require(row['return'] == len(payload), 'namespace control send was incomplete')
    except BaseException as error:
        row['exception'] = failure(error)
        raise


def receive_packet(channel, deadline, maximum, record):
    row = {'direction': 'receive', 'bytes': None, 'flags': None, 'exception': None}
    record.setdefault('packets', []).append(row)
    try:
        channel.settimeout(remaining(deadline))
        payload, ancillary, flags, _address = channel.recvmsg(maximum + 1)
        row['bytes'], row['flags'] = raw(payload), flags
        require(not ancillary and not flags & ~socket.MSG_EOR and payload
                and len(payload) <= maximum, 'invalid namespace control packet')
        def unique(pairs):
            result = {}
            for key, value in pairs:
                require(key not in result, 'duplicate namespace control field')
                result[key] = value
            return result
        return json.loads(payload, object_pairs_hook=unique)
    except BaseException as error:
        row['exception'] = failure(error)
        raise


def decode_raw(value):
    require(type(value) is dict and set(value) == {'encoding', 'payload'}
            and value['encoding'] == 'base64' and type(value['payload']) is str,
            'descriptor observation bytes are absent')
    return base64.b64decode(value['payload'], validate=True)


class DescriptorInventory:
    """Ordered complete kernel entries, never a role-supplied success label."""
    def __init__(self, count, maximum):
        require(type(count) is int and count >= 0, 'invalid descriptor enumeration count')
        require(type(maximum) is int and maximum >= 0, 'invalid descriptor capture budget')
        self.count, self.maximum = count, maximum
        self.entries, self.used = [], 0
        self.previous = None
        self.complete = False

    def append(self, packet):
        require(not self.complete and type(packet) is dict
                and set(packet) == {'state', 'index', 'number', 'linkBytes'}
                and packet['state'] == 'entry' and type(packet['index']) is int
                and packet['index'] == len(self.entries) < self.count,
                'descriptor entry is missing, repeated or out of order')
        number = packet['number']
        require(type(number) is str and number.isascii() and number.isdigit()
                and str(int(number)) == number
                and (self.previous is None or int(number) > self.previous),
                'descriptor number is malformed, repeated or out of order')
        link = decode_raw(packet['linkBytes'])
        require(link and b'\0' not in link, 'descriptor link is empty or malformed')
        self.used += len(number.encode('ascii')) + len(link)
        require(self.used <= self.maximum, 'descriptor raw capture limit exceeded')
        self.entries.append({'number': number, 'linkBytes': packet['linkBytes']})
        self.previous = int(number)

    def finish(self, count):
        require(not self.complete and type(count) is int
                and count == self.count == len(self.entries),
                'descriptor enumeration did not complete exactly once')
        self.complete = True


def validate_descriptor_observation(first, observation, inventory, *, identity,
                                    process_object, pidfd_object, pidfd,
                                    before_namespace, namespace, maximum):
    """Bind retained reader bytes to the daemon's independently held objects."""
    require(type(first) is dict and type(observation) is dict
            and observation.get('schemaVersion') == 1
            and observation.get('producer') == 'daemon-owned-descriptor-reader'
            and observation.get('exception') is None
            and observation.get('enumerationReturned') is True
            and observation.get('inventoryComplete') is True and inventory.complete
            and observation.get('entryCount') == inventory.count,
            'descriptor reader did not complete its inventory')
    require(all(observation.get(key) == first.get(key) for key in (
        'schemaVersion', 'producer', 'beforeNamespace', 'requestedNamespace',
        'readerNamespace', 'subjectProc', 'subjectPidfd', 'subjectIdentity',
        'directory', 'entryCount', 'enumerationReturned')),
        'descriptor reader changed its initial binding')
    require(same_object(observation['beforeNamespace'], before_namespace),
            'descriptor reader started in another namespace')
    for key in ('requestedNamespace', 'readerNamespace', 'afterNamespace'):
        require(same_object(observation[key], namespace),
                'descriptor reader reported another namespace')
    require(same_object(observation['subjectProc'], process_object)
            and same_object(observation['subjectPidfd'], pidfd_object)
            and observation['subjectIdentity'] == identity
            and observation['subjectIdentityAfter'] == identity,
            'descriptor reader observed another process instance')
    reads = observation.get('reads')
    require(type(reads) is list and all(type(item) is dict
        and item.get('returned') is True and item.get('eof') is True
        and item.get('exception') is None for item in reads),
        'descriptor reader has incomplete raw reads')
    pidfd_path = '/proc/self/fdinfo/' + str(pidfd)
    require([item.get('path') for item in reads] ==
            ['/proc/self/status', 'stat', pidfd_path, 'stat', pidfd_path],
            'descriptor reader raw read roster differs')
    require(first.get('reads') == reads[:3]
            and first.get('subjectLiveness') == [{'phase': 'before', 'pidfdReady': False}],
            'descriptor reader changed its initial raw observations')
    raw_reads = [decode_raw(item.get('bytes')) for item in reads]
    require(process_identity(raw_reads[1]) == identity
            and process_identity(raw_reads[3]) == identity
            and all(parse_fields(raw_reads[index]).get(b'Pid') == str(identity['pid']).encode()
                    for index in (2, 4)),
            'descriptor reader identity does not match its raw reads')
    capabilities = parse_fields(raw_reads[0]).get(b'CapEff', b'')
    require(capabilities and all(character in b'0123456789abcdefABCDEF' for character in capabilities)
            and int(capabilities, 16) & (1 << 2),
            'descriptor reader raw status lacks namespace DAC capability')
    require(observation.get('subjectLiveness') == [
        {'phase': 'before', 'pidfdReady': False}, {'phase': 'after', 'pidfdReady': False}],
        'descriptor subject liveness is incomplete')
    raw_used = sum(len(value) for value in raw_reads) + inventory.used
    require(type(observation.get('rawBytesUsed')) is int
            and observation['rawBytesUsed'] == raw_used <= maximum,
            'descriptor raw capture budget or accounting differs')
    return raw_used


def finish_process(process, record, deadline, *, maximum_output, kill=False, cleanup_seconds=20):
    """Own the child through wait and binary EOF, retaining both failure attempts."""
    row = {'pid': process.pid, 'killed': False, 'attempts': [], 'returncode': None}
    record.setdefault('processCleanup', []).append(row)
    primary = None
    buffers = {'stdout': bytearray(), 'stderr': bytearray()}
    reached_eof = {'stdout': False, 'stderr': False}
    limited = set()
    try:
        if kill and process.poll() is None:
            process.kill()
            row['killed'] = True
        for cleanup in (False, True):
            attempt = {'cleanup': cleanup, 'stdout': None, 'stderr': None,
                       'eof': False, 'waitReturned': False, 'exception': None}
            row['attempts'].append(attempt)
            try:
                drain_deadline = time.monotonic() + cleanup_seconds if cleanup or kill else deadline
                with selectors.DefaultSelector() as selector:
                    for name in buffers:
                        stream = getattr(process, name)
                        if stream is None or stream.closed:
                            require(kill or cleanup, 'namespace helper pipe closed before completion')
                            continue
                        if not reached_eof[name] and name not in limited:
                            selector.register(stream, selectors.EVENT_READ, name)
                    while selector.get_map():
                        for key, _events in selector.select(timeout=min(0.1, remaining(drain_deadline))):
                            name = key.data
                            chunk = os.read(key.fileobj.fileno(),
                                            min(65536, maximum_output - len(buffers[name]) + 1))
                            buffers[name].extend(chunk)
                            if len(buffers[name]) > maximum_output:
                                limited.add(name)
                                raise NamespaceRestrictionFailure('namespace helper exceeded original output cap')
                            if not chunk:
                                reached_eof[name] = True
                                selector.unregister(key.fileobj)
                returned = process.wait(timeout=remaining(drain_deadline))
                attempt.update(waitReturned=True, returncode=returned)
                row['returncode'] = process.returncode
                break
            except BaseException as error:
                attempt['exception'] = failure(error)
                if primary is None:
                    primary = error
                else:
                    primary.add_note('owned namespace child cleanup also failed: ' + str(error))
                if process.poll() is None:
                    process.kill()
                    row['killed'] = True
            finally:
                attempt.update(stdout=raw(buffers['stdout']), stderr=raw(buffers['stderr']),
                               eof=all(reached_eof.values()), streamEof=dict(reached_eof),
                               outputCapExceeded=sorted(limited))
        if primary is not None:
            raise primary
        return row['returncode']
    finally:
        for stream in (process.stdin, process.stdout, process.stderr):
            if stream is not None:
                stream.close()


class NamespaceLease:
    """Bootstrap-owned N2 FD; the seed is reaped before any role starts."""
    def __init__(self, *, argv, run_id, expected_parent, deadline, maximum,
                 maximum_request, maximum_output):
        self.argv, self.deadline = tuple(argv), deadline
        self.expected_parent = expected_parent
        self.maximum, self.maximum_request = maximum, maximum_request
        self.maximum_output = maximum_output
        self.descriptor = None
        self.lock = threading.Lock()
        self.record = {'schemaVersion': 1, 'kind': 'namespace-lifetime-setup',
                       'producer': 'mapped-bootstrap', 'runId': run_id,
                       'reads': [], 'writes': [], 'exception': None,
                       'namespaceDescriptorClosed': False}

    def create(self):
        capture = Capture(self.record, self.deadline, self.maximum)
        parent_fd = child_proc = child_pidfd = None
        channel = peer = process = None
        try:
            require(os.geteuid() == 0 and os.getegid() == 0, 'namespace bootstrap is not mapped root')
            parent_fd = os.open('/proc/self/ns/user', os.O_RDONLY | os.O_CLOEXEC)
            self.record['parentNamespace'] = object_identity(os.fstat(parent_fd))
            # N1 cannot ask NS_GET_PARENT for N0 outside its namespace scope.
            # Check that this write cannot affect daemon N0; the daemon itself
            # independently proves the exact N1 -> N0 relation before role GO.
            self.record['expectedDaemonNamespace'] = dict(self.expected_parent)
            require(not same_object(self.record['parentNamespace'], self.expected_parent),
                    'namespace restriction would affect the daemon namespace')
            self.record['currentNamespaceDiffersFromDaemon'] = True
            status = parse_fields(capture.read('/proc/self/status'))
            capabilities = int(status[b'CapEff'], 16)
            needed = {'CAP_SETGID': 6, 'CAP_SETUID': 7,
                      'CAP_SYS_RESOURCE': 24, 'CAP_SETFCAP': 31}
            self.record['requiredCapabilities'] = needed
            require(all(capabilities & (1 << bit) for bit in needed.values()),
                    'mapped bootstrap lacks namespace setup capabilities')
            maps = {name: identity_projection(capture.read('/proc/self/' + name))
                    for name in ('uid_map', 'gid_map')}
            require(capture.read('/proc/self/setgroups').strip() == b'allow',
                    'original group clearing is unavailable')
            channel, peer = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
            arguments = (*self.argv, '--seed', str(peer.fileno()), str(self.deadline),
                         str(self.maximum_request), str(self.maximum))
            self.record['seedCommand'] = list(arguments)
            process = subprocess.Popen(arguments, pass_fds=(peer.fileno(),), close_fds=True,
                                       stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            self.record['seedPid'] = process.pid
            child_pidfd = os.pidfd_open(process.pid)
            child_proc = os.open('/proc/' + str(process.pid), _DIR)
            peer.close()
            peer = None
            reply = receive_packet(channel, self.deadline, self.maximum_request, self.record)
            require(isinstance(reply, dict) and reply.get('state') == 'unshared',
                    'namespace seed did not create its child namespace')
            require(not select.select([child_pidfd], [], [], 0)[0], 'namespace seed exited before mapping')
            identity = process_identity(capture.read('stat', parent=child_proc))
            require(identity['pid'] == process.pid and identity['ppid'] == os.getpid(),
                    'namespace seed identity/parent differs')
            self.record['seedIdentity'] = identity
            self.descriptor = os.open('ns/user', os.O_RDONLY | os.O_CLOEXEC, dir_fd=child_proc)
            self.record['childNamespace'] = object_identity(os.fstat(self.descriptor))
            require(fcntl.ioctl(self.descriptor, NS_GET_NSTYPE) == CLONE_NEWUSER,
                    'namespace seed descriptor has another type')
            actual_parent = fcntl.ioctl(self.descriptor, NS_GET_PARENT)
            try:
                require(same_object(object_identity(os.fstat(actual_parent)),
                                    self.record['parentNamespace']), 'namespace seed has another parent')
            finally:
                os.close(actual_parent)
            require(capture.read('setgroups', parent=child_proc).strip() == b'allow',
                    'namespace seed cannot preserve group clearing')
            for name, payload in maps.items():
                capture.write(name, payload, parent=child_proc)
                require(map_rows(capture.read(name, parent=child_proc)) == map_rows(payload),
                        'namespace seed full mapping differs from intended identity map')
            capture.read(_QUOTA)
            capture.write(_QUOTA, b'0\n')
            require(capture.read(_QUOTA).strip() == b'0', 'parent namespace quota was not restricted')
            require(not select.select([child_pidfd], [], [], 0)[0]
                    and process_identity(capture.read('stat', parent=child_proc)) == identity,
                    'namespace seed changed during mapping')
            verify = os.open('ns/user', os.O_RDONLY | os.O_CLOEXEC, dir_fd=child_proc)
            try:
                require(same_object(object_identity(os.fstat(verify)), self.record['childNamespace']),
                        'namespace seed changed namespaces during mapping')
            finally:
                os.close(verify)
            send_packet(channel, {'state': 'mapped'}, self.deadline, self.maximum_request, self.record)
            result = finish_process(process, self.record, self.deadline,
                                    maximum_output=self.maximum_output)
            process = None
            require(result == 0, 'namespace seed failed its owned completion')
            self.record['ready'] = True
            return self.descriptor
        except BaseException as error:
            self.record['exception'] = failure(error)
            raise
        finally:
            primary = sys.exception()
            if process is not None:
                try:
                    finish_process(process, self.record, self.deadline, kill=True,
                                   maximum_output=self.maximum_output)
                except BaseException as error:
                    self.record['cleanupException'] = failure(error)
                    if primary is not None:
                        primary.add_note('namespace seed cleanup also failed: ' + str(error))
                    else:
                        raise
            for owned in (channel, peer):
                if owned is not None:
                    owned.close()
            for descriptor in (parent_fd, child_proc, child_pidfd):
                if descriptor is not None:
                    os.close(descriptor)

    def spawn_role(self, command, *, deadline, **options):
        """Hold ownership until Popen has inherited its own namespace reference."""
        row = {'descriptor': None, 'command': list(command),
               'spawnReturned': False, 'exception': None}
        acquired = self.lock.acquire(timeout=remaining(deadline))
        require(acquired, 'namespace descriptor borrower did not become available')
        try:
            row['descriptor'] = self.descriptor
            self.record.setdefault('roleBorrows', []).append(row)
            require(self.descriptor is not None, 'namespace descriptor lease is closed')
            require(len(command) > 3 and tuple(command[1:3]) == ('--userns', str(self.descriptor))
                    and command[-1] == str(self.descriptor), 'role command differs from owned descriptor')
            process = subprocess.Popen(command, pass_fds=(self.descriptor,), close_fds=True, **options)
            row.update(spawnReturned=True, pid=process.pid)
            return process
        except BaseException as error:
            row['exception'] = failure(error)
            raise
        finally:
            self.lock.release()

    def close(self, *, timeout=20):
        acquired = self.lock.acquire(timeout=timeout)
        if not acquired:
            self.record['namespaceDescriptorCloseIncomplete'] = True
            raise NamespaceRestrictionFailure('namespace descriptor borrower is still active')
        try:
            if self.descriptor is not None:
                descriptor, self.descriptor = self.descriptor, None
                try:
                    os.close(descriptor)
                    self.record['namespaceDescriptorClosed'] = True
                except BaseException as error:
                    self.record['namespaceDescriptorCloseException'] = failure(error)
                    raise
        finally:
            self.lock.release()


def close_role_descriptor(descriptor):
    require(type(descriptor) is int and descriptor > 2, 'missing role namespace descriptor')
    try:
        require(fcntl.ioctl(descriptor, NS_GET_NSTYPE) == CLONE_NEWUSER,
                'inherited role descriptor is not a user namespace')
        require(same_object(object_identity(os.fstat(descriptor)),
                            object_identity(os.stat('/proc/self/ns/user'))),
                'inherited role namespace differs from current namespace')
    finally:
        os.close(descriptor)


def _seed(channel, deadline, maximum_request, maximum):
    record = {'producer': 'trusted-namespace-seed', 'reads': [], 'exception': None}
    try:
        os.unshare(CLONE_NEWUSER)
        send_packet(channel, {'state': 'unshared'}, deadline, maximum_request, record)
        require(receive_packet(channel, deadline, maximum_request, record) == {'state': 'mapped'},
                'namespace seed mapping was not acknowledged')
        capture = Capture(record, deadline, maximum)
        for name in ('uid_map', 'gid_map'):
            map_rows(capture.read('/proc/self/' + name))
        record['complete'] = True
        return 0
    except BaseException as error:
        record['exception'] = failure(error)
        try:
            send_packet(channel, {'state': 'failed', 'observation': record},
                        deadline, maximum_request, {})
        except BaseException as secondary:
            record['failureSendException'] = failure(secondary)
        return 1
    finally:
        print(json.dumps(record, sort_keys=True), flush=True)


def _quota_reader(channel, namespace_fd, deadline, maximum_request, maximum):
    record = {'schemaVersion': 1, 'producer': 'daemon-owned-namespace-quota-reader',
              'reads': [], 'exception': None, 'confinementEstablished': False}
    try:
        record['beforeNamespace'] = object_identity(os.stat('/proc/self/ns/user'))
        require(fcntl.ioctl(namespace_fd, NS_GET_NSTYPE) == CLONE_NEWUSER,
                'quota reader received another namespace type')
        record['requestedNamespace'] = object_identity(os.fstat(namespace_fd))
        os.setns(namespace_fd, CLONE_NEWUSER)
        os.close(namespace_fd)
        namespace_fd = None
        record['readerNamespace'] = object_identity(os.stat('/proc/self/ns/user'))
        require(same_object(record['readerNamespace'], record['requestedNamespace']),
                'quota reader namespace differs')
        capture = Capture(record, deadline, maximum)
        capture.read('/proc/self/stat')
        capture.read('/proc/self/status')
        payload = capture.read(_QUOTA)
        record['afterNamespace'] = object_identity(os.stat('/proc/self/ns/user'))
        require(same_object(record['afterNamespace'], record['readerNamespace']),
                'quota reader namespace changed')
        record['quotaBytes'] = raw(payload)
        send_packet(channel, {'state': 'observed', 'observation': record},
                    deadline, maximum_request, {})
        require(receive_packet(channel, deadline, maximum_request, record) == {'state': 'retained'},
                'quota reader observation was not retained')
        return 0
    except BaseException as error:
        record['exception'] = failure(error)
        try:
            send_packet(channel, {'state': 'failed', 'observation': record},
                        deadline, maximum_request, {})
        except BaseException as secondary:
            record['failureSendException'] = failure(secondary)
        return 1
    finally:
        if namespace_fd is not None:
            os.close(namespace_fd)
        print(json.dumps(record, sort_keys=True), flush=True)


def _descriptor_reader(channel, namespace_fd, process_fd, pidfd,
                       deadline, maximum_request, maximum):
    record = {'schemaVersion': 1, 'producer': 'daemon-owned-descriptor-reader',
              'reads': [], 'exception': None, 'confinementEstablished': False}
    directory = None
    transport = {}
    capture = None
    returned = 1
    failed_transport = None

    def send(value):
        # The daemon retains every received packet. Keep the currently attempted
        # send locally so a failed transport also survives in the owned stderr.
        transport.clear()
        send_packet(channel, value, deadline, maximum_request, transport)

    def live(capture, phase):
        ready = bool(select.select([pidfd], [], [], 0)[0])
        record.setdefault('subjectLiveness', []).append({'phase': phase, 'pidfdReady': ready})
        require(not ready, 'descriptor subject exited')
        fields = parse_fields(capture.read('/proc/self/fdinfo/' + str(pidfd)))
        require(fields.get(b'Pid') == str(record['subjectIdentity']['pid']).encode(),
                'descriptor subject pidfd differs from held proc directory')

    try:
        record['beforeNamespace'] = object_identity(os.stat('/proc/self/ns/user'))
        require(fcntl.ioctl(namespace_fd, NS_GET_NSTYPE) == CLONE_NEWUSER,
                'descriptor reader received another namespace type')
        record['requestedNamespace'] = object_identity(os.fstat(namespace_fd))
        os.setns(namespace_fd, CLONE_NEWUSER)
        os.close(namespace_fd)
        namespace_fd = None
        record['readerNamespace'] = object_identity(os.stat('/proc/self/ns/user'))
        require(same_object(record['requestedNamespace'], record['readerNamespace']),
                'descriptor reader entered another namespace')
        capture = Capture(record, deadline, maximum)
        status = parse_fields(capture.read('/proc/self/status'))
        # linux/capability.h: effective CAP_DAC_READ_SEARCH is 2. The full
        # mapping and actual reader credentials are also checked by the daemon.
        require(int(status[b'CapEff'], 16) & (1 << 2),
                'descriptor reader lacks namespace DAC read/search capability')
        record['subjectProc'] = object_identity(os.fstat(process_fd))
        record['subjectPidfd'] = object_identity(os.fstat(pidfd))
        record['subjectIdentity'] = process_identity(capture.read('stat', parent=process_fd))
        live(capture, 'before')
        remaining(deadline)
        directory = os.open('fd', _DIR, dir_fd=process_fd)
        record['directory'] = object_identity(os.fstat(directory))
        names = sorted(os.listdir(directory), key=int)
        record['enumerationReturned'] = True
        record['entryCount'] = len(names)
        send({'state': 'begin', 'observation': record})
        for index, number in enumerate(names):
            remaining(deadline)
            require(number.isascii() and number.isdigit() and str(int(number)) == number,
                    'kernel descriptor name is malformed')
            entry = {'state': 'entry', 'index': index, 'number': number, 'linkBytes': None}
            record['pendingEntry'] = entry
            link = os.readlink(os.fsencode(number), dir_fd=directory)
            entry['linkBytes'] = raw(link)
            capture.used += len(number.encode('ascii')) + len(link)
            require(capture.used <= maximum, 'descriptor raw capture limit exceeded')
            send(entry)
            record.pop('pendingEntry')
        record['subjectIdentityAfter'] = process_identity(capture.read('stat', parent=process_fd))
        require(record['subjectIdentityAfter'] == record['subjectIdentity'],
                'descriptor subject identity changed')
        live(capture, 'after')
        record['afterNamespace'] = object_identity(os.stat('/proc/self/ns/user'))
        require(same_object(record['afterNamespace'], record['readerNamespace']),
                'descriptor reader namespace changed')
        record['rawBytesUsed'] = capture.used
        record['inventoryComplete'] = True
        send({'state': 'observed', 'observation': record})
        require(receive_packet(channel, deadline, maximum_request, {}) == {'state': 'retained'},
                'descriptor observation was not retained')
        returned = 0
    except BaseException as error:
        record['exception'] = failure(error)
        if capture is not None:
            record['rawBytesUsed'] = capture.used
        failed_transport = dict(transport)
        try:
            send({'state': 'failed', 'observation': record})
        except BaseException as secondary:
            record['failureSendException'] = failure(secondary)
    finally:
        for descriptor in (directory, namespace_fd, process_fd, pidfd):
            if descriptor is not None:
                try:
                    os.close(descriptor)
                except BaseException as error:
                    record.setdefault('closeExceptions', []).append(
                        {'descriptor': descriptor, 'exception': failure(error)})
                    returned = 1
        if returned:
            # No full inventory is copied to capped stdout. Actual successful
            # entry packets are already retained by the daemon.
            print(json.dumps({'observation': record, 'failedTransport': failed_transport,
                              'lastTransport': transport}, sort_keys=True), file=sys.stderr, flush=True)
    return returned


if __name__ == '__main__':
    if len(sys.argv) == 6 and sys.argv[1] == '--seed':
        with socket.socket(fileno=int(sys.argv[2])) as connection:
            raise SystemExit(_seed(connection, float(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])))
    elif len(sys.argv) == 7 and sys.argv[1] == '--quota-reader':
        with socket.socket(fileno=int(sys.argv[2])) as connection:
            raise SystemExit(_quota_reader(connection, int(sys.argv[3]), float(sys.argv[4]),
                                           int(sys.argv[5]), int(sys.argv[6])))
    elif sys.argv[1:2] == ['--descriptor-reader']:
        channel_fd, namespace_fd, process_fd, pidfd, deadline, request_cap, capture_cap = sys.argv[2:]
        with socket.socket(fileno=int(channel_fd)) as connection:
            raise SystemExit(_descriptor_reader(connection, int(namespace_fd), int(process_fd),
                                                int(pidfd), float(deadline),
                                                int(request_cap), int(capture_cap)))
    raise SystemExit('invalid namespace policy invocation')
