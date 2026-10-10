from __future__ import annotations

from typing import Any

from ..paths import WorldlinePaths
from .namespaces import BubblewrapSandbox


class OverlayAdapter:
    name = "overlayfs+bubblewrap"

    @staticmethod
    def capability(paths: WorldlinePaths) -> dict[str, Any]:
        return BubblewrapSandbox.capability(paths)

    @staticmethod
    def create(paths: WorldlinePaths) -> BubblewrapSandbox:
        return BubblewrapSandbox(paths)
