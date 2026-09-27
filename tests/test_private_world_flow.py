"""Opt-in end-to-end private report flow through daemon, revalidation and promotion."""
from __future__ import annotations

import os
from pathlib import Path
import stat
import sys
import unittest
import json

from worldline.errors import WorldlineError
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


def fork_failure(lab: FreshnessLab, fork: dict) -> str:
    """Preserve the daemon-owned reason when a hosted integration fork degrades.

    FreshnessLab removes its private root on close, and a bare state assertion loses
    the agent stderr and check refusal that distinguish a sandbox failure from an
    examiner failure. The diagnostic appears only in a failed assertion.
    """
    def read(path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8", errors="replace")[-8192:]
        except OSError as exc:
            return f"unavailable: {exc}"

    agent_stderr = lab.paths.logs / f"{fork['instanceId']}.agent.stderr"
    return json.dumps({
        "forkState": fork["state"],
        "checks": fork["checks"],
        "agentStderr": read(agent_stderr),
        "daemonStderr": read(lab.log),
    }, sort_keys=True, default=str)


@unittest.skipUnless(os.environ.get("WORLDLINE_PRIVATE_EVALUATOR_TEST") == "1",
                     "set WORLDLINE_PRIVATE_EVALUATOR_TEST=1 for host boundary campaign")
class PrivateWorldFlow(unittest.TestCase):
    def test_genuine_private_check_survives_revalidation_and_promotes(self) -> None:
        # The private evaluator deliberately reserves /tmp for its own sandbox.
        # The host's default TMPDIR varies, so place this managed root under HOME.
        lab = FreshnessLab(self, policy_value=policy(CHECK), exam=EXAM,
                           temporary_parent=Path.home())
        try:
            lab.init()
            fork = lab.fork("alpha")
            self.assertEqual(fork["state"], "VALID", fork_failure(lab, fork))
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

    def test_revalidation_refuses_prep_metadata_absent_from_finalized_candidate(self) -> None:
        prep = {"id": "prep", "kind": "build", "argv": ["/usr/bin/chmod", "u+x", "candidate.txt"],
                "required": True, "format": "exit", "covers": ["candidate.txt"]}
        revised = {**CHECK, "argv": ["/usr/bin/python3", "evaluator/mode.py"],
                   "verifiers": ["evaluator/mode.py"]}
        mode_exam = '''import stat
from pathlib import Path
ok = bool(Path('candidate.txt').stat().st_mode & stat.S_IXUSR)
Path('/run/worldline-report/report').write_text(
    '<testsuite tests="1" failures="' + ('0' if ok else '1') + '" errors="0"/>')
raise SystemExit(0 if ok else 1)
'''
        lab = FreshnessLab(self, policy_value=policy(CHECK), exam=EXAM,
                           files={"evaluator/mode.py": mode_exam},
                           temporary_parent=Path.home())
        try:
            lab.init()
            fork = lab.fork("alpha")
            self.assertEqual(fork["state"], "VALID", fork_failure(lab, fork))
            payload = Path(lab.client.request("show", {"world": "alpha"})["payload_path"])
            candidate = next(payload.rglob("candidate.txt"))
            mode_before = stat.S_IMODE(candidate.stat().st_mode)
            self.assertFalse(mode_before & stat.S_IXUSR)
            lab.set_policy(policy(prep, revised))
            lab.settle()
            with self.assertRaises(WorldlineError) as raised:
                lab.revalidate("alpha")
            self.assertEqual(raised.exception.code, "REVALIDATION_INPUT_CHANGED")
            self.assertEqual(stat.S_IMODE(candidate.stat().st_mode), mode_before)
            refused = lab.refusal(lab.prepare, "alpha")
            self.assertEqual(refused.code, "EVIDENCE_STALE")
        finally:
            lab.close()


if __name__ == "__main__":
    unittest.main()
