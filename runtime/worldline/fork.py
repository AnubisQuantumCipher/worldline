from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from pathlib import Path
from typing import Any, Callable, Sequence

from .agents import adapter as resolve_adapter
from .checkpoint import CheckpointManager, FrozenParent
from .config import GlobalConfig
from .core import Core, hash_id
from .errors import WorldlineError
from .model import validate_user_alias, World
from .paths import WorldlinePaths
from .project import ProjectConfig
from .runner import AgentRunner
from .scoring import WorldScorer
from .store import StateStore


class ForkManager:
    def __init__(
        self,
        paths: WorldlinePaths,
        store: StateStore,
        config: GlobalConfig,
        checkpoint: CheckpointManager,
        runner: AgentRunner,
        *,
        core: Core | None = None,
    ) -> None:
        self.paths = paths
        self.store = store
        self.config = config
        self.checkpoint = checkpoint
        self.runner = runner
        self.core = core or Core.shared()

    def create_world(
        self,
        name: str,
        mission: str,
        agent_name: str,
        *,
        frozen: FrozenParent | None = None,
    ) -> World:
        if not mission:
            raise WorldlineError("NO_MISSION", "worldline: no mission; pass --mission FILE, pipe stdin, or create mission.md")
        validate_user_alias(name)
        parent = frozen or self.checkpoint.freeze()
        actor = resolve_adapter(agent_name, self.config)
        world = World.create(
            alias=name,
            parent_instance=parent.parent_instance,
            parent_content=parent.parent_content,
            cause=mission,
            actor=actor.name,
            payload_path=self.paths.worlds / "pending" / "payload",
            base_payload_path=parent.payload,
            base_root=parent.state_root,
            root_set_hash=parent.root_set_hash,
            workspace=parent.workspace,
            mission_hash=hash_id(self.core.hash_bytes(b"worldline-mission-v1" + mission.encode("utf-8", "strict"))),
        )
        world.payload_path = str(self.paths.worlds / world.instance_id / "payload")
        self.store.insert_world(world)
        return world

    def run_world(
        self,
        world: World,
        mission: str,
        *,
        progress: Callable[[str, dict[str, Any]], None] | None = None,
        low_priority: bool = False,
    ) -> World:
        selected = resolve_adapter(world.actor, self.config)
        roots = self.store.roots()
        primary = next((root for root in roots if root["primary_root"]), None)
        if primary is None:
            raise WorldlineError("NO_PRIMARY_ROOT", "no primary root is registered")
        project = ProjectConfig.load(Path(os.fsdecode(bytes(primary["path"]))), self.store)
        result = self.runner.run(
            world.instance_id,
            selected,
            mission,
            project,
            progress=progress,
            low_priority=low_priority,
        )
        WorldScorer(self.store).score([result, *self.store.terminal_siblings(result)])
        return result

    def fork(
        self,
        name: str,
        mission: str,
        agent_name: str,
        *,
        wait: bool = False,
        progress: Callable[[str, dict[str, Any]], None] | None = None,
    ) -> World:
        world = self.create_world(name, mission, agent_name)
        return self.run_world(world, mission, progress=progress) if wait else world

    def race(
        self,
        agents: Sequence[str],
        mission: str,
        *,
        wait: bool,
        progress: Callable[[str, dict[str, Any]], None] | None = None,
    ) -> list[World]:
        if len(agents) != 3:
            raise WorldlineError("INVALID_RACE", "race requires exactly three --agent values")
        frozen = self.checkpoint.freeze()
        aliases = ("alpha", "beta", "gamma")
        worlds = [
            self.create_world(alias, mission, agent_name, frozen=frozen)
            for alias, agent_name in zip(aliases, agents, strict=True)
        ]
        if not wait:
            return worlds
        completed: dict[str, World] = {}
        with ThreadPoolExecutor(max_workers=len(worlds), thread_name_prefix="worldline-race") as executor:
            futures = {
                executor.submit(self.run_world, world, mission, progress=progress): world.alias
                for world in worlds
            }
            for future in as_completed(futures):
                completed[futures[future]] = future.result()
        ordered = [completed[alias] for alias in aliases]
        WorldScorer(self.store).score(ordered)
        return ordered
