"""Read-only native allocation from the exact staged custody envelope."""
from __future__ import annotations
import ctypes as C
from dataclasses import dataclass
from enum import IntEnum
from .protected_startup import require
from .retained_chain_kernel import _mapped


class ReplayDisposition(IntEnum):
    WRITE = 1
    DROP = 2
    HOLD = 3


@dataclass(frozen=True)
class ReplayDecision:
    disposition: ReplayDisposition
    ordinal: bytes


def next_output(journal, raw) -> bytes:
    function = journal.core._lib.wl_root_worker_output_next_v1
    function.argtypes = [C.c_void_p, C.c_size_t, C.POINTER(C.c_uint64),
                        C.POINTER(C.c_uint64), C.c_void_p, C.c_size_t,
                        C.POINTER(C.c_size_t)]
    function.restype = C.c_int
    _mapped(journal, journal.core, (function,))
    source = (C.c_ubyte * len(raw)).from_buffer_copy(raw)
    status = C.c_uint64()
    position = C.c_uint64()
    needed = C.c_size_t()
    require(function(source, len(raw), C.byref(status), C.byref(position),
                     None, 0, C.byref(needed)) == 0,
            'ROOT_OUTPUT_NATIVE_QUERY_FAILED')
    first = status.value, position.value, needed.value
    require(status.value == 1 and needed.value > 0,
            'ROOT_OUTPUT_NATIVE_ALLOCATION_REFUSED')
    output = (C.c_ubyte * needed.value)()
    require(function(source, len(raw), C.byref(status), C.byref(position),
                     output, len(output), C.byref(needed)) == 0 and
            first == (status.value, position.value, needed.value),
            'ROOT_OUTPUT_NATIVE_ALLOCATION_CHANGED')
    _mapped(journal, journal.core, (function,))
    return bytes(output)

def replay_output(journal, raw) -> ReplayDecision:
    function = journal.core._lib.wl_root_worker_output_replay_v1
    function.argtypes = [C.c_void_p, C.c_size_t, C.POINTER(C.c_uint64),
                        C.POINTER(C.c_uint64), C.c_void_p, C.c_size_t,
                        C.POINTER(C.c_size_t)]
    function.restype = C.c_int
    _mapped(journal, journal.core, (function,))
    source = (C.c_ubyte * len(raw)).from_buffer_copy(raw)
    status = C.c_uint64()
    position = C.c_uint64()
    needed = C.c_size_t()
    require(function(source, len(raw), C.byref(status), C.byref(position),
                     None, 0, C.byref(needed)) == 0,
            'ROOT_OUTPUT_NATIVE_QUERY_FAILED')
    first = status.value, position.value, needed.value
    require(status.value in (1, 2, 3) and needed.value > 0,
            'ROOT_OUTPUT_NATIVE_REPLAY_REFUSED')
    output = (C.c_ubyte * needed.value)()
    require(function(source, len(raw), C.byref(status), C.byref(position),
                     output, len(output), C.byref(needed)) == 0 and
            first == (status.value, position.value, needed.value),
            'ROOT_OUTPUT_NATIVE_ALLOCATION_CHANGED')
    _mapped(journal, journal.core, (function,))
    return ReplayDecision(ReplayDisposition(status.value), bytes(output))
def written_output(journal, raw) -> bytes:
    function = journal.core._lib.wl_root_worker_output_written_v1
    function.argtypes = [C.c_void_p, C.c_size_t, C.POINTER(C.c_uint64),
                        C.POINTER(C.c_uint64), C.c_void_p, C.c_size_t,
                        C.POINTER(C.c_size_t)]
    function.restype = C.c_int
    _mapped(journal, journal.core, (function,))
    source = (C.c_ubyte * len(raw)).from_buffer_copy(raw)
    status = C.c_uint64()
    position = C.c_uint64()
    needed = C.c_size_t()
    require(function(source, len(raw), C.byref(status), C.byref(position),
                     None, 0, C.byref(needed)) == 0,
            'ROOT_OUTPUT_NATIVE_QUERY_FAILED')
    first = status.value, position.value, needed.value
    require(status.value == 1 and needed.value > 0,
            'ROOT_OUTPUT_NATIVE_ALLOCATION_REFUSED')
    output = (C.c_ubyte * needed.value)()
    require(function(source, len(raw), C.byref(status), C.byref(position),
                     output, len(output), C.byref(needed)) == 0 and
            first == (status.value, position.value, needed.value),
            'ROOT_OUTPUT_NATIVE_ALLOCATION_CHANGED')
    _mapped(journal, journal.core, (function,))
    return bytes(output)


def prefix_output(journal, raw) -> bytes:
    function = journal.core._lib.wl_root_worker_output_prefix_v1
    function.argtypes = [C.c_void_p, C.c_size_t, C.POINTER(C.c_uint64),
                        C.POINTER(C.c_uint64), C.c_void_p, C.c_size_t,
                        C.POINTER(C.c_size_t)]
    function.restype = C.c_int
    _mapped(journal, journal.core, (function,))
    source = (C.c_ubyte * len(raw)).from_buffer_copy(raw)
    status = C.c_uint64()
    position = C.c_uint64()
    needed = C.c_size_t()
    require(function(source, len(raw), C.byref(status), C.byref(position),
                     None, 0, C.byref(needed)) == 0,
            'ROOT_OUTPUT_NATIVE_QUERY_FAILED')
    first = status.value, position.value, needed.value
    require(status.value == 1 and needed.value > 0,
            'ROOT_OUTPUT_NATIVE_PREFIX_REFUSED')
    output = (C.c_ubyte * needed.value)()
    require(function(source, len(raw), C.byref(status), C.byref(position),
                     output, len(output), C.byref(needed)) == 0 and
            first == (status.value, position.value, needed.value),
            'ROOT_OUTPUT_NATIVE_PREFIX_CHANGED')
    _mapped(journal, journal.core, (function,))
    return bytes(output)
