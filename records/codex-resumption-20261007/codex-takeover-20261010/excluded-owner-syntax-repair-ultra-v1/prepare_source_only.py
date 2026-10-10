"""Create an exclusive separate donor; never compile, prove, or alter predecessors."""
from pathlib import Path
import difflib
import hashlib
import json
import re
import shutil
import stat

D = Path(__file__).resolve().parent
T = D.parent
S = T / 'integrated-candidate-v5/source'
NAME = 'core/worldline-excluded_source_owner.adb'
ASPECT_NAMES = ('Hex_Matches', 'Bit', 'Sealed', 'FD_Number',
                'Descriptor_Reference', 'Process_Reference', 'Boolean_Is', 'Receipt_Source')
MODEL = 'openai-codex/gpt-6.1-sol:ultra'
AUTHOR = '/root/proof_ultra'

def pin(path):
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode) and not path.is_symlink()
    data = path.read_bytes()
    after = path.lstat()
    assert (before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
    return {'path': str(path), 'sha256': hashlib.sha256(data).hexdigest(),
            'bytes': after.st_size, 'mode': stat.S_IMODE(after.st_mode)}

def save(name, data):
    path = D / name
    with path.open('x') as stream:
        json.dump(data, stream, indent=2, sort_keys=True)
        stream.write('\n')

def main():
    assert __debug__
    before = (S / NAME).read_text()
    before_pin = pin(S / NAME)
    selected = json.loads((T / 'integrated-candidate-v5/stable-source-inventory.json').read_text())[NAME]
    assert selected['sha256'] == before_pin['sha256']
    assert selected['mode'] == before_pin['mode']
    assert selected['bytes'] == before_pin['bytes']
    assert not (D / 'source').exists() and not (D / 'author-freeze.json').exists()
    for name in (NAME, 'core/worldline-excluded_source_owner.ads', 'core/worldline_core_sources.gpr'):
        target = D / 'preimages' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(S / name, target)
        assert target.read_bytes() == (S / name).read_bytes()
    actual_provenance = T / 'proof_ultra-actual-launch-provenance.json'
    shutil.copy2(actual_provenance, D / 'author-model-provenance.json')
    actual = json.loads(actual_provenance.read_text())
    request = actual['actual_request_event']['payload']
    request_args = json.loads(request['arguments']) if isinstance(request['arguments'], str) else request['arguments']
    assert request_args['model'] == 'gpt-6.1-sol' and request_args['reasoning_effort'] == 'ultra'
    assert request_args['fork_turns'] == 'none'
    assert actual['actual_request_event']['metadata']['client_authored'] is False
    assert actual['actual_response_event']['metadata']['client_authored'] is False

    relocated = before
    relocations = []
    for name in ASPECT_NAMES:
        match = re.search(r'^   function ' + re.escape(name) + r'\b.*?(?=^   function |\Z)', relocated, re.M | re.S)
        assert match
        old = match.group()
        head, body = old.split(' is\n', 1)
        signature, aspects = head.split('\n     with ', 1)
        expression = body.rstrip()
        assert expression.startswith('     (') and expression.endswith(');')
        expression = expression[:-1]
        new = signature + ' is\n' + expression + '\n     with ' + aspects + ';\n'
        assert relocated.count(old) == 1
        relocated = relocated.replace(old, new, 1)
        relocations.append({'function': name, 'original_fragment': old, 'replacement_fragment': new,
                            'expression_bytes_preserved': True, 'aspect_bytes_preserved': True})

    # Ada strings and comments precede the identifier alternative. No byte in
    # either can be rewritten by the reserved-identifier alpha conversion.
    identifier_pattern = re.compile(r'--[^\n]*|"(?:[^"]|"")*"|\bAt\b', re.I)
    renames = []
    pieces = []
    cursor = 0
    output_offset = 0
    for match in identifier_pattern.finditer(relocated):
        if match.group().lower() != 'at':
            continue
        piece = relocated[cursor:match.start()]
        pieces.append(piece)
        output_offset += len(piece)
        renames.append({'original_offset': match.start(), 'original_line': relocated.count('\n', 0, match.start()) + 1,
                        'postimage_offset': output_offset, 'original_token': match.group(), 'replacement_token': 'Cursor'})
        pieces.append('Cursor')
        output_offset += len('Cursor')
        cursor = match.end()
    pieces.append(relocated[cursor:])
    post = ''.join(pieces)
    assert renames
    assert all(m.group().lower() != 'at' for m in identifier_pattern.finditer(post))

    inverse = post
    for rename in reversed(renames):
        start = rename['postimage_offset']
        assert inverse[start:start + len('Cursor')] == 'Cursor'
        inverse = inverse[:start] + rename['original_token'] + inverse[start + len('Cursor'):]
    assert inverse == relocated
    for move in reversed(relocations):
        assert inverse.count(move['replacement_fragment']) == 1
        inverse = inverse.replace(move['replacement_fragment'], move['original_fragment'], 1)
    assert inverse == before

    # Scope-preservation readback: strings/comments, public specification,
    # predicate equations, literal domains, aspect payloads and all other bytes
    # are invariant under the exact reversible transformations above.
    lexical = re.compile(r'--[^\n]*|"(?:[^"]|"")*"')
    assert lexical.findall(post) == lexical.findall(before)
    assert pin(S / NAME) == before_pin
    output = D / 'source' / NAME
    output.parent.mkdir(parents=True)
    output.write_text(post)
    output.chmod(before_pin['mode'])
    with (D / 'repair.patch').open('x') as stream:
        stream.writelines(difflib.unified_diff(before.splitlines(keepends=True), post.splitlines(keepends=True),
                          fromfile='preimages/' + NAME, tofile='source/' + NAME))
    save('exact-transformations.json', {'schema': 'worldline-excluded-owner-exact-syntax-transformations-v1',
         'aspect_relocations': relocations, 'identifier_alpha_conversions': renames,
         'inverse_transform_reconstructs_preimage_byte_exact': True,
         'strings_and_comments_byte_identical': True,
         'target_execution': False, 'phase_acceptance': False})
    source_inputs = {name: pin(S / name) for name in (NAME, 'core/worldline-excluded_source_owner.ads', 'core/worldline_core_sources.gpr')}
    save('SOURCE-IDENTITY.json', {'schema': 'worldline-source-only-donor-identity-v1',
         'author': 'CodexExcludedOwnerSyntaxRepairUltraAuthor', 'author_agent': AUTHOR, 'author_model': MODEL,
         'actual_author_launch': pin(D / 'author-model-provenance.json'),
         'source_selection': pin(T / 'integrated-candidate-v5/source-selection.json'),
         'source_inputs': source_inputs, 'permitted_names': [NAME],
         'source_only': True, 'target_execution': False, 'phase_acceptance': False})
    save('source-only-readback.json', {'schema': 'worldline-source-only-syntax-donor-readback-v1',
         'preimage': pin(D / 'preimages' / NAME), 'postimage': pin(output),
         'unchanged_specification': pin(D / 'preimages/core/worldline-excluded_source_owner.ads'),
         'unchanged_strict_project': pin(D / 'preimages/core/worldline_core_sources.gpr'),
         'exact_transformations': pin(D / 'exact-transformations.json'),
         'inverse_transform_reconstructs_preimage_byte_exact': True,
         'original_body_preimage_unchanged': pin(S / NAME) == before_pin,
         'source_files': [NAME], 'target_execution': False, 'compile_proof_runtime_acceptance': False})
    (D / 'CHANGE.md').write_text('Repair only the observed Ada grammar errors in the excluded owner body.\n\n'
        'Each retained expression-function Global/Depends aspect moves after its complete unchanged parenthesized expression. '
        'Every identifier token At becomes Cursor outside strings and comments, including the nested invocation selector and topology loop. '
        'The public specification, equations, literals, accepted domains, executable branches and proof obligations remain unchanged. '
        'The recorded inverse transforms reconstruct the complete original body byte for byte.\n\n'
        'The strict source GPR enrolls this body. D6 remains prepared and held unrun; N5 failed build evidence remains historical. '
        'No compiler, prover, fixture, target, approval, or acceptance ran in this donor. Full compilation and original strict proof remain open.\n')
    freeze_files = {}
    for path in sorted(D.rglob('*')):
        if path.is_file():
            freeze_files[str(path.relative_to(D))] = pin(path)
    save('author-freeze.json', {'schema': 'worldline-source-only-donor-author-freeze-v1',
         'author': 'CodexExcludedOwnerSyntaxRepairUltraAuthor', 'author_agent': AUTHOR, 'author_model': MODEL,
         'source_only': True, 'files': freeze_files, 'target_execution': False, 'phase_acceptance': False})
    print(json.dumps({'freeze': pin(D / 'author-freeze.json'), 'permitted_names': [NAME],
                      'postimage': pin(output), 'source_only': True, 'target_execution': False}, sort_keys=True))

if __name__ == '__main__':
    main()
