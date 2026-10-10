"""Existing protected scoped journal and whole-native lifecycle service.

This additive path never creates a journal, rewrites an origin, clears an event,
or projects retained scopes into the historical single-context RunState. Its
caller is the actual early-lease protected producer, never a socket DTO. Native
consistency is distinct from authorization. Installation, syscall persistence,
antirollback, full caller/body/native/cost proof and controls remain required.
"""
from __future__ import annotations
from contextlib import closing, contextmanager
from dataclasses import dataclass
from pathlib import Path
import hashlib,hmac,json,os,sqlite3,threading
from . import resource_scoped_run_ledger as S
from .protected_resource_runtime import private,canonical,exact,require,digest,ResourceProducerRefusal

DOMAIN=b'WORLDLINE-protected-scoped-resource-journal-v1\0'

@dataclass(frozen=True,slots=True)
class ScopedSnapshot:
    state:S.ScopedState
    history:tuple[S.ScopeFrame,...]
    rows:tuple[S.L.RunRow,...]
    projection:tuple[S.PhysicalProjection,...]
    buckets:tuple[S.PhysicalBucket,...]


def snapshot_record(snapshot):
    require(type(snapshot) is ScopedSnapshot,'SCOPED_EXACT_SNAPSHOT_REQUIRED')
    return S.record({name:getattr(snapshot,name) for name in snapshot.__dataclass_fields__})


def snapshot_restore(record):
    value=S.restore(record)
    require(type(value) is dict and set(value)==set(ScopedSnapshot.__dataclass_fields__),
            'SCOPED_COMPLETE_SNAPSHOT_REQUIRED')
    snapshot=ScopedSnapshot(**value)
    require(type(snapshot.state) is S.ScopedState and all(type(getattr(snapshot,name)) is tuple
        for name in ('history','rows','projection','buckets')),'SCOPED_SNAPSHOT_TYPE_CHANGED')
    for name,kind in (('history',S.ScopeFrame),('rows',S.L.RunRow),
                      ('projection',S.PhysicalProjection),('buckets',S.PhysicalBucket)):
        require(all(type(item) is kind for item in getattr(snapshot,name)),
                'SCOPED_FULL_ROSTER_TYPE_CHANGED')
    return snapshot


def packet_before(packet):
    return ScopedSnapshot(packet.before,packet.history,packet.rows,packet.projection,packet.buckets)


def packet_after(packet):
    return ScopedSnapshot(packet.proposed,packet.proposed_history,packet.proposed_rows,
                          packet.proposed_projection,packet.proposed_buckets)


class ScopedRunLedgerService:
    """No network entrypoint or root-UID-only mutation authorization."""
    def __init__(self,lease,gate,core,historical):
        from .protected_startup import StartupLease
        from .core import Core
        import intent_gate,run_service
        require(type(lease) is StartupLease and lease.gate is gate and type(gate) is intent_gate.Gate
            and type(core) is Core and type(historical) is run_service.RunLedgerService
            and historical.root==gate.root/'authority/resource' and os.geteuid()==0,
            'SCOPED_ACTUAL_EARLY_LEASE_AND_ORIGINAL_SERVICE_REQUIRED')
        self.lease,self.gate,self.core,self.historical=lease,gate,core,historical
        self.root=historical.root;self.state_dir=self.root/'run-scoped-state-v1'
        self.config_path=self.root/'run-scoped-config-v1.json';self.db_path=self.state_dir/'ledger.sqlite'
        lease.intact();require(self.config_path in lease.allowed and self.state_dir/'instance.lock' in lease.fds
            and str(self.db_path) in lease.spec['provisioned_state'],'SCOPED_PRECONSTRUCTION_LOCK_AND_GENESIS_REQUIRED')
        private(self.state_dir,directory=True);self.config_raw=private(self.config_path)
        require(lease.source_lease.file(str(self.config_path),('DATA',))==self.config_raw,
                'SCOPED_EARLY_OWNER_CONFIGURATION_CHANGED')
        self.cfg=exact(self.config_raw)
        require(type(self.cfg) is dict and set(self.cfg)=={'schema','installation_id','gate_config_sha256',
            'native_sha256','sources','genesis','original_prefix','catalogue','observation_genesis'} and
            self.cfg['schema']=='worldline.protected-scoped-resource-config-v1',
            'SCOPED_OWNER_CONFIGURATION_SCHEMA_CHANGED')
        require(self.cfg['installation_id']==lease.spec['installation_id'] and
            self.cfg['gate_config_sha256']==digest(gate.config_raw) and
            self.cfg['native_sha256']==digest(private(Path(lease.spec['runtime']['native_library']))),
            'SCOPED_ACTUAL_INSTALLATION_BINDING_CHANGED')
        require(type(self.cfg['sources']) is dict and self.cfg['sources'], 'SCOPED_FULL_EXECUTED_SOURCE_ROSTER_REQUIRED')
        for name,expected in self.cfg['sources'].items():
            path=Path(name);require(path.is_absolute() and path in lease.allowed and
                digest(private(path))==expected,'SCOPED_INSTALLED_SOURCE_CHANGED')
        require(str(Path(__file__)) in self.cfg['sources'] and str(Path(S.__file__)) in self.cfg['sources'],
                'SCOPED_EXECUTED_CALLER_SOURCE_UNBOUND')
        self.kernel=S.ScopedRunLedgerKernel(core);self.key=gate.issuer.key
        self.binding={'installation_id':lease.spec['installation_id'],'config_sha256':digest(self.config_raw),
            'gate_config_sha256':digest(gate.config_raw),'original_config_sha256':historical.config_sha,
            'issuer_policy_sha256':gate.issuer.policy_sha256,'key_sha256':digest(self.key),
            'native_sha256':self.cfg['native_sha256'],'sources':self.cfg['sources']}
        self.genesis=snapshot_restore(self.cfg['genesis'])
        original=self.cfg['original_prefix']
        require(type(original) is dict and set(original)=={'genesis','state','rows','events'}
            and type(original['rows']) is list and type(original['events']) is list,
            'SCOPED_COMPLETE_ORIGINAL_PREFIX_REQUIRED')
        require(self.genesis.rows==tuple(S.L.restore_dto(row) for row in original['rows']),
            'SCOPED_GENESIS_DROPS_OR_RELABELS_AN_ORIGINAL_ROW')
        self.order=threading.RLock();self.poisoned=False;self.producer=None
        private(self.db_path);self.identity=self.db_path.lstat()
        require(not self.identity.st_mode&0o077,'SCOPED_DATABASE_NOT_ROOT_PRIVATE')
        with self.connect() as db:
            db.execute('BEGIN')
            try:self._snapshot(db)
            finally:db.rollback()
        lease.loaded()
    def attach(self,producer):
        from .protected_scoped_resource_runtime import ProtectedScopedResourcePrincipal
        require(type(producer) is ProtectedScopedResourcePrincipal and producer.lease is self.lease
            and producer.gate is self.gate and producer.scoped_service is self,
            'SCOPED_ACTUAL_PRODUCER_IDENTITY_REQUIRED')
        require(self.producer is None or self.producer is producer,'SCOPED_PRODUCER_ALREADY_BOUND')
        self.producer=producer
    def intact(self):
        require(not self.poisoned,'SCOPED_DURABILITY_UNKNOWN');self.lease.intact()
        require(private(self.config_path)==self.config_raw and self.gate.issuer.key==self.key,
                'SCOPED_PROTECTED_CONFIGURATION_OR_ISSUER_CHANGED')
        private(self.db_path);info=self.db_path.lstat()
        require((info.st_dev,info.st_ino)==(self.identity.st_dev,self.identity.st_ino),
                'SCOPED_PERSISTED_DATABASE_REPLACED')
    @contextmanager
    def connect(self):
        self.intact()
        with closing(sqlite3.connect('file:'+str(self.db_path)+'?mode=rw',uri=True,isolation_level=None)) as db:
            db.row_factory=sqlite3.Row;db.execute('PRAGMA synchronous=FULL');db.execute('PRAGMA foreign_keys=ON')
            yield db
    def _original_prefix(self):
        # Replays the actual historical native service with every old event and
        # every complete materialized row. Nothing is reconstructed from totals.
        with self.historical.order,self.historical.connect() as db:
            db.execute('BEGIN')
            try:
                old=self.historical._snapshot(db)
                events=tuple(bytes(row[0]) for row in db.execute('SELECT record FROM run_events ORDER BY ordinal'))
                return {'genesis':S.L.dto_record(self.historical.genesis),
                    'state':S.L.dto_record(old.state),'rows':[S.L.dto_record(row) for row in old.rows],
                    'events':[raw.hex() for raw in events]}
            finally:db.rollback()
    def _mac(self,kind,raw):return hmac.new(self.key,DOMAIN+kind+b'\0'+raw,'sha256').hexdigest()
    def _snapshot(self,db):
        require([tuple(row) for row in db.execute('PRAGMA quick_check')]==[('ok',)],'SCOPED_DATABASE_CORRUPT')
        tables={row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        require(tables=={'scoped_meta','scoped_events'},'SCOPED_OWNER_PROVISIONED_SCHEMA_ABSENT')
        for table,names in {'scoped_meta':('binding','genesis','original_prefix','snapshot','head','mac'),
            'scoped_events':('ordinal','request_id','record','mac')}.items():
            require(tuple(row[1] for row in db.execute('PRAGMA table_info('+table+')'))==names,
                    'SCOPED_JOURNAL_SCHEMA_CHANGED')
        meta=db.execute('SELECT * FROM scoped_meta').fetchall();require(len(meta)==1,'SCOPED_GENESIS_MEMBERSHIP_CHANGED')
        meta=meta[0]
        require(meta['binding']==canonical(self.binding) and meta['genesis']==canonical(self.cfg['genesis'])
            and meta['original_prefix']==canonical(self.cfg['original_prefix'])
            and self._original_prefix()==self.cfg['original_prefix'],'SCOPED_ORIGINAL_GENESIS_OR_PREFIX_CHANGED')
        prior=self.genesis;head=digest(canonical({'binding':self.binding,'genesis':self.cfg['genesis'],
            'original_prefix':self.cfg['original_prefix']}));seen=set();events=[]
        for ordinal,row in enumerate(db.execute('SELECT * FROM scoped_events ORDER BY ordinal')):
            raw=bytes(row['record']);event=exact(raw)
            require(row['ordinal']==ordinal and hmac.compare_digest(row['mac'],self._mac(b'event',raw)),
                    'SCOPED_EVENT_MEMBERSHIP_OR_AUTHENTICATION_CHANGED')
            require(set(event)=={'schema','prior','packet','native','source','principal','reply'} and
                event['schema']=='worldline.protected-scoped-resource-event-v1' and event['prior']==head,
                'SCOPED_EVENT_COMPLETE_PREFIX_CHANGED')
            packet=S.restore(event['packet']);decision=S.restore(event['native'])
            require(type(packet) is S.ScopedPacket and type(decision) is S.ScopedNativeDecision,
                    'SCOPED_NATIVE_EVENT_TYPE_CHANGED')
            rid=packet.request.request_id
            require(rid not in seen and row['request_id']==rid and packet_before(packet)==prior,
                    'SCOPED_NATIVE_EVENT_ORIGIN_CHANGED');seen.add(rid)
            actual=self.kernel.decide(packet)
            require(actual==decision and actual.status=='READY','SCOPED_COMPLETE_NATIVE_REDECISION_REFUSED')
            require(event['reply']==self._reply(packet,actual,head),'SCOPED_COMMITTED_REPLY_CHANGED')
            prior=packet_after(packet);head=digest(raw);events.append(event)
        require(meta['snapshot']==canonical(snapshot_record(prior)) and meta['head']==head,
                'SCOPED_ALL_RETAINED_ROWS_OR_HEAD_CHANGED')
        anchor=canonical({'binding':self.binding,'genesis':self.cfg['genesis'],
            'original_prefix':self.cfg['original_prefix'],'snapshot':snapshot_record(prior),'head':head})
        require(hmac.compare_digest(meta['mac'],self._mac(b'head',anchor)), 'SCOPED_HEAD_AUTHENTICATION_CHANGED')
        self.head,self.events=head,tuple(events)
        return prior
    @staticmethod
    def _reply(packet,decision,prior):
        return {'schema':'worldline.protected-scoped-resource-reply-v1','status':decision.status,
            'request_id':packet.request.request_id.hex(),'snapshot':snapshot_record(packet_after(packet)),
            'native':S.record(decision),'prior':prior}
    def snapshot(self):
        with self.order,self.connect() as db:
            db.execute('BEGIN')
            try:return self._snapshot(db)
            finally:db.rollback()
    def committed_history(self):
        # Reentrant RLock only; no ticket reacquisition inside protected callers.
        with self.order,self.connect() as db:
            db.execute('BEGIN')
            try:
                self._snapshot(db);return self.events
            finally:db.rollback()
    def _principal(self,principal):
        from .protected_scoped_resource_runtime import ProtectedScopedResourcePrincipal
        require(type(principal) is ProtectedScopedResourcePrincipal and principal is self.producer
            and principal.scoped_service is self and principal.lease is self.lease and principal.gate is self.gate,
            'SCOPED_ACTUAL_PROTECTED_PRODUCER_REQUIRED')
        principal.intact()
    def _previous(self,db,packet):
        rows=db.execute('SELECT record FROM scoped_events WHERE request_id=?',(packet.request.request_id,)).fetchall()
        require(len(rows)<=1,'SCOPED_REQUEST_MEMBERSHIP_CHANGED')
        if not rows:return None
        event=exact(bytes(rows[0][0]));require(event['packet']==S.record(packet), 'SCOPED_EXACT_REQUEST_ID_CONFLICT')
        return {**event['reply'],'event_sha256':digest(canonical(event))}
    def recover(self,principal,packet):
        # Exact committed result before any fresh context/client/grant check.
        # The whole original native journal is still independently replayed.
        with self.gate.mutex,self.order:
            self._principal(principal)
            require(type(packet) is S.ScopedPacket,'SCOPED_COMPLETE_PACKET_REQUIRED')
            with self.connect() as db:
                db.execute('BEGIN')
                try:
                    self._snapshot(db);reply=self._previous(db,packet)
                    return reply if reply is not None else {'status':'NOT_COMMITTED'}
                finally:db.rollback()
    def commit(self,principal,packet):
        with self.gate.mutex,self.order:
            self._principal(principal)
            require(type(packet) is S.ScopedPacket,'SCOPED_COMPLETE_PACKET_REQUIRED')
            with self.connect() as db:
                db.execute('BEGIN IMMEDIATE')
                try:
                    before=self._snapshot(db);old=self._previous(db,packet)
                    if old is not None:db.rollback();return old
                    require(packet_before(packet)==before,'SCOPED_WHOLE_LEDGER_CAS_CHANGED')
                    source=principal.capture_commit(packet)
                    require(type(source) is dict and source['packet']==S.record(packet),
                            'SCOPED_ACTUAL_PHYSICAL_AND_OPERATION_CAPTURE_CHANGED')
                    decision=self.kernel.decide(packet)
                    require(decision.status=='READY','SCOPED_NATIVE_AUTHORIZATION_'+decision.status)
                    reply=self._reply(packet,decision,self.head)
                    event={'schema':'worldline.protected-scoped-resource-event-v1','prior':self.head,
                        'packet':S.record(packet),'native':S.record(decision),'source':S.record(source),
                        'principal':self.binding,'reply':reply}
                    raw=canonical(event);head=digest(raw)
                    db.execute('INSERT INTO scoped_events VALUES(?,?,?,?)',
                        (len(self.events),packet.request.request_id,raw,self._mac(b'event',raw)))
                    anchor=canonical({'binding':self.binding,'genesis':self.cfg['genesis'],
                        'original_prefix':self.cfg['original_prefix'],'snapshot':snapshot_record(packet_after(packet)),'head':head})
                    db.execute('UPDATE scoped_meta SET snapshot=?,head=?,mac=?',
                        (canonical(snapshot_record(packet_after(packet))),head,self._mac(b'head',anchor)))
                    self._snapshot(db);db.commit()
                    # The existing journal and containing directory are actually
                    # synced before this committed reply can enter an actor ACK.
                    fd=os.open(self.db_path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
                    try:os.fsync(fd)
                    finally:os.close(fd)
                    fd=os.open(self.state_dir,os.O_RDONLY|os.O_DIRECTORY|os.O_CLOEXEC)
                    try:os.fsync(fd)
                    finally:os.close(fd)
                    self._snapshot(db)
                    return {**reply,'event_sha256':head}
                except BaseException:
                    db.rollback();self.poisoned=True;raise
