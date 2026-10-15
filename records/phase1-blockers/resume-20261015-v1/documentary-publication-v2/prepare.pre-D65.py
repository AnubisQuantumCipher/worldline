"""Select the settled D53-D64 documentary epoch, excluding private storage catalogs and active compiler trees."""
import datetime, hashlib, json, re, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'records/phase1-blockers/resume-20261015-v1'
OUT=Path(__file__).resolve().parent
paths={ROOT/p for p in ('docs/decisions.md','docs/phase1-progress.md','OPEN-ISSUES.md')}
for name in ('settled-storage-selection-v2.json',): paths.add(BASE/name)
paths.update(BASE.glob('shared-parser-v2-owned-scope-observation-v*.json'))
frontend=ROOT/'scratch/final-gates/resume-20261015-v1/finalizable-frontend-research-v1'
for name in ('research.md','research.json','installed-version-readback.json','gcc-version.stdout','gcc-version.stderr'):
 paths.add(frontend/name)
paths.update(frontend.glob('*.receipt.json'))
for candidate_name in ('shared-json-parser-v1','shared-json-parser-v2'):
 settled=json.loads((BASE/candidate_name/'parent/result.json').read_text())
 if settled.get('own_scope_terminal') is not True: raise RuntimeError('Candidate is not settled: '+candidate_name)
for directory in (BASE/'storage-settled-v2',BASE/'resource-policy-library-v1',BASE/'storage-settled-v3'):
 for p in directory.rglob('*'):
  if not p.is_file(): continue
  rel=p.relative_to(directory)
  if any(part in ('tmp','cache') for part in rel.parts): continue
  if p.name=='storage-preflight.stdout': continue
  paths.add(p)
for candidate_name in ('shared-json-parser-v1','shared-json-parser-v2'):
 directory=BASE/candidate_name
 for item in directory.iterdir():
  if item.is_file(): paths.add(item)
 for source_dir in ('src','resource-current-D56','resource-historical-original'):
  paths.update(p for p in (directory/source_dir).iterdir() if p.is_file())
 for result_dir in ('parent','scope','results'):
  paths.update(p for p in (directory/result_dir).iterdir() if p.is_file() and p.name!='storage-preflight.stdout')
 report=directory/'obj-current-D56/gnatprove/gnatprove.out'
 if report.is_file():
  target=OUT/(candidate_name+'-gnatprove.out')
  with target.open('xb') as f:f.write(report.read_bytes())
  paths.add(target)
for name in ('transaction-roster-proposal-v1',):
 paths.update(p for p in (BASE/name).iterdir() if p.is_file())
for name in ('canonical-material-interface-v1','resource-policy-library-recipe-v1','shared-parser-preflight-v1'):
 paths.update(p for p in (ROOT/'scratch/final-gates/resume-20261015-v1'/name).iterdir() if p.is_file())
review=ROOT/'scratch/reviewer2/resume-20261015-v1'
for pattern in ('D54-*.json','D55-*.json','D59-*.json','D60-*.json','D61-*.json','D62-*.json','D63-*.json','D53-D62-documentary-preparation-sanity-review-v1.json','shared-parser-functional-proof-readiness-review-v1.json','finalizable-frontend-bounded-research-review-v1.json','shared-json-parser-*.json','canonical-material-baseline-conflict-review-v1.json'):
 paths.update(review.glob(pattern))
for p in (ROOT/'records/phase1-blockers/github-checkpoint-publication-v8').iterdir():
 if p.is_file(): paths.add(p)
paths.add(Path(__file__).resolve())
patterns={'privatekey':rb'-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----','githubtoken':rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})','openaitoken':rb'sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{40,}','awsaccess':rb'AKIA[0-9A-Z]{16}'}
rows=[];flags=[]
for p in sorted(paths):
 if p.is_symlink() or not p.is_file() or not p.is_relative_to(ROOT): raise RuntimeError('Invalid selection '+str(p))
 data=p.read_bytes();rel=str(p.relative_to(ROOT))
 if b'\0' in data: flags.append({'path':rel,'kind':'NUL'})
 if len(data)>1000000: flags.append({'path':rel,'kind':'oversized','bytes':len(data)})
 try:data.decode('utf8')
 except UnicodeDecodeError:flags.append({'path':rel,'kind':'nonUTF8'})
 for name,pattern in patterns.items():
  if re.search(pattern,data):flags.append({'path':rel,'kind':name})
 rows.append({'path':rel,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'scope':'D53-D64 documentary/settled finite execution evidence; no new product source or acceptance','rows':rows,'flags':flags,'excluded':['full host storage catalogs','generated objects/libraries/binders','upstream raw source bodies','user attachments','generated candidate compiler/prover object trees except exact plain report copies'],'limitations':['finite scan is not exhaustive secret detection','metadata/hash correspondence is not correctness','internal review is not independent acceptance']}
with (OUT/'selection.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
print(json.dumps({'selection':str(OUT/'selection.json'),'rows':len(rows),'flags':flags}))
if flags:raise SystemExit(1)
