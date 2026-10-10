"""Original-producer-bound replay vectors. Source only; no acceptance claimed.

The parent supplies actual observations/material from the original complete
kernel fixture roster and serializes these two unchanged archive byte streams
into the pure Ada control driver. This module never redecides, supplies a native
permission Boolean, substitutes a core, or constructs an invented positive DTO.
"""
from __future__ import annotations
import ctypes as C
from dataclasses import dataclass, replace
from worldline.root_worker_codec import archive, raw_archive
from worldline import resource_child_execution as J
from worldline import resource_scoped_run_ledger as S
from worldline import resource_run_ledger as L
from worldline import resource_actor_admission as D
from worldline import operation_authority_kernel as A
from worldline.operation_capture import archive as original_archive
from worldline import canonical_owner_completion_kernel as H
from worldline import canonical_exchange_kernel as X

@dataclass(frozen=True, slots=True)
class ReplayVector:
    name: str
    observation: bytes
    material: bytes
    expectation: str  # MATCH, DECODE_REFUSED, OUTPUT_CONFLICT, NOT_JOINTLY_MATCHED


def _vector(name, observation, material, expectation):
    return ReplayVector(name, archive(observation), archive(material), expectation)


def _set(raw, kind, path, value):
    item = kind.from_buffer_copy(raw)
    selected = item
    names = path.split('.')
    for name in names[:-1]:
        selected = getattr(selected, name)
    setattr(selected, names[-1], value)
    return bytes(item)


def _padding(raw, kind):
    occupied = set()
    for name, field_type in kind._fields_:
        first = getattr(kind, name).offset
        occupied.update(range(first, first + C.sizeof(field_type)))
    for position in range(C.sizeof(kind)):
        if position not in occupied:
            changed = bytearray(raw)
            changed[position] ^= 255
            return bytes(changed)
    raise ValueError('selected original C record has no padding control location')


def _bad_count(rosters, index=0):
    name, raw, count = rosters[index]
    return rosters[:index] + ((name, raw, count + 1),) + rosters[index + 1:]


def root_vectors(material, observation):
    if type(observation) is not J.ResourceChildNativeObservation:
        raise TypeError('actual complete original child observation required')
    # Genuine positives may be root, child, task or any detailed native refusal.
    # The Ada driver compares the actual original expected status separately.
    yield _vector('faithful-complete-original', observation, material, 'MATCH')
    yield _vector('copied-status', replace(observation,
        raw_output=_set(observation.raw_output, L.RawResult, 'status',
                        (L.RawResult.from_buffer_copy(observation.raw_output).status + 1) % len(J.STATUSES))),
        material, 'OUTPUT_CONFLICT')
    yield _vector('one-side-resource-schema', replace(observation,
        actor_input=_set(observation.actor_input, D.RawActorPacket, 'ledger.schema_version', 0)),
        material, 'DECODE_REFUSED')
    yield _vector('one-side-authority-schema', replace(observation,
        authority_input=_set(observation.authority_input, A.Input, 'schema', 0)),
        material, 'DECODE_REFUSED')
    yield _vector('enum-out-of-domain', replace(observation,
        child_input=_set(observation.child_input, J.RawChildInput, 'mode', 255)),
        material, 'DECODE_REFUSED')
    yield _vector('boolean-out-of-domain', replace(observation,
        child_input=_set(observation.child_input, J.RawChildInput, 'controller.bound.operation.present', 2)),
        material, 'DECODE_REFUSED')
    yield _vector('negative-span', replace(observation,
        child_input=_set(observation.child_input, J.RawChildInput, 'controller.raw_request.first', -1)),
        material, 'DECODE_REFUSED')
    yield _vector('truncated-layout', replace(observation, child_input=observation.child_input[:-1]),
        material, 'DECODE_REFUSED')
    yield _vector('overlong-layout', replace(observation, child_input=observation.child_input + b'\0'),
        material, 'DECODE_REFUSED')
    yield _vector('stale-resource-count', replace(observation,
        resource_rosters=_bad_count(observation.resource_rosters)), material, 'DECODE_REFUSED')
    yield _vector('stale-authority-count', replace(observation,
        authority_rosters=_bad_count(observation.authority_rosters)), material, 'DECODE_REFUSED')
    yield _vector('missing-resource-roster', replace(observation,
        resource_rosters=observation.resource_rosters[:-1]), material, 'DECODE_REFUSED')
    yield _vector('conflicting-resource-roster-name', replace(observation,
        resource_rosters=(('not-history', *observation.resource_rosters[0][1:]),) + observation.resource_rosters[1:]),
        material, 'DECODE_REFUSED')
    yield _vector('reordered-resource-roster', replace(observation,
        resource_rosters=(observation.resource_rosters[1], observation.resource_rosters[0]) + observation.resource_rosters[2:]),
        material, 'DECODE_REFUSED')
    yield _vector('nonintegral-array-extent', replace(observation,
        authority_rosters=((observation.authority_rosters[0][0], observation.authority_rosters[0][1] + b'\0',
                            observation.authority_rosters[0][2]),) + observation.authority_rosters[1:]),
        material, 'DECODE_REFUSED')
    # Native ABI padding remains valid and never authority; provenance must
    # still match the actual original zero-initialized producer constructor.
    yield _vector('source-C-padding-conflict', replace(observation,
        child_input=_padding(observation.child_input, J.RawChildInput)), material, 'NOT_JOINTLY_MATCHED')
    yield _vector('transport-conflict', replace(observation, transport_status=-1), material, 'OUTPUT_CONFLICT')
    absent = dict(material)
    del absent['controller']
    yield _vector('missing-authentic-controller', observation, absent, 'NOT_JOINTLY_MATCHED')
    stale = dict(material)
    stale['controller'] = replace(material['controller'], current_source=b'conflicting actual source')
    yield _vector('one-side-stale-source-material', observation, stale, 'NOT_JOINTLY_MATCHED')
    conflicting = dict(material)
    conflicting['controller'] = replace(material['controller'], raw_request=b'conflicting original request')
    yield _vector('one-side-conflicting-request-material', observation, conflicting, 'NOT_JOINTLY_MATCHED')


def scoped_vectors(packet, observation):
    if type(packet) is not S.ScopedPacket or type(observation) is not S.ScopedNativeDecision:
        raise TypeError('actual complete original scoped packet/observation required')
    yield _vector('faithful-complete-original', observation, packet, 'MATCH')
    yield _vector('copied-status', replace(observation,
        raw_output=_set(observation.raw_output, L.RawResult, 'status',
                        L.RawResult.from_buffer_copy(observation.raw_output).status ^ 1)),
        packet, 'OUTPUT_CONFLICT')
    yield _vector('one-side-schema', replace(observation,
        raw_input=_set(observation.raw_input, S.RawScopedPacket, 'schema_version', 0)),
        packet, 'DECODE_REFUSED')
    yield _vector('truncated-layout', replace(observation, raw_input=observation.raw_input[:-1]), packet, 'DECODE_REFUSED')
    yield _vector('missing-roster', replace(observation, raw_rosters=observation.raw_rosters[:-1]), packet, 'DECODE_REFUSED')
    yield _vector('stale-count', replace(observation, raw_rosters=_bad_count(observation.raw_rosters)), packet, 'DECODE_REFUSED')
    yield _vector('padding-not-authority', replace(observation,
        raw_input=_padding(observation.raw_input, S.RawScopedPacket)), packet, 'NOT_JOINTLY_MATCHED')
    yield _vector('copied-ready-label', replace(observation, status='ROOT_READY_CONJUNCTION'), packet, 'OUTPUT_CONFLICT')
    yield _vector('one-side-current-source', observation,
        replace(packet, current=replace(packet.current, cause=b'conflicting cause')), 'NOT_JOINTLY_MATCHED')


def raw_root_vectors(material, observation):
    """Actual x5 original-tag records; never project raw bytes into JSON."""
    if type(observation) is not J.ResourceChildNativeObservation:
        raise TypeError('actual complete original child observation required')
    emit = lambda name, obs, source, expected: ReplayVector(
        name, raw_archive(obs), raw_archive(source), expected)
    yield emit('raw-original-faithful', observation, material, 'MATCH')
    yield emit('raw-original-copied-status', replace(observation,
        raw_output=_set(observation.raw_output, L.RawResult, 'status',
                        (L.RawResult.from_buffer_copy(observation.raw_output).status + 1) % len(J.STATUSES))),
        material, 'OUTPUT_CONFLICT')
    yield emit('raw-original-count-conflict', replace(observation,
        resource_rosters=_bad_count(observation.resource_rosters)), material, 'DECODE_REFUSED')
    yield emit('raw-original-nontuple-rosters', replace(observation,
        resource_rosters=list(observation.resource_rosters)), material, 'DECODE_REFUSED')
    yield emit('raw-original-boolean-count', replace(observation,
        resource_rosters=((observation.resource_rosters[0][0], observation.resource_rosters[0][1], False),)
        + observation.resource_rosters[1:]), material, 'DECODE_REFUSED')
    yield emit('raw-original-truncated-layout', replace(observation,
        child_input=observation.child_input[:-1]), material, 'DECODE_REFUSED')
    yield emit('raw-original-padding-source-conflict', replace(observation,
        child_input=_padding(observation.child_input, J.RawChildInput)), material, 'NOT_JOINTLY_MATCHED')


def raw_scoped_vectors(packet, observation):
    if type(packet) is not S.ScopedPacket or type(observation) is not S.ScopedNativeDecision:
        raise TypeError('actual complete original scoped packet/observation required')
    emit = lambda name, obs, source, expected: ReplayVector(
        name, raw_archive(obs), raw_archive(source), expected)
    yield emit('raw-original-faithful', observation, packet, 'MATCH')
    yield emit('raw-original-copied-status', replace(observation,
        raw_output=_set(observation.raw_output, L.RawResult, 'status',
                        L.RawResult.from_buffer_copy(observation.raw_output).status ^ 1)),
        packet, 'OUTPUT_CONFLICT')
    yield emit('raw-original-count-conflict', replace(observation,
        raw_rosters=_bad_count(observation.raw_rosters)), packet, 'DECODE_REFUSED')
    yield emit('raw-original-nontuple-rosters', replace(observation,
        raw_rosters=list(observation.raw_rosters)), packet, 'DECODE_REFUSED')
    yield emit('raw-original-padding-source-conflict', replace(observation,
        raw_input=_padding(observation.raw_input, S.RawScopedPacket)), packet, 'NOT_JOINTLY_MATCHED')
    yield emit('raw-original-copied-ready-label', replace(observation,
        status='ROOT_READY_CONJUNCTION'), packet, 'OUTPUT_CONFLICT')


def operation_vectors(snapshot, observation):
    if type(observation) is not dict or set(observation) != {'decision','input','arena','rosters','output'}:
        raise TypeError('actual complete original operation observe record required')
    historical = len(observation['rosters']) == 12
    if len(observation['rosters']) not in (4, 12):
        raise ValueError('complete original operation or historical completion roster required')
    kind = H.Input if historical else A.Input
    schema = 'current.schema' if historical else 'schema'
    decisions = H.DECISIONS if historical else A.DECISIONS
    emit = lambda name, obs, material, expected: ReplayVector(name,
        original_archive(obs), original_archive(material), expected)
    yield emit('faithful-complete-original', observation, snapshot, 'MATCH')
    copied = dict(observation)
    output = A.Result.from_buffer_copy(bytes.fromhex(observation['output']))
    output.disposition = (output.disposition + 1) % len(decisions)
    copied['output'] = bytes(output).hex()
    yield emit('copied-status', copied, snapshot, 'OUTPUT_CONFLICT')
    malformed = dict(observation)
    malformed['input'] = _set(bytes.fromhex(observation['input']), kind, schema, 0).hex()
    yield emit('one-side-schema', malformed, snapshot, 'DECODE_REFUSED')
    absent = dict(observation)
    absent['rosters'] = observation['rosters'][:-1]
    yield emit('missing-roster', absent, snapshot, 'DECODE_REFUSED')
    extent = dict(observation)
    extent['rosters'] = [observation['rosters'][0] + '00', *observation['rosters'][1:]]
    yield emit('nonintegral-array-extent', extent, snapshot, 'DECODE_REFUSED')
    padding = dict(observation)
    padding['input'] = _padding(bytes.fromhex(observation['input']), kind).hex()
    yield emit('padding-changed-from-source-constructor', padding, snapshot, 'NOT_JOINTLY_MATCHED')
    extra = dict(observation)
    extra['arena'] += '00'
    yield emit('unbound-arena-tail', extra, snapshot, 'NOT_JOINTLY_MATCHED')
    stale = dict(snapshot)
    stale['binding'] = dict(snapshot['binding'])
    stale['binding']['id'] = dict(snapshot['binding']['id'])
    value = bytearray.fromhex(snapshot['binding']['id']['operation_id'])
    if not value:
        raise ValueError('original operation identity must be present for this control')
    value[0] ^= 1
    stale['binding']['id']['operation_id'] = value.hex()
    yield emit('one-side-original-operation-material', observation, stale, 'NOT_JOINTLY_MATCHED')


def exchange_vectors(arguments, observation):
    if type(arguments) is not tuple or len(arguments) != 12 or len(observation['rosters']) != 8:
        raise TypeError('actual complete original exchange args/observation required')
    emit = lambda name, obs, args, expected: ReplayVector(name,
        original_archive(obs), original_archive(args), expected)
    yield emit('faithful-complete-original-exchange', observation, arguments, 'MATCH')
    copied = dict(observation)
    output = X.Result.from_buffer_copy(bytes.fromhex(observation['output']))
    output.disposition = (output.disposition + 1) % len(X.DECISIONS)
    copied['output'] = bytes(output).hex()
    yield emit('copied-exchange-output', copied, arguments, 'OUTPUT_CONFLICT')
    bad = dict(observation)
    bad['input'] = _set(bytes.fromhex(observation['input']), X.Input,
        'operation_input.authority.schema', 0).hex()
    yield emit('one-side-original-authority-schema', bad, arguments, 'DECODE_REFUSED')
    padding = dict(observation)
    padding['input'] = _padding(bytes.fromhex(observation['input']), X.Input).hex()
    yield emit('exchange-source-padding-conflict', padding, arguments, 'NOT_JOINTLY_MATCHED')
    missing = dict(observation)
    missing['rosters'] = observation['rosters'][:-1]
    yield emit('missing-full-exchange-roster', missing, arguments, 'DECODE_REFUSED')


@dataclass(frozen=True, slots=True)
class ImageVector:
    name: str
    data: bytes
    image: tuple[int, int]
    value: tuple[int, int]
    image_scoped: bool
    value_scoped: bool
    carrier_scoped: bool
    expected: bool  # source equality expectation, never admission input


def _image_vector(name, payload, value, image_scoped, value_scoped, expected,
                  *, carrier_scoped=False):
    carrier = archive(payload) if carrier_scoped else raw_archive(payload)
    encoded = archive(value) if value_scoped else raw_archive(value)
    return ImageVector(name, carrier + encoded, (1, len(carrier)),
                       (len(carrier) + 1, len(encoded)),
                       image_scoped, value_scoped, carrier_scoped, expected)


def image_vectors(original):
    """Full raw domain, including byte-keyed maps and raw-only root DTOs."""
    payload = raw_archive(original)
    for carrier_scoped in (False, True):
        yield _image_vector(f'faithful-raw-image-{carrier_scoped}', payload,
                            original, False, False, True, carrier_scoped=carrier_scoped)
        yield _image_vector(f'truncated-raw-image-{carrier_scoped}', payload[:-1],
                            original, False, False, False, carrier_scoped=carrier_scoped)
        yield _image_vector(f'overlong-raw-image-{carrier_scoped}', payload + b'\0',
                            original, False, False, False, carrier_scoped=carrier_scoped)
    # Exact source relation must not substitute original Python numeric ==.
    yield _image_vector('bool-not-int', raw_archive(False), 0, False, False, False)
    yield _image_vector('signed-zero-bits', raw_archive(-0.0), 0.0, False, False, False)
    yield _image_vector('tuple-not-list', raw_archive((original,)), [original],
                        False, False, False)
    if type(original) is dict:
        yield _image_vector('source-dict-order-independent', payload,
                            dict(reversed(tuple(original.items()))), False, False, True)
    # An OA literal dictionary resembling an SA bytes wrapper is NOT a carrier.
    literal = raw_archive({'type': 'bytes', 'value': raw_archive(True).hex()})
    value = raw_archive(True)
    yield ImageVector('literal-dict-not-byte-carrier', literal + value,
                      (1, len(literal)), (len(literal) + 1, len(value)),
                      False, False, False, False)
    carrier = archive(payload)
    yield ImageVector('scoped-carrier-wrong-flag', carrier + payload,
                      (1, len(carrier)), (len(carrier) + 1, len(payload)),
                      False, False, False, False)
    carrier = raw_archive(payload)
    yield ImageVector('raw-carrier-wrong-flag', carrier + payload,
                      (1, len(carrier)), (len(carrier) + 1, len(payload)),
                      False, False, True, False)


def mixed_image_vectors(original):
    """Only genuine OA/SA overlap sources; raw-only sources use image_vectors."""
    yield from image_vectors(original)
    for image_scoped, value_scoped in ((False, True), (True, False), (True, True)):
        payload = archive(original) if image_scoped else raw_archive(original)
        for carrier_scoped in (False, True):
            yield _image_vector(
                f'faithful-mixed-image-{image_scoped}-{value_scoped}-{carrier_scoped}',
                payload, original, image_scoped, value_scoped, True,
                carrier_scoped=carrier_scoped)
    payload = archive(original)
    yield _image_vector('truncated-scoped-image', payload[:-1],
                        original, True, False, False)
    yield _image_vector('overlong-scoped-image', payload + b'\0',
                        original, True, False, False)
