"""Ordinary owned acquisition/cleanup controls; no host services or proof claim."""
import base64
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
        adapter.journalctl = '/owned/ordinary-journal-command'
        adapter.environment = {}
        unit = 'worldline-11111111-1111-1111-1111-111111111111.service'
        first = b'ordinary non-JSON diagnostic line\n'
        second = json.dumps({'_SYSTEMD_UNIT': f'user@{os.getuid()}.service',
            '_COMM': 'systemd', 'UNIT': unit, '__REALTIME_TIMESTAMP': '0',
            'MESSAGE_ID': adapter.JOURNAL_STARTED, 'MESSAGE': 'ordinary start'}).encode() + b'\n'
        replies = [subprocess.CompletedProcess([], 0, first, b'first stderr\n'),
                   subprocess.CompletedProcess([], 0, second, b'second stderr\n')]
        process = SimpleNamespace(unit=unit, launched_at_us=0,
                                  launcher=SimpleNamespace(stderr=None))
        captured = []
        with patch('worldline.linux.systemd.subprocess.run', side_effect=replies), \
             patch('worldline.linux.systemd.time.monotonic', return_value=0), \
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
        staged = SimpleNamespace(items=[object()], staging=self.root/'verifiers',
            identity=lambda: 'owned-verifier', reread=lambda: ('owned-verifier', []),
            as_evidence=lambda: {'identity': 'owned-verifier'}, close=Mock())
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
