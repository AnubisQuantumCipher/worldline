#!/usr/bin/env python3
"""Prepared original full-runtime runner. Coordinator/reviewer authorize launch.

The flock holder remains outside the 8G worker and owns only recorded UUID units.
No product test, daemon instrumentation or assertion is modified.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,os,re,signal,subprocess,sys,time,traceback,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OWN=ROOT/'scratch/old-analysis'
LOCK='/home/sicarii/.worldline-heavy.lock'
FRAME=ROOT/'scratch/coordinator/final-frame/source'
FREEZE=ROOT/'records/phase1-blockers/freeze-v1/source.json'
BUILD=ROOT/'records/phase1-blockers/final-build-steps-v1/artifacts.json'
REFERENCE=OWN/'runtime_watcher_reference.py'
REFERENCE_SHA='17a166b36993f030e66306631b234c452886923799b1b972e45652898f7f735f'
AUDIT=OWN/'runtime_audit_entry.py'

def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(path,value):
    temp=path.with_name(path.name+'.partial-'+uuid.uuid4().hex)
    with temp.open('x') as f:json.dump(value,f,sort_keys=True,indent=2,default=str);f.write('\n');f.flush();os.fsync(f.fileno())
    temp.replace(path)
def log(path,value):
    with path.open('a') as f:f.write(json.dumps(value,sort_keys=True,default=str)+'\n');f.flush();os.fsync(f.fileno())
def manager_env():
    values=dict(os.environ);runtime='/run/user/'+str(os.getuid())
    values['XDG_RUNTIME_DIR']=runtime;values['DBUS_SESSION_BUS_ADDRESS']='unix:path='+runtime+'/bus'
    return values

def command(argv,timeout=10):
    try:
        p=subprocess.run(argv,env=manager_env(),capture_output=True,text=True,timeout=timeout)
        return {'argv':argv,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
    except (OSError,subprocess.TimeoutExpired) as e:return {'argv':argv,'exit_code':None,'error':repr(e)}

def reference():
    if sha(REFERENCE)!=REFERENCE_SHA:raise RuntimeError('Reviewed watcher reference changed')
    spec=importlib.util.spec_from_file_location('runtime_watcher_reference',REFERENCE);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def canonical(unit):
    if not re.fullmatch(r'worldline-[0-9a-f-]+\.service',unit):return False
    try:ident=uuid.UUID(unit[len('worldline-'):-len('.service')])
    except ValueError:return False
    return ident.version==4 and unit=='worldline-'+str(ident)+'.service'

def inside(value):
    if not isinstance(value,str) or not value.startswith('/'):return False
    try:return Path(value).resolve().is_relative_to(ROOT)
    except OSError:return False

def owned_exec(entry):
    if inside(entry['executable']):return True
    argv=entry['argv']
    if not argv:return False
    program=Path(argv[0]).name
    if program in ('bwrap','bubblewrap'):
        # Only actual mount SOURCE positions establish attribution. Arbitrary
        # arguments that merely print an owned path are not ownership evidence.
        source_options={'--bind','--ro-bind','--dev-bind','--bind-try','--ro-bind-try','--dev-bind-try'}
        return any(option in source_options and i+2<len(argv) and inside(argv[i+1]) for i,option in enumerate(argv))
    if program.startswith('python'):
        # A real script path after interpreter flags; never interpret -c source.
        for value in argv[1:]:
            if value in ('-c','-m'):return False
            if value.startswith('-'):continue
            return inside(value)
    return False

def units():
    r=command(['systemctl','--user','list-units','--all','--type=service','--no-legend','--plain','--no-pager','--output=json'])
    if r['exit_code']!=0:raise RuntimeError('Cannot read complete user-manager unit roster: '+json.dumps(r))
    values=json.loads(r['stdout'])
    if not isinstance(values,list) or not all(isinstance(x,dict) and isinstance(x.get('unit'),str) for x in values):raise RuntimeError('Unrecognized manager unit roster')
    return {x['unit']:x for x in values},r

def typed_exec(unit):
    base=['busctl','--user','--json=short'];service='org.freedesktop.systemd1'
    lookup=command(base+['call',service,'/org/freedesktop/systemd1','org.freedesktop.systemd1.Manager','GetUnit','s',unit])
    receipt={'lookup':lookup}
    if lookup['exit_code']!=0:return None,receipt
    p=json.loads(lookup['stdout'])
    if p.get('type')!='o' or not isinstance(p.get('data'),list) or len(p['data'])!=1:return None,receipt
    object_path=p['data'][0];fields={}
    for name in ('ExecStart','WorkingDirectory'):
        r=command(base+['get-property',service,object_path,'org.freedesktop.systemd1.Service',name]);receipt[name]=r
        if r['exit_code']!=0:return None,receipt
        fields[name]=json.loads(r['stdout'])
    if fields['ExecStart'].get('type')!='a(sasbttttuii)' or fields['WorkingDirectory'].get('type')!='s':return None,receipt
    rows=fields['ExecStart'].get('data');cwd=fields['WorkingDirectory'].get('data')
    if not isinstance(rows,list) or not all(isinstance(x,list) and len(x)>=2 and isinstance(x[0],str) and isinstance(x[1],list) and all(isinstance(a,str) for a in x[1]) for x in rows):return None,receipt
    return {'execs':[{'executable':x[0],'argv':x[1]} for x in rows],'cwd':cwd},receipt

class RuntimeUnits:
    def __init__(self,out,commit):
        self.out=out;self.commit=commit;self.module=reference();self.initial,self.initial_receipt=units();save(out/'manager-initial.json',self.initial_receipt)
        self.known={};self.intent_rows=[];self.failure=[];self.offsets={};self.exact_matches=[];self.exact_keys=set();self.unattributed=set();self.readonly={}
    def intents(self):
        for path in self.out.rglob('popen.jsonl'):
            if path.is_symlink():continue
            offset=self.offsets.get(str(path),0)
            with path.open('rb') as f:
                f.seek(offset)
                while True:
                    begin=f.tell();line=f.readline()
                    if not line:break
                    if not line.endswith(b'\n'):f.seek(begin);break
                    try:row=json.loads(line)
                    except (ValueError,UnicodeError):self.failure.append('Malformed durable audit receipt');continue
                    if row.get('intent'):
                        row['receipt_path']=str(path);self.intent_rows.append(row)
                self.offsets[str(path)]=f.tell()
    def refresh(self):
        self.intents();current,receipt=units();log(self.out/'manager-rosters.jsonl',receipt)
        wanted={r['intent']['unit'] for r in self.intent_rows if isinstance(r.get('intent'),dict) and canonical(r['intent'].get('unit',''))}
        for unit in sorted(set(current)|wanted):
            if not canonical(unit) or unit in self.initial:continue
            info,raw=typed_exec(unit)
            direct=[r for r in self.intent_rows if r['intent']['unit']==unit]
            basis=None
            if info:
                matches=[r for entry in info['execs'] for r in direct
                         if entry['argv']==r['intent']['exec_argv'] and entry['executable']==r['intent']['exec_argv'][0]]
                if matches:
                    basis='direct root Popen intent with exact typed manager ExecStart executable and argv equality'
                    for receipt in matches:
                        key=(unit,receipt['receipt_path'],receipt['monotonic_ns'])
                        if key not in self.exact_keys:
                            self.exact_keys.add(key)
                            matched={'unit':unit,'receipt':receipt,'typed_manager':raw}
                            self.exact_matches.append(matched);log(self.out/'exact-launch-matches.jsonl',matched)
                elif inside(info['cwd']):basis='exact typed manager WorkingDirectory resolves inside owned worktree'
                elif any(owned_exec(entry) for entry in info['execs']):basis='exact typed manager ExecStart executable, Python script, or bwrap mount source resolves inside owned worktree'
            if unit in self.known:continue
            # A collected direct unit can be recorded without issuing stop. Its
            # exact named cgroup must still be absent/readably empty in observe.
            if not info and direct and unit not in current:basis='direct root Popen intent; manager unit already absent, no attribution by arbitrary new name'
            if basis is None:
                self.unattributed.add(unit)
                log(self.out/'unattributed-observations.jsonl',{'unit':unit,'raw':raw,'action':'read only, never stop; ownership and cleanup UNVERIFIED'})
                if unit not in self.readonly:
                    folder=self.out/'readonly-units'/unit;folder.mkdir(parents=True)
                    observer=self.module.OwnUnitWatcher(folder,self.commit,runner=command)
                    observer.unit=unit;observer.manager_root,_=observer.manager_subtree()
                    # Never admitted: even accidental stop_once() must refuse.
                    self.readonly[unit]=observer
                continue
            folder=self.out/'units'/unit;folder.mkdir(parents=True)
            w=self.module.OwnUnitWatcher(folder,self.commit,runner=command);w.unit=unit;w.manager_root,root_receipt=w.manager_subtree();w.admitted=True;w.intent=None
            save(folder/'attribution.json',{'basis':basis,'unit':unit,'initially_absent':True,'direct_intents':direct,'typed_manager':raw,'root':root_receipt})
            self.known[unit]=w
        for w in self.known.values():w.observe()
        for unit,w in self.readonly.items():
            if unit not in self.known:w.observe()
    def readonly_terminal_observations(self):
        # These observations do not establish ownership or watcher cleanup. An
        # unresolved potentially-own sibling makes the result nonpassing; never
        # stop an unattributed unit merely to obtain a green settlement report.
        return {unit:w.observe() for unit,w in self.readonly.items() if unit not in self.known}
    def settle_all(self):
        # Called only after heavy worker supervisor has returned and verified its
        # own scope dead: no admitted child can issue a late service launch.
        self.refresh()
        while True:
            pending=[]
            for unit,w in self.known.items():
                sample=w.observe()
                if not sample['quiescent']:
                    w.stop_once();pending.append(unit)
            if not pending:return
            log(self.out/'cleanup-pending.jsonl',{'owned_units':pending,'lock':'held'})
            time.sleep(1);self.refresh()

def validate_frame(commit,link=False):
    frozen=json.loads(FREEZE.read_text());build=json.loads(BUILD.read_text())
    if frozen['commit']!=commit or frozen['tracked_dirty'] or build['source_commit']!=commit or not build['source_unchanged']:raise RuntimeError('Frozen frame or completed build identity mismatch')
    if any(not (FRAME/p).is_file() or sha(FRAME/p)!=h for p,h in frozen['source_hashes'].items()):raise RuntimeError('Original frozen source bytes differ')
    root_result=json.loads((ROOT/'records/phase1-blockers/final-build-steps-v1/full-root.json').read_text())
    if root_result['source_commit']!=commit or root_result['exit_code']!=0 or not root_result.get('completed_utc'):raise RuntimeError('Full final build not completed')
    if any(not (ROOT/p).is_file() or sha(ROOT/p)!=h for p,h in build['artifacts'].items()):raise RuntimeError('Built artifacts changed from final receipt')
    if link:
        for name in ('lib','bin','obj'):
            destination=FRAME/name;target=ROOT/name
            if destination.is_symlink():
                if destination.resolve()!=target.resolve():raise RuntimeError('Unexpected existing frame artifact link')
            elif destination.exists():raise RuntimeError('Refuse to replace existing frame artifact directory')
            else:destination.symlink_to(target,target_is_directory=True)
    return {'freeze_sha256':sha(FREEZE),'build_sha256':sha(BUILD),'frame':str(FRAME),'source_commit':commit,'all_original_tracked_hashes_match':True,'artifact_hashes':build['artifacts']}

def worker(args):
    out=args.out;save(out/'frame-before.json',validate_frame(args.expected_commit,link=True))
    env=dict(os.environ)
    # These are deliberate child-process isolation settings, never the host's
    # saved shell configuration or a shell task variable named HOME.
    env.update({'HOME':str(ROOT),'TMPDIR':str(ROOT),'XDG_RUNTIME_DIR':str(ROOT),
      'XDG_CONFIG_HOME':str(out/'xdg-config'),'XDG_DATA_HOME':str(out/'xdg-data'),'XDG_STATE_HOME':str(out/'xdg-state'),'XDG_CACHE_HOME':str(out/'xdg-cache'),
      'DBUS_SESSION_BUS_ADDRESS':manager_env()['DBUS_SESSION_BUS_ADDRESS'],
      'PYTHONPATH':str(FRAME/'runtime')+':'+str(FRAME/'tests'),'PYTHONDONTWRITEBYTECODE':'1','WORLDLINE_PRIVATE_EVALUATOR_TEST':'1',
      'WORLDLINE_CORE_LIB':str(ROOT/'lib/libworldline_core.so'),'GPR_PROJECT_PATH':str(OWN/'private-sparklib-experiment/lib/gnat'),
      'SPARKLIB_MODE':'full','SPARKLIB_BUILD':'Production','SPARKLIB_LIBRARY_TYPE':'static','SPARKLIB_INSTALLED':'True',
      'WORLDLINE_PRIVATE_SPARKLIB_PREBUILT':'True','WORLDLINE_BUILD':'checks'})
    for name in ('xdg-config','xdg-data','xdg-state','xdg-cache'):(out/name).mkdir()
    env.pop('GPR_TOOL',None);env.pop('PYTHONSTARTUP',None)
    save(out/'test-environment.json',{k:env[k] for k in ('HOME','TMPDIR','XDG_RUNTIME_DIR','XDG_CONFIG_HOME','XDG_DATA_HOME','XDG_STATE_HOME','XDG_CACHE_HOME','DBUS_SESSION_BUS_ADDRESS','PYTHONPATH','WORLDLINE_CORE_LIB','GPR_PROJECT_PATH','SPARKLIB_MODE','SPARKLIB_BUILD','SPARKLIB_LIBRARY_TYPE','SPARKLIB_INSTALLED','WORLDLINE_PRIVATE_SPARKLIB_PREBUILT','WORLDLINE_BUILD')})
    sys.path.insert(0,str(FRAME/'scripts'))
    from assurance import parse_unittest,check_private_host_suite
    steps=[]
    if args.suite=='qualification':
        roster=[('qualification-plain','plain',['-v','test_supervision_real']),('qualification-audit','audit',['-v','test_supervision_real'])]
    else:roster=[('python-tests','audit',['discover','-v','-s','tests','-p','test_*.py']),('private-host-tests','audit',['discover','-v','-s','tests','-p','test_private_*.py'])]
    for name,mode,flags in roster:
        directory=out/name;testout=directory/'audit';directory.mkdir()
        argv=['bwrap','--die-with-parent','--ro-bind','/','/','--dev','/dev','--proc','/proc','--bind',str(ROOT),str(ROOT),'--chdir',str(FRAME),sys.executable,'-B',str(AUDIT),'--audit',mode,'--out',str(testout),'--',*flags]
        save(directory/'launch.json',{'argv':argv,'cwd':str(FRAME),'scope':'unchanged original unittest cases'})
        with (directory/'output').open('xb') as stream:p=subprocess.run(argv,cwd=FRAME,env=env,stdout=stream,stderr=subprocess.STDOUT)
        # Original parsers operate over the complete retained ordinary unittest
        # output. Source-only prep does not replace them with a custom pass rule.
        text=(directory/'output').read_text(errors='replace')
        parsed=check_private_host_suite(text) if name=='private-host-tests' else parse_unittest(text)
        audit=json.loads((testout/'audit-result.json').read_text()) if (testout/'audit-result.json').is_file() else None
        ok=p.returncode==0 and parsed['ok'] and parsed['skipped']==0 and audit is not None and not audit['audit_failures']
        step={'name':name,'exit_code':p.returncode,'original_parser':parsed,'audit':audit,'ok':ok,'output_sha256':sha(directory/'output')};save(directory/'result.json',step);steps.append(step)
    qualification = None
    if args.suite=='qualification':
        keys=('ran','ok','failures','errors','skipped','expectedFailures','unexpectedSuccesses')
        parity=all(steps[0]['original_parser'][key]==steps[1]['original_parser'][key] for key in keys)
        audit_path=out/'qualification-audit/audit/popen.jsonl'
        observed=audit_path.is_file() and audit_path.stat().st_size>0
        qualification={'original_parser_parity':parity,'real_top_level_popen_observed':observed,
                       'scope':'paired unchanged real manager supervision module only; no universal instrumentation transparency',
                       'typed_manager_execstart_qualification':'pending outer watcher verification' }
        if not parity or not observed:
            steps[-1]['ok']=False
    after=validate_frame(args.expected_commit)
    save(out/'frame-after.json',after)
    result={'source_commit':args.expected_commit,'suite':args.suite,'steps':steps,'all_original_steps_pass':all(x['ok'] for x in steps),
      'audit_qualification':qualification or 'qualification recorded separately; no universal transparency','native_call_observation':'UNVERIFIED','independent_acceptance':'NOT PERFORMED'}
    save(out/'worker-result.json',result)
    return 0 if result['all_original_steps_pass'] else 1

def base(args,phase,out):return [sys.executable,'-B',str(Path(__file__).resolve()),'--phase',phase,'--out',str(out),'--expected-commit',args.expected_commit,'--suite',args.suite,'--scope-timeout',args.scope_timeout]
def stop_scope(out):
    p=out/'scope/scope.jsonl'
    if p.exists():
        value=json.loads(p.read_text().splitlines()[0]);unit=value.get('unit','')
        if not re.fullmatch(r'wl-phase1-[0-9a-f]{32}\.scope',unit):raise RuntimeError('Malformed own scope')
        log(out/'scope-stops.jsonl',command(['systemctl','--user','stop','--no-block','--',unit]))
def locked(args):
    out=args.out;watch=RuntimeUnits(out,args.expected_commit)
    for name in ('scope','scope/tmp','scope/cache','worker'):(out/name).mkdir()
    cancel={'requested':False}
    for sig in (signal.SIGINT,signal.SIGTERM,signal.SIGHUP):signal.signal(sig,lambda s,f:cancel.update(requested=True))
    argv=[sys.executable,'-B',str(ROOT/'scripts/phase1_heavy.py'),'--phase','locked','--out',str(out/'scope'),'--timeout',args.scope_timeout,'--swap-max','0','--',*base(args,'worker',out/'worker')]
    save(out/'watcher.json',{'argv':argv,'pid':os.getpid(),'shared_lock':LOCK,'outside_worker_scope':True,'reference_sha256':sha(REFERENCE),'audit_sha256':sha(AUDIT),'original_enforcement_none_preserved':True,'aggregate_sibling_cap_equivalence':'NOT CLAIMED'})
    process=None;failure=None
    try:
        with (out/'heavy.stdout').open('xb') as stdout,(out/'heavy.stderr').open('xb') as stderr:
            process=subprocess.Popen(argv,env=manager_env(),stdout=stdout,stderr=stderr)
            while process.poll() is None:
                if (out/'cancel-request.json').exists() or cancel['requested']:stop_scope(out)
                watch.refresh();time.sleep(0.5)
    except BaseException as e:
        failure=repr(e);log(out/'watcher-errors.jsonl',{'error':failure,'traceback':traceback.format_exc()})
    finally:
        # Make all worker/daemon descendants unable to launch more siblings
        # before settlement; no absent service is treated as final while live.
        while process is not None and process.poll() is None:
            stop_scope(out);time.sleep(1)
        if process is not None:
            while True:
                try:watch.settle_all();break
                except BaseException as e:log(out/'cleanup-errors.jsonl',{'error':repr(e),'lock':'retained'});time.sleep(1)
    code=process.returncode if process is not None else 1
    marker=out/'scope/admitted.json';capacity=(code==75 and marker.exists() and json.loads(marker.read_text())=={'admitted':False})
    if (failure or watch.failure or cancel['requested']) and not capacity:code=1
    readonly_terminal=watch.readonly_terminal_observations()
    unresolved=[unit for unit,sample in readonly_terminal.items() if not sample['quiescent']]
    save(out/'readonly-terminal-observations.json',{'observations':readonly_terminal,'unresolved':unresolved,'ownership_and_cleanup':'UNVERIFIED; never stopped'})
    if unresolved and not capacity:code=1
    typed_qualification=None
    if args.suite=='qualification' and not capacity:
        matches=[m for m in watch.exact_matches if '/qualification-audit/audit/popen.jsonl' in m['receipt']['receipt_path']]
        forms={m['receipt']['intent']['launch_form'] for m in matches}
        required={'explicit separator','first positional executable'}
        typed_qualification={'required_launch_forms':sorted(required),'observed_exact_typed_matches':matches,
                             'all_required_launch_forms_matched':required.issubset(forms),
                             'scope':'actual unchanged supervision control; no universal callback transparency'}
        if not typed_qualification['all_required_launch_forms_matched']:code=1
        save(out/'typed-manager-qualification.json',typed_qualification)
    save(out/'locked-result.json',{'exit_code':code,'worker_exit_code':process.returncode if process else None,'failure':failure,
         'audit_failures':watch.failure,'owned_units':list(watch.known),'all_owned_units_quiescent':True,
         'unattributed_new_units':sorted(watch.unattributed-set(watch.known)),'unattributed_cleanup':'UNVERIFIED; read only observations, never stopped',
         'unresolved_potential_siblings':unresolved,'all_possible_siblings_known':'UNVERIFIED',
         'typed_manager_qualification':typed_qualification,'independent_acceptance':'NOT PERFORMED'})
    return code

def outer(args):
    args.out.mkdir(parents=True,exist_ok=False);cancel={'requested':False,'attempt':None}
    def stop(s,f):
        cancel['requested']=True
        if cancel['attempt'] is not None:save(cancel['attempt']/'cancel-request.json',{'signal':s})
    for sig in (signal.SIGINT,signal.SIGTERM,signal.SIGHUP):signal.signal(sig,stop)
    save(args.out/'launch.json',{'argv':sys.argv,'source_commit':args.expected_commit,'driver_sha256':sha(__file__),'audit_sha256':sha(AUDIT),'lock':LOCK,'prepared_only_until_authorized':True})
    while not cancel['requested']:
        attempt=args.out/('attempt-'+uuid.uuid4().hex);attempt.mkdir();cancel['attempt']=attempt
        argv=['flock',LOCK,*base(args,'locked',attempt)];log(args.out/'attempts.jsonl',{'argv':argv})
        code=subprocess.call(argv,env=manager_env());marker=attempt/'scope/admitted.json'
        if code==75 and marker.exists() and json.loads(marker.read_text())=={'admitted':False}:
            log(args.out/'backoff.jsonl',{'lock_released':True,'seconds':300});deadline=time.monotonic()+300
            while time.monotonic()<deadline and not cancel['requested']:time.sleep(1)
            continue
        save(args.out/'result.json',{'exit_code':code,'attempt':str(attempt),'independent_acceptance':'NOT PERFORMED'});return code
    return 1

def main():
    p=argparse.ArgumentParser();p.add_argument('--phase',choices=('outer','locked','worker'),default='outer');p.add_argument('--out',type=Path,required=True);p.add_argument('--expected-commit',required=True);p.add_argument('--suite',choices=('qualification','full'),required=True);p.add_argument('--scope-timeout',required=True);args=p.parse_args();args.out=args.out.resolve()
    if not args.out.is_relative_to(OWN) or not re.fullmatch('[a-f0-9]{40}',args.expected_commit):p.error('Own scratch and exact frozen commit required')
    os.chdir(ROOT)
    return {'outer':outer,'locked':locked,'worker':worker}[args.phase](args)
if __name__=='__main__':raise SystemExit(main())
