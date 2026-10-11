"""Explicit offline managed formation and later genuine sealed observations.

No offline snapshot is a daemon seal or authority decision. Original native
RootManager/World transitions create PRIME; original endpoint peer/process/source
checks authenticate the later daemon. Every output below comes from those actual
calls. The caller's existing full offline operator/early-source guard remains
required before this module is imported.
"""
from __future__ import annotations
import sys
_approved = sys.modules.get('_worldline_approved_source_loader')
if _approved is None:
    raise SystemExit('FIXTURE_MANAGED_EARLY_APPROVED_SOURCE_REQUIRED')
_lease = _approved.current()
if type(_lease) is not _approved.ApprovedSourceLease:
    raise SystemExit('FIXTURE_MANAGED_ACTUAL_EARLY_LEASE_REQUIRED')
_lease.check()
import hashlib
import json
import os
from pathlib import Path
import secrets
import socket
import stat
import time


def require(value, reason):
    if not value:
        raise RuntimeError(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode('utf-8')


def inode(info):
    return {'device': info.st_dev, 'inode': info.st_ino, 'mode': info.st_mode,
            'uid': info.st_uid, 'gid': info.st_gid, 'links': info.st_nlink,
            'size': info.st_size, 'mtime_ns': info.st_mtime_ns,
            'ctime_ns': info.st_ctime_ns}


def mapping(path, target, backing, authority_root):
    """Observe only the exact links just produced by original registration."""
    path, target, backing, authority_root = map(Path, (path, target, backing, authority_root))
    require(path.is_relative_to(authority_root) and target.is_relative_to(authority_root)
            and backing.is_relative_to(authority_root), 'FIXTURE_MANAGED_LINK_OUTSIDE_ROOT')
    for directory in (path.parent, target.parent, backing):
        for entry in (*reversed(directory.parents), directory):
            info = entry.lstat()
            require(stat.S_ISDIR(info.st_mode) and info.st_uid == 0
                    and not stat.S_IMODE(info.st_mode) & 0o022,
                    'FIXTURE_MANAGED_BACKING_ANCESTRY_UNTRUSTED')
    before = path.lstat()
    require(stat.S_ISLNK(before.st_mode) and before.st_uid == 0
            and before.st_gid == os.getegid() and os.readlink(path) == str(target)
            and path.resolve(strict=True) == backing,
            'FIXTURE_ORIGINAL_MANAGED_LINK_CHANGED')
    link_fd = os.open(path, os.O_PATH | os.O_NOFOLLOW | os.O_CLOEXEC)
    target_fd = None
    try:
        target_fd = os.open(backing, os.O_PATH | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
        held, destination = os.fstat(link_fd), os.fstat(target_fd)
        require(inode(held) == inode(before) == inode(path.lstat())
                and inode(destination) == inode(backing.lstat())
                and os.readlink(path) == str(target) and path.resolve(strict=True) == backing,
                'FIXTURE_ORIGINAL_MANAGED_LINK_READBACK_CHANGED')
        return {'path': str(path), 'target': str(target), 'backing': str(backing),
                'link_identity': inode(held), 'target_identity': inode(destination)}
    finally:
        if target_fd is not None:
            os.close(target_fd)
        os.close(link_fd)


def formation(builder, paths, store, core, spec):
    require(type(spec) is dict and set(spec) == {'source', 'observation_source',
            'roots', 'kind', 'primary', 'confirmed'}, 'FIXTURE_MANAGED_INPUT_KEYSET')
    require(type(spec['roots']) is list and spec['roots']
            and len(set(spec['roots'])) == len(spec['roots'])
            and spec['primary'] in spec['roots'] and spec['confirmed'] is True,
            'FIXTURE_MANAGED_EXPLICIT_ROOT_SET_CONFIRMATION_REQUIRED')
    roots = [builder.target(relative) for relative in spec['roots']]
    for root in roots:
        builder.protected(root, True)
    original = builder.module('worldline.roots', spec['source'])
    observer = builder.module('observe_worldline', spec['observation_source'])
    from worldline.status import StatusPublisher
    from worldline.canonical import canonical_bytes
    _lease.check()
    registered = original.RootManager(paths, store, core=core).register(
        roots, kind=spec['kind'], primary=builder.target(spec['primary']), confirmed=spec['confirmed'])
    # This actual in-process snapshot is explicitly NOT a sealed daemon verdict.
    status = StatusPublisher(paths, store).snapshot(daemon_state='OFFLINE_OWNER_FORMATION')
    raw = canonical_bytes(status)
    observation = observer.summarize(status, raw)
    require(observation['prime_state'] == 'VALID' and observation['prime_dirty'] is False
            and observation['running_jobs'] == []
            and observation['prime_id'] == registered['prime'].removeprefix('sha256:')
            and observation['prime_generation'] == registered['generation']
            and {row['path'] for row in observation['roots']} == {str(root) for root in roots},
            'FIXTURE_ORIGINAL_MANAGED_FORMATION_READBACK_CHANGED')
    links = {}
    for row in store.roots():
        selected_root = Path(os.fsdecode(bytes(row['path'])))
        live = paths.live / row['root_key']
        backing = paths.generations / registered['generation'] / 'payload' / row['root_key']
        for path, target, role in ((selected_root, live, 'managed-root'), (live, backing, 'live-mapping')):
            fact = mapping(path, target, backing, builder.root)
            fact['role'] = role
            links[str(path)] = fact
    require(set(links) == {str(root) for root in roots}
            | {str(paths.live / row['root_key']) for row in store.roots()},
            'FIXTURE_MANAGED_COMPLETE_MAPPING_KEYSET_CHANGED')
    _lease.check()
    return {'classification': 'ACTUAL_OFFLINE_OWNER_FORMATION_NOT_SEALED_DAEMON',
            'registration': registered, 'status_raw_hex': raw.hex(),
            'observation': observation, 'mappings': links}


def universe(genesis, formation):
    require(type(genesis) is dict and set(genesis) == {'nonce', 'parent_id', 'policy_descriptors',
            'prime_worldline_id', 'prime_id', 'prime_generation', 'receipt_head_id'},
            'FIXTURE_MANAGED_UNIVERSE_FULL_GENESIS_KEYSET')
    require(formation['classification'] == 'ACTUAL_OFFLINE_OWNER_FORMATION_NOT_SEALED_DAEMON',
            'FIXTURE_MANAGED_ACTUAL_FORMATION_REQUIRED')
    require(all(genesis[name] is None for name in ('nonce', 'prime_worldline_id',
            'prime_id', 'receipt_head_id')) and genesis['prime_generation'] == 0,
            'FIXTURE_MANAGED_UNIVERSE_AUTHENTIC_OUTPUT_LEAVES_REQUIRED')
    descriptors = genesis['policy_descriptors']
    require(type(descriptors) is dict and descriptors['worldline_set'] is None
            and descriptors['root_set'] is None,
            'FIXTURE_MANAGED_UNIVERSE_ACTUAL_ROOT_SET_REQUIRED')
    # Copy all original complete owner-selected descriptors; do not edit grants,
    # mission, authority rules, roster or resource/provider/evaluator controls.
    complete = json.loads(canonical(genesis))
    observed = formation['observation']
    complete['nonce'] = secrets.token_hex(32)
    complete['policy_descriptors']['worldline_set'] = [observed['worldline_instance_id']]
    complete['policy_descriptors']['root_set'] = [row['path'] for row in observed['roots']]
    complete['prime_worldline_id'] = observed['worldline_instance_id']
    complete['prime_id'] = observed['prime_id']
    initial = {name: observed[name] for name in ('worldline_instance_uuid', 'worldline_instance_id',
               'root_set_id', 'prime_id', 'prime_generation', 'status_sha256')}
    complete['receipt_head_id'] = hashlib.sha256(
        b'COSMOGONY-INITIAL-WORLDLINE-OBSERVATION-v1\0' + canonical(initial)).hexdigest()
    return complete


def sealed(builder, endpoint, cfg, seal, formation, deadline):
    """Authenticate actual status/ping; offline facts only constrain correspondence."""
    observer = builder.module('observe_worldline',
        builder.plan['owner_inputs']['worldline-store']['managed']['observation_source'])
    from worldline.canonical import canonical_bytes
    records = {}
    for operation in ('status', 'ping'):
        path = builder.target('original-supervisor.' + operation + '.response')
        builder.protected(path.parent, True)
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
        raw = b''
        try:
            with os.fdopen(os.dup(fd), 'wb') as retained:
                with socket.socket(socket.AF_UNIX) as connection:
                    remaining = deadline - time.monotonic()
                    require(remaining > 0, 'FIXTURE_SEALED_OBSERVATION_ORIGINAL_TIMEOUT')
                    connection.settimeout(remaining)
                    connection.connect(cfg['daemon_socket'])
                    endpoint.check_connection(cfg, seal, connection)
                    request_id = secrets.token_hex(16)
                    request = canonical({'id': request_id, 'op': operation, 'args': {}}) + b'\n'
                    connection.sendall(request)
                    # Retain each real fragment before validation or a later
                    # timeout; a truncated response remains actual partial DATA.
                    while b'\n' not in raw and len(raw) <= 8_388_608:
                        remaining = deadline - time.monotonic()
                        require(remaining > 0, 'FIXTURE_SEALED_OBSERVATION_ORIGINAL_TIMEOUT')
                        connection.settimeout(remaining)
                        chunk = connection.recv(min(65536, 8_388_609 - len(raw)))
                        if not chunk:
                            break
                        raw += chunk
                        retained.write(chunk)
                        retained.flush()
                        os.fsync(retained.fileno())
                    endpoint.check_connection(cfg, seal, connection)
                    require(raw and len(raw) <= 8_388_608, 'FIXTURE_SEALED_RESPONSE_INCOMPLETE')
                    value = builder.exact(raw)
                    require(value.get('id') == request_id and value.get('ok') is True
                            and raw == canonical_bytes(value) + b'\n',
                            'FIXTURE_SEALED_RESPONSE_CHANGED')
                    records[operation] = {'request_hex': request.hex(), 'response_hex': raw.hex(),
                        'response_path': str(path), 'result': value['result']}
        finally:
            os.fsync(fd)
            os.close(fd)
            builder.sync(path.parent)
    status, ping = records['status']['result'], records['ping']['result']
    observation = observer.summarize(status, canonical_bytes(status))
    endpoint.check_entry(cfg, seal)
    endpoint.check_process(seal)
    require(endpoint.read_seal(cfg) == seal and ping.get('pid') == seal['pid']
            and observation['daemon']['pid'] == seal['pid']
            and ping.get('runtimeSourcePath') == cfg['daemon_source_path']
            and ping.get('runtimeSourceSha256') == cfg['daemon_source_sha256']
            and observation['prime_state'] == 'VALID' and observation['prime_dirty'] is False
            and observation['running_jobs'] == [], 'FIXTURE_SEALED_MANAGED_OBSERVATION_REFUSED')
    require(all(observation[name] == formation['observation'][name] for name in
            ('worldline_instance_uuid', 'worldline_instance_id', 'root_set_id',
             'prime_id', 'prime_generation')), 'FIXTURE_SEALED_ORIGINAL_FORMATION_CHANGED')
    _lease.check()
    managed = {name: observation[name] for name in ('worldline_instance_uuid', 'worldline_instance_id',
               'root_set_id', 'prime_id', 'prime_generation', 'status_sha256')}
    return {'classification': 'ACTUAL_SEALED_DAEMON_STATUS_AND_PING', 'raw_exchanges': records,
            'observation': managed, 'complete_summary': observation,
            'daemon_endpoint_generation': seal['generation']}
