"""Replay actual Main-produced owner/actor custody, never manufacture a fixture.

Requires a real completed original framed capture and the separately qualified
successor library. Missing input/symbol/baseline fails; no skip or mock fallback.
This native counterexample control is not actor execution or Phase acceptance.
"""
from __future__ import annotations
import argparse
import copy
import ctypes
import hashlib
import json
import os
from pathlib import Path
import struct
import stat
from worldline.root_worker_codec import archive, restore_archive


def retained_records(path):
    with path.open('rb') as stream:
        while True:
            word = stream.readline()
            if not word:
                return
            if not word.endswith(b'\n') or not word[:-1] or any(byte not in b'0123456789' for byte in word[:-1]):
                raise ValueError('complete decimal owner record length required')
            length = 0
            for byte in word[:-1]:
                length = length * 10 + byte - ord('0')
            raw = stream.read(length)
            if len(raw) != length:
                raise ValueError('partial owner record retained; not a completed baseline')
            value = restore_archive(raw)
            if archive(value) != raw:
                raise ValueError('original full scoped transport roundtrip differs')
            yield value


def message_changed(frame, index, change):
    row = frame['messages'][index]
    change(row['message'])
    row['message_raw'] = json.dumps(row['message'], sort_keys=True, separators=(',', ':'),
                                   ensure_ascii=True, allow_nan=False).encode('ascii')
    row['message_descriptor']['size'] = len(row['message_raw'])


def public_output(frame, stdout, stderr):
    if stdout != frame['terminal']['stdout']['raw'] or stderr != frame['terminal']['stderr']['raw']:
        raise AssertionError('original caller output differs from actual retained actor output')
    lines = stdout.splitlines()
    if not lines:
        raise AssertionError('original client identity output missing')
    observations = [json.loads(line) for line in lines]
    identity = observations[0]
    request = frame['request']
    if identity != {'actual_client_pid': frame['child_pid'], 'actual_uid': request['uid'],
                    'actual_gid': request['gid'],
                    'actual_server_ucred_hex': frame['target']['message']['server_credentials_hex']}:
        raise AssertionError('public identity is not the actual excluded socket actor')
    sent = 0
    settled = 0
    progress = False
    for observation in observations[1:]:
        if set(observation) == {'original_request_hex', 'actual_send_complete'}:
            if settled != sent or sent >= len(frame['requests']) or observation['actual_send_complete'] is not True:
                raise AssertionError('original ordered request or terminal response branch differs')
            if bytes.fromhex(observation['original_request_hex']) != frame['requests'][sent]['raw']:
                raise AssertionError('complete raw selected request changed')
            sent += 1
        elif set(observation) == {'original_response_hex'}:
            if settled >= sent or request['disconnect'] == 'after-send':
                raise AssertionError('unexpected original response branch')
            raw = bytes.fromhex(observation['original_response_hex'])
            if not raw.endswith(b'\n') or raw.count(b'\n') != 1:
                raise AssertionError('complete original response framing differs')
            response = json.loads(raw)
            if 'event' in response:
                progress = True
            else:
                settled += 1
        else:
            raise AssertionError('public original-client invocation/output contract changed')
    if request['disconnect'] == 'after-send':
        if sent != 1 or settled != 0:
            raise AssertionError('original after-send branch changed')
    elif request['disconnect'] == 'after-progress' and progress:
        if sent != settled + 1 or 'event' not in json.loads(bytes.fromhex(observations[-1]['original_response_hex'])):
            raise AssertionError('original after-progress branch changed')
    elif sent != len(frame['requests']) or settled != sent:
        raise AssertionError('original complete response sequence missing')
    return {'sent': sent, 'settled': settled, 'disconnect': request['disconnect'],
            'actual_actor_pid': frame['child_pid'], 'actual_owner_pid': frame['owner']['pid'],
            'stdout_sha256': hashlib.sha256(stdout).hexdigest(), 'stderr_sha256': hashlib.sha256(stderr).hexdigest()}


def require(value, reason):
    if not value:
        raise ValueError(reason)


def exact_json(raw):
    def pairs(rows):
        value = {}
        for key, item in rows:
            require(key not in value, 'duplicate Main custody field')
            value[key] = item
        return value
    return json.loads(raw, object_pairs_hook=pairs)


def pin_bytes(pin):
    path = Path(pin['path'])
    before = path.stat(follow_symlinks=False)
    require(stat.S_ISREG(before.st_mode), 'original retained regular artifact required')
    raw = path.read_bytes()
    after = path.stat(follow_symlinks=False)
    require(before == after and len(raw) == pin['bytes'] and stat.S_IMODE(after.st_mode) == pin['mode']
            and hashlib.sha256(raw).hexdigest() == pin['sha256'], 'full retained Main artifact bytes/mode changed')
    return raw


GENERATED_SOURCE_ROOTS = (
    'bin', 'explicit-recovery-marker-tests/bin', 'explicit-recovery-marker-tests/obj',
    'lib', 'obj', 'protocol-adapter-tests/bin', 'protocol-adapter-tests/obj',
    'recovery-protocol-tests/bin', 'recovery-protocol-tests/obj',
    'resource-tests/bin', 'resource-tests/obj', 'use-reservation-tests/bin',
    'use-reservation-tests/obj', 'wire-initialization-tests/bin',
    'wire-initialization-tests/obj',
)
GENERATED_PRIVATE_ROOTS = (
    'lib/gnat/sparklib_obj', 'lib/gnat/sparklib_lib', 'lib/gnat/proof',
)


def generated_fields(metadata):
    return (metadata.st_dev, metadata.st_ino, metadata.st_mode, metadata.st_nlink,
            metadata.st_size, metadata.st_mtime_ns, metadata.st_ctime_ns)


def generated_file_pin(path, *, follow_link=False, target=None):
    named_before = path.lstat()
    if follow_link:
        require(stat.S_ISLNK(named_before.st_mode) and os.readlink(path) == target,
                'generated symlink target changed')
    else:
        require(stat.S_ISREG(named_before.st_mode), 'generated regular file required')
    before = path.stat() if follow_link else named_before
    require(stat.S_ISREG(before.st_mode), 'generated retained file target required')
    flags = os.O_RDONLY | os.O_CLOEXEC
    if not follow_link:
        flags |= os.O_NOFOLLOW
    with os.fdopen(os.open(path, flags), 'rb') as stream:
        require(generated_fields(os.fstat(stream.fileno())) == generated_fields(before),
                'generated file descriptor differs from named file')
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        require(generated_fields(os.fstat(stream.fileno())) == generated_fields(before),
                'generated held file changed')
    require(generated_fields(path.stat()) == generated_fields(before)
            and generated_fields(path.lstat()) == generated_fields(named_before),
            'generated retained file or name changed')
    if follow_link:
        require(os.readlink(path) == target, 'generated symlink target changed')
    return {'path': str(path), 'sha256': digest, 'bytes': before.st_size,
            'mode': stat.S_IMODE(before.st_mode)}


def generated_snapshot(root):
    # Preserve the original generated_outputs/snapshot(allow_links=True) format,
    # including None for a missing root and a file/symlink root snapshot.
    if not root.exists():
        return None
    rows = {}

    def visit(path):
        name = path.relative_to(root).as_posix()
        before = path.lstat()
        mode = stat.S_IMODE(before.st_mode)
        if stat.S_ISDIR(before.st_mode):
            rows[name] = {'kind': 'directory', 'mode': mode}
            for child in sorted(path.iterdir()):
                visit(child)
        elif stat.S_ISREG(before.st_mode):
            pin = generated_file_pin(path)
            rows[name] = {'kind': 'file', **{key: pin[key] for key in ('sha256', 'bytes', 'mode')}}
        elif stat.S_ISLNK(before.st_mode):
            rows[name] = {'kind': 'symlink', 'mode': mode, 'target': os.readlink(path)}
        else:
            raise ValueError('original generated snapshot rejects special files')
        require(generated_fields(before) == generated_fields(path.lstat()),
                'generated snapshot member changed')

    visit(root)
    return rows


def generated_inventory_custody(selected, terminal, inventory, by_path):
    terminal_folder = Path(selected['terminal']['path']).parent
    require(Path(selected['generated_inventory']['path'])
            == terminal_folder / 'owned-generated-output-inventory.json',
            'selector must name the original collector generated-inventory output')
    source_manifest = terminal['source_manifest']
    pin_bytes(source_manifest)
    candidate = Path(source_manifest['path']).parent
    require(Path(selected['proposal']['path']) == candidate / 'reviewed-launch-proposal.json',
            'generated outputs must belong to the actual original selected candidate')
    names = tuple('source/' + name for name in GENERATED_SOURCE_ROOTS) + tuple(
        'private-sparklib/' + name for name in GENERATED_PRIVATE_ROOTS)
    require(type(inventory) is dict and set(inventory) == set(names),
            'complete original generated-output root keyset required')
    expected_retained = set()
    actual_retained = {path for path in by_path if any(
        path == str(candidate / name) or path.startswith(str(candidate / name) + '/')
        for name in names)}
    for name in names:
        root = candidate / name
        actual = generated_snapshot(root)
        # Typed JSON equality excludes bool/float substitutions for genuine
        # integer metadata while preserving arbitrary original lengths/modes.
        require(json.dumps(actual, sort_keys=True, allow_nan=False)
                == json.dumps(inventory[name], sort_keys=True, allow_nan=False),
                'full original generated snapshot differs: ' + name)
        if actual is None:
            continue
        for relative, row in actual.items():
            path = root if relative == '.' else root / relative
            if row['kind'] == 'file':
                pin = {'path': str(path), **{key: row[key] for key in ('sha256', 'bytes', 'mode')}}
            elif row['kind'] == 'symlink' and path.is_file():
                # The original collector retains file symlink targets by their
                # named paths; preserve that behavior without traversing dirs.
                pin = generated_file_pin(path, follow_link=True, target=row['target'])
            else:
                continue
            require(by_path.get(str(path)) == pin,
                    'generated file is absent or mismatched in retained artifacts: ' + str(path))
            expected_retained.add(str(path))
    require(actual_retained == expected_retained,
            'retained generated file keyset differs from the complete snapshots')


def generated_custody_controls(selection_path):
    # Every positive and counterexample derives from the qualified genuine Main
    # collector input. No artifact, receipt, generated file or selector is made.
    selected = exact_json(selection_path.read_bytes())
    terminal = exact_json(pin_bytes(selected['terminal']))
    inventory = exact_json(pin_bytes(selected['generated_inventory']))
    retained = exact_json(pin_bytes(terminal['retained_complete_artifacts']))
    by_path = {pin['path']: pin for pin in retained.values()}
    generated_inventory_custody(selected, terminal, inventory, by_path)
    negative = []

    def refused(name, change):
        operands = copy.deepcopy((selected, terminal, inventory, by_path))
        change(*operands)
        try:
            generated_inventory_custody(*operands)
        except (ValueError, KeyError, TypeError, OSError) as error:
            print(json.dumps({'schema': 'worldline.generated-custody-counterexample-v3',
                              'control': name, 'operands': operands,
                              'refusal': {'type': type(error).__name__, 'reason': str(error)},
                              'authentic_producer_receipt': False}, sort_keys=True), flush=True)
            negative.append(name)
        else:
            raise AssertionError((name, 'incomplete generated custody admitted'))

    first = next(iter(inventory))
    refused('real-release-pin-substituted-for-generated-output',
            lambda selection, terminal, inventory, retained: selection.__setitem__(
                'generated_inventory', selection['release']))
    refused('generated-root-key-omitted',
            lambda selection, terminal, inventory, retained: inventory.pop(first))
    refused('generated-root-key-added',
            lambda selection, terminal, inventory, retained: inventory.__setitem__(
                first + '/not-an-original-output-root', None))
    refused('generated-root-snapshot-partial-or-substituted',
            lambda selection, terminal, inventory, retained: inventory.__setitem__(
                first, {} if inventory[first] is None else None))
    refused('wrong-original-generated-candidate-lineage',
            lambda selection, terminal, inventory, retained: selection.__setitem__(
                'proposal', selection['release']))
    candidate = Path(terminal['source_manifest']['path']).parent
    files = [(root, name, row) for root, snapshot in inventory.items() if snapshot is not None
             for name, row in snapshot.items() if row['kind'] == 'file']
    # The complete original matching native library/build output supplies a real
    # file witness. Missing it is a missing control input, never a skipped pass.
    require(files, 'genuine complete original generated file witness required')
    root, name, row = files[0]
    path = str(candidate / root) if name == '.' else str(candidate / root / name)
    refused('generated-file-row-omitted',
            lambda selection, terminal, inventory, retained: inventory[root].pop(name))
    for key in ('sha256', 'bytes', 'mode'):
        def mismatch(selection, terminal, inventory, retained, key=key):
            original = inventory[root][name][key]
            inventory[root][name][key] = (
                ('0' if original[0] != '0' else '1') + original[1:]
                if key == 'sha256' else original + 1)
        refused('generated-file-' + key + '-mismatch', mismatch)
    refused('generated-file-integer-metadata-replaced-by-float',
            lambda selection, terminal, inventory, retained: inventory[root][name].__setitem__(
                'bytes', float(row['bytes'])))
    refused('generated-retained-file-omitted',
            lambda selection, terminal, inventory, retained: retained.pop(path))
    refused('generated-retained-pin-content-mismatch',
            lambda selection, terminal, inventory, retained: retained[path].__setitem__(
                'bytes', retained[path]['bytes'] + 1))
    return {'positive': {'generated_inventory': selected['generated_inventory'],
                         'original_root_keys': list(inventory),
                         'generated_file_witness': by_path[path]},
            'negative_refused': negative, 'artifact_writes': False}


def completed_input(records):
    finals = [(index, record['value']) for index, record in enumerate(records)
              if record['kind'] == 'OWNER_ACTOR_COMPLETED']
    require(len(finals) == 1, 'actual post-native source checks, cleanup and owner completion are required')
    index, completed = finals[0]
    require(index == len(records) - 1, 'interrupted/reopened owner archive is not a completed baseline')
    call = completed['native_call']
    require(call['phase'] == 'COMPLETE' and call['transport'] == 0 and call['action'] == 3,
            'genuine successful native completion call required')
    raw = call['raw']; frame = restore_archive(raw)
    require(archive(frame) == raw and archive(completed['frame']) == raw,
            'actual completed frame and exact native input diverge')
    inputs = [position for position, record in enumerate(records[:index])
              if record['kind'] == 'NATIVE_INPUT' and record['value']['phase'] == 'COMPLETE'
              and record['value']['raw'] == raw]
    results = [position for position, record in enumerate(records[:index])
               if record['kind'] == 'NATIVE_RESULT' and record['value']['phase'] == 'COMPLETE'
               and record['value']['raw'] == raw and record['value']['transport'] == 0
               and record['value']['action'] == 3]
    require(len(inputs) == len(results) == 1 and inputs[0] < results[0] < index,
            'exact actual input/result/owner completion ordering required')
    cleanup = [record['value'] for record in records[results[0] + 1:index] if record['kind'] == 'OWNER_CLEANUP']
    require(len(cleanup) == 1 and cleanup[0]['closes'] == completed['cleanup'] and not cleanup[0]['errors']
            and not completed['stop_wait'], 'failed/unknown owned actor or cleanup cannot qualify a baseline')
    require(completed['cleanup'] and all(row['call'] == 'close' and row['result'] == 0 and row['errno'] == 0
            and row['readback']['call'] == 'fstat' and row['readback']['result'] == -1
            and row['readback']['errno'] == 9 and row['readback']['fd'] == row['fd']
            for row in completed['cleanup']), 'actual complete descriptor closes/readbacks required')
    require(completed['owner_final_source'] == frame['owner_final_source']
            and call['post_source']['envelope_bytes_hex'] == frame['owner_source']['envelope_bytes_hex']
            and call['post_mapping']['raw'] == frame['native_mapping']['raw'],
            'real original owner finally and post-call checks must correspond')
    require(frame['phase'] == 'COMPLETE' and frame['error'] is None and frame['terminal']['wait'] == 0,
            'actual successful actor terminal custody required')
    return frame, raw, completed


def scope_custody(scope):
    # The original collector preserves only returned manager properties. A
    # missing optional PID property stays absent; it is never normalized to 0.
    require(type(scope) is dict and type(scope.get('returncode')) is int
            and scope['returncode'] == 0, 'successful actual scope observation required')
    props = scope.get('properties'); group = scope.get('cgroup')
    require(type(props) is dict
            and all(type(key) is str and type(value) is str for key, value in props.items()),
            'original unnormalized scope property strings required')
    require(props.get('LoadState') in ('loaded', 'not-found')
            and props.get('ActiveState') in ('inactive', 'failed')
            and props.get('SubState') in ('dead', 'failed'),
            'actual owned scope must be terminal, not loading or unknown')
    require(all(name not in props or props[name] == '0' for name in ('MainPID', 'ControlPID')),
            'every actually supplied scope PID must be exactly string zero')
    require(props.get('Result') == 'success'
            or (props['LoadState'] == 'not-found' and props.get('Result') == ''),
            'relevant failed/unknown scope result is not a successful producer baseline')
    require(type(group) is dict and set(group) == {'path', 'exists', 'processes'}
            and type(group['exists']) is bool
            and (group['processes'] == [] or (group['processes'] is None and group['exists'] is False)),
            'actual owned descendant group must be readable and empty or genuinely absent')
    require(type(props.get('ControlGroup')) is str, 'actual original ControlGroup property required')
    if props['ControlGroup']:
        require(group['path'] == '/sys/fs/cgroup/' + props['ControlGroup'].lstrip('/'),
                'exact owned kernel cgroup path correspondence required')
    else:
        require(group == {'path': None, 'exists': False, 'processes': None},
                'absent original manager group shape required')


def scope_custody_controls(custody):
    # Called only AFTER full main_custody eligibility. These altered guard
    # operands are controls, never new manager observations or producer receipts.
    original = custody['actual_scope_observation']
    source = {key: custody[key] for key in ('selection_sha256', 'producer_mode', 'terminal', 'release')}
    positive = []; negative = []

    def observed(name, scope):
        scope_custody(scope)
        print(json.dumps({'schema': 'worldline.scope-custody-guard-control-v5',
                          'control': name, 'source': source, 'operand': scope,
                          'guard_passed': True, 'authentic_producer_receipt': False},
                         sort_keys=True), flush=True)
        positive.append(name)

    observed('genuine-complete-main-original-scope', original)
    omitted = copy.deepcopy(original)
    for name in ('MainPID', 'ControlPID'):
        omitted['properties'].pop(name, None)
    observed('scope-optional-pid-properties-omitted-without-defaults', omitted)

    def refused(name, change):
        altered = copy.deepcopy(omitted)
        change(altered)
        try:
            scope_custody(altered)
        except (ValueError, KeyError, TypeError) as error:
            print(json.dumps({'schema': 'worldline.scope-custody-guard-control-v5',
                              'control': name, 'source': source, 'operand': altered,
                              'refusal': {'type': type(error).__name__, 'reason': str(error)},
                              'authentic_producer_receipt': False}, sort_keys=True), flush=True)
            negative.append(name)
        else:
            raise AssertionError((name, 'ineligible scope custody admitted'))

    for name in ('MainPID', 'ControlPID'):
        for label, value in (('nonzero', str(custody['owner_pid'])), ('empty', ''),
                             ('padded-zero', '00'), ('negative', '-1'), ('nondecimal', 'unknown'),
                             ('integer-zero', 0), ('float-zero', 0.0), ('null', None), ('boolean', False)):
            refused('scope-' + name + '-' + label,
                    lambda scope, name=name, value=value: scope['properties'].__setitem__(name, value))
    for field, values in (
            ('LoadState', ('loading', 'error', 'unknown')),
            ('ActiveState', ('active', 'activating', 'deactivating')),
            ('SubState', ('running', 'start', 'unknown')),
            ('Result', ('unknown', 'exit-code', 'timeout'))):
        for value in values:
            refused('scope-' + field + '-' + value,
                    lambda scope, field=field, value=value: scope['properties'].__setitem__(field, value))
        refused('scope-' + field + '-missing',
                lambda scope, field=field: scope['properties'].pop(field))
        refused('scope-' + field + '-null',
                lambda scope, field=field: scope['properties'].__setitem__(field, None))
    def loaded_blank_result(scope):
        scope['properties']['LoadState'] = 'loaded'
        scope['properties']['Result'] = ''
    refused('scope-loaded-blank-result', loaded_blank_result)
    refused('scope-ControlGroup-missing', lambda scope: scope['properties'].pop('ControlGroup'))
    refused('scope-ControlGroup-null', lambda scope: scope['properties'].__setitem__('ControlGroup', None))
    refused('scope-observation-nonzero', lambda scope: scope.__setitem__('returncode', 1))
    refused('scope-observation-null', lambda scope: scope.__setitem__('returncode', None))
    refused('scope-observation-boolean-zero', lambda scope: scope.__setitem__('returncode', False))
    refused('scope-properties-null', lambda scope: scope.__setitem__('properties', None))
    refused('scope-cgroup-null', lambda scope: scope.__setitem__('cgroup', None))
    refused('scope-cgroup-processes-missing', lambda scope: scope['cgroup'].pop('processes'))
    refused('scope-cgroup-exists-not-boolean', lambda scope: scope['cgroup'].__setitem__('exists', 0))
    refused('scope-cgroup-path-substituted-with-real-terminal-path',
            lambda scope: scope['cgroup'].__setitem__('path', custody['terminal']['path']))
    refused('scope-cgroup-nonempty',
            lambda scope: scope['cgroup'].__setitem__('processes', [str(custody['actor_pid'])]))
    def unreadable(scope):
        scope['cgroup']['exists'] = True
        scope['cgroup']['processes'] = None
    refused('scope-cgroup-existing-but-unreadable', unreadable)
    return {'source': source, 'positive_guard_boundaries': positive,
            'negative_refused': negative, 'artifact_writes': False,
            'new_manager_observation_or_producer_receipt': False}


def main_custody(selection_path, frame, capture, library, stdout, stderr):
    # This selector names actual original artifacts. It is NOT a Main-approved
    # boolean, a delivered fixture receipt, an installation or a new controller.
    selected = exact_json(selection_path.read_bytes())
    keys = {'schema', 'producer_mode', 'proposal', 'terminal', 'outer_observations', 'release',
            'source_readback', 'private_readback', 'generated_inventory', 'case_result',
            'produce_result', 'export_request', 'owner_stdout', 'owner_stderr'}
    require(set(selected) == keys and selected['schema'] == 'worldline.fixed-source-owner-main-input-custody-v2',
            'explicit authentic Main producer artifact selection is required')
    raw = {key: pin_bytes(selected[key]) for key in keys - {'schema', 'producer_mode'}}
    value = {key: exact_json(data) for key, data in raw.items() if key not in ('owner_stdout', 'owner_stderr')}
    terminal = value['terminal']; release = value['release']
    require(terminal['schema'] == 'worldline-root-actual-ordinary-terminal-v1',
            'original collector family required; fixture wrapper enrollment remains a Main prerequisite')
    require(release['status'] == 'released' and release['terminal'] == selected['terminal']
            and release['at'] >= terminal['at'], 'actual post-terminal coordination release required')
    inventory = exact_json(pin_bytes(terminal['retained_complete_artifacts']))
    by_path = {pin['path']: pin for pin in inventory.values()}
    require(len(by_path) == len(inventory), 'retained artifact paths must be unique')
    for key in ('proposal', 'case_result', 'produce_result', 'export_request', 'owner_stdout', 'owner_stderr'):
        require(selected[key]['path'] in by_path and by_path[selected[key]['path']] == selected[key],
                'actual original retained full artifact inventory must bind ' + key)
    require(value['source_readback']['exact_keyset_bytes_modes_match'] is True
            and value['private_readback']['matches'] is True,
            'original complete source/private dependency readbacks required')
    generated_inventory_custody(selected, terminal, value['generated_inventory'], by_path)
    require(value['source_readback']['actual_files'], 'actual original source inventory required')
    actual_source = value['private_readback']['actual']['complete_source_entries']
    actual_hashes = {name: row['sha256'] for name, row in actual_source.items() if row['kind'] == 'file'}
    require(actual_hashes == value['source_readback']['actual_files'],
            'full original source readback keysets/content must correspond, not only a matches flag')
    for name, row in actual_source.items():
        if row['kind'] != 'file': continue
        matches = [pin for pin in by_path.values() if pin['path'].endswith('/source/' + name)]
        require(len(matches) == 1 and all(matches[0][key] == row[key] for key in ('sha256', 'bytes', 'mode')),
                'actual full source inventory/readback binding differs: ' + name)
        pin_bytes(matches[0])
    private_inputs = value['private_readback']['actual']['dependency']['private_inputs']
    require(private_inputs and value['private_readback']['actual']['dependency']['shared_outputs_unchanged'] is True
            and value['private_readback']['actual']['additional_closure']['proof_data_and_elf_match'] is True,
            'complete original private dependency/DATA/ELF producer observations required')
    for name, row in private_inputs.items():
        if row['kind'] != 'file': continue
        matches = [pin for pin in by_path.values() if pin['path'].endswith('/private-sparklib/' + name)]
        require(len(matches) == 1 and all(matches[0][key] == row[key] for key in ('sha256', 'bytes', 'mode')),
                'actual full private dependency inventory/readback binding differs: ' + name)
        pin_bytes(matches[0])
    for key in ('source_readback', 'private_readback', 'generated_inventory'):
        # Original collector save outputs are retained separately from its
        # producer-tree inventory; their exact selector pins retain full bytes.
        require(Path(selected[key]['path']).parent == Path(selected['terminal']['path']).parent,
                'original collector output lineage differs')
    actions = [action for action in value['proposal']['launches'] if action['mode'] == selected['producer_mode']]
    require(len(actions) == 1, 'one genuinely enrolled relevant producer action required')
    action = actions[0]
    relevant = [row for row in terminal['records'] if row['mode'] == selected['producer_mode']]
    require(len(relevant) == 1, 'missing/unrun/unknown relevant Main producer is not eligible')
    record = relevant[0]; result = record['actual_result']; child = result['child_wait']
    require(record['path'] == str(Path(action['receipt']) / 'result.json')
            and hashlib.sha256(Path(record['path']).read_bytes()).hexdigest() == record['sha256']
            and exact_json(Path(record['path']).read_bytes()) == result,
            'actual original producer result raw bytes must match collector')
    require(child is not None and child['returncode'] == 0 and result['scope_wait'] == 0
            and result['inputs_unchanged'] is True and child['argv'] == action['child_argv'],
            'actual relevant original child/scope waits and input correspondence required')
    # Never require all_required_actual_pass or success of unrelated batch modes.
    scopes = [row for row in terminal['owned_scope_terminal_observations'] if row['unit'] == action['scope_unit']]
    require(len(scopes) == 1, 'exact relevant original owned scope observation required')
    scope = scopes[0]
    scope_custody(scope)
    children = [row for row in terminal['known_child_exit_evidence_and_current_pid_absence']
                if row['pid'] == child['pid']]
    require(len(children) == 1 and children[0]['original_exit_evidence'] == child
            and children[0]['proc_currently_exists'] is False, 'real known child exit/absence required')
    mappings = [row['mapping'] for row in value['outer_observations'] if row['mode'] == selected['producer_mode']]
    require(len(mappings) == 1 and len(mappings[0]['launched']) == 1,
            'one original actual outer-launch mapping required')
    launched = mappings[0]['launched'][0]
    require(launched['kind'] == 'ACTUAL_LAUNCHER_WAIT' and launched['actual_handshake_wait'] == 0
            and launched in mappings[0]['attempts'], 'actual original successful outer handshake wait required')
    for key in ('start', 'wait', 'binding', 'launch_claim', 'disposition', 'launcher_wait'):
        pin_bytes(launched[key])
    start = exact_json(pin_bytes(launched['start'])); outer_wait = exact_json(pin_bytes(launched['wait']))
    disposition = exact_json(pin_bytes(launched['disposition']))
    launcher_wait = exact_json(pin_bytes(launched['launcher_wait']))
    claim = exact_json(pin_bytes(launched['launch_claim']))
    require(start['argv'] == outer_wait['argv'] and start['pid'] == outer_wait['pid']
            and start['wrapper_pid'] == outer_wait['wrapper_pid']
            and outer_wait['actual_handshake_Popen_wait_returncode'] == 0
            and outer_wait['inputs_unchanged'] is True and outer_wait['retention_success'] is True
            and not outer_wait['retention_errors'], 'complete original outer raw custody required')
    require(disposition['action'] == claim['action'] == action and disposition['mode'] == selected['producer_mode']
            and claim['outer_capture_path'] == launched['folder']
            and launcher_wait['argv'] == action['launcher_argv'] and launcher_wait['returncode'] == 0,
            'actual selected action/launcher/disposition correspondence required')
    for pin in outer_wait['raw_files']: pin_bytes(pin)
    case = value['case_result']; produced = value['produce_result']; exported = value['export_request']
    require(case['schema'] == 'worldline.original-custody-live-case-result-v1'
            and case['failure'] is None and not case['still_owned_child_pids'],
            'actual original relevant campaign completion required')
    require(produced['schema'] == 'worldline.original-custody-full-production-v1'
            and exported['schema'] == 'worldline.original-custody-campaign-export-request-v1',
            'genuine complete original campaign producer/export request required')
    argv = action['child_argv']
    require('--entry' in argv and Path(argv[argv.index('--entry') + 1]).name == 'run_campaign.py'
            and '--stage' in argv and argv[argv.index('--stage') + 1] == 'produce'
            and '--plan' in argv and argv[argv.index('--plan') + 1] == case['original_plan'],
            'protected producer must actually be enclosed by the selected original wrapper')
    case_commands = [row for row in produced['records'] if row['case'] == case['case']]
    require(len(case_commands) == 1 and case_commands[0]['actual_wait'] == 0
            and case_commands[0]['argv'] in [row['argv'] for row in exported['original_case_commands']],
            'real campaign parent-child invocation/wait required')
    owner_rows = [row for row in case['records'] if row.get('pid') == frame['owner']['pid']]
    require(len(owner_rows) == 1, 'one actual original launched source OWNER required')
    owner = owner_rows[0]; birth = owner['owner_birth']
    require(owner['actual_wait'] == 0 and owner['argv'] == frame['original_argv']
            and owner['action']['request'] == frame['plan']['request']
            and owner['action']['early_envelope'] == frame['owner_source']['envelope_path']
            and owner['source_owner_retention'] == frame['plan']['retention_directory'],
            'actual public original OWNER invocation/wait/source selection required')
    for key in ('pid', 'start_tick', 'boot_hex', 'namespaces', 'exe', 'cmdline_hex', 'uid_map_hex', 'gid_map_hex'):
        require(birth[key] == frame['owner'][key], 'actual source OWNER birth correspondence differs: ' + key)
    require(hashlib.sha256(capture.read_bytes()).hexdigest() == owner['source_owner_archive_sha256']
            and library.read_bytes() == frame['native_mapping']['raw'],
            'exact actual completed capture and selected native full image required')
    for path in (capture, stdout, stderr):
        matches = [pin for pin in owner['source_owner_retained_files'] if pin['path'] == str(path)]
        require(len(matches) == 1, 'actual owner retained stream/archive custody required')
        pin_bytes({key: matches[0][key] for key in ('path', 'sha256', 'bytes', 'mode')})
        require(str(path) in exported['inventory'] and
                exported['inventory'][str(path)]['sha256'] == matches[0]['sha256'],
                'original fresh export input custody must include all owner/actor data')
    require(raw['owner_stdout'] == stdout.read_bytes() and owner['stdout'] == selected['owner_stdout']['path']
            and owner['stderr'] == selected['owner_stderr']['path']
            and owner['stdout_sha256'] == selected['owner_stdout']['sha256']
            and owner['stderr_sha256'] == selected['owner_stderr']['sha256'],
            'complete actual original owner public output correspondence required')
    marker = b'SOURCE_OWNER_FINAL_CLOSE '
    actor_stderr = stderr.read_bytes()
    require(raw['owner_stderr'].startswith(actor_stderr), 'owner did not retain complete original actor stderr')
    tail = raw['owner_stderr'][len(actor_stderr):]
    require(tail.startswith(marker) and tail.endswith(b'\n') and tail.count(b'\n') == 1,
            'actual final root close footer, not an inner partial capture, required')
    footer = exact_json(tail[len(marker):])
    require(footer == owner['source_owner_final_close'] and footer['owner_pid'] == frame['owner']['pid']
            and footer['child_pid'] == frame['child_pid'] and footer['actual_child_wait'] == 0
            and footer['inner_completed'] is True and not footer['errors'] and len(footer['closes']) == 2,
            'real complete actor/owner terminal custody correspondence required')
    require(all(row['call'] == 'close' and row['result'] == 0 and row['errno'] == 0
            and row['readback']['result'] == -1 and row['readback']['errno'] == 9 for row in footer['closes']),
            'actual final archive/directory close receipts required')
    return {'selection_sha256': hashlib.sha256(selection_path.read_bytes()).hexdigest(),
            'producer_mode': selected['producer_mode'], 'terminal': selected['terminal'],
            'release': selected['release'], 'owner_pid': frame['owner']['pid'], 'actor_pid': frame['child_pid'],
            'complete_raw_artifact_pins': selected,
            'actual_scope_observation': scope,
            'no_all_required_actual_pass_shortcut': True, 'phase_acceptance': False}


def run(capture, library, stdout, stderr, main_input_custody):
    records = list(retained_records(capture))
    baseline, raw, completed = completed_input(records)
    custody = main_custody(main_input_custody, baseline, capture, library, stdout, stderr)
    generated_controls = generated_custody_controls(main_input_custody)
    scope_controls = scope_custody_controls(custody)
    public = public_output(baseline, stdout.read_bytes(), stderr.read_bytes())
    selected = ctypes.CDLL(str(library.resolve(strict=True)), use_errno=True)
    native = selected.wl_excluded_source_owner_decide_v1
    native.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_uint64)]
    native.restype = ctypes.c_int

    def decide(value, control):
        encoded = archive(value)
        if ctypes.c_size_t(len(encoded)).value != len(encoded):
            raise ValueError('owned source extent is not representable')
        owned = (ctypes.c_ubyte * len(encoded)).from_buffer_copy(encoded)
        status = ctypes.c_uint64()
        transport = native(owned, len(encoded), ctypes.byref(status))
        digest = hashlib.sha256(encoded).hexdigest()
        # Emit each full owned input directly into Main's original framed raw
        # stdout; do not accumulate duplicate full source images in the summary.
        print(json.dumps({'schema': 'worldline.fixed-source-owner-native-control-input-v3',
                          'control': control, 'input_hex': encoded.hex(), 'input_bytes': len(encoded),
                          'input_sha256': digest, 'transport': transport, 'action': status.value},
                         sort_keys=True), flush=True)
        if transport != 0:
            raise AssertionError(('native transport failure', transport))
        return status.value, digest

    action, digest = decide(baseline, 'genuine-complete-owner-actor-main-baseline')
    if action != 3:
        raise AssertionError(('actual complete capture refused', action))
    rows = baseline['messages']
    actor_index = next(index for index, row in enumerate(rows) if row['message']['stage'] == 'ACTOR')
    negative = []

    def refused(name, change):
        altered = copy.deepcopy(baseline)
        change(altered)
        action, digest = decide(altered, name)
        if action != 0:
            raise AssertionError((name, 'counterexample accepted', action))
        negative.append({'control': name, 'action': action, 'input_sha256': digest})

    refused('unknown-wait', lambda value: value['terminal'].__setitem__('wait', None))
    refused('unknown-waitid-pid', lambda value: value['terminal']['waitid'].__setitem__('si_pid', 0))
    refused('nonterminal-pidfd', lambda value: value['terminal']['poll'].__setitem__('result', 0))
    refused('replaced-terminal-pidfd', lambda value: value['terminal']['pidfd_current'].__setitem__('inode',
             value['terminal']['pidfd_current']['inode'] + 1))
    refused('native-image-content-mismatch', lambda value: value['native_mapping'].__setitem__('raw',
             value['native_mapping']['raw'] + b'\0'))
    refused('native-symbol-outside-selected-image', lambda value: value['native_mapping'].__setitem__('symbol', 0))
    refused('root-final-envelope-mismatch', lambda value: value['owner_final_source'].__setitem__('envelope_bytes_hex', ''))
    refused('root-final-held-readback-mismatch', lambda value: value['owner_final_source']['file_readbacks'][0]['held_after'].__setitem__(
             'inode', value['owner_final_source']['file_readbacks'][0]['held_after']['inode'] + 1))
    refused('actor-final-check-failed', lambda value: message_changed(value, -1,
             lambda message: message['terminal'].__setitem__('final_check', False)))
    refused('actor-own-hook-flags-failed', lambda value: message_changed(value, actor_index,
             lambda message: message['source']['bootstrap_flags'].__setitem__('isolated', False)))
    refused('actor-projection-mismatch', lambda value: message_changed(value, actor_index,
             lambda message: message['source'].__setitem__('envelope_bytes_hex', '')))
    refused('actor-source-events-removed', lambda value: message_changed(value, actor_index,
             lambda message: message['source'].__setitem__('events', [])))
    refused('actor-start-epoch-mismatch', lambda value: value['messages'][actor_index]['kernel'].__setitem__('start_tick',
             value['messages'][actor_index]['kernel']['start_tick'] + 1))
    refused('actor-namespace-mismatch', lambda value: value['messages'][actor_index]['kernel'].__setitem__('namespaces', {}))
    refused('actor-groups-mismatch', lambda value: message_changed(value, actor_index,
             lambda message: message.__setitem__('groups', message['groups'] + [message['resgid'][0]])))
    refused('actor-saved-uid-not-dropped', lambda value: message_changed(value, actor_index,
             lambda message: message['resuid'].__setitem__(2, 0)))
    refused('actor-real-message-credentials-mismatch', lambda value: value['messages'][actor_index]['receive'].__setitem__('sender',
             struct.pack('@iII', value['owner']['pid'], value['request']['uid'], value['request']['gid'])))
    refused('message-ancillary-truncation', lambda value: value['messages'][actor_index]['receive'].__setitem__('flags', 8))
    refused('message-unsealed-source', lambda value: value['messages'][actor_index].__setitem__('message_seals', 0))
    refused('root-created-target-peer', lambda value: value['target']['descriptor'].__setitem__('uid', 0))
    refused('target-ofd-not-shared', lambda value: value['target']['kcmp'].__setitem__('result', 1))
    refused('target-native-close-unknown', lambda value: value['target'].__setitem__('close', None))
    refused('target-close-readback-not-ebadf', lambda value: value['target']['close']['readback'].__setitem__('errno', 0))
    refused('target-message-credentials-mismatch', lambda value: value['target']['receive'].__setitem__('sender',
             struct.pack('@iII', value['owner']['pid'], value['request']['uid'], value['request']['gid'])))
    refused('endpoint-replaced-after-capability-open', lambda value: value['endpoint_current'].__setitem__('inode',
             value['endpoint_current']['inode'] + 1))
    refused('complete-stdout-content-truncated', lambda value: value['terminal']['stdout'].__setitem__('raw',
             value['terminal']['stdout']['raw'][:-1]))
    refused('incomplete-stderr-readback', lambda value: value['terminal']['stderr'].__setitem__('readback',
             value['terminal']['stderr']['readback'] + b'\0'))
    refused('native-image-not-enrolled-named-object', lambda value: value['native_mapping']['named'].__setitem__(
            'inode', value['native_mapping']['named']['inode'] + 1))
    refused('native-map-inode-differs-from-source-held-object', lambda value: value['native_mapping']['maps'][0]['identity'].__setitem__(
            'inode', value['native_mapping']['maps'][0]['identity']['inode'] + 1))
    refused('native-map-device-token-mismatch', lambda value: value['native_mapping']['maps'][0].__setitem__(
            'device_minor', value['native_mapping']['maps'][0]['device_minor'] + 1))
    refused('native-map-offset-token-mismatch', lambda value: value['native_mapping']['maps'][0].__setitem__(
            'offset', value['native_mapping']['maps'][0]['offset'] + 1))
    refused('owner-start-sentinel-not-a-birth', lambda value: value['owner'].__setitem__('start_tick', -1))
    refused('owner-raw-stat-missing', lambda value: value.__setitem__('owner_origin_stat', b''))
    refused('actor-kernel-raw-stat-missing', lambda value: value['messages'][actor_index].__setitem__('kernel_stat', b''))
    def sentinel_actor(value):
        value['messages'][actor_index]['kernel']['start_tick'] = -1
        message_changed(value, actor_index, lambda message: message['actor'].__setitem__('start_tick', -1))
    refused('matching-invalid-actor-and-kernel-start-sentinels', sentinel_actor)
    refused('carrier-creator-not-actual-root-owner', lambda value: value['owner_channel_capture']['peercred'].__setitem__(
            'raw', struct.pack('@iII', value['child_pid'], value['request']['uid'], value['request']['gid'])))
    refused('creator-peer-does-not-replace-actual-scm-sender', lambda value: message_changed(value, actor_index,
            lambda message: message.__setitem__('carrier_peer_hex',
                struct.pack('@iII', value['child_pid'], value['request']['uid'], value['request']['gid']).hex())))
    def invalid_message_descriptor(value):
        row = value['messages'][actor_index]
        row['message_descriptor']['fd'] = -1
        row['receive']['args']['rights'] = [-1]
        raw = struct.pack('@i', -1)
        row['receive']['rights'] = raw
        row['receive']['controls'] = [
            (level, kind, raw if level == 1 and kind == 1 else body)
            for level, kind, body in row['receive']['controls']]
    refused('matching-negative-received-message-descriptor-and-scm-rights', invalid_message_descriptor)
    for name, receipt in (('message', lambda value: value['messages'][actor_index]['receive']),
                          ('target', lambda value: value['target']['receive'])):
        refused(name + '-receive-negative-carrier-fd',
                lambda value, receipt=receipt: receipt(value).__setitem__('fd', -1))
        refused(name + '-receive-not-held-owner-carrier-fd',
                lambda value, receipt=receipt: receipt(value).__setitem__(
                    'fd', value['owner_channel_capture']['fd'] + 1))
        refused(name + '-receive-source-missing',
                lambda value, receipt=receipt: receipt(value).__setitem__('source', None))
    refused('creator-fstat-call-failed-with-unchanged-identity',
            lambda value: value['owner_channel_capture']['fstat'].update(result=-1, errno=9))
    refused('creator-fstat-not-held-carrier-fd',
            lambda value: value['owner_channel_capture']['fstat'].__setitem__('fd', -1))
    refused('creator-fstat-args-not-held-carrier-fd',
            lambda value: value['owner_channel_capture']['fstat']['args'].__setitem__('fd', -1))
    refused('creator-fstat-source-missing',
            lambda value: value['owner_channel_capture']['fstat'].__setitem__('source', None))
    # Mutate only the target fstat receipt: retain its genuine identity, carrier,
    # post-drop actor, peer, endpoint, OFD and every other completed-input fact.
    refused('target-fstat-call-missing',
            lambda value: value['target']['capture']['fstat'].pop('call'))
    refused('target-fstat-call-not-fstat',
            lambda value: value['target']['capture']['fstat'].__setitem__('call', 'getpeername'))
    refused('target-fstat-fd-missing',
            lambda value: value['target']['capture']['fstat'].pop('fd'))
    refused('target-fstat-negative-fd-with-unchanged-identity',
            lambda value: value['target']['capture']['fstat'].__setitem__('fd', -1))
    refused('target-fstat-not-held-target-fd',
            lambda value: value['target']['capture']['fstat'].__setitem__(
                'fd', value['owner_channel_capture']['fd']))
    refused('target-fstat-args-missing',
            lambda value: value['target']['capture']['fstat'].pop('args'))
    refused('target-fstat-args-fd-missing',
            lambda value: value['target']['capture']['fstat']['args'].pop('fd'))
    refused('target-fstat-args-negative-fd-with-unchanged-identity',
            lambda value: value['target']['capture']['fstat']['args'].__setitem__('fd', -1))
    refused('target-fstat-args-not-held-target-fd',
            lambda value: value['target']['capture']['fstat']['args'].__setitem__(
                'fd', value['owner_channel_capture']['fd']))
    refused('target-fstat-source-field-missing',
            lambda value: value['target']['capture']['fstat'].pop('source'))
    refused('target-fstat-source-null',
            lambda value: value['target']['capture']['fstat'].__setitem__('source', None))
    target_source = archive(baseline['target']['capture']['source'])
    other_owner_source = next((source for source in (
        baseline['owner_source'], baseline['owner_final_source'],
        baseline['owner_channel_capture']['source'], baseline['pidfd_open']['source'])
        if archive(source) != target_source), None)
    if other_owner_source is None:
        raise ValueError('target fstat source substitution needs a distinct genuine qualified owner snapshot')
    # The successful native baseline already qualifies these original owner
    # snapshots; never fabricate an alternative or silently skip this witness.
    refused('target-fstat-source-not-at-call-qualified-owner',
            lambda value: value['target']['capture']['fstat'].__setitem__(
                'source', copy.deepcopy(other_owner_source)))
    refused('target-fstat-failed-with-unchanged-identity',
            lambda value: value['target']['capture']['fstat'].update(result=-1, errno=9))
    refused('target-fstat-errno-mismatch-with-unchanged-identity',
            lambda value: value['target']['capture']['fstat'].__setitem__('errno', 9))
    refused('pidfd-open-source-missing',
            lambda value: value['pidfd_open'].__setitem__('source', None))
    refused('pidfd-open-source-envelope-mismatch',
            lambda value: value['pidfd_open']['source'].__setitem__('envelope_bytes_hex', ''))
    for name, close in (('target', lambda value: value['target']['close']),
                        ('stdout-writer', lambda value: value['output_origins']['stdout']['writer_close']),
                        ('stderr-writer', lambda value: value['output_origins']['stderr']['writer_close'])):
        refused(name + '-close-source-missing',
                lambda value, close=close: close(value).__setitem__('source', None))
        refused(name + '-close-ebadf-readback-source-missing',
                lambda value, close=close: close(value)['readback'].__setitem__('source', None))
        refused(name + '-close-ebadf-readback-source-envelope-mismatch',
                lambda value, close=close: close(value)['readback']['source'].__setitem__('envelope_bytes_hex', ''))
    for name in ('stdout', 'stderr'):
        refused(name + '-writer-at-call-source-missing',
                lambda value, name=name: value['output_origins'][name].__setitem__('writer_close_source', None))
    refused('projection-initial-full-readback-mismatch', lambda value: value['projection_readback'].__setitem__('readback_hex', ''))
    refused('projection-current-full-readback-mismatch', lambda value: value['projection_current_readback'].__setitem__('raw_hex', ''))
    refused('projection-current-nonregular-descriptor', lambda value: value['projection_current_readback']['before'].__setitem__(
            'mode', stat.S_IFSOCK | 0o600))
    refused('actor-own-projection-full-readback-mismatch', lambda value: message_changed(value, actor_index,
            lambda message: message['source']['projection_readback'].__setitem__('readback_hex', '')))
    refused('negative-real-pidfd-number', lambda value: value['pidfd'].__setitem__('fd', -1))
    refused('actual-pidfd-open-result-not-held-descriptor', lambda value: value['pidfd_open'].__setitem__(
            'result', value['pidfd']['fd'] + 1))
    refused('actor-carrier-non-socket', lambda value: message_changed(value, actor_index,
            lambda message: message['channel'].__setitem__('mode', stat.S_IFREG | 0o600)))
    refused('pidfd-duplicate-not-same-open-file-description', lambda value: value['pidfd_ofd_current']['kcmp'].__setitem__('result', 1))
    refused('pre-reap-pidfd-no-longer-live', lambda value: value['terminal']['waitid_receipt']['before_reap']['pidfd'].__setitem__(
            'fdinfo', b'Pid:\t-1\n'))
    refused('pre-reap-raw-child-birth-missing', lambda value: value['terminal']['waitid_receipt']['before_reap'].__setitem__(
            'kernel_stat', b''))
    refused('waitid-not-wnowait', lambda value: value['terminal']['waitid_receipt']['args'].__setitem__('options', 4))
    refused('waitid-real-api-result-differs', lambda value: value['terminal']['waitid_receipt']['api_result'].__setitem__('si_pid', 0))
    refused('reap-wrong-actual-child', lambda value: value['terminal']['reap'].__setitem__(
            'api_result', (value['child_pid'] + 1, 0)))
    refused('post-reap-pidfd-malformed-sentinel', lambda value: value['terminal']['pidfd_current'].__setitem__(
            'fdinfo', b'Pid:\tunknown\n'))
    refused('post-reap-ofd-differs', lambda value: value['terminal']['post_reap_ofd']['kcmp'].__setitem__('result', 1))
    def watch_event(value, mask, wd=None):
        part = next(part for part in value['terminal']['watch_parts'] if part['result'] > 0)
        actual_wd = struct.unpack_from('=i', part['raw'])[0]
        part.update(raw=struct.pack('=iIII', actual_wd if wd is None else wd, mask, 0, 0), result=16, errno=0)
    for name, mask in (('inotify-overflow', 0x4000), ('inotify-ignored-watch', 0x8000),
                       ('inotify-unmounted-watch', 0x2000), ('inotify-deleted-output', 0x400),
                       ('inotify-moved-output', 0x800)):
        refused(name, lambda value, mask=mask: watch_event(value, mask))
    refused('inotify-unenrolled-watch-descriptor', lambda value: watch_event(value, 2, -1))
    refused('inotify-queue-empty-was-unknown-error', lambda value: value['terminal']['watch_parts'][-1].__setitem__('errno', 5))
    refused('inotify-incomplete-raw-header', lambda value: value['terminal']['watch_parts'][0].update(
            raw=b'\0', result=1, errno=0))
    refused('output-fsync-real-call-failed', lambda value: value['terminal']['stdout']['fsync'].update(result=-1, errno=5))
    refused('output-full-pread-receipt-truncated', lambda value: value['terminal']['stdout']['reads'][0].__setitem__('raw', b''))
    refused('output-read-eof-not-actually-observed', lambda value: value['terminal']['stdout']['parts'][-1].update(
            raw=None, result=-1, errno=5))
    refused('missing-private-source-topology', lambda value: value.__setitem__('private_source_topology', []))
    refused('root-owner-heap-readable', lambda value: value['owner_memory_get'].__setitem__('result', 1))
    refused('root-owner-memory-exclusion-unavailable', lambda value: value['owner_memory_set'].update(result=-1, errno=38))
    refused('root-owner-memory-call-birth-missing', lambda value: value['owner_memory_get'].__setitem__('caller_stat', b''))
    custody_negative = []
    def incomplete(name, change):
        altered = copy.deepcopy(records)
        change(altered)
        try: completed_input(altered)
        except (ValueError, KeyError, TypeError): custody_negative.append(name)
        else: raise AssertionError((name, 'partial/failed custody baseline admitted'))
    incomplete('inner-native-result-only', lambda value: value.pop())
    incomplete('real-post-call-source-check-missing', lambda value: value[-1]['value']['native_call'].__setitem__('post_source', None))
    incomplete('root-finally-source-check-missing', lambda value: value[-1]['value'].__setitem__('owner_final_source', None))
    incomplete('actual-owner-cleanup-missing', lambda value: value[-1]['value'].__setitem__('cleanup', []))
    incomplete('unknown-owned-child-after-stop', lambda value: value[-1]['value'].__setitem__('stop_wait', [{'unknown_owned_child': baseline['child_pid']}]))
    incomplete('actual-actor-terminal-wait-unknown', lambda value: value[-1]['value']['frame']['terminal'].__setitem__('wait', None))
    incomplete('reopened-archive-after-owner-completion', lambda value: value.append({'kind': 'FAILURE', 'value': {'error': 'retained'}}))
    return {'schema': 'worldline.fixed-source-owner-native-consumer-controls-v3',
            'capture_sha256': hashlib.sha256(capture.read_bytes()).hexdigest(),
            'library_sha256': hashlib.sha256(library.read_bytes()).hexdigest(),
            'positive': {'action': 3, 'input_sha256': digest}, 'negative': negative,
            'actual_main_input_custody': custody,
            'actual_generated_custody_controls': generated_controls,
            'actual_scope_custody_controls': scope_controls,
            'partial_owner_custody_refused': custody_negative,
            'actual_owner_completion_and_cleanup': completed['cleanup'],
            'public_original_client': public,
            'actor_execution_performed_by_this_control': False, 'phase_acceptance': False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--capture', required=True, type=Path)
    parser.add_argument('--library', required=True, type=Path)
    parser.add_argument('--stdout', required=True, type=Path)
    parser.add_argument('--stderr', required=True, type=Path)
    parser.add_argument('--main-input-custody', required=True, type=Path)
    arguments = parser.parse_args()
    print(json.dumps(run(arguments.capture, arguments.library, arguments.stdout, arguments.stderr,
                         arguments.main_input_custody), sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
