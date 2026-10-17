#!/usr/bin/env python3
"""Read-only mapping of every original action; writes a fresh recipe only."""
from pathlib import Path
import collections,datetime,hashlib,json,os,re,subprocess
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'scratch/acquisition/original-payload-recipe-v2.json'
ROSTER=ROOT/'scratch/reviewer/f3-original-full-action-roster.json'
FREEZE='364fbb9c311b800e7f5b0b75be999a4682e3134f'
FRAME=ROOT/'scratch/coordinator/final-frame'
def digest(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def path_identity(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p)}
roster=json.loads(ROSTER.read_text());actions=roster['actions'];builds={r['mode']:r for r in actions if r['kind']=='build'}
origins=[]
for r in roster['immutable_origins']:
 p=Path(r['path']);actual=digest(p)
 if actual!=r['sha256']:raise RuntimeError('Original source hash drift: '+str(p))
 origins.append({**r,'readback_sha256':actual})
source_prefix=actions[0]['rebindings']['source_prefix'];candidate_prefix=actions[0]['rebindings']['candidate_prefix']
def rebound(text):
 if not isinstance(text,str):return text
 # Exact old owned-frame spelling only; no arbitrary external-path rewrite.
 return text.replace(source_prefix,str(ROOT)).replace(candidate_prefix,str(FRAME))
def project_details(project):
 p=ROOT/project;text=p.read_text()
 mains_match=re.search(r'for\s+Main\s+use\s*\((.*?)\)\s*;',text,re.I|re.S)
 mains=re.findall(r'"([^"]+)"',mains_match.group(1)) if mains_match else []
 ex=re.search(r'for\s+Exec_Dir\s+use\s+"([^"]+)"',text,re.I)
 obj=re.search(r'for\s+Object_Dir\s+use\s+"([^"]+)"',text,re.I)
 execdir=(p.parent/(ex.group(1) if ex else obj.group(1) if obj else '.')).resolve()
 outputs=[str((execdir/Path(x).stem).relative_to(ROOT)) for x in mains]
 imports=re.findall(r'^\s*(?:with|limited\s+with)\s+"([^"]+)"',text,re.I|re.M)
 sourcefiles=[]
 for main in mains:
  target=p.parent/main
  if target.is_file():
   body=target.read_text();sourcefiles.append({**path_identity(target),'main':main,
     'assertion_source_present':bool(re.search(r'pragma\s+Assert|Ada\.Assertions\.Assert',body,re.I)),
     'literal_output_lines':[{'line':i,'text':line.strip()} for i,line in enumerate(body.splitlines(),1) if re.search(r'Put_Line\s*\(',line,re.I)]})
 return {'project':path_identity(p),'declared_mains':mains,'declared_exec_dir':str(execdir.relative_to(ROOT)),
  'static_expected_binary_paths':outputs,'assertion_flag_in_project':'"-gnata"' in text,
  'WORLDLINE_BUILD_required':'checks','imports':imports,'main_sources':sourcefiles,
  'non_claim':'Static simple-GPR mapping only; successful current compiler/binder/linker receipts required'}
rows=[]
for index,r in enumerate(actions):
 original=r['original'];additional=original.get('additional_command')
 row={'roster_index':index,'mode':r['mode'],'kind':r['kind'],'execution_status':'NOT PERFORMED by recipe preparation',
  'original_argv':original['child_argv'],'rebound_argv':[rebound(x) for x in original['child_argv']],
  'original_cwd':original['cwd'],'rebound_cwd':rebound(original['cwd']),
  'original_expected_result':r['expected_result'],'required_build_mode':r['required_build_prerequisite'],
  'original_additional_timeout_seconds':additional['test_timeout_seconds'] if additional else None,
  'original_timeout_evidence':'run_checks.py lines43-57 and388: additional180s only; ordinary payload has no inner timeout',
  'full_carrier_acceptance':'NOT PERFORMED; exact original external carrier/custody is not recreated',
  'current_receipt_required':True}
 if r['kind']=='build':
  row['owner']='coordinator original_aux_builds.py or dedicated frozen native/full build'
  row['disposition']='DELEGATED_BUILD; retain exact per-action build outcome, never infer from aggregate exit alone'
 elif r['kind']=='python-controls':
  row['owner']='old-analysis original/full runtime supervisor; acquisition agent launches none'
  row['disposition']='DELEGATED_PYTHON; explicit original focused payload accounting remains required'
  if r['mode']=='acquisition-regression-tests':
   row['disposition']='FAILED-OPEN retained repeated original deadline; no third acquisition campaign'
   row['current_receipts']=['records/phase1-blockers/acquisition-full-repaired-v1','records/phase1-blockers/acquisition-full-repaired-v2']
  if r['mode']=='execution-evidence-boundary-additional-controls':
   row['disposition']='NOT PERFORMED until coordinator copies original identical additional script to rebound frame path and verifies hash; no Python implementation edits'
   p=Path(original['child_argv'][2]);row['external_original_script_sha256']=digest(p)
   row['additional_marker']='EXECUTION_EVIDENCE_BOUNDARY_RESULT';row['production_custody_established']=False
  if r['mode']=='freshness-json-object-order-additional-controls':
   row['additional_marker']='FRESHNESS_JSON_ORDER_RESULT';row['production_custody_established']=False
  if r['mode']=='capability-native-binding-simulation-controls':row['claim_boundary']='SIMULATED NOT ELF only; no protected native authority'
 else:
  row['owner']='coordinator local payload runner after exact matching build receipt'
  if r['mode']=='original-full-physical-disposable-namespace-controls':
   row['disposition']='CONDITIONAL NAMESPACE: no launch until coordinator-approved private second-filesystem mapping and actual namespace premises are measured'
   row['required_original_fixture']='Distinct private tmpfs mounted at owned worktree path and aliased as /dev/shm only inside disposable namespace; original unshare --user --map-root-user argv retained'
   row['namespace_admission_required']=['coordinator decision and actual GPT-6.1 review artifact for exact wrapper','non-root host entry','actual user/mount namespace identity and ownership-map observations','distinct st_dev for original worktree fixture and private second filesystem','host /dev/shm unchanged/unwritten; bind alias exists only inside disposable namespace','all namespace processes owned and quiescent before cleanup/lock release','original fixture/assertions/180s deadline unchanged']
   row['namespace_review_context']='Reviewer message reports root+reviewer concurrence to private second-filesystem mapping; exact runnable wrapper and receipt not supplied by this recipe'
   row['full_F4_protected']='NOT PERFORMED; namespace fixture cannot supply installed protected authority'
  else:
   prerequisite=builds.get(r['required_build_prerequisite'])
   if not prerequisite:row['disposition']='BLOCKED NOT PERFORMED: exact build prerequisite missing from extracted roster'
   else:
    argv=prerequisite['original']['child_argv'];project=argv[argv.index('-P')+1] if '-P' in argv else None
    if project is None:row['disposition']='BLOCKED NOT PERFORMED: no direct GPR project in build argv'
    else:
     detail=project_details(project)
     if '-o' in argv:
      override=argv[argv.index('-o')+1];bound=Path(rebound(override))
      if not bound.is_absolute():bound=ROOT/bound
      if not bound.resolve().is_relative_to(ROOT):raise RuntimeError('Original output override escapes owned source root')
      detail['original_output_override']=override;detail['rebound_output_override']=str(bound)
      detail['GPR_default_outputs_before_original_override']=detail['static_expected_binary_paths']
      detail['static_expected_binary_paths']=[str(bound.relative_to(ROOT))]
     row['project_binding']=detail
     relative=Path(row['rebound_argv'][0]).relative_to(ROOT).as_posix()
     row['binary_relative']=relative;row['build_original_argv']=argv
     if relative not in detail['static_expected_binary_paths']:
      row['disposition']='BLOCKED NOT PERFORMED: original binary path does not match declared GPR Exec_Dir/Main; no substitute binary'
     elif not detail['assertion_flag_in_project']:
      row['disposition']='BLOCKED NOT PERFORMED: original assertion-enabled build not established by inspected project'
     else:row['disposition']='ELIGIBLE ONLY AFTER successful exact current build and binary/native dependency identity verification'
     row['build_receipt_required']='records/phase1-blockers/original-aux-builds-final-v1/'+r['required_build_prerequisite']+'/result.json'
     row['output_custody_required']=['hash exact built binary after successful prerequisite','retain copy or same-hash immutable binary for payload','readelf dynamic-needed/rpath identities before execution; resolve every dependency and hash it','record WORLDLINE_BUILD=checks and actual compiler switches/ALI or build receipt','verify frozen source unchanged and same selected native library before/after payload']
     if relative=='use-reservation-tests/bin/use_reservation_tests':row['cosmogony_boundary']='Imports original cosmogony-use-component source read-only; no Cosmogony edits or installed protected acceptance'
 rows.append(row)
result={'classification':'MEASURED read-only original roster and static GPR/source mapping; no payload executed',
 'supersedes':'original-payload-recipe-v1.json retained; original explicit -o override honored; namespace conditional after reported approved private mapping',
 'corrections':['v1 GPR-only recovery binary inference ignored original -o and was incomplete; no payload was skipped or executed from v1','v1 namespace blocker refined to conditional private second-filesystem mapping after reviewer reports root concurrence; actual premises remain required'],
 'prepared_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_commit':FREEZE,
 'root_head_observed':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
 'command':['python3','-B','scratch/acquisition/prepare_original_payload_recipe_v2.py'],
 'recipe_generator':path_identity(Path(__file__)),'roster':path_identity(ROSTER),'verified_original_inputs':origins,
 'prefix_rebindings':{source_prefix:str(ROOT),candidate_prefix:str(FRAME)},
 'counts':{'actions':len(rows),'kinds':dict(collections.Counter(r['kind'] for r in rows)),
           'dispositions':dict(collections.Counter(r['disposition'] for r in rows))},
 'actions':rows,'execution_policy':[
 'Coordinator alone executes after internal review; this file is an eligibility recipe, not an acceptance result',
 'Every actual payload uses approved heavy flock/admission8G scope; original additional180s deadline preserved; ordinary payloads had no inner deadline, so local outer bound must be explicit and classified local diagnostic only',
 'No global HOME/CODEX_HOME rewrite, no writes outside worktree, no Cosmogony edit, all TMPDIR and writable outputs inside worktree',
 'Failure/missing matching build or source/binary/library mismatch produces explicit NOT PERFORMED for dependent payload; never run stale binary',
 'Zero exit alone cannot substitute for original assertions/markers, requested cases, timeout semantics, complete raw output and custody',
 'Full unittest supervisor is old-analysis ownership, not duplicated here; original focused/additional argv still need separate accounting',
 'Original external coordination/installed protected custody not recreated; complete F3/F5/carrier acceptance stays open'],
 'independent_acceptance':'NOT PERFORMED'}
if OUT.exists():raise RuntimeError('Fresh output required')
OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps({'path':str(OUT.relative_to(ROOT)),'sha256':digest(OUT),'counts':result['counts']}))
