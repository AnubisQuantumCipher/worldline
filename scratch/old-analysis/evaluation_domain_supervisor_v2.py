#!/usr/bin/env python3
"""Prepared retained two-arm gate with the reviewed owned-service supervisor.

Original predicates and decisive source are loaded unchanged from the explicit
frozen frame. The local retained/audit carrier is an adaptation, not D7 historical
collector equivalence. No execution occurs merely by importing this module.
"""
from __future__ import annotations
import argparse,ast,hashlib,importlib.util,json,os,re,subprocess,sys,tarfile,tempfile,traceback
from pathlib import Path
import full_runtime_supervisor_v3 as carrier
from frozen_source_v2 import validate

ROOT=Path(__file__).resolve().parents[2]
OWN=ROOT/'scratch/old-analysis'
ENTRY=OWN/'evaluation_domain_entry_v1.py'
AUDIT=OWN/'runtime_audit_entry.py'
ORIGINAL_CARRIER=OWN/'full_runtime_supervisor_v3.py'
PIN='1bd5c0890e1c2686b3e33389831c76fe1f5cc25b'
TREE='1c628de542bfc843f5f5e1aaa0580a0c4b12c40e'
TAG='counterexample/verifier-bytes-without-evaluation-domain'

def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def save(path,value):
    with Path(path).open('x') as stream:
        json.dump(value,stream,sort_keys=True,indent=2,default=str);stream.write('\n')

def load(path):return json.loads(Path(path).read_text())
def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args],text=True).strip()

def owned_file(path):
    path=Path(path).resolve(strict=True)
    if not path.is_relative_to(ROOT) or not path.is_file():raise RuntimeError('Required owned file absent')
    return path

def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result)
    return result

def source_contract(frame):
    contract=module(frame/'scripts/assurance_contract.py','phase1_domain_contract')
    if (contract.COUNTEREXAMPLE_TAG,contract.COUNTEREXAMPLE_COMMIT,contract.COUNTEREXAMPLE_RUNTIME_TREE)!=(TAG,PIN,TREE):
        raise RuntimeError('Original control pins changed; no substituted control permitted')
    original_gate=frame/'scripts/evaluation_domain_gate.py'
    original_assurance=frame/'scripts/assurance.py'
    timed=[]
    for path,function in ((original_gate,'run'),(original_assurance,'evaluation_domain')):
        definitions=[n for n in ast.walk(ast.parse(path.read_text())) if isinstance(n,ast.FunctionDef) and n.name==function]
        if len(definitions)!=1:raise RuntimeError('Original function identity ambiguous')
        values=[ast.literal_eval(k.value) for call in ast.walk(definitions[0]) if isinstance(call,ast.Call)
                for k in call.keywords if k.arg=='timeout']
        if len(values)!=1:raise RuntimeError('Original deadline missing or ambiguous')
        timed.append(values[0])
    if timed!=[900,1800]:raise RuntimeError('Original child/caller timeout changed')
    return {'required_steps':list(contract.REQUIRED_STEPS),'tag':TAG,'commit':PIN,'runtime_tree':TREE,
            'decisive_timeout':timed[0],'assurance_caller_timeout':timed[1],
            'sources':{str(p):sha(p) for p in (original_gate,original_assurance,frame/'scripts/decisive_evaluation_test.py',frame/'scripts/assurance_contract.py')}}

def runtime_qualification(path,commit):
    path=owned_file(path);q=load(path)
    if q.get('exit_code')!=0:raise RuntimeError('Actual paired runtime carrier qualification did not pass')
    attempt=Path(q['attempt']).resolve(strict=True)
    if not attempt.is_relative_to(OWN):raise RuntimeError('Qualification attempt outside owned scratch')
    launch=load(path.parent/'launch.json');locked=load(attempt/'locked-result.json')
    worker=load(attempt/'worker/worker-result.json');typed=load(attempt/'typed-manager-qualification.json')
    if (launch.get('source_commit')!=commit or launch.get('driver_sha256')!=sha(ORIGINAL_CARRIER)
        or launch.get('audit_sha256')!=sha(AUDIT) or worker.get('source_commit')!=commit
        or worker.get('suite')!='qualification' or worker.get('all_original_steps_pass') is not True
        or locked.get('exit_code')!=0 or locked.get('all_owned_units_quiescent') is not True
        or locked.get('unresolved_potential_siblings') or locked.get('audit_failures')
        or typed.get('all_required_launch_forms_matched') is not True):
        raise RuntimeError('Missing exact paired runtime/parser/typed-manager/cleanup qualification')
    steps=worker.get('steps')
    if not isinstance(steps,list) or [s.get('name') for s in steps]!=['qualification-plain','qualification-audit']:
        raise RuntimeError('Original paired runtime qualification roster absent')
    if any(s.get('ok') is not True or s.get('original_parser',{}).get('skipped')!=0 for s in steps):
        raise RuntimeError('Runtime qualification skipped or failed a required original case')
    return {'receipt':str(path),'sha256':sha(path),'attempt':str(attempt),
            'joined_files':{str(p):sha(p) for p in (path.parent/'launch.json',attempt/'locked-result.json',attempt/'worker/worker-result.json',attempt/'typed-manager-qualification.json')},
            'scope':'paired unchanged real supervision only; not a universal audit or collector equivalence claim'}

def materialize_control(out):
    actual=(git('rev-parse',TAG+'^{commit}'),git('rev-parse',TAG+':runtime'))
    if actual!=(PIN,TREE):raise RuntimeError('Pinned tag or runtime tree mismatch/unavailable')
    archive=out/'counterexample-runtime.tar';destination=out/'counterexample'
    with archive.open('xb') as stream:
        r=subprocess.run(['git','-C',str(ROOT),'archive','--format=tar',PIN,'runtime'],stdout=stream,stderr=subprocess.PIPE)
    (out/'counterexample-archive.stderr').write_bytes(r.stderr)
    if r.returncode or not archive.stat().st_size:raise RuntimeError('Pinned runtime archive unavailable')
    destination.mkdir()
    with tarfile.open(archive) as tar:
        for member in tar.getmembers():
            path=Path(member.name)
            if path.is_absolute() or '..' in path.parts or path.parts[:1]!=('runtime',) or not (member.isdir() or member.isfile()):
                raise RuntimeError('Original archive contains unsupported ownership/type/path; refuse instead of excluding a source')
        tar.extractall(destination,filter='data')
    rows=[]
    entries=subprocess.check_output(['git','-C',str(ROOT),'ls-tree','-rz',PIN,'runtime']).decode().split('\0')
    for entry in entries:
        if not entry:continue
        metadata,name=entry.split('\t',1);mode,kind,blob=metadata.split()
        path=destination/name
        if kind!='blob' or mode not in ('100644','100755') or not path.is_file() or not path.resolve().is_relative_to(destination):
            raise RuntimeError('Original pinned runtime file type/roster mismatch')
        actual_blob=git('hash-object',str(path))
        if actual_blob!=blob:raise RuntimeError('Pinned runtime source bytes differ: '+name)
        rows.append({'path':name,'git_mode':mode,'expected_blob':blob,'actual_blob':actual_blob,'sha256':sha(path)})
    present={str(p.relative_to(destination)) for p in destination.rglob('*') if p.is_file()}
    if not rows or present!={r['path'] for r in rows}:raise RuntimeError('Pinned runtime source roster incomplete or extra')
    record={'tag':TAG,'commit':PIN,'runtime_tree':TREE,'archive_sha256':sha(archive),'files':rows,
            'no_runtime_source_modification':True,'materialization':str(destination)}
    save(out/'counterexample-source.json',record)
    return destination/'runtime',record

def validate_control(record):
    destination=Path(record['materialization'])
    if (git('rev-parse',TAG+'^{commit}'),git('rev-parse',TAG+':runtime'))!=(PIN,TREE):
        raise RuntimeError('Pinned tag changed during run')
    if any(sha(destination/row['path'])!=row['sha256'] for row in record['files']):
        raise RuntimeError('Pinned runtime mutated during run')

def base(args,phase,out):
    command=[sys.executable,'-B',str(Path(__file__).resolve()),'--phase',phase,'--out',str(out),
        '--expected-commit',args.expected_commit,'--mode',args.mode,'--scope-timeout',args.scope_timeout,
        '--freeze-record',str(args.freeze_record),'--frame',str(args.frame),'--build-manifest',str(args.build_manifest),
        '--runtime-qualification',str(args.runtime_qualification)]
    if args.domain_qualification:command+=['--domain-qualification',str(args.domain_qualification)]
    return command

def payload(args):
    """Load original main/predicates; adapt only run's carrier/retention."""
    record=load(args.payload_record);out=args.out;out.mkdir(exist_ok=False)
    frame=Path(record['frame']);original=module(frame/'scripts/evaluation_domain_gate.py','phase1_original_domain_gate')
    decisive=frame/'scripts/decisive_evaluation_test.py'
    arm_rows=[]
    engines=[Path(record['engine']),Path(record['counterexample'])]
    names=['candidate','counterexample']
    def retained_run(engine,core_lib):
        index=len(arm_rows)
        if index>=len(engines) or engine.resolve()!=engines[index].resolve():
            raise RuntimeError('Original two-arm invocation order/domain changed')
        name=names[index];folder=out/name;folder.mkdir()
        # Original removes only empty ambient values for both arms.
        environment={key:value for key,value in os.environ.items() if value}
        if core_lib is not None:environment['WORLDLINE_CORE_LIB']=str(core_lib)
        temporary=Path(tempfile.mkdtemp(prefix='evaldomain-',dir=ROOT))
        verdict_path=temporary/'verdict.json'
        original_argv=[sys.executable,str(decisive),'--engine',str(engine),'--json',str(verdict_path)]
        command=original_argv if record['audit_mode']=='plain' else [sys.executable,'-B',str(ENTRY),
            '--script',str(decisive),'--script-sha256',sha(decisive),'--out',str(folder/'audit'),'--',*original_argv[2:]]
        row={'name':name,'engine':str(engine),'argv':command,'original_argv':original_argv,
             'timeout':record['contract']['decisive_timeout'],'verdict_directory':str(temporary),
             'retention_adaptation':'Original temporary verdict is retained, never substituted or prepopulated',
             'exit_code':None,'verdict':None,'verdict_present':False,'audit_mode':record['audit_mode']}
        arm_rows.append(row);save(folder/'launch.json',row)
        try:
            with (folder/'stdout-stderr').open('xb') as stream:
                result=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,timeout=row['timeout'],env=environment)
            row['exit_code']=result.returncode
            output=(folder/'stdout-stderr').read_text()
            try:verdict=json.loads(verdict_path.read_text(encoding='utf-8'))
            except (OSError,json.JSONDecodeError):verdict={}
            if verdict_path.is_file():
                (folder/'verdict.json').write_bytes(verdict_path.read_bytes())
                row['verdict_present']=True;row['verdict_sha256']=sha(folder/'verdict.json')
            row['verdict']=verdict
            row['output_sha256']=sha(folder/'stdout-stderr')
            if record['audit_mode']=='audit':
                audit_path=folder/'audit/audit-result.json'
                row['audit_result']=load(audit_path) if audit_path.is_file() else None
            return result.returncode,output,verdict
        except BaseException as error:
            row['exception']={'type':type(error).__name__,'message':str(error)}
            raise
        finally:save(folder/'result.json',row)
    original.run=retained_run
    saved_argv=sys.argv
    status=1;failure=None
    try:
        sys.argv=[str(frame/'scripts/evaluation_domain_gate.py'),'--engine',record['engine'],
                  '--counterexample',record['counterexample'],'--core-lib',record['library']]
        status=original.main()
    except BaseException as error:
        failure={'type':type(error).__name__,'message':str(error)}
        (out/'exception.txt').write_text(traceback.format_exc())
    finally:
        sys.argv=saved_argv
        complete=[r['name'] for r in arm_rows]==names and all(type(r['exit_code']) is int and r['verdict_present'] for r in arm_rows)
        candidate=original.candidate_holds(arm_rows[0]['exit_code'],arm_rows[0]['verdict']) if complete else None
        control=original.control_detected(arm_rows[1]['exit_code'],arm_rows[1]['verdict']) if complete else None
        audit_ok=record['audit_mode']=='plain' or (complete and all(r.get('audit_result') is not None and not r['audit_result']['audit_failures'] and r['audit_result']['exception'] is None for r in arm_rows))
        ok=status==0 and complete and candidate is True and control[0] is True and audit_ok
        save(out/'payload-result.json',{'source_commit':args.expected_commit,'original_main_exit':status,
            'exception':failure,'original_arm_roster':names,'arms':arm_rows,'complete_roster':complete,
            'candidate_holds':candidate,'control_detected':control,'audit_ok':audit_ok,'ok':ok,
            'predicate_source':str(frame/'scripts/evaluation_domain_gate.py'),'predicate_source_sha256':sha(frame/'scripts/evaluation_domain_gate.py'),
            'local_carrier_adaptation':True,'historical_collector_equivalence':'UNVERIFIED','independent_acceptance':'NOT PERFORMED'})
    return 0 if ok else 1

def worker(args):
    out=args.out;status=1;record={'status':'UNVERIFIED','source_commit':args.expected_commit,'steps':[],
        'original_gate_step':'evaluation-domain','independent_acceptance':'NOT PERFORMED',
        'historical_collector_equivalence':'UNVERIFIED; D7 gap not closed by this local carrier'}
    counter_record=None
    try:
        before=validate(args.expected_commit,args.freeze_record,args.frame,args.build_manifest,link=True)
        save(out/'frame-before.json',before);record['identity_before']=before
        record['runtime_qualification']=runtime_qualification(args.runtime_qualification,args.expected_commit)
        contract=source_contract(args.frame);record['original_contract']=contract
        counter,counter_record=materialize_control(out)
        record['counterexample_source']=counter_record
        if args.mode=='gate':
            if args.domain_qualification is None:raise RuntimeError('Actual paired domain qualification required')
            previous=load(owned_file(args.domain_qualification))
            if (previous.get('status')!='TESTED finite paired domain carrier qualification'
                or previous.get('source_commit')!=args.expected_commit
                or previous.get('library_sha256')!=before['library_sha256']
                or previous.get('entry_sha256')!=sha(ENTRY)
                or previous.get('supervisor_sha256')!=sha(__file__)
                or not previous.get('output_hashes')):
                raise RuntimeError('Domain qualification missing or source/library/observer mismatch')
            for path,wanted in previous['output_hashes'].items():
                path=owned_file(path)
                if sha(path)!=wanted:raise RuntimeError('Domain qualification evidence changed')
            record['domain_qualification']={'path':str(args.domain_qualification),'sha256':sha(args.domain_qualification)}
        env=dict(os.environ)
        env.update({'HOME':str(ROOT),'TMPDIR':str(ROOT),'XDG_RUNTIME_DIR':str(ROOT),
            'XDG_CONFIG_HOME':str(out/'xdg-config'),'XDG_DATA_HOME':str(out/'xdg-data'),
            'XDG_STATE_HOME':str(out/'xdg-state'),'XDG_CACHE_HOME':str(out/'xdg-cache'),
            'DBUS_SESSION_BUS_ADDRESS':carrier.manager_env()['DBUS_SESSION_BUS_ADDRESS'],
            'PYTHONPATH':str(args.frame/'runtime'),'PYTHONDONTWRITEBYTECODE':'1',
            'WORLDLINE_PRIVATE_EVALUATOR_TEST':'1','WORLDLINE_CORE_LIB':before['library']})
        for name in ('xdg-config','xdg-data','xdg-state','xdg-cache'):(out/name).mkdir()
        env.pop('PYTHONSTARTUP',None)
        save(out/'environment.json',{key:env[key] for key in ('HOME','TMPDIR','XDG_RUNTIME_DIR','XDG_CONFIG_HOME','XDG_DATA_HOME','XDG_STATE_HOME','XDG_CACHE_HOME','DBUS_SESSION_BUS_ADDRESS','PYTHONPATH','WORLDLINE_CORE_LIB','PYTHONDONTWRITEBYTECODE','WORLDLINE_PRIVATE_EVALUATOR_TEST')})
        modes=['plain','audit'] if args.mode=='qualify' else ['audit']
        for mode in modes:
            config={'frame':str(args.frame),'engine':str(args.frame/'runtime'),'counterexample':str(counter),
                    'library':before['library'],'audit_mode':mode,'contract':contract}
            config_path=out/(mode+'-payload-input.json');save(config_path,config)
            target=out/(mode+'-gate')
            argv=['bwrap','--die-with-parent','--ro-bind','/','/','--dev','/dev','--proc','/proc',
                '--bind',str(ROOT),str(ROOT),'--chdir',str(args.frame),sys.executable,'-B',str(Path(__file__).resolve()),
                '--phase','payload','--out',str(target),'--expected-commit',args.expected_commit,'--payload-record',str(config_path)]
            step={'name':mode,'argv':argv,'timeout':contract['assurance_caller_timeout'],'exit_code':None}
            record['steps'].append(step)
            with (out/(mode+'-gate.output')).open('xb') as stream:
                result=subprocess.run(argv,cwd=args.frame,env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=step['timeout'])
            step['exit_code']=result.returncode
            result_path=target/'payload-result.json'
            step['payload']=load(result_path) if result_path.is_file() else None
            output=(out/(mode+'-gate.output')).read_text()
            step['original_assurance_defect_marker']='the known defect was OBSERVED' in output
            step['ok']=result.returncode==0 and step['original_assurance_defect_marker'] and step['payload'] is not None and step['payload']['ok'] is True
            if not step['ok']:raise RuntimeError('Original complete two-arm gate failed; preserve actual result without running another qualification arm')
        if args.mode=='qualify':
            def signature(value):
                return [{'name':a['name'],'exit_code':a['exit_code'],'allHold':a['verdict'].get('allHold'),
                    'ranAtAll':a['verdict'].get('ranAtAll'),'properties':[(p['name'],p['holds']) for p in a['verdict'].get('properties',[])],
                    'observedVulnerability':a['verdict'].get('observedVulnerability')} for a in value['arms']]
            record['paired_original_predicate_parity']=signature(record['steps'][0]['payload'])==signature(record['steps'][1]['payload'])
            if not record['paired_original_predicate_parity']:raise RuntimeError('Plain/audited decisive outcomes differ')
        validate_control(counter_record)
        after=validate(args.expected_commit,args.freeze_record,args.frame,args.build_manifest)
        save(out/'frame-after.json',after);record['identity_after']=after
        record['status']='TESTED worker original two-arm predicates; outer ownership/cleanup joins still required'
        status=0
    except BaseException as error:
        record['status']='FAILED-OPEN domain prerequisite, instrument or original gate'
        record['exception']={'type':type(error).__name__,'message':str(error)}
        (out/'exception.txt').write_text(traceback.format_exc())
    finally:
        record['exit_code']=status
        save(out/'worker-result.json',record)
    return status

def final_join(args,outer_exit):
    result={'status':'FAILED-OPEN domain carrier or gate','source_commit':args.expected_commit,
        'outer_exit':outer_exit,'mode':args.mode,'entry_sha256':sha(ENTRY),'supervisor_sha256':sha(__file__),
        'original_carrier_sha256':sha(ORIGINAL_CARRIER),'audit_helper_sha256':sha(AUDIT),
        'independent_acceptance':'NOT PERFORMED','historical_collector_equivalence':'UNVERIFIED',
        'native_entry':'UNVERIFIED','output_hashes':{}}
    try:
        outer=load(args.out/'result.json');attempt=Path(outer['attempt'])
        locked=load(attempt/'locked-result.json');worker_record=load(attempt/'worker/worker-result.json')
        result['worker']=worker_record;result['locked_result']=locked
        if outer_exit!=0 or locked.get('exit_code')!=0 or worker_record.get('exit_code')!=0:
            raise RuntimeError('Original gate or owned cleanup did not complete successfully')
        if locked.get('all_owned_units_quiescent') is not True or locked.get('unresolved_potential_siblings'):
            raise RuntimeError('Owned/unknown sibling settlement unresolved')
        match_path=attempt/'exact-launch-matches.jsonl'
        matches=[json.loads(x) for x in match_path.read_text().splitlines()] if match_path.is_file() else []
        audit_step=next(s for s in worker_record['steps'] if s['name']=='audit')
        joined=[]
        for arm in audit_step['payload']['arms']:
            suffix='/audit-gate/'+arm['name']+'/audit/popen.jsonl'
            selected=[x for x in matches if x['receipt']['receipt_path'].endswith(suffix)]
            if not selected:raise RuntimeError('No exact typed manager launch join for original '+arm['name']+' arm')
            joined.extend(selected)
        result['exact_audited_arm_launch_joins']=joined
        result['library_sha256']=worker_record['identity_after']['library_sha256']
        result['status']=('TESTED finite paired domain carrier qualification' if args.mode=='qualify'
                          else 'TESTED original two-arm evaluation-domain predicates on qualified local carrier')
        result['non_claims']=['Not F3 complete assurance or independent acceptance',
            'Not universal audit transparency, native kernel entry, authentic protected/actor execution, or D7 historical collector equivalence',
            'Original no-enforcement fixtures remain; worker scope cap is not an aggregate cap on sibling services']
    except BaseException as error:result['exception']={'type':type(error).__name__,'message':str(error)}
    result['output_hashes']={str(p):sha(p) for p in args.out.rglob('*') if p.is_file() and not p.is_symlink()}
    save(args.out/'domain-final.json',result)
    return 0 if result['status'].startswith('TESTED') else 1

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--phase',choices=('outer','locked','worker','payload'),default='outer')
    p.add_argument('--out',type=Path,required=True);p.add_argument('--expected-commit',required=True)
    p.add_argument('--payload-record',type=Path)
    p.add_argument('--mode',choices=('qualify','gate'));p.add_argument('--scope-timeout')
    for name in ('freeze-record','frame','build-manifest','runtime-qualification','domain-qualification'):
        p.add_argument('--'+name,type=Path)
    args=p.parse_args();args.out=args.out.resolve()
    if not args.out.is_relative_to(OWN) or not re.fullmatch('[a-f0-9]{40}',args.expected_commit):p.error('Fresh owned output and exact source commit required')
    if args.phase=='payload':
        if args.payload_record is None:p.error('Payload input required')
        args.payload_record=owned_file(args.payload_record)
        return payload(args)
    if any(getattr(args,n) is None for n in ('mode','scope_timeout','freeze_record','frame','build_manifest','runtime_qualification')):
        p.error('Explicit frozen identities, runtime qualification and coordinator-selected containment deadline required')
    for name in ('freeze_record','frame','build_manifest','runtime_qualification','domain_qualification'):
        value=getattr(args,name)
        if value is not None:
            value=value.resolve()
            if not value.is_relative_to(ROOT):p.error('All identity/qualification inputs must be owned worktree paths')
            setattr(args,name,value)
    # Reuse original reviewed supervisor unchanged: only its worker argv and
    # audit identity point to this distinct declared local domain carrier.
    carrier.FREEZE=args.freeze_record;carrier.FRAME=args.frame;carrier.BUILD=args.build_manifest
    carrier.AUDIT=ENTRY;carrier.base=base
    args.suite='evaluation-domain'
    os.chdir(ROOT)
    if args.phase=='worker':return worker(args)
    if args.phase=='locked':return carrier.locked(args)
    return final_join(args,carrier.outer(args))

if __name__=='__main__':raise SystemExit(main())
