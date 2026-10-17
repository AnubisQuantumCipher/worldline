from pathlib import Path
import subprocess,hashlib,json,os,datetime
ROOT=Path.cwd()
OUT=ROOT/'records/phase1-blockers/original-aux-builds-final-v6'
OUT.mkdir(exist_ok=False)
freeze=json.loads((ROOT/'records/phase1-blockers/freeze-v5/source.json').read_text())
def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==freeze['commit']
assert all(digest(ROOT/p)==h for p,h in freeze['source_hashes'].items())
roster_path=ROOT/'scratch/reviewer/f1-original-full-planned-build-roster.json'
roster=json.loads(roster_path.read_text())
assert digest(Path(roster['source']))==roster['sha256']
(OUT/'historical-planned-actions.json').write_bytes(Path(roster['source']).read_bytes())
actions=list(roster['builds'])
for name,project in [('original-physical-semantic-build','physical-value-controls/physical_value_controls.gpr'),('original-canonical-exchange-semantic-build','canonical-exchange-tests/canonical_exchange_tests.gpr'),('original-canonical-owner-semantic-build','canonical-owner-completion-tests/canonical_owner_completion_tests.gpr')]:
    actions.append({'mode':name,'argv':['gprbuild','-p','-j2','-P',project],'cwd':str(ROOT),'required_original_roster':'restored original domains; separate historical source review'})
env=dict(os.environ)
env.update(WORLDLINE_BUILD='checks',SPARKLIB_MODE='full',SPARKLIB_BUILD='Production',SPARKLIB_LIBRARY_TYPE='static',SPARKLIB_INSTALLED='True',WORLDLINE_PRIVATE_SPARKLIB_PREBUILT='True',PENDING_OBJECT_DIR=str(ROOT/'obj/pending-standalone'),PENDING_LIBRARY_DIR=str(ROOT/'lib/pending-standalone'))
private=ROOT/'scratch/old-analysis/private-sparklib-experiment/lib/gnat'
env['GPR_PROJECT_PATH']=str(private)+':'+env.get('GPR_PROJECT_PATH','')
for name in ('GPR_TOOL','GPR_PROJECT_PATH_FILE','GPRBUILD_OPTIONS','ADA_INCLUDE_PATH','ADA_OBJECTS_PATH'):env.pop(name,None)
guard=['bwrap','--die-with-parent','--ro-bind','/','/','--dev','/dev','--proc','/proc','--bind',str(ROOT),str(ROOT),'--bind',os.environ['TMPDIR'],'/tmp','--chdir',str(ROOT)]
library=ROOT/'lib/libworldline_core.so'
before=digest(library)
records=[]
for action in actions:
    name=action['mode']; directory=OUT/name;directory.mkdir(exist_ok=False)
    argv=[value.replace(action['cwd'],str(ROOT)) for value in action['argv']]
    record={'name':name,'classification':'TESTED','source_commit':freeze['commit'],'started_utc':utc(),'cwd':str(ROOT),'original':action,'argv':guard+argv,'environment':{k:env[k] for k in ['WORLDLINE_BUILD','GPR_PROJECT_PATH','WORLDLINE_PRIVATE_SPARKLIB_PREBUILT','SPARKLIB_MODE','SPARKLIB_BUILD','SPARKLIB_LIBRARY_TYPE','SPARKLIB_INSTALLED','PENDING_OBJECT_DIR','PENDING_LIBRARY_DIR']}}
    (directory/'launch.json').write_text(json.dumps(record,indent=2)+'\n')
    with (directory/'stdout').open('wb') as o,(directory/'stderr').open('wb') as e:
        result=subprocess.run(guard+argv,env=env,stdout=o,stderr=e);code=result.returncode
    record.update(exit_code=code,ended_utc=utc())
    (directory/'result.json').write_text(json.dumps(record,indent=2)+'\n');records.append(record)
    print(json.dumps({'mode':name,'exit_code':code}),flush=True)
# Original assurance behavior/fuzz commands, retaining their original PASS predicate.
for name,argv in [('ada-tests',['./bin/worldline_core_tests']),('ada-fuzz',['./bin/worldline_core_fuzz'])]:
    directory=OUT/name;directory.mkdir(exist_ok=False)
    record={'name':name,'classification':'TESTED','source_commit':freeze['commit'],'started_utc':utc(),'cwd':str(ROOT),'argv':guard+argv}
    (directory/'launch.json').write_text(json.dumps(record,indent=2)+'\n')
    prerequisite='tests-worldline-core-tests-build' if name=='ada-tests' else 'tests-worldline-core-fuzz-build'
    matching=next((r for r in records if r['name']==prerequisite),None)
    binary=ROOT/argv[0]
    if matching is None or matching.get('exit_code')!=0 or not binary.is_file():
        record.update(exit_code=None,status='NOT PERFORMED',ended_utc=utc(),reason='Matching current prerequisite build failed or absent; no stale binary fallback',prerequisite=prerequisite)
        (directory/'result.json').write_text(json.dumps(record,indent=2)+'\n');records.append(record)
        continue
    record.update(prerequisite=prerequisite,binary_sha256=digest(binary))
    with (directory/'stdout').open('wb') as o,(directory/'stderr').open('wb') as e:
        result=subprocess.run(guard+argv,env=env,stdout=o,stderr=e);code=result.returncode
    output=(directory/'stdout').read_text(errors='replace')
    record.update(exit_code=code,ended_utc=utc(),original_pass_marker='PASS' in output)
    (directory/'result.json').write_text(json.dumps(record,indent=2)+'\n');records.append(record)
    print(json.dumps({'mode':name,'exit_code':code,'original_pass_marker':record['original_pass_marker']}),flush=True)
result={'classification':'TESTED','source_commit':freeze['commit'],'roster_sha256':digest(roster_path),'steps':records,'source_unchanged':all(digest(ROOT/p)==h for p,h in freeze['source_hashes'].items()),'library_before':before,'library_after':digest(library),'full_acceptance':False}
result['library_unchanged'] = result['library_before'] == result['library_after']
result['original_behavior_predicates_passed'] = all(
    any(r['name']==name and r.get('exit_code')==0 and r.get('original_pass_marker') is True for r in records)
    for name in ('ada-tests','ada-fuzz'))
result['passed'] = (all(r['exit_code']==0 for r in records) and result['source_unchanged']
                    and result['library_unchanged'] and result['original_behavior_predicates_passed'])
if not result['library_unchanged']:
    result['artifact_join_status'] = 'FAILED-OPEN: rebuilt library differs; prior joins cannot transfer to dependent runs'
(OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n')
raise SystemExit(0 if result['passed'] else 1)
