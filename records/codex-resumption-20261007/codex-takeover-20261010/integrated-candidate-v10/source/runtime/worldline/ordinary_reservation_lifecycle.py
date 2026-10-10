"""Factual Python protocol acquisition; native ordinary reservation authority.

python-actual-protocol-v1 is an explicit acquisition profile, NOT a claim that
SPARK can execute arbitrary Python methods. Each original __bool__, __eq__,
__ne__, containment or state-membership observation is acquired once, in its
original order, including reflected/subclass dispatch and truth conversion.
Exceptions propagate unchanged. Original objects are retained for projection;
no str/repr/digest replaces their protocols. Native stages authorize which
short-circuited observation may be acquired next and the complete final mask.
"""
from __future__ import annotations
import ctypes
import json
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from .core import Core
from .errors import CoreUnavailable, WorldlineError

_RESOURCE_ERRORS = ContextVar("ordinary_reservation_resource_errors", default=False)

@contextmanager
def resource_error_context():
    token = _RESOURCE_ERRORS.set(True)
    try:
        yield
    finally:
        _RESOURCE_ERRORS.reset(token)

@dataclass(frozen=True, slots=True)
class Plan:
    proceed: bool
    mask: tuple[int, ...]
    position: int

def decide(operation, *, rows=(), core=None, **facts):
    capture = {"schema": "worldline.ordinary-reservation-v1",
               "profile": "python-actual-protocol-v1", "operation": operation,
               "rows": list(rows), **facts}
    raw = json.dumps(capture, ensure_ascii=True, separators=(",", ":"), allow_nan=False).encode("ascii")
    return _transport(raw, len(capture["rows"]), core)

def _transport(raw, row_count, core):
    # No user identity/truth/comparison acquisition occurs inside this catch.
    try:
        return _invoke(raw, row_count, core)
    except CoreUnavailable as exc:
        if _RESOURCE_ERRORS.get():
            raise WorldlineError("RESOURCE_STATE_UNKNOWN",
                                 f"reservation lifecycle plan unavailable: {exc}") from exc
        raise

def _invoke(raw, row_count, core):
    selected = core if core is not None else Core.shared()
    try:
        version = selected._lib.wl_ordinary_reservation_lifecycle_abi_version
        invoke = selected._lib.wl_ordinary_reservation_lifecycle_plan
    except AttributeError as exc:
        raise CoreUnavailable("selected kernel has no ordinary reservation lifecycle API") from exc
    version.argtypes, version.restype = [], ctypes.c_uint32
    if version() != 1:
        raise CoreUnavailable("ordinary reservation lifecycle ABI mismatch")
    invoke.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t,
                       ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_size_t)]
    invoke.restype = ctypes.c_int
    arena = ctypes.create_string_buffer(raw)
    mask = (ctypes.c_uint8 * row_count)()
    code, position = ctypes.c_uint32(), ctypes.c_size_t()
    status = invoke(arena, len(raw), mask, row_count, ctypes.byref(code), ctypes.byref(position))
    if status != 1 or code.value not in (1, 2) or position.value > row_count or any(x > 2 for x in mask):
        raise CoreUnavailable("ordinary reservation lifecycle refused factual capture", status=status, code=code.value)
    return Plan(code.value == 2, tuple(mask), position.value)

def original(value):
    """Lossless builtin payload plus actual custom object acquisition reference.

    Opaque Python object state is not JSON and is not claimed native-equivalent.
    Its real dispatched operator result is the protocol observation authority;
    the reference identifies the retained original object, never a digest key.
    Hex integers avoid Python's decimal digit cap without bounding magnitude.
    """
    cls = type(value)
    captured = {"typeReference": format(id(cls), "x"),
                "reference": format(id(value), "x")}
    if value is None or type(value) is bool:
        captured["value"] = value
    elif issubclass(cls, str):
        captured["utf8SurrogatepassHex"] = str.encode(value, "utf-8", "surrogatepass").hex()
    elif issubclass(cls, int):
        captured["signedHex"] = int.__format__(value, "x")
    elif issubclass(cls, float):
        captured["pythonFloatHex"] = float.hex(value)
    return captured

def comparison(left, right, operator):
    result = left != right if operator == "ne" else left == right
    observed = bool(result)
    return {operator: observed, "left": original(left), "right": original(right),
            "operatorResult": original(result)}

def probe(observation, *, core=None):
    return decide("probe", observation=observation, core=core).proceed

def gate(value):
    # Original truth conversion precedes original string conversion, including
    # exceptions. False/None/empty never opens the ledger or calls str.
    result = bool(value)
    return decide("gate", observation=result, original=original(value)).proceed

def failure_merge(before, after):
    captured_before, captured_after = original(before), original(after)
    result = before
    result |= after
    decide("failure", beforeOriginal=captured_before, afterOriginal=captured_after,
           resultOriginal=original(result))
    return result

def release_plan(identities, requested, *, core=None, require_unique=False):
    rows = [comparison(value, requested, "ne") for value in identities]
    return decide("release", rows=rows, requireUnique=require_unique, core=core)

def attach_unit_plan(reservations, requested, unit):
    rows = []
    for row in reservations:
        captured = comparison(row.reservation_id, requested, "eq")
        unit_comparison = comparison(row.unit, unit, "eq") if probe(captured["eq"]) else None
        captured["unitEq"] = None if unit_comparison is None else unit_comparison["eq"]
        captured["unitComparison"] = unit_comparison
        rows.append(captured)
    return decide("attach-unit", rows=rows)

def identity_match(reservations, requested):
    return decide("identity-match", rows=[comparison(r.reservation_id, requested, "eq") for r in reservations])

def identity_update(reservations, requested):
    # Original performed a SECOND equality pass. Custom stateful protocols
    # may differ; never reuse the membership observation as the update mask.
    return decide("identity-update", rows=[comparison(r.reservation_id, requested, "eq") for r in reservations])

def reconcile_plan(observations, *, core=None, identity_roster=None):
    if identity_roster is None:
        rows = [{"literalFalse": value is False, "original": original(value)}
                for value in observations]
        return decide("reconcile", rows=rows, core=core)
    rows = [{"literalFalse": value is False, "original": original(value),
             "left": original(identity), "builtinString": type(identity) is str}
            for identity, value in zip(identity_roster, observations)]
    return decide("reconcile", rows=rows, requireUnique=True,
                  requireBuiltinStrings=True, core=core)

def unit_valid(unit):
    if not probe(isinstance(unit, str)):
        return False
    if not probe(bool(unit)):
        return False
    if probe(bool("\n" in unit)):
        return False
    return not probe(bool("/" in unit))
