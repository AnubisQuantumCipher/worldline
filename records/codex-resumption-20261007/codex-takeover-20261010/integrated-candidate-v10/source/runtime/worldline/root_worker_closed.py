"""Owned root closure and fresh-front source path; no live-owner shortcut.

An actual Root slot, its transferred original OFDs, authentic terminal message,
namespace ECHILD, helper/namespace pidfds, actual launcher wait and complete raw
capture precede native REAPED and reconstruction. A prior receiver ACK or initial
result never supplies closure. Incomplete startup/resource/native correspondence
refuses and preserves the actual escrow/unknown accounting obligation.
"""
from __future__ import annotations
import os
from pathlib import Path
from .protected_startup import require,StartupLease
from .root_worker_custody import CustodyOffer,named_identity,identity
from .root_worker_current_state import capture_owner_state
from .root_worker_codec import archive

def _rebind_original_owners(front,fresh):
    """Move the actual retained monitors/tasks, never manufacture replacements."""
    oldp,p=front.principal,fresh.principal
    oldresources,resources=oldp.resources,p.resources
    require(not fresh.slots and not fresh.collectors and not resources.slots
        and not resources.actor_slots,'ROOT_RECONSTRUCTION_FRESH_MONITOR_OWNER_NOT_EMPTY')
    p.pending.update(oldp.pending)
    p.active_peers.update(oldp.active_peers)
    resources.actor_slots.update(oldresources.actor_slots)
    for reservation,monitor in oldresources.slots.items():
        require(monitor.principal is oldresources or monitor.principal is oldp,
                'ROOT_RECONSTRUCTION_ORIGINAL_MONITOR_OWNER_CHANGED')
        monitor.principal=resources if monitor.principal is oldresources else p
        resources.slots[reservation]=monitor
    for operation,slot in front.slots.items():
        require(slot.front is front and slot.principal is oldp,
                'ROOT_RECONSTRUCTION_ORIGINAL_ROOT_SLOT_OWNER_CHANGED')
        slot.front=fresh;slot.principal=p
        owned=slot.owned
        owned.front=fresh;owned.principal=p
        owned.source=fresh.source_lease;owned.journal=fresh.custody_journal
        slot.request=owned.retained_peer;owned.request=slot.request
        p.active_peers[operation]=slot.request
        actor=resources.actor_slots.get(owned.row.bound.reservation)
        if actor is not None:actor['original_request']=slot.request
        offer=getattr(slot,'custody_offer',None)
        if offer is not None:
            offer.p=p
            service=getattr(offer,'subject_service',None)
            if service is not None:service.adopt_front(fresh)
        fresh.slots[operation]=slot
    # The same live asyncio.Task objects and task registry retain ownership.
    # Coroutines resolve their slot.front after each actual asynchronous wait.
    fresh.collectors=front.collectors
    fresh.subject_pumps=front.subject_pumps


class ClosedFrontEscrow:
    def __init__(self,front,offer):
        from .protected_root_worker import RootWorkerFront,RootWorkerIntake
        from .protected_root_supervisor import OwnedRootSupervisor
        require(type(front) is RootWorkerFront and type(offer) is CustodyOffer
            and offer.p is front.principal and offer.state=='WORKER_OWNED',
                'ROOT_CLOSED_REAL_COMMITTED_ESCROW_REQUIRED')
        owned=offer.slot.owned
        require(type(owned) is OwnedRootSupervisor and owned.front is front
            and owned.handler_terminal is not None and owned.closed is not None
            and owned.outer is not None and owned.raw_result is not None and not owned.failed,
                'ROOT_CLOSED_AUTHENTIC_FULL_OWNED_CLOSURE_REQUIRED')
        self.front,self.offer,self.owned=front,offer,owned
        self.frame=offer.frame;self.owned_roster=offer.owned_roster
        self.closed=False;self.claimed=set();self.fds={}
        self.phase='PRECONSTRUCTOR';self.fresh_lease=None;self.proof=None
        self.claim_receipts=[]
        self.peer=owned.retained_peer
        self.operation=owned.operation
        self.intake=RootWorkerIntake(front.lease.descriptor_path)
        self.intake.custody=self;self.intake.frame=self.frame
        self.intake.plan=front.plan;self.intake.plan_raw=front.plan_raw
        self.intake.custody_journal=front.custody_journal
        try:
            for path,fd in offer.fds.items():self.fds[path]=os.dup(fd)
            self.intact()
        except BaseException:
            # Copies close on refusal, original offer/slot/OFDs remain owned.
            self.close();raise
    def _physical_native(self):
        from . import resource_scoped_run_ledger as S
        owned=self.owned;journal=owned.journal
        for event in (owned.handler_terminal,owned.closed,owned.outer,owned.raw_result):journal.require_event(event)
        require(owned.pidfd_state(owned.namespace_pidfd)==b'PIDFD_TERMINAL'
            and owned.pidfd_state(owned.helper_pidfd)==b'PIDFD_TERMINAL'
            and owned.pidfd_state(owned.worker_pidfd)==b'PIDFD_TERMINAL',
                'ROOT_CLOSED_GENUINE_OWNED_PIDFD_TERMINALS_REQUIRED')
        terminal=owned.handler_terminal['record']['value'];seed=terminal['native_event']
        event=owned.execution_event;journal.require_event(event)
        require(event['operation']==self.operation and seed['observation'].status=='ROOT_READY_CONJUNCTION'
            and self.front.authority.kernel.root_controller(**seed['material'])==seed['observation'],
                'ROOT_CLOSED_COMPLETE_HISTORICAL_ROOT_NATIVE_CHANGED')
        material=seed['material'];packet=material['packet'];bound=material['controller'].bound
        require(type(packet) is S.ScopedPacket and bound.operation.hex()==self.operation
            and terminal['original_native_use']==self.frame['original_native_use']
            and seed['provenance']['original_request']==self.peer.observation(),
                'ROOT_CLOSED_ORIGINAL_GRANT_USE_REQUEST_CHANGED')
        rows=[row for row in packet.rows if row.bound==bound]
        require(len(rows)==1 and rows[0].state=='RUNNING','ROOT_CLOSED_ORIGINAL_RUNNING_ROW_ABSENT')
        from .root_scoped_capture_profile import capture_retained_scoped
        retained=capture_retained_scoped(self.intake,{'packet':packet,
            'scoped_projection':seed['provenance']['owned_descriptor_roster']['scoped_projection'],
            'roster':self.owned_roster})
        # Re-observe every actual retained row and descriptor. No other LIVE or
        # UNKNOWN fact is copied from the old root packet as a current fact.
        pending=retained['material'];physical=owned.observe()
        kernel=S.ScopedRunLedgerKernel(self.intake.core);native=kernel.classify(pending)
        require(native.status=='REAPED','ROOT_CLOSED_FULL_NATIVE_PHYSICAL_CLASSIFICATION_REFUSED')
        final=pending;consistent=kernel.validate(final)
        require(consistent.status=='CONSISTENT_SNAPSHOT','ROOT_CLOSED_COMPLETE_NATIVE_SNAPSHOT_REFUSED')
        return {'packet':final,'classification_input':pending,'native':native,'consistent':consistent,
            'physical':physical,'original_row':rows[0],'terminal':owned.handler_terminal,
            'terminal_transport':owned.terminal_transport,'owned_closed':owned.closed,
            'outer_wait':owned.outer,'complete_raw':owned.raw_result,'original_use':terminal['original_native_use'],
            'original_request':self.peer.observation(),
            'historical_root_native':{'operation':self.operation,'record':seed},
            'execution_event':event,'complete_custody_history':journal.history(self.operation),
            'provenance':retained}
    def intact(self):
        require(not self.closed,'ROOT_CLOSED_ESCROW_CLOSED')
        self.intake.source_lease.check();self.front.custody_journal.intact()
        for path,fd in self.fds.items():named_identity(fd,path)
        proof=self._physical_native()
        if self.phase=='PRECONSTRUCTOR':
            terminal=self.owned.handler_terminal['record']['value']
            current=capture_owner_state(self.intake)
            proof['actual_state_correspondence']={'before':terminal['owner_state'],'current':current}
            from .root_worker_root_evidence import evidence,native_item
            profile=evidence(self.front,self.operation,
                {'namespace_event':self.owned.closed['event_id'],'outer_event':self.owned.outer['event_id'],
                    'raw_event':self.owned.raw_result['event_id'],'witness':proof},
                native=(native_item('scoped-classify',proof['classification_input'],proof['native'],proof['provenance']),
                    native_item('scoped-validate',proof['packet'],proof['consistent'],proof['provenance'])))
            profile['actor_role']='FRONT'
            self.closed_owner_decision=self.front.custody_journal.require_closed_owner(
                self.operation,{'complete_native_closed':proof},evidence=profile)
        else:
            require(type(self.fresh_lease) is StartupLease and self.fresh_lease.exec_custody is self,
                    'ROOT_CLOSED_FRESH_OWNER_LEASE_CHANGED')
            self.fresh_lease.intact();self.fresh_lease.loaded()
        self.proof=proof;return proof
    def roster(self,paths,authority_paths):
        self.intact();expected={str(path) for path in paths}|{str(path) for path in authority_paths}
        expected.add(str(self.front.custody_journal.lock_path))
        require(set(self.fds)==expected,'ROOT_CLOSED_WHOLE_ORIGINAL_OFD_ROSTER_CHANGED')
    def claim(self,path):
        self.intact();path=str(path)
        require(path in self.fds and path not in self.claimed,'ROOT_CLOSED_DUPLICATE_OR_ABSENT_OFD_CLAIM')
        from .root_worker_root_evidence import syscall
        fd,receipt=syscall(self.front,'dup',{'fd':self.fds[path],'path':path},lambda:os.dup(self.fds[path]))
        require(fd is not None,'ROOT_CLOSED_ACTUAL_ESCROW_DUP_FAILED')
        _,inherit=syscall(self.front,'set_inheritable',{'fd':fd,'inheritable':False},lambda:os.set_inheritable(fd,False))
        require(inherit['errno']==0,'ROOT_CLOSED_ESCROW_CLOEXEC_FAILED')
        self.claimed.add(path);self.claim_receipts.append({'path':path,'dup':receipt,'cloexec':inherit,'identity':identity(fd)})
        return fd
    def bind_fresh(self,lease):
        require(type(lease) is StartupLease and lease.exec_custody is self
            and lease.descriptor_raw==self.frame['descriptor'] and lease.genesis_raw==self.frame['genesis']
            and self.phase=='PRECONSTRUCTOR','ROOT_CLOSED_FRESH_RECONSTRUCTION_OWNER_CHANGED')
        self.fresh_lease=lease;self.phase='RECONSTRUCTED';self.intact()
        from .protected_root_worker import RootWorkerFront
        from .root_owned_descriptor_roster import OwnedDescriptorRoster
        p=lease.canonical_operation_principal
        p.endpoint_identity=self.front.principal.endpoint_identity
        fresh=RootWorkerFront(p,self.front.path,reconstructing=True)
        self.fresh_front=fresh;fresh.prior_owner=self.front
        holders=getattr(self.front,'_scoped_capture_rosters',[])
        self.closed_capture_rosters=tuple(holders)
        for holder in holders:
            if holder.front is self.front:
                holder.retain_closed_capture(self)
        fresh._scoped_capture_rosters=holders
        _rebind_original_owners(self.front,fresh)
        roster=OwnedDescriptorRoster.reconstruct(fresh,self)
        roster.attach(fresh,p.resources)
    def close(self):
        if self.closed:return
        self.closed=True
        for path in tuple(self.fds):os.close(self.fds.pop(path))
        # Original escrow/slot peer and kernel rights belong to the collector;
        # this constructor-copy cleanup never releases capacity or that owner.

async def collect_and_reconstruct(front,offer,context):
    """Actual background owner, retained even after original response/disconnect."""
    from .protected_root_worker import RootWorkerFront
    front=offer.slot.front
    require(type(front) is RootWorkerFront and type(offer) is CustodyOffer
        and front.slots.get(offer.slot.operation) is offer.slot,
            'ROOT_COLLECTOR_ACTUAL_EXCLUSIVE_SLOT_REQUIRED')
    owned=offer.slot.owned;guard=None
    try:
        await owned.receive_handler_terminal(context)
        await owned.actual_closed_and_outer_wait()
        await owned.complete_raw_drains()
        front=offer.slot.front
        prior_front=front
        guard=ClosedFrontEscrow(front,offer)
        front.closed_escrow=guard
        from .root_worker_root_evidence import append,native_item,process_wait,lock_receipts
        witness=append(front,owned.operation,'CLOSED_WITNESS',{'complete_native_closed':guard.proof},
            {'namespace_event':owned.closed['event_id'],'outer_event':owned.outer['event_id'],
                'raw_event':owned.raw_result['event_id'],'witness':guard.proof},
            native=(native_item('scoped-classify',guard.proof['classification_input'],guard.proof['native'],guard.proof['provenance']),
                native_item('scoped-validate',guard.proof['packet'],guard.proof['consistent'],guard.proof['provenance'])))
        front.custody_journal.require_event(witness)
        # The old target owners stay closed. Real constructors must pass every
        # original startup/native/source/provisioning guard; an unavailable full
        # scoped startup reconciler remains a named refusal, never a bypass.
        lease=StartupLease(front.lease.descriptor_path,custody=guard)
        front.reconstruction_lease=lease
        lease.construct()
        from .protected_scoped_resource_runtime import ProtectedScopedResourcePrincipal
        from .protected_operations import CanonicalOperationPrincipal
        resources=lease.resource_principal;p=lease.canonical_operation_principal
        require(type(resources) is ProtectedScopedResourcePrincipal and resources.lease is lease
            and type(p) is CanonicalOperationPrincipal and p.lease is lease and p.resources is resources,
                'ROOT_COLLECTOR_GENUINE_SCOPED_STARTUP_ATTACHMENT_UNAVAILABLE')
        require(guard.fresh_lease is lease and guard.phase=='RECONSTRUCTED',
                'ROOT_COLLECTOR_STARTUP_CLOSED_GUARD_NOT_BOUND')
        fresh=guard.fresh_front
        require(fresh.principal is p and fresh.lease is lease
            and p.root_worker is fresh,'ROOT_COLLECTOR_BOUND_ACTUAL_FRESH_FRONT_REQUIRED')
        fresh.custody_journal.adopt_owner(fresh)
        front=fresh
        from .root_worker_codec import raw_restore_archive
        retained_before=raw_restore_archive(owned.execution_event['retained_record']['x5']['root_evidence'])['owner_before']
        returned=append(front,owned.operation,'CUSTODY_RETURNED',{'complete_closed_proof':guard.proof},
            {'ecr':{'regime':'front-live','held_event':owned.held_event['event_id'],
                'execution_event':owned.execution_event['event_id'],
                'worker':process_wait(front,owned.worker_pidfd,owned.worker_pidfd_origin['descriptor'],owned.worker_identity),
                'namespace_init':process_wait(front,owned.namespace_pidfd,owned.namespace_pidfd_origin,owned.init_identity),
                'locks':lock_receipts(front,retained_before,fds=offer.fds)}},before=retained_before)
        service=getattr(offer,'subject_service',None)
        if service is not None:
            await service.worker_gone(raw_restore_archive(returned['retained_record']['x5']['root_evidence']),
                returned_event=returned)
        from .root_worker_closed_resource import install_root_closed_witness
        closed=install_root_closed_witness(p,guard)
        record=owned.handler_terminal['record']['value']['result']
        with p.historical_scope(owned.operation):settled=p.finish(owned.operation,record)
        from .root_worker_root_evidence import scoped_commit
        from . import resource_scoped_run_ledger as S
        history=resources.scoped_service.committed_history()
        committed={S.restore(item['packet']).request.original.kind:scoped_commit(resources,S.restore(item['packet']))
            for item in history if S.restore(item['packet']).request.original.bound.operation.hex()==owned.operation}
        settlement={'terminal':committed['RECORD_TERMINAL']}
        if 'RELEASE_HOLD' in committed:settlement['release']=committed['RELEASE_HOLD']
        if 'CHARGE_BUDGET' in committed:settlement['charge']=committed['CHARGE_BUDGET']
        physical_settled=append(front,owned.operation,'PHYSICAL_SETTLED',
            {'complete_closed_witness':closed,'complete_resource_settlement':settlement},
            {'witness_event':witness['event_id'],'settlement':settlement})
        event=append(front,owned.operation,'HISTORICAL_SETTLEMENT',
            {'complete_closed_witness':closed,'complete_native_settlement':settled,'result':record},
            {'returned_event':returned['event_id'],'historical':{'event':settled,
                'material':settled['snapshot'],'observation':settled['native']['observation'],
                'result':record,'use':guard.proof['original_use']}})
        front.custody_journal.require_event(event)
        from .daemon import WorldlineDaemon
        from .status import StatusPublisher
        daemon=WorldlineDaemon(p.controller.paths,p.store,StatusPublisher(p.controller.paths,p.store))
        p.controller.register(daemon)
        def resolution(_args,_ctx):raise RuntimeError('principal owns distinct resolution')
        daemon.register('quarantine.resolve',resolution,mutating=True,owner_only=True)
        require(set(daemon._operations)<=set(p.operation_names)|set(p.owner_names),
                'ROOT_COLLECTOR_FRESH_ORIGINAL_HANDLER_ROSTER_UNBOUND')
        fresh.daemon=daemon
        from .root_worker_root_evidence import scoped_capture
        packet,_classification,consistent,_raw=scoped_capture(resources,guard.proof['original_row'].bound.reservation)
        current=capture_owner_state(fresh)
        reconstruction=append(fresh,owned.operation,'FRONT_RECONSTRUCTION',
            {'settlement':event,'fresh_state':current,'source':fresh.source_lease.check()},
            {'settlement_event':event['event_id'],'locks':lock_receipts(fresh,current),
                'reconstruction':{'fresh_state':current,'descriptor':lease.descriptor_raw,'genesis':lease.genesis_raw,
                    'policy':lease.canonical_operation_principal.policy,'source':lease.source_lease.check(),
                    'escrow_claims':tuple(guard.claim_receipts)}},
            current=current,native=(native_item('scoped-validate',packet,consistent,_raw),))
        old_end=front.custody_journal.root_state(owned.operation)
        append(fresh,owned.operation,'FRONT_OWNED',{'old_end':old_end,'new_owner':current},
            {'reconstruction_event':reconstruction['event_id'],'locks':lock_receipts(fresh,current),
                'front_owned':{'old_end':old_end,'new_owner':current}},
            current=current,native=(native_item('scoped-validate',packet,consistent,_raw),))
        lease.require_front_startup()
        fresh.phase='FRONT_OWNED';prior_front.fresh_front=fresh;prior_front.phase='RECONSTRUCTED_CLOSED'
        fresh.slots.pop(owned.operation)
        resources.slots.pop(owned.row.bound.reservation.hex())
        resources.actor_slots.pop(owned.row.bound.reservation,None)
        p.active_peers.pop(owned.operation,None)
        offer.close_subject_escrow()
        offer.close_received_copies();guard.close();owned.retained_peer.close()
        owned.close_received_rights()
        for holder in guard.closed_capture_rosters:holder.close()
        retained=fresh._scoped_capture_rosters
        retained[:]=[holder for holder in retained
            if all(holder is not old for old in guard.closed_capture_rosters)]
        return fresh
    except BaseException as error:
        front.phase='UNKNOWN_CLOSED_RECONSTRUCTION'
        front.collector_failure={'type':type(error).__name__,'message':str(error)}
        from .root_worker_root_evidence import unknown
        try:front.collector_failure_event=unknown(front,owned.operation,
            {'failure':front.collector_failure,'physical_closed':owned.closed,'actual_outer':owned.outer,
             'raw':owned.raw_result,'handler_terminal':owned.handler_terminal,
             'retained_guard':None if guard is None else guard.proof},error,
            {'expected':'complete native CLOSED and genuine fresh owner','actual':front.collector_failure})
        except BaseException as commit_error:
            front.collector_failure['durable_error']={'type':type(commit_error).__name__,'message':str(commit_error)}
        # Keep all original OFDs/rights/journals and charge/hold. No partial
        # constructor or initial response becomes accepted closure/settlement.
        raise
