"""Capture complete policy/run operands; render the native correspondence result."""
from __future__ import annotations
import ctypes
import json
from .errors import CoreUnavailable, WorldlineError


def _integer(value):
    # Storage conversion only. Avoid the host's decimal-string digit limit;
    # no numerical cap or policy interpretation is introduced by transport.
    negative = value < 0
    value = abs(value)
    pieces = []
    while value:
        value, digit = divmod(value, 1_000_000_000)
        pieces.append(digit)
    if not pieces:
        return '0'
    text = str(pieces.pop()) + ''.join(f'{digit:09d}' for digit in reversed(pieces))
    return '-' + text if negative else text


def raw_json(value):
    kind = type(value)
    if kind is int:
        return _integer(value)
    if value is None or kind in (bool, float, str):
        return json.dumps(value, ensure_ascii=True, allow_nan=True, separators=(',', ':'))
    if isinstance(value, (tuple, list)):
        return '[' + ','.join(raw_json(item) for item in value) + ']'
    if isinstance(value, dict):
        return '{' + ','.join(json.dumps(key, ensure_ascii=True) + ':' + raw_json(item)
                              for key, item in value.items()) + '}'
    raise WorldlineError('EVALUATION_POLICY_CAPTURE_TYPE',
                         'the complete policy operand has no original JSON representation')


def _call(core, symbol, operands, *, mode=None):
    from .evaluation_producer import capture
    try:
        call = getattr(core._lib, symbol)
    except AttributeError as exc:
        raise CoreUnavailable('complete native policy producer ABI unavailable') from exc
    owners = tuple(ctypes.create_string_buffer(raw_json(capture(item)).encode('ascii'))
                   for item in operands)
    args = []
    types = []
    for owner in owners:
        args.extend((ctypes.cast(owner, ctypes.c_void_p), len(owner.raw) - 1))
        types.extend((ctypes.c_void_p, ctypes.c_size_t))
    if mode is not None:
        args.append(mode)
        types.append(ctypes.c_uint8)
    call.argtypes = types + [ctypes.c_void_p, ctypes.c_size_t]
    call.restype = ctypes.c_size_t
    required = int(call(*args, None, 0))
    if required == 0:
        raise CoreUnavailable('complete native policy producer refused transport')
    output = ctypes.create_string_buffer(required)
    actual = int(call(*args, ctypes.cast(output, ctypes.c_void_p), required))
    if actual != required:
        raise CoreUnavailable('complete native policy producer output changed')
    try:
        return json.loads(output.raw.decode('utf-8', 'strict'))
    except (UnicodeError, ValueError) as exc:
        raise CoreUnavailable('native policy disposition is malformed') from exc


def project(requirement, *, core=None, additional=(), finalization=False):
    from .core import Core
    from .finalize import CheckDeclaration
    core = Core.shared() if core is None else core
    value = _call(core, 'wl_evaluation_policy_project_v1',
                  (requirement, list(additional)), mode=int(finalization))
    if value['status'] != 'COMPLETE':
        raise WorldlineError(value['status'], 'the native original policy source relation refused')
    # This is only decoding native outputs, not deriving the roster in Python.
    declarations = {name: CheckDeclaration(**record)
                    for name, record in value['declarations'].items()}
    return value['required'], value['empty'], declarations


def capture_plan(core, *, rows, invocations, returns, expected_requirement, context):
    value = _call(core, 'wl_evaluation_capture_plan_v1',
                  (rows, invocations, returns, expected_requirement, context))
    if value['status'] != 'COMPLETE':
        raise WorldlineError(value['status'], 'the native ordered original return relation refused capture')
    return value


def protected_status(core, requirement, delta):
    try:
        call = core._lib.wl_protected_paths_touched_v1
    except AttributeError as exc:
        raise CoreUnavailable('native protected-path producer ABI unavailable') from exc
    owners = tuple(ctypes.create_string_buffer(raw_json(value).encode('ascii'))
                   for value in (requirement, delta))
    call.argtypes = [ctypes.c_void_p, ctypes.c_size_t] * 2
    call.restype = ctypes.c_uint8
    code = int(call(owners[0], len(owners[0].raw) - 1,
                    owners[1], len(owners[1].raw) - 1))
    if code not in (0, 1):
        raise CoreUnavailable('native protected-path producer refused transport')
    return ('PASS', 'FAIL')[code]


def acquisitions_closed(core, subject, observed_owners, acquisitions):
    from .core import Core
    from .finalization_journal import encode
    core = Core.shared() if core is None else core
    try:
        call = core._lib.wl_evaluation_acquisitions_closed_v1
    except AttributeError as exc:
        raise CoreUnavailable('native acquisition closure producer ABI unavailable') from exc
    owners = tuple(ctypes.create_string_buffer(encode(value))
                   for value in (subject, observed_owners, acquisitions))
    call.argtypes = [ctypes.c_void_p, ctypes.c_size_t] * 3
    call.restype = ctypes.c_uint8
    args = []
    for owner in owners:
        args.extend((ctypes.cast(owner, ctypes.c_void_p), len(owner.raw) - 1))
    code = int(call(*args))
    if code not in (0, 1):
        raise CoreUnavailable('native acquisition closure producer refused transport')
    return code == 1
