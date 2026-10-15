"""Mechanical source/diff preparation only. Does not import or run the candidate."""
from pathlib import Path
import ast
import difflib
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
TARGET = ROOT / 'runtime/worldline/proof_manifest.py'
source = TARGET.read_text()

# Same algorithm as the retained proof_manifest normalizer; no target import.
def normalize(text):
    lines = []
    for line in text.splitlines():
        in_string = False
        cut = len(line)
        for index, char in enumerate(line):
            if char == '"':
                in_string = not in_string
            elif not in_string and line.startswith('--', index):
                cut = index
                break
        lines.append(line[:cut])
    return ' '.join(' '.join(lines).split())

mapping = {
    'wl_finalization_decide_v1': ('Finalization_Decide', 'evaluation_finalization_c'),
    'wl_collapse_decide_finalization_v1': ('Finalization_Decide_Mixed', 'evaluation_finalization_c'),
    'wl_recovery_authorization_decide_v3': ('Owned_recovery_authorization_v3', 'worldline-recovery_authorization_v3_c_api'),
    'wl_recovery_protocol_decide_v1': ('Owned_recovery_protocol', 'worldline-recovery_protocol_c_api'),
    'wl_chain_authority_replay_v1': ('Owned_Chain_Replay', 'worldline-chain_authority_c_api'),
}
spec = normalize((ROOT / 'core/worldline-c_api.ads').read_text())
declarations = {}
units = {'core/worldline-c_api.ads', 'core/worldline-c_api.adb'}
for symbol, (name, unit) in mapping.items():
    start = spec.index('function ' + name + ' ')
    terminator = 'External_Name => "' + symbol + '";'
    end = spec.index(terminator, start) + len(terminator)
    declarations[symbol] = spec[start:end]
    units.update({'core/' + unit + '.ads', 'core/' + unit + '.adb'})
pins = {unit: hashlib.sha256(normalize((ROOT / unit).read_text()).encode()).hexdigest()
        for unit in sorted(units)}

helper = '''# The public ABI stayed in C_API when typed semantic entries gained observer
# parameters. These identities are additional migration guards, NOT replacement
# CONTRACT_PINS or a proof of their contents. Full contract/source/proof/ABI gates
# remain required. Review complete units before changing any value below: they
# include aliases, bounds, copies, helpers, status branches and exception paths.
_TYPED_EXPORT_DECLARATIONS = ''' + repr(declarations) + '''
_TYPED_EXPORT_UNIT_PINS = ''' + repr(pins) + '''


def _uses_typed_export_layout(text: str) -> bool:
    # A partial or mixed migration takes the strict typed branch and refuses.
    return any('"' + symbol + '"' in text for symbol in _TYPED_EXPORT_DECLARATIONS)


def _typed_export_correspondence_problems(root: Path) -> list[str]:
    """Closed reviewed transport layout; never infer authority from symbol presence.

    The literal inventory catches direct aspect/pragma/link-name duplicates.
    It is not an Ada constant-expression resolver or linker symbol audit. The
    unchanged complete source inventory and CONTRACT_PINS additionally reject
    nonliteral aliases/new sources; linked ELF/ABI controls remain required.
    """
    problems = []
    texts = {}
    paths = sorted(set((root / 'core').rglob('*.ads')) |
                   set((root / 'core').rglob('*.adb')))
    for path in paths:
        relative = path.relative_to(root).as_posix()
        try:
            texts[relative] = normalized_ada(path.read_text(encoding='utf-8'))
        except (OSError, UnicodeError) as exc:
            problems.append(f'typed export source unreadable: {relative}: {exc}')
    spec = texts.get('core/worldline-c_api.ads', '')
    for symbol, declaration in _TYPED_EXPORT_DECLARATIONS.items():
        locations = [relative for relative, text in texts.items()
                     for _ in range(text.count('"' + symbol + '"'))]
        if locations != ['core/worldline-c_api.ads']:
            problems.append(f'typed export binding inventory differs: {symbol}: {locations}')
        if spec.count(declaration) != 1:
            problems.append(f'typed export ABI declaration differs: {symbol}')
    for relative, expected in _TYPED_EXPORT_UNIT_PINS.items():
        text = texts.get(relative)
        if text is None or hashlib.sha256(text.encode('utf-8')).hexdigest() != expected:
            problems.append(f'typed export complete transport unit differs: {relative}')
    return problems


'''

tree = ast.parse(source)
functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'export_problems']
lines = source.splitlines(keepends=True)
replacements = []
base = ''.join(lines[functions[0].lineno - 1:functions[0].end_lineno])
old = '''    finalization = normalized_ada((root / 'core/evaluation_finalization_c.ads').read_text(encoding='utf-8'))
'''
base = base.replace(old, '''    if problems:
        return problems
    typed_layout = _uses_typed_export_layout(text)
    if typed_layout:
        problems.extend(_typed_export_correspondence_problems(root))
        if problems:
            return problems
    finalization = normalized_ada((root / 'core/evaluation_finalization_c.ads').read_text(encoding='utf-8'))
''')
base = base.replace('if finalization.count(\'External_Name => "wl_finalization_decide_v1"\') != 1 or final_entry not in finalization:',
                    'if not typed_layout and (finalization.count(\'External_Name => "wl_finalization_decide_v1"\') != 1 or final_entry not in finalization):')
base = base.replace('if finalization.count(\'External_Name => "wl_collapse_decide_finalization_v1"\') != 1 or mixed_entry not in finalization:',
                    'if not typed_layout and (finalization.count(\'External_Name => "wl_collapse_decide_finalization_v1"\') != 1 or mixed_entry not in finalization):')
base = base.replace("        if v3.count(f'External_Name => \"{symbol}\"') != 1:",
                    "        if typed_layout and symbol == 'wl_recovery_authorization_decide_v3':\n            continue  # Exact public profile and whole typed transport already checked.\n        if v3.count(f'External_Name => \"{symbol}\"') != 1:")
replacements.append((functions[0], helper + base))
for node in functions[1:]:
    body = ''.join(lines[node.lineno - 1:node.end_lineno])
    body_lines = body.splitlines(keepends=True)
    for i, line in enumerate(body_lines):
        if line.startswith('    problems = '):
            body_lines.insert(i + 1, '    if problems:\n        return problems\n')
            break
    body = ''.join(body_lines)
    if node.lineno == 964:
        body = body.replace("    text = normalized_ada((root / 'core/worldline-recovery_protocol_c_api.ads').read_text(encoding='utf-8'))",
            "    typed_layout = _uses_typed_export_layout(normalized_ada((root / 'core/worldline-c_api.ads').read_text(encoding='utf-8')))\n    text = normalized_ada((root / 'core/worldline-recovery_protocol_c_api.ads').read_text(encoding='utf-8'))")
        body = body.replace("        if text.count(f'External_Name => \"{symbol}\"') != 1:",
            "        if typed_layout and symbol == 'wl_recovery_protocol_decide_v1':\n            continue  # Exact public profile and whole typed transport already checked.\n        if text.count(f'External_Name => \"{symbol}\"') != 1:")
    if node.lineno == 979:
        body = body.replace("    spec = (root / 'core/worldline-chain_authority_c_api.ads').read_text()",
            "    typed_layout = _uses_typed_export_layout(normalized_ada((root / 'core/worldline-c_api.ads').read_text(encoding='utf-8')))\n    if typed_layout:\n        # Predecessor verified all exact wrapper/typed-unit identities, including\n        # Read_Anchors, every Read_Row/Decode, Write_Result(W.Decide(Owned,H)) and\n        # the C_API status-zero-only publication. No call-substring substitution.\n        return problems\n    spec = (root / 'core/worldline-chain_authority_c_api.ads').read_text()")
    replacements.append((node, body))

candidate = source
for node, replacement in reversed(replacements):
    before = ''.join(lines[:node.lineno - 1])
    after = ''.join(lines[node.end_lineno:])
    # Apply bottom-up offsets to the still-original prefix.
    start = len(before)
    end = len(source) - len(after)
    candidate = candidate[:start] + replacement + candidate[end:]

# Syntax-only parse of text is preparation, not module import or test execution.
ast.parse(candidate)
patch = ''.join(difflib.unified_diff(source.splitlines(True), candidate.splitlines(True),
    fromfile='a/runtime/worldline/proof_manifest.py', tofile='b/runtime/worldline/proof_manifest.py'))
(OUT / 'proof_manifest-export-guard-candidate-v1.py').write_text(candidate)
(OUT / 'proof_manifest-export-guard-v1.patch').write_text(patch)
receipt = {
    'evidence_class': 'MEASURED',
    'purpose': 'source-only proposal formation; candidate NOT EXECUTED, NOT APPLIED, NOT PROVED',
    'commit_observed': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    'command': 'python3 -B scratch/acquisition2/resume-20261015-v1/form_export_guard_proposal_v1.py',
    'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in [TARGET] + [ROOT / u for u in sorted(units)]},
    'proposed_normalized_transport_pins': pins,
    'per_symbol_correspondence': mapping,
    'candidate_sha256': hashlib.sha256(candidate.encode()).hexdigest(),
    'patch_sha256': hashlib.sha256(patch.encode()).hexdigest(),
    'CONTRACT_PINS': 'unchanged; existing mismatches remain independent refusals',
    'audit_limits': 'No linker/ABI/runtime/proof checks. New identities require coordinator/reviewer approval before application. Legacy path retains original checks; no historical positive execution claimed.'
}
(OUT / 'export-guard-preparation-receipt-v1.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
