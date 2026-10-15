#!/usr/bin/env python3
"""Prepared post-run original proof gate plus explicit whole-closure joins.

No build/prover launch, source mutation, pin refresh or root manifest publication.
Only a fresh owned output directory is written. Failure receipts use a separate
schema and null proof counts when the original strict parser cannot establish them.
"""
from __future__ import annotations
import argparse,ast,datetime,hashlib,json,re,subprocess,sys,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OWN=ROOT/'scratch/old-analysis'
FRAME=PRIVATE=FREEZE=DEPENDENCY=BUILD=None

def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,value):
    with path.open('x') as stream:json.dump(value,stream,sort_keys=True,indent=2);stream.write('\n')
def original_screen_ast(root):
    source=(root/'prove.sh').read_text().split("<<'PY'\n",1)[1].split('\nPY\n',1)[0]
    tree=ast.parse(source);wanted={'_ASSUME','_JUSTIFY','_SPARK_OFF'}
    nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='code_only'
           or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in wanted for t in n.targets)]
    environment={'re':re};exec(compile(ast.Module(body=nodes,type_ignores=[]),'original prove.sh screening','exec'),environment)
    if not all(key in environment for key in wanted|{'code_only'}):raise RuntimeError('Original screen structure not recognized')
    template=next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='manifest' for t in n.targets))
    return environment,template

def main():
    global FRAME,PRIVATE,FREEZE,DEPENDENCY,BUILD
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--proof-run',type=Path,required=True);p.add_argument('--proof-scope',type=Path,required=True);p.add_argument('--expected-commit',required=True)
    for name in ('frame','freeze-record','build-manifest','dependency-manifest','private-dependency'):
        p.add_argument('--'+name,type=Path,required=True)
    args=p.parse_args()
    FRAME=args.frame.resolve();FREEZE=args.freeze_record.resolve();BUILD=args.build_manifest.resolve()
    DEPENDENCY=args.dependency_manifest.resolve();PRIVATE=args.private_dependency.resolve()
    if any(not value.is_relative_to(ROOT) for value in (FRAME,FREEZE,BUILD,DEPENDENCY,PRIVATE)):
        p.error('Frozen identity and private dependency inputs must remain inside this worktree')
    out=args.out.resolve();run=args.proof_run.resolve();scope=args.proof_scope.resolve()
    if not out.is_relative_to(OWN) or not run.is_relative_to(OWN) or not scope.is_relative_to(OWN) or not re.fullmatch('[a-f0-9]{40}',args.expected_commit):p.error('Owned scratch paths and full commit required')
    out.mkdir(parents=True,exist_ok=False)
    receipt={'schema':'worldline-phase1-proof-gate-outcome-v1','source_commit':args.expected_commit,
      'classification':'MEASURED gate readback; not independent acceptance','gate':'F2','status':'FAILED-OPEN',
      'command':sys.argv,'driver_sha256':sha(Path(__file__)),'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'proof_counts':None,'proof_process_exit':None,'successful_manifest_generated':False,'independent_acceptance':'NOT PERFORMED','findings':[]}
    findings=receipt['findings'];parsed=None;summary=None;sources=None
    try:
        scope_rows={}
        for name in ('admission.jsonl','admitted.json','launch.jsonl','scope.jsonl','cgroup.jsonl','result.jsonl','terminal-scope.jsonl'):
            path=scope/name
            if not path.is_file():
                findings.append({'gate':'scope completion/resources','path':str(path.relative_to(ROOT)),'message':'Required scope receipt absent; not zero or pass'});continue
            raw=path.read_bytes();scope_rows[name]=[json.loads(line) for line in raw.splitlines() if line.strip()]
            receipt.setdefault('scope_receipt_hashes',{})[name]=hashlib.sha256(raw).hexdigest()
        receipt['scope_final_result']=scope_rows.get('result.jsonl');receipt['scope_terminal']=scope_rows.get('terminal-scope.jsonl')
        if scope_rows.get('admitted.json')!=[{'admitted':True}]:findings.append({'gate':'scope admission','message':'Positive memory admission missing'})
        endings=scope_rows.get('result.jsonl',[]);terminal=scope_rows.get('terminal-scope.jsonl',[])
        if len(endings)!=1 or endings[0].get('exit_code')!=0:findings.append({'gate':'scope exit','message':'Heavy scope result is missing, ambiguous or nonzero; raw result preserved'})
        if len(terminal)!=1 or terminal[0].get('populated') is not False:findings.append({'gate':'scope terminal','message':'Terminal scope quiescence not established'})
        samples=[row for row in scope_rows.get('cgroup.jsonl',[]) if row.get('memory.max') is not None]
        if not samples or any(row['memory.max']!='8589934592' or row.get('memory.swap.max')!='0' for row in samples):findings.append({'gate':'scope resource bounds','message':'Actual unchanged 8G MemoryMax and zero swap not established for every retained live sample'})
        events=[]
        for row in samples:
            text=row.get('memory.events')
            if not isinstance(text,str):findings.append({'gate':'scope OOM observation','message':'Live memory.events missing'});continue
            values=dict(line.split() for line in text.splitlines());events.append(values)
            if values.get('oom_kill')!='0' or values.get('oom_group_kill')!='0':findings.append({'gate':'scope OOM observation','message':'OOM counters absent or nonzero','observed':values})
        receipt['observed_memory_events']=events
        frozen=json.loads(FREEZE.read_text());build=json.loads(BUILD.read_text());dependency=json.loads(DEPENDENCY.read_text())
        receipt['identity_records']={str(p.relative_to(ROOT)):sha(p) for p in (FREEZE,BUILD,DEPENDENCY)}
        if frozen['commit']!=args.expected_commit or build['source_commit']!=args.expected_commit:raise RuntimeError('Frozen/build commit join mismatch')
        for relative,expected in frozen['source_hashes'].items():
            if sha(ROOT/relative)!=expected or sha(FRAME/relative)!=expected:raise RuntimeError('Frozen root/frame bytes differ: '+relative)
        sys.path.insert(0,str(FRAME/'runtime'));from worldline import proof_manifest as gate
        screen,template=original_screen_ast(FRAME)
        receipt['original_gate_source_hashes']={p:sha(FRAME/p) for p in ('prove.sh','verify_proof_manifest.py','runtime/worldline/proof_manifest.py')}
        receipt['original_requirements']={'minimum_checks':gate.MINIMUM_CHECKS,'required_proved':gate.REQUIRED_PROVED,'expected_units':sorted(gate.expected_units(ROOT)),'unanalyzed_boundary':sorted(gate.UNANALYZED_BOUNDARY)}
        findings.extend({'gate':'original contract/source/export pins','message':v} for v in gate.contract_problems(ROOT))
        sources=gate.source_paths(ROOT);source_rows=[]
        for key,path in sorted(sources.items()):
            text=screen['code_only'](path)
            hits={label:[{'line':text[:m.start()].count(b'\n')+1,'match':m.group().decode()} for m in screen[pattern].finditer(text)] for label,pattern in (('assume','_ASSUME'),('original_gnatprove_annotation_screen','_JUSTIFY'),('spark_off','_SPARK_OFF'))}
            source_rows.append({'key':key,'sha256':sha(path),'original_off_exception':'c_api' in key,**hits})
            if hits['assume'] or hits['original_gnatprove_annotation_screen'] or (hits['spark_off'] and 'c_api' not in key):findings.append({'gate':'original source screen','path':key,'message':'Original prove.sh screening refuses this source','hits':hits})
        save(out/'original-source-screen.json',source_rows)
        imported=[]
        for relative,expected in {**dependency['source_hashes'],**dependency['project_hashes']}.items():
            if sha(PRIVATE/relative)!=expected:raise RuntimeError('Private dependency bytes differ: '+relative)
        for relative in dependency['source_selection']['active_ada_files']:
            path=PRIVATE/relative;text=screen['code_only'](path)
            hits={label:[{'line':text[:m.start()].count(b'\n')+1,'match':m.group().decode()} for m in screen[pattern].finditer(text)] for label,pattern in (('assume','_ASSUME'),('annotations','_JUSTIFY'),('spark_off','_SPARK_OFF'))}
            imported.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path),**hits})
            if hits['assume']:findings.append({'gate':'imported source closure','path':relative,'message':'pragma Assume exists in selected imported source'})
            if hits['spark_off']:findings.append({'gate':'imported source closure','path':relative,'message':'Existing imported SPARK_Mode Off implementation remains outside proof; no new exemption granted'})
        save(out/'imported-source-screen.json',imported)
        receipt['imported_annotation_scope']='All retained verbatim; imported annotations are not blanket-labelled justified checks. Actual justified/skipped proof results and original required imported coverage remain mandatory.'
        receipt['built_artifact_hashes']=build['artifacts']
        for relative,expected in build['artifacts'].items():
            if sha(ROOT/relative)!=expected:raise RuntimeError('Final built artifact changed: '+relative)
        launch=json.loads((run/'launch.json').read_text());receipt['proof_launch_sha256']=sha(run/'launch.json');receipt['proof_argv']=launch['gnatprove_argv']
        expected_inputs={'frame':str(FRAME),'freeze_record':str(FREEZE),'build_manifest':str(BUILD),'fresh_dependency':str(PRIVATE)}
        if any(launch.get(key)!=value for key,value in expected_inputs.items()):raise RuntimeError('Explicit gate inputs differ from actual full proof launch identities')
        fresh=json.loads((run/'fresh-dependency.json').read_text())
        if (fresh.get('private')!=str(PRIVATE) or fresh.get('manifest')!=str(DEPENDENCY)
            or fresh.get('manifest_sha256')!=sha(DEPENDENCY) or fresh.get('all_installed_source_pins_verified') is not True
            or fresh.get('source_hashes')!=dependency['source_hashes'] or fresh.get('project_hashes')!=dependency['project_hashes']):
            raise RuntimeError('Fresh proof dependency receipt does not join exact selected source/project roster')
        receipt['fresh_dependency_record_sha256']=sha(run/'fresh-dependency.json')
        required=['gnatprove','-P','core/worldline_core.gpr','-U','--mode=all','--level=3','--report=all','--checks-as-errors=on','--proof-warnings=on','--memlimit=1024','--timeout=60','-j2','--subdirs='+launch['subdir'],'-XWORLDLINE_BUILD=checks','-XSPARKLIB_MODE=full','-XSPARKLIB_BUILD=Production','-XSPARKLIB_LIBRARY_TYPE=static','-XSPARKLIB_INSTALLED=True']
        if launch['commit']!=args.expected_commit or launch['gnatprove_argv']!=required:raise RuntimeError('Proof source, exact full aggregate scope or reviewed bounds differ')
        receipt['toolchain']=json.loads((run/'versions.json').read_text());receipt['toolchain_record_sha256']=sha(run/'versions.json')
        if not (run/'result.json').is_file():
            findings.append({'gate':'proof completion','message':'Final proof driver result is absent; NOT COMPLETED, never zero or pass'})
        else:
            result=json.loads((run/'result.json').read_text());receipt['proof_result_sha256']=sha(run/'result.json');receipt['proof_process_exit']=result.get('exit_code');receipt['proof_driver_status']=result.get('status')
            if result.get('exit_code')!=0:findings.append({'gate':'proof process','message':'GNATprove returned nonzero or no return status was established','observed':result.get('exit_code')})
            if result.get('commit')!=args.expected_commit or result.get('commit_after')!=args.expected_commit or not all(result.get(k) is True for k in ('source_unchanged','library_unchanged','private_unchanged')):findings.append({'gate':'proof identity','message':'Complete before/after source, private dependency and library identity not established'})
            paths=result.get('fresh_summary_paths');receipt['fresh_summary_paths']=paths
            if not isinstance(paths,list) or len(paths)!=1:findings.append({'gate':'summary','message':'Unique fresh summary absent or ambiguous; no counts inferred'})
            else:
                summary_path=(ROOT/paths[0]).resolve()
                if not summary_path.is_relative_to(ROOT) or result.get('reports',{}).get(paths[0])!=sha(summary_path):raise RuntimeError('Summary is not bound to completed proof report roster')
                summary=summary_path.read_bytes();(out/'gnatprove.out').write_bytes(summary);receipt['summary_sha256']=hashlib.sha256(summary).hexdigest()
                try:parsed=gate.parse_summary(summary.decode('utf-8'))
                except (UnicodeError,gate.SummaryError) as error:findings.append({'gate':'original strict summary parser','message':str(error)})
                if parsed is not None:
                    receipt['proof_counts']={k:parsed[k] for k in ('total','justified','unproved')};save(out/'strict-summary.json',parsed)
                    if parsed['unproved'] or parsed['justified']:findings.append({'gate':'zero exceptions','message':'Summary has unproved or justified checks'})
                    if parsed['total']<gate.MINIMUM_CHECKS:findings.append({'gate':'original floor','message':'Original proof floor not met'})
                    missing=sorted(gate.expected_units(ROOT)-set(parsed['units']));receipt['missing_original_units']=missing
                    absent=[name for name in gate.REQUIRED_PROVED if name not in parsed['subprograms']];receipt['missing_original_required_subprograms']=absent
                    active_imports={Path(relative).stem for relative in dependency['source_selection']['active_ada_files']};receipt['missing_whole_imported_units']=sorted(active_imports-set(parsed['units']))
                    incomplete={name:counts for name,counts in parsed['units'].items() if counts['analyzed']!=counts['available'] or name not in gate.UNANALYZED_BOUNDARY and counts['available']==0}
                    receipt['incomplete_units']=incomplete
                    if missing or absent or receipt['missing_whole_imported_units'] or incomplete or not parsed['units'] or not parsed['subprograms'] or not gate.UNANALYZED_BOUNDARY.issubset(parsed['units']):findings.append({'gate':'original plus whole imported coverage','message':'Required subprogram/unit/whole imported closure or exact existing boundary coverage incomplete'})
        # Only the original positive manifest structure may be emitted as a
        # candidate, and only after every original and additive join has passed.
        if not findings and parsed is not None and summary is not None:
            versions=receipt['toolchain']
            def first_line(argv):return versions[argv[0]]['stdout'].splitlines()[0]
            context={'root':ROOT,'out_path':summary_path,'lib_path':ROOT/'lib/libworldline_core.so','total':parsed['total'],'justified':parsed['justified'],'unproved':parsed['unproved'],'assumes':0,
              'MINIMUM_CHECKS':gate.MINIMUM_CHECKS,'REQUIRED_PROVED':gate.REQUIRED_PROVED,'UNANALYZED_BOUNDARY':gate.UNANALYZED_BOUNDARY,'sources':sources,'units':parsed['units'],'subprograms':parsed['subprograms'],'sha256':sha,'first_line':first_line}
            manifest=eval(compile(ast.Expression(template),'original prove.sh manifest template','eval'),context)
            manifest['options']=launch['gnatprove_argv'][3:]
            findings.extend({'gate':'original shared manifest verifier','message':v} for v in gate.manifest_problems(manifest,ROOT,library=ROOT/'lib/libworldline_core.so',summary=summary,require_summary=True))
            if not findings:
                save(out/'proof-manifest.candidate.json',manifest);receipt['successful_manifest_generated']=True;receipt['status']='PASSED';receipt['publication']='Candidate retained only; no root manifest installed, no Phase 1 acceptance declared'
    except BaseException as error:
        findings.append({'gate':'readback execution','message':type(error).__name__+': '+str(error)});(out/'traceback.txt').write_text(traceback.format_exc())
    finally:
        receipt['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
        if findings:receipt['status']='FAILED-OPEN'
        save(out/'proof-gate-outcome.json',receipt)
        print(json.dumps({'out':str(out),'status':receipt['status'],'proof_counts':receipt['proof_counts'],'successful_manifest_generated':receipt['successful_manifest_generated']},sort_keys=True))
    return 0 if receipt['status']=='PASSED' else 1
if __name__=='__main__':raise SystemExit(main())
