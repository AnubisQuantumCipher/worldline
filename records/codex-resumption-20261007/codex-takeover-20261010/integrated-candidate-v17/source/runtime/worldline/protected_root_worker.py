"""Selected exec worker running the actual original registered handler.

This source defines the custody/original-handler route. Real root-dispatch and
native Root_Controller typed capture are finite outside-input requirements;
missing providers refuse before close/transfer. It never invents a Running row.
"""
from __future__ import annotations
import asyncio,inspect,os,sys
from pathlib import Path
from .protected_startup import require,StartupRefusal,private_bytes,exact_json
from .client_peer import RequestPeer,request_scope
from .operation_capture import archive
from .operation_owner_kernel import observe_operation
from .protected_operations import CanonicalOperationPrincipal,OperationScope,operation_scope,current_scope,clone


def require_root_kernel(value):
    require(type(value) is RootAuthority,'ROOT_WORKER_SELECTED_FULL_NATIVE_ROOT_KERNEL_REQUIRED')
    value.intact()

class RootAuthority:
    def __init__(self,core,producer):
        from .core import Core
        require(type(core) is Core and type(producer) in (RootWorkerFront,RootWorkerProcess,RootWorkerIntake),
                'ROOT_WORKER_REAL_CORE_AND_CAPTURE_PRODUCER_REQUIRED')
        try:
            from .resource_child_execution import ResourceChildExecutionKernel
        except ImportError as error:
            raise StartupRefusal('ROOT_WORKER_NATIVE_CHILD_EXECUTION_COMPONENT_UNAVAILABLE') from error
        self.core,self.producer=core,producer
        self.kernel=ResourceChildExecutionKernel(core)
    def intact(self):
        self.producer.intact()
    def verify_retained_chain(self):
        # Diagnostic integrity only: never substitutes for decide/root_controller,
        # Gate v2 replay, native Legal/Next/fold, or the final startup refusal.
        from .retained_chain_kernel import verify_current_owner
        return verify_current_owner(self.producer)

    def observe(self,material):
        self.producer.source_lease.check()
        require(type(material) is dict and set(material)=={'packet','controller','crosswalk','authority_snapshot'},
                'ROOT_WORKER_COMPLETE_TYPED_NATIVE_ROOT_INPUT_REQUIRED')
        return self.kernel.root_controller(**material)
    def decide(self,material):
        try:
            self.intact()
            observation=self.observe(material)
            require(observation.status=='ROOT_READY_CONJUNCTION',
                    'ROOT_WORKER_FRESH_FULL_NATIVE_ROOT_REFUSED')
            return observation
        except BaseException as error:
            try:
                from .root_owned_descriptor_roster import release_unclaimed_capture
                release_unclaimed_capture(self.producer)
            except BaseException as cleanup:error.add_note('unclaimed root roster cleanup failed: '+repr(cleanup))
            raise
    def replay_root_custody(self,frame,channel,peer):
        # Actual receiver/current kernel captures must be independently produced.
        # Restoring the sender's controller DTO is expressly insufficient.
        material=self.producer.capture_root_material(frame,channel,peer)
        observed=self.decide(material)
        self.producer.retain_native('ROOT_WORKER_NATIVE_CUSTODY_REDECISION',material,observed)
        return observed

class RootWorkerSlot:
    def __init__(self,front,owned,operation,request):
        require(type(front) is RootWorkerFront and type(request) is RequestPeer,
                'ROOT_WORKER_ACTUAL_FRONT_AND_REQUEST_REQUIRED')
        # Genuine native/physical producer is a separately selected source
        # component, not an argument-supplied implementation or identity flag.
        try:
            from .protected_root_supervisor import OwnedRootSupervisor
        except ImportError as error:
            raise StartupRefusal('ROOT_WORKER_OWNED_ROOT_SUPERVISOR_UNAVAILABLE') from error
        require(type(owned) is OwnedRootSupervisor and owned.principal is front.principal
            and owned.operation==operation and owned.request is request,
            'ROOT_WORKER_REAL_OWNED_ROOT_SLOT_REQUIRED')
        self.front,self.principal,self.owned=front,front.principal,owned
        self.operation,self.request,self.channel=operation,request,owned.custody_channel
    def intact(self):
        require(self.front.slots.get(self.operation) is self,'ROOT_WORKER_SLOT_NOT_CURRENT_OWNER')
        self.owned.intact();self.request.observation()
    def capture(self):
        self.intact();return self.owned.complete_capture()
    def authorize_root(self):
        self.intact()
        material=self.front.capture_root_material(self.capture(),self.channel,self.request)
        native=self.front.authority.decide(material)
        return self.front.retain_native('ROOT_WORKER_NATIVE_BEFORE_HANDOFF',material,native)
    def retain(self,cause,value):
        # This owner journal remains live when actual canonical/Store DB
        # owners have closed. It retains full factual records and grants no use.
        from .root_worker_root_evidence import append,reference,lock_receipts,native_item
        require(cause=='ROOT_WORKER_CUSTODY_INTENT','ROOT_WORKER_IMMUTABLE_NATIVE_DIAGNOSTIC_REQUIRED')
        retained=value['root_native']
        return append(self.front,self.operation,'HANDOFF_INTENT',{'cause':cause,'value':value},
            {'execution_ack_event':reference(self.front.custody_journal,self.operation,'EXECUTION_ACK'),
             'handoff':value,'locks':lock_receipts(self.front)},
            native=(native_item('root-admission',retained['material'],retained['observation'],retained['provenance']),))
    def verify_ack(self,receipt,frame,intent):
        self.owned.verify_full_custody_ack(receipt,frame,intent)
        # Owned receiver is required to prove the exact durable native ACK and
        # source/OFD joins; send/EOF or an ACK string supplies no such witness.

class RootWorkerFront:
    def __init__(self,principal,owner_descriptor,*,reconstructing=False):
        require(type(principal) is CanonicalOperationPrincipal
            and getattr(principal,'root_worker',None) is None,
            'ROOT_WORKER_SINGLE_ACTUAL_CANONICAL_ROUTE_REQUIRED')
        self.principal,self.lease=principal,principal.lease
        self.path=Path(owner_descriptor);self.raw=private_bytes(self.path)
        self.plan_raw=self.raw;self.spec=self.lease.spec;self.descriptor_raw=self.lease.descriptor_raw
        self.source_lease=self.lease.source_lease
        self.core=principal.core
        require(self.lease.source_lease.file(str(self.path),('DATA',))==self.raw,
                'ROOT_WORKER_OWNER_DESCRIPTOR_UNBOUND')
        self.plan=exact_json(self.raw)
        require(type(self.plan) is dict and set(self.plan)=={'schema','installation','startup_descriptor',
            'entry','early_envelope','helper','sources','worker_policy','cost_key','native_components',
            'handoff_genesis','handoff_journal','child_dispatch'}
            and self.plan['schema']=='worldline.protected-root-worker-plan-v1'
            and self.plan['installation']==self.lease.spec['installation_id']
            and self.plan['startup_descriptor']==str(self.lease.descriptor_path),
            'ROOT_WORKER_COMPLETE_OWNER_PLAN_REQUIRED')
        # No state/genesis/key/history is initialized on descriptor absence.
        for name,role in (('entry','ENTRY'),('early_envelope','DATA'),
                          ('helper','EXECUTABLE'),('handoff_genesis','DATA')):
            require(Path(self.plan[name]).is_absolute(),'ROOT_WORKER_OWNER_PATH_NOT_ABSOLUTE')
            self.lease.source_lease.file(self.plan[name],(role,))
        self.lease.source_lease.file(self.plan['native_components']['approved_loader'],('HELPER',))
        require(type(self.plan['sources']) is dict and self.plan['sources'],
                'ROOT_WORKER_FULL_EXECUTED_SOURCE_ROSTER_ABSENT')
        from .protected_startup import digest
        for path,expected in self.plan['sources'].items():
            roles=(('ENTRY',) if path==self.plan['entry'] else ('HELPER',)
                   if path==self.plan['native_components']['approved_loader'] else ('EXECUTABLE',)
                   if path==self.plan['helper'] or path in
                   (self.plan['native_components']['systemctl'],self.plan['native_components']['systemd_run'])
                   else ('SOURCE','EXECUTABLE'))
            require(digest(self.lease.source_lease.file(path,roles))==expected,
                    'ROOT_WORKER_SELECTED_SOURCE_CHANGED')
        self.slots={};self.collectors={};self.phase='FRONT_RECONSTRUCTING' if reconstructing else 'FRONT_OWNED';self.operation=None
        self.subject_pumps={}
        self.authority=RootAuthority(principal.core,self)
        from .root_worker_root_evidence import prepare_capture
        prepare_capture()
        if reconstructing:
            from .root_worker_closed import ClosedFrontEscrow
            from .root_worker_failed_closure import FailedFrontEscrow
            guard=self.lease.exec_custody
            require(type(guard) in (ClosedFrontEscrow,FailedFrontEscrow) and guard.fresh_lease is self.lease
                and guard.phase=='RECONSTRUCTED','ROOT_WORKER_ACTUAL_CLOSED_RECONSTRUCTION_REQUIRED')
        else:self.lease.require_front_startup()
        from .root_worker_journal_v2 import RootCustodyJournalV2
        self.custody_journal=self.lease.custody_journal_v2
        require(type(self.custody_journal) is RootCustodyJournalV2,'ROOT_WORKER_EXISTING_STARTUP_JOURNAL_REQUIRED')
        if not reconstructing:self.custody_journal.adopt_owner(self)
        principal.root_worker=self
        from .protected_root_resource import RootResourceRoute
        self.resource_route=RootResourceRoute(self)
    def intact(self):
        require(self.phase=='FRONT_OWNED','ROOT_WORKER_FRONT_HAS_RELINQUISHED_STATE')
        self.lease.intact();self.lease.loaded()
    def capture_root_material(self,frame,channel,peer,*,subject_roster=None):
        # Owner plan must select the actual protected root observation producer;
        # it binds independently recaptured kernel identities, complete current
        # scoped service history and the original full A frame. No reconstruction.
        from .protected_root_observation import RootControllerCapture
        return RootControllerCapture(self,frame,channel,peer,subject_roster=subject_roster).complete_native_material()
    def retain_native(self,cause,material,observation):
        from .protected_root_observation import retain_root_native
        return retain_root_native(self,cause,material,observation)
    def close_front_owners(self,offer):
        from .root_worker_custody import CustodyOffer
        from .root_worker_root_evidence import append,reference,lock_receipts,selected_owners,close_owner,seed,acquisition_capture
        from .root_worker_current_state import capture_owner_state
        require(type(offer) is CustodyOffer and offer.p is self.principal
            and self.phase=='FRONT_OWNED','ROOT_WORKER_FRONT_CLOSE_OWNER_MISMATCH')
        self.current_offer=offer
        p=self.principal;daemon=getattr(p.controller,'_daemon',None)
        require(daemon is not None and not daemon._background,
                'ROOT_WORKER_FRONT_BACKGROUND_OWNERS_NOT_TRANSFERABLE')
        acquisitions=p.controller.runner._acquisitions_by_job
        require(all(item.quiescent() for item in acquisitions.values()),
                'ROOT_WORKER_FRONT_ACQUISITIONS_NOT_QUIESCENT')
        quiescence={'background':tuple(daemon._background),
            'acquisitions':tuple(acquisition_capture(job,item) for job,item in acquisitions.items())}
        closers=(('resource.observations',self.resource_route.resource.observations.close),
            ('resource.journal',self.resource_route.resource.journal.db.close),
            ('operation.journal',p.journal.db.close),('controller',p.controller.close),
            ('store',p.store.close),('issuer',p.gate.issuer.close),('universe',p.gate.universe.close),
            ('startup',self.lease.db.close))
        before=capture_owner_state(self);before['owners']=selected_owners(self,closers)
        locks=lock_receipts(self,before)
        close_intent=append(self,offer.slot.operation,'FRONT_CLOSE_INTENT',
            {'handoff':offer.intent,'quiescence':quiescence,'owner_before':before},
            {'handoff_event':reference(self.custody_journal,offer.slot.operation,'HANDOFF_INTENT'),
             'quiescence':quiescence,'locks':locks},before=before)
        self.phase='FRONT_CLOSE_INTENDED';self.operation=offer.slot.operation
        try:
            self.resource_route.detach_state_for_exec(offer,close_state=False)
            owners_closed=[]
            for name,close in closers:owners_closed.append(close_owner(self,name,close))
            self._closed_custody_offer=offer
            self._closed_owner_receipts=tuple(owners_closed)
            self.resource_route.resource.poisoned=True;self.lease.poisoned=True
            current=capture_owner_state(self)
            offer.front_closed_event=append(self,self.operation,'FRONT_CLOSED',
                {'front_close_intent':close_intent,'owners_closed':tuple(owners_closed),'owner_state':current},
                {'front_close_event':close_intent['event_id'],'owners_closed':tuple(owners_closed),
                 'locks':lock_receipts(self,before),'seed':seed(self,current)},before=before,current=current)
        except BaseException:
            self.phase='UNKNOWN_FRONT_CLOSE';raise
        self.phase='TRANSFER_PENDING'
    def register_subject_reader(self,operation,role,fd,spool_fd,*,root_operation):
        from .root_worker_subject_pump import register_reader
        return register_reader(self,operation,role,fd,spool_fd,root_operation=root_operation)

    async def invoke(self,request,context,handler):
        require(self.phase=='FRONT_OWNED','ROOT_WORKER_PRIOR_OWNER_UNKNOWN_OR_LIVE')
        p=self.principal
        launch=self.resource_route.launch_root_worker
        row,resource=p._reserve(request);operation=row['capture']['operation']
        owned=None;offer=None
        try:
            from .root_worker_subject_front import queue_front_request
            queued,emitter=queue_front_request(self,request,row,resource,context)
            pending_outputs=getattr(self,'front_queued_requests',None)
            if pending_outputs is None:pending_outputs={};self.front_queued_requests=pending_outputs
            pending_outputs[operation]={'subject':queued,'emitter':emitter,'request':request,'context':context}
            # Original native use is reserved once. Durable effect intent and
            # actual current original pre-effect checks precede root dispatch.
            boundary=p.pre_effect(operation);capture=row['capture'];snapshot=p._snapshot(capture)
            use=observe_operation(p,snapshot,'RESERVE_USE')
            require(use['decision']=='RESERVED_REPLAY','ROOT_WORKER_ORIGINAL_USE_REPLAY_REFUSED')
            p.journal.append(operation,'EFFECT_INTENT',capture,snapshot=snapshot,
                native={'command':'RESERVE_USE','observation':use},boundaries=[boundary])
            owned=await launch(p.pending_for_operation(operation),request,capture['resource_intent'].reservation)
            slot=self.slots[operation]
            require(type(slot) is RootWorkerSlot and slot.owned is owned,
                    'ROOT_WORKER_ACTUAL_LAUNCHED_SLOT_REPLACED')
            slot.request=owned.retained_peer;owned.request=slot.request
            p.active_peers[operation]=slot.request
            p.resources.actor_slots[capture['resource_intent'].reservation]['original_request']=slot.request
            from .custody_control_registration import observe_admitted_front
            await observe_admitted_front(self,slot)
            from .root_worker_custody import CustodyOffer
            offer=CustodyOffer(p,slot.request,slot)
            slot.custody_offer=offer
            require(owned.raw_tasks,'ROOT_WORKER_RAW_READERS_REQUIRED_BEFORE_HANDOFF')
            offer.transfer()
            receipt=await owned.receive_full_custody_ack()
            offer.committed_ack(receipt);self.phase='WORKER_OWNED'
            # Full original registered result/progress is relayed, without
            # invoking the handler in the front or classifying effect authority.
            result=await owned.receive_original_result(context)
            from .root_worker_closed import collect_and_reconstruct
            require(operation not in self.collectors,'ROOT_WORKER_DUPLICATE_TERMINAL_COLLECTOR')
            # Ownership remains in the front even if the initiating client
            # disconnects. Its original response need not wait for detached jobs.
            self.collectors[operation]=asyncio.create_task(collect_and_reconstruct(self,offer,context))
            return result
        except BaseException as error:
            queued_request=getattr(self,'front_queued_requests',{}).get(operation)
            if queued_request is not None:
                from .root_worker_subject_service import _response_error
                emitter=queued_request['emitter']
                try:
                    queued_request['error_output']=emitter.emit('RESPONSE_BYTES',
                        _response_error(context.request_id,error))
                except BaseException as response_error:
                    queued_request['response_error']=response_error
                    error.add_note('Actual queued original error response also failed: '+str(response_error))
            self.phase='UNKNOWN_WORKER_OWNERSHIP'
            if owned is not None:
                await owned.retain_and_stop_unknown(error,offer)
            elif self.phase=='UNKNOWN_WORKER_OWNERSHIP':
                # No dispatch owner exists. Preserve the actual original hold,
                # named failure and native quarantine; never invent a release.
                p.quarantine(operation,error)
            raise
        # Detached tasks remain owned by the worker after initial result;
        # no front return drops the root hold or creates another owner/use.

class RootWorkerProcess:
    def __init__(self,custody,lease,principal,daemon):
        from .root_worker_custody import CustodyReceipt
        from .protected_startup import StartupLease
        from .daemon import WorldlineDaemon
        require(type(custody) is CustodyReceipt and type(lease) is StartupLease
            and type(principal) is CanonicalOperationPrincipal and type(daemon) is WorldlineDaemon
            and principal.lease is lease and principal.controller is lease.controller
            and daemon.store is lease.store and custody.frame['installation']==lease.spec['installation_id'],
            'ROOT_WORKER_ACTUAL_FRESH_TARGET_OWNERS_REQUIRED')
        self.custody,self.lease,self.principal,self.daemon=custody,lease,principal,daemon
        self.channel=custody.channel
        self.operation=custody.frame['operation'];self.request=custody.peer
        row=principal.journal.rows.get(self.operation)
        require(row is not None and row['state']=='EFFECT_INTENT'
            and row['capture']['request']==self.request.observation(),
                'ROOT_WORKER_FRESH_PRINCIPAL_ORIGINAL_INTENT_CHANGED')
        require(self.operation not in principal.active_peers,'ROOT_WORKER_DUPLICATE_ORIGINAL_REQUEST_OWNER')
        principal.active_peers[self.operation]=self.request
        self.spec=lease.spec;self.descriptor_raw=lease.descriptor_raw;self.source_lease=lease.source_lease
        self.core=principal.core
        self.plan_raw=custody.frame['root_plan']['raw'];self.plan=exact_json(self.plan_raw)
        custody.owned_roster.attach(self,principal.resources)
        from .root_worker_journal_v2 import RootCustodyJournalV2
        self.custody_journal=lease.custody_journal_v2
        require(type(self.custody_journal) is RootCustodyJournalV2,'ROOT_WORKER_ORIGINAL_STARTUP_CUSTODY_JOURNAL_REQUIRED')
        self.custody_journal.adopt_owner(self)
        self.tasks=set();self.task_operations={};self.live_requests={};self.failures=[];self.initial_result=None
        self.subject_pumps={}
        self.initial_output_lock=asyncio.Lock()
        from .root_worker_result_channel import WorkerResultChannel
        self.result_channel=WorkerResultChannel(self)
        self.authority=RootAuthority(principal.core,self)
        principal.root_worker_process=self
        # Actual task set is retained before done callbacks remove daemon jobs.
        daemon._root_worker_task_owner=self
        from .root_worker_root_evidence import prepare_capture
        prepare_capture()
    def intact(self):
        self.lease.intact();self.lease.loaded();self.request.observation()
    def capture_root_material(self,frame,channel,peer,*,subject_roster=None):
        from .protected_root_observation import RootControllerCapture
        return RootControllerCapture(self,frame,channel,peer,subject_roster=subject_roster).complete_native_material()
    def retain_native(self,cause,material,observation):
        from .protected_root_observation import retain_root_native
        return retain_root_native(self,cause,material,observation)
    def close_stdin(self,slot,fd):
        from .root_owned_descriptor_roster import prepare_owned_stdin_eof,complete_owned_stdin_eof,owned_stdin_copy_lock,roster_stdin_copy_lock
        from .custody_subject_capture import actor_identity,fd_identity
        from .root_worker_root_evidence import capture_effect
        retained=getattr(self,'stdin_eof_controls',None)
        if retained is None:retained=[];self.stdin_eof_controls=retained
        control={};retained.append(control);failure=None;preflight=None
        service=self.subject_service
        with service.stdin_close_scope():
            try:
                with service.stdin_eof_scope():
                    require(slot.stdin_fd==fd,'ROOT_STDIN_EOF_ACTUAL_ORIGINAL_WRITER_REQUIRED')
                    preflight={'bound':slot.row.bound,'original_writer':{'fd':fd,
                        'identity':fd_identity(fd),'actor':actor_identity(),'source':self.source_lease.check()}}
                    control['preflight']=preflight
                    control['prepared_reply']=self.result_channel.prepare_stdin_eof(preflight)
                    control['cut']=service.await_stdin_eof_front_barrier(preflight,control['prepared_reply'])
                    control['received']=service.prepare_stdin_eof_received(preflight,control['cut'])
                    control['received_reply']=self.result_channel.join_stdin_eof_received(control['received'])
                    service.install_stdin_eof_received(control['received'],control['received_reply'])
                    with roster_stdin_copy_lock(self,slot.row.bound),owned_stdin_copy_lock(slot):
                        context=prepare_owned_stdin_eof(slot,original_writer=preflight['original_writer'])
                        control['context']=context;control['current_writer']=context['current_writer']
                        context['completed']=();context['close_failures']=()
                        slot.stdin_fd=None;closed=None
                        try:_result,closed=capture_effect(self.source_lease,'close',{'fd':fd},lambda:os.close(fd))
                        except BaseException as error:
                            failure=error;control['original_error']=error
                            closed=getattr(error,'custody_receipt',None)
                            if closed is None:raise
                        closes=getattr(slot,'stdin_close_receipts',None)
                        if closes is None:closes=[];slot.stdin_close_receipts=closes
                        closes.append(closed)
                        request={'bound':context['bound'],'original_writer':context['original_writer'],
                            'original_close':closed}
                        control['request']=request
                        try:request['worker_closures']=complete_owned_stdin_eof(slot,context,closed)
                        except BaseException as error:
                            control['local_error']=error
                            request['worker_closures']=context['completed']+context['close_failures']
                            if failure is None:failure=error
                            else:failure.add_note('Actual local input observation copies close also failed: '+repr(error))
                        slot.stdin_observation_closures=request['worker_closures']
                        try:control['barriers']=service.stdin_eof_barriers(request)
                        except BaseException as error:
                            control['barrier_error']=error
                            if failure is None:raise
                            failure.add_note('Actual input source barriers also failed: '+repr(error))
                            raise failure
                try:control['front_ack']=self.result_channel.request_stdin_eof(request)
                except BaseException as error:
                    control['front_error']=error
                    if failure is None:raise
                    failure.add_note('Actual Front input observation copies close also failed: '+repr(error))
                if failure is not None:raise failure
                return control
            except BaseException as error:
                control['failure']=error
                if preflight is not None:
                    try:control['cancel_reply']=self.result_channel.cancel_stdin_eof(preflight)
                    except BaseException as cancel_error:
                        control['cancel_error']=cancel_error
                        error.add_note('Actual Front input send-cut cancellation also failed: '+repr(cancel_error))
                raise
    def own_task(self,key,task):
        require(type(task) is asyncio.Task,'ROOT_WORKER_ACTUAL_DETACHED_TASK_REQUIRED')
        scope=current_scope()
        require(type(scope) is OperationScope and scope.principal is self.principal,
                'ROOT_WORKER_ACTUAL_DETACHED_OPERATION_SCOPE_REQUIRED')
        operation=scope.operation
        self.tasks.add(task);self.task_operations[task]=operation
        row=self.principal.journal.rows[operation]
        self.principal.journal.append(operation,'ACK',row['capture'],snapshot=row['snapshot'],native=row['native'],
            boundaries=row['boundaries']+[{'name':'ROOT_WORKER_DETACHED_TASK','key':key}])
    def _handler_boundary(self,row):
        p=self.principal;operation=row['capture']['operation']
        # The actual running root remains the original starter. The distinct
        # caller's original reserved use is never replaced by the starter use.
        material=self.capture_root_material(self.custody.frame,self.channel,self.request)
        native=self.authority.decide(material)
        self.retain_native('ROOT_WORKER_NATIVE_BEFORE_ORIGINAL_HANDLER',material,native)
        original=p._original_native_use(row)
        require(original['observation']['decision']=='RESERVED_NEW',
                'ROOT_WORKER_ORIGINAL_RESERVED_USE_UNESTABLISHED')
        latest=p.journal.rows[operation]
        return p.journal.append(operation,'ACK',latest['capture'],snapshot=latest['snapshot'],
            native=latest['native'],boundaries=latest['boundaries']+[
                {'name':'ROOT_WORKER_BEFORE_HANDLER','value':archive({
                    'current_material':material,'current_native':native,'original_native_use':original}).hex()}])
    async def _original_handler(self,row,request,context,handler):
        p=self.principal;capture=row['capture'];operation=capture['operation']
        if operation==self.operation:
            from .root_worker_serving_peer import require_selected_peer
            admission=self.initial_request_admission
            require(request is admission['peer'] and request.actual is self.request,
                    'ROOT_WORKER_ORIGINAL_STARTER_REQUEST_REQUIRED')
            require_selected_peer(request,admission)
        else:
            from .root_worker_serving_peer import require_selected_peer
            records=[item for item in self.subject_service.retained
                if item['subject'].operation==operation and item.get('intake') is not None]
            require(len(records)==1,'ROOT_WORKER_SELECTED_HANDLER_INTAKE_REQUIRED')
            require_selected_peer(request,records[0])
        require(context.peer is request and capture['request']==request.observation(),
                'ROOT_WORKER_GENUINE_HANDLER_REQUEST_REQUIRED')
        with request_scope(request),operation_scope(OperationScope(p,operation,request)):
            self._handler_boundary(row)
            if capture['document']['op']=='quarantine.resolve':
                result=p.resolve_quarantine(request,capture,row)
            else:
                result=handler(capture['document']['args'],context)
                if inspect.isawaitable(result):result=await result
            self.daemon.publisher.publish()
            return result
    async def prepare_live_request(self,request):
        p=self.principal
        require(type(request) is RequestPeer,'ROOT_WORKER_GENUINE_LIVE_PREPARATION_REQUEST_REQUIRED')
        async with p.operation_lock:
            with request_scope(request):
                prepared=p._reserve(request)
            operation=prepared[0]['capture']['operation']
            self.live_requests[operation]={'prepared':prepared,'request':request}
            return prepared
    async def abort_live_request(self,prepared,error):
        p=self.principal;operation=prepared[0]['capture']['operation']
        require(self.live_requests[operation]['prepared'] is prepared,
                'ROOT_WORKER_ACTUAL_PREPARATION_ESCROW_REQUIRED')
        async with p.operation_lock:
            # Only native canonical quarantine is possible without a distinct
            # actual owner no-effect resolution; never assert an unwind/release.
            p.quarantine(operation,error)
            self.live_requests[operation]['failure']=error
    def _result_capture(self,capture,result):
        p=self.principal
        return clone({'result':result,'actual_store':p.capture.chain_material(),
            'actual_transaction':None if capture['transaction'] is None else
                p.controller.transactions._load_record(capture['transaction']['transactionId'])})
    def _finish_live(self,operation,result):
        p=self.principal;row=p.journal.rows[operation];capture=row['capture']
        result_capture=self._result_capture(capture,result)
        if row['state']=='SETTLED':
            return p.journal.append(operation,'ACK',capture,snapshot=row['snapshot'],native=row['native'],
                boundaries=row['boundaries']+[{'name':'RETURN_REPORT','value':archive(result_capture).hex()}])
        return p.finish(operation,result_capture)
    async def _finish_detached_live(self,operation,result,request):
        current=asyncio.current_task();p=self.principal
        try:
            while True:
                pending=tuple(task for task in self.tasks
                    if task is not current and self.task_operations.get(task)==operation)
                if not pending:break
                outcomes=await asyncio.gather(*pending,return_exceptions=True)
                for task,outcome in zip(pending,outcomes):
                    self.tasks.discard(task);self.task_operations.pop(task,None)
                    if isinstance(outcome,BaseException):raise outcome
            async with p.operation_lock:
                with request_scope(request),operation_scope(OperationScope(p,operation,request)):
                    self._finish_live(operation,result)
            request.close()
            p.active_peers.pop(operation,None);self.live_requests.pop(operation)
        except BaseException as error:
            self.live_requests[operation]['failure']=error
            await self._retain_failed_operation(operation,error)
            raise
        finally:
            self.tasks.discard(current);self.task_operations.pop(current,None)
    async def invoke_live_request(self,request,context,handler,*,prepared):
        p=self.principal;reserved,resource=prepared;capture=reserved['capture']
        operation=capture['operation'];escrow=self.live_requests[operation]
        records=[item for item in self.subject_service.retained
            if item.get('peer') is request and item.get('intake') is not None]
        require(len(records)==1,'ROOT_WORKER_ACTUAL_NATIVE_LIVE_INTAKE_REQUIRED')
        self.custody_journal.require_event(records[0]['intake'])
        from .root_worker_serving_peer import require_selected_peer
        require_selected_peer(request,records[0])
        require(escrow['prepared'] is prepared and capture['request']==request.observation(),
                'ROOT_WORKER_SAME_ACTUAL_LIVE_PREPARATION_REQUIRED')
        # The preliminary observation descriptor is not an effect owner. The
        # native-intaken original OFD/request now owns this exact reserved use.
        p.active_peers[operation]=request;escrow['request']=request
        try:
            async with p.operation_lock:
                row=p.journal.rows[operation]
                require(row['state']=='RESERVED','ROOT_WORKER_LIVE_INTENT_NOT_ONCE_RESERVED')
                boundary=p.pre_effect(operation);snapshot=p._snapshot(capture)
                native=observe_operation(p,snapshot,'RESERVE_USE')
                require(native['decision']=='RESERVED_REPLAY','ROOT_WORKER_LIVE_RESERVED_USE_CHANGED')
                row=p.journal.append(operation,'EFFECT_INTENT',capture,snapshot=snapshot,
                    native={'command':'RESERVE_USE','observation':native},
                    boundaries=[boundary,{'name':'DISPATCH_INTENT','resource':clone(resource)}])
                result=await self._original_handler(row,request,context,handler)
                pending=tuple(task for task in self.tasks if self.task_operations.get(task)==operation)
                if pending:
                    retained=request.duplicate();p.active_peers[operation]=retained
                    escrow['request']=retained
                    task=asyncio.create_task(self._finish_detached_live(operation,result,retained),
                        name='worldline-original-live-settlement:'+operation)
                    with operation_scope(OperationScope(p,operation,retained)):
                        self.own_task('original-live-settlement:'+operation,task)
                else:
                    with request_scope(request),operation_scope(OperationScope(p,operation,request)):
                        self._finish_live(operation,result)
                    p.active_peers.pop(operation,None);self.live_requests.pop(operation)
                return result
        except BaseException as error:
            escrow['failure']=error
            await self._retain_failed_operation(operation,error)
            raise
    async def run_original(self,progress):
        from .daemon import RequestContext
        p=self.principal;self.custody.intact();p.journal.load()
        row=p.journal.rows[self.operation];capture=row['capture']
        request=self.initial_request_admission['peer']
        require(capture['request']==request.observation() and row['state']=='EFFECT_INTENT',
                'ROOT_WORKER_RESTORED_ORIGINAL_RESERVATION_CHANGED')
        registration=self.daemon._operations.get(capture['document']['op'])
        require(registration is not None,'ROOT_WORKER_ORIGINAL_REGISTERED_HANDLER_ABSENT')
        context=RequestContext(self.daemon,request.observation()['requestId'],progress,
                               request.observation()['peer']['uid'],request)
        p.active_peers[self.operation]=request
        try:
            async with p.operation_lock:
                result=await self._original_handler(row,request,context,registration.handler)
            self.initial_result=clone(result)
            # Return the original detached response immediately without release.
            await self.send_initial_result(result)
            while True:
                while self.tasks:
                    pending=tuple(self.tasks)
                    outcomes=await asyncio.gather(*pending,return_exceptions=True)
                    for task,outcome in zip(pending,outcomes):
                        self.tasks.discard(task);self.task_operations.pop(task,None)
                        if isinstance(outcome,BaseException):self.failures.append(outcome)
                # Actual admission shutdown/wait joins the real receive task.
                # A request admitted while the wait ran remains in self.tasks.
                await self.subject_service.stop_admission()
                if not self.tasks:break
            result_capture=self._result_capture(capture,result)
            with request_scope(request),operation_scope(OperationScope(p,self.operation,request)):
                latest=p.journal.rows[self.operation]
                p.journal.append(self.operation,'ACK',latest['capture'],
                    snapshot=latest['snapshot'],native=latest['native'],
                    boundaries=latest['boundaries']+[{'name':'ROOT_WORKER_FINAL_RESULT_CAPTURE',
                        'value':archive(result_capture).hex()}])
                await self.send_worker_terminal(result_capture,self.failures)
            return result
        except BaseException as error:
            await self._retain_failed_operation(self.operation,error)
            raise
        finally:
            if not self.tasks:p.active_peers.pop(self.operation,None)
    async def publish_initial_output(self,kind,value):
        async with self.initial_output_lock:
            admission=self.initial_request_admission
            admission['peer'].observation()
            produced=admission['emitter'].produce(kind,value);writes=[]
            if kind=='RESPONSE_BYTES':
                native=self.subject_service.native('ROOT_WORKER_BEFORE_INITIAL_RESPONSE_FORWARD',
                    require_ready=False,subject_roster=admission['peer'].subject_roster)
                gates,historical=admission['peer'].retained_gates()
                native+=historical
                admission['response_event']=admission['subject'].respond(admission['original'],value,
                    produced['line'],native=native,gates=gates,
                    out_seq=produced['out_seq'])
            output={'produced':produced,'response_event':admission.get('response_event'),
                'writes':writes,'written':None}
            self.last_initial_output=output
            try:
                forwarded=await self.subject_service._forward_output(admission,produced,writes)
                output['written']=forwarded if type(forwarded) is dict else None
            finally:
                output['writes']=tuple(writes)
                output['replay_decisions']=tuple(admission.get('replay_decisions',()))
                output['output_events']=tuple(admission['emitter'].retained()['produced'])
                output['written_events']=tuple(admission['emitter'].retained()['written'])
            return output

    async def send_initial_result(self,result):
        request_id=self.initial_request_admission['peer'].observation()['requestId']
        output=await self.publish_initial_output('RESPONSE_BYTES',
            {'id':request_id,'ok':True,'result':result,'error':None})
        await self._channel_method('send_original_result',result,worker_output=output)
    async def send_worker_terminal(self,result,failures):
        # Before relinquishing actual target owners, retain every final state
        # row and the current complete native root material. The collector must
        # then obtain actual ECHILD/outer wait; this message is not closure.
        from .root_worker_current_state import capture_owner_state
        material=self.capture_root_material(self.custody.frame,self.custody.channel,self.request)
        native=self.authority.decide(material)
        event=self.retain_native('ROOT_WORKER_NATIVE_BEFORE_OWNER_CLOSE',material,native)
        self.terminal_native=event
        await self._channel_method('send_original_terminal',{'result':result,
            'failures':[{'type':type(x).__name__,'message':str(x)} for x in failures],
            'owner_state':capture_owner_state(self),'native_event':event,
            'original_native_use':self.principal._original_native_use(self.principal.journal.rows[self.operation])})
    def recover_root_append(self,error):
        from .root_worker_journal_v2 import RootCustodyJournalV2
        from .root_worker_codec import raw_archive
        from .root_worker_root_evidence import append_failure,unknown,append,worker_liveness
        old=self.custody_journal;uncertainty=old.capture_uncertainty()
        cause,saved=append_failure(uncertainty)
        require(saved['subject_kind']=='ROOT' and saved['operation']==self.operation,
                'ROOT_RECOVERY_ACTUAL_STARTER_APPEND_REQUIRED')
        recovered=RootCustodyJournalV2(self,preheld=old.lock_fd)
        retained=getattr(self,'append_recoveries',None)
        if retained is None:retained=[];self.append_recoveries=retained
        item={'original_journal':old,'journal':recovered,'uncertainty':uncertainty};retained.append(item)
        action=recovered.load();item['load']=action
        require(action.status in (0,1),'ROOT_RECOVERY_NATIVE_RETAINS_UNKNOWN')
        # Only metadata ownership moves. The original effect lease and original
        # journal remain poisoned and retained; neither can resume handler work.
        self.custody_journal=recovered;self.result_channel.journal=recovered
        original={'operation':self.operation,'original_request':self.request.observation(),
            'value':{'type':type(error).__name__,'message':str(error)}}
        item['unknown']=unknown(self,self.operation,original,error,{'append':uncertainty},
            kind='CAppend',actor_role='RECONCILER')
        history=recovered.history(self.operation)
        persisted=any(raw_archive(event)==raw_archive(saved['attempted_event']) for event in history)
        current=worker_liveness(self,recovered)
        retry={'proposed':cause['raw']['failed_event'],
            'original_owner':saved['candidate']['x5']['actor_identity'],'source':self.source_lease.check()}
        route={'cause':cause,'route':'append-persisted' if persisted else 'append-retry',
            'failed_event':cause['raw']['failed_event'],'retry':retry,'worker':current}
        item['reconciled']=append(self,self.operation,'RECONCILED',original,
            {'cause':cause,'append_uncertainty':saved,'reconciled':route},
            actor_role='RECONCILER',primitive={'unknown_cause':cause})
        supplied=self.root_retry_evidence(saved)
        supplied['actor_role']=saved['actor']
        item['retry']=recovered.append_retry(uncertainty,evidence=supplied)
        item['after']=recovered.load()
        return item

    def root_retry_evidence(self,saved):
        from .root_worker_root_evidence import evidence,lock_receipts,seed,reference,native_item
        from .root_worker_current_state import capture_owner_state
        material=self.capture_root_material(self.custody.frame,self.custody.channel,self.request)
        observed=self.authority.observe(material);capture=self._root_capture
        current=capture_owner_state(self)
        operands={'append_uncertainty':saved,'locks':lock_receipts(self),'seed':seed(self,current)}
        if saved['kind']=='CUSTODY_ACK':
            operands['transfer_event']=reference(self.custody_journal,self.operation,'TRANSFER_SENT')
        elif saved['kind']=='WORKER_RELINQUISH':
            operands['terminal_event']=self.terminal_event['event_id']
            operands['relinquish']={'owners_closed':self.relinquish_owner_receipts,
                'native_event':self.terminal_native,'owner_state':current}
        return evidence(self,self.operation,operands,current=current,
            native=(native_item('root-admission',material,observed,capture.provenance),))

    async def _retain_failed_operation(self,operation,error):
        # Secondary quarantine/report failures never replace the actual cause.
        controls=getattr(self,'failure_controls',None)
        if controls is None:controls=[];self.failure_controls=controls
        retained={'operation':operation,'error':error};controls.append(retained)
        admission=getattr(self,'initial_request_admission',None)
        if operation==self.operation and admission is not None and admission.get('response_event') is None:
            from .root_worker_subject_service import _response_error
            try:
                request_id=admission['peer'].observation()['requestId']
                retained['response_output']=await self.publish_initial_output('RESPONSE_BYTES',
                    _response_error(request_id,error))
            except BaseException as failure:
                retained['response_error']=failure
                error.add_note('Actual initial error response also failed: '+str(failure))
        if self.custody_journal.poisoned:
            try:
                from .root_worker_codec import raw_restore_archive
                saved=raw_restore_archive(self.custody_journal.capture_uncertainty())
                if saved['subject_kind']=='ROOT' and saved['operation']==self.operation:
                    retained['append_recovery']=self.recover_root_append(error)
            except BaseException as failure:
                retained['append_recovery_error']=failure
                error.add_note('Actual root append recovery also failed: '+str(failure))
        try:self.principal.quarantine(operation,error)
        except BaseException as failure:
            retained['quarantine_error']=failure
            error.add_note('Actual original quarantine also failed: '+str(failure))
        try:await self.retain_worker_unknown(error)
        except BaseException as failure:
            retained['report_error']=failure
            error.add_note('Actual root failure report also failed: '+str(failure))
    async def retain_worker_unknown(self,error):
        await self._channel_method('retain_worker_unknown',{'type':type(error).__name__,'message':str(error)})
    async def _channel_method(self,name,value,*,worker_output=None):
        kinds={'send_original_result':'ORIGINAL_RESULT','send_original_terminal':'HANDLER_TERMINAL',
            'send_original_progress':'ORIGINAL_PROGRESS','retain_worker_unknown':'UNKNOWN'}
        require(name in kinds,'ROOT_WORKER_ORIGINAL_CHANNEL_KIND_UNAVAILABLE')
        return await self.result_channel.send(kinds[name],value,worker_output=worker_output)

    def relinquish_owners(self):
        from .root_worker_root_evidence import append,selected_owners,close_owner,lock_receipts,native_item
        from .root_worker_current_state import capture_owner_state
        require(not self.tasks and hasattr(self,'terminal_event'),
                'ROOT_WORKER_AUTHENTIC_TERMINAL_COMMIT_BEFORE_RELINQUISH_REQUIRED')
        p=self.principal
        closers=(('resource.observations',p.resources.observations.close),
            ('resource.journal',p.resources.journal.db.close),('operation.journal',p.journal.db.close),
            ('controller',p.controller.close),('store',p.store.close),
            ('issuer',p.gate.issuer.close),('universe',p.gate.universe.close),('startup',self.lease.db.close))
        before=capture_owner_state(self);before['owners']=selected_owners(self,closers)
        owners_closed=tuple(close_owner(self,name,close) for name,close in closers)
        self.relinquish_owner_receipts=owners_closed
        current=capture_owner_state(self);retained=self.terminal_native
        self.relinquish_event=append(self,self.operation,'WORKER_RELINQUISH',
            {'owners_closed':owners_closed,'native_event':retained,'owner_state':current},
            {'terminal_event':self.terminal_event['event_id'],'locks':lock_receipts(self,before),
                'relinquish':{'owners_closed':owners_closed,'native_event':retained,'owner_state':current}},
            before=before,current=current,
            native=(native_item('root-admission',retained['material'],retained['observation'],retained['provenance']),))
        self.lease.poisoned=True
        self.custody_journal.close()
        for path in reversed(tuple(self.lease.fds)):os.close(self.lease.fds.pop(path))
        self.lease.closed=True

class RootWorkerIntake:
    """Early-selected read/native intake, before StateStore/Gate construction.

    A genuine protected observation producer is required. It must read existing
    full journals under transferred OFDs and independently collect the current
    worker via its owned kernel descriptors. Missing producer is not a default.
    """
    def __init__(self,descriptor):
        from .root_worker_current_state import warm_operation_context_sources
        warm_operation_context_sources()
        self.source=sys.modules.get('_worldline_approved_source_loader')
        require(self.source is not None,'ROOT_WORKER_EARLY_LOADER_REQUIRED')
        self.source_lease=self.source.current();self.source_lease.check()
        self.path=Path(descriptor);raw=private_bytes(self.path);self.descriptor_raw=raw
        require(self.source_lease.file(str(self.path),('DATA',))==raw,
                'ROOT_WORKER_EARLY_DESCRIPTOR_CHANGED')
        self.spec=exact_json(raw)
        from .core import Core
        from .proof_manifest import contract_problems,manifest_problems
        runtime=self.spec['runtime']
        source=Path(runtime['worldline_source']);library=Path(runtime['native_library'])
        proof=exact_json(private_bytes(runtime['proof_manifest']),canonical_required=False)
        require(not contract_problems(source) and not manifest_problems(proof,source,library=library,
            summary=private_bytes(runtime['proof_summary']),require_summary=True),
            'ROOT_WORKER_ORIGINAL_FULL_SOURCE_PROOF_ADMISSION_REQUIRED')
        self.core=Core(Path(runtime['native_library']))
        self.authority=RootAuthority(self.core,self)
        from .root_worker_root_evidence import prepare_capture
        prepare_capture()
    def intact(self):
        self.source_lease.check()
    def bind_received_custody(self,custody):
        from .root_worker_custody import CustodyReceipt
        from .root_worker_journal_v2 import RootCustodyJournalV2
        require(type(custody) is CustodyReceipt and not hasattr(self,'custody'),
                'ROOT_WORKER_INTAKE_CUSTODY_REPLAY')
        selection=custody.frame['root_plan']
        require(type(selection) is dict and set(selection)=={'path','raw'}
            and self.source_lease.file(selection['path'],('DATA',))==selection['raw'],
            'ROOT_WORKER_INTAKE_OWNER_PLAN_UNBOUND')
        self.plan_raw=selection['raw'];self.plan=exact_json(self.plan_raw)
        require(self.plan['startup_descriptor']==str(self.path)
            and self.plan['installation']==self.spec['installation_id'],
            'ROOT_WORKER_INTAKE_OWNER_INSTALLATION_CHANGED')
        self.custody=custody;lock_path=str(self.plan['handoff_journal'])+'.lock'
        require(lock_path in custody.fds,'ROOT_WORKER_ACTUAL_PRIOR_CUSTODY_JOURNAL_LOCK_ABSENT')
        self.custody_journal=RootCustodyJournalV2(self,preheld=custody.fds[lock_path])
    def capture_root_material(self,frame,channel,peer):
        try:
            from .protected_root_observation import RootControllerCapture
        except ImportError as error:
            raise StartupRefusal('ROOT_WORKER_PRECONSTRUCTOR_FULL_CAPTURE_COMPONENT_UNAVAILABLE') from error
        capture=RootControllerCapture(self,frame,channel,peer)
        return capture.complete_native_material()
    def retain_native(self,cause,material,observation):
        # Required protected journal already exists. Its native full capture
        # cannot be rebuilt from a sealed frame or an ordinary assertion.
        from .protected_root_observation import retain_root_native
        return retain_root_native(self,cause,material,observation)
