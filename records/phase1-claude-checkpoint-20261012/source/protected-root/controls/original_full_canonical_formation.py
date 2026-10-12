"""Exclusive new owner formation from the complete actual original PRIME.

This selected offline creator copies actual full manifests, preserving their
byte paths, metadata, ACL and repository semantics. It does not dispatch an
operation, supply a native decision or reconstruct missing historical state.
The original later StartupLease/operation principal and full native broker
still authenticate all declarations and independently observed physical facts.
"""
from __future__ import annotations
import sys
_approved = sys.modules.get('_worldline_approved_source_loader')
if _approved is None:
    raise SystemExit('FIXTURE_FULL_CANONICAL_EARLY_APPROVED_SOURCE_REQUIRED')
_lease = _approved.current()
if type(_lease) is not _approved.ApprovedSourceLease:
    raise SystemExit('FIXTURE_FULL_CANONICAL_ACTUAL_EARLY_LEASE_REQUIRED')
_lease.check()
import hashlib
import hmac
import os
from pathlib import Path


def initialize(builder, action, owner_result):
    spec = action['full_canonical']
    require = builder.require
    require(action['name'] == 'owner-genesis' and action['kind'] == 'owner-genesis'
            and type(spec) is dict and set(spec) == {'store', 'source', 'transaction_source', 'root'}
            and spec['store'] == 'worldline-store' and spec['root'] == 'canonical',
            'FIXTURE_FULL_CANONICAL_EXACT_OWNER_CREATOR_REQUIRED')
    stopped = builder.results['original-supervisor-stop']
    require(stopped['actual_wait'] == 0
            and builder.supervisors['original-supervisor'][0].poll() == stopped['actual_wait'],
            'FIXTURE_FULL_CANONICAL_ACTUAL_STOPPED_SUPERVISOR_REQUIRED')
    store_action = builder.plan['owner_inputs'][spec['store']]
    builder.module('worldline.store', store_action['source'])
    full_module = builder.module('worldline.canonical_full_store', spec['source'])
    transaction_module = builder.module('worldline.transaction', spec['transaction_source'])
    from worldline.paths import WorldlinePaths
    from worldline.core import Core
    from worldline.store import StateStore
    from worldline.manifest import Manifest
    from worldline.protected_startup import store_snapshot
    from original_managed_formation import mapping
    paths = WorldlinePaths(**{key: builder.target(value) for key, value in store_action['paths'].items()})
    core = Core(Path(store_action['library']))
    root = builder.target(spec['root'])
    builder.protected(root, True)
    gate = builder.objects[action['gate']]
    gate.issuer.head()
    owner_raw = builder.protected(builder.target(action['genesis'])).read_bytes()
    require(builder.exact(owner_raw)['body']['binding'] == owner_result['binding'],
            'FIXTURE_FULL_CANONICAL_ACTUAL_OWNER_GENESIS_CHANGED')
    before = store_snapshot(paths.database)
    store = StateStore(paths, core)
    try:
        require(store.get_meta('protectedStoreGenesis') == builder.results[spec['store']]['store_identity']
                and not store.get_meta('dirty', False)
                and not any(job['state'] in {'STARTING', 'RUNNING', 'FINALIZING'} for job in store.jobs()),
                'FIXTURE_FULL_CANONICAL_QUIESCENT_ACTUAL_STORE_REQUIRED')
        prime = store.prime()
        require(prime is not None and prime.content_id is not None,
                'FIXTURE_FULL_CANONICAL_GENUINE_PRIME_REQUIRED')
        roots = store.roots()
        require(roots and len({row['root_key'] for row in roots}) == len(roots),
                'FIXTURE_FULL_CANONICAL_COMPLETE_ACTUAL_ROOT_ROSTER_REQUIRED')
        original_mappings = dict(builder.managed_links)
        transaction = transaction_module.CollapseTransaction(paths, store, core=core)
        data, transactions, staging = (root / name for name in ('full-data', 'full-transactions', 'full-staging'))
        payload, live = data / 'payload', data / 'live'
        for directory in (data, transactions, staging, payload, live):
            require(not os.path.lexists(directory), 'FIXTURE_FULL_CANONICAL_NEW_DIRECTORY_REQUIRED')
            builder.protected(directory.parent, True)
            directory.mkdir(mode=0o700)
            builder.sync(directory.parent)
        manifests, rows, links = [], [], {}
        for registered in roots:
            source = Path(os.fsdecode(paths.root_source(registered)))
            builder.protected(source, True)
            manifest = transaction._capture_payload(source=os.fsencode(source),
                logical=bytes(registered['path']), root=registered)
            destination = payload / registered['root_key']
            # Original full materialization verifies complete destination bytes
            # and metadata. No bounded mission projection substitutes for it.
            copied = Manifest.materialize(manifest, source, destination, core=core)
            require(copied.canonical == manifest.canonical and copied.root_hash == manifest.root_hash,
                    'FIXTURE_FULL_CANONICAL_COMPLETE_MANIFEST_COPY_CHANGED')
            transaction._fsync_payload_tree(destination)
            link = live / registered['root_key']
            os.symlink(os.fsencode(destination), os.fsencode(link))
            fact = mapping(link, destination, destination, builder.root)
            fact['role'] = 'full-canonical-live-mapping'
            # Enroll only this actual newly created mapping. A later failure
            # retains its real custody; it never supplies a success verdict.
            builder.managed_links[str(link)] = fact
            links[str(link)] = fact
            manifests.append(manifest)
            rows.append({'root_key': registered['root_key'], 'logical_path_hex': bytes(registered['path']).hex(),
                'kind': registered['kind'], 'source': str(source), 'destination': str(destination),
                'manifest_raw_hex': manifest.canonical.hex(), 'manifest_root': manifest.root_hash,
                'mapping': fact})
        actual_root = Manifest.root_set_hash(manifests, core)
        require(actual_root == prime.base_root,
                'FIXTURE_FULL_CANONICAL_ACTUAL_PRIME_ROOT_CORRESPONDENCE_CHANGED')
        for directory in (live, payload, data, transactions, staging, root):
            builder.sync(directory)
        # Observe source/store/PRIME again before writing the explicit original
        # owner declaration; no offline status supplies operation authority.
        for row, registered, manifest in zip(rows, roots, manifests, strict=True):
            source = os.fsencode(row['source'])
            require(transaction._capture_payload(source=source, logical=bytes(registered['path']),
                    root=registered).canonical == manifest.canonical,
                    'FIXTURE_FULL_CANONICAL_ORIGINAL_SOURCE_CHANGED')
        require(store.prime().record() == prime.record() and store.roots() == roots,
                'FIXTURE_FULL_CANONICAL_ACTUAL_ORIGINAL_PRIME_CHANGED')
        for name, fact in original_mappings.items():
            actual = mapping(name, fact['target'], fact['backing'], builder.root)
            actual['role'] = fact['role']
            require(actual == fact, 'FIXTURE_FULL_CANONICAL_ORIGINAL_MAPPING_CHANGED')
        history = {'cause': 'OWNER_FULL_CANONICAL_FORMATION', 'original_owner_genesis_sha256': hashlib.sha256(owner_raw).hexdigest(),
            'original_prime': prime.record(), 'actual_root_set': actual_root, 'complete_roots': rows}
        genesis = hashlib.sha256(full_module.DOMAIN + b'owner-formation\0' + full_module.canonical(history)).hexdigest()
        policy = {'schema': 'worldline.full-canonical-policy-v1', 'installation': owner_result['binding']['installation_id'],
            'store_genesis': store.get_meta('protectedStoreGenesis'), 'universe_genesis': gate.universe.genesis_sha256,
            'genesis': genesis, 'source_inventory': {name: value for name, value in
                builder.exact(builder.protected(builder.target(action['policy'])).read_bytes())['sources'].items()},
            'data': str(data), 'transactions': str(transactions), 'staging': str(staging)}
        body = {'schema': 'worldline.full-canonical-state-v1', 'installation': policy['installation'],
            'genesis': genesis, 'worldline_store': policy['store_genesis'],
            'universe_genesis': policy['universe_genesis'], 'history': [history]}
        state = {'body': body, 'mac': hmac.new(gate.issuer.key,
            full_module.DOMAIN + full_module.canonical(body), 'sha256').hexdigest()}
        outputs = {}
        for name, value in (('full-domain-policy.json', policy), ('full-domain-state.json', state)):
            path = root / name
            raw = full_module.canonical(value)
            builder.create(path, raw)
            require(builder.exact(builder.protected(path).read_bytes()) == value,
                    'FIXTURE_FULL_CANONICAL_ACTUAL_OWNER_DECLARATION_READBACK_CHANGED')
            outputs[name] = {'path': str(path), 'sha256': hashlib.sha256(raw).hexdigest(), 'raw_hex': raw.hex()}
        _lease.check()
        return {'classification': 'ACTUAL_EXCLUSIVE_OFFLINE_OWNER_FORMATION_NOT_OPERATION_AUTHORIZATION',
            'artifacts': outputs, 'mappings': links, 'owner_history': history,
            'original_full_manifest_root': actual_root, 'original_later_startup_and_native_acceptance': False}
    finally:
        primary = sys.exc_info()[1]
        failures = []
        try:
            store.close()
        except BaseException as failure:
            failures.append(failure)
        try:
            require(store_snapshot(paths.database) == before,
                    'FIXTURE_FULL_CANONICAL_ORIGINAL_STORE_CHANGED_DURING_CREATION')
        except BaseException as failure:
            failures.append(failure)
        if failures:
            if primary is not None:
                for failure in failures:
                    primary.add_note('Full canonical owner close/readback failed: ' + repr(failure))
            else:
                for failure in failures[1:]:
                    failures[0].add_note('Additional full canonical owner close/readback failure: ' + repr(failure))
                raise failures[0]
