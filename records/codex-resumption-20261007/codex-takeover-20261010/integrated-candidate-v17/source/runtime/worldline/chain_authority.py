"""Owned complete chain transport to the original SPARK Append rules.

Anchors and actual canonical roots must come from the caller's authentic protected
producers. A matching DTO is not a custody or full receipt/effect proof. This module
does not invent genesis, search a matching tail, discard rows or compare chain heads
as an independent authority. Native unavailability refuses without a Python fallback.
"""
from __future__ import annotations
import ctypes
from dataclasses import dataclass
from typing import Sequence
from .core import Core, C_HASH, HASH_BYTES
from .errors import CoreUnavailable

KINDS = ('RECEIPT', 'CAUSAL')
REASONS = ('ANCHOR_ABSENT', 'GENESIS_MISMATCH', 'ROW_ABSENT', 'PAYLOAD_MISMATCH',
           'PREDECESSOR_MISMATCH', 'STORED_HEAD_MISMATCH', 'TAIL_MISMATCH', 'READY')

@dataclass(frozen=True)
class ChainRow:
    previous: bytes | None
    actual_payload_root: bytes | None
    stored_payload_root: bytes | None
    stored_head: bytes | None

@dataclass(frozen=True)
class ChainAnchors:
    kind: str
    observed_genesis: bytes | None
    witnessed_genesis: bytes | None
    witnessed_head: bytes | None

@dataclass(frozen=True)
class ChainResult:
    disposition: str
    head: bytes
    accepted_count: int

class _Digest(ctypes.Structure):
    _fields_ = [('present', ctypes.c_uint8), ('value', C_HASH)]
class _Row(ctypes.Structure):
    _fields_ = [(name, _Digest) for name in
                ('previous', 'actual_payload_root', 'stored_payload_root', 'stored_head')]
class _Anchors(ctypes.Structure):
    _fields_ = [('kind', ctypes.c_uint8)] + [(name, _Digest) for name in
                ('observed_genesis', 'witnessed_genesis', 'witnessed_head')]
class _Result(ctypes.Structure):
    _fields_ = [('disposition', ctypes.c_uint8), ('head', C_HASH),
                ('accepted_count', ctypes.c_int64)]

def _digest(value: bytes | None) -> _Digest:
    if value is None:
        return _Digest()
    if type(value) is not bytes or len(value) != HASH_BYTES:
        raise CoreUnavailable('chain identity must be a complete builtin digest or typed absence')
    return _Digest(1, C_HASH.from_buffer_copy(value))

def _api(core: Core):
    try:
        version = core._lib.wl_chain_authority_version_v1
        layout = core._lib.wl_chain_authority_layout_v1
        replay = core._lib.wl_chain_authority_replay_v1
    except AttributeError as exc:
        raise CoreUnavailable('selected kernel has no complete chain Append/replay API') from exc
    version.argtypes, version.restype = [], ctypes.c_uint32
    layout.argtypes, layout.restype = [ctypes.c_uint32, ctypes.c_uint32], ctypes.c_long
    if version() != 1:
        raise CoreUnavailable('chain authority ABI version mismatch')
    for kind, record in enumerate((_Digest, _Row, _Anchors, _Result), 1):
        if layout(kind, 0) != ctypes.sizeof(record) or layout(kind, 1) != ctypes.alignment(record):
            raise CoreUnavailable('chain authority ABI size/alignment mismatch', kind=kind)
        for field, (name, _) in enumerate(record._fields_, 2):
            if layout(kind, field) != getattr(record, name).offset:
                raise CoreUnavailable('chain authority ABI field offset mismatch', kind=kind, field=name)
    replay.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p,
                       ctypes.c_size_t, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t]
    replay.restype = ctypes.c_int
    return replay

def replay_chain(rows: Sequence[ChainRow], anchors: ChainAnchors, *, core: Core) -> ChainResult:
    try:
        if type(anchors) is not ChainAnchors or type(anchors.kind) is not str:
            raise CoreUnavailable('chain replay requires typed complete anchors')
        retained = tuple(rows)
        if not all(type(row) is ChainRow for row in retained):
            raise CoreUnavailable('chain replay requires the complete typed row roster')
        owned_rows = (_Row * len(retained))(*(
            _Row(*(_digest(getattr(row, name)) for name, _ in _Row._fields_)) for row in retained))
        owned_anchors = _Anchors(KINDS.index(anchors.kind), _digest(anchors.observed_genesis),
                                _digest(anchors.witnessed_genesis), _digest(anchors.witnessed_head))
        owned_result = _Result()
        count = len(retained)
        if ctypes.c_size_t(count).value != count:
            raise CoreUnavailable('chain row storage extent does not fit size_t')
        length = ctypes.sizeof(owned_rows)
        if ctypes.c_size_t(length).value != length:
            raise CoreUnavailable('chain row arena does not fit size_t')
        status = _api(core)(ctypes.byref(owned_anchors), ctypes.sizeof(owned_anchors),
                            owned_rows, count, length,
                            ctypes.byref(owned_result), ctypes.sizeof(owned_result))
        if status != 0:
            raise CoreUnavailable('chain authority native input/transport refused', status=int(status))
        if owned_result.disposition >= len(REASONS) or not 0 <= owned_result.accepted_count <= count:
            raise CoreUnavailable('chain authority returned an invalid typed result')
        return ChainResult(REASONS[owned_result.disposition], bytes(owned_result.head),
                           int(owned_result.accepted_count))
    except CoreUnavailable:
        raise
    except (ValueError, TypeError, OverflowError, MemoryError) as exc:
        raise CoreUnavailable('chain authority owned representation unavailable', error=str(exc)) from exc
