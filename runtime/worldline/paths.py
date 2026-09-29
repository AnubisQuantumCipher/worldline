from __future__ import annotations

from dataclasses import dataclass
import errno
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
    if any(item >= (1 << 32) - 1 for item in items):  # (uid_t)-1 and above are not identities
        raise WorldlineError("INVALID_CLIENT_MODE", f"{name} lists an identity out of range")
    if len(set(items)) != len(items):
        raise WorldlineError("INVALID_CLIENT_MODE", f"{name} must list distinct identities")
    return items


def _refuse_clients_in_daemon_group(uids: tuple[int, ...]) -> None:
    """A listed client must not share the daemon's primary group: content the daemon creates
    carries that group, so its group bits would be the client's."""
    import grp
    import pwd
    try:
        daemon_group = grp.getgrgid(os.getgid())
    except KeyError:
        return
    for uid in uids:
        try:
            entry = pwd.getpwuid(uid)
        except KeyError:
            continue  # no account: it has no primary group and no named membership
        if entry.pw_gid == os.getgid() or entry.pw_name in daemon_group.gr_mem:
            raise WorldlineError("INVALID_CLIENT_MODE",
                                 f"client uid {uid} is in the daemon account's group {daemon_group.gr_name}")


def _refuse_client_group_overlap(client_gid: int) -> None:
    """Every member of the client group can traverse to PRIME, listed or not. A member that is
    also in the daemon's group could write what the daemon's group may write (review of 796cb02).
    Named members are checked; accounts whose primary group is the client group cannot be listed
    here, which is why the two groups must be kept disjoint (SECURITY.md limit 7)."""
    import grp
    import pwd
    try:
        clients = grp.getgrgid(client_gid)
        daemon_group = grp.getgrgid(os.getgid())
    except KeyError:
        return
    for name in clients.gr_mem:
        try:
            entry = pwd.getpwnam(name)
        except KeyError:
            continue
        if entry.pw_uid != os.getuid() and (entry.pw_gid == os.getgid() or name in daemon_group.gr_mem):
            raise WorldlineError("INVALID_CLIENT_MODE",
                                 f"{name}, a member of the client group, is in the daemon account's group {daemon_group.gr_name}")


# Not the runtime lock's name: a layout whose runtime and state directories coincide would have
# the daemon's second lock refuse its first (review of 09f5c0b).
STORE_LOCK_NAME = "worldline-store.lock"
LIVE_MARKER = ".worldline-generation.json"


def acquire_store_lock(state: Path, *, holder: str, create_directory: bool = True) -> int:
    """The store's own lock, kept in its state directory. worldlined takes it before it opens
    anything, and worldline-relocate for its whole run, so neither can touch a store the other
    is using. The daemon's older lock lives in the runtime directory, which systemd removes
    with the unit (lock file included), so a restarted unit locked a new file while another
    process still held the old one; and the daemon wrote its database before taking even that
    lock (review of 796cb02). Returns the descriptor, held until it is closed."""
    import fcntl
    if create_directory:
        try:
            secure_directory(state)
        except PermissionError as exc:
            raise WorldlineError("UNSAFE_STORE", f"the state directory cannot be created or checked: {state}: {exc}") from exc
    path = state / STORE_LOCK_NAME
    try:
        descriptor = os.open(path, os.O_RDWR | os.O_CREAT | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600)
    except OSError as exc:  # a link (ELOOP), a directory (EISDIR), not ours to open
        raise WorldlineError("UNSAFE_STORE", f"the store lock cannot be opened as a file of its own: {path}: {exc}") from exc
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_nlink != 1:
            # Checked before anything is written: a lock hard-linked into another store would
            # otherwise be rewritten there (review of 4490013).
            raise WorldlineError("UNSAFE_STORE",
                                 f"the store lock is not a regular, unlinked-elsewhere file owned by uid {os.getuid()}: {path}")
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise WorldlineError(
                "DAEMON_ALREADY_RUNNING",
                f"{path} is held: a worldlined or worldline-relocate is using this store") from exc
        os.ftruncate(descriptor, 0)
        os.write(descriptor, f"{os.getpid()} {holder}\n".encode("ascii"))
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def store_lock_held_elsewhere(state: Path) -> bool:
    """Whether another process holds the store lock, without creating or changing anything."""
    import fcntl
    try:
        descriptor = os.open(state / STORE_LOCK_NAME, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK)
    except FileNotFoundError:
        return False
    except OSError as exc:
        raise WorldlineError("UNSAFE_STORE", f"the store lock cannot be read: {state / STORE_LOCK_NAME}: {exc}") from exc
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_nlink != 1:
            # The same checks the lock itself makes: a dry run must not pass what the real run
            # refuses (review of 09f5c0b).
            raise WorldlineError("UNSAFE_STORE",
                                 f"the store lock is not a regular, unlinked-elsewhere file owned by uid {os.getuid()}: "
                                 f"{state / STORE_LOCK_NAME}")
        fcntl.flock(descriptor, fcntl.LOCK_SH | fcntl.LOCK_NB)
    except OSError:
        return True
    finally:
        os.close(descriptor)
    return False


def store_directories(env: Mapping[str, str] | None = None) -> tuple[Path, Path]:
    """The store's data and state directories as WorldlinePaths.from_environment spells them,
    without validating client mode: worldlined takes the store lock before it validates, so a
    refused configuration can still close the gate (review of 4490013)."""
    values = os.environ if env is None else env
    home = _absolute(values.get("HOME", str(Path.home())))
    data_home = _absolute(values.get("XDG_DATA_HOME", str(home / ".local/share")))
    state_home = _absolute(values.get("XDG_STATE_HOME", str(home / ".local/state")))
    return data_home / "worldline", state_home / "worldline"


def close_gate_at(data: Path) -> None:
    """Close a data directory to everyone but its owner, whatever mode configured it: 0700 on a
    real directory this account owns. Closing only ever removes reach."""
    try:
        info = data.lstat()
    except FileNotFoundError:
        return
    if stat.S_ISDIR(info.st_mode) and info.st_uid == os.getuid() and stat.S_IMODE(info.st_mode) != 0o700:
        os.chmod(data, 0o700)


def store_lock_intact(state: Path, descriptor: int) -> bool:
    """Whether the lock file at its path is still the one this descriptor holds."""
    try:
        named, held = os.stat(state / STORE_LOCK_NAME, follow_symlinks=False), os.fstat(descriptor)
    except OSError:
        return False
    return (named.st_dev, named.st_ino) == (held.st_dev, held.st_ino)


def _nested(first: Path, second: Path) -> bool:
    """Whether either path contains the other, as spelled or as resolved through symlinks."""
    for a, b in ((first, second), (Path(os.path.realpath(first)), Path(os.path.realpath(second)))):
        if a == b or a in b.parents or b in a.parents:
            return True
    return False


# Content a client can reach must be read-only to it:
# - no other-write bit;
# - a group-write bit only on an entry of the daemon's OWN group. No client may be in that group
#   (from_environment refuses it); any other group (the operator's, kept by a migration that
#   chowned only the owner) may hold a client, so its write bit is a client's write bit.
#   Hosts with umask 002 put that bit on everything a world writes, in the daemon's group;
# - no extended POSIX ACL. Manifests record ACLs and materialization re-applies them, and a
#   `u:<client>:rwx` entry grants write while the mode bits show only its mask;
# - no special bit (a setuid or setgid file there would run as the daemon account for anyone
#   who can reach it).
_CLIENT_SPECIAL_BITS = stat.S_ISUID | stat.S_ISGID | stat.S_ISVTX
_ACL_XATTRS = frozenset(("system.posix_acl_access", "system.posix_acl_default"))


def xattr_risks(path: str | bytes) -> tuple[bool, bool]:
    """(extended ACL, file capability) on an entry, read without following a link.

    Any `system.*acl*` name counts as an ACL (NFSv4, richacl), not only the two POSIX names, and
    a `security.capability` xattr is a file capability: executing such a file grants it, and
    manifests record it like any xattr (review of 796cb02). Only a filesystem without xattr
    support reads as neither; any other error raises instead of reading as none."""
    try:
        names = os.listxattr(path, follow_symlinks=False)
    except OSError as exc:
        if exc.errno in (errno.ENOTSUP, errno.EOPNOTSUPP):
            return False, False
        raise
    acl = any(name in _ACL_XATTRS or (name.startswith("system.") and "acl" in name) for name in names)
    return acl, "security.capability" in names


def has_extended_acl(path: str | bytes) -> bool:
    return xattr_risks(path)[0]


def _unescape_mount_path(field: str) -> str:
    return re.sub(r"\\([0-7]{3})", lambda match: chr(int(match.group(1), 8)), field)


def _host_mount_options(path: str, mountinfo: str = "/proc/1/mountinfo") -> tuple[str, list[str]]:
    """The mount holding `path` in PID 1's mount namespace, and its per-mount options.

    Found by walking the mount tree from the root, following at each path prefix the mounts made
    on the current one, the last one where several are stacked; a longest-prefix match took a
    mount that a later one covered for the mount in use (review of 4490013)."""
    entries: list[tuple[int, int, str, list[str]]] = []
    with open(mountinfo, encoding="utf-8", errors="surrogateescape") as stream:
        for line in stream:
            fields = line.split()
            if len(fields) < 6:
                continue
            entries.append((int(fields[0]), int(fields[1]), _unescape_mount_path(fields[4]), fields[5].split(",")))
    listed = {entry[0] for entry in entries}
    roots = [entry for entry in entries if entry[2] == "/" and (entry[1] not in listed or entry[1] == entry[0])]
    if not roots:
        raise ValueError("the mount table has no root")

    def on_top(current: tuple[int, int, str, list[str]], point: str) -> tuple[int, int, str, list[str]]:
        seen = {current[0]}
        while True:
            # A mount is never its own cover: a root listed as its own parent, and any cycle,
            # would otherwise loop forever on the daemon's event loop (review of 09f5c0b).
            covering = [entry for entry in entries
                        if entry[1] == current[0] and entry[2] == point and entry[0] not in seen]
            if not covering:
                return current
            current = covering[-1]
            seen.add(current[0])

    current = on_top(roots[-1], "/")
    prefix = ""
    for part in [part for part in path.split("/") if part]:
        prefix += "/" + part
        current = on_top(current, prefix)
    return current[2], current[3]


def deployment_facts(data: Path) -> dict[str, dict[str, Any]]:
    """What a client-mode deployment needs from its host that the daemon can observe, each
    `OK`, `MISSING` or `UNKNOWN` (never assumed). Reported by `doctor`; nothing is enforced:
    - fs.protected_hardlinks=1. Without it a client hard-links a PRIME file it can read into a
      directory of its own, and every capture of PRIME refuses EXTERNAL_HARDLINK until the link
      is found (review of ad64cd2);
    - a nosuid store mount, as the host mounts it (PID 1's mount table), since clients reach
      PRIME through the host's mounts. The daemon's own view can differ: systemd mounts
      everything nosuid in a unit with NoNewPrivileges= and a mount namespace, so reading it
      there reported OK over a suid-capable host mount (review of 796cb02);
    - the unit's MemoryMax=, MemorySwapMax= and TasksMax=, which bound repository inspection (it
      runs in the daemon's own cgroup). memory.max does not cover swap.
    RestrictSUIDSGID= on the unit and on the account's user manager cannot be read from here."""
    facts: dict[str, dict[str, Any]] = {}
    try:
        value = Path("/proc/sys/fs/protected_hardlinks").read_text(encoding="ascii").strip()
        facts["protectedHardlinks"] = {"state": "OK" if value == "1" else "MISSING", "value": value}
    except (OSError, ValueError) as exc:
        facts["protectedHardlinks"] = {"state": "UNKNOWN", "reason": str(exc)}
    try:
        # PID 1 must be the host's init for its mount table to be the host's: under PrivatePIDs=
        # or in a container, /proc/1 is this service's own namespace (review of 4490013).
        init = Path("/proc/1/comm").read_text(encoding="utf-8").strip()
        if os.getpid() == 1 or init != "systemd":
            raise ValueError(f"PID 1 here is {init!r}, not the host's systemd")
        point, options = _host_mount_options(os.path.realpath(data))
        facts["storeNosuid"] = {"state": "OK" if "nosuid" in options else "MISSING", "mount": point,
                                "view": "host (PID 1's mount table)"}
    except (OSError, ValueError) as exc:
        facts["storeNosuid"] = {"state": "UNKNOWN", "reason": f"the host's mount table cannot be read here: {exc}"}
    try:
        lines = Path("/proc/self/cgroup").read_text(encoding="utf-8").splitlines()
        unified = next(line[3:] for line in lines if line.startswith("0::"))
        group = Path("/sys/fs/cgroup") / unified.lstrip("/")
    except (OSError, ValueError, StopIteration) as exc:
        group = None
        reason = f"no cgroup v2 membership: {exc}" if str(exc) else "no cgroup v2 membership"
    for name, control in (("memoryMax", "memory.max"), ("memorySwapMax", "memory.swap.max"), ("tasksMax", "pids.max")):
        if group is None:
            facts[name] = {"state": "UNKNOWN", "reason": reason}
            continue
        try:
            value = (group / control).read_text(encoding="ascii").strip()
        except (OSError, ValueError) as exc:
            facts[name] = {"state": "UNKNOWN", "reason": str(exc)}
            continue
        facts[name] = {"state": "MISSING" if value == "max" else "OK", "value": value, "cgroup": str(group)}
    return facts


def client_unsafe(mode: int, gid: int, daemon_gid: int) -> bool:
    return bool(mode & stat.S_IWOTH or mode & _CLIENT_SPECIAL_BITS
                or (mode & stat.S_IWGRP and gid != daemon_gid))


def secure_directory(path: Path, *, create: bool = True, shared_gid: int | None = None,
                     shared_mode: int = 0o750) -> Path:
    """A real directory owned by this uid: 0700, or `shared_mode` with group `shared_gid`."""
    if create:
        try:
            path.mkdir(mode=0o700, parents=True, exist_ok=True)
        except FileExistsError:
            pass  # something that is not a directory: refused by name just below
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
        if gids and gids[0] == os.getgid():
            # Everything the daemon creates carries its primary group, so that group's write bits
            # would be the clients' write bits.
            raise WorldlineError("INVALID_CLIENT_MODE",
                                 "the client group must not be the daemon account's primary group")
        if gids:
            _refuse_clients_in_daemon_group(uids)
            _refuse_client_group_overlap(gids[0])
            spelled = {"HOME": home, "XDG_DATA_HOME": data_home, "XDG_STATE_HOME": state_home,
                       "XDG_CONFIG_HOME": config_home, "XDG_RUNTIME_DIR": runtime_home}
            crooked = sorted(name for name, value in spelled.items()
                             if value.exists() and Path(os.path.realpath(value)) != value)
            if crooked:
                # Masks and gates are applied by path; a spelling through a symlink would put them
                # on the link while the real directory stayed reachable.
                raise WorldlineError("INVALID_CLIENT_MODE",
                                     "in client mode these must be spelled by their real paths: " + ", ".join(crooked))
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
    def store_lock(self) -> Path:
        return self.state / STORE_LOCK_NAME

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

    def assert_client_safe(self, directory: Path | str | bytes) -> None:
        """Client mode: content on the client-searchable path must be the daemon's, and
        read-only to everyone else.

        Manifests record modes and materialization re-applies them, so a candidate chooses the
        modes of the content it stages. A directory there that clients could write would let a
        client write PRIME directly, and the daemon would adopt the write as a new generation
        with no transaction. Refused instead: CLIENT_MODE_UNSAFE_CONTENT names the entries.
        """
        if self.client_gid is None:
            return
        uid = os.getuid()
        daemon_gid = os.getgid()
        root = os.fsencode(directory)
        unsafe: list[str] = []
        unreadable: list[str] = []

        def inspect(path: bytes) -> None:
            info = os.lstat(path)
            if stat.S_ISLNK(info.st_mode):
                return  # a link's own mode is meaningless; its target is inspected where it lies
            try:
                acl, capability = xattr_risks(path)
            except OSError as exc:  # unreadable xattrs are not "none" (review of 796cb02)
                unreadable.append(f"{os.fsdecode(os.path.relpath(path, root))}: xattrs: {exc}")
                return
            if (info.st_uid != uid or client_unsafe(stat.S_IMODE(info.st_mode), info.st_gid, daemon_gid)
                    or acl or capability):
                unsafe.append(f"{stat.S_IMODE(info.st_mode):04o} uid={info.st_uid} gid={info.st_gid}"
                              f"{' acl' if acl else ''}{' file-capability' if capability else ''}"
                              f" {os.fsdecode(os.path.relpath(path, root))}")

        inspect(root)
        for current, subdirectories, files in os.walk(root, onerror=lambda error: unreadable.append(str(error))):
            for name in subdirectories + files:
                inspect(os.path.join(current, name))
        if unsafe or unreadable:
            raise WorldlineError(
                "CLIENT_MODE_UNSAFE_CONTENT",
                "content a client can reach must be owned by the daemon, carry no other-write bit, "
                "no group-write bit outside the daemon's own group, no extended ACL, no file "
                "capability, and no setuid, setgid or sticky bit",
                {"directory": os.fsdecode(root), "count": len(unsafe), "entries": unsafe[:50],
                 "unreadable": unreadable[:20]})

    def close_client_gate(self) -> None:
        """Client mode: withdraw every client's reach into the store. The data directory is the
        root of the client path, so 0700 there closes all of it. Used when reachable content
        turns out unsafe while the daemon runs, and on a start that refuses; the next start
        re-opens only after checking. A data directory that does not exist yet is created closed."""
        if self.client_gid is None:
            return
        close_gate_at(self.data)

    def share_live_chain(self) -> None:
        """Client mode: open the path to the CURRENT PRIME's content to the client group.

        New generations and transactions are created that way; this covers a store that was
        written before client mode (a migrated store) and is otherwise unreadable to clients
        until its next collapse. The content is checked first (assert_client_safe). Only
        existing directories strictly between the store and each root's payload are re-moded;
        a root's own directory keeps the mode its manifest records, and nothing is created.
        """
        if self.client_gid is None:
            return
        store = os.path.realpath(self.data)
        for mapping in sorted(self.live.iterdir()):
            if not mapping.is_symlink():
                if mapping.name == LIVE_MARKER and stat.S_ISREG(mapping.lstat().st_mode):
                    continue
                # A copy that dereferenced links turns a mapping into a real directory, which this
                # check skipped while root_source served it (review of 796cb02).
                raise WorldlineError("LIVE_MAPPING_BROKEN",
                                     f"live holds something other than mapping links: {mapping.name}")
            target = os.path.realpath(mapping)
            payload_areas = (os.path.join(store, "generations") + os.sep, os.path.join(store, "transactions") + os.sep)
            if not target.startswith(payload_areas) or not os.path.isdir(target):
                # The same rule as root_source: a mapping names a generation or transaction payload.
                raise WorldlineError("LIVE_MAPPING_BROKEN", f"live mapping does not resolve to a payload in the store: {mapping.name}")
            self.assert_client_safe(target)
            parts = Path(target).relative_to(store).parts[:-1]
            current = Path(store)
            for part in parts:
                current = current / part
                secure_directory(current, create=False, shared_gid=self.client_gid, shared_mode=0o710)
        # The gate opens last, once everything below it has been checked.
        secure_directory(self.data, create=False, shared_gid=self.client_gid, shared_mode=0o710)

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
        # The link must name the entry `<root key>` in the live directory. The directory is
        # compared resolved, so a HOME reached through a symlink, a doubled or trailing slash, or
        # a relative spelling still routes; a link straight to a payload does not.
        if not os.path.isabs(routed):
            routed = os.path.join(os.path.dirname(raw), routed)
        parent, name = os.path.split(routed.rstrip(b"/"))
        # Compared by kernel identity, resolved in this namespace: every component must exist and
        # be searchable here. A lexical realpath skipped a component it could not see and popped the
        # `..` after it, so a link the daemon cannot follow was reported as routing (review of ad64cd2).
        try:
            parent_identity = os.stat(parent)
            live_identity = os.stat(os.path.dirname(live))
        except OSError as exc:
            raise WorldlineError(
                "LIVE_MAPPING_BROKEN",
                f"managed root does not route through the live mapping: {os.fsdecode(raw)}") from exc
        if (name != os.fsencode(root_key)
                or (parent_identity.st_dev, parent_identity.st_ino) != (live_identity.st_dev, live_identity.st_ino)):
            raise WorldlineError(
                "LIVE_MAPPING_BROKEN",
                f"managed root does not route through the live mapping: {os.fsdecode(raw)}")
        source = os.path.realpath(live)
        store = os.path.realpath(os.fsencode(self.data))
        payload_areas = (store + b"/generations/", store + b"/transactions/")
        if not os.path.islink(live) or not source.startswith(payload_areas) or not os.path.isdir(source):
            # The mapping is a link into a generation or a transaction payload; a real directory
            # there (a copy that dereferenced links) is nothing the daemon published (review of 796cb02).
            raise WorldlineError(
                "LIVE_MAPPING_BROKEN",
                f"live mapping for {root_key} is not a link to a payload in the store")
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
            elif path == self.data and self.client_gid is not None:
                # The gate: created closed, and left as it is (open 0710 or closed 0700) by the
                # many callers of ensure(). Only share_live_chain opens it, after checking what
                # clients would reach; close_client_gate closes it.
                self._client_gate(path)
            elif path in (self.live, self.generations):
                self.prime_directory(path)
            else:
                secure_directory(path)

    def _client_gate(self, path: Path) -> None:
        path.mkdir(mode=0o700, parents=True, exist_ok=True)
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid():
            raise WorldlineError("UNSAFE_STORE", f"store path is not a real directory owned by uid {os.getuid()}: {path}")
        opened = stat.S_IMODE(info.st_mode) == 0o710 and info.st_gid == self.client_gid
        if not opened and stat.S_IMODE(info.st_mode) != 0o700:
            os.chmod(path, 0o700)
