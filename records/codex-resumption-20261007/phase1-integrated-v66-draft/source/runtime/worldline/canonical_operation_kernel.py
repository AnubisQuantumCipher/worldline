"""Owned complete native pre-effect conjunction; no Python authority fallback."""
import ctypes as C
from .operation_authority_kernel import OperationAuthorityKernel,Arena,Input,UID,uid
from . import resource_run_ledger as L
from .core import CCollapseRequest
from .errors import CoreUnavailable
DECISIONS=('AUTHORITY_REFUSED','RESOURCE_REFUSED','BINDING_MISMATCH','COLLAPSE_REFUSED','READY')
class RawInput(C.Structure):
    _fields_=[('authority',Input),('state',L.RawState),('bound',L.RawBinding),
              ('requester',L.RawId),('peer',UID),('collapse',CCollapseRequest)]
class RawResult(C.Structure):_fields_=[('disposition',C.c_uint8)]
class CanonicalOperationKernel:
    def __init__(self,core):
        self.core=core;self.authority=OperationAuthorityKernel(core);L.ResourceRunLedgerKernel(core)
        try:
            version=core._lib.wl_canonical_operation_version_v1;layout=core._lib.wl_canonical_operation_layout_v1
            self.call=core._lib.wl_canonical_operation_decide_v1
        except AttributeError as exc:raise CoreUnavailable('canonical complete authority conjunction unavailable') from exc
        version.argtypes,version.restype=[],C.c_uint32
        layout.argtypes,layout.restype=[C.c_uint32,C.c_uint32],C.c_long
        if version()!=1:raise CoreUnavailable('canonical authority ABI version differs')
        for kind,typ in enumerate((RawInput,RawResult),1):
            if layout(kind,0)!=C.sizeof(typ) or layout(kind,1)!=C.alignment(typ):raise CoreUnavailable('canonical authority size/alignment differs')
            for field,(name,_typ) in enumerate(typ._fields_,2):
                if layout(kind,field)!=getattr(typ,name).offset:raise CoreUnavailable('canonical authority offset differs')
        self.call.argtypes=[C.c_void_p,C.c_size_t,C.c_void_p,C.c_size_t]+[C.c_void_p,C.c_size_t,C.c_size_t]*4+[C.c_void_p,C.c_size_t]
        self.call.restype=C.c_int
    def observe(self,snapshot,state,rows,observed,request,peer_uid,collapse_values):
        if type(rows) is not tuple or type(observed) is not tuple:raise ValueError('complete immutable rosters required')
        arena=Arena();authority,arena,arrays=self.authority.prepare(snapshot,'RESERVE_USE',arena=arena)
        if len(arrays[2]) or len(arrays[3]):raise ValueError('fresh operation has no asserted effect chain')
        raw=RawInput(authority,L._marshal('State',state,arena.raw),L._marshal('Binding',request.bound,arena.raw),
            L._id(request.requester,arena.raw),uid(peer_uid),CCollapseRequest() if collapse_values is None else self.core._raw_collapse_request(collapse_values))
        native_rows=(L.RawRow*len(rows))(*(L._marshal('Row',row,arena.raw) for row in rows))
        native_observed=(L.RawNative*len(observed))(*(L._marshal('Native',row,arena.raw) for row in observed))
        raw_arena=(C.c_uint8*len(arena.raw)).from_buffer_copy(arena.raw);result=RawResult()
        rosters=(arrays[0],arrays[1],native_rows,native_observed)
        args=[C.byref(raw),C.sizeof(raw),raw_arena,len(arena.raw)]
        for roster in rosters:args.extend((roster,len(roster),C.sizeof(roster)))
        args.extend((C.byref(result),C.sizeof(result)))
        if self.call(*args)!=0 or result.disposition>=len(DECISIONS):raise CoreUnavailable('canonical authority owned transport refused')
        return {'decision':DECISIONS[result.disposition],'input':C.string_at(C.byref(raw),C.sizeof(raw)).hex(),
            'arena':bytes(arena.raw).hex(),'rosters':[C.string_at(value,C.sizeof(value)).hex() for value in rosters],
            'output':C.string_at(C.byref(result),C.sizeof(result)).hex()}
