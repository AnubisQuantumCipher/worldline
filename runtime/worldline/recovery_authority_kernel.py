"""Faithful ABI caller for the pure recovery relation.

This module does not authenticate a witness, observe native mappings or replay
protected decision inputs. It accepts their complete typed DTOs and calls the
matching native relation. Authentic protected producers remain required.
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
    _fields_ = [('present', C.c_uint8), ('value', C.c_uint64)]


class Binding(C.Structure):
    _fields_ = [('mode', C.c_uint8)] + [
        (name, OptionalDigest) for name in HASH_FIELDS
    ] + [('policy_epoch', OptionalEpoch), ('resource_epoch', OptionalEpoch)]


class Native(C.Structure):
    _fields_ = [('live_mapping', OptionalDigest), ('live_root', OptionalDigest)]


class Request(C.Structure):
    _fields_ = [('state', C.c_uint8), ('fresh', C.c_uint8),
                ('historical', C.c_uint8), ('grant_eligible', C.c_uint8),
                ('issued_binding', Binding), ('recovered_binding', Binding),
                ('native', Native)]


class Result(C.Structure):
    _fields_ = [('action', C.c_uint8), ('state', C.c_uint8)]


class RecoveryAuthorityKernel:
    def __init__(self, core):
        self.core = core
        try:
            version = core._lib.wl_recovery_authorization_version_v2
            layout = core._lib.wl_recovery_authorization_layout_v2
            self.call = core._lib.wl_recovery_authorization_decide_v2
        except AttributeError as exc:
            raise CoreUnavailable('the selected kernel has no recovery authorization ABI') from exc
        version.argtypes, version.restype = [], C.c_uint32
        layout.argtypes, layout.restype = [C.c_uint32, C.c_uint32], C.c_long
        if version() != 2:
            raise CoreUnavailable('unsupported recovery authorization ABI')
        types = (OptionalDigest, OptionalEpoch, Binding, Native, Request, Result)
        for kind, typ in enumerate(types, 1):
            if layout(kind, 0) != C.sizeof(typ) or layout(kind, 1) != C.alignment(typ):
                raise CoreUnavailable('recovery authorization layout differs')
            for field, (name, _typ) in enumerate(typ._fields_, 2):
                if layout(kind, field) != getattr(typ, name).offset:
                    raise CoreUnavailable('recovery authorization field offset differs', field=name)
        self.call.argtypes = [C.c_void_p, C.c_size_t, C.c_void_p, C.c_size_t]
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
    def _epoch(value):
        answer = OptionalEpoch()
        if value is None:
            return answer
        if type(value) is not int or value < 0 or value > C.c_uint64(-1).value:
            raise ValueError('recovery epoch is not representable')
        answer.present, answer.value = 1, value
        return answer

    @classmethod
    def _binding(cls, value):
        if type(value) is not BoundUse or type(value.mode) is not str or value.mode not in MODES:
            raise ValueError('a complete typed recovery binding is required')
        answer = Binding()
        answer.mode = MODES.index(value.mode)
        for name in HASH_FIELDS:
            setattr(answer, name, cls._digest(getattr(value, name)))
        answer.policy_epoch = cls._epoch(value.policy_epoch)
        answer.resource_epoch = cls._epoch(value.resource_epoch)
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
        return Request(STATES.index(state), FRESH.index(fresh), HISTORICAL.index(historical),
                       int(grant_eligible), self._binding(issued), self._binding(recovered),
                       self._native(native))

    def decide(self, **observations):
        # Keep owned immutable DTOs and fixed raw arenas alive through the call.
        request = self.prepare(**observations)
        result = Result()
        if self.call(C.byref(request), C.sizeof(request),
                     C.byref(result), C.sizeof(result)) != 0:
            raise CoreUnavailable('recovery authorization transport refused')
        if result.action >= len(ACTIONS) or result.state >= len(STATES):
            raise CoreUnavailable('recovery authorization returned no canonical result')
        return ACTIONS[result.action], STATES[result.state]


def binding_record(value):
    """Lossless transport record; this function supplies no authentication."""
    RecoveryAuthorityKernel._binding(value)
    return {field.name: (None if getattr(value, field.name) is None
                        else getattr(value, field.name).hex())
            if field.name in HASH_FIELDS else getattr(value, field.name)
            for field in fields(BoundUse)}


def restore_binding(value):
    expected = {field.name for field in fields(BoundUse)}
    if type(value) is not dict or set(value) != expected:
        raise ValueError('recovery binding schema differs')
    parsed = {}
    for name in HASH_FIELDS:
        raw = value[name]
        if raw is None:
            parsed[name] = None
        elif (type(raw) is str and len(raw) == HASH_BYTES * 2
                and all(character in '0123456789abcdef' for character in raw)):
            parsed[name] = bytes.fromhex(raw)
        else:
            raise ValueError('recovery binding digest encoding differs')
    answer = BoundUse(**parsed, mode=value['mode'], policy_epoch=value['policy_epoch'],
                      resource_epoch=value['resource_epoch'])
    RecoveryAuthorityKernel._binding(answer)
    return answer
