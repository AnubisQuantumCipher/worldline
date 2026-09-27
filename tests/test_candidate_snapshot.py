from __future__ import annotations

from dataclasses import replace
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from worldline.core import Core, hash_id
from worldline.errors import WorldlineError
from worldline.finalize import Finalizer
from worldline.linux.namespaces import BubblewrapSandbox, SandboxSpec
from worldline.manifest import Manifest
from worldline.model import World, WorldState
from worldline.paths import WorldlinePaths
from worldline.project import CheckSpec, ProjectConfig
from worldline.roots import RootManager
from worldline.runner import AgentRunner
from worldline.store import StateStore


def check(identifier: str, profile: str) -> CheckSpec:
    return CheckSpec(identifier, "tests", ("/usr/bin/true",), None, True,
                     "junit" if profile == "private-evaluator-v1" else "exit",
                     None, (), (), profile)


class EvaluationPhaseOrder(unittest.TestCase):
    def test_legacy_builds_precede_private_evaluation_without_reordering(self) -> None:
        build, exam = check("build", "legacy"), check("exam", "private-evaluator-v1")
        project = ProjectConfig(generated=(), checks=(build, exam), services=())
        self.assertEqual(AgentRunner._evaluation_phases(project), ([build], [exam]))

    def test_legacy_writer_after_private_evaluation_is_refused(self) -> None:
        project = ProjectConfig(generated=(), checks=(check("exam", "private-evaluator-v1"),
                                check("late-build", "legacy")), services=())
        with self.assertRaises(WorldlineError) as raised:
            AgentRunner._evaluation_phases(project)
        self.assertEqual(raised.exception.code, "CHECK_PROFILE_ORDER_INVALID")


class CandidateSnapshotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-candidate-snapshot-")
        root = Path(self.temporary.name)
        environment = {"HOME": str(root / "home"), "XDG_DATA_HOME": str(root / "data"),
                       "XDG_STATE_HOME": str(root / "state"), "XDG_CONFIG_HOME": str(root / "config"),
                       "XDG_RUNTIME_DIR": str(root / "runtime")}
        for value in environment.values():
            Path(value).mkdir(mode=0o700, parents=True)
        self.paths = WorldlinePaths.from_environment(environment)
        self.core = Core.shared()
        self.store = StateStore(self.paths, self.core)
        self.work = root / "work"
        self.work.mkdir()
        (self.work / "source.txt").write_text("prime", encoding="utf-8")
        RootManager(self.paths, self.store, core=self.core, toolchains=()).register([self.work], confirmed=True)
        self.sandbox = BubblewrapSandbox(self.paths)
        self.finalizer = Finalizer(self.paths, self.store, self.sandbox, core=self.core)
        registered = self.store.roots()[0]
        self.key = registered["root_key"]
        self.logical = Path(os.fsdecode(bytes(registered["path"])))
        source = self.logical.resolve()
        base = self.paths.worlds / "fixture" / "base"
        manifest = Manifest.capture(source, logical_root=bytes(registered["path"]),
                                    root_key=self.key, kind=registered["kind"], core=self.core)
        Manifest.materialize(manifest, source, base / self.key, core=self.core)
        (base / "manifests").mkdir()
        manifest.save(base / "manifests" / f"{self.key}.json")
        parent = self.store.prime()
        self.world = World.create(
            alias="candidate", parent_instance=parent.instance_id, parent_content=parent.content_id,
            cause="snapshot test", actor="fixture", payload_path=self.paths.worlds / "fixture" / "payload",
            base_payload_path=base, base_root=Manifest.root_set_hash([manifest], self.core),
            root_set_hash=parent.root_set_hash, mission_hash=hash_id(self.core.hash_bytes(b"snapshot test")),
        )
        self.store.insert_world(self.world)
        self.overlays = self.sandbox.overlay_roots(self.world.instance_id,
                                                  [(self.key, base / self.key, self.logical)])
        self.run_in(self.overlays, "from pathlib import Path\nPath('source.txt').write_text('candidate')\n"
                                  "Path('generated.bin').write_text('built before private checks')\n")

    def tearDown(self) -> None:
        self.store.close()
        self.temporary.cleanup()

    def run_in(self, overlays, script: str) -> None:
        runtime = self.paths.overlays / self.world.instance_id / "fixture-runtime"
        process = self.sandbox.launch_world(SandboxSpec(
            instance_id=self.world.instance_id, argv=("/usr/bin/python3", "-c", script),
            cwd=self.logical, environment={"PATH": "/usr/bin"}, roots=tuple(overlays), runtime=runtime,
        ))
        _stdout, stderr = process.process.communicate(timeout=15)
        self.assertEqual(process.process.returncode, 0, stderr.decode("utf-8", "replace"))

    def result(self, snapshot=None) -> dict:
        value = {"id": "exam", "kind": "tests", "required": True, "format": "junit",
                 "profile": "private-evaluator-v1", "status": "FAIL", "exitCode": 1,
                 "origin": "supervisor", "resultChannel": {"accepted": True}}
        if snapshot is not None:
            value["candidateSnapshot"] = snapshot.binding()
        return value

    def finalize(self, *, snapshot=None, results=(), required=()):
        return self.finalizer.finalize(
            self.world.instance_id, self.overlays, candidate_snapshot=snapshot,
            check_results=results, required_checks=required,
            agent_manifest={"adapter": "fixture", "generatedClassifiers": [{"root": self.key, "glob": "*.bin"}]},
        )

    def test_failing_private_check_writes_are_not_promoted(self) -> None:
        snapshot = self.finalizer.capture_candidate(self.world.instance_id, self.overlays)
        scratch = self.finalizer.candidate_overlays(snapshot)
        # The ordinary build output exists for the private check, and subsequent private
        # checks can share scratch output. Neither scratch output nor rewritten source is
        # selected as the final candidate after the failing examination.
        self.run_in(scratch, "from pathlib import Path\n"
                    "assert Path('generated.bin').read_text() == 'built before private checks'\n"
                    "Path('source.txt').write_text('scratch source')\n"
                    "Path('generated.bin').write_text('scratch build')\n"
                    "Path('check-only.txt').write_text('scratch')\n")
        self.run_in(scratch, "from pathlib import Path\nassert Path('check-only.txt').read_text() == 'scratch'\n")
        self.run_in(self.overlays, "from pathlib import Path\nPath('source.txt').write_text('late agent change')\n")
        finalized = self.finalize(snapshot=snapshot, results=[self.result(snapshot)], required=["exam"])
        payload = Path(finalized.payload_path) / self.key
        self.assertEqual(finalized.state, WorldState.DEGRADED)
        self.assertEqual((payload / "source.txt").read_text(), "candidate")
        self.assertEqual((payload / "generated.bin").read_text(), "built before private checks")
        self.assertFalse((payload / "check-only.txt").exists())
        self.assertEqual(finalized.evidence["metrics"]["candidateSnapshot"], snapshot.binding())
        self.assertEqual(finalized.evidence["checks"][0]["candidateSnapshot"], snapshot.binding())
        self.assertEqual(finalized.evidence["metrics"]["generatedClassifiers"],
                         [{"root": self.key, "glob": "*.bin"}])

    def test_legacy_check_outputs_remain_in_the_payload_with_a_nonclaim(self) -> None:
        self.run_in(self.overlays, "from pathlib import Path\nPath('legacy-output.txt').write_text('kept')\n")
        result = {"id": "legacy", "format": "exit", "profile": "legacy", "status": "PASS",
                  "exitCode": 0, "origin": "supervisor", "resultChannel": {"accepted": True}}
        finalized = self.finalize(results=[result], required=["legacy"])
        self.assertEqual(finalized.state, WorldState.VALID)
        self.assertEqual((Path(finalized.payload_path) / self.key / "legacy-output.txt").read_text(), "kept")
        self.assertIsNone(finalized.evidence["metrics"]["candidateSnapshot"])
        self.assertTrue(finalized.evidence["metrics"]["evaluationWorkspace"]["nonClaims"])

    def test_private_result_without_a_snapshot_is_refused(self) -> None:
        with self.assertRaises(WorldlineError) as raised:
            self.finalize(results=[self.result()], required=["exam"])
        self.assertEqual(raised.exception.code, "CANDIDATE_SNAPSHOT_MISSING")

    def test_legacy_materialization_failure_records_a_dead_world(self) -> None:
        with patch.object(self.finalizer, "_capture_candidate",
                          side_effect=WorldlineError("MATERIALIZATION_FAILED", "fixture failure")):
            with self.assertRaises(WorldlineError) as raised:
                self.finalize()
        self.assertEqual(raised.exception.code, "MATERIALIZATION_FAILED")
        world = self.store.world(self.world.instance_id)
        self.assertEqual(world.state, WorldState.DEAD)
        self.assertEqual(world.evidence["supervision"]["code"], "MATERIALIZATION_FAILED")

    def test_result_naming_another_snapshot_is_refused(self) -> None:
        snapshot = self.finalizer.capture_candidate(self.world.instance_id, self.overlays)
        result = self.result(snapshot)
        result["candidateSnapshot"]["rootSetHash"] = "different"
        with self.assertRaises(WorldlineError) as raised:
            self.finalize(snapshot=snapshot, results=[result], required=["exam"])
        self.assertEqual(raised.exception.code, "CANDIDATE_SNAPSHOT_MISMATCH")
        self.assertEqual(self.store.world(self.world.instance_id).state, WorldState.DEAD)

    def test_snapshot_for_another_world_is_refused(self) -> None:
        snapshot = self.finalizer.capture_candidate(self.world.instance_id, self.overlays)
        with self.assertRaises(WorldlineError) as raised:
            self.finalize(snapshot=replace(snapshot, world_instance="another-world"))
        self.assertEqual(raised.exception.code, "CANDIDATE_SNAPSHOT_MISMATCH")

    def test_snapshot_permission_changes_are_refused(self) -> None:
        snapshot = self.finalizer.capture_candidate(self.world.instance_id, self.overlays)
        source = snapshot.directory / self.key / "source.txt"
        # Full manifest comparison matters: Manifest.verify_content alone ignores mode.
        os.chmod(source, 0o600)
        Manifest.verify_content(snapshot.manifests[self.key], snapshot.directory / self.key, self.core)
        with self.assertRaises(WorldlineError) as raised:
            self.finalize(snapshot=snapshot)
        self.assertEqual(raised.exception.code, "CANDIDATE_SNAPSHOT_CHANGED")


if __name__ == "__main__":
    unittest.main()
