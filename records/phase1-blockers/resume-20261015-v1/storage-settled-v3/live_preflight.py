"""Read-only exact-candidate/tool/status preflight; no archive or offload."""
from datetime import datetime,timezone
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[4]
BASE=Path(__file__).resolve().parent
OUT=BASE/'live-preflight'
OUT.mkdir(exist_ok=False)
VAULT=Path('/home/sicarii/Projects/project-vault')
sys.path.insert(0,str(VAULT))
import cold

def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def write(name,value):
    with (OUT/name).open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
def last(path):
    rows=[json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    if not rows:raise RuntimeError('Missing actual terminal rows '+str(path))
    return rows[-1]
selected=[ROOT/'records/phase1-blockers/resume-20261015-v1'/name for name in ('decoder-cursor-v1','decoder-cursor-v2','shared-json-parser-v1','shared-json-parser-v2')]
terminals=[ROOT/'records/phase1-blockers/resume-20261015-v1'/relative for relative in (
    'decoder-cursor-scope-v1/terminal-scope.jsonl','decoder-cursor-scope-v2/terminal-scope.jsonl',
    'shared-json-parser-v1/scope/terminal-scope.jsonl','shared-json-parser-v2/scope/terminal-scope.jsonl',
    'shared-parser-runtime-v1/scope/terminal-scope.jsonl')]
terminal_records=[]
for path in terminals:
    row=last(path)
    if row.get('populated') is not False or row.get('scope_state',{}).get('ActiveState') not in ('inactive','failed'):
        raise RuntimeError('Own selected evidence scope unsettled '+str(path))
    terminal_records.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path),'row':row})
source_before={str(path):sha(path) for path in sorted(VAULT.glob('*.py'))}
config_path=Path('/home/sicarii/.config/project-vault/config.json')
config=json.loads(config_path.read_text());state=Path(config['state'])
pins_path=state/'pinned-paths.json';pins=json.loads(pins_path.read_text())
coordinator=ROOT/'records/phase1-blockers/storage-20261014-v1/coordination.json'
window=json.loads(coordinator.read_text())
if window.get('status')!='reserved' or window.get('owner')!='WORLDLINE Phase1 coordinator astra/phase1-blockers-20261013T165716Z':
    raise RuntimeError('Own storage coordination window not reserved')
commands=[]
for name,argv in [('local-status',[sys.executable,'-B','/home/sicarii/.codex/skills/project-vault/scripts/storage_status.py']),('native-status',['project-vault','status'])]:
    with (OUT/(name+'.stdout')).open('xb') as stdout,(OUT/(name+'.stderr')).open('xb') as stderr:
        actual=subprocess.run(argv,cwd=ROOT,stdout=stdout,stderr=stderr,timeout=60)
    commands.append({'name':name,'argv':argv,'exit_code':actual.returncode,'stdout_sha256':sha(OUT/(name+'.stdout')),'stderr_sha256':sha(OUT/(name+'.stderr'))})
    if actual.returncode!=0:raise RuntimeError('Fresh status command failed '+name)
native=json.loads((OUT/'native-status.stdout').read_text())
local=json.loads((OUT/'local-status.stdout').read_text())
if native.get('mounted') is not True or native.get('initial_archive_transfer_active') is not False:
    raise RuntimeError('Native status is not mounted/initial-transfer-inactive')
if local.get('backup_service',{}).get('exit_status')!=0 or 'ActiveState=inactive' not in local['backup_service']['output']:
    raise RuntimeError('Background backup service status unknown/active')
lock_path=state/'operation.lock'
with lock_path.open('rb') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    fcntl.flock(lock,fcntl.LOCK_UN)
rows=[]
for index,path in enumerate(selected):
    if not path.is_dir() or path.is_symlink() or path.resolve()!=path:raise RuntimeError('Expected real own candidate path')
    overlap=[pin for pin in pins if path==Path(pin) or path.is_relative_to(Path(pin)) or Path(pin).is_relative_to(path)]
    if overlap:raise RuntimeError('Selected path overlaps pin '+str(path))
    active=cold.active_users(path)
    if active:raise RuntimeError('Selected directory active '+str(path))
    inventory=cold.inventory(path)
    inventory_name=str(index)+'.inventory.json'
    write(inventory_name,inventory)
    rows.append({'path':str(path),'inventory_file':inventory_name,'inventory_file_sha256':sha(OUT/inventory_name),
        'content_manifest_sha256':hashlib.sha256(json.dumps(inventory,sort_keys=True).encode()).hexdigest(),
        'active_users':active,'pin_overlaps':overlap,'original_retained':True,'offload':False})
source_after={str(path):sha(path) for path in sorted(VAULT.glob('*.py'))}
if source_before!=source_after:raise RuntimeError('Vault source changed during read-only preflight')
tools={}
for name in ('project-vault','python3','restic'):
    found=shutil.which(name)
    if found is None:raise RuntimeError('Tool missing '+name)
    path=Path(found).resolve();tools[name]={'resolved_path':str(path),'sha256':sha(path)}
receipt={'utc':datetime.now(timezone.utc).isoformat(),'command':sys.orig_argv,'method_sha256':sha(Path(__file__)),
    'selected':rows,'terminals':terminal_records,'commands':commands,'tools_before_archive':tools,'tool_source_before':source_before,'tool_source_after':source_after,
    'tool_source_stable':True,'config_sha256':sha(config_path),'pins_sha256':sha(pins_path),'own_coordination':window,'own_coordination_sha256':sha(coordinator),
    'operation_lock_available_observed':True,'free_bytes':shutil.disk_usage(ROOT).free,
    'native_status_mounted':native['mounted'],'native_initial_transfer_active':native['initial_archive_transfer_active'],'backup_service':local['backup_service'],
    'method_hashes':{name:sha(BASE/name) for name in ('backup_batch.py','run_backup.py')},
    'boundary':'Preflight only, no backup/removal/queue/pin/service change. Lock availability is a momentary observation, not reservation. Native put revalidates mount/device/lock/activity/source/reserve and full recovery; selected candidate backup is not all project/outer evidence coverage. Host catalog/status files private, excluded from publication.'}
write('result.json',receipt)
print(json.dumps({'output':str(OUT/'result.json'),'selected_paths':[str(p) for p in selected],'free_bytes':receipt['free_bytes'],'tool_source_stable':True}))
