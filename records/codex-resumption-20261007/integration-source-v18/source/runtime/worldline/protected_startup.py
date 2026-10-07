"""Protected startup source candidate. No installation or closure claim.

Acquire the existing WORLDLINE store/Gate/broker/actuator locks before importing
and constructing Store/Controller/Gate. Owner provisioning is a separate offline
operation: absent state, locks, bootstrap ledger, or authorization never means
first boot. The historical ordinary startup remains a separate supported API.
"""
from __future__ import annotations

import fcntl
import hashlib
import importlib
import inspect
import json
import os
from pathlib import Path
import socket
import socketserver
import sqlite3
import stat
import struct
import sys
from threading import RLock


class StartupRefusal(RuntimeError):
    pass


def require(value, code):
    if not value:
        raise StartupRefusal(code)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode('utf-8')


def exact_json(raw, *, canonical_required=True):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'STARTUP_DUPLICATE_JSON_KEY')
            result[key] = value
        return result
    result = json.loads(raw, object_pairs_hook=pairs,
        parse_constant=lambda value: (_ for _ in ()).throw(StartupRefusal('STARTUP_NONFINITE_JSON')))
    if canonical_required:
        require(raw in (canonical(result), canonical(result) + b'\n'), 'STARTUP_NONCANONICAL_JSON')
    return result


def protected(path, *, directory=False):
    """Every component is root-owned and unavailable for non-root writes."""
    path = Path(path)
    require(path.is_absolute() and str(path) == os.path.normpath(path), 'STARTUP_PATH_SPELLING')
    for item in (*reversed(path.parents), path):
        info = item.lstat()
        require(not stat.S_ISLNK(info.st_mode) and info.st_uid == 0 and
                not stat.S_IMODE(info.st_mode) & 0o022, 'STARTUP_UNPROTECTED_COMPONENT')
        if item != path or directory:
            require(stat.S_ISDIR(info.st_mode), 'STARTUP_DIRECTORY_REQUIRED')
    info = path.lstat()
    if not directory:
        require(stat.S_ISREG(info.st_mode), 'STARTUP_REGULAR_FILE_REQUIRED')
    return info


def private_bytes(path):
    info = protected(path)
    require(not stat.S_IMODE(info.st_mode) & 0o077, 'STARTUP_PRIVATE_FILE_REQUIRED')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        held = os.fstat(fd)
        require(held.st_nlink == 1 and (held.st_dev, held.st_ino) == (info.st_dev, info.st_ino), 'STARTUP_FILE_CHANGED')
        with os.fdopen(os.dup(fd), 'rb') as stream:
            raw = stream.read()
        after = os.fstat(fd)
        require((held.st_size, held.st_mtime_ns, held.st_ctime_ns) ==
                (after.st_size, after.st_mtime_ns, after.st_ctime_ns) and len(raw) == held.st_size,
                'STARTUP_FILE_CHANGED_DURING_READ')
        require((Path(path).lstat().st_dev, Path(path).lstat().st_ino) ==
                (held.st_dev, held.st_ino), 'STARTUP_FILE_RENAMED')
        return raw
    finally:
        os.close(fd)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def kernel_identity(value):
    """Lossless Linux uid_t/gid_t input, including configured zero."""
    if type(value) is not int or value < 0:
        return False
    try:
        return struct.unpack('I', struct.pack('I', value))[0] == value
    except (struct.error, OverflowError):
        return False


def inventory(root):
    protected(root, directory=True)
    result = {}
    for path in sorted(Path(root).rglob('*')):
        info = protected(path, directory=path.is_dir())
        if path.is_file():
            require(path.suffix != '.pyc' and path.name != '__pycache__', 'STARTUP_BYTECODE_PRESENT')
            result[path.relative_to(root).as_posix()] = {
                'mode': oct(stat.S_IMODE(info.st_mode)), 'sha256': digest(path.read_bytes())}
    return result


def _sql_value(value):
    if type(value) is bytes:
        return {'blob': value.hex()}
    require(value is None or type(value) in (str, int, float), 'STARTUP_SQL_VALUE_INVALID')
    return {'type': type(value).__name__, 'value': value}


def store_snapshot(path):
    """Read a complete SQLite snapshot; no asserted remainder or truncated row."""
    private_bytes(path)
    db = sqlite3.connect(Path(path).as_uri() + '?mode=ro', uri=True, isolation_level=None)
    try:
        db.execute('PRAGMA trusted_schema=OFF')
        db.execute('BEGIN')
        schema = [list(row) for row in db.execute("SELECT type,name,tbl_name,sql FROM sqlite_master WHERE name NOT LIKE 'sqlite_%' ORDER BY type,name")]
        tables = {}
        for kind, name, _table, _sql in schema:
            if kind == 'table':
                quoted = '"' + name.replace('"', '""') + '"'
                rows = [[_sql_value(value) for value in row] for row in db.execute('SELECT * FROM ' + quoted)]
                tables[name] = sorted(rows, key=canonical)
        result = {'schema': schema, 'version': db.execute('PRAGMA user_version').fetchone()[0], 'tables': tables}
        db.execute('ROLLBACK')
        return result
    finally:
        db.close()


class StartupLease:
    """Actual retained file locks and exact installation/owner Genesis bindings.

    This class has no caller-supplied authorization Boolean. The owner-provisioned
    root-private descriptor and preexisting durable ledger are the inputs.
    Protecting these against a hostile root, hardware rollback, or uncooperative
    privileged routes remains a distinct OS custody/deployment obligation.
    """
    def __init__(self, descriptor):
        require(os.geteuid() == 0, 'STARTUP_ROOT_REQUIRED')
        # The operator's early helper must already control the actual importer.
        # Never install a lease here to bless code which ran before this point.
        self.source_module = sys.modules.get('_worldline_approved_source_loader')
        require(type(self.source_module) is type(sys), 'STARTUP_EARLY_SOURCE_LEASE_REQUIRED')
        self.source_lease = self.source_module.current()
        require(type(self.source_lease) is self.source_module.ApprovedSourceLease,
                'STARTUP_ACTUAL_SOURCE_LEASE_REQUIRED')
        self.executed_code_observation = self.source_lease.check()
        self.descriptor_path = Path(descriptor)
        self.descriptor_raw = private_bytes(self.descriptor_path)
        self.spec = exact_json(self.descriptor_raw)
        expected = {'schema', 'installation_id', 'trees', 'files', 'runtime', 'paths',
                    'genesis', 'bootstrap_ledger', 'provisioned_state', 'actuator_transactions', 'endpoint'}
        require(type(self.spec) is dict and set(self.spec) == expected and
                self.spec['schema'] == 'worldline.protected-startup-v1', 'STARTUP_DESCRIPTOR_SCHEMA')
        require(type(self.spec['installation_id']) is str and self.spec['installation_id'], 'STARTUP_INSTALLATION_ABSENT')
        self.closed = False
        self.poisoned = False
        self.fds = {}
        self.named = {}
        self.mutex = RLock()
        self.gate = None
        self.store = None
        self.controller = None
        self.state_path = Path(self.spec['paths']['state'])
        self.genesis_path = Path(self.spec['genesis'])
        self.genesis_raw = private_bytes(self.genesis_path)
        self.genesis = exact_json(self.genesis_raw)
        self.genesis_id = digest(self.genesis_raw)
        self._validate_genesis()
        endpoint = self.spec['endpoint']
        require(type(endpoint) is dict and set(endpoint) == {'path', 'requester_uid', 'requester_gid'} and
                kernel_identity(endpoint['requester_uid']) and
                kernel_identity(endpoint['requester_gid']) and
                Path(endpoint['path']) == Path(self.spec['paths']['authority_root']) / 'authority/protected-runtime/intent.sock',
                'STARTUP_OWNER_ENDPOINT_BINDING_INVALID')
        self._installation()
        self._existing_state()
        self._routes_absent()
        try:
            for path in self._lock_paths():
                self._lock(path)
            self.store_lock_fd = self.fds[self.state_path / 'worldline-store.lock']
            self._routes_absent()
            self._open_ledger()
            self.validate_store_path(self.state_path / 'worldline.sqlite3')
        except BaseException:
            self.close()
            raise

    def _validate_genesis(self):
        expected = {'schema', 'installation_id', 'owner_authorization', 'store', 'gate_config',
                    'gate_head', 'issuer_head', 'journals'}
        require(type(self.genesis) is dict and set(self.genesis) == expected and
                self.genesis['schema'] == 'worldline.owner-provisioned-genesis-v1' and
                self.genesis['installation_id'] == self.spec['installation_id'] and
                type(self.genesis['owner_authorization']) is str and self.genesis['owner_authorization'],
                'STARTUP_OWNER_GENESIS_INVALID')
        require(set(self.genesis['store']) == {'identity', 'schema', 'version', 'initial_head'} and
                type(self.genesis['store']['identity']) is str and self.genesis['store']['identity'],
                'STARTUP_STORE_GENESIS_INVALID')
        require(set(self.genesis['journals']) == {'recovery-full-journal', 'full-use-reservations'},
                'STARTUP_JOURNAL_GENESIS_SET')
        root = Path(self.spec['paths']['authority_root'])
        expected_paths = {'recovery-full-journal': root / 'authority/gate/state/recovery-full-journal.json',
                          'full-use-reservations': root / 'authority/issuer/state/full-use-reservations.json'}
        for name, record in self.genesis['journals'].items():
            require(type(record) is dict and set(record) == {'path', 'initial_envelope'} and
                    Path(record['path']) == expected_paths[name] and type(record['initial_envelope']) is dict,
                    'STARTUP_EXACT_JOURNAL_GENESIS_REQUIRED')

    def _installation(self):
        require(sys.modules.get('_worldline_approved_source_loader') is self.source_module and
                self.source_module.current() is self.source_lease and
                type(self.source_lease) is self.source_module.ApprovedSourceLease,
                'STARTUP_RETAINED_SOURCE_LEASE_CHANGED')
        self.executed_code_observation = self.source_lease.check()
        self.allowed = set()
        require(type(self.spec['trees']) is dict and self.spec['trees'], 'STARTUP_COMPLETE_TREES_REQUIRED')
        for root, expected in self.spec['trees'].items():
            actual = inventory(Path(root))
            require(actual == expected, 'STARTUP_COMPLETE_TREE_CHANGED')
            self.allowed.update(Path(root) / key for key in actual)
        require(type(self.spec['files']) is dict and self.spec['files'], 'STARTUP_COMPLETE_FILES_REQUIRED')
        for name, expected in self.spec['files'].items():
            path = Path(name)
            info = protected(path)
            require({'mode': oct(stat.S_IMODE(info.st_mode)), 'sha256': digest(path.read_bytes())} == expected,
                    'STARTUP_INSTALLED_FILE_CHANGED')
            self.allowed.add(path)
        runtime = self.spec['runtime']
        require(type(runtime) is dict and set(runtime) == {'interpreter', 'worldline_source', 'gate_source',
                'principal_source', 'native_library', 'proof_manifest', 'proof_summary', 'tools', 'shared_objects'},
                'STARTUP_RUNTIME_DESCRIPTOR_SCHEMA')
        require(Path(os.readlink('/proc/self/exe')) == Path(runtime['interpreter']) and
                Path(runtime['interpreter']) in self.allowed and sys.flags.isolated and
                sys.flags.no_site and sys.dont_write_bytecode and
                self.source_lease.interpreter == str(Path(runtime['interpreter'])),
                'STARTUP_EXACT_ISOLATED_INTERPRETER_REQUIRED')
        require(Path(self.source_module.__file__) == Path(self.source_lease.helper_path) and
                Path(self.source_lease.helper_path) in self.allowed,
                'STARTUP_SELECTED_EARLY_HELPER_NOT_INSTALLED')
        require(self.source_lease.file(str(self.descriptor_path), ('DATA',)) == self.descriptor_raw and
                self.source_lease.file(str(self.genesis_path), ('DATA',)) == self.genesis_raw,
                'STARTUP_EARLY_OWNER_BINDING_CHANGED')
        for path, selected in self.source_lease.files.items():
            if selected[0] in ('HELPER', 'ENTRY', 'INTERPRETER', 'SOURCE', 'EXTENSION', 'CACHE'):
                require(Path(path) in self.allowed, 'STARTUP_EXECUTABLE_ENVELOPE_NOT_IN_INSTALLATION')
        require(Path(__file__) == Path(runtime['worldline_source']) / 'runtime/worldline/protected_startup.py',
                'STARTUP_RUNNING_SOURCE_CHANGED')
        for name in ('gate_source', 'principal_source', 'native_library', 'proof_manifest', 'proof_summary'):
            require(Path(runtime[name]) in self.allowed, 'STARTUP_DEPENDENCY_NOT_IN_COMPLETE_INVENTORY')
        require(type(runtime['tools']) is dict and runtime['tools'] and type(runtime['shared_objects']) is list,
                'STARTUP_COMPLETE_TOOL_NATIVE_CLOSURE_REQUIRED')
        for path in (*runtime['tools'].values(), *runtime['shared_objects']):
            require(Path(path) in self.allowed, 'STARTUP_TOOL_OR_NATIVE_UNPINNED')
        # Adapter tools use command names. Pin the exact resolution under a
        # fixed path, and reject inherited Python/native loader lookup inputs.
        require(not any(key.startswith(('PYTHON', 'LD_')) for key in os.environ), 'STARTUP_LOADER_ENVIRONMENT_PRESENT')
        import shutil
        for command, path in runtime['tools'].items():
            found = shutil.which(command)
            require(found is not None and Path(found).resolve(strict=True) == Path(path), 'STARTUP_TOOL_RESOLUTION_CHANGED')

    def _existing_state(self):
        require(type(self.spec['provisioned_state']) is list and self.spec['provisioned_state'], 'STARTUP_PROVISIONED_STATE_REQUIRED')
        required = {self.state_path / 'worldline.sqlite3', self.state_path / 'worldline-store.lock',
                    *(self.state_path / name for name in ('evaluation-pending.db', 'evaluation-pending-target.db',
                      'evaluation-terminal.db', 'evaluation-terminal-target.db', 'evaluation-finalization.db')),
                    Path(self.spec['paths']['runtime']) / 'admission-ledger.json',
                    Path(self.spec['paths']['runtime']) / 'admission.lock',
                    Path(self.spec['paths']['config']) / 'config.json'}
        root = Path(self.spec['paths']['authority_root'])
        required.update(root / name for name in ('authority/gate/config.json', 'authority/gate/state/journal.json',
            'authority/gate/state/gate.lock', 'authority/state/broker.lock', 'authority/state/authority.json',
            'canonical/state.json', 'authority/issuer/state/issuer.lock', 'authority/issuer/state/issuer-key.bin',
            'authority/issuer/state/policy.json', 'authority/issuer/state/head.json',
            'authority/issuer/state/capabilities.sqlite', 'authority/universe/root/universe.lock',
            'authority/universe/root/universe-key.bin', 'authority/universe/root/genesis.json',
            'authority/universe/root/registry.json', 'authority/universe/root/universes.sqlite',
            'authority/evidence/state/evidence.lock', 'authority/evidence/state/key.bin',
            'authority/evidence/state/policy.json', 'authority/evidence/state/head.json',
            'authority/evidence/state/evidence.sqlite'))
        selected = {Path(path) for path in self.spec['provisioned_state']}
        require(required <= selected, 'STARTUP_EXISTING_STATE_ROSTER_INCOMPLETE')
        for path in selected:
            private_bytes(path)
        # No ordinary directory provisioning/chmod path may establish custody.
        for name in ('home', 'data', 'state', 'runtime', 'config'):
            info = protected(self.spec['paths'][name], directory=True)
            require(not stat.S_IMODE(info.st_mode) & 0o077, 'STARTUP_PRIVATE_DIRECTORY_REQUIRED')

    def _lock_paths(self):
        root = Path(self.spec['paths']['authority_root'])
        paths = [self.state_path / 'worldline-store.lock', root / 'authority/gate/state/gate.lock',
                 root / 'authority/state/broker.lock']
        transactions = self.spec['actuator_transactions']
        require(type(transactions) is list and len(set(transactions)) == len(transactions) and
                all(type(value) is str and value and '/' not in value and value not in ('.', '..') for value in transactions),
                'STARTUP_ACTUATOR_TRANSACTION_ROSTER_INVALID')
        actuator = root / 'canonical/actuator'
        protected(actuator, directory=True)
        require(sorted(path.name for path in actuator.iterdir()) == sorted(transactions), 'STARTUP_ACTUATOR_ROSTER_CHANGED')
        for value in transactions:
            paths.append(actuator / value / 'service.lock')
        return paths

    def _lock(self, path):
        private_bytes(path)
        fd = os.open(path, os.O_RDWR | os.O_NOFOLLOW | os.O_CLOEXEC)
        try:
            info = os.fstat(fd)
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.fds[path] = fd
            self.named[path] = (info.st_dev, info.st_ino)
        except BaseException:
            os.close(fd)
            raise

    def _routes_absent(self):
        root = Path(self.spec['paths']['authority_root'])
        for path in (Path(self.spec['paths']['runtime']) / 'worldlined.sock',
                     root / 'authority/authority.sock', root / 'authority/gate/intent.sock'):
            require(not os.path.lexists(path), 'STARTUP_LEGACY_ENDPOINT_PRESENT')

    def _open_ledger(self):
        path = Path(self.spec['bootstrap_ledger'])
        private_bytes(path)
        info = path.stat()
        self.ledger_identity = (info.st_dev, info.st_ino)
        self.db = sqlite3.connect(path.as_uri() + '?mode=rw', uri=True, isolation_level=None, check_same_thread=False)
        self.db.execute('PRAGMA trusted_schema=OFF')
        self.db.execute('PRAGMA synchronous=FULL')
        require(self.db.execute('PRAGMA journal_mode').fetchone()[0].lower() == 'wal', 'STARTUP_BOOTSTRAP_WAL_REQUIRED')
        require(self.db.execute('PRAGMA quick_check').fetchall() == [('ok',)], 'STARTUP_BOOTSTRAP_LEDGER_DAMAGED')
        require({row[0] for row in self.db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")} ==
                {'bootstrap_identity', 'journal_intents', 'journal_history'}, 'STARTUP_BOOTSTRAP_LEDGER_SCHEMA')
        for name, columns in {'bootstrap_identity': ('installation_id', 'genesis_sha256'),
                'journal_intents': ('name', 'path', 'initial_envelope', 'state'),
                'journal_history': ('ordinal', 'name', 'prior', 'state', 'envelope_sha256')}.items():
            require(tuple(row[1] for row in self.db.execute('PRAGMA table_info(' + name + ')')) == columns,
                    'STARTUP_BOOTSTRAP_LEDGER_COLUMNS_CHANGED')
        require(not self.db.execute("SELECT name FROM sqlite_master WHERE type IN ('trigger','view')").fetchall(),
                'STARTUP_BOOTSTRAP_LEDGER_TRIGGER_OR_VIEW')
        identity = self.db.execute('SELECT installation_id,genesis_sha256 FROM bootstrap_identity').fetchall()
        require(identity == [(self.spec['installation_id'], self.genesis_id)], 'STARTUP_BOOTSTRAP_IDENTITY_CHANGED')
        rows = self.db.execute('SELECT name,path,initial_envelope,state FROM journal_intents ORDER BY name').fetchall()
        require({row[0] for row in rows} == set(self.genesis['journals']), 'STARTUP_BOOTSTRAP_JOURNAL_ROSTER')
        for name, path, raw, state in rows:
            record = self.genesis['journals'][name]
            require(path == record['path'] and type(raw) is bytes and raw == canonical(record['initial_envelope']) + b'\n' and
                    state in ('UNUSED', 'INTENT', 'CONSUMED'), 'STARTUP_BOOTSTRAP_JOURNAL_CHANGED')
            history = self.db.execute('SELECT prior,state,envelope_sha256 FROM journal_history WHERE name=? ORDER BY ordinal', (name,)).fetchall()
            expected = [] if state == 'UNUSED' else [('UNUSED', 'INTENT', digest(raw))]
            if state == 'CONSUMED':
                expected.append(('INTENT', 'CONSUMED', digest(raw)))
            require(history == expected, 'STARTUP_BOOTSTRAP_HISTORY_CHANGED')

    def validate_store_path(self, path):
        require(Path(path) == self.state_path / 'worldline.sqlite3', 'STARTUP_STORE_PATH_CHANGED')
        snapshot = store_snapshot(path)
        expected = self.genesis['store']
        require(snapshot['schema'] == expected['schema'] and snapshot['version'] == expected['version'],
                'STARTUP_STORE_SCHEMA_MIGRATION_REQUIRED')
        rows = snapshot['tables'].get('meta', [])
        def payload(row):
            value = row[1]
            return bytes.fromhex(value['blob']) if 'blob' in value else value['value'].encode()
        actual = {row[0]['value']: payload(row) for row in rows}
        require(exact_json(actual['protectedStoreGenesis']) == expected['identity'] and
                type(exact_json(actual['finalizationStoreId'])) is str,
                'STARTUP_EXISTING_STORE_IDENTITY_REQUIRED')
        self.store_initial_head = digest(canonical(snapshot))

    def validate_store(self, paths, version):
        self.intact()
        require(paths.state == self.state_path and version == self.genesis['store']['version'], 'STARTUP_STORE_CONSTRUCTOR_CHANGED')
        self.validate_store_path(paths.database)

    def validate_controller(self, paths, store, core):
        self.intact()
        require(self.store is store and getattr(store, 'startup_lease', None) is self and
                paths.state == self.state_path and core is store.core,
                'STARTUP_CONTROLLER_STORE_LEASE_CHANGED')

    def validate_capability_layout(self, paths):
        """Validate the complete preexisting layout without ensure/chmod/mkdir."""
        self.intact()
        selected = self.spec['paths']
        require(all(getattr(paths, name) == Path(selected[name])
                    for name in ('home', 'data', 'state', 'runtime', 'config')),
                'STARTUP_CAPABILITY_LAYOUT_BINDING_CHANGED')
        for path in (paths.data, paths.state, paths.runtime, paths.config,
                     paths.live, paths.generations, paths.worlds, paths.overlays,
                     paths.events, paths.receipts, paths.transactions, paths.logs):
            # Group traversal selected by the operator is permitted. No component
            # is writable by an unprivileged process, and no absent member is made.
            protected(path, directory=True)

    def reconcile_admission(self, controller):
        self.intact()
        # The separately frozen full ledger has no protected startup roster
        # producer/reconciler yet. Historical reconcile releases selected rows
        # under an incomplete observation and cannot satisfy that obligation.
        raise StartupRefusal('PROTECTED_FULL_LEDGER_STARTUP_RECONCILER_UNAVAILABLE')

    def loaded(self):
        require(sys.modules.get('_worldline_approved_source_loader') is self.source_module and
                self.source_module.current() is self.source_lease,
                'STARTUP_RETAINED_SOURCE_LEASE_CHANGED')
        self.executed_code_observation = self.source_lease.check()
        for module in tuple(sys.modules.values()):
            path = getattr(module, '__file__', None)
            if path is not None:
                require(Path(path).resolve(strict=True) in self.allowed, 'STARTUP_IMPORTED_MODULE_UNPINNED')
        selected = {Path(path) for path in self.spec['runtime']['shared_objects']}
        selected.add(Path(self.spec['runtime']['interpreter']))
        mutable = {Path(path + '-shm') for path in self.spec['provisioned_state']
                   if path.endswith(('.db', '.sqlite', '.sqlite3'))}
        mutable.add(Path(self.spec['bootstrap_ledger'] + '-shm'))
        for line in Path('/proc/self/maps').read_text().splitlines():
            fields = line.split(maxsplit=5)
            if len(fields) != 6 or not fields[5].startswith('/'):
                continue
            path = Path(fields[5])
            if path in mutable and 'x' not in fields[1]:
                # SQLite's retained shared-memory file is mutable state, never
                # executable authority. Validate its exact named custody only.
                private_bytes(path)
                continue
            require(path in selected and path in self.allowed, 'STARTUP_MAPPED_RUNTIME_UNPINNED')
            info = path.stat()
            fd = os.open(Path('/proc/self/map_files') / fields[0], os.O_RDONLY | os.O_CLOEXEC)
            try:
                held = os.fstat(fd)
                require((held.st_dev, held.st_ino) == (info.st_dev, info.st_ino), 'STARTUP_NATIVE_MAPPING_CHANGED')
                with os.fdopen(os.dup(fd), 'rb') as stream:
                    require(stream.read() == path.read_bytes(), 'STARTUP_NATIVE_MAPPING_BYTES_CHANGED')
            finally:
                os.close(fd)

    def intact(self):
        require(not self.closed and not self.poisoned, 'STARTUP_LEASE_UNAVAILABLE')
        require(private_bytes(self.descriptor_path) == self.descriptor_raw and
                private_bytes(self.genesis_path) == self.genesis_raw, 'STARTUP_OWNER_BINDING_CHANGED')
        self._installation()
        self._routes_absent()
        ledger = protected(self.spec['bootstrap_ledger'])
        require((ledger.st_dev, ledger.st_ino) == self.ledger_identity, 'STARTUP_BOOTSTRAP_LEDGER_REPLACED')
        require(set(self._lock_paths()) == set(self.fds), 'STARTUP_LOCK_ROSTER_CHANGED')
        for path, fd in self.fds.items():
            named = protected(path)
            held = os.fstat(fd)
            require((named.st_dev, named.st_ino) == self.named[path] == (held.st_dev, held.st_ino), 'STARTUP_RETAINED_LOCK_CHANGED')
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if self.gate is not None:
            issuer = self.gate.issuer
            require(issuer is not None, 'STARTUP_ACTUAL_ISSUER_ABSENT')
            path = issuer.state / 'issuer.lock'
            info, held = protected(path), os.fstat(issuer.lock_fd)
            require((info.st_dev, info.st_ino) == (held.st_dev, held.st_ino), 'STARTUP_ISSUER_LOCK_CHANGED')
            fcntl.flock(issuer.lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

    def _genesis_heads(self, gate):
        require(gate is self.gate and gate.issuer is not None, 'STARTUP_ACTUAL_GATE_REQUIRED')
        require(digest(gate.config_raw) == self.genesis['gate_config'] and
                digest(canonical(gate.journal)) == self.genesis['gate_head'] and
                gate.issuer.head() == self.genesis['issuer_head'] and
                self.store_initial_head == self.genesis['store']['initial_head'],
                'STARTUP_AUTHORIZED_GENESIS_HEADS_CHANGED')

    def open_journal(self, gate, name, path, genesis_envelope):
        """Consume an explicit exact owner grant with retained intent/readback.

        Once consumed, deletion is a refusal. INTENT without a file is also a
        refusal: no restart constructs a replacement. INTENT with exact bytes
        may complete only the already recorded owner admission.
        """
        with self.mutex:
            self.intact()
            record = self.genesis['journals'].get(name)
            require(gate is self.gate and gate.issuer is not None and record is not None and
                    Path(path) == Path(record['path']), 'STARTUP_JOURNAL_GENESIS_BINDING_CHANGED')
            row = self.db.execute('SELECT state FROM journal_intents WHERE name=?', (name,)).fetchone()
            require(row is not None, 'STARTUP_JOURNAL_NOT_OWNER_AUTHORIZED')
            state = row[0]
            if state == 'CONSUMED':
                require(os.path.lexists(path), 'STARTUP_CONSUMED_JOURNAL_MISSING')
                private_bytes(path)
                return
            require(genesis_envelope == record['initial_envelope'], 'STARTUP_JOURNAL_INITIAL_ENVELOPE_CHANGED')
            expected = canonical(genesis_envelope) + b'\n'
            self._genesis_heads(gate)
            if state == 'UNUSED':
                if os.path.lexists(path):
                    require(private_bytes(path) == expected, 'STARTUP_PREEXISTING_GENESIS_DIFFERS')
                self._transition(name, 'UNUSED', 'INTENT', expected)
                if not os.path.lexists(path):
                    # Owner provisioning authorized these exact complete bytes.
                    # Do not overwrite, truncate, infer a new epoch, or retry
                    # after an uncertain write. The durable INTENT survives.
                    try:
                        protected(Path(path).parent, directory=True)
                        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
                        try:
                            with os.fdopen(os.dup(fd), 'wb') as stream:
                                stream.write(expected)
                                stream.flush()
                                os.fsync(stream.fileno())
                        finally:
                            os.close(fd)
                        directory = os.open(Path(path).parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
                        try:
                            os.fsync(directory)
                        finally:
                            os.close(directory)
                    except BaseException:
                        self.poisoned = True
                        raise
            require(os.path.lexists(path), 'STARTUP_GENESIS_INTENT_MISSING_FILE_REVIEW_REQUIRED')
            # Every admitted present path follows this ordering, including a
            # preexisting UNUSED file and an exact present restart INTENT file.
            # Exact bytes alone do not establish durable file/directory state.
            self._sync_genesis(path, expected)
            self._transition(name, 'INTENT', 'CONSUMED', expected)

    def _sync_genesis(self, path, expected):
        file_fd = directory_fd = None
        try:
            path = Path(path)
            named = protected(path)
            parent = protected(path.parent, directory=True)
            file_fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
            directory_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY |
                                   os.O_NOFOLLOW | os.O_CLOEXEC)
            held, directory = os.fstat(file_fd), os.fstat(directory_fd)
            require(held.st_nlink == 1 and
                    (held.st_dev, held.st_ino) == (named.st_dev, named.st_ino) and
                    (directory.st_dev, directory.st_ino) == (parent.st_dev, parent.st_ino),
                    'STARTUP_GENESIS_SYNC_IDENTITY_CHANGED')
            with os.fdopen(os.dup(file_fd), 'rb') as stream:
                require(stream.read() == expected, 'STARTUP_GENESIS_INTENT_BYTES_CHANGED')
            os.fsync(file_fd)
            os.fsync(directory_fd)
            after = os.fstat(file_fd)
            current, current_parent = protected(path), protected(path.parent, directory=True)
            require((held.st_dev, held.st_ino, held.st_size, held.st_mtime_ns, held.st_ctime_ns) ==
                    (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns) and
                    (current.st_dev, current.st_ino) == (held.st_dev, held.st_ino) and
                    (current_parent.st_dev, current_parent.st_ino) == (directory.st_dev, directory.st_ino),
                    'STARTUP_GENESIS_SYNC_READBACK_CHANGED')
            require(private_bytes(path) == expected, 'STARTUP_GENESIS_SYNC_BYTES_CHANGED')
        except BaseException:
            # An uncertain sync/readback cannot lead to a consuming CAS or retry
            # in this lease; its already durable INTENT remains retained.
            self.poisoned = True
            raise
        finally:
            primary = sys.exc_info()[1]
            failures = []
            for retained in (directory_fd, file_fd):
                if retained is not None:
                    try:
                        os.close(retained)
                    except BaseException as exc:
                        failures.append(exc)
            if failures:
                self.poisoned = True
                self.genesis_sync_close_errors = failures
                if primary is None:
                    raise StartupRefusal('STARTUP_GENESIS_SYNC_CLOSE_UNKNOWN') from failures[0]

    def _transition(self, name, before, after, expected):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            changed = self.db.execute('UPDATE journal_intents SET state=? WHERE name=? AND state=?', (after, name, before)).rowcount
            require(changed == 1, 'STARTUP_BOOTSTRAP_CAS_CHANGED')
            self.db.execute('INSERT INTO journal_history(name,prior,state,envelope_sha256) VALUES(?,?,?,?)',
                            (name, before, after, digest(expected)))
            self.db.execute('COMMIT')
        except BaseException:
            if self.db.in_transaction:
                self.db.execute('ROLLBACK')
            self.poisoned = True
            raise
        try:
            require(self.db.execute('SELECT state FROM journal_intents WHERE name=?', (name,)).fetchone() == (after,),
                    'STARTUP_BOOTSTRAP_READBACK_CHANGED')
        except BaseException:
            self.poisoned = True
            raise

    def construct(self):
        """Actual classes, selected from the complete protected source inventory."""
        self.intact()
        runtime = self.spec['runtime']
        # Import roots must already be fixed by the isolated operator launcher.
        # Never add an ordinary request's sys.path or native library selection.
        from .paths import WorldlinePaths
        from .store import StateStore, STORE_SCHEMA_VERSION
        from .controller import RuntimeController
        from .config import GlobalConfig
        from .capabilities import CapabilityRegistry
        from .core import Core
        from .proof_manifest import contract_problems, manifest_problems
        gate_module = importlib.import_module('intent_gate')
        principal_module = importlib.import_module('recovery_principal')
        require(Path(gate_module.__file__) == Path(runtime['gate_source']) and
                Path(principal_module.__file__) == Path(runtime['principal_source']), 'STARTUP_PRINCIPAL_PROCESS_SOURCE_CHANGED')
        require('startup_lease' in inspect.signature(principal_module.ProtectedRecoveryPrincipal).parameters,
                'STARTUP_QUALIFIED_PRINCIPAL_LEASE_INTERFACE_UNAVAILABLE')
        self.loaded()
        source = Path(runtime['worldline_source'])
        library = Path(runtime['native_library'])
        proof = exact_json(private_bytes(runtime['proof_manifest']), canonical_required=False)
        require(not contract_problems(source) and not manifest_problems(proof, source, library=library,
                summary=private_bytes(runtime['proof_summary']), require_summary=True), 'STARTUP_EXACT_NATIVE_PROOF_UNAVAILABLE')
        core = Core(library)
        self.loaded()
        values = self.spec['paths']
        paths = WorldlinePaths(**{name: Path(values[name]) for name in ('home', 'data', 'state', 'runtime', 'config')})
        self.gate = gate_module.Gate(Path(values['authority_root']) / 'authority/gate/config.json')
        require(self.gate.config['requester_uid'] == self.spec['endpoint']['requester_uid'], 'STARTUP_GATE_ENDPOINT_REQUESTER_CHANGED')
        self.intact()
        self.store = StateStore(paths, core, startup_lease=self)
        config = GlobalConfig(paths, exact_json(private_bytes(paths.config / 'config.json'), canonical_required=False))
        capabilities = CapabilityRegistry(paths, startup_lease=self)
        self.controller = RuntimeController(paths, self.store, config, capabilities, core=core, startup_lease=self)
        self.principal = principal_module.ProtectedRecoveryPrincipal(self.gate, self.controller, startup_lease=self)
        self.loaded()
        self.intact()
        return self.principal

    def close(self):
        if self.closed:
            return
        # Close target owners while every lease lock is still retained. A
        # cleanup failure retains the lease for diagnostics/operator recovery.
        errors = []
        for owner in (self.controller, self.store,
                      getattr(self.gate, 'issuer', None), getattr(self.gate, 'universe', None)):
            if owner is not None:
                try:
                    owner.close()
                except BaseException as exc:
                    errors.append(exc)
        if errors:
            self.poisoned = True
            raise StartupRefusal('STARTUP_TARGET_CLOSE_UNKNOWN') from errors[0]
        self.closed = True
        if hasattr(self, 'db'):
            self.db.close()
        # Target objects must be closed before their lease, retaining every
        # original file. Failure is reported; no stale socket/history is removed.
        for path in reversed(tuple(self.fds)):
            os.close(self.fds[path])
        self.fds.clear()


class IntentDispatcher:
    """Only identifiers reach the actual protected principal; no packets/verdicts."""
    def __init__(self, lease, principal=None, startup_error=None):
        require(type(lease) is StartupLease, 'STARTUP_EXACT_LEASE_REQUIRED')
        self.lease, self.principal, self.startup_error = lease, principal, startup_error

    def handle(self, connection, request):
        require(type(request) is dict and type(request.get('method')) is str, 'STARTUP_INTENT_SCHEMA')
        require(type(connection) is socket.socket and connection.family == socket.AF_UNIX, 'STARTUP_UNIX_PEER_REQUIRED')
        _pid, uid, _gid = struct.unpack('iII', connection.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize('iII')))
        require(uid in (0, self.lease.spec['endpoint']['requester_uid']), 'STARTUP_PEER_REFUSED')
        if request == {'method': 'diagnostics'}:
            return {'state': 'QUARANTINED' if self.startup_error is not None else 'SOURCE_DEPENDENCIES_BOUND',
                    'release_gate': 'BLOCKED', 'startup_error': self.startup_error,
                    'original_guarantees': 'OPEN_UNCHANGED'}
        require(self.startup_error is None and self.principal is not None, 'STARTUP_AUTHORITY_QUARANTINED')
        self.lease.intact()
        method = request['method']
        key = 'transaction' if method == 'issue' else 'operation'
        require(method in ('issue', 'claim', 'recover') and set(request) == {'method', key} and
                type(request[key]) is str and request[key], 'STARTUP_IDENTIFIER_ONLY_INTENT_REQUIRED')
        # Actual principal derives the requester from SO_PEERCRED, reads its
        # retained operation, and makes native full-binding decisions itself.
        return getattr(self.principal, method)(connection, request[key])


class IntentHandler(socketserver.BaseRequestHandler):
    def handle(self):
        raw = bytearray()
        try:
            while True:
                part = self.request.recv(65536)
                require(part, 'STARTUP_INTENT_FRAME_INCOMPLETE')
                raw.extend(part)
                if b'\n' in part:
                    break
            require(raw.endswith(b'\n') and raw.count(b'\n') == 1, 'STARTUP_INTENT_FRAME_INVALID')
            response = self.server.dispatcher.handle(self.request, exact_json(bytes(raw[:-1])))
        except Exception as exc:
            response = {'state': 'REFUSED', 'reason': str(exc), 'release_gate': 'BLOCKED'}
        self.request.sendall(canonical(response) + b'\n')


class IntentServer(socketserver.UnixStreamServer):
    """Separate pre-provisioned endpoint directory; legacy routes stay absent."""
    def __init__(self, path, dispatcher):
        require(type(dispatcher) is IntentDispatcher, 'STARTUP_DISPATCHER_REQUIRED')
        protected(Path(path).parent, directory=True)
        require(Path(path) == Path(dispatcher.lease.spec['endpoint']['path']), 'STARTUP_ENDPOINT_PATH_CHANGED')
        require(not os.path.lexists(path), 'STARTUP_INTENT_ENDPOINT_ALREADY_PRESENT')
        self.dispatcher = dispatcher
        super().__init__(str(path), IntentHandler)
        # Access credentials belong to the owner operator package; a process
        # cannot derive a requester group from untrusted intent input.
        os.chown(path, 0, dispatcher.lease.spec['endpoint']['requester_gid'])
        os.chmod(path, 0o660)


def serve(descriptor):
    """Operator-only start: construction failure retains lease and diagnostics."""
    lease = StartupLease(descriptor)
    try:
        try:
            principal = lease.construct()
        except Exception as exc:
            dispatcher = IntentDispatcher(lease, startup_error=str(exc))
        else:
            dispatcher = IntentDispatcher(lease, principal=principal)
        with IntentServer(lease.spec['endpoint']['path'], dispatcher) as server:
            server.serve_forever()
    finally:
        lease.close()
