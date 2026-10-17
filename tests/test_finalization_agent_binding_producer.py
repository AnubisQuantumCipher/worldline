"""Actual ordinary producer/revalidation/reopen source controls, UNEXECUTED.

This uses the existing real AgentRunner, Bubblewrap, Systemd, StateStore,
finalization/terminal journals and native decisions. It is NOT protected
startup/custody coverage. Do not execute outside its separately admitted frame.
"""
from collections.abc import Mapping
from copy import deepcopy
import os
from pathlib import Path
import unittest
from test_finalization_producer import DefaultProducerRecoveryTests as _Producer
from worldline.agents.generic import GenericAdapter
from worldline.config import GenericAgentCommand
from worldline.core import hash_id
from worldline.manifest import Manifest
from worldline.model import World
from worldline.project import ProjectConfig
from worldline.store import StateStore
from worldline.canonical import atomic_write_json
from worldline.evaluation_authority import read, read_material
from worldline.evaluation_context import agent_context_pair
from worldline.finalize import runner_agent_record
from worldline.revalidate import Revalidator
from worldline.validation import current_requirements

class AgentBindingOrdinaryProducerControls(_Producer):
    def _world_and_command(self):
        root = self.store.roots()[0]
        logical = bytes(root['path'])
        source = Path(os.fsdecode(self.paths.root_source(root)))
        base = self.paths.worlds / 'recovery-fixture' / 'base'
        manifest = Manifest.capture(source, logical_root=logical, root_key=root['root_key'],
                                    kind=root['kind'], core=self.core)
        Manifest.materialize(manifest, source, base / root['root_key'], core=self.core)
        parent = self.store.prime()
        world = World.create(alias='recovery-fixture', parent_instance=parent.instance_id,
            parent_content=parent.content_id, cause='owned finalization recovery', actor='fixture',
            payload_path=self.paths.worlds / 'recovery-fixture' / 'payload', base_payload_path=base,
            base_root=Manifest.root_set_hash([manifest], self.core), root_set_hash=parent.root_set_hash,
            mission_hash=hash_id(self.core.hash_bytes(b'owned-finalization-recovery')))
        self.store.insert_world(world)
        project = ProjectConfig.load(source, self.store)
        self.assertIsNotNone(project.source_sha256)
        self.assertEqual(project.checks, ())
        script = "from pathlib import Path; Path('state.txt').write_text('candidate', encoding='utf-8')"
        command = GenericAgentCommand(name='owned-recovery', argv=('/usr/bin/python3', '-c', script),
            credential_mounts=(), event_format='jsonl', network_hosts=())
        return world, GenericAdapter(command), project

    def test_actual_finalization_revalidation_reopen_retains_independent_evidence(self):
        # Same original fixture/helper, with an explicit empty policy so this
        # is an accepted revalidation instead of missing-policy evidence.
        atomic_write_json(self.work / '.worldline.json',
            {'schemaVersion': 1, 'generated': [], 'checks': [], 'protected': [], 'services': []})
        world, adapter, project = self._world_and_command()
        finalized = self.runner.run(world.alias, adapter, world.cause, project, timeout=15)
        original_evidence = deepcopy(finalized.evidence)
        original_content = finalized.content_id
        retained = self.store.evaluation_finalization.retained(world.instance_id)
        self.assertIsNotNone(retained[1])
        requirement = current_requirements(self.store, self.config, self.core)
        first = read(self.store, finalized, requirement['requirementHash'], core=self.core)
        self.assertEqual(first.source, 'finalization')
        original_agent, _legacy = runner_agent_record(next(item for item in original_evidence['checks']
            if isinstance(item, Mapping) and item.get('id') == 'agent'))
        first_pair = agent_context_pair(first, finalized, original_agent)
        self.assertEqual(first_pair[0], first_pair[1])
        revalidator = Revalidator(self.paths, self.store, self.config,
            self.runner.sandbox, self.runner.checks, core=self.core)
        entry = revalidator.revalidate(world.instance_id)
        self.assertEqual(entry['outcome'], 'PASS')
        current = self.store.world(world.instance_id)
        self.assertEqual(current.evidence, original_evidence)
        self.assertEqual(current.content_id, original_content)
        selected = read(self.store, current, requirement['requirementHash'], core=self.core)
        self.assertTrue(selected.source.startswith('revalidation:'))
        self.assertEqual(selected.authority_material.finalization, retained)
        pair = agent_context_pair(selected, current, original_agent)
        self.assertEqual(pair[0], pair[1])
        self.assertEqual(pair, first_pair)
        # Recovery replays full native producer/classification/history from
        # actual retained material, without running the actor or check again.
        replay = read_material(current, requirement['requirementHash'],
            selected.authority_material, prepared=selected.cursor, core=self.core)
        self.assertEqual(replay.cursor, selected.cursor)
        self.assertEqual(replay.results, selected.results)
        self.assertEqual(replay.authority_material, selected.authority_material)
        self.assertEqual(agent_context_pair(replay, current, original_agent), pair)
        terminal_before = self.store.evaluation_terminal.authority_material_full(world.instance_id)
        self._close_store()
        self.store = StateStore(self.paths, self.core)
        self._attach_runner()
        reopened = self.store.world(world.instance_id)
        self.assertEqual(self.store.evaluation_finalization.retained(world.instance_id), retained)
        self.assertEqual(self.store.evaluation_terminal.authority_material_full(world.instance_id), terminal_before)
        after = read(self.store, reopened, requirement['requirementHash'],
            prepared=selected.cursor, core=self.core)
        self.assertEqual(after.cursor, selected.cursor)
        self.assertEqual(agent_context_pair(after, reopened, original_agent), pair)
        # Modify only the caller's current object, never retained source/store.
        # Native refusal for these distinct tuples is covered separately by
        # the real native-context suite, not claimed from this Python assertion.
        changed = deepcopy(reopened)
        changed.evidence['agent-binding-control'] = 'different-current-object'
        mismatch = agent_context_pair(after, changed, original_agent)
        self.assertNotEqual(mismatch[0], mismatch[1])
        self.assertEqual(self.store.world(world.instance_id).evidence, original_evidence)


def load_tests(loader, _standard_tests, _pattern):
    return unittest.TestSuite(AgentBindingOrdinaryProducerControls(name)
        for name in AgentBindingOrdinaryProducerControls.__dict__ if name.startswith('test_'))
