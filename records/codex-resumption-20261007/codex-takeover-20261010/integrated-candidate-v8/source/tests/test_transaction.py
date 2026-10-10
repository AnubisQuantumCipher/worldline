from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import unittest
import uuid

from worldline.core import Core, hash_id
from worldline.errors import ConflictError
from worldline.delta import Delta
from worldline.manifest import Manifest
from worldline.model import World, WorldState
from worldline.paths import WorldlinePaths
from worldline.roots import RootManager

from validation_support import DECLARED_EMPTY_POLICY
from owned_evaluation_support import OwnedTransactionEvaluation


class CollapseTransactionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-transaction-")
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
        (self.work / ".worldline.json").write_text(json.dumps(DECLARED_EMPTY_POLICY), encoding="utf-8")
        self.roots.register([self.work], confirmed=True)
        self.transaction = self.evaluation.transaction()
        self.sequence = 0

    def tearDown(self) -> None:
        self.evaluation.close()
        self.temporary.cleanup()

    def _candidate(self, value: str) -> World:
        self.sequence += 1
        alias = f"candidate-{self.sequence}"
        root = self.store.roots()[0]
        root_key = root["root_key"]
        logical = bytes(root["path"])
        current_source = Path(os.fsdecode(self.paths.root_source(root)))
        base_directory = self.paths.worlds / alias / "base"
        candidate_directory = self.paths.worlds / alias / "payload"
        base_directory.parent.mkdir(mode=0o700, parents=True)
        current_manifest = Manifest.capture(
            current_source, logical_root=logical, root_key=root_key,
            kind=root["kind"], core=self.core)
        Manifest.materialize(current_manifest, current_source, base_directory / root_key,
                             core=self.core)
        base_manifest = Manifest.capture(
            base_directory / root_key, logical_root=logical, root_key=root_key,
            kind=root["kind"], core=self.core)
        parent = self.store.prime()
        world = World.create(
            alias=alias, parent_instance=parent.instance_id, parent_content=parent.content_id,
            cause=f"set state to {value}", actor="fixture", payload_path=candidate_directory,
            base_payload_path=base_directory,
            base_root=Manifest.root_set_hash([base_manifest], self.core),
            root_set_hash=parent.root_set_hash,
            mission_hash=hash_id(self.core.hash_bytes(value.encode("utf-8"))))
        self.store.insert_world(world)
        return self.evaluation.finalize_and_revalidate(world, value)

    def _receipt_projection_candidate(self, value: str) -> World:
        # Original mutable fixture for the direct receipt projection only.
        # It is never passed to prepare/commit or asserted to have evaluation authority.
        self.sequence += 1
        alias = f"candidate-{self.sequence}"
        root = self.store.roots()[0]
        root_key = root["root_key"]
        logical = bytes(root["path"])
        current_source = Path(os.fsdecode(os.path.realpath(logical)))
        base_directory = self.paths.worlds / alias / "base"
        candidate_directory = self.paths.worlds / alias / "payload"
        base_directory.parent.mkdir(mode=0o700, parents=True)
        current_manifest = Manifest.capture(
            current_source,
            logical_root=logical,
            root_key=root_key,
            kind=root["kind"],
            core=self.core,
        )
        Manifest.materialize(current_manifest, current_source, base_directory / root_key, core=self.core)
        Manifest.materialize(current_manifest, current_source, candidate_directory / root_key, core=self.core)
        (candidate_directory / root_key / "state.txt").write_text(value, encoding="utf-8")
        base_manifest = Manifest.capture(
            base_directory / root_key,
            logical_root=logical,
            root_key=root_key,
            kind=root["kind"],
            core=self.core,
        )
        candidate_manifest = Manifest.capture(
            candidate_directory / root_key,
            logical_root=logical,
            root_key=root_key,
            kind=root["kind"],
            core=self.core,
        )
        # A finalized world declares its manifests; promotion reads them as the tested bytes.
        (candidate_directory / "manifests").mkdir(mode=0o700, exist_ok=True)
        candidate_manifest.save(candidate_directory / "manifests" / f"{root_key}.json")
        delta = Delta.compute_all({root_key: base_manifest}, {root_key: candidate_manifest}, self.core)
        parent = self.store.prime()
        world = World.create(
            alias=alias,
            parent_instance=parent.instance_id,
            parent_content=parent.content_id,
            cause=f"set state to {value}",
            actor="fixture",
            payload_path=candidate_directory,
            base_payload_path=base_directory,
            base_root=Manifest.root_set_hash([base_manifest], self.core),
            root_set_hash=parent.root_set_hash,
            mission_hash=hash_id(self.core.hash_bytes(value.encode("utf-8"))),
        )
        world.components = {
            **Manifest.component_roots([candidate_manifest], self.core),
            "environment": parent.components["environment"],
            "evidence": parent.components["evidence"],
        }
        world.delta_hash = delta.delta_hash
        world.delta = {**delta.value["summary"], "files": delta.value["operations"]}
        world.transition(WorldState.FINALIZING, self.core)
        world.establish_identity(self.core)
        world.transition(WorldState.VALID, self.core)
        self.store.insert_world(world)
        return world

    def test_clean_commit_exchanges_mapping_and_links_receipt(self) -> None:
        candidate = self._candidate("collapsed")
        prepared = self.transaction.prepare(candidate.alias)
        self.assertEqual(prepared.decision, "AUTHORIZED")
        result = self.transaction.commit(prepared.transaction_id)
        self.assertEqual(result["state"], "COMMITTED")
        self.assertEqual((self.work / "state.txt").read_text(encoding="utf-8"), "collapsed")
        self.assertEqual(self.store.world(candidate.alias).state, WorldState.COLLAPSED)
        receipt = self.store.last_receipt()["receipt"]
        self.assertEqual(receipt["transactionId"], prepared.transaction_id)
        self.assertEqual(receipt["beforeRoot"], prepared.before_root)
        self.assertEqual(receipt["afterRoot"], prepared.staged_root)
        self.assertEqual(self.store.verify_chains()["receipts"], 1)

    def test_touched_prime_change_denies_without_mutation(self) -> None:
        candidate = self._candidate("candidate")
        (self.work / "state.txt").write_text("prime changed", encoding="utf-8")
        with self.assertRaises(ConflictError) as caught:
            self.transaction.prepare(candidate.alias)
        self.assertEqual(caught.exception.details["decision"], "CONFLICT")
        self.assertEqual((self.work / "state.txt").read_text(encoding="utf-8"), "prime changed")
        denied = self.store.transactions_in_state(("DENIED",))
        self.assertEqual(len(denied), 1)

    def test_recovery_aborts_before_exchange(self) -> None:
        candidate = self._candidate("not committed")
        prepared = self.transaction.prepare(candidate.alias)
        recovered = self.transaction.recover_all()
        self.assertEqual(recovered, [{"transactionId": prepared.transaction_id, "state": "ABORTED"}])
        self.assertNotEqual((self.work / "state.txt").read_text(encoding="utf-8"), "not committed")
        self.assertEqual(self.store.world(candidate.alias).state, WorldState.VALID)

    def test_recovery_finishes_after_exchange_marker(self) -> None:
        candidate = self._candidate("recovered")
        prepared = self.transaction.prepare(candidate.alias)
        record = self.transaction._load_record(prepared.transaction_id)
        self.transaction._set_state(record, "AUTHORIZED")
        self.transaction.atomic.exchange(self.paths.live, Path(record["preparedMapping"]))
        recovered = self.transaction.recover_all()
        self.assertEqual(recovered[0]["state"], "COMMITTED")
        self.assertEqual((self.work / "state.txt").read_text(encoding="utf-8"), "recovered")
        self.assertIsNotNone(self.store.receipt_for_transaction(prepared.transaction_id))

    def test_receipt_classifies_generated_and_dependency_changes(self) -> None:
        candidate = self._receipt_projection_candidate("details")
        root_key = self.store.roots()[0]["root_key"]
        base_root = Path(candidate.base_payload_path) / root_key
        candidate_root = Path(candidate.payload_path) / root_key
        (base_root / "pyproject.toml").write_text(
            "[project]\nname='fixture'\ndependencies=['alpha==1']\n",
            encoding="utf-8",
        )
        (candidate_root / "pyproject.toml").write_text(
            "[project]\nname='fixture'\ndependencies=['alpha==2', 'beta']\n",
            encoding="utf-8",
        )
        changes = self.transaction._dependency_changes(candidate, self.store.roots())
        self.assertEqual(
            {(item["name"], item["change"]) for item in changes},
            {("alpha", "MODIFY"), ("beta", "ADD")},
        )
        delta = {
            "deltaHash": candidate.delta_hash,
            "baseRoot": candidate.base_root,
            "summary": {"added": 1, "modified": 0, "deleted": 0, "files": 1},
            "operations": [
                {
                    "rootKey": root_key,
                    "pathB64": "Z2VuZXJhdGVkL291dC5qc29u",
                    "pathDisplay": "generated/out.json",
                    "op": "ADD",
                }
            ],
        }
        receipt = self.transaction.receipts.build(
            transaction_id=str(uuid.uuid4()),
            parent_world=candidate.parent_content,
            candidate_world=candidate.content_id,
            before_root=candidate.base_root,
            after_root=candidate.base_root,
            delta=delta,
            contamination=[],
            generated=[{"root": root_key, "glob": "generated/**"}],
            dependency_changes=changes,
        )
        self.assertEqual(len(receipt["mergeSet"]["generatedArtifacts"]), 1)
        self.assertEqual(receipt["mergeSet"]["dependencyChanges"], changes)


if __name__ == "__main__":
    unittest.main()


class ResultingRequirementTransactionTests(CollapseTransactionTests):
    """Actual retained runner/evaluation plus only the original freshness shortcut bypass.

    These controls require native raw authority; legacy mutable receipts are not substitutes.
    """
    def _requirement_candidate(self, value: str, mutation_source: str) -> World:
        self.sequence += 1
        alias = f"candidate-{self.sequence}"
        root = self.store.roots()[0]
        root_key = root["root_key"]
        logical = bytes(root["path"])
        current_source = Path(os.fsdecode(self.paths.root_source(root)))
        base_directory = self.paths.worlds / alias / "base"
        candidate_directory = self.paths.worlds / alias / "payload"
        base_directory.parent.mkdir(mode=0o700, parents=True)
        current_manifest = Manifest.capture(
            current_source, logical_root=logical, root_key=root_key,
            kind=root["kind"], core=self.core)
        Manifest.materialize(current_manifest, current_source, base_directory / root_key,
                             core=self.core)
        base_manifest = Manifest.capture(
            base_directory / root_key, logical_root=logical, root_key=root_key,
            kind=root["kind"], core=self.core)
        parent = self.store.prime()
        world = World.create(
            alias=alias, parent_instance=parent.instance_id, parent_content=parent.content_id,
            cause=f"set state to {value}", actor="fixture", payload_path=candidate_directory,
            base_payload_path=base_directory,
            base_root=Manifest.root_set_hash([base_manifest], self.core),
            root_set_hash=parent.root_set_hash,
            mission_hash=hash_id(self.core.hash_bytes(value.encode("utf-8"))))
        self.store.insert_world(world)
        return self.evaluation.finalize_and_revalidate_mutation(world, value, mutation_source)


    def test_judge_mutations_refuse_even_when_freshness_shortcut_is_bypassed(self) -> None:
        from unittest import mock
        from worldline.validation import current_requirements
        from worldline.errors import WorldlineError
        from worldline.evaluation_authority import read
        policy = {"schemaVersion": 1, "generated": [], "services": [],
                  "protected": ["sentinel"], "checks": [{"id": "exam", "kind": "tests",
                  "argv": ["/usr/bin/python3", "evaluator/exam.py"], "required": True,
                  "format": "exit", "covers": ["state.txt"], "verifiers": ["evaluator/*"]}]}
        # Each control starts from a fresh registered PRIME; no preceding denial is reused.
        for mutation in ("loosen-checks", "drop-protected", "rewrite-examiner"):
            with self.subTest(mutation=mutation):
                import stat
                os.chmod(self.work, stat.S_IMODE(self.work.stat().st_mode) | 0o700)
                policy_path = self.work / ".worldline.json"
                os.chmod(policy_path, stat.S_IMODE(policy_path.stat().st_mode) | 0o600)
                examiner = self.work / "evaluator" / "exam.py"
                if examiner.parent.exists():
                    os.chmod(examiner.parent, stat.S_IMODE(examiner.parent.stat().st_mode) | 0o700)
                if examiner.exists():
                    os.chmod(examiner, stat.S_IMODE(examiner.stat().st_mode) | 0o600)
                examiner.parent.mkdir(exist_ok=True)
                examiner.write_text("raise SystemExit(0)\n", encoding="utf-8")
                (self.work / ".worldline.json").write_text(json.dumps(policy), encoding="utf-8")
                self.store.set_meta("dirty", True)
                self.roots.reconcile()
                if mutation == "rewrite-examiner":
                    script = "from pathlib import Path\nPath('evaluator/exam.py').write_text('# changed judge\\nraise SystemExit(0)\\n')"
                else:
                    field = "checks" if mutation == "loosen-checks" else "protected"
                    script = ("import json\nfrom pathlib import Path\np=Path('.worldline.json')\n"
                              "v=json.loads(p.read_text())\nv[" + repr(field) + "]=[]\np.write_text(json.dumps(v))")
                candidate = self._requirement_candidate(mutation, script)
                current = current_requirements(self.store, self.evaluation.config, self.core)
                selected = read(self.store, candidate, current['requirementHash'], core=self.core)
                context = selected.context
                execution = self.transaction._execution_identity(candidate, current,
                                                                  recorded_checks=selected.results)
                freshness = {"mode": "collapse", "requirementHash": current["requirementHash"],
                    "candidateRequirementHash": context["requirementHash"],
                    "contextHash": context["contextHash"], "source": selected.source,
                    "policySourceSha256": current["policy"].get("sourceSha256"),
                    "subject": candidate.instance_id, "evaluatedAt": context.get("evaluatedAt"),
                    "evidenceInstance": (context.get("candidate") or {}).get("instanceId"),
                    "examinedContentRoot": context.get("examinedContentRoot"),
                    "evaluationCursor": selected.cursor, "current": current, "execution": execution}
                before = (self.work / "state.txt").read_bytes()
                receipts = self.store.receipts()
                with mock.patch.object(self.transaction, '_freshness', return_value=freshness):
                    with self.assertRaises(WorldlineError) as caught:
                        self.transaction.prepare(candidate.alias)
                self.assertEqual(caught.exception.details["decision"], "REQUIREMENT_CHANGED")
                self.assertEqual((self.work / "state.txt").read_bytes(), before)
                self.assertEqual(self.store.receipts(), receipts)
