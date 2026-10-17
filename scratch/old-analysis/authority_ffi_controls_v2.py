#!/usr/bin/env python3
"""Prepared finite observer qualification. Root runs under the approved scope.

No production policy method, native decision or ctypes return is mocked. The
separate libc wrapper control uses an explicit errcheck exception solely to test
exception identity/errno preservation; it is not WORLDLINE authority evidence.
"""
from __future__ import annotations
import argparse
import ctypes
import dataclasses
import hashlib
import json
import os
from pathlib import Path
import sys
import traceback
from frozen_source_v2 import validate
from authority_ffi_observer_v1 import AuthorityObserver, CaptureRefusal, EventLog, ObservedFunction, digest

ROOT=Path(__file__).resolve().parents[2]
OWN=ROOT/'scratch/old-analysis'

def save(path, value):
    with path.open('x') as stream:
        json.dump(value,stream,indent=2,sort_keys=True)
        stream.write('\n')

def main():
    p=argparse.ArgumentParser()
    for name in ('out','freeze-record','frame','build-manifest'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--expected-commit',required=True)
    args=p.parse_args();out=args.out.resolve()
    if not out.is_relative_to(OWN):raise SystemExit('Owned fresh scratch output required')
    out.mkdir(exist_ok=False,parents=True)
    result={'status':'UNVERIFIED','source_commit':args.expected_commit,'argv':sys.argv,'cwd':str(ROOT),
            'observer_sha256':digest(OWN/'authority_ffi_observer_v1.py'),
            'driver_sha256':digest(__file__),'all_controls_pass':False,
            'independent_acceptance':'NOT PERFORMED','controls':[], 'output_hashes':{}}
    observer=None
    exit_code=1
    def check(name,predicate,detail):
        result['controls'].append({'name':name,'passed':bool(predicate),'detail':detail})
        if not predicate:raise AssertionError(name)
    try:
        before=validate(args.expected_commit,args.freeze_record,args.frame,args.build_manifest)
        result['identity_before']=before
        result['library_sha256']=before['library_sha256']
        group=next(x[3:] for x in Path('/proc/self/cgroup').read_text().splitlines() if x.startswith('0::'))
        scope=Path('/sys/fs/cgroup')/group.lstrip('/')
        resources={n:(scope/n).read_text().strip() for n in ('memory.max','memory.swap.max','memory.events')}
        if resources['memory.max']!='8589934592' or resources['memory.swap.max']!='0':
            raise RuntimeError('Reviewed unchanged 8G/zero-swap worker scope required')
        result['resources']=resources
        sys.path.insert(0,str(args.frame.resolve()/'runtime'))
        os.environ['WORLDLINE_CORE_LIB']=before['library']
        from worldline.core import Core
        from worldline import resource_ledger as ledger, resource_policy as policy
        core=Core.shared()
        result['runtime_modules']={m.__name__:{'path':m.__file__,'sha256':digest(m.__file__)} for m in (ledger,policy)}
        def cases():
            answer=[]
            for values in ([],[(0,None)],[(8,3),(2,None),(-4,-2)],[(2**200,None),(1,2**128)]):
                answer.append({'operation':'compute_ledger','input':values,
                               'output':dataclasses.asdict(ledger.compute_ledger(values,core=core))})
            for values in ((0,0,0),(10,3,2),(-4,7,9),(2**200,2**128,3)):
                answer.append({'operation':'compute_headroom','input':values,
                               'output':ledger.compute_headroom(*values,core=core)})
            base=dict(outstanding_count=0,concurrency_limit=None,memory_pressure=None,
                      memory_pressure_ceiling=10,disks=[(100,100)],disk_byte_floor=1,disk_inode_floor=1,
                      available_memory=100,withheld_memory=0,memory_floor=1,requested_memory=1)
            for change in ({},{'requested_memory':1000},{'outstanding_count':2,'concurrency_limit':1},
                           {'memory_pressure':20},{'disks':[(0,100)]},{'disks':[]}):
                inputs={**base,**change}
                answer.append({'operation':'decide_policy','input':inputs,
                               'output':dataclasses.asdict(policy.decide_policy(**inputs,core=core))})
            return answer
        plain=cases();save(out/'plain-results.json',plain)
        observer=AuthorityObserver(core,out/'observed',before['library'],before['library_sha256'])
        observer.step('finite-production-transport-parity')
        wrapped=cases();save(out/'observed-results.json',wrapped)
        check('finite-produced-values-match-plain',plain==wrapped,'Exact Python result structures on fixed cases; no mathematical result recomputed by the harness')
        observed=observer.finish();observer=None;save(out/'observed-summary.json',observed)
        check('all-targets-observed-and-restored',
              set(('wl_resource_ledger_compute','wl_resource_ledger_headroom','wl_resource_policy_admit')).issubset({x['symbol'] for x in observed['completed_calls']})
              and observed['restored_original_functions'] and not observed['observation_errors'] and not observed['restoration_errors'],
              'Original ctypes objects restored; complete before/returned records for all targets')

        observer=AuthorityObserver(core,out/'zero-call',before['library'],before['library_sha256'])
        observer.step('invalid-representation-before-decision')
        try:ledger.compute_ledger([(object(),None)],core=core)
        except Exception as error:zero_exception={'type':type(error).__name__,'message':str(error)}
        else:raise AssertionError('Invalid representation unexpectedly returned')
        zero=observer.finish();observer=None;save(out/'zero-call-summary.json',zero)
        check('zero-decision-call-remains-zero',not zero['completed_calls'] and Path(zero['event_path']).read_text()=='' and zero['restored_original_functions'],zero_exception)

        plain_budget=ledger.compute_headroom(10,3,2,core=core)
        observer=AuthorityObserver(core,out/'capture-refusal',before['library'],before['library_sha256'])
        def decline(args):raise CaptureRefusal('Controlled observation refusal; original call must still execute')
        observer.wrappers['wl_resource_ledger_headroom'].snapshot=decline
        wrapped_budget=ledger.compute_headroom(10,3,2,core=core)
        budget=observer.finish();observer=None;save(out/'capture-refusal-summary.json',budget)
        check('capture-refusal-cannot-invent-complete-evidence',plain_budget==wrapped_budget and bool(budget['observation_errors']) and not budget['completed_calls'] and budget['restored_original_functions'],
              'Original return preserved while observation is explicitly incomplete')

        # A real foreign-function exception control, separate from WORLDLINE.
        libc=ctypes.CDLL(None,use_errno=True)
        function=libc.abs
        function.argtypes=[ctypes.c_int];function.restype=ctypes.c_int
        log=EventLog(out/'libc-wrapper')
        observed_function=ObservedFunction(function,'libc.abs',{'scope':'observer control only; not WORLDLINE'},
                                           lambda a:{'scalar_args':list(a)},log)
        observed_function.argtypes=[ctypes.c_int];observed_function.restype=ctypes.c_int
        baseline=function(-7);forwarded=observed_function(-7)
        check('real-ctypes-return-pass-through',baseline==forwarded and function.argtypes==observed_function.argtypes and function.restype is observed_function.restype,
              'Direct baseline compared to original real libc pointer under forwarding object')
        sentinel=RuntimeError('qualification sentinel')
        calls=[]
        def errcheck(value, called, arguments):
            calls.append({'function_identity':id(called),'arguments':arguments})
            ctypes.set_errno(23)
            raise sentinel
        function.errcheck=errcheck
        try:observed_function(-7)
        except RuntimeError as error:
            same=error is sentinel;actual_errno=ctypes.get_errno()
        else:raise AssertionError('Original foreign-function errcheck exception swallowed')
        finally:del function.errcheck
        check('real-ctypes-exception-identity-once-and-errno',same and len(calls)==1 and actual_errno==23,
              {'errcheck_calls':calls,'exception_identity_preserved':same,'private_errno':actual_errno})
        rejected=False
        try:ObservedFunction(lambda:None,'not-native',{},lambda a:{},log)
        except TypeError:rejected=True
        check('non-ctypes-callable-rejected',rejected,'No Python callback accepted as an original foreign function')
        save(out/'libc-wrapper-summary.json',log.finish())
        after=validate(args.expected_commit,args.freeze_record,args.frame,args.build_manifest)
        result['identity_after']=after
        check('same-library-and-frozen-source',before['library_sha256']==after['library_sha256'], 'Both exact full frozen source validations completed')
        result['all_controls_pass']=all(x['passed'] for x in result['controls'])
        result['status']='TESTED finite observer qualification'
        result['non_claims']=['No native-instruction entry or independent debugger witness',
            'No full authority/retirement/proof coverage or arbitrary-domain instrumentation transparency',
            'Additional observation allocation, timing and concurrent mutation effects remain outside finite qualification',
            'The libc errcheck control is observer machinery qualification only, never a production result']
        exit_code=0
    except BaseException as error:
        result['status']='FAILED-OPEN observer qualification'
        result['exception']={'type':type(error).__name__,'message':str(error)}
        (out/'traceback.txt').write_text(traceback.format_exc())
        exit_code=1
    finally:
        if observer is not None:
            try:save(out/'interrupted-observer-summary.json',observer.finish())
            except BaseException as error:
                result['observer_restore_error']=repr(error)
                result['status']='FAILED-OPEN observer finalization'
                result['all_controls_pass']=False
                exit_code=1
        result['output_hashes']={str(p):digest(p) for p in out.rglob('*') if p.is_file()}
        if result['status']!='TESTED finite observer qualification' or result['all_controls_pass'] is not True:
            exit_code=1
        result['exit_code']=exit_code
        save(out/'result.json',result)
    return exit_code

if __name__=='__main__':raise SystemExit(main())
