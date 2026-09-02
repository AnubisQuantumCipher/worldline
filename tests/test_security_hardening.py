from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from worldline.controller import RuntimeController
from worldline.core import Core
from worldline.errors import WorldlineError
from worldline.linux.git import GitAdapter
from worldline.model import validate_alias, validate_user_alias
from worldline.paths import WorldlinePaths
from worldline.roots import RootManager
from worldline.store import StateStore


class GitConfigExecutionHardening(unittest.TestCase):
    """A hostile repository's .git/config must not execute commands during inspection.

    git runs config-named programs (core.fsmonitor on status, diff.external / textconv on diff)
    during ordinary inspection, and WORLDLINE inspects a repo host-side, before the operator
    confirms `init`/`root add`. GitAdapter._run neutralizes every exec-capable knob.
    """

    def setUp(self) -> None:
        if subprocess.run(["git", "--version"], capture_output=True).returncode != 0:
            self.skipTest("git is unavailable")
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-githard-")
        self.base = Path(self.temporary.name)
        self.repo = self.base / "repo"
        self.repo.mkdir()
        self._git("init", "-q", str(self.repo), cwd=None)
        (self.repo / "f.txt").write_text("original\n", encoding="utf-8")
        self._git("add", "f.txt")
        self._git("-c", "user.email=a@b.c", "-c", "user.name=a", "commit", "-qm", "init")
        (self.repo / "f.txt").write_text("changed\n", encoding="utf-8")
        # plant the exec payloads and point the repo config at them
        self.marker_fsmonitor = self.base / "HIT.fsmonitor"
        self.marker_diff = self.base / "HIT.diff"
        for name, marker in (("fsmonitor.sh", self.marker_fsmonitor), ("diff.sh", self.marker_diff)):
            script = self.base / name
            script.write_text(f"#!/bin/sh\ntouch {marker}\n", encoding="utf-8")
            script.chmod(0o755)
        self._git("config", "core.fsmonitor", str(self.base / "fsmonitor.sh"))
        self._git("config", "diff.external", str(self.base / "diff.sh"))

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _git(self, *args: str, cwd: str | None = "repo") -> None:
        base = ["git"] if cwd is None else ["git", "-C", str(self.repo)]
        subprocess.run([*base, *args], check=True, capture_output=True)

    def _adapter(self) -> GitAdapter:
        adapter = object.__new__(GitAdapter)  # only _run is exercised; Core not required
        adapter.executable = "git"
        return adapter

    def test_capture_argv_does_not_execute_repo_config(self) -> None:
        adapter = self._adapter()
        raw = os.fsencode(self.repo)
        # the exact commands GitAdapter.capture runs
        for argv in (
            ("rev-parse", "--is-inside-work-tree"),
            ("status", "--porcelain=v2", "--branch", "-z"),
            ("diff", "--cached", "--binary", "--no-ext-diff", "--no-textconv"),
            ("diff", "--binary", "--no-ext-diff", "--no-textconv"),
        ):
            adapter._run(raw, *argv, check=False)
        self.assertFalse(self.marker_fsmonitor.exists(), "core.fsmonitor executed through hardened _run")
        self.assertFalse(self.marker_diff.exists(), "diff.external executed through hardened _run")

    def test_repo_is_genuinely_armed(self) -> None:
        # An unhardened git status on the same repo must fire fsmonitor, proving the test is live.
        subprocess.run(
            ["git", "-C", str(self.repo), "status", "--porcelain=v2"],
            env={"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")},
            capture_output=True,
        )
        self.assertTrue(self.marker_fsmonitor.exists(), "control did not fire; repo not armed")


class AliasValidation(unittest.TestCase):
    def test_user_alias_rejects_reserved_and_hostile_names(self) -> None:
        for bad in ("PRIME", "prime-abc", "a\nb", "a\tb", "a\x7fb", "z" * 129):
            with self.assertRaises(WorldlineError, msg=f"accepted {bad!r}"):
                validate_user_alias(bad)

    def test_user_alias_accepts_ordinary_names(self) -> None:
        for good in ("alpha", "fix-upload-retry", "world_2", "prim", "PRIMER"):
            self.assertEqual(validate_user_alias(good), good)

    def test_internal_validator_still_allows_prime_generations(self) -> None:
        # WORLDLINE mints prime-<txid> worlds internally; the low-level validator must not block them.
        self.assertEqual(validate_alias("prime-deadbeef"), "prime-deadbeef")
        self.assertEqual(validate_alias("PRIME"), "PRIME")


class RootIntegrityDetection(unittest.TestCase):
    """`doctor` must report a registered root that no longer routes through the live mapping."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-integ-")
        root = Path(self.temporary.name)
        env = {
            "HOME": str(root / "home"),
            "XDG_DATA_HOME": str(root / "data"),
            "XDG_STATE_HOME": str(root / "state"),
            "XDG_CONFIG_HOME": str(root / "config"),
            "XDG_RUNTIME_DIR": str(root / "runtime"),
        }
        for value in env.values():
            Path(value).mkdir(mode=0o700, parents=True, exist_ok=True)
        self.paths = WorldlinePaths.from_environment(env)
        self.core = Core.shared()
        self.store = StateStore(self.paths, self.core)
        self.manager = RootManager(self.paths, self.store, core=self.core, toolchains=())
        self.work = root / "project"
        self.work.mkdir()
        (self.work / "state.txt").write_bytes(b"prime bytes")
        self.manager.register([self.work], confirmed=True)

    def tearDown(self) -> None:
        self.store.close()
        self.temporary.cleanup()

    def _probe(self):
        controller = object.__new__(RuntimeController)
        controller.store = self.store
        controller.paths = self.paths
        return RuntimeController._root_integrity(controller)

    def test_healthy_root_reports_ok(self) -> None:
        report = self._probe()
        self.assertEqual(report["state"], "OK")
        self.assertTrue(self.work.is_symlink())
        self.assertTrue(all(entry["state"] == "OK" for entry in report["roots"]))

    def test_desymlinked_root_reports_broken(self) -> None:
        # Simulate an interrupted `root remove`: the live symlink becomes a real directory.
        resolved = Path(os.path.realpath(self.work))
        self.work.unlink()
        self.work.mkdir()
        (self.work / "state.txt").write_bytes((resolved / "state.txt").read_bytes())
        report = self._probe()
        self.assertEqual(report["state"], "DEGRADED")
        broken = [entry for entry in report["roots"] if entry["state"] == "BROKEN"]
        self.assertEqual(len(broken), 1)
        self.assertIn("collapses would not reach", broken[0]["reason"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
