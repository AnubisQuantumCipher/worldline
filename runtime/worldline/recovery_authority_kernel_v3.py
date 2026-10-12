"""Full-domain recovery ABI v3 caller. Raw DTOs confer no authority.

The bounded v2 API remains unchanged. This version requires the matching v3
library and never falls back to v2. Protected capture, historical redecision,
issuer custody and durable one-shot enforcement remain independent obligations.
"""
from __future__ import annotations

import ctypes as C
from dataclasses import dataclass, fields

from .core import HASH_BYTES
from .errors import CoreUnavailable

STATES = ('ISSUED', 'CLAIMED', 'COMPLETED', 'DENIED')
FRESH = ('AUTHORIZED', 'REFUSED')
HISTORICAL = ('UNESTABLISHED', 'HISTORICALLY_AUTHORIZED')
MODES = ('CANDIDATE', 'STAGED', 'CHECKPOINT_RETURN')
ACTIONS = ('REFUSE', 'INVOKE_ACTUATOR', 'RECONCILE_ACTUATOR',
           'SETTLE', 'REPLAY', 'ABORT_USE')
HASH_FIELDS = ['operation','transaction','capability','universe_head','instance','subject','staged_root','current_requirement','resulting_requirement','requester','grant_use','policy_identity','selected_evaluation','history_head','reservation','host','before_prime','before_root','before_mapping','staged_mapping','input_snapshot','kernel_build','kernel_library','kernel_mapping','issuer_head','receipt_head','causal_head']


@dataclass(frozen=True, slots=True, kw_only=True)
class BoundUse:
    mode: str
    operation: bytes | None
    transaction: bytes | None
    capability: bytes | None
    universe_head: bytes | None
    instance: bytes | None
    subject: bytes | None
    staged_root: bytes | None
    current_requirement: bytes | None
    resulting_requirement: bytes | None
    requester: bytes | None
    grant_use: bytes | None
    policy_identity: bytes | None
    selected_evaluation: bytes | None
    history_head: bytes | None
    reservation: bytes | None
    host: bytes | None
    before_prime: bytes | None
    before_root: bytes | None
    before_mapping: bytes | None
    staged_mapping: bytes | None
    input_snapshot: bytes | None
    kernel_build: bytes | None
    kernel_library: bytes | None
    kernel_mapping: bytes | None
    issuer_head: bytes | None
    receipt_head: bytes | None
    causal_head: bytes | None
    policy_epoch: int | None
    resource_epoch: int | None


@dataclass(frozen=True, slots=True, kw_only=True)
class NativeObservation:
    live_mapping: bytes | None
    live_root: bytes | None


Digest = C.c_uint8 * HASH_BYTES


class OptionalDigest(C.Structure):
    _fields_ = [('present', C.c_uint8), ('value', Digest)]


class OptionalEpoch(C.Structure):
    _fields_ = [('present', C.c_uint8), ('negative', C.c_uint8),
                ('first', C.c_int64), ('length', C.c_int64)]


class Binding(C.Structure):
    _fields_ = [('mode', C.c_uint8)] + [
        (name, OptionalDigest) for name in HASH_FIELDS
    ] + [('policy_epoch', OptionalEpoch), ('resource_epoch', OptionalEpoch)]


class Native(C.Structure):
    _fields_ = [('live_mapping', OptionalDigest), ('live_root', OptionalDigest)]


class Request(C.Structure):
    _fields_ = [('schema_version', C.c_uint32), ('state', C.c_uint8),
                ('fresh', C.c_uint8), ('historical', C.c_uint8),
                ('grant_eligible', C.c_uint8), ('issued_binding', Binding),
                ('recovered_binding', Binding), ('native', Native)]


class Result(C.Structure):
    _fields_ = [('action', C.c_uint8), ('state', C.c_uint8)]


@dataclass(frozen=True, slots=True)
class PreparedRequest:
    request: Request
    arena: C.Array
    arena_length: int


class RecoveryAuthorityKernelV3:
    def __init__(self, core):
        self.core = core
        try:
            version = core._lib.wl_recovery_authorization_version_v3
            layout = core._lib.wl_recovery_authorization_layout_v3
            self.call = core._lib.wl_recovery_authorization_decide_v3
        except AttributeError as exc:
            raise CoreUnavailable('the selected kernel has no full-domain recovery ABI') from exc
        version.argtypes, version.restype = [], C.c_uint32
        layout.argtypes, layout.restype = [C.c_uint32, C.c_uint32], C.c_long
        if version() != 3:
            raise CoreUnavailable('unsupported full-domain recovery ABI')
        types = (OptionalDigest, OptionalEpoch, Binding, Native, Request, Result)
        for kind, typ in enumerate(types, 1):
            if layout(kind, 0) != C.sizeof(typ) or layout(kind, 1) != C.alignment(typ):
                raise CoreUnavailable('full-domain recovery layout differs')
            for field, (name, _typ) in enumerate(typ._fields_, 2):
                if layout(kind, field) != getattr(typ, name).offset:
                    raise CoreUnavailable('full-domain recovery field offset differs', field=name)
        self.call.argtypes = [C.c_void_p, C.c_size_t, C.c_void_p, C.c_size_t,
                             C.c_void_p, C.c_size_t]
        self.call.restype = C.c_int

    @staticmethod
    def _digest(value):
        answer = OptionalDigest()
        if value is None:
            return answer
        if type(value) is not bytes or len(value) != HASH_BYTES:
            raise ValueError('recovery digest is malformed')
        answer.present = 1
        answer.value = Digest.from_buffer_copy(value)
        return answer

    @staticmethod
    def _epoch(value, arena):
        answer = OptionalEpoch(first=1)
        if value is None:
            return answer
        if type(value) is not int or value < 0:
            raise ValueError('recovery epoch must be a nonnegative integer or typed absence')
        # Division determines storage length, never numeric admission.
        length = (value.bit_length() + 7) // 8
        encoded = value.to_bytes(length, 'little', signed=False)
        first = len(arena) + 1 if encoded else 1
        # This is the original host span domain, not an unsigned epoch cap.
        # Width is queried from the concrete ABI. This limits storage addresses.
        last_index = (1 << (C.sizeof(C.c_int64) * 8 - 1)) - 1
        if length > last_index or first > last_index or len(arena) > last_index - length:
            raise OverflowError('recovery epoch storage exceeds the original host span extent')
        answer.present, answer.first, answer.length = 1, first, length
        arena.extend(encoded)
        return answer

    @classmethod
    def _binding(cls, value, arena):
        if type(value) is not BoundUse or type(value.mode) is not str or value.mode not in MODES:
            raise ValueError('a complete typed full-domain recovery binding is required')
        answer = Binding()
        answer.mode = MODES.index(value.mode)
        for name in HASH_FIELDS:
            setattr(answer, name, cls._digest(getattr(value, name)))
        answer.policy_epoch = cls._epoch(value.policy_epoch, arena)
        answer.resource_epoch = cls._epoch(value.resource_epoch, arena)
        return answer

    @classmethod
    def _native(cls, value):
        if type(value) is not NativeObservation:
            raise ValueError('a typed native recovery observation is required')
        return Native(cls._digest(value.live_mapping), cls._digest(value.live_root))

    def prepare(self, *, state, issued, recovered, fresh, historical, grant_eligible, native):
        if (type(state) is not str or state not in STATES
                or type(fresh) is not str or fresh not in FRESH
                or type(historical) is not str or historical not in HISTORICAL
                or type(grant_eligible) is not bool):
            raise ValueError('recovery observation category is not canonical')
        arena = bytearray()
        issued_raw, recovered_raw = self._binding(issued, arena), self._binding(recovered, arena)
        request = Request(3, STATES.index(state), FRESH.index(fresh), HISTORICAL.index(historical),
                          int(grant_eligible), issued_raw, recovered_raw, self._native(native))
        # A zero-length arena has an owned backing byte; only the declared length is read.
        backing = (C.c_uint8 * max(1, len(arena)))()
        if arena:
            C.memmove(backing, bytes(arena), len(arena))
        return PreparedRequest(request, backing, len(arena))

    def decide(self, **observations):
        prepared = self.prepare(**observations)
        result = Result()
        if self.call(C.byref(prepared.request), C.sizeof(prepared.request),
                     prepared.arena, prepared.arena_length,
                     C.byref(result), C.sizeof(result)) != 0:
            raise CoreUnavailable('full-domain recovery transport refused')
        if result.action >= len(ACTIONS) or result.state >= len(STATES):
            raise CoreUnavailable('full-domain recovery returned no canonical result')
        return ACTIONS[result.action], STATES[result.state]


def binding_record(value):
    """Versioned lossless DTO serialization; no authentication is supplied.

    Epochs use canonical little-endian magnitude hex so durable serialization
    does not inherit Python's decimal integer-string length limit.
    """
    RecoveryAuthorityKernelV3._binding(value, bytearray())
    record = {'schema_version': 3}
    for field in fields(BoundUse):
        datum = getattr(value, field.name)
        if field.name in HASH_FIELDS:
            record[field.name] = None if datum is None else datum.hex()
        elif field.name in ('policy_epoch', 'resource_epoch'):
            record[field.name] = None if datum is None else datum.to_bytes(
                (datum.bit_length() + 7) // 8, 'little').hex()
        else:
            record[field.name] = datum
    return record


def restore_binding(value):
    expected = {field.name for field in fields(BoundUse)} | {'schema_version'}
    if type(value) is not dict or set(value) != expected or (type(value['schema_version']) is not int or value['schema_version'] != 3):
        raise ValueError('full-domain recovery binding schema differs')
    parsed = {}
    for name in HASH_FIELDS + ['policy_epoch', 'resource_epoch']:
        raw = value[name]
        if raw is None:
            parsed[name] = None
            continue
        if (type(raw) is not str or len(raw) % 2 != 0
                or any(character not in '0123456789abcdef' for character in raw)):
            raise ValueError('full-domain recovery binding encoding differs')
        encoded = bytes.fromhex(raw)
        if name in HASH_FIELDS:
            if len(encoded) != HASH_BYTES:
                raise ValueError('full-domain recovery digest encoding differs')
            parsed[name] = encoded
        else:
            if encoded and encoded[-1] == 0:
                raise ValueError('full-domain recovery epoch has noncanonical padding')
            parsed[name] = int.from_bytes(encoded, 'little', signed=False)
    answer = BoundUse(**parsed, mode=value['mode'])
    RecoveryAuthorityKernelV3._binding(answer, bytearray())
    return answer
