"""Actual Completion.Decide/Apply bridge. No Python authorization fallback.

Owned requests retain full bytes and optionals. Transport success or an Ada
retention decision is not authentication of captures, cursors or deployment.
"""
from __future__ import annotations
import ctypes as C
from dataclasses import dataclass
from pathlib import Path
from .pending_kernel import KernelRefused, MAX_COUNT
from .pending_kernel_v2 import Intent

class Span(C.Structure):
    _fields_ = [("first", C.c_int64), ("length", C.c_int64)]

class Optional_Span(C.Structure):
    _fields_ = [("present", C.c_uint32), ("value", Span)]

class Cursor(C.Structure):
    _fields_ = [("present", C.c_uint32), ("sequence", Span), ("run", Span)]

class Binding(C.Structure):
    _fields_ = [("store_id", Span), ("subject", Span), ("content", Span), ("run", Span), ("sequence", Span), ("requirement", Optional_Span)]

class Journal_Row(C.Structure):
    _fields_ = [("bound", Binding), ("previous", Cursor), ("linked", C.c_uint32)]

class Capture(C.Structure):
    _fields_ = [("bound", Binding), ("source_id", Span), ("context", Span), ("state", C.c_uint32), ("outcome", C.c_uint32)]

class Facts(C.Structure):
    _fields_ = [("source", C.c_uint32), ("status", C.c_uint32), ("channel", C.c_uint32), ("stage", C.c_uint32), ("exit_present", C.c_uint32), ("exit_integer", C.c_uint32), ("supervisor", C.c_uint32), ("supervisor_stopped", C.c_uint32), ("bundle_present", C.c_uint32), ("bundle_is_mapping", C.c_uint32), ("bundle_stable", C.c_uint32), ("bundle_changed", C.c_uint32), ("unsatisfied_imports", C.c_uint32)]

class Presence(C.Structure):
    _fields_ = [("record_identified", C.c_uint32), ("verdict_recorded", C.c_uint32), ("binding_established", C.c_uint32), ("declaration_matches", C.c_uint32), ("bundle_identified", C.c_uint32)]

class Required_Row(C.Structure):
    _fields_ = [("check_id", Span), ("declared", Span)]

class Check_Row(C.Structure):
    _fields_ = [("bound", Binding), ("check_id", Span), ("source_id", Span), ("execution", Optional_Span), ("verifier", Optional_Span), ("state", C.c_uint32), ("outcome", C.c_uint32), ("payload", Span), ("observed", Facts), ("report", C.c_uint32), ("evidence", Presence), ("declared", Span)]

class History_Row(C.Structure):
    _fields_ = [("subject", Optional_Span), ("content", Optional_Span), ("requirement", Optional_Span), ("run", Optional_Span), ("sequence", Optional_Span), ("state", C.c_uint32), ("outcome", C.c_uint32)]

class Request(C.Structure):
    _fields_ = [("version", C.c_uint32), ("operation", C.c_uint32), ("data", C.c_void_p), ("data_length", C.c_int64), ("journal", C.c_void_p), ("journal_count", C.c_int64), ("current", Cursor), ("captured", Capture), ("captured_results", C.c_void_p), ("captured_count", C.c_int64), ("retained_present", C.c_uint32), ("retained", Capture), ("retained_results", C.c_void_p), ("retained_count", C.c_int64), ("history", C.c_void_p), ("history_count", C.c_int64), ("required", C.c_void_p), ("required_count", C.c_int64), ("policy", C.c_uint32), ("before_root", Span), ("after_root", Span), ("completion", Required_Row), ("observed_binding", Binding)]

class Result(C.Structure):
    _fields_ = [("reason", C.c_uint32), ("selected", C.c_int64), ("summary_present", C.c_uint32), ("summary", History_Row), ("execution_state", C.c_uint32), ("outcome", C.c_uint32), ("promotion", C.c_uint32)]

LAYOUTS = (Span, Optional_Span, Cursor, Binding, Journal_Row, Capture, Facts, Presence, Required_Row, Check_Row, History_Row, Request, Result)
# Exact declaration order in the pinned Ada packages; not authority labels.
EXECUTION = ('Not_Attempted', 'Prepared', 'Started', 'Interrupted',
             'Error_Before_Examiner', 'Incomplete_Unknown', 'Evaluator_Incomplete',
             'Unclassified', 'Completed')
OUTCOME = (None, 'PASS', 'FAIL')
HISTORY = ('PENDING', 'ERROR', 'ROLLBACK_FENCE', 'COMPLETED')
REASONS = ('Input_Invalid', 'Pending_Journal_Invalid', 'Pending_Not_Linked',
           'Cursor_Mismatch', 'Run_Absent', 'Capture_Binding_Mismatch',
           'Capture_Results_Invalid', 'Retained_Record_Invalid',
           'Retained_Binding_Mismatch', 'Terminal_Conflict', 'Retain_Terminal',
           'Already_Retained', 'History_Invalid', 'History_Conflict')

@dataclass(frozen=True)
class BoundValue:
    store_id: bytes
    subject: bytes
    content: bytes
    run: bytes
    epoch: bytes
    requirement: bytes | None

@dataclass(frozen=True)
class CaptureValue:
    bound: BoundValue
    source: bytes
    context: bytes
    state: str
    outcome: str | None

@dataclass(frozen=True)
class CheckValue:
    bound: BoundValue
    check: bytes
    source: bytes
    execution: bytes | None
    verifier: bytes | None
    state: str
    outcome: str | None
    payload: bytes
    observations: tuple[int, ...] | None = None
    report: str = "UNTRUSTED"
    evidence: tuple[bool, ...] | None = None
    declared: bytes = b""

@dataclass(frozen=True)
class HistoryValue:
    subject: bytes | None
    content: bytes | None
    requirement: bytes | None
    run: bytes | None
    epoch: bytes | None
    state: str
    outcome: str | None

@dataclass(frozen=True)
class Plan:
    reason: str
    selected: int
    summary: HistoryValue | None
    classification: tuple[str, str | None, bool] | None

class CompletionKernel:
    def __init__(self, library: Path):
        self.library = C.CDLL(str(library))
        try:
            version = self.library.wl_completion_abi_version_v1
            size = self.library.wl_completion_layout_size_v1
            alignment = self.library.wl_completion_layout_alignment_v1
            offset = self.library.wl_completion_layout_offset_v1
            self.call = self.library.wl_completion_decide_v1
        except AttributeError as exc:
            raise KernelRefused('COMPLETION_ABI_UNAVAILABLE') from exc
        version.argtypes, version.restype = [], C.c_uint32
        size.argtypes, size.restype = [C.c_uint32], C.c_int64
        alignment.argtypes, alignment.restype = [C.c_uint32], C.c_int64
        offset.argtypes, offset.restype = [C.c_uint32, C.c_uint32], C.c_int64
        if version() != 1:
            raise KernelRefused('COMPLETION_ABI_VERSION')
        for kind, typ in enumerate(LAYOUTS, 1):
            if size(kind) != C.sizeof(typ) or alignment(kind) != C.alignment(typ):
                raise KernelRefused('COMPLETION_ABI_LAYOUT')
            for field, (name, _) in enumerate(typ._fields_, 1):
                if offset(kind, field) != getattr(typ, name).offset:
                    raise KernelRefused('COMPLETION_ABI_OFFSET')
        self.call.argtypes, self.call.restype = [C.POINTER(Request), C.POINTER(Result)], C.c_int

    def decide(self, journal, *, current, capture: CaptureValue, results,
               retained: CaptureValue | None = None, retained_results=(), history=None, required=None, policy=None, measured_roots=None, completion=None, measured_binding=None) -> Plan:
        try:
            return self._owned(tuple(journal), current, capture, tuple(results), retained,
                               tuple(retained_results), None if history is None else tuple(history),
                               None if required is None else tuple(required), policy, measured_roots, completion, measured_binding)
        except (MemoryError, OverflowError) as exc:
            raise KernelRefused('COMPLETION_OWNED_STORAGE_UNAVAILABLE') from exc

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
        response = Result()
        if self.call(C.byref(request), C.byref(response)) != 0:
            raise KernelRefused('COMPLETION_TRANSPORT_REFUSED')
        if response.reason >= len(REASONS) or response.selected < 0 or response.selected > len(js):
            raise KernelRefused('COMPLETION_RESULT_INVALID')
        reason = REASONS[response.reason]
        admitted = reason in ('Retain_Terminal', 'Already_Retained')
        if response.summary_present not in (0, 1) or bool(response.summary_present) != (admitted and history is not None):
            raise KernelRefused('COMPLETION_RESULT_INVALID')
        if admitted != (response.selected > 0):
            raise KernelRefused('COMPLETION_RESULT_INVALID')
        def read(value):
            if value.present not in (0, 1):
                raise KernelRefused('COMPLETION_RESULT_INVALID')
            if not value.present:
                return None
            first, length = value.value.first, value.value.length
            if first < 1 or length < 0 or (length and (first > len(arena) or length > len(arena) - first + 1)):
                raise KernelRefused('COMPLETION_RESULT_INVALID')
            return bytes(arena[first - 1:first - 1 + length]) if length else b''
        summary = None
        if response.summary_present:
            row = response.summary
            if row.state >= len(HISTORY) or row.outcome >= len(OUTCOME):
                raise KernelRefused('COMPLETION_RESULT_INVALID')
            summary = HistoryValue(read(row.subject), read(row.content), read(row.requirement),
                                   read(row.run), read(row.sequence), HISTORY[row.state], OUTCOME[row.outcome])
        classification = None
        if admitted and required is not None:
            if response.execution_state >= len(EXECUTION) or response.outcome >= len(OUTCOME):
                raise KernelRefused('COMPLETION_RESULT_INVALID')
            if response.promotion not in (0, 1):
                raise KernelRefused('COMPLETION_RESULT_INVALID')
            classification = (EXECUTION[response.execution_state], OUTCOME[response.outcome], bool(response.promotion))
        return Plan(reason, response.selected, summary, classification)
