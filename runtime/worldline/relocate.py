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
  receipts, manifests), agent output and the snapshots given to agents are kept byte for byte
  and counted in the report. A mention anywhere else, including any other database column,
  refuses the relocation.

The old copy is never opened for writing. Rolling back is starting the old daemon again.

Run it as the account that will own the store (never root), on a copy that account already owns,
with no daemon serving it: each is checked, and every rewrite is planned and every refusal raised
before anything is written. It does not re-point the operator's root links; `worldline doctor`
(rootIntegrity) shows them once the daemon runs.
"""
from __future__ import annotations

import argparse
import json
import os
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
from .paths import WorldlinePaths

# (table, column) pairs that hold a location in the store. Nothing else in the database may.
LOCATION_COLUMNS = (
    ("worlds", "payload_path"),
    ("worlds", "base_payload_path"),
    ("jobs", "raw_event_path"),
    ("causal_events", "canonical_path"),
    ("transactions", "prepared_path"),
    ("receipts", "canonical_path"),
)
OPEN_TRANSACTION_STATES = ("PREPARED", "AUTHORIZED")
ACTIVE_JOB_STATES = ("STARTING", "RUNNING", "FINALIZING")


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
        self.database = new_state / "worldline.sqlite3"
        if self.database.is_symlink() or not self.database.is_file():
            raise _refuse(f"no store database file at {self.database}")
        # The database is the only file rewritten in place. A hard-linked or symlinked copy could
        # share it with the old store (review of ff201cd): the copy's database, and its -wal and
        # -shm, must each be a file of its own.
        for suffix in ("", "-wal", "-shm"):
            candidate = Path(str(self.database) + suffix)
            if candidate.is_symlink() or (candidate.exists() and candidate.stat().st_nlink != 1):
                raise _refuse(f"{candidate.name} in the copy is linked elsewhere; copy it, do not link it")

    # -- mapping one location

    def _mentions(self, value: bytes) -> bool:
        return any(prefix in value for prefix in self.old)

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
                if mapped != value:
                    plan.append((table, column, rowid, mapped))
        return plan

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
        """Processes this uid can see that hold the copy's database open. A daemon serving the
        copy runs as the same account, so it is visible; `BEGIN EXCLUSIVE` alone does not detect
        an idle WAL connection."""
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
                    if (info.st_dev, info.st_ino) in identities:  # by inode, not by path
                        holders.add(int(process.name))
            except OSError:
                continue  # another uid's process, or gone
        return sorted(holders)

    def _foreign_entries(self) -> tuple[int, list[str], int]:
        """Entries in the copy not owned by the account doing the relocation (it will own the
        store): an incomplete chown after a root copy leaves content the daemon cannot vouch for.
        A directory the account cannot read (overlay work directories are 000 by design) is
        checked itself but not descended; the count of those is reported."""
        uid = os.geteuid()
        count = 0
        undescended = 0
        sample: list[str] = []
        for root in (self.new_data, self.new_state):
            for directory, subdirectories, files in os.walk(root):
                for name in (directory, *[os.path.join(directory, entry) for entry in subdirectories + files]):
                    info = os.lstat(name)
                    if info.st_uid != uid:
                        count += 1
                        if len(sample) < 20:
                            sample.append(f"uid={info.st_uid} {os.path.relpath(name, root)}")
                readable = [entry for entry in subdirectories
                            if not os.path.islink(os.path.join(directory, entry))
                            and os.access(os.path.join(directory, entry), os.R_OK | os.X_OK)]
                undescended += sum(1 for entry in subdirectories
                                   if not os.path.islink(os.path.join(directory, entry)) and entry not in readable)
                subdirectories[:] = readable
        return count, sample, undescended

    def _live_unsafe_for_clients(self) -> tuple[int, list[str]]:
        """PRIME content a client-mode daemon would refuse at start (group or other write, or a
        setuid, setgid or sticky bit): reported so a migration learns it before starting."""
        flags = stat.S_IWGRP | stat.S_IWOTH | stat.S_ISUID | stat.S_ISGID | stat.S_ISVTX
        count = 0
        sample: list[str] = []
        live = self.new_data / "live"
        for link in (sorted(live.iterdir()) if live.is_dir() else []):
            if not link.is_symlink():
                continue
            target = os.path.realpath(link)
            for directory, subdirectories, files in os.walk(target):
                for name in (directory, *[os.path.join(directory, entry) for entry in subdirectories + files]):
                    info = os.lstat(name)
                    if not stat.S_ISLNK(info.st_mode) and stat.S_IMODE(info.st_mode) & flags:
                        count += 1
                        if len(sample) < 20:
                            sample.append(f"{stat.S_IMODE(info.st_mode):04o} {link.name[:12]}/{os.path.relpath(name, target)}")
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
                links = [name for name in files + subdirectories if os.path.islink(os.path.join(directory, name))]
                # Overlay work directories are 000 by design; they hold content, never a location.
                subdirectories[:] = [name for name in subdirectories
                                     if name not in links
                                     and os.access(os.path.join(directory, name), os.R_OK | os.X_OK)]
                for name in files + links:
                    path = os.path.join(directory, name)
                    relative = tuple(Path(path).relative_to(root).parts)
                    if base == "state" and relative[0].startswith("worldline.sqlite3"):
                        continue  # read through SQL, not as bytes
                    link = name in links
                    try:
                        if link:
                            mentioned = self._mentions(os.readlink(os.fsencode(path)))
                        else:
                            with open(path, "rb") as stream:
                                mentioned = self._mentions(stream.read())
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

    def _scan_database(self, connection: sqlite3.Connection, *, skip_locations: bool) -> dict[str, int]:
        """Rows per column that mention an old prefix (location columns omitted when asked)."""
        found: dict[str, int] = {}
        tables = [row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        for table in tables:
            for column in [row[1] for row in connection.execute(f"PRAGMA table_info({table})")]:
                if skip_locations and (table, column) in LOCATION_COLUMNS:
                    continue
                count = 0
                for (value,) in connection.execute(f"SELECT {column} FROM {table}"):
                    if value is None:
                        continue
                    raw = value if isinstance(value, bytes) else str(value).encode("utf-8", "surrogateescape")
                    count += self._mentions(raw)
                if count:
                    found[f"{table}.{column}"] = count
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
        if os.geteuid() == 0:
            raise _refuse("run as the account that will own the store, not as root")
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
            found, refused = self._scan()
            foreign, foreign_sample, undescended = self._foreign_entries()
            unsafe, unsafe_sample = self._live_unsafe_for_clients()
            report = {
                "locationRows": {f"{table}.{column}": sum(1 for row in database_plan if row[:2] == (table, column))
                                 for table, column in LOCATION_COLUMNS},
                "transactionRecords": len(records_plan), "mappingLinks": len(links_plan),
                "mentions": found, "refusedFiles": refused[:200], "refusedDatabaseColumns": stray_columns,
                "foreignOwned": {"count": foreign, "sample": foreign_sample,
                                 "unreadableDirectoriesNotDescended": undescended},
                "liveContentUnsafeForClients": {"count": unsafe, "sample": unsafe_sample},
            }
            if dry_run:
                connection.execute("ROLLBACK")
                connection.close()
                return {"state": "DRY_RUN", **report}
            if refused or stray_columns or foreign:
                raise _refuse("the copy names the old store where it cannot be rewritten, or holds "
                              "entries its account does not own", report)
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
        return {"state": "RELOCATED",
                "rewritten": {"databaseRows": report["locationRows"], "transactionRecords": len(records_plan),
                              "mappingLinks": len(links_plan)},
                "mentionsKept": found, "verification": self.verify()}

    def verify(self) -> dict[str, Any]:
        """The relocated store, read as the daemon will read it."""
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
                    if not os.path.realpath(live).startswith(os.fsdecode(store_root)) or not live.is_dir():
                        raise _refuse(f"live mapping for {root['root_key']} does not resolve inside the new store")
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
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
