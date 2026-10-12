"""Source-only protected full-ledger service; no automatic bootstrap or producer.

Existing resource_lab.service APIs establish root file/peer/SQLite protection;
its U32 budget and consumed-row semantics remain historical. This separate path
calls the exact whole-ledger native kernel before every durable lifecycle write.
Root producer records must be challenge-bound in protected storage. Installing a
record is not an observation proof: producer/native/descendant obligations stay
OPEN until independently qualified. Missing records/config/state fail closed.
"""
from __future__ import annotations
import ctypes
from contextlib import closing,contextmanager
from dataclasses import dataclass
import hashlib,json,os,socket,socketserver,sqlite3,stat,struct,threading
from pathlib import Path
from types import SimpleNamespace
from worldline.resource_run_ledger import (ResourceRunLedgerKernel,RunState,RunRow,
    RunRequest,RunObservation,dto_record,restore_dto)

class Refusal(Exception):pass

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode('ascii')

def digest(value):return hashlib.sha256(value).hexdigest()

def protected_directory(path,*,private=False):
    if not path.is_absolute():raise Refusal('PROTECTED_PATH_INVALID')
    for item in (*reversed(path.parents),path):
        info=item.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid!=0 or info.st_mode&0o022:
            raise Refusal('PROTECTED_DIRECTORY_INVALID')
    if private and path.lstat().st_mode&0o077:raise Refusal('PROTECTED_DIRECTORY_NOT_PRIVATE')

def protected_read(path):
    protected_directory(path.parent)
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        info=os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_uid!=0 or info.st_nlink!=1 or info.st_mode&0o022:
            raise Refusal('PROTECTED_FILE_INVALID')
        with os.fdopen(os.dup(fd),'rb') as source:answer=source.read()
        after=os.fstat(fd)
        if (info.st_dev,info.st_ino,info.st_size,info.st_mtime_ns,info.st_ctime_ns)!=(
             after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns):
            raise Refusal('PROTECTED_FILE_CHANGED')
        return answer
    finally:os.close(fd)

def parse_canonical(raw):
    value=json.loads(raw)
    if canonical(value)!=raw:raise Refusal('NONCANONICAL_PROTECTED_RECORD')
    return value

@dataclass(frozen=True,slots=True)
class Snapshot:
    state: RunState
    rows: tuple[RunRow,...]

class ProtectedObservations:
    """Consume only a separately produced, challenge-bound protected roster.

    The producer is absent from this preparation. This API refuses a missing
    artifact rather than deriving Never_Launched/Reaped from caller metadata,
    launcher return values, absent cgroups, or an asserted protection flag.
    """
    def __init__(self,directory,producer_identity):
        protected_directory(directory,private=True)
        self.directory,self.producer_identity=directory,producer_identity
    def collect(self,before,request):
        challenge=digest(canonical({'domain':'worldline.resource-native-request-v1',
            'state':dto_record(before.state),'rows':[dto_record(row) for row in before.rows],
            'request':dto_record(request)}))
        raw=protected_read(self.directory/(challenge+'.json'))
        record=parse_canonical(raw)
        if (type(record) is not dict or set(record)!={'schema','producer','challenge','observed'}
            or record['schema']!='worldline.protected-resource-observations-v1'
            or record['producer']!=self.producer_identity or record['challenge']!=challenge
            or type(record['observed']) is not list):raise Refusal('PROTECTED_NATIVE_ROSTER_INVALID')
        rows=tuple(restore_dto(row) for row in record['observed'])
        if any(type(row) is not RunObservation for row in rows):raise Refusal('PROTECTED_NATIVE_ROSTER_INVALID')
        return rows

class RunLedgerService:
    def __init__(self,root):
        if os.geteuid()!=0:raise Refusal('ROOT_SERVICE_REQUIRED')
        if (root.name!='resource' or root.parent.name!='authority' or root.parents[1].parent!=Path('/srv')
            or not root.parents[1].name.startswith('cosmogony-canonical-v1.')):
            raise Refusal('UNRECOGNIZED_PROTECTED_RESOURCE_ROOT')
        protected_directory(root)
        self.root=root;self.state_dir=root/'run-state-v1';protected_directory(self.state_dir,private=True)
        self.db_path=self.state_dir/'ledger.sqlite';self.socket_path=root/'run-request-v1.sock'
        self.config_raw=protected_read(root/'run-config-v1.json');cfg=parse_canonical(self.config_raw)
        expected={'schema','genesis','native_sha256','sources','producer','gate_config_sha256'}
        if type(cfg) is not dict or set(cfg) not in (expected,expected|{'source_binding'}):
            raise Refusal('FULL_LEDGER_CONFIG_INVALID')
        if cfg['schema']!='worldline.protected-resource-config-v1':raise Refusal('FULL_LEDGER_CONFIG_INVALID')
        self.config_sha=digest(self.config_raw)
        if type(cfg['sources']) is not dict or not cfg['sources']:raise Refusal('FULL_LEDGER_SOURCE_ROSTER_MISSING')
        required={'run_service.py','runtime/worldline/resource_run_ledger.py'}
        if not required<=cfg['sources'].keys():raise Refusal('FULL_LEDGER_SOURCE_ROSTER_INCOMPLETE')
        self.shared_source=None
        if 'source_binding' in cfg:
            from worldline.protected_shared_source import SharedSourceBinding
            # Config is an authentic owner-created output within initialize.
            # Its protected raw bytes remain bound by the original config SHA;
            # immutable executable inputs and inventory are already lease-selected.
            if protected_read(root/'run-config-v1.json')!=self.config_raw:
                raise Refusal('FULL_LEDGER_CONFIG_CHANGED')
            self.shared_source=SharedSourceBinding(cfg['source_binding'],mutable_root=root)
            self.shared_source.require_roster(cfg['sources'])
            if Path(__file__).absolute()!=self.shared_source.locations['run_service.py']:
                raise Refusal('FULL_LEDGER_SERVICE_LOCATION_INVALID')
            import worldline.resource_run_ledger as caller
            if Path(caller.__file__).absolute()!=self.shared_source.locations['runtime/worldline/resource_run_ledger.py']:
                raise Refusal('FULL_LEDGER_CALLER_LOCATION_INVALID')
        else:
            for name,expected in cfg['sources'].items():
                rel=Path(name)
                if rel.is_absolute() or '..' in rel.parts or type(expected) is not str:
                    raise Refusal('FULL_LEDGER_SOURCE_ROSTER_INVALID')
                if digest(protected_read(root/rel))!=expected:raise Refusal('FULL_LEDGER_SOURCE_CHANGED')
            if Path(__file__).absolute()!=root/'run_service.py':raise Refusal('FULL_LEDGER_SERVICE_LOCATION_INVALID')
            import worldline.resource_run_ledger as caller
            if Path(caller.__file__).absolute()!=root/'runtime/worldline/resource_run_ledger.py':
                raise Refusal('FULL_LEDGER_CALLER_LOCATION_INVALID')
        self.genesis=restore_dto(cfg['genesis'])
        if type(self.genesis) is not RunState:raise Refusal('FULL_LEDGER_GENESIS_INVALID')
        # Epoch zero and nonnegative capacity are native facts. This bootstrap does
        # not use Python range arithmetic as authorization; native genesis is required.
        self.gate_config_sha=cfg['gate_config_sha256']
        gate_cfg=protected_read(root.parent/'gate/config.json')
        if digest(gate_cfg)!=self.gate_config_sha:raise Refusal('FULL_LEDGER_GATE_CONFIG_CHANGED')
        library=(root/'libworldline_core.so' if self.shared_source is None else self.shared_source.library)
        if digest(protected_read(library))!=cfg['native_sha256']:raise Refusal('FULL_LEDGER_NATIVE_CHANGED')
        self.kernel=ResourceRunLedgerKernel(SimpleNamespace(_lib=ctypes.CDLL(str(library))))
        self.observer=ProtectedObservations(root/'native-observations-v1',cfg['producer'])
        self.order=threading.RLock()
        self.order_condition=threading.Condition()
        self.next_ticket=0;self.serving_ticket=0
    @contextmanager
    def ordered_operation(self):
        # Match the original real resource service's method-entry ordering.
        # A recover cannot overtake an already admitted mutation waiting for
        # SQLite. NOT_COMMITTED is still a point-in-time observation.
        if self.shared_source is not None:
            self.shared_source.check()
            if protected_read(self.root/'run-config-v1.json')!=self.config_raw:
                raise Refusal('FULL_LEDGER_CONFIG_CHANGED')
        with self.order_condition:
            ticket=self.next_ticket;self.next_ticket+=1
            self.order_condition.notify_all()
            while ticket!=self.serving_ticket:self.order_condition.wait()
        try:yield
        finally:
            with self.order_condition:
                self.serving_ticket+=1;self.order_condition.notify_all()
    @contextmanager
    def connect(self):
        protected_read(self.db_path)
        info=self.db_path.lstat()
        if info.st_mode&0o077:raise Refusal('FULL_LEDGER_DATABASE_NOT_PRIVATE')
        with closing(sqlite3.connect('file:'+str(self.db_path)+'?mode=rw',uri=True,isolation_level=None)) as db:
            db.row_factory=sqlite3.Row;db.execute('PRAGMA synchronous=FULL');db.execute('PRAGMA foreign_keys=ON')
            yield db
    def _snapshot(self,db):
        results=db.execute('PRAGMA quick_check').fetchall()
        if len(results)!=1 or tuple(results[0])!=('ok',):raise Refusal('FULL_LEDGER_DATABASE_INVALID')
        meta=db.execute('SELECT config_sha,genesis,head FROM run_meta').fetchall()
        if len(meta)!=1 or meta[0]['config_sha']!=self.config_sha or meta[0]['genesis']!=canonical(dto_record(self.genesis)):
            raise Refusal('FULL_LEDGER_BOOTSTRAP_CHANGED')
        rows=db.execute('SELECT ordinal,record FROM run_rows ORDER BY ordinal').fetchall()
        if any(row['ordinal']!=ordinal for ordinal,row in enumerate(rows)):
            raise Refusal('FULL_LEDGER_MEMBERSHIP_INVALID')
        current=Snapshot(restore_dto(parse_canonical(meta[0]['head'])),tuple(restore_dto(parse_canonical(row['record'])) for row in rows))
        if type(current.state) is not RunState or any(type(row) is not RunRow for row in current.rows):
            raise Refusal('FULL_LEDGER_RECORD_INVALID')
        # Native replay checks every retained historical operation and complete roster.
        prior=Snapshot(self.genesis,());seen=set()
        for ordinal,event in enumerate(db.execute('SELECT ordinal,request_id,record FROM run_events ORDER BY ordinal')):
            if event['ordinal']!=ordinal:raise Refusal('FULL_LEDGER_EVENT_MEMBERSHIP_INVALID')
            record=parse_canonical(event['record'])
            legacy={'before','before_rows','proposed','proposed_rows','observed','request'}
            versioned=legacy|{'schema','owner_uid','packet','result'}
            if type(record) is not dict or set(record) not in (legacy,versioned):
                raise Refusal('FULL_LEDGER_EVENT_INVALID')
            before=Snapshot(restore_dto(record['before']),tuple(restore_dto(row) for row in record['before_rows']))
            after=Snapshot(restore_dto(record['proposed']),tuple(restore_dto(row) for row in record['proposed_rows']))
            request=restore_dto(record['request']);observed=tuple(restore_dto(row) for row in record['observed'])
            if type(request) is not RunRequest:raise Refusal('FULL_LEDGER_EVENT_REQUEST_INVALID')
            if request.request_id in seen:raise Refusal('FULL_LEDGER_RETAINED_REQUEST_ID_REUSED')
            seen.add(request.request_id)
            if set(record)==versioned:
                if (record['schema']!='worldline.protected-resource-event-v2' or
                    type(record['owner_uid']) is not int or record['owner_uid']!=0 or
                    record['packet']!=self._event_packet(record) or record['result']!=self._result_body(record)):
                    raise Refusal('FULL_LEDGER_COMPLETE_RESULT_REPLAY_DIVERGED')
            if before!=prior or event['request_id']!=request.request_id:raise Refusal('FULL_LEDGER_REPLAY_DIVERGED')
            if self.kernel.check(before=before.state,before_rows=before.rows,proposed=after.state,
                 proposed_rows=after.rows,observed=observed,request=request)!='READY':raise Refusal('FULL_LEDGER_REPLAY_REFUSED')
            prior=after
        if prior!=current:raise Refusal('FULL_LEDGER_RETAINED_ROWS_DIVERGED')
        return current
    @staticmethod
    def _event_packet(event):
        return {'schema':'worldline.protected-resource-request-v1','proposed':event['proposed'],
                'rows':event['proposed_rows'],'request':event['request']}
    @staticmethod
    def _result_body(event):
        request=restore_dto(event['request'])
        return {'status':'READY','state':event['proposed'],'rows':event['proposed_rows'],
                'request_id':request.request_id.hex()}
    def _event_result(self,event):
        # Exact original response, including the digest of the original
        # complete retained event. Legacy events retain their original bytes.
        return {**self._result_body(event),'event_sha256':digest(canonical(event))}
    @staticmethod
    def _decode_packet(packet):
        if type(packet) is not dict or set(packet)!={'schema','proposed','rows','request'} or packet['schema']!='worldline.protected-resource-request-v1':
            raise Refusal('FULL_LEDGER_REQUEST_INVALID')
        proposed=restore_dto(packet['proposed']);rows=tuple(restore_dto(row) for row in packet['rows']);request=restore_dto(packet['request'])
        if type(proposed) is not RunState or type(request) is not RunRequest or any(type(row) is not RunRow for row in rows):
            raise Refusal('FULL_LEDGER_REQUEST_INVALID')
        return proposed,rows,request
    def _previous(self,db,packet,request,owner_uid):
        rows=db.execute('SELECT record FROM run_events WHERE request_id=?',(request.request_id,)).fetchall()
        if len(rows)>1:raise Refusal('FULL_LEDGER_REQUEST_MEMBERSHIP_DIVERGED')
        if not rows:return None
        event=parse_canonical(rows[0]['record'])
        # All original V1 service commits were accepted from a real root Gate
        # peer. Their owner remains root; no caller Boolean retroactively adds
        # producer authority. Exact logical requester/full tuple is in request.
        recorded_owner=event.get('owner_uid',0)
        if (type(owner_uid) is not int or owner_uid!=recorded_owner or
            self._event_packet(event)!=packet):raise Refusal('FULL_LEDGER_REQUEST_ID_CONFLICT')
        return self._event_result(event)
    def mutate(self,packet,owner_uid):
        with self.ordered_operation():
            if type(owner_uid) is not int or owner_uid!=0:raise Refusal('PEER_NOT_ROOT_GATE')
            proposed,rows,request=self._decode_packet(packet)
            return self._mutate_locked(packet,proposed,rows,request,owner_uid)
    def _mutate(self,packet):
        # Retain the original source API for genuine in-process root service
        # controls; the network path passes its actual SO_PEERCRED uid instead.
        return self.mutate(packet,os.geteuid())
    def _mutate_locked(self,packet,proposed,rows,request,owner_uid):
        with self.order,self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            try:
                before=self._snapshot(db)
                previous=self._previous(db,packet,request,owner_uid)
                if previous is not None:
                    db.rollback()
                    return previous
                observed=self.observer.collect(before,request)
                status=self.kernel.check(before=before.state,before_rows=before.rows,proposed=proposed,
                    proposed_rows=rows,observed=observed,request=request)
                if status!='READY':raise Refusal(status)
                event={'before':dto_record(before.state),'before_rows':[dto_record(row) for row in before.rows],
                    'proposed':dto_record(proposed),'proposed_rows':[dto_record(row) for row in rows],
                    'observed':[dto_record(row) for row in observed],'request':dto_record(request)}
                event.update({'schema':'worldline.protected-resource-event-v2','owner_uid':owner_uid,
                              'packet':packet,'result':self._result_body(event)})
                ordinal=db.execute('SELECT COUNT(*) FROM run_events').fetchone()[0]
                db.execute('INSERT INTO run_events(ordinal,request_id,record) VALUES(?,?,?)',(ordinal,request.request_id,canonical(event)))
                db.execute('DELETE FROM run_rows')
                db.executemany('INSERT INTO run_rows(ordinal,record) VALUES(?,?)',[(i,canonical(dto_record(row))) for i,row in enumerate(rows)])
                db.execute('UPDATE run_meta SET head=?',(canonical(dto_record(proposed)),))
                db.commit()
                return self._event_result(event)
            except BaseException:db.rollback();raise
    def recover(self,packet,owner_uid):
        """Full exact owner/request-bound replay, never a second mutation/effect."""
        with self.ordered_operation():
            if type(owner_uid) is not int or owner_uid!=0:raise Refusal('PEER_NOT_ROOT_GATE')
            _proposed,_rows,request=self._decode_packet(packet)
            with self.order,self.connect() as db:
                db.execute('BEGIN')
                try:
                    self._snapshot(db)
                    answer=self._previous(db,packet,request,owner_uid)
                    return answer if answer is not None else {'status':'NOT_COMMITTED'}
                finally:db.rollback()
    def inspect_launch_intent(self,packet,owner_uid):
        """Read whole native-replayed current ledger plus the exact old result.

        This is retained protected ledger data, not a machine Never_Launched
        observation or a new Boolean authority. Actual producer/custody remains
        required. No append, reservation, charge, release or launch occurs here.
        """
        with self.ordered_operation():
            if type(owner_uid) is not int or owner_uid!=0:raise Refusal('PEER_NOT_ROOT_GATE')
            _proposed,_rows,request=self._decode_packet(packet)
            if request.kind!='RECORD_LAUNCH_INTENT':raise Refusal('FULL_LEDGER_LAUNCH_INTENT_REQUIRED')
            with self.order,self.connect() as db:
                db.execute('BEGIN')
                try:
                    current=self._snapshot(db);previous=self._previous(db,packet,request,owner_uid)
                    if previous is None:return {'status':'NOT_COMMITTED'}
                    return {'schema':'worldline.protected-resource-current-v1','intent_result':previous,
                            'state':dto_record(current.state),'rows':[dto_record(row) for row in current.rows]}
                finally:db.rollback()
    def handle_connection(self,connection):
        pid,uid,_gid=struct.unpack('3i',connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,struct.calcsize('3i')))
        if pid<=0 or uid!=0:raise Refusal('PEER_NOT_ROOT_GATE')
        with connection.makefile('rb') as stream:
            # No magnitude word cap. Framing/host pressure remains OPEN and must be
            # bounded without reducing the original mathematical accepted domain.
            raw=stream.readline()
        if not raw.endswith(b'\n'):raise Refusal('FULL_LEDGER_FRAME_INVALID')
        packet=parse_canonical(raw[:-1])
        if type(packet) is dict and packet.get('schema')=='worldline.protected-resource-recover-v1':
            if set(packet)!={'schema','request'}:raise Refusal('FULL_LEDGER_RECOVER_INVALID')
            return self.recover(packet['request'],uid)
        if type(packet) is dict and packet.get('schema')=='worldline.protected-resource-current-v1':
            if set(packet)!={'schema','request'}:raise Refusal('FULL_LEDGER_CURRENT_INVALID')
            return self.inspect_launch_intent(packet['request'],uid)
        return self.mutate(packet,uid)

class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        try:answer=self.server.ledger.handle_connection(self.request)
        except Refusal as exc:answer={'status':'REFUSED','reason':str(exc)}
        except Exception:answer={'status':'REFUSED','reason':'FULL_LEDGER_PROTECTED_FACT_UNAVAILABLE'}
        self.request.sendall(canonical(answer)+b'\n')

class Server(socketserver.ThreadingMixIn,socketserver.UnixStreamServer):
    daemon_threads=True;allow_reuse_address=False
    def __init__(self,ledger):self.ledger=ledger;super().__init__(str(ledger.socket_path),Handler)

# A producer/install task must establish and seal schema/genesis exactly once.
# Deliberately no CREATE/--init/ready-marker regeneration on an ordinary path.
SCHEMA_SQL="""CREATE TABLE run_meta(config_sha TEXT NOT NULL,genesis BLOB NOT NULL,head BLOB NOT NULL);
CREATE TABLE run_rows(ordinal INTEGER PRIMARY KEY,record BLOB NOT NULL);
CREATE TABLE run_events(ordinal INTEGER PRIMARY KEY,request_id BLOB UNIQUE NOT NULL,record BLOB NOT NULL);"""

def main():
    import argparse,fcntl
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,required=True)
    args=parser.parse_args()
    os.umask(0o077)
    ledger=RunLedgerService(args.root)
    # This lock is provisioned with the sealed initial database; ordinary start
    # cannot create a missing ready/genesis/database/lock artifact.
    lock_path=ledger.state_dir/'instance.lock'
    protected_read(lock_path)
    descriptor=os.open(lock_path,os.O_RDWR|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        fcntl.flock(descriptor,fcntl.LOCK_EX|fcntl.LOCK_NB)
        with ledger.connect() as db:
            db.execute('BEGIN')
            ledger._snapshot(db)
            db.rollback()
        if ledger.socket_path.exists() or ledger.socket_path.is_symlink():
            raise Refusal('FULL_LEDGER_ENDPOINT_ALREADY_PRESENT')
        with Server(ledger) as server:
            os.chmod(ledger.socket_path,0o600)
            server.serve_forever()
    finally:os.close(descriptor)

if __name__=='__main__':main()
