"""UNEXECUTED conditional preparation; never repeats an already executed main.

This independently records literal execution if D62's whole carrier ended
before its runtime phases. It does not rerun, continue or replace proof.
"""
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parent
CANDIDATE = ROOT / 'records/phase1-blockers/resume-20261015-v1/shared-json-parser-v2'
OUT = BASE / 'results'

def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

driver_path = CANDIDATE / 'run_shared_parser.py'
if digest(driver_path) != '2f1424a4fbccff57b599777960e54b0f409f845ef9c134db1f3bd46499290a50':
    raise SystemExit('Original checked candidate driver changed')
spec = importlib.util.spec_from_file_location('d62_checked_identity', driver_path)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
parent_path = CANDIDATE / 'parent/result.json'
parent = json.loads(parent_path.read_text())
if not parent.get('own_scope_terminal') or not all(parent.get(key) for key in ('candidate_unchanged','private_unchanged','tracked_unchanged')):
    raise SystemExit('D62 source/post/own-scope settlement not established')
for before,after in (('candidate_before','candidate_after'),('private_before','private_after'),('tracked_before','tracked_after')):
    if parent.get(before) is None or parent.get(before) != parent.get(after):
        raise SystemExit('D62 actual before/after map absent or inconsistent')
for filename,key in (('source-before.json','tracked_before'),('source-after.json','tracked_after')):
    if json.loads((CANDIDATE/'parent'/filename).read_text()) != parent[key]:
        raise SystemExit('D62 raw tracked-map file differs from parent receipt')
terminal_path = CANDIDATE/'scope/terminal-scope.jsonl'
terminal_rows = [json.loads(line) for line in terminal_path.read_text().splitlines() if line.strip()]
if not terminal_rows or terminal_rows[-1] != parent.get('terminal_scope'):
    raise SystemExit('D62 raw scope settlement differs from parent receipt')
terminal = terminal_rows[-1]
if terminal.get('populated') is not False or terminal.get('scope_state',{}).get('ActiveState') not in ('inactive','failed'):
    raise SystemExit('D62 own scope remains unestablished')
worker_path = CANDIDATE/'scope/worker-result.json'
worker = json.loads(worker_path.read_text())
scope_result_path = CANDIDATE/'scope/result.jsonl'
scope_results = [json.loads(line) for line in scope_result_path.read_text().splitlines() if line.strip()]
if not scope_results or worker.get('exit_code') is None or worker.get('exit_code') != parent.get('heavy_exit') or scope_results[-1].get('exit_code') != parent.get('heavy_exit'):
    raise SystemExit('Original actual worker/heavy/parent exit join absent or inconsistent')
driver_result = parent.get('driver_result')
actual_driver_path = CANDIDATE/'results/result.json'
if driver_result is not None:
    if str(actual_driver_path) != driver_result.get('path') or digest(actual_driver_path) != driver_result.get('sha256') or json.loads(actual_driver_path.read_text()) != driver_result.get('value'):
        raise SystemExit('D62 original driver-result file differs from parent')
    previous = driver_result['value'].get('runtime_exits', {})
    if any(previous.get(name) is not None for name in driver.MAINS):
        raise SystemExit('Original runtime already attempted; no repeat selected')
elif actual_driver_path.exists():
    raise SystemExit('Unexpected original driver result not bound by parent')
event_path = CANDIDATE/'results/events.jsonl'
events = [json.loads(line) for line in event_path.read_text().splitlines() if line.strip()]
if not events or any(not isinstance(row,dict) for row in events):
    raise SystemExit('Missing/malformed original phase history cannot establish never attempted')
if not any(row.get('event')=='phase_finished' and row.get('name')=='build' and row.get('exit_code')==0 for row in events):
    raise SystemExit('Original successful build-finished event absent')
for name in driver.MAINS:
    if any(row.get('name')==name for row in events):
        raise SystemExit('Original runtime phase event exists; no repeat selected')
    for suffix in ('.result.json','.stdout','.stderr'):
        if (CANDIDATE / ('results/' + name + suffix)).exists():
            raise SystemExit('Original runtime partial/result artifact exists; no repeat selected')
build_path = CANDIDATE / 'results/build.result.json'
build = json.loads(build_path.read_text())
if build.get('exit_code') != 0:
    raise SystemExit('No successful original complete candidate build')
if not any(row.get('event')=='phase_finished' and all(row.get(key)==value for key,value in build.items()) for row in events):
    raise SystemExit('Successful build phase event differs from raw build result')
original_launch_path = CANDIDATE/'results/launch.json'
original_launch = json.loads(original_launch_path.read_text())
bwrap_tool = original_launch['tools']['bwrap']
selected_bwrap = shutil.which('bwrap')
if selected_bwrap is None or str(Path(selected_bwrap).resolve()) != bwrap_tool['path'] or digest(Path(selected_bwrap).resolve()) != bwrap_tool['sha256']:
    raise SystemExit('Actual runtime carrier tool differs from original recorded tool')
if subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip() != driver.EPOCH:
    raise SystemExit('Changed source epoch requires separate reviewed binding')
driver.verify_bundle(CANDIDATE)
candidate_before = driver.candidate_identity(CANDIDATE)
if candidate_before != parent['candidate_after']:
    raise SystemExit('Actual candidate changed after original build/proof carrier')
private_before = driver.private_identity(CANDIDATE)
if private_before != parent['private_after']:
    raise SystemExit('Actual private dependency changed after original carrier')
if os.environ.get('PYTHONOPTIMIZE') not in (None,'','0'):
    raise SystemExit('Optimized-away driver checks refused')
cgroup_before = driver.cgroup_identity()
if cgroup_before['memory.max'] != '8589934592' or cgroup_before['memory.swap.max'] != '0':
    raise SystemExit('Actual runtime scope cap differs')
watched = {}
for name in driver.MAINS:
    binary = CANDIDATE / 'bin-current-D56' / name
    ali = CANDIDATE / 'obj-current-D56' / (name + '.ali')
    for path in (binary,ali):
        driver.no_symlink(path)
        if not path.is_file():
            raise SystemExit('Missing regular original build artifact: ' + str(path))
        watched[str(path.relative_to(ROOT))] = digest(path)
    if 'A -gnata' not in ali.read_text().splitlines():
        raise SystemExit('Original main assertions not enabled')
driver.no_symlink(OUT)
OUT.mkdir(exist_ok=False)
for name in ('tmp','cache'):
    (OUT/name).mkdir()
env = dict(os.environ)
env.update(PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1', TMPDIR=str(OUT/'tmp'), XDG_CACHE_HOME=str(OUT/'cache'))
env.pop('LD_PRELOAD',None)
receipt = {'started_utc':driver.stamp(),'source_epoch':driver.EPOCH,'method_sha256':digest(Path(__file__)),
    'candidate_driver_sha256':digest(driver_path),'original_parent_sha256':digest(parent_path),'original_build_sha256':digest(build_path),
    'original_terminal_scope_sha256':digest(terminal_path),'original_phase_history_sha256':digest(event_path),
    'original_worker_result_sha256':digest(worker_path),'original_scope_result_sha256':digest(scope_result_path),'original_launch_sha256':digest(original_launch_path),'original_worker_result':worker,'runtime_carrier_tool':bwrap_tool,
    'candidate_before':candidate_before,'private_before':private_before,'cgroup_before':cgroup_before,'artifacts_before':watched,
    'artifact_observation_boundary':'These are later retained-artifact hashes measured now, not historical build-end pins. The original build receipt has no build-end binary hashes; original successful build/fresh destinations/unchanged source and exact controlled methods provide the separate construction provenance.',
    'python':{'path':sys.executable,'sha256':digest(Path(sys.executable).resolve()),'version':sys.version},
    'environment':{key:env.get(key) for key in ('PATH','LANG','LC_ALL','TMPDIR','XDG_CACHE_HOME','LD_LIBRARY_PATH','LD_PRELOAD','PYTHONOPTIMIZE','PYTHONNOUSERSITE')},
    'steps':[], 'boundary':'Both original assertion-enabled finite candidate mains only. No proof rerun/completion or semantic/full-production/acceptance promotion. D62 failures remain retained.'}
driver.write_json(OUT/'launch.json',receipt)
for name in driver.MAINS:
    payload=[str(CANDIDATE/'bin-current-D56'/name)]
    command=[bwrap_tool['path'],'--die-with-parent','--unshare-pid','--ro-bind','/','/','--dev','/dev','--proc','/proc',
        '--bind',str(OUT),str(OUT),'--bind',str(OUT/'tmp'),'/tmp','--chdir',str(CANDIDATE),*payload]
    row={'name':name,'started_utc':driver.stamp(),'cwd':str(CANDIDATE),'argv':command,'payload_argv':payload}
    driver.event(OUT/'events.jsonl',{'event':'phase_started',**row})
    with (OUT/(name+'.stdout')).open('xb') as stdout, (OUT/(name+'.stderr')).open('xb') as stderr:
        actual=subprocess.run(command,cwd=CANDIDATE,env=env,stdout=stdout,stderr=stderr)
    row.update(ended_utc=driver.stamp(),exit_code=actual.returncode,stdout_sha256=digest(OUT/(name+'.stdout')),stderr_sha256=digest(OUT/(name+'.stderr')))
    receipt['steps'].append(row)
    driver.event(OUT/'events.jsonl',{'event':'phase_finished',**row})
    driver.write_json(OUT/(name+'.result.json'),row)
receipt.update(ended_utc=driver.stamp(),candidate_after=driver.candidate_identity(CANDIDATE),private_after=driver.private_identity(CANDIDATE),
    artifacts_after={relative:digest(ROOT/relative) for relative in watched},cgroup_after=driver.cgroup_identity())
receipt['validation_passed']=(all(row['exit_code']==0 for row in receipt['steps']) and receipt['candidate_after']==candidate_before
    and receipt['private_after']==private_before and receipt['artifacts_after']==watched)
driver.write_json(OUT/'result.json',receipt)
print(json.dumps({'output':str(OUT/'result.json'),'validation_passed':receipt['validation_passed']}))
raise SystemExit(0 if receipt['validation_passed'] else 1)
