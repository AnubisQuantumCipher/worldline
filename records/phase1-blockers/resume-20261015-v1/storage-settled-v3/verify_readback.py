"""Read selected persisted recovery receipts and regenerate native inventories.

No restore/backup/offload/removal/config or service mutation is performed.
"""
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[4]
BASE=Path(__file__).resolve().parent
OUT=BASE/'readback-data'
OUT.mkdir(exist_ok=False)
def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def write(name,value):
    with (OUT/name).open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
def last(path):
    rows=[json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    if not rows:raise RuntimeError('Missing raw receipt '+str(path))
    return rows[-1]
pre_path=BASE/'live-preflight/result.json';pre=json.loads(pre_path.read_text())
sources_now={path:sha(Path(path)) for path in pre['tool_source_before']}
if sources_now!=pre['tool_source_before']:raise RuntimeError('Vault tool source changed before readback')
sys.path.insert(0,'/home/sicarii/Projects/project-vault')
import cold
config_path=Path('/home/sicarii/.config/project-vault/config.json')
if sha(config_path)!=pre['config_sha256']:raise RuntimeError('Vault config changed')
config=json.loads(config_path.read_text());state=Path(config['state'])
parent_path=BASE/'parent/result.json';parent=json.loads(parent_path.read_text())
batch_path=BASE/'backup-results/batch-result.json';batch=json.loads(batch_path.read_text())
terminal_path=BASE/'scope/terminal-scope.jsonl';terminal=last(terminal_path)
if parent.get('exit_code')!=0 or parent.get('tracked_sources_unchanged') is not True:
    raise RuntimeError('Original backup parent failed or tracked source changed')
if terminal.get('populated') is not False or terminal.get('scope_state',{}).get('ActiveState') not in ('inactive','failed'):
    raise RuntimeError('Original owned backup scope unsettled')
if batch.get('complete') is not True or batch.get('offload') is not False:
    raise RuntimeError('Original complete backup-only batch receipt absent')
if [row['path'] for row in batch['results']]!=[row['path'] for row in pre['selected']]:
    raise RuntimeError('Exact selected path roster differs')
rows=[]
for index,selection in enumerate(pre['selected']):
    path=Path(selection['path']);result_path=BASE/'backup-results'/(str(index)+'.result.json')
    result=json.loads(result_path.read_text())
    if result.get('exit_code')!=0 or result.get('offload') is not False or result.get('path')!=str(path) or result!=batch['results'][index]:
        raise RuntimeError('Original per-item command or batch join failed')
    stdout_path=Path(result['stdout']);stderr_path=Path(result['stderr']);stdout=stdout_path.read_text()
    start=stdout.rfind('\n{')
    if start<0:raise RuntimeError('Missing final native CLI item JSON')
    item=json.loads(stdout[start+1:])
    if item.get('path')!=str(path) or item.get('state')!='backed-up-local' or item.get('verification')!='full candidate restore, SHA256 and metadata comparison':
        raise RuntimeError('Native item does not establish selected full recovery comparison')
    local_item_path=state/'items'/(item['id']+'.json')
    remote_item_path=Path(config['root'])/'Recovery/items'/(item['id']+'.json')
    local_item=json.loads(local_item_path.read_text());remote_item=json.loads(remote_item_path.read_text())
    if local_item!=item or remote_item!=item:raise RuntimeError('Persisted local/iPad item differs from actual CLI result')
    job_path=state/'cold-jobs'/hashlib.sha256(str(path).encode()).hexdigest()/'job.json'
    job=json.loads(job_path.read_text())
    if job.get('id')!=item['id'] or job.get('path')!=str(path) or job.get('snapshot')!=item['snapshot'] or job.get('complete') is not True:
        raise RuntimeError('Exact persisted job/snapshot/complete join failed')
    inventory=cold.inventory(path);manifest=hashlib.sha256(json.dumps(inventory,sort_keys=True).encode()).hexdigest()
    original_inventory=json.loads((BASE/'live-preflight'/selection['inventory_file']).read_text())
    if inventory!=original_inventory or manifest!=selection['content_manifest_sha256'] or manifest!=job.get('manifest') or manifest!=item['content_manifest_sha256']:
        raise RuntimeError('Preflight/fresh original/job/item content or metadata manifest differs')
    write(str(index)+'.fresh-inventory.json',inventory)
    write(str(index)+'.persisted-item.json',local_item)
    write(str(index)+'.persisted-job.json',job)
    rows.append({'path':str(path),'item_id':item['id'],'snapshot':item['snapshot'],'bytes':item['bytes'],
        'verification':item['verification'],'content_manifest_sha256':manifest,'per_item_result_sha256':sha(result_path),
        'stdout_sha256':sha(stdout_path),'stderr_sha256':sha(stderr_path),'persisted_local_item_sha256':sha(local_item_path),'persisted_ipad_item_sha256':sha(remote_item_path),
        'persisted_job_sha256':sha(job_path),'fresh_inventory_sha256':sha(OUT/(str(index)+'.fresh-inventory.json')),
        'local_and_ipad_item_equal_cli':True,'job_snapshot_complete_matches':True,'preflight_fresh_original_manifest_matches':True,
        'local_original_retained':path.is_dir(),'offload':False})
sources_after={path:sha(Path(path)) for path in pre['tool_source_before']}
if sources_after!=sources_now:raise RuntimeError('Vault tool source changed during readback')
live=last(BASE/'scope/cgroup.jsonl')
receipt={'utc':datetime.now(timezone.utc).isoformat(),'command':sys.orig_argv,'method_sha256':sha(Path(__file__)),
    'classification':'TESTED native full candidate recoveries reported by actual CLI; MEASURED exact persisted local/iPad item/job/snapshot/manifest and freshly unchanged local inventory correspondence',
    'rows':rows,'preflight_sha256':sha(pre_path),'parent_sha256':sha(parent_path),'batch_sha256':sha(batch_path),'parent_exit':parent['exit_code'],
    'tracked_sources_unchanged':parent['tracked_sources_unchanged'],'terminal_scope_sha256':sha(terminal_path),'terminal_scope':terminal,
    'last_live_cgroup_sample':live,'vault_source_before':sources_now,'vault_source_after':sources_after,'vault_source_stable':True,
    'free_bytes':shutil.disk_usage(ROOT).free,'limitations':['Exact selected candidate backup only; outer carrier/research/project evidence not all covered.',
        'No new full restore is executed by this readback; the original actual native put ran full restore and byte/metadata comparison before persisted item creation.',
        'No repository-wide scrub, original rebuild recipe/toolchain qualification, capacity reclamation, original removal or independent acceptance claim.',
        'Original D63 documentary parent digest transcription error remains separately retained and corrected; actual preflight/review/launch/file hashes agree.']}
with (BASE/'verified-backup-readback.json').open('x') as stream:json.dump(receipt,stream,indent=2);stream.write('\n')
print(json.dumps({'output':str(BASE/'verified-backup-readback.json'),'verified_selected_paths':[row['path'] for row in rows],'free_bytes':receipt['free_bytes']}))
