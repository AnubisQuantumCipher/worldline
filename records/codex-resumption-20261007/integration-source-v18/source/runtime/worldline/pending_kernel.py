"""Exact C binding for the typed transition kernel; no Python decision fallback."""
from __future__ import annotations

import ctypes as C
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path

# Storage extents follow the compiled signed index domain, not an epoch value cap.
# Retained JACKAL status=exact parsed=2^63-1; no arithmetic authority claim.
MAX_COUNT = 9223372036854775807


class KernelRefused(RuntimeError):
    pass


class Reason(IntEnum):
    INPUT_INVALID = 0
    JOURNAL_INVALID = 1
    JOURNAL_CURSOR_MISMATCH = 2
    TARGET_CURSOR_MISMATCH = 3
    REPLAY_REQUIRED = 4
    RUN_ALREADY_USED = 5
    EPOCH_PROPOSAL_INVALID = 6
    REPLAY_ABSENT = 7
    RESERVE_NEW = 8
    WRITE_PENDING = 9
    ACKNOWLEDGE_LINK = 10
    ALREADY_LINKED = 11


class Span(C.Structure):
    _fields_ = [("first", C.c_int64), ("length", C.c_int64)]


class Cursor(C.Structure):
    _fields_ = [("present", C.c_uint32), ("sequence", Span), ("run", Span)]


class Row(C.Structure):
    _fields_ = [("store_id", Span), ("subject", Span), ("content", Span),
                ("run", Span), ("sequence", Span), ("previous", Cursor),
                ("linked", C.c_uint32)]


class Request(C.Structure):
    _fields_ = [("version", C.c_uint32), ("operation", C.c_uint32),
                ("data", C.c_void_p), ("data_length", C.c_int64),
                ("rows", C.c_void_p), ("row_count", C.c_int64),
                ("store_id", Span), ("subject", Span), ("content", Span),
                ("run", Span), ("proposed_epoch", Span), ("authority_head", Cursor), ("target_head", Cursor)]


class Result(C.Structure):
    _fields_ = [("reason", C.c_uint32), ("sequence", Span),
                ("selected", C.c_int64)]


@dataclass(frozen=True)
class Intent:
    store_id: bytes
    subject: bytes
    content: bytes
    run: bytes
    epoch: bytes
    previous: tuple[bytes, bytes] | None
    linked: bool


@dataclass(frozen=True)
class Plan:
    reason: Reason
    epoch: bytes
    selected: int



class PendingKernel:
    """Owned buffers live through the call. Raw foreign pointer validity is
    outside the SPARK core; ABI/native/storage correspondence is still required.
    Loading a library is not authentication of an observation or its producer.
    """

    def __init__(self, library: Path):
        self.library = C.CDLL(str(library))
        try:
            version = self.library.wl_pending_abi_version_v1
            size = self.library.wl_pending_layout_size_v1
            alignment = self.library.wl_pending_layout_alignment_v1
            offset = self.library.wl_pending_layout_offset_v1
            self.call = self.library.wl_pending_decide_v1
        except AttributeError as exc:
            raise KernelRefused("KERNEL_LAYOUT_API_UNAVAILABLE") from exc
        version.argtypes, version.restype = [], C.c_uint32
        size.argtypes, size.restype = [C.c_uint32], C.c_int64
        alignment.argtypes, alignment.restype = [C.c_uint32], C.c_int64
        offset.argtypes, offset.restype = [C.c_uint32, C.c_uint32], C.c_int64
        if version() != 1:
            raise KernelRefused("KERNEL_ABI_VERSION_MISMATCH")
        for kind, record in enumerate((Span, Cursor, Row, Request, Result), 1):
            if size(kind) != C.sizeof(record):
                raise KernelRefused("KERNEL_ABI_SIZE_MISMATCH")
            if alignment(kind) != C.alignment(record):
                raise KernelRefused("KERNEL_ABI_ALIGNMENT_MISMATCH")
            for field, (name, _) in enumerate(record._fields_, 1):
                if offset(kind, field) != getattr(record, name).offset:
                    raise KernelRefused("KERNEL_ABI_OFFSET_MISMATCH")
        self.call.argtypes = [C.POINTER(Request), C.POINTER(Result)]
        self.call.restype = C.c_int

    def decide(self, rows: list[Intent], *, store_id: bytes, subject: bytes,
               content: bytes, run: bytes, authority: tuple[bytes, bytes] | None,
               target: tuple[bytes, bytes] | None, proposed_epoch: bytes, replay: bool) -> Plan:
        try:
            return self._decide_owned(rows, store_id=store_id, subject=subject,
                content=content, run=run, authority=authority, target=target,
                proposed_epoch=proposed_epoch, replay=replay)
        except (MemoryError, OverflowError) as exc:
            raise KernelRefused("OWNED_TRANSPORT_ALLOCATION_UNAVAILABLE") from exc

    def _decide_owned(self, rows: list[Intent], *, store_id: bytes, subject: bytes,
                      content: bytes, run: bytes, authority: tuple[bytes, bytes] | None,
                      target: tuple[bytes, bytes] | None, proposed_epoch: bytes,
                      replay: bool) -> Plan:
        # Capture the ordered roster before sizing or packing it. Every encoded
        # scalar is then copied into owned ctypes rows/request/arena kept alive
        # through the call and result-span copy. No foreign arena is borrowed.
        records = tuple(rows)
        arena = bytearray()

        def span(value: bytes) -> Span:
            if type(value) is not bytes:
                raise KernelRefused("IDENTITY_REPRESENTATION_INVALID")
            start = len(arena) + 1
            # These bounds protect the ABI conversion, not a smaller profile.
            if start > MAX_COUNT or len(value) > MAX_COUNT - len(arena):
                raise KernelRefused("ABI_EXTENT_UNREPRESENTABLE")
            arena.extend(value)
            return Span(start, len(value))

        def cursor(value: tuple[bytes, bytes] | None) -> Cursor:
            if value is None:
                return Cursor(0, Span(1, 0), Span(1, 0))
            return Cursor(1, span(value[0]), span(value[1]))

        if len(records) > MAX_COUNT or len(records) > MAX_COUNT // C.sizeof(Row):
            raise KernelRefused("ABI_EXTENT_UNREPRESENTABLE")
        wire = (Row * len(records))()
        for index, row in enumerate(records):
            if type(row.linked) is not bool:
                raise KernelRefused("LINK_REPRESENTATION_INVALID")
            wire[index] = Row(span(row.store_id), span(row.subject), span(row.content),
                              span(row.run), span(row.epoch), cursor(row.previous),
                              int(row.linked))
        store_span, subject_span, content_span, run_span = map(
            span, (store_id, subject, content, run))
        proposed_span = span(proposed_epoch)
        authority_cursor, target_cursor = cursor(authority), cursor(target)
        data = (C.c_ubyte * len(arena)).from_buffer_copy(arena)
        request = Request(1, int(replay), C.cast(data, C.c_void_p), len(arena),
                          C.cast(wire, C.c_void_p), len(records), store_span, subject_span,
                          content_span, run_span, proposed_span, authority_cursor, target_cursor)
        result = Result()
        status = self.call(C.byref(request), C.byref(result))
        if status != 0:
            raise KernelRefused("KERNEL_TRANSPORT_REFUSED")
        try:
            reason = Reason(result.reason)
        except ValueError as exc:
            raise KernelRefused("KERNEL_RESULT_INVALID") from exc
        if result.selected < 0 or result.selected > len(records):
            raise KernelRefused("KERNEL_RESULT_INVALID")
        first, length = result.sequence.first, result.sequence.length
        if first < 1 or length < 0 or (length and
                (first > len(arena) or length > len(arena) - first + 1)):
            raise KernelRefused("KERNEL_RESULT_INVALID")
        value = bytes(arena[first - 1:first - 1 + length]) if length else b""
        return Plan(reason, value, result.selected)
