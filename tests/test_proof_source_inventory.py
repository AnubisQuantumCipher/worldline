"""Owned path-inventory controls; no compiler, kernel, daemon or source mutation."""
from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from worldline.proof_manifest import DECLARED_CORE_ADA_SOURCES, missing_sources, stray_sources


class ReviewedCoreSourceInventory(unittest.TestCase):
    def populate(self, root: Path) -> None:
        for relative in DECLARED_CORE_ADA_SOURCES:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("-- Owned source-inventory fixture; never compiled.\n", encoding="utf-8")

    def test_complete_declared_tree_has_no_extra_or_missing_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.populate(root)
            self.assertEqual(stray_sources(root), [])
            self.assertEqual(missing_sources(root), [])

    def test_undeclared_top_level_spec_and_body_are_refused_directly(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.populate(root)
            unexpected = ["core/ordinary_extra.adb", "core/ordinary_extra.ads"]
            for relative in unexpected:
                (root / relative).write_text("-- Owned ordinary extra path.\n", encoding="utf-8")
            self.assertEqual(stray_sources(root), unexpected)
            self.assertEqual(missing_sources(root), [])

    def test_undeclared_nested_path_remains_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.populate(root)
            path = root / "core/ordinary/extra.ads"
            path.parent.mkdir()
            path.write_text("-- Owned nested path.\n", encoding="utf-8")
            self.assertEqual(stray_sources(root), ["core/ordinary/extra.ads"])

    def test_missing_body_and_spec_cannot_shrink_required_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.populate(root)
            missing = ["core/evaluation_epoch.adb", "core/evaluation_epoch.ads"]
            for relative in missing:
                (root / relative).unlink()
            self.assertEqual(missing_sources(root), missing)
            self.assertEqual(stray_sources(root), [])

    def test_reviewed_working_tree_core_keyset_matches_literal_inventory(self) -> None:
        found = {path.relative_to(ROOT).as_posix() for path in (ROOT / "core").rglob("*.ad[bs]")}
        self.assertEqual(found, DECLARED_CORE_ADA_SOURCES)


if __name__ == "__main__":
    unittest.main()
