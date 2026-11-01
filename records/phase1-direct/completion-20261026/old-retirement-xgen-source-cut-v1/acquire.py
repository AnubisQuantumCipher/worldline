#!/usr/bin/env python3
"""Bounded, one-attempt acquisition of the registered immutable interface cut."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import signal
import stat
import time
import urllib.error
import urllib.request

BASE = Path('/home/sicarii/Work/worldline-phase1-direct-20261019')
ROOT = Path(__file__).absolute().parent
REG = BASE / 'records/phase1-direct/factory-20261101/resume-20261101T1050/o1-xgen-source-acquisition-registration.json'
INV = BASE / 'records/phase1-direct/completion-20261026/old-retirement-xgen-prerequisites-v1'
PIN = 'b9410c6ed36d4e69a6c4d31e152fa8facaf0235c'
EXPECTED_REG = '1903116243dfcd83b63561ef3658302450839939dcfaa878d8718007efc98b20'
LIMIT_BYTES = 8 * 1024 * 1024
MAX_BODY = 512 * 1024
MAX_NETWORK = 4 * 1024 * 1024


def require(condition, code):
    if not condition:
        raise RuntimeError(code)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def blob_sha1(data):
    prefix = b'blob ' + str(len(data)).encode() + b'\0'
    return hashlib.sha1(prefix + data).hexdigest()


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def checked_read(path, cap):
    require(not path.is_symlink(), 'READ_SYMLINK')
    require(path.is_file() and path.stat().st_size <= cap, 'READ_SIZE_OR_TYPE')
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(descriptor, 'rb') as source:
        data = source.read(cap + 1)
    require(len(data) <= cap, 'READ_BOUND')
    return data


def validate_source(entry, data):
    require(entry['mode'] in ('100644', '100755'), 'SOURCE_MODE')
    require(len(data) == entry['bytes'], 'SOURCE_SIZE')
    require(blob_sha1(data) == entry['git_blob_sha1'], 'SOURCE_BLOB_SHA1')


def make_parents(path):
    relative = path.relative_to(ROOT)
    require(len(relative.parts) <= 8, 'PATH_DEPTH')
    current = ROOT
    for part in relative.parts[:-1]:
        require(part not in ('', '.', '..'), 'PATH_COMPONENT')
        current = current / part
        if not current.exists():
            current.mkdir(mode=0o700)
            descriptor = os.open(current.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        require(current.is_dir() and not current.is_symlink(), 'PARENT_TYPE')


def exclusive_write(path, data):
    require(path.is_relative_to(ROOT), 'WRITE_SCOPE')
    make_parents(path)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    with os.fdopen(descriptor, 'wb') as target:
        require(target.write(data) == len(data), 'WRITE_COUNT')
        target.flush()
        os.fsync(target.fileno())
    require(checked_read(path, LIMIT_BYTES) == data, 'WRITE_READBACK')
    directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def append_receipt(stream, value):
    data = encode(value) + b'\n'
    require(stream.write(data) == len(data), 'RECEIPT_WRITE_COUNT')
    stream.flush()
    os.fsync(stream.fileno())


def alarm_handler(_signal, _frame):
    raise TimeoutError('NETWORK_WALL_DEADLINE')


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, _request, _fp, _code, _msg, _headers, _url):
        raise RuntimeError('HTTP_REDIRECT_REFUSED')


def preflight():
    require(not ROOT.is_symlink() and ROOT.resolve() == ROOT, 'ROOT_PATH')
    for ancestor in [ROOT] + list(ROOT.parents):
        require(not ancestor.is_symlink(), 'ROOT_ANCESTOR_SYMLINK')
    registration_data = checked_read(REG, 16384)
    require(sha256(registration_data) == EXPECTED_REG, 'REGISTRATION_SHA256')
    registration = json.loads(registration_data)
    require(BASE / registration['path'] == ROOT, 'REGISTERED_DESTINATION')
    inventory_data = checked_read(INV / 'selected-source-mapping.json', 524288)
    missing_data = checked_read(INV / 'missing-source-mapping.json', 524288)
    require(sha256(inventory_data) == registration['source_inventory']['selected_mapping_sha256'], 'INVENTORY_SHA256')
    require(sha256(missing_data) == registration['source_inventory']['missing_mapping_sha256'], 'MISSING_SHA256')
    entries = json.loads(inventory_data)['files']
    missing = json.loads(missing_data)['files']
    require(len(entries) == 279 and len(missing) == 269, 'FILE_COUNTS')
    require(sum(e['bytes'] for e in entries) == 3364573, 'FULL_BYTE_SUM')
    require(sum(e['bytes'] for e in missing) == 3308281, 'MISSING_BYTE_SUM')
    require(len({e['path'] for e in entries}) == 279, 'DUPLICATE_PATH')
    for entry in entries:
        path = Path(entry['path'])
        require(not path.is_absolute() and '..' not in path.parts, 'SOURCE_PATH')
        origins = {'AdaCore/spark2014': PIN, 'AdaCore/gnatcoll-core': '1d4374ae9187fd14d42ca99a3deb0ab2ff1ebc55'}
        require(entry['repository'] in origins and entry['ref'] == origins[entry['repository']], 'SOURCE_ORIGIN')
        expected = 'https://raw.githubusercontent.com/' + entry['repository'] + '/' + entry['ref'] + '/' + entry['path']
        require(entry['immutable_source_url'] == expected, 'SOURCE_URL')
        require(0 < entry['bytes'] <= MAX_BODY, 'EXPECTED_SOURCE_BOUND')
    require({e['path'] for e in missing} == {e['path'] for e in entries if not e['local_exact_matches']}, 'MISSING_SET')
    return registration, entries


def reuse_source(entry):
    matches = entry['local_exact_matches']
    require(len(matches) == 1, 'LOCAL_MATCH_COUNT')
    match = matches[0]
    origin = match['retained_payload_file'] + '#' + match['json_pointer']
    payload = json.loads(checked_read(Path(match['retained_payload_file']), LIMIT_BYTES))
    index = int(match['json_pointer'].split('/')[2])
    require(0 <= index < len(payload['readbacks']) <= 100, 'READBACK_INDEX')
    data = payload['readbacks'][index]['content'].encode()
    require(sha256(data) == match['sha256'], 'RETAINED_SHA256')
    validate_source(entry, data)
    return data, origin


def fetch_source(opener, entry, state, receipt):
    require(state['requests'] < 269, 'NETWORK_REQUEST_LIMIT')
    remaining = state['deadline'] - time.monotonic()
    require(remaining > 0, 'NETWORK_RUN_DEADLINE')
    state['requests'] += 1
    receipt.update({'kind': 'network', 'url': entry['immutable_source_url'], 'request_utc': utc(), 'request_number': state['requests']})
    request = urllib.request.Request(entry['immutable_source_url'], headers={'Accept-Encoding': 'identity', 'User-Agent': 'WORLDLINE-bounded-source-acquisition'})
    signal.setitimer(signal.ITIMER_REAL, min(10.0, remaining))
    chunks = []
    try:
        with opener.open(request, timeout=min(10.0, remaining)) as response:
            receipt['http_status'] = response.status
            require(response.status == 200, 'HTTP_STATUS')
            for _ in range(MAX_BODY // 16384 + 1):
                require(time.monotonic() < state['deadline'], 'NETWORK_RUN_DEADLINE')
                chunk = response.read(16384)
                state['body_bytes'] += len(chunk)
                require(state['body_bytes'] <= MAX_NETWORK, 'NETWORK_BODY_SUM')
                chunks.append(chunk)
                require(sum(map(len, chunks)) <= MAX_BODY, 'RESPONSE_BODY_BOUND')
                if not chunk:
                    data = b''.join(chunks)
                    validate_source(entry, data)
                    return data
            raise RuntimeError('RESPONSE_NOT_TERMINATED_WITHIN_BOUND')
    except urllib.error.HTTPError as error:
        receipt['http_status'] = error.code
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        receipt['response_end_utc'] = utc()


def artifact_inventory():
    files = list(ROOT.rglob('*'))
    require(len(files) <= 350, 'TREE_ENTRY_LIMIT')
    result = []
    for path in sorted(files):
        require(not path.is_symlink(), 'ARTIFACT_SYMLINK')
        if path.is_file():
            data = checked_read(path, LIMIT_BYTES)
            require(stat.S_IMODE(path.stat().st_mode) == 0o644, 'ARTIFACT_MODE')
            result.append({'path': str(path.relative_to(ROOT)), 'bytes': len(data), 'sha256': sha256(data)})
    require(len(result) <= 319, 'ARTIFACT_FILE_LIMIT')
    require(sum(e['bytes'] for e in result) <= LIMIT_BYTES - 32768, 'ARTIFACT_BYTE_LIMIT')
    return result


def run():
    registration, entries = preflight()
    state = {'requests': 0, 'body_bytes': 0, 'deadline': time.monotonic() + 300.0}
    started = utc()
    verified = []
    failure = None
    opener = urllib.request.build_opener(NoRedirect())
    signal.signal(signal.SIGALRM, alarm_handler)
    descriptor = os.open(ROOT / 'source-receipts.jsonl', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    with os.fdopen(descriptor, 'wb') as receipts:
        for index, entry in enumerate(entries):
            receipt = {'repository': entry['repository'], 'ref': entry['ref'], 'path': entry['path'], 'upstream_git_mode': entry['mode'], 'materialized_mode': '0644', 'start_utc': utc(), 'http_status': None}
            try:
                if entry['local_exact_matches']:
                    data, origin = reuse_source(entry)
                    receipt.update({'kind': 'local_reuse', 'origin': origin})
                else:
                    data = fetch_source(opener, entry, state, receipt)
                exclusive_write(ROOT / entry['path'], data)
                receipt.update({'status': 'VERIFIED_WRITTEN_READBACK', 'bytes': len(data), 'git_blob_sha1': blob_sha1(data), 'sha256': sha256(data), 'end_utc': utc()})
                append_receipt(receipts, receipt)
                verified.append(receipt)
                if (index + 1) % 20 == 0:
                    print(json.dumps({'completed': index + 1, 'requests': state['requests'], 'body_bytes': state['body_bytes']}), flush=True)
            except Exception as error:
                receipt.update({'status': 'FAILED', 'error_type': type(error).__name__, 'error_code': str(error) if isinstance(error, RuntimeError) else type(error).__name__, 'end_utc': utc()})
                append_receipt(receipts, receipt)
                failure = receipt
                break
    complete = len(verified) == 279 and failure is None
    if complete:
        require(state['requests'] == 269 and state['body_bytes'] == 3308281, 'FINAL_NETWORK_COUNTS')
        require(sum(e['bytes'] for e in verified) == 3364573, 'FINAL_SOURCE_BYTES')
    summary = {'schema': 'worldline.o1.xgen-prerequisite-source-acquisition.v1', 'status': 'COMPLETE_EXACT_SOURCE_CUT' if complete else 'FAILED_PARTIAL_SOURCE_CUT', 'started_utc': started, 'ended_utc': utc(), 'verified_files': len(verified), 'verified_source_bytes': sum(e['bytes'] for e in verified), 'requests': state['requests'], 'response_body_bytes': state['body_bytes'], 'failure': failure, 'registration_sha256': EXPECTED_REG, 'source_to_installed_correspondence': 'UNKNOWN', 'build_closure': 'UNPROVEN', 'semantic_proof': 'UNPROVEN', 'generation_build_proof_executed': False}
    exclusive_write(ROOT / 'acquisition-summary.json', encode(summary))
    note = 'Exact immutable source acquisition only. Source bytes, sizes and Git blobs verified before exclusive writes; own SHA256 and full readback retained. No fetched source or script was executed. No generator, compiler, build, proof or installation ran. Original O1/full-value/implicit Old targets remain open. All bodies stored0644; upstream100755 wrapper modes retained, not executed. Third-party bodies excluded from public checkpoints. Prior8metadataqueries and one registered metadata recovery remain consumed; no reset. Source-to-installed correspondence UNKNOWN; complete executable build closure and semantic adequacy UNPROVEN. Prior tree-query history remains consumed. Each successful source is durably written before proceeding; failure stops without retry.\n'
    exclusive_write(ROOT / 'README.md', note.encode())
    manifest = {'schema': 'worldline.o1.xgen-prerequisite-source-manifest.v1', 'summary': summary, 'command': 'python3 records/phase1-direct/completion-20261026/old-retirement-xgen-source-cut-v1/acquire.py', 'registered_limits': registration, 'files': artifact_inventory(), 'manifest_excludes_itself': True}
    exclusive_write(ROOT / 'manifest.json', encode(manifest))
    print(json.dumps(summary), flush=True)
    return 0 if complete else 1


if __name__ == '__main__':
    raise SystemExit(run())
