"""Freeze and reversibly validate source data; never import target modules."""
from pathlib import Path
import ast, hashlib, json, os, shutil, stat, subprocess, tempfile
T=Path(__file__).resolve().parent
D=T/'physical-completion-integration-main-v3'
S=T/'integrated-candidate-v6/source'
O=T.parent/'phase1-physical-completion-v34-donor'
def pin(p):
    p=Path(p);a=p.lstat();assert stat.S_ISREG(a.st_mode) and not p.is_symlink()
    raw=p.read_bytes();b=p.lstat()
    key=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    assert key(a)==key(b)
    return {'path':str(p),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':b.st_size,'mode':stat.S_IMODE(b.st_mode)}
def save(n,v):
    p=D/n;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:json.dump(v,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.chmod(p,0o644);return pin(p)
delta=json.loads((D/'source-delta.json').read_text())
names=[r['path'] for r in delta]
assert len(names)==len(set(names))
for row in delta:
    n=row['path'];assert pin(D/'source'/n)==row['postimage']
    if row['preimage']:
        assert pin(D/'preimage'/n)==row['preimage']
        assert all(pin(S/n)[k]==row['preimage'][k] for k in ('sha256','bytes','mode'))
    else:assert not (S/n).exists() and not (S/n).is_symlink()
    if row['historical_exact_origin']:
        assert pin(O/'source'/n)==row['historical_exact_origin']
        assert all(row['postimage'][k]==row['historical_exact_origin'][k] for k in ('sha256','bytes','mode'))
    if n.endswith('.py'):ast.parse((D/'source'/n).read_text(),filename=n)
patch_results=[]
with tempfile.TemporaryDirectory(prefix='worldline-inert-physical-delta-') as tmp:
    q=Path(tmp)
    for row in delta:
        if row['preimage']:
            p=q/row['path'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(D/'preimage'/row['path'],p)
    for patch,folder in [('source-forward.patch','source'),('source-inverse.patch','preimage')]:
        run=subprocess.run(['/usr/bin/patch','--batch','--fuzz=0','-p1','-i',str(D/patch)],cwd=q,capture_output=True,text=True)
        patch_results.append({'argv':run.args,'returncode':run.returncode,'stdout':run.stdout,'stderr':run.stderr})
        assert run.returncode==0,patch_results
        expected={r['path'] for r in delta if folder=='source' or r['preimage']}
        actual={str(p.relative_to(q)) for p in q.rglob('*') if p.is_file()}
        assert actual==expected,(actual,expected)
        for n in expected:assert (q/n).read_bytes()==(D/folder/n).read_bytes(),n
save('inert-source-delta-validation.json',{'schema':'worldline-inert-reversible-source-data-check-v1','forward_and_inverse_exact':True,'python_ast_parse':'PASS','patch_results':patch_results,'target_imports':False,'target_execution':False,'phase_acceptance':False})
provenance=Path('/home/sicarii/.codex/sessions/2026/10/10/rollout-2026-10-10T11-18-53-01a12665-43dd-7732-be5f-b7c5bec8be96.jsonl')
latest=None
with provenance.open() as f:
    for line in f:
        r=json.loads(line)
        if r.get('type')=='turn_context':latest=r
assert latest['payload']['model']=='gpt-6.1-sol' and latest['payload']['effort']=='ultra'
save('author-current-turn-model-observation.json',{'schema':'actual-root-turn-model-metadata-observation-v1','source':str(provenance),'observed_event_timestamp':latest.get('timestamp'),'observed_type':latest['type'],'observed_fields':{k:latest['payload'].get(k) for k in ('model','effort','turn_id','cwd')},'provider_fallback_and_speed_fields':'UNOBSERVED_NOT_INVENTED','author_agent':'/root','target_execution':False,'phase_acceptance':False})
save('SOURCE-IDENTITY.json',{'schema':'worldline-source-only-donor-identity-v1','author_agent':'/root','author_model':'openai-codex/gpt-6.1-sol:ultra','actual_author_turn':pin(D/'author-current-turn-model-observation.json'),'source_selection':pin(T/'integrated-candidate-v6/source-selection.json'),'permitted_names':names,'source_inputs':{r['path']:pin(S/r['path']) if r['preimage'] else None for r in delta},'historical_identity':pin(O/'identity.json'),'source_only':True,'target_execution':False,'phase_acceptance':False})
files={str(p.relative_to(D)):pin(p) for p in sorted(D.rglob('*')) if p.is_file()}
files['external-source-preparer']=pin(T/'prepare_original_physical_restoration_main_v3.py')
files['external-source-freezer']=pin(Path(__file__))
save('author-freeze.json',{'schema':'worldline-source-only-donor-author-freeze-v1','author_agent':'/root','author_model':'openai-codex/gpt-6.1-sol:ultra','source_only':True,'target_execution':False,'phase_acceptance':False,'files':files})
packet=save('source-author-packet-v1.json',{'schema':'worldline-source-only-restoration-author-packet-v1','author_agent':'/root','author_model':'openai-codex/gpt-6.1-sol:ultra','actual_author_turn':pin(D/'author-current-turn-model-observation.json'),'author_freeze':pin(D/'author-freeze.json'),'source_identity':pin(D/'SOURCE-IDENTITY.json'),'source_delta':pin(D/'source-delta.json'),'integration_contract':pin(D/'integration-contract-current.json'),'forward_patch':pin(D/'source-forward.patch'),'inverse_patch':pin(D/'source-inverse.patch'),'control_enrollment':pin(D/'historical/control-enrollment.json'),'source_validation':pin(D/'inert-source-delta-validation.json'),'permitted_names':names,'review_destination':str(D/'independent-source-review.json'),'requested_disposition':'QUALIFIED_EXACT_ORIGINAL_PHYSICAL_COMPLETION_GUARDED_RESTORATION_SOURCE_ONLY','source_only':True,'target_execution':False,'phase_acceptance':False,'non_claims':['Original native borrowing, custody, cost, syscall, proof and recovery guarantees remain required and OPEN.','Every original physical source/control body is copied exactly; guarded C_API and additive GPR composition require independent review and actual compilation.','Separate canonical exchange/owner/header/mapping restoration must compose before any complete native acceptance.','No original target bounds, accepted cases, controls, contracts or proof floor weakened.','No installation, policy, protected fixture or actor authorization inferred.']})
print(json.dumps({'packet':packet,'freeze':pin(D/'author-freeze.json'),'source_validation':pin(D/'inert-source-delta-validation.json'),'target_execution':False}))
