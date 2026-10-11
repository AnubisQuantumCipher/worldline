from __future__ import annotations

import unittest

from types import SimpleNamespace

from validation_support import agent_pass_result
from worldline.core import Core
from worldline.finalize import CheckDeclaration, check_declarations
from worldline.transaction import CollapseTransaction


class EvaluatorProfileBinding(unittest.TestCase):
    def test_a_record_whose_only_defect_is_its_profile_is_refused_for_that(self) -> None:
        # An exit-format record: report integrity is not in play, the run completed and
        # passed, and only the evaluator profile differs from what the policy declares.
        manager = object.__new__(CollapseTransaction)
        manager.core = Core.shared()
        subject = SimpleNamespace(evidence={"checks": [agent_pass_result()]})
        declared = {"id": "exam", "format": "exit", "profile": "private-evaluator-v1"}
        current = {"policy": {"requiredChecks": ["exam"], "sourceSha256": "ab" * 32,
                              "canonical": {"checks": [declared], "protected": []}}, "verifiers": []}
        result = {"id": "exam", "format": "exit", "profile": "legacy", "status": "PASS",
                  "origin": "supervisor", "exitCode": 0, "resultChannel": {"accepted": True}}
        identity = manager._execution_identity(subject, current, recorded_checks=[result])
        self.assertFalse(identity["complete"])
        self.assertEqual(identity["problems"], ["exam: evidence incomplete: declarationMatches"])
        # The same record under a policy that declares its profile is admitted.
        matching = {**current, "policy": {**current["policy"], "canonical": {"checks": [{**declared, "profile": "legacy"}], "protected": []}}}
        self.assertTrue(manager._execution_identity(subject, matching, recorded_checks=[result])["complete"])

    def test_check_declarations_reads_the_policy_not_the_record(self) -> None:
        requirement = {"policy": {"canonical": {"checks": [
            {"id": "exam", "format": "junit", "profile": "private-evaluator-v1"},
            {"id": "plain", "format": "exit", "profile": "legacy"},
            {"id": "unstated", "format": "exit"}], "protected": ["secret/**"]}},
            "verifiers": [{"checkId": "exam", "rootKey": "k", "path": "exam.py", "sha256": "x"}]}
        declared = check_declarations(requirement)
        self.assertEqual(declared["exam"], CheckDeclaration("junit", "private-evaluator-v1", True))
        self.assertEqual(declared["plain"], CheckDeclaration("exit", "legacy", False))
        # A check whose profile the policy does not state has no declaration (1.9.0: no default).
        self.assertNotIn("unstated", declared)
        self.assertEqual(declared["protected-paths"], CheckDeclaration("engine", None, False, origin="engine"))
        self.assertNotIn("agent", declared)
        self.assertEqual(check_declarations(None), {})
        self.assertEqual(check_declarations({"policy": "not a mapping"}), {})


if __name__ == "__main__":
    unittest.main()
