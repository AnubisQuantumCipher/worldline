"""Original raw reports enter the mapped owned-execution native parser.

JSON decoding below is transport-only. Counts, status, schema, improvement and
percentage are produced by Worldline.Report_Parser, never rederived in Python.
"""
from __future__ import annotations

import ctypes
import json

from .core import Core, CoreUnavailable
from .errors import WorldlineError


def _integer_bytes(value):
    """Decimal transport without Python's configurable int/str digit ceiling."""
    negative = value < 0
    magnitude = abs(value)
    chunks = []
    while magnitude:
        magnitude, chunk = divmod(magnitude, 1_000_000_000)
        chunks.append(chunk)
    if not chunks:
        return b"0"
    text = str(chunks.pop()) + "".join(f"{chunk:09d}" for chunk in reversed(chunks))
    return (("-" if negative else "") + text).encode("ascii")


def _integer_value(text):
    """Native JSON integer transport, not report interpretation."""
    negative = text.startswith("-")
    digits = text[1:] if negative else text
    value = 0
    for start in range(0, len(digits), 9):
        part = digits[start:start + 9]
        value = value * 10 ** len(part) + int(part)
    return -value if negative else value


def parse(core, check, exit_code, stdout, stderr, result):
    core = core if core is not None else Core.shared()
    try:
        version = core._lib.worldline_report_parser_abi
        native = core._lib.worldline_parse_report
    except AttributeError as exc:
        raise CoreUnavailable("owned execution library lacks native raw report parser",
                              path=str(core.library_path)) from exc
    version.argtypes = []
    version.restype = ctypes.c_uint32
    if version() != 1:
        raise CoreUnavailable("owned execution native report parser ABI is incompatible",
                              path=str(core.library_path))
    pointer, extent, integer = ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int
    native.argtypes = [pointer, extent] * 6 + [integer, pointer, extent,
                                             ctypes.POINTER(extent),
                                             ctypes.POINTER(integer),
                                             ctypes.POINTER(integer)]
    native.restype = integer
    # Byte encoding preserves the original unbounded exit domain.
    raw = (check.format.encode("utf-8"), check.profile.encode("utf-8"),
           _integer_bytes(exit_code), stdout, stderr,
           result if result is not None else b"")
    owned = tuple(ctypes.create_string_buffer(value) for value in raw)
    arguments = tuple(item for value, buffer in zip(raw, owned)
                      for item in (ctypes.cast(buffer, pointer), len(value)))
    required, status, classification = extent(), integer(), integer()
    code = native(*arguments, int(result is not None), None, 0,
                  ctypes.byref(required), ctypes.byref(status), ctypes.byref(classification))
    if code != 0 or required.value == 0:
        raise WorldlineError("CORE_REPORT_PARSER_TRANSPORT", "native report sizing failed")
    output = ctypes.create_string_buffer(required.value)
    code = native(*arguments, int(result is not None), ctypes.cast(output, pointer),
                  len(output), ctypes.byref(required), ctypes.byref(status),
                  ctypes.byref(classification))
    if code != 1 or required.value > len(output):
        raise WorldlineError("CORE_REPORT_PARSER_TRANSPORT", "native report snapshot failed")
    if status.value == 2:
        raise WorldlineError("INVALID_CHECK_FORMAT", f"unsupported check format: {check.format}")
    try:
        parsed = json.loads(output.raw[:required.value].decode("utf-8", "strict"),
                            parse_int=_integer_value)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise WorldlineError("CORE_REPORT_PARSER_TRANSPORT", "native report JSON is invalid") from exc
    if not isinstance(parsed, dict) or parsed.get("status") != ("PASS" if status.value == 0 else "FAIL"):
        raise WorldlineError("CORE_REPORT_PARSER_TRANSPORT", "native report status/diagnostic disagree")
    return parsed
