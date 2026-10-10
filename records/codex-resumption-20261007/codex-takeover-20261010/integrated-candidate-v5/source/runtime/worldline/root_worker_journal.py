"""Read-only original v1 migration grammar; no live constructor or writer.

The exact complete legacy rows and MAC grammar remain migration inputs.
Native v2 migration eligibility decides whether this retained input is usable.
All live custody effects use RootCustodyJournalV2.
"""
from __future__ import annotations
import hashlib,hmac
from .protected_startup import require,digest
from .root_worker_codec import archive,restore_archive
DOMAIN=b'worldline.protected-root-custody-v1\x00'
SCHEMA={
    'genesis':(('name','TEXT'),('value','BLOB')),
    'events':(('event_id','TEXT'),('previous','TEXT'),('operation','TEXT'),('kind','TEXT'),('record','BLOB'),('mac','TEXT')),
    'head':(('name','TEXT'),('event_id','TEXT'),('mac','TEXT')),
}
KINDS=('PREPARED','HELD','RUNNING','EXECUTION_NATIVE','EXECUTION_ACK','HANDOFF_INTENT',
    'CUSTODY_ACK','ORIGINAL_PROGRESS','ORIGINAL_RESULT','HANDLER_TERMINAL','CLOSED',
    'UNKNOWN','FRONT_RECONSTRUCTION','HISTORICAL_SETTLEMENT')

def _mac(key,value):
    return hmac.new(key,DOMAIN+archive(value),hashlib.sha256).hexdigest()

class RetainedV1Reader:
    def _schema(self,db):
        roster=db.execute("SELECT type,name,sql FROM sqlite_master WHERE name NOT LIKE 'sqlite_%'").fetchall()
        require({(kind,name) for kind,name,_sql in roster}=={('table',name) for name in SCHEMA},
                'ROOT_CUSTODY_COMPLETE_SQL_SCHEMA_CHANGED')
        for name,columns in SCHEMA.items():
            observed=db.execute('PRAGMA table_info('+name+')').fetchall()
            require(tuple((row[1],row[2]) for row in observed)==columns,
                    'ROOT_CUSTODY_COMPLETE_SQL_FIELDS_CHANGED')
    def _load(self,db):
        self._schema(db)
        rows=db.execute('SELECT name,value FROM genesis').fetchall()
        require(rows==[('owner-genesis',archive(self.genesis))],
                'ROOT_CUSTODY_PRIOR_GENESIS_ABSENT_OR_CHANGED')
        previous=digest(archive(self.genesis));events=[];seen=set()
        for event_id,prior,operation,kind,raw,mac in db.execute(
                'SELECT event_id,previous,operation,kind,record,mac FROM events ORDER BY rowid'):
            require(type(raw) is bytes and type(operation) is str and kind in KINDS,
                    'ROOT_CUSTODY_RETAINED_EVENT_MALFORMED')
            record=restore_archive(raw)
            base={'previous':prior,'operation':operation,'kind':kind,'record':record}
            expected=digest(archive(base))
            require(prior==previous and event_id==expected and event_id not in seen
                and hmac.compare_digest(mac,_mac(self.key,base)),
                'ROOT_CUSTODY_RETAINED_FULL_HISTORY_CHANGED')
            event={**base,'event_id':event_id,'mac':mac}
            events.append(event);seen.add(event_id);previous=event_id
        heads=db.execute('SELECT name,event_id,mac FROM head').fetchall()
        require(heads==[('current',previous,_mac(self.key,{'head':previous,'genesis':self.genesis}))],
                'ROOT_CUSTODY_CURRENT_HEAD_ABSENT_OR_SPLIT')
        return tuple(events),previous
