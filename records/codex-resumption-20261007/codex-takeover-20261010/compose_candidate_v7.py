"""Compose exact independently reviewed restoration donors into new source data."""
from pathlib import Path
import argparse, ast, hashlib, json, os, shutil, stat, subprocess
T=Path(__file__).resolve().parent
P=T/'integrated-candidate-v6'
C=T/'integrated-candidate-v7'
F=T.parent/'phase1-integrated-v67-draft'
def pin(p):
    p=Path(p);a=p.lstat();assert stat.S_ISREG(a.st_mode) and not p.is_symlink()
    raw=p.read_bytes();b=p.lstat()
    key=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    assert key(a)==key(b)
    return {'path':str(p),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':b.st_size,'mode':stat.S_IMODE(b.st_mode)}
def load(p):return json.loads(Path(p).read_text())
def save(p,v):
    with Path(p).open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
def snapshot(root):
    r={}
    for p in [root,*sorted(root.rglob('*'))]:
        s=p.lstat();assert not p.is_symlink()
        assert stat.S_ISREG(s.st_mode) or stat.S_ISDIR(s.st_mode)
        row={'kind':'directory' if p.is_dir() else 'file','mode':stat.S_IMODE(s.st_mode)}
        if row['kind']=='file':row.update({k:v for k,v in pin(p).items() if k in ('sha256','bytes')})
        r[str(p.relative_to(root))]=row
    return r
def donor(d,disposition):
    d=Path(d).resolve(strict=True)
    packet_path=d/('source-author-packet-v2.json' if (d/'source-author-packet-v2.json').exists() else 'source-author-packet-v1.json')
    packet=load(packet_path)
    review_path=d/('independent-source-review-v2.json' if packet_path.name=='source-author-packet-v2.json' else 'independent-source-review.json')
    review=load(review_path)
    assert review['disposition']==disposition
    assert review['reviewer_agent']=='/root/acceptance_ultra'
    assert pin(Path(review['model_provenance']['path']))==review['model_provenance']
    for name in ('author_freeze','source_identity'):
        row=packet[name];assert pin(Path(row['path']))==row
    for name in ('source_delta','exact_transformations'):
        if name in packet:
            row=packet[name];assert pin(Path(row['path']))==row
    freeze=load(packet['author_freeze']['path'])
    for row in freeze['files'].values():assert pin(Path(row['path']))==row
    names=packet['permitted_names']
    for n in names:
        post=d/'source'/n;assert post.is_file() and not post.is_symlink()
        pres=[d/'preimage'/n,d/'preimages'/n];pre=next((p for p in pres if p.exists()),None)
        if pre:assert all(pin(pre)[k]==pin(P/'source'/n)[k] for k in ('sha256','bytes','mode')),n
        else:assert not (P/'source'/n).exists(),n
    return d,packet,review,{'packet':pin(packet_path),'review':pin(review_path),'files':names}
def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--progress-donor',type=Path,required=True)
    a.add_argument('--enrollment-donor',type=Path,required=True)
    args=a.parse_args()
    assert __debug__ and not C.exists()
    before=snapshot(P/'source');assert before==load(P/'stable-source-inventory.json')
    ph,pp,pr,phrow=donor(T/'physical-completion-integration-main-v3','QUALIFIED_EXACT_ORIGINAL_PHYSICAL_COMPLETION_GUARDED_RESTORATION_SOURCE_ONLY')
    ca,cp,cr,carow=donor(T/'canonical-exchange-owner-abi-donor-ultra-v1','QUALIFIED_EXACT_ORIGINAL_EXCHANGE_OWNER_ABI_MAPPING_CONTROLS_RESTORATION_SOURCE_ONLY')
    le,lp,lr,lerow=donor(T/'excluded-owner-function-termination-legality-ultra-v1','QUALIFIED_EXACT_EXCLUDED_OWNER_FUNCTION_TERMINATION_LEGALITY_SOURCE_ONLY')
    pg,gp,gr,pgrow=donor(args.progress_donor,'QUALIFIED_EXACT_EXCLUDED_OWNER_LOOP_PROGRESS_ANNOTATION_SOURCE_ONLY')
    en,ep,er,enrow=donor(args.enrollment_donor,'QUALIFIED_EXACT_ADDITIVE_ORIGINAL_PHYSICAL_PROOF_ENROLLMENT_SOURCE_ONLY')
    allrows=[phrow,carow,lerow,pgrow,enrow]
    overlap=set(pp['permitted_names'])&set(cp['permitted_names'])
    assert overlap=={'core/worldline-c_api.ads','core/worldline-c_api.adb'}
    seen=set()
    for packet in (pp,cp,lp,gp,ep):
        for n in packet['permitted_names']:
            if n in seen:assert n in overlap,n
            seen.add(n)
    shutil.copytree(P/'source',C/'source')
    assert snapshot(C/'source')==before
    for d,packet in ((ph,pp),(ca,cp),(le,lp),(pg,gp),(en,ep)):
        for n in packet['permitted_names']:
            if n in overlap:continue
            target=C/'source'/n;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(d/'source'/n,target)
            assert all(pin(target)[k]==pin(d/'source'/n)[k] for k in ('sha256','bytes','mode'))
    for suffix in ('ads','adb'):
        n='core/worldline-c_api.'+suffix
        original=(P/'source'/n).read_text()
        canonical=(ca/'source'/n).read_text()
        physical=(ph/('integration/physical-current-c-api.'+suffix+'.inc')).read_text()
        needle='end Worldline.C_API;';assert canonical.count(needle)==1
        merged=canonical.replace(needle,physical+'\n'+needle,1)
        if suffix=='adb':
            context='with Worldline.Actuation_Full_Wire;\n'
            assert context not in canonical;merged=context+merged
            assert merged[len(context):].replace(physical+'\n','',1)==canonical
        else:assert merged.replace(physical+'\n','',1)==canonical
        target=C/'source'/n;target.write_text(merged)
        assert pin(P/'source'/n)['sha256']==hashlib.sha256(original.encode()).hexdigest()
    # Source data hashing only; unchanged AST-selected normalizer, no module import.
    for mode,report in [('write','pin-refresh-source-observation.json'),('check','pin-check-source-observation.json')]:
        argv=['/usr/bin/python3','-B',str(C/'source/refresh_contract_pins.py'),'--'+mode,'--root',str(C/'source'),'--report',str(C/report)]
        r=subprocess.run(argv,capture_output=True)
        (C/('pin-'+mode+'.stdout')).write_bytes(r.stdout);(C/('pin-'+mode+'.stderr')).write_bytes(r.stderr)
        save(C/('pin-'+mode+'-command.json'),{'argv':argv,'returncode':r.returncode,'target_execution':False})
        assert r.returncode==0
    registration=C/'source/protected-root/controls/source_registration.json'
    reg=load(registration);mapping=reg['fixed_excluded_source_owner']['affected_source_sha256']
    changes={n:{'before':old,'after':pin(C/'source'/n)['sha256']} for n,old in mapping.items() if old!=pin(C/'source'/n)['sha256']}
    assert set(changes)<=seen|{'runtime/worldline/proof_manifest.py'}
    for n,row in changes.items():mapping[n]=row['after']
    reg['codex_original_physical_canonical_termination_restoration_binding']={'source_only':True,'preimage_registration':pin(P/'source/protected-root/controls/source_registration.json'),'changes':changes,'reviewed_donors':allrows,'original_control_enrollments':[pp['control_enrollment'],cp['control_enrollment']],'proof_runtime_or_phase_acceptance':False,'actual_operator_policy_recovery_symbol_selection':None}
    registration.write_text(json.dumps(reg,indent=2)+'\n')
    after=snapshot(C/'source')
    changed={n for n in set(before)|set(after) if before.get(n)!=after.get(n)}
    allowed=seen|{'runtime/worldline/proof_manifest.py','protected-root/controls/source_registration.json'}
    assert all(n in allowed or (after.get(n,{}).get('kind')=='directory' and n not in before) for n in changed)
    for n in seen:
        if n.endswith('.py'):ast.parse((C/'source'/n).read_text(),filename=n)
    assert (C/'source/runtime/worldline/canonical_k4_recovery.py').read_bytes()==(P/'source/runtime/worldline/canonical_k4_recovery.py').read_bytes()
    base=load(F/'stable-source-inventory.json')
    delta=[{'path':n,'before':base.get(n),'after':after.get(n)} for n in sorted(set(base)|set(after)) if base.get(n)!=after.get(n)]
    direct=[{'path':n,'before':before.get(n),'after':after.get(n)} for n in sorted(changed)]
    save(C/'stable-source-inventory.json',after)
    save(C/'source-inventory.json',{n:{k:v for k,v in row.items() if k!='bytes'} for n,row in after.items()})
    save(C/'source-changes.json',delta);save(C/'source6-to-source7-delta.json',direct)
    save(C/'restoration-integration.json',{'schema':'worldline-original-physical-canonical-termination-coherent-source-composition-v1','reviewed_donors':allrows,'predecessor_selection':pin(P/'source-selection.json'),'complete_direct_delta':pin(C/'source6-to-source7-delta.json'),'current_registration_changes':changes,'preimage_registration':pin(P/'source/protected-root/controls/source_registration.json'),'postimage_registration':pin(registration),'c_api_composition':'Canonical reviewed postimage plus exact reviewed physical insertion and its single import, preserving all current preimage bytes outside separately reviewed insertions.','target_execution':False,'phase_acceptance':False})
    selection=load(P/'source-selection.json')
    for n in ('source_only_enrollment','enrollment_collection_invocation','enrollment_source_delta','complete_original_f67_to_current_delta','compile_repair_integration','registration_binding_change','proof_manifest_change'):
        selection.pop(n,None)
    selection.update(source=str(C/'source'),source_inventory=pin(C/'source-inventory.json'),stable_source_inventory=pin(C/'stable-source-inventory.json'),source_changes=pin(C/'source-changes.json'),restoration_integration=pin(C/'restoration-integration.json'),preserved_missing_original_join_candidate=pin(P/'source-selection.json'),registration_binding_change=pin(C/'restoration-integration.json'),pin_check_source_observation=pin(C/'pin-check-source-observation.json'),all_literal_pin_check=pin(C/'pin-check-source-observation.json'),pin_refresh_source_observation=pin(C/'pin-refresh-source-observation.json'),all_literal_pin_refresh=pin(C/'pin-refresh-source-observation.json'),reviews='Exact donor source-only opinions preserved; complete composed source and added original proof/control domains require independent review and original matching-source execution.',proof_acceptance=False,runtime_acceptance=False,phase_acceptance=False)
    save(C/'source-selection.json',selection)
    assert snapshot(P/'source')==before
    for row in allrows:
        assert pin(Path(row['packet']['path']))==row['packet'] and pin(Path(row['review']['path']))==row['review']
    print(json.dumps({'selection':pin(C/'source-selection.json'),'direct_delta':pin(C/'source6-to-source7-delta.json'),'changed_paths':sorted(changed),'target_execution':False,'phase_acceptance':False}))
if __name__=='__main__':main()
