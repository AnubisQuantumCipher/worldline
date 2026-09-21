"""Supervision outcome from structured evidence (worldline-lab BREAKWATER release review).

SIMULATED cases: SystemdAdapter is driven by fake `systemctl`, `systemd-run` and `journalctl`
scripts; nothing here touches the real user manager. Real-manager cases live in
test_supervision_real.py. The rule under test: classification comes from the launcher's exit
status and the manager's own journal entries, never from what the workload printed, and every
wait is bounded."""
from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import time
import unittest

from worldline.errors import WorldlineError
from worldline.linux.systemd import SystemdAdapter


def _script(directory: Path, name: str, body: str) -> str:
    path = directory / name
    path.write_text("#!/bin/sh\n" + body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return str(path)


SYSTEMCTL_OK = '''
case "$2" in
  is-system-running) echo degraded; exit 1 ;;
  show)
    if [ "$3" = "--property=Version" ]; then printf 'Version=261\\nNFailedUnits=1\\n'; exit 0; fi
    printf 'LoadState=not-found\\nActiveState=inactive\\nMainPID=0\\n'; exit 0 ;;
  stop) exit 0 ;;
  *) exit 0 ;;
esac
'''
SYSTEMCTL_DOWN = 'echo "Failed to connect to user scope bus via local transport: No such file or directory" >&2; exit 1\n'


def _journal(entries: list[dict], uid: int) -> str:
    """A fake journalctl printing the manager's entries for whatever unit is asked for."""
    lines = []
    for entry in entries:
        record = {"_SYSTEMD_UNIT": f"user@{uid}.service", "_COMM": "systemd", "_PID": "881", "__REALTIME_TIMESTAMP": str(entry.get("ts", 10**18)), **{k: v for k, v in entry.items() if k != "ts"}}
        lines.append(json.dumps(record))
    if not lines:
        return "exit 0\n"
    return "cat <<'JSONEOF'\n" + "\n".join(lines) + "\nJSONEOF\n"


class SimulatedSupervisionTests(unittest.TestCase):
    """SIMULATION: fake executables stand in for the manager."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-supervision-")
        self.directory = Path(self.temporary.name)
        self.adapter = SystemdAdapter()
        self.adapter.environment = {**os.environ, "XDG_RUNTIME_DIR": self.temporary.name}
        self.adapter.JOURNAL_WINDOW_SECONDS = 0.6  # bounded, and short for tests
        self.adapter.systemctl = _script(self.directory, "systemctl", SYSTEMCTL_OK)
        self.uid = os.getuid()
        self.instance = "00000000-0000-4000-8000-00000000000a"
        self.unit = f"worldline-{self.instance}.service"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def journal(self, *entries: dict) -> None:
        self.adapter.journalctl = _script(self.directory, "journalctl", _journal(list(entries), self.uid))

    def launch(self, systemd_run_body: str):
        self.adapter.systemd_run = _script(self.directory, "systemd-run", systemd_run_body)
        process = self.adapter.launch(self.instance, ["/usr/bin/true"], description="t")
        self.addCleanup(self._close, process.launcher)
        return process

    @staticmethod
    def _close(launcher: subprocess.Popen[bytes]) -> None:
        for stream in (launcher.stdin, launcher.stdout, launcher.stderr):
            if stream is not None:
                stream.close()

    def started(self, *, exit_status: int | None = None, stopped: bool = False) -> list[dict]:
        base = 10**18
        entries = [
            {"MESSAGE_ID": SystemdAdapter.JOURNAL_STARTING, "JOB_TYPE": "start", "USER_UNIT": self.unit, "ts": base},
            {"MESSAGE_ID": SystemdAdapter.JOURNAL_STARTED, "JOB_TYPE": "start", "JOB_RESULT": "done", "USER_UNIT": self.unit, "ts": base + 1},
        ]
        if exit_status is not None:
            entries.append({"MESSAGE_ID": SystemdAdapter.JOURNAL_PROCESS_EXIT, "EXIT_CODE": "exited", "EXIT_STATUS": str(exit_status), "USER_UNIT": self.unit, "ts": base + 2})
            if exit_status:
                entries.append({"MESSAGE_ID": SystemdAdapter.JOURNAL_FAILURE_RESULT, "USER_UNIT": self.unit, "ts": base + 3})
        if stopped:
            entries.append({"MESSAGE_ID": SystemdAdapter.JOURNAL_STOPPING, "JOB_TYPE": "stop", "USER_UNIT": self.unit, "ts": base + 2})
            entries.append({"MESSAGE_ID": SystemdAdapter.JOURNAL_STOPPED, "JOB_TYPE": "stop", "JOB_RESULT": "done", "USER_UNIT": self.unit, "ts": base + 3})
        return entries

    def test_capability_reports_a_degraded_manager_as_available(self) -> None:
        result = SystemdAdapter.capability(self.adapter)
        self.assertEqual((result["state"], result["managerState"], result["failedUnits"]), ("AVAILABLE", "degraded", 1))

    def test_capability_unreachable_manager(self) -> None:
        self.adapter.systemctl = _script(self.directory, "systemctl", SYSTEMCTL_DOWN)
        result = SystemdAdapter.capability(self.adapter)
        self.assertEqual(result["state"], "UNAVAILABLE")
        self.assertIn("cannot be reached", result["reason"])

    def test_preflight_refuses_before_spawning(self) -> None:
        self.adapter.systemctl = _script(self.directory, "systemctl", SYSTEMCTL_DOWN)
        marker = self.directory / "spawned"
        self.adapter.systemd_run = _script(self.directory, "systemd-run", f"touch {marker}; exit 0\n")
        with self.assertRaises(WorldlineError) as refused:
            self.adapter.launch(self.instance, ["/usr/bin/true"], description="t")
        self.assertEqual(refused.exception.code, "SUPERVISION_UNAVAILABLE")
        self.assertFalse(marker.exists())

    def test_immediate_successful_completion(self) -> None:
        self.journal(*self.started())
        process = self.launch("exit 0\n")
        outcome = self.adapter.outcome(process, process.launcher.wait())
        self.assertEqual((outcome["kind"], outcome["started"], outcome["result"], outcome["launcherExit"]), ("SUPERVISED", True, "success", 0))

    def test_immediate_application_failure(self) -> None:
        self.journal(*self.started(exit_status=3))
        process = self.launch("exit 3\n")
        outcome = self.adapter.outcome(process, process.launcher.wait())
        self.assertEqual((outcome["kind"], outcome["exitCode"], outcome["exitStatus"], outcome["result"], outcome["launcherExit"]), ("SUPERVISED", "exited", 3, "failure", 3))

    def test_successful_agent_printing_failed_to_is_supervised_success(self) -> None:
        self.journal(*self.started())
        process = self.launch('echo "Failed to do the thing (stdout)"; echo "Failed to connect to bus (stderr, but from the agent)" >&2; exit 0\n')
        outcome = self.adapter.outcome(process, process.launcher.wait())
        self.assertEqual((outcome["kind"], outcome["result"]), ("SUPERVISED", "success"))
        self.assertEqual(outcome["launcherStderr"], "", "stderr must not be consulted on a supervised outcome")

    def test_delayed_startup_is_not_a_failure(self) -> None:
        # SIMULATION: the unit takes longer than any inspection window to start; the launcher
        # simply keeps waiting, and the journal tells the truth afterwards.
        self.journal(*self.started())
        started = time.monotonic()
        process = self.launch("sleep 1.5; exit 0\n")
        outcome = self.adapter.outcome(process, process.launcher.wait())
        self.assertGreaterEqual(time.monotonic() - started, 1.4)
        self.assertEqual((outcome["kind"], outcome["result"]), ("SUPERVISED", "success"))

    def test_manager_loss_between_preflight_and_launch(self) -> None:
        # SIMULATION: preflight answers, then systemd-run cannot reach the manager and no journal
        # entry ever appears. Classified by exit status + absence of a Started entry, not text.
        self.journal()
        process = self.launch('echo "Failed to connect to user scope bus via local transport: No such file or directory" >&2; exit 1\n')
        outcome = self.adapter.outcome(process, process.launcher.wait())
        self.assertEqual((outcome["kind"], outcome["started"], outcome["launcherExit"]), ("LAUNCH_FAILED", False, 1))
        self.assertIn("Failed to connect", outcome["launcherStderr"])  # diagnostic only

    def test_agent_failure_with_failed_to_text_but_a_started_unit_is_a_workload_failure(self) -> None:
        self.journal(*self.started(exit_status=1))
        process = self.launch('echo "Failed to start transient service unit: forged" >&2; exit 1\n')
        outcome = self.adapter.outcome(process, process.launcher.wait())
        self.assertEqual((outcome["kind"], outcome["exitStatus"]), ("SUPERVISED", 1))

    def test_cancellation_during_startup(self) -> None:
        self.journal(*self.started(stopped=True))
        process = self.launch("sleep 5; exit 0\n")
        self.adapter.stop(process.unit)  # fake systemctl stop: exit 0
        process.launcher.terminate()
        outcome = self.adapter.outcome(process, process.launcher.wait(), stopped=True)
        self.assertEqual((outcome["kind"], outcome["stoppedByManager"], outcome["result"]), ("SUPERVISED", True, "stopped"))

    def test_unit_collected_before_inspection(self) -> None:
        # The fake `systemctl show <unit>` answers not-found (collected); the journal still holds
        # the manager's Started entry, so the outcome is established without a race.
        self.journal(*self.started())
        process = self.launch("exit 0\n")
        self.assertEqual(self.adapter.metadata(process.unit).get("ActiveState"), "inactive")
        outcome = self.adapter.outcome(process, process.launcher.wait())
        self.assertEqual(outcome["kind"], "SUPERVISED")

    def test_unreadable_journal_is_indeterminate_not_a_fallback(self) -> None:
        self.adapter.journalctl = _script(self.directory, "journalctl", "exit 1\n")
        process = self.launch("exit 0\n")
        started = time.monotonic()
        outcome = self.adapter.outcome(process, process.launcher.wait())
        self.assertLess(time.monotonic() - started, 2.0, "an unreadable journal must not wait out the window")
        self.assertEqual((outcome["kind"], outcome["source"]), ("INDETERMINATE", "journal-unavailable"))

    def test_silent_journal_is_bounded_and_indeterminate(self) -> None:
        self.journal()
        process = self.launch("exit 0\n")
        started = time.monotonic()
        outcome = self.adapter.outcome(process, process.launcher.wait())
        self.assertLess(time.monotonic() - started, self.adapter.JOURNAL_WINDOW_SECONDS + 1.0)
        self.assertEqual(outcome["kind"], "INDETERMINATE")


if __name__ == "__main__":
    unittest.main()
