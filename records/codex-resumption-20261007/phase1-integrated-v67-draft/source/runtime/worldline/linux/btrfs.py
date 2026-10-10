from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
from typing import Any

from ..errors import WorldlineError
from ..paths import WorldlinePaths


def _unescape_mount(value: str) -> str:
    return value.replace("\\040", " ").replace("\\011", "\t").replace("\\012", "\n").replace("\\134", "\\")


def filesystem_type(path: Path) -> str | None:
    resolved = path.resolve(strict=True)
    selected: tuple[int, str] | None = None
    for line in Path("/proc/self/mountinfo").read_text(encoding="utf-8").splitlines():
        fields = line.split()
        try:
            separator = fields.index("-")
        except ValueError:
            continue
        mount_point = Path(_unescape_mount(fields[4]))
        try:
            common = Path(os.path.commonpath((resolved, mount_point)))
        except ValueError:
            continue
        if common != mount_point:
            continue
        candidate = (len(str(mount_point)), fields[separator + 1])
        if selected is None or candidate[0] > selected[0]:
            selected = candidate
    return None if selected is None else selected[1]


class BtrfsAdapter:
    def __init__(self, paths: WorldlinePaths) -> None:
        self.paths = paths
        fs_type = filesystem_type(paths.data)
        if fs_type != "btrfs":
            raise WorldlineError("BTRFS_UNAVAILABLE", f"WORLDLINE data store filesystem is {fs_type or 'unknown'}, not btrfs")
        self.executable = shutil.which("btrfs")
        if self.executable is None:
            raise WorldlineError("BTRFS_UNAVAILABLE", "btrfs userspace tool is not installed")

    def readonly_snapshot(self, source: Path, destination: Path) -> None:
        source = source.resolve(strict=True)
        destination = destination.absolute()
        data = self.paths.data.resolve(strict=True)
        if Path(os.path.commonpath((destination, data))) != data:
            raise WorldlineError("BTRFS_SCOPE_VIOLATION", f"snapshot destination is outside WORLDLINE data: {destination}")
        if destination.exists():
            raise WorldlineError("BTRFS_DESTINATION_EXISTS", f"snapshot destination exists: {destination}")
        show = subprocess.run(
            [self.executable, "subvolume", "show", str(source)],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=15,
        )
        if show.returncode != 0:
            raise WorldlineError("BTRFS_NOT_SUBVOLUME", f"snapshot source is not a Btrfs subvolume: {source}")
        result = subprocess.run(
            [self.executable, "subvolume", "snapshot", "-r", str(source), str(destination)],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=60,
        )
        if result.returncode != 0:
            raise WorldlineError(
                "BTRFS_SNAPSHOT_FAILED",
                result.stderr.decode("utf-8", "replace").strip() or f"btrfs exited {result.returncode}",
            )

    @classmethod
    def capability(cls, paths: WorldlinePaths) -> dict[str, Any]:
        try:
            cls(paths)
        except WorldlineError as exc:
            return {"state": "UNAVAILABLE", "reason": exc.message}
        return {"state": "AVAILABLE", "backend": "btrfs-subvolume"}
