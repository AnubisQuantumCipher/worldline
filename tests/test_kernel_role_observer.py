"""Additive startup-observer coverage; no confinement/phase acceptance claim."""
from __future__ import annotations

from contextlib import ExitStack
import array
import base64
import json
import os
import socket
import stat
import struct
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from worldline.linux.kernel_role_observer import (
    KernelRoleObserver, RoleObservationFailure, _Capture, _Subject,
    _fields, _mount_root_statx, identity_map, mapped_identity, mount_table, process_identity,
)
from worldline.raw_observation import ObservationRetentionError


def stat_record(pid=42, parent=41, start=900, name=b'helper ) ( name'):
    # /proc/pid/stat fields, in their documented order through starttime.
    values = [('state', b'S'), ('ppid', str(parent).encode()), ('pgrp', b'42'),
              ('session', b'42'), ('tty_nr', b'0'), ('tpgid', b'-1'),
              ('flags', b'0'), ('minflt', b'0'), ('cminflt', b'0'),
              ('majflt', b'0'), ('cmajflt', b'0'), ('utime', b'0'),
              ('stime', b'0'), ('cutime', b'0'), ('cstime', b'0'),
              ('priority', b'20'), ('nice', b'0'), ('num_threads', b'1'),
              ('itrealvalue', b'0'), ('starttime', str(start).encode())]
    return str(pid).encode() + b' (' + name + b') ' + b' '.join(v for _k, v in values) + b'\n'


class KernelRecordParsing(unittest.TestCase):
    def test_native_filter_sample_keeps_observed_fields_and_evidence_boundary(self):
        from worldline.linux.kernel_role_observer import native_filter_fields
        fields = _fields(b'NoNewPrivs:\t1\nSeccomp:\t2\nSeccomp_filters:\t3\n')
        result = native_filter_fields(fields)
        self.assertEqual(result, {'scope': 'held-proc-status-sample-only',
            'NoNewPrivs': '1', 'Seccomp': '2', 'Seccomp_filters': '3',
            'independentKernelProgramObservation': False})
        self.assertEqual(fields[b'Seccomp_filters'], b'3')

    def test_native_filter_sample_refuses_absence_malformed_and_unfiltered_modes(self):
        from worldline.linux.kernel_role_observer import native_filter_fields
        fields = {b'NoNewPrivs': b'1', b'Seccomp': b'2', b'Seccomp_filters': b'1'}
        for key in fields:
            changed = dict(fields)
            del changed[key]
            with self.subTest(missing=key), self.assertRaises(RoleObservationFailure):
                native_filter_fields(changed)
        for key, values in ((b'NoNewPrivs', (b'0', b'01', None, True)),
                            (b'Seccomp', (b'0', b'1', b'02', None, 2)),
                            (b'Seccomp_filters', (b'0', b'-1', b'+1', b'01', b'1\n',
                                                   b'', b'1.0', b'\xff', None, 1, True))):
            for value in values:
                with self.subTest(key=key, value=value), self.assertRaises(RoleObservationFailure):
                    native_filter_fields({**fields, key: value})

    def test_native_maps_preserve_readwrite_data_and_anonymous_paths(self):
        from worldline.linux.kernel_role_observer import native_mapping_rows
        rows = native_mapping_rows(
            b'1000-2000 r-xp 00000000 00:01 42 /run/guard.so\n'
            b'2000-3000 rw-p 00001000 00:01 42 /run/guard.so\n'
            b'3000-4000 rw-p 00000000 00:00 0\n')
        self.assertEqual([row['permissions'] for row in rows], ['r-xp', 'rw-p', 'rw-p'])
        self.assertEqual([row['inode'] for row in rows], [42, 42, 0])
        self.assertEqual(base64.b64decode(rows[0]['pathBytes']['payload']), b'/run/guard.so')
        self.assertIsNone(rows[-1]['pathBytes'])

    def test_native_maps_reject_incomplete_or_malformed_kernel_rows(self):
        from worldline.linux.kernel_role_observer import native_mapping_rows
        for value in (b'', b'1000-1000 r-xp 0 00:01 42 /guard\n',
                      b'1000-2000 r-xq 0 00:01 42 /guard\n',
                      b'1000-2000 r-xp wrong 00:01 42 /guard\n',
                      b'1000-2000 r-xp 0 bad 42 /guard\n',
                      b'1000-2000 r-xp 0 00:01 absent /guard\n'):
            with self.subTest(value=value), self.assertRaises(RoleObservationFailure):
                native_mapping_rows(value)

    def test_comm_delimiters_do_not_select_a_different_process_identity(self):
        self.assertEqual(process_identity(stat_record()),
                         {'pid': 42, 'ppid': 41, 'starttime': 900})
        for content in (b'', b'42 (short) S 41', b'x (bad) S 41'):
            with self.subTest(content=content), self.assertRaises(RoleObservationFailure):
                process_identity(content)

    def test_receiver_view_mapping_preserves_sparse_inside_ids(self):
        rows = identity_map(b'0 1000 1\n1 100000 65535\n')
        self.assertEqual(mapped_identity(rows, 0), 1000)
        self.assertEqual(mapped_identity(rows, 1), 100000)
        with self.assertRaises(RoleObservationFailure):
            mapped_identity(rows, 70000)
        for content in (b'', b'0 1000 0\n', b'0 1000 3\n2 2000 1\n',
                        b'0 1000 3\n9 1001 1\n', b'0 x 1\n'):
            with self.subTest(content=content), self.assertRaises(RoleObservationFailure):
                identity_map(content)

    def test_required_status_fields_are_never_replaced_by_defaults(self):
        self.assertEqual(_fields(b'Uid:\t100000 100000 100000 100000\nGroups:\t\n'),
                         {b'Uid': b'100000 100000 100000 100000', b'Groups': b''})
        for content in (b'Uid: 1\nUid: 2\n', b'not a field\n'):
            with self.subTest(content=content), self.assertRaises(RoleObservationFailure):
                _fields(content)

    def test_mountinfo_keeps_bind_access_mode_and_full_topology(self):
        rows = mount_table(
            b'57 31 0:27 /private\\040source /logical\\040root ro,nosuid shared:9 - tmpfs tmpfs rw\n')
        self.assertEqual(rows, [{'id': 57, 'parent': 31, 'device': '0:27',
                                'root': '/private source', 'target': '/logical root',
                                'options': ['ro', 'nosuid'], 'optional': ['shared:9'],
                                'filesystem': 'tmpfs', 'source': 'tmpfs', 'superOptions': ['rw']}])
        valid = b'57 31 0:27 / /run rw - tmpfs tmpfs rw\n'
        for content in (b'', valid + valid, b'57 31 bad / /run rw - tmpfs tmpfs rw\n',
                        b'57 31 0:27 / /bad\\777 ro - tmpfs tmpfs rw\n',
                        b'57 31 0:27 / /bad\\x ro - tmpfs tmpfs rw\n'):
            with self.subTest(content=content), self.assertRaises(RoleObservationFailure):
                mount_table(content)


class OwnedKernelReads(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='worldline-kernel-read-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.record = {'reads': [], 'namespaces': []}
        self.stop = threading.Event()

    def capture(self, maximum=65536):
        return _Capture(self.record, maximum, time.monotonic() + 60, self.stop)

    def payload(self, item):
        return base64.b64decode(item['bytes']['payload'], validate=True)

    def test_complete_empty_and_non_utf8_reads_are_retained_before_parsing(self):
        capture = self.capture()
        for content in (b'', b'\x00\xff\r\n'):
            source = self.root / 'entry'
            source.write_bytes(content)
            self.assertEqual(capture.read(None, str(source), 'fixture'), content)
            item = self.record['reads'][-1]
            self.assertTrue(item['returned'])
            self.assertTrue(item['eof'])
            self.assertEqual(self.payload(item), content)
            self.assertIsNone(item['exception'])

    def test_missing_and_over_limit_reads_remain_failed_observations(self):
        missing = self.root / 'missing'
        with self.assertRaises(FileNotFoundError):
            self.capture().read(None, str(missing), 'fixture')
        item = self.record['reads'][-1]
        self.assertFalse(item['returned'])
        self.assertFalse(item['eof'])
        self.assertIsNone(item['descriptor'])
        self.assertEqual(item['errno'], 2)
        source = self.root / 'entry'
        source.write_bytes(b'abcd')
        with self.assertRaises(RoleObservationFailure):
            self.capture(maximum=3).read(None, str(source), 'fixture')
        item = self.record['reads'][-1]
        self.assertFalse(item['returned'])
        self.assertFalse(item['eof'])
        self.assertEqual(self.payload(item), b'abcd')
        self.assertIsNotNone(item['exception'])

    def test_cancelled_read_cannot_be_reported_as_empty_eof(self):
        self.stop.set()
        with self.assertRaises(RoleObservationFailure):
            self.capture().read(None, str(self.root / 'entry'), 'fixture')
        self.assertFalse(self.record['reads'][-1]['eof'])

    def test_failed_subject_construction_closes_its_owned_pidfd(self):
        descriptor = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY)
        with ExitStack() as owned, patch('worldline.linux.kernel_role_observer.os.open',
                                        side_effect=PermissionError('controlled proc denial')):
            with self.assertRaises(PermissionError):
                _Subject(42, descriptor, self.capture(), owned)
        with self.assertRaises(OSError):
            os.fstat(descriptor)


class ObserverRetention(unittest.TestCase):
    def make_observer(self, callback=None):
        return KernelRoleObserver({'runtime': '/unopened', 'runId': 'fixture'},
                                  maximum_bytes=65536, maximum_request=65536,
                                  handshake_seconds=60, observer=callback)

    def test_retention_takes_ownership_and_failure_has_no_success_record(self):
        receiver = []
        observer = self.make_observer(lambda kind, number, value: receiver.append((kind, number, value)))
        record = {'kind': 'fixture', 'nested': {'bytes': 'original'}}
        observer._retain(record)
        record['nested']['bytes'] = 'changed'
        self.assertEqual(observer.records[0]['nested']['bytes'], 'original')
        self.assertEqual(receiver[0][2]['nested']['bytes'], 'original')
        def fail(*_args):
            raise OSError('controlled retention failure')
        failing = self.make_observer(fail)
        with self.assertRaises(ObservationRetentionError):
            failing._retain(record)
        self.assertEqual(failing.records, [])

    def test_returned_roster_requires_every_observed_role_once(self):
        observer = self.make_observer()
        observer.roles = {'exam-id': 'examiner', 'worker-id': 'worker'}
        boundary = {'examiner': {'role': 'examiner', 'kernelObservationId': 'exam-id'},
                    'workers': [{'observation': {'role': 'worker', 'kernelObservationId': 'worker-id'}}]}
        returned = observer.finish(boundary)
        self.assertEqual(returned[-1]['kind'], 'observer-cleanup')
        self.assertTrue(returned[-1]['returned'])
        malformed = [
            {**boundary, 'workers': []},
            {**boundary, 'workers': [None]},
            {**boundary, 'workers': [{'observation': boundary['examiner']}]},
            {**boundary, 'examiner': {'role': 'examiner'}},
        ]
        for value in malformed:
            with self.subTest(value=value), self.assertRaises(RoleObservationFailure):
                observer.finish(value)

    def test_deferred_cleanup_has_one_owner_and_closes_after_thread_exit(self):
        observer = self.make_observer()
        closed = []
        observer.stack.callback(lambda: closed.append('stack'))
        class Listener:
            def close(self):
                closed.append('listener')
        class NotYetJoined:
            def join(self, timeout):
                pass
            def is_alive(self):
                return True
        observer.listener, observer.thread = Listener(), NotYetJoined()
        with self.assertRaises(RoleObservationFailure):
            observer._close()
        self.assertTrue(observer.cleanup_deferred)
        self.assertTrue(observer.join_incomplete)
        self.assertNotIn('stack', closed)
        # Model the stopped service loop reaching its finally; no target launch.
        observer._serve()
        self.assertEqual(closed.count('stack'), 1)
        self.assertTrue(observer.cleanup_claimed)
        self.assertTrue(observer.service_done)
        with self.assertRaises(RoleObservationFailure):
            observer._close()
        self.assertEqual(closed.count('stack'), 1)

    def test_service_exit_before_transfer_closes_once_but_join_still_refuses(self):
        observer = self.make_observer()
        closed = []
        observer.stack.callback(lambda: closed.append('stack'))
        class Listener:
            def close(self):
                closed.append('listener')
        class FinalizingThread:
            def join(self, timeout):
                # Service finally has made its decision, but the thread has not
                # yet returned. This is the other side of the ownership race.
                observer._serve()
            def is_alive(self):
                return True
        observer.listener, observer.thread = Listener(), FinalizingThread()
        with self.assertRaises(RoleObservationFailure):
            observer._close()
        self.assertTrue(observer.service_done)
        self.assertTrue(observer.join_incomplete)
        self.assertFalse(observer.cleanup_deferred)
        self.assertTrue(observer.cleanup_claimed)
        self.assertEqual(closed.count('stack'), 1)
        cleanup = [record for record in observer.records if record['kind'] == 'observer-cleanup']
        self.assertEqual(len(cleanup), 1)
        self.assertEqual(cleanup[0]['owner'], 'caller')
        self.assertTrue(cleanup[0]['returned'])
        with self.assertRaises(RoleObservationFailure):
            observer._close()
        self.assertEqual(closed.count('stack'), 1)

    def test_dual_service_close_failure_attempts_every_channel_and_defers_until_both_finish(self):
        for completion_order in ((False, True), (True, False)):
            with self.subTest(completion_order=completion_order):
                observer = self.make_observer()
                observer.native_service_done = False
                events = []
                observer.stack.callback(lambda: events.append('shared-stack'))
                primary = KeyboardInterrupt('controlled listener close interruption')
                class Channel:
                    def __init__(self, name, failure=None):
                        self.name, self.failure = name, failure
                    def close(self):
                        events.append(self.name)
                        if self.failure is not None:
                            raise self.failure
                class WaitingThread:
                    def __init__(self, name):
                        self.name = name
                    def join(self, timeout):
                        events.append('join-' + self.name)
                        self.timeout = timeout
                    def is_alive(self):
                        return True
                observer.listener = Channel('listener', primary)
                observer.native_listener = Channel('native-listener', OSError('second controlled close'))
                observer.active = Channel('active-role')
                observer.native_active = Channel('active-native')
                observer.thread = WaitingThread('role')
                observer.native_thread = WaitingThread('native')
                with self.assertRaises(KeyboardInterrupt) as caught:
                    observer._close()
                self.assertIs(caught.exception, primary)
                self.assertEqual(events, ['listener', 'native-listener', 'active-role', 'active-native',
                                          'join-role', 'join-native'])
                self.assertTrue(observer.cleanup_deferred)
                self.assertTrue(observer.join_incomplete)
                self.assertFalse(observer.cleanup_claimed)
                self.assertLessEqual(observer.native_thread.timeout, observer.thread.timeout)
                observer._service_complete(native=completion_order[0])
                self.assertNotIn('shared-stack', events)
                observer._service_complete(native=completion_order[1])
                self.assertEqual(events.count('shared-stack'), 1)
                self.assertTrue(observer.cleanup_claimed)
                self.assertIs(observer.failure, primary)
                cleanup = next(row for row in observer.records if row['kind'] == 'observer-channel-cleanup')
                self.assertEqual([row['returned'] for row in cleanup['closes']], [False, False, True, True])
                self.assertTrue(all(row['joinReturned'] and row['alive'] for row in cleanup['joins']))

    def test_join_failure_still_joins_other_service_and_cleans_only_after_nonlive_observations(self):
        observer = self.make_observer()
        observer.native_service_done = False
        events = []
        observer.stack.callback(lambda: events.append('shared-stack'))
        primary = SystemExit('controlled first join interruption')
        class FinishedThread:
            def __init__(self, name, failure=None):
                self.name, self.failure = name, failure
            def join(self, timeout):
                events.append('join-' + self.name)
                if self.failure is not None:
                    raise self.failure
            def is_alive(self):
                events.append('nonlive-' + self.name)
                return False
        observer.thread = FinishedThread('role', primary)
        observer.native_thread = FinishedThread('native')
        with self.assertRaises(SystemExit) as caught:
            observer._close()
        self.assertIs(caught.exception, primary)
        self.assertEqual(events, ['join-role', 'nonlive-role', 'join-native', 'nonlive-native', 'shared-stack'])
        self.assertFalse(observer.cleanup_deferred)
        self.assertFalse(observer.join_incomplete)
        self.assertTrue(observer.cleanup_claimed)
        self.assertIsNone(observer.thread)
        self.assertIsNone(observer.native_thread)

    def test_malformed_packet_closes_every_delivered_descriptor(self):
        observer = self.make_observer()
        record = {'reads': [], 'namespaces': []}
        capture = _Capture(record, 65536, time.monotonic() + 60, threading.Event())
        descriptors = [os.open('/dev/null', os.O_RDONLY) for _ in ('first', 'second')]
        peer = (42, 1000, 1000)
        class Packet:
            def recvmsg(self, *_args):
                return (b'MOUNT\n', [
                    (socket.SOL_SOCKET, socket.SCM_RIGHTS, array.array('i', descriptors).tobytes()),
                    (socket.SOL_SOCKET, socket.SCM_CREDENTIALS, struct.pack('=iII', *peer)),
                ], socket.MSG_CTRUNC, None)
        with ExitStack() as owned:
            with self.assertRaises(RoleObservationFailure):
                observer._packet(Packet(), capture, owned, peer)
        for descriptor in descriptors:
            with self.assertRaises(OSError):
                os.fstat(descriptor)
        self.assertIsNotNone(record['packets'][-1]['exception'])


class KernelMountRootBinding(unittest.TestCase):
    def test_actual_mount_root_and_ordinary_descendant_are_distinct(self):
        descriptor = os.open('/', os.O_PATH | os.O_CLOEXEC)
        try:
            observed = {}
            mount_id = _mount_root_statx(descriptor, observed)
            fields = _fields(Path('/proc/self/fdinfo/' + str(descriptor)).read_bytes())
            self.assertEqual(mount_id, int(fields[b'mnt_id']))
            self.assertEqual(observed['inode'], os.fstat(descriptor).st_ino)
            self.assertEqual(observed['return'], 0)
            self.assertTrue(observed['attributesMask'] & 0x00002000)
            self.assertTrue(observed['attributes'] & 0x00002000)
        finally:
            os.close(descriptor)
        with tempfile.TemporaryDirectory(prefix='worldline-statx-descendant-') as temporary:
            descriptor = os.open(temporary, os.O_PATH | os.O_CLOEXEC)
            try:
                observed = {}
                with self.assertRaises(RoleObservationFailure):
                    _mount_root_statx(descriptor, observed)
                self.assertEqual(observed['return'], 0)
                self.assertTrue(observed['attributesMask'] & 0x00002000)
                self.assertFalse(observed['attributes'] & 0x00002000)
            finally:
                os.close(descriptor)


@unittest.skipUnless(os.environ.get('WORLDLINE_PRIVATE_EVALUATOR_TEST') == '1',
                     'same controlled user-systemd integration prerequisite as original cases')
class KernelRoleIntegration(unittest.TestCase):
    def setUp(self):
        # Reuse the original fixture unchanged, including its direct Path reads.
        from test_private_evaluator import PrivateEvaluatorIntegration
        PrivateEvaluatorIntegration.setUp(self)

    def test_actual_original_examiner_has_daemon_retained_kernel_subjects(self):
        from test_private_evaluator import PrivateEvaluatorIntegration
        result = PrivateEvaluatorIntegration.run_examiner(self, b'ordinary worker complete\n', 'kernel-observed')
        self.assertEqual(result['exitCode'], 0)
        self.assertIn(b'failures="0"', (result['reportDirectory'] / 'report').read_bytes())
        records = result['boundary']['daemonRoleObservations']
        bootstrap = [row for row in records if row['kind'] == 'bootstrap-anchor']
        self.assertEqual(len(bootstrap), 1)
        roles = [row for row in records if row['kind'] == 'role-startup']
        self.assertEqual({row['roleClaim'] for row in roles}, {'examiner', 'worker'})
        for row in roles:
            self.assertFalse(row['confinementEstablished'])
            self.assertEqual(row['scope'], 'startup-snapshot-only')
            self.assertEqual(row['peerCredentials']['pid'], row['identity']['pid'])
            self.assertEqual(row['ancestry'][-1], bootstrap[0]['identity'])
            self.assertTrue(all(item['returned'] and item['eof'] for item in row['reads']))
            self.assertTrue(all(item['returned'] for item in row['namespaces']))
            self.assertTrue(all(not item['pidfdReady'] for item in row['liveness']))
            self.assertIsNone(row['exception'])
        self.assertEqual((self.source / 'source.txt').read_text(), 'ordinary source\n')
        self.assertFalse((self.source / 'nested/created.txt').exists())


@unittest.skipUnless(os.environ.get('WORLDLINE_PRIVATE_EVALUATOR_TEST') == '1',
                     'same controlled user-systemd integration prerequisite as original cases')
class KernelPrivateDirectoryCase(unittest.TestCase):
    def setUp(self):
        from test_private_case_lease import PrivateCaseLeaseIntegration
        PrivateCaseLeaseIntegration.setUp(self)
        # Add a valid owner-only tree case; the original fixture stays unchanged.
        self.source.chmod(0o700)

    def test_original_positive_case_with_private_candidate_root(self):
        from test_private_case_lease import PrivateCaseLeaseIntegration
        _spec, result = PrivateCaseLeaseIntegration.run_mode(self, 'positive')
        self.assertEqual(result['exitCode'], 0, result['stdout'] + result['stderr'])
        self.assertIn(b'failures="0"', (result['reportDirectory'] / 'report').read_bytes())
        self.assertEqual(stat.S_IMODE(self.source.stat().st_mode), 0o700)
        candidates = [row for row in result['boundary']['daemonRoleObservations']
                      if row['kind'] == 'role-startup' and row['roleClaim'] == 'candidate']
        self.assertTrue(candidates)
        for row in candidates:
            for handle in row['mountHandles']:
                self.assertEqual(handle['mount']['id'], handle['fdinfoMountId'])
                self.assertEqual(handle['statx']['mountId'], handle['fdinfoMountId'])
                self.assertTrue(handle['statx']['attributes'] & 0x00002000)


if __name__ == '__main__':
    unittest.main()
