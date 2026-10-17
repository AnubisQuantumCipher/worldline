import datetime, hashlib, json, os, shutil, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results'
OUT.mkdir(exist_ok=False)
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
receipt={'started_utc':stamp(),'purpose':'Installed compiler/SPARK strict Finalizable scalar discriminator only; no heap retirement/full O1 claim','cwd':str(ROOT),'source_hashes':{p.name:digest(p) for p in ROOT.iterdir() if p.is_file()},'environment':{k:os.environ.get(k) for k in ('PATH','LANG','LC_ALL','ADA_PROJECT_PATH','GPR_PROJECT_PATH','TMPDIR','XDG_CACHE_HOME')}}
receipt['steps']=[]
def run(name,argv):
    item={'name':name,'argv':argv,'started_utc':stamp()}
    with (OUT/(name+'.stdout')).open('xb') as stdout,(OUT/(name+'.stderr')).open('xb') as stderr:
        result=subprocess.run(argv,cwd=ROOT,stdout=stdout,stderr=stderr)
    item.update(exit_code=result.returncode,ended_utc=stamp(),stdout_sha256=digest(OUT/(name+'.stdout')),stderr_sha256=digest(OUT/(name+'.stderr')))
    receipt['steps'].append(item)
    (OUT/'result.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return result.returncode
for name in ('gnatls','gprbuild','gnatprove'):
    executable=Path(shutil.which(name)).resolve()
    receipt[name]={'path':str(executable),'sha256':digest(executable)}
    run(name+'-version',[str(executable),'--version'])
build=run('build',['gprbuild','-P','probe.gpr','-j1'])
proof=run('proof',['gnatprove','-P','probe.gpr','-U','--mode=all','--level=3','--report=all','--checks-as-errors=on','--proof-warnings=on','--memlimit=1024','--timeout=60','-j1'])
runtime=run('runtime',[str(ROOT/'bin/main')]) if build==0 else None
receipt.update(ended_utc=stamp(),source_hashes_after={p.name:digest(p) for p in ROOT.iterdir() if p.is_file()},build_exit=build,proof_exit=proof,runtime_exit=runtime)
(OUT/'result.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'result':str(OUT/'result.json'),'build_exit':build,'proof_exit':proof,'runtime_exit':runtime}))
sys.exit(0 if build==proof==runtime==0 else 1)
