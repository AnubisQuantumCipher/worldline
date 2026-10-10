"""Produce every real original custody domain, then export under a fresh lease.

Construction is fixture_builder's explicit offline action, never startup. The
produce stage writes an exact export request/inventory for Main's new approved
DATA/native/source envelope. Export cannot relax the producer's old ABSENT
selection or fabricate a passing fixture/capture when a real process crashed.
"""
from __future__ import annotations
import sys
_approved = sys.modules.get('_worldline_approved_source_loader')
if _approved is None:
    raise SystemExit('FULL_CAMPAIGN_EARLY_SOURCE_REQUIRED')
_lease = _approved.current()
_lease.check()
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess


def require(value, reason):
    if not value:
        raise RuntimeError(reason)


def modules(runtime, capture_source_root):
    for root in (runtime, capture_source_root, str(Path(__file__).parent)):
        _lease.directory_or_absent(root)
    sys.path[:0] = [runtime, capture_source_root, str(Path(__file__).parent)]


def produce(plan_path, output_directory):
    raw = _lease.file(plan_path, ('DATA',))
    plan = json.loads(raw)
    require(plan['schema'] == 'worldline.original-custody-live-campaign-v2'
            and set(plan) == {'schema', 'runtime', 'capture_source_root', 'cases', 'case_envelopes'},
            'FULL_CAMPAIGN_EXACT_PLAN_SCHEMA')
    require(plan['cases'] and set(plan['case_envelopes']) == set(plan['cases']),
            'FULL_CAMPAIGN_COMPLETE_SELECTED_CASE_ENVELOPES_REQUIRED')
    modules(plan['runtime'], plan['capture_source_root'])
    from live_campaign import private_directory, output, selected_json
    from capture_coverage import check
    from custody_runtime_controls_v35 import KINDS, CONTROLS
    from observed_controls import SUBJECT_CASES
    from campaign_registry import bind
    cases = bind(plan)
    out = private_directory(output_directory)
    installations = set()
    captures = []
    for name, record in cases.items():
        descriptor = selected_json(record['startup_descriptor'])
        root = descriptor['paths']['authority_root']
        require(root not in installations, 'FULL_CAMPAIGN_ORIGINAL_FIXTURES_MUST_BE_DISTINCT')
        installations.add(root)
        captures.extend(record['capture_paths'])
    require(len(set(captures)) == len(captures), 'FULL_CAMPAIGN_ACTUAL_PROCESS_OUTPUT_ALIAS')
    entry = str(Path(__file__).with_name('live_campaign.py'))
    _lease.file(entry, ('SOURCE', 'ENTRY'))
    rows = []
    for name, record in cases.items():
        envelope = plan['case_envelopes'][name]
        _lease.file(envelope, ('DATA',))
        command = [_lease.interpreter, '-I', '-S', '-B', _lease.helper_path,
                   '--bootstrap-envelope', envelope, '--entry', entry,
                   '--plan', plan_path, '--case', name]
        with (out / (name + '.stdout')).open('xb') as stdout, (out / (name + '.stderr')).open('xb') as stderr:
            child = subprocess.Popen(command, env={'PATH': '/usr/bin:/bin', 'HOME': str(out),
                'TMPDIR': str(out), 'LC_ALL': 'C'}, stdout=stdout, stderr=stderr)
            wait = child.wait(timeout=record['timeout'])
            stdout.flush(); stderr.flush(); os.fsync(stdout.fileno()); os.fsync(stderr.fileno())
        row = {'case': name, 'argv': command, 'pid': child.pid, 'actual_wait': wait,
               'stdout_sha256': hashlib.sha256((out / (name + '.stdout')).read_bytes()).hexdigest(),
               'stderr_sha256': hashlib.sha256((out / (name + '.stderr')).read_bytes()).hexdigest()}
        rows.append(row)
        require(wait == 0, 'FULL_CAMPAIGN_GENUINE_ORIGINAL_CASE_FAILED_' + name)
        require(_lease.file(plan_path, ('DATA',)) == raw, 'FULL_CAMPAIGN_ORIGINAL_PLAN_CHANGED')
        _lease.check()
    # This unconditional complete roster is independent of individual case
    # declarations: no case plan can narrow all43/all13/mandatory edge controls.
    coverage = check(captures, KINDS, CONTROLS, SUBJECT_CASES)
    captures = [record['capture'] for record in coverage['captures']]
    inventory = {}
    case_results = {}
    for case_name, case in cases.items():
        directory = private_directory(case['result_directory'])
        result_path = directory / 'result.json'
        result_raw = result_path.read_bytes()
        result = json.loads(result_raw)
        require(result['schema'] == 'worldline.original-custody-live-case-result-v1'
                and result['case'] == case_name and result['original_plan'] == plan_path,
                'FULL_CAMPAIGN_ACTUAL_CASE_RESULT_LINEAGE_SPLIT')
        actual_files = {result_path, out / (case_name + '.stdout'), out / (case_name + '.stderr')}
        actual_files.update(directory.glob('*.stdout'))
        actual_files.update(directory.glob('*.stderr'))
        for owner in result.get('source_owner_custody', []):
            ownership_directory = private_directory(owner['source_owner_retention'])
            actual_files.update(ownership_directory.iterdir())
            actual_files.update((Path(owner['stdout']), Path(owner['stderr'])))
        if case['duplex_control'] is not None:
            from worldline.root_worker_codec import raw_restore_archive
            from campaign_registry import DUPLEX_CASES
            control_raw = _lease.file(case['duplex_control'], ('DATA',))
            control = json.loads(control_raw)
            control_path = Path(control['result_path'])
            private_directory(control_path.parent)
            require(control['mode'] == DUPLEX_CASES[case_name],
                    'FULL_CAMPAIGN_ACTUAL_DUPLEX_SELECTED_MODE_CHANGED')
            control_result = raw_restore_archive(control_path.read_bytes())
            require(control_result['schema'] == control['schema']
                    and control_result['selected_plan_raw'] == control_raw
                    and control_result['mode'] == control['mode']
                    and control_result['request']['requestId'] == control['request_id']
                    and control_result['actual_native_output_queries']
                    and 'actual_failure' not in control_result,
                    'FULL_CAMPAIGN_ACTUAL_DUPLEX_NATIVE_INPUT_LINEAGE_REQUIRED')
            actual_files.add(control_path)
            front_path = directory / 'duplex-front-output.archive'
            front_result = raw_restore_archive(front_path.read_bytes())
            require(front_result['schema'] == 'worldline.original-custody-live-duplex-front-outputs-v1'
                    and front_result['case'] == case_name and front_result['original_plan'] == plan_path
                    and front_result['request'] == control_result['request']
                    and front_result['actual_intake'] == control_result['intake']
                    and any(row['entry'].endswith('.prefix_output') for row in front_result['actual_native_output_queries']),
                    'FULL_CAMPAIGN_GENUINE_FRONT_PREFIX_QUERY_REQUIRED')
            from duplex_original_control import validate_front_observations
            validate_front_observations(front_result, control)
            actual_files.add(front_path)
        for path in sorted(actual_files):
            require(path.is_file() and not path.is_symlink(), 'FULL_CAMPAIGN_ACTUAL_CASE_PROOF_FILE_REQUIRED')
            proof = path.read_bytes()
            inventory[str(path)] = {'sha256': hashlib.sha256(proof).hexdigest(),
                                    'mode': oct(path.stat().st_mode & 0o777)}
        faults = [record for record in result['records']
                  if isinstance(record.get('action'), dict) and record['action'].get('kind') == 'fault']
        for fault in faults:
            require(fault['actual_wait'] == 0 and fault['argv'],
                    'FULL_CAMPAIGN_ACTUAL_SYSCALL_TRACER_NOT_COMPLETED')
            require(any(hashlib.sha256(path.read_bytes()).hexdigest() == fault['stderr_sha256']
                        and b'ACTUAL_SYSCALL_FAULT_APPLIED' in path.read_bytes()
                        for path in directory.glob('fault-*.stderr')),
                    'FULL_CAMPAIGN_ACTUAL_SYSCALL_TRACER_PROOF_MISSING')
        case_results[case_name] = {'path': str(result_path),
            'sha256': hashlib.sha256(result_raw).hexdigest(), 'actual_fault_records': faults}
    for manifest_path in captures:
        path = Path(manifest_path)
        private_directory(path.parent)
        manifest = json.loads(path.read_bytes())
        names = {str(path)}
        for row in manifest['cases']:
            for slot in ('input', 'delta', 'before_load', 'after_load', 'context', 'uncertainty'):
                if slot in row:
                    names.add(str(path.parent / row[slot]['path']))
        for name in sorted(names):
            data = Path(name).read_bytes()
            inventory[name] = {'sha256': hashlib.sha256(data).hexdigest(),
                               'mode': oct(Path(name).stat().st_mode & 0o777)}
    for failure in coverage['publication_errors']:
        if failure['raw_hex'] is None:
            continue
        path = Path(failure['path'])
        data = path.read_bytes()
        require(data.hex() == failure['raw_hex'], 'FULL_CAMPAIGN_INTERRUPTED_PUBLICATION_CHANGED')
        inventory[str(path)] = {'sha256': hashlib.sha256(data).hexdigest(),
                                'mode': oct(path.stat().st_mode & 0o777)}
    request = {'schema': 'worldline.original-custody-campaign-export-request-v1',
        'runtime': plan['runtime'], 'capture_source_root': plan['capture_source_root'],
        'captures': captures, 'inventory': inventory, 'original_case_commands': rows,
        'coverage': coverage, 'original_case_results': case_results, 'phase_acceptance': False}
    output(out / 'export-request.json', request)
    output(out / 'produce-result.json', {'schema': 'worldline.original-custody-full-production-v1',
        'plan_sha256': hashlib.sha256(raw).hexdigest(), 'records': rows,
        'coverage': coverage, 'selected_source': _lease.check(), 'phase_acceptance': False})


def export(request_path, library, output_directory):
    raw = _lease.file(request_path, ('DATA',))
    request = json.loads(raw)
    require(request['schema'] == 'worldline.original-custody-campaign-export-request-v1',
            'FULL_CAMPAIGN_ACTUAL_EXPORT_REQUEST_REQUIRED')
    modules(request['runtime'], request['capture_source_root'])
    for path, expected in request['inventory'].items():
        actual = _lease.file(path, ('DATA',))
        require(hashlib.sha256(actual).hexdigest() == expected['sha256']
                and oct(Path(path).stat().st_mode & 0o777) == expected['mode'],
                'FULL_CAMPAIGN_FRESH_QUALIFIED_ACTUAL_CAPTURE_CHANGED')
    import custody_runtime_controls_v35 as exporter
    command = [exporter.__file__, '--export', output_directory, '--library', library,
               '--runtime', request['runtime'], '--captures', *request['captures']]
    original = sys.argv
    sys.argv = command
    try:
        result = exporter.main()
    finally:
        sys.argv = original
    require(result == 0, 'FULL_CAMPAIGN_REAL_NATIVE_INPUT_EXPORT_FAILED')
    _lease.check()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=('produce', 'export'), required=True)
    parser.add_argument('--plan')
    parser.add_argument('--request')
    parser.add_argument('--library')
    parser.add_argument('--result-directory', required=True)
    args = parser.parse_args()
    require(os.geteuid() == 0 and sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode,
            'FULL_CAMPAIGN_EXPLICIT_ROOT_I_S_B_REQUIRED')
    if args.stage == 'produce':
        require(args.plan is not None and args.request is None and args.library is None,
                'FULL_CAMPAIGN_EXACT_PRODUCE_COMMAND_REQUIRED')
        produce(args.plan, args.result_directory)
    else:
        require(args.request is not None and args.library is not None and args.plan is None,
                'FULL_CAMPAIGN_EXACT_FRESH_EXPORT_COMMAND_REQUIRED')
        export(args.request, args.library, args.result_directory)


if __name__ == '__main__':
    main()
