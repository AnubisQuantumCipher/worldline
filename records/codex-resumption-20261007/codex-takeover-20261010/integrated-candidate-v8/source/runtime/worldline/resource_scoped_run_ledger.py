"""Owned complete full-domain scoped-history native transport; DTOs are data.

The actual protected source/custody/current/physical/history/canonical caller
must supply complete immutable snapshots. No Python permission calculation,
label, HMAC, receipt or asserted remainder substitutes for native Check.
All original public APIs and wire domains remain separate and unchanged.
"""
from __future__ import annotations
import ctypes as C
from dataclasses import dataclass,fields
from .errors import CoreUnavailable
from . import resource_run_ledger as L
from . import resource_os_observation as O

SCOPED_ACTIONS = ('ORDINARY','ADVANCE_CONTEXT')
SCOPED_STATUSES = ('READY', 'INVALID_BEFORE', 'INVALID_PROPOSED', 'HISTORY_INVALID', 'CURRENT_OBSERVATION_INVALID', 'PHYSICAL_ROSTER_INVALID', 'PHYSICAL_PROJECTION_INVALID', 'PHYSICAL_CONSERVATION_MISMATCH', 'PARENT_INVALID', 'REQUEST_INVALID', 'STALE_EPOCH', 'LEDGER_HEAD_MISMATCH', 'EPOCH_NOT_SUCCESSOR', 'HISTORICAL_ROW_REMOVED', 'HISTORICAL_ROW_CHANGED', 'IMMUTABLE_ORIGIN_CHANGED', 'NATIVE_ROSTER_INVALID', 'ILLEGAL_LIFECYCLE', 'CONTEXT_CHANGED', 'CAPACITY_EXCEEDED', 'CONTEXT_ADVANCE_INVALID')

@dataclass(frozen=True,slots=True,kw_only=True)
class ScopedState:
    current: L.RunContext
    resource_epoch: int | None
    universe_head: bytes | None
    ledger_head: bytes | None
    history_head: bytes | None
    physical_head: bytes | None

@dataclass(frozen=True,slots=True,kw_only=True)
class ScopeFrame:
    scope: L.RunContext
    first_epoch: int | None
    universe_head: bytes | None
    frame_head: bytes | None
    prior_frame: bytes | None
    store_genesis: bytes | None
    store_id: bytes | None
    root_head: bytes | None
    prime: bytes | None
    root_count: int
    cause: bytes | None
    requester: bytes | None
    receipt: bytes | None
    catalogue_head: bytes | None
    observation_head: bytes | None

@dataclass(frozen=True,slots=True,kw_only=True)
class PhysicalKey:
    machine: bytes | None
    resource: bytes | None
    unit: bytes | None

@dataclass(frozen=True,slots=True,kw_only=True)
class PhysicalBucket:
    key: PhysicalKey
    capacity: int
    held_total: int
    charged_total: int
    capacity_source: bytes | None
    catalogue_head: bytes | None
    observation_head: bytes | None

@dataclass(frozen=True,slots=True,kw_only=True)
class PhysicalProjection:
    key: PhysicalKey
    bound: L.RunBinding
    origin: L.RunContext
    catalogue_head: bytes | None
    numerator: int
    denominator: int
    amount: int

@dataclass(frozen=True,slots=True,kw_only=True)
class CurrentObservation:
    scope: L.RunContext
    resource_epoch: int | None
    universe_head: bytes | None
    ledger_head: bytes | None
    history_head: bytes | None
    physical_head: bytes | None
    store_genesis: bytes | None
    store_id: bytes | None
    root_head: bytes | None
    prime: bytes | None
    root_count: int
    cause: bytes | None
    requester: bytes | None
    receipt: bytes | None
    catalogue_head: bytes | None
    observation_head: bytes | None

@dataclass(frozen=True,slots=True,kw_only=True)
class ScopedIntent:
    kind: str
    original: L.RunRequest
    expected_epoch: int | None
    expected_ledger_head: bytes | None
    request_id: bytes | None
    cause: bytes | None
    requester: bytes | None
    receipt: bytes | None

class RawScopedState(C.Structure):
    _fields_ = [
        ('current',L.RawContext),
        ('resource_epoch',L.RawEpoch),
        ('universe_head',L.RawId),
        ('ledger_head',L.RawId),
        ('history_head',L.RawId),
        ('physical_head',L.RawId),
    ]

class RawScopeFrame(C.Structure):
    _fields_ = [
        ('scope',L.RawContext),
        ('first_epoch',L.RawEpoch),
        ('universe_head',L.RawId),
        ('frame_head',L.RawId),
        ('prior_frame',L.RawId),
        ('store_genesis',L.RawId),
        ('store_id',L.RawId),
        ('root_head',L.RawId),
        ('prime',L.RawId),
        ('root_count',L.RawQuantity),
        ('cause',L.RawId),
        ('requester',L.RawId),
        ('receipt',L.RawId),
        ('catalogue_head',L.RawId),
        ('observation_head',L.RawId),
    ]

class RawPhysicalKey(C.Structure):
    _fields_ = [
        ('machine',L.RawId),
        ('resource',L.RawId),
        ('unit',L.RawId),
    ]

class RawPhysicalBucket(C.Structure):
    _fields_ = [
        ('key',RawPhysicalKey),
        ('capacity',L.RawQuantity),
        ('held_total',L.RawQuantity),
        ('charged_total',L.RawQuantity),
        ('capacity_source',L.RawId),
        ('catalogue_head',L.RawId),
        ('observation_head',L.RawId),
    ]

class RawPhysicalProjection(C.Structure):
    _fields_ = [
        ('key',RawPhysicalKey),
        ('bound',L.RawBinding),
        ('origin',L.RawContext),
        ('catalogue_head',L.RawId),
        ('numerator',L.RawQuantity),
        ('denominator',L.RawQuantity),
        ('amount',L.RawQuantity),
    ]

class RawCurrentObservation(C.Structure):
    _fields_ = [
        ('scope',L.RawContext),
        ('resource_epoch',L.RawEpoch),
        ('universe_head',L.RawId),
        ('ledger_head',L.RawId),
        ('history_head',L.RawId),
        ('physical_head',L.RawId),
        ('store_genesis',L.RawId),
        ('store_id',L.RawId),
        ('root_head',L.RawId),
        ('prime',L.RawId),
        ('root_count',L.RawQuantity),
        ('cause',L.RawId),
        ('requester',L.RawId),
        ('receipt',L.RawId),
        ('catalogue_head',L.RawId),
        ('observation_head',L.RawId),
    ]

class RawScopedIntent(C.Structure):
    _fields_ = [
        ('kind',C.c_uint8),
        ('original',L.RawRequest),
        ('expected_epoch',L.RawEpoch),
        ('expected_ledger_head',L.RawId),
        ('request_id',L.RawId),
        ('cause',L.RawId),
        ('requester',L.RawId),
        ('receipt',L.RawId),
    ]

class RawScopedPacket(C.Structure):
    _fields_=[('schema_version',C.c_uint32),('before_state',RawScopedState),
              ('proposed_state',RawScopedState),('current',RawCurrentObservation),
              ('request',RawScopedIntent)]

@dataclass(frozen=True,slots=True,kw_only=True)
class ScopedPacket:
    before: ScopedState
    history: tuple[ScopeFrame,...]
    rows: tuple[L.RunRow,...]
    projection: tuple[PhysicalProjection,...]
    buckets: tuple[PhysicalBucket,...]
    proposed: ScopedState
    proposed_history: tuple[ScopeFrame,...]
    proposed_rows: tuple[L.RunRow,...]
    proposed_projection: tuple[PhysicalProjection,...]
    proposed_buckets: tuple[PhysicalBucket,...]
    actual_buckets: tuple[PhysicalBucket,...]
    observed: tuple[L.RunObservation,...]
    facts: tuple[O.PhysicalFacts,...]
    current: CurrentObservation
    request: ScopedIntent

@dataclass(frozen=True,slots=True)
class ScopedNativeDecision:
    entry_point: str
    status: str
    raw_input: bytes
    raw_arena: bytes
    raw_rosters: tuple[tuple[str,bytes,int],...]
    raw_output: bytes
    transport_status: int

_RECORDS = {
    ScopedState: RawScopedState,
    ScopeFrame: RawScopeFrame,
    PhysicalKey: RawPhysicalKey,
    PhysicalBucket: RawPhysicalBucket,
    PhysicalProjection: RawPhysicalProjection,
    CurrentObservation: RawCurrentObservation,
    ScopedIntent: RawScopedIntent,
}
_LAYOUT = [
    (0,RawScopedState),
    (1,RawScopeFrame),
    (2,RawPhysicalKey),
    (3,RawPhysicalBucket),
    (4,RawPhysicalProjection),
    (5,RawCurrentObservation),
    (6,RawScopedIntent),
    (7,RawScopedPacket),
    (8,L.RawResult),
]
_ROSTERS = (
    ('history',RawScopeFrame,ScopeFrame),
    ('proposed_history',RawScopeFrame,ScopeFrame),
    ('rows',L.RawRow,L.RunRow),
    ('proposed_rows',L.RawRow,L.RunRow),
    ('projection',RawPhysicalProjection,PhysicalProjection),
    ('proposed_projection',RawPhysicalProjection,PhysicalProjection),
    ('buckets',RawPhysicalBucket,PhysicalBucket),
    ('proposed_buckets',RawPhysicalBucket,PhysicalBucket),
    ('actual_buckets',RawPhysicalBucket,PhysicalBucket),
    ('observed',L.RawNative,L.RunObservation),
    ('facts',O.RawFacts,O.PhysicalFacts),
)


def _facts(value,arena):
    if type(value) is not O.PhysicalFacts:raise ValueError('complete original physical facts required')
    raw=O.RawFacts()
    for name,typ in raw._fields_:
        datum=getattr(value,name)
        if typ is L.RawId:encoded=L._id(datum,arena)
        elif typ is L.RawEpoch:encoded=L._epoch(datum,arena)
        elif typ is L.RawContext:encoded=L._marshal('Context',datum,arena)
        elif typ is L.RawBinding:encoded=L._marshal('Binding',datum,arena)
        else:
            if datum not in O.JOURNAL_PHASE:raise ValueError('original physical phase differs')
            encoded=O.JOURNAL_PHASE.index(datum)
        setattr(raw,name,encoded)
    return raw


def _marshal(value,arena):
    typ=_RECORDS.get(type(value))
    if typ is None:raise ValueError('complete scoped typed record required')
    raw=typ()
    for name,kind in raw._fields_:
        datum=getattr(value,name)
        if kind is L.RawId:encoded=L._id(datum,arena)
        elif kind is L.RawEpoch:encoded=L._epoch(datum,arena)
        elif kind is L.RawQuantity:encoded=L._quantity(datum,arena)
        elif kind is L.RawContext:encoded=L._marshal('Context',datum,arena)
        elif kind is L.RawBinding:encoded=L._marshal('Binding',datum,arena)
        elif kind is L.RawRequest:encoded=L._marshal('Request',datum,arena)
        elif kind is RawPhysicalKey:encoded=_marshal(datum,arena)
        else:
            if datum not in SCOPED_ACTIONS:raise ValueError('scoped action differs')
            encoded=SCOPED_ACTIONS.index(datum)
        setattr(raw,name,encoded)
    return raw


class ScopedRunLedgerKernel:
    """Actual selected library only; full copied packet/rosters precede output."""
    def __init__(self,core):
        self.base=O.ResourceObservationKernel(core)
        try:
            version=core._lib.wl_resource_scoped_run_ledger_version_v1
            layout=core._lib.wl_resource_scoped_run_ledger_layout_v1
            self.call=core._lib.wl_resource_scoped_run_ledger_check_v1
            self.validate_call=core._lib.wl_resource_scoped_run_ledger_validate_v1
            self.classify_call=core._lib.wl_resource_scoped_run_ledger_classify_v1
        except AttributeError as error:
            raise CoreUnavailable('full scoped resource native ABI unavailable') from error
        version.argtypes,version.restype=[],C.c_uint32
        layout.argtypes,layout.restype=[C.c_uint32,C.c_uint32],C.c_long
        if version()!=1:raise CoreUnavailable('scoped resource native version differs')
        for kind,typ in _LAYOUT:
            if layout(kind,0)!=C.sizeof(typ) or layout(kind,1)!=C.alignment(typ):
                raise CoreUnavailable('scoped resource native layout differs')
            for selector,(name,_kind) in enumerate(typ._fields_,2):
                if layout(kind,selector)!=getattr(typ,name).offset:
                    raise CoreUnavailable('scoped resource native field differs',field=name)
        self.call.argtypes=[C.c_void_p,C.c_size_t]*(len(_ROSTERS)+3)
        self.call.restype=C.c_int
        self.validate_call.argtypes=self.call.argtypes
        self.validate_call.restype=C.c_int
        self.classify_call.argtypes=self.call.argtypes
        self.classify_call.restype=C.c_int

    def prepare(self,packet):
        if type(packet) is not ScopedPacket:raise ValueError('complete scoped packet required')
        arena=bytearray()
        raw=RawScopedPacket(1,_marshal(packet.before,arena),_marshal(packet.proposed,arena),
                            _marshal(packet.current,arena),_marshal(packet.request,arena))
        rosters=[]
        for name,raw_type,data_type in _ROSTERS:
            values=getattr(packet,name)
            if type(values) is not tuple or any(type(row) is not data_type for row in values):
                raise ValueError('complete scoped roster required: '+name)
            owned=(raw_type*len(values))()
            for index,row in enumerate(values):
                if data_type is O.PhysicalFacts:value=_facts(row,arena)
                elif data_type in (L.RunRow,L.RunObservation):
                    value=L._marshal('Row' if data_type is L.RunRow else 'Native',row,arena)
                else:value=_marshal(row,arena)
                owned[index]=value
            rosters.append((name,owned,len(values)))
        data=(C.c_uint8*max(1,len(arena)))()
        if arena:C.memmove(data,bytes(arena),len(arena))
        return raw,data,len(arena),tuple(rosters)

    def decide(self,packet):
        return self._invoke(packet,self.call,SCOPED_STATUSES,'wl_resource_scoped_run_ledger_check_v1')

    def classify(self,packet):
        return self._invoke(packet,self.classify_call,L.LIVENESS,
            'wl_resource_scoped_run_ledger_classify_v1')

    def validate(self,packet):
        return self._invoke(packet,self.validate_call,('INVALID_SNAPSHOT','CONSISTENT_SNAPSHOT'),
                            'wl_resource_scoped_run_ledger_validate_v1')

    def _invoke(self,packet,entry,statuses,name):
        raw,arena,length,rosters=self.prepare(packet)
        result=L.RawResult()
        arguments=[C.byref(raw),C.sizeof(raw),arena,L._extent(length)]
        for _name,owned,count in rosters:arguments.extend((owned,L._extent(count)))
        arguments.extend((C.byref(result),C.sizeof(result)))
        transport=entry(*arguments)
        if transport!=0:raise CoreUnavailable('scoped resource native transport refused')
        if result.status>=len(statuses):raise CoreUnavailable('scoped resource native output malformed')
        # Complete owned raw records are retained for actual native redecision.
        # This record is evidence data, never protected custody by itself.
        return ScopedNativeDecision(name,statuses[result.status],bytes(raw),
            bytes(arena)[:length],tuple((name,bytes(owned),count) for name,owned,count in rosters),
            bytes(result),transport)

# Complete declared owned-schema framing only; public arbitrary-value encoders
# and their callback/probe semantics are untouched. These tags confer no authority.
_KNOWN={typ.__name__:typ for typ in (*_RECORDS,ScopedPacket,ScopedNativeDecision,
    L.RunContext,L.RunBinding,L.RunRow,L.RunState,L.RunObservation,L.RunRequest,O.PhysicalFacts)}


def record(value):
    kind=type(value)
    if kind in _KNOWN.values():
        return {'type':kind.__name__,'fields':{field.name:record(getattr(value,field.name)) for field in fields(value)}}
    if kind is bytes:return {'type':'bytes','value':value.hex()}
    if kind is float:
        import struct
        return {'type':'float','bits':struct.pack('!d',value).hex()}
    if kind is int:
        magnitude=abs(value)
        return {'type':'integer','negative':value<0,
            'magnitude':magnitude.to_bytes((magnitude.bit_length()+7)//8,'little').hex()}
    if kind in (str,bool) or value is None:return {'type':kind.__name__,'value':value}
    if kind in (tuple,list):return {'type':kind.__name__,'items':[record(item) for item in value]}
    if kind is dict:
        if any(type(key) is not str for key in value):raise ValueError('scoped record keys must be exact strings')
        return {'type':'dict','fields':{key:record(item) for key,item in value.items()}}
    raise ValueError('complete declared scoped source record required')


def restore(value):
    if type(value) is not dict or type(value.get('type')) is not str:
        raise ValueError('complete scoped source record required')
    name=value['type']
    if name in _KNOWN:
        typ=_KNOWN[name]
        if set(value)!={'type','fields'} or type(value['fields']) is not dict or set(value['fields'])!={field.name for field in fields(typ)}:
            raise ValueError('complete scoped record fields required')
        return typ(**{key:restore(item) for key,item in value['fields'].items()})
    if name=='bytes':
        if set(value)!={'type','value'} or type(value['value']) is not str:raise ValueError('scoped complete bytes required')
        raw=bytes.fromhex(value['value'])
        if raw.hex()!=value['value']:raise ValueError('scoped byte representation differs')
        return raw
    if name=='float':
        import struct
        if set(value)!={'type','bits'} or type(value['bits']) is not str:
            raise ValueError('scoped complete float bits required')
        raw=bytes.fromhex(value['bits'])
        if raw.hex()!=value['bits'] or len(raw)!=struct.calcsize('!d'):
            raise ValueError('scoped float representation differs')
        return struct.unpack('!d',raw)[0]
    if name=='integer':
        if set(value)!={'type','negative','magnitude'} or type(value['negative']) is not bool or type(value['magnitude']) is not str:
            raise ValueError('scoped complete integer magnitude required')
        raw=bytes.fromhex(value['magnitude'])
        if raw.hex()!=value['magnitude']:raise ValueError('scoped integer representation differs')
        magnitude=int.from_bytes(raw,'little')
        return -magnitude if value['negative'] else magnitude
    if name in ('str','bool','NoneType'):
        if set(value)!={'type','value'} or type(value['value']).__name__!=name:raise ValueError('scoped atom type differs')
        return value['value']
    if name in ('tuple','list'):
        if set(value)!={'type','items'} or type(value['items']) is not list:raise ValueError('scoped complete roster required')
        items=[restore(item) for item in value['items']]
        return tuple(items) if name=='tuple' else items
    if name=='dict':
        if set(value)!={'type','fields'} or type(value['fields']) is not dict or any(type(key) is not str for key in value['fields']):
            raise ValueError('scoped complete mapping required')
        return {key:restore(item) for key,item in value['fields'].items()}
    raise ValueError('unknown scoped source record type')
