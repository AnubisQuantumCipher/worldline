"""Faithful owned caller for protocol order; supplies no observation authority."""
import ctypes as C
from .errors import CoreUnavailable
STATES=('ISSUED','EFFECT_INTENT','EFFECT_OBSERVED','SETTLED','ABORTED','QUARANTINED')
EVENTS=('FRESH_CLAIM','HISTORICAL_EFFECT','SETTLEMENT_COMPLETE','NO_EFFECT_RELEASED',
        'UNKNOWN_OBSERVATION','OWNER_EFFECT_RESOLUTION','OWNER_NO_EFFECT_RESOLUTION','REPLAY')
class Request(C.Structure):
    _fields_=[('before',C.c_uint8),('cause',C.c_uint8)]
class Result(C.Structure):
    _fields_=[('after',C.c_uint8)]
class RecoveryProtocolKernel:
    def __init__(self,core):
        try:
            version=core._lib.wl_recovery_protocol_version_v1
            layout=core._lib.wl_recovery_protocol_layout_v1
            self.call=core._lib.wl_recovery_protocol_decide_v1
        except AttributeError as exc:
            raise CoreUnavailable('protected recovery protocol ABI unavailable') from exc
        version.argtypes,version.restype=[],C.c_uint32
        layout.argtypes,layout.restype=[C.c_uint32,C.c_uint32],C.c_long
        if version()!=1: raise CoreUnavailable('protected recovery protocol ABI version differs')
        for kind,typ in enumerate((Request,Result),1):
            if layout(kind,0)!=C.sizeof(typ) or layout(kind,1)!=C.alignment(typ):
                raise CoreUnavailable('protected recovery protocol layout differs')
            for field,(name,_type) in enumerate(typ._fields_,2):
                if layout(kind,field)!=getattr(typ,name).offset:
                    raise CoreUnavailable('protected recovery protocol offset differs')
        self.call.argtypes=[C.c_void_p,C.c_size_t,C.c_void_p,C.c_size_t]
        self.call.restype=C.c_int
    def advance(self,before,cause):
        if type(before) is not str or before not in STATES or type(cause) is not str or cause not in EVENTS:
            raise ValueError('noncanonical protected recovery protocol category')
        request=Request(STATES.index(before),EVENTS.index(cause)); result=Result()
        if self.call(C.byref(request),C.sizeof(request),C.byref(result),C.sizeof(result))!=0:
            raise CoreUnavailable('protected recovery protocol transport refused')
        if result.after>=len(STATES): raise CoreUnavailable('protected recovery protocol output differs')
        return STATES[result.after]
