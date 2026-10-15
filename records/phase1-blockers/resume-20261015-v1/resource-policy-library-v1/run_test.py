import datetime, hashlib, json, os, re, shutil, signal, subprocess, sys, time
from pathlib import Path
ROOT = Path('/home/sicarii/Work/worldline-phase1-blockers-20261013T165716Z')
OUT = ROOT / 'records/phase1-blockers/resume-20261015-v1/resource-policy-library-v1/test-parent'
SCOPE = ROOT / 'records/phase1-blockers/resume-20261015-v1/resource-policy-library-v1/test-scope'
OUT.mkdir(exist_ok=False)
def stamp(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def sources():
    paths = subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).split(b'\0')
    return {os.fsdecode(p): digest(ROOT/os.fsdecode(p)) for p in paths if p and (ROOT/os.fsdecode(p)).is_file() and not (ROOT/os.fsdecode(p)).is_symlink()}
preflight = ['python3','/home/sicarii/.codex/skills/project-vault/scripts/storage_status.py']
with (OUT/'storage-preflight.stdout').open('xb') as stdout, (OUT/'storage-preflight.stderr').open('xb') as stderr:
    pre = subprocess.run(preflight,stdout=stdout,stderr=stderr,cwd=ROOT)
if pre.returncode != 0 or shutil.disk_usage(ROOT).free < 20000000000: raise SystemExit('Storage preflight refused')
command = [sys.executable,'-B',str(ROOT/'scripts/phase1_heavy.py'),'--timeout','10m','--out',str(SCOPE),'--','bash','-c','source /home/sicarii/opt/gnat/env.sh; exec python3 -B "$1"','phase1-resource-policy-test',str(ROOT/'records/phase1-blockers/resume-20261015-v1/resource-policy-library-v1/test.py')]
before = sources()
(OUT/'source-before.json').write_text(json.dumps(before,sort_keys=True,indent=2)+'\n')
(OUT/'source.diff').write_bytes(subprocess.check_output(['git','diff','HEAD','--binary','--'],cwd=ROOT))
started = stamp()
receipt = {'argv':command,'cwd':str(ROOT),'started_utc':started,'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'source_diff_sha256':digest(OUT/'source.diff'),'python_version':sys.version,'python_path':sys.executable,'python_sha256':digest(Path(sys.executable).resolve()),'driver_sha256':digest(Path(__file__)),'environment':{k:os.environ.get(k) for k in ['PATH','LANG','LC_ALL','LD_LIBRARY_PATH','WORLDLINE_CORE_LIBRARY']},'explicit_environment':{'GNAT_environment_script':'/home/sicarii/opt/gnat/env.sh','worker_TMPDIR':str(SCOPE/'tmp'),'worker_XDG_CACHE_HOME':str(SCOPE/'cache'),'PYTHONDONTWRITEBYTECODE':'1'},'scope':'Complete unchanged original resource-policy module against exact freshly built production library; finite ordinary controls only, not full runtime/proof or protected acceptance'}
(OUT/'launch.json').write_text(json.dumps(receipt,indent=2)+'\n')
with (OUT/'stdout').open('xb') as stdout, (OUT/'stderr').open('xb') as stderr:
    process = subprocess.Popen(command,cwd=ROOT,stdout=stdout,stderr=stderr,start_new_session=True)
    with (OUT/'disk.jsonl').open('x') as disk:
        while True:
            code = process.poll(); free = shutil.disk_usage(ROOT).free
            disk.write(json.dumps({'utc':stamp(),'free_bytes':free,'minimum_reserve_bytes':10000000000,'early_stop_bytes':20000000000})+'\n');disk.flush()
            if code is not None: break
            if free < 20000000000:
                sf = SCOPE/'scope.jsonl'
                if sf.exists():
                    unit=json.loads(sf.read_text().splitlines()[-1])['unit']
                    if not re.fullmatch(r'wl-phase1-[0-9a-f]{32}\.scope',unit): raise RuntimeError('Unexpected owned scope identity')
                    subprocess.run(['systemctl','--user','stop',unit],check=False)
                os.killpg(process.pid,signal.SIGTERM);code=process.wait();break
            time.sleep(5)
after=sources();(OUT/'source-after.json').write_text(json.dumps(after,sort_keys=True,indent=2)+'\n')
receipt.update(ended_utc=stamp(),exit_code=code,tracked_sources_unchanged=(before==after),source_before_sha256=digest(OUT/'source-before.json'),source_after_sha256=digest(OUT/'source-after.json'),stdout_sha256=digest(OUT/'stdout'),stderr_sha256=digest(OUT/'stderr'))
(OUT/'result.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'exit_code':code,'tracked_sources_unchanged':before==after,'result':str(OUT/'result.json')}))
raise SystemExit(code if before==after else 125)
