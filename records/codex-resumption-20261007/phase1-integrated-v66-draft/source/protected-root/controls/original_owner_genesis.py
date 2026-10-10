"""Original explicit offline owner declarations from genuine creator facts.

These are signed original owner declarations, not captured native decisions or
permission DTOs. Ordinary constructors/native grant checks still authenticate and
replay them. No files are written here; the explicit exclusive fixture builder
owns creation and readback. All original event/grant bodies are retained.
"""
from __future__ import annotations
import hashlib
import hmac


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def envelope(body, key, domain, canonical, suffix=b''):
    return {'body': body, 'mac': hmac.new(key, domain + suffix + canonical(body), 'sha256').hexdigest()}


def launch(module, cfg, gate, historical, store_identity, issuer_head):
    policy = {name: value for name, value in cfg.items() if name != 'launch_genesis'}
    binding = {'installation_id': cfg['installation_id'],
        'producer_policy_sha256': digest(module.canonical(policy)),
        'resource_config_sha256': historical.config_sha,
        'gate_config_sha256': digest(gate.config_raw), 'helper_sha256': cfg['helper_sha256'],
        'issuer_policy_sha256': gate.issuer.policy_sha256, 'issuer_key_sha256': digest(gate.issuer.key)}
    genesis = dict(cfg['launch_genesis'], binding=binding, store_genesis=store_identity,
        issuer_head=issuer_head, resource_genesis=module.dto_record(historical.genesis))
    complete = dict(cfg, launch_genesis=genesis)
    anchor = {'binding': binding, 'genesis': genesis, 'head': genesis['event_head']}
    mac = hmac.new(gate.issuer.key, module.DOMAIN + b'head\0' + module.canonical(anchor), 'sha256').hexdigest()
    return complete, binding, mac


def owner(module, policy_raw, policy, gate, installation_genesis_raw, installation_genesis,
          resource_genesis):
    binding = {key: policy[key] for key in ('installation_id', 'owner_issuer_id', 'owner_uid',
        'gate_config_sha256', 'issuer_policy_sha256', 'issuer_key_sha256', 'store_genesis', 'native_sha256')}
    binding['policy_sha256'] = digest(policy_raw)
    canonical = module.canonical; key = gate.issuer.key
    journal_body = {'schema': 'worldline.protected-owner-journal-v1', 'binding': binding, 'events': []}
    journal = canonical(envelope(journal_body, key, module.DOMAIN, canonical)) + b'\n'
    head_body = {'schema': 'worldline.protected-owner-head-v1', 'binding': binding,
                 'event_head': 'GENESIS', 'journal_sha256': digest(journal)}
    head = canonical(envelope(head_body, key, module.DOMAIN, canonical)) + b'\n'
    body = {'schema': 'worldline.protected-owner-genesis-v1', 'binding': binding,
        'installation_genesis_sha256': digest(installation_genesis_raw),
        'gate_head': installation_genesis['gate_head'], 'issuer_head': installation_genesis['issuer_head'],
        'store_head': installation_genesis['store']['initial_head'], 'resource_genesis': resource_genesis,
        'journal_sha256': digest(journal), 'head_sha256': digest(head)}
    genesis = canonical(envelope(body, key, module.DOMAIN, canonical, b'genesis\0')) + b'\n'
    admission = {'schema': 'worldline.owner-bootstrap-admission-v1', 'genesis_sha256': digest(genesis),
        'binding': binding, 'state': 'CONSUMED', 'events': [{'cause': 'OWNER_GENESIS_PROVISIONED',
        'genesis_sha256': digest(genesis), 'journal_sha256': digest(journal), 'head_sha256': digest(head)}]}
    bootstrap = canonical(envelope(admission, key, module.DOMAIN, canonical, b'bootstrap\0')) + b'\n'
    return {'binding': binding, 'journal': journal, 'head': head, 'genesis': genesis, 'bootstrap': bootstrap}


def operation(module, policy_raw, policy, gate, installation_genesis_raw, installation_genesis,
              owner_binding, historical, original_prefix, original_initial_body):
    # The entire original owner-selected grant roster/chains is preserved,
    # never replaced by a smaller test grant or an invented successful report.
    expected = {'schema', 'binding', 'grants', 'events', 'chains'}
    from worldline.resource_run_ledger import dto_record
    if set(original_initial_body) != expected or original_initial_body['events']:
        raise RuntimeError('FIXTURE_OPERATION_GENUINE_INITIAL_OWNER_BODY_REQUIRED')
    binding = {'installation': installation_genesis['installation_id'], 'genesis': policy['genesis'],
        'policy_bytes': policy_raw.hex(), 'issuer_key': digest(gate.issuer.key), 'store_genesis': policy['store_genesis']}
    initial_body = dict(original_initial_body, binding=binding)
    initial = envelope(initial_body, gate.issuer.key, module.DOMAIN, module.canonical)
    journal = module.canonical(initial) + b'\n'
    body = {'schema': 'worldline.operation-owner-genesis-v1',
        'installation': installation_genesis['installation_id'], 'installation_genesis': digest(installation_genesis_raw),
        'binding': binding, 'gate_head': installation_genesis['gate_head'], 'issuer_head': installation_genesis['issuer_head'],
        'universe': {'genesis_sha256': gate.universe.genesis_sha256}, 'store': installation_genesis['store'],
        'resource': {'genesis': dto_record(historical.genesis), 'events': original_prefix['events']},
        'owner': owner_binding, 'initial_envelope': initial}
    owner = module.canonical(envelope(body, gate.issuer.key, module.DOMAIN, module.canonical, b'owner-genesis\0')) + b'\n'
    return {'binding': binding, 'journal': journal, 'owner_genesis': owner, 'initial_envelope': initial}
