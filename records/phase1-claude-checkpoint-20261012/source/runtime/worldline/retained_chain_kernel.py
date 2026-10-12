"""Owning retained-v1 transport. Integrity observations never grant startup/effect use."""
from __future__ import annotations
import ctypes as C
from dataclasses import dataclass
import os
from pathlib import Path
from .errors import CoreUnavailable
from .protected_startup import require
from .root_worker_retained_inputs import RetainedInputs, capture_retained_inputs

_SYMBOLS = ('wl_retained_chain_version_v1', 'wl_retained_chain_layout_v1',
            'wl_retained_chain_verify_v1')
_STATES = ('Retained_Chain_Matches', 'Malformed_Input', 'Genesis_Mismatch',
           'Row_Malformed', 'Row_Link', 'Row_Id', 'Row_Duplicate', 'Row_Mac',
           'Head_Mismatch', 'Head_Archive_Mismatch', 'Head_Mac')

class _Span(C.Structure):
    _fields_ = [('first', C.c_int64), ('length', C.c_int64)]

class _Output(C.Structure):
    _fields_ = [('status', C.c_int), ('failing_row', C.c_int64),
               ('origin', C.c_ubyte * 32), ('head', C.c_ubyte * 32)]

@dataclass(frozen=True)
class RetainedObservation:
    state: str
    failing_row: int
    origin: bytes
    head: bytes
    inputs: RetainedInputs


def _symbols(native):
    try:
        return tuple(getattr(native, name) for name in _SYMBOLS)
    except AttributeError as error:
        raise CoreUnavailable('native retained custody chain unavailable') from error


def _mapped(owner, core, functions):
    # Existing selected owner/source lease remains authority. No supplied library,
    # capture document, callback, or caller authorization boolean is accepted.
    owner.intact()
    selected = Path(owner.spec['runtime']['native_library']).resolve(strict=True)
    require(core.library_path == selected, 'RETAINED_SELECTED_NATIVE_SPLIT')
    lease = owner.source_lease
    lease.check()
    # check_files uses this same envelope-selected role; no new role invented.
    require(str(selected) in lease.files, 'RETAINED_NATIVE_SOURCE_ENVELOPE_ABSENT')
    raw = lease.file(str(selected), (lease.files[str(selected)][0],))
    before = selected.stat()
    executable = []
    for line in Path('/proc/self/maps').read_text().splitlines():
        fields = line.split(maxsplit=5)
        if len(fields) != 6 or fields[5] != str(selected):
            continue
        bounds, permissions = fields[:2]
        fd = os.open(Path('/proc/self/map_files') / bounds, os.O_RDONLY | os.O_CLOEXEC)
        try:
            mapped = os.fstat(fd)
            with os.fdopen(os.dup(fd), 'rb') as source:
                content = source.read()
            require((mapped.st_dev, mapped.st_ino) == (before.st_dev, before.st_ino)
                    and content == raw, 'RETAINED_MAPPED_NATIVE_DIFFERS')
        finally:
            os.close(fd)
        if 'x' in permissions:
            executable.append(tuple(int(value, 16) for value in bounds.split('-')))
    for function in functions:
        address = C.cast(function, C.c_void_p).value
        require(address is not None and any(start <= address < end for start, end in executable),
                'RETAINED_SYMBOL_OUTSIDE_SELECTED_NATIVE')
    require(selected.read_bytes() == raw, 'RETAINED_NATIVE_BYTES_CHANGED')
    owner.intact()


def _pack(inputs):
    require(type(inputs) is RetainedInputs and type(inputs.arena) is bytes,
            'RETAINED_OWNED_INPUT_REQUIRED')
    flat = [inputs.key, inputs.genesis_archive, inputs.head_archive]
    for rows, width in ((inputs.genesis_rows, 2), (inputs.event_rows, 7), (inputs.head_rows, 3)):
        require(type(rows) is tuple, 'RETAINED_ROW_CONTAINER')
        for row in rows:
            require(type(row) is tuple and len(row) == width, 'RETAINED_ROW_ARITY')
            flat.extend(row)
    spans = (_Span * len(flat))()
    for index, span in enumerate(flat):
        require(type(span) is tuple and len(span) == 2 and
                all(type(value) is int for value in span), 'RETAINED_SPAN_TYPES')
        first, length = span
        require(first >= 1 and length >= 0 and first - 1 <= len(inputs.arena)
                and length <= len(inputs.arena) - (first - 1), 'RETAINED_SPAN_BOUNDS')
        # Empty spans have no selected bytes; canonical zero-length position
        # avoids a one-past-arena integer representation restriction.
        if length == 0:
            first = 1
        require(C.c_int64(first).value == first and C.c_int64(length).value == length,
                'RETAINED_SPAN_HOST_REPRESENTATION')
        spans[index] = _Span(first, length)
    for count in (len(inputs.arena), len(flat), len(inputs.genesis_rows),
                  len(inputs.event_rows), len(inputs.head_rows)):
        require(C.c_size_t(count).value == count and C.c_int64(count).value == count,
                'RETAINED_COUNT_HOST_REPRESENTATION')
    data = (C.c_ubyte * len(inputs.arena)).from_buffer_copy(inputs.arena)
    return data, spans


def _invoke(functions, inputs):
    version, layout, verify = functions
    version.argtypes = []; version.restype = C.c_uint32
    layout.argtypes = [C.c_uint8, C.c_uint8]; layout.restype = C.c_size_t
    verify.argtypes = [C.c_void_p, C.c_size_t, C.c_void_p, C.c_size_t,
                       C.c_size_t, C.c_size_t, C.c_size_t, C.c_void_p, C.c_size_t]
    verify.restype = C.c_int
    if version() != 1:
        raise CoreUnavailable('native retained custody chain version mismatch')
    for kind, record in ((1, _Span), (2, _Output)):
        expected = [C.sizeof(record), C.alignment(record)]
        expected.extend(getattr(record, name).offset for name, _ in record._fields_)
        if any(layout(kind, field) != value for field, value in enumerate(expected)):
            raise CoreUnavailable('native retained custody chain layout mismatch')
    data, spans = _pack(inputs)
    output = _Output()
    code = verify(data, len(inputs.arena), spans, len(spans), len(inputs.genesis_rows),
                  len(inputs.event_rows), len(inputs.head_rows), C.byref(output), C.sizeof(output))
    if code != 0:
        raise CoreUnavailable('native retained custody chain transport failed')
    if not 0 <= output.status < len(_STATES) or not 0 <= output.failing_row <= len(inputs.event_rows):
        raise CoreUnavailable('native retained custody chain malformed observation')
    state = _STATES[output.status]
    # Native Verify reports an original row index only for row-specific failures.
    # The C wrapper owns a one-based event array, including its empty null range.
    row_failure = state in ('Row_Malformed', 'Row_Link', 'Row_Id', 'Row_Duplicate', 'Row_Mac')
    if (row_failure and output.failing_row == 0) or (not row_failure and output.failing_row != 0):
        raise CoreUnavailable('native retained custody chain inconsistent failure location')
    return RetainedObservation(state, output.failing_row,
                               bytes(output.origin), bytes(output.head), inputs)


def verify_current_owner(owner):
    from .protected_root_worker import RootWorkerFront, RootWorkerProcess, RootWorkerIntake
    require(type(owner) in (RootWorkerFront, RootWorkerProcess, RootWorkerIntake),
            'RETAINED_ACTUAL_ROOT_OWNER_REQUIRED')
    core = owner.core if type(owner) is RootWorkerIntake else owner.principal.core
    functions = _symbols(core._lib)  # Resolve only; invoke no version/layout query yet.
    _mapped(owner, core, functions)
    inputs = capture_retained_inputs(owner)
    # Recheck after capture and before the first foreign invocation.
    _mapped(owner, core, functions)
    result = _invoke(functions, inputs)
    _mapped(owner, core, functions)
    return result
