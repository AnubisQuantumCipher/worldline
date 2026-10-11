"""Offline explicit-input empty-v2 writer; NOT migration/startup authority.

Never called on ordinary startup. Supplied snapshots/held directory descriptors
must come from a separately qualified operator provisioner. No `closed`, `ready`
or caller-authenticated Boolean substitutes for the still-open native joins.
Partial outputs are retained on failure; retries never replace them.
"""
from __future__ import annotations
from dataclasses import dataclass
import fcntl
import hashlib
import hmac
import os
from pathlib import Path
import sqlite3
import stat
from urllib.parse import quote
from .protected_startup import exact_json, digest, require
from .root_worker_codec import archive

DOMAIN = b'worldline.protected-root-custody-v2\x00'
DDL = "CREATE TABLE genesis (\n  name  TEXT PRIMARY KEY CHECK (name = 'owner-genesis'),\n  value BLOB NOT NULL CHECK (typeof(value) = 'blob'),\n  mac   TEXT NOT NULL CHECK (typeof(mac) = 'text' AND length(mac) = 64)\n);\nCREATE TABLE events (\n  seq           INTEGER PRIMARY KEY,\n  event_id      TEXT NOT NULL UNIQUE CHECK (typeof(event_id) = 'text' AND length(event_id) = 64),\n  previous      TEXT NOT NULL UNIQUE CHECK (typeof(previous) = 'text' AND length(previous) = 64),\n  generation    BLOB NOT NULL CHECK (typeof(generation) = 'blob' AND length(generation) >= 1\n                  AND substr(generation, length(generation), 1) <> x'00'),\n  operation     TEXT NOT NULL CHECK (typeof(operation) = 'text'),\n  subject_kind  TEXT NOT NULL CHECK (subject_kind IN ('ROOT','REQUEST','DESCRIPTOR')),\n  subject       TEXT NOT NULL CHECK (typeof(subject) = 'text'),\n  subgeneration BLOB NOT NULL CHECK (typeof(subgeneration) = 'blob' AND (length(subgeneration) = 0\n                  OR substr(subgeneration, length(subgeneration), 1) <> x'00')),\n  kind          TEXT NOT NULL CHECK (kind IN (\n    'PREPARED','HELD','RUNNING','EXECUTION_NATIVE','EXECUTION_ACK','HANDOFF_INTENT',\n    'FRONT_CLOSE_INTENT','FRONT_CLOSED','TRANSFER_SENT','ROSTER_EVIDENCE','CUSTODY_ACK','ABANDON',\n    'FRONT_RETAINED_ESCROW','HANDOFF_ABORT','ORIGINAL_PROGRESS','ORIGINAL_RESULT','HANDLER_TERMINAL',\n    'WORKER_RELINQUISH','WORKER_REATTACHED','CUSTODY_RETURNED','CLOSED_NS','CLOSED_OUTER','CLOSED_RAW',\n    'CLOSED_WITNESS','PHYSICAL_SETTLED','HISTORICAL_SETTLEMENT','FRONT_RECONSTRUCTION','FRONT_OWNED',\n    'UNKNOWN','RECONCILED',\n    'REQUEST_QUEUED','REQUEST_TRANSFER_INTENT','REQUEST_INTAKE','REQUEST_ABANDON','REQUEST_RESPONDED',\n    'REQUEST_LOST',\n    'DRAIN_STOP_INTENT','DRAIN_FREEZE','DRAIN_OFD_EVIDENCE','DRAIN_INTAKE','DRAIN_ABANDON',\n    'DRAIN_RELEASED','DRAIN_RECLAIMED')),\n  actor         TEXT NOT NULL CHECK (actor IN ('FRONT','WORKER','COLLECTOR','RECONCILER')),\n  record        BLOB NOT NULL CHECK (typeof(record) = 'blob'),\n  base          BLOB NOT NULL CHECK (typeof(base) = 'blob'),\n  mac           TEXT NOT NULL CHECK (typeof(mac) = 'text' AND length(mac) = 64),\n  CHECK ((subject_kind = 'ROOT') = (subject = ''))\n);\nCREATE TABLE alternatives (\n  generation      BLOB NOT NULL CHECK (typeof(generation) = 'blob'),\n  operation       TEXT NOT NULL,\n  subject_kind    TEXT NOT NULL CHECK (subject_kind IN ('ROOT','REQUEST','DESCRIPTOR')),\n  subject         TEXT NOT NULL,\n  subgeneration   BLOB NOT NULL CHECK (typeof(subgeneration) = 'blob'),\n  alternative_set TEXT NOT NULL CHECK (alternative_set IN ('ACK','REQUEST','DRAIN')),\n  event_id        TEXT NOT NULL UNIQUE REFERENCES events(event_id),\n  PRIMARY KEY (generation, operation, subject_kind, subject, subgeneration, alternative_set)\n);\nCREATE TABLE root_state (\n  generation          BLOB PRIMARY KEY CHECK (typeof(generation) = 'blob' AND length(generation) >= 1\n                        AND substr(generation, length(generation), 1) <> x'00'),\n  operation           TEXT NOT NULL CHECK (typeof(operation) = 'text'),\n  phase               TEXT NOT NULL CHECK (phase IN (\n    'FRONT_OWNED','PREPARED','HELD','RUNNING','EXECUTION_NATIVE','EXECUTION_ACK','HANDOFF_INTENT',\n    'FRONT_CLOSE_INTENT','FRONT_CLOSED','TRANSFER_SENT','ROSTER_EVIDENCE','WORKER_OWNED',\n    'ORIGINAL_RESULT','HANDLER_TERMINAL','WORKER_RELINQUISH','ABANDONED','FRONT_RETAINED_ESCROW',\n    'HANDOFF_ABORTED','CUSTODY_RETURNED','HISTORICAL_SETTLEMENT','FRONT_RECONSTRUCTION','ENDED',\n    'UNKNOWN')),\n  before_unknown      TEXT,\n  owners_open         INTEGER NOT NULL CHECK (owners_open IN (0,1)),\n  abort_class         TEXT CHECK (abort_class IS NULL OR abort_class IN ('NEVER_DISPATCHED','DISPATCHED')),\n  launched            INTEGER NOT NULL CHECK (launched IN (0,1)),\n  closure_ns          INTEGER NOT NULL CHECK (closure_ns IN (0,1)),\n  closure_outer       INTEGER NOT NULL CHECK (closure_outer IN (0,1)),\n  closure_raw         INTEGER NOT NULL CHECK (closure_raw IN (0,1)),\n  witness             INTEGER NOT NULL CHECK (witness IN (0,1)),\n  settled             INTEGER NOT NULL CHECK (settled IN (0,1)),\n  released_unlaunched INTEGER NOT NULL CHECK (released_unlaunched IN (0,1)),\n  unknown_cause       TEXT CHECK (unknown_cause IS NULL OR length(unknown_cause) = 64),\n  reattach_epoch      BLOB NOT NULL CHECK (typeof(reattach_epoch) = 'blob' AND (length(reattach_epoch) = 0\n                        OR substr(reattach_epoch, length(reattach_epoch), 1) <> x'00')),\n  head_event          TEXT NOT NULL REFERENCES events(event_id),\n  CHECK ((phase = 'UNKNOWN') = (before_unknown IS NOT NULL)),\n  CHECK (before_unknown IS NULL OR before_unknown NOT IN ('UNKNOWN','ENDED'))\n);\nCREATE TABLE subject_state (\n  generation    BLOB NOT NULL REFERENCES root_state(generation),\n  subject_kind  TEXT NOT NULL CHECK (subject_kind IN ('REQUEST','DESCRIPTOR')),\n  subject       TEXT NOT NULL,\n  subgeneration BLOB NOT NULL CHECK (typeof(subgeneration) = 'blob' AND (length(subgeneration) = 0\n                  OR substr(subgeneration, length(subgeneration), 1) <> x'00')),\n  phase         TEXT NOT NULL,\n  mode          TEXT NOT NULL CHECK (mode IN ('NONE','FRESH','RELAY')),\n  position      BLOB CHECK (position IS NULL OR (typeof(position) = 'blob' AND (length(position) = 0\n                  OR substr(position, length(position), 1) <> x'00'))),\n  carried_from  BLOB CHECK (carried_from IS NULL OR (typeof(carried_from) = 'blob' AND length(carried_from) >= 1\n                  AND substr(carried_from, length(carried_from), 1) <> x'00')),\n  head_event    TEXT NOT NULL REFERENCES events(event_id),\n  PRIMARY KEY (generation, subject_kind, subject),\n  CHECK ((subject_kind = 'REQUEST' AND phase IN\n           ('QUEUED','TRANSFER_INTENT','INTAKE','ABANDONED','RESPONDED','LOST'))\n      OR (subject_kind = 'DESCRIPTOR' AND phase IN\n           ('FRONT_HELD','STOP_INTENT','FROZEN','OFD_EVIDENCE','INTAKE','ABANDONED','RELEASED','RECLAIMED')))\n);\nCREATE TABLE blobs (\n  sha256 TEXT PRIMARY KEY CHECK (length(sha256) = 64),\n  kind   TEXT NOT NULL CHECK (kind IN ('RAW_OBSERVATION','SPOOL_CHUNK','CAPTURE','RESPONSE')),\n  bytes  BLOB NOT NULL\n);\nCREATE TABLE head (\n  name      TEXT PRIMARY KEY CHECK (name = 'current'),\n  head_kind TEXT NOT NULL CHECK (head_kind IN ('ORIGIN','EVENT')),\n  event_id  TEXT REFERENCES events(event_id),\n  origin    TEXT CHECK (origin IS NULL OR length(origin) = 64),\n  mac       TEXT NOT NULL CHECK (length(mac) = 64),\n  CHECK ((head_kind = 'ORIGIN' AND event_id IS NULL AND origin IS NOT NULL)\n      OR (head_kind = 'EVENT' AND event_id IS NOT NULL AND origin IS NULL))\n);"
STATEMENTS = tuple(part.strip() for part in DDL.split(';') if part.strip())
TABLES = tuple(statement.split()[2] for statement in STATEMENTS)
GENESIS_KEYS = frozenset(('schema', 'installation', 'startup_descriptor_sha256',
                        'owner_plan_sha256', 'issuer_key_sha256', 'initial_event', 'prior_custody'))

@dataclass(frozen=True)
class Target:
    # Caller retains custody of directory_fd for the entire call. A basename
    # selects the new file; the writer never follows an output symlink.
    directory_fd: int
    name: str

@dataclass(frozen=True)
class ExplicitInputs:
    descriptor_raw: bytes
    plan_raw: bytes
    genesis_raw: bytes
    key: bytes

@dataclass(frozen=True)
class WrittenArtifacts:
    genesis_sha256: str
    journal_sha256: str
    origin: str
    # This is a production/readback receipt, never authorization or X5 status.
    state: str = 'EMPTY_V2_WRITTEN_SOURCE_AND_MIGRATION_AUTHORITY_OPEN'


def _mac(key, value):
    return hmac.new(key, DOMAIN + archive(value), hashlib.sha256).hexdigest()


def _prepare(inputs):
    require(type(inputs) is ExplicitInputs and all(type(value) is bytes for value in
            (inputs.descriptor_raw, inputs.plan_raw, inputs.genesis_raw, inputs.key)),
            'CUSTODY_V2_EXPLICIT_BYTES_REQUIRED')
    descriptor = exact_json(inputs.descriptor_raw)
    plan = exact_json(inputs.plan_raw)
    genesis = exact_json(inputs.genesis_raw)
    require(type(descriptor) is dict and type(plan) is dict and
            type(genesis) is dict and set(genesis) == GENESIS_KEYS,
            'CUSTODY_V2_EXPLICIT_GENESIS_SHAPE')
    require(genesis['schema'] == 'worldline.owner-provisioned-root-custody-v2' and
            genesis['initial_event'] is None and
            genesis['installation'] == descriptor['installation_id'] == plan['installation'] and
            plan.get('schema') == 'worldline.protected-root-worker-plan-v1' and
            genesis['startup_descriptor_sha256'] == digest(inputs.descriptor_raw) and
            genesis['owner_plan_sha256'] == digest(inputs.plan_raw) and
            genesis['issuer_key_sha256'] == digest(inputs.key),
            'CUSTODY_V2_EXPLICIT_GENESIS_BINDINGS')
    # prior_custody is retained exactly. This low-level writer cannot decide
    # absence of an old installation or closed-v1 eligibility from these bytes.
    # It intentionally offers no deploy/start/migrate entrypoint.
    row = archive(genesis)
    origin = digest(row)
    genesis_mac = _mac(inputs.key, {'genesis': genesis})
    head_mac = _mac(inputs.key, {'head_kind': 'ORIGIN', 'head': origin, 'genesis': genesis})
    return row, origin, genesis_mac, head_mac


def _target_identity(target):
    require(type(target) is Target and type(target.directory_fd) is int and
            type(target.name) is str and target.name not in ('', '.', '..') and
            '/' not in target.name and '\x00' not in target.name,
            'CUSTODY_V2_EXACT_TARGET_REQUIRED')
    info = os.fstat(target.directory_fd)
    require(stat.S_ISDIR(info.st_mode) and info.st_uid == os.geteuid() and
            not (info.st_mode & (stat.S_IWGRP | stat.S_IWOTH)),
            'CUSTODY_V2_OWNED_PRIVATE_DIRECTORY_REQUIRED')
    return info.st_dev, info.st_ino, target.name


def _plan_target(target, word):
    require(type(word) is str and Path(word).is_absolute() and Path(word).name == target.name,
            'CUSTODY_V2_PLAN_TARGET_DIFFERS')
    named = os.stat(Path(word).parent, follow_symlinks=False)
    held = os.fstat(target.directory_fd)
    require(stat.S_ISDIR(named.st_mode) and (named.st_dev, named.st_ino) ==
            (held.st_dev, held.st_ino), 'CUSTODY_V2_PLAN_DIRECTORY_DIFFERS')


def _absent(target):
    try:
        os.stat(target.name, dir_fd=target.directory_fd, follow_symlinks=False)
    except FileNotFoundError:
        return
    raise FileExistsError('CUSTODY_V2_EXCLUSIVE_TARGET_EXISTS: ' + target.name)


def _same_file(target, fd):
    opened = os.fstat(fd)
    named = os.stat(target.name, dir_fd=target.directory_fd, follow_symlinks=False)
    require(stat.S_ISREG(named.st_mode) and (opened.st_dev, opened.st_ino) ==
            (named.st_dev, named.st_ino), 'CUSTODY_V2_CREATED_FILE_REPLACED')


def _write(fd, raw):
    remaining = memoryview(raw)
    while remaining:
        written = os.write(fd, remaining)
        require(written > 0, 'CUSTODY_V2_SHORT_WRITE')
        remaining = remaining[written:]
    os.fsync(fd)


def _uri(target, mode):
    # Directory FD pins the lookup root; the final component was exclusively
    # created and is rechecked against its still-open FD around SQLite use.
    return 'file:/proc/self/fd/' + str(target.directory_fd) + '/' + quote(target.name, safe='') + '?mode=' + mode


def _verify(db, row, origin, genesis_mac, head_mac):
    require(tuple(db.execute('PRAGMA foreign_keys')) == ((1,),), 'CUSTODY_V2_FK_NOT_ON')
    schema = tuple(db.execute("SELECT type,name,sql FROM sqlite_master WHERE name NOT LIKE 'sqlite_%' ORDER BY rowid"))
    require(schema == tuple(('table', name, sql) for name, sql in zip(TABLES, STATEMENTS)),
            'CUSTODY_V2_COMPLETE_DDL_READBACK')
    require(tuple(db.execute('SELECT name,value,mac FROM genesis')) ==
            (('owner-genesis', row, genesis_mac),), 'CUSTODY_V2_GENESIS_READBACK')
    require(tuple(db.execute('SELECT name,head_kind,event_id,origin,mac FROM head')) ==
            (('current', 'ORIGIN', None, origin, head_mac),), 'CUSTODY_V2_HEAD_READBACK')
    for table in ('events', 'alternatives', 'root_state', 'subject_state', 'blobs'):
        require(tuple(db.execute('SELECT * FROM ' + table)) == (), 'CUSTODY_V2_NONEMPTY_INITIAL_ROWS')
    require(tuple(db.execute('PRAGMA foreign_key_check')) == (), 'CUSTODY_V2_FOREIGN_KEY_READBACK')
    require(tuple(db.execute('PRAGMA integrity_check')) == (('ok',),), 'CUSTODY_V2_INTEGRITY_READBACK')


def write_empty_artifacts(inputs, journal, genesis, lock):
    """Durably create exact empty artifacts from EXPLICIT value inputs only.

    Caller must supply already-held authentic directory FDs, bind these targets
    to its original plan paths, and obtain offline provisioning authorization.
    This API does not certify those prerequisites or infer migration safety.
    Existing and partial files are never removed, replaced or re-genesised.
    """
    row, origin, genesis_mac, head_mac = _prepare(inputs)
    targets = (journal, genesis, lock)
    identities = tuple(_target_identity(target) for target in targets)
    plan = exact_json(inputs.plan_raw)
    _plan_target(journal, plan['handoff_journal'])
    _plan_target(genesis, plan['handoff_genesis'])
    require(len(set(identities)) == len(identities), 'CUSTODY_V2_TARGET_ALIAS')
    require(identities[2][:2] == identities[0][:2] and lock.name == journal.name + '.lock',
            'CUSTODY_V2_LOCK_PATH_DIFFERS')
    sidecars = tuple(Target(journal.directory_fd, journal.name + suffix)
                     for suffix in ('-journal', '-wal', '-shm'))
    require(not any(_target_identity(target) in identities for target in sidecars),
            'CUSTODY_V2_SQLITE_SIDECAR_ALIAS')
    for target in targets + sidecars:
        _absent(target)
    opened = []
    try:
        # Reserve the lock first and hold its OFD throughout readback/fsync.
        for target in (lock, journal, genesis):
            fd = os.open(target.name, os.O_RDWR | os.O_CREAT | os.O_EXCL |
                         os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=target.directory_fd)
            opened.append((target, fd))
            if target is lock:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            os.fsync(target.directory_fd)
        fds = {target: fd for target, fd in opened}
        _write(fds[genesis], inputs.genesis_raw)
        os.fsync(fds[lock])
        _same_file(journal, fds[journal])
        db = sqlite3.connect(_uri(journal, 'rw'), uri=True, isolation_level=None)
        try:
            db.execute('PRAGMA trusted_schema=OFF')
            db.execute('PRAGMA foreign_keys=ON')
            require(tuple(db.execute('PRAGMA journal_mode=DELETE')) == (('delete',),),
                    'CUSTODY_V2_JOURNAL_MODE')
            db.execute('PRAGMA synchronous=FULL')
            db.execute('BEGIN IMMEDIATE')
            for statement in STATEMENTS:
                db.execute(statement)
            db.execute('INSERT INTO genesis VALUES (?,?,?)', ('owner-genesis', row, genesis_mac))
            db.execute('INSERT INTO head VALUES (?,?,?,?,?)', ('current', 'ORIGIN', None, origin, head_mac))
            _verify(db, row, origin, genesis_mac, head_mac)
            db.commit()
        except BaseException:
            if db.in_transaction:
                db.rollback()
            raise
        finally:
            db.close()
        _same_file(journal, fds[journal])
        db = sqlite3.connect(_uri(journal, 'ro'), uri=True, isolation_level=None)
        try:
            db.execute('PRAGMA trusted_schema=OFF'); db.execute('PRAGMA query_only=ON')
            db.execute('PRAGMA foreign_keys=ON'); db.execute('BEGIN')
            _verify(db, row, origin, genesis_mac, head_mac)
            db.rollback()
        finally:
            db.close()
        for target, fd in opened:
            _same_file(target, fd)
            os.fsync(fd)
            os.fsync(target.directory_fd)
        # Hash the actual retained inode, not an independently resolved path.
        os.lseek(fds[journal], 0, os.SEEK_SET)
        with os.fdopen(os.dup(fds[journal]), 'rb') as source:
            journal_digest = hashlib.file_digest(source, 'sha256').hexdigest()
        return WrittenArtifacts(digest(inputs.genesis_raw), journal_digest, origin)
    finally:
        # On any failure, all exclusively-created files remain for inspection.
        for target, fd in reversed(opened):
            os.close(fd)
