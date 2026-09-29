from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import uuid
from typing import Any, Callable

from .core import Core
from .errors import WorldlineError
from .linux.git import GitAdapter
from .linux.inotify import InotifyWatcher
from .manifest import CapturedManifest, Manifest
from .paths import WorldlinePaths
from .prime import PrimeManager
from .store import StateStore


@dataclass(frozen=True, slots=True)
class FrozenParent:
    generation_id: str
    parent_instance: str
    parent_content: str
    payload: Path
    state_root: str
    workspace: dict[str, Any]
    root_set_hash: str
    manifests: dict[str, CapturedManifest]


class CheckpointManager:
    def __init__(
        self,
        paths: WorldlinePaths,
        store: StateStore,
        *,
        core: Core | None = None,
        watcher: InotifyWatcher | None = None,
        reconcile: Callable[[], Any] | None = None,
    ) -> None:
        self.paths = paths
        self.store = store
        self.core = core or Core.shared()
        self.watcher = watcher
        self.reconcile = reconcile
        self.prime = PrimeManager(paths, store, self.core)
        self.git = GitAdapter(self.core)

    def freeze(self) -> FrozenParent:
        if self.reconcile is not None and self.store.get_meta("dirty", False):
            self.reconcile()
        parent = self.store.prime()
        if parent is None or parent.content_id is None:
            raise WorldlineError("NO_PRIME", "fork requires an initialized PRIME")
        if self.watcher is None and self.store.roots():
            # 1.9.0: without a PRIME watcher nothing tells this freeze that PRIME moved while it
            # was copied, and the collapse decision would refuse the world later anyway
            # (MEASUREMENT_ABSENT). Refuse at the start instead.
            raise WorldlineError("PRIME_WATCH_UNAVAILABLE",
                                 "PRIME is not being watched (inotify unavailable or no root mappable); "
                                 "`worldline doctor` shows why")
        generation_id = str(uuid.uuid4())
        generation = self.paths.generations / generation_id
        payload = generation / "payload"
        manifests_directory = payload / "manifests"
        self.paths.prime_directory(generation)
        self.paths.prime_directory(payload)
        manifests_directory.mkdir(mode=0o700)
        before = self.watcher.synchronized_generation() if self.watcher is not None else None
        manifests: dict[str, CapturedManifest] = {}
        try:
            for root in self.store.roots():
                root_key = root["root_key"]
                logical = bytes(root["path"])
                source = self.paths.root_source(root)
                repository = self.git.capture(source) if root["kind"] == "repo" else None
                manifest = Manifest.capture(
                    source,
                    logical_root=logical,
                    root_key=root_key,
                    kind=root["kind"],
                    core=self.core,
                    repository=repository,
                )
                Manifest.materialize(manifest, source, payload / root_key, core=self.core)
                manifest.save(manifests_directory / f"{root_key}.json")
                manifests[root_key] = manifest
            parent_state = Path(parent.payload_path) / "manifests"
            for name in ("environment.json", "evidence.json", "agent.json"):
                source = parent_state / name
                if source.is_file():
                    shutil.copy2(source, manifests_directory / name)
            if self.watcher is not None and before != self.watcher.synchronized_generation():
                raise WorldlineError(
                    "PRIME_CHANGED_DURING_CAPTURE",
                    "PRIME changed while the fork checkpoint was copied and hashed",
                )
            state_root = Manifest.root_set_hash(manifests.values(), self.core)
            root_set = self.prime.root_set_hash(self.store.roots())
            return FrozenParent(
                generation_id=generation_id,
                parent_instance=parent.instance_id,
                parent_content=parent.content_id,
                payload=payload,
                state_root=state_root,
                workspace=parent.workspace,
                root_set_hash=root_set,
                manifests=manifests,
            )
        except BaseException:
            shutil.rmtree(generation, ignore_errors=True)
            raise

