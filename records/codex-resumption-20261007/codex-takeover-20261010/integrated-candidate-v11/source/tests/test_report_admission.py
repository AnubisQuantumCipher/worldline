"""Actual finalization and revalidation gates for candidate-reachable reports."""
from __future__ import annotations

import unittest

from freshness_support import EXAM_CHECK, FreshnessLab, policy
from worldline.errors import WorldlineError


_JUNIT_CHECK = {**EXAM_CHECK, "format": "junit", "result": "report.xml",
                "covers": ["candidate.txt", "attacker.py"]}
_FORGED_EXAM = '''from pathlib import Path
import subprocess
Path("report.xml").write_text('<testsuite tests="1" failures="1" errors="0" skipped="0"/>')
subprocess.run(["/usr/bin/python3", "attacker.py"], check=True)
'''
_ATTACKER = '''from pathlib import Path
Path("report.xml").write_text('<testsuite tests="1" failures="0" errors="0" skipped="0"/>')
'''


class ReportAdmission(unittest.TestCase):
    def test_replaced_failing_junit_report_cannot_validate_a_world(self) -> None:
        lab = FreshnessLab(self, policy_value=policy(_JUNIT_CHECK), exam=_FORGED_EXAM,
                           files={"attacker.py": _ATTACKER})
        try:
            lab.init()
            world = lab.fork("alpha")
            check = next(item for item in world["checks"] if item["id"] == "exam")
            self.assertEqual(check["status"], "PASS")
            self.assertEqual(check["failures"], 0)
            self.assertEqual(check["evaluation"]["reportIntegrity"], "UNTRUSTED")
            self.assertFalse(check["evaluation"]["admissibleForPromotion"])
            self.assertEqual(world["state"], "DEGRADED")
            with self.assertRaises(WorldlineError) as raised:
                lab.prepare("alpha")
            self.assertEqual(raised.exception.code, "INVALID_CANDIDATE")
        finally:
            lab.close()

if __name__ == "__main__":
    unittest.main()
