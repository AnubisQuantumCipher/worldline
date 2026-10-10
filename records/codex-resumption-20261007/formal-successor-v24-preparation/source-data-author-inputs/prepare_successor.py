"""Reviewed source/data-only adaptation of formal-successor-v12.

Missing final selection/review/pins refuses. This is never readiness, reservation,
launch, collection, independent review or proof acceptance. Partial output is
retained on failure; existing author freezes and historical frames are immutable.
"""
from pathlib import Path
import ast
import datetime
import hashlib
import importlib.util
import json
import os
import shutil
import stat
import subprocess
import sys

sys.dont_write_bytecode = True
D = Path(__file__).resolve().parent
R = D.parent
F = R / 'formal-successor-v12'
C = R / 'formal-successor-v24-preparation'
AUTHOR = 'SolPhaseOneIntegration'
MODEL = 'openai-codex/gpt-6.1-sol:max'
GOAL = '01a1149d-db62-74b0-a5f7-b0239f285c44'
SIX = {'prepare_successor.py', 'authorization.py', 'inherited-pins.json',
       'CHANGE.md', 'source-bindings.json', 'proof-obligations.json'}


def pin(path):
    path = Path(path)
    first = path.lstat()
    assert stat.S_ISREG(first.st_mode) and not path.is_symlink(), str(path)
    with path.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    last = path.lstat()
    fields = lambda row: (row.st_dev, row.st_ino, row.st_mode, row.st_size,
                          row.st_mtime_ns, row.st_ctime_ns)
    assert fields(first) == fields(last), str(path)
    return {'sha256': digest, 'bytes': last.st_size, 'mode': stat.S_IMODE(last.st_mode)}


def load(path):
    return json.loads(Path(path).read_text())


def save(name, value):
    path = D / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    return path


def module(name):
    path = D / (name + '.py')
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def main():
    assert __debug__ and sys.argv[1:] == ['--prepare-source-data-only'], 'Explicit checked source-data mode required'
    binding = load(D / 'source-bindings.json')
    assert binding.get('state') == 'EXPLICIT_FINAL_SOURCE_REVIEW_BOUND', (
        'Refuse: Main must supply final complete selected source, genuine independent strict-source review and enrollment')
    assert D == C and str(D) == binding['intended_sibling'], 'Never materialize an author draft or an old frame'
    for name in ('source', 'private-sparklib', 'author-freeze.json', 'inputs.json', 'evidence'):
        assert not (D / name).exists() and not (D / name).is_symlink(), ('Never overwrite materialized/frozen/attempted input', name)
    review = load(D / 'preparation-review.json')
    assert review['actual_model_selection'] == MODEL and review['author'] == AUTHOR
    assert isinstance(review['reviewer'], str) and review['reviewer'].strip() and review['reviewer'] != AUTHOR
    assert set(review['files']) == SIX and review['blocking_findings'] == []
    assert review['target_execution'] is False
    assert review['disposition'] == 'QUALIFIED_SOURCE_DATA_ONLY_SUCCESSOR_PREPARATION'
    for name, digest in review['files'].items():
        assert pin(D / name)['sha256'] == digest, name
    for name, row in load(D / 'inherited-pins.json').items():
        assert pin(name) == row, ('Inherited/supplemental pin changed', name)
    support = module('successor_support')
    assert support.AUTHOR == AUTHOR and support.MODEL == MODEL and support.CANDIDATE == D
    support.check_historical_source_history()
    observation = load(D / 'fresh-preparation-goal.json')
    portable_goal = module('portable_goal')
    portable_goal.check_observation(D, 'preparation', observation)
    for name, row in binding['pins'].items():
        support.matched(row)
    assert pin(D / 'proof-obligations.json')['sha256'] == binding['proof_obligations_sha256']
    source, entries, selected_inventory = support.selected_entries(support.matched(binding['pins']['source_selection']))
    assert str(source) == binding['source'] and entries == binding['complete_current_entries']
    inventory_row = binding['pins']['source_inventory']
    if selected_inventory is not None:
        assert selected_inventory == inventory_row
    else:
        assert load(support.matched(inventory_row)) == support.file_rows(source, entries)
    support.source_review(binding['pins']['source_review'], binding['pins']['source_selection'], inventory_row)
    support.check_current_project_routing(source, entries)
    base_source, base_entries, _ = support.selected_entries(support.matched(binding['pins']['predecessor_source_selection']))
    assert str(base_source) == binding['predecessor_source']
    support.verify_delta(base_entries, entries, binding['complete_predecessor_to_current_delta'])
    history = load(support.matched(binding['pins']['historical_enrollment']))
    report, policy = support.check_enrollment(support.matched(binding['pins']['proof_enrollment']), source, entries, history)
    assert report == binding['proof_enrollment']
    dependency = binding['private_dependency']
    assert support.dependency_plan() == dependency, 'Installed private-input preimage changed; explicit reviewed rebinding required'
    if binding['current_closure_binding'] is not None:
        closure = load(support.matched(binding['current_closure_binding']['binding']))
        closure_review_pin = support.check_closure_review(D)
        save('current-closure-review-binding.json', {
            'current_closure_binding': binding['current_closure_binding']['binding'],
            'independent_review': closure_review_pin,
            'historical_drift_acknowledgement': binding['pins']['historical_drift_acknowledgement'],
            'acknowledgement_expanded': False, 'target_execution': False})
        assert closure['documents'] == binding['closure_documents']
        assert closure['deltas'] == binding['complete_inherited_to_current_closure_deltas']
    else:
        assert binding['closure_documents'] == {name: support.pinned(F / name) for name in support.CLOSURE_FILES}
    # Current data is explicit and reviewed, never invented by an observer on drift.
    documents = support.rehome({name: load(support.matched(row)) for name, row in binding['closure_documents'].items()})
    original_documents = support.check_closure_contract({name: load(support.matched(row)) for name, row in binding['closure_documents'].items()})
    for name, original in original_documents.items():
        current = load(support.matched(binding['closure_documents'][name]))
        delta = binding['complete_inherited_to_current_closure_deltas'][name]
        assert support.json_delta(original, current) == delta, ('Incomplete current closure delta', name)
        assert support.apply_json_delta(original, delta) == current and support.apply_json_delta(current, delta, reverse=True) == original, name
    raw = support.snapshot(source)
    save('retained-runtime-output-observation.json', {
        'source': str(source), 'excluded_generated_entries': {name: row for name, row in raw.items() if name not in entries},
        'policy': 'Only original obj/lib/resource-tests/obj/resource-tests/bin partitions are omitted; every selected source entry is retained',
        'copied': False, 'execution_credit': False})
    support.copy_entries(source, D / 'source', entries)
    assert support.source_snapshot(source) == entries, 'Source changed during copy'
    save('selected-source-entries.json', entries)
    save('generated-preservation-exclusions.json', {'excluded': [],
        'source_selection': binding['pins']['source_selection'], 'source_inventory': inventory_row,
        'all_selected_entries_preserved': True, 'source_acceptance': False})
    private = D / 'private-sparklib'
    support.copy_entries(support.INSTALLED, private, dependency['entries'])
    for name, seed in dependency['initial_output_inventory'].items():
        if seed is not None:
            support.copy_entries(support.INSTALLED / name, private / name, seed)
    save('dependency-inventory.json', dependency)
    support.check_dependency(D)
    inherited_names = [
        'run_checks.py', 'outer_capture.py', 'tool_inventory.py', 'native_inventory.py',
        'runtime_inventory.py', 'proof_elf_inventory.py', 'proof_data_inventory.py',
        'display_observer.py', 'required-ordinary-roster.json', 'required-lifetime-controls.json',
        'required-current-component-controls.json', 'historical-drift-acknowledged-rows.json',
        'review/root-live-lane-v1/live_check.py', 'review/root-live-lane-v1/handshake.py',
        'review/root-live-lane-v1/positive-boundary-receipt.json', 'review/root-live-lane-v1/threshold-receipt.json',
        'review/root-live-lane-v1/zero-boundary-receipt.json', 'review/root-adoption-v1/root_ready.py',
        'review/root-terminal-v1/collect_terminal.py']
    deltas = []
    for name in inherited_names:
        origin, destination = F / name, D / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        assert not destination.exists() and not destination.is_symlink(), name
        if origin.suffix == '.py':
            before = origin.read_text()
            after = support.adapt_machinery(name, before)
            ast.parse(after)
            with destination.open('x') as stream:
                stream.write(after)
            destination.chmod(pin(origin)['mode'])
            if before != after:
                deltas.append({'file': name, 'preimage': support.pinned(origin),
                               'emitted': support.pinned(destination), 'before': before, 'after': after,
                               'change': 'Original complete source/private guards plus explicitly reviewed original600/840/1000 owned deadline/signal/retention and missing-result classification correction; no proof argv, source contract or roster change'})
            else:
                assert pin(origin) == pin(destination), name
        else:
            shutil.copy2(origin, destination)
            assert pin(origin) == pin(destination), name
    save('administrative-successor-deltas.json', deltas)
    assert pin(D / 'historical-drift-acknowledged-rows.json') == pin(F / 'historical-drift-acknowledged-rows.json')
    inventory = support.file_rows(D / 'source', entries)
    files = {name: row['sha256'] for name, row in inventory.items()}
    modes = {name: oct(row['mode']) for name, row in inventory.items()}
    save('final-source-inventory.json', inventory)
    shutil.copy2(F / 'proof-plan.json', D / 'historical-proof-plan.json')
    assert pin(D / 'historical-proof-plan.json') == pin(F / 'proof-plan.json')
    plan = load(F / 'proof-plan.json')
    assert plan['required_worldline_command'] == support.COMMAND and plan['original_floor'] == 251
    assert plan['only_original_boundary'] == 'worldline-c_api'
    plan.update(at=datetime.datetime.now(datetime.timezone.utc).isoformat(), source=str(D / 'source'),
        source_inventory=str(D / 'final-source-inventory.json'), source_inventory_sha256=pin(D / 'final-source-inventory.json')['sha256'],
        source_members=inventory, complete_ada_specs_projects_and_bodies=sorted(name for name in inventory if Path(name).suffix in ('.ads', '.adb', '.gpr')),
        predecessor_proof_plan_history=support.pinned(D / 'historical-proof-plan.json'),
        current_obligation_map=support.pinned(D / 'proof-obligations.json'), source_bindings=support.pinned(D / 'source-bindings.json'),
        current_full_composition_qualification='SOURCE_REVIEW_BOUND_EMITTED_FRAME_REVIEW_REQUIRED',
        expected_open_blockers='All historical failures and every original/new body/reference/caller/flow/RTE/termination/native-semantics/cost obligation remain OPEN. Complete current enrollment is required, never proof acceptance. No old VC/runtime/native/source-review qualification transfer.',
        private_dependency_inventory=support.pinned(D / 'dependency-inventory.json'),
        target_execution=False, phase_acceptance=False, shared_window_reserved=False)
    save('proof-plan.json', plan)
    save('source-composition.json', {'source_files': files, 'source_modes': modes,
        'source_inventory_sha256': pin(D / 'final-source-inventory.json')['sha256'],
        'complete_entry_inventory': support.pinned(D / 'selected-source-entries.json'),
        'qualification': 'SOURCE_REVIEW_BOUND_EMITTED_FRAME_REVIEW_REQUIRED',
        'historical_component_reviews': 'Historical scope only; no proof/native/runtime acceptance transfer'})
    env = dict(os.environ, PATH=documents['launch-environment.json']['PATH'],
        XDG_RUNTIME_DIR='/run/user/1000', DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/1000/bus')
    save('launch-environment.json', documents['launch-environment.json'])
    template = documents['tool-inventory-template.json']
    inherited_protected = dict(template['tool_inventory_spec']['effective_environment'])
    save('inherited-protected-environment.json', inherited_protected)
    protected = template['tool_inventory_spec']['effective_environment']
    protected['GPR_PROJECT_PATH'] = str(D / 'private-sparklib/lib/gnat') + ':' + protected['GPR_PROJECT_PATH']
    for key in support.DEPENDENCY_UNSET:
        assert env.get(key) is None, ('Unexpected inherited project/mode override', key)
        protected[key] = None
    save('tool-inventory-template.json', template)
    tools = module('tool_inventory').observe(template['tool_inventory_spec'])
    baseline = documents['action-baseline.json']
    assert tools == baseline['tool_inventory'], 'Tools drift; no automatic rebaseline'
    native = module('native_inventory').observe()
    assert native == documents['native-input-baseline.json'], 'Native/header drift; no automatic rebaseline'
    save('native-input-baseline.json', native)
    runtime = module('runtime_inventory')
    rc = documents['runtime-closure.json']
    runtime.verify_environment(rc['spec'], env)
    assert runtime.observe(rc['spec']) == rc['inventory'], 'Runtime/cache/alias/keyset drift; no automatic rebaseline'
    save('runtime-closure.json', rc)
    pc = documents['proof-data-closure.json']
    assert module('proof_data_inventory').observe(pc['spec']) == pc['inventory'], 'Proof installation/data drift'
    save('proof-data-closure.json', pc)
    elf = module('proof_elf_inventory').observe(tools)
    assert elf == documents['proof-elf-baseline.json'], 'Proof ELF drift'
    save('proof-elf-baseline.json', elf)
    vendors = documents['vendor-template.json']
    assert all(pin(row['original'])['sha256'] == row['sha256'] for row in vendors), 'Vendor drift'
    save('vendor-template.json', vendors)
    manager = subprocess.run(['/usr/bin/systemctl', '--user', 'show-environment'], env=env, capture_output=True, text=True, timeout=30, check=True)
    values = dict(line.split('=', 1) for line in manager.stdout.splitlines() if '=' in line)
    assert {key: values.get(key) for key in baseline['manager_environment']} == baseline['manager_environment'], 'Manager environment drift'
    baseline['source_files'] = files
    save('action-baseline.json', baseline)
    proposal = support.rehome(load(F / 'reviewed-launch-proposal.json'))
    assert proposal['full_scope']['command'] == support.COMMAND and proposal['full_scope']['summary_floor'] == 251
    assert len(proposal['launches']) == 1 and proposal['launches'][0]['child_argv'] == support.COMMAND
    action = proposal['launches'][0]
    assert action['launcher_argv'][:1] == ['/usr/bin/env'] and action['launcher_argv'][1].startswith('PATH=')
    action['explicit_inbound_environment']['PATH'] = env['PATH']
    action['launcher_argv'][1] = 'PATH=' + env['PATH']
    action['owned_deadline_controls'] = {
        'proof_child_wait_seconds': 600, 'scope_wait_seconds': 840,
        'systemd_scope_RuntimeMaxSec': '840s', 'systemd_scope_TimeoutStopSec': '15s',
        'Main_total_seconds': 1000, 'Main_execution_cutoff_reserves_seconds': 45,
        'child_TERM_KILL_reap_seconds': [5, 5], 'scope_TERM_KILL_reap_seconds': [15, 5],
        'handshake_TERM_KILL_reap_seconds': [25, 5], 'outer_TERM_KILL_reap_seconds': [35, 5],
        'actual_waits_unknown_timeouts_signals_and_retention_failures_separate': True,
        'affected_actual_smoke_review_emitted_adoption_required': True,
        'enforcement_qualified_or_executed_here': False}
    proposal.update(root_adoption=None, target_execution=False, source_qualification='SOURCE_REVIEW_BOUND_EMITTED_FRAME_REVIEW_REQUIRED')
    proposal['private_dependency'] = {'inventory': support.pinned(D / 'dependency-inventory.json'),
        'owned_output_roots': list(support.DEPENDENCY_OUTPUTS), 'shared_install_writes_allowed': False,
        'proof_only_substitution': False}
    save('reviewed-launch-proposal.json', proposal)
    g = D / 'review/root-live-lane-v1'
    save('review/root-live-lane-v1/source-pins.json', {str(D / 'source' / name): row['sha256'] for name, row in inventory.items()})
    controls = load(F / 'review/root-live-lane-v1/control-pins.json')
    for path, digest in controls.items():
        assert pin(path)['sha256'] == digest, ('Inherited original control drift', path)
    for path in sorted(D.rglob('*')):
        relative = path.relative_to(D)
        if path.is_file() and not path.is_symlink() and relative.parts[0] != 'source' and not support.under(relative.as_posix(), tuple('private-sparklib/' + name for name in support.DEPENDENCY_OUTPUTS)) and '__pycache__' not in relative.parts and path.name != 'fresh-preparation-goal.json':
            assert str(path) not in controls, str(path)
            controls[str(path)] = pin(path)['sha256']
    save('review/root-live-lane-v1/control-pins.json', controls)
    gate = load(F / 'review/root-live-lane-v1/inputs.json')
    gate['files'] = {name: pin(g / name)['sha256'] for name in gate['files']}
    for path, digest in gate['external_pins'].items():
        assert pin(path)['sha256'] == digest, ('Historical pin drift', path)
    save('review/root-live-lane-v1/inputs.json', gate)
    immutable = {}
    for path in sorted(D.rglob('*')):
        relative = path.relative_to(D)
        if path.is_file() and not path.is_symlink() and '__pycache__' not in relative.parts and path.name not in ('fresh-preparation-goal.json', 'preparation-review.json') and not support.under(relative.as_posix(), tuple('private-sparklib/' + name for name in support.DEPENDENCY_OUTPUTS)):
            immutable[relative.as_posix()] = pin(path)
    assert support.source_snapshot(source) == entries and support.source_snapshot(D / 'source') == entries
    assert support.file_rows(D / 'source', entries) == inventory
    support.check_dependency(D)
    save('inputs.json', {'schema': 'codex-current-formal-source-data-successor-v1', 'files': immutable,
        'source_files': files, 'source_modes': modes,
        'source_qualification': 'SOURCE_REVIEW_BOUND_EMITTED_FRAME_REVIEW_REQUIRED',
        'different_author_review_required': True, 'target_execution': False})
    frozen = dict(immutable)
    frozen['preparation-review.json'] = pin(D / 'preparation-review.json')
    frozen['inputs.json'] = pin(D / 'inputs.json')
    save('author-freeze.json', {'author': AUTHOR, 'author_model': MODEL, 'files': frozen,
        'target_execution': False, 'acceptance': False})
    print(json.dumps({'status': 'PREPARED_SOURCE_DATA_ONLY_ACTUAL_EMITTED_REVIEW_ADOPTION_FRESH_GATES_REQUIRED',
        'target_execution': False, 'proof_acceptance': False, 'phase_acceptance': False}))


if __name__ == '__main__':
    main()
