"""Actual in-process protected full-ledger OS producer and lifecycle owner.

Source preparation only. Ordinary packets, root-file observations, UID alone,
empty/missing cgroups and launcher waits cannot issue liveness or reservations.
The physical classifier and whole ledger decide from complete retained inputs.
Startup must hold the exact existing locks before constructing this object.
"""
from __future__ import annotations
from dataclasses import fields,replace
from pathlib import Path
import array,asyncio,fcntl,hashlib,hmac,importlib,json,os,select,socket,sqlite3,stat,struct,subprocess,threading,uuid
from .resource_run_ledger import RunContext,RunBinding,RunRequest,RunRow,RunObservation,RunState,dto_record,restore_dto
from .resource_os_observation import PhysicalFacts,ResourceObservationKernel,facts_record

DOMAIN=b'WORLDLINE-protected-resource-launch-v1\0'
HEADER=b'WL-RESOURCE-SUPERVISOR-v1\n'
class ResourceProducerRefusal(RuntimeError):pass
def require(condition,reason):
    if not condition:raise ResourceProducerRefusal(reason)
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode('ascii')
def digest(raw):return hashlib.sha256(raw).hexdigest()
def exact(raw):
    parsed=json.loads(raw);require(canonical(parsed)==raw,'RESOURCE_NONCANONICAL_PROTECTED_RECORD');return parsed
def private(path,*,directory=False):
    path=Path(path);require(path.is_absolute(),'RESOURCE_PROTECTED_PATH_REQUIRED')
    for parent in (*reversed(path.parents),path):
        info=parent.lstat();leaf=parent==path
        require(info.st_uid==0 and not info.st_mode&0o022 and not stat.S_ISLNK(info.st_mode)
            and (stat.S_ISDIR(info.st_mode) if not leaf or directory else stat.S_ISREG(info.st_mode)),
            'RESOURCE_PROTECTED_CUSTODY_UNAVAILABLE')
    if directory:return info
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        held=os.fstat(fd);require((held.st_dev,held.st_ino)==(info.st_dev,info.st_ino) and held.st_nlink==1,'RESOURCE_PROTECTED_FILE_CHANGED')
        with os.fdopen(os.dup(fd),'rb') as stream:raw=stream.read()
        after=os.fstat(fd);require((held.st_size,held.st_mtime_ns,held.st_ctime_ns)==(after.st_size,after.st_mtime_ns,after.st_ctime_ns),'RESOURCE_PROTECTED_FILE_CHANGED')
        return raw
    finally:os.close(fd)
def full_capture_record(value):
    # Existing explicit DTO grammar: preserve every byte/type/quantity. This
    # storage frame is not a permission, principal or reconstructed live owner.
    from .operation_capture import archive
    return {'schema':'worldline.original-full-capture-archive-v1','archive_hex':archive(value).hex()}
def preparation_records(pending,binding):
    # Both representations originate in THIS authenticated complete capture.
    # Never decode a retained row into permission or rewrite its signed bytes.
    archive_record={'pending':full_capture_record(pending),
        'operation_binding':full_capture_record(binding)}
    try:
        original_json={'pending':json.loads(canonical(pending)),
            'operation_binding':json.loads(canonical(binding))}
    except (TypeError,ValueError):
        # The old JSON grammar cannot represent some complete native DTOs.
        # The original lossless archive preserves them without projection.
        original_json=None
    return {'original_json':original_json,'archive':archive_record}
def preparation_payloads(row,native_result,original_request,join,records,*,archive_first=False):
    # Every candidate carries the complete SAME row/result/request/credential
    # join and the complete paired pending/binding. No partial replay match.
    base={'row':dto_record(row),'native_result':native_result,
        'original_request':original_request}
    if join is not None:base['credential_join']=join
    choices=('archive','original_json') if archive_first else ('original_json','archive')
    return [{**base,**records[name]} for name in choices if records[name] is not None]
def kernel_bytes(path):
    # This reads the actual pseudo-file. It does not accept a path from a packet.
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        before=os.fstat(fd)
        with os.fdopen(os.dup(fd),'rb') as stream:raw=stream.read()
        after=os.fstat(fd);require((before.st_dev,before.st_ino)==(after.st_dev,after.st_ino),'RESOURCE_KERNEL_FILE_CHANGED')
        return raw
    finally:os.close(fd)
def identity_record(info):return {'device':info.st_dev,'inode':info.st_ino,'uid':info.st_uid,'gid':info.st_gid,'mode':stat.S_IMODE(info.st_mode)}
def empty_binding():return RunBinding(**{field.name:None for field in fields(RunBinding)})
def operation_bytes(value):
    if type(value) is bytes:
        require(value,'RESOURCE_OPERATION_ID_ABSENT');return value
    require(type(value) is str and value,'RESOURCE_OPERATION_ID_INVALID')
    encoded=bytes.fromhex(value);require(encoded and encoded.hex()==value,'RESOURCE_OPERATION_ID_NONCANONICAL');return encoded
def lossless_data(value):
    # Complete framing only, never a permission result or quantity projection.
    kind=type(value)
    if kind is bytes:return {'kind':'bytes','value':value.hex()}
    if kind is float:return {'kind':'float-binary','value':struct.pack('!d',value).hex()}
    if kind is int:
        magnitude=abs(value)
        return {'kind':'int-magnitude','negative':value<0,'magnitude':magnitude.to_bytes((magnitude.bit_length()+7)//8,'little').hex()}
    if kind in (str,bool) or value is None:return {'kind':kind.__name__,'value':value}
    if kind in (list,tuple):return {'kind':kind.__name__,'value':[lossless_data(item) for item in value]}
    if kind is dict:
        require(all(type(key) is str for key in value),'RESOURCE_RECORD_KEY_INVALID')
        return {'kind':'dict','value':{key:lossless_data(item) for key,item in value.items()}}
    raise ResourceProducerRefusal('RESOURCE_COMPLETE_RECORD_ENCODING_UNAVAILABLE')
def startup_policy(spec):
    # The complete descriptor and every installed byte are independently bound
    # by the early source lease. This nonrecursive policy projection binds the
    # meaning of the deployment without hashing a descriptor that inventories
    # the producer configuration containing that hash.
    return {name:spec[name] for name in ('schema','installation_id','runtime','paths','endpoint','actuator_transactions')}

class LaunchJournal:
    """Existing signed append-only SQLite journal; no CREATE/on-absence path."""
    def __init__(self,owner,path):
        self.owner,self.path=owner,path;private(path)
        require(not path.lstat().st_mode&0o077,'RESOURCE_LAUNCH_JOURNAL_NOT_PRIVATE')
        self.db=sqlite3.connect('file:'+str(path)+'?mode=rw',uri=True,isolation_level=None,check_same_thread=False)
        self.db.execute('PRAGMA synchronous=FULL');self.db.execute('PRAGMA foreign_keys=ON')
        self.events=[];self.rows={};self.load()
    def load(self):
        with self.owner.order:return self._load_serial()
    def _load_serial(self):
        require(self.db.execute('PRAGMA quick_check').fetchall()==[('ok',)],'RESOURCE_LAUNCH_JOURNAL_CORRUPT')
        require({row[0] for row in self.db.execute("SELECT name FROM sqlite_master WHERE type='table'")}=={'launch_meta','launch_events'},'RESOURCE_LAUNCH_SCHEMA_UNAVAILABLE')
        for table,names in {'launch_meta':('binding','genesis','head','mac'),'launch_events':('ordinal','record','mac')}.items():
            require(tuple(row[1] for row in self.db.execute('PRAGMA table_info('+table+')'))==names,'RESOURCE_LAUNCH_SCHEMA_CHANGED')
        meta=self.db.execute('SELECT binding,genesis,head,mac FROM launch_meta').fetchall()
        require(len(meta)==1 and meta[0][0]==canonical(self.owner.binding) and meta[0][1]==canonical(self.owner.cfg['launch_genesis']),
            'RESOURCE_LAUNCH_GENESIS_CHANGED')
        events=[];rows={};prior=self.owner.cfg['launch_genesis']['event_head']
        for ordinal,record,mac in self.db.execute('SELECT ordinal,record,mac FROM launch_events ORDER BY ordinal'):
            require(ordinal==len(events),'RESOURCE_LAUNCH_EVENT_MEMBERSHIP_CHANGED')
            expected=hmac.new(self.owner.key,DOMAIN+b'event\0'+record,'sha256').hexdigest()
            require(hmac.compare_digest(mac,expected),'RESOURCE_LAUNCH_EVENT_AUTHENTICATION_FAILED')
            event=exact(record)
            require(set(event)=={'prior','cause','reservation','payload'} and event['prior']==prior,'RESOURCE_LAUNCH_EVENT_PREFIX_CHANGED')
            reservation=event['reservation'];old=rows.get(reservation);cause=event['cause'];payload=event['payload']
            if cause=='PREPARED':
                required={'row','native_result','pending','original_request','operation_binding'}
                require(old is None and type(payload) is dict and set(payload) in (required,required|{'credential_join'}),'RESOURCE_LAUNCH_PREPARATION_CHANGED')
                if self.owner.separate_workload:
                    require(payload.get('credential_join')==self.owner._credential_join_record(payload['original_request']),
                        'RESOURCE_RETAINED_REQUESTER_WORKLOAD_JOIN_CHANGED')
                else:require('credential_join' not in payload,'RESOURCE_LEGACY_CREDENTIAL_RECORD_CHANGED')
                row=restore_dto(payload['row']);require(type(row) is RunRow and row.state=='RESERVED' and row.bound.reservation.hex()==reservation,'RESOURCE_LAUNCH_ROW_INVALID')
                rows[reservation]={'phase':'NEVER_DISPATCHED','prepared':event,'events':[event]}
            elif cause in ('DISPATCH_INTENT','HELD','GO_INTENT','CLOSED','UNKNOWN'):
                require(old is not None,'RESOURCE_LAUNCH_PREPARATION_ABSENT')
                allowed={'DISPATCH_INTENT':('NEVER_DISPATCHED',),'HELD':('DISPATCH_INTENDED',),
                    'GO_INTENT':('NAMESPACE_HELD',),'CLOSED':('NAMESPACE_HELD','GO_INTENDED'),
                    'UNKNOWN':('DISPATCH_INTENDED','NAMESPACE_HELD','GO_INTENDED','UNKNOWN')}
                require(old['phase'] in allowed[cause],'RESOURCE_LAUNCH_EVENT_ORDER_CHANGED')
                if cause=='DISPATCH_INTENT' and self.owner.separate_workload:
                    require(type(payload) is dict and payload.get('credential_join')==old['prepared']['payload']['credential_join'],
                        'RESOURCE_DISPATCH_REQUESTER_WORKLOAD_JOIN_CHANGED')
                old['events'].append(event)
                old['phase']={'DISPATCH_INTENT':'DISPATCH_INTENDED','HELD':'NAMESPACE_HELD','GO_INTENT':'GO_INTENDED','CLOSED':'NAMESPACE_CLOSED','UNKNOWN':'UNKNOWN'}[cause]
            elif cause=='MACHINE_ADMISSION':
                require(old is not None and type(payload) is dict and payload.get('schema')=='worldline.protected-machine-admission-v1',
                    'RESOURCE_MACHINE_ADMISSION_RECORD_CHANGED')
                old['events'].append(event)
            elif cause=='OBSERVATION':
                require(type(payload) is dict and set(payload)=={'challenge','state','rows','request','facts','observed','sources'},'RESOURCE_PHYSICAL_OBSERVATION_CHANGED')
            else:raise ResourceProducerRefusal('RESOURCE_LAUNCH_CAUSE_UNKNOWN')
            prior=digest(record);events.append(event)
        require(meta[0][2]==prior,'RESOURCE_LAUNCH_HEAD_CHANGED')
        anchor=canonical({'binding':self.owner.binding,'genesis':self.owner.cfg['launch_genesis'],'head':prior})
        require(hmac.compare_digest(meta[0][3],hmac.new(self.owner.key,DOMAIN+b'head\0'+anchor,'sha256').hexdigest()),'RESOURCE_LAUNCH_HEAD_AUTHENTICATION_FAILED')
        self.events,self.rows,self.head=events,rows,prior
    def append(self,cause,reservation,payload):
        with self.owner.order:return self._append_serial(cause,reservation,payload)
    def _append_serial(self,cause,reservation,payload):
        self.owner.intact();self.db.execute('BEGIN IMMEDIATE')
        try:
            self.load();event={'prior':self.head,'cause':cause,'reservation':reservation,'payload':payload};raw=canonical(event)
            mac=hmac.new(self.owner.key,DOMAIN+b'event\0'+raw,'sha256').hexdigest()
            self.db.execute('INSERT INTO launch_events VALUES(?,?,?)',(len(self.events),raw,mac));head=digest(raw)
            anchor=canonical({'binding':self.owner.binding,'genesis':self.owner.cfg['launch_genesis'],'head':head})
            mac=hmac.new(self.owner.key,DOMAIN+b'head\0'+anchor,'sha256').hexdigest()
            self.db.execute('UPDATE launch_meta SET head=?,mac=?',(head,mac));self.load();self.db.commit();self.load();return event
        except BaseException:self.db.rollback();self.owner.poisoned=True;raise

class ProtectedResourcePrincipal:
    def __init__(self,lease,gate,store,core):
        from .protected_startup import StartupLease,kernel_identity
        from .store import StateStore
        import intent_gate
        require(type(lease) is StartupLease and type(gate) is intent_gate.Gate and type(store) is StateStore
            and lease.gate is gate and lease.store is store and os.geteuid()==0,'RESOURCE_EXACT_STARTUP_PRINCIPAL_REQUIRED')
        self.lease,self.gate,self.store,self.core=lease,gate,store,core;self.poisoned=False;self.order=threading.RLock();self.slots={};self.operation_principal=None
        lease.intact();self.root=gate.root/'authority/resource';self.config_path=self.root/'os-producer-v1.json'
        require(self.config_path in lease.allowed,'RESOURCE_PRODUCER_NOT_INSTALLED')
        self.config_raw=private(self.config_path);self.cfg=exact(self.config_raw)
        expected={'schema','installation_id','startup_policy_sha256','gate_config_sha256','native_sha256','helper','helper_sha256',
            'source_sha256','launch_genesis','workload_uid','workload_gid','costs','systemd_run','systemctl'}
        require(set(self.cfg) in (expected,expected|{'store_genesis_context'}) and self.cfg['schema']=='worldline.protected-resource-os-producer-v1','RESOURCE_PRODUCER_SCHEMA_INVALID')
        require(self.cfg['installation_id']==lease.spec['installation_id'] and self.cfg['startup_policy_sha256']==digest(canonical(startup_policy(lease.spec)))
            and self.cfg['gate_config_sha256']==digest(gate.config_raw),'RESOURCE_PRODUCER_INSTALLATION_CHANGED')
        require(lease.source_lease.file(str(self.config_path),('DATA',))==self.config_raw,
            'RESOURCE_PRODUCER_EARLY_DATA_ENVELOPE_CHANGED')
        self.helper=Path(self.cfg['helper']);require(self.helper in lease.allowed and digest(private(self.helper))==self.cfg['helper_sha256'],
            'RESOURCE_SUPERVISOR_NOT_INSTALLED')
        require(Path(__file__) in lease.allowed and digest(private(Path(__file__)))==self.cfg['source_sha256'],'RESOURCE_PRODUCER_EXECUTED_SOURCE_CHANGED')
        require(self.cfg['native_sha256']==digest(private(Path(lease.spec['runtime']['native_library']))),'RESOURCE_PRODUCER_NATIVE_CHANGED')
        # The owner-inventoried existing actor profile supplies the confined
        # workload UID/GID. The original kernel requester is independent and
        # may be zero. No new required map file or missing-map bootstrap exists.
        require(kernel_identity(self.cfg['workload_uid']) and self.cfg['workload_uid']!=0
            and kernel_identity(self.cfg['workload_gid']),'RESOURCE_WORKLOAD_CREDENTIAL_BINDING_UNAVAILABLE')
        self.separate_workload=self.cfg['workload_uid']!=lease.spec['endpoint']['requester_uid']
        for command in ('systemd_run','systemctl'):
            tool=Path(self.cfg[command]);require(tool in lease.allowed and tool in map(Path,lease.spec['runtime']['tools'].values()),'RESOURCE_MANAGER_TOOL_UNPINNED')
        require(gate.issuer is not None and gate.universe is not None,'RESOURCE_CURRENT_AUTHORITIES_UNAVAILABLE')
        self.key=gate.issuer.key
        module=importlib.import_module('run_service')
        shared=getattr(lease,'shared_source',None)
        if shared is None:
            require(Path(module.__file__)==self.root/'run_service.py','RESOURCE_ACTUAL_LEDGER_SERVICE_UNAVAILABLE')
        else:
            shared.check()
            require(Path(module.__file__)==shared.locations['run_service.py'],
                    'RESOURCE_ACTUAL_LEDGER_SERVICE_UNAVAILABLE')
        self.service=module.RunLedgerService(self.root)
        require((self.service.shared_source is None)==(shared is None),
                'RESOURCE_LEDGER_STARTUP_SOURCE_LAYOUT_CHANGED')
        if shared is not None:
            require(self.service.shared_source.binding==shared.binding,
                    'RESOURCE_LEDGER_STARTUP_COMPLETE_SOURCE_BINDING_CHANGED')
        self.kernel=ResourceObservationKernel(core)
        policy={name:value for name,value in self.cfg.items() if name!='launch_genesis'}
        self.binding={'installation_id':lease.spec['installation_id'],'producer_policy_sha256':digest(canonical(policy)),
            'resource_config_sha256':self.service.config_sha,'gate_config_sha256':digest(gate.config_raw),'helper_sha256':self.cfg['helper_sha256'],
            'issuer_policy_sha256':gate.issuer.policy_sha256,'issuer_key_sha256':digest(self.key)}
        genesis=self.cfg['launch_genesis']
        require(type(genesis) is dict and set(genesis)=={'schema','binding','store_genesis','issuer_head','resource_genesis','event_head'}
            and genesis['schema']=='worldline.protected-resource-launch-genesis-v1' and genesis['binding']==self.binding
            and genesis['store_genesis']==store.get_meta('protectedStoreGenesis') and genesis['issuer_head']==lease.genesis['issuer_head']
            and genesis['resource_genesis']==dto_record(self.service.genesis),'RESOURCE_OWNER_PROVISIONED_GENESIS_UNAVAILABLE')
        path=self.root/'run-state-v1/launch.sqlite'
        require(str(path) in lease.spec['provisioned_state'] and self.root/'run-state-v1/instance.lock' in lease.fds
            and self.root/'run-state-v1/launch.lock' in lease.fds,'RESOURCE_PRECONSTRUCTION_LOCK_GENESIS_REQUIRED')
        self.journal=LaunchJournal(self,path);self.service.observer=self
        lease.loaded();self.intact()
    def intact(self):
        require(not self.poisoned,'RESOURCE_PRODUCER_DURABILITY_UNKNOWN');self.lease.intact()
        require(self.lease.gate is self.gate and self.lease.store is self.store and self.gate.issuer.key==self.key
            and private(self.config_path)==self.config_raw and digest(private(self.helper))==self.cfg['helper_sha256'],
            'RESOURCE_PRODUCER_CUSTODY_CHANGED')
    def current_snapshot(self):
        self.intact()
        with self.service.order,self.service.connect() as db:
            db.execute('BEGIN')
            try:return self.service._snapshot(db)
            finally:db.rollback()
    def _credential_join_record(self,original_record):
        """Complete source/credential data; native grant/use decides authority.

        The already installed owner profile selects actual helper credentials.
        Retained full requester bytes remain unchanged by that choice. A record
        reconstructed from authenticated history cannot replace a fresh socket
        for a new before-effect request; credential_join reads that real socket.
        """
        from .client_peer import validate_observation,decode_credentials
        validate_observation(original_record);peer=original_record['peer']
        raw=bytes.fromhex(peer['rawUcred'])
        require(decode_credentials(raw)==(peer['pid'],peer['uid'],peer['gid'])
            and peer['uid']==self.lease.spec['endpoint']['requester_uid'],
            'RESOURCE_ORIGINAL_REQUESTER_CREDENTIAL_CHANGED')
        return {'schema':'worldline.existing-owner-workload-credential-join-v2',
            'installation_id':self.lease.spec['installation_id'],
            'endpoint':self.lease.spec['endpoint'],
            'startup_policy':startup_policy(self.lease.spec),
            'producer_config_raw':self.config_raw.hex(),
            'producer_config_sha256':digest(self.config_raw),
            'helper':str(self.helper),'helper_sha256':self.cfg['helper_sha256'],
            'workload_uid':self.cfg['workload_uid'],'workload_gid':self.cfg['workload_gid'],
            'original_request':original_record}
    def credential_join(self,original_request):
        if not self.separate_workload:return None
        self.intact()
        from .client_peer import RequestPeer
        require(type(original_request) is RequestPeer,'RESOURCE_ACTUAL_ORIGINAL_REQUEST_PEER_REQUIRED')
        original_record=original_request.observation()
        # Keep the originally accepted equal-UID deployment/event/hash route
        # literal. The new branch consumes the same existing owner profile and
        # adds its full authentic source join, not a caller-selected mapping.
        return self._credential_join_record(original_record)
    def current_context(self):
        self.intact();universe=self.gate.universe.read();record=universe['record'];genesis=self.store.get_meta('protectedStoreGenesis')
        require(genesis==self.lease.genesis['store']['identity'] and type(genesis) is str,
            'RESOURCE_ACTUAL_STORE_GENESIS_CHANGED')
        prime=self.store.prime();roots=self.store.roots();store_id=self.store.get_meta('finalizationStoreId')
        require(type(store_id) is str and store_id,'RESOURCE_ACTUAL_FINALIZATION_STORE_ID_UNAVAILABLE')
        genesis_context=None
        if prime is None:
            genesis_context=self.cfg.get('store_genesis_context')
            require(type(genesis_context) is dict and set(genesis_context)=={'schema','installation_id','store_genesis',
                'finalization_store_id','universe_genesis_sha256','universe_id','instance_id','roots','prime'}
                and genesis_context['schema']=='worldline.owner-provisioned-empty-store-resource-context-v1'
                and genesis_context['installation_id']==self.lease.spec['installation_id']
                and genesis_context['store_genesis']==genesis and genesis_context['finalization_store_id']==store_id
                and genesis_context['universe_genesis_sha256']==self.gate.universe.genesis_sha256
                and genesis_context['universe_id']==universe['universe_id']
                and genesis_context['roots']==[] and genesis_context['prime'] is None,
                'RESOURCE_AUTHENTIC_EMPTY_STORE_GENESIS_CROSSWALK_UNAVAILABLE')
            # This names an owner-provisioned WORLDLINE store/Universe context,
            # never a dummy PRIME UUID or an inferred first-boot permission.
            instance_id=genesis_context['instance_id']
            require(instance_id==record['prime_worldline_id'], 'RESOURCE_GENESIS_UNIVERSE_STORE_CONTEXT_CHANGED')
        else:
            prime_uuid=uuid.UUID(prime.instance_id)
            require(str(prime_uuid)==prime.instance_id,'RESOURCE_ACTUAL_STORE_PRIME_ID_INVALID')
            # Existing adapter grammar applied to the real retained store.
            instance_id=hashlib.sha256(b'COSMOGONY-worldline-instance-v1\0'+prime_uuid.bytes).hexdigest()
            require(instance_id==record['prime_worldline_id']
                and self.gate.config['managed_observation'] is not None
                and instance_id==self.gate.config['managed_observation']['worldline_instance_id'],
                'RESOURCE_ACTUAL_STORE_UNIVERSE_INSTANCE_CHANGED')
        def hex_id(value):
            require(type(value) is str,'RESOURCE_CURRENT_IDENTITY_UNAVAILABLE')
            encoded=bytes.fromhex(value);require(encoded.hex()==value and encoded,'RESOURCE_CURRENT_IDENTITY_INVALID');return encoded
        snapshot=self.current_snapshot();host=kernel_bytes('/etc/machine-id').removesuffix(b'\n');boot=kernel_bytes('/proc/sys/kernel/random/boot_id').removesuffix(b'\n')
        require(host and boot,'RESOURCE_PHYSICAL_HOST_BOOT_UNAVAILABLE')
        # Unit is an owner provisioned cost-policy datum from the independently
        # sealed configuration, never copied from the row being classified.
        units=[]
        require(type(self.cfg['costs']) is dict and self.cfg['costs'],'RESOURCE_FULL_COST_POLICY_UNAVAILABLE')
        for cost in self.cfg['costs'].values():
            require(type(cost) is dict and set(cost)=={'schema','kind','amount','scope'}
                and cost['schema']=='worldline.protected-resource-cost-v1','RESOURCE_COST_POLICY_SCHEMA_CHANGED')
            cost_scope=restore_dto(cost['scope']);require(type(cost_scope) is RunContext,'RESOURCE_COST_POLICY_CONTEXT_INVALID')
            if cost_scope.resource==hex_id(record['policy']['resource_id']) and cost_scope.policy==hex_id(self.gate.config['policy_id']):
                units.append(cost_scope.unit)
        require(units and type(units[0]) is bytes and units[0] and all(unit==units[0] for unit in units),
            'RESOURCE_INDEPENDENT_CURRENT_UNIT_POLICY_UNAVAILABLE')
        # All policy members come from the actual protected Universe replay. The
        # complete policy digest is the real Gate's current policy mapping.
        scope=RunContext(universe=hex_id(universe['universe_id']),policy=hex_id(self.gate.config['policy_id']),
            resource=hex_id(record['policy']['resource_id']),unit=units[0],
            instance=hex_id(instance_id),host=host,boot=boot,authority=hex_id(record['policy']['authority_id']),
            policy_epoch=record['policy_epoch'])
        source={'universe':universe,'store_genesis':genesis,'finalization_store_id':store_id,'store_roots':lossless_data(roots),
            'store_root_count':len(roots),'genesis_context':genesis_context,
            'prime_record':lossless_data(prime.record()) if prime is not None else None,'instance_crosswalk':instance_id,
            'gate_config':self.gate.config,'host':host.hex(),'boot':boot.hex(),
            'resource_state':dto_record(snapshot.state),'resource_rows':[dto_record(row) for row in snapshot.rows],
            'issuer_head':self.gate.issuer.head(),'launch_head':self.journal.head}
        return scope,snapshot.state.resource_epoch,hex_id(universe['event_head']),snapshot.state.ledger_head,source
    def _current_checked(self,before,blank,source):
        owner=source['genesis_context']
        if owner is None:
            require(self.kernel.current(before.state,before.rows[0] if before.rows else None,blank)=='CURRENT_READY',
                'RESOURCE_ACTUAL_CURRENT_CONTEXT_NATIVE_REFUSED')
            return blank
        facts=replace(blank,actual_store_genesis=source['store_genesis'].encode('utf-8'),
            actual_store_id=source['finalization_store_id'].encode('utf-8'),
            owner_store_genesis=owner['store_genesis'].encode('utf-8'),owner_store_id=owner['finalization_store_id'].encode('utf-8'),
            genesis_universe=bytes.fromhex(owner['universe_id']),genesis_instance=bytes.fromhex(owner['instance_id']),
            genesis_context_head=hashlib.sha256(canonical(owner)).digest(),genesis_prime=None,genesis_root_count=source['store_root_count'])
        require(self.kernel.genesis_current(before.state,before.rows[0] if before.rows else None,facts)=='CURRENT_READY',
            'RESOURCE_EMPTY_STORE_GENESIS_NATIVE_REFUSED')
        return facts
    @staticmethod
    def _blank(scope,epoch,universe_head,ledger_head,row,head):
        values={field.name:None for field in fields(PhysicalFacts)}
        values.update(current=scope,current_epoch=epoch,current_universe_head=universe_head,current_ledger_head=ledger_head,
            retained=row.bound if row is not None else empty_binding(),observation_head=head,phase='UNAVAILABLE')
        return PhysicalFacts(**values)
    def collect(self,before,request):
        """Direct actual producer, including the entire retained protected row set."""
        with self.order:
            self.intact();self.journal.load();actual=self.current_snapshot()
            require(before==actual,'RESOURCE_COLLECTOR_CURRENT_LEDGER_CHANGED')
            scope,epoch,uhead,lhead,source=self.current_context()
            challenge=digest(canonical({'domain':'worldline.resource-native-request-v1','state':dto_record(before.state),
                'rows':[dto_record(row) for row in before.rows],'request':dto_record(request)}))
            blank=self._blank(scope,epoch,uhead,lhead,before.rows[0] if before.rows else None,bytes.fromhex(challenge))
            blank=self._current_checked(before,blank,source)
            observed=[];facts=[];sources=[]
            for row in before.rows:
                physical,raw=self._facts(row,blank,challenge)
                kind=self.kernel.classify(before.state,row,physical)
                # Raw category strings are only formatted from the actual native
                # result. They are never selected by a caller or file Boolean.
                effect=kind in ('LIVE','REAPED')
                observed.append(RunObservation(scope=scope,resource_epoch=epoch,bound=row.bound,
                    actual_unit=physical.actual_unit if effect else row.actual_unit,cgroup=physical.cgroup if effect else row.cgroup,
                    invocation=physical.invocation if effect else row.invocation,observation_head=physical.observation_head,observed=kind))
                facts.append(facts_record(physical));sources.append(raw)
            payload={'challenge':challenge,'state':dto_record(before.state),'rows':[dto_record(row) for row in before.rows],
                'request':dto_record(request),'facts':facts,'observed':[dto_record(row) for row in observed],
                'sources':{'current':source,'rows':sources}}
            self.journal.append('OBSERVATION',None,payload)
            return tuple(observed)
    def _facts(self,row,blank,challenge):
        physical=replace(blank,retained=row.bound);key=row.bound.reservation.hex();retained=self.journal.rows.get(key)
        source={'reservation':key,'journal_head':self.journal.head,'challenge':challenge,'events':retained['events'] if retained else [],'kernel':None}
        if retained is None:return physical,source
        prepared=retained['prepared'];require(restore_dto(prepared['payload']['row']).bound==row.bound,'RESOURCE_RETAINED_LAUNCH_BINDING_CHANGED')
        physical=replace(physical,intent=bytes.fromhex(digest(canonical(prepared))))
        if retained['phase']=='NEVER_DISPATCHED':return replace(physical,phase='NEVER_DISPATCHED'),source
        slot=self.slots.get(key)
        if slot is None:
            # Restart lacks the original owned kernel/channel descriptors. Full
            # retained closure recovery is separately verified below; absence
            # cannot become Never_Launched or Reaped.
            return physical,source
        try:captured=slot.observe()
        except (ResourceProducerRefusal,OSError) as exc:
            # Actual loss/absence of a cgroup, descriptor or manager identity
            # keeps the entire original obligation UNKNOWN. It never releases.
            source['kernel']={'refusal':str(exc)};return physical,source
        source['kernel']=captured['raw']
        values=captured['native_fields']
        physical=replace(physical,**values)
        physical=replace(physical,observation_head=bytes.fromhex(digest(canonical(source))))
        return physical,source
    def bind_operation_principal(self,principal):
        module=importlib.import_module('protected_canonical_operations')
        require(type(principal) is module.CanonicalOperationPrincipal and principal.startup_lease is self.lease
            and principal.gate is self.gate,'RESOURCE_ACTUAL_OPERATION_PRINCIPAL_REQUIRED')
        require(self.operation_principal is None or self.operation_principal is principal,'RESOURCE_OPERATION_PRINCIPAL_ALREADY_BOUND')
        self.operation_principal=principal
    def intent_for_operation(self,original_request,operation_id,transaction_record):
        self.intact();principal=self.operation_principal
        require(principal is not None,'RESOURCE_ALL_OPERATION_PRODUCER_UNAVAILABLE')
        material=principal.resource_request_material(original_request,operation_id,transaction_record)
        require(type(material) is dict and set(material)=={'requester','capability','grant_use','workload','payload','provenance','parent','cost_key'},
            'RESOURCE_ACTUAL_OPERATION_MATERIAL_UNAVAILABLE')
        scope,epoch,uhead,lhead,_source=self.current_context();before=self.current_snapshot()
        cost=self.cfg['costs'].get(material['cost_key'])
        require(type(cost) is dict and set(cost)=={'schema','kind','amount','scope'} and cost['schema']=='worldline.protected-resource-cost-v1'
            and cost['scope']==dto_record(scope),'RESOURCE_AUTHENTIC_COST_POLICY_UNAVAILABLE')
        # Policy amounts are complete original quantity encodings. Python does
        # data decoding/proposal only; the full native kernel authorizes them.
        amount_record={**dto_record(RunRow(scope=scope,bound=empty_binding(),parent=None,kind=cost['kind'],state='RESERVED',amount=0,
            observed_usage=None,planned_unit=None,actual_unit=None,cgroup=None,invocation=None)),'amount':cost['amount']}
        amount=restore_dto(amount_record).amount
        from .client_peer import RequestPeer
        require(type(original_request) is RequestPeer,'RESOURCE_ACTUAL_ORIGINAL_REQUEST_PEER_REQUIRED')
        operation_id=operation_bytes(operation_id)
        raw=original_request.observation();seed_record={'operation':operation_id,'request':raw,'transaction':transaction_record,'policy':cost}
        join=self.credential_join(original_request)
        if join is not None:seed_record['credential_join']=join
        seed=canonical(lossless_data(seed_record))
        reservation=hashlib.sha256(DOMAIN+b'reservation\0'+seed).digest();rid=hashlib.sha256(DOMAIN+b'reserve-request\0'+seed).digest()
        bound=RunBinding(reservation=reservation,operation=operation_id,owner=material['requester'],workload=material['workload'],
            universe_head=uhead,capability=material['capability'],grant_use=material['grant_use'],payload=material['payload'],
            provenance=material['provenance'],resource_epoch=epoch)
        row=RunRow(scope=scope,bound=bound,parent=material['parent'],kind=cost['kind'],state='RESERVED',amount=amount,
            observed_usage=None,planned_unit=None,actual_unit=None,cgroup=None,invocation=None)
        require(before.state.resource_epoch==epoch and before.state.ledger_head==lhead,'RESOURCE_PLANNED_CONTEXT_CHANGED')
        return RunRequest(kind='RESERVE',scope=scope,expected_epoch=epoch,expected_ledger_head=lhead,request_id=rid,
            reservation=reservation,operation_id=operation_id,requester=material['requester'],bound=bound,new_row=row)
    def submit_bound(self,pending,packet,original_request):
        """Actual operation/use custody plus original complete native ledger write."""
        with self.gate.mutex,self.order:
            self.intact();principal=self.operation_principal
            require(principal is not None,'RESOURCE_ALL_OPERATION_BINDING_UNAVAILABLE')
            proposed,rows,request=self.service._decode_packet(packet)
            self.journal.load()
            retained=self.journal.rows.get(request.reservation.hex())
            captured=(principal.resource_binding(pending,original_request) if request.kind=='RESERVE' else
                principal.resource_lifecycle_binding(pending,original_request,request,
                    retained['events'] if retained is not None else []))
            require(type(captured) is dict and {'scope','bound','request','native_use','event_id'}<=set(captured),'RESOURCE_NATIVE_OPERATION_BINDING_UNAVAILABLE')
            require(captured['scope']==dto_record(request.scope) and captured['bound']==dto_record(request.bound)
                and captured['request']==dto_record(request),'RESOURCE_FULL_OPERATION_INTENT_CHANGED')
            require(pending is principal.pending_for_operation(request.operation_id),
                'RESOURCE_ACTUAL_NATIVE_OPERATION_PENDING_REQUIRED')
            join=self.credential_join(original_request) if request.kind=='RESERVE' else None
            records=preparation_records(pending,captured) if request.kind=='RESERVE' else None
            answer=self.service.mutate(packet,os.geteuid())
            if request.kind=='RESERVE':
                key=request.reservation.hex();self.journal.load();old=self.journal.rows.get(key)
                payloads=preparation_payloads(request.new_row,answer,original_request.observation(),join,records)
                if old is None:self.journal.append('PREPARED',key,payloads[0])
                else:require(any(old['prepared']['payload']==payload for payload in payloads),
                    'RESOURCE_COMMITTED_PREPARATION_REPLAY_CHANGED')
            return answer
    def capture_control_submission(self,control,packet):
        """Authenticate the complete operation before its genuine socket RPC.

        The Gate bridge owns its mutex while waiting on that RPC. A different
        server thread must not attempt to borrow/reacquire that mutex. The exact
        owner control captures the original native/use binding before dispatch
        and verifies the actual complete commit before retaining preparation.
        """
        from .owner_resource_control import OwnerResourceControl
        require(type(control) is OwnerResourceControl and control.resources is self
            and control.principal is self.operation_principal,
            'RESOURCE_ACTUAL_SELECTED_CONTROL_REQUIRED')
        with self.gate.mutex,self.order:
            control.intact();self.intact();principal=self.operation_principal
            _proposed,_rows,request=self.service._decode_packet(packet)
            self.journal.load();retained=self.journal.rows.get(request.reservation.hex())
            pending=principal.pending_for_operation(request.operation_id)
            original=control.request
            captured=(principal.resource_binding(pending,original) if request.kind=='RESERVE' else
                principal.resource_lifecycle_binding(pending,original,request,
                    retained['events'] if retained is not None else []))
            require(type(captured) is dict and {'scope','bound','request','native_use','event_id'}<=set(captured)
                and captured['scope']==dto_record(request.scope)
                and captured['bound']==dto_record(request.bound)
                and captured['request']==dto_record(request),
                'RESOURCE_FULL_OPERATION_INTENT_CHANGED')
            join=self.credential_join(original) if request.kind=='RESERVE' else None
            records=preparation_records(pending,captured)
            return {'packet':json.loads(canonical(packet)),'binding':records['archive']['operation_binding'],
                'pending':records['archive']['pending'],'preparation_records':records,
                'original_request':original.observation(),'credential_join':join}
    def retain_control_submission(self,control,captured,answer):
        """Whole actual native service result; no caller success Boolean."""
        from .owner_resource_control import OwnerResourceControl
        require(type(control) is OwnerResourceControl and control.resources is self,
            'RESOURCE_ACTUAL_SELECTED_CONTROL_REQUIRED')
        # The real Gate bridge owns its mutex in the waiting client thread.
        # This exact control's sole admitted server thread retains the commit
        # under the whole resource order, using the immutable capture made
        # before dispatch. Canonical/Gate mutation resumes only after reply.
        with self.order:
            control.intact();self.intact();packet=captured['packet']
            key=restore_dto(packet['request']).request_id.hex()
            require(control.captures.get(key) is captured,
                'RESOURCE_CONTROL_ACTUAL_PRE_DISPATCH_CAPTURE_REQUIRED')
            _proposed,_rows,request=self.service._decode_packet(packet)
            require(captured['original_request']==control.request.observation()
                and captured['pending']==full_capture_record(
                    self.operation_principal.pending_for_operation(request.operation_id)),
                'RESOURCE_ACTUAL_NATIVE_OPERATION_PENDING_REQUIRED')
            actual=self.service.recover(packet,os.geteuid())
            require(actual==answer and actual.get('status')=='READY',
                'RESOURCE_ACTUAL_COMMITTED_RESULT_REQUIRED')
            if request.kind=='RESERVE':
                self.journal.load();key=request.reservation.hex();old=self.journal.rows.get(key)
                records=captured['preparation_records']
                require(records['archive']=={'pending':captured['pending'],
                    'operation_binding':captured['binding']},
                    'RESOURCE_CONTROL_COMPLETE_CAPTURE_PAIR_CHANGED')
                payloads=preparation_payloads(request.new_row,actual,captured['original_request'],
                    captured['credential_join'],records,archive_first=True)
                if old is None:self.journal.append('PREPARED',key,payloads[0])
                else:require(any(old['prepared']['payload']==payload for payload in payloads),
                    'RESOURCE_COMMITTED_PREPARATION_REPLAY_CHANGED')
            return actual
    def dispatch_control_launch(self,control,reservation):
        """Real original supervisor dispatch after an already committed intent.

        RECORD_RUNNING and GO remain separate, native-checked caller steps. The
        complete original policy, machine admission, descriptor and supervisor
        observations are retained; no future InvocationID can be supplied.
        """
        from .owner_resource_control import OwnerResourceControl
        from .admission import ResourcePolicy
        require(type(control) is OwnerResourceControl and control.resources is self,
            'RESOURCE_ACTUAL_SELECTED_CONTROL_REQUIRED')
        control.intact();self.intact();self.journal.load()
        retained=self.journal.rows.get(reservation.hex())
        require(retained is not None and retained['phase']=='NEVER_DISPATCHED'
            and reservation.hex() not in self.slots,'RESOURCE_LAUNCH_REPLAY_OR_UNKNOWN')
        plan=self.operation_principal.resource_launch_material(control.request,reservation)
        require(type(plan) is dict and set(plan)=={'bound','argv','cwd','environment',
            'systemd_properties','policy','executables'},
            'RESOURCE_AUTHENTIC_OPERATION_LAUNCH_PLAN_UNAVAILABLE')
        before=self.current_snapshot();selected=[row for row in before.rows
            if row.bound.reservation==reservation]
        require(len(selected)==1 and selected[0].state=='LAUNCH_INTENT'
            and plan['bound']==dto_record(selected[0].bound),
            'RESOURCE_NATIVE_LAUNCH_INTENT_REQUIRED_BEFORE_DISPATCH')
        row=selected[0];require(row.parent is None,
            'RESOURCE_PARENT_NAMESPACE_LAUNCH_ROUTING_UNAVAILABLE')
        join=self.credential_join(control.request)
        if join is not None:require(retained['prepared']['payload'].get('credential_join')==join,
            'RESOURCE_ACTUAL_REQUESTER_WORKLOAD_JOIN_CHANGED_BEFORE_LAUNCH')
        require(type(plan['argv']) is list and plan['argv'] and all(type(word) is str
            and '\0' not in word for word in plan['argv']) and type(plan['cwd']) is str
            and Path(plan['cwd']).is_absolute() and type(plan['environment']) is dict,
            'RESOURCE_LAUNCH_PLAN_ENCODING_INVALID')
        require(type(plan['systemd_properties']) is list and all(type(word) is str
            and word and '\0' not in word for word in plan['systemd_properties'])
            and type(plan['policy']) is dict and type(plan['executables']) is dict,
            'RESOURCE_COMPLETE_ENFORCED_POLICY_UNAVAILABLE')
        policy=ResourcePolicy.from_mapping(plan['policy'])
        require(policy.enforcement=='cgroup2' and plan['systemd_properties']==policy.unit_properties(),
            'RESOURCE_ORIGINAL_ENFORCED_POLICY_CHANGED')
        sandbox=Path(self.lease.spec['runtime']['tools']['bwrap'])
        require(plan['argv'][0]==str(sandbox) and sandbox in self.lease.allowed
            and plan['executables'].get(str(sandbox))==digest(private(sandbox)),
            'RESOURCE_ACTUAL_SANDBOX_EXECUTABLE_UNAVAILABLE')
        for name,value in plan['environment'].items():
            require(type(name) is str and type(value) is str and name
                and name.replace('_','a').isalnum() and not name[0].isdigit()
                and '\0' not in value,'RESOURCE_WORKLOAD_ENVIRONMENT_INVALID')
        self.machine_admission(reservation,policy,'DISPATCH')
        require(before==self.current_snapshot(),'RESOURCE_MACHINE_LEDGER_CHANGED_BEFORE_EFFECT')
        packet=control.packet_for_kind('RECORD_LAUNCH_INTENT')
        require(packet['rows']==[dto_record(item) for item in before.rows],
            'RESOURCE_ACTUAL_COMMITTED_LAUNCH_INTENT_CHANGED')
        directory=Path(self.lease.spec['paths']['runtime'])/'resource-supervisor'
        private(directory,directory=True);endpoint=directory/reservation.hex()
        require(not os.path.lexists(endpoint),'RESOURCE_RETAINED_SUPERVISOR_ENDPOINT_EXISTS')
        listener=socket.socket(socket.AF_UNIX,socket.SOCK_SEQPACKET|socket.SOCK_CLOEXEC)
        slot=None
        try:
            listener.bind(str(endpoint));os.chmod(endpoint,0o600);listener.listen()
            listener.settimeout(control.remaining())
            ticket=digest(canonical({'reservation':dto_record(row),
                'request':control.request.observation(),'launch_head':self.journal.head}))
            helper_arguments=[self.cfg['helper'],str(endpoint),ticket,
                str(self.cfg['workload_uid']),str(self.cfg['workload_gid']),plan['cwd']]
            for name,value in sorted(plan['environment'].items()):
                helper_arguments.extend(('--env',name,value))
            helper_arguments.extend(('--',*plan['argv']))
            payload={'ticket':ticket,'endpoint':str(endpoint),'row':dto_record(row),
                'plan':plan,'launch_intent_packet':packet,'helper_arguments':helper_arguments}
            if join is not None:payload['credential_join']=join
            dispatch=self.journal.append('DISPATCH_INTENT',reservation.hex(),payload)
            slot=OwnedSupervisor(self,row,dispatch,listener);self.slots[reservation.hex()]=slot
            args=[self.cfg['systemd_run'],'--system','--no-block','--unit='+row.planned_unit.decode('ascii'),
                '--property=Type=exec','--property=RemainAfterExit=yes','--property=Delegate=no',
                '--property=User=root','--property=Group=root',
                *(('--property='+value) for value in plan['systemd_properties']),*helper_arguments]
            launched=subprocess.run(args,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,check=False,timeout=control.remaining(),
                env={'PATH':'/usr/bin:/bin','LANG':'C'})
            control.record('actual-system-manager-dispatch',{'argv':args,
                'stdout_hex':launched.stdout.hex(),'stderr_hex':launched.stderr.hex(),
                'returncode':launched.returncode})
            require(launched.returncode==0,'RESOURCE_SYSTEM_MANAGER_DISPATCH_UNKNOWN')
            held=slot.accept_held();control.record('actual-supervisor-held',held['raw'])
            return slot,held['native_fields']
        except BaseException as exc:
            self.journal.load();phase=self.journal.rows[reservation.hex()]['phase']
            if phase in ('DISPATCH_INTENDED','NAMESPACE_HELD','GO_INTENDED','UNKNOWN'):
                self.journal.append('UNKNOWN',reservation.hex(),
                    {'refusal':str(exc),'retained_endpoint':str(endpoint)})
            if slot is None:listener.close()
            raise
    def channel_extent(self):
        # The protocol uses the actual platform pid_t/int ABI, not resource
        # quantities. Build the longest signed C-int strings without truncating
        # any quantity, epoch, binding or retained source byte.
        import ctypes
        largest=str(-(2**(ctypes.sizeof(ctypes.c_int)*8-1))).encode('ascii')
        return len(HEADER+b'CLOSED\n'+self.cfg['helper_sha256'].encode('ascii')+b'\n'+largest+b'\n'+largest+b'\nECHILD\n')
    def reserve_packet(self,intent):
        self.intact();require(type(intent) is RunRequest and intent.kind=='RESERVE' and type(intent.new_row) is RunRow,
            'RESOURCE_COMPLETE_NATIVE_RESERVE_INTENT_REQUIRED')
        before=self.current_snapshot();rows=(*before.rows,intent.new_row)
        proposed=self.propose(before,intent,rows)
        return {'schema':'worldline.protected-resource-request-v1','proposed':dto_record(proposed),
            'rows':[dto_record(row) for row in rows],'request':dto_record(intent)}
    def lifecycle_packet(self,original_request,reservation,kind,changes):
        """Complete retained proposal data; only actual native commit grants it."""
        return self._lifecycle_packet_record(original_request.observation(),reservation,kind,changes)
    def _lifecycle_packet_record(self,original_record,reservation,kind,changes):
        self.intact();before=self.current_snapshot();self.journal.load()
        retained=self.journal.rows.get(reservation.hex())
        require(retained is not None and retained['prepared']['payload']['original_request']==original_record,
            'RESOURCE_LIFECYCLE_ORIGINAL_REQUEST_CHANGED')
        selected=[row for row in before.rows if row.bound.reservation==reservation]
        require(len(selected)==1,'RESOURCE_FULL_LEDGER_MEMBERSHIP_INVALID');old=selected[0]
        require(set(changes)<={'state','planned_unit','actual_unit','cgroup','invocation'},'RESOURCE_IMMUTABLE_ROW_CHANGE_REFUSED')
        row=replace(old,**changes);rows=tuple(row if item.bound.reservation==reservation else item for item in before.rows)
        seed=canonical({'kind':kind,'before':dto_record(before.state),'row':dto_record(row),'request':original_record,
            'launch_events':retained['events']})
        request=RunRequest(kind=kind,scope=old.scope,expected_epoch=before.state.resource_epoch,
            expected_ledger_head=before.state.ledger_head,request_id=hashlib.sha256(DOMAIN+b'lifecycle-request\0'+seed).digest(),
            reservation=reservation,operation_id=old.bound.operation,requester=old.bound.owner,bound=old.bound,new_row=None)
        proposed=self.propose(before,request,rows)
        return {'schema':'worldline.protected-resource-request-v1','proposed':dto_record(proposed),
            'rows':[dto_record(item) for item in rows],'request':dto_record(request)}
    def machine_admission(self,reservation,policy,stage):
        """Genuine original machine stage under the complete retained ledger.

        The actual existing observer supplies measurements; the selected native
        ledger and admission kernels decide. Unknown usage retains the entire
        promise. No ordinary liveness filter deletes or omits an old obligation.
        OS snapshot stability, physical unit correspondence, parser/body/cost
        proofs and global scoped rollover remain required independent evidence.
        """
        from .admission import observe,ResourcePolicy
        from .resource_ledger import compute_ledger
        from .resource_policy import decide_policy
        with self.gate.mutex,self.order:
            self.intact();controller=getattr(self,'controller',None)
            require(controller is not None and controller.protected_resources is self,
                'RESOURCE_ORIGINAL_MACHINE_ADMISSION_UNAVAILABLE')
            require(type(policy) is ResourcePolicy and stage in ('DISPATCH','GO'),
                'RESOURCE_ORIGINAL_MACHINE_POLICY_REQUIRED')
            before=self.current_snapshot();scope,epoch,uhead,lhead,source=self.current_context()
            blank=self._blank(scope,epoch,uhead,lhead,before.rows[0] if before.rows else None,hashlib.sha256(canonical(source)).digest())
            blank=self._current_checked(before,blank,source)
            selected=[row for row in before.rows if row.bound.reservation==reservation]
            require(len(selected)==1,'RESOURCE_MACHINE_SELECTED_RESERVATION_ABSENT')
            actual=observe({'state':controller.paths.state,'share':controller.paths.data})
            require(actual.state=='OBSERVED','RESOURCE_ORIGINAL_MACHINE_OBSERVATION_UNKNOWN')
            floors=controller.config.admission_floors;inputs=[];details=[];outstanding=[]
            for row in before.rows:
                if row.kind!='HELD_CAPACITY' or row.state=='RELEASED':continue
                if row.bound.reservation!=reservation:outstanding.append(row)
                # Child promises remain represented and counted, while inclusive
                # parent memory accounting is charged once by the native ledger.
                if row.parent is not None:continue
                used=None;raw=None
                if row.bound.reservation!=reservation:
                    slot=self.slots.get(row.bound.reservation.hex())
                    if slot is not None:
                        try:
                            facts,physical=self._facts(row,blank,'MACHINE')
                            observed=self.kernel.classify(before.state,row,facts)
                            if observed in ('LIVE','REAPED'):
                                path=Path('/sys/fs/cgroup')/os.fsdecode(row.cgroup.removeprefix(b'/'))/'memory.current'
                                raw=kernel_bytes(path);digits=raw.removesuffix(b'\n')
                                require(digits and digits.isdigit() and b'\n' not in digits,
                                    'RESOURCE_ACTUAL_MEMORY_CURRENT_INVALID')
                                used=int(digits)
                        except (ResourceProducerRefusal,OSError):used=None
                inputs.append((row.amount,used));details.append({'row':dto_record(row),'used':lossless_data(used),
                    'memory_current':raw.hex() if raw is not None else None})
            projection=compute_ledger(tuple(inputs),core=self.core)
            disks=tuple((name,values['freeBytes'],values['freeInodes']) for name,values in actual.disk.items())
            native_input={'outstanding_count':len(outstanding),'concurrency_limit':policy.max_concurrent_workloads,
                'memory_pressure':actual.memory_pressure_hundredths,'memory_pressure_ceiling':floors.max_memory_pressure_hundredths,
                'disks':tuple((free,inodes) for _name,free,inodes in disks),'disk_byte_floor':floors.min_free_disk_bytes,
                'disk_inode_floor':floors.min_free_inodes,'available_memory':actual.mem_available_bytes,
                'withheld_memory':projection.total,'memory_floor':floors.min_free_memory_bytes,'requested_memory':0}
            # The already committed selected reservation is included in withheld
            # with independent absent usage. It is never added a second time.
            numeric=decide_policy(**native_input,core=self.core)
            record={'schema':'worldline.protected-machine-admission-v1','stage':stage,'reservation':reservation.hex(),
                'state':dto_record(before.state),'rows':[dto_record(row) for row in before.rows],
                'current':source,'measurement':lossless_data(actual.as_dict()),'policy':lossless_data(policy.canonical()),
                'floors':lossless_data({name:getattr(floors,name) for name in floors.__dataclass_fields__}),
                'ledger_input':lossless_data(tuple(inputs)),'ledger_details':details,
                'ledger_result':lossless_data({'total':projection.total,'withheld':projection.withheld}),
                'disk_roster':lossless_data(disks),'native_input':lossless_data(native_input),
                'native_output':{'gate':numeric.gate,'disk_index':numeric.disk_index}}
            self.journal.append('MACHINE_ADMISSION',reservation.hex(),record)
            require(numeric.ready,'RESOURCE_ORIGINAL_MACHINE_FLOOR_REFUSED')
            require(before==self.current_snapshot(),'RESOURCE_MACHINE_LEDGER_CHANGED_BEFORE_EFFECT')
            return record
    def launch_reserved(self,pending,original_request,reservation):
        """Whole native LaunchIntent/Running and durable GO before actor exec."""
        with self.gate.mutex,self.order:
            self.intact();require(self.operation_principal is not None,'RESOURCE_ACTUAL_OPERATION_LAUNCH_UNAVAILABLE')
            self.journal.load();retained=self.journal.rows.get(reservation.hex())
            require(retained is not None and retained['phase']=='NEVER_DISPATCHED' and reservation.hex() not in self.slots,
                'RESOURCE_LAUNCH_REPLAY_OR_UNKNOWN')
            plan=self.operation_principal.resource_launch_material(original_request,reservation)
            require(type(plan) is dict and set(plan)=={'bound','argv','cwd','environment','systemd_properties','policy','executables'},
                'RESOURCE_AUTHENTIC_OPERATION_LAUNCH_PLAN_UNAVAILABLE')
            before=self.current_snapshot();selected=[row for row in before.rows if row.bound.reservation==reservation]
            require(len(selected)==1 and selected[0].state=='RESERVED' and plan['bound']==dto_record(selected[0].bound),
                'RESOURCE_NATIVE_RESERVATION_REQUIRED_BEFORE_LAUNCH')
            old=selected[0]
            join=self.credential_join(original_request)
            if join is not None:
                require(retained['prepared']['payload'].get('credential_join')==join,
                    'RESOURCE_ACTUAL_REQUESTER_WORKLOAD_JOIN_CHANGED_BEFORE_LAUNCH')
            require(old.parent is None,'RESOURCE_PARENT_NAMESPACE_LAUNCH_ROUTING_UNAVAILABLE')
            require(type(plan['argv']) is list and plan['argv'] and all(type(word) is str and '\0' not in word for word in plan['argv'])
                and type(plan['cwd']) is str and Path(plan['cwd']).is_absolute() and type(plan['environment']) is dict,
                'RESOURCE_LAUNCH_PLAN_ENCODING_INVALID')
            require(type(plan['systemd_properties']) is list and all(type(word) is str and word and '\0' not in word for word in plan['systemd_properties'])
                and type(plan['policy']) is dict and type(plan['executables']) is dict,'RESOURCE_COMPLETE_ENFORCED_POLICY_UNAVAILABLE')
            from .admission import ResourcePolicy
            policy=ResourcePolicy.from_mapping(plan['policy'])
            require(policy.enforcement=='cgroup2' and plan['systemd_properties']==policy.unit_properties(),
                'RESOURCE_ORIGINAL_ENFORCED_POLICY_CHANGED')
            sandbox=Path(self.lease.spec['runtime']['tools']['bwrap'])
            require(plan['argv'][0]==str(sandbox) and sandbox in self.lease.allowed
                and plan['executables'].get(str(sandbox))==digest(private(sandbox)),
                'RESOURCE_ACTUAL_SANDBOX_EXECUTABLE_UNAVAILABLE')
            for name,value in plan['environment'].items():
                require(type(name) is str and type(value) is str and name and name.replace('_','a').isalnum()
                    and not name[0].isdigit() and '\0' not in value,'RESOURCE_WORKLOAD_ENVIRONMENT_INVALID')
            self.machine_admission(reservation,policy,'DISPATCH')
            unit=b'worldline-resource-'+reservation.hex().encode('ascii')+b'.service'
            packet=self.lifecycle_packet(original_request,reservation,'RECORD_LAUNCH_INTENT',{'state':'LAUNCH_INTENT','planned_unit':unit})
            self.submit_bound(pending,packet,original_request)
            after=self.current_snapshot();row=[item for item in after.rows if item.bound.reservation==reservation][0]
            directory=Path(self.lease.spec['paths']['runtime'])/'resource-supervisor';private(directory,directory=True)
            endpoint=directory/reservation.hex();require(not os.path.lexists(endpoint),'RESOURCE_RETAINED_SUPERVISOR_ENDPOINT_EXISTS')
            listener=socket.socket(socket.AF_UNIX,socket.SOCK_SEQPACKET|socket.SOCK_CLOEXEC)
            try:
                listener.bind(str(endpoint));os.chmod(endpoint,0o600);listener.listen()
                ticket=digest(canonical({'reservation':dto_record(row),'request':original_request.observation(),'launch_head':self.journal.head}))
                helper_arguments=[self.cfg['helper'],str(endpoint),ticket,str(self.cfg['workload_uid']),str(self.cfg['workload_gid']),plan['cwd']]
                for name,value in sorted(plan['environment'].items()):helper_arguments.extend(('--env',name,value))
                helper_arguments.extend(('--',*plan['argv']))
                payload={'ticket':ticket,'endpoint':str(endpoint),'row':dto_record(row),'plan':plan,'launch_intent_packet':packet,
                    'helper_arguments':helper_arguments}
                if join is not None:payload['credential_join']=join
                dispatch=self.journal.append('DISPATCH_INTENT',reservation.hex(),payload)
                slot=OwnedSupervisor(self,row,dispatch,listener);self.slots[reservation.hex()]=slot
                args=[self.cfg['systemd_run'],'--system','--no-block','--unit='+unit.decode('ascii'),
                    '--property=Type=exec','--property=RemainAfterExit=yes','--property=Delegate=no','--property=User=root',
                    '--property=Group=root',*(('--property='+value) for value in plan['systemd_properties']),*helper_arguments]
                launched=subprocess.run(args,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False,
                    env={'PATH':'/usr/bin:/bin','LANG':'C'})
                require(launched.returncode==0,'RESOURCE_SYSTEM_MANAGER_DISPATCH_UNKNOWN')
                held=slot.accept_held();native=held['native_fields']
                packet=self.lifecycle_packet(original_request,reservation,'RECORD_RUNNING',{'state':'RUNNING',
                    'actual_unit':native['actual_unit'],'cgroup':native['cgroup'],'invocation':native['invocation']})
                self.submit_bound(pending,packet,original_request);slot.go();return slot
            except BaseException as exc:
                self.journal.load();phase=self.journal.rows[reservation.hex()]['phase']
                if phase in ('DISPATCH_INTENDED','NAMESPACE_HELD','GO_INTENDED','UNKNOWN'):
                    self.journal.append('UNKNOWN',reservation.hex(),{'refusal':str(exc),'retained_endpoint':str(endpoint)})
                # Preserve endpoint, dispatch and capacity. No second launch or
                # release is inferred from an exception, EOF or launcher wait.
                raise
    def settle_bound(self,pending,original_request,reservation):
        with self.gate.mutex,self.order:
            self.intact();before=self.current_snapshot();selected=[row for row in before.rows if row.bound.reservation==reservation]
            require(len(selected)==1,'RESOURCE_FULL_SETTLEMENT_MEMBERSHIP_INVALID');row=selected[0]
            if row.state in ('RELEASED','CHARGED'):
                return self.operation_principal.resource_committed_settlement(pending,original_request,reservation)
            scope,epoch,uhead,lhead,source=self.current_context()
            blank=self._blank(scope,epoch,uhead,lhead,row,hashlib.sha256(canonical(source)).digest())
            physical,_raw=self._facts(row,blank,'SETTLEMENT');kind=self.kernel.classify(before.state,row,physical)
            if kind=='REAPED':
                if row.state!='TERMINAL':
                    packet=self.lifecycle_packet(original_request,reservation,'RECORD_TERMINAL',{'state':'TERMINAL'})
                    self.submit_bound(pending,packet,original_request)
                action='RELEASE_HOLD' if row.kind=='HELD_CAPACITY' else 'CHARGE_BUDGET'
                packet=self.lifecycle_packet(original_request,reservation,action,{'state':'RELEASED' if row.kind=='HELD_CAPACITY' else 'CHARGED'})
                return self.submit_bound(pending,packet,original_request)
            if kind=='NEVER_LAUNCHED' and row.kind=='HELD_CAPACITY':
                packet=self.lifecycle_packet(original_request,reservation,'RELEASE_HOLD',{'state':'RELEASED'})
                return self.submit_bound(pending,packet,original_request)
            if kind=='UNKNOWN' and row.state in ('LAUNCH_INTENT','RUNNING','TERMINATING','SETTLEMENT_UNKNOWN'):
                packet=self.lifecycle_packet(original_request,reservation,'RETAIN_UNCERTAIN',{'state':'SETTLEMENT_UNKNOWN'})
                return self.submit_bound(pending,packet,original_request)
            raise ResourceProducerRefusal('RESOURCE_CAPACITY_RETAINED_LIVE_OR_UNKNOWN')
    def settle_historical(self,principal,operation,reservation):
        """Original authenticated aftereffect history; no fresh socket or grant.

        A lost owned descriptor remains UNKNOWN. The current V4 kernel cannot
        authorize changed-context history; its required successor is explicit.
        No terminal classification is inferred from a historical receipt alone.
        """
        with self.gate.mutex,self.order:
            self.intact();require(principal is self.operation_principal and principal.startup_lease is self.lease
                and principal.gate is self.gate,'RESOURCE_ACTUAL_HISTORICAL_PRINCIPAL_REQUIRED')
            operation=operation_bytes(operation);reservation=operation_bytes(reservation)
            captured=principal.resource_historical_settlement(operation,reservation)
            require(type(captured) is dict and {'original_request','scope','bound','native_use','event_id','effects','receipts','causal','resource_packets'}<=set(captured),
                'RESOURCE_COMPLETE_AUTHENTIC_AFTEREFFECT_HISTORY_UNAVAILABLE')
            self.journal.load();retained=self.journal.rows.get(reservation.hex())
            require(retained is not None and retained['prepared']['payload']['original_request']==captured['original_request'],
                'RESOURCE_HISTORICAL_ORIGINAL_REQUEST_CHANGED')
            before=self.current_snapshot();selected=[row for row in before.rows if row.bound.reservation==reservation]
            require(len(selected)==1 and selected[0].bound.operation==operation and captured['scope']==dto_record(selected[0].scope)
                and captured['bound']==dto_record(selected[0].bound),'RESOURCE_HISTORICAL_FULL_BINDING_CHANGED')
            row=selected[0]
            if row.state in ('RELEASED','CHARGED'):
                require(type(captured['resource_packets']) is list and captured['resource_packets'],'RESOURCE_COMMITTED_SETTLEMENT_HISTORY_UNAVAILABLE')
                packet=captured['resource_packets'][-1];_state,_rows,request=self.service._decode_packet(packet)
                require(request.reservation==reservation and request.operation_id==operation and request.bound==row.bound
                    and request.kind in ('RELEASE_HOLD','CHARGE_BUDGET'),'RESOURCE_EXACT_COMMITTED_SETTLEMENT_CHANGED')
                answer=self.service.recover(packet,os.geteuid());require(answer.get('status')!='NOT_COMMITTED','RESOURCE_COMMITTED_SETTLEMENT_NOT_FOUND')
                return answer
            scope,epoch,uhead,lhead,source=self.current_context()
            blank=self._blank(scope,epoch,uhead,lhead,row,hashlib.sha256(canonical(source)).digest())
            facts,_raw=self._facts(row,blank,'HISTORICAL_SETTLEMENT');kind=self.kernel.classify(before.state,row,facts)
            def commit(action,changes):
                packet=self._lifecycle_packet_record(captured['original_request'],reservation,action,changes)
                _state,_rows,request=self.service._decode_packet(packet)
                self.journal.load();events=self.journal.rows[reservation.hex()]['events']
                binding=principal.resource_historical_lifecycle_binding(operation,reservation,request,events)
                require(type(binding) is dict and {'scope','bound','request','native_use','event_id'}<=set(binding)
                    and binding['scope']==dto_record(request.scope) and binding['bound']==dto_record(request.bound)
                    and binding['request']==dto_record(request),'RESOURCE_HISTORICAL_NATIVE_LIFECYCLE_BINDING_CHANGED')
                return self.service.mutate(packet,os.geteuid())
            if kind=='REAPED':
                if row.state!='TERMINAL':commit('RECORD_TERMINAL',{'state':'TERMINAL'})
                return commit('RELEASE_HOLD' if row.kind=='HELD_CAPACITY' else 'CHARGE_BUDGET',
                    {'state':'RELEASED' if row.kind=='HELD_CAPACITY' else 'CHARGED'})
            if kind=='NEVER_LAUNCHED' and row.kind=='HELD_CAPACITY':return commit('RELEASE_HOLD',{'state':'RELEASED'})
            if kind=='UNKNOWN' and row.state in ('LAUNCH_INTENT','RUNNING','TERMINATING','SETTLEMENT_UNKNOWN'):
                return commit('RETAIN_UNCERTAIN',{'state':'SETTLEMENT_UNKNOWN'})
            raise ResourceProducerRefusal('RESOURCE_HISTORICAL_CAPACITY_RETAINED_LIVE_OR_UNKNOWN')
    def close(self):
        with self.order:
            for slot in self.slots.values():slot.close()
            self.journal.db.close()
            self.poisoned=True
    def propose(self,before,request,rows):
        """Lossless proposal, never a Python permission result; native rechecks it."""
        held=charged=0
        for row in rows:
            if row.parent is None and row.state!='RELEASED':
                amount=row.amount
                if row.kind=='HELD_CAPACITY' and row.observed_usage is not None:amount=max(amount,row.observed_usage)
                if row.kind=='HELD_CAPACITY':held+=amount
                else:charged+=amount
        epoch=before.state.resource_epoch+1
        new_head=hashlib.sha256(DOMAIN+b'ledger-head\0'+canonical({'before':dto_record(before.state),
            'request':dto_record(request),'rows':[dto_record(row) for row in rows]})).digest()
        return replace(before.state,resource_epoch=epoch,ledger_head=new_head,held_total=held,charged_total=charged)
    def reconcile(self,controller):
        """Whole protected membership inspection before any Controller effect.

        This first source component never releases unknown/restored descriptors.
        Fresh scope rollover and authentic after-restart closure are explicit
        required successors. Historical selected-row reconcile stays untouched.
        """
        self.intact();before=self.current_snapshot();scope,epoch,uhead,lhead,source=self.current_context()
        blank=self._blank(scope,epoch,uhead,lhead,before.rows[0] if before.rows else None,hashlib.sha256(canonical(source)).digest())
        blank=self._current_checked(before,blank,source)
        self.journal.load();observations=[]
        for row in before.rows:
            facts,raw=self._facts(row,blank,'STARTUP')
            observations.append({'row':dto_record(row),'facts':facts_record(facts),'native':self.kernel.classify(before.state,row,facts),'source':raw})
        self.controller=controller
        controller.protected_resources=self
        # The ordinary local ledger remains a historical API. It cannot be used
        # for protected admissions until genuine all-operation routing binds the
        # exact operation principal and the original machine/floor conjunction.
        controller.admission=ProtectedAdmission(self,controller.admission)
        self.startup_observation={'schema':'worldline.protected-resource-startup-v1','state':dto_record(before.state),
            'rows':observations,'current':source,'released':[]}
        return []

class ProtectedAdmission:
    def __init__(self,principal,historical):self.principal,self.historical=principal,historical
    def admit(self,*args,**kwargs):
        self.principal.intact()
        if self.principal.operation_principal is None:raise ResourceProducerRefusal('RESOURCE_ALL_OPERATION_ADMISSION_UNAVAILABLE')
        return self.principal.operation_principal.admit_resource(self.principal,*args,**kwargs)
    def release(self,*args,**kwargs):
        self.principal.intact()
        if self.principal.operation_principal is None:raise ResourceProducerRefusal('RESOURCE_HISTORICAL_RELEASE_BINDING_UNAVAILABLE')
        return self.principal.operation_principal.settle_resource(self.principal,*args,**kwargs)
    def attach_unit(self,*args,**kwargs):
        raise ResourceProducerRefusal('RESOURCE_PROTECTED_SUPERVISOR_REQUIRED')
    def attach_process_identity(self,*args,**kwargs):
        raise ResourceProducerRefusal('RESOURCE_ORDINARY_PROCESS_IS_NOT_PROTECTED_AUTHORITY')
    def snapshot(self,*args,**kwargs):
        self.principal.intact();return self.principal.startup_observation
    def reconcile(self,*args,**kwargs):
        raise ResourceProducerRefusal('RESOURCE_RECONCILE_REQUIRES_PRECONSTRUCTION_LEASE')

def attach_resource(lease,gate,store,core):
    require(getattr(lease,'resource_principal',None) is None,'RESOURCE_STARTUP_ALREADY_ATTACHED')
    principal=ProtectedResourcePrincipal(lease,gate,store,core);lease.resource_principal=principal;return principal

class OwnedSupervisor:
    """A real kernel channel/namespace/pidfd owner, never a reconstructed DTO."""
    def __init__(self,principal,row,dispatch,listener):
        self.principal,self.row,self.dispatch,self.listener=principal,row,dispatch,listener
        self.connection=None;self.namespace_fd=None;self.namespace_pidfd=None;self.helper_pidfd=None
        self.stdout_fd=None;self.stderr_fd=None;self.stdout=None;self.stderr=None;self.pipe_transports=[]
        self.held=None;self.closed=None;self.closed_event=None;self.started=False;self.failed=False
    def manager(self):
        p=self.principal
        names=('Id','MainPID','InvocationID','ControlGroup','Delegate','ActiveState','SubState')
        answer=subprocess.run([p.cfg['systemctl'],'--system','show',self.row.planned_unit.decode('ascii'),
            '--no-pager',*(('--property='+name) for name in names)],stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False,env={'PATH':'/usr/bin:/bin','LANG':'C'})
        require(answer.returncode==0,'RESOURCE_ACTUAL_MANAGER_OBSERVATION_UNAVAILABLE')
        parts=answer.stdout.splitlines();parsed={}
        for raw in parts:
            name,separator,value=raw.partition(b'=');require(separator and name.decode('ascii') in names
                and name not in parsed,'RESOURCE_MANAGER_PROPERTY_INVALID');parsed[name]=value
        require(set(parsed)=={name.encode('ascii') for name in names}
            and parsed[b'Id']==self.row.planned_unit,'RESOURCE_MANAGER_UNIT_CHANGED')
        return parsed,{'stdout':answer.stdout.hex(),'stderr':answer.stderr.hex(),'returncode':answer.returncode}
    @staticmethod
    def number(raw):
        require(raw and raw.isdigit() and str(int(raw)).encode('ascii')==raw,'RESOURCE_KERNEL_DECIMAL_INVALID')
        return int(raw)
    @staticmethod
    def pidfd_state(fd):
        poll=select.poll();poll.register(fd,select.POLLIN|select.POLLHUP|select.POLLERR)
        events=poll.poll(0)
        require(not any(mask&select.POLLERR for _fd,mask in events),'RESOURCE_PIDFD_STATUS_UNKNOWN')
        return b'PIDFD_TERMINAL' if events else b'PIDFD_LIVE'
    @staticmethod
    def fd_pid(fd):
        raw=kernel_bytes('/proc/self/fdinfo/'+str(fd));matches=[line.removeprefix(b'Pid:\t') for line in raw.splitlines() if line.startswith(b'Pid:\t')]
        require(len(matches)==1,'RESOURCE_ACTUAL_PIDFD_UNAVAILABLE');return OwnedSupervisor.number(matches[0]),raw
    def accept_held(self):
        p=self.principal;p.intact();connection,_address=self.listener.accept()
        self.connection=connection
        raw_peer=connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,struct.calcsize('@iII'))
        helper_pid,uid,gid=struct.unpack('@iII',raw_peer)
        require(helper_pid>0 and uid==0,'RESOURCE_SUPERVISOR_KERNEL_PEER_REFUSED')
        body,control,flags,_address=connection.recvmsg(p.channel_extent(),socket.CMSG_SPACE(array.array('i').itemsize*4),socket.MSG_CMSG_CLOEXEC)
        owned=[]
        try:
            require(not flags&(socket.MSG_TRUNC|socket.MSG_CTRUNC),'RESOURCE_SUPERVISOR_FRAME_TRUNCATED')
            for level,kind,raw in control:
                require(level==socket.SOL_SOCKET and kind==socket.SCM_RIGHTS,'RESOURCE_SUPERVISOR_CONTROL_UNKNOWN')
                rights=array.array('i');require(len(raw)%rights.itemsize==0,'RESOURCE_SUPERVISOR_RIGHTS_INVALID');rights.frombytes(raw);owned.extend(rights)
            require(len(owned)==4,'RESOURCE_SUPERVISOR_DESCRIPTOR_ROSTER_INVALID')
            parts=body.split(b'\n')
            require(len(parts)==5 and parts[:2]==[HEADER.removesuffix(b'\n'),b'HELD'] and parts[2]==self.dispatch['payload']['ticket'].encode('ascii')
                and parts[-1]==b'','RESOURCE_SUPERVISOR_HELD_FRAME_INVALID')
            init_pid=self.number(parts[3]);require(init_pid>0,'RESOURCE_SUPERVISOR_INIT_PID_INVALID')
            ns,pidfd,out,err=owned;self.namespace_fd,self.namespace_pidfd=ns,pidfd
            self.stdout_fd,self.stderr_fd=out,err;owned=[]
            require(stat.S_ISFIFO(os.fstat(out).st_mode) and stat.S_ISFIFO(os.fstat(err).st_mode),
                'RESOURCE_SUPERVISOR_ACTUAL_OUTPUT_PIPE_REQUIRED')
            actual_pid,raw_fd=self.fd_pid(pidfd);require(actual_pid==init_pid,'RESOURCE_SUPERVISOR_PIDFD_BINDING_CHANGED')
            actual_ns=os.open('/proc/'+str(init_pid)+'/ns/pid',os.O_RDONLY|os.O_CLOEXEC)
            try:require(identity_record(os.fstat(ns))==identity_record(os.fstat(actual_ns)),'RESOURCE_SUPERVISOR_NAMESPACE_BINDING_CHANGED')
            finally:os.close(actual_ns)
            self.helper_pidfd=os.pidfd_open(helper_pid,0)
            helper_again,helper_fd=self.fd_pid(self.helper_pidfd);require(helper_again==helper_pid,'RESOURCE_SUPERVISOR_PEER_PIDFD_CHANGED')
            properties,manager=self.manager()
            require(self.number(properties[b'MainPID'])==helper_pid and properties[b'InvocationID']
                and properties[b'ControlGroup'].startswith(b'/'),'RESOURCE_MANAGER_HELPER_BINDING_CHANGED')
            image=Path(os.readlink('/proc/'+str(helper_pid)+'/exe'))
            require(image==p.helper and digest(private(image))==p.cfg['helper_sha256'],'RESOURCE_ACTUAL_SUPERVISOR_IMAGE_CHANGED')
            maps=kernel_bytes('/proc/'+str(helper_pid)+'/maps')
            for line in maps.splitlines():
                pieces=line.split(None,5)
                if len(pieces)==6 and pieces[5].startswith(b'/'):
                    mapped=Path(os.fsdecode(pieces[5]));require(mapped in p.lease.allowed,'RESOURCE_SUPERVISOR_MAPPED_RUNTIME_UNPINNED');private(mapped)
            proc_cgroup=kernel_bytes('/proc/'+str(helper_pid)+'/cgroup')
            require(proc_cgroup==b'0::'+properties[b'ControlGroup']+b'\n','RESOURCE_HELPER_CGROUP_BINDING_CHANGED')
            command_line=kernel_bytes('/proc/'+str(helper_pid)+'/cmdline')
            require(command_line==b'\0'.join(os.fsencode(word) for word in self.dispatch['payload']['helper_arguments'])+b'\0',
                'RESOURCE_ACTUAL_SUPERVISOR_COMMAND_CHANGED')
            namespace=canonical(identity_record(os.fstat(ns)));peer=raw_peer
            challenge=hashlib.sha256(canonical({'dispatch':self.dispatch,'held_frame':body.hex(),'peer':peer.hex(),
                'namespace':namespace.hex(),'manager':manager,'maps':maps.hex(),'proc_cgroup':proc_cgroup.hex()})).digest()
            self.held={'frame':body.hex(),'peer':peer.hex(),'helper_pid':helper_pid,'init_pid':init_pid,'namespace':namespace.hex(),
                'pidfd_info':raw_fd.hex(),'helper_pidfd_info':helper_fd.hex(),'manager':manager,'properties':{name.decode():value.hex() for name,value in properties.items()},
                'maps':maps.hex(),'proc_cgroup':proc_cgroup.hex(),'cmdline':command_line.hex(),'challenge':challenge.hex(),'helper_sha256':p.cfg['helper_sha256'],
                'stdout_identity':identity_record(os.fstat(out)),'stderr_identity':identity_record(os.fstat(err))}
            event=p.journal.append('HELD',self.row.bound.reservation.hex(),self.held)
            self.held_event=event;connection.setblocking(False);return self.observe()
        except BaseException:
            self.failed=True
            for fd in owned:os.close(fd)
            raise
    def poll_closed(self):
        if self.closed is not None or self.failed:return
        try:body,control,flags,_address=self.connection.recvmsg(self.principal.channel_extent(),socket.CMSG_SPACE(array.array('i').itemsize),socket.MSG_CMSG_CLOEXEC)
        except BlockingIOError:return
        owned=[]
        try:
            for level,kind,raw in control:
                if level==socket.SOL_SOCKET and kind==socket.SCM_RIGHTS:
                    rights=array.array('i');require(len(raw)%rights.itemsize==0,'RESOURCE_SUPERVISOR_RIGHTS_INVALID');rights.frombytes(raw);owned.extend(rights)
            require(body and not control and not flags&(socket.MSG_TRUNC|socket.MSG_CTRUNC),'RESOURCE_SUPERVISOR_CLOSURE_UNAVAILABLE')
            parts=body.split(b'\n')
            require(len(parts)==7 and parts[:2]==[HEADER.removesuffix(b'\n'),b'CLOSED']
                and parts[2]==self.dispatch['payload']['ticket'].encode('ascii') and self.number(parts[3])==self.held['init_pid']
                and parts[5:]==[b'ECHILD',b''],'RESOURCE_SUPERVISOR_CLOSURE_INVALID')
            status=self.number(parts[4]);require(os.WIFEXITED(status) or os.WIFSIGNALED(status),'RESOURCE_SUPERVISOR_MAIN_WAIT_INVALID')
            require(self.pidfd_state(self.namespace_pidfd)==b'PIDFD_TERMINAL','RESOURCE_SUPERVISOR_NAMESPACE_NOT_TERMINAL')
            raw_peer=self.connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,struct.calcsize('@iII'))
            require(raw_peer.hex()==self.held['peer'],'RESOURCE_SUPERVISOR_CLOSED_PEER_CHANGED')
            self.closed={'frame':body.hex(),'peer':raw_peer.hex(),'namespace':canonical(identity_record(os.fstat(self.namespace_fd))).hex(),
                'held':digest(canonical(self.held_event)),'main_wait_status':status}
            self.closed_event=self.principal.journal.append('CLOSED',self.row.bound.reservation.hex(),self.closed)
            self.connection.sendall(b'A')
        except BaseException:
            self.failed=True;raise
        finally:
            for fd in owned:os.close(fd)
    def cgroup(self,raw_path):
        require(raw_path.startswith(b'/') and b'..' not in raw_path.split(b'/') and b'\0' not in raw_path,'RESOURCE_KERNEL_CGROUP_PATH_INVALID')
        path=Path('/sys/fs/cgroup')/os.fsdecode(raw_path.removeprefix(b'/'));private(path,directory=True)
        # Every ancestor and every retained subgroup lacks an unprivileged
        # migration write. No delegated user manager is used for this launch.
        for root,directories,files in os.walk(path,followlinks=False):
            private(root,directory=True)
            for name in ('cgroup.procs','cgroup.threads','cgroup.subtree_control'):
                selected=Path(root)/name
                if selected.exists():private(selected)
        info=path.lstat();events=kernel_bytes(path/'cgroup.events');kind=kernel_bytes(path/'cgroup.type')
        return info,events,kind,{'path':str(path),'identity':identity_record(info),'events':events.hex(),'type':kind.hex()}
    def observe(self):
        p=self.principal;p.intact();require(self.held is not None and not self.failed,'RESOURCE_OWNED_SUPERVISOR_OBSERVATION_UNAVAILABLE')
        self.poll_closed();properties,manager=self.manager()
        retained=self.held['properties'];cg=bytes.fromhex(retained['ControlGroup']);inv=bytes.fromhex(retained['InvocationID'])
        require(properties[b'InvocationID']==inv and properties[b'ControlGroup']==cg,'RESOURCE_MANAGER_INVOCATION_CHANGED')
        info,events,kind,cgroup=self.cgroup(cg)
        peer=self.connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,struct.calcsize('@iII'))
        require(peer.hex()==self.held['peer'],'RESOURCE_OWNED_SUPERVISOR_PEER_CHANGED')
        namespace=canonical(identity_record(os.fstat(self.namespace_fd)))
        require(namespace.hex()==self.held['namespace'],'RESOURCE_OWNED_NAMESPACE_CHANGED')
        namespace_wait=self.pidfd_state(self.namespace_pidfd);helper_wait=self.pidfd_state(self.helper_pidfd)
        if helper_wait==b'PIDFD_LIVE':
            require(self.number(properties[b'MainPID'])==self.held['helper_pid'],'RESOURCE_MANAGER_LIVE_HELPER_CHANGED')
            actual_image=Path(os.readlink('/proc/'+str(self.held['helper_pid'])+'/exe'))
            require(actual_image==p.helper and digest(private(actual_image))==p.cfg['helper_sha256'],'RESOURCE_LIVE_SUPERVISOR_IMAGE_CHANGED')
        else:require(properties[b'MainPID']==b'0','RESOURCE_MANAGER_TERMINAL_HELPER_CHANGED')
        phase='NAMESPACE_CLOSED' if self.closed is not None else 'NAMESPACE_HELD'
        raw={'held':self.held,'closed':self.closed,'manager':manager,'cgroup':cgroup,'namespace_wait':namespace_wait.hex(),'helper_wait':helper_wait.hex()}
        native={'dispatch':bytes.fromhex(digest(canonical(self.dispatch))),'actual_unit':properties[b'Id'],'cgroup':cg,'invocation':inv,
            'namespace':namespace,'held_namespace':bytes.fromhex(self.held['namespace']),'peer':peer,'held_peer':bytes.fromhex(self.held['peer']),
            'helper_image':bytes.fromhex(p.cfg['helper_sha256']),'expected_helper_image':bytes.fromhex(p.cfg['helper_sha256']),
            'challenge':bytes.fromhex(self.held['challenge']),'held_challenge':bytes.fromhex(self.held['challenge']),
            'protocol':b'CLOSED_ECHILD' if self.closed is not None else b'HELD',
            'closed_event':bytes.fromhex(digest(canonical(self.closed_event))) if self.closed_event is not None else None,
            'namespace_wait':namespace_wait,'helper_wait':helper_wait,'cgroup_events':events,'cgroup_type':kind,'manager_delegate':properties[b'Delegate'],
            'cgroup_owner':info.st_uid,'cgroup_group_write':info.st_mode&stat.S_IWGRP,'cgroup_other_write':info.st_mode&stat.S_IWOTH,'phase':phase}
        return {'native_fields':native,'raw':raw}
    def go(self):
        p=self.principal;p.intact();require(not self.started and not self.failed and self.closed is None,'RESOURCE_SUPERVISOR_GO_REPLAY_REFUSED')
        snapshot=p.current_snapshot();rows=[row for row in snapshot.rows if row.bound.reservation==self.row.bound.reservation]
        require(len(rows)==1 and rows[0].state=='RUNNING' and rows[0].bound==self.row.bound,'RESOURCE_NATIVE_RUNNING_REQUIRED_BEFORE_GO')
        captured=self.observe();require(captured['native_fields']['namespace_wait']==b'PIDFD_LIVE'
            and captured['native_fields']['helper_wait']==b'PIDFD_LIVE','RESOURCE_SUPERVISOR_NOT_LIVE_BEFORE_GO')
        from .admission import ResourcePolicy
        machine=p.machine_admission(self.row.bound.reservation,ResourcePolicy.from_mapping(self.dispatch['payload']['plan']['policy']),'GO')
        p.journal.append('GO_INTENT',self.row.bound.reservation.hex(),{'running_state':dto_record(snapshot.state),'running_row':dto_record(rows[0]),'observation':captured['raw'],'machine_admission':machine})
        try:self.connection.sendall(b'G');self.started=True
        except BaseException:self.failed=True;raise
    async def attach_output(self):
        """Original complete actor bytes through owned real pipes, not journalctl."""
        require(self.stdout is None and self.stderr is None,'RESOURCE_OUTPUT_ALREADY_OWNED')
        loop=asyncio.get_running_loop()
        for name,fd in (('stdout',self.stdout_fd),('stderr',self.stderr_fd)):
            require(fd is not None,'RESOURCE_ACTUAL_OUTPUT_DESCRIPTOR_ABSENT')
            reader=asyncio.StreamReader();protocol=asyncio.StreamReaderProtocol(reader)
            transport,_protocol=await loop.connect_read_pipe(lambda:protocol,os.fdopen(os.dup(fd),'rb',buffering=0))
            self.pipe_transports.append(transport);setattr(self,name,reader)
        return self
    async def wait(self):
        """Waits real closure and owned helper pidfd; no launcher/EOF verdict."""
        require(self.started and not self.failed,'RESOURCE_ACTUAL_RUNNING_WAIT_REQUIRED')
        loop=asyncio.get_running_loop()
        async def readable(fd):
            future=loop.create_future()
            def ready():
                if not future.done():future.set_result(None)
            loop.add_reader(fd,ready)
            try:await future
            finally:loop.remove_reader(fd)
        while self.closed is None:
            await readable(self.connection.fileno());self.poll_closed()
        if self.pidfd_state(self.helper_pidfd)!=b'PIDFD_TERMINAL':await readable(self.helper_pidfd)
        require(self.pidfd_state(self.namespace_pidfd)==b'PIDFD_TERMINAL'
            and self.pidfd_state(self.helper_pidfd)==b'PIDFD_TERMINAL','RESOURCE_WAIT_TERMINAL_OWNERSHIP_UNKNOWN')
        return os.waitstatus_to_exitcode(self.closed['main_wait_status'])
    def close(self):
        # Closing descriptors never classifies a workload as reaped or releases
        # capacity. A helper losing its channel before GO kills its namespace
        # init; after GO closure can become unobservable. Neither emits an
        # accepted CLOSED frame, and the retained obligation stays UNKNOWN.
        for transport in self.pipe_transports:transport.close()
        for fd in (self.namespace_fd,self.namespace_pidfd,self.helper_pidfd,self.stdout_fd,self.stderr_fd):
            if fd is not None:os.close(fd)
        for channel in (self.connection,self.listener):
            if channel is not None:channel.close()
        self.failed=True
