"""Explicit genuine protected control entry, never ordinary test discovery.

The outer reviewed WORLDLINE launcher must admit this exact command and complete
descriptor/fixture/runtime closure under its original resource controls. This
entry supplies no authority, provisioning, admission or synthetic positive.
Missing authentic disposable installations or bindings are failures, not skips.
"""
from __future__ import annotations
import sys
_approved=sys.modules.get("_worldline_approved_source_loader")
if _approved is None:raise SystemExit("CONTROL_EARLY_APPROVED_SOURCE_LEASE_REQUIRED")
_lease=_approved.current()
_lease.check()
import argparse,hashlib,json,os,socket,stat,subprocess,types,unittest
from pathlib import Path

CASES={
 'SEQUENTIAL':'test_successful_same_pending_operation_advances_all_lifecycle_steps',
 'DUPLICATE':'test_exact_committed_duplicate_and_recover_return_original_result_without_append',
 'LOST_ACK_RESTART':'test_committed_lost_ack_after_restart_reconciles_once',
 'CONFLICT':'test_same_id_changed_complete_packet_or_owner_refuses_without_mutation',
 'CLOSED_AFTER_COMMIT':'test_historical_exact_response_survives_later_native_state_and_closed_gate',
 'NOT_COMMITTED':'test_not_committed_recovery_does_not_create_an_event',
 'DISPATCH_UNKNOWN':'test_repeated_dispatch_intent_never_launches_again',
 'LEGACY_COMMITTED':'test_legacy_result_import_preserves_complete_original_row',
}

class CampaignRefusal(RuntimeError):pass
def require(value,reason):
    if not value:raise CampaignRefusal(reason)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode('ascii')
def parse(raw):
    def pairs(rows):
        result={}
        for key,val in rows:
            require(key not in result,'CONTROL_DUPLICATE_KEY');result[key]=val
        return result
    value=json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(CampaignRefusal('CONTROL_NONFINITE_JSON')))
    require(raw in (canonical(value),canonical(value)+b'\n'),'CONTROL_NONCANONICAL_DESCRIPTOR')
    return value
def protected(path,*,directory=False,private=False):
    path=Path(path)
    require(path.is_absolute() and str(path)==os.path.normpath(path),'CONTROL_PATH_SPELLING')
    for part in (*reversed(path.parents),path):
        info=part.lstat()
        require(not stat.S_ISLNK(info.st_mode) and info.st_uid==0 and not info.st_mode&0o022,'CONTROL_UNPROTECTED_PATH')
        if part!=path or directory:require(stat.S_ISDIR(info.st_mode),'CONTROL_DIRECTORY_REQUIRED')
    if not directory:require(stat.S_ISREG(info.st_mode),'CONTROL_REGULAR_FILE_REQUIRED')
    if private:require(not path.lstat().st_mode&0o077,'CONTROL_PRIVATE_PATH_REQUIRED')
    return path
def read(path):
    path=protected(path);fd=os.open(path,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW)
    try:
        before=os.fstat(fd);require(before.st_nlink==1,'CONTROL_FILE_LINKS')
        with os.fdopen(os.dup(fd),'rb') as stream:raw=stream.read()
        after=os.fstat(fd);named=path.lstat()
        require((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==
                (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),'CONTROL_FILE_CHANGED')
        require((named.st_dev,named.st_ino)==(after.st_dev,after.st_ino),'CONTROL_FILE_REPLACED')
        return raw
    finally:os.close(fd)
def tree(root):
    root=protected(root,directory=True);result={}
    for path in sorted(root.rglob('*')):
        protected(path,directory=path.is_dir())
        require(path.name!='__pycache__' and path.suffix!='.pyc','CONTROL_TARGET_BYTECODE_PRESENT')
        if path.is_file():result[path.relative_to(root).as_posix()]={'sha256':sha(read(path)),'mode':oct(stat.S_IMODE(path.stat().st_mode))}
    return result
def checked_descriptor(path):
    require(os.geteuid()==0 and sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode,'CONTROL_ISOLATED_ROOT_ENTRY_REQUIRED')
    _lease.check()
    raw=read(protected(path,private=True));record=parse(raw)
    require(type(record) is dict and set(record)=={'schema','installation','trees','files','runtime_files','interpreter','environment','cases'},'CONTROL_DESCRIPTOR_SCHEMA')
    require(record['schema']=='worldline.protected-resource-control-campaign-v1' and type(record['installation']) is str and record['installation'],'CONTROL_INSTALLATION_ABSENT')
    require(type(record['trees']) is dict and record['trees'],'CONTROL_COMPLETE_SOURCE_CLOSURE_REQUIRED')
    allowed=set()
    for root,expected in record['trees'].items():
        actual=tree(root);require(actual==expected,'CONTROL_COMPLETE_SOURCE_CHANGED');allowed.update(Path(root)/key for key in actual)
    require(type(record['files']) is dict and record['files'],'CONTROL_INSTALLED_FILE_CLOSURE_REQUIRED')
    for name,expected in record['files'].items():
        path=protected(name)
        require({'sha256':sha(read(path)),'mode':oct(stat.S_IMODE(path.stat().st_mode))}==expected,'CONTROL_INSTALLED_FILE_CHANGED')
        require(path.suffix!='.pyc','CONTROL_TARGET_BYTECODE_PRESENT')
        if path.suffix=='.py':
            cache=path.parent/'__pycache__'
            require(not path.with_suffix('.pyc').exists() and not (cache.exists() and any(cache.glob(path.stem+'.*.pyc'))),'CONTROL_TARGET_BYTECODE_PRESENT')
        allowed.add(path)
    require(type(record['runtime_files']) is dict and record['runtime_files'],'CONTROL_RUNTIME_CLOSURE_REQUIRED')
    for name,expected in record['runtime_files'].items():require(sha(read(name))==expected,'CONTROL_RUNTIME_CHANGED')
    require(Path(os.readlink('/proc/self/exe'))==Path(record['interpreter']) and record['interpreter'] in record['runtime_files'],'CONTROL_INTERPRETER_CHANGED')
    require(Path(__file__) in allowed,'CONTROL_RUNNING_ENTRY_UNBOUND')
    for module in tuple(sys.modules.values()):
        name=getattr(module,'__file__',None)
        if name is not None:require(Path(name) in allowed or name in record['runtime_files'],'CONTROL_PRELOADED_SOURCE_UNBOUND')
        cache=getattr(module,'__cached__',None)
        if cache is not None and os.path.lexists(cache):require(cache in record['runtime_files'],'CONTROL_PRELOADED_BYTECODE_UNBOUND')
    require(type(record['environment']) is dict and set(record['environment'])=={'PATH','HOME','TMPDIR','LC_ALL'},'CONTROL_ENVIRONMENT_SCHEMA')
    require(type(record['cases']) is dict and set(record['cases'])==set(CASES),'CONTROL_COMPLETE_CASE_ROSTER_REQUIRED')
    for name,spec in record['cases'].items():
        require(type(spec) is dict and set(spec)=={'method','fixture','fixture_sha256','source_roots','control_source','resource_root','gate_source','bridge_source','native_library'},'CONTROL_CASE_BINDING_SCHEMA')
        require(spec['method']==CASES[name],'CONTROL_CASE_METHOD_CHANGED')
        require(type(spec['source_roots']) is list and spec['source_roots'] and len(set(spec['source_roots']))==len(spec['source_roots']),'CONTROL_IMPORT_ROOT_ROSTER')
        for root in spec['source_roots']:
            require(root in record['trees'] or Path(root) in {Path(name).parent for name in record['files']},'CONTROL_IMPORT_ROOT_UNBOUND')
        for key in ('control_source','gate_source','bridge_source','native_library'):require(Path(spec[key]) in allowed,'CONTROL_CASE_SOURCE_OR_NATIVE_UNBOUND')
        require(sha(read(spec['fixture']))==spec['fixture_sha256'],'CONTROL_COMPLETE_FIXTURE_CHANGED')
        fixture=json.loads(read(spec['fixture']))
        require(fixture['resource_root']==spec['resource_root'],'CONTROL_FIXTURE_RESOURCE_ROOT_CHANGED')
        require(Path(spec['resource_root']).name=='resource' and Path(spec['resource_root']).parents[1].parent==Path('/srv') and
                Path(spec['resource_root']).parents[1].name.startswith('cosmogony-canonical-v1.control-'),'CONTROL_DISPOSABLE_INSTALLATION_REQUIRED')
        require(Path(spec['native_library'])==Path(spec['resource_root'])/'libworldline_core.so','CONTROL_NATIVE_LIBRARY_SPLIT')
    return raw,record,allowed
def execute_case(name,record,allowed):
    spec=record['cases'][name]
    # Explicit source roots come only from the complete protected descriptor.
    # Ordinary assurance's import path and discovery remain untouched.
    sys.path[:0]=spec['source_roots']
    import run_service,gate_bridge,intent_gate
    import worldline.resource_run_ledger as caller
    require(Path(run_service.__file__)==Path(spec['resource_root'])/'run_service.py','CONTROL_SERVICE_SOURCE_SPLIT')
    require(Path(gate_bridge.__file__)==Path(spec['bridge_source']) and Path(intent_gate.__file__)==Path(spec['gate_source']),'CONTROL_GATE_SOURCE_SPLIT')
    require(Path(caller.__file__)==Path(spec['resource_root'])/'runtime/worldline/resource_run_ledger.py','CONTROL_CALLER_SOURCE_SPLIT')
    for module in tuple(sys.modules.values()):
        path=getattr(module,'__file__',None)
        if path is not None:require(Path(path) in allowed or path in record['runtime_files'],'CONTROL_IMPORTED_SOURCE_UNBOUND')
    os.environ['WORLDLINE_FULL_RESOURCE_CONTROL_'+name]=spec['fixture']
    path=Path(spec['control_source']);module=types.ModuleType('worldline_genuine_resource_control');module.__file__=str(path)
    # Execute the exact retained control source, never a cached/import substitute.
    exec(_lease.compile_source(str(path),'worldline_genuine_resource_control'),module.__dict__)
    suite=unittest.defaultTestLoader.loadTestsFromName('FullResourceReplayV2Controls.'+spec['method'],module)
    result=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(suite)
    passed=result.wasSuccessful() and result.testsRun==1 and not result.skipped and not result.expectedFailures and not result.unexpectedSuccesses
    print(json.dumps({'case':name,'method':spec['method'],'status':'PASS' if passed else 'FAIL','testsRun':result.testsRun,'skipped':len(result.skipped),'native_and_protected_fixture_required':True,'full_phase_acceptance':False}))
    return 0 if passed else 1
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--descriptor',type=Path,required=True);parser.add_argument('--result-directory',type=Path,required=True);parser.add_argument('--case',choices=tuple(CASES));args=parser.parse_args()
    raw,record,allowed=checked_descriptor(args.descriptor)
    if args.case is not None:
        case_out=protected(args.result_directory,directory=True,private=True)
        try:return execute_case(args.case,record,allowed)
        finally:
            try:closure=_lease.check();closure['closure_status']='CHECKED_SOURCE_COMPONENT'
            except _approved.Refusal as exc:
                closure=_lease.snapshot();closure['closure_status']='REFUSED';closure['reason']=str(exc)
                with (case_out/(args.case+'.executed-code.json')).open('xb') as output:
                    output.write(canonical(closure)+b'\n');output.flush();os.fsync(output.fileno())
                raise CampaignRefusal(str(exc)) from exc
            with (case_out/(args.case+'.executed-code.json')).open('xb') as output:
                output.write(canonical(closure)+b'\n');output.flush();os.fsync(output.fileno())
    out=protected(args.result_directory,directory=True,private=True);records=[];unrun=list(CASES)
    environment=dict(record['environment'])
    for name in CASES:
        # Native service module location binds each case to its own genuine
        # disposable installation. Separate processes avoid import cross-talk.
        command=[record['interpreter'],'-I','-S','-B',_lease.helper_path,'--bootstrap-envelope',_lease.envelope_path,'--entry',str(Path(__file__)),'--descriptor',str(args.descriptor),'--result-directory',str(out),'--case',name]
        with (out/(name+'.stdout')).open('xb') as stdout,(out/(name+'.stderr')).open('xb') as stderr:
            child=subprocess.Popen(command,env=environment,stdout=stdout,stderr=stderr)
            wait=child.wait();stdout.flush();stderr.flush();os.fsync(stdout.fileno());os.fsync(stderr.fileno())
        records.append({'case':name,'argv':command,'pid':child.pid,'actual_child_wait':wait,'stdout_sha256':sha(read(out/(name+'.stdout'))),'stderr_sha256':sha(read(out/(name+'.stderr')))})
        closure_path=out/(name+'.executed-code.json')
        if closure_path.exists():
            closure_raw=read(closure_path);closure=parse(closure_raw)
            records[-1]['executed_code_sha256']=sha(closure_raw)
            require(closure['envelope_bytes_hex']==_lease.envelope.hex() and closure['authority_or_phase_acceptance'] is False,'CONTROL_CHILD_BOOTSTRAP_ENVELOPE_SPLIT')
            if closure.get('closure_status')!='CHECKED_SOURCE_COMPONENT':wait=1
        else:
            records[-1]['executed_code_closure']='ABSENT_REFUSED';wait=1
        records[-1]['entry_and_closure_success']=wait==0
        unrun.remove(name)
        require(read(args.descriptor)==raw,'CONTROL_DESCRIPTOR_CHANGED_AFTER_CASE')
        checked_descriptor(args.descriptor)
        if wait!=0:break
    summary={'schema':'worldline.protected-resource-control-results-v1','descriptor_sha256':sha(raw),'records':records,'unrun':unrun,'all_actual_pass':not unrun and all(row['actual_child_wait']==0 and row['entry_and_closure_success'] for row in records),'full_phase_acceptance':False,'outer_actual_scope_wait_and_full_admission_binding_still_required':True}
    with (out/'result.json').open('xb') as f:f.write(canonical(summary)+b'\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(summary));return 0 if summary['all_actual_pass'] else 1
if __name__=='__main__':
    try:raise SystemExit(main())
    except (CampaignRefusal,_approved.Refusal) as exc:
        print(json.dumps({'status':'REFUSED','reason':str(exc),'no_skip_or_positive_claim':True}),file=sys.stderr);raise SystemExit(1)
