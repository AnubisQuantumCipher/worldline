"""Explicit genuine protected startup campaign; no ordinary discovery changes.

Requires a separately qualified early helper and genuine owner-provisioned
disposable fixtures, outer admission and child terminal/mapping evidence. UNRUN.
"""
import sys
_approved=sys.modules.get('_worldline_approved_source_loader')
if _approved is None:raise SystemExit('STARTUP_CONTROL_EARLY_APPROVED_LEASE_REQUIRED')
_lease=_approved.current()
if type(_lease) is not _approved.ApprovedSourceLease:raise SystemExit('STARTUP_CONTROL_EXACT_EARLY_LEASE_REQUIRED')
_lease.check()
import argparse,hashlib,json,os,stat,subprocess,types,unittest
from pathlib import Path

ORIGINAL_SHA='a0d2d529aff1322ce11e66d955f5af4161cbdfff59e0c032d770c51e734cdbeb'
ORIGINAL_CASES={
 'SECOND_LEASE':('test_second_lease_refuses_original_store_lock','EMPTY_GENESIS'),
 'MISSING_LOCK':('test_missing_prior_lock_does_not_regenerate','MISSING_LOCK'),
 'LEGACY_ENDPOINT':('test_legacy_endpoint_refuses_without_removing_it','LEGACY_ENDPOINT'),
 'CONSUMED_MISSING':('test_missing_consumed_journal_refuses_exact_existing_ledger','CONSUMED_MISSING'),
 'INTENT_MISSING':('test_pending_missing_intent_refuses_without_recreation','INTENT_MISSING'),
 'OWNER_GENESIS':('test_owner_genesis_creates_exact_bytes_once','EMPTY_GENESIS'),
 'INTENT_PRESENT':('test_exact_present_intent_finishes_without_file_replacement','INTENT_PRESENT'),
 'FRONTIER':('test_current_source_frontier_names_full_ledger_startup_gap','COMPOSED_NATIVE_PROOF'),
}
ADDITIONAL_CASES={
 'PRESENT_UNUSED':'test_present_unused_consumes_without_replacing_exact_file',
 'CHANGED_INTENT':'test_changed_present_intent_refuses_without_consumption',
 'SYMLINK_INTENT':'test_symlink_intent_refuses_without_replacement',
 'MULTILINK_INTENT':'test_multilink_intent_refuses_without_consumption',
 'PRESENT_CAPABILITY':'test_present_capability_layout_has_no_provisioning_effect',
 'MISSING_CAPABILITY':'test_missing_capability_member_refuses_without_creation',
 'UNSAFE_CAPABILITY':'test_unsafe_capability_member_refuses_without_chmod',
 'ZERO_KERNEL_PEER':'test_configured_zero_uid_matches_actual_kernel_peer_without_authorizing',
}
ALL_CASES=tuple(ORIGINAL_CASES)+tuple(ADDITIONAL_CASES)
class Refusal(RuntimeError):pass
def require(condition,reason):
    if not condition:raise Refusal(reason)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf-8')
def parse(raw):
    def pairs(rows):
        value={}
        for key,item in rows:require(key not in value,'STARTUP_CONTROL_DUPLICATE_KEY');value[key]=item
        return value
    value=json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(Refusal('STARTUP_CONTROL_NONFINITE_JSON')))
    require(raw in (canonical(value),canonical(value)+b'\n'),'STARTUP_CONTROL_NONCANONICAL_JSON');return value
def protected(path,*,directory=False,private=False):
    path=Path(path);require(path.is_absolute() and str(path)==os.path.normpath(path),'STARTUP_CONTROL_PATH_SPELLING')
    for part in (*reversed(path.parents),path):
        info=part.lstat();require(info.st_uid==0 and not stat.S_ISLNK(info.st_mode) and not info.st_mode&0o022,'STARTUP_CONTROL_UNPROTECTED_PATH')
        if part!=path or directory:require(stat.S_ISDIR(info.st_mode),'STARTUP_CONTROL_DIRECTORY_REQUIRED')
    if not directory:require(stat.S_ISREG(info.st_mode),'STARTUP_CONTROL_REGULAR_FILE_REQUIRED')
    if private:require(not info.st_mode&0o077,'STARTUP_CONTROL_PRIVATE_PATH_REQUIRED')
    return path
def read(path,*,links=1):
    path=protected(path);fd=os.open(path,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW)
    try:
        before=os.fstat(fd);require(before.st_nlink==links,'STARTUP_CONTROL_LINK_ROSTER_CHANGED')
        with os.fdopen(os.dup(fd),'rb') as source:raw=source.read()
        after=os.fstat(fd);named=path.lstat()
        require((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns,before.st_mode,before.st_nlink)==
                (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns,after.st_mode,after.st_nlink),'STARTUP_CONTROL_FILE_CHANGED')
        require((named.st_dev,named.st_ino)==(after.st_dev,after.st_ino),'STARTUP_CONTROL_FILE_REPLACED');return raw
    finally:os.close(fd)
def tree(root):
    root=protected(root,directory=True);records={}
    for path in sorted(root.rglob('*')):
        protected(path,directory=path.is_dir())
        if path.is_file():records[path.relative_to(root).as_posix()]={'sha256':sha(read(path)),'mode':oct(stat.S_IMODE(path.stat().st_mode))}
    return records
def checked_campaign(path):
    require(os.geteuid()==0 and sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode,'STARTUP_CONTROL_ROOT_I_S_B_REQUIRED')
    _lease.check();raw=_lease.file(str(protected(path,private=True)),('DATA',));value=parse(raw)
    require(type(value) is dict and set(value)=={'schema','entry','control_source','additional_source','trees','files','cases','environment'},'STARTUP_CONTROL_CAMPAIGN_SCHEMA')
    require(value['schema']=='worldline.protected-startup-control-campaign-v1' and value['entry']==__file__,'STARTUP_CONTROL_RUNNING_ENTRY_SPLIT')
    require(type(value['trees']) is dict and value['trees'] and type(value['files']) is dict and value['files'],'STARTUP_CONTROL_COMPLETE_IMMUTABLE_SOURCE_REQUIRED')
    allowed=set()
    for root,expected in value['trees'].items():
        actual=tree(root);require(actual==expected,'STARTUP_CONTROL_SOURCE_TREE_CHANGED');allowed.update(str(Path(root)/name) for name in actual)
    for name,expected in value['files'].items():
        actual=read(name);require({'sha256':sha(actual),'mode':oct(stat.S_IMODE(Path(name).stat().st_mode))}==expected,'STARTUP_CONTROL_IMMUTABLE_FILE_CHANGED');allowed.add(name)
    for name in (value['entry'],value['control_source'],value['additional_source'],_lease.helper_path):require(name in allowed,'STARTUP_CONTROL_EXECUTABLE_SOURCE_UNBOUND')
    require(sha(read(value['control_source']))==ORIGINAL_SHA and stat.S_IMODE(Path(value['control_source']).stat().st_mode)==0o644,'STARTUP_CONTROL_ORIGINAL_SOURCE_CHANGED')
    require(type(value['cases']) is dict and set(value['cases'])==set(ALL_CASES),'STARTUP_CONTROL_COMPLETE_CASE_ROSTER_REQUIRED')
    require(type(value['environment']) is dict and set(value['environment'])=={'PATH','HOME','TMPDIR','LC_ALL'},'STARTUP_CONTROL_ENVIRONMENT_SCHEMA')
    selected=[]
    for name,spec in value['cases'].items():
        require(type(spec) is dict and set(spec)=={'method','startup_descriptor','startup_descriptor_sha256','fixture','immutable_files','initial_files','initial_nodes','expected_absent'},'STARTUP_CONTROL_CASE_SCHEMA')
        expected=ORIGINAL_CASES[name][0] if name in ORIGINAL_CASES else ADDITIONAL_CASES[name]
        require(spec['method']==expected,'STARTUP_CONTROL_CASE_METHOD_CHANGED')
        selected.append(spec['startup_descriptor'])
        descriptor_raw=_lease.file(str(protected(spec['startup_descriptor'],private=True)),('DATA',))
        require(sha(descriptor_raw)==spec['startup_descriptor_sha256'],'STARTUP_CONTROL_EXACT_DESCRIPTOR_CHANGED');descriptor=parse(descriptor_raw)
        require(descriptor['schema']=='worldline.protected-startup-v1','STARTUP_CONTROL_INSTALLED_DESCRIPTOR_SCHEMA')
        runtime=descriptor['runtime'];authority=Path(descriptor['paths']['authority_root'])
        require(authority.parent==Path('/srv') and authority.name.startswith('cosmogony-canonical-v1.control-'),'STARTUP_CONTROL_DISPOSABLE_INSTALLATION_REQUIRED')
        require(runtime['interpreter']==_lease.interpreter,'STARTUP_CONTROL_INTERPRETER_SPLIT')
        roots=(str(Path(runtime['worldline_source'])/'runtime'),str(Path(runtime['gate_source']).parent),str(Path(runtime['principal_source']).parent))
        for root in roots:_lease.directory_or_absent(root)
        require(runtime['worldline_source'] in descriptor['trees'],'STARTUP_CONTROL_COMPLETE_WORLDLINE_SOURCE_REQUIRED')
        for key in ('gate_source','principal_source','native_library','proof_manifest','proof_summary'):
            require(runtime[key] in allowed,'STARTUP_CONTROL_NATIVE_PROOF_OR_PRINCIPAL_UNBOUND')
        require(runtime['worldline_source']+'/runtime/worldline/protected_startup.py' in allowed,'STARTUP_CONTROL_STARTUP_SOURCE_UNBOUND')
        genesis=parse(_lease.file(str(protected(descriptor['genesis'],private=True)),('DATA',)))
        declared=set(spec['immutable_files'])|set(spec['initial_files'])|set(spec['initial_nodes'])|set(spec['expected_absent'])
        required=set(descriptor['provisioned_state'])|{spec['startup_descriptor'],descriptor['genesis'],descriptor['bootstrap_ledger']}
        required.update(journal['path'] for journal in genesis['journals'].values())
        require(required<=declared,'STARTUP_CONTROL_COMPLETE_STATE_ROSTER_MISSING')
        if name=='MISSING_LOCK':require(str(Path(descriptor['paths']['state'])/'worldline-store.lock') in spec['expected_absent'],'STARTUP_CONTROL_MISSING_LOCK_FIXTURE_CHANGED')
        if name=='LEGACY_ENDPOINT':require(str(Path(descriptor['paths']['runtime'])/'worldlined.sock') in spec['initial_nodes'],'STARTUP_CONTROL_LEGACY_ENDPOINT_FIXTURE_CHANGED')
        if name in ORIGINAL_CASES:require(spec['fixture']==spec['startup_descriptor'],'STARTUP_CONTROL_ORIGINAL_FIXTURE_SPLIT')
        else:
            additive=parse(_lease.file(str(protected(spec['fixture'],private=True)),('DATA',)))
            require(set(additive)=={'startup_descriptor','journal_name','capability_member'} and additive['startup_descriptor']==spec['startup_descriptor'],'STARTUP_CONTROL_ADDITIVE_FIXTURE_SPLIT')
    require(len(set(selected))==len(selected),'STARTUP_CONTROL_FIXTURES_MUST_BE_DISTINCT_INSTALLATIONS')
    return raw,value
def initial_fixture(spec):
    require(type(spec['immutable_files']) is dict and spec['immutable_files'] and type(spec['initial_files']) is dict and spec['initial_files'],'STARTUP_CONTROL_COMPLETE_INITIAL_FIXTURE_REQUIRED')
    observations={'files':{},'nodes':{},'absent':[]}
    for group in ('immutable_files','initial_files'):
        for path,expected in spec[group].items():
            require(set(expected)=={'sha256','mode','links'},'STARTUP_CONTROL_INITIAL_FILE_SCHEMA')
            raw=read(path,links=expected['links'])
            require(sha(raw)==expected['sha256'] and oct(stat.S_IMODE(Path(path).stat().st_mode))==expected['mode'],'STARTUP_CONTROL_INITIAL_FIXTURE_CHANGED')
            observations['files'][path]={'sha256':sha(raw),'mode':expected['mode'],'links':expected['links'],'state_kind':group}
    require(type(spec['initial_nodes']) is dict and type(spec['expected_absent']) is list,'STARTUP_CONTROL_NODE_ABSENCE_ROSTER')
    for path,expected in spec['initial_nodes'].items():
        protected(Path(path).parent,directory=True);info=Path(path).lstat()
        actual={'device':info.st_dev,'inode':info.st_ino,'mode':info.st_mode,'links':info.st_nlink,'uid':info.st_uid,'gid':info.st_gid,'link':os.readlink(path) if stat.S_ISLNK(info.st_mode) else None}
        require(actual==expected,'STARTUP_CONTROL_INITIAL_NODE_CHANGED');observations['nodes'][path]=actual
    for path in spec['expected_absent']:
        absolute=Path(path);require(absolute.is_absolute() and str(absolute)==os.path.normpath(absolute),'STARTUP_CONTROL_ABSENT_PATH_SPELLING')
        for parent in reversed(absolute.parents):
            if not os.path.lexists(parent):break
            protected(parent,directory=True)
        require(not os.path.lexists(absolute),'STARTUP_CONTROL_EXPECTED_ABSENCE_CHANGED');observations['absent'].append(path)
    return observations
def execute_case(name,record,out):
    spec=record['cases'][name];before=initial_fixture(spec)
    descriptor=parse(_lease.file(spec['startup_descriptor'],('DATA',)));runtime=descriptor['runtime']
    sys.path[:0]=[str(Path(runtime['worldline_source'])/'runtime'),str(Path(runtime['gate_source']).parent),str(Path(runtime['principal_source']).parent)]
    import worldline.protected_startup as startup
    require(startup.__file__==runtime['worldline_source']+'/runtime/worldline/protected_startup.py','STARTUP_CONTROL_ACTUAL_STARTUP_SOURCE_SPLIT')
    if name in ORIGINAL_CASES:
        method,environment_name=ORIGINAL_CASES[name];os.environ['WORLDLINE_PROTECTED_BOOTSTRAP_CONTROL_'+environment_name]=spec['fixture']
        source=record['control_source'];cls='ProtectedStartupControls'
    else:
        method=ADDITIONAL_CASES[name];os.environ['WORLDLINE_PROTECTED_STARTUP_ADDITIVE_CASE']=spec['fixture']
        source=record['additional_source'];cls='AdditionalStartupControls'
    module=types.ModuleType('worldline_genuine_startup_control');module.__file__=source
    exec(_lease.compile_source(source,'worldline_genuine_startup_control'),module.__dict__)
    result=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName(cls+'.'+method,module))
    passed=result.wasSuccessful() and result.testsRun==1 and not result.skipped and not result.expectedFailures and not result.unexpectedSuccesses
    response={'case':name,'method':method,'status':'PASS' if passed else 'FAIL','testsRun':result.testsRun,'initial_fixture_observation':before,'full_phase_acceptance':False}
    print(json.dumps(response,sort_keys=True));return 0 if passed else 1
def write(path,value):
    with Path(path).open('xb') as stream:stream.write(canonical(value)+b'\n');stream.flush();os.fsync(stream.fileno())
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--campaign',required=True);parser.add_argument('--result-directory',required=True);parser.add_argument('--case',choices=ALL_CASES);args=parser.parse_args()
    raw,record=checked_campaign(args.campaign);out=protected(args.result_directory,directory=True,private=True)
    if args.case is not None:
        try:return execute_case(args.case,record,out)
        finally:
            try:closure=_lease.check();closure['closure_status']='CHECKED_SOURCE_COMPONENT'
            except _approved.Refusal as exc:
                closure=_lease.snapshot();closure['closure_status']='REFUSED';closure['reason']=str(exc);write(out/(args.case+'.executed-code.json'),closure);raise
            write(out/(args.case+'.executed-code.json'),closure)
    # Full genuine required fixture roster is checked before the first target
    # child. Later state-changing controls do not reassert their old initial head.
    for spec in record['cases'].values():initial_fixture(spec)
    records=[];unrun=list(ALL_CASES);failure=None
    try:
        for name in ALL_CASES:
            command=[_lease.interpreter,'-I','-S','-B',_lease.helper_path,'--bootstrap-envelope',_lease.envelope_path,'--entry',__file__,'--campaign',args.campaign,'--result-directory',str(out),'--case',name]
            with (out/(name+'.stdout')).open('xb') as stdout,(out/(name+'.stderr')).open('xb') as stderr:
                child=subprocess.Popen(command,env=dict(record['environment']),stdout=stdout,stderr=stderr);wait=child.wait()
                for stream in (stdout,stderr):stream.flush();os.fsync(stream.fileno())
            row={'case':name,'argv':command,'pid':child.pid,'actual_child_wait':wait,'stdout_sha256':sha(read(out/(name+'.stdout'))),'stderr_sha256':sha(read(out/(name+'.stderr'))),'entry_and_closure_success':False};records.append(row);unrun.remove(name)
            closure_path=out/(name+'.executed-code.json')
            if closure_path.exists():
                closure_raw=read(closure_path);closure=parse(closure_raw);row['executed_code_sha256']=sha(closure_raw)
                require(closure['envelope_bytes_hex']==_lease.envelope.hex() and closure['authority_or_phase_acceptance'] is False,'STARTUP_CONTROL_CHILD_ENVELOPE_SPLIT')
                row['entry_and_closure_success']=wait==0 and closure.get('closure_status')=='CHECKED_SOURCE_COMPONENT'
            require(_lease.file(args.campaign,('DATA',))==raw,'STARTUP_CONTROL_CAMPAIGN_CHANGED');checked_campaign(args.campaign)
            if not row['entry_and_closure_success']:break
    except BaseException as exc:failure={'kind':type(exc).__name__,'reason':str(exc)};raise
    finally:
        summary={'schema':'worldline.protected-startup-campaign-results-v1','campaign_sha256':sha(raw),'records':records,'unrun':unrun,'failure':failure,'all_actual_pass':not unrun and failure is None and all(r['entry_and_closure_success'] for r in records),'all_additional_external_obligations':'OPEN_REQUIRED','full_phase_acceptance':False,'outer_actual_scope_mapping_and_admission':'STILL_REQUIRED'}
        write(out/'result.json',summary);print(json.dumps(summary,sort_keys=True))
    return 0 if summary['all_actual_pass'] else 1
if __name__=='__main__':
    try:raise SystemExit(main())
    except (Refusal,_approved.Refusal) as exc:print(json.dumps({'status':'REFUSED','reason':str(exc),'no_skip_or_acceptance':True}),file=sys.stderr);raise SystemExit(1)
