"""Owned full-ledger ABI transport. It makes no Python numerical authorization.

Every quantity and epoch is a complete signed little-endian magnitude. Typed
absence is independent. This caller requires matching native decision/layout
symbols and refuses missing native support; there is no selected-row fallback.
"""
from __future__ import annotations
import ctypes as C
from dataclasses import dataclass,fields
from .errors import CoreUnavailable

CHARGE_KIND = ('HELD_CAPACITY', 'IRREVERSIBLE_BUDGET')
PHASE = ('RESERVED', 'LAUNCH_INTENT', 'RUNNING', 'TERMINATING', 'TERMINAL', 'SETTLEMENT_UNKNOWN', 'RELEASED', 'CHARGED')
LIVENESS = ('UNKNOWN', 'LIVE', 'REAPED', 'NEVER_LAUNCHED')
OPERATION = ('UNKNOWN_OPERATION', 'RESERVE', 'RECORD_LAUNCH_INTENT', 'RECORD_RUNNING', 'RECORD_TERMINATING', 'RECORD_TERMINAL', 'RETAIN_UNCERTAIN', 'RELEASE_HOLD', 'CHARGE_BUDGET')
STATUS = ('READY', 'UNKNOWN_KIND', 'INVALID_BEFORE', 'INVALID_PROPOSED', 'NATIVE_ROSTER_INVALID', 'REQUEST_INVALID', 'STALE_EPOCH', 'LEDGER_HEAD_MISMATCH', 'CONTEXT_CHANGED', 'EPOCH_NOT_SUCCESSOR', 'HISTORICAL_ROW_REMOVED', 'HISTORICAL_ROW_CHANGED', 'DUPLICATE_RESERVATION', 'WRONG_OWNER', 'OPERATION_MISMATCH', 'ILLEGAL_LIFECYCLE', 'NATIVE_NOT_ESTABLISHED', 'PARENT_INVALID', 'CONSERVATION_MISMATCH', 'CAPACITY_EXCEEDED')

@dataclass(frozen=True,slots=True,kw_only=True)
class RunContext:
    universe: bytes | None
    policy: bytes | None
    resource: bytes | None
    unit: bytes | None
    instance: bytes | None
    host: bytes | None
    boot: bytes | None
    authority: bytes | None
    policy_epoch: int | None

@dataclass(frozen=True,slots=True,kw_only=True)
class RunBinding:
    reservation: bytes | None
    operation: bytes | None
    owner: bytes | None
    workload: bytes | None
    universe_head: bytes | None
    capability: bytes | None
    grant_use: bytes | None
    payload: bytes | None
    provenance: bytes | None
    resource_epoch: int | None

@dataclass(frozen=True,slots=True,kw_only=True)
class RunRow:
    scope: RunContext
    bound: RunBinding
    parent: bytes | None
    kind: str
    state: str
    amount: int
    observed_usage: int | None
    planned_unit: bytes | None
    actual_unit: bytes | None
    cgroup: bytes | None
    invocation: bytes | None

@dataclass(frozen=True,slots=True,kw_only=True)
class RunState:
    scope: RunContext
    resource_epoch: int | None
    universe_head: bytes | None
    ledger_head: bytes | None
    capacity: int
    held_total: int
    charged_total: int

@dataclass(frozen=True,slots=True,kw_only=True)
class RunObservation:
    scope: RunContext
    resource_epoch: int | None
    bound: RunBinding
    actual_unit: bytes | None
    cgroup: bytes | None
    invocation: bytes | None
    observation_head: bytes | None
    observed: str

@dataclass(frozen=True,slots=True,kw_only=True)
class RunRequest:
    kind: str
    scope: RunContext
    expected_epoch: int | None
    expected_ledger_head: bytes | None
    request_id: bytes | None
    reservation: bytes | None
    operation_id: bytes | None
    requester: bytes | None
    bound: RunBinding
    new_row: RunRow | None

class RawId(C.Structure):
    _fields_ = [('present', C.c_uint8), ('first', C.c_int64), ('length', C.c_int64)]

class RawQuantity(C.Structure):
    _fields_ = [('negative', C.c_uint8), ('first', C.c_int64), ('length', C.c_int64)]

class RawEpoch(C.Structure):
    _fields_ = [('present', C.c_uint8), ('value', RawQuantity)]

class RawContext(C.Structure):
    _fields_ = [('universe', RawId), ('policy', RawId), ('resource', RawId), ('unit', RawId), ('instance', RawId), ('host', RawId), ('boot', RawId), ('authority', RawId), ('policy_epoch', RawEpoch)]

class RawBinding(C.Structure):
    _fields_ = [('reservation', RawId), ('operation', RawId), ('owner', RawId), ('workload', RawId), ('universe_head', RawId), ('capability', RawId), ('grant_use', RawId), ('payload', RawId), ('provenance', RawId), ('resource_epoch', RawEpoch)]

class RawRow(C.Structure):
    _fields_ = [('scope', RawContext), ('bound', RawBinding), ('parent', RawId), ('kind', C.c_uint8), ('state', C.c_uint8), ('amount', RawQuantity), ('observed_usage', RawEpoch), ('planned_unit', RawId), ('actual_unit', RawId), ('cgroup', RawId), ('invocation', RawId)]

class RawState(C.Structure):
    _fields_ = [('scope', RawContext), ('resource_epoch', RawEpoch), ('universe_head', RawId), ('ledger_head', RawId), ('capacity', RawQuantity), ('held_total', RawQuantity), ('charged_total', RawQuantity)]

class RawNative(C.Structure):
    _fields_ = [('scope', RawContext), ('resource_epoch', RawEpoch), ('bound', RawBinding), ('actual_unit', RawId), ('cgroup', RawId), ('invocation', RawId), ('observation_head', RawId), ('observed', C.c_uint8)]

class RawRequest(C.Structure):
    _fields_ = [('kind', C.c_uint8), ('scope', RawContext), ('expected_epoch', RawEpoch), ('expected_ledger_head', RawId), ('request_id', RawId), ('reservation', RawId), ('operation_id', RawId), ('requester', RawId), ('bound', RawBinding), ('new_row', RawRow)]

class RawPacket(C.Structure):
    _fields_ = [('schema_version', C.c_uint32), ('before_state', RawState), ('proposed_state', RawState), ('intent', RawRequest)]

class RawResult(C.Structure):
    _fields_ = [('status', C.c_uint32)]

@dataclass(frozen=True,slots=True)
class OwnedPacket:
    packet: RawPacket
    arena: C.Array
    arena_length: int
    before_rows: C.Array
    proposed_rows: C.Array
    native: C.Array

_ID_NAMES = {'Id': (), 'Quantity': (), 'Epoch': (), 'Context': ('universe', 'policy', 'resource', 'unit', 'instance', 'host', 'boot', 'authority'), 'Binding': ('reservation', 'operation', 'owner', 'workload', 'universe_head', 'capability', 'grant_use', 'payload', 'provenance'), 'Row': ('parent', 'planned_unit', 'actual_unit', 'cgroup', 'invocation'), 'State': ('universe_head', 'ledger_head'), 'Native': ('actual_unit', 'cgroup', 'invocation', 'observation_head'), 'Request': ('expected_ledger_head', 'request_id', 'reservation', 'operation_id', 'requester'), 'Packet': (), 'Result': ()}
_QUANTITY_NAMES = frozenset(('policy_epoch','resource_epoch','expected_epoch','amount','observed_usage','capacity','held_total','charged_total'))
_ENUM_FIELDS = {('Row','kind'):CHARGE_KIND,('Row','state'):PHASE,
                ('Native','observed'):LIVENESS,('Request','kind'):OPERATION}
_DTO = {'Context': 'RunContext', 'Binding': 'RunBinding', 'Row': 'RunRow', 'State': 'RunState', 'Native': 'RunObservation', 'Request': 'RunRequest'}
_DTO = {name:globals()[cls] for name,cls in _DTO.items()}
_RAW = {'Id': 'RawId', 'Quantity': 'RawQuantity', 'Epoch': 'RawEpoch', 'Context': 'RawContext', 'Binding': 'RawBinding', 'Row': 'RawRow', 'State': 'RawState', 'Native': 'RawNative', 'Request': 'RawRequest', 'Packet': 'RawPacket', 'Result': 'RawResult'}
_RAW = {name:globals()[cls] for name,cls in _RAW.items()}
_SCHEMA = {'Id': (('present', 'U8'), ('first', 'I64'), ('length', 'I64')), 'Quantity': (('negative', 'U8'), ('first', 'I64'), ('length', 'I64')), 'Epoch': (('present', 'U8'), ('value', 'Raw_Quantity')), 'Context': (('universe', 'Raw_Id'), ('policy', 'Raw_Id'), ('resource', 'Raw_Id'), ('unit', 'Raw_Id'), ('instance', 'Raw_Id'), ('host', 'Raw_Id'), ('boot', 'Raw_Id'), ('authority', 'Raw_Id'), ('policy_epoch', 'Raw_Epoch')), 'Binding': (('reservation', 'Raw_Id'), ('operation', 'Raw_Id'), ('owner', 'Raw_Id'), ('workload', 'Raw_Id'), ('universe_head', 'Raw_Id'), ('capability', 'Raw_Id'), ('grant_use', 'Raw_Id'), ('payload', 'Raw_Id'), ('provenance', 'Raw_Id'), ('resource_epoch', 'Raw_Epoch')), 'Row': (('scope', 'Raw_Context'), ('bound', 'Raw_Binding'), ('parent', 'Raw_Id'), ('kind', 'U8'), ('state', 'U8'), ('amount', 'Raw_Quantity'), ('observed_usage', 'Raw_Epoch'), ('planned_unit', 'Raw_Id'), ('actual_unit', 'Raw_Id'), ('cgroup', 'Raw_Id'), ('invocation', 'Raw_Id')), 'State': (('scope', 'Raw_Context'), ('resource_epoch', 'Raw_Epoch'), ('universe_head', 'Raw_Id'), ('ledger_head', 'Raw_Id'), ('capacity', 'Raw_Quantity'), ('held_total', 'Raw_Quantity'), ('charged_total', 'Raw_Quantity')), 'Native': (('scope', 'Raw_Context'), ('resource_epoch', 'Raw_Epoch'), ('bound', 'Raw_Binding'), ('actual_unit', 'Raw_Id'), ('cgroup', 'Raw_Id'), ('invocation', 'Raw_Id'), ('observation_head', 'Raw_Id'), ('observed', 'U8')), 'Request': (('kind', 'U8'), ('scope', 'Raw_Context'), ('expected_epoch', 'Raw_Epoch'), ('expected_ledger_head', 'Raw_Id'), ('request_id', 'Raw_Id'), ('reservation', 'Raw_Id'), ('operation_id', 'Raw_Id'), ('requester', 'Raw_Id'), ('bound', 'Raw_Binding'), ('new_row', 'Raw_Row')), 'Packet': (('schema_version', 'U32'), ('before_state', 'Raw_State'), ('proposed_state', 'Raw_State'), ('intent', 'Raw_Request')), 'Result': (('status', 'U32'),)}

def _extent(value):
    if type(value) is not int or value < 0 or C.c_size_t(value).value != value:
        raise CoreUnavailable('full-ledger storage extent is unavailable')
    return value


def _span(encoded,arena):
    first = len(arena)+1 if encoded else 1
    length = len(encoded)
    if C.c_int64(first).value != first or C.c_int64(length).value != length:
        raise CoreUnavailable('full-ledger span exceeds original host storage range')
    arena.extend(encoded)
    if C.c_int64(len(arena)).value != len(arena):
        raise CoreUnavailable('full-ledger arena exceeds original host storage range')
    return first,length


def _id(value,arena):
    if value is None:return RawId(0,1,0)
    if type(value) is not bytes:raise ValueError('full-ledger identity must be exact bytes or absence')
    first,length=_span(value,arena)
    return RawId(1,first,length)


def _quantity(value,arena):
    if type(value) is not int:raise ValueError('full-ledger quantity must be a builtin integer')
    magnitude=abs(value)
    encoded=magnitude.to_bytes((magnitude.bit_length()+7)//8,'little')
    first,length=_span(encoded,arena)
    return RawQuantity(int(value<0),first,length)


def _epoch(value,arena):
    return RawEpoch(0,RawQuantity(0,1,0)) if value is None else RawEpoch(1,_quantity(value,arena))


def _marshal(name,value,arena):
    if name=='Row' and value is None:return _unused_row()
    if type(value) is not _DTO[name]:raise ValueError('complete typed '+name+' input is required')
    answer=_RAW[name]()
    for field,typ in _SCHEMA[name]:
        datum=getattr(value,field)
        if typ=='Raw_Id':raw=_id(datum,arena)
        elif typ=='Raw_Quantity':raw=_quantity(datum,arena)
        elif typ=='Raw_Epoch':raw=_epoch(datum,arena)
        elif typ.startswith('Raw_'):raw=_marshal(typ[4:],datum,arena)
        else:
            choices=_ENUM_FIELDS[(name,field)]
            if type(datum) is not str or datum not in choices:raise ValueError('unknown full-ledger category')
            raw=choices.index(datum)
        setattr(answer,field,raw)
    return answer


def _unused_row():
    # Canonical absent metadata is still not an authoritative or valid reservation.
    row=RawRow()
    def reset(raw):
        for field,typ in raw._fields_:
            datum=getattr(raw,field)
            if isinstance(datum,(RawId,RawQuantity)):
                datum.first=1
            elif isinstance(datum,C.Structure):reset(datum)
    reset(row)
    return row


class ResourceRunLedgerKernel:
    def __init__(self,core):
        self.core=core
        try:
            version=core._lib.wl_resource_run_ledger_version_v1
            layout=core._lib.wl_resource_run_ledger_layout_v1
            self.call=core._lib.wl_resource_run_ledger_check_v1
        except AttributeError as exc:raise CoreUnavailable('full-ledger kernel API is unavailable') from exc
        version.argtypes,version.restype=[],C.c_uint32
        layout.argtypes,layout.restype=[C.c_uint32,C.c_uint32],C.c_long
        if version()!=1:raise CoreUnavailable('full-ledger ABI version differs')
        for kind,typ in enumerate(_RAW.values(),1):
            if layout(kind,0)!=C.sizeof(typ) or layout(kind,1)!=C.alignment(typ):raise CoreUnavailable('full-ledger layout differs')
            for field,(name,_typ) in enumerate(typ._fields_,2):
                if layout(kind,field)!=getattr(typ,name).offset:raise CoreUnavailable('full-ledger field offset differs',field=name)
        self.call.argtypes=[C.c_void_p,C.c_size_t]*6
        self.call.restype=C.c_int

    def prepare(self,*,before,before_rows,proposed,proposed_rows,observed,request):
        if any(type(rows) is not tuple for rows in (before_rows,proposed_rows,observed)):
            raise ValueError('owned immutable complete row rosters are required')
        arena=bytearray()
        intent=_marshal('Request',request,arena)
        if request.new_row is None:intent.new_row=_unused_row()
        packet=RawPacket(1,_marshal('State',before,arena),_marshal('State',proposed,arena),intent)
        raw_before=(RawRow*len(before_rows))(*(_marshal('Row',row,arena) for row in before_rows))
        raw_proposed=(RawRow*len(proposed_rows))(*(_marshal('Row',row,arena) for row in proposed_rows))
        raw_native=(RawNative*len(observed))(*(_marshal('Native',row,arena) for row in observed))
        owned=(C.c_uint8*max(1,len(arena)))()
        if arena:C.memmove(owned,bytes(arena),len(arena))
        return OwnedPacket(packet,owned,len(arena),raw_before,raw_proposed,raw_native)

    def check(self,**inputs):
        owned=self.prepare(**inputs)
        result=RawResult()
        status=self.call(C.byref(owned.packet),C.sizeof(owned.packet),owned.arena,_extent(owned.arena_length),
            owned.before_rows,_extent(len(owned.before_rows)),owned.proposed_rows,_extent(len(owned.proposed_rows)),
            owned.native,_extent(len(owned.native)),C.byref(result),C.sizeof(result))
        if status!=0:raise CoreUnavailable('full-ledger native transport refused')
        if result.status>=len(STATUS):raise CoreUnavailable('full-ledger native result is malformed')
        return STATUS[result.status]


def dto_record(value):
    if value is None:return None
    if type(value) not in _DTO.values():raise ValueError('full-ledger DTO is required')
    record={'type':type(value).__name__,'schema_version':1}
    for field in fields(value):
        datum=getattr(value,field.name)
        if field.name in _QUANTITY_NAMES:
            if datum is None:record[field.name]=None
            else:
                if type(datum) is not int:raise ValueError('noninteger quantity')
                magnitude=abs(datum)
                record[field.name]={'negative':datum<0,'magnitude':magnitude.to_bytes((magnitude.bit_length()+7)//8,'little').hex()}
        elif type(datum) in _DTO.values():record[field.name]=dto_record(datum)
        elif type(datum) is bytes:record[field.name]={'bytes':datum.hex()}
        elif datum is None or type(datum) is str:record[field.name]=datum
        else:raise ValueError('noncanonical full-ledger DTO field')
    return record


def restore_dto(record):
    if record is None:return None
    if type(record) is not dict or type(record.get('schema_version')) is not int or record['schema_version']!=1:
        raise ValueError('full-ledger DTO schema differs')
    typ=next((typ for typ in _DTO.values() if typ.__name__==record.get('type')),None)
    if typ is None or set(record)!={'type','schema_version'}|{field.name for field in fields(typ)}:
        raise ValueError('full-ledger DTO field roster differs')
    values={}
    def decode_hex(raw):
        if type(raw) is not str or len(raw)%2 or any(ch not in '0123456789abcdef' for ch in raw):raise ValueError('noncanonical hex')
        return bytes.fromhex(raw)
    for field in fields(typ):
        datum=record[field.name]
        if field.name in _QUANTITY_NAMES:
            if datum is None:values[field.name]=None
            else:
                if type(datum) is not dict or set(datum)!={'negative','magnitude'} or type(datum['negative']) is not bool:
                    raise ValueError('quantity schema differs')
                magnitude=decode_hex(datum['magnitude'])
                if magnitude and magnitude[-1]==0:raise ValueError('noncanonical magnitude')
                number=int.from_bytes(magnitude,'little')
                if datum['negative'] and number==0:raise ValueError('serialized signed zero is noncanonical')
                values[field.name]=-number if datum['negative'] else number
        elif type(datum) is dict and set(datum)=={'bytes'}:values[field.name]=decode_hex(datum['bytes'])
        elif type(datum) is dict:values[field.name]=restore_dto(datum)
        elif datum is None or type(datum) is str:values[field.name]=datum
        else:raise ValueError('DTO field encoding differs')
    return typ(**values)
