"""Additional controls over actual complete snapshots from the inherited campaign.

No positive fixture is synthesized here. The parent supplies distinct original
accepted OBSERVE_EFFECT and SETTLE_USE snapshots from the authenticated isolated
operation journal, plus an earlier original accepted operation snapshot. This
module does not provision, dispatch, install, exchange or invoke an actor.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
from worldline.operation_capture import archive, restore_archive
from worldline.protected_operations import clone
from worldline.operation_authority_kernel import OperationAuthorityKernel
from worldline.operation_result_relation import OperationResultRelation
from worldline.canonical import atomic_write


def export_operation_effect_fixture(core, snapshot, destination):
    """Enroll the inherited Ada assertions using the actual full native frame."""
    authority = OperationAuthorityKernel(core)
    native = authority.observe(snapshot, 'OBSERVE_EFFECT')
    assert native['decision'] == 'EFFECT_ACCEPTED', native
    assert OperationResultRelation(core).observe(snapshot)['decision'] == 'READY'
    packet = {'input': bytes.fromhex(native['input']), 'arena': bytes.fromhex(native['arena']),
              **{name: bytes.fromhex(raw) for name, raw in zip(
                  ('grants', 'uses', 'receipts', 'events'), native['rosters'], strict=True)},
              'output': bytes.fromhex(native['output']),
              'source_snapshot': archive(snapshot), 'source_observation': archive(native)}
    raw = archive(packet)
    atomic_write(Path(destination), raw)
    return {'path': str(destination), 'sha256': hashlib.sha256(raw).hexdigest(),
            'source_sha256': hashlib.sha256(packet['source_snapshot']).hexdigest()}


def capture_live_operation_effect_sources(principal, operation):
    """Acquire genuine original frames from the live authenticated journal.

    The read never provisions an actor or re-enters its handler. The native
    journal read redecides every original retained frame before selection;
    the selected effect and settlement frames retain their own full historical
    grants, reservations, result and store acquisition, not today's policy.
    """
    principal.journal.load()
    events = [event for event in principal.journal.body['events']
              if event['operation'] == operation and event['native'] is not None]
    frames = {}
    for event in events:
        command = event['native']['command']
        if command not in ('OBSERVE_EFFECT', 'SETTLE_USE') or command in frames:
            continue
        snapshot = restore_archive(bytes.fromhex(event['snapshot']))
        observed = OperationAuthorityKernel(principal.core).observe(snapshot, command)
        assert observed == event['native']['observation'], (command, observed)
        assert OperationResultRelation(principal.core).observe(snapshot)['decision'] == 'READY'
        frames[command] = snapshot
    assert 'OBSERVE_EFFECT' in frames and 'SETTLE_USE' in frames, operation
    capture = principal.journal.rows[operation]['capture']
    reserved = [index for index, event in enumerate(principal.journal.body['events'])
                if event['operation'] == operation and event['cause'] == 'RESERVED']
    assert len(reserved) == 1, operation
    return {
        'operation': operation,
        'action': capture['document']['op'],
        'reservation_index': reserved[0],
        'journal_raw': bytes(principal.journal.raw),
        'journal_sha256': hashlib.sha256(principal.journal.raw).hexdigest(),
        'original_capture': archive(capture),
        'observe_snapshot': frames['OBSERVE_EFFECT'],
        'settle_snapshot': frames['SETTLE_USE'],
    }


def export_live_operation_effect_fixture(principal, operation, destination):
    """Export an actual live-owned accepted original frame for Ada controls."""
    source = capture_live_operation_effect_sources(principal, operation)
    result = export_operation_effect_fixture(
        principal.core, source['observe_snapshot'], destination)
    return {**result, 'operation': operation, 'action': source['action'],
            'journal_sha256': source['journal_sha256'],
            'capture_sha256': hashlib.sha256(source['original_capture']).hexdigest()}


def exercise_live_actor_operation_result_controls(principal, operation, earlier_operation):
    """Enroll two actual completed actor operations without synthetic positives."""
    current = capture_live_operation_effect_sources(principal, operation)
    earlier = capture_live_operation_effect_sources(principal, earlier_operation)
    assert operation != earlier_operation
    assert earlier['reservation_index'] < current['reservation_index']
    exercise_operation_result_controls(
        principal.core, current['observe_snapshot'], current['settle_snapshot'],
        earlier['observe_snapshot'])
    return {'operation': operation, 'earlier_operation': earlier_operation,
            'journal_sha256': current['journal_sha256'],
            'earlier_journal_sha256': earlier['journal_sha256']}


def exercise_operation_result_controls(core, observe_snapshot, settle_snapshot, earlier_snapshot):
    authority = OperationAuthorityKernel(core)
    relation = OperationResultRelation(core)
    assert authority.observe(observe_snapshot, 'OBSERVE_EFFECT')['decision'] == 'EFFECT_ACCEPTED'
    assert authority.observe(settle_snapshot, 'SETTLE_USE')['decision'] in ('SETTLED_NEW', 'SETTLED_REPLAY')
    assert relation.observe(observe_snapshot)['decision'] == 'READY'
    assert relation.observe(settle_snapshot)['decision'] == 'READY'
    assert relation.observe(earlier_snapshot)['decision'] == 'READY'
    assert earlier_snapshot['binding']['id']['operation_id'] != observe_snapshot['binding']['id']['operation_id']

    def material(snapshot):
        return restore_archive(bytes.fromhex(snapshot['evidence']['effect_material']))

    def refused(change):
        changed = clone(observe_snapshot)
        source = material(changed)
        change(source)
        changed['evidence']['effect_material'] = archive(source).hex()
        assert relation.observe(changed)['decision'] != 'READY'
        assert authority.observe(changed, 'OBSERVE_EFFECT')['decision'] == 'REFUSED'

    missing = clone(observe_snapshot)
    missing['evidence']['effect_material'] = None
    assert relation.observe(missing)['decision'] != 'READY'
    assert authority.observe(missing, 'OBSERVE_EFFECT')['decision'] == 'REFUSED'

    earlier = material(earlier_snapshot)
    refused(lambda value: value.__setitem__('capture', clone(earlier['capture'])))
    refused(lambda value: value['capture'].__setitem__('request', clone(earlier['capture']['request'])))
    refused(lambda value: value.__setitem__('result', clone(earlier['result'])))
    refused(lambda value: value['original_snapshot'].__setitem__('binding', clone(earlier_snapshot['binding'])))
    refused(lambda value: value.__setitem__('original_observation', clone(earlier['original_observation'])))
    refused(lambda value: value.__setitem__('receipt_payloads', [*value['receipt_payloads'], value['receipt_payloads'][0]]))
    refused(lambda value: value.__setitem__('event_payloads', value['event_payloads'][:-1]))
    refused(lambda value: value['original_observation'].__setitem__('output', '00'))

    source = material(observe_snapshot)
    assert source['original_worldline_chains']['events'], 'the original actor fixture must contain its complete causal history'
    refused(lambda value: value['current_store'].__setitem__('events', value['current_store']['events'][:-1]))
    assert source['original_intents'], 'use an actual acknowledged operation, not a prospective packet'
    refused(lambda value: value['original_intents'][0].__setitem__('head', earlier['capture']['binding']['id']['operation_id']))
    refused(lambda value: value['stored_capture'].__setitem__('request', clone(earlier['capture']['request'])))
    refused(lambda value: value['reservation_preimage'].__setitem__('operation', earlier['capture']['operation']))
    refused(lambda value: value['requester'].__setitem__('binding', clone(earlier['capture']['binding'])))
    refused(lambda value: value['store_views']['original']['events'][0].__setitem__('raw', b'{}'))
    refused(lambda value: value['store_views']['current']['events'][0]['sql'].__setitem__('chain_hash', 'sha256:' + '00' * 32))
    if source['historical_sources']:
        refused(lambda value: value['historical_sources'][0].__setitem__('original_observation', clone(source['original_observation'])))
        refused(lambda value: value['historical_sources'][0].__setitem__('stored_result', clone(source['result'])))

    revoked = clone(settle_snapshot)
    for grant in revoked['grants']:
        grant['state'] = 'REVOKED'
    assert relation.observe(revoked)['decision'] == 'READY'
    assert authority.observe(revoked, 'SETTLE_USE')['decision'] in ('SETTLED_NEW', 'SETTLED_REPLAY')
    assert archive(material(revoked)['original_snapshot']) == archive(material(settle_snapshot)['original_snapshot'])

    # The older operation is checked using its frozen full captured history,
    # not today's selected grant, the last newer row or a regenerated result.
    assert relation.observe(clone(earlier_snapshot))['decision'] == 'READY'
