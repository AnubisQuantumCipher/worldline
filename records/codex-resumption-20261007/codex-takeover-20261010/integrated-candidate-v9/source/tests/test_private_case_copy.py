#!/usr/bin/env python3
"""Focused standalone tests for the scoped private case copier."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))

from worldline.linux.private_case_copy import CaseCopyError, copy_case_tree


class CaseCopyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-case-copy-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "source"
        self.source.mkdir()
        self.destination = self.root / "destination"

    def test_ordinary_roundtrip(self) -> None:
        (self.source / "state").mkdir()
        (self.source / "state" / "ledger.jsonl").write_bytes(b"one\ntwo\n")
        (self.source / "empty").mkdir()
        first = copy_case_tree(self.source, self.destination,
                               logical_root="/run/janus-case/example")
        self.assertEqual((self.destination / "state" / "ledger.jsonl").read_bytes(),
                         b"one\ntwo\n")
        self.assertTrue((self.destination / "empty").is_dir())
        returned = self.root / "returned"
        second = copy_case_tree(self.destination, returned,
                                logical_root="/run/janus-case/example")
        self.assertEqual(first, second)
        self.assertEqual((returned / "state" / "ledger.jsonl").read_bytes(),
                         b"one\ntwo\n")

    def test_internal_symlink_text_survives(self) -> None:
        (self.source / "external").mkdir()
        (self.source / "external" / "sentinel").write_bytes(b"untouched")
        (self.source / "state").mkdir()
        (self.source / "state" / "shard").symlink_to("../external",
                                                     target_is_directory=True)
        copy_case_tree(self.source, self.destination,
                       logical_root="/run/janus-case/example")
        link = self.destination / "state" / "shard"
        self.assertTrue(link.is_symlink())
        self.assertEqual(os.readlink(link), "../external")
        self.assertEqual((link / "sentinel").read_bytes(), b"untouched")

    def test_external_symlink_refused(self) -> None:
        (self.source / "escape").symlink_to("../../outside")
        with self.assertRaises(CaseCopyError) as caught:
            copy_case_tree(self.source, self.destination,
                           logical_root="/run/janus-case/example")
        self.assertEqual(caught.exception.code, "CASE_COPY_LINK_ESCAPE")

    def test_link_that_climbs_after_a_name_is_refused(self) -> None:
        # `dirlink -> .` makes the kernel resolve `dirlink/../../outside` one level above
        # what lexical normalization claims, so it escapes the case. Absolute targets with
        # `..` and inner `..` that happen to stay inside are refused by the same rule.
        (self.source / "subdir").mkdir()
        (self.source / "subdir" / "dirlink").symlink_to(".", target_is_directory=True)
        cases = (("subdir/a", "dirlink/../../outside"), ("subdir/b", "dirlink/../sibling"),
                 ("c", "/run/janus-case/example/subdir/../subdir"))
        for name, target in cases:
            with self.subTest(target=target):
                link = self.source / name
                link.symlink_to(target)
                destination = self.root / ("refused-" + name.replace("/", "-"))
                with self.assertRaises(CaseCopyError) as caught:
                    copy_case_tree(self.source, destination,
                                   logical_root="/run/janus-case/example")
                self.assertEqual(caught.exception.code, "CASE_COPY_LINK_ESCAPE")
                link.unlink()

    def test_leading_parent_and_dot_links_still_copy(self) -> None:
        (self.source / "external").mkdir()
        (self.source / "state").mkdir()
        (self.source / "state" / "shard").symlink_to("../external", target_is_directory=True)
        (self.source / "state" / "self").symlink_to("./shard")
        (self.source / "absolute").symlink_to("/run/janus-case/example/external")
        copy_case_tree(self.source, self.destination, logical_root="/run/janus-case/example")
        self.assertEqual(os.readlink(self.destination / "state" / "self"), "./shard")
        self.assertEqual(os.readlink(self.destination / "absolute"),
                         "/run/janus-case/example/external")

    def test_hardlink_refused(self) -> None:
        (self.source / "original").write_bytes(b"same inode")
        os.link(self.source / "original", self.source / "alias")
        with self.assertRaises(CaseCopyError) as caught:
            copy_case_tree(self.source, self.destination,
                           logical_root="/run/janus-case/example")
        self.assertEqual(caught.exception.code, "CASE_COPY_HARDLINK")


if __name__ == "__main__":
    unittest.main()
