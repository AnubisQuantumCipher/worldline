from pathlib import Path
import ast,difflib,hashlib,json,stat
T=Path(__file__).resolve().parent.parent
S=T/'integrated-candidate-v6/source';O=T.parent/'phase1-physical-completion-v34-donor';P=Path(__file__).resolve().parent

def pin(p):
 p=Path(p);s=p.stat();return {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':s.st_size,'mode':stat.S_IMODE(s.st_mode)}
def write(n,data):
 p=P/n;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(data.encode() if isinstance(data,str) else data)
def dump(n,v):write(n,json.dumps(v,indent=2,sort_keys=True)+'\n')
identity=json.loads((O/'identity.json').read_text());original_checks={}
for n,q in identity['files'].items():
 a=pin(O/n);assert all(a[k]==q[k] for k in ('sha256','bytes','mode')),n;original_checks[n]=a
original_body=(P/'integration/original-exchange-owner-c-api.adb.inc').read_text()
body=(P/'integration/exchange-owner-c-api.adb.inc').read_text()
spec=(P/'integration/exchange-owner-c-api.ads.inc').read_text()
context=(P/'integration/exchange-owner-context.ads.inc').read_text()
assert spec==(P/'integration/original-exchange-owner-c-api.ads.inc').read_text()
functions=['Canonical_Exchange_Version','Canonical_Exchange_Layout','Canonical_Exchange_Decide','Canonical_Owner_Completion_Version','Canonical_Owner_Completion_Layout','Canonical_Owner_Completion_Decide']
for f in functions:assert body.count('   function '+f)==1 and body.count('   end '+f+';')==1
assert body.count('Native_Call : Native_Call_Guard;')==len(functions)
post={}
needles={'core/worldline-c_api.ads':'   function Completion_ABI_Version return Interfaces.Unsigned_32','core/worldline-c_api.adb':'   function Operation_Result_Relation\n'}
for n,block in [('core/worldline-c_api.ads',spec),('core/worldline-c_api.adb',body)]:
 old=(S/n).read_text();needle=needles[n];assert old.count(needle)==1
 new=old.replace(needle,block+needle,1)
 if n.endswith('.adb'):
  assert all(line not in old for line in context.splitlines());new=context+new
  assert new[len(context):].replace(block,'',1)==old
 else:assert new.replace(block,'',1)==old
 post[n]=new
n='runtime/worldline/operation_owner_kernel.py';old=(S/n).read_text();original=(O/'source'/n).read_text();i=original.index('\n\nEXCHANGE_SYMBOLS =')
assert old.rstrip('\n')==original[:i].rstrip('\n')
post[n]=original
n='runtime/worldline/protected_operations.py';old=(S/n).read_text();new=old
replacements=[('        from .canonical_owner_completion_kernel import CanonicalOwnerCompletionKernel\n        from .canonical_exchange_kernel import CanonicalExchangeKernel\n        require(CanonicalExchangeKernel(self.core).observe(*proof[\'arguments\'])==proof[\'native\'],','        from .operation_owner_kernel import observe_owner_completion\n        from .operation_owner_kernel import observe_exchange, initialize_exchange_kernel, prepare_exchange\n        require(observe_exchange(self, *proof[\'arguments\'])==proof[\'native\'],'),('        native=CanonicalOwnerCompletionKernel(self.core).observe(proof[\'arguments\'],current)','        native=observe_owner_completion(self, proof[\'arguments\'],current)'),('        from .canonical_exchange_kernel import CanonicalExchangeKernel\n        native=CanonicalExchangeKernel(self.core).observe(*proof[\'arguments\'])','        from .operation_owner_kernel import observe_exchange, initialize_exchange_kernel, prepare_exchange\n        native=observe_exchange(self, *proof[\'arguments\'])')]
for before,after in replacements:assert new.count(before)==1;new=new.replace(before,after,1)
back=new
for before,after in reversed(replacements):assert back.count(after)==1;back=back.replace(after,before,1)
assert back==old;post[n]=new
copies=['core/worldline_canonical_exchange_v1.h','core/worldline_canonical_owner_completion_v1.h','core/worldline_canonical_operation_v1.h','canonical-exchange-tests/canonical_exchange_controls.adb','canonical-exchange-tests/canonical_exchange_tests.gpr','canonical-owner-completion-tests/canonical_owner_completion_controls.adb','canonical-owner-completion-tests/canonical_owner_completion_tests.gpr','tests/test_canonical_exchange_owner_exports_native.py','tests/test_canonical_owner_mapping_order.py']
for n in copies:assert not (S/n).exists();post[n]=(O/'source'/n).read_text()
strong=['core/worldline-canonical_exchange.ads','core/worldline-canonical_exchange.adb','core/worldline-canonical_exchange_wire.ads','core/worldline-canonical_owner_completion.ads','core/worldline-canonical_owner_completion.adb','core/worldline-canonical_owner_completion_wire.ads']
for n in strong:assert (S/n).read_bytes()==(O/'source'/n).read_bytes()
header='core/worldline_operation_authority_v1.h';extra=' int64_t effect_material_first,effect_material_length;\n';h=(S/header).read_text();assert h.count(extra)==1 and h.replace(extra,'',1)==(O/'source'/header).read_text()
changes=[];forward=[];inverse=[]
for n,new in sorted(post.items()):
 old=(S/n).read_text() if (S/n).exists() else ''
 if (S/n).exists():write('preimage/'+n,(S/n).read_bytes())
 write('source/'+n,new)
 if n.endswith('.py'):ast.parse(new,filename=n)
 forward.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+n if old else '/dev/null',tofile='b/'+n))
 inverse.extend(difflib.unified_diff(new.splitlines(True),old.splitlines(True),fromfile='b/'+n,tofile='a/'+n if old else '/dev/null'))
 changes.append({'name':n,'before':pin(S/n) if (S/n).exists() else None,'after':pin(P/'source'/n),'original_donor_after':pin(O/'source'/n),'exact_original_postimage':new==(O/'source'/n).read_text()})
write('repair.patch',''.join(forward));write('inverse.patch',''.join(inverse))
write('author-model-provenance.json',(T/'proof_ultra-actual-launch-provenance.json').read_bytes())
dump('source-delta.json',{'schema':'worldline-exact-source-delta-v1','source_only':True,'acceptance':False,'changes':changes})
dump('original-correspondence-and-restoration.json',{'schema':'worldline-original-exchange-owner-restoration-v1','source_only':True,'target_execution':False,'phase_acceptance':False,'original_identity':pin(O/'identity.json'),'original_identity_physical_checks':original_checks,'original_contract':pin(O/'integration-contract.json'),'original_input_pins':pin(O/'input-pins.json'),'original_verification':pin(O/'verification.json'),'original_verification_is_historical_source_only':True,'unchanged_strong_spark_units':{n:{'current':pin(S/n),'original':pin(O/'source'/n)} for n in strong},'current_public_authority_header_retained':{'current':pin(S/header),'original':pin(O/'source'/header),'sole_divergence_preserved':extra,'reason':'Current strong Raw_Evidence and ctypes caller already include effect_material slice; never overwrite with historical narrower header.'},'c_api_adaptation':{'functions':functions,'original_spec_segment':pin(P/'integration/original-exchange-owner-c-api.ads.inc'),'original_body_segment':pin(P/'integration/original-exchange-owner-c-api.adb.inc'),'current_body_segment':pin(P/'integration/exchange-owner-c-api.adb.inc'),'imports':pin(P/'integration/exchange-owner-context.ads.inc'),'spec_insertion_needle':needles['core/worldline-c_api.ads'],'body_insertion_needle':needles['core/worldline-c_api.adb'],'original_all_shape_checks_input_copies_decode_full_rosters_decide_arguments_retained':True,'each_export_existing_native_guard_and_outer_raw_refusal':True,'decide_actual_answer_flush_before_output_and_raw_exception_flush':True,'sole_existing_off_boundary_retained':True,'raw_pointer_readability':'OPEN; extent/alignment guards do not establish mapped readability'},'protected_mapping_exact_reversible_substitutions':[{'before':a,'after':b} for a,b in replacements],'owner_helper_original_prefix_preserved_modulo_terminal_newlines':True,'no_other_current_source_change':True,'root_owned_composition_files_not_modified':['runtime/worldline/canonical_full_broker.py','runtime/worldline/canonical_physical.py','runtime/worldline/canonical_k4_recovery.py','core/worldline_core.gpr'],'verification':{'build':'UNRUN','proof':'UNRUN','native_ABI_controls':'UNRUN','semantic_controls':'UNRUN','mapping_controls':'UNRUN','source_python_ast_parse':'PASS'}})
enrollment=json.loads((O/'references/exchange-owner-input/control-enrollment.json').read_text())
enrollment.update({'schema':'worldline-original-additive-control-enrollment-v1','original_document':pin(O/'references/exchange-owner-input/control-enrollment.json'),'original_controls_byteidentical':{n:pin(P/'source'/n) for n in copies if n.startswith(('canonical-','tests/'))},'current_complete_planned_actions':pin(T/'runtime-frame-successor-v6-ultra-draft/candidate/planned-actions.json') if (T/'runtime-frame-successor-v6-ultra-draft/candidate/planned-actions.json').exists() else None,'preserve_original_all_actions':True,'preserve_original_contracts_domains_proof_floor':True,'execution':False,'acceptance':False})
dump('control-enrollment.json',enrollment)
dump('SOURCE-IDENTITY.json',{'schema':'worldline-source-only-donor-identity-v1','author':'CodexCanonicalExchangeOwnerAbiRestorationUltraAuthor','author_agent':'/root/proof_ultra','author_model':'openai-codex/gpt-6.1-sol:ultra','actual_author_launch':pin(P/'author-model-provenance.json'),'source_selection':pin(T/'integrated-candidate-v6/source-selection.json'),'current_source_opinion':pin(T/'frame-review-draft/integrated-v6-independent-source-review.json'),'permitted_names':sorted(post),'source_inputs':{n:pin(S/n) if (S/n).exists() else None for n in sorted(post)},'unchanged_source_inputs':{n:pin(S/n) for n in strong+[header,'core/worldline_core_sources.gpr','runtime/worldline/canonical_exchange_kernel.py','runtime/worldline/canonical_owner_completion_kernel.py','runtime/worldline/operation_authority_kernel.py']},'source_only':True,'target_execution':False,'phase_acceptance':False})
write('CHANGE.md','Restore original canonical-exchange and owner-completion exports, complete dynamic rosters, caller-matching layouts, public headers, authenticated mapping joins, and additive original controls from the pinned v34 source-only donor. All consequential decisions remain the unchanged existing SPARK X.Decide and Y.Decide. Each added native export uses the current recursive transaction/diagnostic owner guard; decisions flush only after their real answer and preserve refusal/output semantics. Current effect_material evidence/header additions and later recovery witnesses remain intact. This donor is unbuilt, unproved and unexecuted. Complete original target/proof/ABI/control admission and independent review remain required.\n')
files={str(p.relative_to(P)):pin(p) for p in sorted(P.rglob('*')) if p.is_file()}
dump('author-freeze.json',{'schema':'worldline-source-only-donor-author-freeze-v1','author':'CodexCanonicalExchangeOwnerAbiRestorationUltraAuthor','author_agent':'/root/proof_ultra','author_model':'openai-codex/gpt-6.1-sol:ultra','source_only':True,'target_execution':False,'phase_acceptance':False,'files':files})
dump('source-author-packet-v1.json',{'schema':'worldline-source-only-restoration-author-packet-v1','author_agent':'/root/proof_ultra','author_model':'openai-codex/gpt-6.1-sol:ultra','actual_author_launch':pin(P/'author-model-provenance.json'),'author_freeze':pin(P/'author-freeze.json'),'source_identity':pin(P/'SOURCE-IDENTITY.json'),'source_delta':pin(P/'source-delta.json'),'original_correspondence':pin(P/'original-correspondence-and-restoration.json'),'forward_patch':pin(P/'repair.patch'),'inverse_patch':pin(P/'inverse.patch'),'control_enrollment':pin(P/'control-enrollment.json'),'permitted_names':sorted(post),'review_destination':str(P/'independent-source-review.json'),'requested_disposition':'QUALIFIED_EXACT_ORIGINAL_EXCHANGE_OWNER_ABI_MAPPING_CONTROLS_RESTORATION_SOURCE_ONLY','source_only':True,'target_execution':False,'phase_acceptance':False,'non_claims':['No historical compile, proof, target, custody or ABI success transferred.','No current missing-domain acceptance by review alone.','Root must integrate additive physical blocks and enroll all original controls, refresh original literal pins, and rerun full original admitted checks.']})
print(json.dumps({'packet':pin(P/'source-author-packet-v1.json'),'freeze':pin(P/'author-freeze.json'),'permitted_names':sorted(post)},indent=2))
