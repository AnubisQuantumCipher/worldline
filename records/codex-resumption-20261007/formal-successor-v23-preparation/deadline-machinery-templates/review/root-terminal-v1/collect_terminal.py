"""Root data-only terminal observation and reserved-window release; no target launch."""
from pathlib import Path
import datetime, fcntl, hashlib, json, os, stat, subprocess, tempfile, sys

D = Path(__file__).resolve().parents[2]
R = Path(__file__).resolve().parent
WINDOW = Path('/home/sicarii/Documents/Codex/2026-09-30/how-do-u-feel-about-the/work/worldline-build-proof-window.json')
GOAL = '01a1149d-db62-74b0-a5f7-b0239f285c44'
sys.dont_write_bytecode=True
sys.path.insert(0,str(D))
import authorization
import successor_support
adoption=authorization.check('collect')
independent_review=json.loads(authorization.matched(adoption['independent_review']).read_text())
env = dict(os.environ, XDG_RUNTIME_DIR='/run/user/1000', DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/1000/bus')

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
    p = Path(p); before = p.stat()
    with p.open('rb') as f: value = hashlib.file_digest(f, 'sha256').hexdigest()
    after = p.stat()
    assert (before.st_ino,before.st_size,before.st_mtime_ns,before.st_mode)==(after.st_ino,after.st_size,after.st_mtime_ns,after.st_mode), str(p)
    return value
def pin(p):
    p=Path(p)
    return {'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode)}
def save(name, value):
    p=R/name
    with p.open('x') as f: json.dump(value,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
    return pin(p)
def invoke(argv):
    r=subprocess.run(argv,env=env,capture_output=True,text=True,timeout=30)
    return {'command':argv,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr}

assert not (R/'actual-results-and-window-release.json').exists(), 'terminal observation already retained'
assert sha(D/'inputs.json')==independent_review['inputs_sha256']
assert sha(D/'reviewed-launch-proposal.json')==independent_review['proposal_sha256']
proposal=json.loads((D/'reviewed-launch-proposal.json').read_text())
records=[];unrun=[];unknown=[];children=[];scopes=[];execution_observations=[]
for action in proposal['launches']:
    p=Path(action['receipt'])/'result.json'
    if p.is_file():
        result=json.loads(p.read_text())
        records.append({'mode':action['mode'],'path':str(p),'sha256':sha(p),'actual_result':result})
        wait=result.get('child_wait')
        if wait:
            cp=Path('/proc')/str(wait['pid'])
            children.append({'pid':wait['pid'],'original_exit_evidence':wait,'proc_currently_exists':cp.exists()})
        if not wait or result.get('scope_wait') is None: unknown.append(action['mode'])
    else:
        execution = successor_support.action_execution_observation(action)
        execution_observations.append({'mode': action['mode'], **execution})
        if execution['state'] == 'NEVER_LAUNCHED':
            unrun.append(action['mode'])
        else:
            unknown.append(action['mode'])
        wait = execution['actual_child_wait']
        if wait and wait.get('pid') is not None:
            cp = Path('/proc') / str(wait['pid'])
            children.append({'pid': wait['pid'], 'original_exit_evidence': wait,
                             'proc_currently_exists': cp.exists()})
    row=invoke(['/usr/bin/systemctl','--user','show',action['scope_unit']]+[v for key in ('LoadState','ActiveState','SubState','MainPID','ControlPID','ControlGroup','Result') for v in ('-p',key)])
    row['unit']=action['scope_unit'];props=dict(line.split('=',1) for line in row['stdout'].splitlines() if '=' in line);row['properties']=props
    group=props.get('ControlGroup','')
    cg=Path('/sys/fs/cgroup')/group.lstrip('/') if group else None
    row['cgroup']={'path':str(cg) if cg else None,'exists':cg.exists() if cg else False,'processes':(cg/'cgroup.procs').read_text().split() if cg and (cg/'cgroup.procs').is_file() else None}
    scopes.append(row)
outer_observations=[]
for folder in sorted((D/'review/root-outer-capture-v1').glob('*')):
    if not folder.is_dir(): continue
    started=folder/'outer-child-start.json';ended=folder/'outer-child-wait.json'
    row={'path':str(folder),'start':json.loads(started.read_text()) if started.exists() else None,'wait':json.loads(ended.read_text()) if ended.exists() else None,'refusal':pin(folder/'outer-retention-refusal.json') if (folder/'outer-retention-refusal.json').exists() else None}
    pid=(row['wait'] or row['start'] or {}).get('pid')
    row['pid_observed_nonlive']=pid is not None and not (Path('/proc')/str(pid)).exists()
    wrapper_pid=(row['wait'] or row['start'] or {}).get('wrapper_pid')
    row['wrapper_pid_observed_nonlive']=wrapper_pid is not None and not (Path('/proc')/str(wrapper_pid)).exists()
    outer_observations.append(row)
    if pid is None or not row['pid_observed_nonlive'] or not row['wrapper_pid_observed_nonlive']:
        save('outer-ownership-unresolved.json',{'outer_observations':outer_observations,'release':False})
        raise RuntimeError('outer child ownership unresolved; no release')
    if not row['wait'] or row['wait'].get('actual_handshake_Popen_wait_returncode') is None or row['wait'].get('retention_success') is not True or row['refusal']:
        unknown.append('outer-capture-retention-or-wait')
if records and not outer_observations:
    unknown.append('required-outer-capture-absent')
save('outer-terminal-observations.json',outer_observations)
save('owned-terminal-observations.json',{'at':now(),'scopes':scopes,'known_children':children})
assert all(x['returncode']==0 and x['properties'].get('ActiveState') in ('inactive','failed') and not x['cgroup']['processes'] for x in scopes), 'an owned scope is nonterminal or observation failed; no release inferred'
assert all(not x['proc_currently_exists'] for x in children), 'known child PID exists; actual identity must be resolved before release'

composition=json.loads((D/'source-composition.json').read_text())
allowed=('obj/','lib/','resource-tests/obj/','resource-tests/bin/')
actual={str(p.relative_to(D/'source')):sha(p) for p in sorted((D/'source').rglob('*')) if p.is_file() and not str(p.relative_to(D/'source')).startswith(allowed)}
source_match=actual==composition['source_files'] and all(oct(stat.S_IMODE((D/'source'/rel).stat().st_mode))==mode for rel,mode in composition['source_modes'].items())
private_readback = successor_support.retained_readback(D)
source_match = source_match and private_readback['matches']
save('private-source-dependency-readback.json', private_readback)
save('owned-generated-output-inventory.json', successor_support.generated_outputs(D))
save('complete-source-readback.json',{'actual_files':actual,'declared_source_sha256':sha(D/'source-composition.json'),'exact_keyset_bytes_modes_match':source_match})
live={name:invoke(argv) for name,argv in {
    'proof_lanes':['/usr/bin/systemctl','--user','list-units','--all','--state=active,activating,deactivating','--no-legend','--plain','codex-*proof*'],
    'codex_scopes':['/usr/bin/systemctl','--user','list-units','--all','--state=active,activating,deactivating','--no-legend','--plain','codex-*.scope'],
    'process_sample':['/usr/bin/ps','-eo','pid,comm'],
}.items()}
live['at']=now();live['boundary']='Current observations only; unrelated activity does not prevent giving back an ended owned window and is never stopped.'
save('fresh-terminal-live-sample.json',live)
inventory={}
for base in (D/'source',D/'private-sparklib',D/'evidence',D/'native-artifacts',D/'review/root-live-lane-v1/attempts',D/'review/root-outer-capture-v1'):
    for p in sorted(base.rglob('*')):
        if p.is_file(): inventory[str(p.relative_to(D))]=pin(p)
artifacts=save('retained-artifacts.json',inventory)
passed=source_match and not unrun and not unknown and all(x['actual_result']['child_wait']['returncode']==0 and x['actual_result']['scope_wait']==0 and x['actual_result']['inputs_unchanged'] is True for x in records)
reason=('Standalone full strict formal diagnostic command has actual successful child/scope waits and unchanged inputs. All observed owned scopes/children ended. Window released; complete diagnostic output still requires full original body/caller/native-cost/floor review. No ordinary, architecture or phase acceptance.' if passed else 'Standalone full strict formal diagnostic ended with retained failures/unknowns/unrun. All observed owned scopes/children ended. Window released for source engineering without ordinary/proof/phase acceptance or weakening.')
summary={'schema':'worldline-root-full-strict-formal-diagnostic-terminal-v1','at':now(),'status':'STRICT_DIAGNOSTIC_COMMAND_ACTUAL_WAIT_ZERO_NO_PROOF_ACCEPTANCE' if passed else 'BATCH_TERMINAL_WITH_RETAINED_GAPS_NO_ACCEPTANCE','required_actions':len(proposal['launches']),'all_required_actual_pass':passed,'records':records,'unrun':unrun,'unknown':unknown,'execution_observations':execution_observations,'source_manifest':pin(D/'inputs.json'),'source_exact_keyset_bytes_modes_match':source_match,'owned_scope_terminal_observations':scopes,'known_child_exit_evidence_and_current_pid_absence':children,'fresh_terminal_live_sample':live,'retained_complete_artifacts':artifacts,'all_original_guarantees':'OPEN_UNCHANGED','next_action':('Different-author full actual diagnostic and source/body/reference/caller/native-cost assessment; original floor and sole boundary unchanged. All ordinary and COSMO obligations remain required separately.' if passed else 'Retain every diagnostic failure/unknown and engineer against fixed original scope. This standalone diagnostic authorizes no dependent action or ordinary restart.')}
terminal=save('actual-results-and-window-release.json',summary)
with Path(str(WINDOW)+'.lock').open('a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX)
    prior=pin(WINDOW);coord=json.loads(WINDOW.read_text())
    assert coord['status']=='reserved' and coord['holder_task']==GOAL and coord['candidate']==str(D),'coordination ownership changed; do not overwrite'
    at=now();coord.setdefault('release_history',[]).append({'at':at,'reason':reason,'evidence':terminal})
    coord.update(status='released',released_at=at,updated_at=at,reason=reason,pending_request={'state':'WORLDLINE_FULL_STRICT_FORMAL_DIAGNOSTIC_ENDED_WINDOW_RELEASED'})
    with tempfile.NamedTemporaryFile('w',dir=WINDOW.parent,prefix=WINDOW.name+'.',delete=False) as f:
        json.dump(coord,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno());tmp=Path(f.name)
    os.chmod(tmp,stat.S_IMODE(WINDOW.stat().st_mode));os.replace(tmp,WINDOW)
    fd=os.open(WINDOW.parent,os.O_DIRECTORY);os.fsync(fd);os.close(fd)
    release=save('coordination-release.json',{'at':at,'status':'released','prior':prior,'current':pin(WINDOW),'terminal':terminal,'reason':reason,'notification':'Task-message tool unavailable; watched coordination record updated. No unrelated job stopped.'})
print(json.dumps({'terminal':terminal,'release':release,'actual_all_required_pass':passed,'required_actions':len(proposal['launches']),'unrun':unrun,'unknown':unknown,'formal_or_phase_acceptance':False}))
