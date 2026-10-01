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
