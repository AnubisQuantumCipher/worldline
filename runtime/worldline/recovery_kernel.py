"""Owned-buffer transport for the SPARK recovery marker selector.

Python reads markers and performs the action returned by the kernel. It does not
compare marker identities or substitute an action when the kernel is unavailable.
This binding does not establish marker custody or durable recovery completion.
"""
from __future__ import annotations

import ctypes

from .core import Core
from .errors import CoreUnavailable

_ACTIONS = ("FINISH_COMMITTED", "ABORT_PREPARED", "AMBIGUOUS")


def select_action(expected: str, live: str | None, prepared: str | None,
                  *, core: Core) -> str:
    try:
        version = core._lib.wl_recovery_abi_version
        decide = core._lib.wl_recovery_select
    except AttributeError as exc:
        raise CoreUnavailable("the selected kernel has no recovery API") from exc
    version.argtypes, version.restype = [], ctypes.c_uint32
    if version() != 1:
        raise CoreUnavailable("unsupported recovery ABI")
    decide.argtypes = [ctypes.c_void_p, ctypes.c_size_t,
                       ctypes.c_uint8, ctypes.c_void_p, ctypes.c_size_t,
                       ctypes.c_uint8, ctypes.c_void_p, ctypes.c_size_t]
    decide.restype = ctypes.c_uint8

    def identity(value: str | None, *, optional: bool):
        if value is None and optional:
            return 0, None, 0
        if not isinstance(value, str):
            raise ValueError("recovery identities must be strings")
        # surrogatepass preserves every Python str admitted by the existing JSON
        # reader. The kernel compares bytes; it imposes no UTF-8 grammar change.
        encoded = value.encode("utf-8", errors="surrogatepass")
        if ctypes.c_size_t(len(encoded)).value != len(encoded):
            raise OverflowError("recovery identity extent does not fit size_t")
        buffer = (ctypes.c_uint8 * len(encoded)).from_buffer_copy(encoded)
        return 1, buffer, len(encoded)

    _, expected_data, expected_length = identity(expected, optional=False)
    live_present, live_data, live_length = identity(live, optional=True)
    prepared_present, prepared_data, prepared_length = identity(prepared, optional=True)
    # Local references retain every allocated buffer through the native call.
    code = int(decide(expected_data, expected_length,
                      live_present, live_data, live_length,
                      prepared_present, prepared_data, prepared_length))
    if code >= len(_ACTIONS):
        raise CoreUnavailable("recovery kernel returned no canonical action", code=code)
    return _ACTIONS[code]
