from __future__ import annotations

from dataclasses import dataclass
import os
import re
import shutil
import subprocess
import time
from typing import Any, Sequence
import uuid

from ..errors import WorldlineError

_UNIT_PATTERN = re.compile(r"^worldline-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.service$")


@dataclass(slots=True)
class SystemdProcess:
    unit: str
    launcher: subprocess.Popen[bytes]
    manager: "SystemdAdapter"
    # Bytes read from the launcher's stderr while confirming supervision; the runner writes them
    # ahead of the rest so nothing the agent said is lost.
    stderr_prelude: bytes = b""
    supervision_confirmed: bool = False

    @property
    def pid(self) -> int | None:
        value = self.manager.metadata(self.unit).get("MainPID")
        return value if isinstance(value, int) and value > 0 else None

    def stop(self) -> None:
        self.manager.stop(self.unit)


def manager_environment(environment: dict[str, str] | None = None) -> dict[str, str]:
    """Environment under which `systemctl --user` can reach the session's real manager.

    `systemctl --user` connects to `$XDG_RUNTIME_DIR/systemd/private` and does not fall back to
    `DBUS_SESSION_BUS_ADDRESS`, while `systemd-run --user` does. WORLDLINE redirects
    XDG_RUNTIME_DIR whenever it runs isolated (the health check, the e2e tests, any second
    instance), which made the daemon able to START transient units it could then neither stop,
    query, nor cancel -- the "supervision is not exercised in the harness" caveat, and a real
    gap for cancel. Point every systemd call at the manager that actually owns the units.
    """
    values = dict(os.environ if environment is None else environment)
    runtime = values.get("XDG_RUNTIME_DIR")
    if runtime and os.path.exists(os.path.join(runtime, "systemd", "private")):
        return values
    real = f"/run/user/{os.getuid()}"
    if os.path.exists(os.path.join(real, "systemd", "private")):
        values["XDG_RUNTIME_DIR"] = real
        values.setdefault("DBUS_SESSION_BUS_ADDRESS", f"unix:path={real}/bus")
    return values


class SystemdAdapter:
    def __init__(self) -> None:
        self.systemd_run = shutil.which("systemd-run")
        self.systemctl = shutil.which("systemctl")
        if self.systemd_run is None or self.systemctl is None:
            raise WorldlineError("SYSTEMD_UNAVAILABLE", "systemd-run or systemctl is not installed")
        self.environment = manager_environment()

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
        # Supervision is required, not best effort: the manager must answer BEFORE a unit is
        # asked of it, and the unit must be seen by the manager AFTER. A launcher that dies
        # without the manager ever knowing the unit was never a supervised world, and is refused
        # by name instead of being read as an agent that failed.
        self.verify_manager()
        try:
            launcher = subprocess.Popen(
                command,
                stdin=stdin,
                stdout=stdout,
                stderr=stderr,
                start_new_session=True,
                close_fds=True,
                env=self.environment,
            )
        except OSError as exc:
            raise WorldlineError("SYSTEMD_LAUNCH_FAILED", str(exc), {"unit": unit}) from exc
        return self._confirm_supervision(unit, launcher)

    def verify_manager(self) -> dict[str, str]:
        """Ask the user service manager something only it can answer. A manager that is
        `degraded` (some unit failed somewhere) answers; one that cannot be reached does not."""
        result = subprocess.run(
            [self.systemctl, "--user", "show", "--property=Version", "--property=NFailedUnits"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=10,
            env=self.environment,
        )
        if result.returncode != 0:
            reason = result.stderr.decode("utf-8", "replace").strip() or f"systemctl exited {result.returncode}"
            raise WorldlineError("SUPERVISION_UNAVAILABLE", f"the user service manager cannot be reached: {reason}")
        values: dict[str, str] = {}
        for line in result.stdout.decode("utf-8", "replace").splitlines():
            name, separator, value = line.partition("=")
            if separator:
                values[name] = value
        return values

    _CONFIRM_WINDOW_SECONDS = 1.0

    def _confirm_supervision(self, unit: str, launcher: subprocess.Popen[bytes]) -> SystemdProcess:
        deadline = time.monotonic() + self._CONFIRM_WINDOW_SECONDS
        while True:
            shown = subprocess.run(
                [self.systemctl, "--user", "show", unit, "--property=LoadState", "--property=ActiveState"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=10,
                env=self.environment,
            )
            if shown.returncode == 0 and "LoadState=loaded" in shown.stdout.decode("utf-8", "replace"):
                return SystemdProcess(unit=unit, launcher=launcher, manager=self, supervision_confirmed=True)
            code = launcher.poll()
            if code is None:
                if time.monotonic() >= deadline:
                    # The manager answered the pre-flight and the launcher is alive; the unit has
                    # just not been observed yet. Proceed unconfirmed rather than refuse late.
                    return SystemdProcess(unit=unit, launcher=launcher, manager=self)
                time.sleep(0.05)
                continue
            if code == 0:
                # Ran to completion before it could be observed: a very short world.
                return SystemdProcess(unit=unit, launcher=launcher, manager=self)
            prelude = b""
            if launcher.stderr is not None:
                try:
                    prelude = launcher.stderr.read()
                except OSError:
                    prelude = b""
            if prelude.lstrip().startswith(b"Failed to"):
                # systemd-run's own failure ("Failed to connect to bus", "Failed to start
                # transient service unit"): the manager never took the unit.
                first = prelude.decode("utf-8", "replace").strip().splitlines()[0]
                raise WorldlineError("SUPERVISION_UNAVAILABLE", f"transient unit was not started: {first}", {"unit": unit, "exitCode": code})
            return SystemdProcess(unit=unit, launcher=launcher, manager=self, stderr_prelude=prelude)

    def stop(self, unit: str) -> None:
        self._validate_unit(unit)
        result = subprocess.run(
            [self.systemctl, "--user", "stop", unit],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=20,
            env=self.environment,
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
            env=self.environment,
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
    def capability(cls, adapter: "SystemdAdapter | None" = None) -> dict[str, Any]:
        try:
            adapter = adapter or cls()
        except WorldlineError as exc:
            return {"state": "UNAVAILABLE", "reason": exc.message}
        # AVAILABLE means the manager can be QUERIED, which is what launch, cancel, and the
        # startup sweep need. `is-system-running` is recorded as information only: it answers
        # "degraded" with exit status 1 whenever any unit anywhere has failed, and the earlier
        # probe read that exit status as "no supervision" while every world kept running in a
        # transient unit exactly as before (worldline-lab D8b, 2026-09-21).
        try:
            manager = adapter.verify_manager()
        except WorldlineError as exc:
            return {"state": "UNAVAILABLE", "reason": exc.message}
        result = subprocess.run(
            [adapter.systemctl, "--user", "is-system-running"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=10,
            env=adapter.environment,
        )
        state = result.stdout.decode("utf-8", "replace").strip() or "unknown"
        runtime = adapter.environment.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
        filesystem = os.statvfs(runtime)
        if filesystem.f_bavail == 0:
            return {"state": "UNAVAILABLE", "reason": f"XDG runtime filesystem is full: {runtime}"}
        failed = manager.get("NFailedUnits", "")
        return {
            "state": "AVAILABLE",
            "managerState": state,
            "manager": runtime,
            "managerVersion": manager.get("Version"),
            "failedUnits": int(failed) if failed.isdigit() else failed,
        }
