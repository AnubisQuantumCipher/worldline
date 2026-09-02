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
