"""Exact compiler-output-only transfer for a future reviewed fresh formal frame.

Import has no effects. Authentication never imports target code, supplies proof
credit, or makes the compiler accept an output. Only the original checked
preparer may call materialize after the independent reviews and fresh guards.
"""
from pathlib import Path
import contextlib
import hashlib
import os
import shutil
import stat
import successor_support as support

ORIGIN = support.R / 'formal-successor-v25-preparation'
PARTITIONS = ('source/obj', 'private-sparklib/lib/gnat/sparklib_obj',
              'private-sparklib/lib/gnat/sparklib_lib')


def compiler_member(partition, name):
    path = Path(name)
    if partition == 'source/obj':
        return (path.parent.as_posix() == 'core/gnatprove/data_representation'
                and (path.suffix in ('.ali', '.cswi', '.s')
                     or name.endswith(('.adb.json', '.ads.json'))))
    if path.parent.as_posix() != '.':
        return False
    return path.suffix in (('.ali', '.o', '.lexch') if partition.endswith('_obj')
                           else ('.ali', '.a'))


def file_identity(value):
    return (value.st_dev, value.st_ino, value.st_mode, value.st_size,
            value.st_mtime_ns, value.st_ctime_ns)


@contextlib.contextmanager
def origin_directories(selection):
    """Hold no-follow origin directory descriptors through full reads and copying."""
    assert selection['origin'] == str(ORIGIN) and ORIGIN.is_absolute()
    assert set(selection['partitions']) == set(PARTITIONS)
    selected, needed = {}, {ORIGIN, *ORIGIN.parents}
    for partition, entries in selection['partitions'].items():
        support.validate_entries(entries)
        for name, row in entries.items():
            path = ORIGIN / partition / name
            assert path.is_relative_to(ORIGIN) and '..' not in path.parts
            if row['kind'] == 'directory':
                selected[path] = row['mode']
                needed.add(path)
            else:
                assert row['kind'] == 'file' and compiler_member(partition, name), (partition, name)
                needed.add(path.parent)
            needed.update(path.parents)
    descriptors, observations = {}, {}
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    with contextlib.ExitStack() as held:
        for path in sorted(needed, key=lambda item: (len(item.parts), str(item))):
            before = path.lstat()
            assert stat.S_ISDIR(before.st_mode) and not path.is_symlink(), ('Origin component is not a no-follow directory', str(path))
            if path == Path(path.anchor):
                descriptor = os.open(path, flags)
            else:
                descriptor = os.open(path.name, flags, dir_fd=descriptors[path.parent])
            held.callback(os.close, descriptor)
            opened = os.fstat(descriptor)
            identity = (opened.st_dev, opened.st_ino, opened.st_mode)
            assert identity == (before.st_dev, before.st_ino, before.st_mode), ('Origin component changed during open', str(path))
            assert path.resolve(strict=True) == path
            assert path.is_relative_to(ORIGIN) or path in ORIGIN.parents
            if path in selected:
                assert stat.S_IMODE(opened.st_mode) == selected[path], ('Retained selected origin directory mode changed', str(path))
            descriptors[path] = descriptor
            observations[str(path)] = {'kind': 'directory', 'canonical_path': str(path),
                                      'device': opened.st_dev, 'inode': opened.st_ino,
                                      'mode': stat.S_IMODE(opened.st_mode),
                                      'selected_retained_mode': selected.get(path)}
        yield descriptors, observations
        for path, descriptor in descriptors.items():
            after, opened = path.lstat(), os.fstat(descriptor)
            original = observations[str(path)]
            expected = (original['device'], original['inode'], original['mode'])
            assert (after.st_dev, after.st_ino, stat.S_IMODE(after.st_mode)) == expected
            assert stat.S_ISDIR(after.st_mode) and path.resolve(strict=True) == path
            assert (opened.st_dev, opened.st_ino, stat.S_IMODE(opened.st_mode)) == expected


@contextlib.contextmanager
def origin_file(path, row, directories):
    """Hash and copy the same regular inode through its authenticated parent FD."""
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC
    descriptor = os.open(path.name, flags, dir_fd=directories[path.parent])
    with os.fdopen(descriptor, 'rb') as stream:
        before = os.fstat(stream.fileno())
        assert stat.S_ISREG(before.st_mode) and row['kind'] == 'file', str(path)
        assert before.st_size == row['bytes'] and stat.S_IMODE(before.st_mode) == row['mode'], str(path)
        assert path.resolve(strict=True) == path and path.is_relative_to(ORIGIN)
        assert hashlib.file_digest(stream, 'sha256').hexdigest() == row['sha256'], str(path)
        assert file_identity(os.fstat(stream.fileno())) == file_identity(before), ('Origin file changed during hash', str(path))
        assert file_identity(os.stat(path.name, dir_fd=directories[path.parent], follow_symlinks=False)) == file_identity(before)
        stream.seek(0)
        yield stream
        assert file_identity(os.fstat(stream.fileno())) == file_identity(before), ('Origin file changed during copy', str(path))
        assert file_identity(os.stat(path.name, dir_fd=directories[path.parent], follow_symlinks=False)) == file_identity(before)


def copy_partition(partition, destination, entries, directories):
    """Use only authenticated no-follow source FDs and new destination files."""
    assert not destination.exists() and not destination.is_symlink(), str(destination)
    destination.mkdir()
    modes = []
    for name, row in sorted(entries.items(), key=lambda item: (len(Path(item[0]).parts), item[0])):
        path = destination / name
        if row['kind'] == 'directory':
            if name != '.':
                path.mkdir()
            modes.append((path, row['mode']))
        else:
            assert row['kind'] == 'file' and compiler_member(partition, name), (partition, name)
            with origin_file(ORIGIN / partition / name, row, directories) as source:
                with path.open('xb') as output:
                    shutil.copyfileobj(source, output)
                shutil.copystat(source.fileno(), path)
    for path, mode in reversed(modes):
        path.chmod(mode)
    assert support.snapshot(destination) == entries, 'Copied complete compiler inventory differs'


def authenticate(root, binding, source_entries, dependency):
    """Refuse changed inputs, ambiguous origins, proof outputs or implicit selection."""
    root = Path(root)
    assert __debug__ and root == support.CANDIDATE
    selection_row = binding['pins']['compiler_output_seed_selection']
    assert support.matched(selection_row) == root / 'compiler-output-seed-selection.json'
    support.matched(binding['pins']['compiler_seed_module'])
    selection = support.load(selection_row['path'])
    assert selection['schema'] == 'worldline-exact-owned-compiler-output-seed-selection-v1'
    assert selection['author'] == support.AUTHOR and selection['candidate'] == str(root)
    assert selection['origin'] == str(ORIGIN) and set(selection['partitions']) == set(PARTITIONS)
    for key in ('target_execution', 'proof_acceptance', 'runtime_acceptance',
                'phase_acceptance', 'proof_reports_transferred', 'proof_sessions_transferred',
                'coverage_credit_transferred', 'compiler_acceptance_established',
                'cross_root_efficacy_established', 'forced_reuse', 'shared_install_writes'):
        assert selection[key] is False, key
    generation = selection['generation']
    for row in generation['pins'].values():
        path = support.matched(row)
        assert path.is_relative_to(ORIGIN) and path.resolve(strict=True).is_relative_to(ORIGIN)
    pins = generation['pins']
    terminal = support.load(pins['terminal']['path'])
    assert terminal['retained_complete_artifacts'] == pins['retained_artifacts']
    assert terminal['source_exact_keyset_bytes_modes_match'] is True
    assert terminal['status'] == 'BATCH_TERMINAL_WITH_RETAINED_GAPS_NO_ACCEPTANCE'
    retained = support.load(pins['retained_artifacts']['path'])
    generated = support.load(pins['generated_inventory']['path'])
    freeze = support.load(pins['author_freeze']['path'])
    for name, row in pins.items():
        relative = Path(row['path']).relative_to(ORIGIN).as_posix()
        if relative in retained:
            assert retained[relative] == row, name
        elif relative in freeze['files']:
            assert {'path': row['path'], **freeze['files'][relative]} == row, name
        else:
            assert name in ('terminal', 'retained_artifacts', 'generated_inventory',
                            'private_readback', 'author_freeze'), name
    old_entries = support.load(pins['selected_source_entries']['path'])
    assert source_entries == old_entries, 'Compiler seeds require the same complete physical F67 inputs'
    assert generation['selected_source_artifacts'] == support.load(pins['source_bindings']['path'])['reviewed_source_artifacts']
    current_source_review = support.load(support.matched(binding['pins']['source_review']))
    assert generation['current_destination_source_artifacts'] == current_source_review['artifacts']
    for pair in generation['current_source_opinions'].values():
        support.matched(pair['review'])
        support.matched(pair['model'])
    readback = support.load(pins['private_readback']['path'])
    assert readback['matches'] is True and readback['actual']['complete_source_entries'] == old_entries
    old_dependency = support.load(pins['dependency_inventory']['path'])
    assert readback['actual']['dependency']['private_immutable_entries'] == old_dependency['entries']
    assert readback['actual']['dependency']['shared_outputs_unchanged'] is True
    expected_dependency = support.rehome(old_dependency, old=ORIGIN, new=root)
    expected_dependency['installed_initial_output_inventory'] = expected_dependency['initial_output_inventory']
    expected_dependency['initial_output_inventory'] = {
        name: selection['partitions'].get('private-sparklib/' + name)
        for name in support.DEPENDENCY_OUTPUTS}
    expected_dependency['compiler_seed_selection'] = selection_row
    expected_dependency['initial_output_copy_policy'] = 'Only explicit authenticated C25 compiler outputs; no installed or retained proof/session/report output transfer'
    assert expected_dependency == dependency, 'Private compiler source/project/shared seed generation drift'
    old_binding = support.load(pins['source_bindings']['path'])
    assert set(binding['closure_documents']) == set(support.CLOSURE_FILES)
    old_documents = {}
    for name in support.CLOSURE_FILES:
        assert pins['closure:' + name] == old_binding['closure_documents'][name]
        old_documents[name] = support.load(pins['closure:' + name]['path'])
        current = support.load(support.matched(binding['closure_documents'][name]))
        assert support.rehome(old_documents[name], old=ORIGIN, new=root) == current, ('Compiler generation input closure changed', name)
    inputs = support.load(pins['inputs_before']['path'])
    start = support.load(pins['child_start']['path'])
    wait = support.load(pins['child_wait']['path'])
    scope_owner = support.load(pins['scope_owner']['path'])
    assert inputs['child_argv'] == start['argv'] == wait['argv'] == support.COMMAND
    assert inputs['formal_diagnostic_only'] is True and inputs['cwd'] == str(ORIGIN / 'source')
    assert inputs['runner_sha256'] == scope_owner['runner']['sha256']
    assert scope_owner['runner'] == pins['runner']
    assert scope_owner['receipt'] == str(ORIGIN / 'evidence/full-strict-formal-diagnostic-v1')
    assert start['actual_prover_launch_observed'] is True and start['pid'] == wait['pid']
    assert wait['actual_wait_observed'] is True and type(wait['returncode']) is int
    assert wait['phase_acceptance'] is False
    assert support.load(pins['private_before']['path'])['complete_source_entries'] == old_entries
    assert support.load(pins['tools_before']['path']) == old_documents['action-baseline.json']['tool_inventory']
    assert support.load(pins['native_before']['path']) == old_documents['native-input-baseline.json']
    assert support.load(pins['runtime_before']['path']) == support.rehome(old_documents['runtime-closure.json'], new=ORIGIN)['inventory']
    assert support.load(pins['proof_data_before']['path']) == old_documents['proof-data-closure.json']['inventory']
    assert support.load(pins['proof_elf_before']['path']) == old_documents['proof-elf-baseline.json']
    assert support.load(pins['vendors_before']['path']) == old_documents['action-baseline.json']['vendor_inventory']
    with origin_directories(selection) as (directories, _):
        for partition, entries in selection['partitions'].items():
            assert entries['.'] == generated[partition]['.'], partition
            for name, row in entries.items():
                assert row == generated[partition][name], (partition, name)
                if row['kind'] == 'directory':
                    assert any(other != name and (name == '.' or other.startswith(name + '/'))
                               and item['kind'] == 'file' for other, item in entries.items()), name
                    continue
                assert row['kind'] == 'file' and compiler_member(partition, name), (partition, name)
                relative = partition + '/' + name
                origin_row = {'path': str(ORIGIN / relative), **{k: v for k, v in row.items() if k != 'kind'}}
                assert retained[relative] == origin_row
                assert selection['files'][relative] == {'kind': 'file', 'origin': origin_row,
                                                        'destination': str(root / relative)}
                with origin_file(ORIGIN / relative, row, directories):
                    pass
    selected_files = {partition + '/' + name for partition, entries in selection['partitions'].items()
                      for name, row in entries.items() if row['kind'] == 'file'}
    assert set(selection['files']) == selected_files, 'Seed selection is explicit and complete, not a glob at copy time'
    return selection


def check_pristine_before_compiler(root):
    """Fresh full output keyset/hash/mode readback immediately before the first use."""
    root = Path(root)
    assert root == support.CANDIDATE
    binding = support.load(root / 'source-bindings.json')
    selection_row = binding['pins']['compiler_output_seed_selection']
    selection = support.load(support.matched(selection_row))
    copied = support.load(root / 'compiler-output-seed-copy-receipt.json')
    assert copied['candidate'] == str(root) and copied['selection'] == selection_row
    assert {row['partition']: row['entries'] for row in copied['copied_output_partitions']} == selection['partitions']
    expected = {name: None for name in
                tuple('source/' + item for item in support.SOURCE_OUTPUTS)
                + tuple('private-sparklib/' + item for item in support.DEPENDENCY_OUTPUTS)}
    expected.update(selection['partitions'])
    observed = support.generated_outputs(root)
    assert observed == expected, 'Compiler seed keyset/kind/hash/size/mode changed before owned use'
    return {'selection': selection_row, 'actual_owned_output_inventory': observed,
            'compiler_acceptance_established': False, 'cross_root_efficacy_established': False,
            'proof_acceptance': False, 'phase_acceptance': False}


def materialize(root, selection):
    """Copy only into absent owned output roots; preserve bytes/modes/mtime unchanged."""
    root = Path(root)
    assert root == support.CANDIDATE and selection['candidate'] == str(root)
    destinations = []
    with origin_directories(selection) as (directories, origin_observations):
        for partition in PARTITIONS:
            destination = root / partition
            assert not destination.exists() and not destination.is_symlink(), ('Never overwrite compiler output', partition)
            parent = destination.parent
            while parent != root:
                assert parent.is_dir() and not parent.is_symlink(), str(parent)
                parent = parent.parent
        for partition in PARTITIONS:
            destination = root / partition
            copy_partition(partition, destination, selection['partitions'][partition], directories)
            destinations.append({'partition': partition, 'entries': support.snapshot(destination)})
    return {'schema': 'worldline-owned-compiler-output-seed-copy-receipt-v1',
            'candidate': str(root), 'selection': support.pinned(root / 'compiler-output-seed-selection.json'),
            'copied_output_partitions': destinations, 'immutable_source_replaced': False,
            'actual_origin_directory_chain_readback': origin_observations,
            'origin_reads_and_copy_use_same_authenticated_no_follow_descriptors': True,
            'default_compiler_acceptance_and_rebuild_unchanged': True,
            'mtime_or_embedded_paths_rewritten': False, 'proof_reports_transferred': False,
            'proof_sessions_transferred': False, 'compiler_acceptance_established': False,
            'cross_root_efficacy_established': False, 'target_execution': False,
            'proof_acceptance': False, 'runtime_acceptance': False, 'phase_acceptance': False}
