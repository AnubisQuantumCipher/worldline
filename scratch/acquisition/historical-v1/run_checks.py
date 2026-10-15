from pathlib import Path
import datetime, hashlib, json, os, resource, shutil, subprocess, sys
sys.dont_write_bytecode = True
import tool_inventory
import native_inventory
import runtime_inventory
import integrity
import successor_support
import restored_original_domains

root = Path(__file__).resolve().parent
source = root / 'source'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

mode = sys.argv[1]
if mode == 'child':
    receipt = Path(sys.argv[2])
    integrity.check_frame()
    write(receipt / 'private-inputs-child-before.json', successor_support.check_current_inputs(root))
    expected_environment = json.loads((root / 'tool-inventory-template.json').read_text())['tool_inventory_spec']['effective_environment']
    assert {key: os.environ.get(key) for key in expected_environment} == expected_environment, 'actual ordinary child environment drift'
    assert all(os.environ.get(key) is None for key in successor_support.DEPENDENCY_UNSET)
    config = json.loads((receipt / 'inputs-before.json').read_text())
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
    additional_deadline = config.get('additional_timeout_seconds')
    assert additional_deadline in (None, 180)
    timed_out = False
    with (receipt / 'child.stdout').open('w') as out, (receipt / 'child.stderr').open('w') as err:
        process = subprocess.Popen(config['child_argv'], cwd=source, stdout=out, stderr=err)
        try:
            code = process.wait(timeout=additional_deadline)
        except subprocess.TimeoutExpired:
            timed_out = True
            process.terminate()
            code = process.wait()
    write(receipt / 'child-wait.json', {'at': now(), 'pid': process.pid,
          'argv': config['child_argv'], 'returncode': code,
          'additional_timeout_seconds': additional_deadline, 'additional_deadline_expired': timed_out,
          'meaning': 'actual subprocess.Popen.wait return value; no proof acceptance'})
    raise SystemExit(1 if timed_out and code == 0 else code)

assert mode in restored_original_domains.MODES or mode in ('freshness-json-object-order-additional-controls', 'execution-evidence-boundary-additional-controls') or mode in ('native-build', 'native-component-tests', 'entry-component-tests', 'acquisition-regression-tests', 'finalization-kernel-tests', 'finalization-producer-tests', 'artifact-build', 'artifact-tests', 'authority-build', 'authority-tests', 'default-tests', 'metadata-tests', 'staged-tests', 'core-abi-tests', 'store-tests', 'revalidation-tests', 'transaction-tests', 'finalization-tests', 'core-all-source-build', 'proof-source-tests', 'wire-build', 'wire-tests', 'report-facts-build', 'report-facts-tests', 'raw-observation-tests', 'terminal-tests', 'roster-d2-python-tests', 'roster-d2-build', 'roster-d2-tests', 'completion-build', 'completion-tests', 'pending-v2-tests', 'transition-direct-build', 'transition-direct-tests', 'pending-build', 'pending-tests', 'build', 'tests', 'admission-tests', 'evaluation-tests', 'direct-build', 'direct-tests',
    'legacy-direct-build', 'legacy-direct-tests', 'resource-direct-build', 'resource-direct-tests', 'recovery-integration-tests', 'resource-runtime-controls', 'recovery-domain-controls', 'recovery-epoch-build', 'recovery-epoch-tests', 'serializer-controls', 'root-custody-context-build', 'root-custody-context-controls', 'capability-native-binding-simulation-controls', 'archive-leaf-build', 'archive-leaf-controls', 'root-custody-replay-build', 'root-custody-replay-controls', 'root-custody-abandon-build', 'root-custody-abandon-controls', 'chain-bounds-tests-test-bounds-build', 'chain-bounds-tests-test-bounds', 'decision-correspondence-tests-test-completion-correspondence-build', 'decision-correspondence-tests-test-completion-correspondence', 'decision-correspondence-tests-test-transition-correspondence-build', 'decision-correspondence-tests-test-transition-correspondence', 'decision-correspondence-tests-test-history-correspondence-build', 'decision-correspondence-tests-test-history-correspondence', 'decision-correspondence-tests-test-raw-roster-correspondence-build', 'decision-correspondence-tests-test-raw-roster-correspondence', 'decision-correspondence-tests-test-run-metadata-correspondence-build', 'decision-correspondence-tests-test-run-metadata-correspondence', 'epoch-correspondence-core-test-epoch-correspondence-build', 'epoch-correspondence-core-test-epoch-correspondence', 'epoch-correspondence-pending-test-epoch-correspondence-build', 'epoch-correspondence-pending-test-epoch-correspondence', 'explicit-recovery-marker-tests-test-explicit-recovery-markers-build', 'explicit-recovery-marker-tests-test-explicit-recovery-markers', 'finalization-value-controls-test-finalization-values-build', 'finalization-value-controls-test-finalization-values', 'finalization-value-controls-test-finalization-parent-values-build', 'finalization-value-controls-test-finalization-parent-values', 'finalization-value-controls-test-finalization-projection-build', 'finalization-value-controls-test-finalization-projection', 'protocol-adapter-tests-test-protocol-adapter-build', 'protocol-adapter-tests-test-protocol-adapter', 'recovery-protocol-tests-test-protocol-build', 'recovery-protocol-tests-test-protocol', 'request-abandon-controls-request-abandon-controls-build', 'request-abandon-controls-request-abandon-controls', 'resource-ledger-correspondence-tests-test-resource-ledger-correspondence-build', 'resource-ledger-correspondence-tests-test-resource-ledger-correspondence', 'resources-prefix-correspondence-tests-test-resources-prefix-correspondence-build', 'resources-prefix-correspondence-tests-test-resources-prefix-correspondence', 'tests-resource-policy-smoke-build', 'tests-resource-policy-smoke', 'tests-worldline-core-tests-build', 'tests-worldline-core-tests', 'tests-worldline-core-fuzz-build', 'tests-worldline-core-fuzz', 'use-reservation-tests-use-reservation-tests-build', 'use-reservation-tests-use-reservation-tests', 'wire-initialization-tests-test-wire-initialization-build', 'wire-initialization-tests-test-wire-initialization', 'test-context-cast-lifetime-controls', 'test-finalization-cast-lifetime-controls', 'test-finalization-agent-binding-controls', 'test-finalization-agent-binding-additional-controls', 'test-finalization-agent-binding-producer-controls', 'test-custody-foreign-key-capture-controls', 'test-custody-provision-kernel-controls', 'test-custody-subject-primitives-controls', 'test-custody-v2-explicit-provision-controls', 'test-custody-v2-sql-capture-controls', 'test-root-worker-codec-lossless-controls')
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

if mode == 'root-custody-context-build':
    child = [str(gnat / 'gprbuild-aarch64-linux-26.0.0-1/bin/gprbuild'), '-p', '-j2', '-P', 'root-custody-context-controls/controls.gpr']
if mode == 'root-custody-context-controls':
    child = [str(source / 'obj/root-custody-context-controls/root_custody_context_controls')]

if mode == 'capability-native-binding-simulation-controls':
    child = ['/usr/bin/python3', '-m', 'unittest', '-v', 'test_capability_native_binding_simulation']

tail_enrollment = json.loads((root / 'tail-enrollment.json').read_text())
from enrollment_integrity import validate as validate_enrollment
validate_enrollment(json.loads((root / 'planned-actions.json').read_text()), tail_enrollment, json.loads((root / 'scope-map.json').read_text()), root)
tail_modes = tail_enrollment['ordered_tail_modes']
control_modes = tuple(tail_enrollment['controls'])
if mode in tail_modes:
    control_mode = mode if mode in control_modes else next(k for k,v in tail_enrollment['controls'].items() if v['build_mode'] == mode)
    control_spec = tail_enrollment['controls'][control_mode]
    if 'python_module' in control_spec:
        child = ['/usr/bin/python3', *control_spec.get('python_flags', []), '-m', 'unittest', '-v', control_spec['python_module']]
    elif mode == control_spec['build_mode']:
        child = [str(gnat / 'gprbuild-aarch64-linux-26.0.0-1/bin/gprbuild'), '-p', '-j2', '-P', control_spec['project']]
    else:
        child = [str(source / control_spec['binary'])]

additional_actions = json.loads((root / 'additional-actions.json').read_text())
additional_modes = tuple(row['mode'] for row in additional_actions)
import restored_original_domains
assert additional_modes == restored_original_domains.ORIGINAL_ADDITIONS + restored_original_domains.MODES
additional_action = next((row for row in additional_actions if row['mode'] == mode), None)
if additional_action is not None:
    assert 'PYTHONOPTIMIZE' not in os.environ and '-O' not in additional_action['child_argv'] and '-OO' not in additional_action['child_argv']
    child = additional_action['child_argv']
    enrollment = json.loads((root / 'additional-command-enrollment-with-original-restored-domains.json').read_text())
    command = next(row for row in enrollment['additional_commands'] if row['mode'] == mode)
    assert command == {key: value for key, value in additional_action['additional_command'].items() if key != 'materialized_runner'}
    command = additional_action['additional_command']
    assert command['test_timeout_seconds'] == 180 and command['assertions_required'] is True
    if command.get('restored_original_domain') is True:
        restored_original_domains.validate(root, additional_action, command, source)
        if command['kind'] == 'run':
            build_mode = command['mode'].replace('-controls', '-build')
            built = json.loads((root / 'evidence' / (build_mode + '-v1') / 'restored-built-binary.json').read_text())
            binary = source / command['binary']
            assert built == {'path': str(binary), 'sha256': digest(binary), 'bytes': binary.stat().st_size, 'mode': binary.stat().st_mode & 0o7777}
            shutil.copy2(binary, receipt / binary.name)
            restored_binary_pin = {'sha256': digest(binary), 'bytes': binary.stat().st_size, 'mode': binary.stat().st_mode & 0o7777}
    elif 'external_runner' in command:
        successor_support.matched(command['external_runner'])
        runner = successor_support.matched(command['materialized_runner'])
        assert child == ['/usr/bin/python3', '-B', str(runner)]
        assert {key: command['materialized_runner'][key] for key in ('sha256', 'bytes', 'mode')} == {key: command['external_runner'][key] for key in ('sha256', 'bytes', 'mode')}
        shutil.copy2(runner, receipt / runner.name)
    else:
        assert child == ['/usr/bin/python3', '-B', str(source / command['source_relative_runner'])]

# Complete original source keyset before any target child, excluding only the
# separately owned generated output partitions declared by the launch proposal.
def observe_source():
    allowed_outputs = ('bin/', 'explicit-recovery-marker-tests/bin/', 'explicit-recovery-marker-tests/obj/', 'lib/', 'obj/', 'protocol-adapter-tests/bin/', 'protocol-adapter-tests/obj/', 'recovery-protocol-tests/bin/', 'recovery-protocol-tests/obj/', 'resource-tests/bin/', 'resource-tests/obj/', 'use-reservation-tests/bin/', 'use-reservation-tests/obj/', 'wire-initialization-tests/bin/', 'wire-initialization-tests/obj/', 'physical-value-controls/obj/', 'physical-value-controls/bin/', 'canonical-exchange-tests/obj/', 'canonical-exchange-tests/bin/', 'canonical-owner-completion-tests/obj/', 'canonical-owner-completion-tests/bin/')
    found = {}
    for f in sorted(source.rglob('*')):
        if not f.is_file():
            continue
        rel = str(f.relative_to(source))
        if rel.startswith(allowed_outputs):
            continue
        found[rel] = digest(f)
    return found

write(receipt / 'private-inputs-before.json', successor_support.check_current_inputs(root))
runtime_closure = json.loads((root / 'runtime-closure.json').read_text())
runtime_inventory.verify_environment(runtime_closure['spec'], environment)
runtime_before = runtime_inventory.observe(runtime_closure['spec'])
write(receipt / 'runtime-closure-before.json', runtime_before)
assert runtime_before == runtime_closure['inventory'], 'Python/cache/spool closure drift'

baseline = json.loads((root / 'action-baseline.json').read_text())
assert observe_source() == baseline['source_files'], 'source differs from frozen composition'
files = {}
for relative, entry in integrity.check_source().items():
    if entry['kind'] == 'file':
        path = source / relative
        destination = receipt / 'inputs' / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
        files[relative] = {key: entry[key] for key in ('sha256', 'bytes', 'mode')}
write(receipt / 'complete-source-inputs-before.json', integrity.check_source())
if mode in additional_modes or mode in ('entry-component-tests', 'acquisition-regression-tests', 'finalization-kernel-tests', 'finalization-producer-tests', 'artifact-tests', 'authority-tests', 'default-tests', 'metadata-tests', 'staged-tests', 'core-abi-tests', 'store-tests', 'revalidation-tests', 'transaction-tests', 'finalization-tests', 'wire-tests', 'proof-source-tests', 'report-facts-tests', 'raw-observation-tests', 'terminal-tests', 'roster-d2-python-tests', 'roster-d2-tests', 'completion-tests', 'pending-v2-tests', 'transition-direct-tests', 'pending-tests', 'tests', 'admission-tests', 'evaluation-tests', 'direct-tests', 'legacy-direct-tests', 'resource-direct-tests', 'recovery-integration-tests', 'resource-runtime-controls', 'recovery-domain-controls', 'recovery-epoch-tests', 'serializer-controls', 'root-custody-context-controls', 'archive-leaf-controls', 'root-custody-replay-controls', 'root-custody-abandon-controls') or mode in control_modes:
    library = source / 'lib/libworldline_core.so'
    shutil.copy2(library, receipt / 'libworldline_core.so')
    files[str(library.relative_to(source))] = {'sha256': digest(library), 'bytes': library.stat().st_size}
scope = ['/usr/bin/systemd-run', '--user', '--scope', '--unit=codex-worldline-terminal-witness-lifetime-successor-v1-' + mode + '-' + label,
         '-p', 'MemoryMax=8G', '-p', 'MemorySwapMax=0', '/usr/bin/python3', str(Path(__file__).resolve()),
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
    env=environment, capture_output=True, text=True, check=True)
manager_values = dict(line.split('=', 1) for line in manager.stdout.splitlines() if '=' in line)
manager_observed = {k: manager_values.get(k) for k in baseline['manager_environment']}
write(receipt / 'manager-environment-before.json', manager_observed)
assert manager_observed == baseline['manager_environment'], 'manager environment drift'

vendors = json.loads((root / 'vendor-template.json').read_text())
observed_vendors = {r['original']: digest(Path(r['original'])) for r in vendors}
assert all(observed_vendors[r['original']] == r['sha256'] for r in vendors)
write(receipt / 'vendors-before.json', observed_vendors)
assert observed_vendors == baseline['vendor_inventory'], 'vendor differs from reviewed baseline'
if mode in ('artifact-tests', 'authority-tests', 'wire-tests', 'report-facts-tests', 'roster-d2-tests', 'completion-tests', 'transition-direct-tests', 'direct-tests', 'legacy-direct-tests', 'resource-direct-tests', 'recovery-epoch-tests', 'root-custody-context-controls', 'archive-leaf-controls', 'root-custody-replay-controls', 'root-custody-abandon-controls'):
    binary = Path(child[0])
    shutil.copy2(binary, receipt / binary.name)
    files[str(binary.relative_to(source))] = {'sha256': digest(binary), 'bytes': binary.stat().st_size}

native_inputs = native_inventory.observe()
write(receipt / 'native-inputs-before.json', native_inputs)
assert native_inputs == json.loads((root / 'native-input-baseline.json').read_text()), 'native compiler/header/library inputs changed'
native_artifacts_before = {}
native_build_dependency = None
native_directory = root / 'native-artifacts'
if mode != 'native-build':
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
# Additive tail actions require the complete original ordinary roster first.
# The reviewed enclosing frame must additionally enforce its original admission
# ceiling and continuation gates; these checks grant no launch authority.
if mode in ('root-custody-context-build', 'root-custody-context-controls'):
    enrollment = json.loads((root / 'custody-controls-enrollment.json').read_text())
    predecessors = list(enrollment['original_action_dependencies'])
    if mode == 'root-custody-context-controls':
        predecessors.append({'mode': 'root-custody-context-build', 'label': 'v1'})
    for previous in predecessors:
        prior = root / 'evidence' / (previous['mode'] + '-' + previous['label'])
        waited = json.loads((prior / 'result.json').read_text())
        bound = json.loads((prior / 'inputs-before.json').read_text())
        assert waited['scope_wait'] == 0 and waited['inputs_unchanged'] is True
        assert waited['child_wait'] is not None and waited['child_wait']['returncode'] == 0
        assert bound['runner_sha256'] == digest(Path(__file__)), 'predecessor runner differs'
    if mode == 'root-custody-context-controls':
        built = json.loads((root / 'evidence/root-custody-context-build-v1/custody-built-binary.json').read_text())
        assert built['path'] == str(Path(child[0])) and built['sha256'] == digest(Path(child[0]))

if mode == 'capability-native-binding-simulation-controls':
    enrollment = json.loads((root / 'custody-controls-enrollment.json').read_text())
    predecessors = list(enrollment['original_action_dependencies']) + [{'mode': 'root-custody-context-build', 'label': 'v1'}, {'mode': 'root-custody-context-controls', 'label': 'v1'}]
    for previous in predecessors:
        prior = root / 'evidence' / (previous['mode'] + '-' + previous['label'])
        waited = json.loads((prior / 'result.json').read_text())
        bound = json.loads((prior / 'inputs-before.json').read_text())
        assert waited['scope_wait'] == 0 and waited['inputs_unchanged'] is True
        assert waited['child_wait'] is not None and waited['child_wait']['returncode'] == 0
        assert bound['runner_sha256'] == digest(Path(__file__))
        if previous['mode'] == 'root-custody-context-controls':
            assert waited['custody_controls_completion'] is True

if mode in tail_modes or mode in additional_modes:
    proposal = json.loads((root / 'reviewed-launch-proposal.json').read_text())
    ordered = proposal['launches']
    position = next(i for i,a in enumerate(ordered) if a['mode'] == mode)
    assert [a['mode'] for a in ordered] == tail_enrollment['original_prefix_modes'] + tail_modes + list(additional_modes)
    for previous in ordered[:position]:
        prior = Path(previous['receipt'])
        waited = json.loads((prior / 'result.json').read_text())
        bound = json.loads((prior / 'inputs-before.json').read_text())
        assert waited['scope_wait'] == 0 and waited['inputs_unchanged'] is True
        assert waited['child_wait'] is not None and waited['child_wait']['returncode'] == 0
        assert bound['runner_sha256'] == digest(Path(__file__))
        if previous['mode'] == 'root-custody-context-controls':
            assert waited['custody_controls_completion'] is True
        if previous['mode'] in control_modes:
            assert waited['tail_control_completion'] is True
        if previous['mode'] in additional_modes:
            assert waited['additional_controls_completion'] is True
    if mode in control_modes and 'python_module' not in control_spec:
        build_row = next(a for a in ordered if a['mode'] == control_spec['build_mode'])
        built = json.loads((Path(build_row['receipt']) / 'tail-built-binary.json').read_text())
        executable = source / control_spec['binary']
        assert built == {'path': str(executable), 'sha256': digest(executable), 'bytes': executable.stat().st_size, 'mode': executable.stat().st_mode & 0o7777}

if additional_action is not None and additional_action['additional_command'].get('restored_original_domain') is True and command['kind'] == 'run':
    files[str(binary.relative_to(source))] = restored_binary_pin

write(receipt / 'inputs-before.json', {'at': now(), 'child_argv': child, 'scope_argv': scope,
    'source_library': files, 'cwd': str(source),
    'additional_timeout_seconds': 180 if additional_action is not None else None,
    'native_artifacts_before': native_artifacts_before,
    'native_build_dependency': native_build_dependency,
    'native_input_baseline_sha256': digest(root / 'native-input-baseline.json'),
    'tools': {path: digest(Path(path).resolve()) for path in ['/usr/bin/python3', '/usr/bin/systemd-run', child[0]]},
    'runner_sha256': digest(Path(__file__)),
    'environment': {k: environment[k] for k in ['PATH', 'GPR_PROJECT_PATH', 'PYTHONPATH',
        'WORLDLINE_BUILD', 'WORLDLINE_CORE_LIB', 'PENDING_OBJECT_DIR', 'PENDING_LIBRARY_DIR',
        'XDG_RUNTIME_DIR', 'DBUS_SESSION_BUS_ADDRESS']},
    'additive_control_environment': {'WORLDLINE_PRIVATE_EVALUATOR_TEST': environment.get('WORLDLINE_PRIVATE_EVALUATOR_TEST')} if mode in ('entry-component-tests', 'acquisition-regression-tests') else {},
    'role': 'ordinary complete shared build or explicit finite real-library controls; no heavy proof/campaign/product mutation'})
integrity.check_frame()
with (receipt / 'scope.stdout').open('w') as out, (receipt / 'scope.stderr').open('w') as err:
    process = subprocess.Popen(scope, cwd=source, env=environment, stdout=out, stderr=err,
        preexec_fn=lambda: resource.setrlimit(resource.RLIMIT_CORE, (0, 0)))
    code = process.wait()

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
unchanged = unchanged and (native_build_dependency is None or digest(Path(native_build_dependency['path'])) == native_build_dependency['sha256'])
unchanged = unchanged and (native_build_dependency is None or native_artifacts_after == native_artifacts_before)
private_after = successor_support.retained_readback(root)
write(receipt / 'private-inputs-after.json', private_after)
write(receipt / 'owned-generated-output-inventory.json', successor_support.generated_outputs(root))
unchanged = unchanged and private_after['matches']
if additional_action is not None and 'external_runner' in command:
    successor_support.matched(command['external_runner'])
    successor_support.matched(command['materialized_runner'])
result = {'at': now(), 'scope_wait': code, 'inputs_unchanged': unchanged,
    'native_artifacts_before': native_artifacts_before, 'native_artifacts_after': native_artifacts_after,
    'native_inputs_unchanged': native_inputs_after == native_inputs,
    'child_wait': json.loads((receipt / 'child-wait.json').read_text()) if (receipt / 'child-wait.json').exists() else None,
    'original_targets': 'OPEN_UNCHANGED', 'no_proof_claim': True}
if mode == 'root-custody-context-controls':
    result['custody_controls_completion'] = (
        result['scope_wait'] == 0 and result['child_wait'] is not None
        and result['child_wait']['returncode'] == 0 and result['inputs_unchanged'] is True
        and (receipt / 'child.stdout').is_file()
        and (receipt / 'child.stdout').read_text().splitlines() == ['ROOT_CUSTODY_CONTEXT_CONTROLS_PASS'])
if mode in control_modes:
    marker = tail_enrollment['controls'][mode]['marker']
    result['tail_control_completion'] = (
        result['scope_wait'] == 0 and result['child_wait'] is not None
        and result['child_wait']['returncode'] == 0 and result['inputs_unchanged'] is True
        and (marker is None or ((receipt / 'child.stdout').is_file()
             and (receipt / 'child.stdout').read_text().splitlines() == [marker])))
if additional_action is not None and additional_action['additional_command'].get('restored_original_domain') is True:
    command = additional_action['additional_command']
    result['additional_controls_completion'] = (result['scope_wait'] == 0 and result['child_wait'] is not None
        and result['child_wait']['returncode'] == 0 and not result['child_wait']['additional_deadline_expired']
        and result['inputs_unchanged'] is True)
    if result['additional_controls_completion'] and command['kind'] == 'build':
        binary = source / command['binary']
        assert binary.is_file() and not binary.is_symlink()
        write(receipt / 'restored-built-binary.json', {'path': str(binary), 'sha256': digest(binary), 'bytes': binary.stat().st_size, 'mode': binary.stat().st_mode & 0o7777})
        shutil.copy2(binary, receipt / binary.name)
elif additional_action is not None:
    prefix = additional_action['additional_command']['expected_result_prefix']
    lines = (receipt / 'child.stdout').read_text().splitlines() if (receipt / 'child.stdout').is_file() else []
    result['additional_controls_completion'] = (result['scope_wait'] == 0 and result['child_wait'] is not None
        and result['child_wait']['returncode'] == 0 and not result['child_wait']['additional_deadline_expired']
        and result['inputs_unchanged'] is True and len(lines) == 1 and lines[0].startswith(prefix))
write(receipt / 'result.json', result)
print(json.dumps(result, indent=2))
print((receipt / 'scope.stderr').read_text())
if (receipt / 'child.stderr').exists():
    print((receipt / 'child.stderr').read_text())

assert unchanged, 'frozen source/tool/vendor changed'
if mode in ('root-custody-context-build', 'root-custody-context-controls'):
    assert result['scope_wait'] == 0 and result['child_wait'] is not None
    assert result['child_wait']['returncode'] == 0, 'control build/run did not terminate successfully'
    if mode == 'root-custody-context-build':
        built = source / 'obj/root-custody-context-controls/root_custody_context_controls'
        assert built.is_file()
        write(receipt / 'custody-built-binary.json', {'path': str(built), 'sha256': digest(built)})
    else:
        marker = 'ROOT_CUSTODY_CONTEXT_CONTROLS_PASS'
        assert (receipt / 'child.stdout').read_text().splitlines() == [marker], 'missing or unexpected control completion output'
        write(receipt / 'custody-controls-completion.json', {'marker': marker, 'child_and_scope_terminal_success': True, 'proof_claim': False})
if mode in tail_modes:
    assert result['scope_wait'] == 0 and result['child_wait'] is not None
    assert result['child_wait']['returncode'] == 0, 'additive control build/run did not terminate successfully'
    if mode not in control_modes:
        built = source / control_spec['binary']
        assert built.is_file()
        shutil.copy2(built, receipt / built.name)
        write(receipt / 'tail-built-binary.json', {'path': str(built), 'sha256': digest(built), 'bytes': built.stat().st_size, 'mode': built.stat().st_mode & 0o7777})
    else:
        assert result['tail_control_completion'] is True
        write(receipt / 'tail-controls-completion.json', {'marker': control_spec['marker'], 'child_and_scope_terminal_success': True, 'proof_claim': False})
if additional_action is not None:
    assert result['additional_controls_completion'] is True, 'Missing or unsuccessful original additional control result'
raise SystemExit(code)
