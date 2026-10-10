"""Unexecuted native context controls; synthetic source DTOs, no custody claim.

Run these named methods in the admitted ordinary frame with the existing real
WORLDLINE_CORE_LIB and original test support. No native decision is mocked.
"""
from copy import deepcopy
from dataclasses import replace
from test_raw_evaluation_default import RawRequiredFailureControls
from worldline.evaluation_context import bind_selected, agent_context_pair
from worldline.evaluation_terminal import value_bytes
from worldline.evaluation_pending import identity
from worldline.canonical import canonical_bytes
from worldline.recovery_material import AuthorityMaterial
from worldline.finalization_values import (StartValue, InputValue, CaptureValue,
    ComponentsValue, SealValue, ClassifiedValue, SealedValue)

class FinalizationAgentBindingControls(RawRequiredFailureControls):
    def independent_agent_case(self):
        manager, subject, policy, chosen, request, agent = self.producer_case()
        payload = {'id': 'agent', 'origin': 'agent', 'format': 'exit', 'status': 'PASS',
            'exitCode': 0, 'supervision': {'kind': 'SUPERVISED'},
            'resources': {'ceilingFired': False}}
        evidence = {'checks': [deepcopy(payload)], 'extra-retained-field': ['complete', None]}
        subject.evidence = deepcopy(evidence)
        # Complete typed shape for correspondence testing. The finalization
        # seal/authentication is intentionally NOT claimed by this fixture.
        start = StartValue(b'store', identity(subject.instance_id), b'final-run', b'',
            identity(policy['requirementHash']), value_bytes(policy), b'plan', b'context',
            b'parent', b'config', b'repository', (), 'Explicit_Empty')
        input_value = InputValue(start, b'root', b'manifests', b'filesystem', b'config', b'repository')
        capture = CaptureValue(start, input_value, b'root', b'manifests', b'context',
            b'source', (), (b'evaluation-complete', b'declaration'))
        seal_value = SealValue(capture, identity(subject.content_id),
            ComponentsValue(b'environment', b'evidence-component'), canonical_bytes(evidence), b'environment')
        sealed = SealedValue(seal_value, b'seal-id', ClassifiedValue('Completed', 'PASS', True),
            'COMPLETED', 'PASS')
        chosen.authority_material = AuthorityMaterial((), (start, sealed, ()), b'store')
        return manager, subject, policy, chosen, request, agent, payload

    def joined_decision(self, case):
        manager, subject, policy, chosen, request, agent, payload = case
        bind_selected(manager, chosen, values=request, subject=subject, candidate=subject,
            authoritative_requirement=policy, resulting_requirement=policy, authoritative_roots=[],
            agent=agent, agent_record=payload, role='primary', prepared_cursor=chosen.cursor)
        return self.core.collapse_decide_with_evaluation(request,
            primary=chosen.raw, staged=None, agent=agent)

    def test_retained_finalization_agent_matches_actual_context(self):
        case = self.independent_agent_case()
        self.assertEqual(self.joined_decision(case), 'AUTHORIZED')

    def test_changed_agent_payload_cannot_compare_with_itself(self):
        case = self.independent_agent_case()
        # Still a PASS raw record and unchanged legacy hashes. Equality must
        # use the independent retained evidence, not this changed dict twice.
        case[-1]['extra-agent-metadata'] = 'substituted'
        case[1].evidence['checks'][0]['extra-agent-metadata'] = 'substituted'
        self.assertEqual(self.joined_decision(case), 'INVALID_REQUEST')

    def test_unrelated_finalization_evidence_not_filtered_out(self):
        case = self.independent_agent_case()
        case[1].evidence['extra-retained-field'] = ['changed', None]
        self.assertEqual(self.joined_decision(case), 'INVALID_REQUEST')

    def test_other_retained_subject_cannot_share_agent_payload(self):
        case = self.independent_agent_case()
        material = case[3].authority_material
        start, sealed, events = material.finalization
        case[3].authority_material = replace(material,
            finalization=(replace(start, subject=b'other-world'), sealed, events))
        self.assertEqual(self.joined_decision(case), 'INVALID_REQUEST')

    def test_full_agent_list_is_retained_even_with_duplicate_names(self):
        case = self.independent_agent_case()
        case[1].evidence['checks'].append(deepcopy(case[-1]))
        self.assertEqual(self.joined_decision(case), 'INVALID_REQUEST')

    def test_existing_constructor_pair_stays_identical(self):
        manager, subject, policy, chosen, request, agent = self.producer_case()
        original = {'ordinary-agent': True}
        self.assertEqual(agent_context_pair(chosen, subject, original),
                         (value_bytes(original), value_bytes(original)))
