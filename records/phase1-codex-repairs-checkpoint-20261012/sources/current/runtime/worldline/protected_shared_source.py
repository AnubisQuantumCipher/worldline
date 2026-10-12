"""Explicit owner-selected immutable source layout, never an authority verdict.

The complete source tree remains distinct from every mutable fixture root.
An already installed early source lease must authenticate this module, each
file, every directory, the external inventory and the actual import roots.
The outer interpreter/ELF/prelaunch custody and native/proof decisions remain
independent requirements. Nothing here creates, installs or rebaselines state.
"""
import sys
_approved = sys.modules.get('_worldline_approved_source_loader')
if _approved is None:
    raise RuntimeError('SHARED_SOURCE_EARLY_APPROVED_LEASE_REQUIRED')
_lease = _approved.current()
if type(_lease) is not _approved.ApprovedSourceLease:
    raise RuntimeError('SHARED_SOURCE_ACTUAL_EARLY_LEASE_REQUIRED')
_lease.check()
import hashlib
import json
import os
from pathlib import Path
import stat


class SourceBindingRefusal(RuntimeError):
    pass


def require(value, reason):
    if not value:
        raise SourceBindingRefusal(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode('ascii')


def exact(raw):
    def pairs(items):
        value = {}
        for key, item in items:
            require(key not in value, 'SHARED_SOURCE_DUPLICATE_JSON_KEY')
            value[key] = item
        return value
    value = json.loads(raw, object_pairs_hook=pairs,
        parse_constant=lambda value: (_ for _ in ()).throw(
            SourceBindingRefusal('SHARED_SOURCE_NONFINITE_JSON')))
    require(raw in (canonical(value), canonical(value) + b'\n'),
            'SHARED_SOURCE_NONCANONICAL_DATA')
    return value


def path(value):
    require(type(value) is str and value.startswith('/') and '\x00' not in value
            and value == os.path.normpath(value), 'SHARED_SOURCE_CANONICAL_PATH_REQUIRED')
    return Path(value)


def protected(value, *, directory=False, private=False):
    value = path(str(value))
    for item in (*reversed(value.parents), value):
        info = item.lstat()
        require(info.st_uid == 0 and not stat.S_ISLNK(info.st_mode)
                and not stat.S_IMODE(info.st_mode) & 0o022,
                'SHARED_SOURCE_ROOT_CUSTODY_REQUIRED')
        if item != value or directory:
            require(stat.S_ISDIR(info.st_mode), 'SHARED_SOURCE_DIRECTORY_REQUIRED')
    info = value.lstat()
    if not directory:
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1,
                'SHARED_SOURCE_UNALIASED_REGULAR_FILE_REQUIRED')
    if private:
        require(not stat.S_IMODE(info.st_mode) & 0o077,
                'SHARED_SOURCE_PRIVATE_INPUT_REQUIRED')
    return info


def selected(value, roles, *, private=False):
    value = path(str(value))
    before = protected(value, private=private)
    raw = _lease.file(str(value), roles)
    after = protected(value, private=private)
    require((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns,
             before.st_ctime_ns, before.st_mode, before.st_uid, before.st_gid) ==
            (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns,
             after.st_ctime_ns, after.st_mode, after.st_uid, after.st_gid)
            and len(raw) == after.st_size, 'SHARED_SOURCE_SELECTED_INPUT_CHANGED')
    return raw, after


class SharedSourceBinding:
    """Complete installed bytes and directories under a genuine early lease."""
    def __init__(self, binding, *, mutable_root):
        require(os.geteuid() == 0 and _approved.current() is _lease,
                'SHARED_SOURCE_REAL_ROOT_AND_RETAINED_LEASE_REQUIRED')
        _lease.check()
        require(type(binding) is dict and set(binding) ==
                {'schema', 'root', 'inventory', 'library', 'locations'}
                and binding['schema'] == 'worldline.protected-full-ledger-shared-source-binding-v1',
                'SHARED_SOURCE_BINDING_SCHEMA')
        self.binding = exact(canonical(binding))
        self.root = path(binding['root'])
        mutable = path(str(mutable_root))
        require(not self.root.is_relative_to(mutable) and not mutable.is_relative_to(self.root),
                'SHARED_SOURCE_MUTABLE_ROOT_OVERLAP')
        self.inventory_path = path(binding['inventory'])
        require(not self.inventory_path.is_relative_to(self.root),
                'SHARED_SOURCE_EXTERNAL_COMPLETE_INVENTORY_REQUIRED')
        self.library = path(binding['library'])
        require(self.library == self.root / 'libworldline_core.so',
                'SHARED_SOURCE_EXACT_ORIGINAL_NATIVE_LOCATION_REQUIRED')
        require(type(binding['locations']) is dict and binding['locations'],
                'SHARED_SOURCE_COMPLETE_LOCATION_CORRESPONDENCE_REQUIRED')
        self.locations = {}
        for name, value in binding['locations'].items():
            require(type(name) is str and name and Path(name).as_posix() == name
                    and not Path(name).is_absolute() and not set(Path(name).parts) & {'.', '..'},
                    'SHARED_SOURCE_LOGICAL_SOURCE_NAME_INVALID')
            source = path(value)
            expected = self.root / ('protected-resource/run_service.py' if name == 'run_service.py' else name)
            require(source == expected, 'SHARED_SOURCE_EXACT_SOURCE_LOCATION_REQUIRED')
            self.locations[name] = source
        require({'run_service.py', 'runtime/worldline/resource_run_ledger.py'} <= set(self.locations),
                'SHARED_SOURCE_ORIGINAL_LEDGER_CALLERS_REQUIRED')
        require(Path(__file__) == self.root / 'runtime/worldline/protected_shared_source.py',
                'SHARED_SOURCE_ACTUAL_BINDING_MODULE_REQUIRED')
        self.inventory_raw, _ = selected(self.inventory_path, ('DATA',), private=True)
        self.inventory = exact(self.inventory_raw)
        require(type(self.inventory) is dict and self.inventory,
                'SHARED_SOURCE_COMPLETE_INVENTORY_REQUIRED')
        for name, item in self.inventory.items():
            require(type(name) is str and name and not Path(name).is_absolute()
                    and Path(name).as_posix() == name and not set(Path(name).parts) & {'.', '..'}
                    and type(item) is dict and set(item) == {'mode', 'sha256'}
                    and type(item['mode']) is str and type(item['sha256']) is str,
                    'SHARED_SOURCE_INVENTORY_ROW_INVALID')
        self.last_observation = self.check()

    def check(self):
        require(_approved.current() is _lease and sys.modules.get('_worldline_approved_source_loader') is _approved,
                'SHARED_SOURCE_RETAINED_EARLY_LEASE_CHANGED')
        _lease.check()
        raw, _ = selected(self.inventory_path, ('DATA',), private=True)
        require(raw == self.inventory_raw, 'SHARED_SOURCE_IMMUTABLE_INVENTORY_CHANGED')
        protected(self.root, directory=True, private=True)
        _lease.directory_or_absent(str(self.root))
        files, directories = {}, {}
        for item in (self.root, *sorted(self.root.rglob('*'))):
            info = item.lstat()
            if stat.S_ISDIR(info.st_mode):
                protected(item, directory=True)
                _lease.directory_or_absent(str(item))
                directories[str(item)] = stat.S_IMODE(info.st_mode)
                continue
            require(stat.S_ISREG(info.st_mode) and item.suffix != '.pyc'
                    and '__pycache__' not in item.parts, 'SHARED_SOURCE_UNDECLARED_FILE_KIND')
            role = _lease.files.get(str(item), (None,))[0]
            require(role in ('SOURCE', 'ENTRY', 'HELPER', 'DATA', 'EXTENSION', 'EXECUTABLE'),
                    'SHARED_SOURCE_FULL_TREE_NOT_EARLY_SELECTED')
            body, held = selected(item, (role,), private=True)
            files[item.relative_to(self.root).as_posix()] = {
                'mode': oct(stat.S_IMODE(held.st_mode)), 'sha256': hashlib.sha256(body).hexdigest()}
        expected_directories = {name:mode for name,mode in _lease.directories.items()
                                if path(name).is_relative_to(self.root)}
        require(directories == expected_directories and files == self.inventory,
                'SHARED_SOURCE_COMPLETE_IMMUTABLE_KEYSET_CHANGED')
        require(Path(__file__).relative_to(self.root).as_posix() in files
                and self.library.relative_to(self.root).as_posix() in files
                and all(value.relative_to(self.root).as_posix() in files for value in self.locations.values()),
                'SHARED_SOURCE_ACTUAL_DEPENDENCY_MISSING')
        _lease.check()
        self.last_observation = {'schema': 'worldline.protected-shared-source-readback-v1',
            'root': str(self.root), 'inventory_path': str(self.inventory_path),
            'inventory_raw_hex': self.inventory_raw.hex(), 'files': files,
            'directories': directories, 'early_source': _lease.snapshot(),
            'native_or_startup_authorization': None}
        return self.last_observation

    def require_roster(self, sources):
        require(type(sources) is dict and set(sources) == set(self.locations),
                'SHARED_SOURCE_EXACT_LEDGER_SOURCE_ROSTER_REQUIRED')
        self.check()
        for name, expected in sources.items():
            source = self.locations[name]
            require(type(expected) is str and
                    self.inventory[source.relative_to(self.root).as_posix()]['sha256'] == expected,
                    'SHARED_SOURCE_LEDGER_SOURCE_DIGEST_CHANGED')
            selected(source, ('SOURCE', 'ENTRY'))


def from_path(binding_path, *, mutable_root):
    raw, _ = selected(path(binding_path), ('DATA',), private=True)
    return SharedSourceBinding(exact(raw), mutable_root=mutable_root)


def startup_import_roots(runtime, binding):
    require(path(runtime['worldline_source']) == binding.root
            and path(runtime['native_library']) == binding.library,
            'SHARED_SOURCE_STARTUP_SOURCE_NATIVE_CORRESPONDENCE_REQUIRED')
    gate = path(runtime['gate_source'])
    principal = path(runtime['principal_source'])
    require(principal == binding.root / 'protected-lab/recovery_principal.py',
            'SHARED_SOURCE_STARTUP_PRINCIPAL_LOCATION_REQUIRED')
    selected(gate, ('SOURCE',))
    selected(principal, ('SOURCE',))
    roots = (binding.root / 'runtime', binding.root / 'protected-resource',
             binding.root / 'protected-lab', gate.parent,
             gate.parent / 'universe_source', gate.parent / 'evidence_source')
    for directory in roots:
        protected(directory, directory=True)
        _lease.directory_or_absent(str(directory))
    return tuple(str(directory) for directory in roots)


def worker_control_inputs(spec):
    """Select DATA only; no custody/admission/worker-owner result is returned."""
    runtime = spec['runtime']
    if 'worker_control_inputs' not in runtime:
        return None
    chosen = runtime['worker_control_inputs']
    require(type(chosen) is dict and set(chosen) in ({'observer'}, {'observer', 'duplex'}),
            'SHARED_SOURCE_WORKER_CONTROL_INPUT_SCHEMA')
    root = path(spec['paths']['authority_root'])
    result = {}
    for name, value in chosen.items():
        source = path(value)
        require(source.is_relative_to(root), 'SHARED_SOURCE_CONTROL_DATA_OUTSIDE_FIXTURE_ROOT')
        selected(source, ('DATA',), private=True)
        result[name] = source
    require(len(set(result.values())) == len(result), 'SHARED_SOURCE_CONTROL_DATA_ALIAS')
    return result
