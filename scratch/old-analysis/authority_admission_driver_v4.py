#!/usr/bin/env python3
"""Prepared ordinary admission/release observation; never an authority gate pass.

An optional scratch observer forwards production ctypes function lookups to the
exact original _CFuncPtr. Native instruction entry and proof remain unverified.
No workload, service, actor, protected principal or real host ledger is created.
"""
from __future__ import annotations
import argparse
import ctypes
import dataclasses
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[2]
OWN = ROOT / 'scratch/old-analysis'
FRAME = None
FREEZE = None
BUILD = None
from frozen_source_v2 import validate as validate_frozen_source
SYMBOLS = {
    'C1': ['wl_resource_ledger_compute', 'wl_resource_ledger_headroom',
           'wl_resource_policy_admit'],
    'C2': ['wl_ordinary_reservation_lifecycle_plan'],
    'C3': ['wl_transaction_relation_v1'],
    'C4': ['wl_completion_raw_decide_v1', 'wl_evaluation_history_select',
           'wl_finalization_decide_v1', 'wl_evaluation_roster_complete'],
}


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def identity(expected):
    return validate_frozen_source(expected, FREEZE, FRAME, BUILD)

def resolve_symbols(core):
    class DlInfo(ctypes.Structure):
        _fields_ = [('filename', ctypes.c_char_p), ('base', ctypes.c_void_p),
                    ('symbol', ctypes.c_char_p), ('address', ctypes.c_void_p)]
    runtime = ctypes.CDLL(None)
    dladdr = runtime.dladdr
    dladdr.argtypes = [ctypes.c_void_p, ctypes.POINTER(DlInfo)]
    dladdr.restype = ctypes.c_int
    rows = []
    for gate, symbols in SYMBOLS.items():
        for name in symbols:
            address = ctypes.cast(getattr(core._lib, name), ctypes.c_void_p)
            info = DlInfo()
            if dladdr(address, ctypes.byref(info)) == 0 or not info.filename:
                raise RuntimeError('Native symbol owner unresolved: ' + name)
            owner = Path(os.fsdecode(info.filename)).resolve(strict=True)
            if owner != core.library_path:
                raise RuntimeError('Native symbol belongs to a different library: ' + name)
            if info.symbol != name.encode('ascii') or info.address != address.value:
                raise RuntimeError('Exact exported symbol/address did not resolve: ' + name)
            rows.append({'gate': gate, 'requested_symbol': name,
                         'address': address.value, 'resolved_owner': str(owner),
                         'owner_sha256': sha(owner), 'library_base': info.base,
                         'resolved_symbol': os.fsdecode(info.symbol) if info.symbol else None,
                         'resolved_symbol_address': info.address,
                         'classification': 'MEASURED symbol resolution only; invocation UNVERIFIED'})
    return rows


def main():
    global FREEZE, FRAME, BUILD
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--expected-commit', required=True)
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--observe-ffi', action='store_true')
    parser.add_argument('--ffi-qualification', type=Path)
    parser.add_argument('--freeze-record', type=Path, required=True)
    parser.add_argument('--frame', type=Path, required=True)
    parser.add_argument('--build-manifest', type=Path, required=True)
    args = parser.parse_args()
    FREEZE = args.freeze_record.resolve()
    FRAME = args.frame.resolve()
    BUILD = args.build_manifest.resolve()
    if any(not value.is_relative_to(ROOT) for value in (FREEZE, FRAME, BUILD)):
        parser.error('Identity inputs must remain in this worktree')
    out = args.out.resolve()
    if not out.is_relative_to(OWN):
        parser.error('Fresh output must remain in owned scratch')
    out.mkdir(parents=True, exist_ok=False)
    result = {'status': 'UNVERIFIED', 'command': sys.argv, 'driver_sha256': sha(__file__),
              'source_commit': args.expected_commit, 'scope': 'ordinary pre-launch reservation component only',
              'native_invocation_observation': 'UNVERIFIED: no qualified entry/return observer installed',
              'gate_status': {'C1': 'UNVERIFIED', 'C2': 'UNVERIFIED',
                              'C3': 'NOT PERFORMED', 'C4': 'NOT PERFORMED'},
              'independent_acceptance': 'NOT PERFORMED', 'steps': []}
    exit_code = 1
    class PrerequisiteOnlyComplete(Exception):
        pass
    authority = None
    ffi_observer = None
    owned_reservations = []
    try:
        result['before'] = identity(args.expected_commit)
        sys.dont_write_bytecode = True
        sys.path.insert(0, str(FRAME / 'runtime'))
        os.environ['WORLDLINE_CORE_LIB'] = result['before']['library']
        from worldline.core import Core
        core = Core.shared()
        if str(core.library_path) != result['before']['library']:
            raise RuntimeError('Production shared Core selected another library')
        result['library_selection'] = core.library_source
        save(out / 'native-symbol-provenance.json', resolve_symbols(core))
        (out / 'process-maps-before.txt').write_bytes(Path('/proc/self/maps').read_bytes())
        from worldline import admission, config, paths
        result['runtime_modules'] = {module.__name__: {'path': module.__file__, 'sha256': sha(module.__file__)}
                                     for module in (admission, config, paths)}
        if not args.run:
            result['status'] = 'TESTED symbol/identity prerequisite only; production exercise NOT PERFORMED'
            exit_code = 0
            raise PrerequisiteOnlyComplete()
        group = next(line[3:] for line in Path('/proc/self/cgroup').read_text().splitlines()
                     if line.startswith('0::'))
        cgroup = Path('/sys/fs/cgroup') / group.lstrip('/')
        facts = {name: (cgroup / name).read_text().strip()
                 for name in ('memory.max', 'memory.swap.max', 'memory.events')}
        if facts['memory.max'] != '8589934592' or facts['memory.swap.max'] != '0':
            raise RuntimeError('Reviewed unchanged 8G/zero-swap worker scope required')
        result['scope_resources'] = {'path': str(cgroup), **facts}
        if args.observe_ffi:
            from authority_ffi_observer_v1 import AuthorityObserver
            if args.ffi_qualification is None:
                raise RuntimeError('Explicit reviewed finite FFI qualification record required')
            qpath = args.ffi_qualification.resolve(strict=True)
            if not qpath.is_relative_to(OWN):
                raise RuntimeError('FFI qualification must be owned scratch evidence')
            qualification = json.loads(qpath.read_text())
            if (qualification.get('status') != 'TESTED finite observer qualification'
                or qualification.get('observer_sha256') != sha(OWN/'authority_ffi_observer_v1.py')
                or qualification.get('source_commit') != args.expected_commit
                or qualification.get('library_sha256') != result['before']['library_sha256']
                or qualification.get('all_controls_pass') is not True):
                raise RuntimeError('Missing or mismatching finite observer qualification')
            for path, expected in qualification.get('output_hashes', {}).items():
                target = Path(path).resolve(strict=True)
                if not target.is_relative_to(OWN) or sha(target) != expected:
                    raise RuntimeError('FFI qualification output differs')
            if not qualification.get('output_hashes'):
                raise RuntimeError('FFI qualification has no retained output roster')
            result['ffi_qualification'] = {'path':str(qpath),'sha256':sha(qpath),
                'scope':'finite correspondence only; no universal transparency or native instruction entry'}
            ffi_observer = AuthorityObserver(core,out/'ffi-dispatch',result['before']['library'],
                                            result['before']['library_sha256'])
        local = paths.WorldlinePaths(home=out/'home', data=out/'data', state=out/'state',
                                    runtime=out/'runtime', config=out/'config')
        local.ensure()
        settings = config.GlobalConfig.default(local)
        ledger = admission.Ledger(local.runtime)
        authority = admission.AdmissionAuthority(ledger, settings.admission_floors,
                                                paths={'state': local.state, 'share': local.data})
        policy = settings.resource_policy
        save(out / 'production-default-configuration.json', settings.value)
        result['input_boundary'] = ('Real admission.observe reads /proc and own filesystem; original defaults. '
            'Reservations have no unit yet, so the original pending/no-unit liveness rule applies. '
            'Usage remains explicitly unknown; no fabricated zero or manager observation. '
            'No service is launched, so enforcement, Consume, running usage and manager cleanup are NOT PERFORMED.')

        def snapshot(label):
            target = out / ('ledger-' + label + '.json')
            if ledger.path.exists():
                target.write_bytes(ledger.path.read_bytes())
                return {'present': True, 'path': str(target), 'sha256': sha(target)}
            return {'present': False, 'path': str(ledger.path)}

        def perform(name, action):
            if ffi_observer is not None:
                ffi_observer.step(name)
            step = {'name': name, 'start_monotonic_ns': time.monotonic_ns(),
                    'ledger_before': snapshot(name + '-before')}
            try:
                value = action()
                step['returned'] = (value.as_dict() if hasattr(value, 'as_dict') else
                    [dataclasses.asdict(item) for item in value] if isinstance(value, list) else value)
                if hasattr(value, 'reservation_id') and value.reservation_id is not None:
                    owned_reservations.append(value.reservation_id)
                return value
            except BaseException as error:
                step['exception'] = {'type': type(error).__name__, 'message': str(error)}
                raise
            finally:
                step['end_monotonic_ns'] = time.monotonic_ns()
                step['ledger_after'] = snapshot(name + '-after')
                save(out / (name + '.json'), step)
                result['steps'].append(name)

        perform('initial-report', lambda: authority.report(policy))
        first = perform('ordinary-admission', lambda: authority.admit(
            workload='phase1-owned-authority-observation', policy=policy, memory_bytes=1))
        if first.outcome != admission.ADMITTED or first.reservation_id is None:
            raise RuntimeError('Original actual host admission refused; no positive result invented')
        perform('reserved-report', lambda: authority.report(policy))
        rejected = perform('capacity-refusal-request', lambda: authority.admit(
            workload='phase1-capacity-negative-control', policy=policy,
            memory_bytes=admission.MAX_MEMORY_BYTES))
        if rejected.outcome != admission.RESOURCES_UNAVAILABLE:
            raise RuntimeError('Expected resource refusal not observed; retained actual outcome')
        released = perform('release-owned-reservation', lambda: authority.release(first.reservation_id))
        if released is not True:
            raise RuntimeError('Owned release did not return literal True')
        if perform('release-again', lambda: authority.release(first.reservation_id)) is not False:
            raise RuntimeError('Repeated release did not return literal False')
        perform('reconcile-after-release', authority.reconcile)
        perform('final-report', lambda: authority.report(policy))
        if ledger.outstanding():
            raise RuntimeError('Owned component ledger remains nonempty')
        result['status'] = 'TESTED ordinary component outcomes only; C1/C2 full authority gates remain UNVERIFIED'
        exit_code = 0
    except PrerequisiteOnlyComplete:
        pass
    except BaseException as error:
        result['status'] = 'FAILED-OPEN component exercise or prerequisite'
        result['exception'] = {'type': type(error).__name__, 'message': str(error)}
        (out / 'traceback.txt').write_text(traceback.format_exc())
        exit_code = 1
    finally:
        if ffi_observer is not None:
            ffi_observer.step('owned-reservation-cleanup')
        if authority is not None:
            result['cleanup'] = []
            for reservation in owned_reservations:
                try:
                    result['cleanup'].append({'reservation_id': reservation,
                                              'release_returned': authority.release(reservation)})
                except BaseException as error:
                    result['cleanup'].append({'reservation_id': reservation, 'error': repr(error)})
                    result['status'] = 'FAILED-OPEN owned reservation cleanup'
        if ffi_observer is not None:
            try:
                observed = ffi_observer.finish()
                save(out/'ffi-observer-result.json',observed)
                result['ffi_observer_result'] = {'path':str(out/'ffi-observer-result.json'),
                                                'sha256':sha(out/'ffi-observer-result.json')}
                seen = {row['symbol'] for row in observed['completed_calls']}
                complete = (set(('wl_resource_ledger_compute','wl_resource_ledger_headroom',
                                 'wl_resource_policy_admit')).issubset(seen)
                    and not observed['observation_errors'] and not observed['restoration_errors']
                    and observed['restored_original_functions'] is True
                    and observed['library_sha256_after'] == result['before']['library_sha256'])
                result['native_invocation_observation'] = (
                    'TESTED qualified finite Python dispatch to pinned real ctypes functions and their returned buffers; native instruction entry UNVERIFIED'
                    if complete else 'UNVERIFIED: incomplete FFI observer coverage or error')
                if not complete:
                    result['status'] = 'FAILED-OPEN incomplete FFI observation'
            except BaseException as error:
                result['ffi_observer_finish_error'] = repr(error)
                result['status'] = 'FAILED-OPEN FFI observer finalization'
        try:
            result['after'] = identity(args.expected_commit)
        except BaseException as error:
            result['identity_after_error'] = repr(error)
            result['status'] = 'FAILED-OPEN final identity'
        try:
            (out / 'process-maps-after.txt').write_bytes(Path('/proc/self/maps').read_bytes())
        except BaseException as error:
            result['maps_after_error'] = repr(error)
            result['status'] = 'FAILED-OPEN final mapping observation'
        save(out / 'result.json', result)
        if result['status'].startswith('FAILED-OPEN'):
            exit_code = 1
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
