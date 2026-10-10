"""Main-only data collection and custody release for the exact interrupted O2.

The frozen original collector still refuses its absent outer-child-wait.json.
This separate recovery never supplies that artifact, infers a Popen wait, imports
an original target/helper, launches/stops a process, or establishes acceptance.
"""
from pathlib import Path
import argparse
import datetime
import fcntl
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
P = Path(__file__).resolve().parent
C = P.parent / 'ordinary-successor-v67-draft-v2/candidate'
WINDOW = Path('/home/sicarii/Documents/Codex/2026-09-30/how-do-u-feel-about-the/work/worldline-build-proof-window.json')
HOLDER = '01a1149d-db62-74b0-a5f7-b0239f285c44'
AUTHOR = 'F67OrdinaryFrameOwner'
REVIEWER = 'F67OrdinarySourceReview'
MODEL = 'openai-codex/gpt-6.1-sol:max'
DISPOSITION = 'QUALIFIED_DATA_ONLY_DEAD_OWNER_COLLECTION'
MAX_AGE = datetime.timedelta(minutes=30)
SOURCE_OUTPUTS = ('bin', 'explicit-recovery-marker-tests/bin', 'explicit-recovery-marker-tests/obj',
                  'lib', 'obj', 'protocol-adapter-tests/bin', 'protocol-adapter-tests/obj',
                  'recovery-protocol-tests/bin', 'recovery-protocol-tests/obj', 'resource-tests/bin',
                  'resource-tests/obj', 'use-reservation-tests/bin', 'use-reservation-tests/obj',
                  'wire-initialization-tests/bin', 'wire-initialization-tests/obj')
PRIVATE_OUTPUTS = ('lib/gnat/sparklib_obj', 'lib/gnat/sparklib_lib', 'lib/gnat/proof')
MUTABLE_DIRS = ('evidence', 'native-artifacts', 'review/root-live-lane-v1/attempts',
                'review/root-outer-capture-v1',
                'review/root-source-binding-adoption-v1/full-read-only-readiness',
                'review/root-source-binding-adoption-v1/final-reservation-live-observation')
MUTABLE_FILES = ('review/root-source-binding-adoption-v1/adoption.json',
                 'review/root-batch-terminal-v1/owned-terminal-observations.json',
                 'review/root-batch-terminal-v1/outer-capture-observations.json',
                 'review/root-batch-terminal-v1/complete-source-readback.json',
                 'review/root-batch-terminal-v1/fresh-terminal-live-sample.json',
                 'review/root-batch-terminal-v1/retained-artifacts.json',
                 'review/root-batch-terminal-v1/actual-results-and-window-release.json',
                 'review/root-batch-terminal-v1/coordination-release.json',
                 'review/root-batch-terminal-v1/private-source-dependency-readback.json',
                 'review/root-batch-terminal-v1/owned-generated-output-inventory.json')
ENV = dict(os.environ, XDG_RUNTIME_DIR='/run/user/1000',
           DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/1000/bus')


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def now():
    return datetime.datetime.now(datetime.timezone.utc)


def fields(value):
    return (value.st_dev, value.st_ino, value.st_mode, value.st_nlink,
            value.st_size, value.st_mtime_ns, value.st_ctime_ns)


def canonical(path):
    path = Path(path)
    require(path.is_absolute() and path.resolve(strict=True) == path,
            'Absolute canonical non-symlink path required: ' + str(path))
    return path


def file_record(path, header=False):
    path = canonical(path)
    before = path.lstat()
    require(stat.S_ISREG(before.st_mode), 'Not a regular file: ' + str(path))
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    digest = hashlib.sha256()
    prefix = b''
    try:
        require(fields(os.fstat(descriptor)) == fields(before), 'Named/held file differs')
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            if len(prefix) < 64:
                prefix += chunk[:64 - len(prefix)]
            digest.update(chunk)
        require(fields(os.fstat(descriptor)) == fields(before), 'Held file changed')
        require(fields(path.lstat()) == fields(before), 'Named file changed')
    finally:
        os.close(descriptor)
    result = {'path': str(path), 'sha256': digest.hexdigest(),
              'bytes': before.st_size, 'mode': stat.S_IMODE(before.st_mode)}
    if header:
        result['header_first_64_bytes_hex'] = prefix.hex()
    return result


def matched(row):
    require(isinstance(row, dict) and set(row) == {'path', 'sha256', 'bytes', 'mode'},
            'Exact four-field pin required')
    require(file_record(row['path']) == row, 'Exact pinned file changed: ' + str(row['path']))
    return Path(row['path'])


def no_duplicates(pairs):
    value = {}
    for name, member in pairs:
        require(name not in value, 'Duplicate JSON field: ' + name)
        value[name] = member
    return value


def invalid_constant(value):
    raise ValueError('Non-JSON constant: ' + value)


def load(path):
    path = canonical(path)
    prior = file_record(path)
    value = json.loads(path.read_bytes(), object_pairs_hook=no_duplicates,
                       parse_constant=invalid_constant)
    require(file_record(path) == prior, 'JSON changed during read: ' + str(path))
    return value


def descriptor(row):
    return {key: row[key] for key in ('sha256', 'bytes', 'mode')}


def under(name, roots):
    return any(name == root or name.startswith(root + '/') for root in roots)


def snapshot(root, excluded_dirs=(), excluded_files=(), allow_links=False, headers=False):
    root = Path(root)
    if allow_links and root.is_symlink():
        require(root.is_absolute() and root.parent.resolve(strict=True) == root.parent,
                'Output symlink parent must be canonical; never follow its target')
    else:
        root = canonical(root)
    rows = {}
    def visit(path):
        name = path.relative_to(root).as_posix()
        before = path.lstat()
        mode = stat.S_IMODE(before.st_mode)
        if name in excluded_dirs:
            require(stat.S_ISDIR(before.st_mode), 'Excluded output is not a real directory')
            return
        if name in excluded_files:
            require(stat.S_ISREG(before.st_mode), 'Mutable record is not a regular file')
            return
        if stat.S_ISDIR(before.st_mode):
            rows[name] = {'kind': 'directory', 'mode': mode}
            for child in sorted(path.iterdir()):
                visit(child)
        elif stat.S_ISREG(before.st_mode):
            record = file_record(path, headers)
            rows[name] = {'kind': 'file', **descriptor(record)}
            if headers:
                rows[name]['header_first_64_bytes_hex'] = record['header_first_64_bytes_hex']
        elif allow_links and stat.S_ISLNK(before.st_mode):
            target = os.readlink(path)
            rows[name] = {'kind': 'symlink', 'mode': mode, 'target': target}
            if headers:
                raw = os.fsencode(target)
                rows[name].update(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
        elif allow_links:
            rows[name] = {'kind': 'special', 'mode': mode,
                          'file_type': stat.S_IFMT(before.st_mode),
                          'device': before.st_rdev}
        else:
            raise RuntimeError('Unadmitted link/special input: ' + str(path))
        require(fields(before) == fields(path.lstat()), 'Changed during traversal: ' + str(path))
    visit(root)
    return rows


def save_new(directory, name, value):
    path = directory / name
    raw = (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False,
                      allow_nan=False) + '\n').encode('utf-8')
    descriptor_fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                            os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    with os.fdopen(descriptor_fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    return file_record(path)


def source_receiver(inputs):
    manifest_path = matched(inputs['source_manifest'])
    require(manifest_path == P / 'source-pins.json', 'Different recovery source manifest')
    manifest = load(manifest_path)
    expected = manifest['files']
    actual = snapshot(P, ('Main-owned-inputs', 'Main-owned-collections'), ('source-pins.json',))
    actual_files = {name: descriptor(row) for name, row in actual.items() if row['kind'] == 'file'}
    require(actual_files == expected, 'Complete recovery author keyset/content/mode drift')
    review = load(matched(inputs['independent_review']))
    require(review['author'] == AUTHOR and review['reviewer'] == REVIEWER and AUTHOR != REVIEWER,
            'Original independent reviewer and actual helper author required')
    require(review['actual_model_selection'] == MODEL and review['disposition'] == DISPOSITION,
            'Wrong actual model or authorized data-only dead-owner review scope')
    require(review['blocking_findings'] == [] and review['target_execution'] is False and
            review['phase_acceptance'] is False, 'Review does not qualify data-only source')
    require(review['source_manifest'] == inputs['source_manifest'] and review['files'] == expected,
            'Review does not bind every exact recovery author object')
    require(review['candidate'] == str(C) and review['original_receiver_author'] == 'Main' and
            review['underlying_source_author'] == 'SolPhaseOneIntegration', 'Authorship/receiver drift')
    model = load(matched(review['model_provenance']))
    require(model['resolvedModelIdentity'] == 'openai-codex/gpt-6.1-sol' and
            model['resolvedThinkingLevel'] == 'max' and model['fallback_used'] is False and
            model['speed_priority'] == 'none' and model['reviewer'] == REVIEWER,
            'Genuine original reviewer model companion required')
    contract = load(P / 'recovery-contract.json')
    require(review['retained_original_pins'] == contract['retained_original_pins'],
            'Original full receiving scope/pins not carried')
    for row in contract['retained_original_pins'].values():
        matched(row)
    refusal = contract['original_collector_refusal']
    capture = load(matched(refusal['complete_actual_tool_event_capture']))
    failures = [row for row in capture['complete_tool_result_events'] if row['id'] == refusal['event_id']]
    require(len(failures) == 1, 'Original actual collector refusal event is not uniquely retained')
    message = failures[0]['message']
    text = '\n'.join(row.get('text', '') for row in message['content'] if row.get('type') == 'text')
    require(message['toolName'] == 'bash' and message['details']['exitCode'] == 1 and
            all(value in text for value in refusal['exact_failure_fragments']),
            'Original collector refusal changed; never substitute recovery success')
    require(inputs['candidate'] == str(C) and inputs['observer'] == 'Main' and
            inputs['operation'] == 'collect-partial-ownership-and-release-custody' and
            inputs['phase_acceptance'] is False, 'Main-only exact custody operation required')
    require(inputs['expected_window'] == contract['reserved_window'], 'Original reserved preimage differs')
    require(inputs['actual_runtime_and_routing_binding'] == contract['current_runtime_binding'],
            'Must retain actual OMP18.8.7 binding, not old OMP18.8.0 correspondence')
    return manifest, contract


def fresh_goal(inputs, contract):
    stage_path = matched(inputs['stage_goal_observation'])
    evidence_roots = (C / 'evidence', P / 'Main-owned-inputs')
    require(any(stage_path.is_relative_to(root) for root in evidence_roots),
            'Fresh Main stage must be retained in the exact candidate/recovery evidence namespace')
    observation = load(stage_path)
    require(observation['schema'] == 'worldline-current-controller-stage-observation-v1' and
            observation['stage'] == 'collect' and observation['candidate'] == str(C),
            'Separate genuine current collect-stage observation required')
    require(observation['required_window_holder'] == HOLDER and
            observation['no_goal_mutation'] is True and observation['no_phase_acceptance'] is True,
            'Original holder and nonmutation/nonacceptance fields required')
    require('goalToolObservation' not in observation, 'Native id must never become a legacy threadId')
    require(observation['actual_runtime_and_routing_binding'] == contract['current_runtime_binding'],
            'Current actual Main source/runtime binding differs')
    runtime = load(matched(contract['current_runtime_binding']))
    require(runtime['actual_current_controller_identity'] == contract['current_native_goal'] and
            runtime['actual_main_model'] == MODEL and runtime['original_goal_objective_or_gate_hash_changed'] is False,
            'Actual current controller or fixed original objective differs')
    require(runtime['historical_OMP18_8_0_correspondence_claimed'] is False,
            'Old runtime correspondence cannot be relabelled')
    matched(runtime['actual_runtime'])
    native_path = matched(observation['nativeGoalToolObservation'])
    require(any(native_path.is_relative_to(root) for root in evidence_roots),
            'Native Main record outside retained stage evidence')
    native = load(native_path)
    require(native['observer'] == 'Main' and native['source_tool'] == 'functions.goal' and
            native['arguments'] == {'op': 'get'} and native['actual_response']['details']['op'] == 'get',
            'Actual native get record required, not an RPC substitute or authored goal')
    require(native['candidate'] == str(C) and native['stage'] == 'collect' and
            native['required_window_holder'] == HOLDER and native['no_phase_acceptance'] is True,
            'Native stage/candidate/holder differs')
    goal = native['actual_response']['details']['goal']
    require('threadId' not in goal and goal['status'] == 'active' and
            {name: goal[name] for name in ('id', 'objective', 'createdAt')} == contract['current_native_goal'],
            'Same exact active native goal required; original paused holder is not resumed')
    clock_record = observation['clockToolObservation']
    require(clock_record['source_tool'] == 'functions.bash' and
            clock_record['command'] == "/usr/bin/date -u '+%Y-%m-%d %H:%M:%S UTC'",
            'Original supported direct UTC clock record required')
    clock = datetime.datetime.strptime(clock_record['current_time'], '%Y-%m-%d %H:%M:%S UTC').replace(tzinfo=datetime.timezone.utc)
    require(clock_record['actual_response']['text'].startswith(clock_record['current_time'] + '\n'),
            'Clock field not joined to actual Main response')
    recorded = datetime.datetime.fromisoformat(native['recorded_at'].replace('Z', '+00:00'))
    require(recorded.tzinfo is not None and recorded.utcoffset() == datetime.timedelta(0),
            'Actual native get must have UTC timestamp')
    at = now()
    require(datetime.timedelta(0) <= at - clock <= MAX_AGE and
            datetime.timedelta(0) <= at - recorded <= MAX_AGE and abs(clock - recorded) <= MAX_AGE,
            'Original thirty-minute native get/clock freshness gate failed')
    return {'stage_observation': inputs['stage_goal_observation'],
            'native_observation': observation['nativeGoalToolObservation'],
            'clockToolObservation': clock_record, 'current_native_goal': contract['current_native_goal'],
            'original_holder_status': 'historically_paused_not_resumed', 'goal_mutation': False}


def frame_readback(contract):
    frozen = load(matched(contract['retained_original_pins']['frozen_frame']))
    require(len(frozen['files']) == 84 and len(frozen['immutable_snapshot']) == 235,
            'Do not narrow original84/235 receiving scope')
    for name, expected in frozen['files'].items():
        path = C / name
        require(path.is_relative_to(C) and '..' not in Path(name).parts and not Path(name).is_absolute(),
                'Invalid frozen relative input')
        require(descriptor(file_record(path)) == expected, 'Original frozen input changed: ' + name)
    actual_frame = snapshot(C, ('source',) + tuple('private-sparklib/' + name for name in PRIVATE_OUTPUTS) + MUTABLE_DIRS,
                            ('author-freeze.json',) + MUTABLE_FILES)
    require(actual_frame == frozen['immutable_snapshot'], 'Full original235 immutable shape drift')
    source_expected = load(C / 'selected-source-entries.json')
    source_expected = {name: row for name, row in source_expected.items() if not under(name, SOURCE_OUTPUTS)}
    source_actual = snapshot(C / 'source', SOURCE_OUTPUTS)
    require(source_actual == source_expected, 'Original full source types/dirs/modes/bytes/sha/keyset drift')
    plan = load(C / 'dependency-inventory.json')
    require(plan['private_root'] == str(C / 'private-sparklib') and
            plan['output_directories'] == list(PRIVATE_OUTPUTS) and plan['source_mode'] == 'full' and
            plan['compiler_mode'] == 'Production' and plan['library_kind'] == 'static' and
            plan['proof_only_substitution'] is False and plan['GPR_TOOL_override'] is False,
            'Original full Production static private dependency contract differs')
    private_actual = snapshot(C / 'private-sparklib', PRIVATE_OUTPUTS)
    require(private_actual == plan['entries'] and len(private_actual) == 141,
            'Complete original private141 input drift')
    installed = canonical(plan['installed_root'])
    installed_entries = {'.': {'kind': 'directory', 'mode': stat.S_IMODE(installed.lstat().st_mode)}}
    for name in ('include', 'lib', 'lib/gnat'):
        path = canonical(installed / name)
        require(path.is_dir(), 'Installed dependency ancestor is not a real directory')
        installed_entries[name] = {'kind': 'directory', 'mode': stat.S_IMODE(path.lstat().st_mode)}
    for name, row in snapshot(installed / 'include/spark').items():
        installed_entries['include/spark' + ('' if name == '.' else '/' + name)] = row
    for name in ('lib/gnat/sparklib.gpr', 'lib/gnat/sparklib_common.gpr'):
        installed_entries[name] = {'kind': 'file', **descriptor(file_record(installed / name))}
    require(installed_entries == plan['entries'], 'Original installed/private source correspondence drift')
    shared = {name: snapshot(installed / name, allow_links=True) if (installed / name).exists() else None
              for name in PRIVATE_OUTPUTS}
    require(shared == plan['shared_output_inventory'], 'Original shared output inventory drift; no rebaseline')
    proposal = load(C / 'reviewed-launch-proposal.json')
    planned = load(C / 'planned-actions.json')
    additional = load(C / 'additional-actions.json')
    require(len(planned) == 116 and len(additional) == 2 and len(proposal['launches']) == 118 and
            proposal['launches'] == planned + additional, 'Exact original116 plus distinct2 roster differs')
    require([row['mode'] for row in planned[:5]] == contract['original_first_five'] and
            len({row['mode'] for row in proposal['launches']}) == 118 and
            len({row['scope_unit'] for row in proposal['launches']}) == 118,
            'First-five, scope or mode correspondence differs')
    generated_names = tuple('source/' + name for name in SOURCE_OUTPUTS) + tuple('private-sparklib/' + name for name in PRIVATE_OUTPUTS)
    generated = {name: snapshot(C / name, allow_links=True, headers=True) if (C / name).exists() else None
                 for name in generated_names}
    return {'immutable_frame': actual_frame, 'source_inputs': source_actual,
            'private_inputs': private_actual, 'installed_source_inputs': installed_entries,
            'shared_outputs': shared, 'generated_outputs': generated,
            'source_private_frame_matches': True, 'acceptance': False}, proposal['launches']


def invoke(argv):
    result = subprocess.run(argv, env=ENV, capture_output=True, text=True, timeout=30, check=False)
    return {'command': argv, 'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}


def scope_observations(actions):
    rows = []
    for action in actions:
        unit = action['scope_unit']
        require(re.fullmatch(r'codex-worldline-ordinary-source-v67-v2-[A-Za-z0-9_.-]+\.scope', unit),
                'Different or malformed owned unit')
        observation = invoke(['/usr/bin/systemctl', '--user', 'show', unit] +
                             [value for key in ('LoadState', 'ActiveState', 'SubState', 'MainPID', 'ControlPID', 'ControlGroup', 'Result') for value in ('-p', key)])
        properties = dict(line.split('=', 1) for line in observation['stdout'].splitlines() if '=' in line)
        group = properties.get('ControlGroup', '')
        require(not group or (group.startswith('/') and '..' not in Path(group).parts), 'Invalid cgroup path')
        cgroup = Path('/sys/fs/cgroup') / group.lstrip('/') if group else None
        exists = cgroup.exists() if cgroup is not None else False
        processes = None
        readable = True
        if exists:
            processes_file = cgroup / 'cgroup.procs'
            readable = processes_file.is_file() and not processes_file.is_symlink()
            if readable:
                processes = processes_file.read_text().split()
        terminal = (observation['returncode'] == 0 and not observation['stderr'].strip() and
                    properties.get('LoadState') in ('loaded', 'not-found') and
                    properties.get('ActiveState') in ('inactive', 'failed') and
                    properties.get('SubState') in ('dead', 'failed') and
                    all(properties[key] == '0' for key in ('MainPID', 'ControlPID') if key in properties) and
                    readable and not processes)
        rows.append({'mode': action['mode'], 'unit': unit, 'observation': observation,
                     'properties': properties, 'cgroup': {'path': str(cgroup) if cgroup else None,
                     'exists': exists, 'processes': processes, 'readable': readable},
                     'owned_scope_inactive_or_failed_and_cgroup_empty_or_absent': terminal})
    return {'at': now().isoformat(), 'required_scope_count': 118, 'scopes': rows,
            'all_owned_scopes_terminal_empty': len(rows) == 118 and all(row['owned_scope_inactive_or_failed_and_cgroup_empty_or_absent'] for row in rows)}


def owned_records(actions, contract):
    known = []
    records = []
    unknown = []
    missing_results = []
    def add(pid, role, evidence, argv=None):
        require(type(pid) is int and pid > 0, 'Owned process identity not recorded: ' + role)
        known.append({'pid': pid, 'role': role, 'evidence': evidence, 'original_argv': argv})
    by_mode = {action['mode']: action for action in actions}
    for action in actions:
        receipt = Path(action['receipt'])
        require(receipt.is_relative_to(C / 'evidence') and '..' not in receipt.parts, 'Receipt outside exact candidate')
        path = receipt / 'result.json'
        if not path.exists():
            missing_results.append(action['mode'])
            continue
        result = load(path)
        result_pin = file_record(path)
        records.append({'mode': action['mode'], 'result_pin': result_pin, 'actual_result': result})
        wait = result.get('child_wait')
        if wait is not None:
            add(wait['pid'], action['mode'] + ':target-child', result_pin, wait['argv'])
        if wait is None or result.get('scope_wait') is None:
            unknown.append(action['mode'] + ':target-or-scope-wait')
        if wait is not None and (wait.get('returncode') != 0 or result.get('scope_wait') != 0):
            unknown.append(action['mode'] + ':actual-target-or-scope-nonzero')
    outers = []
    base = C / 'review/root-outer-capture-v1'
    mapped_bindings = set()
    folders = sorted(base.iterdir()) if base.exists() else []
    for folder in folders:
        require(folder.is_dir() and not folder.is_symlink(), 'Outer inventory has non-directory member')
        start_path = folder / 'outer-child-start.json'
        wait_path = folder / 'outer-child-wait.json'
        start = load(start_path) if start_path.exists() else None
        end = load(wait_path) if wait_path.exists() else None
        require(start is not None, 'Unresolved outer identity: absent start record ' + str(folder))
        argv = start['argv']
        require(len(argv) == 5 and argv[:3] == ['/usr/bin/python3', '-B', str(C / 'review/root-live-lane-v1/handshake.py')] and
                argv[3] in by_mode and argv[4] == contract['gate_sha256'], 'Unmapped original outer action')
        mode = argv[3]
        expected_inputs = {str(C / 'review/root-live-lane-v1' / name): file_record(C / 'review/root-live-lane-v1' / name)
                           for name in ('handshake.py', 'inputs.json')}
        require(start['inputs'] == expected_inputs and start['raw_stdout'] == str(folder / 'handshake.stdout') and
                start['raw_stderr'] == str(folder / 'handshake.stderr'), 'Original outer control/raw correspondence differs')
        add(start['pid'], mode + ':handshake-child', file_record(start_path), argv)
        add(start['wrapper_pid'], mode + ':outer-wrapper', file_record(start_path))
        bindings = []
        attempts_base = C / 'review/root-live-lane-v1/attempts' / mode
        for binding_path in sorted(attempts_base.glob('*/outer-capture-binding.json')):
            binding = load(binding_path)
            if binding['outer_capture_path'] != str(folder):
                continue
            require(binding['handshake_pid'] == start['pid'] and binding['wrapper_pid'] == start['wrapper_pid'],
                    'Actual outer/handshake identity join differs')
            bindings.append(binding_path)
            mapped_bindings.add(str(binding_path))
        require(len(bindings) <= 1, 'Outer belongs to multiple original attempts')
        launcher_wait = None
        if bindings:
            attempt = bindings[0].parent
            launcher_path = attempt / 'launcher-wait.json'
            launcher_wait = load(launcher_path) if launcher_path.exists() else None
            if launcher_wait is not None:
                require(launcher_wait['argv'] == by_mode[mode]['launcher_argv'], 'Original launcher argv differs')
                add(launcher_wait['pid'], mode + ':launcher-child', file_record(launcher_path), launcher_wait['argv'])
            elif (attempt / 'disposition.json').exists():
                unknown.append(mode + ':admitted-launcher-wait-missing')
        if end is not None:
            require(type(end.get('actual_handshake_Popen_wait_returncode')) is int or
                    end.get('actual_handshake_Popen_wait_returncode') is None,
                    'Original handshake wait must be an actual integer or UNKNOWN/None')
            require(end['pid'] == start['pid'] and end['wrapper_pid'] == start['wrapper_pid'] and end['argv'] == argv,
                    'Original outer start/wait identity differs')
            for raw in end['raw_files']:
                require(raw['path'] in (str(folder / 'handshake.stdout'), str(folder / 'handshake.stderr')),
                        'Original outer raw descriptor outside owned folder')
                matched(raw)
            if launcher_wait is not None:
                require(launcher_wait['returncode'] == end['actual_handshake_Popen_wait_returncode'],
                        'Retained original launcher/handshake waits conflict')
        actual_wait = end.get('actual_handshake_Popen_wait_returncode') if end is not None else None
        retention_success = end.get('retention_success') if end is not None else None
        missing = [name for name in ('outer-child-start.json', 'outer-child-wait.json', 'handshake.stdout', 'handshake.stderr')
                   if not (folder / name).exists()]
        if actual_wait is None or actual_wait != 0 or retention_success is not True or (folder / 'outer-retention-refusal.json').exists():
            unknown.append(mode + ':outer-wait-or-retention-not-success')
        outers.append({'folder': str(folder), 'mode': mode, 'start': file_record(start_path),
                       'wait': file_record(wait_path) if end is not None else None,
                       'actual_original_handshake_Popen_wait': actual_wait,
                       'wait_status': 'UNKNOWN' if actual_wait is None else 'ACTUAL_RETAINED_WAIT',
                       'original_retention_success': retention_success,
                       'partial_retention_status': 'PARTIAL_RETAINED_WITH_GAPS' if missing or retention_success is not True else 'ORIGINAL_COMPLETE_RETAINED',
                       'missing_original_artifacts': missing,
                       'bindings': [file_record(path) for path in bindings],
                       'actual_launcher_wait': launcher_wait, 'original_artifacts_padded': False})
    attempts_root = C / 'review/root-live-lane-v1/attempts'
    all_bindings = {str(path) for path in attempts_root.glob('*/*/outer-capture-binding.json')}
    require(mapped_bindings == all_bindings, 'Incomplete original full partial outer/attempt inventory')
    for claim_path in sorted(attempts_root.glob('*/launch-claim.json')):
        claim = load(claim_path)
        require(claim['action']['mode'] in by_mode and claim['action'] == by_mode[claim['action']['mode']],
                'Original durable launch claim is not the exact enrolled action')
        require(any(row['folder'] == claim['outer_capture_path'] for row in outers), 'Unmapped durable launch claim')
    prefix = load(matched(contract['retained_original_pins']['actual_prefix_observation']))
    for row in prefix['actual_completed_outer_waits']:
        add(row['actual_outer_pid'], row['mode'] + ':Main-outer-child',
            contract['retained_original_pins']['actual_prefix_observation'], row['actual_outer_argv'])
    cleanup = [row for row in prefix['errors'] if 'cleanup_owned_outer_pid' in row]
    for row in cleanup:
        add(row['cleanup_owned_outer_pid'], 'Main-owned-interrupted-outer-cleanup',
            contract['retained_original_pins']['actual_prefix_observation'])
    lost = next((row for row in outers if row['folder'] == contract['lost_outer_folder']), None)
    require(lost is not None and lost['wait'] is None and lost['actual_original_handshake_Popen_wait'] is None,
            'Historical lost Popen wait must remain absent/UNKNOWN, never reconstructed')
    return {'records': records, 'missing_result_modes': missing_results,
            'unknown_or_non_success_evidence': unknown, 'outer_observations': outers,
            'all_outer_directories_mapped': True, 'known_owned_processes': known,
            'actual_Main_prefix_observation': prefix, 'all_required_actual_pass': False,
            'original_collector_refusal': contract['original_collector_refusal'],
            'root_outcome_eligibility': False, 'phase_acceptance': False}


def process_observations(known):
    observations = []
    for identity in known:
        proc = Path('/proc') / str(identity['pid'])
        row = {**identity, 'at': now().isoformat(), 'proc_currently_exists': proc.exists(),
               'observed_nonlive': False, 'wait_inferred_from_process_absence': False}
        if row['proc_currently_exists']:
            # PID reuse is retained for Main resolution, never killed or silently
            # equated to the departed owned child. A present PID fails closed.
            try:
                row['current_stat_raw'] = (proc / 'stat').read_text()
                row['current_cmdline_hex'] = (proc / 'cmdline').read_bytes().hex()
                row['current_cgroup_raw'] = (proc / 'cgroup').read_text()
                row['current_executable_link'] = os.readlink(proc / 'exe')
                row['current_status_raw'] = (proc / 'status').read_text()
            except OSError as error:
                row['current_identity_observation_error'] = str(error)
        else:
            row['observed_nonlive'] = True
        observations.append(row)
    return {'at': now().isoformat(), 'processes': observations,
            'all_known_owned_identities_resolved_nonlive': all(row['observed_nonlive'] for row in observations),
            'unrelated_processes_stopped': False, 'numeric_wait_reconstructed': False}


def commit_window(state, prior):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile('w', dir=WINDOW.parent, prefix=WINDOW.name + '.', delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(state, stream, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, prior['mode'])
        require(file_record(WINDOW) == prior, 'Reserved window changed before atomic commit')
        os.replace(temporary, WINDOW)
        temporary = None
        descriptor_fd = os.open(WINDOW.parent, os.O_DIRECTORY | os.O_CLOEXEC)
        try:
            os.fsync(descriptor_fd)
        finally:
            os.close(descriptor_fd)
    finally:
        if temporary is not None:
            temporary.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('selected_inputs', type=Path)
    parser.add_argument('selected_inputs_sha256')
    parser.add_argument('collection_name')
    args = parser.parse_args()
    require(not os.environ.get('PYTHONOPTIMIZE') and __debug__, 'Assertions may not be suppressed')
    require(re.fullmatch(r'[0-9a-f]{64}', args.selected_inputs_sha256) is not None, 'Exact selected-input SHA256 required')
    input_pin = file_record(args.selected_inputs)
    require(input_pin['sha256'] == args.selected_inputs_sha256, 'Selected-input pin differs')
    require(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,95}', args.collection_name) is not None,
            'Safe exclusive Main collection name required')
    inputs = load(args.selected_inputs)
    required = {'schema', 'observer', 'operation', 'candidate', 'source_manifest', 'independent_review',
                'stage_goal_observation', 'actual_runtime_and_routing_binding', 'expected_window',
                'operator_preferences', 'phase_acceptance'}
    require(set(inputs) == required and inputs['schema'] == 'worldline-original-partial-ownership-recovery-Main-inputs-v1',
            'Closed exact original recovery selected-input schema required')
    manifest, contract = source_receiver(inputs)
    goal = fresh_goal(inputs, contract)
    if inputs['operator_preferences'] is not None:
        matched(inputs['operator_preferences'])
    parent = P / 'Main-owned-collections'
    if not parent.exists():
        parent.mkdir(mode=0o700)
    canonical(parent)
    require(parent.is_dir() and stat.S_IMODE(parent.stat().st_mode) == 0o700, 'Private Main collection parent required')
    output = parent / args.collection_name
    output.mkdir(mode=0o700, exist_ok=False)
    try:
        save_new(output, 'selected-inputs-retention.json', {'selected_inputs': input_pin,
                 'actual_selected_inputs': inputs, 'source_manifest': inputs['source_manifest'],
                 'phase_acceptance': False, 'target_execution': False})
        readback, actions = frame_readback(contract)
        readback_pin = save_new(output, 'original-full-frame-source-private-generated-readback.json', readback)
        retained = snapshot(C, allow_links=True, headers=True)
        retained_pin = save_new(output, 'complete-original-retained-files-dirs-types-modes-sha-headers.json',
                                {'candidate': str(C), 'entries': retained, 'original_artifacts_modified': False,
                                 'includes_entire_original_partial_outer_inventory': True})
        outcomes = owned_records(actions, contract)
        outcomes_pin = save_new(output, 'original-real-outcomes-and-explicit-unknowns.json', outcomes)
        scope_sample = scope_observations(actions)
        processes = process_observations(outcomes['known_owned_processes'])
        live = {name: invoke(argv) for name, argv in {
            'proof_lanes': ['/usr/bin/systemctl', '--user', 'list-units', '--all', '--state=active,activating,deactivating', '--no-legend', '--plain', 'codex-*proof*'],
            'codex_scopes': ['/usr/bin/systemctl', '--user', 'list-units', '--all', '--state=active,activating,deactivating', '--no-legend', '--plain', 'codex-*.scope'],
            'process_sample': ['/usr/bin/ps', '-eo', 'pid,comm'],
        }.items()}
        save_new(output, 'fresh-terminal-live-sample.json', {'at': now().isoformat(), 'observations': live,
                 'boundary': 'Unrelated activity is observed, never stopped; it does not manufacture an owned wait.'})
        save_new(output, 'owned-terminal-observations.json', {'scopes': scope_sample, 'known_children_outer_handshake_launchers': processes})
        require(scope_sample['all_owned_scopes_terminal_empty'] and
                processes['all_known_owned_identities_resolved_nonlive'], 'Owned scope/process identity remains live or unresolved')
        require(snapshot(C, allow_links=True, headers=True) == retained, 'Original complete retained files changed during recovery')
        with Path(str(WINDOW) + '.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            source_receiver(inputs)
            goal = fresh_goal(inputs, contract)
            require(file_record(args.selected_inputs) == input_pin, 'Selected input changed')
            prior = file_record(WINDOW)
            require(prior == inputs['expected_window'], 'Full original reserved window pin differs')
            state = load(WINDOW)
            require(state['status'] == 'reserved' and state['holder_task'] == HOLDER and state['candidate'] == str(C),
                    'Exact original holder/candidate/reservation required; never overwrite a sibling')
            prior_state = json.loads(json.dumps(state))
            prior_raw = WINDOW.read_bytes().hex()
            require(file_record(WINDOW) == prior, 'Window changed during exact preimage retention')
            final_scopes = scope_observations(actions)
            final_processes = process_observations(outcomes['known_owned_processes'])
            require(final_scopes['all_owned_scopes_terminal_empty'] and
                    final_processes['all_known_owned_identities_resolved_nonlive'], 'Fresh owned liveness changed before custody release')
            require(snapshot(C, allow_links=True, headers=True) == retained, 'Original retained evidence changed before release')
            fresh_goal(inputs, contract)
            at = now().isoformat()
            terminal = save_new(output, 'custody-only-partial-ownership-collection.json', {
                'schema': 'worldline-original-partial-ownership-recovery-custody-only-v1', 'at': at,
                'candidate': str(C), 'holder_task': HOLDER, 'prior_window': prior,
                'source_manifest': inputs['source_manifest'], 'independent_review': inputs['independent_review'],
                'goal_observation': goal, 'original_full_readback': readback_pin,
                'complete_original_retained_inventory': retained_pin, 'original_real_outcomes': outcomes_pin,
                'fresh_all118_owned_scopes': final_scopes, 'fresh_all_known_owned_processes': final_processes,
                'lost_original_handshake_Popen_wait': None, 'lost_wait_status': 'UNKNOWN',
                'original_collector_refusal': contract['original_collector_refusal'],
                'all_required_actual_pass': False, 'root_outcome_eligibility': False,
                'original_batch_acceptance': False, 'matching_source_runtime_acceptance': False,
                'full_strict_proof_acceptance': False, 'phase_acceptance': False,
                'original_fixture_baseline_created': False, 'unrelated_processes_stopped': False,
                'original_guarantees': 'OPEN_UNCHANGED', 'window_released': False,
                'truth_boundary': 'Custody collection only. Child/scope4 and Main outer-15 are genuine distinct facts, never the lost handshake parent Popen wait.'})
            reason = 'Exact interrupted O2 owned scopes and known identities freshly nonlive; complete original evidence and collector refusal retained. CUSTODY ONLY: lost handshake wait UNKNOWN, pending-build4, unrun obligations and every original guarantee OPEN; no batch/runtime/proof/fixture/Phase One acceptance.'
            record = {'at': at, 'holder_task': HOLDER, 'candidate': str(C), 'prior': prior,
                      'reason': reason, 'evidence': terminal, 'custody_only': True,
                      'lost_original_handshake_Popen_wait': None, 'phase_acceptance': False}
            state.setdefault('release_history', []).append(record)
            state.update(status='released', released_at=at, updated_at=at, reason=reason,
                         pending_request={'state': 'WORLDLINE_ORIGINAL_O2_PARTIAL_OWNERSHIP_CUSTODY_ONLY_RELEASED_UNKNOWN_WAIT_RETAINED'})
            save_new(output, 'complete-window-before-after-and-inverse.json', {
                'prior': prior, 'exact_prior_raw_bytes_hex': prior_raw, 'before': prior_state, 'after': state,
                'changed_fields': {name: {'before_present': name in prior_state,
                                         'before': prior_state.get(name), 'after': state[name]}
                                   for name in ('status', 'released_at', 'updated_at', 'reason', 'pending_request', 'release_history')},
                'all_other_fields_and_complete_old_histories_retained': True,
                'inverse_is_evidence_only_not_permission_to_re_reserve': True})
            commit_window(state, prior)
            release = save_new(output, 'coordination-custody-only-release.json', {
                **record, 'current': file_record(WINDOW), 'status': 'released',
                'original_collector_not_reclassified_as_success': True,
                'original_outer_missing_end_not_created': True, 'original_candidate_modified': False})
        print(json.dumps({'custody_collection': terminal, 'release': release,
                          'lost_original_handshake_Popen_wait': None, 'phase_acceptance': False}))
    except BaseException as error:
        save_new(output, 'recovery-refusal.json', {'at': now().isoformat(), 'candidate': str(C),
                 'type': type(error).__name__, 'message': str(error),
                 'window_status_must_be_read_from_actual_coordination_record': True,
                 'no_wait_or_acceptance_inferred': True, 'phase_acceptance': False})
        raise


if __name__ == '__main__':
    main()
