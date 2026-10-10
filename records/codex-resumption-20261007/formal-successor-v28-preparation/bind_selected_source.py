"""Bind Main's explicit final source and real review into the six-file author package.

Source/data only: no target imports or execution, observations/admission, reservation,
materialized source, private library build or author freeze. Missing data refuses.
Never selects v48 by default, creates an approval, or overwrites a qualified package.
"""
from pathlib import Path
import argparse
import json
import os
import shutil
import stat
import sys
import tempfile

sys.dont_write_bytecode = True
import successor_support as support

D = Path(__file__).resolve().parent
HISTORICAL_ENROLLMENT = support.R / 'phase1-integrated-v38-draft/explicit-library-proof-enrollment-v39.json'
HELPERS = ('successor_support.py', 'capture_closure_inputs.py', 'bind_selected_source.py', 'compiler_seed.py')
PENDING = 'WAITING_EXPLICIT_FINAL_SOURCE_SELECTION_AND_INDEPENDENT_STRICT_SOURCE_REVIEW'


def replace_unqualified(path, value):
    """The only mutable records are this new package's explicitly unbound author data."""
    path = Path(path)
    assert path.parent == support.DRAFT and path.name in ('source-bindings.json', 'proof-obligations.json', 'inherited-pins.json')
    assert not path.is_symlink() and path.is_file()
    before = support.pin(path)
    with tempfile.NamedTemporaryFile('w', dir=path.parent, prefix=path.name + '.', delete=False) as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
        temporary = Path(stream.name)
    assert support.pin(path) == before, 'Author data changed during binding'
    temporary.chmod(before['mode'])
    os.replace(temporary, path)


def main():
    assert __debug__, 'Checked Python required'
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-selection', required=True, type=Path)
    parser.add_argument('--source-review', required=True, type=Path)
    parser.add_argument('--proof-enrollment', required=True, type=Path)
    parser.add_argument('--formal-inventory', type=Path,
        help='Required only for historical nested selection; independently reviewed complete file inventory')
    parser.add_argument('--current-closure-bindings', required=True, type=Path)
    parser.add_argument('--closure-review', type=Path)
    parser.add_argument('--current-controller-bindings', required=True, type=Path)
    parser.add_argument('--current-controller-review', required=True, type=Path)
    args = parser.parse_args()
    assert D == support.CANDIDATE
    for root in (support.DRAFT, D):
        for name in ('source', 'private-sparklib', 'author-freeze.json', 'preparation-review.json', 'inputs.json', 'evidence'):
            assert not (root / name).exists() and not (root / name).is_symlink(), ('Never overwrite qualified/materialized/attempted frame', root, name)
    pending = support.load(support.DRAFT / 'source-bindings.json')
    assert pending['state'] == PENDING, 'Only a never-qualified explicit pending author package can be bound'
    assert pending['fresh_current_closure_required'] is True, 'C28 requires an actual newly captured current closure'
    required = pending['explicit_selected_source_artifacts']
    assert support.pinned(args.source_selection.resolve(strict=True)) == required['source-selection.json'], 'C28 binds only the explicitly selected complete F67 DATA-v2 source'
    assert support.pinned(args.proof_enrollment.resolve(strict=True)) == required['enrollment-report.json']
    integrated_row = pending['genuine_integrated_source_review']
    assert integrated_row is not None, 'Genuine exact current F67 DATA-v2 integrated SOURCE review is missing'
    integrated = support.load(support.matched(integrated_row))
    support.source_opinion(integrated, pending['integrated_source_disposition'])
    assert integrated['artifacts'] == required, 'Integrated SOURCE qualification names another source'
    assert integrated['phase_acceptance'] is False
    auxiliary = support.load(support.matched(pending['genuine_auxiliary_review']))
    support.source_opinion(auxiliary, 'QUALIFIED_EXACT_F53_RUNTIME_PROOF_SOURCE_FOR_NONPRIVILEGED_DIAGNOSTIC_PREPARATION_ONLY')
    assert auxiliary['artifacts'] == required
    assert integrated['runtime_proof_review'] == pending['genuine_auxiliary_review']
    support.matched(pending['genuine_auxiliary_model_provenance'])
    support.matched(pending['genuine_source_review_model_provenance'])
    support.matched(pending['genuine_formal_source_review_model_provenance'])
    inherited = support.load(support.DRAFT / 'inherited-pins.json')
    for path, row in inherited.items():
        assert support.pin(path) == row, ('Inherited/helper input changed', path)
    historical_binding = support.check_historical_source_history()
    selection_row = support.pinned(args.source_selection.resolve(strict=True))
    review_row = support.pinned(args.source_review.resolve(strict=True))
    source, entries, inventory_row = support.selected_entries(selection_row['path'])
    if inventory_row is None:
        assert args.formal_inventory is not None, 'Nested selection requires the exact independently reviewed formal inventory'
        inventory_row = support.pinned(args.formal_inventory.resolve(strict=True))
        assert support.load(inventory_row['path']) == support.file_rows(source, entries)
    else:
        assert args.formal_inventory is None or support.pinned(args.formal_inventory.resolve(strict=True)) == inventory_row
    selected_review = support.source_review(review_row, selection_row, inventory_row)
    assert selected_review['artifacts'] == required, 'Full strict SOURCE qualification names another complete source'
    assert review_row == pending['genuine_full_strict_source_review'], 'C28 requires the actual separately retained current F67 DATA-v2 formal SOURCE review'
    assert selected_review['runtime_proof_review'] == pending['genuine_auxiliary_review']
    support.check_current_project_routing(source, entries)
    controller_row = support.pinned(args.current_controller_bindings.resolve(strict=True))
    assert support.matched(controller_row) == D / 'current-controller-binding.json'
    controller = support.load(controller_row['path'])
    assert controller['schema'] == 'worldline-current-controller-original-lineage-binding-v1'
    assert controller['candidate'] == str(D) and controller['required_window_holder'] == support.GOAL
    assert controller['author'] == support.AUTHOR and controller['author_model'] == support.MODEL
    assert controller['approval'] is False and controller['phase_acceptance'] is False
    controller_review_row = support.pinned(args.current_controller_review.resolve(strict=True))
    controller_review = support.load(controller_review_row['path'])
    support.independent(controller_review, 'QUALIFIED_EXACT_CURRENT_CONTROLLER_OBSERVATION_SURFACE_FOR_ORIGINAL_FORMAL_GOAL', support.AUTHOR)
    assert controller_review['phase_acceptance'] is False
    for row in controller_review['artifacts'].values():
        support.matched(row)
    for name, path in (('portable_goal.py', D / 'portable_goal.py'),
                       ('current-controller-binding.json', D / 'current-controller-binding.json'),
                       ('prepare_successor.py', support.DRAFT / 'prepare_successor.py'),
                       ('authorization.py', support.DRAFT / 'authorization.py'),
                       ('successor_support.py', D / 'successor_support.py'),
                       ('capture_closure_inputs.py', D / 'capture_closure_inputs.py'),
                       ('bind_selected_source.py', D / 'bind_selected_source.py'),
                       ('compiler_seed.py', D / 'compiler_seed.py'),
                       ('compiler-output-seed-selection.json', D / 'compiler-output-seed-selection.json'),
                       ('deadline-machinery-pins.json', D / 'deadline-machinery-pins.json'),
                       ('closure-budget-design.json', D / 'closure-budget-design.json'),
                       *((name, D / name) for name in (
                           'deadline-machinery-templates/run_checks.py',
                           'deadline-machinery-templates/outer_capture.py',
                           'deadline-machinery-templates/review/root-live-lane-v1/handshake.py',
                           'deadline-machinery-templates/review/root-terminal-v1/collect_terminal.py'))):
        identity = {key: controller_review['artifacts'][name][key] for key in ('sha256', 'bytes', 'mode')}
        assert support.pin(path) == identity, ('Controller review names another actual C28 component', name)
    for row in controller['provenance'].values():
        support.matched(row)
    enrollment_row = support.pinned(args.proof_enrollment.resolve(strict=True))
    historical_row = support.pinned(HISTORICAL_ENROLLMENT)
    historical = support.load(HISTORICAL_ENROLLMENT)
    report, policy = support.check_enrollment(enrollment_row['path'], source, entries, historical)
    selection = support.load(support.matched(selection_row))
    if 'source_only_enrollment' in selection:
        assert selection['source_only_enrollment'] == enrollment_row, 'Selected current enrollment pin differs'
        assert selected_review['artifacts']['enrollment-report.json'] == enrollment_row, 'Current enrollment is not source-reviewed'
    assert report['schema'] == 'worldline-source-only-proof-enrollment-v49'
    base_selection = historical_binding['source_selection']
    base_source, base_entries, _ = support.selected_entries(support.matched(base_selection))
    delta = support.exact_delta(base_entries, entries)
    support.verify_delta(base_entries, entries, delta)
    old_documents = {name: support.load(support.F / name) for name in support.CLOSURE_FILES}
    closure_document_pins = {name: support.pinned(support.F / name) for name in support.CLOSURE_FILES}
    closure_choice = None
    closure_deltas = {name: [] for name in support.CLOSURE_FILES}
    assert args.closure_review is None or args.current_closure_bindings is not None, 'A closure review cannot name an unspecified current binding'
    if args.current_closure_bindings is not None:
        current_pin = support.pinned(args.current_closure_bindings.resolve(strict=True))
        current = support.load(current_pin['path'])
        current_review_pin = None
        ack_row = support.pinned(support.F / 'historical-drift-acknowledged-rows.json')
        if args.closure_review is not None:
            current_review_pin = support.pinned(args.closure_review.resolve(strict=True))
            current_review = support.load(current_review_pin['path'])
            support.independent(current_review, 'QUALIFIED_EXACT_CURRENT_CLOSURE_BINDING_FOR_FORMAL_SUCCESSOR', support.AUTHOR)
            assert current_review['current_closure_binding'] == current_pin
            assert current_review['historical_drift_acknowledgement'] == ack_row
        assert current['schema'] == 'worldline-formal-current-closure-binding-v1' and current['candidate'] == str(D)
        assert current['author'] == support.AUTHOR and current['author_model'] == support.MODEL
        assert current['approval'] is False and current['target_execution'] is False
        assert current['historical_acknowledgement_grants_additional_drift'] is False
        assert current['predecessor_inputs'] == closure_document_pins
        assert current['historical_drift_acknowledgement'] == ack_row
        closure_document_pins = current['documents']
        documents = {name: support.load(support.matched(row)) for name, row in closure_document_pins.items()}
        support.check_closure_contract(documents)
        closure_deltas = current['deltas']
        assert set(closure_deltas) == set(support.CLOSURE_FILES)
        for name, original in old_documents.items():
            assert support.json_delta(original, documents[name]) == closure_deltas[name], name
            assert support.apply_json_delta(original, closure_deltas[name]) == documents[name], name
            assert support.apply_json_delta(documents[name], closure_deltas[name], reverse=True) == original, name
        closure_choice = {'binding': current_pin, 'review': current_review_pin}
    else:
        support.check_closure_contract(old_documents)
    pins = {
        'source_selection': selection_row, 'source_inventory': inventory_row, 'source_review': review_row,
        'proof_enrollment': enrollment_row, 'historical_enrollment': historical_row,
        'predecessor_source_selection': base_selection,
        'predecessor_source_bindings': support.pinned(support.F / 'source-bindings.json'),
        'predecessor_preparation_review': support.pinned(support.F / 'preparation-review.json'),
        'predecessor_frame_freeze': support.pinned(support.F / 'author-freeze.json'),
        'predecessor_formal_inventory': support.pinned(support.F / 'final-source-inventory.json'),
        'predecessor_proof_plan': support.pinned(support.F / 'proof-plan.json'),
        'predecessor_proof_obligations': support.pinned(support.F / 'proof-obligations.json'),
        'historical_drift_acknowledgement': support.pinned(support.F / 'historical-drift-acknowledged-rows.json'),
        'integrated_source_review': integrated_row,
        'current_controller_binding': controller_row,
        'portable_goal_module': support.pinned(D / 'portable_goal.py'),
        'portable_goal_guard_review': controller_review_row,
        'explicit_additional_command_enrollment': pending['explicit_additional_command_enrollment'],
        'qualified_native_observer_final_source_consumption_binding': pending['qualified_native_observer_final_source_consumption_binding'],
        'genuine_auxiliary_review': pending['genuine_auxiliary_review'],
        'genuine_auxiliary_model_provenance': pending['genuine_auxiliary_model_provenance'],
        'genuine_source_review_model_provenance': pending['genuine_source_review_model_provenance'],
        'genuine_formal_source_review_model_provenance': pending['genuine_formal_source_review_model_provenance'],
    }
    pins['compiler_output_seed_selection'] = pending['compiler_output_seed_selection']
    pins['compiler_seed_module'] = support.pinned(D / 'compiler_seed.py')
    additional_enrollment = support.load(support.matched(pending['explicit_additional_command_enrollment']))
    assert additional_enrollment['additional_commands'] == pending['additional_commands']
    for command in pending['additional_commands']:
        if 'external_runner' in command:
            pins['additional_runner:' + command['mode']] = command['external_runner']
    for name, row in selected_review['artifacts'].items():
        pins['reviewed_artifact:' + name] = row
    dependency = support.dependency_plan()
    import compiler_seed
    compiler_seed.authenticate(D, {'pins': pins, 'closure_documents': closure_document_pins},
                               entries, dependency)
    obligations = support.load(support.F / 'proof-obligations.json')
    obligations['retained_f12_map_pin'] = pins['predecessor_proof_obligations']
    obligations['retained_f12_map'] = support.load(support.F / 'proof-obligations.json')
    obligations['current_open'] += [
        'Complete explicitly selected current source and byte-identical private installed SPARKlib remain under the original full strict command; all historic failures/outcomes retain their historical scope.',
        'All seven original authority areas, original accepted domains/controls, full Posts/bodies/private helpers/callers/flow/RTE/termination/native semantics/checked finite costs remain required. No permission by discovery or new unanalyzed boundary.',
        'A real complete current source review is only source-diagnostic qualification. Actual emitted-frame review, adoption, fresh goal/clock/resource/storage/JACKAL/window/no-sibling admission and the complete proof/native/control campaigns remain required.',
        'Imported SPARKlib bodies and declaration coverage must be reviewed against actual vendor sources; private copying or successful name enrollment is never a proof-only substitute or an assumption exemption.']
    obligations.update(state='EXPLICIT_FINAL_SOURCE_REVIEW_BOUND', original_floor=251,
        inherited_required_prefix=historical['original_required_names'], current_required_proved=policy['REQUIRED_PROVED'],
        declared_core_ada_sources=sorted(policy['DECLARED_CORE_ADA_SOURCES']), effective_contract_pins=policy['CONTRACT_PINS'],
        imported_dependency_evidence=report['importedDependencyEvidence'], imported_proof_units=report['importedProofUnits'],
        source_selection=selection_row, source_inventory=inventory_row, source_review=review_row,
        source_enrollment=enrollment_row, full_strict_command=support.COMMAND,
        complete_relevant_source_scope={name: {'entry': row,
            'required': 'Original full spec/body/reference/caller/flow/RTE/termination and native-semantic/cost obligations; not acceptance'}
            for name, row in entries.items() if Path(name).suffix in ('.ads', '.adb', '.gpr', '.h', '.c', '.py')},
        phase_acceptance=False, target_execution=False, proof_acceptance=False)
    replace_unqualified(support.DRAFT / 'proof-obligations.json', obligations)
    for row in list(pins.values()) + list(closure_document_pins.values()) + ([] if closure_choice is None else [row for row in closure_choice.values() if row is not None]):
        support.matched(row)
        identity = {key: row[key] for key in ('sha256', 'bytes', 'mode')}
        if row['path'] in inherited:
            assert inherited[row['path']] == identity, 'Do not silently rebaseline an inherited file pin'
        else:
            inherited[row['path']] = identity
    for name in HELPERS:
        path = D / name
        assert inherited[str(path)] == support.pin(path), name
    replace_unqualified(support.DRAFT / 'inherited-pins.json', inherited)
    binding = {
        'schema': 'worldline-complete-source-data-formal-successor-v13',
        'state': 'EXPLICIT_FINAL_SOURCE_REVIEW_BOUND', 'author': support.AUTHOR,
        'author_model': support.MODEL, 'intended_sibling': str(D), 'source': str(source),
        'pins': pins, 'complete_current_entries': entries,
        'predecessor_source': str(base_source), 'complete_predecessor_to_current_delta': delta,
        'historical_source_bindings_preserved': historical_binding,
        'proof_enrollment': report,
        'reviewed_source_artifacts': selected_review['artifacts'],
        'proof_obligations_sha256': support.sha(support.DRAFT / 'proof-obligations.json'),
        'private_dependency': dependency, 'closure_documents': closure_document_pins,
        'current_closure_binding': closure_choice,
        'explicit_additional_command_enrollment': pending['explicit_additional_command_enrollment'],
        'additional_commands': pending['additional_commands'],
        'additional_runner_is_not_an_extra_full_strict_launch': True,
        'original_ordered_runtime_enrollment': pending['original_ordered_runtime_enrollment'],
        'qualified_native_observer_final_source_consumption_binding': pending['qualified_native_observer_final_source_consumption_binding'],
        'current_controller_observation_surface': {
            'profile': controller_row, 'affected_guard_review': controller_review_row,
            'original_window_holder_unchanged': True, 'historical_paused_status_retained': True,
            'native_id_is_not_legacy_thread_id': True,
            'separate_real_six_file_preparation_review_required': True,
            'target_execution': False, 'phase_acceptance': False},
        'complete_inherited_to_current_closure_deltas': closure_deltas,
        'source_read_only': True, 'target_execution': False,
        'preparation_approval': False, 'proof_acceptance': False, 'phase_acceptance': False}
    assert support.source_snapshot(source) == entries, 'Selected source changed during binding'
    assert support.pinned(args.source_selection.resolve(strict=True)) == selection_row
    assert support.pinned(args.source_review.resolve(strict=True)) == review_row
    assert support.pinned(args.proof_enrollment.resolve(strict=True)) == enrollment_row
    replace_unqualified(support.DRAFT / 'source-bindings.json', binding)
    # Stage only the six reviewed author inputs. Source/private outputs/freeze stay absent.
    for name in support.SIX_FILES:
        destination = D / name
        assert not destination.exists() and not destination.is_symlink(), name
        shutil.copy2(support.DRAFT / name, destination)
        assert support.pin(destination) == support.pin(support.DRAFT / name), name
    six = {name: support.sha(support.DRAFT / name) for name in support.SIX_FILES}
    next_pins = support.save(D / 'bound-review-needed-pins.json', {
        'schema': 'worldline-formal-v13-real-preparation-review-needed',
        'actual_model_required': support.MODEL, 'author': support.AUTHOR,
        'files': six, 'supplemental_helpers': {name: support.pinned(D / name) for name in (*HELPERS, 'portable_goal.py')},
        'current_controller_profile': controller_row, 'affected_guard_review': controller_review_row,
        'genuine_integrated_source_review': integrated_row,
        'source_selection': selection_row, 'source_inventory': inventory_row, 'source_review': review_row,
        'proof_enrollment': enrollment_row, 'disposition_required': 'QUALIFIED_SOURCE_DATA_ONLY_SUCCESSOR_PREPARATION',
        'blocking_findings_required': [], 'target_execution_required': False,
        'current_closure_binding': closure_choice,
        'current_closure_review_required': closure_choice is not None and closure_choice['review'] is None,
        'pending_closure_review_consumed_only_from_genuine_preparation_review_pin': 'current_closure_review',
        'review_record_destination': str(D / 'preparation-review.json'),
        'approval': False, 'materialized_source': False,
        'next_existing_command': ['/usr/bin/python3', '-B', str(D / 'prepare_successor.py'), '--prepare-source-data-only'],
        'after_materialization': 'Real actual emitted-frame and emitted-source review, concrete existing adoption and separately fresh observations; no source review/proof acceptance transfer'})
    print(json.dumps({'bound_review_needed_pins': next_pins, 'six_files': six,
                      'materialized_source': False, 'approval': False, 'target_execution': False}, sort_keys=True))


if __name__ == '__main__':
    main()
