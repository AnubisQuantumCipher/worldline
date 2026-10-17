"""Complete SQL-cell producer envelope; native X4/X5 owns all decisions."""
from __future__ import annotations
import ctypes as C
from dataclasses import dataclass
from .errors import CoreUnavailable
from .protected_startup import require
from .root_worker_codec import scoped_archive as archive
from .retained_chain_kernel import _mapped

@dataclass(frozen=True)
class LoadObservation:
    status: int
    position: int
    envelope: bytes
    @property
    def state(self):
        from .custody_native_status import name
        return name(self.status)

def invoke(native, envelope):
    require(type(envelope) is bytes, 'CUSTODY_LOAD_OWNED_ENVELOPE_REQUIRED')
    require(C.c_size_t(len(envelope)).value == len(envelope), 'CUSTODY_LOAD_HOST_EXTENT')
    try:
        function = native.wl_custody_load_decide_v2
    except AttributeError as error:
        raise CoreUnavailable('native full custody-v2 loader unavailable') from error
    function.argtypes = [C.c_void_p, C.c_size_t, C.POINTER(C.c_uint64), C.POINTER(C.c_uint64)]
    function.restype = C.c_int
    data = (C.c_ubyte * len(envelope)).from_buffer_copy(envelope)
    status = C.c_uint64(); position = C.c_uint64()
    code = function(data, len(envelope), C.byref(status), C.byref(position))
    if code != 0: raise CoreUnavailable('native custody-v2 load transport refused')
    return LoadObservation(status.value, position.value, envelope)

def decide_journal(journal, envelope):
    from .root_worker_journal_v2 import RootCustodyJournalV2
    require(type(journal) is RootCustodyJournalV2, 'CUSTODY_LOAD_REAL_JOURNAL_REQUIRED')
    journal.intact()
    try: function = journal.core._lib.wl_custody_load_decide_v2
    except AttributeError as error: raise CoreUnavailable('native full custody-v2 loader unavailable') from error
    _mapped(journal, journal.core, (function,))
    result = invoke(journal.core._lib, envelope)
    _mapped(journal, journal.core, (function,))
    journal.intact()
    return result

def envelope(key, genesis_raw, genesis_row, genesis_mac, owner_roster, rows, genesis):
    require(type(key) is bytes and type(genesis_raw) is bytes and type(genesis_row) is bytes
            and type(genesis_mac) is str, 'CUSTODY_LOAD_ORIGINAL_GENESIS_CELLS_REQUIRED')
    require(set(rows) == {'events', 'heads', 'roots', 'subjects', 'alternatives', 'blobs'},
            'CUSTODY_LOAD_FULL_TABLE_SET_REQUIRED')
    return archive({'schema': 'worldline.custody-load-v2', 'key': key,
                    'genesis_file': genesis_raw, 'genesis_row': genesis_row,
                    'genesis_message': archive({'genesis': genesis}), 'genesis_mac': genesis_mac,
                    'owner_roster': owner_roster, **rows})
