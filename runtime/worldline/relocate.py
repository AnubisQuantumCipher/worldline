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
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
from typing import Any, Iterator

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
        if not self.database.is_file():
            raise _refuse(f"no store database at {self.database}")

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

    def _rewrite_database(self, connection: sqlite3.Connection) -> dict[str, int]:
        counts: dict[str, int] = {}
        for table, column in LOCATION_COLUMNS:
            rows = connection.execute(f"SELECT rowid, {column} FROM {table}").fetchall()
            changed = 0
            for rowid, value in rows:
                if not isinstance(value, str):
                    raise _refuse(f"{table}.{column} holds a non-text location", {"rowid": rowid})
                mapped = os.fsdecode(self._map(os.fsencode(value), f"{table}.{column}"))
                if mapped != value:
                    connection.execute(f"UPDATE {table} SET {column}=? WHERE rowid=?", (mapped, rowid))
                    changed += 1
            counts[f"{table}.{column}"] = changed
        return counts

    def _rewrite_json_strings(self, value: Any, where: str) -> Any:
        if isinstance(value, dict):
            return {key: self._rewrite_json_strings(item, where) for key, item in value.items()}
        if isinstance(value, list):
            return [self._rewrite_json_strings(item, where) for item in value]
        if isinstance(value, str) and self._mentions(os.fsencode(value)):
            return os.fsdecode(self._map(os.fsencode(value), where))
        return value

    def _rewrite_transaction_records(self) -> int:
        changed = 0
        directory = self.new_state / "transactions"
        if not directory.is_dir():
            return 0
        for path in sorted(directory.glob("*.json")):
            raw = path.read_bytes()
            if not self._mentions(raw):
                continue
            value = json.loads(raw)
            if canonical_bytes(value) != raw:
                # Rewriting re-serializes. Only a canonical record re-serializes to itself.
                raise _refuse(f"transaction record is not canonical JSON: {path.name}")
            atomic_write_json(path, self._rewrite_json_strings(value, f"transactions/{path.name}"),
                              mode=path.stat().st_mode & 0o777)
            changed += 1
        return changed

    def _mapping_links(self) -> Iterator[Path]:
        live = self.new_data / "live"
        if live.is_dir():
            yield from (item for item in sorted(live.iterdir()) if item.is_symlink())
        transactions = self.new_data / "transactions"
        if transactions.is_dir():
            for mapping in sorted(transactions.glob("*/mapping")):
                if mapping.is_dir() and not mapping.is_symlink():
                    yield from (item for item in sorted(mapping.iterdir()) if item.is_symlink())

    def _rewrite_mapping_links(self) -> int:
        changed = 0
        for link in self._mapping_links():
            target = os.readlink(os.fsencode(link))
            mapped = self._map(target, f"mapping link {link.relative_to(self.new_data)}")
            if mapped == target:
                continue
            temporary = link.with_name(f".{link.name}.relocate")
            os.symlink(mapped, os.fsencode(temporary))
            os.replace(temporary, link)
            changed += 1
        return changed

    # -- classification of every remaining mention

    def _classify(self, relative: tuple[str, ...], base: str, *, link: bool) -> str | None:
        """What a mention of an old prefix is, or None if it may not exist at all.

        "location" is what the relocation rewrites; after it, a location that still mentions the
        old store is refused. Every other class is kept byte for byte.
        """
        if base == "state":
            if len(relative) == 2 and relative[0] == "transactions" and relative[1].endswith(".json") and not link:
                return "location"
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
        connection = sqlite3.connect(self.database, isolation_level=None)
        try:
            try:
                connection.execute("BEGIN EXCLUSIVE")  # a daemon serving this copy would hold it
                self._quiescent(connection)
                if dry_run:
                    planned = {f"{table}.{column}": count for (table, column) in LOCATION_COLUMNS
                               if (count := sum(1 for (value,) in connection.execute(f"SELECT {column} FROM {table}")
                                                if isinstance(value, str) and self._mentions(os.fsencode(value))))}
                    connection.execute("ROLLBACK")
                    found, refused = self._scan()
                    return {"state": "DRY_RUN", "locationRows": planned, "mentions": found,
                            "refusedFiles": refused[:200],
                            "refusedDatabaseColumns": self._scan_database(connection, skip_locations=True)}
                columns = self._rewrite_database(connection)
                connection.execute("COMMIT")
            except BaseException:
                if connection.in_transaction:
                    connection.execute("ROLLBACK")
                raise
            records = self._rewrite_transaction_records()
            links = self._rewrite_mapping_links()
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
                "rewritten": {"databaseRows": columns, "transactionRecords": records, "mappingLinks": links},
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
                missing = [world.alias for world in store.worlds()
                           if not world.payload_pruned and not Path(world.payload_path).is_dir()]
                if missing:
                    raise _refuse("retained world payloads are missing from the new store", {"worlds": missing[:50]})
            finally:
                store.close()
        finally:
            import shutil
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
