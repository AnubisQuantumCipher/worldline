"""Owned transport for complete native transaction consumer relations.

No policy/roster/marker status or equality flag is sent as authority. Original
objects and separately encoded full preimages stay alive through the call.
"""
from __future__ import annotations

import ctypes
from typing import Mapping

from .canonical import canonical_bytes
from .errors import CoreUnavailable
from .operation_capture import archive

ACCEPTED = 0
CONTEXT_MISSING = 1
CONTEXT_INVALID = 2
VERIFIER_MODIFIED = 3
EVIDENCE_STALE = 4
RECORD_INVALID = 5
LIVE_MANIFESTS = 6
HISTORICAL_MANIFESTS = 7
STAGED_MISMATCH = 8
FINISH_COMMITTED = 9
ABORT_PREPARED = 10
AMBIGUOUS = 11
ROSTER_INCOMPLETE = 12


def _decide(core, request):
    try:
        call = core._lib.wl_transaction_relation_v1
    except AttributeError as exc:
        raise CoreUnavailable('complete transaction relation ABI unavailable') from exc
    raw = archive(request)
    if ctypes.c_size_t(len(raw)).value != len(raw):
        raise OverflowError('transaction archive extent does not fit size_t')
    owner = (ctypes.c_uint8 * len(raw)).from_buffer_copy(raw)
    call.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
    call.restype = ctypes.c_uint8
    code = int(call(owner, len(raw)))
    if code not in range(ROSTER_INCOMPLETE + 1):
        raise CoreUnavailable('complete transaction relation refused transport', code=code)
    return code


def _requirement_body(requirement):
    result = {key: value for key, value in requirement.items() if key != 'requirementHash'}
    result['policy'] = {key: value for key, value in dict(requirement.get('policy') or {}).items()
                        if key not in ('sourceSha256', 'warnings', 'sourceObservation')}
    return result


def freshness(core, context, current):
    context_body = ({key: value for key, value in context.items() if key != 'contextHash'}
                    if isinstance(context, dict) else None)
    requirement = context.get('requirement') or {} if isinstance(context, dict) else {}
    requirement_body = _requirement_body(requirement) if isinstance(requirement, dict) else None
    current_body = _requirement_body(current)
    return _decide(core, {'relation': 'freshness', 'context': context, 'current': dict(current),
        'contextBody': context_body, 'contextJSON': canonical_bytes(context_body),
        'requirementBody': requirement_body, 'requirementJSON': canonical_bytes(requirement_body),
        'currentBody': current_body, 'currentJSON': canonical_bytes(current_body)})


def _row(source, *, agent=False):
    from .evaluation_producer import capture
    from .finalization_journal import payload_acquisitions
    from .finalize import runner_agent_record
    from .evaluation_policy import raw_json
    result, _legacy = runner_agent_record(source) if agent else (source, False)
    expected = capture(source.get('engineInvocationObservation'))
    observed = capture(payload_acquisitions(source.get('engineRawObservations')))
    normal = capture(result)
    return {'source': dict(source), 'normal': normal,
            'recordJSON': raw_json(normal).encode('ascii'),
            'expected': expected, 'expectedJSON': raw_json(expected).encode('ascii'),
            'observed': observed, 'observedJSON': raw_json(observed).encode('ascii')}


def execution(core, subject, current, recorded_checks):
    finalization = subject.evidence.get('checks') if isinstance(subject.evidence, dict) else None
    agent = next((item for item in (finalization or ())
                  if isinstance(item, Mapping) and item.get('id') == 'agent'), None)
    sources = [dict(item) for item in recorded_checks if isinstance(item, Mapping)]
    return _decide(core, {'relation': 'execution', 'subject': subject,
        'current': dict(current), 'currentJSON': canonical_bytes(dict(current)),
        'selectedRows': sources, 'rows': [_row(item) for item in sources],
        'agent': None if agent is None else _row(agent, agent=True)}) == ACCEPTED


def record_identity(core, expected, record):
    return _decide(core, {'relation': 'record-identity', 'expected': expected,
                          'record': record}) == ACCEPTED


def record_state(core, expected, row, record):
    return _decide(core, {'relation': 'record', 'expected': expected,
                          'row': dict(row), 'record': record}) == ACCEPTED


def verifiers_unchanged(core, context):
    return _decide(core, {'relation': 'verifiers', 'context': context}) == ACCEPTED


def marker_valid(core, marker):
    return _decide(core, {'relation': 'marker-value', 'marker': marker}) == ACCEPTED


def frozen_manifests(manifests):
    return [{'rootKey': key, 'value': item.value,
             'canonical': item.canonical.decode('utf-8'), 'rootHash': item.root_hash}
            for key, item in sorted(manifests.items())]


def _manifest_values(manifests):
    if manifests is None:
        return None, None, None
    items = [{'rootKey': key, 'value': item.value, 'canonical': item.canonical,
              'rootHash': item.root_hash} for key, item in sorted(manifests.items())]
    roots = [{'rootKey': item['rootKey'], 'manifestRoot': item['rootHash']} for item in items]
    return items, roots, canonical_bytes(roots)


def manifests(core, record, live, retained=None):
    actual, actual_roots, actual_json = _manifest_values(live)
    historical, historical_roots, historical_json = _manifest_values(retained)
    return _decide(core, {'relation': 'manifests', 'record': dict(record),
        'live': actual, 'liveRootSet': actual_roots, 'liveRootJSON': actual_json,
        'retained': historical, 'retainedRootSet': historical_roots,
        'retainedRootJSON': historical_json,
        'retainedFrozen': None if retained is None else frozen_manifests(retained)})


def marker_state(expected, live, prepared, *, core):
    code = _decide(core, {'relation': 'marker', 'expected': expected,
                          'live': live, 'prepared': prepared})
    actions = {FINISH_COMMITTED: 'FINISH_COMMITTED', ABORT_PREPARED: 'ABORT_PREPARED',
               AMBIGUOUS: 'AMBIGUOUS'}
    if code not in actions:
        raise CoreUnavailable('transaction marker relation returned no action', code=code)
    return actions[code]


def frozen_roots(roots):
    import base64
    return [{'record': {key: value for key, value in root.items() if key != 'path'},
             'pathB64': base64.b64encode(bytes(root['path'])).decode('ascii')}
            for root in roots]


def recovery_roots(record, current):
    import base64
    frozen = record.get('stagedRootRecords')
    if frozen is None:
        return current()
    return [{**item['record'], 'path': base64.b64decode(item['pathB64'], validate=True)}
            for item in frozen]


def committed_frame(material):
    """Select full retained sources; no current grant/policy is reacquired here."""
    result = material['result']
    return {'relation': 'committed', 'original': material['capture']['transaction'],
            'actual': result['actual_transaction'], 'result': result['result'],
            'chains': material['original_worldline_chains'],
            'authority': material['commit_authority']}


def committed(core, material):
    return _decide(core, committed_frame(material)) == ACCEPTED


def recovery_syntax_fact(packet: bytes, capsules: list):
    """Carry independently acquired full syntax facts, never a source verdict.

    Native Complete checks each capsule's original source/context/role/custody
    and actual parser/helper/input/output. The packet remains byte-for-byte.
    """
    return {'name': 'RECOVERY_SYNTAX_FACTS_V1',
            'value': archive({'packet': packet, 'capsules': capsules}).hex()}


def recovery_packets(authority, actual):
    """Select exact retained packet bytes for separate protected fact acquisition.

    ISSUED arguments retain the PREPARED values, not another packet: native
    Authority_Matches joins both to FULL_PRE_EFFECT_BOUNDARY's original packet.
    Packet selection supplies no source verdict and leaves authority untouched.
    """
    packets = []
    for item in authority:
        if item['name'] == 'FULL_PRE_EFFECT_BOUNDARY' and item['collapse_packet'] is not None:
            packet = bytes.fromhex(item['collapse_packet'])
            if packet not in packets:
                packets.append(packet)
    post = None if actual is None else actual.get('postFlushPacket')
    if post is not None:
        packet = bytes.fromhex(post)
        if packet not in packets:
            packets.append(packet)
    return packets
