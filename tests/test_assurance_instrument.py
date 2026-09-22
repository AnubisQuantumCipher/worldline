"""The assurance instrument must fail when it cannot do its own job.

Four defects were found by inspection rather than by any test, which is the point of this file:
every one of them made the instrument *report success* for work it had not done, and nothing in
the suite objected.

    1. an action step returning {"ok": false} was recorded as a passing step
    2. the evaluation-domain gate would run with no counterexample at all
    3. any non-zero counterexample exit counted as "the defect was detected"
    4. assurance.py and release_gate.py kept disagreeing rosters of required steps

A gate whose failure path is untested is a gate whose failure path does not exist.

These are `unittest` cases because assurance runs `python -m unittest discover`. The first
version of this file was written against pytest and imported it, so on a runner without pytest
the module failed to load and every assertion here was silently absent from the gate that
decides whether the branch is releasable. `TheSuiteRunsUnderTheAssuranceRunner` keeps that from
recurring.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import assurance  # noqa: E402
import assurance_contract  # noqa: E402
import evaluation_domain_gate as gate  # noqa: E402
import release_gate  # noqa: E402


# --------------------------------------------------------------------------- defect 1


class ActionFailuresAreRecordedAsFailures(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="assurance-instrument-")
        self.addCleanup(self.temporary.cleanup)
        self.runner = assurance.Runner(Path(self.temporary.name))

    def last(self) -> dict:
        return self.runner.steps[-1]

    def test_an_action_reporting_failure_is_a_failed_step(self) -> None:
        self.assertIs(self.runner.step("explicit-failure", action=lambda: {"ok": False, "reason": "no"}), False)
        self.assertEqual(self.last()["status"], "failure")
        # exitCode 0 on a failed step reads as success to anything that looks at the number.
        self.assertNotEqual(self.last()["exitCode"], 0)

    def test_an_action_returning_no_result_is_a_failed_step(self) -> None:
        self.assertIs(self.runner.step("no-result", action=lambda: None), False)
        self.assertEqual(self.last()["status"], "failure")
        self.assertNotEqual(self.last()["exitCode"], 0)

    def test_an_action_returning_a_non_result_is_a_failed_step(self) -> None:
        self.assertIs(self.runner.step("wrong-type", action=lambda: "fine!"), False)
        self.assertEqual(self.last()["status"], "failure")

    def test_an_action_that_raises_is_a_failed_step_with_a_non_zero_code(self) -> None:
        def explode():
            raise RuntimeError("the gate itself broke")

        self.assertIs(self.runner.step("raises", action=explode), False)
        self.assertEqual(self.last()["status"], "failure")
        self.assertNotEqual(self.last()["exitCode"], 0)
        self.assertIn("RuntimeError", self.last()["summary"]["exception"])

    def test_an_action_that_succeeds_still_passes(self) -> None:
        self.assertIs(self.runner.step("fine", action=lambda: {"ok": True}), True)
        self.assertEqual(self.last()["status"], "success")
        self.assertEqual(self.last()["exitCode"], 0)


# --------------------------------------------------------------------------- defect 2


class TheCounterexampleIsRequired(unittest.TestCase):
    def test_the_gate_refuses_to_run_without_a_counterexample(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "evaluation_domain_gate.py"), "--engine", str(ROOT / "runtime")],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=120,
        )
        # Exit 2 is argparse refusing a required argument. A traceback would also be non-zero, so
        # asserting only "non-zero" would let this pass for the wrong reason — the same mistake
        # the gate itself was making about the counterexample arm.
        self.assertEqual(proc.returncode, 2, proc.stdout)
        self.assertNotIn("Traceback", proc.stdout)
        self.assertIn("counterexample", proc.stdout.lower())

    def test_the_gate_names_the_counterexample_as_required(self) -> None:
        text = (SCRIPTS / "evaluation_domain_gate.py").read_text(encoding="utf-8")
        self.assertIn('"--counterexample", required=True', text)


# --------------------------------------------------------------------------- defect 3


VULNERABLE = {
    "ranAtAll": True,
    "observedVulnerability": {
        "fabricatedOutputAccepted": True,
        "harnessOwnershipMarkers": ["HARNESS-OWNED-subprocess"],
        "trustedExaminerRan": False,
    },
}


class OnlyTheKnownDefectCountsAsDetection(unittest.TestCase):
    def test_the_known_defect_is_accepted(self) -> None:
        detected, detail = gate.control_detected(1, VULNERABLE)
        self.assertIs(detected, True)
        self.assertIn("trusted examiner ran False", detail)

    def test_a_counterexample_that_merely_crashes_is_not_a_detection(self) -> None:
        # An import error, an incompatible library, a missing fixture: all exit non-zero and none
        # of them is evidence that the instrument can still see the vulnerability.
        detected, detail = gate.control_detected(1, {})
        self.assertIs(detected, False)
        self.assertIn("crash is not a detection", detail)

    def test_a_counterexample_that_ran_but_showed_nothing_is_not_a_detection(self) -> None:
        detected, _ = gate.control_detected(1, {"ranAtAll": True, "observedVulnerability": {"trustedExaminerRan": True}})
        self.assertIs(detected, False)

    def test_a_counterexample_with_no_fingerprints_is_not_a_detection(self) -> None:
        partial = {"ranAtAll": True, "observedVulnerability": {
            "trustedExaminerRan": False, "fabricatedOutputAccepted": False, "harnessOwnershipMarkers": []}}
        detected, detail = gate.control_detected(1, partial)
        self.assertIs(detected, False)
        self.assertIn("neither fabricated output nor harness ownership", detail)

    def test_a_counterexample_that_passes_is_not_a_detection(self) -> None:
        detected, detail = gate.control_detected(0, {**VULNERABLE, "allHold": True})
        self.assertIs(detected, False)
        self.assertIn("PASSED", detail)

    def test_a_candidate_with_no_verdict_does_not_hold(self) -> None:
        # Exit code alone is not the verdict: the structured result must say so.
        self.assertIs(gate.candidate_holds(0, {}), False)
        self.assertIs(gate.candidate_holds(0, {"allHold": False}), False)
        self.assertIs(gate.candidate_holds(1, {"allHold": True}), False)
        self.assertIs(gate.candidate_holds(0, {"allHold": True}), True)


# --------------------------------------------------------------------------- defect 4


class OneRoster(unittest.TestCase):
    def test_assurance_and_release_gate_share_one_roster(self) -> None:
        # They disagreed: assurance required nine steps, the release gate eight, and the one the
        # release gate did not require was the evaluation-domain gate itself.
        self.assertIs(assurance.REQUIRED_STEPS, assurance_contract.REQUIRED_STEPS)
        self.assertIs(release_gate.REQUIRED_STEPS, assurance_contract.REQUIRED_STEPS)

    def test_the_roster_requires_the_evaluation_domain_gate(self) -> None:
        self.assertIn("evaluation-domain", assurance_contract.REQUIRED_STEPS)

    def test_the_roster_has_no_duplicates(self) -> None:
        self.assertEqual(len(set(assurance_contract.REQUIRED_STEPS)), len(assurance_contract.REQUIRED_STEPS))


# ------------------------------------------------------- the control's own identity


class TheControlHasAPinnedIdentity(unittest.TestCase):
    def test_the_pinned_counterexample_is_accepted(self) -> None:
        self.assertIsNone(assurance.check_counterexample_identity(
            assurance_contract.COUNTEREXAMPLE_COMMIT, assurance_contract.COUNTEREXAMPLE_RUNTIME_TREE))

    def test_a_repointed_tag_refuses(self) -> None:
        # The failure this guards: someone re-points the tag at a repaired build, the control arm
        # starts passing, and the gate reports a healthy instrument while measuring nothing.
        refusal = assurance.check_counterexample_identity("0" * 40, assurance_contract.COUNTEREXAMPLE_RUNTIME_TREE)
        self.assertIsNotNone(refusal)
        self.assertIs(refusal["ok"], False)
        self.assertEqual(refusal["counterexampleControl"], "IDENTITY_MISMATCH")

    def test_a_rewritten_subtree_refuses(self) -> None:
        refusal = assurance.check_counterexample_identity(assurance_contract.COUNTEREXAMPLE_COMMIT, "0" * 40)
        self.assertIsNotNone(refusal)
        self.assertIs(refusal["ok"], False)

    def test_the_pins_are_full_object_ids(self) -> None:
        for pin in (assurance_contract.COUNTEREXAMPLE_COMMIT, assurance_contract.COUNTEREXAMPLE_RUNTIME_TREE):
            self.assertEqual(len(pin), 40)
            self.assertTrue(all(c in "0123456789abcdef" for c in pin))

    def test_ci_provisions_the_counterexample_explicitly(self) -> None:
        # Without this step the CI checkout is shallow and fetches no tags, so the control arm
        # would be unavailable on every run — the gate degrading to one arm in the one place
        # nobody watches it run.
        workflow = (ROOT / ".github/workflows/assurance.yml").read_text(encoding="utf-8")
        for pin in ("COUNTEREXAMPLE_TAG", "COUNTEREXAMPLE_COMMIT", "COUNTEREXAMPLE_RUNTIME_TREE"):
            self.assertIn(pin, workflow)


# ------------------------------------------------- the suite must run where it is judged


class TheSuiteRunsUnderTheAssuranceRunner(unittest.TestCase):
    """A test module that cannot be imported is not a failing test — it is an absent one.

    Assurance runs `python -m unittest discover`, on a runner that installs no test framework.
    A module importing pytest loads fine locally and vanishes there, taking its assertions out
    of the release decision without failing anything. That is the missing-roster problem in
    another costume, so it gets a check of its own rather than a convention.
    """

    def test_no_test_module_needs_a_third_party_framework(self) -> None:
        offenders = []
        for path in sorted((ROOT / "tests").glob("*.py")):
            text = path.read_text(encoding="utf-8")
            for number, line in enumerate(text.splitlines(), 1):
                stripped = line.strip()
                if stripped.startswith(("import pytest", "from pytest")):
                    offenders.append(f"{path.name}:{number}")
        self.assertEqual(offenders, [], "assurance runs unittest discover, which has no pytest")

    def test_every_test_module_imports_under_the_assurance_runner(self) -> None:
        # Discovery is what assurance actually does; an import error here is what it would hit.
        import unittest.loader

        loader = unittest.loader.TestLoader()
        suite = loader.discover(str(ROOT / "tests"), pattern="test_*.py", top_level_dir=str(ROOT / "tests"))
        self.assertEqual(loader.errors, [], "a test module failed to import under unittest discovery")
        self.assertGreater(suite.countTestCases(), 0)


if __name__ == "__main__":
    unittest.main()
