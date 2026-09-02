from __future__ import annotations

import base64
import os
from pathlib import Path
import tempfile
import unittest

from worldline.core import Core
from worldline.errors import WorldlineError
from worldline.manifest import Manifest


class ManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-manifest-")
        self.root = os.fsencode(Path(self.temporary.name) / "source")
        os.mkdir(self.root, 0o700)
        self.core = Core.shared()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_non_utf8_hardlink_xattr_and_symlink_round_trip(self) -> None:
        raw_name = b"raw-\xff.bin"
        first = os.path.join(self.root, raw_name)
        second = os.path.join(self.root, b"linked.bin")
        with open(first, "wb") as stream:
            stream.write(b"worldline bytes\x00\xff")
        os.link(first, second)
        os.setxattr(first, b"user.worldline", b"manifest-value")
        os.mkdir(os.path.join(self.root, b"nested"), 0o750)
        os.symlink(b"../linked.bin", os.path.join(self.root, b"nested/link"))

        one = Manifest.capture(self.root, root_key="fixture-root", kind="filesystem", core=self.core)
        two = Manifest.capture(self.root, root_key="fixture-root", kind="filesystem", core=self.core)
        self.assertEqual(one.canonical, two.canonical)
        self.assertEqual(one.root_hash, two.root_hash)
        raw_entry = next(item for item in one.value["entries"] if item["pathB64"] == base64.b64encode(raw_name).decode("ascii"))
        self.assertIn("�", raw_entry["pathDisplay"])
        self.assertIsNotNone(raw_entry["hardLinkGroup"])

        destination = os.fsencode(Path(self.temporary.name) / "restored")
        restored = Manifest.materialize(one, self.root, destination, core=self.core)
        self.assertEqual(restored.root_hash, one.root_hash)
        restored_first = os.path.join(destination, raw_name)
        restored_second = os.path.join(destination, b"linked.bin")
        self.assertEqual(os.stat(restored_first).st_ino, os.stat(restored_second).st_ino)
        self.assertEqual(os.getxattr(restored_first, b"user.worldline"), b"manifest-value")

    def test_special_file_is_rejected(self) -> None:
        fifo = os.path.join(self.root, b"unsupported.fifo")
        os.mkfifo(fifo)
        with self.assertRaises(WorldlineError) as caught:
            Manifest.capture(self.root, root_key="fixture-root", kind="filesystem", core=self.core)
        self.assertEqual(caught.exception.code, "UNSUPPORTED_SPECIAL_FILE")


if __name__ == "__main__":
    unittest.main()
