"""Actual early-lease scoped-history producer; every DTO remains data.

All old rows and scopes remain immutable. Original current Roots/typed absent
PRIME are observed from the actual retained store, with the original explicit
owner genesis crosswalk. New work uses genuine current native operation/use;
historical completion uses genuine retained original effect/closure witnesses.
The selected complete native kernels, machine floors, source/custody and durable
journals are all necessary. Missing correspondence retains obligations.
"""
from __future__ import annotations
from dataclasses import fields,replace
from pathlib import Path
import hashlib,importlib,os,socket,struct,subprocess,threading,uuid
from . import resource_scoped_run_ledger as S
from .protected_resource_runtime import (ProtectedResourcePrincipal,ProtectedAdmission,RunContext,RunBinding,
    RunRequest,RunRow,RunObservation,PhysicalFacts,empty_binding,operation_bytes,private,kernel_bytes,
    identity_record,canonical,exact,digest,require,ResourceProducerRefusal,lossless_data,DOMAIN)
from .protected_scoped_resource_service import ScopedRunLedgerService,ScopedSnapshot,packet_before,packet_after,snapshot_record
from .protected_scoped_observation_journal import ScopedObservationJournal
from .protected_scoped_supervisor_v3 import OwnedSupervisorV3
from .resource_actor_admission import ActorAdmissionKernel,ActorNativeObservation,ActorCapability
from .resource_actor_credentials import wait_observation,send_committed_ack
from .resource_actor_execution import ActorExecutionKernel,ActorExecutionCrosswalk


def _id(value):
    require(type(value) is str,'SCOPED_SOURCE_IDENTITY_REQUIRED')
    raw=bytes.fromhex(value);require(raw and raw.hex()==value,'SCOPED_SOURCE_IDENTITY_NONCANONICAL');return raw


def _decimal(raw):
    require(type(raw) is bytes and raw and all(b'0'[0]<=byte<=b'9'[0] for byte in raw),
            'SCOPED_ACTUAL_PROC_DECIMAL_INVALID')
    value=0
    for digit in raw:value=value*10+digit-b'0'[0]
    return value


def _hex(raw):
    require(type(raw) is bytes and raw,'SCOPED_ACTUAL_PROC_HEX_ABSENT')
    # Complete observed bytes, no host decimal digit policy or magnitude cap.
    value=0
    for digit in raw:
        if b'0'[0]<=digit<=b'9'[0]:item=digit-b'0'[0]
        elif b'a'[0]<=digit<=b'f'[0]:item=digit-b'a'[0]+10
        elif b'A'[0]<=digit<=b'F'[0]:item=digit-b'A'[0]+10
        else:raise ResourceProducerRefusal('SCOPED_ACTUAL_PROC_HEX_INVALID')
        value=value*16+item
    return value


def attach_scoped_resource(lease,gate,store,core):
    require(getattr(lease,'resource_principal',None) is None,'SCOPED_STARTUP_ALREADY_ATTACHED')
    selected=Path(lease.spec['runtime']['resource_scoped_producer'])
    require(selected==gate.root/'authority/resource/run-scoped-config-v1.json' and selected in lease.allowed,
            'SCOPED_EXACT_EARLY_SELECTED_PRODUCER_REQUIRED')
    principal=ProtectedScopedResourcePrincipal(lease,gate,store,core)
    lease.resource_principal=principal;return principal


class ProtectedScopedResourcePrincipal(ProtectedResourcePrincipal):
    def __init__(self,lease,gate,store,core):
        # Reads the genuine original producer/service/journal first. It neither
        # launches/reconciles nor changes any historical API or row semantics.
        super().__init__(lease,gate,store,core)
        self.historical_service=self.service
        self.scoped_service=ScopedRunLedgerService(lease,gate,core,self.historical_service)
        self.scoped_kernel=self.scoped_service.kernel;self.actor_kernel=ActorAdmissionKernel(core)
        self.execution_kernel=ActorExecutionKernel(core)
        self.observations=ScopedObservationJournal(self);self.planned={};self.actor_slots={}
        self.launch_identity=identity_record(self.journal.path.lstat())
        self.scoped_service.attach(self)
        require(self.cfg['helper']==str(Path(lease.spec['runtime']['tools']['resource_supervisor_v3']))
            and Path(self.cfg['helper']) in lease.allowed,'SCOPED_SELECTED_V3_HELPER_ENVELOPE_REQUIRED')
        self.service=self.scoped_service
        self.intact()
    def intact(self):
        # During original construction, no scoped members have been attached.
        super().intact()
        if hasattr(self,'scoped_service'):self.scoped_service.intact()
        if hasattr(self,'launch_identity'):
            require(identity_record(self.journal.path.lstat())==self.launch_identity,
                'SCOPED_LAUNCH_DATABASE_REPLACED')
    def sync_launch_journal(self,event):
        # SQLite FULL commit remains necessary. Synchronize the complete actual
        # database, any live journal/WAL files and its directory before an ACK
        # or externally visible launch/GO. Missing/replaced files never recreate.
        self.intact();self.journal.load()
        require(event in self.journal.events,'SCOPED_DURABLE_LAUNCH_EVENT_NOT_RETAINED')
        for path in (self.journal.path,Path(str(self.journal.path)+'-journal'),
                     Path(str(self.journal.path)+'-wal'),Path(str(self.journal.path)+'-shm')):
            if path!=self.journal.path and not os.path.lexists(path):continue
            private(path);fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
            try:
                if path==self.journal.path:
                    require(identity_record(os.fstat(fd))==self.launch_identity,
                        'SCOPED_DURABLE_LAUNCH_DATABASE_REPLACED')
                os.fsync(fd)
            finally:os.close(fd)
        directory=os.open(self.journal.path.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
        try:os.fsync(directory)
        finally:os.close(directory)
        self.intact();self.journal.load()
        require(event in self.journal.events,'SCOPED_DURABLE_LAUNCH_PREFIX_CHANGED')
    def current_snapshot(self):
        if not hasattr(self,'scoped_service'):return super().current_snapshot()
        return self.scoped_service.snapshot()
    def bind_operation_principal(self,principal):
        from .protected_operations import CanonicalOperationPrincipal
        require(type(principal) is CanonicalOperationPrincipal and principal.lease is self.lease
            and principal.gate is self.gate,'SCOPED_ACTUAL_CANONICAL_PRINCIPAL_REQUIRED')
        require(self.operation_principal is None or self.operation_principal is principal,
                'SCOPED_CANONICAL_PRINCIPAL_ALREADY_BOUND');self.operation_principal=principal
    def _context(self,before):
        self.intact();universe=self.gate.universe.read();entry=universe['record']
        genesis=self.store.get_meta('protectedStoreGenesis');store_id=self.store.get_meta('finalizationStoreId')
        require(genesis==self.lease.genesis['store']['identity'] and type(genesis) is str and type(store_id) is str and store_id,
                'SCOPED_ACTUAL_PROTECTED_STORE_IDENTITIES_CHANGED')
        # The store is under the exact preconstruction lock. Its entire ordered
        # Root roster is retained, including no-PRIME/nonempty accepted states.
        with self.store._lock:
            roots=self.store.roots();prime=self.store.prime()
        owner=None
        if prime is None:
            owner=self.cfg.get('store_genesis_context')
            require(type(owner) is dict and set(owner)=={'schema','installation_id','store_genesis',
                'finalization_store_id','universe_genesis_sha256','universe_id','instance_id','roots','prime'}
                and owner['schema']=='worldline.owner-provisioned-empty-store-resource-context-v1'
                and owner['installation_id']==self.lease.spec['installation_id']
                and owner['store_genesis']==genesis and owner['finalization_store_id']==store_id
                and owner['universe_genesis_sha256']==self.gate.universe.genesis_sha256
                and owner['universe_id']==universe['universe_id'] and owner['roots']==[] and owner['prime'] is None,
                'SCOPED_AUTHENTIC_ORIGINAL_GENESIS_CROSSWALK_REQUIRED')
            instance=owner['instance_id'];require(instance==entry['prime_worldline_id'],
                'SCOPED_ACTUAL_EMPTY_PRIME_UNIVERSE_CROSSWALK_CHANGED')
            prime_id=None;prime_record=None
        else:
            actual=uuid.UUID(prime.instance_id);require(str(actual)==prime.instance_id,'SCOPED_ACTUAL_PRIME_ID_INVALID')
            instance=hashlib.sha256(b'COSMOGONY-worldline-instance-v1\0'+actual.bytes).hexdigest()
            require(instance==entry['prime_worldline_id'] and self.gate.config['managed_observation'] is not None
                and instance==self.gate.config['managed_observation']['worldline_instance_id'],
                'SCOPED_ACTUAL_PRIME_UNIVERSE_BINDING_CHANGED')
            prime_id=actual.bytes;prime_record=prime.record()
        host=kernel_bytes('/etc/machine-id').removesuffix(b'\n')
        boot=kernel_bytes('/proc/sys/kernel/random/boot_id').removesuffix(b'\n')
        require(host and boot,'SCOPED_ACTUAL_MACHINE_BOOT_ABSENT')
        catalogue=S.restore(self.scoped_service.cfg['catalogue'])
        require(type(catalogue) is dict and set(catalogue)=={'schema','entries'} and
            catalogue['schema']=='worldline.protected-physical-catalogue-v1' and type(catalogue['entries']) is tuple,
            'SCOPED_COMPLETE_OWNER_PHYSICAL_CATALOGUE_REQUIRED')
        candidates=[]
        for physical in catalogue['entries']:
            require(type(physical) is dict and set(physical)=={'scope_policy','scope_resource','scope_unit','key',
                'numerator','denominator','capacity','capacity_source','costs','role'},
                'SCOPED_PHYSICAL_CATALOGUE_ENTRY_CHANGED')
            if physical['scope_policy']==_id(self.gate.config['policy_id']) and physical['scope_resource']==_id(entry['policy']['resource_id']):
                candidates.append(physical)
        require(candidates and all(item['scope_unit']==candidates[0]['scope_unit'] for item in candidates),
                'SCOPED_ACTUAL_CURRENT_UNIT_CROSSWALK_UNAVAILABLE')
        scope=RunContext(universe=_id(universe['universe_id']),policy=_id(self.gate.config['policy_id']),
            resource=_id(entry['policy']['resource_id']),unit=candidates[0]['scope_unit'],instance=_id(instance),
            host=host,boot=boot,authority=_id(entry['policy']['authority_id']),policy_epoch=entry['policy_epoch'])
        root_raw=canonical(lossless_data({'store_genesis':genesis,'store_id':store_id,'roots':roots,'prime':prime_record}))
        catalogue_raw=canonical(self.scoped_service.cfg['catalogue'])
        source={'universe':universe,'gate_config_raw':self.gate.config_raw,'issuer_head':self.gate.issuer.head(),
            'actual_store_genesis':genesis,'actual_store_id':store_id,'actual_roots':roots,'actual_prime':prime_record,
            'original_owner_genesis':owner,'host_raw':host,'boot_raw':boot,'catalogue_raw':catalogue_raw,
            'scoped_before':snapshot_record(before),'launch_prefix':self.journal.events,
            'installation':self.lease.spec,'store_lock_fd_info':kernel_bytes('/proc/self/fdinfo/'+str(self.lease.store_lock_fd))}
        cause=hashlib.sha256(canonical(S.record(source))).digest()
        requester=hashlib.sha256(canonical(self.binding)).digest()
        receipt=hashlib.sha256(b'WORLDLINE-scoped-current-source\0'+canonical(S.record(source))).digest()
        current=S.CurrentObservation(scope=scope,resource_epoch=before.state.resource_epoch,
            universe_head=_id(universe['event_head']),ledger_head=before.state.ledger_head,
            history_head=before.state.history_head,physical_head=hashlib.sha256(catalogue_raw).digest(),
            store_genesis=genesis.encode('utf-8'),store_id=store_id.encode('utf-8'),root_head=hashlib.sha256(root_raw).digest(),
            prime=prime_id,root_count=len(roots),cause=cause,requester=requester,receipt=receipt,
            catalogue_head=hashlib.sha256(catalogue_raw).digest(),observation_head=cause)
        return current,source,catalogue
    def current_context(self):
        with self.gate.mutex,self.order:
            before=self.current_snapshot();current,source,_catalogue=self._context(before)
            return current.scope,current.resource_epoch,current.universe_head,current.ledger_head,source
    def _request(self,before,reservation=None):
        row=next((row for row in before.rows if row.bound.reservation==reservation),None)
        bound=row.bound if row else empty_binding();scope=row.scope if row else before.state.current
        identity=hashlib.sha256(canonical(snapshot_record(before))).digest()
        return RunRequest(kind='UNKNOWN_OPERATION',scope=scope,expected_epoch=before.state.resource_epoch,
            expected_ledger_head=before.state.ledger_head,request_id=identity,reservation=bound.reservation,
            operation_id=bound.operation,requester=bound.owner,bound=bound,new_row=row)
    def _inspect(self,before,current,observed,facts,request=None):
        request=request or self._request(before)
        intent=S.ScopedIntent(kind='ORDINARY',original=request,expected_epoch=before.state.resource_epoch,
            expected_ledger_head=before.state.ledger_head,request_id=request.request_id,
            cause=current.cause,requester=current.requester,receipt=current.receipt)
        return S.ScopedPacket(before=before.state,history=before.history,rows=before.rows,
            projection=before.projection,buckets=before.buckets,proposed=before.state,proposed_history=before.history,
            proposed_rows=before.rows,proposed_projection=before.projection,proposed_buckets=before.buckets,
            actual_buckets=before.buckets,observed=observed,facts=facts,current=current,request=intent)
    def _retained_closed(self,row,blank):
        self.observations.load()
        for event in reversed(self.observations.events):
            if event['cause']!='CLOSED_NATIVE_WITNESS' or event['reservation']!=row.bound.reservation.hex():continue
            body=S.restore(event['payload']);packet=body['packet'];native=body['native']
            require(type(packet) is S.ScopedPacket and type(native) is S.ScopedNativeDecision and
                packet.request.original.bound==row.bound and body['original_row'].bound==row.bound and
                body['original_row'].scope==row.scope and body['original_row'].actual_unit==row.actual_unit
                and body['original_row'].cgroup==row.cgroup and body['original_row'].invocation==row.invocation,
                'SCOPED_RETAINED_CLOSED_FULL_ORIGIN_CHANGED')
            require(body['owned_closed'] and body['launch_prefix']==body['source']['launch_prefix'] and
                body['source']['kernel']['closed']==body['owned_closed'],
                'SCOPED_RETAINED_REAL_CLOSED_SOURCE_MISSING')
            actual=self.scoped_kernel.classify(packet)
            require(actual==native and actual.status=='REAPED','SCOPED_RETAINED_REAL_NATIVE_CLOSURE_REFUSED')
            indexes=[i for i,item in enumerate(packet.rows) if item.bound==row.bound]
            require(len(indexes)==1,'SCOPED_RETAINED_CLOSED_MEMBERSHIP_CHANGED')
            old=packet.facts[indexes[0]]
            # Only the independently observed current header changes. Every
            # actual earlier closure/ownership/syscall fact is retained intact.
            # The current whole native ledger/classifier redecides disposition.
            physical=replace(old,current=blank.current,current_epoch=blank.current_epoch,
                current_universe_head=blank.current_universe_head,current_ledger_head=blank.current_ledger_head,
                observation_head=hashlib.sha256(canonical(S.record({'current':blank,'witness':event}))).digest())
            return physical,{'schema':'worldline.genuine-retained-closed-projection-v1','witness':event,
                             'actual_native_redecision':S.record(actual),'original_physical':S.record(old)}
        return blank,{'schema':'worldline.missing-owned-closed-witness-v1','retained':'UNKNOWN'}
    def _capture(self,before,current):
        self.journal.load();facts=[];raw=[]
        for row in before.rows:
            blank=self._blank(current.scope,current.resource_epoch,current.universe_head,current.ledger_head,row,current.observation_head)
            physical,source=super()._facts(row,blank,current.observation_head.hex())
            if row.bound.reservation.hex() not in self.slots and physical.phase=='UNAVAILABLE':
                physical,historical=self._retained_closed(row,physical);source['historical']=historical
            facts.append(physical);raw.append(source)
        initial=tuple(RunObservation(scope=row.scope,resource_epoch=before.state.resource_epoch,bound=row.bound,
            actual_unit=row.actual_unit,cgroup=row.cgroup,invocation=row.invocation,
            observation_head=fact.observation_head,observed='UNKNOWN') for row,fact in zip(before.rows,facts))
        observed=[];decisions=[]
        for row,fact in zip(before.rows,facts):
            packet=self._inspect(before,current,initial,tuple(facts),self._request(before,row.bound.reservation))
            native=self.scoped_kernel.classify(packet);kind=native.status;effect=kind in ('LIVE','REAPED')
            observed.append(RunObservation(scope=row.scope,resource_epoch=before.state.resource_epoch,bound=row.bound,
                actual_unit=fact.actual_unit if effect else row.actual_unit,cgroup=fact.cgroup if effect else row.cgroup,
                invocation=fact.invocation if effect else row.invocation,observation_head=fact.observation_head,observed=kind))
            decisions.append(native)
        observed=tuple(observed);facts=tuple(facts);raw=tuple(raw);decisions=tuple(decisions)
        for index,row in enumerate(before.rows):
            slot=self.slots.get(row.bound.reservation.hex())
            if decisions[index].status=='REAPED' and type(slot) is OwnedSupervisorV3:
                self._retain_owned_closed(before,current,observed,facts,raw,decisions,index,slot)
        return observed,facts,raw,decisions
    def _retain_owned_closed(self,before,current,observed,facts,raw,decisions,index,slot):
        row=before.rows[index]
        require(slot.principal is self and self.slots.get(row.bound.reservation.hex()) is slot
            and slot.closed is not None and slot.closed_event is not None and not slot.failed
            and slot.pidfd_state(slot.namespace_pidfd)==b'PIDFD_TERMINAL'
            and slot.pidfd_state(slot.helper_pidfd)==b'PIDFD_TERMINAL',
            'SCOPED_GENUINE_FULL_CLOSED_KERNEL_OWNERSHIP_REQUIRED')
        source=dict(raw[index]);source['launch_prefix']=self.journal.events
        require(source['kernel']['closed']==slot.closed and decisions[index].status=='REAPED',
            'SCOPED_FULL_ACTUAL_NATIVE_CLOSED_SOURCE_CHANGED')
        packet=self._inspect(before,current,observed,facts,self._request(before,row.bound.reservation))
        native=self.scoped_kernel.classify(packet)
        require(decisions[index].status=='REAPED' and native.status=='REAPED',
            'SCOPED_FULL_CLOSED_NATIVE_REDECISION_CHANGED')
        self.observations.load()
        for event in self.observations.events:
            if event['cause']=='CLOSED_NATIVE_WITNESS' and event['reservation']==row.bound.reservation.hex():
                old=S.restore(event['payload'])
                if old['owned_closed']==slot.closed and old['original_row'].bound==row.bound:
                    require(self.scoped_kernel.classify(old['packet'])==old['native']
                        and old['native'].status=='REAPED','SCOPED_PRIOR_FULL_CLOSED_NATIVE_CHANGED')
                    return event
        # Real ECHILD/CLOSED + owned wait/cgroup facts, original immutable row,
        # complete launch/source/issuer/native prefix are retained before any
        # historical release. The HMAC/kind alone is never a terminal verdict.
        body={'packet':packet,'native':native,'original_row':row,'owned_closed':slot.closed,
            'owned_closed_event':slot.closed_event,'launch_prefix':self.journal.events,'source':source,
            'current_source':self._context(before)[1],'issuer_head':self.gate.issuer.head(),
            'installation':self.lease.spec,'committed_history':self.scoped_service.committed_history()}
        return self.observations.append('CLOSED_NATIVE_WITNESS',row.bound.reservation.hex(),body)
    def _projection(self,rows,old,catalogue,current):
        projected=[]
        for index,row in enumerate(rows):
            if index<len(old.projection):
                origin=old.projection[index]
                require(origin.bound==row.bound and origin.origin==row.scope,'SCOPED_IMMUTABLE_PROJECTION_ORIGIN_CHANGED')
            else:
                matching=[entry for entry in catalogue['entries'] if entry['scope_policy']==row.scope.policy
                    and entry['scope_resource']==row.scope.resource and entry['scope_unit']==row.scope.unit]
                require(len(matching)==1,'SCOPED_GENUINE_PHYSICAL_ROW_CROSSWALK_REQUIRED');entry=matching[0]
                origin=S.PhysicalProjection(key=entry['key'],bound=row.bound,origin=row.scope,
                    catalogue_head=current.catalogue_head,numerator=entry['numerator'],denominator=entry['denominator'],amount=0)
            amount=0 if row.state=='RELEASED' else row.amount
            if row.kind=='HELD_CAPACITY' and row.observed_usage is not None:amount=max(amount,row.observed_usage)
            # Proposal arithmetic only: the native exact remainder/equality,
            # original signed-zero/padding validity and full conservation decide.
            denominator=origin.denominator
            projected.append(replace(origin,amount=(amount*origin.numerator//denominator if denominator else 0)))
        return tuple(projected)
    def _buckets(self,rows,projection,old,catalogue,current):
        keys=[bucket.key for bucket in old.buckets]
        for entry in catalogue['entries']:
            if entry['key'] not in keys:keys.append(entry['key'])
        result=[]
        for key in keys:
            matching=[entry for entry in catalogue['entries'] if entry['key']==key]
            require(matching and all((entry['capacity'],entry['capacity_source'])==
                (matching[0]['capacity'],matching[0]['capacity_source']) for entry in matching),
                'SCOPED_WHOLE_RETAINED_PHYSICAL_CAPACITY_SOURCE_REQUIRED')
            held=charged=0
            for row,physical in zip(rows,projection):
                if row.parent is not None or row.state=='RELEASED' or physical.key!=key:continue
                if row.kind=='HELD_CAPACITY':held+=physical.amount
                else:charged+=physical.amount
            result.append(S.PhysicalBucket(key=key,capacity=matching[0]['capacity'],held_total=held,charged_total=charged,
                capacity_source=matching[0]['capacity_source'],catalogue_head=current.catalogue_head,
                observation_head=hashlib.sha256(canonical(S.record({'key':key,'catalogue':catalogue}))).digest()))
        return tuple(result)
    def _propose_packet(self,before,current,source,catalogue,request,rows,*,history=None,advance=False,material=None):
        observed,facts,raw,classification=self._capture(before,current)
        projected=self._projection(rows,before,catalogue,current)
        buckets=self._buckets(rows,projected,before,catalogue,current)
        epoch=before.state.resource_epoch+1
        intent=S.ScopedIntent(kind='ADVANCE_CONTEXT' if advance else 'ORDINARY',original=request,
            expected_epoch=before.state.resource_epoch,expected_ledger_head=before.state.ledger_head,
            request_id=request.request_id,cause=current.cause if advance else request.operation_id,
            requester=current.requester if advance else request.requester,receipt=current.receipt)
        frames=history or before.history
        proposed=replace(before.state,current=current.scope if advance else before.state.current,resource_epoch=epoch,
            universe_head=current.universe_head if advance else before.state.universe_head,
            history_head=current.history_head if advance else before.state.history_head,
            physical_head=current.physical_head if advance else before.state.physical_head,
            ledger_head=hashlib.sha256(canonical(S.record({'before':snapshot_record(before),'intent':intent,
                'rows':rows,'projection':projected,'buckets':buckets,'history':frames}))).digest())
        packet=S.ScopedPacket(before=before.state,history=before.history,rows=before.rows,projection=before.projection,
            buckets=before.buckets,proposed=proposed,proposed_history=frames,proposed_rows=rows,
            proposed_projection=projected,proposed_buckets=buckets,actual_buckets=buckets,observed=observed,
            facts=facts,current=current,request=intent)
        custody={'packet':S.record(packet),'current_source':source,'physical_source':raw,
            'physical_native':classification,'canonical_material':material,'original_issuer_head':self.gate.issuer.head(),
            'source_envelope':self.lease.spec,'launch_prefix':self.journal.events}
        self.planned[request.request_id]={'packet':packet,'custody':custody}
        return packet
    def capture_commit(self,packet):
        # No arbitrary caller packet/Boolean supplies authentic observations.
        retained=self.planned.get(packet.request.request_id)
        require(retained is not None and retained['packet'] is packet,
                'SCOPED_ACTUAL_OWNED_PROPOSAL_REQUIRED')
        current,source,_catalogue=self._context(packet_before(packet))
        previous=retained['custody']['current_source']
        for name in ('universe','gate_config_raw','actual_store_genesis','actual_store_id','actual_roots','actual_prime','host_raw','boot_raw','catalogue_raw'):
            require(source[name]==previous[name],'SCOPED_ACTUAL_SOURCE_CHANGED_BEFORE_COMMIT')
        self.lease.loaded();self.intact()
        return retained['custody']
    def reconcile_context(self):
        with self.gate.mutex,self.order:
            before=self.current_snapshot();current,source,catalogue=self._context(before);last=before.history[-1]
            if (current.scope,current.universe_head,current.root_head,current.prime,current.catalogue_head,current.physical_head)==(
                before.state.current,before.state.universe_head,last.root_head,last.prime,last.catalogue_head,before.state.physical_head):
                return before
            epoch=before.state.resource_epoch+1
            frame=S.ScopeFrame(scope=current.scope,first_epoch=epoch,universe_head=current.universe_head,
                frame_head=None,prior_frame=before.state.history_head,store_genesis=current.store_genesis,
                store_id=current.store_id,root_head=current.root_head,prime=current.prime,root_count=current.root_count,
                cause=current.cause,requester=current.requester,receipt=current.receipt,
                catalogue_head=current.catalogue_head,observation_head=current.observation_head)
            head=hashlib.sha256(canonical(S.record(frame))).digest();frame=replace(frame,frame_head=head)
            current=replace(current,history_head=head)
            request=replace(self._request(before),request_id=hashlib.sha256(canonical(S.record({'frame':frame,'before':before.state}))).digest())
            packet=self._propose_packet(before,current,source,catalogue,request,before.rows,
                history=(*before.history,frame),advance=True)
            self.scoped_service.commit(self,packet);return self.current_snapshot()
    def _selected_cost(self,key,scope,catalogue):
        matches=[entry for entry in catalogue['entries'] if entry['scope_policy']==scope.policy
            and entry['scope_resource']==scope.resource and entry['scope_unit']==scope.unit]
        require(len(matches)==1 and type(matches[0]['costs']) is dict and key in matches[0]['costs'],
                'SCOPED_AUTHENTIC_CURRENT_OPERATION_COST_UNAVAILABLE')
        cost=matches[0]['costs'][key]
        require(type(cost) is dict and set(cost)=={'kind','amount'},'SCOPED_FULL_OWNER_COST_SCHEMA_CHANGED')
        return cost
    def intent_for_operation(self,original_request,operation_id,transaction_record):
        from .client_peer import RequestPeer
        from .operation_capture import archive
        with self.gate.mutex,self.order:
            self.intact();require(type(original_request) is RequestPeer and self.operation_principal is not None,
                'SCOPED_GENUINE_ORIGINAL_REQUEST_AND_PRINCIPAL_REQUIRED')
            before=self.reconcile_context();current,_source,catalogue=self._context(before)
            material=self.operation_principal.resource_request_material(original_request,operation_id,transaction_record)
            require(type(material) is dict and set(material)=={'requester','capability','grant_use','workload','payload','provenance','parent','cost_key'},
                'SCOPED_AUTHENTIC_OPERATION_COST_MATERIAL_REQUIRED')
            cost=self._selected_cost(material['cost_key'],current.scope,catalogue);operation=operation_bytes(operation_id)
            seed=canonical(S.record({'operation':operation,'original_request':original_request.observation(),
                'transaction_full_raw':archive(transaction_record),'cost':cost,'current':current,
                'credential_join':self.credential_join(original_request)}))
            reservation=hashlib.sha256(DOMAIN+b'scoped-reservation\0'+seed).digest()
            bound=RunBinding(reservation=reservation,operation=operation,owner=material['requester'],
                workload=material['workload'],universe_head=current.universe_head,capability=material['capability'],
                grant_use=material['grant_use'],payload=material['payload'],provenance=material['provenance'],resource_epoch=current.resource_epoch)
            row=RunRow(scope=current.scope,bound=bound,parent=material['parent'],kind=cost['kind'],state='RESERVED',amount=cost['amount'],
                observed_usage=None,planned_unit=None,actual_unit=None,cgroup=None,invocation=None)
            return RunRequest(kind='RESERVE',scope=current.scope,expected_epoch=current.resource_epoch,
                expected_ledger_head=current.ledger_head,request_id=hashlib.sha256(DOMAIN+b'scoped-request\0'+seed).digest(),
                reservation=reservation,operation_id=operation,requester=material['requester'],bound=bound,new_row=row)
    def reserve_packet(self,intent):
        with self.gate.mutex,self.order:
            require(type(intent) is RunRequest and intent.kind=='RESERVE' and type(intent.new_row) is RunRow,
                    'SCOPED_COMPLETE_RESERVATION_INTENT_REQUIRED')
            before=self.current_snapshot();current,source,catalogue=self._context(before)
            return self._propose_packet(before,current,source,catalogue,intent,(*before.rows,intent.new_row))
    def submit_bound(self,pending,packet,original_request):
        with self.gate.mutex,self.order:
            require(type(packet) is S.ScopedPacket and self.operation_principal is not None,
                    'SCOPED_ACTUAL_NATIVE_OPERATION_PRINCIPAL_REQUIRED')
            request=packet.request.original
            replay=self.scoped_service.recover(self,packet)
            if replay.get('status')!='NOT_COMMITTED':
                if request.kind=='RESERVE':self._restore_prepared(packet,replay)
                return replay
            self.journal.load()
            retained=self.journal.rows.get(request.reservation.hex())
            captured=(self.operation_principal.resource_binding(pending,original_request) if request.kind=='RESERVE' else
                self.operation_principal.resource_lifecycle_binding(pending,original_request,request,
                    retained['events'] if retained else []))
            require(captured['scope']==S.L.dto_record(request.scope) and captured['bound']==S.L.dto_record(request.bound)
                and captured['request']==S.L.dto_record(request) and
                pending is self.operation_principal.pending_for_operation(request.operation_id),
                'SCOPED_COMPLETE_ACTUAL_OPERATION_BINDING_CHANGED')
            owned=self.planned.get(packet.request.request_id)
            if owned is not None:
                owned['custody']['canonical_material']=captured
                if request.kind=='RESERVE':
                    owned['custody']['reserve_origin']={'pending':exact(canonical(pending)),
                        'original_request':original_request.observation(),
                        'credential_join':self.credential_join(original_request)}
            reply=self.scoped_service.commit(self,packet)
            if request.kind=='RESERVE':
                self._restore_prepared(packet,reply)
                self.actor_slots.setdefault(request.reservation,{'original_request':original_request,'pending':pending})
            return reply
    def _restore_prepared(self,packet,reply):
        # A crash between the native scoped commit and PREPARED may restore
        # only that exact authenticated original event. No fresh grant, peer or
        # current pending record substitutes for the retained source capture.
        request=packet.request.original
        selected=[event for event in self.scoped_service.committed_history()
            if event['packet']==S.record(packet)]
        require(len(selected)==1,'SCOPED_EXACT_RESERVATION_COMMIT_REQUIRED')
        source=S.restore(selected[0]['source']);origin=source.get('reserve_origin')
        require(type(origin) is dict and set(origin)=={'pending','original_request','credential_join'},
            'SCOPED_RETAINED_COMPLETE_RESERVE_ORIGIN_UNAVAILABLE')
        payload={'row':S.L.dto_record(request.new_row),'native_result':reply,'pending':origin['pending'],
            'original_request':origin['original_request'],'operation_binding':source['canonical_material']}
        if origin['credential_join'] is not None:payload['credential_join']=origin['credential_join']
        self.journal.load();old=self.journal.rows.get(request.reservation.hex())
        if old is None:event=self.journal.append('PREPARED',request.reservation.hex(),payload)
        else:
            require(old['prepared']['payload']==payload,'SCOPED_COMMITTED_PREPARATION_REPLAY_CHANGED')
            event=old['prepared']
        self.sync_launch_journal(event)
    def _lifecycle_packet_record(self,original_record,reservation,kind,changes):
        self.intact();self.journal.load();before=self.reconcile_context()
        old=next((row for row in before.rows if row.bound.reservation==reservation),None)
        retained=self.journal.rows.get(reservation.hex())
        require(old is not None and retained is not None and retained['prepared']['payload']['original_request']==original_record,
                'SCOPED_ORIGINAL_LIFECYCLE_CUSTODY_CHANGED')
        require(set(changes)<={'state','planned_unit','actual_unit','cgroup','invocation'},'SCOPED_IMMUTABLE_ROW_CHANGE_REFUSED')
        row=replace(old,**changes);rows=tuple(row if item.bound==old.bound else item for item in before.rows)
        current,source,catalogue=self._context(before)
        seed=canonical(S.record({'kind':kind,'before':snapshot_record(before),'row':row,'original_request':original_record,
            'launch_prefix':retained['events']}))
        request=RunRequest(kind=kind,scope=old.scope,expected_epoch=before.state.resource_epoch,
            expected_ledger_head=before.state.ledger_head,request_id=hashlib.sha256(DOMAIN+b'scoped-lifecycle\0'+seed).digest(),
            reservation=reservation,operation_id=old.bound.operation,requester=old.bound.owner,bound=old.bound,new_row=None)
        return self._propose_packet(before,current,source,catalogue,request,rows)
    def _committed_material(self,packet,reply):
        # Only transport the actual full committed event. Neither a DTO nor a
        # shortened reply can manufacture a packet, native result or closure.
        self.intact()
        require(type(packet) is S.ScopedPacket and type(reply) is dict,
            'SCOPED_COMPLETE_COMMITTED_MATERIAL_REQUIRED')
        history=self.scoped_service.committed_history()
        selected=[event for event in history if event['packet']==S.record(packet)]
        require(len(selected)==1,'SCOPED_EXACT_COMMITTED_MATERIAL_MEMBERSHIP_REQUIRED')
        native=self.scoped_kernel.decide(packet)
        require(native.status=='READY' and S.restore(selected[0]['native'])==native,
            'SCOPED_COMPLETE_COMMITTED_NATIVE_MATERIAL_CHANGED')
        actual=self.scoped_service.recover(self,packet)
        require(actual==reply and actual.get('status')=='READY',
            'SCOPED_COMPLETE_COMMITTED_REPLY_MATERIAL_CHANGED')
        return {'packet':packet,'reply':reply,'native':native,
            'committed_event':selected[0],'complete_history':history}
    def _committed_terminal_material(self,operation,reservation):
        selected=self.committed_resource_history(operation,reservation)
        terminal=[event for event in selected if S.restore(event['packet']).request.original.kind in ('RELEASE_HOLD','CHARGE_BUDGET')]
        require(len(terminal)==1,'SCOPED_EXACT_COMMITTED_TERMINAL_MEMBERSHIP_REQUIRED')
        packet=S.restore(terminal[0]['packet'])
        reply=self._committed_terminal(operation,reservation)
        return self._committed_material(packet,reply)
    def _committed_terminal(self,operation,reservation):
        selected=self.committed_resource_history(operation,reservation)
        terminal=[event for event in selected if S.restore(event['packet']).request.original.kind in ('RELEASE_HOLD','CHARGE_BUDGET')]
        require(len(terminal)==1,'SCOPED_EXACT_COMMITTED_TERMINAL_MEMBERSHIP_REQUIRED')
        packet=S.restore(terminal[0]['packet']);reply=self.scoped_service.recover(self,packet)
        require(reply.get('status')!='NOT_COMMITTED','SCOPED_COMMITTED_TERMINAL_NOT_FOUND');return reply
    def settle_bound(self,pending,original_request,reservation):
        with self.gate.mutex,self.order:
            self.intact();before=self.reconcile_context()
            selected=[row for row in before.rows if row.bound.reservation==reservation]
            require(len(selected)==1,'SCOPED_COMPLETE_SETTLEMENT_MEMBERSHIP_REQUIRED');row=selected[0]
            if row.state in ('RELEASED','CHARGED'):return self._committed_terminal(row.bound.operation,reservation)
            current,_source,_catalogue=self._context(before);observed,_facts,_raw,_native=self._capture(before,current)
            kind=observed[before.rows.index(row)].observed
            def commit(action,changes):
                packet=self.lifecycle_packet(original_request,reservation,action,changes)
                return self.submit_bound(pending,packet,original_request)
            if kind=='REAPED':
                if row.state!='TERMINAL':commit('RECORD_TERMINAL',{'state':'TERMINAL'})
                return commit('RELEASE_HOLD' if row.kind=='HELD_CAPACITY' else 'CHARGE_BUDGET',
                    {'state':'RELEASED' if row.kind=='HELD_CAPACITY' else 'CHARGED'})
            if kind=='NEVER_LAUNCHED' and row.kind=='HELD_CAPACITY':return commit('RELEASE_HOLD',{'state':'RELEASED'})
            if kind=='UNKNOWN' and row.state in ('LAUNCH_INTENT','RUNNING','TERMINATING','SETTLEMENT_UNKNOWN'):
                return commit('RETAIN_UNCERTAIN',{'state':'SETTLEMENT_UNKNOWN'})
            raise ResourceProducerRefusal('SCOPED_CAPACITY_RETAINED_LIVE_OR_UNKNOWN')
    def settle_historical(self,principal,operation,reservation):
        with self.gate.mutex,self.order:
            self.intact();require(principal is self.operation_principal and principal.lease is self.lease
                and principal.gate is self.gate,'SCOPED_ACTUAL_HISTORICAL_CANONICAL_PRINCIPAL_REQUIRED')
            operation,reservation=operation_bytes(operation),operation_bytes(reservation)
            method=getattr(principal,'resource_scoped_historical_settlement',None)
            require(callable(method),'SCOPED_CANONICAL_HISTORICAL_ADAPTER_UNAVAILABLE')
            captured=method(operation,reservation)
            require(type(captured) is dict and {'original_request','scope','bound','native_use','event_id','effects',
                'receipts','causal','resource_packets'}<=set(captured),'SCOPED_FULL_AUTHENTIC_HISTORICAL_EFFECT_REQUIRED')
            self.journal.load();retained=self.journal.rows.get(reservation.hex())
            require(retained is not None and retained['prepared']['payload']['original_request']==captured['original_request'],
                'SCOPED_HISTORICAL_ORIGINAL_REQUEST_CHANGED')
            before=self.reconcile_context();selected=[row for row in before.rows if row.bound.reservation==reservation]
            require(len(selected)==1 and selected[0].bound.operation==operation
                and captured['scope']==S.L.dto_record(selected[0].scope) and captured['bound']==S.L.dto_record(selected[0].bound),
                'SCOPED_HISTORICAL_FULL_BINDING_CHANGED');row=selected[0]
            if row.state in ('RELEASED','CHARGED'):return self._committed_terminal_material(operation,reservation)
            current,_source,_catalogue=self._context(before);observed,_facts,_raw,_native=self._capture(before,current)
            kind=observed[before.rows.index(row)].observed
            def commit(action,changes):
                packet=self._lifecycle_packet_record(captured['original_request'],reservation,action,changes)
                request=packet.request.original;self.journal.load()
                method=getattr(principal,'resource_scoped_historical_lifecycle_binding',None)
                require(callable(method),'SCOPED_CANONICAL_HISTORICAL_LIFECYCLE_ADAPTER_UNAVAILABLE')
                binding=method(operation,reservation,request,
                    self.journal.rows[reservation.hex()]['events'])
                require(type(binding) is dict and {'scope','bound','request','native_use','event_id'}<=set(binding)
                    and binding['scope']==S.L.dto_record(request.scope) and binding['bound']==S.L.dto_record(request.bound)
                    and binding['request']==S.L.dto_record(request),'SCOPED_FULL_HISTORICAL_NATIVE_LIFECYCLE_CHANGED')
                self.planned[packet.request.request_id]['custody']['canonical_material']=binding
                reply=self.scoped_service.commit(self,packet)
                return self._committed_material(packet,reply)
            if kind=='REAPED':
                if row.state!='TERMINAL':commit('RECORD_TERMINAL',{'state':'TERMINAL'})
                return commit('RELEASE_HOLD' if row.kind=='HELD_CAPACITY' else 'CHARGE_BUDGET',
                    {'state':'RELEASED' if row.kind=='HELD_CAPACITY' else 'CHARGED'})
            if kind=='NEVER_LAUNCHED' and row.kind=='HELD_CAPACITY':return commit('RELEASE_HOLD',{'state':'RELEASED'})
            if kind=='UNKNOWN' and row.state in ('LAUNCH_INTENT','RUNNING','TERMINATING','SETTLEMENT_UNKNOWN'):
                return commit('RETAIN_UNCERTAIN',{'state':'SETTLEMENT_UNKNOWN'})
            raise ResourceProducerRefusal('SCOPED_HISTORICAL_CAPACITY_RETAINED_LIVE_OR_UNKNOWN')
    def resolve_historical(self,principal,operation,reservation,complete_owner_native_proof):
        with self.gate.mutex,self.order:
            self.intact();require(principal is self.operation_principal and principal.lease is self.lease
                and principal.gate is self.gate,'SCOPED_ACTUAL_OWNER_RESOLUTION_PRINCIPAL_REQUIRED')
            operation,reservation=operation_bytes(operation),operation_bytes(reservation)
            method=getattr(principal,'resource_scoped_owner_resolution_material',None)
            require(callable(method),'SCOPED_CANONICAL_OWNER_HISTORY_ADAPTER_UNAVAILABLE')
            captured=method(operation,complete_owner_native_proof)
            required={'operation','event_id','proof','original_request','original_capture','original_native_use',
                'scope','bound','packets','retained_resource_history','owner_event_id','owner_capture','owner_native_intent'}
            require(type(captured) is dict and required<=set(captured)
                and captured['proof']==complete_owner_native_proof,'SCOPED_FULL_REDECIDED_OWNER_DISPOSITION_REQUIRED')
            self.journal.load();retained=self.journal.rows.get(reservation.hex())
            require(retained is not None and retained['prepared']['payload']['original_request']==captured['original_request'],
                'SCOPED_OWNER_RESOLUTION_ORIGINAL_REQUEST_CHANGED')
            before=self.reconcile_context();selected=[row for row in before.rows if row.bound.reservation==reservation]
            require(len(selected)==1 and selected[0].bound.operation==operation
                and captured['scope']==S.L.dto_record(selected[0].scope) and captured['bound']==S.L.dto_record(selected[0].bound),
                'SCOPED_OWNER_RESOLUTION_ORIGINAL_FULL_BINDING_CHANGED');row=selected[0]
            actual=self.committed_resource_history(operation,reservation)
            require(tuple(captured['retained_resource_history'])==actual,
                'SCOPED_OWNER_RESOLUTION_COMPLETE_PROTECTED_RESOURCE_HISTORY_CHANGED')
            self.observations.append('OWNER_RESOLUTION_CAPTURE',reservation.hex(),{'owner_material':captured,
                'actual_complete_resource_history':actual,'original_row':row,'current_snapshot':snapshot_record(before)})
            if row.state in ('RELEASED','CHARGED'):return self._committed_terminal_material(operation,reservation)
            current,_source,_catalogue=self._context(before);observed,_facts,_raw,_native=self._capture(before,current)
            kind=observed[before.rows.index(row)].observed
            def commit(action,changes):
                packet=self._lifecycle_packet_record(captured['original_request'],reservation,action,changes)
                self.planned[packet.request.request_id]['custody']['canonical_material']=captured
                reply=self.scoped_service.commit(self,packet)
                return self._committed_material(packet,reply)
            if kind=='REAPED':
                if row.state!='TERMINAL':commit('RECORD_TERMINAL',{'state':'TERMINAL'})
                return commit('RELEASE_HOLD' if row.kind=='HELD_CAPACITY' else 'CHARGE_BUDGET',
                    {'state':'RELEASED' if row.kind=='HELD_CAPACITY' else 'CHARGED'})
            if kind=='NEVER_LAUNCHED' and row.kind=='HELD_CAPACITY':return commit('RELEASE_HOLD',{'state':'RELEASED'})
            # A Before mapping alone is not a resource release, and split or
            # unknown owned descendants remain charged/quarantined.
            raise ResourceProducerRefusal('SCOPED_OWNER_RESOLUTION_PHYSICAL_LIFECYCLE_UNKNOWN_OR_LIVE')
    def committed_resource_history(self,operation,reservation):
        operation,reservation=operation_bytes(operation),operation_bytes(reservation)
        return tuple(event for event in self.scoped_service.committed_history()
            if (S.restore(event['packet']).request.original.operation_id==operation and
                S.restore(event['packet']).request.original.reservation==reservation))
    def reconcile(self,controller):
        with self.gate.mutex,self.order:
            before=self.reconcile_context();current,source,_catalogue=self._context(before)
            observed,facts,raw,native=self._capture(before,current)
            packet=self._inspect(before,current,observed,facts);consistent=self.scoped_kernel.validate(packet)
            require(consistent.status=='CONSISTENT_SNAPSHOT','SCOPED_STARTUP_WHOLE_NATIVE_SNAPSHOT_REFUSED')
            self.controller=controller;controller.protected_resources=self
            controller.admission=ProtectedAdmission(self,controller.admission)
            event=self.observations.append('STARTUP_RECONCILED',None,{'packet':packet,'native':consistent,
                'source':source,'physical':raw,'classification':native,'released':()})
            self.startup_observation={'schema':'worldline.protected-scoped-startup-v1','event':event,'released':[]}
            return []
    def lifecycle_packet(self,original_request,reservation,kind,changes):
        from .client_peer import RequestPeer
        require(type(original_request) is RequestPeer,'SCOPED_ACTUAL_LIFECYCLE_REQUEST_PEER_REQUIRED')
        return self._lifecycle_packet_record(original_request.observation(),reservation,kind,changes)
    def machine_admission(self,reservation,policy,stage):
        from .admission import observe,ResourcePolicy
        from .resource_machine_evidence import observe_ledger,observe_policy
        with self.gate.mutex,self.order:
            self.intact();controller=getattr(self,'controller',None)
            require(controller is not None and controller.protected_resources is self
                and type(policy) is ResourcePolicy and stage in ('DISPATCH','GO'),
                'SCOPED_ACTUAL_ORIGINAL_MACHINE_POLICY_AND_CONTROLLER_REQUIRED')
            retained=self.actor_slots.get(reservation)
            require(retained is not None and self.operation_principal is not None,
                'SCOPED_AUTHENTIC_ORIGINAL_MACHINE_POLICY_SOURCE_REQUIRED')
            plan=self.operation_principal.resource_launch_material(retained['original_request'],reservation)
            selected_policy=ResourcePolicy.from_mapping(plan['policy'])
            require(selected_policy.canonical()==policy.canonical(),
                'SCOPED_CALLER_MACHINE_POLICY_DIFFERS_FROM_ACTUAL_OWNER_PLAN')
            before=self.reconcile_context();current,source,catalogue=self._context(before)
            observed,facts,raw,classification=self._capture(before,current)
            packet=self._inspect(before,current,observed,facts)
            consistency=self.scoped_kernel.validate(packet)
            require(consistency.status=='CONSISTENT_SNAPSHOT','SCOPED_FULL_MACHINE_LEDGER_INVALID')
            selected=[row for row in before.rows if row.bound.reservation==reservation]
            require(len(selected)==1,'SCOPED_MACHINE_SELECTED_RESERVATION_ABSENT')
            actual=observe({'state':controller.paths.state,'share':controller.paths.data})
            require(actual.state=='OBSERVED','SCOPED_ORIGINAL_MACHINE_OBSERVATION_UNKNOWN')
            inputs=[];details=[];outstanding=[]
            for index,(row,projection) in enumerate(zip(before.rows,before.projection)):
                if row.kind!='HELD_CAPACITY' or row.state=='RELEASED':continue
                if row.bound.reservation!=reservation:outstanding.append(row)
                # Child promises remain in the native physical containment
                # roster. A cgroup memory counter includes all its descendants,
                # so a top-level promise and its children are charged once.
                if row.parent is not None:continue
                entries=[entry for entry in catalogue['entries'] if entry['key']==projection.key]
                require(entries and all(entry['role']==entries[0]['role'] for entry in entries),
                    'SCOPED_AUTHENTIC_FULL_PHYSICAL_ROLE_CROSSWALK_REQUIRED')
                if entries[0]['role']!='MEMORY_BYTES':continue
                used=None;counter=None
                if row.bound.reservation!=reservation and observed[index].observed in ('LIVE','REAPED'):
                    slot=self.slots.get(row.bound.reservation.hex())
                    if slot is not None:
                        try:
                            path=Path('/sys/fs/cgroup')/os.fsdecode(row.cgroup.removeprefix(b'/'))/'memory.current'
                            counter=kernel_bytes(path);used=_decimal(counter.removesuffix(b'\n'))
                        except (ResourceProducerRefusal,OSError):used=None
                inputs.append((projection.amount,used));details.append({'row':row,'projection':projection,
                    'counter':counter,'used':used,'native_classification':classification[index],'physical_source':raw[index]})
            projection,ledger_native=observe_ledger(tuple(inputs),core=self.core)
            floors=controller.config.admission_floors
            disks=tuple((name,values['freeBytes'],values['freeInodes']) for name,values in actual.disk.items())
            native_input={'outstanding_count':len(outstanding),'concurrency_limit':policy.max_concurrent_workloads,
                'memory_pressure':actual.memory_pressure_hundredths,'memory_pressure_ceiling':floors.max_memory_pressure_hundredths,
                'disks':tuple((free,inodes) for _name,free,inodes in disks),'disk_byte_floor':floors.min_free_disk_bytes,
                'disk_inode_floor':floors.min_free_inodes,'available_memory':actual.mem_available_bytes,
                'withheld_memory':projection.total,'memory_floor':floors.min_free_memory_bytes,'requested_memory':0}
            numeric,policy_native=observe_policy(**native_input,core=self.core)
            # Preserve the original LaunchJournal schema. Full scoped inputs
            # and actual complete original native machine frames are additive.
            record={'schema':'worldline.protected-machine-admission-v1','stage':stage,'reservation':reservation.hex(),
                'scoped_snapshot':snapshot_record(before),'scoped_packet':S.record(packet),
                'scoped_native':S.record(consistency),'current':S.record(source),
                'measurement':lossless_data(actual.as_dict()),'policy':lossless_data(policy.canonical()),
                'floors':lossless_data({name:getattr(floors,name) for name in floors.__dataclass_fields__}),
                'ledger_input':lossless_data(tuple(inputs)),'ledger_details':S.record(tuple(details)),
                'ledger_result':lossless_data({'total':projection.total,'withheld':projection.withheld}),
                'disk_roster':lossless_data(disks),'native_input':lossless_data(native_input),
                'native_output':{'gate':numeric.gate,'disk_index':numeric.disk_index},
                'full_original_ledger_native':S.record(ledger_native),'full_original_policy_native':S.record(policy_native)}
            self.journal.append('MACHINE_ADMISSION',reservation.hex(),record)
            require(numeric.ready,'SCOPED_ORIGINAL_MACHINE_FLOOR_REFUSED')
            require(before==self.current_snapshot(),'SCOPED_MACHINE_LEDGER_CHANGED_BEFORE_EFFECT')
            return record
    def launch_reserved(self,pending,original_request,reservation):
        from .client_peer import RequestPeer
        from .admission import ResourcePolicy
        with self.gate.mutex,self.order:
            self.intact();require(self.operation_principal is not None and type(original_request) is RequestPeer,
                'SCOPED_ACTUAL_NATIVE_OPERATION_AND_REQUEST_REQUIRED')
            self.journal.load();retained=self.journal.rows.get(reservation.hex())
            require(retained is not None and retained['phase']=='NEVER_DISPATCHED' and reservation.hex() not in self.slots,
                'SCOPED_LAUNCH_REPLAY_OR_UNKNOWN')
            require(original_request.observation()==retained['prepared']['payload']['original_request'],
                'SCOPED_ACTUAL_LAUNCH_ORIGINAL_REQUEST_CHANGED')
            self.actor_slots[reservation]={'original_request':original_request,
                'pending':retained['prepared']['payload']['pending']}
            plan=self.operation_principal.resource_launch_material(original_request,reservation)
            require(type(plan) is dict and set(plan)=={'bound','argv','cwd','environment','systemd_properties','policy','executables'},
                'SCOPED_FULL_AUTHENTIC_OPERATION_LAUNCH_PLAN_REQUIRED')
            before=self.reconcile_context();selected=[row for row in before.rows if row.bound.reservation==reservation]
            require(len(selected)==1 and selected[0].state=='RESERVED' and plan['bound']==S.L.dto_record(selected[0].bound),
                'SCOPED_FULL_NATIVE_RESERVATION_REQUIRED_BEFORE_LAUNCH')
            old=selected[0];join=self.credential_join(original_request)
            if join is not None:require(retained['prepared']['payload'].get('credential_join')==join,
                'SCOPED_ACTUAL_REQUESTER_WORKLOAD_JOIN_CHANGED')
            # The child task/parent controller successor is separately required.
            # This entry is the original top-level operation launch only; it
            # never rewrites a child into a root or borrows a released hold.
            require(old.parent is None,'SCOPED_PARENT_NAMESPACE_CHILD_DISPATCH_REQUIRES_SUCCESSOR')
            require(type(plan['argv']) is list and plan['argv'] and all(type(word) is str and '\0' not in word for word in plan['argv'])
                and type(plan['cwd']) is str and Path(plan['cwd']).is_absolute() and type(plan['environment']) is dict,
                'SCOPED_ORIGINAL_LAUNCH_PLAN_ENCODING_INVALID')
            require(type(plan['systemd_properties']) is list and all(type(word) is str and word and '\0' not in word for word in plan['systemd_properties'])
                and type(plan['policy']) is dict and type(plan['executables']) is dict,'SCOPED_COMPLETE_ENFORCED_POLICY_UNAVAILABLE')
            policy=ResourcePolicy.from_mapping(plan['policy'])
            require(policy.enforcement=='cgroup2' and plan['systemd_properties']==policy.unit_properties(),
                'SCOPED_ORIGINAL_ENFORCED_POLICY_CHANGED')
            sandbox=Path(self.lease.spec['runtime']['tools']['bwrap'])
            require(plan['argv'][0]==str(sandbox) and sandbox in self.lease.allowed
                and plan['executables'].get(str(sandbox))==digest(private(sandbox)),
                'SCOPED_ACTUAL_SELECTED_SANDBOX_EXECUTABLE_UNAVAILABLE')
            for name,value in plan['environment'].items():
                require(type(name) is str and type(value) is str and name and name.replace('_','a').isalnum()
                    and not name[0].isdigit() and '\0' not in value,'SCOPED_ORIGINAL_WORKLOAD_ENVIRONMENT_INVALID')
            self.machine_admission(reservation,policy,'DISPATCH')
            unit=b'worldline-resource-'+reservation.hex().encode('ascii')+b'.service'
            packet=self.lifecycle_packet(original_request,reservation,'RECORD_LAUNCH_INTENT',{'state':'LAUNCH_INTENT','planned_unit':unit})
            self.submit_bound(pending,packet,original_request)
            row=next(item for item in self.current_snapshot().rows if item.bound.reservation==reservation)
            directory=Path(self.lease.spec['paths']['runtime'])/'resource-supervisor';private(directory,directory=True)
            endpoint=directory/reservation.hex();require(not os.path.lexists(endpoint),'SCOPED_RETAINED_SUPERVISOR_ENDPOINT_EXISTS')
            listener=socket.socket(socket.AF_UNIX,socket.SOCK_SEQPACKET|socket.SOCK_CLOEXEC)
            try:
                listener.bind(str(endpoint));os.chmod(endpoint,0o600);listener.listen()
                ticket=digest(canonical({'reservation':S.L.dto_record(row),'request':original_request.observation(),'launch_head':self.journal.head}))
                arguments=[self.cfg['helper'],str(endpoint),ticket,str(self.cfg['workload_uid']),str(self.cfg['workload_gid']),plan['cwd']]
                for name,value in sorted(plan['environment'].items()):arguments.extend(('--env',name,value))
                arguments.extend(('--',*plan['argv']))
                payload={'ticket':ticket,'endpoint':str(endpoint),'row':S.L.dto_record(row),'plan':plan,
                    'launch_intent_packet':S.record(packet),'helper_arguments':arguments}
                if join is not None:payload['credential_join']=join
                dispatch=self.journal.append('DISPATCH_INTENT',reservation.hex(),payload)
                self.sync_launch_journal(dispatch)
                slot=OwnedSupervisorV3(self,row,dispatch,listener);self.slots[reservation.hex()]=slot
                self.actor_slots[reservation]={'original_request':original_request,'pending':pending,'plan':plan}
                command=[self.cfg['systemd_run'],'--system','--no-block','--unit='+unit.decode('ascii'),
                    '--property=Type=exec','--property=RemainAfterExit=yes','--property=Delegate=no','--property=User=root',
                    '--property=Group=root',*(('--property='+value) for value in plan['systemd_properties']),*arguments]
                launched=subprocess.run(command,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                    check=False,env={'PATH':'/usr/bin:/bin','LANG':'C'})
                require(launched.returncode==0,'SCOPED_SYSTEM_MANAGER_DISPATCH_UNKNOWN')
                held=slot.accept_held();native=held['native_fields']
                packet=self.lifecycle_packet(original_request,reservation,'RECORD_RUNNING',{'state':'RUNNING',
                    'actual_unit':native['actual_unit'],'cgroup':native['cgroup'],'invocation':native['invocation']})
                self.submit_bound(pending,packet,original_request);slot.go();slot.close_empty_input();return slot
            except BaseException as exc:
                self.journal.load();phase=self.journal.rows[reservation.hex()]['phase']
                if phase in ('DISPATCH_INTENDED','NAMESPACE_HELD','GO_INTENDED','UNKNOWN'):
                    self.journal.append('UNKNOWN',reservation.hex(),{'refusal':str(exc),'retained_endpoint':str(endpoint)})
                # Keep the exact original capacity/endpoint/intent. No launch
                # retry or terminal verdict follows from a launcher exception.
                raise
    def _actor_process(self,slot,observation):
        pid=observation.host_pid;slot.actor_pidfd=os.pidfd_open(pid,0)
        actual,fdinfo=slot.fd_pid(slot.actor_pidfd)
        require(actual==pid,'SCOPED_ACTUAL_ACTOR_PIDFD_CHANGED')
        root=Path('/proc')/str(pid)
        ns=os.open(root/'ns/pid',os.O_RDONLY|os.O_CLOEXEC)
        try:
            namespace=canonical(identity_record(os.fstat(ns)))
            require(namespace.hex()==slot.held['namespace'],'SCOPED_ACTUAL_ACTOR_NAMESPACE_CHANGED')
        finally:os.close(ns)
        image=Path(os.readlink(root/'exe'))
        require(image==self.helper and digest(private(image))==self.cfg['helper_sha256'],
                'SCOPED_PREEXEC_ACTUAL_HELPER_IMAGE_CHANGED')
        names=('status','cgroup','maps','cmdline')
        before={name:kernel_bytes(root/name) for name in names}
        parsed={}
        for line in before['status'].splitlines():
            name,sep,value=line.partition(b':')
            require(sep and name not in parsed,'SCOPED_ACTUAL_PROC_STATUS_INVALID');parsed[name]=value.strip()
        required=(b'Pid',b'NSpid',b'Uid',b'Gid',b'Groups',b'CapEff',b'CapPrm',b'CapInh',b'CapBnd',b'CapAmb',b'NoNewPrivs')
        require(all(name in parsed for name in required),'SCOPED_COMPLETE_ACTOR_PROC_STATUS_REQUIRED')
        uids=tuple(_decimal(raw) for raw in parsed[b'Uid'].split());gids=tuple(_decimal(raw) for raw in parsed[b'Gid'].split())
        namespaces=tuple(_decimal(raw) for raw in parsed[b'NSpid'].split())
        require(len(uids)==4 and len(gids)==4 and namespaces,'SCOPED_ACTUAL_PROC_ID_ROSTERS_REQUIRED')
        require(before['cgroup']==b'0::'+bytes.fromhex(slot.held['properties']['ControlGroup'])+b'\n',
                'SCOPED_ACTOR_DISPATCH_CGROUP_CHANGED')
        for line in before['maps'].splitlines():
            pieces=line.split(None,5)
            if len(pieces)==6 and pieces[5].startswith(b'/'):
                mapped=Path(os.fsdecode(pieces[5]));require(mapped in self.lease.allowed,'SCOPED_ACTOR_MAPPED_SOURCE_UNPINNED');private(mapped)
        after={name:kernel_bytes(root/name) for name in names}
        require(after==before,'SCOPED_ACTUAL_ACTOR_PROC_CHANGED_DURING_CAPTURE')
        wait=slot.pidfd_state(slot.actor_pidfd)
        return {'pid':_decimal(parsed[b'Pid']),'namespace_pid':namespaces[-1],'uids':uids,'gids':gids,
            'groups':tuple(_decimal(raw) for raw in parsed[b'Groups'].split()),'namespace':namespace,
            'fdinfo':fdinfo,'wait':wait,'raw':before,'cap_effective':_hex(parsed[b'CapEff']),
            'cap_permitted':_hex(parsed[b'CapPrm']),'cap_inheritable':_hex(parsed[b'CapInh']),
            'cap_bounding':_hex(parsed[b'CapBnd']),'cap_ambient':_hex(parsed[b'CapAmb']),
            'no_new_privs':_decimal(parsed[b'NoNewPrivs']),'image':str(image),'image_sha256':self.cfg['helper_sha256']}
    def _execution_crosswalk(self,authority,current,plan,original_requester):
        # Actual principal method returns the retained authenticated owner/Gate/
        # store capture. Every field is data; the full native composite and
        # producer/source correspondence remain independent requirements.
        full=authority['current'];crosswalk=full.get('execution_crosswalk')
        names={'schema','owner_genesis','installation','gate_config_raw','gate_managed_observation',
            'operation_grant','operation_binding','operation_policy','resource_policy','root_set','root_head',
            'resource_current','resource_source','transaction','original_request','preparer_peer'}
        require(type(crosswalk) is dict and set(crosswalk)==names
            and crosswalk['schema']=='worldline.protected-operation-resource-crosswalk-v1',
            'SCOPED_ACTUAL_FULL_OWNER_OPERATION_RESOURCE_CROSSWALK_REQUIRED')
        require(crosswalk['owner_genesis']==self.operation_principal.journal.owner_genesis
            and crosswalk['installation']==self.lease.spec and crosswalk['gate_config_raw']==self.gate.config_raw
            and crosswalk['gate_managed_observation']==self.gate.config['managed_observation']
            and crosswalk['original_request']==authority['original_request']
            and crosswalk['operation_binding']==authority['authority_snapshot']['evidence']['owner_resolution']
            and crosswalk['operation_policy']==crosswalk['operation_grant']['policy']
            and crosswalk['resource_policy']==current.scope.policy.hex()
            and crosswalk['root_head']==current.root_head.hex()
            and S.restore(crosswalk['resource_current'])==current,
            'SCOPED_ACTUAL_OWNER_CURRENT_CROSSWALK_CHANGED')
        require(crosswalk['resource_source']==full['current_source']
            and full['plan']==plan and crosswalk['operation_binding']['id']['root_set']==crosswalk['root_set'],
            'SCOPED_FULL_CURRENT_SOURCE_PLAN_OR_ROOT_CROSSWALK_CHANGED')
        def complete(value):return canonical(S.record(value))
        return ActorExecutionCrosswalk(resource_current=current,
            operation_policy=_id(crosswalk['operation_policy']),operation_root_set=_id(crosswalk['root_set']),
            owner_genesis=complete(crosswalk['owner_genesis']),installation=complete(crosswalk['installation']),
            gate_config=crosswalk['gate_config_raw'],managed_observation=complete(crosswalk['gate_managed_observation']),
            original_grant=complete(crosswalk['operation_grant']),complete_crosswalk=complete(crosswalk),
            current_source=complete(crosswalk['resource_source']),original_request=complete(crosswalk['original_request']),
            original_requester=original_requester,
            original_transaction=None if crosswalk['transaction'] is None else complete(crosswalk['transaction']),
            preparer=None if crosswalk['preparer_peer'] is None else complete(crosswalk['preparer_peer']),
            selected_plan=hashlib.sha256(complete(plan)).digest())
    def go_scoped(self,slot):
        from .client_peer import RequestPeer
        from .admission import ResourcePolicy
        with self.gate.mutex,self.order:
            self.intact();require(type(slot) is OwnedSupervisorV3 and self.slots.get(slot.row.bound.reservation.hex()) is slot
                and not slot.started and not slot.failed and slot.closed is None,'SCOPED_ACTUAL_SINGLE_GO_OWNER_REQUIRED')
            retained=self.actor_slots.get(slot.row.bound.reservation)
            require(retained is not None and type(retained['original_request']) is RequestPeer,
                    'SCOPED_ACTUAL_BEFORE_EXEC_REQUEST_DESCRIPTOR_REQUIRED')
            before=self.current_snapshot();row=next((row for row in before.rows if row.bound==slot.row.bound),None)
            require(row is not None and row.state=='RUNNING','SCOPED_ACTUAL_NATIVE_RUNNING_REQUIRED_BEFORE_GO')
            policy=ResourcePolicy.from_mapping(slot.dispatch['payload']['plan']['policy'])
            machine=self.machine_admission(row.bound.reservation,policy,'GO')
            go_event=self.journal.append('GO_INTENT',row.bound.reservation.hex(),{'running_snapshot':snapshot_record(before),
                'running_row':S.L.dto_record(row),'machine_admission':machine})
            self.sync_launch_journal(go_event)
            try:
                slot.connection.sendall(b'G');slot.started=True
                # Sole actual receiver under producer order. The trusted child
                # sends once and blocks; no concurrent/extra queue fallback.
                measured=wait_observation(slot.credential_receiver,slot.dispatch['payload']['ticket'].encode('ascii'))
                process=self._actor_process(slot,measured)
                input_transport=slot.bind_actor_stdin(process)
                method=getattr(self.operation_principal,'resource_actor_execution_material',None)
                require(callable(method),'SCOPED_ACTUAL_BEFORE_EXEC_NATIVE_OPERATION_BRIDGE_UNAVAILABLE')
                authority=method(row.bound.operation,row.bound.reservation,retained['original_request'])
                require(type(authority) is dict and {'original_request','scope','bound','native_use','event_id',
                    'native','current','plan','scoped_history','authority_snapshot','material'}<=set(authority),
                    'SCOPED_COMPLETE_ACTUAL_BEFORE_EXEC_NATIVE_OPERATION_REQUIRED')
                require(authority['original_request']==retained['original_request'].observation()
                    and authority['scope']==S.L.dto_record(row.scope) and authority['bound']==S.L.dto_record(row.bound)
                    and authority['plan']==slot.dispatch['payload']['plan']
                    and tuple(authority['scoped_history'])==self.committed_resource_history(row.bound.operation,row.bound.reservation),
                    'SCOPED_ACTUAL_CURRENT_OPERATION_SCOPE_OR_EXECUTABLE_CHANGED')
                before=self.current_snapshot();current,source,_catalogue=self._context(before)
                observed,facts,raw,_classification=self._capture(before,current)
                packet=self._inspect(before,current,observed,facts,self._request(before,row.bound.reservation))
                running=[event for event in self.committed_resource_history(row.bound.operation,row.bound.reservation)
                    if S.restore(event['packet']).request.original.kind=='RECORD_RUNNING']
                require(len(running)==1,'SCOPED_EXACT_COMMITTED_NATIVE_RUNNING_EVENT_REQUIRED')
                raw_peer=bytes.fromhex(authority['original_request']['peer']['rawUcred'])
                _pid,requester_uid,requester_gid=struct.unpack('@iII',raw_peer)
                source_id=hashlib.sha256(canonical(self.lease.spec)).digest()
                plan_id=hashlib.sha256(canonical(S.record(authority['plan']))).digest()
                running_id=hashlib.sha256(canonical(running[0])).digest();use_id=operation_bytes(authority['event_id'])
                physical=slot.observe()['native_fields'];words=measured.capability_words
                native_observation=ActorNativeObservation(bound=row.bound,raw_frame=measured.raw_frame,
                    raw_sender=measured.raw_sender_credentials,ticket=measured.ticket,
                    raw_proc_status=process['raw']['status'],raw_proc_cgroup=process['raw']['cgroup'],
                    raw_proc_maps=process['raw']['maps'],raw_proc_cmdline=process['raw']['cmdline'],raw_pidfd_info=process['fdinfo'],
                    namespace=process['namespace'],held_namespace=bytes.fromhex(slot.held['namespace']),
                    helper_image=bytes.fromhex(process['image_sha256']),expected_helper_image=bytes.fromhex(self.cfg['helper_sha256']),
                    executable_plan=plan_id,expected_executable_plan=plan_id,original_requester=row.bound.owner,
                    requester_credentials=raw_peer,expected_requester_credentials=raw_peer,
                    dispatch=physical['dispatch'],running_event=running_id,expected_running_event=running_id,
                    canonical_use_event=use_id,expected_canonical_use_event=use_id,
                    store_genesis=current.store_genesis,expected_store_genesis=self.lease.genesis['store']['identity'].encode('utf-8'),
                    source_lease=source_id,expected_source_lease=source_id,actor_wait=process['wait'],
                    helper_wait=physical['helper_wait'],namespace_wait=physical['namespace_wait'],
                    host_pid=measured.host_pid,namespace_pid=measured.namespace_pid,sender_uid=measured.sender_real_uid,
                    sender_gid=measured.sender_real_gid,real_uid=measured.uids[0],effective_uid=measured.uids[1],saved_uid=measured.uids[2],
                    real_gid=measured.gids[0],effective_gid=measured.gids[1],saved_gid=measured.gids[2],
                    capability_version=measured.capability_version,effective_low=words[0][0],permitted_low=words[0][1],inheritable_low=words[0][2],
                    effective_high=words[1][0],permitted_high=words[1][1],inheritable_high=words[1][2],
                    securebits=measured.securebits,no_new_privs=measured.no_new_privs,requester_uid=requester_uid,requester_gid=requester_gid,
                    configured_requester_uid=self.lease.spec['endpoint']['requester_uid'],workload_uid=self.cfg['workload_uid'],workload_gid=self.cfg['workload_gid'],
                    proc_host_pid=process['pid'],proc_namespace_pid=process['namespace_pid'],proc_real_uid=process['uids'][0],
                    proc_effective_uid=process['uids'][1],proc_saved_uid=process['uids'][2],proc_fs_uid=process['uids'][3],
                    proc_real_gid=process['gids'][0],proc_effective_gid=process['gids'][1],proc_saved_gid=process['gids'][2],proc_fs_gid=process['gids'][3],
                    proc_effective=process['cap_effective'],proc_permitted=process['cap_permitted'],proc_inheritable=process['cap_inheritable'],
                    proc_bounding=process['cap_bounding'],proc_ambient=process['cap_ambient'],proc_no_new_privs=process['no_new_privs'])
                capabilities=tuple(ActorCapability(*values) for values in measured.capabilities)
                native=self.actor_kernel.check(packet,native_observation,capabilities,measured.supplementary_groups,process['groups'])
                require(native.status=='READY_CONJUNCT','SCOPED_NATIVE_ACTOR_CREDENTIAL_CONJUNCT_REFUSED')
                crosswalk=self._execution_crosswalk(authority,current,authority['plan'],row.bound.owner)
                composite=self.execution_kernel.check(packet,native_observation,capabilities,
                    measured.supplementary_groups,process['groups'],crosswalk,authority['authority_snapshot'])
                require(composite.status=='READY_VALUE_CONJUNCTION',
                    'SCOPED_CLOSED_NATIVE_ACTOR_OPERATION_RESOURCE_CONJUNCTION_REFUSED')
                machine=self.machine_admission(row.bound.reservation,policy,'GO')
                witness={'schema':'worldline.genuine-actor-native-durable-witness-v1','packet':packet,
                    'actor':native_observation,'capabilities':capabilities,'groups':measured.supplementary_groups,
                    'proc_groups':process['groups'],'native':native,'measured':measured.record(),'process':process,
                    'authority':authority,'crosswalk':crosswalk,'composite':composite,'machine_admission':machine,'physical':raw,'current_source':source,
                    'running_event':running[0],'held_event':slot.held_event,'dispatch':slot.dispatch,
                    'input_transport':input_transport,
                    'source_envelope':self.lease.spec,'issuer_head':self.gate.issuer.head()}
                # Complete native result and genuine raw physical/source/operation
                # joins are committed and fsynced before the pre-exec child ACK.
                event=self.observations.append('ACTOR_NATIVE_COMMITTED',row.bound.reservation.hex(),witness)
                persisted=S.restore(event['payload']);redecision=self.actor_kernel.check(persisted['packet'],persisted['actor'],
                    persisted['capabilities'],persisted['groups'],persisted['proc_groups'])
                require(redecision==native,'SCOPED_DURABLE_ACTOR_NATIVE_REDECISION_CHANGED')
                closed_redecision=self.execution_kernel.check(persisted['packet'],persisted['actor'],
                    persisted['capabilities'],persisted['groups'],persisted['proc_groups'],persisted['crosswalk'],
                    persisted['authority']['authority_snapshot'])
                require(closed_redecision==composite,'SCOPED_DURABLE_CLOSED_NATIVE_CONJUNCTION_CHANGED')
                body=send_committed_ack(slot.credential_receiver,measured.raw_frame,canonical(event))
                slot.credential_committed=event
                slot.credential_ack_event=self.observations.append('ACTOR_ACK_SENT',row.bound.reservation.hex(),{'committed_event':event,'ack':body})
                return event
            except BaseException:
                slot.failed=True;self.journal.append('UNKNOWN',row.bound.reservation.hex(),
                    {'cause':'SCOPED_ACTOR_NATIVE_ACK_OR_CUSTODY_UNKNOWN'});raise
    def close(self):
        for slot in self.slots.values():slot.close()
        if hasattr(self,'observations'):self.observations.close()
        self.journal.db.close();self.poisoned=True


