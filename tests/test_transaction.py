from __future__ import annotations

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
from worldline.store import StateStore
from worldline.transaction import CollapseTransaction


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
        self.store = StateStore(self.paths, self.core)
        self.roots = RootManager(self.paths, self.store, core=self.core, toolchains=())
        self.work = root / "work"
        self.work.mkdir()
        (self.work / "state.txt").write_text("prime", encoding="utf-8")
        self.roots.register([self.work], confirmed=True)
        self.transaction = CollapseTransaction(self.paths, self.store, core=self.core)
        self.sequence = 0

    def tearDown(self) -> None:
        self.store.close()
        self.temporary.cleanup()

    def _candidate(self, value: str) -> World:
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
        candidate = self._candidate("details")
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
