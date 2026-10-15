"""Finite actual sandbox controls only; coordinator heavy launch required."""
from __future__ import annotations
import argparse
import datetime
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

HERE=Path(__file__).resolve()
ROOT=HERE.parents[2]
DRIVER=HERE.with_name('original_binary_controls_v5.py')
spec=importlib.util.spec_from_file_location('binary_controls_v5',DRIVER)
D=importlib.util.module_from_spec(spec);spec.loader.exec_module(D)

def save(path,value):D.save(path,value)
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()

def process(pid):
    raw=Path(f'/proc/{pid}/stat').read_text()
    rest=raw[raw.rfind(')')+2:].split()
    result={'pid':pid,'starttime':rest[19],'state':rest[0],'ppid':int(rest[1]),
            'pgid':int(rest[2]),'session':int(rest[3]),'refusals':[]}
    for key,read in (('cgroup',lambda:Path(f'/proc/{pid}/cgroup').read_text()),
                     ('pid_namespace',lambda:os.readlink(f'/proc/{pid}/ns/pid')),
                     ('mount_namespace',lambda:os.readlink(f'/proc/{pid}/ns/mnt'))):
        try:result[key]=read()
        except OSError as error:
            result[key]=None;result['refusals'].append({'field':key,'error':str(error)})
    # A readable stat row, including a zombie, is never converted into ABSENT
    # merely because a namespace link or cgroup observation refused.
    return result

def descendants(parent):
    rows=[];pending=[parent];seen=set()
    while pending:
        pid=pending.pop()
        if pid in seen:continue
        seen.add(pid)
        try:
            row=process(pid)
            children=Path(f'/proc/{pid}/task/{pid}/children').read_text().split()
            if process(pid)['starttime']!=row['starttime']:
                raise RuntimeError('PID identity changed during ownership traversal')
        except FileNotFoundError:
            continue
        rows.append(row);pending.extend(int(x) for x in children)
    return rows

def fixture(out,mode):
    facts={'utc':utc(),'mode':mode,'pid':os.getpid(),'euid':os.geteuid(),
           'pid_namespace':os.readlink('/proc/self/ns/pid'),
           'mount_namespace':os.readlink('/proc/self/ns/mnt'),
           'root_readonly':bool(os.statvfs(ROOT).f_flag&os.ST_RDONLY),
           'frame_readonly':bool(os.statvfs(Path.cwd()).f_flag&os.ST_RDONLY),
           'own_output_readonly':bool(os.statvfs(out).f_flag&os.ST_RDONLY)}
    if mode=='detached':
        pid=os.fork()
        if pid==0:
            os.setsid()
            save(out/'detached-ready.json',{'utc':utc(),'pid':os.getpid(),
                 'session':os.getsid(0),'pid_namespace':os.readlink('/proc/self/ns/pid')})
            while True:time.sleep(1)
        deadline=time.monotonic()+10
        while not (out/'detached-ready.json').exists() and time.monotonic()<deadline:time.sleep(.02)
        if not (out/'detached-ready.json').exists():raise RuntimeError('own detached child not ready')
    save(out/'fixture-ready.json',facts)
    if mode=='normal':return 0
    while True:time.sleep(1)

def one(out,mode):
    out.mkdir();(out/'temp').mkdir();(out/'second').mkdir()
    command=D.guard(out)+['/usr/bin/python3','-B',str(HERE),'--fixture',str(out),mode]
    record={'utc':utc(),'mode':mode,'argv':command,'classification':'TESTED finite sandbox control'}
    with (out/'stdout').open('xb') as stdout,(out/'stderr').open('xb') as stderr:
        child=subprocess.Popen(command,cwd=D.FRAME,env=D.environment(out/'temp'),
                               stdout=stdout,stderr=stderr,start_new_session=True)
        record['started_child']=process(child.pid)
        save(out/'launch.json',record)
        stop=time.monotonic()+15
        owned=[]
        while time.monotonic()<stop:
            owned=descendants(child.pid)
            if (out/'fixture-ready.json').exists() or child.poll() is not None:break
            time.sleep(.05)
        save(out/'ownership-before-cleanup.json',{'utc':utc(),'direct_child':record['started_child'],'descendants':owned})
        ready=D.load(out/'fixture-ready.json') if (out/'fixture-ready.json').exists() else None
        if mode=='normal':
            try:code=child.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid,signal.SIGKILL);code=child.wait(timeout=10)
                record['unexpected_normal_timeout']=True
        else:
            # Same exact outer cleanup used by binary driver, solely owned child group.
            try:
                code=child.wait(timeout=1)
                record['expected_timeout_observed']=False
            except subprocess.TimeoutExpired:
                record['expected_timeout_observed']=True
                before=process(child.pid)
                if before['starttime']!=record['started_child']['starttime']:
                    raise RuntimeError('owned cleanup child identity changed')
                os.killpg(child.pid,signal.SIGKILL)
                code=child.wait(timeout=10)
        record['wait_exit_code']=code
    stop=time.monotonic()+10;remaining=[];observations=[]
    while True:
        remaining=[]
        for row in owned:
            try:current=process(row['pid'])
            except FileNotFoundError:
                observations.append({'pid':row['pid'],'starttime':row['starttime'],'state':'ABSENT'});continue
            if current['starttime']!=row['starttime']:
                observations.append({'pid':row['pid'],'starttime':row['starttime'],'state':'REUSED','current_starttime':current['starttime']});continue
            remaining.append(current)
        if not remaining or time.monotonic()>=stop:break
        time.sleep(.05)
    record.update(ready=ready,after=remaining,terminal_identity_observations=observations,
                  tracked_descendants_absent=not remaining,
                  child_reaped=child.returncode is not None,
                  readiness_observed=ready is not None)
    # A zombie is retained as remaining; no fabricated disappearance or live-quiescence.
    record['passed']=(ready is not None and ready['root_readonly'] and ready['frame_readonly']
         and not ready['own_output_readonly'] and not remaining and child.returncode is not None
         and ((mode=='normal' and code==0) or (mode!='normal' and record.get('expected_timeout_observed') is True)))
    save(out/'result.json',record)
    return record

def namespace_control(out):
    out.mkdir();(out/'temp').mkdir();(out/'second').mkdir()
    # Synthetic premise control only; real original unittest payload is not launched.
    payload=['/usr/bin/env','WORLDLINE_TEMP_PHYSICAL_NAMESPACE=1','WORLDLINE_PHYSICAL_SECOND_TMP=/dev/shm',
       '/usr/bin/unshare','--user','--map-root-user','/usr/bin/python3','-B','-c',
       'import os; assert os.geteuid()==0; print("NAMESPACE_PREMISE_ONLY")']
    command=D.guard(out,True)+['/usr/bin/python3','-B',str(DRIVER),'--namespace-inner',str(out),'--',*payload]
    with (out/'stdout').open('xb') as stdout,(out/'stderr').open('xb') as stderr:
        child=subprocess.Popen(command,cwd=D.FRAME,env=D.environment(out/'temp'),stdout=stdout,stderr=stderr,start_new_session=True)
        started=process(child.pid)
        save(out/'launch.json',{'utc':utc(),'argv':command,'started_child':started})
        try:code=child.wait(timeout=60)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid,signal.SIGKILL);code=child.wait(timeout=10)
    paths=('namespace-premises-before.json','namespace-user-probe.json','namespace-original-exec.json','namespace-payload-result.json')
    facts={name:D.load(out/name) if (out/name).exists() else None for name in paths}
    result={'utc':utc(),'classification':'TESTED disposable namespace premise only',
            'exit_code':code,'facts':facts,'stdout':D.identity(out/'stdout'),'stderr':D.identity(out/'stderr'),
            'passed':code==0 and all(x is not None for x in facts.values())
                 and (out/'stdout').read_text().splitlines()==['NAMESPACE_PREMISE_ONLY'],
            'non_claim':'No original syscall fixture or protected authority executed'}
    save(out/'result.json',result);return result

def main():
    if len(sys.argv)>1 and sys.argv[1]=='--fixture':return fixture(D.owned(sys.argv[2]),sys.argv[3])
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--frame',required=True)
    a=p.parse_args();D.FRAME=Path(a.frame).resolve()
    if not D.FRAME.is_relative_to(ROOT):raise RuntimeError('frame outside owned worktree')
    out=D.owned(a.out);out.mkdir(parents=True,exist_ok=False)
    save(out/'scope.json',D.scope_identity())
    save(out/'identity.json',{'utc':utc(),'script':D.identity(HERE),'driver':D.identity(DRIVER),'frame':str(D.FRAME)})
    rows=[]
    for mode in ('normal','timeout','detached'):
        row=one(out/mode,mode);rows.append(row)
        if not row['passed']:
            save(out/'result.json',{'passed':False,'controls':rows,'namespace':'NOT PERFORMED after sandbox refusal'})
            return 1
    namespace=namespace_control(out/'namespace')
    result={'classification':'TESTED finite actual sandbox qualification','controls':rows,
            'namespace':namespace,'passed':all(r['passed'] for r in rows) and namespace['passed'],
            'non_claims':['No original binary/native/actor/protected payload executed.','Observed finite cleanup does not prove arbitrary descendant semantics.']}
    save(out/'result.json',result)
    return 0 if result['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
