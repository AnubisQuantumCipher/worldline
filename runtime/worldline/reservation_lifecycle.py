"""Owned lifecycle plan transport, including original Python comparison protocols.

The existing exact-byte ABI/layout controls remain available; ordinary callers
use the full native-authorized actual-protocol profile, with no legacy fallback.
"""
from __future__ import annotations

import ctypes
from typing import Sequence

from .core import Core
from .errors import CoreUnavailable


class _Row(ctypes.Structure):
    _fields_ = [("first", ctypes.c_size_t), ("length", ctypes.c_size_t),
                ("observed", ctypes.c_uint8)]


def _api(core: Core):
    try:
        version = core._lib.wl_reservation_lifecycle_abi_version
        size = core._lib.wl_reservation_lifecycle_row_size
        offset = core._lib.wl_reservation_lifecycle_row_offset
        plan = core._lib.wl_reservation_lifecycle_plan
    except AttributeError as exc:
        raise CoreUnavailable("selected kernel has no reservation lifecycle API") from exc
    version.argtypes, version.restype = [], ctypes.c_uint32
    size.argtypes, size.restype = [], ctypes.c_size_t
    offset.argtypes, offset.restype = [ctypes.c_uint8], ctypes.c_size_t
    if version() != 1 or size() != ctypes.sizeof(_Row):
        raise CoreUnavailable("reservation lifecycle ABI/layout mismatch")
    for field, (name, _) in enumerate(_Row._fields_, 1):
        if offset(field) != getattr(_Row, name).offset:
            raise CoreUnavailable("reservation lifecycle field offset mismatch", field=name)
    plan.argtypes = [ctypes.c_void_p, ctypes.c_size_t,
                     ctypes.POINTER(_Row), ctypes.c_size_t,
                     ctypes.c_uint8, ctypes.c_uint8, ctypes.c_size_t, ctypes.c_size_t,
                     ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t]
    plan.restype = ctypes.c_uint8
    return plan


def release_plan(identities: Sequence[str], requested: str, *,
                 core: Core | None = None) -> tuple[bool, ...]:
    from .ordinary_reservation_lifecycle import release_plan as native_release
    return tuple(action != 0 for action in native_release(
        identities, requested, core=core, require_unique=True).mask)


def reconcile_plan(identities: Sequence[str], observations: Sequence[object], *,
                   core: Core | None = None) -> tuple[bool, ...]:
    if len(identities) != len(observations):
        raise CoreUnavailable("reservation observation roster length mismatch")
    from .ordinary_reservation_lifecycle import reconcile_plan as native_reconcile
    return tuple(action != 0 for action in native_reconcile(
        observations, core=core, identity_roster=identities).mask)
