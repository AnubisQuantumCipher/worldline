"""Full selected original native machine/ledger input-output retention.

The original public implementations remain exact. These additive owned-source
observers use the same complete quantity domain, named exceptions and actual
native ABI/decoder, retaining all bytes for independent real-library redecision.
No native result or custody/source/body/cost proof is inferred from a record.
"""
from __future__ import annotations
import ctypes
from typing import Sequence
from .core import Core
from .errors import CoreUnavailable
from . import resource_policy as P
from . import resource_ledger as L

def observe_policy(*, outstanding_count: int, concurrency_limit: int | None,
                  memory_pressure: int | None, memory_pressure_ceiling: int,
                  disks: Sequence[tuple[int, int]], disk_byte_floor: int, disk_inode_floor: int,
                  available_memory: int, withheld_memory: int, memory_floor: int,
                  requested_memory: int, core: Core | None = None):
    """Call the real policy kernel with every integer's full signed magnitude.

    Every allocation is private to this call and kept alive until it returns.
    Absent optional payloads are never encoded or read by the Ada decoder.
    Empty magnitude represents zero. No semantic quantity is cast to a C word.
    """
    decide = P._api(core if core is not None else Core.shared())
    arena = bytearray()

    def quantity(value: int) -> P._Quantity:
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("resource policy quantities must be integers, not booleans")
        magnitude = abs(value)
        raw = magnitude.to_bytes((magnitude.bit_length() + 7) // 8, "little")
        q = P._Quantity(P._size(len(arena) + 1) if raw else 1, P._size(len(raw)), int(value < 0))
        arena.extend(raw)
        return q

    def optional(value: int | None) -> P._Optional:
        return P._Optional(0, P._Quantity()) if value is None else P._Optional(1, quantity(value))

    inputs = P._Input(quantity(outstanding_count), optional(concurrency_limit), optional(memory_pressure),
                    quantity(memory_pressure_ceiling), quantity(disk_byte_floor), quantity(disk_inode_floor),
                    quantity(available_memory), quantity(withheld_memory), quantity(memory_floor),
                    quantity(requested_memory))
    disk_values = tuple(P._Disk(quantity(free_bytes), quantity(free_inodes)) for free_bytes, free_inodes in disks)
    rows = (P._Disk * len(disk_values))(*disk_values)
    data = (ctypes.c_uint8 * len(arena)).from_buffer_copy(arena)
    result = P._Result()
    transport = int(decide(ctypes.cast(data, ctypes.c_void_p), P._size(len(data)),
                           ctypes.byref(inputs), rows, P._size(len(rows)), ctypes.byref(result)))
    if transport != 0:
        raise CoreUnavailable("resource policy kernel refused the wire representation", transport=transport)
    return P._decode(result, len(rows)), {'entry_point':'wl_resource_policy_admit',
        'arena':bytes(arena),'input':bytes(inputs),'disks':bytes(rows),'disk_count':len(rows),
        'output':bytes(result),'transport_status':transport}

def observe_ledger(rows: Sequence[tuple[int, int | None]], *,
                   core: Core | None = None):
    """Compute ordered rows with full signed magnitudes and distinct None usage.

    bool is an integer here, as in the original accounting loop. Noninteger
    numeric protocols are not implemented by this typed ABI and yield unknown.
    All buffers and ctypes records are privately owned for the entire call.
    Counts/offsets below provision storage only; they never calculate accounting.
    """
    try:
        compute = L._api(core if core is not None else Core.shared())
        arena = bytearray()

        def quantity(value: int) -> L._Quantity:
            if not isinstance(value, int):
                raise CoreUnavailable("resource ledger quantities must be integers")
            # Materialize a built-in integer before encoding; do not put an
            # integer magnitude in any machine-word field.
            value = int(value)
            magnitude = abs(value)
            raw = magnitude.to_bytes((magnitude.bit_length() + 7) // 8, "little")
            encoded = L._Quantity(L._size(len(arena) + 1) if raw else 1,
                                L._size(len(raw)), int(value < 0))
            arena.extend(raw)
            return encoded

        encoded_rows = []
        slots = []
        detail_length = 0
        for reserved, used in rows:
            r = quantity(reserved)
            u = L._Optional(0, L._Quantity(1, 0, 0)) if used is None else L._Optional(1, quantity(used))
            # A full extra byte covers a signed difference carry. Summed slot
            # lengths provision the total workspace, including intermediate
            # prefixes. These are byte-extents, never the withheld quantities.
            capacity = L._size(max(r.length, u.value.length if u.present else 0) + 1)
            first = L._size(detail_length + 1)
            detail_length = L._size(detail_length + capacity)
            encoded_rows.append(L._Row(r, u, first, capacity))
            slots.append((first, capacity))
        row_count = L._size(len(encoded_rows))
        L._size(row_count * ctypes.sizeof(L._Row))
        L._size(row_count * ctypes.sizeof(L._Quantity))
        data = (ctypes.c_uint8 * L._size(len(arena))).from_buffer_copy(arena)
        wire_rows = (L._Row * row_count)(*encoded_rows)
        detail_data = (ctypes.c_uint8 * detail_length)()
        total_data = (ctypes.c_uint8 * detail_length)()
        details = (L._Quantity * row_count)()
        result = L._Result()
        transport = int(compute(ctypes.cast(data, ctypes.c_void_p), len(data),
                                wire_rows, row_count,
                                ctypes.cast(detail_data, ctypes.c_void_p), len(detail_data),
                                ctypes.cast(total_data, ctypes.c_void_p), len(total_data),
                                details, ctypes.byref(result)))
        if transport != 0:
            raise CoreUnavailable("resource ledger kernel refused the wire representation", transport=transport)
        return L._decode(result, bytes(detail_data), bytes(total_data), details, slots), {
            'entry_point':'wl_resource_ledger_compute','arena':bytes(arena),'rows':bytes(wire_rows),'row_count':row_count,
            'detail_output':bytes(detail_data),'total_output':bytes(total_data),'details':bytes(details),
            'slots':tuple(slots),'output':bytes(result),'transport_status':transport}
    except CoreUnavailable:
        raise
    except (ValueError, TypeError, OverflowError, MemoryError, ctypes.ArgumentError) as exc:
        raise CoreUnavailable("resource ledger representation or storage could not be prepared",
                              exception_type=type(exc).__name__) from exc
