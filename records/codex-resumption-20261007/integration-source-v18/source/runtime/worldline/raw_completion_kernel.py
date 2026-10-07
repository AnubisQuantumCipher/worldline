"""Full raw completion transport with no D30 fixed roster count.

The original owned request/binding domain is retained. Every new entry invokes
Raw_Roster.Classify inside Ada; Python never passes a promotion success byte.
"""
from dataclasses import dataclass
import ctypes as C
from .completion_kernel import (CompletionKernel, Span, Optional_Span, Cursor,
    Binding, Capture, Facts, Presence, Check_Row, History_Row, Journal_Row,
    Required_Row, Request, Result, BoundValue, CaptureValue, EXECUTION, OUTCOME,
    HISTORY, REASONS, MAX_COUNT, KernelRefused)
from .evaluation_wire import Raw, OwnedRecord

@dataclass
class PreparedRawEvaluation:
    request: Request
    raw: object
    confinement: object
    owned: tuple
    context: object = None
    context_owners: tuple = ()
    metadata_context: object = None
    metadata_owners: tuple = ()
    def arguments(self):
        return C.byref(self.request), C.cast(self.raw, C.c_void_p), C.cast(self.confinement, C.c_void_p)

class RawCompletionKernel(CompletionKernel):
    def __init__(self, library):
        super().__init__(library)
        self.raw_call = self.library.wl_completion_raw_decide_v1
        self.raw_call.argtypes = [C.c_void_p] * 4
        self.raw_call.restype = C.c_int

    def prepare(self, journal, *, current, capture, results, wire_records,
                required, policy, measured_roots, completion, measured_binding):
        result_values, wires = tuple(results), tuple(wire_records)
        if len(result_values) != len(wires) or any(type(x) is not OwnedRecord for x in wires):
            raise KernelRefused('RAW_COMPLETION_COUNT_MISMATCH')
        packed = super().decide(tuple(journal), current=current, capture=capture,
            results=result_values, required=tuple(required), policy=policy,
            measured_roots=measured_roots, completion=completion,
            measured_binding=measured_binding)
        request, owned = packed
        try:
            raw = (Raw * len(wires))(*(item.native() for item in wires))
            confinement = (C.c_uint8 * len(wires))(*(item.confinement for item in wires))
        except (MemoryError, OverflowError) as exc:
            raise KernelRefused('RAW_COMPLETION_OWNED_STORAGE_UNAVAILABLE') from exc
        return PreparedRawEvaluation(request, raw, confinement, owned)

    def classify(self, prepared):
        output = Result()
        if self.raw_call(*prepared.arguments(), C.byref(output)) != 0:
            raise KernelRefused('RAW_COMPLETION_TRANSPORT_REFUSED')
        if output.reason >= len(REASONS) or REASONS[output.reason] not in ('Retain_Terminal', 'Already_Retained'):
            raise KernelRefused('RAW_COMPLETION_BINDING_REFUSED')
        if output.execution_state >= len(EXECUTION) or output.outcome >= len(OUTCOME) or output.promotion not in (0, 1):
            raise KernelRefused('RAW_COMPLETION_RESULT_INVALID')
        return EXECUTION[output.execution_state], OUTCOME[output.outcome], bool(output.promotion)

    def _owned(self, journal, current, capture, results, retained, retained_results, history, required, policy, measured_roots, completion, measured_binding):
        arena = bytearray()
        def span(value):
            if type(value) is not bytes:
                raise KernelRefused('COMPLETION_BYTES_REQUIRED')
            start = len(arena) + 1
            if start > MAX_COUNT or len(value) > MAX_COUNT - len(arena):
                raise KernelRefused('COMPLETION_EXTENT_UNREPRESENTABLE')
            arena.extend(value)
            return Span(start, len(value))
        def optional(value):
            return Optional_Span(0, Span(1, 0)) if value is None else Optional_Span(1, span(value))
        def cursor(value):
            return Cursor(0, Span(1, 0), Span(1, 0)) if value is None else Cursor(1, span(value[0]), span(value[1]))
        def bound(value):
            return Binding(span(value.store_id), span(value.subject), span(value.content),
                           span(value.run), span(value.epoch), optional(value.requirement))
        def enum(values, value):
            if value not in values:
                raise KernelRefused('COMPLETION_ENUM_INVALID')
            return values.index(value)
        def terminal(value):
            return Capture(bound(value.bound), span(value.source), span(value.context),
                           enum(EXECUTION, value.state), enum(OUTCOME, value.outcome))
        def check(value):
            facts = Facts()
            evidence = Presence()
            if value.observations is not None:
                if len(value.observations) != len(Facts._fields_) or any(type(x) is not int or x < 0 or x > C.c_uint32(-1).value for x in value.observations):
                    raise KernelRefused('COMPLETION_OBSERVATION_INVALID')
                facts = Facts(*value.observations)
            if value.evidence is not None:
                if len(value.evidence) != len(Presence._fields_) or any(type(x) is not bool for x in value.evidence):
                    raise KernelRefused('COMPLETION_EVIDENCE_INVALID')
                evidence = Presence(*(int(x) for x in value.evidence))
            return Check_Row(bound(value.bound), span(value.check), span(value.source),
                             optional(value.execution), optional(value.verifier),
                             enum(EXECUTION, value.state), enum(OUTCOME, value.outcome), span(value.payload),
                             facts, enum(("NOT_APPLICABLE", "VERIFIED", "UNTRUSTED"), value.report), evidence, span(value.declared))
        def past(value):
            return History_Row(optional(value.subject), optional(value.content), optional(value.requirement),
                               optional(value.run), optional(value.epoch), enum(HISTORY, value.state), enum(OUTCOME, value.outcome))
        def intent(value):
            if type(value.linked) is not bool:
                raise KernelRefused('COMPLETION_LINK_INVALID')
            b = BoundValue(value.store_id, value.subject, value.content, value.run, value.epoch, value.requirement)
            return Journal_Row(bound(b), cursor(value.previous), int(value.linked))
        def rows(typ, values, convert):
            if len(values) > MAX_COUNT // C.sizeof(typ):
                raise KernelRefused('COMPLETION_EXTENT_UNREPRESENTABLE')
            owned = (typ * len(values))()
            for index, value in enumerate(values):
                owned[index] = convert(value)
            return owned
        js = rows(Journal_Row, journal, intent)
        cs = rows(Check_Row, results, check)
        rs = rows(Check_Row, retained_results, check)
        hs = rows(History_Row, () if history is None else history, past)
        if required is not None and history is not None:
            raise KernelRefused('COMPLETION_OPERATION_CONFLICT')
        required_wire = rows(Required_Row, () if required is None else required,
                             lambda pair: Required_Row(span(pair[0]), span(pair[1])))
        policy_wire = 0 if required is None else enum(('Missing_Declaration', 'Explicit_Empty', 'Required_Checks'), policy)
        if required is not None and (measured_roots is None or completion is None or measured_binding is None):
            raise KernelRefused('COMPLETION_MEASUREMENT_ABSENT')
        before_root, after_root = ((Span(1, 0), Span(1, 0)) if measured_roots is None
                                   else (span(measured_roots[0]), span(measured_roots[1])))
        completion_wire = Required_Row(Span(1, 0), Span(1, 0)) if completion is None else Required_Row(span(completion[0]), span(completion[1]))
        observed_wire = bound(capture.bound if measured_binding is None else measured_binding)
        current_wire, captured_wire = cursor(current), terminal(capture)
        retained_wire = Capture() if retained is None else terminal(retained)
        data = (C.c_ubyte * len(arena)).from_buffer_copy(arena)
        address = lambda value: C.cast(value, C.c_void_p)
        request = Request(1, 2 if required is not None else int(history is not None), address(data), len(arena), address(js), len(js),
            current_wire, captured_wire, address(cs), len(cs), int(retained is not None), retained_wire,
            address(rs), len(rs), address(hs), len(hs), address(required_wire), len(required_wire), policy_wire, before_root, after_root, completion_wire, observed_wire)
        return request, (data, js, cs, rs, hs, required_wire)
