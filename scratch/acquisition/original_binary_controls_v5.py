"""Original binary roster local payloads; no original-carrier acceptance.

Coordinator launches --run through its approved locked heavy scope. --plan is
read-only except its fresh scratch output. Missing prerequisites never pass.
"""
from __future__ import annotations
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import signal
import stat
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OWN = ROOT / 'scratch/acquisition'
FRAME = ROOT / 'scratch/coordinator/final-frame-v5/source'
COMMIT = None  # Required --expected-commit comes from freeze-v5/source.json.
ROSTER = ROOT / 'scratch/reviewer/f3-original-full-action-roster.json'
RECIPE = OWN / 'original-payload-recipe-v2.json'
FREEZE = ROOT / 'records/phase1-blockers/freeze-v5/source.json'
AUX = ROOT / 'records/phase1-blockers/original-aux-builds-final-v6'
CARRIER = OWN / 'historical-v1/run_checks.py'
FULL_BUILD = ROOT / 'records/phase1-blockers/final-build-steps-v5/artifacts.json'
ARTIFACT_MANIFEST = None

def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def identity(path):
    path = Path(path)
    st = path.stat()
    return {'path': str(path), 'sha256': sha(path), 'bytes': st.st_size,
            'mode': stat.S_IMODE(st.st_mode), 'device': st.st_dev, 'inode': st.st_ino}

def save(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')

def load(path):
    return json.loads(Path(path).read_bytes())

def owned(path):
    path = Path(path).resolve()
    if not path.is_relative_to(OWN) or path == OWN:
        raise RuntimeError('output must be a new acquisition scratch descendant')
    return path

def freeze_identity():
    frozen = load(FREEZE)
    if frozen['commit'] != COMMIT:
        raise RuntimeError('unexpected frozen commit')
    if subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() != COMMIT:
        raise RuntimeError('HEAD changed')
    for name, expected in frozen['source_hashes'].items():
        for base in (ROOT, FRAME):
            if sha(base / name) != expected:
                raise RuntimeError(f'frozen source mismatch: {base/name}')
    return {'utc': utc(), 'commit': COMMIT, 'freeze': identity(FREEZE),
            'root_and_frame_match_all_frozen_source_hashes': True}

def plan():
    source = load(ROSTER)
    old = {r['mode']: r for r in load(RECIPE)['actions']}
    origins = {Path(x['path']).name: x for x in source['immutable_origins']}
    if sha(CARRIER) != origins['run_checks.py']['sha256']:
        raise RuntimeError('retained original carrier changed')
    tail_path = Path(origins['tail-enrollment.json']['path'])
    if sha(tail_path) != origins['tail-enrollment.json']['sha256']:
        raise RuntimeError('original tail enrollment changed')
    tail = load(tail_path)['controls']
    rows = []
    for action in source['actions']:
        if action['kind'] != 'binary-controls':
            continue
        mode = action['mode']; mapping = old[mode]; original = action['original']
        prefix = action['rebindings']['source_prefix']
        argv = [s.replace(prefix, str(ROOT)) for s in original['child_argv']]
        additional = original.get('additional_command')
        marker = tail.get(mode, {}).get('marker')
        if mode == 'root-custody-context-controls':
            marker = 'ROOT_CUSTODY_CONTEXT_CONTROLS_PASS'
        if action['expected_result'].get('source_specific_marker') not in (None, marker):
            raise RuntimeError('marker extraction disagrees with roster')
        row = {'mode': mode, 'original': action, 'argv': argv, 'cwd': str(FRAME),
               'required_build': action['required_build_prerequisite'],
               'original_payload_timeout_seconds': additional['test_timeout_seconds'] if additional else None,
               'original_stdout_exact_lines': None if marker is None else [marker],
               'initial_status': 'NOT PERFORMED', 'carrier_acceptance': 'NOT PERFORMED: D7 gap retained'}
        if 'project_binding' in mapping:
            detail = mapping['project_binding']; project = ROOT / detail['project']['path']
            if sha(project) != detail['project']['sha256']:
                raise RuntimeError('project drift from reviewed original mapping: '+str(project))
            text = project.read_text()
            match = re.search(r'for\s+Object_Dir\s+use\s+"([^"]+)"', text, re.I)
            if not match or not detail['assertion_flag_in_project']:
                raise RuntimeError('explicit original object/assertion mapping absent')
            mains = detail['declared_mains']
            chosen = Path(argv[0]).name + '.adb'
            if chosen not in mains:
                if len(mains) != 1:
                    raise RuntimeError('ambiguous main for '+mode)
                chosen = mains[0]
            object_dir = (project.parent / match.group(1)).resolve()
            row.update(binary=argv[0], project=identity(project),
                       main=identity(project.parent / chosen),
                       main_ali=str(object_dir / (Path(chosen).stem+'.ali')),
                       original_build_argv=mapping['build_original_argv'],
                       assertion_policy='WORLDLINE_BUILD=checks and actual main ALI A -gnata required')
        else:
            if mode != 'original-full-physical-disposable-namespace-controls':
                raise RuntimeError('unmapped binary action: '+mode)
            row.update(namespace=True,
                       additional_native_prerequisite='successful frozen main/native build artifacts; real current core library',
                       namespace_non_claim='Disposable syscall fixture only; no installed protected authority/actor credit')
        rows.append(row)
    if len(rows) != 41 or len({r['mode'] for r in rows}) != len(rows):
        raise RuntimeError('complete original 41-action binary roster required')
    return {'classification': 'MEASURED original roster/source mapping; no payload execution',
            'utc': utc(), 'source_commit': COMMIT, 'roster': identity(ROSTER),
            'recipe': identity(RECIPE), 'original_carrier': identity(CARRIER),
            'original_tail_enrollment': identity(tail_path), 'script': identity(__file__),
            'timeout_evidence': 'run_checks.py43-57 wait(None) for ordinary; additional180s. Scope276-278 has no RuntimeMax. External original admission ceiling remains D7; local outer deadline must be reported separately.',
            'actions': rows, 'non_claims': ['Local payload survey preserves each original action but does not recreate original predecessor ordering/custody/admission.', 'No all-gate or independent acceptance.']}

def scope_identity():
    raw = Path('/proc/self/cgroup').read_text()
    rel = next(line.split(':', 2)[2] for line in raw.splitlines() if line.startswith('0::'))
    group = Path('/sys/fs/cgroup') / rel.lstrip('/')
    values = {name: (group/name).read_text().strip() for name in ('memory.max', 'memory.swap.max')}
    if values != {'memory.max': '8589934592', 'memory.swap.max': '0'}:
        raise RuntimeError('exact 8G/swap0 enclosing scope required')
    return {'utc': utc(), 'membership': raw, 'cgroup': str(group), **values,
            'lock_claim': 'Coordinator-approved heavy launcher owns lock/admission; worker does not reacquire it'}

def environment(temp):
    env = dict(os.environ)
    for name in ('PYTHONOPTIMIZE', 'LD_PRELOAD', 'LD_LIBRARY_PATH', 'LD_AUDIT', 'LIBRARY_PATH'):
        env.pop(name, None)
    env.update(WORLDLINE_BUILD='checks', PYTHONDONTWRITEBYTECODE='1',
               PYTHONPATH=str(FRAME/'runtime')+':'+str(FRAME/'tests'),
               WORLDLINE_CORE_LIB=str(ROOT/'lib/libworldline_core.so'),
               PENDING_OBJECT_DIR=str(ROOT/'obj/pending-standalone'),
               PENDING_LIBRARY_DIR=str(ROOT/'lib/pending-standalone'), TMPDIR=str(temp))
    return env

def guard(out, namespace=False):
    argv = ['/usr/bin/bwrap', '--die-with-parent', '--new-session', '--unshare-pid',
            '--ro-bind', '/', '/', '--dev', '/dev', '--proc', '/proc',
            '--bind', str(out), str(out), '--bind', str(out/'temp'), '/tmp',
            '--chdir', str(FRAME)]
    if namespace:
        # A bind source is resolved in this bwrap process's existing root.
        # Start the inner guard after the outer guard has mounted the tmpfs.
        inner = argv + ['--bind', str(out/'second'), str(out/'second'),
                        '--bind', str(out/'second'), '/dev/shm']
        argv += ['--tmpfs', str(out/'second'), '--', *inner]
    return argv

def checked_capture(argv, out, label, env):
    with (out/(label+'.stdout')).open('xb') as stdout, (out/(label+'.stderr')).open('xb') as stderr:
        result = subprocess.run(argv, env=env, cwd=FRAME, stdout=stdout, stderr=stderr, timeout=30)
    receipt = {'argv': argv, 'exit_code': result.returncode,
               'stdout': identity(out/(label+'.stdout')), 'stderr': identity(out/(label+'.stderr'))}
    save(out/(label+'.json'), receipt)
    if result.returncode:
        raise RuntimeError('metadata command refused: '+label)
    return (out/(label+'.stdout')).read_text(errors='strict')

def build_recipe_join(expected_argv, actual_argv, required_build):
    if not expected_argv:
        return None
    tail = actual_argv[-len(expected_argv):]
    if tail == expected_argv:
        return 'original-exact'
    if (Path(expected_argv[0]).name == 'gprbuild'
            and tail[1:] == expected_argv[1:]
            and tail and Path(tail[0]).name == 'gprbuild'):
        return 'original-selected-executable-name'
    # D31 already authorizes these exact restored builds with jobs2.
    projects = {
        'original-physical-semantic-build': 'physical-value-controls/physical_value_controls.gpr',
        'original-canonical-exchange-semantic-build': 'canonical-exchange-tests/canonical_exchange_tests.gpr',
        'original-canonical-owner-semantic-build': 'canonical-owner-completion-tests/canonical_owner_completion_tests.gpr',
    }
    project = projects.get(required_build)
    if (project is not None and len(expected_argv) == 4
            and Path(expected_argv[0]).name == 'gprbuild'
            and expected_argv[1:] == ['-p', '-P', project]
            and len(actual_argv) >= 5
            and Path(actual_argv[-5]).name == 'gprbuild'
            and actual_argv[-4:] == ['-p', '-j2', '-P', project]):
        return 'D31-reviewed-restored-j2'
    return None

def artifact_join(row, out, env, aux):
    if aux['source_commit'] != COMMIT or aux.get('source_unchanged') is not True or aux.get('library_unchanged') is not True:
        raise RuntimeError('current source/auxiliary library join missing')
    matches = [x for x in aux['steps'] if x['name'] == row['required_build']]
    if len(matches) != 1 or matches[0].get('exit_code') != 0:
        raise RuntimeError('matching fresh prerequisite build failed or absent')
    step = matches[0]
    receipt = AUX/row['required_build']/'result.json'
    if load(receipt) != step or step['source_commit'] != COMMIT or step['cwd'] != str(ROOT):
        raise RuntimeError('per-step build receipt mismatch')
    if step.get('environment', {}).get('WORLDLINE_BUILD') != 'checks':
        raise RuntimeError('original assertion-enabled build environment missing')
    recipe_join = None
    if not row.get('namespace'):
        prefix = row['original']['rebindings']['source_prefix']
        expected_argv = [x.replace(prefix, str(ROOT)) for x in row['original_build_argv']]
        actual_argv = step['argv']
        recipe_join = build_recipe_join(expected_argv, actual_argv, row['required_build'])
        if recipe_join is None:
            raise RuntimeError('original prerequisite build argv mismatch')
    joins = {'build_result': identity(receipt), 'source_commit': COMMIT,
             'core_library': identity(ROOT/'lib/libworldline_core.so')}
    if recipe_join is not None:
        joins['build_recipe_join'] = {'classification': 'MEASURED command correspondence',
                                    'kind': recipe_join,
                                    'original_rebound_argv': expected_argv,
                                    'actual_build_argv': actual_argv}
    if joins['core_library']['sha256'] != aux['library_after']:
        raise RuntimeError('core library changed after builds')
    if row.get('namespace'):
        built = load(FULL_BUILD)
        if built['source_commit'] != COMMIT or built.get('source_unchanged') is not True:
            raise RuntimeError('namespace current native build missing')
        for name, expected in built['artifacts'].items():
            if sha(ROOT/name) != expected:
                raise RuntimeError('namespace native artifact mismatch: '+name)
        joins['native_build'] = identity(FULL_BUILD)
        return joins
    binary = Path(row['binary']); ali = Path(row['main_ali'])
    if binary.is_symlink() or not binary.is_file() or not os.access(binary, os.X_OK):
        raise RuntimeError('required exact binary missing/not regular executable')
    ali_text = ali.read_text()
    flags = [x[2:] for x in ali_text.splitlines() if x.startswith('A ')]
    if '-gnata' not in flags or '-gnatp' in flags:
        raise RuntimeError('actual main ALI lacks required assertions')
    if Path(row['main']['path']).name not in ali_text:
        raise RuntimeError('actual main ALI source name mismatch')
    joins.update(binary=identity(binary), main_ali=identity(ali), ali_compiler_arguments=flags,
                 project=identity(row['project']['path']), main=identity(row['main']['path']))
    if joins['project']['sha256'] != row['project']['sha256'] or joins['main']['sha256'] != row['main']['sha256']:
        raise RuntimeError('project/main drift')
    # Preserve actual resolved dynamic dependencies without ldd executing a target.
    prefix = guard(out)
    elf = checked_capture(prefix+['/usr/bin/readelf', '-lW', str(binary)], out, 'elf-program-headers', env)
    checked_capture(prefix+['/usr/bin/readelf', '-dW', str(binary)], out, 'elf-dynamic', env)
    match = re.search(r'Requesting program interpreter:\s*(\S+)\]', elf)
    if not match:
        raise RuntimeError('ELF interpreter absent; static dependency qualification not implemented')
    interpreter = Path(match.group(1))
    listing = checked_capture(prefix+[str(interpreter), '--list', str(binary)], out, 'loader-list', env)
    dependencies = {str(interpreter.resolve())}
    for line in listing.splitlines():
        if 'not found' in line:
            raise RuntimeError('unresolved ELF dependency')
        match = re.search(r'=>\s+(/\S+)\s+\(', line)
        direct = re.match(r'\s*(/\S+)\s+\(', line)
        if match or direct:
            dependencies.add(str(Path((match or direct).group(1)).resolve()))
        elif line.strip() and not re.match(r'\s*(?:linux-vdso|linux-gate)', line):
            raise RuntimeError('unparsed dynamic dependency line: '+line)
    joins['interpreter'] = identity(interpreter)
    joins['resolved_dependencies'] = [identity(Path(x)) for x in sorted(dependencies)]
    joins['artifact_join_limit'] = 'Post-build readback tied to successful exact project/main build; not original external tool/native/custody collector.'
    return joins

def same_joins(joins):
    for name in ('core_library', 'binary', 'main_ali', 'project', 'main', 'interpreter', 'native_build', 'build_result'):
        if name in joins and identity(joins[name]['path']) != joins[name]:
            return False
    return all(identity(x['path']) == x for x in joins.get('resolved_dependencies', []))

def namespace_inner(out, argv):
    """Runs inside isolated mount/PID namespace; original payload argv unchanged."""
    if os.geteuid() == 0:
        raise RuntimeError('original unshare must begin from actual non-root caller')
    pre = {'utc': utc(), 'uid': os.getuid(), 'euid': os.geteuid(),
           'uid_map': Path('/proc/self/uid_map').read_text(),
           'namespaces': {n: os.readlink('/proc/self/ns/'+n) for n in ('user', 'mnt', 'pid')},
           'first_st_dev': (out/'temp').stat().st_dev,
           'second_st_dev': (out/'second').stat().st_dev,
           'logical_dev_shm_st_dev': Path('/dev/shm').stat().st_dev}
    save(out/'namespace-premises-before.json', pre)
    if pre['first_st_dev'] == pre['second_st_dev'] or pre['second_st_dev'] != pre['logical_dev_shm_st_dev']:
        raise RuntimeError('real distinct filesystem and logical alias required')
    # Separate read-only premise control with the original unshare flags.
    probe = ['/usr/bin/unshare', '--user', '--map-root-user', '/usr/bin/python3', '-B',
             str(Path(__file__).resolve()), '--namespace-probe', str(out/'namespace-user-probe.json')]
    result = subprocess.run(probe, timeout=30)
    if result.returncode or load(out/'namespace-user-probe.json')['euid'] != 0:
        raise RuntimeError('actual original unshare premise refused')
    save(out/'namespace-original-exec.json', {'utc': utc(), 'argv': argv,
         'fixture_unchanged': True, 'protected_authority': 'NOT PERFORMED'})
    payload = subprocess.Popen(argv, start_new_session=True)
    timed_out = False
    try:
        code = payload.wait(timeout=180)
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(payload.pid, signal.SIGKILL)
        code = payload.wait(timeout=10)
    save(out/'namespace-payload-result.json', {'utc': utc(), 'argv': argv,
         'exit_code': code, 'additional_deadline_expired': timed_out,
         'original_payload_timeout_seconds': 180})
    return 124 if timed_out else code

def run(args):
    out = owned(args.out); out.mkdir(parents=True, exist_ok=False)
    roster = plan(); save(out/'plan.json', roster)
    save(out/'source-before.json', freeze_identity())
    save(out/'scope.json', scope_identity())
    aux = load(AUX/'result.json')
    save(out/'aux-manifest-reference.json', identity(AUX/'result.json'))
    retained = load(ARTIFACT_MANIFEST)
    if retained['source_commit'] != COMMIT or retained['aux_manifest'] != identity(AUX/'result.json'):
        raise RuntimeError('post-build artifact manifest is not this frozen build')
    save(out/'post-build-artifact-reference.json', identity(ARTIFACT_MANIFEST))
    results = []
    for row in roster['actions']:
        directory = out/row['mode']; directory.mkdir()
        (directory/'temp').mkdir(); (directory/'second').mkdir()
        env = environment(directory/'temp')
        record = {'mode': row['mode'], 'source_commit': COMMIT, 'started_utc': utc(),
                  'status': 'NOT PERFORMED', 'classification': 'UNVERIFIED',
                  'exit_code': None, 'original_payload_timeout_seconds': row['original_payload_timeout_seconds'],
                  'carrier_acceptance': 'NOT PERFORMED: D7 external original order/admission/custody not recreated'}
        child = None
        try:
            joins = artifact_join(row, directory, env, aux)
            candidates = [r for r in retained['actions'] if r['mode'] == row['mode']]
            if len(candidates) != 1 or candidates[0].get('status') != 'MEASURED' or candidates[0].get('joins') != joins:
                raise RuntimeError('binary/ALI/dependency identity differs from retained post-build artifacts')
            save(directory/'identity-before.json', joins)
            command = guard(directory, row.get('namespace', False))
            if row.get('namespace'):
                command += ['/usr/bin/python3', '-B', str(Path(__file__).resolve()),
                            '--namespace-inner', str(directory), '--', *row['argv']]
            else:
                command += row['argv']
            save(directory/'launch.json', {'utc': utc(), 'argv': command, 'original_rebound_argv': row['argv'],
                 'cwd': str(FRAME), 'environment': {k: env[k] for k in ('WORLDLINE_BUILD','WORLDLINE_CORE_LIB','PENDING_OBJECT_DIR','PENDING_LIBRARY_DIR','PYTHONPATH','TMPDIR')},
                 'original_timeout_seconds': row['original_payload_timeout_seconds'],
                 'local_outer_timeout': 'Owned coordinator heavy scope receipt; not invented as original deadline'})
            timed_out = False
            with (directory/'stdout').open('xb') as stdout, (directory/'stderr').open('xb') as stderr:
                child = subprocess.Popen(command, cwd=FRAME, env=env, stdout=stdout, stderr=stderr,
                                         start_new_session=True)
                try:
                    # Namespace wrapper applies180s only to unchanged original argv after its separate premise probe.
                    deadline = None if row.get('namespace') else row['original_payload_timeout_seconds']
                    code = child.wait(timeout=deadline)
                except subprocess.TimeoutExpired:
                    timed_out = True
                    # Only this session's bwrap process group; private PID ns retires descendants.
                    os.killpg(child.pid, signal.SIGKILL)
                    code = child.wait(timeout=10)
            unchanged = same_joins(joins)
            exact_lines = row['original_stdout_exact_lines']
            marker_ok = exact_lines is None or (directory/'stdout').read_text().splitlines() == exact_lines
            namespace_ok = True
            namespace_summary = None
            if row.get('namespace'):
                payload_receipt = load(directory/'namespace-payload-result.json')
                timed_out = payload_receipt['additional_deadline_expired']
                stderr_text = (directory/'stderr').read_text(errors='replace')
                summary_match = re.search(r'^Ran ([0-9]+) tests? in .*$', stderr_text, re.M)
                namespace_summary = {'ran_summary': summary_match.group(0) if summary_match else None,
                     'observed_test_count': int(summary_match.group(1)) if summary_match else None,
                     'exact_OK_line': 'OK' in stderr_text.splitlines(),
                     'failure_or_skip_marker': bool(re.search(r'^(?:FAILED|OK \(skipped)|\.\.\. (?:skipped|FAIL|ERROR)', stderr_text, re.M))}
                namespace_ok = ((directory/'namespace-original-exec.json').is_file()
                     and payload_receipt['exit_code'] == 0 and summary_match is not None
                     and namespace_summary['observed_test_count'] > 0
                     and namespace_summary['exact_OK_line'] and not namespace_summary['failure_or_skip_marker'])
            record.update(classification='TESTED', exit_code=code, additional_deadline_expired=timed_out,
                          unchanged_artifacts=unchanged, original_stdout_marker_matches=marker_ok,
                          namespace_premises_observed=namespace_ok, namespace_unittest_summary=namespace_summary,
                          stdout=identity(directory/'stdout'), stderr=identity(directory/'stderr'),
                          status='PASSED' if code == 0 and not timed_out and unchanged and marker_ok and namespace_ok else 'FAILED-OPEN')
        except BaseException as error:
            record.update(error_type=type(error).__name__, error=str(error))
            if child is not None:
                record.update(status='FAILED-OPEN', classification='TESTED')
                if child.poll() is None:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait(timeout=10)
            if not isinstance(error, Exception):
                record['ended_utc'] = utc(); save(directory/'result.json', record)
                raise
        record['ended_utc'] = utc()
        save(directory/'result.json', record); results.append(record)
        print(json.dumps({'mode': row['mode'], 'status': record['status'], 'exit_code': record['exit_code']}), flush=True)
    after = freeze_identity(); save(out/'source-after.json', after)
    final = {'classification': 'TESTED local original-payload survey', 'source_commit': COMMIT,
             'actions': results, 'roster_complete': [r['mode'] for r in results] == [r['mode'] for r in roster['actions']],
             'all_payload_conditions_passed': all(r['status']=='PASSED' for r in results),
             'full_F3_acceptance': False, 'original_carrier_acceptance': 'NOT PERFORMED',
             'independent_acceptance': 'NOT PERFORMED', 'source_after': after}
    save(out/'result.json', final)
    return 0 if final['all_payload_conditions_passed'] else 1


def configure(args):
    global COMMIT, FRAME, FREEZE, AUX, FULL_BUILD, ARTIFACT_MANIFEST
    COMMIT = args.expected_commit
    if not re.fullmatch(r'[0-9a-f]{40}', COMMIT):
        raise RuntimeError('explicit full frozen commit required')
    def input_path(value):
        path = Path(value).resolve()
        if not path.is_relative_to(ROOT):
            raise RuntimeError('input must remain in the owned worktree')
        return path
    FRAME = input_path(args.frame)
    FREEZE = input_path(args.freeze)
    AUX = input_path(args.aux_manifest).parent
    if Path(args.aux_manifest).name != 'result.json':
        raise RuntimeError('actual auxiliary final result.json required')
    FULL_BUILD = input_path(args.full_build_manifest)
    ARTIFACT_MANIFEST = input_path(args.artifact_manifest) if args.artifact_manifest else None

def collect(args):
    out = owned(args.out); out.mkdir(parents=True, exist_ok=False)
    roster = plan(); save(out/'plan.json', roster)
    save(out/'source-before.json', freeze_identity())
    save(out/'scope.json', scope_identity())
    aux = load(AUX/'result.json')
    rows = []
    for row in roster['actions']:
        directory=out/row['mode']; directory.mkdir()
        (directory/'temp').mkdir(); (directory/'second').mkdir()
        record={'mode':row['mode'], 'source_commit':COMMIT, 'utc':utc(),
                'status':'NOT PERFORMED', 'classification':'UNVERIFIED', 'payload_executed':False}
        try:
            record['joins']=artifact_join(row,directory,environment(directory/'temp'),aux)
            record.update(status='MEASURED', classification='MEASURED')
        except Exception as error:
            record.update(error_type=type(error).__name__,error=str(error))
        save(directory/'result.json',record);rows.append(record)
    after=freeze_identity(); save(out/'source-after.json',after)
    result={'schema':'worldline.original-binary-post-build-artifacts-v1',
            'classification':'MEASURED post-build readback, no payload execution',
            'source_commit':COMMIT,'utc':utc(),'script':identity(__file__),
            'aux_manifest':identity(AUX/'result.json'),'full_build_manifest':identity(FULL_BUILD),
            'source_after':after,'actions':rows,'complete_original_roster':True,
            'all_artifacts_qualified':all(r['status']=='MEASURED' for r in rows),
            'non_claims':['No original external carrier/tool/custody collector or acceptance.',
                          'Failed/missing prerequisite artifacts retained explicitly; no stale fallback.']}
    save(out/'artifacts.json',result)
    return 0 if result['all_artifacts_qualified'] else 1

def main():
    if len(sys.argv)>1 and sys.argv[1]=='--namespace-probe':
        save(owned(sys.argv[2]), {'utc': utc(), 'euid': os.geteuid(), 'uid': os.getuid(),
             'uid_map': Path('/proc/self/uid_map').read_text(),
             'namespaces': {n: os.readlink('/proc/self/ns/'+n) for n in ('user','mnt','pid')}})
        return 0
    if len(sys.argv)>1 and sys.argv[1]=='--namespace-inner':
        if sys.argv[3]!='--': raise RuntimeError('argv separator missing')
        return namespace_inner(owned(sys.argv[2]), sys.argv[4:])
    parser=argparse.ArgumentParser()
    parser.add_argument('--plan', action='store_true'); parser.add_argument('--run', action='store_true')
    parser.add_argument('--collect', action='store_true')
    parser.add_argument('--expected-commit', required=True)
    parser.add_argument('--freeze', required=True); parser.add_argument('--frame', required=True)
    parser.add_argument('--aux-manifest', required=True); parser.add_argument('--full-build-manifest', required=True)
    parser.add_argument('--artifact-manifest')
    parser.add_argument('--out', required=True); args=parser.parse_args()
    if sum((args.plan,args.run,args.collect)) != 1: parser.error('choose exactly --plan, --collect or --run')
    configure(args)
    if args.run and ARTIFACT_MANIFEST is None: parser.error('--run requires --artifact-manifest')
    if args.plan:
        save(owned(args.out), plan()); return 0
    resource.setrlimit(resource.RLIMIT_CORE, (0,0))
    return collect(args) if args.collect else run(args)

if __name__=='__main__':
    raise SystemExit(main())
