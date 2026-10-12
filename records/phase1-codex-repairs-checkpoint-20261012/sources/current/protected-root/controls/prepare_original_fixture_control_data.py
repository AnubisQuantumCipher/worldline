"""Form original fixture DATA from actual selected bytes, never authority.

The dedicated resource descriptor omits only the original optional root_worker
member for the explicitly selected offline full-resource control purpose. The
original final root-worker descriptor is retained unchanged. Cache specimens
come from real selected benign source compilation by the original early lease;
they are compared by the unchanged loader controls and never executed here.
"""
from __future__ import annotations
import sys
_approved = sys.modules.get('_worldline_approved_source_loader')
if _approved is None:
    raise SystemExit('FIXTURE_DATA_FORMATION_EARLY_SOURCE_REQUIRED')
_lease = _approved.current()
if type(_lease) is not _approved.ApprovedSourceLease:
    raise SystemExit('FIXTURE_DATA_FORMATION_ACTUAL_EARLY_LEASE_REQUIRED')
_lease.check()
import argparse
import hashlib
import importlib._bootstrap_external as _external
import importlib.util
import json
import os
from pathlib import Path
import stat

SCHEMA = 'worldline.original-fixture-control-data-formation-v1'
KEYS = {'schema', 'startup_descriptor', 'output_directory', 'resource_descriptor',
        'loader_fixture', 'cache_source', 'different_cache_source'}


def require(value, reason):
    if not value:
        raise RuntimeError(reason)


def exact(raw):
    def pairs(rows):
        value = {}
        for key, item in rows:
            require(key not in value, 'FIXTURE_DATA_DUPLICATE_KEY')
            value[key] = item
        return value
    return json.loads(raw, object_pairs_hook=pairs,
        parse_constant=lambda text: (_ for _ in ()).throw(RuntimeError('FIXTURE_DATA_NONFINITE_JSON')))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
        ensure_ascii=False, allow_nan=False).encode()


def selected(path, roles):
    require(type(path) is str and path.startswith('/') and path == os.path.normpath(path)
            and '\0' not in path, 'FIXTURE_DATA_EXACT_ABSOLUTE_PATH_REQUIRED')
    raw = _lease.file(path, roles)
    info = Path(path).lstat()
    require(stat.S_ISREG(info.st_mode) and info.st_uid == 0 and info.st_gid == 0
        and info.st_nlink == 1 and not info.st_mode & 0o022,
        'FIXTURE_DATA_SELECTED_ROOT_REGULAR_REQUIRED')
    return raw, {'path': path, 'raw_hex': raw.hex(), 'sha256': hashlib.sha256(raw).hexdigest(),
        'bytes': len(raw), 'mode': stat.S_IMODE(info.st_mode), 'uid': info.st_uid,
        'gid': info.st_gid, 'links': info.st_nlink, 'device': info.st_dev, 'inode': info.st_ino}


def private_directory(path):
    require(type(path) is str and path.startswith('/') and path == os.path.normpath(path)
            and '\0' not in path, 'FIXTURE_DATA_OUTPUT_PATH_REQUIRED')
    target = Path(path)
    for member in (target, *target.parents):
        info = member.lstat()
        require(stat.S_ISDIR(info.st_mode) and not stat.S_ISLNK(info.st_mode)
                and info.st_uid == 0 and not info.st_mode & 0o022,
                'FIXTURE_DATA_ACTUAL_PROTECTED_ANCESTOR_REQUIRED')
    require(not target.lstat().st_mode & 0o077, 'FIXTURE_DATA_EXTERNAL_PRIVATE_OUTPUT_REQUIRED')
    return target


def publish(path, raw, attempts):
    record = {'path': str(path), 'requested_mode': 0o600,
        'expected_raw_hex': raw.hex(), 'expected_sha256': hashlib.sha256(raw).hexdigest(),
        'created_identity': None, 'actual_readback': None, 'error': None}
    attempts.append(record)
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
                             | os.O_CLOEXEC, 0o600)
        try:
            stream = os.fdopen(descriptor, 'wb')
        except BaseException as holder_error:
            try:
                os.close(descriptor)
            except BaseException as close_error:
                record['unresolved_descriptor_close'] = {'descriptor': descriptor,
                    'type': type(close_error).__qualname__, 'message': str(close_error)}
                holder_error.add_note('Actual output descriptor close: ' + repr(close_error))
            raise
        with stream:
            info = os.fstat(stream.fileno())
            record['created_identity'] = {'device': info.st_dev, 'inode': info.st_ino,
                'mode': stat.S_IMODE(info.st_mode), 'uid': info.st_uid, 'gid': info.st_gid,
                'links': info.st_nlink}
            record['actual_write_return'] = stream.write(raw)
            stream.flush(); os.fsync(stream.fileno())
        parent = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
        try:
            os.fsync(parent)
        finally:
            os.close(parent)
        info = path.lstat(); actual = path.read_bytes()
        value = {'path': str(path), 'raw_hex': actual.hex(), 'sha256': hashlib.sha256(actual).hexdigest(),
            'bytes': len(actual), 'mode': stat.S_IMODE(info.st_mode), 'uid': info.st_uid,
            'gid': info.st_gid, 'links': info.st_nlink, 'device': info.st_dev, 'inode': info.st_ino}
        record['actual_readback'] = value
        require(actual == raw and stat.S_ISREG(info.st_mode) and info.st_uid == 0
            and info.st_gid == 0 and info.st_nlink == 1 and stat.S_IMODE(info.st_mode) == 0o600,
            'FIXTURE_DATA_ACTUAL_PUBLICATION_READBACK_REQUIRED')
        return value
    except BaseException as caught:
        record['error'] = {'module': type(caught).__module__, 'type': type(caught).__qualname__,
            'message': str(caught), 'repr': repr(caught), 'errno': getattr(caught, 'errno', None)}
        if record['created_identity'] is not None:
            try:
                info = path.lstat()
                if (info.st_dev, info.st_ino) == (record['created_identity']['device'],
                                               record['created_identity']['inode']):
                    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
                    with os.fdopen(descriptor, 'rb') as stream:
                        partial = stream.read()
                    record['actual_partial_raw_hex'] = partial.hex()
            except BaseException as read_error:
                record['actual_partial_read_error'] = {'type': type(read_error).__qualname__,
                    'message': str(read_error), 'repr': repr(read_error)}
        raise


def form(plan_path):
    require(os.geteuid() == 0 and sys.flags.isolated and sys.flags.no_site
        and sys.dont_write_bytecode, 'FIXTURE_DATA_ACTUAL_ROOT_I_S_B_REQUIRED')
    raw, plan_observation = selected(plan_path, ('DATA',))
    plan = exact(raw)
    require(type(plan) is dict and set(plan) == KEYS and plan['schema'] == SCHEMA
        and type(plan['resource_descriptor']) is bool and type(plan['loader_fixture']) is bool
        and (plan['resource_descriptor'] or plan['loader_fixture']),
        'FIXTURE_DATA_COMPLETE_SELECTED_FORMATION_REQUIRED')
    output = private_directory(plan['output_directory'])
    observed = {'schema': 'worldline.original-fixture-control-data-observation-v1',
        'selected_plan': plan_observation, 'inputs': {}, 'outputs': {}, 'errors': [],
        'publication_attempts': [], 'actual_authority_or_native_verdict': None, 'phase_acceptance': False}
    primary = None
    try:
        if plan['resource_descriptor']:
            descriptor_raw, before = selected(plan['startup_descriptor'], ('DATA',))
            observed['inputs']['original_descriptor'] = before
            spec = exact(descriptor_raw)
            require(type(spec) is dict and spec['schema'] == 'worldline.protected-startup-v1'
                and type(spec.get('root_worker')) is dict and set(spec['root_worker']) == {'owner_plan'},
                'FIXTURE_DATA_ORIGINAL_FULL_ROOT_WORKER_DESCRIPTOR_REQUIRED')
            root = Path(spec['paths']['authority_root'])
            require(root.parent == Path('/srv') and root.name.startswith('cosmogony-canonical-v1.control-')
                and output != root and not output.is_relative_to(root),
                'FIXTURE_DATA_DISTINCT_EXTERNAL_FORMATION_REQUIRED')
            derivative = dict(spec)
            del derivative['root_worker']
            require(set(derivative) == set(spec) - {'root_worker'}
                and all(derivative[key] == spec[key] for key in derivative),
                'FIXTURE_DATA_ONLY_ORIGINAL_OPTIONAL_MEMBER_MAY_DIFFER')
            observed['outputs']['resource_descriptor'] = publish(output / 'resource-control-descriptor.json',
                canonical(derivative) + b'\n', observed['publication_attempts'])
            after_raw, after = selected(plan['startup_descriptor'], ('DATA',))
            observed['inputs']['original_descriptor_after'] = after
            require(after_raw == descriptor_raw and after == before,
                'FIXTURE_DATA_ORIGINAL_FINAL_DESCRIPTOR_CHANGED')
            observed['resource_control_purpose'] = 'NEW_EXPLICIT_OFFLINE_RESOURCE_CONTROL_DATA_ONLY'
        else:
            require(plan['startup_descriptor'] is None, 'FIXTURE_DATA_UNSELECTED_DESCRIPTOR_REFUSED')
        if plan['loader_fixture']:
            source_raw, source = selected(plan['cache_source'], ('SOURCE',))
            other_raw, other = selected(plan['different_cache_source'], ('SOURCE',))
            observed['inputs']['cache_source'] = source
            observed['inputs']['different_cache_source'] = other
            require(source_raw != other_raw and plan['cache_source'] != plan['different_cache_source'],
                'FIXTURE_DATA_DISTINCT_GENUINE_CACHE_SOURCE_REQUIRED')
            faithful = _lease.compile_source(plan['cache_source'], '_worldline_fixture_cache_source')
            unfaithful = _lease.compile_source(plan['different_cache_source'], '_worldline_fixture_other_cache_source')
            source_hash = importlib.util.source_hash(source_raw)
            faithful_raw = bytes(_external._code_to_hash_pyc(faithful, source_hash, checked=True))
            unfaithful_raw = bytes(_external._code_to_hash_pyc(unfaithful, source_hash, checked=True))
            require(faithful_raw != unfaithful_raw, 'FIXTURE_DATA_CACHE_SPECIMENS_MUST_ACTUALLY_DIFFER')
            good = publish(output / 'faithful-cache.pyc', faithful_raw, observed['publication_attempts'])
            bad = publish(output / 'unfaithful-cache.pyc', unfaithful_raw, observed['publication_attempts'])
            observed['outputs']['faithful_cache'] = good
            observed['outputs']['unfaithful_cache'] = bad
            fixture = {'source': plan['cache_source'], 'faithful_cache': good['path'], 'unfaithful_cache': bad['path']}
            observed['outputs']['loader_fixture'] = publish(output / 'approved-loader-fixture.json', canonical(fixture), observed['publication_attempts'])
            require(selected(plan['cache_source'], ('SOURCE',))[0] == source_raw
                and selected(plan['different_cache_source'], ('SOURCE',))[0] == other_raw,
                'FIXTURE_DATA_ACTUAL_CACHE_SOURCE_DRIFT')
        else:
            require(plan['cache_source'] is None and plan['different_cache_source'] is None,
                'FIXTURE_DATA_UNSELECTED_CACHE_SOURCE_REFUSED')
        _lease.check()
    except BaseException as caught:
        primary = caught
        observed['errors'].append({'module': type(caught).__module__, 'type': type(caught).__qualname__,
            'message': str(caught), 'repr': repr(caught), 'errno': getattr(caught, 'errno', None)})
        raise
    finally:
        try:
            observed['selected_source_at_publication'] = _lease.check()
        except BaseException as source_error:
            observed['errors'].append({'stage': 'actual-source-readback', 'type': type(source_error).__qualname__,
                'message': str(source_error), 'repr': repr(source_error)})
            if primary is None:
                primary = source_error
        try:
            publish(output / 'formation-observation.json', canonical(observed), [])
        except BaseException as retention_error:
            if primary is None:
                raise
            primary.add_note('Actual fixture DATA retention: ' + repr(retention_error))
        if primary is not None and sys.exc_info()[0] is None:
            raise primary
    return observed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', required=True)
    args = parser.parse_args()
    form(args.plan)


if __name__ == '__main__':
    main()
