"""Phase 1 item 3 (1.9.0): typed absence and honest collapse inputs, end to end.

Each refusal here is the proved kernel's, reached through the real prepare and commit paths
with one input moved: a DENIED record, live PRIME unchanged, no receipt. The kernel tests
(worldline_core_tests, the fuzz oracle, test_core_abi) cover every decision code in isolation;
these show that each producer reaches the kernel with the value it claims, and that nothing
absent is filled in on the way.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import sys
import tempfile
from typing import Any, Callable
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

from worldline.checkpoint import CheckpointManager
from worldline.core import Core, hash_id
from worldline.errors import WorldlineError
from worldline.returning import ReturnManager
from worldline.roots import RootManager
from worldline.store import StateStore
from worldline.transaction import CollapseTransaction
from worldline.validation import _digest, current_requirements

from freshness_support import FreshnessLab, isolated_paths, synthetic_candidate, tree_bytes
from validation_support import DECLARED_EMPTY_POLICY, attach_fresh_context
from watch_support import FakeWatcher, watched


class _InProcess(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-typed-absence-")
        root = Path(self.temporary.name)
        self.paths, _env = isolated_paths(root)
        self.core = Core.shared()
        self.store = StateStore(self.paths, self.core)
        self.work = root / "work"; self.work.mkdir()
        (self.work / ".worldline.json").write_text(json.dumps(DECLARED_EMPTY_POLICY), encoding="utf-8")
        (self.work / "state.txt").write_text("prime", encoding="utf-8")
        (self.work / "other.txt").write_text("one", encoding="utf-8")
        self.roots = RootManager(self.paths, self.store, core=self.core, toolchains=())
        self.roots.register([self.work], confirmed=True)
        self.transaction = watched(CollapseTransaction(self.paths, self.store, core=self.core, reconcile=self.roots.reconcile),
                                   self.paths, self.store)
        self.key = self.store.roots()[0]["root_key"]

    def tearDown(self) -> None:
        self.store.close()
        self.temporary.cleanup()

    def candidate(self, alias: str, changes: dict[str, str] | None = None) -> Any:
        world = synthetic_candidate(self.paths, self.store, self.core, alias, changes or {"state.txt": alias})
        attach_fresh_context(self.store, world, core=self.core)
        return self.store.world(alias)

    def live(self) -> Path:
        return Path(os.path.realpath(self.work))

    def write_live(self, relative: str, text: str) -> None:
        # Live PRIME is a published generation with the candidate's modes; open it to a write
        # the way an operator's editor would.
        live = self.live()
        target = live / relative
        for path in (live, target):
            if path.exists():
                os.chmod(path, stat.S_IMODE(path.stat().st_mode) | 0o200)
        target.write_text(text, encoding="utf-8")

    def reconciled(self) -> None:
        """What the daemon does for an external write: the watcher marks PRIME dirty and the
        next status reconciles it into a PRIME generation."""
        self.store.set_meta("dirty", True)
        self.roots.reconcile()

    def record(self, transaction_id: str) -> tuple[Path, dict[str, Any]]:
        path = Path(self.store.transaction_record(transaction_id)["prepared_path"])
        return path, json.loads(path.read_text(encoding="utf-8"))

    def denied(self, action: Callable[[], Any], decision: str, *, code: str = "CONFLICT") -> WorldlineError:
        before, prime, receipts = tree_bytes(self.work), self.store.prime().instance_id, len(self.store.receipts())
        with self.assertRaises(WorldlineError) as raised:
            action()
        error = raised.exception
        self.assertEqual((error.code, error.details.get("decision")), (code, decision), error.details)
        self.assertEqual(self.store.transaction_record(error.details["transactionId"])["state"], "DENIED")
        self.assertEqual(tree_bytes(self.work), before, "live PRIME bytes changed across a refusal")
        self.assertEqual(self.store.prime().instance_id, prime, "PRIME moved across a refusal")
        self.assertEqual(len(self.store.receipts()), receipts, "a refusal produced a receipt")
        return error


class A_EvidenceSubject(_InProcess):
    """The evidence subject pair has two producers: the promotion's own arguments, and the
    binding the speaking evaluation (or the return vehicle) carries."""

    def returns(self) -> ReturnManager:
        checkpoints = watched(CheckpointManager(self.paths, self.store, core=self.core), self.paths, self.store)
        return ReturnManager(self.paths, self.store, checkpoints, self.transaction, core=self.core)

    def test_a_context_rebound_to_another_world_with_its_hash_recomputed_is_refused(self) -> None:
        alpha = self.candidate("alpha")
        beta = self.candidate("beta")
        context = json.loads(json.dumps(beta.evidence["validationContext"]))
        context["candidate"]["instanceId"] = alpha.instance_id
        context["contextHash"] = _digest({k: v for k, v in context.items() if k != "contextHash"}, self.core)
        beta.evidence = {**beta.evidence, "validationContext": context}
        self.store.save_world(beta)
        self.denied(lambda: self.transaction.prepare("beta"), "EVIDENCE_SUBJECT_MISMATCH")

    def test_an_edited_return_vehicle_is_refused(self) -> None:
        start = self.store.prime()
        self.assertEqual(self.transaction.commit(self.transaction.prepare(self.candidate("w").alias).transaction_id)["state"], "COMMITTED")
        returns = self.returns()
        vehicle = returns.prepare_candidate(returns.select(start.instance_id))
        vehicle.mission_hash = hash_id(self.core.hash_bytes(b"a mission that is not this return"))
        self.store.save_world(vehicle)
        self.denied(lambda: self.transaction.prepare(vehicle.instance_id, kind="return", return_of=start.instance_id),
                    "EVIDENCE_SUBJECT_MISMATCH")

    def test_an_edited_return_of_at_commit_is_refused(self) -> None:
        start = self.store.prime()
        w = self.candidate("w")
        self.assertEqual(self.transaction.commit(self.transaction.prepare("w").transaction_id)["state"], "COMMITTED")
        returns = self.returns()
        vehicle = returns.prepare_candidate(returns.select(start.instance_id))
        prepared = self.transaction.prepare(vehicle.instance_id, kind="return", return_of=start.instance_id)
        self.assertEqual(prepared.decision, "AUTHORIZED")
        path, record = self.record(prepared.transaction_id)
        record["returnOf"] = w.instance_id
        path.write_text(json.dumps(record), encoding="utf-8")
        self.denied(lambda: self.transaction.commit(prepared.transaction_id), "EVIDENCE_SUBJECT_MISMATCH",
                    code="EVIDENCE_SUBJECT_MISMATCH")

    def test_a_deleted_evidence_subject_is_absent_never_equal(self) -> None:
        prepared = self.transaction.prepare(self.candidate("alpha").alias)
        path, record = self.record(prepared.transaction_id)
        del record["decisionInputs"]["evidenceSubject"]
        path.write_text(json.dumps(record), encoding="utf-8")
        error = self.denied(lambda: self.transaction.commit(prepared.transaction_id), "IDENTITY_ABSENT", code="IDENTITY_ABSENT")
        self.assertIn("evidence_subject", error.details["absentInputs"])

    def test_a_record_that_does_not_state_conflicts_were_measured_is_unmeasured(self) -> None:
        prepared = self.transaction.prepare(self.candidate("alpha").alias)
        path, record = self.record(prepared.transaction_id)
        del record["decisionInputs"]["conflictsMeasured"]
        path.write_text(json.dumps(record), encoding="utf-8")
        self.denied(lambda: self.transaction.commit(prepared.transaction_id), "MEASUREMENT_ABSENT", code="MEASUREMENT_ABSENT")


class B_StagedRoot(_InProcess):
    def test_staging_tampered_between_prepare_and_commit_is_refused_by_the_kernel(self) -> None:
        prepared = self.transaction.prepare(self.candidate("alpha").alias)
        _path, record = self.record(prepared.transaction_id)
        staged = Path(record["stagingPayload"]) / self.key
        os.chmod(staged, stat.S_IMODE(staged.stat().st_mode) | 0o700)
        replacement = staged / ".tampered"
        replacement.write_text("not what was prepared", encoding="utf-8")
        os.replace(replacement, staged / "state.txt")  # a new inode: the candidate payload is untouched
        self.denied(lambda: self.transaction.commit(prepared.transaction_id), "STAGED_ROOT_MISMATCH", code="STAGED_ROOT_MISMATCH")


class C_ForeignWrites(_InProcess):
    def test_an_unreported_write_is_refused_then_reconciled_and_authorized(self) -> None:
        alpha = self.candidate("alpha")
        prime = self.store.prime()
        self.write_live("unreported.txt", "nobody told the watcher")
        error = self.denied(lambda: self.transaction.prepare(alpha.alias), "FOREIGN_MANAGED_WRITE")
        self.assertEqual(error.details["foreignWrites"]["state"], "FOUND")
        self.assertIn("filesystem", error.details["foreignWrites"]["differing"])
        self.assertTrue(self.store.get_meta("dirty", False))
        kinds = [item["event"].get("kind") for item in self.store.causal_events_for_world(prime.instance_id)]
        self.assertIn("unaccounted-write", kinds)
        # The retry reconciles first, since PRIME is dirty. The reconciled write is now PRIME
        # content the candidate's evidence never examined, so a staged evaluation covers it.
        self.transaction.validator = _staged_validator(self)
        prepared = self.transaction.prepare(alpha.alias)
        self.assertEqual(prepared.decision, "AUTHORIZED")
        self.assertNotEqual(self.store.prime().instance_id, prime.instance_id)
        self.assertEqual(self.transaction.commit(prepared.transaction_id)["state"], "COMMITTED")
        receipt = self.store.receipt_for_transaction(prepared.transaction_id)["receipt"]
        foreign = receipt["foreignWorldContamination"]
        self.assertEqual((foreign["state"], foreign["measurement"], foreign["measuredBy"]),
                         ("NONE", "NONE_FOUND", "live-capture-vs-prime-record"))

    def test_a_prime_record_without_its_components_is_unmeasured(self) -> None:
        alpha = self.candidate("alpha")
        prime = self.store.prime()
        prime.components = {name: value for name, value in prime.components.items() if name != "config"}
        self.store.save_world(prime)
        error = self.denied(lambda: self.transaction.prepare(alpha.alias), "MEASUREMENT_ABSENT")
        self.assertEqual(error.details["foreignWrites"]["state"], "UNMEASURED")
        self.assertFalse(self.store.get_meta("dirty", False))

    def test_recorded_contamination_is_a_foreign_write(self) -> None:
        alpha = self.candidate("alpha")
        alpha.contamination = [{"path": "state.txt", "by": "hand"}]
        self.store.save_world(alpha)
        error = self.denied(lambda: self.transaction.prepare(alpha.alias), "FOREIGN_MANAGED_WRITE")
        self.assertEqual(error.details["foreignWrites"]["measuredBy"], "recorded-contamination")
        self.assertFalse(self.store.get_meta("dirty", False))


class _MovingWatcher(FakeWatcher):
    """A watcher whose generation moves on every read: PRIME changed while it was captured."""

    def synchronized_generation(self) -> int:
        self.generation += 1
        return self.generation


class D_WatchAndGeneration(_InProcess):
    def test_a_root_the_watcher_is_not_watching_is_watch_incomplete(self) -> None:
        alpha = self.candidate("alpha")
        self.transaction.watcher.missing = {self.key}
        self.denied(lambda: self.transaction.prepare(alpha.alias), "WATCH_INCOMPLETE")

    def test_no_watcher_is_measurement_absent(self) -> None:
        alpha = self.candidate("alpha")
        self.transaction.watcher = None
        error = self.denied(lambda: self.transaction.prepare(alpha.alias), "MEASUREMENT_ABSENT")
        self.assertTrue({"generation_before", "generation_after", "watched_set"} <= set(error.details["absentInputs"]),
                        error.details["absentInputs"])

    def test_a_generation_that_moves_during_prepare_is_prime_changed(self) -> None:
        alpha = self.candidate("alpha")
        self.transaction.watcher = _MovingWatcher(self.paths, self.store)
        error = self.denied(lambda: self.transaction.prepare(alpha.alias), "PRIME_CHANGED", code="PRIME_CHANGED_DURING_CAPTURE")
        self.assertNotEqual(error.details["beforeGeneration"], error.details["afterGeneration"])

    def test_a_generation_that_moves_during_commit_is_prime_changed(self) -> None:
        prepared = self.transaction.prepare(self.candidate("alpha").alias)
        self.transaction.watcher = _MovingWatcher(self.paths, self.store)
        self.denied(lambda: self.transaction.commit(prepared.transaction_id), "PRIME_CHANGED", code="PRIME_CHANGED_DURING_CAPTURE")


def _staged_validator(test: _InProcess, **override: Any) -> Callable[..., dict[str, Any]]:
    """A staged evaluation that ran the current requirement and records what it examined."""
    def validate(payload: Path, candidate: Any, current_manifests: Any, staged_manifests: Any, staged_content_root: str) -> dict[str, Any]:
        entry = {"validationId": "staged-fixture", "outcome": "PASS", "summary": "fixture",
                 "requirementHash": current_requirements(test.store, None, test.core)["requirementHash"],
                 "contextHash": None, "examinedContentRoot": staged_content_root, "results": [],
                 "context": {}, "stagedContentRoot": staged_content_root}
        entry.update(override)
        return entry
    return validate


class E_StagedEvidence(_InProcess):
    """PRIME moved under the candidate: the staged bytes are not the bytes its evidence examined.
    The kernel accepts them only through a staged evaluation that examined exactly them."""

    def moved(self, alias: str = "alpha") -> Any:
        world = self.candidate(alias)
        self.write_live("other.txt", f"moved under {alias}")
        self.reconciled()
        return world

    def test_a_staged_evaluation_of_exactly_the_staged_bytes_authorizes(self) -> None:
        alpha = self.moved()
        self.transaction.validator = _staged_validator(self)
        prepared = self.transaction.prepare(alpha.alias)
        self.assertEqual(prepared.decision, "AUTHORIZED")
        self.assertNotEqual(prepared.tested_root, prepared.staged_content_root)
        self.assertEqual(prepared.staged_validation["examinedContentRoot"], prepared.staged_content_root)

    def test_each_way_a_staged_evaluation_can_fail_to_cover_is_staged_untested(self) -> None:
        cases = {
            "examined other bytes": {"examinedContentRoot": hash_id(bytes([7]) * 32)},
            "examined nothing it can name": {"examinedContentRoot": None},
            "ran a stale requirement": {"requirementHash": hash_id(bytes([8]) * 32)},
            "ran no requirement it can name": {"requirementHash": None},
        }
        for index, (label, override) in enumerate(cases.items()):
            with self.subTest(label):
                alpha = self.moved(f"alpha{index}")
                self.transaction.validator = _staged_validator(self, **override)
                self.denied(lambda: self.transaction.prepare(alpha.alias), "STAGED_UNTESTED")

    def test_without_a_validator_moved_bytes_are_staged_untested(self) -> None:
        alpha = self.moved()
        error = self.denied(lambda: self.transaction.prepare(alpha.alias), "STAGED_UNTESTED")
        self.assertTrue(any(p.endswith(":other.txt") for p in error.details["untestedPaths"]))

    def test_a_staged_run_that_rewrote_a_verifier_is_refused_by_name(self) -> None:
        alpha = self.moved()
        self.transaction.validator = _staged_validator(self, context={"verifiersModifiedByCandidate": ["exam.py (modified)"]})
        with self.assertRaises(WorldlineError) as raised:
            self.transaction.prepare(alpha.alias)
        self.assertEqual(raised.exception.code, "VERIFIER_MODIFIED_BY_CANDIDATE")


class F_RecordsAndReapplication(_InProcess):
    def test_a_conflict_records_no_staged_root(self) -> None:
        alpha = self.candidate("alpha", {"state.txt": "alpha"})
        self.write_live("state.txt", "somebody else")
        self.reconciled()
        error = self.denied(lambda: self.transaction.prepare(alpha.alias), "CONFLICT")
        row = self.store.transaction_record(error.details["transactionId"])
        self.assertEqual(row["staged_root"], "absent")
        record = json.loads(Path(row["prepared_path"]).read_text(encoding="utf-8"))
        self.assertIsNone(record["stagedRoot"])
        self.assertIsNone(record["decisionInputs"]["stagedRoot"])

    def _reapply_without_finalized_manifests(self) -> tuple[Any, ReturnManager]:
        w = self.candidate("w", {"state.txt": "w"})
        self.assertEqual(self.transaction.commit(self.transaction.prepare("w").transaction_id)["state"], "COMMITTED")
        x = self.candidate("x", {"other.txt": "x"})
        self.assertEqual(self.transaction.commit(self.transaction.prepare("x").transaction_id)["state"], "COMMITTED")
        manifests = Path(self.store.world("w").payload_path) / "manifests"
        os.chmod(manifests, stat.S_IMODE(manifests.stat().st_mode) | 0o700)
        for item in manifests.iterdir():
            item.unlink()
        checkpoints = watched(CheckpointManager(self.paths, self.store, core=self.core), self.paths, self.store)
        return self.store.world("w"), ReturnManager(self.paths, self.store, checkpoints, self.transaction, core=self.core)

    def test_reapplication_without_finalized_manifests_and_no_validator_is_staged_untested(self) -> None:
        w, returns = self._reapply_without_finalized_manifests()
        error = self.denied(lambda: returns.execute(w.instance_id), "STAGED_UNTESTED")
        self.assertEqual(error.details["validation"]["mode"], "re-application")
        _path, record = self.record(error.details["transactionId"])
        self.assertIsNone(record["testedRoot"])
        self.assertEqual(record["decisionInputs"]["testedRootSource"], "finalized-manifests-missing")

    def test_reapplication_without_finalized_manifests_authorizes_on_a_staged_evaluation(self) -> None:
        w, returns = self._reapply_without_finalized_manifests()
        self.transaction.validator = _staged_validator(self)
        self.assertEqual(returns.execute(w.instance_id)["state"], "COMMITTED")


class G_DoctorPromotionReadiness(unittest.TestCase):
    """The census the 1.9.0 upgrade notes rely on: read-only, and it names what promotion
    will refuse before anyone tries."""

    def test_doctor_reports_readiness_and_measures_foreign_writes_only_on_refresh(self) -> None:
        lab = FreshnessLab(self, policy_value=DECLARED_EMPTY_POLICY)
        try:
            lab.init()
            self.assertEqual(lab.fork("alpha")["state"], "VALID")
            report = lab.client.request("doctor", {})["promotionReadiness"]
            self.assertEqual(report["pendingTransactions"], [])
            self.assertEqual(report["watchCoverage"]["state"], "COMPLETE")
            self.assertEqual(report["watchCoverage"]["unwatchedRoots"], [])
            self.assertIsNone(report["foreignWrites"]["state"])  # not captured without --refresh
            self.assertEqual([w["alias"] for w in report["validWorlds"]["fresh"]], ["alpha"])
            # PRIME and WORLDLINE's own generations are return points, not candidates.
            self.assertEqual(report["validWorlds"]["needsRevalidation"], [])
            self.assertEqual(report["validWorlds"]["notRevalidatable"], [])
            refreshed = lab.client.request("doctor", {"refresh": True})["promotionReadiness"]
            self.assertEqual(refreshed["foreignWrites"]["state"], "NONE_FOUND")
            self.assertFalse(refreshed["foreignWrites"]["primeDirty"])
            prepared = lab.prepare("alpha")
            pending = lab.client.request("doctor", {})["promotionReadiness"]["pendingTransactions"]
            self.assertEqual(pending, [prepared["transaction_id"]])
            # A VALID world whose declared manifests are gone cannot be revalidated.
            lab.client.request("transaction.abort", {"transactionId": prepared["transaction_id"]})
            self.assertEqual(lab.fork("beta")["state"], "VALID")
            lab.stop()
            store = lab.open_store()
            try:
                beta = store.world("beta")
            finally:
                store.close()
            manifests = Path(beta.payload_path) / "manifests"
            os.chmod(manifests, stat.S_IMODE(manifests.stat().st_mode) | 0o700)
            for item in manifests.iterdir():
                item.unlink()
            lab.start()
            report = lab.client.request("doctor", {})["promotionReadiness"]
            self.assertEqual([(w["alias"], w["missing"]) for w in report["validWorlds"]["notRevalidatable"]], [("beta", ["manifest"])])
        finally:
            lab.close()


class H_RequirementIdentity(unittest.TestCase):
    def test_an_unreadable_resource_policy_is_refused_not_hashed_as_none(self) -> None:
        from worldline.validation import execution_context

        class Broken:
            network_policy, network_allow, readonly_home_paths = "none", (), ()

            @property
            def resource_policy(self) -> Any:
                raise OSError("policy file unreadable")

        with self.assertRaises(WorldlineError) as raised:
            execution_context(Broken())
        self.assertEqual(raised.exception.code, "REQUIREMENT_IDENTITY_UNAVAILABLE")

    def test_an_unconfigured_resource_policy_is_stated_as_none(self) -> None:
        from worldline.validation import execution_context
        self.assertIsNone(execution_context(None)["resourcePolicy"])
        self.assertRegex(execution_context(None)["kernelLibrarySha256"], r"^[0-9a-f]{64}$")


class I_TamperedCandidateRow(_InProcess):
    """Each identity pair has two producers; a store edit that restates one side is caught by the
    other (review of a23c265: base, delta and root set had no end-to-end test)."""

    def restated(self, alias: str, **fields: Any) -> Any:
        world = self.candidate(alias)
        for name, value in fields.items():
            setattr(world, name, value)
        self.store.save_world(world)
        return world

    def test_a_restated_base_is_a_base_mismatch(self) -> None:
        world = self.restated("alpha", base_root=hash_id(bytes([3]) * 32))
        self.denied(lambda: self.transaction.prepare(world.alias), "BASE_MISMATCH")

    def test_a_restated_delta_is_a_delta_mismatch(self) -> None:
        world = self.restated("alpha", delta_hash=hash_id(bytes([4]) * 32))
        self.denied(lambda: self.transaction.prepare(world.alias), "DELTA_MISMATCH")

    def test_a_restated_root_set_is_a_root_set_mismatch(self) -> None:
        world = self.restated("alpha", root_set_hash=hash_id(bytes([5]) * 32))
        self.denied(lambda: self.transaction.prepare(world.alias), "ROOT_SET_MISMATCH")

    def test_missing_declared_manifests_leave_the_tested_root_absent(self) -> None:
        world = self.candidate("alpha")
        manifests = Path(world.payload_path) / "manifests"
        os.chmod(manifests, stat.S_IMODE(manifests.stat().st_mode) | 0o700)
        for item in manifests.iterdir():
            item.unlink()
        error = self.denied(lambda: self.transaction.prepare(world.alias), "STAGED_UNTESTED")
        _path, record = self.record(error.details["transactionId"])
        self.assertIsNone(record["testedRoot"])
        self.assertEqual(record["decisionInputs"]["testedRootSource"], "declared-manifests-missing")

    def test_an_edited_payload_with_its_delta_restated_and_manifests_gone_is_not_tested(self) -> None:
        # The 1.8.0 defect: with write access to the store, delete the declared manifests, edit
        # the payload and restate the row's delta. 1.8.0 re-captured the edited payload as
        # "tested" and committed it; 1.9.0 has no tested root to cover it.
        from worldline.delta import Delta
        from worldline.manifest import Manifest
        world = self.candidate("alpha")
        payload = Path(world.payload_path)
        manifests = payload / "manifests"
        os.chmod(manifests, stat.S_IMODE(manifests.stat().st_mode) | 0o700)
        for item in manifests.iterdir():
            item.unlink()
        target = payload / self.key / "state.txt"
        os.chmod(target.parent, stat.S_IMODE(target.parent.stat().st_mode) | 0o700)
        if target.exists():
            os.chmod(target, stat.S_IMODE(target.stat().st_mode) | 0o600)
        target.write_text("never evaluated", encoding="utf-8")
        root = self.store.roots()[0]
        capture = lambda directory: Manifest.capture(directory, logical_root=bytes(root["path"]), root_key=self.key,
                                                     kind=root["kind"], core=self.core)
        world.delta_hash = Delta.compute_all({self.key: capture(Path(world.base_payload_path) / self.key)},
                                             {self.key: capture(payload / self.key)}, self.core).delta_hash
        self.store.save_world(world)
        self.denied(lambda: self.transaction.prepare(world.alias), "STAGED_UNTESTED")


class _EventWatcher(FakeWatcher):
    """A watcher whose generation moves only when a test says a PRIME event happened."""

    def event(self) -> None:
        self.generation += 1


class J_StabilityWindow(_InProcess):
    """The generation pair spans the requirement read, the capture and merge, and the staged
    evaluation at prepare, and the requirement read through the decision at commit; a PRIME
    event anywhere inside is PRIME_CHANGED, one after the decision is not (review of a23c265:
    a watcher moving on every read could not tell)."""

    def setUp(self) -> None:
        super().setUp()
        self.watcher = _EventWatcher(self.paths, self.store)
        self.transaction.watcher = self.watcher

    def requirement_read_with_event(self):
        import worldline.transaction as module
        real = module.current_requirements

        def during(*args: Any, **kwargs: Any) -> Any:
            self.watcher.event()
            return real(*args, **kwargs)
        return mock.patch.object(module, "current_requirements", during)

    def test_an_event_during_the_requirement_read_at_prepare_is_prime_changed(self) -> None:
        alpha = self.candidate("alpha")
        with self.requirement_read_with_event():
            self.denied(lambda: self.transaction.prepare(alpha.alias), "PRIME_CHANGED", code="PRIME_CHANGED_DURING_CAPTURE")

    def test_an_event_during_the_staged_evaluation_is_prime_changed(self) -> None:
        alpha = self.candidate("alpha")
        self.write_live("other.txt", "moved")
        self.reconciled()
        validate = _staged_validator(self)

        def during(*args: Any) -> dict[str, Any]:
            self.watcher.event()
            return validate(*args)
        self.transaction.validator = during
        self.denied(lambda: self.transaction.prepare(alpha.alias), "PRIME_CHANGED", code="PRIME_CHANGED_DURING_CAPTURE")

    def test_an_event_after_the_prepare_decision_does_not_refuse_it(self) -> None:
        prepared = self.transaction.prepare(self.candidate("alpha").alias)
        self.assertEqual(prepared.decision, "AUTHORIZED")
        self.watcher.event()  # after the decision: the next commit starts a new window

    def test_an_event_during_the_requirement_read_at_commit_is_prime_changed(self) -> None:
        prepared = self.transaction.prepare(self.candidate("alpha").alias)
        with self.requirement_read_with_event():
            self.denied(lambda: self.transaction.commit(prepared.transaction_id), "PRIME_CHANGED", code="PRIME_CHANGED_DURING_CAPTURE")

    def test_an_event_between_the_commit_decision_and_the_exchange_aborts(self) -> None:
        prepared = self.transaction.prepare(self.candidate("alpha").alias)
        real = self.transaction._fsync_payload_tree

        def during(path: Path) -> None:
            real(path)
            self.watcher.event()
        self.transaction._fsync_payload_tree = during
        before, receipts = tree_bytes(self.work), len(self.store.receipts())
        with self.assertRaises(WorldlineError) as raised:
            self.transaction.commit(prepared.transaction_id)
        self.assertEqual(raised.exception.code, "PRIME_CHANGED_DURING_CAPTURE")
        self.assertEqual(self.store.transaction_record(prepared.transaction_id)["state"], "ABORTED")
        self.assertEqual((tree_bytes(self.work), len(self.store.receipts())), (before, receipts))


class K_EvidenceAdmissionRules(_InProcess):
    """The 1.9.0 rules for evidence it writes, driven through the real promotion path."""

    RECORD = {"id": "extra", "format": "exit", "profile": "legacy", "status": "PASS", "origin": "supervisor",
              "exitCode": 0, "resultChannel": {"accepted": True}, "executedVerifierSet": None}

    def setUp(self) -> None:
        super().setUp()
        from freshness_support import EXTRA_CHECK, policy
        self.write_live(".worldline.json", json.dumps(policy(EXTRA_CHECK)))
        self.reconciled()

    def with_record(self, alias: str, record: dict[str, Any]) -> Any:
        world = synthetic_candidate(self.paths, self.store, self.core, alias, {"state.txt": alias})
        world.evidence = {"checks": [record]}
        self.store.save_world(world)
        attach_fresh_context(self.store, world, core=self.core)
        return self.store.world(alias)

    def test_the_stated_record_authorizes(self) -> None:
        self.assertEqual(self.transaction.prepare(self.with_record("good", dict(self.RECORD)).alias).decision, "AUTHORIZED")

    def test_a_policy_record_without_a_profile_is_not_admitted(self) -> None:
        record = {k: v for k, v in self.RECORD.items() if k != "profile"}
        world = self.with_record("unprofiled", record)
        self.denied(lambda: self.transaction.prepare(world.alias), "EXECUTION_EVIDENCE_INCOMPLETE")

    def test_a_record_that_does_not_state_what_executed_is_absent(self) -> None:
        record = {k: v for k, v in self.RECORD.items() if k != "executedVerifierSet"}
        world = self.with_record("unstated", record)
        error = self.denied(lambda: self.transaction.prepare(world.alias), "IDENTITY_ABSENT")
        self.assertIn("executed_verifiers", error.details["absentInputs"])

    def test_a_record_naming_a_bundle_the_check_does_not_declare_does_not_match(self) -> None:
        record = {**self.RECORD, "executedVerifierSet": {"identity": hash_id(bytes([9]) * 32), "stable": True}}
        world = self.with_record("undeclared", record)
        self.denied(lambda: self.transaction.prepare(world.alias), "VERIFIER_EXECUTION_IDENTITY_MISMATCH")

    def test_engine_records_match_by_origin_and_never_with_a_profile(self) -> None:
        from worldline.finalize import ENGINE_DECLARATIONS, _declaration_matches
        agent = {"id": "agent", "format": "exit", "origin": "agent", "status": "PASS"}
        self.assertTrue(_declaration_matches(agent, ENGINE_DECLARATIONS["agent"]))
        self.assertFalse(_declaration_matches({**agent, "profile": "legacy"}, ENGINE_DECLARATIONS["agent"]))
        self.assertFalse(_declaration_matches({**agent, "origin": "supervisor"}, ENGINE_DECLARATIONS["agent"]))


class L_MeasurementProducers(_InProcess):
    def test_every_component_is_compared(self) -> None:
        from types import SimpleNamespace
        from worldline.manifest import Manifest
        live = self.transaction._capture_current_roots()
        components = Manifest.component_roots(live.values(), self.core)
        self.assertEqual(self.transaction._foreign_writes(live, SimpleNamespace(components=components), None)[0], "NONE_FOUND")
        for name in ("filesystem", "config", "repository"):
            with self.subTest(component=name):
                recorded = {**components, name: hash_id(bytes([6]) * 32)}
                state, detail = self.transaction._foreign_writes(live, SimpleNamespace(components=recorded), None)
                self.assertEqual((state, detail["differing"]), ("FOUND", [name]))

    def test_an_unreported_write_after_prepare_is_refused_at_commit(self) -> None:
        prepared = self.transaction.prepare(self.candidate("alpha").alias)
        self.write_live("late.txt", "after the decision, before commit")
        with self.assertRaises(WorldlineError) as raised:
            self.transaction.commit(prepared.transaction_id)
        self.assertEqual(raised.exception.code, "PRIME_CHANGED_AFTER_PREPARE")
        self.assertEqual(self.store.transaction_record(prepared.transaction_id)["state"], "DENIED")

    def test_fork_refuses_without_a_watcher(self) -> None:
        checkpoints = CheckpointManager(self.paths, self.store, core=self.core)
        checkpoints.watcher = None
        with self.assertRaises(WorldlineError) as raised:
            checkpoints.freeze()
        self.assertEqual(raised.exception.code, "PRIME_WATCH_UNAVAILABLE")

    def test_a_write_the_watcher_reported_is_reconciled_not_refused(self) -> None:
        class Reporting(FakeWatcher):
            # The daemon's tracker marks PRIME dirty when the watcher's events are drained.
            def synchronized_generation(inner) -> int:
                if inner.pending:
                    inner.pending = False
                    inner.generation += 1
                    self.store.set_meta("dirty", True)
                return inner.generation
        watcher = Reporting(self.paths, self.store)
        watcher.pending = False
        self.transaction.watcher = watcher
        alpha = self.candidate("alpha")
        self.write_live("reported.txt", "the watcher saw this")
        watcher.pending = True
        self.transaction.validator = _staged_validator(self)
        self.assertEqual(self.transaction.prepare(alpha.alias).decision, "AUTHORIZED")
        kinds = [item["event"].get("kind") for w in self.store.worlds() for item in self.store.causal_events_for_world(w.instance_id)]
        self.assertNotIn("unaccounted-write", kinds)

    def test_a_kernel_library_that_cannot_be_read_is_refused(self) -> None:
        from types import SimpleNamespace
        import worldline.validation as validation
        saved = dict(validation._KERNEL_LIBRARY_CACHE)
        validation._KERNEL_LIBRARY_CACHE.clear()
        try:
            with mock.patch.object(validation.Core, "shared", return_value=SimpleNamespace(library_path="/nonexistent/libworldline_core.so")):
                with self.assertRaises(WorldlineError) as raised:
                    validation.execution_context(None)
            self.assertEqual(raised.exception.code, "REQUIREMENT_IDENTITY_UNAVAILABLE")
        finally:
            validation._KERNEL_LIBRARY_CACHE.clear()
            validation._KERNEL_LIBRARY_CACHE.update(saved)


class M_SymlinkTargets(_InProcess):
    def test_a_retargeted_link_in_prime_is_not_covered_by_evidence_for_the_old_target(self) -> None:
        # Review of a23c265: content roots ignored symlink targets, so a link retargeted in PRIME
        # after the fork left tested == staged and went live with no evaluation.
        live = self.live()
        os.chmod(live, stat.S_IMODE(live.stat().st_mode) | 0o200)
        (live / "v1.txt").write_text("v1", encoding="utf-8")
        (live / "v2.txt").write_text("v2", encoding="utf-8")
        os.symlink("v1.txt", live / "shared.txt")
        self.reconciled()
        alpha = self.candidate("alpha")
        live = self.live()
        os.chmod(live, stat.S_IMODE(live.stat().st_mode) | 0o200)
        (live / "shared.txt").unlink()
        os.symlink("v2.txt", live / "shared.txt")
        self.reconciled()
        error = self.denied(lambda: self.transaction.prepare(alpha.alias), "STAGED_UNTESTED")
        self.assertTrue(any(p.endswith(":shared.txt") for p in error.details["untestedPaths"]), error.details["untestedPaths"])

    def test_content_roots_differ_by_link_target(self) -> None:
        from worldline.manifest import Manifest
        from worldline.validation import content_root_set
        roots = []
        for target in ("x", "y"):
            directory = Path(self.temporary.name) / f"links-{target}"
            directory.mkdir()
            os.symlink(target, directory / "l")
            roots.append(content_root_set({"k": Manifest.capture(directory, logical_root=bytes(directory), root_key="k",
                                                                  kind="filesystem", core=self.core)}, self.core))
        self.assertNotEqual(roots[0], roots[1])


class N_RevalidatedWorlds(unittest.TestCase):
    """Review of a23c265: a revalidation identified what it examined by a capture of the
    read-only finalized payload, so its examined root never equalled the staged tree and every
    collapse of a revalidated world re-ran all checks as a staged evaluation."""

    def test_a_revalidated_world_is_covered_by_its_own_revalidation(self) -> None:
        lab = FreshnessLab(self)
        try:
            lab.init()
            self.assertEqual(lab.fork("alpha")["state"], "VALID")
            self.assertEqual(lab.revalidate("alpha")["outcome"], "PASS")
            prepared = lab.prepare("alpha")
            self.assertEqual(prepared["decision"], "AUTHORIZED")
            self.assertEqual(prepared["tested_root"], prepared["staged_content_root"])
            self.assertIsNone(prepared["staged_validation"])
            self.assertEqual(prepared["untested_paths"], [])
            self.assertEqual(prepared["validation"]["source"].split(":")[0], "revalidation")
            self.assertEqual(lab.commit(prepared["transaction_id"])["state"], "COMMITTED")
        finally:
            lab.close()

    def test_a_payload_whose_modes_differ_from_its_declared_manifest_is_not_revalidated(self) -> None:
        lab = FreshnessLab(self)
        try:
            lab.init()
            self.assertEqual(lab.fork("alpha")["state"], "VALID")
            lab.stop()
            store = lab.open_store()
            try:
                payload = Path(store.world("alpha").payload_path)
                key = store.roots()[0]["root_key"]
            finally:
                store.close()
            target = payload / key / "candidate.txt"
            os.chmod(target, stat.S_IMODE(target.stat().st_mode) | 0o111)  # a mode edit, bytes unchanged
            lab.start()
            self.assertEqual(lab.refusal(lab.revalidate, "alpha").code, "PAYLOAD_INTEGRITY_FAILED")
        finally:
            lab.close()


if __name__ == "__main__":
    unittest.main()
