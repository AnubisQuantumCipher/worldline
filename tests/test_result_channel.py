"""Who is allowed to say what a check concluded.

Isolating the harness's imports closed the route to OWNING the harness. It left open the
simpler one: the record used to be a file in /run/worldline-runtime, which is bind-mounted
read-write as the world's XDG_RUNTIME_DIR, so the processes under examination could write the
document that reported on them.

A secret would not have fixed it. The examiner's children run as the same user in the same PID
namespace, so anything passed in argv, the environment or the spec is readable through procfs —
and, as `CandidateCannotForgeTheRecord` demonstrates by doing it, so is the harness's own
stdout. What the candidate cannot do is make the stream contain exactly one frame while the
service manager reports an exit status that agrees with it.

The tests that launch real sandboxes are marked in their names. They are the ones that matter:
the rest check that the parsing and classification cannot be talked out of a refusal.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "runtime"))

from worldline.admission import AdmissionAuthority, Floors, Gate, Ledger, ResourcePolicy  # noqa: E402
from worldline.checks import (  # noqa: E402
    RECORD_MARKER,
    CheckRunner,
    expected_unit_exit,
    parse_record_stream,
)
from worldline.finalize import evaluation_record  # noqa: E402
from worldline.linux.namespaces import BubblewrapSandbox, OverlayRoot  # noqa: E402
from worldline.linux.systemd import SystemdAdapter  # noqa: E402
from worldline.paths import WorldlinePaths  # noqa: E402
from worldline.project import CheckSpec  # noqa: E402

ROOT_KEY = "a1" * 32
LOGICAL = "/logical/root"


def _frame(**fields) -> bytes:
    record = {"schemaVersion": 2, "exitCode": 0, "durationNs": 1,
              "stdoutB64": "", "stderrB64": "", "resultB64": None, **fields}
    return (RECORD_MARKER + json.dumps(record, sort_keys=True, separators=(",", ":")) + RECORD_MARKER).encode()


class TheFrameMustBeAttributable(unittest.TestCase):
    def test_a_clean_frame_parses(self) -> None:
        record, error = parse_record_stream(_frame())
        self.assertIsNone(error)
        self.assertEqual(record["exitCode"], 0)

    def test_an_empty_stream_is_not_a_result(self) -> None:
        _, error = parse_record_stream(b"")
        self.assertIn("no result record", error)

    def test_bytes_before_the_frame_refuse(self) -> None:
        _, error = parse_record_stream(b"anything at all" + _frame())
        self.assertIn("more than the harness", error)

    def test_bytes_after_the_frame_refuse(self) -> None:
        _, error = parse_record_stream(_frame() + b"trailing")
        self.assertIn("more than the harness", error)

    def test_a_second_frame_refuses(self) -> None:
        # A candidate that adds its own frame cannot remove the harness's.
        _, error = parse_record_stream(_frame(exitCode=0) + _frame(exitCode=0))
        self.assertIn("cannot be attributed", error)

    def test_an_unparseable_frame_refuses(self) -> None:
        _, error = parse_record_stream(RECORD_MARKER.encode() + b"{not json" + RECORD_MARKER.encode())
        self.assertIn("not valid JSON", error)

    def test_a_foreign_schema_refuses(self) -> None:
        _, error = parse_record_stream(_frame(schemaVersion=1))
        self.assertIn("expected schema", error)

    def test_the_exit_mapping_is_the_shell_convention(self) -> None:
        self.assertEqual(expected_unit_exit(0), 0)
        self.assertEqual(expected_unit_exit(3), 3)
        self.assertEqual(expected_unit_exit(-9), 137)   # SIGKILL
        self.assertEqual(expected_unit_exit(-15), 143)  # SIGTERM


class IncompleteIsNotFailed(unittest.TestCase):
    """A check that did not complete is not a check that failed, and neither is promotable."""

    def _record(self, **result):
        return evaluation_record({"executedVerifierSet": {"stable": True, "changedDuringExecution": False}, **result})

    def test_a_refused_channel_is_never_admissible(self) -> None:
        for stage in ("NO_ATTRIBUTABLE_RECORD", "CHANNEL_DISAGREEMENT", "UNCORROBORATED",
                      "RECORD_MALFORMED", "HARNESS_SIGNALLED", "STOPPED_BY_MANAGER"):
            with self.subTest(stage=stage):
                record = self._record(status="FAIL", resultChannel={"accepted": False, "stage": stage})
                self.assertFalse(record["admissibleForPromotion"])
                self.assertNotEqual(record["executionStatus"], "COMPLETED")
                self.assertEqual(record["evaluationOutcome"], "NONE")

    def test_an_unattributable_record_does_not_claim_a_stage_it_cannot_know(self) -> None:
        # ERROR_BEFORE_EXAMINER asserts which side of the examiner execution stopped on. When no
        # record arrived, nothing trusted establishes that.
        record = self._record(status="FAIL", resultChannel={"accepted": False, "stage": "NO_ATTRIBUTABLE_RECORD"})
        self.assertEqual(record["executionStatus"], "INCOMPLETE_UNKNOWN")

    def test_a_sandbox_that_never_started_did_stop_before_the_examiner(self) -> None:
        record = self._record(status="FAIL", resultChannel={"accepted": False, "stage": "SANDBOX_NEVER_STARTED"})
        self.assertEqual(record["executionStatus"], "ERROR_BEFORE_EXAMINER")

    def test_an_engine_evaluated_check_declares_its_origin(self) -> None:
        # This used to be inferred from "a status is present and an exit code is not", which is
        # also what a subverted harness looks like.
        record = evaluation_record({"origin": "engine", "status": "PASS", "format": "engine"})
        self.assertEqual(record["executionStatus"], "COMPLETED")
        self.assertTrue(record["admissibleForPromotion"])

    def test_a_missing_origin_is_not_promoted_to_engine(self) -> None:
        record = evaluation_record({"status": "PASS", "executedVerifierSet": {"stable": True}})
        self.assertNotEqual(record["executionStatus"], "COMPLETED")
        self.assertFalse(record["admissibleForPromotion"])


class CandidateCannotForgeTheRecord(unittest.TestCase):
    """Real sandboxes, real attacks, run by the real CheckRunner."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-channel-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        environment = dict(os.environ,
                           XDG_STATE_HOME=str(self.base / "state"), XDG_DATA_HOME=str(self.base / "data"),
                           XDG_RUNTIME_DIR=str(self.base / "run"), XDG_CONFIG_HOME=str(self.base / "cfg"))
        for name in ("state", "data", "run", "cfg"):
            (self.base / name).mkdir(parents=True, exist_ok=True)
        self.paths = WorldlinePaths.from_environment(environment)
        self.paths.ensure()
        self.lower = self.base / "lower"
        (self.lower / "exam").mkdir(parents=True)
        self.upper = self.base / "upper"
        self.upper.mkdir()
        self.work = self.base / "work"
        self.work.mkdir()
        self.overlay = OverlayRoot(root_key=ROOT_KEY, lower=self.lower, upper=self.upper,
                                   work=self.work, target=Path(LOGICAL))
        gate = Gate(AdmissionAuthority(Ledger(self.paths.runtime), Floors()), ResourcePolicy.from_mapping({}))
        self.runner = CheckRunner(self.paths, BubblewrapSandbox(self.paths), SystemdAdapter(), gate)

    def run_examiner(self, body: str) -> dict:
        (self.lower / "exam" / "run.py").write_text(body, encoding="utf-8")
        check = CheckSpec("exam", "tests", ("/usr/bin/python3", f"{LOGICAL}/exam/run.py"),
                          None, True, "exit", None, (), ())
        entries = [{"checkId": "exam", "rootKey": ROOT_KEY, "path": "exam/run.py", "source": "argv"}]
        return self.runner.run(world_instance=str(uuid.uuid4()), overlays=[self.overlay],
                               primary_target=Path(LOGICAL), checks=[check],
                               verifiers=entries, logical_roots={ROOT_KEY: LOGICAL})[0]

    FORGE = """
import os, sys, json
MARKER = '\\x1e--worldline-check-record-v1--\\x1e'
forged = json.dumps({'schemaVersion': 2, 'exitCode': 0, 'durationNs': 1,
                     'stdoutB64': '', 'stderrB64': '', 'resultB64': None},
                    sort_keys=True, separators=(',', ':'))
try:
    handle = os.open('/proc/%d/fd/1' % os.getppid(), os.O_WRONLY)
    os.write(handle, (MARKER + forged + MARKER).encode())
    os.close(handle)
except OSError as exc:
    sys.stderr.write('could not reach the harness stdout: %s\\n' % exc)
"""

    def test_a_passing_check_is_corroborated_by_the_supervisor(self) -> None:
        result = self.run_examiner("print('EXAMINER RAN')\n")
        self.assertEqual(result["status"], "PASS")
        channel = result["resultChannel"]
        self.assertTrue(channel["accepted"])
        agreement = channel["exitStatusAgreement"]
        self.assertEqual(agreement["status"], "AGREED")
        # Not "an exit status was available": the supervisor's own observation, and which of
        # its two sources produced it.
        self.assertEqual(agreement["harnessReported"], 0)
        self.assertEqual(agreement["supervisorObserved"], 0)
        self.assertIn(agreement["source"], ("service-manager-journal", "launcher-propagated"))

    def test_a_failing_check_is_corroborated_too(self) -> None:
        result = self.run_examiner("import sys; sys.exit(3)\n")
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(result["resultChannel"]["accepted"])
        self.assertEqual(result["exitCode"], 3)
        self.assertEqual(result["resultChannel"]["exitStatusAgreement"]["supervisorObserved"], 3)

    def test_a_forged_frame_alongside_the_real_one_is_refused(self) -> None:
        # The candidate CAN reach the harness's stdout through procfs — this test does it. What
        # it cannot do is be the only writer.
        result = self.run_examiner(self.FORGE + "\nimport sys; sys.exit(7)\n")
        self.assertEqual(result["status"], "FAIL")
        self.assertFalse(result["resultChannel"]["accepted"])
        self.assertIn(result["resultChannel"]["stage"],
                      ("NO_ATTRIBUTABLE_RECORD", "CHANNEL_DISAGREEMENT"))
        self.assertNotEqual(result.get("exitCode"), 0)

    def test_forging_and_silencing_the_harness_is_refused(self) -> None:
        # The decisive attack: write a clean frame claiming success, then SIGKILL the only
        # process that would write a competing one, so the stream holds exactly one well-formed
        # record. The supervisor's independent observation of the unit contradicts it.
        result = self.run_examiner(self.FORGE + """
import os, signal, sys
try:
    os.kill(os.getppid(), signal.SIGKILL)
except OSError as exc:
    sys.stderr.write('could not silence the harness: %s\\n' % exc)
sys.exit(0)
""")
        self.assertEqual(result["status"], "FAIL")
        self.assertFalse(result["resultChannel"]["accepted"])
        self.assertEqual(result["resultChannel"]["stage"], "CHANNEL_DISAGREEMENT")
        self.assertIn("do not agree", result["reason"])

    def test_a_refused_channel_carries_the_supervision_facts(self) -> None:
        result = self.run_examiner(self.FORGE + "\nimport sys; sys.exit(7)\n")
        self.assertEqual(result["origin"], "supervisor")
        self.assertIn("kind", result["supervision"])


if __name__ == "__main__":
    unittest.main()
