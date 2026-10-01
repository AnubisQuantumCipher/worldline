"""Owned transport for the kernel's exact release/reconciliation plan.

There is no Python identity-selection fallback. Builtin strings use exact
surrogatepass UTF-8 bytes, without normalization or a semantic size cap. Custom
Python comparison protocols are outside this added entry point; the original
direct Ledger.release API remains unchanged until that domain is engineered.
"""
from __future__ import annotations

import ctypes
from typing import Sequence

from .core import Core
from .errors import CoreUnavailable


class _Row(ctypes.Structure):
    _fields_ = [("first", ctypes.c_size_t), ("length", ctypes.c_size_t),
                ("observed", ctypes.c_uint8)]


def _size(value: int) -> int:
    if value < 0 or ctypes.c_size_t(value).value != value:
        raise CoreUnavailable("reservation lifecycle extent does not fit size_t")
    return value


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


def _plan(identities: Sequence[str], requested: str | None,
          observations: Sequence[object] | None, *, core: Core | None) -> tuple[bool, ...]:
    try:
        arena = bytearray()

        def identity(value: str) -> tuple[int, int]:
            if type(value) is not str:
                raise CoreUnavailable("exact identity entry requires a builtin string")
            encoded = value.encode("utf-8", "surrogatepass")
            first = _size(len(arena) + 1)
            arena.extend(encoded)
            return first, _size(len(encoded))

        if observations is not None and len(observations) != len(identities):
            raise CoreUnavailable("reservation observation roster length mismatch")
        rows = []
        for index, value in enumerate(identities):
            first, length = identity(value)
            observed = None if observations is None else observations[index]
            # Preserve original `verdict(row) is False`, without invoking any
            # user-defined equality or truth conversion on the observation.
            code = 2 if observed is False else (1 if observed is True else 0)
            rows.append(_Row(first, length, code))
        if observations is None:
            first, length = identity(requested)
            mode, present = 1, 1
        else:
            first, length, mode, present = 1, 0, 2, 0
        raw = (ctypes.c_uint8 * len(arena)).from_buffer_copy(arena)
        owned_rows = (_Row * len(rows))(*rows)
        mask = (ctypes.c_uint8 * len(rows))()
        status = _api(core if core is not None else Core.shared())(
            raw, _size(len(arena)), owned_rows, _size(len(rows)),
            mode, present, first, length, mask, _size(len(rows)))
        if status not in (2, 3):
            raise CoreUnavailable("reservation lifecycle kernel refused the plan", status=int(status))
        if any(value not in (0, 1) for value in mask):
            raise CoreUnavailable("reservation lifecycle returned an invalid mask")
        result = tuple(value == 1 for value in mask)
        if (status == 3) != any(result):
            raise CoreUnavailable("reservation lifecycle status/mask mismatch")
        return result
    except CoreUnavailable:
        raise
    except (MemoryError, OverflowError, ValueError, TypeError) as exc:
        raise CoreUnavailable("reservation lifecycle representation unavailable", error=str(exc)) from exc


def release_plan(identities: Sequence[str], requested: str, *,
                 core: Core | None = None) -> tuple[bool, ...]:
    return _plan(identities, requested, None, core=core)


def reconcile_plan(identities: Sequence[str], observations: Sequence[object], *,
                   core: Core | None = None) -> tuple[bool, ...]:
    return _plan(identities, None, observations, core=core)
