"""Opt-in end-to-end private report flow through daemon, revalidation and promotion."""
from __future__ import annotations

import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from freshness_support import EXAM_CHECK, FreshnessLab, policy


CHECK = {
    **EXAM_CHECK,
    "format": "junit",
    "profile": "private-evaluator-v1",
    "verifiers": ["evaluator/exam.py"],
}
EXAM = '''from pathlib import Path
ok = Path('candidate.txt').read_text() == 'candidate'
Path('/run/worldline-report/report').write_text(
    '<testsuite tests="1" failures="' + ('0' if ok else '1') + '" errors="0"/>')
raise SystemExit(0 if ok else 1)
'''


@unittest.skipUnless(os.environ.get("WORLDLINE_PRIVATE_EVALUATOR_TEST") == "1",
                     "set WORLDLINE_PRIVATE_EVALUATOR_TEST=1 for host boundary campaign")
class PrivateWorldFlow(unittest.TestCase):
    def test_genuine_private_check_survives_revalidation_and_promotes(self) -> None:
        lab = FreshnessLab(self, policy_value=policy(CHECK), exam=EXAM)
        try:
            lab.init()
            fork = lab.fork("alpha")
            self.assertEqual(fork["state"], "VALID")
            exam = next(item for item in fork["checks"] if item["id"] == "exam")
            self.assertEqual(exam["evaluation"]["reportIntegrity"], "VERIFIED")
            self.assertTrue(exam["evaluation"]["admissibleForPromotion"])
            revalidation = lab.revalidate("alpha")
            self.assertEqual(revalidation["outcome"], "PASS")
            self.assertEqual(revalidation["results"][0]["evaluation"]["reportIntegrity"], "VERIFIED")
            prepared = lab.prepare("alpha")
            self.assertEqual(prepared["decision"], "AUTHORIZED")
            self.assertEqual(lab.commit(prepared["transaction_id"])["state"], "COMMITTED")
            self.assertEqual((lab.work / "candidate.txt").read_text(), "candidate")
        finally:
            lab.close()


if __name__ == "__main__":
    unittest.main()
