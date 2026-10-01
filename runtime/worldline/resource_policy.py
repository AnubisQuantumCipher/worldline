"""Owned-buffer binding to the SPARK numeric admission policy.

Python validates representation and the returned ABI schema. It never compares
resource quantities to authorize/refuse work, and has no Python policy fallback.
Byte extents, custody, stable snapshots and Ada pointer correspondence remain
separate obligations; successful marshalling does not prove their universal truth.
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


class _Input(ctypes.Structure):
    _fields_ = [("outstanding_count", _Quantity), ("concurrency_limit", _Optional),
                ("memory_pressure", _Optional), ("memory_pressure_ceiling", _Quantity),
                ("disk_byte_floor", _Quantity), ("disk_inode_floor", _Quantity),
                ("available_memory", _Quantity), ("withheld_memory", _Quantity),
                ("memory_floor", _Quantity), ("requested_memory", _Quantity)]


class _Disk(ctypes.Structure):
    _fields_ = [("free_bytes", _Quantity), ("free_inodes", _Quantity)]


class _Result(ctypes.Structure):
    _fields_ = [("status", ctypes.c_uint8), ("failed_gate", ctypes.c_uint8),
                ("field", ctypes.c_uint8), ("disk_present", ctypes.c_uint8),
                ("disk_index", ctypes.c_size_t)]


# Exact declaration order in Resource_Admission, separately versioned by this ABI.
_GATES = ("NO_GATE", "CONCURRENCY", "PRESSURE", "DISK_BYTES", "DISK_INODES", "CAPACITY")
_STATUS = ("PASSED", "INSUFFICIENT", "INVALID_REPRESENTATION", "NEGATIVE_DEBIT")
_FIELDS = ("NO_FIELD", "OUTSTANDING_COUNT", "CONCURRENCY_LIMIT", "MEMORY_PRESSURE",
           "MEMORY_PRESSURE_CEILING", "FREE_BYTES", "DISK_BYTE_FLOOR", "FREE_INODES",
           "DISK_INODE_FLOOR", "AVAILABLE_MEMORY", "WITHHELD_MEMORY", "MEMORY_FLOOR",
           "REQUESTED_MEMORY")
_GATE_FIELDS = {
    "CONCURRENCY": {"OUTSTANDING_COUNT", "CONCURRENCY_LIMIT"},
    "PRESSURE": {"MEMORY_PRESSURE", "MEMORY_PRESSURE_CEILING"},
    "DISK_BYTES": {"FREE_BYTES", "DISK_BYTE_FLOOR"},
    "DISK_INODES": {"FREE_INODES", "DISK_INODE_FLOOR"},
    "CAPACITY": {"AVAILABLE_MEMORY", "WITHHELD_MEMORY", "MEMORY_FLOOR", "REQUESTED_MEMORY"},
}


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    """A canonical Ready or numeric refusal; disk_index is Python row indexing."""
    gate: str | None
    disk_index: int | None = None

    @property
    def ready(self) -> bool:
        return self.gate is None


def _size(value: int) -> int:
    """Representation check only; never silently narrow a byte count or index."""
    if ctypes.c_size_t(value).value != value:
        raise OverflowError("resource policy storage index does not fit size_t")
    return value


def _api(core: Core):
    try:
        version = core._lib.wl_resource_policy_abi_version
        size = core._lib.wl_resource_policy_layout_size
        offset = core._lib.wl_resource_policy_layout_offset
        decide = core._lib.wl_resource_policy_admit
    except AttributeError as exc:
        raise CoreUnavailable("the selected kernel has no resource policy API") from exc
    version.argtypes, version.restype = [], ctypes.c_uint32
    if version() != 1:
        raise CoreUnavailable("unsupported resource policy ABI")
    size.argtypes, size.restype = [ctypes.c_uint8], ctypes.c_size_t
    offset.argtypes, offset.restype = [ctypes.c_uint8, ctypes.c_uint8], ctypes.c_size_t
    for selector, record in enumerate((_Quantity, _Optional, _Input, _Disk, _Result), 1):
        if size(selector) != ctypes.sizeof(record):
            raise CoreUnavailable("resource policy record size mismatch", record=record.__name__)
        for field, (name, _) in enumerate(record._fields_, 1):
            if offset(selector, field) != getattr(record, name).offset:
                raise CoreUnavailable("resource policy record offset mismatch", record=record.__name__, field=name)
    decide.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(_Input),
                       ctypes.POINTER(_Disk), ctypes.c_size_t, ctypes.POINTER(_Result)]
    decide.restype = ctypes.c_uint8
    return decide


def _decode(result: _Result, disk_count: int) -> PolicyDecision:
    try:
        status, gate, field = (_STATUS[result.status], _GATES[result.failed_gate], _FIELDS[result.field])
    except IndexError as exc:
        raise CoreUnavailable("resource policy kernel returned an unknown result code") from exc
    if status == "PASSED":
        if (gate, field, result.disk_present, result.disk_index) != ("NO_GATE", "NO_FIELD", 0, 0):
            raise CoreUnavailable("resource policy kernel returned a noncanonical Ready")
        return PolicyDecision(None)
    if gate not in _GATE_FIELDS:
        raise CoreUnavailable("resource policy refusal has no gate")
    if gate in ("DISK_BYTES", "DISK_INODES"):
        if result.disk_present != 1 or not 1 <= result.disk_index <= disk_count:
            raise CoreUnavailable("resource policy refusal has no corresponding filesystem")
        disk_index = result.disk_index - 1
    else:
        if result.disk_present != 0 or result.disk_index != 0:
            raise CoreUnavailable("resource policy refusal has an unexpected filesystem")
        disk_index = None
    if status == "INSUFFICIENT":
        if field != "NO_FIELD":
            raise CoreUnavailable("resource policy numeric refusal has an unexpected field")
        return PolicyDecision(gate, disk_index)
    if field not in _GATE_FIELDS[gate]:
        raise CoreUnavailable("resource policy unknown result names an unrelated field")
    if status == "NEGATIVE_DEBIT" and (gate != "CAPACITY" or field == "AVAILABLE_MEMORY"):
        raise CoreUnavailable("resource policy negative-debit result has an invalid field")
    raise CoreUnavailable("resource policy kernel could not decide the numeric stage",
                          status=status, gate=gate, field=field, disk_index=disk_index)


def decide_policy(*, outstanding_count: int, concurrency_limit: int | None,
                  memory_pressure: int | None, memory_pressure_ceiling: int,
                  disks: Sequence[tuple[int, int]], disk_byte_floor: int, disk_inode_floor: int,
                  available_memory: int, withheld_memory: int, memory_floor: int,
                  requested_memory: int, core: Core | None = None) -> PolicyDecision:
    """Call the real policy kernel with every integer's full signed magnitude.

    Every allocation is private to this call and kept alive until it returns.
    Absent optional payloads are never encoded or read by the Ada decoder.
    Empty magnitude represents zero. No semantic quantity is cast to a C word.
    """
    decide = _api(core if core is not None else Core.shared())
    arena = bytearray()

    def quantity(value: int) -> _Quantity:
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("resource policy quantities must be integers, not booleans")
        magnitude = abs(value)
        raw = magnitude.to_bytes((magnitude.bit_length() + 7) // 8, "little")
        q = _Quantity(_size(len(arena) + 1) if raw else 1, _size(len(raw)), int(value < 0))
        arena.extend(raw)
        return q

    def optional(value: int | None) -> _Optional:
        return _Optional(0, _Quantity()) if value is None else _Optional(1, quantity(value))

    inputs = _Input(quantity(outstanding_count), optional(concurrency_limit), optional(memory_pressure),
                    quantity(memory_pressure_ceiling), quantity(disk_byte_floor), quantity(disk_inode_floor),
                    quantity(available_memory), quantity(withheld_memory), quantity(memory_floor),
                    quantity(requested_memory))
    disk_values = tuple(_Disk(quantity(free_bytes), quantity(free_inodes)) for free_bytes, free_inodes in disks)
    rows = (_Disk * len(disk_values))(*disk_values)
    data = (ctypes.c_uint8 * len(arena)).from_buffer_copy(arena)
    result = _Result()
    transport = int(decide(ctypes.cast(data, ctypes.c_void_p), _size(len(data)),
                           ctypes.byref(inputs), rows, _size(len(rows)), ctypes.byref(result)))
    if transport != 0:
        raise CoreUnavailable("resource policy kernel refused the wire representation", transport=transport)
    return _decode(result, len(rows))
