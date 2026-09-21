from __future__ import annotations

from dataclasses import dataclass
import json
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
    # Realtime (µs) just before systemd-run was spawned: the journal window opens here.
    launched_at_us: int = 0

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
        self.journalctl = shutil.which("journalctl")
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
        # asked of it. What happened AFTER is read from the manager's own journal entries once
        # the launcher exits (`outcome`), never from anything the workload printed.
        self.verify_manager()
        launched_at_us = time.time_ns() // 1000
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
        return SystemdProcess(unit=unit, launcher=launcher, manager=self, launched_at_us=launched_at_us)

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

    # Journal message ids the user manager writes about a unit (systemd catalog; stable across
    # releases). Entries are matched on these ids and on journald's trusted `_` fields, so a
    # workload cannot forge them (the sandbox has no journal socket at all).
    JOURNAL_STARTING = "7d4958e842da4a758f6c1cdc7b36dcc5"
    JOURNAL_STARTED = "39f53479d3a045ac8e11786248231fbf"
    JOURNAL_STOPPING = "de5b426a63be47a7b6ac3eaac82e2f6f"
    JOURNAL_STOPPED = "9d1aaa27d60140bd96365438aad20286"
    JOURNAL_PROCESS_EXIT = "98e322203f7a4ed290d09fe03c09fe15"
    JOURNAL_FAILURE_RESULT = "d9b373ed55a64feb8242e02dbe79a49c"
    JOURNAL_WINDOW_SECONDS = 5.0

    def journal_events(self, unit: str, since_us: int) -> list[dict[str, Any]] | None:
        """The user manager's own journal entries about `unit` since `since_us`, structured.
        None when the journal cannot be read (then supervision is INDETERMINATE, never assumed)."""
        self._validate_unit(unit)
        journalctl = self.journalctl
        if journalctl is None:
            return None
        result = subprocess.run(
            [journalctl, "--user", "-u", unit, "-o", "json", "--no-pager", f"--since=@{max(since_us // 1_000_000 - 2, 0)}"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=15,
            env=self.environment,
        )
        if result.returncode != 0:
            return None
        manager_unit = f"user@{os.getuid()}.service"
        events: list[dict[str, Any]] = []
        for line in result.stdout.decode("utf-8", "replace").splitlines():
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(entry, dict):
                continue
            # Trusted fields only: authored by the manager process, about this unit, in window.
            if entry.get("_SYSTEMD_UNIT") != manager_unit or entry.get("_COMM") != "systemd":
                continue
            if entry.get("USER_UNIT") not in (None, unit) and entry.get("UNIT") not in (None, unit):
                continue
            try:
                stamp = int(entry.get("__REALTIME_TIMESTAMP", "0"))
            except (TypeError, ValueError):
                continue
            if stamp < since_us:
                continue
            events.append(
                {
                    "messageId": entry.get("MESSAGE_ID"),
                    "message": str(entry.get("MESSAGE", ""))[:200],
                    "jobType": entry.get("JOB_TYPE"),
                    "jobResult": entry.get("JOB_RESULT"),
                    "exitCode": entry.get("EXIT_CODE"),
                    "exitStatus": entry.get("EXIT_STATUS"),
                    "managerPid": entry.get("_PID"),
                    "realtimeUs": stamp,
                }
            )
        return events

    def outcome(self, process: SystemdProcess, launcher_exit: int, *, stopped: bool = False) -> dict[str, Any]:
        """Structured supervision outcome for a finished launcher. Exactly one of:
        SUPERVISED (the manager started the unit; the workload's exit is authoritative),
        LAUNCH_FAILED (the launcher ended without the manager ever starting the unit),
        INDETERMINATE (the journal could not be read, or no entry appeared inside the window).
        Bounded: polls the journal for at most JOURNAL_WINDOW_SECONDS after the launcher exit."""
        deadline = time.monotonic() + self.JOURNAL_WINDOW_SECONDS
        events: list[dict[str, Any]] | None = None
        journal_readable = True
        while True:
            events = self.journal_events(process.unit, process.launched_at_us)
            if events is None:
                journal_readable = False
                events = []
            ids = {event["messageId"] for event in events}
            started = self.JOURNAL_STARTED in ids
            ended = bool(ids & {self.JOURNAL_PROCESS_EXIT, self.JOURNAL_FAILURE_RESULT, self.JOURNAL_STOPPED})
            if started and (ended or launcher_exit == 0 or stopped):
                break
            if not journal_readable or time.monotonic() >= deadline:
                break
            time.sleep(0.2)
        exit_entry = next((event for event in events if event["messageId"] == self.JOURNAL_PROCESS_EXIT), None)
        failure_entry = next((event for event in events if event["messageId"] == self.JOURNAL_FAILURE_RESULT), None)
        started = any(event["messageId"] == self.JOURNAL_STARTED for event in events)
        launched = any(event["messageId"] == self.JOURNAL_STARTING for event in events)
        stopped_by_manager = any(event["messageId"] in {self.JOURNAL_STOPPING, self.JOURNAL_STOPPED} for event in events)
        if started:
            kind = "SUPERVISED"
        elif not journal_readable:
            kind = "INDETERMINATE"
        elif launcher_exit != 0 and not launched:
            kind = "LAUNCH_FAILED"
        else:
            kind = "INDETERMINATE"
        launcher_stderr = ""
        if kind != "SUPERVISED" and process.launcher.stderr is not None:
            try:
                launcher_stderr = process.launcher.stderr.read().decode("utf-8", "replace")[:400]
            except (OSError, ValueError):
                launcher_stderr = ""
        return {
            "kind": kind,
            "unit": process.unit,
            "source": "journal" if journal_readable else "journal-unavailable",
            "launcherExit": launcher_exit,
            "started": started,
            "stoppedByManager": stopped_by_manager,
            "exitCode": None if exit_entry is None else exit_entry.get("exitCode"),
            "exitStatus": None if exit_entry is None or exit_entry.get("exitStatus") is None else int(exit_entry["exitStatus"]) if str(exit_entry["exitStatus"]).isdigit() else exit_entry.get("exitStatus"),
            "result": (
                "stopped" if stopped_by_manager
                else "failure" if failure_entry is not None or (exit_entry is not None and str(exit_entry.get("exitStatus")) not in ("0", "None"))
                else "success" if started and launcher_exit == 0
                else None
            ),
            # Canonical JSON carries no floats: the bounded window is reported in milliseconds.
            "windowMilliseconds": int(self.JOURNAL_WINDOW_SECONDS * 1000),
            "events": events,
            # Diagnostic only, never used to classify: what the launcher itself printed.
            "launcherStderr": launcher_stderr,
        }

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
        properties = ("MainPID", "ControlGroup", "ActiveState", "SubState", "ExecMainStatus", "Result", "InvocationID", "ExecMainStartTimestampMonotonic")
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
