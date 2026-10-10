"""Read-only native folded quantities and heads; projection never grants effects."""
from __future__ import annotations
import ctypes as C
from .protected_startup import require, exact_json
from .root_worker_codec import raw_archive, scoped_archive, scoped_restore_archive
from .custody_mutation_kernel import mutation_input
from .custody_sql_delta import row, unhex
from .retained_chain_kernel import _mapped

ROOT_COLUMNS = ('generation','operation','phase','before_unknown','owners_open','abort_class','launched',
    'closure_ns','closure_outer','closure_raw','witness','settled','released_unlaunched',
    'unknown_cause','reattach_epoch','head_event')
SUBJECT_COLUMNS = ('generation','subject_kind','subject','subgeneration','phase','mode','position','carried_from','head_event')


def capture_context_input(journal, raw):
    """Capture native bytes from the exact immutable mutation input."""
    function = journal.core._lib.wl_custody_context_view_v2
    function.argtypes = [C.c_void_p, C.c_size_t, C.POINTER(C.c_uint64), C.POINTER(C.c_uint64),
                        C.c_void_p, C.c_size_t, C.POINTER(C.c_uint64)]
    function.restype = C.c_int
    _mapped(journal, journal.core, (function,))
    source = (C.c_ubyte * len(raw)).from_buffer_copy(raw)
    status = C.c_uint64()
    position = C.c_uint64()
    written = C.c_uint64()
    require(function(source, len(raw), C.byref(status), C.byref(position), None, 0,
                     C.byref(written)) == 0, 'CUSTODY_CONTEXT_NATIVE_SIZING_REFUSED')
    first = status.value, position.value, written.value
    require(C.c_size_t(written.value).value == written.value,
            'CUSTODY_CONTEXT_NATIVE_CAPACITY_UNREPRESENTABLE')
    output = (C.c_ubyte * written.value)()
    require(function(source, len(raw), C.byref(status), C.byref(position), output, len(output),
                     C.byref(written)) == 0 and first == (status.value, position.value, written.value),
            'CUSTODY_CONTEXT_NATIVE_PROJECTION_CHANGED')
    _mapped(journal, journal.core, (function,))
    return {'raw': bytes(output), 'status': status.value, 'position': position.value}


def context_view(journal, before, operation, kind, actor, subject_kind, subject, original, *,
                 query_purpose='MUTATION', root_generation=None):
    raw = mutation_input(before, operation, kind, actor, subject_kind, subject,
                         {'original': raw_archive(original), 'x5': {}})
    if query_purpose != 'MUTATION' or root_generation is not None:
        value = scoped_restore_archive(raw)
        if query_purpose != 'MUTATION':
            value['query_purpose'] = query_purpose
        if root_generation is not None:
            value['candidate']['root_generation'] = root_generation
        raw = scoped_archive(value)
    captured = capture_context_input(journal, raw)
    require(captured['status'] in (0, 1, 2), 'CUSTODY_CONTEXT_NATIVE_PROJECTION_REFUSED')
    profile = exact_json(captured['raw'])
    require(type(profile) is dict and profile['schema'] == 'worldline.custody-context-view-v2',
            'CUSTODY_CONTEXT_COMPLETE_NATIVE_SCHEMA')
    decoded = dict(profile)
    decoded['roots'] = tuple(dict(zip(ROOT_COLUMNS, row(item, 16))) for item in profile['roots'])
    decoded['subjects'] = tuple(dict(zip(SUBJECT_COLUMNS, row(item, 9))) for item in profile['subjects'])
    decoded['current_root'] = None if profile['current_root'] is None else dict(zip(ROOT_COLUMNS, row(profile['current_root'], 16)))
    decoded['root'] = None if profile['root'] is None else dict(zip(ROOT_COLUMNS, row(profile['root'], 16)))
    decoded['subject'] = None if profile['subject'] is None else dict(zip(SUBJECT_COLUMNS, row(profile['subject'], 9)))
    for name in ('generation', 'reattach_epoch', 'event_generation', 'event_subgeneration',
                 'next_subgeneration', 'next_reattach_epoch'):
        decoded[name] = None if profile[name] is None else unhex(profile[name])
    return decoded
