"""Complete factual descriptor custody; no liveness or permission in Python.

Every retained row keeps its own binding/scope. Original transport owners keep
wait, CLOSED, EOF, cancellation and drain duties; the transferred duplicates are
observation custody, not a reconstructed supervisor or a second actuation right.
The native classifier receives every row, and original ChildRootAdmission/X5
receive the complete captured packet/source. SCM frames remain original one-FD
frames, so this inventory has no descriptor-count or reservation-count ceiling.
"""
from dataclasses import replace
import errno,hashlib,os,select,socket,stat,struct,subprocess
from pathlib import Path
from .protected_startup import require
from .root_worker_custody import identity,named_identity,_send_fd,_receive_fd
from .root_worker_process_capture import RootProcessCapture,_read_at
import threading
from contextlib import ExitStack

_STDIN_COPY_LOCK_CREATION=threading.Lock()


def owned_stdin_copy_lock(slot):
    """Serialize actual acquisition and the original owner's writer-close cut."""
    with _STDIN_COPY_LOCK_CREATION:
        lock=getattr(slot,'_scoped_stdin_copy_lock',None)
        if lock is None:lock=threading.RLock();slot._scoped_stdin_copy_lock=lock
        return lock


def roster_stdin_copy_lock(owner,bound):
    """One actual owner/binding acquisition lock across every live roster alias."""
    with _STDIN_COPY_LOCK_CREATION:
        locks=getattr(owner,'_scoped_stdin_roster_locks',None)
        if locks is None:locks={};owner._scoped_stdin_roster_locks=locks
        key=bound.reservation
        if key not in locks:locks[key]=threading.RLock()
        return locks[key]

DOMAIN='worldline.complete-owned-scoped-descriptor-roster-v1'
IDENTITY_FIELDS=('device','inode','mode','uid','gid')
ROLES=('listener','supervisor_channel','worker_namespace','namespace_pidfd','helper_pidfd',
       'worker_pidfd','actor_pidfd','credential_receiver','custody_channel',
       'stdout_fd','stderr_fd','stdin_fd','retained_peer')
DESCRIPTOR_ROLES=ROLES+('helper_namespace',)


def _complete(value):
    from .protected_root_observation import complete
    return complete(value)


def source_bytes(value):
    """Complete genuine root raw archive, including ProcessObservation values."""
    from .root_worker_codec import raw_archive
    return raw_archive(value)


def capture_root_fact(producer,slot,row,blank,challenge):
    """Original factual _facts projection, with its actual root raw grammar."""
    from .protected_root_supervisor import OwnedRootSupervisor
    from .protected_resource_runtime import canonical,digest,restore_dto,ResourceProducerRefusal
    require(type(slot) is OwnedRootSupervisor and slot.principal is producer.operation_principal
        and producer.slots.get(row.bound.reservation.hex()) is slot and slot.row.bound==row.bound,
        'ROOT_ROSTER_GENUINE_ROOT_SOURCE_SLOT_REQUIRED')
    key=row.bound.reservation.hex();retained=producer.journal.rows.get(key)
    source={'reservation':key,'journal_head':producer.journal.head,'challenge':challenge,
        'events':retained['events'] if retained else [],'kernel':None}
    physical=replace(blank,retained=row.bound)
    if retained is None:return physical,source
    prepared=retained['prepared']
    require(restore_dto(prepared['payload']['row']).bound==row.bound,'RESOURCE_RETAINED_LAUNCH_BINDING_CHANGED')
    physical=replace(physical,intent=bytes.fromhex(digest(canonical(prepared))))
    if retained['phase']=='NEVER_DISPATCHED':return replace(physical,phase='NEVER_DISPATCHED'),source
    try:captured=slot.observe()
    except (ResourceProducerRefusal,OSError) as error:
        source['kernel']={'refusal':str(error)};return physical,source
    source['kernel']=captured['raw'];physical=replace(physical,**captured['native_fields'])
    tree=dict(source);raw=source_bytes(tree)
    source['head_tree']=tree;source['head_preimage']=raw;source['head_encoding']='ROOT_RAW_ARCHIVE'
    return replace(physical,observation_head=hashlib.sha256(raw).digest()),source


def descriptor_identity(fd):
    """Stable kernel object identity AND complete current raw FD observation."""
    return identity(fd)


def require_descriptor_identity(fd,prior):
    now=descriptor_identity(fd)
    require({key:now[key] for key in IDENTITY_FIELDS}==
            {key:prior[key] for key in IDENTITY_FIELDS},'ROOT_ROSTER_KERNEL_DESCRIPTOR_REPLACED')
    return now


def _bytes(fd):
    # pread never changes a shared OFD position; retain the whole actual file.
    parts=[];position=0
    while True:
        raw=os.pread(fd,65536,position)
        if not raw:return b''.join(parts)
        parts.append(raw);position+=len(raw)


def _descriptors(slot):
    result={role:None for role in ROLES}
    for role,attribute in (('worker_namespace','namespace_fd'),('namespace_pidfd','namespace_pidfd'),
            ('helper_pidfd','helper_pidfd'),('worker_pidfd','worker_pidfd'),('actor_pidfd','actor_pidfd'),
            ('stdout_fd','stdout_fd'),('stderr_fd','stderr_fd'),('stdin_fd','stdin_fd')):
        result[role]=getattr(slot,attribute,None)
    for role,attribute in (('listener','listener'),('supervisor_channel','connection'),
            ('credential_receiver','credential_receiver'),('custody_channel','custody_channel')):
        channel=getattr(slot,attribute,None)
        result[role]=None if channel is None else channel.fileno()
    peer=getattr(slot,'retained_peer',None)
    if peer is not None:result['retained_peer']=peer.peer.descriptor()
    return result


def _owner_kind(slot,front,producer):
    from .protected_root_supervisor import OwnedRootSupervisor
    from .protected_scoped_supervisor_v3 import OwnedSupervisorV3
    from .protected_resource_runtime import OwnedSupervisor
    if type(slot) is OwnedRootSupervisor:
        actual=slot.front
        require(slot.principal is producer.operation_principal and actual.principal is slot.principal and
                actual.slots.get(slot.operation) is not None and
                actual.slots[slot.operation].owned is slot,'ROOT_ROSTER_ROOT_OWNER_CHANGED')
        return 'ROOT'
    require(type(slot) in (OwnedSupervisorV3,OwnedSupervisor) and slot.principal is producer,
            'ROOT_ROSTER_ACTUAL_SELECTED_SUPERVISOR_REQUIRED')
    return 'ACTOR_V3' if type(slot) is OwnedSupervisorV3 else 'SUPERVISOR_V1'


def prepare_roster_stdin_eof(roster,owner,bound,original_writer,*,descriptor=None):
    """Acquire a full pre-close image; this function neither closes nor authorizes."""
    from .custody_subject_capture import actor_identity,fd_identity,kcmp
    from .root_worker_codec import raw_archive,raw_restore_archive
    require(type(roster) is OwnedDescriptorRoster and not roster.closed,
        'ROOT_ROSTER_EOF_ACTUAL_CUSTODY_REQUIRED')
    source_name='row/'+bound.reservation.hex()+'/stdin_fd'
    name=source_name if descriptor is None else descriptor
    if name not in roster.fds:return None
    matches=[item for item in roster.frame['rows'] if item['row'].bound==bound]
    require(len(matches)==1,'ROOT_ROSTER_EOF_ACTUAL_BOUND_ROW_REQUIRED');row=matches[0]
    if name==source_name:
        require(row['roles']['stdin_fd']==name,'ROOT_ROSTER_EOF_ACTUAL_WRITER_ROLE_REQUIRED')
    else:
        origin=roster.frame.get('writer_aliases',{}).get(name)
        require(origin is not None and origin['bound']==bound and origin['scope']==row['row'].scope
            and origin['role']=='stdin_fd' and origin['source_descriptor']==source_name,
            'ROOT_ROSTER_EOF_ACTUAL_WRITER_ALIAS_REQUIRED')
    source=owner.source_lease.check();actor=actor_identity();fd=roster.fds[name]
    before=raw_restore_archive(raw_archive(roster.retained_inventory(owner)))
    alias={'fd':fd,'identity':fd_identity(fd),'kcmp':None,'descriptor':name}
    if all(original_writer['actor'][key]==actor[key] for key in ('pid','boot','start_tick','credentials')):
        alias['kcmp']=kcmp(os.getpid(),os.getpid(),original_writer['fd'],fd,source)
    return {'bound':bound,'scope':row['row'].scope,'role':'stdin_fd','before_inventory':before,
        'actor':actor,'source':source,'original_writer':original_writer,'alias':alias}


def prepare_roster_stdin_eofs(roster,owner,bound,original_writer):
    """Snapshot every factual writer import before any original or copied close."""
    names=['row/'+bound.reservation.hex()+'/stdin_fd']
    names.extend(name for name,origin in roster.frame.get('writer_aliases',{}).items()
        if origin['bound']==bound)
    contexts=[]
    for name in names:
        context=prepare_roster_stdin_eof(roster,owner,bound,original_writer,descriptor=name)
        if context is not None:contexts.append(context)
    return tuple(contexts)


def complete_roster_stdin_eof(roster,owner,context,original_close,*,closed=None):
    """Close only the actual acquired writer copy, retaining its entire lineage."""
    from .custody_subject_capture import syscall
    if context is None:return None
    name=context['alias'].get('descriptor','row/'+context['bound'].reservation.hex()+'/stdin_fd')
    require(name in roster.fds and roster.fds[name]==context['alias']['fd'],
        'ROOT_ROSTER_EOF_COPIED_DESCRIPTOR_CHANGED')
    require(original_close['call']=='close'
        and original_close['args']['fd']==context['original_writer']['fd'],
        'ROOT_ROSTER_EOF_ACTUAL_ORIGINAL_CLOSE_REQUIRED')
    context['original_close']=original_close
    closed={} if closed is None else closed;fd=roster.fds[name]
    if fd in closed:
        receipt=closed[fd]
        require(receipt['call']=='close' and receipt['args']['fd']==fd and receipt['errno']==0,
            'ROOT_ROSTER_EOF_SHARED_ACTUAL_CLOSE_CHANGED')
    else:
        require_descriptor_identity(fd,context['alias']['identity'])
        _,receipt=syscall(owner,'close',{'fd':fd,'role':name},lambda:os.close(fd))
        context['close']=receipt
        require(receipt['errno']==0,'ROOT_ROSTER_EOF_COPIED_CLOSE_FAILED')
        closed[fd]=receipt
    record={**context,'original_close':original_close,'close':receipt}
    roster.fds.pop(name)
    frame=dict(roster.frame);frame['descriptors']=dict(frame['descriptors']);frame['descriptors'].pop(name)
    frame['original_roles']=tuple(item for item in frame['original_roles'] if item['role']!=name)
    frame['extensions']=tuple(item for item in frame.get('extensions',()) if item['descriptor']!=name)
    frame['writer_aliases']={key:value for key,value in frame.get('writer_aliases',{}).items() if key!=name}
    rows=[]
    for item in frame['rows']:
        if item['row'].bound==context['bound'] and item['roles']['stdin_fd']==name:
            item=dict(item);item['roles']=dict(item['roles']);item['roles']['stdin_fd']=None
        rows.append(item)
    frame['rows']=tuple(rows)
    frame['closed_roles']={**frame.get('closed_roles',{}),name:record}
    frame['retained_roles']={key:value for key,value in frame.get('retained_roles',{}).items() if key!=name}
    frame.pop('evolution',None);frame.pop('reconstruction',None)
    if hasattr(roster,'reconstruction'):del roster.reconstruction
    for attr in ('send_receipts','receive_receipts','sender_receipts'):
        receipts=getattr(roster,attr,None)
        if receipts is not None:setattr(roster,attr,{key:value for key,value in receipts.items() if key!=name})
    broker=getattr(roster,'sender_role_roster',None)
    if broker is not None:
        roster.sender_role_roster={**broker,'roles':tuple(item for item in broker['roles'] if item['role']!=name)}
    roster.frame=frame
    return record


def prepare_owned_stdin_eof(slot,*,original_writer=None):
    from .custody_subject_capture import actor_identity,fd_identity
    require(slot.stdin_fd is not None,'ROOT_ROSTER_EOF_ACTUAL_ORIGINAL_WRITER_REQUIRED')
    owner=getattr(slot,'front',None)
    if owner is None:
        principal=slot.principal.lease.canonical_operation_principal
        owner=getattr(principal,'root_worker_process',None) or getattr(principal,'root_worker',None)
    require(owner is not None,'ROOT_ROSTER_EOF_ACTUAL_WRITER_OWNER_REQUIRED')
    current_writer={'fd':slot.stdin_fd,'identity':fd_identity(slot.stdin_fd),
        'actor':actor_identity(),'source':owner.source_lease.check()}
    if original_writer is None:original_writer=current_writer
    else:
        require(type(original_writer) is dict and original_writer['fd']==current_writer['fd']
            and all(original_writer['identity'][key]==current_writer['identity'][key] for key in IDENTITY_FIELDS)
            and all(original_writer['actor'][key]==current_writer['actor'][key]
                for key in ('pid','boot','start_tick','credentials'))
            and all(original_writer['source'][key]==current_writer['source'][key]
                for key in ('envelope_path','envelope_bytes_hex','interpreter')),
            'ROOT_ROSTER_EOF_ACTUAL_PREFLIGHT_WRITER_CHANGED')
    contexts=[];seen=set()
    for roster in getattr(slot,'_scoped_stdin_copy_rosters',()):
        if id(roster) in seen or roster.closed:continue
        seen.add(id(roster))
        roster_owner=roster.front or getattr(roster,'reconstruction_owner',None)
        require(roster_owner is not None,'ROOT_ROSTER_EOF_COPY_ACTUAL_OWNER_ABSENT')
        contexts.extend((roster,roster_owner,context)
            for context in prepare_roster_stdin_eofs(roster,roster_owner,slot.row.bound,original_writer))
    return {'bound':slot.row.bound,'original_writer':original_writer,
        'current_writer':current_writer,'copies':tuple(contexts)}


def complete_owned_stdin_eof(slot,contexts,original_close):
    require(contexts['bound']==slot.row.bound,'ROOT_ROSTER_EOF_ORIGINAL_BOUND_CHANGED')
    records=[];failure=None;closed={}
    for roster,owner,context in contexts['copies']:
        try:records.append(complete_roster_stdin_eof(roster,owner,context,original_close,closed=closed))
        except BaseException as error:
            if failure is None:failure=error
            else:failure.add_note('additional actual stdin observation-copy close failed: '+repr(error))
    contexts['completed']=tuple(records)
    contexts['close_failures']=tuple({key:value for key,value in context.items()}
        for _roster,_owner,context in contexts['copies'] if 'close' in context and context['close']['errno']!=0)
    if failure is not None:raise failure
    return tuple(records)
def adopt_subject_role_receipts(owner,full_original_frame,actual_fds,actual_receive_receipts,
        header_sender,full_original_transcript,*,sender_role_roster):
    """Enroll already-received real rights; never duplicate or synthesize a receipt."""
    from .protected_root_worker import RootWorkerProcess
    from .root_worker_codec import raw_archive,raw_restore_archive
    from .canonical_actor_execution import scoped_components
    require(type(owner) is RootWorkerProcess and type(full_original_frame) is bytes
        and type(actual_fds) is dict and type(actual_receive_receipts) is dict
        and type(header_sender) is bytes and len(header_sender)==12
        and type(full_original_transcript) is dict and type(sender_role_roster) in (tuple,list),
        'ROOT_ROSTER_ACTUAL_SUBJECT_ROLE_DELIVERY_REQUIRED')
    frame=raw_restore_archive(full_original_frame)
    require(type(frame) is dict and frame.get('schema')==DOMAIN
        and type(frame.get('descriptors')) is dict
        and set(actual_fds)==set(frame['descriptors'])==set(actual_receive_receipts),
        'ROOT_ROSTER_COMPLETE_SUBJECT_ROLE_DELIVERY_CHANGED')
    sent=full_original_transcript.get('send')
    require(full_original_transcript.get('kind')=='SEND_TRANSCRIPT'
        and type(sent) in (tuple,list) and len(sent)==len(actual_fds),
        'ROOT_ROSTER_ACTUAL_SUBJECT_SEND_TRANSCRIPT_REQUIRED')
    obj=object.__new__(OwnedDescriptorRoster);obj.frame=frame;obj.fds=actual_fds
    obj.closed=False;obj.received=True;obj.front=None;obj.producer=None;obj.slots={}
    obj.escrow=True;obj.reconstruction_owner=owner;obj.send_receipts={}
    obj.receive_receipts={};obj.sender_receipts={};obj.sender_role_roster=None
    obj.subject_transport={'original_frame':full_original_frame,'header_sender':header_sender,
        'original_transcript':full_original_transcript,'original_sender_roles':sender_role_roster,
        'original_receive_receipts':actual_receive_receipts}
    obj.subject_transport['root_binding']={'operation':owner.operation,'frame':raw_archive(owner.custody.frame)}
    for name,send in zip(sorted(actual_fds),sent):
        received=actual_receive_receipts[name]
        require(type(send) is dict and type(received) is dict and received['sender']==header_sender,
            'ROOT_ROSTER_SUBJECT_SCM_RECEIPT_SENDER_CHANGED')
        require_descriptor_identity(actual_fds[name],frame['descriptors'][name])
        obj.sender_receipts[name]=send
        obj.receive_receipts[name]=(received,)
    obj._shape()
    producer=scoped_components(owner.principal)
    with ExitStack() as acquisitions:
        for entry in sorted(frame['rows'],key=lambda item:item['row'].bound.reservation):
            acquisitions.enter_context(roster_stdin_copy_lock(owner,entry['row'].bound))
        for entry in frame['rows']:
            slot=producer.slots.get(entry['row'].bound.reservation.hex())
            if slot is None:continue
            require(slot.row.bound==entry['row'].bound,'ROOT_ROSTER_SUBJECT_ACTUAL_SLOT_BOUND_CHANGED')
            acquisitions.enter_context(owned_stdin_copy_lock(slot))
            holders=getattr(slot,'_scoped_stdin_copy_rosters',None)
            if holders is None:holders=[];slot._scoped_stdin_copy_rosters=holders
            holders.append(obj)
        holders=getattr(owner,'_scoped_capture_rosters',None)
        if holders is None:holders=[];owner._scoped_capture_rosters=holders
        holders.append(obj)
    return obj




class OwnedDescriptorRoster:
    """Front-owned escrow or received read-only observation custody."""
    @classmethod
    def capture(cls,front,packet,sources):
        return cls._capture_actual(front,packet,sources)
    @classmethod
    def refresh(cls,owner,packet,sources,retained):
        from .protected_root_worker import RootWorkerFront,RootWorkerProcess
        require(type(owner) in (RootWorkerFront,RootWorkerProcess) and type(retained) is cls,
            'ROOT_ROSTER_ACTUAL_CURRENT_OWNER_REFRESH_REQUIRED')
        return cls._capture_actual(owner,packet,sources,retained)
    @classmethod
    def _capture_actual(cls,front,packet,sources,retained=None):
        from .protected_root_worker import RootWorkerFront,RootWorkerProcess
        from .canonical_actor_execution import scoped_components
        from . import resource_scoped_run_ledger as S
        require(type(front) in (RootWorkerFront,RootWorkerProcess) and type(packet) is S.ScopedPacket,
                'ROOT_ROSTER_ACTUAL_FRONT_AND_COMPLETE_PACKET_REQUIRED')
        producer=scoped_components(front.principal)
        require(len(packet.rows)==len(packet.observed)==len(packet.facts)==len(sources),
                'ROOT_ROSTER_COMPLETE_NATIVE_ROW_CORRESPONDENCE_REQUIRED')
        obj=object.__new__(cls);obj.fds={};obj.closed=False;obj.front=front;obj.producer=producer
        obj.slots={};obj.received=False;obj.escrow=False
        obj.send_receipts={};obj.receive_receipts={};obj.sender_receipts=None
        if retained is not None:previous=retained.retained_inventory(front)
        else:previous=None
        obj.local_registry=[];obj.reconstruction_owner=front
        acquisitions=ExitStack()
        try:
            for bound in sorted((row.bound for row in packet.rows),key=lambda value:value.reservation):
                acquisitions.enter_context(roster_stdin_copy_lock(front,bound))
            for key,slot in sorted(producer.slots.items()):
                if any(row.bound.reservation.hex()==key for row in packet.rows):
                    acquisitions.enter_context(owned_stdin_copy_lock(slot))
            obj.fds['host_proc']=(os.dup(retained.fds['host_proc']) if retained is not None
                else os.open('/proc',os.O_RDONLY|os.O_DIRECTORY|os.O_CLOEXEC))
            rows=[];retained_roles={}
            for row,native,fact,source in zip(packet.rows,packet.observed,packet.facts,sources):
                key=row.bound.reservation.hex();slot=producer.slots.get(key)
                require(native.bound==fact.retained==row.bound,'ROOT_ROSTER_NATIVE_ROW_BINDING_CHANGED')
                if slot is None:
                    old=[] if retained is None else [entry for entry in retained.frame['rows'] if entry['row'].bound==row.bound]
                    if old and old[0]['kind'] is not None:
                        entry=dict(old[0]);entry['row']=row;entry['source']=source
                        for name in tuple(value for role,value in entry['roles'].items() if role!='cgroup' and value is not None):
                            obj.fds[name]=os.dup(retained.fds[name])
                        cg=entry['roles']['cgroup']
                        if cg is not None:obj.fds[cg['descriptor']]=os.dup(retained.fds[cg['descriptor']])
                        rows.append(entry);continue
                    require(native.observed!='LIVE','ROOT_ROSTER_LIVE_ROW_WITHOUT_OWNED_DESCRIPTORS')
                    rows.append({'row':row,'kind':None,'roles':None,'held':None,'dispatch':None,
                        'closed':None,'outer':None,'closed_event':None,'source':source})
                    continue
                require(slot.row.bound==row.bound and key not in obj.slots,'ROOT_ROSTER_OWNED_ROW_ALIAS')
                obj.slots[key]=slot;kind=_owner_kind(slot,front,producer);roles={}
                registry={'bound':row.bound,'kind':kind,'descriptors':{}};obj.local_registry.append(registry)
                for role,fd in _descriptors(slot).items():
                    if fd is None:roles[role]=None;registry['descriptors'][role]=None;continue
                    name='row/'+key+'/'+role
                    try:obj.fds[name]=os.dup(fd)
                    except OSError as error:
                        if native.observed=='LIVE' or error.errno!=errno.EBADF:raise
                        roles[role]=None;source=dict(source)
                        absent=dict(source.get('descriptor_absence',{}))
                        absent[role]={'call':'dup','fd':fd,'result':-1,'errno':error.errno,'message':str(error)}
                        source['descriptor_absence']=absent
                        registry['descriptors'][role]={'fd':fd,'absence':absent[role]}
                    else:
                        roles[role]=name
                        from .custody_subject_capture import kcmp
                        registry['descriptors'][role]={'fd':fd,'identity':identity(fd),'descriptor':name,
                            'current_fd':obj.fds[name],'kcmp':kcmp(os.getpid(),os.getpid(),fd,obj.fds[name],front.source_lease.check())}
                roles['helper_namespace']=None
                helper=roles['helper_pidfd']
                if helper is not None:
                    from .protected_root_supervisor import OwnedRootSupervisor
                    if OwnedRootSupervisor.pidfd_state(obj.fds[helper])==b'PIDFD_LIVE':
                        from .root_worker_host_peer import host_fdinfo
                        helper_pid,_raw=host_fdinfo(obj.fds['host_proc'],obj.fds[helper])
                        name='row/'+key+'/helper_namespace'
                        obj.fds[name]=(os.dup(retained.fds[name]) if retained is not None and name in retained.fds else
                            os.open(str(helper_pid)+'/ns/pid',os.O_RDONLY|os.O_CLOEXEC,dir_fd=obj.fds['host_proc']))
                        roles['helper_namespace']=name
                cg=fact.cgroup
                if cg is None and slot.held is not None:
                    properties=slot.held['properties']
                    cg=properties[b'ControlGroup'] if kind=='ROOT' else bytes.fromhex(properties['ControlGroup'])
                roles['cgroup']=None
                if cg is not None:
                    require(cg.startswith(b'/') and not any(word in (b'.',b'..') for word in cg.split(b'/')),
                            'ROOT_ROSTER_CGROUP_PATH_INVALID')
                    path=Path('/sys/fs/cgroup')/os.fsdecode(cg).lstrip('/');name='row/'+key+'/cgroup'
                    flags=os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC
                    try:obj.fds[name]=(os.dup(retained.fds[name]) if retained is not None and name in retained.fds else os.open(path,flags))
                    except OSError as error:
                        if native.observed=='LIVE':raise
                        source=dict(source);source['actual_cgroup_open']={'call':'open','path':str(path),
                            'flags':flags,'result':-1,'errno':error.errno,'message':str(error)}
                    else:roles['cgroup']={'descriptor':name,'path':str(path)}
                require(native.observed!='LIVE' or all(roles[name] is not None for name in
                    ('supervisor_channel','worker_namespace','namespace_pidfd','helper_pidfd','cgroup')),
                    'ROOT_ROSTER_LIVE_PHYSICAL_DESCRIPTOR_ABSENT')
                rows.append({'row':row,'kind':kind,'roles':roles,'held':slot.held,'dispatch':slot.dispatch,
                    'closed':slot.closed,'outer':getattr(slot,'outer',None),
                    'closed_event':getattr(slot,'closed_event',None),'source':source})
            require(set(producer.slots)==set(obj.slots),'ROOT_ROSTER_OWNED_SLOT_OUTSIDE_COMPLETE_LEDGER')
            files=[]
            for path,(role,_mode,_expected) in sorted(front.source_lease.files.items()):
                raw=front.source_lease.file(path,(role,));name='source/'+path
                fd=(os.dup(retained.fds[name]) if retained is not None and name in retained.fds else
                    os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC));obj.fds[name]=fd
                require(_bytes(fd)==raw,'ROOT_ROSTER_PINNED_SOURCE_BYTES_CHANGED')
                files.append({'path':path,'role':role,'descriptor':name,'raw':raw})
            actual_locks={str(path):fd for path,fd in front.lease.fds.items()}
            for authority,leaf in ((front.principal.gate.issuer,'issuer.lock'),
                                   (front.principal.gate.universe,'universe.lock')):
                path=str(authority.state/leaf)
                require(path not in actual_locks,'ROOT_ROSTER_LEASE_LOCK_ALIAS');actual_locks[path]=authority.lock_fd
            journal=front.custody_journal;path=str(journal.lock_path)
            require(path not in actual_locks,'ROOT_ROSTER_JOURNAL_LOCK_ALIAS');actual_locks[path]=journal.lock_fd
            locks=[]
            for path,fd in actual_locks.items():
                name='lease/'+path;obj.fds[name]=os.dup(fd)
                locks.append({'path':path,'descriptor':name,'identity':named_identity(obj.fds[name],path)})
            locks=tuple(locks)
            if retained is not None:
                for extension in retained.frame.get('extensions',()):
                    name=extension['descriptor'];obj.fds[name]=os.dup(retained.fds[name])
                for name,fd in retained.fds.items():
                    if name in obj.fds:continue
                    inherited=retained.frame.get('retained_roles',{}).get(name)
                    if inherited is not None:retained_roles[name]=dict(inherited)
                    else:
                        matches=[(entry,role) for entry in retained.frame['rows'] if entry['roles'] is not None
                            for role,value in entry['roles'].items()
                            if (value['descriptor'] if role=='cgroup' and value is not None else value)==name]
                        require(len(matches)==1,'ROOT_ROSTER_RETAINED_DESCRIPTOR_ORIGIN_REQUIRED')
                        entry,role=matches[0]
                        retained_roles[name]={'bound':entry['row'].bound,'scope':entry['row'].scope,'role':role}
                    obj.fds[name]=os.dup(fd)
            from .custody_subject_capture import actor_identity,original_roles
            from .scoped_capture_namespace_source import capture_actor_namespace
            actor=actor_identity()
            selected=(front.slots.get(packet.request.original.operation_id.hex()) if type(front) is RootWorkerFront else None)
            worker=None if selected is None or selected.owned.worker_pidfd is None else identity(selected.owned.worker_pidfd)
            if type(front) is RootWorkerProcess:worker=identity(front.custody.origins['worker_pidfd'])
            original=original_roles({name:obj.fds[name] for name in sorted(obj.fds)},front.source_lease.check(),
                actor,worker,{item['descriptor']:item['path'] for item in locks})
            obj.frame={'schema':DOMAIN,'packet':packet,'rows':tuple(rows),'source_files':tuple(files),
                'source':front.source_lease.check(),'lease_locks':locks,'installation':front.spec,
                'resource_config':producer.cfg,'descriptors':{name:identity(fd) for name,fd in obj.fds.items()},
                'original_roles':original,'sender_actor_namespace':capture_actor_namespace(actor,front.source_lease.check())}
            if retained_roles:obj.frame['retained_roles']=retained_roles
            if retained is not None and 'closed_roles' in retained.frame:
                obj.frame['closed_roles']=retained.frame['closed_roles']
            if retained is not None and 'extensions' in retained.frame:
                obj.frame['extensions']=retained.frame['extensions']
            if retained is not None and 'writer_aliases' in retained.frame:
                obj.frame['writer_aliases']=retained.frame['writer_aliases']
            if retained is not None:
                from .custody_subject_capture import kcmp
                source=front.source_lease.check();copies=[]
                for name in sorted(set(retained.fds)&set(obj.fds)):
                    copies.append({'role':name,'origin_fd':retained.fds[name],'current_fd':obj.fds[name],
                        'origin':identity(retained.fds[name]),'current':identity(obj.fds[name]),
                        'kcmp':kcmp(os.getpid(),os.getpid(),retained.fds[name],obj.fds[name],source)})
                obj.frame['evolution']={'original_inventory':previous,'copies':tuple(copies),
                    'local_registry':tuple(obj.local_registry),'source':source}
            for slot in obj.slots.values():
                if slot.stdin_fd is not None:
                    holders=getattr(slot,'_scoped_stdin_copy_rosters',None)
                    if holders is None:holders=[];slot._scoped_stdin_copy_rosters=holders
                    holders.append(obj)
            obj.intact(front);return obj
        except BaseException:
            obj.close();raise
        finally:
            acquisitions.close()

    @classmethod
    def receive(cls,channel,frame,sender,source=None):
        require(type(frame) is dict and set(frame)-{'extensions','reconstruction','evolution','retained_roles','closed_roles','writer_aliases'}=={'schema','packet','rows','source_files','source',
            'lease_locks','installation','resource_config','descriptors','original_roles','sender_actor_namespace'} and frame['schema']==DOMAIN,
            'ROOT_ROSTER_COMPLETE_DESCRIPTOR_FRAME_REQUIRED')
        obj=object.__new__(cls);obj.frame=frame;obj.fds={};obj.closed=False;obj.received=True
        obj.front=None;obj.producer=None;obj.slots={};obj.escrow=True
        obj.send_receipts={};obj.receive_receipts={};obj.sender_receipts=None
        try:
            for name in sorted(frame['descriptors']):
                receipts=[];fd,again=_receive_fd(channel,receipts,source);obj.fds[name]=fd
                obj.receive_receipts[name]=tuple(receipts)
                require(again==sender,'ROOT_ROSTER_SCM_SENDER_CHANGED')
                require_descriptor_identity(fd,frame['descriptors'][name])
            obj._shape();return obj
        except BaseException:
            obj.close();raise

    def _shape(self):
        from . import resource_scoped_run_ledger as S
        packet=self.frame['packet'];entries=self.frame['rows']
        require(type(packet) is S.ScopedPacket and type(entries) is tuple and
                tuple(item['row'] for item in entries)==packet.rows,'ROOT_ROSTER_COMPLETE_ROWS_CHANGED')
        require(len({row.bound.reservation for row in packet.rows})==len(packet.rows),
                'ROOT_ROSTER_RESERVATION_ALIAS')
        require(len(packet.rows)==len(packet.observed)==len(packet.facts),
                'ROOT_ROSTER_COMPLETE_NATIVE_ROW_LENGTHS_CHANGED')
        expected={'host_proc'}
        for item,native in zip(entries,packet.observed):
            require(set(item)=={'row','kind','roles','held','dispatch','closed','outer','closed_event','source'},
                    'ROOT_ROSTER_ROW_SCHEMA_CHANGED')
            roles=item['roles']
            if item['kind'] is None:
                require(roles is None and native.observed!='LIVE','ROOT_ROSTER_LIVE_UNOWNED_ROW')
                continue
            require(item['kind'] in ('ROOT','ACTOR_V3','SUPERVISOR_V1') and
                    type(roles) is dict and set(roles)==set(DESCRIPTOR_ROLES)|{'cgroup'},'ROOT_ROSTER_ROLE_SCHEMA_CHANGED')
            require(native.observed!='LIVE' or all(roles[name] is not None for name in
                ('supervisor_channel','worker_namespace','namespace_pidfd','helper_pidfd','cgroup')),
                'ROOT_ROSTER_LIVE_PHYSICAL_DESCRIPTOR_ABSENT')
            for role in DESCRIPTOR_ROLES:
                name=roles[role]
                if name is not None:
                    require(name=='row/'+item['row'].bound.reservation.hex()+'/'+role,
                            'ROOT_ROSTER_DESCRIPTOR_ROLE_CHANGED')
                    expected.add(name)
            if roles['cgroup'] is not None:
                require(set(roles['cgroup'])=={'descriptor','path'},'ROOT_ROSTER_CGROUP_ROLE_CHANGED')
                name=roles['cgroup']['descriptor']
                require(name=='row/'+item['row'].bound.reservation.hex()+'/cgroup',
                        'ROOT_ROSTER_CGROUP_DESCRIPTOR_CHANGED');expected.add(name)
        for item in self.frame['source_files']:
            require(set(item)=={'path','role','descriptor','raw'} and item['descriptor']=='source/'+item['path'],
                    'ROOT_ROSTER_SOURCE_ROLE_CHANGED');expected.add(item['descriptor'])
        for item in self.frame['lease_locks']:
            require(set(item)=={'path','descriptor','identity'} and item['descriptor']=='lease/'+item['path'],
                    'ROOT_ROSTER_LEASE_LOCK_ROLE_CHANGED');expected.add(item['descriptor'])
        for item in self.frame.get('extensions',()):
            require(set(item)=={'descriptor','source_fd','identity'}
                and item['descriptor'].startswith('extension/')
                and item['descriptor'] not in expected,'ROOT_ROSTER_EXTENSION_ROLE_CHANGED')
            expected.add(item['descriptor'])
        for name,origin in self.frame.get('retained_roles',{}).items():
            require(set(origin)=={'bound','scope','role'} and name not in expected
                and name=='row/'+origin['bound'].reservation.hex()+'/'+origin['role'],
                'ROOT_ROSTER_RETAINED_ROLE_ORIGIN_CHANGED')
            matches=[item for item in entries if item['row'].bound==origin['bound']
                and item['row'].scope==origin['scope'] and item['roles'] is not None]
            require(len(matches)==1 and matches[0]['roles'][origin['role']] is None,
                'ROOT_ROSTER_RETAINED_ROLE_CURRENT_ACQUISITION_CHANGED')
            expected.add(name)
        for name,origin in self.frame.get('writer_aliases',{}).items():
            require(set(origin)=={'bound','scope','role','source_descriptor','source_fd','alias_source_fd','identity','kcmp'}
                and origin['role']=='stdin_fd' and name in expected,
                'ROOT_ROSTER_ACTUAL_WRITER_ALIAS_SCHEMA_CHANGED')
            matches=[item for item in entries if item['row'].bound==origin['bound']
                and item['row'].scope==origin['scope'] and item['roles'] is not None]
            require(len(matches)==1 and matches[0]['roles']['stdin_fd']==origin['source_descriptor'],
                'ROOT_ROSTER_ACTUAL_WRITER_ALIAS_BOUND_CHANGED')
            require_descriptor_identity(self.fds[name],origin['identity'])
        require(set(self.fds)==set(self.frame['descriptors'])==expected,'ROOT_ROSTER_FULL_DESCRIPTOR_SET_CHANGED')
        require(stat.S_ISDIR(os.fstat(self.fds['host_proc']).st_mode),'ROOT_ROSTER_HOST_PROC_DESCRIPTOR_INVALID')

    def intact(self,owner=None):
        return self._inventory(owner,self.slots)
    def retained_inventory(self,owner):
        from .protected_root_worker import RootWorkerFront,RootWorkerProcess,RootWorkerIntake
        require(type(owner) in (RootWorkerFront,RootWorkerProcess,RootWorkerIntake),
            'ROOT_ROSTER_ACTUAL_RETAINED_KERNEL_SOURCE_OWNER_REQUIRED')
        return self._inventory(owner,None)
    def _inventory(self,owner,owned_slots):
        from . import resource_scoped_run_ledger as S
        require(not self.closed,'ROOT_ROSTER_OBSERVATION_CUSTODY_CLOSED');self._shape()
        current={name:require_descriptor_identity(fd,self.frame['descriptors'][name]) for name,fd in self.fds.items()}
        selected=(self.front if self.front is not None else getattr(self,'reconstruction_owner',None)) if owner is None else owner
        require(selected is not None and selected.spec==self.frame['installation'],
                'ROOT_ROSTER_SELECTED_INSTALLATION_CHANGED')
        source=selected.source_lease.check()
        require(source['envelope_path']==self.frame['source']['envelope_path'] and
                source['envelope_bytes_hex']==self.frame['source']['envelope_bytes_hex'] and
                source['interpreter']==self.frame['source']['interpreter'],
                'ROOT_ROSTER_SOURCE_LEASE_IDENTITY_CHANGED')
        files=[]
        for item in self.frame['source_files']:
            fd=self.fds[item['descriptor']];named=os.stat(item['path'],follow_symlinks=False);held=os.fstat(fd)
            raw=_bytes(fd);lease_raw=selected.source_lease.file(item['path'],(item['role'],))
            named_record={'device':named.st_dev,'inode':named.st_ino,'mode':named.st_mode,'uid':named.st_uid,'gid':named.st_gid}
            files.append({'path':item['path'],'role':item['role'],'descriptor':item['descriptor'],
                'identity':identity(fd),'named':named_record,'raw':raw,'lease_raw':lease_raw})
            require((named.st_dev,named.st_ino,named.st_mode,named.st_uid,named.st_gid)==
                    (held.st_dev,held.st_ino,held.st_mode,held.st_uid,held.st_gid) and
                    raw==item['raw']==lease_raw,'ROOT_ROSTER_SOURCE_DESCRIPTOR_OR_BYTES_CHANGED')
        if self.front is not None and owned_slots is not None:
            require(set(self.producer.slots)==set(self.slots) and all(self.producer.slots.get(key) is slot
                    for key,slot in self.slots.items()),'ROOT_ROSTER_ACTUAL_SUPERVISOR_OWNERSHIP_CHANGED')
            for item in self.frame['rows']:
                if item['kind'] is None or item['row'].bound.reservation.hex() not in self.slots:continue
                slot=self.slots[item['row'].bound.reservation.hex()]
                require(slot.row.bound==item['row'].bound and _owner_kind(slot,self.front,self.producer)==item['kind']
                    and slot.held==item['held'] and slot.dispatch==item['dispatch'] and
                    slot.closed==item['closed'] and getattr(slot,'outer',None)==item['outer'],
                    'ROOT_ROSTER_OWNED_ORIGINAL_SOURCE_CHANGED')
                for role,fd in _descriptors(slot).items():
                    name=item['roles'][role]
                    if fd is not None and name is None:
                        absence=item['source'].get('descriptor_absence',{}).get(role)
                        require(absence is not None and absence['fd']==fd,
                                'ROOT_ROSTER_DESCRIPTOR_PRESENCE_CHANGED')
                        try:identity(fd)
                        except OSError as error:
                            require(error.errno==errno.EBADF==absence['errno'],
                                    'ROOT_ROSTER_DESCRIPTOR_ABSENCE_CHANGED')
                        else:require(False,'ROOT_ROSTER_CLOSED_DESCRIPTOR_REUSED')
                    else:
                        require((fd is None)==(name is None),'ROOT_ROSTER_DESCRIPTOR_PRESENCE_CHANGED')
                        if fd is not None:require_descriptor_identity(fd,self.frame['descriptors'][name])
        for item in self.frame['lease_locks']:
            fd=self.fds[item['descriptor']]
            require_descriptor_identity(fd,item['identity']);named_identity(fd,item['path'])
            if self.received:
                custody=getattr(selected,'current_offer',None) or getattr(selected,'custody',None)
                if custody is None:custody=selected.lease.exec_custody
                require(custody is not None,'ROOT_ROSTER_SOURCE_LEASE_ESCROW_ABSENT')
                held_locks=dict(custody.fds);journal=getattr(selected,'custody_journal',None)
                if journal is not None:held_locks[str(journal.lock_path)]=journal.lock_fd
                require(item['path'] in held_locks,'ROOT_ROSTER_SOURCE_LEASE_OFD_ABSENT')
                require_descriptor_identity(held_locks[item['path']],item['identity'])
        from .custody_subject_capture import role_roster,actor_identity
        roles=role_roster(self.frame['original_roles'],{name:self.fds[name] for name in sorted(self.fds)},source,
            worker_pid=os.getpid() if self.received else None)
        from .scoped_capture_namespace_source import namespace_source
        actor=actor_identity();namespaces=namespace_source(selected,self,actor)
        result={'frame':self.frame,'current_descriptors':current,'current_source':source,'roles':roles,
            'send_receipts':self.send_receipts,'receive_receipts':self.receive_receipts,
            'sender_receipts':self.sender_receipts,'reconstruction':getattr(self,'reconstruction',self.frame.get('reconstruction')),
            'sender_role_roster':getattr(self,'sender_role_roster',None),
            'current_actor':actor,'installation_json':_complete(selected.spec),'namespace_source':namespaces,
            'installation_scoped':S.record(selected.spec),
            'current_source_files':tuple(files)}
        if hasattr(self,'subject_transport'):result['subject_transport']=self.subject_transport
        initial=getattr(selected,'custody',None)
        if initial is not None and getattr(initial,'owned_roster',None) is self:
            result['initial_root_transport']=capture_initial_root_transport(selected,initial,source,actor)
        return result

    def retain_closed_front(self,offer):
        from .root_worker_custody import CustodyOffer
        require(type(offer) is CustodyOffer and offer.owned_roster is self and self.escrow
            and offer.slot.front is self.front and offer.p is self.front.principal,
            'ROOT_ROSTER_ACTUAL_CLOSED_FRONT_ESCROW_REQUIRED')
        self.reconstruction_owner=self.front;self.front=None
        self.closed_front_offer=offer
    def retain_closed_capture(self,guard):
        """Keep these real copies across genuine constructor cutover only."""
        from .root_worker_closed import ClosedFrontEscrow
        require(type(guard) is ClosedFrontEscrow and guard.front is self.front
            and guard.offer.p is self.front.principal
            and self.producer is guard.offer.p.resources
            and not self.closed,'ROOT_ROSTER_ACTUAL_CLOSED_CAPTURE_CUTOVER_REQUIRED')
        self.reconstruction_owner=self.front;self.front=None;self.escrow=True
        self.closed_front_guard=guard

    def extend_owned(self,owner,service):
        """Duplicate the complete genuine service registry without reopening state."""
        from .root_worker_subject_service import FrontSubjectService,RequestEscrow
        from .root_worker_subject_pump import CustodyDescriptorPump
        from .protected_root_worker import RootWorkerFront
        from .custody_subject_capture import actor_identity,original_roles,syscall,kcmp,fd_identity
        require(type(owner) is RootWorkerFront and type(service) is FrontSubjectService
            and service.owner is owner
            and (service.offer.owned_roster is self or
                (owner.current_offer is service.offer and getattr(owner,'_retained_owned_roster',None) is self))
            and not service.closed
            and all(type(value) is RequestEscrow and value.service is service for value in service.escrows.values())
            and all(type(value) is CustodyDescriptorPump and value.owner is owner
                for value in owner.subject_pumps.values()),'ROOT_ROSTER_ACTUAL_COMPLETE_SERVICE_OWNERS_REQUIRED')
        acquisitions=ExitStack()
        for bound in sorted((item['row'].bound for item in self.frame['rows']),key=lambda value:value.reservation):
            acquisitions.enter_context(roster_stdin_copy_lock(owner,bound))
        try:
            if self.front is owner:self.retain_closed_front(service.offer)
            original_inventory=self.intact(owner);registry=service.descriptors();source=owner.source_lease.check()
        except BaseException:
            acquisitions.close();raise
        obj=object.__new__(type(self));obj.frame=dict(self.frame);obj.fds={};obj.closed=False
        obj.frame.pop('evolution',None)
        obj.front=None;obj.producer=None;obj.slots={};obj.received=False;obj.escrow=True
        obj.reconstruction_owner=owner;obj.send_receipts={};obj.receive_receipts={};obj.sender_receipts=None
        receipts=[];extensions=[];rebinds=[]
        complete=dict(self.fds)
        complete.update(('extension/'+name,fd) for name,fd in registry.items())
        try:
            for role,fd in sorted(registry.items()):
                name='extension/'+role
                if name in self.fds:
                    rebinds.append({'role':name,'original_fd':self.fds[name],'registry_fd':fd,
                        'original_identity':identity(self.fds[name]),'registry_identity':identity(fd),
                        'kcmp':kcmp(os.getpid(),os.getpid(),self.fds[name],fd,source)})
            for name in sorted(complete):
                old=complete[name]
                fd,receipt=syscall(owner,'dup',{'fd':old,'role':name},lambda:os.dup(old))
                require(fd is not None,'ROOT_ROSTER_ACTUAL_SERVICE_DESCRIPTOR_DUP_FAILED')
                obj.fds[name]=fd;current=require_descriptor_identity(fd,identity(old))
                receipts.append({'role':name,'dup':receipt,'kcmp':kcmp(os.getpid(),os.getpid(),old,fd,source),
                    'origin':identity(old),'current':current})
                if name.startswith('extension/'):
                    extensions.append({'descriptor':name,'source_fd':old,'identity':identity(old)})
            require(registry==service.descriptors(),'ROOT_ROSTER_SERVICE_DESCRIPTOR_OWNERSHIP_CHANGED')
            from .scoped_capture_namespace_source import capture_actor_namespace
            actor=actor_identity(service.channel);obj.frame['sender_actor_namespace']=capture_actor_namespace(actor,source)
            obj.frame['descriptors']={name:identity(fd) for name,fd in obj.fds.items()}
            obj.frame['extensions']=tuple(extensions)
            aliases=dict(self.frame.get('writer_aliases',{}))
            for entry in service.offer.owned_roster.frame['rows']:
                if entry['roles'] is None or entry['roles']['stdin_fd'] is None:continue
                source_name=entry['roles']['stdin_fd'];registry_name='scoped/'+source_name
                require(source_name in self.fds and registry_name in registry,
                    'ROOT_ROSTER_ACTUAL_SERVICE_WRITER_ALIAS_SOURCE_ABSENT')
                aliases['extension/'+registry_name]={'bound':entry['row'].bound,
                    'scope':entry['row'].scope,'role':'stdin_fd','source_descriptor':source_name,
                    'source_fd':self.fds[source_name],'alias_source_fd':registry[registry_name],
                    'identity':identity(registry[registry_name]),
                    'kcmp':kcmp(os.getpid(),os.getpid(),self.fds[source_name],registry[registry_name],source)}
            if aliases:obj.frame['writer_aliases']=aliases
            obj.frame['original_roles']=original_roles({name:obj.fds[name] for name in sorted(obj.fds)},source,
                actor,fd_identity(service.offer.origins['worker_pidfd']),
                {item['descriptor']:item['path'] for item in obj.frame['lease_locks']})
            obj.reconstruction={'original_frame':self.frame,'original_inventory':original_inventory,
                'duplicates':tuple(receipts),'source':source,
                'service_registry':tuple({'role':name,'fd':fd,'identity':identity(fd)}
                    for name,fd in sorted(registry.items()))}
            if rebinds:obj.reconstruction['extension_rebinds']=tuple(rebinds)
            obj.frame['reconstruction']=obj.reconstruction
            obj._shape();obj.intact(owner)
            return obj
        except BaseException:
            obj.close();raise
        finally:
            acquisitions.close()

    def send(self,channel):
        selected=self.front if self.front is not None else self.reconstruction_owner
        with ExitStack() as acquisitions:
            for bound in sorted((item['row'].bound for item in self.frame['rows']),key=lambda value:value.reservation):
                acquisitions.enter_context(roster_stdin_copy_lock(selected,bound))
            self.intact()
            source=selected.source_lease.check()
            for name in sorted(self.fds):
                receipt=_send_fd(channel,self.fds[name],source=source)
                self.send_receipts[name]=receipt
        # Originals and duplicates are escrow through the native effect return,
        # not just send or ACK. Only explicit owning cleanup calls close().

    def has(self,row):
        return any(item['row'].bound==row.bound and item['kind'] is not None for item in self.frame['rows'])

    def _entry(self,row):
        matches=[item for item in self.frame['rows'] if item['row'].bound==row.bound]
        require(len(matches)==1 and matches[0]['row'].scope==row.scope,
                'ROOT_ROSTER_ORIGINAL_ROW_SCOPE_CHANGED')
        return matches[0]

    def capture_fact(self,owner,row,blank,challenge,history_owner=None):
        self.intact(owner);item=self._entry(row);source=dict(item['source']);source['challenge']=challenge
        roles=item['roles'];physical=replace(blank,retained=row.bound)
        from .scoped_capture_history_source import capture_receiver_history_owner
        if history_owner is None:
            from .root_worker_current_state import capture_startup_owner_state
            history_owner=capture_receiver_history_owner(owner,capture_startup_owner_state(owner),self)
        events=tuple(event for event in history_owner['launch_events']
            if event['reservation']==row.bound.reservation.hex() and event['cause']!='OBSERVATION')
        source['events']=events;source['journal_head']=history_owner['launch_head']
        prepared=tuple(event for event in events if event['cause']=='PREPARED')
        require(len(prepared)<=1,'ROOT_ROSTER_AUTHENTIC_PREPARATION_ALIAS')
        from .protected_resource_runtime import canonical
        physical=replace(physical,intent=None if not prepared else hashlib.sha256(canonical(prepared[0])).digest())
        if roles is None:return physical,source
        if item['held'] is None:
            # Real pre-HELD/failed acquisition has no native LIVE premise.
            source['kernel']={'owned_unavailable':item,'inventory':self.intact(owner)}
            return physical,source
        rights={role:self.fds[name] for role,name in roles.items() if role!='cgroup' and name is not None}
        rights['host_proc']=self.fds['host_proc']
        absent=tuple(role for role in ('supervisor_channel','worker_namespace','namespace_pidfd','helper_pidfd')
                     if roles[role] is None)
        if absent:
            source['kernel']={'actual_descriptor_absence':item['source'].get('descriptor_absence',{}),
                'absent_roles':absent,'rights':{name:identity(fd) for name,fd in rights.items()},
                'current_source':owner.source_lease.check()}
            source['inventory']=self.intact(owner)
            return replace(physical,observation_head=hashlib.sha256(source_bytes(source)).digest()),source
        if roles['cgroup'] is None:
            properties=item['held']['properties']
            cg=properties[b'ControlGroup'] if item['kind']=='ROOT' else bytes.fromhex(properties['ControlGroup'])
            require(cg.startswith(b'/') and not any(word in (b'.',b'..') for word in cg.split(b'/')),
                    'ROOT_ROSTER_CGROUP_PATH_INVALID')
            path=Path('/sys/fs/cgroup')/os.fsdecode(cg).lstrip('/')
            flags=os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC
            try:fd=os.open(path,flags)
            except OSError as error:
                source['kernel']={'actual_cgroup_open':{'call':'open','path':str(path),'flags':flags,
                    'result':-1,'errno':error.errno,'message':str(error)},'rights':{name:identity(fd) for name,fd in rights.items()},
                    'current_source':owner.source_lease.check()}
                source['inventory']=self.intact(owner)
                return replace(physical,observation_head=hashlib.sha256(source_bytes(source)).digest()),source
            else:
                os.close(fd)
                require(False,'ROOT_ROSTER_CGROUP_ABSENCE_CHANGED_RECAPTURE_REQUIRED')
        if item['kind']=='ROOT':
            from .root_worker_physical import observe
            captured=observe(owner,row,item['dispatch'],item['held'],rights,closed=item['closed'],outer=item['outer'])
        else:captured=self._observe_supervisor(owner,row,item,rights)
        if captured['native_fields'] is None:
            source['kernel']=captured['raw'];source['inventory']=self.intact(owner)
            source['process_inventory']=self._capture_process_inventory(owner,roles,rights,
                {'actual_unit':None,'invocation':None})
            return replace(physical,observation_head=hashlib.sha256(source_bytes(source)).digest()),source
        cg=roles['cgroup']
        require(cg is not None,'ROOT_ROSTER_HELD_CGROUP_DESCRIPTOR_ABSENT')
        fd=self.fds[cg['descriptor']];named=os.stat(cg['path'],follow_symlinks=False);held=os.fstat(fd)
        require((named.st_dev,named.st_ino)==(held.st_dev,held.st_ino) and
                _read_at(fd,'cgroup.events')==captured['native_fields']['cgroup_events'] and
                _read_at(fd,'cgroup.type')==captured['native_fields']['cgroup_type'],
                'ROOT_ROSTER_CURRENT_CGROUP_DESCRIPTOR_CHANGED')
        from .protected_resource_runtime import canonical
        dispatch_value=item['dispatch']['resource_dispatch'] if item['kind']=='ROOT' else item['dispatch']
        helper_path=owner.plan['helper'] if item['kind']=='ROOT' else self.frame['resource_config']['helper']
        source['physical_projection']={'namespace_identity':identity(rights['worker_namespace']),
            'dispatch_value':dispatch_value,'dispatch_json':canonical(dispatch_value),
            'helper_path':helper_path,'helper_image_bytes':owner.source_lease.file(helper_path,('EXECUTABLE',)),
            'challenge_hex':item['dispatch']['ticket'] if item['kind']=='ROOT' else item['held']['challenge']}
        source['cgroup_descriptor']={'path':cg['path'],'descriptor':cg['descriptor'],'identity':identity(fd),
            'named':{'device':named.st_dev,'inode':named.st_ino,'mode':named.st_mode,'uid':named.st_uid,'gid':named.st_gid},
            'events':_read_at(fd,'cgroup.events'),'type':_read_at(fd,'cgroup.type')}
        source['kernel']=captured['raw'];source['inventory']=self.intact(owner)
        inventory=self._capture_process_inventory(owner,roles,rights,captured['native_fields'])
        role='worker_pidfd' if item['kind']=='ROOT' else 'actor_pidfd'
        source['process']=inventory[role]['observation'];source['process_raw']=inventory[role]['raw']
        source['process_inventory']=inventory
        physical=replace(physical,**captured['native_fields'])
        from .scoped_capture_history_source import owned_protocol_preimages
        source['owned_protocol']=owned_protocol_preimages(item,source,history_owner)
        tree=dict(source);raw=source_bytes(tree)
        source['head_tree']=tree;source['head_preimage']=raw;source['head_encoding']='ROOT_RAW_ARCHIVE'
        physical=replace(physical,observation_head=hashlib.sha256(raw).digest())
        return physical,source

    def _capture_process_inventory(self,owner,roles,rights,physical):
        # Each pidfd has its own actual zero-timeout poll; no inherited LIVE bit.
        source_id=hashlib.sha256(_complete(owner.spec)).digest();inventory={}
        for role in ('namespace_pidfd','helper_pidfd','worker_pidfd','actor_pidfd'):
            if roles[role] is None:
                inventory[role]={'descriptor':None,'wait':None,'poll':None,'observation':None,'raw':None}
                continue
            fd=rights[role];poller=select.poll();poller.register(fd,select.POLLIN|select.POLLHUP|select.POLLERR)
            returned=tuple(poller.poll(0))
            wait=b'PIDFD_TERMINAL' if returned else b'PIDFD_LIVE'
            poll={'call':'poll','args':{'fd':fd,'events':select.POLLIN|select.POLLHUP|select.POLLERR,'timeout':0},
                'result':len(returned),'errno':0,'returned':returned,'source':owner.source_lease.check()}
            if wait==b'PIDFD_LIVE':
                namespace=rights['helper_namespace'] if role=='helper_pidfd' else rights['worker_namespace']
                process,raw=RootProcessCapture(rights['host_proc'],fd,namespace,owner.source_lease).capture(
                    physical['actual_unit'],physical['invocation'],source_id)
            else:
                process=None;raw={'actual_pidfd_wait':wait,'identity':identity(fd),
                    'full_fdinfo':Path('/proc/self/fdinfo/'+str(fd)).read_bytes()}
            inventory[role]={'descriptor':roles[role],'wait':wait,'poll':poll,'observation':process,'raw':raw}
        return inventory

    def recapture(self,owner,packet,owner_state=None):
        from . import resource_scoped_run_ledger as S
        from .resource_run_ledger import RunObservation
        require(len(packet.rows)==len(self.frame['packet'].rows) and all(
            row.bound==old.bound and row.scope==old.scope
            for row,old in zip(packet.rows,self.frame['packet'].rows)),
            'ROOT_ROSTER_COMPLETE_RETAINED_ROW_ORIGINS_CHANGED')
        self.intact(owner);facts=[];sources=[]
        from .scoped_capture_history_source import recapture_unowned_source,capture_receiver_history_owner
        if owner_state is None:
            from .root_worker_current_state import capture_startup_owner_state
            owner_state=capture_startup_owner_state(owner)
        history_owner=capture_receiver_history_owner(owner,owner_state,self)
        from .protected_resource_runtime import ProtectedResourcePrincipal,canonical
        for row,old in zip(packet.rows,packet.facts):
            blank=ProtectedResourcePrincipal._blank(packet.current.scope,packet.current.resource_epoch,
                packet.current.universe_head,packet.current.ledger_head,row,packet.current.observation_head)
            item=self._entry(row)
            if item['kind'] is None:
                fact,source=recapture_unowned_source(owner,row,blank,item['source'],owner_state,self)
                facts.append(fact);sources.append(source);continue
            fact,source=self.capture_fact(owner,row,blank,packet.current.observation_head.hex(),history_owner)
            facts.append(fact);sources.append(source)
        initial=tuple(RunObservation(scope=row.scope,resource_epoch=packet.before.resource_epoch,bound=row.bound,
            actual_unit=row.actual_unit,cgroup=row.cgroup,invocation=row.invocation,
            observed='UNKNOWN',observation_head=fact.observation_head)
            for row,fact in zip(packet.rows,facts))
        from .protected_root_worker import RootWorkerIntake
        from .protected_scoped_resource_service import packet_before,snapshot_record
        core=owner.core if type(owner) is RootWorkerIntake else owner.principal.core
        interim=replace(packet,facts=tuple(facts),observed=initial);classifier=S.ScopedRunLedgerKernel(core)
        request_id=hashlib.sha256(canonical(snapshot_record(packet_before(packet)))).digest()
        observed=[];classifications=[];materials=[]
        for row,fact in zip(packet.rows,facts):
            request=replace(packet.request.original,kind='UNKNOWN_OPERATION',scope=row.scope,
                expected_epoch=packet.before.resource_epoch,expected_ledger_head=packet.before.ledger_head,
                request_id=request_id,reservation=row.bound.reservation,operation_id=row.bound.operation,
                requester=row.bound.owner,bound=row.bound,new_row=row)
            intent=replace(packet.request,kind='ORDINARY',original=request,expected_epoch=packet.before.resource_epoch,
                expected_ledger_head=packet.before.ledger_head,request_id=request_id,
                cause=packet.current.cause,requester=packet.current.requester,receipt=packet.current.receipt)
            material=replace(interim,request=intent,proposed=packet.before,proposed_history=packet.history,
                proposed_rows=packet.rows,proposed_projection=packet.projection,proposed_buckets=packet.buckets,
                actual_buckets=packet.buckets)
            decision=classifier.classify(material);materials.append(material)
            effect=decision.status in ('LIVE','REAPED')
            observed.append(RunObservation(scope=row.scope,resource_epoch=packet.before.resource_epoch,bound=row.bound,
                actual_unit=fact.actual_unit if effect else row.actual_unit,cgroup=fact.cgroup if effect else row.cgroup,
                invocation=fact.invocation if effect else row.invocation,observation_head=fact.observation_head,observed=decision.status))
            classifications.append(decision)
        result=replace(interim,observed=tuple(observed))
        return result,{'inventory':self.intact(owner),'rows':tuple({'row':row,'physical':fact,'observed':native,
            'native_classification':decision,'classification_material':material,'source':source}
            for row,fact,native,decision,material,source in
            zip(result.rows,result.facts,result.observed,classifications,materials,sources)),'packet':result}

    def _observe_supervisor(self,owner,row,item,rights):
        from .root_worker_host_peer import host_peer,host_fdinfo
        from .protected_scoped_supervisor_v3 import OwnedSupervisorV3 as V
        from .protected_resource_runtime import canonical,identity_record,private,kernel_bytes,digest
        cfg=self.frame['resource_config'];held=item['held'];dispatch=item['dispatch'];host=rights['host_proc']
        path=cfg['systemctl'];owner.source_lease.file(path,('EXECUTABLE',))
        names=('Id','MainPID','InvocationID','ControlGroup','Delegate','ActiveState','SubState')
        answer=subprocess.run([path,'--system','show',row.planned_unit.decode('ascii'),'--no-pager',
            *(('--property='+name) for name in names)],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,check=False,env={'PATH':'/usr/bin:/bin','LANG':'C'})
        if answer.returncode!=0:
            return {'native_fields':None,'raw':{'manager':{'argv':answer.args,'stdout':answer.stdout,
                'stderr':answer.stderr,'returncode':answer.returncode},'held':held,'dispatch':dispatch,
                'rights':{name:identity(fd) for name,fd in rights.items()},'source':owner.source_lease.check()}}
        properties={}
        for line in answer.stdout.splitlines():
            name,separator,value=line.partition(b'=')
            require(separator and name.decode('ascii') in names and name not in properties,
                    'ROOT_ROSTER_COMPLETE_MANAGER_PROPERTIES_INVALID');properties[name]=value
        require(set(properties)=={name.encode('ascii') for name in names} and properties[b'Id']==row.planned_unit,
                'ROOT_ROSTER_SELECTED_MANAGER_UNIT_CHANGED')
        cg=bytes.fromhex(held['properties']['ControlGroup']);inv=bytes.fromhex(held['properties']['InvocationID'])
        require(properties[b'ControlGroup']==cg and properties[b'InvocationID']==inv,
                'ROOT_ROSTER_ORIGINAL_SUPERVISOR_MANAGER_CHANGED')
        namespace=canonical(identity_record(os.fstat(rights['worker_namespace'])))
        require(namespace.hex()==held['namespace'],'ROOT_ROSTER_ORIGINAL_SUPERVISOR_NAMESPACE_CHANGED')
        ns_wait=V.pidfd_state(rights['namespace_pidfd']);helper_wait=V.pidfd_state(rights['helper_pidfd'])
        channel=socket.socket(fileno=os.dup(rights['supervisor_channel']))
        try:
            require(channel.family==socket.AF_UNIX and channel.getsockopt(socket.SOL_SOCKET,socket.SO_TYPE)==socket.SOCK_SEQPACKET,
                    'ROOT_ROSTER_REAL_SUPERVISOR_CHANNEL_REQUIRED')
            if helper_wait==b'PIDFD_LIVE':peer,peer_source=host_peer(host,channel,owner.source_lease)
            else:peer=bytes.fromhex(held['peer']);peer_source={'retained_terminal_peer':peer,
                'relative_peer':channel.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,struct.calcsize('@iII'))}
        finally:channel.close()
        require(peer.hex()==held['peer'],'ROOT_ROSTER_ORIGINAL_SUPERVISOR_PEER_CHANGED')
        cg_role=item['roles']['cgroup'];fd=self.fds[cg_role['descriptor']];path=Path(cg_role['path'])
        for root,directories,_files in os.walk(path,followlinks=False):
            private(root,directory=True)
            for name in ('cgroup.procs','cgroup.threads','cgroup.subtree_control'):
                selected=Path(root)/name
                if selected.exists():private(selected)
        info=os.fstat(fd);events=_read_at(fd,'cgroup.events');kind=_read_at(fd,'cgroup.type');proc=None
        if helper_wait==b'PIDFD_LIVE':
            pid,fdinfo=host_fdinfo(host,rights['helper_pidfd'])
            require(pid==held['helper_pid'] and V.number(properties[b'MainPID'])==pid,
                    'ROOT_ROSTER_LIVE_HELPER_MANAGER_CHANGED')
            root=os.open(str(pid),os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=host)
            try:
                image=os.readlink('exe',dir_fd=root)
                raw=owner.source_lease.file(image,('EXECUTABLE',))
                require(image==cfg['helper'] and digest(raw)==cfg['helper_sha256'],'ROOT_ROSTER_HELPER_IMAGE_CHANGED')
                proc={name:_read_at(root,name) for name in ('status','stat','cgroup','maps','cmdline')}
                require(proc['cgroup']==b'0::'+cg+b'\n' and proc['cmdline']==
                    b'\0'.join(os.fsencode(word) for word in dispatch['payload']['helper_arguments'])+b'\0',
                    'ROOT_ROSTER_HELPER_COMMAND_OR_CGROUP_CHANGED')
                for line in proc['maps'].splitlines():
                    parts=line.split(None,5)
                    if len(parts)==6 and parts[5].startswith(b'/'):
                        owner.source_lease.file(os.fsdecode(parts[5]),('EXECUTABLE','EXTENSION'))
            finally:os.close(root)
        else:require(properties[b'MainPID']==b'0','ROOT_ROSTER_TERMINAL_HELPER_MANAGER_CHANGED')
        closed=item['closed'];closed_event=item['closed_event'];source=owner.source_lease.check()
        return {'native_fields':{'dispatch':bytes.fromhex(digest(canonical(dispatch))),'actual_unit':properties[b'Id'],
            'cgroup':cg,'invocation':inv,'namespace':namespace,'held_namespace':bytes.fromhex(held['namespace']),
            'peer':peer,'held_peer':bytes.fromhex(held['peer']),'helper_image':bytes.fromhex(cfg['helper_sha256']),
            'expected_helper_image':bytes.fromhex(cfg['helper_sha256']),'challenge':bytes.fromhex(held['challenge']),
            'held_challenge':bytes.fromhex(held['challenge']),'protocol':b'CLOSED_ECHILD' if closed is not None else b'HELD',
            'closed_event':None if closed_event is None else bytes.fromhex(digest(canonical(closed_event))),
            'namespace_wait':ns_wait,'helper_wait':helper_wait,'cgroup_events':events,'cgroup_type':kind,
            'manager_delegate':properties[b'Delegate'],'cgroup_owner':info.st_uid,'cgroup_group_write':info.st_mode&stat.S_IWGRP,
            'cgroup_other_write':info.st_mode&stat.S_IWOTH,'phase':'NAMESPACE_CLOSED' if closed is not None else 'NAMESPACE_HELD'},
            'raw':{'held':held,'closed':closed,'manager':{'argv':answer.args,'stdout':answer.stdout,'stderr':answer.stderr,
                'returncode':answer.returncode},'cgroup':{'path':str(path),'identity':identity(fd),'events':events,'type':kind},
                'namespace_wait':ns_wait,'helper_wait':helper_wait,'helper_proc':proc,'peer_source':peer_source,
                'rights':{name:identity(fd) for name,fd in rights.items()},'source':source}}

    @classmethod
    def reconstruct(cls,front,guard):
        from .protected_root_worker import RootWorkerFront
        from .root_worker_closed import ClosedFrontEscrow
        from .custody_subject_capture import actor_identity,original_roles,syscall,kcmp
        require(type(front) is RootWorkerFront and type(guard) is ClosedFrontEscrow
            and guard.fresh_lease is front.lease and front.lease.exec_custody is guard
            and guard.phase=='RECONSTRUCTED' and type(guard.owned_roster) is cls,
            'ROOT_ROSTER_REAL_CLOSED_RECONSTRUCTION_GUARD_REQUIRED')
        original=guard.owned_roster;acquisitions=ExitStack()
        for bound in sorted((item['row'].bound for item in original.frame['rows']),key=lambda value:value.reservation):
            acquisitions.enter_context(roster_stdin_copy_lock(front,bound))
        try:original_inventory=original.intact(guard.intake)
        except BaseException:
            acquisitions.close();raise
        obj=object.__new__(cls);obj.frame=dict(original.frame);obj.fds={};obj.closed=False
        obj.frame.pop('evolution',None)
        obj.front=None;obj.producer=None;obj.slots={};obj.received=False;obj.escrow=True
        obj.send_receipts={};obj.receive_receipts={};obj.sender_receipts=None
        obj.reconstruction_owner=front;receipts=[]
        try:
            source=front.source_lease.check()
            for name in sorted(original.fds):
                old=original.fds[name]
                fd,receipt=syscall(front,'dup',{'fd':old,'role':name},lambda:os.dup(old))
                require(fd is not None,'ROOT_ROSTER_RECONSTRUCTION_DUP_FAILED');obj.fds[name]=fd
                current=require_descriptor_identity(fd,original.frame['descriptors'][name])
                comparison=kcmp(os.getpid(),os.getpid(),old,fd,source)
                receipts.append({'role':name,'dup':receipt,'kcmp':comparison,'origin':identity(old),'current':current})
            obj.frame['descriptors']={name:identity(fd) for name,fd in obj.fds.items()}
            from .scoped_capture_namespace_source import capture_actor_namespace
            actor=actor_identity();obj.frame['sender_actor_namespace']=capture_actor_namespace(actor,source)
            obj.frame['original_roles']=original_roles({name:obj.fds[name] for name in sorted(obj.fds)},source,
                actor,None,{item['descriptor']:item['path'] for item in obj.frame['lease_locks']})
            obj.reconstruction={'original_frame':original.frame,'original_inventory':original_inventory,
                'duplicates':tuple(receipts),'source':source,'service_registry':()}
            obj.frame['reconstruction']=obj.reconstruction
            obj._shape();obj.intact(front)
            guard.reconstructed_roster=obj
            return obj
        except BaseException:
            obj.close();raise
        finally:
            acquisitions.close()

    def attach(self,owner,producer):
        from .protected_root_worker import RootWorkerProcess,RootWorkerFront
        from .root_worker_closed import ClosedFrontEscrow
        from .protected_scoped_resource_runtime import ProtectedScopedResourcePrincipal
        require(type(producer) is ProtectedScopedResourcePrincipal and producer.lease is owner.lease,
            'ROOT_ROSTER_ACTUAL_FRESH_SCOPED_OWNER_REQUIRED')
        if type(owner) is RootWorkerProcess:
            require(owner.custody.owned_roster is self,'ROOT_ROSTER_REAL_RECEIVED_OWNER_REQUIRED')
        else:
            guard=owner.lease.exec_custody
            require(type(owner) is RootWorkerFront and type(guard) is ClosedFrontEscrow
                and guard.fresh_lease is owner.lease and guard.reconstructed_roster is self
                and self.reconstruction_owner is owner,'ROOT_ROSTER_REAL_RECONSTRUCTED_OWNER_REQUIRED')
        self.intact(owner);producer.received_roster=self;producer.received_roster_owner=owner

    def close(self):
        if self.closed:return
        self.closed=True
        failure=None
        for name in tuple(self.fds):
            try:os.close(self.fds.pop(name))
            except OSError as error:
                if failure is None:failure=error
                else:failure.add_note('additional owned descriptor close failed: '+repr(error))
        if failure is not None:raise failure


def capture_initial_root_transport(owner,receipt,source,actor):
    """Observe the original whole Root transfer, not a fabricated secondary request."""
    from .root_worker_custody import CustodyReceipt
    from .custody_subject_capture import role_roster
    from .root_worker_subject_transfer import received_descriptors
    require(type(receipt) is CustodyReceipt and owner.custody is receipt
        and receipt.owned_roster is not None,'ROOT_INITIAL_ACTUAL_RECEIPT_REQUIRED')
    supplied=received_descriptors(receipt);original=receipt.frame['subject_custody']['roles']
    received=receipt.subject_intake['transfer']['roles'];current=[]
    require(len(received)==len(original),'ROOT_INITIAL_COMPLETE_ORIGINAL_ROLE_OBSERVATIONS_REQUIRED')
    for declared,prior in zip(original,received):
        name=declared['role']
        require(prior['role']==name,'ROOT_INITIAL_ORIGINAL_ROLE_ORDER_CHANGED')
        fd=supplied.get(name,prior['worker_fd'])
        require(type(fd) is int,'ROOT_INITIAL_ACTUAL_RECEIVED_DESCRIPTOR_REQUIRED')
        try:os.fstat(fd)
        except OSError as error:
            current.append({'role':name,'fd':fd,'fstat':{'call':'fstat','args':{'fd':fd},
                'fd':fd,'result':-1,'errno':error.errno,'source':source}})
        else:current.extend(role_roster((declared,),{name:fd},source,worker_pid=os.getpid()))
    return {'schema':'worldline.initial-root-subject-transport-source-v1',
        'frame':receipt.frame,'trailer':receipt.send_transcript,'transfer':receipt.subject_intake['transfer'],
        'ofd_broker':receipt.ofd_broker,'sender_role_roster':receipt.sender_role_roster,
        'current_roles':tuple(current),'current_actor':actor,'current_source':source}


def offer_roster(offer,native_event):
    """Claim only the genuine full-native capture used by this actual offer."""
    from .root_worker_custody import CustodyOffer
    from .protected_root_observation import RootControllerCapture
    require(type(offer) is CustodyOffer,'ROOT_ROSTER_REAL_CUSTODY_OFFER_REQUIRED')
    capture=getattr(offer.p.root_worker,'_root_capture',None)
    require(type(capture) is RootControllerCapture and capture.owner is offer.p.root_worker
        and capture.material==native_event['material']
        and capture.provenance==native_event['provenance']
        and type(capture.owned_roster) is OwnedDescriptorRoster,
        'ROOT_ROSTER_ORIGINAL_FULL_NATIVE_CAPTURE_CHANGED')
    capture.owned_roster.intact();capture.owned_roster.escrow=True
    offer.p.root_worker._retained_owned_roster=capture.owned_roster
    return capture.owned_roster


def install_retained_root_refresh(owner,roster,seed,*,transfer):
    """Acquire an actual complete worker-to-front SCM inventory, not permission."""
    from .protected_root_worker import RootWorkerFront
    from .root_worker_custody import CustodyOffer
    from .root_worker_process_capture import RootProcessCapture
    from .custody_subject_capture import actor_identity,kcmp,fd_identity
    from . import resource_scoped_run_ledger as S
    require(type(owner) is RootWorkerFront and type(roster) is OwnedDescriptorRoster
        and roster.received and not roster.closed and type(owner.current_offer) is CustodyOffer
        and owner.current_offer.p is owner.principal and type(seed) is dict
        and set(seed)=={'cause','material','observation','provenance'} and type(transfer) is dict,
        'ROOT_ROSTER_ACTUAL_FULL_SCM_REFRESH_REQUIRED')
    offer=owner.current_offer;material=seed['material'];packet=material['packet']
    require(type(packet) is S.ScopedPacket and material['controller'].bound.operation.hex()==offer.frame['operation']
        and roster.frame['packet'].rows==packet.rows and roster.frame['packet'].before==packet.before
        and seed['provenance']['original_request']==offer.request.observation(),
        'ROOT_ROSTER_ACTUAL_REFRESH_ORIGINAL_ROOT_CHANGED')
    entries=[entry for entry in roster.frame['rows'] if entry['row'].bound==material['controller'].bound]
    require(len(entries)==1 and entries[0]['kind']=='ROOT','ROOT_ROSTER_ACTUAL_REFRESH_SELECTED_ROOT_REQUIRED')
    entry=entries[0];roles=entry['roles'];row=entry['row']
    process,raw=RootProcessCapture(roster.fds['host_proc'],roster.fds[roles['worker_pidfd']],
        roster.fds[roles['worker_namespace']],owner.source_lease).capture(row.actual_unit,row.invocation,
            material['controller'].source_lease)
    sender_host_pid=process.host_pid;actor=actor_identity();source=owner.source_lease.check()
    import select
    fd=roster.fds[roles['worker_pidfd']];poller=select.poll()
    poller.register(fd,select.POLLIN|select.POLLHUP|select.POLLERR);returned=tuple(poller.poll(0))
    poll={'call':'poll','args':{'fd':fd,'events':select.POLLIN|select.POLLHUP|select.POLLERR,'timeout':0},
        'result':len(returned),'errno':0,'returned':returned,'source':source}
    process_item={'descriptor':roles['worker_pidfd'],'observation':process,'raw':raw,'poll':poll,
        'wait':b'PIDFD_TERMINAL' if returned else b'PIDFD_LIVE'}
    broker_roles=[]
    for original in roster.frame['original_roles']:
        name=original['role'];fd=roster.fds[name]
        broker_roles.append({'role':name,'front_fd':original['fd'],'worker_fd':fd,
            'origin':original['identity'],'current':fd_identity(fd),
            'kcmp':kcmp(sender_host_pid,os.getpid(),original['fd'],fd,source)})
    roster.sender_receipts=transfer['send_receipts']
    roster.sender_role_roster={'roles':tuple(broker_roles),'source':source,
        'actor':roster.frame['sender_actor_namespace']['actor'],
        'worker_pidfd':roster.frame['original_roles'][0]['worker_pidfd'],
        'worker_host_pid':os.getpid(),'reverse_host_broker':{'sender_host_pid':sender_host_pid,
            'sender_process':process,'sender_process_source':raw,'sender_process_item':process_item,
            'receiver_actor':actor,'transfer':transfer}}
    roster.reconstruction_owner=owner;roster.refresh_offer=offer;roster.escrow=True
    holders=getattr(owner,'_scoped_capture_rosters',None)
    if holders is None:holders=[];owner._scoped_capture_rosters=holders
    holders.append(roster)
    owner._retained_owned_roster=roster;owner._retained_root_native=seed
    return roster


def release_unclaimed_capture(owner):
    """Close only these unclaimed observation duplicates, never transport owners."""
    from .protected_root_worker import RootWorkerFront,RootWorkerProcess,RootWorkerIntake
    require(type(owner) in (RootWorkerFront,RootWorkerProcess,RootWorkerIntake),
            'ROOT_ROSTER_EXACT_NATIVE_CAPTURE_OWNER_REQUIRED')
    capture=getattr(owner,'_root_capture',None)
    roster=None if capture is None else capture.owned_roster
    if roster is not None and not roster.escrow:roster.close()
