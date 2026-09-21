from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from pathlib import Path
from typing import Any, Callable, Sequence

from .agents import adapter as resolve_adapter
from .agents.base import AgentContext
from .checkpoint import CheckpointManager, FrozenParent
from .config import GlobalConfig
from .core import Core, hash_id
from .errors import WorldlineError
from .model import validate_user_alias, World, WorldState
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
        # Resolve the adapter before freezing: a freeze materializes a full generation on disk,
        # and an unknown or unavailable adapter used to abandon it (an unreferenced payload the
        # doctor then had to explain).
        actor = resolve_adapter(agent_name, self.config)
        # Credentials are checked before the freeze for the same reason: an agent that cannot be
        # authenticated (pi with an empty auth.json, a generic command whose declared credential
        # file is gone) should be a refusal at the prompt, not a world that is born DEAD.
        actor.credential_mounts(self._probe_context())
        parent = frozen or self.checkpoint.freeze()
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
        timeout: float | None = None,
    ) -> World:
        try:
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
                timeout=timeout if timeout is not None else self.config.default_timeout_seconds,
            )
        except BaseException as exc:
            # A world whose run could not even start (adapter vanished, project config invalid,
            # sandbox refused) must not stay MUTABLE forever: that is a nonterminal world with no
            # supervisor, which blocks every later root-set change and reads as "running" in
            # every surface. Record the failure and terminate it through the kernel.
            self._terminate_failed_start(world.instance_id, exc)
            raise
        WorldScorer(self.store).score([result, *self.store.terminal_siblings(result)])
        return result

    def _terminate_failed_start(self, instance_id: str, exc: BaseException) -> None:
        try:
            current = self.store.world(instance_id)
        except WorldlineError:
            return
        if current.state not in (WorldState.MUTABLE, WorldState.FINALIZING):
            return
        error = exc.as_dict() if isinstance(exc, WorldlineError) else {
            "code": "RUN_FAILED",
            "message": f"{type(exc).__name__}: {exc}",
            "details": {},
        }
        checks = list(current.evidence.get("checks", [])) if isinstance(current.evidence, dict) else []
        current.evidence = {"summary": "FAIL", "checks": checks, "supervision": error}
        current.transition(WorldState.DEAD, self.core)
        self.store.save_world(current)

    def _probe_context(self) -> AgentContext:
        home = self.paths.home
        return AgentContext(
            primary_root=home,
            workspace=home,
            mission_file=Path("/run/worldline-runtime/mission.txt"),
            world_state=Path("/run/worldline-runtime/world.json"),
            home=home,
            is_git_root=False,
        )

    def fork(
        self,
        name: str,
        mission: str,
        agent_name: str,
        *,
        wait: bool = False,
        progress: Callable[[str, dict[str, Any]], None] | None = None,
        timeout: float | None = None,
    ) -> World:
        world = self.create_world(name, mission, agent_name)
        return self.run_world(world, mission, progress=progress, timeout=timeout) if wait else world

    def race(
        self,
        agents: Sequence[str],
        mission: str,
        *,
        wait: bool,
        progress: Callable[[str, dict[str, Any]], None] | None = None,
        name: str | None = None,
        timeout: float | None = None,
    ) -> list[World]:
        if len(agents) != 3:
            raise WorldlineError("INVALID_RACE", "race requires exactly three --agent values")
        # Lanes are alpha/beta/gamma; an optional name prefixes them so a second race from the
        # same PRIME does not collide with the first (aliases are unique per store).
        if name is not None:
            validate_user_alias(name)
            aliases = tuple(f"{name}-{lane}" for lane in ("alpha", "beta", "gamma"))
        else:
            aliases = ("alpha", "beta", "gamma")
        for agent_name in agents:
            resolve_adapter(agent_name, self.config).credential_mounts(self._probe_context())
        for alias in aliases:
            try:
                self.store.world(alias)
            except WorldlineError:
                continue
            raise WorldlineError("WORLD_CONFLICT", f"world alias already exists: {alias}; pass --name to prefix the lanes", {"alias": alias})
        frozen = self.checkpoint.freeze()
        worlds = [
            self.create_world(alias, mission, agent_name, frozen=frozen)
            for alias, agent_name in zip(aliases, agents, strict=True)
        ]
        if not wait:
            return worlds
        completed: dict[str, World] = {}
        with ThreadPoolExecutor(max_workers=len(worlds), thread_name_prefix="worldline-race") as executor:
            futures = {
                executor.submit(self.run_world, world, mission, progress=progress, timeout=timeout): world.alias
                for world in worlds
            }
            for future in as_completed(futures):
                completed[futures[future]] = future.result()
        ordered = [completed[alias] for alias in aliases]
        WorldScorer(self.store).score(ordered)
        return ordered
