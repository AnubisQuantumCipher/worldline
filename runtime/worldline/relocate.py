"""Relocate a stopped WORLDLINE store to new data and state directories.

A store records absolute paths to itself: world payloads, job event logs, the canonical files of
causal events and receipts, transaction records, prepared mappings and the live mapping's links.
Moving its directories breaks every one of them, and a store under a directory another account
can rename is not a store that account cannot write. `relocate` runs on a COPY already placed at
the new location, with no daemon serving it. It rewrites exactly the persisted LOCATIONS from the
old prefixes to the new ones and proves the result:

- every row of the six location columns lies under the new prefixes;
- the live mapping and every prepared mapping resolve inside the new store, and every retained
  world payload exists there;
- the causal and receipt chains replay through the proved kernel;
- nothing the daemon dereferences still names the old store. Any other mention of an old prefix
  is classified. Content (payload trees, world upper layers), hashed records (causal events,
  receipts, manifests, and each world's evidence column), agent output and the snapshots given
  to agents are kept byte for byte and counted in the report. A mention anywhere else, including
  any other database column, refuses the relocation.

The old copy is never opened for writing. Rolling back is starting the old daemon again.

Run it as the account that will own the store (never root), on a copy that account already owns,
with no daemon serving it: each is checked, and every rewrite is planned and every planning refusal
raised before anything is written. The final verification (chains, mappings, payloads) runs after
the writes; if it refuses, the copy stays rewritten, the old copy is intact, and a rerun is safe. It does not re-point the operator's root links; `worldline doctor`
(rootIntegrity) shows them once the daemon runs.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
import shutil
import sqlite3
import stat
import sys
import tempfile
from typing import Any, Iterator
import uuid

from .canonical import atomic_write_json, canonical_bytes
from .core import Core
from .errors import WorldlineError
from .model import NONTERMINAL_STATES
from .paths import (LIVE_MARKER, STORE_LOCK_NAME, WorldlinePaths, _unescape_mount_path, acquire_store_lock,
                    store_lock_held_elsewhere, store_lock_intact, xattr_risks)

# (table, column) pairs that hold a location in the store. Nothing else in the database may.
LOCATION_COLUMNS = (
    ("worlds", "payload_path"),
    ("worlds", "base_payload_path"),
    ("jobs", "raw_event_path"),
    ("causal_events", "canonical_path"),
    ("transactions", "prepared_path"),
    ("receipts", "canonical_path"),
)
# (table, column) pairs that hold hashed records. A world's evidence is covered by its evidence
# root, which its components and so its content id cover; it records where a check ran (a private
# evaluator's sandbox command line and frozen inputs), and nothing reads a path back out of it (the
# evaluator opens only the paths of the run it is executing). Kept byte for byte, like the hashed
# record files, and counted; rewriting it would change the identity of every world it belongs to.
RECORD_COLUMNS = (("worlds", "evidence"),)
# Rows of the key/value table that hold records of the same kind: a revalidation stores its
# check results (with a private evaluator's boundary and frozen inputs) under
# `validation:<world instance>`, and they are read only for their freshness context and results.
RECORD_META_PREFIXES = ("validation:",)
OPEN_TRANSACTION_STATES = ("PREPARED", "AUTHORIZED")
# A world's instance id and a root key: an agent can make `agent-runtime/work/work` or a check
# named `work` in its own overlay, which the looser rule took for overlayfs's (review of 09f5c0b).
_INSTANCE_ID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
_ROOT_KEY = re.compile(r"[0-9a-f]{64}")
_DATABASE_FILES = frozenset(("worldline.sqlite3", "worldline.sqlite3-wal", "worldline.sqlite3-shm",
                             "worldline.sqlite3-journal"))
ACTIVE_JOB_STATES = ("STARTING", "RUNNING", "FINALIZING")


_VIEW_FILESYSTEMS = ("cifs", "smb3", "9p", "virtiofs", "ceph", "glusterfs", "afs", "davfs")


def _mount_table(path: str = "/proc/self/mountinfo") -> list[dict[str, Any]]:
    entries = []
    with open(path, encoding="utf-8", errors="surrogateescape") as stream:
        for line in stream:
            fields = line.split()
            if "-" not in fields or len(fields) < 7:
                continue
            dash = fields.index("-")
            entries.append({"id": int(fields[0]), "parent": int(fields[1]), "device": fields[2],
                            "root": _unescape_mount_path(fields[3]), "point": _unescape_mount_path(fields[4]),
                            "options": fields[5].split(","), "fstype": fields[dash + 1]})
    return entries


def _holding_mount(path: str, entries: list[dict[str, Any]]) -> dict[str, Any]:
    """The mount in use for `path`, walking the tree from the root as the kernel resolves it."""
    listed = {entry["id"] for entry in entries}
    roots = [entry for entry in entries if entry["point"] == "/" and (entry["parent"] not in listed or entry["parent"] == entry["id"])]
    if not roots:
        raise _refuse("the mount table has no root")

    def on_top(current: dict[str, Any], point: str) -> dict[str, Any]:
        seen = {current["id"]}
        while True:
            covering = [entry for entry in entries
                        if entry["parent"] == current["id"] and entry["point"] == point and entry["id"] not in seen]
            if not covering:
                return current
            current = covering[-1]
            seen.add(current["id"])

    current = on_top(roots[-1], "/")
    prefix = ""
    for part in [part for part in path.split("/") if part]:
        prefix += "/" + part
        current = on_top(current, prefix)
    return current


def _mount_source(path: str, entries: list[dict[str, Any]]) -> tuple[dict[str, Any], str]:
    """The mount holding `path` and the path's location inside that mount's filesystem."""
    mount = _holding_mount(path, entries)
    inside = os.path.relpath(path, mount["point"])
    return mount, os.path.normpath(os.path.join(mount["root"], "" if inside == "." else inside))


def _fdinfo_identity(path: str) -> tuple[int, int] | None:
    """(mount id, inode) of an open descriptor, from its fdinfo; None when unreadable."""
    try:
        with open(path, encoding="ascii", errors="replace") as stream:
            fields = dict(line.split(":", 1) for line in stream if ":" in line)
        return int(fields["mnt_id"]), int(fields["ino"])
    except (OSError, KeyError, ValueError):
        return None


def _refuse(message: str, details: dict[str, Any] | None = None) -> WorldlineError:
    return WorldlineError("RELOCATION_REFUSED", message, details or {})


class Relocation:
    def __init__(self, *, old_data: Path, old_state: Path, new_data: Path, new_state: Path,
                 core: Core | None = None) -> None:
        self.core = core or Core.shared()
        for name, value in (("old data", old_data), ("old state", old_state),
                            ("new data", new_data), ("new state", new_state)):
            if not value.is_absolute() or os.path.normpath(value) != str(value):
                raise _refuse(f"{name} directory must be an absolute, normalized path: {value}")
        for name, value in (("new data", new_data), ("new state", new_state)):
            if value.is_symlink() or not value.is_dir():
                raise _refuse(f"{name} directory is not a real directory: {value}")
        self.old = (os.fsencode(old_data), os.fsencode(old_state))
        self.new = (os.fsencode(new_data), os.fsencode(new_state))
        prefixes = [*self.old, *self.new]
        for index, first in enumerate(prefixes):
            for second in prefixes[index + 1:]:
                if first in second or second in first:
                    # Mentions are found by substring: one prefix inside another would blur them.
                    raise _refuse("old and new directories must not contain one another's names",
                                  {"first": os.fsdecode(first), "second": os.fsdecode(second)})
        self.new_data, self.new_state = new_data, new_state
        # The copy must be a copy: spelled by its real path (a symlinked parent could lead back
        # into the old store), apart from the old store, and not the same directory under another
        # name (a bind mount). Each of these once had the OLD store rewritten in place (review of
        # ad64cd2). When the old store is not visible to this account the comparison is skipped;
        # ownership then separates them (the copy must be this account's, the old store is not).
        for name, value in (("new data", new_data), ("new state", new_state)):
            if os.path.realpath(value) != str(value):
                raise _refuse(f"{name} directory must be spelled by its real path: {value} is {os.path.realpath(value)}")
        for old_value, new_value in ((old_data, new_data), (old_state, new_state), (old_data, new_state), (old_state, new_data)):
            old_real, new_real = os.path.realpath(old_value), os.path.realpath(new_value)
            if old_real == new_real or new_real.startswith(old_real + os.sep) or old_real.startswith(new_real + os.sep):
                raise _refuse("the copy and the old store overlap", {"old": old_real, "new": new_real})
            try:
                old_info, new_info = os.stat(old_value), os.stat(new_value)
            except OSError:
                continue
            if (old_info.st_dev, old_info.st_ino) == (new_info.st_dev, new_info.st_ino):
                raise _refuse("the copy is the old store under another name (a bind mount?)",
                              {"old": str(old_value), "new": str(new_value)})
        self.old_real = tuple(os.fsencode(os.path.realpath(value)) for value in (old_data, old_state))
        self.database = new_state / "worldline.sqlite3"
        if self.database.is_symlink() or not self.database.is_file():
            raise _refuse(f"no store database file at {self.database}")
        # The database is the only file rewritten in place. A hard-linked or symlinked copy could
        # share it with the old store (review of ff201cd): the copy's database, and its -wal and
        # -shm, must each be a file of its own.
        for suffix in ("", "-wal", "-shm"):
            candidate = Path(str(self.database) + suffix)
            if candidate.exists() and not candidate.is_symlink() and not stat.S_ISREG(candidate.lstat().st_mode):
                # A FIFO there hung the holder check (review of c7d89f1).
                raise _refuse(f"{candidate.name} in the copy is not a regular file")
            if candidate.is_symlink() or (candidate.exists() and candidate.stat().st_nlink != 1):
                raise _refuse(f"{candidate.name} in the copy is linked elsewhere; copy it, do not link it")
            try:
                old_info = os.stat(os.path.join(old_state, "worldline.sqlite3" + suffix))
            except OSError:
                continue
            if candidate.exists():
                new_info = candidate.stat()
                if (old_info.st_dev, old_info.st_ino) == (new_info.st_dev, new_info.st_ino):
                    raise _refuse(f"{candidate.name} in the copy is the old store's own file")
        # The copy's store lock is written by a real run: it must not be the old store's own lock
        # file, through a hard link or a file bind mount (review of 09f5c0b).
        lock = new_state / STORE_LOCK_NAME
        try:
            old_lock, new_lock = os.stat(os.path.join(old_state, STORE_LOCK_NAME)), os.lstat(lock)
        except OSError:
            pass
        else:
            if (old_lock.st_dev, old_lock.st_ino) == (new_lock.st_dev, new_lock.st_ino):
                raise _refuse(f"{STORE_LOCK_NAME} in the copy is the old store's own lock file")

    # -- mapping one location

    def _mentions(self, value: bytes) -> bool:
        return any(prefix in value for prefix in self.old)

    def _file_mentions(self, path: str) -> bool | None:
        """Whether a regular file mentions an old prefix, streamed so a large payload file is never
        held whole; None for anything that is not a regular file. Sockets, FIFOs and devices hold no
        bytes to rewrite, and opening one can fail or block (a dead world's runtime keeps its
        sockets: relocating production's store once crashed on one)."""
        if not stat.S_ISREG(os.lstat(path).st_mode):
            return None  # checked before opening: open() on a socket fails outright (ENXIO)
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK)
        try:
            if not stat.S_ISREG(os.fstat(descriptor).st_mode):
                return None
            overlap = max(len(prefix) for prefix in self.old) - 1
            tail = b""
            while True:
                chunk = os.read(descriptor, 1 << 20)
                if not chunk:
                    return False
                window = tail + chunk
                if self._mentions(window):
                    return True
                tail = window[-overlap:] if overlap > 0 else b""
        finally:
            os.close(descriptor)

    def _map(self, value: bytes, where: str) -> bytes:
        """The new location for a stored one. Already-new values are accepted, so a run that
        stopped part way through can be repeated."""
        for old, new in zip(self.old, self.new):
            if value == old or value.startswith(old + b"/"):
                mapped = new + value[len(old):]
                if self._mentions(mapped):
                    raise _refuse(f"{where}: a location names the old store twice", {"value": os.fsdecode(value)})
                return mapped
        if any(value == new or value.startswith(new + b"/") for new in self.new):
            return value
        raise _refuse(f"{where}: a stored location is outside the old and new store",
                      {"value": os.fsdecode(value)})

    # -- the three kinds of persisted location

    def _plan_database(self, connection: sqlite3.Connection) -> list[tuple[str, str, int, str]]:
        """Every location row's new value, computed (and refused) before anything is written."""
        plan: list[tuple[str, str, int, str]] = []
        for table, column in LOCATION_COLUMNS:
            for rowid, value in connection.execute(f"SELECT rowid, {column} FROM {table}").fetchall():
                if not isinstance(value, str):
                    raise _refuse(f"{table}.{column} holds a non-text location", {"rowid": rowid})
                mapped = os.fsdecode(self._map(os.fsencode(value), f"{table}.{column}"))
                self._require_inside_new(mapped, f"{table}.{column}")
                if mapped != value:
                    plan.append((table, column, rowid, mapped))
        return plan

    def _inside_new(self, path: str | bytes) -> bool:
        real = os.path.realpath(os.fsencode(path))
        return any(real == base or real.startswith(base + b"/")
                   for base in (os.path.realpath(os.fsencode(self.new_data)), os.path.realpath(os.fsencode(self.new_state))))

    def _require_inside_new(self, location: str, where: str) -> None:
        """A recorded location that exists in the copy must resolve inside the new store. Checked
        while planning, before anything is written: a link inside the copy could otherwise lead a
        rewritten location back into the old store (review of ad64cd2)."""
        if os.path.lexists(location) and not self._inside_new(location):
            raise _refuse(f"{where}: a recorded location resolves outside the new store",
                          {"location": location, "resolves": os.path.realpath(location)})

    def _rewrite_json_strings(self, value: Any, where: str) -> Any:
        if isinstance(value, dict):
            return {key: self._rewrite_json_strings(item, where) for key, item in value.items()}
        if isinstance(value, list):
            return [self._rewrite_json_strings(item, where) for item in value]
        if isinstance(value, str) and self._mentions(os.fsencode(value)):
            return os.fsdecode(self._map(os.fsencode(value), where))
        return value

    def _plan_transaction_records(self) -> list[tuple[Path, Any, int]]:
        plan: list[tuple[Path, Any, int]] = []
        directory = self.new_state / "transactions"
        if not directory.is_dir():
            return plan
        for path in sorted(directory.glob("*.json")):
            info = path.lstat()
            if not stat.S_ISREG(info.st_mode):
                raise _refuse(f"transaction record is not a regular file: {path.name}")
            raw = path.read_bytes()
            if not self._mentions(raw):
                continue
            value = json.loads(raw)
            if canonical_bytes(value) != raw:
                # Rewriting re-serializes. Only a canonical record re-serializes to itself.
                raise _refuse(f"transaction record is not canonical JSON: {path.name}")
            rewritten = self._rewrite_json_strings(value, f"transactions/{path.name}")
            if self._mentions(canonical_bytes(rewritten)):
                raise _refuse(f"transaction record names the old store where it cannot be rewritten: {path.name}")
            plan.append((path, rewritten, path.stat().st_mode & 0o777))
        return plan

    def _mapping_links(self) -> Iterator[Path]:
        live = self.new_data / "live"
        if live.is_dir():
            yield from (item for item in sorted(live.iterdir()) if item.is_symlink())
        transactions = self.new_data / "transactions"
        if transactions.is_dir():
            for mapping in sorted(transactions.glob("*/mapping")):
                if mapping.is_dir() and not mapping.is_symlink():
                    yield from (item for item in sorted(mapping.iterdir()) if item.is_symlink())

    def _plan_mapping_links(self) -> list[tuple[Path, bytes]]:
        plan: list[tuple[Path, bytes]] = []
        for link in self._mapping_links():
            target = os.readlink(os.fsencode(link))
            mapped = self._map(target, f"mapping link {link.relative_to(self.new_data)}")
            if mapped != target:
                plan.append((link, mapped))
        return plan

    def _holders(self) -> list[int]:
        """Processes this uid can see that hold the copy's database open, matched by device and
        inode: each descriptor's mount id and inode come from /proc/<pid>/fdinfo, and the mount id
        is mapped to its device through that process's own mount table, since mount ids differ
        between mount namespaces (review of c7d89f1). Nothing is stat'ed through another
        process's descriptor, which a hung FUSE mount would block (review of 09f5c0b), except on
        a kernel whose fdinfo has no inode. A daemon serving the copy runs as the same account, so
        it is visible; `BEGIN EXCLUSIVE` alone does not detect an idle WAL connection."""
        identities: set[tuple[str, int]] = set()
        for suffix in ("", "-wal", "-shm"):
            path = str(self.database) + suffix
            try:
                info = os.lstat(path)
            except FileNotFoundError:
                continue
            if not stat.S_ISREG(info.st_mode):
                raise _refuse(f"{Path(path).name} in the copy is not a regular file")
            identities.add((f"{os.major(info.st_dev)}:{os.minor(info.st_dev)}", info.st_ino))
            descriptor = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK)
            try:
                if _fdinfo_identity(f"/proc/self/fdinfo/{descriptor}") is None:
                    return self._holders_by_stat()  # a kernel whose fdinfo has no inode
            finally:
                os.close(descriptor)
        holders: set[int] = set()
        for process in Path("/proc").iterdir():
            if not process.name.isdigit() or int(process.name) == os.getpid():
                continue
            try:
                devices: dict[int, str] | None = None
                for info in (process / "fdinfo").iterdir():
                    identity = _fdinfo_identity(str(info))
                    if identity is None:
                        continue
                    if devices is None:
                        devices = {entry["id"]: entry["device"] for entry in _mount_table(str(process / "mountinfo"))}
                    if (devices.get(identity[0]), identity[1]) in identities:
                        holders.add(int(process.name))
            except OSError:
                continue  # another uid's process, or gone
        return sorted(holders)

    def _holders_by_stat(self) -> list[int]:
        identities = set()
        for suffix in ("", "-wal", "-shm"):
            try:
                info = os.stat(str(self.database) + suffix)
            except FileNotFoundError:
                continue
            identities.add((info.st_dev, info.st_ino))
        holders: set[int] = set()
        for process in Path("/proc").iterdir():
            if not process.name.isdigit() or int(process.name) == os.getpid():
                continue
            try:
                for descriptor in (process / "fd").iterdir():
                    try:
                        info = os.stat(descriptor)
                    except OSError:
                        continue
                    if (info.st_dev, info.st_ino) in identities:
                        holders.add(int(process.name))
            except OSError:
                continue
        return sorted(holders)

    @staticmethod
    def _overlay_work_directory(base: str, relative: tuple[str, ...]) -> bool:
        """overlayfs makes `<workdir>/work` 0000; it holds only transient kernel state. Only the
        layout the daemon makes, `overlays/<world>/<root key>/work/work`, qualifies: a 0000
        `work/work` anywhere else (inside PRIME's content, say) is refused (review of 4490013)."""
        return (base == "data" and len(relative) == 5 and relative[0] == "overlays"
                and _INSTANCE_ID.fullmatch(relative[1]) is not None and _ROOT_KEY.fullmatch(relative[2]) is not None
                and relative[3] == "work" and relative[4] == "work")

    def _mounts_inside(self) -> list[str]:
        """Mount points strictly inside the copy, from the mount table. A bind mount on the same
        filesystem has the same device number, so comparing devices missed it and the relocation
        rewrote the old store through it (review of 4490013)."""
        roots = [(base, os.path.realpath(root)) for base, root in (("data", self.new_data), ("state", self.new_state))]
        found: list[str] = []
        with open("/proc/self/mountinfo", encoding="utf-8", errors="surrogateescape") as stream:
            for line in stream:
                fields = line.split()
                if len(fields) < 5:
                    continue
                point = _unescape_mount_path(fields[4])
                for base, root in roots:
                    if point.startswith(root + os.sep):
                        found.append(f"{base}/{os.path.relpath(point, root)}")
        return sorted(set(found))

    def _walk_copy(self) -> dict[str, Any]:
        """Every entry of the copy, each once:
        - entries not owned by the account doing the relocation (it will own the store): an
          incomplete chown after a root copy leaves content the daemon cannot vouch for;
        - mount points inside the copy: a directory mounted there (a bind of the old store's
          `live`, say) would have the relocation rewrite the old store (review of 796cb02);
        - regular files with links outside the copy (`cp -al`, `rsync --link-dest`): writes
          through the new store would change the old one (review of 796cb02);
        - directories the account cannot read. overlayfs work directories are 0000 by design
          and hold nothing the daemon reads; any other is refused, since what it holds cannot
          be checked (review of 796cb02)."""
        uid = os.geteuid()
        foreign: list[str] = []
        foreign_count = 0
        mounts: list[str] = []
        unreadable: list[str] = []
        work_directories = 0
        inodes: dict[tuple[int, int], list[Any]] = {}
        for base, root in (("data", self.new_data), ("state", self.new_state)):
            root_device = os.lstat(root).st_dev
            for directory, subdirectories, files in os.walk(root):
                entries = [os.path.join(directory, entry) for entry in subdirectories + files]
                for name in ([directory] if directory == str(root) else []) + entries:
                    info = os.lstat(name)
                    relative = os.path.relpath(name, root)
                    if info.st_uid != uid:
                        foreign_count += 1
                        if len(foreign) < 20:
                            foreign.append(f"uid={info.st_uid} {base}/{relative}")
                    if info.st_dev != root_device:
                        mounts.append(f"{base}/{relative}")
                    if stat.S_ISREG(info.st_mode) and info.st_nlink > 1:
                        seen = inodes.setdefault((info.st_dev, info.st_ino), [info.st_nlink, 0, f"{base}/{relative}"])
                        seen[1] += 1
                readable = []
                for entry in subdirectories:
                    path = os.path.join(directory, entry)
                    if os.path.islink(path) or os.lstat(path).st_dev != root_device:
                        continue  # a link is not descended; a mount point is already refused
                    if os.access(path, os.R_OK | os.X_OK):
                        readable.append(entry)
                    elif self._overlay_work_directory(base, tuple(Path(os.path.relpath(path, root)).parts)):
                        work_directories += 1
                    else:
                        unreadable.append(f"{base}/{os.path.relpath(path, root)}")
                subdirectories[:] = readable
        linked_outside = [where for links, found, where in inodes.values() if found < links]
        mounts = sorted(set(mounts) | set(self._mounts_inside()))
        return {
            "foreignOwned": {"count": foreign_count, "sample": foreign,
                             "overlayWorkDirectoriesNotDescended": work_directories},
            "mountsInsideCopy": mounts[:50],
            "linkedOutsideCopy": {"count": len(linked_outside), "sample": sorted(linked_outside)[:20]},
            "unreadableDirectories": unreadable[:50],
        }

    def _live_unsafe_for_clients(self) -> tuple[int, list[str]]:
        """PRIME content a client-mode daemon would refuse at start: other-write, group-write on
        an entry outside the account's own group (a migration that chowned only the owner keeps
        the operator's group, and the operator is a client), an extended ACL, a file capability,
        a setuid, setgid or sticky bit, an unreadable directory, or anything in `live` other than
        mapping links. Reported so a migration learns it before starting the daemon.

        Read in the COPY: until the relocation rewrites them, the copy's live links still name
        the old store, and following them reported on the old store's content instead (review of
        796cb02). Each link's target is mapped onto the new prefix first."""
        flags = stat.S_IWOTH | stat.S_ISUID | stat.S_ISGID | stat.S_ISVTX
        own_group = os.getegid()
        count = 0
        sample: list[str] = []

        def note(line: str) -> None:
            nonlocal count
            count += 1
            if len(sample) < 20:
                sample.append(line)

        live = self.new_data / "live"
        for link in (sorted(live.iterdir()) if live.is_dir() else []):
            if not link.is_symlink():
                if not (link.name == LIVE_MARKER and link.is_file()):
                    note(f"live/{link.name}: not a mapping link")
                continue
            raw_target = os.readlink(os.fsencode(link))
            if not os.path.isabs(raw_target):
                raw_target = os.path.join(os.fsencode(live), raw_target)
            try:
                target = os.fsdecode(self._map(os.path.normpath(raw_target), f"live/{link.name}"))
            except WorldlineError:
                note(f"live/{link.name}: names neither the old nor the new store")
                continue
            if not os.path.isdir(target):
                note(f"live/{link.name}: its content is missing from the copy")
                continue
            for directory, subdirectories, files in os.walk(
                    target, onerror=lambda error: note(f"{link.name[:12]}: unreadable: {error.filename}")):
                for name in (directory, *[os.path.join(directory, entry) for entry in subdirectories + files]):
                    info = os.lstat(name)
                    if stat.S_ISLNK(info.st_mode):
                        continue
                    mode = stat.S_IMODE(info.st_mode)
                    try:
                        acl, capability = xattr_risks(name)
                    except OSError:
                        acl, capability = True, False  # unreadable xattrs are not "none"
                    if (mode & flags or (mode & stat.S_IWGRP and info.st_gid != own_group)
                            or acl or capability):
                        note(f"{mode:04o}{' acl' if acl else ''}{' file-capability' if capability else ''}"
                             f" {link.name[:12]}/{os.path.relpath(name, target)}")
        return count, sample

    # -- classification of every remaining mention

    def _classify(self, relative: tuple[str, ...], base: str, *, link: bool) -> str | None:
        """What a mention of an old prefix is, or None if it may not exist at all.

        "location" is what the relocation rewrites; after it, a location that still mentions the
        old store is refused. Every other class is kept byte for byte.
        """
        if base == "state":
            if len(relative) == 2 and relative[0] == "transactions" and relative[1].endswith(".json") and not link:
                return "location"
            if relative[:1] == ("install-backups",):
                return "install backup"  # the single-account installer's own rollback copies
            if relative[:1] in (("events",), ("receipts",)):
                return "hashed record"
            if relative[:1] == ("logs",):
                return "agent output"
            return None
        head = relative[:1]
        if link and (
            (len(relative) == 2 and head == ("live",))
            or (len(relative) == 4 and head == ("transactions",) and relative[2] == "mapping")
        ):
            return "location"
        if head in (("generations",), ("transactions",), ("worlds",)):
            if not link and "manifests" in relative[1:3]:
                return "hashed record"
            if len(relative) > 3 and relative[2] == "payload":
                return "content"
            return None
        if head == ("overlays",):
            if len(relative) > 2 and relative[2] == "agent-runtime":
                return "agent snapshot"
            return "content"
        return None

    def _scan(self) -> tuple[dict[str, int], list[str]]:
        found: dict[str, int] = {}
        refused: list[str] = []
        for base, root in (("data", self.new_data), ("state", self.new_state)):
            for directory, subdirectories, files in os.walk(root):
                directory_links = [name for name in subdirectories if os.path.islink(os.path.join(directory, name))]
                # Overlay work directories are 000 by design; they hold content, never a location.
                subdirectories[:] = [name for name in subdirectories
                                     if name not in directory_links
                                     and os.access(os.path.join(directory, name), os.R_OK | os.X_OK)]
                for name in files + directory_links:  # os.walk lists links to files among files
                    path = os.path.join(directory, name)
                    relative = tuple(Path(path).relative_to(root).parts)
                    if (base == "state" and len(relative) == 1 and relative[0] in _DATABASE_FILES
                            and stat.S_ISREG(os.lstat(path).st_mode)):
                        continue  # read through SQL, not as bytes; a link by that name is checked below
                    link = os.path.islink(path)
                    if link:
                        problem = self._link_problem(relative, base, path)
                        if problem:
                            refused.append(f"{base}/{'/'.join(relative)} ({problem})")
                            continue
                    try:
                        if link:
                            mentioned = self._mentions(os.readlink(os.fsencode(path)))
                        else:
                            mentioned = self._file_mentions(path)
                            if mentioned is None:
                                continue  # not a regular file: nothing in it can name a location
                    except PermissionError:
                        refused.append(f"{base}/{'/'.join(relative)} (unreadable)")
                        continue
                    if not mentioned:
                        continue
                    kind = self._classify(relative, base, link=link)
                    if kind is None:
                        refused.append(f"{base}/{'/'.join(relative)}")
                    else:
                        found[kind] = found.get(kind, 0) + 1
        return found, refused

    def _link_problem(self, relative: tuple[str, ...], base: str, path: str) -> str | None:
        """Why a symlink in the copy may not stay, or None. The daemon itself makes only the live
        and prepared mapping links; content may hold links of its own: a payload below its root,
        and anything inside a world's overlay (its upper layer, the agent's runtime snapshot, a
        check's frozen inputs). A link anywhere else, or any link resolving into the old store,
        would have the relocated daemon read, and prune delete, inside the old copy."""
        location = self._classify(relative, base, link=True) == "location"
        real = os.path.realpath(os.fsencode(path))
        into_old = any(real == old or real.startswith(old + b"/") for old in self.old_real)
        if location:
            return None  # rewritten; a mapping link must then resolve inside the new store (verify)
        if into_old:
            return "resolves into the old store"
        head = relative[:1]
        content = ((head in (("generations",), ("transactions",), ("worlds",)) and len(relative) > 4
                    and relative[2] == "payload")
                   or (head == ("overlays",) and len(relative) > 3))
        if base == "data" and content:
            return None
        return "a link where the daemon makes none"

    def _scan_database(self, connection: sqlite3.Connection, *, skip_locations: bool,
                       records: bool = False) -> dict[str, int]:
        """Rows per column that mention an old prefix: the record columns and record rows when
        `records`, else everything else (location columns omitted when asked)."""
        found: dict[str, int] = {}
        tables = [row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        for table in tables:
            for column in [row[1] for row in connection.execute(f"PRAGMA table_info({table})")]:
                if skip_locations and (table, column) in LOCATION_COLUMNS:
                    continue
                if (table, column) == ("meta", "value"):
                    rows = ((str(key).startswith(RECORD_META_PREFIXES), value)
                            for key, value in connection.execute("SELECT key, value FROM meta"))
                    label = "meta.value (validation:*)" if records else "meta.value"
                else:
                    is_record = (table, column) in RECORD_COLUMNS
                    rows = ((is_record, value) for (value,) in connection.execute(f"SELECT {column} FROM {table}"))
                    label = f"{table}.{column}"
                count = 0
                for is_record, value in rows:
                    if is_record != records or value is None:
                        continue
                    raw = value if isinstance(value, bytes) else str(value).encode("utf-8", "surrogateescape")
                    count += self._mentions(raw)
                if count:
                    found[label] = count
        return found

    # -- preconditions and the whole operation

    def _quiescent(self, connection: sqlite3.Connection) -> None:
        states = tuple(state.value for state in NONTERMINAL_STATES)
        worlds = connection.execute(
            f"SELECT alias FROM worlds WHERE state IN ({','.join('?' * len(states))})", states).fetchall()
        transactions = connection.execute(
            f"SELECT transaction_id FROM transactions WHERE state IN ({','.join('?' * len(OPEN_TRANSACTION_STATES))})",
            OPEN_TRANSACTION_STATES).fetchall()
        jobs = connection.execute(
            f"SELECT job_id FROM jobs WHERE state IN ({','.join('?' * len(ACTIVE_JOB_STATES))})",
            ACTIVE_JOB_STATES).fetchall()
        if worlds or transactions or jobs:
            raise _refuse("the store is not quiescent: finish or cancel every world, job and open transaction first",
                          {"worlds": [row[0] for row in worlds], "transactions": [row[0] for row in transactions],
                           "jobs": [row[0] for row in jobs]})

    def run(self, *, dry_run: bool = False) -> dict[str, Any]:
        """Plan, and unless `dry_run`, rewrite and verify. The copy's own store lock is held for the
        whole real run, so no worldlined can start on the copy meanwhile (it takes the same lock
        before it opens anything); a dry run, which writes nothing, only checks it is free."""
        if os.geteuid() == 0:
            raise _refuse("run as the account that will own the store, not as root")
        if dry_run:
            try:
                held = store_lock_held_elsewhere(self.new_state)
            except WorldlineError as exc:
                raise _refuse(exc.message) from exc
            if held:
                raise _refuse("the copy's store lock is held: a daemon is using the copy; stop it first")
            self._refuse_mounted_views()
            return self._run(dry_run=True, lock=None)
        mounts = self._mounts_inside()
        if mounts:
            # Before the lock is written: a file bind of the old store's lock would otherwise be
            # rewritten first (review of 09f5c0b).
            raise _refuse("a mount inside the copy would have the relocation write through it", {"mounts": mounts[:50]})
        # Both view checks before the lock is written or the database opened: through a view,
        # those land in the old store (review of c7d89f1).
        self._refuse_mounted_views()
        self._refuse_views_of_the_old_store()
        try:
            lock = acquire_store_lock(self.new_state, holder="worldline-relocate", create_directory=False)
        except WorldlineError as exc:
            if exc.code == "DAEMON_ALREADY_RUNNING":
                raise _refuse("the copy's store lock is held: a daemon is using the copy; stop it first") from exc
            raise _refuse(exc.message) from exc
        try:
            return self._run(dry_run=False, lock=lock)
        finally:
            os.close(lock)

    def _refuse_mounted_views(self) -> None:
        """Whether a copy root is the old store seen through a mount, judged from the mount table
        alone, so it holds when the relocating account cannot see the old store (the dedicated-
        account migration): the copy's filesystem location must not overlap the old store's on the
        same device, and a copy root on FUSE, a network filesystem or an idmapped mount is refused,
        since those can present anything with any owner (review of c7d89f1)."""
        entries = _mount_table()
        pairs = [(("data", self.new_data), self.old[0]), (("state", self.new_state), self.old[1]),
                 (("data", self.new_data), self.old[1]), (("state", self.new_state), self.old[0])]
        for (base, new_root), old_root in pairs:
            mount, source = _mount_source(os.path.realpath(new_root), entries)
            if mount["fstype"].startswith(("fuse", "nfs")) or mount["fstype"] in _VIEW_FILESYSTEMS:
                raise _refuse(f"the copy's {base} directory is on {mount['fstype']}, which can show another store as this one",
                              {"mount": mount["point"]})
            if "idmapped" in mount["options"]:
                raise _refuse(f"the copy's {base} directory is on an idmapped mount", {"mount": mount["point"]})
            old_mount, old_source = _mount_source(os.path.normpath(os.fsdecode(old_root)), entries)
            if mount["device"] == old_mount["device"] and (
                    source == old_source or source.startswith(old_source.rstrip("/") + "/")
                    or old_source.startswith(source.rstrip("/") + "/")):
                raise _refuse("the copy is the old store seen through a mount",
                              {"copy": str(new_root), "old": os.fsdecode(old_root), "mount": mount["point"]})

    def _refuse_views_of_the_old_store(self) -> None:
        """A FUSE or network view of the old store at the copy's path has a device of its own, so
        the identity checks pass it: a file made in each copy root must not appear in the old
        store (review of 09f5c0b). When the old store is not visible to this account, ownership
        separates them instead."""
        token = f".worldline-relocate-canary-{uuid.uuid4().hex}"
        for new_root, old_root in ((self.new_data, self.old[0]), (self.new_state, self.old[1])):
            canary = new_root / token
            descriptor = os.open(canary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
            os.close(descriptor)
            try:
                if os.path.lexists(os.path.join(os.fsdecode(old_root), token)):
                    raise _refuse("the copy is the old store seen through another filesystem",
                                  {"copy": str(new_root), "old": os.fsdecode(old_root)})
            finally:
                canary.unlink()

    def _lock_still_held(self, lock: int | None) -> None:
        if lock is not None and not store_lock_intact(self.new_state, lock):
            raise _refuse("the copy's store lock file was replaced during the relocation; rerun it")

    def _run(self, *, dry_run: bool, lock: int | None) -> dict[str, Any]:
        for directory in (self.new_data, self.new_state):
            if directory.stat().st_uid != os.geteuid():
                raise _refuse(f"{directory} is not owned by the account running the relocation")
        holders = self._holders()
        if holders:
            raise _refuse("the copy's database is open in another process; stop its daemon first",
                          {"pids": holders})
        scratch: str | None = None
        database = self.database
        if dry_run:
            # Opening a database can checkpoint its WAL and create or delete -wal/-shm. A dry run
            # plans against a private copy, so the copy under relocation is not touched at all.
            scratch = tempfile.mkdtemp(prefix="worldline-relocate-plan-")
            for suffix in ("", "-wal", "-shm"):
                source = str(self.database) + suffix
                if os.path.exists(source):
                    shutil.copy2(source, os.path.join(scratch, "worldline.sqlite3" + suffix))
            database = Path(scratch) / "worldline.sqlite3"
        connection = sqlite3.connect(database, isolation_level=None)
        try:
            # Everything is planned, and every planning refusal raised, before anything is written.
            connection.execute("BEGIN EXCLUSIVE")
            self._quiescent(connection)
            database_plan = self._plan_database(connection)
            records_plan = self._plan_transaction_records()
            links_plan = self._plan_mapping_links()
            stray_columns = self._scan_database(connection, skip_locations=True)
            record_columns = self._scan_database(connection, skip_locations=True, records=True)
            found, refused = self._scan()
            walk = self._walk_copy()
            unsafe, unsafe_sample = self._live_unsafe_for_clients()
            report = {
                "locationRows": {f"{table}.{column}": sum(1 for row in database_plan if row[:2] == (table, column))
                                 for table, column in LOCATION_COLUMNS},
                "transactionRecords": len(records_plan), "mappingLinks": len(links_plan),
                "mentions": found, "refusedFiles": refused[:200], "refusedDatabaseColumns": stray_columns,
                "recordColumnsKept": record_columns,
                **walk,
                "liveContentUnsafeForClients": {"count": unsafe, "sample": unsafe_sample},
            }
            if dry_run:
                connection.execute("ROLLBACK")
                connection.close()
                return {"state": "DRY_RUN", **report}
            if (refused or stray_columns or walk["foreignOwned"]["count"] or walk["mountsInsideCopy"]
                    or walk["linkedOutsideCopy"]["count"] or walk["unreadableDirectories"]):
                raise _refuse("the copy names the old store where it cannot be rewritten, holds entries "
                              "its account does not own, holds a mount, a file linked outside it or a "
                              "directory it cannot read", report)
            self._lock_still_held(lock)
            for table, column, rowid, mapped in database_plan:
                connection.execute(f"UPDATE {table} SET {column}=? WHERE rowid=?", (mapped, rowid))
            connection.execute("COMMIT")
        except BaseException:
            if connection.in_transaction:
                connection.execute("ROLLBACK")
            connection.close()
            raise
        finally:
            if scratch is not None:
                shutil.rmtree(scratch, ignore_errors=True)
        # Idempotent from here: a rerun accepts values that are already new.
        for path, value, mode in records_plan:
            atomic_write_json(path, value, mode=mode)
        for link, mapped in links_plan:
            for stale in link.parent.glob(f".{link.name}.relocate*"):
                if stale.is_symlink():
                    stale.unlink()  # left by an interrupted run
            temporary = link.with_name(f".{link.name}.relocate-{uuid.uuid4().hex}")
            os.symlink(mapped, os.fsencode(temporary))
            os.replace(temporary, link)
        try:
            database = self._scan_database(connection, skip_locations=False)
            connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        finally:
            connection.close()
        found, refused = self._scan()
        if found.get("location"):
            refused.append(f"{found.pop('location')} location file(s) or link(s) still name the old store")
        if database or refused:
            raise _refuse("the old store is still named where the daemon reads it",
                          {"databaseColumns": database, "files": refused[:200]})
        verification = self.verify()
        self._lock_still_held(lock)
        return {"state": "RELOCATED",
                "rewritten": {"databaseRows": report["locationRows"], "transactionRecords": len(records_plan),
                              "mappingLinks": len(links_plan)},
                "mentionsKept": found, "recordColumnsKept": report["recordColumnsKept"],
                "liveContentUnsafeForClients": dict(zip(("count", "sample"), self._live_unsafe_for_clients())),
                "verification": verification}

    def verify(self) -> dict[str, Any]:
        """The relocated store, read as the daemon will read it. Opening it as the daemon does
        also sets its directories' modes and would migrate an older schema."""
        from .store import StateStore

        scratch = Path(tempfile.mkdtemp(prefix="worldline-relocate-"))
        try:
            paths = WorldlinePaths(home=scratch, data=self.new_data, state=self.new_state,
                                   runtime=scratch / "runtime", config=scratch / "config")
            store = StateStore(paths, self.core)
            try:
                chains = store.verify_chains()
                store_root = os.path.realpath(os.fsencode(self.new_data)) + b"/"
                for link in self._mapping_links():
                    if not os.path.realpath(os.fsencode(link)).startswith(store_root):
                        raise _refuse(f"a mapping link does not resolve inside the new store: {link}")
                for root in store.roots():
                    live = paths.live / root["root_key"]
                    areas = (os.fsdecode(store_root) + "generations/", os.fsdecode(store_root) + "transactions/")
                    if not live.is_symlink() or not os.path.realpath(live).startswith(areas) or not live.is_dir():
                        # The daemon's own rule (root_source): a link into a payload (review of 09f5c0b).
                        raise _refuse(f"live mapping for {root['root_key']} is not a link to a payload in the new store")
                retained = [world for world in store.worlds() if not world.payload_pruned]
                missing = [world.alias for world in retained if not Path(world.payload_path).is_dir()]
                if missing:
                    raise _refuse("retained world payloads are missing from the new store", {"worlds": missing[:50]})
                outside = [world.alias for world in retained
                           if not os.path.realpath(os.fsencode(world.payload_path)).startswith(store_root)]
                if outside:
                    # A path under the new prefix can still resolve into the old store through a
                    # link inside the copy (review of ff201cd).
                    raise _refuse("retained world payloads resolve outside the new store", {"worlds": outside[:50]})
                connection = sqlite3.connect(f"file:{self.database}?mode=ro", uri=True)
                try:  # a Connection's `with` commits; it does not close
                    for table, column in LOCATION_COLUMNS:
                        for (value,) in connection.execute(f"SELECT {column} FROM {table}"):
                            self._require_inside_new(value, f"{table}.{column}")
                finally:
                    connection.close()
            finally:
                store.close()
        finally:
            shutil.rmtree(scratch, ignore_errors=True)
        return {"chains": chains, "roots": "RESOLVED", "payloads": "PRESENT"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="worldline-relocate",
        description="Rewrite a stopped store copy's recorded locations from its old directories to its new ones.")
    parser.add_argument("--from-data", required=True, type=Path)
    parser.add_argument("--from-state", required=True, type=Path)
    parser.add_argument("--to-data", required=True, type=Path)
    parser.add_argument("--to-state", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    arguments = parser.parse_args(argv)
    try:
        result = Relocation(old_data=arguments.from_data, old_state=arguments.from_state,
                            new_data=arguments.to_data, new_state=arguments.to_state).run(dry_run=arguments.dry_run)
    except WorldlineError as exc:
        print(json.dumps({"state": "REFUSED", **exc.as_dict()}, indent=2, sort_keys=True), file=sys.stderr)
        return 1
    except (OSError, MemoryError, RecursionError, sqlite3.Error, ValueError) as exc:
        # A corrupt database, a record that is not JSON, a vanished file: named, never a
        # traceback (review of 796cb02 found the first two escaping).
        refused = _refuse(f"relocation stopped: {exc.__class__.__name__}: {exc}")
        print(json.dumps({"state": "REFUSED", **refused.as_dict()}, indent=2, sort_keys=True), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
