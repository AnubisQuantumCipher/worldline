from __future__ import annotations

from copy import deepcopy
import time
from typing import Any, Callable

from .linux.atomic import AtomicExchange
from .linux.btrfs import BtrfsAdapter
from .linux.cgroups import CgroupAdapter
from .linux.criu import CriuAdapter
from .linux.docker import DockerAdapter
from .linux.git import GitAdapter
from .linux.hyprland import HyprlandAdapter
from .linux.inotify import InotifyWatcher
from .linux.overlay import OverlayAdapter
from .linux.systemd import SystemdAdapter
from .model import utc_now
from .paths import WorldlinePaths

# A probe that answered UNAVAILABLE is re-run after this many seconds. The first snapshot is
# taken when the daemon starts, which under a graphical session is while the user's systemd
# manager may still be "starting"; caching that answer forever reported systemd as UNAVAILABLE
# for the whole session even though `is-system-running` flipped to "running" seconds later.
# AVAILABLE answers stay cached (some probes launch a sandbox) until `doctor --refresh`.
_REPROBE_SECONDS = 30.0

_STATIC_SYSTEM_ROOT = {
    "state": "UNAVAILABLE",
    "reason": "system-root collapse requires a Btrfs system-root backend",
}


class CapabilityRegistry:
    def __init__(
        self,
        paths: WorldlinePaths,
        *,
        reprobe_seconds: float = _REPROBE_SECONDS,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.paths = paths
        self.paths.ensure()
        self._cached: dict[str, Any] | None = None
        self._probed_at: dict[str, float] = {}
        self._reprobe_seconds = reprobe_seconds
        self._clock = clock
        self._probes: dict[str, Callable[[], dict[str, Any]]] = {
            "overlay": lambda: OverlayAdapter.capability(self.paths),
            "btrfs": lambda: BtrfsAdapter.capability(self.paths),
            "systemd": SystemdAdapter.capability,
            "cgroups": CgroupAdapter.capability,
            "git": GitAdapter.capability,
            "docker": DockerAdapter.capability,
            "criu": lambda: CriuAdapter.capability(self.paths),
            "hyprland": HyprlandAdapter.capability,
            "inotify": InotifyWatcher.capability,
            "atomicExchange": lambda: AtomicExchange.capability(self.paths.data),
        }

    @staticmethod
    def _safe(probe: Callable[[], dict[str, Any]]) -> dict[str, Any]:
        try:
            return probe()
        except BaseException as exc:
            return {"state": "UNAVAILABLE", "reason": f"capability probe failed: {type(exc).__name__}: {exc}"}

    def _run(self, name: str) -> dict[str, Any]:
        value = self._safe(self._probes[name])
        value["probedAt"] = utc_now()
        self._probed_at[name] = self._clock()
        return value

    def _stale(self, name: str, entry: dict[str, Any]) -> bool:
        if entry.get("state") == "AVAILABLE":
            return False
        probed = self._probed_at.get(name)
        return probed is None or self._clock() - probed >= self._reprobe_seconds

    def snapshot(self, *, refresh: bool = False) -> dict[str, Any]:
        if self._cached is None or refresh:
            probed = {name: self._run(name) for name in self._probes}
        else:
            probed = {name: self._cached[name] for name in self._probes}
            for name, entry in list(probed.items()):
                if self._stale(name, entry):
                    probed[name] = self._run(name)
        overlay = probed["overlay"]
        value: dict[str, Any] = {
            "selectedBackend": "overlayfs" if overlay.get("state") == "AVAILABLE" else None,
            **probed,
            "namespaces": overlay,
            "systemRootCollapse": dict(_STATIC_SYSTEM_ROOT),
        }
        self._cached = value
        return deepcopy(value)
