from __future__ import annotations

from pathlib import Path
import unittest

from worldline.core import hash_id
from worldline.model import World, WorldState
from worldline.scoring import WorldScorer


class _Store:
    def __init__(self, worlds):
        self._worlds = worlds

    def worlds(self):
        return self._worlds

    def save_world(self, world):
        return None


class ScoringTests(unittest.TestCase):
    def _world(self, alias: str, changed: int) -> World:
        zero = hash_id(bytes(32))
        world = World.create(
            alias=alias,
            parent_instance="parent",
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
        world.delta = {"files": [{"path": str(index)} for index in range(changed)]}
        world.evidence = {
            "checks": [{"id": "required", "required": True, "status": "PASS"}],
            "summary": "PASS",
        }
        return world

    def test_relative_complexity_and_risk_facts(self) -> None:
        low = self._world("low", 1)
        middle = self._world("middle", 2)
        high = self._world("high", 3)
        scorer = WorldScorer(_Store([low, middle, high]))
        scorer.score()
        self.assertEqual((low.complexity, middle.complexity, high.complexity), ("LOW", "MEDIUM", "HIGH"))
        self.assertEqual(low.risk, "LOW")
        self.assertIn("canonicalDeltaBytes", low.evidence["scoreFacts"])
        middle.evidence["checks"].append({"id": "optional", "required": False, "status": "UNAVAILABLE"})
        scorer.score()
        self.assertEqual(middle.risk, "MEDIUM")


if __name__ == "__main__":
    unittest.main()
