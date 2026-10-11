"""Selected original composed Ledger creation, inside original gate-config action.

This helper is not an authority implementation. It derives exactly the original
bind_gate.py resource configuration from authentic creator outputs, invokes the
selected original Ledger initializer, and retains its actual replay readback.
No service process, socket, reservation, capability or successful verdict is
supplied here. The original Gate and native library keep all later decisions.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

_lease = getattr(sys, '_worldline_approved_source_loader', None)
if _lease is None:
    raise RuntimeError('ORIGINAL_COMPOSED_LEDGER_APPROVED_SOURCE_LEASE_REQUIRED')
_lease.check()


def initialize(builder, action, binding, gate_config):
    require = builder.require
    require(set(binding) == {'kind', 'source', 'root', 'universe', 'gate_source',
                             'library', 'field'} and
            binding['kind'] == 'original-composed-ledger' and
            binding['field'] == ['resource_config_sha256'] and
            action['name'] == 'gate-config' and
            action['path'] == 'authority/gate/config.json',
            'FIXTURE_ORIGINAL_COMPOSED_LEDGER_BINDING_SHAPE')
    root = builder.target(binding['root'])
    require(root == builder.root / 'authority/resource' and
            Path(binding['source']) == root / 'service.py' and
            Path(binding['library']) == root / 'libcosmogony_core.so' and
            Path(binding['gate_source']) == builder.root / 'install/intent_gate.py',
            'FIXTURE_ORIGINAL_COMPOSED_LEDGER_SOURCE_PATHS')
    builder.protected(root, True)
    builder.protected(root / 'state', True)
    library_raw = builder.selected(binding['library'])
    library_sha = hashlib.sha256(library_raw).hexdigest()
    inventory = builder.exact(builder.protected(builder.root / 'install/source-inventory.json').read_bytes())
    require(inventory['universe_source/lib/libcosmogony_core.so'] == library_sha and
            inventory['resource_source/resource_lab/service.py'] ==
                hashlib.sha256(builder.selected(binding['source'], ('SOURCE', 'ENTRY'))).hexdigest() and
            inventory['intent_gate.py'] ==
                hashlib.sha256(builder.selected(binding['gate_source'], ('SOURCE', 'ENTRY'))).hexdigest(),
            'FIXTURE_ORIGINAL_COMPOSED_LEDGER_FULL_INSTALLED_CORRESPONDENCE')
    universe_action = next(item for item in builder.plan['owner_actions']
                           if item['name'] == binding['universe'])
    require(universe_action['kind'] == 'universe', 'FIXTURE_ORIGINAL_COMPOSED_UNIVERSE_CREATOR_REQUIRED')
    universe = builder.results[binding['universe']]
    genesis = universe.get('managed_genesis')
    if genesis is None:
        genesis = builder.data(universe_action['genesis'])
    require(gate_config['fact_scope'] == 'BROKER_AND_PROTECTED_UNIVERSE' and
            gate_config['universe_id'] == universe['activated']['universe_id'] and
            gate_config['universe_genesis_sha256'] == universe['genesis_sha256'] and
            gate_config['resource_config_sha256'] is None,
            'FIXTURE_ORIGINAL_COMPOSED_LEDGER_ACTUAL_UNIVERSE_BINDING')
    gate = builder.module('intent_gate', binding['gate_source'])
    service = builder.module('service', binding['source'])
    config = {'universe_id': universe['activated']['universe_id'],
              'policy_epoch': gate_config['policy_epoch'], 'principal_uid': 0,
              'limits': gate.ledger_limits(genesis), 'native_sha256': library_sha}
    raw = service.canonical(config)
    # Original bind_gate.py creates precisely these canonical bytes exclusively
    # before the authentic original Ledger --init constructor/initializer.
    path = root / 'config.json'
    builder.create(path, raw)
    ledger = service.Ledger(root)
    ledger.initialize()
    readback = ledger.audit()
    require(builder.protected(path).read_bytes() == raw and
            readback['policy_digest'] == hashlib.sha256(raw).hexdigest(),
            'FIXTURE_ORIGINAL_COMPOSED_LEDGER_DURABLE_READBACK_CHANGED')
    builder.objects['original-composed-resource-ledger'] = ledger
    return {'source': binding['source'], 'native_sha256': library_sha,
            'config_path': str(path), 'config_hex': raw.hex(),
            'config_sha256': hashlib.sha256(raw).hexdigest(),
            'original_initializer': 'Ledger.initialize', 'actual_audit': readback,
            'files': {str(p): {'sha256': hashlib.sha256(builder.protected(p).read_bytes()).hexdigest()}
                      for p in (ledger.db_path, ledger.ready_path)},
            'request_socket_started': False, 'phase_acceptance': False}
