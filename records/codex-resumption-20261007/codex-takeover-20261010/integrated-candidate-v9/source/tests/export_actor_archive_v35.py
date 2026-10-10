"""Original native value and authenticated principal fixture exporters; UNRUN.

Import/run only in Main's identified guarded same-source campaign. Value
specimens exercise the actual original native library; they do not claim a live
protected actor, owner enrollment or authenticated principal provisioning.
"""
from __future__ import annotations
import ctypes as C
from dataclasses import replace
import json
import os
from pathlib import Path
from types import SimpleNamespace


def export_actor_values(directory):
    from worldline import resource_actor_execution as X
    from worldline import resource_actor_admission as D
    from worldline.operation_authority_kernel import Input
    from worldline.root_worker_codec import archive
    from test_resource_actor_execution_v1 import specimen
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    kernel = X.ActorExecutionKernel(SimpleNamespace(_lib=C.CDLL(os.environ['WORLDLINE_CORE_LIB'])))
    cases = []

    def emit(name, decision, material, replay, correspondence):
        observation = directory / (name + '.actor')
        operands = directory / (name + '.material')
        observation.write_bytes(archive(decision))
        operands.write_bytes(archive({'observation': decision, 'material': material}))
        cases.append({'name': name, 'observation': observation.name, 'material': operands.name,
                      'replay': replay, 'correspondence': correspondence})

    for uid in (0, 7):
        values = specimen(uid)
        material = dict(zip(('packet', 'actor', 'capabilities', 'groups', 'proc_groups',
                             'crosswalk', 'authority_snapshot'), values))
        original = kernel.check(*values)
        assert original.status == 'READY_VALUE_CONJUNCTION'
        emit(f'uid-{uid}-accepted', original, material, 'NATIVE_REDECIDED:READY_VALUE_CONJUNCTION', True)
        for field, raw_type in (('actor_input', D.RawActorPacket),
                                ('authority_input', Input),
                                ('crosswalk', X.RawExecutionCrosswalk)):
            for name, _kind in raw_type._fields_:
                raw = bytearray(getattr(original, field))
                raw[getattr(raw_type, name).offset] ^= 1
                changed = replace(original, **{field: bytes(raw)})
                emit(f'uid-{uid}-{field}-{name}', changed, material, None, False)
        for field in ('actor_arena', 'authority_arena'):
            for offset in range(len(getattr(original, field))):
                raw = bytearray(getattr(original, field)); raw[offset] ^= 1
                emit(f'uid-{uid}-{field}-{offset}', replace(original, **{field: bytes(raw)}), material, None, False)
            emit(f'uid-{uid}-{field}-trailing', replace(original, **{field: getattr(original, field) + b'\0'}), material, None, False)
        for field in ('actor_rosters', 'authority_rosters'):
            rosters = getattr(original, field)
            for ordinal, (name, raw, count) in enumerate(rosters):
                altered = list(rosters); altered[ordinal] = (name, raw, count + 1)
                emit(f'uid-{uid}-{field}-{name}-count', replace(original, **{field: tuple(altered)}), material,
                     'DECODE_REFUSED:READY_VALUE_CONJUNCTION', False)
                altered = list(rosters); altered[ordinal] = (name + '-changed', raw, count)
                emit(f'uid-{uid}-{field}-{name}-name', replace(original, **{field: tuple(altered)}), material,
                     'DECODE_REFUSED:READY_VALUE_CONJUNCTION', False)
                for offset in range(len(raw)):
                    body = bytearray(raw); body[offset] ^= 1
                    altered = list(rosters); altered[ordinal] = (name, bytes(body), count)
                    emit(f'uid-{uid}-{field}-{name}-byte-{offset}', replace(original, **{field: tuple(altered)}), material, None, False)
        changed = list(values); changed[1] = replace(changed[1], sender_uid=0)
        if uid == 0: changed[1] = replace(changed[1], proc_saved_uid=0)
        refused = kernel.check(*changed)
        assert refused.status == 'ACTOR_REFUSED'
        refusal_material = dict(zip(material, changed))
        emit(f'uid-{uid}-authentic-native-refusal', refused, refusal_material, 'NATIVE_REDECIDED:ACTOR_REFUSED', True)
        import copy
        changed = list(values); changed[-1] = copy.deepcopy(values[-1])
        changed[-1]['grants'][0]['state'] = 'REVOKED'
        refused = kernel.check(*changed)
        assert refused.status == 'AUTHORITY_REFUSED'
        emit(f'uid-{uid}-authentic-authority-refusal', refused, dict(zip(material, changed)),
             'NATIVE_REDECIDED:AUTHORITY_REFUSED', True)
        for status in X.STATUSES[1:]:
            emit(f'uid-{uid}-label-{status}', replace(original, status=status), material,
                 'OUTPUT_CONFLICT:READY_VALUE_CONJUNCTION', True)
        for offset in range(len(original.raw_output)):
            raw = bytearray(original.raw_output); raw[offset] ^= 1
            emit(f'uid-{uid}-output-{offset}', replace(original, raw_output=bytes(raw)), material,
                 'OUTPUT_CONFLICT:READY_VALUE_CONJUNCTION', True)
        emit(f'uid-{uid}-transport', replace(original, transport_status=1), material,
             'OUTPUT_CONFLICT:READY_VALUE_CONJUNCTION', True)
    (directory / 'cases.json').write_text(json.dumps(cases, sort_keys=True, indent=2) + '\n')
    return cases


def export_original_envelopes(principal, directory):
    """Export only existing genuine protected original journal captures.

    This never creates an operation/grant/Geneses, dispatches an actor/effect,
    edits a principal or fabricates an accepted followup/broker boundary.
    The guarded principal campaign supplies an already authentic actual principal.
    """
    from worldline.protected_operations import CanonicalOperationPrincipal
    from worldline.protected_startup import private_bytes, require
    from worldline.root_worker_current_state import capture_operation_context
    from worldline.root_worker_codec import archive
    from worldline.canonical_actor_execution import scoped_components
    require(type(principal) is CanonicalOperationPrincipal, 'ACTOR_EXPORT_ACTUAL_PRINCIPAL_REQUIRED')
    principal.intact()
    require(private_bytes(principal.journal.path) == principal.journal.raw, 'ACTOR_EXPORT_JOURNAL_CHANGED')
    principal.journal.load()
    producer = scoped_components(principal)
    context = capture_operation_context(principal)
    directory = Path(directory); directory.mkdir(parents=True, exist_ok=True)
    names = {'ACTOR_EXECUTION_NATIVE': 'ACTOR_EXECUTION', 'FOLLOWUP_NATIVE': 'FOLLOWUP',
             'FULL_BROKER_NATIVE': 'FULL_BROKER'}
    cases = []
    for ordinal, event in enumerate(principal.journal.body['events']):
        for index, boundary in enumerate(event['boundaries']):
            if boundary['name'] not in names: continue
            kind = names[boundary['name']]
            material = boundary['value'] if kind == 'FULL_BROKER' else boundary['material']
            path = directory / f'{ordinal}-{index}-{kind}.boundary'
            path.write_bytes(archive({'material': material, 'event': event, 'context': context}))
            cases.append({'kind': kind, 'path': path.name, 'expected': True})
    require(set(row['kind'] for row in cases) == set(names.values()), 'ACTOR_EXPORT_COMPLETE_ORIGINAL_ENVELOPES_REQUIRED')
    (directory / 'boundaries.json').write_text(json.dumps(cases, sort_keys=True, indent=2) + '\n')
    from worldline import resource_scoped_run_ledger as S
    from worldline.resource_actor_execution import ActorExecutionNativeDecision
    producer.observations.load()
    actors = []
    for ordinal, event in enumerate(producer.observations.events):
        if event['cause'] != 'ACTOR_NATIVE_COMMITTED': continue
        witness = S.restore(event['payload'])
        require(witness['schema'] == 'worldline.genuine-actor-native-durable-witness-v1'
                and type(witness['composite']) is ActorExecutionNativeDecision,
                'ACTOR_EXPORT_ORIGINAL_COMPLETE_WITNESS_REQUIRED')
        material = {name: witness[name] for name in
                    ('packet', 'actor', 'capabilities', 'groups', 'proc_groups', 'crosswalk')}
        material['authority_snapshot'] = witness['authority']['authority_snapshot']
        observed = producer.execution_kernel.check(
            material['packet'], material['actor'], material['capabilities'], material['groups'],
            material['proc_groups'], material['crosswalk'], material['authority_snapshot'])
        require(observed == witness['composite'], 'ACTOR_EXPORT_ORIGINAL_NATIVE_REPLAY_CHANGED')
        path = directory / f'authentic-{ordinal}.actor'
        operands = directory / f'authentic-{ordinal}.material'
        path.write_bytes(archive(witness['composite']))
        operands.write_bytes(archive({'observation': witness['composite'], 'material': material}))
        actors.append({'observation': path.name, 'material': operands.name,
                       'replay': 'NATIVE_REDECIDED:' + observed.status})
    require(bool(actors), 'ACTOR_EXPORT_GENUINE_ORIGINAL_ACTOR_CAPTURE_REQUIRED')
    (directory / 'authentic-actors.json').write_text(json.dumps(actors, sort_keys=True, indent=2) + '\n')
    return cases


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(); parser.add_argument('directory')
    export_actor_values(parser.parse_args().directory)
