#!/usr/bin/env python3
"""Acquire only the three registered driver action source bodies as nonexecutable data."""
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
REG = BASE / 'records/phase1-direct/factory-20261101/resume-20261101T1050/o1-driver-actions-source-registration.json'
REG_HASH = '37040390cf57c2928180548919c244de19386087dfa1ebbb9105cafa46bd2e95'
CAP = 65536


def require(condition, code):
    if not condition:
        raise RuntimeError(code)


def encode(value):
    return json.dumps(value, separators=(',', ':')).encode()


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def read(path):
    require(not path.is_symlink(), 'READ_SYMLINK')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as source:
        data = source.read(1048577)
    require(len(data) <= 1048576, 'READ_CAP')
    return data


def sync_dir(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def write(path, data):
    relative = path.relative_to(ROOT)
    require(len(relative.parts) <= 4, 'WRITE_DEPTH')
    parent = ROOT
    for part in relative.parts[:-1]:
        require(part not in ('', '.', '..'), 'WRITE_COMPONENT')
        parent = parent / part
        if not parent.exists():
            parent.mkdir(mode=0o700)
            sync_dir(parent.parent)
        require(parent.is_dir() and not parent.is_symlink(), 'WRITE_PARENT')
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    with os.fdopen(fd, 'wb') as target:
        require(target.write(data) == len(data), 'WRITE_COUNT')
        target.flush()
        os.fsync(target.fileno())
    require(read(path) == data and stat.S_IMODE(path.stat().st_mode) == 0o644, 'WRITE_READBACK_MODE')
    sync_dir(path.parent)


def append(stream, value):
    data = encode(value) + b'\n'
    require(len(data) <= 4096 and stream.write(data) == len(data), 'RECEIPT_BOUND_WRITE')
    stream.flush()
    os.fsync(stream.fileno())


def alarm(_signum, _frame):
    raise TimeoutError('NETWORK_WALL_DEADLINE')


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, _request, _fp, _code, _msg, _headers, _url):
        raise RuntimeError('HTTP_REDIRECT_REFUSED')


def preflight():
    require(ROOT.resolve() == ROOT and all(not x.is_symlink() for x in [ROOT] + list(ROOT.parents)), 'ROOT_PATH')
    raw = read(REG)
    require(sha(raw) == REG_HASH, 'REGISTRATION_SHA256')
    registration = json.loads(raw)
    require(BASE / registration['permitted_write_root'] == ROOT and len(registration['files']) == 3, 'SCOPE')
    tree_raw = read(Path(registration['mapping']['path']))
    require(len(tree_raw) == registration['mapping']['bytes'] and sha(tree_raw) == registration['mapping']['sha256'], 'MAPPING_HASH')
    tree = json.loads(tree_raw)
    require(tree['sha'] == '0f1f51c51973750ae9d69c6b83c78afdb2598307' and tree['truncated'] is False, 'MAPPING_TREE')
    for entry in registration['files']:
        require(entry['path'] in ('src/gnatprove/configuration.ads', 'src/gnatprove/gpr2-build-actions-process-compile-ada-analysis.adb', 'src/gnatprove/gpr2-build-actions-process-compile-ada-global_gen.adb'), 'SOURCE_PATH')
        nodes = [x for x in tree['tree'] if x['path'] == entry['path'][4:]]
        require(len(nodes) == 1, 'MAPPING_JOIN')
        node = nodes[0]
        require(node['type'] == 'blob' and node['mode'] == entry['mode'] == '100644', 'MAPPING_MODE')
        require(node['size'] == entry['bytes'] and node['sha'] == entry['git_blob'], 'MAPPING_IDENTITY')
    require(sum(x['bytes'] for x in registration['files']) == 39488, 'SOURCE_BYTE_SUM')
    return registration


def fetch(entry, registration, state, receipt):
    require(state['requests'] < 3, 'REQUEST_LIMIT')
    remaining = state['deadline'] - time.monotonic()
    require(remaining > 0, 'NETWORK_RUN_LIMIT')
    url = 'https://raw.githubusercontent.com/AdaCore/spark2014/' + registration['source_commit'] + '/' + entry['path']
    receipt.update({'url': url, 'request_utc': utc(), 'http_status': None})
    state['requests'] += 1
    opener = urllib.request.build_opener(NoRedirect())
    request = urllib.request.Request(url, headers={'Accept-Encoding': 'identity', 'User-Agent': 'WORLDLINE-bounded-driver-source'})
    signal.setitimer(signal.ITIMER_REAL, min(10.0, remaining))
    try:
        parts = []
        size = 0
        with opener.open(request, timeout=min(10.0, remaining)) as response:
            receipt['http_status'] = response.status
            require(response.status == 200, 'HTTP_STATUS')
            for _ in range(CAP // 16384 + 1):
                chunk = response.read(16384)
                size += len(chunk)
                state['response_bytes'] += len(chunk)
                require(size <= CAP and state['response_bytes'] <= CAP, 'RESPONSE_BOUND')
                parts.append(chunk)
                if not chunk:
                    data = b''.join(parts)
                    require(len(data) == entry['bytes'] and blob(data) == entry['git_blob'], 'SOURCE_SIZE_GIT_BLOB')
                    return data
            raise RuntimeError('RESPONSE_NOT_TERMINATED_WITHIN_BOUND')
    except urllib.error.HTTPError as error:
        receipt['http_status'] = error.code
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        receipt['response_end_utc'] = utc()


def finish(summary):
    summary['ended_utc'] = utc()
    write(ROOT / 'summary.json', encode(summary))
    note = 'Three exact registered driver action source bodies only, stored0644 without execution. Immutable size/Git blob checked before materializing; source SHA256, fsynced per-file receipts and full readback retained. Remaining gnatprove main/body and any other source NOT_AUTHORIZED. No compiler, generator, proof, driver, installation, service, lock, archive, staging or commit action. Source identity is observed; translator-selection mechanism, source compatibility and installed correspondence remain UNKNOWN/UNPROVEN. Preserve prior query/failure history and exclude third-party bodies from public checkpoints.\n'
    write(ROOT / 'README.md', note.encode())
    files = sorted(x for x in ROOT.rglob('*') if x.is_file())
    require(len(files) <= 8 and sum(x.stat().st_size for x in files) <= 1048576 - 16384, 'PACKET_BUDGET')
    rows = [{'path': str(x.relative_to(ROOT)), 'bytes': len(read(x)), 'sha256': sha(read(x))} for x in files]
    write(ROOT / 'manifest.json', encode({'schema': 'worldline.o1.driver-actions-source-packet.v1', 'registration_sha256': REG_HASH, 'command': 'python3 records/phase1-direct/completion-20261026/old-retirement-driver-actions-source-cut-v1/acquire.py', 'summary': summary, 'files': rows, 'manifest_excludes_itself': True}))
    print(json.dumps(summary), flush=True)


def run():
    registration = preflight()
    filesystem = os.statvfs(BASE)
    available = filesystem.f_bavail * filesystem.f_frsize
    require(available >= 10000000000 + 2 * 1048576, 'CAPACITY_RESERVE')
    write(ROOT / 'selected-source-mapping.json', encode({'registration_sha256': REG_HASH, 'mapping': registration['mapping'], 'source_commit': registration['source_commit'], 'files': registration['files']}))
    summary = {'schema': 'worldline.o1.driver-actions-source-acquisition.v1', 'started_utc': utc(), 'verified_files': 0, 'verified_bytes': 0, 'failure': None, 'available_bytes_before_acquisition': available, 'source_execution': False, 'installed_correspondence': 'UNKNOWN', 'retries': 0, 'redirects': 0}
    state = {'requests': 0, 'response_bytes': 0, 'deadline': time.monotonic() + 40.0}
    signal.signal(signal.SIGALRM, alarm)
    fd = os.open(ROOT / 'source-receipts.jsonl', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    sync_dir(ROOT)
    with os.fdopen(fd, 'wb') as receipts:
        for entry in registration['files']:
            receipt = {'path': entry['path'], 'source_commit': registration['source_commit'], 'upstream_git_mode': entry['mode'], 'materialized_mode': '0644'}
            try:
                data = fetch(entry, registration, state, receipt)
                write(ROOT / entry['path'], data)
                receipt.update({'status': 'VERIFIED_WRITTEN_READBACK', 'bytes': len(data), 'git_blob_sha1': blob(data), 'sha256': sha(data), 'end_utc': utc()})
                append(receipts, receipt)
                summary['verified_files'] += 1
                summary['verified_bytes'] += len(data)
            except Exception as error:
                receipt.update({'status': 'FAILED', 'error_type': type(error).__name__, 'error_code': str(error) if isinstance(error, RuntimeError) else type(error).__name__, 'end_utc': utc()})
                append(receipts, receipt)
                summary['failure'] = receipt
                break
    complete = summary['verified_files'] == 3 and summary['failure'] is None
    if complete:
        require(summary['verified_bytes'] == state['response_bytes'] == 39488 and state['requests'] == 3, 'FINAL_COUNTS')
    summary.update({'status': 'COMPLETE_EXACT_THREE_FILE_SOURCE_CUT' if complete else 'FAILED_PARTIAL_SOURCE_CUT', 'requests': state['requests'], 'response_bytes': state['response_bytes']})
    finish(summary)
    return 0 if complete else 1


if __name__ == '__main__':
    raise SystemExit(run())
