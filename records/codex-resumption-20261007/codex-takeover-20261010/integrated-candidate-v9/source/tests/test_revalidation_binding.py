"""A promotion decision must read its freshness half and its execution half from ONE evaluation.

Campaign F5/F6. Two defects around revalidation:

F5  A revalidation stores a fresh context but the promotion path read the execution identity
    from the world's FINALIZATION evidence, assembling one apparently complete evaluation from
    two runs -- run 2's freshness over run 1's execution binding. The revalidation entry also
    projected its own results down to {id, status, required, reason}, discarding the execution
    facts, so even reading the right entry would have found nothing.

F6  Revalidation built its evaluation overlays from the candidate's payload and then staged the
    examiner from that SAME lower layer -- so the candidate's own bytes supplied the examiner
    that judged it. The trusted evaluator snapshot must be current PRIME, named separately from
    the tree under evaluation.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "runtime"))

from worldline.agents.generic import GenericAdapter  # noqa: E402
from worldline.config import GenericAgentCommand  # noqa: E402
from worldline.causal import CausalIndexer  # noqa: E402
from worldline.canonical import canonical_bytes  # noqa: E402
from worldline.core import Core, hash_id  # noqa: E402
from worldline.delta import Delta  # noqa: E402
from worldline.errors import WorldlineError  # noqa: E402
from worldline.manifest import Manifest  # noqa: E402
from worldline.model import World, WorldState  # noqa: E402
from worldline.paths import WorldlinePaths  # noqa: E402
from worldline.project import ProjectConfig  # noqa: E402
from worldline.roots import RootManager  # noqa: E402
from worldline.validation import current_requirements, effective_evidence  # noqa: E402
from owned_evaluation_support import OwnedTransactionEvaluation, WRITE_STATE  # noqa: E402
from validation_support import DECLARED_EMPTY_POLICY  # noqa: E402


# This is the examiner actually staged from PRIME and run by the private backend.
# Its report follows the observed worker return; the fixture does not construct a
# result record, completion record, context, confinement fact, or authority answer.
EXAMINER = '''import candidate
from pathlib import Path
result = candidate.run(['/usr/bin/python3', '-c',
    "from pathlib import Path; print(Path('state.txt').read_text())"], timeout=20)
ok = result.returncode == 0 and result.stdout.startswith(b'candidate')
Path('/run/worldline-report/report').write_text(
    '<testsuite tests="1" failures="' + ('0' if ok else '1') + '" errors="0"/>')
print('owned examiner passed' if ok else 'owned examiner failed')
raise SystemExit(0 if ok else 1)
'''


class OneCoherentEvaluation(unittest.TestCase):
    """Real temporary producers; no legacy metadata can authorize selection.

    The finalization-only positives require the actual Start/Seal journal and
    default F-slot integration. The required-examiner positives also require
    measured confinement. These are required assertions, not skips or expected
    failures; provisioning those producers remains a composition prerequisite.
    """

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-revalidation-")
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        env = {
            "HOME": str(root / "home"),
            "XDG_DATA_HOME": str(root / "data"),
            "XDG_STATE_HOME": str(root / "state"),
            "XDG_CONFIG_HOME": str(root / "config"),
            "XDG_RUNTIME_DIR": str(root / "runtime"),
        }
        for value in env.values():
            Path(value).mkdir(mode=0o700, parents=True, exist_ok=True)
        self.paths = WorldlinePaths.from_environment(env)
        self.core = Core.shared()
        self.evaluation = OwnedTransactionEvaluation(self, self.paths, self.core)
        self.addCleanup(self.evaluation.close)
        self.store = self.evaluation.store
        self.roots = RootManager(self.paths, self.store, core=self.core, toolchains=())
        self.work = root / "work"
        self.work.mkdir()
        (self.work / "state.txt").write_text("prime", encoding="utf-8")
        (self.work / ".worldline.json").write_text(
            json.dumps(DECLARED_EMPTY_POLICY), encoding="utf-8")
        self.roots.register([self.work], confirmed=True)
        self.sequence = 0

    def _primary(self) -> Path:
        root = next(item for item in self.store.roots() if item['primary_root'])
        return Path(os.fsdecode(self.paths.root_source(root)))

    def _policy(self, **changes) -> None:
        policy = {**DECLARED_EMPTY_POLICY, **changes}
        (self._primary() / '.worldline.json').write_text(json.dumps(policy), encoding='utf-8')

    def _private_policy(self) -> None:
        (self._primary() / 'exam.py').write_text(EXAMINER, encoding='utf-8')
        self._policy(checks=[{
            'id': 'exam', 'kind': 'tests', 'argv': ['/usr/bin/python3', 'exam.py'],
            'required': True, 'format': 'junit', 'verifiers': ['exam.py'],
            'profile': 'private-evaluator-v1',
        }])

    def _candidate(self, value='candidate') -> World:
        """Actual agent/finalizer only: deliberately no later revalidation."""
        self.sequence += 1
        alias = f'candidate-{self.sequence}'
        root = self.store.roots()[0]
        key, logical = root['root_key'], bytes(root['path'])
        current_source = Path(os.fsdecode(self.paths.root_source(root)))
        base_directory = self.paths.worlds / alias / 'base'
        base_directory.parent.mkdir(mode=0o700, parents=True)
        current = Manifest.capture(current_source, logical_root=logical,
            root_key=key, kind=root['kind'], core=self.core)
        Manifest.materialize(current, current_source, base_directory / key, core=self.core)
        base = Manifest.capture(base_directory / key, logical_root=logical,
            root_key=key, kind=root['kind'], core=self.core)
        parent = self.store.prime()
        world = World.create(alias=alias, parent_instance=parent.instance_id,
            parent_content=parent.content_id, cause=f'set state to {value}', actor='fixture',
            payload_path=self.paths.worlds / alias / 'payload', base_payload_path=base_directory,
            base_root=Manifest.root_set_hash([base], self.core), root_set_hash=parent.root_set_hash,
            mission_hash=hash_id(self.core.hash_bytes(value.encode('utf-8'))))
        self.store.insert_world(world)
        encoded = base64.b64encode(value.encode('utf-8')).decode('ascii')
        command = GenericAgentCommand(name='ordinary-revalidation',
            argv=(sys.executable, '-c', WRITE_STATE, encoded),
            credential_mounts=(), event_format='jsonl', network_hosts=())
        project = ProjectConfig.load(self._primary(), self.store)
        finalized = self.evaluation.runner.run(
            world.alias, GenericAdapter(command), world.cause, project)
        self.assertEqual(finalized.state, WorldState.VALID)
        agent = next(row for row in finalized.evidence['checks'] if row['id'] == 'agent')
        self.assertEqual(agent['origin'], 'agent')
        self.assertEqual(agent['exitCode'], 0)
        self.assertEqual(agent['supervision']['kind'], 'SUPERVISED')
        self.assertIs(agent['resources']['ceilingFired'], False)
        self.assertEqual(self.evaluation.terminal.snapshot(finalized.instance_id)['history'], [])
        return finalized

    def _requirement(self):
        return current_requirements(self.store, self.evaluation.config, self.core)

    def test_missing_base_manifest_does_not_allow_changed_base_causal_events(self) -> None:
        world = self._candidate()
        root = self.store.roots()[0]
        base = Path(world.base_payload_path)
        manifest_path = base / 'manifests' / f"{root['root_key']}.json"
        self.assertFalse(manifest_path.exists())
        before = self.store.causal_events_for_world(world.instance_id)
        self.assertTrue(any(row['kind'] == 'file-delta' for row in before))
        (base / root['root_key'] / 'state.txt').write_text('changed base', encoding='utf-8')
        project = ProjectConfig.load(self._primary(), self.store)
        with self.assertRaises(WorldlineError) as caught:
            CausalIndexer(self.store).index(world, project)
        self.assertEqual(caught.exception.code, 'BASE_ROOT_MISMATCH')
        self.assertEqual(self.store.causal_events_for_world(world.instance_id), before)
        self.assertFalse(manifest_path.exists())

    def test_saved_base_manifest_does_not_allow_changed_base_causal_events(self) -> None:
        world = self._candidate()
        root = self.store.roots()[0]
        base = Path(world.base_payload_path)
        source = base / root['root_key']
        manifest = Manifest.capture(source, logical_root=bytes(root['path']),
            root_key=root['root_key'], kind=root['kind'], core=self.core)
        self.assertEqual(Manifest.root_set_hash([manifest], self.core), world.base_root)
        manifest_path = base / 'manifests' / f"{root['root_key']}.json"
        manifest_path.parent.mkdir()
        manifest.save(manifest_path)
        original_manifest = manifest_path.read_bytes()
        before = self.store.causal_events_for_world(world.instance_id)
        self.assertTrue(any(row['kind'] == 'file-delta' for row in before))
        (source / 'state.txt').write_text('changed saved base', encoding='utf-8')
        project = ProjectConfig.load(self._primary(), self.store)
        with self.assertRaises(WorldlineError) as caught:
            CausalIndexer(self.store).index(world, project)
        self.assertEqual(caught.exception.code, 'BASE_CHECKPOINT_UNVERIFIED')
        self.assertEqual(self.store.causal_events_for_world(world.instance_id), before)
        self.assertEqual(manifest_path.read_bytes(), original_manifest)

    def test_saved_base_manifest_does_not_allow_actual_metadata_change(self) -> None:
        world = self._candidate()
        root = self.store.roots()[0]
        base = Path(world.base_payload_path)
        source = base / root['root_key']
        manifest = Manifest.capture(source, logical_root=bytes(root['path']),
            root_key=root['root_key'], kind=root['kind'], core=self.core)
        self.assertEqual(Manifest.root_set_hash([manifest], self.core), world.base_root)
        manifest_path = base / 'manifests' / f"{root['root_key']}.json"
        manifest_path.parent.mkdir()
        manifest.save(manifest_path)
        original_manifest = manifest_path.read_bytes()
        before = self.store.causal_events_for_world(world.instance_id)
        self.assertTrue(any(row['kind'] == 'file-delta' for row in before))
        state = source / 'state.txt'
        original_content = state.read_bytes()
        original_mode = stat.S_IMODE(state.stat().st_mode)
        state.chmod(original_mode ^ stat.S_IXUSR)
        self.assertNotEqual(stat.S_IMODE(state.stat().st_mode), original_mode)
        self.assertEqual(state.read_bytes(), original_content)
        project = ProjectConfig.load(self._primary(), self.store)
        with self.assertRaises(WorldlineError) as caught:
            CausalIndexer(self.store).index(world, project)
        self.assertEqual(caught.exception.code, 'BASE_ROOT_MISMATCH')
        self.assertEqual(self.store.causal_events_for_world(world.instance_id), before)
        self.assertEqual(manifest_path.read_bytes(), original_manifest)

    def test_saved_manifest_metadata_identity_refusal_is_preserved(self) -> None:
        world = self._candidate()
        root = self.store.roots()[0]
        base = Path(world.base_payload_path)
        source = base / root['root_key']
        manifest = Manifest.capture(source, logical_root=bytes(root['path']),
            root_key=root['root_key'], kind=root['kind'], core=self.core)
        self.assertEqual(Manifest.root_set_hash([manifest], self.core), world.base_root)
        manifest_path = base / 'manifests' / f"{root['root_key']}.json"
        manifest_path.parent.mkdir()
        manifest.save(manifest_path)
        before = self.store.causal_events_for_world(world.instance_id)
        self.assertTrue(any(row['kind'] == 'file-delta' for row in before))
        state = source / 'state.txt'
        original_content = state.read_bytes()
        original_mode = stat.S_IMODE(state.stat().st_mode)
        changed = json.loads(manifest_path.read_bytes())
        changed['rootMetadata']['mode'] ^= stat.S_IXUSR
        manifest_path.write_bytes(canonical_bytes(changed))
        changed_manifest = manifest_path.read_bytes()
        self.assertNotEqual(changed_manifest, manifest.canonical)
        self.assertEqual(state.read_bytes(), original_content)
        self.assertEqual(stat.S_IMODE(state.stat().st_mode), original_mode)
        project = ProjectConfig.load(self._primary(), self.store)
        with self.assertRaises(WorldlineError) as caught:
            CausalIndexer(self.store).index(world, project)
        self.assertEqual(caught.exception.code, 'BASE_ROOT_MISMATCH')
        self.assertEqual(self.store.causal_events_for_world(world.instance_id), before)
        self.assertEqual(manifest_path.read_bytes(), changed_manifest)

    def _effective(self, world):
        return effective_evidence(self.store, world, requirement_hash=self._requirement()['requirementHash'])

    def test_binary_acquisitions_reach_actual_capture_reader_and_native_context(self) -> None:
        import ctypes as C
        from copy import deepcopy
        from dataclasses import replace
        from types import SimpleNamespace
        from unittest.mock import patch
        from worldline.completion_kernel import Optional_Span, Span
        from worldline.evaluation_authority import read
        from worldline.evaluation_context import bind_selected, CONTEXT_FIELDS, ROW_FIELDS, ContextRow
        from worldline.evaluation_wire import record
        from worldline.executed import bundle_identity, NO_BUNDLE_IDENTITY
        from worldline.finalization_journal import encode, decode, payload_acquisitions
        from worldline.finalization_writer import EngineFinalizationWriter
        from worldline.finalize import ENGINE_DECLARATIONS, required_roster, runner_agent_record
        from worldline.validation import content_root_set
        from test_raw_evaluation_default import RawDependencyControls

        # Only these appended acquisition values are an explicit transport
        # fixture. The existing actual agent, source capture, journal, native
        # seal, reader and context binding remain the real implementation.
        fixtures = [{'bytes': b'\x00\xfffirst', 'identity': (b'whole', [None, b''])},
                    {'bytes': b'\x00\xffsecond', 'identity': (b'whole', [None, b''])}]
        original_return = EngineFinalizationWriter.invocation_result
        def returned(writer, *, world_instance, check, result):
            if check == 'agent':
                for fixture in fixtures:
                    writer.invocation_raw(world_instance=world_instance, check=check,
                        kind='explicit-binary-transport-control', observed=fixture, occurrence=0)
            return original_return(writer, world_instance=world_instance, check=check, result=result)
        with patch.object(EngineFinalizationWriter, 'invocation_result', returned):
            world = self._candidate()
        manager = self.evaluation.transaction()
        policy = self._requirement()
        roots = self.store.roots()
        agent_record, _legacy = runner_agent_record(next(
            row for row in world.evidence['checks'] if row['id'] == 'agent'))
        agent = record(agent_record, ENGINE_DECLARATIONS['agent'])

        def bound():
            chosen = read(self.store, world, policy['requirementHash'], core=self.core)
            self.assertEqual(chosen.source, 'finalization')
            header = chosen.retained_stream[0][0]
            root = content_root_set({key: SimpleNamespace(value=value) for key, value in
                header['measurement']['manifests'].items()}, self.core)
            declared = bundle_identity([('', check, NO_BUNDLE_IDENTITY)
                for check in required_roster(policy)[0]])
            subject = manager._identity(manager._subject_digest(world.instance_id, ''))
            # Unrelated watch/stage coordinates come from the existing labelled
            # typed-request fixture. Relevant subject/root/policy/roster values
            # are measured by the actual world and retained finalization.
            request = replace(RawDependencyControls.checkpoint(), mode='CANDIDATE_EVALUATION',
                phase='PREPARE', expected_checkpoint=None, witnessed_checkpoint=None,
                actual_staged_root=None,
                expected_parent=manager._identity(world.parent_content),
                candidate_parent=manager._identity(world.parent_content),
                expected_subject=subject, evidence_subject=subject,
                expected_base=manager._identity(world.base_root), candidate_base=manager._identity(world.base_root),
                expected_delta=manager._identity(world.delta_hash), candidate_delta=manager._identity(world.delta_hash),
                expected_root_set=manager._identity(world.root_set_hash),
                candidate_root_set=manager._identity(world.root_set_hash),
                staged_content_root=manager._identity(root), tested_root=manager._identity(root),
                current_requirement=manager._identity(policy['requirementHash']),
                resulting_requirement=manager._identity(policy['requirementHash']),
                evaluated_requirement=manager._identity(policy['requirementHash']),
                declared_verifiers=manager._identity(declared), executed_verifiers=manager._identity(declared),
                roster_complete=True)
            self.assertEqual(self.core.collapse_raw_dependencies(request),
                {'valid': True, 'primary': True, 'staged': False, 'agent': True})
            bind_selected(manager, chosen, values=request, subject=world, candidate=world,
                authoritative_requirement=policy, resulting_requirement=policy, authoritative_roots=roots, agent=agent,
                agent_record=agent_record, role='primary', prepared_cursor=chosen.cursor)
            self.assertEqual(self.core.collapse_decide_with_evaluation(request,
                primary=chosen.raw, staged=None, agent=agent), 'AUTHORIZED')
            return chosen, request

        chosen, request = bound()
        # Retain the D8 malformed PREPARE request as a negative control. The
        # inherited COMMIT-only field must still be rejected before evidence
        # joining; clearing it above does not weaken the native phase rule.
        malformed_prepare = replace(request,
            actual_staged_root=RawDependencyControls.checkpoint().actual_staged_root)
        self.assertEqual(self.core.collapse_raw_dependencies(malformed_prepare),
            {'valid': False, 'primary': False, 'staged': False, 'agent': False})
        self.assertEqual(self.core.collapse_decide_with_evaluation(malformed_prepare,
            primary=chosen.raw, staged=None, agent=agent), 'INVALID_REQUEST')
        agent_index = next(index for index, row in enumerate(chosen.results) if row['id'] == 'agent')
        projected = payload_acquisitions(chosen.results[agent_index]['engineRawObservations'])
        observed = [event['observation'] for event in projected
                    if event['kind'] == 'explicit-binary-transport-control']
        self.assertEqual(encode(observed), encode(fixtures))
        retained = [event[3] for event in chosen.retained_stream[1]
                    if event[1] == 'explicit-binary-transport-control']
        self.assertEqual(encode(retained), encode(fixtures))

        for lane in ('raw_acquisitions', 'acquisition_stream'):
            for change in ('changed-byte', 'tuple-to-list', 'omission', 'duplicate', 'reordered'):
                with self.subTest(lane=lane, change=change):
                    chosen, request = bound()
                    context = chosen.raw.context
                    if lane == 'raw_acquisitions':
                        rows = C.cast(context.rows, C.POINTER(ContextRow))
                        pair = rows[agent_index].observed
                        field = ROW_FIELDS.index(lane)
                    else:
                        pair = context.observed
                        field = CONTEXT_FIELDS.index(lane)
                    span = pair[field]
                    self.assertEqual(span.present, 1)
                    arena = C.string_at(context.data, context.data_length)
                    raw = arena[span.value.first - 1:span.value.first - 1 + span.value.length]
                    events = list(deepcopy(decode(raw)))
                    indices = [index for index, event in enumerate(events)
                        if (event['kind'] if lane == 'raw_acquisitions' else event[1])
                        == 'explicit-binary-transport-control']
                    first, second = indices
                    payload = events[first]['observation'] if lane == 'raw_acquisitions' else events[first][3]
                    if change == 'changed-byte':
                        payload['bytes'] = b'\x00\xfefirst'
                    elif change == 'tuple-to-list':
                        payload['identity'] = list(payload['identity'])
                    elif change == 'omission':
                        del events[first]
                    elif change == 'duplicate':
                        events.insert(first, deepcopy(events[first]))
                    else:
                        events[first], events[second] = events[second], events[first]
                    altered = encode(events if lane == 'raw_acquisitions' else tuple(events))
                    self.assertNotEqual(altered, raw)
                    data = (C.c_uint8 * (len(arena) + len(altered))).from_buffer_copy(arena + altered)
                    # Change only the observed acquisition lane. The retained
                    # native seal, original rows and metadata stay unchanged;
                    # a metadata mismatch cannot be the reason for refusal.
                    context.data = C.cast(data, C.c_void_p)
                    context.data_length = len(arena) + len(altered)
                    pair[field] = Optional_Span(1, Span(len(arena) + 1, len(altered)))
                    chosen.raw.context_owners += (data,)
                    self.assertEqual(self.core.collapse_decide_with_evaluation(request,
                        primary=chosen.raw, staged=None, agent=agent), 'INVALID_REQUEST')
        self.assertEqual(self.evaluation.terminal.snapshot(world.instance_id)['history'], [])

    def _retained(self, world, answer):
        history = self.evaluation.terminal.snapshot(world.instance_id)['history']
        matches = [row for row in history if row['validationId'] == answer['validationId']]
        self.assertEqual(len(matches), 1)
        row = matches[0]
        self.assertEqual(row['worldInstance'], world.instance_id)
        self.assertEqual(row['worldContentId'], world.content_id)
        self.assertEqual(row['requirementHash'], answer['requirementHash'])
        self.assertEqual(row['evaluationEpoch'], answer['evaluationEpoch'])
        self.assertEqual(row['results'], answer['results'])
        self.assertEqual(row['partialResults'], answer['partialResults'])
        return row

    def test_finalization_speaks_when_there_is_no_revalidation(self) -> None:
        self._private_policy()
        world = self._candidate()
        actual = next(row for row in world.evidence['checks'] if row['id'] == 'exam')
        context, source, records = self._effective(world)
        self.assertEqual(source, 'finalization')
        self.assertEqual(context['contextHash'], world.evidence['validationContext']['contextHash'])
        selected = next(row for row in records if row['id'] == 'exam')
        self.assertEqual(selected['executedVerifierSet'], actual['executedVerifierSet'])
        self.assertEqual(selected['privateReport'], actual['privateReport'])
        self.assertIs(actual['executedVerifierSet']['stable'], True)
        self.assertEqual(self.evaluation.terminal.snapshot(world.instance_id)['history'], [])

    def test_explicit_empty_finalization_is_not_replaced_by_an_extra_revalidation(self) -> None:
        world = self._candidate()
        context, source, records = self._effective(world)
        self.assertEqual(source, 'finalization')
        self.assertEqual(context['candidate']['instanceId'], world.instance_id)
        self.assertEqual(records[-1]['id'], 'evaluation-complete')
        self.assertEqual(self.evaluation.terminal.snapshot(world.instance_id)['history'], [])

    def test_a_passing_revalidation_supplies_BOTH_halves(self) -> None:
        self._private_policy()
        world = self._candidate()
        fork = next(row for row in world.evidence['checks'] if row['id'] == 'exam')
        answer = self.evaluation.revalidator.revalidate(world.alias)
        retained = self._retained(world, answer)
        self.assertEqual(answer['evaluationState'], 'COMPLETED')
        self.assertEqual(answer['outcome'], 'PASS')
        context, source, records = self._effective(world)
        self.assertEqual(source, 'revalidation:' + answer['validationId'])
        self.assertEqual(context, retained['context'])
        self.assertEqual(records, retained['results'])
        self.assertNotEqual(context['contextHash'], world.evidence['validationContext']['contextHash'])
        observed = next(row for row in records if row['id'] == 'exam')
        # The same unchanged examiner can have the same content digest. Its
        # actual invocation/report run must nevertheless be this fresh run.
        self.assertNotEqual(observed['privateReport']['runId'], fork['privateReport']['runId'])
        self.assertEqual(observed['engineInvocationObservation']['evaluationRun'], answer['validationId'])
        self.assertEqual(records[-1]['validationId'], answer['validationId'])
        self.assertEqual(records[-1]['captureObservation']['returnedContext'], context)
        self.assertEqual(observed['executedVerifierSet'],
                         next(row for row in answer['results'] if row['id'] == 'exam')['executedVerifierSet'])

    def test_empty_revalidation_retains_its_own_context_and_full_completion(self) -> None:
        world = self._candidate()
        answer = self.evaluation.revalidator.revalidate(world.alias)
        retained = self._retained(world, answer)
        context, source, records = self._effective(world)
        self.assertEqual(source, 'revalidation:' + answer['validationId'])
        self.assertEqual(context, retained['context'])
        self.assertEqual(records, retained['results'])
        self.assertEqual(records[-1]['validationId'], answer['validationId'])
        self.assertEqual(records[-1]['captureObservation']['returnedContext'], context)
        self.assertNotEqual(context['contextHash'], world.evidence['validationContext']['contextHash'])

    def test_a_failed_revalidation_does_not_speak(self) -> None:
        # Original v5 D2 supersedes this case's old fallback expectation. A
        # genuine newer required FAIL must refuse; it cannot expose old PASS.
        world = self._candidate()
        earlier = self.evaluation.revalidator.revalidate(world.alias)
        self.assertEqual(earlier['outcome'], 'PASS')
        self._effective(world)
        self._policy(protected=['state.txt'])
        answer = self.evaluation.revalidator.revalidate(world.alias)
        retained = self._retained(world, answer)
        self.assertEqual(answer['evaluationState'], 'COMPLETED')
        self.assertEqual(answer['outcome'], 'FAIL')
        failed = next(row for row in retained['results'] if row['id'] == 'protected-paths')
        self.assertEqual(failed['status'], 'FAIL')
        self.assertTrue(failed['touched'])
        self.assertEqual(retained['results'][-1]['id'], 'evaluation-complete')
        with self.assertRaises(WorldlineError) as caught:
            self._effective(world)
        self.assertEqual(caught.exception.code, 'EVIDENCE_FAIL_TERMINAL')
        # Refusal does not erase either actual history row or change its head.
        history = self.evaluation.terminal.snapshot(world.instance_id)['history']
        self.assertEqual([row['validationId'] for row in history],
                         [earlier['validationId'], answer['validationId']])

    def test_a_revalidation_for_different_content_does_not_speak(self) -> None:
        # An actual different world has its own journal partition. No invalid
        # same-world row is inserted and no backwards content filter is used.
        self._private_policy()
        world = self._candidate()
        other = self._candidate('candidate-other')
        self.assertNotEqual(world.content_id, other.content_id)
        answer = self.evaluation.revalidator.revalidate(other.alias)
        self._retained(other, answer)
        context, source, _records = self._effective(world)
        self.assertEqual(source, 'finalization')
        self.assertEqual(context['candidate']['instanceId'], world.instance_id)
        self.assertEqual(self.evaluation.terminal.snapshot(world.instance_id)['history'], [])

    def test_a_revalidation_missing_execution_facts_cannot_borrow_them(self) -> None:
        self._private_policy()
        world = self._candidate()
        fork = next(row for row in world.evidence['checks'] if row['id'] == 'exam')
        self.assertIsNotNone(fork['executedVerifierSet'])
        # An ordinary declared process really runs. No verifier is declared,
        # so its observed exit is not complete promotion evidence for exam.
        self._policy(checks=[{'id': 'exam', 'kind': 'tests', 'argv': ['/usr/bin/true'],
                             'required': True, 'format': 'exit'}])
        answer = self.evaluation.revalidator.revalidate(world.alias)
        retained = self._retained(world, answer)
        self.assertEqual(answer['evaluationState'], 'ERROR')
        self.assertIsNone(answer['outcome'])
        self.assertEqual(answer['results'], [])
        missing = next(row for row in retained['partialResults'] if row['id'] == 'exam')
        self.assertEqual(missing['status'], 'PASS')
        self.assertIsNone(missing['executedVerifierSet'])
        self.assertEqual(missing['supervision']['kind'], 'SUPERVISED')
        self.assertNotIn('evaluation-complete', [row['id'] for row in retained['partialResults']])
        with self.assertRaises(WorldlineError) as caught:
            self._effective(world)
        self.assertEqual(caught.exception.code, 'EVALUATION_INCOMPLETE')

    def test_wrong_content_is_refused_before_a_same_world_intent_is_created(self) -> None:
        world = self._candidate()
        parent = self.store.world(world.parent_instance)
        self.assertNotEqual(world.content_id, parent.content_id)
        manifests = {root['root_key']: Manifest.load(
            Path(world.payload_path) / 'manifests' / (root['root_key'] + '.json'), self.core)
            for root in self.store.roots()}
        bases = {root['root_key']: Manifest.capture(
            Path(world.base_payload_path) / root['root_key'], logical_root=bytes(root['path']),
            root_key=root['root_key'], kind=root['kind'], core=self.core)
            for root in self.store.roots()}
        before = self.evaluation.terminal.snapshot(world.instance_id)
        with self.assertRaises(WorldlineError) as caught:
            self.evaluation.revalidator.evaluate_retained(
                terminal=self.evaluation.terminal, content_identity=parent.content_id,
                source_dir=Path(world.payload_path),
                subject={'instanceId': world.instance_id, 'alias': world.alias,
                         'baseRoot': world.base_root, 'rootSetHash': world.root_set_hash,
                         'missionHash': world.mission_hash},
                prime_at_fork={'instanceId': parent.instance_id, 'contentId': parent.content_id,
                               'generation': parent.instance_id},
                protected_delta=lambda: Delta.compute_all(bases, manifests, self.core),
                source='revalidation', declared=manifests)
        self.assertEqual(caught.exception.code, 'EVALUATION_CONTENT_BINDING_MISMATCH')
        self.assertEqual(self.evaluation.terminal.snapshot(world.instance_id), before)

    def test_a_new_pending_attempt_cannot_borrow_the_previous_pass(self) -> None:
        world = self._candidate()
        answer = self.evaluation.revalidator.revalidate(world.alias)
        self.assertEqual(answer['outcome'], 'PASS')
        self._effective(world)
        pending = self.evaluation.pending.begin(world.instance_id, world.content_id,
                                                self._requirement()['requirementHash'])
        with self.assertRaises(WorldlineError) as caught:
            self._effective(world)
        self.assertEqual(caught.exception.code, 'EVALUATION_INCOMPLETE')
        history = self.evaluation.terminal.snapshot(world.instance_id)['history']
        self.assertEqual(history[-1]['validationId'], pending.run)
        self.assertEqual(history[-1]['evaluationState'], 'PENDING')
        self.assertEqual(history[-1]['results'], [])
        self.assertEqual(history[0]['validationId'], answer['validationId'])

    def test_actual_private_examiner_is_staged_from_current_prime(self) -> None:
        self._private_policy()
        world = self._candidate()
        fork = next(row for row in world.evidence['checks'] if row['id'] == 'exam')
        # A legitimate owner update changes current requirements after the
        # fork. Keep the frozen candidate unchanged; observe which bytes run.
        current_examiner = EXAMINER + '\n# current PRIME examiner revision\n'
        (self._primary() / 'exam.py').write_text(current_examiner, encoding='utf-8')
        actual_digest = hashlib.sha256((self._primary() / 'exam.py').read_bytes()).hexdigest()
        answer = self.evaluation.revalidator.revalidate(world.alias)
        retained = self._retained(world, answer)
        rows = retained['results'] if retained['evaluationState'] == 'COMPLETED' else retained['partialResults']
        observed = next(row for row in rows if row['id'] == 'exam')
        self.assertEqual(observed['status'], 'PASS')
        self.assertIs(observed['executedVerifierSet']['stable'], True)
        member = next(item for item in observed['executedVerifierSet']['members'] if item['path'] == 'exam.py')
        self.assertEqual(member['sha256'], actual_digest)
        self.assertNotEqual(observed['executedVerifierSet']['identity'], fork['executedVerifierSet']['identity'])
        self.assertEqual(observed['engineInvocationObservation']['evaluationRun'], answer['validationId'])
        self.assertEqual(observed['privateReport']['runId'], observed['evaluatorBoundary']['runId'])
        # The old candidate verifier no longer matches current requirements.
        # Running the current examiner does not make that mismatch disappear.
        self.assertTrue(answer['verifiersModifiedByCandidate'])
        self.assertEqual(answer['evaluationState'], 'COMPLETED')
        self.assertEqual(answer['outcome'], 'FAIL')
        with self.assertRaises(WorldlineError) as caught:
            self._effective(world)
        self.assertEqual(caught.exception.code, 'EVIDENCE_FAIL_TERMINAL')


class RevalidationStoresExecutionFacts(unittest.TestCase):
    """The stored revalidation entry keeps the execution-identity fields, not just id/status."""

    def test_the_projection_preserves_the_execution_fields(self) -> None:
        source = (REPO / "runtime/worldline/revalidate.py").read_text(encoding="utf-8")
        # The stored results projection names each field promotion reads.
        self.assertIn('"executedVerifierSet": r.get("executedVerifierSet")', source)
        self.assertIn('"executionBinding": r.get("executionBinding")', source)
        self.assertIn('"evaluation": r.get("evaluation")', source)

    def test_the_examiner_is_staged_from_current_prime_not_the_candidate(self) -> None:
        # F6: the trusted evaluator snapshot is each registered root's current PRIME content,
        # resolved through the store's live mapping (1.7.0; before, the realpath of the root's
        # own link), passed as verifier_sources -- never the overlay lower (the candidate payload).
        source = (REPO / "runtime/worldline/revalidate.py").read_text(encoding="utf-8")
        self.assertIn("evaluator_sources = {r[\"root_key\"]: Path(os.fsdecode(self.paths.root_source(r)))", source)
        self.assertIn("verifier_sources=evaluator_sources", source)
        # And it is NOT read from r.lower anywhere in _evaluate.
        evaluate = source[source.index("def _evaluate"):]
        self.assertNotIn("r.lower for r in overlays", evaluate)


if __name__ == "__main__":
    unittest.main()
