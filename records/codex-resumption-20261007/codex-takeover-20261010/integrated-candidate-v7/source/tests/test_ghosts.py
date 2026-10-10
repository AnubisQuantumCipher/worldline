from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from worldline.config import GlobalConfig
from worldline.core import hash_id
from worldline.ghosts import GhostManager
from worldline.model import World, WorldState
from worldline.paths import WorldlinePaths


class _Store:
    def __init__(self):
        self.values = {}

    def set_meta(self, key, value):
        self.values[key] = value

    def get_meta(self, key, default=None):
        return self.values.get(key, default)


class GhostTests(unittest.TestCase):
    def _world(self, alias: str) -> World:
        zero = hash_id(bytes(32))
        world = World.create(
            alias=alias,
            parent_instance=None,
            parent_content=zero,
            cause="fixture",
            actor="fixture",
            payload_path=Path("/tmp") / alias,
            base_payload_path=Path("/tmp/base"),
            base_root=zero,
            root_set_hash=zero,
            mission_hash=zero,
        )
        world.state = WorldState.VALID
        return world

    def test_missing_objective_evidence_never_recommends(self) -> None:
        with tempfile.TemporaryDirectory(prefix="worldline-ghost-") as temporary:
            root = Path(temporary)
            env = {
                "HOME": str(root / "home"),
                "XDG_DATA_HOME": str(root / "data"),
                "XDG_STATE_HOME": str(root / "state"),
                "XDG_CONFIG_HOME": str(root / "config"),
                "XDG_RUNTIME_DIR": str(root / "runtime"),
            }
            for value in env.values():
                Path(value).mkdir(mode=0o700, parents=True, exist_ok=True)
            config = GlobalConfig.default(WorldlinePaths.from_environment(env))
            manager = GhostManager(config, _Store())
            parent = self._world("parent")
            candidate = self._world("candidate")
            parent.evidence = {"checks": [], "metrics": {"nonblankSourceLines": 20}}
            candidate.evidence = {"checks": [], "metrics": {}}
            self.assertIsNone(manager.recommendation("simplification", candidate, parent))
            candidate.evidence["metrics"]["nonblankSourceLines"] = 10
            recommendation = manager.recommendation("simplification", candidate, parent)
            self.assertEqual(recommendation["action"], "Inspect")
            self.assertEqual(recommendation["objective"], "simplification")


if __name__ == "__main__":
    unittest.main()
