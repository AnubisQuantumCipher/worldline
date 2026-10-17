#!/usr/bin/env python3
"""Top-level unittest subprocess audit receipts; no child hook injection."""
from __future__ import annotations
import argparse,hashlib,json,os,runpy,sys,time,traceback,uuid
from pathlib import Path

def canonical_unit(value):
    if not isinstance(value,str) or not value.startswith('worldline-') or not value.endswith('.service'):return False
    try:ident=uuid.UUID(value[len('worldline-'):-len('.service')])
    except ValueError:return False
    return ident.version==4 and 'worldline-'+str(ident)+'.service'==value

# This parser recognizes only original production forms and the unchanged real
# supervision collision control. Unknown options are evidence gaps, never a
# reason to change, suppress, or reinterpret the subprocess call.
SYSTEMD_RUN = '/usr/bin/systemd-run'
def unit_intent(executable,argv):
    if type(executable) is not str or executable != SYSTEMD_RUN:return None
    if type(argv) not in (list,tuple) or not argv or not all(type(x) is str for x in argv):return None
    if argv[0] != SYSTEMD_RUN:return None
    flags={'--user','--collect','--quiet','--pty','--pipe'}
    values={'--unit','-u','--description','--service-type','--property','-p'}
    names=[];user=False;index=1;separator=False
    while index<len(argv):
        arg=argv[index]
        if arg=='--':separator=True;index+=1;break
        if not arg.startswith('-'):break
        if arg in flags:
            if arg=='--user':user=True
            index+=1;continue
        option,equal,value=arg.partition('=')
        if option not in values:return None
        if not equal:
            index+=1
            if index>=len(argv):return None
            value=argv[index]
        if not value:return None
        if option in ('--unit','-u'):names.append(value)
        index+=1
    if not user or len(names)!=1 or not canonical_unit(names[0]) or index>=len(argv):return None
    command=list(argv[index:])
    if not command[0].startswith('/'):return None
    return {'unit':names[0],'exec_argv':command,'systemd_run_argv':list(argv),
            'launch_form':'explicit separator' if separator else 'first positional executable',
            'parser_scope':'exact supported original option grammar; unknown form unobserved'}

def install_audit(path,mode):
    owner=os.getpid();failures=[]
    fd=os.open(path,os.O_WRONLY|os.O_APPEND|os.O_CREAT,0o600)
    # Keep the original descriptor open through unittest; no wrapper or hook is
    # installed in a child interpreter. Forked descendants also fail this PID test.
    def hook(event,values):
        if event!='subprocess.Popen' or os.getpid()!=owner:return
        try:
            # Exact built-in types only: observing must not invoke a supplied
            # __str__, __fspath__, iterator override, or custom JSON fallback.
            if type(values) is not tuple or len(values)!=4:
                failures.append('Opaque subprocess audit arguments');return
            executable,argv,cwd,env=values
            plain_argv=type(argv) in (tuple,list) and all(type(x) is str for x in argv)
            plain_executable=type(executable) is str
            plain_cwd=cwd is None or type(cwd) is str
            if not (plain_argv and plain_executable and plain_cwd):
                failures.append('Opaque subprocess value; observation incomplete')
            receipt={'event':event,'pid':owner,'monotonic_ns':time.monotonic_ns(),
                     'executable':executable if plain_executable else None,
                     'argv':list(argv) if plain_argv else {'unobserved':'non-builtin-string argv'},
                     'cwd':cwd if plain_cwd else None,'intent':unit_intent(executable,argv),
                     'scope':'top-level test process only; not child daemon instrumentation'}
            payload=(json.dumps(receipt,sort_keys=True)+'\n').encode()
            view=memoryview(payload)
            while view:
                written=os.write(fd,view)
                if written<=0:raise OSError('audit receipt write incomplete')
                view=view[written:]
            os.fsync(fd)
        except BaseException as error:
            # Preserve original Popen, values and exception behavior. Evidence
            # failure independently makes audit qualification/run nonpassing.
            failures.append(type(error).__name__)
    if mode=='audit':sys.addaudithook(hook)
    return failures,fd

def main():
    p=argparse.ArgumentParser();p.add_argument('--audit',choices=('plain','audit'),required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('unittest',nargs=argparse.REMAINDER)
    args=p.parse_args();argv=args.unittest[1:] if args.unittest[:1]==['--'] else args.unittest
    args.out.mkdir(parents=True,exist_ok=False)
    with open(SYSTEMD_RUN,'rb') as stream:systemd_sha=hashlib.file_digest(stream,'sha256').hexdigest()
    (args.out/'audit-start.json').write_text(json.dumps({'pid':os.getpid(),'mode':args.audit,
        'systemd_run':SYSTEMD_RUN,'systemd_run_sha256':systemd_sha,'entry_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},sort_keys=True,indent=2)+'\n')
    failures,fd=install_audit(args.out/'popen.jsonl',args.audit)
    status=1;exception=None
    try:
        sys.argv=['python3 -m unittest',*argv]
        runpy.run_module('unittest',run_name='__main__')
        status=0
    except SystemExit as error:
        status=error.code if isinstance(error.code,int) else (0 if error.code is None else 1)
    except BaseException as error:
        exception=type(error).__name__+': '+str(error)
        (args.out/'exception.txt').write_text(traceback.format_exc())
    finally:
        os.fsync(fd);os.close(fd)
        (args.out/'audit-result.json').write_text(json.dumps({'pid':os.getpid(),'mode':args.audit,'unittest_argv':argv,'unittest_exit':status,'audit_failures':failures,'exception':exception,
          'qualification':'bounded instrumentation observation only; universal transparency UNVERIFIED','child_instrumentation':'none'},sort_keys=True,indent=2)+'\n')
    return status if not failures and exception is None else 1
if __name__=='__main__':raise SystemExit(main())
