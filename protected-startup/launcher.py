"""Source-only entry through the approved early helper under -I -S -B.

No environment-derived import root. Complete source/native/tool identity is
checked by the already-active import lease and StartupLease before construction.
The root-private descriptor is the owner's explicit installation selection.
"""
import sys
_source_module = sys.modules.get('_worldline_approved_source_loader')
if type(_source_module) is not type(sys):
    raise SystemExit('PROTECTED_EARLY_APPROVED_SOURCE_ENTRY_REQUIRED')
_source_lease = _source_module.current()
if type(_source_lease) is not _source_module.ApprovedSourceLease:
    raise SystemExit('PROTECTED_ACTUAL_APPROVED_SOURCE_ENTRY_REQUIRED')
_source_lease.check()
import json,os,pathlib,stat

def main():
    if os.geteuid()!=0 or len(sys.argv)!=2 or not sys.flags.isolated or not sys.flags.no_site or not sys.dont_write_bytecode:
        raise SystemExit('PROTECTED_ISOLATED_OPERATOR_ENTRY_REQUIRED')
    descriptor=pathlib.Path(sys.argv[1])
    if not descriptor.is_absolute():raise SystemExit('PROTECTED_DESCRIPTOR_ABSOLUTE_REQUIRED')
    for path in (*reversed(descriptor.parents),descriptor):
        info=path.lstat()
        if stat.S_ISLNK(info.st_mode) or info.st_uid!=0 or stat.S_IMODE(info.st_mode)&0o022:
            raise SystemExit('PROTECTED_DESCRIPTOR_CUSTODY_REQUIRED')
    value=json.loads(_source_lease.file(str(descriptor), ('DATA',)))
    runtime=value['runtime']
    paths=[pathlib.Path(runtime['worldline_source'])/'runtime',
           pathlib.Path(runtime['gate_source']).parent,pathlib.Path(runtime['principal_source']).parent]
    for path in paths:
        info=path.lstat()
        if not path.is_absolute() or stat.S_ISLNK(info.st_mode) or info.st_uid!=0 or stat.S_IMODE(info.st_mode)&0o022:
            raise SystemExit('PROTECTED_IMPORT_ROOT_REQUIRED')
    sys.path[:0]=[str(path) for path in paths]
    _source_lease.check()
    from worldline.protected_startup import serve
    try:serve(descriptor)
    except Exception as exc:
        # If installation custody itself is unavailable, no authority socket is
        # exposed. The supervisor retains a named diagnostic on standard error.
        print(json.dumps({'state':'QUARANTINED','release_gate':'BLOCKED','reason':str(exc)},sort_keys=True),file=sys.stderr)
        raise SystemExit('PROTECTED_STARTUP_REFUSED') from exc

if __name__=='__main__':main()
