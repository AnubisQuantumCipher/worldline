from __future__ import annotations

import os
from typing import Any, Callable

from . import SCHEMA_VERSION, __version__
from .canonical import atomic_write_json
from .model import utc_now
from .paths import WorldlinePaths
from .store import StateStore

_STATUS_FIELDS = {
    "schemaVersion",
    "daemon",
    "prime",
    "activeWorld",
    "worlds",
    "jobs",
    "capabilities",
    "lastReceipt",
    "ghostRecommendation",
}


class StatusPublisher:
    def __init__(
        self,
        paths: WorldlinePaths,
        store: StateStore,
        capabilities: Callable[[], dict[str, Any]] | None = None,
    ) -> None:
        self.paths = paths
        self.store = store
        self._capabilities = capabilities or (lambda: {})

    def snapshot(self, *, daemon_state: str = "RUNNING") -> dict[str, Any]:
        roots = self.store.roots()
        prime = self.store.prime()
        worlds = self.store.worlds()
        active = self.store.get_meta("activeWorld", "PRIME")
        last_receipt = self.store.last_receipt()
        prime_value: dict[str, Any] | None
        if prime is None:
            prime_value = None
        else:
            prime_value = {
                "alias": "PRIME",
                "instanceId": prime.instance_id,
                "id": prime.content_id,
                "state": "DEGRADED" if self.store.get_meta("watchState") == "DEGRADED" else prime.state.value,
                "generation": self.store.get_meta("primeGeneration"),
                "dirty": bool(self.store.get_meta("dirty", False)),
                # Set while the watcher's re-capture refuses; PRIME is then its last checkpoint.
                "watchError": self.store.get_meta("watchError"),
                "roots": [
                    {
                        "rootKey": root["root_key"],
                        "path": root["display_path"],
                        "kind": root["kind"],
                        "manifestRoot": root["manifest_root"],
                        "primary": bool(root["primary_root"]),
                    }
                    for root in roots
                ],
            }
        value: dict[str, Any] = {
            "schemaVersion": SCHEMA_VERSION,
            "daemon": {
                "state": daemon_state,
                "pid": os.getpid(),
                "version": __version__,
                "socket": str(self.paths.socket),
                "publishedAt": utc_now(),
            },
            "prime": prime_value,
            "activeWorld": active,
            "worlds": [world.summary() for world in worlds],
            "jobs": [
                {
                    "id": job["job_id"],
                    "world": job["world_instance"],
                    "state": job["state"],
                    "unit": job.get("systemd_unit"),
                    "started": job["started_at"],
                    "ended": job["ended_at"],
                    "error": job["error"],
                }
                for job in self.store.jobs()
            ],
            "capabilities": self._capabilities(),
            "lastReceipt": None if last_receipt is None else last_receipt["receipt"],
            "ghostRecommendation": self.store.get_meta("ghostRecommendation"),
        }
        if set(value) != _STATUS_FIELDS:
            raise AssertionError("runtime status schema drifted")
        return value

    def publish(self, *, daemon_state: str = "RUNNING") -> dict[str, Any]:
        value = self.snapshot(daemon_state=daemon_state)
        atomic_write_json(self.paths.status, value)
        return value
