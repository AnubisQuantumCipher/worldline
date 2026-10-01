"""Owned-buffer transport for Resource_Ledger's exact signed accounting.

Only the Ada kernel calculates withheld values and their total. Python encodes
integers, provisions storage, and checks the returned representation; it has no
numeric accounting fallback. Allocation/custody, the full native boundary and
storage-sufficiency proof remain separate obligations.
"""
from __future__ import annotations

import ctypes
from dataclasses import dataclass
from typing import Sequence

from .core import Core
from .errors import CoreUnavailable


class _Quantity(ctypes.Structure):
    _fields_ = [("first", ctypes.c_size_t), ("length", ctypes.c_size_t),
                ("negative", ctypes.c_uint8)]


class _Optional(ctypes.Structure):
    _fields_ = [("present", ctypes.c_uint8), ("value", _Quantity)]


class _Row(ctypes.Structure):
    _fields_ = [("reserved", _Quantity), ("used", _Optional),
                ("output_first", ctypes.c_size_t), ("output_length", ctypes.c_size_t)]


class _Result(ctypes.Structure):
    _fields_ = [("status", ctypes.c_uint8), ("total", _Quantity)]


@dataclass(frozen=True, slots=True)
class LedgerProjection:
    total: int
    withheld: tuple[int, ...]


def _size(value: int) -> int:
    if value < 0 or ctypes.c_size_t(value).value != value:
        raise CoreUnavailable("resource ledger storage extent does not fit size_t")
    return value


def _api(core: Core):
    try:
        version = core._lib.wl_resource_ledger_abi_version
        size = core._lib.wl_resource_ledger_layout_size
        offset = core._lib.wl_resource_ledger_layout_offset
        compute = core._lib.wl_resource_ledger_compute
    except AttributeError as exc:
        raise CoreUnavailable("the selected kernel has no resource ledger API") from exc
    version.argtypes, version.restype = [], ctypes.c_uint32
    if version() != 1:
        raise CoreUnavailable("unsupported resource ledger ABI")
    size.argtypes, size.restype = [ctypes.c_uint8], ctypes.c_size_t
    offset.argtypes, offset.restype = [ctypes.c_uint8, ctypes.c_uint8], ctypes.c_size_t
    for selector, record in enumerate((_Quantity, _Optional, _Row, _Result), 1):
        if size(selector) != ctypes.sizeof(record):
            raise CoreUnavailable("resource ledger record size mismatch", record=record.__name__)
        for field, (name, _) in enumerate(record._fields_, 1):
            if offset(selector, field) != getattr(record, name).offset:
                raise CoreUnavailable("resource ledger record offset mismatch",
                                      record=record.__name__, field=name)
    compute.argtypes = [ctypes.c_void_p, ctypes.c_size_t,
                        ctypes.POINTER(_Row), ctypes.c_size_t,
                        ctypes.c_void_p, ctypes.c_size_t,
                        ctypes.c_void_p, ctypes.c_size_t,
                        ctypes.POINTER(_Quantity), ctypes.POINTER(_Result)]
    compute.restype = ctypes.c_uint8
    return compute


def _decode_quantity(data: bytes, value: _Quantity, slot: tuple[int, int],
                     label: str) -> int:
    """Check the closed canonical/per-slot contract before decoding a value."""
    first, capacity = slot
    start = first - 1
    end = start + capacity
    if first < 1 or capacity < 0 or start > len(data) or end > len(data):
        raise CoreUnavailable("resource ledger output slot is outside its arena", field=label)
    if value.negative not in (0, 1):
        raise CoreUnavailable("resource ledger output has an invalid sign", field=label)
    if value.length == 0:
        if value.first != 1 or value.negative != 0:
            raise CoreUnavailable("resource ledger output has a noncanonical zero", field=label)
        used_end = start
        decoded = 0
    else:
        if value.first != first or value.length > capacity:
            raise CoreUnavailable("resource ledger output escapes its assigned slot", field=label)
        used_end = start + value.length
        if data[used_end - 1] == 0:
            raise CoreUnavailable("resource ledger output has a high zero digit", field=label)
        decoded = int.from_bytes(data[start:used_end], "little")
        if value.negative:
            decoded = -decoded
    if any(data[used_end:end]):
        raise CoreUnavailable("resource ledger output has nonzero slot padding", field=label)
    return decoded


def _decode(result: _Result, detail_data: bytes, total_data: bytes,
            details: Sequence[_Quantity], slots: Sequence[tuple[int, int]]) -> LedgerProjection:
    if result.status != 0:
        raise CoreUnavailable("resource ledger kernel did not compute accounting", status=int(result.status))
    if len(details) != len(slots):
        raise CoreUnavailable("resource ledger output detail count mismatch")
    total = _decode_quantity(total_data, result.total, (1, len(total_data)), "total")
    withheld = []
    cursor = 0
    for index, (value, slot) in enumerate(zip(details, slots)):
        start = slot[0] - 1
        if start < cursor or any(detail_data[cursor:start]):
            raise CoreUnavailable("resource ledger output frame is not canonical", row=index)
        withheld.append(_decode_quantity(detail_data, value, slot, f"row[{index}]"))
        cursor = start + slot[1]
    if any(detail_data[cursor:]):
        raise CoreUnavailable("resource ledger output has a nonzero trailing frame")
    return LedgerProjection(total, tuple(withheld))


def compute_ledger(rows: Sequence[tuple[int, int | None]], *,
                   core: Core | None = None) -> LedgerProjection:
    """Compute ordered rows with full signed magnitudes and distinct None usage.

    bool is an integer here, as in the original accounting loop. Noninteger
    numeric protocols are not implemented by this typed ABI and yield unknown.
    All buffers and ctypes records are privately owned for the entire call.
    Counts/offsets below provision storage only; they never calculate accounting.
    """
    try:
        compute = _api(core if core is not None else Core.shared())
        arena = bytearray()

        def quantity(value: int) -> _Quantity:
            if not isinstance(value, int):
                raise CoreUnavailable("resource ledger quantities must be integers")
            # Materialize a built-in integer before encoding; do not put an
            # integer magnitude in any machine-word field.
            value = int(value)
            magnitude = abs(value)
            raw = magnitude.to_bytes((magnitude.bit_length() + 7) // 8, "little")
            encoded = _Quantity(_size(len(arena) + 1) if raw else 1,
                                _size(len(raw)), int(value < 0))
            arena.extend(raw)
            return encoded

        encoded_rows = []
        slots = []
        detail_length = 0
        for reserved, used in rows:
            r = quantity(reserved)
            u = _Optional(0, _Quantity(1, 0, 0)) if used is None else _Optional(1, quantity(used))
            # A full extra byte covers a signed difference carry. Summed slot
            # lengths provision the total workspace, including intermediate
            # prefixes. These are byte-extents, never the withheld quantities.
            capacity = _size(max(r.length, u.value.length if u.present else 0) + 1)
            first = _size(detail_length + 1)
            detail_length = _size(detail_length + capacity)
            encoded_rows.append(_Row(r, u, first, capacity))
            slots.append((first, capacity))
        row_count = _size(len(encoded_rows))
        _size(row_count * ctypes.sizeof(_Row))
        _size(row_count * ctypes.sizeof(_Quantity))
        data = (ctypes.c_uint8 * _size(len(arena))).from_buffer_copy(arena)
        wire_rows = (_Row * row_count)(*encoded_rows)
        detail_data = (ctypes.c_uint8 * detail_length)()
        total_data = (ctypes.c_uint8 * detail_length)()
        details = (_Quantity * row_count)()
        result = _Result()
        transport = int(compute(ctypes.cast(data, ctypes.c_void_p), len(data),
                                wire_rows, row_count,
                                ctypes.cast(detail_data, ctypes.c_void_p), len(detail_data),
                                ctypes.cast(total_data, ctypes.c_void_p), len(total_data),
                                details, ctypes.byref(result)))
        if transport != 0:
            raise CoreUnavailable("resource ledger kernel refused the wire representation", transport=transport)
        return _decode(result, bytes(detail_data), bytes(total_data), details, slots)
    except CoreUnavailable:
        raise
    except (ValueError, TypeError, OverflowError, MemoryError, ctypes.ArgumentError) as exc:
        raise CoreUnavailable("resource ledger representation or storage could not be prepared",
                              exception_type=type(exc).__name__) from exc
