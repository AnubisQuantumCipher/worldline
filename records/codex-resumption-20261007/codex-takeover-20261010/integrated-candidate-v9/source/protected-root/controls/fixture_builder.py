"""Explicit offline creation of one owner-selected disposable original fixture.

Run materialize and initialize under separately qualified early envelopes. An
initializer never runs under the materializer's old ABSENT/source selection.
The plan contains exact original owner inputs, not authority verdicts. Partial
creation is retained; neither this utility nor ordinary startup repairs it.
"""
from __future__ import annotations
import sys
_approved = sys.modules.get('_worldline_approved_source_loader')
if _approved is None:
    raise SystemExit('FIXTURE_EARLY_APPROVED_SOURCE_REQUIRED')
_lease = _approved.current()
if type(_lease) is not _approved.ApprovedSourceLease:
    raise SystemExit('FIXTURE_ACTUAL_EARLY_LEASE_REQUIRED')
_lease.check()
import argparse
import hashlib
import hmac
import importlib
import json
import os
from pathlib import Path
import sqlite3
import stat

SCHEMA = 'worldline.original-custody-fixture-construction-v2'


def require(value, reason):
    if not value:
        raise RuntimeError(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode('utf-8')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def exact(raw):
    def pairs(items):
        value = {}
        for key, item in items:
            require(key not in value, 'FIXTURE_DUPLICATE_JSON_KEY')
            value[key] = item
        return value
    value = json.loads(raw, object_pairs_hook=pairs,
                       parse_constant=lambda _: require(False, 'FIXTURE_NONFINITE_JSON'))
    require(raw in (canonical(value), canonical(value) + b'\n'), 'FIXTURE_CANONICAL_PLAN_REQUIRED')
    return value


def selected(path, roles=('DATA',)):
    return _lease.file(str(path), roles)


def protected(path, directory=False):
    path = Path(path)
    require(path.is_absolute() and str(path) == os.path.normpath(path), 'FIXTURE_PATH_SPELLING')
    for part in (*reversed(path.parents), path):
        info = part.lstat()
        require(info.st_uid == 0 and not stat.S_ISLNK(info.st_mode) and not info.st_mode & 0o022,
                'FIXTURE_PROTECTED_ANCESTRY_REQUIRED')
        if part != path or directory:
            require(stat.S_ISDIR(info.st_mode), 'FIXTURE_DIRECTORY_REQUIRED')
        else:
            require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, 'FIXTURE_SINGLE_REGULAR_FILE_REQUIRED')
    return path


def sync(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def create(path, raw, mode=0o600):
    protected(path.parent, True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, mode)
    try:
        with os.fdopen(os.dup(fd), 'wb') as output:
            output.write(raw)
            output.flush()
            os.fsync(output.fileno())
    finally:
        os.close(fd)
    sync(path.parent)
    require(path.read_bytes() == raw, 'FIXTURE_EXCLUSIVE_WRITE_READBACK_CHANGED')


def inventory(root):
    result = {}
    for path in (root, *sorted(root.rglob('*'))):
        info = path.lstat()
        require(not stat.S_ISLNK(info.st_mode), 'FIXTURE_SYMLINK_IN_CONSTRUCTION')
        row = {'mode': oct(stat.S_IMODE(info.st_mode)), 'uid': info.st_uid, 'gid': info.st_gid,
               'device': info.st_dev, 'inode': info.st_ino, 'links': info.st_nlink}
        if stat.S_ISREG(info.st_mode):
            require(info.st_nlink == 1, 'FIXTURE_CONSTRUCTION_EXTERNAL_HARDLINK')
            row.update(kind='file', sha256=sha(path.read_bytes()))
        elif stat.S_ISSOCK(info.st_mode):
            row['kind'] = 'socket'
        elif stat.S_ISFIFO(info.st_mode):
            row['kind'] = 'fifo'
        else:
            require(stat.S_ISDIR(info.st_mode), 'FIXTURE_UNEXPECTED_CONSTRUCTION_NODE')
            row['kind'] = 'directory'
        result[path.relative_to(root).as_posix()] = row
    return result


class Builder:
    def __init__(self, path, stage):
        require(os.geteuid() == 0 and sys.flags.isolated and sys.flags.no_site
                and sys.dont_write_bytecode, 'FIXTURE_EXPLICIT_ROOT_I_S_B_REQUIRED')
        self.raw = selected(path)
        self.plan = exact(self.raw)
        require(set(self.plan) == {'schema', 'operator_authorization', 'root', 'guard', 'directories',
                'files', 'import_roots', 'owner_inputs', 'expected_absent'}, 'FIXTURE_PLAN_KEYSET')
        require(self.plan['schema'] == SCHEMA, 'FIXTURE_PLAN_SCHEMA')
        _lease.directory_or_absent(str(Path(__file__).parent))
        sys.path.insert(0, str(Path(__file__).parent))
        from construction_registry import bind
        self.plan['owner_actions'] = bind(self.plan['owner_inputs'])
        self.root = Path(self.plan['root'])
        require(self.root.is_absolute() and self.root.parent == Path('/srv')
                and self.root.name.startswith('cosmogony-canonical-v1.control-')
                and str(self.root) == os.path.normpath(self.root), 'FIXTURE_DISPOSABLE_ROOT_ONLY')
        authorization = self.plan['operator_authorization']
        require(type(authorization) is str and authorization == 'EXCLUSIVE OFFLINE DISPOSABLE ' + str(self.root),
                'FIXTURE_EXACT_OFFLINE_OPERATOR_ACTION_REQUIRED')
        guard = exact(selected(self.plan['guard']))
        require(set(guard) == {'schema', 'root', 'operator_entry', 'cgroup', 'plan_sha256'}
                and guard['schema'] == 'worldline.offline-disposable-fixture-guard-v1'
                and guard['root'] == str(self.root) and guard['operator_entry'] == __file__
                and guard['plan_sha256'] == sha(self.raw)
                and guard['cgroup'] == Path('/proc/self/cgroup').read_text(),
                'FIXTURE_ACTUAL_SELECTED_OPERATOR_SCOPE_REQUIRED')
        protected(self.root.parent, True)
        self.stage = stage
        self.actions = []
        self.results = {}
        self.objects = {}
        self.supervisors = {}
        self.closers = []
        self.before = None

    def target(self, relative):
        require(type(relative) is str and relative and not relative.startswith('/')
                and all(part not in ('', '.', '..') for part in relative.split('/')),
                'FIXTURE_EXACT_RELATIVE_TARGET_REQUIRED')
        return self.root / relative

    def data(self, path):
        return exact(selected(path))

    def module(self, name, source):
        _lease.check()
        role = _lease.files.get(source, (None,))[0]
        require(role in ('SOURCE', 'ENTRY'), 'FIXTURE_OWNER_SOURCE_NOT_SELECTED')
        selected(source, (role,))
        module = importlib.import_module(name)
        require(module.__file__ == source, 'FIXTURE_ORIGINAL_OWNER_MODULE_LOCATION_SPLIT')
        _lease.check()
        return module

    def materialize(self):
        require(not os.path.lexists(self.root), 'FIXTURE_ROOT_ALREADY_EXISTS')
        self.root.mkdir(mode=0o700)
        sync(self.root.parent)
        for record in self.plan['directories']:
            require(set(record) == {'path', 'mode'}, 'FIXTURE_DIRECTORY_RECORD')
            path = self.target(record['path'])
            mode = int(record['mode'], 8)
            require(mode & 0o022 == 0 and mode & ~0o777 == 0, 'FIXTURE_DIRECTORY_MODE')
            protected(path.parent, True)
            path.mkdir(mode=mode)
            sync(path.parent)
        for record in self.plan['files']:
            require(set(record) == {'path', 'source', 'sha256', 'mode'}, 'FIXTURE_ORIGINAL_FILE_RECORD')
            source = record['source']
            role = _lease.files.get(source, (None,))[0]
            require(role is not None, 'FIXTURE_ORIGINAL_INPUT_NOT_SELECTED')
            raw = selected(source, (role,))
            require(sha(raw) == record['sha256'], 'FIXTURE_ORIGINAL_INPUT_BYTES_CHANGED')
            mode = int(record['mode'], 8)
            require(mode & 0o022 == 0 and mode & ~0o777 == 0, 'FIXTURE_FILE_MODE')
            create(self.target(record['path']), raw, mode)
        for relative in self.plan['expected_absent']:
            require(not os.path.lexists(self.target(relative)), 'FIXTURE_ORIGINAL_CREATION_SLOT_PRESENT')

    def initialize(self):
        protected(self.root, True)
        self.before = inventory(self.root)
        require('materialized.json' in self.before and 'initialized.json' not in self.before,
                'FIXTURE_SEPARATE_EXCLUSIVE_INITIALIZATION_REQUIRED')
        materialized = exact((self.root / 'materialized.json').read_bytes())
        require(materialized['plan_sha256'] == sha(self.raw), 'FIXTURE_PLAN_CHANGED_BETWEEN_STAGES')
        actual = dict(self.before)
        del actual['materialized.json']
        require(actual == materialized['inventory'], 'FIXTURE_MATERIALIZED_PREIMAGE_CHANGED')
        for root in self.plan['import_roots']:
            _lease.directory_or_absent(root)
        sys.path[:0] = self.plan['import_roots']
        _lease.directory_or_absent(str(Path(__file__).parent))
        sys.path.insert(0, str(Path(__file__).parent))
        for index, action in enumerate(self.plan['owner_actions']):
            if action['kind'] == 'owner-entry':
                continue
            _lease.check()
            require(action['name'] not in self.results, 'FIXTURE_OWNER_ACTION_NAME_REUSED')
            before = inventory(self.root)
            result = self.owner_action(action)
            self.results[action['name']] = result
            self.actions.append({'index': index, 'original_action': action, 'result': result,
                                 'before': before, 'after': inventory(self.root)})
        for relative in self.plan['expected_absent']:
            require(not os.path.lexists(self.target(relative)), 'FIXTURE_REQUIRED_ABSENCE_REPLACED')

    def provision(self):
        protected(self.root, True)
        marker_path = self.root / 'initialized.json'
        initialized_raw = selected(marker_path)
        marker = exact(initialized_raw)
        require(marker['stage'] == 'initialize' and marker['plan_sha256'] == sha(self.raw)
                and not os.path.lexists(self.root / 'provisioned.json'),
                'FIXTURE_SEPARATE_EXCLUSIVE_NATIVE_OWNER_PROVISION_REQUIRED')
        actual = inventory(self.root)
        del actual['initialized.json']
        require(actual == marker['inventory'], 'FIXTURE_OWNER_INITIALIZATION_PREIMAGE_CHANGED')
        entries = [(index, action) for index, action in enumerate(self.plan['owner_actions'])
                   if action['kind'] == 'owner-entry']
        require(entries, 'FIXTURE_GENUINE_ORIGINAL_OWNER_ENTRIES_REQUIRED')
        for index, action in entries:
            _lease.check()
            before = inventory(self.root)
            result = self.owner_action(action)
            self.actions.append({'index': index, 'original_action': action, 'result': result,
                                 'before': before, 'after': inventory(self.root)})
        require(selected(marker_path) == initialized_raw, 'FIXTURE_ORIGINAL_OWNER_EVIDENCE_CHANGED')

    def owner_action(self, action):
        kind = action['kind']
        if kind == 'worldline-store':
            from worldline.paths import WorldlinePaths
            from worldline.core import Core
            from worldline.store import StateStore
            self.module('worldline.store', action['source'])
            paths = WorldlinePaths(**{key: self.target(value) for key, value in action['paths'].items()})
            require(not os.path.lexists(paths.database), 'FIXTURE_STORE_MUST_BE_NEW')
            create(paths.database, b'')
            core = Core(Path(action['library']))
            store = StateStore(paths, core)
            try:
                # This calls the original explicit owned creation APIs, including
                # all five native producer journals, not handcrafted SQLite rows.
                store.ensure_finalization_journal()
                import uuid
                store_identity = str(uuid.uuid4())
                store.set_meta('protectedStoreGenesis', store_identity)
                from worldline.protected_startup import store_snapshot
                result = store_snapshot(paths.database)
            finally:
                store.close()
            return {'store_snapshot': result, 'store_identity': store_identity,
                    'initial_head': sha(canonical(result))}
        if kind == 'universe':
            module = self.module('universe_authority.protected', action['source'])
            state = self.target(action['state'])
            require(not os.path.lexists(state), 'FIXTURE_UNIVERSE_MUST_BE_NEW')
            with module.ProtectedUniverse.create(state, self.data(action['genesis'])) as universe:
                activated = universe.transition('active', universe.read()['event_head'])
                require(activated['accepted'] and activated['record']['life'] == 'active',
                        'FIXTURE_ORIGINAL_NATIVE_UNIVERSE_ACTIVATION_REFUSED')
                return {'activated': activated, 'genesis_sha256': universe.genesis_sha256}
        if kind == 'issuer':
            module = self.module('issuer.protected', action['source'])
            from issuer import lab_policy
            universe = self.results[action['universe']]
            policy = lab_policy.issuer_policy(universe['activated']['record'],
                self.data(action['genesis'])['policy_descriptors'], lab_policy.actor_id(action['requester_uid']))
            state = self.target(action['state'])
            require(not os.path.lexists(state), 'FIXTURE_ISSUER_MUST_BE_NEW')
            with module.ProtectedIssuer.create(state, policy) as issuer:
                grant = issuer.issue(policy['root_grant'], issuer.head()['event_head'])
                return {'policy_sha256': issuer.policy_sha256, 'head': issuer.head(), 'grant': grant,
                        'capability_id': policy['root_grant']['capability_id']}
        if kind == 'evidence':
            module = self.module('evidence_authority.protected', action['source'])
            state = self.target(action['state'])
            require(not os.path.lexists(state), 'FIXTURE_EVIDENCE_MUST_BE_NEW')
            with module.ProtectedEvidence.create_live(state, self.data(action['policy'])) as evidence:
                return {'policy_sha256': evidence.policy_sha256, 'head': evidence.head()}
        if kind == 'full-run-ledger':
            module = self.module('run_service', action['source'])
            root = self.target(action['root'])
            ledger = module.RunLedgerService(root)
            path = ledger.db_path
            require(not os.path.lexists(path), 'FIXTURE_RUN_LEDGER_MUST_BE_NEW')
            raw = module.canonical(module.dto_record(ledger.genesis))
            create(path, b'')
            db = sqlite3.connect(path.as_uri() + '?mode=rw', uri=True, isolation_level=None)
            db.row_factory = sqlite3.Row
            try:
                db.execute('PRAGMA journal_mode=WAL')
                db.execute('PRAGMA synchronous=FULL')
                db.execute('PRAGMA foreign_keys=ON')
                db.executescript('BEGIN IMMEDIATE;' + module.SCHEMA_SQL)
                db.execute('INSERT INTO run_meta VALUES(?,?,?)', (ledger.config_sha, raw, raw))
                db.execute('COMMIT')
                snapshot = ledger._snapshot(db)
                prefix = {'genesis': module.dto_record(ledger.genesis),
                    'state': module.dto_record(snapshot.state),
                    'rows': [module.dto_record(row) for row in snapshot.rows],
                    'events': [bytes(row[0]).hex() for row in
                        db.execute('SELECT record FROM run_events ORDER BY ordinal')]}
                db.execute('PRAGMA wal_checkpoint(FULL)')
            finally:
                db.close()
            create(ledger.state_dir / 'instance.lock', b'')
            sync(path.parent)
            self.objects[action['name']] = ledger
            return {'config_sha256': ledger.config_sha, 'genesis_hex': raw.hex(), 'original_prefix': prefix,
                    'original_prefix_sha256': sha(module.canonical(prefix))}
        if kind == 'scoped-ledgers':
            scoped = self.module('worldline.protected_scoped_resource_service', action['source'])
            observed = self.module('worldline.protected_scoped_observation_journal', action['observation_source'])
            historical = self.objects[action['historical']]
            gate = self.objects[action['gate']]
            config_path = self.target(action['config'])
            config_raw = protected(config_path).read_bytes()
            cfg = scoped.exact(config_raw)
            prefix = self.results[action['historical']]['original_prefix']
            require(cfg['original_prefix'] == prefix, 'FIXTURE_SCOPE_MUST_RETAIN_FULL_ORIGINAL_PREFIX')
            genesis = scoped.snapshot_restore(cfg['genesis'])
            require(genesis.rows == tuple(scoped.S.L.restore_dto(row) for row in prefix['rows'])
                    and scoped.snapshot_record(genesis) == cfg['genesis'],
                    'FIXTURE_SCOPED_GENESIS_MUST_RETAIN_FULL_ORIGINAL_TYPES_AND_ROWS')
            require(cfg['gate_config_sha256'] == sha(gate.config_raw)
                    and cfg['native_sha256'] == sha(selected(action['library'], ('DATA',))),
                    'FIXTURE_SCOPED_GENUINE_GATE_AND_NATIVE_BINDING_REQUIRED')
            for source_path, expected in cfg['sources'].items():
                require(sha(selected(source_path, ('SOURCE', 'ENTRY'))) == expected,
                        'FIXTURE_SCOPED_ORIGINAL_INSTALLED_SOURCE_CHANGED')
            binding = {'installation_id': cfg['installation_id'], 'config_sha256': sha(config_raw),
                'gate_config_sha256': sha(gate.config_raw), 'original_config_sha256': historical.config_sha,
                'issuer_policy_sha256': gate.issuer.policy_sha256, 'key_sha256': sha(gate.issuer.key),
                'native_sha256': cfg['native_sha256'], 'sources': cfg['sources']}
            anchor = {'binding': binding, 'genesis': cfg['genesis'], 'original_prefix': prefix}
            head = sha(scoped.canonical(anchor))
            anchor.update(snapshot=cfg['genesis'], head=head)
            mac = hmac.new(gate.issuer.key, scoped.DOMAIN + b'head\0' + scoped.canonical(anchor), 'sha256').hexdigest()
            observation_genesis = cfg['observation_genesis']
            require(observation_genesis['original_prefix_sha256'] == sha(scoped.canonical(prefix))
                    and observation_genesis['store_genesis'] == self.results[action['store']]['store_identity']
                    and observation_genesis['issuer_head'] == gate.issuer.head(),
                    'FIXTURE_SCOPED_REAL_OBSERVATION_OWNER_GENESIS_REQUIRED')
            observation_anchor = {'binding': binding, 'genesis': observation_genesis,
                                  'head': observation_genesis['event_head']}
            observation_mac = hmac.new(gate.issuer.key,
                observed.DOMAIN + b'head\0' + observed.canonical(observation_anchor), 'sha256').hexdigest()
            schema = ('CREATE TABLE scoped_meta(binding BLOB NOT NULL,genesis BLOB NOT NULL,'
                'original_prefix BLOB NOT NULL,snapshot BLOB NOT NULL,head TEXT NOT NULL,mac TEXT NOT NULL);'
                'CREATE TABLE scoped_events(ordinal INTEGER PRIMARY KEY,request_id TEXT NOT NULL UNIQUE,'
                'record BLOB NOT NULL,mac TEXT NOT NULL);')
            observation_schema = ('CREATE TABLE observations_meta(binding BLOB NOT NULL,genesis BLOB NOT NULL,'
                'head TEXT NOT NULL,mac TEXT NOT NULL);'
                'CREATE TABLE observations_events(ordinal INTEGER PRIMARY KEY,cause TEXT NOT NULL,'
                'reservation TEXT NOT NULL,record BLOB NOT NULL,mac TEXT NOT NULL);')
            writes = ((action['ledger'], schema, 'INSERT INTO scoped_meta VALUES(?,?,?,?,?,?)',
                (scoped.canonical(binding), scoped.canonical(cfg['genesis']), scoped.canonical(prefix),
                    scoped.canonical(cfg['genesis']), head, mac)),
                (action['observations'], observation_schema, 'INSERT INTO observations_meta VALUES(?,?,?,?)',
                (observed.canonical(binding), observed.canonical(observation_genesis),
                    observation_genesis['event_head'], observation_mac)))
            for relative, sql, insertion, values in writes:
                path = self.target(relative)
                create(path, b'')
                db = sqlite3.connect(path.as_uri() + '?mode=rw', uri=True, isolation_level=None)
                try:
                    db.execute('PRAGMA synchronous=FULL')
                    db.executescript('BEGIN IMMEDIATE;' + sql)
                    db.execute(insertion, values); db.execute('COMMIT')
                    actual = tuple(db.execute('SELECT * FROM ' +
                        ('scoped_meta' if relative == action['ledger'] else 'observations_meta')).fetchone())
                    require(actual == values and db.execute('PRAGMA quick_check').fetchall() == [('ok',)],
                            'FIXTURE_ORIGINAL_SCOPED_GENESIS_DURABLE_SQL_READBACK_CHANGED')
                finally:
                    db.close()
                fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
                try: os.fsync(fd)
                finally: os.close(fd)
                sync(path.parent)
            return {'binding': binding, 'original_prefix': prefix, 'snapshot': cfg['genesis'],
                'head': head, 'observation_genesis': observation_genesis,
                'schema_sql': schema, 'observation_schema_sql': observation_schema,
                'original_service_source_sha256': sha(selected(action['source'], ('SOURCE',))),
                'original_observation_source_sha256': sha(selected(action['observation_source'], ('SOURCE',))),
                'native_startup_admission_not_yet_exercised': True}
        if kind == 'launch-ledger':
            from original_owner_genesis import launch
            module = self.module('worldline.protected_resource_runtime', action['source'])
            gate = self.objects[action['gate']]
            historical = self.objects[action['historical']]
            cfg = self.data(action['template'])
            complete, binding, mac = launch(module, cfg, gate, historical,
                self.results[action['store']]['store_identity'], gate.issuer.head())
            config_raw = module.canonical(complete)
            create(self.target(action['config']), config_raw)
            path = self.target(action['ledger'])
            create(path, b'')
            sql = ('CREATE TABLE launch_meta(binding BLOB NOT NULL,genesis BLOB NOT NULL,'
                   'head TEXT NOT NULL,mac TEXT NOT NULL);'
                   'CREATE TABLE launch_events(ordinal INTEGER PRIMARY KEY,record BLOB NOT NULL,mac TEXT NOT NULL);')
            values = (module.canonical(binding), module.canonical(complete['launch_genesis']),
                      complete['launch_genesis']['event_head'], mac)
            db = sqlite3.connect(path.as_uri() + '?mode=rw', uri=True, isolation_level=None)
            try:
                db.execute('PRAGMA synchronous=FULL')
                db.executescript('BEGIN IMMEDIATE;' + sql)
                db.execute('INSERT INTO launch_meta VALUES(?,?,?,?)', values)
                db.execute('COMMIT')
                require(db.execute('SELECT * FROM launch_meta').fetchone() == values,
                        'FIXTURE_ORIGINAL_LAUNCH_OWNER_READBACK_CHANGED')
            finally: db.close()
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
            try: os.fsync(fd)
            finally: os.close(fd)
            sync(path.parent)
            return {'config': complete, 'binding': binding, 'schema_sql': sql, 'config_sha256': sha(config_raw)}
        if kind in ('owner-genesis', 'operation-owner-genesis'):
            import original_owner_genesis as declaration
            module_name = 'worldline.protected_owner' if kind == 'owner-genesis' else 'worldline.protected_operations'
            module = self.module(module_name, action['source'])
            gate = self.objects[action['gate']]
            historical = self.objects[action['historical']]
            genesis_raw = protected(self.target(action['installation_genesis'])).read_bytes()
            genesis = exact(genesis_raw)
            policy_raw = protected(self.target(action['policy'])).read_bytes()
            policy = exact(policy_raw)
            if kind == 'owner-genesis':
                from worldline.resource_run_ledger import dto_record
                result = declaration.owner(module, policy_raw, policy, gate,
                    genesis_raw, genesis, dto_record(historical.genesis))
                fields = ('journal', 'head', 'genesis', 'bootstrap')
            else:
                result = declaration.operation(module, policy_raw, policy, gate, genesis_raw, genesis,
                    self.results[action['owner']]['binding'], historical,
                    self.results[action['historical']]['original_prefix'], self.data(action['initial_body']))
                fields = ('journal', 'owner_genesis')
            pins = {}
            for field in fields:
                raw = result[field]
                path = self.target(action[field])
                create(path, raw)
                require(protected(path).read_bytes() == raw, 'FIXTURE_ORIGINAL_SIGNED_OWNER_READBACK_CHANGED')
                pins[field] = {'path': str(path), 'sha256': sha(raw)}
            return {'binding': result['binding'], 'artifacts': pins}
        if kind == 'startup-descriptor':
            from worldline.protected_startup import inventory as original_inventory
            value = self.data(action['template'])
            value['trees'] = {root: original_inventory(Path(root)) for root in value['trees']}
            value['files'] = {path: {'mode': oct(stat.S_IMODE(protected(path).stat().st_mode)),
                'sha256': sha(protected(path).read_bytes())} for path in value['files']}
            raw = canonical(value)
            path = self.target(action['path'])
            create(path, raw)
            return {'path': str(path), 'sha256': sha(raw), 'descriptor': value}
        if kind == 'custody-genesis':
            from worldline.custody_v2_provision_values import GENESIS_KEYS
            descriptor = protected(self.target(action['descriptor'])).read_bytes()
            plan_raw = protected(self.target(action['plan'])).read_bytes()
            spec = exact(descriptor); plan = exact(plan_raw)
            gate = self.objects[action['gate']]
            value = {'schema': 'worldline.owner-provisioned-root-custody-v2',
                'installation': spec['installation_id'], 'startup_descriptor_sha256': sha(descriptor),
                'owner_plan_sha256': sha(plan_raw), 'issuer_key_sha256': sha(gate.issuer.key),
                'initial_event': None, 'prior_custody': self.data(action['prior']) if action['prior'] is not None else None}
            require(set(value) == GENESIS_KEYS and plan['installation'] == value['installation'],
                    'FIXTURE_CUSTODY_ORIGINAL_FULL_GENESIS_BINDING_CHANGED')
            raw = canonical(value); path = self.target(action['path']); create(path, raw)
            return {'path': str(path), 'sha256': sha(raw), 'genesis': value}
        if kind == 'owner-data':
            # Bind original owner configuration fields to actual creator
            # results and current named bytes, never to supplied verdicts.
            if action['name'] in ('scoped-config', 'scoped-producer-policy'):
                from worldline.protected_resource_runtime import canonical as owner_canonical, exact as owner_exact
                require(not action['newline'], 'FIXTURE_ORIGINAL_SCOPED_CANONICAL_GRAMMAR_REQUIRED')
                value = owner_exact(selected(action['template']))
            elif action['name'] == 'historical-config':
                original = next(item for item in self.plan['owner_actions'] if item['name'] == 'historical-ledger')
                service = self.module('run_service', original['source'])
                owner_canonical, owner_exact = service.canonical, service.parse_canonical
                require(not action['newline'], 'FIXTURE_ORIGINAL_FULL_LEDGER_CANONICAL_GRAMMAR_REQUIRED')
                value = owner_exact(selected(action['template']))
            else:
                owner_canonical = canonical
                owner_exact = exact
                value = self.data(action['template'])
            for binding in action['bindings']:
                if binding['kind'] == 'result':
                    fact = self.results[binding['action']]
                    for component in binding['select']:
                        fact = fact[component]
                elif binding['kind'] == 'file-sha256':
                    fact = sha(protected(self.target(binding['path'])).read_bytes())
                elif binding['kind'] == 'original-json':
                    fact = owner_exact(protected(self.target(binding['path'])).read_bytes())
                    for component in binding['select']:
                        fact = fact[component]
                elif binding['kind'] == 'source-inventory':
                    directory = self.target(binding['path'])
                    protected(directory, True)
                    records = inventory(directory)
                    if binding['format'] == 'sha256':
                        fact = {name: record['sha256'] for name, record in records.items()
                                if record['kind'] == 'file'}
                    else:
                        require(binding['format'] == 'mode-sha256', 'FIXTURE_ORIGINAL_INVENTORY_FORMAT')
                        fact = {name: {'mode': record['mode'], 'sha256': record['sha256']}
                                for name, record in records.items() if record['kind'] == 'file'}
                else:
                    raise RuntimeError('FIXTURE_ORIGINAL_FACT_BINDING_REQUIRED')
                parent = value
                for component in binding['field'][:-1]:
                    parent = parent[component]
                require(binding['field'][-1] in parent, 'FIXTURE_ORIGINAL_CONFIG_FIELD_MISSING')
                parent[binding['field'][-1]] = fact
            path = self.target(action['path'])
            raw = owner_canonical(value) + (b'\n' if action['newline'] else b'')
            create(path, raw)
            return {'path': str(path), 'sha256': sha(raw)}
        if kind == 'canonical':
            module = self.module('canonical_store', action['source'])
            cfg = exact(protected(self.target(action['config'])).read_bytes())
            store = module.CanonicalStore(self.target(action['root']),
                managed_root=Path(cfg['managed_root']), daemon_data_root=Path(cfg['daemon_data_root']),
                mission_target=cfg['mission_spec']['target'],
                expected_target_sha256=cfg['mission_spec']['expected_sha256'],
                fixture_baseline_sha256=cfg['fixture_baseline_sha256'], fixture_modes=cfg['fixture_modes'],
                fault_laboratory=cfg['accepted_fault_laboratory'])
            self.objects[action['name']] = store
            return {'state': store.state}
        if kind == 'authority':
            module = self.module('authority_service', action['source'])
            authority = module.Authority(self.target(action['config']))
            self.objects[action['name']] = authority
            return {'state': authority.state}
        if kind == 'gate':
            module = self.module('intent_gate', action['source'])
            gate = module.Gate(self.target(action['config']))
            self.objects[action['name']] = gate
            if gate.issuer is not None:
                self.closers.append(gate.issuer.close)
            if gate.universe is not None:
                self.closers.append(gate.universe.close)
            return {'facts': gate.facts(), 'journal': gate.journal}
        if kind == 'startup-genesis':
            from worldline.protected_startup import canonical as startup_canonical, store_snapshot
            use_module = self.module('worldline.protected_capability_uses', action['use_source'])
            recovery_module = self.module('recovery_principal', action['recovery_source'])
            gate = self.objects[action['gate']]
            key = gate.issuer.key
            require(key == protected(gate.issuer.state / 'issuer-key.bin').read_bytes(),
                    'FIXTURE_ACTUAL_ORIGINAL_ISSUER_KEY_CHANGED')
            recovery_body = {'schema': 'worldline.protected-recovery-journal-v1',
                'gate_config': sha(gate.config_raw), 'issuer_policy': gate.issuer.policy_sha256, 'events': []}
            use_body = {'schema': 'cosmogony.full-protected-use-reservations-v1', 'events': []}
            def envelope(body, domain):
                return {'body': body, 'mac': hmac.new(key, domain + gate_module_canonical(body),
                                                     hashlib.sha256).hexdigest()}
            gate_module_canonical = importlib.import_module('intent_gate').canonical
            snapshot = store_snapshot(self.target(action['database']))
            identity = self.results[action['store']]['store_identity']
            value = {'schema': 'worldline.owner-provisioned-genesis-v1',
                'installation_id': action['installation_id'], 'owner_authorization': self.plan['operator_authorization'],
                'store': {'identity': identity, 'schema': snapshot['schema'], 'version': snapshot['version'],
                          'initial_head': sha(startup_canonical(snapshot))},
                'gate_config': sha(gate.config_raw), 'gate_head': gate.facts()['head'],
                'issuer_head': gate.issuer.head(), 'journals': {
                    'recovery-full-journal': {'path': str(gate.state_dir / 'recovery-full-journal.json'),
                        'initial_envelope': envelope(recovery_body, recovery_module._DOMAIN)},
                    'full-use-reservations': {'path': str(gate.issuer.state / 'full-use-reservations.json'),
                        'initial_envelope': envelope(use_body, use_module._DOMAIN)}}}
            raw = startup_canonical(value) + b'\n'
            path = self.target(action['path'])
            create(path, raw)
            return {'path': str(path), 'sha256': sha(raw), 'genesis': value,
                    'store_initial_snapshot': snapshot, 'store_initial_head': value['store']['initial_head']}
        if kind == 'original-supervisor-start':
            import subprocess
            import time
            module = self.module('daemon_supervisor', action['source'])
            endpoint_module = self.module('daemon_endpoint', action['endpoint_source'])
            cfg = module.checked_config(self.root)
            entry = str(Path(__file__).with_name('original_supervisor_entry.py'))
            selected(entry, ('SOURCE', 'ENTRY'))
            selected(action['early_envelope'])
            command = [_lease.interpreter, '-I', '-S', '-B', _lease.helper_path,
                '--bootstrap-envelope', action['early_envelope'], '--entry', entry, str(self.root), 'start']
            stdout = self.target(action['name'] + '.stdout')
            stderr = self.target(action['name'] + '.stderr')
            out = stdout.open('xb'); err = stderr.open('xb')
            try:
                child = subprocess.Popen(command, env=dict(action['environment']), stdout=out, stderr=err)
            except BaseException:
                out.close(); err.close(); raise
            def close():
                primary = sys.exc_info()[1]
                try:
                    if child.poll() is None:
                        module.stop_sealed(cfg)
                    child.wait(timeout=action['timeout'])
                except BaseException as error:
                    if primary is None: raise
                    primary.add_note('Original supervisor owner close failed: ' + repr(error))
                finally:
                    out.flush(); err.flush(); os.fsync(out.fileno()); os.fsync(err.fileno())
                    out.close(); err.close()
            self.closers.append(close)
            self.supervisors[action['name']] = (child, module, cfg, close)
            deadline = time.monotonic() + action['timeout']
            while not Path(cfg['daemon_seal_record']).exists():
                require(child.poll() is None, 'FIXTURE_ORIGINAL_SUPERVISOR_EXITED_BEFORE_SEAL')
                require(time.monotonic() < deadline, 'FIXTURE_ORIGINAL_SUPERVISOR_SEAL_TIMEOUT')
                time.sleep(0.05)
            observed = endpoint_module.read_seal(cfg)
            endpoint_module.check_entry(cfg, observed)
            endpoint_module.check_process(observed)
            return {'argv': command, 'supervisor_pid': child.pid, 'original_seal': observed}
        if kind == 'original-supervisor-stop':
            child, module, cfg, close = self.supervisors[action['supervisor']]
            result = module.stop_sealed(cfg)
            child.wait(timeout=action['timeout'])
            require(child.returncode == 0, 'FIXTURE_ORIGINAL_SUPERVISOR_STOP_FAILED')
            self.closers.remove(close); close()
            return {'original_stop_result': result, 'supervisor_pid': child.pid,
                    'actual_wait': child.returncode}
        if kind == 'owner-entry':
            # The selected original bootstrap/head/custody utilities enforce
            # their own exact ENTRY identity. This stage deliberately does not
            # impersonate that identity by calling their main() in this process.
            import subprocess
            entry = action['entry']
            role = _lease.files.get(entry, (None,))[0]
            require(role in ('SOURCE', 'ENTRY'), 'FIXTURE_OWNER_ENTRY_NOT_SELECTED')
            selected(entry, (role,))
            envelope = action['early_envelope']
            selected(envelope)
            command = [_lease.interpreter, '-I', '-S', '-B', _lease.helper_path,
                       '--bootstrap-envelope', envelope, '--entry', entry, *action['argv']]
            stdout = self.target(action['name'] + '.stdout')
            stderr = self.target(action['name'] + '.stderr')
            with stdout.open('xb') as out, stderr.open('xb') as err:
                child = subprocess.Popen(command, env=dict(action['environment']), stdout=out, stderr=err)
                wait = child.wait(timeout=action['timeout'])
                out.flush(); err.flush(); os.fsync(out.fileno()); os.fsync(err.fileno())
            require(wait == 0, 'FIXTURE_ACTUAL_ORIGINAL_OWNER_ENTRY_FAILED')
            return {'argv': command, 'pid': child.pid, 'actual_wait': wait,
                    'stdout_sha256': sha(stdout.read_bytes()), 'stderr_sha256': sha(stderr.read_bytes())}
        raise RuntimeError('FIXTURE_UNKNOWN_ORIGINAL_OWNER_ACTION_' + str(kind))

    def publish(self):
        record = {'schema': 'worldline.original-custody-fixture-created-v2', 'stage': self.stage,
                  'plan_sha256': sha(self.raw), 'original_plan_hex': self.raw.hex(),
                  'selected_source': _lease.check(), 'actions': self.actions,
                  'inventory': inventory(self.root), 'phase_acceptance': False}
        create(self.root / {'materialize': 'materialized.json', 'initialize': 'initialized.json',
                           'provision': 'provisioned.json'}[self.stage], canonical(record) + b'\n')
        return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', required=True)
    parser.add_argument('--stage', choices=('materialize', 'initialize', 'provision'), required=True)
    args = parser.parse_args()
    builder = Builder(args.plan, args.stage)
    try:
        getattr(builder, args.stage)()
        builder.publish()
    finally:
        for close in reversed(builder.closers):
            close()


if __name__ == '__main__':
    main()
