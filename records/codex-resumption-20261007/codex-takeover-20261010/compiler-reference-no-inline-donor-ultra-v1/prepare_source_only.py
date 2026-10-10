"""Prepare a disjoint compiler-only reference No_Inline contingency, without targets."""
from pathlib import Path
import ast
import difflib
import hashlib
import json
import stat

T = Path(__file__).resolve().parent
S = T / 'integrated-candidate-v8/source'
P = T / 'compiler-reference-no-inline-donor-ultra-v1'
MANIFEST = 'runtime/worldline/proof_manifest.py'
INSERTIONS = {
    'core/evaluation_raw_roster.ads': (
        'end Evaluation_Raw_Roster;',
        '   pragma No_Inline (Reference);\n'),
    'core/evaluation_finalization.ads': (
        'end Evaluation_Finalization;',
        '   pragma No_Inline\n'
        '     (Capture_Reference, Artifact_Binding, Seal_Classification_Equation,\n'
        '      Seal_Equation, Seal_Reference);\n'),
}
TARGETS = [
    'Evaluation_Raw_Roster.Reference',
    'Evaluation_Finalization.Capture_Reference',
    'Evaluation_Finalization.Artifact_Binding',
    'Evaluation_Finalization.Seal_Classification_Equation',
    'Evaluation_Finalization.Seal_Equation',
    'Evaluation_Finalization.Seal_Reference',
]


def pin(path):
    p = Path(path)
    a = p.lstat()
    raw = p.read_bytes()
    z = p.lstat()
    fields = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    assert stat.S_ISREG(a.st_mode) and not p.is_symlink() and fields(a) == fields(z)
    return {'path': str(p), 'sha256': hashlib.sha256(raw).hexdigest(),
            'bytes': len(raw), 'mode': stat.S_IMODE(z.st_mode)}


def write(name, value):
    p = P / name
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('xb') as f:
        f.write(value.encode() if isinstance(value, str) else value)
    p.chmod(0o644)
    return pin(p)


def save(name, value):
    return write(name, json.dumps(value, sort_keys=True, indent=2) + '\n')


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
            c = node.value
            if isinstance(c.func, ast.Attribute) and isinstance(c.func.value, ast.Name) and c.func.value.id == 'CONTRACT_PINS' and c.func.attr == 'update':
                assert len(c.args) == 1 and not c.keywords
                values['CONTRACT_PINS'].update(ast.literal_eval(c.args[0]))
    return values


def main():
    P.mkdir(exist_ok=False)
    changes = []
    for name, (ending, pragma) in INSERTIONS.items():
        old = (S / name).read_text()
        assert old.count(ending) == 1 and 'pragma No_Inline' not in old and 'Inline_Always' not in old
        new = old.replace(ending, pragma + ending, 1)
        assert new.replace(pragma, '', 1) == old
        write('preimage/' + name, old)
        write('source/' + name, new)
        changes.append({'name': name, 'before': pin(S / name), 'after': pin(P / 'source' / name),
                        'sole_added_compiler_pragma': pragma, 'whole_preimage_reconstructed_by_pragma_removal': True})

    old_manifest = (S / MANIFEST).read_text()
    tree = ast.parse(old_manifest)
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ('normalized_ada', 'contract_text', 'contract_pin')]
    assert {n.name for n in functions} == {'normalized_ada', 'contract_text', 'contract_pin'}
    isolated = ast.Module(body=[ast.ImportFrom(module='__future__', names=[ast.alias(name='annotations')], level=0), *functions], type_ignores=[])
    ns = {'Path': Path, 'hashlib': hashlib}
    exec(compile(ast.fix_missing_locations(isolated), str(S / MANIFEST), 'exec'), ns)
    before_policy = policy(old_manifest)
    assert set(TARGETS) <= set(before_policy['REQUIRED_PROVED'])
    affected = [k for k in before_policy['CONTRACT_PINS'] if k.partition('#')[0] in INSERTIONS]
    assert set(INSERTIONS) <= set(affected)
    derived = {k: ns['contract_pin'](P / 'source', k) for k in affected}
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
                stop = sum(len(x) for x in lines[:value.end_lineno - 1]) + value.end_col_offset
                quote = encoded[start:start + 1]
                assert quote in (b"'", b'"')
                replacements.append((start, stop, quote + derived[key.value].encode() + quote))
                literal_rows.append({'key': key.value, 'before': value.value, 'after': derived[key.value], 'line': value.lineno})
    rewritten = encoded
    for start, stop, replacement in sorted(replacements, reverse=True):
        rewritten = rewritten[:start] + replacement + rewritten[stop:]
    new_manifest = rewritten.decode()
    after_policy = policy(new_manifest)
    for key in ('MINIMUM_CHECKS', 'UNANALYZED_BOUNDARY', 'REQUIRED_PROVED', 'DECLARED_CORE_ADA_SOURCES'):
        assert after_policy[key] == before_policy[key]
    assert after_policy['CONTRACT_PINS'] == dict(before_policy['CONTRACT_PINS'], **derived)
    old_ast = ast.parse(old_manifest)
    new_ast = ast.parse(new_manifest)
    for x in (old_ast, new_ast):
        for node in ast.walk(x):
            if isinstance(node, ast.Dict):
                for key, value in zip(node.keys, node.values):
                    if isinstance(key, ast.Constant) and key.value in derived:
                        value.value = '__exact_affected_literal_pin__'
    assert ast.dump(old_ast, include_attributes=False) == ast.dump(new_ast, include_attributes=False)
    write('preimage/' + MANIFEST, old_manifest)
    write('source/' + MANIFEST, new_manifest)
    changes.append({'name': MANIFEST, 'before': pin(S / MANIFEST), 'after': pin(P / 'source' / MANIFEST),
                    'sole_delta': 'Only existing affected normalized spec digest literals; original policy AST and complete ordered roster unchanged.'})

    for reverse, filename in ((False, 'repair.patch'), (True, 'inverse.patch')):
        chunks = []
        for row in changes:
            name = row['name']
            old = (P / 'preimage' / name).read_text()
            new = (P / 'source' / name).read_text()
            a, b = (new, old) if reverse else (old, new)
            chunks.append(''.join(difflib.unified_diff(a.splitlines(True), b.splitlines(True),
                          fromfile=('b/' if reverse else 'a/') + name,
                          tofile=('a/' if reverse else 'b/') + name)))
        write(filename, ''.join(chunks))
    write('author-model-provenance.json', (T / 'proof_ultra-actual-launch-provenance.json').read_bytes())

    doc_root = Path('/home/sicarii/opt/gnat/gnatprove-aarch64-linux-16.1.0-1/libexec/spark/share/info')
    rm = (doc_root / 'gnat_rm.info').read_text()
    ugn = (doc_root / 'gnat_ugn.info').read_text()
    marker = 'File: gnat_rm.info,  Node: Pragma No_Inline,'
    a = rm.index(marker)
    b = rm.index('\x1f', a)
    write('references/installed-gnat16.1-No_Inline.txt', rm[:rm.index('\x1f')] + '\n' + rm[a:b])
    marker = '‘-fno-inline’'
    a = ugn.index(marker)
    b = ugn.index('‘-fno-ivopts’', a)
    write('references/installed-gnat16.1-inlining-controls.txt', ugn[:ugn.index('\x1f')] + '\n' + ugn[a:b])
    save('references/compiler-and-proof-semantics.json', {
        'installed_primary_manuals': {n: pin(doc_root / n) for n in ('gnat_rm.info', 'gnat_ugn.info')},
        'installed_revision': 'GCC version16.1.0; GNAT manual Jan09,2026',
        'installed_No_Inline_node': 'GNAT RM 2.117: Pragma No_Inline',
        'primary_GNAT_url': 'https://docs.adacore.com/gnat_rm-docs/html/gnat_rm/gnat_rm/implementation_defined_pragmas.html#pragma-no-inline',
        'primary_SPARK_RM_url': 'https://docs.adacore.com/live/wave/spark2014/html/spark2014_rm/language-defined-pragmas.html#gnat-implementation-defined-pragmas',
        'SPARK_RM_reference_release': '28.0w; separate from installed compiler16.1 revision',
        'compiler_semantics': 'Suppresses compiler inlining of the named callable, including pragma Inline inlining; active independently of -gnatn/-gnatN. Inline_Always conflict is illegal and absent from affected units.',
        'proof_semantics': 'SPARK RM lists GNAT No_Inline as permitted with no effect on contextual analysis of subprograms. The compiler pragma is not a GNATprove proof annotation. Original expression equations, helper bodies, existing contracts, contextual analysis and all caller/body obligations remain required.',
        'actual_acceptance_boundary': 'Primary manuals and unchanged source equations establish intended semantics, not installed compiler acceptance, cost efficacy or proof completion; complete actual original build/full strict proof/matching runtime still required.'})
    for name in ('core/evaluation_finalization.adb', 'core/evaluation_raw_roster.adb',
                 'core/worldline_core_sources.gpr', 'refresh_contract_pins.py'):
        write('references/source8/' + name, (S / name).read_bytes())
    save('cost-source-justification.json', {
        'actual_D9_owned_compiler_observation': pin(T / 'formal-v9-passive-compiler-owned-observation-v1.json'),
        'actual_D9_expansion_observation': pin(T / 'formal-v9-passive-compiler-expansion-observation-v2.json'),
        'selected_targets': TARGETS,
        'selection': {
            'Evaluation_Raw_Roster.Reference': 'Full classification reference called from Capture_Reference, Seal classification equations, Seal_Reference and checked Seal equalities; raw-roster compiler also observed in actual prior native/core campaign.',
            'Evaluation_Finalization.Capture_Reference': 'Full capture/classification expression used in checked Classify_Capture and Seal post; actual assembly contains capture_reference and classify_capture wrappers.',
            'Evaluation_Finalization.Artifact_Binding': 'Full canonical artifact/source binding expression repeated in runtime Seal and full postconditions; actual assembly contains artifact_binding and checked Seal wrapper.',
            'Evaluation_Finalization.Seal_Classification_Equation': 'Full ghost classification expression repeated in Seal_Equation; actual assembly emits ghost classification equation under retained assertion checks.',
            'Evaluation_Finalization.Seal_Equation': 'Full ghost result equation of Seal_Reference post; retained unabridged equation is required both at runtime and in original full proof.',
            'Evaluation_Finalization.Seal_Reference': 'Full checked reference called by Seal full result-equality post; current actual assembly emission reaches Seal checked wrapper with large text/exception tables.'},
        'minimal_scope': 'Named reference cut points only. No global inlining switch, no changes to consequential decisions, Seal executable body, original inputs/contracts/equations/caps or debug/optimization/assertion flags. No small scalar helper targets.',
        'general_vs_assignment_tracking': 'S8 leaves general variable tracking enabled, disables assignment tracking only. This independent contingency targets native body expansion; it is not a general tracking flag or proof-inlining change.',
        'causality_limit': 'Actual source/assembly/process observations identify large checked reference expansion, not a profiler-isolated dominant cost. No fixed-deadline D9 outcome or efficacy is inferred.'})
    save('contract-and-policy-preservation.json', {
        'schema': 'worldline-compiler-only-no-inline-full-guarantee-preservation-v1',
        'permitted_names': list(INSERTIONS) + [MANIFEST],
        'selected_targets_already_in_original_required_order': TARGETS,
        'full_original_required_order': before_policy['REQUIRED_PROVED'],
        'full_current_required_order': after_policy['REQUIRED_PROVED'],
        'original_floor': before_policy['MINIMUM_CHECKS'],
        'original_boundary': sorted(before_policy['UNANALYZED_BOUNDARY']),
        'original_declared_core_roster': sorted(before_policy['DECLARED_CORE_ADA_SOURCES']),
        'affected_literal_rows': literal_rows,
        'derived_effective_pins': derived,
        'normalizer_derivation': 'Unchanged original AST-isolated normalized_ada/contract_text/contract_pin only; no target module imports.',
        'entire_public_specs_preserved_except_compiler_pragmas': True,
        'entire_executable_and_ghost_bodies_byte_identical': True,
        'all_original_public_contracts_reference_equations_accepted_domains_unchanged': True,
        'all_original_flags_checks_commands_deadlines_caps_rosters_unchanged': True,
        'no_proof_annotation_assumption_skip_hide_waiver_or_input_cap': True,
        'mandatory_evidence': 'Complete same-final-source build/full strict proof with every original functional, flow, RTE and termination obligation, full runtime/authentic original controls and independent final acceptance. Changed code-generation call layout must pass original runtime bounds and ABI checks.',
        'Compress_donor_relationship': 'Separate unselected contingency; no Compress contract/pin/enrollment additions included here. Any composition must preserve every original equation/body/caller obligation and both reviewed deltas.',
        'target_execution': False, 'proof_acceptance': False, 'phase_acceptance': False})
    save('source-delta.json', {'schema': 'worldline-exact-source-delta-v1', 'changes': changes,
                              'source_only': True, 'target_execution': False, 'phase_acceptance': False})
    save('SOURCE-IDENTITY.json', {
        'schema': 'worldline-source-only-donor-identity-v1', 'author': 'CodexCompilerReferenceNoInlineUltraAuthor',
        'author_agent': '/root/proof_ultra', 'author_model': 'openai-codex/gpt-6.1-sol:ultra',
        'actual_author_launch': pin(P / 'author-model-provenance.json'),
        'source_selection': pin(T / 'integrated-candidate-v8/source-selection.json'),
        'current_source_opinion': pin(T / 'frame-review-draft/integrated-v8-independent-source-review.json'),
        'permitted_names': list(INSERTIONS) + [MANIFEST],
        'source_inputs': {n: pin(S / n) for n in list(INSERTIONS) + [MANIFEST]},
        'source_only': True, 'target_execution': False, 'proof_acceptance': False, 'phase_acceptance': False})
    write('CHANGE.md', 'Disjoint source-only compiler No_Inline contingency at exact heavy reference cut points. Removing only the new compiler pragma blocks reconstructs both entire original specifications. All executable/ghost bodies, public contracts, complete equations, accepted inputs, proof policy/order/floor/boundary, original O2/g/assertion flags/commands/caps/deadlines remain exact. Only existing affected normalized spec pin literals are refreshed. Installed GNAT16.1 primary manuals and SPARK RM distinguish compiler inlining from contextual proof analysis. No compiler/proof/cost/runtime/acceptance credit; S8/D9/N8 stay unchanged.\n')
    write('prepare_source_only.py', Path(__file__).read_bytes())
    save('author-freeze.json', {
        'schema': 'worldline-source-only-donor-author-freeze-v1', 'author': 'CodexCompilerReferenceNoInlineUltraAuthor',
        'author_agent': '/root/proof_ultra', 'author_model': 'openai-codex/gpt-6.1-sol:ultra',
        'source_only': True, 'target_execution': False, 'proof_acceptance': False, 'phase_acceptance': False,
        'files': {str(p.relative_to(P)): pin(p) for p in sorted(P.rglob('*')) if p.is_file()}})
    packet = save('source-author-packet-v1.json', {
        'schema': 'worldline-source-only-donor-author-packet-v1',
        'author_freeze': pin(P / 'author-freeze.json'), 'source_identity': pin(P / 'SOURCE-IDENTITY.json'),
        'source_delta': pin(P / 'source-delta.json'),
        'contract_and_policy_preservation': pin(P / 'contract-and-policy-preservation.json'),
        'cost_source_justification': pin(P / 'cost-source-justification.json'),
        'actual_author_launch': pin(P / 'author-model-provenance.json'),
        'permitted_names': list(INSERTIONS) + [MANIFEST],
        'review_destination': str(P / 'independent-source-review.json'),
        'requested_disposition': 'QUALIFIED_EXACT_COMPILER_ONLY_REFERENCE_NO_INLINE_COST_DONOR_SOURCE_ONLY',
        'required_review_boundary': 'Compiler-only named No_Inline pragmas must preserve all original checks, full bodies/public equations/contracts/accepted domains and unchanged complete proof/caller/flow/RTE/termination coverage. No proof inlining annotation, efficacy or target acceptance inferred.',
        'source_only': True, 'target_execution': False, 'proof_acceptance': False, 'phase_acceptance': False})
    print(json.dumps({'packet': packet, 'freeze': pin(P / 'author-freeze.json'), 'target_execution': False}, sort_keys=True))


if __name__ == '__main__':
    main()
