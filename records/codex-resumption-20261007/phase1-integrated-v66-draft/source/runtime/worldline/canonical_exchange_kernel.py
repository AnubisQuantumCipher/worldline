"""Owned unbounded dual-canonical protocol ABI, no Python decision fallback."""
import ctypes as C
from . import resource_run_ledger as L
from . import recovery_authority_kernel_v3 as RV
from .operation_authority_kernel import OperationAuthorityKernel,Arena,uid,digest,keys
from .canonical_operation_kernel import RawInput as OperationInput,CanonicalOperationKernel
from .chain_authority import _Row
from .core import CCollapseRequest
from .errors import CoreUnavailable
PHASES=('ISSUED','WORKER_INTENT','WORKER_OBSERVED','CANONICAL_INTENT','EFFECT_OBSERVED','SETTLED','ABORTED','QUARANTINED')
MODES=('ADVANCE','SETTLE_HISTORICAL','REPLAY_HISTORICAL','RESOLVE_OWNER')
DECISIONS=('REFUSED','DISPATCH_WORKER','RECORD_WORKER','DISPATCH_CANONICAL','RECORD_EFFECT','SETTLE_SAME_USE','REPLAY_SAME_USE','OWNER_RECORD_ABORT','OWNER_RECORD_EFFECT')
BINDINGS=('worker_issued','worker_recovered','canonical_issued','canonical_recovered')
NATIVES=('worker_native','canonical_native')
DIGESTS=('worker_receipt_genesis','owner_receipt_genesis','worker_receipt_head','worker_causal_genesis','owner_causal_genesis','worker_causal_head','quarantine_head')
class Material(C.Structure):
    _fields_=[(name,RV.Binding) for name in BINDINGS]+[(name,RV.Native) for name in NATIVES]+[(name,RV.OptionalDigest) for name in DIGESTS]
class Input(C.Structure):
    _fields_=[('operation_input',OperationInput),('material',Material),('before',C.c_uint8),('mode',C.c_uint8)]
class Result(C.Structure):_fields_=[('disposition',C.c_uint8)]
class CanonicalExchangeKernel:
    def __init__(self,core):
        self.core=core;self.authority=OperationAuthorityKernel(core)
        CanonicalOperationKernel(core)
        try:
            version=core._lib.wl_canonical_exchange_version_v1
            layout=core._lib.wl_canonical_exchange_layout_v1
            self.call=core._lib.wl_canonical_exchange_decide_v1
        except AttributeError as exc:raise CoreUnavailable('full dual-canonical native protocol unavailable') from exc
        version.argtypes,version.restype=[],C.c_uint32
        layout.argtypes,layout.restype=[C.c_uint32,C.c_uint32],C.c_long
        if version()!=1:raise CoreUnavailable('full canonical protocol version differs')
        for kind,typ in enumerate((Material,Input,Result),1):
            if layout(kind,0)!=C.sizeof(typ) or layout(kind,1)!=C.alignment(typ):raise CoreUnavailable('canonical protocol layout differs')
            for field,(name,_typ) in enumerate(typ._fields_,2):
                if layout(kind,field)!=getattr(typ,name).offset:raise CoreUnavailable('canonical protocol field offset differs')
        self.call.argtypes=[C.c_void_p,C.c_size_t,C.c_void_p,C.c_size_t]+[C.c_void_p,C.c_size_t,C.c_size_t]*8+[C.c_void_p,C.c_size_t]
        self.call.restype=C.c_int
    def prepare(self,snapshot,state,rows,observed,request,peer_uid,collapse_values,material,before,mode,worker_receipts,worker_events,*,arena=None):
        keys(material,(*BINDINGS,*NATIVES,*DIGESTS))
        if before not in PHASES or mode not in MODES:raise ValueError('full protocol phase/command required')
        arena=Arena() if arena is None else arena
        authority,arena,arrays=self.authority.prepare(snapshot,'RESERVE_USE',arena=arena)
        operation=OperationInput(authority,L._marshal('State',state,arena.raw),L._marshal('Binding',request.bound,arena.raw),
            L._id(request.requester,arena.raw),uid(peer_uid),self.core._raw_collapse_request(collapse_values))
        raw_material=Material(*(RV.RecoveryAuthorityKernelV3._binding(material[name],arena.raw) for name in BINDINGS),
            *(RV.RecoveryAuthorityKernelV3._native(material[name]) for name in NATIVES),
            *(digest(material[name]) for name in DIGESTS))
        raw=Input(operation,raw_material,PHASES.index(before),MODES.index(mode))
        raw_rows=(L.RawRow*len(rows))(*(L._marshal('Row',row,arena.raw) for row in rows))
        raw_observed=(L.RawNative*len(observed))(*(L._marshal('Native',row,arena.raw) for row in observed))
        def chain(items):
            answer=[]
            for value in items:
                names=('previous','actual_payload_root','stored_payload_root','stored_head');keys(value,names)
                answer.append(_Row(*(digest(value[name]) for name in names)))
            return (_Row*len(answer))(*answer)
        rosters=(arrays[0],arrays[1],raw_rows,raw_observed,chain(worker_receipts),chain(worker_events),arrays[2],arrays[3])
        storage=(C.c_uint8*len(arena.raw)).from_buffer_copy(arena.raw)
        return raw,arena,storage,rosters
    def observe(self,*args):
        raw,arena,storage,rosters=self.prepare(*args);output=Result()
        argv=[C.byref(raw),C.sizeof(raw),storage,len(arena.raw)]
        for item in rosters:argv.extend((item,len(item),C.sizeof(item)))
        argv.extend((C.byref(output),C.sizeof(output)))
        if self.call(*argv)!=0 or output.disposition>=len(DECISIONS):raise CoreUnavailable('full canonical native transport refused')
        return {'decision':DECISIONS[output.disposition],'input':C.string_at(C.byref(raw),C.sizeof(raw)).hex(),
            'arena':bytes(arena.raw).hex(),'rosters':[C.string_at(item,C.sizeof(item)).hex() for item in rosters],
            'output':C.string_at(C.byref(output),C.sizeof(output)).hex()}
