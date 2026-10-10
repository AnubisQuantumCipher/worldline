"""Owned offline custody eligibility transport through the existing C_API."""
from __future__ import annotations
import ctypes as C
from dataclasses import dataclass
from .errors import CoreUnavailable
from .protected_startup import require, exact_json
from .root_worker_codec import archive, restore_archive
from .retained_v1_migration_capture import RetainedV1Capture
from .retained_chain_kernel import _Span, _mapped

_SYMBOLS = ('wl_custody_provision_version_v2', 'wl_custody_provision_layout_v2',
            'wl_custody_provision_decide_v2')
_STATES = ('Selected_Context_Refused', 'Prior_Context_Refused', 'Retained_Chain_Refused',
           'Operation_Not_Closed', 'New_Origin_Eligible', 'Closed_V1_Migration_Eligible')
class _Output(C.Structure):
    _fields_ = [('status', C.c_int), ('failing_row', C.c_int64)]
@dataclass(frozen=True)
class ProvisionInputs:
    arena: bytes
    spans: tuple
    genesis_count: int
    event_count: int
    head_count: int
@dataclass(frozen=True)
class ProvisionDecision:
    state: str
    position: int
    inputs: ProvisionInputs

def operands(descriptor_raw, plan_raw, genesis_raw, descriptor_path, plan_path,
             genesis_path, journal_path, key, mode, prior):
    require(mode in ('NEW', 'MIGRATE') and (prior is None) == (mode == 'NEW'),
            'CUSTODY_PROVISION_EXPLICIT_MODE_REQUIRED')
    arena = bytearray(); spans = []
    def put(raw):
        require(type(raw) is bytes, 'CUSTODY_PROVISION_OWNED_BYTES_REQUIRED')
        spans.append((len(arena) + 1, len(raw))); arena.extend(raw)
    def text(word):
        require(type(word) is str, 'CUSTODY_PROVISION_TEXT_REQUIRED')
        put(word.encode('utf-8', 'surrogatepass'))
    for raw, path in ((descriptor_raw, descriptor_path), (plan_raw, plan_path),
                      (genesis_raw, genesis_path)):
        put(raw); put(archive(exact_json(raw))); text(path)
    text(journal_path); put(key); text(mode)
    counts = (0, 0, 0); tables = None
    if prior is None:
        for _ in range(25):
            put(b'')
    else:
        require(type(prior) is RetainedV1Capture, 'CUSTODY_PROVISION_ACTUAL_RETAINED_CAPTURE_REQUIRED')
        prior.intact(); selected = prior.selected
        for raw, path, expected in (
                (prior.descriptor_raw, selected.descriptor_path, selected.descriptor_sha256),
                (prior.plan_raw, selected.plan_path, selected.plan_sha256),
                (prior.genesis_raw, selected.genesis_path, selected.genesis_sha256),
                (prior.journal_raw, selected.journal_path, selected.journal_sha256),
                (prior.key, prior.key_path, selected.issuer_key_sha256)):
            put(raw); text(path); text(path); text(expected)
        put(archive(exact_json(prior.descriptor_raw))); put(archive(exact_json(prior.plan_raw)))
        put(prior.genesis_archive); put(prior.head_archive); text(selected.head_event)
        database = restore_archive(prior.logical_database_archive)
        tables = {table['name']: table for table in database['tables']}
        counts = tuple(len(tables[name]['rows']) for name in ('genesis', 'events', 'head'))
    if tables is not None:
        for _, name, value in tables['genesis']['rows']:
            text(name); put(value)
        for _, event_id, previous, operation, kind, raw, mac in tables['events']['rows']:
            for word in (event_id, previous, operation, kind): text(word)
            put(raw); text(mac)
            put(archive({'previous': previous, 'operation': operation, 'kind': kind,
                         'record': restore_archive(raw)}))
        for _, name, event_id, mac in tables['head']['rows']:
            text(name); text(event_id); text(mac)
    return ProvisionInputs(bytes(arena), tuple(spans), *counts)

def invoke(functions, inputs):
    require(type(inputs) is ProvisionInputs, 'CUSTODY_PROVISION_EXACT_INPUT_TYPE_REQUIRED')
    version, layout, decide = functions
    version.argtypes = []; version.restype = C.c_uint32
    layout.argtypes = [C.c_uint8, C.c_uint8]; layout.restype = C.c_size_t
    decide.argtypes = [C.c_void_p, C.c_size_t, C.c_void_p, C.c_size_t,
                      C.c_size_t, C.c_size_t, C.c_size_t, C.c_void_p, C.c_size_t]
    decide.restype = C.c_int
    if version() != 2: raise CoreUnavailable('custody provision version mismatch')
    for kind, record in ((1, _Span), (2, _Output)):
        expected = [C.sizeof(record), C.alignment(record)]
        expected.extend(getattr(record, name).offset for name, _ in record._fields_)
        if any(layout(kind, field) != value for field, value in enumerate(expected)):
            raise CoreUnavailable('custody provision layout mismatch')
    counts = (len(inputs.arena), len(inputs.spans), inputs.genesis_count, inputs.event_count, inputs.head_count)
    require(all(type(n) is int and n >= 0 and C.c_size_t(n).value == n and C.c_int64(n).value == n
                for n in counts), 'CUSTODY_PROVISION_HOST_EXTENT')
    require(len(inputs.spans) == 37 + inputs.genesis_count * 2 + inputs.event_count * 7 + inputs.head_count * 3,
            'CUSTODY_PROVISION_ROSTER_EXTENT')
    spans = (_Span * len(inputs.spans))()
    for index, (first, length) in enumerate(inputs.spans):
        require(type(first) is int and type(length) is int and first >= 1 and length >= 0
                and first - 1 <= len(inputs.arena) and length <= len(inputs.arena) - (first - 1),
                'CUSTODY_PROVISION_SPAN_EXTENT')
        first = first if length else 1
        require(C.c_int64(first).value == first and C.c_int64(length).value == length,
                'CUSTODY_PROVISION_SPAN_REPRESENTATION')
        spans[index] = _Span(first, length)
    data = (C.c_ubyte * len(inputs.arena)).from_buffer_copy(inputs.arena)
    output = _Output()
    code = decide(data, len(inputs.arena), spans, len(spans), inputs.genesis_count,
                  inputs.event_count, inputs.head_count, C.byref(output), C.sizeof(output))
    if code != 0: raise CoreUnavailable('custody provision transport refused')
    if not 0 <= output.status < len(_STATES) or not 0 <= output.failing_row <= inputs.event_count:
        raise CoreUnavailable('custody provision malformed decision')
    return ProvisionDecision(_STATES[output.status], output.failing_row, inputs)

def decide_selected(provisioner):
    from .custody_v2_provision_entry import OfflineCustodyProvisioner
    require(type(provisioner) is OfflineCustodyProvisioner, 'CUSTODY_PROVISION_REAL_OPERATOR_ENTRY_REQUIRED')
    provisioner.intact()
    try:
        functions = tuple(getattr(provisioner.core._lib, name) for name in _SYMBOLS)
    except AttributeError as error:
        raise CoreUnavailable('native custody provision unavailable') from error
    _mapped(provisioner, provisioner.core, functions)
    result = invoke(functions, provisioner.native_inputs())
    _mapped(provisioner, provisioner.core, functions)
    provisioner.intact()
    return result
