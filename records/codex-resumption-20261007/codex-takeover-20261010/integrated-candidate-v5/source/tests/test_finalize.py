from __future__ import annotations

import os
from pathlib import Path
import stat
import tempfile
import unittest

from owned_evaluation_support import OwnedTransactionEvaluation
from worldline.agents.generic import GenericAdapter
from worldline.config import GenericAgentCommand
from worldline.core import Core, hash_id
from worldline.admission import AdmissionAuthority, Floors, Gate, Ledger, ResourcePolicy
from worldline.linux.systemd import SystemdAdapter
from worldline.manifest import Manifest
from worldline.model import World, WorldState
from worldline.paths import WorldlinePaths
from worldline.project import ProjectConfig, ServiceSpec
from worldline.roots import RootManager
from worldline.services import ServiceManager


class FinalizerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-finalize-")
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
        self.work = root / "work"
        self.work.mkdir()
        (self.work / "value.txt").write_text("prime", encoding="utf-8")
        RootManager(self.paths, self.store, core=self.core, toolchains=()).register([self.work], confirmed=True)
        self.sandbox = self.evaluation.sandbox

    def tearDown(self) -> None:
        self.evaluation.close()
        self.temporary.cleanup()

    def test_overlay_is_materialized_hashed_and_made_readonly(self) -> None:
        root = self.store.roots()[0]
        root_key = root["root_key"]
        logical = bytes(root["path"])
        current_source = Path(os.fsdecode(os.path.realpath(logical)))
        base = self.paths.worlds / "fixture" / "base"
        manifest = Manifest.capture(
            current_source,
            logical_root=logical,
            root_key=root_key,
            kind=root["kind"],
            core=self.core,
        )
        Manifest.materialize(manifest, current_source, base / root_key, core=self.core)
        (base / "manifests").mkdir()
        manifest.save(base / "manifests" / f"{root_key}.json")
        parent = self.store.prime()
        world = World.create(
            alias="alpha",
            parent_instance=parent.instance_id,
            parent_content=parent.content_id,
            cause="fixture change",
            actor="fixture",
            payload_path=self.paths.worlds / "fixture" / "payload",
            base_payload_path=base,
            base_root=Manifest.root_set_hash([manifest], self.core),
            root_set_hash=parent.root_set_hash,
            mission_hash=hash_id(self.core.hash_bytes(b"fixture")),
        )
        self.store.insert_world(world)
        # Preserve the original no-policy/agent-only accepted case. The actual
        # AgentRunner obtains supervision and runs the real finalization producer;
        # this fixture supplies no result/context/completion or custody assertion.
        primary = next(item for item in self.store.roots() if item['primary_root'])
        agent_project = ProjectConfig.load(
            Path(os.fsdecode(self.paths.root_source(primary))), self.store)
        self.assertIsNone(agent_project.source_sha256)
        self.assertEqual(agent_project.checks, ())
        script = f"from pathlib import Path; Path({str(Path(os.fsdecode(logical)) / 'value.txt')!r}).write_text('candidate', encoding='utf-8')"
        command = GenericAgentCommand(
            name="ordinary-finalization", argv=("/usr/bin/python3", "-c", script),
            credential_mounts=(), event_format="jsonl", network_hosts=())
        finalized = self.evaluation.runner.run(
            world.alias, GenericAdapter(command), world.cause, agent_project, timeout=15)
        agent = next(row for row in finalized.evidence['checks'] if row['id'] == 'agent')
        self.assertEqual(agent['exitCode'], 0)
        self.assertEqual(agent['origin'], 'agent')
        self.assertEqual(agent['supervision']['kind'], 'SUPERVISED')
        self.assertIs(agent['resources']['ceilingFired'], False)
        self.assertEqual(finalized.evidence['checks'][-1]['id'], 'evaluation-complete')
        # This is finalization-only: an added revalidation must not manufacture
        # the passing evidence for the old materialization/service positive.
        self.assertEqual(self.evaluation.terminal.snapshot(finalized.instance_id)['history'], [])
        payload_file = Path(finalized.payload_path) / root_key / "value.txt"
        self.assertEqual(finalized.state, WorldState.VALID)
        self.assertEqual(payload_file.read_text(encoding="utf-8"), "candidate")
        self.assertNotIn("", [item["pathB64"] for item in finalized.delta["files"]])
        self.assertFalse(stat.S_IMODE(payload_file.stat().st_mode) & 0o222)
        self.assertEqual((self.work / "value.txt").read_text(encoding="utf-8"), "prime")
        self.assertEqual((base / root_key / "value.txt").read_text(encoding="utf-8"), "prime")

        services = ServiceManager(
            self.paths,
            self.store,
            self.sandbox,
            SystemdAdapter(),
            Gate(AdmissionAuthority(Ledger(self.paths.runtime), Floors()), ResourcePolicy.from_mapping({})),
        )
        project = ProjectConfig(
            generated=(),
            checks=(),
            services=(
                ServiceSpec(
                    id="fixture-service",
                    argv=("/usr/bin/sleep", "5"),
                    cwd=".",
                    env={},
                    health_argv=("/usr/bin/true",),
                    restart="never",
                ),
            ),
        )
        started = services.start_declared(finalized, project)
        self.assertEqual(started[0]["health"]["status"], "PASS")
        services.stop_world(finalized.instance_id)


if __name__ == "__main__":
    unittest.main()
