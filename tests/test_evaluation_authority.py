"""The evaluation lifecycle authority (1.8.0): classification, per-check admission, the roster,
and the C boundary under them are the proved core's, and the runtime only supplies facts."""
from __future__ import annotations

import ctypes
from dataclasses import replace
from itertools import product
from types import SimpleNamespace
from pathlib import Path
import unittest

from worldline.core import (
    COLLAPSE_DECISIONS,
    ABI_VERSION,
    CCollapseRequest,
    CEvaluationClassification,
    CEvaluationObservations,
    CEvidencePresence,
    Core,
    EVALUATION_EXECUTIONS,
    EvaluationFacts,
    EvidencePresence,
)
from worldline.errors import WorldlineError
from worldline.finalize import CheckDeclaration, evaluation_record, roster_decision
from worldline.transaction import CollapseTransaction

from validation_support import agent_pass_result

FULL = EvidencePresence(True, True, True, True, True)
SUPERVISED_PASS = {"id": "exam", "format": "exit", "profile": "legacy", "status": "PASS", "origin": "supervisor",
                   "exitCode": 0, "resultChannel": {"accepted": True}, "executedVerifierSet": None}
EXIT_DECLARED = CheckDeclaration("exit", "legacy", False)

# Spec section 4, written out independently of the Ada body: the only allowed steps.
ALLOWED = {
    ("NOT_ATTEMPTED", "PREPARED"),
    ("PREPARED", "STARTED"), ("PREPARED", "INTERRUPTED"), ("PREPARED", "ERROR_BEFORE_EXAMINER"),
    ("PREPARED", "INCOMPLETE_UNKNOWN"), ("PREPARED", "UNCLASSIFIED"),
    ("STARTED", "COMPLETED"), ("STARTED", "INTERRUPTED"), ("STARTED", "INCOMPLETE_UNKNOWN"),
    ("STARTED", "EVALUATOR_INCOMPLETE"), ("STARTED", "UNCLASSIFIED"),
}


class EvaluationAuthorityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.core = Core(Path(__file__).resolve().parents[1] / "lib/libworldline_core.so")

    def good_facts(self) -> EvaluationFacts:
        return EvaluationFacts(
            source="external", status="PASS", channel="ACCEPTED", stage="ABSENT",
            exit_present=True, exit_integer=True, supervisor="ABSENT",
            supervisor_stopped=False, bundle_present=True, bundle_is_mapping=True,
            bundle_stable=True, bundle_changed=False, unsatisfied_imports=False,
        )

    def test_positive_observations_and_typed_presence(self) -> None:
        classification = self.core.evaluation_classify(self.good_facts())
        self.assertEqual((classification.execution, classification.outcome,
                          classification.bundle), ("COMPLETED", "PASS", "VERIFIED"))
        self.assertTrue(self.core.evaluation_admissible(
            classification, report_integrity="VERIFIED", presence=FULL))
        for field in EvidencePresence.__slots__:
            with self.subTest(missing=field):
                self.assertFalse(self.core.evaluation_admissible(
                    classification, report_integrity="VERIFIED", presence=replace(FULL, **{field: False})))
        self.assertFalse(self.core.evaluation_admissible(
            classification, report_integrity="UNTRUSTED", presence=FULL))

    def test_presence_must_be_typed_facts_not_truthy_values(self) -> None:
        classification = self.core.evaluation_classify(self.good_facts())
        for value in (1, "yes", None, {"x": 1}):
            with self.subTest(value=value), self.assertRaises(WorldlineError):
                self.core.evaluation_admissible(classification, report_integrity="VERIFIED",
                                                presence=replace(FULL, record_identified=value))
        with self.assertRaises(WorldlineError):
            self.core.evaluation_admissible(classification, report_integrity="VERIFIED", presence=True)

    def test_missing_exit_and_malformed_channel_never_complete(self) -> None:
        for facts in (
            replace(self.good_facts(), exit_present=False, exit_integer=False),
            replace(self.good_facts(), channel="MALFORMED"),
            replace(self.good_facts(), status="OTHER"),
            replace(self.good_facts(), unsatisfied_imports=True, status="FAIL"),
        ):
            with self.subTest(facts=facts):
                result = self.core.evaluation_classify(facts)
                self.assertNotEqual(result.execution, "COMPLETED")
                self.assertFalse(self.core.evaluation_admissible(
                    result, report_integrity="VERIFIED", presence=FULL))

    def test_unsatisfied_imports_relabel_a_failure_but_not_a_pass(self) -> None:
        # A FAIL from an examiner that could not load its own helpers is not a verdict on the
        # candidate. A PASS resolved its imports; the analysis cannot tell a missing helper from
        # the module under test, so a PASS stays a completed pass (decision D1).
        failed = self.core.evaluation_classify(replace(self.good_facts(), unsatisfied_imports=True, status="FAIL"))
        self.assertEqual((failed.execution, failed.outcome), ("EVALUATOR_INCOMPLETE", "NONE"))
        passed = self.core.evaluation_classify(replace(self.good_facts(), unsatisfied_imports=True))
        self.assertEqual((passed.execution, passed.outcome), ("COMPLETED", "PASS"))

    def test_every_non_completed_state_and_a_completed_fail_are_refused(self) -> None:
        cases = {
            "NOT_ATTEMPTED": {**SUPERVISED_PASS, "status": "UNASSESSED"},
            "INTERRUPTED": {**SUPERVISED_PASS, "resultChannel": {"accepted": False, "stage": "STOPPED_BY_MANAGER"}},
            "ERROR_BEFORE_EXAMINER": {**SUPERVISED_PASS, "resultChannel": {"accepted": False, "stage": "SANDBOX_NEVER_STARTED"}},
            "INCOMPLETE_UNKNOWN": {"id": "exam", "format": "exit", "status": "PASS", "origin": "supervisor"},
            "EVALUATOR_INCOMPLETE": {**SUPERVISED_PASS, "status": "FAIL", "exitCode": 1, "executedVerifierSet": {
                "identity": "sha256:" + "11" * 32, "stable": True, "unsatisfiedImports": [{"module": "helper"}]}},
            "UNCLASSIFIED": {**SUPERVISED_PASS, "resultChannel": "not a mapping"},
        }
        for expected, record in cases.items():
            with self.subTest(state=expected):
                declared = CheckDeclaration("exit", "legacy", "executedVerifierSet" in record)
                value = evaluation_record(record, declared=declared)
                self.assertEqual(value["executionStatus"], expected)
                self.assertFalse(value["admissibleForPromotion"])
        failed = evaluation_record({**SUPERVISED_PASS, "status": "FAIL", "exitCode": 1}, declared=EXIT_DECLARED)
        self.assertEqual((failed["executionStatus"], failed["evaluationOutcome"]), ("COMPLETED", "FAIL"))
        self.assertFalse(failed["admissibleForPromotion"])

    def test_boolean_exit_and_empty_bundle_do_not_authorize_promotion(self) -> None:
        valid = evaluation_record(SUPERVISED_PASS, declared=EXIT_DECLARED)
        self.assertEqual(valid["executionStatus"], "COMPLETED")
        self.assertTrue(valid["admissibleForPromotion"])
        boolean_exit = evaluation_record({**SUPERVISED_PASS, "exitCode": True}, declared=EXIT_DECLARED)
        self.assertNotEqual(boolean_exit["executionStatus"], "COMPLETED")
        self.assertFalse(boolean_exit["admissibleForPromotion"])
        empty_bundle = evaluation_record({**SUPERVISED_PASS, "executedVerifierSet": {}}, declared=EXIT_DECLARED)
        self.assertEqual(empty_bundle["bundleIntegrity"], "COMPROMISED")
        self.assertFalse(empty_bundle["admissibleForPromotion"])

    def test_the_declaration_comes_from_the_policy_not_the_record(self) -> None:
        self.assertFalse(evaluation_record(SUPERVISED_PASS, declared=None)["admissibleForPromotion"])
        self.assertFalse(evaluation_record(SUPERVISED_PASS, declared=CheckDeclaration("junit", "legacy", False))["admissibleForPromotion"])
        self.assertFalse(evaluation_record(SUPERVISED_PASS, declared=CheckDeclaration("exit", "private-evaluator-v1", False))["admissibleForPromotion"])
        # A declared bundle must be named as what executed.
        unnamed = evaluation_record(SUPERVISED_PASS, declared=CheckDeclaration("exit", "legacy", True))
        self.assertFalse(unnamed["evidencePresence"]["bundleIdentified"])
        self.assertFalse(unnamed["admissibleForPromotion"])
        missing_id = evaluation_record({k: v for k, v in SUPERVISED_PASS.items() if k != "id"}, declared=EXIT_DECLARED)
        self.assertFalse(missing_id["evidencePresence"]["recordIdentified"])
        self.assertFalse(missing_id["admissibleForPromotion"])

    def test_the_roster_is_the_kernels_and_an_empty_one_must_be_declared(self) -> None:
        self.assertFalse(self.core.evaluation_roster_complete([], empty_declared=False))
        self.assertTrue(self.core.evaluation_roster_complete([], empty_declared=True))
        self.assertFalse(self.core.evaluation_roster_complete([True, False], empty_declared=True))
        self.assertTrue(self.core.evaluation_roster_complete([True, True], empty_declared=False))
        with self.assertRaises(WorldlineError):
            self.core.evaluation_roster_complete([1], empty_declared=False)
        declarations = {"exam": EXIT_DECLARED}
        present = roster_decision(["exam"], {"exam": SUPERVISED_PASS}, declarations, empty_declared=False, core=self.core)
        self.assertTrue(present["complete"])
        absent = roster_decision(["exam"], {}, declarations, empty_declared=True, core=self.core)
        self.assertFalse(absent["complete"])
        self.assertEqual(absent["refused"], [{"id": "exam", "reason": "no execution record"}])
        # A saved classification is not authority: a forged "admissible" evaluation on a record
        # whose raw facts say otherwise is recomputed and refused.
        forged = {**SUPERVISED_PASS, "status": "FAIL", "evaluation": {"admissibleForPromotion": True, "executionStatus": "COMPLETED"}}
        self.assertFalse(roster_decision(["exam"], {"exam": forged}, declarations, empty_declared=False, core=self.core)["complete"])

    def test_the_lifecycle_export_is_the_spec_relation(self) -> None:
        for source, target in product(EVALUATION_EXECUTIONS, repeat=2):
            with self.subTest(source=source, target=target):
                self.assertEqual(self.core.evaluation_transition_allowed(source, target),
                                 (source, target) in ALLOWED)
        state = "NOT_ATTEMPTED"
        for step in ("COMPLETED", "PREPARED", "COMPLETED", "STARTED", "COMPLETED", "STARTED"):
            state = self.core.evaluation_advance(state, step)
        self.assertEqual(state, "COMPLETED")

    def test_c_boundary_rejects_invalid_enum_and_boolean_codes(self) -> None:
        raw = CEvaluationObservations(2, 1, 2, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0)
        result = CEvaluationClassification()
        self.assertEqual(self.core._lib.wl_evaluation_classify(
            ctypes.byref(raw), ctypes.byref(result)), 0)
        raw.status = 255
        self.assertEqual(self.core._lib.wl_evaluation_classify(
            ctypes.byref(raw), ctypes.byref(result)), 255)
        raw.status = 1
        raw.exit_present = 2
        self.assertEqual(self.core._lib.wl_evaluation_classify(
            ctypes.byref(raw), ctypes.byref(result)), 255)
        raw.exit_present = 0
        self.assertEqual(self.core._lib.wl_evaluation_classify(
            ctypes.byref(raw), ctypes.byref(result)), 255)
        self.assertEqual(self.core._lib.wl_evaluation_classify(None, ctypes.byref(result)), 255)
        presence = CEvidencePresence(1, 1, 1, 1, 1)
        for execution, outcome, expected in ((8, 1, 1), (255, 1, 255), (8, 0, 255), (7, 1, 255)):
            with self.subTest(execution=execution, outcome=outcome):
                value = CEvaluationClassification(execution, outcome, 1)
                self.assertEqual(self.core._lib.wl_evaluation_admissible(
                    ctypes.byref(value), 1, ctypes.byref(presence)), expected)
        presence.declaration_matches = 2
        value = CEvaluationClassification(8, 1, 1)
        self.assertEqual(self.core._lib.wl_evaluation_admissible(ctypes.byref(value), 1, ctypes.byref(presence)), 255)
        self.assertEqual(self.core._lib.wl_evaluation_admissible(ctypes.byref(value), 1, None), 255)
        self.assertEqual(self.core._lib.wl_evaluation_transition_allowed(9, 0), 255)
        self.assertEqual(self.core._lib.wl_evaluation_roster_complete(None, 1, 1), 255)
        self.assertEqual(self.core._lib.wl_evaluation_roster_complete(None, 0, 2), 255)
        too_many = (ctypes.c_uint8 * 4097)(*([1] * 4097))
        self.assertEqual(self.core._lib.wl_evaluation_roster_complete(too_many, 4097, 0), 255)

    def test_collapse_request_wire_encodings_are_validated(self) -> None:
        # ABI generation 5: every Boolean and enum byte in range, every presence byte 0 or 1, an
        # absent value all zero, a present hash never all zero, and no value in a slot the
        # request's mode or phase does not consult. Anything else is 255, never a decision.
        values = {"expected_parent": 1, "candidate_parent": 1, "expected_subject": 2, "evidence_subject": 2,
                  "expected_base": 3, "candidate_base": 3, "expected_delta": 4, "candidate_delta": 4,
                  "expected_root_set": 5, "candidate_root_set": 5, "expected_staged_root": 6,
                  "actual_staged_root": 6, "staged_content_root": 7, "tested_root": 7,
                  "current_requirement": 8, "evaluated_requirement": 8, "declared_verifiers": 9,
                  "executed_verifiers": 9, "registered_watch_set": 10, "watched_set": 10}

        def put(field, byte: int) -> None:
            field.present = 1
            field.value = (ctypes.c_uint8 * 32)(*([byte] * 32))

        def request(**overrides) -> CCollapseRequest:
            value = CCollapseRequest()
            value.candidate_state, value.phase, value.evaluation_mode = 2, 0, 0
            value.conflicts, value.foreign_writes, value.roster_complete = 1, 1, 1
            for name, byte in values.items():
                put(getattr(value, name), byte)
            for name in ("generation_before", "generation_after"):
                getattr(value, name).present = 1
                getattr(value, name).value_le[0] = 41
            for name, change in overrides.items():
                change(value)
            return value

        self.assertEqual(self.core._lib.wl_collapse_decide(ctypes.byref(request())), 0)
        malformed = {
            "presence byte 2": lambda r: setattr(r.expected_parent, "present", 2),
            "absent with a value": lambda r: (setattr(r.expected_parent, "present", 0)),
            "present all-zero hash": lambda r: setattr(r.tested_root, "value", (ctypes.c_uint8 * 32)()),
            "absent counter with bytes": lambda r: setattr(r.generation_before, "present", 0),
            "candidate state": lambda r: setattr(r, "candidate_state", 7),
            "phase": lambda r: setattr(r, "phase", 2),
            "mode": lambda r: setattr(r, "evaluation_mode", 2),
            "conflicts": lambda r: setattr(r, "conflicts", 3),
            "foreign writes": lambda r: setattr(r, "foreign_writes", 3),
            "roster byte": lambda r: setattr(r, "roster_complete", 2),
            "prepare with a second capture": lambda r: setattr(r, "phase", 1),
            "checkpoint field in candidate mode": lambda r: put(r.witnessed_checkpoint, 20),
            "checkpoint mode with primary evidence": lambda r: setattr(r, "evaluation_mode", 1),
        }
        for label, change in malformed.items():
            with self.subTest(malformed=label):
                self.assertEqual(self.core._lib.wl_collapse_decide(ctypes.byref(request(change=change))), 255)
        self.assertEqual(self.core._lib.wl_collapse_decide(None), 255)

        # Each slot a mode ignores must be empty on its own (review of a23c265: the combined
        # case above could not tell which conjunct refused).
        def clear(field) -> None:
            field.present = 0
            field.value = (ctypes.c_uint8 * 32)()

        def checkpoint(r) -> None:
            r.evaluation_mode, r.roster_complete = 1, 0
            clear(r.evaluated_requirement)
            clear(r.executed_verifiers)
            put(r.expected_checkpoint, 21)
            put(r.witnessed_checkpoint, 21)

        decide = lambda value: self.core._lib.wl_collapse_decide(ctypes.byref(value))
        self.assertEqual(decide(request(mode=checkpoint)), 0)
        singles = {
            "expected checkpoint alone in candidate mode": lambda r: put(r.expected_checkpoint, 21),
            "evaluated requirement alone in checkpoint mode": lambda r: (checkpoint(r), put(r.evaluated_requirement, 8)),
            "executed verifiers alone in checkpoint mode": lambda r: (checkpoint(r), put(r.executed_verifiers, 9)),
            "roster byte alone in checkpoint mode": lambda r: (checkpoint(r), setattr(r, "roster_complete", 1)),
        }
        for label, change in singles.items():
            with self.subTest(ignored_slot=label):
                self.assertEqual(decide(request(change=change)), 255)

        # Counters are little-endian 64-bit: a difference in any byte is a different generation.
        def counters(before: int, after: int):
            def change(r) -> None:
                r.generation_before.value_le = (ctypes.c_uint8 * 8)(*before.to_bytes(8, "little"))
                r.generation_after.value_le = (ctypes.c_uint8 * 8)(*after.to_bytes(8, "little"))
            return change
        prime_changed = next(code for code, name in COLLAPSE_DECISIONS.items() if name == "PRIME_CHANGED")
        for before, after in ((0, 1 << 8), (0, 1 << 56), (1 << 56, 1 << 57), ((1 << 64) - 1, (1 << 64) - 2)):
            with self.subTest(before=before, after=after):
                self.assertEqual(decide(request(change=counters(before, after))), prime_changed)
        self.assertEqual(decide(request(change=counters((1 << 56) + 257, (1 << 56) + 257))), 0)

    def test_the_library_is_the_abi_generation_this_runtime_expects(self) -> None:
        self.assertEqual(self.core._lib.wl_abi_version(), ABI_VERSION)
        for selector, structure in ((0, CCollapseRequest), (1, CEvaluationObservations),
                                    (2, CEvaluationClassification), (3, CEvidencePresence)):
            self.assertEqual(self.core._lib.wl_layout_size(selector), ctypes.sizeof(structure))
        self.assertEqual(self.core._lib.wl_layout_size(9), 0)

    def test_promotion_recomputes_and_refuses_what_1_7_3_let_through(self) -> None:
        manager = object.__new__(CollapseTransaction)
        manager.core = self.core
        subject = SimpleNamespace(evidence={"checks": [agent_pass_result()]})
        current = {"policy": {"requiredChecks": ["exam"], "sourceSha256": "ab" * 32, "canonical": {
            "checks": [{"id": "exam", "format": "exit", "profile": "legacy"}], "protected": []}}, "verifiers": []}
        self.assertTrue(manager._execution_identity(subject, current, recorded_checks=[SUPERVISED_PASS])["complete"])
        # A completed FAIL: 1.7.3 checked only that execution reached the examiner.
        completed_fail = {**SUPERVISED_PASS, "status": "FAIL", "exitCode": 1}
        self.assertFalse(manager._execution_identity(subject, current, recorded_checks=[completed_fail])["complete"])
        # A record with no classifiable execution: 1.7.3 accepted a missing executionStatus.
        bare = {"id": "exam", "format": "exit", "status": "PASS"}
        self.assertFalse(manager._execution_identity(subject, current, recorded_checks=[bare])["complete"])
        # An empty roster: declared by a policy file, or not declared at all.
        empty = {"policy": {"requiredChecks": [], "sourceSha256": "ab" * 32, "canonical": {"checks": [], "protected": []}}, "verifiers": []}
        self.assertTrue(manager._execution_identity(subject, empty, recorded_checks=[])["complete"])
        undeclared = {"policy": {"requiredChecks": [], "sourceSha256": None, "canonical": {"checks": [], "protected": []}}, "verifiers": []}
        identity = manager._execution_identity(subject, undeclared, recorded_checks=[])
        self.assertFalse(identity["complete"])
        self.assertTrue(identity["problems"])
        # Protected paths are on the promotion roster whenever the policy protects anything.
        protected = {"policy": {"requiredChecks": [], "sourceSha256": "ab" * 32, "canonical": {"checks": [], "protected": ["secret/**"]}}, "verifiers": []}
        self.assertFalse(manager._execution_identity(subject, protected, recorded_checks=[])["complete"])
        touched = {"id": "protected-paths", "format": "engine", "origin": "engine", "status": "FAIL"}
        self.assertFalse(manager._execution_identity(subject, protected, recorded_checks=[touched])["complete"])
        self.assertTrue(manager._execution_identity(subject, protected, recorded_checks=[{**touched, "status": "PASS"}])["complete"])

    def test_the_agents_own_exit_is_on_every_promotion_roster(self) -> None:
        # PB-1: a world DEGRADED by its agent's failure becomes ARCHIVED when a sibling
        # collapses; `return` must still judge the agent from the finalization record.
        manager = object.__new__(CollapseTransaction)
        manager.core = self.core
        current = {"policy": {"requiredChecks": [], "sourceSha256": "ab" * 32, "canonical": {"checks": [], "protected": []}}, "verifiers": []}
        ok = SimpleNamespace(evidence={"checks": [agent_pass_result()]})
        self.assertTrue(manager._execution_identity(ok, current, recorded_checks=[])["complete"])
        for label, evidence in (("failed", {"checks": [{**agent_pass_result(), "status": "FAIL", "exitCode": 1}]}),
                                ("stopped", {"checks": [{**agent_pass_result(), "supervision": {"kind": "SUPERVISED", "stoppedByManager": True}}]}),
                                ("missing", {"checks": []}), ("no evidence", None)):
            with self.subTest(agent=label):
                identity = manager._execution_identity(SimpleNamespace(evidence=evidence), current, recorded_checks=[])
                self.assertFalse(identity["complete"])
                self.assertTrue(any(problem.startswith("agent:") for problem in identity["problems"]), identity["problems"])
        # A world forked before 1.5.0: the runner wrote no `origin`. Recognised by its exact
        # shape and still judged by the kernel (a failed or stopped legacy agent is refused).
        legacy = {k: v for k, v in agent_pass_result().items() if k != "origin"}
        legacy.update({"argv": ["agent"], "rawEventHash": "sha256:" + "00" * 32, "stderrHash": "sha256:" + "00" * 32})
        identity = manager._execution_identity(SimpleNamespace(evidence={"checks": [legacy]}), current, recorded_checks=[])
        self.assertTrue(identity["complete"], identity["problems"])
        self.assertTrue(identity["legacyAgentRecord"])
        for label, variant in (("failed", {**legacy, "status": "FAIL", "exitCode": 1}),
                               ("stopped", {**legacy, "supervision": {"kind": "STOPPED"}}),
                               ("channel", {**legacy, "resultChannel": {"accepted": True}}),
                               ("no event hash", {k: v for k, v in legacy.items() if k != "rawEventHash"})):
            with self.subTest(legacy=label):
                self.assertFalse(manager._execution_identity(SimpleNamespace(evidence={"checks": [variant]}), current, recorded_checks=[])["complete"])
        # A revalidation's records cannot stand in for it: they never carry the agent.
        failed = SimpleNamespace(evidence={"checks": [{**agent_pass_result(), "status": "FAIL", "exitCode": 1}]})
        self.assertFalse(manager._execution_identity(failed, current, recorded_checks=[agent_pass_result()])["complete"])


if __name__ == "__main__":
    unittest.main()
