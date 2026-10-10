"""Capture explicitly proposed current read-only closure inputs, never approve them.

Reuses F12 observers (file hashes/readelf/ldconfig and manager readback only).
No target/source import, builder/prover, live-lane admission, window or toolchain
write occurs. A separate actual GPT6.1 independent closure review is mandatory
before these changed pins can be selected by bind_selected_source.py.
"""
from pathlib import Path
import datetime
import importlib.util
import os
import subprocess
import sys

sys.dont_write_bytecode = True
import successor_support as support

D = Path(__file__).resolve().parent


def observer(name):
    path = support.F / (name + '.py')
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def main():
    assert __debug__ and sys.argv[1:] == ['--capture-current-inputs-only']
    assert D == support.CANDIDATE
    for name in ('source', 'author-freeze.json', 'preparation-review.json', 'current-closure-inputs'):
        assert not (D / name).exists() and not (D / name).is_symlink(), ('Never rebind qualified/attempted inputs', name)
    pending = support.load(support.DRAFT / 'source-bindings.json')
    required = pending['explicit_selected_source_artifacts']
    formal_row = pending['genuine_full_strict_source_review']
    assert formal_row is not None, 'Genuine exact current F64 full-strict SOURCE review is missing'
    formal = support.source_review(formal_row, required['source-selection.json'], required['source-inventory.json'])
    assert formal['artifacts'] == required, 'Formal SOURCE qualification names another complete source'
    integrated_row = pending['genuine_integrated_source_review']
    assert integrated_row is not None, 'Genuine exact current F64 integrated SOURCE review is missing'
    integrated = support.load(support.matched(integrated_row))
    support.independent(integrated, pending['integrated_source_disposition'], support.AUTHOR)
    assert integrated['artifacts'] == required and integrated['phase_acceptance'] is False
    auxiliary = support.load(support.matched(pending['genuine_auxiliary_review']))
    support.independent(auxiliary, 'QUALIFIED_EXACT_F53_RUNTIME_PROOF_SOURCE_FOR_NONPRIVILEGED_DIAGNOSTIC_PREPARATION_ONLY', support.AUTHOR)
    assert auxiliary['artifacts'] == required
    assert integrated['runtime_proof_review'] == formal['runtime_proof_review'] == pending['genuine_auxiliary_review']
    support.matched(pending['genuine_auxiliary_model_provenance'])
    support.matched(pending['genuine_source_review_model_provenance'])
    support.matched(pending['genuine_formal_source_review_model_provenance'])
    inherited_pins = support.load(support.DRAFT / 'inherited-pins.json')
    for path, row in inherited_pins.items():
        assert support.pin(path) == row, ('Inherited author preimage changed', path)
    documents = {name: support.load(support.F / name) for name in support.CLOSURE_FILES}
    # These are proposed current observations, not authorization to disregard drift.
    inbound_path = os.environ['PATH']
    prefixes = ':'.join('/home/sicarii/opt/gnat/' + name + '/bin' for name in
        ('gnat-aarch64-linux-16.1.0-1', 'gprbuild-aarch64-linux-26.0.0-1', 'gnatprove-aarch64-linux-16.1.0-1'))
    documents['launch-environment.json']['PATH'] = inbound_path
    template = documents['tool-inventory-template.json']['tool_inventory_spec']
    template['effective_environment']['PATH'] = prefixes + ':' + inbound_path
    tools = observer('tool_inventory').observe(template)
    baseline = documents['action-baseline.json']
    baseline['tool_inventory'] = tools
    documents['native-input-baseline.json'] = observer('native_inventory').observe()
    runtime = observer('runtime_inventory')
    env = dict(os.environ, PATH=inbound_path, XDG_RUNTIME_DIR='/run/user/1000',
               DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/1000/bus')
    rc = documents['runtime-closure.json']
    runtime.verify_environment(rc['spec'], env)
    rc['inventory'] = runtime.observe(rc['spec'])
    elf = observer('proof_elf_inventory')
    pc = documents['proof-data-closure.json']
    pc['inventory'] = observer('proof_data_inventory').observe(pc['spec'])
    documents['proof-elf-baseline.json'] = elf.observe(tools)
    for row in documents['vendor-template.json']:
        identity = support.pin(row['original'])
        row['sha256'] = identity['sha256']
        for name in ('bytes', 'mode'):
            if name in row:
                row[name] = identity[name]
    baseline['vendor_inventory'] = {row['original']: row['sha256'] for row in documents['vendor-template.json']}
    manager = subprocess.run(['/usr/bin/systemctl', '--user', 'show-environment'], env=env,
        capture_output=True, text=True, timeout=30, check=True)
    values = dict(line.split('=', 1) for line in manager.stdout.splitlines() if '=' in line)
    baseline['manager_environment'] = {key: values.get(key) for key in baseline['manager_environment']}
    original = support.check_closure_contract(documents)
    delta = {name: support.json_delta(original[name], documents[name]) for name in support.CLOSURE_FILES}
    for name, rows in delta.items():
        assert support.apply_json_delta(original[name], rows) == documents[name]
        assert support.apply_json_delta(documents[name], rows, reverse=True) == original[name]
    out = D / 'current-closure-inputs'
    out.mkdir(exist_ok=False)
    pins = {name: support.save(out / name, value) for name, value in documents.items()}
    binding = support.save(out / 'current-closure-bindings.json', {
        'schema': 'worldline-formal-current-closure-binding-v1',
        'author': support.AUTHOR, 'author_model': support.MODEL,
        'candidate': str(D), 'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'documents': pins, 'deltas': delta,
        'predecessor_inputs': {name: support.pinned(support.F / name) for name in support.CLOSURE_FILES},
        'historical_drift_acknowledgement': support.pinned(support.F / 'historical-drift-acknowledged-rows.json'),
        'manager_observation': {'argv': manager.args, 'stdout': manager.stdout,
                                'stderr': manager.stderr, 'returncode': manager.returncode},
        'approval': False, 'historical_acknowledgement_grants_additional_drift': False,
        'target_execution': False, 'proof_acceptance': False, 'phase_acceptance': False,
        'required_review_disposition': 'QUALIFIED_EXACT_CURRENT_CLOSURE_BINDING_FOR_FORMAL_SUCCESSOR'})
    print({'proposed_current_closure_binding': binding, 'approval': False, 'target_execution': False})


if __name__ == '__main__':
    main()
