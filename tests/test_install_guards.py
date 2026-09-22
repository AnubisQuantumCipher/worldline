"""Controls for install.sh's refusals, exercised without performing an install.

These drive the real installer, so what is tested is the shipped shell, not a description of it.

Safety: each run gets a sandbox HOME, an environment scrubbed of every inherited WORLDLINE_*
variable, and a PATH shim whose `gprbuild` and `systemctl` refuse loudly. A guard that fired
correctly never reaches either. A guard that REGRESSED hits the gprbuild shim and fails there, so
the test still cannot touch the real daemon, the real user manager or the real installation — and
the assertion that the build banner never printed is what distinguishes "refused by the guard"
from "refused by the shim".

The ordering these depend on is deliberate: identities are resolved before the build, so an
unpinned or unreachable plugin costs a second rather than a full build.

Coverage limit, stated rather than implied: every control here exercises a guard that runs BEFORE
the build. The post-build sequence — preflight, stopping the daemon, the backup, the swap, the
restart and the identity verification — cannot be reached without a real gprbuild and proof run,
so it is NOT covered by any automated test. `tests/test_preflight.py` covers the preflight in
isolation, `tests/test_rollback.py` covers the recovery path, and the upgrade rehearsal covers
the engine behaviour across versions; the installer's own post-build path is exercised only by
performing an actual installation.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BUILD_BANNER = "== WORLDLINE build =="

SHIM = """#!/usr/bin/env bash
echo "SHIM $(basename "$0") was reached: a guard that should have refused did not" >&2
echo "SHIM-SAW WORLDLINE_CORE_LIB=[${WORLDLINE_CORE_LIB-unset}]"
exit 97
"""


class InstallGuards(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-install-guards-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.home = self.base / "home"
        (self.home / ".local/state/worldline").mkdir(parents=True)
        self.shims = self.base / "shims"
        self.shims.mkdir()
        for name in ("gprbuild", "systemctl", "hyprctl", "omarchy-restart-shell", "omarchy-shell"):
            shim = self.shims / name
            shim.write_text(SHIM, encoding="utf-8")
            os.chmod(shim, 0o755)
        # A throwaway plugin repository, so the plugin guards are about the ref and not about a
        # missing directory.
        self.plugin = self.base / "plugin"
        self.plugin.mkdir()
        self._init_repo(self.plugin, "plugin\n")
        self.plugin_head = self._head(self.plugin)

    # ---- fixtures -------------------------------------------------------------------------------
    def _init_repo(self, root: Path, content: str) -> None:
        def run(*args: str) -> None:
            subprocess.run(["git", "-C", str(root), *args], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        run("init", "-q")
        run("symbolic-ref", "HEAD", "refs/heads/main")  # the runner's init.defaultBranch is not main
        (root / "README.md").write_text(content, encoding="utf-8")
        run("add", "-A")
        run("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "init")

    def _head(self, root: Path) -> str:
        return subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                              stdout=subprocess.PIPE, text=True, check=True).stdout.strip()

    def engine_copy(self, *, as_git_repo: bool = True, inside: Path | None = None) -> Path:
        """A self-contained copy of this engine's tracked files, so guards about the ENGINE
        checkout are deterministic instead of depending on the state of the worktree running the
        tests. The installer under test is this repository's own install.sh, copied verbatim."""
        destination = (inside or self.base) / "engine-copy"
        destination.mkdir(parents=True)
        listing = subprocess.run(["git", "-C", str(REPO), "ls-files", "-z"],
                                 stdout=subprocess.PIPE, check=True).stdout
        for raw in listing.split(b"\0"):
            if not raw:
                continue
            source = REPO / raw.decode()
            if not source.is_file():
                continue
            target = destination / raw.decode()
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        if as_git_repo:
            def run(*args: str) -> None:
                subprocess.run(["git", "-C", str(destination), *args], check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            run("init", "-q")
            run("symbolic-ref", "HEAD", "refs/heads/main")
            run("add", "-A")
            run("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "engine")
        return destination

    def _run(self, env_extra: dict, root: Path | None = None, timeout: int = 120) -> subprocess.CompletedProcess:
        # Every inherited WORLDLINE_* variable is dropped: a variable set in the developer's shell
        # must not be able to decide whether one of these controls passes.
        env = {k: v for k, v in os.environ.items() if not k.startswith("WORLDLINE_")}
        env.update({
            "HOME": str(self.home),
            "PATH": f"{self.shims}:{os.environ.get('PATH', '/usr/bin')}",
            "WORLDLINE_PLUGIN_SRC": str(self.plugin),
            "GNAT_ENV": "/nonexistent",
            # These cases are about other guards; the dirty-worktree guard is covered separately.
            "WORLDLINE_ALLOW_DIRTY": "1",
        })
        env.update(env_extra)
        installer = (root or REPO) / "install.sh"
        return subprocess.run(["bash", str(installer)], env=env, stdin=subprocess.DEVNULL,
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
        engine = self.engine_copy()
        (engine / "README.md").write_text("an uncommitted local edit\n", encoding="utf-8")
        proc = self._run({"WORLDLINE_PLUGIN_REF": self.plugin_head, "WORLDLINE_ALLOW_DIRTY": "0"}, root=engine)
        self.assert_refused_before_building(proc, "uncommitted changes")
        self.assertIn("README.md", proc.stdout, "the refusal must name what is uncommitted")

    def test_a_clean_worktree_is_identified_by_its_own_commit(self) -> None:
        engine = self.engine_copy()
        proc = self._run({"WORLDLINE_PLUGIN_REF": self.plugin_head, "WORLDLINE_ALLOW_DIRTY": "0"}, root=engine)
        self.assertIn(f"install: engine {self._head(engine)}", proc.stdout)
        self.assertIn(BUILD_BANNER, proc.stdout)

    def test_an_enclosing_repositorys_head_is_not_claimed_as_the_engine_commit(self) -> None:
        # Unpacking a release archive inside another repository must not make that repository's
        # HEAD the recorded engine identity: a false identity is worse than none.
        outer = self.base / "outer"
        outer.mkdir()
        self._init_repo(outer, "some unrelated project\n")
        engine = self.engine_copy(as_git_repo=False, inside=outer)
        proc = self._run({"WORLDLINE_PLUGIN_REF": self.plugin_head}, root=engine)
        self.assertNotIn(self._head(outer), proc.stdout, "it claimed the enclosing repository's commit")
        self.assertIn("install: engine unknown", proc.stdout)
        self.assertIn("is not a git checkout of its own", proc.stdout)
        self.assertIn(BUILD_BANNER, proc.stdout, "an unidentified engine is reported, not refused")

    # ---- the environment must not be able to redirect what is proved --------------------------
    def test_a_caller_supplied_core_library_is_dropped(self) -> None:
        # Executed, not grepped: the build shim reports the value it actually inherited, so this
        # fails if the `unset` is removed, moved after the build, or stops taking effect.
        proc = self._run({"WORLDLINE_PLUGIN_REF": self.plugin_head,
                          "WORLDLINE_CORE_LIB": "/tmp/somewhere-else/libworldline_core.so"})
        self.assertIn(BUILD_BANNER, proc.stdout)
        self.assertIn("SHIM-SAW WORLDLINE_CORE_LIB=[unset]", proc.stdout,
                      "the build inherited a caller-supplied library path, so the gates would not"
                      f" exercise the library this build produced:\n{proc.stdout[-600:]}")


if __name__ == "__main__":
    unittest.main()
