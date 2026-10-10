"""Deterministic controls for the pre-upgrade gate (scripts/preflight.py).

Every test drives the real script, so what is exercised is the shipped decision logic rather
than a description of it. Each run is hermetic: the `worldline` binary, `systemctl`, the socket,
the unit name and both data directories are injected, so no test depends on whether this
machine's daemon happens to be running or whether a world happens to be active.

The known-good control must PERMIT; every defective control must REFUSE. A gate that cannot
observe its condition must refuse, and a gate that is never recorded at all must refuse too —
that last one is the defect an independent review found in the first version of this file.
"""
from __future__ import annotations

import importlib.util
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
    "prime": {"alias": "PRIME", "id": "sha256:aa", "instanceId": "i", "generation": "g", "roots": [],
              "dirty": False, "watchError": None},
    "jobs": [],
    "worlds": [{"alias": "alpha", "state": "VALID"}],
    "activeWorld": None,
    "daemon": {"version": "1.3.1"},
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
        self.state = self.root / "state/worldline"
        (self.state / "transactions").mkdir(parents=True)
        self.share = self.root / "share/worldline"
        self.share.mkdir(parents=True)
        self.socket = self.root / "absent.sock"

    # ---- injected environment -----------------------------------------------------------------
    def _binary(self, *, status=HEALTHY_STATUS, doctor=HEALTHY_DOCTOR, ghost=GHOSTS_OFF,
                status_exit: int = 0, status_raw: str | None = None, silent: bool = False) -> Path:
        script = self.root / "worldline"
        if silent:
            script.write_text("#!/usr/bin/env python3\nimport sys\nsys.exit(1)\n", encoding="utf-8")
            os.chmod(script, 0o755)
            return script
        payload = {
            "status": status_raw if status_raw is not None else json.dumps(status),
            "doctor": json.dumps(doctor),
            "ghost": json.dumps(ghost),
            "status_exit": status_exit,
        }
        script.write_text(
            "#!/usr/bin/env python3\n"
            "import sys\n"
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

    def _systemctl(self, active_state: str = "active", units: str = "", fail: bool = False) -> Path:
        """A systemctl whose ActiveState and unit listing the gate must interpret."""
        script = self.root / "systemctl"
        script.write_text(
            "#!/usr/bin/env python3\n"
            "import sys\n"
            f"STATE = {active_state!r}\nUNITS = {units!r}\nFAIL = {fail!r}\n"
            "args = sys.argv[1:]\n"
            "if FAIL:\n"
            "    sys.exit(1)\n"
            "if 'show' in args:\n"
            "    sys.stdout.write(STATE + '\\n'); sys.exit(0)\n"
            "if 'list-units' in args:\n"
            "    sys.stdout.write(UNITS); sys.exit(0)\n"
            "sys.exit(0)\n",
            encoding="utf-8",
        )
        os.chmod(script, 0o755)
        return script

    def _run(self, binary: Path, *extra: str, active_state: str = "active", units: str = "",
             systemctl_fails: bool = False) -> dict:
        argv = [sys.executable, str(PREFLIGHT), "--json", "--binary", str(binary),
                "--systemctl", str(self._systemctl(active_state, units, systemctl_fails)),
                "--socket", str(self.socket), "--state-dir", str(self.state), "--share-dir", str(self.share),
                *extra]
        proc = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=180)
        report = json.loads(proc.stdout)
        report["_exit"] = proc.returncode
        return report

    def _gate(self, report: dict, name: str) -> dict:
        return next(g for g in report["gates"] if g["gate"] == name)

    # ---- known-good control --------------------------------------------------------------------
    def test_healthy_installation_is_permitted(self) -> None:
        report = self._run(self._binary())
        self.assertTrue(report["permitted"], report["refused"] + report["missingGates"])
        self.assertEqual(report["_exit"], 0)
        self.assertEqual(report["missingGates"], [])

    def test_every_required_gate_is_recorded_on_the_healthy_path(self) -> None:
        report = self._run(self._binary())
        self.assertEqual({g["gate"] for g in report["gates"]}, set(report["requiredGates"]))

    # ---- the roster: an unasked question is a refusal -------------------------------------------
    def test_a_missing_gate_refuses_even_when_everything_recorded_is_ok(self) -> None:
        """The defect an independent review found: `permitted` was `all()` over whatever happened
        to be recorded, so a gate that was never asked could not fail."""
        spec = importlib.util.spec_from_file_location("preflight_mod", PREFLIGHT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        gate = module.Gate()
        for name in module.REQUIRED_GATES:
            gate.ok(name, "fine")
        self.assertTrue(gate.permitted)
        gate.results = [r for r in gate.results if r["gate"] != "store-integrity"]
        self.assertFalse(gate.permitted, "a gate that was never recorded must refuse")
        self.assertEqual(gate.missing, ["store-integrity"])

    # ---- the defect that motivated the gate ------------------------------------------------------
    def test_unparseable_status_refuses_instead_of_reading_zero_jobs(self) -> None:
        report = self._run(self._binary(status_raw="<html>gateway timeout</html>"))
        self.assertFalse(report["permitted"])
        self.assertEqual(report["_exit"], 2)
        self.assertEqual(self._gate(report, "status-readable")["state"], "UNKNOWN")
        self.assertEqual(self._gate(report, "no-active-jobs")["state"], "UNKNOWN")

    def test_status_command_failure_refuses_while_the_unit_is_active(self) -> None:
        report = self._run(self._binary(silent=True), active_state="active")
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

    # ---- daemon liveness is a state, not an exit code ---------------------------------------------
    def test_a_unit_in_transition_refuses(self) -> None:
        for transitional in ("activating", "deactivating"):
            report = self._run(self._binary(), active_state=transitional)
            self.assertFalse(report["permitted"], transitional)
            self.assertEqual(self._gate(report, "daemon-state")["state"], "REFUSE", transitional)

    def test_an_unreachable_user_manager_refuses(self) -> None:
        report = self._run(self._binary(), systemctl_fails=True)
        self.assertFalse(report["permitted"])
        self.assertEqual(self._gate(report, "daemon-state")["state"], "UNKNOWN")
        self.assertEqual(self._gate(report, "no-world-units")["state"], "UNKNOWN")

    # ---- a stopped daemon does not blind the store gates -------------------------------------------
    def test_a_quiet_daemon_still_refuses_on_an_open_transaction_read_from_disk(self) -> None:
        (self.state / "transactions/t1.json").write_text(
            json.dumps({"transactionId": "t1", "state": "PREPARED"}), encoding="utf-8")
        report = self._run(self._binary(silent=True), "--daemon-down-unchecked", active_state="inactive")
        self.assertFalse(report["permitted"])
        gate = self._gate(report, "no-open-transactions")
        self.assertEqual(gate["state"], "REFUSE")
        self.assertIn("t1", gate["observed"])

    def test_a_quiet_daemon_leaves_integrity_unobservable_and_that_refuses(self) -> None:
        report = self._run(self._binary(silent=True), active_state="inactive")
        self.assertFalse(report["permitted"])
        for name in ("recovery-clean", "store-integrity", "root-integrity", "no-unsupervised-worlds"):
            self.assertEqual(self._gate(report, name)["state"], "UNKNOWN", name)
        self.assertEqual(self._gate(report, "no-open-transactions")["state"], "OK",
                         "open transactions ARE answerable offline and must still be checked")

    def test_the_unobservable_gates_can_be_waived_only_deliberately(self) -> None:
        report = self._run(self._binary(silent=True), "--daemon-down-unchecked", active_state="inactive")
        self.assertTrue(report["permitted"], report["refused"])
        self.assertIn("--daemon-down-unchecked", self._gate(report, "store-integrity")["detail"])

    def test_a_socket_present_with_a_silent_cli_is_not_quiet(self) -> None:
        self.socket.write_text("", encoding="utf-8")
        report = self._run(self._binary(silent=True), "--daemon-down-unchecked", active_state="inactive")
        self.assertFalse(report["permitted"])
        self.assertEqual(self._gate(report, "status-readable")["state"], "UNKNOWN")

    def test_a_running_job_is_seen_even_when_the_unit_is_inactive(self) -> None:
        status = {**HEALTHY_STATUS, "jobs": [{"world": "w", "state": "RUNNING"}]}
        report = self._run(self._binary(status=status), active_state="inactive")
        self.assertFalse(report["permitted"], "a job under a directly-launched daemon must still refuse")
        self.assertEqual(self._gate(report, "no-active-jobs")["state"], "REFUSE")

    # ---- live work ----------------------------------------------------------------------------------
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

    def test_a_leftover_world_unit_refuses(self) -> None:
        report = self._run(self._binary(), units="worldline-abc.service loaded active running a world\n")
        self.assertFalse(report["permitted"])
        self.assertEqual(self._gate(report, "no-world-units")["state"], "REFUSE")

    # ---- transactional and store state ----------------------------------------------------------------
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

    # ---- ghosts fork a world mid-upgrade ---------------------------------------------------------------
    def test_enabled_ghosts_refuse_unless_explicitly_allowed(self) -> None:
        enabled = {"enabled": True, "agent": "codex"}
        report = self._run(self._binary(ghost=enabled))
        self.assertFalse(report["permitted"])
        self.assertEqual(self._gate(report, "ghosts-quiet")["state"], "REFUSE")
        allowed = self._run(self._binary(ghost=enabled), "--allow-ghosts")
        self.assertEqual(self._gate(allowed, "ghosts-quiet")["state"], "OK")

    # ---- the backup estimate describes what is actually copied ------------------------------------------
    def test_backup_space_sizes_payloads_only_when_they_will_be_copied(self) -> None:
        (self.share / "big.bin").write_bytes(b"x" * 4096)
        (self.state / "small.bin").write_bytes(b"x" * 16)
        without = self._run(self._binary())
        self.assertEqual(without["payloadBytes"], 0)
        self.assertGreaterEqual(without["stateBytes"], 16)
        with_payloads = self._run(self._binary(), "--with-payloads")
        self.assertGreaterEqual(with_payloads["payloadBytes"], 4096)

    def test_an_absent_state_directory_refuses_rather_than_reporting_nothing_to_do(self) -> None:
        report = self._run(self._binary(), "--state-dir", str(self.root / "nowhere"))
        self.assertFalse(report["permitted"])
        self.assertEqual(self._gate(report, "backup-space")["state"], "REFUSE")

    # ---- the report names what refused -------------------------------------------------------------------
    def test_refusal_report_names_the_failing_gates(self) -> None:
        status = {**HEALTHY_STATUS, "jobs": [{"world": "w", "state": "RUNNING"}]}
        report = self._run(self._binary(status=status))
        self.assertIn("no-active-jobs", [r["gate"] for r in report["refused"]])
        self.assertTrue(all("state" in r and "detail" in r for r in report["gates"]))


if __name__ == "__main__":
    unittest.main()
