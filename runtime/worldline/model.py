from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
import os
from pathlib import Path
import uuid
from typing import Any

from .core import Core, hash_bytes_from_id, hash_id
from .errors import WorldlineError


class WorldState(StrEnum):
    MUTABLE = "MUTABLE"
    FINALIZING = "FINALIZING"
    VALID = "VALID"
    DEGRADED = "DEGRADED"
    DEAD = "DEAD"
    ARCHIVED = "ARCHIVED"
    COLLAPSED = "COLLAPSED"


TERMINAL_STATES = {
    WorldState.VALID,
    WorldState.DEGRADED,
    WorldState.DEAD,
    WorldState.ARCHIVED,
    WorldState.COLLAPSED,
}

NONTERMINAL_STATES = {WorldState.MUTABLE, WorldState.FINALIZING}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


_ALIAS_MAX = 128


def validate_alias(alias: str) -> str:
    if not alias or alias.strip() != alias or "/" in alias or "\x00" in alias:
        raise WorldlineError(
            "INVALID_ALIAS",
            "world alias must be nonempty, trimmed, and contain neither slash nor NUL",
            {"alias": alias},
        )
    if len(alias) > _ALIAS_MAX:
        raise WorldlineError(
            "INVALID_ALIAS",
            f"world alias must be at most {_ALIAS_MAX} characters",
            {"alias": alias[:64] + "...", "length": len(alias)},
        )
    # Control characters would corrupt list/log rendering, bar-widget lines, systemd unit
    # descriptions, and terminal titles the alias flows into as a display string.
    if any(ord(character) < 0x20 or ord(character) == 0x7F for character in alias):
        raise WorldlineError(
            "INVALID_ALIAS",
            "world alias must not contain control characters",
            {"alias": alias},
        )
    return alias


def validate_user_alias(alias: str) -> str:
    # Additional rules for operator-supplied fork/race names only. WORLDLINE itself mints
    # internal worlds named "PRIME" (the active-world sentinel) and "prime-<txid>" (published
    # PRIME generations, which `why` renders as "PRIME" and scoring excludes), so those names
    # are reserved: a user fork taking one would spoof provenance and make name resolution
    # ambiguous. Internal callers use validate_alias directly and are not subject to this.
    validate_alias(alias)
    if alias == "PRIME" or alias.startswith("prime-"):
        raise WorldlineError(
            "RESERVED_ALIAS",
            "world alias must not be the reserved name 'PRIME' or begin with 'prime-'",
            {"alias": alias},
        )
    return alias


@dataclass(slots=True)
class World:
    instance_id: str
    alias: str
    parent_instance: str | None
    parent_content: str
    cause: str
    actor: str
    born: str
    ended: str | None
    state: WorldState
    components: dict[str, str]
    content_id: str | None
    payload_path: str
    mission_hash: str
    agent_reference: str | None
    evidence: dict[str, Any]
    workspace: dict[str, Any]
    base_payload_path: str
    base_root: str
    root_set_hash: str
    delta_hash: str | None
    delta: dict[str, Any]
    conflicts: list[dict[str, Any]]
    contamination: list[dict[str, Any]]
    world_kind: str = "computational"
    descendants: int = 0
    complexity: str = "MEDIUM"
    risk: str = "MEDIUM"

    @classmethod
    def create(
        cls,
        *,
        alias: str,
        parent_instance: str | None,
        parent_content: str,
        cause: str,
        actor: str,
        payload_path: Path,
        base_payload_path: Path,
        base_root: str,
        root_set_hash: str,
        mission_hash: str,
        workspace: dict[str, Any] | None = None,
        world_kind: str = "computational",
    ) -> "World":
        validate_alias(alias)
        return cls(
            instance_id=str(uuid.uuid4()),
            alias=alias,
            parent_instance=parent_instance,
            parent_content=parent_content,
            cause=cause,
            actor=actor,
            born=utc_now(),
            ended=None,
            state=WorldState.MUTABLE,
            components={},
            content_id=None,
            payload_path=os.fsdecode(payload_path),
            mission_hash=mission_hash,
            agent_reference=None,
            evidence={"checks": [], "summary": "UNASSESSED"},
            workspace=workspace or {},
            base_payload_path=os.fsdecode(base_payload_path),
            base_root=base_root,
            root_set_hash=root_set_hash,
            delta_hash=None,
            delta={"files": [], "added": 0, "modified": 0, "deleted": 0},
            conflicts=[],
            contamination=[],
            world_kind=world_kind,
        )

    def transition(self, target: WorldState, core: Core | None = None) -> None:
        verifier = core or Core.shared()
        if not verifier.transition_allowed(self.state.value, target.value):
            raise WorldlineError(
                "INVALID_TRANSITION",
                f"world cannot transition from {self.state.value} to {target.value}",
                {"from": self.state.value, "to": target.value, "world": self.alias},
            )
        self.state = target
        if target in TERMINAL_STATES:
            self.ended = utc_now()

    def establish_identity(self, core: Core | None = None) -> str:
        required = ("filesystem", "config", "repository", "environment", "evidence")
        missing = [name for name in required if name not in self.components]
        if missing:
            raise WorldlineError("INCOMPLETE_WORLD", "world component roots are incomplete", {"missing": missing})
        verifier = core or Core.shared()
        digest = verifier.world_id(
            {
                "parent": hash_bytes_from_id(self.parent_content),
                **{name: hash_bytes_from_id(self.components[name]) for name in required},
            }
        )
        self.content_id = hash_id(digest)
        return self.content_id

    def summary(self) -> dict[str, Any]:
        checks = self.evidence.get("checks", [])
        proof_checks = [item for item in checks if item.get("kind") == "proofs"]
        benchmark_checks = [item for item in checks if item.get("kind") == "benchmark"]
        return {
            "alias": self.alias,
            "id": self.content_id,
            "instanceId": self.instance_id,
            "parent": self.parent_instance,
            "parentId": self.parent_content,
            "agent": self.actor,
            "state": self.state.value,
            "delta": self.delta,
            "checks": checks,
            "proofs": proof_checks,
            "perf": benchmark_checks,
            "complexity": self.complexity,
            "risk": self.risk,
            "workspace": self.workspace,
            "born": self.born,
            "ended": self.ended,
            "cause": self.cause,
            "hash": self.content_id,
            "descendants": self.descendants,
            "baseRoot": self.base_root,
            "rootSetHash": self.root_set_hash,
            "conflicts": self.conflicts,
            "contamination": self.contamination,
            "kind": self.world_kind,
        }

    def record(self) -> dict[str, Any]:
        value = asdict(self)
        value["state"] = self.state.value
        return value
