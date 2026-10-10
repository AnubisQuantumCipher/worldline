"""Exact source/data adaptation and additive guards for the inherited formal frame.

Importing this module performs no target, capture or window operation.
The original admitted owners explicitly call its guards and bounded custody helpers.
"""
from pathlib import Path
import ast
import contextlib
import hashlib
import json
import os
import shutil
import stat
import signal
import subprocess
import time
import sys

sys.dont_write_bytecode = True
R = Path(__file__).resolve().parent.parent
F = R / 'formal-successor-v12'
DRAFT = R / 'formal-successor-v24-preparation' / 'source-data-author-inputs'
CANDIDATE = R / 'formal-successor-v24-preparation'
INSTALLED = Path('/home/sicarii/opt/gnat/gnatprove-aarch64-linux-16.1.0-1')
MODEL = 'openai-codex/gpt-6.1-sol:max'
AUTHOR = 'SolPhaseOneIntegration'
GOAL = '01a1149d-db62-74b0-a5f7-b0239f285c44'
MODE = 'full-strict-formal-diagnostic'
COMMAND = [str(INSTALLED / 'bin/gnatprove'), '-P', 'core/worldline_core_sources.gpr',
           '-U', '--mode=all', '--level=3', '--report=all', '--checks-as-errors=on',
           '--proof-warnings=on', '-j2']
SIX_FILES = ('prepare_successor.py', 'authorization.py', 'inherited-pins.json',
             'CHANGE.md', 'source-bindings.json', 'proof-obligations.json')
SOURCE_OUTPUTS = ('obj', 'lib', 'resource-tests/obj', 'resource-tests/bin')
DEPENDENCY_OUTPUTS = ('lib/gnat/sparklib_obj', 'lib/gnat/sparklib_lib', 'lib/gnat/proof')
DEPENDENCY_PROJECTS = ('lib/gnat/sparklib.gpr', 'lib/gnat/sparklib_common.gpr')
DEPENDENCY_UNSET = ('GPR_TOOL', 'GPR_PROJECT_PATH_FILE', 'GPR_CONFIG', 'GPR_RUNTIME_PATH',
                    'SPARKLIB_INSTALLED', 'SPARKLIB_MODE', 'SPARKLIB_BUILD',
                    'SPARKLIB_LIBRARY_TYPE', 'LIBRARY_TYPE')
CLOSURE_FILES = ('launch-environment.json', 'tool-inventory-template.json',
                 'action-baseline.json', 'native-input-baseline.json',
                 'runtime-closure.json', 'proof-data-closure.json',
                 'proof-elf-baseline.json', 'vendor-template.json')


def sha(path):
    return pin(path)['sha256']


def pin(path):
    path = Path(path)
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode) and not path.is_symlink(), str(path)
    with path.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    after = path.lstat()
    fields = lambda row: (row.st_dev, row.st_ino, row.st_mode, row.st_size,
                          row.st_mtime_ns, row.st_ctime_ns)
    assert fields(before) == fields(after), ('Changed during read', str(path))
    return {'sha256': digest, 'bytes': after.st_size, 'mode': stat.S_IMODE(after.st_mode)}


def pinned(path):
    return {'path': str(Path(path)), **pin(path)}


def matched(row):
    assert set(row) == {'path', 'sha256', 'bytes', 'mode'}, row
    path = Path(row['path'])
    assert path.is_absolute() and pinned(path) == row, str(path)
    return path


def load(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    return pinned(path)


def under(name, roots):
    return any(name == root or name.startswith(root + '/') for root in roots)


def snapshot(root, outputs=()):
    """Complete stable no-follow keyset; only explicitly owned output roots are omitted."""
    root = Path(root)
    assert root.is_dir() and not root.is_symlink(), str(root)
    rows = {}
    def visit(path):
        name = path.relative_to(root).as_posix()
        before = path.lstat()
        mode = stat.S_IMODE(before.st_mode)
        if under(name, outputs):
            assert stat.S_ISDIR(before.st_mode) and not path.is_symlink(), name
            # Generated descendants are inspected separately, never followed as inputs.
            snapshot(path)
            return
        if stat.S_ISDIR(before.st_mode):
            rows[name] = {'kind': 'directory', 'mode': mode}
            for child in sorted(path.iterdir()):
                visit(child)
        elif stat.S_ISREG(before.st_mode):
            rows[name] = {'kind': 'file', **pin(path)}
        elif stat.S_ISLNK(before.st_mode):
            rows[name] = {'kind': 'symlink', 'mode': mode, 'target': os.readlink(path)}
        else:
            raise RuntimeError('Unsupported inventory entry: ' + str(path))
        after = path.lstat()
        fields = lambda row: (row.st_dev, row.st_ino, row.st_mode, row.st_size,
                              row.st_mtime_ns, row.st_ctime_ns)
        assert fields(before) == fields(after), ('Changed during traversal', name)
    visit(root)
    return rows


def source_snapshot(root):
    return snapshot(root, SOURCE_OUTPUTS)


def validate_entries(entries):
    assert isinstance(entries, dict) and entries.get('.', {}).get('kind') == 'directory'
    for name, row in entries.items():
        path = Path(name)
        assert name == '.' or (not path.is_absolute() and path.as_posix() == name
                               and '..' not in path.parts), name
        assert isinstance(row.get('mode'), int) and 0 <= row['mode'] <= 0o7777, name
        if row['kind'] == 'file':
            assert set(row) == {'kind', 'mode', 'bytes', 'sha256'}, name
            assert isinstance(row['bytes'], int) and row['bytes'] >= 0, name
            assert len(row['sha256']) == 64 and all(c in '0123456789abcdef' for c in row['sha256']), name
        elif row['kind'] == 'directory':
            assert set(row) == {'kind', 'mode'}, name
        elif row['kind'] == 'symlink':
            assert set(row) == {'kind', 'mode', 'target'} and isinstance(row['target'], str), name
        else:
            raise RuntimeError('Unknown entry kind: ' + name)
        if name != '.':
            parent = path.parent.as_posix()
            assert entries.get(parent, {}).get('kind') == 'directory', name
    return entries


def selected_entries(selection_path):
    """Bind either current direct kind/mode/hash maps or the historical nested inventory.

    Current inventories omit lengths. Real stable lengths are added only after the
    complete observed keyset/kinds/modes/hashes/links equal the explicitly selected map.
    """
    selection = load(selection_path)
    current = 'source' in selection and 'source_inventory' in selection
    historical = 'snapshot' in selection and 'full_candidate_inventory' in selection
    assert current != historical, 'Require exactly one supported complete selection representation'
    if current:
        source = Path(selection['source'])
        inventory_path = matched(selection['source_inventory'])
        declared = load(inventory_path)
        observed = source_snapshot(source)
        if declared and all('bytes' not in row for row in declared.values()):
            projected = {name: {k: v for k, v in row.items() if k != 'bytes'}
                         for name, row in observed.items()}
        else:
            projected = observed
        assert projected == declared, 'Complete selected source keyset/kind/mode/content/link mismatch'
        inventory_pin = pinned(inventory_path)
        if 'stable_source_inventory' in selection:
            assert load(matched(selection['stable_source_inventory'])) == observed, 'Complete stable inventory differs from selected frozen source'
    else:
        source = Path(selection['snapshot'])
        declared = selection['full_candidate_inventory']['entries']
        observed = source_snapshot(source)
        assert observed == declared, 'Historical complete source mismatch'
        inventory_pin = None
    assert source.is_absolute() and source.resolve() == source and source != CANDIDATE / 'source'
    entries = validate_entries(observed)
    assert not any(under(name, SOURCE_OUTPUTS) for name in entries), 'Selected generated outputs are not source'
    for name, row in entries.items():
        if row['kind'] == 'symlink':
            target = source / name
            assert target.resolve(strict=True).is_relative_to(source), ('Source link escapes', name)
            assert not under(target.resolve().relative_to(source).as_posix(), SOURCE_OUTPUTS), name
    return source, entries, inventory_pin


def exact_delta(before, after):
    return [{'path': name, 'before': before.get(name), 'after': after.get(name)}
            for name in sorted(set(before) | set(after)) if before.get(name) != after.get(name)]


def apply_delta(entries, delta, reverse=False):
    value = dict(entries)
    assert len({row['path'] for row in delta}) == len(delta), 'Repeated delta path'
    for row in reversed(delta) if reverse else delta:
        old, new = ('after', 'before') if reverse else ('before', 'after')
        name = row['path']
        assert value.get(name) == row[old], ('Delta preimage mismatch', name)
        if row[new] is None:
            assert name in value, name
            del value[name]
        else:
            value[name] = row[new]
    return value


def verify_delta(before, after, delta):
    assert exact_delta(before, after) == delta, 'Incomplete or unexpected source delta'
    assert apply_delta(before, delta) == after, 'Forward delta differs'
    assert apply_delta(after, delta, reverse=True) == before, 'Inverse delta differs'


def copy_entries(origin, destination, entries):
    origin, destination = Path(origin), Path(destination)
    assert not destination.exists() and not destination.is_symlink(), str(destination)
    validate_entries(entries)
    destination.mkdir()
    directories = []
    for name, row in sorted(entries.items(), key=lambda item: (len(Path(item[0]).parts), item[0])):
        path = destination / name
        if row['kind'] == 'directory':
            if name != '.':
                path.mkdir()
            directories.append((path, row['mode']))
        elif row['kind'] == 'symlink':
            path.symlink_to(row['target'])
        else:
            assert pin(origin / name) == {k: v for k, v in row.items() if k != 'kind'}, name
            shutil.copy2(origin / name, path)
    for path, mode in reversed(directories):
        path.chmod(mode)
    assert snapshot(destination) == entries, 'Copied complete inventory differs'


def rehome(value, old=F, new=CANDIDATE):
    if isinstance(value, str):
        return value.replace(str(old), str(new))
    if isinstance(value, list):
        return [rehome(item, old, new) for item in value]
    if isinstance(value, dict):
        return {rehome(k, old, new): rehome(v, old, new) for k, v in value.items()}
    return value


def independent(review, disposition, author=None):
    assert review['actual_model_selection'] == MODEL, 'Actual current GPT6.1 review required; no aliases/fallback'
    assert isinstance(review['author'], str) and review['author'].strip()
    assert isinstance(review['reviewer'], str) and review['reviewer'].strip()
    assert review['author'] != review['reviewer'] and review['reviewer'] != AUTHOR, 'No self-review'
    if author is not None:
        assert review['author'] == author, 'Wrong author identity'
    assert review['blocking_findings'] == [] and review['target_execution'] is False
    assert review['disposition'] == disposition, 'Review scope does not qualify this action'


def check_closure_review(root):
    """A proposed binding is data, never a review or drift acknowledgement."""
    root = Path(root)
    binding = load(root / 'source-bindings.json')
    choice = binding['current_closure_binding']
    if choice is None:
        return None
    row = choice['review']
    if row is None:
        gate = load(root / 'preparation-review.json')
        assert 'current_closure_review' in gate, 'Real independent current-closure review pin is missing from the genuine six-file review'
        row = gate['current_closure_review']
    reviewed = load(matched(row))
    independent(reviewed, 'QUALIFIED_EXACT_CURRENT_CLOSURE_BINDING_FOR_FORMAL_SUCCESSOR', AUTHOR)
    assert reviewed['current_closure_binding'] == choice['binding'], 'Current closure review binds another proposal'
    assert reviewed['historical_drift_acknowledgement'] == binding['pins']['historical_drift_acknowledgement']
    matched(choice['binding'])
    matched(binding['pins']['historical_drift_acknowledgement'])
    return row


def source_review(row, selection_row, inventory_row):
    value = load(matched(row))
    independent(value, 'QUALIFIED_EXACT_COMPLETE_SELECTED_SOURCE_FOR_FULL_STRICT_FORMAL_DIAGNOSTIC_ONLY')
    assert value['artifacts']['source-selection.json'] == selection_row
    assert value['artifacts']['source-inventory.json'] == inventory_row
    selection = load(matched(selection_row))
    for artifact in value['artifacts'].values():
        matched(artifact)
    for key, name in (('stable_source_inventory', 'stable-source-inventory.json'),
                      ('source_changes', 'source-changes.json'),
                      ('source_only_enrollment', 'enrollment-report.json')):
        if key in selection:
            assert value['artifacts'][name] == selection[key], ('Selected supplementary artifact is not reviewed', key)
    assert value['strict_proof'] is False and value['phase_acceptance'] is False
    return value


def manifest_data(path):
    """Interpret only reviewed top-level literal policy assignments; never import a target."""
    wanted = {'MINIMUM_CHECKS', 'REQUIRED_PROVED', 'UNANALYZED_BOUNDARY',
              'DECLARED_CORE_ADA_SOURCES', 'CONTRACT_PINS'}
    values = {}
    def literal(node):
        if isinstance(node, ast.Name) and node.id in values:
            return values[node.id]
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.BitOr)):
            left, right = literal(node.left), literal(node.right)
            return left + right if isinstance(node.op, ast.Add) else left | right
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ('frozenset', 'set', 'list', 'tuple'):
            assert len(node.args) <= 1 and not node.keywords
            constructors = {'frozenset': frozenset, 'set': set, 'list': list, 'tuple': tuple}
            return constructors[node.func.id](literal(node.args[0]) if node.args else ())
        return ast.literal_eval(node)
    for node in ast.parse(Path(path).read_text()).body:
        if isinstance(node, ast.Assign):
            selected = [target.id for target in node.targets if isinstance(target, ast.Name) and target.id in wanted]
            for name in selected:
                values[name] = literal(node.value)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id in wanted:
            values[node.target.id] = literal(node.value)
        elif isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name) and node.target.id in wanted:
            name, right = node.target.id, literal(node.value)
            assert isinstance(node.op, (ast.Add, ast.BitOr)), name
            values[name] = values[name] + right if isinstance(node.op, ast.Add) else values[name] | right
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            call = node.value
            if isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Name) and call.func.value.id in wanted:
                assert call.func.attr == 'update' and len(call.args) == 1 and not call.keywords
                values[call.func.value.id].update(literal(call.args[0]))
        elif not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            for child in ast.walk(node):
                if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store) and child.id in wanted:
                    raise RuntimeError('Nonliteral proof-policy assignment requires explicit adapter update: ' + child.id)
    assert set(values) == wanted, 'Complete current proof policy required'
    return values


def check_enrollment(path, source, entries, historical):
    report = load(path)
    policy = manifest_data(Path(source) / 'runtime/worldline/proof_manifest.py')
    prefix = historical['original_required_names']
    assert len(prefix) == 535 and report['inheritedPrefix'] == prefix
    assert policy['REQUIRED_PROVED'][:535] == prefix and report['requiredProved'] == policy['REQUIRED_PROVED']
    assert policy['MINIMUM_CHECKS'] == report['floor'] == 251
    assert sorted(policy['UNANALYZED_BOUNDARY']) == report['unanalyzedBoundary'] == ['worldline-c_api']
    actual = sorted(name for name in entries if name.startswith('core/') and Path(name).suffix in ('.ads', '.adb'))
    assert actual == sorted(policy['DECLARED_CORE_ADA_SOURCES']) == sorted(report['declaredCoreAdaSources'])
    assert policy['CONTRACT_PINS'] == report['effectiveContractPins'], 'Effective overrides/pins differ'
    for name in policy['CONTRACT_PINS']:
        assert name.partition('#')[0] in entries, name
    if 'root' in report:
        assert report['root'] == str(source), 'Enrollment must describe the exact selected frozen source root'
    if 'staleLiteralContractPins' in report:
        assert report['staleLiteralContractPins'] == [], 'Stale normalized contract literals remain'
    for row in report.get('sourceHashInputs', {}).values():
        path = matched(row)
        assert path.is_relative_to(source), 'Enrollment source-hash input escapes selected source'
        name = path.relative_to(source).as_posix()
        assert name in entries and entries[name]['kind'] == 'file'
        assert {key: row[key] for key in ('sha256', 'bytes', 'mode')} == {
            key: entries[name][key] for key in ('sha256', 'bytes', 'mode')}
    return report, policy


def dependency_plan():
    entries = {'.': {'kind': 'directory', 'mode': stat.S_IMODE(INSTALLED.stat().st_mode)}}
    for name in ('include', 'lib', 'lib/gnat'):
        path = INSTALLED / name
        assert path.is_dir() and not path.is_symlink(), name
        entries[name] = {'kind': 'directory', 'mode': stat.S_IMODE(path.stat().st_mode)}
    for name, row in snapshot(INSTALLED / 'include/spark').items():
        assert row['kind'] != 'symlink', 'Vendor alias requires separate review'
        entries['include/spark' + ('' if name == '.' else '/' + name)] = row
    for name in DEPENDENCY_PROJECTS:
        entries[name] = {'kind': 'file', **pin(INSTALLED / name)}
    inspected = load(R / 'phase1-v47-native-diagnostic-v1/dependency-inventory.json')
    for name in DEPENDENCY_PROJECTS:
        assert entries[name] == inspected['entries'][name], ('Vendor output/source/default routing changed since the inspected private pattern', name)
    outputs = {}
    for name in DEPENDENCY_OUTPUTS:
        path = INSTALLED / name
        assert not path.is_symlink(), name
        outputs[name] = snapshot(path) if path.exists() else None
    return {'schema': 'worldline-byte-identical-private-sparklib-v1',
            'installed_root': str(INSTALLED), 'private_root': str(CANDIDATE / 'private-sparklib'),
            'entries': validate_entries(entries), 'initial_output_inventory': outputs,
            'shared_output_inventory': outputs, 'output_directories': list(DEPENDENCY_OUTPUTS),
            'project_resolution': 'private lib/gnat first; byte-identical vendor projects and all actual vendor sources',
            'source_mode': 'full', 'compiler_mode': 'Production', 'library_kind': 'static',
            'Proof_Dir_literal': 'proof',
            'Proof_Dir_containment': 'Renamed vendor Prove package remains byte-identical; both project-relative lib/gnat/proof and object-relative sparklib_obj/proof are owned private outputs',
            'proof_only_substitution': False, 'shared_install_writes_allowed': False,
            'GPR_TOOL_override': False, 'execution_credit': False}


def check_dependency(root):
    root = Path(root)
    plan = load(root / 'dependency-inventory.json')
    assert plan['installed_root'] == str(INSTALLED)
    private = root / 'private-sparklib'
    assert plan['private_root'] == str(private) and plan['output_directories'] == list(DEPENDENCY_OUTPUTS)
    assert snapshot(private, DEPENDENCY_OUTPUTS) == plan['entries'], 'Private dependency keyset/kind/mode/content changed'
    original = dependency_plan()
    assert original['entries'] == plan['entries'], 'Actual installed SPARK sources/projects changed'
    assert original['shared_output_inventory'] == plan['shared_output_inventory'], 'Shared SPARK output drift; never a private output'
    return {'private_immutable_entries': plan['entries'], 'shared_outputs_unchanged': True,
            'private_outputs': {name: snapshot(private / name) if (private / name).exists() else None
                                for name in DEPENDENCY_OUTPUTS}, 'acceptance': False}


def check_source_and_dependency(root):
    root = Path(root)
    source = source_snapshot(root / 'source')
    assert source == load(root / 'selected-source-entries.json'), 'Complete source keyset/kind/mode/content/link drift'
    check_current_project_routing(root / 'source', source)
    return {'complete_source_entries': source, 'dependency': check_dependency(root),
            'current_closure_review': check_closure_review(root), 'acceptance': False}


def child_environment(root, environment):
    result = dict(environment)
    for key in DEPENDENCY_UNSET:
        assert result.get(key) is None, ('Unexpected project/source/mode override', key)
    inherited = load(Path(root) / 'inherited-protected-environment.json')
    assert result['GPR_PROJECT_PATH'] == inherited['GPR_PROJECT_PATH']
    result['GPR_PROJECT_PATH'] = str(Path(root) / 'private-sparklib/lib/gnat') + ':' + result['GPR_PROJECT_PATH']
    return result


def generated_outputs(root):
    root = Path(root)
    names = tuple('source/' + name for name in SOURCE_OUTPUTS) + tuple('private-sparklib/' + name for name in DEPENDENCY_OUTPUTS)
    return {name: snapshot(root / name) if (root / name).exists() else None for name in names}


def file_rows(root, entries):
    root = Path(root)
    rows = {}
    for name, row in entries.items():
        path = root / name
        if row['kind'] == 'file':
            rows[name] = {k: v for k, v in row.items() if k != 'kind'}
        elif row['kind'] == 'symlink' and path.is_file():
            assert path.resolve(strict=True).is_relative_to(root), name
            rows[name] = pin(path.resolve(strict=True))
    return rows


def retained_readback(root):
    try:
        return {'matches': True, 'actual': check_source_and_dependency(root)}
    except (OSError, AssertionError, RuntimeError, ValueError) as error:
        return {'matches': False, 'error': repr(error), 'acceptance': False,
                'meaning': 'Unavailable or changed immutable inputs; no inferred equivalence'}


def adapt_machinery(name, text):
    """Exact affected inserts into the original machinery, not a replacement launcher."""
    replacements = {
        'run_checks.py': [
            ('import authorization\n', 'import authorization\nimport successor_support\n'),
            ("    authorization.check('dispatch')\n    config =", "    authorization.check('dispatch')\n    write(receipt / 'private-inputs-child-before.json', successor_support.check_source_and_dependency(root))\n    expected_environment = json.loads((root / 'tool-inventory-template.json').read_text())['tool_inventory_spec']['effective_environment']\n    assert {key: os.environ.get(key) for key in expected_environment} == expected_environment, 'Actual strict-child protected environment drift'\n    config ="),
            ("environment['GPR_PROJECT_PATH'] = str(gnat / 'gnatprove-aarch64-linux-16.1.0-1/lib/gnat') + ':' + str(gnat / 'auxiliary/share/gpr')\n", "environment['GPR_PROJECT_PATH'] = str(gnat / 'gnatprove-aarch64-linux-16.1.0-1/lib/gnat') + ':' + str(gnat / 'auxiliary/share/gpr')\nenvironment = successor_support.child_environment(root, environment)\n"),
            ("runtime_closure = json.loads((root / 'runtime-closure.json').read_text())\n", "write(receipt / 'private-inputs-before.json', successor_support.check_source_and_dependency(root))\nruntime_closure = json.loads((root / 'runtime-closure.json').read_text())\n"),
            ("result = {'at': now(), 'scope_wait': code, 'inputs_unchanged': unchanged,\n", "private_after = successor_support.retained_readback(root)\nwrite(receipt / 'private-inputs-after.json', private_after)\nwrite(receipt / 'owned-generated-output-inventory.json', successor_support.generated_outputs(root))\nunchanged = unchanged and private_after['matches']\nresult = {'at': now(), 'scope_wait': code, 'inputs_unchanged': unchanged,\n"),
        ],
        'review/root-live-lane-v1/live_check.py': [
            ("def check_inputs(out,env):\n", "def check_inputs(out,env):\n    import sys\n    sys.path.insert(0, str(D))\n    import successor_support\n    save(out, 'private-source-dependency-readback.json', successor_support.check_source_and_dependency(D))\n"),
        ],
        'review/root-terminal-v1/collect_terminal.py': [
            ("import authorization\n", "import authorization\nimport successor_support\n"),
            ("save('complete-source-readback.json',", "private_readback = successor_support.retained_readback(D)\nsource_match = source_match and private_readback['matches']\nsave('private-source-dependency-readback.json', private_readback)\nsave('owned-generated-output-inventory.json', successor_support.generated_outputs(D))\nsave('complete-source-readback.json',"),
            ("for base in (D/'source',D/'evidence',D/'native-artifacts',D/'review/root-live-lane-v1/attempts',D/'review/root-outer-capture-v1'):", "for base in (D/'source',D/'private-sparklib',D/'evidence',D/'native-artifacts',D/'review/root-live-lane-v1/attempts',D/'review/root-outer-capture-v1'):"),
        ],
    }
    for before, after in replacements.get(name, ()):
        assert text.count(before) == 1, ('Unexpected machinery preimage', name, before)
        text = text.replace(before, after)
    if name in DEADLINE_MACHINERY:
        row = DEADLINE_MACHINERY[name]
        assert matched(row['preimage']).read_text() == text, ('Exact C22 adapted machinery preimage changed', name)
        text = matched(row['template']).read_text()
    return text


def json_delta(before, after, path=()):
    if isinstance(before, dict) and isinstance(after, dict):
        rows = []
        for key in sorted(set(before) | set(after)):
            if key in before and key in after:
                rows.extend(json_delta(before[key], after[key], path + (key,)))
            else:
                rows.append({'path': list(path + (key,)), 'before_present': key in before,
                             'after_present': key in after, 'before': before.get(key),
                             'after': after.get(key)})
        return rows
    if before == after:
        return []
    return [{'path': list(path), 'before_present': True, 'after_present': True,
             'before': before, 'after': after}]


def apply_json_delta(value, delta, reverse=False):
    # JSON round-trip detaches nested mappings before reversible mutation.
    value = json.loads(json.dumps(value))
    assert len({tuple(row['path']) for row in delta}) == len(delta), 'Repeated JSON delta path'
    for row in reversed(delta) if reverse else delta:
        old, new = ('after', 'before') if reverse else ('before', 'after')
        path = row['path']
        if not path:
            assert row[old + '_present'] and value == row[old]
            assert row[new + '_present']
            value = row[new]
            continue
        parent = value
        for key in path[:-1]:
            assert isinstance(parent, dict) and key in parent, path
            parent = parent[key]
        key = path[-1]
        assert (key in parent) == row[old + '_present'], path
        if row[old + '_present']:
            assert parent[key] == row[old], path
        if row[new + '_present']:
            parent[key] = row[new]
        else:
            del parent[key]
    return value


def check_closure_contract(documents):
    """Changing identities needs review; removing inherited check inputs is forbidden."""
    assert set(documents) == set(CLOSURE_FILES)
    inherited = {name: load(F / name) for name in CLOSURE_FILES}
    old = inherited['tool-inventory-template.json']['tool_inventory_spec']
    new = documents['tool-inventory-template.json']['tool_inventory_spec']
    for name in ('roots', 'direct_paths', 'path_commands'):
        assert new[name] == old[name], ('Original tool closure check removed/reordered', name)
    assert set(new['effective_environment']) == set(old['effective_environment'])
    for name, value in old['effective_environment'].items():
        if name != 'PATH':
            assert new['effective_environment'][name] == value, ('Original protected environment changed', name)
    for name in ('runtime-closure.json', 'proof-data-closure.json'):
        assert documents[name]['spec'] == inherited[name]['spec'], ('Original closure discovery/check specification changed', name)
    assert set(documents['action-baseline.json']['manager_environment']) == set(inherited['action-baseline.json']['manager_environment'])
    assert documents['action-baseline.json']['source_files'] == inherited['action-baseline.json']['source_files']
    assert [row['original'] for row in documents['vendor-template.json']] == [row['original'] for row in inherited['vendor-template.json']]
    prefixes = ':'.join('/home/sicarii/opt/gnat/' + name + '/bin' for name in
        ('gnat-aarch64-linux-16.1.0-1', 'gprbuild-aarch64-linux-26.0.0-1', 'gnatprove-aarch64-linux-16.1.0-1'))
    assert new['effective_environment']['PATH'] == prefixes + ':' + documents['launch-environment.json']['PATH']
    return inherited


def check_historical_source_history():
    """Repeat F12's exact historical source checks without transferring qualification."""
    check_historical_acknowledgement()
    binding = load(F / 'source-bindings.json')
    for key in ('source_selection', 'source_review', 'formal_inventory',
                'predecessor_preparation_review', 'd7_terminal', 'd8_terminal',
                'd9_terminal', 'base_source_selection', 'base_source_review',
                'base_formal_inventory', 'raw_fixture_review', 'base_frame_freeze'):
        matched(binding[key])
    old_review = load(matched(binding['source_review']))
    assert old_review['actual_model_selection'] == 'gpt-6.1-sol'
    assert old_review['author'] != old_review['reviewer'] and old_review['blocking_findings'] == []
    assert old_review['target_execution'] is False
    assert old_review['source_selection'] == binding['source_selection']
    assert old_review['formal_source_inventory'] == binding['formal_inventory']
    assert old_review['disposition'] == 'QUALIFIED_EXACT_V24_PLUS_QUANTITY_DIRECT_REFERENCE_SOURCE_DIAGNOSTIC_COMPOSITION'
    base_review = load(matched(binding['base_source_review']))
    assert base_review['actual_model_selection'] == 'gpt-6.1-sol' and base_review['blocking_findings'] == []
    assert base_review['author'] != base_review['reviewer']
    assert base_review['artifacts']['author-freeze.json'] == binding['base_frame_freeze']
    assert base_review['artifacts']['final-source-inventory.json'] == binding['base_formal_inventory']
    base_source, base_entries, _ = selected_entries(matched(binding['base_source_selection']))
    source, entries, _ = selected_entries(matched(binding['source_selection']))
    assert file_rows(base_source, base_entries) == load(matched(binding['base_formal_inventory']))
    assert file_rows(source, entries) == load(matched(binding['formal_inventory']))
    verify_delta(base_entries, entries, binding['complete_base_to_current_delta'])
    return binding


def check_historical_acknowledgement():
    descriptor = load(F / 'historical-drift-acknowledged-rows.json')
    acknowledgement = load(matched(descriptor['acknowledgement']))
    assert acknowledgement['schema'] == 'lead-explicit-historical-identity-drift-acknowledgement-v1'
    approval = acknowledgement['operator_approval']
    matched({key: approval[key] for key in ('path', 'sha256', 'bytes', 'mode')})
    assert matched(descriptor['operator_approval']) == Path(approval['path'])
    rows = {row['path']: row for row in acknowledgement['rows']}
    assert len(rows) == len(acknowledgement['rows']) == 2
    assert set(rows) == set(descriptor['used']) == {
        str(INSTALLED / 'lib/gnat/sparklib_lib/libsparklib.a'),
        str(INSTALLED / 'lib/gnat/sparklib_obj/sparklib.lexch')}
    # These exact historical/approved-current rows are retained as history only.
    # A separately reviewed current closure never rewrites or widens them.
    assert descriptor['history_only'] is True and descriptor['target_execution'] is False
    return descriptor


def check_current_project_routing(source, entries):
    import re
    imports = []
    names = {'sparklib', 'sparklib_common'}
    for name, row in entries.items():
        if Path(name).suffix.lower() != '.gpr' or row['kind'] not in ('file', 'symlink'):
            continue
        assert Path(name).stem.lower() not in names, ('Source-local vendor project would shadow private byte-identical dependency', name)
        text = Path(source, name).read_text()
        text = re.sub(r'--[^\n]*', '', text)
        for clause in re.findall(r'\bwith\s+([^;]+);', text, flags=re.IGNORECASE):
            for imported in re.findall(r'"([^"]+)"', clause):
                if Path(imported).stem.lower() in names:
                    assert imported.lower() in ('sparklib', 'sparklib.gpr', 'sparklib_common', 'sparklib_common.gpr'), ('Vendor import bypasses private project lookup', name, imported)
                    imports.append({'project': name, 'import': imported})
    return {'vendor_imports': imports, 'private_project_resolution': 'GPR_PROJECT_PATH prefix; no source-local vendor shadow or installed absolute import', 'proof_acceptance': False}


class OwnerStop(BaseException):
    """Observed owner signal, never a reconstructed child return code."""
    def __init__(self, number):
        self.number = number
        super().__init__('owner received signal ' + str(number))


@contextlib.contextmanager
def owner_signals(deadline=None):
    previous = {number: signal.getsignal(number)
                for number in (signal.SIGTERM, signal.SIGINT, signal.SIGALRM)}
    old_delay, old_interval = signal.getitimer(signal.ITIMER_REAL)
    entered = time.monotonic()
    def stop(number, frame):
        raise OwnerStop(number)
    for number in previous:
        signal.signal(number, stop)
    signal.setitimer(signal.ITIMER_REAL, 0)
    if deadline is not None:
        remaining = deadline - entered
        if old_delay:
            remaining = min(remaining, old_delay)
        signal.setitimer(signal.ITIMER_REAL, max(0.000001, remaining))
    elif old_delay:
        signal.setitimer(signal.ITIMER_REAL, old_delay)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        for number, handler in previous.items():
            signal.signal(number, handler)
        if old_delay:
            signal.setitimer(signal.ITIMER_REAL,
                             max(0.000001, old_delay - (time.monotonic() - entered)),
                             old_interval)


def owner_error(stage, error):
    return {'stage': stage, 'type': type(error).__name__, 'message': str(error)}


def process_birth(pid):
    text = Path('/proc', str(pid), 'stat').read_text()
    return text[text.rindex(')') + 2:].split()[19]


def owned_group(process):
    assert os.getpgid(process.pid) == process.pid and os.getsid(process.pid) == process.pid
    return {'pid': process.pid, 'pgid': process.pid, 'starttime': process_birth(process.pid)}


def signal_owned_group(process, identity, number):
    if process.returncode is not None:
        return
    assert process.pid == identity['pid'] and process_birth(process.pid) == identity['starttime']
    assert os.getpgid(process.pid) == identity['pgid'] == process.pid
    assert os.getsid(process.pid) == process.pid
    os.killpg(identity['pgid'], number)


def signal_owned_pid(process, identity, number):
    if process.returncode is not None:
        return
    descriptor = os.pidfd_open(process.pid)
    try:
        assert process_birth(process.pid) == identity['starttime']
        signal.pidfd_send_signal(descriptor, number)
    finally:
        os.close(descriptor)


def bounded_wait(process, deadline, errors):
    """Every retry retains the same finite absolute deadline."""
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return None
        try:
            return process.wait(timeout=remaining)
        except subprocess.TimeoutExpired:
            return None
        except (OwnerStop, KeyboardInterrupt, InterruptedError) as error:
            errors.append(owner_error('reap_interrupted', error))
        except BaseException as error:
            errors.append(owner_error('reap_unknown', error))
            return None


def wait_owned(process, seconds, *, term_seconds=5, kill_seconds=5,
               stop=None, on_stop=None, deadline=None, hard_deadline=None):
    """Wait, TERM, KILL and reap only the freshly created owned session."""
    assert seconds > 0 and term_seconds > 0 and kill_seconds > 0
    errors = []
    row = {'pid': process.pid, 'returncode': None, 'timeout': False,
           'owner_signal': None, 'stop_reason': None, 'errors': errors,
           'term_seconds': term_seconds, 'kill_seconds': kill_seconds,
           'actual_wait_observed': False, 'owned_scope_signals': []}
    try:
        identity = owned_group(process)
        row['owned_process_group'] = identity
    except BaseException as error:
        errors.append(owner_error('owned_group_identity', error))
        identity = None
        stop = stop or error
    end = min(time.monotonic() + seconds, deadline) if deadline is not None else time.monotonic() + seconds
    with owner_signals():
        try:
            if stop is not None:
                raise stop
            remaining = end - time.monotonic()
            if remaining <= 0:
                raise subprocess.TimeoutExpired(process.args, seconds)
            row['returncode'] = process.wait(timeout=remaining)
        except subprocess.TimeoutExpired:
            row.update(timeout=True, stop_reason='deadline')
        except OwnerStop as error:
            row.update(owner_signal=error.number, timeout=error.number == signal.SIGALRM,
                       stop_reason='deadline' if error.number == signal.SIGALRM else 'signal')
        except BaseException as error:
            row['stop_reason'] = 'control_or_retention_failure'
            errors.append(owner_error('wait_or_start_retention', error))
        if row['returncode'] is None:
            for number, grace in ((signal.SIGTERM, term_seconds), (signal.SIGKILL, kill_seconds)):
                until = time.monotonic() + grace
                if hard_deadline is not None:
                    until = min(until, hard_deadline)
                scoped = None
                if on_stop is not None:
                    try:
                        scoped = on_stop(number)
                        row['owned_scope_signals'].append(scoped)
                    except BaseException as error:
                        errors.append(owner_error('owned_scope_signal', error))
                if identity is not None:
                    try:
                        if isinstance(scoped, dict) and 'actual_pidfd_signals' in scoped:
                            if process.pid not in scoped['actual_pidfd_signals']:
                                signal_owned_pid(process, identity, number)
                        else:
                            signal_owned_group(process, identity, number)
                    except ProcessLookupError:
                        pass
                    except BaseException as error:
                        errors.append(owner_error('owned_group_signal', error))
                row['returncode'] = bounded_wait(process, until, errors)
                if row['returncode'] is not None:
                    break
    row['actual_wait_observed'] = row['returncode'] is not None
    row['child_signal'] = -row['returncode'] if row['returncode'] is not None and row['returncode'] < 0 else None
    row['ownership_collection_required'] = row['returncode'] is None or bool(errors)
    return row


def retained_owner_record(path, value):
    path = Path(path)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'w') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    directory = os.open(path.parent, os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    return pinned(path)


def capture_owned(argv, directory, prefix, seconds, *, cwd=None, env=None,
                  stdin=None, term_seconds=5, kill_seconds=5, deadline=None,
                  on_started=None, on_stop=None, wait_name=None, hard_deadline=None):
    """Production owners and Main's harmless stand-ins use this same implementation."""
    directory = Path(directory)
    assert directory.is_dir() and not directory.is_symlink()
    assert prefix and '/' not in prefix and prefix not in ('.', '..')
    errors, streams, raw = [], [], []
    process = None
    stopped = None
    row = {'argv': list(argv), 'pid': None, 'returncode': None,
           'launch_observed': False, 'actual_wait_observed': False,
           'timeout': False, 'owner_signal': None, 'stop_reason': None}
    with owner_signals(hard_deadline):
        try:
            for suffix in ('stdout', 'stderr'):
                fd = os.open(directory / (prefix + '.' + suffix),
                             os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
                streams.append(os.fdopen(fd, 'wb'))
            process = subprocess.Popen(argv, cwd=cwd, env=env, stdin=stdin,
                                       stdout=streams[0], stderr=streams[1], start_new_session=True)
            row.update(pid=process.pid, launch_observed=True)
            if on_started is not None:
                on_started(process)
        except BaseException as error:
            stopped = error
            errors.append(owner_error('open_spawn_or_start_receipt', error))
        finally:
            if process is not None:
                row.update(wait_owned(process, seconds, term_seconds=term_seconds,
                                      kill_seconds=kill_seconds, stop=stopped,
                                      deadline=deadline, on_stop=on_stop,
                                      hard_deadline=hard_deadline))
            for index, stream in enumerate(streams):
                for stage, function in (('flush', stream.flush),
                                        ('fsync', lambda stream=stream: os.fsync(stream.fileno())),
                                        ('close', stream.close)):
                    try:
                        function()
                    except BaseException as error:
                        errors.append(owner_error('raw_' + str(index) + '_' + stage, error))
            for suffix in ('stdout', 'stderr'):
                try:
                    raw.append(pinned(directory / (prefix + '.' + suffix)))
                except BaseException as error:
                    errors.append(owner_error('raw_identity_' + suffix, error))
        errors.extend(row.pop('errors', []))
        row.update(raw_files=raw, retention_errors=errors, phase_acceptance=False,
                   truth_boundary='Actual owned wait only when observed; timeouts, signals, unknown waits and retention failures never substitute return codes or grant proof/phase acceptance.')
        row['retention_success'] = not errors and row['actual_wait_observed']
        try:
            retained_owner_record(directory / (wait_name or (prefix + '-wait.json')), row)
        except BaseException as error:
            errors.append(owner_error('wait_receipt_retention', error))
            row['retention_success'] = False
            try:
                retained_owner_record(directory / (prefix + '-retention-refusal.json'), row)
            except BaseException as refusal_error:
                errors.append(owner_error('refusal_receipt_retention', refusal_error))
    return row


def owner_exit_code(row):
    code = row['returncode']
    if code is None or row.get('timeout') or row.get('owner_signal') or row.get('stop_reason') or row.get('retention_errors') or row.get('errors'):
        return 1
    return code if code >= 0 else 128 - code


def record_owned_scope(receipt, unit, runner):
    membership = Path('/proc/self/cgroup').read_text()
    relative = next(line.split(':', 2)[2] for line in membership.splitlines() if line.startswith('0::'))
    group = Path('/sys/fs/cgroup') / relative.lstrip('/')
    assert group.name == unit and group.is_dir() and not group.is_symlink()
    status = group.stat()
    return retained_owner_record(Path(receipt) / 'owned-scope-child-start.json', {
        'unit': unit, 'runner': pinned(runner), 'receipt': str(Path(receipt).resolve()),
        'pid': os.getpid(), 'starttime': process_birth(os.getpid()),
        'membership': relative, 'cgroup_device': status.st_dev, 'cgroup_inode': status.st_ino})


def signal_recorded_scope(receipt, unit, runner, number):
    receipt = Path(receipt).resolve()
    owner = load(receipt / 'owned-scope-child-start.json')
    assert owner['unit'] == unit and owner['receipt'] == str(receipt) and owner['runner'] == pinned(runner)
    group = Path('/sys/fs/cgroup') / owner['membership'].lstrip('/')
    status = group.stat()
    assert group.name == unit and not group.is_symlink()
    assert (status.st_dev, status.st_ino) == (owner['cgroup_device'], owner['cgroup_inode'])
    signalled = []
    for raw_pid in (group / 'cgroup.procs').read_text().split():
        pid = int(raw_pid)
        try:
            descriptor = os.pidfd_open(pid)
        except ProcessLookupError:
            continue
        try:
            membership = Path('/proc', raw_pid, 'cgroup').read_text()
            actual = next(line.split(':', 2)[2] for line in membership.splitlines() if line.startswith('0::'))
            assert actual == owner['membership'], 'PID moved out of the exact owned scope'
            signal.pidfd_send_signal(descriptor, number)
            signalled.append(pid)
        except ProcessLookupError:
            pass
        finally:
            os.close(descriptor)
    return {'unit': unit, 'signal': number, 'exact_owned_cgroup_inode': status.st_ino,
            'actual_pidfd_signals': signalled}


def action_execution_observation(action):
    """Missing terminal result does not erase independently observed launch/proof."""
    receipt = Path(action['receipt'])
    evidence = {}
    for name in ('inputs-before.json', 'owned-scope-child-start.json',
                 'effective-limits-before.json', 'child-start.json', 'scope-start.json',
                 'child-wait.json', 'scope-wait.json', 'child.stdout', 'child.stderr'):
        path = receipt / name
        if path.is_file() and not path.is_symlink():
            evidence[name] = pinned(path)
    launched = any(name in evidence for name in ('owned-scope-child-start.json', 'effective-limits-before.json', 'child-start.json', 'scope-start.json', 'child-wait.json', 'scope-wait.json'))
    raw_proof = any(name in evidence and evidence[name]['bytes'] > 0 for name in ('child.stdout', 'child.stderr'))
    child_wait = load(receipt / 'child-wait.json') if 'child-wait.json' in evidence else None
    scope_wait = load(receipt / 'scope-wait.json') if 'scope-wait.json' in evidence else None
    launcher_starts = []
    for path in sorted((receipt.parent.parent / 'review/root-live-lane-v1/attempts' / action['mode']).glob('*/launcher-start.json')):
        started = load(path)
        if started.get('argv') == action['launcher_argv']:
            launcher_starts.append(pinned(path))
    observed = launched or raw_proof or bool(launcher_starts)
    return {'state': 'EXECUTED_WITH_UNKNOWN_RESULT' if observed else 'NEVER_LAUNCHED',
            'actual_launch_or_child_start_observed': launched,
            'actual_launcher_start_observed': bool(launcher_starts),
            'actual_raw_proof_present': raw_proof, 'launcher_start_evidence': launcher_starts,
            'evidence': evidence, 'actual_child_wait': child_wait, 'actual_scope_wait': scope_wait,
            'no_unknown_wait_reconstructed': True}


def strict_terminal_classification(result, *, child_wait=None, scope_wait=None,
                                   launcher_wait=None, outer_wait=None, refusals=(),
                                   execution_observed=False):
    """Pure consumer of actual receipts; refusal never rewrites a raw wait."""
    failures, unknown = [], []

    def expected(row, key, value, label):
        if key not in row or row[key] is None and value is not None:
            unknown.append(label + '.' + key)
        elif type(row[key]) is not type(value) or row[key] != value:
            failures.append(label + '.' + key)

    def owner(row, label, captured):
        if not isinstance(row, dict):
            unknown.append(label)
            return
        for key, value in (
            ('returncode', 0), ('actual_wait_observed', True), ('timeout', False),
            ('owner_signal', None), ('child_signal', None), ('stop_reason', None),
            ('ownership_collection_required', False), ('owned_scope_signals', []),
        ):
            expected(row, key, value, label)
        if captured:
            for key, value in (
                ('launch_observed', True), ('retention_success', True),
                ('retention_errors', []), ('phase_acceptance', False),
            ):
                expected(row, key, value, label)
        else:
            expected(row, 'errors', [], label)
        for key in ('errors', 'retention_errors'):
            if key in row and row[key] != []:
                failures.append(label + '.' + key)
        for key in ('root_collection_required', 'retention_refused'):
            if key in row:
                expected(row, key, False, label)
        if 'status' in row or 'disposition' in row:
            # These controls have no success-status alias: an extra status is
            # not evidence that an original refusal or unknown became normal.
            unknown.append(label + '.unexpected_status_or_disposition')

    if refusals:
        failures.append('retained_refusal_receipts')
    if isinstance(result, dict):
        expected(result, 'scope_wait', 0, 'result')
        expected(result, 'inputs_unchanged', True, 'result')
        if result.get('post_run_readback_error') is not None:
            failures.append('result.post_run_readback_error')
        owner(result.get('child_wait'), 'result.child_wait', True)
        owner(result.get('scope_owner_control'), 'result.scope_owner_control', True)
        for label, row, original in (
            ('child_wait_receipt', child_wait, result.get('child_wait')),
            ('scope_wait_receipt', scope_wait, result.get('scope_owner_control')),
        ):
            owner(row, label, True)
            if isinstance(row, dict) and row != original:
                failures.append(label + '.does_not_match_result')
        execution_observed = True
    else:
        unknown.append('result')
        owner(child_wait, 'child_wait_receipt', True)
        owner(scope_wait, 'scope_wait_receipt', True)
    owner(launcher_wait, 'launcher_wait_receipt', True)
    if isinstance(outer_wait, dict):
        expected(outer_wait, 'actual_handshake_Popen_wait_returncode', 0, 'outer_wait')
        expected(outer_wait, 'inputs_unchanged', True, 'outer_wait')
        expected(outer_wait, 'retention_success', True, 'outer_wait')
        expected(outer_wait, 'retention_errors', [], 'outer_wait')
        owner(outer_wait.get('owner_control'), 'outer_wait.owner_control', False)
        if isinstance(outer_wait.get('owner_control'), dict) and (
                outer_wait['owner_control'].get('returncode') !=
                outer_wait.get('actual_handshake_Popen_wait_returncode')):
            failures.append('outer_wait.actual_wait_mismatch')
    else:
        unknown.append('outer_wait_receipt')
    execution_observed = execution_observed or any(
        isinstance(row, dict) and (
            row.get('launch_observed') is True or row.get('actual_wait_observed') is True)
        for row in (child_wait, scope_wait, launcher_wait))
    passed = not failures and not unknown
    state = ('NORMAL_TERMINAL_ACTUAL_WAIT_ZERO' if passed else
             'FAILED_TERMINAL' if failures else
             'EXECUTED_WITH_UNKNOWN_RESULT' if execution_observed else
             'NEVER_LAUNCHED')
    return {'state': state, 'all_required_actual_pass': passed,
            'failures': failures, 'unknown': unknown,
            'actual_waits_rewritten': False, 'phase_acceptance': False,
            'proof_acceptance': False}


MAIN_DEADLINE_ENV = 'WORLDLINE_FORMAL_MAIN_DEADLINE_MONOTONIC'


def inherited_main_deadline():
    import math
    value = float(os.environ[MAIN_DEADLINE_ENV])
    current = time.monotonic()
    assert math.isfinite(value) and current < value <= current + 1000
    return value


def retain_terminal_or_refusal(path, value):
    """Return retention errors without losing already observed actual waits."""
    try:
        retained_owner_record(path, value)
        return []
    except BaseException as error:
        errors = [owner_error('terminal_retention', error)]
        try:
            retained_owner_record(Path(path).with_name(Path(path).name + '.retention-refusal.json'),
                                  {'actual_terminal': value, 'retention_errors': errors,
                                   'retention_success': False, 'phase_acceptance': False})
        except BaseException as refusal_error:
            errors.append(owner_error('terminal_refusal_retention', refusal_error))
        return errors


DEADLINE_MACHINERY = {'run_checks.py': {'preimage': {'path': '/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/records/codex-resumption-20261007/formal-successor-v22-preparation/run_checks.py', 'sha256': 'fd08caf7765e41c7590270f1d18aaf492188d0fd2a1de37e658b2a8a240edacb', 'bytes': 25416, 'mode': 420}, 'template': {'path': '/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/records/codex-resumption-20261007/formal-successor-v24-preparation/deadline-machinery-templates/run_checks.py', 'sha256': 'fb346eb7c4da940fd8765b9fe14cb98e1a6abb03bc9623bd2621b34a3c3f42a4', 'bytes': 27399, 'mode': 420}}, 'outer_capture.py': {'preimage': {'path': '/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/records/codex-resumption-20261007/formal-successor-v22-preparation/outer_capture.py', 'sha256': 'f9bc56e4aa6cdca237aec7fb83cc79ed349eb6eaad853ab330c5b9512ac6487d', 'bytes': 5586, 'mode': 420}, 'template': {'path': '/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/records/codex-resumption-20261007/formal-successor-v24-preparation/deadline-machinery-templates/outer_capture.py', 'sha256': '2def33f0caef731d1de53328f2a6c9cad87b71f19ae11a07042130aec793d11c', 'bytes': 6174, 'mode': 420}}, 'review/root-live-lane-v1/handshake.py': {'preimage': {'path': '/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/records/codex-resumption-20261007/formal-successor-v22-preparation/review/root-live-lane-v1/handshake.py', 'sha256': '05e1f4ad0ef8b391ca67e64bcf986a3b188c1f44b744d3e7beca698b066bfd08', 'bytes': 14083, 'mode': 420}, 'template': {'path': '/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/records/codex-resumption-20261007/formal-successor-v24-preparation/deadline-machinery-templates/review/root-live-lane-v1/handshake.py', 'sha256': 'a53bb432bd07848561a69fe937fa94bc5f2cd72bdc5ca5516d5dc2ae611ffa35', 'bytes': 14721, 'mode': 420}}, 'review/root-terminal-v1/collect_terminal.py': {'preimage': {'path': '/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/records/codex-resumption-20261007/formal-successor-v22-preparation/review/root-terminal-v1/collect_terminal.py', 'sha256': '521cfd91a87e8cfc2874db3cad033ed2716b2d4d2b71b01c6c8bcdeaa106b85c', 'bytes': 10385, 'mode': 420}, 'template': {'path': '/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/records/codex-resumption-20261007/formal-successor-v24-preparation/deadline-machinery-templates/review/root-terminal-v1/collect_terminal.py', 'sha256': '593327de3d962e56f4cbc6351b8339e43b1e2bd93a9bd880c028e9b363b1ba0f', 'bytes': 13266, 'mode': 420}}}
