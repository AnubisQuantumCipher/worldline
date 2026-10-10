"""Factual transport for the pure Manager_Resource_Lifecycle policy.

No fallback or Python terminal/identity/accounting predicate is retained.
"""
from __future__ import annotations

import ctypes
from functools import lru_cache
import json

from .core import Core
from .errors import WorldlineError
from .evaluation_policy import raw_json


@lru_cache(maxsize=1)
def _native():
    core = Core()
    try:
        function = core._lib.wl_manager_resource_lifecycle_v1
    except AttributeError as error:
        raise WorldlineError('CORE_UNAVAILABLE', 'manager resource lifecycle native ABI is unavailable') from error
    function.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p,
                         ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
    function.restype = ctypes.c_int
    return core, function


_TYPE_MRO = type.__dict__['__mro__']
_TYPE_NAME = type.__dict__['__name__']


def _json_kind(value):
    # C json encoding checks actual subtype storage, not __class__ spoofing,
    # metaclass __instancecheck__/__eq__/__getattribute__, or user formatting.
    bases = _TYPE_MRO.__get__(type(value))
    for target in (str, int, float, list, tuple, dict):
        if any(base is target for base in bases):
            return target
    return None


def capture_json(value):
    """Original JSON scalar/container semantics with unrestricted integer atoms.

    Write members in order rather than normalizing a tree: distinct original
    keys may encode to the same string, and key/value failures retain their
    original order. This is storage capture only, never lifecycle policy.
    """
    parts = []
    markers = set()
    default = json.JSONEncoder().default

    def atom(item, kind):
        if kind is str:
            return raw_json(str.__str__(item))
        if kind is int:
            return raw_json(int.__index__(item))
        if kind is float:
            return raw_json(float.__float__(item))
        return None

    def key_text(key):
        kind = _json_kind(key)
        if kind is str:
            return str.__str__(key)
        if kind is float:
            return atom(key, kind)
        if key is True:
            return 'true'
        if key is False:
            return 'false'
        if key is None:
            return 'null'
        if kind is int:
            return atom(key, kind)
        name = _TYPE_NAME.__get__(type(key))
        raise TypeError('keys must be str, int, float, bool or None, not ' + name)

    def write(item):
        if item is None or item is True or item is False:
            parts.append(raw_json(item))
            return
        kind = _json_kind(item)
        if kind is str or kind is int or kind is float:
            parts.append(atom(item, kind))
            return
        if kind is list or kind is tuple:
            # Match PySequence_Fast: exact list/tuple storage is used directly;
            # subclasses acquire their iterator, then materialize that iterator
            # (not the original object's __len__/__bool__) before circularity.
            sequence = item if type(item) is list or type(item) is tuple else list(iter(item))
            if len(sequence) == 0:
                parts.append('[]')
                return
            identity = id(item)
            if identity in markers:
                raise ValueError('Circular reference detected')
            markers.add(identity)
            parts.append('[')
            first = True
            for element in sequence:
                if not first:
                    parts.append(',')
                first = False
                write(element)
            parts.append(']')
            markers.remove(identity)
            return
        if kind is dict:
            # C json's empty-dict fast path uses underlying storage, including
            # for subclasses; nonempty subclasses retain their .items protocol.
            if dict.__len__(item) == 0:
                parts.append('{}')
                return
            identity = id(item)
            if identity in markers:
                raise ValueError('Circular reference detected')
            markers.add(identity)
            items = dict.items(item) if type(item) is dict else item.items()
            if type(item) is not dict and type(items) is not list:
                items = list(iter(items))
            parts.append('{')
            first = True
            for entry in items:
                if _json_kind(entry) is not tuple or tuple.__len__(entry) != 2:
                    raise ValueError('items must return 2-tuples')
                key = tuple.__getitem__(entry, 0)
                element = tuple.__getitem__(entry, 1)
                encoded_key = raw_json(key_text(key))
                if not first:
                    parts.append(',')
                first = False
                parts.extend((encoded_key, ':'))
                write(element)
            parts.append('}')
            markers.remove(identity)
            return
        # Preserve the original encoder's unsupported-value exception instead
        # of a new capture refusal or a supplied substitute representation.
        write(default(item))

    write(value)
    return ''.join(parts)


def _parse_integer(token):
    """Decode a JSON integer in bounded-size chunks, never applying a digit cap."""
    negative = token.startswith('-')
    start = 1 if negative else 0
    value = 0
    for offset in range(start, len(token), 9):
        chunk = token[offset:offset + 9]
        value = value * (10 ** len(chunk)) + int(chunk)
    return -value if negative else value


def decide(profile, *, observer=None):
    payload = capture_json(profile).encode('ascii')
    _, function = _native()
    source = ctypes.create_string_buffer(payload)
    required = ctypes.c_size_t()
    if function(source, len(payload), None, 0, ctypes.byref(required)) != 0:
        raise WorldlineError('CORE_INVALID_MANAGER_CAPTURE', 'native manager capture sizing failed')
    output = ctypes.create_string_buffer(required.value)
    if function(source, len(payload), output, len(output), ctypes.byref(required)) != 1:
        raise WorldlineError('CORE_INVALID_MANAGER_CAPTURE', 'native manager capture decision failed')
    result_bytes = output.raw[:required.value]
    result = json.loads(result_bytes, parse_int=_parse_integer)
    if observer is not None:
        from .raw_observation import retain_observation, optional_bytes
        retain_observation(observer, {'schemaVersion': 1, 'site': 'manager-resource-lifecycle-native',
            'capture': optional_bytes(payload), 'decision': optional_bytes(result_bytes)})
    return result


def terminal_decide(profile, *, observer=None):
    """Reauthorize the complete retained factual terminal profile, never its state label."""
    return decide(profile, observer=observer)


def identity_capture(identity):
    if identity is None:
        return None
    return {'unit': identity.unit, 'invocationId': identity.invocation_id,
            'controlGroup': identity.control_group}


def persisted_capture(unit, value):
    """Capture original dictionary cardinality and original identity field types."""
    def atom(item):
        if isinstance(item, str):
            return item
        if isinstance(item, bytes):
            return {'pythonType': 'bytes', 'hex': bytes.hex(item)}
        return {'pythonTypeReference': hex(id(type(item)))}
    return {'op': 'persisted', 'unit': atom(unit),
            'identityKeyCount': len(value) if isinstance(value, dict) else None,
            'identity': ({name: atom(value.get(name))
                          for name in ('unit', 'invocationId', 'controlGroup')}
                         if isinstance(value, dict) else None)}


def failure_capture(value):
    kind = type(value)
    if kind is bool or kind is str or kind is type(None):
        return value
    if kind is int:
        return {'pythonType': 'builtins.int', 'hex': hex(value)}
    if kind is float:
        return {'pythonType': 'builtins.float', 'hex': value.hex()}
    if kind is bytes:
        return {'pythonType': 'builtins.bytes', 'hex': value.hex()}
    return {'pythonTypeReference': hex(id(kind)),
            'reference': hex(id(value))}


def pipe_capture(manager, process, *, after_failure=False, returncode=None,
                 observer=None, on_failure=None):
    """Acquire original launcher protocols in exactly the order requested natively."""
    unit = process.unit
    capture = {'op': 'owned',
            'unit': str.__str__(unit) if isinstance(unit, str) else failure_capture(unit),
            'managerSame': process.manager is manager,
            'returncode': failure_capture(returncode),
            'returncodeKind': 'exact-int' if type(returncode) is int else 'other',
            'afterFailure': failure_capture(after_failure),
            'launcherProtocols': {}}
    facts = capture['launcherProtocols']
    actual = {}
    while True:
        action = decide(capture, observer=observer)['action']
        if action == 'done':
            break
        try:
            if action == 'pipe_unit_type':
                from .linux.systemd import _UNIT_PATTERN
                _UNIT_PATTERN.fullmatch(unit)
            elif action == 'pipe_argv':
                args = process.launcher.args
                iterator = (list.__iter__(args) if isinstance(args, list) else
                            tuple.__iter__(args) if isinstance(args, tuple) else ())
                capture['argsKind'] = 'tuple' if isinstance(args, tuple) else 'list' if isinstance(args, list) else 'other'
                capture['argsExactBuiltin'] = type(args) is list or type(args) is tuple
                capture['args'] = ([failure_capture(item) for item in iterator]
                                   if isinstance(args, (list, tuple)) else failure_capture(args))
            elif action == 'pipe_nonempty':
                facts['nonempty'] = bool(args)
            elif action == 'pipe_first':
                first = args[0]
                systemd_run = manager.systemd_run
                facts['first'] = failure_capture(first)
                capture['systemdRun'] = failure_capture(systemd_run)
                facts['firstDiffers'] = bool(first != systemd_run)
            elif action == 'pipe_time':
                launched_at_us = process.launched_at_us
                capture['launchedAtUs'] = failure_capture(launched_at_us)
                facts['timeLeZero'] = bool(launched_at_us <= 0)
            elif action == 'pipe_separator':
                contains = '--' in args
                actual['separator'] = args.index('--') if contains else len(args)
                facts['separatorContains'] = contains
                facts['separator'] = failure_capture(actual['separator'])
            elif action == 'pipe_slice':
                actual['options'] = args[1:actual['separator']]
                options = actual['options']
                iterator = (list.__iter__(options) if isinstance(options, list) else
                            tuple.__iter__(options) if isinstance(options, tuple) else None)
                facts['options'] = ([failure_capture(item) for item in iterator]
                                    if iterator is not None else failure_capture(options))
                facts['optionsExactBuiltin'] = type(options) is list or type(options) is tuple
            elif action == 'pipe_unit_count':
                actual['unitOption'] = f'--unit={process.unit}'
                facts['unitOption'] = actual['unitOption']
                actual['unitCount'] = actual['options'].count(actual['unitOption'])
                facts['unitCount'] = failure_capture(actual['unitCount'])
            elif action == 'pipe_prefix_sum':
                actual['prefixSum'] = sum(item.startswith('--unit=') for item in actual['options'])
                facts['prefixSum'] = failure_capture(actual['prefixSum'])
            elif action == 'pipe_pipe_count':
                actual['pipeCount'] = actual['options'].count('--pipe')
                facts['pipeCount'] = failure_capture(actual['pipeCount'])
            elif action in ('pipe_unit_count_compare', 'pipe_prefix_sum_compare', 'pipe_pipe_count_compare'):
                name = {'pipe_unit_count_compare': 'unitCount',
                        'pipe_prefix_sum_compare': 'prefixSum',
                        'pipe_pipe_count_compare': 'pipeCount'}[action]
                facts[name + 'EqualsOne'] = bool(actual[name] == 1)
            elif action == 'pipe_pty':
                facts['ptyAbsent'] = '--pty' not in actual['options']
            elif action == 'pipe_user':
                facts['userPresent'] = '--user' in actual['options']
            elif action == 'pipe_exec':
                facts['execPresent'] = '--service-type=exec' in actual['options']
            elif action == 'pipe_kill':
                facts['killPresent'] = '--property=KillMode=control-group' in actual['options']
            else:
                raise WorldlineError('CORE_INVALID_MANAGER_CAPTURE', 'unknown native launcher acquisition action')
        except BaseException as error:
            if on_failure is not None:
                on_failure(capture, action, error)
            raise
    capture['op'] = 'terminal'
    if type(after_failure) is bool:
        capture['afterFailureTruth'] = after_failure
    return capture
