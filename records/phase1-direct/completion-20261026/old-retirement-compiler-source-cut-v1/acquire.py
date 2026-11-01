#!/usr/bin/env python3
"""Materialize registered immutable candidate sources; never execute fetched code."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import signal
import stat
import time
import urllib.error
import urllib.request

BASE = Path('/home/sicarii/Work/worldline-phase1-direct-20261019')
ROOT = Path(__file__).absolute().parent
REG = BASE / 'records/phase1-direct/factory-20261101/resume-20261101T1050/o1-compiler-source-acquisition-registration.json'
REG_HASH = 'a7afb054222f96394be98c5c41c3e5d90c86066c2a12dd75fe3fd72324aca18f'
PREFIXES = {'AdaCore/spark2014': 'spark2014', 'gcc-mirror/gcc': 'gcc'}
PINS = {'AdaCore/spark2014': 'b9410c6ed36d4e69a6c4d31e152fa8facaf0235c', 'gcc-mirror/gcc': '6afcc4f6da931eb93f3ab001a0dd9650ea71d1ea'}
FILE_CAP = 4194304
RESPONSE_CAP = 33554432
OUTPUT_CAP = 50331648


def require(condition, code):
    if not condition:
        raise RuntimeError(code)


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def encode(value):
    return json.dumps(value, separators=(',', ':'), ensure_ascii=False).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def read(path, cap=FILE_CAP):
    require(not path.is_symlink(), 'READ_SYMLINK')
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(descriptor, 'rb') as source:
        data = source.read(cap + 1)
    require(len(data) <= cap, 'READ_CAP')
    return data


def sync_directory(path):
    descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def write(path, data):
    relative = path.relative_to(ROOT)
    require(len(relative.parts) <= 10, 'WRITE_DEPTH')
    parent = ROOT
    for part in relative.parts[:-1]:
        require(part not in ('', '.', '..'), 'WRITE_COMPONENT')
        parent = parent / part
        if not parent.exists():
            parent.mkdir(mode=0o700)
            sync_directory(parent.parent)
        require(parent.is_dir() and not parent.is_symlink(), 'WRITE_PARENT')
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    with os.fdopen(descriptor, 'wb') as output:
        require(output.write(data) == len(data), 'WRITE_COUNT')
        output.flush()
        os.fsync(output.fileno())
    require(read(path, OUTPUT_CAP) == data, 'WRITE_READBACK')
    require(stat.S_IMODE(path.stat().st_mode) == 0o644, 'LOCAL_DATA_MODE')
    sync_directory(path.parent)


def append(stream, receipt):
    data = encode(receipt) + b'\n'
    require(len(data) <= 8192, 'RECEIPT_BOUND')
    require(stream.write(data) == len(data), 'RECEIPT_COUNT')
    stream.flush()
    os.fsync(stream.fileno())


def open_log(name):
    descriptor = os.open(ROOT / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    sync_directory(ROOT)
    return os.fdopen(descriptor, 'wb')


def capacity(state, stream):
    now = time.monotonic()
    if now - state.get('capacity_monotonic', -1000.0) < 30.0:
        return
    filesystem = os.statvfs(BASE)
    available = filesystem.f_bavail * filesystem.f_frsize
    receipt = {'utc': utc(), 'available_bytes': available, 'reserve_bytes': 10000000000, 'output_budget': OUTPUT_CAP, 'recovery_budget': OUTPUT_CAP, 'maximum_observation_age_seconds': 60}
    append(stream, receipt)
    require(available >= 10000000000 + 2 * OUTPUT_CAP, 'CAPACITY_RESERVE')
    state['capacity_monotonic'] = now


def validate_source(entry, data):
    require(entry['mode'] in ('100644', '100755'), 'UPSTREAM_SOURCE_MODE')
    require(len(data) == entry['bytes'], 'SOURCE_SIZE')
    require(blob(data) == entry['git_blob_sha1'], 'SOURCE_GIT_BLOB')


def reuse(entry):
    matches = entry['local_exact_matches']
    require(0 < len(matches) <= 5, 'REUSE_ALTERNATIVE_COUNT')
    result = None
    for match in matches:
        if match['kind'] == 'local_file':
            data = read(Path(match['path']))
        else:
            require(match['kind'] == 'embedded_json', 'REUSE_KIND')
            payload = json.loads(read(Path(match['path'])))
            index = int(match['json_pointer'].split('/')[2])
            require(0 <= index < len(payload['readbacks']) <= 100, 'REUSE_POINTER')
            data = payload['readbacks'][index]['content'].encode()
        require(match['transform'] in ('identity', 'append_one_LF'), 'REUSE_TRANSFORM')
        if match['transform'] == 'append_one_LF':
            require(len(data) == match['original_bytes'] and blob(data) == match['original_blob'], 'RECONSTRUCTION_INPUT')
            data += b'\n'
        validate_source(entry, data)
        require(sha(data) == match['sha256'], 'REUSE_SHA256')
        result = data
    require(result is not None, 'REUSE_RESULT')
    return result


def timeout(_signum, _frame):
    raise TimeoutError('NETWORK_WALL_DEADLINE')


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, _request, _fp, _code, _msg, _headers, _url):
        raise RuntimeError('HTTP_REDIRECT_REFUSED')


def fetch(opener, entry, state, receipt):
    require(state['requests'] < 671, 'REQUEST_LIMIT')
    remaining = state['deadline'] - time.monotonic()
    require(remaining > 0, 'TOTAL_NETWORK_DEADLINE')
    require(time.monotonic() - state['capacity_monotonic'] <= 60, 'CAPACITY_OBSERVATION_AGE')
    state['requests'] += 1
    receipt.update({'kind': 'network', 'url': entry['immutable_source_url'], 'request_number': state['requests'], 'request_utc': utc()})
    request = urllib.request.Request(entry['immutable_source_url'], headers={'Accept-Encoding': 'identity', 'User-Agent': 'WORLDLINE-bounded-compiler-source-acquisition'})
    signal.setitimer(signal.ITIMER_REAL, min(10.0, remaining))
    try:
        chunks = []
        size = 0
        with opener.open(request, timeout=min(10.0, remaining)) as response:
            receipt['http_status'] = response.status
            require(response.status == 200, 'HTTP_STATUS')
            for _ in range(FILE_CAP // 65536 + 1):
                chunk = response.read(65536)
                size += len(chunk)
                state['response_bytes'] += len(chunk)
                require(size <= FILE_CAP and state['response_bytes'] <= RESPONSE_CAP, 'RESPONSE_BYTE_BOUND')
                chunks.append(chunk)
                if not chunk:
                    data = b''.join(chunks)
                    validate_source(entry, data)
                    return data
            raise RuntimeError('RESPONSE_NOT_TERMINATED_WITHIN_BOUND')
    except urllib.error.HTTPError as error:
        receipt['http_status'] = error.code
        limit = min(4096, RESPONSE_CAP - state['response_bytes'])
        failure_body = error.read(max(0, limit))
        state['response_bytes'] += len(failure_body)
        write(ROOT / 'failed-response-body.bin', failure_body)
        receipt['failure_body_sha256'] = sha(failure_body)
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        receipt['response_end_utc'] = utc()


def preflight():
    require(ROOT.resolve() == ROOT and all(not x.is_symlink() for x in [ROOT] + list(ROOT.parents)), 'ROOT_PATH')
    data = read(REG, 16384)
    require(sha(data) == REG_HASH, 'REGISTRATION_HASH')
    registration = json.loads(data)
    require(BASE / registration['output_root'] == ROOT, 'REGISTERED_ROOT')
    selected_data = read(BASE / registration['selected_mapping']['path'])
    missing_data = read(BASE / registration['missing_mapping']['path'])
    require(sha(selected_data) == registration['selected_mapping']['sha256'], 'SELECTED_MAPPING_HASH')
    require(sha(missing_data) == registration['missing_mapping']['sha256'], 'MISSING_MAPPING_HASH')
    entries = json.loads(selected_data)['files']
    missing = json.loads(missing_data)['files']
    require(len(entries) == 771 and sum(x['bytes'] for x in entries) == 37730838, 'SELECTED_COUNTS')
    require(len(missing) == 671 and sum(x['bytes'] for x in missing) == 30118965, 'MISSING_COUNTS')
    require(len({(x['repository'], x['path']) for x in entries}) == 771, 'DUPLICATE_SOURCE_PATH')
    require({(x['repository'], x['path']) for x in missing} == {(x['repository'], x['path']) for x in entries if not x['local_exact_matches']}, 'MISSING_PARTITION')
    for entry in entries:
        path = Path(entry['path'])
        require(not path.is_absolute() and '..' not in path.parts and len(path.parts) <= 8, 'SOURCE_PATH')
        require(entry['repository'] in PINS and entry['ref'] == PINS[entry['repository']], 'SOURCE_PIN')
        expected = 'https://raw.githubusercontent.com/' + entry['repository'] + '/' + entry['ref'] + '/' + entry['path']
        require(entry['immutable_source_url'] == expected and 0 < entry['bytes'] <= FILE_CAP, 'SOURCE_URL_SIZE')
    return registration, entries


def finalize(summary, registration):
    summary['ended_utc'] = utc()
    write(ROOT / 'acquisition-summary.json', encode(summary))
    note = 'Exact registered source candidate only. SPARK repository layout is under spark2014/; GCC repository layout is under gcc/ (thus gcc/gcc/ada/). Original metadata paths, pins, Git modes and explicit one-LF transformations remain in per-file receipts; all materialized data0644. Every successful source was validated before exclusive write and durably fsynced/read back before moving on. No fetched script, generator, compiler or proof was executed. Complete executable closure and installed correspondence remain UNPROVEN/UNKNOWN. Original O1 and unchanged D47 static-leak baseline remain required. No source-list amendment, retry, review-budget reset or public body publication is authorized. Retain third-party headers and exclude source bodies from public checkpoints.\n'
    write(ROOT / 'README.md', note.encode())
    paths = list(ROOT.rglob('*'))
    require(len(paths) <= 900 and all(not x.is_symlink() for x in paths), 'OUTPUT_TREE_BOUND')
    files = sorted(x for x in paths if x.is_file())
    require(len(files) <= 799 and sum(x.stat().st_size for x in files) <= OUTPUT_CAP - 262144, 'OUTPUT_BUDGET')
    payloads = [{'path': str(x.relative_to(ROOT)), 'bytes': len(read(x)), 'sha256': sha(read(x))} for x in files]
    manifest = {'schema': 'worldline.o1.compiler-source-candidate-manifest.v1', 'registration_sha256': REG_HASH, 'registered_scope': registration, 'repository_prefixes': PREFIXES, 'summary': summary, 'command': 'python3 records/phase1-direct/completion-20261026/old-retirement-compiler-source-cut-v1/acquire.py', 'files': payloads, 'manifest_excludes_itself': True}
    write(ROOT / 'manifest.json', encode(manifest))
    print(json.dumps(summary), flush=True)


def acquire(entries, state):
    verified = []
    failure = None
    opener = urllib.request.build_opener(NoRedirect())
    with open_log('source-receipts.jsonl') as receipts, open_log('capacity-observations.jsonl') as capacities:
        for index, entry in enumerate(entries):
            local_path = PREFIXES[entry['repository']] + '/' + entry['path']
            receipt = {'repository': entry['repository'], 'ref': entry['ref'], 'path': entry['path'], 'materialized_path': local_path, 'upstream_git_mode': entry['mode'], 'materialized_mode': '0644', 'start_utc': utc(), 'http_status': None}
            try:
                capacity(state, capacities)
                if entry['local_exact_matches']:
                    data = reuse(entry)
                    receipt.update({'kind': 'local_reuse', 'verified_alternatives': entry['local_exact_matches']})
                else:
                    data = fetch(opener, entry, state, receipt)
                write(ROOT / local_path, data)
                receipt.update({'status': 'VERIFIED_WRITTEN_READBACK', 'bytes': len(data), 'git_blob_sha1': blob(data), 'sha256': sha(data), 'end_utc': utc()})
                append(receipts, receipt)
                verified.append(receipt)
                if (index + 1) % 50 == 0:
                    print(json.dumps({'completed': index + 1, 'requests': state['requests'], 'response_bytes': state['response_bytes']}), flush=True)
            except Exception as error:
                receipt.update({'status': 'FAILED', 'error_type': type(error).__name__, 'error_code': str(error) if isinstance(error, RuntimeError) else type(error).__name__, 'end_utc': utc()})
                append(receipts, receipt)
                failure = receipt
                break
    return verified, failure


def run():
    registration, entries = preflight()
    started = utc()
    state = {'requests': 0, 'response_bytes': 0, 'deadline': time.monotonic() + 900.0}
    signal.signal(signal.SIGALRM, timeout)
    verified, failure = acquire(entries, state)
    complete = len(verified) == 771 and failure is None
    if complete:
        require(state['requests'] == 671 and state['response_bytes'] == 30118965, 'FINAL_NETWORK_COUNTS')
        require(sum(x['bytes'] for x in verified) == 37730838, 'FINAL_SOURCE_COUNTS')
    summary = {'schema': 'worldline.o1.compiler-source-candidate-acquisition.v1', 'status': 'COMPLETE_EXACT_CANDIDATE_SOURCE_BYTES' if complete else 'FAILED_PARTIAL_CANDIDATE_SOURCE_CUT', 'started_utc': started, 'verified_files': len(verified), 'verified_source_bytes': sum(x['bytes'] for x in verified), 'requests': state['requests'], 'response_bytes': state['response_bytes'], 'failure': failure, 'source_mapping_sha256': registration['selected_mapping']['sha256'], 'source_head_registered': registration['source_head'], 'installed_correspondence': 'UNKNOWN', 'candidate_executable_closure': 'UNPROVEN', 'generation_compiler_proof_install': 'UNRUN', 'source_list_amended': False, 'retries': 0, 'redirects': 0}
    finalize(summary, registration)
    return 0 if complete else 1


if __name__ == '__main__':
    raise SystemExit(run())
