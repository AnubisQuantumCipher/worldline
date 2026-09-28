from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import stat
from typing import Mapping

from .errors import WorldlineError


def _absolute(value: str | os.PathLike[str]) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        raise WorldlineError("INVALID_XDG_PATH", f"XDG path is not absolute: {path}")
    return path


def _identity_list(value: str | None, name: str) -> tuple[int, ...]:
    """Parse a comma-separated list of positive numeric identities from the environment."""
    if value is None or value == "":
        return ()
    try:
        items = tuple(int(part) for part in value.split(","))
    except ValueError as exc:
        raise WorldlineError("INVALID_CLIENT_MODE", f"{name} must list numeric identities") from exc
    if any(item <= 0 for item in items) or len(set(items)) != len(items):
        raise WorldlineError("INVALID_CLIENT_MODE", f"{name} must list distinct positive identities")
    return items


def secure_directory(path: Path, *, create: bool = True, shared_gid: int | None = None) -> Path:
    """A real directory owned by this uid: 0700, or 0750 group `shared_gid` in client mode."""
    if create:
        path.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        info = path.lstat()
    except FileNotFoundError as exc:
        raise WorldlineError("STORE_MISSING", f"required directory is missing: {path}") from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        raise WorldlineError("UNSAFE_STORE", f"store path is not a real directory: {path}")
    if info.st_uid != os.getuid():
        raise WorldlineError("UNSAFE_STORE", f"store path is not owned by uid {os.getuid()}: {path}")
    if shared_gid is not None:
        # Dedicated-account client mode: the listed clients' group may traverse, never write.
        if info.st_gid != shared_gid:
            os.chown(path, -1, shared_gid)
        if stat.S_IMODE(info.st_mode) != 0o750:
            os.chmod(path, 0o750)
        after = path.lstat()
        if after.st_gid != shared_gid or stat.S_IMODE(after.st_mode) != 0o750:
            raise WorldlineError("UNSAFE_STORE", f"shared runtime directory is not 0750 for its group: {path}")
        return path
    if stat.S_IMODE(info.st_mode) & 0o077:
        os.chmod(path, 0o700)
        if stat.S_IMODE(path.stat().st_mode) & 0o077:
            raise WorldlineError("UNSAFE_STORE", f"store path is accessible by another user: {path}")
    return path


@dataclass(frozen=True, slots=True)
class WorldlinePaths:
    home: Path
    data: Path
    state: Path
    runtime: Path
    config: Path
    # Dedicated-account client mode, set only by the root-owned service environment: the
    # group that may reach the socket and status, and the peer uids the daemon serves.
    client_gid: int | None = None
    client_uids: tuple[int, ...] = ()
    # Client side: the uid the daemon must run as (defaults to the caller's own uid).
    daemon_uid: int | None = None

    @classmethod
    def from_environment(cls, env: Mapping[str, str] | None = None) -> "WorldlinePaths":
        values = os.environ if env is None else env
        home = _absolute(values.get("HOME", str(Path.home())))
        data_home = _absolute(values.get("XDG_DATA_HOME", str(home / ".local/share")))
        state_home = _absolute(values.get("XDG_STATE_HOME", str(home / ".local/state")))
        config_home = _absolute(values.get("XDG_CONFIG_HOME", str(home / ".config")))
        runtime_home = _absolute(values.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}"))
        gids = _identity_list(values.get("WORLDLINE_CLIENT_GID"), "WORLDLINE_CLIENT_GID")
        uids = _identity_list(values.get("WORLDLINE_CLIENT_UIDS"), "WORLDLINE_CLIENT_UIDS")
        daemon = _identity_list(values.get("WORLDLINE_DAEMON_UID"), "WORLDLINE_DAEMON_UID")
        if len(gids) > 1 or len(daemon) > 1 or (uids and not gids):
            raise WorldlineError(
                "INVALID_CLIENT_MODE",
                "client mode needs exactly one WORLDLINE_CLIENT_GID for its WORLDLINE_CLIENT_UIDS")
        return cls(
            home=home,
            data=data_home / "worldline",
            state=state_home / "worldline",
            runtime=runtime_home / "worldline",
            config=config_home / "worldline",
            client_gid=gids[0] if gids else None,
            client_uids=uids,
            daemon_uid=daemon[0] if daemon else None,
        )

    @property
    def database(self) -> Path:
        return self.state / "worldline.sqlite3"

    @property
    def socket(self) -> Path:
        return self.runtime / "worldlined.sock"

    @property
    def status(self) -> Path:
        return self.runtime / "status.json"

    @property
    def live(self) -> Path:
        return self.data / "live"

    @property
    def generations(self) -> Path:
        return self.data / "generations"

    @property
    def worlds(self) -> Path:
        return self.data / "worlds"

    @property
    def overlays(self) -> Path:
        return self.data / "overlays"

    @property
    def events(self) -> Path:
        return self.state / "events"

    @property
    def receipts(self) -> Path:
        return self.state / "receipts"

    @property
    def transactions(self) -> Path:
        return self.state / "transactions"

    @property
    def logs(self) -> Path:
        return self.state / "logs"

    @property
    def config_file(self) -> Path:
        return self.config / "config.json"

    def ensure(self) -> None:
        for path in (
            self.data,
            self.state,
            self.runtime,
            self.config,
            self.live,
            self.generations,
            self.worlds,
            self.overlays,
            self.events,
            self.receipts,
            self.transactions,
            self.logs,
        ):
            secure_directory(path, shared_gid=self.client_gid if path == self.runtime else None)
