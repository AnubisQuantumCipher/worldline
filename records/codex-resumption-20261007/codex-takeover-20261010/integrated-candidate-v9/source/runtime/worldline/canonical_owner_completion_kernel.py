"""Complete historical K4 input redecision; no verdict-as-authority fallback.

Both original and current full frames/rosters share one owned magnitude arena.
The original native dual observation is redecided at its retained intent; fresh
denial never causes another exchange, grant or capability use. Protected journal,
actual source mapping and genuine resource terminal custody remain mandatory.
"""
import ctypes as C
from .canonical_exchange_kernel import CanonicalExchangeKernel,Input as ExchangeInput
from .operation_authority_kernel import OperationAuthorityKernel,Input as AuthorityInput,Arena
from .errors import CoreUnavailable

DECISIONS=('REFUSED','RESOLVED_EFFECT','RESOLVED_NO_EFFECT','EFFECT_ALREADY','NO_EFFECT_ALREADY')
class Input(C.Structure):
    _fields_=[('historical',ExchangeInput),('current',AuthorityInput)]
class Result(C.Structure):
    _fields_=[('disposition',C.c_uint8)]

class CanonicalOwnerCompletionKernel:
    def __init__(self,core):
        self.exchange=CanonicalExchangeKernel(core)
        self.authority=OperationAuthorityKernel(core)
        try:
            version=core._lib.wl_canonical_owner_completion_version_v1
            layout=core._lib.wl_canonical_owner_completion_layout_v1
            self.call=core._lib.wl_canonical_owner_completion_decide_v1
        except AttributeError as exc:
            raise CoreUnavailable('full historical owner completion unavailable') from exc
        version.argtypes,version.restype=[],C.c_uint32
        layout.argtypes,layout.restype=[C.c_uint32,C.c_uint32],C.c_long
        if version()!=1:raise CoreUnavailable('historical owner ABI version differs')
        for kind,typ in enumerate((Input,Result),1):
            if layout(kind,0)!=C.sizeof(typ) or layout(kind,1)!=C.alignment(typ):
                raise CoreUnavailable('historical owner ABI size/alignment differs')
            for field,(name,_type) in enumerate(typ._fields_,2):
                if layout(kind,field)!=getattr(typ,name).offset:
                    raise CoreUnavailable('historical owner ABI offset differs')
        roster_types=self.exchange.call.argtypes[4:-2]+self.authority.call.argtypes[4:-2]
        self.call.argtypes=[C.c_void_p,C.c_size_t,C.c_void_p,C.c_size_t]+roster_types+[C.c_void_p,C.c_size_t]
        self.call.restype=C.c_int
    def observe(self,historical_arguments,current_snapshot):
        arena=Arena()
        historical,arena,_storage,original_rosters=self.exchange.prepare(*historical_arguments,arena=arena)
        current,arena,current_rosters=self.authority.prepare(current_snapshot,'REPLAY_USE',arena=arena)
        raw=Input(historical,current)
        storage=(C.c_uint8*len(arena.raw)).from_buffer_copy(arena.raw)
        result=Result();rosters=(*original_rosters,*current_rosters)
        argv=[C.byref(raw),C.sizeof(raw),storage,len(arena.raw)]
        for roster in rosters:argv.extend((roster,len(roster),C.sizeof(roster)))
        argv.extend((C.byref(result),C.sizeof(result)))
        if self.call(*argv)!=0 or result.disposition>=len(DECISIONS):
            raise CoreUnavailable('historical owner complete transport refused')
        return {'decision':DECISIONS[result.disposition],
            'input':C.string_at(C.byref(raw),C.sizeof(raw)).hex(),
            'arena':bytes(arena.raw).hex(),
            'rosters':[C.string_at(item,C.sizeof(item)).hex() for item in rosters],
            'output':C.string_at(C.byref(result),C.sizeof(result)).hex()}
