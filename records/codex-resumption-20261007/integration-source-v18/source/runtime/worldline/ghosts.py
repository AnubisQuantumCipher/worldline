from __future__ import annotations

from typing import Any

from .config import GlobalConfig
from .errors import WorldlineError
from .model import World, WorldState
from .store import StateStore

_GHOST_MISSIONS = {
    "security-refactor": "Find and implement a security refactor. Preserve behavior and run every configured required check.",
    "performance": "Find and implement a measurable performance improvement. Preserve behavior and produce configured benchmark evidence.",
    "remove-dependency": "Remove one or more declared dependencies without regressing any configured required check.",
    "simplification": "Simplify the implementation and reduce nonblank source lines without regressing any configured required check.",
}


class GhostManager:
    def __init__(self, config: GlobalConfig, store: StateStore) -> None:
        self.config = config
        self.store = store

    @property
    def missions(self) -> dict[str, str]:
        return dict(_GHOST_MISSIONS)

    def enable(self, agent: str) -> dict[str, Any]:
        self.config.enable_ghosts(agent)
        return self.status()

    def disable(self) -> dict[str, Any]:
        self.config.disable_ghosts()
        self.store.set_meta("ghostRecommendation", None)
        return self.status()

    def status(self) -> dict[str, Any]:
        return {
            "enabled": self.config.value["ghosts"]["enabled"],
            "agent": self.config.value["ghosts"]["agent"],
            "missions": sorted(_GHOST_MISSIONS),
            "recommendation": self.store.get_meta("ghostRecommendation"),
        }

    def recommendation(self, objective: str, candidate: World, parent: World) -> dict[str, Any] | None:
        if objective not in _GHOST_MISSIONS:
            raise WorldlineError("UNKNOWN_GHOST", f"unknown ghost mission: {objective}")
        if candidate.state is not WorldState.VALID:
            return None
        candidate_checks = {item.get("id"): item for item in candidate.evidence.get("checks", [])}
        parent_checks = {item.get("id"): item for item in parent.evidence.get("checks", [])}
        for identifier, check in parent_checks.items():
            if check.get("required") and check.get("status") == "PASS":
                if candidate_checks.get(identifier, {}).get("status") != "PASS":
                    return None
        facts: dict[str, Any] | None = None
        if objective == "security-refactor":
            improved = [
                identifier
                for identifier, check in parent_checks.items()
                if "security" in str(identifier).lower()
                and check.get("status") != "PASS"
                and candidate_checks.get(identifier, {}).get("status") == "PASS"
            ]
            if improved:
                facts = {"securityChecksNowPassing": improved}
        elif objective == "performance":
            improved = [
                check.get("id")
                for check in candidate.evidence.get("checks", [])
                if check.get("kind") == "benchmark" and check.get("improved") is True
            ]
            if improved:
                facts = {"benchmarksImproved": improved}
        elif objective == "remove-dependency":
            before = parent.evidence.get("metrics", {}).get("dependencyCount")
            after = candidate.evidence.get("metrics", {}).get("dependencyCount")
            if isinstance(before, int) and isinstance(after, int) and after < before:
                facts = {"dependenciesBefore": before, "dependenciesAfter": after}
        elif objective == "simplification":
            before = parent.evidence.get("metrics", {}).get("nonblankSourceLines")
            after = candidate.evidence.get("metrics", {}).get("nonblankSourceLines")
            if isinstance(before, int) and isinstance(after, int) and after < before:
                facts = {"sourceLinesBefore": before, "sourceLinesAfter": after}
        if facts is None:
            return None
        value = {
            "title": "WORLDLINE — A better future has been found",
            "world": candidate.alias,
            "instanceId": candidate.instance_id,
            "objective": objective,
            "facts": facts,
            "action": "Inspect",
        }
        self.store.set_meta("ghostRecommendation", value)
        return value

    @staticmethod
    def assert_not_self_collapse(world: World) -> None:
        if world.evidence.get("ghostObjective") in _GHOST_MISSIONS:
            raise WorldlineError("GHOST_SELF_COLLAPSE_FORBIDDEN", "a ghost world cannot collapse itself")
