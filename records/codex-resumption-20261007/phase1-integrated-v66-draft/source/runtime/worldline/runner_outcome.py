"""Capture original provider values and execute native-requested protocols only."""
from __future__ import annotations

import ctypes
import json

from .finalization_journal import encode
from .errors import CoreUnavailable


def _reference(value):
    return {'profile': 'python-actual-protocol-v1', 'reference': str(id(value)),
            'typeReference': str(id(type(value)))}


def _operand(value):
    kind = type(value)
    if (kind is type(None) or kind is bool or kind is int or kind is float
            or kind is str or kind is bytes):
        return {'profile': 'builtin-v1', 'value': value}
    return _reference(value)


def _builtin_archive(value):
    """Retain codec storage, including subclasses, without foreign dispatch.

    Actual object/type identities and operator traces remain separate facts.
    This storage lens does not claim that subclass get/bool/eq is builtin.
    """
    from .evaluation_terminal import value_bytes

    def lift(item):
        kind = type(item)
        if kind is bytes:
            import base64
            return ['bytes', base64.b64encode(item).decode('ascii')]
        if kind in (type(None), bool, int, float):
            return ['scalar', item]
        if issubclass(kind, str):
            return ['scalar', str.__str__(item)]
        if issubclass(kind, dict):
            pairs = []
            for key, child in dict.items(item):
                if not issubclass(type(key), str):
                    raise TypeError('source codec key is not textual')
                pairs.append([str.__str__(key), lift(child)])
            return ['object', pairs]
        if issubclass(kind, list):
            return ['list', [lift(child) for child in list.__iter__(item)]]
        if issubclass(kind, tuple):
            return ['tuple', [lift(child) for child in tuple.__iter__(item)]]
        raise TypeError('source codec storage is unavailable')

    try:
        return value_bytes(lift(value))
    except TypeError:
        return None


def _decide(core, capture):
    try:
        call = core._lib.wl_runner_outcome_decide_v1
    except AttributeError as exc:
        raise CoreUnavailable('native original runner terminal ABI unavailable') from exc
    raw = encode(capture)
    owner = ctypes.create_string_buffer(raw)
    call.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t]
    call.restype = ctypes.c_size_t
    address = ctypes.cast(owner, ctypes.c_void_p)
    # The result contains only fixed fields and enumerated stage names. This
    # output-only bound does not constrain the complete borrowed input.
    output = ctypes.create_string_buffer(1024)
    actual = int(call(address, len(raw), ctypes.cast(output, ctypes.c_void_p), len(output)))
    if not 0 < actual <= len(output):
        raise CoreUnavailable('native original runner terminal refused capture')
    try:
        return json.loads(output.raw[:actual].decode('utf-8', 'strict'))
    except (UnicodeError, ValueError) as exc:
        raise CoreUnavailable('native runner terminal output is malformed') from exc


def terminal_outcome(core, *, cancelled, timed_out, exit_code, supervision, resources,
                     stop_membership=None, prepare_agent_prefix=None, prepare_agent_result=None,
                     source_observer=None, protocol_observer=None):
    if (prepare_agent_prefix is None) != (prepare_agent_result is None):
        raise CoreUnavailable('native runner result owner requires both original materialization phases')
    observed = resources.get('observed') if isinstance(resources.get('observed'), dict) else {}
    manager_result = supervision.get('result') if isinstance(supervision, dict) else None
    kind_source = _reference(supervision)
    kind_source.update(lookup='getitem', key='kind')
    capture = {'schema': 'worldline.runner-terminal-v2',
        'mode': 'policy-only-v1' if prepare_agent_result is None else 'runner-owner-v1',
        'cancelled': cancelled, 'timedOut': timed_out, 'stopMembership': stop_membership,
        'resourceObservation': _reference(observed), 'managerResult': _operand(manager_result),
        'resourceContainer': _reference(resources),
        'supervisionKind': kind_source, 'exitCode': _operand(exit_code)}
    if source_observer is not None:
        source_observer({
            'resourceReference': str(id(resources)),
            'resourceTypeReference': str(id(type(resources))),
            'resourceObservationReference': str(id(observed)),
            'resourceObservationTypeReference': str(id(type(observed))),
            'supervisionReference': str(id(supervision)),
            'supervisionTypeReference': str(id(type(supervision))),
            'launcherExitReference': str(id(exit_code)),
            'launcherExitTypeReference': str(id(type(exit_code))),
            'managerResultReference': str(id(manager_result)),
            'managerResultTypeReference': str(id(type(manager_result))),
            'dictionaryTypeReference': str(id(dict)),
            'booleanTypeReference': str(id(bool)),
            'integerTypeReference': str(id(int)),
            'stringTypeReference': str(id(str)),
            'floatTypeReference': str(id(float)),
            'bytesTypeReference': str(id(bytes)),
            'listTypeReference': str(id(list)),
            'tupleTypeReference': str(id(tuple)),
            'noneTypeReference': str(id(type(None))),
            'trueReference': str(id(True)), 'falseReference': str(id(False)),
            'noneReference': str(id(None)),
            'supervisionArchive': _builtin_archive(supervision),
            'resourceObservationArchive': _builtin_archive(observed),
            'resourceContainerArchive': _builtin_archive(resources),
            'resourceContainerValue': resources,
            'managerResultArchive': _builtin_archive(manager_result),
            'supervisionValue': supervision})
    protocols = {
        'ceilingHitLookup1': (observed, 'get_truth', 'hitMemoryCeiling', None),
        'ceilingOomLookup1': (observed, 'get_truth', 'oomKilled', None),
        'managerOomComparison1': (manager_result, 'eq', None, 'oom-kill'),
        'observedStateComparison': (observed, 'get_ne', 'state', 'OBSERVED'),
        'ceilingHitLookup2': (observed, 'get_truth', 'hitMemoryCeiling', None),
        'managerOomComparison2': (manager_result, 'eq', None, 'oom-kill'),
        'ceilingEvidenceNoneLookup': (resources, 'getitem_is_none', 'ceilingFired', None),
        'launchComparison': (supervision, 'eq', 'kind', 'LAUNCH_FAILED'),
        'supervisedComparison': (supervision, 'ne', 'kind', 'SUPERVISED'),
        'exitComparison': (exit_code, 'eq', None, 0),
        'ceilingReasonLookup': (resources, 'get_truth', 'ceilingFired', None),
        'indeterminateComparison': (supervision, 'eq', 'kind', 'INDETERMINATE'),
    }
    kind_stages = ('launchComparison', 'supervisedComparison', 'indeterminateComparison')
    publications = {'publishCeilingFired': 'ceilingFired',
                    'publishCeilingEvidence': 'ceilingEvidence'}
    while True:
        value = _decide(core, capture)
        if value.get('status') == 'COMPLETE':
            value['capture'] = capture
            return value
        if value.get('status') != 'CAPTURE_REQUIRED':
            raise CoreUnavailable('native original runner terminal policy refused capture')
        stage = value.get('operation')
        if (stage not in protocols and stage not in publications
                and stage not in ('prepareAgentPrefix', 'prepareAgentResult')) or stage in capture:
            raise CoreUnavailable('native runner requested an invalid/repeated provider operation')
        if stage == 'prepareAgentPrefix':
            if prepare_agent_prefix is None:
                raise CoreUnavailable('native runner requested an unowned prefix materialization')
            prefix = prepare_agent_prefix()
            capture[stage] = {'profile': 'python-actual-protocol-v1',
                'operation': 'prefix-materialization', 'reference': str(id(prefix)),
                'typeReference': str(id(type(prefix)))}
            continue
        if stage == 'prepareAgentResult':
            if prepare_agent_result is None:
                raise CoreUnavailable('native runner requested an unowned result materialization')
            materialized = prepare_agent_result(value['agentStatus'])
            capture[stage] = {'profile': 'python-actual-protocol-v1',
                'operation': 'result-materialization', 'reference': str(id(materialized)),
                'typeReference': str(id(type(materialized))), 'nativeStatus': value['agentStatus']}
            continue
        if stage in publications:
            key = publications[stage]
            assigned = value['value']
            resources[key] = assigned
            capture[stage] = {'profile': 'python-actual-protocol-v1', 'operation': 'setitem',
                             'key': key, 'leftReference': str(id(resources)),
                             'leftTypeReference': str(id(type(resources))), 'operand': assigned}
            continue
        left, operation, key, right = protocols[stage]
        protocol = {'profile': 'python-actual-protocol-v1', 'operation': operation}
        source = None if protocol_observer is None else {
            'stage': stage, 'sourceReference': str(id(left)),
            'sourceTypeReference': str(id(type(left))),
            'sourceBeforeArchive': _builtin_archive(left)}
        if source is not None and type(left) is dict and key is not None:
            stored = None
            key_types = []
            for storage_key, storage_value in dict.items(left):
                key_types.append(str(id(type(storage_key))))
                if type(storage_key) is str and str.__eq__(storage_key, key):
                    stored = storage_value
            source.update(storageKeyTypeReferences=key_types,
                          keyStorageReference=str(id(stored)),
                          keyStorageTypeReference=str(id(type(stored))),
                          keyStorageArchive=_builtin_archive(stored))
        if stage in kind_stages:
            protocol.update(sourceReference=str(id(left)), sourceOperation='getitem',
                            sourceKey='kind', sourceTypeReference=str(id(type(left))))
            left = left['kind']
        protocol.update(leftReference=str(id(left)), leftTypeReference=str(id(type(left))))
        if source is not None:
            source.update(leftReference=str(id(left)),
                          leftTypeReference=str(id(type(left))),
                          leftBeforeArchive=_builtin_archive(left))
        if operation == 'get_truth':
            returned = left.get(key)
            if source is not None:
                source.update(lookupReference=str(id(returned)),
                              lookupTypeReference=str(id(type(returned))),
                              lookupArchive=_builtin_archive(returned))
            protocol['key'] = key
        elif operation == 'getitem_is_none':
            returned = left[key]
            if source is not None:
                source.update(lookupReference=str(id(returned)),
                              lookupTypeReference=str(id(type(returned))),
                              lookupArchive=_builtin_archive(returned))
            protocol.update(key=key, lookupValue=_operand(returned),
                            returnedReference=str(id(returned)),
                            returnedTypeReference=str(id(type(returned))))
            capture[stage] = protocol
            if source is not None:
                protocol_observer(source)
            continue
        elif operation == 'get_ne':
            looked_up = left.get(key)
            if source is not None:
                source.update(lookupReference=str(id(looked_up)),
                              lookupTypeReference=str(id(type(looked_up))),
                              lookupArchive=_builtin_archive(looked_up))
            protocol.update(key=key, lookupValue=_operand(looked_up), operand=right)
            returned = looked_up != right
        else:
            protocol['operand'] = right
            returned = left != right if operation == 'ne' else left == right
        if source is not None:
            source.update(returnedReference=str(id(returned)),
                          returnedTypeReference=str(id(type(returned))),
                          returnedArchive=_builtin_archive(returned))
        protocol.update(returnedReference=str(id(returned)),
                        returnedTypeReference=str(id(type(returned))),
                        returnedTruth=bool(returned))
        capture[stage] = protocol
        if source is not None:
            protocol_observer(source)
