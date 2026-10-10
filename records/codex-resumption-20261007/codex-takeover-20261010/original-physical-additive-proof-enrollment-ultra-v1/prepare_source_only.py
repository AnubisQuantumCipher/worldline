from pathlib import Path
import ast,hashlib,json,re,stat,difflib
T=Path(__file__).resolve().parent;S=T/'integrated-candidate-v6/source';PH=T/'physical-completion-integration-main-v3';O=T.parent/'phase1-physical-completion-v34-donor';P=T/'original-physical-additive-proof-enrollment-ultra-v1';P.mkdir(exist_ok=False)
NAME='runtime/worldline/proof_manifest.py';old=(S/NAME).read_text();tree=ast.parse(old,filename=str(S/NAME))
def pin(p):
 p=Path(p);s=p.stat();return {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':s.st_size,'mode':stat.S_IMODE(s.st_mode)}
def write(n,v):
 p=P/n;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(v.encode() if isinstance(v,str) else v)
def dump(n,v):write(n,json.dumps(v,indent=2,sort_keys=True)+'\n')
# Isolate only unchanged pure pin normalizer definitions; no target module imports.
norms=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['normalized_ada','contract_text','contract_pin']];assert len(norms)==3
ns={'Path':Path,'hashlib':hashlib};nt=ast.Module(body=[ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0),*norms],type_ignores=[]);exec(compile(ast.fix_missing_locations(nt),str(S/NAME),'exec'),ns)
units=['core/worldline-actuation.ads','core/worldline-actuation.adb','core/worldline-actuation_full_wire.ads']
for n in units:assert not (S/n).exists() and (PH/'source'/n).read_bytes()==(O/'source'/n).read_bytes()
new_pins={n:ns['contract_pin'](PH/'source',n) for n in units}
required=['Worldline.Actuation.Same_Entry','Worldline.Actuation.Decide','Worldline.Actuation_Full_Wire.Well_Formed','Worldline.Actuation_Full_Wire.Decode']
all_callables=[]
for n in units:
 text=(PH/'source'/n).read_text();pkg=re.search(r'package(?: body)?\s+([A-Za-z0-9_.]+)\s+with',text).group(1)
 all_callables.extend(pkg+'.'+x for x in re.findall(r'\b(?:function|procedure)\s+([A-Za-z0-9_]+)\s*\(',text))
assert set(all_callables)==set(required)
# Evaluate literal policy only; reject unsupported dynamic assignments.
def policy(src):
 tr=ast.parse(src);v={}
 def evalnode(n):
  if isinstance(n,ast.Name):return v[n.id]
  if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='frozenset' and len(n.args)==1 and not n.keywords:return frozenset(ast.literal_eval(n.args[0]))
  if isinstance(n,ast.BinOp) and isinstance(n.op,ast.BitOr):return evalnode(n.left)|evalnode(n.right)
  return ast.literal_eval(n)
 names={'MINIMUM_CHECKS','UNANALYZED_BOUNDARY','REQUIRED_PROVED','DECLARED_CORE_ADA_SOURCES','CONTRACT_PINS'}
 for n in tr.body:
  if isinstance(n,ast.Assign):
   for t in n.targets:
    if isinstance(t,ast.Name) and t.id in names:v[t.id]=evalnode(n.value)
  elif isinstance(n,ast.AugAssign) and isinstance(n.target,ast.Name) and n.target.id in names:
   assert n.target.id=='REQUIRED_PROVED' and isinstance(n.op,ast.Add);v[n.target.id]+=ast.literal_eval(n.value)
  elif isinstance(n,ast.Expr) and isinstance(n.value,ast.Call):
   c=n.value
   if isinstance(c.func,ast.Attribute) and isinstance(c.func.value,ast.Name) and c.func.value.id=='CONTRACT_PINS' and c.func.attr=='update':assert len(c.args)==1 and not c.keywords;v['CONTRACT_PINS'].update(ast.literal_eval(c.args[0]))
 return v
before=policy(old);assert not(set(units)&before['DECLARED_CORE_ADA_SOURCES']);assert not(set(new_pins)&set(before['CONTRACT_PINS']));assert not(set(required)&set(before['REQUIRED_PROVED']))
block='\n\n# Original physical Actuation domain restored additively; no historical proof credit.\n# Preserve the entire inherited ordered roster, exact floor and C_API boundary.\nREQUIRED_PROVED += [\n'+''.join('    '+repr(n)+',\n' for n in required)+']\nDECLARED_CORE_ADA_SOURCES = DECLARED_CORE_ADA_SOURCES | frozenset({\n'+''.join('    '+repr(n)+',\n' for n in units)+'})\nCONTRACT_PINS.update({\n'+''.join('    '+repr(n)+': '+repr(new_pins[n])+',\n' for n in units)+'})\n'
new=old+block;after=policy(new);assert new[:len(old)]==old
assert after['REQUIRED_PROVED']==before['REQUIRED_PROVED']+required
assert after['DECLARED_CORE_ADA_SOURCES']==before['DECLARED_CORE_ADA_SOURCES']|frozenset(units)
assert after['CONTRACT_PINS']==dict(before['CONTRACT_PINS'],**new_pins)
for n in ['MINIMUM_CHECKS','UNANALYZED_BOUNDARY']:assert after[n]==before[n]
assert ast.dump(ast.parse(new).body[0])==ast.dump(tree.body[0]) and len(ast.parse(new).body)==len(tree.body)+3
write('source/'+NAME,new);write('preimage/'+NAME,old);write('integration/additive-original-actuation-enrollment.inc',block)
for n in units:write('references/physical-source/'+n,(PH/'source'/n).read_bytes())
write('references/refresh_contract_pins.py',(S/'refresh_contract_pins.py').read_bytes());write('author-model-provenance.json',(T/'proof_ultra-actual-launch-provenance.json').read_bytes())
write('repair.patch',''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+NAME,tofile='b/'+NAME)));write('inverse.patch',''.join(difflib.unified_diff(new.splitlines(True),old.splitlines(True),fromfile='b/'+NAME,tofile='a/'+NAME)))
dump('source-delta.json',{'schema':'worldline-exact-source-delta-v1','source_only':True,'target_execution':False,'phase_acceptance':False,'changes':[{'name':NAME,'before':pin(S/NAME),'after':pin(P/'source'/NAME)}]})
dump('exact-additive-enrollment.json',{'schema':'worldline-literal-original-physical-proof-enrollment-delta-v1','entire_current_manifest_byte_prefix_retained':True,'sole_additive_block':pin(P/'integration/additive-original-actuation-enrollment.inc'),'new_declared_core_sources':units,'new_required_callable_names':required,'all_original_new_callable_occurrences':all_callables,'overload_guarantee':'Both Well_Formed overloads and both Decode overloads remain in whole source/strict full checks; named REQUIRED_PROVED rows do not replace required zero-unproved whole-scope checks.','new_full_source_contract_pins':new_pins,'pin_derivation':'Only unchanged original normalized_ada/contract_text/contract_pin function ASTs executed; no target/module/native imports.','physical_packet':pin(PH/'source-author-packet-v1.json'),'physical_source_inputs':{n:pin(PH/'source'/n) for n in units},'original_source_inputs':{n:pin(O/'source'/n) for n in units},'old_ordered_required_roster':before['REQUIRED_PROVED'],'old_declared_core_sources':sorted(before['DECLARED_CORE_ADA_SOURCES']),'old_effective_contract_pins':before['CONTRACT_PINS'],'old_check_floor':before['MINIMUM_CHECKS'],'old_unanalyzed_boundary':sorted(before['UNANALYZED_BOUNDARY']),'new_check_floor':after['MINIMUM_CHECKS'],'new_unanalyzed_boundary':sorted(after['UNANALYZED_BOUNDARY']),'before_counts':{'required_proved':len(before['REQUIRED_PROVED']),'declared_core_sources':len(before['DECLARED_CORE_ADA_SOURCES']),'effective_contract_pins':len(before['CONTRACT_PINS'])},'after_counts':{'required_proved':len(after['REQUIRED_PROVED']),'declared_core_sources':len(after['DECLARED_CORE_ADA_SOURCES']),'effective_contract_pins':len(after['CONTRACT_PINS'])},'integration_required':'After all source7 restorations, run unchanged refresh_contract_pins.py --write and --check over the final integrated source to refresh every original literal, retaining complete old AST/policy plus only this additive block. Original full source-only collector must verify exact actual core == declared, exact full pins and full required sequence; actual proof still mandatory.','target_execution':False,'phase_acceptance':False})
dump('SOURCE-IDENTITY.json',{'schema':'worldline-source-only-donor-identity-v1','author':'CodexOriginalPhysicalProofEnrollmentUltraAuthor','author_agent':'/root/proof_ultra','author_model':'openai-codex/gpt-6.1-sol:ultra','actual_author_launch':pin(P/'author-model-provenance.json'),'source_selection':pin(T/'integrated-candidate-v6/source-selection.json'),'current_source_opinion':pin(T/'frame-review-draft/integrated-v6-independent-source-review.json'),'permitted_names':[NAME],'source_inputs':{NAME:pin(S/NAME),'refresh_contract_pins.py':pin(S/'refresh_contract_pins.py')},'physical_new_core_source_inputs':{n:pin(PH/'source'/n) for n in units},'source_only':True,'target_execution':False,'phase_acceptance':False})
write('CHANGE.md','Append only literal proof enrollment for restored original Actuation and Actuation_Full_Wire units: all new source files, complete callable names and full source contract pins derived with the unchanged original AST-isolated normalizer. Every current manifest byte remains its exact prefix; original ordered required roster, floor and excluded C_API boundary stay intact. Overloaded wire helpers remain within whole-source strict checks. Root must refresh every original literal after complete source integration and obtain exact-core declaration/source/control enrollment plus actual full strict evidence; no source, historical or subset proof credit.\n')
write('prepare_source_only.py',Path(__file__).read_bytes())
dump('author-freeze.json',{'schema':'worldline-source-only-donor-author-freeze-v1','author':'CodexOriginalPhysicalProofEnrollmentUltraAuthor','author_agent':'/root/proof_ultra','author_model':'openai-codex/gpt-6.1-sol:ultra','source_only':True,'target_execution':False,'phase_acceptance':False,'files':{str(p.relative_to(P)):pin(p) for p in sorted(P.rglob('*')) if p.is_file()}})
dump('source-author-packet-v1.json',{'schema':'worldline-source-only-donor-author-packet-v1','author_freeze':pin(P/'author-freeze.json'),'source_identity':pin(P/'SOURCE-IDENTITY.json'),'source_delta':pin(P/'source-delta.json'),'exact_additive_enrollment':pin(P/'exact-additive-enrollment.json'),'actual_author_launch':pin(P/'author-model-provenance.json'),'permitted_names':[NAME],'review_destination':str(P/'independent-source-review.json'),'requested_disposition':'QUALIFIED_EXACT_ADDITIVE_ORIGINAL_PHYSICAL_PROOF_ENROLLMENT_SOURCE_ONLY','source_only':True,'target_execution':False,'phase_acceptance':False})
print(json.dumps({'packet':pin(P/'source-author-packet-v1.json'),'freeze':pin(P/'author-freeze.json'),'source':pin(P/'source'/NAME),'additive_block':pin(P/'integration/additive-original-actuation-enrollment.inc'),'after_counts':{'required':len(after['REQUIRED_PROVED']),'declared':len(after['DECLARED_CORE_ADA_SOURCES']),'effective_pins':len(after['CONTRACT_PINS'])}},indent=2))
