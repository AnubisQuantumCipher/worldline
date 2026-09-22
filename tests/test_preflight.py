"""Deterministic controls for the pre-upgrade gate (scripts/preflight.py).

The gate exists because the released installer converted an unreadable daemon into "0 jobs
running" and upgraded anyway. Every test here drives the real script against a fake `worldline`
binary, so what is exercised is the shipped decision logic, not a re-implementation of it.

The known-good control must PERMIT; every defective control must REFUSE. A gate that cannot
observe its condition must refuse, never permit.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PREFLIGHT = REPO / "scripts/preflight.py"

HEALTHY_STATUS = {
    "schemaVersion": 1,
    "prime": {"alias": "PRIME", "id": "sha256:aa", "instanceId": "i", "generation": "g", "roots": [], "dirty": False, "watchError": None},
    "jobs": [],
    "worlds": [{"alias": "alpha", "state": "VALID"}],
    "activeWorld": None,
    "daemon": {"version": "1.3.0"},
    "capabilities": {},
    "lastReceipt": None,
    "ghostRecommendation": None,
}
HEALTHY_DOCTOR = {
    "openTransactions": [],
    "recovery": {"state": "OK", "quarantined": []},
    "storeIntegrity": {"state": "OK", "findings": []},
    "rootIntegrity": {"roots": [{"path": "/p", "rootKey": "k", "state": "OK"}]},
    "unsupervisedWorlds": [],
}
GHOSTS_OFF = {"enabled": False, "agent": None}


class PreflightControls(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-preflight-")
        self.root = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)

    def _binary(self, *, status=HEALTHY_STATUS, doctor=HEALTHY_DOCTOR, ghost=GHOSTS_OFF,
                status_exit: int = 0, status_raw: str | None = None) -> Path:
        """A fake `worldline` whose --json output the gate must interpret."""
        payload = {
            "status": status_raw if status_raw is not None else json.dumps(status),
            "doctor": json.dumps(doctor),
            "ghost": json.dumps(ghost),
            "status_exit": status_exit,
        }
        script = self.root / "worldline"
        script.write_text(
            "#!/usr/bin/env python3\n"
            "import json, sys\n"
            f"P = {payload!r}\n"
            "args = [a for a in sys.argv[1:] if a != '--json']\n"
            "if args[:1] == ['status']:\n"
            "    sys.stdout.write(P['status']); sys.exit(P['status_exit'])\n"
            "if args[:1] == ['doctor']:\n"
            "    sys.stdout.write(P['doctor']); sys.exit(0)\n"
            "if args[:2] == ['ghost', 'status']:\n"
            "    sys.stdout.write(P['ghost']); sys.exit(0)\n"
            "sys.exit(1)\n",
            encoding="utf-8",
        )
        os.chmod(script, 0o755)
        return script

    def _run(self, binary: Path, *extra: str) -> dict:
        return self._run_env(binary, {}, *extra)

    def _run_env(self, binary: Path, env_extra: dict, *extra: str) -> dict:
        proc = subprocess.run([sys.executable, str(PREFLIGHT), "--json", "--binary", str(binary), *extra],
                              env={**os.environ, **env_extra},
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=180)
        report = json.loads(proc.stdout)
        report["_exit"] = proc.returncode
        return report

    def _gate(self, report: dict, name: str) -> dict:
        return next(g for g in report["gates"] if g["gate"] == name)

    # ---- known-good control ------------------------------------------------------------------
    def test_healthy_installation_is_permitted(self) -> None:
        report = self._run(self._binary())
        self.assertTrue(report["permitted"], report["refused"])
        self.assertEqual(report["_exit"], 0)
        self.assertEqual(self._gate(report, "no-active-jobs")["state"], "OK")

    # ---- the defect that motivated the gate ---------------------------------------------------
    def test_unparseable_status_refuses_instead_of_reading_zero_jobs(self) -> None:
        report = self._run(self._binary(status_raw="<html>gateway timeout</html>"))
        self.assertFalse(report["permitted"])
        self.assertEqual(report["_exit"], 2)
        self.assertEqual(self._gate(report, "status-readable")["state"], "UNKNOWN")
        self.assertEqual(self._gate(report, "no-active-jobs")["state"], "UNKNOWN")

    def test_status_command_failure_refuses(self) -> None:
        report = self._run(self._binary(status_raw="", status_exit=1))
        self.assertFalse(report["permitted"])
        self.assertEqual(self._gate(report, "status-readable")["state"], "UNKNOWN")

    def test_status_of_unexpected_shape_refuses(self) -> None:
        report = self._run(self._binary(status_raw=json.dumps({"unexpected": True})))
        self.assertFalse(report["permitted"])
        self.assertEqual(self._gate(report, "status-readable")["state"], "UNKNOWN")

    def test_missing_binary_is_a_first_install_not_an_upgrade(self) -> None:
        report = self._run(self.root / "absent")
        self.assertTrue(report["permitted"])
        self.assertEqual(report["mode"], "first-install")

    # ---- live work ----------------------------------------------------------------------------
    def test_running_job_refuses(self) -> None:
        status = {**HEALTHY_STATUS, "jobs": [{"world": "w", "state": "RUNNING"}]}
        report = self._run(self._binary(status=status))
        self.assertFalse(report["permitted"])
        self.assertEqual(self._gate(report, "no-active-jobs")["state"], "REFUSE")

    def test_finalizing_job_refuses(self) -> None:
        status = {**HEALTHY_STATUS, "jobs": [{"world": "w", "state": "FINALIZING"}]}
        self.assertFalse(self._run(self._binary(status=status))["permitted"])

    def test_mutable_world_refuses(self) -> None:
        status = {**HEALTHY_STATUS, "worlds": [{"alias": "w", "state": "MUTABLE"}]}
        report = self._run(self._binary(status=status))
        self.assertFalse(report["permitted"])
        self.assertEqual(self._gate(report, "no-unfinished-worlds")["state"], "REFUSE")

    # ---- transactional and store state --------------------------------------------------------
    def test_open_transaction_refuses(self) -> None:
        doctor = {**HEALTHY_DOCTOR, "openTransactions": [{"transactionId": "t", "state": "PREPARED"}]}
        report = self._run(self._binary(doctor=doctor))
        self.assertFalse(report["permitted"])
        self.assertEqual(self._gate(report, "no-open-transactions")["state"], "REFUSE")

    def test_quarantined_recovery_refuses(self) -> None:
        doctor = {**HEALTHY_DOCTOR, "recovery": {"state": "QUARANTINED", "quarantined": ["t"]}}
        self.assertFalse(self._run(self._binary(doctor=doctor))["permitted"])

    def test_store_integrity_failure_refuses(self) -> None:
        doctor = {**HEALTHY_DOCTOR, "storeIntegrity": {"state": "DEGRADED", "findings": ["x"]}}
        self.assertFalse(self._run(self._binary(doctor=doctor))["permitted"])

    def test_root_integrity_failure_refuses(self) -> None:
        doctor = {**HEALTHY_DOCTOR, "rootIntegrity": {"roots": [{"path": "/p", "state": "EXTERNAL_HARDLINK"}]}}
        report = self._run(self._binary(doctor=doctor))
        self.assertFalse(report["permitted"])
        self.assertEqual(self._gate(report, "root-integrity")["state"], "REFUSE")

    def test_missing_doctor_fields_refuse_rather_than_pass(self) -> None:
        report = self._run(self._binary(doctor={}))
        self.assertFalse(report["permitted"])
        for name in ("no-open-transactions", "recovery-clean", "store-integrity", "root-integrity"):
            self.assertEqual(self._gate(report, name)["state"], "UNKNOWN", name)

    # ---- ghosts can fork a world mid-upgrade --------------------------------------------------
    def test_enabled_ghosts_refuse_unless_explicitly_allowed(self) -> None:
        enabled = {"enabled": True, "agent": "codex"}
        report = self._run(self._binary(ghost=enabled))
        self.assertFalse(report["permitted"])
        self.assertEqual(self._gate(report, "ghosts-quiet")["state"], "REFUSE")
        allowed = self._run(self._binary(ghost=enabled), "--allow-ghosts")
        self.assertEqual(self._gate(allowed, "ghosts-quiet")["state"], "OK")

    # ---- "no daemon is running" must be OBSERVED, never inferred from the unit alone ----------
    def test_a_silent_daemon_is_only_quiet_when_every_signal_agrees(self) -> None:
        """CI on a host with no worldlined unit caught this: the gates used to short-circuit to OK
        whenever the unit was inactive, so the installation was never consulted at all and a
        running job could not be seen. Quiet now requires the CLI to fail AND the unit to be
        inactive AND no socket."""
        silent = self.root / "silent"
        silent.write_text("#!/usr/bin/env python3\nimport sys\nsys.exit(1)\n", encoding="utf-8")
        os.chmod(silent, 0o755)
        absent = self.root / "no-such-socket"
        # no socket present -> genuinely quiet, and permitted
        quiet = self._run(silent, "--socket", str(absent), "--unit", "worldline-absent-for-tests.service")
        self.assertTrue(quiet["permitted"], quiet["refused"])
        self.assertIn("no daemon is running", self._gate(quiet, "status-readable")["detail"])
        # a socket present with an unanswering CLI is NOT quiet: something is there
        present = self.root / "worldlined.sock"
        present.write_text("", encoding="utf-8")
        noisy = self._run(silent, "--socket", str(present), "--unit", "worldline-absent-for-tests.service")
        self.assertFalse(noisy["permitted"])
        self.assertEqual(self._gate(noisy, "status-readable")["state"], "UNKNOWN")

    def test_a_running_job_is_seen_even_when_the_unit_is_inactive(self) -> None:
        status = {**HEALTHY_STATUS, "jobs": [{"world": "w", "state": "RUNNING"}]}
        report = self._run(self._binary(status=status), "--socket", str(self.root / "no-such-socket"),
                           "--unit", "worldline-absent-for-tests.service")
        self.assertFalse(report["permitted"], "a job running under a directly-launched daemon must still refuse")
        self.assertEqual(self._gate(report, "no-active-jobs")["state"], "REFUSE")

    # ---- the report is machine-readable and names what refused --------------------------------
    def test_refusal_report_names_the_failing_gates(self) -> None:
        status = {**HEALTHY_STATUS, "jobs": [{"world": "w", "state": "RUNNING"}]}
        report = self._run(self._binary(status=status))
        self.assertTrue(report["refused"])
        self.assertIn("no-active-jobs", [r["gate"] for r in report["refused"]])
        self.assertTrue(all("state" in r and "detail" in r for r in report["gates"]))


if __name__ == "__main__":
    unittest.main()
