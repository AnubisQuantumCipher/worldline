"""Prepared ordinary controls; no execution or universal-proof claim.
Existing D2 controls are inherited unchanged through the new real raw ABI.
"""
import ctypes
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
import os
import unittest
from test_evaluation_roster_d2 import RequiredFailureControls
from worldline.core import Core, CollapseInput, ROSTER_MAX
from worldline.evaluation_wire import Raw, OwnedRecord, record, U8
from worldline.raw_completion_kernel import RawCompletionKernel
from worldline.finalize import ENGINE_DECLARATIONS
from worldline.evaluation_authority import read
from worldline.errors import WorldlineError
from worldline.evaluation_history import EvaluationRecord, EvaluationCursor, EvaluationQuery, select_history

class RawRequiredFailureControls(RequiredFailureControls):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.raw_kernel = RawCompletionKernel(Path(os.environ['WORLDLINE_CORE_LIB']))

    def prepared(self, rows):
        from worldline.evaluation_context import RowMetadata
        rows = tuple(rows)
        wires = tuple(OwnedRecord(bytes(Raw((U8 * 14)(*row.observations, 0), 0,
            (U8 * 14)(), (U8 * 5)(*(int(x) for x in row.evidence)))), 0) for row in rows)
        prepared = self.raw_kernel.prepare(self.journal,
            current=(self.bound.epoch, self.bound.run), capture=self.capture,
            results=rows, wire_records=wires,
            required=((b'required-check', self.declaration),), policy='Required_Checks',
            measured_roots=(b'same-root', b'same-root'),
            completion=(b'evaluation-complete', self.declaration), measured_binding=self.bound)
        # Explicit TEST_ONLY paired semantic inputs. The production decoder
        # derives its independent side from payload/invocation, never this list.
        prepared.test_only_metadata = tuple(RowMetadata(row.check, row.source,
            row.payload, row.execution, row.verifier) for row in rows)
        return prepared

    def classify(self, rows):
        before = tuple(rows)
        answer = self.raw_kernel.classify(self.prepared(before))
        self.assertEqual(tuple(rows), before)
        return answer

    def joined(self, request, prepared, agent, **changes):
        from worldline.evaluation_context import attach, CONTEXT_FIELDS, ROW_FIELDS
        from worldline.evaluation_terminal import value_bytes
        # A total typed-owned synthetic context. Truth/authentication is not an
        # ordinary-test claim; independent source deltas below exercise actual
        # C/Ada field, cursor, row and legacy slot correspondence.
        expected = {name: value_bytes({'field': name, 'complete': []}) for name in CONTEXT_FIELDS}
        expected['returned_context'] = self.capture.context
        expected['source_id'] = self.capture.source
        expected['examined_root'] = b'same-root'
        observed = dict(expected)
        pairs = [({name: None for name in ROW_FIELDS}, {name: None for name in ROW_FIELDS})
                 for _ in range(prepared.request.captured_count)]
        args = dict(expected_binding=self.bound,
            expected_current=(self.bound.epoch, self.bound.run),
            prepared_current=(self.bound.epoch, self.bound.run),
            expected=expected, observed=observed, row_pairs=pairs,
            row_metadata=prepared.test_only_metadata,
            required=((b'required-check', self.declaration),), policy=2,
            projection=self.core._raw_collapse_request(request), agent=agent)
        args.update(changes)
        return attach(self.core, prepared, **args)

    def bound_request(self):
        request = replace(RawDependencyControls.checkpoint(), mode='CANDIDATE_EVALUATION',
            evaluated_requirement=RawDependencyControls.checkpoint().current_requirement,
            executed_verifiers=RawDependencyControls.checkpoint().declared_verifiers,
            expected_checkpoint=None, witnessed_checkpoint=None)
        agent = record({'id': 'agent', 'origin': 'agent', 'format': 'exit', 'status': 'PASS',
            'exitCode': 0, 'supervision': {'kind': 'SUPERVISED'},
            'resources': {'ceilingFired': False}}, ENGINE_DECLARATIONS['agent'])
        prepared = self.prepared((self.measured(b'required-check', 'PASS'),
                                  self.measured(b'evaluation-complete', 'PASS')))
        return request, agent, prepared

    def test_complete_owned_join_and_padded_epoch(self):
        request, agent, prepared = self.bound_request()
        self.joined(request, prepared, agent,
            expected_binding=replace(self.bound, epoch=self.bound.epoch + b'\0\0'))
        before = bytes(prepared.request)
        self.assertEqual(self.core.collapse_decide_with_evaluation(request,
            primary=prepared, staged=None, agent=agent), 'AUTHORIZED')
        self.assertEqual(bytes(prepared.request), before)

    def test_same_legacy_hashes_do_not_join_another_full_subject(self):
        request, agent, prepared = self.bound_request()
        self.joined(request, prepared, agent, expected_binding=replace(self.bound, subject=b'other-full-subject'))
        self.assertEqual(self.core.collapse_decide_with_evaluation(request,
            primary=prepared, staged=None, agent=agent), 'INVALID_REQUEST')

    def test_context_requires_independently_retained_current_cursor(self):
        request, agent, prepared = self.bound_request()
        self.joined(request, prepared, agent, expected_current=(self.bound.epoch, b'other-current-run'))
        self.assertEqual(self.core.collapse_decide_with_evaluation(request,
            primary=prepared, staged=None, agent=agent), 'INVALID_REQUEST')

    def test_context_keeps_prepared_cursor_distinct_from_current(self):
        request, agent, prepared = self.bound_request()
        self.joined(request, prepared, agent, prepared_current=(self.bound.epoch, b'other-prepared-run'))
        self.assertEqual(self.core.collapse_decide_with_evaluation(request,
            primary=prepared, staged=None, agent=agent), 'INVALID_REQUEST')

    def test_context_policy_full_bytes_cannot_be_replaced_by_digest(self):
        from worldline.evaluation_context import CONTEXT_FIELDS
        request, agent, prepared = self.bound_request()
        self.joined(request, prepared, agent)
        prepared.context.observed[CONTEXT_FIELDS.index('full_policy')] = prepared.context.expected[CONTEXT_FIELDS.index('root_manifests')]
        self.assertEqual(self.core.collapse_decide_with_evaluation(request,
            primary=prepared, staged=None, agent=agent), 'INVALID_REQUEST')

    def test_context_recomputes_used_legacy_projection(self):
        request, agent, prepared = self.bound_request()
        self.joined(request, prepared, agent, projection=self.core._raw_collapse_request(
            replace(request, executed_verifiers=request.expected_root_set)))
        self.assertEqual(self.core.collapse_decide_with_evaluation(request,
            primary=prepared, staged=None, agent=agent), 'INVALID_REQUEST')

    def test_context_cannot_change_required_declaration(self):
        request, agent, prepared = self.bound_request()
        self.joined(request, prepared, agent, required=((b'required-check', b'other-complete-declaration'),))
        self.assertEqual(self.core.collapse_decide_with_evaluation(request,
            primary=prepared, staged=None, agent=agent), 'INVALID_REQUEST')

    def test_context_preserves_all_ordered_actual_rows(self):
        request, agent, prepared = self.bound_request()
        self.joined(request, prepared, agent)
        prepared.context_owners[1][0].item.check_id = prepared.context_owners[1][1].item.check_id
        self.assertEqual(self.core.collapse_decide_with_evaluation(request,
            primary=prepared, staged=None, agent=agent), 'INVALID_REQUEST')

    def test_context_compares_complete_effective_verifier_member_bytes(self):
        from worldline.evaluation_context import ROW_FIELDS
        request, agent, prepared = self.bound_request()
        self.joined(request, prepared, agent)
        prepared.context_owners[1][0].observed[ROW_FIELDS.index('verifier_members')] = prepared.context.expected[0]
        self.assertEqual(self.core.collapse_decide_with_evaluation(request,
            primary=prepared, staged=None, agent=agent), 'INVALID_REQUEST')

    def test_context_malformed_owned_span_is_not_a_promotion_result(self):
        request, agent, prepared = self.bound_request()
        self.joined(request, prepared, agent)
        prepared.context.expected[0].value.first = 0
        self.assertEqual(self.core.collapse_decide_with_evaluation(request,
            primary=prepared, staged=None, agent=agent), 'INVALID_REQUEST')

    def test_context_present_empty_is_distinct_from_absence(self):
        from worldline.evaluation_context import ROW_FIELDS
        from worldline.completion_kernel import Optional_Span, Span
        request, agent, prepared = self.bound_request()
        self.joined(request, prepared, agent)
        prepared.context_owners[1][0].observed[ROW_FIELDS.index('invocation_start')] = Optional_Span(1, Span(1, 0))
        self.assertEqual(self.core.collapse_decide_with_evaluation(request,
            primary=prepared, staged=None, agent=agent), 'INVALID_REQUEST')

    def producer_case(self):
        # Explicit TEST_ONLY current-policy/world/store snapshot. The actual
        # legacy projection routines and new native join run against the real
        # library; this does not establish a protected production producer.
        from dataclasses import asdict
        from worldline.evaluation_context import bind_selected
        from worldline.evaluation_authority import SelectedEvaluation
        from worldline.evaluation_pending import identity
        from worldline.evaluation_terminal import value_bytes
        from worldline.completion_kernel import CaptureValue
        from worldline.pending_kernel_v2 import Intent
        from worldline.executed import bundle_identity, NO_BUNDLE_IDENTITY
        from worldline.validation import requirement_hash, content_root_set, build_context
        from worldline.transaction import CollapseTransaction
        from worldline.prime import PrimeManager
        from types import MethodType
        policy = {'schemaVersion': 1, 'policy': {'canonical': {'checks': [], 'protected': ['owned-path']},
            'requiredChecks': [], 'sourceSha256': 'owned-policy', 'warnings': []},
            'verifiers': [], 'execution': {}}
        policy['requirementHash'] = requirement_hash(policy, self.core)
        root = content_root_set({}, self.core)
        prime = SimpleNamespace(core=self.core)
        prime.root_set_hash = MethodType(PrimeManager.root_set_hash, prime)
        subject = SimpleNamespace(instance_id='world', content_id='content',
            root_set_hash=prime.root_set_hash([]), mission_hash=None)
        manager = SimpleNamespace(core=self.core, prime=prime,
            store=SimpleNamespace(evaluation_terminal=SimpleNamespace(pending=SimpleNamespace(store=b'store'))))
        manager._identity = CollapseTransaction._identity
        manager._subject_digest = MethodType(CollapseTransaction._subject_digest, manager)
        manager._return_binding = MethodType(CollapseTransaction._return_binding, manager)
        self.bound = replace(self.bound, requirement=identity(policy['requirementHash']))
        self.journal = (Intent(self.bound.store_id, self.bound.subject, self.bound.content,
            self.bound.run, self.bound.epoch, None, True, self.bound.requirement),)
        declaration = value_bytes(asdict(ENGINE_DECLARATIONS['protected-paths']))
        self.declaration = declaration
        payloads = [{'id': 'protected-paths', 'origin': 'engine', 'format': 'engine', 'required': True, 'status': 'PASS'},
                    {'id': 'evaluation-complete', 'origin': 'engine', 'format': 'engine', 'required': True, 'status': 'PASS'}]
        context = build_context(requirement=policy, candidate={'instanceId': 'world'},
            prime_at_fork={}, roots=[], results=payloads, candidate_verifiers=[], adapter={},
            evaluated_at='ordinary-fixture', core=self.core, source='owned-test-input', examined_content_root=root)
        header = {'subject': context['candidate'], 'requirement': policy,
            'measurement': {'worldInstance': 'world', 'contentId': 'content',
                'storedRootSetHash': subject.root_set_hash, 'observedContentRoot': root, 'manifests': {}},
            'source': 'owned-test-input', 'run': 'run', 'evaluationEpoch': 1, 'storeId': 'store'}
        observed = {'captureContext': header, 'returnedContext': context,
                    'postMeasurement': {'observedContentRoot': root}, 'runnerResults': []}
        self.capture = CaptureValue(self.bound, b'owned-test-input', value_bytes(context), 'Incomplete_Unknown', None)
        typed = tuple(replace(self.measured(identity(row['id']), 'PASS'),
            source=value_bytes(row.get('origin')), payload=value_bytes(row)) for row in payloads)
        prepared = self.raw_kernel.prepare(self.journal, current=(self.bound.epoch, self.bound.run),
            capture=self.capture, results=typed, wire_records=tuple(record(row, ENGINE_DECLARATIONS['protected-paths']) for row in payloads),
            required=((b'protected-paths', declaration),), policy='Required_Checks',
            measured_roots=(identity(root), identity(root)), completion=(b'evaluation-complete', declaration), measured_binding=self.bound)
        chosen = SelectedEvaluation(context, 'ordinary-fixture', payloads, {'epoch': 1, 'run': 'run'},
            prepared, self.capture, typed, ((header, ()), ()), observed)
        request, agent, _unused = self.bound_request()
        declared = bundle_identity([('', 'protected-paths', NO_BUNDLE_IDENTITY)])
        subject_digest = manager._subject_digest('world', '')
        request = replace(request, expected_subject=manager._identity(subject_digest), evidence_subject=manager._identity(subject_digest),
            expected_root_set=manager._identity(subject.root_set_hash), candidate_root_set=manager._identity(subject.root_set_hash),
            staged_content_root=manager._identity(root), tested_root=manager._identity(root),
            current_requirement=manager._identity(policy['requirementHash']), evaluated_requirement=manager._identity(policy['requirementHash']),
            declared_verifiers=manager._identity(declared), executed_verifiers=manager._identity(declared))
        return manager, subject, policy, chosen, request, agent

    def test_default_producer_recomputes_complete_matching_context(self):
        from worldline.evaluation_context import bind_selected
        manager, subject, policy, chosen, request, agent = self.producer_case()
        bind_selected(manager, chosen, values=request, subject=subject, candidate=subject,
            authoritative_requirement=policy, authoritative_roots=[], agent=agent,
            agent_record={'ordinary-agent': True}, role='primary', prepared_cursor=chosen.cursor)
        self.assertEqual(self.core.collapse_decide_with_evaluation(request,
            primary=chosen.raw, staged=None, agent=agent), 'AUTHORIZED')

    def test_default_producer_keeps_complete_current_policy_separate(self):
        from worldline.evaluation_context import bind_selected
        from copy import deepcopy
        manager, subject, policy, chosen, request, agent = self.producer_case()
        current = deepcopy(policy)
        current['execution']['new-observed-setting'] = 'different-full-byte-context'
        # Carrying the old hash is insufficient: the typed full-policy equality
        # sees the actual source records before legacy Collapse can authorize.
        bind_selected(manager, chosen, values=request, subject=subject, candidate=subject,
            authoritative_requirement=current, authoritative_roots=[], agent=agent,
            agent_record={'ordinary-agent': True}, role='primary', prepared_cursor=chosen.cursor)
        self.assertEqual(self.core.collapse_decide_with_evaluation(request,
            primary=chosen.raw, staged=None, agent=agent), 'INVALID_REQUEST')

    def retained_error_case(self, *, has_final, metadata_source=None):
        # Actual owned temporary pending/terminal stores and the real default
        # reader. A coherent ERROR summary does not decide raw D15/D2 facts.
        import tempfile
        from copy import deepcopy
        from worldline.evaluation_pending import PendingJournal, identity
        from worldline.evaluation_terminal import TerminalJournal, value_bytes
        manager, subject, policy, chosen, _request, _agent = self.producer_case()
        with tempfile.TemporaryDirectory(prefix='worldline-raw-default-ordinary-') as directory:
            root = Path(directory)
            pending = PendingJournal(root/'pending-j.db', root/'pending-t.db',
                store_id='store', library=Path(self.core.library_path), create=True)
            terminal = TerminalJournal(pending, root/'terminal-j.db', root/'terminal-t.db',
                library=Path(self.core.library_path), create=True)
            try:
                handle = pending.begin('world', 'content', policy['requirementHash'])
                bound = replace(chosen.capture.bound, run=identity(handle.run),
                    epoch=handle.epoch.to_bytes((handle.epoch.bit_length() + 7) // 8, 'little'))
                captured = deepcopy(chosen.observed)
                captured['captureContext']['run'] = handle.run
                captured['captureContext']['evaluationEpoch'] = handle.epoch
                rows = [dict(chosen.results[0], status='FAIL')]
                if has_final:
                    rows.append(dict(chosen.results[-1], captureObservation=captured))
                typed = tuple(replace(self.measured(identity(row['id']), row['status']),
                    bound=bound, source=value_bytes(row.get('origin')), payload=value_bytes(row)) for row in rows)
                if metadata_source is not None:
                    typed = tuple(replace(row, source=metadata_source) for row in typed)
                capture = replace(chosen.capture, bound=bound,
                    state='Incomplete_Unknown', outcome=None)
                terminal.complete(capture, typed)
                before = terminal.snapshot('world')
                self.assertEqual(before['history'][-1]['evaluationState'], 'ERROR')
                with self.assertRaises(WorldlineError) as caught:
                    read(SimpleNamespace(evaluation_terminal=terminal, core=self.core),
                         subject, policy['requirementHash'], core=self.core)
                self.assertEqual(terminal.snapshot('world'), before)
                return caught.exception.code
            finally:
                terminal.close(); pending.close()

    def test_default_reader_raw_failure_survives_stored_error_summary(self):
        self.assertEqual(self.retained_error_case(has_final=True), 'EVIDENCE_FAIL_TERMINAL')

    def test_default_reader_partial_error_does_not_invent_final_completion(self):
        self.assertEqual(self.retained_error_case(has_final=False), 'EVALUATION_INCOMPLETE')

    def staged_journal(self):
        # Real owned SQLite journals and real native history/roster calls. The
        # synthetic engine rows are explicit ordinary input, not a protected
        # production producer or confinement claim.
        from contextlib import contextmanager
        from copy import deepcopy
        from tempfile import TemporaryDirectory
        from types import MethodType
        from worldline.evaluation_pending import PendingJournal, identity
        from worldline.evaluation_terminal import TerminalJournal, value_bytes
        from worldline.transaction import CollapseTransaction

        @contextmanager
        def opened():
            manager, subject, policy, chosen, _request, _agent = self.producer_case()
            manager.staged_fixture_values = (_request, _agent)
            subject.evidence = {'checks': [{'id': 'agent', 'origin': 'agent', 'format': 'exit',
                'status': 'PASS', 'exitCode': 0, 'supervision': {'kind': 'SUPERVISED'},
                'resources': {'ceilingFired': False}}]}
            with TemporaryDirectory(prefix='worldline-staged-cursor-ordinary-') as directory:
                root = Path(directory)
                pending = PendingJournal(root/'pending-j.db', root/'pending-t.db',
                    store_id='store', library=Path(self.core.library_path), create=True)
                terminal = TerminalJournal(pending, root/'terminal-j.db', root/'terminal-t.db',
                    library=Path(self.core.library_path), create=True)
                terminal.enable_raw_capture()
                events = []
                def lookup(instance):
                    self.assertEqual(instance, subject.instance_id)
                    return subject
                manager.store = SimpleNamespace(evaluation_terminal=terminal, core=self.core,
                    world=lookup, append_causal_event=lambda event, **kw: events.append((event, kw)))
                for name in ('_freshness_after_staged', '_selected_freshness', '_execution_identity'):
                    setattr(manager, name, MethodType(getattr(CollapseTransaction, name), manager))
                def append(status='PASS', *, final=True):
                    handle = pending.begin(subject.instance_id, subject.content_id, policy['requirementHash'])
                    bound = replace(chosen.capture.bound, run=identity(handle.run),
                        epoch=handle.epoch.to_bytes((handle.epoch.bit_length() + 7) // 8, 'little'))
                    observed = deepcopy(chosen.observed)
                    observed['captureContext']['run'] = handle.run
                    observed['captureContext']['evaluationEpoch'] = handle.epoch
                    terminal.open_stream(bound, chosen.capture.source, value_bytes(observed['captureContext']))
                    rows = [dict(chosen.results[0], status=status)]
                    if final: rows.append(dict(chosen.results[-1], captureObservation=observed))
                    typed = tuple(replace(self.measured(identity(row['id']), row['status']),
                        bound=bound, source=value_bytes(row.get('origin')), payload=value_bytes(row)) for row in rows)
                    capture = replace(chosen.capture, bound=bound,
                        state='Completed' if final else 'Incomplete_Unknown', outcome=status if final else None)
                    terminal.complete(capture, typed)
                    return {'epoch': handle.epoch, 'run': handle.run}
                try:
                    initial_cursor = append()
                    selected = read(manager.store, subject, policy['requirementHash'], core=self.core)
                    previous = manager._selected_freshness(subject, policy, selected, kind='collapse')
                    self.assertEqual(previous['evaluationCursor'], initial_cursor)
                    yield manager, subject, policy, previous, append, terminal
                finally:
                    terminal.close(); pending.close()
        return opened()

    def test_post_stage_uses_one_actual_current_evaluation_not_returned_summary(self):
        from copy import deepcopy
        with self.staged_journal() as (manager, subject, policy, previous, append, terminal):
            old = deepcopy(previous)
            cursor = append()
            before = terminal.snapshot(subject.instance_id)
            refreshed = manager._freshness_after_staged(subject, kind='collapse', return_of=None,
                previous=previous, staged={'evaluationCursor': cursor, 'outcome': 'FAIL',
                'results': [], 'requirementHash': 'carried-wrong-value', 'examinedContentRoot': 'carried-wrong-root'})
            selected = read(manager.store, subject, policy['requirementHash'], prepared=cursor, core=self.core)
            self.assertEqual(refreshed, manager._selected_freshness(subject, policy, selected, kind='collapse'))
            self.assertEqual(refreshed['evaluationCursor'], cursor)
            from worldline.evaluation_context import bind_selected
            request, agent = manager.staged_fixture_values
            bind_selected(manager, selected, values=request, subject=subject, candidate=subject,
                authoritative_requirement=policy, authoritative_roots=[], agent=agent,
                agent_record=subject.evidence['checks'][0], role='primary',
                prepared_cursor=refreshed['evaluationCursor'])
            self.assertEqual(self.core.collapse_decide_with_evaluation(request,
                primary=selected.raw, staged=None, agent=agent), 'AUTHORIZED')
            self.assertNotEqual(refreshed['evaluationCursor'], previous['evaluationCursor'])
            self.assertEqual(previous, old)
            self.assertEqual(terminal.snapshot(subject.instance_id), before)

    def test_post_stage_missing_cursor_is_not_latest_pass_fallback(self):
        with self.staged_journal() as (manager, subject, _policy, previous, append, _terminal):
            append()
            with self.assertRaises(WorldlineError) as caught:
                manager._freshness_after_staged(subject, kind='collapse', return_of=None,
                    previous=previous, staged={'outcome': 'PASS'})
            self.assertEqual(caught.exception.code, 'STAGED_EVALUATION_CURSOR_ABSENT')

    def test_post_stage_stale_cursor_does_not_accept_another_run(self):
        with self.staged_journal() as (manager, subject, _policy, previous, append, _terminal):
            cursor = append()
            append()
            with self.assertRaises(WorldlineError) as caught:
                manager._freshness_after_staged(subject, kind='collapse', return_of=None,
                    previous=previous, staged={'evaluationCursor': cursor, 'outcome': 'PASS'})
            self.assertEqual(caught.exception.code, 'EVIDENCE_SUPERSEDED')

    def test_post_stage_required_failure_is_not_replaced_by_old_pass(self):
        with self.staged_journal() as (manager, subject, _policy, previous, append, _terminal):
            cursor = append('FAIL')
            with self.assertRaises(WorldlineError) as caught:
                manager._freshness_after_staged(subject, kind='collapse', return_of=None,
                    previous=previous, staged={'evaluationCursor': cursor, 'outcome': 'PASS'})
            self.assertEqual(caught.exception.code, 'EVIDENCE_FAIL_TERMINAL')

    def test_post_stage_error_head_is_not_replaced_by_old_pass(self):
        with self.staged_journal() as (manager, subject, _policy, previous, append, _terminal):
            cursor = append(final=False)
            with self.assertRaises(WorldlineError) as caught:
                manager._freshness_after_staged(subject, kind='collapse', return_of=None,
                    previous=previous, staged={'evaluationCursor': cursor, 'outcome': 'PASS'})
            self.assertEqual(caught.exception.code, 'EVALUATION_INCOMPLETE')

    def test_post_stage_later_pass_does_not_clear_required_failure_latch(self):
        with self.staged_journal() as (manager, subject, _policy, previous, append, _terminal):
            append('FAIL')
            cursor = append()
            with self.assertRaises(WorldlineError) as caught:
                manager._freshness_after_staged(subject, kind='collapse', return_of=None,
                    previous=previous, staged={'evaluationCursor': cursor, 'outcome': 'PASS'})
            self.assertEqual(caught.exception.code, 'EVIDENCE_FAIL_TERMINAL')

    def test_post_stage_return_vehicle_does_not_replace_original_subject(self):
        with self.staged_journal() as (manager, subject, _policy, previous, append, _terminal):
            cursor = append()
            vehicle = SimpleNamespace(instance_id='return-vehicle', content_id='vehicle-content')
            refreshed = manager._freshness_after_staged(vehicle, kind='return', return_of=subject.instance_id,
                previous=previous, staged={'evaluationCursor': cursor})
            self.assertEqual(refreshed['subject'], subject.instance_id)
            self.assertEqual(refreshed['evidenceInstance'], subject.instance_id)
            self.assertEqual(refreshed['mode'], 're-application')
            self.assertEqual(refreshed['evaluationCursor'], cursor)

    def test_prepared_post_stage_cursor_stays_a_commit_fence(self):
        with self.staged_journal() as (manager, subject, policy, previous, append, _terminal):
            cursor = append()
            refreshed = manager._freshness_after_staged(subject, kind='collapse', return_of=None,
                previous=previous, staged={'evaluationCursor': cursor})
            append()
            with self.assertRaises(WorldlineError) as caught:
                read(manager.store, subject, policy['requirementHash'],
                    prepared=refreshed['evaluationCursor'], core=self.core)
            self.assertEqual(caught.exception.code, 'EVIDENCE_SUPERSEDED')

    def test_full_semantic_array_exceeds_fixed_transport(self):
        rows = tuple(self.measured(b'unrelated', 'PASS') for _ in range(ROSTER_MAX))
        rows += (self.measured(b'required-check', 'PASS'), self.measured(b'evaluation-complete', 'PASS'))
        self.assertEqual(self.classify(rows), ('Completed', 'PASS', True))

    def test_new_requirement_head_is_not_filtered_away(self):
        old = EvaluationRecord('world', 'content', 'old', 'old-run', 1, 'COMPLETED', 'PASS')
        new = EvaluationRecord('world', 'content', 'new', 'new-run', 2, 'COMPLETED', 'PASS')
        current = EvaluationCursor(new.epoch, new.run)
        answer = select_history((old, new), None,
            EvaluationQuery('world', 'content', 'old', current, current), core=self.core)
        self.assertEqual(answer.reason, 'REQUIREMENT_CHANGED')
        self.assertEqual(answer.head.index, 1)

    def test_prior_raw_failure_survives_later_pass(self):
        failed = self.classify((self.measured(b'required-check', 'FAIL'),
                               self.measured(b'evaluation-complete', 'PASS')))
        passed = self.classify((self.measured(b'required-check', 'PASS'),
                               self.measured(b'evaluation-complete', 'PASS')))
        rows = (EvaluationRecord('world', 'content', 'req', 'first', 1, failed[0].upper(), failed[1]),
                EvaluationRecord('world', 'content', 'req', 'second', 2, passed[0].upper(), passed[1]))
        cursor = EvaluationCursor(rows[-1].epoch, rows[-1].run)
        answer = select_history(rows, None, EvaluationQuery('world', 'content', 'req', cursor, cursor), core=self.core)
        self.assertEqual(answer.reason, 'EVIDENCE_FAIL_TERMINAL')

    def test_collapse_recomputes_carried_roster(self):
        def h(value): return bytes([value]) * 32
        request = CollapseInput(candidate_state='VALID', phase='COMMIT', mode='CANDIDATE_EVALUATION',
            conflicts='NONE_FOUND', foreign_writes='NONE_FOUND', roster_complete=False, staged_roster_complete=False,
            expected_parent=h(1), candidate_parent=h(1), expected_subject=h(2), evidence_subject=h(2),
            expected_base=h(3), candidate_base=h(3), expected_delta=h(4), candidate_delta=h(4),
            expected_root_set=h(5), candidate_root_set=h(5), expected_staged_root=h(6), actual_staged_root=h(6),
            staged_content_root=h(7), tested_root=h(7), current_requirement=h(8), evaluated_requirement=h(8),
            declared_verifiers=h(9), executed_verifiers=h(9), staged_evaluated_requirement=None,
            staged_executed_verifiers=None, staged_examined_root=None, expected_checkpoint=None, witnessed_checkpoint=None,
            registered_watch_set=h(10), watched_set=h(10), generation_before=41, generation_after=41)
        agent = record({'id':'agent', 'origin':'agent', 'format':'exit', 'status':'PASS', 'exitCode':0,
            'supervision':{'kind':'SUPERVISED'}, 'resources':{'ceilingFired':False}}, ENGINE_DECLARATIONS['agent'])
        passed = self.prepared((self.measured(b'required-check','PASS'), self.measured(b'evaluation-complete','PASS')))
        failed = self.prepared((self.measured(b'required-check','FAIL'), self.measured(b'evaluation-complete','PASS')))
        # The prototype's formerly unbound positive request is now explicitly
        # refused: matching small legacy hashes do not establish a raw join.
        self.assertEqual(self.core.collapse_decide_with_evaluation(request, primary=passed, staged=None, agent=agent), 'INVALID_REQUEST')
        self.joined(request, passed, agent)
        self.assertEqual(self.core.collapse_decide_with_evaluation(request, primary=passed, staged=None, agent=agent), 'AUTHORIZED')
        self.assertEqual(self.core.collapse_decide_with_evaluation(replace(request, roster_complete=True),
            primary=failed, staged=None, agent=agent), 'EXECUTION_EVIDENCE_INCOMPLETE')

    def test_required_raw_failure_does_not_require_coherent_carried_pair(self):
        failed = replace(self.measured(b'required-check', 'FAIL'),
                         state='Incomplete_Unknown', outcome='FAIL')
        completed = self.measured(b'evaluation-complete', 'PASS')
        self.assertEqual(self.classify((failed, completed)), ('Completed', 'FAIL', False))

    def test_raw_completion_ignores_incoherent_terminal_projection(self):
        from worldline.completion_kernel import EXECUTION, OUTCOME
        prepared = self.prepared((self.measured(b'required-check', 'FAIL'),
                                  self.measured(b'evaluation-complete', 'PASS')))
        prepared.request.captured.state = EXECUTION.index('Incomplete_Unknown')
        prepared.request.captured.outcome = OUTCOME.index('PASS')
        before = bytes(prepared.request)
        self.assertEqual(self.raw_kernel.classify(prepared), ('Completed', 'FAIL', False))
        self.assertEqual(bytes(prepared.request), before)

    def test_raw_pass_still_requires_carried_row_correspondence(self):
        stale = replace(self.measured(b'required-check', 'PASS'),
                        state='Incomplete_Unknown', outcome='PASS')
        self.assertEqual(self.classify((stale, self.measured(b'evaluation-complete', 'PASS'))),
                         ('Incomplete_Unknown', None, False))


class RawDependencyControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = Core(Path(os.environ['WORLDLINE_CORE_LIB']))

    @staticmethod
    def checkpoint():
        def h(value): return bytes([value]) * 32
        return CollapseInput(candidate_state='VALID', phase='COMMIT', mode='CHECKPOINT_RETURN',
            conflicts='NONE_FOUND', foreign_writes='NONE_FOUND', roster_complete=False, staged_roster_complete=False,
            expected_parent=h(1), candidate_parent=h(1), expected_subject=h(2), evidence_subject=h(2),
            expected_base=h(3), candidate_base=h(3), expected_delta=h(4), candidate_delta=h(4),
            expected_root_set=h(5), candidate_root_set=h(5), expected_staged_root=h(6), actual_staged_root=h(6),
            staged_content_root=h(7), tested_root=h(7), current_requirement=h(8), evaluated_requirement=None,
            declared_verifiers=h(9), executed_verifiers=None, staged_evaluated_requirement=None,
            staged_executed_verifiers=None, staged_examined_root=None, expected_checkpoint=h(2), witnessed_checkpoint=h(2),
            registered_watch_set=h(10), watched_set=h(10), generation_before=41, generation_after=41)

    def test_primary_covered_checkpoint_has_no_raw_dependency(self):
        value = self.checkpoint()
        self.assertEqual(self.core.collapse_raw_dependencies(value),
            {'valid': True, 'primary': False, 'staged': False, 'agent': False})
        # Ordinary Python values in unused evidence slots must not be decoded.
        ignored = object()
        self.assertEqual(self.core.collapse_decide_with_evaluation(value,
            primary=ignored, staged=ignored, agent=ignored), self.core.collapse_decide(value))
        self.assertEqual(self.core.collapse_decide(value), 'AUTHORIZED')

    def test_uncovered_checkpoint_keeps_staged_and_agent_obligations(self):
        value = replace(self.checkpoint(), tested_root=None)
        self.assertEqual(self.core.collapse_raw_dependencies(value),
            {'valid': True, 'primary': False, 'staged': True, 'agent': True})
        self.assertEqual(self.core.collapse_decide_with_evaluation(value,
            primary=object(), staged=None, agent=None), 'STAGED_UNTESTED')


class UnprovisionedAuthorityControls(unittest.TestCase):
    def test_legacy_pass_list_is_not_an_authority_fallback(self):
        def forbidden(*args, **kwargs): raise AssertionError('legacy PASS search was called')
        store = SimpleNamespace(evaluation_terminal=None, get_meta=forbidden)
        with self.assertRaises(WorldlineError) as caught:
            read(store, SimpleNamespace(instance_id='world', content_id='content'), 'req')
        self.assertEqual(caught.exception.code, 'EVALUATION_AUTHORITY_UNAVAILABLE')

if __name__ == '__main__': unittest.main()
