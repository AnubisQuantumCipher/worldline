from pathlib import Path
import subprocess,hashlib,json,datetime,sys
root=Path.cwd()
out=root/'scratch/old-analysis/old-inventory-final-v4.json'
assert not out.exists()
def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
freeze=json.loads((root/'records/phase1-blockers/freeze-v5/source.json').read_text())
supplement=root/'scratch/old-analysis/evidence/old-contract-supplement-v1.json'
data=json.loads(supplement.read_text())
native={p:{'sha256':digest(root/p),'matches_reviewed':digest(root/p)==v['sha256'],'matches_frozen':digest(root/p)==freeze['source_hashes'][p]} for p,v in data['native_source_identity'].items()}
imported=[]
for row in data['selected_library_source_identity']:
    for name,entry in [('installed',row['installed']),*row['private_copies'].items()]:
        imported.append({'role':name,'path':entry['path'],'sha256':digest(Path(entry['path'])),'matches_reviewed':digest(Path(entry['path']))==entry['sha256']})
versions=[]
for command in [['gnatprove','--version'],['gnatls','--version'],['gprbuild','--version']]:
    p=subprocess.run(command,capture_output=True,text=True)
    versions.append({'argv':command,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
command=data['donor_roster']['command_result']['argv']; p=subprocess.run(command,capture_output=True,text=True)
current=dict(line.split() for line in p.stdout.splitlines())
refs=['records/phase1-blockers/old-contract-inventory-v2.json','records/phase1-blockers/old-contract-inventory-v3.json',str(supplement.relative_to(root))]
result={'classification':'MEASURED','claim':'reviewed scoped contract, implicit temporary and imported copy/finalization inventory joined to final source; no proof or retirement claim',
 'source_commit':freeze['commit'],'current_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
 'command':['bash','-c','source /home/sicarii/opt/gnat/env.sh; python3 -B scratch/old-analysis/final_old_inventory_v4.py'],
 'cwd':str(root),'started_utc':start,'ended_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'references':[{'path':p,'sha256':digest(root/p)} for p in refs], 'native':native,'imported':imported,'tool_versions':versions,
 'donors':{'argv':command,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'matches_reviewed_nonempty':bool(current) and current==data['donor_roster']['reviewed']},
 'original_guarantee':'FAILED-OPEN','narrowed_claims':[]}
result['inventory_identity_complete']=(result['source_commit']==result['current_commit'] and all(v['matches_reviewed'] and v['matches_frozen'] for v in native.values()) and all(v['matches_reviewed'] for v in imported) and all(v['exit_code']==0 for v in versions) and result['donors']['matches_reviewed_nonempty'])
out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'inventory_identity_complete':result['inventory_identity_complete'],'path':str(out),'sha256':digest(out)}))
sys.exit(0 if result['inventory_identity_complete'] else 1)
