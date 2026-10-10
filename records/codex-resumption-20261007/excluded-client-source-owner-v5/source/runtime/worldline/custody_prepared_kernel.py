"""Owned PREPARED value-step ABI. Never authenticates custody or starts runtime.

Original operation snapshots are captured under the actual front owner's lease.
Explicit custody prefix/root/event operands remain value inputs, not authority.
"""
from __future__ import annotations
import ctypes as C
from dataclasses import dataclass
from . import operation_authority_kernel as OW
from . import recovery_authority_kernel_v3 as RW
from .errors import CoreUnavailable
from .protected_startup import require, private_bytes
from .retained_chain_kernel import _mapped
from .root_worker_prepared_wire import PreparedWire, capture_prepared_wire

_SYMBOLS = ('wl_custody_prepared_version_v1', 'wl_custody_prepared_layout_v1',
            'wl_custody_prepared_decide_v1')
STATES = ('Malformed_Reserve', 'Malformed_Intent', 'Malformed_Roster',
          'Operation_Or_Grant_Changed', 'Native_Prepared_Refused',
          'Prepared_Value_Step_Only')

class Span(C.Structure):
    _fields_ = [('first', C.c_int64), ('length', C.c_int64)]

class Root(C.Structure):
    _fields_ = [('generation', OW.Quantity), ('operation', OW.Quantity), ('phase', C.c_uint8), ('before_unknown', C.c_uint8), ('owners_open', C.c_uint8), ('abort_kind', C.c_uint8), ('launched', C.c_uint8), ('ns', C.c_uint8), ('outer', C.c_uint8), ('raw', C.c_uint8), ('witness', C.c_uint8), ('settled', C.c_uint8), ('released_unlaunched', C.c_uint8), ('unknown_cause', OW._Digest), ('reattach_epoch', OW.Quantity), ('head', C.c_uint8 * len(OW._Digest().value))]

class Event(C.Structure):
    _fields_ = [('event_id', Span), ('previous', Span), ('generation', Span), ('operation', Span), ('subject_kind', Span), ('subject', Span), ('subgeneration', Span), ('kind', Span), ('actor', Span), ('record_archive', Span), ('base_archive', Span), ('mac', Span)]

class Output(C.Structure):
    _fields_ = [('status', C.c_int), ('after_state', Root)]

# Includes every nested record, not merely top-level size guesses.
_LAYOUTS = (Span, Root, Event, Output, OW.Quantity, OW.UID, OW.Binding,
            OW.Grant, OW.Use, OW.Evidence, OW.Input, OW._Digest, OW._Row,
            RW.OptionalEpoch, RW.OptionalDigest, RW.Binding, RW.Native, RW.Request)

@dataclass(frozen=True)
class CustodyValueInput:
    prefix: bytes
    event: bytes
    before_root: bytes

@dataclass(frozen=True)
class PreparedObservation:
    state: str
    after_root: bytes
    operation_inputs: PreparedWire
    custody_input: CustodyValueInput


def _symbols(native):
    try:
        return tuple(getattr(native, name) for name in _SYMBOLS)
    except AttributeError as exc:
        raise CoreUnavailable('native PREPARED value step unavailable') from exc


def _field_values(value):
    # Compare complete semantic fields, never C padding bytes.
    if isinstance(value, C.Structure):
        return tuple(_field_values(getattr(value, name)) for name, _ in value._fields_)
    if isinstance(value, C.Array):
        return tuple(_field_values(v) for v in value)
    return value


def _invoke(functions, prepared, custody):
    require(type(prepared) is PreparedWire and type(custody) is CustodyValueInput,
            'PREPARED_OWNED_VALUES_REQUIRED')
    require(all(type(v) is bytes for v in (prepared.arena, custody.prefix,
                custody.event, custody.before_root)), 'PREPARED_OWNED_BYTES_REQUIRED')
    require(prepared.arena.startswith(custody.prefix), 'PREPARED_CUSTODY_PREFIX_CHANGED')
    version, layout, decide = functions
    version.argtypes, version.restype = [], C.c_uint32
    layout.argtypes, layout.restype = [C.c_uint32, C.c_uint32], C.c_size_t
    if version() != 1:
        raise CoreUnavailable('native PREPARED value-step version differs')
    for kind, typ in enumerate(_LAYOUTS, 1):
        expected = [C.sizeof(typ), C.alignment(typ)]
        expected.extend(getattr(typ, name).offset for name, _ in typ._fields_)
        if any(layout(kind, field) != value for field, value in enumerate(expected)):
            raise CoreUnavailable('native PREPARED complete layout differs')
    require(len(custody.event) == C.sizeof(Event) and len(custody.before_root) == C.sizeof(Root),
            'PREPARED_CUSTODY_RECORD_SIZE')
    event = Event.from_buffer_copy(custody.event)
    root = Root.from_buffer_copy(custody.before_root)
    requests = []
    roster_sets = []
    for snap in (prepared.reserve, prepared.intent):
        require(type(snap.request) is bytes and len(snap.request) == C.sizeof(OW.Input),
                'PREPARED_OPERATION_REQUEST_SIZE')
        require(type(snap.rosters) is tuple and type(snap.counts) is tuple and
                len(snap.rosters) == len(snap.counts) == len((OW.Grant, OW.Use, OW._Row, OW._Row)),
                'PREPARED_COMPLETE_ROSTER_SET')
        requests.append(OW.Input.from_buffer_copy(snap.request))
        arrays = []
        for raw, count, typ in zip(snap.rosters, snap.counts, (OW.Grant, OW.Use, OW._Row, OW._Row)):
            require(type(raw) is bytes and type(count) is int and count >= 0 and
                    C.c_size_t(count).value == count and C.c_int64(count).value == count and
                    len(raw) == count * C.sizeof(typ), 'PREPARED_ROSTER_EXTENT')
            arrays.append((typ * count).from_buffer_copy(raw))
        roster_sets.append(arrays)
    require(C.c_size_t(len(prepared.arena)).value == len(prepared.arena) and
            C.c_int64(len(prepared.arena)).value == len(prepared.arena), 'PREPARED_ARENA_EXTENT')
    data = (C.c_uint8 * len(prepared.arena)).from_buffer_copy(prepared.arena)
    result = Output()
    # Order matches the explicit C_API signature; every array remains owned.
    ordered = (roster_sets[0][0], roster_sets[1][0], roster_sets[0][1], roster_sets[1][1],
               roster_sets[0][2], roster_sets[0][3], roster_sets[1][2], roster_sets[1][3])
    args = [data, len(data), C.byref(event), C.byref(root), C.byref(requests[0]), C.byref(requests[1]),
            C.sizeof(event), C.sizeof(root), C.sizeof(requests[0]), C.sizeof(requests[1])]
    signature = [C.c_void_p, C.c_size_t] + [C.c_void_p] * len((event, root, *requests)) + [C.c_size_t] * len((event, root, *requests))
    for array in ordered:
        args.extend((array, len(array), C.sizeof(array)))
        signature.extend((C.c_void_p, C.c_size_t, C.c_size_t))
    args.extend((C.byref(result), C.sizeof(result)))
    signature.extend((C.c_void_p, C.c_size_t))
    decide.argtypes, decide.restype = signature, C.c_int
    if decide(*args) != 0:
        raise CoreUnavailable('native PREPARED value-step transport refused')
    if not 0 <= result.status < len(STATES):
        raise CoreUnavailable('native PREPARED value-step status unknown')
    after = result.after_state
    if STATES[result.status] != 'Prepared_Value_Step_Only':
        if _field_values(after) != _field_values(root):
            raise CoreUnavailable('native PREPARED refusal changed root')
    else:
        # Output correspondence checks cannot grant a transition. Native policy
        # already decided it; these detect malformed native transport/results.
        for name, _ in Root._fields_:
            if name not in ('phase', 'operation', 'head') and _field_values(getattr(root, name)) != _field_values(getattr(after, name)):
                raise CoreUnavailable('native PREPARED frame fields changed')
        if after.phase != 1 or _field_values(after.operation) != (1, 0, event.operation.first, event.operation.length):
            raise CoreUnavailable('native PREPARED image differs')
        first, length = event.event_id.first, event.event_id.length
        require(first >= 1 and length >= 0 and first - 1 <= len(prepared.arena) and
                length <= len(prepared.arena) - (first - 1), 'PREPARED_OUTPUT_EVENT_SPAN')
        encoded = prepared.arena[first - 1:first - 1 + length]
        if encoded != bytes(after.head).hex().encode('ascii'):
            raise CoreUnavailable('native PREPARED event head differs')
    return PreparedObservation(STATES[result.status], bytes(after), prepared, custody)


def observe_owner_value_step(owner, operation, custody):
    from .protected_root_worker import RootWorkerFront
    require(type(owner) is RootWorkerFront, 'PREPARED_ACTUAL_FRONT_REQUIRED')
    require(type(custody) is CustodyValueInput and type(custody.prefix) is bytes,
            'PREPARED_EXPLICIT_CUSTODY_VALUES_REQUIRED')
    core = owner.principal.core
    functions = _symbols(core._lib)  # Resolve before query; absent export stays typed.
    _mapped(owner, core, functions)
    prepared = capture_prepared_wire(owner, operation, custody_prefix=custody.prefix)
    _mapped(owner, core, functions)
    result = _invoke(functions, prepared, custody)
    _mapped(owner, core, functions)
    journal = owner.principal.journal
    require(private_bytes(journal.path) == prepared.retained.journal_raw and
            tuple(journal.head_row()) == prepared.retained.admission_head,
            'PREPARED_OPERATION_CAPTURE_CHANGED')
    return result
