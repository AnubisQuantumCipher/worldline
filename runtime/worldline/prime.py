from __future__ import annotations

from dataclasses import dataclass
import base64
from pathlib import Path
import uuid
from typing import Any

from .canonical import canonical_bytes
from .core import Core, hash_id
from .errors import WorldlineError
from .model import World, WorldState
from .paths import WorldlinePaths, secure_directory
from .store import StateStore


@dataclass(frozen=True, slots=True)
class Generation:
    generation_id: str
    payload: Path
    root_set_hash: str
    state_root: str
    component_roots: dict[str, str]


class PrimeManager:
    def __init__(self, paths: WorldlinePaths, store: StateStore, core: Core | None = None) -> None:
        self.paths = paths
        self.store = store
        self.core = core or Core.shared()

    def new_generation(self, *, generation_id: str | None = None) -> Path:
        identifier = generation_id or str(uuid.uuid4())
        try:
            parsed = uuid.UUID(identifier)
        except ValueError as exc:
            raise WorldlineError("INVALID_GENERATION", f"generation id is not canonical UUIDv4 text: {identifier}") from exc
        if str(parsed) != identifier or parsed.version != 4:
            raise WorldlineError("INVALID_GENERATION", f"generation id is not canonical UUIDv4 text: {identifier}")
        path = self.paths.generations / identifier / "payload"
        secure_directory(path)
        return path

    def root_set_hash(self, roots: list[dict[str, Any]]) -> str:
        value = [
            {
                "rootKey": root["root_key"],
                "pathB64": base64.b64encode(bytes(root["path"])).decode("ascii"),
                "kind": root["kind"],
            }
            for root in sorted(roots, key=lambda item: item["root_key"])
        ]
        return hash_id(self.core.hash_bytes(b"worldline-root-set-v1" + canonical_bytes(value)))

    def publish_checkpoint(
        self,
        *,
        generation: Generation,
        cause: str,
        environment_root: str,
        evidence_root: str,
        workspace: dict[str, Any] | None = None,
    ) -> World:
        if not generation.payload.is_dir():
            raise WorldlineError("INVALID_GENERATION", f"generation payload is missing: {generation.payload}")
        required = {"filesystem", "config", "repository"}
        if set(generation.component_roots) != required:
            raise WorldlineError(
                "INCOMPLETE_WORLD",
                "generation component roots must be filesystem, config, and repository",
                {"supplied": sorted(generation.component_roots)},
            )
        current = self.store.prime()
        parent_content = hash_id(bytes(32)) if current is None else current.content_id
        if parent_content is None:
            raise WorldlineError("INCOMPLETE_WORLD", "current PRIME has no content identity")
        mission_hash = hash_id(
            self.core.hash_bytes(b"worldline-prime-cause-v1" + cause.encode("utf-8", "strict"))
        )
        world = World.create(
            alias=f"prime-{generation.generation_id}",
            parent_instance=None if current is None else current.instance_id,
            parent_content=parent_content,
            cause=cause,
            actor="worldline",
            payload_path=generation.payload,
            base_payload_path=generation.payload,
            base_root=generation.state_root,
            root_set_hash=generation.root_set_hash,
            mission_hash=mission_hash,
            workspace=workspace,
        )
        world.components = {
            **generation.component_roots,
            "environment": environment_root,
            "evidence": evidence_root,
        }
        world.transition(WorldState.FINALIZING, self.core)
        world.establish_identity(self.core)
        world.transition(WorldState.VALID, self.core)
        world.evidence = {"checks": [], "summary": "UNASSESSED"}
        # The alias is deterministic (prime-<transactionId>) and this insert autocommits before
        # set_prime below, so a crash in between makes recovery replay the publish and hit the
        # UNIQUE alias constraint — which, unhandled, would fail every subsequent daemon start
        # even though the atomic exchange had already committed. A replay is legitimate only if
        # it recomputed the same content identity; instance_id is not part of content_id, so a
        # genuine replay differs there and matches here. Anything else is real divergence.
        try:
            self.store.insert_world(world)
        except WorldlineError as exc:
            if exc.code != "WORLD_CONFLICT":
                raise
            existing = self.store.world(world.alias)
            if existing.content_id != world.content_id:
                raise WorldlineError(
                    "RECOVERY_STATE_MISMATCH",
                    "a different PRIME generation is already published under this transaction",
                    {
                        "alias": world.alias,
                        "existing": existing.content_id,
                        "candidate": world.content_id,
                    },
                ) from exc
            world = existing
        if current is not None and current.state in (WorldState.VALID, WorldState.COLLAPSED):
            current.transition(WorldState.ARCHIVED, self.core)
            self.store.save_world(current)
        self.store.set_prime(world.instance_id, world.content_id, generation.generation_id)
        self.store.set_meta("activeWorld", "PRIME")
        return world
