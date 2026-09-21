"""Supervision outcome against the REAL user manager: disposable transient units named like
WORLDLINE's, launched and observed through the same adapter the daemon uses. Skipped when no
user manager answers. Identity is read from the manager (`show`) and its journal."""
from __future__ import annotations

import os
import subprocess
import time
import unittest
import uuid

from worldline.linux.systemd import SystemdAdapter


def _manager_answers() -> bool:
    try:
        SystemdAdapter().verify_manager()
        return True
    except Exception:  # noqa: BLE001
        return False


@unittest.skipUnless(_manager_answers(), "no user service manager answers")
class RealManagerSupervisionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = SystemdAdapter()
        self.instance = str(uuid.uuid4())
        self.unit = f"worldline-{self.instance}.service"
        self.addCleanup(lambda: subprocess.run(["/usr/bin/systemctl", "--user", "stop", self.unit], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))

    def run_and_classify(self, argv: list[str], *, stop_after: float | None = None) -> tuple[dict, int]:
        process = self.adapter.launch(self.instance, argv, description="worldline-lab real supervision test")
        self.addCleanup(lambda: [s.close() for s in (process.launcher.stdin, process.launcher.stdout, process.launcher.stderr) if s is not None])
        process.launcher.stdin.close()
        if stop_after is not None:
            time.sleep(stop_after)
            identity = self.adapter.metadata(self.unit)
            self.assertEqual(identity.get("ActiveState"), "active", identity)
            self.assertTrue(identity.get("InvocationID"), identity)
            self.assertIn(self.unit, identity.get("ControlGroup", ""), identity)
            self.adapter.stop(self.unit)
        code = process.launcher.wait(timeout=60)
        return self.adapter.outcome(process, code, stopped=stop_after is not None), code

    def test_immediate_successful_completion_and_collection_before_inspection(self) -> None:
        outcome, code = self.run_and_classify(["/bin/true"])
        self.assertEqual(code, 0)
        self.assertEqual(self.adapter.metadata(self.unit).get("ActiveState"), "inactive", "expected the unit to be collected already")
        self.assertEqual((outcome["kind"], outcome["started"], outcome["result"], outcome["source"]), ("SUPERVISED", True, "success", "journal"))
        self.assertTrue(all(e["managerPid"] for e in outcome["events"]))

    def test_immediate_application_failure(self) -> None:
        outcome, code = self.run_and_classify(["/bin/sh", "-c", "exit 3"])
        self.assertEqual(code, 3)
        self.assertEqual((outcome["kind"], outcome["exitCode"], outcome["exitStatus"], outcome["result"]), ("SUPERVISED", "exited", 3, "failure"))

    def test_successful_agent_printing_failed_to_on_both_streams(self) -> None:
        outcome, code = self.run_and_classify(["/bin/sh", "-c", 'echo "Failed to connect to bus (agent stdout)"; echo "Failed to start transient service unit (agent stderr)" >&2; exit 0'])
        self.assertEqual(code, 0)
        self.assertEqual((outcome["kind"], outcome["result"]), ("SUPERVISED", "success"))

    def test_cancellation_during_startup(self) -> None:
        outcome, _code = self.run_and_classify(["/usr/bin/sleep", "30"], stop_after=0.4)
        self.assertEqual((outcome["kind"], outcome["stoppedByManager"], outcome["result"]), ("SUPERVISED", True, "stopped"))
        self.assertNotEqual(self.adapter.metadata(self.unit).get("ActiveState"), "active")

    def test_launcher_failure_with_a_reachable_manager_is_launch_failed(self) -> None:
        # Occupy the unit name first: systemd-run then fails to start the transient unit and the
        # manager records nothing new for it inside the window.
        subprocess.run(["/usr/bin/systemd-run", "--user", f"--unit={self.unit}", "--collect", "--quiet", "/usr/bin/sleep", "30"], check=True)
        time.sleep(0.3)
        process = self.adapter.launch(self.instance, ["/bin/true"], description="collides")
        self.addCleanup(lambda: [s.close() for s in (process.launcher.stdin, process.launcher.stdout, process.launcher.stderr) if s is not None])
        process.launcher.stdin.close()
        code = process.launcher.wait(timeout=30)
        outcome = self.adapter.outcome(process, code)
        self.assertEqual((outcome["kind"], outcome["started"], code), ("LAUNCH_FAILED", False, 1))
        self.assertIn("already loaded", outcome["launcherStderr"])


if __name__ == "__main__":
    unittest.main()
