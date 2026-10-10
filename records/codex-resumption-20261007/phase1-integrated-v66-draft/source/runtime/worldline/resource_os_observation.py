"""Owned complete native physical-observation transport; input DTOs are data.

No protected flag, synthetic producer verdict, fake library or bounded epoch
fallback exists. The protected collector independently owns the OS sources.
"""
from __future__ import annotations
import ctypes as C
from dataclasses import dataclass,fields
from .errors import CoreUnavailable
from . import resource_run_ledger as L

JOURNAL_PHASE=('UNAVAILABLE','NEVER_DISPATCHED','DISPATCH_INTENDED','NAMESPACE_HELD','NAMESPACE_CLOSED')

@dataclass(frozen=True,slots=True,kw_only=True)
class PhysicalFacts:
    current: L.RunContext
    current_epoch: int | None
    retained: L.RunBinding
    current_universe_head: bytes | None
    current_ledger_head: bytes | None
    intent: bytes | None
    dispatch: bytes | None
    observation_head: bytes | None
    actual_unit: bytes | None
    cgroup: bytes | None
    invocation: bytes | None
    namespace: bytes | None
    held_namespace: bytes | None
    peer: bytes | None
    held_peer: bytes | None
    helper_image: bytes | None
    expected_helper_image: bytes | None
    challenge: bytes | None
    held_challenge: bytes | None
    protocol: bytes | None
    closed_event: bytes | None
    namespace_wait: bytes | None
    helper_wait: bytes | None
    cgroup_events: bytes | None
    cgroup_type: bytes | None
    manager_delegate: bytes | None
    cgroup_owner: int | None
    cgroup_group_write: int | None
    cgroup_other_write: int | None
    actual_store_genesis: bytes | None
    actual_store_id: bytes | None
    owner_store_genesis: bytes | None
    owner_store_id: bytes | None
    genesis_universe: bytes | None
    genesis_instance: bytes | None
    genesis_context_head: bytes | None
    genesis_prime: bytes | None
    genesis_root_count: int | None
    phase: str

_FACT_FIELDS=[('current',L.RawContext),('current_epoch',L.RawEpoch),('retained',L.RawBinding)]
_FACT_FIELDS += [(name,L.RawId) for name in ('current_universe_head','current_ledger_head','intent','dispatch','observation_head','actual_unit','cgroup','invocation',
    'namespace','held_namespace','peer','held_peer','helper_image','expected_helper_image','challenge','held_challenge',
    'protocol','closed_event','namespace_wait','helper_wait','cgroup_events','cgroup_type','manager_delegate')]
_FACT_FIELDS += [(name,L.RawEpoch) for name in ('cgroup_owner','cgroup_group_write','cgroup_other_write')]
_FACT_FIELDS += [(name,L.RawId) for name in ('actual_store_genesis', 'actual_store_id', 'owner_store_genesis', 'owner_store_id', 'genesis_universe', 'genesis_instance', 'genesis_context_head', 'genesis_prime')]
_FACT_FIELDS += [('genesis_root_count',L.RawEpoch)]
_FACT_FIELDS += [('phase',C.c_uint8)]

class RawFacts(C.Structure): _fields_=_FACT_FIELDS
class RawObservationInput(C.Structure):
    _fields_=[('state',L.RawState),('item',L.RawRow),('captured',RawFacts)]

def facts_record(facts):
    if type(facts) is not PhysicalFacts:raise ValueError('complete physical facts required')
    answer={}
    for field in fields(facts):
        value=getattr(facts,field.name)
        if type(value) in (L.RunContext,L.RunBinding):answer[field.name]=L.dto_record(value)
        elif type(value) is bytes:answer[field.name]={'bytes':value.hex()}
        elif type(value) is int:
            magnitude=abs(value)
            answer[field.name]={'negative':value<0,'magnitude':magnitude.to_bytes((magnitude.bit_length()+7)//8,'little').hex()}
        elif value is None or type(value) is str:answer[field.name]=value
        else:raise ValueError('physical source field type differs')
    return answer

class ResourceObservationKernel:
    def __init__(self,core):
        # Checks every unchanged base resource ABI field and offset too.
        self.base=L.ResourceRunLedgerKernel(core)
        try:
            version=core._lib.wl_resource_observation_version_v1
            layout=core._lib.wl_resource_observation_layout_v1
            self.call=core._lib.wl_resource_observation_classify_v1
            self.current_call=core._lib.wl_resource_observation_current_v1
            self.genesis_call=core._lib.wl_resource_observation_genesis_current_v1
        except AttributeError as exc:raise CoreUnavailable('protected physical-observation native ABI unavailable') from exc
        version.argtypes,version.restype=[],C.c_uint32
        layout.argtypes,layout.restype=[C.c_uint32,C.c_uint32],C.c_long
        if version()!=1:raise CoreUnavailable('physical-observation native version differs')
        for kind,typ in enumerate((RawFacts,RawObservationInput),1):
            if layout(kind,0)!=C.sizeof(typ) or layout(kind,1)!=C.alignment(typ):raise CoreUnavailable('physical-observation native layout differs')
            for index,(name,_typ) in enumerate(typ._fields_,2):
                if layout(kind,index)!=getattr(typ,name).offset:raise CoreUnavailable('physical-observation native field differs',field=name)
        self.call.argtypes=[C.c_void_p,C.c_size_t]*3;self.call.restype=C.c_int
        self.current_call.argtypes=self.call.argtypes;self.current_call.restype=C.c_int
        self.genesis_call.argtypes=self.call.argtypes;self.genesis_call.restype=C.c_int
    def prepare(self,state,row,facts):
        if type(facts) is not PhysicalFacts:raise ValueError('complete typed physical facts required')
        arena=bytearray();raw=RawFacts()
        for name,typ in RawFacts._fields_:
            datum=getattr(facts,name)
            if typ is L.RawId:value=L._id(datum,arena)
            elif typ is L.RawEpoch:value=L._epoch(datum,arena)
            elif typ is L.RawContext:value=L._marshal('Context',datum,arena)
            elif typ is L.RawBinding:value=L._marshal('Binding',datum,arena)
            else:
                if datum not in JOURNAL_PHASE:raise ValueError('physical journal phase differs')
                value=JOURNAL_PHASE.index(datum)
            setattr(raw,name,value)
        packet=RawObservationInput(L._marshal('State',state,arena),L._marshal('Row',row,arena),raw)
        owned=(C.c_uint8*max(1,len(arena)))()
        if arena:C.memmove(owned,bytes(arena),len(arena))
        return packet,owned,len(arena)
    def classify(self,state,row,facts):
        packet,arena,length=self.prepare(state,row,facts);result=L.RawResult()
        status=self.call(C.byref(packet),C.sizeof(packet),arena,L._extent(length),C.byref(result),C.sizeof(result))
        if status!=0:raise CoreUnavailable('physical observation native transport refused')
        if result.status>=len(L.LIVENESS):raise CoreUnavailable('physical observation native output malformed')
        return L.LIVENESS[result.status]
    def current(self,state,row,facts):
        packet,arena,length=self.prepare(state,row,facts);result=L.RawResult()
        status=self.current_call(C.byref(packet),C.sizeof(packet),arena,L._extent(length),C.byref(result),C.sizeof(result))
        if status!=0:raise CoreUnavailable('current resource context native transport refused')
        if result.status not in (0,1):raise CoreUnavailable('current resource context native output malformed')
        return ('CURRENT_REFUSED','CURRENT_READY')[result.status]

    def genesis_current(self,state,row,facts):
        packet,arena,length=self.prepare(state,row,facts);result=L.RawResult()
        status=self.genesis_call(C.byref(packet),C.sizeof(packet),arena,L._extent(length),C.byref(result),C.sizeof(result))
        if status!=0:raise CoreUnavailable('current resource context native transport refused')
        if result.status not in (0,1):raise CoreUnavailable('current resource context native output malformed')
        return ('CURRENT_REFUSED','CURRENT_READY')[result.status]
