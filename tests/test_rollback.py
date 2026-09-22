"""Controls for scripts/rollback.sh, exercised against a sandbox installation.

Rollback is the recovery path: it runs when an install has already gone wrong, which is the worst
possible moment to discover that it was never tested. These drive the real script, so what is
covered is the shipped shell rather than a description of it.

Safety: every run gets its own HOME, its own XDG_RUNTIME_DIR and a PATH shim for `systemctl` that
tracks one unit's state and creates or removes the socket the way the daemon would. Nothing here
can reach the real user manager, the real daemon or the real installation. The backup manifests
are written by the shipped `backup_manifest.py`, not hand-rolled, so a manifest the installer
could not actually produce cannot make a test pass.
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROLLBACK = REPO / "scripts/rollback.sh"
MANIFEST = REPO / "scripts/backup_manifest.py"

SYSTEMCTL = """#!/usr/bin/env bash
# Faithful enough for rollback.sh: it records every invocation, tracks one unit's active state and
# creates or removes the socket, so the script's wait loops resolve immediately instead of idling.
echo "$*" >> "$SYSTEMCTL_LOG"
verb=""
for a in "$@"; do
  case "$a" in -*) continue ;; esac
  verb="$a"; break
done
case "$verb" in
  is-active) [[ "$(cat "$SYSTEMCTL_STATE")" == "active" ]] ;;
  stop) echo inactive > "$SYSTEMCTL_STATE"; rm -f "$SYSTEMCTL_SOCKET" ;;
  start)
    [[ "${SYSTEMCTL_START_FAILS:-0}" == "1" ]] && { echo "start refused" >&2; exit 1; }
    echo active > "$SYSTEMCTL_STATE"
    python3 -c 'import os,socket,sys
p = sys.argv[1]
os.makedirs(os.path.dirname(p), exist_ok=True)
socket.socket(socket.AF_UNIX).bind(p)' "$SYSTEMCTL_SOCKET"
    ;;
  list-units) cat "$SYSTEMCTL_UNITS" 2>/dev/null || true ;;
  *) : ;;
esac
"""

LAUNCHER_OK = """#!/usr/bin/env bash
echo '{"schemaVersion": 1, "daemon": {"version": "1.2.2"}}'
"""


class RollbackControls(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-rollback-")
        self.addCleanup(self.temporary.cleanup)
        base = Path(self.temporary.name)
        self.home = base / "home"
        for relative in (".local/bin", ".local/lib/worldline/runtime/worldline", ".local/state/worldline",
                         ".local/share/worldline", ".config/systemd/user", ".config/omarchy", ".config/hypr"):
            (self.home / relative).mkdir(parents=True, exist_ok=True)

        # An AF_UNIX path is capped at ~108 bytes, so the runtime directory has to be short. If the
        # session runtime directory is unusable the control says so rather than pretending to pass.
        runtime_base = Path(os.environ.get("XDG_RUNTIME_DIR") or f"/run/user/{os.getuid()}")
        if not os.access(runtime_base, os.W_OK):
            self.skipTest(f"{runtime_base} is not writable, so the daemon socket cannot be simulated")
        self.runtime = Path(tempfile.mkdtemp(prefix="wlrb-", dir=runtime_base))
        self.addCleanup(lambda: subprocess.run(["rm", "-rf", str(self.runtime)], check=False))
        self.socket = self.runtime / "worldline/worldlined.sock"
        if len(str(self.socket)) > 100:
            self.skipTest("the simulated socket path would exceed the AF_UNIX limit")

        # The installation being rolled back FROM: version 9.9.9, which must disappear.
        self.destination = self.home / ".local/lib/worldline"
        self._write_runtime(self.destination, "9.9.9")
        (self.home / ".local/bin/worldline").write_text("#!/bin/sh\nexit 3\n", encoding="utf-8")
        os.chmod(self.home / ".local/bin/worldline", 0o755)
        (self.home / ".local/bin/worldlined").write_text("#!/bin/sh\nexit 3\n", encoding="utf-8")
        self.unit = self.home / ".config/systemd/user/worldlined.service"
        self.unit.write_text("[Service]\nExecStart=/new\n", encoding="utf-8")
        (self.home / ".config/omarchy/shell.json").write_text('{"new": true}\n', encoding="utf-8")
        (self.home / ".config/hypr/bindings.lua").write_text("-- new\n", encoding="utf-8")
        (self.home / ".local/state/worldline/store.sqlite").write_text("AFTER THE INSTALL\n", encoding="utf-8")

        # The plugin, with the commit the backup will name and a later one checked out.
        self.plugin = self.home / ".config/omarchy/plugins/khephri.worldline"
        self.plugin.mkdir(parents=True)
        self._git("init", "-q")
        (self.plugin / "README.md").write_text("old\n", encoding="utf-8")
        self._git("add", "-A")
        self._git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "old")
        self.old_plugin_commit = self._git_out("rev-parse", "HEAD")
        (self.plugin / "README.md").write_text("new\n", encoding="utf-8")
        self._git("add", "-A")
        self._git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "new")
        self.new_plugin_commit = self._git_out("rev-parse", "HEAD")

        self.shims = base / "shims"
        self.shims.mkdir()
        systemctl = self.shims / "systemctl"
        systemctl.write_text(SYSTEMCTL, encoding="utf-8")
        os.chmod(systemctl, 0o755)
        self.systemctl_log = base / "systemctl.log"
        self.systemctl_log.write_text("", encoding="utf-8")
        self.systemctl_state = base / "unit-active"
        self.systemctl_state.write_text("active\n", encoding="utf-8")
        self.systemctl_units = base / "transient-units"
        self.systemctl_units.write_text("", encoding="utf-8")

    # ---- fixture helpers -----------------------------------------------------------------------
    def _git(self, *args: str) -> None:
        subprocess.run(["git", "-C", str(self.plugin), *args], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def _git_out(self, *args: str) -> str:
        return subprocess.run(["git", "-C", str(self.plugin), *args], check=True,
                              stdout=subprocess.PIPE, text=True).stdout.strip()

    def _write_runtime(self, root: Path, version: str) -> None:
        package = root / "runtime/worldline"
        package.mkdir(parents=True, exist_ok=True)
        (package / "__init__.py").write_text(f'__version__ = "{version}"\n', encoding="utf-8")

    def make_backup(self, *, version: str = "1.2.2", with_state: bool = True, with_manifest: bool = True,
                    plugin_commit: str | None = None, unit_enabled: str = "enabled",
                    unit_active: str = "active", with_payloads: bool = False) -> Path:
        """A backup exactly as install.sh lays one out, with its manifest written by the real script."""
        backup = self.home / ".local/state/worldline/install-backups/20260922T000000Z-1"
        backup.mkdir(parents=True)
        self._write_runtime(backup / "lib-worldline", version)
        for launcher, body in (("worldline", LAUNCHER_OK), ("worldlined", "#!/bin/sh\nexit 0\n")):
            (backup / launcher).write_text(body, encoding="utf-8")
            os.chmod(backup / launcher, 0o755)
        (backup / "worldlined.service").write_text("[Service]\nExecStart=/old\n", encoding="utf-8")
        (backup / "shell.json").write_text('{"old": true}\n', encoding="utf-8")
        (backup / "bindings.lua").write_text("-- old\n", encoding="utf-8")
        (backup / "plugin-commit").write_text((plugin_commit or self.old_plugin_commit) + "\n", encoding="utf-8")
        (backup / "unit-state.json").write_text(
            json.dumps({"unitEnabled": unit_enabled, "unitActive": unit_active}) + "\n", encoding="utf-8")
        if with_state:
            store = backup / "state/worldline"
            store.mkdir(parents=True)
            (store / "store.sqlite").write_text("BEFORE THE INSTALL\n", encoding="utf-8")
        if with_payloads:
            payloads = backup / "share/worldline"
            payloads.mkdir(parents=True)
            (payloads / "payload").write_text("BEFORE THE INSTALL\n", encoding="utf-8")
        (backup / "payload-inventory.txt").write_text("4096\t/share/worldline/payloads\n", encoding="utf-8")
        if with_manifest:
            subprocess.run(["python3", str(MANIFEST), str(backup), str(self.destination),
                            str(self.home / ".local/bin/worldline"), str(self.home / ".local/bin/worldlined"),
                            str(self.unit), str(self.home / ".config/omarchy/shell.json"),
                            str(self.home / ".config/hypr/bindings.lua")], check=True)
        return backup

    def run_rollback(self, backup: Path, *extra: str, env_extra: dict | None = None) -> subprocess.CompletedProcess:
        env = {
            **os.environ,
            "HOME": str(self.home),
            "PATH": f"{self.shims}:{os.environ.get('PATH', '/usr/bin')}",
            "XDG_RUNTIME_DIR": str(self.runtime),
            "SYSTEMCTL_LOG": str(self.systemctl_log),
            "SYSTEMCTL_STATE": str(self.systemctl_state),
            "SYSTEMCTL_SOCKET": str(self.socket),
            "SYSTEMCTL_UNITS": str(self.systemctl_units),
            "WORLDLINE_NO_SHELL_RESTART": "1",
            **(env_extra or {}),
        }
        return subprocess.run(["bash", str(ROLLBACK), str(backup), *extra], env=env, stdin=subprocess.DEVNULL,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=120)

    def installed_version(self) -> str:
        return (self.destination / "runtime/worldline/__init__.py").read_text(encoding="utf-8").split('"')[1]

    def systemctl_calls(self) -> list[str]:
        return self.systemctl_log.read_text(encoding="utf-8").splitlines()

    # ---- a backup that cannot be trusted must not be restored -----------------------------------
    def test_a_backup_without_a_manifest_is_refused(self) -> None:
        backup = self.make_backup(with_manifest=False)
        proc = self.run_rollback(backup)
        self.assertNotEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("never completed", proc.stdout)
        self.assertEqual(self.installed_version(), "9.9.9", "a refused rollback must change nothing")

    def test_a_backup_that_failed_to_capture_something_is_refused(self) -> None:
        backup = self.make_backup()
        manifest = json.loads((backup / "backup-manifest.json").read_text(encoding="utf-8"))
        manifest["uncaptured"] = ["lib-worldline"]
        (backup / "backup-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        proc = self.run_rollback(backup)
        self.assertNotEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("incomplete", proc.stdout)
        self.assertEqual(self.installed_version(), "9.9.9")

    def test_state_rollback_is_refused_when_the_backup_holds_no_state(self) -> None:
        backup = self.make_backup(with_state=False)
        proc = self.run_rollback(backup, "--with-state")
        self.assertNotEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("holds no state copy", proc.stdout)
        self.assertEqual(self.installed_version(), "9.9.9")

    def test_leftover_world_units_are_refused_rather_than_torn_down(self) -> None:
        self.systemctl_units.write_text("worldline-alpha.service loaded active running\n", encoding="utf-8")
        proc = self.run_rollback(self.make_backup())
        self.assertNotEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("worldline-alpha.service", proc.stdout)
        self.assertEqual(self.installed_version(), "9.9.9")

    # ---- the engine rollback ---------------------------------------------------------------------
    def test_the_engine_is_restored_and_the_store_is_left_alone(self) -> None:
        proc = self.run_rollback(self.make_backup())
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertEqual(self.installed_version(), "1.2.2")
        self.assertIn("[Service]\nExecStart=/old", self.unit.read_text(encoding="utf-8"))
        self.assertIn('{"old": true}', (self.home / ".config/omarchy/shell.json").read_text(encoding="utf-8"))
        self.assertEqual(self._git_out("rev-parse", "HEAD"), self.old_plugin_commit)
        self.assertIn("AFTER THE INSTALL",
                      (self.home / ".local/state/worldline/store.sqlite").read_text(encoding="utf-8"),
                      "an engine rollback must not quietly discard recorded work")
        self.assertIn("was NOT restored", proc.stdout, "it must say the store was left as it is")

    def test_the_partial_install_marker_is_cleared_so_the_next_install_can_proceed(self) -> None:
        marker = self.home / ".local/state/worldline/install-incomplete"
        marker.write_text("started earlier\n", encoding="utf-8")
        proc = self.run_rollback(self.make_backup())
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertFalse(marker.exists(), "while the marker exists the next install refuses, so recovery cannot close")

    # ---- the data rollback -----------------------------------------------------------------------
    def test_state_rollback_restores_the_store_and_keeps_the_superseded_one(self) -> None:
        proc = self.run_rollback(self.make_backup(), "--with-state")
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("BEFORE THE INSTALL",
                      (self.home / ".local/state/worldline/store.sqlite").read_text(encoding="utf-8"))
        aside = sorted((self.home / ".local/state").glob(".worldline-superseded-*"))
        self.assertTrue(aside, "a data rollback must itself be reversible")
        self.assertIn("AFTER THE INSTALL",
                      (aside[0] / "worldline/store.sqlite").read_text(encoding="utf-8"))

    def test_state_rollback_says_payloads_were_not_captured_rather_than_restoring_a_mismatch(self) -> None:
        proc = self.run_rollback(self.make_backup(), "--with-state")
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("payload data was NOT captured", proc.stdout)
        self.assertIn("payload-inventory.txt", proc.stdout)

    def test_payloads_are_restored_when_the_backup_actually_holds_them(self) -> None:
        (self.home / ".local/share/worldline/payload").write_text("AFTER THE INSTALL\n", encoding="utf-8")
        proc = self.run_rollback(self.make_backup(with_payloads=True), "--with-state")
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("BEFORE THE INSTALL",
                      (self.home / ".local/share/worldline/payload").read_text(encoding="utf-8"))
        aside = sorted((self.home / ".local/share").glob(".worldline-superseded-*"))
        self.assertTrue(aside, "the superseded payloads must be kept, not deleted")

    # ---- the daemon is put back the way it was, not simply switched on ---------------------------
    def test_a_daemon_that_was_inactive_before_the_install_is_not_started(self) -> None:
        proc = self.run_rollback(self.make_backup(unit_active="inactive"))
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("NOT starting it", proc.stdout)
        self.assertNotIn("start worldlined.service", self.systemctl_calls())
        self.assertEqual(self.installed_version(), "1.2.2", "the engine is still rolled back")

    def test_a_unit_that_was_disabled_before_the_install_is_left_disabled(self) -> None:
        proc = self.run_rollback(self.make_backup(unit_enabled="disabled"))
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("leaving it disabled", proc.stdout)
        self.assertIn("--user disable worldlined.service", self.systemctl_calls())
        self.assertNotIn("--user enable worldlined.service", self.systemctl_calls())

    def test_an_unrecorded_enablement_is_named_rather_than_guessed(self) -> None:
        backup = self.make_backup()
        (backup / "unit-state.json").unlink()
        proc = self.run_rollback(backup)
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("records no unit enablement", proc.stdout)
        self.assertNotIn("--user enable worldlined.service", self.systemctl_calls())

    def test_a_daemon_that_does_not_come_back_is_reported_as_a_failure(self) -> None:
        proc = self.run_rollback(self.make_backup(), env_extra={"SYSTEMCTL_START_FAILS": "1"})
        self.assertNotEqual(proc.returncode, 0, proc.stdout)
        self.assertEqual(self.installed_version(), "1.2.2",
                         "the files are restored; it is the restart that failed, and it must say so")

    # ---- the plugin is a separate thing that can fail on its own ---------------------------------
    def test_an_absent_plugin_commit_is_named_and_the_engine_is_still_rolled_back(self) -> None:
        proc = self.run_rollback(self.make_backup(plugin_commit="0" * 40))
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("is not present in", proc.stdout)
        self.assertIn("FAILED (commit absent)", proc.stdout)
        self.assertEqual(self.installed_version(), "1.2.2")
        self.assertEqual(self._git_out("rev-parse", "HEAD"), self.new_plugin_commit,
                         "it must leave the plugin as it is rather than guess")

    def test_a_dirty_plugin_does_not_abort_the_engine_rollback(self) -> None:
        (self.plugin / "README.md").write_text("uncommitted local edit\n", encoding="utf-8")
        proc = self.run_rollback(self.make_backup())
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertEqual(self.installed_version(), "1.2.2",
                         "aborting here would leave the engine half-rolled-back and the daemon stopped")
        self.assertIn("plugin:", proc.stdout, "the summary must state what happened to the plugin")

    # ---- the desktop is told, and a failure there is not hidden ----------------------------------
    def test_a_failing_desktop_restart_is_reported_not_swallowed(self) -> None:
        for name in ("hyprctl", "omarchy-shell"):
            (self.shims / name).write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            os.chmod(self.shims / name, 0o755)
        (self.shims / "omarchy-restart-shell").write_text("#!/bin/sh\necho 'shell restart failed' >&2\nexit 1\n",
                                                          encoding="utf-8")
        os.chmod(self.shims / "omarchy-restart-shell", 0o755)
        proc = self.run_rollback(self.make_backup(), env_extra={"WORLDLINE_NO_SHELL_RESTART": "0"})
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("desktop shell restart FAILED", proc.stdout)
        self.assertIn("desktop shell: FAILED", proc.stdout)


if __name__ == "__main__":
    unittest.main()
