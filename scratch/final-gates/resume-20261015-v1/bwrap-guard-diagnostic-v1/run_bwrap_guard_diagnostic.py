#!/usr/bin/env python3
"""One metadata-only failed-private-carrier diagnostic; coordinator launch only.

No production imports, private executor, tests, services, configuration writes or
foreign process interaction. The child reads only its own proc identity, public
bwrap bytes/stat and explicit environment operands. No acceptance classification.
"""
from __future__ import annotations
import argparse, ast, datetime, hashlib, json, os, re, subprocess, time
from pathlib import Path

ROOT = Path('/home/sicarii/Work/worldline-phase1-blockers-20261013T165716Z')
METHOD = Path(__file__).resolve().parent
PINS = {'created_utc': '2026-10-15T03:01:40.812055+00:00', 'historical_source_commit': 'ef7b7e38a2940bfabbe0bbd601c6c00df69fc7ac', 'identities': {'historical_launch': {'path': 'scratch/old-analysis/private-host-runtime-v5/attempt-fe4dbe1e5a184941b949fdf3c42baa94/worker/private-host-tests/launch.json', 'sha256': 'f6cbdc19cb97454f23bca5c2456028e2eb8d777c0e40329b46bd5808ae7b0cb4', 'bytes': 1055}, 'historical_environment': {'path': 'scratch/old-analysis/private-host-runtime-v5/attempt-fe4dbe1e5a184941b949fdf3c42baa94/worker/test-environment.json', 'sha256': '2b9514b835238fbb55fad019e519b8d378cc117fcee6e106e1e3e37df8470d86', 'bytes': 1765}, 'original_carrier': {'path': 'scratch/old-analysis/full_runtime_supervisor_v3.py', 'sha256': '3105162b3f9eac3a61460e9a1cb23966a84296fa9e4af9ddc69c1155e97b39e1', 'bytes': 23118}, 'frozen_guard': {'path': 'scratch/coordinator/final-frame-v5/source/runtime/worldline/linux/private_evaluator.py', 'sha256': '36094019564b0d4ce7911e07c0f0655bea03790ac9e8fbaadde5860ca830d42e', 'bytes': 154059}, 'current_guard': {'path': 'runtime/worldline/linux/private_evaluator.py', 'sha256': '36094019564b0d4ce7911e07c0f0655bea03790ac9e8fbaadde5860ca830d42e', 'bytes': 154059}, 'historical_positive_source': {'path': 'scratch/coordinator/final-frame-v5/source/tests/test_private_evaluator.py', 'sha256': 'f3f167299ab21a06265dc6435b5fbd41c4a6edcf3e9efcb5c7d860746ffcbba3', 'bytes': 12215}}, 'guard_function_sha256': 'ef76fe722a542f63bc70b7f0c628119df636ff89b9b32e0d089d6c8dd68df229', 'guard_expression': 'not path.is_absolute() or not stat.S_ISREG(info.st_mode)\n            or info.st_uid not in (0, os.getuid()) or info.st_mode & 0o7022\n            or not os.access(path, os.X_OK)', 'classification': 'MEASURED method source readback only; diagnostic not executed'}
PINS_SHA = 'bd899073874a582997c4dcdff226df190d82a44539c2d21d9262d7086327aa2f'
PAYLOAD_SHA = 'ada4e1921e0317a583b1b42a9d00dc3d5c6ce5ed852f429b4f03209ec5b64403'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def stamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def save(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')


def git(*args):
    return subprocess.check_output(['git','-C',str(ROOT),*args], text=True).strip()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--expected-head', required=True)
    parser.add_argument('--decisions-sha256', required=True)
    parser.add_argument('--out', required=True, type=Path)
    args=parser.parse_args()
    os.umask(0o077)
    if not re.fullmatch('[0-9a-f]{40}',args.expected_head) or not re.fullmatch('[0-9a-f]{64}',args.decisions_sha256):
        raise RuntimeError('Exact actual baseline HEAD and decisions SHA required')
    if git('rev-parse','HEAD') != args.expected_head:
        raise RuntimeError('Expected baseline HEAD is not current')
    dirty_before=git('diff','HEAD','--name-only').splitlines()
    decisions=ROOT/'docs/decisions.md'
    if sha(decisions)!=args.decisions_sha256 or not re.search(r'^## D45(?:\s|—|[-])',decisions.read_text(),re.M):
        raise RuntimeError('Actual D45/log identity unavailable')
    if sha(METHOD/'source-pins.json')!=PINS_SHA or sha(METHOD/'payload.py.txt')!=PAYLOAD_SHA:
        raise RuntimeError('Reviewed diagnostic method bytes changed')
    for item in PINS['identities'].values():
        if sha(ROOT/item['path'])!=item['sha256']:
            raise RuntimeError('Original diagnostic source/recipe preimage changed: '+item['path'])
    if PINS['identities']['current_guard']['sha256']!=PINS['identities']['frozen_guard']['sha256']:
        raise RuntimeError('Current and original frozen guard bytes differ')
    source=(ROOT/PINS['identities']['current_guard']['path']).read_text()
    function=next(node for node in ast.parse(source).body if isinstance(node,ast.FunctionDef) and node.name=='_bubblewrap_identity')
    if hashlib.sha256(ast.get_source_segment(source,function).encode()).hexdigest()!=PINS['guard_function_sha256']:
        raise RuntimeError('Original guard source does not match')
    old=json.loads((ROOT/PINS['identities']['historical_launch']['path']).read_text())
    overrides=json.loads((ROOT/PINS['identities']['historical_environment']['path']).read_text())
    frame=Path(old['cwd'])
    expected=['bwrap','--die-with-parent','--ro-bind','/','/','--dev','/dev','--proc','/proc',
              '--bind',str(ROOT),str(ROOT),'--chdir',str(frame),'/usr/bin/python3','-B']
    if old['argv'][:len(expected)]!=expected or not frame.is_relative_to(ROOT):
        raise RuntimeError('Original carrier prefix/cwd differs')
    # Same original explicit overrides, including historical owned XDG paths.
    # Payload never creates files there. Ambient historical values were not
    # retained; current inheritance follows the original worker recipe.
    env=dict(os.environ)
    env.update(overrides)
    env.update({'PYTHONDONTWRITEBYTECODE':'1','WORLDLINE_PRIVATE_EVALUATOR_TEST':'1'})
    env.pop('GPR_TOOL',None)
    env.pop('PYTHONSTARTUP',None)
    payload=(METHOD/'payload.py.txt').read_text()
    argv=[*expected,'-c',payload]
    out=args.out.resolve()
    if not out.is_relative_to(ROOT) or out==ROOT:
        raise RuntimeError('Output must be a fresh owned worktree directory')
    out.mkdir(parents=True,exist_ok=False)
    started=stamp();started_ns=time.monotonic_ns()
    launch={'classification':'DIAGNOSTIC ONLY; no acceptance evidence',
            'baseline_commit':args.expected_head,'decisions_sha256':args.decisions_sha256,
            'historical_tested_source':PINS['historical_source_commit'],
            'tracked_paths_differing_from_baseline':dirty_before,
            'source_identity_scope':'Pinned selected method/guard bytes; HEAD alone is not a clean-source claim',
            'argv':argv,'cwd':str(frame),'timeout_seconds':60,
            'explicit_environment_overrides':{**overrides,'PYTHONDONTWRITEBYTECODE':'1','WORLDLINE_PRIVATE_EVALUATOR_TEST':'1'},
            'removed_environment_keys':['GPR_TOOL','PYTHONSTARTUP'],
            'historical_ambient_environment':'UNVERIFIED; original did not retain all inherited values',
            'current_PATH':env.get('PATH'),'original_launch':PINS['identities']['historical_launch'],
            'method_sha256':sha(__file__),'payload_sha256':PAYLOAD_SHA,'pins_sha256':PINS_SHA,
            'started_utc':started,'external_containment':'existing phase1_heavy wrapper required; no new scope/manager operations in this script'}
    save(out/'launch.json',launch)
    exception=None;exit_code=None
    with (out/'stdout').open('xb') as stdout,(out/'stderr').open('xb') as stderr:
        try:
            result=subprocess.run(argv,cwd=frame,env=env,stdout=stdout,stderr=stderr,timeout=60)
            exit_code=result.returncode
        except (subprocess.TimeoutExpired,OSError) as error:
            # subprocess.run kills/waits only this owned timed-out bwrap child.
            exception={'type':type(error).__name__,'message':str(error)}
    result={'classification':'MEASURED diagnostic invocation only',
            'baseline_commit':args.expected_head,'started_utc':started,'ended_utc':stamp(),
            'elapsed_monotonic_ns':time.monotonic_ns()-started_ns,'exit_code':exit_code,'exception':exception,
            'stdout_sha256':sha(out/'stdout'),'stderr_sha256':sha(out/'stderr'),
            'current_HEAD_after':git('rev-parse','HEAD'),
            'tracked_paths_differing_from_baseline_after':git('diff','HEAD','--name-only').splitlines(),
            'guard_source_sha256_after':sha(ROOT/PINS['identities']['current_guard']['path']),
            'decisions_sha256_after':sha(decisions),'metadata_complete':False,
            'guard_would_refuse':None,'failed_predicates':None,
            'non_claims':['Not the original private suite','Not historical missing-stat reconstruction',
                          'No guard change or acceptance result','No inference that any other private prerequisite passes']}
    if exit_code==0 and exception is None:
        try:
            observed=json.loads((out/'stdout').read_text())
            result['metadata_complete']=(isinstance(observed,dict) and observed.get('stat') is not None
                and observed.get('predicates') is not None
                and all(observed.get(name,{}).get('returned') is True for name in ('uid_map','gid_map','user_namespace','mount_namespace'))
                and observed.get('file_sha256') is not None and observed.get('stat_to_hash_identity_equal') is True
                and type(observed.get('guard_would_refuse')) is bool
                and result['current_HEAD_after']==args.expected_head
                and result['decisions_sha256_after']==args.decisions_sha256
                and result['guard_source_sha256_after']==PINS['identities']['current_guard']['sha256'])
            result['guard_would_refuse']=observed.get('guard_would_refuse')
            p=observed.get('predicates')
            if isinstance(p,dict):
                result['failed_predicates']=[name for name in ('absolute','regular_file','owner_is_root_or_real_uid','executable_access') if p.get(name) is False]
                if p.get('forbidden_mode_bits'):
                    result['failed_predicates'].append('forbidden_mode_bits')
        except (ValueError,UnicodeError) as error:
            result['parse_exception']={'type':type(error).__name__,'message':str(error)}
    save(out/'result.json',result)
    print(json.dumps({'out':str(out),'exit_code':exit_code,'metadata_complete':result['metadata_complete'],
                      'guard_would_refuse':result['guard_would_refuse'],'result_sha256':sha(out/'result.json')}))
    return 0 if exit_code==0 and result['metadata_complete'] else 1

if __name__=='__main__':
    raise SystemExit(main())
