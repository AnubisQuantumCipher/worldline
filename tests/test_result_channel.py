"""Who produces the authoritative record, and where the verdict rests.

Campaign F2. The record used to be written by a harness INSIDE the sandbox, to its own stdout,
which the supervisor read as a framed message. The examiner's own descendants share its uid and
PID namespace and can open /proc/<harness>/fd/1, so they could take the harness's frame off the
pipe and put back a forged one, or inject bytes while it was mid-write. Protecting the frame
protocol could not fix that: the transport itself was reachable.

The record producer is now the DAEMON, outside the sandbox, in a different PID and mount
namespace from everything the candidate can run. There is no in-sandbox producer fd to steal.
The verdict is the SERVICE MANAGER's observation of how the unit exited -- measured outside the
sandbox -- so a candidate can change it only by changing how the examiner actually exits.

An honest limit remains and is recorded rather than hidden: a result-file format's verdict rests
on file bytes written inside the sandbox, which a sibling under the same uid can replace. Such a
check is marked candidate-reachable and does not get the "isolated from the candidate" claim for
its report. Closing that needs uid separation between the examiner and candidate code.
"""
from __future__ import annotations

import base64
import os
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "runtime"))

from worldline.admission import AdmissionAuthority, Floors, Gate, Ledger, ResourcePolicy  # noqa: E402
from worldline.checks import CheckRunner  # noqa: E402
from worldline.finalize import evaluation_record  # noqa: E402
from worldline.linux.namespaces import BubblewrapSandbox, OverlayRoot  # noqa: E402
from worldline.linux.systemd import SystemdAdapter  # noqa: E402
from worldline.paths import WorldlinePaths  # noqa: E402
from worldline.project import CheckSpec  # noqa: E402

ROOT_KEY = "a1" * 32
LOGICAL = "/logical/root"


class ProducerOutsideTheSandbox(unittest.TestCase):
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
        (self.upper / "exam").mkdir(parents=True)
        self.work = self.base / "work"
        self.work.mkdir()
        self.overlay = OverlayRoot(root_key=ROOT_KEY, lower=self.lower, upper=self.upper,
                                   work=self.work, target=Path(LOGICAL))
        gate = Gate(AdmissionAuthority(Ledger(self.paths.runtime), Floors()), ResourcePolicy.from_mapping({}))
        self.runner = CheckRunner(self.paths, BubblewrapSandbox(self.paths), SystemdAdapter(), gate)

    def run_examiner(self, body: str, *, fmt: str = "exit", result: str | None = None) -> dict:
        (self.lower / "exam" / "run.py").write_text(body, encoding="utf-8")
        check = CheckSpec("exam", "tests", ("/usr/bin/python3", f"{LOGICAL}/exam/run.py"),
                          None, True, fmt, result, (), ())
        entries = [{"checkId": "exam", "rootKey": ROOT_KEY, "path": "exam/run.py", "source": "argv"}]
        result_dict = self.runner.run(world_instance=str(uuid.uuid4()), overlays=[self.overlay],
                                      primary_target=Path(LOGICAL), checks=[check],
                                      verifier_sources={ROOT_KEY: self.lower},
                                      verifiers=entries, logical_roots={ROOT_KEY: LOGICAL})[0]
        result_dict["evaluation"] = evaluation_record(result_dict)
        return result_dict

    # A child tries every old trick: write a forged v2 frame to every fd/1 it can reach, and to
    # its own stdout. None of it is the verdict any more.
    FORGE = r'''
import os, sys, json
MARKER = "\x1e--worldline-check-record-v1--\x1e"
forged = json.dumps({"schemaVersion": 2, "exitCode": 0, "durationNs": 1,
                     "stdoutB64": "", "stderrB64": "", "resultB64": None})
for pid in os.listdir("/proc"):
    if not pid.isdigit():
        continue
    try:
        fd = os.open("/proc/%s/fd/1" % pid, os.O_WRONLY)
        os.write(fd, (MARKER + forged + MARKER).encode())
        os.close(fd)
    except OSError:
        pass
sys.stdout.write(MARKER + forged + MARKER)
sys.stdout.flush()
'''

    def test_a_passing_check_is_accepted_with_the_daemon_as_producer(self) -> None:
        result = self.run_examiner("print('EXAMINER RAN')\n")
        self.assertEqual(result["status"], "PASS")
        channel = result["resultChannel"]
        self.assertTrue(channel["accepted"])
        self.assertEqual(channel["recordProducer"], "daemon-outside-sandbox")
        self.assertEqual(channel["exitStatus"]["observed"], 0)
        self.assertEqual(result["evaluationProfile"]["verdictAuthority"], "supervisor-exit-status")

    def test_a_failing_check_is_a_fail(self) -> None:
        result = self.run_examiner("import sys; sys.exit(3)\n")
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["exitCode"], 3)
        self.assertFalse(result["evaluation"]["admissibleForPromotion"])

    def test_a_forged_frame_cannot_flip_a_real_failure(self) -> None:
        # The whole F2 attack, defeated by construction: the examiner exits 1, writes forged
        # passing frames everywhere, and the verdict is still FAIL because it is the supervisor's
        # observed exit, not anything written inside the sandbox.
        result = self.run_examiner(self.FORGE + "\nimport sys; sys.exit(1)\n")
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["exitCode"], 1)
        self.assertFalse(result["evaluation"]["admissibleForPromotion"])

    def test_forging_and_silencing_no_longer_has_a_producer_to_silence(self) -> None:
        # The decisive T3 attack was: forge a passing frame, then SIGKILL the harness so only the
        # forged frame remains. There is no harness to silence now; killing the examiner itself
        # is observed by the supervisor as a non-zero exit.
        result = self.run_examiner(self.FORGE + '''
import os, signal
os.kill(os.getpid(), signal.SIGKILL)
''')
        self.assertEqual(result["status"], "FAIL")
        self.assertFalse(result["evaluation"]["admissibleForPromotion"])

    def test_the_launch_failure_stage_is_named(self) -> None:
        # A non-existent interpreter path: the unit never starts. Distinct from a candidate FAIL.
        check = CheckSpec("exam", "tests", ("/usr/bin/does-not-exist",), None, True, "exit", None, (), ())
        result = self.runner.run(world_instance=str(uuid.uuid4()), overlays=[self.overlay],
                                 primary_target=Path(LOGICAL), checks=[check],
                                 verifier_sources={ROOT_KEY: self.lower},
                                 verifiers=[], logical_roots={ROOT_KEY: LOGICAL})[0]
        result["evaluation"] = evaluation_record(result)
        # bwrap starts, the exec of a missing interpreter fails inside it: a non-zero exit the
        # supervisor observes. A FAIL, never admissible; the point is that the daemon's verdict
        # comes from the observed exit, not from anything the sandbox produced.
        self.assertEqual(result["status"], "FAIL")
        self.assertFalse(result["evaluation"]["admissibleForPromotion"])


class ResultFileTrustIsHonest(unittest.TestCase):
    """A result-file verdict rests on candidate-reachable bytes, and says so."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-rf-")
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
        (self.upper / "exam").mkdir(parents=True)
        self.work = self.base / "work"
        self.work.mkdir()
        self.overlay = OverlayRoot(root_key=ROOT_KEY, lower=self.lower, upper=self.upper,
                                   work=self.work, target=Path(LOGICAL))
        gate = Gate(AdmissionAuthority(Ledger(self.paths.runtime), Floors()), ResourcePolicy.from_mapping({}))
        self.runner = CheckRunner(self.paths, BubblewrapSandbox(self.paths), SystemdAdapter(), gate)

    def run_junit(self, body: str) -> dict:
        (self.lower / "exam" / "run.py").write_text(body, encoding="utf-8")
        check = CheckSpec("exam", "tests", ("/usr/bin/python3", f"{LOGICAL}/exam/run.py"),
                          None, True, "junit", "report.xml", (), ())
        entries = [{"checkId": "exam", "rootKey": ROOT_KEY, "path": "exam/run.py", "source": "argv"}]
        return self.runner.run(world_instance=str(uuid.uuid4()), overlays=[self.overlay],
                               primary_target=Path(LOGICAL), checks=[check],
                               verifier_sources={ROOT_KEY: self.lower},
                               verifiers=entries, logical_roots={ROOT_KEY: LOGICAL})[0]

    def test_a_result_file_verdict_is_marked_candidate_reachable(self) -> None:
        body = ('open("report.xml", "w").write('
                '\'<testsuite tests="1" failures="0" errors="0" skipped="0"/>\')\n')
        result = self.run_junit(body)
        self.assertEqual(result["status"], "PASS")
        profile = result["evaluationProfile"]
        self.assertEqual(profile["verdictAuthority"], "candidate-reachable-report")
        self.assertEqual(profile["reportTrust"], "candidate-reachable")
        self.assertTrue(any("not isolated from the candidate" in n for n in profile["nonClaims"]))

    def test_the_result_file_is_read_host_side(self) -> None:
        # The daemon reads the file from the overlay upper, outside the sandbox, after the run.
        body = ('open("report.xml", "w").write('
                '\'<testsuite tests="2" failures="0" errors="0" skipped="0"/>\')\n')
        result = self.run_junit(body)
        self.assertEqual(result.get("tests"), 2)
        self.assertTrue((self.upper / "report.xml").is_file())


if __name__ == "__main__":
    unittest.main()
