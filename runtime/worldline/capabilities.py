from __future__ import annotations

from copy import deepcopy
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
from .paths import WorldlinePaths


class CapabilityRegistry:
    def __init__(self, paths: WorldlinePaths) -> None:
        self.paths = paths
        self.paths.ensure()
        self._cached: dict[str, Any] | None = None

    @staticmethod
    def _safe(probe: Callable[[], dict[str, Any]]) -> dict[str, Any]:
        try:
            return probe()
        except BaseException as exc:
            return {"state": "UNAVAILABLE", "reason": f"capability probe failed: {type(exc).__name__}: {exc}"}

    def snapshot(self, *, refresh: bool = False) -> dict[str, Any]:
        if self._cached is not None and not refresh:
            return deepcopy(self._cached)
        overlay = self._safe(lambda: OverlayAdapter.capability(self.paths))
        value = {
            "selectedBackend": "overlayfs" if overlay.get("state") == "AVAILABLE" else None,
            "overlay": overlay,
            "btrfs": self._safe(lambda: BtrfsAdapter.capability(self.paths)),
            "namespaces": overlay,
            "systemd": self._safe(SystemdAdapter.capability),
            "cgroups": self._safe(CgroupAdapter.capability),
            "git": self._safe(GitAdapter.capability),
            "docker": self._safe(DockerAdapter.capability),
            "criu": self._safe(lambda: CriuAdapter.capability(self.paths)),
            "hyprland": self._safe(HyprlandAdapter.capability),
            "inotify": self._safe(InotifyWatcher.capability),
            "atomicExchange": self._safe(lambda: AtomicExchange.capability(self.paths.data)),
            "systemRootCollapse": {
                "state": "UNAVAILABLE",
                "reason": "system-root collapse requires a Btrfs system-root backend",
            },
        }
        self._cached = value
        return deepcopy(value)
