"""Full native packet controls from the original actual transaction actor.

The original OwnedTransactionEvaluation runs GenericAdapter in its actual
sandbox, retains real journals and observations, and revalidates. Nothing here
assigns a success/confinement/authority label or performs a live exchange.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path
import unittest

from test_transaction import CollapseTransactionTests
from worldline.errors import WorldlineError
from worldline.manifest import Manifest
from worldline.validation import current_requirements, content_root_set
from worldline.recovery_observation import archive, restore_archive, capture_packet, restore_packet, redecide_packet, acquire_syntax_facts
from worldline.raw_completion_kernel import PreparedRawEvaluation


class RecoveryPacketNativeControls(CollapseTransactionTests):
    def actual_packet(self):
        candidate = self._candidate('native full recovery packet actual actor')
        prepared = self.transaction.prepare(candidate.alias)
        self.assertEqual(prepared.decision, 'AUTHORIZED')
        record = self.transaction._load_record(prepared.transaction_id)
        generation = self.transaction._generation()
        current = self.transaction._capture_current_roots()
        staged = self.transaction._capture_staged(record)
        requirement = current_requirements(self.store, self.transaction.config, self.core)
        decision, observed = self.transaction._observe_authorization(
            record, candidate, current_manifests=current,
            staged_root=Manifest.root_set_hash(staged.values(), self.core),
            staged_content_root=content_root_set(staged, self.core),
            current_requirement=requirement, generation_before=generation)
        self.assertEqual(decision, 'AUTHORIZED')
        self.assertEqual(observed.decide(self.core), 'AUTHORIZED')
        self.assertIs(type(observed.packet), bytes)
        return observed.packet

    def test_actual_actor_complete_native_packet_and_all_full_source_mutations(self):
        raw = self.actual_packet()
        self.assertEqual(redecide_packet(raw, core=self.core), 'AUTHORIZED')
        restored = restore_packet(raw, core=self.core)
        self.assertIs(type(restored.primary), PreparedRawEvaluation)
        self.assertEqual(restored.packet, raw)
        self.assertEqual(restored.decide(self.core), 'AUTHORIZED')
        with self.assertRaises(WorldlineError) as mismatch:
            replace(restored, values=replace(restored.values, conflicts='FOUND')).decide(self.core)
        self.assertEqual(mismatch.exception.code, 'RECOVERY_PACKET_PROJECTION_CHANGED')
        original = restore_archive(raw)
        self.assertEqual(archive(original), raw)
        agent = original['agentRecord']
        self.assertEqual(agent['origin'], 'agent')
        self.assertEqual(agent['exitCode'], 0)
        self.assertEqual(agent['supervision']['kind'], 'SUPERVISED')
        self.assertIs(agent['resources']['ceilingFired'], False)
        from worldline.evaluation_authority import read
        chosen = read(self.store, original['subject'], original['currentRequirementArgument'],
                      prepared=original['inputs']['primary']['evaluationCursor'], core=self.core)
        staged = (None if original['staged'] is None else
            read(self.store, original['subject'], original['currentRequirementArgument'],
                 prepared=original['inputs']['staged']['evaluationCursor'], core=self.core))
        changed_requirement = dict(original['authoritativeRequirement'])
        changed_requirement['requirementHash'] = 'sha256:' + '3' * 64
        refused_capture = capture_packet(values=original['values'], primary=chosen, staged=staged,
            agent=original['agent'], agent_record=original['agentRecord'], inputs=original['inputs'],
            candidate=original['candidate'], subject=original['subject'], witness=original['witness'],
            authoritative_requirement=changed_requirement, resulting_requirement=original['resultingRequirement'],
            authoritative_roots=original['authoritativeRoots'],
            current_requirement=original['currentRequirementArgument'], owner=original.get('owner'),
            core=self.core)
        # Capture is lossless observation transport, not native permission.
        self.assertIs(type(refused_capture), bytes)
        with self.assertRaises(WorldlineError):
            redecide_packet(refused_capture, core=self.core)
        for mutation in ('source', 'selected-result', 'prepared-cursor', 'pending-store',
                         'authoritative-requirement', 'resulting-requirement', 'agent',
                         'actual-agent', 'typed-row-source', 'retained-stream', 'schema'):
            packet = restore_archive(raw)
            selected = packet['primary']
            if mutation == 'source':
                selected['source'] += ':changed'
            elif mutation == 'selected-result':
                selected['results'][0]['status'] = 'FAIL'
            elif mutation == 'prepared-cursor':
                packet['inputs']['primary']['evaluationCursor']['run'] += ':changed'
            elif mutation == 'pending-store':
                selected['authorityMaterial'] = replace(selected['authorityMaterial'], pending_store=None)
            elif mutation == 'authoritative-requirement':
                packet['authoritativeRequirement']['requirementHash'] = 'sha256:' + '1' * 64
            elif mutation == 'resulting-requirement':
                packet['resultingRequirement']['requirementHash'] = 'sha256:' + '2' * 64
            elif mutation == 'agent':
                packet['agentRecord']['exitCode'] = 1
            elif mutation == 'actual-agent':
                next(row for row in packet['subject'].evidence['checks'] if row['id'] == 'agent')['exitCode'] = 1
            elif mutation == 'typed-row-source':
                rows = selected['typedRows']
                selected['typedRows'] = (*rows[:-1], replace(rows[-1], source=b'changed-actual-retained-source'))
            elif mutation == 'retained-stream':
                selected['retainedStream'] = None
            else:
                packet['authority-label'] = True
            with self.subTest(mutation=mutation), self.assertRaises(WorldlineError):
                redecide_packet(archive(packet), core=self.core)


def export_actual_packet(directory, *, syntax_context=None):
    """Main-only exporter: produce original full bytes, no synthetic arena."""
    destination = Path(directory)
    destination.mkdir(mode=0o700, parents=True, exist_ok=False)
    case = RecoveryPacketNativeControls('test_actual_actor_complete_native_packet_and_all_full_source_mutations')
    try:
        case.setUp()
        raw = case.actual_packet()
        (destination / 'actual-transaction-actor.packet').write_bytes(raw)
        # A complete operation DTO copy is an independent decoder/domain control,
        # not a replacement for the original packet consumed by native Complete.
        from worldline.operation_capture import archive as operation_archive
        (destination / 'actual-transaction-actor.operation').write_bytes(operation_archive(restore_archive(raw)))
        # Primitive syntax acquisition is genuine native-requested work under
        # Main's actual qualified shared admission, not a fixture AST/label.
        capsules = acquire_syntax_facts(raw, core=case.core, syntax_context=syntax_context)
        (destination / 'actual-transaction-actor.syntax-facts.operation').write_bytes(
            operation_archive(capsules))
        return destination / 'actual-transaction-actor.packet'
    finally:
        try:
            case.tearDown()
        finally:
            case.doCleanups()


def load_tests(loader, tests, pattern):
    return unittest.TestSuite((RecoveryPacketNativeControls(
        'test_actual_actor_complete_native_packet_and_all_full_source_mutations'),))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--export', type=Path)
    args, remaining = parser.parse_known_args()
    if args.export is not None:
        print(export_actual_packet(args.export))
    else:
        unittest.main(argv=['recovery_packet_native_controls.py', *remaining])
