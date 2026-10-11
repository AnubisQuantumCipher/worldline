"""Owned native audit/conjunction transport; supplied bytes are not authority."""
from __future__ import annotations
import ctypes
from dataclasses import dataclass
from .core import Core, CCollapseRequest, COptionalHash
from .errors import CoreUnavailable
from .evaluation_history import EvaluationRecord, EvaluationCursor, STATES, OUTCOMES
from .owner_transitions import (OwnerGrant, OwnerRequest, OPERATIONS, GRANT_STATES,
                                _Identity, _Cursor, _Row, _Grant, _Request, _size)

AUDIT_REASONS = ("INPUT_INVALID", "BEFORE_NOT_AUTHORIZED", "PREFIX_CHANGED", "AFTER_INVALID",
    "ATTEMPT_NOT_COMPLETED_PASS", "USE_NOT_CONSUMED", "CURRENT_BINDING_CHANGED", "READY")
JOIN_REASONS = ("INPUT_INVALID", "ORIGINAL_COLLAPSE_DENIED", "RESULTING_REQUIREMENT_ABSENT",
    "REQUIREMENT_CHANGED", "OWNER_SCOPE_MISMATCH", "OWNER_NOT_AUTHORIZED", "RETRY_NOT_ADMITTED", "READY")

@dataclass(frozen=True)
class UseReceipt:
    consumed: OwnerGrant
    issued_event: str | None
    reserved_event: str | None
    consumed_event: str | None
    consumed_issue: str | None
    consumed_reservation: str | None

@dataclass(frozen=True)
class RetryAudit:
    before_request: OwnerRequest
    receipt: UseReceipt
    current_head: EvaluationCursor | None
    prepared_evidence: EvaluationCursor | None
    current_epoch: int | None

@dataclass(frozen=True)
class FullScope:
    subject: str | None
    content: str | None
    transaction: str | None

class _Audit(ctypes.Structure):
    _fields_ = [("before_request", _Request), ("consumed", _Grant)] + [
        (name, _Identity) for name in ("issued_event", "reserved_event", "consumed_event",
                                     "consumed_issue", "consumed_reservation")] + [
        ("current_head", _Cursor), ("prepared_evidence", _Cursor), ("current_epoch", _Identity)]

class _Scope(ctypes.Structure):
    _fields_ = [("subject", _Identity), ("content", _Identity), ("transaction", _Identity)]

class Owned:
    def __init__(self): self.arena = bytearray()
    def identity(self, value):
        if value is None: return _Identity()
        if type(value) is not str: raise CoreUnavailable("owner full identity requires a builtin string")
        raw = value.encode("utf-8", "surrogatepass"); first = _size(len(self.arena) + 1)
        self.arena.extend(raw); return _Identity(1, first, _size(len(raw)))
    def epoch(self, value):
        if value is None: return _Identity()
        if type(value) is not int or value < 0: raise CoreUnavailable("owner epoch requires nonnegative builtin integer")
        raw = value.to_bytes((value.bit_length() + 7) // 8, "little"); first = _size(len(self.arena) + 1)
        self.arena.extend(raw); return _Identity(1, first, _size(len(raw)))
    def cursor(self, value):
        if value is None: return _Cursor()
        if type(value) is not EvaluationCursor: raise CoreUnavailable("owner cursor requires complete typed value")
        return _Cursor(1, self.epoch(value.epoch), self.identity(value.run))
    def row(self, value):
        if value is None: return _Row()
        if type(value) is not EvaluationRecord: raise CoreUnavailable("owner history requires complete typed row")
        return _Row(self.identity(value.subject), self.identity(value.content), self.identity(value.requirement),
            self.identity(value.run), self.epoch(value.epoch), self.category(value.state, STATES), OUTCOMES.index(value.outcome))
    def category(self, value, choices):
        if type(value) is not str: raise CoreUnavailable("owner category requires builtin string")
        return choices.index(value)
    def grant(self, value):
        if type(value) is not OwnerGrant: raise CoreUnavailable("owner grant requires full typed value")
        return _Grant(self.category(value.action, OPERATIONS), self.category(value.state, GRANT_STATES),
            *(self.identity(getattr(value, name)) for name in ("grant", "use_id", "issuer", "principal", "subject",
              "content", "transaction", "current_requirement", "expected_requirement", "reason", "issued_grant",
              "reserved_grant", "reserved_use")), self.cursor(value.failed_run), self.cursor(value.prior_head),
            self.cursor(value.next_run), self.epoch(value.epoch))
    def request(self, value):
        if value is None: return _Request()
        if type(value) is not OwnerRequest: raise CoreUnavailable("owner request requires full typed value")
        return _Request(self.category(value.action, OPERATIONS), *(self.identity(getattr(value, name)) for name in
            ("peer", "owner", "trusted_issuer", "subject", "content", "transaction", "current_requirement", "resulting_requirement")),
            self.cursor(value.current_head), self.cursor(value.attempt), self.epoch(value.current_epoch), self.grant(value.grant))
    def audit(self, value):
        if value is None: return _Audit()
        if type(value) is not RetryAudit or type(value.receipt) is not UseReceipt:
            raise CoreUnavailable("owner audit/receipt requires complete typed value")
        r=value.receipt
        return _Audit(self.request(value.before_request), self.grant(r.consumed),
            *(self.identity(getattr(r, name)) for name in ("issued_event", "reserved_event", "consumed_event",
                                                         "consumed_issue", "consumed_reservation")),
            self.cursor(value.current_head), self.cursor(value.prepared_evidence), self.epoch(value.current_epoch))
    def scope(self, value):
        if value is None: return _Scope()
        if type(value) is not FullScope: raise CoreUnavailable("owner scope requires complete typed value")
        return _Scope(self.identity(value.subject), self.identity(value.content), self.identity(value.transaction))

def _api(core):
    try:
        version=core._lib.wl_owner_audit_version_v1; layout=core._lib.wl_owner_audit_layout_v1
        decide=core._lib.wl_owner_audit_decide_v1
    except AttributeError as exc: raise CoreUnavailable("selected kernel has no complete owner audit/conjunction API") from exc
    version.argtypes,version.restype=[],ctypes.c_uint32
    layout.argtypes,layout.restype=[ctypes.c_uint8,ctypes.c_uint8],ctypes.c_size_t
    if version()!=1: raise CoreUnavailable("owner audit ABI mismatch")
    for kind,record in enumerate((_Identity,_Cursor,_Row,_Grant,_Request,_Audit,_Scope),1):
        if layout(kind,0)!=ctypes.sizeof(record) or layout(kind,1)!=ctypes.alignment(record):
            raise CoreUnavailable("owner audit record layout mismatch",kind=kind)
        for field,(name,_) in enumerate(record._fields_,2):
            if layout(kind,field)!=getattr(record,name).offset: raise CoreUnavailable("owner audit field layout mismatch",field=name)
    decide.argtypes=[ctypes.c_uint8,ctypes.c_void_p,ctypes.c_size_t,ctypes.POINTER(_Row),ctypes.c_size_t,
        ctypes.POINTER(_Row),ctypes.c_size_t,ctypes.c_uint8,ctypes.POINTER(_Row),ctypes.c_uint8,ctypes.POINTER(_Row),
        ctypes.POINTER(_Audit),ctypes.POINTER(CCollapseRequest),ctypes.POINTER(_Scope),ctypes.POINTER(COptionalHash),
        ctypes.c_uint8,ctypes.POINTER(_Request),ctypes.POINTER(ctypes.c_uint8)]
    decide.restype=ctypes.c_int; return decide

def _decide(mode,before,after,before_final,after_final,audit,original,scope,resulting,adopt,core):
    core=core if core is not None else Core.shared()
    try:
        owned=Owned(); before=tuple(before); after=tuple(after)
        b=(_Row*len(before))(*(owned.row(row) for row in before))
        h=(_Row*len(after))(*(owned.row(row) for row in after))
        bf,af=owned.row(before_final),owned.row(after_final)
        q,s,g=owned.audit(audit),owned.scope(scope),owned.request(adopt)
        c=CCollapseRequest() if original is None else core._raw_collapse_request(original)
        r=core._optional_hash(resulting,"independently resulting requirement")
        data=(ctypes.c_uint8*len(owned.arena)).from_buffer_copy(owned.arena); code=ctypes.c_uint8()
        status=_api(core)(mode,data,_size(len(owned.arena)),b,_size(len(before)),h,_size(len(after)),
            int(before_final is not None),ctypes.byref(bf),int(after_final is not None),ctypes.byref(af),
            ctypes.byref(q),ctypes.byref(c),ctypes.byref(s),ctypes.byref(r),int(adopt is not None),ctypes.byref(g),ctypes.byref(code))
        choices=AUDIT_REASONS if mode==0 else JOIN_REASONS
        if status!=0 or code.value>=len(choices): raise CoreUnavailable("owner audit native transport/result unavailable",status=int(status))
        return choices[code.value]
    except CoreUnavailable: raise
    except (ValueError,TypeError,OverflowError,MemoryError) as exc: raise CoreUnavailable("owner audit representation unavailable") from exc

def decide_retry(before,after,before_final,after_final,audit,*,core=None):
    return _decide(0,before,after,before_final,after_final,audit,None,None,None,None,core)
def authorize_retry_collapse(before,after,before_final,after_final,audit,original,scope,*,core=None):
    return _decide(1,before,after,before_final,after_final,audit,original,scope,None,None,core)
def authorize_checkpoint(history,finalization,original,resulting,scope,adopt,*,core=None):
    return _decide(2,history,(),finalization,None,None,original,scope,resulting,adopt,core)

def authorize_adopt_receipt(history,finalization,audit,original,scope,resulting,*,core=None):
    return _decide(3,history,(),finalization,None,audit,original,scope,resulting,None,core)
