from __future__ import annotations

from contextlib import contextmanager
import json
import os
from pathlib import Path
import sqlite3
import stat
from threading import RLock
from typing import Any, Iterator, Sequence

from . import SCHEMA_VERSION
from .canonical import atomic_write, canonical_bytes
from .core import Core, hash_bytes_from_id, hash_id
from .errors import NotFound, WorldlineError
from .model import NONTERMINAL_STATES, World, WorldState, utc_now
from .paths import WorldlinePaths

_ZERO_HASH = bytes(32)

# The SQLite schema version (PRAGMA user_version). Independent of SCHEMA_VERSION, which names the
# document formats (status, events, receipts) and stays 1. Bump this when a table changes and add
# the forward migration below; never edit an old migration.
STORE_SCHEMA_VERSION = 2
_MIGRATIONS: dict[int, tuple[str, ...]] = {
    2: (
        "ALTER TABLE worlds ADD COLUMN payload_pruned INTEGER NOT NULL DEFAULT 0 CHECK (payload_pruned IN (0, 1))",
        "ALTER TABLE worlds ADD COLUMN pruned_at TEXT",
    ),
}

_SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value BLOB NOT NULL
) STRICT;

CREATE TABLE IF NOT EXISTS roots (
    root_key TEXT PRIMARY KEY,
    path BLOB NOT NULL UNIQUE,
    display_path TEXT NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('repo', 'config', 'filesystem')),
    device INTEGER NOT NULL,
    primary_root INTEGER NOT NULL CHECK (primary_root IN (0, 1)),
    generation_id TEXT,
    manifest_root TEXT,
    added_at TEXT NOT NULL
) STRICT;

CREATE UNIQUE INDEX IF NOT EXISTS one_primary_root
ON roots(primary_root) WHERE primary_root = 1;

CREATE TABLE IF NOT EXISTS worlds (
    instance_id TEXT PRIMARY KEY,
    alias TEXT NOT NULL UNIQUE,
    parent_instance TEXT REFERENCES worlds(instance_id) ON DELETE RESTRICT,
    parent_content TEXT NOT NULL,
    cause TEXT NOT NULL,
    actor TEXT NOT NULL,
    born TEXT NOT NULL,
    ended TEXT,
    state TEXT NOT NULL CHECK (state IN ('MUTABLE','FINALIZING','VALID','DEGRADED','DEAD','ARCHIVED','COLLAPSED')),
    components BLOB NOT NULL,
    content_id TEXT UNIQUE,
    payload_path TEXT NOT NULL,
    mission_hash TEXT NOT NULL,
    agent_reference TEXT,
    evidence BLOB NOT NULL,
    workspace BLOB NOT NULL,
    base_payload_path TEXT NOT NULL,
    base_root TEXT NOT NULL,
    root_set_hash TEXT NOT NULL,
    delta_hash TEXT,
    delta BLOB NOT NULL,
    conflicts BLOB NOT NULL,
    contamination BLOB NOT NULL,
    world_kind TEXT NOT NULL CHECK (world_kind IN ('computational','system')),
    complexity TEXT NOT NULL CHECK (complexity IN ('LOW','MEDIUM','HIGH')),
    risk TEXT NOT NULL CHECK (risk IN ('LOW','MEDIUM','HIGH')),
    payload_pruned INTEGER NOT NULL DEFAULT 0 CHECK (payload_pruned IN (0, 1)),
    pruned_at TEXT
) STRICT;

CREATE INDEX IF NOT EXISTS worlds_parent ON worlds(parent_instance);
CREATE INDEX IF NOT EXISTS worlds_state ON worlds(state);

CREATE TABLE IF NOT EXISTS jobs (
    job_id TEXT PRIMARY KEY,
    world_instance TEXT NOT NULL REFERENCES worlds(instance_id) ON DELETE RESTRICT,
    state TEXT NOT NULL,
    systemd_unit TEXT,
    pid INTEGER,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    error BLOB,
    raw_event_path TEXT NOT NULL,
    sandbox BLOB NOT NULL
) STRICT;

CREATE INDEX IF NOT EXISTS jobs_world ON jobs(world_instance);

CREATE TABLE IF NOT EXISTS causal_events (
    event_id TEXT PRIMARY KEY,
    world_instance TEXT NOT NULL REFERENCES worlds(instance_id) ON DELETE RESTRICT,
    ordinal INTEGER NOT NULL,
    kind TEXT NOT NULL,
    actor TEXT,
    tool TEXT,
    reason TEXT,
    path_b64 TEXT,
    path_display TEXT,
    line_start INTEGER,
    line_end INTEGER,
    predecessor TEXT NOT NULL,
    event_root TEXT NOT NULL,
    chain_hash TEXT NOT NULL UNIQUE,
    canonical_path TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    UNIQUE(world_instance, ordinal)
) STRICT;

CREATE TABLE IF NOT EXISTS line_ranges (
    range_id INTEGER PRIMARY KEY,
    world_instance TEXT NOT NULL REFERENCES worlds(instance_id) ON DELETE RESTRICT,
    event_id TEXT NOT NULL REFERENCES causal_events(event_id) ON DELETE RESTRICT,
    root_key TEXT NOT NULL,
    path_b64 TEXT NOT NULL,
    path_display TEXT NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    granularity TEXT NOT NULL CHECK (granularity IN ('line','file')),
    CHECK (start_line > 0 AND end_line >= start_line)
) STRICT;

CREATE INDEX IF NOT EXISTS line_ranges_lookup
ON line_ranges(root_key, path_b64, start_line, end_line);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,
    kind TEXT NOT NULL CHECK (kind IN ('collapse','return')),
    state TEXT NOT NULL CHECK (state IN ('PREPARED','AUTHORIZED','DENIED','COMMITTED','ABORTED')),
    candidate_world TEXT NOT NULL REFERENCES worlds(instance_id) ON DELETE RESTRICT,
    prepared_path TEXT NOT NULL UNIQUE,
    before_root TEXT NOT NULL,
    base_root TEXT NOT NULL,
    candidate_root TEXT NOT NULL,
    delta_hash TEXT NOT NULL,
    staged_root TEXT NOT NULL,
    root_set_hash TEXT NOT NULL,
    generation_marker TEXT NOT NULL,
    created_at TEXT NOT NULL,
    committed_at TEXT,
    error BLOB
) STRICT;

CREATE TABLE IF NOT EXISTS receipts (
    receipt_id TEXT PRIMARY KEY,
    previous_receipt TEXT,
    transaction_id TEXT NOT NULL UNIQUE REFERENCES transactions(transaction_id) ON DELETE RESTRICT,
    receipt_root TEXT NOT NULL,
    chain_hash TEXT NOT NULL UNIQUE,
    canonical_path TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
) STRICT;
"""


def _json_blob(value: Any) -> bytes:
    return canonical_bytes(value)


def _json_load(value: bytes | str | None, default: Any) -> Any:
    if value is None:
        return default
    if isinstance(value, str):
        value = value.encode("utf-8")
    return json.loads(value.decode("utf-8"))


class StateStore:
    def __init__(self, paths: WorldlinePaths, core: Core | None = None) -> None:
        self.paths = paths
        self.paths.ensure()
        self.core = core or Core.shared()
        self._lock = RLock()
        self._connection = sqlite3.connect(
            self.paths.database,
            timeout=30.0,
            isolation_level=None,
            check_same_thread=False,
        )
        self._connection.row_factory = sqlite3.Row
        self._configure()
        self._create_schema()
        self._secure_database_files()

    def _configure(self) -> None:
        with self._lock:
            self._connection.execute("PRAGMA foreign_keys=ON")
            mode = self._connection.execute("PRAGMA journal_mode=WAL").fetchone()[0]
            if str(mode).lower() != "wal":
                raise WorldlineError("SQLITE_WAL_UNAVAILABLE", f"SQLite selected journal mode {mode}")
            self._connection.execute("PRAGMA synchronous=FULL")
            self._connection.execute("PRAGMA wal_autocheckpoint=1000")
            self._connection.execute("PRAGMA busy_timeout=30000")
            self._connection.execute("PRAGMA trusted_schema=OFF")

    def _create_schema(self) -> None:
        with self._lock:
            current = int(self._connection.execute("PRAGMA user_version").fetchone()[0])
            if current > STORE_SCHEMA_VERSION:
                raise WorldlineError(
                    "UNSUPPORTED_SCHEMA",
                    f"database schema {current} is newer than this runtime supports ({STORE_SCHEMA_VERSION}); "
                    "upgrade worldline rather than downgrading the store",
                    {"found": current, "supported": STORE_SCHEMA_VERSION},
                )
            # CREATE IF NOT EXISTS gives a fresh store the whole current schema and is a no-op on an
            # existing one; forward-only migrations then bring an older store up, one version at a
            # time, and each step is recorded so the history is inspectable.
            self._connection.executescript(_SCHEMA)
            if current == 0:
                self._connection.execute(f"PRAGMA user_version={STORE_SCHEMA_VERSION}")
            else:
                for version in range(current + 1, STORE_SCHEMA_VERSION + 1):
                    for statement in _MIGRATIONS[version]:
                        self._connection.execute(statement)
                    self._connection.execute(f"PRAGMA user_version={version}")
                    history = list(self.get_meta("schemaMigrations", []) or [])
                    history.append({"from": version - 1, "to": version, "at": utc_now()})
                    self.set_meta("schemaMigrations", history)
            self.set_meta("schemaVersion", SCHEMA_VERSION)
            self.set_meta("storeSchemaVersion", STORE_SCHEMA_VERSION)
            self.set_meta("dirty", False)
            self.set_meta("inotifyGeneration", 0)

    def _secure_database_files(self) -> None:
        for path in (self.paths.database, Path(f"{self.paths.database}-wal"), Path(f"{self.paths.database}-shm")):
            if not path.exists():
                continue
            info = path.lstat()
            if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid():
                raise WorldlineError("UNSAFE_STORE", f"unsafe SQLite file: {path}")
            os.chmod(path, 0o600)

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        with self._lock:
            self._connection.execute("BEGIN IMMEDIATE")
            try:
                yield self._connection
            except BaseException:
                self._connection.execute("ROLLBACK")
                raise
            else:
                self._connection.execute("COMMIT")

    def close(self) -> None:
        with self._lock:
            self._connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            self._connection.close()

    def set_meta(self, key: str, value: Any) -> None:
        payload = _json_blob(value)
        with self._lock:
            self._connection.execute(
                "INSERT INTO meta(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, payload),
            )

    def get_meta(self, key: str, default: Any = None) -> Any:
        with self._lock:
            row = self._connection.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return default if row is None else _json_load(row[0], default)

    def add_root(
        self,
        *,
        root_key: str,
        raw_path: bytes,
        display_path: str,
        kind: str,
        device: int,
        primary: bool,
        generation_id: str | None = None,
        manifest_root: str | None = None,
    ) -> None:
        with self._lock:
            try:
                self._connection.execute(
                    """INSERT INTO roots
                    (root_key,path,display_path,kind,device,primary_root,generation_id,manifest_root,added_at)
                    VALUES(?,?,?,?,?,?,?,?,?)""",
                    (
                        root_key,
                        sqlite3.Binary(raw_path),
                        display_path,
                        kind,
                        device,
                        int(primary),
                        generation_id,
                        manifest_root,
                        utc_now(),
                    ),
                )
            except sqlite3.IntegrityError as exc:
                raise WorldlineError("ROOT_CONFLICT", f"root is already registered: {display_path}") from exc

    def update_root_generation(self, root_key: str, generation_id: str, manifest_root: str) -> None:
        with self._lock:
            cursor = self._connection.execute(
                "UPDATE roots SET generation_id=?, manifest_root=? WHERE root_key=?",
                (generation_id, manifest_root, root_key),
            )
        if not cursor.rowcount:
            raise NotFound("root", root_key)

    def remove_root(self, root_key: str) -> None:
        with self._lock:
            cursor = self._connection.execute("DELETE FROM roots WHERE root_key=?", (root_key,))
        if not cursor.rowcount:
            raise NotFound("root", root_key)

    def set_primary_root(self, root_key: str) -> None:
        with self.transaction() as connection:
            exists = connection.execute("SELECT 1 FROM roots WHERE root_key=?", (root_key,)).fetchone()
            if exists is None:
                raise NotFound("root", root_key)
            connection.execute("UPDATE roots SET primary_root=0 WHERE primary_root=1")
            connection.execute("UPDATE roots SET primary_root=1 WHERE root_key=?", (root_key,))

    def roots(self) -> list[dict[str, Any]]:
        with self._lock:
            rows = self._connection.execute(
                "SELECT * FROM roots ORDER BY primary_root DESC, path"
            ).fetchall()
        return [dict(row) for row in rows]

    def root(self, value: str | bytes) -> dict[str, Any]:
        with self._lock:
            if isinstance(value, bytes):
                row = self._connection.execute("SELECT * FROM roots WHERE path=?", (sqlite3.Binary(value),)).fetchone()
            else:
                row = self._connection.execute(
                    "SELECT * FROM roots WHERE root_key=? OR display_path=?",
                    (value, value),
                ).fetchone()
        if row is None:
            raise NotFound("root", os.fsdecode(value))
        return dict(row)

    def insert_world(self, world: World) -> None:
        values = world.record()
        with self._lock:
            try:
                self._connection.execute(
                    """INSERT INTO worlds
                    (instance_id,alias,parent_instance,parent_content,cause,actor,born,ended,state,
                     components,content_id,payload_path,mission_hash,agent_reference,evidence,workspace,
                     base_payload_path,base_root,root_set_hash,delta_hash,delta,conflicts,contamination,
                     world_kind,complexity,risk,payload_pruned,pruned_at)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        values["instance_id"], values["alias"], values["parent_instance"],
                        values["parent_content"], values["cause"], values["actor"], values["born"],
                        values["ended"], values["state"], _json_blob(values["components"]),
                        values["content_id"], values["payload_path"], values["mission_hash"],
                        values["agent_reference"], _json_blob(values["evidence"]),
                        _json_blob(values["workspace"]), values["base_payload_path"],
                        values["base_root"], values["root_set_hash"], values["delta_hash"],
                        _json_blob(values["delta"]), _json_blob(values["conflicts"]),
                        _json_blob(values["contamination"]), values["world_kind"],
                        values["complexity"], values["risk"], int(bool(values["payload_pruned"])), values["pruned_at"],
                    ),
                )
            except sqlite3.IntegrityError as exc:
                raise WorldlineError("WORLD_CONFLICT", f"world alias or identity already exists: {world.alias}") from exc

    def save_world(self, world: World) -> None:
        values = world.record()
        with self._lock:
            cursor = self._connection.execute(
                """UPDATE worlds SET
                alias=?,parent_instance=?,parent_content=?,cause=?,actor=?,born=?,ended=?,state=?,
                components=?,content_id=?,payload_path=?,mission_hash=?,agent_reference=?,evidence=?,workspace=?,
                base_payload_path=?,base_root=?,root_set_hash=?,delta_hash=?,delta=?,conflicts=?,contamination=?,
                world_kind=?,complexity=?,risk=?,payload_pruned=?,pruned_at=? WHERE instance_id=?""",
                (
                    values["alias"], values["parent_instance"], values["parent_content"], values["cause"],
                    values["actor"], values["born"], values["ended"], values["state"],
                    _json_blob(values["components"]), values["content_id"], values["payload_path"],
                    values["mission_hash"], values["agent_reference"], _json_blob(values["evidence"]),
                    _json_blob(values["workspace"]), values["base_payload_path"], values["base_root"],
                    values["root_set_hash"], values["delta_hash"], _json_blob(values["delta"]),
                    _json_blob(values["conflicts"]), _json_blob(values["contamination"]),
                    values["world_kind"], values["complexity"], values["risk"],
                    int(bool(values["payload_pruned"])), values["pruned_at"], values["instance_id"],
                ),
            )
        if not cursor.rowcount:
            raise NotFound("world", world.instance_id)

    @staticmethod
    def _world_from_row(row: sqlite3.Row) -> World:
        return World(
            instance_id=row["instance_id"],
            alias=row["alias"],
            parent_instance=row["parent_instance"],
            parent_content=row["parent_content"],
            cause=row["cause"],
            actor=row["actor"],
            born=row["born"],
            ended=row["ended"],
            state=WorldState(row["state"]),
            components=_json_load(row["components"], {}),
            content_id=row["content_id"],
            payload_path=row["payload_path"],
            mission_hash=row["mission_hash"],
            agent_reference=row["agent_reference"],
            evidence=_json_load(row["evidence"], {}),
            workspace=_json_load(row["workspace"], {}),
            base_payload_path=row["base_payload_path"],
            base_root=row["base_root"],
            root_set_hash=row["root_set_hash"],
            delta_hash=row["delta_hash"],
            delta=_json_load(row["delta"], {}),
            conflicts=_json_load(row["conflicts"], []),
            contamination=_json_load(row["contamination"], []),
            world_kind=row["world_kind"],
            complexity=row["complexity"],
            risk=row["risk"],
            payload_pruned=bool(row["payload_pruned"]),
            pruned_at=row["pruned_at"],
        )

    def world(self, value: str) -> World:
        with self._lock:
            row = self._connection.execute(
                "SELECT * FROM worlds WHERE instance_id=? OR alias=? OR content_id=?",
                (value, value, value),
            ).fetchone()
        if row is None:
            raise NotFound("world", value)
        world = self._world_from_row(row)
        world.descendants = self.descendant_count(world.instance_id)
        return world

    def worlds(self) -> list[World]:
        with self._lock:
            rows = self._connection.execute("SELECT * FROM worlds ORDER BY born, instance_id").fetchall()
        result = [self._world_from_row(row) for row in rows]
        counts = self._descendant_counts()
        for world in result:
            world.descendants = counts.get(world.instance_id, 0)
        return result

    def _descendant_counts(self) -> dict[str, int]:
        with self._lock:
            rows = self._connection.execute(
                """WITH RECURSIVE descendants(ancestor, child) AS (
                    SELECT parent_instance, instance_id FROM worlds WHERE parent_instance IS NOT NULL
                    UNION ALL
                    SELECT descendants.ancestor, worlds.instance_id
                    FROM descendants JOIN worlds ON worlds.parent_instance = descendants.child
                )
                SELECT ancestor, COUNT(*) AS count FROM descendants GROUP BY ancestor"""
            ).fetchall()
        return {row["ancestor"]: row["count"] for row in rows}

    def descendant_count(self, instance_id: str) -> int:
        return self._descendant_counts().get(instance_id, 0)

    def nonterminal_worlds(self) -> list[World]:
        placeholders = ",".join("?" for _ in NONTERMINAL_STATES)
        states = tuple(state.value for state in NONTERMINAL_STATES)
        with self._lock:
            rows = self._connection.execute(
                f"SELECT * FROM worlds WHERE state IN ({placeholders}) ORDER BY born",
                states,
            ).fetchall()
        return [self._world_from_row(row) for row in rows]

    def terminal_siblings(self, world: World) -> list[World]:
        with self._lock:
            rows = self._connection.execute(
                """SELECT * FROM worlds
                WHERE parent_instance IS ? AND instance_id != ?
                  AND state IN ('VALID','DEGRADED','DEAD','ARCHIVED','COLLAPSED')
                ORDER BY born""",
                (world.parent_instance, world.instance_id),
            ).fetchall()
        return [self._world_from_row(row) for row in rows]

    def set_prime(self, instance_id: str, content_id: str, generation_id: str) -> None:
        with self.transaction():
            self.set_meta("primeInstance", instance_id)
            self.set_meta("primeContent", content_id)
            self.set_meta("primeGeneration", generation_id)
            self.set_meta("dirty", False)

    def prime(self) -> World | None:
        instance_id = self.get_meta("primeInstance")
        return None if not instance_id else self.world(instance_id)

    def create_job(
        self,
        *,
        job_id: str,
        world_instance: str,
        state: str,
        raw_event_path: Path,
        sandbox: dict[str, Any],
        systemd_unit: str | None = None,
        pid: int | None = None,
    ) -> None:
        with self._lock:
            self._connection.execute(
                """INSERT INTO jobs
                (job_id,world_instance,state,systemd_unit,pid,started_at,raw_event_path,sandbox)
                VALUES(?,?,?,?,?,?,?,?)""",
                (job_id, world_instance, state, systemd_unit, pid, utc_now(), str(raw_event_path), _json_blob(sandbox)),
            )

    def update_job(
        self,
        job_id: str,
        *,
        state: str,
        systemd_unit: str | None = None,
        pid: int | None = None,
        error: dict[str, Any] | None = None,
        ended: bool = False,
    ) -> None:
        with self._lock:
            cursor = self._connection.execute(
                """UPDATE jobs SET state=?,systemd_unit=COALESCE(?,systemd_unit),pid=COALESCE(?,pid),
                error=?,ended_at=? WHERE job_id=?""",
                (state, systemd_unit, pid, None if error is None else _json_blob(error), utc_now() if ended else None, job_id),
            )
        if not cursor.rowcount:
            raise NotFound("job", job_id)

    def jobs(self) -> list[dict[str, Any]]:
        with self._lock:
            rows = self._connection.execute("SELECT * FROM jobs ORDER BY started_at").fetchall()
        result: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            item["error"] = _json_load(item["error"], None)
            item["sandbox"] = _json_load(item["sandbox"], {})
            result.append(item)
        return result

    def active_jobs_for_world(self, world_instance: str) -> list[dict[str, Any]]:
        return [
            job
            for job in self.jobs()
            if job["world_instance"] == world_instance
            and job["state"] in {"STARTING", "RUNNING", "FINALIZING"}
        ]

    def sweep_unsupervised(self) -> dict[str, int]:
        """Resolve every world and job that has no live supervisor.

        Runs at daemon start, before the socket is published, when by construction no
        background task exists: every STARTING/RUNNING/FINALIZING job lost its owner with the
        previous daemon, and every MUTABLE/FINALIZING world has nobody to finish it -- whether
        its job vanished with the daemon or it never got a job at all (an adapter that failed
        after the world row was inserted used to leave such a world MUTABLE forever, which in
        turn blocked every later `root add`/`root remove` with ROOT_SET_BUSY).

        The world transitions go through World.transition, i.e. the proved kernel. The previous
        implementation wrote state='DEGRADED' straight into SQL from MUTABLE, a transition the
        kernel forbids (Mutable -> Finalizing | Dead only): a world with no coherent payload is
        DEAD, and its evidence records why.
        """
        swept_jobs = 0
        swept_worlds = 0
        with self.transaction() as connection:
            rows = connection.execute(
                "SELECT job_id FROM jobs WHERE state IN ('STARTING','RUNNING','FINALIZING')"
            ).fetchall()
            for row in rows:
                error = _json_blob({"code": "DAEMON_RESTART", "message": "job owner disappeared during daemon restart"})
                connection.execute(
                    "UPDATE jobs SET state='DEGRADED',ended_at=?,error=? WHERE job_id=?",
                    (utc_now(), error, row["job_id"]),
                )
                swept_jobs += 1
        for world in self.nonterminal_worlds():
            had_job = any(job["world_instance"] == world.instance_id for job in self.jobs())
            reason = {
                "code": "DAEMON_RESTART" if had_job else "NO_SUPERVISING_JOB",
                "message": (
                    "supervision was lost during a daemon restart before the world finalized"
                    if had_job
                    else "the world was created but no agent job ever supervised it"
                ),
            }
            checks = list(world.evidence.get("checks", [])) if isinstance(world.evidence, dict) else []
            world.evidence = {"summary": "FAIL", "checks": checks, "supervision": reason}
            world.transition(WorldState.DEAD, self.core)
            self.save_world(world)
            swept_worlds += 1
        return {"jobs": swept_jobs, "worlds": swept_worlds}

    def append_causal_event(self, event: dict[str, Any]) -> dict[str, str]:
        if event.get("schemaVersion") != SCHEMA_VERSION:
            raise WorldlineError("INVALID_SCHEMA", "causal event schemaVersion must be literal 1")
        world_instance = str(event.get("worldInstance", ""))
        self.world(world_instance)
        payload = canonical_bytes(event)
        event_root = self.core.hash_bytes(b"worldline-event-v1" + payload)
        with self._lock:
            previous_row = self._connection.execute(
                "SELECT chain_hash,ordinal FROM causal_events ORDER BY rowid DESC LIMIT 1"
            ).fetchone()
            previous = _ZERO_HASH if previous_row is None else hash_bytes_from_id(previous_row["chain_hash"])
            chain = self.core.causal_link(previous, event_root)
            event_id = hash_id(chain)
            path = self.paths.events / f"{chain.hex()}.json"
            atomic_write(path, payload)
            ordinal = 0 if previous_row is None else int(previous_row["ordinal"]) + 1
            self._connection.execute(
                """INSERT INTO causal_events
                (event_id,world_instance,ordinal,kind,actor,tool,reason,path_b64,path_display,
                 line_start,line_end,predecessor,event_root,chain_hash,canonical_path,created_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    event_id, world_instance, ordinal, str(event.get("kind", "event")),
                    event.get("actor"), event.get("tool"), event.get("reason"),
                    event.get("pathB64"), event.get("pathDisplay"), event.get("lineStart"),
                    event.get("lineEnd"), hash_id(previous), hash_id(event_root), hash_id(chain),
                    str(path), utc_now(),
                ),
            )
        return {"eventId": event_id, "eventRoot": hash_id(event_root), "chainHash": hash_id(chain)}

    def add_line_ranges(self, ranges: Sequence[dict[str, Any]]) -> None:
        with self.transaction() as connection:
            for item in ranges:
                connection.execute(
                    """INSERT INTO line_ranges
                    (world_instance,event_id,root_key,path_b64,path_display,start_line,end_line,granularity)
                    VALUES(?,?,?,?,?,?,?,?)""",
                    (
                        item["worldInstance"], item["eventId"], item["rootKey"], item["pathB64"],
                        item["pathDisplay"], item["startLine"], item["endLine"], item["granularity"],
                    ),
                )

    def newest_line_event(self, root_key: str, path_b64: str, line: int) -> dict[str, Any] | None:
        with self._lock:
            row = self._connection.execute(
                """SELECT line_ranges.*,causal_events.* FROM line_ranges
                JOIN causal_events USING(event_id)
                WHERE line_ranges.root_key=? AND line_ranges.path_b64=?
                  AND line_ranges.start_line<=? AND line_ranges.end_line>=?
                ORDER BY causal_events.ordinal DESC LIMIT 1""",
                (root_key, path_b64, line, line),
            ).fetchone()
        return None if row is None else dict(row)

    def line_events(self, root_key: str, path_b64: str, line: int) -> list[dict[str, Any]]:
        """Every recorded line-range hit for a path and line, newest first (why decides which counts)."""
        with self._lock:
            rows = self._connection.execute(
                """SELECT line_ranges.*,causal_events.* FROM line_ranges
                JOIN causal_events USING(event_id)
                WHERE line_ranges.root_key=? AND line_ranges.path_b64=?
                  AND line_ranges.start_line<=? AND line_ranges.end_line>=?
                ORDER BY causal_events.ordinal DESC""",
                (root_key, path_b64, line, line),
            ).fetchall()
        return [dict(row) for row in rows]

    def causal_events_for_world(self, world_instance: str) -> list[dict[str, Any]]:
        with self._lock:
            rows = self._connection.execute(
                "SELECT * FROM causal_events WHERE world_instance=? ORDER BY ordinal",
                (world_instance,),
            ).fetchall()
        result: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            item["event"] = json.loads(Path(row["canonical_path"]).read_text(encoding="utf-8"))
            result.append(item)
        return result

    def create_transaction(self, record: dict[str, Any]) -> None:
        with self._lock:
            self._connection.execute(
                """INSERT INTO transactions
                (transaction_id,kind,state,candidate_world,prepared_path,before_root,base_root,candidate_root,
                 delta_hash,staged_root,root_set_hash,generation_marker,created_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    record["transactionId"], record["kind"], record["state"], record["candidateWorld"],
                    record["preparedPath"], record["beforeRoot"], record["baseRoot"], record["candidateRoot"],
                    record["deltaHash"], record["stagedRoot"], record["rootSetHash"],
                    record["generationMarker"], record.get("createdAt", utc_now()),
                ),
            )

    def update_transaction(
        self,
        transaction_id: str,
        state: str,
        *,
        error: dict[str, Any] | None = None,
        committed: bool = False,
    ) -> None:
        with self._lock:
            cursor = self._connection.execute(
                "UPDATE transactions SET state=?,error=?,committed_at=? WHERE transaction_id=?",
                (state, None if error is None else _json_blob(error), utc_now() if committed else None, transaction_id),
            )
        if not cursor.rowcount:
            raise NotFound("transaction", transaction_id)

    def transactions_in_state(self, states: Sequence[str]) -> list[dict[str, Any]]:
        placeholders = ",".join("?" for _ in states)
        with self._lock:
            rows = self._connection.execute(
                f"SELECT * FROM transactions WHERE state IN ({placeholders}) ORDER BY created_at",
                tuple(states),
            ).fetchall()
        return [dict(row) for row in rows]

    def transaction_record(self, transaction_id: str) -> dict[str, Any]:
        with self._lock:
            row = self._connection.execute(
                "SELECT * FROM transactions WHERE transaction_id=?", (transaction_id,)
            ).fetchone()
        if row is None:
            raise NotFound("transaction", transaction_id)
        result = dict(row)
        result["error"] = _json_load(result["error"], None)
        return result

    def append_receipt(self, receipt: dict[str, Any]) -> dict[str, str]:
        if receipt.get("schemaVersion") != SCHEMA_VERSION:
            raise WorldlineError("INVALID_SCHEMA", "receipt schemaVersion must be literal 1")
        required = {
            "schemaVersion", "receiptId", "previousReceipt", "parentWorld", "candidateWorld",
            "baseState", "candidateDelta", "foreignWorldContamination", "mergeSet",
            "invariantPreservation", "atomicCollapse", "beforeRoot", "afterRoot",
            "transactionId", "nonClaims",
        }
        # 1.3.0 receipts name the evidence that authorized the bytes; 1.2 receipts (already on
        # the chain, and any produced while recovering a 1.2-prepared record) lack the field.
        optional = {"evidenceBinding"}
        if not required <= set(receipt) or not set(receipt) <= required | optional:
            raise WorldlineError(
                "INVALID_RECEIPT",
                "collapse receipt fields do not match schema",
                {"missing": sorted(required - set(receipt)), "extra": sorted(set(receipt) - required)},
            )
        payload = canonical_bytes(receipt)
        root = self.core.hash_bytes(b"worldline-receipt-record-v1" + payload)
        with self._lock:
            previous_row = self._connection.execute(
                "SELECT receipt_id,chain_hash FROM receipts ORDER BY rowid DESC LIMIT 1"
            ).fetchone()
        expected_previous_id = None if previous_row is None else previous_row["receipt_id"]
        if receipt["previousReceipt"] != expected_previous_id:
            raise WorldlineError(
                "RECEIPT_PREDECESSOR_MISMATCH",
                "receipt does not name the current predecessor",
                {"expected": expected_previous_id, "supplied": receipt["previousReceipt"]},
            )
        previous_hash = _ZERO_HASH if previous_row is None else hash_bytes_from_id(previous_row["chain_hash"])
        chain = self.core.receipt_link(previous_hash, root)
        path = self.paths.receipts / f"{chain.hex()}.json"
        atomic_write(path, payload)
        with self._lock:
            self._connection.execute(
                """INSERT INTO receipts
                (receipt_id,previous_receipt,transaction_id,receipt_root,chain_hash,canonical_path,created_at)
                VALUES(?,?,?,?,?,?,?)""",
                (
                    receipt["receiptId"], receipt["previousReceipt"], receipt["transactionId"],
                    hash_id(root), hash_id(chain), str(path), utc_now(),
                ),
            )
        return {"receiptRoot": hash_id(root), "chainHash": hash_id(chain)}

    def receipts(self) -> list[dict[str, Any]]:
        with self._lock:
            rows = self._connection.execute("SELECT * FROM receipts ORDER BY rowid").fetchall()
        return [dict(row) for row in rows]

    def receipt_for_transaction(self, transaction_id: str) -> dict[str, Any] | None:
        with self._lock:
            row = self._connection.execute(
                "SELECT * FROM receipts WHERE transaction_id=?", (transaction_id,)
            ).fetchone()
        if row is None:
            return None
        result = dict(row)
        result["receipt"] = json.loads(Path(row["canonical_path"]).read_text(encoding="utf-8"))
        return result

    def receipt_for_candidate(self, content_id: str) -> dict[str, Any] | None:
        for row in reversed(self.receipts()):
            receipt = json.loads(Path(row["canonical_path"]).read_text(encoding="utf-8"))
            if receipt.get("candidateWorld") == content_id:
                return {**row, "receipt": receipt}
        return None

    def verify_chains(self) -> dict[str, int]:
        previous = _ZERO_HASH
        causal_count = 0
        with self._lock:
            causal_rows = self._connection.execute("SELECT * FROM causal_events ORDER BY rowid").fetchall()
            receipt_rows = self._connection.execute("SELECT * FROM receipts ORDER BY rowid").fetchall()
        for row in causal_rows:
            payload = Path(row["canonical_path"]).read_bytes()
            root = self.core.hash_bytes(b"worldline-event-v1" + payload)
            chain = self.core.causal_link(previous, root)
            if hash_id(previous) != row["predecessor"] or hash_id(root) != row["event_root"] or hash_id(chain) != row["chain_hash"]:
                raise WorldlineError("CAUSAL_CHAIN_INVALID", f"causal chain broke at {row['event_id']}")
            previous = chain
            causal_count += 1

        previous = _ZERO_HASH
        previous_receipt: str | None = None
        receipt_count = 0
        for row in receipt_rows:
            payload = Path(row["canonical_path"]).read_bytes()
            receipt = json.loads(payload.decode("utf-8"))
            if receipt.get("previousReceipt") != previous_receipt:
                raise WorldlineError("RECEIPT_CHAIN_INVALID", f"receipt predecessor broke at {row['receipt_id']}")
            root = self.core.hash_bytes(b"worldline-receipt-record-v1" + payload)
            chain = self.core.receipt_link(previous, root)
            if hash_id(root) != row["receipt_root"] or hash_id(chain) != row["chain_hash"]:
                raise WorldlineError("RECEIPT_CHAIN_INVALID", f"receipt chain broke at {row['receipt_id']}")
            previous = chain
            previous_receipt = row["receipt_id"]
            receipt_count += 1
        return {"causalEvents": causal_count, "receipts": receipt_count}

    def last_receipt(self) -> dict[str, Any] | None:
        with self._lock:
            row = self._connection.execute("SELECT * FROM receipts ORDER BY rowid DESC LIMIT 1").fetchone()
        if row is None:
            return None
        result = dict(row)
        result["receipt"] = json.loads(Path(row["canonical_path"]).read_text(encoding="utf-8"))
        return result
