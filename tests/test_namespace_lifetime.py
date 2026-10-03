"""Additive defensive namespace controls; no promotion or proof acceptance."""
from __future__ import annotations

import base64
import copy
import errno
import fcntl
import hashlib
import json
import os
from pathlib import Path
import socket
import stat
import subprocess
import tempfile
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import uuid

from worldline.linux.namespace_lifetime import (
    Capture, DescriptorInventory, NamespaceLease, NamespaceRestrictionFailure,
    close_role_descriptor, finish_process, identity_projection, map_rows,
    object_identity, raw, receive_packet, validate_descriptor_observation,
)
from worldline.trusted import trusted_inline, trusted_script, TRUSTED_INTERPRETER


def decoded(value):
    return base64.b64decode(value['payload'], validate=True)


class CompleteIdentityMaps(unittest.TestCase):
    def test_projection_keeps_every_sparse_range_and_all_subordinate_ids(self):
        parent = b'0 1000 1\n1 100000 65535\n90000 300000 4000\n'
        projected = identity_projection(parent)
        self.assertEqual(projected, b'0 0 1\n1 1 65535\n90000 90000 4000\n')
        self.assertEqual(map_rows(projected), ((0, 0, 1), (1, 1, 65535), (90000, 90000, 4000)))
        self.assertEqual(parent, b'0 1000 1\n1 100000 65535\n90000 300000 4000\n')

    def test_empty_overlap_zero_overflow_and_malformed_maps_refuse(self):
        for payload in (b'', b'0 0 0\n', b'0 10 3\n2 20 2\n', b'0 10 3\n8 11 1\n',
                        b'-1 0 1\n', b'0 x 1\n', b'4294967295 0 1\n',
                        b'0 4294967295 1\n', b'0 0 1 trailing\n'):
            with self.subTest(payload=payload), self.assertRaises(NamespaceRestrictionFailure):
                identity_projection(payload)

    def test_self_view_identity_is_distinct_from_receiver_view(self):
        parent = b'0 1000 1\n1 100000 65535\n'
        self.assertNotEqual(map_rows(parent), map_rows(identity_projection(parent)))
        # The complete projected domain is preserved; raw parent evidence is not rewritten.
        self.assertEqual([(inside, count) for inside, _, count in map_rows(parent)],
                         [(inside, count) for inside, _, count in map_rows(identity_projection(parent))])


class OwnedNamespaceIO(unittest.TestCase):
    def test_daemon_namespace_is_rejected_before_any_write_or_seed(self):
        lease = NamespaceLease(argv=('unused-seed',), run_id='owned-negative',
            expected_parent=object_identity(os.stat('/proc/self/ns/user')),
            deadline=time.monotonic() + 60, maximum=65536,
            maximum_request=65536, maximum_output=65536)
        # Only the mapped-root precondition is supplied. The actual held kernel
        # namespace is unchanged, and comparison must reject before any write.
        with patch('worldline.linux.namespace_lifetime.os.geteuid', return_value=0), \
             patch('worldline.linux.namespace_lifetime.os.getegid', return_value=0):
            with self.assertRaisesRegex(NamespaceRestrictionFailure, 'daemon namespace'):
                lease.create()
        self.assertEqual(lease.record['writes'], [])
        self.assertNotIn('seedPid', lease.record)
        self.assertIsNone(lease.descriptor)

    def test_full_read_and_limit_refusal_keep_actual_bytes_and_eof_separate(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'raw'
            payload = b'namespace\x00\xff\r\n'
            path.write_bytes(payload)
            record = {}
            capture = Capture(record, time.monotonic() + 60, len(payload))
            self.assertEqual(capture.read(str(path)), payload)
            self.assertTrue(record['reads'][0]['returned'])
            self.assertTrue(record['reads'][0]['eof'])
            self.assertEqual(decoded(record['reads'][0]['bytes']), payload)
            refused = {}
            with self.assertRaises(NamespaceRestrictionFailure):
                Capture(refused, time.monotonic() + 60, 1).read(str(path))
            self.assertFalse(refused['reads'][0]['returned'])
            self.assertFalse(refused['reads'][0]['eof'])
            self.assertTrue(decoded(refused['reads'][0]['bytes']))
            self.assertIsNotNone(refused['reads'][0]['exception'])

    def test_failed_open_retains_errno_and_no_fabricated_eof(self):
        with tempfile.TemporaryDirectory() as directory:
            record = {}
            with self.assertRaises(FileNotFoundError):
                Capture(record, time.monotonic() + 60, 65536).read(str(Path(directory) / 'missing'))
            row = record['reads'][0]
            self.assertEqual(row['exception']['nodes'][0]['errno'], errno.ENOENT)
            self.assertFalse(row['eof'])
            self.assertFalse(row['returned'])

    def test_duplicate_or_oversize_control_packet_is_not_a_valid_reply(self):
        for payload, limit in ((b'{"state":"observed","state":"failed"}', 65536),
                               (b'{"state":"observed"}', 1)):
            with self.subTest(payload=payload), _pair() as pair:
                receiving, sending = pair
                sending.send(payload)
                record = {}
                with self.assertRaises(NamespaceRestrictionFailure):
                    receive_packet(receiving, time.monotonic() + 60, limit, record)
                self.assertIsNotNone(record['packets'][0]['bytes'])
                self.assertIsNotNone(record['packets'][0]['exception'])

    def test_role_handle_is_validated_and_closed_before_return(self):
        descriptor = os.open('/proc/self/ns/user', os.O_RDONLY | os.O_CLOEXEC)
        close_role_descriptor(descriptor)
        with self.assertRaises(OSError) as raised:
            fcntl.fcntl(descriptor, fcntl.F_GETFD)
        self.assertEqual(raised.exception.errno, errno.EBADF)

    def test_wrong_role_handle_is_closed_and_refused(self):
        with tempfile.TemporaryFile() as stream:
            descriptor = os.dup(stream.fileno())
            with self.assertRaises(OSError):
                close_role_descriptor(descriptor)
            with self.assertRaises(OSError) as raised:
                fcntl.fcntl(descriptor, fcntl.F_GETFD)
            self.assertEqual(raised.exception.errno, errno.EBADF)

    def test_owned_child_binary_output_and_wait_are_retained(self):
        process = subprocess.Popen(trusted_inline(
            'import os; os.write(1, bytes((0,255))); os.write(2,b"stderr\\n")'),
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        record = {}
        self.assertEqual(finish_process(process, record, time.monotonic() + 60,
                                        maximum_output=65536), 0)
        row = record['processCleanup'][0]['attempts'][0]
        self.assertEqual(decoded(row['stdout']), b'\x00\xff')
        self.assertEqual(decoded(row['stderr']), b'stderr\n')
        self.assertTrue(row['eof'])
        self.assertTrue(row['waitReturned'])

    def test_owned_output_limit_keeps_failure_even_after_successful_wait(self):
        process = subprocess.Popen(trusted_inline('import os; os.write(1,b"over-cap")'),
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        record = {}
        with self.assertRaises(NamespaceRestrictionFailure):
            finish_process(process, record, time.monotonic() + 60, maximum_output=1)
        self.assertIsNotNone(process.returncode)
        first = record['processCleanup'][0]['attempts'][0]
        self.assertEqual(first['outputCapExceeded'], ['stdout'])
        self.assertFalse(first['eof'])
        self.assertEqual(decoded(first['stdout']), b'ov')
        self.assertIsNotNone(first['exception'])


class _pair:
    def __enter__(self):
        self.pair = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        return self.pair

    def __exit__(self, *_exception):
        for endpoint in self.pair:
            endpoint.close()


class DescriptorReaderProtocol(unittest.TestCase):
    @staticmethod
    def entry(index, number, link):
        return {'state': 'entry', 'index': index, 'number': number, 'linkBytes': raw(link)}

    def test_complete_inventory_preserves_binary_links_and_requires_one_end(self):
        packets = [self.entry(0, '0', b'/dev/null'),
                   self.entry(1, '7', b'/owned/name with spaces\xff (deleted)')]
        limit = sum(len(row['number']) + len(decoded(row['linkBytes'])) for row in packets)
        inventory = DescriptorInventory(len(packets), limit)
        for row in packets:
            inventory.append(row)
        inventory.finish(len(packets))
        self.assertTrue(inventory.complete)
        self.assertEqual(inventory.used, limit)
        self.assertEqual(inventory.entries, [
            {'number': row['number'], 'linkBytes': row['linkBytes']} for row in packets])
        with self.assertRaises(NamespaceRestrictionFailure):
            inventory.finish(len(packets))
        with self.assertRaises(NamespaceRestrictionFailure):
            inventory.append(self.entry(2, '8', b'/extra'))

    def test_missing_repeated_reordered_or_malformed_entries_refuse(self):
        for packet in (self.entry(0, '7', b'/duplicate-index'),
                       self.entry(2, '8', b'/missing-index'),
                       self.entry(True, '8', b'/boolean-index'),
                       self.entry(1, '7', b'/duplicate-number'),
                       self.entry(1, '6', b'/decreasing-number'),
                       self.entry(1, '08', b'/noncanonical-number'),
                       self.entry(1, '\u0668', b'/non-ascii-number'),
                       self.entry(1, '8', b''), self.entry(1, '8', b'bad\x00link')):
            with self.subTest(packet=packet):
                inventory = DescriptorInventory(2, 65536)
                inventory.append(self.entry(0, '7', b'/first'))
                with self.assertRaises(NamespaceRestrictionFailure):
                    inventory.append(packet)
                self.assertFalse(inventory.complete)
        inventory = DescriptorInventory(2, 65536)
        inventory.append(self.entry(0, '7', b'/first'))
        with self.assertRaises(NamespaceRestrictionFailure):
            inventory.finish(2)
        self.assertFalse(inventory.complete)

    def test_capture_limit_and_raw_envelope_cannot_be_bypassed(self):
        packet = self.entry(0, '0', b'/dev/null')
        inventory = DescriptorInventory(1, len(b'/dev/null'))
        with self.assertRaises(NamespaceRestrictionFailure):
            inventory.append(packet)
        self.assertFalse(inventory.complete)
        for envelope in ({'encoding': 'utf8', 'payload': '/dev/null'},
                         {'encoding': 'base64', 'payload': '!!!!'},
                         {**raw(b'/dev/null'), 'extra': True}):
            with self.subTest(envelope=envelope), self.assertRaises(ValueError):
                DescriptorInventory(1, 65536).append({**packet, 'linkBytes': envelope})
        for count in (True, -1, '1'):
            with self.subTest(count=count), self.assertRaises(NamespaceRestrictionFailure):
                DescriptorInventory(count, 65536)
        empty = DescriptorInventory(0, 0)
        empty.finish(0)
        self.assertTrue(empty.complete)

    @staticmethod
    def fixture():
        # Synthetic protocol facts, never a kernel/namespace acceptance receipt.
        identity = {'pid': 123, 'ppid': 45, 'starttime': 678}
        fields = ['0'] * 20
        fields[0], fields[1], fields[19] = 'S', str(identity['ppid']), str(identity['starttime'])
        proc_stat = (str(identity['pid']) + ' (fixture comm) ' + ' '.join(fields)).encode()
        pidfd = 9
        proc = {'device': 1, 'inode': 2, 'mode': stat.S_IFDIR | 0o555}
        pid_object = {'device': 1, 'inode': 3, 'mode': stat.S_IFREG | 0o600}
        before = {'device': 2, 'inode': 4, 'mode': stat.S_IFREG | 0o444}
        namespace = {'device': 2, 'inode': 5, 'mode': stat.S_IFREG | 0o444}
        reads = [{'path': name, 'bytes': raw(value), 'returned': True, 'eof': True,
                  'exception': None} for name, value in (
            ('/proc/self/status', b'CapEff:\t0000000000000004\n'),
            ('stat', proc_stat), ('/proc/self/fdinfo/9', b'Pid:\t123\n'),
            ('stat', proc_stat), ('/proc/self/fdinfo/9', b'Pid:\t123\n'))]
        inventory = DescriptorInventory(1, 65536)
        inventory.append(DescriptorReaderProtocol.entry(0, '0', b'/dev/null'))
        inventory.finish(1)
        last = {'schemaVersion': 1, 'producer': 'daemon-owned-descriptor-reader',
                'exception': None, 'enumerationReturned': True, 'inventoryComplete': True,
                'entryCount': 1, 'beforeNamespace': before, 'requestedNamespace': namespace,
                'readerNamespace': namespace, 'afterNamespace': namespace,
                'subjectProc': proc, 'subjectPidfd': pid_object, 'subjectIdentity': identity,
                'subjectIdentityAfter': identity, 'directory': proc, 'reads': reads,
                'subjectLiveness': [{'phase': 'before', 'pidfdReady': False},
                                    {'phase': 'after', 'pidfdReady': False}],
                'rawBytesUsed': sum(len(decoded(item['bytes'])) for item in reads) + inventory.used}
        first = copy.deepcopy(last)
        first['reads'] = first['reads'][:3]
        first['subjectLiveness'] = first['subjectLiveness'][:1]
        for key in ('inventoryComplete', 'afterNamespace', 'subjectIdentityAfter', 'rawBytesUsed'):
            first.pop(key)
        expected = {'identity': copy.deepcopy(identity), 'process_object': copy.deepcopy(proc),
                    'pidfd_object': copy.deepcopy(pid_object), 'pidfd': pidfd,
                    'before_namespace': copy.deepcopy(before), 'namespace': copy.deepcopy(namespace),
                    'maximum': 65536}
        return first, last, inventory, expected

    def test_complete_observation_binds_raw_identity_objects_and_initial_reads(self):
        first, last, inventory, expected = self.fixture()
        self.assertEqual(validate_descriptor_observation(first, last, inventory, **expected),
                         last['rawBytesUsed'])
        expected['maximum'] = last['rawBytesUsed']
        self.assertEqual(validate_descriptor_observation(first, last, inventory, **expected),
                         last['rawBytesUsed'])
        expected['maximum'] -= 1
        with self.assertRaises(NamespaceRestrictionFailure):
            validate_descriptor_observation(first, last, inventory, **expected)

    def test_changed_process_namespace_or_held_object_refuses(self):
        for key, field in (('subjectIdentityAfter', 'pid'), ('subjectIdentityAfter', 'ppid'),
                           ('subjectIdentityAfter', 'starttime'), ('subjectProc', 'inode'),
                           ('subjectPidfd', 'inode'), ('beforeNamespace', 'inode'),
                           ('requestedNamespace', 'inode'), ('afterNamespace', 'inode')):
            with self.subTest(key=key, field=field):
                first, last, inventory, expected = self.fixture()
                last[key] = {**last[key], field: -1}
                if key in first:
                    first[key] = copy.deepcopy(last[key])
                with self.assertRaises(NamespaceRestrictionFailure):
                    validate_descriptor_observation(first, last, inventory, **expected)

    def test_missing_false_or_changed_raw_evidence_refuses(self):
        for change in ('eof', 'return', 'exception', 'roster', 'pidfd', 'stat',
                       'initial', 'dead', 'capability', 'budget', 'count'):
            with self.subTest(change=change):
                first, last, inventory, expected = self.fixture()
                if change == 'eof':
                    last['reads'][3]['eof'] = False
                elif change == 'return':
                    last['reads'][3]['returned'] = False
                elif change == 'exception':
                    last['reads'][3]['exception'] = {'message': 'incomplete read'}
                elif change == 'roster':
                    last['reads'].reverse()
                elif change == 'pidfd':
                    last['reads'][4]['bytes'] = raw(b'Pid:\t999\n')
                elif change == 'stat':
                    last['reads'][3]['bytes'] = raw(decoded(last['reads'][3]['bytes']).replace(b'123 (', b'999 ('))
                elif change == 'initial':
                    first['reads'][0]['bytes'] = raw(b'CapEff:\t0\n')
                elif change == 'dead':
                    last['subjectLiveness'][1]['pidfdReady'] = True
                elif change == 'capability':
                    first['reads'][0]['bytes'] = last['reads'][0]['bytes'] = raw(b'CapEff:\t0\n')
                elif change == 'budget':
                    last['rawBytesUsed'] += 1
                elif change == 'count':
                    first['entryCount'] = last['entryCount'] = 2
                with self.assertRaises(NamespaceRestrictionFailure):
                    validate_descriptor_observation(first, last, inventory, **expected)

    def test_failed_owned_reader_retains_errno_wait_and_binary_eof(self):
        # A regular file cannot be a namespace. This launches only the fixed
        # reader's refusal path; it neither enters nor creates any namespace.
        import worldline.linux.namespace_lifetime as policy
        with tempfile.TemporaryFile() as invalid_namespace, _pair() as pair:
            process_fd = os.open('/proc/self', os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
            pidfd = os.pidfd_open(os.getpid())
            process = None
            record = {}
            deadline = time.monotonic() + 60
            try:
                channel, peer = pair
                command = trusted_script(policy.__file__, '--descriptor-reader', str(peer.fileno()),
                    str(invalid_namespace.fileno()), str(process_fd), str(pidfd),
                    str(deadline), '65536', '65536')
                process = subprocess.Popen(command, close_fds=True,
                    pass_fds=(peer.fileno(), invalid_namespace.fileno(), process_fd, pidfd),
                    stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                peer.close()
                packet = receive_packet(channel, deadline, 65536, record)
                self.assertEqual(packet['state'], 'failed')
                self.assertEqual(packet['observation']['exception']['nodes'][0]['errno'], errno.ENOTTY)
                self.assertEqual(finish_process(process, record, deadline, maximum_output=65536), 1)
                self.assertIsNotNone(process.returncode)
                attempt = record['processCleanup'][0]['attempts'][0]
                self.assertTrue(attempt['waitReturned'])
                self.assertTrue(attempt['eof'])
                self.assertEqual(decoded(attempt['stdout']), b'')
                detail = json.loads(decoded(attempt['stderr']))
                self.assertEqual(detail['observation']['exception']['nodes'][0]['errno'], errno.ENOTTY)
                self.assertNotIn('inventoryComplete', detail['observation'])
            finally:
                if process is not None and process.poll() is None:
                    finish_process(process, record, deadline, kill=True, maximum_output=65536)
                os.close(process_fd)
                os.close(pidfd)


class NamespaceLeaseOwnership(unittest.TestCase):
    def setUp(self):
        self.lease = NamespaceLease(argv=('unused-seed',), run_id='owned-borrow',
            expected_parent={}, deadline=time.monotonic() + 60, maximum=65536,
            maximum_request=65536, maximum_output=65536)
        # Hold an existing namespace only: these ordering controls neither
        # create nor enter a namespace and never write namespace policy.
        self.lease.descriptor = os.open('/proc/self/ns/user', os.O_RDONLY | os.O_CLOEXEC)
        self.descriptor = self.lease.descriptor
        self.command = ('unused-bwrap', '--userns', str(self.descriptor),
                        '--', 'unused-role', str(self.descriptor))

    def tearDown(self):
        self.lease.close()

    def test_spawn_first_retains_parent_until_child_owns_reference(self):
        entered, release, closing = threading.Event(), threading.Event(), threading.Event()
        results, errors = {}, []

        def popen(command, **options):
            self.assertEqual(command, self.command)
            self.assertEqual(options['pass_fds'], (self.descriptor,))
            self.assertTrue(options['close_fds'])
            entered.set()
            if not release.wait(20):
                raise AssertionError('test did not release the owned spawn')
            # Model the Popen inheritance boundary with a real kernel reference.
            results['inherited'] = os.dup(self.descriptor)
            return SimpleNamespace(pid=os.getpid())

        def spawn():
            try:
                results['process'] = self.lease.spawn_role(
                    self.command, deadline=time.monotonic() + 60)
            except BaseException as error:
                errors.append(error)

        def close():
            closing.set()
            try:
                self.lease.close()
            except BaseException as error:
                errors.append(error)

        spawning = threading.Thread(target=spawn)
        closer = threading.Thread(target=close)
        try:
            with patch('worldline.linux.namespace_lifetime.subprocess.Popen', side_effect=popen) as launch:
                spawning.start()
                self.assertTrue(entered.wait(20))
                # A cleanup deadline while Popen owns the reference must refuse,
                # preserve the live descriptor, and retain incomplete cleanup.
                with self.assertRaisesRegex(NamespaceRestrictionFailure, 'borrower is still active'):
                    self.lease.close(timeout=0)
                self.assertTrue(self.lease.record['namespaceDescriptorCloseIncomplete'])
                self.assertEqual(self.lease.descriptor, self.descriptor)
                fcntl.fcntl(self.descriptor, fcntl.F_GETFD)
                closer.start()
                self.assertTrue(closing.wait(20))
                release.set()
                spawning.join(20)
                closer.join(20)
                self.assertFalse(spawning.is_alive())
                self.assertFalse(closer.is_alive())
                self.assertEqual(errors, [])
                launch.assert_called_once()
            self.assertIsNone(self.lease.descriptor)
            self.assertTrue(self.lease.record['namespaceDescriptorClosed'])
            self.assertTrue(self.lease.record['roleBorrows'][0]['spawnReturned'])
            fcntl.fcntl(results['inherited'], fcntl.F_GETFD)
            with self.assertRaises(OSError) as raised:
                fcntl.fcntl(self.descriptor, fcntl.F_GETFD)
            self.assertEqual(raised.exception.errno, errno.EBADF)
        finally:
            release.set()
            if spawning.ident is not None:
                spawning.join(20)
            if closer.ident is not None:
                closer.join(20)
            if 'inherited' in results:
                os.close(results['inherited'])

    def test_close_first_refuses_spawn_even_after_numeric_descriptor_reuse(self):
        self.lease.close()
        replacement = os.open('/dev/null', os.O_RDONLY | os.O_CLOEXEC)
        if replacement != self.descriptor:
            os.dup2(replacement, self.descriptor)
            os.close(replacement)
        try:
            replacement_identity = object_identity(os.fstat(self.descriptor))
            with patch('worldline.linux.namespace_lifetime.subprocess.Popen') as launch:
                with self.assertRaisesRegex(NamespaceRestrictionFailure, 'lease is closed'):
                    self.lease.spawn_role(self.command, deadline=time.monotonic() + 60)
                launch.assert_not_called()
            self.lease.close()
            self.assertEqual(object_identity(os.fstat(self.descriptor)), replacement_identity)
            self.assertFalse(self.lease.record['roleBorrows'][0]['spawnReturned'])
            self.assertIsNotNone(self.lease.record['roleBorrows'][0]['exception'])
        finally:
            os.close(self.descriptor)

    def test_spawn_error_releases_ownership_and_retains_original_error(self):
        with patch('worldline.linux.namespace_lifetime.subprocess.Popen',
                   side_effect=OSError(errno.ENOENT, 'owned launch failed')):
            with self.assertRaises(OSError) as raised:
                self.lease.spawn_role(self.command, deadline=time.monotonic() + 60)
        self.assertEqual(raised.exception.errno, errno.ENOENT)
        self.assertEqual(self.lease.record['roleBorrows'][0]['exception']['nodes'][0]['errno'], errno.ENOENT)
        self.lease.close(timeout=0)
        self.assertTrue(self.lease.record['namespaceDescriptorClosed'])

    def test_mismatched_command_cannot_borrow_the_owned_descriptor(self):
        for command in (('unused-bwrap', '--userns', 'not-owned', '--', str(self.descriptor)),
                        (*self.command[:-1], 'not-owned')):
            with self.subTest(command=command), \
                 patch('worldline.linux.namespace_lifetime.subprocess.Popen') as launch:
                with self.assertRaisesRegex(NamespaceRestrictionFailure, 'differs from owned descriptor'):
                    self.lease.spawn_role(command, deadline=time.monotonic() + 60)
                launch.assert_not_called()
            fcntl.fcntl(self.descriptor, fcntl.F_GETFD)


_BOUNDARY_PROBE = '''import errno, json, os, threading
def observe():
    facts = {'uid': os.geteuid(), 'descriptors': []}
    for number in os.listdir('/proc/self/fd'):
        try:
            link = os.readlink('/proc/self/fd/' + number)
        except FileNotFoundError:
            continue
        facts['descriptors'].append(link)
        assert not any(link.startswith(kind + ':[') for kind in
                       ('user', 'mnt', 'pid', 'net', 'ipc', 'uts', 'cgroup', 'time'))
    try:
        os.unshare(os.CLONE_NEWUSER)
    except OSError as error:
        facts['userNamespaceErrno'] = error.errno
        assert error.errno == errno.ENOSPC
    else:
        raise AssertionError('further user namespace creation was not denied')
    for kind, flag in (('mnt', os.CLONE_NEWNS), ('net', os.CLONE_NEWNET)):
        descriptor = os.open('/proc/self/ns/' + kind, os.O_RDONLY)
        try:
            try:
                os.setns(descriptor, flag)
            except OSError as error:
                facts[kind + 'JoinErrno'] = error.errno
                assert error.errno == errno.EPERM
            else:
                raise AssertionError('namespace join was not denied')
        finally:
            os.close(descriptor)
    completed = []
    thread = threading.Thread(target=lambda: completed.append('ordinary thread'))
    thread.start()
    thread.join()
    assert completed == ['ordinary thread']
    facts['ordinaryThread'] = completed
    return facts
'''

_PROBE = _BOUNDARY_PROBE + '''
if __name__ == '__main__':
    import subprocess
    facts = observe()
    child = subprocess.run(['/usr/bin/true'], check=True)
    facts['ordinaryProcessReturncode'] = child.returncode
    print(json.dumps(facts, sort_keys=True))
'''

_EXAMINER = _BOUNDARY_PROBE + '''import candidate
from pathlib import Path
facts = [observe()]
for runner in (candidate.run, candidate.run_isolated):
    result = runner(['/usr/bin/python3', 'probe.py'], timeout=20)
    assert result.returncode == 0, (result.stdout, result.stderr)
    facts.append(json.loads(result.stdout))
assert [item['uid'] for item in facts] == [0, 1, 2]
Path('/run/worldline-report/report').write_text('<testsuite tests="1" failures="0" errors="0"/>')
print(json.dumps(facts, sort_keys=True))
'''


@unittest.skipUnless(os.environ.get('WORLDLINE_PRIVATE_EVALUATOR_TEST') == '1',
                     'same controlled user-systemd prerequisite as original integration')
class NamespaceRestrictionIntegration(unittest.TestCase):
    def test_actual_roles_keep_ids_and_normal_processes_without_namespace_authority(self):
        from worldline.linux.private_evaluator import PrivateEvaluationSpec, PrivateEvaluator, VERIFIER_MOUNT
        from worldline.linux.systemd import SystemdAdapter
        with tempfile.TemporaryDirectory(prefix='worldline-namespace-lifetime-') as directory:
            root = Path(directory)
            source, verifiers, report = root / 'source', root / 'verifiers', root / 'report'
            for path in (source, verifiers, report):
                path.mkdir(mode=0o700)
            (source / 'probe.py').write_text(_PROBE)
            (verifiers / 'exam.py').write_text(_EXAMINER)
            before_host_quota = Path('/proc/sys/user/max_user_namespaces').read_bytes()
            spec = PrivateEvaluationSpec(str(uuid.uuid4()), {'/logical/namespace-test': source}, verifiers,
                (TRUSTED_INTERPRETER, VERIFIER_MOUNT + '/exam.py'), '/logical/namespace-test',
                report, root / 'run', timeout_seconds=60,
                verifier_digests={path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                                  for path in verifiers.iterdir()})
            result = PrivateEvaluator(SystemdAdapter()).run(spec, resource_properties=(
                'MemoryMax=1G', 'TasksMax=64', 'CPUQuota=100%', 'IOAccounting=yes'))
            self.assertEqual(result['exitCode'], 0, result['stdout'] + result['stderr'])
            self.assertEqual(Path('/proc/sys/user/max_user_namespaces').read_bytes(), before_host_quota)
            self.assertEqual((source / 'probe.py').read_text(), _PROBE)
            self.assertEqual(os.stat(source).st_mode & 0o777, 0o700)
            facts = json.loads(result['stdout'])
            self.assertEqual([item['uid'] for item in facts], [0, 1, 2])
            for item in facts:
                self.assertEqual(item['userNamespaceErrno'], errno.ENOSPC)
                self.assertEqual(item['ordinaryThread'], ['ordinary thread'])
            # Direct examiner spawning is prohibited by the original runtime
            # guard target. Ordinary spawning is preserved for worker/candidate.
            self.assertNotIn('ordinaryProcessReturncode', facts[0])
            for item in facts[1:]:
                self.assertEqual(item['ordinaryProcessReturncode'], 0)
            boundary = result['boundary']
            self.assertTrue(boundary['namespaceLifetimeSetup']['namespaceDescriptorClosed'])
            self.assertTrue(boundary['namespaceLifetimeSetup']['ready'])
            cleanup = boundary['namespaceLifetimeSetup']['processCleanup']
            self.assertTrue(all(row['returncode'] == 0 for row in cleanup))
            records = boundary['daemonRoleObservations']
            quotas = [row for row in records if row['kind'] == 'namespace-quota-reader']
            self.assertEqual(len(quotas), 1)
            self.assertEqual(decoded(quotas[0]['observation']['quotaBytes']).strip(), b'0')
            self.assertFalse(quotas[0]['confinementEstablished'])
            roles = [row for row in records if row['kind'] == 'role-startup']
            self.assertEqual({row['roleClaim'] for row in roles}, {'examiner', 'worker', 'candidate'})
            for row in roles:
                self.assertTrue(row['inheritedDescriptorInventory'])
                self.assertFalse(row['confinementEstablished'])
            self.assertIn(b'failures="0"', (report / 'report').read_bytes())


if __name__ == '__main__':
    unittest.main()
