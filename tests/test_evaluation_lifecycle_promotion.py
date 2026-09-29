"""Promotion paths that 1.7.3 left open, reproduced and refused (1.8.0, evaluation lifecycle).

Each case drives a private daemon end to end through the client, the way an operator would:
nothing here builds kernel inputs by hand. The reproducers for 1.7.3 live with the release
evidence; these tests are the 1.8.0 side of the same scenarios.
"""
from __future__ import annotations

import json
import os
import unittest

from freshness_support import EXAM_CHECK, FreshnessLab, P0, P1, isolated_paths, policy, synthetic_candidate
from validation_support import DECLARED_EMPTY_POLICY, attach_fresh_context
from worldline.config import GlobalConfig
from worldline.core import Core
from worldline.errors import WorldlineError
from worldline.model import WorldState
from worldline.project import ProjectConfig
from worldline.roots import RootManager
from worldline.store import StateStore
from worldline.transaction import CollapseTransaction


class ReapplyingAFailedWorld(unittest.TestCase):
    def setUp(self) -> None:
        self.lab = FreshnessLab(self, policy_value=P0)
        self.addCleanup(self.lab.close)
        self.lab.init()

    def worlds(self) -> dict[str, str]:
        return {world["alias"]: world["state"] for world in self.lab.client.request("status")["worlds"]}

    def fail_then_archive(self) -> None:
        self.assertEqual(self.lab.fork("bad", agent="slacker")["state"], "DEGRADED")
        self.assertEqual(self.lab.fork("good")["state"], "VALID")
        self.lab.commit(self.lab.prepare("good")["transaction_id"])
        self.assertEqual(self.worlds()["bad"], "ARCHIVED")

    def test_an_archived_formerly_degraded_world_cannot_be_reapplied(self) -> None:
        # 1.7.3: `return bad` re-applied a world whose required exam had COMPLETED with FAIL. The
        # promotion boundary checked only that execution reached the examiner, so the failed
        # world became PRIME. The kernel now admits a check only when it completed AND passed.
        self.fail_then_archive()
        before = self.lab.live()
        refused = self.lab.refusal(self.lab.return_prepare, "bad")
        self.assertEqual(refused.details.get("decision"), "EXECUTION_EVIDENCE_INCOMPLETE", refused.details)
        self.assertTrue(any(problem.startswith("exam:") for problem in refused.details["execution"]["problems"]))
        self.assertEqual(self.lab.live(), before)

    def test_the_synthetic_world_a_refused_return_leaves_is_not_a_checkpoint(self) -> None:
        # 1.7.3: a refused `return X` left its synthetic candidate (actor "worldline") VALID in
        # the store, and `return <that world>` then took the checkpoint path, which needs no
        # evidence at all. The case is now explicit in the kernel and needs a lineage witness,
        # which a world that never became live does not have.
        self.fail_then_archive()
        self.lab.refusal(self.lab.return_prepare, "bad")
        leftovers = [alias for alias, state in self.worlds().items()
                     if alias.startswith("return-bad-") and state == "VALID"]
        self.assertEqual(len(leftovers), 1, self.worlds())
        # Any later change to PRIME gives the next synthetic world a different identity (the
        # operator keeps working); without one the second step is refused as WORLD_CONFLICT.
        self.lab.write("notes.txt", "later work\n")
        self.lab.settle()
        before = self.lab.live()
        refused = self.lab.refusal(self.lab.return_prepare, leftovers[0])
        self.assertEqual(refused.details.get("decision"), "CHECKPOINT_UNWITNESSED", refused.details)
        self.assertIsNone(refused.details["validation"]["witness"])
        self.assertEqual(self.lab.live(), before)

    def test_a_stale_world_cannot_ride_the_synthetic_world_either(self) -> None:
        # The same two steps with evidence that is merely stale: the refusal of the first step is
        # a different code, and the second step must still be refused.
        self.assertEqual(self.lab.fork("stale")["state"], "VALID")
        self.lab.set_policy(P1)
        self.lab.settle()
        self.assertEqual(self.lab.refusal(self.lab.return_prepare, "stale").code, "EVIDENCE_STALE")
        leftovers = [alias for alias, state in self.worlds().items() if alias.startswith("return-stale-")]
        self.assertEqual(len(leftovers), 1, self.worlds())
        self.lab.write("notes.txt", "later work\n")
        self.lab.settle()
        before = self.lab.live()
        refused = self.lab.refusal(self.lab.return_prepare, leftovers[0])
        self.assertEqual(refused.details.get("decision"), "CHECKPOINT_UNWITNESSED", refused.details)
        self.assertEqual(self.lab.live(), before)

    def test_returning_to_a_previous_checkpoint_is_witnessed_and_still_works(self) -> None:
        prime_before = self.lab.prime()
        self.assertEqual(self.lab.fork("good")["state"], "VALID")
        self.lab.commit(self.lab.prepare("good")["transaction_id"])
        prepared = self.lab.return_prepare(prime_before["instanceId"])
        self.assertEqual(prepared["validation"]["mode"], "checkpoint-return")
        witness = prepared["validation"]["witness"]
        self.assertEqual(witness["expected"], witness["witnessed"])
        self.assertTrue(witness["source"].startswith(("lineage:", "prime-register")))
        self.assertEqual(self.lab.commit(prepared["transaction_id"])["state"], "COMMITTED")


class NoManufacturedCompletion(unittest.TestCase):
    def test_a_project_with_no_policy_has_declared_nothing(self) -> None:
        lab = FreshnessLab(self, policy_value=None)
        self.addCleanup(lab.close)
        lab.init()
        # The agent's own exit is still judged at finalization...
        self.assertEqual(lab.fork("w")["state"], "VALID")
        # ...but nothing declares what a collapse requires, and nothing is not a pass.
        before = lab.live()
        refused = lab.refusal(lab.prepare, "w")
        self.assertEqual(refused.details.get("decision"), "EXECUTION_EVIDENCE_INCOMPLETE", refused.details)
        self.assertTrue(refused.details["execution"]["problems"])
        self.assertEqual(lab.live(), before)

    def test_a_declared_empty_policy_is_an_explicit_fact(self) -> None:
        lab = FreshnessLab(self, policy_value=DECLARED_EMPTY_POLICY)
        self.addCleanup(lab.close)
        lab.init()
        self.assertEqual(lab.fork("w")["state"], "VALID")
        self.assertEqual(lab.commit(lab.prepare("w")["transaction_id"])["state"], "COMMITTED")


class SystemFuturesAreNeverPromoted(unittest.TestCase):
    def test_a_system_world_cannot_be_returned_to(self) -> None:
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory(prefix="worldline-system-return-") as temporary:
            paths, _env = isolated_paths(Path(temporary))
            core = Core.shared()
            store = StateStore(paths, core)
            self.addCleanup(store.close)
            work = Path(temporary) / "work"; work.mkdir()
            (work / "state.txt").write_text("prime", encoding="utf-8")
            (work / ".worldline.json").write_text(json.dumps(DECLARED_EMPTY_POLICY), encoding="utf-8")
            RootManager(paths, store, core=core, toolchains=()).register([work], confirmed=True)
            future = synthetic_candidate(paths, store, core, "future", {"state.txt": "simulated"})
            future.world_kind = "system"
            store.save_world(future)
            carrier = synthetic_candidate(paths, store, core, "carrier", {"state.txt": "simulated"})
            attach_fresh_context(store, carrier, core=core)
            with self.assertRaises(WorldlineError) as raised:
                CollapseTransaction(paths, store, core=core).prepare("carrier", kind="return", return_of=future.instance_id)
            self.assertEqual(raised.exception.code, "SYSTEM_ROOT_COLLAPSE_UNSUPPORTED")


class ReservedNames(unittest.TestCase):
    def test_an_adapter_may_not_take_an_actor_name_worldline_writes(self) -> None:
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as temporary:
            paths, _env = isolated_paths(Path(temporary))
            base = GlobalConfig.default(paths).value
            for name in ("worldline", "system", "WorldLine"):
                with self.subTest(name=name):
                    value = {**base, "agentCommands": {name: {"argv": ["/usr/bin/true"], "credentialMounts": [], "eventFormat": "jsonl"}}}
                    with self.assertRaises(WorldlineError) as raised:
                        GlobalConfig(paths, value)
                    self.assertEqual(raised.exception.code, "INVALID_CONFIG")
                    self.assertIn("reserved", raised.exception.message)

    def test_a_policy_may_not_declare_a_check_worldline_produces_itself(self) -> None:
        import tempfile
        from pathlib import Path
        for identifier in ("agent", "protected-paths"):
            with self.subTest(identifier=identifier), tempfile.TemporaryDirectory() as temporary:
                paths, _env = isolated_paths(Path(temporary))
                store = StateStore(paths, Core.shared())
                self.addCleanup(store.close)
                root = Path(temporary) / "root"; root.mkdir()
                (root / ".worldline.json").write_text(json.dumps(policy({**EXAM_CHECK, "id": identifier})), encoding="utf-8")
                with self.assertRaises(WorldlineError) as raised:
                    ProjectConfig.load(root, store)
                self.assertEqual(raised.exception.code, "INVALID_PROJECT_CONFIG")


if __name__ == "__main__":
    unittest.main()
