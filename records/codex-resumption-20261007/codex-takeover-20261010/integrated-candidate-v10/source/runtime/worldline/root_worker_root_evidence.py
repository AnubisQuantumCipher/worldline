"""Actual root lifecycle operands; native replay alone decides their meaning.

Original payloads and syscall arguments are never reduced to readiness flags.
Receipts describe calls made here, not calls inferred from later state.
"""
from __future__ import annotations
import array,errno,fcntl,os,select,socket,stat,struct
from pathlib import Path
from .protected_startup import require,exact_json,digest,canonical,private_bytes
from .root_worker_codec import archive,restore_archive,raw_archive,raw_restore_archive
from .custody_subject_capture import syscall,actor_identity,kcmp
from .root_worker_custody import identity
from .operation_capture import restore_archive as restore_operation


def descriptor_inventory():
    """Read every retained descriptor, excluding this capture's directory FD."""
    directory=os.open('/proc/self/fd',os.O_RDONLY|os.O_DIRECTORY|os.O_CLOEXEC)
    try:
        rows=[]
        for name in os.listdir(directory):
            fd=int(name)
            if fd==directory:continue
            try:held=identity(fd)
            except OSError as error:
                # listdir's already-closed directory duplicate is not retained.
                if error.errno==errno.EBADF:continue
                raise
            rows.append({'fd':fd,'identity':held,
                'link':os.readlink('/proc/self/fd/'+name),
                'fdinfo':Path('/proc/self/fdinfo/'+name).read_bytes()})
        return tuple(rows)
    finally:os.close(directory)


def capture_effect(source_lease,call,args,fn):
    """Retain a real syscall/API result and preserve its original exception."""
    receipt={'call':call,'args':args,'source':source_lease.check()}
    try:value=fn()
    except OSError as error:
        receipt.update(result=-1,errno=error.errno,message=str(error))
        error.custody_receipt=receipt
        raise
    result=len(value) if type(value) is bytes else value if type(value) is int else 0
    receipt.update(result=result,errno=0,api_result=value)
    if type(value) is bytes:receipt['raw']=value
    return value,receipt


def close_owned_stdin(slot,fd):
    """End real input and every acquired observation-writer lifetime together."""
    from .root_owned_descriptor_roster import prepare_owned_stdin_eof,complete_owned_stdin_eof,owned_stdin_copy_lock,roster_stdin_copy_lock
    from .protected_root_worker import RootWorkerProcess
    require(slot.stdin_fd==fd,'ROOT_STDIN_EOF_ORIGINAL_DESCRIPTOR_CHANGED')
    owner=getattr(slot,'front',None)
    if owner is None:
        principal=slot.principal.lease.canonical_operation_principal
        owner=getattr(principal,'root_worker_process',None) or getattr(principal,'root_worker',None)
    if type(owner) is RootWorkerProcess:return owner.close_stdin(slot,fd)
    with roster_stdin_copy_lock(owner,slot.row.bound),owned_stdin_copy_lock(slot):
        context=prepare_owned_stdin_eof(slot)
        slot.stdin_fd=None;closed=None
        try:
            _result,closed=capture_effect(owner.source_lease,'close',{'fd':fd},lambda:os.close(fd))
        except BaseException as error:
            closed=getattr(error,'custody_receipt',None)
            if closed is not None:
                try:slot.stdin_observation_closures=complete_owned_stdin_eof(slot,context,closed)
                except BaseException as close_error:
                    slot.stdin_observation_close_error=close_error
                    error.add_note('Actual input observation copies close also failed: '+repr(close_error))
            raise
        finally:
            if closed is not None:
                retained=getattr(slot,'stdin_close_receipts',None)
                if retained is None:retained=[];slot.stdin_close_receipts=retained
                retained.append(closed)
        slot.stdin_observation_closures=complete_owned_stdin_eof(slot,context,closed)
        return slot.stdin_observation_closures


def capture_lock_call(source_lease,call,args,fn):
    """Observe the actual selected constructor effect without replacing errors."""
    before=descriptor_inventory()
    receipt={'call':call,'args':args,'before':before,'source':source_lease.check()}
    try:value=fn()
    except OSError as error:
        receipt.update(result=-1,errno=error.errno,message=str(error))
        error.custody_lock_receipt=receipt
        raise
    receipt.update(result=value if type(value) is int else 0,errno=0,api_result=value)
    if call in ('open','dup'):
        try:
            receipt['identity']=identity(value)
            receipt['proc_link']=os.readlink('/proc/self/fd/'+str(value))
            receipt['proc_fdinfo']=Path('/proc/self/fdinfo/'+str(value)).read_bytes()
            if call=='dup':
                receipt['ofd']=kcmp(os.getpid(),os.getpid(),args['fd'],value,source_lease.check())
        except BaseException as error:
            receipt['readback_error']={'type':type(error).__qualname__,
                'module':type(error).__module__,'message':str(error),'args':error.args,
                'errno':getattr(error,'errno',None)}
            cleanup={'call':'close','args':{'fd':value},'source':source_lease.check()}
            try:
                result=os.close(value);cleanup.update(result=0,errno=0,api_result=result)
            except OSError as failure:
                cleanup.update(result=-1,errno=failure.errno,message=str(failure))
                error.add_note('Actual acquired-descriptor cleanup failed: '+str(failure))
            receipt['cleanup']=cleanup;error.custody_lock_receipt=receipt
            raise
    return value,receipt


def original_record(event):
    record=event['record']
    return record['original'] if type(record) is dict and set(record)=={'original','x5'} else record


def reference(journal,operation,kind):
    events=[event for event in journal.history(operation) if event['kind']==kind]
    require(events,'ROOT_RAW_PRIOR_'+kind+'_ABSENT')
    return events[-1]['event_id']


def process_identity(pid,start_tick=None):
    raw=(Path('/proc')/str(pid)/'stat').read_bytes()
    tail=raw[raw.rfind(b')')+2:].split()
    tick=int(tail[19])
    if start_tick is not None:require(tick==start_tick,'ROOT_RAW_PROCESS_START_CHANGED')
    return {'boot':Path('/proc/sys/kernel/random/boot_id').read_bytes(),'pid':pid,'start_tick':tick}


def poll_receipt(owner,fd):
    source=owner.source_lease.check()
    poll=select.poll();poll.register(fd,select.POLLIN|select.POLLHUP|select.POLLERR)
    events=poll.poll(0)
    return {'call':'poll','args':{'fd':fd,'events':select.POLLIN|select.POLLHUP|select.POLLERR,'timeout':0},
        'result':len(events),'errno':0,'source':source,
        'revents':0 if not events else events[0][1],'events':tuple(events)}


def process_wait(owner,fd,origin,recorded=None):
    return {'recorded':recorded,'origin':origin,'current':identity(fd),'poll':poll_receipt(owner,fd)}


def held_fds(owner):
    custody=getattr(owner,'custody',None)
    offer=getattr(owner,'current_offer',None)
    if offer is not None and owner.phase!='FRONT_OWNED':return dict(offer.fds)
    if custody is not None:fds=dict(custody.fds)
    else:
        lease=owner.lease;fds={str(path):fd for path,fd in lease.fds.items()}
        for authority,leaf in ((owner.principal.gate.issuer,'issuer.lock'),(owner.principal.gate.universe,'universe.lock')):
            fds[str(authority.state/leaf)]=authority.lock_fd
    journal=owner.custody_journal;fds[str(journal.lock_path)]=journal.lock_fd
    return fds


def lock_receipts(owner,before=None,fds=None):
    fds=held_fds(owner) if fds is None else fds
    roster=tuple({'path':path,'identity':identity(fd)} for path,fd in fds.items()) if before is None else before['held_locks']
    gate=getattr(getattr(owner,'principal',None),'gate',None)
    acquisitions={};old_acquisitions={};duplicates={}
    holders=[getattr(owner,'lease',None),getattr(gate,'issuer',None),
        getattr(gate,'universe',None),getattr(owner,'custody_journal',None),owner]
    lease=getattr(owner,'lease',None);guard=None if lease is None else lease.exec_custody
    old=None if guard is None else getattr(guard,'front',None)
    if old is not None:
        old_gate=old.principal.gate
        old_holders=[old.lease,old_gate.issuer,old_gate.universe,old.custody_journal]
        for holder in old_holders:
            old_acquisitions.update(getattr(holder,'lock_open_receipts',{}))
        holders[0:0]=old_holders
    for holder in holders:
        if holder is not None:
            acquisitions.update(getattr(holder,'lock_open_receipts',{}))
            for path,receipt in getattr(holder,'lock_duplicate_receipts',{}).items():
                duplicates.setdefault(path,[]).append({'receipt':receipt,'ofd':receipt.get('ofd')})
    for offer in (getattr(owner,'current_offer',None),None if guard is None else getattr(guard,'offer',None)):
        if offer is not None:
            for path,edge in offer.duplicate_receipts.items():
                duplicates.setdefault(path,[]).append(edge)
    rows=[]
    for item in roster:
        path=item['path'];fd=fds[path]
        named_fd,opened=syscall(owner,'open',{'path':path,'flags':os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC},
            lambda:os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC))
        try:named=identity(named_fd)
        finally:
            _,closed=syscall(owner,'close',{'fd':named_fd},lambda:os.close(named_fd))
        comparison=kcmp(os.getpid(),os.getpid(),fd,fd,owner.source_lease.check())
        receiver_comparison=None;broker=None
        custody=getattr(owner,'custody',None)
        intake=None if custody is None else getattr(custody,'subject_intake',None)
        if intake is not None:
            roles=[row for row in intake['transfer']['roles'] if row['lock_path']==path]
            require(len(roles)==1,'ROOT_RAW_ORIGINAL_RECEIVED_OFD_JOIN_ABSENT')
            received=roles[0];receiver_comparison=received['kcmp']
            broker=custody.sender_role_roster
            sender=[row for row in broker['roles'] if row['role']==received['role']]
            require(len(sender)==1,'ROOT_RAW_AUTHENTIC_SENDER_OFD_JOIN_ABSENT')
            comparison=sender[0]['kcmp'];flock=received['flock']
        else:
            _,flock=syscall(owner,'flock',{'fd':fd,'operation':fcntl.LOCK_EX|fcntl.LOCK_NB},
                lambda:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB))
        duplicate_rows=[]
        for edge in duplicates.get(path,()):
            proof=dict(edge);receipt=proof['receipt']
            if proof['ofd'] is None and receipt['result']==fd:
                proof['ofd']=kcmp(os.getpid(),os.getpid(),receipt['args']['fd'],fd,owner.source_lease.check())
            duplicate_rows.append(proof)
        acquisition=acquisitions.get(path)
        original_offer=None if guard is None else getattr(guard,'offer',None)
        if original_offer is not None and original_offer.fds.get(path)==fd:
            acquisition=old_acquisitions.get(path)
        rows.append({'path':path,'origin':item['identity'],'current':identity(fd),'named':named,
            'ofd':comparison,'flock':flock,'open':acquisition,
            'current_acquisition':acquisitions.get(path),
            'named_open':opened,'named_close':closed,'duplicates':tuple(duplicate_rows),
            'receiver_ofd':receiver_comparison,'sender_role_roster':broker})
    return tuple(rows)


def native_item(role,material,observation,provenance=None):
    item={'role':role,'material':material,'observation':observation}
    if provenance is not None:item['provenance']=provenance
    return item


def scoped_commit(resource,packet):
    from . import resource_scoped_run_ledger as S
    from .scoped_source_image import source_restore
    entries=[event for event in resource.scoped_service.committed_history() if event['packet']==S.record(packet)]
    require(len(entries)==1,'ROOT_RAW_EXACT_SCOPED_COMMIT_ABSENT')
    event=entries[0];source=source_restore(event['source'])
    provenance=raw_restore_archive(source['complete_scoped_capture_image'])
    return {'event':event,'raw':canonical(event),'material':packet,
        'observation':S.restore(event['native']),'provenance':provenance}


def scoped_capture(resource,reservation):
    from .root_scoped_capture_profile import capture_live_scoped
    p=resource.lease.canonical_operation_principal
    owner=getattr(p,'root_worker',None) or getattr(p,'root_worker_process',None)
    before=resource.current_snapshot();current,source,catalogue=resource._context(before)
    observed,facts,raw,classification=resource._capture(before,current)
    packet=resource._inspect(before,current,observed,facts,resource._request(before,reservation))
    captured=capture_live_scoped(resource,packet,raw,classification,
        resource.scoped_classification_materials,owner)
    roster=captured['roster']
    retained=getattr(owner,'_scoped_capture_rosters',None)
    if retained is None:retained=[];owner._scoped_capture_rosters=retained
    if all(item is not roster for item in retained):retained.append(roster)
    provenance={name:value for name,value in captured.items() if name!='roster'}
    packet=captured['material']
    return packet,resource.scoped_kernel.classify(packet),captured['observation'],provenance


def evidence(owner,operation,operands=None,*,native=(),primitive=None,before=None,current=None):
    from .root_worker_current_state import capture_owner_state
    source=owner.source_lease.check()
    custody=getattr(owner,'custody',None)
    frame=None if custody is None else custody.frame
    p=getattr(owner,'principal',None)
    if p is not None:
        envelope=exact_json(private_bytes(p.journal.path));events=envelope['body']['events']
        reserved=[row for row in events if row['operation']==operation and row['cause']=='RESERVED']
        require(len(reserved)==1,'ROOT_RAW_ORIGINAL_RESERVATION_ABSENT')
        reserved=reserved[0]
        capture=restore_operation(bytes.fromhex(reserved['capture']))
        use={'snapshot':restore_operation(bytes.fromhex(reserved['snapshot'])),
            'observation':reserved['native']['observation'],'event':digest(canonical(reserved))}
        request=capture['request']
    else:
        require(frame is not None,'ROOT_RAW_RECEIVED_ORIGINAL_FRAME_ABSENT')
        context=owner.custody_journal.capture_operation_context()
        envelope=context['operation_journal_envelope'];request=frame['original_request'];use=frame['original_native_use']
    before=capture_owner_state(owner) if before is None else before
    current=capture_owner_state(owner) if current is None else current
    channel=getattr(owner,'channel',None) or getattr(custody,'channel',None)
    if channel is None:
        slot=getattr(owner,'slots',{}).get(operation)
        channel=None if slot is None else slot.channel
    if channel is None:
        lease=getattr(owner,'lease',None);guard=None if lease is None else lease.exec_custody
        channel=None if guard is None else guard.owned.custody_channel
    actor=actor_identity(channel)
    profile={'schema':'worldline.custody-root-raw-v1','source':source,'actor':actor,'request':request,'use':use,
        'operation_journal_envelope':envelope,'owner_before':before,'owner_current':current,
        'captures':tuple({'role':item['role'],'provenance':item['provenance']} for item in native if 'provenance' in item)}
    if operands:profile.update(operands)
    profile['native_observations']=tuple(native)
    return {'root_evidence':profile,'native_observations':tuple(native),
        'primitive_inputs':{} if primitive is None else primitive}


def append(owner,operation,kind,record,operands=None,*,actor_role=None,**kwargs):
    supplied=evidence(owner,operation,operands,**kwargs)
    collector={'CLOSED_NS','CLOSED_OUTER','CLOSED_RAW','CLOSED_WITNESS','PHYSICAL_SETTLED','CUSTODY_RETURNED',
        'HISTORICAL_SETTLEMENT','FRONT_RECONSTRUCTION'}
    worker={'CUSTODY_ACK','ORIGINAL_PROGRESS','ORIGINAL_RESULT','HANDLER_TERMINAL','WORKER_RELINQUISH'}
    supplied['actor_role']=actor_role or ('RECONCILER' if kind=='RECONCILED' else
        'COLLECTOR' if kind in collector else 'WORKER' if kind in worker else 'FRONT')
    return owner.custody_journal.append(operation,kind,record,evidence=supplied)


def append_failure(raw):
    """Retain the actual saved mutation, with no guessed IDs or retry grant."""
    from .root_worker_codec import scoped_archive
    require(type(raw) is bytes,'ROOT_ACTUAL_APPEND_UNCERTAINTY_IMAGE_REQUIRED')
    saved=raw_restore_archive(raw);attempted=saved['attempted_event']
    retained=attempted['retained_record'];record=scoped_archive(retained)
    failed={name:attempted[name] for name in
        ('generation','operation','subject_kind','subject','subgeneration','kind')}
    failed['record_digest']=digest(record)
    item={'class':'CAppend','operation':attempted['operation'],
        'generation':attempted['generation'],'source':retained['x5']['source_identity'],
        'raw':{'append':raw,'failed_event':failed,'record':record}}
    return item,saved


def worker_liveness(worker,journal):
    """Measure the real namespace worker through its retained host proc mount."""
    execution=[event for event in journal.history(worker.operation) if event['kind']=='EXECUTION_NATIVE']
    require(len(execution)==1,'ROOT_RECOVERY_ACTUAL_EXECUTION_REFERENCE_REQUIRED')
    event=execution[0];original=original_record(event)
    recorded=raw_restore_archive(event['retained_record']['x5']['root_evidence'])['worker_identity']
    host_proc=worker.custody.origins['host_proc']
    pidfd,opened=capture_effect(worker.source_lease,'pidfd_open',
        {'pid':os.getpid(),'flags':0},lambda:os.pidfd_open(os.getpid(),0))
    def host_read(path):
        fd,opened_file=capture_effect(worker.source_lease,'openat',{'dirfd':host_proc,'path':path,
            'flags':os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC},
            lambda:os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=host_proc))
        receipts=[opened_file];chunks=[]
        try:
            while True:
                raw,read_receipt=capture_effect(worker.source_lease,'read',{'fd':fd,'count':65536},lambda:os.read(fd,65536))
                receipts.append(read_receipt)
                if not raw:break
                chunks.append(raw)
        finally:
            _,closed=capture_effect(worker.source_lease,'close',{'fd':fd},lambda:os.close(fd));receipts.append(closed)
        return b''.join(chunks),tuple(receipts)
    live=None
    try:
        fdinfo,fdinfo_reads=host_read('self/fdinfo/'+str(pidfd))
        process_stat,stat_reads=host_read(str(recorded['pid'])+'/stat')
        live={'recorded':recorded,'current_boot':Path('/proc/sys/kernel/random/boot_id').read_bytes(),
            'pidfd_open':opened,'pidfd_info':fdinfo,'stat':process_stat,'poll':poll_receipt(worker,pidfd),
            'namespace_context':{'actor':actor_identity(worker.custody.channel),'host_proc':identity(host_proc),
                'host_proc_fd':host_proc,'execution_event':event['event_id'],'execution':original,
                'reads':{'pidfd_info':fdinfo_reads,'stat':stat_reads}}}
    finally:
        _,closed=capture_effect(worker.source_lease,'close',{'fd':pidfd},lambda:os.close(pidfd))
        if live is not None:live['pidfd_close']=closed
    return live


def cause(owner,operation,error,raw,kind='CEvidence'):
    if kind=='CAppend':
        item,_saved=append_failure(raw['append'])
        require(item['operation']==operation,'ROOT_ACTUAL_APPEND_OPERATION_CHANGED')
        return item
    root=owner.custody_journal.root_state(operation)
    return {'class':kind,'operation':operation,'generation':root['generation'],
        'source':owner.source_lease.check(),'raw':raw,'error':{'type':type(error).__name__,'message':str(error)}}


def unknown(owner,operation,record,error,raw,kind='CEvidence',*,actor=None,actor_role=None):
    item=cause(owner,operation,error,raw,kind)
    operands={'cause':item}
    if kind=='CEvidence':operands['failed_material']=raw['actual']
    if kind=='CAppend':operands['append_uncertainty']=raw_restore_archive(raw['append'])
    if 'worker_report' in raw:operands['worker_report']=raw['worker_report']
    if actor is not None:operands['actor']=actor
    return append(owner,operation,'UNKNOWN',record,operands,actor_role=actor_role,
        primitive={'unknown_cause':item})


def seed(owner,current=None):
    from .root_worker_current_state import capture_owner_state
    current=capture_owner_state(owner) if current is None else current
    return {'owner':current,'prefix':tuple(event['event_id'] for event in owner.custody_journal.history())}


def selected_owners(owner,closers):
    """Bind owner API objects to factual descriptors before the selected closes."""
    rows=[]
    for name,_close in closers:
        rows.append({'owner':name,'api':'owner.close'})
    return tuple(rows)


def close_owner(owner,name,close):
    from .custody_subject_capture import fd_identity
    descriptors={}
    for path in Path('/proc/self/fd').iterdir():
        fd=int(path.name)
        try:descriptors[fd]={'fd':fd,'identity':fd_identity(fd)}
        except OSError:continue
    result,receipt=syscall(owner,'owner.close',{'owner':name,'descriptors':tuple(descriptors.values())},close)
    receipt['result']=result
    require(receipt['errno']==0,'ROOT_ACTUAL_OWNER_CLOSE_API_FAILED')
    readback=[]
    for fd,old in descriptors.items():
        try:value=fcntl.fcntl(fd,fcntl.F_GETFD);error=0
        except OSError as failure:value=-1;error=failure.errno
        readback.append({'before':old,'identity':None if error else fd_identity(fd),
            'call':'fcntl','args':{'fd':fd,'command':fcntl.F_GETFD},
            'result':value,'errno':error,'source':receipt['source']})
    receipt['readback']=tuple(readback)
    return {'owner':name,'close':receipt}


def acquisition_capture(job,item):
    observation=item.quiescence_observation()
    return {'job':job,'observation':observation,'observation_raw':canonical(observation)}


def execution_ack(owner,owned,measured,event):
    from .root_worker_credentials import commit_ack_bytes
    from .root_worker_custody import _memfd
    witness={'kind':event['kind'],'operation':event['operation'],
        'event_id':event['event_id'],'record':original_record(event)}
    witness_raw=raw_archive(witness);body=commit_ack_bytes(measured.raw_frame,witness_raw)
    fd=_memfd(witness_raw);channel=owned.credential_receiver
    peer=struct.pack('@iII',os.getpid(),os.geteuid(),os.getegid())
    args={'fd':channel.fileno(),'channel':identity(channel.fileno()),'body':body,
        'rights':(fd,),'credentials':peer,'flags':socket.MSG_NOSIGNAL}
    try:
        sent,send=syscall(owner,'sendmsg',args,lambda:channel.sendmsg([body],[
            (socket.SOL_SOCKET,socket.SCM_CREDENTIALS,peer),
            (socket.SOL_SOCKET,socket.SCM_RIGHTS,array.array('i',[fd]))],socket.MSG_NOSIGNAL))
        require(sent==len(body),'ROOT_EXECUTION_ACK_SEND_FAILED')
    finally:os.close(fd)
    poll=select.poll();poll.register(channel.fileno(),select.POLLIN|select.POLLHUP|select.POLLERR);poll.poll()
    import termios
    count=array.array('i',[0]);fcntl.ioctl(channel.fileno(),termios.FIONREAD,count,True)
    require(count[0]>0,'ROOT_EXECUTION_ACK_RECEIVE_TRANSCRIPT_ABSENT')
    raw,controls,flags,_address=channel.recvmsg(count[0],socket.CMSG_SPACE(struct.calcsize('@iII')),
        socket.MSG_CMSG_CLOEXEC)
    require(len(raw)==count[0] and flags==0 and len(controls)==1 and
        controls[0][:2]==(socket.SOL_SOCKET,socket.SCM_CREDENTIALS),
        'ROOT_EXECUTION_ACK_RECEIVE_TRANSCRIPT_UNKNOWN')
    receiver_credentials=controls[0][2]
    require(struct.unpack('@iII',receiver_credentials)[0]==owned.worker_host_pid,
        'ROOT_EXECUTION_ACK_MEASURED_RECEIVER_CHANGED')
    fields=raw.split(b'\n',4)
    require(len(fields)==5 and fields[0]==b'WL-ROOT-WORKER-ACK-RECEIPT-v1',
        'ROOT_EXECUTION_ACK_RECEIVE_TRANSCRIPT_MALFORMED')
    received=int(fields[1]);message_flags=int(fields[2]);receive_fd=int(fields[3])
    received_peer=fields[4][:struct.calcsize('@iII')];received_body=fields[4][struct.calcsize('@iII'):]
    require(received==len(body) and received_body==body and message_flags==0,
        'ROOT_EXECUTION_ACK_ORIGINAL_RECEIVE_CHANGED')
    receive={'call':'recvmsg','args':{'fd':receive_fd,'flags':socket.MSG_CMSG_CLOEXEC},
        'body':received_body,'sender_credentials':received_peer,'msg_flags':message_flags,
        'result':received,'errno':0,'source':send['source'],
        'transport':{'raw':raw,'sender_credentials':receiver_credentials,'channel':identity(channel.fileno())},
        'namespace_identity':owned.held['namespace_identity'],'worker_pidfd':identity(owned.worker_pidfd)}
    opened,opened_receipt=syscall(owner,'pidfd_open',{'pid':owned.worker_host_pid,'flags':0},
        lambda:os.pidfd_open(owned.worker_host_pid,0))
    require(opened is not None,'ROOT_EXECUTION_ACK_RECEIVER_PIDFD_UNAVAILABLE')
    try:
        receive['context']={'namespace_identity':owned.held['namespace_identity'],
            'worker':{'recorded':owned.worker_identity,
                'current_boot':Path('/proc/sys/kernel/random/boot_id').read_bytes(),
                'pidfd_open':opened_receipt,'pidfd_info':Path('/proc/self/fdinfo/'+str(opened)).read_bytes(),
                'stat':(Path('/proc')/str(owned.worker_host_pid)/'stat').read_bytes(),
                'poll':poll_receipt(owner,opened)}}
    finally:os.close(opened)
    return body,{'execution_event':event['event_id'],'request':owned.request.observation(),
        'ticket':measured.ticket,'peer':peer,'measured_frame':measured.raw_frame,
        'frame':body,'witness':witness,'witness_raw':witness_raw,'send':send,'receive':receive}


def wait_launcher(owner,launcher):
    source=owner.source_lease.check()
    pid,status=os.waitpid(launcher.pid,0)
    receipt={'call':'waitpid','args':{'pid':launcher.pid,'options':0},'result':pid,
        'status':status,'errno':0,'source':source}
    launcher.returncode=os.waitstatus_to_exitcode(status)
    return launcher.returncode,receipt


def prepare_capture():
    # Selected modules are loaded before syscall source receipts.  Import
    # events are part of the genuine source lease; never rewrite a receipt's
    # source to a later, different import roster.
    from .root_worker_codec import _schema
    from .root_worker_current_state import warm_operation_context_sources
    warm_operation_context_sources()
    from . import (custody_subject_capture,root_worker_subject_custody,
        root_worker_subject_transfer,root_worker_subject_spool,root_worker_subject_pump,
        root_worker_subject_service,root_worker_subject_relay,root_worker_subject_output,
        root_worker_subject_sync,root_worker_subject_front,
        root_worker_serving_peer,root_worker_current_state,protected_root_observation,
        root_owned_descriptor_roster,root_scoped_capture_profile)
    _schema()
