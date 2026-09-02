from __future__ import annotations

import os
from pathlib import Path
import stat
import tempfile
import unittest

from worldline.core import Core, hash_id
from worldline.model import World
from worldline.paths import WorldlinePaths
from worldline.store import StateStore


class StateStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-store-")
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

    def tearDown(self) -> None:
        self.store.close()
        self.temporary.cleanup()

    def test_owner_only_wal_store_and_world_round_trip(self) -> None:
        mode = stat.S_IMODE(self.paths.database.stat().st_mode)
        self.assertEqual(mode, 0o600)
        zero = hash_id(bytes(32))
        world = World.create(
            alias="alpha",
            parent_instance=None,
            parent_content=zero,
            cause="fixture mission",
            actor="fixture",
            payload_path=self.paths.worlds / "alpha/payload",
            base_payload_path=self.paths.generations / "base",
            base_root=zero,
            root_set_hash=zero,
            mission_hash=zero,
        )
        self.store.insert_world(world)
        loaded = self.store.world("alpha")
        self.assertEqual(loaded.instance_id, world.instance_id)
        self.assertEqual(loaded.evidence["summary"], "UNASSESSED")

    def test_canonical_events_survive_database_rendering(self) -> None:
        zero = hash_id(bytes(32))
        world = World.create(
            alias="beta",
            parent_instance=None,
            parent_content=zero,
            cause="fixture mission",
            actor="fixture",
            payload_path=self.paths.worlds / "beta/payload",
            base_payload_path=self.paths.generations / "base",
            base_root=zero,
            root_set_hash=zero,
            mission_hash=zero,
        )
        self.store.insert_world(world)
        result = self.store.append_causal_event(
            {
                "schemaVersion": 1,
                "worldInstance": world.instance_id,
                "kind": "mission",
                "actor": "fixture",
                "reason": None,
            }
        )
        self.assertTrue(result["chainHash"].startswith("sha256:"))
        self.assertEqual(self.store.verify_chains(), {"causalEvents": 1, "receipts": 0})


if __name__ == "__main__":
    unittest.main()
