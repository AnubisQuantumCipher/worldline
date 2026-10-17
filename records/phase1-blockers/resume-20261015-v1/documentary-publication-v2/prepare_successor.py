"""Add-only successor after exact metadata-size disposition; no staging."""
from datetime import datetime,timezone
import hashlib,json,re,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
original_path=OUT/'selection.json';original=json.loads(original_path.read_text())
review_path=ROOT/'scratch/reviewer2/resume-20261015-v1/D66-selection-size-disposition-review-v1.json'
review=json.loads(review_path.read_text())
if review['selection_sha256']!=sha(original_path) or review['finite_audit_sha256']!=sha(OUT/'finite-audit-v1.json'):
 raise RuntimeError('Exact reviewed selection/audit identity changed')
approved={row['path']:(row['sha256'],row['bytes']) for row in review['size_disposition']}
flags={row['path']:row for row in original['flags']}
if set(approved)!=set(flags) or any(row['kind']!='oversized' for row in flags.values()):raise RuntimeError('Unreviewed initial flag')
for expected in original['rows']:
 path=ROOT/expected['path']
 if sha(path)!=expected['sha256'] or path.stat().st_size!=expected['bytes']:raise RuntimeError('Original selected bytes changed before append')
append='\nD66 exact metadata-size disposition: actual GPT-6.1 D66-selection-size-disposition-review-v1.json CONCUR permits only the following immutable own metadata blobs, preserving the original selector exit1 and oversized flags. No global publication threshold or acceptance/resource/proof/runtime condition changes.\n'
for row in review['size_disposition']:
 append+='- `'+row['path']+'`: bytes `'+str(row['bytes'])+'`, SHA256 `'+row['sha256']+'`; parsed own command/source/resource metadata, retained whole.\n'
append+='Finite audit reports no other findings in its assigned UTF8/NUL/token/path/container checks; this is not exhaustive secret/privacy/license certification. Exact successor and staged bytes still require actual GPT-6.1 review before commit/push.\n'
append_path=OUT/'D66-size-disposition-append.md'
with append_path.open('x') as stream:stream.write(append)
doc=ROOT/'docs/decisions.md'
with doc.open('a') as stream:stream.write(append)
rows=[]
for expected in original['rows']:
 path=ROOT/expected['path'];data=path.read_bytes()
 if expected['path']=='docs/decisions.md':
  if not data.endswith(append.encode()) or hashlib.sha256(data[:-len(append.encode())]).hexdigest()!=expected['sha256']:
   raise RuntimeError('Unexpected documentary change outside exact append')
 elif sha(path)!=expected['sha256']:raise RuntimeError('Original selected bytes changed after append')
 rows.append({'path':expected['path'],'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
additions=[original_path,OUT/'finite_audit_v1.py',OUT/'finite-audit-v1.json',append_path,review_path,Path(__file__).resolve()]
known={row['path'] for row in rows}
for path in additions:
 relative=str(path.relative_to(ROOT))
 if relative not in known:
  rows.append({'path':relative,'bytes':path.stat().st_size,'sha256':sha(path)});known.add(relative)
patterns={
 'private_key':rb'-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----',
 'github_token':rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})',
 'openai_token':rb'sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{40,}',
 'aws_access_key':rb'AKIA[0-9A-Z]{16}',
 'slack_token':rb'xox[baprs]-[A-Za-z0-9-]{25,}',
 'google_api_key':rb'AIza[A-Za-z0-9_-]{30,}',
 'hf_token':rb'hf_[A-Za-z0-9]{30,}'
}
findings=[]
for row in rows:
 path=ROOT/row['path'];data=path.read_bytes()
 if path.is_symlink() or not path.is_file():raise RuntimeError('Nonregular selected path')
 try:data.decode('utf8')
 except UnicodeDecodeError:findings.append({'path':row['path'],'kind':'nonUTF8'})
 if b'\0' in data:findings.append({'path':row['path'],'kind':'NUL'})
 for name,pattern in patterns.items():
  if re.search(pattern,data):findings.append({'path':row['path'],'kind':name})
 if len(data)>1000000 and approved.get(row['path'])!=(row['sha256'],row['bytes']):findings.append({'path':row['path'],'kind':'unreviewed_oversized'})
receipt={'utc':datetime.now(timezone.utc).isoformat(),'command':sys.orig_argv,'method_sha256':sha(Path(__file__)),
 'original_selection_sha256':sha(original_path),'size_disposition_review':{'path':str(review_path.relative_to(ROOT)),'sha256':sha(review_path)},
 'scope':'Add-only finite successor; original rows retained, only exact D66 decision append changed, approved size findings preserved',
 'rows':sorted(rows,key=lambda row:row['path']),'original_flags_retained':original['flags'],'exact_approved_size_dispositions':review['size_disposition'],
 'documentary_append':{'path':str(append_path.relative_to(ROOT)),'sha256':sha(append_path)},'findings':findings,
 'staging_rule':'This manifest itself is excluded from its own row hashes; stage it explicitly with all rows after separate actual successor review. No other paths.',
 'boundary':'No staging/commit/push; raw failed scans/logs preserved. Finite scan not exhaustive. Actual successor and exact-index review mandatory.'}
with (OUT/'successor-selection-v1.json').open('x') as stream:json.dump(receipt,stream,indent=2);stream.write('\n')
print(json.dumps({'output':str(OUT/'successor-selection-v1.json'),'rows':len(rows),'findings':findings}))
raise SystemExit(1 if findings else 0)
