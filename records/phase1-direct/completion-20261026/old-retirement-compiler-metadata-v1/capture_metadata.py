#!/usr/bin/env python3
"""Registered two-tree capture and finite candidate mapping; acquire no source."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import re
import signal
import time
import urllib.error
import urllib.request

BASE = Path('/home/sicarii/Work/worldline-phase1-direct-20261019')
ROOT = Path(__file__).absolute().parent
RECORDS = BASE / 'records/phase1-direct/completion-20261026'
REG = BASE / 'records/phase1-direct/factory-20261101/resume-20261101T1050/o1-compiler-metadata-registration.json'
REG_HASH = '98c57eaea91d3da99289f635d05df9667776fdb86cd5043c927b4c0f498748bf'
SPARK = 'b9410c6ed36d4e69a6c4d31e152fa8facaf0235c'
GCC = '6afcc4f6da931eb93f3ab001a0dd9650ea71d1ea'
OLD = RECORDS / 'old-retirement-source-inventory-v1'
CAP = 1048576
PACKET_CAP = 8388608


def require(condition, code):
    if not condition:
        raise RuntimeError(code)


def encode(value):
    return json.dumps(value, separators=(',', ':'), ensure_ascii=False).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def read(path, cap=4194304):
    require(not path.is_symlink(), 'READ_SYMLINK')
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(descriptor, 'rb') as source:
        data = source.read(cap + 1)
    require(len(data) <= cap, 'READ_CAP')
    return data


def write(name, data):
    require('/' not in name and name not in ('', '.', '..'), 'WRITE_NAME')
    descriptor = os.open(ROOT / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    with os.fdopen(descriptor, 'wb') as target:
        require(target.write(data) == len(data), 'WRITE_COUNT')
        target.flush()
        os.fsync(target.fileno())
    require(read(ROOT / name, PACKET_CAP) == data, 'WRITE_READBACK')
    directory = os.open(ROOT, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def timeout(_signum, _frame):
    raise TimeoutError('NETWORK_WALL_DEADLINE')


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, _request, _fp, _code, _msg, _headers, _url):
        raise RuntimeError('HTTP_REDIRECT_REFUSED')


def capture(spec, name, deadline):
    remaining = deadline - time.monotonic()
    require(remaining > 0, 'TOTAL_NETWORK_DEADLINE')
    receipt = {'url': spec['url'], 'start_utc': utc(), 'http_status': None, 'response_bytes': 0, 'retries': 0, 'redirects': 0}
    opener = urllib.request.build_opener(NoRedirect())
    request = urllib.request.Request(spec['url'], headers={'Accept': 'application/vnd.github+json', 'Accept-Encoding': 'identity', 'User-Agent': 'WORLDLINE-bounded-compiler-metadata'})
    signal.setitimer(signal.ITIMER_REAL, min(30.0, remaining))
    started = time.monotonic()
    try:
        chunks = []
        with opener.open(request, timeout=min(30.0, remaining)) as response:
            receipt['http_status'] = response.status
            require(response.status == 200, 'HTTP_STATUS')
            for _ in range(CAP // 16384 + 1):
                chunk = response.read(16384)
                receipt['response_bytes'] += len(chunk)
                require(receipt['response_bytes'] <= CAP, 'RESPONSE_CAP')
                chunks.append(chunk)
                if not chunk:
                    raw = b''.join(chunks)
                    write(name + '-tree-response.json', raw)
                    receipt.update({'status': 'RAW_CAPTURED_BEFORE_PARSE', 'end_utc': utc(), 'elapsed_seconds': time.monotonic() - started, 'sha256': sha(raw)})
                    write(name + '-capture-receipt.json', encode(receipt))
                    return raw
            raise RuntimeError('RESPONSE_NOT_TERMINATED_WITHIN_BOUND')
    except Exception as error:
        if isinstance(error, urllib.error.HTTPError):
            receipt['http_status'] = error.code
        receipt.update({'status': 'FAILED_CAPTURE', 'end_utc': utc(), 'error_type': type(error).__name__, 'error_code': str(error) if isinstance(error, RuntimeError) else type(error).__name__})
        write(name + '-failed-receipt.json', encode(receipt))
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


def validate_tree(raw, expected):
    tree = json.loads(raw)
    require(tree['sha'] == expected and tree['truncated'] is False, 'TREE_ID_OR_TRUNCATION')
    require(isinstance(tree['tree'], list) and len(tree['tree']) <= 4096, 'TREE_ENTRY_BOUND')
    require(len({x['path'] for x in tree['tree']}) == len(tree['tree']), 'DUPLICATE_PATH')
    modes = {'blob': {'100644', '100755', '120000'}, 'tree': {'040000', '40000'}, 'commit': {'160000'}}
    for node in tree['tree']:
        path = Path(node['path'])
        require(not path.is_absolute() and len(path.parts) <= 16 and all(x not in ('', '.', '..') for x in path.parts), 'UNSAFE_PATH')
        require(node['type'] in modes and node['mode'] in modes[node['type']], 'GIT_MODE_TYPE')
        require(re.fullmatch('[0-9a-f]{40}', node['sha']) is not None, 'GIT_OBJECT_ID')
        if node['type'] == 'blob':
            require(isinstance(node['size'], int) and 0 <= node['size'] <= 8388608, 'BLOB_SIZE_BOUND')
    return tree


def entry(node, repository, ref, prefix, role):
    path = prefix + node['path']
    return {'repository': repository, 'ref': ref, 'path': path, 'mode': node['mode'], 'bytes': node['size'], 'git_blob_sha1': node['sha'], 'role': role, 'immutable_source_url': 'https://raw.githubusercontent.com/' + repository + '/' + ref + '/' + path}


def select(spark_src, gcc_ada):
    spark_root = json.loads(read(OLD / 'sparkroot.tree.json'))
    gnat = json.loads(read(OLD / 'sparkgnat2why.tree.json'))
    gcc_root = json.loads(read(OLD / 'gccroot.tree.json'))
    require(spark_root['sha'] == SPARK and gcc_root['sha'] == GCC and not gnat['truncated'], 'RETAINED_ROOT_IDS')
    selected = []
    excluded = []
    direct = {'why', 'spark', 'utils', 'flow', 'common', 'counterexamples'}
    for node in spark_src['tree']:
        if node['type'] != 'blob':
            continue
        parts = Path(node['path']).parts
        keep = len(parts) == 2 and parts[0] in direct or node['path'].startswith('why/xgen/')
        row = entry(node, 'AdaCore/spark2014', SPARK, 'src/', 'direct_project_input_or_xgen')
        if keep:
            selected.append(row)
        else:
            excluded.append(dict(row, exclusion_reason='Outside direct six translator source directories and complete xgen subtree'))
    for node in gnat['tree']:
        if node['type'] != 'blob':
            continue
        keep = '/' not in node['path'] and (Path(node['path']).suffix in {'.gpr', '.adc', '.in', '.c', '.h'} or node['path'] == 'Makefile')
        row = entry(node, 'AdaCore/spark2014', SPARK, 'gnat2why/', 'translator_project_config_template_C')
        (selected if keep else excluded).append(row if keep else dict(row, exclusion_reason='Formatting or analyzer artifact; not a selected compilation/setup input'))
    for node in spark_root['tree']:
        if node['type'] == 'blob' and (Path(node['path']).suffix in {'.ads', '.adb'} or node['path'] in {'LICENSE', '.gitmodules'}):
            selected.append(entry(node, 'AdaCore/spark2014', SPARK, '', 'root_Ada_license_or_submodule_metadata'))
    omitted_bodies = {'back_end.adb', 'indepsw-aix.adb', 'indepsw-darwin.adb', 'indepsw-gnu.adb'}
    for node in gcc_ada['tree']:
        if node['type'] != 'blob':
            continue
        name = node['path']
        keep = ('/' not in name and (Path(name).suffix in {'.ads', '.adb'} or name.endswith('-tmpl')) and name not in omitted_bodies) or name == 'libgnat/s-rident.ads'
        row = entry(node, 'gcc-mirror/gcc', GCC, 'gcc/ada/', 'embedded_frontend_or_generator_input')
        if keep:
            selected.append(row)
        else:
            reason = 'Excluded GNAT subproject body; selection optimization only, not acceptance' if name in omitted_bodies else 'Outside direct Ada/template inputs and required s-rident; source include closure UNPROVEN'
            excluded.append(dict(row, exclusion_reason=reason))
    for node in gcc_root['tree']:
        if node['type'] == 'blob' and node['path'].startswith('COPYING'):
            selected.append(entry(node, 'gcc-mirror/gcc', GCC, '', 'license'))
    links = [x for x in spark_root['tree'] if x['path'] == 'why3' and x['type'] == 'commit']
    require(len(links) == 1 and links[0]['sha'] == '120ec564d7b465507b2652251999a01045c9323a', 'WHY3_GITLINK')
    return selected, excluded, links[0]


def add_pool(pool, data, origin, expected=None):
    identity = blob(data)
    if expected is not None:
        require(len(data) == expected['bytes'] and identity == expected['git_blob_sha1'], 'LOCAL_REUSE_MATCH')
    pool.append(dict(origin, bytes=len(data), git_blob_sha1=identity, sha256=sha(data)))


def local_pool():
    pool = []
    interface = RECORDS / 'old-retirement-interface-source-cut-v1'
    manifest = json.loads(read(interface / 'manifest.json'))
    for item in manifest['files']:
        if item['path'].startswith('src/why/'):
            data = read(interface / item['path'])
            require(len(data) == item['bytes'] and sha(data) == item['sha256'], 'INTERFACE_PAYLOAD')
            add_pool(pool, data, {'kind': 'local_file', 'path': str(interface / item['path']), 'transform': 'identity'})
    previous = json.loads(read(OLD / 'reusable-source-evidence.json'))
    for item in previous['files']:
        for actual in item.get('local_matches', []):
            add_pool(pool, read(Path(actual['path'])), {'kind': 'local_file', 'path': actual['path'], 'transform': 'identity'}, actual)
    sdk = RECORDS / 'old-retirement-xgen-source-cut-v1'
    for path in ['src/why/why.ads', 'COPYING3', 'COPYING.RUNTIME']:
        add_pool(pool, read(sdk / path), {'kind': 'local_file', 'path': str(sdk / path), 'transform': 'identity'})
    allowed_lf = {'/readbacks/3/content': ('79ee48e0da968084e74edcf29ee206f612db430d', 3247), '/readbacks/4/content': ('6dc07130eeb94c44d03769bdc86247200b5b43a0', 2893), '/readbacks/5/content': ('2cc64843b052ae5e6fbcbc8368eb042435273339', 67)}
    for name in ['old-retirement-build-inputs.json', 'old-retirement-translator-build-closure.json']:
        path = RECORDS / name
        payload = json.loads(read(path))
        require(len(payload['readbacks']) <= 100, 'EMBEDDED_ROSTER_BOUND')
        for index, item in enumerate(payload['readbacks']):
            data = item.get('content', '').encode()
            if not data:
                continue
            pointer = '/readbacks/' + str(index) + '/content'
            add_pool(pool, data, {'kind': 'embedded_json', 'path': str(path), 'json_pointer': pointer, 'transform': 'identity'})
            if name == 'old-retirement-build-inputs.json' and pointer in allowed_lf:
                expected_blob, expected_size = allowed_lf[pointer]
                rebuilt = data + b'\n'
                require(len(rebuilt) == expected_size and blob(rebuilt) == expected_blob, 'REGISTERED_LF_RECONSTRUCTION')
                add_pool(pool, rebuilt, {'kind': 'embedded_json', 'path': str(path), 'json_pointer': pointer, 'transform': 'append_one_LF', 'original_bytes': len(data), 'original_blob': blob(data)})
    require(len(pool) <= 200, 'REUSE_POOL_BOUND')
    return pool


def derive(raws, registration):
    trees = [validate_tree(raw, spec['sha']) for raw, spec in zip(raws, registration['endpoints'])]
    selected, excluded, link = select(trees[0], trees[1])
    require(len(selected) <= 2830 and len(excluded) <= 3000, 'CANDIDATE_COUNT_BOUND')
    require(len({(x['repository'], x['path']) for x in selected}) == len(selected), 'SELECTED_DUPLICATE')
    require(all(x['mode'] in ('100644', '100755') for x in selected), 'SELECTED_REGULAR_SOURCE_ONLY')
    pool = local_pool()
    for row in selected:
        row['local_exact_matches'] = [x for x in pool if x['git_blob_sha1'] == row['git_blob_sha1'] and x['bytes'] == row['bytes']]
    reusable = [x for x in selected if x['local_exact_matches']]
    missing = [x for x in selected if not x['local_exact_matches']]
    counters = lambda items: {'paths': len(items), 'source_bytes': sum(x['bytes'] for x in items)}
    counts = {'selected': counters(selected), 'reusable': counters(reusable), 'missing': counters(missing), 'excluded_prior_roster': counters(excluded), 'spark_src_entries': len(trees[0]['tree']), 'gcc_ada_entries': len(trees[1]['tree'])}
    prior = [x for x in selected + excluded if not (x['repository'] == 'AdaCore/spark2014' and x['path'] == '.gitmodules')]
    require(sum(x['repository'] == 'AdaCore/spark2014' for x in prior) == 334, 'ORIGINAL_SPARK_ROSTER')
    require(sum(x['repository'] == 'gcc-mirror/gcc' for x in prior) == 2495, 'ORIGINAL_GCC_ROSTER')
    rules = {'status': 'PROJECT_SOURCE_CANDIDATE_ONLY; EXECUTABLE_CLOSURE_UNPROVEN', 'spark': 'All direct files in six translator source directories, full xgen subtree, direct root Ada, LICENSE and additional .gitmodules metadata; direct GNAT2Why project/config/template/C inputs', 'gcc': 'Direct Ada files except four recorded excluded bodies, direct *-tmpl, libgnat/s-rident.ads and five root COPYING files; retain gnat1drv.adb for setup copy', 'conservative_choices': ['Keep all direct source-directory files regardless extension; auxiliary input necessity unresolved', 'Keep all direct GNAT2Why .h/.c/.in/.adc/.gpr inputs and Makefile', 'Exclude four original GNAT bodies only as source-selection optimization; actual include/unit resolution may demand explicit amendment'], 'original_rosters': {'spark': 334, 'gcc': 2495}, 'additional_metadata': '.gitmodules 67 bytes; reconstructed only by recorded one-LF transformation', 'full_value_O1_target_unchanged': True, 'installed_correspondence': 'UNKNOWN'}
    write('selection-rules.json', encode(rules))
    for name, items in [('selected-candidate-mapping.json', selected), ('reusable-candidate-mapping.json', reusable), ('missing-candidate-mapping.json', missing), ('excluded-observed-paths.json', excluded)]:
        write(name, encode({'status': 'CANDIDATE_NOT_QUALIFIED_BUILD_CLOSURE', 'counts': counters(items), 'files': items}))
    write('why3-gitlink-metadata.json', encode({'repository': 'AdaCore/why3', 'ref': link['sha'], 'parent_repository': 'AdaCore/spark2014', 'parent_ref': SPARK, 'gitlink': link, 'source_body_fetches': 0, 'compatibility': 'UNKNOWN'}))
    write('reuse-pool-provenance.json', encode({'entries': pool, 'source_bytes_copied': 0, 'LF_reconstruction_is_explicit_not_source_relaxation': True}))
    return counts


def finish(summary):
    summary['ended_utc'] = utc()
    write('summary.json', encode(summary))
    text = 'Two registered compiler metadata captures only. Raw responses and receipts fsynced and read back before parsing. Every exclusion from the historical334SPARK/2495GCC roster is retained; .gitmodules is explicit additional metadata. Reuse includes exact verified bytes or three individually registered one-LF reconstructions. No source bytes copied or fetched. Candidate closure UNPROVEN; source-to-installed correspondence UNKNOWN. Future compiler acceptance requires complete include/unit/link inputs, generated/configuration identities, checked bounded unmodified translator build and unchanged D47 static-leak failures. Original O1/full-value/implicit Old target and negative controls remain open. Prior8queries, separate GNATcoll recovery and persistence failure remain retained; no review or execution-budget reset. No generation/compiler/proof/install/storage/publication action.\n'
    write('README.md', text.encode())
    files = sorted(x for x in ROOT.iterdir() if x.is_file())
    require(len(files) <= 31 and sum(x.stat().st_size for x in files) <= PACKET_CAP - 32768, 'PACKET_BUDGET')
    payloads = [{'path': x.name, 'bytes': len(read(x, PACKET_CAP)), 'sha256': sha(read(x, PACKET_CAP))} for x in files]
    write('manifest.json', encode({'schema': 'worldline.o1.compiler-metadata.v1', 'registration_sha256': REG_HASH, 'summary': summary, 'files': payloads, 'manifest_excludes_itself': True, 'command': 'python3 records/phase1-direct/completion-20261026/old-retirement-compiler-metadata-v1/capture_metadata.py'}))
    print(json.dumps(summary), flush=True)


def run():
    require(ROOT.resolve() == ROOT and all(not x.is_symlink() for x in [ROOT] + list(ROOT.parents)), 'ROOT_PATH')
    data = read(REG, 16384)
    require(sha(data) == REG_HASH, 'REGISTRATION_HASH')
    registration = json.loads(data)
    require(BASE / registration['permitted_write_root'] == ROOT and len(registration['endpoints']) == 2, 'REGISTRATION_SCOPE')
    summary = {'schema': 'worldline.o1.compiler-metadata-summary.v1', 'started_utc': utc(), 'requests': 0, 'source_body_requests': 0, 'source_bytes_copied': 0, 'installed_correspondence': 'UNKNOWN', 'candidate_closure': 'UNPROVEN', 'source_head_registered': registration['source_head'], 'failure': None}
    signal.signal(signal.SIGALRM, timeout)
    deadline = time.monotonic() + 90.0
    raws = []
    try:
        for index, spec in enumerate(registration['endpoints']):
            summary['requests'] += 1
            name = ['spark-src', 'gcc-ada'][index]
            raws.append(capture(spec, name, deadline))
            print(json.dumps({'captured': name, 'bytes': len(raws[-1]), 'sha256': sha(raws[-1]), 'durable_before_parse': True}), flush=True)
        summary['counts'] = derive(raws, registration)
        summary['status'] = 'COMPLETE_DURABLE_CANDIDATE_METADATA'
    except Exception as error:
        summary['status'] = 'FAILED_METADATA_OR_MAPPING; RETAIN_CAPTURED_EVIDENCE'
        summary['failure'] = {'type': type(error).__name__, 'code': str(error) if isinstance(error, RuntimeError) else type(error).__name__}
    finish(summary)
    return 0 if summary['failure'] is None else 1


if __name__ == '__main__':
    raise SystemExit(run())
