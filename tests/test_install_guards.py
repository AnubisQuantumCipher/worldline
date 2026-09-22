"""Controls for install.sh's refusals, exercised without performing an install.

These drive the real installer, so what is tested is the shipped shell, not a description of it.
Safety: each run gets a sandbox HOME, and a PATH shim whose `gprbuild` and `systemctl` refuse
loudly. A guard that fired correctly never reaches either. A guard that REGRESSED hits the
gprbuild shim and fails there, so the test still cannot touch the real daemon, the real user
manager or the real installation — and the assertion that the build banner never printed is what
distinguishes "refused by the guard" from "refused by the shim".

The ordering these depend on is deliberate: identities are resolved before the build, so an
unpinned or unreachable plugin costs a second rather than a full build.
"""
from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INSTALL = REPO / "install.sh"
BUILD_BANNER = "== WORLDLINE build =="

SHIM = """#!/usr/bin/env bash
echo "SHIM $(basename "$0") was reached: a guard that should have refused did not" >&2
exit 97
"""


class InstallGuards(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-install-guards-")
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name) / "home"
        (self.home / ".local/state/worldline").mkdir(parents=True)
        self.shims = Path(self.temporary.name) / "shims"
        self.shims.mkdir()
        for name in ("gprbuild", "systemctl", "hyprctl", "omarchy-restart-shell", "omarchy-shell"):
            shim = self.shims / name
            shim.write_text(SHIM, encoding="utf-8")
            os.chmod(shim, 0o755)
        # A throwaway plugin repository, so the plugin guards are about the ref and not about a
        # missing directory.
        self.plugin = Path(self.temporary.name) / "plugin"
        self.plugin.mkdir()
        run = lambda *a: subprocess.run(a, cwd=self.plugin, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        run("git", "init", "-q")
        (self.plugin / "README.md").write_text("plugin\n", encoding="utf-8")
        run("git", "add", "-A")
        run("git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "init")
        self.plugin_head = subprocess.run(["git", "-C", str(self.plugin), "rev-parse", "HEAD"],
                                          stdout=subprocess.PIPE, text=True, check=True).stdout.strip()

    def _run(self, env_extra: dict, timeout: int = 90) -> subprocess.CompletedProcess:
        env = {
            **os.environ,
            "HOME": str(self.home),
            "PATH": f"{self.shims}:{os.environ.get('PATH', '/usr/bin')}",
            "WORLDLINE_PLUGIN_SRC": str(self.plugin),
            "GNAT_ENV": "/nonexistent",
            # These cases are about other guards; the dirty-worktree guard is covered separately.
            "WORLDLINE_ALLOW_DIRTY": "1",
            **env_extra,
        }
        env.pop("WORLDLINE_PLUGIN_REF", None)
        env.update(env_extra)
        return subprocess.run(["bash", str(INSTALL)], env=env, stdin=subprocess.DEVNULL,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=timeout)

    def assert_refused_before_building(self, proc: subprocess.CompletedProcess, needle: str) -> None:
        self.assertNotIn(BUILD_BANNER, proc.stdout,
                         "the installer started building before refusing; the guard is too late to be useful")
        self.assertNotIn("SHIM ", proc.stdout, f"a shim was reached, so the guard did not fire:\n{proc.stdout[-600:]}")
        self.assertNotEqual(proc.returncode, 0, proc.stdout[-600:])
        self.assertIn(needle, proc.stdout, proc.stdout[-600:])

    # ---- the plugin is not identified by the engine release -----------------------------------
    def test_unpinned_plugin_is_refused_and_says_how_to_pin_it(self) -> None:
        proc = self._run({})
        self.assert_refused_before_building(proc, "WORLDLINE_PLUGIN_REF is not set")
        self.assertIn("rev-parse main", proc.stdout, "the refusal should show how to pin it")

    def test_unresolvable_plugin_ref_is_refused(self) -> None:
        proc = self._run({"WORLDLINE_PLUGIN_REF": "does-not-exist"})
        self.assert_refused_before_building(proc, "does not resolve to a commit")

    def test_a_moving_ref_is_accepted_only_when_asked_for_explicitly(self) -> None:
        proc = self._run({"WORLDLINE_PLUGIN_ALLOW_MOVING_REF": "1"})
        # It must get PAST the identity gate: reaching the build shim is the proof.
        self.assertIn("WARNING", proc.stdout)
        self.assertIn(BUILD_BANNER, proc.stdout, "an explicitly allowed moving ref should proceed to the build")

    def test_an_exact_plugin_commit_proceeds_past_the_identity_gate(self) -> None:
        proc = self._run({"WORLDLINE_PLUGIN_REF": self.plugin_head})
        self.assertIn(self.plugin_head, proc.stdout)
        self.assertIn(BUILD_BANNER, proc.stdout)

    # ---- a previous install that did not finish ------------------------------------------------
    def test_an_unfinished_previous_install_is_refused(self) -> None:
        marker = self.home / ".local/state/worldline/install-incomplete"
        marker.write_text("started 2026-09-22T00:00:00Z backup=/tmp/some-backup engine=deadbeef\n", encoding="utf-8")
        proc = self._run({"WORLDLINE_PLUGIN_REF": self.plugin_head})
        self.assert_refused_before_building(proc, "a previous install did not finish")
        self.assertIn("/tmp/some-backup", proc.stdout, "the refusal must name the backup to roll back to")

    def test_an_unfinished_previous_install_can_be_overridden_deliberately(self) -> None:
        (self.home / ".local/state/worldline/install-incomplete").write_text("started earlier\n", encoding="utf-8")
        proc = self._run({"WORLDLINE_PLUGIN_REF": self.plugin_head, "WORLDLINE_FORCE_AFTER_PARTIAL": "1"})
        self.assertIn(BUILD_BANNER, proc.stdout)

    # ---- the installed engine must correspond to a commit -------------------------------------
    def test_a_dirty_worktree_is_refused(self) -> None:
        dirty = subprocess.run(["git", "-C", str(REPO), "status", "--porcelain", "--untracked-files=no"],
                               stdout=subprocess.PIPE, text=True).stdout.strip()
        if not dirty:
            self.skipTest("this worktree is clean, so the dirty guard cannot be exercised here")
        proc = self._run({"WORLDLINE_PLUGIN_REF": self.plugin_head, "WORLDLINE_ALLOW_DIRTY": "0"})
        self.assert_refused_before_building(proc, "uncommitted changes")

    # ---- the environment must not be able to redirect what is proved --------------------------
    def test_a_caller_supplied_core_library_is_dropped(self) -> None:
        text = INSTALL.read_text(encoding="utf-8")
        self.assertIn("unset WORLDLINE_CORE_LIB", text)
        self.assertLess(text.index("unset WORLDLINE_CORE_LIB"), text.index(BUILD_BANNER),
                        "the override must be dropped before anything is built or tested with it")


if __name__ == "__main__":
    unittest.main()
