"""Fresh native closed owner correspondence; no event or effect is granted."""
import ctypes as C
from enum import IntEnum
from .protected_startup import require
from .retained_chain_kernel import _mapped


class ClosedOwnerDecision(IntEnum):
    EVIDENCE_REFUSED = 0
    EVIDENCE_JOINED = 1


def decide_closed_owner(journal, raw):
    function = journal.core._lib.wl_custody_closed_decide_v2
    function.argtypes = [C.c_void_p, C.c_size_t, C.POINTER(C.c_uint64), C.POINTER(C.c_uint64)]
    function.restype = C.c_int
    _mapped(journal, journal.core, (function,))
    source = (C.c_ubyte * len(raw)).from_buffer_copy(raw)
    status = C.c_uint64()
    position = C.c_uint64()
    require(function(source, len(raw), C.byref(status), C.byref(position)) == 0,
            'CUSTODY_CLOSED_NATIVE_TRANSPORT_REFUSED')
    first = status.value, position.value
    require(function(source, len(raw), C.byref(status), C.byref(position)) == 0
            and first == (status.value, position.value), 'CUSTODY_CLOSED_NATIVE_CHANGED')
    _mapped(journal, journal.core, (function,))
    require(status.value == ClosedOwnerDecision.EVIDENCE_JOINED,
            'CUSTODY_CLOSED_NATIVE_REFUSED_' + str(status.value) + '_' + str(position.value))
    return ClosedOwnerDecision(status.value)
