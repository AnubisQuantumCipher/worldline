from pathlib import Path
import datetime, hashlib, json, os, resource, shutil, subprocess, sys
sys.dont_write_bytecode = True
import tool_inventory
import native_inventory
import runtime_inventory
import proof_elf_inventory
import proof_data_inventory
import authorization
import successor_support
import time
MAIN_DEADLINE = successor_support.inherited_main_deadline()

root = Path(__file__).resolve().parent
source = root / 'source'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

mode = sys.argv[1]
os.umask(0o077)
FORMAL_COMMAND = ['/home/sicarii/opt/gnat/gnatprove-aarch64-linux-16.1.0-1/bin/gnatprove', '-P', 'core/worldline_core_sources.gpr', '-U', '--mode=all', '--level=3', '--report=all', '--checks-as-errors=on', '--proof-warnings=on', '-j2']
if mode == 'child':
    receipt = Path(sys.argv[2])
    authorization.check('dispatch')
    write(receipt / 'private-inputs-child-before.json', successor_support.check_source_and_dependency(root))
    import compiler_seed
    write(receipt / 'compiler-seed-child-before.json', compiler_seed.check_pristine_before_compiler(root))
    expected_environment = json.loads((root / 'tool-inventory-template.json').read_text())['tool_inventory_spec']['effective_environment']
    assert {key: os.environ.get(key) for key in expected_environment} == expected_environment, 'Actual strict-child protected environment drift'
    config = json.loads((receipt / 'inputs-before.json').read_text())
    assert config['child_argv'] == FORMAL_COMMAND and config['formal_diagnostic_only'] is True
    membership = Path('/proc/self/cgroup').read_text()
    relative = next(x.split(':', 2)[2] for x in membership.splitlines() if x.startswith('0::'))
    group = Path('/sys/fs/cgroup') / relative.lstrip('/')
    limits = {'at': now(), 'pid': os.getpid(), 'membership': membership,
              'memory.max': (group / 'memory.max').read_text().strip(),
              'memory.swap.max': (group / 'memory.swap.max').read_text().strip(),
              'core_soft_hard': list(resource.getrlimit(resource.RLIMIT_CORE))}
    write(receipt / 'effective-limits-before.json', limits)
    assert limits['memory.max'] == '8589934592'
    assert limits['memory.swap.max'] == '0'
    assert limits['core_soft_hard'] == [0, 0]
    scope_unit = config['scope_argv'][3].split('=', 1)[1]
    if not scope_unit.endswith('.scope'):
        scope_unit += '.scope'
    successor_support.record_owned_scope(receipt, scope_unit, Path(__file__).resolve())
    child_wait = successor_support.capture_owned(
        config['child_argv'], receipt, 'child', 600, cwd=source,
        term_seconds=5, kill_seconds=5, hard_deadline=MAIN_DEADLINE,
        on_started=lambda process: successor_support.retained_owner_record(
            receipt / 'child-start.json', {'at': now(), 'pid': process.pid,
            'argv': config['child_argv'], 'actual_prover_launch_observed': True,
            'owned_process_group': successor_support.owned_group(process)}))
    raise SystemExit(successor_support.owner_exit_code(child_wait))

assert mode == authorization.MODE, 'standalone formal diagnostic only; no ordinary roster authority'
authorization.check('dispatch')
assert mode in (authorization.MODE, 'native-build', 'native-component-tests', 'entry-component-tests', 'acquisition-regression-tests', 'finalization-kernel-tests', 'finalization-producer-tests', 'artifact-build', 'artifact-tests', 'authority-build', 'authority-tests', 'default-tests', 'metadata-tests', 'staged-tests', 'core-abi-tests', 'store-tests', 'revalidation-tests', 'transaction-tests', 'finalization-tests', 'core-all-source-build', 'proof-source-tests', 'wire-build', 'wire-tests', 'report-facts-build', 'report-facts-tests', 'raw-observation-tests', 'terminal-tests', 'roster-d2-python-tests', 'roster-d2-build', 'roster-d2-tests', 'completion-build', 'completion-tests', 'pending-v2-tests', 'transition-direct-build', 'transition-direct-tests', 'pending-build', 'pending-tests', 'build', 'tests', 'admission-tests', 'evaluation-tests', 'direct-build', 'direct-tests',
    'legacy-direct-build', 'legacy-direct-tests', 'resource-direct-build', 'resource-direct-tests', 'recovery-integration-tests', 'resource-runtime-controls', 'recovery-domain-controls', 'recovery-epoch-build', 'recovery-epoch-tests', 'serializer-controls')
label = sys.argv[2] if len(sys.argv) > 2 else 'v1'
assert label in ('v1', 'v2', 'v3')
receipt = root / 'evidence' / (mode + '-' + label)
receipt.mkdir(parents=True, exist_ok=False)
gnat = Path('/home/sicarii/opt/gnat')
environment = dict(os.environ, XDG_RUNTIME_DIR='/run/user/1000',
    DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/1000/bus', WORLDLINE_BUILD='checks',
    GNAT_ROOT=str(gnat), PYTHONPATH=str(source / 'runtime') + ':' + str(source / 'tests'),
    WORLDLINE_CORE_LIB=str(source / 'lib/libworldline_core.so'), PYTHONDONTWRITEBYTECODE='1',
    PENDING_OBJECT_DIR=str(source / 'obj/pending-standalone'),
    PENDING_LIBRARY_DIR=str(source / 'lib/pending-standalone'))
environment['PATH'] = ':'.join(str(gnat / p / 'bin') for p in
    ['gnat-aarch64-linux-16.1.0-1', 'gprbuild-aarch64-linux-26.0.0-1',
     'gnatprove-aarch64-linux-16.1.0-1']) + ':' + environment.get('PATH', '/usr/bin')
environment['GPR_PROJECT_PATH'] = str(gnat / 'gnatprove-aarch64-linux-16.1.0-1/lib/gnat') + ':' + str(gnat / 'auxiliary/share/gpr')
environment = successor_support.child_environment(root, environment)
child = ([str(gnat / 'gprbuild-aarch64-linux-26.0.0-1/bin/gprbuild'), '-p', '-j2', '-P', 'core/worldline_core.gpr']
         if mode == 'build' else ['/usr/bin/python3', '-m', 'unittest', '-v',
            'test_resource_kernel', 'test_resource_policy', 'test_recovery_kernel',
            'test_resource_ledger', 'test_resource_headroom', 'test_reservation_lifecycle'])
if mode == 'pending-build':
    child = [str(gnat / 'gprbuild-aarch64-linux-26.0.0-1/bin/gprbuild'), '-p', '-j2', '-P', 'pending-component/pending.gpr']
if mode == 'pending-tests':
    child = ['/usr/bin/python3', '-m', 'unittest', '-v', 'test_evaluation_pending']
if mode == 'admission-tests':
    child = ['/usr/bin/python3', '-m', 'unittest', '-v', 'test_admission']
if mode == 'evaluation-tests':
    child = ['/usr/bin/python3', '-m', 'unittest', '-v', 'test_evaluation_history']
if mode == 'direct-build':
    child = [str(gnat / 'gprbuild-aarch64-linux-26.0.0-1/bin/gprbuild'), '-p', '-j2', '-P', 'evaluation-history-tests/tests.gpr']
if mode == 'direct-tests':
    child = [str(source / 'obj/evaluation-history-tests/test_history')]
if mode == 'legacy-direct-build':
    child = [str(gnat / 'gprbuild-aarch64-linux-26.0.0-1/bin/gprbuild'), '-p', '-j2', '-P', 'reservation-tests/tests.gpr']
if mode == 'legacy-direct-tests':
    child = [str(source / 'obj/reservation-tests/test_lifecycle')]
if mode == 'resource-direct-build':
    child = [str(gnat / 'gprbuild-aarch64-linux-26.0.0-1/bin/gprbuild'), '-p', '-j2', '-P', 'resource-tests/resource_tests.gpr']
if mode == 'resource-direct-tests':
    child = [str(source / 'resource-tests/bin/resource_tests')]
if mode == 'transition-direct-build':
    child = [str(gnat / 'gprbuild-aarch64-linux-26.0.0-1/bin/gprbuild'), '-p', '-j2', '-P', 'transition-tests/tests.gpr']
if mode == 'transition-direct-tests':
    child = [str(source / 'obj/transition-tests/test_transition')]
if mode == 'completion-build':
    child = [str(gnat / 'gprbuild-aarch64-linux-26.0.0-1/bin/gprbuild'), '-p', '-j2', '-P', 'completion-tests/completion_tests.gpr']
if mode == 'completion-tests':
    child = [str(source / 'obj/completion-tests/test_completion')]
if mode == 'pending-v2-tests':
    child = ['/usr/bin/python3', '-m', 'unittest', '-v', 'test_evaluation_pending_requirements']
if mode == 'terminal-tests':
    child = ['/usr/bin/python3', '-m', 'unittest', '-v', 'test_evaluation_terminal']
if mode == 'roster-d2-python-tests':
    child = ['/usr/bin/python3', '-m', 'unittest', '-v', 'test_evaluation_roster_d2']
if mode == 'roster-d2-build':
    child = [str(gnat / 'gprbuild-aarch64-linux-26.0.0-1/bin/gprbuild'), '-p', '-j2', '-P', 'roster-d2-tests/roster_d2_tests.gpr']
if mode == 'roster-d2-tests':
    child = [str(source / 'obj/roster-d2-tests/test_roster_d2')]
if mode == 'report-facts-build':
    child = [str(gnat / 'gprbuild-aarch64-linux-26.0.0-1/bin/gprbuild'), '-p', '-j2', '-P', 'report-facts-tests/report_facts_tests.gpr']
if mode == 'report-facts-tests':
    child = [str(source / 'obj/report-facts-tests/test_report_facts')]
if mode == 'raw-observation-tests':
    child = ['/usr/bin/python3', '-m', 'unittest', '-v', 'test_raw_observation']
if mode == 'core-all-source-build':
    child = [str(gnat / 'gprbuild-aarch64-linux-26.0.0-1/bin/gprbuild'), '-p', '-j2', '-c', '-U', '-P', 'core/worldline_core_sources.gpr']
if mode == 'proof-source-tests':
    child = ['/usr/bin/python3', '-m', 'unittest', '-v', 'test_proof_source_inventory']
if mode == 'wire-build':
    child = [str(gnat / 'gprbuild-aarch64-linux-26.0.0-1/bin/gprbuild'), '-p', '-j2', '-P', 'evaluation-wire-tests/evaluation_wire_tests.gpr']
if mode == 'wire-tests':
    child = [str(source / 'obj/evaluation-wire-tests/test_evaluation_wire')]
if mode == 'authority-build':
    child = [str(gnat / 'gprbuild-aarch64-linux-26.0.0-1/bin/gprbuild'), '-p', '-j2', '-P', 'evaluation-authority-tests/evaluation_authority_tests.gpr']
if mode == 'authority-tests':
    child = [str(source / 'obj/evaluation-authority-tests/test_evaluation_authority')]
if mode == 'default-tests':
    child = ['/usr/bin/python3', '-m', 'unittest', '-v', 'test_raw_evaluation_default']
if mode == 'metadata-tests':
    child = ['/usr/bin/python3', '-m', 'unittest', '-v', 'test_evaluation_row_projection']
if mode == 'staged-tests':
    child = ['/usr/bin/python3', '-m', 'unittest', '-v', 'test_staged_authority_callbacks']
if mode == 'core-abi-tests':
    child = ['/usr/bin/python3', '-m', 'unittest', '-v', 'test_core_abi']
if mode == 'store-tests':
    child = ['/usr/bin/python3', '-m', 'unittest', '-v', 'test_store']
if mode == 'revalidation-tests':
    child = ['/usr/bin/python3', '-m', 'unittest', '-v', 'test_revalidation_binding']
if mode == 'transaction-tests':
    child = ['/usr/bin/python3', '-m', 'unittest', '-v', 'test_transaction']
if mode == 'finalization-tests':
    child = ['/usr/bin/python3', '-m', 'unittest', '-v', 'test_finalize']
if mode == 'finalization-kernel-tests':
    child = ['/usr/bin/python3', '-m', 'unittest', '-v', 'test_finalization_kernel']
if mode == 'finalization-producer-tests':
    child = ['/usr/bin/python3', '-m', 'unittest', '-v', 'test_finalization_producer']
if mode == 'artifact-build':
    child = [str(gnat / 'gprbuild-aarch64-linux-26.0.0-1/bin/gprbuild'), '-p', '-j2', '-P', 'artifact-tests/canonical_artifact_tests.gpr']
if mode == 'artifact-tests':
    child = [str(source / 'obj/artifact-tests/test_canonical_artifacts')]
if mode == 'native-build':
    child = ['/usr/bin/python3', '-B', str(source / 'native/build_guard.py'), str(root / 'native-artifacts')]
if mode == 'native-component-tests':
    child = ['/usr/bin/python3', '-B', '-m', 'unittest', '-v', 'test_examiner_native_guard', 'test_examiner_native_generators']
if mode == 'entry-component-tests':
    environment['WORLDLINE_PRIVATE_EVALUATOR_TEST'] = '1'
    child = ['/usr/bin/python3', '-m', 'unittest', '-v', 'test_examiner_entry_code', 'test_examiner_entry_retention', 'test_examiner_bound_loader', 'test_finalization_journal_sequence', 'test_tagged_object_cursor', 'test_private_evaluator', 'test_kernel_role_observer', 'test_namespace_lifetime', 'test_private_acquisition_terminal', 'test_evaluation_terminal', 'test_raw_observation']
if mode == 'acquisition-regression-tests':
    environment['WORLDLINE_PRIVATE_EVALUATOR_TEST'] = '1'
    child = ['/usr/bin/python3', '-m', 'revalidation_diagnostic', '-v', 'test_raw_process_ownership', 'test_agent_acquisition_ownership', 'test_causal', 'test_netguard', 'test_systemd', 'test_revalidation_binding', 'test_causal_root_coverage', 'test_examiner_audit', 'test_kernel_role_observer', 'test_namespace_lifetime']
if mode == 'recovery-integration-tests':
    child = ['/usr/bin/python3', '-m', 'unittest', '-v', 'test_recovery_witness_relation', 'test_recovery_observation_codec', 'test_recovery_authority', 'test_resulting_requirement_caller']

if mode == 'resource-runtime-controls':
    child = ['/usr/bin/python3', '-m', 'unittest', '-v', 'test_admission_custody_repair', 'test_admission_terminal_repair', 'test_recovery_packet_producer']
if mode == 'recovery-domain-controls':
    child = ['/usr/bin/python3', '-m', 'unittest', '-v', 'test_recovery_witness_relation_v3']
if mode == 'recovery-epoch-build':
    child = [str(gnat / 'gprbuild-aarch64-linux-26.0.0-1/bin/gprbuild'), '-p', '-j2', '-P', 'recovery-epoch-tests/recovery_epoch_tests.gpr', '-o', str(source / 'obj/test_recovery_epochs')]
if mode == 'recovery-epoch-tests':
    child = [str(source / 'obj/test_recovery_epochs')]
if mode == 'serializer-controls':
    child = ['/usr/bin/python3', '-m', 'unittest', '-v', 'test_diagnostic_value_stream']

if mode == authorization.MODE:
    child = FORMAL_COMMAND

# Complete original source keyset before any target child, excluding only the
# separately owned generated output partitions declared by the launch proposal.
def observe_source():
    allowed_outputs = ('obj/', 'lib/', 'resource-tests/obj/', 'resource-tests/bin/')
    found = {}
    for f in sorted(source.rglob('*')):
        if not f.is_file():
            continue
        rel = str(f.relative_to(source))
        if rel.startswith(allowed_outputs):
            continue
        found[rel] = digest(f)
    return found

write(receipt / 'private-inputs-before.json', successor_support.check_source_and_dependency(root))
runtime_closure = json.loads((root / 'runtime-closure.json').read_text())
runtime_inventory.verify_environment(runtime_closure['spec'], environment)
runtime_before = runtime_inventory.observe(runtime_closure['spec'])
write(receipt / 'runtime-closure-before.json', runtime_before)
assert runtime_before == runtime_closure['inventory'], 'Python/cache/spool closure drift'

baseline = json.loads((root / 'action-baseline.json').read_text())
assert observe_source() == baseline['source_files'], 'source differs from frozen composition'
files = {}
source_modes_before = {p: oct((source / p).stat().st_mode & 0o7777) for p in baseline['source_files']}
assert source_modes_before == json.loads((root / 'source-composition.json').read_text())['source_modes']
for relative_text in baseline['source_files']:
    path = source / relative_text
    destination = receipt / 'inputs' / relative_text
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, destination)
    files[relative_text] = {'sha256': digest(path), 'bytes': path.stat().st_size, 'mode': path.stat().st_mode & 0o7777}
for directory in ['native', 'artifact-tests', 'evaluation-authority-tests', 'evaluation-wire-tests', 'report-facts-tests', 'roster-d2-tests', 'completion-tests', 'transition-tests', 'core', 'runtime', 'tests', 'evaluation-history-tests', 'reservation-tests', 'resource-tests', 'pending-component', 'recovery-epoch-tests']:
    for path in sorted((source / directory).rglob('*')):
        if path.is_file() and not {'__pycache__', 'obj', 'bin'}.intersection(path.relative_to(source).parts):
            relative = path.relative_to(source)
            destination = receipt / 'inputs' / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
            files[str(relative)] = {'sha256': digest(path), 'bytes': path.stat().st_size}
if mode in ('entry-component-tests', 'acquisition-regression-tests', 'finalization-kernel-tests', 'finalization-producer-tests', 'artifact-tests', 'authority-tests', 'default-tests', 'metadata-tests', 'staged-tests', 'core-abi-tests', 'store-tests', 'revalidation-tests', 'transaction-tests', 'finalization-tests', 'wire-tests', 'proof-source-tests', 'report-facts-tests', 'raw-observation-tests', 'terminal-tests', 'roster-d2-python-tests', 'roster-d2-tests', 'completion-tests', 'pending-v2-tests', 'transition-direct-tests', 'pending-tests', 'tests', 'admission-tests', 'evaluation-tests', 'direct-tests', 'legacy-direct-tests', 'resource-direct-tests', 'recovery-integration-tests', 'resource-runtime-controls', 'recovery-domain-controls', 'recovery-epoch-tests', 'serializer-controls'):
    library = source / 'lib/libworldline_core.so'
    shutil.copy2(library, receipt / 'libworldline_core.so')
    files[str(library.relative_to(source))] = {'sha256': digest(library), 'bytes': library.stat().st_size}
scope = ['/usr/bin/systemd-run', '--user', '--scope', '--unit=codex-worldline-full-formal-diagnostic-v8-' + mode + '-' + label,
         '-p', 'MemoryMax=8G', '-p', 'MemorySwapMax=0',
         '-p', 'RuntimeMaxSec=840s', '-p', 'TimeoutStopSec=15s', '/usr/bin/python3', str(Path(__file__).resolve()),
         'child', str(receipt)]
template = json.loads((root / 'tool-inventory-template.json').read_text())
spec = template['tool_inventory_spec']
observed_tools = tool_inventory.observe(spec)
write(receipt / 'complete-tools-before.json', observed_tools)
assert observed_tools == baseline['tool_inventory'], 'tool closure differs from reviewed baseline'
protected_environment = {k: environment.get(k) for k in spec['effective_environment']}
write(receipt / 'effective-environment-before.json', protected_environment)
assert protected_environment == spec['effective_environment'], 'protected environment drift'
manager = subprocess.run(['/usr/bin/systemctl', '--user', 'show-environment'],
    env=environment, capture_output=True, text=True, check=True, timeout=30)
manager_values = dict(line.split('=', 1) for line in manager.stdout.splitlines() if '=' in line)
manager_observed = {k: manager_values.get(k) for k in baseline['manager_environment']}
write(receipt / 'manager-environment-before.json', manager_observed)
assert manager_observed == baseline['manager_environment'], 'manager environment drift'

vendors = json.loads((root / 'vendor-template.json').read_text())
observed_vendors = {r['original']: digest(Path(r['original'])) for r in vendors}
assert all(observed_vendors[r['original']] == r['sha256'] for r in vendors)
write(receipt / 'vendors-before.json', observed_vendors)
assert observed_vendors == baseline['vendor_inventory'], 'vendor differs from reviewed baseline'
if mode in ('artifact-tests', 'authority-tests', 'wire-tests', 'report-facts-tests', 'roster-d2-tests', 'completion-tests', 'transition-direct-tests', 'direct-tests', 'legacy-direct-tests', 'resource-direct-tests', 'recovery-epoch-tests'):
    binary = Path(child[0])
    shutil.copy2(binary, receipt / binary.name)
    files[str(binary.relative_to(source))] = {'sha256': digest(binary), 'bytes': binary.stat().st_size}

native_inputs = native_inventory.observe()
write(receipt / 'native-inputs-before.json', native_inputs)
assert native_inputs == json.loads((root / 'native-input-baseline.json').read_text()), 'native compiler/header/library inputs changed'
native_artifacts_before = {}
native_build_dependency = None
native_directory = root / 'native-artifacts'
if mode not in ('native-build', authorization.MODE):
    build_result_path = root / 'evidence/native-build-v1/result.json'
    build_result_bytes = build_result_path.read_bytes()
    build_result = json.loads(build_result_bytes)
    assert build_result['scope_wait'] == 0 and build_result['child_wait']['returncode'] == 0 and build_result['inputs_unchanged'] is True
    native_build = json.loads((native_directory / 'build.json').read_text())
    native_library = native_directory / 'libworldline_examiner_guard.so'
    assert native_build['artifact'] == str(native_library) and native_build['sha256'] == digest(native_library)
    assert native_build['compilerReturncode'] == 0
    (receipt / 'native-artifacts').mkdir()
    for path in (native_library, native_directory / 'build.json'):
        native_artifacts_before[str(path)] = {'sha256': digest(path), 'bytes': path.stat().st_size, 'mode': path.stat().st_mode & 0o7777}
        shutil.copy2(path, receipt / 'native-artifacts' / path.name)
    assert native_artifacts_before == build_result['native_artifacts_after'], 'native artifacts differ from retained actual build result'
    native_build_dependency = {'path': str(build_result_path), 'sha256': hashlib.sha256(build_result_bytes).hexdigest(), 'bytes': len(build_result_bytes)}
    assert digest(build_result_path) == native_build_dependency['sha256'], 'prior native build result changed during read'
    (receipt / 'native-build-result.json').write_bytes(build_result_bytes)
proof_data_closure = json.loads((root / 'proof-data-closure.json').read_text())
proof_data_before = proof_data_inventory.observe(proof_data_closure['spec'])
write(receipt / 'proof-data-before.json', proof_data_before)
assert proof_data_before == proof_data_closure['inventory'], 'proof configuration/install data drift'
proof_elf_before = proof_elf_inventory.observe(observed_tools)
write(receipt / 'proof-elf-before.json', proof_elf_before)
assert proof_elf_before == json.loads((root / 'proof-elf-baseline.json').read_text()), 'proof ELF closure drift'
write(receipt / 'inputs-before.json', {'at': now(), 'child_argv': child, 'scope_argv': scope,
    'source_library': files, 'source_modes': source_modes_before, 'cwd': str(source), 'formal_diagnostic_only': mode == authorization.MODE,
    'native_artifacts_before': native_artifacts_before,
    'native_build_dependency': native_build_dependency,
    'native_input_baseline_sha256': digest(root / 'native-input-baseline.json'),
    'tools': {path: digest(Path(path).resolve()) for path in ['/usr/bin/python3', '/usr/bin/systemd-run', child[0]]},
    'runner_sha256': digest(Path(__file__)),
    'environment': {k: environment[k] for k in ['PATH', 'GPR_PROJECT_PATH', 'PYTHONPATH',
        'WORLDLINE_BUILD', 'WORLDLINE_CORE_LIB', 'PENDING_OBJECT_DIR', 'PENDING_LIBRARY_DIR',
        'XDG_RUNTIME_DIR', 'DBUS_SESSION_BUS_ADDRESS']},
    'additive_control_environment': {'WORLDLINE_PRIVATE_EVALUATOR_TEST': environment.get('WORLDLINE_PRIVATE_EVALUATOR_TEST')} if mode in ('entry-component-tests', 'acquisition-regression-tests') else {},
    'role': 'Standalone exact full strict formal diagnostic only; no ordinary outcome, architectural qualification, body coverage or phase acceptance'})
scope_unit = scope[3].split('=', 1)[1]
if not scope_unit.endswith('.scope'):
    scope_unit += '.scope'
# The owner and systemd both enforce the original840; original core0 remains inherited.
resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
scope_wait = successor_support.capture_owned(
    scope, receipt, 'scope', 840, cwd=source, env=environment,
    term_seconds=15, kill_seconds=5, hard_deadline=MAIN_DEADLINE,
    on_started=lambda process: successor_support.retained_owner_record(
        receipt / 'scope-start.json', {'at': now(), 'pid': process.pid,
        'argv': scope, 'scope_unit': scope_unit, 'actual_scope_launch_observed': True}),
    on_stop=lambda number: successor_support.signal_recorded_scope(
        receipt, scope_unit, Path(__file__).resolve(), number))
code = scope_wait['returncode']

post_error = None
result = {'at': now(), 'scope_wait': code, 'inputs_unchanged': None,
          'child_wait': None, 'scope_owner_control': scope_wait,
          'child_wait_binding_error': None, 'early_wait_retention_errors': [],
          'after_readback_status': 'NOT_COMPLETED',
          'original_targets': 'OPEN_UNCHANGED', 'no_proof_claim': True}
try:
    with successor_support.owner_signals(MAIN_DEADLINE):
        wait_binding = successor_support.bind_owned_child_wait(
            receipt, Path(__file__).resolve(), child, scope, scope_unit, scope_wait)
        result['child_wait'] = wait_binding['child_wait']
        result['child_wait_binding'] = wait_binding['receipt_observations']
        result['child_wait_binding_error'] = wait_binding['validation_error']
        # This durable checkpoint precedes every expensive post-run closure observer.
        result['early_wait_retention_errors'] = successor_support.retain_terminal_or_refusal(
            receipt / 'scope-return-child-wait.json', result)
        native_inputs_after = native_inventory.observe()
        write(receipt / 'native-inputs-after.json', native_inputs_after)
        native_artifacts_after = {}
        for path in (native_directory / 'libworldline_examiner_guard.so', native_directory / 'build.json'):
            if path.is_file():
                native_artifacts_after[str(path)] = {'sha256': digest(path), 'bytes': path.stat().st_size, 'mode': path.stat().st_mode & 0o7777}
                (receipt / 'native-artifacts-after').mkdir(exist_ok=True)
                shutil.copy2(path, receipt / 'native-artifacts-after' / path.name)
        unchanged = all(digest(source / p) == v['sha256'] for p, v in files.items())
        tools_after = tool_inventory.observe(spec)
        write(receipt / 'complete-tools-after.json', tools_after)
        vendors_after = {r['original']: digest(Path(r['original'])) for r in vendors}
        write(receipt / 'vendors-after.json', vendors_after)
        unchanged = unchanged and tools_after == observed_tools and vendors_after == observed_vendors
        unchanged = unchanged and observe_source() == baseline['source_files']
        runtime_after = runtime_inventory.observe(runtime_closure['spec'])
        write(receipt / 'runtime-closure-after.json', runtime_after)
        unchanged = unchanged and runtime_after == runtime_before
        unchanged = unchanged and native_inputs_after == native_inputs
        proof_elf_after = proof_elf_inventory.observe(tools_after)
        write(receipt / 'proof-elf-after.json', proof_elf_after)
        proof_data_after = proof_data_inventory.observe(proof_data_closure['spec'])
        write(receipt / 'proof-data-after.json', proof_data_after)
        source_modes_after = {p: oct((source / p).stat().st_mode & 0o7777) for p in baseline['source_files']}
        write(receipt / 'source-modes-after.json', source_modes_after)
        unchanged = unchanged and proof_elf_after == proof_elf_before and proof_data_after == proof_data_before and source_modes_after == source_modes_before
        unchanged = unchanged and (native_build_dependency is None or digest(Path(native_build_dependency['path'])) == native_build_dependency['sha256'])
        unchanged = unchanged and (native_build_dependency is None or native_artifacts_after == native_artifacts_before)
        private_after = successor_support.retained_readback(root)
        write(receipt / 'private-inputs-after.json', private_after)
        write(receipt / 'owned-generated-output-inventory.json', successor_support.generated_outputs(root))
        unchanged = unchanged and private_after['matches']
        result.update(at=now(), inputs_unchanged=unchanged,
            native_artifacts_before=native_artifacts_before, native_artifacts_after=native_artifacts_after,
            native_inputs_unchanged=native_inputs_after == native_inputs,
            after_readback_status='COMPLETE')
except BaseException as error:
    post_error = error
    result['post_run_readback_error'] = successor_support.owner_error('post_run_readback', error)
    result['after_readback_status'] = 'INTERRUPTED_OR_UNAVAILABLE'
finally:
    result['scope_owner_control'] = scope_wait
    with successor_support.owner_signals(MAIN_DEADLINE):
        terminal_errors = successor_support.retain_terminal_or_refusal(receipt / 'result.json', result)
if post_error is not None:
    raise post_error
if terminal_errors:
    raise RuntimeError('Actual waits retained separately; result retention failed: ' + repr(terminal_errors))
if result['early_wait_retention_errors']:
    raise RuntimeError('Early actual-wait checkpoint retention failed: ' + repr(result['early_wait_retention_errors']))
if result['child_wait_binding_error'] is not None:
    raise RuntimeError('Owned child-wait binding failed: ' + repr(result['child_wait_binding_error']))
print(json.dumps(result, indent=2))
print((receipt / 'scope.stderr').read_text())
if (receipt / 'child.stderr').exists():
    print((receipt / 'child.stderr').read_text())

assert unchanged, 'frozen source/tool/vendor changed'
raise SystemExit(successor_support.owner_exit_code(scope_wait))
