from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
from typing import Any, AbstractSet

from .. import SCHEMA_VERSION
from ..canonical import atomic_write_json
from ..errors import WorldlineError
from ..paths import WorldlinePaths


class CriuAdapter:
    def __init__(self, paths: WorldlinePaths, owned_pids: AbstractSet[int]) -> None:
        self.paths = paths
        self.owned_pids = owned_pids
        self.executable = shutil.which("criu")
        if self.executable is None:
            raise WorldlineError("CRIU_UNAVAILABLE", "criu is not installed")
        check = subprocess.run(
            [self.executable, "check"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=30,
        )
        if check.returncode != 0:
            raise WorldlineError("CRIU_UNAVAILABLE", check.stderr.decode("utf-8", "replace").strip() or "criu check failed")

    def checkpoint(self, pid: int, destination: Path) -> None:
        if pid not in self.owned_pids:
            raise WorldlineError("CRIU_SCOPE_VIOLATION", f"pid is not WORLDLINE-owned: {pid}")
        if not Path(f"/proc/{pid}").is_dir():
            raise WorldlineError("PROCESS_EXITED", f"WORLDLINE-owned pid exited: {pid}")
        destination = destination.absolute()
        data = self.paths.data.resolve(strict=True)
        if Path(os.path.commonpath((destination, data))) != data:
            raise WorldlineError("CRIU_SCOPE_VIOLATION", f"checkpoint destination is outside WORLDLINE data: {destination}")
        destination.mkdir(mode=0o700, parents=True, exist_ok=False)
        result = subprocess.run(
            [self.executable, "dump", "--tree", str(pid), "--images-dir", str(destination), "--leave-running"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=120,
        )
        if result.returncode != 0:
            shutil.rmtree(destination, ignore_errors=True)
            raise WorldlineError("CRIU_CHECKPOINT_FAILED", result.stderr.decode("utf-8", "replace").strip())
        atomic_write_json(
            destination / "worldline-criu.json",
            {
                "schemaVersion": SCHEMA_VERSION,
                "owner": "worldline",
                "sourcePid": pid,
            },
        )

    def restore(self, checkpoint: Path) -> None:
        checkpoint = checkpoint.resolve(strict=True)
        data = self.paths.data.resolve(strict=True)
        if Path(os.path.commonpath((checkpoint, data))) != data:
            raise WorldlineError("CRIU_SCOPE_VIOLATION", f"checkpoint is outside WORLDLINE data: {checkpoint}")
        marker = checkpoint / "worldline-criu.json"
        try:
            import json

            value = json.loads(marker.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise WorldlineError("CRIU_SCOPE_VIOLATION", f"checkpoint lacks a WORLDLINE ownership marker: {checkpoint}") from exc
        if value.get("schemaVersion") != SCHEMA_VERSION or value.get("owner") != "worldline":
            raise WorldlineError("CRIU_SCOPE_VIOLATION", f"checkpoint ownership marker is invalid: {checkpoint}")
        result = subprocess.run(
            [
                self.executable,
                "restore",
                "--images-dir",
                str(checkpoint),
                "--restore-detached",
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=120,
        )
        if result.returncode != 0:
            raise WorldlineError("CRIU_RESTORE_FAILED", result.stderr.decode("utf-8", "replace").strip())

    @classmethod
    def capability(cls, paths: WorldlinePaths) -> dict[str, Any]:
        try:
            cls(paths, frozenset())
        except (WorldlineError, subprocess.TimeoutExpired) as exc:
            reason = exc.message if isinstance(exc, WorldlineError) else str(exc)
            return {"state": "UNAVAILABLE", "reason": reason}
        return {"state": "AVAILABLE", "scope": "worldline-owned-processes-only"}
