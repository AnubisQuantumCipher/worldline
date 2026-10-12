"""Fixed genuine owner construction topology for the original whole fixture.

Owner-selected full configurations remain original data. They cannot replace
creators with prebuilt authority objects or skip installation/source/genesis
joins. Every dependent value is bound by fixture_builder to actual prior creator
results or actual installed bytes; native creator utilities decide permission.
"""
from __future__ import annotations

TOPOLOGY = (
    ('worldline-store', 'worldline-store'),
    ('universe', 'universe'),
    ('issuer', 'issuer'),
    ('evidence', 'evidence'),
    ('authority-config', 'owner-data'),
    ('original-supervisor', 'original-supervisor-start'),
    ('canonical-store', 'canonical'),
    ('original-authority', 'authority'),
    ('gate-config', 'owner-data'),
    ('original-gate', 'gate'),
    ('historical-config', 'owner-data'),
    ('historical-ledger', 'full-run-ledger'),
    ('scoped-config', 'owner-data'),
    ('scoped-ledgers', 'scoped-ledgers'),
    ('launch-ledger', 'launch-ledger'),
    ('startup-genesis', 'startup-genesis'),
    ('original-supervisor-stop', 'original-supervisor-stop'),
    ('owner-policy', 'owner-data'),
    ('owner-genesis', 'owner-genesis'),
    ('operation-policy', 'owner-data'),
    ('operation-owner-genesis', 'operation-owner-genesis'),
    ('recovery-bind', 'owner-data'),
    ('producer-policy', 'owner-data'),
    ('scoped-producer-policy', 'owner-data'),
    ('root-owner-plan', 'owner-data'),
    ('startup-descriptor', 'startup-descriptor'),
    ('custody-genesis', 'custody-genesis'),
    ('original-bootstrap-owner', 'owner-entry'),
    ('original-operation-head-owner', 'owner-entry'),
    ('original-custody-owner', 'owner-entry'),
)
DEPENDENCIES = {
    'issuer': {'universe': 'universe'},
    'scoped-ledgers': {'historical': 'historical-ledger', 'gate': 'original-gate'},
    'launch-ledger': {'historical': 'historical-ledger', 'gate': 'original-gate', 'store': 'worldline-store'},
    'owner-genesis': {'historical': 'historical-ledger', 'gate': 'original-gate'},
    'operation-owner-genesis': {'historical': 'historical-ledger', 'gate': 'original-gate', 'owner': 'owner-genesis'},
    'custody-genesis': {'gate': 'original-gate'},
    'original-supervisor-stop': {'supervisor': 'original-supervisor'},
}


def bind(owner_inputs):
    if set(owner_inputs) != {name for name, _ in TOPOLOGY}:
        raise RuntimeError('ORIGINAL_COMPLETE_OWNER_CONSTRUCTION_TOPOLOGY_REQUIRED')
    actions = []
    for name, kind in TOPOLOGY:
        selected = owner_inputs[name]
        if 'kind' in selected or 'name' in selected:
            raise RuntimeError('ORIGINAL_CREATOR_ID_AND_KIND_ARE_COMMITTED_SOURCE')
        for key, expected in DEPENDENCIES.get(name, {}).items():
            if selected.get(key) != expected:
                raise RuntimeError('ORIGINAL_CREATOR_ACTUAL_RESULT_DEPENDENCY_CHANGED_' + name)
        actions.append(dict(selected, name=name, kind=kind))
    return actions
