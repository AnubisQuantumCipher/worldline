"""Compose the exact qualified compiler debug-cost donor as new source data."""
from pathlib import Path
import hashlib, json, os, shutil, stat, subprocess

T=Path(__file__).resolve().parent
P=T/'integrated-candidate-v7'
C=T/'integrated-candidate-v8'
D=T/'compiler-debug-tracking-cost-donor-ultra-v1'
NAME='core/worldline_core_sources.gpr'

def load(p): return json.loads(Path(p).read_text())
def pin(p):
    p=Path(p); a=p.lstat()
    assert stat.S_ISREG(a.st_mode) and not p.is_symlink()
    data=p.read_bytes(); b=p.lstat()
    key=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    assert key(a)==key(b)
    return {'path':str(p),'sha256':hashlib.sha256(data).hexdigest(),'bytes':b.st_size,'mode':stat.S_IMODE(b.st_mode)}
def save(p,v):
    with Path(p).open('x') as f:
        json.dump(v,f,indent=2,sort_keys=True); f.write('\n'); f.flush(); os.fsync(f.fileno())
def snapshot(root):
    out={}
    for p in [root,*sorted(root.rglob('*'))]:
        s=p.lstat(); assert not p.is_symlink()
        assert stat.S_ISREG(s.st_mode) or stat.S_ISDIR(s.st_mode)
        row={'kind':'directory' if p.is_dir() else 'file','mode':stat.S_IMODE(s.st_mode)}
        if row['kind']=='file': row.update({k:v for k,v in pin(p).items() if k in ('sha256','bytes')})
        out[str(p.relative_to(root))]=row
    return out
def main():
    assert __debug__ and not C.exists()
    before=snapshot(P/'source'); assert before==load(P/'stable-source-inventory.json')
    packet=load(D/'source-author-packet-v2.json')
    opinion=load(D/'independent-source-review-v2.json')
    assert opinion['disposition']=='QUALIFIED_EXACT_COMPILER_DEBUG_ASSIGNMENT_TRACKING_COST_REPAIR_SOURCE_ONLY'
    assert packet['permitted_names']==[NAME]
    for key in ('author_freeze','source_identity','source_delta','exact_transformations','actual_author_launch','prior_qualified_source_only_review','installed_compiler_metadata_supplement','historical_exact_v1_packet'):
        assert pin(packet[key]['path'])==packet[key]
    freeze=load(packet['author_freeze']['path'])
    for row in freeze['files'].values(): assert pin(row['path'])==row
    assert all(pin(D/'preimages'/NAME)[k]==pin(P/'source'/NAME)[k] for k in ('sha256','bytes','mode'))
    original=(P/'source'/NAME).read_bytes()
    needle=b'("-gnat2022", "-gnatwa", "-gnatVa", "-gnatf", "-O2", "-g", "-fPIC");'
    assert original.count(needle)==1
    expected=original.replace(needle,needle.replace(b'"-fPIC"',b'"-fPIC", "-fno-var-tracking-assignments"'),1)
    assert expected==(D/'source'/NAME).read_bytes()
    shutil.copytree(P/'source',C/'source')
    assert snapshot(C/'source')==before
    shutil.copy2(D/'source'/NAME,C/'source'/NAME)
    for mode,report in [('write','pin-refresh-source-observation.json'),('check','pin-check-source-observation.json')]:
        argv=['/usr/bin/python3','-B',str(C/'source/refresh_contract_pins.py'),'--'+mode,'--root',str(C/'source'),'--report',str(C/report)]
        r=subprocess.run(argv,capture_output=True)
        (C/('pin-'+mode+'.stdout')).write_bytes(r.stdout); (C/('pin-'+mode+'.stderr')).write_bytes(r.stderr)
        save(C/('pin-'+mode+'-command.json'),{'argv':argv,'returncode':r.returncode,'target_execution':False})
        assert r.returncode==0
        changes=load(C/report)['changed']
        assert ({row['path'] for row in changes}=={NAME} if mode=='write' else changes==[])
    registration=C/'source/protected-root/controls/source_registration.json'
    reg=load(registration)
    mapping=reg['fixed_excluded_source_owner']['affected_source_sha256']
    assert NAME not in mapping
    reg_changes={n:{'before':old,'after':pin(C/'source'/n)['sha256']} for n,old in mapping.items() if old!=pin(C/'source'/n)['sha256']}
    assert set(reg_changes)<={'runtime/worldline/proof_manifest.py'}
    for n,row in reg_changes.items(): mapping[n]=row['after']
    reg['codex_compiler_debug_cost_source_binding']={'source_only':True,'preimage_registration':pin(P/'source/protected-root/controls/source_registration.json'),'changes':reg_changes,'reviewed_donor_packet':pin(D/'source-author-packet-v2.json'),'reviewed_donor_opinion':pin(D/'independent-source-review-v2.json'),'proof_runtime_or_phase_acceptance':False,'actual_operator_policy_recovery_symbol_selection':None}
    registration.write_text(json.dumps(reg,indent=2)+'\n')
    after=snapshot(C/'source')
    changed={n for n in set(before)|set(after) if before.get(n)!=after.get(n)}
    assert changed=={NAME,'runtime/worldline/proof_manifest.py','protected-root/controls/source_registration.json'}
    direct=[{'path':n,'before':before.get(n),'after':after.get(n)} for n in sorted(changed)]
    base=load(T.parent/'phase1-integrated-v67-draft/stable-source-inventory.json')
    delta=[{'path':n,'before':base.get(n),'after':after.get(n)} for n in sorted(set(base)|set(after)) if base.get(n)!=after.get(n)]
    save(C/'stable-source-inventory.json',after)
    save(C/'source-inventory.json',{n:{k:v for k,v in row.items() if k!='bytes'} for n,row in after.items()})
    save(C/'source-changes.json',delta); save(C/'source7-to-source8-delta.json',direct)
    save(C/'compiler-cost-integration.json',{'schema':'worldline-exact-qualified-compiler-debug-cost-source-composition-v1','predecessor_selection':pin(P/'source-selection.json'),'predecessor_review':pin(T/'frame-review-draft/integrated-v7-independent-source-review.json'),'reviewed_donor_packet':pin(D/'source-author-packet-v2.json'),'reviewed_donor_opinion':pin(D/'independent-source-review-v2.json'),'complete_direct_delta':pin(C/'source7-to-source8-delta.json'),'registration_changes':reg_changes,'preimage_registration':pin(P/'source/protected-root/controls/source_registration.json'),'postimage_registration':pin(registration),'scope':'Only the independently reviewed GPR switch, original AST-selected digest literals for that GPR, and exact affected manifest registration are changed. All source contracts, executable Ada/Python/C, domains, rosters, floor, GPR check settings, original proof argv and runtime obligations remain unchanged. Debug assignment-location history is reduced. Actual effectiveness, complete proof/runtime and phase acceptance remain open.','target_execution':False,'phase_acceptance':False})
    argv=['/usr/bin/python3','-B',str(T.parent/'proof-enrollment-repair-v49/collect_enrollment_report.py'),'--root',str(C/'source'),'--output',str(C/'enrollment-report.json'),'--pin-refresh-report',str(C/'pin-refresh-source-observation.json')]
    r=subprocess.run(argv,capture_output=True)
    (C/'enrollment.stdout').write_bytes(r.stdout); (C/'enrollment.stderr').write_bytes(r.stderr)
    save(C/'enrollment-collection-invocation.json',{'schema':'worldline-original-source-only-enrollment-collector-invocation-v1','argv':argv,'returncode':r.returncode,'stdout':pin(C/'enrollment.stdout'),'stderr':pin(C/'enrollment.stderr'),'source_mutated':False,'target_execution':False,'proof_acceptance':False,'phase_acceptance':False,'collector_guard_unchanged':True})
    assert r.returncode==0 and snapshot(C/'source')==after
    selection=load(P/'source-selection.json')
    selection.update(source=str(C/'source'),source_inventory=pin(C/'source-inventory.json'),stable_source_inventory=pin(C/'stable-source-inventory.json'),source_changes=pin(C/'source-changes.json'),complete_original_f67_to_current_delta=pin(C/'source-changes.json'),source7_to_source8_delta=pin(C/'source7-to-source8-delta.json'),compiler_cost_integration=pin(C/'compiler-cost-integration.json'),preserved_full_strict_timeout_source_selection=pin(P/'source-selection.json'),pin_check_source_observation=pin(C/'pin-check-source-observation.json'),all_literal_pin_check=pin(C/'pin-check-source-observation.json'),pin_refresh_source_observation=pin(C/'pin-refresh-source-observation.json'),all_literal_pin_refresh=pin(C/'pin-refresh-source-observation.json'),source_only_enrollment=pin(C/'enrollment-report.json'),enrollment_collection_invocation=pin(C/'enrollment-collection-invocation.json'),enrollment_source_delta=pin(C/'enrollment-report.source.patch'),reviews='Predecessor coherent source and exact debug-cost donor have independent source-only opinions. Complete composition and all matching-source execution and final acceptance remain mandatory.',proof_acceptance=False,runtime_acceptance=False,phase_acceptance=False)
    save(C/'source-selection.json',selection)
    assert snapshot(P/'source')==before
    print(json.dumps({'selection':pin(C/'source-selection.json'),'direct_delta':pin(C/'source7-to-source8-delta.json'),'enrollment':pin(C/'enrollment-report.json'),'changed_paths':sorted(changed),'target_execution':False,'phase_acceptance':False}))

if __name__=='__main__': main()
