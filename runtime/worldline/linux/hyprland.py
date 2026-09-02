from __future__ import annotations

import json
import re
import shutil
import subprocess
from typing import Any
import uuid

from ..errors import WorldlineError

_WORKSPACE_PATTERN = re.compile(r"^worldline:([0-9a-f-]{36})$")
_ADDRESS_PATTERN = re.compile(r"^0x[0-9a-fA-F]+$")


class HyprlandAdapter:
    def __init__(self) -> None:
        self.executable = shutil.which("hyprctl")
        if self.executable is None:
            raise WorldlineError("HYPRLAND_UNAVAILABLE", "hyprctl is not installed")

    def query(self, section: str) -> Any:
        if section not in {"clients", "workspaces", "monitors", "activeworkspace"}:
            raise WorldlineError("INVALID_HYPRLAND_QUERY", f"unsupported Hyprland query: {section}")
        result = subprocess.run(
            [self.executable, "-j", section],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=10,
        )
        if result.returncode != 0:
            raise WorldlineError("HYPRLAND_QUERY_FAILED", result.stderr.decode("utf-8", "replace").strip())
        try:
            return json.loads(result.stdout.decode("utf-8", "strict"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise WorldlineError("HYPRLAND_QUERY_FAILED", f"hyprctl {section} returned invalid JSON") from exc

    @staticmethod
    def workspace_name(instance_id: str) -> str:
        try:
            parsed = uuid.UUID(instance_id)
        except ValueError as exc:
            raise WorldlineError("INVALID_WORLD_INSTANCE", f"world instance is not a UUIDv4: {instance_id}") from exc
        if parsed.version != 4 or str(parsed) != instance_id:
            raise WorldlineError("INVALID_WORLD_INSTANCE", f"world instance is not a UUIDv4: {instance_id}")
        return f"worldline:{instance_id}"

    def focus_workspace(self, instance_id: str) -> None:
        name = self.workspace_name(instance_id)
        code = (
            'return hl.dispatch(hl.dsp.focus({ workspace = "name:'
            + name
            + '" }))'
        )
        result = subprocess.run(
            [self.executable, "eval", code],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=10,
        )
        if result.returncode != 0 or not result.stdout.startswith(b"ok"):
            raise WorldlineError("HYPRLAND_DISPATCH_FAILED", result.stderr.decode("utf-8", "replace").strip() or result.stdout.decode("utf-8", "replace").strip())

    def restore_live_clients(self, workspace: str, recorded: list[dict[str, Any]]) -> dict[str, list[str]]:
        match = _WORKSPACE_PATTERN.fullmatch(workspace)
        if match is None:
            raise WorldlineError("INVALID_WORKSPACE", f"not a WORLDLINE workspace: {workspace}")
        uuid.UUID(match.group(1))
        current = {item.get("address") for item in self.query("clients")}
        moved: list[str] = []
        missing: list[str] = []
        for client in recorded:
            address = client.get("address")
            if not isinstance(address, str) or _ADDRESS_PATTERN.fullmatch(address) is None:
                continue
            if address not in current:
                missing.append(address)
                continue
            code = (
                'return hl.dispatch(hl.dsp.window.move({ workspace = "name:'
                + workspace
                + '", follow = false, window = "address:'
                + address
                + '" }))'
            )
            result = subprocess.run(
                [self.executable, "eval", code],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=10,
            )
            if result.returncode == 0 and result.stdout.startswith(b"ok"):
                moved.append(address)
            else:
                missing.append(address)
        return {"moved": moved, "notReconstructed": missing}

    @classmethod
    def capability(cls) -> dict[str, Any]:
        try:
            adapter = cls()
            monitors = adapter.query("monitors")
        except (WorldlineError, subprocess.TimeoutExpired) as exc:
            reason = exc.message if isinstance(exc, WorldlineError) else str(exc)
            return {"state": "UNAVAILABLE", "reason": reason}
        return {"state": "AVAILABLE", "monitors": len(monitors) if isinstance(monitors, list) else None}
