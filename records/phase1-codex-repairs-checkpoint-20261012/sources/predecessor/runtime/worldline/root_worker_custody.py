"""Full exec-worker OFD handoff, not root-UID or packet authorization.

The native Root_Controller_Admission producer/ABI is a declared outside input.
An unavailable native producer is a named refusal before target owners close.
No live Controller/SQLite/thread state is forked. Every received FD is closed on
intake failure; the sender's copies and the counted root hold remain retained.
"""
from __future__ import annotations
import array,fcntl,os,socket,stat
from pathlib import Path
from .client_peer import KernelPeer,RequestPeer,UCRED
from .root_worker_codec import archive,restore_archive,raw_archive,raw_restore_archive
from .protected_startup import require,private_bytes,StartupRefusal
from .custody_subject_capture import actor_identity,fd_identity

SEALS=fcntl.F_SEAL_SEAL|fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_GROW|fcntl.F_SEAL_WRITE
DOMAIN='worldline.root-worker-custody-v1'

def identity(fd):
    s=os.fstat(fd)
    return {'device':s.st_dev,'inode':s.st_ino,'mode':s.st_mode,'uid':s.st_uid,
            'gid':s.st_gid,'fdinfo':Path('/proc/self/fdinfo/'+str(fd)).read_bytes()}

def named_identity(fd,path):
    # FD position/number in fdinfo may change after transfer. Complete raw
    # observations are retained separately; the named inode join is factual.
    named=Path(path).lstat();held=os.fstat(fd)
    require(stat.S_ISREG(named.st_mode) and stat.S_ISREG(held.st_mode)
        and named.st_uid==0 and not stat.S_IMODE(named.st_mode)&0o077
        and (named.st_dev,named.st_ino)==(held.st_dev,held.st_ino),
        'ROOT_WORKER_TRANSFERRED_LOCK_NAMED_IDENTITY_CHANGED')
    fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
    return identity(fd)

def _memfd(raw,*,name='worldline-full-root-custody'):
    require(name in ('worldline-full-root-custody','worldline-handoff-transfer-payload','worldline-handoff-transfer-trailer'),
        'ROOT_WORKER_SOURCE_SELECTED_MEMFD_PURPOSE_REQUIRED')
    fd=os.memfd_create(name,os.MFD_CLOEXEC|os.MFD_ALLOW_SEALING)
    try:
        with os.fdopen(os.dup(fd),'wb') as stream:
            stream.write(raw);stream.flush();os.fsync(stream.fileno())
        fcntl.fcntl(fd,fcntl.F_ADD_SEALS,SEALS)
        require(os.pread(fd,len(raw),0)==raw,'ROOT_WORKER_COMPLETE_SEALED_BYTES_CHANGED')
        return fd
    except BaseException:
        os.close(fd);raise

def _read_memfd(fd,*,original=False):
    before=os.fstat(fd);seals=fcntl.fcntl(fd,fcntl.F_GET_SEALS)
    require(stat.S_ISREG(before.st_mode) and before.st_uid==0
        and seals&SEALS==SEALS,'ROOT_WORKER_FULL_SEALED_CAPTURE_REQUIRED')
    with os.fdopen(os.dup(fd),'rb') as stream:
        stream.seek(0);raw=stream.read()
    after=os.fstat(fd)
    require(len(raw)==before.st_size and before==after,
            'ROOT_WORKER_FULL_CAPTURE_CHANGED')
    return (raw_restore_archive(raw) if original else restore_archive(raw)),raw

def _send_fd(channel,fd,receipts=None,source=None):
    rights=array.array('i',[fd]);raw=rights.tobytes()
    credentials=UCRED.pack(os.getpid(),os.getuid(),os.getgid())
    receipt={'call':'sendmsg','fd':channel.fileno(),'frame':b'F','rights':raw,
        'sender':credentials,'flags':socket.MSG_NOSIGNAL,'source':source,'parts':None,
        'controls':[(socket.SOL_SOCKET,socket.SCM_RIGHTS,raw),
            (socket.SOL_SOCKET,socket.SCM_CREDENTIALS,credentials)]}
    observed=channel_source(channel)
    receipt['args']={'body':b'F','rights':[fd],'channel':observed['identity'],
        'peer':observed['peer'],'flags':socket.MSG_NOSIGNAL}
    try:
        sent=channel.sendmsg([b'F'],[(socket.SOL_SOCKET,socket.SCM_RIGHTS,rights),
            (socket.SOL_SOCKET,socket.SCM_CREDENTIALS,credentials)],socket.MSG_NOSIGNAL)
    except OSError as error:
        receipt.update(result=-1,errno=error.errno)
        if receipts is not None:receipts.append(receipt)
        raise
    receipt.update(result=sent,errno=0)
    if receipts is not None:receipts.append(receipt)
    require(sent==1,'ROOT_WORKER_RIGHTS_SEND_UNKNOWN')
    return receipt

def _receive_fd(channel,receipts=None,source=None):
    descriptors=[]
    observed=channel_source(channel)
    try:
        body,controls,flags,_=channel.recvmsg(1,socket.CMSG_SPACE(array.array('i').itemsize)
            +socket.CMSG_SPACE(UCRED.size),socket.MSG_CMSG_CLOEXEC)
        credentials=[]
        malformed=False
        for level,kind,raw in controls:
            if level==socket.SOL_SOCKET and kind==socket.SCM_RIGHTS:
                rights=array.array('i')
                whole=len(raw)-len(raw)%rights.itemsize
                rights.frombytes(raw[:whole]);descriptors.extend(rights)
                malformed|=whole!=len(raw)
            elif level==socket.SOL_SOCKET and kind==socket.SCM_CREDENTIALS:
                credentials.append(raw)
            else:malformed=True
        receipt={'call':'recvmsg','fd':channel.fileno(),'frame':body,
            'rights':array.array('i',descriptors).tobytes(),'sender':credentials[0] if credentials else None,
            'controls':[(level,kind,bytes(raw)) for level,kind,raw in controls],
            'flags':flags,'input_flags':socket.MSG_CMSG_CLOEXEC,'result':len(body),
            'errno':0,'source':source,'parts':None}
        receipt['args']={'body':body,'rights':list(descriptors),'channel':observed['identity'],
            'peer':observed['peer'],'flags':socket.MSG_CMSG_CLOEXEC}
        receipt['sender_credentials']=credentials[0] if credentials else None;receipt['msg_flags']=flags
        if receipts is not None:receipts.append(receipt)
        require(body==b'F' and not flags&(socket.MSG_TRUNC|socket.MSG_CTRUNC)
            and not malformed and len(descriptors)==1 and len(credentials)==1
            and len(credentials[0])==UCRED.size,'ROOT_WORKER_RIGHTS_FRAME_MALFORMED')
        return descriptors.pop(),credentials[0]
    except OSError as error:
        failure={'call':'recvmsg','fd':channel.fileno(),'result':-1,'errno':error.errno,
            'source':source,'input_flags':socket.MSG_CMSG_CLOEXEC,'message':str(error)}
        if receipts is not None:receipts.append(failure)
        error.custody_receipts=receipts
        raise
    finally:
        for fd in descriptors:os.close(fd)

def channel_source(channel):
    require(type(channel) is socket.socket and channel.family==socket.AF_UNIX
        and channel.getsockopt(socket.SOL_SOCKET,socket.SO_TYPE)==socket.SOCK_STREAM,
        'ROOT_WORKER_ACTUAL_OWNED_CHANNEL_REQUIRED')
    channel.getpeername()
    return {'identity':identity(channel.fileno()),
        'peer':channel.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,UCRED.size)}

class CustodyOffer:
    """Exact actual front principal and held worker, never an input dictionary."""
    def __init__(self,principal,request,slot):
        from .protected_operations import CanonicalOperationPrincipal
        from .protected_root_worker import RootWorkerSlot
        require(type(principal) is CanonicalOperationPrincipal and type(request) is RequestPeer
            and type(slot) is RootWorkerSlot and slot.principal is principal
            and slot.request is request and principal.root_worker.slots.get(slot.operation) is slot,
            'ROOT_WORKER_ACTUAL_FRONT_PRINCIPAL_SLOT_REQUIRED')
        principal.intact();slot.intact()
        self.p,self.request,self.slot=principal,request,slot
        self.state='PREPARED';self.fds={};self.origins={};self.closed_owners=False
        self.owned_roster=None;self.send_receipts=[];self.close_receipts=[]
        self.subject_fds={};self.subject_send_receipts={};self.subject_service=None
        self.duplicate_receipts={}
        self.failure_observations=[];self.failure_capture=None
        self.original_peer=request.peer.duplicate()
        try:
            for path,fd in principal.lease.fds.items():
                self.fds[str(path)]=self.duplicate_lock(str(path),fd)
            for owner,leaf in ((principal.gate.issuer,'issuer.lock'),
                               (principal.gate.universe,'universe.lock')):
                path=str(owner.state/leaf)
                require(path not in self.fds,'ROOT_WORKER_LOCK_ROSTER_ALIAS')
                self.fds[path]=self.duplicate_lock(path,owner.lock_fd)
            journal=principal.root_worker.custody_journal
            require(str(journal.lock_path) not in self.fds,'ROOT_WORKER_JOURNAL_LOCK_ROSTER_ALIAS')
            self.fds[str(journal.lock_path)]=self.duplicate_lock(str(journal.lock_path),journal.lock_fd)
            require(slot.owned.worker_pidfd is not None,'ROOT_WORKER_ACTUAL_MEASURED_WORKER_PIDFD_REQUIRED')
            self.origins={'host_proc':os.open('/proc',os.O_RDONLY|os.O_DIRECTORY|os.O_CLOEXEC),
                'worker_pidfd':os.dup(slot.owned.worker_pidfd),'worker_namespace':os.dup(slot.owned.namespace_fd),
                'helper_pidfd':os.dup(slot.owned.helper_pidfd),'namespace_pidfd':os.dup(slot.owned.namespace_pidfd),
                'supervisor_channel':os.dup(slot.owned.connection.fileno())}
            self.locks={path:named_identity(fd,path) for path,fd in self.fds.items()}
            from .root_worker_subject_service import FrontSubjectService
            self.subject_service=FrontSubjectService(self)
            self.subject_fds={'request_service':self.subject_service.worker_channel.fileno(),
                'relay_service':self.subject_service.worker_relay_channel.fileno()}
            # Producer performs the actual complete selected native root call;
            # a prior RESERVED result or an assertion that Running exists fails.
            native=slot.authorize_root()
            from .root_owned_descriptor_roster import offer_roster
            self.owned_roster=offer_roster(self,native)
            from .root_worker_subject_transfer import prepare_offer
            subject_custody=prepare_offer(self)
            self.frame={'schema':DOMAIN,'installation':principal.lease.spec['installation_id'],
                'descriptor':principal.lease.descriptor_raw,'genesis':principal.lease.genesis_raw,
                'operation':slot.operation,'original_request':request.observation(),
                'original_native_use':principal._original_native_use(principal.journal.rows[slot.operation]),
                'root_native':native,'worker':slot.capture(),'locks':self.locks,
                'channel':channel_source(slot.channel),'source':principal.lease.source_lease.check(),
                'root_plan':{'path':str(principal.root_worker.path),'raw':principal.root_worker.plan_raw},
                'origin_descriptors':{name:identity(fd) for name,fd in self.origins.items()},
                'owned_descriptor_roster':self.owned_roster.frame,'subject_custody':subject_custody,
                'subject_pumps':{},
                'subject_descriptor_origins':{name:identity(fd) for name,fd in self.subject_fds.items()}}
            self.intent=slot.retain('ROOT_WORKER_CUSTODY_INTENT',self.frame)
        except BaseException as error:
            try:self.close_received_copies()
            except BaseException as cleanup:error.add_note('custody intake duplicate cleanup failed: '+repr(cleanup))
            raise
    def duplicate_lock(self,path,fd):
        from .root_worker_root_evidence import capture_lock_call
        value,receipt=capture_lock_call(self.slot.front.source_lease,'dup',{'fd':fd},lambda:os.dup(fd))
        self.duplicate_receipts[path]={'receipt':receipt,'ofd':receipt['ofd']}
        return value
    def close_received_copies(self):
        from .custody_subject_capture import close_descriptor
        if self.state!='PREPARED':
            self.slot.front.custody_journal.require_event(self.subject_service.returned_event)
        source=self.p.lease.source_lease.check()
        for path in tuple(self.fds):
            receipt=close_descriptor(self.fds[path],source);self.close_receipts.append(receipt)
            require(receipt['result']==0,'ROOT_WORKER_ESCROW_CLOSE_UNKNOWN');self.fds.pop(path)
        for name in tuple(self.origins):
            receipt=close_descriptor(self.origins[name],source);self.close_receipts.append(receipt)
            require(receipt['result']==0,'ROOT_WORKER_ESCROW_CLOSE_UNKNOWN');self.origins.pop(name)
        if self.owned_roster is not None:self.owned_roster.close()
        self.original_peer.close()
        if self.subject_service is not None and not self.subject_service.closed:
            if self.state=='PREPARED':self.subject_service.close_unclaimed()
            else:self.subject_service.close_escrow()
    def close_subject_escrow(self):
        service=self.subject_service
        if service is None or service.closed:return
        self.slot.front.custody_journal.require_event(service.returned_event)
        service.wake_closed_transport()
        service.close_escrow()
    def transfer(self):
        require(self.state=='PREPARED','ROOT_WORKER_CUSTODY_REPLAY_OR_UNKNOWN')
        self.slot.intact();self.slot.authorize_root()
        self.owned_roster.intact()
        from .root_worker_handoff_failure import prepare
        prepare(self)
        # First close all actual target owners while duplicated original OFDs
        # remain held. A failed close never sends a half-constructed owner.
        self.p.root_worker.close_front_owners(self)
        self.closed_owners=True;self.state='TRANSFER_INTENDED'
        self.owned_roster.retain_closed_front(self)
        payload=_memfd(raw_archive(self.frame),name='worldline-handoff-transfer-payload')
        try:
            source=self.p.lease.source_lease.check()
            _send_fd(self.slot.channel,payload,self.send_receipts,source)
            _send_fd(self.slot.channel,self.original_peer.descriptor(),self.send_receipts,source)
            for path in sorted(self.fds):_send_fd(self.slot.channel,self.fds[path],self.send_receipts,source)
            for name in sorted(self.origins):_send_fd(self.slot.channel,self.origins[name],self.send_receipts,source)
            self.owned_roster.send(self.slot.channel)
            for name in sorted(self.subject_fds):
                self.subject_send_receipts[name]=_send_fd(self.slot.channel,self.subject_fds[name],source=source)
            from .root_worker_subject_transfer import send_trailer
            from .root_worker_root_evidence import append,lock_receipts,seed
            actual=send_trailer(self)
            all_sent=list(self.send_receipts)+list(self.owned_roster.send_receipts.values())+list(self.subject_send_receipts.values())
            self.transfer_event=append(self.slot.front,self.slot.operation,'TRANSFER_SENT',
                {'frame':self.frame,'actual_send':actual},
                {'front_closed_event':self.front_closed_event['event_id'],
                 'locks':lock_receipts(self.slot.front,fds=self.fds),'seed':seed(self.slot.front),
                 'transfer':{'frame':self.frame,'actual_send':actual,'receipts':all_sent,
                     'descriptors':[{'fd':row['args']['rights'][0]} for row in all_sent],
                     'duplicates':tuple(self.duplicate_receipts.values())}})
            trailer=_memfd(raw_archive(dict(actual,transfer_event=self.transfer_event)),name='worldline-handoff-transfer-trailer')
            try:_send_fd(self.slot.channel,trailer,source=source)
            finally:os.close(trailer)
            self.slot.channel.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1)
            reported_fd=None;self.ofd_report_receipts=[]
            try:
                reported_fd,self.ofd_report_sender=_receive_fd(self.slot.channel,self.ofd_report_receipts,source)
                self.ofd_report,self.ofd_report_raw=_read_memfd(reported_fd,original=True)
                require(type(self.ofd_report) is dict
                    and self.ofd_report['schema']=='worldline.actual-root-ofd-report-v1',
                    'ROOT_WORKER_AUTHENTIC_FULL_OFD_REPORT_REQUIRED')
                self.slot.owned._sender_owned({'sender_credentials':self.ofd_report_sender})
                broker=self.subject_service._broker(self.ofd_report['transfer'])
                proof={'roles':tuple(broker['roles']),'source':self.slot.front.source_lease.check(),
                    'actor':actor_identity(self.slot.channel),'worker_host_pid':self.slot.owned.worker_host_pid,
                    'worker_pidfd':fd_identity(self.slot.owned.worker_pidfd)}
                self.sender_role_roster=proof
                response={'schema':'worldline.actual-root-ofd-broker-v1','transfer':broker,
                    'sender_role_roster':proof}
                broker_fd=_memfd(raw_archive(response))
                try:self.ofd_broker_send=_send_fd(self.slot.channel,broker_fd,source=source)
                finally:os.close(broker_fd)
            finally:
                if reported_fd is not None:os.close(reported_fd)
            self.state='SENT_UNACKNOWLEDGED'
        finally:os.close(payload)
        # Send/ACK/EOF never closes escrow or proves descendant/drain closure.
    def committed_ack(self,receipt):
        require(self.state=='SENT_UNACKNOWLEDGED','ROOT_WORKER_CUSTODY_ACK_OUT_OF_ORDER')
        self.slot.verify_ack(receipt,self.frame,self.intent)
        self.ack_event=self.slot.front.custody_journal.require_event(receipt)
        self.state='WORKER_OWNED'
        # Escrow OFDs remain held through actual worker/descendant closure.
        # Their presence gives the front no actuation right; its owners are
        # closed and its phase is WORKER_OWNED. Never reopen state on lost ACK.
        # Original peer is escrow too: release only at actual full closure.

class CustodyReceipt:
    """Intake of original OFDs; authority still requires genuine native replay."""
    @classmethod
    def receive(cls,channel,selected_native):
        # selected_native is the exact early-selected native wrapper instance,
        # validated by the root dispatcher, not a user callback or verdict.
        from .protected_root_worker import require_root_kernel
        require_root_kernel(selected_native)
        channel.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1)
        obj=object.__new__(cls);obj.channel=channel;obj.fds={};obj.origins={};obj.claimed=set()
        obj.peer=None;obj.kernel=selected_native;obj.closed=False
        obj.owned_roster=None;obj.receive_receipts=[];obj.close_receipts=[]
        obj.request_fd=None
        obj.subject_fds={};obj.subject_receive_receipts={};obj.descriptor_ofd_events={}
        payload=None;original=None;trailer=None
        source=selected_native.producer.source_lease.check()
        try:
            payload,sender=_receive_fd(channel,obj.receive_receipts,source);frame,raw=_read_memfd(payload,original=True)
            require(type(frame) is dict and set(frame)=={'schema','installation','descriptor','genesis',
                'operation','original_request','original_native_use','root_native','worker','locks','channel','source','root_plan','origin_descriptors','owned_descriptor_roster','subject_custody','subject_pumps','subject_descriptor_origins'}
                and frame['schema']==DOMAIN,'ROOT_WORKER_COMPLETE_CUSTODY_SCHEMA_REQUIRED')
            require(UCRED.unpack(sender)[1]==0,'ROOT_WORKER_NONROOT_CUSTODY_SENDER')
            original,again=_receive_fd(channel,obj.receive_receipts,source);require(again==sender,'ROOT_WORKER_CUSTODY_SENDER_CHANGED')
            peer=KernelPeer.capture_descriptor(original)
            obj.peer=RequestPeer.receive_descriptor(peer,frame['original_request'])
            obj.request_fd=original;original=None
            require(type(frame['locks']) is dict and frame['locks'],'ROOT_WORKER_LOCK_ROSTER_ABSENT')
            for path in sorted(frame['locks']):
                fd,again=_receive_fd(channel,obj.receive_receipts,source)
                obj.fds[path]=fd
                require(again==sender,'ROOT_WORKER_CUSTODY_SENDER_CHANGED')
                now=named_identity(fd,path);prior=frame['locks'][path]
                require({key:now[key] for key in ('device','inode','mode','uid','gid')}==
                    {key:prior[key] for key in ('device','inode','mode','uid','gid')},
                    'ROOT_WORKER_TRANSFERRED_OFD_IDENTITY_CHANGED')
            require(type(frame['origin_descriptors']) is dict and
                set(frame['origin_descriptors'])=={'host_proc','worker_pidfd','worker_namespace','helper_pidfd','namespace_pidfd','supervisor_channel'},
                'ROOT_WORKER_COMPLETE_KERNEL_ORIGIN_ROSTER_REQUIRED')
            for name in sorted(frame['origin_descriptors']):
                fd,again=_receive_fd(channel,obj.receive_receipts,source);obj.origins[name]=fd
                require(again==sender,'ROOT_WORKER_KERNEL_ORIGIN_SENDER_CHANGED')
                now=identity(fd);prior=frame['origin_descriptors'][name]
                require({key:now[key] for key in ('device','inode','mode','uid','gid')}==
                    {key:prior[key] for key in ('device','inode','mode','uid','gid')},
                    'ROOT_WORKER_ACTUAL_KERNEL_ORIGIN_DESCRIPTOR_CHANGED')
            from .root_owned_descriptor_roster import OwnedDescriptorRoster
            obj.owned_roster=OwnedDescriptorRoster.receive(channel,frame['owned_descriptor_roster'],sender,source=source)
            for name in sorted(frame['subject_descriptor_origins']):
                actual=[]
                fd,again=_receive_fd(channel,actual,source);obj.subject_fds[name]=fd
                obj.subject_receive_receipts[name]=actual[0]
                require(again==sender,'ROOT_WORKER_SUBJECT_DESCRIPTOR_SENDER_CHANGED')
                now=identity(fd);prior=frame['subject_descriptor_origins'][name]
                require({key:now[key] for key in ('device','inode','mode','uid','gid')}==
                    {key:prior[key] for key in ('device','inode','mode','uid','gid')},
                    'ROOT_WORKER_SUBJECT_DESCRIPTOR_REPLACED')
            obj.frame,obj.raw,obj.sender=frame,raw,sender
            trailer,again=_receive_fd(channel,source=source)
            require(again==sender,'ROOT_WORKER_TRANSCRIPT_SENDER_CHANGED')
            transcript,obj.transcript_raw=_read_memfd(trailer,original=True)
            from .root_worker_subject_transfer import capture_received
            capture_received(obj,transcript,source)
            reported={'schema':'worldline.actual-root-ofd-report-v1','transfer':obj.subject_intake['transfer'],
                'complete_received_roster':obj.owned_roster.intact(selected_native.producer)}
            reported_fd=_memfd(raw_archive(reported))
            try:obj.ofd_report_send=_send_fd(channel,reported_fd,source=source)
            finally:os.close(reported_fd)
            broker_fd=None;obj.ofd_broker_receipts=[]
            try:
                broker_fd,again=_receive_fd(channel,obj.ofd_broker_receipts,source)
                require(again==sender,'ROOT_WORKER_OFD_BROKER_SENDER_CHANGED')
                broker,obj.ofd_broker_raw=_read_memfd(broker_fd,original=True)
                require(type(broker) is dict and broker['schema']=='worldline.actual-root-ofd-broker-v1',
                    'ROOT_WORKER_AUTHENTIC_FULL_OFD_BROKER_REQUIRED')
                obj.ofd_broker=broker;obj.sender_role_roster=broker['sender_role_roster']
                obj.owned_roster.sender_role_roster=dict(obj.sender_role_roster,
                    roles=tuple(dict(row,role=row['role'].removeprefix('scoped/'))
                        for row in obj.sender_role_roster['roles'] if row['role'].startswith('scoped/')),
                    root_roles=obj.sender_role_roster['roles'])
            finally:
                if broker_fd is not None:os.close(broker_fd)
            selected_native.producer.bind_received_custody(obj)
            obj.admission=selected_native.replay_root_custody(frame,channel,obj.peer)
            obj.intact();return obj
        except BaseException:
            obj.close();raise
        finally:
            if payload is not None:os.close(payload)
            if original is not None:os.close(original)
            if trailer is not None:os.close(trailer)
    def intact(self):
        require(not self.closed and self.peer is not None,'ROOT_WORKER_CUSTODY_CLOSED')
        self.peer.observation()
        for path,fd in self.fds.items():named_identity(fd,path)
        # Full input/arenas/rosters/output and independently recaptured actual
        # worker/current-source are redecided; envelope/MAC/ACK alone grants none.
        self.admission=self.kernel.replay_root_custody(self.frame,self.channel,self.peer)
    def bind_live_owner(self,worker,material,native):
        from .protected_root_worker import RootWorkerProcess
        require(type(worker) is RootWorkerProcess and worker.custody is self
            and worker.lease.exec_custody is self and worker.request is self.peer,
                'ROOT_WORKER_REAL_FRESH_OWNER_CUSTODY_REQUIRED')
        require(worker.authority.decide(material)==native and native.status=='ROOT_READY_CONJUNCTION',
                'ROOT_WORKER_FRESH_RECONSTRUCTED_OWNER_NATIVE_REFUSED')
        # Typed actual owner plus full current native replay replaces only the
        # preconstructor intake guard. It never grants a second use or exchange.
        self.kernel=worker.authority;self.admission=native
        from .root_worker_root_evidence import lock_receipts,native_item
        retained=worker.retain_native('ROOT_WORKER_FULL_RECEIVED_ROSTER_REPORT',material,native)
        self.worker_roster_report={
            'original':{'complete_received_roster':self.subject_intake,
                'sender_transcript':self.send_transcript,'sender_role_roster':self.sender_role_roster},
            'evidence':{'transfer_event':self.send_transcript['transfer_event']['event_id'],
                'locks':lock_receipts(worker),
                'roster':{'received_locks':{path:identity(fd) for path,fd in self.fds.items()},
                    'origin_descriptors':{name:identity(fd) for name,fd in self.origins.items()},
                    'sender':self.sender,'channel':channel_source(self.channel),
                    'actual_rights':self.receive_receipts,'complete_owned_roster':self.owned_roster.intact(worker),
                    'sender_role_roster':self.sender_role_roster}},
            'native':(native_item('root-admission',retained['material'],retained['observation'],retained['provenance']),)}
    def activate_initial_request(self,worker):
        from .protected_root_worker import RootWorkerProcess
        from .root_worker_subject_custody import SubjectCustody
        from .root_worker_serving_peer import CrosswalkRequestPeer
        require(type(worker) is RootWorkerProcess and worker.custody is self,
            'ROOT_WORKER_ACTUAL_INITIAL_SUBJECT_OWNER_REQUIRED')
        worker.custody_journal.require_event(worker.custody_ack)
        source=self.subject_intake
        worker.custody_journal.require_event(self.frame['subject_custody']['intent'])
        native=worker.subject_service.native('ROOT_WORKER_INITIAL_REQUEST_INTAKE',subject_roster=self.owned_roster)
        transfer=dict(source['transfer'],roles=self.sender_role_roster['roles'],
            current_inventory=raw_archive(native[0]['provenance']['subject_capture']['inventory']))
        subject=SubjectCustody(worker,worker.operation,'REQUEST',
            source['original']['original_request']['observationId'])
        intake=subject.request_intake(source['original'],source['front_socket'],source['worker_socket'],
            transfer,native=native)
        worker.custody_journal.require_event(intake)
        peer=CrosswalkRequestPeer(self.peer,subject,source['original'],transfer,source['front_socket'],
            worker.subject_service,subject_roster=self.owned_roster,admission_native=native)
        worker.subject_service.request_holders.append(peer)
        from .root_worker_subject_output import RequestOutputEmitter
        def native_capture(cause,require_ready=True):
            current=worker.subject_service.native(cause,require_ready,subject_roster=self.owned_roster)
            return current+peer.retained_gates()[1]
        emitter=RequestOutputEmitter(worker,subject,source['original'],intake,native_capture=native_capture)
        admission={'peer':peer,'subject':subject,'intake':intake,'original':source['original'],
            'transfer':transfer,'emitter':emitter}
        worker.initial_request_admission=admission
        return admission
    def start_live_subject_service(self,worker):
        from .protected_root_worker import RootWorkerProcess
        require(type(worker) is RootWorkerProcess and worker.custody is self,
            'ROOT_WORKER_ACTUAL_SUBJECT_SERVICE_OWNER_REQUIRED')
        worker.custody_journal.require_event(worker.custody_ack)
        require(not hasattr(worker,'subject_service'),'ROOT_WORKER_SUBJECT_SERVICE_REPLAY')
        from .root_worker_subject_service import WorkerSubjectService
        worker.subject_service=WorkerSubjectService(worker)
        return worker.subject_service
    def roster(self,paths,authority_paths):
        self.intact();expected={str(path) for path in paths}|{str(path) for path in authority_paths}
        expected.add(str(self.kernel.producer.custody_journal.lock_path))
        require(set(self.fds)==expected,'ROOT_WORKER_COMPLETE_TRANSFERRED_LOCK_ROSTER_CHANGED')
    def claim(self,path):
        self.intact();path=str(path)
        require(path in self.fds and path not in self.claimed,'ROOT_WORKER_LOCK_DUPLICATE_OR_ABSENT')
        fd=os.dup(self.fds[path]);self.claimed.add(path);os.set_inheritable(fd,False);return fd
    def close(self):
        if getattr(self,'closed',False):return
        self.closed=True
        if self.peer is not None:self.peer.close()
        if self.request_fd is not None:os.close(self.request_fd);self.request_fd=None
        for path in tuple(self.fds):os.close(self.fds.pop(path))
        for name in tuple(self.origins):os.close(self.origins.pop(name))
        if self.owned_roster is not None:self.owned_roster.close()
        for name in tuple(self.subject_fds):os.close(self.subject_fds.pop(name))
