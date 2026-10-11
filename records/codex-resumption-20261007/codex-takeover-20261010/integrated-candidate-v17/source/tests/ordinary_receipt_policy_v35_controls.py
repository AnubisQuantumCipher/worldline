"""Additive source-only controls; Main runs on genuine isolated original sources.

Exported packets are observations, never grant/owner/source-authority DTOs.
Actual route positives originate in WorldlineDaemon.register and the selected
original RequestPeer. Chain positives come from actual store rows/opened files.
No control replaces inherited cases, contracts, assertions or timeout budgets.
"""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path

from worldline.core import hash_id
from worldline.store import CHAIN_GENESIS
from worldline.errors import WorldlineError
from worldline.operation_capture import archive
from worldline.ordinary_receipt_policy import (
    _COLUMN_NAMES, _decide, _route_decide, event_policy, mutating_request,
    actual_requester, owner_request, receipt_policy, receipt_schema, reserved_claim, verify_columns,
)


def export_actual_route_frame(daemon, operation, peer, destination):
    selected = daemon._operations[operation]
    reason, packet = _route_decide(daemon.store.core, 0, daemon, operation, selected, 'owner_only')
    if reason == 'PEER_OBSERVATION_REQUIRED':
        packet['peer_uid'] = peer.observation()['peer']['uid']
        packet['daemon_uid'] = os.getuid()
        reason = _decide(daemon.store.core, 0, packet)
    assert reason == 'READY'
    mutation_reason, mutation = _route_decide(daemon.store.core, 7, daemon, operation, selected, 'mutating')
    assert mutation_reason in ('READY', 'READY_MUTATING')
    frame = {'owner': packet, 'mutation': mutation}
    Path(destination).write_bytes(archive(frame))
    return frame


def exercise_actual_route_controls(core, frame):
    assert _decide(core, 0, frame['owner']) == 'READY'
    assert _decide(core, 7, frame['mutation']) in ('READY', 'READY_MUTATING')
    for mode, original in ((0, frame['owner']), (7, frame['mutation'])):
        for label, alter in (
            ('selected-identity', lambda p: p['selected'].__setitem__('identity', 0)),
            ('selected-handler', lambda p: p['selected'].__setitem__('handler_identity', 0)),
            ('missing-register-history', lambda p: p['registrations'].clear()),
            ('truncated-register-history', lambda p: p['registrations'].pop()),
            ('truncated-runtime-roster', lambda p: p['routes'].pop()),
            ('register-handler-split', lambda p: p['registrations'][0].__setitem__('handler_identity', 0)),
            ('register-key-split', lambda p: p['registrations'][0].__setitem__('key_identity', 0)),
            ('metadata-record-class', lambda p: p['routes'][0].__setitem__('class', 'ProjectedFlags')),
            ('missing-original-field', lambda p: p['routes'][0]['fields'].pop('owner_only')),
        ):
            altered = deepcopy(original)
            alter(altered)
            assert _decide(core, mode, altered) == 'ROUTE_OBSERVATION_MISMATCH', label
    return ('selected-identity', 'selected-handler', 'missing-register-history',
            'truncated-register-history', 'truncated-runtime-roster', 'register-handler-split',
            'register-key-split', 'metadata-record-class', 'missing-original-field')


def exercise_custom_register_domain(core, daemon, peer):
    """Use the real register API and genuine existing ping handler, not DTO flags.

    Main supplies a disposable isolated daemon; registrations intentionally remain
    in its complete source roster. No production daemon is a control fixture.
    """
    observations = []
    class LiveTruth:
        def __init__(self, label, value):
            self.label, self.value = label, value
        def __bool__(self):
            observations.append(self.label)
            return self.value
    values = (None, False, True, 0, 1, -(1 << 257), 0.0, -0.0,
              float('nan'), float('inf'), '', 'x', b'', b'x', [], [None],
              {}, {'opaque-member': object()}, set(), {object()}, bytearray(), bytearray(b'x'),
              range(1 << 257))
    actual_uid = peer.observation()['peer']['uid']
    for index, value in enumerate(values):
        name = f'ordinary-v35-custom-{index}'
        daemon.register(name, daemon._ping, mutating=value, owner_only=value)
        selected = daemon._operations[name]
        reason, packet = _route_decide(core, 0, daemon, name, selected, 'owner_only')
        assert reason == ('PEER_OBSERVATION_REQUIRED' if bool(value) else 'READY')
        if reason == 'PEER_OBSERVATION_REQUIRED':
            packet['peer_uid'], packet['daemon_uid'] = actual_uid, os.getuid()
            expected = 'READY' if actual_uid == os.getuid() else 'NEEDS_DAEMON_ACCOUNT'
            assert _decide(core, 0, packet) == expected
        assert mutating_request(core, daemon, name, selected) == bool(value)
    # A non-string registered key cannot be selected by JSON op, but remains in
    # the original complete roster. Do not silently filter or reject it.
    daemon.register(object(), daemon._ping)
    name = 'ordinary-v35-live-protocol'
    daemon.register(name, daemon._ping, owner_only=LiveTruth('owner', False),
                    mutating=LiveTruth('mutating', True))
    selected = daemon._operations[name]
    owner_request(core, daemon, name, selected,
                  lambda: (_ for _ in ()).throw(AssertionError('unexpected peer observation')))
    assert observations == ['owner']
    assert mutating_request(core, daemon, name, selected)
    assert observations == ['owner', 'mutating']
    class OriginalMetaclass(type):
        def __getattribute__(self, attribute):
            if attribute in ('__module__', '__qualname__'):
                raise AssertionError('metadata acquisition invoked a custom metaclass protocol')
            return super().__getattribute__(attribute)
    class OriginalMetadata(metaclass=OriginalMetaclass):
        def __bool__(self):
            observations.append('metaclass-truth')
            return False
    name = 'ordinary-v35-original-metaclass'
    daemon.register(name, daemon._ping, owner_only=OriginalMetadata(),
                    mutating=OriginalMetadata())
    selected = daemon._operations[name]
    owner_request(core, daemon, name, selected,
                  lambda: (_ for _ in ()).throw(AssertionError('unexpected peer observation')))
    assert not mutating_request(core, daemon, name, selected)
    assert observations == ['owner', 'mutating', 'metaclass-truth', 'metaclass-truth']
    return ('all-original-builtin-truth-domains', 'arbitrary-int', 'both-zero-signs',
            'nan-and-infinity-truth', 'opaque-container-members', 'huge-range',
            'complete-nonstring-register-key', 'actual-protocol-order',
            'no-new-metaclass-observation-protocol')


def exercise_schema_actor_controls(core):
    for value in (1, True, 1.0):
        event_policy(core, {'schemaVersion': value}, True)
    calls = []
    class ActualSchema:
        def __ne__(self, value):
            calls.append(('schema-ne', value))
            return False
    event_policy(core, {'schemaVersion': ActualSchema()}, True)
    assert calls == [('schema-ne', 1)]
    class ActualAuthored:
        def __bool__(self):
            raise AssertionError('authored truth must follow successful schema')
    for value in (False, 0, '1', None, float('nan'), float('inf')):
        try:
            event_policy(core, {'schemaVersion': value}, ActualAuthored())
        except WorldlineError as exc:
            assert exc.code == 'INVALID_SCHEMA'
        else:
            raise AssertionError('invalid original schema accepted')
    class LaterKind:
        def __str__(self):
            raise AssertionError('kind conversion must follow actor refusal')
    assert reserved_claim({'actor': '\u2003WorldLINE\u00a0', 'kind': LaterKind()}, core=core)
    assert reserved_claim({'actor': '\u017fY\u017fTEM', 'kind': LaterKind()}, core=core)
    assert reserved_claim({'actor': 'independent-agent', 'kind': '\u2003 FILE-DELTA\u00a0'}, core=core)
    assert reserved_claim({'actor': 'independent-agent', 'kind': 'independent-record'}, core=core) is None
    return ('bool-int-float-schema-one', 'live-schema-comparison-domain',
            'invalid-schema-before-authored-truth', 'unicode-strip-casefold',
            'reserved-actor-before-kind-conversion', 'original-kind-conversion')


def export_actual_chain_frames(store, destination):
    frames = []
    with store._lock:
        for kind, table in (('events', 'causal_events'), ('receipts', 'receipts')):
            previous = CHAIN_GENESIS
            rows = store._connection.execute(f'SELECT * FROM {table} ORDER BY rowid').fetchall()
            for row in rows:
                raw = store.read_canonical(kind, row['canonical_path'], chain_hash=row['chain_hash'])
                payload = json.loads(raw.decode('utf-8'))
                root = store.core.hash_bytes((b'worldline-event-v1' if kind == 'events'
                                              else b'worldline-receipt-record-v1') + raw)
                head = (store.core.causal_link(previous, root) if kind == 'events'
                        else store.core.receipt_link(previous, root))
                if kind == 'events':
                    columns = {'event_id': hash_id(head), 'world_instance': str(payload.get('worldInstance', '')),
                               'kind': str(payload.get('kind', 'event')), 'actor': payload.get('actor'),
                               'tool': payload.get('tool'), 'reason': payload.get('reason'),
                               'path_b64': payload.get('pathB64'), 'path_display': payload.get('pathDisplay'),
                               'line_start': payload.get('lineStart'), 'line_end': payload.get('lineEnd')}
                else:
                    columns = {'receipt_id': payload.get('receiptId'), 'transaction_id': payload.get('transactionId'),
                               'previous_receipt': payload.get('previousReceipt')}
                frames.append({'kind': kind, 'sql': dict(row), 'payload': payload, 'raw': raw,
                               'columns': columns, 'previous': hash_id(previous)})
                previous = head
    Path(destination).write_bytes(archive(frames))
    return frames


def exercise_actual_chain_controls(core, frames):
    assert {frame['kind'] for frame in frames} == {'events', 'receipts'}
    checked = set()
    for frame in frames:
        assert _decide(core, 8, frame) == 'READY'
        previous = bytes.fromhex(frame['previous'][7:])
        assert verify_columns(core, frame['kind'], frame['sql'], frame['payload'], frame['raw'],
                              frame['columns'], previous) == []
        for name in frame['columns']:
            altered = deepcopy(frame)
            marker = 'ordinary-v35-mismatching-column'
            if altered['sql'][name] == marker:
                marker += '-other'
            altered['sql'][name] = marker
            assert _decide(core, 8, altered) == 'ROW_COLUMNS_MISMATCH', name
            differing = verify_columns(core, altered['kind'], altered['sql'], altered['payload'], altered['raw'],
                                       altered['columns'], previous)
            assert differing == [name], (name, differing)
            checked.add(name)
        altered = deepcopy(frame)
        altered['raw'] += b'not-json'
        assert _decide(core, 8, altered) == 'MALFORMED_INPUT'
    assert checked == set(_COLUMN_NAMES)
    return tuple(sorted(checked))


def exercise_actual_requester_controls(store, receipt):
    """Main invokes separately in actual operation and owner-canonical scopes."""
    requester = actual_requester(store)
    assert requester is not None
    assert requester['schema'] in ('worldline.requester-operation-binding-v1',
                                   'worldline.owner-canonical-binding-v1')
    source = receipt_schema(store.core, receipt)
    receipt_policy(store.core, receipt, requester, source)
    altered = deepcopy(receipt)
    altered['requesterBinding'] = {**requester, 'source-substitution': 'not-original'}
    try:
        receipt_policy(store.core, altered, requester, source)
    except WorldlineError as exc:
        assert exc.code == 'INVALID_RECEIPT'
    else:
        raise AssertionError('foreign requester source accepted')
    return requester['schema']
