#!/usr/bin/env python3
"""One registered metadata GET; persist first, derive mappings, acquire no source."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import signal
import time
import urllib.error
import urllib.request

BASE = Path('/home/sicarii/Work/worldline-phase1-direct-20261019')
ROOT = Path(__file__).absolute().parent
REG = BASE / 'records/phase1-direct/factory-20261101/resume-20261101T1050/o1-prerequisite-metadata-registration.json'
REG_HASH = '9d6fb3d15ba42d88f39634e23d603cbb8438d6769f21d0ac31493bc5e53ad93b'
PIN = '1d4374ae9187fd14d42ca99a3deb0ab2ff1ebc55'
URL = 'https://api.github.com/repos/AdaCore/gnatcoll-core/git/trees/' + PIN + '?recursive=1'
CAP = 524288
PACKET_CAP = 4194304
OLD_HASH = 'e6775528ebcc32e18e3f92a9f07c2698133a4f2efd6522ef0031c7f2b1c9af9d'


def require(condition, code):
    if not condition:
        raise RuntimeError(code)


def encode(value):
    return json.dumps(value, separators=(',', ':'), ensure_ascii=False).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def read(path, cap=PACKET_CAP):
    require(not path.is_symlink(), 'READ_SYMLINK')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as source:
        data = source.read(cap + 1)
    require(len(data) <= cap, 'READ_CAP')
    return data


def write(name, data):
    require('/' not in name and name not in ('', '.', '..'), 'WRITE_NAME')
    fd = os.open(ROOT / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    with os.fdopen(fd, 'wb') as target:
        require(target.write(data) == len(data), 'WRITE_COUNT')
        target.flush()
        os.fsync(target.fileno())
    require(read(ROOT / name) == data, 'WRITE_READBACK')
    directory = os.open(ROOT, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def alarm(_signum, _frame):
    raise TimeoutError('NETWORK_WALL_DEADLINE')


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, _request, _fp, _code, _msg, _headers, _url):
        raise RuntimeError('HTTP_REDIRECT_REFUSED')


def fetch(receipt):
    opener = urllib.request.build_opener(NoRedirect())
    request = urllib.request.Request(URL, headers={'Accept': 'application/vnd.github+json', 'Accept-Encoding': 'identity', 'User-Agent': 'WORLDLINE-bounded-metadata-recovery'})
    chunks = []
    signal.signal(signal.SIGALRM, alarm)
    signal.setitimer(signal.ITIMER_REAL, 10.0)
    try:
        with opener.open(request, timeout=10) as response:
            receipt['http_status'] = response.status
            require(response.status == 200, 'HTTP_STATUS')
            for _ in range(CAP // 16384 + 1):
                chunk = response.read(16384)
                chunks.append(chunk)
                receipt['response_bytes'] += len(chunk)
                require(receipt['response_bytes'] <= CAP, 'RESPONSE_CAP')
                if not chunk:
                    data = b''.join(chunks)
                    write('gnatcoll-tree-response.json', data)
                    receipt['raw_response_sha256'] = digest(data)
                    receipt['raw_response_persisted_before_parse'] = True
                    return data
            raise RuntimeError('BODY_NOT_TERMINATED_WITHIN_BOUND')
    except urllib.error.HTTPError as error:
        receipt['http_status'] = error.code
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


def mapping(data):
    tree = json.loads(data)
    require(tree['sha'] == PIN and tree['truncated'] is False, 'TREE_ID_OR_TRUNCATION')
    require(tree['url'] == URL.split('?')[0], 'TREE_URL')
    require(isinstance(tree['tree'], list) and len(tree['tree']) <= 2000, 'TREE_COUNT_BOUND')
    names = [x['path'] for x in tree['tree']]
    require(len(names) == len(set(names)), 'DUPLICATE_TREE_PATH')
    roots = {'Makefile', 'gnatcoll.gpr', 'COPYING3', 'COPYING.RUNTIME'}
    helpers = {'gprproject/__init__.py', 'gprproject/gprbuild.py', 'gprproject/os.py'}
    selected = []
    for node in tree['tree']:
        path = Path(node['path'])
        require(not path.is_absolute() and '..' not in path.parts, 'TREE_PATH')
        if node['type'] != 'blob':
            continue
        if not (node['path'].startswith(('core/', 'minimal/')) or node['path'] in roots | helpers):
            continue
        require(node['mode'] in ('100644', '100755') and 0 < node['size'] <= CAP, 'SOURCE_METADATA_BOUND')
        selected.append({'repository': 'AdaCore/gnatcoll-core', 'ref': PIN, 'path': node['path'], 'mode': node['mode'], 'bytes': node['size'], 'git_blob_sha1': node['sha'], 'immutable_source_url': 'https://raw.githubusercontent.com/AdaCore/gnatcoll-core/' + PIN + '/' + node['path']})
    core_minimal = [x for x in selected if x['path'].startswith(('core/', 'minimal/'))]
    require(len(core_minimal) == 271 and sum(x['bytes'] for x in core_minimal) == 3293604, 'PRIOR_CORE_MINIMAL_RECONCILIATION')
    require(len(selected) == 278 and sum(x['bytes'] for x in selected) == 3362074, 'SELECTED_RECONCILIATION')
    return tree, selected


def reusable(selected):
    source = BASE / 'records/phase1-direct/completion-20261026/old-retirement-translator-build-closure.json'
    closure = json.loads(read(source))
    matches = []
    for index, entry in enumerate(closure['readbacks']):
        if entry['repository'] != 'AdaCore/gnatcoll-core':
            continue
        candidates = [x for x in selected if x['path'] == entry['path']]
        require(len(candidates) == 1 and entry['ref'] == PIN, 'REUSE_SELECTION')
        data = entry['content'].encode()
        require(len(data) == candidates[0]['bytes'] and blob(data) == candidates[0]['git_blob_sha1'], 'REUSE_BLOB_MATCH')
        matches.append({'path': entry['path'], 'bytes': len(data), 'git_blob_sha1': blob(data), 'sha256': digest(data), 'retained_payload_file': str(source), 'json_pointer': '/readbacks/' + str(index) + '/content'})
    require(len(matches) == 10 and sum(x['bytes'] for x in matches) == 56292, 'REUSE_COUNT_BYTES')
    return matches


def derive(raw, receipt):
    tree, selected = mapping(raw)
    receipt['parsed_json_reserialization_sha256'] = digest(encode(tree))
    receipt['prior_observed_reserialization_sha256'] = OLD_HASH
    receipt['prior_serialization_hash_match'] = digest(encode(tree)) == OLD_HASH
    require(receipt['prior_serialization_hash_match'], 'PRIOR_TREE_SERIALIZATION_MISMATCH')
    matches = reusable(selected)
    for entry in selected:
        entry['local_exact_matches'] = [x for x in matches if x['path'] == entry['path']]
    selected.append({'repository': 'AdaCore/spark2014', 'ref': 'b9410c6ed36d4e69a6c4d31e152fa8facaf0235c', 'path': 'src/why/why.ads', 'mode': '100644', 'bytes': 2499, 'git_blob_sha1': '1853905acc5d03980a1047332a19618d707d6abc', 'immutable_source_url': 'https://raw.githubusercontent.com/AdaCore/spark2014/b9410c6ed36d4e69a6c4d31e152fa8facaf0235c/src/why/why.ads', 'local_exact_matches': [], 'mapping_basis': 'Previously observed exact SPARK source tree; no body fetched'})
    missing = [x for x in selected if not x['local_exact_matches']]
    require(len(selected) == 279 and sum(x['bytes'] for x in selected) == 3364573, 'FULL_SELECTION_COUNTS')
    require(len(missing) == 269 and sum(x['bytes'] for x in missing) == 3308281, 'MISSING_SELECTION_COUNTS')
    write('selected-source-mapping.json', encode({'status': 'COMPLETE_IMMUTABLE_MAPPING_ONLY', 'files': selected}))
    write('missing-source-mapping.json', encode({'status': 'SOURCE_BODY_ACQUISITION_NOT_AUTHORIZED', 'files': missing}))
    write('reusable-exact-payloads.json', encode({'status': 'TEN_RETAINED_PAYLOADS_FRESHLY_HASHED; NO_SOURCE_COPIES', 'files': matches}))
    return {'tree_entries': len(tree['tree']), 'selected_paths': len(selected), 'selected_source_bytes': sum(x['bytes'] for x in selected), 'reusable_paths': len(matches), 'reusable_bytes': sum(x['bytes'] for x in matches), 'missing_paths': len(missing), 'missing_source_bytes': sum(x['bytes'] for x in missing)}


def finish(receipt, counts, failure):
    receipt.update({'end_utc': utc(), 'status': 'COMPLETE_METADATA_MAPPING' if failure is None else 'FAILED_METADATA_RECOVERY', 'failure': failure, 'counts': counts, 'source_bodies_fetched': 0, 'generation_build_proof': 'UNRUN', 'installed_correspondence': 'UNKNOWN', 'history': 'Original8queries consumed; prior in-memory persistence FAILED; one separately registered recovery request; no reset'})
    write('recovery-receipt.json', encode(receipt))
    note = 'Metadata-only recovery. The exact raw HTTP response was fsynced and read back before JSON parsing. Complete selected source mapping contains core/minimal, root Makefile/gnatcoll.gpr/COPYING3/COPYING.RUNTIME, three gprproject helpers, and the fixed SPARK Why parent. Ten retained exact source payloads were freshly hashed but not copied. No missing source body, generator, compiler, build, proof, install or storage operation is authorized here. Original source headers/pins and the prior FAILED persistence boundary remain intact; prior query history is not reset. Future third-party bodies remain excluded from public checkpoints. Source-to-installed correspondence UNKNOWN; executable build closure and semantic adequacy UNPROVEN.\n'
    write('README.md', note.encode())
    payloads = [x for x in ROOT.iterdir() if x.is_file()]
    require(len(payloads) <= 63 and sum(x.stat().st_size for x in payloads) <= PACKET_CAP - 16384, 'PACKET_CAP')
    inventory = [{'path': x.name, 'bytes': len(read(x)), 'sha256': digest(read(x))} for x in sorted(payloads)]
    write('manifest.json', encode({'schema': 'worldline.o1.xgen-prerequisite-metadata.v1', 'registration_sha256': REG_HASH, 'receipt': receipt, 'command': 'python3 records/phase1-direct/completion-20261026/old-retirement-xgen-prerequisites-v1/recover_metadata.py', 'files': inventory, 'manifest_excludes_itself': True}))
    print(json.dumps(receipt), flush=True)


def run():
    require(ROOT.resolve() == ROOT and all(not x.is_symlink() for x in [ROOT] + list(ROOT.parents)), 'ROOT_PATH')
    registration = read(REG, 16384)
    require(digest(registration) == REG_HASH, 'REGISTRATION_SHA256')
    settings = json.loads(registration)
    require(BASE / settings['path'] == ROOT and settings['url'] == URL, 'REGISTRATION_SCOPE')
    receipt = {'schema': 'worldline.o1.durable-metadata-get.v1', 'start_utc': utc(), 'url': URL, 'requests': 1, 'response_bytes': 0, 'http_status': None, 'retries': 0, 'redirects': 0}
    started = time.monotonic()
    failure = None
    counts = None
    try:
        raw = fetch(receipt)
        receipt['network_and_capture_seconds'] = time.monotonic() - started
        counts = derive(raw, receipt)
    except Exception as error:
        failure = {'error_type': type(error).__name__, 'code': str(error) if isinstance(error, RuntimeError) else type(error).__name__}
    finish(receipt, counts, failure)
    return 0 if failure is None else 1


if __name__ == '__main__':
    raise SystemExit(run())
