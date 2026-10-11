"""Live post-ACK request/OFD transport using actual retained descriptor owners.

The initial request remains the original ROOT request. This separate connected
channel serves new requests only after the native ROOT custody acknowledgement.
It carries whole sealed original DTOs and per-syscall SCM transcripts; EOF,
shutdown and message acknowledgement are never root or descriptor closure.
"""
from __future__ import annotations
import asyncio,json,os,select,socket,sqlite3,threading
from contextlib import contextmanager
from .canonical import canonical_bytes
from .client_peer import KernelPeer,RequestPeer,request_scope
from .custody_subject_capture import actor_identity,close_descriptor,fd_identity,kcmp,original_roles,role_roster,socket_capture,socket_cookie
from .root_worker_codec import raw_archive,original_archive
from .root_worker_subject_custody import SubjectCustody
from .root_worker_subject_transfer import _stream,offer_descriptors
from .protected_startup import require

DOMAIN='worldline.live-subject-service-v1'


def _send_message(channel,value,source,receipts):
    from .root_worker_custody import _memfd,_send_fd
    fd=_memfd(raw_archive(value))
    try:return _send_fd(channel,fd,receipts,source)
    finally:os.close(fd)


def _receive_message(channel,source,receipts):
    from .root_worker_custody import _receive_fd,_read_memfd
    fd,sender=_receive_fd(channel,receipts,source)
    try:value,raw=_read_memfd(fd,original=True)
    finally:os.close(fd)
    require(type(value) is dict and value.get('schema')==DOMAIN,
        'CUSTODY_LIVE_COMPLETE_ORIGINAL_MESSAGE_REQUIRED')
    return value,raw,sender


def _message(kind,**fields):
    return dict(schema=DOMAIN,kind=kind,**fields)


def _root_native(worker,cause,require_ready=True,*,subject_roster=None):
    material=worker.capture_root_material(worker.custody.frame,worker.custody.channel,worker.request,
        subject_roster=subject_roster)
    observation=worker.authority.decide(material) if require_ready else worker.authority.observe(material)
    retained=worker.retain_native(cause,material,observation)
    return ({'role':'root-admission','material':retained['material'],
        'observation':retained['observation'],'provenance':retained['provenance']},)


def _response_error(request_id,error):
    from .errors import WorldlineError,storage_error
    if isinstance(error,WorldlineError):detail=error.as_dict()
    elif isinstance(error,(OSError,sqlite3.Error)):detail=storage_error(error).as_dict()
    else:detail={'code':'INTERNAL_ERROR','message':'daemon operation failed','details':{}}
    return {'id':request_id,'ok':False,'result':None,'error':detail}


def _write_line(peer,line,source,receipts):
    """Write exact original NDJSON bytes, retaining real nonblocking outcomes."""
    require(type(line) is bytes and line.endswith(b'\n'),'CUSTODY_LIVE_ORIGINAL_LINE_REQUIRED')
    fd=peer.peer.descriptor();position=0
    while position<len(line):
        offered=line[position:]
        try:count=os.write(fd,offered)
        except BlockingIOError as error:
            receipt={'call':'write','fd':fd,'offered':offered,'raw':None,
                'result':-1,'errno':error.errno,'source':source,'wait':[]}
            receipts.append(receipt)
            poller=select.poll();poller.register(fd,select.POLLOUT|select.POLLERR|select.POLLHUP)
            receipt['wait'].append({'call':'poll','events':poller.poll(),'source':source})
            continue
        except OSError as error:
            receipts.append({'call':'write','fd':fd,'offered':offered,'raw':None,
                'result':-1,'errno':error.errno,'source':source})
            raise
        receipts.append({'call':'write','fd':fd,'offered':offered,'raw':offered[:count],
            'result':count,'errno':0,'source':source})
        require(count>0,'CUSTODY_LIVE_RESPONSE_WRITE_UNKNOWN');position+=count
    return line


def _write_response(peer,value,source,receipts):
    return _write_line(peer,canonical_bytes(value)+b'\n',source,receipts)


class RequestEscrow:
    def __init__(self,service,request):
        self.service=service;self.peer=request.duplicate()
        self.subject=None;self.original=None;self.transfer=None;self.roles=None
        self.sent=[];self.received=[];self.original_messages=[];self.response_writes=[]
        self.prepared=None;self.intake=None;self.response=None;self.failure=None
        self.relay_admitted=threading.Event();self.output_pending={};self.output_written=[];self.next_output=0


class FrontSubjectService:
    def __init__(self,offer):
        self.offer=offer;self.owner=offer.slot.front
        self.channel,self.worker_channel=socket.socketpair(socket.AF_UNIX,socket.SOCK_STREAM|socket.SOCK_CLOEXEC)
        self.channel.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1)
        self.relay_channel,self.worker_relay_channel=socket.socketpair(socket.AF_UNIX,socket.SOCK_STREAM|socket.SOCK_CLOEXEC)
        self.relay_channel.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1)
        self.worker_relay_channel.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1)
        self.relay_send_receipts=[];self.relay_receive_receipts=[];self.relay_endpoint=None
        self.worker_channel.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1)
        self.lock=asyncio.Lock();self.escrows={};self.send_receipts=[];self.receive_receipts=[]
        self.drain_transfers=[];self.close_receipts=[];self.closed=False
        self.registry_rosters=[]
        self.source_syncs=[]
        self.stdin_eof_records=[]
        self.stdin_barrier_condition=threading.Condition();self.stdin_barriers={};self.message_failure=None
        self.send_lock=threading.Lock();self.stdin_send_cut=None;self.stdin_prepare_records=[]
        from .root_worker_subject_messages import SubjectMessageReader
        self.message_reader=SubjectMessageReader(self,self.channel,self.receive_receipts)
        from .root_worker_subject_relay import FrontRelayEndpoint
        self.relay_endpoint=FrontRelayEndpoint(self)
    def descriptors(self):
        result=dict(offer_descriptors(self.offer))
        result['service/front']=self.channel.fileno()
        result['service/front-relay']=self.relay_channel.fileno()
        for name,escrow in self.escrows.items():result['subject/'+name]=escrow.peer.peer.descriptor()
        for role,pump in self.owner.subject_pumps.items():
            if pump.fd is not None:result['reader/'+role]=pump.fd
            result['spool/'+role]=pump.spool_fd
        return result
    def native(self,cause,require_ready=False):
        material=self.owner.capture_root_material(self.offer.frame,self.offer.slot.channel,self.offer.request)
        observation=self.owner.authority.decide(material) if require_ready else self.owner.authority.observe(material)
        retained=self.owner.retain_native(cause,material,observation)
        return ({'role':'root-admission','material':retained['material'],
            'observation':retained['observation'],'provenance':retained['provenance']},)
    async def _send(self,value):
        return await asyncio.to_thread(self.send_message,value)
    def send_message(self,value):
        with self.send_lock:
            return _send_message(self.channel,value,self.owner.source_lease.check(),self.send_receipts)
    def send_prepare(self,observation,fd,receipts):
        from .root_worker_custody import _send_fd
        with self.send_lock:
            source=self.owner.source_lease.check()
            _send_message(self.channel,_message('PREPARE',request=observation),source,self.send_receipts)
            return _send_fd(self.channel,fd,receipts,source)
    def send_roles(self,value,descriptors,roles,operation,sent):
        from .root_worker_custody import _send_fd
        with self.send_lock:
            source=self.owner.source_lease.check()
            _send_message(self.channel,value,source,self.send_receipts)
            for row in roles:_send_fd(self.channel,descriptors[row['role']],sent,source)
            _send_message(self.channel,_message('SEND_TRANSCRIPT',operation=operation,send=sent),
                source,self.send_receipts)
    def stdin_eof_prepare(self,preflight,*,transport):
        require(type(preflight) is dict and set(preflight)=={'bound','original_writer'},
            'CUSTODY_LIVE_COMPLETE_ORIGINAL_STDIN_PREFLIGHT_REQUIRED')
        retained={'request':preflight,'transport':transport,'front_barrier':[],
            'failure':None,'released':None}
        self.stdin_prepare_records.append(retained)
        self.send_lock.acquire()
        try:
            require(self.stdin_send_cut is None,'CUSTODY_LIVE_ORIGINAL_STDIN_PREFLIGHT_OVERLAP')
            self.stdin_send_cut=retained
            _send_message(self.channel,_message('INPUT_EOF_FRONT_BARRIER',request=preflight),
                self.owner.source_lease.check(),retained['front_barrier'])
            return {'request':preflight,'prepared':{'front_barrier':tuple(retained['front_barrier']),
                'transport':transport}}
        except BaseException as error:
            retained['failure']={'class':type(error).__name__,'message':str(error),
                'errno':getattr(error,'errno',None)}
            self.stdin_send_cut=None;self.send_lock.release()
            raise
    def stdin_eof_cancel(self,preflight,*,transport):
        retained=self.stdin_send_cut
        require(retained is not None and raw_archive(retained['request'])==raw_archive(preflight),
            'CUSTODY_LIVE_ORIGINAL_STDIN_CUT_REQUIRED')
        retained['released']={'request':preflight,'transport':transport,'reason':'CANCEL'}
        self.stdin_send_cut=None;self.send_lock.release()
        return retained['released']
    def stdin_eof_received(self,capture,*,transport):
        cut=self.stdin_send_cut
        require(cut is not None and raw_archive(cut['request'])==raw_archive(capture['request']),
            'CUSTODY_LIVE_ORIGINAL_STDIN_CUT_REQUIRED')
        retained={'capture':capture,'transport':transport,'joined':[],'failure':None}
        cut.setdefault('received_joins',[]).append(retained)
        try:
            for item in capture['received']:
                joined=self._broker({'roles':item['roles']})
                profile={'roles':joined['roles'],'source':self.owner.source_lease.check(),
                    'actor':actor_identity(self.channel),
                    'worker_pidfd':fd_identity(self.offer.origins['worker_pidfd']),
                    'worker_host_pid':self.offer.slot.owned.worker_host_pid}
                retained['joined'].append({'received':item,'roles':joined['roles'],'profile':profile})
        except BaseException as error:
            retained['failure']={'class':type(error).__name__,'message':str(error),
                'errno':getattr(error,'errno',None)}
            raise
        return {'request':capture['request'],'received':capture['received'],
            'joined':tuple(retained['joined'])}
    async def _receive(self):
        return await asyncio.to_thread(self.message_reader.take)
    def observe_service_control(self,value,transport):
        if value['kind']!='INPUT_EOF_BARRIER':return False
        self.observe_stdin_barrier('SERVICE',value['request'],transport)
        return True
    def observe_stdin_barrier(self,channel,request,transport):
        key=raw_archive(request)
        with self.stdin_barrier_condition:
            observed=self.stdin_barriers.setdefault(key,{})
            require(channel not in observed,'CUSTODY_LIVE_STDIN_BARRIER_REPLAY')
            observed[channel]=transport;self.stdin_barrier_condition.notify_all()
    def message_reader_failed(self,error):
        with self.stdin_barrier_condition:
            self.message_failure=error;self.stdin_barrier_condition.notify_all()
    def _roles(self):
        extended=self.owner._retained_owned_roster.extend_owned(self.owner,self)
        self.registry_rosters.append(extended);self.latest_registry=extended
        self.owner._retained_owned_roster=extended
        descriptors=extended.fds;source=self.owner.source_lease.check()
        locks={row['descriptor']:row['path'] for row in extended.frame['lease_locks']}
        return descriptors,original_roles(descriptors,source,actor_identity(self.channel),
            fd_identity(self.offer.origins['worker_pidfd']),locks)
    def _broker(self,transfer):
        source=self.owner.source_lease.check();actor=actor_identity(self.channel)
        pid=self.offer.slot.owned.worker_host_pid
        rows=[]
        for observed in transfer['roles']:
            row=dict(observed,worker_kcmp=observed['kcmp'],kcmp_source=source,kcmp_actor=actor)
            row['kcmp']=kcmp(actor['pid'],pid,row['front_fd'],row['worker_fd'],source)
            rows.append(row)
        return dict(transfer,roles=rows)
    async def dispatch_line(self,caller,line,writer):
        """Use the original public protocol without consulting the closed Store."""
        from .errors import InvalidRequest,WorldlineError
        request_id=None;peer=None
        try:
            try:document=json.loads(line.decode('utf-8','strict'))
            except (UnicodeDecodeError,json.JSONDecodeError) as error:
                raise InvalidRequest('request is not UTF-8 JSON') from error
            if not isinstance(document,dict) or set(document)!={'id','op','args'}:
                raise InvalidRequest('request must have exactly id, op, and args fields')
            request_id=document['id']
            if isinstance(request_id,bool) or not isinstance(request_id,(str,int)):
                raise InvalidRequest('request id must be a string or integer')
            if not isinstance(document['op'],str) or not isinstance(document['args'],dict):
                raise InvalidRequest('op must be a string and args must be an object')
            if caller._operations.get(document['op']) is None:
                raise WorldlineError('UNKNOWN_OPERATION',f"unknown daemon operation: {document['op']}")
            peer=RequestPeer.capture(writer,line=line,operation=document['op'],request_id=request_id)
        except (WorldlineError,OSError,sqlite3.Error) as error:
            await caller._send(writer,_response_error(request_id,error))
            return
        try:
            await self.invoke_request(peer,mode='RELAY')
        finally:
            from .client_peer import peer_read_source
            with peer_read_source(self.owner.source_lease.check()):
                peer.close()
    async def invoke_request(self,request,*,mode='FRESH'):
        from .root_worker_custody import _send_fd
        async with self.lock:
            require(not self.closed,'CUSTODY_LIVE_SERVICE_CLOSED')
            require(mode in ('FRESH','RELAY'),'CUSTODY_LIVE_ACTUAL_TRANSPORT_MODE_REQUIRED')
            self.owner.custody_journal.require_event(self.offer.ack_event)
            identifier=request.observation()['observationId']
            require(identifier not in self.escrows,'CUSTODY_LIVE_REQUEST_REPLAY')
            escrow=RequestEscrow(self,request);self.escrows[identifier]=escrow
            try:
                await asyncio.to_thread(self.send_prepare,request.observation(),
                    escrow.peer.peer.descriptor(),escrow.sent)
                source=self.owner.source_lease.check()
                prepared,raw,sender=await self._receive();escrow.original_messages.append((prepared,raw,sender))
                require(prepared['kind'] in ('PREPARED','PREPARE_FAILED') and prepared['request']==identifier,
                    'CUSTODY_LIVE_PREPARE_BINDING_REQUIRED')
                if prepared['kind']=='PREPARE_FAILED':
                    # No native reservation/subject exists. This is the original
                    # error envelope from the actual live canonical principal.
                    _write_response(escrow.peer,prepared['response'],source,escrow.response_writes)
                    return prepared['response']
                operation=prepared['operation'];escrow.prepared=prepared
                descriptors,roles=self._roles();escrow.roles=roles
                subject=SubjectCustody(self.owner,operation,'REQUEST',identifier,root_operation=self.offer.slot.operation)
                escrow.subject=subject;subject.request_queued(escrow.peer,roles)
                escrow.original=subject.last_original
                front=socket_capture(escrow.peer.peer.descriptor(),source)
                cookie,cookie_receipt=socket_cookie(escrow.peer.peer.descriptor(),source)
                transfer={'mode':mode,'frame':None,'sender':actor_identity(self.channel)['credentials'],
                    'received_sender':None,'send':None,'receive':None,'roles':role_roster(roles,descriptors,source),
                    'roster':roles,'worker_document':None,'origin_user_ns':os.readlink('/proc/self/ns/user'),
                    'reader_user_ns':None,'origin_pid_ns':os.readlink('/proc/self/ns/pid'),'reader_pid_ns':None,
                    'held_pid_ns':os.readlink('/proc/self/fd/'+str(self.offer.origins['worker_namespace'])),
                    'host_cookie':cookie,'reader_cookie':None,'host_cookie_receipt':cookie_receipt,
                    'reader_cookie_receipt':None}
                escrow.transfer=transfer
                transfer['original_frame']=raw_archive(self.latest_registry.frame)
                from .root_worker_subject_transfer import role_socket_document
                carrier=socket_capture(self.channel.fileno(),source)
                transfer.update(send_channel=carrier,send_channel_document=role_socket_document(carrier),
                    receive_channel=None,receive_channel_document=None)
                if mode=='RELAY':
                    from .root_worker_subject_transfer import role_socket_document
                    context=subject.journal.subject_context(operation,'REQUEST',identifier,escrow.original,
                        root_operation=subject.root_operation,kind='REQUEST_TRANSFER_INTENT',actor_role='FRONT')
                    channel=socket_capture(self.relay_channel.fileno(),source)
                    relay={'channel':channel,'channel_document':role_socket_document(channel),
                        'reattach_epoch':str(int.from_bytes(context['native_context']['reattach_epoch'],'little')),
                        'front_reread':escrow.peer.observation(),'transfer_head':None}
                    intent=subject.request_transfer_intent(escrow.original,front,transfer,relay=relay)
                    escrow.intent=intent
                    packet={'original':escrow.original,'front_socket':front,'transfer':transfer,
                        'relay':relay,'intent':intent,'operation':operation}
                    await self._send(_message('RELAY_REQUEST',packet=packet))
                    admitted,raw,sender=await self._receive()
                    escrow.original_messages.append((admitted,raw,sender))
                    require(admitted['kind']=='RELAY_INTAKE' and admitted['operation']==operation,
                        'CUSTODY_RELAY_ACTUAL_ADMISSION_REPLY_REQUIRED')
                    self.owner.custody_journal.require_event(admitted['intake'])
                    escrow.intake=admitted['intake'];escrow.relay_admitted.set()
                    completed,raw,sender=await self._receive()
                    escrow.original_messages.append((completed,raw,sender))
                    require(completed['kind']=='COMPLETE' and completed['operation']==operation,
                        'CUSTODY_RELAY_ACTUAL_COMPLETION_REQUIRED')
                    self.owner.custody_journal.require_event(completed['response_event'])
                    escrow.response=completed['response_event']
                    return completed['response']
                intent=subject.request_transfer_intent(escrow.original,front,transfer)
                escrow.intent=intent
                packet={'original':escrow.original,'front_socket':front,'transfer':transfer,
                    'intent':intent,'operation':operation,'request_role':'extension/subject/'+identifier}
                sent=[]
                await asyncio.to_thread(self.send_roles,_message('REQUEST',packet=packet),
                    descriptors,roles,operation,sent)
                escrow.sent.extend(sent)
                report,raw,sender=await self._receive();escrow.original_messages.append((report,raw,sender))
                require(report['kind']=='REQUEST_REPORT' and report['operation']==operation,
                    'CUSTODY_LIVE_AUTHENTIC_REQUEST_REPORT_REQUIRED')
                broker=self._broker(report['transfer'])
                await self._send(_message('OFD_JOIN',operation=operation,transfer=broker))
                completed,raw,sender=await self._receive();escrow.original_messages.append((completed,raw,sender))
                require(completed['kind']=='COMPLETE' and completed['operation']==operation,
                    'CUSTODY_LIVE_COMPLETE_BINDING_REQUIRED')
                self.owner.custody_journal.require_event(completed['intake'])
                self.owner.custody_journal.require_event(completed['response_event'])
                escrow.intake=completed['intake'];escrow.response=completed['response_event']
                # Actual response bytes were already written by the live owner.
                # COMPLETE/EOF is not requester, descendant or drain closure.
                return completed['response']
            except BaseException as error:
                escrow.failure={'type':type(error).__name__,'message':str(error),
                    'errno':getattr(error,'errno',None)}
                # Ambiguous outcomes retain all original peer/OFD escrow. Native
                # reconciliation, not a send/ACK/EOF exception, chooses abandon.
                raise
    async def transfer_readers(self):
        from .root_worker_subject_pump import freeze_readers
        from .root_worker_subject_transfer import subject_descriptors
        from .root_worker_custody import _send_fd
        async with self.lock:
            self.owner.custody_journal.require_event(self.offer.ack_event)
            self._roles()
            frozen=await freeze_readers(self.owner,self.offer.slot.operation)
            if not frozen:return {}
            descriptors=subject_descriptors(self.owner);source=self.owner.source_lease.check()
            from .root_worker_subject_transfer import role_socket_document
            carrier=socket_capture(self.channel.fileno(),source)
            packet={'subject_pumps':frozen,'roles':self.owner.subject_live_roster,
                'origin_user_ns':os.readlink('/proc/self/ns/user'),
                'origin_pid_ns':os.readlink('/proc/self/ns/pid'),
                'held_pid_ns':os.readlink('/proc/self/fd/'+str(self.offer.origins['worker_namespace'])),
                'send_channel':carrier,'send_channel_document':role_socket_document(carrier)}
            retained={'packet':packet,'send':[],'messages':[],'failure':None};self.drain_transfers.append(retained)
            try:
                await asyncio.to_thread(self.send_roles,_message('DRAINS',packet=packet),
                    descriptors,packet['roles'],None,retained['send'])
                report,raw,sender=await self._receive();retained['messages'].append((report,raw,sender))
                require(report['kind']=='DRAIN_REPORT' and set(report['subjects'])==set(frozen),
                    'CUSTODY_LIVE_FULL_DRAIN_REPORT_REQUIRED')
                events={}
                for role,pump in self.owner.subject_pumps.items():
                    item=report['subjects'][role]
                    transfer=self._broker(item['transfer'])
                    events[role]=pump.ofd_evidence(transfer,item['worker_report'])
                await self._send(_message('DRAIN_COMMIT',events=events))
                intake,raw,sender=await self._receive();retained['messages'].append((intake,raw,sender))
                require(intake['kind']=='DRAIN_INTAKES' and set(intake['events'])==set(frozen),
                    'CUSTODY_LIVE_FULL_DRAIN_INTAKE_REQUIRED')
                for role,pump in self.owner.subject_pumps.items():
                    self.owner.custody_journal.require_event(intake['events'][role]);pump.release()
                return intake['events']
            except BaseException as error:
                retained['failure']={'type':type(error).__name__,'message':str(error),
                    'errno':getattr(error,'errno',None)}
                raise
    def stdin_eof(self,request,*,transport):
        from .root_owned_descriptor_roster import prepare_roster_stdin_eofs,complete_roster_stdin_eof,roster_stdin_copy_lock
        require(type(request) is dict and set(request)=={
            'bound','original_writer','original_close','worker_closures'},
            'CUSTODY_LIVE_COMPLETE_ORIGINAL_STDIN_EOF_REQUIRED')
        key=raw_archive(request)
        preflight={'bound':request['bound'],'original_writer':request['original_writer']}
        cut=self.stdin_send_cut
        require(cut is not None and raw_archive(cut['request'])==raw_archive(preflight),
            'CUSTODY_LIVE_ORIGINAL_STDIN_PREFLIGHT_REQUIRED')
        retained={'request':request,'transport':transport,'barriers':{},
            'prepared':[],'closures':[],'failure':None,'close_failures':[]}
        self.stdin_eof_records.append(retained)
        try:
            with self.stdin_barrier_condition:
                while set(self.stdin_barriers.get(key,{}))!={'SERVICE','RELAY'}:
                    if self.message_failure is not None:raise self.message_failure
                    if self.relay_endpoint.failure is not None:raise self.relay_endpoint.failure
                    self.stdin_barrier_condition.wait()
                retained['barriers']=dict(self.stdin_barriers[key])
            require(all(item['sender']==transport['sender_credentials'] for item in retained['barriers'].values()),
                'CUSTODY_LIVE_STDIN_BARRIERS_SAME_ACTUAL_ROOT_SENDER_REQUIRED')
            with roster_stdin_copy_lock(self.owner,request['bound']):
                rosters=[self.offer.owned_roster,self.owner._retained_owned_roster]
                rosters.extend(self.registry_rosters)
                rosters.extend(item['roster'] for item in self.source_syncs)
                rosters.extend(getattr(self.owner,'_scoped_capture_rosters',()))
                rosters.extend(getattr(self.offer.slot,'_scoped_stdin_copy_rosters',()))
                seen=set()
                for roster in rosters:
                    if id(roster) in seen:continue
                    seen.add(id(roster))
                    contexts=prepare_roster_stdin_eofs(roster,self.owner,request['bound'],request['original_writer'])
                    retained['prepared'].extend((roster,context) for context in contexts)
                closed={};first_error=None
                for roster,context in retained['prepared']:
                    try:
                        record=complete_roster_stdin_eof(roster,self.owner,context,request['original_close'],closed=closed)
                        retained['closures'].append(record)
                    except BaseException as error:
                        retained['close_failures'].append({'context':context,
                            'class':type(error).__name__,'message':str(error),
                            'errno':getattr(error,'errno',None)})
                        if first_error is None:first_error=error
                if first_error is not None:raise first_error
        except BaseException as error:
            retained['failure']={'class':type(error).__name__,'message':str(error),
                'errno':getattr(error,'errno',None)}
            raise
        finally:
            cut['released']={'request':request,'transport':transport,'reason':'EOF',
                'closures':tuple(retained['closures']),'failure':retained['failure']}
            self.stdin_send_cut=None;self.send_lock.release()
        return tuple(retained['closures'])
    def adopt_front(self,fresh):
        from .protected_root_worker import RootWorkerFront
        require(type(fresh) is RootWorkerFront and fresh.prior_owner is self.owner,
            'CUSTODY_LIVE_ACTUAL_RECONSTRUCTED_FRONT_REQUIRED')
        self.owner=fresh
        for escrow in self.escrows.values():
            if escrow.subject is not None:
                escrow.subject.owner=fresh;escrow.subject.journal=fresh.custody_journal
    def abandon_request(self,identifier):
        escrow=self.escrows[identifier]
        require(escrow.subject is not None,'CUSTODY_LIVE_ACTUAL_REQUEST_SUBJECT_REQUIRED')
        # The native full mutation, never a local phase table, decides whether
        # this requested cancellation can commit. Refusal retains escrow.
        return escrow.subject.abandon_request()
    def abandon_reader(self,role):
        pump=self.owner.subject_pumps[role]
        require(pump.subject.last_original is not None,'CUSTODY_LIVE_ACTUAL_DRAIN_HISTORY_REQUIRED')
        return pump.subject.drain_abandon(pump.subject.last_original,pump.subject.last_profile['descriptor'])
    def worker_gone(self,root_evidence,*,returned_event):
        from .custody_cleanup_kernel import CleanupAction
        actual=self.owner.custody_journal.require_event(returned_event)
        require(actual['kind']=='CUSTODY_RETURNED' and actual['operation']==self.offer.slot.operation
            and actual['retained_record']['x5']['root_evidence']==raw_archive(root_evidence),
            'CUSTODY_LIVE_SAME_AUTHENTIC_FULL_RETURN_REQUIRED')
        results=[]
        for escrow in self.escrows.values():
            if escrow.subject is not None:
                results.append(escrow.subject.worker_gone('REQUEST_LOST',escrow.original,root_evidence))
        for pump in self.owner.subject_pumps.values():
            if pump.subject.last_original is not None:
                results.append(pump.subject.worker_gone('DRAIN_RECLAIMED',pump.subject.last_original,
                    root_evidence,pump.subject.last_profile['descriptor']))
        self.cleanup_results=results;self.returned_event=actual;self.gone_evidence=root_evidence
        require(all(item['action']!=CleanupAction.RETAIN_UNKNOWN for item in results),
            'CUSTODY_LIVE_SUBJECT_CLEANUP_RETAINS_UNKNOWN')
        return tuple(results)
    def wake_closed_transport(self):
        self.owner.custody_journal.require_event(self.returned_event)
        if self.relay_endpoint is not None:
            self.relay_endpoint.stopping=True
            for escrow in self.escrows.values():escrow.relay_admitted.set()
        source=self.owner.source_lease.check();self.shutdown_receipts=[]
        for channel in (self.channel,self.worker_channel,self.relay_channel,self.worker_relay_channel):
            try:channel.shutdown(socket.SHUT_RDWR)
            except OSError as error:
                self.shutdown_receipts.append({'call':'shutdown','fd':channel.fileno(),'how':socket.SHUT_RDWR,
                    'result':-1,'errno':error.errno,'source':source});raise
            self.shutdown_receipts.append({'call':'shutdown','fd':channel.fileno(),'how':socket.SHUT_RDWR,
                'result':0,'errno':0,'source':source})
        self.relay_endpoint.thread.join();self.message_reader.thread.join()
        cut=self.stdin_send_cut
        if cut is not None:
            cut['released']={'reason':'RETURNED','event':self.returned_event,
                'shutdown':tuple(self.shutdown_receipts)}
            self.stdin_send_cut=None;self.send_lock.release()
    def close_unclaimed(self):
        require(self.offer.state=='PREPARED' and not self.escrows and not self.registry_rosters,
            'CUSTODY_LIVE_ACTUAL_UNCLAIMED_CHANNELS_REQUIRED')
        source=self.owner.source_lease.check()
        for channel in (self.channel,self.worker_channel,self.relay_channel,self.worker_relay_channel):
            self.close_receipts.append(close_descriptor(channel.detach(),source))
        self.closed=True
        self.relay_endpoint.thread.join();self.message_reader.thread.join()
    def close_escrow(self):
        self.owner.custody_journal.require_event(self.returned_event)
        source=self.owner.source_lease.check()
        from .client_peer import peer_read_source
        with peer_read_source(source):
            for escrow in self.escrows.values():escrow.peer.close()
        for roster in self.registry_rosters:roster.close()
        for channel in (self.channel,self.worker_channel,self.relay_channel,self.worker_relay_channel):
            fd=channel.detach()
            self.close_receipts.append(close_descriptor(fd,source))
        self.closed=True


class WorkerSubjectService:
    def __init__(self,worker):
        self.owner=worker
        fd=worker.custody.subject_fds['request_service']
        self.duplicate_receipts={}
        self.channel=socket.socket(fileno=self._duplicate_channel('request_service',fd))
        self.channel.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1)
        from .root_worker_subject_custody import AuthenticatedSubjectRelay
        self.relay_channel=socket.socket(fileno=self._duplicate_channel('relay_service',
            worker.custody.subject_fds['relay_service']))
        self.relay_channel.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1)
        self.relay=AuthenticatedSubjectRelay(self.relay_channel,worker.custody_journal.key,
            worker.source_lease.check())
        self.relay_send_receipts=[];self.relay_receive_receipts=[];self.relay_lock=threading.RLock()
        self.send_receipts=[];self.receive_receipts=[];self.retained=[];self.prepared={};self.request_holders=[]
        self.source_syncs=[]
        self.send_lock=threading.RLock();self.stdin_eof_barrier_records=[]
        self.stdin_close_lock=threading.Lock()
        self.front_stdin_condition=threading.Condition();self.front_stdin_barriers={};self.front_stdin_failure=None
        from .root_worker_subject_messages import WorkerSubjectMessageReader
        self.message_reader=WorkerSubjectMessageReader(self)
        from .root_worker_relay_dispatch import RelayReplyDispatcher
        self.relay_replies=RelayReplyDispatcher(self)
        self.stopping=False;self.task=asyncio.create_task(self._run(),name='worldline-live-subject-service')
        # The perpetual admission reader is not a detached effect task. Every
        # admitted original request/pump task below is in the actual worker set.
    def _duplicate_channel(self,role,fd):
        from .root_worker_root_evidence import capture_lock_call
        value,receipt=capture_lock_call(self.owner.source_lease,'dup',{'fd':fd},lambda:os.dup(fd))
        self.duplicate_receipts[role]={'receipt':receipt,'ofd':receipt['ofd']}
        return value
    def native(self,cause,require_ready=True,*,subject_roster=None):
        from .root_worker_serving_peer import fact_capture
        with fact_capture():return _root_native(self.owner,cause,require_ready,subject_roster=subject_roster)
    async def _send(self,value):
        return await asyncio.to_thread(self.send_current_reply,value)
    def send_current_reply(self,value):
        from .root_worker_subject_sync import send_current
        with self.send_lock:
            return send_current(self,self.channel,value,self.send_receipts,'ROOT_WORKER_SUBJECT_SERVICE_REPLY')
    def stdin_close_scope(self):
        return self.stdin_close_lock
    def observe_front_stdin_barrier(self,preflight,delivery):
        key=raw_archive(preflight)
        with self.front_stdin_condition:
            require(key not in self.front_stdin_barriers,'CUSTODY_LIVE_FRONT_STDIN_BARRIER_REPLAY')
            self.front_stdin_barriers[key]=delivery;self.front_stdin_condition.notify_all()
    def front_stdin_reader_failed(self,error):
        with self.front_stdin_condition:
            self.front_stdin_failure=error;self.front_stdin_condition.notify_all()
    def await_stdin_eof_front_barrier(self,preflight,preparedreply):
        require(raw_archive(preparedreply['record']['request'])==raw_archive(preflight),
            'CUSTODY_LIVE_ORIGINAL_STDIN_PREPARED_REQUIRED')
        key=raw_archive(preflight)
        with self.front_stdin_condition:
            while key not in self.front_stdin_barriers:
                if self.front_stdin_failure is not None:raise self.front_stdin_failure
                self.front_stdin_condition.wait()
            delivery=self.front_stdin_barriers[key]
        require(delivery['sender']==preparedreply['transport']['sender_credentials'],
            'CUSTODY_LIVE_FRONT_STDIN_BARRIER_SAME_ACTUAL_ROOT_SENDER_REQUIRED')
        return {'request':preflight,'prepared_reply':preparedreply,'barrier':delivery}
    def prepare_stdin_eof_received(self,preflight,cut):
        require(raw_archive(cut['request'])==raw_archive(preflight),
            'CUSTODY_LIVE_ORIGINAL_STDIN_CUT_REQUIRED')
        received=[]
        from .root_worker_codec import raw_restore_archive
        from .root_worker_serving_peer import fact_capture
        for delivery in self.message_reader.retained:
            if delivery['roster'] is None:continue
            with fact_capture():
                current_inventory=raw_restore_archive(raw_archive(delivery['roster'].retained_inventory(self.owner)))
            received.append({'message':delivery['message'],'raw':delivery['raw'],
                'original_frame':delivery['message']['packet']['transfer']['original_frame'],
                'roles':current_inventory['roles'],'current_inventory':current_inventory,
                'original_received_roles':delivery['received_roles'],'header_sender':delivery['sender'],
                'header_receive':delivery['header_receive'],'receipts':delivery['role_receipts'],
                'transcript':delivery['transcript'],'transcript_raw':delivery['transcript_raw'],
                'transcript_receipts':delivery['transcript_receipts']})
        return {'request':preflight,'received':tuple(received)}
    def install_stdin_eof_received(self,capture,reply):
        require(raw_archive(reply['record']['request'])==raw_archive(capture['request'])
            and raw_archive(reply['record']['received'])==raw_archive(capture['received']),
            'CUSTODY_LIVE_ORIGINAL_STDIN_RECEIVED_JOIN_REQUIRED')
        require(len(reply['record']['joined'])==len(capture['received']),
            'CUSTODY_LIVE_COMPLETE_STDIN_RECEIVED_JOIN_REQUIRED')
        deliveries=[item for item in self.message_reader.retained if item['roster'] is not None]
        require(len(deliveries)==len(capture['received']),'CUSTODY_LIVE_STDIN_PHYSICAL_CUT_CHANGED')
        for delivery,original,joined in zip(deliveries,capture['received'],reply['record']['joined']):
            require(raw_archive(joined['received'])==raw_archive(original),
                'CUSTODY_LIVE_ORIGINAL_STDIN_ROLE_JOIN_CHANGED')
            delivery['roster'].sender_role_roster=joined['profile']
            delivery['roster'].subject_transport['preclose_join']={'capture':original,'joined':joined,
                'transport':reply['transport']}
        return reply
    @contextmanager
    def stdin_eof_scope(self):
        with self.send_lock,self.relay_lock:
            yield
    def stdin_eof_barriers(self,request):
        import secrets
        retained={'request':request,'service':None,'relay':None};self.stdin_eof_barrier_records.append(retained)
        with self.send_lock,self.relay_lock:
            source=self.owner.source_lease.check()
            value=_message('INPUT_EOF_BARRIER',request=request)
            _send_message(self.channel,value,source,self.send_receipts)
            retained['service']={'value':value,'send':self.send_receipts[-1]}
            body={'type':'INPUT_EOF_BARRIER','nonce':secrets.token_hex(32),'payload':request}
            frame=self.relay.send(body)
            relay_send=self.relay.sent[-1]
            report=_message('INPUT_EOF_BARRIER_SOURCE',request=request,frame=frame,body=body,send=relay_send)
            _send_message(self.relay_channel,report,source,self.relay_send_receipts)
            retained['relay']={'body':body,'frame':frame,'send':relay_send,'report':report,
                'report_send':self.relay_send_receipts[-1]}
        return retained
    async def _receive(self):
        delivery=await asyncio.to_thread(self.message_reader.take)
        self.last_delivery=delivery
        return delivery['message'],delivery['raw'],delivery['sender']
    def transmit_relay(self,body,source_kind,source_values,*,reply_kind,native=None,output=None):
        from .root_worker_subject_sync import send_current
        with self.relay_lock:
            ticket=self.relay_replies.register(reply_kind,body,output=output)
            frame=self.relay.send(body);ticket['frame']=frame;ticket['send']=self.relay.sent[-1]
            send_current(self,self.relay_channel,_message(source_kind,**source_values),
                self.relay_send_receipts,'ROOT_WORKER_RELAY_'+source_kind,native=native)
            return ticket
    def _output_body(self,record,produced,scope):
        import secrets
        return {'type':produced['type'],'generation':str(int.from_bytes(scope['generation'],'little')),
            'reattach_epoch':str(int.from_bytes(scope['reattach_epoch'],'little')),
            'request':scope['request'],'subgeneration':str(int.from_bytes(scope['subgeneration'],'little')),
            'operation':scope['operation'],'gate':'','sequence':produced['out_seq'],
            'nonce':secrets.token_hex(32),'admission_head':record['emitter'].intake['event_id'],
            'payload':{'line':produced['line'],'sha256':produced['sha256'],'out_seq':produced['out_seq']}}
    def _relay_output(self,record,produced,transport=None):
        from .root_worker_subject_transfer import role_socket_document
        emitter=record['emitter']
        decision=emitter.replay(produced);replay=emitter.replay_candidate(produced);scope=replay['scope']
        record.setdefault('replay_decisions',[]).append({'ordinal':decision.ordinal,
            'disposition':decision.disposition.name})
        body=self._output_body(record,produced,scope) if transport is None else transport['body']
        if transport is not None:
            require(self.relay.frame(body)==transport['frame'],'CUSTODY_RELAY_ORIGINAL_RESPONSE_FRAME_CHANGED')
        with self.relay_lock:
            worker_native=self.native('ROOT_WORKER_RELAY_OUTPUT_SOURCE',require_ready=False,
                subject_roster=record['delivery']['roster'])
            source=self.owner.source_lease.check();channel=socket_capture(self.relay_channel.fileno(),source)
            ticket=self.relay_replies.register('RESPONSE_WRITTEN',body,
                output={'record':record,'produced':produced,'native':worker_native})
            frame=self.relay.send(body);ticket.update(frame=frame,send=self.relay.sent[-1])
            from .root_worker_subject_sync import send_current
            send_current(self,self.relay_channel,_message('OUTPUT_SOURCE',records=tuple(emitter.records),
                candidate=replay,send=ticket['send'],worker_channel=channel,
                worker_channel_document=role_socket_document(channel),actor=actor_identity(self.relay_channel),
                native=worker_native,worker_origin=self.owner.custody.sender_role_roster,
                channel_duplicate=self.duplicate_receipts['relay_service']),self.relay_send_receipts,
                'ROOT_WORKER_RELAY_OUTPUT_SOURCE',native=worker_native)
        record.setdefault('output_transports',[]).append(ticket)
        # A genuine status exchange observes the real written prefix even when
        # the Front holds this frame. It is never a fabricated write receipt.
        self.peer_status(record)
        return ticket['result'] if ticket['complete'] else decision
    def consume_written_reply(self,ticket,reply):
        output=ticket['output'];record=output['record'];produced=output['produced'];body=ticket['request']
        written=reply['body'];report=reply['packet']['report']
        require(all(written[key]==body[key] for key in
            ('generation','reattach_epoch','request','subgeneration','operation','gate',
             'sequence','nonce','admission_head')) and written['payload']=={
            'out_seq':produced['out_seq'],'sha256':produced['sha256']},
            'CUSTODY_RELAY_AUTHENTIC_WRITTEN_BINDING_CHANGED')
        relay=self.relay.profile(ticket['frame'],body,reply['frame'],written)
        relay.update(front_channel=report['channel'],front_channel_document=report['channel_document'],
            front_socket=report['front_socket'],output_send=ticket['send'],
            written_receive=reply['receive'],output_receive=report['output_receive'],
            written_send=report['written_send'],report_raw=reply['raw'],report_sender=reply['sender'],
            writer_actor=report['actor'],writer_native=raw_archive(report['native']),
            worker_origin=self.owner.custody.sender_role_roster,worker_native=raw_archive(output['native']))
        relay['channel_duplicate']=self.duplicate_receipts['relay_service']
        from .scoped_capture_namespace_source import namespace_source
        relay['relay_namespace_source']=namespace_source(self.owner,self.owner._root_capture.owned_roster,
            actor_identity(self.relay_channel),sender_actor_namespace=report['sender_actor_namespace'])
        record.setdefault('relay_outputs',[]).append(relay)
        return record['emitter'].acknowledge(produced,report['write'],report['source'],relay=relay)
    def peer_status(self,record):
        import secrets
        emitter=record['emitter'];scope=emitter.scope()
        worker_native=self.native('ROOT_WORKER_BEFORE_PEER_HELD',require_ready=False,
            subject_roster=record['delivery']['roster'])
        body={'type':'PEER_HELD','generation':str(int.from_bytes(scope['generation'],'little')),
            'reattach_epoch':str(int.from_bytes(scope['reattach_epoch'],'little')),
            'request':scope['request'],'subgeneration':str(int.from_bytes(scope['subgeneration'],'little')),
            'operation':scope['operation'],'gate':'','sequence':emitter.records[-1]['out_seq'],
            'nonce':secrets.token_hex(32),'admission_head':emitter.intake['event_id'],
            'payload':{'written':tuple(emitter.written)}}
        ticket=self.transmit_relay(body,'PEER_HELD_SOURCE',
            {'channel_duplicate':self.duplicate_receipts['relay_service'],'records':tuple(emitter.records)},
            reply_kind='PEER_STATUS',native=worker_native)
        reply=self.relay_replies.wait(ticket);status=reply['body'];report=reply['packet']['report']
        require(all(status[key]==body[key] for key in
            ('generation','reattach_epoch','request','subgeneration','operation','gate',
             'nonce','admission_head')),'CUSTODY_RELAY_AUTHENTIC_PEER_STATUS_BINDING_CHANGED')
        relay=self.relay.profile(ticket['frame'],body,reply['frame'],status)
        relay.update(front_channel=report['channel'],front_channel_document=report['channel_document'],
            writer_actor=report['actor'],writer_native=raw_archive(report['native']),
            worker_native=raw_archive(worker_native),worker_origin=self.owner.custody.sender_role_roster,
            request_send=ticket['send'],request_receive=report['request_receive'],
            peer_status_send=report['peer_status_send'],peer_status_receive=reply['receive'],
            report_raw=reply['raw'],report_sender=reply['sender'])
        relay['channel_duplicate']=self.duplicate_receipts['relay_service']
        from .scoped_capture_namespace_source import namespace_source
        relay['relay_namespace_source']=namespace_source(self.owner,self.owner._root_capture.owned_roster,
            actor_identity(self.relay_channel),sender_actor_namespace=report['sender_actor_namespace'])
        candidate={'request':emitter.subject.subject,'admission_head':emitter.intake['event_id'],
            'type':'PEER_STATUS','source':report['source'],'scope':scope,
            'relay':relay,'written':report['written']}
        quantity=emitter.retain_peer_status(candidate)
        record.setdefault('peer_status',[]).append(candidate)
        return quantity
    async def _forward_output(self,record,produced,writes,transport=None):
        record['peer'].observation()
        if record['peer'].custody_mode=='RELAY':
            result=await asyncio.to_thread(self._relay_output,record,produced,transport)
            await asyncio.to_thread(self.peer_status,record)
            return result
        from .root_worker_output_kernel import ReplayDisposition
        decision=record['emitter'].replay(produced)
        record.setdefault('replay_decisions',[]).append({'ordinal':decision.ordinal,
            'disposition':decision.disposition.name})
        if decision.disposition is not ReplayDisposition.WRITE:return decision
        source=self.owner.source_lease.check()
        await asyncio.to_thread(_write_line,record['peer'],produced['line'],source,writes)
        return record['emitter'].acknowledge(produced,writes,source)
    async def _run(self):
        try:
            while not self.stopping:
                message,raw,sender=await self._receive()
                delivery=self.last_delivery
                record={'message':message,'raw':raw,'sender':sender,'fds':delivery['fds'],
                    'receipts':delivery['receipts'],'delivery':delivery,'failure':None}
                self.retained.append(record)
                if message['kind']=='PREPARE':await self._prepare(record)
                elif message['kind']=='REQUEST':await self._request(record)
                elif message['kind']=='RELAY_REQUEST':await self._relay_request(record)
                elif message['kind']=='DRAINS':await self._drains(record)
                else:require(False,'CUSTODY_LIVE_UNKNOWN_MESSAGE')
        except BaseException as error:
            if self.stopping:
                self.stop_error={'type':type(error).__name__,'message':str(error),
                    'errno':getattr(error,'errno',None)}
                return
            self.owner.failures.append(error)
            for pending in self.prepared.values():
                future=pending['admission_future']
                if not future.done():
                    await self.owner.abort_live_request(pending['prepared'],error)
                    future.set_exception(error)
            self.failure=error
            raise
    async def _prepare(self,record):
        task=asyncio.create_task(self._prepare_active(record),name='worldline-live-prepare')
        self.owner.tasks.add(task)
        try:await task
        finally:self.owner.tasks.discard(task)
    async def _prepare_active(self,record):
        message=record['message'];fd=record['fds']['request']
        peer=RequestPeer.receive_descriptor(KernelPeer.capture_descriptor(fd),message['request'])
        record['peer']=peer;identifier=peer.observation()['observationId']
        require(identifier not in self.prepared,'CUSTODY_LIVE_PREPARE_REPLAY')
        try:
            prepared=await self.owner.prepare_live_request(peer)
        except BaseException as error:
            if isinstance(error,asyncio.CancelledError):raise
            record['failure']={'type':type(error).__name__,'message':str(error),
                'errno':getattr(error,'errno',None)}
            await self._send(_message('PREPARE_FAILED',request=identifier,
                response=_response_error(peer.observation()['requestId'],error)))
            return
        row,resources=prepared;operation=row['capture']['operation']
        record['prepared']=prepared;self.prepared[identifier]=record
        future=asyncio.get_running_loop().create_future();record['admission_future']=future
        async def await_intake():return await future
        hold=asyncio.create_task(await_intake(),name='worldline-prepared-custody:'+operation)
        record['admission_task']=hold;self.owner.tasks.add(hold)
        def finished(task,owner=self.owner):
            if not task.cancelled() and task.exception() is not None:owner.failures.append(task.exception())
            owner.tasks.discard(task)
        hold.add_done_callback(finished)
        await self._send(_message('PREPARED',request=identifier,operation=operation,
            original_request=row['capture']['request']))
    async def _receive_roles(self,record,roles):
        source=self.owner.source_lease.check();delivery=record['delivery']
        transcript=delivery['transcript']
        require(transcript is not None and delivery['transcript_sender']==record['sender'],
            'CUSTODY_LIVE_FULL_AUTHENTIC_TRANSCRIPT_REQUIRED')
        record['transcript']=transcript;record['transcript_raw']=delivery['transcript_raw']
        return source,transcript['send']
    async def _request(self,record):
        packet=record['message']['packet'];roles=packet['transfer']['roster']
        source,sent=await self._receive_roles(record,roles)
        peer=RequestPeer.receive_descriptor(KernelPeer.capture_descriptor(record['fds'][packet['request_role']]),
            packet['original']['original_request'])
        record['peer']=peer;identifier=peer.observation()['observationId']
        prepared=self.prepared[identifier]['prepared'];row,resources=prepared
        require(row['capture']['operation']==packet['operation'] and row['capture']['request']==peer.observation(),
            'CUSTODY_LIVE_ORIGINAL_RESERVATION_CHANGED')
        self.owner.custody_journal.require_event(packet['intent'])
        self.owner.custody_journal.require_event(self.owner.custody_ack)
        transfer=dict(packet['transfer']);transfer.update(frame=b''.join(item['frame'] for item in sent),
            send=_stream(sent,sent[0]['source']),receive=_stream(record['receipts'],source),
            received_sender=record['sender'],roles=record['delivery']['received_roles'],
            worker_document=peer.worker_observation(),reader_user_ns=os.readlink('/proc/self/ns/user'),
            reader_pid_ns=os.readlink('/proc/self/ns/pid'))
        from .root_worker_subject_transfer import role_socket_document
        carrier=socket_capture(self.channel.fileno(),source)
        transfer.update(receive_channel=carrier,receive_channel_document=role_socket_document(carrier))
        cookie,cookie_receipt=socket_cookie(peer.peer.descriptor(),source)
        transfer.update(reader_cookie=cookie,reader_cookie_receipt=cookie_receipt)
        report_native=self.native('ROOT_WORKER_LIVE_REQUEST_OFD_REPORT',subject_roster=record['delivery']['roster'])
        transfer['current_inventory']=raw_archive(report_native[0]['provenance']['subject_capture']['inventory'])
        report=_message('REQUEST_REPORT',operation=packet['operation'],transfer=transfer,
            root_native=raw_archive(report_native))
        record['request_report']=report
        await self._send(report)
        broker,broker_raw,sender=await self._receive()
        require(broker['kind']=='OFD_JOIN' and broker['operation']==packet['operation']
            and sender==record['sender'],'CUSTODY_LIVE_AUTHENTIC_FRONT_OFD_JOIN_REQUIRED')
        record['broker']=broker;record['broker_raw']=broker_raw
        subject=SubjectCustody(self.owner,packet['operation'],'REQUEST',identifier)
        native=self.native('ROOT_WORKER_BEFORE_LIVE_REQUEST_INTAKE',subject_roster=record['delivery']['roster'])
        transfer=dict(broker['transfer'],current_inventory=raw_archive(native[0]['provenance']['subject_capture']['inventory']))
        record['subject']=subject;record['transfer']=transfer
        intake=subject.request_intake(packet['original'],packet['front_socket'],
            socket_capture(peer.peer.descriptor(),source),transfer,native=native)
        self.owner.custody_journal.require_event(intake);record['intake']=intake;record['intake_native']=native
        self.prepared[identifier]['admission_future'].set_result(intake)
        from .root_worker_serving_peer import CrosswalkRequestPeer
        peer=CrosswalkRequestPeer(peer,subject,packet['original'],transfer,packet['front_socket'],self,
            subject_roster=record['delivery']['roster'],admission_native=native)
        record['peer']=peer
        await self._invoke_admitted(record,packet,prepared)
    async def _relay_request(self,record):
        from .root_worker_subject_transfer import role_socket_document
        from .root_worker_serving_peer import RelayRequestPeer
        packet=record['message']['packet'];document=packet['original']['original_request']
        identifier=document['observationId'];prepared=self.prepared[identifier]['prepared']
        row,resources=prepared
        require(row['capture']['operation']==packet['operation'] and row['capture']['request']==document,
            'CUSTODY_RELAY_ACTUAL_ORIGINAL_RESERVATION_CHANGED')
        self.owner.custody_journal.require_event(packet['intent'])
        self.owner.custody_journal.require_event(self.owner.custody_ack)
        source=self.owner.source_lease.check()
        channel=socket_capture(self.relay_channel.fileno(),source)
        relay=dict(packet['relay'],channel=channel,channel_document=role_socket_document(channel),
            transfer_head=packet['intent']['event_id'])
        transfer=dict(packet['transfer'],reader_user_ns=os.readlink('/proc/self/ns/user'),
            reader_pid_ns=os.readlink('/proc/self/ns/pid'),send=None,receive=None)
        subject=SubjectCustody(self.owner,packet['operation'],'REQUEST',identifier)
        record['subject']=subject;record['transfer']=transfer;record['relay']=relay
        intake=subject.request_intake(packet['original'],packet['front_socket'],None,transfer,relay=relay,
            native=self.native('ROOT_WORKER_BEFORE_RELAY_REQUEST_INTAKE'))
        self.owner.custody_journal.require_event(intake);record['intake']=intake
        self.prepared[identifier]['admission_future'].set_result(intake)
        record['peer']=RelayRequestPeer(subject,packet['original'],self,intake)
        await self._send(_message('RELAY_INTAKE',operation=packet['operation'],intake=intake))
        await self._invoke_admitted(record,packet,prepared)
    async def _invoke_admitted(self,record,packet,prepared):
        from .daemon import RequestContext
        peer=record['peer'];subject=record['subject'];intake=record['intake'];row,resources=prepared
        from .root_worker_subject_output import RequestOutputEmitter
        def native_capture(cause,require_ready=True):
            current=self.native(cause,require_ready,subject_roster=record['delivery']['roster'])
            return current+record['intake_native'] if peer.custody_mode=='FRESH' else current
        emitter=RequestOutputEmitter(self.owner,subject,packet['original'],intake,native_capture=native_capture)
        record['emitter']=emitter;output_lock=asyncio.Lock()
        from .custody_control_registration import observe_admitted_worker
        await observe_admitted_worker(self,record,output_lock)
        async def progress(event,data):
            with request_scope(peer):request_id=peer.observation()['requestId']
            value={'id':request_id,'event':event,'data':data}
            async with output_lock:
                produced=emitter.produce('PROGRESS_BYTES',value);writes=[]
                record.setdefault('progress',[]).append({'output':produced,'write':writes})
                await self._forward_output(record,produced,writes)
        registration=self.owner.daemon._operations[row['capture']['document']['op']]
        async def invoke():
            try:
                context=RequestContext(self.owner.daemon,peer.observation()['requestId'],progress,
                    peer.observation()['peer']['uid'],peer)
                with request_scope(peer):
                    result=await self.owner.invoke_live_request(peer,context,registration.handler,prepared=prepared)
                response={'id':context.request_id,'ok':True,'result':result,'error':None}
            except BaseException as error:
                if isinstance(error,asyncio.CancelledError):raise
                record['failure']={'type':type(error).__name__,'message':str(error),
                    'errno':getattr(error,'errno',None)}
                response=_response_error(packet['original']['original_request']['requestId'],error)
            async with output_lock:
                produced=emitter.produce('RESPONSE_BYTES',response)
                writes=[];record['response_writes']=writes
                native=self.native('ROOT_WORKER_BEFORE_LIVE_RESPONSE_FORWARD',require_ready=False,
                    subject_roster=record['delivery']['roster'])
                if peer.custody_mode=='FRESH':
                    gates,historical_native=peer.retained_gates()
                    native+=historical_native
                else:gates=tuple(peer.gates)
                transport=None
                if peer.custody_mode=='RELAY':
                    body=self._output_body(record,produced,emitter.scope())
                    transport={'body':body,'frame':self.relay.frame(body)}
                    record['response_transport']=transport
                event=subject.respond(packet['original'],response,produced['line'],native=native,
                    relay=None if transport is None else transport['frame'],
                    relay_body=None if transport is None else dict(transport['body'],
                        payload=original_archive(transport['body']['payload'])),
                    gates=gates,out_seq=produced['out_seq'])
                record['response_event']=event
                await self._forward_output(record,produced,writes,transport)
            await self._send(_message('COMPLETE',operation=packet['operation'],intake=intake,
                response=response,response_event=event))
        task=asyncio.create_task(invoke(),name='worldline-live-request:'+packet['operation'])
        self.owner.tasks.add(task)
        try:await task
        finally:self.owner.tasks.discard(task)
    async def _drains(self,record):
        from .root_worker_subject_pump import CustodyDescriptorPump
        packet=record['message']['packet'];roles=packet['roles']
        source,sent=await self._receive_roles(record,roles)
        transfer={'mode':'FRESH','frame':b''.join(item['frame'] for item in sent),
            'sender':sent[0]['sender'],'received_sender':record['sender'],
            'send':_stream(sent,sent[0]['source']),'receive':_stream(record['receipts'],source),
            'roles':role_roster(roles,record['fds'],source,worker_pid=os.getpid()),'roster':roles,
            'worker_document':None,'origin_user_ns':packet['origin_user_ns'],
            'reader_user_ns':os.readlink('/proc/self/ns/user'),
            'origin_pid_ns':packet['origin_pid_ns'],'reader_pid_ns':os.readlink('/proc/self/ns/pid'),
            'held_pid_ns':packet['held_pid_ns']}
        transfer.update(host_cookie=None,reader_cookie=None,host_cookie_receipt=None,reader_cookie_receipt=None)
        from .root_worker_subject_transfer import role_socket_document
        carrier=socket_capture(self.channel.fileno(),source)
        transfer.update(send_channel=packet['send_channel'],send_channel_document=packet['send_channel_document'],
            receive_channel=carrier,receive_channel_document=role_socket_document(carrier))
        native=_root_native(self.owner,'ROOT_WORKER_BEFORE_LIVE_DRAIN_REPORT')
        subjects={}
        for role,frame in packet['subject_pumps'].items():
            subjects[role]={'transfer':transfer,'worker_report':{'role':role,'fd':record['fds'][role],
                'spool_fd':record['fds'][role+'/spool'],'roles':transfer['roles'],'source':source,
                'actor':actor_identity(self.channel),'native_observations':native}}
        await self._send(_message('DRAIN_REPORT',subjects=subjects))
        committed,raw,sender=await self._receive();record['committed']=committed;record['committed_raw']=raw
        require(committed['kind']=='DRAIN_COMMIT' and set(committed['events'])==set(packet['subject_pumps'])
            and sender==record['sender'],'CUSTODY_LIVE_FULL_AUTHENTIC_DRAIN_COMMIT_REQUIRED')
        events={}
        for role,frame in packet['subject_pumps'].items():
            ofd=committed['events'][role];self.owner.custody_journal.require_event(ofd['event'])
            pump=CustodyDescriptorPump(self.owner,frame['operation'],role,record['fds'][role],
                record['fds'][role+'/spool'],records=frame['records'],acquisitions=frame['original']['acquisitions'])
            pump.ofd=ofd
            pump.intake=pump.subject.drain_intake(ofd['original'],ofd['descriptor'],ofd['ofd'],
                native=self.native('ROOT_WORKER_BEFORE_ACTUAL_DRAIN_INTAKE:'+role))
            self.owner.custody_journal.require_event(pump.intake)
            events[role]=pump.intake;self.owner.subject_pumps[role]=pump
            task=pump.start();self.owner.tasks.add(task)
            def finished(task,owner=self.owner):
                if not task.cancelled() and task.exception() is not None:owner.failures.append(task.exception())
                owner.tasks.discard(task)
            task.add_done_callback(finished)
        await self._send(_message('DRAIN_INTAKES',events=events))
    async def stop_admission(self):
        self.stopping=True;source=self.owner.source_lease.check()
        try:self.channel.shutdown(socket.SHUT_RD)
        except OSError as error:
            self.shutdown_receipt={'call':'shutdown','fd':self.channel.fileno(),'how':socket.SHUT_RD,
                'result':-1,'errno':error.errno,'source':source};raise
        else:self.shutdown_receipt={'call':'shutdown','fd':self.channel.fileno(),'how':socket.SHUT_RD,
            'result':0,'errno':0,'source':source}
        await self.task
        await asyncio.to_thread(self.message_reader.thread.join)
        # Original received rights and request escrows survive shutdown/EOF.
        # Their lifetime ends only with the authentic owned root full closure.
