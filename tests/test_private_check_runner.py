"""Opt-in host campaign through policy staging, separated roles, report and admission.

The worker writes a forged passing XML file into its disposable candidate tree. A failing
examiner must still produce a private failing report; promotion may read only that report.
"""
from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
import uuid

from worldline.admission import AdmissionAuthority, Floors, Gate, Ledger, ResourcePolicy
from worldline.checks import CheckRunner
from worldline.finalize import evaluation_record
from worldline.linux.namespaces import BubblewrapSandbox, OverlayRoot
from worldline.linux.systemd import SystemdAdapter
from worldline.paths import WorldlinePaths
from worldline.project import CheckSpec
from worldline.trusted import TRUSTED_INTERPRETER


ROOT_KEY = "d7" * 32
LOGICAL = "/logical/private-check"

WORKER = '''from pathlib import Path
Path('candidate-report.xml').write_text('<testsuite tests="1" failures="0" errors="0"/>')
assert not Path('/run/worldline-report').exists()
assert not Path('/run/worldline-broker.sock').exists()
assert not Path('/opt/worldline-gnat').exists()
Path('source.txt').write_text('changed only in disposable worker')
print('actual worker result')
'''

EXAMINER = '''import candidate
from pathlib import Path
import sys
observed = candidate.run(['/usr/bin/python3', 'worker.py'], timeout=20)
if observed.returncode:
    print(observed.stderr.decode('utf-8', 'replace'), file=sys.stderr)
assert Path('source.txt').read_text() == 'frozen source'
assert not Path('candidate-report.xml').exists()
passed = observed.returncode == 0 and observed.stdout == EXPECTED
Path('/run/worldline-report/report').write_text(
    '<testsuite tests="1" failures="' + ('0' if passed else '1') + '" errors="0"/>')
raise SystemExit(0 if passed else 1)
'''


@unittest.skipUnless(os.environ.get("WORLDLINE_PRIVATE_EVALUATOR_TEST") == "1",
                     "set WORLDLINE_PRIVATE_EVALUATOR_TEST=1 for real user-systemd integration")
class PrivateCheckRunnerIntegration(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="worldline-private-runner-")
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        environment = dict(os.environ,
                           XDG_STATE_HOME=str(self.base / "state"),
                           XDG_DATA_HOME=str(self.base / "data"),
                           XDG_RUNTIME_DIR=str(self.base / "run"),
                           XDG_CONFIG_HOME=str(self.base / "config"))
        for name in ("state", "data", "run", "config"):
            (self.base / name).mkdir(mode=0o700)
        paths = WorldlinePaths.from_environment(environment)
        paths.ensure()
        gate = Gate(AdmissionAuthority(Ledger(paths.runtime), Floors()), ResourcePolicy.from_mapping({}))
        self.runner = CheckRunner(paths, BubblewrapSandbox(paths), SystemdAdapter(), gate)
        self.lower = self.base / "frozen"
        (self.lower / "exam").mkdir(parents=True)
        (self.lower / "source.txt").write_text("frozen source")
        (self.lower / "worker.py").write_text(WORKER)
        self.overlay = OverlayRoot(ROOT_KEY, self.lower, self.base / "upper",
                                   self.base / "work", Path(LOGICAL))
        self.overlay.upper.mkdir()
        self.overlay.work.mkdir()

    def run_check(self, expected: bytes) -> dict:
        (self.lower / "exam" / "check.py").write_text("EXPECTED = " + repr(expected) + "\n" + EXAMINER)
        world_id = str(uuid.uuid4())
        check = CheckSpec("exam", "tests",
                          (TRUSTED_INTERPRETER, f"{LOGICAL}/exam/check.py"),
                          None, True, "junit", None, (), ("exam/check.py",),
                          "private-evaluator-v1")
        entries = [{"checkId": "exam", "rootKey": ROOT_KEY,
                    "path": "exam/check.py", "source": "declared"}]
        result = self.runner.run(
            world_instance=world_id, overlays=(self.overlay,),
            primary_target=Path(LOGICAL), checks=(check,),
            verifier_sources={ROOT_KEY: self.lower}, verifiers=entries,
            logical_roots={ROOT_KEY: LOGICAL},
            candidate_snapshot={"worldInstance": world_id,
                                "rootSetHash": "snapshot-identity",
                                "rootManifests": {ROOT_KEY: "root-identity"},
                                "role": "pre-check-input"},
        )[0]
        result["evaluation"] = evaluation_record(result)
        return result

    def test_real_private_report_admits_genuine_pass_and_refuses_candidate_forgery(self) -> None:
        passing = self.run_check(b"actual worker result\n")
        self.assertEqual(passing["status"], "PASS", passing.get("reason"))
        self.assertEqual(passing["evaluation"]["reportIntegrity"], "VERIFIED")
        self.assertTrue(passing["evaluation"]["admissibleForPromotion"])
        self.assertEqual((self.lower / "source.txt").read_text(), "frozen source")
        self.assertFalse((self.lower / "candidate-report.xml").exists())

        failing = self.run_check(b"fabricated expected output\n")
        self.assertEqual(failing["status"], "FAIL", failing.get("reason"))
        self.assertEqual(failing["failures"], 1)
        self.assertFalse(failing["evaluation"]["admissibleForPromotion"])
        self.assertEqual(failing["privateReport"]["collection"], "private-directory")


if __name__ == "__main__":
    unittest.main()
