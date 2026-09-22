"""The assurance instrument must fail when it cannot do its own job.

Three defects were found by inspection rather than by any test, which is the point of this
file: every one of them made the instrument *report success* for work it had not done, and
nothing in the suite objected.

    1. an action step returning {"ok": false} was recorded as a passing step
    2. the evaluation-domain gate would run with no counterexample at all
    3. any non-zero counterexample exit counted as "the defect was detected"

A gate whose failure path is untested is a gate whose failure path does not exist.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import assurance  # noqa: E402
import assurance_contract  # noqa: E402
import evaluation_domain_gate as gate  # noqa: E402
import release_gate  # noqa: E402


# --------------------------------------------------------------------------- defect 1


def _runner(tmp_path: Path) -> assurance.Runner:
    return assurance.Runner(tmp_path)


def test_action_reporting_failure_is_recorded_as_a_failed_step(tmp_path):
    runner = _runner(tmp_path)
    ok = runner.step("explicit-failure", action=lambda: {"ok": False, "reason": "no"})
    assert ok is False
    record = runner.steps[-1]
    assert record["status"] == "failure"
    # exitCode 0 on a failed step reads as success to anything that looks at the number.
    assert record["exitCode"] != 0


def test_action_returning_no_result_is_a_failed_step(tmp_path):
    runner = _runner(tmp_path)
    assert runner.step("no-result", action=lambda: None) is False
    assert runner.steps[-1]["status"] == "failure"
    assert runner.steps[-1]["exitCode"] != 0


def test_action_returning_a_non_result_is_a_failed_step(tmp_path):
    runner = _runner(tmp_path)
    assert runner.step("wrong-type", action=lambda: "fine!") is False
    assert runner.steps[-1]["status"] == "failure"


def test_action_raising_is_a_failed_step_with_a_non_zero_code(tmp_path):
    runner = _runner(tmp_path)

    def explode():
        raise RuntimeError("the gate itself broke")

    assert runner.step("raises", action=explode) is False
    record = runner.steps[-1]
    assert record["status"] == "failure"
    assert record["exitCode"] != 0
    assert "RuntimeError" in record["summary"]["exception"]


def test_an_action_that_succeeds_still_passes(tmp_path):
    runner = _runner(tmp_path)
    assert runner.step("fine", action=lambda: {"ok": True}) is True
    assert runner.steps[-1]["status"] == "success"
    assert runner.steps[-1]["exitCode"] == 0


# --------------------------------------------------------------------------- defect 2


def test_the_gate_refuses_to_run_without_a_counterexample():
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "evaluation_domain_gate.py"), "--engine", str(ROOT / "runtime")],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=60,
    )
    # Exit 2 is argparse refusing a required argument. A traceback would also be non-zero, so
    # asserting only "non-zero" would let this test pass for the wrong reason — which is the
    # same mistake the gate itself was making about the counterexample arm.
    assert proc.returncode == 2, proc.stdout
    assert "Traceback" not in proc.stdout
    assert "counterexample" in proc.stdout.lower()


def test_the_gate_names_the_counterexample_as_required():
    # A default of None would let a caller omit it and still see PASS. The control is not
    # optional: a green candidate proves nothing unless the instrument still fails the
    # known-vulnerable build.
    text = (SCRIPTS / "evaluation_domain_gate.py").read_text(encoding="utf-8")
    assert '"--counterexample", required=True' in text


# --------------------------------------------------------------------------- defect 3


VULNERABLE = {
    "ranAtAll": True,
    "observedVulnerability": {
        "fabricatedOutputAccepted": True,
        "harnessOwnershipMarkers": ["HARNESS-OWNED-subprocess"],
        "trustedExaminerRan": False,
    },
}


def test_the_known_defect_is_accepted_as_detection():
    detected, detail = gate.control_detected(1, VULNERABLE)
    assert detected is True
    assert "trusted examiner ran False" in detail


def test_a_counterexample_that_merely_crashes_is_not_a_detection():
    # An import error, an incompatible library, a missing fixture: all exit non-zero and none
    # of them is evidence that the instrument can still see the vulnerability.
    detected, detail = gate.control_detected(1, {})
    assert detected is False
    assert "crash is not a detection" in detail


def test_a_counterexample_that_ran_but_showed_nothing_is_not_a_detection():
    partial = {"ranAtAll": True, "observedVulnerability": {"trustedExaminerRan": True}}
    detected, _ = gate.control_detected(1, partial)
    assert detected is False


def test_a_counterexample_that_ran_with_no_fingerprints_is_not_a_detection():
    partial = {
        "ranAtAll": True,
        "observedVulnerability": {
            "trustedExaminerRan": False,
            "fabricatedOutputAccepted": False,
            "harnessOwnershipMarkers": [],
        },
    }
    detected, detail = gate.control_detected(1, partial)
    assert detected is False
    assert "neither fabricated output nor harness ownership" in detail


def test_a_counterexample_that_passes_is_not_a_detection():
    detected, detail = gate.control_detected(0, {**VULNERABLE, "allHold": True})
    assert detected is False
    assert "PASSED" in detail


def test_a_candidate_with_no_verdict_does_not_hold():
    # Exit code alone is not the verdict: a harness that dies after printing can still exit 0
    # under a wrapper. The structured result must say so.
    assert gate.candidate_holds(0, {}) is False
    assert gate.candidate_holds(0, {"allHold": False}) is False
    assert gate.candidate_holds(1, {"allHold": True}) is False
    assert gate.candidate_holds(0, {"allHold": True}) is True


# --------------------------------------------------------------------------- one roster


def test_assurance_and_release_gate_share_one_roster():
    # They disagreed: assurance required nine steps, the release gate eight, and the one the
    # release gate did not require was the evaluation-domain gate itself.
    assert assurance.REQUIRED_STEPS is assurance_contract.REQUIRED_STEPS
    assert release_gate.REQUIRED_STEPS is assurance_contract.REQUIRED_STEPS


def test_the_roster_requires_the_evaluation_domain_gate():
    assert "evaluation-domain" in assurance_contract.REQUIRED_STEPS


def test_the_roster_has_no_duplicates():
    assert len(set(assurance_contract.REQUIRED_STEPS)) == len(assurance_contract.REQUIRED_STEPS)


# ------------------------------------------------------- the control's own identity


def test_the_pinned_counterexample_is_accepted():
    assert assurance.check_counterexample_identity(
        assurance_contract.COUNTEREXAMPLE_COMMIT,
        assurance_contract.COUNTEREXAMPLE_RUNTIME_TREE,
    ) is None


def test_a_repointed_counterexample_tag_refuses():
    # The failure this guards: someone re-points the tag at a repaired build, the control arm
    # starts passing, and the gate reports a healthy instrument while measuring nothing.
    refusal = assurance.check_counterexample_identity("0" * 40, assurance_contract.COUNTEREXAMPLE_RUNTIME_TREE)
    assert refusal is not None and refusal["ok"] is False
    assert refusal["counterexampleControl"] == "IDENTITY_MISMATCH"


def test_a_rewritten_counterexample_subtree_refuses():
    refusal = assurance.check_counterexample_identity(assurance_contract.COUNTEREXAMPLE_COMMIT, "0" * 40)
    assert refusal is not None and refusal["ok"] is False


def test_the_pins_are_full_object_ids():
    for pin in (assurance_contract.COUNTEREXAMPLE_COMMIT, assurance_contract.COUNTEREXAMPLE_RUNTIME_TREE):
        assert len(pin) == 40 and all(c in "0123456789abcdef" for c in pin)


def test_ci_provisions_the_counterexample_explicitly():
    # Without this step the CI checkout is shallow and fetches no tags, so the control arm
    # would be unavailable on every run — the gate degrading to one arm in the one place
    # nobody watches it run.
    workflow = (ROOT / ".github/workflows/assurance.yml").read_text(encoding="utf-8")
    assert "COUNTEREXAMPLE_TAG" in workflow
    assert "COUNTEREXAMPLE_COMMIT" in workflow
    assert "COUNTEREXAMPLE_RUNTIME_TREE" in workflow
