"""Ordinary owned temporary-store controls, prepared and never run in this draft.
These finite controls do not establish producer provenance or a full proof.
"""
import ctypes
import os
from pathlib import Path
import tempfile
import unittest
from dataclasses import replace

from worldline.core import Core
from worldline.completion_kernel import BoundValue, CaptureValue, CheckValue, CompletionKernel, LAYOUTS
from worldline.evaluation_pending import PendingJournal, identity
from worldline.evaluation_terminal import TerminalJournal, TerminalRefused, value_bytes, bytes_value
from worldline.evaluation_writer import EngineEvaluationWriter
from worldline.evaluation_history import EvaluationRecord, EvaluationCursor, EvaluationQuery, select_history
from worldline.finalize import CheckDeclaration

LIBRARY = Path(os.environ['WORLDLINE_CORE_LIB']).resolve()

class TerminalControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='worldline-terminal-ordinary-')
        self.root = Path(self.temp.name)
        self.pending = PendingJournal(self.root/'pending-j.db', self.root/'pending-t.db', store_id='owned', library=LIBRARY, create=True)
        self.terminal = TerminalJournal(self.pending, self.root/'terminal-j.db', self.root/'terminal-t.db', library=LIBRARY, create=True)
        self.core = Core(LIBRARY)

    def tearDown(self):
        self.terminal.close(); self.pending.close(); self.temp.cleanup()

    def bound(self, handle, requirement='req'):
        e = handle.epoch
        return BoundValue(identity(handle.store_id), identity(handle.subject), identity(handle.content),
                          identity(handle.run), e.to_bytes((e.bit_length()+7)//8, 'little'),
                          None if requirement is None else identity(requirement))

    def observation(self, handle, outcome='FAIL', requirement='req'):
        bound = self.bound(handle, requirement)
        capture = CaptureValue(bound, b'ordinary-control', value_bytes({'requirementHash': requirement}), 'Completed', outcome)
        result = CheckValue(bound, b'check', b'ordinary-control', None, None, 'Completed', outcome,
                            value_bytes({'id': 'check', 'status': outcome}))
        return capture, (result,)

    def test_layout_all_fields(self):
        kernel = CompletionKernel(LIBRARY)
        for kind, record in enumerate(LAYOUTS, 1):
            self.assertEqual(kernel.library.wl_completion_layout_size_v1(kind), ctypes.sizeof(record))
            self.assertEqual(kernel.library.wl_completion_layout_alignment_v1(kind), ctypes.alignment(record))
            for field, (name, _) in enumerate(record._fields_, 1):
                self.assertEqual(kernel.library.wl_completion_layout_offset_v1(kind, field), getattr(record, name).offset)

    def test_reserved_head_retains_older_failure_and_reconciles(self):
        older = self.pending.begin('world', 'content', 'req')
        newer = self.pending.reserve_pending('world', 'content', 'req')
        capture, results = self.observation(older)
        self.terminal.retain(capture, results)
        self.assertEqual([x.run for x in self.terminal.discover()], [older.run])
        self.terminal.replay(older.run)
        self.assertEqual(self.pending.pending_snapshot('world')['history'][-1]['validationId'], newer.run)
        passed, pass_results = self.observation(newer, 'PASS')
        self.terminal.complete(passed, pass_results)
        rows = self.terminal.snapshot('world')['history']
        self.assertEqual([row['outcome'] for row in rows], ['FAIL', 'PASS'])
        selection = select_history([EvaluationRecord(row['worldInstance'], row['worldContentId'], row['requirementHash'],
            row['validationId'], row['evaluationEpoch'], row['evaluationState'], row['outcome']) for row in rows], None,
            EvaluationQuery('world', 'content', 'req', EvaluationCursor(newer.epoch, newer.run), EvaluationCursor(newer.epoch, newer.run)), core=self.core)
        self.assertEqual(selection.reason, 'EVIDENCE_FAIL_TERMINAL')
        self.assertEqual(self.terminal.discover(), ())

    def test_replay_exact_and_terminal_conflict(self):
        handle = self.pending.begin('world', 'content', '')
        capture, results = self.observation(handle, requirement='')
        self.terminal.complete(capture, results)
        self.terminal.complete(capture, results)
        before = self.terminal.snapshot('world')
        with self.assertRaises(TerminalRefused): self.terminal.retain(replace(capture, outcome='PASS'), results)
        self.assertEqual(self.terminal.snapshot('world'), before)

    def test_nullable_incomplete_and_owned_value_roundtrip(self):
        handle = self.pending.begin('world', 'content', None)
        value = {'text':'\ud800\x00', 'empty':'', 'values':[True, False, None, -0.0], 'array':[]}
        self.assertEqual(value_bytes(bytes_value(value_bytes(value))), value_bytes(value))
        capture = CaptureValue(self.bound(handle, None), b'', value_bytes(value), 'Incomplete_Unknown', None)
        self.terminal.complete(capture, ())
        row = self.terminal.snapshot('world')['history'][0]
        self.assertEqual(row['evaluationState'], 'ERROR')
        self.assertIsNone(row['requirementHash'])
        self.assertEqual(value_bytes(row['context']), value_bytes(value))

    def writer(self, subject='writer'):
        writer = EngineEvaluationWriter(self.terminal, 'content')
        writer.begin({'instanceId':subject}, {'requirementHash':'req'}, 'ordinary-engine-hook',
            measured={'worldInstance':subject, 'contentId':'content', 'observedContentRoot':'same-root', 'scratchId':'scratch'}, declarations={}, core=self.core)
        return writer

    def entry(self):
        return {'requirementHash':'req', 'results':[], 'context':{'requirementHash':'req'},
                'verifiersModifiedByCandidate':False, 'examinedContentRoot':'same-root', 'outcome':'PASS'}

    def test_actual_writer_empty_declared_completion_record_last(self):
        writer = self.writer()
        answer = writer.finish(self.entry(), raw_results=[], runner_results=[],
            post_measurement={'observedContentRoot':'same-root'}, required=[], empty_declared=True,
            declarations={}, core=self.core)
        self.assertEqual(answer['terminalExecution'], 'Completed')
        self.assertTrue(answer['promotionRosterAdmitted'])
        self.assertEqual(answer['results'][-1]['id'], 'evaluation-complete')
        self.assertEqual(self.terminal.snapshot('writer')['history'][0]['validationId'], writer.handle.run)

    def test_partial_return_is_durable_without_completion_record(self):
        writer = self.writer('partial')
        declaration = CheckDeclaration('engine', None, False, origin='engine')
        writer.declarations = {'first': declaration}
        writer.invocation_started(world_instance='scratch', check='first', invocation='owned-first', candidate_snapshot=None, verifier_entries=())
        first = {'id':'first', 'origin':'engine', 'format':'engine', 'status':'FAIL'}
        writer.invocation_result(world_instance='scratch', check='first', result=first)
        writer.invocation_started(world_instance='scratch', check='second', invocation='owned-second', candidate_snapshot=None, verifier_entries=())
        writer.interrupted(RuntimeError('ordinary later evaluation exception'))
        row = self.terminal.snapshot('partial')['history'][0]
        self.assertEqual(row['evaluationState'], 'ERROR')
        self.assertEqual(row['results'], [])
        self.assertEqual([r['id'] for r in row['partialResults']], ['first','second'])
        self.assertNotIn('evaluation-complete', [r['id'] for r in row['partialResults']])

    def test_genuine_required_fail_preserved_when_other_admission_missing(self):
        writer = self.writer('failed')
        declarations = {'required': CheckDeclaration('engine', None, False, origin='engine'),
                        'other': CheckDeclaration('engine', None, False, origin='engine')}
        # Engine-origin ordinary typed rows; the raw classifier and full kernel
        # execute for real. No fixture supplies an admitted/completed Boolean.
        rows = [{'id':'required','origin':'engine','format':'engine','status':'FAIL'},
                {'id':'other','origin':'external','format':'engine','status':'UNASSESSED'}]
        for row in rows:
            writer.invocation_started(world_instance='scratch', check=row['id'], invocation=row['id'], candidate_snapshot=None, verifier_entries=())
            writer.invocation_result(world_instance='scratch', check=row['id'], result=row)
        answer = writer.finish(self.entry(), raw_results=rows, runner_results=rows,
            post_measurement={'observedContentRoot':'same-root'}, required=['required','other'],
            empty_declared=False, declarations=declarations, core=self.core)
        self.assertEqual(answer['outcome'], 'FAIL')
        self.assertFalse(answer['promotionRosterAdmitted'])
        self.assertEqual(answer['results'][-1]['id'], 'evaluation-complete')


    def test_raw_present_empty_and_absent_before_interruption(self):
        from worldline.raw_observation import optional_bytes, exception_observation
        writer = self.writer('raw-partial')
        writer.invocation_started(world_instance='scratch', check='check', invocation='raw-invocation',
                                  candidate_snapshot=None, verifier_entries=())
        observed = {'stdout': optional_bytes(b''), 'stderr': optional_bytes(None),
                    'processReturnObserved': True, 'launcherReturncode': 0}
        writer.invocation_raw(world_instance='scratch', check='check',
                              kind='legacy-process-return', observed=observed)
        writer.invocation_raw(world_instance='scratch', check='check',
                              kind='legacy-process-return', observed=observed)
        error = RuntimeError('ordinary incomplete observation')
        writer.invocation_exception(world_instance='scratch', check='check', error=error)
        writer.interrupted(error)
        row = self.terminal.snapshot('raw-partial')['history'][0]
        self.assertEqual(row['results'], [])
        raw = row['partialResults'][0]['engineRawObservations']
        self.assertEqual(raw, [
            {'kind': 'legacy-process-return', 'observation': observed},
            {'kind': 'invocation-exception', 'observation': exception_observation(error)}])
        self.assertEqual(raw[0]['observation']['stdout'], {'encoding': 'base64', 'payload': ''})
        self.assertIsNone(raw[0]['observation']['stderr'])
        self.assertEqual(row['partialResults'][0]['kind'], 'invocation-did-not-return')

    def test_owned_legacy_report_bytes_retained_before_return(self):
        from types import SimpleNamespace
        from worldline.checks import CheckRunner
        from worldline.raw_observation import optional_bytes
        writer = self.writer('raw-legacy')
        writer.invocation_started(world_instance='scratch', check='check', invocation='legacy-invocation',
                                  candidate_snapshot=None, verifier_entries=())
        report = self.root / 'ordinary-report'
        original = b'ordinary report bytes\n'
        report.write_bytes(original)
        runner = CheckRunner.__new__(CheckRunner)
        check = SimpleNamespace(result=report.name, cwd=None)
        overlay = SimpleNamespace(target=Path('/owned-logical-root'), upper=self.root)
        returned = runner._read_result_file(check, [overlay], overlay.target,
            _raw_observer=lambda record: writer.invocation_raw(world_instance='scratch', check='check',
                                                kind='legacy-report', observed=record))
        self.assertEqual(returned, original)
        records = self.terminal.captured_observations(writer.bound)
        self.assertEqual([kind for _invocation, kind, _record in records], ['legacy-report'])
        self.assertEqual(records[0][2]['bytes'], optional_bytes(original))
        self.assertTrue(records[0][2]['readReachedEof'])
        self.assertTrue(records[0][2]['readReturned'])
        self.assertEqual(runner._read_result_file(check, [overlay], overlay.target), original)

    def test_owned_private_binding_and_report_bytes_retained(self):
        from worldline.report import prepare_private_report, collect_private_report
        from worldline.raw_observation import optional_bytes
        writer = self.writer('raw-private')
        writer.invocation_started(world_instance='scratch', check='check', invocation='private-invocation',
                                  candidate_snapshot=None, verifier_entries=())
        base = self.root / 'private-reports'
        base.mkdir(mode=0o700)
        directory = prepare_private_report(base, run_id='private-invocation', check_id='check',
            candidate_identity='owned-candidate', verifier_identity='owned-verifier')
        original = b''
        (directory / 'report').write_bytes(original)
        original_binding = (directory / '.binding').read_bytes()
        payload, evidence = collect_private_report(directory, run_id='private-invocation', check_id='check',
            candidate_identity='owned-candidate', verifier_identity='owned-verifier',
            _raw_observer=lambda kind, record: writer.invocation_raw(world_instance='scratch', check='check',
                                                            kind=kind, observed=record))
        self.assertEqual(payload, original)
        records = self.terminal.captured_observations(writer.bound)
        self.assertEqual([kind for _invocation, kind, _record in records],
                         ['private-report-binding', 'private-report'])
        self.assertEqual(records[0][2]['bytes'], optional_bytes(original_binding))
        self.assertEqual(records[1][2]['bytes'], optional_bytes(original))
        self.assertTrue(records[1][2]['readReachedEof'])
        self.assertEqual(collect_private_report(directory, run_id='private-invocation', check_id='check',
            candidate_identity='owned-candidate', verifier_identity='owned-verifier'), (payload, evidence))


    def test_exact_prior_schema_upgrade_is_idempotent_and_preserves_rows(self):
        handle = self.pending.begin('prior-schema', 'content', 'req')
        capture, results = self.observation(handle)
        self.terminal.complete(capture, results)
        before = self.terminal.snapshot('prior-schema')
        tables = ('identity', 'terminal_intents', 'terminal_links', 'capture_streams',
                  'invocation_starts', 'invocation_results')
        original_rows = {name: [tuple(row) for row in self.terminal.journal.execute('SELECT * FROM main.' + name)]
                         for name in tables}
        self.assertIsNone(self.terminal.journal.execute("SELECT name FROM main.sqlite_schema WHERE name='invocation_observations'").fetchone())
        self.terminal.enable_raw_capture()
        self.terminal.enable_raw_capture()
        self.assertIsNotNone(self.terminal.journal.execute("SELECT name FROM main.sqlite_schema WHERE name='invocation_observations'").fetchone())
        self.assertEqual({name: [tuple(row) for row in self.terminal.journal.execute('SELECT * FROM main.' + name)]
                          for name in tables}, original_rows)
        self.assertEqual(self.terminal.snapshot('prior-schema'), before)
        self.assertEqual(list(self.terminal.journal.execute('SELECT * FROM main.invocation_observations')), [])


    def test_distinct_raw_occurrences_exact_replay_and_conflict(self):
        writer = self.writer('raw-occurrences')
        writer.invocation_started(world_instance='scratch', check='check', invocation='poll-invocation',
                                  candidate_snapshot=None, verifier_entries=())
        first = {'site': 'journal-poll', 'stdout': 'first complete owned bytes'}
        second = {'site': 'journal-poll', 'stdout': 'second complete owned bytes'}
        for occurrence, observed in ((0, first), (1, second), (0, first)):
            writer.invocation_raw(world_instance='scratch', check='check',
                kind='legacy-supervision-acquisition', occurrence=occurrence, observed=observed)
        before = self.terminal.captured_observation_events(writer.bound)
        self.assertEqual(before, (
            ('poll-invocation', 'legacy-supervision-acquisition', 0, first),
            ('poll-invocation', 'legacy-supervision-acquisition', 1, second)))
        with self.assertRaises(TerminalRefused):
            writer.invocation_raw(world_instance='scratch', check='check',
                kind='legacy-supervision-acquisition', occurrence=0, observed=second)
        self.assertEqual(self.terminal.captured_observation_events(writer.bound), before)
        writer.interrupted(RuntimeError('ordinary stream stop'))
        row = self.terminal.snapshot('raw-occurrences')['history'][0]
        self.assertEqual(row['results'], [])
        self.assertEqual([r['occurrence'] for r in row['partialResults'][0]['engineRawObservations']], [0, 1])
        self.assertEqual(row['partialResults'][0]['kind'], 'invocation-return-not-retained')
        self.assertIsNone(row['partialResults'][0]['checkReturnObserved'])

    def test_actual_return_is_retried_exactly_before_interrupted_projection(self):
        from unittest.mock import patch
        writer = self.writer('return-observed')
        writer.declarations = {'check': CheckDeclaration('engine', None, False, origin='engine')}
        writer.invocation_started(world_instance='scratch', check='check', invocation='returned-invocation',
                                  candidate_snapshot=None, verifier_entries=())
        returned = {'id': 'check', 'origin': 'engine', 'format': 'engine', 'status': 'FAIL'}
        storage_error = OSError('owned result acknowledgment unavailable')
        with patch.object(self.terminal, 'observe_result', side_effect=storage_error):
            with self.assertRaises(OSError) as caught:
                writer.invocation_result(world_instance='scratch', check='check', result=returned)
        self.assertIs(caught.exception, storage_error)
        writer.interrupted(storage_error)
        row = self.terminal.snapshot('return-observed')['history'][0]
        self.assertEqual(row['evaluationState'], 'ERROR')
        self.assertEqual(row['results'], [])
        self.assertEqual(row['partialResults'][0]['status'], 'FAIL')
        self.assertNotIn('kind', row['partialResults'][0])
        self.assertNotIn('evaluation-complete', [r['id'] for r in row['partialResults']])

    def test_direct_incomplete_finish_uses_partial_projection(self):
        writer = self.writer('finish-incomplete')
        answer = writer.finish(self.entry(), raw_results=[], runner_results=[],
            post_measurement={'observedContentRoot': 'same-root'}, required=[], empty_declared=False,
            declarations={}, core=self.core)
        self.assertEqual(answer['evaluationState'], 'ERROR')
        self.assertEqual(answer['results'], [])
        self.assertIsNone(answer['outcome'])
        self.assertEqual(answer['partialResults'], [])
        self.assertEqual(answer['context']['source'], 'revalidation-incomplete')
        self.assertEqual(answer['context']['observedContext'], self.entry()['context'])
        self.assertEqual(answer['engineCapture']['kind'], 'whole-run-return-and-post-recapture-observation')
        stored = self.terminal.snapshot('finish-incomplete')['history'][0]
        self.assertEqual(stored['results'], [])
        self.assertEqual(stored['partialResults'], answer['partialResults'])
        self.assertEqual(stored['context'], answer['context'])

    def test_prior_raw_rows_are_copied_exactly_without_rewriting(self):
        from worldline.evaluation_terminal import RAW_CAPTURE
        handle = self.pending.begin('old-raw', 'content', 'req')
        bound = self.bound(handle)
        self.terminal.open_stream(bound, b'owned', value_bytes({'source': 'prior'}))
        self.terminal.observe_start(bound, 'old-invocation', {'checkId': 'old'})
        with self.terminal._transaction(self.terminal.journal, 'journal'):
            self.terminal.journal.execute(RAW_CAPTURE)
        prior = {'stdout': 'full prior acquisition'}
        self.terminal.observe_raw(bound, 'old-invocation', 'legacy-process-return', prior)
        before = [tuple(row) for row in self.terminal.journal.execute('SELECT * FROM main.invocation_observations')]
        self.terminal.enable_raw_capture()
        self.terminal.enable_raw_capture()
        self.assertEqual([tuple(row) for row in self.terminal.journal.execute('SELECT * FROM main.invocation_observations')], before)
        self.assertEqual(self.terminal.captured_observation_events(bound),
                         (('old-invocation', 'legacy-process-return', None, prior),))

    def test_unmatched_post_recapture_never_emits_completion(self):
        writer = self.writer('recapture-mismatch')
        answer = writer.finish(self.entry(), raw_results=[], runner_results=[],
            post_measurement={'observedContentRoot': 'different-observed-root'}, required=[], empty_declared=True,
            declarations={}, core=self.core)
        self.assertEqual(answer['evaluationState'], 'ERROR')
        self.assertEqual(answer['results'], [])
        self.assertEqual(answer['partialResults'], [])
        self.assertEqual(answer['context']['source'], 'revalidation-incomplete')
        self.assertEqual(answer['engineCapture']['postMeasurement'],
                         {'observedContentRoot': 'different-observed-root'})
        stored = self.terminal.snapshot('recapture-mismatch')['history'][0]
        self.assertEqual(stored['results'], [])
        self.assertEqual(stored['partialResults'], [])
        self.assertEqual(stored['context'], answer['context'])

    def test_returned_run_with_unadmitted_required_row_remains_error(self):
        writer = self.writer('returned-unadmitted')
        declarations = {'required': CheckDeclaration('engine', None, False, origin='engine')}
        rows = [{'id': 'required', 'origin': 'external', 'format': 'engine', 'status': 'UNASSESSED'}]
        writer.invocation_started(world_instance='scratch', check='required', invocation='unadmitted-invocation',
                                  candidate_snapshot=None, verifier_entries=())
        writer.invocation_result(world_instance='scratch', check='required', result=rows[0])
        answer = writer.finish(self.entry(), raw_results=rows, runner_results=rows,
            post_measurement={'observedContentRoot': 'same-root'}, required=['required'], empty_declared=False,
            declarations=declarations, core=self.core)
        self.assertEqual(answer['evaluationState'], 'ERROR')
        self.assertEqual(answer['results'], [])
        self.assertIsNone(answer['outcome'])
        self.assertFalse(answer['promotionRosterAdmitted'])
        self.assertEqual([row['id'] for row in answer['partialResults']], ['required'])
        self.assertEqual(answer['partialResults'][0]['rawRunnerResult'], rows[0])
        self.assertEqual(answer['context']['source'], 'revalidation-incomplete')
        stored = self.terminal.snapshot('returned-unadmitted')['history'][0]
        self.assertEqual(stored['results'], [])
        self.assertEqual(stored['partialResults'], answer['partialResults'])
        self.assertEqual(stored['context'], answer['context'])

    def test_required_fail_with_unadmitted_sibling_keeps_final_d15_in_both_projections(self):
        writer = self.writer('failed-full-projection')
        declarations = {'required': CheckDeclaration('engine', None, False, origin='engine'),
                        'other': CheckDeclaration('engine', None, False, origin='engine')}
        rows = [{'id': 'required', 'origin': 'engine', 'format': 'engine', 'status': 'FAIL'},
                {'id': 'other', 'origin': 'external', 'format': 'engine', 'status': 'UNASSESSED'}]
        for row in rows:
            writer.invocation_started(world_instance='scratch', check=row['id'], invocation=row['id'],
                                      candidate_snapshot=None, verifier_entries=())
            writer.invocation_result(world_instance='scratch', check=row['id'], result=row)
        answer = writer.finish(self.entry(), raw_results=rows, runner_results=rows,
            post_measurement={'observedContentRoot': 'same-root'}, required=['required', 'other'],
            empty_declared=False, declarations=declarations, core=self.core)
        self.assertEqual(answer['evaluationState'], 'COMPLETED')
        self.assertEqual(answer['outcome'], 'FAIL')
        self.assertFalse(answer['promotionRosterAdmitted'])
        self.assertEqual([row['id'] for row in answer['results']],
                         ['required', 'other', 'evaluation-complete'])
        self.assertEqual(answer['partialResults'], [])
        stored = self.terminal.snapshot('failed-full-projection')['history'][0]
        self.assertEqual(stored['evaluationState'], 'COMPLETED')
        self.assertEqual(stored['outcome'], 'FAIL')
        self.assertEqual(stored['results'], answer['results'])
        self.assertEqual(stored['partialResults'], [])

    def test_finish_storage_failure_retains_whole_return_observation_without_d15(self):
        from unittest.mock import patch
        writer = self.writer('finish-storage-failure')
        failure = OSError('owned terminal retention unavailable')
        with patch.object(self.terminal, 'retain', side_effect=failure):
            with self.assertRaises(OSError) as caught:
                writer.finish(self.entry(), raw_results=[], runner_results=[],
                    post_measurement={'observedContentRoot': 'same-root'}, required=[], empty_declared=True,
                    declarations={}, core=self.core)
        self.assertIs(caught.exception, failure)
        writer.interrupted(failure)
        stored = self.terminal.snapshot('finish-storage-failure')['history'][0]
        self.assertEqual(stored['evaluationState'], 'ERROR')
        self.assertEqual(stored['context']['source'], 'revalidation-incomplete')
        self.assertEqual(stored['context']['engineCapture']['kind'],
                         'whole-run-return-and-post-recapture-observation')
        self.assertEqual(stored['results'], [])
        self.assertEqual(stored['partialResults'], [])

    def _assert_early_finish_observation(self, subject, failed_reader=None, missing_prefix=False):
        from contextlib import nullcontext
        from unittest.mock import patch
        writer = self.writer(subject)
        writer.declarations = {'ordinary': CheckDeclaration('engine', None, False, origin='engine')}
        row = {'id': 'ordinary', 'origin': 'engine', 'format': 'engine', 'status': 'PASS',
               'completeRawField': {'empty': '', 'absent': None, 'text': '\ud800\x00'}}
        writer.invocation_started(world_instance='scratch', check='ordinary', invocation='ordinary-return',
                                  candidate_snapshot=None, verifier_entries=())
        writer.invocation_result(world_instance='scratch', check='ordinary', result=row)
        entry = self.entry()
        entry['context']['fullObservation'] = {'ordered': ['first', 'second'], 'presentEmpty': ''}
        post = {'observedContentRoot': 'same-root', 'examinedContentRoot': 'same-root',
                'manifests': {'owned-root': {'retained': ['full', 'measurement']}}}
        rows = [] if missing_prefix else [row]
        runner_rows = [row]
        expected = bytes_value(value_bytes({'returnedEntry': entry, 'postMeasurement': post,
                                             'rawResults': rows, 'runnerResults': runner_rows}))
        refusal = OSError('owned terminal observation read unavailable')
        scope = (patch.object(self.terminal, failed_reader, side_effect=refusal)
                 if failed_reader is not None else nullcontext())
        with scope:
            with self.assertRaises(OSError if failed_reader is not None else TerminalRefused) as caught:
                writer.finish(entry, raw_results=rows, runner_results=runner_rows,
                    post_measurement=post, required=['ordinary'], empty_declared=False,
                    declarations=writer.declarations, core=self.core)
        if failed_reader is not None:
            self.assertIs(caught.exception, refusal)
        else:
            self.assertEqual(str(caught.exception), 'ENGINE_RESULT_PREFIX_MISSING')
        # Mutate caller-owned nested containers after the refusal. The actual
        # received arguments must already have their own exact retained value.
        entry['context']['fullObservation']['ordered'].append('caller-later-change')
        post['manifests']['owned-root']['retained'].append('caller-later-change')
        row['completeRawField']['text'] = 'caller-later-change'
        runner_rows.append({'id': 'caller-later-extra'})
        writer.interrupted(caught.exception)
        stored = self.terminal.snapshot(subject)['history'][0]
        self.assertEqual(stored['evaluationState'], 'ERROR')
        self.assertEqual(stored['context']['source'], 'revalidation-incomplete')
        self.assertEqual(stored['results'], [])
        self.assertEqual([item['id'] for item in stored['partialResults']], ['ordinary'])
        self.assertNotIn('evaluation-complete', [item['id'] for item in stored['partialResults']])
        observation = stored['context']['engineCapture']
        self.assertEqual(observation['kind'], 'whole-run-return-and-post-recapture-observation')
        for name, value in expected.items():
            self.assertEqual(value_bytes(observation[name]), value_bytes(value))
        self.assertEqual(value_bytes(observation['returnedContext']),
                         value_bytes(expected['returnedEntry']['context']))
        # finish did not yet join a successful journal view to this observation;
        # interrupted keeps its separately obtained stream context outside it.
        self.assertNotIn('captureContext', observation)

    def test_finish_stream_read_refusal_preserves_owned_actual_arguments(self):
        self._assert_early_finish_observation('early-stream-read', failed_reader='captured_stream')

    def test_finish_event_read_refusal_preserves_owned_actual_arguments(self):
        self._assert_early_finish_observation('early-event-read', failed_reader='captured_observation_events')

    def test_finish_prefix_refusal_preserves_owned_actual_arguments(self):
        self._assert_early_finish_observation('early-prefix', missing_prefix=True)

    def test_observed_whole_return_is_not_reported_as_nonreturn_after_storage_failure(self):
        from unittest.mock import patch
        writer = self.writer('whole-return-not-finalized')
        failure = OSError('owned terminal retention unavailable')
        with patch.object(self.terminal, 'retain', side_effect=failure):
            with self.assertRaises(OSError):
                writer.finish(self.entry(), raw_results=[], runner_results=[],
                    post_measurement={'observedContentRoot': 'same-root'}, required=[],
                    empty_declared=True, declarations={}, core=self.core)
        writer.interrupted(failure)
        stored = self.terminal.snapshot('whole-return-not-finalized')['history'][0]
        self.assertEqual(stored['evaluationState'], 'ERROR')
        self.assertEqual(stored['results'], [])
        self.assertEqual(stored['partialResults'], [])
        self.assertEqual(stored['context']['kind'], 'engine-run-return-not-finalized')
        self.assertIs(stored['context']['engineRunReturnObserved'], True)
        self.assertEqual(stored['context']['engineCapture']['kind'],
                         'whole-run-return-and-post-recapture-observation')

    def test_missing_whole_return_observation_stays_unknown_on_interruption(self):
        writer = self.writer('whole-return-not-observed')
        writer.interrupted(RuntimeError('owned engine stopped before finish observation'))
        stored = self.terminal.snapshot('whole-return-not-observed')['history'][0]
        self.assertEqual(stored['evaluationState'], 'ERROR')
        self.assertEqual(stored['results'], [])
        self.assertEqual(stored['context']['kind'], 'engine-run-return-not-observed')
        self.assertIsNone(stored['context']['engineRunReturnObserved'])
        self.assertIsNone(stored['context']['engineCapture'])


    def test_native_fact_dependencies_refuse_before_terminal_retention(self):
        from worldline.completion_kernel import Facts, KernelRefused
        # Actual owned C requests through CompletionKernel, no process launch
        # and no authorization inference. Each case isolates an original raw
        # dependent relation; a typed negative is covered separately below.
        malformed = [
            {'exit_integer': 1},
            {'bundle_stable': 1, 'bundle_is_mapping': 1},
            {'bundle_stable': 1, 'bundle_present': 1},
            {'bundle_changed': 1, 'bundle_is_mapping': 1},
            {'bundle_changed': 1, 'bundle_present': 1},
        ]
        for index, updates in enumerate(malformed):
            with self.subTest(observations=updates):
                handle = self.pending.begin('native-invalid-' + str(index), 'content', 'req')
                capture, rows = self.observation(handle)
                facts = Facts()
                for name, value in updates.items():
                    setattr(facts, name, value)
                raw = tuple(getattr(facts, name) for name, _type in Facts._fields_)
                row = replace(rows[0], observations=raw)
                with self.assertRaisesRegex(KernelRefused, 'COMPLETION_TRANSPORT_REFUSED'):
                    self.terminal.retain(capture, (row,))
                self.assertIsNone(self.terminal._intent(capture.bound.run))
                self.assertEqual(self.terminal.discover(), ())

    def test_native_fact_dependencies_preserve_original_valid_negative_encodings(self):
        from worldline.completion_kernel import Facts
        valid = [
            {},
            {'exit_present': 1, 'exit_integer': 1},
            {'bundle_present': 1, 'bundle_is_mapping': 1, 'bundle_stable': 1},
            {'bundle_present': 1, 'bundle_is_mapping': 1, 'bundle_changed': 1},
            # The original predicate permits this ordinary absent-bundle
            # observation when neither dependent stability bit claims a result.
            {'bundle_is_mapping': 1},
        ]
        for index, updates in enumerate(valid):
            with self.subTest(observations=updates):
                handle = self.pending.begin('native-valid-' + str(index), 'content', 'req')
                capture, rows = self.observation(handle)
                facts = Facts()
                for name, value in updates.items():
                    setattr(facts, name, value)
                raw = tuple(getattr(facts, name) for name, _type in Facts._fields_)
                retained = self.terminal.retain(capture, (replace(rows[0], observations=raw),))
                self.assertEqual(retained.run, handle.run)
                self.assertIsNotNone(self.terminal._intent(capture.bound.run))
