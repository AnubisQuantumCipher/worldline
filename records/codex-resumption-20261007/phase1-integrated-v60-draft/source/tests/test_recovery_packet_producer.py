"""Ordinary packet/native replay controls; protected custody is not a claim.

These additive cases use the original accepted fixture, actual temporary
pending/terminal/finalization journals and actual native ABI. They do not change
its assertions and do not mock native permission, world exchange or confinement.
"""
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from test_raw_evaluation_default import RawRequiredFailureControls as _Fixture
from test_finalization_kernel import FinalizationNativeControls as _FinalizationFixture
from worldline.core import hash_id
from worldline.errors import WorldlineError
from worldline.evaluation_authority import read, read_material
from worldline.evaluation_context import bind_selected
from worldline.evaluation_pending import identity
from worldline.finalization_journal import FinalizationJournal
from worldline.model import World, WorldState
from worldline.recovery_material import AuthorityMaterial
from worldline.recovery_observation import (
    archive, restore_archive, capture_packet, restore_packet, redecide_packet,
    protected_historical_authority,
)


class RecoveryPacketProducerControls(_Fixture):
    def full_world(self, subject, request):
        return World(instance_id=subject.instance_id, alias='ordinary-packet-fixture',
            parent_instance=None, parent_content=hash_id(request.expected_parent),
            cause='ordinary-test-input', actor='ordinary-test-input', born='ordinary-test-input',
            ended=None, state=WorldState.VALID, components={}, content_id=subject.content_id,
            payload_path='', mission_hash='', agent_reference=None,
            evidence=deepcopy(subject.evidence), workspace={}, base_payload_path='',
            base_root=hash_id(request.expected_base), root_set_hash=subject.root_set_hash,
            delta_hash=hash_id(request.expected_delta), delta={}, conflicts=[], contamination=[])

    def owned_packet(self, manager, subject, policy, cursor):
        request, agent = manager.staged_fixture_values
        world = self.full_world(subject, request)
        chosen = read(manager.store, world, policy['requirementHash'], prepared=cursor, core=self.core)
        bind_selected(manager, chosen, values=request, subject=world, candidate=world,
            authoritative_requirement=policy, resulting_requirement=policy, authoritative_roots=[],
            agent=agent, agent_record=world.evidence['checks'][0], role='primary', prepared_cursor=cursor)
        verdict = self.core.collapse_decide_with_evaluation(request,
            primary=chosen.raw, staged=None, agent=agent)
        packet = capture_packet(values=request, primary=chosen, staged=None, agent=agent,
            agent_record=world.evidence['checks'][0],
            inputs={'primary': {'evaluationCursor': cursor}, 'staged': {'ran': False}},
            candidate=world, subject=world, witness=None, authoritative_requirement=policy,
            resulting_requirement=policy, authoritative_roots=[], current_requirement=policy['requirementHash'])
        return packet, chosen, verdict

    def test_actual_decision_observer_captures_full_real_producer_and_redecides(self):
        from worldline.transaction import CollapseTransaction
        with self.staged_journal() as (manager, subject, policy, previous, _append, _terminal):
            request, _agent = manager.staged_fixture_values
            world = self.full_world(subject, request)
            inputs = {'conflictsMeasured': True, 'foreignWrites': {'state': request.foreign_writes},
                'expectedSubject': hash_id(request.expected_subject),
                'evidenceSubject': hash_id(request.evidence_subject),
                'testedRoot': hash_id(request.tested_root),
                'primary': {'rosterComplete': request.roster_complete,
                    'declaredVerifiers': hash_id(request.declared_verifiers),
                    'executedVerifiers': hash_id(request.executed_verifiers),
                    'evaluatedRequirement': hash_id(request.evaluated_requirement),
                    'evaluationCursor': previous['evaluationCursor']},
                'staged': {'ran': False, 'rosterComplete': request.staged_roster_complete},
                'watchSets': {'registered': hash_id(request.registered_watch_set),
                              'watched': hash_id(request.watched_set)},
                'generations': {'before': request.generation_before, 'after': request.generation_after}}
            observed = CollapseTransaction._observe_decision(manager,
                phase=request.phase, kind_mode='collapse', candidate=world, subject=world,
                expected_parent=hash_id(request.expected_parent), base_root=hash_id(request.candidate_base),
                delta_hash=hash_id(request.candidate_delta), root_set=hash_id(request.expected_root_set),
                expected_staged_root=hash_id(request.expected_staged_root),
                actual_staged_root=hash_id(request.actual_staged_root),
                staged_content_root=hash_id(request.staged_content_root), conflicts=False,
                current_requirement=policy['requirementHash'], resulting_requirement=policy,
                inputs=inputs, witness=None, authoritative_requirement=policy,
                authoritative_roots=[], retain_packet=True)
            self.assertEqual(observed.values, request)
            self.assertEqual(observed.decide(self.core), 'AUTHORIZED')
            self.assertEqual(redecide_packet(observed.packet, core=self.core), 'AUTHORIZED')
            retained = restore_archive(observed.packet)
            self.assertEqual(retained['inputs'], inputs)
            self.assertIs(type(retained['primary']['authorityMaterial']), AuthorityMaterial)

    def test_complete_packet_reconstructs_real_owned_arenas_and_same_native_decision(self):
        with self.staged_journal() as (manager, subject, policy, previous, _append, terminal):
            before = terminal.snapshot(subject.instance_id)
            packet, chosen, verdict = self.owned_packet(manager, subject, policy, previous['evaluationCursor'])
            self.assertEqual(verdict, 'AUTHORIZED')
            observation = restore_packet(packet, core=self.core)
            self.assertEqual(observation.packet, packet)
            self.assertEqual(observation.decide(self.core), verdict)
            self.assertEqual(restore_archive(packet)['primary']['authorityMaterial'], chosen.authority_material)
            self.assertEqual(terminal.snapshot(subject.instance_id), before)

    def test_replay_keeps_historical_policy_separate_from_later_live_policy(self):
        with self.staged_journal() as (manager, subject, policy, previous, append, terminal):
            packet, _chosen, verdict = self.owned_packet(manager, subject, policy, previous['evaluationCursor'])
            append(status='FAIL')
            with self.assertRaises(WorldlineError) as refused:
                read(manager.store, subject, policy['requirementHash'], core=self.core)
            self.assertEqual(refused.exception.code, 'EVIDENCE_FAIL_TERMINAL')
            policy['execution']['later-policy-observation'] = 'revoked-or-changed'
            self.assertEqual(redecide_packet(packet, core=self.core), verdict)
            restored = restore_archive(packet)
            self.assertNotIn('later-policy-observation', restored['authoritativeRequirement']['execution'])

    def test_unsealed_finalization_retains_whole_start_and_events_when_history_speaks(self):
        with self.staged_journal() as (manager, subject, policy, previous, _append, _terminal):
            start, _unused = _FinalizationFixture.values(self)
            start = replace(start, store_id=b'store', subject=identity(subject.instance_id),
                run=b'ordinary-unsealed-start', requirement=identity(policy['requirementHash']))
            with TemporaryDirectory(prefix='worldline-packet-unsealed-') as directory:
                finalization = FinalizationJournal(Path(directory)/'finalization.db', b'store',
                    library=Path(self.core.library_path), create=True)
                try:
                    finalization.reserve(start)
                    raw_observation = {'kind': 'private-process-return', 'occurrence': None,
                        'observation': (b'raw\0stdout\xff', None, [b'duplicate', b'duplicate'])}
                    finalization.observe(start, b'raw-event-a', b'raw-invocation', 'acquisition', raw_observation)
                    finalization.observe(start, b'raw-event-b', b'raw-invocation', 'acquisition', raw_observation)
                    manager.store.evaluation_finalization = finalization
                    packet, chosen, verdict = self.owned_packet(manager, subject, policy, previous['evaluationCursor'])
                    self.assertEqual(chosen.authority_material.finalization, finalization.retained(subject.instance_id))
                    self.assertIsNone(chosen.authority_material.finalization[1])
                    restored = restore_archive(packet)['primary']['authorityMaterial'].finalization
                    self.assertEqual(restored[0], start)
                    self.assertEqual(restored[2], finalization.retained(subject.instance_id)[2])
                    self.assertEqual([event['phase'] for event in restored[2]], ['acquisition', 'acquisition'])
                    self.assertEqual(restored[2][0]['payload'], restored[2][-1]['payload'])
                    self.assertEqual(redecide_packet(packet, core=self.core), verdict)
                finally:
                    finalization.close()

    def test_all_old_failure_and_new_pass_rows_are_retained_and_cannot_be_filtered(self):
        with self.staged_journal() as (manager, subject, policy, _previous, append, terminal):
            append(status='FAIL')
            cursor = append(status='PASS')
            full = terminal.authority_material_full(subject.instance_id)
            material = AuthorityMaterial(tuple(full), None, terminal.pending.store)
            restored = restore_archive(archive(material))
            self.assertEqual(restored, material)
            self.assertEqual([row[0].outcome for row in restored.terminal[2]], ['PASS', 'FAIL', 'PASS'])
            with self.assertRaises(WorldlineError) as refused:
                read_material(subject, policy['requirementHash'], restored, prepared=cursor, core=self.core)
            self.assertEqual(refused.exception.code, 'EVIDENCE_FAIL_TERMINAL')

    def test_changed_full_selection_cursor_or_missing_material_refuses(self):
        with self.staged_journal() as (manager, subject, policy, previous, _append, _terminal):
            packet, _chosen, _verdict = self.owned_packet(manager, subject, policy, previous['evaluationCursor'])
            for change in ('selection', 'cursor', 'material', 'pending-store', 'extra-schema-field'):
                value = restore_archive(packet)
                if change == 'selection':
                    value['primary']['results'][0]['status'] = 'FAIL'
                elif change == 'cursor':
                    value['inputs']['primary']['evaluationCursor']['run'] = 'absent-run'
                elif change == 'material':
                    value['primary']['authorityMaterial'] = None
                elif change == 'pending-store':
                    value['primary']['authorityMaterial'] = replace(
                        value['primary']['authorityMaterial'], pending_store=None)
                else:
                    value['protected-success'] = True
                with self.subTest(change=change), self.assertRaises(WorldlineError):
                    restore_packet(archive(value), core=self.core)

    def test_raw_retained_metadata_substitution_refuses_before_native_collapse(self):
        with self.staged_journal() as (manager, subject, policy, previous, _append, _terminal):
            packet, _chosen, _verdict = self.owned_packet(manager, subject, policy, previous['evaluationCursor'])
            value = restore_archive(packet)
            material = value['primary']['authorityMaterial']
            journal, current, rows, streams = material.terminal
            summary, retained = rows[-1]
            stored, capture, results = retained
            altered = (*results[:-1], replace(results[-1], source=b'other-full-raw-source'))
            changed_rows = (*rows[:-1], (summary, (stored, capture, altered)))
            value['primary']['authorityMaterial'] = replace(material,
                terminal=(journal, current, changed_rows, streams))
            with self.assertRaises(WorldlineError):
                restore_packet(archive(value), core=self.core)

    def test_native_positive_packet_cannot_manufacture_protected_historical_authority(self):
        with self.staged_journal() as (manager, subject, policy, previous, _append, _terminal):
            packet, _chosen, verdict = self.owned_packet(manager, subject, policy, previous['evaluationCursor'])
            self.assertEqual(verdict, 'AUTHORIZED')
            self.assertEqual(redecide_packet(packet, core=self.core), 'AUTHORIZED')
            with self.assertRaises(WorldlineError) as refused:
                protected_historical_authority(packet, core=self.core)
            self.assertEqual(refused.exception.code, 'RECOVERY_PROTECTED_AUTHORITY_UNAVAILABLE')

    def test_original_constructor_fixture_is_accepted_but_missing_packet_material_named_refuses(self):
        _manager, subject, policy, chosen, request, agent = self.producer_case()
        self.assertIsNone(chosen.authority_material)
        with self.assertRaises(WorldlineError) as refused:
            capture_packet(values=request, primary=chosen, staged=None, agent=agent,
                agent_record=None, inputs={}, candidate=subject, subject=subject, witness=None,
                authoritative_requirement=policy, resulting_requirement=policy, authoritative_roots=[])
        self.assertEqual(refused.exception.code, 'RECOVERY_PACKET_MATERIAL')


def load_tests(loader, tests, pattern):
    # The original suite remains unchanged and is discovered separately. Here
    # reuse its accepted fixture without duplicating every inherited campaign.
    names = [name for name, method in RecoveryPacketProducerControls.__dict__.items()
             if name.startswith('test_') and callable(method)]
    return unittest.TestSuite(RecoveryPacketProducerControls(name) for name in names)


if __name__ == '__main__':
    unittest.main()
