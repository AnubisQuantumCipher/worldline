"""Existing early-lease-owned full observation/ACK journal; no absence bootstrap."""
from __future__ import annotations
from pathlib import Path
import hashlib,hmac,os,sqlite3,threading
from .protected_resource_runtime import private,canonical,exact,require,digest
from . import resource_scoped_run_ledger as S

DOMAIN=b'WORLDLINE-protected-scoped-observation-journal-v1\0'

class ScopedObservationJournal:
    def __init__(self,producer):
        self.producer=producer;service=producer.scoped_service
        self.path=service.state_dir/'observations.sqlite';self.key=service.key;self.binding=service.binding
        require(str(self.path) in producer.lease.spec['provisioned_state'] and
            service.state_dir/'observations.lock' in producer.lease.fds,
            'SCOPED_OBSERVATION_EARLY_LOCK_AND_GENESIS_REQUIRED')
        private(self.path);self.identity=self.path.lstat()
        require(not self.identity.st_mode&0o077,'SCOPED_OBSERVATION_JOURNAL_NOT_PRIVATE')
        self.genesis=service.cfg['observation_genesis']
        require(type(self.genesis) is dict and set(self.genesis)=={'schema','installation_id','store_genesis',
            'issuer_head','original_prefix_sha256','event_head'} and
            self.genesis['schema']=='worldline.protected-scoped-observation-genesis-v1' and
            self.genesis['installation_id']==producer.lease.spec['installation_id'] and
            self.genesis['store_genesis']==producer.store.get_meta('protectedStoreGenesis') and
            self.genesis['issuer_head']==producer.lease.genesis['issuer_head'] and
            self.genesis['original_prefix_sha256']==digest(canonical(service.cfg['original_prefix'])),
            'SCOPED_OWNER_PROVISIONED_OBSERVATION_GENESIS_CHANGED')
        self.db=sqlite3.connect('file:'+str(self.path)+'?mode=rw',uri=True,isolation_level=None)
        self.db.execute('PRAGMA synchronous=FULL');self.load()
    def _mac(self,kind,raw):return hmac.new(self.key,DOMAIN+kind+b'\0'+raw,'sha256').hexdigest()
    def load(self):
        private(self.path);info=self.path.lstat()
        require((info.st_dev,info.st_ino)==(self.identity.st_dev,self.identity.st_ino),
                'SCOPED_OBSERVATION_DATABASE_REPLACED')
        require(self.db.execute('PRAGMA quick_check').fetchall()==[('ok',)],'SCOPED_OBSERVATION_DATABASE_CORRUPT')
        require({row[0] for row in self.db.execute("SELECT name FROM sqlite_master WHERE type='table'")}==
            {'observations_meta','observations_events'},'SCOPED_OBSERVATION_SCHEMA_UNPROVISIONED')
        for table,names in {'observations_meta':('binding','genesis','head','mac'),
            'observations_events':('ordinal','cause','reservation','record','mac')}.items():
            require(tuple(row[1] for row in self.db.execute('PRAGMA table_info('+table+')'))==names,
                    'SCOPED_OBSERVATION_SCHEMA_CHANGED')
        meta=self.db.execute('SELECT * FROM observations_meta').fetchall()
        require(len(meta)==1 and meta[0][0]==canonical(self.binding) and meta[0][1]==canonical(self.genesis),
                'SCOPED_OBSERVATION_GENESIS_BINDING_CHANGED')
        head=self.genesis['event_head'];events=[]
        allowed={'PHYSICAL_SAMPLE','CLOSED_NATIVE_WITNESS','ACTOR_NATIVE_COMMITTED','ACTOR_ACK_SENT',
                 'FOLLOWUP_PLANNED','OWNER_RESOLUTION_CAPTURE','STARTUP_RECONCILED',
                 'ACTOR_STDIN_INTENT','ACTOR_STDIN_COMPLETE','ACTOR_STDIN_UNKNOWN',
                 'ACTOR_TRANSPORT_STOP_INTENT','ACTOR_TRANSPORT_STOP_REPLY',
                 'ACTOR_TRANSPORT_FAILURE','ACTOR_TRANSPORT_FAILURE_OUTPUT','ACTOR_TRANSPORT_FAILURE_RESULT',
                 'ACTOR_TRANSPORT_OUTPUT_READ'}
        for ordinal,cause,reservation,raw,mac in self.db.execute('SELECT * FROM observations_events ORDER BY ordinal'):
            raw=bytes(raw);event=exact(raw)
            require(ordinal==len(events) and cause in allowed and
                hmac.compare_digest(mac,self._mac(b'event',raw)) and set(event)=={'schema','prior','cause','reservation','payload'}
                and event['schema']=='worldline.protected-scoped-observation-event-v1' and event['prior']==head
                and event['cause']==cause and event['reservation']==reservation,
                'SCOPED_OBSERVATION_FULL_PREFIX_CHANGED')
            # Payload interpretation occurs only in the exact protected producer
            # and actual native redecision. This MAC is custody, not liveness.
            S.restore(event['payload']);head=digest(raw);events.append(event)
        anchor=canonical({'binding':self.binding,'genesis':self.genesis,'head':head})
        require(meta[0][2]==head and hmac.compare_digest(meta[0][3],self._mac(b'head',anchor)),
                'SCOPED_OBSERVATION_DURABLE_HEAD_CHANGED')
        self.head,self.events=head,tuple(events)
    def append(self,cause,reservation,payload):
        self.producer.intact();self.db.execute('BEGIN IMMEDIATE')
        try:
            self.load();event={'schema':'worldline.protected-scoped-observation-event-v1','prior':self.head,
                'cause':cause,'reservation':reservation,'payload':S.record(payload)};raw=canonical(event);head=digest(raw)
            self.db.execute('INSERT INTO observations_events VALUES(?,?,?,?,?)',
                (len(self.events),cause,reservation,raw,self._mac(b'event',raw)))
            anchor=canonical({'binding':self.binding,'genesis':self.genesis,'head':head})
            self.db.execute('UPDATE observations_meta SET head=?,mac=?',(head,self._mac(b'head',anchor)))
            self.load();self.db.commit()
            # Existing full journal bytes and its containing directory are synced
            # before an acknowledged native actor commit/terminal witness escapes.
            fd=os.open(self.path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
            try:os.fsync(fd)
            finally:os.close(fd)
            fd=os.open(self.path.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_CLOEXEC)
            try:os.fsync(fd)
            finally:os.close(fd)
            self.load();return event
        except BaseException:self.db.rollback();self.producer.poisoned=True;raise
    def close(self):self.db.close()
