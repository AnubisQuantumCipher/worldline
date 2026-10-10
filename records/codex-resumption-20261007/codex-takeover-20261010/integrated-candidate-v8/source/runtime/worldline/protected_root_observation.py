"""Actual root current-state/process producer, before or after constructors.

Full sender inputs are retained history. The intake recaptures existing complete
protected state under transferred OFDs plus actual kernel process/helper/manager
observations before constructing any target Store/Controller/Gate. Factual state
correspondence is not permission: the complete selected root native conjunction
is always redecided. Full source/projection/custody/body/cost proof remains open.
"""
from dataclasses import replace
import hashlib,os,struct
from pathlib import Path
from .protected_startup import require,digest
from .root_worker_codec import archive
from .root_worker_current_state import capture_owner_state,same_logical_state
from .root_worker_process_capture import RootProcessCapture
from .root_worker_custody import identity,channel_source

def complete(value):
    from .protected_resource_runtime import canonical
    from . import resource_scoped_run_ledger as S
    return canonical(S.record(value))

class RootControllerCapture:
    def __init__(self,owner,frame,channel,peer):
        from .protected_root_worker import RootWorkerFront,RootWorkerIntake,RootWorkerProcess
        from .client_peer import RequestPeer
        require(type(owner) in (RootWorkerFront,RootWorkerIntake,RootWorkerProcess)
            and type(peer) is RequestPeer,'ROOT_CAPTURE_ACTUAL_CUSTODY_OWNER_AND_PEER_REQUIRED')
        owner.source_lease.check();peer.observation()
        self.owner,self.frame,self.channel,self.peer=owner,frame,channel,peer
        self.provenance=None;self.material=None
    def _controller(self,row,physical,process,source,plan,running):
        from .resource_child_schema import RootController
        owner=self.owner;observation=self.peer.observation()
        _pid,uid,gid=struct.unpack('@iII',bytes.fromhex(observation['peer']['rawUcred']))
        source_id=hashlib.sha256(complete(owner.spec)).digest()
        handler_id=hashlib.sha256(complete(plan)).digest()
        running_id=hashlib.sha256(complete(running)).digest()
        expected_endpoint=owner.spec['endpoint']['path'].encode('utf-8')
        image=physical['native_fields']['helper_image']
        return RootController(bound=row.bound,process=process,requester_uid=uid,requester_gid=gid,
            raw_manager=complete(physical['raw']['manager']),raw_channel=complete(channel_source(self.channel)),
            owner_endpoint=expected_endpoint,expected_owner_endpoint=expected_endpoint,
            source_lease=source_id,expected_source_lease=source_id,worker_image=image,expected_worker_image=image,
            handler_plan=handler_id,expected_handler_plan=handler_id,raw_request=complete(observation),
            requester=row.bound.owner,dispatch=physical['native_fields']['dispatch'],
            running_event=running_id,expected_running_event=running_id,
            store_genesis=source['actual_store_genesis'].encode('utf-8'),
            expected_store_genesis=source['actual_store_genesis'].encode('utf-8'),current_source=complete(source))
    def _current(self):
        from .protected_root_worker import RootWorkerFront,RootWorkerProcess
        from .canonical_actor_execution import scoped_components,capture_execution
        from .root_worker_physical import observe
        from . import resource_scoped_run_ledger as S
        owner=self.owner;p=owner.principal;producer=scoped_components(p)
        operation=owner.operation if type(owner) is RootWorkerProcess else self.frame['held']['dispatch']['operation']
        with p.gate.mutex,producer.order:
            p.intact();captured=p.journal.rows[operation]['capture'];reservation=captured['resource_intent'].reservation
            require(p.active_peers.get(operation) is self.peer and captured['request']==self.peer.observation(),
                    'ROOT_CAPTURE_ACTUAL_ORIGINAL_REQUESTER_CHANGED')
            authority=capture_execution(p,operation,reservation,self.peer)
            before=producer.current_snapshot();current,source,_catalogue=producer._context(before)
            observed,facts,raw,classified=producer._capture(before,current)
            packet=producer._inspect(before,current,observed,facts,producer._request(before,reservation))
            selected=[item for item in before.rows if item.bound==captured['resource_intent'].bound]
            require(len(selected)==1 and selected[0].state=='RUNNING','ROOT_CAPTURE_ACTUAL_NATIVE_RUNNING_REQUIRED')
            row=selected[0]
            if type(owner) is RootWorkerFront:
                slot=owner.slots.get(operation)
                require(slot is not None,'ROOT_CAPTURE_ACTUAL_ROOT_SLOT_ABSENT')
                owned=slot.owned;physical=owned.observe();rights={'host_proc':os.open('/proc',os.O_RDONLY|os.O_DIRECTORY|os.O_CLOEXEC),
                    'worker_pidfd':owned.worker_pidfd,'worker_namespace':owned.namespace_fd}
                try:
                    process,process_raw=RootProcessCapture(rights['host_proc'],rights['worker_pidfd'],
                        rights['worker_namespace'],owner.source_lease).capture(row.actual_unit,row.invocation,
                            hashlib.sha256(complete(owner.spec)).digest())
                finally:os.close(rights['host_proc'])
            else:
                rights=owner.custody.origins;held=self.frame['worker']['held'];dispatch=held['dispatch']
                physical=observe(owner,row,dispatch,held,rights)
                process,process_raw=RootProcessCapture(rights['host_proc'],rights['worker_pidfd'],
                    rights['worker_namespace'],owner.source_lease).capture(row.actual_unit,row.invocation,
                        hashlib.sha256(complete(owner.spec)).digest())
            plan=authority['plan'];running=[event for event in authority['scoped_history']
                if S.restore(event['packet']).request.original.kind=='RECORD_RUNNING']
            require(len(running)==1,'ROOT_CAPTURE_SINGLE_ACTUAL_RUNNING_EVENT_REQUIRED')
            controller=self._controller(row,physical,process,source,plan,running[0])
            crosswalk=producer._execution_crosswalk(authority,current,plan,row.bound.owner)
            require(crosswalk.current_source==controller.current_source and crosswalk.selected_plan==controller.handler_plan,
                    'ROOT_CAPTURE_CURRENT_PLAN_OR_SOURCE_PROJECTION_CHANGED')
            material={'packet':packet,'controller':controller,'crosswalk':crosswalk,
                'authority_snapshot':authority['authority_snapshot']}
            state=capture_owner_state(owner)
            provenance={'authority':authority,'current_source':source,'running_event':running[0],
                'resource_capture':raw,'resource_classifications':classified,'physical':physical,
                'process':process_raw,'owner_state':state,'original_request':self.peer.observation()}
            return material,provenance
    def _before_constructors(self):
        from . import resource_scoped_run_ledger as S
        from .resource_run_ledger import RunObservation
        from .root_worker_physical import observe
        owner=self.owner;frame=self.frame
        require(owner.custody.frame is frame and owner.custody.peer is self.peer,
                'ROOT_CAPTURE_ACTUAL_RECEIVED_CUSTODY_REQUIRED')
        event=owner.custody_journal.require_event(frame['root_native'])
        seed=event['record']
        require(set(seed)=={'cause','material','observation','provenance'}
            and seed['observation'].status=='ROOT_READY_CONJUNCTION',
                'ROOT_CAPTURE_COMPLETE_RETAINED_ROOT_NATIVE_SEED_REQUIRED')
        before=seed['provenance']['owner_state'];current_state=capture_owner_state(owner)
        correspondence=same_logical_state(before,current_state)
        material=seed['material'];packet=material['packet'];original=material['controller']
        require(type(packet) is S.ScopedPacket and original.bound.operation.hex()==frame['operation']
            and seed['provenance']['original_request']==self.peer.observation(),
                'ROOT_CAPTURE_RETAINED_ORIGINAL_TUPLE_CHANGED')
        rows=[row for row in packet.rows if row.bound==original.bound]
        require(len(rows)==1 and rows[0].state=='RUNNING','ROOT_CAPTURE_CURRENT_ROOT_ROW_UNAVAILABLE')
        row=rows[0];held=frame['worker']['held'];dispatch=held['dispatch']
        physical=observe(owner,row,dispatch,held,owner.custody.origins)
        process,process_raw=RootProcessCapture(owner.custody.origins['host_proc'],owner.custody.origins['worker_pidfd'],
            owner.custody.origins['worker_namespace'],owner.source_lease).capture(row.actual_unit,row.invocation,original.source_lease)
        # Complete current descriptor handoff for another LIVE reservation has
        # not yet been authored. Do not silently retain a stale live observation
        # or flatten it to the current root. All original simultaneous/unknown
        # scope obligations remain open at their original strength.
        require(not any(native.observed=='LIVE' and native.bound!=row.bound for native in packet.observed),
                'ROOT_CAPTURE_OTHER_LIVE_OWNED_DESCRIPTOR_ROSTER_UNAVAILABLE')
        source=seed['provenance']['current_source']
        controller=self._controller(row,physical,process,source,seed['provenance']['authority']['plan'],
                                    seed['provenance']['running_event'])
        facts=tuple(replace(fact,**physical['native_fields']) if fact.retained==row.bound else fact for fact in packet.facts)
        interim=replace(packet,facts=facts)
        classifier=S.ScopedRunLedgerKernel(owner.core)
        initial=tuple(replace(native,observed='UNKNOWN') if native.bound==row.bound else native for native in interim.observed)
        root_packet=replace(interim,observed=initial)
        decision=classifier.classify(root_packet)
        # No Python classification or static READY result is invented.
        require(decision.status=='LIVE','ROOT_CAPTURE_ACTUAL_NAMESPACE_NATIVE_CLASSIFICATION_REFUSED')
        observed=tuple(replace(native,actual_unit=physical['native_fields']['actual_unit'],
            cgroup=physical['native_fields']['cgroup'],invocation=physical['native_fields']['invocation'],observed=decision.status)
            if native.bound==row.bound else native for native in initial)
        final=replace(root_packet,observed=observed)
        current={'packet':final,'controller':controller,'crosswalk':material['crosswalk'],
                 'authority_snapshot':material['authority_snapshot']}
        # Full source and protected-state guard is retained. Native input/source
        # projection correspondence remains a required proof; source text or
        # equality alone cannot close that obligation.
        return current,{'owner_state':current_state,'state_correspondence':correspondence,
            'seed_event':event,'physical':physical,'process':process_raw,
            'native_classification':decision,'original_request':self.peer.observation()}
    def complete_native_material(self):
        from .protected_root_worker import RootWorkerIntake
        material,provenance=self._before_constructors() if type(self.owner) is RootWorkerIntake else self._current()
        self.material,self.provenance=material,provenance;self.owner._root_capture=self
        return material

def retain_root_native(owner,cause,material,observation):
    capture=getattr(owner,'_root_capture',None)
    require(type(capture) is RootControllerCapture and capture.owner is owner and capture.material is material,
            'ROOT_CAPTURE_REAL_FULL_NATIVE_PRODUCER_REQUIRED')
    require(owner.authority.kernel.root_controller(**material)==observation,
            'ROOT_CAPTURE_FULL_SELECTED_NATIVE_REDECISION_CHANGED')
    return owner.custody_journal.append(material['controller'].bound.operation.hex(),'EXECUTION_NATIVE',
        {'cause':cause,'material':material,'observation':observation,'provenance':capture.provenance})
