"""Owned closed actor/canonical/scoped native conjunction, no Python verdict."""
from __future__ import annotations
import ctypes as C
from dataclasses import dataclass,fields
from . import resource_scoped_run_ledger as S
from . import resource_run_ledger as L
from .resource_actor_admission import ActorAdmissionKernel,RawActorPacket
from .operation_authority_kernel import OperationAuthorityKernel,digest,_Digest
from .recovery_authority_kernel_v3 import BoundUse,NativeObservation
from .errors import CoreUnavailable

STATUSES=('READY_VALUE_CONJUNCTION','ACTOR_REFUSED','AUTHORITY_REFUSED',
    'ORIGINAL_BINDING_MISMATCH','CURRENT_BINDING_MISMATCH','CROSSWALK_MISMATCH',
    'REQUESTER_MISMATCH','PHYSICAL_ORIGIN_MISMATCH')
@dataclass(frozen=True,slots=True,kw_only=True)
class ActorExecutionCrosswalk:
    resource_current:S.CurrentObservation
    operation_policy:bytes
    operation_root_set:bytes
    owner_genesis:bytes
    installation:bytes
    gate_config:bytes
    managed_observation:bytes
    original_grant:bytes
    complete_crosswalk:bytes
    current_source:bytes
    original_request:bytes
    original_requester:bytes
    original_transaction:bytes|None
    preparer:bytes|None
    selected_plan:bytes
@dataclass(frozen=True,slots=True)
class ActorExecutionNativeDecision:
    entry_point:str
    status:str
    actor_input:bytes
    actor_arena:bytes
    actor_rosters:tuple[tuple[str,bytes,int],...]
    crosswalk:bytes
    authority_input:bytes
    authority_arena:bytes
    authority_rosters:tuple[tuple[str,bytes,int],...]
    raw_output:bytes
    transport_status:int
class RawExecutionCrosswalk(C.Structure):
    _fields_=[('resource_current',S.RawCurrentObservation),('operation_policy',_Digest),
        ('operation_root_set',_Digest)]+[(name,L.RawId) for name in
        ('owner_genesis','installation','gate_config','managed_observation','original_grant',
         'complete_crosswalk','current_source','original_request','original_requester',
         'original_transaction','preparer','selected_plan')]
S._KNOWN.update({ActorExecutionCrosswalk.__name__:ActorExecutionCrosswalk,
                ActorExecutionNativeDecision.__name__:ActorExecutionNativeDecision,
                BoundUse.__name__:BoundUse,NativeObservation.__name__:NativeObservation})
class ActorExecutionKernel:
    def __init__(self,core):
        self.actor=ActorAdmissionKernel(core);self.authority=OperationAuthorityKernel(core)
        try:
            version=core._lib.wl_resource_actor_execution_version_v1
            layout=core._lib.wl_resource_actor_execution_layout_v1
            self.call=core._lib.wl_resource_actor_execution_decide_v1
        except AttributeError as error:raise CoreUnavailable('complete actor/canonical native conjunction unavailable') from error
        version.argtypes,version.restype=[],C.c_uint32
        layout.argtypes,layout.restype=[C.c_uint32,C.c_uint32],C.c_long
        if version()!=1:raise CoreUnavailable('actor/canonical native version differs')
        if layout(3,0)!=C.sizeof(RawExecutionCrosswalk) or layout(3,1)!=C.alignment(RawExecutionCrosswalk):
            raise CoreUnavailable('actor/canonical crosswalk ABI differs')
        for selector,(name,_type) in enumerate(RawExecutionCrosswalk._fields_,2):
            if layout(3,selector)!=getattr(RawExecutionCrosswalk,name).offset:
                raise CoreUnavailable('actor/canonical crosswalk ABI field differs',field=name)
        # Actor input + arena + every complete roster, canonical input + arena
        # and every complete roster + typed crosswalk + output. Storage extents
        # are representation limits, never quantity/epoch domain limits.
        self.call.argtypes=[C.c_void_p,C.c_size_t]*(2+len(S._ROSTERS)+3+2+4+1+1)
        self.call.restype=C.c_int
    def prepare(self,packet,observation,capabilities,groups,proc_groups,crosswalk,authority_snapshot):
        if type(crosswalk) is not ActorExecutionCrosswalk:
            raise ValueError('complete genuine typed actor crosswalk required')
        actor,data,length,rosters=self.actor.prepare(packet,observation,capabilities,groups,proc_groups)
        arena=bytearray(bytes(data)[:length]);raw=RawExecutionCrosswalk()
        for name,kind in raw._fields_:
            value=getattr(crosswalk,name)
            if kind is S.RawCurrentObservation:datum=S._marshal(value,arena)
            elif kind is _Digest:
                if type(value) is not bytes:raise ValueError('complete operation identity bytes required')
                datum=digest(value.hex())
            else:datum=L._id(value,arena)
            setattr(raw,name,datum)
        data=(C.c_uint8*max(1,len(arena)))()
        if arena:C.memmove(data,bytes(arena),len(arena))
        authority,authority_arena,arrays=self.authority.prepare(authority_snapshot,'AUTHORIZE_EXECUTION')
        full_authority=(C.c_uint8*max(1,len(authority_arena.raw)))()
        if authority_arena.raw:C.memmove(full_authority,bytes(authority_arena.raw),len(authority_arena.raw))
        named=tuple((name,array,len(array)) for name,array in zip(('grants','uses','receipts','events'),arrays))
        return actor,data,len(arena),rosters,authority,full_authority,len(authority_arena.raw),named,raw
    def check(self,packet,observation,capabilities,groups,proc_groups,crosswalk,authority_snapshot):
        actor,data,length,rosters,authority,authority_arena,authority_length,named,raw=self.prepare(
            packet,observation,capabilities,groups,proc_groups,crosswalk,authority_snapshot)
        result=L.RawResult()
        arguments=[C.byref(actor),C.sizeof(actor),data,L._extent(length)]
        for _name,owned,count in rosters:arguments.extend((owned,L._extent(count)))
        arguments.extend((C.byref(authority),C.sizeof(authority),authority_arena,L._extent(authority_length)))
        for _name,array,count in named:arguments.extend((array,L._extent(count)))
        arguments.extend((C.byref(raw),C.sizeof(raw),C.byref(result),C.sizeof(result)))
        transport=self.call(*arguments)
        if transport!=0:raise CoreUnavailable('actor/canonical complete native transport refused')
        if result.status>=len(STATUSES):raise CoreUnavailable('actor/canonical native output malformed')
        return ActorExecutionNativeDecision('wl_resource_actor_execution_decide_v1',STATUSES[result.status],
            bytes(actor),bytes(data)[:length],tuple((name,bytes(owned),count) for name,owned,count in rosters),bytes(raw),
            bytes(authority),bytes(authority_arena)[:authority_length],tuple((name,bytes(owned),count) for name,owned,count in named),
            bytes(result),transport)
