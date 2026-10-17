"""Ordinary owned acquisition/cleanup controls; no host services or proof claim."""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from worldline.checks import CheckRunner
from worldline.linux.systemd import SystemdAdapter
from worldline.raw_observation import (
    ObservationRetentionError, exception_observation, guarded_cleanup,
    optional_bytes, private_return_observation, retention_failed,
)


class RawObservationControls(unittest.TestCase):
    def test_distinct_journal_polls_retain_full_bytes_before_parsing(self):
        adapter = SystemdAdapter.__new__(SystemdAdapter)
        adapter.environment = {}
        unit = 'worldline-11111111-1111-1111-1111-111111111111.service'
        first = b'ordinary non-JSON diagnostic line\n'
        second = json.dumps({'_SYSTEMD_UNIT': f'user@{os.getuid()}.service',
            '_COMM': 'systemd', 'UNIT': unit, '__REALTIME_TIMESTAMP': '0',
            'MESSAGE_ID': adapter.JOURNAL_STARTED, 'MESSAGE': 'ordinary start'}).encode() + b'\n'
        replies = [subprocess.CompletedProcess([], 0, first, b'first stderr\n'),
                   subprocess.CompletedProcess([], 0, second, b'second stderr\n')]
        # Keep the original replies and assertions while exercising the owned
        # Popen transport, which no longer goes through subprocess.run.
        temporary = tempfile.TemporaryDirectory(prefix='worldline-journal-query-')
        self.addCleanup(temporary.cleanup)
        command = Path(temporary.name) / 'ordinary-journal-command'
        command.with_suffix('.json').write_text(json.dumps([
            {'stdout': base64.b64encode(reply.stdout).decode('ascii'),
             'stderr': base64.b64encode(reply.stderr).decode('ascii'),
             'returncode': reply.returncode} for reply in replies]))
        command.write_text('''#!/usr/bin/python3
import base64, json, sys
from pathlib import Path
command = Path(__file__)
counter = command.with_suffix('.count')
index = int(counter.read_text()) if counter.exists() else 0
reply = json.loads(command.with_suffix('.json').read_text())[index]
counter.write_text(str(index + 1))
sys.stdout.buffer.write(base64.b64decode(reply['stdout'], validate=True))
sys.stderr.buffer.write(base64.b64decode(reply['stderr'], validate=True))
raise SystemExit(reply['returncode'])
''')
        command.chmod(0o700)
        adapter.journalctl = str(command)
        process = SimpleNamespace(unit=unit, launched_at_us=0,
                                  launcher=SimpleNamespace(stderr=None))
        captured = []
        with patch('worldline.linux.systemd.time.monotonic', return_value=0), \
             patch('worldline.linux.systemd.time.sleep'):
            result = adapter.outcome(process, 0,
                _raw_observer=lambda occurrence, value: captured.append((occurrence, value)))
        self.assertEqual(result['kind'], 'SUPERVISED')
        self.assertEqual([occurrence for occurrence, _ in captured], [0, 1])
        self.assertEqual([row['stdout'] for _, row in captured],
                         [optional_bytes(first), optional_bytes(second)])
        self.assertEqual([row['stderr'] for _, row in captured],
                         [optional_bytes(b'first stderr\n'), optional_bytes(b'second stderr\n')])
        self.assertTrue(all(row['processReturnObserved'] for _, row in captured))
        self.assertTrue(all(row['unit'] == unit and row['site'] == 'journal-poll'
                            for _, row in captured))

    def test_owned_report_sink_and_close_failures_keep_retention_primary(self):
        with tempfile.TemporaryDirectory(prefix='worldline-raw-owned-') as directory:
            root = Path(directory); report = root/'ordinary-report'
            report.write_bytes(b'owned bytes\n')
            runner = CheckRunner.__new__(CheckRunner)
            check = SimpleNamespace(result=report.name, cwd=None)
            overlay = SimpleNamespace(target=Path('/owned-logical-root'), upper=root)
            sink_error = OSError('owned sink failed')
            def sink(_record): raise sink_error
            real_close = os.close
            def close_then_report(fd):
                real_close(fd)
                raise OSError('owned descriptor cleanup report')
            with patch('worldline.checks.os.close', side_effect=close_then_report):
                with self.assertRaises(ObservationRetentionError) as caught:
                    runner._read_result_file(check, [overlay], overlay.target, _raw_observer=sink)
            self.assertIs(caught.exception.__cause__, sink_error)
            self.assertTrue(any('cleanup also failed' in note
                                for note in caught.exception.__notes__))

    def test_read_exception_with_secondary_sink_failure_cannot_be_missing_report(self):
        with tempfile.TemporaryDirectory(prefix='worldline-raw-read-') as directory:
            root = Path(directory); report = root/'ordinary-report'
            report.write_bytes(b'owned bytes\n')
            runner = CheckRunner.__new__(CheckRunner)
            check = SimpleNamespace(result=report.name, cwd=None)
            overlay = SimpleNamespace(target=Path('/owned-logical-root'), upper=root)
            primary = OSError('owned read failed')
            def sink(_record): raise ValueError('owned sink failed')
            with patch('worldline.checks.os.read', side_effect=primary):
                with self.assertRaises(OSError) as caught:
                    runner._read_result_file(check, [overlay], overlay.target, _raw_observer=sink)
            self.assertIs(caught.exception, primary)
            self.assertTrue(retention_failed(primary))
            self.assertTrue(any('observation retention also failed' in note for note in primary.__notes__))
            self.assertEqual(exception_observation(primary)['exceptionGraph'][0]['notes'],
                             primary.__notes__)

    def test_resource_exit_cannot_replace_capture_failure(self):
        class OwnedGuard:
            def __enter__(self): return self
            def __exit__(self, *_args): raise OSError('owned release failed')
        primary = ObservationRetentionError('owned capture failed')
        with self.assertRaises(ObservationRetentionError) as caught:
            with guarded_cleanup(OwnedGuard()): raise primary
        self.assertIs(caught.exception, primary)
        self.assertTrue(any('resource guard cleanup also failed' in note for note in primary.__notes__))

    def test_actual_backend_path_field_has_owned_full_byte_encoding(self):
        directory = Path('/owned/private-report')
        original = {'stdout': b'', 'stderr': None, 'reportDirectory': directory,
                    'boundary': {'rolesCompleted': True}}
        encoded = private_return_observation(original)
        self.assertIs(original['reportDirectory'], directory)
        self.assertEqual(encoded['reportDirectory']['kind'], 'filesystem-path-observation')
        self.assertEqual(encoded['reportDirectory']['sourceType'], type(directory).__qualname__)
        self.assertEqual(base64.b64decode(encoded['reportDirectory']['bytes']['payload'], validate=True),
                         b'/owned/private-report')
        self.assertEqual(encoded['stdout'], {'encoding': 'base64', 'payload': ''})
        self.assertIsNone(encoded['stderr'])


class PrivateBackendAcquisitionControls(unittest.TestCase):
    """Owned synthetic process replies and temporary files; no launch or host service."""
    def setUp(self):
        from unittest.mock import Mock
        temporary = tempfile.TemporaryDirectory(prefix='worldline-private-acquisition-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root/'bootstrap-ready').write_bytes(b'ready')
        self.boundary = self.root/'boundary.json'
        self.boundary.write_bytes(b'{"rolesCompleted": true}\r\n')
        self.spec = SimpleNamespace(runtime=self.root, run_id='owned-run',
                                    timeout_seconds=20, report_directory=self.root/'report')
        self.process = SimpleNamespace(unit='owned-private-unit', launcher=Mock(returncode=0))
        self.process.launcher.communicate.return_value = (b'full stdout\x00\xff', b'full stderr\n')
        self.systemd = SimpleNamespace(
            _show=Mock(return_value={'NoNewPrivileges': 'no', 'MainPID': 'owned-pid'}),
            stop=Mock(), outcome=Mock(return_value={'kind': 'SUPERVISED'}))
        self.events = []

    def capture(self, kind, occurrence, record):
        # This owned round-trip also catches accidentally unencoded bytes.
        self.events.append((kind, occurrence, json.loads(json.dumps(record))))

    def collect(self, observer=None):
        from worldline.linux.private_evaluator import PrivateEvaluator
        return PrivateEvaluator(self.systemd)._collect_observed(
            self.spec, self.process, self.capture if observer is None else observer)

    def test_boundary_parse_failure_keeps_actual_return_and_original_file_bytes(self):
        raw = b'{ordinary incomplete JSON\r\n'
        self.boundary.write_bytes(raw)
        with self.assertRaises(json.JSONDecodeError):
            self.collect()
        self.assertEqual([(kind, ordinal) for kind, ordinal, _ in self.events],
                         [('private-communicate-acquisition', 0),
                          ('private-boundary-acquisition', 1)])
        returned = self.events[0][2]
        self.assertTrue(returned['communicateReturned'])
        self.assertEqual(returned['stdout'], optional_bytes(b'full stdout\x00\xff'))
        self.assertEqual(returned['stderr'], optional_bytes(b'full stderr\n'))
        self.assertIsNone(returned['exception'])
        boundary = self.events[1][2]
        self.assertEqual(boundary['bytes'], optional_bytes(raw))
        self.assertTrue(boundary['readReturned'])
        self.assertTrue(boundary['readReachedEof'])
        self.systemd.stop.assert_not_called()

    def test_boundary_decode_failure_keeps_undecodable_bytes(self):
        raw = b'{"ordinary": "\xff"}'
        self.boundary.write_bytes(raw)
        with self.assertRaises(UnicodeDecodeError):
            self.collect()
        self.assertEqual(self.events[-1][2]['bytes'], optional_bytes(raw))

    def test_supervision_failure_happens_after_actual_return_retention(self):
        primary = ValueError('owned supervision parse failure')
        def outcome(*_args, **_kwargs):
            self.assertEqual(self.events[0][0], 'private-communicate-acquisition')
            self.assertTrue(self.events[0][2]['communicateReturned'])
            raise primary
        self.systemd.outcome.side_effect = outcome
        with self.assertRaises(ValueError) as caught:
            self.collect()
        self.assertIs(caught.exception, primary)
        self.assertEqual([kind for kind, _ordinal, _record in self.events],
                         ['private-communicate-acquisition'])

    def test_timeout_and_cleanup_returns_have_distinct_truthful_occurrences(self):
        from worldline.linux.private_evaluator import BackendFailure
        timeout = subprocess.TimeoutExpired(['owned-command'], 20,
                                            output=b'available prefix', stderr=None)
        self.process.launcher.communicate.side_effect = [timeout, (b'complete output', b'')]
        with self.assertRaises(BackendFailure) as caught:
            self.collect()
        self.assertEqual(caught.exception.code, 'PRIVATE_EVALUATOR_TIMEOUT')
        self.assertEqual([ordinal for _kind, ordinal, _record in self.events], [0, 1])
        first, second = [record for _kind, _ordinal, record in self.events]
        self.assertFalse(first['communicateReturned'])
        self.assertEqual(first['stdout'], optional_bytes(b'available prefix'))
        self.assertIsNone(first['stderr'])
        self.assertEqual(first['exception']['exceptionType'], 'TimeoutExpired')
        self.assertTrue(second['communicateReturned'])
        self.assertEqual(second['stdout'], optional_bytes(b'complete output'))
        self.assertEqual(second['stderr'], optional_bytes(b''))
        self.assertEqual(second['site'], 'timeout-cleanup')
        self.systemd.stop.assert_called_once_with(self.process.unit)
        self.systemd.outcome.assert_not_called()

    def test_communication_error_survives_stop_error_and_retains_cleanup(self):
        primary = OSError('owned communication failed')
        self.process.launcher.communicate.side_effect = [primary, (b'cleanup stdout', None)]
        self.systemd.stop.side_effect = OSError('owned stop report failed')
        with self.assertRaises(OSError) as caught:
            self.collect()
        self.assertIs(caught.exception, primary)
        self.assertFalse(self.events[0][2]['communicateReturned'])
        self.assertIsNone(self.events[0][2]['stdout'])
        self.assertTrue(self.events[1][2]['communicateReturned'])
        self.assertEqual(self.events[1][2]['stdout'], optional_bytes(b'cleanup stdout'))
        self.assertTrue(any('cleanup also failed' in note for note in primary.__notes__))

    def test_successful_return_sink_failure_stays_primary_through_cleanup(self):
        sink_error = OSError('owned acquisition store failed')
        self.process.launcher.communicate.side_effect = [
            (b'actual returned bytes', None), (b'actual cleanup bytes', b'')]
        def observer(kind, occurrence, record):
            self.capture(kind, occurrence, record)
            if record['site'] == 'examiner-wait':
                raise sink_error
        self.systemd.stop.side_effect = OSError('owned cleanup stop failed')
        with self.assertRaises(ObservationRetentionError) as caught:
            self.collect(observer)
        self.assertIs(caught.exception.__cause__, sink_error)
        self.assertTrue(all(record['communicateReturned'] for _, _, record in self.events))
        self.assertEqual([ordinal for _, ordinal, _ in self.events], [0, 1])
        self.assertEqual(self.events[0][2]['stdout'], optional_bytes(b'actual returned bytes'))
        self.systemd.outcome.assert_not_called()

    def test_cleanup_sink_failure_marks_original_timeout_not_ordinary_refusal(self):
        primary = subprocess.TimeoutExpired(['owned-command'], 20, output=b'prefix', stderr=b'')
        self.process.launcher.communicate.side_effect = [primary, (b'cleanup return', None)]
        def observer(kind, occurrence, record):
            self.capture(kind, occurrence, record)
            if record['site'] == 'timeout-cleanup':
                raise OSError('owned cleanup store failed')
        with self.assertRaises(subprocess.TimeoutExpired) as caught:
            self.collect(observer)
        self.assertIs(caught.exception, primary)
        self.assertTrue(retention_failed(primary))
        self.assertTrue(any('private communication cleanup also failed' in note
                            for note in primary.__notes__))
        self.assertTrue(self.events[1][2]['communicateReturned'])

    def test_communication_exception_sink_failure_keeps_primary_and_available_bytes(self):
        primary = OSError('owned communication failed after partial output')
        primary.output = b'available output'
        primary.stderr = b''
        self.process.launcher.communicate.side_effect = [primary, (b'cleanup return', None)]
        def observer(kind, occurrence, record):
            self.capture(kind, occurrence, record)
            if record['site'] == 'examiner-wait':
                raise OSError('owned exception store failed')
        with self.assertRaises(OSError) as caught:
            self.collect(observer)
        self.assertIs(caught.exception, primary)
        self.assertTrue(retention_failed(primary))
        self.assertFalse(self.events[0][2]['communicateReturned'])
        self.assertEqual(self.events[0][2]['stdout'], optional_bytes(primary.output))
        self.assertEqual(self.events[0][2]['stderr'], optional_bytes(b''))
        self.assertTrue(self.events[1][2]['communicateReturned'])

    def test_partial_boundary_read_keeps_bytes_and_original_error_on_close_failure(self):
        from unittest.mock import Mock
        from worldline.linux.private_evaluator import _PrivateAcquisitions
        primary = OSError('owned boundary read failed')
        stream = Mock()
        stream.read.side_effect = [b'available raw prefix', primary]
        stream.close.side_effect = OSError('owned boundary close failed')
        acquisition = _PrivateAcquisitions(self.spec, self.process, self.capture)
        with patch.object(Path, 'open', return_value=stream):
            with self.assertRaises(OSError) as caught:
                acquisition.boundary_bytes(self.boundary)
        self.assertIs(caught.exception, primary)
        record = self.events[0][2]
        self.assertEqual(record['bytes'], optional_bytes(b'available raw prefix'))
        self.assertFalse(record['readReturned'])
        self.assertFalse(record['readReachedEof'])
        self.assertTrue(any('cleanup also failed' in note for note in primary.__notes__))

    def test_absent_and_empty_communication_bytes_stay_distinct(self):
        self.process.launcher.communicate.return_value = (None, b'')
        result = self.collect()
        self.assertIsNone(self.events[0][2]['stdout'])
        self.assertEqual(self.events[0][2]['stderr'], optional_bytes(b''))
        self.assertIsNone(result['stdout'])
        self.assertEqual(result['stderr'], b'')

    def test_private_runner_threads_acquisitions_to_actual_writer_before_backend_return(self):
        from contextlib import nullcontext
        from unittest.mock import Mock
        from worldline.evaluation_writer import EngineEvaluationWriter
        from worldline.linux.private_evaluator import PrivateEvaluator
        records = []
        terminal = SimpleNamespace(observe_raw=lambda bound, invocation, kind, observed, **kw:
            records.append((bound, invocation, kind, kw.get('occurrence'), observed)))
        writer = EngineEvaluationWriter(terminal, 'owned-content')
        writer.bound = object()
        writer.invocations[('owned-world', 'owned-check')] = ('owned-invocation', {})
        runner = CheckRunner.__new__(CheckRunner)
        runner.systemd = self.systemd
        runner.sandbox = SimpleNamespace(executable='/owned/bwrap-reference')
        runner.gate = SimpleNamespace(guard=lambda _label: nullcontext(), unit_properties=lambda: ())
        staged_source = self.root / 'verifiers' / 'owned-root' / 'examiner.py'
        staged_source.parent.mkdir(parents=True)
        staged_source.write_bytes(b'pass\n')
        member = {'rootKey': 'owned-root', 'path': 'examiner.py',
                  'executedAs': '/run/worldline-verifiers/owned-root/examiner.py',
                  'sha256': hashlib.sha256(staged_source.read_bytes()).hexdigest()}
        staged = SimpleNamespace(items=[object()], staging=self.root/'verifiers',
            identity=lambda: 'owned-verifier', reread=lambda: ('owned-verifier', []),
            as_evidence=lambda: {'identity': 'owned-verifier', 'members': [dict(member)]}, close=Mock())
        check = SimpleNamespace(id='owned-check', kind='tests', required=True,
            format='junit', profile='private-evaluator-v1', covers=())
        overlay = SimpleNamespace(root_key='owned-root', target=Path('/owned-target'), lower=self.root)
        snapshot = {'worldInstance': 'owned-world', 'rootSetHash': 'owned-root-set',
                    'rootManifests': {'owned-root': 'owned-root-observation'}}
        self.systemd.outcome.side_effect = ValueError('owned supervision parse failure')
        def run_owned(evaluator, spec, _properties, **observers):
            # Actual public run wrapper and actual collector; no backend launch.
            return evaluator._collect_observed(self.spec, self.process,
                observers['_acquisition_observer'],
                _supervision_observer=observers.get('_supervision_observer'))
        with patch.object(PrivateEvaluator, '_run', new=run_owned), \
             patch('worldline.checks.prepare_private_report', return_value=self.root/'report'):
            result = runner._run_private(run_id='owned-run', world_instance='owned-world',
                runtime=self.root, cwd=overlay.target, check=check, overlays=[overlay],
                staged=staged, argv=(), rewrites=(), candidate_snapshot=snapshot,
                _observation_writer=writer)
        self.assertEqual(result['resultChannel']['stage'], 'PRIVATE_EVALUATOR_REFUSED')
        returned = next(row for row in records if row[2] == 'private-communicate-acquisition')
        self.assertIs(returned[0], writer.bound)
        self.assertEqual(returned[1], 'owned-invocation')
        self.assertEqual(returned[3], 0)
        self.assertTrue(returned[4]['communicateReturned'])
        self.assertEqual(returned[4]['stdout'], optional_bytes(b'full stdout\x00\xff'))
        self.assertNotIn('private-process-return', [row[2] for row in records])
        staged.close.assert_called_once()


class ProtectedSyntaxReturnTransportControls(unittest.TestCase):
    """Real controller transport with owned backend replies; no native admission claim."""
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='worldline-syntax-return-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.results = [self._backend(phase) for phase in ('before', 'after')]

    def _backend(self, phase):
        return {'stdout': b'full stdout\x00\xff', 'stderr': b'full stderr\r\n',
                'reportDirectory': self.root / (phase + '-report-\udcff'),
                'protectedProviderCapture': {'report': {'sealed': {'bytes':
                    optional_bytes(b'full sealed artifact\x00\xff')}}},
                'boundary': {'rolesCompleted': True}, 'exitCode': 0}

    def _acquire(self, observer=None):
        from worldline.linux import protected_source_parser as parser
        phases = ('before', 'after')
        with patch.object(parser, '_read_examiner_source', return_value=b'fixed helper bytes'), \
             patch.object(parser, '_stage'), patch.object(parser, '_write'), \
             patch.object(parser.PrivateEvaluator, 'run', side_effect=self.results):
            return parser.acquire_protected_source_ast(object(),
                historical_audit={phase: {'runtime': {}, 'files': []} for phase in phases},
                parser_declaration={'original': 'declaration'},
                phase_invocations={phase: {'invocationId': phase} for phase in phases},
                phase_reports={phase: {'directory': self.root / (phase + '-report'),
                    'binding': {'original': phase}} for phase in phases},
                work_directory=self.root / 'syntax', acquisition_observer=observer)

    def test_path_only_transport_keeps_full_bytes_backend_and_other_fields(self):
        from worldline.evaluation_producer import capture, encode
        from worldline.errors import CoreUnavailable
        callbacks = []
        with patch('worldline.raw_observation.private_return_observation',
                   wraps=private_return_observation) as projection:
            controller = self._acquire(lambda *args: callbacks.append(args))
        self.assertEqual(projection.call_count, len(self.results))
        for phase, backend, callback in zip(('before', 'after'), self.results, callbacks):
            row = controller['phases'][phase]
            expected = private_return_observation(backend)['reportDirectory']
            self.assertIsNot(row['result'], backend)
            self.assertIsInstance(backend['reportDirectory'], Path)
            self.assertEqual(row['result']['reportDirectory'], expected)
            self.assertEqual(base64.b64decode(expected['bytes']['payload'], validate=True),
                             os.fsencode(backend['reportDirectory']))
            self.assertEqual(expected['sourceType'], type(backend['reportDirectory']).__qualname__)
            self.assertEqual(set(row['result']), set(backend))
            for key in backend.keys() - {'reportDirectory'}:
                self.assertIs(row['result'][key], backend[key])
            self.assertEqual(callback[:2], ('private-process-return', 0))
            self.assertEqual(row['acquisitions'][0]['observation'], capture(callback[2]))
            self.assertEqual(row['artifact'], backend['protectedProviderCapture']['report']['sealed']['bytes'])
            self.assertEqual(row['artifactSha256'], hashlib.sha256(b'full sealed artifact\x00\xff').hexdigest())
            with self.assertRaisesRegex(CoreUnavailable, 'unsupported operand type: .*Path'):
                capture(backend)
        captured = json.loads(encode(controller))
        for phase in ('before', 'after'):
            self.assertEqual(captured['phases'][phase]['result']['stdout'], optional_bytes(b'full stdout\x00\xff'))
            self.assertEqual(captured['phases'][phase]['result']['stderr'], optional_bytes(b'full stderr\r\n'))

    def test_external_projection_mutation_cannot_change_retained_path_marker(self):
        def observer(_kind, _occurrence, observed):
            observed['reportDirectory']['bytes']['payload'] = 'Y2FsbGJhY2s='
            observed['reportDirectory']['sourceType'] = 'callback replacement'
            observed['reportDirectory'] = {'kind': 'callback replacement'}
        controller = self._acquire(observer)
        for phase, backend in zip(('before', 'after'), self.results):
            row = controller['phases'][phase]
            expected = private_return_observation(backend)['reportDirectory']
            self.assertEqual(row['result']['reportDirectory'], expected)
            self.assertEqual(row['acquisitions'][0]['observation']['reportDirectory'], expected)
            self.assertIsInstance(backend['reportDirectory'], Path)

    def test_callback_replacement_of_backend_field_is_not_overwritten(self):
        def observer(_kind, _occurrence, _observed):
            for backend in self.results:
                backend['reportDirectory'] = 'callback supplied primitive'
        controller = self._acquire(observer)
        for phase, backend in zip(('before', 'after'), self.results):
            self.assertIs(controller['phases'][phase]['result'], backend)
            self.assertEqual(backend['reportDirectory'], 'callback supplied primitive')

    def test_callback_new_path_remains_in_general_refusal_domain(self):
        from worldline.evaluation_producer import encode
        from worldline.errors import CoreUnavailable
        replacement = self.root / 'callback-other-path'
        def observer(_kind, _occurrence, _observed):
            self.results[0]['reportDirectory'] = replacement
        controller = self._acquire(observer)
        self.assertIs(controller['phases']['before']['result'], self.results[0])
        self.assertIs(self.results[0]['reportDirectory'], replacement)
        with self.assertRaisesRegex(CoreUnavailable, 'unsupported operand type: .*Path'):
            encode(controller)

    def test_missing_and_nonpath_field_are_not_projected(self):
        self.results[0].pop('reportDirectory')
        self.results[1]['reportDirectory'] = {'original': 'primitive observation'}
        controller = self._acquire()
        for phase, backend in zip(('before', 'after'), self.results):
            self.assertIs(controller['phases'][phase]['result'], backend)
        self.assertNotIn('reportDirectory', controller['phases']['before']['result'])
        self.assertIs(controller['phases']['after']['result']['reportDirectory'],
                      self.results[1]['reportDirectory'])

    def test_bytearray_streams_keep_original_general_codec_refusal(self):
        from worldline.evaluation_producer import encode
        from worldline.errors import CoreUnavailable
        self.results[0]['stdout'] = bytearray(b'raw stdout\x00\xff')
        self.results[1]['stderr'] = bytearray(b'raw stderr\x00\xff')
        controller = self._acquire()
        self.assertIs(controller['phases']['before']['result']['stdout'], self.results[0]['stdout'])
        self.assertIs(controller['phases']['after']['result']['stderr'], self.results[1]['stderr'])
        for phase in ('before', 'after'):
            with self.assertRaisesRegex(CoreUnavailable, 'unsupported operand type: bytearray'):
                encode(controller['phases'][phase]['result'])

    def test_other_path_refuses_before_callback_and_artifact_extraction(self):
        from worldline.errors import CoreUnavailable
        self.results[0]['otherPath'] = self.root / 'unsupported-other-field'
        callbacks = []
        with self.assertRaisesRegex(CoreUnavailable, 'unsupported operand type: .*Path') as caught:
            self._acquire(lambda *args: callbacks.append(args))
        row = caught.exception.protected_source_syntax_capture['phases']['before']
        self.assertEqual(callbacks, [])
        self.assertIs(row['result'], self.results[0])
        self.assertIsNone(row['artifact'])
        self.assertEqual(row['acquisitions'], [])

    def test_callback_failure_keeps_original_exception_and_partial_raw_result(self):
        primary = RuntimeError('original callback failure')
        def observer(*_args):
            raise primary
        with self.assertRaises(RuntimeError) as caught:
            self._acquire(observer)
        self.assertIs(caught.exception, primary)
        row = primary.protected_source_syntax_capture['phases']['before']
        self.assertIs(row['result'], self.results[0])
        self.assertIsNone(row['artifact'])
        self.assertIsInstance(row['result']['reportDirectory'], Path)
        self.assertEqual(len(row['acquisitions']), 1)

    def test_artifact_decode_failure_precedes_result_transport_copy(self):
        import binascii
        self.results[0]['protectedProviderCapture']['report']['sealed']['bytes']['payload'] = '!'
        callbacks = []
        with self.assertRaises(binascii.Error) as caught:
            self._acquire(lambda *args: callbacks.append(args))
        row = caught.exception.protected_source_syntax_capture['phases']['before']
        self.assertEqual(len(callbacks), 1)
        self.assertIs(row['result'], self.results[0])
        self.assertIsInstance(row['result']['reportDirectory'], Path)
        self.assertEqual(row['artifact']['payload'], '!')
        self.assertNotIn('artifactSha256', row)

    def test_declared_driver_bytes_match_actual_controller_without_parser_change(self):
        from worldline.linux import protected_source_parser as parser
        package = Path(parser.__file__).parent.parent
        selected = json.loads((package / 'source_syntax_selection.json').read_bytes())
        self.assertEqual(base64.b64decode(selected['driverBytes']['payload'], validate=True),
                         Path(parser.__file__).read_bytes())
        self.assertEqual(base64.b64decode(selected['parserBytes']['payload'], validate=True),
                         Path(parser.__file__).with_name(parser.HELPER_NAME).read_bytes())


    def test_fspath_replacement_does_not_bind_original_marker_to_new_path(self):
        from worldline.evaluation_producer import encode
        from worldline.errors import CoreUnavailable
        backend = self.results[0]
        replacement = self.root / 'fspath-replacement'
        class MutatingPath(type(Path())):
            def __fspath__(self):
                backend['reportDirectory'] = replacement
                return super().__fspath__()
        original = MutatingPath(str(self.root / 'fspath-original-\udcff'))
        backend['reportDirectory'] = original
        expected_bytes = os.fsencode(str(original))
        controller = self._acquire()
        row = controller['phases']['before']
        self.assertIs(row['result'], backend)
        self.assertIs(backend['reportDirectory'], replacement)
        marker = row['acquisitions'][0]['observation']['reportDirectory']
        self.assertEqual(marker['sourceType'], type(original).__qualname__)
        self.assertEqual(base64.b64decode(marker['bytes']['payload'], validate=True), expected_bytes)
        with self.assertRaisesRegex(CoreUnavailable, 'unsupported operand type: .*Path'):
            encode(controller)
