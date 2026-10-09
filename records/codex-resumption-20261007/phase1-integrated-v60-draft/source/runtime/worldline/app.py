from __future__ import annotations

from dataclasses import dataclass

from .capabilities import CapabilityRegistry
from .config import GlobalConfig
from .controller import RuntimeController
from .core import Core
from .daemon import WorldlineDaemon
from .paths import WorldlinePaths
from .status import StatusPublisher
from .store import StateStore


@dataclass(slots=True)
class WorldlineApplication:
    paths: WorldlinePaths
    core: Core
    store: StateStore
    config: GlobalConfig
    capabilities: CapabilityRegistry
    publisher: StatusPublisher
    controller: RuntimeController
    daemon: WorldlineDaemon

    @classmethod
    def build(cls, paths: WorldlinePaths | None = None) -> "WorldlineApplication":
        selected_paths = paths or WorldlinePaths.from_environment()
        core = Core.shared()
        store = StateStore(selected_paths, core)
        config = GlobalConfig.load(selected_paths)
        capabilities = CapabilityRegistry(selected_paths)
        publisher = StatusPublisher(selected_paths, store, capabilities.snapshot)
        controller = RuntimeController(selected_paths, store, config, capabilities, core=core)
        daemon = WorldlineDaemon(
            selected_paths,
            store,
            publisher,
            recover=controller.recover,
            reconcile_status=controller.roots.reconcile,
        )
        controller.register(daemon)
        return cls(
            selected_paths,
            core,
            store,
            config,
            capabilities,
            publisher,
            controller,
            daemon,
        )

    async def close(self) -> None:
        await self.daemon.stop()
        self.controller.close()
        self.store.close()
