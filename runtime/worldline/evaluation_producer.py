"""Lossless acquisition encoding for the native evaluation producer.

This module acquires/parser-encodes operands. It never decides report integrity,
completion, supervision, audit cleanliness, confinement or admission.
"""
from __future__ import annotations
import base64
import ctypes
import dataclasses
import copy
import hashlib
import json
import io
from pathlib import Path
import uuid
import struct
import threading
from collections.abc import Mapping
from .errors import CoreUnavailable
from .raw_observation import optional_bytes, exception_observation


def capture(value):
    if type(value) is bytes:
        return optional_bytes(value)
    if value is None or type(value) in (str, bool, int, float):
        return value
    if isinstance(value, Mapping):
        if any(type(key) is not str for key in value):
            raise CoreUnavailable('raw evaluation contains a non-string object key')
        return {key: capture(item) for key, item in value.items()}
    if type(value) in (list, tuple):
        return [capture(item) for item in value]
    if dataclasses.is_dataclass(value):
        return {field.name: capture(getattr(value, field.name))
                for field in dataclasses.fields(value)}
    raise CoreUnavailable('raw evaluation has unsupported operand type: ' + type(value).__qualname__)


from . import evaluation_policy as _producer_json_policy


_PRODUCER_JSON_CAPTURE = capture
_PRODUCER_JSON_OPTIONAL_BYTES = optional_bytes
_PRODUCER_JSON_RAW_JSON = _producer_json_policy.raw_json
_PRODUCER_JSON_INTEGER = _producer_json_policy._integer
_PRODUCER_JSON_DUMPS = json.dumps
_PRODUCER_JSON_JSON_ENCODER = json.JSONEncoder
_PRODUCER_JSON_DEFAULT_ENCODER = json._default_encoder
_PRODUCER_JSON_ENCODER_MODULE = json.encoder
_PRODUCER_JSON_DEFAULT_STATE = tuple(vars(_PRODUCER_JSON_DEFAULT_ENCODER).items())
_PRODUCER_JSON_ENCODER_METHODS = tuple((name, getattr(_PRODUCER_JSON_JSON_ENCODER, name)) for name in
                         ('__init__', 'encode', 'iterencode', 'default'))
_PRODUCER_JSON_ENCODER_GLOBALS = tuple((name, getattr(json.encoder, name)) for name in
                         ('JSONEncoder', 'encode_basestring_ascii', 'encode_basestring',
                          'c_make_encoder', '_make_iterencode', 'INFINITY'))
_PRODUCER_JSON_ENCODER_CLASS_STATE = tuple(vars(_PRODUCER_JSON_JSON_ENCODER).items())
_PRODUCER_JSON_FUNCTION_STATES = tuple((function, function.__code__, function.__defaults__,
                          None if function.__kwdefaults__ is None else
                          tuple(function.__kwdefaults__.items()))
                         for function in (_PRODUCER_JSON_DUMPS, _PRODUCER_JSON_RAW_JSON, _PRODUCER_JSON_INTEGER, _PRODUCER_JSON_CAPTURE,
                                          *(function for _, function in _PRODUCER_JSON_ENCODER_METHODS),
                                          json.encoder._make_iterencode))


def _producer_json_same_state(current, expected):
    # Check string keys before lookups, avoiding foreign key equality hooks.
    if type(current) is not dict or len(current) != len(expected):
        return False
    if any(type(key) is not str for key in current):
        return False
    return all(key in current and current[key] is value for key, value in expected)


def _producer_json_pristine():
    # A bounded snapshot of the actual scalar/key formatter call graph. A
    # changed hook/configuration declines BEFORE speculative formatter calls.
    # This does not establish equivalence under concurrent mutation after it.
    if getattr(json, '_default_encoder', None) is not _PRODUCER_JSON_DEFAULT_ENCODER or json.encoder is not _PRODUCER_JSON_ENCODER_MODULE:
        return False
    if tuple(vars(_PRODUCER_JSON_JSON_ENCODER)) != tuple(key for key, _ in _PRODUCER_JSON_ENCODER_CLASS_STATE):
        return False
    if not all(vars(_PRODUCER_JSON_JSON_ENCODER)[key] is value for key, value in _PRODUCER_JSON_ENCODER_CLASS_STATE):
        return False
    if not _producer_json_same_state(vars(_PRODUCER_JSON_DEFAULT_ENCODER), _PRODUCER_JSON_DEFAULT_STATE):
        return False
    if not all(getattr(json.encoder, key, None) is value for key, value in _PRODUCER_JSON_ENCODER_GLOBALS):
        return False
    for function, code, defaults, kwdefaults in _PRODUCER_JSON_FUNCTION_STATES:
        if function.__code__ is not code or function.__defaults__ is not defaults:
            return False
        current = function.__kwdefaults__
        if kwdefaults is None:
            if current is not None:
                return False
        elif not _producer_json_same_state(current, kwdefaults):
            return False
    return True


def encode(value):
    # Match original encode's import-before-capture binding, including hooks
    # that replace the policy module attribute during capture itself.
    from .evaluation_policy import raw_json
    captured = shadow = output = pending = item = iterator = child = key = None
    try:
        # Keep the exact original capture once. It already owns plain containers,
        # invokes foreign Mapping/dataclass hooks once, and retains full leaves.
        captured = capture(value)

        class Decline(Exception):
            pass

        def deepest(item):
            best = child = shape = key = None
            try:
                kind = type(item)
                if item is None or kind in (str, bool, int, float):
                    # None exercises json.dumps' scalar frame path. If conservative
                    # preflight refuses a near-limit original integer tree, fallback
                    # still invokes the original codec on the exact captured operand.
                    return None, 0
                if kind not in (dict, list):
                    raise Decline
                best = None
                best_depth = -1
                if kind is dict:
                    for key, child in item.items():
                        if type(key) is not str:
                            raise Decline
                        shape, depth = deepest(child)
                        if depth > best_depth:
                            best, best_depth = (key, shape), depth
                    return ({} if best is None else {best[0]: best[1]}), best_depth + 1
                for child in item:
                    shape, depth = deepest(child)
                    if depth > best_depth:
                        best, best_depth = shape, depth
                return ([] if best_depth < 0 else [best]), best_depth + 1

            finally:
                item = best = child = shape = key = None

        try:
            pristine = (raw_json is _PRODUCER_JSON_RAW_JSON
                        and capture is _PRODUCER_JSON_CAPTURE
                        and optional_bytes is _PRODUCER_JSON_OPTIONAL_BYTES
                        and _producer_json_policy.raw_json is _PRODUCER_JSON_RAW_JSON
                        and _producer_json_policy._integer is _PRODUCER_JSON_INTEGER
                        and json.dumps is _PRODUCER_JSON_DUMPS
                        and json.JSONEncoder is _PRODUCER_JSON_JSON_ENCODER
                        and _producer_json_pristine())
        except Exception:
            pristine = False
        shadow = output = pending = None
        if pristine:
            try:
                shadow, _depth = deepest(captured)
                # The original recursive formatter remains the depth/refusal gate
                # at the encoder function's original caller depth.
                raw_json(shadow)
                shadow = None
                output = io.BytesIO()
                pending = [('value', captured)]
                while pending:
                    action, item = pending.pop()
                    if action == 'array-items':
                        iterator, separated = item
                        try:
                            child = next(iterator)
                        except StopIteration:
                            output.write(b']')
                        else:
                            if separated:
                                output.write(b',')
                            pending.append(('array-items', (iterator, True)))
                            pending.append(('value', child))
                        continue
                    if action == 'object-items':
                        iterator, separated = item
                        try:
                            key, child = next(iterator)
                        except StopIteration:
                            output.write(b'}')
                        else:
                            if separated:
                                output.write(b',')
                            output.write(json.dumps(key, ensure_ascii=True).encode('ascii'))
                            output.write(b':')
                            pending.append(('object-items', (iterator, True)))
                            pending.append(('value', child))
                        continue
                    kind = type(item)
                    if kind is int:
                        output.write(_producer_json_policy._integer(item).encode('ascii'))
                    elif item is None or kind in (bool, float, str):
                        output.write(json.dumps(item, ensure_ascii=True, allow_nan=True,
                                                separators=(',', ':')).encode('ascii'))
                    elif kind is list:
                        output.write(b'[')
                        pending.append(('array-items', (iter(item), False)))
                    elif kind is dict:
                        output.write(b'{')
                        pending.append(('object-items', (iter(item.items()), False)))
                    else:
                        raise Decline
                return output.getvalue()
            except Exception:
                pass
            finally:
                shadow = output = pending = item = iterator = child = key = None

        # Reuse the once-captured operand, including after a declined preflight.
        # Calling capture again would change foreign hooks and mutation timing.
        return raw_json(captured).encode('ascii')
    finally:
        # Do not retain additional owned capture/traversal/output references in
        # this encoder's traceback frame on refusals or BaseException.
        captured = shadow = output = pending = item = iterator = child = key = None


def _json_operand(payload):
    from .report_parser import _integer_value
    return json.loads(payload, parse_int=_integer_value)


def warm_syntax_acquisition_sources():
    """Load the fixed host acquisition closure before source-lease evidence.

    No parser run, selection read, reservation, principal construction or
    admission occurs here. Missing integrated provider modules fail normally;
    the standalone selected helper remains bytes, never a host module import.
    """
    from . import evaluation_policy, examiner_audit, report, report_parser, raw_observation, trusted
    from .linux import (
        examiner_loader, kernel_role_observer, namespace_lifetime, native_lifetime,
        private_evaluator, protected_report_channel, protected_report_provider,
        protected_source_parser,
    )


def _source_declaration(original_bytes, *, work, source_context, observer):
    """Issue fixed-source operands before launching either protected phase.

    The packaged selection is independent of the helper the driver subsequently
    reads. Only native fixed-reference/custody verification gives it authority.
    No caller chooses an interpreter, parser path, helper or provider.
    """
    from .examiner_audit import _runtime
    from .linux.private_evaluator import _read_examiner_source
    from .report import prepare_private_report
    selection_read = {}
    try:
        selected = json.loads(_read_examiner_source(
            Path(__file__).with_name('source_syntax_selection.json'), selection_read))
        helper = base64.b64decode(selected['parserBytes']['payload'], validate=True)
    except BaseException as error:
        if observer is not None:
            try:
                observer('source-syntax-selection-exception', 0,
                    {'read': selection_read, 'exception': exception_observation(error)})
            except BaseException as retention_error:
                error.add_note('source syntax selection error retention also failed: ' +
                               str(retention_error))
        raise
    candidate = hashlib.sha256(original_bytes).hexdigest()
    verifier = hashlib.sha256(helper).hexdigest()
    runtime = _runtime()
    reports_base = work / 'private-reports'
    reports_base.mkdir(mode=0o700)
    starts, reports, bindings = {}, {}, {}
    for phase in ('before', 'after'):
        invocation = str(uuid.uuid4())
        starts[phase] = {'invocationId': invocation,
            'checkId': 'worldline-source-syntax-phase', 'phase': phase,
            'candidateScope': candidate}
        binding = {'runId': invocation, 'checkId': 'worldline-source-syntax-phase',
            'candidateIdentity': candidate, 'verifierIdentity': verifier}
        directory = prepare_private_report(reports_base,
            run_id=invocation, check_id=binding['checkId'],
            candidate_identity=candidate, verifier_identity=verifier)
        bindings[phase] = binding
        reports[phase] = {'directory': directory, 'binding': copy.deepcopy(binding)}
    declaration = {'parserBytes': copy.deepcopy(selected['parserBytes']),
        'driverBytes': copy.deepcopy(selected['driverBytes']), 'runtime': runtime,
        'phaseInvocations': starts,
        'phaseReports': {phase: {'directory': str(reports[phase]['directory']),
                                'binding': copy.deepcopy(bindings[phase])}
                         for phase in ('before', 'after')},
        'selectionRead': selection_read, 'sourceContext': capture(source_context)}
    # This operand is retained independently of the driver/controller output.
    if observer is not None:
        observer('source-syntax-declaration', 0, copy.deepcopy(declaration))
        for occurrence, phase in enumerate(('before', 'after')):
            observer('source-syntax-invocation-start', occurrence,
                {'phase': phase, 'invocation': copy.deepcopy(starts[phase]),
                 'privateReportBinding': copy.deepcopy(bindings[phase])})
    return declaration, reports


def _acquire_source_capsule(original_bytes, *, systemd, gate, work_directory,
                            source_context, acquisition_observer=None):
    from .linux.protected_source_parser import acquire_protected_source_ast
    if type(original_bytes) is not bytes:
        raise CoreUnavailable('source syntax original operand is not exact JSON bytes')
    original = _json_operand(original_bytes.decode('utf-8', 'strict'))
    if not isinstance(original, Mapping):
        raise CoreUnavailable('source syntax original result is not an object')
    # Absence is retained for native original-domain interpretation; malformed
    # present audit data must reach the actual driver rather than disappear.
    audit = original.get('examinerAudit')
    if audit is None:
        return {'result': original_bytes, 'declaration': b'null', 'capsule': b'null'}
    work = Path(work_directory) / ('source-syntax-' + str(uuid.uuid4()))
    work.mkdir(mode=0o700)
    declaration, reports = _source_declaration(original_bytes, work=work,
        source_context=source_context, observer=acquisition_observer)
    retained_count = 0
    retention_lock = threading.RLock()
    def retain_controller(kind, occurrence, observation):
        nonlocal retained_count
        if acquisition_observer is not None:
            with retention_lock:
                retained = retained_count
                retained_count += 1
                # Do not collide with the original check's raw private return
                # or with the other protected phase's occurrence zero.
                acquisition_observer('source-syntax-acquisition', retained,
                    {'kind': kind, 'occurrence': occurrence, 'observation': observation})
    try:
        capsule = acquire_protected_source_ast(systemd,
            historical_audit=audit, parser_declaration=copy.deepcopy(declaration),
            phase_invocations=copy.deepcopy(declaration['phaseInvocations']),
            phase_reports=reports, work_directory=work / 'controller',
            resource_properties=gate.unit_properties(),
            admission_guards={phase: gate.guard('source-syntax:' + phase)
                              for phase in ('before', 'after')},
            acquisition_observer=retain_controller)
    except BaseException as error:
        partial = getattr(error, 'protected_source_syntax_capture', None)
        if acquisition_observer is not None:
            try:
                acquisition_observer('source-syntax-acquisition-exception', 0,
                    {'exception': exception_observation(error), 'capture': partial,
                     'declaration': declaration, 'originalResult': original_bytes})
            except BaseException as retention_error:
                error.add_note('source syntax exception retention also failed: ' +
                               str(retention_error))
        raise
    return {'result': original_bytes, 'declaration': encode(declaration),
            'capsule': encode(capsule)}


def acquire_syntax_capsules(original_results, *, systemd, gate, work_directory,
                            source_context):
    """Read-only adjunct for ALL native-extracted original owner result bytes.

    Recovery's native Syntax_Inputs performs the complete operation/archive,
    terminal, finalization and SpecialAdopt traversal. This function never
    selects accepted/PASS results, rewrites history or uses today's grants.
    Its result is archived as owner_context.native_replay_capsules_raw.
    """
    answer = []
    for original_bytes in original_results:
        try:
            answer.append(_acquire_source_capsule(original_bytes, systemd=systemd,
                gate=gate, work_directory=work_directory, source_context=source_context))
        except BaseException as error:
            error.source_syntax_completed_capsules = answer
            raise
    return answer


def _capsule_ast(capsule):
    """Transport the actual sealed primitive profile, never an audit decision."""
    profiles = {}
    for phase in ('before', 'after'):
        artifact = capsule['phases'][phase]['artifact']
        payload = base64.b64decode(artifact['payload'], validate=True)
        profiles[phase] = _json_operand(payload.decode('utf-8', 'strict'))['profile']
    return {'runtime': profiles['before']['runtime'],
            'before': profiles['before']['files'], 'after': profiles['after']['files']}


def _float_observations(value, path=()):
    """Retain original IEEE bits, including nonfinite payload and sign."""
    if type(value) is float:
        yield {'path': list(path), 'bits': optional_bytes(struct.pack('>d', value))}
    elif isinstance(value, Mapping):
        for key, item in value.items():
            yield from _float_observations(item, path + (key,))
    elif type(value) in (list, tuple):
        for index, item in enumerate(value):
            yield from _float_observations(item, path + (index,))
    elif dataclasses.is_dataclass(value):
        for field in dataclasses.fields(value):
            yield from _float_observations(getattr(value, field.name), path + (field.name,))


def _lifetime_capture(result):
    """Flatten actual retained binary records, without interpreting events."""
    boundary = result.get('evaluatorBoundary')
    observations = boundary.get('daemonRoleObservations') if isinstance(boundary, Mapping) else None
    if type(observations) is not list:
        return None
    pieces, records, offset = [], [], 0
    try:
        for observation in observations:
            if not isinstance(observation, Mapping) or observation.get('kind') not in (
                    'native-lifetime-receive', 'native-lifetime-terminal'):
                continue
            transfers = observation.get('transferObjects')
            leaf = transfers[0].get('bytes') if type(transfers) is list and transfers else None
            if not isinstance(leaf, Mapping) or leaf.get('encoding') != 'base64':
                raise ValueError('native lifetime record byte acquisition is absent')
            payload = base64.b64decode(leaf.get('payload'), validate=True)
            records.append({'recordId': observation.get('recordId'),
                            'offset': offset, 'sizeBytes': len(payload)})
            pieces.append(payload)
            offset += len(payload)
    except (TypeError, ValueError, KeyError) as failure:
        return {'bytes': None, 'records': records, 'exception': exception_observation(failure)}
    return {'bytes': optional_bytes(b''.join(pieces)), 'records': records, 'exception': None}


def acquire(result, *, systemd, gate, work_directory, source_context=None,
            acquisition_observer=None):
    """Acquire current syntax BEFORE the immutable invocation-result callback.

    Original JSON is retained separately from the four ephemeral syntax fields.
    Native verification hashes those exact bytes and joins the full controller,
    declared starts, report bindings, runtime and original source inventory.
    """
    if not isinstance(result, Mapping):
        raise CoreUnavailable('raw evaluation result is not an object')
    owned = dict(result)
    owned['nativeFloatObservations'] = list(_float_observations(result))
    owned['nativeLifetimeCapture'] = _lifetime_capture(result)
    if owned.get('examinerAudit') is not None:
        original_bytes = encode(owned)
        if acquisition_observer is not None:
            acquisition_observer('source-syntax-original-result', 0,
                {'originalResult': original_bytes, 'checkReturnObserved': True})
        triple = _acquire_source_capsule(original_bytes, systemd=systemd, gate=gate,
            work_directory=work_directory, source_context=source_context,
            acquisition_observer=acquisition_observer)
        declaration = _json_operand(triple['declaration'])
        capsule = _json_operand(triple['capsule'])
        owned['sourceParserOriginalResult'] = original_bytes.decode('utf-8', 'strict')
        owned['sourceParserDeclaration'] = declaration
        owned['sourceParserCapture'] = capsule
        owned['nativeSourceAST'] = _capsule_ast(capsule)
    return owned


def operands(result, declared):
    from .finalization_journal import payload_acquisitions
    if not isinstance(result, Mapping):
        raise CoreUnavailable('raw evaluation result is not an object')
    expected = result.get('engineInvocationObservation')
    acquired = payload_acquisitions(result.get('engineRawObservations'))
    returned = dict(result)
    from .finalization_journal import encode as encode_finalization
    terminal = b''
    for item in (() if acquired is None else acquired):
        if isinstance(item, Mapping) and item.get('kind') == 'manager-return':
            observation = item.get('observation')
            if isinstance(observation, Mapping):
                retained = observation.get('terminalBytes')
                if type(retained) is bytes:
                    terminal = retained
                elif 'terminalCapture' in observation:
                    terminal = encode_finalization(observation['terminalCapture'])
    return tuple(encode(value) for value in (expected, acquired, returned, declared)) + (terminal,)


def derive(core, result, declared):
    from .evaluation_wire import OwnedRecord, Raw
    values = operands(result, declared)
    owners = tuple(ctypes.create_string_buffer(value) for value in values)
    raw = Raw()
    confinement = ctypes.c_uint8()
    try:
        call = core._lib.wl_evaluation_producer_derive_v1
    except AttributeError as failure:
        raise CoreUnavailable('native raw evaluation producer ABI unavailable') from failure
    call.argtypes = [ctypes.c_void_p, ctypes.c_size_t] * 5 + [ctypes.c_void_p, ctypes.c_void_p]
    call.restype = ctypes.c_uint8
    arguments = []
    for owner, value in zip(owners, values):
        arguments.extend((ctypes.cast(owner, ctypes.c_void_p), len(value)))
    status = int(call(*arguments, ctypes.byref(raw), ctypes.byref(confinement)))
    if status != 0:
        raise CoreUnavailable('native raw evaluation producer refused transport: ' + str(status))
    return OwnedRecord(bytes(raw), int(confinement.value))
