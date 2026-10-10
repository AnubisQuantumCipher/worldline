"""Owned complete native owner-transition transport, with no Python verdict.

Matching DTOs establish only a value relation. Protected issuer/journal/socket
and actual before-attempt/checkpoint callers must establish authentic facts.
No token mint, reservation, epoch allocation or history editing occurs here.
"""
from __future__ import annotations
import ctypes
from dataclasses import dataclass
from typing import Sequence
from .core import Core
from .errors import CoreUnavailable
from .evaluation_history import EvaluationRecord, EvaluationCursor, STATES, OUTCOMES

OPERATIONS = ("RETRY_EVALUATION", "ADOPT_REQUIREMENT")
GRANT_STATES = ("ISSUED", "RESERVED", "CONSUMED", "REVOKED")
REASONS = ("INPUT_ABSENT", "INPUT_INVALID", "REQUESTER_NOT_OWNER", "ISSUER_MISMATCH",
           "GRANT_UNAVAILABLE", "OPERATION_MISMATCH", "SUBJECT_MISMATCH",
           "CONTENT_MISMATCH", "TRANSACTION_MISMATCH", "REQUIREMENT_MISMATCH",
           "REASON_ABSENT", "RESERVATION_MISMATCH", "EPOCH_MISMATCH", "HISTORY_INVALID",
           "FAILED_HEAD_MISMATCH", "ATTEMPT_MISMATCH", "READY")

@dataclass(frozen=True)
class OwnerGrant:
    action: str
    state: str
    grant: str | None
    use_id: str | None
    issuer: str | None
    principal: str | None
    subject: str | None
    content: str | None
    transaction: str | None
    current_requirement: str | None
    expected_requirement: str | None
    reason: str | None
    issued_grant: str | None
    reserved_grant: str | None
    reserved_use: str | None
    failed_run: EvaluationCursor | None
    prior_head: EvaluationCursor | None
    next_run: EvaluationCursor | None
    epoch: int | None

@dataclass(frozen=True)
class OwnerRequest:
    action: str
    peer: str | None
    owner: str | None
    trusted_issuer: str | None
    subject: str | None
    content: str | None
    transaction: str | None
    current_requirement: str | None
    resulting_requirement: str | None
    current_head: EvaluationCursor | None
    attempt: EvaluationCursor | None
    current_epoch: int | None
    grant: OwnerGrant

class _Identity(ctypes.Structure):
    _fields_ = [("present", ctypes.c_uint8), ("first", ctypes.c_size_t), ("length", ctypes.c_size_t)]
class _Cursor(ctypes.Structure):
    _fields_ = [("present", ctypes.c_uint8), ("sequence", _Identity), ("run", _Identity)]
class _Row(ctypes.Structure):
    _fields_ = [("subject", _Identity), ("content", _Identity), ("requirement", _Identity),
                ("run", _Identity), ("sequence", _Identity), ("state", ctypes.c_uint8), ("outcome", ctypes.c_uint8)]
class _Grant(ctypes.Structure):
    _fields_ = [("action", ctypes.c_uint8), ("state", ctypes.c_uint8)] + [
        (name, _Identity) for name in ("grant", "use_id", "issuer", "principal", "subject", "content",
          "transaction", "current_requirement", "expected_requirement", "reason", "issued_grant",
          "reserved_grant", "reserved_use")] + [("failed_run", _Cursor), ("prior_head", _Cursor),
                                                  ("next_run", _Cursor), ("epoch", _Identity)]
class _Request(ctypes.Structure):
    _fields_ = [("action", ctypes.c_uint8)] + [(name, _Identity) for name in
        ("peer", "owner", "trusted_issuer", "subject", "content", "transaction",
         "current_requirement", "resulting_requirement")] + [("current_head", _Cursor),
         ("attempt", _Cursor), ("current_epoch", _Identity), ("grant", _Grant)]

def _size(value: int) -> int:
    if value < 0 or ctypes.c_size_t(value).value != value:
        raise CoreUnavailable("owner transition extent does not fit size_t")
    return value

def _api(core: Core):
    try:
        version = core._lib.wl_owner_transition_version_v1
        layout = core._lib.wl_owner_transition_layout_v1
        authorize = core._lib.wl_owner_transition_authorize_v1
    except AttributeError as exc:
        raise CoreUnavailable("selected kernel has no owner transition API") from exc
    version.argtypes, version.restype = [], ctypes.c_uint32
    layout.argtypes, layout.restype = [ctypes.c_uint8, ctypes.c_uint8], ctypes.c_size_t
    if version() != 1:
        raise CoreUnavailable("owner transition ABI mismatch")
    for kind, record in enumerate((_Identity, _Cursor, _Row, _Grant, _Request), 1):
        if layout(kind, 0) != ctypes.sizeof(record) or layout(kind, 1) != ctypes.alignment(record):
            raise CoreUnavailable("owner transition layout mismatch", kind=kind)
        for field, (name, _) in enumerate(record._fields_, 2):
            if layout(kind, field) != getattr(record, name).offset:
                raise CoreUnavailable("owner transition field offset mismatch", kind=kind, field=name)
    authorize.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(_Row), ctypes.c_size_t,
                         ctypes.c_uint8, ctypes.POINTER(_Row), ctypes.POINTER(_Request), ctypes.POINTER(ctypes.c_uint8)]
    authorize.restype = ctypes.c_int
    return authorize

def authorize_owner(history: Sequence[EvaluationRecord], finalization: EvaluationRecord | None,
                    request: OwnerRequest, *, core: Core | None = None) -> str:
    """Native value decision retaining all rows and complete byte identities.

    This call does not authenticate supplied owner/grant/issuer/reservation facts.
    The selected protected producer must reserve before the attempt or adoption.
    """
    try:
        arena = bytearray()
        def identity(value: str | None) -> _Identity:
            if value is None:
                return _Identity()
            if type(value) is not str:
                raise CoreUnavailable("owner identity requires a builtin string")
            encoded = value.encode("utf-8", "surrogatepass")
            first = _size(len(arena) + 1)
            arena.extend(encoded)
            return _Identity(1, first, _size(len(encoded)))
        def epoch(value: int | None) -> _Identity:
            if value is None:
                return _Identity()
            if type(value) is not int or value < 0:
                raise CoreUnavailable("owner epoch requires a nonnegative builtin integer")
            encoded = value.to_bytes((value.bit_length() + 7) // 8, "little")
            first = _size(len(arena) + 1)
            arena.extend(encoded)
            return _Identity(1, first, _size(len(encoded)))
        def cursor(value: EvaluationCursor | None) -> _Cursor:
            if value is None:
                return _Cursor()
            if type(value) is not EvaluationCursor or value.run is None:
                raise CoreUnavailable("owner cursor is unavailable")
            return _Cursor(1, epoch(value.epoch), identity(value.run))
        def category(value: str, choices: tuple[str, ...]) -> int:
            if type(value) is not str:
                raise CoreUnavailable("owner category requires a builtin string")
            return choices.index(value)
        def row(value: EvaluationRecord) -> _Row:
            if type(value) is not EvaluationRecord:
                raise CoreUnavailable("owner history row is not a typed record")
            if value.outcome is not None and type(value.outcome) is not str:
                raise CoreUnavailable("owner history outcome requires a builtin category")
            return _Row(identity(value.subject), identity(value.content), identity(value.requirement),
                        identity(value.run), epoch(value.epoch), category(value.state, STATES), OUTCOMES.index(value.outcome))
        if type(request) is not OwnerRequest or type(request.grant) is not OwnerGrant:
            raise CoreUnavailable("owner request/grant is not a typed record")
        records = tuple(history)
        rows = (_Row * len(records))(*(row(value) for value in records))
        final = _Row() if finalization is None else row(finalization)
        g = request.grant
        grant = _Grant(category(g.action, OPERATIONS), category(g.state, GRANT_STATES),
          *(identity(getattr(g, name)) for name in ("grant", "use_id", "issuer", "principal", "subject", "content",
            "transaction", "current_requirement", "expected_requirement", "reason", "issued_grant", "reserved_grant", "reserved_use")),
          cursor(g.failed_run), cursor(g.prior_head), cursor(g.next_run), epoch(g.epoch))
        q = _Request(category(request.action, OPERATIONS),
          *(identity(getattr(request, name)) for name in ("peer", "owner", "trusted_issuer", "subject", "content",
             "transaction", "current_requirement", "resulting_requirement")),
          cursor(request.current_head), cursor(request.attempt), epoch(request.current_epoch), grant)
        data = (ctypes.c_uint8 * len(arena)).from_buffer_copy(arena)
        result = ctypes.c_uint8()
        status = _api(core if core is not None else Core.shared())(
          data, _size(len(arena)), rows, _size(len(records)), int(finalization is not None),
          ctypes.byref(final), ctypes.byref(q), ctypes.byref(result))
        if status != 0 or result.value >= len(REASONS):
            raise CoreUnavailable("owner native transport/result unavailable", status=int(status))
        return REASONS[result.value]
    except CoreUnavailable:
        raise
    except (MemoryError, OverflowError, ValueError, TypeError) as exc:
        raise CoreUnavailable("owner representation unavailable", error=str(exc)) from exc
