"""Marshal resource facts into the selected WORLDLINE kernel.

No Python comparison grants admission. Whole quantities use little-endian byte
arrays; byte-length representation and pointer provenance remain binding proof
obligations, distinct from the arithmetic unit's formal proof.
"""
from __future__ import annotations

import ctypes

from .core import Core
from .errors import CoreUnavailable


def _encode(value: int) -> ctypes.Array:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("resource magnitude must be a nonnegative integer")
    raw = value.to_bytes((value.bit_length() + 7) // 8, "little")
    return (ctypes.c_uint8 * len(raw)).from_buffer_copy(raw)


def can_reserve(available: int, withheld: int, floor: int, requested: int,
                *, core: Core | None = None) -> bool:
    if isinstance(available, bool) or not isinstance(available, int):
        raise ValueError("available memory must be an integer")
    selected = core if core is not None else Core.shared()
    try:
        version = selected._lib.wl_resources_abi_version
        decide = selected._lib.wl_resources_can_reserve
    except AttributeError as exc:
        raise CoreUnavailable("the selected kernel has no resource arithmetic API") from exc
    version.argtypes = []
    version.restype = ctypes.c_uint32
    if version() != 1:
        raise CoreUnavailable("unsupported resource arithmetic ABI")
    decide.argtypes = [ctypes.c_uint8] + [ctypes.c_void_p, ctypes.c_size_t] * 4
    decide.restype = ctypes.c_uint8
    buffers = tuple(_encode(value) for value in
                    (abs(available), withheld, floor, requested))
    arguments: list[object] = [int(available < 0)]
    for buffer in buffers:
        arguments.extend((ctypes.cast(buffer, ctypes.c_void_p), len(buffer)))
    result = int(decide(*arguments))
    if result == 0:
        return False
    if result == 1:
        return True
    raise CoreUnavailable("resource kernel refused the input representation", result=result)
