#!/usr/bin/env python3
"""Prepared top-level audit entry for the unchanged decisive script.

No child interpreter or daemon hook is installed. This runpy carrier requires
its own finite plain/audited qualification; unittest qualification alone is not
evidence that the decisive instrument is unaffected.
"""
from __future__ import annotations
import argparse,hashlib,json,os,runpy,sys,traceback
from pathlib import Path
from runtime_audit_entry import install_audit

def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--script',type=Path,required=True)
    p.add_argument('--script-sha256',required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('arguments',nargs=argparse.REMAINDER)
    args=p.parse_args();argv=args.arguments[1:] if args.arguments[:1]==['--'] else args.arguments
    script=args.script.resolve(strict=True)
    if sha(script)!=args.script_sha256:raise SystemExit('Decisive script identity mismatch')
    args.out.mkdir(parents=True,exist_ok=False)
    start={'pid':os.getpid(),'script':str(script),'script_sha256':sha(script),
           'script_argv':argv,'entry_sha256':sha(__file__),
           'audit_helper_sha256':sha(Path(__file__).with_name('runtime_audit_entry.py')),
           'systemd_run_sha256':sha('/usr/bin/systemd-run'),
           'scope':'top-level decisive process only; no child instrumentation'}
    (args.out/'audit-start.json').write_text(json.dumps(start,indent=2,sort_keys=True)+'\n')
    failures,fd=install_audit(args.out/'popen.jsonl','audit')
    status=1;exception=None
    try:
        # Match normal script argv/import precedence. The extra already-loaded
        # carrier modules remain an explicitly qualified instrumentation change.
        sys.argv=[str(script),*argv]
        sys.path[0]=str(script.parent)
        runpy.run_path(str(script),run_name='__main__')
        status=0
    except SystemExit as error:
        status=error.code if isinstance(error.code,int) else (0 if error.code is None else 1)
    except BaseException as error:
        exception={'type':type(error).__name__,'message':str(error)}
        (args.out/'exception.txt').write_text(traceback.format_exc())
    finally:
        try:os.fsync(fd);os.close(fd)
        except OSError as error:failures.append(type(error).__name__)
        outcome={**start,'script_exit':status,'audit_failures':failures,'exception':exception,
                 'native_entry':'UNVERIFIED','independent_acceptance':'NOT PERFORMED'}
        (args.out/'audit-result.json').write_text(json.dumps(outcome,indent=2,sort_keys=True)+'\n')
    return status if not failures and exception is None else 1

if __name__=='__main__':raise SystemExit(main())
