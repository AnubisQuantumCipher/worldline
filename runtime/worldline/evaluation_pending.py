"""Private pending-attempt producer. Never imported by the default runtime.

The two durable stores are separate protocol participants. Mere possession of
these paths, an SQLite commit or a matching byte string does not authenticate
the caller, the current policy, a completed evaluation, or rollback resistance.
Protected custody and the deployment/recovery gate remain required externally.
This module has no completion operation and cannot return a PASS record.
"""
from __future__ import annotations

import base64
from contextlib import contextmanager
from dataclasses import dataclass
import json
import os
from pathlib import Path
import sqlite3
import stat
from threading import RLock

from .pending_kernel import Intent, PendingKernel, Reason


class PendingRefused(RuntimeError):
    """No caller may turn this into permission to use an older evaluation."""


def identity(value: str) -> bytes:
    if not isinstance(value, str):
        raise PendingRefused("IDENTITY_NOT_A_STRING")
    # Base method preserves the actual string, including isolated surrogates.
    return str.encode(value, "utf-8", "surrogatepass")


def text(value: bytes) -> str:
    if type(value) is not bytes:
        raise PendingRefused("IDENTITY_STORAGE_INVALID")
    return value.decode("utf-8", "surrogatepass")


def magnitude(value: bytes) -> bytes:
    if type(value) is not bytes or (value and value[-1] == 0):
        raise PendingRefused("EPOCH_STORAGE_NOT_CANONICAL")
    return value


def previous_cursor(epoch: bytes | None, run: bytes | None) -> tuple[bytes, bytes] | None:
    """Decode the complete nullable pair before constructing typed absence.

    The database CHECK is additional protection, not a decoder premise when an
    existing store is opened. Present empty values remain present values.
    """
    if (epoch is None) != (run is None):
        raise PendingRefused("PREVIOUS_CURSOR_PARTIAL")
    if epoch is None:
        return None
    return magnitude(epoch), identity(text(run))


def next_proposal(before: bytes) -> bytes:
    """Untrusted arithmetic proposal only; the actual Ada successor relation
    must accept it before it can be recorded. There is no Python success lane.
    """
    out = bytearray(magnitude(before))
    for index in range(len(out)):
        if out[index] != 255:
            out[index] += 1
            return bytes(out)
        out[index] = 0
    out.append(1)
    return bytes(out)


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("ascii")


def row_payload(*, store: bytes, subject: bytes, content: bytes,
                requirement: bytes | None, run: bytes, epoch: bytes,
                previous: tuple[bytes, bytes] | None) -> bytes:
    # Arbitrary epochs are BLOBs in the protocol; decimal conversion and the
    # host JSON integer digit limit never determine which epochs are accepted.
    return canonical({
        "schemaVersion": 1, "kind": "evaluation-pending-intent",
        "storeId": text(store), "worldInstance": text(subject),
        "worldContentId": text(content),
        "requirementHash": None if requirement is None else text(requirement),
        "validationId": text(run),
        "epochMagnitudeLE": base64.b64encode(magnitude(epoch)).decode("ascii"),
        "previous": None if previous is None else {
            "epochMagnitudeLE": base64.b64encode(magnitude(previous[0])).decode("ascii"),
            "validationId": text(previous[1])},
        "evaluationState": "PENDING", "outcome": None,
        "context": None, "results": []})


COMMON = """
CREATE TABLE identity (singleton INTEGER PRIMARY KEY CHECK(singleton=1), store_id BLOB NOT NULL) STRICT;
CREATE TABLE heads (subject BLOB PRIMARY KEY, epoch BLOB NOT NULL, run BLOB NOT NULL UNIQUE) STRICT;
"""
JOURNAL = """
CREATE TABLE intents (
 run BLOB PRIMARY KEY, subject BLOB NOT NULL, content BLOB NOT NULL,
 requirement BLOB, epoch BLOB NOT NULL, previous_epoch BLOB, previous_run BLOB,
 payload BLOB NOT NULL, UNIQUE(subject,epoch),
 CHECK((previous_epoch IS NULL)=(previous_run IS NULL))) STRICT;
CREATE TABLE links (run BLOB PRIMARY KEY REFERENCES intents(run), payload BLOB NOT NULL) STRICT;
"""
TARGET = """
CREATE TABLE pending_history (
 run BLOB PRIMARY KEY, subject BLOB NOT NULL, content BLOB NOT NULL,
 requirement BLOB, epoch BLOB NOT NULL, previous_epoch BLOB, previous_run BLOB,
 payload BLOB NOT NULL, UNIQUE(subject,epoch),
 CHECK((previous_epoch IS NULL)=(previous_run IS NULL))) STRICT;
CREATE TABLE outbox (
 run BLOB PRIMARY KEY REFERENCES pending_history(run), payload BLOB NOT NULL) STRICT;
"""


@dataclass(frozen=True)
class PendingHandle:
    store_id: str
    subject: str
    content: str
    run: str
    epoch: int


class PendingJournal:
    """Owned connections to explicitly created private stores.

    There is deliberately no legacy key migration, default path, caller-history
    list, caller epoch or authenticated-success flag. This constructor is not a
    protected-broker implementation: production use remains blocked until that
    separately required boundary and anti-rollback mechanism exist.
    """

    def __init__(self, journal: Path, target: Path, *, store_id: str,
                 library: Path, create: bool = False):
        self.kernel = PendingKernel(library)
        self.store = identity(store_id)
        self.lock = RLock()
        self.journal_path, self.target_path = Path(journal), Path(target)
        if self.journal_path.resolve() == self.target_path.resolve():
            raise PendingRefused("JOURNAL_TARGET_NOT_DISTINCT")
        if create:
            for path in (self.journal_path, self.target_path):
                # No replace, truncate, parent creation, migration or cleanup.
                fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                             0o600)
                try:
                    os.fsync(fd)
                finally:
                    os.close(fd)
                parent = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
                try:
                    os.fsync(parent)
                finally:
                    os.close(parent)
        infos = [path.lstat() for path in (self.journal_path, self.target_path)]
        if any(not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
               for info in infos):
            raise PendingRefused("STORE_FILE_INVALID")
        if (infos[0].st_dev, infos[0].st_ino) == (infos[1].st_dev, infos[1].st_ino):
            raise PendingRefused("JOURNAL_TARGET_NOT_DISTINCT")
        self.journal = self._connect(self.journal_path)
        self.target = self._connect(self.target_path)
        if create:
            for db, schema in ((self.journal, JOURNAL), (self.target, TARGET)):
                db.executescript("BEGIN IMMEDIATE;" + COMMON + schema)
                try:
                    db.execute("INSERT INTO identity VALUES(1,?)", (self.store,))
                    db.execute("COMMIT")
                except BaseException:
                    if db.in_transaction:
                        db.execute("ROLLBACK")
                    raise
        for db in (self.journal, self.target):
            found = db.execute("SELECT store_id FROM identity WHERE singleton=1").fetchall()
            if len(found) != 1 or found[0][0] != self.store:
                raise PendingRefused("STORE_IDENTITY_MISMATCH")
        self._schema(self.journal, JOURNAL)
        self._schema(self.target, TARGET)

    @staticmethod
    def _schema(db: sqlite3.Connection, role: str) -> None:
        """Check the complete owned store format before consuming its records.

        These literal schemas belong to this private journal protocol. The
        check is not a migration, custody authentication or anti-rollback proof.
        It admits the format this producer creates and refuses missing or extra
        schema behavior rather than assuming constraints on an existing store.
        """
        if role not in (JOURNAL, TARGET):
            raise PendingRefused("STORE_ROLE_INVALID")

        def normalized(sql: str) -> str:
            # The owned declarations contain no quoted string literals; only
            # whitespace and the trailing statement terminator are ignored.
            return " ".join(sql.strip().removesuffix(";").split())

        expected = {}
        for statement in (COMMON + role).split(";"):
            if not statement.strip():
                continue
            tokens = statement.split()
            if tokens[:2] != ["CREATE", "TABLE"]:
                raise PendingRefused("OWNED_SCHEMA_DECLARATION_INVALID")
            expected[tokens[2]] = normalized(statement)
        objects = db.execute("SELECT type,name,tbl_name,sql FROM main.sqlite_schema "
                             "ORDER BY type,name").fetchall()
        actual = {}
        for row in objects:
            if row["type"] == "table" and row["name"] in expected:
                actual[row["name"]] = normalized(row["sql"])
            elif (row["type"] == "index" and row["sql"] is None
                  and row["tbl_name"] in expected
                  and row["name"].startswith("sqlite_autoindex_" + row["tbl_name"] + "_")):
                # These implicit indexes implement the literal table keys.
                # A user-declared index has SQL and does not take this lane.
                continue
            else:
                raise PendingRefused("STORE_SCHEMA_OBJECT_CONFLICT")
        if actual != expected:
            raise PendingRefused("STORE_SCHEMA_CONFLICT")
        if db.execute("PRAGMA main.foreign_key_check").fetchone() is not None:
            raise PendingRefused("STORE_ORPHAN_RECORD")

    @staticmethod
    def _connect(path: Path) -> sqlite3.Connection:
        db = sqlite3.connect(path, isolation_level=None, check_same_thread=False)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        if db.execute("PRAGMA journal_mode=WAL").fetchone()[0] != "wal":
            raise PendingRefused("WAL_UNAVAILABLE")
        db.execute("PRAGMA synchronous=FULL")
        db.execute("PRAGMA trusted_schema=OFF")
        PendingJournal._durability(db)
        return db

    @staticmethod
    def _durability(db: sqlite3.Connection) -> None:
        if (db.execute("PRAGMA journal_mode").fetchone()[0] != "wal"
            or db.execute("PRAGMA synchronous").fetchone()[0] != 2
            or db.execute("PRAGMA foreign_keys").fetchone()[0] != 1
            or db.execute("PRAGMA trusted_schema").fetchone()[0] != 0):
            raise PendingRefused("REQUIRED_STORE_POLICY_UNAVAILABLE")

    @contextmanager
    def _transaction(self, db: sqlite3.Connection):
        self._durability(db)
        db.execute("BEGIN IMMEDIATE")
        try:
            if db is self.journal:
                self._schema(db, JOURNAL)
            elif db is self.target:
                self._schema(db, TARGET)
            else:
                raise PendingRefused("STORE_CONNECTION_UNKNOWN")
            yield
            db.execute("COMMIT")
        except BaseException:
            if db.in_transaction:
                db.execute("ROLLBACK")
            raise

    @staticmethod
    def _head(db: sqlite3.Connection, subject: bytes) -> tuple[bytes, bytes] | None:
        row = db.execute("SELECT epoch,run FROM heads WHERE subject=?", (subject,)).fetchone()
        if row is None:
            return None
        return magnitude(row["epoch"]), identity(text(row["run"]))

    def _rows(self, subject: bytes) -> tuple[list[sqlite3.Row], list[Intent]]:
        # Physical append order is retained; no result/epoch sorting or filter.
        rows = self.journal.execute(
            "SELECT intents.*,links.payload AS linked_payload FROM intents "
            "LEFT JOIN links USING(run) WHERE subject=? ORDER BY intents.rowid",
            (subject,)).fetchall()
        typed = []
        for row in rows:
            previous = previous_cursor(row["previous_epoch"], row["previous_run"])
            expected = row_payload(store=self.store, subject=row["subject"],
                                   content=row["content"], requirement=row["requirement"],
                                   run=row["run"], epoch=row["epoch"], previous=previous)
            if row["payload"] != expected or (row["linked_payload"] is not None
                                             and row["linked_payload"] != expected):
                raise PendingRefused("JOURNAL_RECORD_CONFLICT")
            typed.append(Intent(self.store, row["subject"], row["content"], row["run"],
                                row["epoch"], previous, row["linked_payload"] is not None))
        return rows, typed

    def _target_prefix(self, subject: bytes, journal_rows: list[sqlite3.Row]):
        rows = self.target.execute(
            "SELECT pending_history.*,outbox.payload AS outbox_payload "
            "FROM pending_history LEFT JOIN outbox USING(run) WHERE subject=? "
            "ORDER BY pending_history.rowid", (subject,)).fetchall()
        if len(rows) > len(journal_rows):
            raise PendingRefused("TARGET_HISTORY_AHEAD")
        for target, source in zip(rows, journal_rows):
            for field in ("run", "subject", "content", "requirement", "epoch",
                          "previous_epoch", "previous_run", "payload"):
                if target[field] != source[field]:
                    raise PendingRefused("TARGET_HISTORY_CONFLICT")
            if target["outbox_payload"] != source["payload"]:
                raise PendingRefused("TARGET_OUTBOX_CONFLICT")
        head = self._head(self.target, subject)
        expected = None if not rows else (rows[-1]["epoch"], rows[-1]["run"])
        if head != expected:
            raise PendingRefused("TARGET_CURSOR_CONFLICT")
        return head

    def _reserve_locked(self, subject_bytes: bytes, content_bytes: bytes,
                        required: bytes | None) -> tuple[bytes, bytes]:
        """Caller holds self.lock; retain the original journal→target lock order.
        Return only the exact internally allocated run and kernel-accepted epoch.
        """
        with self._transaction(self.journal):
            rows, typed = self._rows(subject_bytes)
            with self._transaction(self.target):
                target = self._target_prefix(subject_bytes, rows)
                authority = self._head(self.journal, subject_bytes)
                proposed = next_proposal(b"" if authority is None else authority[0])
                # Lossless internally allocated identity, not a digest,
                # UUID-sized domain or caller-chosen run. Its epoch is
                # still merely proposed until the Ada relation accepts.
                run = canonical({"kind": "evaluation-run-v1",
                    "storeId": text(self.store), "worldInstance": text(subject_bytes),
                    "worldContentId": text(content_bytes),
                    "epochMagnitudeLE": base64.b64encode(proposed).decode("ascii")})
                plan = self.kernel.decide(typed, store_id=self.store, subject=subject_bytes,
                    content=content_bytes, run=run, authority=authority, target=target,
                    proposed_epoch=proposed, replay=False)
                if plan.reason is not Reason.RESERVE_NEW or plan.epoch != proposed:
                    raise PendingRefused("BEGIN_REFUSED:" + plan.reason.name)
            payload = row_payload(store=self.store, subject=subject_bytes,
                content=content_bytes, requirement=required, run=run, epoch=plan.epoch,
                previous=authority)
            self.journal.execute("INSERT INTO intents VALUES(?,?,?,?,?,?,?,?)",
                (run, subject_bytes, content_bytes, required, plan.epoch,
                 None if authority is None else authority[0],
                 None if authority is None else authority[1], payload))
            self.journal.execute("INSERT INTO heads VALUES(?,?,?) ON CONFLICT(subject) "
                "DO UPDATE SET epoch=excluded.epoch,run=excluded.run",
                (subject_bytes, plan.epoch, run))
        return run, plan.epoch

    def reserve_pending(self, subject: str, content: str,
                        requirement: str | None) -> PendingHandle:
        """Retain an intent only; this handle is not permission to start work.

        The explicit staging API permits a caller to reopen the retained stores
        and discover the same intent before requesting its existing replay path.
        No target pending row, outbox or acknowledgment is written here.
        """
        subject_bytes, content_bytes = identity(subject), identity(content)
        required = None if requirement is None else identity(requirement)
        with self.lock:
            run, epoch = self._reserve_locked(subject_bytes, content_bytes, required)
            return PendingHandle(text(self.store), text(subject_bytes), text(content_bytes),
                                 text(run), int.from_bytes(epoch, "little"))

    def begin(self, subject: str, content: str, requirement: str | None) -> PendingHandle:
        subject_bytes, content_bytes = identity(subject), identity(content)
        required = None if requirement is None else identity(requirement)
        with self.lock:
            run, _epoch = self._reserve_locked(subject_bytes, content_bytes, required)
            # The intent COMMIT precedes every target write, as before. Keep
            # the outer RLock across reservation and exact replay.
            return self.replay(text(run))

    def discover_pending(self) -> tuple[PendingHandle, ...]:
        """Discover retained unlinked intents globally, without changing them.

        Complete per-subject journals and both observed cursors are checked by
        the actual kernel before any handle is returned. Order is exact stored
        subject-byte order; each subject retains its physical journal order.
        These supplied-store observations do not authenticate custody, establish
        rollback resistance or authorize evaluation execution.
        """
        with self.lock, self._transaction(self.journal), self._transaction(self.target):
            subjects = set()
            for db, table in ((self.journal, "intents"),
                              (self.target, "pending_history")):
                for row in db.execute("SELECT subject FROM " + table +
                                      " UNION SELECT subject FROM heads"):
                    value = row["subject"]
                    # Validate storage type/encoding before grouping. This does
                    # not silently coerce a malformed store field into identity.
                    if identity(text(value)) != value:
                        raise PendingRefused("SUBJECT_STORAGE_INVALID")
                    subjects.add(value)
            found = []
            for subject in sorted(subjects):
                rows, typed = self._rows(subject)
                target = self._target_prefix(subject, rows)
                authority = self._head(self.journal, subject)
                if not rows:
                    if authority is not None:
                        raise PendingRefused("EMPTY_HISTORY_CURSOR_CONFLICT")
                    continue
                latest = rows[-1]
                plan = self.kernel.decide(typed, store_id=self.store, subject=subject,
                    content=latest["content"], run=latest["run"], authority=authority,
                    target=target, proposed_epoch=b"", replay=True)
                if plan.reason not in (Reason.WRITE_PENDING, Reason.ACKNOWLEDGE_LINK,
                                       Reason.ALREADY_LINKED):
                    raise PendingRefused("DISCOVERY_REFUSED:" + plan.reason.name)
                if plan.selected < 1 or plan.epoch != latest["epoch"] or \
                        rows[plan.selected - 1]["run"] != latest["run"]:
                    raise PendingRefused("KERNEL_SELECTED_IDENTITY_CONFLICT")
                if plan.reason is not Reason.ALREADY_LINKED:
                    found.append(PendingHandle(text(self.store), text(subject),
                        text(latest["content"]), text(latest["run"]),
                        int.from_bytes(latest["epoch"], "little")))
            return tuple(found)

    def replay(self, validation_id: str) -> PendingHandle:
        run = identity(validation_id)
        with self.lock, self._transaction(self.journal):
            selected = self.journal.execute("SELECT * FROM intents WHERE run=?", (run,)).fetchone()
            if selected is None:
                raise PendingRefused("INTENT_ABSENT")
            subject, content = selected["subject"], selected["content"]
            rows, typed = self._rows(subject)
            authority = self._head(self.journal, subject)
            with self._transaction(self.target):
                target = self._target_prefix(subject, rows)
                plan = self.kernel.decide(typed, store_id=self.store, subject=subject,
                    content=content, run=run, authority=authority, target=target,
                    proposed_epoch=b"", replay=True)
                if plan.reason not in (Reason.WRITE_PENDING, Reason.ACKNOWLEDGE_LINK,
                                       Reason.ALREADY_LINKED):
                    raise PendingRefused("REPLAY_REFUSED:" + plan.reason.name)
                if plan.epoch != selected["epoch"] or plan.selected < 1 or \
                        rows[plan.selected - 1]["run"] != run:
                    raise PendingRefused("KERNEL_SELECTED_IDENTITY_CONFLICT")
                if plan.reason is Reason.WRITE_PENDING:
                    self.target.execute("INSERT INTO pending_history VALUES(?,?,?,?,?,?,?,?)",
                        tuple(selected[field] for field in ("run", "subject", "content",
                            "requirement", "epoch", "previous_epoch", "previous_run", "payload")))
                    self.target.execute("INSERT INTO heads VALUES(?,?,?) ON CONFLICT(subject) "
                        "DO UPDATE SET epoch=excluded.epoch,run=excluded.run",
                        (subject, selected["epoch"], run))
                    self.target.execute("INSERT INTO outbox VALUES(?,?)", (run, selected["payload"]))
                self._target_prefix(subject, rows)
            # Link only after the atomic pending row/cursor/outbox COMMIT.
            # Repeated acknowledgment must be byte-identical, never overwritten.
            link = self.journal.execute("SELECT payload FROM links WHERE run=?", (run,)).fetchone()
            if link is None:
                self.journal.execute("INSERT INTO links VALUES(?,?)", (run, selected["payload"]))
            elif link[0] != selected["payload"]:
                raise PendingRefused("LINK_CONFLICT")
        return PendingHandle(text(self.store), text(subject), text(content), text(run),
                             int.from_bytes(selected["epoch"], "little"))

    def pending_snapshot(self, subject: str) -> dict:
        """Only this unit's pending stream, never invented finalization evidence.
        Completion, finalization and protected current-cursor readers are still
        separate producers. This is not wired to the default selector.
        """
        subject_bytes = identity(subject)
        with self.lock, self._transaction(self.journal), self._transaction(self.target):
            rows, typed = self._rows(subject_bytes)
            target = self._target_prefix(subject_bytes, rows)
            if any(row["linked_payload"] is None for row in rows):
                raise PendingRefused("UNLINKED_INTENT_REQUIRES_REPLAY")
            authority = self._head(self.journal, subject_bytes)
            if rows:
                latest = rows[-1]
                plan = self.kernel.decide(typed, store_id=self.store, subject=subject_bytes,
                    content=latest["content"], run=latest["run"], authority=authority,
                    target=target, proposed_epoch=b"", replay=True)
                if plan.reason is not Reason.ALREADY_LINKED:
                    raise PendingRefused("SNAPSHOT_REFUSED:" + plan.reason.name)
            elif authority is not None:
                raise PendingRefused("EMPTY_HISTORY_CURSOR_CONFLICT")
            history = []
            for row in rows:
                history.append({"worldInstance": text(row["subject"]),
                    "worldContentId": text(row["content"]),
                    "requirementHash": None if row["requirement"] is None else text(row["requirement"]),
                    "validationId": text(row["run"]),
                    "evaluationEpoch": int.from_bytes(row["epoch"], "little"),
                    "evaluationState": "PENDING", "outcome": None,
                    "context": None, "results": []})
            return {"schemaVersion": 1, "finalization": None, "history": history}

    def close(self) -> None:
        with self.lock:
            self.journal.close()
            self.target.close()
