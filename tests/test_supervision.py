"""Supervision is required, not best effort (worldline-lab BREAKWATER, 2026-09-21).

The user manager's global health (`is-system-running`) is not the question; whether it can be
queried and takes units is. These tests drive SystemdAdapter with fake executables so no real
manager state is touched; the lab's D8/D8b/D8c drills observe the same through /proc and the
real manager."""
from __future__ import annotations

import os
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest

from worldline.errors import WorldlineError
from worldline.linux.systemd import SystemdAdapter


def _script(directory: Path, name: str, body: str) -> str:
    path = directory / name
    path.write_text("#!/bin/sh\n" + body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return str(path)


SYSTEMCTL_DEGRADED = '''
case "$2" in
  is-system-running) echo degraded; exit 1 ;;
  show)
    if [ "$3" = "--property=Version" ]; then printf 'Version=257\\nNFailedUnits=1\\n'; exit 0; fi
    printf 'LoadState=not-found\\nActiveState=inactive\\n'; exit 0 ;;
  *) exit 0 ;;
esac
'''
SYSTEMCTL_DOWN = 'echo "Failed to connect to bus: No such file or directory" >&2; exit 1\n'
SYSTEMCTL_UNIT_SEEN = '''
case "$2" in
  is-system-running) echo running; exit 0 ;;
  show)
    if [ "$3" = "--property=Version" ]; then printf 'Version=257\\nNFailedUnits=0\\n'; exit 0; fi
    printf 'LoadState=loaded\\nActiveState=active\\n'; exit 0 ;;
  *) exit 0 ;;
esac
'''


class SupervisionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-supervision-")
        self.directory = Path(self.temporary.name)
        self.adapter = SystemdAdapter()
        self.adapter.environment = {**os.environ, "XDG_RUNTIME_DIR": self.temporary.name}

    def tearDown(self) -> None:
        self.temporary.cleanup()

    @staticmethod
    def _close(launcher: subprocess.Popen[bytes]) -> None:
        for stream in (launcher.stdin, launcher.stdout, launcher.stderr):
            if stream is not None:
                stream.close()

    def test_degraded_manager_is_available_and_reports_its_state(self) -> None:
        self.adapter.systemctl = _script(self.directory, "systemctl", SYSTEMCTL_DEGRADED)
        result = SystemdAdapter.capability(self.adapter)
        self.assertEqual(result["state"], "AVAILABLE", result)
        self.assertEqual(result["managerState"], "degraded")
        self.assertEqual(result["failedUnits"], 1)
        self.assertEqual(result["managerVersion"], "257")

    def test_unreachable_manager_is_unavailable_by_reason(self) -> None:
        self.adapter.systemctl = _script(self.directory, "systemctl", SYSTEMCTL_DOWN)
        result = SystemdAdapter.capability(self.adapter)
        self.assertEqual(result["state"], "UNAVAILABLE")
        self.assertIn("cannot be reached", result["reason"])
        self.assertIn("Failed to connect to bus", result["reason"])

    def test_launch_refuses_before_spawning_when_manager_is_unreachable(self) -> None:
        self.adapter.systemctl = _script(self.directory, "systemctl", SYSTEMCTL_DOWN)
        marker = self.directory / "spawned"
        self.adapter.systemd_run = _script(self.directory, "systemd-run", f"touch {marker}; exit 0\n")
        with self.assertRaises(WorldlineError) as refused:
            self.adapter.launch("00000000-0000-4000-8000-000000000001", ["/usr/bin/true"], description="t")
        self.assertEqual(refused.exception.code, "SUPERVISION_UNAVAILABLE")
        self.assertFalse(marker.exists(), "a process was spawned although supervision was refused")

    def test_launch_refuses_when_systemd_run_itself_fails(self) -> None:
        self.adapter.systemctl = _script(self.directory, "systemctl", SYSTEMCTL_DEGRADED)
        self.adapter.systemd_run = _script(self.directory, "systemd-run", 'echo "Failed to connect to bus: No such file or directory" >&2; exit 1\n')
        with self.assertRaises(WorldlineError) as refused:
            self.adapter.launch("00000000-0000-4000-8000-000000000002", ["/usr/bin/true"], description="t")
        self.assertEqual(refused.exception.code, "SUPERVISION_UNAVAILABLE")
        self.assertIn("Failed to connect to bus", refused.exception.message)

    def test_agent_failure_is_not_mistaken_for_missing_supervision(self) -> None:
        self.adapter.systemctl = _script(self.directory, "systemctl", SYSTEMCTL_DEGRADED)
        self.adapter.systemd_run = _script(self.directory, "systemd-run", 'echo boom >&2; exit 2\n')
        process = self.adapter.launch("00000000-0000-4000-8000-000000000003", ["/usr/bin/false"], description="t")
        self.addCleanup(self._close, process.launcher)
        self.assertEqual(process.launcher.wait(), 2)
        self.assertEqual(process.stderr_prelude, b"boom\n")
        self.assertFalse(process.supervision_confirmed)

    def test_unit_seen_by_manager_is_confirmed(self) -> None:
        self.adapter.systemctl = _script(self.directory, "systemctl", SYSTEMCTL_UNIT_SEEN)
        self.adapter.systemd_run = _script(self.directory, "systemd-run", "sleep 0.3; exit 0\n")
        process = self.adapter.launch("00000000-0000-4000-8000-000000000004", ["/usr/bin/true"], description="t")
        self.addCleanup(self._close, process.launcher)
        self.assertTrue(process.supervision_confirmed)
        self.assertEqual(process.launcher.wait(), 0)
        self.assertEqual(process.stderr_prelude, b"")


if __name__ == "__main__":
    unittest.main()
