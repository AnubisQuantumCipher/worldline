"""Full interpreted result relation before and after canonical effect writes.

The existing expanded operation transport owns all layouts and raw packing.
This entry neither issues a capability use nor chooses an exchange or handler.
"""
from __future__ import annotations
import ctypes as C
from .errors import CoreUnavailable
from .operation_authority_kernel import OperationAuthorityKernel, Result
REASONS = ('READY', 'OPERATION_ORIGINAL_CAPTURE_NATIVE_REFUSED',
           'OPERATION_RESULT_CANONICAL_MATERIAL_CHANGED',
           'OPERATION_RESULT_CAUSAL_RELATION_NATIVE_REFUSED',
           'OPERATION_SAME_USE_RECORD_CHANGED', 'OPERATION_ORIGINAL_FULL_CHAIN_NATIVE_REFUSED')

class OperationResultRelation:
    def __init__(self, core):
        self.authority = OperationAuthorityKernel(core)
        try:
            self.call = core._lib.wl_operation_result_relation_v1
        except AttributeError as exc:
            raise CoreUnavailable('complete native canonical result relation unavailable') from exc
        self.call.argtypes = [C.c_void_p, C.c_size_t, C.c_void_p, C.c_size_t] + [C.c_void_p, C.c_size_t, C.c_size_t] * 4 + [C.c_void_p, C.c_size_t]
        self.call.restype = C.c_int

    def observe(self, snapshot):
        request, arena, arrays = self.authority.prepare(snapshot, 'OBSERVE_EFFECT')
        raw = (C.c_uint8 * len(arena.raw)).from_buffer_copy(arena.raw)
        result = Result()
        args = [C.byref(request), C.sizeof(request), raw, len(arena.raw)]
        for array in arrays:
            args.extend((array, len(array), C.sizeof(array)))
        args.extend((C.byref(result), C.sizeof(result)))
        if self.call(*args) != 0 or result.disposition >= len(REASONS):
            raise CoreUnavailable('complete native canonical result relation transport refused')
        return {'decision': REASONS[result.disposition],
                'input': C.string_at(C.byref(request), C.sizeof(request)).hex(),
                'arena': bytes(arena.raw).hex(),
                'rosters': [C.string_at(a, C.sizeof(a)).hex() for a in arrays],
                'output': C.string_at(C.byref(result), C.sizeof(result)).hex()}
