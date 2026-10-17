"""Finite publication-byte/path audit; does not stage, commit or publish."""
from datetime import datetime,timezone
import hashlib,json,re,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
selection_path=OUT/'selection.json'
selection=json.loads(selection_path.read_text())
patterns={
 'private_key':rb'-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----',
 'github_token':rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})',
 'openai_token':rb'sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{40,}',
 'aws_access_key':rb'AKIA[0-9A-Z]{16}',
 'slack_token':rb'xox[baprs]-[A-Za-z0-9-]{25,}',
 'google_api_key':rb'AIza[A-Za-z0-9_-]{30,}',
 'hf_token':rb'hf_[A-Za-z0-9]{30,}'
}
forbidden_parts={'.git','node_modules','vendor','third_party','__pycache__','obj','bin','lib','raw','tmp','cache','obj-current-D56','bin-current-D56','obj-historical-original'}
forbidden_suffixes={'.o','.ali','.a','.so','.dll','.exe','.pyc','.spark','.smt2','.psmt2','.mlw','.sqlite','.sqlite3','.db','.tar','.zip','.gz','.zst','.pem','.key','.p12'}
forbidden_names={'native-status.stdout','local-status.stdout','storage-preflight.stdout'}
findings=[];large=[];rows=[]
for expected in selection['rows']:
 p=ROOT/expected['path']
 if p.is_symlink() or not p.is_file() or not p.is_relative_to(ROOT):raise RuntimeError('Nonregular selected input')
 data=p.read_bytes();digest=hashlib.sha256(data).hexdigest()
 if digest!=expected['sha256'] or len(data)!=expected['bytes']:raise RuntimeError('Original selection changed '+expected['path'])
 relative=p.relative_to(ROOT)
 if any(part in forbidden_parts for part in relative.parts) or p.suffix in forbidden_suffixes or p.name in forbidden_names:
  findings.append({'path':str(relative),'kind':'forbidden_path_or_container'})
 try:data.decode('utf8')
 except UnicodeDecodeError:findings.append({'path':str(relative),'kind':'nonUTF8'})
 if b'\0' in data:findings.append({'path':str(relative),'kind':'NUL'})
 for name,pattern in patterns.items():
  if re.search(pattern,data):findings.append({'path':str(relative),'kind':name})
 if len(data)>1000000:
  if p.name=='result.json':
   parsed=json.loads(data);classification={'format':'JSON object','top_level_keys':sorted(parsed)}
  elif p.suffix=='.jsonl':
   parsed=[json.loads(line) for line in data.splitlines() if line.strip()]
   if any(not isinstance(row,dict) for row in parsed):raise RuntimeError('Nonobject JSONL metadata')
   classification={'format':'JSON-lines objects','observed_key_union':sorted({key for row in parsed for key in row})}
  else:raise RuntimeError('Unclassified oversized selected bytes')
  large.append({**expected,'classification':classification,'disposition':'PENDING exact reviewer size-finding disposition; original scan exit1/flags retained. No threshold/gate changed.'})
 rows.append(expected)
receipt={'utc':datetime.now(timezone.utc).isoformat(),'command':sys.orig_argv,'method_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'selection_sha256':hashlib.sha256(selection_path.read_bytes()).hexdigest(),'rows':rows,'assigned_patterns':list(patterns),
 'other_findings':findings,'original_size_flags':selection['flags'],'oversized_exact_metadata_candidates':large,
 'exclusions_checked':{'parts':sorted(forbidden_parts),'suffixes':sorted(forbidden_suffixes),'names':sorted(forbidden_names)},
 'boundary':'Exact finite bytes/path/token-pattern/container audit only, not exhaustive secret/privacy/vendor detection. No staging/commit/push or size exception authorized here; initial size-flag exit1 and all failed logs retained. Actual GPT-6.1 result/index review remains mandatory.'}
with (OUT/'finite-audit-v1.json').open('x') as stream:json.dump(receipt,stream,indent=2);stream.write('\n')
print(json.dumps({'output':str(OUT/'finite-audit-v1.json'),'other_findings':findings,'oversized_metadata_candidates':large}))
raise SystemExit(1 if findings else 0)
