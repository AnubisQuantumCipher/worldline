import datetime,hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
ROOT=Path.cwd(); OUT=ROOT/'records/phase1-blockers/resume-20261015-v1/invocation-id-compile-result-v1';OUT.mkdir(exist_ok=False)
OBJECTS=ROOT/'obj/core/phase1-d46-compile-v1'
if OBJECTS.exists():raise SystemExit('Refuse nonfresh object directory')
if (ROOT/'obj').is_symlink() or (ROOT/'obj/core').is_symlink():raise SystemExit('Refuse symlink output ancestry')
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
private=ROOT/'scratch/old-analysis/private-sparklib-experiment/lib/gnat'
watched=[ROOT/'lib/libworldline_core.so',ROOT/'obj/core/worldline-evaluation_role_native.o',ROOT/'obj/core/worldline-evaluation_role_native.ali']
watched += [p for name in ('sparklib_obj','sparklib_lib') for p in (private/name).rglob('*') if p.is_file()]
def identities():return {str(p.relative_to(ROOT)):sha(p) for p in watched if p.is_file()}
env=dict(os.environ);env['GPR_PROJECT_PATH']=str(private)+':'+env.get('GPR_PROJECT_PATH','');env['WORLDLINE_BUILD']='checks';env.pop('GPR_TOOL',None)
command=['gprbuild','-p','-P','core/worldline_core_sources.gpr','-c','-u','worldline-evaluation_role_native.adb','--subdirs=phase1-d46-compile-v1','-j2','-XSPARKLIB_MODE=full','-XSPARKLIB_BUILD=Production','-XSPARKLIB_LIBRARY_TYPE=static','-XSPARKLIB_INSTALLED=True','-XWORLDLINE_PRIVATE_SPARKLIB_PREBUILT=True','-cargs:Ada','-fPIC']
argv=['bwrap','--die-with-parent','--ro-bind','/','/','--dev','/dev','--proc','/proc','--bind',str(ROOT),str(ROOT),'--bind',env['TMPDIR'],'/tmp','--chdir',str(ROOT),*command]
receipt={'started_utc':stamp(),'commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'argv':argv,'gpr_argv':command,'cwd':str(ROOT),'environment':{k:env.get(k) for k in ('PATH','GPR_PROJECT_PATH','WORLDLINE_BUILD','GPR_TOOL','TMPDIR','XDG_CACHE_HOME')},'source_sha256':sha(ROOT/'core/worldline-evaluation_role_native.adb'),'method_sha256':sha(Path(__file__)),'scope':'Focused changed Ada unit compilation only, not link, proof, runtime or full F1','watched_before':identities()}
for tool in ('gnatls','gprbuild','gcc'):
 resolved=Path(shutil.which(tool)).resolve()
 r=subprocess.run([tool,'--version'],capture_output=True,text=True);receipt[tool]={'path':str(resolved),'sha256':sha(resolved),'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
(OUT/'launch.json').write_text(json.dumps(receipt,indent=2)+'\n')
with (OUT/'stdout').open('xb') as stdout,(OUT/'stderr').open('xb') as stderr:r=subprocess.run(argv,env=env,stdout=stdout,stderr=stderr)
receipt.update(ended_utc=stamp(),exit_code=r.returncode,watched_after=identities(),source_sha256_after=sha(ROOT/'core/worldline-evaluation_role_native.adb'),stdout_sha256=sha(OUT/'stdout'),stderr_sha256=sha(OUT/'stderr'))
receipt['watched_unchanged']=receipt['watched_before']==receipt['watched_after']
receipt['artifacts']={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'obj/core/phase1-d46-compile-v1').glob('*') if p.is_file()}
ali=ROOT/'obj/core/phase1-d46-compile-v1/worldline-evaluation_role_native.ali'
receipt['assertions_enabled_ali']=('A -gnata' in ali.read_text().splitlines()) if ali.is_file() else None
object_file=OBJECTS/'worldline-evaluation_role_native.o'
receipt['expected_artifacts_present']=all(p.is_file() and not p.is_symlink() for p in (object_file,ali))
receipt['validation_passed']=(r.returncode==0 and receipt['watched_unchanged'] and receipt['expected_artifacts_present'] and receipt['assertions_enabled_ali'] is True and receipt['source_sha256']==receipt['source_sha256_after'])
(OUT/'result.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'result':str(OUT/'result.json'),'exit_code':r.returncode,'watched_unchanged':receipt['watched_unchanged'],'assertions_enabled_ali':receipt['assertions_enabled_ali']}))
sys.exit(0 if receipt['validation_passed'] else (r.returncode or 125))
