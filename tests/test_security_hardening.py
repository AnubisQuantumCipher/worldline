from __future__ import annotations

import base64
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

from worldline.controller import RuntimeController
from worldline.core import Core, hash_id
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


class GitFilterDriversAreContained(unittest.TestCase):
    """A repository's own config can define `filter.<any name>.clean`, which `.gitattributes`
    applies during `status` and `diff`. No `-c` denylist can name it (review of ff201cd, blocking:
    a world's repository ran commands as the daemon account, host-side). Every git process now runs
    in a bubblewrap sandbox with no network, the system directories read-only, and only the
    inspected root (read-only), its git directories and a private scratch directory from the host.

    The filter lives INSIDE the repository, so the sandbox can run it, and it replaces the file's
    content with a marker: the marker in the captured diff proves the filter ran in the sandbox,
    and the absent marker files prove it wrote nowhere the host can see."""

    MARKER = b"FILTERED-BY-THE-REPOSITORY-CLEAN-DRIVER"

    def setUp(self) -> None:
        if subprocess.run(["git", "--version"], capture_output=True).returncode != 0:
            self.skipTest("git is unavailable")
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-gitfilter-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.repo = self.base / "repo"
        self.repo.mkdir()
        self.git = lambda *args: subprocess.run(["git", "-C", str(self.repo), *args], check=True, capture_output=True)
        self.git("init", "-q")
        (self.repo / "f.txt").write_text("original\n", encoding="utf-8")
        self.git("add", "f.txt")
        self.git("-c", "user.email=a@b.c", "-c", "user.name=a", "commit", "-qm", "init")
        self.outside = self.base / "HIT.outside-root"   # its parent is never mounted in the sandbox
        self.inside = self.repo / "HIT.inside-root"      # the root is bound read-only
        script = self.repo / "filter.sh"
        script.write_text(f"#!/bin/sh\ntouch {self.outside} 2>/dev/null\ntouch {self.inside} 2>/dev/null\n"
                          f"echo {self.MARKER.decode()}\n", encoding="utf-8")
        script.chmod(0o755)
        self.git("config", "filter.evil.clean", str(script))
        (self.repo / ".gitattributes").write_text("f.txt filter=evil\n", encoding="utf-8")
        (self.repo / "f.txt").write_text("changed\n", encoding="utf-8")
        os.utime(self.repo / "f.txt", (1, 1))  # racy stat data makes git re-read, and so re-filter

    def test_the_repository_is_genuinely_armed(self) -> None:
        subprocess.run(["git", "-C", str(self.repo), "diff"], capture_output=True,
                       env={"PATH": "/usr/bin:/bin", "HOME": str(self.base),
                            "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull})
        self.assertTrue(self.outside.exists(), "control did not fire; the filter is not armed")

    def test_a_filter_cannot_make_a_working_sandbox_read_as_broken(self) -> None:
        # Review of 796cb02: stderr starting with `bwrap:` was read as the sandbox failing to start.
        script = self.repo / "filter.sh"
        script.write_text("#!/bin/sh\necho 'bwrap: pretend the sandbox failed' >&2\ncat\n", encoding="utf-8")
        captured = GitAdapter(Core.shared()).capture(self.repo)
        self.assertIsNotNone(captured["head"])

    def test_the_filter_runs_inside_the_sandbox_and_reaches_nothing_outside(self) -> None:
        captured = GitAdapter(Core.shared()).capture(self.repo)
        diff = base64.b64decode(captured["worktreeDiffRawB64"])
        self.assertIn(self.MARKER, diff, "the filter did not run inside the sandbox; nothing was contained")
        self.assertFalse(self.outside.exists(), "a repository filter wrote outside the inspected root")
        self.assertFalse(self.inside.exists(), "a repository filter wrote into the inspected root")


class GitSandboxLayout(unittest.TestCase):
    """What the repository sandbox binds and refuses (reviews of 80007ba and ad64cd2).

    Only a repository's own top-level directory is inspected, with its `.git` a real directory
    inside it. A `.git` FILE names a directory elsewhere, chosen by the content being inspected:
    binding it once put another repository's committed content into a world's recorded facts."""

    SECRET = "SECRET-DEPLOY-KEY-OF-ANOTHER-REPOSITORY"

    def setUp(self) -> None:
        if subprocess.run(["git", "--version"], capture_output=True).returncode != 0:
            self.skipTest("git is unavailable")
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-gitlayout-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.main = self.base / "main"
        self.main.mkdir()
        self.git = lambda *args: subprocess.run(["git", "-C", str(self.main), *args], check=True, capture_output=True)
        self.git("init", "-q", "-b", "main")
        (self.main / "secret.txt").write_text(self.SECRET + "\n", encoding="utf-8")
        (self.main / "sub").mkdir()
        (self.main / "sub" / "f.txt").write_text("in a subdirectory\n", encoding="utf-8")
        self.git("add", "secret.txt", "sub/f.txt")
        self.git("-c", "user.email=a@b.c", "-c", "user.name=a", "commit", "-qm", "init")

    def refused(self, root: Path, code: str) -> WorldlineError:
        with self.assertRaises(WorldlineError) as caught:
            GitAdapter(Core.shared()).capture(root)
        self.assertEqual(caught.exception.code, code)
        return caught.exception

    def test_a_git_file_naming_another_repository_binds_and_leaks_nothing(self) -> None:
        hostile = self.base / "hostile"
        hostile.mkdir()
        (hostile / ".git").write_text(f"gitdir: {self.main / '.git'}\n", encoding="utf-8")
        self.refused(hostile, "GIT_LINKED_WORKTREE_UNSUPPORTED")
        argv = GitAdapter._sandbox(os.fsencode(hostile), None, GitAdapter._task_limit())
        self.assertFalse(any(str(self.main) in item for item in argv), "another repository was bound")

    def test_a_linked_worktree_root_is_refused_by_name(self) -> None:
        linked = self.base / "linked"
        self.git("worktree", "add", "-q", "-b", "feature", str(linked))
        self.refused(linked, "GIT_LINKED_WORKTREE_UNSUPPORTED")

    def test_a_link_named_git_is_refused_by_name(self) -> None:
        linked = self.base / "linked-dir"
        linked.mkdir()
        (linked / ".git").symlink_to(self.main / ".git")
        self.refused(linked, "GIT_LINKED_WORKTREE_UNSUPPORTED")

    def test_a_subdirectory_of_a_repository_is_refused_by_name(self) -> None:
        self.refused(self.main / "sub", "NOT_A_GIT_ROOT")

    def test_an_index_link_that_leaves_the_root_is_not_read(self) -> None:
        outside = self.base / "outside-secret"
        outside.write_bytes(b"DIRC" + b"\0" * 60)
        index = self.main / ".git" / "index"
        index.unlink()
        index.symlink_to(outside)
        self.assertIsNone(GitAdapter._read_index(os.fsencode(self.main)))
        captured = GitAdapter(Core.shared()).capture(self.main)
        self.assertEqual(captured["state"], "CAPTURED")
        self.assertIsNone(captured["indexHash"])

    def test_an_ordinary_index_is_hashed_from_the_bytes_that_are_copied(self) -> None:
        captured = GitAdapter(Core.shared()).capture(self.main)
        expected = hash_id(Core.shared().hash_file(self.main / ".git" / "index"))
        self.assertEqual(captured["indexHash"], expected)

    def test_a_sandbox_that_does_not_start_refuses_instead_of_recording_a_fact(self) -> None:
        # Review of ad64cd2: a launch failure during `rev-parse --verify HEAD` (check=False) was
        # recorded as head=None for a repository that has a HEAD.
        with mock.patch.object(GitAdapter, "_task_limit", return_value=1):
            self.refused(self.main, "GIT_SANDBOX_UNAVAILABLE")

    def test_the_doctor_names_a_layout_the_sandbox_cannot_inspect(self) -> None:
        from worldline.controller import _require_alternates_inside
        alternates = self.main / ".git" / "objects" / "info" / "alternates"
        alternates.parent.mkdir(parents=True, exist_ok=True)
        alternates.write_text(str(self.base / "elsewhere" / "objects") + "\n", encoding="utf-8")
        with self.assertRaises(WorldlineError) as caught:
            _require_alternates_inside(os.fsencode(self.main))
        self.assertEqual(caught.exception.code, "GIT_ALTERNATES_OUTSIDE_ROOT")
        alternates.unlink()
        _require_alternates_inside(os.fsencode(self.main))

    def test_the_sandbox_limits_tasks_and_forbids_nested_user_namespaces(self) -> None:
        limit = GitAdapter._task_limit()
        argv = GitAdapter._sandbox(os.fsencode(self.main), None, limit)
        self.assertTrue(argv[0].endswith("choom"))
        self.assertEqual(argv[1:4], ["-n", "1000", "--"])
        self.assertTrue(argv[4].endswith("prlimit"))
        self.assertEqual(argv[5], f"--nproc={limit}:{limit}")
        self.assertGreater(limit, GitAdapter._uid_tasks(os.getuid()))
        for flag in ("--unshare-user", "--disable-userns"):
            self.assertIn(flag, argv)
        size = argv.index("--size")
        self.assertEqual(argv[size + 1:size + 4], [str(GitAdapter._TMPFS_BYTES), "--tmpfs", "/tmp"])
        # Demonstrated, not assumed: inside the sandbox a new user namespace cannot be made, so
        # a fresh RLIMIT_NPROC count cannot be had that way.
        nested = subprocess.run([*argv, "/usr/bin/unshare", "--user", "/usr/bin/true"],
                                capture_output=True, timeout=30)
        self.assertNotEqual(nested.returncode, 0, nested.stderr)
        plain = subprocess.run([*argv, "/usr/bin/true"], capture_output=True, timeout=30)
        self.assertEqual(plain.returncode, 0, plain.stderr)
        # Inspection shares the daemon's cgroup; the kernel's OOM killer is to pick it first
        # (review of 796cb02).
        score = subprocess.run([*argv, "/bin/sh", "-c", "cat /proc/self/oom_score_adj"],
                               capture_output=True, timeout=30)
        self.assertEqual(score.stdout.strip(), b"1000", score.stderr)

    def test_a_git_killed_by_a_signal_is_not_a_fact(self) -> None:
        # Review of 4490013: a child killed after launch (exit 137 in bwrap's report) was read by
        # a check=False call such as `rev-parse --verify HEAD` as "no HEAD".
        def killed(root, scratch, task_limit, status_fd=None):
            return ["/bin/sh", "-c", f'printf "{{\\"exit-code\\": 137}}" >&{status_fd}; exit 137']

        with mock.patch.object(GitAdapter, "_sandbox", side_effect=killed):
            with self.assertRaises(WorldlineError) as caught:
                GitAdapter(Core.shared())._run(os.fsencode(self.main), "rev-parse", "--verify", "HEAD", check=False)
        self.assertEqual(caught.exception.code, "GIT_INSPECTION_FAILED")
        self.assertIn("signal 9", caught.exception.message)

    def test_a_failed_submodule_listing_is_refused_not_read_as_none(self) -> None:
        # Review of 09f5c0b: a failing `submodule status` was recorded as "no submodules".
        head = subprocess.run(["git", "-C", str(self.main), "rev-parse", "HEAD"], check=True,
                              capture_output=True, text=True).stdout.strip()
        # A gitlink with no mapping in .gitmodules anywhere (worktree, index or HEAD): git itself
        # refuses `submodule status` with "no submodule mapping found", exit 128.
        subprocess.run(["git", "-C", str(self.main), "update-index", "--add", "--cacheinfo", f"160000,{head},libmodule"],
                       check=True, capture_output=True)
        with self.assertRaises(WorldlineError) as caught:
            GitAdapter(Core.shared()).capture(self.main)
        self.assertEqual(caught.exception.code, "GIT_INSPECTION_FAILED")

    def test_an_alternates_entry_leaving_the_root_is_judged_without_lookups(self) -> None:
        from worldline.controller import _require_alternates_inside
        info = self.main / ".git" / "objects" / "info"
        info.mkdir(parents=True, exist_ok=True)
        (info / "alternates").write_text("../../../../elsewhere/objects\n", encoding="utf-8")
        with mock.patch("worldline.controller.os.path.realpath", side_effect=AssertionError("looked up")):
            with self.assertRaises(WorldlineError) as caught:
                _require_alternates_inside(os.fsencode(self.main))
        self.assertEqual(caught.exception.code, "GIT_ALTERNATES_OUTSIDE_ROOT")

    def test_git_outside_the_bound_directories_refuses_before_running(self) -> None:
        with mock.patch("worldline.linux.git.shutil.which", return_value="/opt/elsewhere/bin/git"):
            with self.assertRaises(WorldlineError) as caught:
                GitAdapter(Core.shared())._sandboxed_git()
        self.assertEqual(caught.exception.code, "GIT_SANDBOX_UNAVAILABLE")

    def test_alternates_behind_a_link_are_not_read(self) -> None:
        # Review of 796cb02: the doctor opened `objects/info/alternates` following links.
        from worldline.controller import _require_alternates_inside
        decoy = self.base / "decoy-alternates"
        decoy.write_text(str(self.base / "elsewhere" / "objects") + "\n", encoding="utf-8")
        info = self.main / ".git" / "objects" / "info"
        info.mkdir(parents=True, exist_ok=True)
        (info / "alternates").symlink_to(decoy)
        _require_alternates_inside(os.fsencode(self.main))  # not followed, so nothing to refuse


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



class RecoveryContainment(unittest.TestCase):
    """Recovery must quarantine an unresolvable transaction, never take the daemon down.

    A crash between the prepared-record write and its database row leaves the two durably
    disagreeing. Raising out of recover_all would fail daemon.start() before the socket is
    published, so every command -- including the read-only diagnostics needed to understand the
    problem -- would return DAEMON_UNAVAILABLE on every boot until the operator hand-edited
    JSON and SQLite. Fail open for diagnosis; fail closed for mutation.
    """

    def _transactions(self):
        from worldline.transaction import CollapseTransaction

        transactions = object.__new__(CollapseTransaction)
        transactions.unrecoverable = {}
        return transactions

    def test_unresolvable_transaction_is_quarantined_not_raised(self) -> None:
        from worldline.transaction import CollapseTransaction

        transactions = self._transactions()
        rows = [{"transaction_id": "wedged"}, {"transaction_id": "healthy"}]
        transactions.store = type("S", (), {
            "transactions_in_state": lambda _self, states: rows if "PREPARED" in states else [],
            "receipt_for_transaction": lambda _self, _tx: object(),
        })()

        def recover_one(transaction_id):
            if transaction_id == "wedged":
                raise WorldlineError("TRANSACTION_RECORD_INVALID", "database and record differ")
            return {"transactionId": transaction_id, "state": "ABORTED"}

        transactions._recover_one = recover_one
        recovered = CollapseTransaction.recover_all(transactions)

        self.assertEqual(len(recovered), 2)
        self.assertEqual(recovered[0]["state"], "UNRECOVERABLE")
        self.assertEqual(recovered[1]["state"], "ABORTED")
        self.assertIn("wedged", transactions.unrecoverable)
        self.assertNotIn("healthy", transactions.unrecoverable)

    def test_mutation_refuses_while_a_transaction_is_unrecoverable(self) -> None:
        from worldline.transaction import CollapseTransaction

        transactions = self._transactions()
        transactions.unrecoverable = {"wedged": {"code": "TRANSACTION_RECORD_INVALID"}}
        with self.assertRaises(WorldlineError) as raised:
            CollapseTransaction._assert_recovery_complete(transactions)
        self.assertEqual(raised.exception.code, "RECOVERY_INCOMPLETE")
        self.assertEqual(raised.exception.details["transactions"], ["wedged"])

    def test_clean_recovery_permits_mutation(self) -> None:
        from worldline.transaction import CollapseTransaction

        transactions = self._transactions()
        CollapseTransaction._assert_recovery_complete(transactions)  # must not raise


class DoctorIntegrityReports(unittest.TestCase):
    """doctor must surface state that log --verify and rootIntegrity cannot see."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-doctor-")
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
        self.paths.ensure()
        self.core = Core.shared()
        self.store = StateStore(self.paths, self.core)

    def tearDown(self) -> None:
        self.store.close()
        self.temporary.cleanup()

    def _probe(self):
        controller = object.__new__(RuntimeController)
        controller.store = self.store
        controller.paths = self.paths
        return controller

    def test_store_integrity_flags_an_unreferenced_captured_payload(self) -> None:
        # This is what a SIGKILL during `worldline init` leaves behind: the operator's real
        # directory is in the store and nothing points at it.
        orphan = self.paths.generations / "abandoned" / "payload" / ("a" * 64)
        orphan.mkdir(mode=0o700, parents=True)
        (orphan / "state.txt").write_bytes(b"the user's data")
        report = RuntimeController._store_integrity(self._probe())
        self.assertEqual(report["state"], "DEGRADED")
        kinds = [entry["kind"] for entry in report["findings"]]
        self.assertIn("ORPHANED_GENERATION", kinds)

    def test_store_integrity_ignores_the_manifests_sibling(self) -> None:
        # Every generation payload holds a `manifests/` directory beside its root-key
        # directories. Reporting it would be a false alarm, and a diagnostic that cries wolf is
        # the same sin as one that stays silent.
        manifests = self.paths.generations / "gen" / "payload" / "manifests"
        manifests.mkdir(mode=0o700, parents=True)
        (manifests / "root.json").write_text("{}", encoding="utf-8")
        report = RuntimeController._store_integrity(self._probe())
        self.assertEqual(report["state"], "OK", report["findings"])

    def test_store_integrity_is_ok_on_a_clean_store(self) -> None:
        report = RuntimeController._store_integrity(self._probe())
        self.assertEqual(report["state"], "OK")
        self.assertEqual(report["findings"], [])

    def test_receipt_coverage_flags_a_committed_collapse_with_no_receipt(self) -> None:
        # log --verify cannot see this: a receipt that was never written leaves both chains
        # internally consistent, merely shorter, so verification passes over the hole.
        probe = self._probe()
        probe.store = type("S", (), {
            "transactions_in_state": lambda _s, states: (
                [{"transaction_id": "tx-1"}] if "COMMITTED" in states else []
            ),
            "receipt_for_transaction": lambda _s, _tx: None,
        })()
        report = RuntimeController._receipt_coverage(probe)
        self.assertEqual(report["state"], "DEGRADED")
        self.assertEqual(report["committedWithoutReceipt"], ["tx-1"])

    def test_receipt_coverage_is_ok_when_every_collapse_has_a_receipt(self) -> None:
        probe = self._probe()
        probe.store = type("S", (), {
            "transactions_in_state": lambda _s, states: (
                [{"transaction_id": "tx-1"}] if "COMMITTED" in states else []
            ),
            "receipt_for_transaction": lambda _s, _tx: {"receiptId": "WL:x"},
        })()
        report = RuntimeController._receipt_coverage(probe)
        self.assertEqual(report["state"], "OK")
        self.assertEqual(report["committedWithoutReceipt"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
