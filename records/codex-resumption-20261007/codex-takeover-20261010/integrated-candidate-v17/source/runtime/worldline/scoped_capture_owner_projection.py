"""Complete factual SQL/JSON preimages for the native scoped owner join.

No policy is evaluated here. Every row, original SQL value and original parser
result stays available, including empty stores, no PRIME and retained scopes.
Call under the existing producer locks; the parent retains descriptor/source
custody and passes the independently captured owner_state to native code.
"""
from pathlib import Path
import json
from .protected_resource_runtime import canonical,private,require
from . import resource_scoped_run_ledger as S

DOMAIN='worldline.scoped-owner-sql-source-v1'


def decoded_database(database):
    """Lossless decoding receipts, never a replacement for complete SQL rows."""
    result=[]
    for table in database['tables']:
        names=tuple(column[1] for column in table['columns'])
        without='WITHOUT ROWID' in next(row[4] for row in database['schema']
            if row[0]=='table' and row[1]==table['name']).upper()
        offset=0 if without else 1
        for row in table['rows']:
            cells=[]
            for index,name in enumerate(names):
                raw=row[index+offset]
                if type(raw) not in (bytes,str):continue
                try:value=json.loads(raw)
                except (ValueError,UnicodeError):continue
                cells.append({'column':name,'raw':raw,'value':value})
            result.append({'table':table['name'],'row':row,'cells':tuple(cells)})
    return tuple(result)


def prime_sql_query(db,selector):
    """Original parameter binding and complete first-row SQL observation.

    Do not coerce the parameter in Python: bool binds as INTEGER, floats bind
    as REAL, bytes bind as BLOB, and arbitrary Python integers retain SQLite's
    actual OverflowError. CAST is a separate factual result, not the parameter
    storage class or a license to equate BLOB with TEXT.
    """
    query='SELECT * FROM worlds WHERE instance_id=? OR alias=? OR content_id=?'
    affinity_query='SELECT CAST(? AS TEXT)'
    cursor=db.execute(query,(selector,selector,selector)) if selector else None
    affinity=None if not selector else db.execute(affinity_query,(selector,)).fetchone()[0]
    return {'query':query,'selector':selector,'row':None if cursor is None else cursor.fetchone(),
        'affinity_query':affinity_query,'affinity':affinity,
        'columns':tuple(item[0] for item in db.execute('SELECT * FROM worlds LIMIT 0').description)}


def capture_owner_sql_projection(producer,owner_state):
    from .protected_scoped_resource_runtime import ProtectedScopedResourcePrincipal
    require(type(producer) is ProtectedScopedResourcePrincipal,
        'SCOPED_OWNER_SQL_ACTUAL_PRODUCER_REQUIRED')
    producer.intact()
    result=_capture_sql_projection(producer.lease.spec,producer.lease.source_lease,
        producer.scoped_projection,owner_state)
    producer.intact()
    return result


def _sql_dict_rows(owner_state,suffix,table_name):
    matches=[entry for entry in owner_state['paths'] if entry['path'].endswith(suffix)]
    require(len(matches)==1,'SCOPED_OWNER_SQL_EXACT_DATABASE_REQUIRED')
    tables=[table for table in matches[0]['logical_database']['tables'] if table['name']==table_name]
    require(len(tables)==1,'SCOPED_OWNER_SQL_EXACT_TABLE_REQUIRED')
    table=tables[0];names=tuple(column[1] for column in table['columns'])
    rows=[]
    for row in table['rows']:
        offset=len(row)-len(names)
        require(offset in (0,1),'SCOPED_OWNER_SQL_FULL_ROW_REQUIRED')
        rows.append(dict(zip(names,row[offset:],strict=True)))
    return tuple(rows)


def owner_sql_history(owner_state):
    """Decode acquired current owner SQL without reopening a semantic owner.

    Native must authenticate the original full rows and their complete head
    anchors before relying on this value. This is not an owner absence claim.
    """
    launch=_sql_dict_rows(owner_state,'/authority/resource/run-state-v1/launch.sqlite','launch_events')
    lmeta=_sql_dict_rows(owner_state,'/authority/resource/run-state-v1/launch.sqlite','launch_meta')
    observed=_sql_dict_rows(owner_state,'/authority/resource/run-scoped-state-v1/observations.sqlite','observations_events')
    ometa=_sql_dict_rows(owner_state,'/authority/resource/run-scoped-state-v1/observations.sqlite','observations_meta')
    require(len(lmeta)==len(ometa)==1,'SCOPED_OWNER_SQL_SINGLE_HEAD_REQUIRED')
    # Complete factual V1/V2 event values emitted by the actual current owner
    # SQL capture. RootCustodyFold, not this field name, establishes authority.
    root_events=tuple(event for entry in owner_state['paths']
        for event in entry.get('logical_database',{}).get('authenticated_root_events',()))
    return {'launch_events':tuple(json.loads(row['record']) for row in sorted(launch,key=lambda row:row['ordinal'])),
        'binding':json.loads(lmeta[0]['binding']),
        'launch_head':lmeta[0]['head'],
        'observation_events':tuple(json.loads(row['record']) for row in sorted(observed,key=lambda row:row['ordinal'])),
        'observation_head':ometa[0]['head'],'root_events':root_events}


def selected_owner_files(owner):
    """Independent full reads of exact source-selected JSON files.

    Parent attaches these to owner_state['selected_files']; the native join
    compares the second receipt read against these bytes and paths. Parent's
    original source/descriptor guard remains the acquisition authority.
    """
    root=Path(owner.spec['paths']['authority_root'])
    paths=(root/'authority/resource/os-producer-v1.json',
        root/'authority/resource/run-config-v1.json',
        root/'authority/resource/run-scoped-config-v1.json',Path(owner.spec['genesis']),
        root/'authority/gate/config.json',root/'authority/issuer/state/policy.json',
        root/'authority/issuer/state/head.json',root/'authority/universe/root/genesis.json',
        root/'authority/universe/root/registry.json')
    owner.source_lease.check()
    result=tuple({'path':str(path),'raw':private(path)} for path in paths)
    owner.source_lease.check()
    return result


def capture_retained_owner_sql_projection(owner,projection,owner_state):
    from .protected_root_worker import RootWorkerFront,RootWorkerIntake,RootWorkerProcess
    require(type(owner) in (RootWorkerFront,RootWorkerIntake,RootWorkerProcess),
        'SCOPED_OWNER_SQL_ACTUAL_RETAINED_OWNER_REQUIRED')
    return _capture_sql_projection(owner.spec,owner.source_lease,projection,owner_state)


def _capture_sql_projection(spec,source_lease,projection,owner_state):
    # Actual raw acquisition only. Never load a semantic journal or reopen its
    # owner; reconstruction/intake runs before those owners exist.
    from .root_worker_current_state import _database
    from .scoped_source_image import source_restore
    import hashlib,sqlite3
    from urllib.parse import quote
    from .store import _json_load
    source_lease.check();root=Path(spec['paths']['authority_root'])
    paths=(root/'authority/resource/os-producer-v1.json',root/'authority/resource/run-config-v1.json',
        root/'authority/resource/run-scoped-config-v1.json',
        Path(spec['genesis']),root/'authority/gate/config.json',root/'authority/issuer/state/policy.json',
        root/'authority/issuer/state/head.json',root/'authority/universe/root/genesis.json',
        root/'authority/universe/root/registry.json')
    files=tuple({'path':str(path),'raw':private(path)} for path in paths)
    files=tuple(dict(item,value=json.loads(item['raw']),canonical=canonical(json.loads(item['raw']))) for item in files)
    databases=[]
    for entry in owner_state['paths']:
        if 'logical_database' not in entry:continue
        database=_database(Path(entry['path']))
        databases.append({'path':entry['path'],'logical_database':database,'decoded':decoded_database(database)})
    # Select by exact descriptor-derived paths, not suffixes offered by data.
    observed={'paths':tuple(databases)}
    journals=[]
    for name,suffix,meta_name,event_name in (
        ('scoped','/authority/resource/run-scoped-state-v1/ledger.sqlite','scoped_meta','scoped_events'),
        ('launch','/authority/resource/run-state-v1/launch.sqlite','launch_meta','launch_events'),
        ('observations','/authority/resource/run-scoped-state-v1/observations.sqlite','observations_meta','observations_events')):
        matches=[entry for entry in databases if entry['path']==str(root)+suffix]
        require(len(matches)==1,'SCOPED_OWNER_SQL_SELECTED_DATABASE_REQUIRED')
        rows=_sql_dict_rows(observed,suffix,meta_name)
        require(len(rows)==1,'SCOPED_OWNER_SQL_SINGLE_HEAD_REQUIRED');meta=rows[0]
        binding=json.loads(meta['binding']);genesis=json.loads(meta['genesis'])
        anchor={'binding':binding,'genesis':genesis,'head':meta['head']}
        initial={'binding':binding,'genesis':genesis}
        if name=='scoped':
            anchor.update(original_prefix=json.loads(meta['original_prefix']),snapshot=json.loads(meta['snapshot']))
            initial.update(original_prefix=anchor['original_prefix'])
        events=sorted(_sql_dict_rows(observed,suffix,event_name),key=lambda row:row['ordinal'])
        bodies=tuple(json.loads(row['record']) for row in events)
        journals.append({'kind':name,'path':str(root)+suffix,'binding':binding,'genesis':genesis,
            'events':bodies,'head':meta['head'],'anchor':anchor,'anchor_json':canonical(anchor),
            'initial':initial,'initial_json':canonical(initial),
            'initial_head':hashlib.sha256(canonical(initial)).hexdigest(),
            'event_receipts':tuple({'event':body,'raw':bytes(row['record']),
                'packet':S.restore(body['packet']) if name=='scoped' else None,
                'source':source_restore(body['source']) if name=='scoped' else None,
                'native':S.restore(body['native']) if name=='scoped' else None}
                for row,body in zip(events,bodies,strict=True))})
    def file_value(path):return next(item['value'] for item in files if item['path']==str(path))
    registry=file_value(root/'authority/universe/root/registry.json')
    issuer=file_value(root/'authority/issuer/state/head.json')
    registry_base={key:registry[key] for key in ('schema','universe_id','sequence','event_head','genesis_sha256')}
    issuer_base={key:issuer[key] for key in ('schema','sequence','event_head','policy_sha256')}
    # Original PRIME lookup, with the actual selected row/columns retained.
    store_path=Path(spec['paths']['state'])/'worldline.sqlite3'
    db=sqlite3.connect('file:'+quote(str(store_path),safe='/')+'?mode=ro',uri=True,isolation_level=None)
    try:
        db.execute('PRAGMA query_only=ON');db.execute('BEGIN')
        raw=db.execute('SELECT value FROM meta WHERE key=?',('primeInstance',)).fetchone()
        selector=None if raw is None else _json_load(raw[0],None)
        prime_query=prime_sql_query(db,selector)
        db.rollback()
    finally:db.close()
    original=file_value(root/'authority/resource/run-scoped-config-v1.json')['original_prefix']
    from .resource_run_ledger import restore_dto
    original_typed={'genesis':restore_dto(original['genesis']),'state':restore_dto(original['state']),
        'rows':tuple(restore_dto(row) for row in original['rows']),
        'events':tuple(bytes.fromhex(raw) for raw in original['events'])}
    source_lease.check()
    return {'schema':DOMAIN,'files':files,'databases':tuple(databases),'journals':tuple(journals),
        'lease_genesis':file_value(Path(spec['genesis'])),
        'scoped_config':file_value(root/'authority/resource/run-scoped-config-v1.json'),
        'original_prefix_typed':original_typed,
        'scoped_binding':next(item['binding'] for item in journals if item['kind']=='scoped'),
        'registry_base':registry_base,'registry_base_json':canonical(registry_base),
        'issuer_base':issuer_base,'issuer_base_json':canonical(issuer_base),'prime_query':prime_query}
