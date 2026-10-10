from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest

from worldline.core import Core
from worldline.errors import WorldlineError
from worldline.paths import WorldlinePaths
from worldline.roots import RootManager
from worldline.store import StateStore


class RootManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-roots-")
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
        self.work = root / "work"
        self.work.mkdir()
        (self.work / "state.txt").write_bytes(b"prime bytes")

    def tearDown(self) -> None:
        self.store.close()
        self.temporary.cleanup()

    def test_confirmation_registration_and_materialized_removal(self) -> None:
        with self.assertRaises(WorldlineError) as confirmation:
            self.manager.register([self.work])
        self.assertEqual(confirmation.exception.code, "CONFIRMATION_REQUIRED")
        self.assertFalse(self.work.is_symlink())
        self.assertEqual((self.work / "state.txt").read_bytes(), b"prime bytes")

        result = self.manager.register([self.work], confirmed=True)
        self.assertTrue(self.work.is_symlink())
        self.assertEqual((self.work / "state.txt").read_bytes(), b"prime bytes")
        roots = self.store.roots()
        self.assertEqual(len(roots), 1)
        self.assertEqual(len(roots[0]["root_key"]), 64)
        self.assertEqual(result["prime"], self.store.prime().content_id)
        self.assertTrue(
            (
                Path(self.store.prime().payload_path)
                / "manifests"
                / "environment.json"
            ).is_file()
        )

        with self.assertRaises(WorldlineError) as removal_confirmation:
            self.manager.remove(roots[0]["root_key"])
        self.assertEqual(removal_confirmation.exception.code, "CONFIRMATION_REQUIRED")
        self.assertTrue(self.work.is_symlink())

        self.manager.remove(roots[0]["root_key"], confirmed=True)
        self.assertFalse(self.work.is_symlink())
        self.assertTrue(self.work.is_dir())
        self.assertEqual((self.work / "state.txt").read_bytes(), b"prime bytes")
        self.assertEqual(self.store.roots(), [])

    def test_additional_root_can_atomically_become_primary(self) -> None:
        second = self.work.parent / "second"
        second.mkdir()
        (second / "other.txt").write_bytes(b"secondary bytes")
        self.manager.register([self.work], confirmed=True)
        self.manager.register([second], primary=second, confirmed=True)
        roots = self.store.roots()
        self.assertEqual(len(roots), 2)
        primary = next(root for root in roots if root["primary_root"])
        self.assertEqual(bytes(primary["path"]), os.fsencode(second))
        self.assertTrue(self.work.is_symlink())
        self.assertTrue(second.is_symlink())
        self.assertEqual((self.work / "state.txt").read_bytes(), b"prime bytes")
        self.assertEqual((second / "other.txt").read_bytes(), b"secondary bytes")

        self.manager.remove(primary["root_key"], confirmed=True)
        remaining = self.store.roots()
        self.assertEqual(len(remaining), 1)
        self.assertTrue(remaining[0]["primary_root"])
        self.assertFalse(second.is_symlink())
        self.manager.remove(remaining[0]["root_key"], confirmed=True)
        self.assertFalse(self.work.is_symlink())


if __name__ == "__main__":
    unittest.main()
