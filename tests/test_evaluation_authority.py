from __future__ import annotations

import ctypes
from dataclasses import replace
from pathlib import Path
import unittest

from worldline.core import (
    CEvaluationClassification,
    CEvaluationObservations,
    Core,
    EvaluationFacts,
)
from worldline.finalize import evaluation_record


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

    def test_positive_observations_and_explicit_roster(self) -> None:
        classification = self.core.evaluation_classify(self.good_facts())
        self.assertEqual((classification.execution, classification.outcome,
                          classification.bundle), ("COMPLETED", "PASS", "VERIFIED"))
        self.assertTrue(self.core.evaluation_admissible(
            classification, report_integrity="VERIFIED", evidence_complete=True))
        self.assertFalse(self.core.evaluation_admissible(
            classification, report_integrity="VERIFIED", evidence_complete=False))
        self.assertFalse(self.core.evaluation_admissible(
            classification, report_integrity="UNTRUSTED", evidence_complete=True))

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
                    result, report_integrity="VERIFIED", evidence_complete=True))

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
        result.execution = 255
        self.assertEqual(self.core._lib.wl_evaluation_admissible(
            ctypes.byref(result), 1, 1), 255)

    def test_runtime_uses_core_for_unknown_and_not_attempted(self) -> None:
        self.assertFalse(evaluation_record({"status": "UNASSESSED"})["admissibleForPromotion"])
        unknown = evaluation_record({"status": "PASS", "resultChannel": {"accepted": "maybe"}})
        self.assertNotEqual(unknown["executionStatus"], "COMPLETED")
        self.assertFalse(unknown["admissibleForPromotion"])


if __name__ == "__main__":
    unittest.main()
