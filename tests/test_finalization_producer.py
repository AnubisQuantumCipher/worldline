"""Owned producer/recovery regressions; ordinary execution is not formal proof."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from worldline.admission import AdmissionAuthority, Gate, Ledger
from worldline.agents.generic import GenericAdapter
from worldline.config import GenericAgentCommand, GlobalConfig
from worldline.core import Core, hash_id
from worldline.evaluation_authority import read
from worldline.finalize import Finalizer
from worldline.linux.namespaces import BubblewrapSandbox
from worldline.linux.systemd import SystemdAdapter
from worldline.manifest import Manifest
from worldline.model import World, WorldState
from worldline.paths import WorldlinePaths
from worldline.project import ProjectConfig
from worldline.roots import RootManager
from worldline.runner import AgentRunner, _AgentAcquisition
from worldline.store import StateStore
from worldline.validation import current_requirements


class AcquisitionFailureTests(unittest.TestCase):
    def test_actual_wait_retention_refusal_still_joins_and_cleans_owned_resources(self):
        # Only cleanup transport is stubbed here. This test makes no native,
        # manager-supervision, custody or promotion claim from those stubs.
        process = subprocess.Popen(['/usr/bin/python3', '-c',
            "import sys; sys.stdout.buffer.write(b'actual-out'); sys.stderr.buffer.write(b'actual-err')"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.addCleanup(process.stdout.close)
        self.addCleanup(process.stderr.close)
        refusal = RuntimeError('wait observation persistence refused')
        observations, cleanup, data = [], [], {}
        def observe(**value):
            observations.append(value)
            if value['kind'] == 'agent-launcher-wait':
                raise refusal
        def outcome(unit, code, **kwargs):
            cleanup.append(('manager', code))
            return {'kind': 'TEST_CLEANUP_TRANSPORT_ONLY'}
        owner = _AgentAcquisition(SimpleNamespace(systemd=SimpleNamespace(outcome=outcome)),
                                  SimpleNamespace(invocation_raw=observe), 'owned-subject')
        owner.unit = SimpleNamespace(launcher=process, unit='owned-test-only')
        owner.guard = SimpleNamespace(release=lambda: cleanup.append('guard'))
        owner.proxy = SimpleNamespace(stop=lambda: cleanup.append('proxy'))
        owner.proxy_started = True
        for name, stream in (('stdout', process.stdout), ('stderr', process.stderr)):
            thread = threading.Thread(target=lambda name=name, stream=stream: data.update({name: stream.read()}))
            thread.start()
            owner.threads.append(thread)
        try:
            owner.wait()
        except RuntimeError as actual:
            self.assertIs(actual, refusal)
            with self.assertRaises(RuntimeError) as caught:
                owner.finish(actual)
            self.assertIs(caught.exception, refusal)
        else:
            self.fail('the injected persistence refusal must propagate')
        self.assertTrue(owner.wait_observed)
        self.assertEqual(owner.exit_code, process.returncode)
        self.assertTrue(all(not thread.is_alive() for thread in owner.threads))
        self.assertEqual(data, {'stdout': b'actual-out', 'stderr': b'actual-err'})
        self.assertEqual(cleanup, [('manager', process.returncode), 'proxy', 'guard'])
        self.assertTrue(observations[0]['observed']['waitReturnObserved'])


class DefaultProducerRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='worldline-finalization-producer-')
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        env = {key: str(root / directory) for key, directory in (
            ('HOME', 'home'), ('XDG_DATA_HOME', 'data'), ('XDG_STATE_HOME', 'state'),
            ('XDG_CONFIG_HOME', 'config'), ('XDG_RUNTIME_DIR', 'runtime'))}
        for value in env.values():
            Path(value).mkdir(mode=0o700, parents=True)
        self.paths = WorldlinePaths.from_environment(env)
        self.core = Core.shared()
        self.store = StateStore(self.paths, self.core)
        self.addCleanup(self._close_store)
        self.config = GlobalConfig.default(self.paths)
        self.work = root / 'work'
        self.work.mkdir()
        (self.work / 'state.txt').write_text('prime', encoding='utf-8')
        RootManager(self.paths, self.store, core=self.core, toolchains=()).register([self.work], confirmed=True)
        self._attach_runner()

    def _close_store(self):
        if self.store is not None:
            self.store.close()
            self.store = None

    def _attach_runner(self):
        self.runner = AgentRunner(self.paths, self.store, self.config,
            BubblewrapSandbox(self.paths), SystemdAdapter(),
            Gate(AdmissionAuthority(Ledger(self.paths.runtime), self.config.admission_floors,
                paths={'data': self.paths.data, 'state': self.paths.state}), self.config.resource_policy),
            core=self.core)

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
        self.assertIsNone(project.source_sha256)
        self.assertEqual(project.checks, ())
        script = "from pathlib import Path; Path('state.txt').write_text('candidate', encoding='utf-8')"
        command = GenericAgentCommand(name='owned-recovery', argv=('/usr/bin/python3', '-c', script),
            credential_mounts=(), event_format='jsonl', network_hosts=())
        return world, GenericAdapter(command), project

    def test_published_unlinked_world_cannot_acknowledge_before_readonly_recovery(self):
        world, adapter, project = self._world_and_command()
        refusal = OSError('injected original readonly operation failure')
        with patch.object(Finalizer, '_make_readonly', side_effect=refusal):
            with self.assertRaises(OSError) as caught:
                self.runner.run(world.alias, adapter, world.cause, project, timeout=15)
            self.assertIs(caught.exception, refusal)
            journal = self.store.evaluation_finalization
            published = self.store.world(world.instance_id)
            self.assertEqual(published.state, WorldState.VALID)
            self.assertTrue(journal.publication_pending(world.instance_id))
            with self.assertRaises(OSError):
                journal.acknowledge(self.store, world.instance_id)
            self.assertTrue(journal.publication_pending(world.instance_id))
        recovered = self.runner.run(world.alias, adapter, world.cause, project, timeout=15)
        self.assertEqual(recovered.record(), published.record())
        self.assertFalse(journal.publication_pending(world.instance_id))
        Finalizer._verify_readonly(Path(recovered.payload_path))
        self.assertEqual(journal.retained(world.instance_id)[1].value.content,
                         recovered.content_id.encode('utf-8'))

    def test_default_journals_reopen_and_read_finalization_without_rerunning_agent(self):
        world, adapter, project = self._world_and_command()
        finalized = self.runner.run(world.alias, adapter, world.cause, project, timeout=15)
        before = self.store.evaluation_finalization.retained(world.instance_id)
        self._close_store()
        self.store = StateStore(self.paths, self.core)
        self._attach_runner()
        self.assertIsNotNone(self.store.evaluation_terminal)
        self.assertIsNotNone(self.store.evaluation_finalization)
        self.assertEqual(self.store.evaluation_finalization.retained(world.instance_id), before)
        requirement = current_requirements(self.store, self.config, self.core)
        selected = read(self.store, self.store.world(world.instance_id), requirement['requirementHash'], core=self.core)
        self.assertEqual(selected.source, 'finalization')
        self.assertEqual(selected.results[-1]['id'], 'evaluation-complete')
        self.assertEqual(selected.raw.value.finalization_state, 'COMPLETED')
        self.assertEqual(selected.raw.value.finalization_outcome, 'PASS')
        self.assertEqual(self.store.evaluation_terminal.snapshot(finalized.instance_id)['history'], [])

    def test_failed_primary_is_retained_as_completed_failure_not_materialization_error(self):
        world, _adapter, project = self._world_and_command()
        command = GenericAgentCommand(name='failed-primary',
            argv=('/usr/bin/python3', '-c', 'import sys; sys.exit(7)'),
            credential_mounts=(), event_format='jsonl', network_hosts=())
        finalized = self.runner.run(
            world.alias, GenericAdapter(command), world.cause, project, timeout=15)
        self.assertEqual(finalized.state, WorldState.DEGRADED)
        agent = next(row for row in finalized.evidence['checks'] if row['id'] == 'agent')
        self.assertEqual(agent['exitCode'], 7)
        self.assertEqual(agent['evaluation']['executionStatus'], 'COMPLETED')
        self.assertEqual(agent['evaluation']['evaluationOutcome'], 'FAIL')
        self.assertNotIn('materializationError', finalized.evidence)
        _start, sealed, _events = self.store.evaluation_finalization.retained(world.instance_id)
        self.assertEqual(sealed.finalization_state, 'COMPLETED')
        self.assertEqual(sealed.finalization_outcome, 'FAIL')


if __name__ == '__main__':
    unittest.main()
