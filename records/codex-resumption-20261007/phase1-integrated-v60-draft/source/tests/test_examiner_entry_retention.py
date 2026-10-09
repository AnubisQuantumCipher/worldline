"""Real socket/object controls plus original private integration.

Transport unit controls use a labeled synthetic subject; they do not establish
kernel identity or confinement. The integration class uses the real backend.
"""
from contextlib import contextmanager
import array
import base64
import copy
import fcntl
import hashlib
import json
import os
from pathlib import Path
import socket
import tempfile
import threading
import time
import types
import unittest
from unittest.mock import patch
import uuid

from worldline.linux import private_evaluator as evaluator
from worldline.linux.kernel_role_observer import KernelRoleObserver, _DescriptorOwner
from worldline.raw_observation import optional_bytes
from worldline.linux import kernel_role_observer as kernel_observer


class EntryRetentionTransport(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='worldline-entry-retention-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.verifiers = self.root / 'verifiers'
        self.verifiers.mkdir()
        self.path = self.verifiers / 'entry.py'
        self.mount = patch.object(evaluator, 'VERIFIER_MOUNT', str(self.verifiers))
        self.mount.start()
        self.addCleanup(self.mount.stop)

    def binding(self, source):
        return dict(schemaVersion=1, runId='entry-retention', sourceRecordId='daemon-source',
                    path=str(self.path), sha256=hashlib.sha256(source).hexdigest(), byteCount=len(source))

    def prepare(self, source):
        self.path.write_bytes(source)
        record = {}
        prepared = evaluator._prepare_examiner_entry(str(self.path), 'entry-retention',
                                                    self.binding(source), record)
        return prepared, record

    @contextmanager
    def exchange(self, binding, retain=None, *, cancelled=False, peer=None):
        left, right = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        left.settimeout(5)
        right.settimeout(0.05)
        right.setsockopt(socket.SOL_SOCKET, socket.SO_PASSCRED, 1)
        observer = KernelRoleObserver(dict(runtime=str(self.root), runId=binding['runId'],
            argv=['/usr/bin/python3', str(self.path)], examinerEntryBinding=binding, timeout=5),
            maximum_bytes=evaluator.MAX_TREE_BYTES, maximum_request=evaluator.MAX_REQUEST_BYTES,
            handshake_seconds=evaluator.BOOTSTRAP_HANDSHAKE_SECONDS, observer=retain)
        if cancelled:
            observer.stop.set()
        pidfd = os.pidfd_open(os.getpid())
        subject = types.SimpleNamespace(capture=None, pidfd=pidfd)
        checks = []
        subject.recheck = lambda: checks.append('synthetic-subject-recheck')
        state = {'errors': [], 'observer': observer, 'checks': checks}
        def receive():
            try:
                with right:
                    observer._entry_preparation(right, subject,
                        peer or (os.getpid(), os.geteuid(), os.getegid()), {'recordId': 'startup'})
            except BaseException as error:
                state['errors'].append(error)
        thread = threading.Thread(target=receive)
        thread.start()
        try:
            yield left, state
        finally:
            left.close()
            thread.join(timeout=6)
            if thread.is_alive():
                observer.stop.set()
                try:
                    right.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                thread.join(timeout=6)
            self.assertFalse(thread.is_alive(), 'receiver must finish before its subject handle closes')
            os.close(pidfd)

    def record(self, state):
        return next(r for r in state['observer'].records
                    if r['kind'] == 'examiner-entry-preparation-receive')

    def test_prepare_and_retained_ack_precede_execution_with_real_objects(self):
        marker = self.root / 'executed'
        source = ('from pathlib import Path\nPath(' + repr(str(marker)) + ').write_text("ran")\n').encode()
        self.path.write_bytes(source)
        retained = []
        def retain(*args):
            self.assertFalse(marker.exists())
            retained.append(args)
        with self.exchange(self.binding(source), retain) as (channel, state):
            registry, code = evaluator._prepare_retained_entry(str(self.path), 'entry-retention',
                self.binding(source), channel, 'startup')
            self.assertFalse(marker.exists())
        self.assertFalse(state['errors'])
        record = self.record(state)
        self.assertTrue(record['transferDescriptorsClosed'])
        self.assertEqual(record['helperReport']['read']['bytes'], optional_bytes(source))
        self.assertTrue(record['helperReport']['compile']['returned'])
        self.assertTrue(all(x['eof'] and x['returned'] for x in record['transferObjects']))
        self.assertEqual([x[1] for x in retained], list(range(len(retained))))
        self.assertFalse(record['confinementEstablished'])
        self.assertEqual(state['observer'].roles, {})
        registry.run_main(code, str(self.path))
        self.assertEqual(marker.read_text(), 'ran')

    def test_empty_latin1_and_binary_compile_failure_remain_complete(self):
        for source in (b'', b'# coding: latin-1\nx = "\xff"\n', b'\x00\xff'):
            with self.subTest(source=source):
                self.path.write_bytes(source)
                with self.exchange(self.binding(source)) as (channel, state):
                    if source == b'\x00\xff':
                        with self.assertRaises((SyntaxError, ValueError)):
                            evaluator._prepare_retained_entry(str(self.path), 'entry-retention',
                                self.binding(source), channel, 'startup')
                    else:
                        evaluator._prepare_retained_entry(str(self.path), 'entry-retention',
                            self.binding(source), channel, 'startup')
                self.assertFalse(state['errors'])
                report = self.record(state)['helperReport']
                self.assertEqual(report['read']['bytes'], optional_bytes(source))
                self.assertTrue(report['read']['readReachedEof'])
                self.assertEqual(report['compile']['returned'], source != b'\x00\xff')

    def test_missing_source_failure_keeps_absence_and_acknowledges_retention(self):
        binding = self.binding(b'pass\n')
        with self.exchange(binding) as (channel, state):
            with self.assertRaises(FileNotFoundError):
                evaluator._prepare_retained_entry(str(self.path), 'entry-retention', binding, channel, 'startup')
        self.assertFalse(state['errors'])
        report = self.record(state)['helperReport']
        self.assertIsNone(report['read']['bytes'])
        self.assertFalse(report['compile']['started'])
        self.assertIsNotNone(report['exception'])

    def test_changed_source_retains_actual_bytes_without_success_digest_requirement(self):
        self.path.write_bytes(b'actual = 2\n')
        binding = self.binding(b'expected = 1\n')
        with self.exchange(binding) as (channel, state):
            with self.assertRaises(Exception):
                evaluator._prepare_retained_entry(str(self.path), 'entry-retention', binding, channel, 'startup')
        self.assertFalse(state['errors'])
        report = self.record(state)['helperReport']
        self.assertEqual(report['read']['bytes'], optional_bytes(b'actual = 2\n'))
        self.assertFalse(report['compile']['returned'])
        self.assertIsNotNone(report['compile']['exception'])

    def test_original_baseexception_survives_secondary_retention_failure(self):
        self.path.write_bytes(b'pass\n')
        primary = KeyboardInterrupt('compile interruption')
        def refuse(*args):
            raise OSError('retained storage refused')
        with self.exchange(self.binding(b'pass\n'), refuse) as (channel, state):
            with patch.object(evaluator._RegisteredExaminerCode, 'compile_entry', side_effect=primary):
                with self.assertRaises(KeyboardInterrupt) as caught:
                    evaluator._prepare_retained_entry(str(self.path), 'entry-retention',
                        self.binding(b'pass\n'), channel, 'startup')
        self.assertIs(caught.exception, primary)
        self.assertTrue(any('retention also failed' in note for note in primary.__notes__))
        self.assertTrue(state['errors'])

    def test_role_channel_cleanup_preserves_primary_and_refuses_success_on_close_error(self):
        primary = SystemExit(7)
        channel = types.SimpleNamespace(close=lambda: (_ for _ in ()).throw(OSError('close failed')))
        with patch.object(evaluator.socket, 'socket', return_value=channel):
            with self.assertRaises(SystemExit) as caught:
                with evaluator._owned_role_channel():
                    raise primary
            with self.assertRaises(OSError):
                with evaluator._owned_role_channel():
                    pass
        self.assertIs(caught.exception, primary)
        self.assertTrue(any('channel cleanup' in note for note in primary.__notes__))

    def manual(self, source, *, change=None, metadata_change=None, raw_metadata=None,
               unsealed=False, extra=False, duplicate=False, empty_record=False, peer=None):
        _prepared, report = self.prepare(source)
        metadata = copy.deepcopy(report)
        metadata['read'].pop('bytes')
        if metadata_change:
            metadata_change(metadata)
        encoded = raw_metadata(metadata) if raw_metadata else json.dumps(metadata).encode()
        request = dict(schemaVersion=1, operation='examiner-entry-prepared', runId='entry-retention',
            startupRecordId='startup', transferId=str(uuid.uuid4()), metadataBytes=len(encoded),
            sourcePresent=True, sourceBytes=len(source))
        if change:
            change(request)
        descriptors = []
        try:
            for name, content in [('metadata', encoded), ('source', source)]:
                if unsealed:
                    fd = os.memfd_create(name, os.MFD_CLOEXEC | os.MFD_ALLOW_SEALING)
                    descriptors.append(fd)
                    self.assertEqual(os.write(fd, content), len(content))
                else:
                    descriptors.append(evaluator._sealed_entry_object(name, content))
            if extra:
                descriptors.append(os.dup(descriptors[1]))
            with self.exchange(self.binding(source), peer=peer) as (channel, state):
                packet = json.dumps(request).encode()
                channel.sendmsg([packet], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, array.array('i', descriptors))])
                if duplicate:
                    channel.send(packet)
                if empty_record:
                    channel.send(b'')
                channel.shutdown(socket.SHUT_WR)
                self.assertEqual(channel.recv(evaluator.MAX_REQUEST_BYTES), b'')
            self.assertTrue(state['errors'])
            self.assertIsNotNone(self.record(state)['exception'])
            return state
        finally:
            for fd in descriptors:
                os.close(fd)

    def test_wrong_binding_typed_lengths_presence_and_credentials_refuse(self):
        for change in (lambda r: r.update(startupRecordId='old-startup'),
                       lambda r: r.update(runId='other-run'),
                       lambda r: r.update(metadataBytes=True),
                       lambda r: r.update(sourcePresent=1),
                       lambda r: r.update(sourceBytes=0),
                       lambda r: r.update(sourcePresent=False)):
            with self.subTest(change=change):
                self.manual(b'pass\n', change=change)
        self.manual(b'pass\n', peer=(os.getpid(), os.geteuid(), os.getegid() + 1))

    def test_missing_seals_extra_descriptors_and_duplicate_transfer_refuse(self):
        before = set(os.listdir('/proc/self/fd'))
        self.manual(b'pass\n', unsealed=True)
        self.manual(b'pass\n', extra=True)
        self.manual(b'pass\n', duplicate=True)
        self.manual(b'pass\n', empty_record=True)
        self.assertEqual(set(os.listdir('/proc/self/fd')), before)

    def test_nested_descriptor_owners_preserve_primary_and_attempt_every_close(self):
        primary = KeyboardInterrupt('original preparation failure')
        outer, inner, calls = {}, {}, []
        descriptors = [os.memfd_create('cleanup-control') for _ in range(3)]
        def close_then_fail(fd):
            os.close(fd)
            calls.append(fd)
            raise OSError('observed close failure')
        with self.assertRaises(KeyboardInterrupt) as caught:
            with _DescriptorOwner(outer) as held:
                held.callback(close_then_fail, descriptors[0])
                with _DescriptorOwner(inner) as received:
                    for fd in descriptors[1:]:
                        received.callback(close_then_fail, fd)
                    raise primary
        self.assertIs(caught.exception, primary)
        self.assertEqual(calls, list(reversed(descriptors)))
        self.assertEqual(len(primary.__notes__), len(descriptors))
        self.assertTrue(all(row['exception'] for row in outer['descriptorCloses'] + inner['descriptorCloses']))
        failure = OSError('success cleanup failed')
        with self.assertRaises(OSError) as caught:
            with _DescriptorOwner({}) as owned:
                owned.callback(lambda unused: (_ for _ in ()).throw(failure), -1)
        self.assertIs(caught.exception, failure)

    def test_received_close_failure_preserves_primary_and_prevents_success_ack(self):
        _prepared, report = self.prepare(b'pass\n')
        original = _DescriptorOwner.callback
        def register(owner, close, descriptor):
            def failing(fd):
                close(fd)
                raise OSError('received descriptor close failed')
            original(owner, failing, descriptor)
        before = set(os.listdir('/proc/self/fd'))
        primary = KeyboardInterrupt('original receive failure')
        with patch.object(_DescriptorOwner, 'callback', register):
            with patch.object(KernelRoleObserver, '_entry_object_bytes', side_effect=primary):
                with self.exchange(self.binding(b'pass\n')) as (channel, state):
                    with self.assertRaises(Exception):
                        evaluator._send_entry_preparation(channel, 'startup', self.binding(b'pass\n'), report)
            self.assertIs(state['errors'][0], primary)
            self.assertTrue(primary.__notes__)
            with self.exchange(self.binding(b'pass\n')) as (channel, state):
                with self.assertRaises(Exception):
                    evaluator._send_entry_preparation(channel, 'startup', self.binding(b'pass\n'), report)
            self.assertIsInstance(state['errors'][0], OSError)
        self.assertEqual(set(os.listdir('/proc/self/fd')), before)

    def test_bad_acknowledgements_and_received_ack_handles_never_release_code(self):
        marker = self.root / 'ack-executed'
        source = ('from pathlib import Path\nPath(' + repr(str(marker)) + ').touch()\n').encode()
        self.path.write_bytes(source)
        binding = self.binding(source)
        before = set(os.listdir('/proc/self/fd'))
        for case in ('malformed', 'truncated', 'mismatched', 'duplicate-field', 'descriptor'):
            with self.subTest(case=case):
                client, server = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
                client.settimeout(5)
                server.settimeout(5)
                errors = []
                def respond():
                    owned = []
                    try:
                        with server:
                            packet, ancillary, flags, _ = server.recvmsg(
                                evaluator.MAX_REQUEST_BYTES, evaluator.MAX_REQUEST_BYTES, socket.MSG_CMSG_CLOEXEC)
                            for level, kind, data in ancillary:
                                if level == socket.SOL_SOCKET and kind == socket.SCM_RIGHTS:
                                    numbers = array.array('i'); numbers.frombytes(data)
                                    owned.extend(numbers)
                            request = json.loads(packet)
                            self.assertEqual(server.recv(1), b'')
                            metadata, actual_source = [os.pread(fd, os.fstat(fd).st_size, 0) for fd in owned]
                            ack = dict(schemaVersion=1, operation='examiner-entry-retained',
                                runId=binding['runId'], startupRecordId='startup',
                                transferId=request['transferId'], recordId='retained', entrySource=binding,
                                metadataSha256=hashlib.sha256(metadata).hexdigest(),
                                sourceSha256=hashlib.sha256(actual_source).hexdigest(), sourcePresent=True)
                            if case == 'mismatched':
                                ack['transferId'] = 'another-exchange'
                            payload = json.dumps(ack).encode()
                            if case == 'malformed': payload = b'{'
                            if case == 'truncated': payload = b'x' * (evaluator.MAX_REQUEST_BYTES + 2)
                            if case == 'duplicate-field': payload = b'{"schemaVersion":1,' + payload[1:]
                            control = []
                            if case == 'descriptor':
                                control = [(socket.SOL_SOCKET, socket.SCM_RIGHTS, array.array('i', [owned[0]]))]
                            server.sendmsg([payload], control)
                    except BaseException as error:
                        errors.append(error)
                    finally:
                        for fd in owned: os.close(fd)
                thread = threading.Thread(target=respond)
                thread.start()
                try:
                    with client, self.assertRaises(Exception):
                        registry, code = evaluator._prepare_retained_entry(str(self.path), 'entry-retention',
                            binding, client, 'startup')
                        registry.run_main(code, str(self.path))
                finally:
                    client.close(); thread.join(timeout=6)
                self.assertFalse(thread.is_alive())
                self.assertFalse(errors, errors)
                self.assertFalse(marker.exists())
        self.assertEqual(set(os.listdir('/proc/self/fd')), before)

    def test_duplicate_missing_and_nonfinite_metadata_are_retained_and_refused(self):
        cases = [lambda r: b'{"schemaVersion":1,' + json.dumps(r).encode()[1:],
                 lambda r: b'{"schemaVersion":1}',
                 lambda r: json.dumps(r).replace('"exception": null', '"exception": 1e400', 1).encode()]
        for changed in cases:
            with self.subTest(changed=changed):
                state = self.manual(b'pass\n', raw_metadata=changed)
                objects = self.record(state)['transferObjects']
                self.assertTrue(objects[0]['returned'])
                self.assertIsNotNone(objects[0]['bytes'])

    def test_successful_compile_report_must_match_actual_source(self):
        self.manual(b'pass\n', metadata_change=lambda r: r['binding'].update(sha256='0' * 64))
        self.manual(b'pass\n', metadata_change=lambda r: r['compile'].update(returned=False))

    def test_cancelled_receive_cannot_release_prepared_code(self):
        _prepared, report = self.prepare(b'pass\n')
        with self.exchange(self.binding(b'pass\n'), cancelled=True) as (channel, state):
            with self.assertRaises(Exception):
                evaluator._send_entry_preparation(channel, 'startup', self.binding(b'pass\n'), report)
        self.assertTrue(state['errors'])
        self.assertIn('cancelled', str(state['errors'][0]))

    def test_actual_writer_receives_complete_preparation_and_ack_ordinals(self):
        from test_private_acquisition_terminal import PrivateAcquisitionTerminal
        from worldline.evaluation_terminal import value_bytes
        fixture = PrivateAcquisitionTerminal(methodName='runTest')
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        writer = fixture.writer('entry-retention-world')
        _prepared, report = self.prepare(b'pass\n')
        with self.exchange(self.binding(b'pass\n'),
                           lambda kind, occurrence, value: fixture.retain(writer, kind, occurrence, value)) as (channel, state):
            evaluator._send_entry_preparation(channel, 'startup', self.binding(b'pass\n'), report)
        self.assertFalse(state['errors'])
        expected = tuple(('private-invocation', 'private-kernel-role-observation', n, row)
                         for n, row in enumerate(state['observer'].records))
        actual = fixture.terminal.captured_observation_events(writer.bound)
        self.assertEqual(value_bytes(actual), value_bytes(expected))
        self.assertTrue(any(row[3].get('helperReport') for row in actual))


class NativePreparationTransport(unittest.TestCase):
    """Real sockets and sealed objects with a synthetic startup anchor and subject.

    The helper status is deliberately synthetic protocol input. These controls
    establish no native membership, private-role identity or confinement claim.
    """
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='worldline-native-retention-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def source(self, name, payload, *, origin='verifier', kind='source'):
        path = self.root / name
        path.write_bytes(payload)
        binding = dict(path=str(path), byteCount=len(payload),
                       sha256=hashlib.sha256(payload).hexdigest(), origin=origin)
        read = {}
        evaluator._read_examiner_source(path, read)
        return {'kind': kind, 'binding': binding}, read

    @contextmanager
    def exchange(self, roster, *, retain=None, maximum_bytes=evaluator.MAX_TREE_BYTES,
                 change_startup=None):
        run_id = 'native-transport-only'
        native = {'schema': 'worldline-examiner-native-v1', 'runId': run_id,
                  'path': evaluator.NATIVE_GUARD_MOUNT, 'byteCount': 1,
                  'sha256': '0' * 64, 'sourceRecordId': 'synthetic-native',
                  'buildReceiptSha256': '0' * 64}
        policy = {'path': evaluator.LOADER_POLICY_MOUNT, 'byteCount': 1,
                  'sha256': '0' * 64, 'sourceRecordId': 'synthetic-policy'}
        observer = KernelRoleObserver(
            dict(runtime=str(self.root), runId=run_id, timeout=5,
                 nativeGuardBinding=native, examinerLoaderBinding=policy,
                 examinerEntryBinding={'byteCount': 0}, nativeSourceRoster=roster),
            maximum_bytes=maximum_bytes, maximum_request=evaluator.MAX_REQUEST_BYTES,
            handshake_seconds=evaluator.BOOTSTRAP_HANDSHAKE_SECONDS, observer=retain)
        synthetic_identity = {'pid': os.getpid(), 'ppid': os.getppid(),
                              'starttime': 'synthetic-transport-only'}
        synthetic_group = b'synthetic-transport-only'
        observer.native_startup = dict(recordId='synthetic-startup',
            peer=(os.getpid(), os.geteuid(), os.getegid()),
            identity=dict(synthetic_identity), cgroup=synthetic_group,
            namespaces={}, credentialFields={})
        def synthetic_subject(pid, pidfd, capture, handles):
            handles.callback(os.close, pidfd)
            self.assertEqual(pid, os.getpid())
            subject = types.SimpleNamespace(identity=dict(synthetic_identity),
                cgroup=synthetic_group, namespaces={}, status={}, capture=capture)
            subject.recheck = lambda: subject.capture.check()
            return subject
        if change_startup:
            change_startup(observer.native_startup)
        listener = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_PASSCRED, 1)
        address = str(self.root / (uuid.uuid4().hex + '.sock'))
        listener.bind(address)
        listener.listen(1)
        listener.settimeout(5)
        state = {'observer': observer, 'errors': [], 'connection': None}
        def receive():
            try:
                with listener:
                    connection, _ = listener.accept()
                    state['connection'] = connection
                    with connection:
                        connection.settimeout(0.05)
                        observer._native_preparation(connection)
            except BaseException as error:
                state['errors'].append(error)
        thread = threading.Thread(target=receive)
        thread.start()
        startup = dict(recordId='synthetic-startup', nativeGuard=native, loaderPolicy=policy)
        channel = evaluator._NativePreparationChannel(run_id, startup)
        channel.native_status = lambda: dict(runId=run_id, phase='configured',
            preinitializationInstalled=True, violated=False, permitActive=False,
            scope='synthetic-transport-helper-report-only')
        with patch.object(evaluator, 'NATIVE_PREPARATION_MOUNT', address), \
                patch.object(kernel_observer, '_Subject', side_effect=synthetic_subject):
            try:
                yield channel, state
            finally:
                if channel.connection is not None:
                    channel.connection.close()
                thread.join(timeout=6)
                if thread.is_alive():
                    observer.stop.set()
                    connection = state['connection']
                    if connection is not None:
                        try:
                            connection.shutdown(socket.SHUT_RDWR)
                        except OSError:
                            pass
                    listener.close()
                    thread.join(timeout=6)
                self.assertFalse(thread.is_alive(), 'native receiver must release its held subject')

    def test_binary_empty_ordered_receipts_close_before_ack_and_keep_one_deadline(self):
        first, first_read = self.source('empty', b'', kind='policy')
        second, second_read = self.source('binary', b'\x00\xff\xfe\n')
        retained = []
        def retain(_kind, _occurrence, record):
            if record['kind'] == 'native-preparation-receive':
                self.assertTrue(record['transferDescriptorsClosed'])
                self.assertTrue(all(row['closed'] for row in record['descriptorCloses']))
            retained.append(record)
        before = set(os.listdir('/proc/self/fd'))
        with self.exchange([first, second], retain=retain) as (channel, state):
            with channel:
                deadline = channel.deadline
                receipts = [channel.previous]
                for row, read in ((first, first_read), (second, second_read)):
                    channel.retain_read(row['kind'], row['binding']['path'], read)
                    receipts.append(channel.previous)
                    self.assertEqual(channel.deadline, deadline)
        self.assertFalse(state['errors'], state['errors'])
        reads = [row for row in retained if row['kind'] == 'native-preparation-receive']
        self.assertEqual([row['sequence'] for row in reads], [0, 1])
        self.assertEqual([row['previousReceiptSha256'] for row in reads], receipts[:-1])
        self.assertEqual([row['helperRead']['bytes'] for row in reads],
                         [optional_bytes(b''), optional_bytes(b'\x00\xff\xfe\n')])
        terminal = next(row for row in retained if row['kind'] == 'native-preparation-terminal')
        self.assertTrue(terminal['trueEof'])
        self.assertFalse(terminal['failed'])
        self.assertIn('synthetic-startup', state['observer'].native_completions)
        self.assertEqual(set(os.listdir('/proc/self/fd')), before)

    def test_independent_tree_domains_do_not_share_an_aggregate_ceiling(self):
        # A small explicit transport fixture exercises accounting without
        # changing either original production tree ceiling.
        ceiling = 16384
        verifier, verifier_read = self.source('verifier', b'v' * ceiling)
        stdlib, stdlib_read = self.source('stdlib', b's' * ceiling, origin='stdlib')
        self.assertGreater(sum(row['binding']['byteCount'] for row in (verifier, stdlib)), ceiling)
        with self.exchange([verifier, stdlib], maximum_bytes=ceiling) as (channel, state):
            with channel:
                channel.retain_read('source', verifier['binding']['path'], verifier_read)
                channel.retain_read('source', stdlib['binding']['path'], stdlib_read)
        self.assertFalse(state['errors'], state['errors'])
        terminal = next(row for row in state['observer'].records
                        if row['kind'] == 'native-preparation-terminal')
        self.assertEqual(terminal['treeDeclaredBytes'], {'verifier': ceiling, 'stdlib': ceiling})

    def test_expired_shared_deadline_refuses_next_read_and_never_completes(self):
        row, read = self.source('source', b'pass\n')
        with self.exchange([row]) as (channel, state):
            with self.assertRaises(evaluator.BackendFailure) as caught:
                with channel:
                    channel.deadline = time.monotonic() - 1
                    state['observer'].stop.set()
                    channel.retain_read('source', row['binding']['path'], read)
        self.assertIn('deadline', str(caught.exception))
        self.assertTrue(state['errors'])
        self.assertEqual(state['observer'].native_completions, {})

    def test_missing_and_actual_partial_read_failures_keep_the_primary_and_full_prefix(self):
        for mode in ('absent', 'partial'):
            with self.subTest(mode=mode):
                row, _ = self.source(mode, b'actual-prefix\x00\xff')
                path = Path(row['binding']['path'])
                read = {}
                if mode == 'absent':
                    path.unlink()
                    with self.assertRaises(FileNotFoundError) as caught:
                        evaluator._read_examiner_source(path, read)
                    primary = caught.exception
                    expected = None
                else:
                    target = path.stat()
                    original_read = os.read
                    calls = []
                    primary = OSError('controlled source read failure after a real prefix')
                    def fail_after_prefix(descriptor, count):
                        actual = os.fstat(descriptor)
                        if (actual.st_dev, actual.st_ino) == (target.st_dev, target.st_ino):
                            if calls:
                                raise primary
                            calls.append(descriptor)
                            return original_read(descriptor, 3)
                        return original_read(descriptor, count)
                    with patch.object(evaluator.os, 'read', side_effect=fail_after_prefix), \
                            self.assertRaises(OSError) as caught:
                        evaluator._read_examiner_source(path, read)
                    self.assertIs(caught.exception, primary)
                    expected = b'act'
                with self.exchange([row]) as (channel, state):
                    with self.assertRaises(type(primary)) as caught:
                        with channel:
                            channel.retain_read('source', row['binding']['path'], read)
                            raise primary
                self.assertIs(caught.exception, primary)
                self.assertFalse(state['errors'], state['errors'])
                actual = next(item for item in state['observer'].records
                              if item['kind'] == 'native-preparation-receive')['helperRead']
                self.assertEqual(actual['bytes'], optional_bytes(expected))
                self.assertFalse(actual['readReturned'])
                terminal = next(item for item in state['observer'].records
                                if item['kind'] == 'native-preparation-terminal')
                self.assertTrue(terminal['failed'])
                self.assertTrue(terminal['trueEof'])

    def test_wrong_sequence_previous_receipt_and_subject_refuse(self):
        row, read = self.source('source', b'pass\n')
        before = set(os.listdir('/proc/self/fd'))
        for mode in ('sequence', 'previous', 'subject'):
            with self.subTest(mode=mode):
                change = (lambda startup: startup.update(cgroup=b'synthetic-wrong-cgroup')) \
                    if mode == 'subject' else None
                with self.exchange([row], change_startup=change) as (channel, state):
                    with self.assertRaises(Exception):
                        with channel:
                            if mode == 'sequence':
                                channel.sequence = 1
                            elif mode == 'previous':
                                channel.previous = '0' * 64
                            channel.retain_read('source', row['binding']['path'], read)
                self.assertTrue(state['errors'])
                self.assertEqual(state['observer'].native_completions, {})
        self.assertEqual(set(os.listdir('/proc/self/fd')), before)

    def test_incomplete_roster_or_extra_terminal_packet_is_never_complete(self):
        row, read = self.source('source', b'pass\n')
        for mode in ('incomplete', 'extra'):
            with self.subTest(mode=mode):
                with self.exchange([row]) as (channel, state):
                    with self.assertRaises(Exception):
                        if mode == 'incomplete':
                            with channel:
                                pass
                        else:
                            channel.__enter__()
                            channel.retain_read('source', row['binding']['path'], read)
                            channel._send({**channel._context(), 'operation': 'native-preparation-terminal',
                                'sequence': channel.sequence, 'previousReceiptSha256': channel.previous,
                                'exception': None, 'nativeStatus': channel.native_status()})
                            channel._send({'unexpected': 'extra packet before EOF'})
                            channel.connection.shutdown(socket.SHUT_WR)
                            channel._receive()
                self.assertTrue(state['errors'])
                self.assertEqual(state['observer'].native_completions, {})

    def test_retention_failure_cannot_acknowledge_success_or_replace_primary(self):
        row, read = self.source('source', b'full source\x00\xff')
        retained = []
        def refuse(_kind, _occurrence, record):
            if record['kind'] == 'native-preparation-receive':
                retained.append(record)
                raise OSError('controlled native retention failure')
        primary = KeyboardInterrupt('original preparation interruption')
        with self.exchange([row], retain=refuse) as (channel, state):
            with self.assertRaises(KeyboardInterrupt) as caught:
                with channel:
                    try:
                        channel.retain_read('source', row['binding']['path'], read)
                    except Exception:
                        raise primary
        self.assertIs(caught.exception, primary)
        self.assertTrue(any('retention also failed' in note for note in primary.__notes__))
        self.assertTrue(state['errors'])
        self.assertTrue(retained)
        self.assertEqual(retained[0]['helperRead']['bytes'], optional_bytes(b'full source\x00\xff'))
        self.assertTrue(retained[0]['transferDescriptorsClosed'])
        self.assertEqual(state['observer'].native_completions, {})


@unittest.skipUnless(os.environ.get('WORLDLINE_PRIVATE_EVALUATOR_TEST') == '1',
                     'original controlled user-systemd integration prerequisite')
class EntryRetentionIntegration(unittest.TestCase):
    def setUp(self):
        from test_private_evaluator import PrivateEvaluatorIntegration
        PrivateEvaluatorIntegration.setUp(self)

    def test_real_examiner_receive_and_ack_are_distinct_from_original_startup(self):
        from test_private_evaluator import PrivateEvaluatorIntegration
        result = PrivateEvaluatorIntegration.run_examiner(self, b'ordinary worker complete\n', 'retained-entry')
        self.assertEqual(result['exitCode'], 0, result['stdout'] + result['stderr'])
        self.assertIn(b'failures="0"', (result['reportDirectory'] / 'report').read_bytes())
        records = result['boundary']['daemonRoleObservations']
        startup = [r for r in records if r['kind'] == 'role-startup' and r['roleClaim'] == 'examiner']
        preparation = [r for r in records if r['kind'] == 'examiner-entry-preparation-receive']
        acknowledgement = [r for r in records if r['kind'] == 'examiner-entry-retention-acknowledgement']
        self.assertEqual(len(startup), 1)
        self.assertEqual(len(preparation), 1)
        self.assertEqual(len(acknowledgement), 1)
        row = preparation[0]
        self.assertEqual(row['startupRecordId'], startup[0]['recordId'])
        self.assertEqual(acknowledgement[0]['recordId'], row['recordId'])
        self.assertTrue(row['transferDescriptorsClosed'])
        self.assertIsNone(row['exception'])
        self.assertTrue(row['helperReport']['compile']['returned'])
        self.assertEqual(row['helperReport']['read']['bytes'],
                         result['boundary']['daemonExaminerEntrySource']['bytes'])
        self.assertFalse(row['confinementEstablished'])
        self.assertEqual((self.source / 'source.txt').read_text(), 'ordinary source\n')


if __name__ == '__main__':
    unittest.main()
