from __future__ import annotations

from pathlib import Path
from typing import Any

from ..errors import WorldlineError
from .systemd import SystemdAdapter


class CgroupAdapter:
    def __init__(self, systemd: SystemdAdapter | None = None) -> None:
        self.systemd = systemd or SystemdAdapter()
        self.root = Path("/sys/fs/cgroup")
        if not (self.root / "cgroup.controllers").is_file():
            raise WorldlineError("CGROUPS_UNAVAILABLE", "unified cgroup v2 is not mounted")

    def capture(self, unit: str) -> dict[str, Any]:
        metadata = self.systemd.metadata(unit)
        control_group = metadata.get("ControlGroup")
        if not isinstance(control_group, str) or not control_group.startswith("/"):
            return {"state": "UNAVAILABLE", "unit": unit, "reason": "systemd did not report a control group"}
        directory = self.root / control_group.removeprefix("/")
        if not directory.is_dir():
            return {"state": "EXITED", "unit": unit, "controlGroup": control_group, "pids": []}

        def text(name: str) -> str | None:
            path = directory / name
            try:
                return path.read_text(encoding="ascii").strip()
            except FileNotFoundError:
                return None

        process_text = text("cgroup.procs") or ""
        pids = sorted(int(item) for item in process_text.splitlines() if item.isdigit())
        return {
            "state": "CAPTURED",
            "unit": unit,
            "controlGroup": control_group,
            "pids": pids,
            "memoryCurrent": text("memory.current"),
            "cpuStat": text("cpu.stat"),
            "pidsCurrent": text("pids.current"),
        }

    @classmethod
    def capability(cls) -> dict[str, Any]:
        try:
            cls()
        except WorldlineError as exc:
            return {"state": "UNAVAILABLE", "reason": exc.message}
        return {"state": "AVAILABLE", "version": "cgroup-v2"}
