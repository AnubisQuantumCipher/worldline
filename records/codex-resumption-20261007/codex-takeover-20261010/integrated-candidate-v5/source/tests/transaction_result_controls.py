"""Additive controls consuming actual acquired, retained WORLDLINE transactions.

No positive is synthesized. Main obtains each material from its genuine actor
commit/retry campaign, with the complete operation journal and packet sources.
These controls do not replace the inherited assertions or their timeouts.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

from worldline.canonical import canonical_bytes
from worldline.operation_capture import archive, restore_archive
from worldline.recovery_observation import restore_archive as restore_packet_archive
from worldline.transaction_relation import ACCEPTED, RECORD_INVALID, _decide, committed_frame


def export_transaction_frame(material, destination):
    """Export the exact complete six-span request selected from actual material."""
    frame = committed_frame(material)
    Path(destination).write_bytes(archive(frame))
    return frame


def _initial(frame):
    sources = [restore_archive(bytes.fromhex(item['value']))
               for item in frame['authority'] if item['name'] == 'FULL_BROKER_NATIVE']
    selected = [item['facts']['worldline_chains'] for item in sources
                if item['phase'] == 'ISSUED']
    assert len(selected) == 1
    return selected[0]


def _collapse_events(frame):
    transaction = frame['actual']['transactionId']
    return [index for index, (_, raw) in enumerate(frame['chains']['events'])
            if (payload := json.loads(raw.decode('utf-8'))).get('kind') == 'collapse-receipt'
            and payload.get('transactionId') == transaction]


def _refuses(core, original, change):
    altered = deepcopy(original)
    change(altered)
    assert _decide(core, altered) == RECORD_INVALID


def _replace_event_field(core, frame, name, value):
    index = _collapse_events(frame)[-1]
    sql, raw = frame['chains']['events'][index]
    payload = json.loads(raw.decode('utf-8'))
    payload[name] = value
    raw = canonical_bytes(payload)
    sql = dict(sql)
    root = core.hash_bytes(b'worldline-event-v1' + raw)
    previous = bytes.fromhex(sql['predecessor'][7:])
    head = core.causal_link(previous, root)
    sql.update(event_root='sha256:' + root.hex(), chain_hash='sha256:' + head.hex(),
               event_id='sha256:' + head.hex())
    frame['chains']['events'][index] = (sql, raw)


def _append_retry_event(frame):
    indexes = _collapse_events(frame)
    if indexes:
        candidate = deepcopy(frame['chains']['events'][indexes[-1]])
    else:
        # Explicitly negative, unpersisted append candidate. Never manufacture
        # a positive old event for the genuine receipt-existing crash profile.
        candidate = ({}, canonical_bytes({
            'schemaVersion': 1, 'kind': 'collapse-receipt', 'actor': 'worldline',
            'origin': 'worldline', 'reason': None,
            'worldInstance': frame['actual']['candidateWorld'],
            'transactionId': frame['actual']['transactionId'],
            'receiptId': frame['result']['receipt']['receiptId'],
            'receiptRoot': frame['result']['receipt']['receiptRoot']}))
    frame['chains']['events'].append(candidate)


def exercise_transaction_result_controls(core, acquired):
    """acquired has real commit/retry/foreign/unrelated/recaptured/historical materials.

    recaptured must be a genuine successful transaction with independently
    different pre-effect/post-flush packet inputs. retry must retain the receipt
    that was already present in its genuine ISSUED observation. foreign refers
    to a real populated measurement, not an invented FOUND authorization.
    historical retains original old packets and actual worker records without
    a manufactured postFlushPacket. Its syntax capsules are actual acquisitions.
    """
    required = ('commit', 'retry', 'foreign', 'unrelated', 'recaptured', 'historical')
    assert set(required) <= set(acquired)
    frames = {name: committed_frame(acquired[name]) for name in required}
    for frame in frames.values():
        assert _decide(core, frame) == ACCEPTED

    commit = frames['commit']
    initial = _initial(commit)
    assert not any(sql['transaction_id'] == commit['actual']['transactionId']
                   for sql, _ in initial['receipts'])
    assert len(commit['chains']['receipts']) == len(initial['receipts']) + 1
    assert len(_collapse_events(commit)) == 1

    retry = frames['retry']
    retry_initial = _initial(retry)
    assert any(sql['transaction_id'] == retry['actual']['transactionId']
               for sql, _ in retry_initial['receipts'])
    assert retry['chains']['receipts'] == retry_initial['receipts']
    old_count = sum(json.loads(raw.decode('utf-8')).get('kind') == 'collapse-receipt'
                    and json.loads(raw.decode('utf-8')).get('transactionId') == retry['actual']['transactionId']
                    for _, raw in retry_initial['events'])
    assert len(_collapse_events(retry)) == old_count

    foreign = frames['foreign']['result']['receipt']['foreignWorldContamination']
    assert 'measuredBy' in foreign and 'measurement' in foreign
    assert frames['unrelated']['result']['receipt']['mergeSet']['unrelatedConfigurationMutations']
    recaptured = frames['recaptured']
    before = [item for item in recaptured['authority'] if item['name'] == 'FULL_PRE_EFFECT_BOUNDARY']
    assert len(before) == 1
    pre_packet = restore_packet_archive(bytes.fromhex(before[0]['collapse_packet']))
    post_packet = restore_packet_archive(bytes.fromhex(recaptured['actual']['postFlushPacket']))
    assert archive(pre_packet['inputs']) != archive(post_packet['inputs'])

    _refuses(core, commit, lambda f: f['chains']['events'].pop(_collapse_events(f)[-1]))
    _refuses(core, commit, lambda f: f['chains']['events'].append(deepcopy(f['chains']['events'][_collapse_events(f)[-1]])))
    _refuses(core, commit, lambda f: _replace_event_field(core, f, 'receiptId', 'WL:' + '0' * 64))
    _refuses(core, commit, lambda f: _replace_event_field(core, f, 'receiptRoot', 'sha256:' + '0' * 64))
    _refuses(core, commit, lambda f: _replace_event_field(core, f, 'worldInstance', 'different-world'))
    _refuses(core, commit, lambda f: _replace_event_field(core, f, 'transactionId', 'different-transaction'))
    _refuses(core, retry, lambda f: f['chains']['receipts'].append(deepcopy(f['chains']['receipts'][-1])))
    _refuses(core, retry, _append_retry_event)
    _refuses(core, frames['foreign'], lambda f: f['result']['receipt']['foreignWorldContamination'].__setitem__('measurement', 'FOUND'))
    _refuses(core, frames['unrelated'], lambda f: f['result']['receipt']['mergeSet'].__setitem__('unrelatedConfigurationMutations', []))
    _refuses(core, recaptured, lambda f: f['actual'].__setitem__('postFlushPacket', before[0]['collapse_packet']))
    _refuses(core, recaptured, lambda f: f['actual'].pop('postFlushPacket'))
    historical = frames['historical']
    assert 'postFlushPacket' not in historical['actual']
    _refuses(core, historical, lambda f: f['actual']['decisionInputsAtCommit'].__setitem__('foreignWrites', {'state': 'FOUND'}))
    _refuses(core, commit, lambda f: f['actual']['stagedRootRecords'][0].__setitem__('pathB64', 'L2RpZmZlcmVudA=='))
    _refuses(core, commit, lambda f: f['actual']['stagedManifestRecords'][0].__setitem__('rootHash', 'sha256:' + '0' * 64))
    _refuses(core, commit, lambda f: f['authority'].clear())
    _refuses(core, commit, lambda f: f['result']['receipt'].__setitem__('transactionId', 'different-transaction'))
    return {'positive': required, 'negative': ('missing-event', 'duplicate-event', 'wrong-receipt-id',
        'wrong-receipt-root', 'wrong-world', 'wrong-transaction', 'duplicate-retry-receipt',
        'duplicate-retry-event', 'foreign-projection', 'unrelated-projection', 'copied-pre-packet',
        'dropped-post-packet', 'historical-commit-inputs', 'root-registration', 'manifest-root',
        'missing-authority', 'cross-transaction')}


def exercise_requirement_coercion_controls(core, acquired):
    """Use original accepted context/current operand captures, not hash flags."""
    from worldline.transaction_relation import freshness
    required = ('absent', 'null', 'false', 'zero', 'empty-string', 'empty-list',
                'empty-map', 'list-pairs', 'string-pairs', 'duplicate-pairs')
    assert set(required) <= set(acquired)
    for name in required:
        context, current = acquired[name]
        assert freshness(core, context, current) == ACCEPTED
    return required


def exercise_historical_syntax_controls(core, material):
    """Require genuine old signed packets and actual protected syntax capsules."""
    frame = committed_frame(material)
    facts = [item for item in frame['authority']
             if item['name'] == 'RECOVERY_SYNTAX_FACTS_V1']
    assert facts and 'postFlushPacket' not in frame['actual']
    for item in facts:
        payload = restore_archive(bytes.fromhex(item['value']))
        assert type(payload['packet']) is bytes and payload['capsules']
        for capsule in payload['capsules']:
            assert set(capsule) == {'result', 'declaration', 'capsule'}
            assert all(type(value) is bytes for value in capsule.values())
    assert _decide(core, frame) == ACCEPTED

    def alter_fact(altered, change):
        selected = next(item for item in altered['authority']
                        if item['name'] == 'RECOVERY_SYNTAX_FACTS_V1')
        payload = restore_archive(bytes.fromhex(selected['value']))
        change(payload)
        selected['value'] = archive(payload).hex()

    _refuses(core, frame, lambda f: alter_fact(f, lambda p: p.__setitem__('packet', b'\\0')))
    _refuses(core, frame, lambda f: alter_fact(f, lambda p: p.__setitem__('capsules', [])))
    for key in ('result', 'declaration', 'capsule'):
        _refuses(core, frame, lambda f, key=key: alter_fact(f,
            lambda p: p['capsules'][0].__setitem__(key, b'{}')))
    return ('actual-historical-capsules', 'wrong-original-packet', 'missing-capsules',
            'changed-original-result', 'changed-independent-declaration', 'changed-controller')


def exercise_recovery_packet_selector_controls(core, noncommit_snapshot, committed_material):
    """Preserve actual absent-packet operation/history and malformed negatives."""
    from worldline.operation_result_relation import OperationResultRelation
    from worldline.transaction_relation import recovery_packets
    assert OperationResultRelation(core).observe(noncommit_snapshot)['decision'] == 'READY'
    material = restore_archive(bytes.fromhex(noncommit_snapshot['evidence']['effect_material']))
    assert material['result']['actual_transaction'] is None
    boundaries = material['commit_authority']
    original = [item for item in boundaries if item['name'] == 'FULL_PRE_EFFECT_BOUNDARY']
    assert original and all(item['collapse_packet'] is None for item in original)
    assert recovery_packets(boundaries, None) == []
    actual = committed_material['result']['actual_transaction']
    packets = recovery_packets(committed_material['commit_authority'], actual)
    assert packets and all(type(packet) is bytes for packet in packets)
    bad = deepcopy(boundaries)
    next(item for item in bad if item['name'] == 'FULL_PRE_EFFECT_BOUNDARY')['collapse_packet'] = 'not-hex'
    try:
        recovery_packets(bad, None)
    except ValueError:
        pass
    else:
        raise AssertionError('present malformed packet was silently treated as absent')
    return ('actual-noncommit-absent-packets', 'actual-commit-packets', 'malformed-present-packet')
