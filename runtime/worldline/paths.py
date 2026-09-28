from __future__ import annotations

from dataclasses import dataclass
import os
import re
from pathlib import Path
import stat
from typing import Any, Mapping

from .errors import WorldlineError


def _absolute(value: str | os.PathLike[str]) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        raise WorldlineError("INVALID_XDG_PATH", f"XDG path is not absolute: {path}")
    return path


_IDENTITY = re.compile(r"[1-9][0-9]{0,9}")


def _identity_list(value: str | None, name: str) -> tuple[int, ...]:
    """Parse a comma-separated list of distinct positive decimal identities from the environment.

    ASCII digits only: `int()` alone also takes spaces, underscores and other scripts' digits.
    """
    if value is None or value == "":
        return ()
    parts = value.split(",")
    if not all(_IDENTITY.fullmatch(part) for part in parts):
        raise WorldlineError("INVALID_CLIENT_MODE", f"{name} must list positive decimal identities")
    items = tuple(int(part) for part in parts)
    if len(set(items)) != len(items):
        raise WorldlineError("INVALID_CLIENT_MODE", f"{name} must list distinct identities")
    return items


def _nested(first: Path, second: Path) -> bool:
    return first == second or first in second.parents or second in first.parents


def secure_directory(path: Path, *, create: bool = True, shared_gid: int | None = None,
                     shared_mode: int = 0o750) -> Path:
    """A real directory owned by this uid: 0700, or `shared_mode` with group `shared_gid`."""
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
        # Dedicated-account client mode: the listed clients' group may read or traverse, never write.
        if shared_mode & 0o7027:
            raise ValueError(f"not a client-mode directory mode: {shared_mode:o}")
        if info.st_gid != shared_gid:
            try:
                os.chown(path, -1, shared_gid)
            except PermissionError as exc:
                raise WorldlineError(
                    "INVALID_CLIENT_MODE",
                    f"the daemon account is not a member of client group {shared_gid}") from exc
        if stat.S_IMODE(info.st_mode) != shared_mode:
            os.chmod(path, shared_mode)
        after = path.lstat()
        if after.st_gid != shared_gid or stat.S_IMODE(after.st_mode) != shared_mode:
            raise WorldlineError("UNSAFE_STORE", f"shared directory is not {shared_mode:o} for its group: {path}")
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
        if len(gids) > 1 or len(daemon) > 1 or bool(uids) != bool(gids):
            raise WorldlineError(
                "INVALID_CLIENT_MODE",
                "client mode needs exactly one WORLDLINE_CLIENT_GID and at least one WORLDLINE_CLIENT_UIDS")
        runtime = runtime_home / "worldline"
        if gids and any(_nested(runtime, other / "worldline") for other in (data_home, state_home, config_home)):
            # The runtime directory is opened to the client group; the store must never share it.
            raise WorldlineError("INVALID_CLIENT_MODE",
                                 "in client mode the runtime directory must be apart from data, state and config")
        return cls(
            home=home,
            data=data_home / "worldline",
            state=state_home / "worldline",
            runtime=runtime,
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

    def prime_directory(self, path: Path) -> Path:
        """A directory on the way from the live mapping to PRIME's content.

        In client mode the client group may traverse it (0710) but not list or write it, so a
        client reads PRIME through the symlink chain and nothing else. Otherwise it is 0700 like
        every store directory.
        """
        return secure_directory(path, shared_gid=self.client_gid, shared_mode=0o710)

    def share_live_chain(self) -> None:
        """Client mode: open the path to the CURRENT PRIME's content to the client group.

        New generations and transactions are created that way; this covers a store that was
        written before client mode (a migrated store) and is otherwise unreadable to clients
        until its next collapse. Only directories strictly between the store and each root's
        payload are touched; a root's own directory keeps the mode its manifest records.
        """
        if self.client_gid is None:
            return
        store = os.path.realpath(self.data)
        for mapping in sorted(self.live.iterdir()):
            if not mapping.is_symlink():
                continue
            target = os.path.realpath(mapping)
            if not target.startswith(store + os.sep):
                raise WorldlineError("LIVE_MAPPING_BROKEN", f"live mapping leaves the store: {mapping.name}")
            parts = Path(target).relative_to(store).parts[:-1]
            current = Path(store)
            for part in parts:
                current = current / part
                self.prime_directory(current)

    def root_source(self, root: Mapping[str, Any]) -> bytes:
        """The store directory holding a managed root's content, resolved through WORLDLINE's own
        live mapping and never through the registered path.

        The registered path is a link in a directory its operator owns. When the daemon runs as a
        dedicated account, that operator is only a client, and a client that re-points the link
        must not choose what the daemon captures, validates, loads policy from or keeps when
        pruning. The link must still route through the live mapping, or the root is refused.
        """
        root_key = str(root["root_key"])
        raw = bytes(root["path"])
        live = os.fsencode(self.live / root_key)
        try:
            routed = os.readlink(raw)
        except OSError as exc:
            raise WorldlineError(
                "LIVE_MAPPING_BROKEN",
                f"managed root is not a WORLDLINE symlink: {os.fsdecode(raw)}") from exc
        if routed != live:
            raise WorldlineError(
                "LIVE_MAPPING_BROKEN",
                f"managed root does not route through the live mapping: {os.fsdecode(raw)}")
        source = os.path.realpath(live)
        store = os.path.realpath(os.fsencode(self.data))
        if not source.startswith(store + b"/") or not os.path.isdir(source):
            raise WorldlineError(
                "LIVE_MAPPING_BROKEN",
                f"live mapping for {root_key} does not resolve to a directory in the store")
        return source

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
            if path == self.runtime:
                secure_directory(path, shared_gid=self.client_gid)
            elif path in (self.data, self.live, self.generations):
                self.prime_directory(path)
            else:
                secure_directory(path)
