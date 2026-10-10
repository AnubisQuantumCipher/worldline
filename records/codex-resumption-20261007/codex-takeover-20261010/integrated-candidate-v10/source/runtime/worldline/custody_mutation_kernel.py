"""Native-derived SQL delta transport; Python never implements Legal or Next."""
from __future__ import annotations
import ctypes as C
from dataclasses import dataclass
from .errors import CoreUnavailable
from .protected_startup import require, exact_json
from .root_worker_codec import scoped_archive as archive, scoped_restore_archive as restore_archive
from .retained_chain_kernel import _mapped

@dataclass(frozen=True)
class MutationObservation:
    status: int
    position: int
    delta: object
    inputs: bytes
    @property
    def state(self):
        from .custody_native_status import name
        return name(self.status, mutation=True)

def mutation_input(before, operation, kind, actor, subject_kind, subject, record):
    require(type(before) is bytes and all(type(word) is str for word in
            (operation, kind, actor, subject_kind, subject)) and type(record) is dict
            and set(record) == {'original', 'x5'}, 'CUSTODY_MUTATION_COMPLETE_ORIGINAL_INPUT_REQUIRED')
    return archive({'schema': 'worldline.custody-mutation-v2', 'before': restore_archive(before),
                    'candidate': {'operation': operation, 'kind': kind, 'actor': actor,
                                  'subject_kind': subject_kind, 'subject': subject, 'record': record}})

def invoke(native, raw):
    try: function = native.wl_custody_mutation_decide_v2
    except AttributeError as error: raise CoreUnavailable('native complete custody-v2 mutation unavailable') from error
    return _invoke(function, raw)

def invoke_retry(native, raw):
    try: function = native.wl_custody_retry_decide_v2
    except AttributeError as error: raise CoreUnavailable('native complete custody-v2 retry unavailable') from error
    return _invoke(function, raw)

def _invoke(function, raw):
    require(type(raw) is bytes and C.c_size_t(len(raw)).value == len(raw), 'CUSTODY_MUTATION_HOST_INPUT_EXTENT')
    function.argtypes = [C.c_void_p, C.c_size_t, C.POINTER(C.c_uint64), C.POINTER(C.c_uint64),
                        C.c_void_p, C.c_size_t, C.POINTER(C.c_uint64)]
    function.restype = C.c_int
    data = (C.c_ubyte * len(raw)).from_buffer_copy(raw)
    status = C.c_uint64(); position = C.c_uint64(); written = C.c_uint64()
    code = function(data, len(raw), C.byref(status), C.byref(position), None, 0, C.byref(written))
    if code != 0: raise CoreUnavailable('custody-v2 mutation sizing transport refused')
    first = (status.value, position.value, written.value)
    require(C.c_size_t(written.value).value == written.value, 'CUSTODY_MUTATION_HOST_OUTPUT_EXTENT')
    output = (C.c_ubyte * written.value)()
    code = function(data, len(raw), C.byref(status), C.byref(position),
                    output if written.value else None, len(output), C.byref(written))
    if code != 0: raise CoreUnavailable('custody-v2 mutation output transport refused')
    if (status.value, position.value, written.value) != first:
        raise CoreUnavailable('custody-v2 mutation changed over identical immutable input')
    delta = exact_json(bytes(output)) if written.value else None
    return MutationObservation(status.value, position.value, delta, raw)

def decide_journal(journal, raw):
    from .root_worker_journal_v2 import RootCustodyJournalV2
    require(type(journal) is RootCustodyJournalV2, 'CUSTODY_MUTATION_ACTUAL_OWNER_REQUIRED')
    journal.intact()
    try: function = journal.core._lib.wl_custody_mutation_decide_v2
    except AttributeError as error: raise CoreUnavailable('native complete custody-v2 mutation unavailable') from error
    _mapped(journal, journal.core, (function,))
    result = invoke(journal.core._lib, raw)
    _mapped(journal, journal.core, (function,))
    journal.intact()
    return result

def decide_retry(journal, raw):
    from .root_worker_journal_v2 import RootCustodyJournalV2
    require(type(journal) is RootCustodyJournalV2, 'CUSTODY_RETRY_ACTUAL_OWNER_REQUIRED')
    journal.intact()
    try: function = journal.core._lib.wl_custody_retry_decide_v2
    except AttributeError as error: raise CoreUnavailable('native complete custody-v2 retry unavailable') from error
    _mapped(journal, journal.core, (function,))
    result = invoke_retry(journal.core._lib, raw)
    _mapped(journal, journal.core, (function,))
    journal.intact()
    return result
