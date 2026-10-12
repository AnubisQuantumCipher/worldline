"""Exclusive new resource owner DATA from genuine original creator facts.

This factory does not authorize a reservation, grant, physical capacity or
launch. Complete original DTOs describe an explicitly selected new owner
genesis. Existing native/principal/current-source checks remain mandatory.
"""
from __future__ import annotations
import sys
_approved = sys.modules.get('_worldline_approved_source_loader')
if _approved is None:
    raise SystemExit('FIXTURE_RESOURCE_DATA_EARLY_APPROVED_SOURCE_REQUIRED')
_lease = _approved.current()
if type(_lease) is not _approved.ApprovedSourceLease:
    raise SystemExit('FIXTURE_RESOURCE_DATA_ACTUAL_EARLY_LEASE_REQUIRED')
_lease.check()
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import uuid


def context(builder, binding):
    require = builder.require
    require(binding['store'] == 'worldline-store' and binding['gate'] == 'original-gate',
            'FIXTURE_RESOURCE_DATA_ORIGINAL_CREATORS_REQUIRED')
    store_action = builder.plan['owner_inputs'][binding['store']]
    store_module = builder.module('worldline.store', store_action['source'])
    from worldline.paths import WorldlinePaths
    from worldline.protected_startup import store_snapshot
    from worldline.protected_resource_runtime import kernel_bytes, lossless_data
    from worldline.resource_run_ledger import RunContext
    paths = WorldlinePaths(**{key: builder.target(value) for key, value in store_action['paths'].items()})
    gate = builder.objects[binding['gate']]
    gate.issuer.head()
    universe = gate.universe.read()
    actual = builder.results['original-supervisor']['managed_observation']
    observation = actual['observation']
    require(gate.config['managed_observation'] == observation
            and gate.config['daemon_endpoint_generation'] == actual['daemon_endpoint_generation'],
            'FIXTURE_RESOURCE_DATA_GENUINE_SEALED_OBSERVATION_REQUIRED')
    builder.protected(paths.database)
    before = store_snapshot(paths.database)
    db = sqlite3.connect(paths.database.as_uri() + '?mode=ro', uri=True, isolation_level=None)
    db.row_factory = sqlite3.Row
    try:
        db.execute('PRAGMA query_only=ON')
        db.execute('BEGIN')
        require(db.execute('PRAGMA quick_check').fetchall()[0][0] == 'ok',
                'FIXTURE_RESOURCE_DATA_ORIGINAL_STORE_CORRUPT')
        def meta(name):
            rows = db.execute('SELECT value FROM meta WHERE key=?', (name,)).fetchall()
            require(len(rows) == 1, 'FIXTURE_RESOURCE_DATA_ORIGINAL_META_REQUIRED')
            return json.loads(bytes(rows[0][0]))
        genesis, store_id = meta('protectedStoreGenesis'), meta('finalizationStoreId')
        require(genesis == builder.results[binding['store']]['store_identity']
                and type(genesis) is str and genesis and type(store_id) is str and store_id
                and meta('dirty') is False,
                'FIXTURE_RESOURCE_DATA_GENUINE_QUIESCENT_STORE_REQUIRED')
        require(not db.execute("SELECT * FROM jobs WHERE state IN ('STARTING','RUNNING','FINALIZING')").fetchall(),
                'FIXTURE_RESOURCE_DATA_ACTIVE_ORIGINAL_JOB_REFUSED')
        roots = [dict(row) for row in db.execute('SELECT * FROM roots ORDER BY primary_root DESC, path')]
        prime_id = meta('primeInstance')
        worlds = db.execute('SELECT * FROM worlds WHERE instance_id=?', (prime_id,)).fetchall()
        require(len(worlds) == 1 and roots,
                'FIXTURE_RESOURCE_DATA_ACTUAL_NONEMPTY_PRIME_REQUIRED')
        prime = store_module.StateStore._world_from_row(worlds[0])
        prime_record = prime.record()
        actual_uuid = uuid.UUID(prime.instance_id)
        require(str(actual_uuid) == prime.instance_id, 'FIXTURE_RESOURCE_DATA_ACTUAL_PRIME_UUID_INVALID')
        instance = hashlib.sha256(b'COSMOGONY-worldline-instance-v1\0' + actual_uuid.bytes).hexdigest()
        require(instance == universe['record']['prime_worldline_id']
                and instance == observation['worldline_instance_id'],
                'FIXTURE_RESOURCE_DATA_GENUINE_PRIME_UNIVERSE_CROSSWALK_REQUIRED')
        db.execute('COMMIT')
    finally:
        db.close()
    after = store_snapshot(paths.database)
    require(before == after and gate.universe.read() == universe,
            'FIXTURE_RESOURCE_DATA_COMPLETE_ACTUAL_SOURCE_CHANGED')
    host = kernel_bytes('/etc/machine-id').removesuffix(b'\n')
    boot = kernel_bytes('/proc/sys/kernel/random/boot_id').removesuffix(b'\n')
    require(host and boot and type(binding['unit']) is str and binding['unit'],
            'FIXTURE_RESOURCE_DATA_ACTUAL_HOST_AND_OWNER_UNIT_REQUIRED')
    def identifier(value):
        require(type(value) is str, 'FIXTURE_RESOURCE_DATA_ORIGINAL_ID_TYPE')
        raw = bytes.fromhex(value)
        require(raw and raw.hex() == value, 'FIXTURE_RESOURCE_DATA_ORIGINAL_ID_GRAMMAR')
        return raw
    scope = RunContext(universe=identifier(universe['universe_id']),
        policy=identifier(gate.config['policy_id']), resource=identifier(universe['record']['policy']['resource_id']),
        unit=binding['unit'].encode('utf-8'), instance=identifier(instance), host=host, boot=boot,
        authority=identifier(universe['record']['policy']['authority_id']),
        policy_epoch=universe['record']['policy_epoch'])
    root_raw = builder.canonical(lossless_data({'store_genesis': genesis, 'store_id': store_id,
                                               'roots': roots, 'prime': prime_record}))
    facts = {'classification': 'ACTUAL_CREATOR_SOURCE_FOR_NEW_OWNER_DATA_NOT_NATIVE_AUTHORIZATION',
        'universe': universe, 'gate_config_sha256': builder.sha(gate.config_raw),
        'issuer_head': gate.issuer.head(), 'store_snapshot': before, 'store_genesis': genesis,
        'store_id': store_id, 'roots': lossless_data(roots), 'prime': lossless_data(prime_record),
        'prime_uuid_hex': actual_uuid.bytes.hex(), 'root_source_raw_hex': root_raw.hex(),
        'host_hex': host.hex(), 'boot_hex': boot.hex(), 'selected_unit': binding['unit'],
        'native_decision': None, 'physical_admission': None}
    return scope, facts, actual_uuid.bytes, len(roots), hashlib.sha256(root_raw).digest()


def form(builder, action, binding, value):
    require = builder.require
    require(type(binding) is dict and set(binding) == {'kind','store','gate','unit','capacity','catalogue','field'}
            and binding['kind'] == 'original-resource-owner-data'
            and action['name'] in {'historical-config','scoped-config'}
            and binding['field'] == ['genesis'], 'FIXTURE_RESOURCE_DATA_EXACT_SELECTED_BINDING_REQUIRED')
    require(type(binding['capacity']) is int and binding['capacity'] >= 0,
            'FIXTURE_RESOURCE_DATA_OWNER_CAPACITY_DATUM_REQUIRED')
    from worldline import resource_run_ledger as L
    from worldline import resource_scoped_run_ledger as S
    from worldline.protected_scoped_resource_service import ScopedSnapshot, snapshot_record
    scope, facts, prime, count, root_head = context(builder, binding)
    if action['name'] == 'historical-config':
        require(binding['catalogue'] is None, 'FIXTURE_RESOURCE_DATA_HISTORICAL_CATALOGUE_ABSENT')
        source = builder.canonical(S.record({'facts': facts, 'capacity': binding['capacity']}))
        ledger_head = hashlib.sha256(b'WORLDLINE-new-owner-resource-genesis-v1\0' + source).digest()
        fact = L.dto_record(L.RunState(scope=scope, resource_epoch=0,
            universe_head=bytes.fromhex(facts['universe']['event_head']), ledger_head=ledger_head,
            capacity=binding['capacity'], held_total=0, charged_total=0))
        require(type(L.restore_dto(fact)) is L.RunState,
                'FIXTURE_RESOURCE_DATA_FULL_HISTORICAL_DTO_REQUIRED')
    else:
        prefix = builder.results['historical-ledger']['original_prefix']
        # This optional factory is solely an exclusive NEW empty-prefix owner
        # design. Default and every retained nonempty original prefix remain
        # untouched and must use their complete genuine supplied owner DATA.
        require(prefix['rows'] == [] and prefix['events'] == [] and prefix['state'] == prefix['genesis'],
                'FIXTURE_RESOURCE_DATA_NEW_EMPTY_ORIGINAL_PREFIX_REQUIRED')
        historical = L.restore_dto(prefix['state'])
        require(type(historical) is L.RunState and historical.scope == scope
                and historical.capacity == binding['capacity'],
                'FIXTURE_RESOURCE_DATA_HISTORICAL_FULL_CONTEXT_CHANGED')
        require(type(binding['catalogue']) is list and binding['catalogue'],
                'FIXTURE_RESOURCE_DATA_COMPLETE_OWNER_CATALOGUE_REQUIRED')
        entries = []
        for selected in binding['catalogue']:
            require(type(selected) is dict and set(selected) == {'resource','unit','numerator','denominator',
                    'capacity','costs','role'} and type(selected['resource']) is str and selected['resource']
                    and type(selected['unit']) is str and selected['unit'],
                    'FIXTURE_RESOURCE_DATA_ORIGINAL_CATALOGUE_INPUT_SCHEMA')
            require(all(type(selected[name]) is int for name in ('numerator','denominator','capacity')),
                    'FIXTURE_RESOURCE_DATA_OWNER_QUANTITY_TYPES_REQUIRED')
            capacity_source = hashlib.sha256(builder.canonical(selected)).digest()
            entries.append({'scope_policy': scope.policy, 'scope_resource': scope.resource,
                'scope_unit': scope.unit, 'key': S.PhysicalKey(machine=scope.host,
                    resource=selected['resource'].encode('utf-8'), unit=selected['unit'].encode('utf-8')),
                'numerator': selected['numerator'], 'denominator': selected['denominator'],
                'capacity': selected['capacity'], 'capacity_source': capacity_source,
                'costs': selected['costs'], 'role': selected['role']})
        catalogue = S.record({'schema': 'worldline.protected-physical-catalogue-v1', 'entries': tuple(entries)})
        catalogue_head = hashlib.sha256(builder.canonical(catalogue)).digest()
        source = builder.canonical(S.record({'facts': facts, 'prefix': prefix, 'catalogue': catalogue}))
        owner_declaration = hashlib.sha256(b'WORLDLINE-new-owner-scoped-genesis-v1\0' + source).digest()
        frame_head = hashlib.sha256(b'WORLDLINE-new-owner-scoped-frame-v1\0' + source).digest()
        frame = S.ScopeFrame(scope=scope, first_epoch=historical.resource_epoch,
            universe_head=historical.universe_head, frame_head=frame_head, prior_frame=None,
            store_genesis=facts['store_genesis'].encode('utf-8'), store_id=facts['store_id'].encode('utf-8'),
            root_head=root_head, prime=prime, root_count=count, cause=owner_declaration,
            requester=hashlib.sha256(builder.canonical(binding)).digest(), receipt=owner_declaration,
            catalogue_head=catalogue_head, observation_head=owner_declaration)
        buckets = tuple(S.PhysicalBucket(key=row['key'], capacity=row['capacity'], held_total=0, charged_total=0,
            capacity_source=row['capacity_source'], catalogue_head=catalogue_head,
            observation_head=owner_declaration) for row in entries)
        snapshot = ScopedSnapshot(state=S.ScopedState(current=scope, resource_epoch=historical.resource_epoch,
            universe_head=historical.universe_head, ledger_head=historical.ledger_head,
            history_head=frame_head, physical_head=catalogue_head), history=(frame,), rows=(),
            projection=(), buckets=buckets)
        require('catalogue' in value, 'FIXTURE_RESOURCE_DATA_ORIGINAL_CATALOGUE_FIELD_REQUIRED')
        value['catalogue'] = catalogue
        fact = snapshot_record(snapshot)
    return fact, {'actual_creator_sources': facts,
        'owner_data_classification': 'NEW_EXCLUSIVE_OFFLINE_OWNER_DECLARATION_NOT_NATIVE_OR_OPERATION_VERDICT',
        'full_dto': fact, 'native_admission': None, 'installation_authority': None}
