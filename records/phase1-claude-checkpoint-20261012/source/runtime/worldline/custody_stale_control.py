"""Selected real precommit SQL refusal; its archive never grants custody.

The unchanged native append decides the full candidate first. A restrictive
SQLite authorizer denies its actual events INSERT before COMMIT. Only a fully
observed rollback permits the unchanged ordinary request append to continue.
The later original stale-CAS control rechecks that full old candidate against
the current native context. No row, native answer, grant or wait is invented.
"""
from __future__ import annotations
import hashlib
import os
from pathlib import Path
import sqlite3
import stat
import sys
import time

from .protected_startup import canonical, exact_json, require
from .root_worker_codec import raw_archive, scoped_archive, scoped_restore_archive

_SELECTED = None


def failure(error):
    return {'module': type(error).__module__, 'type': type(error).__qualname__,
            'message': str(error), 'args': tuple(error.args), 'repr': repr(error),
            'errno': getattr(error, 'errno', None),
            'sqlite_errorcode': getattr(error, 'sqlite_errorcode', None),
            'sqlite_errorname': getattr(error, 'sqlite_errorname', None),
            'notes': tuple(getattr(error, '__notes__', ()))}


def identity(info):
    return {'device': info.st_dev, 'inode': info.st_ino, 'uid': info.st_uid,
            'gid': info.st_gid, 'mode': stat.S_IMODE(info.st_mode), 'links': info.st_nlink}


def journal_binding(journal):
    return {'path': str(journal.path), 'genesis_raw': journal.genesis_raw,
            'issuer_key_sha256': hashlib.sha256(journal.key).hexdigest(),
            'descriptor_raw': journal.descriptor_raw, 'plan_raw': journal.plan_raw,
            'installation': journal.spec['installation_id']}


def enroll_from_source(path, front, output_directory, input_path, timeout):
    global _SELECTED
    from .protected_root_worker import RootWorkerFront
    require(_SELECTED is None and type(front) is RootWorkerFront,
            'STALE_CONTROL_SINGLE_ACTUAL_FRONT_REQUIRED')
    approved = sys.modules.get('_worldline_approved_source_loader')
    require(approved is not None, 'STALE_CONTROL_ACTUAL_SOURCE_LEASE_REQUIRED')
    source = approved.current(); source.check(); front.source_lease.check()
    raw = source.file(str(path), ('DATA',)); plan = exact_json(raw)
    require(type(plan) is dict and set(plan) == {
        'schema', 'journal_path', 'installation_id', 'request_source',
        'request_sha256', 'input_path', 'receipt_path', 'timeout'}
        and plan['schema'] == 'worldline.original-stale-cas-sql-rollback-control-v1',
        'STALE_CONTROL_COMPLETE_SELECTED_PLAN_REQUIRED')
    require(type(timeout) in (int, float) and timeout > 0 and plan['timeout'] == timeout,
            'STALE_CONTROL_ORIGINAL_CASE_TIMEOUT_REQUIRED')
    journal = front.custody_journal; journal.intact()
    require(plan['journal_path'] == str(journal.path)
            and plan['installation_id'] == journal.spec['installation_id']
            and plan['input_path'] == str(input_path),
            'STALE_CONTROL_ACTUAL_OWNER_JOURNAL_OUTPUT_JOIN_REQUIRED')
    payload = source.file(plan['request_source'], ('DATA',))
    require(payload.endswith(b'\n') and hashlib.sha256(payload).hexdigest() == plan['request_sha256'],
            'STALE_CONTROL_EXACT_ORIGINAL_REQUEST_BYTES_REQUIRED')
    output = Path(output_directory)
    targets = [Path(plan[name]) for name in ('input_path', 'receipt_path')]
    require(output.is_absolute() and len(set(targets)) == len(targets)
            and all(p.is_absolute() and p.parent == output for p in targets),
            'STALE_CONTROL_EXACT_CASE_OUTPUT_DIRECTORY_REQUIRED')
    for parent in (*reversed(output.parents), output):
        info = parent.lstat()
        require(stat.S_ISDIR(info.st_mode) and info.st_uid == 0 and not info.st_mode & 0o022,
                'STALE_CONTROL_PROTECTED_OUTPUT_ANCESTRY_REQUIRED')
    require(not output.lstat().st_mode & 0o077 and all(not os.path.lexists(p) for p in targets),
            'STALE_CONTROL_EXCLUSIVE_PRIVATE_OUTPUT_REQUIRED')
    source.check()
    _SELECTED = SqlRollbackProbe(source, str(path), raw, plan, payload, front, journal)


class SqlRollbackProbe:
    def __init__(self, source, path, raw, plan, payload, front, journal):
        self.source, self.path, self.plan_raw, self.plan = source, path, raw, plan
        self.payload, self.front, self.journal = payload, front, journal
        self.binding = journal_binding(journal)
        self.deadline = time.monotonic() + plan['timeout']
        self.used = False; self.inputs = None; self.before = None; self.rows = None
        self.decision = None; self.db = None; self.error = None; self.rolled_back = False
        self.authorizer_calls = []; self.retained = {}; self.outputs = {}

    def selected_intact(self):
        self.source.check()
        require(self.source.file(self.path, ('DATA',)) == self.plan_raw
                and self.source.file(self.plan['request_source'], ('DATA',)) == self.payload,
                'STALE_CONTROL_SELECTED_SOURCE_DATA_CHANGED')

    def intact(self, journal):
        require(_SELECTED is self and journal is self.journal and self.used
                and self.inputs is None and time.monotonic() <= self.deadline,
                'STALE_CONTROL_ACTUAL_SELECTED_PRECOMMIT_PROBE_REQUIRED')
        self.selected_intact(); journal.intact()
        require(journal_binding(journal) == self.binding,
                'STALE_CONTROL_ACTUAL_OWNER_CONTEXT_CHANGED')

    def arm(self, journal, db, inputs, before, decision):
        self.intact(journal)
        require(db.in_transaction and decision.status == 0 and decision.delta is not None
                and decision.inputs == inputs,
                'STALE_CONTROL_NATIVE_FULL_READY_APPLY_REQUIRED')
        self.inputs, self.before, self.decision, self.db = inputs, before, decision, db
        self.rows = journal.capture_rows(db)
        self.retained.update(native_input=inputs, full_before=before,
            native_status=decision.status, native_position=decision.position,
            native_delta=decision.delta, rows_before=self.rows,
            source_at_arm=self.source.check(), journal_binding=self.binding)

        def authorize(action, first, second, database, trigger):
            deny = action == sqlite3.SQLITE_INSERT and first == 'events' and database == 'main'
            answer = sqlite3.SQLITE_DENY if deny else sqlite3.SQLITE_OK
            # Callback records arguments only; it never uses the invoking connection.
            self.authorizer_calls.append({'action': action, 'first': first, 'second': second,
                'database': database, 'trigger': trigger, 'returned': answer})
            return answer

        db.set_authorizer(authorize)

    def record_rollback(self, journal, db, error):
        # This method is entered only after the original append's real rollback.
        self.error = error; self.retained['append_error'] = failure(error)
        require(journal is self.journal and db is self.db and db is not None
                and not db.in_transaction and self.inputs is not None,
                'STALE_CONTROL_ACTUAL_PRECOMMIT_ROLLBACK_REQUIRED')
        db.set_authorizer(None)
        db.execute('BEGIN')
        try:
            after = journal.capture_rows(db)
            require(scoped_archive(after) == scoped_archive(self.rows),
                    'STALE_CONTROL_COMPLETE_ROLLBACK_ROWS_CHANGED')
            self.retained['rows_after_rollback'] = after
        finally:
            db.rollback()
        require(not db.in_transaction, 'STALE_CONTROL_ROLLBACK_READBACK_TRANSACTION_OPEN')
        self.retained['authorizer_calls'] = tuple(self.authorizer_calls)
        self.rolled_back = True

    def finish(self, error):
        require(self.error is error and isinstance(error, sqlite3.DatabaseError)
                and getattr(error, 'sqlite_errorcode', None) == sqlite3.SQLITE_AUTH
                and self.rolled_back
                and any(row['action'] == sqlite3.SQLITE_INSERT and row['first'] == 'events'
                        and row['database'] == 'main' and row['returned'] == sqlite3.SQLITE_DENY
                        for row in self.authorizer_calls),
                'STALE_CONTROL_OBSERVED_SQL_AUTH_REFUSAL_AND_ROLLBACK_REQUIRED')
        self.selected_intact()
        self.retained.update(schema='worldline.original-stale-cas-actual-rollback-v1',
            selected_plan_raw=self.plan_raw, source_after_rollback=self.source.check(),
            commit_attempted=False, phase_acceptance=False)
        # Exact input handed to the actual native mutation, not a reconstructed candidate.
        self._publish('input_path', self.inputs)
        self._publish('receipt_path', raw_archive(self.retained))

    def _publish(self, key, raw):
        path = Path(self.plan[key]); self.source.check()
        require(key not in self.outputs and not os.path.lexists(path),
                'STALE_CONTROL_OUTPUT_ALREADY_EXISTS')
        state = {'path': str(path), 'fd': None, 'raw': raw, 'close_attempted': False,
                 'status': 'CREATION_PENDING'}
        self.outputs[key] = state
        fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
        state['fd'] = fd; state['identity'] = identity(os.fstat(fd)); state['status'] = 'OWNED'
        position = 0
        while position < len(raw):
            require(time.monotonic() <= self.deadline, 'STALE_CONTROL_ORIGINAL_CASE_DEADLINE')
            sent = os.write(fd, raw[position:])
            require(sent > 0, 'STALE_CONTROL_ACTUAL_OUTPUT_WRITE_PROGRESS_REQUIRED')
            position += sent
        os.fsync(fd)
        require(os.pread(fd, len(raw), 0) == raw and os.fstat(fd).st_size == len(raw)
                and identity(path.lstat()) == state['identity'],
                'STALE_CONTROL_COMPLETE_OWNED_OUTPUT_READBACK_REQUIRED')
        state['status'] = 'DURABLE_READBACK'


def probe_request(subject, request, socket_roster):
    probe = _SELECTED
    if probe is None:
        return
    document = request.observation()
    if document['rawRequest'] != probe.payload.hex():
        return
    require(subject.owner is probe.front and subject.journal is probe.journal
            and not probe.used, 'STALE_CONTROL_EXACT_SELECTED_REQUEST_OWNER_REQUIRED')
    probe.selected_intact(); probe.used = True
    from .custody_subject_capture import socket_capture
    source = subject.owner.source_lease.check()
    original = {'original_request': document, 'socket_roster': socket_roster,
                'source_control_plan': probe.plan_raw}
    try:
        subject.append('REQUEST_QUEUED', original, request=document,
            front_socket=socket_capture(request.peer.descriptor(), source), _control_sql_probe=probe)
    except BaseException as error:
        # Suppress only the exact actually observed restrictive SQL failure.
        # Every native/source/commit/readback/cleanup failure remains a refusal.
        try:
            probe.finish(error)
        except BaseException as observation_error:
            probe.retained['export_failure'] = failure(observation_error)
            error.add_note('actual stale-control rollback capture also failed: '+repr(observation_error))
            try:
                emit_retained('append-or-export-refusal')
            except BaseException as stream_error:
                error.add_note('actual stale-control raw retention also failed: '+repr(stream_error))
            raise error
        emit_retained('actual-rollback-and-durable-exports')
        return
    require(False, 'STALE_CONTROL_RESTRICTIVE_SQL_FAILURE_NOT_OBSERVED')


def produced_input(journal, path, input_path):
    from .root_worker_journal_v2 import RootCustodyJournalV2
    probe = _SELECTED
    require(type(probe) is SqlRollbackProbe and type(journal) is RootCustodyJournalV2
            and probe.rolled_back and probe.path == str(path)
            and probe.plan['input_path'] == str(input_path),
            'STALE_CONTROL_ACTUAL_SAME_PROCESS_ROLLBACK_PRODUCER_REQUIRED')
    probe.selected_intact(); journal.intact()
    # A real handoff can reconstruct the current journal. Authenticate its full
    # selected identity rather than borrowing the old front's live authority.
    require(journal_binding(journal) == probe.binding,
            'STALE_CONTROL_CURRENT_JOURNAL_BINDING_CHANGED')
    state = probe.outputs.get('input_path')
    require(type(state) is dict and state['status'] == 'DURABLE_READBACK'
            and not state['close_attempted'] and state['fd'] is not None,
            'STALE_CONTROL_ACTUAL_HELD_INPUT_REQUIRED')
    info = os.fstat(state['fd']); named = Path(state['path']).lstat()
    require(identity(info) == state['identity'] == identity(named)
            and info.st_nlink == 1 and info.st_uid == 0 and stat.S_IMODE(info.st_mode) == 0o600
            and os.pread(state['fd'], len(probe.inputs), 0) == probe.inputs
            and info.st_size == len(probe.inputs),
            'STALE_CONTROL_FULL_ORIGINAL_OWNED_INPUT_CHANGED')
    scoped_restore_archive(probe.inputs)
    return probe.inputs


def close_produced_outputs():
    probe = _SELECTED
    if probe is None:
        return
    errors = []
    for state in probe.outputs.values():
        if state['fd'] is None or state['close_attempted']:
            continue
        try:
            probe.source.check()
            require(identity(os.fstat(state['fd'])) == state['identity'],
                    'STALE_CONTROL_OWNED_OUTPUT_IDENTITY_CHANGED')
            state['close_attempted'] = True; state['status'] = 'UNKNOWN_AFTER_CLOSE_ATTEMPT'
            os.close(state['fd'])
            state['fd'] = None; state['status'] = 'CLOSED_RETURNED_ZERO'
        except BaseException as error:
            state['close_error'] = failure(error); errors.append(error)
    if errors:
        for secondary in errors[1:]:
            errors[0].add_note('additional actual stale-output close failure: '+repr(secondary))
        raise errors[0]


def retained_observation():
    probe = _SELECTED
    if probe is None:
        return None
    # Every retained value is an actual capture, including partial creation and
    # errors. No live connection/function/owner object is serialized as a fact.
    return {'schema': 'worldline.original-stale-cas-partial-custody-v1',
        'selected_plan_raw': probe.plan_raw, 'used': probe.used,
        'native_input': probe.inputs, 'full_before': probe.before,
        'rows_before': probe.rows, 'actual_rollback_readback': probe.rolled_back,
        'actual_append_error': None if probe.error is None else failure(probe.error),
        'authorizer_calls': tuple(probe.authorizer_calls), 'retained': dict(probe.retained),
        'outputs': {name: dict(state) for name, state in probe.outputs.items()},
        'phase_acceptance': False}


def emit_retained(cause):
    observation = retained_observation()
    if observation is None:
        return
    # The original campaign parent owns and retains stderr. Export actual raw
    # capture even when a source-check/write/fsync refuses the selected file.
    # This stream is custody only; it supplies no source permission or success.
    raw = canonical({'schema': 'worldline.original-stale-cas-raw-custody-frame-v1',
        'cause': cause, 'archive_hex': raw_archive(observation).hex()}) + b'\n'
    position = 0
    while position < len(raw):
        sent = os.write(2, raw[position:])
        require(sent > 0, 'STALE_CONTROL_ACTUAL_RAW_CUSTODY_WRITE_PROGRESS_REQUIRED')
        position += sent
    return observation
