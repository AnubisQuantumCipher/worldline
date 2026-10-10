"""Full read-only protected state observation before target reconstruction.

Complete bytes and every SQLite logical schema/row/value are retained under the
actual original OFDs. Equality is a factual correspondence guard. Native full
redecision still owns permission; this module does not define grant eligibility,
use ceilings, resource totals, lifecycle or effect status.
"""
import os,sqlite3,stat
from pathlib import Path
from urllib.parse import quote
from .protected_startup import require,private_bytes,protected
from .root_worker_custody import named_identity

def _quoted(name):
    require(type(name) is str,'ROOT_CURRENT_SQL_IDENTIFIER_INVALID')
    return '"'+name.replace('"','""')+'"'

def _database(path,journal=None):
    db=sqlite3.connect('file:'+quote(str(path),safe='/')+'?mode=ro',uri=True,isolation_level=None)
    try:
        db.execute('PRAGMA trusted_schema=OFF');db.execute('PRAGMA query_only=ON');db.execute('BEGIN')
        schema=tuple(db.execute('SELECT type,name,tbl_name,rootpage,sql FROM sqlite_master ORDER BY rowid'))
        tables=[]
        for kind,name,_table,_root,_sql in schema:
            if kind!='table':continue
            columns=tuple(db.execute('PRAGMA table_xinfo('+_quoted(name)+')'))
            # Every original column/value is transported. rowid is retained
            # where the real schema has one; WITHOUT ROWID uses its declared
            # primary-key ordering rather than a made-up ordinal or projection.
            without=_sql is not None and 'WITHOUT ROWID' in _sql.upper()
            if without:
                key=tuple(row[1] for row in sorted(columns,key=lambda row:row[5]) if row[5])
                require(key,'ROOT_CURRENT_WITHOUT_ROWID_PRIMARY_KEY_ABSENT')
                query='SELECT * FROM '+_quoted(name)+' ORDER BY '+','.join(_quoted(item) for item in key)
            else:query='SELECT rowid,* FROM '+_quoted(name)+' ORDER BY rowid'
            rows=tuple(tuple(row) for row in db.execute(query))
            tables.append({'name':name,'columns':columns,'query':query,'rows':rows,
                'foreign_key_list':tuple(tuple(row) for row in db.execute(
                    'PRAGMA foreign_key_list('+_quoted(name)+')'))})
        complete={'schema':schema,'tables':tuple(tables),'encoding':tuple(db.execute('PRAGMA encoding')),
            'user_version':tuple(db.execute('PRAGMA user_version')),'application_id':tuple(db.execute('PRAGMA application_id')),
            'integrity':tuple(db.execute('PRAGMA quick_check')),
            'foreign_keys':tuple(db.execute('PRAGMA foreign_keys')),
            'journal_mode':tuple(tuple(row) for row in db.execute('PRAGMA journal_mode')),
            'foreign_key_check':tuple(tuple(row) for row in db.execute('PRAGMA foreign_key_check'))}
        require(complete['integrity']==(('ok',),),'ROOT_CURRENT_DATABASE_CORRUPT')
        if journal is not None:
            complete['authenticated_root_events'],complete['authenticated_root_head']=journal._load(db)
        db.rollback();return complete
    finally:db.close()

def capture_owner_state(owner):
    from .protected_root_worker import RootWorkerFront,RootWorkerIntake,RootWorkerProcess
    require(type(owner) in (RootWorkerFront,RootWorkerIntake,RootWorkerProcess),
            'ROOT_CURRENT_REAL_SOURCE_CUSTODY_OWNER_REQUIRED')
    source=owner.source_lease;source.check()
    if type(owner) is RootWorkerIntake:
        locks=owner.custody.fds
    else:
        locks={str(path):fd for path,fd in owner.lease.fds.items()}
        for authority,leaf in ((owner.principal.gate.issuer,'issuer.lock'),(owner.principal.gate.universe,'universe.lock')):
            locks[str(authority.state/leaf)]=authority.lock_fd
    for path,fd in locks.items():named_identity(fd,path)
    roster=owner.spec['provisioned_state']
    require(type(roster) is list and len(set(roster))==len(roster),'ROOT_CURRENT_COMPLETE_STATE_ROSTER_CHANGED')
    observations=[]
    for word in roster:
        path=Path(word);info=protected(path);raw=private_bytes(path)
        entry={'path':str(path),'identity':{'device':info.st_dev,'inode':info.st_ino,'uid':info.st_uid,
            'gid':info.st_gid,'mode':stat.S_IMODE(info.st_mode)},'raw':raw}
        if raw.startswith(b'SQLite format 3\x00'):
            journal=owner.custody_journal if path==owner.custody_journal.path else None
            entry['logical_database']=_database(path,journal)
            entry['physical_database_after']=private_bytes(path)
        observations.append(entry)
    return {'installation':owner.spec,'paths':tuple(observations),
        'descriptor_raw':owner.descriptor_raw,'source':source.check(),
        'held_locks':tuple({'path':path,'identity':named_identity(fd,path)} for path,fd in locks.items())}

def same_logical_state(before,current):
    require(before['installation']==current['installation'] and before['descriptor_raw']==current['descriptor_raw'],
            'ROOT_CURRENT_SELECTED_INSTALLATION_CHANGED')
    require(tuple(entry['path'] for entry in before['paths'])==tuple(entry['path'] for entry in current['paths']),
            'ROOT_CURRENT_COMPLETE_PROVISIONED_PATHS_CHANGED')
    for earlier,later in zip(before['paths'],current['paths']):
        require(earlier['identity']==later['identity'],'ROOT_CURRENT_PROTECTED_STATE_FILE_REPLACED')
        if 'logical_database' in earlier or 'logical_database' in later:
            require('logical_database' in earlier and 'logical_database' in later,
                    'ROOT_CURRENT_DATABASE_TYPE_CHANGED')
            left=earlier['logical_database'];right=later['logical_database']
            if 'authenticated_root_events' in left or 'authenticated_root_events' in right:
                # This is a complete authenticated append relation, not a path
                # exclusion. Both entire SQLite snapshots/raw files/heads stay
                # retained; every original root-custody row must be a prefix.
                require('authenticated_root_events' in left and 'authenticated_root_events' in right
                    and right['authenticated_root_events'][:len(left['authenticated_root_events'])]==left['authenticated_root_events'],
                        'ROOT_CURRENT_PRIOR_CUSTODY_HISTORY_LOST_OR_REWRITTEN')
                require({key:value for key,value in left.items() if key not in
                    ('tables','authenticated_root_events','authenticated_root_head')}==
                    {key:value for key,value in right.items() if key not in
                    ('tables','authenticated_root_events','authenticated_root_head')},
                        'ROOT_CURRENT_CUSTODY_SCHEMA_OR_SQL_METADATA_CHANGED')
                ltab={table['name']:table for table in left['tables']};rtab={table['name']:table for table in right['tables']}
                require(set(ltab)==set(rtab)=={'genesis','events','head'} and ltab['genesis']==rtab['genesis'],
                        'ROOT_CURRENT_CUSTODY_COMPLETE_TABLES_CHANGED')
                for name in ('events','head'):
                    require({key:value for key,value in ltab[name].items() if key!='rows'}==
                        {key:value for key,value in rtab[name].items() if key!='rows'},
                            'ROOT_CURRENT_CUSTODY_TABLE_DEFINITION_CHANGED')
                require(rtab['events']['rows'][:len(ltab['events']['rows'])]==ltab['events']['rows'],
                        'ROOT_CURRENT_CUSTODY_FULL_SQL_ROW_PREFIX_CHANGED')
                # Actual _load authenticated the sole current head in the same
                # read transaction, including all new full records and MACs.
            else:require(left==right,'ROOT_CURRENT_FULL_SQLITE_LOGICAL_STATE_CHANGED')
        else:require(earlier['raw']==later['raw'],'ROOT_CURRENT_FULL_STATE_BYTES_CHANGED')
    # Do not compare process-local descriptor numbers or mutable SQLite page/WAL
    # layout as semantic state. All of those complete physical observations stay
    # retained above. Selected source and original named OFD joins are recaptured
    # separately by the actual early source lease and custody owner.
    return {'before':before,'current':current}


def capture_current_roster(owner):
    """Capture a stable COMPLETE actual owner roster, with both observations.

    This is input material, not X4 authentication, X5 fold or startup permission.
    In particular, original v1 journal authentication remains v1. No PREPARED
    row is interpreted as evidence of Never_Launched, and no absent descriptor
    is reconstructed. The original owner/OFD/source checks execute on each pass.
    """
    from .protected_root_worker import RootWorkerFront,RootWorkerIntake,RootWorkerProcess
    require(type(owner) in (RootWorkerFront,RootWorkerIntake,RootWorkerProcess),
        'ROOT_CURRENT_REAL_SOURCE_CUSTODY_OWNER_REQUIRED')
    owner.intact()
    before=capture_owner_state(owner)
    current=capture_owner_state(owner)
    # Existing recovery comparison allows authenticated journal append. A
    # current-roster capture must instead observe the SAME complete logical
    # state. Do not silently use the looser recovery relation here.
    require(before['installation']==current['installation']
        and before['descriptor_raw']==current['descriptor_raw'],
        'ROOT_CURRENT_ROSTER_INSTALLATION_CHANGED')
    require(before['held_locks']==current['held_locks'],
        'ROOT_CURRENT_ROSTER_HELD_LOCKS_CHANGED')
    require(tuple(item['path'] for item in before['paths'])==
        tuple(item['path'] for item in current['paths']),
        'ROOT_CURRENT_ROSTER_PATHS_CHANGED')
    for earlier,later in zip(before['paths'],current['paths']):
        require(earlier['identity']==later['identity'],
            'ROOT_CURRENT_ROSTER_FILE_REPLACED')
        if 'logical_database' in earlier or 'logical_database' in later:
            require('logical_database' in earlier and 'logical_database' in later
                and earlier['logical_database']==later['logical_database'],
                'ROOT_CURRENT_ROSTER_DATABASE_CHANGED')
        else:
            require(earlier['raw']==later['raw'],
                'ROOT_CURRENT_ROSTER_FILE_CHANGED')
    owner.intact()
    # Retain changing physical SQLite bytes as evidence without mistaking page
    # placement for semantic row identity. Complete schemas, columns, rows,
    # authenticated original events and heads were compared above. Raw source
    # and lock evidence from BOTH captures remain available to native framing.
    return {'schema':'worldline.protected-current-owner-roster-v1',
        'before':before,'current':current}

def _database_connection(db,journal=None):
    """Full factual capture in the caller's already-active SQLite transaction."""
    require(db.in_transaction,'ROOT_CURRENT_TRANSACTION_REQUIRED')
    schema=tuple(db.execute('SELECT type,name,tbl_name,rootpage,sql FROM sqlite_master ORDER BY rowid'))
    tables=[]
    for kind,name,_table,_root,_sql in schema:
        if kind!='table':continue
        columns=tuple(db.execute('PRAGMA table_xinfo('+_quoted(name)+')'))
        # Every original column/value is transported. rowid is retained
        # where the real schema has one; WITHOUT ROWID uses its declared
        # primary-key ordering rather than a made-up ordinal or projection.
        without=_sql is not None and 'WITHOUT ROWID' in _sql.upper()
        if without:
            key=tuple(row[1] for row in sorted(columns,key=lambda row:row[5]) if row[5])
            require(key,'ROOT_CURRENT_WITHOUT_ROWID_PRIMARY_KEY_ABSENT')
            query='SELECT * FROM '+_quoted(name)+' ORDER BY '+','.join(_quoted(item) for item in key)
        else:query='SELECT rowid,* FROM '+_quoted(name)+' ORDER BY rowid'
        rows=tuple(tuple(row) for row in db.execute(query))
        tables.append({'name':name,'columns':columns,'query':query,'rows':rows,
            'foreign_key_list':tuple(tuple(row) for row in db.execute(
                'PRAGMA foreign_key_list('+_quoted(name)+')'))})
    complete={'schema':schema,'tables':tuple(tables),'encoding':tuple(db.execute('PRAGMA encoding')),
        'user_version':tuple(db.execute('PRAGMA user_version')),'application_id':tuple(db.execute('PRAGMA application_id')),
        'integrity':tuple(db.execute('PRAGMA quick_check')),
        'foreign_keys':tuple(db.execute('PRAGMA foreign_keys')),
        'journal_mode':tuple(tuple(row) for row in db.execute('PRAGMA journal_mode')),
        'foreign_key_check':tuple(tuple(row) for row in db.execute('PRAGMA foreign_key_check'))}
    require(complete['integrity']==(('ok',),),'ROOT_CURRENT_DATABASE_CORRUPT')
    table_names = {table['name'] for table in tables}
    if {'genesis', 'events', 'head', 'root_state', 'subject_state', 'alternatives', 'blobs'} <= table_names:
        from .root_worker_journal_v2 import RootCustodyJournalV2
        event_rows = tuple(db.execute('SELECT * FROM events ORDER BY seq'))
        events = tuple(RootCustodyJournalV2._event(tuple(row)) for row in event_rows)
        complete['authenticated_root_events'] = events
        complete['root_events'] = events
    if {'canonical_operation_head', 'canonical_operation_admission'} & table_names:
        named_rows = {}
        for name, sql in (
            ('head', 'SELECT installation,genesis,head,state,prior_envelope,next_envelope FROM canonical_operation_head WHERE name=?'),
            ('admission', 'SELECT installation,genesis,owner_envelope,initial_envelope,state FROM canonical_operation_admission WHERE name=?')):
            args = ('worldline-operations',)
            try:
                row = db.execute(sql, args).fetchone()
                error = None
            except sqlite3.Error as observed:
                row = None
                error = {'type': type(observed).__qualname__, 'module': type(observed).__module__,
                         'message': str(observed), 'args': tuple(observed.args),
                         'sqlite_errorcode': getattr(observed, 'sqlite_errorcode', None),
                         'sqlite_errorname': getattr(observed, 'sqlite_errorname', None)}
            named_rows[name] = {'sql': sql, 'args': args,
                                'row': None if row is None else tuple(row), 'error': error}
        complete['operation_named_rows'] = named_rows
    if journal is not None:
        from .root_worker_journal_v2 import RootCustodyJournalV2
        if type(journal) is RootCustodyJournalV2:
            complete['custody_v2_rows']=journal.capture_rows(db)
            raw, observed = journal._accepted_capture(db)
            complete['custody_v2_load'] = {'envelope': raw, 'status': observed.status,
                                          'position': observed.position}
        else:
            complete['authenticated_root_events'],complete['authenticated_root_head']=journal._load(db)
    return complete

def capture_intake_admission_profiles(owner, operation_context=None):
    from .protected_root_worker import RootWorkerIntake
    from .protected_startup import exact_json
    from .custody_startup_capture import capture_admission_profiles_from_sources
    require(type(owner) is RootWorkerIntake, 'CUSTODY_ADMISSIONS_ACTUAL_INTAKE_REQUIRED')
    if operation_context is None:
        operation_context = capture_intake_operation_context(owner)
    gate = exact_json(operation_context['gate_config_raw'])
    return capture_admission_profiles_from_sources(spec=owner.spec,
        genesis=operation_context['lease_genesis'], descriptor_path=str(owner.path),
        issuer_state=Path(gate['root']) / 'authority/issuer/state',
        source_lease=owner.source_lease, store_initial_snapshot=None,
        store_initial_snapshot_raw=None, store_initial_head=None)

def capture_startup_owner_state(owner, *, custody_connection=None):
    """Full raw factual owner SQL without recursively authenticating a load."""
    return _capture_owner_sources(owner, None, custody_connection)

def _capture_owner_sources(owner, journal, custody_connection=None):
    from .protected_root_worker import RootWorkerFront, RootWorkerIntake, RootWorkerProcess
    from .protected_startup import StartupLease
    require(type(owner) in (StartupLease, RootWorkerFront, RootWorkerIntake, RootWorkerProcess),
            'ROOT_CURRENT_REAL_SOURCE_CUSTODY_OWNER_REQUIRED')
    source = owner.source_lease
    source.check()
    lease = owner if type(owner) is StartupLease else getattr(owner, 'lease', None)
    actual_journal = (getattr(owner, 'custody_journal_v2', None) if type(owner) is StartupLease
                      else getattr(owner, 'custody_journal', None))
    if custody_connection is not None:
        require(type(custody_connection) is sqlite3.Connection and custody_connection.in_transaction
                and actual_journal is not None,
                'ROOT_CURRENT_ACTUAL_CUSTODY_TRANSACTION_REQUIRED')
        databases = custody_connection.execute('PRAGMA database_list').fetchall()
        require(len([item for item in databases if item[1] == 'main'
                and Path(item[2]) == actual_journal.path]) == 1,
                'ROOT_CURRENT_CUSTODY_TRANSACTION_PATH_CHANGED')
    offer = getattr(owner, 'current_offer', None)
    if offer is not None:
        from .root_worker_custody import CustodyOffer
        require(type(offer) is CustodyOffer and offer.p is owner.principal,
                'ROOT_CURRENT_ACTUAL_ESCROW_OFD_OWNER_REQUIRED')
        locks = dict(offer.fds)
    elif getattr(owner, 'custody', None) is not None:
        locks = dict(owner.custody.fds)
    elif lease is not None and getattr(lease, 'exec_custody', None) is not None:
        locks = dict(lease.exec_custody.fds)
    else:
        require(lease is not None, 'ROOT_CURRENT_ACTUAL_LOCK_OWNER_REQUIRED')
        locks = {str(path): fd for path, fd in lease.fds.items()}
        if lease.gate is not None:
            for authority, leaf in ((lease.gate.issuer, 'issuer.lock'),
                                    (lease.gate.universe, 'universe.lock')):
                locks[str(authority.state / leaf)] = authority.lock_fd
    if actual_journal is not None:
        locks[str(actual_journal.lock_path)] = actual_journal.lock_fd
    for path,fd in locks.items():named_identity(fd,path)
    roster=owner.spec['provisioned_state']
    require(type(roster) is list and len(set(roster))==len(roster),'ROOT_CURRENT_COMPLETE_STATE_ROSTER_CHANGED')
    observations=[]
    for word in roster:
        path=Path(word);info=protected(path);raw=private_bytes(path)
        entry={'path':str(path),'identity':{'device':info.st_dev,'inode':info.st_ino,'uid':info.st_uid,
            'gid':info.st_gid,'mode':stat.S_IMODE(info.st_mode)},'raw':raw}
        if raw.startswith(b'SQLite format 3\x00'):
            observed_journal = journal if journal is not None and path == journal.path else None
            if custody_connection is not None and path == actual_journal.path:
                entry['logical_database'] = _database_connection(custody_connection)
            else:
                entry['logical_database'] = _database(path, observed_journal)
            entry['physical_database_after']=private_bytes(path)
        observations.append(entry)
    return {'installation':owner.spec,'paths':tuple(observations),
        'descriptor_raw':owner.descriptor_raw,'source':source.check(),
        'held_locks':tuple({'path':path,'identity':named_identity(fd,path)} for path,fd in locks.items())}

def warm_operation_context_sources():
    """Load the fixed factual readers before recording an executed-source image."""
    from .operation_capture import archive as original_archive
    from .protected_owner import private
    from .protected_resource_runtime import canonical, exact
    from .custody_operation_sources import capture_kernel_material
    from .protected_recovery_capture import refuse
    from . import resource_scoped_run_ledger as S
    from .recovery_observation import acquire_readonly_syntax_context, acquire_syntax_facts_from_original
    from .evaluation_producer import warm_syntax_acquisition_sources
    warm_syntax_acquisition_sources()
    from . import (custody_subject_capture, root_worker_subject_custody,
        root_worker_subject_transfer, root_worker_subject_spool, root_worker_subject_pump,
        root_worker_subject_service, root_worker_serving_peer, root_worker_root_evidence,
        protected_root_observation, root_owned_descriptor_roster, root_scoped_capture_profile,
        scoped_source_image, client_peer, client_peer_relay, root_worker_output_kernel,
        custody_closed_kernel, root_worker_subject_relay, root_worker_subject_output,
        root_worker_subject_sync, root_worker_subject_front, root_worker_relay_dispatch,
        scoped_capture_namespace_source, root_worker_subject_messages, custody_control_registration)
    from .root_worker_codec import _schema
    _schema()

def capture_operation_context(principal):
    """Capture authentic current files through actual original owner paths."""
    from .protected_operations import CanonicalOperationPrincipal
    from .protected_scoped_resource_runtime import ProtectedScopedResourcePrincipal
    require(type(principal) is CanonicalOperationPrincipal,
            'CUSTODY_OPERATION_CONTEXT_ACTUAL_PRINCIPAL_REQUIRED')
    p = principal
    p.lease.source_lease.check()
    scoped = p.resources.scoped_service if type(p.resources) is ProtectedScopedResourcePrincipal else None
    owner = p.owner
    root = owner.gate.state_path.parent
    paths = {'owner': {'policy': str(owner.policy_path), 'genesis': str(root / 'owner-genesis.json'),
        'bootstrap': str(root / 'owner-bootstrap.json'), 'journal': str(owner.journal.path),
        'head': str(owner.journal.head), 'mutation_intent': str(owner.journal.intent)},
        'issuer_key': str(owner.gate.issuer.state / 'issuer-key.bin'),
        'operation_policy': str(p.policy_path), 'native': str(owner.core.library_path),
        'original_config': str(p.resource_origin_service.root / 'run-config-v1.json'),
        'original_database': str(p.resource_origin_service.db_path),
        'scoped_config': None if scoped is None else str(scoped.config_path),
        'scoped_database': None if scoped is None else str(scoped.db_path),
        'store_database': str(p.lease.state_path / 'worldline.sqlite3'),
        'universe_genesis': str(p.gate.universe.state / 'genesis.json')}
    from .custody_operation_sources import capture_kernel_material
    with owner.lock:
        context = _capture_operation_sources(p.lease.spec, p.lease.genesis_raw,
            p.gate.config_raw, paths, capture_kernel_material(p.core, p.capture.conf['kernel_build']),
            core=p.core, source_lease=p.lease.source_lease)
    p.lease.source_lease.check()
    return context

def capture_intake_operation_context(owner):
    """Independent full read-only sources before target constructors exist."""
    from .protected_root_worker import RootWorkerIntake
    from .protected_startup import exact_json
    from .custody_operation_sources import capture_kernel_material
    require(type(owner) is RootWorkerIntake, 'CUSTODY_CONTEXT_ACTUAL_INTAKE_REQUIRED')
    owner.source_lease.check()
    spec = owner.spec
    gate_path = Path(spec['paths']['authority_root']) / 'authority/gate/config.json'
    gate_raw = private_bytes(gate_path)
    gate_config = exact_json(gate_raw)
    authority = Path(gate_config['root'])
    # These paths are the actual Gate/ProtectedOwner/RunLedgerService grammar;
    # native authenticates the independently read configuration and bindings.
    gate_state = authority / 'authority/gate/state'
    issuer_state = authority / 'authority/issuer/state'
    resource = authority / 'authority/resource'
    recovery_raw = private_bytes(authority / 'authority/gate/recovery-bind.json')
    recovery = exact_json(recovery_raw)
    scoped_config = resource / 'run-scoped-config-v1.json'
    try:
        scoped_config.lstat()
    except FileNotFoundError:
        scoped_path = None
    else:
        scoped_path = str(scoped_config)
    paths = {'owner': {'policy': str(gate_state / 'owner-policy.json'),
        'genesis': str(gate_state / 'owner-genesis.json'),
        'bootstrap': str(gate_state / 'owner-bootstrap.json'),
        'journal': str(gate_state / 'owner-transitions.json'),
        'head': str(gate_state / 'owner-head.json'),
        'mutation_intent': str(gate_state / 'owner-mutation-intent.json')},
        'issuer_key': str(issuer_state / 'issuer-key.bin'),
        'operation_policy': str(issuer_state / 'worldline-operation-policy.json'),
        'native': str(owner.core.library_path),
        'original_config': str(resource / 'run-config-v1.json'),
        'original_database': str(resource / 'run-state-v1/ledger.sqlite'),
        'scoped_config': scoped_path,
        'scoped_database': None if scoped_path is None else str(resource / 'run-scoped-state-v1/ledger.sqlite'),
        'store_database': str(Path(spec['paths']['state']) / 'worldline.sqlite3'),
        'universe_genesis': str(authority / 'authority/universe/root/genesis.json')}
    context = _capture_operation_sources(spec, private_bytes(spec['genesis']), gate_raw,
        paths, capture_kernel_material(owner.core, recovery['kernel_build']),
        core=owner.core, source_lease=owner.source_lease)
    owner.source_lease.check()
    return context

def _capture_operation_sources(spec, lease_genesis_raw, gate_config_raw, paths, native, *, core, source_lease,
                               head_capture=None):
    """One complete source representation shared by live and early Intake."""
    from .operation_capture import archive as original_archive
    from .protected_owner import private
    from .protected_resource_runtime import canonical, exact
    from .protected_startup import exact_json, digest
    from . import resource_scoped_run_ledger as S
    lease_genesis = exact_json(lease_genesis_raw)
    policy_raw = private_bytes(paths['operation_policy'])
    policy = exact_json(policy_raw)
    journal_path = policy['journal']
    journal_raw = private_bytes(journal_path)
    body = exact_json(journal_raw)['body']
    owner_paths = paths['owner']
    owner_policy_raw = private(owner_paths['policy'])
    owner_policy = exact_json(owner_policy_raw)
    owner_journal_raw = private(owner_paths['journal'])
    owner_context = {'schema': 'worldline.owner-current-context-v1', 'paths': owner_paths,
        'policy_raw': owner_policy_raw, 'genesis_raw': private(owner_paths['genesis']),
        'bootstrap_raw': private(owner_paths['bootstrap']), 'journal_raw': owner_journal_raw,
        'head_raw': private(owner_paths['head']),
        'mutation_intent_present': os.path.lexists(owner_paths['mutation_intent']),
        'issuer_key_path': paths['issuer_key'], 'native_path': paths['native'],
        'source_files': [{'path': str(path), 'raw': private(path, confidential=False)}
            for path in dict.fromkeys((*owner_policy['sources'], paths['native']))]}
    original_config_raw = private_bytes(paths['original_config'])
    original_config = exact(original_config_raw)
    original_sql = _database(paths['original_database'])
    original_tables = {table['name']: table for table in original_sql['tables']}
    meta = [list(row[1:]) for row in original_tables['run_meta']['rows']]
    rows = [list(row[1:]) for row in original_tables['run_rows']['rows']]
    events = [list(row[1:]) for row in original_tables['run_events']['rows']]
    original = {'family': 'ORIGINAL', 'config_raw': original_config_raw,
        'genesis': original_config['genesis'], 'meta': meta, 'rows': rows, 'events': events}
    history = original
    scoped_history = ()
    if paths['scoped_config'] is not None:
        scoped_config_raw = private_bytes(paths['scoped_config'])
        cfg = exact(scoped_config_raw)
        scoped_sql = _database(paths['scoped_database'])
        scoped_tables = {table['name']: table for table in scoped_sql['tables']}
        scoped_meta = [list(row[1:]) for row in scoped_tables['scoped_meta']['rows']]
        scoped_events = [list(row[1:]) for row in scoped_tables['scoped_events']['rows']]
        require(len(scoped_meta) == 1, 'CUSTODY_OPERATION_SCOPED_META_CARDINALITY')
        binding = exact(bytes(scoped_meta[0][0]))
        scoped_history = tuple(exact(bytes(row[2])) for row in scoped_events)
        genesis_anchor = {'binding': binding, 'genesis': cfg['genesis'],
                          'original_prefix': cfg['original_prefix']}
        head_anchor = {**genesis_anchor, 'snapshot': exact(bytes(scoped_meta[0][3])),
                       'head': scoped_meta[0][4]}
        history = {'family': 'SCOPED', 'original': original, 'config_raw': scoped_config_raw,
            'binding': binding, 'genesis': cfg['genesis'], 'original_prefix': cfg['original_prefix'],
            'genesis_archive_raw': original_archive(S.record(S.restore(cfg['genesis']))),
            'meta': scoped_meta, 'events': scoped_events,
            'event_archives': [original_archive(event) for event in scoped_history],
            'replay_archives': [original_archive({'packet': S.record(S.restore(event['packet'])),
                'native': S.record(S.restore(event['native']))}) for event in scoped_history],
            'genesis_anchor_raw': canonical(genesis_anchor), 'head_anchor_raw': canonical(head_anchor)}
    observations = [{'event': event, 'material': bytes.fromhex(event['snapshot']),
        'observation': event['native']['observation']}
        for event in body['events'] if event['cause'] not in ('PREPARATION', 'OWNER_CANONICAL')]
    store_sql = _database(paths['store_database'])
    store_tables = {table['name']: table for table in store_sql['tables']}
    chains = {}
    canonical_files = []
    for table, kind in (('causal_events', 'events'), ('receipts', 'receipts')):
        captured = store_tables[table]
        columns = [row[1] for row in captured['columns']]
        chain = []
        for cells in captured['rows']:
            row = dict(zip(columns, cells[1:]))
            path = Path(row['canonical_path'])
            before = path.lstat()
            raw = private(path, confidential=False)
            after = path.lstat()
            require(before == after and stat.S_ISREG(after.st_mode),
                    'CUSTODY_OPERATION_CANONICAL_FILE_CHANGED')
            chain.append((row, raw))
            canonical_files.append({'kind': kind, 'canonical_path': row['canonical_path'],
                'path': str(path), 'raw': raw, 'identity': {'device': after.st_dev,
                'inode': after.st_ino, 'uid': after.st_uid, 'gid': after.st_gid,
                'mode': stat.S_IMODE(after.st_mode)}})
        chains[kind] = chain
    owner_genesis = exact_json(private_bytes(policy['genesis_file']))['body']
    head_sql = (_database(policy['head_database']) if head_capture is None
                else head_capture['logical_database'])
    context = {'binding': body['binding'],
        'owner_binding': exact_json(owner_journal_raw)['body']['binding'],
        'policy': policy, 'owner_genesis': owner_genesis, 'journal': body,
        'owner_genesis_raw': original_archive(owner_genesis),
        'lease_genesis_raw': lease_genesis_raw, 'lease_genesis': lease_genesis,
        'installation_raw': original_archive(spec), 'gate_config_raw': gate_config_raw,
        'gate_managed_observation_raw': original_archive(exact_json(gate_config_raw)['managed_observation']),
        'resource_genesis': original_config['genesis'],
        'resource_events': [bytes(row[2]).hex() for row in events],
        'universe_genesis_sha256': digest(private_bytes(paths['universe_genesis'])),
        'universe_genesis_path': paths['universe_genesis'],
        'universe_genesis_raw': private_bytes(paths['universe_genesis']),
        'head_database_journal_mode': None if head_sql is None else head_sql['journal_mode'],
        'current_chain_material': original_archive(chains), 'canonical_files': canonical_files,
        'resource_ack_history': history, 'resource_ack_history_raw': original_archive(scoped_history),
        'owner_context': owner_context, 'native_context': original_archive(native),
        'owner_initial_archive': original_archive(owner_genesis['initial_envelope']),
        'boundary_archives': [[original_archive(boundary) for boundary in event['boundaries']]
                              for event in body['events']],
        'operation_authority_observations': observations}
    if head_capture is not None:
        context['head_artifact'] = head_capture
    from .recovery_observation import acquire_readonly_syntax_context, acquire_syntax_facts_from_original
    syntax_context = acquire_readonly_syntax_context(core=core, source_lease=source_lease, spec=spec)
    capsules = acquire_syntax_facts_from_original(original_archive(context), core=core,
                                                  syntax_context=syntax_context)
    owner_context['native_replay_capsules_raw'] = original_archive(capsules)
    require(private_bytes(journal_path) == journal_raw and private_bytes(paths['operation_policy']) == policy_raw
            and private(owner_paths['journal']) == owner_journal_raw
            and private(owner_paths['policy']) == owner_policy_raw,
            'CUSTODY_OPERATION_CONTEXT_SOURCE_CHANGED_DURING_CAPTURE')
    return context
