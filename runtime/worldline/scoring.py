from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from .canonical import canonical_bytes
from .model import World, WorldState
from .store import StateStore


class WorldScorer:
    def __init__(self, store: StateStore) -> None:
        self.store = store

    def score(self, worlds: Iterable[World] | None = None) -> list[World]:
        selected = list(worlds if worlds is not None else self.store.worlds())
        groups: dict[str | None, list[World]] = defaultdict(list)
        for world in selected:
            if world.state in {
                WorldState.VALID,
                WorldState.DEGRADED,
                WorldState.DEAD,
                WorldState.ARCHIVED,
                WorldState.COLLAPSED,
            } and not world.alias.startswith("prime-"):
                groups[world.parent_instance].append(world)
        for siblings in groups.values():
            sizes = {world.instance_id: len(canonical_bytes(world.delta)) for world in siblings}
            distinct = sorted(set(sizes.values()))
            for world in siblings:
                if len(siblings) == 1 or len(distinct) == 1:
                    world.complexity = "MEDIUM"
                elif sizes[world.instance_id] == distinct[0]:
                    world.complexity = "LOW"
                elif sizes[world.instance_id] == distinct[-1]:
                    world.complexity = "HIGH"
                else:
                    world.complexity = "MEDIUM"
                self._risk(world, sizes[world.instance_id])
                self.store.save_world(world)
        return selected

    @staticmethod
    def _risk(world: World, delta_bytes: int) -> None:
        checks = world.evidence.get("checks", [])
        required_failures = [
            item.get("id")
            for item in checks
            if item.get("required") and item.get("status") != "PASS"
        ]
        optional_gaps = [
            item.get("id")
            for item in checks
            if not item.get("required") and item.get("status") != "PASS"
        ]
        missing = not checks
        integrity_failure = world.state not in {WorldState.VALID, WorldState.COLLAPSED, WorldState.ARCHIVED}
        if integrity_failure or world.contamination or world.conflicts or required_failures:
            world.risk = "HIGH"
        elif missing or optional_gaps:
            world.risk = "MEDIUM"
        else:
            world.risk = "LOW"
        world.evidence["scoreFacts"] = {
            "canonicalDeltaBytes": delta_bytes,
            "requiredFailures": required_failures,
            "optionalGaps": optional_gaps,
            "missingEvidence": missing,
            "contaminationCount": len(world.contamination),
            "conflictCount": len(world.conflicts),
            "integrityState": world.state.value,
        }
