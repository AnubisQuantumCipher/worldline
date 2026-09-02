from __future__ import annotations

from typing import Any, Callable

from . import SCHEMA_VERSION
from .linux.inotify import InotifyWatcher, stable_capture
from .store import StateStore


class PrimeChangeTracker:
    def __init__(self, store: StateStore, watcher: InotifyWatcher) -> None:
        self.store = store
        self.watcher = watcher

    def external_event(self, event: dict[str, Any]) -> None:
        self.store.set_meta("dirty", True)
        self.store.set_meta("inotifyGeneration", event["generation"])
        if event["kind"] == "overflow":
            self.store.set_meta("watchState", "DEGRADED")
        prime = self.store.prime()
        if prime is None:
            return
        self.store.append_causal_event(
            {
                "schemaVersion": SCHEMA_VERSION,
                "worldInstance": prime.instance_id,
                "kind": "external",
                "actor": "external",
                "tool": None,
                "reason": None,
                "rootKey": event.get("rootKey"),
                "pathB64": event.get("pathB64"),
                "pathDisplay": event.get("pathDisplay"),
                "inotifyMask": event["mask"],
                "generation": event["generation"],
            }
        )

    def reconcile(self, capture: Callable[[], Any]) -> Any:
        result = stable_capture(self.watcher, capture)
        self.store.set_meta("dirty", False)
        self.store.set_meta("watchState", "HEALTHY")
        self.store.set_meta("inotifyGeneration", self.watcher.generation)
        return result
