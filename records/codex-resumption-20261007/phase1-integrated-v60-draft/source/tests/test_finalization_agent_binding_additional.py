"""Additive branch/native controls, unexecuted. No protected custody claim."""
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from test_finalization_agent_binding import FinalizationAgentBindingControls as _Binding
from test_finalization_kernel import FinalizationNativeControls as _Native
from worldline.evaluation_authority import read
from worldline.evaluation_context import agent_context_pair, bind_selected
from worldline.evaluation_terminal import value_bytes
from worldline.evaluation_pending import identity
from worldline.finalization_journal import FinalizationJournal
from worldline.finalize import runner_agent_record
from worldline.canonical import canonical_bytes
from worldline.errors import WorldlineError

class AgentBindingAdditionalControls(_Binding):
    def bind_real_material(self, manager, subject, policy, previous):
        request, agent = manager.staged_fixture_values
        cursor = previous['evaluationCursor']
        selected = read(manager.store, subject, policy['requirementHash'], prepared=cursor, core=self.core)
        payload, _legacy = runner_agent_record(subject.evidence['checks'][0])
        pair = agent_context_pair(selected, subject, payload)
        self.assertEqual(pair, (value_bytes(payload), value_bytes(payload)))
        bind_selected(manager, selected, values=request, subject=subject, candidate=subject,
            authoritative_requirement=policy, resulting_requirement=policy, authoritative_roots=[],
            agent=agent, agent_record=payload, role='primary', prepared_cursor=cursor)
        self.assertEqual(self.core.collapse_decide_with_evaluation(request,
            primary=selected.raw, staged=None, agent=agent), 'AUTHORIZED')
        return selected

    def test_actual_terminal_material_without_finalization_preserves_domain(self):
        with self.staged_journal() as (manager, subject, policy, previous, _append, _terminal):
            selected = self.bind_real_material(manager, subject, policy, previous)
            self.assertIsNotNone(selected.authority_material)
            self.assertIsNone(selected.authority_material.finalization)

    def test_actual_native_reserved_unsealed_start_preserves_domain(self):
        with self.staged_journal() as (manager, subject, policy, previous, _append, _terminal):
            with TemporaryDirectory(prefix='worldline-agent-unsealed-') as directory:
                journal = FinalizationJournal(Path(directory) / 'final.sqlite', 'store',
                    library=Path(self.core.library_path), create=True)
                try:
                    start, _inputs = _Native.values(self)
                    start = replace(start, store_id=b'store', subject=identity(subject.instance_id),
                        run=b'actual-reserved-unsealed-run', requirement=identity(policy['requirementHash']))
                    journal.reserve(start)  # actual original native start + durable COMMIT
                    manager.store.evaluation_finalization = journal
                    selected = self.bind_real_material(manager, subject, policy, previous)
                    self.assertEqual(selected.authority_material.finalization[0], start)
                    self.assertIsNone(selected.authority_material.finalization[1])
                    self.assertIsNone(journal.retained(subject.instance_id)[1])
                finally:
                    journal.close()

    def test_exact_legacy_agent_shape_keeps_original_acceptance(self):
        case = list(self.independent_agent_case())
        legacy = {'id': 'agent', 'kind': 'build', 'format': 'exit', 'status': 'PASS',
            'exitCode': 0, 'supervision': {'kind': 'SUPERVISED'}, 'rawEventHash': 'retained-raw',
            'resources': {'ceilingFired': False}}
        case[1].evidence = {'checks': [deepcopy(legacy)]}
        material = case[3].authority_material
        start, sealed, events = material.finalization
        sealed = replace(sealed, value=replace(sealed.value,
            evidence=canonical_bytes(case[1].evidence)))
        case[3].authority_material = replace(material, finalization=(start, sealed, events))
        case[-1], mapped = runner_agent_record(legacy)
        self.assertTrue(mapped)
        self.assertNotIn('origin', legacy)
        self.assertEqual(self.joined_decision(tuple(case)), 'AUTHORIZED')

    def test_changed_sealed_content_is_native_refusal(self):
        case = self.independent_agent_case()
        material = case[3].authority_material
        start, sealed, events = material.finalization
        case[3].authority_material = replace(material, finalization=(start,
            replace(sealed, value=replace(sealed.value, content=b'other-retained-content')), events))
        self.assertEqual(self.joined_decision(case), 'INVALID_REQUEST')

    def test_malformed_material_and_sealed_dtos_do_not_take_absence_branch(self):
        for malformed in ({}, (), {'finalization': None}):
            case = self.independent_agent_case()
            case[3].authority_material = malformed
            with self.assertRaises(WorldlineError) as caught:
                self.joined_decision(case)
            self.assertEqual(caught.exception.code, 'EVALUATION_CAPTURE_INVALID')
        for malformed in ((), [], ('only-one-field',), (None, object(), ())):
            case = self.independent_agent_case()
            case[3].authority_material = replace(case[3].authority_material, finalization=malformed)
            with self.assertRaises(WorldlineError) as caught:
                self.joined_decision(case)
            self.assertEqual(caught.exception.code, 'EVALUATION_CAPTURE_INVALID')


def load_tests(loader, _standard_tests, _pattern):
    # Only this additive module's new cases; original modules/rosters unchanged.
    return unittest.TestSuite(AgentBindingAdditionalControls(name)
        for name in AgentBindingAdditionalControls.__dict__ if name.startswith('test_'))
