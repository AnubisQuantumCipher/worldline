"""Real owned-journal compatibility controls; no confinement or proof claim."""
from dataclasses import replace
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest

from worldline.completion_kernel import BoundValue
from worldline.core import Core
from worldline.evaluation_pending import PendingJournal, identity
from worldline.evaluation_terminal import (
    RAW_CAPTURE, TerminalJournal, TerminalRefused, bytes_value, value_bytes,
)
from worldline.evaluation_writer import EngineEvaluationWriter
from worldline.linux.kernel_role_observer import KernelRoleObserver
from worldline.linux.private_evaluator import (
    MAX_REQUEST_BYTES, MAX_TREE_BYTES, BOOTSTRAP_HANDSHAKE_SECONDS,
    VERIFIER_MOUNT, PrivateEvaluationSpec, PrivateEvaluator,
    _PrivateAcquisitions,
)
from worldline.raw_observation import optional_bytes


LIBRARY = Path(os.environ['WORLDLINE_CORE_LIB']).resolve()
ORIGINAL_SITES = (
    'legacy-process-return', 'legacy-process-exception', 'legacy-report',
    'private-process-return', 'private-report-binding', 'private-report',
    'private-collection-exception', 'invocation-exception',
    'legacy-supervision-acquisition', 'private-supervision-acquisition',
)


class PrivateAcquisitionTerminal(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='worldline-private-terminal-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.pending = PendingJournal(
            self.root / 'pending-j.db', self.root / 'pending-t.db',
            store_id='owned', library=LIBRARY, create=True)
        self.addCleanup(self.pending.close)
        self.terminal = TerminalJournal(
            self.pending, self.root / 'terminal-j.db', self.root / 'terminal-t.db',
            library=LIBRARY, create=True)
        self.addCleanup(lambda: self.terminal.close())
        self.core = Core(LIBRARY)

    def writer(self, subject='world'):
        writer = EngineEvaluationWriter(self.terminal, 'content')
        writer.begin({'instanceId': subject}, {'requirementHash': 'req'},
            'private-acquisition-control', measured={
                'worldInstance': subject, 'contentId': 'content',
                'observedContentRoot': 'same-root', 'scratchId': 'scratch'},
            declarations={}, core=self.core)
        writer.invocation_started(world_instance='scratch', check='check',
            invocation='private-invocation', candidate_snapshot=None, verifier_entries=())
        return writer

    def retain(self, writer, kind, occurrence, observed):
        writer.invocation_raw(world_instance='scratch', check='check', kind=kind,
                              occurrence=occurrence, observed=observed)

    def rows(self, table='invocation_acquisitions'):
        return [tuple(row) for row in self.terminal.journal.execute(
            'SELECT * FROM main.' + table + ' ORDER BY rowid')]

    def refused(self, code, action):
        with self.assertRaises(TerminalRefused) as caught:
            action()
        self.assertEqual(str(caught.exception), code)

    def legacy_stream(self):
        handle = self.pending.begin('legacy-world', 'content', 'req')
        epoch = handle.epoch
        bound = BoundValue(identity(handle.store_id), identity(handle.subject),
            identity(handle.content), identity(handle.run),
            epoch.to_bytes((epoch.bit_length() + 7) // 8, 'little'), identity('req'))
        self.terminal.open_stream(bound, b'owned', value_bytes({'source': 'legacy'}))
        self.terminal.observe_start(bound, 'legacy-invocation', {'checkId': 'check'})
        with self.terminal._transaction(self.terminal.journal, 'journal'):
            self.terminal.journal.execute(RAW_CAPTURE)
        return bound

    def test_actual_audit_entry_and_kernel_callbacks_keep_complete_owned_records(self):
        writer = self.writer()
        runtime = self.root / 'private'
        verifiers = runtime / 'verifiers'
        verifiers.mkdir(parents=True)
        source = b'pass\n'
        entry = verifiers / 'examiner.py'
        entry.write_bytes(source)
        spec = PrivateEvaluationSpec(
            run_id='private-invocation', roots={'/work': self.root / 'candidate'},
            verifier_directory=verifiers,
            argv=('/usr/bin/python3', VERIFIER_MOUNT + '/examiner.py'), cwd='/work',
            report_directory=runtime / 'report', runtime=runtime,
            verifier_digests={'examiner.py': hashlib.sha256(source).hexdigest()})
        retain = lambda kind, occurrence, record: self.retain(writer, kind, occurrence, record)
        before = PrivateEvaluator._audit_copy(spec, 'before', retain)
        binding, read = PrivateEvaluator._entry_source(spec, retain)
        after = PrivateEvaluator._audit_copy(spec, 'after', retain)
        self.assertTrue(before['clean'], before['findings'])
        self.assertTrue(after['clean'], after['findings'])
        self.assertEqual(read['bytes'], optional_bytes(source))
        self.assertEqual(binding['sourceRecordId'], read['recordId'])

        # Exercise the actual owned retention callback, without claiming a kernel
        # measurement or starting its listener/roles from this finite control.
        observer = KernelRoleObserver({'runtime': str(runtime)},
            maximum_bytes=MAX_TREE_BYTES, maximum_request=MAX_REQUEST_BYTES,
            handshake_seconds=BOOTSTRAP_HANDSHAKE_SECONDS, observer=retain)
        record = {'kind': 'callback-control', 'bytes': optional_bytes(b'\x00\xff'),
                  'missing': None, 'empty': optional_bytes(b''), 'returned': False}
        original = bytes_value(value_bytes(record))
        observer._retain(record)
        record['bytes']['payload'] = 'changed caller value'
        observer._retain({'kind': 'callback-control-end', 'exception': None})
        expected = (
            ('private-invocation', 'private-examiner-audit', 'before', before),
            ('private-invocation', 'private-examiner-entry-source', 0, read),
            ('private-invocation', 'private-examiner-audit', 'after', after),
            ('private-invocation', 'private-kernel-role-observation', 0, original),
            ('private-invocation', 'private-kernel-role-observation', 1,
             {'kind': 'callback-control-end', 'exception': None}),
        )
        actual = self.terminal.captured_observation_events(writer.bound)
        self.assertEqual(value_bytes(actual), value_bytes(expected))
        self.assertEqual(observer.records[0], original)
        stored = self.rows()
        self.assertEqual([row[3] for row in stored],
                         [value_bytes(item[2]) for item in expected])
        self.assertEqual([row[4] for row in stored],
                         [value_bytes(item[3]) for item in expected])

    def test_actual_child_communication_and_boundary_read_retain_their_shared_ordinals(self):
        writer = self.writer()
        retain = lambda kind, occurrence, record: self.retain(writer, kind, occurrence, record)
        with subprocess.Popen([sys.executable, '-c',
                               "import sys; sys.stdout.buffer.write(b'\\x00\\xff'); "
                               "sys.stderr.buffer.write(b'')"],
                              stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE) as child:
            acquisition = _PrivateAcquisitions(
                SimpleNamespace(run_id='private-invocation'),
                SimpleNamespace(unit='owned-child-control', launcher=child), retain)
            self.assertEqual(acquisition.communicate(10, site='examiner-wait'),
                             (b'\x00\xff', b''))
            self.assertEqual(child.returncode, 0)
            boundary = self.root / 'boundary.json'
            original = b'{"owned": true}\r\n\xff'
            boundary.write_bytes(original)
            self.assertEqual(acquisition.boundary_bytes(boundary), original)
        events = self.terminal.captured_observation_events(writer.bound)
        self.assertEqual([(kind, occurrence) for _, kind, occurrence, _ in events], [
            ('private-communicate-acquisition', 0), ('private-boundary-acquisition', 1)])
        self.assertEqual(events[0][3]['stdout'], optional_bytes(b'\x00\xff'))
        self.assertEqual(events[0][3]['stderr'], optional_bytes(b''))
        self.assertTrue(events[0][3]['communicateReturned'])
        self.assertEqual(events[0][3]['launcherReturncode'], 0)
        self.assertEqual(events[1][3]['bytes'], optional_bytes(original))
        self.assertTrue(events[1][3]['readReturned'])
        self.assertTrue(events[1][3]['readReachedEof'])
        self.assertEqual([row[4] for row in self.rows()],
                         [value_bytes(item[3]) for item in events])

    def test_supplied_before_audit_still_causes_real_after_audit_and_absence_stays_absent(self):
        for audit_lifecycle in (False, True):
            with self.subTest(audit_lifecycle=audit_lifecycle):
                runtime = self.root / str(audit_lifecycle)
                verifiers = runtime / 'verifiers'
                verifiers.mkdir(parents=True)
                path = verifiers / 'examiner.py'
                path.write_bytes(b'pass\n')
                (runtime / 'bootstrap-ready').write_bytes(b'ready')
                (runtime / 'boundary.json').write_bytes(b'{"rolesCompleted":true}')
                spec = PrivateEvaluationSpec(
                    run_id='private-invocation', roots={'/work': self.root / 'candidate'},
                    verifier_directory=verifiers,
                    argv=('/usr/bin/python3', VERIFIER_MOUNT + '/examiner.py'), cwd='/work',
                    report_directory=runtime / 'report', runtime=runtime,
                    verifier_digests={'examiner.py': hashlib.sha256(path.read_bytes()).hexdigest()})
                captured = []
                retain = lambda *args: captured.append(args)
                before = (PrivateEvaluator._audit_copy(spec, 'before', retain)
                          if audit_lifecycle else None)
                path.write_bytes(b'pass\n# changed after before-audit\n')
                with subprocess.Popen([sys.executable, '-c', 'pass'],
                                      stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE) as child:
                    systemd = SimpleNamespace(
                        _show=lambda *_args: {'NoNewPrivileges': 'no', 'MainPID': str(child.pid)},
                        outcome=lambda *_args: {'kind': 'SUPERVISED'})
                    result = PrivateEvaluator(systemd)._collect_observed(
                        spec, SimpleNamespace(unit='owned-collection-control', launcher=child),
                        retain, _audit_before=before)
                self.assertIs(result['examinerAudit']['before'], before)
                phases = [occurrence for kind, occurrence, _ in captured
                          if kind == 'private-examiner-audit']
                if audit_lifecycle:
                    self.assertTrue(before['clean'])
                    self.assertEqual(phases, ['before', 'after'])
                    self.assertFalse(result['examinerAudit']['after']['clean'])
                    self.assertEqual(captured[-1][2], result['examinerAudit']['after'])
                else:
                    self.assertIsNone(result['examinerAudit']['after'])
                    self.assertEqual(phases, [])

    def test_audit_phases_and_kernel_ordinals_remain_distinct_and_reopen_in_order(self):
        writer = self.writer()
        events = (
            ('private-examiner-audit', 'after', {'stage': 'actual first append'}),
            ('private-examiner-audit', 'before', {'stage': 'actual second append'}),
            ('private-examiner-entry-source', 0, {'bytes': optional_bytes(b'')}),
            ('private-kernel-role-observation', 1, {'bytes': None}),
            ('private-kernel-role-observation', 0, {'bytes': optional_bytes(b'\xff')}),
        )
        for kind, occurrence, observed in events:
            self.retain(writer, kind, occurrence, observed)
        expected = tuple(('private-invocation', *item) for item in events)
        self.assertEqual(self.terminal.captured_observation_events(writer.bound), expected)
        self.terminal.close()
        self.terminal = TerminalJournal(
            self.pending, self.root / 'terminal-j.db', self.root / 'terminal-t.db',
            library=LIBRARY)
        self.assertEqual(self.terminal.captured_observation_events(writer.bound), expected)
        self.assertEqual(self.terminal.captured_observations(writer.bound),
                         tuple((invocation, kind, value) for invocation, kind, _, value in expected))

    def test_duplicate_is_idempotent_conflict_preserves_every_prior_byte(self):
        writer = self.writer()
        observed = {'bytes': optional_bytes(b'\xff\x00'), 'absent': None}
        for kind, occurrence in (('private-examiner-audit', 'before'),
                                  ('private-examiner-entry-source', 0),
                                  ('private-kernel-role-observation', 0),
                                  ('private-communicate-acquisition', 0),
                                  ('private-boundary-acquisition', 0)):
            with self.subTest(kind=kind):
                self.retain(writer, kind, occurrence, observed)
                before = self.rows()
                self.retain(writer, kind, occurrence, bytes_value(value_bytes(observed)))
                self.assertEqual(self.rows(), before)
                self.refused('INVOCATION_RAW_OBSERVATION_CONFLICT', lambda:
                    self.retain(writer, kind, occurrence, {'bytes': optional_bytes(b'')}))
                self.assertEqual(self.rows(), before)

    def test_original_sites_keep_all_prior_null_and_integer_occurrences(self):
        writer = self.writer()
        for kind in ORIGINAL_SITES:
            for occurrence in (None, 0, 1, 1 << 256):
                with self.subTest(kind=kind, occurrence=occurrence):
                    self.retain(writer, kind, occurrence, {'site': kind, 'seen': occurrence})
        expected = tuple(('private-invocation', kind, occurrence,
                          {'site': kind, 'seen': occurrence})
                         for kind in ORIGINAL_SITES for occurrence in (None, 0, 1, 1 << 256))
        self.assertEqual(self.terminal.captured_observation_events(writer.bound), expected)

    def test_wrong_site_and_occurrence_domains_refuse_without_mutation(self):
        writer = self.writer()
        before = self.rows()
        invalid = {
            'private-examiner-audit': (None, 0, 1, True, False, '', 'BEFORE', 'unknown', [], {}),
            'private-examiner-entry-source': (None, 1, -1, True, False, 0.0, '0', 'before', [], {}),
            'private-kernel-role-observation': (None, -1, True, False, 0.0, '0', 'before', [], {}),
            'private-communicate-acquisition': (None, -1, True, False, 0.0, '0', 'before', [], {}),
            'private-boundary-acquisition': (None, -1, True, False, 0.0, '0', 'before', [], {}),
        }
        invalid.update({kind: (-1, True, False, 0.0, '', 'before', 'after', [], {})
                        for kind in ORIGINAL_SITES})
        for kind, occurrences in invalid.items():
            for occurrence in occurrences:
                with self.subTest(kind=kind, occurrence=occurrence):
                    self.refused('RAW_CAPTURE_OCCURRENCE_INVALID', lambda:
                        self.retain(writer, kind, occurrence, {'data': 'unretained'}))
                    self.assertEqual(self.rows(), before)
        for kind in ('unknown', '', 'private-examiner-audit-extra', None, [], {}):
            with self.subTest(kind=kind):
                self.refused('RAW_CAPTURE_KIND_INVALID', lambda:
                    self.retain(writer, kind, 0, {'data': 'unretained'}))
                self.assertEqual(self.rows(), before)

    def test_invocation_run_and_binding_checks_still_precede_any_new_row(self):
        writer = self.writer()
        before = self.rows()
        self.refused('ENGINE_INVOCATION_START_MISSING', lambda:
            writer.invocation_raw(world_instance='scratch', check='missing',
                kind='private-examiner-audit', occurrence='before', observed={}))
        self.refused('INVOCATION_START_ABSENT', lambda:
            self.terminal.observe_raw(writer.bound, 'missing', 'private-examiner-audit',
                                      {}, occurrence='before'))
        self.refused('CAPTURE_STREAM_ABSENT', lambda:
            self.terminal.observe_raw(replace(writer.bound, run=identity('different-run')),
                'private-invocation', 'private-examiner-audit', {}, occurrence='before'))
        self.refused('CAPTURE_STREAM_BINDING_CONFLICT', lambda:
            self.terminal.observe_raw(replace(writer.bound, content=identity('different-content')),
                'private-invocation', 'private-examiner-audit', {}, occurrence='before'))
        self.assertEqual(self.rows(), before)

    def test_interruption_keeps_raw_phases_and_no_completion_or_promotion(self):
        writer = self.writer()
        observations = [('private-examiner-audit', 'before', {'clean': True}),
                        ('private-examiner-entry-source', 0, {'bytes': optional_bytes(b'')}),
                        ('private-kernel-role-observation', 0, {'confinementEstablished': False})]
        for kind, occurrence, observed in observations:
            self.retain(writer, kind, occurrence, observed)
        before = self.rows()
        writer.interrupted(RuntimeError('retained incomplete private evaluation'))
        row = self.terminal.snapshot('world')['history'][0]
        self.assertEqual(row['evaluationState'], 'ERROR')
        self.assertIsNone(row['outcome'])
        self.assertEqual(row['results'], [])
        self.assertNotIn('evaluation-complete', [item['id'] for item in row['partialResults']])
        self.assertEqual(row['partialResults'][0]['engineRawObservations'], [
            {'kind': kind, 'occurrence': occurrence, 'observation': observed}
            for kind, occurrence, observed in observations])
        self.assertEqual(self.rows(), before)
        self.refused('TERMINAL_STREAM_ALREADY_CLOSED', lambda:
            self.retain(writer, 'private-examiner-audit', 'after', {'clean': True}))
        self.assertEqual(self.rows(), before)

    def test_legacy_schema_refuses_phase_loss_and_existing_upgrade_preserves_rows(self):
        bound = self.legacy_stream()
        payload = {'bytes': optional_bytes(b'\x00\xff'), 'absent': None}
        self.terminal.observe_raw(bound, 'legacy-invocation', 'legacy-process-return', payload)
        original = self.rows('invocation_observations')
        for kind, occurrence in (('private-examiner-audit', 'before'),
                                  ('private-examiner-entry-source', 0),
                                  ('private-kernel-role-observation', 0),
                                  ('private-communicate-acquisition', 0),
                                  ('private-boundary-acquisition', 0)):
            self.refused('RAW_CAPTURE_OCCURRENCE_SCHEMA_REQUIRED', lambda:
                self.terminal.observe_raw(bound, 'legacy-invocation', kind, payload,
                                          occurrence=occurrence))
        self.assertEqual(self.rows('invocation_observations'), original)
        self.assertEqual(self.terminal.captured_observation_events(bound),
                         (('legacy-invocation', 'legacy-process-return', None, payload),))
        self.terminal.enable_raw_capture()
        self.terminal.enable_raw_capture()
        self.assertEqual(self.rows('invocation_observations'), original)
        self.terminal.observe_raw(bound, 'legacy-invocation', 'private-examiner-audit',
                                  payload, occurrence='before')
        self.assertEqual(self.terminal.captured_observation_events(bound), (
            ('legacy-invocation', 'legacy-process-return', None, payload),
            ('legacy-invocation', 'private-examiner-audit', 'before', payload)))

    def test_extended_readback_refuses_malformed_stored_identity_without_repairing_it(self):
        writer = self.writer()
        self.retain(writer, 'private-examiner-audit', 'before', {'absent': None})
        for kind, occurrence, code in (
            ('private-examiner-audit', None, 'RAW_CAPTURE_OCCURRENCE_INVALID'),
            ('private-examiner-audit', 'unknown', 'RAW_CAPTURE_OCCURRENCE_INVALID'),
            ('private-examiner-entry-source', True, 'RAW_CAPTURE_OCCURRENCE_INVALID'),
            ('private-kernel-role-observation', -1, 'RAW_CAPTURE_OCCURRENCE_INVALID'),
            ('private-communicate-acquisition', None, 'RAW_CAPTURE_OCCURRENCE_INVALID'),
            ('private-boundary-acquisition', True, 'RAW_CAPTURE_OCCURRENCE_INVALID'),
            ('unknown', 0, 'RAW_CAPTURE_KIND_INVALID')):
            with self.subTest(kind=kind, occurrence=occurrence):
                with self.terminal._transaction(self.terminal.journal, 'journal'):
                    self.terminal.journal.execute(
                        'UPDATE main.invocation_acquisitions SET kind=?,occurrence=?',
                        (kind, value_bytes(occurrence)))
                before = self.rows()
                self.refused(code, lambda: self.terminal.captured_observation_events(writer.bound))
                self.refused(code, lambda: self.terminal.captured_observations(writer.bound))
                self.assertEqual(self.rows(), before)

    def test_legacy_readback_validates_kind_and_implicit_null_identity(self):
        bound = self.legacy_stream()
        self.terminal.observe_raw(bound, 'legacy-invocation', 'legacy-process-return', {})
        for kind, code in (('unknown', 'RAW_CAPTURE_KIND_INVALID'),
                           ('private-examiner-audit', 'RAW_CAPTURE_OCCURRENCE_INVALID'),
                           ('private-examiner-entry-source', 'RAW_CAPTURE_OCCURRENCE_INVALID'),
                           ('private-kernel-role-observation', 'RAW_CAPTURE_OCCURRENCE_INVALID'),
                           ('private-communicate-acquisition', 'RAW_CAPTURE_OCCURRENCE_INVALID'),
                           ('private-boundary-acquisition', 'RAW_CAPTURE_OCCURRENCE_INVALID')):
            with self.subTest(kind=kind):
                with self.terminal._transaction(self.terminal.journal, 'journal'):
                    self.terminal.journal.execute('UPDATE main.invocation_observations SET kind=?', (kind,))
                before = self.rows('invocation_observations')
                self.refused(code, lambda: self.terminal.captured_observation_events(bound))
                self.refused(code, lambda: self.terminal.captured_observations(bound))
                self.assertEqual(self.rows('invocation_observations'), before)


if __name__ == '__main__':
    unittest.main()
