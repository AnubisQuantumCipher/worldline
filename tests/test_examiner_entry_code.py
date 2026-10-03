"""Bound entry/source controls; no global confinement or formal-proof claim."""
from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

from worldline.linux import private_evaluator as evaluator
from worldline.linux.kernel_role_observer import KernelRoleObserver
from worldline.raw_observation import ObservationRetentionError, retention_failed


LOGICAL = evaluator.VERIFIER_MOUNT + '/examiner.py'


def binding_for(source):
    return {'schemaVersion': 1, 'runId': 'entry-control',
            'sourceRecordId': 'source-control', 'path': LOGICAL,
            'sha256': hashlib.sha256(source).hexdigest(), 'byteCount': len(source)}


class EntrySourceAcquisition(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='worldline-entry-source-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.verifiers = self.root / 'verifiers'
        self.verifiers.mkdir()
        self.path = self.verifiers / 'examiner.py'
        self.spec = evaluator.PrivateEvaluationSpec(
            run_id='entry-control', roots={'/work': self.root / 'candidate'},
            verifier_directory=self.verifiers, argv=('/usr/bin/python3', LOGICAL),
            cwd='/work', report_directory=self.root / 'report', runtime=self.root)

    def payload(self, record):
        return base64.b64decode(record['bytes']['payload'], validate=True)

    def assert_closed(self, record):
        rows = record['directories'] + ([record['file']] if record['file'] else [])
        self.assertTrue(rows)
        for row in rows:
            self.assertTrue(row['closed'])
            self.assertIsNone(row['closeException'])
            with self.assertRaises(OSError):
                os.fstat(row['descriptor'])

    def test_empty_and_non_utf8_bytes_are_acquired_without_decoding(self):
        for source in (b'', b'\x00\xff\r\nsource bytes'):
            with self.subTest(source=source):
                self.path.write_bytes(source)
                records = []
                binding, record = evaluator.PrivateEvaluator._entry_source(
                    self.spec, lambda *args: records.append(args))
                self.assertEqual(records, [('private-examiner-entry-source', 0, record)])
                self.assertEqual(self.payload(record), source)
                self.assertTrue(record['readReturned'])
                self.assertTrue(record['readReachedEof'])
                self.assertIsNone(record['exception'])
                self.assertEqual(binding['sourceRecordId'], record['recordId'])
                self.assertEqual(binding['sha256'], hashlib.sha256(source).hexdigest())
                self.assertEqual(binding['byteCount'], len(source))
                self.assertIsNone(self.spec.verifier_digests)
                self.assert_closed(record)

    def test_missing_entry_retains_absence_and_failure_before_raising(self):
        retained = []
        with self.assertRaises(FileNotFoundError) as raised:
            evaluator.PrivateEvaluator._entry_source(self.spec, lambda *args: retained.append(args))
        record = retained[0][2]
        self.assertIs(record, raised.exception.examiner_entry_observation)
        self.assertIsNone(record['bytes'])
        self.assertIsNone(record['binding'])
        self.assertFalse(record['readReturned'])
        self.assertFalse(record['readReachedEof'])
        self.assertIsNotNone(record['exception'])
        self.assert_closed(record)

    def test_direct_backend_failure_keeps_the_actual_available_source_record(self):
        with self.assertRaises(FileNotFoundError) as raised:
            evaluator.PrivateEvaluator._entry_source(self.spec, None)
        self.assertIsNotNone(raised.exception.examiner_entry_observation['exception'])
        self.assertIsNone(raised.exception.examiner_entry_observation['bytes'])

    def test_source_and_ancestor_links_special_objects_and_original_cap_refuse(self):
        regular = self.root / 'regular'
        regular.write_bytes(b'pass\n')
        for kind in ('symlink', 'hardlink', 'directory', 'fifo', 'oversize'):
            with self.subTest(kind=kind):
                if kind == 'symlink':
                    self.path.symlink_to(regular)
                elif kind == 'hardlink':
                    os.link(regular, self.path)
                elif kind == 'directory':
                    self.path.mkdir()
                elif kind == 'fifo':
                    os.mkfifo(self.path)
                else:
                    with self.path.open('wb') as stream:
                        stream.truncate(evaluator.MAX_TREE_BYTES + 1)
                record = {}
                with self.assertRaises((OSError, evaluator.BackendFailure)):
                    evaluator._read_examiner_source(self.path, record)
                self.assertFalse(record['readReturned'])
                self.assertIsNotNone(record['exception'])
                self.assert_closed(record)
                if kind == 'directory':
                    self.path.rmdir()
                else:
                    self.path.unlink()
        alias = self.root / 'alias'
        alias.symlink_to(self.verifiers, target_is_directory=True)
        with self.assertRaises(OSError):
            evaluator._read_examiner_source(alias / 'examiner.py', {})

    def test_replaced_file_is_refused_with_the_actual_old_bytes_retained(self):
        source = b'value = "original"\n'
        self.path.write_bytes(source)
        actual_read = os.read
        changed = False

        def replace_after_read(descriptor, size):
            nonlocal changed
            result = actual_read(descriptor, size)
            if not changed:
                changed = True
                self.path.rename(self.verifiers / 'old-entry')
                self.path.write_bytes(b'value = "replacement"\n')
            return result

        retained = []
        with patch.object(evaluator.os, 'read', replace_after_read):
            with self.assertRaises(evaluator.BackendFailure):
                evaluator.PrivateEvaluator._entry_source(self.spec, lambda *args: retained.append(args))
        record = retained[0][2]
        self.assertTrue(record['readReachedEof'])
        self.assertFalse(record['readReturned'])
        self.assertEqual(self.payload(record), source)
        self.assertNotEqual(record['file']['before'], record['file']['edgeAfter'])
        self.assert_closed(record)

    def test_unrelated_ancestor_directory_changes_do_not_change_source_identity(self):
        source = b'pass\n'
        self.path.write_bytes(source)
        actual_read = os.read
        changed = False

        def add_unrelated_child(descriptor, size):
            nonlocal changed
            if not changed:
                changed = True
                (self.root / 'unrelated-directory').mkdir()
            return actual_read(descriptor, size)

        with patch.object(evaluator.os, 'read', add_unrelated_child):
            record = {}
            self.assertEqual(evaluator._read_examiner_source(self.path, record), source)
        self.assertTrue(record['readReturned'])
        self.assert_closed(record)

    def test_retention_failure_escapes_on_success_and_preserves_primary_read_error(self):
        def refuse(*_args):
            raise OSError('controlled evidence write failure')

        self.path.write_bytes(b'pass\n')
        with self.assertRaises(ObservationRetentionError) as raised:
            evaluator.PrivateEvaluator._entry_source(self.spec, refuse)
        self.assertTrue(raised.exception.examiner_entry_observation['readReturned'])
        self.path.unlink()
        with self.assertRaises(FileNotFoundError) as raised:
            evaluator.PrivateEvaluator._entry_source(self.spec, refuse)
        self.assertTrue(retention_failed(raised.exception))
        self.assertFalse(raised.exception.examiner_entry_observation['readReturned'])


class EntryAcknowledgement(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='worldline-entry-ack-')
        self.addCleanup(temporary.cleanup)
        self.binding = binding_for(b'pass\n')
        self.payload = ['/usr/bin/python3', LOGICAL, 'ordinary-argument']
        self.observer = KernelRoleObserver(
            {'runId': 'entry-control', 'argv': self.payload, 'runtime': temporary.name,
             'examinerEntryBinding': self.binding}, maximum_bytes=evaluator.MAX_TREE_BYTES,
            maximum_request=evaluator.MAX_REQUEST_BYTES, handshake_seconds=60)

    def test_daemon_and_examiner_join_the_exact_binding_before_entry_execution(self):
        record = {'recordId': 'role-control'}
        ack = json.loads(self.observer._acknowledgement('examiner', record))
        self.assertEqual(record['examinerEntryBinding'], self.binding)
        self.assertEqual(evaluator._role_acknowledgement(
            ack, 'examiner', self.payload, 'entry-control'), self.binding)
        self.assertEqual(ack['recordId'], record['recordId'])

    def test_worker_and_candidate_keep_the_original_ack_shape(self):
        for role in ('worker', 'candidate'):
            with self.subTest(role=role):
                record = {'recordId': 'role-control'}
                ack = json.loads(self.observer._acknowledgement(role, record))
                self.assertEqual(ack, record)
                self.assertEqual(set(ack), {'recordId'})
                self.assertIsNone(evaluator._role_acknowledgement(
                    ack, role, self.payload, 'entry-control'))

    def test_missing_malformed_cross_run_and_cross_path_bindings_are_refused(self):
        bad = [None, {}, {**self.binding, 'extra': True},
               {**self.binding, 'schemaVersion': True}, {**self.binding, 'byteCount': True},
               {**self.binding, 'byteCount': -1}, {**self.binding, 'sha256': 'not-a-digest'},
               {**self.binding, 'sourceRecordId': ''}, {**self.binding, 'runId': 'another-run'},
               {**self.binding, 'path': evaluator.VERIFIER_MOUNT + '/other.py'}]
        for changed in bad:
            with self.subTest(binding=changed), self.assertRaises(evaluator.BackendFailure):
                evaluator._role_acknowledgement({'recordId': 'role', 'entrySource': changed},
                                               'examiner', self.payload, 'entry-control')
        with self.assertRaises(evaluator.BackendFailure):
            evaluator._role_acknowledgement({'recordId': 'role'}, 'examiner', self.payload, 'entry-control')
        self.observer.plan['examinerEntryBinding'] = {**self.binding, 'runId': 'another-run'}
        with self.assertRaises(evaluator.BackendFailure):
            self.observer._acknowledgement('examiner', {'recordId': 'role'})

    def test_duplicate_json_fields_never_select_one_claim_silently(self):
        for payload in ('{"recordId":"old","recordId":"new"}',
                        '{"entrySource":{"runId":"old","runId":"new"}}'):
            with self.subTest(payload=payload), self.assertRaises(evaluator.BackendFailure):
                json.loads(payload, object_pairs_hook=evaluator._unique_role_fields)


class EntryCodeIdentity(unittest.TestCase):
    def run_source(self, source):
        registry = evaluator._RegisteredExaminerCode()
        code = registry.compile_entry(source, binding_for(source))
        return registry.run_main(code, LOGICAL)

    def test_actual_returned_and_nested_code_objects_are_registered_by_identity(self):
        source = b'def outer():\n    return lambda value: [x for x in value]\n'
        registry = evaluator._RegisteredExaminerCode()
        code = registry.compile_entry(source, binding_for(source))
        pending = [code]
        while pending:
            item = pending.pop()
            self.assertTrue(registry.contains(item))
            self.assertFalse(registry.contains(item.replace()))
            pending.extend(value for value in item.co_consts if type(value) is types.CodeType)
        with self.assertRaises(evaluator.BackendFailure):
            registry.run_main(code.replace(), LOGICAL)
        with self.assertRaises(evaluator.BackendFailure):
            registry.run_main(code, evaluator.VERIFIER_MOUNT + '/other.py')

    def test_source_digest_and_length_must_both_match_before_compilation(self):
        source = b'pass\n'
        for changed in ({**binding_for(source), 'sha256': hashlib.sha256(b'other').hexdigest()},
                        {**binding_for(source), 'byteCount': len(source) + 1}):
            with self.subTest(binding=changed), self.assertRaises(evaluator.BackendFailure):
                evaluator._RegisteredExaminerCode().compile_entry(source, changed)

    def test_encoding_cookie_and_source_future_flags_are_preserved(self):
        result = self.run_source(b'# coding: latin-1\nvalue = "caf\xe9"\n')
        self.assertEqual(result['value'], 'caf\xe9')
        source = b'def annotated(value: int) -> int:\n    return value\n'
        self.assertIs(self.run_source(source)['annotated'].__annotations__['value'], int)
        source = b'from __future__ import annotations\ndef annotated(value: int) -> int:\n    return value\n'
        self.assertEqual(self.run_source(source)['annotated'].__annotations__['value'], 'int')

    def test_runpy_source_namespace_argv_and_main_module_are_preserved(self):
        previous = sys.modules['__main__']
        argv = list(sys.argv)
        result = self.run_source(b'import sys\nseen_main = sys.modules[__name__]\nseen_args = list(sys.argv)\n')
        self.assertIs(sys.modules['__main__'], previous)
        self.assertEqual(sys.argv, argv)
        self.assertEqual(result['__name__'], '__main__')
        self.assertEqual(result['__file__'], LOGICAL)
        self.assertEqual(result['__package__'], '')
        for key in ('__cached__', '__doc__', '__loader__', '__spec__'):
            self.assertIsNone(result[key])
        self.assertIs(result['seen_main'].__dict__['seen_main'], result['seen_main'])
        self.assertEqual(result['seen_args'], [LOGICAL, *argv[1:]])

    def test_main_and_argv_restore_after_exception_or_system_exit(self):
        previous = sys.modules['__main__']
        argv = list(sys.argv)
        for source, failure in ((b'raise RuntimeError("entry exception")\n', RuntimeError),
                                (b'raise SystemExit(0)\n', SystemExit)):
            with self.subTest(source=source), self.assertRaises(failure):
                self.run_source(source)
            self.assertIs(sys.modules['__main__'], previous)
            self.assertEqual(sys.argv, argv)

    def test_original_stdlib_generators_and_direct_data_reads_still_work(self):
        with tempfile.TemporaryDirectory(prefix='worldline-entry-data-') as temporary:
            data = Path(temporary) / 'candidate.txt'
            data.write_text('ordinary candidate data\n')
            source = ('from collections import namedtuple\n'
                      'from dataclasses import dataclass\n'
                      'from enum import Enum\nfrom typing import NamedTuple\n'
                      'from pathlib import Path\n'
                      'Point = namedtuple("Point", "value")\n'
                      '@dataclass\nclass Box:\n    value: str\n'
                      'class Choice(Enum):\n    item = "item"\n'
                      'class Typed(NamedTuple):\n    value: str\n'
                      'text = Path(' + repr(str(data)) + ').read_text()\n'
                      'observed = (Point(text).value, Box(text).value, '
                      'Choice.item.value, Typed(text).value)\n').encode()
            result = self.run_source(source)
            self.assertEqual(result['observed'], ('ordinary candidate data\n',
                'ordinary candidate data\n', 'item', 'ordinary candidate data\n'))
            self.assertEqual(data.read_text(), 'ordinary candidate data\n')


@unittest.skipUnless(os.environ.get('WORLDLINE_PRIVATE_EVALUATOR_TEST') == '1',
                     'original controlled user-systemd integration prerequisite')
class EntryOriginalIntegration(unittest.TestCase):
    def setUp(self):
        from test_private_evaluator import PrivateEvaluatorIntegration
        PrivateEvaluatorIntegration.setUp(self)

    def test_original_private_examiner_retains_bound_source_and_ack_without_admission(self):
        from test_private_evaluator import PrivateEvaluatorIntegration
        result = PrivateEvaluatorIntegration.run_examiner(self, b'ordinary worker complete\n', 'entry-observed')
        self.assertEqual(result['exitCode'], 0, result['stdout'] + result['stderr'])
        self.assertIn(b'failures="0"', (result['reportDirectory'] / 'report').read_bytes())
        source = result['boundary']['daemonExaminerEntrySource']
        self.assertTrue(source['readReturned'])
        self.assertTrue(source['readReachedEof'])
        actual = base64.b64decode(source['bytes']['payload'], validate=True)
        self.assertEqual(source['binding']['sha256'], hashlib.sha256(actual).hexdigest())
        self.assertEqual(source['binding']['byteCount'], len(actual))
        roles = [row for row in result['boundary']['daemonRoleObservations']
                 if row['kind'] == 'role-startup' and row['roleClaim'] == 'examiner']
        self.assertEqual(len(roles), 1)
        self.assertEqual(roles[0]['examinerEntryBinding'], source['binding'])
        self.assertFalse(roles[0]['confinementEstablished'])
        self.assertFalse(result['examinerAudit']['before']['clean'])
        self.assertEqual((self.source / 'source.txt').read_text(), 'ordinary source\n')


if __name__ == '__main__':
    unittest.main()
