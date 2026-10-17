"""Owned additive Start/Input/capture/Seal calls; no Python decision fallback.

The finalization request is distinct from an ordinary pending request. The
context-only projection below is never given to the ordinary retention API.
Its payload and metadata are checked again by the finalization collapse entry.
"""
from __future__ import annotations

import ctypes as C
from dataclasses import dataclass
from .completion_kernel import (Span, Optional_Span, Required_Row, BoundValue,
    CaptureValue as BoundCapture, CheckValue, EXECUTION, OUTCOME, HISTORY,
    KernelRefused, MAX_COUNT, CompletionKernel, Cursor, Binding, Capture,
    Facts, Presence, Check_Row, Request as ContextRequest)
from .core import HASH_BYTES
from .evaluation_wire import Raw, OwnedRecord
from .finalization_values import (StartValue, InputValue, UnsealedResult,
    CaptureValue, ComponentsValue, SealValue, ClassifiedValue, SealedValue)

U32, I64 = C.c_uint32, C.c_int64
Digest = C.c_uint8 * HASH_BYTES
DECLARATIONS = ('Missing_Declaration', 'Explicit_Empty', 'Required_Checks')

class Start(C.Structure):
    _fields_ = [('store_id', Span), ('subject', Span), ('run', Span),
        ('sequence', Span), ('requirement', Optional_Span), ('policy', Span),
        ('verifier_plan', Span), ('base_context', Span), ('parent', Digest),
        ('config', Digest), ('repository', Digest), ('required', Span),
        ('declaration', U32)]

class Input(C.Structure):
    _fields_ = [('start', Start), ('root', Span), ('manifests', Span),
        ('filesystem', Digest), ('config', Digest), ('repository', Digest)]

class Row(C.Structure):
    _fields_ = [('start', Start), ('check_id', Span), ('source_id', Span),
        ('execution', Optional_Span), ('verifier', Optional_Span),
        ('state', U32), ('outcome', U32), ('payload', Span), ('declared', Span),
        ('raw', Raw), ('confinement', C.c_uint8)]

class Request(C.Structure):
    _fields_ = [('version', U32), ('operation', U32), ('data', C.c_void_p),
        ('data_length', I64), ('start', Start), ('inputs', Input),
        ('post_root', Span), ('post_manifests', Span), ('rows', C.c_void_p),
        ('row_count', I64), ('required', C.c_void_p), ('required_count', I64),
        ('completion', Required_Row), ('content', Span),
        ('environment_root', Digest), ('evidence_root', Digest),
        ('context', Span), ('source_id', Span), ('evidence', Span), ('environment', Span)]

class Result(C.Structure):
    _fields_ = [('reason', U32), ('state', U32), ('outcome', U32),
        ('promotion', U32), ('finalization_state', U32),
        ('finalization_outcome', U32), ('identity', Digest)]


@dataclass
class PreparedFinalization:
    native_request: Request
    native_owners: tuple
    value: SealedValue
    request: object
    owned: tuple
    capture: BoundCapture
    typed_rows: tuple
    context: object = None
    context_owners: tuple = ()
    metadata_context: object = None
    metadata_owners: tuple = ()

    @property
    def seal_value(self):
        """The complete retained immutable DTO whose native Seal was checked."""
        return self.value.value

    def finalization_arguments(self):
        return C.byref(self.native_request), (None if self.metadata_context is None
            else C.byref(self.metadata_context))


class FinalizationKernel:
    def __init__(self, library):
        self.library = C.CDLL(str(library))
        self.library_path = library
        # Verify every reused context layout against this same selected library.
        self.context_layout = CompletionKernel(library)
        try:
            version = self.library.wl_finalization_version_v1
            layout = self.library.wl_finalization_layout_v1
            self.call = self.library.wl_finalization_decide_v1
        except AttributeError as exc:
            raise KernelRefused('FINALIZATION_ABI_UNAVAILABLE') from exc
        version.argtypes, version.restype = [], U32
        layout.argtypes, layout.restype = [U32, U32], I64
        if version() != 1:
            raise KernelRefused('FINALIZATION_ABI_VERSION')
        for kind, typ in enumerate((Start, Input, Row, Request, Result), 1):
            if layout(kind, 0) != C.sizeof(typ) or layout(kind, 1) != C.alignment(typ):
                raise KernelRefused('FINALIZATION_ABI_LAYOUT')
            for field, (name, _) in enumerate(typ._fields_, 2):
                if layout(kind, field) != getattr(typ, name).offset:
                    raise KernelRefused('FINALIZATION_ABI_OFFSET')
        self.call.argtypes, self.call.restype = [C.c_void_p, C.c_void_p], C.c_int

    def _pack(self, operation, start, inputs=None, capture=None, seal=None):
        arena, plans, cache = bytearray(), [], {}
        def span(value):
            if type(value) is not bytes:
                raise KernelRefused('FINALIZATION_BYTES_REQUIRED')
            first = len(arena) + 1
            if first > MAX_COUNT or len(value) > MAX_COUNT - len(arena):
                raise KernelRefused('FINALIZATION_EXTENT_UNREPRESENTABLE')
            arena.extend(value)
            return Span(first, len(value))
        def optional(value):
            return Optional_Span(0, Span(1, 0)) if value is None else Optional_Span(1, span(value))
        def digest(value):
            if type(value) is not bytes or len(value) != HASH_BYTES:
                raise KernelRefused('FINALIZATION_COMPONENT_DIGEST_INVALID')
            return Digest.from_buffer_copy(value)
        def enum(values, value):
            if value not in values:
                raise KernelRefused('FINALIZATION_ENUM_INVALID')
            return values.index(value)
        def bound(value):
            if type(value) is not StartValue or type(value.required) is not tuple:
                raise KernelRefused('FINALIZATION_START_TYPE')
            for field in ('store_id', 'subject', 'run', 'epoch', 'policy',
                          'verifier_plan', 'base_context', 'parent', 'config', 'repository'):
                if type(getattr(value, field)) is not bytes:
                    raise KernelRefused('FINALIZATION_BYTES_REQUIRED')
            if value.requirement is not None and type(value.requirement) is not bytes:
                raise KernelRefused('FINALIZATION_REQUIREMENT_TYPE')
            if type(value.declaration) is not str:
                raise KernelRefused('FINALIZATION_DECLARATION_TYPE')
            for pair in value.required:
                if type(pair) is not tuple or len(pair) != 2 or any(type(x) is not bytes for x in pair):
                    raise KernelRefused('FINALIZATION_REQUIRED_PAIR_INVALID')
            # All cached fields are immutable primitive bytes/tuples. This is
            # representation sharing, not an admission/equality decision.
            if value in cache:
                return cache[value]
            first = len(plans) + 1
            if first > MAX_COUNT or len(value.required) > MAX_COUNT - len(plans):
                raise KernelRefused('FINALIZATION_ROSTER_EXTENT_UNREPRESENTABLE')
            for pair in value.required:
                if type(pair) is not tuple or len(pair) != 2:
                    raise KernelRefused('FINALIZATION_REQUIRED_PAIR_INVALID')
                plans.append(Required_Row(span(pair[0]), span(pair[1])))
            result = Start(span(value.store_id), span(value.subject), span(value.run),
                span(value.epoch), optional(value.requirement), span(value.policy),
                span(value.verifier_plan), span(value.base_context), digest(value.parent),
                digest(value.config), digest(value.repository), Span(first, len(value.required)),
                enum(DECLARATIONS, value.declaration))
            cache[value] = result
            return result
        def input_value(value):
            if type(value) is not InputValue:
                raise KernelRefused('FINALIZATION_INPUT_TYPE')
            return Input(bound(value.start), span(value.root), span(value.manifests),
                digest(value.filesystem), digest(value.config), digest(value.repository))
        def row(value):
            if type(value) is not UnsealedResult or type(value.wire) is not OwnedRecord:
                raise KernelRefused('FINALIZATION_ROW_TYPE')
            return Row(bound(value.start), span(value.check), span(value.source),
                optional(value.execution), optional(value.verifier), enum(EXECUTION, value.state),
                enum(OUTCOME, value.outcome), span(value.payload), span(value.declared),
                value.wire.native(), value.wire.confinement)
        request = Request()
        request.version, request.operation = 1, operation
        request.start = bound(start)
        if inputs is not None:
            request.inputs = input_value(inputs)
        values = ()
        if capture is not None:
            if type(capture) is not CaptureValue or type(capture.results) is not tuple:
                raise KernelRefused('FINALIZATION_CAPTURE_TYPE')
            if len(capture.results) > MAX_COUNT // C.sizeof(Row):
                raise KernelRefused('FINALIZATION_ROWS_EXTENT_UNREPRESENTABLE')
            values = tuple(row(value) for value in capture.results)
            request.post_root, request.post_manifests = span(capture.post_root), span(capture.post_manifests)
            if type(capture.completion) is not tuple or len(capture.completion) != 2:
                raise KernelRefused('FINALIZATION_COMPLETION_PAIR_INVALID')
            request.completion = Required_Row(span(capture.completion[0]), span(capture.completion[1]))
            request.context, request.source_id = span(capture.context), span(capture.source)
        if seal is not None:
            if type(seal) is not SealValue or type(seal.components) is not ComponentsValue:
                raise KernelRefused('FINALIZATION_SEAL_TYPE')
            request.content = span(seal.content)
            request.environment_root, request.evidence_root = digest(seal.components.environment), digest(seal.components.evidence)
            request.evidence, request.environment = span(seal.evidence), span(seal.environment)
        if len(plans) > MAX_COUNT // C.sizeof(Required_Row):
            raise KernelRefused('FINALIZATION_ROSTER_EXTENT_UNREPRESENTABLE')
        owned_rows, owned_plans = (Row * len(values))(*values), (Required_Row * len(plans))(*plans)
        data = (C.c_uint8 * len(arena)).from_buffer_copy(arena)
        request.data, request.data_length = C.cast(data, C.c_void_p), len(arena)
        request.rows, request.row_count = C.cast(owned_rows, C.c_void_p), len(values)
        request.required, request.required_count = C.cast(owned_plans, C.c_void_p), len(plans)
        return request, (data, owned_rows, owned_plans)

    def _invoke(self, operation, start, inputs=None, capture=None, seal=None):
        try:
            request, owners = self._pack(operation, start, inputs, capture, seal)
            result = Result()
            if self.call(C.byref(request), C.byref(result)) != 0:
                raise KernelRefused('FINALIZATION_NATIVE_TRANSPORT_REFUSED')
            if result.reason != 0:
                raise KernelRefused('FINALIZATION_NATIVE_RELATION_REFUSED')
            return result, request, owners
        except (MemoryError, OverflowError) as exc:
            raise KernelRefused('FINALIZATION_OWNED_STORAGE_UNAVAILABLE') from exc

    @staticmethod
    def _classification(result):
        if result.state >= len(EXECUTION) or result.outcome >= len(OUTCOME) or result.promotion not in (0, 1):
            raise KernelRefused('FINALIZATION_NATIVE_CLASSIFICATION_INVALID')
        return ClassifiedValue(EXECUTION[result.state], OUTCOME[result.outcome], bool(result.promotion))

    def validate_start(self, start):
        self._invoke(0, start)

    def validate_input(self, start, value):
        self._invoke(1, start, value)

    def classify_capture(self, value):
        result, _request, _owners = self._invoke(2, value.start, value.input, value)
        return self._classification(result)

    def _seal(self, value):
        result, request, owners = self._invoke(3, value.capture.start,
            value.capture.input, value.capture, value)
        if result.finalization_state >= len(HISTORY) or result.finalization_outcome >= len(OUTCOME):
            raise KernelRefused('FINALIZATION_NATIVE_SUMMARY_INVALID')
        sealed = SealedValue(value, bytes(result.identity), self._classification(result),
            HISTORY[result.finalization_state], OUTCOME[result.finalization_outcome])
        return sealed, request, owners

    def seal(self, value):
        return self._seal(value)[0]

    def prepare_finalization(self, value):
        sealed, native_request, native_owners = self._seal(value)
        start, capture = value.capture.start, value.capture
        binding = BoundValue(start.store_id, start.subject, value.content, start.run, start.epoch, start.requirement)
        terminal = BoundCapture(binding, capture.source, capture.context,
            sealed.classification.state, sealed.classification.outcome)
        typed = tuple(CheckValue(binding, row.check, row.source, row.execution,
            row.verifier, row.state, row.outcome, row.payload, declared=row.declared)
            for row in capture.results)
        # Exact same-arena projection, with no ordinary pending intent.
        # ContextRow.item spans must name the Seal arena also reconstructed by
        # the native mixed entry; reserializing these rows would change offsets.
        x = native_request
        bound = Binding(x.start.store_id, x.start.subject, x.content, x.start.run,
                        x.start.sequence, x.start.requirement)
        rows = (Check_Row * x.row_count)(*(Check_Row(bound, row.check_id,
            row.source_id, row.execution, row.verifier, row.state, row.outcome,
            row.payload, Facts(), 0, Presence(), row.declared)
            for row in native_owners[1]))
        plans = (Required_Row * x.start.required.length)(*
            native_owners[2][x.start.required.first - 1:
                            x.start.required.first - 1 + x.start.required.length])
        projection = ContextRequest(1, 2, x.data, x.data_length, None, 0,
            Cursor(1, x.start.sequence, x.start.run),
            Capture(bound, x.source_id, x.context,
                EXECUTION.index(sealed.classification.state), OUTCOME.index(sealed.classification.outcome)),
            C.cast(rows, C.c_void_p), len(rows), 0,
            Capture(bound, x.source_id, x.context, 0, 0), None, 0, None, 0,
            C.cast(plans, C.c_void_p), len(plans), x.start.declaration,
            x.inputs.root, x.post_root, x.completion, bound)
        # owned[2] is the original attach() row convention. The data owner is
        # the very same object as native_request.data; all owners survive call.
        owners = (native_owners[0], None, rows, None, None, plans, native_owners)
        return PreparedFinalization(native_request, native_owners, sealed,
            projection, owners, terminal, typed)


def decide_mixed(authority, request, primary, staged, agent):
    """The actual native authority revalidates each selected request kind.

    Both sources retain full owners through the call. An ordinary request
    still takes its original native pending/context/metadata guards. This
    dispatch does not inspect a Python promotion flag or emulate authority.
    """
    from .raw_completion_kernel import PreparedRawEvaluation
    from .core import COLLAPSE_DECISIONS
    from .errors import CoreUnavailable
    def arguments(value):
        if value is None:
            return (0, None, None, None, None)
        if type(value) not in (PreparedFinalization, PreparedRawEvaluation):
            raise CoreUnavailable('complete owned evaluation kind absent')
        metadata = None if value.metadata_context is None else C.byref(value.metadata_context)
        if type(value) is PreparedFinalization:
            return (2, C.byref(value.native_request), None, None, metadata)
        if type(value) is PreparedRawEvaluation:
            return (1, *value.arguments(), metadata)
        raise CoreUnavailable('complete owned evaluation kind absent')
    try:
        call = authority.lib.wl_collapse_decide_finalization_v1
    except AttributeError as exc:
        raise CoreUnavailable('finalization collapse ABI unavailable') from exc
    call.argtypes = ([C.c_void_p] + [U32] + [C.c_void_p] * 4
        + [U32] + [C.c_void_p] * 5 + [C.c_uint8])
    call.restype = C.c_uint8
    needs = authority.dependencies(request)
    primary = primary if needs['primary'] else None
    staged = staged if needs['staged'] else None
    agent = agent if needs['agent'] else None
    raw_agent = None if agent is None else agent.native()
    code = int(call(C.byref(request), *arguments(primary), *arguments(staged),
        None if raw_agent is None else C.byref(raw_agent),
        0 if agent is None else agent.confinement))
    return COLLAPSE_DECISIONS.get(code, 'INVALID_REQUEST')
