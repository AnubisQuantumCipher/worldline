#!/usr/bin/env python3
"""Prepared full aggregate + imported-source proof driver; no work on import.

Coordinator must run through scripts/phase1_heavy.py. Does not generate a success
manifest: a fresh complete proof must separately pass all existing manifest gates.
"""
from __future__ import annotations
import argparse,datetime,hashlib,json,os,re,shutil,subprocess,sys,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OWN=ROOT/'scratch/old-analysis'
PRIVATE=None
MANIFEST=None
FRAME=None
FREEZE=None
BUILD=None
from frozen_source_v2 import validate as validate_frozen_source
SCENARIO=['-XWORLDLINE_BUILD=checks','-XSPARKLIB_MODE=full','-XSPARKLIB_BUILD=Production',
          '-XSPARKLIB_LIBRARY_TYPE=static','-XSPARKLIB_INSTALLED=True']

def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,value):
    with p.open('x') as f:json.dump(value,f,sort_keys=True,indent=2,default=str);f.write('\n')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def run(argv,env):return subprocess.run(argv,cwd=FRAME,env=env,text=True,capture_output=True)
def sources():
    paths=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    return {p:sha(FRAME/p) for p in paths if p and Path(p).suffix in ('.ads','.adb','.gpr','.c','.h','.py','.sh') and (FRAME/p).is_file()}
def cgroup():
    entry=next(x[3:] for x in Path('/proc/self/cgroup').read_text().splitlines() if x.startswith('0::'))
    p=Path('/sys/fs/cgroup')/entry.lstrip('/')
    return {'path':str(p),**{n:(p/n).read_text().strip() for n in ('memory.max','memory.swap.max','memory.peak','memory.events')}}
def report_paths(subdir):
    values=set()
    for folder in (FRAME/'obj',PRIVATE/'lib/gnat'):
        if folder.exists():
            for p in folder.rglob('*'):
                if p.is_file() and (subdir in p.parts or p.is_relative_to(PRIVATE/'lib/gnat/proof')) and (p.suffix in ('.spark','.json','.out','.stderr','.stdout','.why','.mlw') or p.name in ('gnatprove.out','gnatprove.json')):
                    values.add(p)
    return sorted(values)

def main():
    global PRIVATE,MANIFEST,FRAME,FREEZE,BUILD
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--expected-commit',required=True)
    parser.add_argument('--subdir',required=True)
    parser.add_argument('--freeze-record',type=Path,required=True)
    parser.add_argument('--frame',type=Path,required=True)
    parser.add_argument('--build-manifest',type=Path,required=True)
    parser.add_argument('--dependency-template',type=Path,required=True)
    parser.add_argument('--dependency-manifest',type=Path,required=True)
    args=parser.parse_args();out=args.out.resolve()
    FRAME=args.frame.resolve();FREEZE=args.freeze_record.resolve();BUILD=args.build_manifest.resolve()
    TEMPLATE=args.dependency_template.resolve();MANIFEST=args.dependency_manifest.resolve();PRIVATE=out/'private-sparklib'
    if any(not value.is_relative_to(ROOT) for value in (FRAME,FREEZE,BUILD,TEMPLATE,MANIFEST)):
        raise SystemExit('Explicit frame and dependency inputs must remain inside this worktree')
    if not out.is_relative_to(OWN) or not re.fullmatch(r'phase1-[a-z0-9-]+',args.subdir):
        raise SystemExit('Use fresh owned scratch output and phase1 subdirectory')
    if not re.fullmatch(r'[a-f0-9]{40}',args.expected_commit):raise SystemExit('Expected commit must be exact')
    out.mkdir(parents=True,exist_ok=False)
    metadata={'claim_class':'MEASURED','status':'UNVERIFIED','started_utc':now(),'argv':sys.argv,'cwd':str(FRAME),'frame':str(FRAME),'freeze_record':str(FREEZE),'build_manifest':str(BUILD),'dependency_template':str(TEMPLATE),'fresh_dependency':str(PRIVATE),
       'driver_sha256':sha(Path(__file__)),'private_manifest_sha256':sha(MANIFEST),
       'phase1_acceptance':'NOT PERFORMED','independent_acceptance':'NOT PERFORMED',
       'original_retirement_gate':'FAILED-OPEN; this run cannot relabel Off implementations as proved',
       'manifest_generated':False,'subdir':args.subdir,'required_commit':args.expected_commit}
    result=None;start_sources=None;dependency=None;library=ROOT/'lib/libworldline_core.so'
    try:
        current=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        metadata['commit']=current
        if current!=args.expected_commit:raise RuntimeError('Frozen commit mismatch')
        diff=subprocess.check_output(['git','diff','HEAD','--'],cwd=ROOT)
        (out/'tracked.diff').write_bytes(diff)
        if diff:raise RuntimeError('Tracked source differs from frozen commit')
        metadata['frozen_identity_before']=validate_frozen_source(args.expected_commit,FREEZE,FRAME,BUILD)
        start_sources=sources();metadata['source_hashes_before']=start_sources
        if not library.is_file():raise RuntimeError('Same-source built library is missing')
        metadata['library_sha256_before']=sha(library)
        dependency=json.loads(MANIFEST.read_text())
        if not dependency.get('all_source_bytes_match_installed'):raise RuntimeError('Dependency identity absent')
        if not dependency.get('source_hashes') or not dependency.get('project_hashes'):
            raise RuntimeError('Missing or empty original dependency roster')
        installed=Path(dependency['installed_root']).resolve(strict=True)
        if sha(installed/'lib/gnat/sparklib.gpr')!=dependency['installed_project_sha256']:
            raise RuntimeError('Installed dependency project pin differs')
        for p,h in dependency['source_hashes'].items():
            if sha(installed/p)!=h:raise RuntimeError('Installed dependency source pin differs: '+p)
        if PRIVATE.exists():raise RuntimeError('Fresh dependency output already exists')
        PRIVATE.mkdir()
        for p,h in {**dependency['source_hashes'],**dependency['project_hashes']}.items():
            if Path(p).is_absolute() or '..' in Path(p).parts:
                raise RuntimeError('Unsafe dependency roster path')
            if sha(TEMPLATE/p)!=h:raise RuntimeError('Private template source/project identity changed: '+p)
            destination=PRIVATE/p;destination.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(TEMPLATE/p,destination)
            if sha(destination)!=h:raise RuntimeError('Fresh private dependency copy differs: '+p)
        metadata['dependency_adaptation']=dependency['project_diff']
        metadata['dependency_materialization']='Fresh copy of all exact pinned source/project files only; no old proof/build artifacts copied; genuine GNATprove Externally_Built branch remains False'
        save(out/'fresh-dependency.json',{'template':str(TEMPLATE),'manifest':str(MANIFEST),'manifest_sha256':sha(MANIFEST),'private':str(PRIVATE),'source_hashes':dependency['source_hashes'],'project_hashes':dependency['project_hashes'],'project_diff':dependency['project_diff'],'all_installed_source_pins_verified':True})
        metadata['private_source_and_project_hashes']={**dependency['source_hashes'],**dependency['project_hashes']}
        metadata['active_imported_ada_roster']=dependency['source_selection']['active_ada_files']
        metadata['dependency_boundary']=dependency['boundary']
        metadata['existing_imported_off_markers']={p:[{'line':i,'text':line} for i,line in enumerate((PRIVATE/p).read_text().splitlines(),1) if re.search(r'\bSPARK_Mode\s*(?:=>|\()\s*Off\b',line,re.I)] for p in metadata['active_imported_ada_roster']}
        metadata['existing_imported_off_markers']={p:v for p,v in metadata['existing_imported_off_markers'].items() if v}
        tmp=Path(os.environ.get('TMPDIR','')).resolve()
        if not os.environ.get('TMPDIR') or not tmp.is_relative_to(ROOT) or not tmp.is_dir():raise RuntimeError('Missing worktree-local runner TMPDIR')
        metadata['scope_before']=cgroup()
        if metadata['scope_before']['memory.max']!='8589934592' or metadata['scope_before']['memory.swap.max']!='0':raise RuntimeError('Approved unchanged 8G/zero-swap scope required')
        if report_paths(args.subdir):raise RuntimeError('Prior output exists for this proof directory; use a fresh private dependency and subdir')
        env=dict(os.environ);env.pop('GPR_TOOL',None)
        env['GPR_PROJECT_PATH']=str(PRIVATE/'lib/gnat')
        env['PYTHONDONTWRITEBYTECODE']='1';env['PYTHONPATH']=str(FRAME/'runtime')
        for name,relative in [('HOME','home'),('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data'),('XDG_STATE_HOME','state')]:
            directory=out/relative;directory.mkdir();env[name]=str(directory)
        metadata['environment']={key:env[key] for key in ('GPR_PROJECT_PATH','PYTHONDONTWRITEBYTECODE','PYTHONPATH','HOME','TMPDIR','XDG_CONFIG_HOME','XDG_CACHE_HOME','XDG_DATA_HOME','XDG_STATE_HOME')}
        metadata['GPR_TOOL']='not set by driver; genuine executable selects its project branch'
        versions={}
        for tool in ('gnat','gnatprove','gprbuild'):
            p=run([tool,'--version'],env);versions[tool]={'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
            if p.returncode:raise RuntimeError('Toolchain version probe failed: '+tool)
        save(out/'versions.json',versions)
        options=['-P','core/worldline_core.gpr','-U','--mode=all','--level=3','--report=all','--checks-as-errors=on','--proof-warnings=on','--memlimit=1024','--timeout=60','-j2','--subdirs='+args.subdir,*SCENARIO]
        command=['gnatprove',*options]
        isolated=['bwrap','--die-with-parent','--ro-bind','/','/','--dev','/dev','--proc','/proc','--bind',str(ROOT),str(ROOT),'--chdir',str(FRAME),*command]
        metadata['gnatprove_argv']=command;metadata['isolated_argv']=isolated
        save(out/'launch.json',metadata)
        with (out/'stdout').open('xb') as stdout,(out/'stderr').open('xb') as stderr:
            result=subprocess.run(isolated,cwd=FRAME,env=env,stdout=stdout,stderr=stderr)
        metadata['exit_code']=result.returncode
        reports=report_paths(args.subdir)
        metadata['reports']={str(p.relative_to(ROOT)):sha(p) for p in reports}
        summaries=[p for p in reports if p.name=='gnatprove.out']
        metadata['fresh_summary_paths']=[str(p.relative_to(ROOT)) for p in summaries]
        if result.returncode!=0:
            metadata['status']='FAILED-OPEN full proof command returned nonzero'
            return 1
        if len(summaries)!=1:raise RuntimeError('Expected one actual fresh aggregate summary; missing or ambiguous reports cannot pass')
        sys.path.insert(0,str(FRAME/'runtime'))
        from worldline.proof_manifest import parse_summary,contract_problems,expected_units,REQUIRED_PROVED,UNANALYZED_BOUNDARY,MINIMUM_CHECKS
        parsed=parse_summary(summaries[0].read_text())
        metadata['strict_summary']=parsed
        problems=contract_problems(FRAME)
        if parsed['unproved'] or parsed['justified']:problems.append('Summary retains unproved or justified checks')
        if parsed['total']<MINIMUM_CHECKS:problems.append('Pinned proof floor not reached')
        units=parsed['units'];subprograms=parsed['subprograms']
        if not units or not subprograms:problems.append('Summary coverage empty')
        missing=sorted(expected_units(FRAME)-set(units))
        if missing:problems.append('Required units absent: '+', '.join(missing))
        missing_subprograms=[name for name in REQUIRED_PROVED if name not in subprograms]
        if missing_subprograms:problems.append('Required subprograms absent: '+', '.join(missing_subprograms))
        for unit,counts in units.items():
            if counts['analyzed']!=counts['available'] or (unit not in UNANALYZED_BOUNDARY and counts['available']==0):problems.append('Unit not fully analyzed: '+unit)
        for unit in UNANALYZED_BOUNDARY:
            if unit not in units:problems.append('Declared existing boundary absent: '+unit)
        metadata['preliminary_gate_problems']=problems
        metadata['status']='FAILED-OPEN full proof or coverage gate' if problems else 'TESTED command and preliminary summary gates; original manifest screening still REQUIRED'
        # Deliberately no proof-manifest write: original source screening and
        # shared manifest verifier must both pass on this exact summary later.
        return 1 if problems else 0
    except BaseException as error:
        metadata['status']='FAILED-OPEN proof driver or prerequisite'
        metadata['error']={'type':type(error).__name__,'message':str(error)}
        (out/'traceback.txt').write_text(traceback.format_exc())
        return 1
    finally:
        metadata['finished_utc']=now()
        metadata['commit_after']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        metadata['source_unchanged']=start_sources is not None and sources()==start_sources
        metadata['library_unchanged']=library.is_file() and sha(library)==metadata.get('library_sha256_before')
        metadata['private_unchanged']=dependency is not None and all((PRIVATE/p).is_file() and sha(PRIVATE/p)==h for p,h in {**dependency['source_hashes'],**dependency['project_hashes']}.items())
        try:
            metadata['frozen_identity_after']=validate_frozen_source(args.expected_commit,FREEZE,FRAME,BUILD)
        except BaseException as error:
            metadata['frozen_identity_after_error']=repr(error)
        identity_changed='frozen_identity_after_error' in metadata or metadata['commit_after']!=args.expected_commit or not all(metadata[k] for k in ('source_unchanged','library_unchanged','private_unchanged'))
        if identity_changed:metadata['status']='FAILED-OPEN source or library identity changed or not established'
        save(out/'result.json',metadata)
        print(json.dumps({'out':str(out),'status':metadata['status'],'exit_code':metadata.get('exit_code'),'manifest_generated':False}))
        if identity_changed:raise SystemExit(1)

if __name__=='__main__':raise SystemExit(main())
