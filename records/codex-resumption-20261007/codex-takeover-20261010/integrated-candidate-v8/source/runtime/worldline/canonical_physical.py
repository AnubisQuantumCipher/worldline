"""Owned full native exchange and historical durable-recognition transport.

The selected C_API recaptures real syscall facts and redecides the complete
SPARK exchange frame. Python never supplies a durable/clean success assertion.
All input owners and disjoint output buffers stay live until the call returns.
Foreign readability, confinement, termination and native correspondence remain
original acceptance obligations, not conclusions from matching ABI lengths.
"""
import ctypes as C
import os
from .core import CCollapseRequest, HASH_BYTES
from .protected_startup import require, protected
from .errors import CoreUnavailable
from .operation_owner_kernel import _owner_mapping, RESOURCE_SYMBOLS, EXCHANGE_SYMBOLS

PHYSICAL_SYMBOLS = ("wl_full_physical_version_v1", "wl_full_physical_layout_v1",
                    "wl_full_physical_exchange_v1", "wl_full_physical_recover_v1",
                    "wl_actuation_decide", "wl_hash_bytes")


def _physical_mapping(principal):
    _owner_mapping(principal, RESOURCE_SYMBOLS + EXCHANGE_SYMBOLS + PHYSICAL_SYMBOLS)


class Entry(C.Structure):
    _fields_ = [('present', C.c_uint8), ('device', C.c_uint64), ('inode', C.c_uint64)]


class Request(C.Structure):
    _fields_ = [('collapse_facts', CCollapseRequest), ('expected_live', Entry), ('observed_live', Entry),
                ('expected_stage', Entry), ('observed_stage', Entry),
                ('expected_marker_digest', C.c_uint8 * HASH_BYTES),
                ('observed_marker_digest', C.c_uint8 * HASH_BYTES),
                ('payload_durable', C.c_uint8), ('recovery_clean', C.c_uint8)]


class Witness(C.Structure):
    _fields_ = [('live_before', Entry), ('stage_before', Entry), ('live_after', Entry), ('stage_after', Entry),
                ('marker_digest', C.c_uint8 * HASH_BYTES), ('decision', C.c_uint8),
                ('exchange_attempted', C.c_uint8), ('syscall_errno', C.c_int),
                ('payload_durable', C.c_uint8), ('recovery_clean', C.c_uint8), ('parents_durable', C.c_uint8)]


def raw(value):
    return C.string_at(C.byref(value), C.sizeof(value))


def entry(path):
    protected(path, directory=True)
    info = path.stat()
    return Entry(1, info.st_dev, info.st_ino)


class FullPhysicalActuator:
    def __init__(self, principal):
        self.p = principal
        _physical_mapping(principal)
        try:
            version = principal.core._lib.wl_full_physical_version_v1
            layout = principal.core._lib.wl_full_physical_layout_v1
            self.call = principal.core._lib.wl_full_physical_exchange_v1
            self.recover_call = principal.core._lib.wl_full_physical_recover_v1
        except AttributeError as exc:
            raise CoreUnavailable('selected full physical native boundary unavailable') from exc
        version.argtypes, version.restype = [], C.c_uint32
        layout.argtypes, layout.restype = [C.c_uint32, C.c_uint32], C.c_long
        require(version() == 1, 'FULL_PHYSICAL_VERSION_CHANGED')
        for kind, typ in enumerate((Entry, Request, Witness), 1):
            require(layout(kind, 0) == C.sizeof(typ) and layout(kind, 1) == C.alignment(typ),
                    'FULL_PHYSICAL_LAYOUT_CHANGED')
            for field, (name, _type) in enumerate(typ._fields_, 2):
                require(layout(kind, field) == getattr(typ, name).offset, 'FULL_PHYSICAL_FIELD_CHANGED')
        arguments = ([C.c_int] * 4 + [C.c_void_p, C.c_size_t, C.c_void_p, C.c_size_t]
                     + [C.c_void_p, C.c_size_t, C.c_size_t] * 8
                     + [C.c_void_p, C.c_size_t, C.c_void_p, C.c_size_t])
        for call in (self.call, self.recover_call):
            call.argtypes, call.restype = arguments, C.c_int
        _physical_mapping(principal)

    def _invoke(self, call, peer, data, transaction, payload, prepared, expected_live, expected_stage, marker):
        _physical_mapping(self.p)
        if peer is not None:
            peer.observation()
        raw_input, arena, storage, rosters = prepared
        marker_parent = transaction / 'mapping' if peer is not None else data / 'live'
        request = Request(raw_input.operation_input.collapse, expected_live, entry(data / 'live'), expected_stage,
                          entry(transaction / 'mapping'), (C.c_uint8 * HASH_BYTES).from_buffer_copy(marker),
                          (C.c_uint8 * HASH_BYTES).from_buffer_copy(self.p.core.hash_bytes(
                              (marker_parent / '.worldline-generation.json').read_bytes())), 0, 0)
        # The native helper disregards these two caller bytes and derives both
        # facts from real fsync/readback and the full original native decision.
        witness = Witness()
        fds = []
        try:
            for path in (data, transaction, payload):
                protected(path, directory=True)
                fds.append(os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC))
            args = [peer.peer.descriptor() if peer is not None else -1, *fds,
                    C.byref(raw_input), C.sizeof(raw_input), storage, len(arena.raw)]
            for roster in rosters:
                args.extend((roster, len(roster), C.sizeof(roster)))
            args.extend((C.byref(request), C.sizeof(request), C.byref(witness), C.sizeof(witness)))
            _physical_mapping(self.p)
            status = call(*args)
            # Preserve actual attempted/errno/uncertain evidence before owner
            # revalidation. Refusal is not retried and uncertainty is not success.
            return {'status': status, 'request': raw(request).hex(), 'witness': raw(witness).hex()}
        finally:
            for fd in fds:
                os.close(fd)

    def exchange(self, peer, data, transaction, prepared, expected_live, expected_stage, marker, *, payload):
        return self._invoke(self.call, peer, data, transaction, payload, prepared, expected_live, expected_stage, marker)

    def recover(self, data, transaction, prepared, expected_live, expected_stage, marker, *, payload):
        # Historical recognition cannot dispatch a syscall or mint a new peer.
        return self._invoke(self.recover_call, None, data, transaction, payload, prepared,
                            expected_live, expected_stage, marker)
