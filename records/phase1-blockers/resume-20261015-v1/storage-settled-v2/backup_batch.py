import datetime, json, os, shutil, signal, subprocess, time
from pathlib import Path
ROOT = Path('/home/sicarii/Work/worldline-phase1-blockers-20261013T165716Z')
OUT = ROOT / 'records/phase1-blockers/resume-20261015-v1/storage-settled-v2/backup-results'
OUT.mkdir(exist_ok=False)
SELECTED = ['records/phase1-blockers/resume-20261015-v1/'+name for name in ('finalizable-scalar-v1','finalizable-heap-v1','finalizable-heap-v2','finalizable-fresh-v1','toolchain-support-research-v1')] + ['scratch/final-gates/resume-20261015-v1/toolchain-support-source-research-v1']
def stamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()
results=[]
for index, relative in enumerate(SELECTED):
    target=ROOT/relative
    free=shutil.disk_usage(ROOT).free
    if free < 20000000000:
        raise SystemExit('Storage admission refused at unchanged early-stop margin')
    argv=['project-vault','put',str(target)]
    start=stamp()
    with (OUT/f'{index}.stdout').open('xb') as stdout, (OUT/f'{index}.stderr').open('xb') as stderr:
        process=subprocess.Popen(argv,cwd=ROOT,stdout=stdout,stderr=stderr,start_new_session=True)
        with (OUT/f'{index}.disk.jsonl').open('x') as disk:
            while True:
                code=process.poll()
                free=shutil.disk_usage(ROOT).free
                disk.write(json.dumps({'utc':stamp(),'free_bytes':free,'minimum_reserve_bytes':10000000000,'early_stop_bytes':20000000000})+'\n');disk.flush()
                if code is not None:
                    break
                if free < 20000000000:
                    os.killpg(process.pid,signal.SIGTERM)
                    code=process.wait()
                    break
                time.sleep(5)
    row={'path':str(target),'argv':argv,'cwd':str(ROOT),'started_utc':start,'ended_utc':stamp(),'exit_code':code,'local_directory_retained':target.is_dir(),'stdout':str(OUT/f'{index}.stdout'),'stderr':str(OUT/f'{index}.stderr'),'offload':False}
    results.append(row)
    (OUT/f'{index}.result.json').write_text(json.dumps(row,indent=2)+'\n')
    print(json.dumps({'index':index,'path':relative,'exit_code':code,'local_directory_retained':target.is_dir()}),flush=True)
    if code != 0:
        (OUT/'batch-result.json').write_text(json.dumps({'results':results,'complete':False,'stopped_on_failure':True},indent=2)+'\n')
        raise SystemExit(code)
(OUT/'batch-result.json').write_text(json.dumps({'results':results,'complete':True,'offload':False,'boundary':'CLI exits and directory retention only; item/snapshot/full recovery comparison receipts require separate readback.'},indent=2)+'\n')
