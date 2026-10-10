"""Restore the original v34 physical source into a disjoint source-only donor.

No target import, compiler, prover, tests, root installation or actor is executed.
Current source and historical donor are only read. Original controls and contracts
are copied intact; the current sole C_API transaction guard encloses new exports.
"""
from pathlib import Path
import ast, difflib, hashlib, json, os, re, shutil, stat

T=Path(__file__).resolve().parent
ORIGINAL=T.parent/'phase1-physical-completion-v34-donor'
CURRENT=T/'integrated-candidate-v6/source'
D=T/'physical-completion-integration-main-v3'
assert not D.exists()

def pin(p):
    p=Path(p); a=p.lstat(); assert stat.S_ISREG(a.st_mode) and not p.is_symlink()
    raw=p.read_bytes(); b=p.lstat()
    fields=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    assert fields(a)==fields(b),str(p)
    return {'path':str(p),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':b.st_size,'mode':stat.S_IMODE(b.st_mode)}
def save(p,raw):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
    os.chmod(p,0o644);return pin(p)
def json_save(p,v):return save(p,(json.dumps(v,sort_keys=True,indent=2)+'\n').encode())
def copy(a,b):
    before=pin(a);b.parent.mkdir(parents=True,exist_ok=True);assert not b.exists()
    shutil.copy2(a,b);assert pin(a)==before
    assert {k:pin(b)[k] for k in ('sha256','bytes','mode')}=={k:before[k] for k in ('sha256','bytes','mode')}

identity=json.loads((ORIGINAL/'identity.json').read_text())
for name,row in identity['files'].items():
    actual=pin(ORIGINAL/name);assert {k:actual[k] for k in row}==row,name
names=(
'core/worldline-actuation.ads','core/worldline-actuation.adb','core/worldline-actuation_full_wire.ads',
'core/worldline_actuation_v1.h','core/worldline_full_physical_v1.h',
'physical-value-controls/physical_value_controls.adb','physical-value-controls/physical_value_controls.gpr',
'protected-canonical/full_physical_actuator.c','protected-canonical/full_physical_actuator.h',
'protected-canonical/full_physical_sources.gpr',
'protected-canonical/vendor-transaction-035545/worldline_actuator.c',
'protected-canonical/vendor-transaction-035545/worldline_actuator.h',
'tests/test_full_physical_exports_native.py','tests/test_full_physical_syscalls_native.py',
'runtime/worldline/canonical_physical.py','runtime/worldline/canonical_full_broker.py')
D.mkdir(mode=0o755)
origins={}
for name in names:
    source=CURRENT/name
    if source.exists():
        before=ORIGINAL/'preimage'/name
        assert before.exists() and source.read_bytes()==before.read_bytes(),name
        copy(source,D/'preimage'/name)
    else:assert not source.is_symlink(),name
    copy(ORIGINAL/'source'/name,D/'source'/name)
    origins[name]=pin(ORIGINAL/'source'/name)

# Keep every current project entry, library interface, option and compiler pin.
project='core/worldline_core.gpr'
copy(CURRENT/project,D/'preimage'/project)
text=(CURRENT/project).read_text()
before='("worldline_core_sources.gpr", "attest_sha256.gpr");'
after='("worldline_core_sources.gpr", "attest_sha256.gpr",\n      "../protected-canonical/full_physical_sources.gpr");'
assert text.count(before)==1;text=text.replace(before,after,1)
needle='      "Worldline.Source_Syntax_Reference");'
addition='''      "Worldline.Source_Syntax_Reference",
      "Worldline.Actuation",
      "Worldline.Actuation_Full_Wire",
      "Worldline.Canonical_Exchange",
      "Worldline.Canonical_Exchange_Wire",
      "Worldline.Canonical_Owner_Completion",
      "Worldline.Canonical_Owner_Completion_Wire");'''
assert text.count(needle)==1;text=text.replace(needle,addition,1)
save(D/'source'/project,text.encode())

physical=(ORIGINAL/'integration/physical-c-api.adb.inc').read_text()
wrapped=[]
names_of_exports=('Full_Physical_Version','Full_Physical_Layout','Full_Physical_Exchange','Full_Physical_Recover','Actuation_Decide')
for name in names_of_exports:
    start=physical.index('   function '+name)
    end=physical.index('   end '+name+';',start)+len('   end '+name+';')
    function=physical[start:end]
    split=function.index(' is\n')+len(' is\n')
    header=function[:split]
    body=function[split:function.rindex('   end '+name+';')]
    if name in ('Full_Physical_Exchange','Full_Physical_Recover'):
        line=next(l for l in body.splitlines() if l.strip().startswith('return Native ('))
        call=line.strip()[len('return '):-1]
        body=body.replace(line,
            '      Native_Attempted := True;\n'
            '      Native_Status := '+call+';\n'
            '      Native_Returned := True;\n'
            '      Flush_Native_Diagnostic_Trace;\n'
            '      return Native_Status;',1)
        declarations='      Native_Attempted, Native_Returned : Boolean := False;\n      Native_Status : Interfaces.C.int := 1;\n'
        handler=('      when others =>\n'
                 '         if Native_Returned then return Native_Status;\n'
                 '         elsif Native_Attempted then return 3;\n'
                 '         else return 1; end if;\n')
    elif name=='Actuation_Decide':
        exact="         return Interfaces.C.unsigned_char(W.A.Decision'Pos(W.A.Decide(W.Decode(Value))));"
        replacement=("         Decision_Status :=\n"
                     "           Interfaces.C.unsigned_char(W.A.Decision'Pos(W.A.Decide(W.Decode(Value))));\n"
                     "         Decision_Returned := True;\n"
                     "         Flush_Native_Diagnostic_Trace;\n"
                     "         return Decision_Status;")
        assert body.count(exact)==1;body=body.replace(exact,replacement,1)
        fallback='   exception when others=>return 255;'
        retained=("   exception\n         when others =>\n"
                  "            if Decision_Returned then return Decision_Status;\n"
                  "            else return 255; end if;")
        assert body.count(fallback)==1;body=body.replace(fallback,retained,1)
        declarations=('      Decision_Returned : Boolean := False;\n'
                      '      Decision_Status : Interfaces.C.unsigned_char := 255;\n')
        handler=('      when others =>\n'
                 '         if Decision_Returned then return Decision_Status;\n'
                 '         else return 255; end if;\n')
    else:
        declarations=''
        failure='0' if name=='Full_Physical_Version' else '-1'
        handler='      when others => return '+failure+';\n'
    wrapped.append(header+declarations+'   begin\n      declare\n'
                   '         Native_Call : Native_Call_Guard;\n'
                   '         pragma Unreferenced (Native_Call);\n'+body+
                   '      end;\n   exception\n'+handler+'   end '+name+';\n')

body_insert=''.join(wrapped)
spec_insert=(ORIGINAL/'integration/physical-c-api.ads.inc').read_text()
for suffix,insert in (('adb',body_insert),('ads',spec_insert)):
    name='core/worldline-c_api.'+suffix;copy(CURRENT/name,D/'preimage'/name)
    text=(CURRENT/name).read_text();needle='end Worldline.C_API;'
    assert text.count(needle)==1;text=text.replace(needle,insert+'\n'+needle,1)
    if suffix=='adb':
        assert 'with Worldline.Actuation_Full_Wire;' not in text
        text='with Worldline.Actuation_Full_Wire;\n'+text
    save(D/'source'/name,text.encode())
save(D/'integration/physical-current-c-api.adb.inc',body_insert.encode())
save(D/'integration/physical-current-c-api.ads.inc',spec_insert.encode())
copy(ORIGINAL/'integration/physical-c-api.adb.inc',D/'historical/physical-c-api.adb.inc')
copy(ORIGINAL/'integration/physical-c-api.ads.inc',D/'historical/physical-c-api.ads.inc')
for name in ('identity.json','integration-contract.json','completion-notes.json','control-enrollment.json','verification.json'):
    copy(ORIGINAL/name,D/'historical'/name)

delta=[];forward=[];inverse=[]
for p in sorted((D/'source').rglob('*')):
    if not p.is_file():continue
    rel=p.relative_to(D/'source');pre=D/'preimage'/rel
    raw=p.read_bytes();previous=pre.read_bytes() if pre.exists() else b''
    if p.suffix=='.py':ast.parse(raw.decode())
    forward.extend(difflib.unified_diff(previous.decode().splitlines(keepends=True),raw.decode().splitlines(keepends=True),fromfile='preimage/'+str(rel) if pre.exists() else '/dev/null',tofile='source/'+str(rel)))
    inverse.extend(difflib.unified_diff(raw.decode().splitlines(keepends=True),previous.decode().splitlines(keepends=True),fromfile='source/'+str(rel),tofile='preimage/'+str(rel) if pre.exists() else '/dev/null'))
    delta.append({'path':str(rel),'preimage':pin(pre) if pre.exists() else None,'postimage':pin(p),'historical_exact_origin':origins.get(str(rel))})
save(D/'source-forward.patch',''.join(forward).encode())
save(D/'source-inverse.patch',''.join(inverse).encode())
json_save(D/'source-delta.json',delta)
json_save(D/'integration-contract-current.json',{
'schema':'worldline-current-original-physical-completion-restoration-v1',
'author':'Main','current_source':str(CURRENT),
'historical_donor':str(ORIGINAL),'historical_identity':pin(ORIGINAL/'identity.json'),
'original_physical_sources_and_controls':'EXACT_UNCHANGED_COPY',
'current_c_api_adaptation':'Only five original physical exports added in sole Off boundary, enclosed by unchanged current Native_Call_Guard; existing actual diagnostic drain preserved. Physical and actual typed actuation returned status retained across secondary finalizer/observer exceptions; attempted call without returned status maps to original POST_EXCHANGE_UNCERTAIN=3; pre-call refusal maps to original REFUSED=1.',
'current_gpr_adaptation':'Retain every current aggregate/project/library/interface/option; add original physical C project and all six original public SPARK physical/canonical interfaces.',
'root_unmodified_runtime':'canonical_k4_recovery.py already contains original observed-exchange wrappers and later native full-history resource-ack proof. Preserve byte-exact.',
'separate_exchange_owner_donor':'Required exact original exports/header closure/mapping helpers/protected_operations and semantic controls; this physical donor alone is not a complete integrated source.',
'operator_required':'Exact original selected broker physical_symbols roster includes recovery export; no policy provisioning, root installation, runtime provider or actor approval invented.',
'original_guarantees':'OPEN_UNCHANGED','target_imports':False,'build':False,'proof':False,'tests':False,'installation':False,'phase_acceptance':False})
print(json.dumps({'donor':str(D),'changed_files_observed':len(delta),'source_delta':pin(D/'source-delta.json'),'target_execution':False,'independent_review':'REQUIRED'}))

