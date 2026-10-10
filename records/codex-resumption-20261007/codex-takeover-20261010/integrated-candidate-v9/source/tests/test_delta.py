from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest

from worldline.core import Core
from worldline.delta import Delta
from worldline.manifest import Manifest


class DeltaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-delta-")
        root = Path(self.temporary.name)
        self.base_path = root / "base"
        self.current_path = root / "current"
        self.candidate_path = root / "candidate"
        self.stage_path = root / "stage"
        self.base_path.mkdir()
        (self.base_path / "modify.txt").write_text("base modify", encoding="utf-8")
        (self.base_path / "unrelated.txt").write_text("base unrelated", encoding="utf-8")
        (self.base_path / "delete.txt").write_text("delete me", encoding="utf-8")
        self.core = Core.shared()
        self.base = Manifest.capture(self.base_path, root_key="fixture", kind="filesystem", core=self.core)
        Manifest.materialize(self.base, self.base_path, self.current_path, core=self.core)
        Manifest.materialize(self.base, self.base_path, self.candidate_path, core=self.core)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _capture(self, path: Path):
        return Manifest.capture(
            path,
            logical_root=self.base_path,
            root_key="fixture",
            kind="filesystem",
            core=self.core,
        )

    def test_add_modify_delete_preserve_unrelated_prime_change(self) -> None:
        (self.candidate_path / "modify.txt").write_text("candidate modify", encoding="utf-8")
        (self.candidate_path / "delete.txt").unlink()
        (self.candidate_path / "add.txt").write_text("candidate add", encoding="utf-8")
        (self.current_path / "unrelated.txt").write_text("prime unrelated", encoding="utf-8")
        candidate = self._capture(self.candidate_path)
        current = self._capture(self.current_path)

        delta = Delta.compute(self.base, candidate, self.core)
        operations = {item["op"] for item in delta.value["operations"]}
        self.assertEqual(operations, {"ADD", "MODIFY", "DELETE"})
        merged = Delta.merge(
            base=self.base,
            current=current,
            candidate=candidate,
            current_source=self.current_path,
            candidate_source=self.candidate_path,
            stage=self.stage_path,
            core=self.core,
        )
        self.assertEqual(merged.conflicts, [])
        self.assertEqual((self.stage_path / "modify.txt").read_text(encoding="utf-8"), "candidate modify")
        self.assertEqual((self.stage_path / "unrelated.txt").read_text(encoding="utf-8"), "prime unrelated")
        self.assertEqual((self.stage_path / "add.txt").read_text(encoding="utf-8"), "candidate add")
        self.assertFalse((self.stage_path / "delete.txt").exists())

    def test_divergent_touched_path_conflicts_without_staging(self) -> None:
        (self.candidate_path / "modify.txt").write_text("candidate", encoding="utf-8")
        (self.current_path / "modify.txt").write_text("prime", encoding="utf-8")
        candidate = self._capture(self.candidate_path)
        current = self._capture(self.current_path)
        merged = Delta.merge(
            base=self.base,
            current=current,
            candidate=candidate,
            current_source=self.current_path,
            candidate_source=self.candidate_path,
            stage=self.stage_path,
            core=self.core,
        )
        self.assertEqual(len(merged.conflicts), 1)
        self.assertIsNone(merged.staged)
        self.assertFalse(self.stage_path.exists())
        self.assertEqual((self.current_path / "modify.txt").read_text(encoding="utf-8"), "prime")


if __name__ == "__main__":
    unittest.main()
