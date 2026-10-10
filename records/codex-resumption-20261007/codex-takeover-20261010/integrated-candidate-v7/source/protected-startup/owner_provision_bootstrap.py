"""Offline owner provisioning source; never called by ordinary daemon startup.

Consumes a complete prewritten root-private owner Genesis and installation
descriptor. It provisions only the one-shot bootstrap ledger. Existing issuer
keys, Gate/Universe journals, native proof, WORLDLINE schema and immutable store
identity must already be separately provisioned and reviewed. No target API is
invoked and no existing state is overwritten or initialized on absence.
"""
import sys
_source_module = sys.modules.get('_worldline_approved_source_loader')
if type(_source_module) is not type(sys):
    raise SystemExit('OWNER_EARLY_APPROVED_SOURCE_ENTRY_REQUIRED')
_source_lease = _source_module.current()
if type(_source_lease) is not _source_module.ApprovedSourceLease:
    raise SystemExit('OWNER_ACTUAL_APPROVED_SOURCE_ENTRY_REQUIRED')
_source_lease.check()
import fcntl,json,os,pathlib,sqlite3,stat

def provision(descriptor_path):
    # Resolve only the explicit installed descriptor's approved runtime root;
    # isolated launch does not inherit an environment-selected Python package.
    descriptor_path = pathlib.Path(descriptor_path)
    raw = _source_lease.file(str(descriptor_path), ('DATA',))
    selected = json.loads(raw)
    source_root = pathlib.Path(selected['runtime']['worldline_source']) / 'runtime'
    _source_lease.directory_or_absent(str(source_root))
    sys.path.insert(0, str(source_root))
    _source_lease.check()
    from worldline.protected_startup import canonical,exact_json,private_bytes,protected,digest,require
    require(os.geteuid()==0,'OWNER_PROVISION_ROOT_REQUIRED')
    descriptor=exact_json(private_bytes(descriptor_path))
    require(descriptor['schema']=='worldline.protected-startup-v1','OWNER_INSTALLATION_SCHEMA')
    genesis_raw=private_bytes(descriptor['genesis'])
    require(_source_lease.file(str(pathlib.Path(descriptor['genesis'])), ('DATA',)) == genesis_raw,
            'OWNER_GENESIS_DATA_BINDING_CHANGED')
    genesis=exact_json(genesis_raw)
    require(genesis['schema']=='worldline.owner-provisioned-genesis-v1' and
            genesis['installation_id']==descriptor['installation_id'] and
            type(genesis['owner_authorization']) is str and genesis['owner_authorization'],
            'OWNER_COMPLETE_GENESIS_AUTHORIZATION_REQUIRED')
    require(set(genesis['journals'])=={'recovery-full-journal','full-use-reservations'},'OWNER_COMPLETE_JOURNAL_SET_REQUIRED')
    root=pathlib.Path(descriptor['paths']['authority_root'])
    locks=[pathlib.Path(descriptor['paths']['state'])/'worldline-store.lock',
           root/'authority/gate/state/gate.lock',root/'authority/state/broker.lock']
    actuator=root/'canonical/actuator';protected(actuator,directory=True)
    require(sorted(path.name for path in actuator.iterdir())==sorted(descriptor['actuator_transactions']),
            'OWNER_ACTUATOR_ROSTER_CHANGED')
    locks.extend(actuator/value/'service.lock' for value in descriptor['actuator_transactions'])
    held=[]
    try:
        for path in locks:
            private_bytes(path)
            fd=os.open(path,os.O_RDWR|os.O_NOFOLLOW|os.O_CLOEXEC)
            held.append(fd);fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        for path in (pathlib.Path(descriptor['paths']['runtime'])/'worldlined.sock',
                     root/'authority/authority.sock',root/'authority/gate/intent.sock'):
            require(not os.path.lexists(path),'OWNER_LEGACY_ENDPOINT_PRESENT')
        target=pathlib.Path(descriptor['bootstrap_ledger'])
        protected(target.parent,directory=True)
        # Explicit owner instruction is the only creator. Partial provisioning
        # remains on disk and requires owner review; there is no retry cleanup.
        fd=os.open(target,os.O_RDWR|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
        os.close(fd)
        db=sqlite3.connect(target.as_uri()+'?mode=rw',uri=True,isolation_level=None)
        try:
            db.execute('PRAGMA journal_mode=WAL');db.execute('PRAGMA synchronous=FULL')
            db.execute('PRAGMA trusted_schema=OFF')
            db.execute('BEGIN IMMEDIATE')
            db.execute('CREATE TABLE bootstrap_identity(installation_id TEXT NOT NULL,genesis_sha256 TEXT NOT NULL)')
            db.execute("CREATE TABLE journal_intents(name TEXT PRIMARY KEY,path TEXT NOT NULL,initial_envelope BLOB NOT NULL,state TEXT NOT NULL CHECK(state IN ('UNUSED','INTENT','CONSUMED')))")
            db.execute('CREATE TABLE journal_history(ordinal INTEGER PRIMARY KEY,name TEXT NOT NULL,prior TEXT NOT NULL,state TEXT NOT NULL,envelope_sha256 TEXT NOT NULL)')
            db.execute('INSERT INTO bootstrap_identity VALUES(?,?)',(descriptor['installation_id'],digest(genesis_raw)))
            for name,record in genesis['journals'].items():
                db.execute('INSERT INTO journal_intents VALUES(?,?,?,?)',
                           (name,record['path'],canonical(record['initial_envelope'])+b'\n','UNUSED'))
            db.execute('COMMIT')
            require(db.execute('PRAGMA quick_check').fetchall()==[('ok',)],'OWNER_BOOTSTRAP_READBACK_FAILED')
            db.execute('PRAGMA wal_checkpoint(FULL)')
        finally:db.close()
        parent=os.open(target.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
        try:os.fsync(parent)
        finally:os.close(parent)
    finally:
        for fd in reversed(held):os.close(fd)

if __name__=='__main__':
    if len(sys.argv)!=2:
        raise SystemExit('OWNER_EXPLICIT_DESCRIPTOR_REQUIRED')
    provision(sys.argv[1])
