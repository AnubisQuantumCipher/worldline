"""Existing-only complete custody-v2 loader, original v1 remains read-only migration input."""
from __future__ import annotations
import fcntl
import os
from pathlib import Path
import sqlite3
import stat
from threading import RLock
from urllib.parse import quote
from .protected_startup import require, protected, private_bytes, exact_json, digest
from .root_worker_custody import named_identity
from .root_worker_codec import (scoped_archive as archive, scoped_restore_archive as restore_archive,
                                raw_archive, raw_restore_archive)
from .custody_v2_provision_values import STATEMENTS, TABLES, GENESIS_KEYS
from .custody_v2_provision_entry import PRIOR_KEYS, PLAN_KEYS
from .retained_v1_migration_capture import RetainedContext, capture_retained_v1, shared_identity
from .custody_load_kernel import envelope, decide_journal

_SQL_TABLES = {'events': 'events', 'heads': 'head', 'roots': 'root_state',
               'subjects': 'subject_state', 'alternatives': 'alternatives', 'blobs': 'blobs'}
class RootCustodyJournalV2:
    def __init__(self, owner, *, preheld=None):
        from .protected_startup import StartupLease
        from .protected_root_worker import RootWorkerFront, RootWorkerIntake, RootWorkerProcess
        require(type(owner) in (StartupLease, RootWorkerFront, RootWorkerIntake, RootWorkerProcess),
                'CUSTODY_V2_SELECTED_ACTUAL_OWNER_REQUIRED')
        self.owner = owner; self.closed = False; self.poisoned = False
        self.lock = RLock(); self.prior = None
        self.source_lease = owner.source_lease; self.spec = owner.spec
        self.source = self.source_lease
        self.plan = owner.plan; self.plan_raw = owner.plan_raw; self.descriptor_raw = owner.descriptor_raw
        require(type(self.plan) is dict and set(self.plan) == PLAN_KEYS, 'CUSTODY_V2_COMPLETE_PLAN_REQUIRED')
        self.path = Path(self.plan['handoff_journal']); self.genesis_path = Path(self.plan['handoff_genesis'])
        self.lock_path = Path(str(self.path) + '.lock')
        self.genesis_raw = private_bytes(self.genesis_path)
        require(self.source.file(str(self.genesis_path), ('DATA',)) == self.genesis_raw,
                'CUSTODY_V2_GENESIS_DATA_BINDING')
        self.genesis = exact_json(self.genesis_raw)
        require(type(self.genesis) is dict and set(self.genesis) == GENESIS_KEYS and
                self.genesis['schema'] == 'worldline.owner-provisioned-root-custody-v2' and
                self.genesis['installation'] == self.spec['installation_id'] and
                self.genesis['startup_descriptor_sha256'] == digest(self.descriptor_raw) and
                self.genesis['owner_plan_sha256'] == digest(self.plan_raw), 'CUSTODY_V2_SELECTED_GENESIS_CONTEXT')
        self.key_path = Path(self.spec['paths']['authority_root']) / 'authority/issuer/state/issuer-key.bin'
        self.key = private_bytes(self.key_path)
        require(digest(self.key) == self.genesis['issuer_key_sha256'], 'CUSTODY_V2_EXISTING_KEY_CHANGED')
        require({str(self.path), str(self.genesis_path), str(self.lock_path)} <= set(self.spec['provisioned_state']),
                'CUSTODY_V2_FULL_EXISTING_ROSTER_REQUIRED')
        self.file_identity = protected(self.path); protected(self.lock_path)
        from .root_worker_current_state import warm_operation_context_sources
        warm_operation_context_sources()
        from .root_worker_root_evidence import capture_lock_call
        self.lock_open_receipts = {}
        self.lock_duplicate_receipts = {}
        self.lock_flock_receipts = {}
        flags = os.O_RDWR | os.O_NOFOLLOW | os.O_CLOEXEC
        receipts = self.lock_open_receipts if preheld is None else self.lock_duplicate_receipts
        call = 'open' if preheld is None else 'dup'
        args = {'path': str(self.lock_path), 'flags': flags} if preheld is None else {'fd': preheld}
        action = (lambda: os.open(self.lock_path, flags)) if preheld is None else (lambda: os.dup(preheld))
        try:
            self.lock_fd, receipt = capture_lock_call(self.source, call, args, action)
        except BaseException as error:
            receipt = getattr(error, 'custody_lock_receipt', None)
            if receipt is not None:
                receipts[str(self.lock_path)] = receipt
            raise
        receipts[str(self.lock_path)] = receipt
        try:
            named_identity(self.lock_fd, self.lock_path)
            try:
                result, receipt = capture_lock_call(self.source, 'flock',
                    {'fd': self.lock_fd, 'operation': fcntl.LOCK_EX | fcntl.LOCK_NB},
                    lambda: fcntl.flock(self.lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB))
            except BaseException as error:
                receipt = getattr(error, 'custody_lock_receipt', None)
                if receipt is not None:
                    self.lock_flock_receipts[str(self.lock_path)] = receipt
                raise
            self.lock_flock_receipts[str(self.lock_path)] = receipt
            prior = self.genesis['prior_custody']
            if prior is not None:
                require(type(prior) is dict and set(prior) == PRIOR_KEYS, 'CUSTODY_V2_RETAINED_PRIOR_KEYSET')
                self.prior = capture_retained_v1(self.source,
                    RetainedContext(**prior, installation=self.spec['installation_id']))
                for path, expected in ((prior['descriptor_path'], prior['descriptor_sha256']),
                                       (prior['plan_path'], prior['plan_sha256']),
                                       (prior['genesis_path'], prior['genesis_sha256']),
                                       (prior['journal_path'], prior['journal_sha256'])):
                    require(self.spec['files'].get(path, {}).get('sha256') == expected,
                            'CUSTODY_V2_RETAINED_CONTEXT_NOT_SELECTED_DATA')
            db = self.connect()
            try:
                db.execute('BEGIN'); self.capture_rows(db); db.rollback()
            finally: db.close()
            from .custody_control_registration import attach_source_observer
            attach_source_observer(self)
        except BaseException:
            self.close(); raise
    @property
    def core(self):
        from .protected_startup import StartupLease
        if type(self.owner) is StartupLease: return self.owner.core
        from .protected_root_worker import RootWorkerIntake
        if type(self.owner) is RootWorkerIntake: return self.owner.core
        return self.owner.principal.core
    def intact(self):
        require(not self.closed and not self.poisoned, 'CUSTODY_V2_JOURNAL_UNAVAILABLE')
        self.source.check(); named_identity(self.lock_fd, self.lock_path)
        now = protected(self.path); before = self.file_identity
        require((now.st_dev, now.st_ino, now.st_uid, stat.S_IMODE(now.st_mode)) ==
                (before.st_dev, before.st_ino, before.st_uid, stat.S_IMODE(before.st_mode)),
                'CUSTODY_V2_EXISTING_JOURNAL_REPLACED')
        require(private_bytes(self.genesis_path) == self.genesis_raw and
                self.source.file(str(self.genesis_path), ('DATA',)) == self.genesis_raw and
                private_bytes(self.key_path) == self.key, 'CUSTODY_V2_EXISTING_GENESIS_OR_KEY_CHANGED')
        if self.prior is not None: self.prior.intact()
    def connect(self):
        self.intact()
        db = sqlite3.connect('file:' + quote(str(self.path), safe='/') + '?mode=rw', uri=True, isolation_level=None)
        try:
            db.execute('PRAGMA trusted_schema=OFF'); db.execute('PRAGMA foreign_keys=ON')
            db.execute('PRAGMA synchronous=FULL')
            require(db.execute('PRAGMA foreign_keys').fetchall() == [(1,)], 'CUSTODY_V2_FOREIGN_KEYS_NOT_ENABLED')
            self.intact()
            return db
        except BaseException: db.close(); raise
    def _schema(self, db):
        expected = {statement.split()[2]: statement for statement in STATEMENTS}
        actual = db.execute("SELECT type,name,sql FROM sqlite_master WHERE name NOT LIKE 'sqlite_%'").fetchall()
        require(len(actual) == len(expected) and {name for _, name, _ in actual} == set(expected) and
                all(kind == 'table' and sql == expected[name] for kind, name, sql in actual),
                'CUSTODY_V2_COMPLETE_DDL_CHANGED')
    def capture_rows(self, db):
        require(db.in_transaction, 'CUSTODY_V2_SINGLE_CAPTURE_TRANSACTION_REQUIRED')
        self._schema(db)
        return {word: [list(row) for row in db.execute('SELECT * FROM ' + table +
                    (' ORDER BY seq' if table == 'events' else ' ORDER BY rowid'))]
                for word, table in _SQL_TABLES.items()}
    def capture(self, db, operation_append_candidate=None, startup_admission=None, recovery_operation=None):
        require(db.in_transaction, 'CUSTODY_V2_SINGLE_CAPTURE_TRANSACTION_REQUIRED')
        rows = self.capture_rows(db)
        genesis = db.execute('SELECT name,value,mac FROM genesis ORDER BY rowid').fetchall()
        require(len(genesis) == 1 and genesis[0][0] == 'owner-genesis', 'CUSTODY_V2_GENESIS_CARDINALITY')
        roster = self._owner_roster(db)
        if operation_append_candidate is not None:
            roster['operation_context']['append_candidate'] = operation_append_candidate
        if recovery_operation is not None:
            require(type(recovery_operation) is str, 'CUSTODY_RECOVERY_ACTUAL_OPERATION_REQUIRED')
            roster['operation_context']['recovery_operation'] = recovery_operation
        if startup_admission is not None:
            roster['startup_admission'] = startup_admission
        roster['custody_head_messages'] = [archive({'head_kind': row[1],
            'head': row[3] if row[1] == 'ORIGIN' else row[2], 'genesis': self.genesis}) for row in rows['heads']]
        roster['retained_v1'] = None if self.prior is None else {
            'selected': self.genesis['prior_custody'], 'descriptor_raw': self.prior.descriptor_raw,
            'plan_raw': self.prior.plan_raw, 'genesis_raw': self.prior.genesis_raw,
            'journal_raw': self.prior.journal_raw, 'logical_database_archive': self.prior.logical_database_archive,
            'lock_identity': shared_identity(self.prior.lock_fd, self.prior.selected.journal_path + '.lock')}
        return envelope(self.key, self.genesis_raw, genesis[0][1], genesis[0][2], roster, rows, self.genesis)
    def _owner_roster(self, db):
        from .root_worker_current_state import (_database_connection, _database, capture_operation_context,
            capture_intake_operation_context, capture_intake_admission_profiles, warm_operation_context_sources)
        from .protected_startup import StartupLease
        from .protected_root_worker import RootWorkerIntake
        warm_operation_context_sources()
        owner = self.owner
        intake = type(owner) is RootWorkerIntake
        lease = None if intake else (owner if type(owner) is StartupLease else owner.lease)
        # Both full captures retain every SQL storage class and actual FK row.
        # The custody journal itself uses this same transaction in both scans.
        def scan():
            source = self.source.check()
            offer = getattr(owner, 'current_offer', None)
            if offer is not None:
                from .root_worker_custody import CustodyOffer
                require(type(offer) is CustodyOffer and offer.p is owner.principal,
                        'CUSTODY_V2_ACTUAL_ESCROW_OWNER_REQUIRED')
                locks = dict(offer.fds)
                gate = None
            else:
                received = getattr(owner, 'custody', None)
                locks = (dict(received.fds) if received is not None
                         else {str(path): fd for path, fd in lease.fds.items()})
                gate = None if received is not None else lease.gate
            if gate is not None:
                for authority, name in ((gate.issuer, 'issuer.lock'), (gate.universe, 'universe.lock')):
                    if authority is not None:
                        locks[str(authority.state / name)] = authority.lock_fd
            locks[str(self.lock_path)] = self.lock_fd
            held = [{'path': path, 'identity': named_identity(fd, path),
                     'fdinfo': Path('/proc/self/fdinfo/' + str(fd)).read_bytes()} for path, fd in locks.items()]
            paths = []
            roster = self.spec['provisioned_state']
            require(type(roster) is list and len(set(roster)) == len(roster), 'CUSTODY_V2_COMPLETE_OWNER_ROSTER')
            for word in roster:
                path = Path(word); info = protected(path); raw = private_bytes(path)
                item = {'path': word, 'identity': {'device': info.st_dev, 'inode': info.st_ino,
                    'uid': info.st_uid, 'gid': info.st_gid, 'mode': stat.S_IMODE(info.st_mode)}, 'raw': raw}
                if path == self.path:
                    item['logical_database'] = _database_connection(db)
                elif raw.startswith(b'SQLite format 3\x00'):
                    item['logical_database'] = _database(path)
                paths.append(item)
            return {'installation': self.spec, 'descriptor_raw': self.descriptor_raw,
                    'source': source, 'held_locks': held, 'paths': paths,
                    'process': {'pid': os.getpid(), 'uid': os.getuid(), 'gid': os.getgid(),
                        'boot': Path('/proc/sys/kernel/random/boot_id').read_bytes(),
                        'stat': Path('/proc/self/stat').read_bytes(),
                        'status': Path('/proc/self/status').read_bytes()}}
        before = scan(); current = scan()
        require(before['held_locks'] == current['held_locks'] and
                [(row['path'], row['identity'], row.get('logical_database', row['raw'])) for row in before['paths']] ==
                [(row['path'], row['identity'], row.get('logical_database', row['raw'])) for row in current['paths']],
                'CUSTODY_V2_ACTUAL_OWNER_ROSTER_CHANGED')
        self.intact()
        custody = owner.custody if intake else lease.exec_custody
        principal = (lease.canonical_operation_principal if type(owner) is StartupLease
                     else getattr(owner, 'principal', None))
        if intake:
            operation_context = capture_intake_operation_context(owner)
            startup_admissions = capture_intake_admission_profiles(owner, operation_context)
            from .root_owned_descriptor_roster import capture_for_intake
            startup_native = capture_for_intake(owner, custody_connection=db, owner_state=current)
        else:
            require(principal is not None, 'CUSTODY_V2_ACTUAL_OPERATION_CONTEXT_REQUIRED')
            operation_context = capture_operation_context(principal)
            startup_admissions = lease.capture_admission_profiles(owner)
            startup_native = lease.capture_startup_native(owner, custody_connection=db, owner_state=current)
        return {'schema': 'worldline.protected-current-owner-roster-v2', 'before': before, 'current': current,
            'descriptor_path': self.plan['startup_descriptor'],
            'owner_plan_path': self.spec['root_worker']['owner_plan'], 'owner_plan_raw': self.plan_raw,
            'custody_database_path': str(self.path), 'custody_genesis_path': str(self.genesis_path),
            'custody_lock': {'path': str(self.lock_path), 'identity': named_identity(self.lock_fd, self.lock_path)},
            'operation_context': operation_context, 'startup_native': startup_native,
            'startup_admissions': startup_admissions,
            'received_custody': None if custody is None else {
                'frame': custody.frame,
                'held_locks': {path: named_identity(fd, path) for path, fd in custody.fds.items()}}}
    def retained_context(self):
        from .custody_provision_kernel import operands, invoke, _SYMBOLS
        from .retained_chain_kernel import _mapped
        from .errors import CoreUnavailable
        self.intact()
        inputs = operands(self.descriptor_raw, self.plan_raw, self.genesis_raw,
            self.plan['startup_descriptor'], self.spec['root_worker']['owner_plan'],
            str(self.genesis_path), str(self.path), self.key,
            'NEW' if self.prior is None else 'MIGRATE', self.prior)
        try: functions = tuple(getattr(self.core._lib, name) for name in _SYMBOLS)
        except AttributeError as error: raise CoreUnavailable('native custody retained-context eligibility unavailable') from error
        _mapped(self, self.core, functions)
        decision = invoke(functions, inputs)
        _mapped(self, self.core, functions)
        expected = 'New_Origin_Eligible' if self.prior is None else 'Closed_V1_Migration_Eligible'
        require(decision.state == expected, 'CUSTODY_V2_RETAINED_NATIVE_' + decision.state)
        return decision
    def load(self):
        with self.lock:
            self.intact(); db = self.connect()
            try:
                self.retained_context()
                db.execute('BEGIN'); result = decide_journal(self, self.capture(db)); db.rollback()
                self.intact(); return result
            finally: db.close()
    def adopt_owner(self, owner):
        """Transfer the live journal object, never reacquire its original OFD."""
        from .protected_startup import StartupLease
        from .protected_root_worker import RootWorkerFront, RootWorkerProcess
        with self.lock:
            self.intact()
            require(type(self.owner) is StartupLease and type(owner) in (RootWorkerFront, RootWorkerProcess)
                    and owner.lease is self.owner and owner.plan_raw == self.plan_raw
                    and owner.descriptor_raw == self.descriptor_raw,
                    'CUSTODY_V2_ACTUAL_STARTUP_FRONT_HANDOFF_REQUIRED')
            if type(owner) is RootWorkerProcess:
                require(owner.custody is self.owner.exec_custody,
                        'CUSTODY_V2_ACTUAL_RECEIVED_STARTUP_HANDOFF_REQUIRED')
            self.owner = owner
            return self

    def capture_operation_context(self):
        from .root_worker_current_state import capture_operation_context, capture_intake_operation_context
        from .protected_startup import StartupLease
        from .protected_root_worker import RootWorkerIntake
        owner = self.owner
        if type(owner) is RootWorkerIntake:
            return capture_intake_operation_context(owner)
        principal = (owner.canonical_operation_principal if type(owner) is StartupLease
                     else getattr(owner, 'principal', None))
        require(principal is not None, 'CUSTODY_V2_ACTUAL_CANONICAL_CONTEXT_REQUIRED')
        return capture_operation_context(principal)

    def capture_uncertainty(self):
        """Freeze the actual failed append; this never makes the owner usable."""
        with self.lock:
            captured = getattr(self, 'uncertain_append', None)
            require(self.poisoned and type(captured) is dict,
                    'CUSTODY_ACTUAL_UNCERTAIN_APPEND_REQUIRED')
            return raw_archive(captured)

    def root_state(self, operation):
        from .custody_event_capture import root_state
        with self.lock:
            db = self.connect()
            try:
                db.execute('BEGIN')
                raw, _ = self._accepted_capture(db)
                value = root_state(self, db, operation, before=raw)
                db.rollback()
                return value
            finally:
                db.close()

    def _accepted_capture(self, db):
        raw = self.capture(db)
        observed = decide_journal(self, raw)
        require(observed.status in (0, 1, 2), 'CUSTODY_V2_NATIVE_LOAD_' + observed.state)
        return raw, observed

    @staticmethod
    def _event(row):
        require(type(row) in (list, tuple) and len(row) == 13,
                'CUSTODY_V2_COMPLETE_EVENT_ROW_REQUIRED')
        seq, event_id, previous, generation, operation, subject_kind, subject, subgeneration, kind, actor, raw, base, mac = row
        wrapper = restore_archive(raw)
        require(type(wrapper) is dict and set(wrapper) == {'original', 'x5'}
                and type(wrapper['original']) is bytes,
                'CUSTODY_V2_COMPLETE_STORED_WRAPPER_REQUIRED')
        return {'seq': seq, 'event_id': event_id, 'previous': previous,
                'generation': generation, 'operation': operation,
                'subject_kind': subject_kind, 'subject': subject,
                'subgeneration': subgeneration, 'kind': kind, 'actor': actor,
                'record': raw_restore_archive(wrapper['original']), 'retained_record': wrapper,
                'base': base, 'mac': mac}

    def history(self, operation=None):
        require(operation is None or type(operation) is str, 'CUSTODY_V2_HISTORY_OPERATION_DOMAIN')
        with self.lock:
            db = self.connect()
            try:
                db.execute('BEGIN')
                self._accepted_capture(db)
                events = tuple(self._event(row) for row in self.capture_rows(db)['events'])
                db.rollback()
            finally:
                db.close()
        return events if operation is None else tuple(event for event in events if event['operation'] == operation)

    def require_event(self, event):
        require(type(event) is dict and type(event.get('operation')) is str
                and any(raw_archive(actual) == raw_archive(event) for actual in self.history(event['operation'])),
                'CUSTODY_V2_COMPLETE_COMMITTED_EVENT_ABSENT')
        return event

    def subject_context(self, operation, subject_kind, subject, original, *, root_operation=None,
                        kind=None, actor_role=None, query_purpose='MUTATION'):
        """Expose authentic retained cells; never compute generation or Legal."""
        from .custody_event_capture import subject_context
        with self.lock:
            db = self.connect()
            try:
                db.execute('BEGIN')
                raw, observed = self._accepted_capture(db)
                context = subject_context(self, db, operation, subject_kind, subject, original,
                                          raw, observed, root_operation=root_operation,
                                          kind=kind, actor_role=actor_role, query_purpose=query_purpose)
                db.rollback()
                return context
            finally:
                db.close()

    def output_quantity(self, operation, original, *, subject, evidence):
        from .root_worker_output_kernel import next_output
        return self._output_observation(operation, original, subject, evidence, next_output)

    def output_replay(self, operation, original, *, subject, evidence):
        from .root_worker_output_kernel import replay_output
        return self._output_observation(operation, original, subject, evidence, replay_output)

    def output_written(self, operation, original, *, subject, evidence):
        from .root_worker_output_kernel import written_output
        return self._output_observation(operation, original, subject, evidence, written_output)

    def output_prefix(self, operation, original, *, subject, evidence):
        from .root_worker_output_kernel import prefix_output
        return self._output_observation(operation, original, subject, evidence, prefix_output)

    def capture_output_query(self, operation, original, *, subject, evidence):
        """Capture actual full query bytes; this does not authorize an output."""
        with self.lock:
            db = self.connect()
            try:
                db.execute('BEGIN')
                raw = self._capture_output_query(db, operation, original, subject, evidence)
                db.rollback()
                return raw
            finally:
                db.close()

    def _capture_output_query(self, db, operation, original, subject, evidence):
        from .custody_event_capture import capture_event
        from .custody_mutation_kernel import mutation_input
        before, _ = self._accepted_capture(db)
        actor, wrapper = capture_event(self, db, operation, 'REQUEST_RESPONDED', None,
            'REQUEST', subject, original, evidence, before, query_purpose='OUTPUT')
        wrapper['x5']['emitter'] = evidence['emitter']
        return mutation_input(before, operation, 'REQUEST_RESPONDED', actor,
                              'REQUEST', subject, wrapper)

    def _output_observation(self, operation, original, subject, evidence, observe):
        """Retain the same full native profile for allocation, replay and writes."""
        with self.lock:
            db = self.connect()
            raw = None
            try:
                db.execute('BEGIN')
                raw = self._capture_output_query(db, operation, original, subject, evidence)
                result = observe(self, raw)
                if getattr(self, '_control_capture', None) is not None:
                    observed_result = result if type(result) is bytes else {
                        'disposition': result.disposition.value, 'ordinal': result.ordinal}
                    self.output_observations.append({'raw': raw, 'result': observed_result,
                        'result_type': type(result).__module__ + '.' + type(result).__qualname__,
                        'entry': observe.__module__ + '.' + observe.__name__, 'error': None})
                db.rollback()
                return result
            except BaseException as error:
                if raw is not None and getattr(self, '_control_capture', None) is not None:
                    self.output_observations.append({'raw': raw, 'result': None, 'result_type': None,
                        'entry': observe.__module__ + '.' + observe.__name__,
                        'error': {'type': type(error).__qualname__, 'module': type(error).__module__,
                                  'message': str(error), 'args': tuple(error.args)}})
                raise
            finally:
                db.close()

    def require_closed_owner(self, operation, original, *, evidence):
        """Re-decide full original closed-owner operands before an actual use."""
        from .custody_event_capture import capture_event
        from .custody_mutation_kernel import mutation_input
        from .custody_closed_kernel import decide_closed_owner
        with self.lock:
            db = self.connect()
            try:
                db.execute('BEGIN')
                before, _ = self._accepted_capture(db)
                actor, wrapper = capture_event(self, db, operation, 'CLOSED_WITNESS', None,
                    'ROOT', '', original, evidence, before, query_purpose='CLOSED_OWNER')
                raw = mutation_input(before, operation, 'CLOSED_WITNESS', actor,
                                     'ROOT', '', wrapper)
                joined = decide_closed_owner(self, raw)
                db.rollback()
                return joined
            finally:
                db.close()

    def serve_subject(self, operation, original, *, subject_kind='REQUEST', subject, evidence):
        """Require a fresh native full serving join immediately before a use."""
        from .custody_event_capture import capture_event
        from .custody_mutation_kernel import mutation_input
        from .custody_serving_kernel import decide_serving
        with self.lock:
            db = self.connect()
            try:
                db.execute('BEGIN')
                before, _ = self._accepted_capture(db)
                actor, wrapper = capture_event(self, db, operation, 'REQUEST_RESPONDED', None,
                    subject_kind, subject, original, evidence, before, query_purpose='SERVING')
                raw = mutation_input(before, operation, 'REQUEST_RESPONDED', actor,
                                     subject_kind, subject, wrapper)
                joined = decide_serving(self, raw)
                db.rollback()
                return joined
            finally:
                db.close()

    def cleanup_action(self, operation, kind, record, *, actor=None,
                       subject_kind, subject, evidence):
        """Ask native about the full actual cleanup candidate without writing."""
        from .custody_event_capture import capture_event
        from .custody_mutation_kernel import mutation_input
        from .custody_cleanup_kernel import decide_cleanup
        with self.lock:
            db = self.connect()
            try:
                db.execute('BEGIN')
                before, _ = self._accepted_capture(db)
                selected_actor, wrapper = capture_event(self, db, operation, kind, actor,
                    subject_kind, subject, record, evidence, before, query_purpose='CLEANUP')
                raw = mutation_input(before, operation, kind, selected_actor,
                                     subject_kind, subject, wrapper)
                action = decide_cleanup(self, raw)
                db.rollback()
                return action
            finally:
                db.close()

    def cleanup_subject(self, operation, kind, record, *, subject_kind, subject, evidence):
        from .custody_cleanup_kernel import CleanupAction
        action = self.cleanup_action(operation, kind, record, actor='COLLECTOR',
            subject_kind=subject_kind, subject=subject, evidence=evidence)
        if action in (CleanupAction.NO_EVENT, CleanupAction.RETAIN_UNKNOWN):
            return {'action': action, 'event': None}
        require(action.name == kind, 'CUSTODY_CLEANUP_NATIVE_EVENT_KIND_CHANGED')
        # append performs a fresh full native mutation decision under BEGIN
        # IMMEDIATE. The preceding route never substitutes for that decision.
        event = self.append(operation, kind, record, actor='COLLECTOR',
            subject_kind=subject_kind, subject=subject, evidence=evidence)
        return {'action': action, 'event': event}

    def append_retry(self, uncertainty, *, evidence):
        """Re-decide a saved actual attempt against fresh reconciled custody."""
        require(type(uncertainty) is bytes, 'CUSTODY_RETRY_FULL_UNCERTAINTY_IMAGE_REQUIRED')
        saved = raw_restore_archive(uncertainty)
        original = raw_restore_archive(saved['candidate']['original'])
        return self.append(saved['operation'], saved['kind'], original,
            subject_kind=saved['subject_kind'], subject=saved['subject'], evidence=evidence,
            _retry_attempt=uncertainty)

    def append(self, operation, kind, record, *, actor=None, subject_kind='ROOT',
               subject='', evidence=None, _retry_attempt=None):
        """Apply only native-produced complete SQL delta under one writer lock.

        A failed COMMIT or any failed durable readback latches uncertainty.
        No caller can turn a matching partial row or transport ACK into success.
        Ordinary retries retain old X5; uncertainty retries authenticate the
        saved full attempt and obtain a fresh native delta or exact old replay.
        """
        from .custody_mutation_kernel import mutation_input, decide_journal as mutate
        from .custody_sql_delta import apply
        from .custody_event_capture import capture_event
        if _retry_attempt is not None:
            from .custody_mutation_kernel import decide_retry as mutate
        require(all(type(word) is str for word in (operation, kind, subject_kind, subject)),
                'CUSTODY_V2_EVENT_DOMAIN')
        with self.lock:
            db = self.connect()
            commit_attempted = False
            decision = None
            control = getattr(self, '_control_capture', None)
            captured = False
            control_context = None
            try:
                db.execute('BEGIN IMMEDIATE')
                before, before_decision = self._accepted_capture(db)
                candidate_actor, wrapper = capture_event(self, db, operation, kind, actor,
                    subject_kind, subject, record, evidence, before)
                inputs = mutation_input(before, operation, kind, candidate_actor,
                                        subject_kind, subject, wrapper)
                if _retry_attempt is not None:
                    value = restore_archive(inputs)
                    value['retry_attempt'] = _retry_attempt
                    inputs = archive(value)
                if control is not None:
                    from .custody_context_kernel import capture_context_input
                    control_context = capture_context_input(self, inputs)
                decision = mutate(self, inputs)
                if control is not None:
                    control.before_effect(operation, kind, inputs, decision, before,
                                          before_decision, context=control_context)
                if decision.status == 1:
                    require(decision.delta is None, 'CUSTODY_V2_REPLAY_MUST_NOT_WRITE')
                    rows = self.capture_rows(db)['events']
                    if _retry_attempt is not None:
                        saved = raw_restore_archive(_retry_attempt)
                        expected = saved['attempted_event']
                        matches = [self._event(row) for row in rows
                                   if raw_archive(self._event(row)) == raw_archive(expected)]
                    else:
                        matches = [self._event(row) for row in rows if row[4] == operation
                            and row[8] == kind and row[9] == candidate_actor
                            and row[5] == subject_kind and row[6] == subject
                            and row[10] == archive(wrapper)]
                    require(len(matches) == 1, 'CUSTODY_V2_NATIVE_REPLAY_EVENT_MEMBERSHIP')
                    db.rollback()
                    if control is not None:
                        control.observe(operation, kind, inputs, decision, before,
                                        before_load=before_decision, context=control_context)
                        captured = True
                    return matches[0]
                require(decision.status == 0 and decision.delta is not None,
                        'CUSTODY_V2_NATIVE_MUTATION_' + decision.state)
                values = apply(db, decision.delta)
                after_rows = self.capture_rows(db)
                after, after_decision = self._accepted_capture(db)
                matches = [self._event(row) for row in after_rows['events']
                           if row[1] == values['event'][0]]
                require(len(matches) == 1 and archive(matches[0]['retained_record']) == archive(wrapper)
                        and matches[0]['base'] == values['event'][10],
                        'CUSTODY_V2_NATIVE_COMPLETE_DELTA_READBACK')
                expected_rows = archive(after_rows)
                expected_event = matches[0]
                self.intact()
                commit_attempted = True
                db.commit()
                db.close()
                db = None
                self._sync()
                durable = self.connect()
                try:
                    durable.execute('BEGIN')
                    actual_rows = self.capture_rows(durable)
                    _, durable_decision = self._accepted_capture(durable)
                    require(archive(actual_rows) == expected_rows
                            and durable_decision.status == after_decision.status
                            and durable_decision.position == after_decision.position,
                            'CUSTODY_V2_DURABLE_FULL_READBACK_CHANGED')
                    durable.rollback()
                finally:
                    durable.close()
                if control is not None:
                    control.observe(operation, kind, inputs, decision, before, after,
                                    before_decision, after_decision, context=control_context)
                    captured = True
                return expected_event
            except BaseException as error:
                if db is not None and db.in_transaction:
                    try:
                        db.rollback()
                    except BaseException as rollback_error:
                        error.add_note('custody rollback also failed: ' + repr(rollback_error))
                if commit_attempted:
                    self.poisoned = True
                    self.uncertain_append = {'operation': operation, 'kind': kind,
                        'subject_kind': subject_kind, 'subject': subject,
                        'input': inputs, 'before': before, 'candidate': wrapper,
                        'actor': candidate_actor, 'native_delta': decision.delta,
                        'native_status': decision.status, 'native_position': decision.position,
                        'attempted_event': expected_event, 'applied_rows': expected_rows,
                        'error': {'type': type(error).__qualname__, 'module': type(error).__module__,
                            'message': str(error), 'args': tuple(error.args),
                            'errno': getattr(error, 'errno', None),
                            'filename': getattr(error, 'filename', None),
                            'filename2': getattr(error, 'filename2', None),
                            'sqlite_errorcode': getattr(error, 'sqlite_errorcode', None),
                            'sqlite_errorname': getattr(error, 'sqlite_errorname', None),
                            'notes': tuple(getattr(error, '__notes__', ())) }}
                    lease = getattr(self.owner, 'lease', self.owner)
                    lease.poisoned = True
                if control is not None and decision is not None and not captured:
                    try:
                        control.observe(operation, kind, inputs, decision, before,
                                        before_load=before_decision, error=error,
                                        context=control_context)
                    except BaseException as capture_error:
                        error.add_note('custody control export also failed: ' + repr(capture_error))
                raise
            finally:
                if db is not None:
                    db.close()

    def _sync(self):
        self.intact()
        paths = [self.path]
        # SQLite FULL commit synchronizes its own journal. Also synchronize any
        # surviving actual WAL, then the named DB and directory, retaining OFDs.
        wal = Path(str(self.path) + '-wal')
        if os.path.lexists(wal):
            paths.insert(0, wal)
        for path in paths:
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
            try:
                named = path.lstat()
                held = os.fstat(fd)
                require(stat.S_ISREG(held.st_mode) and held.st_uid == 0
                        and held.st_nlink == 1 and (named.st_dev, named.st_ino) == (held.st_dev, held.st_ino),
                        'CUSTODY_V2_SYNC_NAMED_FILE_CHANGED')
                os.fsync(fd)
            finally:
                os.close(fd)
        directory = os.open(self.path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
        self.intact()
    def close(self):
        if self.closed: return
        self.closed = True
        primary = None
        if self.prior is not None:
            try: self.prior.close()
            except BaseException as error: primary = error
        try: os.close(self.lock_fd)
        except BaseException as error:
            if primary is None: primary = error
        if primary is not None and __import__('sys').exc_info()[1] is None: raise primary
