"""Exact raw owner/K4 witness transport to the native full-history authority."""
from __future__ import annotations
import ctypes as C
from .errors import CoreUnavailable
from .operation_capture import archive
from .protected_startup import require
from .retained_chain_kernel import _mapped


def invoke(native, kind, current, input_bytes):
    require(type(current) is bytes and type(input_bytes) is bytes,
            'JOURNAL_WITNESS_OWNED_BYTES_REQUIRED')
    require(C.c_size_t(len(current)).value == len(current)
            and C.c_size_t(len(input_bytes)).value == len(input_bytes),
            'JOURNAL_WITNESS_HOST_EXTENT')
    try:
        function = native.wl_journal_witness_decide_v1
    except AttributeError as error:
        raise CoreUnavailable('native full journal witness authority unavailable') from error
    function.argtypes = [C.c_uint8, C.c_void_p, C.c_size_t, C.c_void_p,
                         C.c_size_t, C.POINTER(C.c_uint64)]
    function.restype = C.c_int
    current_buffer = (C.c_ubyte * len(current)).from_buffer_copy(current)
    input_buffer = (C.c_ubyte * len(input_bytes)).from_buffer_copy(input_bytes)
    decision = C.c_uint64()
    result = function(kind, current_buffer, len(current), input_buffer,
                      len(input_bytes), C.byref(decision))
    if result != 0:
        raise CoreUnavailable('native journal witness transport refused')
    return decision.value


def _decide(principal, kind, value):
    from .root_worker_journal_v2 import RootCustodyJournalV2
    journal = principal.lease.custody_journal_v2
    require(type(journal) is RootCustodyJournalV2,
            'JOURNAL_WITNESS_REAL_CURRENT_CUSTODY_REQUIRED')
    journal.intact()
    # Capture directly under the original transaction. Calling load here would
    # recursively replay the operation journal whose witness is being checked.
    with journal.lock, principal.owner.lock:
        db = journal.connect()
        try:
            db.execute('BEGIN')
            current = journal.capture(db)
            input_bytes = archive(value)
            try:
                function = principal.core._lib.wl_journal_witness_decide_v1
            except AttributeError as error:
                raise CoreUnavailable('native full journal witness authority unavailable') from error
            _mapped(journal, principal.core, (function,))
            decision = invoke(principal.core._lib, kind, current, input_bytes)
            _mapped(journal, principal.core, (function,))
            journal.intact()
        finally:
            try:
                db.rollback()
            finally:
                db.close()
    return decision


def verify_owner(principal, captured):
    decision = _decide(principal, 0, captured)
    require(decision == 0, 'OWNER_CANONICAL_FULL_NATIVE_WITNESS_REFUSED')
    return 'READY'


def verify_resource_ack(principal, capture, acknowledgement):
    decision = _decide(principal, 1, {'capture': capture, 'ack': acknowledgement})
    require(decision == 0, 'FULL_BROKER_K4_AUTHENTIC_CURRENT_NATIVE_ACK_REFUSED')
    return 'READY'
