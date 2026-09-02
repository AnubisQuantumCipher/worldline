from __future__ import annotations

from dataclasses import dataclass
import os
import re
import shutil
import subprocess
from typing import Any, Sequence
import uuid

from ..errors import WorldlineError

_UNIT_PATTERN = re.compile(r"^worldline-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.service$")


@dataclass(slots=True)
class SystemdProcess:
    unit: str
    launcher: subprocess.Popen[bytes]
    manager: "SystemdAdapter"

    @property
    def pid(self) -> int | None:
        value = self.manager.metadata(self.unit).get("MainPID")
        return value if isinstance(value, int) and value > 0 else None

    def stop(self) -> None:
        self.manager.stop(self.unit)


class SystemdAdapter:
    def __init__(self) -> None:
        self.systemd_run = shutil.which("systemd-run")
        self.systemctl = shutil.which("systemctl")
        if self.systemd_run is None or self.systemctl is None:
            raise WorldlineError("SYSTEMD_UNAVAILABLE", "systemd-run or systemctl is not installed")

    @staticmethod
    def unit_name(instance_id: str) -> str:
        try:
            parsed = uuid.UUID(instance_id)
        except ValueError as exc:
            raise WorldlineError("INVALID_WORLD_INSTANCE", f"world instance is not a UUIDv4: {instance_id}") from exc
        if parsed.version != 4 or str(parsed) != instance_id:
            raise WorldlineError("INVALID_WORLD_INSTANCE", f"world instance is not a UUIDv4: {instance_id}")
        return f"worldline-{instance_id}.service"

    @staticmethod
    def _validate_unit(unit: str) -> None:
        if _UNIT_PATTERN.fullmatch(unit) is None:
            raise WorldlineError("FOREIGN_SYSTEMD_UNIT", f"refusing to manage non-WORLDLINE unit: {unit}")

    def launch(
        self,
        instance_id: str,
        argv: Sequence[str],
        *,
        description: str,
        nice: int | None = None,
        restart: str = "never",
        pty: bool = False,
        stdin: int | Any = subprocess.PIPE,
        stdout: int | Any = subprocess.PIPE,
        stderr: int | Any = subprocess.PIPE,
    ) -> SystemdProcess:
        if not argv or any(not isinstance(item, str) or not item for item in argv):
            raise WorldlineError("INVALID_AGENT_COMMAND", "transient unit argv must be nonempty strings")
        unit = self.unit_name(instance_id)
        command = [
            self.systemd_run,
            "--user",
            f"--unit={unit}",
            f"--description={description}",
            "--collect",
            "--pty" if pty else "--pipe",
            "--quiet",
            "--service-type=exec",
            "--property=KillMode=control-group",
            "--property=SendSIGKILL=yes",
            "--property=TimeoutStopSec=10s",
            "--property=NoNewPrivileges=yes",
            "--property=PrivateTmp=no",
            "--",
            *argv,
        ]
        if nice is not None:
            if not isinstance(nice, int) or nice < -20 or nice > 19:
                raise WorldlineError("INVALID_PRIORITY", f"systemd Nice value is invalid: {nice}")
            command.insert(command.index("--"), f"--property=Nice={nice}")
        if restart not in {"never", "on-failure"}:
            raise WorldlineError("INVALID_RESTART_POLICY", f"unsupported restart policy: {restart}")
        if restart == "on-failure":
            separator = command.index("--")
            command.insert(separator, "--property=RestartSec=2s")
            command.insert(separator, "--property=Restart=on-failure")
        try:
            launcher = subprocess.Popen(
                command,
                stdin=stdin,
                stdout=stdout,
                stderr=stderr,
                start_new_session=True,
                close_fds=True,
            )
        except OSError as exc:
            raise WorldlineError("SYSTEMD_LAUNCH_FAILED", str(exc), {"unit": unit}) from exc
        return SystemdProcess(unit=unit, launcher=launcher, manager=self)

    def stop(self, unit: str) -> None:
        self._validate_unit(unit)
        result = subprocess.run(
            [self.systemctl, "--user", "stop", unit],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=20,
        )
        if result.returncode not in (0, 5):
            raise WorldlineError(
                "SYSTEMD_STOP_FAILED",
                result.stderr.decode("utf-8", "replace").strip() or f"systemctl exited {result.returncode}",
                {"unit": unit},
            )

    def metadata(self, unit: str) -> dict[str, Any]:
        self._validate_unit(unit)
        properties = ("MainPID", "ControlGroup", "ActiveState", "SubState", "ExecMainStatus", "Result")
        result = subprocess.run(
            [self.systemctl, "--user", "show", unit, *[f"--property={item}" for item in properties]],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=10,
        )
        if result.returncode != 0:
            return {"unit": unit, "state": "UNAVAILABLE", "reason": result.stderr.decode("utf-8", "replace").strip()}
        values: dict[str, Any] = {"unit": unit, "state": "CAPTURED"}
        for line in result.stdout.decode("utf-8", "replace").splitlines():
            name, separator, value = line.partition("=")
            if not separator:
                continue
            values[name] = int(value) if name in {"MainPID", "ExecMainStatus"} and value.isdigit() else value
        return values

    @classmethod
    def capability(cls) -> dict[str, Any]:
        try:
            adapter = cls()
        except WorldlineError as exc:
            return {"state": "UNAVAILABLE", "reason": exc.message}
        result = subprocess.run(
            [adapter.systemctl, "--user", "is-system-running"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=10,
        )
        state = result.stdout.decode("utf-8", "replace").strip()
        if result.returncode != 0 or state not in {"running", "degraded"}:
            return {"state": "UNAVAILABLE", "reason": state or result.stderr.decode("utf-8", "replace").strip()}
        runtime = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
        filesystem = os.statvfs(runtime)
        if filesystem.f_bavail == 0:
            return {"state": "UNAVAILABLE", "reason": f"XDG runtime filesystem is full: {runtime}"}
        return {"state": "AVAILABLE", "managerState": state}
