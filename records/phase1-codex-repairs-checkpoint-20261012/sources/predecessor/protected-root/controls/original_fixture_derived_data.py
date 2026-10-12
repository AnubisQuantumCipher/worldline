"""Explicit offline owner bindings for the original unchanged creator order.

All values here are owner declarations or actual original creator readbacks.
No function supplies a native outcome, operation permission or runtime startup
waiver. The operator-selected early source closure and genuine installation,
full proof, native admission and original complete controls remain required.
"""
from __future__ import annotations
import sys
_approved = sys.modules.get('_worldline_approved_source_loader')
if _approved is None:
    raise SystemExit('FIXTURE_DERIVED_DATA_EARLY_APPROVED_SOURCE_REQUIRED')
_lease = _approved.current()
if type(_lease) is not _approved.ApprovedSourceLease:
    raise SystemExit('FIXTURE_DERIVED_DATA_ACTUAL_EARLY_LEASE_REQUIRED')
_lease.check()
import hashlib
import json
from pathlib import Path


def selected_source_inventory(builder, binding):
    builder.require(type(binding) is dict and set(binding) == {'kind','field'}
        and binding['kind'] == 'original-selected-source-inventory'
        and binding['field'] == ['sources'],
        'FIXTURE_ACTUAL_COMPLETE_SELECTED_SOURCE_BINDING_REQUIRED')
    _lease.check()
    value = {path:builder.sha(_lease.file(path,(record[0],)))
        for path,record in _lease.files.items() if record[0] in ('SOURCE','ENTRY')}
    builder.require(value, 'FIXTURE_COMPLETE_SELECTED_SOURCE_INVENTORY_ABSENT')
    _lease.check()
    return value


def launch(builder, action, module, cfg):
    require = builder.require
    spec = action['owner_binding']
    require(type(spec) is dict and set(spec) == {'gate','historical','startup_template'}
            and spec['gate'] == 'original-gate' and spec['historical'] == 'historical-ledger'
            and action['gate'] == spec['gate'] and action['historical'] == spec['historical'],
            'FIXTURE_LAUNCH_EXACT_ORIGINAL_OWNER_BINDING_REQUIRED')
    gate, historical = builder.objects[spec['gate']], builder.objects[spec['historical']]
    startup = builder.data(spec['startup_template'])
    require(startup['schema'] == 'worldline.protected-startup-v1'
            and startup['installation_id'] == cfg['installation_id'],
            'FIXTURE_LAUNCH_SAME_ORIGINAL_STARTUP_POLICY_REQUIRED')
    complete = dict(cfg)
    complete['startup_policy_sha256'] = module.digest(module.canonical(module.startup_policy(startup)))
    complete['gate_config_sha256'] = module.digest(gate.config_raw)
    complete['native_sha256'] = module.digest(builder.selected(startup['runtime']['native_library'], ('DATA',)))
    complete['helper_sha256'] = module.digest(builder.selected(complete['helper'], ('EXECUTABLE','SOURCE')))
    complete['source_sha256'] = module.digest(builder.selected(action['source'], ('SOURCE',)))
    scope = module.dto_record(historical.genesis.scope)
    require(type(complete['costs']) is dict and complete['costs'], 'FIXTURE_LAUNCH_COMPLETE_COST_POLICY_REQUIRED')
    costs = {}
    for key, cost in complete['costs'].items():
        require(type(cost) is dict and set(cost) == {'schema','kind','amount','scope'}
                and cost['schema'] == 'worldline.protected-resource-cost-v1'
                and cost['kind'] in ('HELD_CAPACITY','IRREVERSIBLE_BUDGET')
                and type(cost['amount']) is int,
                'FIXTURE_LAUNCH_ORIGINAL_FULL_COST_DATUM_REQUIRED')
        costs[key] = dict(cost, scope=scope)
    complete['costs'] = costs
    require(type(complete['launch_genesis']) is dict and set(complete['launch_genesis']) ==
            {'schema','binding','store_genesis','issuer_head','resource_genesis','event_head'},
            'FIXTURE_LAUNCH_ORIGINAL_FULL_GENESIS_FIELDS_REQUIRED')
    source = {'policy': {key:value for key,value in complete.items() if key != 'launch_genesis'},
        'historical_genesis': module.dto_record(historical.genesis), 'gate_sha256': module.digest(gate.config_raw),
        'issuer_head': gate.issuer.head(), 'store_genesis': builder.results[action['store']]['store_identity']}
    event_head = module.digest(b'WORLDLINE-new-owner-launch-genesis-v1\0' + module.canonical(source))
    complete['launch_genesis'] = dict(complete['launch_genesis'], event_head=event_head)
    return complete, {'classification':'NEW_ORIGINAL_OWNER_DATA_NOT_LAUNCH_OR_NATIVE_AUTHORIZATION',
        'actual_source_binding':source, 'startup_policy':module.startup_policy(startup),
        'actual_launch_or_native':None}


def operation_policy(builder, action, binding, policy):
    require = builder.require
    require(action['name'] == 'operation-policy' and binding['field'] == ['selection']
            and type(binding) is dict and set(binding) == {'kind','gate','store','grants','field'}
            and binding['gate'] == 'original-gate' and binding['store'] == 'worldline-store',
            'FIXTURE_OPERATION_EXACT_ORIGINAL_OWNER_BINDING_REQUIRED')
    stopped = builder.results['original-supervisor-stop']
    require(stopped['actual_wait'] == 0
            and builder.supervisors['original-supervisor'][0].poll() == stopped['actual_wait'],
            'FIXTURE_OPERATION_ACTUAL_STOPPED_SUPERVISOR_REQUIRED')
    store_action = builder.plan['owner_inputs'][binding['store']]
    builder.module('worldline.store', store_action['source'])
    from worldline.paths import WorldlinePaths
    from worldline.core import Core, hash_bytes_from_id
    from worldline.store import StateStore, CHAIN_GENESIS
    from worldline.protected_startup import store_snapshot
    from worldline.protected_operations import quantity
    from worldline.operation_authority_kernel import OPS
    paths = WorldlinePaths(**{key: builder.target(value) for key,value in store_action['paths'].items()})
    gate = builder.objects[binding['gate']]
    universe, issuer_head = gate.universe.read(), gate.issuer.head()
    managed = gate.config['managed_observation']
    require(managed == builder.results['original-supervisor']['managed_observation']['observation'],
            'FIXTURE_OPERATION_GENUINE_SEALED_MANAGED_BINDING_REQUIRED')
    before = store_snapshot(paths.database)
    store = StateStore(paths, Core(Path(store_action['library'])))
    try:
        require(store.get_meta('protectedStoreGenesis') == builder.results[binding['store']]['store_identity']
                and not store.get_meta('dirty', False)
                and not any(job['state'] in {'STARTING','RUNNING','FINALIZING'} for job in store.jobs()),
                'FIXTURE_OPERATION_GENUINE_QUIESCENT_STORE_REQUIRED')
        store.verify_chains()
        material = {}
        for table,kind in (('causal_events','events'),('receipts','receipts')):
            with store._lock:
                rows = store._connection.execute('SELECT * FROM '+table+' ORDER BY rowid').fetchall()
            material[kind] = [(dict(row), store.read_canonical(kind,row['canonical_path'],chain_hash=row['chain_hash']))
                              for row in rows]
        from worldline.root_worker_codec import archive
        source = {'installation':policy['installation'], 'actual_store_snapshot':before,
            'actual_full_chain_material_hex':archive(material).hex(), 'universe':universe,
            'issuer_head':issuer_head, 'managed':managed, 'selected_grants':binding['grants']}
        declaration = builder.sha(archive(source))
        chains = {}
        for kind in ('receipts','events'):
            head = CHAIN_GENESIS if not material[kind] else hash_bytes_from_id(material[kind][-1][0]['chain_hash'])
            chains[kind] = {'genesis':CHAIN_GENESIS.hex(), 'head':head.hex()}
        for kind in ('operation_receipts','operation_events'):
            head = builder.sha(b'WORLDLINE-new-owner-operation-chain-v1\0' + kind.encode('ascii') + archive(source))
            chains[kind] = {'genesis':head, 'head':head}
    finally:
        primary = sys.exc_info()[1]
        try:
            store.close()
            require(store_snapshot(paths.database) == before,
                    'FIXTURE_OPERATION_COMPLETE_ORIGINAL_STORE_SOURCE_CHANGED')
        except BaseException as error:
            if primary is None:raise
            primary.add_note('Original operation creator source close/readback failed: '+repr(error))
    require(type(binding['grants']) is list and binding['grants'],
            'FIXTURE_OPERATION_COMPLETE_OWNER_GRANT_DESIGN_REQUIRED')
    grants, selection = [], {}
    for chosen in binding['grants']:
        require(type(chosen) is dict and set(chosen) == {'subject','owner','rights','ceiling','issued_at','expires_at'}
                and type(chosen['subject']) is int and type(chosen['owner']) is int
                and type(chosen['rights']) is dict and set(chosen['rights']) == set(OPS)
                and all(type(value) is bool for value in chosen['rights'].values()),
                'FIXTURE_OPERATION_FULL_ORIGINAL_ORDERED_RIGHTS_DATUM_REQUIRED')
        grant_id = builder.sha(b'WORLDLINE-new-owner-operation-grant-v1\0' + archive({'source':source,'grant':chosen}))
        grant = {'id':grant_id,'parent':None,'issuer':gate.issuer.policy['issuer_id'],
            'instance':managed['worldline_instance_id'],'root_set':managed['root_set_id'],
            'policy':gate.config['policy_id'],'subject':chosen['subject'],'owner':chosen['owner'],
            'allowed':[chosen['rights'][name] for name in OPS], 'state':'ACTIVE',
            'epoch':quantity(universe['record']['policy_epoch']), 'ceiling':quantity(chosen['ceiling']),
            'issued_at':quantity(chosen['issued_at']), 'expires_at':quantity(chosen['expires_at'])}
        grants.append(grant)
        require(str(chosen['subject']) not in selection,
                'FIXTURE_OPERATION_EXPLICIT_SINGLE_CANDIDATE_SELECTION_REQUIRED')
        selection[str(chosen['subject'])] = {name:grant_id for name in OPS}
    policy['issuer'] = gate.issuer.policy['issuer_id']
    policy['genesis'] = declaration
    policy['chains'] = chains
    body = {'schema':'worldline.canonical-operation-journal-v1','binding':None,
            'grants':grants,'events':[],'chains':chains}
    return selection, {'classification':'NEW_SIGNED_OWNER_DESIGN_NOT_OPERATION_AUTHORIZATION',
        'actual_source_binding':source,'full_initial_body':body,'native_grant_or_operation_outcome':None}


def operation_initial_body(builder, action, original):
    require = builder.require
    require(action['owner_binding'] == {'policy':'operation-policy'},
            'FIXTURE_OPERATION_INITIAL_BODY_EXACT_PRIOR_CREATOR_REQUIRED')
    require(type(original) is dict and set(original) == {'schema','binding','grants','events','chains'}
            and original['schema'] == 'worldline.canonical-operation-journal-v1' and original['events'] == [],
            'FIXTURE_OPERATION_ORIGINAL_FULL_INITIAL_TEMPLATE_REQUIRED')
    fact = builder.results['operation-policy']['original_derived_owner_data']['full_initial_body']
    policy_raw = builder.protected(builder.target(builder.plan['owner_inputs']['operation-policy']['path'])).read_bytes()
    require(builder.sha(policy_raw) == builder.results['operation-policy']['sha256'],
            'FIXTURE_OPERATION_PRIOR_ACTUAL_POLICY_OUTPUT_CHANGED')
    policy = builder.exact(policy_raw)
    require(policy['chains'] == fact['chains'] and fact['events'] == [],
            'FIXTURE_OPERATION_COMPLETE_INITIAL_OWNER_CHAIN_CORRESPONDENCE_REQUIRED')
    return fact


def offline_operation_descriptor(builder, action, full):
    require = builder.require
    spec = action['offline_operation_descriptor']
    require(type(spec) is dict and set(spec) == {'path','plan'} and spec['plan'] == 'root-owner-plan'
            and full['root_worker'] == {'owner_plan':str(builder.target(builder.plan['owner_inputs'][spec['plan']]['path']))},
            'FIXTURE_OFFLINE_OPERATION_DESCRIPTOR_SAME_FINAL_FULL_PLAN_REQUIRED')
    plan = builder.exact(builder.protected(builder.target(builder.plan['owner_inputs'][spec['plan']]['path'])).read_bytes())
    omitted = {plan['handoff_journal'],plan['handoff_genesis'],plan['handoff_journal']+'.lock'}
    require(omitted <= set(full['provisioned_state']),
            'FIXTURE_OFFLINE_OPERATION_DESCRIPTOR_FINAL_CUSTODY_ROSTER_REQUIRED')
    # Original StartupLease explicitly permits its base schema without the
    # optional root_worker member. Only the genuine offline head utility gets
    # this distinct new descriptor; final runtime keeps the complete full one.
    variant = {name:value for name,value in full.items() if name != 'root_worker'}
    variant['provisioned_state'] = [path for path in full['provisioned_state'] if path not in omitted]
    raw = builder.canonical(variant)
    path = builder.target(spec['path'])
    builder.create(path, raw)
    require(builder.protected(path).read_bytes() == raw,
            'FIXTURE_OFFLINE_OPERATION_DESCRIPTOR_ACTUAL_EXCLUSIVE_READBACK_CHANGED')
    return {'path':str(path),'sha256':builder.sha(raw),'descriptor':variant,
        'original_full_descriptor_preserved':True,'omitted_future_custody_paths':sorted(omitted),
        'scope':'ORIGINAL_OFFLINE_OPERATION_HEAD_UTILITY_ONLY_NOT_RUNTIME_STARTUP_OR_OPERATION_PERMISSION'}
