"""Controls for scripts/prune_backups.py.

This is the one script in the install path whose job is to DELETE, so what it refuses to touch
matters more than what it removes.
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/prune_backups.py"


class PruneBackups(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-prune-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "install-backups"
        self.root.mkdir(parents=True)

    def backup(self, name: str, payload: str = "x" * 1024) -> Path:
        directory = self.root / name
        (directory / "state/worldline").mkdir(parents=True)
        (directory / "state/worldline/store.sqlite").write_text(payload, encoding="utf-8")
        (directory / "backup-manifest.json").write_text("{}\n", encoding="utf-8")
        return directory

    def run_prune(self, *extra: str) -> dict:
        proc = subprocess.run(["python3", str(SCRIPT), str(self.root), "--json", *extra],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return json.loads(proc.stdout)

    def names(self) -> list[str]:
        return sorted(p.name for p in self.root.iterdir())

    def test_without_apply_it_reports_and_removes_nothing(self) -> None:
        for stamp in ("20260101T000000Z-1", "20260102T000000Z-1", "20260103T000000Z-1"):
            self.backup(stamp)
        report = self.run_prune("--keep", "1")
        self.assertEqual([e["name"] for e in report["removed"]], ["20260102T000000Z-1", "20260101T000000Z-1"])
        self.assertEqual(len(self.names()), 3, "a report without --apply must not delete anything")
        self.assertFalse(report["applied"])

    def test_the_most_recent_are_kept_and_the_rest_removed(self) -> None:
        for stamp in ("20260101T000000Z-1", "20260102T000000Z-1", "20260103T000000Z-1", "20260104T000000Z-9"):
            self.backup(stamp)
        report = self.run_prune("--keep", "2", "--apply")
        self.assertEqual(self.names(), ["20260103T000000Z-1", "20260104T000000Z-9"])
        self.assertEqual(report["kept"], ["20260104T000000Z-9", "20260103T000000Z-1"])
        self.assertGreater(report["freedBytes"], 2000, "it should account for the bytes it freed")

    def test_recency_is_read_from_the_stamp_not_the_modification_time(self) -> None:
        old = self.backup("20260101T000000Z-1")
        self.backup("20260201T000000Z-1")
        # A restore, a copy or a backup tool would rewrite mtimes; the name is the record.
        os.utime(old, (2 ** 31 - 1, 2 ** 31 - 1))
        self.run_prune("--keep", "1", "--apply")
        self.assertEqual(self.names(), ["20260201T000000Z-1"])

    def test_keep_zero_disables_pruning(self) -> None:
        for stamp in ("20260101T000000Z-1", "20260102T000000Z-1"):
            self.backup(stamp)
        report = self.run_prune("--keep", "0", "--apply")
        self.assertEqual(len(self.names()), 2)
        self.assertEqual(report["removed"], [])
        self.assertIn("disabled", report["note"])

    def test_anything_that_is_not_one_of_our_backups_is_left_alone(self) -> None:
        self.backup("20260101T000000Z-1")
        self.backup("20260102T000000Z-1")
        (self.root / "notes.txt").write_text("keep me\n", encoding="utf-8")
        (self.root / "my-own-copy").mkdir()
        (self.root / "my-own-copy/important").write_text("keep me\n", encoding="utf-8")
        report = self.run_prune("--keep", "1", "--apply")
        self.assertTrue((self.root / "notes.txt").exists())
        self.assertTrue((self.root / "my-own-copy/important").exists())
        self.assertIn("my-own-copy", [s["name"] for s in report["skipped"]])
        self.assertEqual([e["name"] for e in report["removed"]], ["20260101T000000Z-1"])

    def test_a_symlinked_backup_is_never_followed(self) -> None:
        target = Path(self.temporary.name) / "somewhere-else"
        (target / "state").mkdir(parents=True)
        (target / "state/precious").write_text("not ours to delete\n", encoding="utf-8")
        self.backup("20260301T000000Z-1")
        (self.root / "20260101T000000Z-1").symlink_to(target)
        self.run_prune("--keep", "1", "--apply")
        self.assertTrue((target / "state/precious").exists(), "it followed a symlink out of the backup area")
        self.assertTrue((self.root / "20260101T000000Z-1").is_symlink(), "the link itself must be left alone")

    def test_a_missing_backup_directory_is_not_an_error(self) -> None:
        proc = subprocess.run(["python3", str(SCRIPT), str(self.root / "absent"), "--keep", "5", "--apply"],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("nothing to do", proc.stdout)


if __name__ == "__main__":
    unittest.main()
