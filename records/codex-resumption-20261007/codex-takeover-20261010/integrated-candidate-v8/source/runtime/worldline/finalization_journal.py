"""Immutable epoch-zero acquisition log and native-guarded finalization storage.

The single log commits start, capture, seal and outbox facts atomically within
this database. A later StateStore acknowledgement is a separate durable step.
Owner-only files and SQLite durability do not establish protected production
custody, a rollback barrier or the truth of an examiner observation.
"""
from __future__ import annotations

import base64
from contextlib import contextmanager
from dataclasses import fields
import os
from pathlib import Path
import sqlite3
import stat
from threading import RLock

from .evaluation_pending import PendingJournal, identity, magnitude
from .evaluation_terminal import bytes_value, value_bytes
from .evaluation_wire import OwnedRecord
from .errors import WorldlineError
from .finalization_values import (StartValue, InputValue, UnsealedResult,
    CaptureValue, ComponentsValue, SealValue, ClassifiedValue, SealedValue)


def _refuse(code):
    raise WorldlineError(code, 'the immutable finalization log could not be validated')


def _fsync_close(fd):
    try:
        os.fsync(fd)
    except BaseException as original:
        try:
            os.close(fd)
        except BaseException as cleanup:
            original.add_note('Finalization descriptor cleanup failed: ' + repr(cleanup))
        raise
    else:
        os.close(fd)


def encode(value):
    """Lossless full-value encoding; neither JSON projection nor digest shortening."""
    def lift(item):
        if type(item) is bytes:
            return ['bytes', base64.b64encode(item).decode('ascii')]
        if isinstance(item, list):
            return ['list', [lift(x) for x in item]]
        if isinstance(item, tuple):
            return ['tuple', [lift(x) for x in item]]
        if isinstance(item, dict):
            if any(not isinstance(key, str) for key in item):
                _refuse('FINALIZATION_OBJECT_KEY_INVALID')
            return ['object', [[key, lift(val)] for key, val in item.items()]]
        if item is None or type(item) in (bool, int, float) or isinstance(item, str):
            return ['scalar', item]
        _refuse('FINALIZATION_VALUE_UNSUPPORTED')
    return value_bytes(lift(value))


def decode(raw):
    def lower(item):
        if type(item) is not list or len(item) != 2 or type(item[0]) is not str:
            _refuse('FINALIZATION_STORAGE_INVALID')
        tag, val = item
        if tag == 'bytes' and type(val) is str:
            try:
                answer = base64.b64decode(val, validate=True)
            except (ValueError, UnicodeError) as exc:
                raise WorldlineError('FINALIZATION_STORAGE_INVALID',
                                     'a byte field is malformed') from exc
            if base64.b64encode(answer).decode('ascii') != val:
                _refuse('FINALIZATION_STORAGE_INVALID')
            return answer
        if tag in ('list', 'tuple') and type(val) is list:
            items = [lower(x) for x in val]
            return items if tag == 'list' else tuple(items)
        if tag == 'object' and type(val) is list:
            result = {}
            for pair in val:
                if (type(pair) is not list or len(pair) != 2
                        or type(pair[0]) is not str or pair[0] in result):
                    _refuse('FINALIZATION_STORAGE_INVALID')
                result[pair[0]] = lower(pair[1])
            return result
        if tag == 'scalar' and (val is None or type(val) in (bool, int, float, str)):
            return val
        _refuse('FINALIZATION_STORAGE_INVALID')
    if type(raw) is not bytes:
        _refuse('FINALIZATION_STORAGE_INVALID')
    result = lower(bytes_value(raw))
    if encode(result) != raw:
        _refuse('FINALIZATION_STORAGE_INVALID')
    return result


ACQUISITIONS_ENCODING = 'worldline-finalization-acquisitions-v1'


def acquisitions_payload(values):
    """Carry complete binary acquisitions inside the unchanged JSON row codec."""
    if type(values) is not list:
        _refuse('FINALIZATION_ACQUISITIONS_INVALID')
    return {'encoding': ACQUISITIONS_ENCODING,
            'payload': base64.b64encode(encode(values)).decode('ascii')}


def payload_acquisitions(value):
    """Decode a versioned full-value envelope or the original JSON-list form.

    Absence is distinct from a present empty list. A malformed envelope never
    falls back to the legacy representation, and legacy values retain their
    original JSON-only domain.
    """
    if value is None:
        return None
    if type(value) is list:
        return bytes_value(value_bytes(value))
    if (type(value) is not dict or set(value) != {'encoding', 'payload'}
            or value['encoding'] != ACQUISITIONS_ENCODING
            or type(value['payload']) is not str):
        _refuse('FINALIZATION_ACQUISITIONS_INVALID')
    try:
        raw = base64.b64decode(value['payload'], validate=True)
    except (ValueError, UnicodeError) as exc:
        raise WorldlineError('FINALIZATION_ACQUISITIONS_INVALID',
                             'the acquisition envelope is malformed') from exc
    if base64.b64encode(raw).decode('ascii') != value['payload']:
        _refuse('FINALIZATION_ACQUISITIONS_INVALID')
    values = decode(raw)
    if type(values) is not list:
        _refuse('FINALIZATION_ACQUISITIONS_INVALID')
    return values


_RECORDS = {kind.__name__: kind for kind in (StartValue, InputValue,
    UnsealedResult, CaptureValue, ComponentsValue, SealValue, ClassifiedValue,
    SealedValue, OwnedRecord)}


def record_bytes(value):
    """Explicit tagged DTO grammar; user lists cannot masquerade as records."""
    def tree(item):
        kind = type(item)
        if kind.__name__ in _RECORDS and _RECORDS[kind.__name__] is kind:
            return ['record', kind.__name__,
                    [[field.name, tree(getattr(item, field.name))] for field in fields(kind)]]
        if isinstance(item, dict):
            if any(not isinstance(key, str) for key in item):
                _refuse('FINALIZATION_OBJECT_KEY_INVALID')
            return ['object', [[key, tree(val)] for key, val in item.items()]]
        if isinstance(item, list):
            return ['list', [tree(val) for val in item]]
        if isinstance(item, tuple):
            return ['tuple', [tree(val) for val in item]]
        return ['atom', item]
    return encode(tree(value))


def bytes_record(raw, kind):
    def restore(item):
        if type(item) is not list or not item or type(item[0]) is not str:
            _refuse('FINALIZATION_RECORD_INVALID')
        if item[0] == 'record' and len(item) == 3:
            name, values = item[1:]
            if type(name) is not str or name not in _RECORDS or type(values) is not list:
                _refuse('FINALIZATION_RECORD_INVALID')
            expected = [field.name for field in fields(_RECORDS[name])]
            if (any(type(pair) is not list or len(pair) != 2 for pair in values)
                    or [pair[0] for pair in values] != expected):
                _refuse('FINALIZATION_RECORD_INVALID')
            return _RECORDS[name](**{key: restore(val) for key, val in values})
        if item[0] in ('list', 'tuple') and len(item) == 2 and type(item[1]) is list:
            answer = [restore(val) for val in item[1]]
            return answer if item[0] == 'list' else tuple(answer)
        if item[0] == 'object' and len(item) == 2 and type(item[1]) is list:
            answer = {}
            for pair in item[1]:
                if (type(pair) is not list or len(pair) != 2 or type(pair[0]) is not str
                        or pair[0] in answer):
                    _refuse('FINALIZATION_RECORD_INVALID')
                answer[pair[0]] = restore(pair[1])
            return answer
        if item[0] == 'atom' and len(item) == 2:
            return item[1]
        _refuse('FINALIZATION_RECORD_INVALID')
    value = restore(decode(raw))
    if type(value) is not kind or record_bytes(value) != raw:
        _refuse('FINALIZATION_RECORD_INVALID')
    return value


SCHEMA = '''
CREATE TABLE identity (singleton INTEGER PRIMARY KEY CHECK(singleton=1), store_id BLOB NOT NULL, role TEXT NOT NULL) STRICT;
CREATE TABLE starts (run BLOB PRIMARY KEY, subject BLOB NOT NULL UNIQUE, payload BLOB NOT NULL) STRICT;
CREATE TABLE execution_claims (run BLOB PRIMARY KEY REFERENCES starts(run), payload BLOB NOT NULL) STRICT;
CREATE TABLE inputs (run BLOB PRIMARY KEY REFERENCES starts(run), payload BLOB NOT NULL) STRICT;
CREATE TABLE observations (run BLOB NOT NULL REFERENCES starts(run), event BLOB NOT NULL, ordinal BLOB NOT NULL, invocation BLOB NOT NULL, phase TEXT NOT NULL, payload BLOB NOT NULL, PRIMARY KEY(run,event), UNIQUE(run,ordinal)) STRICT;
CREATE TABLE captures (run BLOB PRIMARY KEY REFERENCES starts(run), payload BLOB NOT NULL) STRICT;
CREATE TABLE seals (run BLOB PRIMARY KEY REFERENCES captures(run), payload BLOB NOT NULL, summary BLOB NOT NULL) STRICT;
CREATE TABLE outbox (run BLOB PRIMARY KEY REFERENCES seals(run), payload BLOB NOT NULL) STRICT;
CREATE TABLE links (run BLOB PRIMARY KEY REFERENCES outbox(run), payload BLOB NOT NULL) STRICT;
CREATE TABLE interruptions (run BLOB NOT NULL REFERENCES starts(run), event BLOB NOT NULL, payload BLOB NOT NULL, PRIMARY KEY(run,event)) STRICT;
'''


class _FinalizationLog:
    """Private byte storage. The public facade must admit writes through Ada."""
    def __init__(self, path, store_id, *, create=False):
        self.path, self.store_id = Path(path), identity(store_id)
        self.lock = RLock()
        if create:
            fd = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            _fsync_close(fd)
            parent = os.open(self.path.parent, os.O_RDONLY | os.O_DIRECTORY)
            _fsync_close(parent)
        observed = self.path.lstat()
        if (not stat.S_ISREG(observed.st_mode) or observed.st_uid != os.getuid()
                or stat.S_IMODE(observed.st_mode) & 0o077):
            _refuse('FINALIZATION_FILE_INVALID')
        self.file_identity = (observed.st_dev, observed.st_ino)
        self.db = self._connect(self.path)
        try:
            if create:
                self.db.executescript('BEGIN IMMEDIATE;' + SCHEMA)
                self.db.execute('INSERT INTO main.identity VALUES(1,?,?)',
                                (self.store_id, 'finalization-start-seal-v1'))
                self.db.execute('COMMIT')
            self._guard()
        except BaseException as original:
            self._rollback_preserving(original)
            self._close_preserving(self.db, original)
            raise

    @staticmethod
    def _close_preserving(db, original):
        try:
            db.close()
        except BaseException as cleanup:
            original.add_note('Finalization connection cleanup failed: ' + repr(cleanup))

    @classmethod
    def _connect(cls, path):
        db = sqlite3.connect(path, isolation_level=None, check_same_thread=False)
        try:
            db.row_factory = sqlite3.Row
            db.execute('PRAGMA foreign_keys=ON')
            if db.execute('PRAGMA journal_mode=WAL').fetchone()[0] != 'wal':
                _refuse('FINALIZATION_WAL_UNAVAILABLE')
            db.execute('PRAGMA synchronous=FULL')
            db.execute('PRAGMA trusted_schema=OFF')
            PendingJournal._durability(db)
            return db
        except BaseException as original:
            cls._close_preserving(db, original)
            raise

    def _rollback_preserving(self, original):
        try:
            if self.db.in_transaction:
                self.db.execute('ROLLBACK')
        except BaseException as cleanup:
            original.add_note('Finalization rollback failed: ' + repr(cleanup))

    def _guard(self):
        observed = self.path.lstat()
        if (not stat.S_ISREG(observed.st_mode) or observed.st_uid != os.getuid()
                or stat.S_IMODE(observed.st_mode) & 0o077
                or (observed.st_dev, observed.st_ino) != self.file_identity):
            _refuse('FINALIZATION_FILE_CHANGED')
        PendingJournal._durability(self.db)
        namespaces = self.db.execute('PRAGMA database_list').fetchall()
        if (any(row[1] not in ('main', 'temp') for row in namespaces)
                or not any(row[1] == 'main' for row in namespaces)
                or self.db.execute('SELECT name FROM temp.sqlite_schema').fetchone() is not None):
            _refuse('FINALIZATION_NAMESPACE_CONFLICT')
        normalize = lambda sql: ' '.join(sql.strip().removesuffix(';').split())
        expected = {sql.split()[2]: normalize(sql)
                    for sql in SCHEMA.split(';') if sql.strip()}
        actual = {}
        for row in self.db.execute('SELECT type,name,tbl_name,sql FROM main.sqlite_schema'):
            if row['type'] == 'table' and row['name'] in expected:
                actual[row['name']] = normalize(row['sql'])
            elif (row['type'] == 'index' and row['sql'] is None
                    and row['tbl_name'] in expected
                    and row['name'].startswith('sqlite_autoindex_' + row['tbl_name'] + '_')):
                continue
            else:
                _refuse('FINALIZATION_SCHEMA_OBJECT_CONFLICT')
        if actual != expected:
            _refuse('FINALIZATION_SCHEMA_CONFLICT')
        if self.db.execute('PRAGMA main.foreign_key_check').fetchone() is not None:
            _refuse('FINALIZATION_ORPHAN_RECORD')
        identities = self.db.execute('SELECT singleton,store_id,role FROM main.identity').fetchall()
        if (len(identities) != 1
                or tuple(identities[0]) != (1, self.store_id, 'finalization-start-seal-v1')):
            _refuse('FINALIZATION_IDENTITY_MISMATCH')

    @contextmanager
    def _transaction(self):
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                self._guard()
                yield
                self.db.execute('COMMIT')
            except BaseException as original:
                self._rollback_preserving(original)
                raise

    def _start(self, run, subject, payload):
        existing = self.db.execute('SELECT run,subject,payload FROM main.starts WHERE run=? OR subject=?',
                                   (run, subject)).fetchall()
        if existing:
            if len(existing) != 1 or tuple(existing[0]) != (run, subject, payload):
                _refuse('FINALIZATION_START_REPLAY_CONFLICT')
            return
        self.db.execute('INSERT INTO main.starts VALUES(?,?,?)', (run, subject, payload))

    def _require_start(self, run, payload):
        row = self.db.execute('SELECT payload FROM main.starts WHERE run=?', (run,)).fetchone()
        if row is None or row['payload'] != payload:
            _refuse('FINALIZATION_START_MISMATCH')

    def _once(self, table, run, payload):
        # Table names are internal constants, never caller-controlled SQL.
        if table not in ('inputs', 'captures', 'outbox', 'links'):
            _refuse('FINALIZATION_TABLE_INVALID')
        old = self.db.execute('SELECT payload FROM main.' + table + ' WHERE run=?', (run,)).fetchone()
        if old is not None:
            if old['payload'] != payload:
                _refuse('FINALIZATION_IMMUTABLE_REPLAY_CONFLICT')
            return
        self.db.execute('INSERT INTO main.' + table + ' VALUES(?,?)', (run, payload))

    @staticmethod
    def _ordered_events(rows):
        numbered = []
        for row in rows:
            ordinal = magnitude(row['ordinal'])
            if ordinal != row['ordinal']:
                _refuse('FINALIZATION_ORDINAL_INVALID')
            numbered.append((int.from_bytes(ordinal, 'little'), row))
        numbered.sort(key=lambda item: item[0])
        if any(number != position for position, (number, _row) in enumerate(numbered)):
            _refuse('FINALIZATION_OBSERVATION_SEQUENCE_INVALID')
        return tuple(row for _number, row in numbered)

    def _events(self, run):
        rows = self.db.execute('SELECT event,ordinal,invocation,phase,payload FROM main.observations WHERE run=?',
                               (run,)).fetchall()
        return self._ordered_events(rows)

    def _event_count(self, run):
        # Appending needs the validated complete ordinal sequence, not copies
        # of all earlier payload BLOBs. Do not replace this with COUNT or cache
        # the frontier: a malformed or gapped persisted prefix must still refuse.
        rows = self.db.execute('SELECT ordinal FROM main.observations WHERE run=?',
                               (run,)).fetchall()
        return len(self._ordered_events(rows))

    def close(self):
        with self.lock:
            self.db.close()


class FinalizationJournal(_FinalizationLog):
    """Durable native-admitted start, full capture, external seal and outbox."""
    def __init__(self, path, store_id, *, library, create=False):
        from .finalization_kernel import FinalizationKernel
        self.kernel = FinalizationKernel(library)
        super().__init__(path, store_id, create=create)

    def _owned_start(self, start):
        if type(start) is not StartValue or start.store_id != self.store_id:
            _refuse('FINALIZATION_START_STORE_MISMATCH')
        self.kernel.validate_start(start)
        return record_bytes(start)

    def reserve(self, start):
        frozen = self._owned_start(start)
        with self._transaction():
            self._start(start.run, start.subject, frozen)
        # The method returns only after COMMIT has returned under WAL/FULL.
        # This observed acknowledgement precedes the producer's owned effects.
        return start

    def discover(self, subject):
        subject = identity(subject)
        with self._transaction():
            row = self.db.execute('SELECT run,payload FROM main.starts WHERE subject=?',
                                  (subject,)).fetchone()
            if row is None:
                return None
            value = bytes_record(row['payload'], StartValue)
            if value.run != row['run'] or value.subject != subject:
                _refuse('FINALIZATION_START_STORAGE_MISMATCH')
            self._owned_start(value)
            return value

    def record_input(self, start, value):
        frozen = self._owned_start(start)
        self.kernel.validate_input(start, value)
        with self._transaction():
            self._require_start(start.run, frozen)
            self._once('inputs', start.run, record_bytes(value))
        return value

    def claim_execution(self, start):
        """Reserve a single execution before its first owned effect.

        A recovered claim is not evidence that an effect did or did not run.
        Interrupted effectful acquisitions require explicit recovery rather
        than a fresh in-memory writer discarding their retained prefix.
        """
        frozen = self._owned_start(start)
        with self._transaction():
            self._require_start(start.run, frozen)
            if self.db.execute('SELECT run FROM main.execution_claims WHERE run=?',
                               (start.run,)).fetchone() is not None:
                _refuse('FINALIZATION_EXECUTION_ALREADY_CLAIMED')
            if (self.db.execute('SELECT run FROM main.inputs WHERE run=?', (start.run,)).fetchone() is not None
                    or any(row['phase'] != 'capture-header' for row in self._events(start.run))
                    or self.db.execute('SELECT run FROM main.interruptions WHERE run=?', (start.run,)).fetchone() is not None):
                _refuse('FINALIZATION_ACQUISITION_REQUIRES_RECOVERY')
            self.db.execute('INSERT INTO main.execution_claims VALUES(?,?)', (start.run, frozen))
        return start

    def _observe_locked(self, start, event, invocation, phase, payload):
        if (type(event) is not bytes or type(invocation) is not bytes
                or not isinstance(phase, str) or type(payload) is not bytes):
            _refuse('FINALIZATION_OBSERVATION_INVALID')
        old = self.db.execute('SELECT invocation,phase,payload FROM main.observations WHERE run=? AND event=?',
                              (start.run, event)).fetchone()
        if old is not None:
            if tuple(old) != (invocation, phase, payload):
                _refuse('FINALIZATION_OBSERVATION_REPLAY_CONFLICT')
            return
        if self.db.execute('SELECT run FROM main.captures WHERE run=?', (start.run,)).fetchone() is not None:
            _refuse('FINALIZATION_CAPTURE_ALREADY_RETURNED')
        position = self._event_count(start.run)
        ordinal = position.to_bytes((position.bit_length() + 7) // 8, 'little')
        self.db.execute('INSERT INTO main.observations VALUES(?,?,?,?,?,?)',
                        (start.run, event, ordinal, invocation, phase, payload))

    def observe(self, start, event, invocation, phase, observation):
        frozen = self._owned_start(start)
        with self._transaction():
            self._require_start(start.run, frozen)
            self._observe_locked(start, event, invocation, phase, encode(observation))

    def record_result(self, start, event, invocation, result):
        if type(result) is not UnsealedResult or result.start != start:
            _refuse('FINALIZATION_RESULT_START_MISMATCH')
        frozen = self._owned_start(start)
        with self._transaction():
            self._require_start(start.run, frozen)
            self._observe_locked(start, event, invocation, 'result', record_bytes(result))

    def record_interruption(self, start, event, observation):
        frozen, payload = self._owned_start(start), encode(observation)
        if type(event) is not bytes:
            _refuse('FINALIZATION_INTERRUPTION_IDENTITY_INVALID')
        with self._transaction():
            self._require_start(start.run, frozen)
            previous = self.db.execute('SELECT payload FROM main.interruptions WHERE run=? AND event=?',
                                       (start.run, event)).fetchone()
            if previous is None:
                self.db.execute('INSERT INTO main.interruptions VALUES(?,?,?)', (start.run, event, payload))
            elif previous['payload'] != payload:
                _refuse('FINALIZATION_INTERRUPTION_REPLAY_CONFLICT')

    def interruptions(self, subject):
        start = self.discover(subject)
        if start is None:
            return ()
        with self._transaction():
            self._require_start(start.run, record_bytes(start))
            return tuple((row['event'], decode(row['payload'])) for row in self.db.execute(
                'SELECT event,payload FROM main.interruptions WHERE run=? ORDER BY event', (start.run,)))

    def retain_capture(self, value):
        if type(value) is not CaptureValue:
            _refuse('FINALIZATION_CAPTURE_TYPE_INVALID')
        start = value.start
        frozen = self._owned_start(start)
        self.kernel.validate_input(start, value.input)
        # This is an actual fresh native call, never a caller-carried result.
        classification = self.kernel.classify_capture(value)
        with self._transaction():
            self._require_start(start.run, frozen)
            stored_input = self.db.execute('SELECT payload FROM main.inputs WHERE run=?',
                                           (start.run,)).fetchone()
            if stored_input is None or stored_input['payload'] != record_bytes(value.input):
                _refuse('FINALIZATION_INPUT_STORAGE_MISMATCH')
            events = self._events(start.run)
            results = tuple(bytes_record(row['payload'], UnsealedResult)
                            for row in events if row['phase'] == 'result')
            # A final completion proposal is not persisted before its actual
            # native Completed result. All earlier rows must correspond in
            # full, in order, including duplicate check identifiers.
            if value.results == results:
                pass
            elif (classification.state == 'Completed' and value.results and value.results[:-1] == results
                    and value.results[-1].check == value.completion[0]
                    and value.results[-1].declared == value.completion[1]):
                final = value.results[-1]
                self._observe_locked(start, b'finalization-completion:' + start.run,
                                     start.run, 'result', record_bytes(final))
            else:
                _refuse('FINALIZATION_CAPTURE_SEQUENCE_MISMATCH')
            if (classification.state != 'Completed'
                    and any(row.check == value.completion[0] for row in value.results)):
                _refuse('FINALIZATION_ERROR_HAS_COMPLETION')
            self._once('captures', start.run, record_bytes(value))
        return classification

    def _publication(self, sealed, publication):
        from .core import hash_bytes_from_id
        from .model import World, WorldState
        if type(publication) is not dict:
            _refuse('FINALIZATION_PUBLICATION_INVALID')
        record = dict(publication)
        try:
            record['state'] = WorldState(record['state'])
            world = World(**record)
        except (KeyError, TypeError, ValueError) as exc:
            raise WorldlineError('FINALIZATION_PUBLICATION_INVALID', 'full world record is malformed') from exc
        start, value = sealed.value.capture.start, sealed.value
        expected = value.capture.input
        if (identity(world.instance_id) != start.subject
                or identity(world.content_id) != value.content
                or hash_bytes_from_id(world.parent_content) != start.parent
                or hash_bytes_from_id(world.components['filesystem']) != expected.filesystem
                or hash_bytes_from_id(world.components['config']) != expected.config
                or hash_bytes_from_id(world.components['repository']) != expected.repository
                or hash_bytes_from_id(world.components['environment']) != value.components.environment
                or hash_bytes_from_id(world.components['evidence']) != value.components.evidence):
            _refuse('FINALIZATION_PUBLICATION_BINDING_MISMATCH')
        expected_state = ('VALID' if sealed.finalization_state == 'COMPLETED'
                          and sealed.finalization_outcome == 'PASS' else 'DEGRADED')
        if world.state.value != expected_state:
            _refuse('FINALIZATION_PUBLICATION_STATE_MISMATCH')
        return world

    def retain_seal(self, value, publication):
        if type(value) is not SealValue:
            _refuse('FINALIZATION_SEAL_TYPE_INVALID')
        start = value.capture.start
        frozen = self._owned_start(start)
        sealed = self.kernel.seal(value)
        if type(sealed) is not SealedValue or sealed.value != value:
            _refuse('FINALIZATION_NATIVE_SEAL_INVALID')
        self._publication(sealed, publication)
        payload = record_bytes(sealed)
        outbox = encode({'seal': payload, 'publication': publication})
        summary = encode({'subject': start.subject, 'content': value.content,
            'requirement': start.requirement, 'run': start.run, 'epoch': start.epoch,
            'state': sealed.finalization_state, 'outcome': sealed.finalization_outcome})
        with self._transaction():
            self._require_start(start.run, frozen)
            capture = self.db.execute('SELECT payload FROM main.captures WHERE run=?',
                                      (start.run,)).fetchone()
            if capture is None or capture['payload'] != record_bytes(value.capture):
                _refuse('FINALIZATION_CAPTURE_STORAGE_MISMATCH')
            old = self.db.execute('SELECT payload,summary FROM main.seals WHERE run=?',
                                  (start.run,)).fetchone()
            if old is None:
                self.db.execute('INSERT INTO main.seals VALUES(?,?,?)', (start.run, payload, summary))
            elif tuple(old) != (payload, summary):
                _refuse('FINALIZATION_SEAL_REPLAY_CONFLICT')
            # Seal and its discoverable outbox are in the same transaction.
            # No cross-StateStore atomicity is inferred from this commit.
            self._once('outbox', start.run, outbox)
        return sealed

    def retained(self, subject):
        subject = identity(subject)
        with self._transaction():
            found = self.db.execute('SELECT run,payload FROM main.starts WHERE subject=?',
                                   (subject,)).fetchone()
            if found is None:
                return None
            start = bytes_record(found['payload'], StartValue)
            if start.subject != subject or start.run != found['run']:
                _refuse('FINALIZATION_START_STORAGE_MISMATCH')
            self._owned_start(start)
            sealed_row = self.db.execute('SELECT payload,summary FROM main.seals WHERE run=?',
                                        (start.run,)).fetchone()
            if sealed_row is None:
                return start, None, tuple(self._events(start.run))
            sealed = bytes_record(sealed_row['payload'], SealedValue)
            capture = self.db.execute('SELECT payload FROM main.captures WHERE run=?',
                                      (start.run,)).fetchone()
            input_row = self.db.execute('SELECT payload FROM main.inputs WHERE run=?',
                                        (start.run,)).fetchone()
            outbox = self.db.execute('SELECT payload FROM main.outbox WHERE run=?',
                                    (start.run,)).fetchone()
            if (capture is None or input_row is None or outbox is None
                    or record_bytes(sealed.value.capture.start) != found['payload']
                    or capture['payload'] != record_bytes(sealed.value.capture)
                    or input_row['payload'] != record_bytes(sealed.value.capture.input)):
                _refuse('FINALIZATION_RETAINED_CHAIN_INVALID')
            pending = decode(outbox['payload'])
            if (type(pending) is not dict or set(pending) != {'seal', 'publication'}
                    or pending['seal'] != sealed_row['payload']):
                _refuse('FINALIZATION_OUTBOX_INVALID')
            self._publication(sealed, pending['publication'])
            actual = self.kernel.seal(sealed.value)
            if record_bytes(actual) != sealed_row['payload']:
                _refuse('FINALIZATION_RETAINED_NATIVE_MISMATCH')
            summary = {'subject': start.subject, 'content': sealed.value.content,
                'requirement': start.requirement, 'run': start.run, 'epoch': start.epoch,
                'state': actual.finalization_state, 'outcome': actual.finalization_outcome}
            if encode(summary) != sealed_row['summary']:
                _refuse('FINALIZATION_RETAINED_SUMMARY_MISMATCH')
            events = tuple(self._events(start.run))
            results = tuple(bytes_record(row['payload'], UnsealedResult)
                            for row in events if row['phase'] == 'result')
            if results != sealed.value.capture.results:
                _refuse('FINALIZATION_RETAINED_SEQUENCE_MISMATCH')
            return start, actual, events

    def _publication_artifacts(self, world, sealed):
        directory = Path(world.payload_path) / 'manifests'
        if ((directory / 'evidence.json').read_bytes() != sealed.value.evidence
                or (directory / 'environment.json').read_bytes() != sealed.value.environment):
            _refuse('FINALIZATION_PUBLICATION_ARTIFACT_MISMATCH')

    def acknowledge(self, store, subject):
        """Acknowledge an observed committed world, separately from the seal.

        No StateStore transaction is presented as atomic with this journal.
        Repeated acknowledgements compare the immutable full publication.
        """
        with store._lock, self.lock:
            retained = self.retained(subject)
            if retained is None or retained[1] is None:
                _refuse('FINALIZATION_SEAL_ABSENT')
            start, sealed, _events = retained
            outbox = self.db.execute('SELECT payload FROM main.outbox WHERE run=?',
                                     (start.run,)).fetchone()
            pending = decode(outbox['payload'])
            wanted = self._publication(sealed, pending['publication'])
            actual = store.world(subject)
            # Store lifecycle may subsequently advance. Only the exact initial
            # publication can first acquire an acknowledgement; later replay
            # retains that original publication instead of replacing it.
            old = self.db.execute('SELECT payload FROM main.links WHERE run=?',
                                  (start.run,)).fetchone()
            if old is None and actual.record() != wanted.record():
                _refuse('FINALIZATION_PUBLICATION_NOT_COMMITTED')
            if (actual.instance_id != wanted.instance_id
                    or actual.content_id != wanted.content_id
                    or actual.parent_content != wanted.parent_content
                    or actual.components != wanted.components):
                _refuse('FINALIZATION_PUBLICATION_CHANGED')
            self._publication_artifacts(actual, sealed)
            from .finalize import Finalizer
            if old is None:
                # Publication and read-only materialization are separate steps.
                # A crash after StateStore.save_world cannot acquire its first
                # link until the original materialization obligation completes.
                Finalizer._make_readonly(Path(actual.payload_path))
            Finalizer._verify_readonly(Path(actual.payload_path))
            self._publication_artifacts(actual, sealed)
            with self._transaction():
                self._once('links', start.run, outbox['payload'])
            return sealed

    def publication_pending(self, subject):
        with self.lock:
            retained = self.retained(subject)
            if retained is None or retained[1] is None:
                return False
            start = retained[0]
            with self._transaction():
                return self.db.execute('SELECT 1 FROM main.links WHERE run=?',
                                       (start.run,)).fetchone() is None

    def recover(self, store, subject):
        """Finish a retained, native-revalidated outbox without rerunning work."""
        with store._lock, self.lock:
            retained = self.retained(subject)
            if retained is None or retained[1] is None:
                _refuse('FINALIZATION_SEAL_ABSENT')
            start, sealed, _events = retained
            linked = self.db.execute('SELECT 1 FROM main.links WHERE run=?',
                                     (start.run,)).fetchone()
            if linked is not None:
                # Revalidate an existing publication without rolling a later
                # lifecycle transition back to the outbox's initial state.
                self.acknowledge(store, subject)
                return store.world(subject)
            row = self.db.execute('SELECT payload FROM main.outbox WHERE run=?',
                                  (start.run,)).fetchone()
            wanted = self._publication(sealed, decode(row['payload'])['publication'])
            actual = store.world(subject)
            self._publication_artifacts(wanted, sealed)
            if actual.record() != wanted.record():
                from .model import WorldState
                if actual.state is not WorldState.FINALIZING or actual.content_id is not None:
                    _refuse('FINALIZATION_RECOVERY_WORLD_CONFLICT')
                initial = decode(start.base_context)['world']
                # The retained original antecedents, not a caller-selected new
                # world, govern which interrupted StateStore row may advance.
                for field in ('instance_id', 'alias', 'parent_instance', 'parent_content',
                              'cause', 'actor', 'born', 'payload_path', 'mission_hash',
                              'workspace', 'base_payload_path', 'base_root', 'root_set_hash'):
                    if actual.record()[field] != initial[field]:
                        _refuse('FINALIZATION_RECOVERY_ANTECEDENT_CHANGED')
                store.save_world(wanted)
            from .finalize import Finalizer
            Finalizer._make_readonly(Path(wanted.payload_path))
            self.acknowledge(store, subject)
            return store.world(subject)
