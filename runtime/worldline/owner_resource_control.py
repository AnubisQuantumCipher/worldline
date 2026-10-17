"""Source-owned original full-resource replay factory; no simulated authority.

This is a new owner-controlled fixture producer executed today. It retains the
actual startup/Gate/issuer/Universe/resource/canonical principals throughout the
unchanged assertions. Packets are proposals formed from preceding actual native
commits and owned OS observations. The v1 compatibility case writes its intent
before its real RPC; it is not a claim of historical writer provenance.
"""
from __future__ import annotations
import asyncio
import hashlib
import json
import math
import os
from pathlib import Path
import select
import socket
import stat
import subprocess
import sys
import threading
import time
import uuid
from .protected_startup import StartupLease,canonical,exact_json,private_bytes,protected,require
from .client_peer import KernelPeer,RequestPeer,request_scope
from .resource_run_ledger import dto_record,restore_dto

SCHEMA='worldline.original-full-resource-control-factory-v1'
CASES=('SEQUENTIAL','DUPLICATE','LOST_ACK_RESTART','CONFLICT',
       'CLOSED_AFTER_COMMIT','NOT_COMMITTED','DISPATCH_UNKNOWN','LEGACY_COMMITTED')
SEQUENTIAL=('RESERVE','RECORD_LAUNCH_INTENT','RECORD_RUNNING',
            'RECORD_TERMINATING','RECORD_TERMINAL','RELEASE_HOLD')
PLAN_KEYS={'schema','case','startup_descriptor','request','peer_child_entry',
           'peer_child_envelope','result_directory','timeout','injector_timeout'}


def _source():
    module=sys.modules.get('_worldline_approved_source_loader')
    require(type(module) is type(sys),'RESOURCE_CONTROL_EARLY_SOURCE_REQUIRED')
    source=module.current()
    require(type(source) is module.ApprovedSourceLease,'RESOURCE_CONTROL_ACTUAL_SOURCE_REQUIRED')
    source.check();return source


def _error(value):
    return {'module':type(value).__module__,'type':type(value).__qualname__,
            'repr':repr(value),'message':str(value),'errno':getattr(value,'errno',None)}


def selected_plan(path, *, peer_child=False):
    source=_source();raw=source.file(str(path),('DATA',));plan=exact_json(raw)
    require(type(plan) is dict and set(plan)==PLAN_KEYS and plan['schema']==SCHEMA
        and plan['case'] in CASES,'RESOURCE_CONTROL_COMPLETE_SELECTED_PLAN_REQUIRED')
    for name,expected in (('timeout',600),('injector_timeout',120)):
        value=plan[name]
        require(type(value) in (int,float) and math.isfinite(value) and value==expected,
            'RESOURCE_CONTROL_ORIGINAL_FINITE_CAP_REQUIRED')
    descriptor=exact_json(source.file(plan['startup_descriptor'],('DATA',)))
    request_raw=source.file(plan['request'],('DATA',))
    request=exact_json(request_raw,canonical_required=False)
    require(type(request) is dict and set(request)=={'id','op','args'}
        and type(request['id']) in (str,int) and type(request['op']) is str
        and type(request['args']) is dict,'RESOURCE_CONTROL_ORIGINAL_REQUEST_REQUIRED')
    source.file(plan['peer_child_entry'],('SOURCE','ENTRY'))
    require(type(peer_child) is bool,'RESOURCE_CONTROL_EXACT_CALLER_CHILD_ROUTE_REQUIRED')
    if peer_child:
        # The original lease owns these actual bootstrap bytes. Parent retains
        # the DATA member; a child cannot recursively embed its own envelope.
        actual=source.check()
        require(plan['peer_child_envelope']==source.envelope_path
            and actual['envelope_path']==plan['peer_child_envelope']
            and actual['envelope_bytes_hex']==source.envelope.hex(),
            'RESOURCE_CONTROL_ACTUAL_HELD_CHILD_ENVELOPE_SPLIT')
    else:
        source.file(plan['peer_child_envelope'],('DATA',))
    root=Path(descriptor['paths']['authority_root'])
    require(root.parent==Path('/srv') and root.name.startswith('cosmogony-canonical-v1.'),
        'RESOURCE_CONTROL_ORIGINAL_DISPOSABLE_ROOT_REQUIRED')
    output=Path(plan['result_directory']);protected(output,directory=True)
    require(not output.stat().st_mode&0o077 and output!=root and not output.is_relative_to(root),
        'RESOURCE_CONTROL_EXTERNAL_PRIVATE_RETENTION_REQUIRED')
    source.check();return source,plan,raw,descriptor,request_raw,request


class LivePackets:
    """One traversal, original literal kinds, no materialized future packets."""
    def __init__(self,owner):self.owner=owner;self.started=False
    def kinds(self):return SEQUENTIAL
    def __iter__(self):
        require(not self.started,'RESOURCE_CONTROL_PACKET_TRAVERSAL_REPLAY_REFUSED')
        self.started=True;yield from self.owner.sequential()


class OwnerResourceControl:
    def __init__(self,path,case):
        self.plan_path=Path(path)
        (self.source_lease,self.plan,self.plan_raw,self.descriptor,
         self.request_raw,self.document)=selected_plan(self.plan_path)
        require(case==self.plan['case'],'RESOURCE_CONTROL_SELECTED_CASE_CHANGED')
        self.deadline=time.monotonic()+self.plan['timeout']
        self.lease=None;self.resources=None;self.principal=None;self.request=None
        self.child=None;self.child_pidfd=None;self.peer_connection=None;self.peer_listener=None
        self.server=None;self.server_thread=None;self.server_socket_identity=None;self.server_state=None
        self.peer_socket_identity=None;self.output=Path(self.plan['result_directory'])
        self.events=[];self.packet_records=[];self.captures={};self.responses={}
        self.reserve_result=None;self.slot=None;self.drains=[];self.drop_ack_packet=None
        self.closed=False;self.close_attempted=False;self.request_scope=None;self.operation=None
        self.requester_transport=None;self.requester_actor=None;self.requester_actor_pidfd=None
        self.peer_raw_files=[];self.operational_dispatch=None;self.rpc_threads={}
        self.rpc_lock=threading.Lock();self.record_lock=threading.Lock()
        fd=os.open(self.output/'resource-control-events.jsonl',
            os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
        self.event_file=os.fdopen(fd,'wb',buffering=0)
        try:
            self.record('selected-owner-inputs',{'plan_hex':self.plan_raw.hex(),
                'plan_sha256':hashlib.sha256(self.plan_raw).hexdigest(),
                'request_hex':self.request_raw.hex(),'source':self.source_lease.check()})
        except BaseException as primary:
            try:self.event_file.close()
            except BaseException as secondary:primary.add_note('Actual event-file close: '+repr(secondary))
            raise
    def remaining(self):
        left=self.deadline-time.monotonic()
        require(left>0,'RESOURCE_CONTROL_ORIGINAL_CASE_DEADLINE')
        return left
    def record(self,cause,value):
        event={'cause':cause,'value':value,'monotonic':time.monotonic()}
        raw=canonical(event)+b'\n'
        with self.record_lock:
            self.event_file.write(raw);os.fsync(self.event_file.fileno())
            self.events.append(event)
    def validate_startup_descriptor(self,path):
        require(str(Path(path))==self.plan['startup_descriptor']
            and self.source_lease.file(self.plan['startup_descriptor'],('DATA',))
               ==private_bytes(path),'RESOURCE_CONTROL_ACTUAL_STARTUP_SELECTION_REQUIRED')
    def intact(self):
        require(not self.closed,'RESOURCE_CONTROL_CLOSED')
        self.source_lease.check()
        require(self.source_lease.file(str(self.plan_path),('DATA',))==self.plan_raw
            and self.source_lease.file(self.plan['request'],('DATA',))==self.request_raw,
            'RESOURCE_CONTROL_SELECTED_INPUT_CHANGED')
        if self.lease is not None:self.lease.intact()
        if self.request is not None:self.request.observation()
    def attach(self,lease):
        require(type(lease) is StartupLease and lease.full_resource_control is self,
            'RESOURCE_CONTROL_ACTUAL_LEASE_REQUIRED')
        self.lease=lease;self.resources=lease.resource_principal
        self.principal=lease.canonical_operation_principal
        require(self.resources.lease is lease and self.principal.resources is self.resources
            and self.principal.gate is lease.gate,'RESOURCE_CONTROL_ACTUAL_OWNER_JOIN_REQUIRED')
    def selected_gate(self,lease):
        require(type(lease) is StartupLease,'RESOURCE_CONTROL_ACTUAL_GATE_LEASE_REQUIRED')
        gate_source=lease.spec['runtime']['gate_source']
        self.source_lease.file(gate_source,('SOURCE',))
        for directory in reversed((str(Path(gate_source).parent),*(lease.shared_import_roots if lease.shared_source is not None else ()))):
            self.source_lease.directory_or_absent(directory)
            if directory not in sys.path:sys.path.insert(0,directory)
        self.source_lease.check()
        import intent_gate
        require(Path(intent_gate.__file__)==Path(gate_source),
            'RESOURCE_CONTROL_ACTUAL_SELECTED_GATE_SOURCE_SPLIT')
        return intent_gate
    def requester_selection(self):
        return self.requester_selection_data(self.source_lease,self.plan,self.plan_path,
            self.descriptor,self.request_raw,self.output)
    @staticmethod
    def requester_selection_data(source_lease,plan,plan_path,descriptor,request_raw,output):
        original=Path(descriptor['runtime']['worldline_source'])/'protected-root/controls/original_client.py'
        resource=Path(descriptor['runtime']['worldline_source'])/'protected-resource/controls/owner_full_resource_control_entry.py'
        if Path(plan['peer_child_entry']) not in (original,resource):return None
        path=str(plan_path)+'.requester.json'
        raw=source_lease.file(path,('DATA',));record=exact_json(raw)
        endpoint=descriptor['endpoint']
        require(type(record) is dict and set(record)=={'schema','uid','gid','groups','endpoint','requests','timeout','disconnect'}
            and record['schema']=='worldline.original-custody-client-v1'
            and record['uid']==endpoint['requester_uid'] and record['gid']==endpoint['requester_gid']
            and record['groups']==[] and record['endpoint']==endpoint['path']
            and record['requests']==[plan['request']] and record['timeout']==plan['timeout']
            and record['disconnect']=='never','RESOURCE_CONTROL_EXACT_ORIGINAL_CLIENT_SELECTION_REQUIRED')
        require(request_raw.endswith(b'\n') and request_raw.count(b'\n')==1,
            'RESOURCE_CONTROL_COMPLETE_ORIGINAL_CLIENT_LINE_REQUIRED')
        owner_path=path+'.source-owner.json'
        owner_raw=source_lease.file(owner_path,('DATA',));owner=exact_json(owner_raw)
        require(type(owner) is dict and set(owner)=={'schema','request','entry','descriptor','import_roots',
                'actor_closure','retention_directory','timeout'}
            and owner['schema']=='worldline.fixed-original-client-source-owner-v1'
            and owner['request']==path and owner['entry']==str(original)
            and owner['descriptor']==plan['startup_descriptor']
            and owner['import_roots']==[str(original.parents[2]/'runtime')]
            and owner['timeout']==plan['timeout'],
            'RESOURCE_CONTROL_FIXED_NATIVE_SOURCE_OWNER_SELECTION_REQUIRED')
        retention=Path(owner['retention_directory']);protected(retention,directory=True)
        require(not retention.stat().st_mode&0o077 and retention.is_relative_to(output)
            and not os.path.lexists(retention/'source-owner.archive'),
            'RESOURCE_CONTROL_FRESH_PRIVATE_SOURCE_OWNER_RETENTION_REQUIRED')
        return {'entry':str(original),'path':path,'raw':raw,'record':record,'owner_path':owner_path,
            'owner_raw':owner_raw,'owner':owner,'archive':str(retention/'source-owner.archive')}
    def retained_source_owner_rows(self):
        from .root_worker_codec import restore_archive
        selection=self.requester_transport;path=Path(selection['archive'])
        raw=private_bytes(path)
        self.record('actual-source-owner-archive-read-before-parse',{'path':str(path),'raw_hex':raw.hex()})
        rows=[];position=0
        while position<len(raw):
            end=raw.find(b'\n',position)
            if end<0:break
            word=raw[position:end]
            require(word and word.isdigit() and str(int(word)).encode('ascii')==word,
                'RESOURCE_CONTROL_SOURCE_OWNER_ARCHIVE_EXTENT_REQUIRED')
            size=int(word);require(size>0,'RESOURCE_CONTROL_SOURCE_OWNER_ARCHIVE_PROGRESS_REQUIRED')
            start=end+1
            if size>len(raw)-start:break
            value=restore_archive(raw[start:start+size])
            require(type(value) is dict and set(value)=={'kind','value'},
                'RESOURCE_CONTROL_COMPLETE_SOURCE_OWNER_ARCHIVE_ROW_REQUIRED')
            rows.append(value);position=start+size
        self.record('actual-source-owner-framing-readback',{'complete_extent':position,
            'partial_tail_hex':raw[position:].hex(),'row_kinds':[row['kind'] for row in rows]})
        return rows
    def source_owner_native_frame(self,phase,action):
        import ctypes as C
        from .root_worker_codec import restore_archive
        rows=self.retained_source_owner_rows();selected=[]
        for row in rows:
            value=row['value']
            if (row['kind']=='NATIVE_RESULT' and type(value) is dict
                    and value.get('phase')==phase and value.get('transport')==0
                    and value.get('action')==action):selected.append(value)
        require(selected,'RESOURCE_CONTROL_ACTUAL_SOURCE_OWNER_NATIVE_PHASE_REQUIRED')
        value=selected[-1];raw=value['raw'];frame=restore_archive(raw)
        require(type(frame) is dict and frame['phase']==phase
            and frame['owner']['pid']==self.child.pid
            and frame['plan_raw']==self.requester_transport['owner_raw']
            and frame['request_raw']==self.requester_transport['raw']
            and frame['descriptor_raw']==self.source_lease.file(self.plan['startup_descriptor'],('DATA',))
            and frame['plan']['entry']==self.requester_transport['entry'],
            'RESOURCE_CONTROL_ACTUAL_SOURCE_OWNER_FRAME_JOIN_REQUIRED')
        library_path=self.descriptor['runtime']['native_library']
        self.source_lease.file(library_path,(self.source_lease.files[library_path][0],))
        library=C.CDLL(library_path,use_errno=True)
        native=library.wl_excluded_source_owner_decide_v1
        native.argtypes=[C.c_void_p,C.c_size_t,C.POINTER(C.c_uint64)];native.restype=C.c_int
        operand=(C.c_ubyte*len(raw)).from_buffer_copy(raw);status=C.c_uint64()
        self.record('actual-source-owner-native-redecision-start',{'phase':phase,
            'raw_hex':raw.hex(),'library':library_path,'source':self.source_lease.check()})
        code=native(operand,len(raw),C.byref(status))
        self.record('actual-source-owner-native-redecision-result',{'phase':phase,
            'raw_hex':raw.hex(),'transport':code,'action':status.value,'source':self.source_lease.check()})
        require(code==0 and status.value==action,'RESOURCE_CONTROL_NATIVE_SOURCE_OWNER_REDECISION_REFUSED')
        return frame
    def join_requester_actor(self,observed):
        module=sys.modules['_worldline_approved_source_loader']
        frame=self.source_owner_native_frame('ACQUIRE',2)
        actual=module.process_facts(observed['pid']);owner=module.process_facts(self.child.pid)
        self.record('actual-connected-actor-and-root-owner',{'peer':observed,'actor':actual,
            'owner':owner,'source_owner_frame_hex':__import__('worldline.root_worker_codec',fromlist=['archive']).archive(frame).hex()})
        require(frame['child_pid']==observed['pid'] and observed['pid']!=self.child.pid
            and frame['owner']['start_tick']==owner['start_tick']
            and frame['owner']['boot_hex']==owner['boot_hex']
            and frame['target'] is not None and frame['target']['close']['result']==0,
            'RESOURCE_CONTROL_ACTUAL_NESTED_ACTOR_NATIVE_JOIN_REQUIRED')
        matching=[row for row in frame['messages'] if row['kernel']['pid']==observed['pid']
            and row['kernel']['start_tick']==actual['start_tick']
            and row['kernel']['boot_hex']==actual['boot_hex']]
        require(matching and actual['real_uid']==observed['uid'] and actual['real_gid']==observed['gid'],
            'RESOURCE_CONTROL_ACTUAL_CONNECTED_ACTOR_BIRTH_REQUIRED')
        self.requester_actor=actual
        self.requester_actor_pidfd=os.pidfd_open(observed['pid'])
        self.record('actual-connected-actor-pidfd',{'pid':observed['pid'],
            'fd':self.requester_actor_pidfd,'actor':module.process_facts(observed['pid'])})
        require(module.process_facts(observed['pid'])['start_tick']==actual['start_tick'],
            'RESOURCE_CONTROL_ACTOR_CHANGED_DURING_PIDFD_ACQUISITION')
    def complete_requester_owner(self):
        require(self.child.returncode==0,'RESOURCE_CONTROL_ACTUAL_SOURCE_OWNER_OUTER_WAIT_REQUIRED')
        frame=self.source_owner_native_frame('COMPLETE',3)
        require(self.requester_actor is not None and frame['child_pid']==self.requester_actor['pid']
            and frame['terminal']['wait']==0,'RESOURCE_CONTROL_ACTUAL_NESTED_ACTOR_WAIT_REQUIRED')
        poller=select.poll();poller.register(self.requester_actor_pidfd,25)
        actual=poller.poll(0)
        self.record('actual-nested-actor-terminal-poll',{'pid':self.requester_actor['pid'],
            'pidfd':self.requester_actor_pidfd,'result':actual,'source_owner_terminal_hex':__import__('worldline.root_worker_codec',fromlist=['archive']).archive(frame['terminal']).hex()})
        require(actual,'RESOURCE_CONTROL_ACTUAL_NESTED_ACTOR_TERMINAL_UNKNOWN')
    def provision_original_journals(self):
        """Genuine one-time native admission; never reset a prior ledger."""
        lease=StartupLease(Path(self.plan['startup_descriptor']),resource_control=self)
        self.lease=lease;primary=None
        try:
            intent_gate=self.selected_gate(lease)
            require(lease.db.execute('SELECT * FROM journal_history ORDER BY ordinal').fetchall()==[],
                'RESOURCE_CONTROL_ORIGINAL_UNUSED_OWNER_REQUIRED')
            rows=lease.db.execute('SELECT name,state FROM journal_intents ORDER BY name').fetchall()
            require({name for name,_state in rows}==set(lease.genesis['journals'])
                and all(state=='UNUSED' for _name,state in rows)
                and all(not os.path.lexists(row['path']) for row in lease.genesis['journals'].values()),
                'RESOURCE_CONTROL_NO_PRIOR_JOURNAL_ADMISSION_REQUIRED')
            lease.gate=lease._construct_gate(intent_gate)
            for name,row in lease.genesis['journals'].items():
                lease.open_journal(lease.gate,name,Path(row['path']),row['initial_envelope'])
                decision=lease.journal_admission_decisions[name][-1]
                self.record('actual-owner-native-journal-admission',{'name':name,
                    'path':row['path'],'raw_hex':private_bytes(row['path']).hex(),
                    'status':decision.status,'position':decision.position,
                    'envelope_hex':decision.envelope.hex(),'name_hex':decision.name.hex()})
        except BaseException as exc:primary=exc;raise
        finally:
            try:lease.close()
            except BaseException as exc:
                self.record('actual-offline-owner-close-failure',_error(exc))
                if primary is None:raise
                primary.add_note('Actual offline owner close: '+repr(exc))
            if lease.closed:self.lease=None
    def construct(self):
        lease=StartupLease(Path(self.plan['startup_descriptor']),resource_control=self)
        self.lease=lease;lease.construct();self.intact()
        self.record('actual-full-owner-constructed',{'descriptor':str(lease.descriptor_path),
            'genesis_sha256':lease.genesis_id,'complete_lock_roster':list(lease.fds)})
    @staticmethod
    def peer_child(path):
        source,plan,_raw,descriptor,raw,_document=selected_plan(path,peer_child=True)
        source.check()
        transport=OwnerResourceControl.requester_selection_data(source,plan,Path(path),
            descriptor,raw,Path(plan['result_directory']))
        if transport is not None:
            require(os.geteuid()==0 and not source.excluded_actor(),
                'RESOURCE_CONTROL_ACTUAL_ROOT_SOURCE_OWNER_BRIDGE_REQUIRED')
            require(sys.argv==[plan['peer_child_entry'],'--peer-child','--plan',str(path)]
                and sys.modules['__main__'].__file__==plan['peer_child_entry'],
                'RESOURCE_CONTROL_ORIGINAL_ENTRY_EXEC_CORRESPONDENCE_REQUIRED')
            source.file(transport['entry'],('ENTRY',))
            source.file(source.interpreter,('INTERPRETER',))
            argv=[source.interpreter,'-I','-S','-B',source.helper_path,
                '--bootstrap-envelope',plan['peer_child_envelope'],'--entry',
                transport['entry'],'--request',transport['path']]
            original={'schema':'worldline.original-resource-root-source-exec-boundary-v1',
                'pid':os.getpid(),'argv_before':list(sys.orig_argv),'entry_before':sys.argv[0],
                'argv_after_selected':argv,'source_before_exec':source.check(),
                'selected_original_client_hex':transport['raw'].hex(),
                'selected_source_owner_hex':transport['owner_raw'].hex()}
            sys.stderr.write(json.dumps(original,sort_keys=True,separators=(',',':'))+'\n')
            sys.stderr.flush();os.fsync(2)
            os.execve(source.interpreter,argv,dict(os.environ))
            raise RuntimeError('RESOURCE_CONTROL_ACTUAL_EXEC_RETURNED')
        endpoint=descriptor['endpoint'];named=Path(endpoint['path'])
        before=named.lstat()
        require(stat.S_ISSOCK(before.st_mode) and before.st_uid==0
            and before.st_gid==endpoint['requester_gid'] and stat.S_IMODE(before.st_mode)==0o660,
            'RESOURCE_CONTROL_SELECTED_SOCKET_INODE_REQUIRED')
        held=None;close_attempted=False;primary=None
        observed={'schema':'worldline.original-resource-requester-held-endpoint-v1',
            'endpoint':str(named),'named_identity':[before.st_dev,before.st_ino,before.st_mode,
                before.st_uid,before.st_gid],'held_identity':None,'connect':None,
            'final_credentials':None,'close':None,'error':None,'phase_acceptance':False}
        def retain():
            body=canonical(observed)+b'\n';position=0
            while position<len(body):
                sent=os.write(1,body[position:]);require(sent>0,'RESOURCE_CONTROL_ACTUAL_CHILD_RAW_WRITE_REQUIRED')
                position+=sent
        try:
            # Hold THIS socket inode, not an ancestry-bypassing asserted parent.
            # Linux proc magic-link and Unix inode lookup semantics are referenced
            # in the packet. Actual installed-kernel behavior remains a control.
            held=os.open(named,os.O_PATH|os.O_NOFOLLOW|os.O_CLOEXEC)
            info=os.fstat(held);current=named.lstat()
            observed['held_identity']=[info.st_dev,info.st_ino,info.st_mode,info.st_uid,info.st_gid]
            require(observed['held_identity']==observed['named_identity']
                and (current.st_dev,current.st_ino)==(info.st_dev,info.st_ino),
                'RESOURCE_CONTROL_EXACT_HELD_ENDPOINT_INODE_REQUIRED')
            os.setgroups([]);os.setgid(endpoint['requester_gid']);os.setuid(endpoint['requester_uid'])
            credentials={'pid':os.getpid(),'uids':list(os.getresuid()),
                'gids':list(os.getresgid()),'groups':os.getgroups()}
            observed['final_credentials']=credentials
            require(all(uid==endpoint['requester_uid'] for uid in credentials['uids'])
                and all(gid==endpoint['requester_gid'] for gid in credentials['gids'])
                and credentials['groups']==[], 'RESOURCE_CONTROL_ACTUAL_FINAL_CREDENTIALS_REQUIRED')
            require((os.fstat(held).st_dev,os.fstat(held).st_ino)==(info.st_dev,info.st_ino),
                'RESOURCE_CONTROL_HELD_SOCKET_CHANGED_AFTER_CREDENTIAL_DROP')
            deadline=time.monotonic()+plan['timeout']
            with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM|socket.SOCK_CLOEXEC) as connection:
                route='/proc/self/fd/'+str(held)
                connection.settimeout(max(0,deadline-time.monotonic()))
                observed['connect']={'route':route,'result':None,'credentials':credentials}
                connection.connect(route)
                observed['connect'].update(result=0,peer_name=connection.getpeername(),
                    local_name=connection.getsockname())
                retain()
                connection.sendall(raw.rstrip(b'\n')+b'\n')
                require(connection.recv(1)==b'C','RESOURCE_CONTROL_ACTUAL_PARENT_CLOSE_REQUIRED')
        except BaseException as error:
            primary=error;observed['error']=_error(error);raise
        finally:
            if held is not None and not close_attempted:
                close_attempted=True;observed['close']={'status':'UNKNOWN_AFTER_CLOSE_ATTEMPT'}
                try:
                    os.close(held);observed['close']={'result':0}
                except BaseException as error:
                    observed['close']['error']=_error(error)
                    if primary is None:primary=error
                    else:primary.add_note('Actual held endpoint close: '+repr(error))
            try:retain()
            except BaseException as error:
                if primary is None:primary=error
                else:primary.add_note('Actual held endpoint raw retention: '+repr(error))
            if primary is not None and sys.exc_info()[1] is None:raise primary

    def acquire_request_peer(self):
        self.intact();endpoint=self.lease.spec['endpoint'];path=Path(endpoint['path'])
        protected(path.parent,directory=True)
        require(not os.path.lexists(path),'RESOURCE_CONTROL_PEER_ENDPOINT_ALREADY_EXISTS')
        listener=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM|socket.SOCK_CLOEXEC)
        self.peer_listener=listener;listener.bind(str(path))
        os.chown(path,0,endpoint['requester_gid']);os.chmod(path,0o660)
        self.peer_socket_identity=(path.stat().st_dev,path.stat().st_ino)
        listener.listen();listener.settimeout(self.remaining())
        out=(self.output/'request-peer.stdout').open('x+b');self.peer_raw_files.append(out)
        os.fchmod(out.fileno(),0o600)
        err=(self.output/'request-peer.stderr').open('x+b');self.peer_raw_files.append(err)
        os.fchmod(err.fileno(),0o600)
        argv=[self.source_lease.interpreter,'-I','-S','-B',self.source_lease.helper_path,
            '--bootstrap-envelope',self.plan['peer_child_envelope'],'--entry',
            self.plan['peer_child_entry'],'--peer-child','--plan',str(self.plan_path)]
        self.requester_transport=self.requester_selection()
        if (self.requester_transport is not None
                and self.plan['peer_child_entry']==self.requester_transport['entry']):
            argv=[self.source_lease.interpreter,'-I','-S','-B',self.source_lease.helper_path,
                '--bootstrap-envelope',self.plan['peer_child_envelope'],'--entry',
                self.plan['peer_child_entry'],'--request',self.requester_transport['path']]
        child=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=out,stderr=err,
            env={'PATH':'/usr/bin:/bin','LANG':'C'});self.child=child
        self.record('actual-request-peer-popen-identity',{'argv':argv,'pid':child.pid})
        self.child_pidfd=os.pidfd_open(child.pid)
        birth=(Path('/proc')/str(child.pid)/'stat').read_bytes()
        self.record('actual-request-peer-start',{'argv':argv,'pid':child.pid,
            'stat_hex':birth.hex(),'cmdline_hex':(Path('/proc')/str(child.pid)/'cmdline').read_bytes().hex()})
        connection,_address=listener.accept();self.peer_connection=connection
        connection.settimeout(self.remaining())
        with connection.makefile('rb') as stream:raw=stream.readline()
        require(raw==self.request_raw.rstrip(b'\n')+b'\n',
            'RESOURCE_CONTROL_REAL_REQUEST_BYTES_CHANGED')
        peer=KernelPeer.capture_descriptor(connection.fileno())
        try:
            observed=peer.observation()
            if self.requester_transport is not None:
                self.join_requester_actor(observed)
            require((observed['pid']==child.pid if self.requester_transport is None
                    else observed['pid']==self.requester_actor['pid'])
                and observed['uid']==endpoint['requester_uid']
                and observed['gid']==endpoint['requester_gid'],
                'RESOURCE_CONTROL_ACTUAL_REQUESTER_CREDENTIALS_REQUIRED')
            self.request=RequestPeer(peer,{'schema':'worldline.client-request-observation-v1',
                'observationId':uuid.uuid4().hex,'requestId':self.document['id'],
                'operation':self.document['op'],'rawRequest':raw.hex(),'peer':observed})
        except BaseException:peer.close();raise
        self.request_scope=request_scope(self.request);self.request_scope.__enter__()
        self.record('actual-request-peer-capture',self.request.observation())
    def start_server(self):
        import run_service
        owner=self
        class Handler(run_service.Handler):
            def handle(inner):
                state=owner.rpc_state(inner.request)
                try:answer=owner.handle_rpc(inner.request)
                except run_service.Refusal as exc:
                    state['errors'].append({'stage':'handler-refusal','actual':_error(exc)})
                    owner.retain_rpc(state,'actual-handler-refusal')
                    answer={'status':'REFUSED','reason':str(exc)}
                except Exception as exc:
                    state['errors'].append({'stage':'handler-exception','actual':_error(exc)})
                    owner.retain_rpc(state,'actual-handler-exception')
                    answer={'status':'REFUSED','reason':'FULL_LEDGER_PROTECTED_FACT_UNAVAILABLE'}
                if owner.drop_ack_packet is not None and answer.get('status')=='READY':
                    packet=owner.drop_ack_packet
                    actual=owner.resources.service.recover(packet,os.geteuid())
                    require(actual==answer,'RESOURCE_CONTROL_LOST_ACK_EXACT_NATIVE_COMMIT_REQUIRED')
                    owner.record('actual-native-commit-before-deliberate-ack-disconnect',
                        {'packet':packet,'native_result':actual})
                    owner.drop_ack_packet=None
                    state['ack_shutdown']={'attempted':True,'result':None}
                    try:inner.request.shutdown(socket.SHUT_WR);state['ack_shutdown']['result']=0
                    except BaseException as exc:
                        state['ack_shutdown']['error']=_error(exc);raise
                    finally:owner.retain_rpc(state,'actual-deliberate-ack-disconnect')
                    return
                raw=run_service.canonical(answer)+b'\n'
                state['response_hex']=raw.hex()
                owner.retain_rpc(state,'actual-native-rpc-response-before-send')
                position=0
                while position<len(raw):
                    try:sent=inner.request.send(raw[position:])
                    except BaseException as exc:
                        state['send_calls'].append({'offered_hex':raw[position:].hex(),
                            'result':None,'actual_error':_error(exc)})
                        owner.retain_rpc(state,'actual-rpc-send-exception');raise
                    state['send_calls'].append({'offered_hex':raw[position:].hex(),
                        'result':sent,'sent_hex':raw[position:position+sent].hex()})
                    owner.retain_rpc(state,'actual-rpc-send-return')
                    require(sent>0,'RESOURCE_CONTROL_RPC_SEND_PROGRESS_REQUIRED');position+=sent
        path=self.resources.service.socket_path
        require(not os.path.lexists(path),'RESOURCE_CONTROL_SERVICE_ENDPOINT_ALREADY_EXISTS')
        class ControlServer(run_service.Server):
            def process_request(inner,connection,address):
                # Register actual accepted socket ownership BEFORE fstat/ucred or
                # a worker start can fail. All initial fields are UNKNOWN.
                key=uuid.uuid4().hex
                state={'key':key,'connection':connection,'thread':None,'started':False,
                    'identity':None,'peer_hex':None,'complete':False,'exception':None,
                    'errors':[],'recv_calls':[],'send_calls':[],'stream_end':None,
                    'shutdown':None,'shutdown_attempted':False,'address':address}
                with owner.rpc_lock:owner.rpc_threads[key]=state
                thread=threading.Thread(target=inner.process_request_thread,
                    args=(connection,address),daemon=True);state['thread']=thread
                try:thread.start();state['started']=True
                except BaseException as exc:
                    state['errors'].append({'stage':'thread-start','actual':_error(exc)})
                    owner.retain_rpc(state,'actual-rpc-thread-start-refusal');raise
            def process_request_thread(inner,connection,address):
                state=owner.rpc_state(connection);primary=None
                state['started']=True
                try:
                    info=os.fstat(connection.fileno());state['identity']=[info.st_dev,info.st_ino]
                    state['peer_hex']=connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,
                        __import__('worldline.client_peer',fromlist=['UCRED']).UCRED.size).hex()
                    owner.retain_rpc(state,'actual-owned-rpc-handler-intake')
                    inner.finish_request(connection,address)
                except BaseException as exc:
                    primary=exc;state['exception']=_error(exc)
                    state['errors'].append({'stage':'request-thread','actual':_error(exc)})
                finally:
                    try:inner.shutdown_request(connection)
                    except BaseException as exc:
                        state['errors'].append({'stage':'shutdown-request','actual':_error(exc)})
                        if primary is None:primary=exc
                        else:primary.add_note('Actual owned RPC shutdown: '+repr(exc))
                    state['complete']=True
                    try:owner.retain_rpc(state,'actual-owned-rpc-handler-return')
                    except BaseException as exc:
                        state['errors'].append({'stage':'final-retention','actual':_error(exc)})
                        if primary is None:primary=exc
                        else:primary.add_note('Actual owned RPC return retention: '+repr(exc))
                if primary is not None:raise primary
            def shutdown_request(inner,connection):
                state=owner.rpc_state(connection)
                require(not state['shutdown_attempted'],'RESOURCE_CONTROL_RPC_CLOSE_ALREADY_ATTEMPTED')
                state['shutdown_attempted']=True
                state['shutdown']={'status':'UNKNOWN_AFTER_SOCKET_CLOSE_ATTEMPT'}
                try:
                    super(ControlServer,inner).shutdown_request(connection)
                    state['shutdown']={'result':0,'fileno_after':connection.fileno()}
                except BaseException as exc:
                    state['shutdown']['error']=_error(exc);raise
        server=ControlServer(self.resources.service)
        server.RequestHandlerClass=Handler;self.server=server
        os.chmod(path,0o600);self.server_socket_identity=(path.stat().st_dev,path.stat().st_ino)
        lifecycle={'started':False,'entered':False,'returned':False,'error':None,
            'shutdown_thread':None,'shutdown_started':False,'shutdown_returned':False,'shutdown_error':None}
        self.server_state=lifecycle
        def serve():
            lifecycle['entered']=True
            try:server.serve_forever()
            except BaseException as exc:lifecycle['error']=_error(exc);raise
            finally:lifecycle['returned']=True
        thread=threading.Thread(target=serve,daemon=True);self.server_thread=thread
        try:thread.start();lifecycle['started']=True
        except BaseException as exc:
            lifecycle['error']=_error(exc)
            self.record('actual-native-rpc-server-thread-start-refusal',{'error':_error(exc)})
            raise
        self.record('actual-native-rpc-owner-start',{'path':str(path),
            'identity':list(self.server_socket_identity),'owner_pid':os.getpid()})

    def rpc_state(self,connection):
        with self.rpc_lock:
            states=[value for value in self.rpc_threads.values() if value['connection'] is connection]
        require(len(states)==1,'RESOURCE_CONTROL_ACTUAL_REGISTERED_RPC_SOCKET_REQUIRED')
        return states[0]
    def rpc_snapshot(self,state):
        return {key:value for key,value in state.items() if key not in ('connection','thread')} | {
            'thread':None if state['thread'] is None else state['thread'].ident,
            'alive':None if state['thread'] is None else state['thread'].is_alive()}
    def retain_rpc(self,state,cause):
        snapshot=self.rpc_snapshot(state)
        raw=canonical({'schema':'worldline.original-resource-rpc-actual-custody-v1',
            'cause':cause,'state':snapshot})+b'\n';position=0
        while position<len(raw):
            sent=os.write(2,raw[position:]);require(sent>0,'RESOURCE_CONTROL_RAW_RPC_RETENTION_PROGRESS_REQUIRED')
            position+=sent
        self.record(cause,snapshot)
    def handle_rpc(self,connection):
        import struct
        import run_service
        pid,uid,_gid=struct.unpack('3i',connection.getsockopt(socket.SOL_SOCKET,
            socket.SO_PEERCRED,struct.calcsize('3i')))
        require(pid>0 and uid==0,'PEER_NOT_ROOT_GATE')
        connection.settimeout(self.remaining())
        state=self.rpc_state(connection);chunks=[]
        while True:
            try:piece=connection.recv(4096)
            except BaseException as exc:
                state['recv_calls'].append({'result':None,'raw_hex':None,'actual_error':_error(exc)})
                self.retain_rpc(state,'actual-rpc-read-exception');raise
            state['recv_calls'].append({'result':len(piece),'raw_hex':piece.hex()})
            if not piece:state['stream_end']='EOF'
            self.retain_rpc(state,'actual-rpc-read-return')
            chunks.append(piece)
            if not piece or b'\n' in piece:break
        received=b''.join(chunks);raw=received.split(b'\n',1)[0]+(b'\n' if b'\n' in received else b'')
        state['request_line_hex']=raw.hex()
        require(raw.endswith(b'\n'),'FULL_LEDGER_FRAME_INVALID')
        info=os.fstat(connection.fileno())
        self.record('actual-root-native-rpc-request',{'peer_pid':pid,'peer_uid':uid,
            'peer_gid':_gid,'identity':[info.st_dev,info.st_ino],
            'raw_hex':raw.hex()})
        message=run_service.parse_canonical(raw[:-1])
        if type(message) is dict and message.get('schema') in (
                'worldline.protected-resource-recover-v1','worldline.protected-resource-current-v1'):
            require(set(message)=={'schema','request'},'FULL_LEDGER_RECOVER_INVALID')
            if message['schema']=='worldline.protected-resource-current-v1':
                return self.resources.service.inspect_launch_intent(message['request'],uid)
            return self.resources.service.recover(message['request'],uid)
        _state,_rows,request=self.resources.service._decode_packet(message)
        capture=self.captures.get(request.request_id.hex())
        require(capture is not None and capture['packet']==message,
            'RESOURCE_CONTROL_ACTUAL_CANONICAL_CAPTURE_REQUIRED_BEFORE_RPC')
        self.intact()
        require(self.request.observation()==capture['original_request'],
            'RESOURCE_CONTROL_ACTUAL_REQUESTER_CHANGED_BEFORE_RPC')
        answer=self.resources.service.mutate(message,uid)
        # The actual native transaction commits before PREPARED retention and
        # before its socket reply. Lost ACK therefore keeps the complete native
        # result and preparation; a retention refusal never emits a success.
        retained=self.resources.retain_control_submission(self,capture,answer)
        self.responses[request.request_id.hex()]=retained
        if request.kind=='RESERVE':self.reserve_result=retained
        self.record('actual-native-commit-and-preparation-before-rpc-reply',
            {'packet':message,'native_result':retained})
        return retained
    def prepare(self):
        self.provision_original_journals();self.construct();self.acquire_request_peer()
        row=self.principal.prepare_resource_control(self.request,self)
        self.operation=row['capture']['operation'];intent=row['capture']['resource_intent']
        self.reservation=intent.reservation
        packet=self.resources.reserve_packet(intent)
        self.publish_owner_crosswalk(packet,row)
        self.start_server();self.capture(packet)
        value={'schema':SCHEMA,'case':self.plan['case'],
            'gate_config':str(self.lease.gate.root/'authority/gate/config.json'),
            'resource_root':str(self.resources.service.root),'operation_id':self.operation,
            'packets':[packet]}
        case=self.plan['case']
        if case=='SEQUENTIAL':value['packets']=LivePackets(self)
        elif case=='LOST_ACK_RESTART':
            from gate_bridge import FullResourceGateBridge
            self.drop_ack_packet=packet
            try:FullResourceGateBridge(self.lease.gate).submit(**self.arguments(packet))
            except (OSError,ValueError,RuntimeError) as exc:
                self.record('actual-lost-ack-caller-exception',_error(exc))
            else:raise RuntimeError('RESOURCE_CONTROL_ACTUAL_ACK_LOSS_REQUIRED')
            self.after(packet);self.restart_owners()
        elif case=='CLOSED_AFTER_COMMIT':
            from gate_bridge import FullResourceGateBridge
            answer=FullResourceGateBridge(self.lease.gate).submit(**self.arguments(packet))
            self.after(packet,answer)
            with self.lease.gate.mutex:
                self.lease.gate.close_pending(self.lease.gate.journal['pending'],
                    'FULL_RESOURCE_ACTUAL_COMMITTED_CONTROL',native_result=answer)
            self.record('actual-gate-closed-after-native-commit',self.lease.gate.journal)
        elif case=='LEGACY_COMMITTED':self.commit_v1_compatibility(packet)
        elif case=='DISPATCH_UNKNOWN':
            from gate_bridge import FullResourceGateBridge
            from .linux.systemd import SystemdAdapter
            answer=FullResourceGateBridge(self.lease.gate).submit(**self.arguments(packet))
            self.after(packet,answer);self.start_effect()
            self.dispatch_instance=str(uuid.uuid4())
            unit=('worldline-'+self.dispatch_instance+'.service').encode('ascii')
            self.record('actual-dispatch-instance-selection',{'instance_id':self.dispatch_instance})
            launch=self.resources.lifecycle_packet(self.request,self.reservation,
                'RECORD_LAUNCH_INTENT',{'state':'LAUNCH_INTENT','planned_unit':unit})
            self.capture(launch)
            plan=self.principal.resource_launch_material(self.request,self.reservation)
            bridge=FullResourceGateBridge(self.lease.gate)
            try:
                process=bridge.launch_after_intent(**self.arguments(launch),manager=SystemdAdapter(),
                    instance_id=self.dispatch_instance,argv=plan['argv'],
                    resource_properties=plan['systemd_properties'],
                    description='Original full resource dispatch-intent control')
                self.operational_dispatch=process
                self.record('actual-original-manager-dispatch-return',{'unit':process.unit})
            except BaseException as exc:
                self.record('actual-original-manager-dispatch-exception',_error(exc))
                completed,_outstanding,dispatched=bridge._history()
                require(restore_dto(launch['request']).request_id.hex() in dispatched,
                    'RESOURCE_CONTROL_ACTUAL_DISPATCH_INTENT_REQUIRED')
            self.after(launch);value.update(packets=[launch],instance_id=self.dispatch_instance,
                argv=plan['argv'],description='Original full resource dispatch-intent control')
        self.intact();return value
    @staticmethod
    def arguments(packet):
        return {'proposed':restore_dto(packet['proposed']),
            'rows':tuple(restore_dto(row) for row in packet['rows']),
            'request':restore_dto(packet['request'])}
    def publish_owner_crosswalk(self,packet,row):
        intent_gate=self.selected_gate(self.lease)
        gate=self.lease.gate;request=restore_dto(packet['request'])
        with gate.mutex:
            raw,current=__import__('gate_bridge').gate_bytes(gate.state_path)
            require(current==gate.journal and current.get('pending') is None
                and current.get('history')==[] and current.get('full_resource_history_v2',[])==[],
                'RESOURCE_CONTROL_NEW_OWNER_HISTORY_REQUIRED')
            require('full_resource_history_v2' not in current
                or type(current['full_resource_history_v2']) is list,
                'RESOURCE_CONTROL_OWNER_HISTORY_SCHEMA_CHANGED')
            captured=self.principal.resource_binding(
                self.principal.pending_for_operation(request.operation_id),self.request)
            require(captured['request']==packet['request'] and row['native']['observation']['decision']=='RESERVED_NEW',
                'RESOURCE_CONTROL_ACTUAL_CANONICAL_NATIVE_RESERVATION_REQUIRED')
            pending={'operation_id':request.operation_id.hex(),'request_id':self.document['id'],
                'resource':{'reserve':{'binding':{'universe_id':request.scope.universe.hex(),
                    'universe_head':request.bound.universe_head.hex(),
                    'candidate_digest':request.bound.payload.hex()}}},
                'full_resource_scope_v1':dto_record(request.scope),
                'full_resource_binding_v1':dto_record(request.bound),
                'full_canonical_operation_source_v1':{'native_use':
                    __import__('worldline.protected_resource_runtime',fromlist=['full_capture_record']).full_capture_record(captured['native_use']),
                    'event_id':captured['event_id'],'full_capture_hex':captured['full_capture']}}
            gate.journal['pending']=pending;gate.journal['full_resource_history_v2']=[]
            require(__import__('gate_bridge').gate_bytes(gate.state_path)[0]==raw,
                'RESOURCE_CONTROL_OWNER_HISTORY_CHANGED_BEFORE_SAVE')
            intent_gate.save(gate.state_path,gate.journal)
            require(__import__('gate_bridge').gate_bytes(gate.state_path)[1]==gate.journal,
                'RESOURCE_CONTROL_OWNER_CROSSWALK_DURABILITY_UNKNOWN')
            self.record('actual-owner-native-crosswalk-publication',pending)
    def capture(self,packet):
        self.intact();record=self.resources.capture_control_submission(self,packet)
        key=restore_dto(packet['request']).request_id.hex()
        require(key not in self.captures,'RESOURCE_CONTROL_PACKET_CAPTURE_REPLAY')
        self.captures[key]=record;self.packet_records.append(packet)
        self.record('actual-canonical-before-resource-rpc',record)
        return packet
    def after(self,packet,answer=None):
        key=restore_dto(packet['request']).request_id.hex()
        actual=self.resources.service.recover(packet,os.geteuid())
        require(actual.get('status')=='READY' and (answer is None or actual==answer),
            'RESOURCE_CONTROL_REAL_NATIVE_COMMIT_REQUIRED')
        retained=self.resources.retain_control_submission(self,self.captures[key],actual)
        self.responses[key]=retained
        if restore_dto(packet['request']).kind=='RESERVE':self.reserve_result=retained
        self.record('actual-complete-resource-native-result',{'packet':packet,'result':retained})
        return retained
    def packet_for_kind(self,kind):
        rows=[packet for packet in self.packet_records if restore_dto(packet['request']).kind==kind]
        require(len(rows)==1,'RESOURCE_CONTROL_EXACT_ACTUAL_PACKET_REQUIRED');return rows[0]
    def start_effect(self):self.principal.start_resource_control_effect(self.request,self)
    def commit_v1_compatibility(self,packet):
        intent_gate=self.selected_gate(self.lease)
        from gate_bridge import FullResourceGateBridge,detached
        bridge=FullResourceGateBridge(self.lease.gate)
        with self.lease.gate.mutex:
            completed,outstanding,_dispatch=bridge._begin()
            require(not completed and outstanding is None,
                'RESOURCE_CONTROL_V1_FRESH_NATIVE_TRANSACTION_REQUIRED')
            pending=self.lease.gate.journal['pending'];bridge._binding(packet,pending)
            require('full_resource_intent_v1' not in pending,
                'RESOURCE_CONTROL_V1_INTENT_ALREADY_PRESENT')
            pending['full_resource_intent_v1']={'request':detached(packet),
                'sha256':hashlib.sha256(intent_gate.canonical(packet)).hexdigest()}
            bridge._save()
            self.record('actual-new-v1-format-owner-intent-before-native-rpc',pending['full_resource_intent_v1'])
            answer=bridge._rpc(packet)
            pending['full_resource_intent_v1']['result']=detached(answer);bridge._save()
            self.record('actual-new-v1-format-native-result-retained',pending['full_resource_intent_v1'])
        self.after(packet,answer)
    def restart_owners(self):
        # A genuine close/reconstruction from the retained owner paths. No SQL,
        # source history, native result or missing preparation is recreated.
        self.stop_server();old=self.lease;old.close()
        require(old.closed,'RESOURCE_CONTROL_ACTUAL_OLD_OWNER_CLOSE_REQUIRED')
        self.lease=None;self.resources=None;self.principal=None
        self.construct();self.start_server()
        self.record('actual-owner-restart-from-retained-state',{'operation':self.operation})
    def sequential(self):
        packet=self.packet_for_kind('RESERVE');yield packet;self.after(packet)
        self.start_effect();unit=b'worldline-resource-'+self.reservation.hex().encode('ascii')+b'.service'
        packet=self.capture(self.resources.lifecycle_packet(self.request,self.reservation,
            'RECORD_LAUNCH_INTENT',{'state':'LAUNCH_INTENT','planned_unit':unit}))
        yield packet;self.after(packet)
        self.slot,native=self.resources.dispatch_control_launch(self,self.reservation)
        self.start_raw_drains()
        packet=self.capture(self.resources.lifecycle_packet(self.request,self.reservation,
            'RECORD_RUNNING',{'state':'RUNNING','actual_unit':native['actual_unit'],
                'cgroup':native['cgroup'],'invocation':native['invocation']}))
        yield packet;self.after(packet);self.slot.go()
        packet=self.capture(self.resources.lifecycle_packet(self.request,self.reservation,
            'RECORD_TERMINATING',{'state':'TERMINATING'}))
        yield packet;self.after(packet)
        status=asyncio.run(asyncio.wait_for(self.slot.wait(),timeout=self.remaining()))
        self.record('actual-original-supervisor-closed-and-pidfd-wait',{'returncode':status,
            'closed':self.slot.closed,'observation':self.slot.observe()['raw']})
        packet=self.capture(self.resources.lifecycle_packet(self.request,self.reservation,
            'RECORD_TERMINAL',{'state':'TERMINAL'}))
        yield packet;self.after(packet)
        packet=self.capture(self.resources.lifecycle_packet(self.request,self.reservation,
            'RELEASE_HOLD',{'state':'RELEASED'}))
        yield packet;self.after(packet)
    def start_raw_drains(self):
        for name,fd in (('stdout',self.slot.stdout_fd),('stderr',self.slot.stderr_fd)):
            info=os.fstat(fd);require(stat.S_ISFIFO(info.st_mode),
                'RESOURCE_CONTROL_REAL_OWNED_OUTPUT_PIPE_REQUIRED')
            held=os.dup(fd)
            state={'fd':held,'output':None,'stop':threading.Event(),'stream_end':None,
                'error':None,'close':None,'close_attempted':False,'thread':None,'started':False,
                'identity':[info.st_dev,info.st_ino,info.st_mode]}
            self.drains.append(state)
            os.set_blocking(held,False)
            output=(self.output/('workload.'+name)).open('x+b');state['output']=output
            os.fchmod(output.fileno(),0o600)
            def drain(state=state):
                try:
                    while not state['stop'].is_set():
                        readable,_write,_exceptional=select.select([state['fd']],[],[],0.01)
                        if not readable:continue
                        chunk=os.read(state['fd'],65536)
                        if not chunk:state['stream_end']='EOF';break
                        state['output'].write(chunk);os.fsync(state['output'].fileno())
                except BaseException as exc:state['error']=_error(exc)
                finally:
                    # One close attempt, never retry a possibly reused FD.
                    state['close_attempted']=True
                    try:os.close(state['fd']);state['close']={'result':0}
                    except BaseException as exc:state['close']={'error':_error(exc)}
            thread=threading.Thread(target=drain,daemon=True);state['thread']=thread
            thread.start();state['started']=True
    def retain_server(self,cause):
        lifecycle=self.server_state
        with self.rpc_lock:states=list(self.rpc_threads.values())
        value={'server':None if lifecycle is None else {
            key:item for key,item in lifecycle.items() if key!='shutdown_thread'},
            'server_thread':None if self.server_thread is None else {
                'ident':self.server_thread.ident,'alive':self.server_thread.is_alive()},
            'shutdown_thread':None if lifecycle is None or lifecycle['shutdown_thread'] is None else {
                'ident':lifecycle['shutdown_thread'].ident,'alive':lifecycle['shutdown_thread'].is_alive()},
            'rpc_roster':[self.rpc_snapshot(state) for state in states],
            'phase_acceptance':False}
        raw=canonical({'schema':'worldline.original-resource-server-actual-custody-v1',
            'cause':cause,'value':value})+b'\n';position=0
        while position<len(raw):
            sent=os.write(2,raw[position:]);require(sent>0,'RESOURCE_CONTROL_RAW_SERVER_RETENTION_REQUIRED')
            position+=sent
        self.record(cause,value)
    def stop_server(self):
        try:
            if self.server is None:return
            server=self.server;path=server.ledger.socket_path;lifecycle=self.server_state
            require(type(lifecycle) is dict,'RESOURCE_CONTROL_ACTUAL_SERVER_LIFECYCLE_REQUIRED')
            # shutdown() waits indefinitely for serve_forever's finally event. Never
            # call it for a never-started thread. A real started but uncertain loop
            # retains a separately owned shutdown thread under the ORIGINAL deadline.
            if self.server_thread is not None and self.server_thread.is_alive():
                def shutdown():
                    try:server.shutdown();lifecycle['shutdown_returned']=True
                    except BaseException as exc:lifecycle['shutdown_error']=_error(exc);raise
                thread=threading.Thread(target=shutdown,daemon=True)
                lifecycle['shutdown_thread']=thread
                try:thread.start();lifecycle['shutdown_started']=True
                except BaseException as exc:lifecycle['shutdown_error']=_error(exc);raise
                thread.join(timeout=max(0,self.deadline-time.monotonic()))
                require(not thread.is_alive() and lifecycle['shutdown_returned'],
                    'RESOURCE_CONTROL_SERVER_SHUTDOWN_WAIT_UNKNOWN')
            if self.server_thread is not None and self.server_thread.ident is not None:
                self.server_thread.join(timeout=max(0,self.deadline-time.monotonic()))
            require(self.server_thread is None or not self.server_thread.is_alive(),
                'RESOURCE_CONTROL_SERVICE_STOP_UNKNOWN')
            with self.rpc_lock:states=list(self.rpc_threads.values())
            for state in states:
                thread=state['thread']
                if thread is not None and thread.ident is not None:
                    thread.join(timeout=max(0,self.deadline-time.monotonic()))
            unknown=[state for state in states if (state['thread'] is not None
                and state['thread'].is_alive()) or not state['complete']]
            self.record('actual-complete-rpc-handler-roster',{'roster':[self.rpc_snapshot(state) for state in states],
                'server':{key:value for key,value in lifecycle.items() if key!='shutdown_thread'}})
            require(not unknown,'RESOURCE_CONTROL_RPC_HANDLER_CUSTODY_UNKNOWN')
            server.server_close();self.server=None
            info=path.lstat();require((info.st_dev,info.st_ino)==self.server_socket_identity
                and stat.S_ISSOCK(info.st_mode),'RESOURCE_CONTROL_SERVICE_ENDPOINT_IDENTITY_CHANGED')
            path.unlink();self.record('actual-service-owner-close',{'path':str(path)})
        finally:
            primary=sys.exc_info()[1]
            try:self.retain_server('actual-server-stop-partial-custody')
            except BaseException as secondary:
                if primary is None:raise
                primary.add_note('Actual server stop custody retention: '+repr(secondary))

    def close(self):
        if self.closed:return
        require(not self.close_attempted,
            'RESOURCE_CONTROL_PRIOR_CLEANUP_UNKNOWN_REQUIRES_CUSTODY_COLLECTION')
        self.close_attempted=True
        errors=[]
        def attempt(name,function):
            try:function()
            except BaseException as exc:
                errors.append(exc)
                try:self.record('actual-cleanup-exception',{'name':name,'error':_error(exc)})
                except BaseException as retention:
                    errors.append(retention);exc.add_note('Actual cleanup retention: '+repr(retention))
            else:
                try:self.record('actual-cleanup-return',{'name':name})
                except BaseException as retention:errors.append(retention)
        if self.server is not None:attempt('native-service-owner',self.stop_server)
        rpc_quiescent=self.server is None
        # Retain actual any direct-service commit made by the unchanged conflict
        # test before cleanup; NOT_COMMITTED remains a recorded fact, not a pass.
        if rpc_quiescent and self.resources is not None and self.request is not None:
            for packet in self.packet_records:
                key=restore_dto(packet['request']).request_id.hex()
                if key not in self.responses:
                    def retain_actual(packet=packet):
                        actual=self.resources.service.recover(packet,os.geteuid())
                        if actual.get('status')=='READY':self.after(packet,actual)
                        else:self.record('actual-uncommitted-resource-packet',{'packet':packet,'result':actual})
                    attempt('retain-actual-direct-service-commit',retain_actual)
            if (self.principal is not None and self.operation is not None
                    and self.operation in self.principal.journal.rows):
                row=self.principal.journal.rows[self.operation]
                if row['state'] not in ('SETTLED','RELEASED','QUARANTINED'):
                    attempt('retain-unsettled-canonical-use-quarantine',lambda:self.principal.quarantine(
                        self.operation,RuntimeError('Original full-resource control retains separate canonical effect obligation')))
        if self.operational_dispatch is not None:
            attempt('original-operational-dispatch-stop',self.operational_dispatch.stop)
        if self.peer_connection is not None:
            if self.requester_transport is None:
                attempt('request-peer-child-go-close',lambda:self.peer_connection.sendall(b'C'))
            else:
                response=canonical({'control':'ORIGINAL_RESOURCE_OWNER_DISPOSAL',
                    'prior_cleanup_errors':[_error(exc) for exc in errors]})+b'\n'
                def respond():
                    self.record('actual-source-owner-client-disposal-response-before-send',
                        {'raw_hex':response.hex()})
                    self.peer_connection.sendall(response)
                    self.record('actual-source-owner-client-disposal-response-return',
                        {'raw_hex':response.hex()})
                attempt('request-peer-source-owner-disposal-response',respond)
        if self.child is not None:
            attempt('actual-request-peer-child-wait',lambda:self.record('actual-request-peer-child-wait',
                {'returncode':self.child.wait(timeout=self.remaining())}))
            if self.requester_transport is not None:
                if self.child.returncode is None:
                    def interrupt_owned_source_owner():
                        import signal
                        receipt={'call':'pidfd_send_signal','pid':self.child.pid,
                            'pidfd':self.child_pidfd,'signal':signal.SIGINT,
                            'result':None,'error':None}
                        try:self.record('actual-source-owner-interrupt-before-call',receipt)
                        except BaseException as retention:errors.append(retention)
                        try:
                            require(self.child_pidfd is not None,
                                'RESOURCE_CONTROL_ACTUAL_HELD_OWNER_PIDFD_REQUIRED')
                            signal.pidfd_send_signal(self.child_pidfd,signal.SIGINT)
                            receipt['result']=0
                        except BaseException as exc:
                            receipt['error']=_error(exc);raise
                        finally:
                            try:self.record('actual-source-owner-interrupt-return',receipt)
                            except BaseException as retention:errors.append(retention)
                    attempt('actual-held-source-owner-interrupt',interrupt_owned_source_owner)
                    attempt('actual-source-owner-interrupt-wait',lambda:self.record(
                        'actual-source-owner-interrupt-wait',{'returncode':self.child.wait(
                            timeout=max(0,self.deadline-time.monotonic()))}))
                if self.child.returncode is None:
                    attempt('retain-actual-nested-source-owner-custody-unknown',lambda:self.record(
                        'actual-nested-source-owner-custody-unknown',
                        {'owner_pid':self.child.pid,'actor':self.requester_actor,
                         'actor_pidfd':self.requester_actor_pidfd,
                         'cause':'ORIGINAL_CASE_WAIT_UNKNOWN','outer_collector':'REQUIRED'}))
                else:attempt('actual-nested-source-owner-completion',self.complete_requester_owner)
        if self.request_scope is not None:attempt('original-request-context',lambda:self.request_scope.__exit__(None,None,None))
        if self.request is not None:attempt('original-request-peer',self.request.close)
        for name,obj in (('peer-connection',self.peer_connection),('peer-listener',self.peer_listener)):
            if obj is not None:attempt(name,obj.close)
        if self.peer_socket_identity is not None:
            path=Path(self.descriptor['endpoint']['path'])
            def remove_peer():
                info=path.lstat();require((info.st_dev,info.st_ino)==self.peer_socket_identity
                    and stat.S_ISSOCK(info.st_mode),'RESOURCE_CONTROL_PEER_ENDPOINT_IDENTITY_CHANGED')
                path.unlink()
            attempt('owned-peer-endpoint',remove_peer)
        if self.lease is not None:
            if rpc_quiescent:attempt('full-startup-owner',self.lease.close)
            else:self.record('actual-native-owner-retained-unknown',
                {'complete_lock_roster':list(self.lease.fds),'cause':'RPC_HANDLER_CUSTODY_UNKNOWN'})
        for state in self.drains:
            state['stop'].set()
            if state['started']:
                state['thread'].join(timeout=max(0,self.deadline-time.monotonic()))
            elif not state['close_attempted']:
                state['close_attempted']=True
                try:os.close(state['fd']);state['close']={'result':0}
                except BaseException as exc:state['close']={'error':_error(exc)};errors.append(exc)
            if state['started'] and state['thread'].is_alive():
                errors.append(RuntimeError('RESOURCE_CONTROL_RAW_PUMP_STILL_OWNED'))
                self.record('actual-raw-pump-retained-unknown',{'identity':state['identity']})
                continue
            if state['output'] is None:
                self.record('actual-raw-pump-formation-incomplete',{'identity':state['identity'],
                    'close':state['close'],'stream_end':None})
                continue
            def retain_output(state=state):
                raw=os.pread(state['output'].fileno(),os.fstat(state['output'].fileno()).st_size,0)
                self.record('actual-complete-read-output',{'identity':state['identity'],
                    'raw_hex':raw.hex(),'sha256':hashlib.sha256(raw).hexdigest(),
                    'stream_end':state['stream_end'],'error':state['error'],'close':state['close']})
            attempt('retain-owned-raw-output',retain_output)
            attempt('owned-raw-output-file',state['output'].close)
        if self.requester_actor_pidfd is not None:
            attempt('request-peer-nested-actor-pidfd',lambda:os.close(self.requester_actor_pidfd))
        if self.child_pidfd is not None:attempt('request-peer-pidfd',lambda:os.close(self.child_pidfd))
        if self.peer_raw_files:
            for stream in self.peer_raw_files:
                def retain_peer_output(stream=stream):
                    raw=os.pread(stream.fileno(),os.fstat(stream.fileno()).st_size,0)
                    self.record('actual-request-peer-raw-output',{'raw_hex':raw.hex(),
                        'sha256':hashlib.sha256(raw).hexdigest(),'stream_end':None})
                attempt('retain-request-peer-raw-output',retain_peer_output)
                attempt('request-peer-raw-file',stream.close)
        self.closed=not errors
        self.record('owner-control-cleanup',{'state':'CLOSED' if self.closed else 'UNKNOWN',
            'errors':[_error(exc) for exc in errors]})
        if self.closed:self.event_file.close()
        if errors:raise RuntimeError('RESOURCE_CONTROL_ACTUAL_CLEANUP_UNKNOWN') from errors[0]


def open_fixture(value,case):
    require(type(value) is dict and set(value)=={'schema','case','plan'}
        and value['schema']==SCHEMA and value['case']==case,
        'RESOURCE_CONTROL_EXACT_FACTORY_SELECTOR_REQUIRED')
    owner=OwnerResourceControl(value['plan'],case)
    try:return owner,owner.prepare()
    except BaseException as primary:
        owner.record('actual-owner-formation-primary-exception',_error(primary))
        try:owner.close()
        except BaseException as secondary:primary.add_note('Actual control cleanup: '+repr(secondary))
        raise
