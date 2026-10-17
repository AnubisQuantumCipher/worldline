"""Lossless original result transport with post-receive raw custody evidence.

The worker sends an immutable original payload.  Its real recipient commits the
report only after recvmsg, SCM credentials and the sealed memfd are observed.
No successful send is reported as a successful receive.
"""
import asyncio,fcntl,os,threading
from .root_worker_custody import _memfd,_read_memfd,_send_fd,_receive_fd,identity,channel_source
from .protected_startup import require
from .root_worker_codec import raw_archive
from .root_worker_root_evidence import append,original_record,native_item,reference,lock_receipts,seed,unknown,poll_receipt


def send_event(channel,event,source=None):
    fd=_memfd(raw_archive(event));receipts=[]
    try:_send_fd(channel,fd,receipts=receipts,source=source)
    finally:os.close(fd)
    return tuple(receipts)


def receive_event(channel,journal,owner=None):
    receipts=[];fd,sender=_receive_fd(channel,receipts=receipts,source=journal.owner.source_lease.check())
    try:
        event,raw=_read_memfd(fd,original=True)
        transport={'raw':raw,'sender_credentials':sender,'receive':receipts[-1],
            'channel':channel_source(channel)['identity'],'channel_source':channel_source(channel),
            'sealed_memfd':{'fd':fd,'identity':identity(fd),'seals':fcntl.fcntl(fd,fcntl.F_GET_SEALS)}}
        if event['kind'] in ('INPUT_EOF_PREPARE','INPUT_EOF_RECEIVED','INPUT_EOF_CANCEL','INPUT_EOF'):
            require(owner is not None and event['operation']==owner.operation,
                    'ROOT_STDIN_EOF_ACTUAL_FRONT_RECEIVER_REQUIRED')
            owner._sender_owned(transport)
            request=event['record']
            service=owner.slot.custody_offer.subject_service
            try:
                if event['kind']=='INPUT_EOF_PREPARE':
                    prepared=service.stdin_eof_prepare(request,transport=transport)
                    response={'kind':'INPUT_EOF_PREPARED','operation':owner.operation,
                        'record':prepared}
                elif event['kind']=='INPUT_EOF_RECEIVED':
                    joined=service.stdin_eof_received(request,transport=transport)
                    response={'kind':'INPUT_EOF_RECEIVED_ACK','operation':owner.operation,
                        'record':joined}
                elif event['kind']=='INPUT_EOF_CANCEL':
                    cancelled=service.stdin_eof_cancel(request,transport=transport)
                    response={'kind':'INPUT_EOF_CANCELLED','operation':owner.operation,
                        'record':{'request':request,'cancelled':cancelled}}
                else:
                    closures=service.stdin_eof(request,transport=transport)
                    response={'kind':'INPUT_EOF_ACK','operation':owner.operation,
                        'record':{'request':request,'closures':closures}}
            except BaseException as error:
                response={'kind':'INPUT_EOF_FAILED','operation':owner.operation,
                    'record':{'request':request,'error':{
                        'module':type(error).__module__,'type':type(error).__qualname__,
                        'message':str(error),'args':error.args,
                        'errno':getattr(error,'errno',None),
                        'filename':getattr(error,'filename',None),
                        'filename2':getattr(error,'filename2',None)}}}
            transport['wire_event']=event
            transport['response']=response
            transport['response_send']=send_event(channel,response,owner.front.source_lease.check())
            retained=getattr(owner,'stdin_eof_reports',None)
            if retained is None:retained=[];owner.stdin_eof_reports=retained
            retained.append({'request':event,'transport':transport,'response':response})
            return event,transport
        if event['kind']=='ROSTER_EVIDENCE':
            require(owner is not None and event['operation']==owner.operation,
                    'ROOT_ROSTER_ACTUAL_FRONT_RECEIVER_REQUIRED')
            owner._sender_owned(transport)
            report=event['receiver_report'];operands=dict(report['evidence'])
            operands['receiver_report']={'report':report,'event':event,'raw':raw,
                'transport':transport}
            committed=append(owner.front,event['operation'],'ROSTER_EVIDENCE',
                event['record'],operands,native=report['native'])
            transport['wire_event']=event
            send_event(channel,committed,owner.front.source_lease.check())
            return committed,transport
        if event['kind'] in ('ORIGINAL_PROGRESS','ORIGINAL_RESULT','HANDLER_TERMINAL','UNKNOWN'):
            require(owner is not None,'ROOT_REPORT_ACTUAL_RECEIVER_REQUIRED')
            owner._sender_owned(transport)
            operation=event['operation'];record=event['record']
            if event['kind']=='UNKNOWN':
                error=RuntimeError(record['value']['message'])
                report={'event':event,'raw':raw,'transport':transport,
                    'worker':owner.worker_identity,'worker_actor':owner.worker_actor,
                    'execution_event':owner.execution_event['event_id'],
                    'worker_pidfd':{'fd':owner.worker_pidfd,'origin':owner.worker_pidfd_origin['descriptor'],
                        'current':identity(owner.worker_pidfd),
                        'poll':poll_receipt(owner.front,owner.worker_pidfd)}}
                if 'append_uncertainty' in event:
                    committed=unknown(owner.front,operation,record,error,
                        {'append':event['append_uncertainty'],'worker_report':report},
                        kind='CAppend',actor_role='RECONCILER')
                else:
                    committed=unknown(owner.front,operation,record,error,
                        {'expected':'complete original handler custody','actual':record['value'],
                            'worker_report':report},
                        actor=owner.worker_actor,actor_role='WORKER')
            else:
                value=record['value'];native=()
                if event['kind']=='HANDLER_TERMINAL':
                    retained=value['native_event']
                    native=(native_item('root-admission',retained['material'],retained['observation'],retained['provenance']),)
                report={'event':event,'raw':raw,'sender_credentials':sender,
                    'request':record['original_request'],'use':owner.original_use,
                    'execution_event':owner.execution_event['event_id'],'worker':owner.worker_identity,
                    'channel':transport['channel'],'receive':transport['receive'],'sealed_memfd':transport['sealed_memfd']}
                committed=append(owner.front,operation,event['kind'],record,
                    {'report':report,'actor':owner.worker_actor},native=native)
            if 'worker_output' in event:
                transport['worker_output']=event['worker_output']
            transport['wire_event']=event
            if event['kind']=='HANDLER_TERMINAL':send_event(channel,committed,journal.owner.source_lease.check())
            return committed,transport
        journal.require_event(event)
        return event,transport
    finally:os.close(fd)


class WorkerResultChannel:
    def __init__(self,worker):
        from .protected_root_worker import RootWorkerProcess
        require(type(worker) is RootWorkerProcess,'ROOT_WORKER_REAL_RESULT_CHANNEL_OWNER_REQUIRED')
        self.worker=worker;self.channel=worker.custody.channel;self.journal=worker.custody_journal
        self.transport_lock=threading.RLock()
        self.stdin_eof_exchanges=[]
    def prepare_stdin_eof(self,request):
        return self._stdin_exchange('INPUT_EOF_PREPARE','INPUT_EOF_PREPARED',request)
    def join_stdin_eof_received(self,capture):
        return self._stdin_exchange('INPUT_EOF_RECEIVED','INPUT_EOF_RECEIVED_ACK',capture)
    def cancel_stdin_eof(self,request):
        return self._stdin_exchange('INPUT_EOF_CANCEL','INPUT_EOF_CANCELLED',request)
    def request_stdin_eof(self,request):
        return self._stdin_exchange('INPUT_EOF','INPUT_EOF_ACK',request)
    def _stdin_exchange(self,kind,reply_kind,request):
        event={'kind':kind,'operation':self.worker.operation,'record':request}
        exchange={'request':event}
        self.stdin_eof_exchanges.append(exchange)
        with self.transport_lock:
            exchange['send']=send_event(self.channel,event,self.worker.source_lease.check())
            receipts=[]
            fd,sender=_receive_fd(self.channel,receipts=receipts,source=self.worker.source_lease.check())
            try:
                response,raw=_read_memfd(fd,original=True)
                exchange['response']=response
                exchange['transport']={'raw':raw,'sender_credentials':sender,
                    'receive':tuple(receipts),'channel_source':channel_source(self.channel),
                    'sealed_memfd':{'fd':fd,'identity':identity(fd),
                        'seals':fcntl.fcntl(fd,fcntl.F_GET_SEALS)}}
                received_join=kind=='INPUT_EOF_RECEIVED' and response['kind']==reply_kind
                original_request=request['request'] if received_join else request
                require(sender==self.worker.custody.sender
                    and response['operation']==self.worker.operation
                    and response['kind'] in (reply_kind,'INPUT_EOF_FAILED')
                    and raw_archive(response['record']['request'])==raw_archive(original_request),
                    'ROOT_STDIN_EOF_EXACT_FRONT_RECEIPT_CHANGED')
                require(response['kind']==reply_kind,'ROOT_STDIN_EOF_FRONT_CLOSURE_FAILED')
                if received_join:
                    require(raw_archive(response['record']['received'])==raw_archive(request['received']),
                        'ROOT_STDIN_EOF_ORIGINAL_RECEIVED_CAPTURE_CHANGED')
                return {'record':response['record'],'transport':exchange['transport']}
            finally:os.close(fd)
    def _send_report(self,event):
        with self.transport_lock:
            receipts=send_event(self.channel,event,self.worker.source_lease.check())
            committed=None
            if event['kind']=='HANDLER_TERMINAL':
                committed=receive_committed(self.channel,self.journal,event)
            return receipts,committed
    async def send(self,kind,value,*,worker_output=None):
        if kind=='UNKNOWN':
            # A factual failure report cannot revive the poisoned effect owner.
            self.worker.source_lease.check()
        else:self.worker.intact()
        record={'operation':self.worker.operation,'original_request':self.worker.request.observation(),'value':value}
        event={'operation':self.worker.operation,'kind':kind,'record':record}
        if kind in ('ORIGINAL_PROGRESS','ORIGINAL_RESULT'):
            require(type(worker_output) is dict,'ROOT_WORKER_EXACT_INITIAL_OUTPUT_CAPSULE_REQUIRED')
            event['worker_output']=worker_output
        if kind=='UNKNOWN' and hasattr(self.worker,'last_initial_output'):
            event['worker_output']=self.worker.last_initial_output
        if kind=='UNKNOWN' and self.journal.poisoned:
            event['append_uncertainty']=self.journal.capture_uncertainty()
        receipts,committed=await asyncio.to_thread(self._send_report,event)
        self.worker.last_result_transport={'event':event,'send':receipts}
        if kind=='HANDLER_TERMINAL':self.worker.terminal_event=committed
        return event
    async def commit_custody(self,material,native):
        require(native.status=='ROOT_READY_CONJUNCTION' and self.worker.authority.decide(material)==native,
                'ROOT_WORKER_FULL_NATIVE_CUSTODY_ACK_REFUSED')
        capture=self.worker._root_capture;current=capture.provenance['owner_state']
        report=self.worker.custody.worker_roster_report
        proposed={'operation':self.worker.operation,'kind':'ROSTER_EVIDENCE',
            'record':report['original'],'receiver_report':report}
        sends=await asyncio.to_thread(send_event,self.channel,proposed,self.worker.source_lease.check())
        self.worker.roster_send={'event':proposed,'send':sends}
        roster=await asyncio.to_thread(receive_committed,self.channel,self.journal,proposed)
        self.worker.roster_event=roster
        material=self.worker.capture_root_material(self.worker.custody.frame,self.channel,self.worker.request)
        native=self.worker.authority.decide(material)
        capture=self.worker._root_capture;current=capture.provenance['owner_state']
        event=append(self.worker,self.worker.operation,'CUSTODY_ACK',{'frame':self.worker.custody.frame,
            'native_material':material,'native':native,'received_sender':self.worker.custody.sender,
            'actual_received_locks':{path:identity(fd) for path,fd in self.worker.custody.fds.items()}},
            {'transfer_event':reference(self.journal,self.worker.operation,'TRANSFER_SENT'),
                'locks':lock_receipts(self.worker,current),'seed':seed(self.worker,current)},
            current=current,native=(native_item('root-admission',material,native,capture.provenance),))
        self.journal.require_event(event);self.worker.custody_ack=event
        self.worker.custody.start_live_subject_service(self.worker)
        self.worker.initial_request_admission=self.worker.custody.activate_initial_request(self.worker)
        await asyncio.to_thread(send_event,self.channel,event,self.worker.source_lease.check())
        return event


def receive_committed(channel,journal,original):
    receipts=[];fd,sender=_receive_fd(channel,receipts=receipts,source=journal.owner.source_lease.check())
    try:
        event,raw=_read_memfd(fd,original=True);journal.require_event(event)
        require(event['kind']==original['kind'] and event['operation']==original['operation']
            and event['record']==original['record'],'ROOT_WORKER_TERMINAL_COMMIT_RECEIPT_CHANGED')
        return event
    finally:os.close(fd)
