"""Actual failed-handoff collection. Native replay owns closure and accounting.

There is deliberately no handler result. A committed native failed handoff,
the same owned worker/namespace/helper, full CLOSED protocol, actual launcher
wait, raw EOF/fsync and complete current escrow precede reconstruction. The
original operation use stays natively QUARANTINED pending distinct resolution.
"""
import asyncio,math,os,signal
from .protected_startup import require,StartupLease
from .root_worker_closed import ClosedFrontEscrow,_rebind_original_owners
from .root_worker_custody import CustodyOffer,identity,named_identity
from .root_worker_current_state import capture_owner_state
from .root_worker_codec import raw_restore_archive


def intact(owned):
    from .protected_root_supervisor import OwnedRootSupervisor
    require(type(owned) is OwnedRootSupervisor and owned.failed and owned.held is not None
        and owned.execution_event is not None and owned.failure_event is not None,
        'ROOT_FAILED_ACTUAL_OWNED_DISPATCH_REQUIRED')
    owned.source.check();owned.journal.intact()
    failure=owned.journal.require_event(owned.failure_event)
    require(failure['operation']==owned.operation
        and failure['kind'] in ('HANDOFF_ABORT','FRONT_RETAINED_ESCROW'),
        'ROOT_FAILED_AUTHENTIC_NATIVE_FAILURE_REQUIRED')
    owned.journal.require_event(owned.execution_event)
    owned.journal.require_event(owned.held_event)
    import socket,struct
    require(owned.connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,struct.calcsize('@iII'))
        ==owned.held['peer'],'ROOT_FAILED_ORIGINAL_HELPER_PEER_CHANGED')
    require(identity(owned.namespace_fd)==owned.held['namespace_identity'],
        'ROOT_FAILED_ORIGINAL_NAMESPACE_CHANGED')
    offer=owned.failure_offer
    require(type(offer) is CustodyOffer and offer.slot.owned is owned
        and offer.slot.front is owned.front and offer.closed_owners
        and offer.front_closed_event is not None,'ROOT_FAILED_COMPLETE_CLOSED_FRONT_REQUIRED')
    owned.journal.require_event(offer.front_closed_event)
    if failure['kind']=='HANDOFF_ABORT':
        require(not offer.send_receipts and not offer.owned_roster.send_receipts
            and not offer.subject_send_receipts and getattr(offer,'transfer_event',None) is None,
            'ROOT_FAILED_ABORT_ACTUAL_PARTIAL_SEND_UNKNOWN')
    else:
        require(getattr(offer,'transfer_event',None) is not None,'ROOT_FAILED_ESCROW_ORIGINAL_TRANSFER_ABSENT')
        owned.journal.require_event(offer.transfer_event)
    for path,fd in offer.fds.items():named_identity(fd,path)
    return failure


async def physical(owned,offer):
    """Stop only the held admitted worker; the real init/helper retains reaping."""
    owned.failure_offer=offer
    intact(owned)
    from .root_worker_root_evidence import capture_effect,process_wait
    policy=owned.dispatch['resource_dispatch']['payload']['plan']['policy']
    timeout=policy['timeoutSeconds']
    require(type(timeout) in (int,float) and math.isfinite(timeout) and timeout>0,
        'ROOT_FAILED_ORIGINAL_FINITE_WORKER_TIMEOUT_REQUIRED')
    async def collect():
        # Bind the original held pidfd before signaling, retaining even failure.
        owned.failure_physical_attempts=[]
        attempt={'worker_origin':owned.worker_pidfd_origin,'worker_current':identity(owned.worker_pidfd),
            'worker_poll_before':process_wait(owned.front,owned.worker_pidfd,
                owned.worker_pidfd_origin['descriptor'],owned.worker_identity),
            'source':owned.source.check()}
        owned.failure_physical_attempts.append(attempt)
        if owned.stdin_fd is not None:
            attempt['stdin_original_writer_before']=identity(owned.stdin_fd)
            attempt['stdin_observation_closures']=owned.close_input()
            attempt['stdin_close_receipts']=tuple(owned.stdin_close_receipts)
        require(owned.stdin_fd is None,'ROOT_FAILED_ORIGINAL_WRITER_STILL_HELD')
        try:
            state=owned.pidfd_state(owned.worker_pidfd);attempt['worker_state_before']=state
            if state==b'PIDFD_TERMINAL':
                attempt['signal']=None
            else:
                require(state==b'PIDFD_LIVE','ROOT_FAILED_SIGNAL_PIDFD_UNKNOWN')
                _value,receipt=capture_effect(owned.source,'pidfd_send_signal',
                    {'pidfd':owned.worker_pidfd,'signal':signal.SIGTERM,'siginfo':None,'flags':0},
                    lambda:signal.pidfd_send_signal(owned.worker_pidfd,signal.SIGTERM,None,0))
                attempt['signal']=receipt
        except BaseException as error:
            attempt['signal']=getattr(error,'custody_receipt',None)
            attempt['error']={'type':type(error).__qualname__,'message':str(error)}
            raise
        await owned.failed_actual_closed_and_outer_wait()
        await owned.failed_complete_raw_drains()
        attempt['closed']=owned.closed;attempt['outer']=owned.outer;attempt['raw']=owned.raw_result
        intact(owned)
        return attempt
    # One selected original worker window; never renew after ARM/stop/waits.
    task=asyncio.create_task(collect())
    owned.failure_physical_task=task
    try:return await asyncio.wait_for(task,timeout)
    except BaseException as error:
        owned.failure_physical_error={'type':type(error).__qualname__,'message':str(error)}
        # Actual task/cancellation remains retained. Unknown waits never release.
        raise


class FailedFrontEscrow(ClosedFrontEscrow):
    """Distinct failed guard; the successful guard's domain stays unchanged."""
    def __init__(self,front,offer):
        from .protected_root_worker import RootWorkerFront,RootWorkerIntake
        require(type(front) is RootWorkerFront and type(offer) is CustodyOffer
            and offer.p is front.principal,'ROOT_FAILED_REAL_FRONT_OFFER_REQUIRED')
        owned=offer.slot.owned;intact(owned)
        require(owned.front is front and owned.closed is not None and owned.outer is not None
            and owned.raw_result is not None and owned.handler_terminal is None,
            'ROOT_FAILED_FULL_PHYSICAL_NO_HANDLER_REQUIRED')
        self.front,self.offer,self.owned=front,offer,owned
        self.frame=offer.frame;self.owned_roster=offer.owned_roster
        self.closed=False;self.claimed=set();self.fds={};self.close_attempts=[]
        self.phase='PRECONSTRUCTOR';self.fresh_lease=None;self.proof=None;self.claim_receipts=[]
        self.peer=owned.retained_peer;self.operation=owned.operation
        self.intake=RootWorkerIntake(front.lease.descriptor_path)
        self.intake.custody=self;self.intake.frame=self.frame
        self.intake.plan=front.plan;self.intake.plan_raw=front.plan_raw
        self.intake.custody_journal=front.custody_journal
        self.failure_owner=raw_restore_archive(owned.failure_event['retained_record']['x5']['root_evidence'])['owner_current']
        self.owned_roster.retain_failed_physical_closure(front,owned)
        try:
            for path,fd in offer.fds.items():self.fds[path]=os.dup(fd)
            self.intact()
        except BaseException as error:
            try:self.close()
            except BaseException as close_error:error.add_note('Actual failed guard copy close: '+repr(close_error))
            raise

    def _physical_native(self):
        intact(self.owned)
        from . import resource_scoped_run_ledger as S
        from .root_scoped_capture_profile import capture_retained_scoped
        owned=self.owned;journal=owned.journal
        for event in (owned.failure_event,owned.execution_event,owned.closed,owned.outer,owned.raw_result):
            journal.require_event(event)
        require(all(owned.pidfd_state(fd)==b'PIDFD_TERMINAL'
            for fd in (owned.namespace_pidfd,owned.helper_pidfd,owned.worker_pidfd)),
            'ROOT_FAILED_FULL_ACTUAL_PIDFD_TERMINALS_REQUIRED')
        seed=self.frame['root_native'];material=seed['material']
        require(seed['observation'].status=='ROOT_READY_CONJUNCTION'
            and self.front.authority.kernel.root_controller(**material)==seed['observation'],
            'ROOT_FAILED_FULL_ORIGINAL_NATIVE_ADMISSION_CHANGED')
        packet=material['packet'];bound=material['controller'].bound
        require(type(packet) is S.ScopedPacket and bound.operation.hex()==self.operation
            and seed['provenance']['original_request']==self.peer.observation(),
            'ROOT_FAILED_ORIGINAL_BOUND_REQUEST_CHANGED')
        rows=[row for row in packet.rows if row.bound==bound]
        require(len(rows)==1 and rows[0].state=='RUNNING','ROOT_FAILED_ORIGINAL_RUNNING_ROW_REQUIRED')
        retained=capture_retained_scoped(self.intake,{'packet':packet,
            'scoped_projection':seed['provenance']['owned_descriptor_roster']['scoped_projection'],
            'roster':self.owned_roster})
        current=retained['material'];kernel=S.ScopedRunLedgerKernel(self.intake.core)
        native=kernel.classify(current);consistent=kernel.validate(current)
        require(native.status=='REAPED' and consistent.status=='CONSISTENT_SNAPSHOT',
            'ROOT_FAILED_COMPLETE_NATIVE_PHYSICAL_REFUSAL')
        return {'failure_schema':'worldline.failed-root-physical-closure-v1',
            'failure_event':owned.failure_event,'handoff_intent':self.offer.intent,
            'failure_owner_state':self.failure_owner,'packet':current,'classification_input':current,
            'native':native,'consistent':consistent,'physical':owned.failed_observe(),'original_row':rows[0],
            'terminal':None,'terminal_transport':None,'owned_closed':owned.closed,'outer_wait':owned.outer,
            'complete_raw':owned.raw_result,'original_use':self.frame['original_native_use'],
            'original_request':self.peer.observation(),'historical_root_native':{'operation':self.operation,'record':seed},
            'execution_event':owned.execution_event,'complete_custody_history':journal.history(self.operation),
            'provenance':retained}

    def intact(self):
        require(not self.closed,'ROOT_FAILED_ESCROW_CLOSED')
        self.intake.source_lease.check();self.front.custody_journal.intact()
        for path,fd in self.fds.items():named_identity(fd,path)
        proof=self._physical_native()
        if self.phase=='PRECONSTRUCTOR':
            proof['actual_state_correspondence']={'before':self.failure_owner,'current':capture_owner_state(self.intake)}
            from .root_worker_root_evidence import evidence,native_item
            profile=evidence(self.front,self.operation,{'namespace_event':self.owned.closed['event_id'],
                'outer_event':self.owned.outer['event_id'],'raw_event':self.owned.raw_result['event_id'],'witness':proof},
                native=(native_item('scoped-classify',proof['classification_input'],proof['native'],proof['provenance']),
                    native_item('scoped-validate',proof['packet'],proof['consistent'],proof['provenance'])))
            profile['actor_role']='FRONT'
            self.closed_owner_decision=self.front.custody_journal.require_closed_owner(
                self.operation,{'complete_native_closed':proof},evidence=profile)
        else:
            require(type(self.fresh_lease) is StartupLease and self.fresh_lease.exec_custody is self,
                'ROOT_FAILED_FRESH_OWNER_LEASE_CHANGED')
            self.fresh_lease.intact();self.fresh_lease.loaded()
        self.proof=proof;return proof

    def close(self):
        if self.closed:return
        self.closed=True;failure=None
        for path in tuple(self.fds):
            fd=self.fds.pop(path);attempt={'path':path,'fd':fd};self.close_attempts.append(attempt)
            try:os.close(fd)
            except OSError as error:
                attempt.update(result=-1,errno=error.errno,message=str(error))
                if failure is None:failure=error
            else:attempt.update(result=0,errno=0)
        if failure is not None:raise failure


async def collect_failed_and_reconstruct(front,offer,error):
    """Genuine native failure history remains distinguishable from success."""
    owned=offer.slot.owned;guard=None
    require(front.slots.get(owned.operation) is offer.slot,'ROOT_FAILED_EXCLUSIVE_SLOT_REQUIRED')
    try:
        await physical(owned,offer)
        guard=FailedFrontEscrow(front,offer);front.closed_escrow=guard
        from .root_worker_root_evidence import append,native_item,process_wait,lock_receipts,scoped_capture,scoped_commit
        witness=append(front,owned.operation,'CLOSED_WITNESS',{'complete_native_closed':guard.proof},
            {'namespace_event':owned.closed['event_id'],'outer_event':owned.outer['event_id'],
                'raw_event':owned.raw_result['event_id'],'witness':guard.proof},actor_role='FRONT',
            native=(native_item('scoped-classify',guard.proof['classification_input'],guard.proof['native'],guard.proof['provenance']),
                native_item('scoped-validate',guard.proof['packet'],guard.proof['consistent'],guard.proof['provenance'])))
        front.custody_journal.require_event(witness)
        lease=StartupLease(front.lease.descriptor_path,custody=guard)
        front.reconstruction_lease=lease
        recorder=getattr(front.lease,'operation_native_recorder',None)
        if recorder is not None:lease.set_operation_native_recorder(recorder)
        lease.construct()
        fresh=guard.fresh_front;p=fresh.principal;resources=p.resources
        require(guard.fresh_lease is lease and fresh.lease is lease and p.root_worker is fresh,
            'ROOT_FAILED_ACTUAL_NATIVE_APPROVED_RECONSTRUCTION_REQUIRED')
        fresh.custody_journal.adopt_owner(fresh)
        retained_before=raw_restore_archive(owned.execution_event['retained_record']['x5']['root_evidence'])['owner_before']
        returned=append(fresh,owned.operation,'CUSTODY_RETURNED',{'complete_closed_proof':guard.proof},
            {'ecr':{'regime':'front-live','held_event':owned.held_event['event_id'],
                'execution_event':owned.execution_event['event_id'],
                'worker':process_wait(fresh,owned.worker_pidfd,owned.worker_pidfd_origin['descriptor'],owned.worker_identity),
                'namespace_init':process_wait(fresh,owned.namespace_pidfd,owned.namespace_pidfd_origin,owned.init_identity),
                'locks':lock_receipts(fresh,retained_before,fds=offer.fds)}},before=retained_before)
        service=getattr(offer,'subject_service',None)
        if service is not None:
            service.worker_gone(raw_restore_archive(returned['retained_record']['x5']['root_evidence']),returned_event=returned)
        from .root_worker_closed_resource import install_root_closed_witness
        closed=install_root_closed_witness(p,guard)
        # No handler result/effect is asserted. Native quarantine retains the use.
        p.quarantine(owned.operation,error)
        p.unresolved.add(owned.operation)
        resources.settle_bound(p.pending_for_operation(owned.operation),owned.retained_peer,
            guard.proof['original_row'].bound.reservation)
        from . import resource_scoped_run_ledger as S
        history=resources.scoped_service.committed_history()
        committed={S.restore(item['packet']).request.original.kind:scoped_commit(resources,S.restore(item['packet']))
            for item in history if S.restore(item['packet']).request.original.bound.operation.hex()==owned.operation}
        settlement={'terminal':committed['RECORD_TERMINAL']}
        if 'RELEASE_HOLD' in committed:settlement['release']=committed['RELEASE_HOLD']
        if 'CHARGE_BUDGET' in committed:settlement['charge']=committed['CHARGE_BUDGET']
        append(fresh,owned.operation,'PHYSICAL_SETTLED',{'complete_closed_witness':closed,
            'complete_resource_settlement':settlement},{'witness_event':witness['event_id'],'settlement':settlement})
        row=p.journal.rows[owned.operation]
        require(row['state']=='QUARANTINED' and row['native']['command']=='QUARANTINE_USE',
            'ROOT_FAILED_REAL_NATIVE_QUARANTINE_REQUIRED')
        event=append(fresh,owned.operation,'HISTORICAL_SETTLEMENT',{'complete_closed_witness':closed,
            'complete_native_settlement':row,'result':None},
            {'returned_event':returned['event_id'],'historical':{'event':row,'material':row['snapshot'],
                'observation':row['native']['observation'],'result':None,'use':guard.proof['original_use']}})
        fresh.custody_journal.require_event(event)
        # The same real handlers are constructed; unresolved-use policy remains.
        from .daemon import WorldlineDaemon
        from .status import StatusPublisher
        daemon=WorldlineDaemon(p.controller.paths,p.store,StatusPublisher(p.controller.paths,p.store));p.controller.register(daemon)
        def resolution(_args,_ctx):raise RuntimeError('principal owns distinct resolution')
        daemon.register('quarantine.resolve',resolution,mutating=True,owner_only=True)
        require(set(daemon._operations)<=set(p.operation_names)|set(p.owner_names),
            'ROOT_FAILED_FRESH_HANDLER_ROSTER_UNBOUND')
        fresh.daemon=daemon
        packet,_classification,consistent,raw=scoped_capture(resources,guard.proof['original_row'].bound.reservation)
        current=capture_owner_state(fresh)
        reconstruction=append(fresh,owned.operation,'FRONT_RECONSTRUCTION',{'settlement':event,'fresh_state':current,
            'source':fresh.source_lease.check()},
            {'settlement_event':event['event_id'],'locks':lock_receipts(fresh,current),
                'reconstruction':{'fresh_state':current,'descriptor':lease.descriptor_raw,'genesis':lease.genesis_raw,
                    'policy':p.policy,'source':lease.source_lease.check(),'escrow_claims':tuple(guard.claim_receipts)}},
            current=current,native=(native_item('scoped-validate',packet,consistent,raw),))
        old_end=fresh.custody_journal.root_state(owned.operation)
        append(fresh,owned.operation,'FRONT_OWNED',{'old_end':old_end,'new_owner':current},
            {'reconstruction_event':reconstruction['event_id'],'locks':lock_receipts(fresh,current),
                'front_owned':{'old_end':old_end,'new_owner':current}},current=current,
            native=(native_item('scoped-validate',packet,consistent,raw),))
        lease.require_front_startup()
        fresh.phase='FRONT_OWNED';front.fresh_front=fresh;front.phase='RECONSTRUCTED_CLOSED'
        # Disposal follows real committed closure/accounting/startup only.
        fresh.slots.pop(owned.operation);resources.slots.pop(owned.row.bound.reservation.hex())
        resources.actor_slots.pop(owned.row.bound.reservation,None);p.active_peers.pop(owned.operation,None)
        offer.close_subject_escrow();dispose_offer(offer);guard.close();owned.retained_peer.close()
        dispose_owned(owned)
        for holder in guard.closed_capture_rosters:holder.close()
        fresh._scoped_capture_rosters[:]=[holder for holder in fresh._scoped_capture_rosters
            if all(holder is not old for old in guard.closed_capture_rosters)]
        owned.failure_reconstructed_front=fresh
        return fresh
    except BaseException as failure:
        front.failed_physical_collection={'type':type(failure).__qualname__,'message':str(failure),
            'physical_closed':owned.closed,'actual_outer':owned.outer,'raw':owned.raw_result,
            'retained_guard':None if guard is None else guard.proof}
        front.phase='UNKNOWN_FAILED_PHYSICAL_RECONSTRUCTION'
        from .root_worker_root_evidence import unknown
        try:
            front.failed_physical_collection_event=unknown(owned.front,owned.operation,
                front.failed_physical_collection,failure,
                {'expected':'complete distinct native failed closure and actual fresh owner',
                    'actual':front.failed_physical_collection})
        except BaseException as commit_error:
            front.failed_physical_collection['durable_error']={'type':type(commit_error).__qualname__,
                'message':str(commit_error)}
            if owned.journal.poisoned:
                front.failed_physical_collection['uncertainty']=owned.journal.capture_uncertainty()
        raise


def dispose_offer(offer):
    """Only after real returned/settled custody; never retry a numeric close."""
    offer.slot.front.custody_journal.require_event(offer.subject_service.returned_event)
    from .custody_subject_capture import close_descriptor
    source=offer.p.lease.source_lease.check();errors=[]
    for mapping in (offer.fds,offer.origins):
        for key in tuple(mapping):
            fd=mapping.pop(key)
            try:receipt=close_descriptor(fd,source)
            except BaseException as error:
                offer.close_receipts.append({'key':key,'fd':fd,'exception':type(error).__qualname__,'message':str(error)})
                errors.append(error)
            else:
                offer.close_receipts.append(receipt)
                if receipt['result']!=0:errors.append(RuntimeError('ROOT_FAILED_ESCROW_CLOSE_UNKNOWN'))
    try:offer.owned_roster.close()
    except BaseException as error:errors.append(error)
    try:offer.original_peer.close()
    except BaseException as error:errors.append(error)
    if errors:raise errors[0]


def dispose_owned(owned):
    require(owned.stdin_fd is None,'ROOT_FAILED_ORIGINAL_STDIN_LIFETIME_UNCLOSED')
    from .custody_subject_capture import close_descriptor
    source=owned.source.check();owned.failure_disposal_attempts=[];errors=[]
    for name in ('credential_receiver','custody_channel','connection'):
        channel=getattr(owned,name,None)
        if channel is None:continue
        setattr(owned,name,None)
        try:fd=channel.detach()
        except BaseException as error:
            owned.failure_disposal_attempts.append({'name':name,'error':type(error).__qualname__,'message':str(error)})
            errors.append(error);continue
        try:receipt=close_descriptor(fd,source)
        except BaseException as error:
            owned.failure_disposal_attempts.append({'name':name,'fd':fd,'error':type(error).__qualname__,'message':str(error)})
            errors.append(error)
        else:
            owned.failure_disposal_attempts.append({'name':name,'receipt':receipt})
            if receipt['result']!=0:errors.append(RuntimeError('ROOT_FAILED_SOCKET_CLOSE_UNKNOWN'))
    for name in ('namespace_fd','namespace_pidfd','helper_pidfd','worker_pidfd','stdout_fd','stderr_fd'):
        fd=getattr(owned,name,None)
        if fd is None:continue
        setattr(owned,name,None)
        try:receipt=close_descriptor(fd,source)
        except BaseException as error:
            owned.failure_disposal_attempts.append({'name':name,'fd':fd,'error':type(error).__qualname__,'message':str(error)})
            errors.append(error)
        else:
            owned.failure_disposal_attempts.append({'name':name,'receipt':receipt})
            if receipt['result']!=0:errors.append(RuntimeError('ROOT_FAILED_RIGHT_CLOSE_UNKNOWN'))
    if errors:raise errors[0]
