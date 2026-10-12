"""Actual native raw closure controls; source enrollment is UNRUN."""
import copy
import unittest
import base64
import hashlib
import json
from pathlib import Path
import tempfile
from worldline.core import Core
from worldline.evaluation_policy import acquisitions_closed


class NativeAcquisitionClosure(unittest.TestCase):
    def setUp(self):
        self.core = Core.shared()
        self.owner = {'subject': 'subject', 'actualUnit': None,
            'launcherReturncode': None, 'cleanupStarted': True,
            'unclosedCommands': [], 'activeControllerCalls': [],
            'streamEofObserved': None, 'launcherStreamsClosed': False,
            'launcherWaitObserved': False, 'launcherPresent': False,
            'timerAlive': False, 'samplerAlive': False, 'streams': [],
            'tailDrains': [], 'tailErrors': [], 'proxyPresent': False,
            'proxyClosed': False, 'proxy': None, 'guardPresent': False,
            'guardReleased': False}
        self.owner.update(controllerCallsAfterClosure=[], launcherStreams=[],
            guardOwned=False, guardDecisionPresent=False,
            guardReleaseReturnObserved=False, guardReleaseAttempted=False)

    def decide(self, acquisitions=()):
        return acquisitions_closed(self.core, 'subject', [self.owner], list(acquisitions))

    def launcher(self):
        self.owner.update(actualUnit='actual-unit', launcherReturncode=0,
            launcherPresent=True, launcherWaitObserved=True, launcherStreamsClosed=True)
        return {'kind': 'agent-launcher-wait', 'observation': {
            'unit': 'actual-unit', 'returncode': 0, 'waitReturnObserved': True}}

    def test_unlaunched_original_owner_can_close_without_inventing_wait(self):
        self.assertTrue(self.decide())
        self.owner['cleanupStarted'] = False
        self.assertFalse(self.decide())

    def test_claimed_wait_cannot_replace_raw_return_or_join_wrong_unit(self):
        wait = self.launcher()
        self.assertFalse(self.decide())
        self.assertTrue(self.decide([wait]))
        wait['observation']['returncode'] = None
        self.assertFalse(self.decide([wait]))
        wait['observation']['returncode'] = 0
        wait['observation']['unit'] = 'another-unit'
        self.assertFalse(self.decide([wait]))
        wait['observation']['unit'] = 'actual-unit'
        self.owner['launcherReturncode'] = None
        self.assertFalse(self.decide([wait]))

    def test_stream_empty_is_not_absent_and_raw_eof_is_required(self):
        wait = self.launcher()
        self.owner['streamEofObserved'] = {'stderr': True}
        self.assertFalse(self.decide([wait]))
        eof = {'kind': 'agent-stderr-read', 'observation': {
            'unit': 'actual-unit', 'bytes': {'encoding': 'base64', 'payload': ''}}}
        self.assertTrue(self.decide([wait, eof]))
        eof['observation']['bytes'] = None
        self.assertFalse(self.decide([wait, eof]))
        eof['observation']['bytes'] = {'encoding': 'base64', 'payload': 'eA=='}
        self.assertFalse(self.decide([wait, eof]))

    def test_actual_live_thread_controller_sampler_timer_and_socket_refuse(self):
        for name, value in [('timerAlive', True), ('samplerAlive', True),
            ('streams', [{'name': 'reader', 'ident': 1, 'alive': True}]),
            ('tailDrains', [{'name': 'tail', 'ident': 2, 'alive': True}]),
            ('activeControllerCalls', [['call', {'unit': 'actual-unit'}]])]:
            old = copy.deepcopy(self.owner[name])
            self.owner[name] = value
            self.assertFalse(self.decide(), name)
            self.owner[name] = old
        self.owner.update(proxyPresent=True, proxyClosed=True,
            proxy={'stopping': True, 'listenerAlive': False, 'handlers': [],
                   'sockets': [{'fileno': -1}], 'handlerErrors': []})
        self.assertTrue(self.decide())
        self.owner['proxy']['sockets'][0]['fileno'] = 5
        self.assertFalse(self.decide())

    def test_late_original_controller_effect_makes_closed_generation_stale(self):
        self.assertTrue(self.decide())
        self.owner['controllerCallsAfterClosure'] = [{'token': 'actual-call',
            'unit': 'actual-unit', 'returned': True, 'exception': None}]
        self.assertFalse(self.decide())

    def test_guard_release_label_needs_actual_callback_and_residual_clear(self):
        self.owner.update(guardPresent=True, guardReleased=True, guardOwned=True)
        self.assertFalse(self.decide())
        self.owner['guardReleaseReturnObserved'] = True
        self.assertTrue(self.decide())
        self.owner['guardDecisionPresent'] = True
        self.assertFalse(self.decide())

    def test_raw_helper_no_wait_or_eof_cannot_be_erased_by_empty_owner_summary(self):
        control = {'kind': 'agent-control-acquisition', 'observation': {
            'processCreatedObserved': True, 'processWaitReturnObserved': True,
            'processWaitReturncode': 0, 'stdoutReachedEof': True, 'stderrReachedEof': True}}
        self.assertTrue(self.decide([control]))
        control['observation']['stderrReachedEof'] = False
        self.assertFalse(self.decide([control]))
        control['observation']['stderrReachedEof'] = True
        control['observation']['processWaitReturncode'] = None
        self.assertFalse(self.decide([control]))

    def cgroup_read(self, payload=b'max\r\n'):
        from unittest.mock import patch
        from worldline.linux.systemd import SystemdAdapter
        adapter = object.__new__(SystemdAdapter)
        observations = []
        with patch.object(Path, 'read_bytes', return_value=payload):
            with adapter.acquisition_scope(observations.append):
                result = adapter._cgroup_value('/owned-fixture', 'memory.max')
        self.assertEqual(result, payload.decode('utf-8').replace('\r\n', '\n').replace('\r', '\n').strip())
        self.assertEqual(len(observations), 1)
        self.assertEqual(set(observations[0]), {'schemaVersion', 'site', 'controlGroup',
            'name', 'path', 'readReturned', 'bytes', 'exception'})
        self.assertEqual(observations[0]['bytes'], {'encoding': 'base64',
            'payload': base64.b64encode(payload).decode('ascii')})
        return {'kind': 'agent-control-acquisition', 'observation': observations[0]}

    def test_original_successful_cgroup_read_closes_without_process_flags(self):
        for payload in (b'max\r\n', b'', b'17\n'):
            with self.subTest(payload=payload):
                acquired = self.cgroup_read(payload)
                self.assertNotIn('processCreatedObserved', acquired['observation'])
                self.assertTrue(self.decide([acquired]))
                self.assertTrue(self.decide([acquired, copy.deepcopy(acquired)]))

    def test_cgroup_read_missing_malformed_or_failed_shape_refuses(self):
        acquired = self.cgroup_read()
        for name in acquired['observation']:
            changed = copy.deepcopy(acquired)
            del changed['observation'][name]
            with self.subTest(missing=name):
                self.assertFalse(self.decide([changed]))
        replacements = [('schemaVersion', True), ('schemaVersion', 2),
            ('site', 'unrecognized-file-read'), ('controlGroup', None),
            ('controlGroup', ''), ('name', b'memory.max'), ('name', ''),
            ('path', '/sys/fs/cgroup/owned-fixture/memory.max'), ('path', b''),
            ('readReturned', False), ('readReturned', 1), ('bytes', None),
            ('bytes', {'encoding': 'base64', 'payload': 'not canonical'}),
            ('bytes', {'encoding': 'base64', 'payload': 'AB=='}),
            ('bytes', {'encoding': 'hex', 'payload': 'eA=='}),
            ('bytes', {'encoding': 'base64', 'payload': 'eA==', 'extra': True}),
            ('exception', {'type': 'OSError', 'message': 'original read/close failed'})]
        for name, value in replacements:
            changed = copy.deepcopy(acquired)
            changed['observation'][name] = value
            with self.subTest(field=name, value=value):
                self.assertFalse(self.decide([changed]))
        changed = copy.deepcopy(acquired)
        changed['observation']['unrecognizedResource'] = 'must not be erased'
        self.assertFalse(self.decide([changed]))

    def failed_cgroup_read(self, error=None):
        """The real producer's record for a read that raised; read_bytes' own context
        manager has closed the handle. This is the Source20 first original error's
        shape: memory.events vanished with the unit's cgroup between `systemctl show`
        and the read, and the retained ENOENT observation kept finalization from ever
        closing an otherwise finished workload."""
        from unittest.mock import patch
        from worldline.linux.systemd import SystemdAdapter
        adapter = object.__new__(SystemdAdapter)
        observations = []
        failure = FileNotFoundError(2, 'No such file or directory') if error is None else error
        with patch.object(Path, 'read_bytes', side_effect=failure):
            with adapter.acquisition_scope(observations.append):
                result = adapter._cgroup_value('/owned-fixture', 'memory.events')
        self.assertIsNone(result)
        self.assertEqual(len(observations), 1)
        self.assertEqual(set(observations[0]), {'schemaVersion', 'site', 'controlGroup',
            'name', 'path', 'readReturned', 'bytes', 'exception'})
        self.assertIs(observations[0]['readReturned'], False)
        self.assertIsNone(observations[0]['bytes'])
        self.assertEqual(observations[0]['exception']['kind'], 'exception-observation')
        self.assertEqual(observations[0]['exception']['exceptionType'], type(failure).__qualname__)
        return {'kind': 'agent-control-acquisition', 'observation': observations[0]}

    def test_original_failed_cgroup_read_is_ended_not_live(self):
        # A read that returned by raising has nothing left to clean up. Its complete
        # retained exception observation is the terminal fact, exactly as the
        # agent-native producer already reads it (honest absence). The owner and
        # every process acquisition still have to close on their own evidence.
        for error in (FileNotFoundError(2, 'No such file or directory'),
                      PermissionError(13, 'Permission denied'),
                      OSError(5, 'Input/output error')):
            with self.subTest(error=type(error).__name__):
                failed = self.failed_cgroup_read(error)
                self.assertTrue(self.decide([failed]))
                self.assertTrue(self.decide([self.cgroup_read(), failed]))
                self.assertTrue(self.decide([failed, copy.deepcopy(failed)]))
        failed = self.failed_cgroup_read()
        control = {'kind': 'agent-control-acquisition', 'observation': {
            'site': 'systemd-show', 'processCreatedObserved': True,
            'processWaitReturnObserved': True, 'processWaitReturncode': 0,
            'stdoutReachedEof': True, 'stderrReachedEof': False}}
        self.assertFalse(self.decide([failed, control]))
        self.owner['cleanupStarted'] = False
        self.assertFalse(self.decide([failed]))

    def test_failed_cgroup_read_partial_or_contradictory_shape_refuses(self):
        failed = self.failed_cgroup_read()
        for name in failed['observation']:
            changed = copy.deepcopy(failed)
            del changed['observation'][name]
            with self.subTest(missing=name):
                self.assertFalse(self.decide([changed]))
        replacements = [
            ('bytes', {'encoding': 'base64', 'payload': ''}),   # bytes beside a failure
            ('bytes', {'encoding': 'base64', 'payload': 'bWF4Cg=='}),
            ('exception', None), ('exception', 'FileNotFoundError'),
            ('exception', {'type': 'OSError', 'message': 'not the producer record'}),
            ('readReturned', True), ('readReturned', None), ('readReturned', 0),
            ('site', 'unrecognized-file-read'), ('schemaVersion', 2), ('schemaVersion', True),
            ('controlGroup', ''), ('controlGroup', None), ('name', ''), ('name', b'memory.events'),
            ('path', b''), ('path', '/sys/fs/cgroup/owned-fixture/memory.events')]
        for name, value in replacements:
            changed = copy.deepcopy(failed)
            changed['observation'][name] = value
            with self.subTest(field=name, value=value):
                self.assertFalse(self.decide([changed]))
        for key in failed['observation']['exception']:
            changed = copy.deepcopy(failed)
            del changed['observation']['exception'][key]
            with self.subTest(missing_exception_field=key):
                self.assertFalse(self.decide([changed]))
        for key, value in [('kind', 'exception'), ('schemaVersion', 2), ('schemaVersion', 0),
                           ('exceptionType', ''), ('exceptionType', None),
                           ('exception', None), ('exceptionGraph', []), ('exceptionGraph', None),
                           ('root', 1), ('root', -1), ('root', None), ('extra', True)]:
            changed = copy.deepcopy(failed)
            changed['observation']['exception'][key] = value
            with self.subTest(exception_field=key, value=value):
                self.assertFalse(self.decide([changed]))
        changed = copy.deepcopy(failed)
        changed['observation']['unrecognizedResource'] = 'must not be erased'
        self.assertFalse(self.decide([changed]))

    def test_successful_file_read_does_not_hide_process_wait_or_eof_failure(self):
        acquired = self.cgroup_read()
        control = {'kind': 'agent-control-acquisition', 'observation': {
            'site': 'systemd-show', 'processCreatedObserved': True,
            'processWaitReturnObserved': True, 'processWaitReturncode': 0,
            'stdoutReachedEof': True, 'stderrReachedEof': True}}
        self.assertTrue(self.decide([acquired, control]))
        for field in ('processCreatedObserved', 'processWaitReturnObserved',
                      'processWaitReturncode', 'stdoutReachedEof', 'stderrReachedEof'):
            changed = copy.deepcopy(control)
            del changed['observation'][field]
            with self.subTest(missing_process_field=field):
                self.assertFalse(self.decide([acquired, changed]))
        for field in ('processWaitReturnObserved', 'stdoutReachedEof', 'stderrReachedEof'):
            changed = copy.deepcopy(control)
            changed['observation'][field] = False
            with self.subTest(incomplete_process_field=field):
                self.assertFalse(self.decide([acquired, changed]))
        spoofed = copy.deepcopy(control)
        spoofed['observation']['site'] = 'cgroup-read'
        self.assertFalse(self.decide([spoofed]))
        for value in (True, False, None):
            changed = copy.deepcopy(acquired)
            changed['observation']['processCreatedObserved'] = value
            self.assertFalse(self.decide([changed]))
        self.owner['cleanupStarted'] = False
        self.assertFalse(self.decide([acquired]))


class ProtectedSyntaxAcquisitionOperands(unittest.TestCase):
    """Real issuer/storage controls; protected native runtime remains required."""

    def test_original_byte_identity_precedes_independent_fresh_phase_starts(self):
        from worldline.evaluation_producer import _source_declaration
        original = b' { "id": "failed", "status": "FAIL", "message": "\\u03bb" } \n'
        observations = []
        with tempfile.TemporaryDirectory() as location:
            work = Path(location)
            declaration, reports = _source_declaration(original, work=work,
                source_context={'originalOperation': b'full-owner-original'},
                observer=lambda kind, occurrence, value:
                    observations.append((kind, occurrence, value)))
            digest = hashlib.sha256(original).hexdigest()
            helper = base64.b64decode(declaration['parserBytes']['payload'], validate=True)
            verifier = hashlib.sha256(helper).hexdigest()
            starts = declaration['phaseInvocations']
            self.assertNotEqual(starts['before']['invocationId'],
                                starts['after']['invocationId'])
            self.assertEqual(observations[0][0], 'source-syntax-declaration')
            self.assertEqual([row[0] for row in observations[1:]],
                ['source-syntax-invocation-start', 'source-syntax-invocation-start'])
            for phase in ('before', 'after'):
                start = starts[phase]
                self.assertEqual(start['candidateScope'], digest)
                self.assertEqual(start['phase'], phase)
                report = declaration['phaseReports'][phase]
                binding = report['binding']
                self.assertEqual(binding, {'runId': start['invocationId'],
                    'checkId': 'worldline-source-syntax-phase',
                    'candidateIdentity': digest, 'verifierIdentity': verifier})
                self.assertEqual(report['directory'], str(reports[phase]['directory']))
                self.assertEqual(json.loads((Path(report['directory']) / '.binding').read_bytes()),
                                 binding)
                self.assertFalse((Path(report['directory']) / 'report').exists())
            # Re-encoding the semantic object is NOT the original identity.
            rebuilt = json.dumps(json.loads(original), separators=(',', ':')).encode()
            self.assertNotEqual(hashlib.sha256(rebuilt).hexdigest(), digest)
            starts['before']['candidateScope'] = 'changed'
            self.assertEqual(observations[0][2]['phaseInvocations']['before']['candidateScope'],
                             digest)

    def test_complete_absent_audit_roster_retains_failure_and_original_bytes(self):
        from worldline.evaluation_producer import acquire_syntax_capsules
        original = [
            b'{"id":"passed","status":"PASS"}',
            b' { "id":"failed", "status":"FAIL" } ',
            b'{"id":"incomplete","exception":"original"}\n',
        ]
        rows = acquire_syntax_capsules(original, systemd=None, gate=None,
            work_directory=Path('/not-used-with-absent-audit'),
            source_context={'originalOperation': b'full-owner-original'})
        self.assertEqual([row['result'] for row in rows], original)
        for row in rows:
            self.assertEqual(set(row), {'result', 'declaration', 'capsule'})
            self.assertEqual(row['declaration'], b'null')
            self.assertEqual(row['capsule'], b'null')

    def test_actual_operand_decode_preserves_unbounded_integer_transport(self):
        from worldline.evaluation_producer import _json_operand, encode
        value = 1 << 20000
        operand = {'positive': value, 'negative': -value}
        self.assertEqual(_json_operand(encode(operand)), operand)


class FullAgentTerminalTransport(unittest.TestCase):
    """Transport controls only: these do not establish native source custody."""

    def test_immutable_terminal_bytes_are_not_reencoded_as_projected_json(self):
        from worldline.evaluation_producer import operands
        from worldline.finalization_journal import acquisitions_payload, encode
        capture = {'schema': 'worldline.runner-terminal-v2',
            'bytes': b'\x00\xff', 'tuple': (None, True, 2 ** 1000),
            'floats': [-0.0, float('nan'), float('inf')]}
        terminal = encode(capture)
        result = {'origin': 'agent', 'engineRawObservations':
            acquisitions_payload([{'kind': 'manager-return',
                'observation': {'terminalCapture': capture, 'terminalBytes': terminal}}])}
        values = operands(result, None)
        self.assertEqual(len(values), 5)
        self.assertEqual(values[4], terminal)
        self.assertEqual(encode(capture), values[4])
        self.assertEqual(capture['bytes'], b'\x00\xff')

    def test_full_original_capture_without_byte_adjunct_keeps_lossless_domain(self):
        from worldline.evaluation_producer import operands
        from worldline.finalization_journal import acquisitions_payload, encode
        capture = {'original': (b'\x80', -0.0, 2 ** 1000)}
        result = {'origin': 'agent', 'engineRawObservations':
            acquisitions_payload([{'kind': 'manager-return',
                'observation': {'terminalCapture': capture}}])}
        self.assertEqual(operands(result, None)[4], encode(capture))

    def test_absent_terminal_source_stays_absent_not_a_completed_capture(self):
        from worldline.evaluation_producer import operands
        from worldline.finalization_journal import acquisitions_payload
        for observations in (None, acquisitions_payload([]),
                acquisitions_payload([{'kind': 'manager-return', 'observation': {}}])):
            result = {'origin': 'agent', 'engineRawObservations': observations}
            self.assertEqual(operands(result, None)[4], b'')


class AgentSourceStorageLens(unittest.TestCase):
    """Actual codec correspondence only; no synthetic source authority."""

    def test_harmless_encodable_subclasses_keep_original_full_archive(self):
        from worldline.runner_outcome import _builtin_archive
        from worldline.finalization_journal import encode

        class Supervisor(dict):
            pass

        class Word(str):
            pass

        value = Supervisor(kind=Word('SUPERVISED'), launcherExit=0,
                           result=Word('success'), events=[])
        self.assertEqual(_builtin_archive(value), encode(value))

    def test_storage_lens_does_not_dispatch_foreign_container_overrides(self):
        from worldline.runner_outcome import _builtin_archive
        from worldline.finalization_journal import encode

        class Supervisor(dict):
            def items(self):
                raise AssertionError('foreign items must not be reacquired')

            def __iter__(self):
                raise AssertionError('foreign iteration must not be reacquired')

        class Events(list):
            def __iter__(self):
                raise AssertionError('foreign iteration must not be reacquired')

        value = Supervisor(kind='SUPERVISED', events=Events([None, -0.0, 2 ** 1000]))
        expected = {'kind': 'SUPERVISED', 'events': [None, -0.0, 2 ** 1000]}
        self.assertEqual(_builtin_archive(value), encode(expected))
