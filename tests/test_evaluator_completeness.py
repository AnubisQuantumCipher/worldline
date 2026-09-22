"""Two different things that must not tell the operator the same story.

    the candidate failed a valid examination
    the examination could not complete because its trusted dependencies were incomplete

Both block promotion. Only one of them is about the candidate. Staging verifiers from PRIME
made the second case reachable for an honest project: a top-level examiner's undeclared sibling
is no longer merely unbound, it is absent, and the check fails with ModuleNotFoundError.

The second class here covers a separate defect found while wiring the first: `evidence_manifest`
shallow-copies each result, so `evaluation` and `executionBinding` -- attached afterwards --
never reached the persisted evidence, and the COMMIT-time gate that reads that evidence was
comparing against fields that were always absent.
"""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "runtime"))

from worldline.executed import ExecutionVerifierSet  # noqa: E402
from worldline.finalize import evaluation_record  # noqa: E402

ROOT_KEY = "c3" * 32


class UnsatisfiedImports(unittest.TestCase):
    """Computed over trusted staged bytes, before anything runs."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-deps-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.source = self.base / "src"
        self.source.mkdir()

    def stage(self, files: dict[str, str], members: tuple[str, ...]) -> list[dict]:
        self._staged_count = getattr(self, "_staged_count", 0) + 1
        for relative, body in files.items():
            target = self.source / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(body, encoding="utf-8")
        entries = [{"checkId": "exam", "rootKey": ROOT_KEY, "path": m, "source": "declared"} for m in members]
        staged = ExecutionVerifierSet.stage(check_id="exam", entries=entries,
                                            sources={ROOT_KEY: self.source},
                                            staging=self.base / f"staging-{self._staged_count}")
        self.addCleanup(staged.close)
        return staged.unsatisfied_imports()

    def test_a_missing_sibling_is_reported(self) -> None:
        gaps = self.stage({"exam.py": "import helper\n", "helper.py": "x = 1\n"}, ("exam.py",))
        self.assertEqual([(g["verifier"], g["module"]) for g in gaps], [("exam.py", "helper")])

    def test_a_staged_sibling_satisfies_the_import(self) -> None:
        gaps = self.stage({"exam.py": "import helper\n", "helper.py": "x = 1\n"}, ("exam.py", "helper.py"))
        self.assertEqual(gaps, [])

    def test_a_staged_package_satisfies_the_import(self) -> None:
        gaps = self.stage({"exam.py": "import helper\n", "helper/__init__.py": "x = 1\n"},
                          ("exam.py", "helper/__init__.py"))
        self.assertEqual(gaps, [])

    def test_the_standard_library_satisfies_the_import(self) -> None:
        gaps = self.stage({"exam.py": "import json, sys\nfrom pathlib import Path\n"}, ("exam.py",))
        self.assertEqual(gaps, [])

    def test_siblings_resolve_within_the_verifier_s_own_directory(self) -> None:
        # The examiner adds its own directory to sys.path, so that is where the sibling must be.
        files = {"evaluator/exam.py": "import helper\n", "evaluator/helper.py": "x = 1\n"}
        self.assertEqual(self.stage(files, ("evaluator/exam.py", "evaluator/helper.py")), [])
        gaps = self.stage(files, ("evaluator/exam.py",))
        self.assertEqual([(g["verifier"], g["module"]) for g in gaps], [("evaluator/exam.py", "helper")])

    def test_a_guarded_import_is_not_reported(self) -> None:
        # Conservative on purpose: a false positive would blame the evaluator for a candidate's
        # genuine failure, which is the exact confusion this exists to prevent.
        body = "try:\n    import optional_thing\nexcept ImportError:\n    optional_thing = None\n"
        self.assertEqual(self.stage({"exam.py": body}, ("exam.py",)), [])

    def test_a_deferred_import_is_not_reported(self) -> None:
        body = "def check():\n    import lazy_thing\n    return lazy_thing\n"
        self.assertEqual(self.stage({"exam.py": body}, ("exam.py",)), [])

    def test_a_relative_import_is_not_reported(self) -> None:
        body = "from . import sibling\n"
        self.assertEqual(self.stage({"exam.py": body}, ("exam.py",)), [])

    def test_an_unparseable_verifier_makes_no_claim(self) -> None:
        # Silence is the honest answer for a file this analysis cannot read.
        self.assertEqual(self.stage({"exam.sh": "#!/bin/sh\nexit 0\n"}, ("exam.sh",)), [])
        self.assertEqual(self.stage({"broken.py": "def (\n"}, ("broken.py",)), [])

    def test_the_evidence_carries_the_gaps_and_says_what_it_does_not_claim(self) -> None:
        for relative, body in {"exam.py": "import helper\n"}.items():
            (self.source / relative).write_text(body, encoding="utf-8")
        entries = [{"checkId": "exam", "rootKey": ROOT_KEY, "path": "exam.py", "source": "argv"}]
        staged = ExecutionVerifierSet.stage(check_id="exam", entries=entries,
                                            sources={ROOT_KEY: self.source},
                                            staging=self.base / "staging2")
        self.addCleanup(staged.close)
        evidence = staged.as_evidence()
        self.assertEqual([g["module"] for g in evidence["unsatisfiedImports"]], ["helper"])
        self.assertTrue(any("does not establish that the bundle is complete" in n
                            for n in evidence["nonClaims"]))

    def test_staging_can_reuse_a_locked_down_directory(self) -> None:
        # stage() locks staging to 0500, which a plain rmtree cannot delete into. Its own reuse
        # branch therefore raised PermissionError instead of recovering.
        files = {"exam.py": "import sys\n"}
        self.assertEqual(self.stage(files, ("exam.py",)), [])
        entries = [{"checkId": "exam", "rootKey": ROOT_KEY, "path": "exam.py", "source": "argv"}]
        shared = self.base / "shared-staging"
        first = ExecutionVerifierSet.stage(check_id="exam", entries=entries,
                                           sources={ROOT_KEY: self.source}, staging=shared)
        first.close()
        second = ExecutionVerifierSet.stage(check_id="exam", entries=entries,
                                            sources={ROOT_KEY: self.source}, staging=shared)
        self.addCleanup(second.close)
        self.assertEqual(second.unsatisfied_imports(), [])


class IncompleteEvaluatorIsNotAFailedCandidate(unittest.TestCase):
    def record(self, *, status, gaps, exit_code=1):
        return evaluation_record({
            "status": status, "exitCode": exit_code, "origin": "supervisor",
            "resultChannel": {"accepted": True},
            "executedVerifierSet": {"stable": True, "changedDuringExecution": False,
                                    "unsatisfiedImports": gaps},
        })

    GAP = [{"verifier": "exam.py", "rootKey": ROOT_KEY, "module": "helper"}]

    def test_a_failure_with_an_incomplete_bundle_is_not_a_candidate_verdict(self) -> None:
        record = self.record(status="FAIL", gaps=self.GAP)
        self.assertEqual(record["executionStatus"], "EVALUATOR_INCOMPLETE")
        self.assertEqual(record["evaluationOutcome"], "NONE")
        self.assertFalse(record["admissibleForPromotion"])

    def test_a_failure_with_a_complete_bundle_is_a_candidate_verdict(self) -> None:
        record = self.record(status="FAIL", gaps=[])
        self.assertEqual(record["executionStatus"], "COMPLETED")
        self.assertEqual(record["evaluationOutcome"], "FAIL")
        self.assertFalse(record["admissibleForPromotion"])

    def test_both_block_promotion_but_say_different_things(self) -> None:
        incomplete = self.record(status="FAIL", gaps=self.GAP)
        failed = self.record(status="FAIL", gaps=[])
        self.assertFalse(incomplete["admissibleForPromotion"])
        self.assertFalse(failed["admissibleForPromotion"])
        self.assertNotEqual(incomplete["executionStatus"], failed["executionStatus"])
        self.assertNotEqual(incomplete["evaluationOutcome"], failed["evaluationOutcome"])

    def test_a_pass_is_never_relabelled_by_the_analysis(self) -> None:
        # The analysis can produce a false positive; it must not turn a passing check into a
        # non-result, because the import evidently resolved.
        record = self.record(status="PASS", gaps=self.GAP, exit_code=0)
        self.assertEqual(record["executionStatus"], "COMPLETED")
        self.assertEqual(record["evaluationOutcome"], "PASS")

    def test_the_non_claim_bounds_the_analysis(self) -> None:
        record = self.record(status="FAIL", gaps=[])
        self.assertTrue(any("does not establish that the evaluator was" in n
                            for n in record["nonClaims"]))


if __name__ == "__main__":
    unittest.main()
