import hashlib, json, os, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path.cwd()
OUT = ROOT / 'records/phase1-blockers/final-build-steps-v5'
OUT.mkdir(exist_ok=False)
FROZEN = json.loads((ROOT/'records/phase1-blockers/freeze-v5/source.json').read_text())
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip() == FROZEN['commit']
assert not subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],text=True)

def digest(p):
    with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()

def step(name, command):
    record={'name':name,'argv':command,'cwd':str(ROOT),'source_commit':FROZEN['commit'],
            'utc':datetime.now(timezone.utc).isoformat(),'WORLDLINE_BUILD':os.environ['WORLDLINE_BUILD']}
    with (OUT/(name+'.stdout')).open('wb') as o, (OUT/(name+'.stderr')).open('wb') as e:
        result=subprocess.run(command,stdout=o,stderr=e)
    record.update(exit_code=result.returncode,completed_utc=datetime.now(timezone.utc).isoformat())
    (OUT/(name+'.json')).write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record),flush=True)
    return result.returncode

# Retain rather than delete earlier generated objects, including incomplete proof.
quiescence = subprocess.run(['python3','-B','scratch/coordinator/check_owned_quiescence.py',str(OUT/'owned-quiescence-before.json')])
if quiescence.returncode: raise SystemExit('Refuse artifact moves without positive owned-job quiescence')
users=[]
for process in Path('/proc').iterdir():
    if not process.name.isdigit(): continue
    try:
        for line in (process/'maps').read_text().splitlines():
            if str(ROOT/'lib')+'/' in line: users.append({'pid':process.name,'mapping':line})
    except (OSError,PermissionError): pass
(OUT/'library-users-before.json').write_text(json.dumps(users,indent=2)+'\n')
if users: raise SystemExit('Refuse moving libraries with current mapped users')
retained=ROOT/'scratch/coordinator/retained-prefreeze-generated-v5'
retained.mkdir(exist_ok=False)
inventory={}
for name in ('obj','bin','lib'):
    folder=ROOT/name
    if folder.exists():
        inventory[name]={str(p.relative_to(ROOT)):digest(p) for p in folder.rglob('*') if p.is_file()}
        folder.rename(retained/name)
private=ROOT/'scratch/old-analysis/private-sparklib-experiment/lib/gnat'
for name in ('sparklib_obj','sparklib_lib'):
    folder=private/name
    if folder.exists():
        inventory[name]={str(p.relative_to(ROOT)):digest(p) for p in folder.rglob('*') if p.is_file()}
        folder.rename(retained/name)
(OUT/'retained-generated.json').write_text(json.dumps(inventory,indent=2)+'\n')

driver=['python3','-B','scratch/old-analysis/sparklib_build_experiment.py']
standalone='scratch/old-analysis/sparklib-standalone-final-v5'
code=step('private-dependency',driver+['standalone','--out',standalone])
if code: raise SystemExit(code)
code=step('full-root',driver+['full','--out','scratch/old-analysis/sparklib-full-final-v5','--standalone-receipt',standalone+'/result.json'])
if code: raise SystemExit(code)
guard=['bwrap','--die-with-parent','--ro-bind','/','/','--dev','/dev','--proc','/proc','--bind',str(ROOT),str(ROOT),'--bind',os.environ['TMPDIR'],'/tmp','--chdir',str(ROOT)]
os.environ['PENDING_OBJECT_DIR']=str(ROOT/'obj/pending-standalone')
os.environ['PENDING_LIBRARY_DIR']=str(ROOT/'lib/pending-standalone')
code=step('pending',guard+['gprbuild','-p','-P','pending-component/pending.gpr','-j2'])
if code: raise SystemExit(code)
frame=ROOT/'scratch/coordinator/final-frame-v5'
code=step('native',guard+['python3','-B',str(frame/'source/native/build_guard.py'),str(frame/'native-artifacts')])
if code: raise SystemExit(code)
artifacts={str(p.relative_to(ROOT)):digest(p) for folder in (ROOT/'bin',ROOT/'lib',frame/'native-artifacts') for p in folder.rglob('*') if p.is_file()}
required_ali_names={'worldline_core_tests.ali','worldline_core_fuzz.ali','native_diagnostic_trace.ali'}
ali_paths=[p for p in (ROOT/'obj').rglob('*.ali') if p.name in required_ali_names]
ali={str(p.relative_to(ROOT)): 'A -gnata' in p.read_text().splitlines() for p in ali_paths}
ali_roster_complete={p.name for p in ali_paths} == required_ali_names
unchanged=all((ROOT/p).is_file() and digest(ROOT/p)==h for p,h in FROZEN['source_hashes'].items())
(OUT/'artifacts.json').write_text(json.dumps({'classification':'MEASURED','source_commit':FROZEN['commit'],'source_unchanged':unchanged,'assertion_options':ali,'required_assertion_ali_names':sorted(required_ali_names),'assertion_ali_roster_complete':ali_roster_complete,'artifacts':artifacts},indent=2)+'\n')
if not unchanged or not ali_roster_complete or not all(ali.values()): raise SystemExit('source or assertion option verification failed')
