#!/usr/bin/env python3
"""Only the two original F3 additions; coordinator's heavy scope is mandatory."""
from __future__ import annotations
import argparse
import importlib.util
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
OWN = ROOT / 'scratch/acquisition2'
COMMIT = None  # Read from the future freeze-v5 record before strict validation.
FRAME = ROOT / 'scratch/coordinator/final-frame-v5/source'
FREEZE = ROOT / 'records/phase1-blockers/freeze-v5/source.json'
BUILD = ROOT / 'records/phase1-blockers/final-build-steps-v5/artifacts.json'
PINS = {
    'scratch/acquisition/original_binary_controls_v5.py': '61621b564757b7bf4acacb62adfdda3f361081479d63149f201ac1ba73a7a1cf',
    'scratch/acquisition/qualify_original_binary_sandbox_v3.py': 'd491dbb77ccfa48e47e1ccd96e755ff2f9eb39e083b8fca5012109ff494b7850',
    'scratch/old-analysis/frozen_source_v2.py': '76273e84d9ab37b6aaaa1d858709b32af90193f435045e90d6a0a80487b64f2e',
    'scratch/reviewer/f3-original-full-action-roster.json': 'df3a06cc674b9b6556f03722e56167c0d38da9ae80cd869abde56001ef9e7dbe',
    'scratch/acquisition/original-additional/run_execution_evidence_boundary_controls.py': 'a2e6fd4648d5eed25b81770946335d49df5eaa8ce9a69f7f596fa50e20e10c62',
    'tests/test_raw_evaluation_default.py': '21067fd8d8db9fee5472fadcda532abfcb5da35fe6a93fa3e4efdc116c20121f',
    'tests/run_freshness_json_order_controls.py': '487a14a56f6845ce037f805c23bebbe099aef3d2283dac51a46f5239deecf0d5',
    'tests/freshness_json_order_controls.py': 'af30ea6766680a00f4d1f0b3e1e57fcc98fbd3dfa8d2e9056375448161f0c4fe',
}
CASES = (
    ('freshness-json-object-order-additional-controls', FRAME / 'tests/run_freshness_json_order_controls.py',
     'FRESHNESS_JSON_ORDER_RESULT ', 'unchanged-original-TEST_ONLY-producer_case'),
    ('execution-evidence-boundary-additional-controls', ROOT / 'scratch/acquisition/original-additional/run_execution_evidence_boundary_controls.py',
     'EXECUTION_EVIDENCE_BOUNDARY_RESULT ', 'unchanged-original-TEST_ONLY-producer_case-and-staged_journal'),
)

def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value

def pin_inputs():
    import hashlib
    for relative, expected in PINS.items():
        path = ROOT / relative
        with path.open('rb') as stream:
            actual = hashlib.file_digest(stream, 'sha256').hexdigest()
        if actual != expected:
            raise RuntimeError('Pinned original/helper source changed: ' + relative)

def source_join(F, D):
    pin_inputs()
    joined = F.validate(COMMIT, FREEZE, FRAME, BUILD)
    built = D.load(BUILD)
    if built.get('assertion_ali_roster_complete') is not True or not built.get('assertion_options') or not all(v is True for v in built['assertion_options'].values()):
        raise RuntimeError('Original checked artifact roster is incomplete')
    if 'lib/pending-standalone/libevaluation_pending.so' not in joined['artifact_hashes']:
        raise RuntimeError('Matching pending library artifact absent')
    joined['build_steps'] = {}
    for name in ('pending', 'native'):
        path = BUILD.parent / (name + '.json')
        step = D.load(path)
        if step.get('source_commit') != COMMIT or type(step.get('exit_code')) is not int or step['exit_code'] != 0 or not step.get('completed_utc') or step.get('WORLDLINE_BUILD') != 'checks':
            raise RuntimeError('Matching checked build prerequisite incomplete: ' + name)
        joined['build_steps'][name] = D.identity(path)
    joined['pinned_inputs'] = {name: D.identity(ROOT / name) for name in PINS}
    return joined

def existing_qualification(path, D):
    path = path.resolve(strict=True)
    if not path.is_relative_to(ROOT / 'scratch/acquisition') or path.name != 'result.json':
        raise RuntimeError('Existing owned binary sandbox qualification result required')
    result = D.load(path)
    identity = D.load(path.parent / 'identity.json')
    scope = D.load(path.parent / 'scope.json')
    rows = result.get('controls', [])
    if (result.get('passed') is not True or [r.get('mode') for r in rows] != ['normal', 'timeout', 'detached']
        or any(r.get('passed') is not True or r.get('tracked_descendants_absent') is not True or r.get('child_reaped') is not True for r in rows)
        or result.get('namespace', {}).get('passed') is not True
        or identity.get('frame') != str(FRAME)
        or identity.get('script') != D.identity(ROOT / 'scratch/acquisition/qualify_original_binary_sandbox_v3.py')
        or identity.get('driver') != D.identity(ROOT / 'scratch/acquisition/original_binary_controls_v5.py')
        or scope.get('memory.max') != '8589934592' or scope.get('memory.swap.max') != '0'):
        raise RuntimeError('Existing exact carrier qualification is absent, failed or stale')
    return {name: D.identity(path.parent / name) for name in ('result.json', 'identity.json', 'scope.json')}

def stop_owned(child, started, Q):
    if child.poll() is None:
        current = Q.process(child.pid)
        if current['starttime'] != started['starttime']:
            raise RuntimeError('Owned child identity changed; refusing signal')
        os.killpg(child.pid, signal.SIGKILL)
        child.wait(timeout=10)

def run_case(case, out, D, Q, parser):
    mode, script, marker, provenance = case
    directory = out / mode
    directory.mkdir()
    (directory / 'temp').mkdir()
    env = D.environment(directory / 'temp')
    argv = D.guard(directory) + ['/usr/bin/python3', '-B', str(script)]
    record = {'mode': mode, 'source_commit': COMMIT, 'status': 'NOT PERFORMED',
              'classification': 'UNVERIFIED', 'original_payload_timeout_seconds': 180,
              'production_custody_established': False}
    child = None
    started = None
    owned = {}
    remaining = []
    try:
        pin_inputs()
        library_before = D.identity(ROOT / 'lib/libworldline_core.so')
        D.save(directory / 'launch.json', {'utc': D.utc(), 'argv': argv, 'cwd': str(FRAME),
            'environment': {k: env[k] for k in ('WORLDLINE_BUILD', 'WORLDLINE_CORE_LIB', 'PENDING_OBJECT_DIR', 'PENDING_LIBRARY_DIR', 'PYTHONPATH', 'TMPDIR', 'PYTHONDONTWRITEBYTECODE')},
            'PYTHONOPTIMIZE_absent': 'PYTHONOPTIMIZE' not in env, 'inner_deadline_seconds': 180,
            'source_commit': COMMIT, 'script': D.identity(script), 'library': library_before})
        with (directory / 'stdout').open('xb') as stdout, (directory / 'stderr').open('xb') as stderr:
            child = subprocess.Popen(argv, cwd=FRAME, env=env, stdout=stdout, stderr=stderr, start_new_session=True)
            deadline = time.monotonic() + 180
            started = Q.process(child.pid)
            owned[(started['pid'], started['starttime'])] = started
            D.save(directory / 'started-child.json', started)
            timed_out = False
            while child.poll() is None:
                for row in Q.descendants(child.pid):
                    owned[(row['pid'], row['starttime'])] = row
                wait = deadline - time.monotonic()
                if wait <= 0:
                    timed_out = True
                    stop_owned(child, started, Q)
                    break
                try:
                    child.wait(timeout=min(wait, 0.05))
                except subprocess.TimeoutExpired:
                    pass
        record.update(classification='TESTED', exit_code=child.returncode, additional_deadline_expired=timed_out)
        parsed = parser((directory / 'stderr').read_text(errors='replace'))
        lines = [line[len(marker):] for line in (directory / 'stdout').read_text(errors='replace').splitlines() if line.startswith(marker)]
        payload = json.loads(lines[0]) if len(lines) == 1 else None
        marker_ok = (type(payload) is dict and payload.get('input_kind') == provenance
                     and payload.get('production_custody_established') is False
                     and (mode != CASES[0][0] or payload.get('phase_acceptance') is False))
        original_ok = (parsed['ok'] and parsed['ran'] == 1 and parsed['verdictLine'] == 'OK'
                       and all(parsed[k] == 0 for k in ('failures', 'errors', 'skipped', 'expectedFailures', 'unexpectedSuccesses')))
        pin_inputs()
        unchanged = D.identity(ROOT / 'lib/libworldline_core.so') == library_before
        record.update(original_parser=parsed, marker=marker, marker_payload=payload,
                      original_marker_matches=marker_ok, unchanged_library=unchanged,
                      payload_predicates_passed=child.returncode == 0 and not timed_out and original_ok and marker_ok and unchanged)
    except BaseException as error:
        record.update(error_type=type(error).__name__, error=str(error))
    finally:
        cleanup_error = None
        try:
            if child is not None:
                if started is None:
                    raise RuntimeError('Child identity unavailable; enclosing owned scope must settle it')
                stop_owned(child, started, Q)
            stop = time.monotonic() + 10
            observations = []
            while True:
                remaining = []
                observations = []
                for old in owned.values():
                    try:
                        current = Q.process(old['pid'])
                    except FileNotFoundError:
                        observations.append({'pid': old['pid'], 'starttime': old['starttime'], 'state': 'ABSENT'})
                        continue
                    if current['starttime'] != old['starttime']:
                        observations.append({'pid': old['pid'], 'starttime': old['starttime'], 'state': 'REUSED', 'current_starttime': current['starttime']})
                    else:
                        remaining.append(current)
                if not remaining or time.monotonic() >= stop:
                    break
                time.sleep(0.05)
        except BaseException as error:
            cleanup_error = type(error).__name__ + ': ' + str(error)
            observations = []
        cleanup = {'observed_owned_processes': list(owned.values()), 'terminal_identity_observations': observations,
            'remaining': remaining, 'error': cleanup_error, 'direct_child_reaped': child is not None and child.returncode is not None,
            'observed_descendants_absent': bool(owned) and not remaining and cleanup_error is None,
            'scope_cleanup': 'Separate phase1_heavy terminal-scope receipt is required; no all-descendant completeness inferred from polling'}
        D.save(directory / 'cleanup.json', cleanup)
        record['cleanup'] = cleanup
        record['status'] = ('PASSED' if record.get('payload_predicates_passed') is True and cleanup['direct_child_reaped']
                            and cleanup['observed_descendants_absent'] else 'FAILED-OPEN' if child is not None else 'NOT PERFORMED')
        record['outputs'] = {name: D.identity(directory / name) for name in ('stdout', 'stderr') if (directory / name).is_file()}
        D.save(directory / 'result.json', record)
    return record

def main():
    global COMMIT
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--sandbox-qualification', type=Path, required=True)
    args = p.parse_args()
    out = args.out.resolve()
    if not out.is_relative_to(OWN) or out == OWN:
        p.error('Fresh output must be below scratch/acquisition2')
    pin_inputs()
    D = module(ROOT / 'scratch/acquisition/original_binary_controls_v5.py', 'original_binary_carrier')
    Q = module(ROOT / 'scratch/acquisition/qualify_original_binary_sandbox_v3.py', 'original_sandbox_helpers')
    F = module(ROOT / 'scratch/old-analysis/frozen_source_v2.py', 'original_frozen_source')
    COMMIT = D.load(FREEZE)['commit']
    D.FRAME = FRAME
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    out.mkdir(parents=True, exist_ok=False)
    result = {'classification': 'UNVERIFIED', 'source_commit': COMMIT, 'argv': sys.argv,
        'driver': D.identity(__file__), 'actions': [], 'original_carrier_acceptance': 'NOT PERFORMED',
        'full_F3_acceptance': False, 'independent_acceptance': 'NOT PERFORMED'}
    try:
        D.save(out / 'scope.json', D.scope_identity())
        result['before'] = source_join(F, D)
        result['sandbox_qualification'] = existing_qualification(args.sandbox_qualification, D)
        roster = D.load(ROOT / 'scratch/reviewer/f3-original-full-action-roster.json')
        selected = [r for r in roster['actions'] if r['mode'] in {case[0] for case in CASES}]
        if [r['mode'] for r in selected] != [case[0] for case in CASES]:
            raise RuntimeError('Original additional order or roster changed')
        for row, case in zip(selected, CASES):
            original = row['original']['additional_command']
            if original['test_timeout_seconds'] != 180 or original['expected_result_prefix'] != case[2] or original['assertions_required'] is not True:
                raise RuntimeError('Original additional predicate or deadline changed')
        D.save(out / 'original-actions.json', selected)
        assurance = module(FRAME / 'scripts/assurance.py', 'original_assurance_predicates')
        for case in CASES:
            if result['actions'] and result['actions'][-1]['status'] != 'PASSED':
                result['actions'].append({'mode': case[0], 'status': 'NOT PERFORMED', 'reason': 'Original predecessor payload failed'})
                break
            result['actions'].append(run_case(case, out, D, Q, assurance.parse_unittest))
        result['after'] = source_join(F, D)
        result['unchanged_source_and_artifacts'] = result['before'] == result['after']
        result['all_payload_conditions_passed'] = (len(result['actions']) == len(CASES)
            and all(r['status'] == 'PASSED' for r in result['actions']) and result['unchanged_source_and_artifacts'])
        result['classification'] = 'TESTED finite original additional payloads only'
    except BaseException as error:
        result.update(error_type=type(error).__name__, error=str(error), all_payload_conditions_passed=False)
    D.save(out / 'result.json', result)
    return 0 if result.get('all_payload_conditions_passed') is True else 1

if __name__ == '__main__':
    raise SystemExit(main())
