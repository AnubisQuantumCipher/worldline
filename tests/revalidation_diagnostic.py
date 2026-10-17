"""Retain actual failing evaluation inputs before temporary fixtures clean up.

Run only through a separately reviewed controlled diagnostic action. The exact
unittest arguments, tests, assertions, runtime calls and native decisions remain
in force. This observer is diagnostic evidence, not ordinary acceptance or proof.
"""
from __future__ import annotations

import base64
import ctypes
import dataclasses
from functools import wraps
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from diagnostic_value_stream import write_record as _write_record


_refusals = []


def _owned(value):
    """Copy named actual values without dereferencing foreign pointers."""
    if value is None or type(value) in (bool, int, float, str):
        return value
    if type(value) is bytes:
        return {'type': 'bytes', 'base64': base64.b64encode(value).decode('ascii')}
    if type(value) in (list, tuple):
        return {'type': type(value).__name__, 'items': [_owned(item) for item in value]}
    if type(value) is dict:
        return {'type': 'dict', 'items': [[_owned(key), _owned(item)]
                                        for key, item in value.items()]}
    if isinstance(value, Path):
        return {'type': 'path', 'pathBytes': _owned(os.fsencode(value))}
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {'type': type(value).__module__ + '.' + type(value).__qualname__,
                'fields': {field.name: _owned(getattr(value, field.name))
                           for field in dataclasses.fields(value)}}
    if isinstance(value, (ctypes.Structure, ctypes.Array)):
        # Copy the owned ABI object itself. Pointer fields are addresses only;
        # their targets are never read by this observer.
        return {'type': type(value).__name__, 'abiBytes': _owned(bytes(value))}
    raise TypeError('diagnostic value not covered: ' + type(value).__qualname__)


def _record(site, values):
    try:
        _write_record(sys.stderr, site, values)
    except Exception as error:
        # A diagnostic refusal cannot replace the original return/exception or
        # make the diagnostic action successful. The final exit retains it.
        _refusals.append(type(error).__qualname__ + ': ' + str(error))
        try:
            sys.stderr.write('WORLDLINE_DIAGNOSTIC_REFUSED ' + _refusals[-1] + '\n')
            sys.stderr.flush()
        except Exception:
            # The first write failure is already latched; a second failure on
            # that same stream must not replace the original runtime outcome.
            pass


def _exception(error):
    return {'type': type(error).__module__ + '.' + type(error).__qualname__,
            'message': str(error), 'code': getattr(error, 'code', None),
            'notes': list(getattr(error, '__notes__', ())),
            # Private evaluator failures carry the daemon's retained kernel
            # observations here. Copy them through the existing owned-value
            # encoder before the temporary fixture is reclaimed.
            'details': getattr(error, 'details', None)}


def main():
    from worldline import evaluation_context
    from worldline.core import Core
    from worldline.finalization_writer import EngineFinalizationWriter
    from worldline.linux.private_evaluator import PrivateEvaluator

    original_private = PrivateEvaluator.run
    original_seal = EngineFinalizationWriter.seal
    original_attach = evaluation_context.attach
    original_decide = Core.collapse_decide_with_evaluation

    @wraps(original_private)
    def private(self, *args, **kwargs):
        spec = args[0] if args else kwargs['spec']
        try:
            result = original_private(self, *args, **kwargs)
        except BaseException as error:
            _record('private-refusal', {'spec': spec, 'exception': _exception(error)})
            raise
        _record('private-return', {'spec': spec, 'result': result})
        return result

    @wraps(original_seal)
    def seal(self, world, *args, **kwargs):
        try:
            result = original_seal(self, world, *args, **kwargs)
        except BaseException as error:
            _record('seal-refusal', {'exception': _exception(error),
                                   'start': self.start, 'capture': self.capture})
            raise
        _record('seal-return', {'result': result, 'start': self.start,
                               'capture': self.capture, 'checks': self.rows,
                               'world_state': world.state.value})
        return result

    @wraps(original_attach)
    def attach(core, prepared, **kwargs):
        _record('attach-input', {'arguments': kwargs,
                                'prepared': prepared,
                                'raw_request': prepared.request,
                                'raw_capture': prepared.capture,
                                'raw_arena': prepared.owned[0],
                                'raw_rows': prepared.owned[2],
                                'raw_required': prepared.owned[5]})
        result = original_attach(core, prepared, **kwargs)
        # The actual native mixed call consumes the finalization request and
        # the newly constructed context/metadata descriptors. Their pointer
        # fields are addresses only; the dataclass also retains every owned
        # arena and array, which _owned copies without pointer dereferencing.
        _record('attach-return', {'prepared': prepared})
        return result

    @wraps(original_decide)
    def decide(self, request, **kwargs):
        # Retain the actual selected kinds and separate agent argument at the
        # decision boundary, after attach has populated its owned descriptors.
        _record('collapse-input', {'request': request, 'arguments': kwargs})
        # This control observes the existing call. It neither repeats an
        # authority decision nor writes any authority input or owned arena.
        native_control = None
        native_active = False
        try:
            native_control = self._lib.wl_native_diagnostic_control_v1
            native_control.argtypes = [ctypes.c_uint32]
            native_control.restype = ctypes.c_uint32
            status = int(native_control(1))
            native_active = status == 0
            _record('native-trace-start', {'status': status})
            if not native_active:
                _refusals.append('native diagnostic activation refused: ' + str(status))
        except Exception as error:
            _refusals.append('native diagnostic activation failed: ' +
                             type(error).__qualname__ + ': ' + str(error))
        try:
            result = original_decide(self, request, **kwargs)
        except BaseException as error:
            _record('collapse-refusal', {'request': request,
                                        'exception': _exception(error)})
            raise
        finally:
            if native_active:
                try:
                    status = int(native_control(0))
                    _record('native-trace-stop', {'status': status})
                    if status != 0:
                        _refusals.append('native diagnostic retention failed: ' + str(status))
                except Exception as error:
                    _refusals.append('native diagnostic stop failed: ' +
                                     type(error).__qualname__ + ': ' + str(error))
        _record('collapse-return', {'request': request, 'answer': result})
        return result

    with patch.object(PrivateEvaluator, 'run', private), \
         patch.object(EngineFinalizationWriter, 'seal', seal), \
         patch.object(evaluation_context, 'attach', attach), \
         patch.object(Core, 'collapse_decide_with_evaluation', decide):
        # The caller supplies the original explicit module roster and flags.
        # unittest remains responsible for test discovery, failures and output.
        program = unittest.main(module=None, argv=sys.argv, exit=False)
    _record('diagnostic-terminal', {'observer_refusals': list(_refusals),
                                    'successful_tests': program.result.wasSuccessful()})
    raise SystemExit(0 if program.result.wasSuccessful() and not _refusals else 1)


if __name__ == '__main__':
    main()
