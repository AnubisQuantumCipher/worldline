"""Real private benchmark path and a candidate-owned report forgery.

Opt in with WORLDLINE_PRIVATE_EVALUATOR_TEST=1. The examiner measures two
broker-supervised runs, writes the sole accepted report, and decides whether
the candidate improved. Candidate stdout and files remain untrusted data.
"""
from __future__ import annotations

import base64
import hashlib
import json
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


ROOT_KEY = "e8" * 32
LOGICAL = "/logical/private-benchmark"
FORGED_REPORT = {
    "metric": "broker-run-duration", "unit": "ns",
    "baseline": "999999999999", "candidate": "1", "direction": "lower-is-better",
}

EXAMINER = '''import candidate
import json
from pathlib import Path

# Both values are supplied by the host broker, not by candidate stdout or a
# candidate-authored timing file. Each call gets a disposable worker copy.
baseline = candidate.run(
    ['/usr/bin/python3', '-c', 'import time; time.sleep(0.75)'], timeout=15)
measured = candidate.run(['/usr/bin/python3', 'candidate.py'], timeout=15)
assert not Path('candidate-owned-benchmark.json').exists()
passed = (
    baseline.returncode == 0 and measured.returncode == 0
    and measured.duration_ns < baseline.duration_ns
    and measured.stdout == b'measured candidate\\n'
)
report = {
    'metric': 'broker-run-duration', 'unit': 'ns',
    'baseline': str(baseline.duration_ns),
    'candidate': str(measured.duration_ns),
    'direction': 'lower-is-better',
}
Path('/run/worldline-report/report').write_text(json.dumps(report))
raise SystemExit(0 if passed else 1)
'''

PASSING_CANDIDATE = "print('measured candidate')\n"
FAILING_CANDIDATE = '''import json
from pathlib import Path
import time
forged = {
    'metric': 'broker-run-duration', 'unit': 'ns',
    'baseline': '999999999999', 'candidate': '1',
    'direction': 'lower-is-better',
}
Path('candidate-owned-benchmark.json').write_text(json.dumps(forged))
print(json.dumps(forged))
time.sleep(1.5)
'''


@unittest.skipUnless(os.environ.get("WORLDLINE_PRIVATE_EVALUATOR_TEST") == "1",
                     "set WORLDLINE_PRIVATE_EVALUATOR_TEST=1 for real user-systemd integration")
class PrivateBenchmarkIntegration(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="worldline-private-benchmark-")
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
        (self.lower / "exam" / "check.py").write_text(EXAMINER)
        self.candidate_file = self.lower / "candidate.py"
        self.overlay = OverlayRoot(ROOT_KEY, self.lower, self.base / "upper",
                                   self.base / "work", Path(LOGICAL))
        self.overlay.upper.mkdir()
        self.overlay.work.mkdir()

    def run_benchmark(self, candidate_source: str) -> dict:
        self.candidate_file.write_text(candidate_source)
        world_id = str(uuid.uuid4())
        check = CheckSpec("bench", "benchmark",
                          (TRUSTED_INTERPRETER, f"{LOGICAL}/exam/check.py"),
                          None, True, "worldline-benchmark-v1", None, (),
                          ("exam/check.py",), "private-evaluator-v1")
        entries = [{"checkId": "bench", "rootKey": ROOT_KEY,
                    "path": "exam/check.py", "source": "declared"}]
        result = self.runner.run(
            world_instance=world_id, overlays=(self.overlay,),
            primary_target=Path(LOGICAL), checks=(check,),
            verifier_sources={ROOT_KEY: self.lower}, verifiers=entries,
            logical_roots={ROOT_KEY: LOGICAL},
            candidate_snapshot={"worldInstance": world_id,
                                "rootSetHash": "frozen-benchmark-input",
                                "rootManifests": {ROOT_KEY: "root-identity"},
                                "role": "pre-check-input"},
        )[0]
        result["evaluation"] = evaluation_record(result)
        return result

    def test_measured_pass_and_candidate_report_forgery_refused(self) -> None:
        passing = self.run_benchmark(PASSING_CANDIDATE)
        failing = self.run_benchmark(FAILING_CANDIDATE)

        self.assertEqual(passing["status"], "PASS", passing.get("reason"))
        self.assertTrue(passing["improved"])
        self.assertEqual(passing["evaluation"]["reportIntegrity"], "VERIFIED")
        self.assertTrue(passing["evaluation"]["admissibleForPromotion"])

        self.assertEqual(failing["status"], "FAIL", failing.get("reason"))
        self.assertFalse(failing["improved"])
        self.assertEqual(failing["evaluation"]["reportIntegrity"], "VERIFIED")
        self.assertEqual(failing["evaluation"]["executionStatus"], "COMPLETED")
        self.assertFalse(failing["evaluation"]["admissibleForPromotion"])
        self.assertFalse((self.lower / "candidate-owned-benchmark.json").exists())
        self.assertNotEqual(failing["candidate"], FORGED_REPORT["candidate"])
        candidate_worker = failing["evaluatorBoundary"]["workers"][1]
        self.assertEqual(candidate_worker["returncode"], 0)
        forged_stdout = (json.dumps(FORGED_REPORT) + "\n").encode()
        self.assertEqual(candidate_worker["stdoutSha256"], hashlib.sha256(forged_stdout).hexdigest())
        for result in (passing, failing):
            private_bytes = base64.b64decode(result["privateReport"]["payloadB64"], validate=True)
            report = json.loads(private_bytes)
            self.assertEqual(set(report), set(FORGED_REPORT))
            self.assertEqual(report["metric"], "broker-run-duration")
            self.assertEqual(report["unit"], "ns")
            self.assertEqual(result["baseline"], report["baseline"])
            self.assertEqual(result["candidate"], report["candidate"])
            self.assertTrue(result["evaluatorBoundary"]["rolesCompleted"])
            self.assertEqual(len(result["evaluatorBoundary"]["workers"]), 2)

        evidence = os.environ.get("WORLDLINE_PRIVATE_BENCHMARK_EVIDENCE")
        if evidence:
            destination = Path(evidence)
            destination.mkdir(mode=0o700, parents=True, exist_ok=True)
            (destination / "positive.json").write_text(json.dumps(passing, indent=2, sort_keys=True))
            (destination / "negative.json").write_text(json.dumps(failing, indent=2, sort_keys=True))
            (destination / "candidate-forgery.json").write_text(json.dumps(FORGED_REPORT, indent=2))


if __name__ == "__main__":
    unittest.main()
