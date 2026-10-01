"""Explicit private terminal journal, target/history and outbox dependency.

This module is additive and is not selected by default promotion. Full captured
bytes and successful Ada decisions do not certify capture provenance, policy,
roster truth, protected cursors, custody, anti-rollback, or durable deployment.
An older terminal observation is committed before reconciliation of a newer
journal-only pending intent. It remains discoverable if reconciliation refuses.
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
import struct
from threading import RLock

from .completion_kernel import (BoundValue, CaptureValue, CheckValue, CompletionKernel,
                                HistoryValue, EXECUTION, OUTCOME)
from .evaluation_pending import PendingJournal, PendingRefused, identity, text, magnitude, canonical
from .pending_kernel_v2 import Reason

class TerminalRefused(PendingRefused):
    pass

# Lossless observation encoding. This is a reversible storage format, not a
# provenance signature or JSON grammar proof. Arbitrary host integers are stored
# as magnitude bytes; decimal digit limits never become epoch/value caps.
def _b64(value: bytes) -> str:
    if type(value) is not bytes:
        raise TerminalRefused('CAPTURE_BYTES_REQUIRED')
    return base64.b64encode(value).decode('ascii')

def _unb64(value: str) -> bytes:
    if type(value) is not str:
        raise TerminalRefused('CAPTURE_STORAGE_INVALID')
    try:
        result = base64.b64decode(value, validate=True)
    except (ValueError, UnicodeError) as exc:
        raise TerminalRefused('CAPTURE_STORAGE_INVALID') from exc
    if _b64(result) != value:
        raise TerminalRefused('CAPTURE_STORAGE_INVALID')
    return result

def value_bytes(value) -> bytes:
    def encode(item):
        if item is None: return ['null']
        if type(item) is bool: return ['bool', item]
        if isinstance(item, str): return ['str', _b64(identity(item))]
        if type(item) is int:
            value = abs(item)
            return ['int', item < 0, _b64(value.to_bytes((value.bit_length() + 7) // 8, 'little'))]
        if type(item) is float: return ['float', _b64(struct.pack('!d', item))]
        if isinstance(item, (list, tuple)): return ['array', [encode(x) for x in item]]
        if isinstance(item, dict):
            if any(not isinstance(key, str) for key in item):
                raise TerminalRefused('CAPTURE_OBJECT_KEY_INVALID')
            return ['object', [[_b64(identity(key)), encode(val)] for key, val in item.items()]]
        raise TerminalRefused('CAPTURE_VALUE_UNSUPPORTED')
    return canonical(encode(value))

def bytes_value(raw: bytes):
    def decode(item):
        if type(item) is not list or not item or type(item[0]) is not str:
            raise TerminalRefused('CAPTURE_STORAGE_INVALID')
        tag = item[0]
        if tag == 'null' and len(item) == 1: return None
        if tag == 'bool' and len(item) == 2 and type(item[1]) is bool: return item[1]
        if tag == 'str' and len(item) == 2: return text(_unb64(item[1]))
        if tag == 'int' and len(item) == 3 and type(item[1]) is bool:
            blob = magnitude(_unb64(item[2])); val = int.from_bytes(blob, 'little')
            if item[1] and val == 0: raise TerminalRefused('CAPTURE_STORAGE_INVALID')
            return -val if item[1] else val
        if tag == 'float' and len(item) == 2:
            blob = _unb64(item[1])
            if len(blob) != struct.calcsize('!d'): raise TerminalRefused('CAPTURE_STORAGE_INVALID')
            return struct.unpack('!d', blob)[0]
        if tag == 'array' and len(item) == 2 and type(item[1]) is list:
            return [decode(x) for x in item[1]]
        if tag == 'object' and len(item) == 2 and type(item[1]) is list:
            answer = {}
            for pair in item[1]:
                if type(pair) is not list or len(pair) != 2: raise TerminalRefused('CAPTURE_STORAGE_INVALID')
                key = text(_unb64(pair[0]))
                if key in answer: raise TerminalRefused('CAPTURE_STORAGE_INVALID')
                answer[key] = decode(pair[1])
            return answer
        raise TerminalRefused('CAPTURE_STORAGE_INVALID')
    if type(raw) is not bytes: raise TerminalRefused('CAPTURE_STORAGE_INVALID')
    try:
        encoded = json.loads(raw)
        if canonical(encoded) != raw: raise TerminalRefused('CAPTURE_STORAGE_INVALID')
        return decode(encoded)
    except (ValueError, UnicodeError) as exc:
        raise TerminalRefused('CAPTURE_STORAGE_INVALID') from exc

def _binding(bound):
    return [_b64(bound.store_id), _b64(bound.subject), _b64(bound.content),
            _b64(bound.run), _b64(magnitude(bound.epoch)),
            None if bound.requirement is None else _b64(bound.requirement)]

def _decode_binding(raw):
    if type(raw) is not list or len(raw) != 6: raise TerminalRefused('TERMINAL_STORAGE_INVALID')
    fields = [_unb64(x) for x in raw[:5]]
    magnitude(fields[4])
    return BoundValue(*fields, None if raw[5] is None else _unb64(raw[5]))

def payload(capture: CaptureValue, results) -> bytes:
    return canonical({'schemaVersion': 1, 'capture': [_binding(capture.bound),
        _b64(capture.source), _b64(capture.context), capture.state, capture.outcome],
        'results': [[_binding(row.bound), _b64(row.check), _b64(row.source),
                     None if row.execution is None else _b64(row.execution),
                     None if row.verifier is None else _b64(row.verifier),
                     row.state, row.outcome, _b64(row.payload), None if row.observations is None else list(row.observations), row.report, None if row.evidence is None else list(row.evidence), _b64(row.declared)] for row in results]})

def decode_payload(raw: bytes):
    if type(raw) is not bytes: raise TerminalRefused('TERMINAL_STORAGE_INVALID')
    try:
        value = json.loads(raw)
        if type(value) is not dict or set(value) != {'schemaVersion', 'capture', 'results'} \
                or type(value['schemaVersion']) is not int or value['schemaVersion'] != 1:
            raise TerminalRefused('TERMINAL_STORAGE_INVALID')
        c = value['capture']
        if type(c) is not list or len(c) != 5 or c[3] not in EXECUTION or c[4] not in OUTCOME:
            raise TerminalRefused('TERMINAL_STORAGE_INVALID')
        capture = CaptureValue(_decode_binding(c[0]), _unb64(c[1]), _unb64(c[2]), c[3], c[4])
        if type(value['results']) is not list: raise TerminalRefused('TERMINAL_STORAGE_INVALID')
        results = []
        for row in value['results']:
            if type(row) is not list or len(row) != 12 or row[5] not in EXECUTION or row[6] not in OUTCOME:
                raise TerminalRefused('TERMINAL_STORAGE_INVALID')
            if (row[8] is not None and (type(row[8]) is not list or any(type(x) is not int for x in row[8]))) or \
                    row[9] not in ('NOT_APPLICABLE', 'VERIFIED', 'UNTRUSTED') or \
                    (row[10] is not None and (type(row[10]) is not list or any(type(x) is not bool for x in row[10]))):
                raise TerminalRefused('TERMINAL_STORAGE_INVALID')
            results.append(CheckValue(_decode_binding(row[0]), _unb64(row[1]), _unb64(row[2]),
                None if row[3] is None else _unb64(row[3]), None if row[4] is None else _unb64(row[4]),
                row[5], row[6], _unb64(row[7]), None if row[8] is None else tuple(row[8]), row[9], None if row[10] is None else tuple(row[10]), _unb64(row[11])))
        frozen = tuple(results)
        if payload(capture, frozen) != raw: raise TerminalRefused('TERMINAL_STORAGE_INVALID')
        return capture, frozen
    except (ValueError, UnicodeError, TypeError) as exc:
        raise TerminalRefused('TERMINAL_STORAGE_INVALID') from exc

COMMON = 'CREATE TABLE identity (singleton INTEGER PRIMARY KEY CHECK(singleton=1), store_id BLOB NOT NULL, role TEXT NOT NULL) STRICT;'
JOURNAL = '''CREATE TABLE terminal_intents (run BLOB PRIMARY KEY, subject BLOB NOT NULL, payload BLOB NOT NULL) STRICT;
CREATE TABLE terminal_links (run BLOB PRIMARY KEY REFERENCES terminal_intents(run), payload BLOB NOT NULL) STRICT;
CREATE TABLE capture_streams (run BLOB PRIMARY KEY, subject BLOB NOT NULL, payload BLOB NOT NULL) STRICT;
CREATE TABLE invocation_starts (run BLOB NOT NULL REFERENCES capture_streams(run), invocation BLOB NOT NULL, payload BLOB NOT NULL, PRIMARY KEY(run,invocation)) STRICT;
CREATE TABLE invocation_results (run BLOB NOT NULL, invocation BLOB NOT NULL, payload BLOB NOT NULL, PRIMARY KEY(run,invocation), FOREIGN KEY(run,invocation) REFERENCES invocation_starts(run,invocation)) STRICT;'''
RAW_CAPTURE = 'CREATE TABLE invocation_observations (run BLOB NOT NULL, invocation BLOB NOT NULL, kind TEXT NOT NULL, payload BLOB NOT NULL, PRIMARY KEY(run,invocation,kind), FOREIGN KEY(run,invocation) REFERENCES invocation_starts(run,invocation)) STRICT;'
RAW_OCCURRENCES = 'CREATE TABLE invocation_acquisitions (run BLOB NOT NULL, invocation BLOB NOT NULL, kind TEXT NOT NULL, occurrence BLOB NOT NULL, payload BLOB NOT NULL, PRIMARY KEY(run,invocation,kind,occurrence), FOREIGN KEY(run,invocation) REFERENCES invocation_starts(run,invocation)) STRICT;'
TARGET = '''CREATE TABLE terminal_history (run BLOB PRIMARY KEY, subject BLOB NOT NULL, payload BLOB NOT NULL, summary BLOB NOT NULL) STRICT;
CREATE TABLE terminal_outbox (run BLOB PRIMARY KEY REFERENCES terminal_history(run), payload BLOB NOT NULL, summary BLOB NOT NULL) STRICT;'''

@dataclass(frozen=True)
class TerminalHandle:
    run: str
    subject: str
    epoch: int

class TerminalJournal:
    def __init__(self, pending: PendingJournal, journal: Path, target: Path, *, library: Path, create=False):
        self.pending = pending
        self.kernel = CompletionKernel(library)
        self.lock = RLock()
        paths = [pending.journal_path, pending.target_path, Path(journal), Path(target)]
        if len({p.resolve() for p in paths}) != len(paths): raise TerminalRefused('TERMINAL_STORES_NOT_DISTINCT')
        if create:
            for path in paths[-2:]:
                fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
                try: os.fsync(fd)
                finally: os.close(fd)
                parent = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
                try: os.fsync(parent)
                finally: os.close(parent)
        infos = [path.lstat() for path in paths]
        if any(not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() for info in infos):
            raise TerminalRefused('TERMINAL_FILE_INVALID')
        if len({(info.st_dev, info.st_ino) for info in infos}) != len(infos):
            raise TerminalRefused('TERMINAL_STORES_NOT_DISTINCT')
        self.journal = pending._connect(paths[-2]); self.target = pending._connect(paths[-1])
        if create:
            for db, role, schema in ((self.journal, 'journal', JOURNAL), (self.target, 'target', TARGET)):
                db.executescript('BEGIN IMMEDIATE;' + COMMON + schema)
                try:
                    db.execute('INSERT INTO main.identity VALUES(1,?,?)', (pending.store, role))
                    db.execute('COMMIT')
                except BaseException:
                    if db.in_transaction: db.execute('ROLLBACK')
                    raise
        self._guard(self.journal, 'journal'); self._guard(self.target, 'target')

    @staticmethod
    def _namespaces(db):
        databases = db.execute('PRAGMA database_list').fetchall()
        if any(row[1] not in ('main', 'temp') for row in databases) \
                or not any(row[1] == 'main' for row in databases):
            raise TerminalRefused('STORE_ATTACHED_DATABASE_UNEXPECTED')
        if db.execute('SELECT name FROM temp.sqlite_schema').fetchone() is not None:
            raise TerminalRefused('STORE_TEMP_SCHEMA_UNEXPECTED')

    def _guard(self, db, role):
        self._namespaces(db); self.pending._durability(db)
        if role not in ('journal', 'target'): raise TerminalRefused('TERMINAL_ROLE_INVALID')
        schema = JOURNAL if role == 'journal' else TARGET
        normal = lambda sql: ' '.join(sql.strip().removesuffix(';').split())
        expected = {stmt.split()[2]: normal(stmt) for stmt in (COMMON + schema).split(';') if stmt.strip()}
        extended = {**expected, 'invocation_observations': normal(RAW_CAPTURE)} if role == 'journal' else expected
        occurrences = {**extended, 'invocation_acquisitions': normal(RAW_OCCURRENCES)} if role == 'journal' else extended
        found = {}
        for row in db.execute('SELECT type,name,tbl_name,sql FROM main.sqlite_schema ORDER BY type,name'):
            if row['type'] == 'table' and row['name'] in occurrences:
                found[row['name']] = normal(row['sql'])
            elif (row['type'] == 'index' and row['sql'] is None and row['tbl_name'] in occurrences
                  and row['name'].startswith('sqlite_autoindex_' + row['tbl_name'] + '_')):
                continue
            else: raise TerminalRefused('TERMINAL_SCHEMA_OBJECT_CONFLICT')
        if found != expected and found != extended and found != occurrences:
            raise TerminalRefused('TERMINAL_SCHEMA_CONFLICT')
        if role == 'journal' and found == occurrences:
            # The original table is retained, not rewritten. Every historical
            # acquisition must remain exactly mirrored in the ordered extension.
            missing = db.execute('SELECT legacy.run FROM main.invocation_observations AS legacy '
                'LEFT JOIN main.invocation_acquisitions AS acquired '
                'ON acquired.run=legacy.run AND acquired.invocation=legacy.invocation AND acquired.kind=legacy.kind '
                'AND acquired.occurrence=? WHERE acquired.payload IS NULL OR acquired.payload!=legacy.payload LIMIT 1',
                (value_bytes(None),)).fetchone()
            if missing is not None:
                raise TerminalRefused('RAW_CAPTURE_LEGACY_MIRROR_CONFLICT')
        if db.execute('PRAGMA main.foreign_key_check').fetchone() is not None:
            raise TerminalRefused('TERMINAL_ORPHAN_RECORD')
        rows = db.execute('SELECT singleton,store_id,role FROM main.identity').fetchall()
        if len(rows) != 1 or tuple(rows[0]) != (1, self.pending.store, role):
            raise TerminalRefused('TERMINAL_IDENTITY_MISMATCH')

    @contextmanager
    def _transaction(self, db, role):
        db.execute('BEGIN IMMEDIATE')
        try:
            self._guard(db, role)
            yield
            db.execute('COMMIT')
        except BaseException:
            if db.in_transaction: db.execute('ROLLBACK')
            raise

    @contextmanager
    def _pending_view(self, subject):
        # Stable acquisition order throughout this adapter: pending lock,
        # adapter lock, pending journal, pending target, terminal journal/target.
        self._namespaces(self.pending.journal); self._namespaces(self.pending.target)
        with self.pending._transaction(self.pending.journal), self.pending._transaction(self.pending.target):
            rows, typed = self.pending._rows(subject)
            self.pending._target_prefix(subject, rows)
            current = self.pending._head(self.pending.journal, subject)
            if rows:
                latest = rows[-1]
                plan = self.pending.kernel.decide(typed, store_id=self.pending.store,
                    subject=subject, content=latest['content'], run=latest['run'],
                    authority=current, target=self.pending._head(self.pending.target, subject),
                    proposed_epoch=b'', replay=True, requirement=latest['requirement'])
                if (plan.reason not in (Reason.WRITE_PENDING, Reason.ACKNOWLEDGE_LINK, Reason.ALREADY_LINKED)
                    or plan.selected < 1 or rows[plan.selected - 1]['run'] != latest['run']
                    or plan.epoch != latest['epoch'] or plan.requirement != latest['requirement']):
                    raise TerminalRefused('PENDING_VIEW_REFUSED')
            elif current is not None:
                raise TerminalRefused('PENDING_VIEW_CURSOR_CONFLICT')
            yield rows, typed, current

    @staticmethod
    def _admitted(plan, rows, run):
        if plan.reason not in ('Retain_Terminal', 'Already_Retained'):
            raise TerminalRefused('COMPLETION_REFUSED:' + plan.reason)
        if plan.selected < 1 or plan.selected > len(rows) or rows[plan.selected - 1]['run'] != run:
            raise TerminalRefused('COMPLETION_SELECTED_IDENTITY_CONFLICT')

    def _intent(self, run):
        row = self.journal.execute('SELECT * FROM main.terminal_intents WHERE run=?', (run,)).fetchone()
        if row is None: return None
        capture, results = decode_payload(row['payload'])
        if capture.bound.run != row['run'] or capture.bound.subject != row['subject']:
            raise TerminalRefused('TERMINAL_INTENT_IDENTITY_CONFLICT')
        link = self.journal.execute('SELECT payload FROM main.terminal_links WHERE run=?', (run,)).fetchone()
        if link is not None and link[0] != row['payload']: raise TerminalRefused('TERMINAL_LINK_CONFLICT')
        return row, capture, results

    def retain(self, capture: CaptureValue, results) -> TerminalHandle:
        """Commit the immutable observation before any reconciliation target work.

        This is a retained observation, not a completed-publication receipt. Use
        replay/discover for target/outbox acknowledgment. No capture flags are
        accepted as authenticated evidence; the actual kernel binds identities.
        """
        immutable = tuple(results); raw = payload(capture, immutable)
        with self.pending.lock, self.lock, self._pending_view(capture.bound.subject) as (rows, typed, current):
            with self._transaction(self.journal, 'journal'):
                old = self._intent(capture.bound.run)
                plan = self.kernel.decide(typed, current=current, capture=capture, results=immutable,
                    retained=None if old is None else old[1], retained_results=() if old is None else old[2])
                self._admitted(plan, rows, capture.bound.run)
                if old is None:
                    self.journal.execute('INSERT INTO main.terminal_intents VALUES(?,?,?)',
                                         (capture.bound.run, capture.bound.subject, raw))
                elif old[0]['payload'] != raw:
                    raise TerminalRefused('TERMINAL_REPLAY_BYTES_CONFLICT')
        return TerminalHandle(text(capture.bound.run), text(capture.bound.subject), int.from_bytes(capture.bound.epoch, 'little'))

    @staticmethod
    def _pending_row(row):
        return HistoryValue(row['subject'], row['content'], row['requirement'], row['run'], row['epoch'], 'PENDING', None)

    @staticmethod
    def _summary_bytes(summary):
        return canonical([None if value is None else _b64(value) for value in
                          (summary.subject, summary.content, summary.requirement, summary.run, summary.epoch)]
                         + [summary.state, summary.outcome])

    def _history(self, rows):
        for link in self.journal.execute('SELECT run,payload FROM main.terminal_links'):
            target = self.target.execute('SELECT payload FROM main.terminal_history WHERE run=?', (link['run'],)).fetchone()
            if target is None or target[0] != link['payload']:
                raise TerminalRefused('TERMINAL_ACK_WITHOUT_MATCHED_TARGET')
        by_run = {row['run']: row for row in rows}
        stored = {}
        for row in self.target.execute('SELECT terminal_history.*,terminal_outbox.payload AS out_payload, '
                'terminal_outbox.summary AS out_summary FROM main.terminal_history '
                'LEFT JOIN main.terminal_outbox USING(run) ORDER BY terminal_history.rowid'):
            old = self._intent(row['run'])
            if old is None or old[0]['payload'] != row['payload'] or old[0]['subject'] != row['subject'] \
                    or row['out_payload'] != row['payload'] or row['out_summary'] != row['summary']:
                raise TerminalRefused('TERMINAL_TARGET_CONFLICT')
            capture = old[1]
            summary = HistoryValue(capture.bound.subject, capture.bound.content, capture.bound.requirement,
                capture.bound.run, capture.bound.epoch, 'COMPLETED' if capture.state == 'Completed' else 'ERROR', capture.outcome)
            # Stored summary must be the exact prior kernel result, not a changed
            # display projection. Every result is checked again by Apply below.
            if row['summary'] != self._summary_bytes(summary): raise TerminalRefused('TERMINAL_SUMMARY_CONFLICT')
            if row['run'] in by_run:
                source = by_run[row['run']]
                if source['linked_payload'] is None: raise TerminalRefused('TERMINAL_PENDING_NOT_LINKED')
                if (summary.subject, summary.content, summary.requirement, summary.epoch) != \
                        (source['subject'], source['content'], source['requirement'], source['epoch']):
                    raise TerminalRefused('TERMINAL_PENDING_BINDING_CONFLICT')
                stored[row['run']] = (summary, old[1], old[2])
            elif rows and row['subject'] == rows[0]['subject']:
                raise TerminalRefused('TERMINAL_RUN_MISSING_FROM_PENDING')
        return [stored[row['run']][0] if row['run'] in stored else self._pending_row(row) for row in rows], stored

    def replay(self, validation_id: str) -> TerminalHandle:
        run = identity(validation_id)
        with self.pending.lock, self.lock:
            with self._transaction(self.journal, 'journal'):
                old = self._intent(run)
                if old is None: raise TerminalRefused('TERMINAL_INTENT_ABSENT')
                subject = old[1].bound.subject
            # A legitimate Reserved head is reconciled using the existing exact
            # pending protocol. If this fails the terminal intent above persists.
            with self._pending_view(subject) as (rows, _typed, _current):
                todo = [text(row['run']) for row in rows if row['linked_payload'] is None]
            for pending_run in todo: self.pending.replay(pending_run)
            with self._pending_view(subject) as (rows, typed, current):
                if any(row['linked_payload'] is None for row in rows):
                    raise TerminalRefused('TERMINAL_PENDING_RECONCILIATION_REQUIRED')
                with self._transaction(self.journal, 'journal'):
                    old = self._intent(run)
                    if old is None: raise TerminalRefused('TERMINAL_INTENT_ABSENT')
                    record, capture, results = old
                    with self._transaction(self.target, 'target'):
                        history, stored = self._history(rows)
                        past = stored.get(run)
                        plan = self.kernel.decide(typed, current=current, capture=capture, results=results,
                            retained=None if past is None else past[1], retained_results=() if past is None else past[2], history=history)
                        self._admitted(plan, rows, run)
                        if plan.summary is None: raise TerminalRefused('COMPLETION_SUMMARY_ABSENT')
                        summary = self._summary_bytes(plan.summary)
                        if past is None:
                            self.target.execute('INSERT INTO main.terminal_history VALUES(?,?,?,?)',
                                                (run, subject, record['payload'], summary))
                            self.target.execute('INSERT INTO main.terminal_outbox VALUES(?,?,?)', (run, record['payload'], summary))
                        else:
                            actual = self.target.execute('SELECT payload,summary FROM main.terminal_history WHERE run=?', (run,)).fetchone()
                            if tuple(actual) != (record['payload'], summary): raise TerminalRefused('TERMINAL_TARGET_CONFLICT')
                    # Target history+outbox COMMIT completed. Only now acknowledge.
                    link = self.journal.execute('SELECT payload FROM main.terminal_links WHERE run=?', (run,)).fetchone()
                    if link is None:
                        self.journal.execute('INSERT INTO main.terminal_links VALUES(?,?)', (run, record['payload']))
                    elif link[0] != record['payload']: raise TerminalRefused('TERMINAL_LINK_CONFLICT')
            return TerminalHandle(text(run), text(subject), int.from_bytes(capture.bound.epoch, 'little'))

    def complete(self, capture: CaptureValue, results) -> TerminalHandle:
        handle = self.retain(capture, results)
        return self.replay(handle.run)

    def discover(self) -> tuple[TerminalHandle, ...]:
        """Validate and enumerate all unacknowledged captures without a handle.
        Discovery neither fabricates target rows nor erases a refused observation.
        """
        with self.pending.lock, self.lock:
            with self._transaction(self.journal, 'journal'):
                runs = [row[0] for row in self.journal.execute('SELECT run FROM main.terminal_intents ORDER BY rowid')]
            found = []
            for run in runs:
                with self._transaction(self.journal, 'journal'):
                    old = self._intent(run)
                    subject = old[1].bound.subject
                with self._pending_view(subject) as (rows, typed, current), self._transaction(self.journal, 'journal'):
                    old = self._intent(run)
                    plan = self.kernel.decide(typed, current=current, capture=old[1], results=old[2], retained=old[1], retained_results=old[2])
                    self._admitted(plan, rows, run)
                    if self.journal.execute('SELECT run FROM main.terminal_links WHERE run=?', (run,)).fetchone() is None:
                        found.append(TerminalHandle(text(run), text(subject), int.from_bytes(old[1].bound.epoch, 'little')))
            return tuple(found)

    def snapshot(self, subject: str) -> dict:
        """Stable full history for the explicit cursor selector, never default.
        No list filtering, head rewrite, synthetic pending row or old-PASS lookup.
        """
        encoded = identity(subject)
        with self.pending.lock, self.lock, self._pending_view(encoded) as (rows, typed, current):
            if any(row['linked_payload'] is None for row in rows):
                raise TerminalRefused('TERMINAL_PENDING_RECONCILIATION_REQUIRED')
            with self._transaction(self.journal, 'journal'), self._transaction(self.target, 'target'):
                history, stored = self._history(rows)
                for run, (_summary, capture, results) in stored.items():
                    plan = self.kernel.decide(typed, current=current, capture=capture, results=results,
                                             retained=capture, retained_results=results, history=history)
                    self._admitted(plan, rows, run)
                    if self.journal.execute('SELECT run FROM main.terminal_links WHERE run=?', (run,)).fetchone() is None:
                        raise TerminalRefused('TERMINAL_ACKNOWLEDGMENT_PENDING')
                answer = []
                for row, summary in zip(rows, history):
                    terminal = stored.get(row['run'])
                    answer.append({'worldInstance': text(summary.subject), 'worldContentId': text(summary.content),
                        'requirementHash': None if summary.requirement is None else text(summary.requirement),
                        'validationId': text(summary.run), 'evaluationEpoch': int.from_bytes(summary.epoch, 'little'),
                        'evaluationState': summary.state, 'outcome': summary.outcome,
                        'context': None if terminal is None else bytes_value(terminal[1].context),
                        # D15: incomplete/error observations remain available but
                        # are never projected as completed evaluation results.
                        'results': [] if terminal is None or summary.state != 'COMPLETED'
                            else [bytes_value(item.payload) for item in terminal[2]],
                        'partialResults': [bytes_value(item.payload) for item in terminal[2]]
                            if terminal is not None and summary.state == 'ERROR' else []})
                return {'schemaVersion': 1, 'finalization': None, 'history': answer}

    def select_at_cursor(self, subject, content, requirement, *, current, prepared, core):
        """Explicit pure consumer of this stable full snapshot. Cursors must be
        supplied independently; they are never synthesized from a selected row.
        This does not authorize effects or replace the default collapse gates.
        """
        from .evaluation_history import EvaluationRecord, EvaluationQuery, select_history
        snapshot = self.snapshot(subject)
        records = tuple(EvaluationRecord(row['worldInstance'], row['worldContentId'],
            row['requirementHash'], row['validationId'], row['evaluationEpoch'],
            row['evaluationState'], row['outcome']) for row in snapshot['history'])
        decision = select_history(records, None,
            EvaluationQuery(subject, content, requirement, current, prepared), core=core)
        if decision.reason != 'READY':
            raise TerminalRefused('TERMINAL_EVIDENCE_REFUSED:' + decision.reason)
        if decision.head.kind != 'HISTORY_ENTRY' or decision.head.index is None:
            raise TerminalRefused('TERMINAL_EVIDENCE_REFERENCE_INVALID')
        # Return the full same entry. Consumers still apply original context,
        # raw roster, policy, protection and promotion gates to these bytes.
        return snapshot['history'][decision.head.index]

    def open_stream(self, bound: BoundValue, source: bytes, context: bytes):
        raw = canonical({'binding': _binding(bound), 'source': _b64(source), 'context': _b64(context)})
        with self.pending.lock, self.lock, self._pending_view(bound.subject) as (rows, typed, current):
            capture = CaptureValue(bound, source, context, 'Incomplete_Unknown', None)
            plan = self.kernel.decide(typed, current=current, capture=capture, results=())
            self._admitted(plan, rows, bound.run)
            with self._transaction(self.journal, 'journal'):
                old = self.journal.execute('SELECT subject,payload FROM main.capture_streams WHERE run=?', (bound.run,)).fetchone()
                if old is None:
                    self.journal.execute('INSERT INTO main.capture_streams VALUES(?,?,?)', (bound.run, bound.subject, raw))
                elif tuple(old) != (bound.subject, raw): raise TerminalRefused('CAPTURE_STREAM_CONFLICT')

    def observe_start(self, bound, invocation: str, observed: dict):
        self._observe(bound, invocation, observed, result=False)

    def observe_result(self, bound, invocation: str, observed: dict):
        self._observe(bound, invocation, observed, result=True)

    def _observe(self, bound, invocation, observed, *, result):
        key, raw = identity(invocation), value_bytes(observed)
        with self.pending.lock, self.lock, self._pending_view(bound.subject) as (rows, typed, current):
            with self._transaction(self.journal, 'journal'):
                stream = self.journal.execute('SELECT subject,payload FROM main.capture_streams WHERE run=?', (bound.run,)).fetchone()
                if stream is None or stream['subject'] != bound.subject: raise TerminalRefused('CAPTURE_STREAM_ABSENT')
                header = json.loads(stream['payload'])
                if canonical(header) != stream['payload'] or _decode_binding(header['binding']) != bound:
                    raise TerminalRefused('CAPTURE_STREAM_BINDING_CONFLICT')
                capture = CaptureValue(bound, _unb64(header['source']), _unb64(header['context']), 'Incomplete_Unknown', None)
                plan = self.kernel.decide(typed, current=current, capture=capture, results=())
                self._admitted(plan, rows, bound.run)
                if self._intent(bound.run) is not None: raise TerminalRefused('TERMINAL_STREAM_ALREADY_CLOSED')
                if result and self.journal.execute('SELECT invocation FROM main.invocation_starts WHERE run=? AND invocation=?', (bound.run, key)).fetchone() is None:
                    raise TerminalRefused('INVOCATION_START_ABSENT')
                table = 'invocation_results' if result else 'invocation_starts'
                old = self.journal.execute('SELECT payload FROM main.' + table + ' WHERE run=? AND invocation=?', (bound.run, key)).fetchone()
                if old is None:
                    self.journal.execute('INSERT INTO main.' + table + ' VALUES(?,?,?)', (bound.run, key, raw))
                elif old[0] != raw: raise TerminalRefused('INVOCATION_OBSERVATION_CONFLICT')

    def enable_raw_capture(self):
        """Explicit idempotent extension of the exact prior private schema.

        This is reached only by the retained writer, before it allocates an
        attempt. All recognized complete schema shapes are checked, including
        identity and foreign keys. No original row is rewritten or inferred.
        """
        with self.pending.lock, self.lock, self._transaction(self.journal, 'journal'):
            present = self.journal.execute("SELECT name FROM main.sqlite_schema WHERE type='table' AND name='invocation_observations'").fetchone()
            if present is None:
                self.journal.execute(RAW_CAPTURE)
            if self.journal.execute("SELECT name FROM main.sqlite_schema WHERE type='table' AND name='invocation_acquisitions'").fetchone() is None:
                self.journal.execute(RAW_OCCURRENCES)
                for row in self.journal.execute('SELECT run,invocation,kind,payload FROM main.invocation_observations ORDER BY rowid').fetchall():
                    self.journal.execute('INSERT INTO main.invocation_acquisitions VALUES(?,?,?,?,?)',
                        (row['run'], row['invocation'], row['kind'], value_bytes(None), row['payload']))
            self._guard(self.journal, 'journal')

    def observe_raw(self, bound, invocation: str, kind: str, observed, *, occurrence=None):
        """Retain one acquired observation under an existing exact invocation.
        Closed names describe acquisition sites, not verdicts or trusted facts.
        Exact repeats are idempotent; conflicting observations are never replaced.
        """
        kinds = {
            'legacy-process-return', 'legacy-process-exception', 'legacy-report',
            'private-process-return', 'private-report-binding', 'private-report',
            'private-collection-exception', 'invocation-exception',
            'legacy-supervision-acquisition', 'private-supervision-acquisition',
        }
        if kind not in kinds: raise TerminalRefused('RAW_CAPTURE_KIND_INVALID')
        if occurrence is not None and (type(occurrence) is not int or occurrence < 0):
            raise TerminalRefused('RAW_CAPTURE_OCCURRENCE_INVALID')
        occurrence_bytes = value_bytes(occurrence)
        key, raw = identity(invocation), value_bytes(observed)
        with self.pending.lock, self.lock, self._pending_view(bound.subject) as (rows, typed, current):
            with self._transaction(self.journal, 'journal'):
                stream = self.journal.execute('SELECT subject,payload FROM main.capture_streams WHERE run=?', (bound.run,)).fetchone()
                if stream is None or stream['subject'] != bound.subject:
                    raise TerminalRefused('CAPTURE_STREAM_ABSENT')
                header = json.loads(stream['payload'])
                if canonical(header) != stream['payload'] or _decode_binding(header['binding']) != bound:
                    raise TerminalRefused('CAPTURE_STREAM_BINDING_CONFLICT')
                capture = CaptureValue(bound, _unb64(header['source']), _unb64(header['context']), 'Incomplete_Unknown', None)
                plan = self.kernel.decide(typed, current=current, capture=capture, results=())
                self._admitted(plan, rows, bound.run)
                if self._intent(bound.run) is not None:
                    raise TerminalRefused('TERMINAL_STREAM_ALREADY_CLOSED')
                if self.journal.execute('SELECT invocation FROM main.invocation_starts WHERE run=? AND invocation=?', (bound.run, key)).fetchone() is None:
                    raise TerminalRefused('INVOCATION_START_ABSENT')
                extended = self.journal.execute("SELECT name FROM main.sqlite_schema WHERE type='table' AND name='invocation_acquisitions'").fetchone() is not None
                if extended:
                    old = self.journal.execute('SELECT payload FROM main.invocation_acquisitions WHERE run=? AND invocation=? AND kind=? AND occurrence=?',
                        (bound.run, key, kind, occurrence_bytes)).fetchone()
                    if old is None:
                        self.journal.execute('INSERT INTO main.invocation_acquisitions VALUES(?,?,?,?,?)',
                            (bound.run, key, kind, occurrence_bytes, raw))
                    elif old[0] != raw:
                        raise TerminalRefused('INVOCATION_RAW_OBSERVATION_CONFLICT')
                else:
                    # Exact prior API/schema remains usable for singleton sites;
                    # an ordinal cannot silently collapse into a legacy key.
                    if occurrence is not None:
                        raise TerminalRefused('RAW_CAPTURE_OCCURRENCE_SCHEMA_REQUIRED')
                    old = self.journal.execute('SELECT payload FROM main.invocation_observations WHERE run=? AND invocation=? AND kind=?', (bound.run, key, kind)).fetchone()
                    if old is None:
                        self.journal.execute('INSERT INTO main.invocation_observations VALUES(?,?,?,?)', (bound.run, key, kind, raw))
                    elif old[0] != raw:
                        raise TerminalRefused('INVOCATION_RAW_OBSERVATION_CONFLICT')

    def captured_observations(self, bound):
        """Compatibility projection; full occurrence identities remain stored."""
        return tuple((invocation, kind, value) for invocation, kind, _occurrence, value
                     in self.captured_observation_events(bound))

    def captured_observation_events(self, bound):
        """Return complete retained acquisition identities in actual append order."""
        with self.pending.lock, self.lock, self._transaction(self.journal, 'journal'):
            stream = self.journal.execute('SELECT payload FROM main.capture_streams WHERE run=?', (bound.run,)).fetchone()
            if stream is None: raise TerminalRefused('CAPTURE_STREAM_ABSENT')
            header = json.loads(stream[0])
            if canonical(header) != stream[0] or _decode_binding(header['binding']) != bound:
                raise TerminalRefused('CAPTURE_STREAM_BINDING_CONFLICT')
            # A prior exact terminal schema contains no raw acquisition table.
            # The explicit writer enables it before starting any new attempt.
            if self.journal.execute("SELECT name FROM main.sqlite_schema WHERE type='table' AND name='invocation_observations'").fetchone() is None:
                return ()
            if self.journal.execute("SELECT name FROM main.sqlite_schema WHERE type='table' AND name='invocation_acquisitions'").fetchone() is not None:
                rows = self.journal.execute('SELECT invocation,kind,occurrence,payload FROM main.invocation_acquisitions WHERE run=? ORDER BY rowid', (bound.run,)).fetchall()
                answer = []
                for row in rows:
                    occurrence = bytes_value(row['occurrence'])
                    if occurrence is not None and (type(occurrence) is not int or occurrence < 0):
                        raise TerminalRefused('RAW_CAPTURE_OCCURRENCE_INVALID')
                    answer.append((text(row['invocation']), row['kind'], occurrence, bytes_value(row['payload'])))
                return tuple(answer)
            rows = self.journal.execute('SELECT invocation,kind,payload FROM main.invocation_observations WHERE run=? ORDER BY rowid', (bound.run,)).fetchall()
            return tuple((text(row['invocation']), row['kind'], None, bytes_value(row['payload'])) for row in rows)

    def captured_stream(self, bound):
        with self.pending.lock, self.lock, self._transaction(self.journal, 'journal'):
            header = self.journal.execute('SELECT payload FROM main.capture_streams WHERE run=?', (bound.run,)).fetchone()
            if header is None: raise TerminalRefused('CAPTURE_STREAM_ABSENT')
            raw = json.loads(header[0])
            if canonical(raw) != header[0] or _decode_binding(raw['binding']) != bound:
                raise TerminalRefused('CAPTURE_STREAM_BINDING_CONFLICT')
            rows = self.journal.execute('SELECT invocation_starts.invocation,invocation_starts.payload AS started,invocation_results.payload AS finished '
                'FROM main.invocation_starts LEFT JOIN main.invocation_results USING(run,invocation) '
                'WHERE run=? ORDER BY invocation_starts.rowid', (bound.run,)).fetchall()
            return bytes_value(_unb64(raw['context'])), tuple((text(row['invocation']), bytes_value(row['started']),
                None if row['finished'] is None else bytes_value(row['finished'])) for row in rows)

    def close(self):
        with self.lock: self.journal.close(); self.target.close()
