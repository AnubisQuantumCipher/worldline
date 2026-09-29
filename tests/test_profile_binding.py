from __future__ import annotations

import unittest

from worldline.core import Core
from worldline.transaction import CollapseTransaction


class EvaluatorProfileBinding(unittest.TestCase):
    def test_promotion_rejects_check_record_from_another_profile(self) -> None:
        manager = object.__new__(CollapseTransaction)
        manager.core = Core.shared()
        current = {"policy": {"requiredChecks": ["exam"], "canonical": {"checks": [
            {"id": "exam", "format": "junit", "profile": "private-evaluator-v1"}
        ]}}, "verifiers": []}
        result = {"id": "exam", "format": "junit", "profile": "legacy",
                  "status": "PASS", "exitCode": 0, "resultChannel": {"accepted": True}}
        identity = manager._execution_identity(None, current, recorded_checks=[result])
        self.assertFalse(identity["complete"])
        self.assertTrue(any("declarationMatches" in problem or "report" in problem
                            for problem in identity["problems"]), identity["problems"])


if __name__ == "__main__":
    unittest.main()
