"""Owned transport for complete evaluation history selection.

Identity is the full builtin Python string encoded with UTF-8 surrogatepass:
no digest, truncation, normalization, prefix match or fixed identity-length cap.
Epochs use arbitrary-length unsigned little-endian magnitudes; missing epochs
remain absent. Storage extents do not cap the numerical epoch value. This module does not allocate, authenticate or derive
epochs, completion facts, current authority or a protected head from the roster.
The caller must supply a stable complete retained snapshot and independently
obtained current/prepared cursors. That producer/custody work remains mandatory.
"""
from __future__ import annotations

import ctypes
from dataclasses import dataclass
from typing import Sequence

from .core import Core
from .errors import CoreUnavailable


@dataclass(frozen=True)
class EvaluationRecord:
    subject: str | None
    content: str | None
    requirement: str | None
    run: str | None
    epoch: int | None
    state: str
    outcome: str | None


@dataclass(frozen=True)
class EvaluationCursor:
    epoch: int | None
    run: str


@dataclass(frozen=True)
class EvaluationQuery:
    subject: str | None
    content: str | None
    requirement: str | None
    current_head: EvaluationCursor | None
    prepared_evidence: EvaluationCursor | None


@dataclass(frozen=True)
class RecordReference:
    kind: str
    index: int | None = None  # Python position only for HISTORY_ENTRY.


@dataclass(frozen=True)
class EvaluationSelection:
    reason: str
    head: RecordReference
    completed_failure: RecordReference


STATES = ("PENDING", "ERROR", "ROLLBACK_FENCE", "COMPLETED")
OUTCOMES = (None, "PASS", "FAIL")
REASONS = ("INPUT_ABSENT", "INPUT_INVALID", "FINALIZATION_INVALID",
           "HISTORY_INVALID", "EVIDENCE_ABSENT", "EVIDENCE_SUPERSEDED",
           "REQUIREMENT_ABSENT", "REQUIREMENT_CHANGED", "EVIDENCE_FENCED",
           "EVALUATION_INCOMPLETE", "EVIDENCE_FAIL_TERMINAL", "READY")
SOURCES = ("ABSENT", "FINALIZATION", "HISTORY_ENTRY")


class _Identity(ctypes.Structure):
    _fields_ = [("present", ctypes.c_uint8), ("first", ctypes.c_size_t),
                ("length", ctypes.c_size_t)]


class _Epoch(ctypes.Structure):
    _fields_ = [("present", ctypes.c_uint8), ("first", ctypes.c_size_t),
                ("length", ctypes.c_size_t)]


class _Cursor(ctypes.Structure):
    _fields_ = [("present", ctypes.c_uint8), ("sequence", _Epoch), ("run", _Identity)]


class _Row(ctypes.Structure):
    _fields_ = [("subject", _Identity), ("content", _Identity),
                ("requirement", _Identity), ("run", _Identity),
                ("sequence", _Epoch), ("state", ctypes.c_uint8),
                ("outcome", ctypes.c_uint8)]


class _Query(ctypes.Structure):
    _fields_ = [("subject", _Identity), ("content", _Identity),
                ("requirement", _Identity), ("current_head", _Cursor),
                ("prepared_evidence", _Cursor)]


class _Selection(ctypes.Structure):
    _fields_ = [("reason", ctypes.c_uint8), ("head_kind", ctypes.c_uint8),
                ("head_index", ctypes.c_size_t), ("failure_kind", ctypes.c_uint8),
                ("failure_index", ctypes.c_size_t)]


def _size(value: int) -> int:
    if value < 0 or ctypes.c_size_t(value).value != value:
        raise CoreUnavailable("evaluation history extent does not fit size_t")
    return value


def _api(core: Core):
    try:
        version = core._lib.wl_evaluation_history_abi_version
        size = core._lib.wl_evaluation_history_layout_size
        offset = core._lib.wl_evaluation_history_layout_offset
        select = core._lib.wl_evaluation_history_select
    except AttributeError as exc:
        raise CoreUnavailable("selected kernel has no evaluation history API") from exc
    version.argtypes, version.restype = [], ctypes.c_uint32
    size.argtypes, size.restype = [ctypes.c_uint8], ctypes.c_size_t
    offset.argtypes, offset.restype = [ctypes.c_uint8, ctypes.c_uint8], ctypes.c_size_t
    if version() != 1:
        raise CoreUnavailable("evaluation history ABI mismatch")
    for kind, record in enumerate((_Identity, _Epoch, _Cursor, _Row, _Query, _Selection), 1):
        if size(kind) != ctypes.sizeof(record):
            raise CoreUnavailable("evaluation history record size mismatch", kind=kind)
        for field, (name, _) in enumerate(record._fields_, 1):
            if offset(kind, field) != getattr(record, name).offset:
                raise CoreUnavailable("evaluation history field offset mismatch", kind=kind, field=name)
    select.argtypes = [ctypes.c_void_p, ctypes.c_size_t,
                      ctypes.POINTER(_Row), ctypes.c_size_t, ctypes.c_uint8,
                      ctypes.POINTER(_Row), ctypes.POINTER(_Query),
                      ctypes.POINTER(_Selection)]
    select.restype = ctypes.c_uint8
    return select


def select_history(history: Sequence[EvaluationRecord], finalization: EvaluationRecord | None,
                   query: EvaluationQuery, *, core: Core | None = None) -> EvaluationSelection:
    """Select only through the actual kernel; retain every supplied roster row.

    No Python newest-PASS search, cursor fabrication or refusal fallback exists.
    Schema/representation failures are distinguished from the typed decisions.
    This pure call does not establish the truth or durability of supplied facts.
    """
    try:
        arena = bytearray()

        def identity(value: str | None) -> _Identity:
            if value is None:
                return _Identity(0, 0, 0)
            if type(value) is not str:
                raise CoreUnavailable("evaluation identity requires a builtin string")
            encoded = value.encode("utf-8", "surrogatepass")
            first = _size(len(arena) + 1)
            arena.extend(encoded)
            return _Identity(1, first, _size(len(encoded)))

        def epoch(value: int | None) -> _Epoch:
            if value is None:
                return _Epoch(0, 0, 0)
            if type(value) is not int or value < 0:
                raise CoreUnavailable("evaluation epoch requires a nonnegative builtin integer")
            encoded = value.to_bytes((value.bit_length() + 7) // 8, "little")
            first = _size(len(arena) + 1)
            arena.extend(encoded)
            return _Epoch(1, first, _size(len(encoded)))

        def cursor(value: EvaluationCursor | None) -> _Cursor:
            if value is None:
                return _Cursor()
            if type(value) is not EvaluationCursor or value.run is None:
                raise CoreUnavailable("evaluation cursor representation is unavailable")
            return _Cursor(1, epoch(value.epoch), identity(value.run))

        def row(value: EvaluationRecord) -> _Row:
            if type(value) is not EvaluationRecord:
                raise CoreUnavailable("evaluation history row is not a typed record")
            if type(value.state) is not str or (value.outcome is not None and type(value.outcome) is not str):
                raise CoreUnavailable("evaluation lifecycle/outcome requires a builtin category string")
            return _Row(identity(value.subject), identity(value.content),
                        identity(value.requirement), identity(value.run), epoch(value.epoch),
                        STATES.index(value.state), OUTCOMES.index(value.outcome))

        if type(query) is not EvaluationQuery:
            raise CoreUnavailable("evaluation history query is not a typed record")
        records = tuple(history)
        rows = (_Row * len(records))(*(row(value) for value in records))
        final = _Row() if finalization is None else row(finalization)
        q = _Query(identity(query.subject), identity(query.content), identity(query.requirement),
                   cursor(query.current_head), cursor(query.prepared_evidence))
        raw = (ctypes.c_uint8 * len(arena)).from_buffer_copy(arena)
        selected = _Selection()
        status = _api(core if core is not None else Core.shared())(
            raw, _size(len(arena)), rows, _size(len(records)),
            int(finalization is not None), ctypes.byref(final), ctypes.byref(q), ctypes.byref(selected))
        if status != 0 or selected.reason >= len(REASONS):
            raise CoreUnavailable("evaluation history kernel transport/result unavailable", status=int(status))

        def reference(kind: int, index: int) -> RecordReference:
            if kind >= len(SOURCES):
                raise CoreUnavailable("evaluation history returned an unknown reference kind")
            if kind == 2:
                if not 1 <= index <= len(records):
                    raise CoreUnavailable("evaluation history returned an invalid history reference")
                return RecordReference(SOURCES[kind], index - 1)
            if index != 0 or (kind == 1 and finalization is None):
                raise CoreUnavailable("evaluation history returned an invalid absent/finalization reference")
            return RecordReference(SOURCES[kind])

        return EvaluationSelection(REASONS[selected.reason],
            reference(selected.head_kind, selected.head_index),
            reference(selected.failure_kind, selected.failure_index))
    except CoreUnavailable:
        raise
    except (MemoryError, OverflowError, ValueError, TypeError) as exc:
        raise CoreUnavailable("evaluation history representation unavailable", error=str(exc)) from exc
