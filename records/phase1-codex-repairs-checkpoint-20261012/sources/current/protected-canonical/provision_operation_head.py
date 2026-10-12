"""Exclusive offline operation-head owner provisioning; never startup.

Every effect follows the dedicated genuine native Bootstrap action over actual
original owner/grant/source/genesis/HMAC/SQL/syscall observations. Neither the
two-journal owner action nor normal OJ Stable/recovery is creation permission.
Partial creations are retained on failure: no overwrite, retry or fake CONSUMED.
"""
from __future__ import annotations
import sys
_loader = sys.modules.get('_worldline_approved_source_loader')
if _loader is None:
    raise SystemExit('OPERATION_BOOTSTRAP_EARLY_SOURCE_REQUIRED')
_source = _loader.current()
_source.check()
import argparse
import ctypes as C
import hashlib
import importlib
import json
import os
from pathlib import Path
import sqlite3

SCHEMA_SQL = (
    'CREATE TABLE canonical_operation_head(name TEXT PRIMARY KEY,installation TEXT NOT NULL,'
    'genesis TEXT NOT NULL,head TEXT NOT NULL,state TEXT NOT NULL,prior_envelope BLOB,next_envelope BLOB);'
    'CREATE TABLE canonical_operation_admission(name TEXT PRIMARY KEY,installation TEXT NOT NULL,'
    'genesis TEXT NOT NULL,owner_envelope BLOB NOT NULL,initial_envelope TEXT NOT NULL,state TEXT NOT NULL);')
SYMBOL = 'wl_custody_operation_bootstrap_decide_v2'


def require(value, reason):
    if not value:
        raise RuntimeError(reason)


def write(path, raw):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    try:
        with os.fdopen(os.dup(fd), 'wb') as stream:
            stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    finally:
        os.close(fd)
    directory = os.open(Path(path).parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try: os.fsync(directory)
    finally: os.close(directory)


def original_paths(spec, core):
    root = Path(spec['paths']['authority_root'])
    gate = root / 'authority/gate/state'; issuer = root / 'authority/issuer/state'
    resource = root / 'authority/resource'; scoped = str(resource / 'run-scoped-config-v1.json')
    return {'owner': {'policy': str(gate / 'owner-policy.json'), 'genesis': str(gate / 'owner-genesis.json'),
        'bootstrap': str(gate / 'owner-bootstrap.json'), 'journal': str(gate / 'owner-transitions.json'),
        'head': str(gate / 'owner-head.json'), 'mutation_intent': str(gate / 'owner-mutation-intent.json')},
        'issuer_key': str(issuer / 'issuer-key.bin'),
        'operation_policy': str(issuer / 'worldline-operation-policy.json'), 'native': str(core.library_path),
        'original_config': str(resource / 'run-config-v1.json'),
        'original_database': str(resource / 'run-state-v1/ledger.sqlite'), 'scoped_config': scoped,
        'scoped_database': None if scoped is None else str(resource / 'run-scoped-state-v1/ledger.sqlite'),
        'store_database': str(Path(spec['paths']['state']) / 'worldline.sqlite3'),
        'universe_genesis': str(root / 'authority/universe/root/genesis.json')}


class Operator:
    def __init__(self, request_path):
        self.lease = self.guard = self.target = self.db = None
        self.records = []
        try:
            self.initialize(request_path)
        except BaseException:
            self.close()
            raise

    def initialize(self, request_path):
        self.request_raw = _source.file(request_path, ('DATA',))
        request = json.loads(self.request_raw)
        require(set(request) == {'schema', 'descriptor', 'mode', 'import_roots', 'export_directory'}
                and request['schema'] == 'worldline.original-operation-head-bootstrap-request-v1'
                and request['mode'] in ('CREATE', 'REUSE'), 'OPERATION_BOOTSTRAP_EXACT_OPERATOR_REQUEST')
        self.request = request; self.lease = self.guard = self.target = self.db = None
        self.records = []
        descriptor_raw = _source.file(request['descriptor'], ('DATA',))
        self.spec = json.loads(descriptor_raw)
        root = Path(self.spec['paths']['authority_root'])
        require(root.parent == Path('/srv') and root.name.startswith('cosmogony-canonical-v1.control-'),
                'OPERATION_BOOTSTRAP_EXPLICIT_DISPOSABLE_ONLY')
        self.path = root / 'authority/issuer/state/worldline-operation-head.sqlite'
        self.out = Path(request['export_directory'])
        require(self.out.is_relative_to(root) and self.out.is_dir() and not self.out.is_symlink()
                and self.out.stat().st_uid == 0 and not self.out.stat().st_mode & 0o077,
                'OPERATION_BOOTSTRAP_PRECREATED_PRIVATE_EXPORT_REQUIRED')
        expected_entry = Path(self.spec['runtime']['worldline_source']) / 'protected-canonical/provision_operation_head.py'
        require(Path(__file__) == expected_entry and sys.argv[0] == str(expected_entry)
                and _source.files.get(str(expected_entry), (None,))[0] == 'ENTRY',
                'OPERATION_BOOTSTRAP_EXACT_ORIGINAL_OWNER_ENTRY_REQUIRED')
        controls = expected_entry.parent.parent / 'protected-root/controls'
        for root_path in (*request['import_roots'], str(controls)):
            _source.directory_or_absent(root_path)
        sys.path[:0] = [*request['import_roots'], str(controls)]
        from head_target import HeadTarget
        from worldline.protected_startup import StartupLease, private_bytes, exact_json
        from worldline.custody_operation_sources import capture_kernel_material
        if request['mode'] == 'CREATE':
            # Hold the original locks/store, but do not consume journal
            # admissions before the dedicated native absence-slot decision.
            self.lease = StartupLease(request['descriptor'], operation_head_creation=self.path)
            core = self.lease._owner_admission_core()
            gate_module = importlib.import_module('intent_gate')
            self.lease.gate = self.lease._construct_gate(gate_module)
            gate = self.lease.gate
            for name, record in self.lease.genesis['journals'].items():
                self.lease.capture_journal_admission(gate, name, Path(record['path']), record['initial_envelope'])
            self.sources = {'spec': self.lease.spec, 'genesis': self.lease.genesis,
                'genesis_raw': self.lease.genesis_raw, 'descriptor_path': self.lease.descriptor_path,
                'descriptor_raw': self.lease.descriptor_raw, 'issuer_state': gate.issuer.state,
                'source_lease': self.lease.source_lease, 'held_fds': dict(self.lease.fds),
                'store_initial_snapshot': self.lease.store_initial_snapshot,
                'store_initial_snapshot_raw': self.lease.store_initial_snapshot_raw,
                'store_initial_head': self.lease.store_initial_head, 'bootstrap_connection': self.lease.db}
            self.sources['held_fds'].update({gate.issuer.state / 'issuer.lock': gate.issuer.lock_fd,
                                          gate.universe.state / 'universe.lock': gate.universe.lock_fd})
            self.gate_raw = gate.config_raw
        else:
            # Reuse must not invoke the absence-only slot or normal controller
            # effects. All owner/grant/resource/native validation is native over
            # complete independently captured original source bytes.
            from offline_owner_guard import OriginalOwnerGuard
            self.guard = OriginalOwnerGuard(request['descriptor']); self.guard.__enter__()
            facts = self.guard.readfacts()
            self.sources = {name: facts[name] for name in ('spec', 'genesis', 'genesis_raw',
                'descriptor_path', 'descriptor_raw', 'issuer_state', 'source_lease', 'held_fds',
                'store_initial_snapshot', 'store_initial_snapshot_raw', 'store_initial_head')}
            from worldline.core import Core
            from worldline.proof_manifest import contract_problems, manifest_problems
            runtime = self.spec['runtime']; library = Path(runtime['native_library'])
            proof = exact_json(private_bytes(runtime['proof_manifest']), canonical_required=False)
            require(not contract_problems(Path(runtime['worldline_source'])) and not manifest_problems(
                proof, Path(runtime['worldline_source']), library=library,
                summary=private_bytes(runtime['proof_summary']), require_summary=True),
                'OPERATION_BOOTSTRAP_EXACT_EXISTING_NATIVE_PROOF_REQUIRED')
            core = Core(library)
            self.gate_raw = private_bytes(root / 'authority/gate/config.json')
        self.core = core
        recovery = exact_json(private_bytes(root / 'authority/gate/recovery-bind.json'))
        self.kernel_material = capture_kernel_material(core, recovery['kernel_build'])
        self.paths = original_paths(self.spec, core)
        self.target = HeadTarget(self.path, _source)
        self.function = getattr(core._lib, SYMBOL)
        self.function.argtypes = (C.c_void_p, C.c_size_t, C.POINTER(C.c_uint64), C.POINTER(C.c_uint64))
        self.function.restype = C.c_int
        address = C.cast(self.function, C.c_void_p).value
        library = Path(core.library_path)
        info = library.stat()
        matching = []
        for line in Path('/proc/self/maps').read_text().splitlines():
            fields = line.split(maxsplit=5)
            if len(fields) != 6:
                continue
            extent, permissions, offset, device, inode, named = fields
            first, last = (int(value, 16) for value in extent.split('-'))
            if (address is not None and first <= address < last and 'x' in permissions
                    and named == str(library) and int(inode) == info.st_ino
                    and device == f'{os.major(info.st_dev):02x}:{os.minor(info.st_dev):02x}'):
                matching.append(line)
        require(len(matching) == 1, 'OPERATION_BOOTSTRAP_SELECTED_NATIVE_SYMBOL_MAPPING_DIFFERS')
        self.symbol_mapping = {'symbol': SYMBOL, 'address': address, 'maps_line': matching[0]}

    def observe(self, expected=None):
        from worldline.custody_startup_capture import capture_original_admission_roster
        from worldline.root_worker_current_state import _capture_operation_sources
        from worldline.root_worker_codec import scoped_archive
        artifact = self.target.capture()
        name = 'recovery-full-journal'
        original = self.sources['genesis']['journals'][name]['initial_envelope']
        roster = capture_original_admission_roster(**self.sources, name=name,
            initial_envelope=original, head_capture=artifact)
        context = _capture_operation_sources(self.spec, self.sources['genesis_raw'], self.gate_raw,
            self.paths, self.kernel_material, core=self.core, source_lease=_source, head_capture=artifact)
        roster['operation_context'] = context
        bootstrap = {'path': str(self.path), 'entry': sys.argv[0], 'arguments': list(sys.argv),
            'actor': {'status': Path('/proc/self/status').read_bytes(), 'stat': Path('/proc/self/stat').read_bytes(),
                      'exe': os.fsencode(os.readlink('/proc/self/exe'))},
            'source_profile': roster['startup_admission'], 'artifact': artifact,
            'creation': self.target.creation, 'sync': self.target.sync_receipt}
        material = {'schema': 'worldline.operation-head-bootstrap-v1', 'owner_roster': roster,
                    'bootstrap': bootstrap}
        raw = scoped_archive(material)
        actor_pid = os.getpid(); actor_euid = os.geteuid()
        buffer = C.create_string_buffer(raw); status = C.c_uint64(); position = C.c_uint64()
        transport = self.function(C.cast(buffer, C.c_void_p), len(raw), C.byref(status), C.byref(position))
        require(transport == 0 and status.value in (0, 1, 2), 'OPERATION_BOOTSTRAP_NATIVE_TRANSPORT_OR_ENUM_REFUSED')
        index = len(self.records); filename = 'bootstrap-' + str(index) + '.archive'
        write(self.out / filename, raw)
        self.records.append({'input': filename, 'sha256': hashlib.sha256(raw).hexdigest(),
            'native_status': status.value, 'native_position': position.value, 'original_command': list(sys.argv),
            'actual_pid': actor_pid, 'actual_euid': actor_euid,
            'bootstrap_action': ('Bootstrap_Refused', 'Create_Fresh', 'Reuse_Authentic')[status.value],
            'native_symbol_mapping': self.symbol_mapping,
            'selected_source': _source.check()})
        require(status.value != 0, 'OPERATION_BOOTSTRAP_NATIVE_REFUSED_' + str(position.value))
        if expected is not None:
            require((status.value, position.value) == expected, 'OPERATION_BOOTSTRAP_NATIVE_NEXT_EFFECT_CHANGED')
        return raw, material, status.value, position.value

    def run(self):
        raw, material, action, position = self.observe()
        if action == 2:
            require(self.request['mode'] == 'REUSE' and position == 4,
                    'OPERATION_BOOTSTRAP_AUTHENTIC_REUSE_DOMAIN_CHANGED')
            self.target.release_capture()
            return
        require(self.request['mode'] == 'CREATE' and (action, position) == (1, 0),
                'OPERATION_BOOTSTRAP_NATIVE_EXCLUSIVE_CREATE_REQUIRED')
        self.target.exclusive_open(raw, material['bootstrap']['artifact'])
        self.observe((1, 1)); self.target.release_capture()
        self.db = sqlite3.connect(self.path.as_uri() + '?mode=rw', uri=True, isolation_level=None)
        mode = self.db.execute('PRAGMA journal_mode=WAL').fetchone()
        require(mode == ('wal',), 'OPERATION_BOOTSTRAP_ORIGINAL_WAL_SETUP_REFUSED')
        self.db.execute('PRAGMA synchronous=FULL'); self.db.execute('PRAGMA foreign_keys=ON')
        self.db.executescript('BEGIN IMMEDIATE;' + SCHEMA_SQL + 'COMMIT;')
        _, _, _, _ = self.observe((1, 2)); self.target.release_capture()
        from worldline.protected_startup import private_bytes, exact_json, digest
        from worldline.operation_capture import archive
        policy = exact_json(private_bytes(self.paths['operation_policy']))
        owner_raw = private_bytes(policy['genesis_file']); owner = exact_json(owner_raw)
        initial = owner['body']['initial_envelope']
        journal_raw = private_bytes(policy['journal'])
        self.db.execute('BEGIN IMMEDIATE')
        try:
            self.db.execute('INSERT INTO canonical_operation_head VALUES(?,?,?,?,?,?,?)',
                ('worldline-operations', self.spec['installation_id'], policy['genesis'], digest(journal_raw),
                 'STABLE', None, None))
            self.db.execute('INSERT INTO canonical_operation_admission VALUES(?,?,?,?,?,?)',
                ('worldline-operations', self.spec['installation_id'], policy['genesis'], owner_raw,
                 archive(initial).hex(), 'CONSUMED'))
            self.db.execute('COMMIT')
        except BaseException:
            if self.db.in_transaction: self.db.execute('ROLLBACK')
            raise
        self.observe((1, 3)); self.target.release_capture()
        self.target.sync()
        self.observe((2, 4)); self.target.release_capture()

    def close(self):
        errors = []
        for close in (None if self.db is None else self.db.close,
                      None if self.target is None else self.target.close,
                      None if self.lease is None else self.lease.close,
                      None if self.guard is None else lambda: self.guard.__exit__(None, None, None)):
            if close is not None:
                try: close()
                except BaseException as error: errors.append(error)
        if errors:
            primary = sys.exc_info()[1]
            if primary is None: raise errors[0]
            for error in errors: primary.add_note('Original offline owner close failed: ' + repr(error))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', required=True)
    args = parser.parse_args()
    require(os.geteuid() == 0 and sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode,
            'OPERATION_BOOTSTRAP_EXPLICIT_ROOT_I_S_B_REQUIRED')
    operator = None; failure = None
    try:
        operator = Operator(args.request)
        operator.run()
    except BaseException as error:
        failure = {'type': type(error).__qualname__, 'message': str(error), 'args': tuple(error.args)}
        raise
    finally:
        if operator is not None:
            try:
                write(operator.out / 'bootstrap-result.json', json.dumps({
                    'schema': 'worldline.original-operation-head-bootstrap-result-v1',
                    'request_sha256': hashlib.sha256(operator.request_raw).hexdigest(),
                    'records': operator.records, 'actual_error': failure, 'schema_sql': SCHEMA_SQL,
                    'phase_acceptance': False}, sort_keys=True, separators=(',', ':'), default=str).encode() + b'\n')
            finally: operator.close()


if __name__ == '__main__':
    main()
