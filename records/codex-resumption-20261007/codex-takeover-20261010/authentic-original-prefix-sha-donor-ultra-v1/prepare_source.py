"""Passive source-data authoring for one authentic produced-prefix hash leaf."""
from pathlib import Path
import ast, hashlib, json, difflib, stat
T=Path(__file__).parent.parent
D=Path(__file__).parent
S=T/'integrated-candidate-v8/source'
REL='protected-root/controls/fixture_builder.py'
def pin(p):
 p=Path(p);r=p.read_bytes();i=p.lstat();assert stat.S_ISREG(i.st_mode)
 return {'path':str(p),'sha256':hashlib.sha256(r).hexdigest(),'bytes':len(r),'mode':stat.S_IMODE(i.st_mode)}
def save(n,v):
 p=D/n;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(json.dumps(v,sort_keys=True,ensure_ascii=True,indent=2).encode()+b'\n')
 return pin(p)
def main():
 old=(S/REL).read_text()
 before="            return {'config_sha256': ledger.config_sha, 'genesis_hex': raw.hex(), 'original_prefix': prefix}\n"
 after="            return {'config_sha256': ledger.config_sha, 'genesis_hex': raw.hex(), 'original_prefix': prefix,\n                    'original_prefix_sha256': sha(module.canonical(prefix))}\n"
 assert old.count(before)==1
 new=old.replace(before,after)
 for side,b in [('preimages',old),('postimages',new)]:
  p=D/side/REL;p.parent.mkdir(parents=True,exist_ok=True)
  with p.open('x') as f:f.write(b)
 patch=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+REL,tofile='b/'+REL))
 inverse=''.join(difflib.unified_diff(new.splitlines(True),old.splitlines(True),fromfile='a/'+REL,tofile='b/'+REL))
 (D/'forward.patch').write_text(patch);(D/'inverse.patch').write_text(inverse)
 # Ensure the exact canonical functions used by producer/receiver have the same AST semantics.
 def canon(path):
  tree=ast.parse(path.read_text());f=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='canonical')
  return ast.dump(f,include_attributes=False)
 assert canon(S/'protected-resource/run_service.py')==canon(S/'runtime/worldline/protected_resource_runtime.py')
 original=ast.parse(old); successor=ast.parse(new)
 # Sole source delta: a dictionary field appended to the full-run-ledger return.
 original_dump=ast.dump(original,include_attributes=False)
 ret=next(x for x in ast.walk(successor) if isinstance(x,ast.Return) and isinstance(x.value,ast.Dict)
          and [getattr(k,'value',None) for k in x.value.keys]==['config_sha256','genesis_hex','original_prefix','original_prefix_sha256'])
 ret.value.keys.pop();ret.value.values.pop()
 assert ast.dump(successor,include_attributes=False)==original_dump
 consumers={}
 for rel in ['protected-resource/run_service.py','runtime/worldline/protected_resource_runtime.py','runtime/worldline/protected_scoped_resource_service.py','protected-root/controls/construction_registry.py']:
  consumers[rel]=pin(S/rel)
 bindings={'name':'scoped-config','existing_binding_kind':'result','binding':{'kind':'result','action':'historical-ledger','select':['original_prefix_sha256'],'field':['observation_genesis','original_prefix_sha256']},'producer':'historical-ledger result after actual original complete SQLite snapshot/checkpoint/lock and sync','receiving_contract':'fixture_builder scoped-ledgers unchanged exact observation_genesis.original_prefix_sha256 == sha(scoped.canonical(prefix))','existing_result_fields_unchanged':['config_sha256','genesis_hex','original_prefix'],'new_result_field':'original_prefix_sha256','no_new_plan_or_binding_schema':True,'no_future_hash_authored':True,'whole_original_prefix':'genesis/state/all full typed rows/all event bytes in original ordered SQL capture; same object returned unchanged','scope':'source-only producer DATA, never grant/native decision/receipt or successful stage marker'}
 save('CALLER-CORRESPONDENCE.json',bindings)
 reg=save('INERT-SOURCE-CORRESPONDENCE-RESULT.json',{'schema':'worldline.actual-prefix-hash-inert-source-correspondence-v1','canonical_producer_receiver_AST_equal':True,'only_added_return_dictionary_field':True,'whole_original_DB_native_constructor_AST_preserved':True,'target_execution':False,'fixture_or_producer_output_created':False})
 packet={'schema':'worldline.authentic-original-prefix-sha-source-author-packet-v1','author':'CodexAuthenticOriginalPrefixShaAuthor','author_agent':'/root/protected_ultra','actual_model_selection':'openai-codex/gpt-6.1-sol:ultra','model_provenance':pin(T/'protected_ultra-actual-launch-provenance.json'),'source_context':{'selector':pin(T/'integrated-candidate-v8/source-selection.json'),'independent_source_review':pin(T/'frame-review-draft/integrated-v8-independent-source-review.json')},'preimages':{REL:pin(D/'preimages'/REL)},'postimages':{REL:pin(D/'postimages'/REL)},'forward_patch':pin(D/'forward.patch'),'inverse_patch':pin(D/'inverse.patch'),'unchanged_consumers':consumers,'caller_correspondence':pin(D/'CALLER-CORRESPONDENCE.json'),'inert_correspondence':reg,'requested_disposition':'QUALIFIED_EXACT_AUTHENTIC_ORIGINAL_PREFIX_SHA_PRODUCER_BINDING_SOURCE_ONLY','review_destination':str(D/'independent-source-review.json'),'full_original_guarantees_unchanged':True,'source_only':True,'target_execution':False,'installation':None,'actual_original_prefix_or_SHA_output':None,'actual_stage_or_receipt':None,'phase_acceptance':False}
 p=save('AUTHOR-PACKET.json',packet);print(json.dumps(p))
if __name__=='__main__':main()

