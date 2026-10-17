"""Additive native controls; run only inside the lead's admitted execution frame.

The caller supplies an original context/current pair retained from a genuine
evaluation or the unchanged original TEST_ONLY producer fixture. The latter
does not establish production custody. This file creates no positive transaction.
It preserves every original control and timeout. No native calls run on import.
"""
from __future__ import annotations

from copy import deepcopy
import json

from worldline.canonical import canonical_bytes
from worldline.operation_capture import archive
from worldline.transaction_relation import (
    ACCEPTED, CONTEXT_INVALID, _decide, _requirement_body, freshness,
)


def _ordered(value, *, reverse):
    if type(value) is dict:
        return {key: _ordered(value[key], reverse=reverse)
                for key in sorted(value, reverse=reverse)}
    if type(value) is list:
        return [_ordered(item, reverse=reverse) for item in value]
    return deepcopy(value)


def _request(context, current):
    """Complete operands for a negative transport probe, not a Python verdict."""
    body = {key: value for key, value in context.items() if key != 'contextHash'}
    requirement = _requirement_body(context['requirement'])
    current_body = _requirement_body(current)
    return {'relation': 'freshness', 'context': deepcopy(context),
            'current': deepcopy(current), 'contextBody': body,
            'contextJSON': canonical_bytes(body),
            'requirementBody': requirement,
            'requirementJSON': canonical_bytes(requirement),
            'currentBody': current_body,
            'currentJSON': canonical_bytes(current_body)}


def exercise_freshness_json_order_controls(core, context, current):
    """Use the actual native core and an original schemaVersion=1 input pair.

    Reported labels mean these additive controls passed on that supplied pair,
    never complete Phase One acceptance or proof. Preserve input provenance in
    the enclosing frame result. No skip is allowed for an unsuitable fixture.
    """
    if not __debug__:
        raise RuntimeError('native regression controls require assertions enabled')
    assert type(context) is dict and type(current) is dict
    assert type(context.get('schemaVersion')) is int
    assert context['schemaVersion'] == 1
    original_context = archive(context)
    original_current = archive(current)
    assert freshness(core, context, current) == ACCEPTED

    increasing = _ordered(context, reverse=False)
    decreasing = _ordered(context, reverse=True)
    assert archive(increasing) != archive(decreasing), 'order probe is vacuous'
    for reverse in (False, True):
        changed_context = _ordered(context, reverse=reverse)
        changed_current = _ordered(current, reverse=reverse)
        # Object order changes, while values, list order and canonical hashes do
        # not. Hashes are not repaired to manufacture a positive case.
        assert canonical_bytes(changed_context) == canonical_bytes(context)
        assert canonical_bytes(changed_current) == canonical_bytes(current)
        assert freshness(core, changed_context, changed_current) == ACCEPTED

    body = _request(context, current)['contextBody']
    assert '__json_order_control_extra__' not in body
    malformed = {}
    for name, replacement in (('boolean-for-integer', True),
                              ('float-for-integer', 1.0),
                              ('changed-integer', 2)):
        value = deepcopy(body)
        value['schemaVersion'] = replacement
        malformed[name] = json.dumps(value, ensure_ascii=False, allow_nan=False,
                                     sort_keys=True, separators=(',', ':')).encode('utf-8')
    missing = deepcopy(body)
    del missing['schemaVersion']
    malformed['missing-member'] = canonical_bytes(missing)
    extra = deepcopy(body)
    extra['__json_order_control_extra__'] = None
    malformed['extra-member'] = canonical_bytes(extra)
    original_json = canonical_bytes(body)
    assert original_json.endswith(b'}')
    # Ordinary JSON retains last-key-wins semantics. An identical duplicate is
    # not a refusal case; the last value here intentionally disagrees with the
    # original archive's schemaVersion. Do not tighten the accepted codec.
    malformed['duplicate-last-value-mismatch'] = (
        original_json[:-1] + b',"schemaVersion":2}')

    for name, raw in malformed.items():
        request = _request(context, current)
        request['contextJSON'] = raw
        # Deliberately make the negative's claimed JSON digest consistent with
        # its altered bytes. The native JSON/archive correspondence check must
        # reject it; a stale digest must not accidentally be the only guard.
        request['context']['contextHash'] = 'sha256:' + core.hash_bytes(
            b'worldline-validation-v1' + raw).hex()
        assert _decide(core, request) == CONTEXT_INVALID, name

    assert archive(context) == original_context, 'original context was mutated'
    assert archive(current) == original_current, 'original current was mutated'
    return {'positive': ('actual-original', 'ascending-object-order',
                         'descending-object-order'),
            'negative': tuple(malformed), 'phase_acceptance': False}
