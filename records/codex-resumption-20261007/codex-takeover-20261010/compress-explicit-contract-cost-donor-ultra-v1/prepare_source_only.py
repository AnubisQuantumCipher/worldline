"""Prepare disjoint preserved-body Compress contracts and additive proof enrollment."""
from pathlib import Path
import ast
import difflib
import hashlib
import json
import shutil
import stat

T = Path(__file__).resolve().parent
S = T / 'integrated-candidate-v8/source'
P = T / 'compress-explicit-contract-cost-donor-ultra-v1'
MANIFEST = 'runtime/worldline/proof_manifest.py'
UNITS = ['core/attest/attest-sha256.adb', 'core/attest/attest-custody_sha256.adb']
REQUIRED = ['Attest.SHA256.Compress', 'Attest.Custody_SHA256.Compress']
BEFORE = '   procedure Compress (H : in out State; B : Block) is\n'
AFTER = ('   procedure Compress (H : in out State; B : Block)\n'
         '     with Global => null,\n'
         '          Depends => (H => (H, B)),\n'
         '          Always_Terminates\n'
         '   is\n')


def pin(path):
    p = Path(path)
    a = p.lstat()
    assert stat.S_ISREG(a.st_mode) and not p.is_symlink()
    b = p.read_bytes()
    z = p.lstat()
    fields = lambda r: (r.st_dev, r.st_ino, r.st_mode, r.st_size, r.st_mtime_ns, r.st_ctime_ns)
    assert fields(a) == fields(z)
    return dict(path=str(p), sha256=hashlib.sha256(b).hexdigest(), bytes=len(b), mode=stat.S_IMODE(z.st_mode))


def write(name, raw):
    p = P / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(raw.encode() if isinstance(raw, str) else raw)
    p.chmod(0o644)
    return pin(p)


def save(name, obj):
    return write(name, json.dumps(obj, sort_keys=True, indent=2) + '\n')


def policy(raw):
    values = {}
    def evaluate(node):
        if isinstance(node, ast.Name):
            return values[node.id]
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'frozenset':
            assert len(node.args) == 1 and not node.keywords
            return frozenset(ast.literal_eval(node.args[0]))
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
            return evaluate(node.left) | evaluate(node.right)
        return ast.literal_eval(node)
    names = {'MINIMUM_CHECKS', 'UNANALYZED_BOUNDARY', 'REQUIRED_PROVED', 'DECLARED_CORE_ADA_SOURCES', 'CONTRACT_PINS'}
    for node in ast.parse(raw).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in names:
                    values[target.id] = evaluate(node.value)
        elif isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name) and node.target.id in names:
            assert node.target.id == 'REQUIRED_PROVED' and isinstance(node.op, ast.Add)
            values[node.target.id] += ast.literal_eval(node.value)
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            call = node.value
            if isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Name) and call.func.value.id == 'CONTRACT_PINS' and call.func.attr == 'update':
                assert len(call.args) == 1 and not call.keywords
                values['CONTRACT_PINS'].update(ast.literal_eval(call.args[0]))
    return values


def main():
    P.mkdir(exist_ok=False)
    changes = []
    for name in UNITS:
        old = (S / name).read_text()
        assert old.count(BEFORE) == 1 and AFTER not in old
        new = old.replace(BEFORE, AFTER, 1)
        assert new.replace(AFTER, BEFORE, 1) == old
        write('preimage/' + name, old)
        write('source/' + name, new)
        changes.append({'name': name, 'before': pin(S / name), 'after': pin(P / 'source' / name),
                        'sole_added_contract': AFTER, 'whole_executable_body_preimage_reconstructed': True})
    old_manifest = (S / MANIFEST).read_text()
    tree = ast.parse(old_manifest)
    normalizers = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ('normalized_ada', 'contract_text', 'contract_pin')]
    assert {n.name for n in normalizers} == {'normalized_ada', 'contract_text', 'contract_pin'}
    ns = {'Path': Path, 'hashlib': hashlib}
    isolated = ast.Module(body=[ast.ImportFrom(module='__future__', names=[ast.alias(name='annotations')], level=0), *normalizers], type_ignores=[])
    exec(compile(ast.fix_missing_locations(isolated), str(S / MANIFEST), 'exec'), ns)
    old_policy = policy(old_manifest)
    assert not (set(REQUIRED) & set(old_policy['REQUIRED_PROVED']))
    affected_keys = [k for k in old_policy['CONTRACT_PINS'] if k.partition('#')[0] in UNITS]
    assert set(UNITS) <= set(affected_keys)
    derived = {k: ns['contract_pin'](P / 'source', k) for k in affected_keys}
    encoded = old_manifest.encode()
    lines = encoded.splitlines(True)
    replacements = []
    literal_rows = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        for key, value in zip(node.keys, node.values):
            if isinstance(key, ast.Constant) and key.value in derived:
                assert isinstance(value, ast.Constant) and isinstance(value.value, str)
                start = sum(len(x) for x in lines[:value.lineno - 1]) + value.col_offset
                end = sum(len(x) for x in lines[:value.end_lineno - 1]) + value.end_col_offset
                quote = encoded[start:start + 1]
                assert quote in (b"'", b'"')
                replacement = quote + derived[key.value].encode() + quote
                replacements.append((start, end, replacement))
                literal_rows.append({'key': key.value, 'before': value.value, 'after': derived[key.value], 'line': value.lineno})
    rewritten = encoded
    for start, end, replacement in sorted(replacements, reverse=True):
        rewritten = rewritten[:start] + replacement + rewritten[end:]
    block = ('\n\n# Explicit local SHA compression contracts: retain every original proof obligation.\n'
             '# Add separate private-helper proof names; no inherited or contextual proof credit.\n'
             'REQUIRED_PROVED += [\n' + ''.join('    ' + repr(n) + ',\n' for n in REQUIRED) + ']\n')
    new_manifest = rewritten.decode() + block
    new_policy = policy(new_manifest)
    assert new_policy['REQUIRED_PROVED'] == old_policy['REQUIRED_PROVED'] + REQUIRED
    for key in ('MINIMUM_CHECKS', 'UNANALYZED_BOUNDARY', 'DECLARED_CORE_ADA_SOURCES'):
        assert new_policy[key] == old_policy[key]
    assert new_policy['CONTRACT_PINS'] == dict(old_policy['CONTRACT_PINS'], **derived)
    write('preimage/' + MANIFEST, old_manifest)
    write('source/' + MANIFEST, new_manifest)
    write('integration/additive-compress-proof-enrollment.inc', block)
    changes.append({'name': MANIFEST, 'before': pin(S / MANIFEST), 'after': pin(P / 'source' / MANIFEST),
                    'sole_policy_delta': 'Append exact private Compress names; refresh only every affected existing body digest literal using unchanged original normalizer.'})
    forward = []
    inverse = []
    for row in changes:
        name = row['name']
        old = (P / 'preimage' / name).read_text()
        new = (P / 'source' / name).read_text()
        forward.append(''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True), fromfile='a/' + name, tofile='b/' + name)))
        inverse.append(''.join(difflib.unified_diff(new.splitlines(True), old.splitlines(True), fromfile='b/' + name, tofile='a/' + name)))
    write('repair.patch', ''.join(forward))
    write('inverse.patch', ''.join(inverse))
    shutil.copy2(T / 'proof_ultra-actual-launch-provenance.json', P / 'author-model-provenance.json')
    for name in ['core/attest/attest-sha256.ads', 'core/attest/attest-custody_sha256.ads', 'refresh_contract_pins.py']:
        write('references/source8/' + name, (S / name).read_bytes())
    EX = Path('/home/sicarii/opt/gnat/gnatprove-aarch64-linux-16.1.0-1/share/examples/spark/gnatprove_by_example/ug__arith_with_local_subp')
    for p in sorted(EX.iterdir()):
        if p.is_file():
            write('references/installed-contextual-example/' + p.name, p.read_bytes())
    save('contextual-proof-reference.json', {
        'primary_url': 'https://docs.adacore.com/spark2014-docs/html/ug/en/source/how_to_write_subprogram_contracts.html#contextual-analysis-of-subprograms-without-contracts',
        'reference_release': '28.0w', 'installed_example_release': 'distributed16.1',
        'paraphrase': 'Local procedures lacking Global, Depends, Pre, Post or Contract_Cases can be analyzed in caller context. An explicit contract prevents contextual inlining. Explicit dependencies must be checked on the body and caller, and procedure termination remains an actual obligation.',
        'installed_acceptance_required': 'Actual unchanged strict full command; documentation and example files do not establish acceptance of this donor or effectiveness.'})
    save('contract-preservation-and-enrollment.json', {
        'schema': 'worldline-preserved-body-compress-explicit-contract-enrollment-v1',
        'affected_units': UNITS, 'new_required_private_callable_names': REQUIRED,
        'new_private_contract': {'Global': 'null', 'Depends': 'H => (H, B)', 'Always_Terminates': True},
        'whole_body_preservation': 'Removing only the explicit aspect list reconstructs the entire exact source8 body. Constants, arithmetic, shifts, rotations, loops, variants, invariants, buffer/hash operations and every call remain byte-identical.',
        'public_specs_and_equations': {n: pin(S / n) for n in ('core/attest/attest-sha256.ads', 'core/attest/attest-custody_sha256.ads')},
        'no_added_precondition_or_reduced_postcondition': True,
        'no_skip_assume_hide_info_justification_or_command_delta': True,
        'full_existing_required_order': old_policy['REQUIRED_PROVED'],
        'full_current_required_order': new_policy['REQUIRED_PROVED'],
        'floor_before': old_policy['MINIMUM_CHECKS'], 'floor_after': new_policy['MINIMUM_CHECKS'],
        'boundary_before': sorted(old_policy['UNANALYZED_BOUNDARY']), 'boundary_after': sorted(new_policy['UNANALYZED_BOUNDARY']),
        'declared_core_roster_unchanged': sorted(old_policy['DECLARED_CORE_ADA_SOURCES']),
        'affected_existing_literal_pin_refresh_rows': literal_rows,
        'new_effective_contract_pins': derived,
        'derivation': 'Only unchanged original AST-isolated normalized_ada/contract_text/contract_pin definitions executed; no target module imports.',
        'mandatory_guarantees': ['Every original public and private helper/caller obligation remains required.', 'Separate Compress body flow/dependency, runtime safety and termination obligations must be fully discharged; all original caller checks and full strict report must pass.', 'Exact integrated source pins, independent current source review, complete matching runtime/authentic original controls and independent final acceptance remain required.'],
        'no_effectiveness_claim': True, 'target_execution': False, 'proof_acceptance': False, 'phase_acceptance': False})
    save('source-delta.json', {'schema': 'worldline-exact-source-delta-v1', 'changes': changes, 'source_only': True, 'target_execution': False, 'phase_acceptance': False})
    save('SOURCE-IDENTITY.json', {
        'schema': 'worldline-source-only-donor-identity-v1', 'author': 'CodexCompressContractCostUltraAuthor',
        'author_agent': '/root/proof_ultra', 'author_model': 'openai-codex/gpt-6.1-sol:ultra',
        'actual_author_launch': pin(P / 'author-model-provenance.json'),
        'source_selection': pin(T / 'integrated-candidate-v8/source-selection.json'),
        'current_source_opinion': pin(T / 'frame-review-draft/integrated-v8-independent-source-review.json'),
        'actual_partial_proof_observation': pin(T / 'formal-v8-passive-phase3-proof-cost-observation-v1.json'),
        'permitted_names': UNITS + [MANIFEST], 'source_inputs': {n: pin(S / n) for n in UNITS + [MANIFEST]},
        'source_only': True, 'target_execution': False, 'proof_acceptance': False, 'phase_acceptance': False})
    write('CHANGE.md', 'Disjoint unbuilt/unproved source-only proposal: add exact dependency and termination contracts to the two local SHA Compress procedures, preserve every executable byte and public specification, and add their private helper names to the complete original proof roster. Every affected existing body digest literal is refreshed with the unchanged original AST-isolated normalizer; all remaining policy/floor/boundary is exact. Independent review must assess the complete original guarantee and call/body coverage. No timeout efficacy, compiler/proof/runtime or acceptance credit is claimed. S8/D9/N8 remain unchanged.\n')
    write('prepare_source_only.py', Path(__file__).read_bytes())
    save('author-freeze.json', {'schema': 'worldline-source-only-donor-author-freeze-v1', 'author': 'CodexCompressContractCostUltraAuthor', 'author_agent': '/root/proof_ultra', 'author_model': 'openai-codex/gpt-6.1-sol:ultra', 'source_only': True, 'target_execution': False, 'proof_acceptance': False, 'phase_acceptance': False, 'files': {str(p.relative_to(P)): pin(p) for p in sorted(P.rglob('*')) if p.is_file()}})
    packet = save('source-author-packet-v1.json', {'schema': 'worldline-source-only-donor-author-packet-v1',
        'author_freeze': pin(P / 'author-freeze.json'), 'source_identity': pin(P / 'SOURCE-IDENTITY.json'),
        'source_delta': pin(P / 'source-delta.json'), 'contract_preservation_and_enrollment': pin(P / 'contract-preservation-and-enrollment.json'),
        'actual_author_launch': pin(P / 'author-model-provenance.json'), 'permitted_names': UNITS + [MANIFEST],
        'review_destination': str(P / 'independent-source-review.json'),
        'requested_disposition': 'QUALIFIED_EXACT_PRESERVED_BODY_COMPRESS_CONTRACT_COST_DONOR_SOURCE_ONLY',
        'required_review_boundary': 'Do not qualify any loss of original body/caller/check/functional/termination/domain obligations. New complete private helper enrollment is mandatory; runtime executable body/public equations/specs remain exact. No compiler acceptance or efficacy inferred.',
        'source_only': True, 'target_execution': False, 'proof_acceptance': False, 'phase_acceptance': False})
    print(json.dumps({'packet': packet, 'freeze': pin(P / 'author-freeze.json'), 'target_execution': False}, sort_keys=True))


if __name__ == '__main__':
    main()
