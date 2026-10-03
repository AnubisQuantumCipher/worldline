"""Byte-bound examiner imports and identified stdlib generator routes.

The daemon supplies the inventory. These Python loaders are an implementation
dependency, not a tamper-proof registry or a confinement verdict. In particular,
cached modules and native extension execution retain their separate boundaries.
"""
from __future__ import annotations

import __future__
import ast
import builtins
import collections
import dataclasses
import hashlib
import importlib.machinery
import importlib.util
from importlib._bootstrap import _load_module_shim as _FROZEN_LOAD_SHIM
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import sysconfig
import types
import uuid


SCHEMA = 'worldline-examiner-loader-v1'
POLICY_MOUNT = '/run/worldline-loader-policy.json'
HELPER_MOUNT = '/run/worldline-examiner-loader.py'
VERIFIER_MOUNT = '/run/worldline-verifiers'
NATIVE_MOUNT = '/run/worldline-examiner-guard.so'
_DIR = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
_HEX = re.compile(r'[0-9a-f]{64}\Z')
_COMPILE, _EXEC, _EVAL = compile, exec, eval
_ABSENT = object()


class LoaderRefusal(ImportError):
    pass


def _require(condition, message):
    if not condition:
        raise LoaderRefusal(message)


def _path(value):
    return (type(value) is str and value.startswith('/') and '\0' not in value
            and str(PurePosixPath(value)) == value
            and '..' not in PurePosixPath(value).parts)


def _inside(path, root):
    return path == root or path.startswith(root.rstrip('/') + '/')


def _identity(info):
    # uid/gid are translated inside the held role user namespace.
    return {'device': info.st_dev, 'inode': info.st_ino, 'mode': info.st_mode}


def _error(error):
    return {'type': type(error).__module__ + '.' + type(error).__qualname__,
            'message': str(error), 'errno': getattr(error, 'errno', None)}


def _unique(pairs):
    value = {}
    for key, item in pairs:
        _require(key not in value, 'duplicate loader policy field')
        value[key] = item
    return value


def _nonfinite(value):
    raise LoaderRefusal('non-finite loader policy value: ' + value)


def _close(descriptor, observation, primary=None):
    try:
        os.close(descriptor)
        observation['closeReturned'] = True
    except BaseException as error:
        observation['closeException'] = _error(error)
        if primary is None:
            raise
        primary.add_note('loader directory close also failed: ' + str(error))


def _open_directory(path):
    _require(_path(str(path)), 'directory path is not absolute and normalized')
    handles, result, primary = [], None, None
    try:
        descriptor = os.open('/', _DIR)
        handles.append(descriptor)
        for component in Path(path).parts[1:]:
            descriptor = os.open(component, _DIR, dir_fd=descriptor)
            handles.append(descriptor)
        result = handles.pop()
    except BaseException as error:
        primary = error
        raise
    finally:
        cleanup = None
        while handles:
            descriptor = handles.pop()
            try:
                os.close(descriptor)
            except BaseException as error:
                if primary is not None:
                    primary.add_note('loader ancestor cleanup also failed: ' + str(error))
                elif cleanup is None:
                    cleanup = error
                else:
                    cleanup.add_note('another loader ancestor cleanup failed: ' + str(error))
        if cleanup is not None:
            if result is not None:
                _close(result, {}, cleanup)
            raise cleanup
    return result


def capture_policy(verifiers, run_id, entry_binding, read_source, *,
                   maximum_bytes, maximum_entries, retain=None, stdlib=None):
    """Read daemon-owned inventories; retain every completed or failed acquisition.

    Each tree retains the original tree bounds. Adding the trusted interpreter
    inventory does not subtract its bytes from the admitted verifier-tree domain.
    ``stdlib`` is an explicit file-only test dependency; production uses sysconfig.
    """
    library = Path(sysconfig.get_path('stdlib') if stdlib is None else stdlib)
    _require(_path(str(library)), 'stdlib path is not absolute and normalized')
    records, files, directories = [], [], []
    occurrence = 0

    def retained(record):
        nonlocal occurrence
        records.append(record)
        index = occurrence
        occurrence += 1
        if retain is not None:
            retain(index, record)

    def keep(record, primary=None):
        try:
            retained(record)
        except BaseException as error:
            if primary is None:
                raise
            primary.add_note('loader acquisition retention also failed: ' + str(error))
            primary._worldline_retention_failed = True

    try:
        for root, logical_root, origin in (
                (Path(verifiers), VERIFIER_MOUNT, 'verifier'),
                (library, str(library), 'stdlib')):
            totals = {'bytes': 0, 'entries': 0}

            def visit(physical, logical, depth=0, parent=None):
                _require(depth <= 128, 'loader tree exceeds original depth bound')
                record = {'schemaVersion': 1, 'kind': 'loader-directory',
                          'recordId': str(uuid.uuid4()), 'runId': run_id,
                          'producer': 'daemon-loader-reader', 'path': logical,
                          'physicalPath': str(physical), 'origin': origin,
                          'before': None, 'after': None, 'namesBefore': None,
                          'namesAfter': None, 'excluded': [], 'returned': False,
                          'closeReturned': False, 'closeException': None,
                          'exception': None}
                descriptor, primary = None, None
                try:
                    # Parents were opened without following links during recursion;
                    # the reader independently anchors every file component as well.
                    descriptor = (_open_directory(physical) if parent is None else
                                  os.open(physical.name, _DIR, dir_fd=parent))
                    before = os.fstat(descriptor)
                    record['before'] = _identity(before)
                    names = sorted(os.listdir(descriptor))
                    record['namesBefore'] = names
                    totals['entries'] += 1
                    _require(totals['entries'] + len(names) <= maximum_entries,
                             'loader tree exceeds original entry bound')
                    directories.append({'path': logical, 'origin': origin,
                                        'object': _identity(before)})
                    for name in names:
                        _require(name not in ('.', '..') and '/' not in name and '\0' not in name,
                                 'invalid loader directory member')
                        info = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
                        child, path = physical / name, logical + '/' + name
                        if origin == 'stdlib' and name in ('__pycache__', 'site-packages', 'dist-packages'):
                            record['excluded'].append(name)
                            continue
                        if stat.S_ISDIR(info.st_mode):
                            visit(child, path, depth + 1, descriptor)
                        elif stat.S_ISREG(info.st_mode):
                            kind = ('source' if name.endswith('.py') else
                                    'native' if any(name.endswith(suffix) for suffix in
                                                    importlib.machinery.EXTENSION_SUFFIXES) else 'data')
                            # The entire copied verifier tree is inventoried. Standard
                            # library non-code data stays data and is not loader authority.
                            if origin == 'stdlib' and kind == 'data':
                                continue
                            item = {'schemaVersion': 1, 'kind': 'loader-file',
                                    'recordId': str(uuid.uuid4()), 'runId': run_id,
                                    'producer': 'daemon-loader-reader', 'path': path,
                                    'physicalPath': str(child), 'origin': origin,
                                    'fileKind': kind, 'binding': None, 'read': {},
                                    'exception': None}
                            failure = None
                            try:
                                content = read_source(child, item['read'])
                                totals['bytes'] += len(content)
                                totals['entries'] += 1
                                _require(totals['bytes'] <= maximum_bytes,
                                         'loader tree exceeds original byte bound')
                                _require(totals['entries'] <= maximum_entries,
                                         'loader tree exceeds original entry bound')
                                binding = {'path': path, 'origin': origin, 'kind': kind,
                                           'byteCount': len(content),
                                           'sha256': hashlib.sha256(content).hexdigest(),
                                           'sourceRecordId': item['recordId']}
                                item['binding'] = binding
                            except BaseException as error:
                                failure = error
                                item['exception'] = _error(error)
                                raise
                            finally:
                                keep(item, failure)
                            files.append(binding)
                        else:
                            raise LoaderRefusal('unsupported loader-tree member: ' + path)
                        current = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
                        _require(_identity(current) == _identity(info),
                                 'loader directory edge changed during capture')
                    record['namesAfter'] = sorted(os.listdir(descriptor))
                    after = os.fstat(descriptor)
                    record['after'] = _identity(after)
                    _require(record['namesAfter'] == names and _identity(after) == _identity(before),
                             'loader directory changed during capture')
                    record['returned'] = True
                except BaseException as error:
                    primary = error
                    record['exception'] = _error(error)
                    raise
                finally:
                    try:
                        if descriptor is not None:
                            _close(descriptor, record, primary)
                    except BaseException as error:
                        primary = error
                        record['returned'] = False
                        record['exception'] = _error(error)
                        raise
                    finally:
                        keep(record, primary)

            visit(root, logical_root)
        policy = {'schema': SCHEMA, 'runId': run_id, 'entrySource': entry_binding,
                  'stdlib': str(library), 'files': sorted(files, key=lambda item: item['path']),
                  'directories': sorted(directories, key=lambda item: item['path'])}
        return policy, records
    except BaseException as error:
        error.examiner_loader_observations = records
        raise


def validate_binding(binding, run_id, *, maximum_bytes):
    _require(type(binding) is dict and set(binding) ==
             {'schema', 'runId', 'path', 'byteCount', 'sha256'}, 'invalid loader policy binding fields')
    _require(binding['schema'] == SCHEMA and binding['runId'] == run_id
             and type(run_id) is str and bool(run_id)
             and binding['path'] == POLICY_MOUNT
             and type(binding['byteCount']) is int and 0 <= binding['byteCount'] <= maximum_bytes
             and type(binding['sha256']) is str and _HEX.fullmatch(binding['sha256']) is not None,
             'invalid loader policy binding')
    return dict(binding)


def decode_policy(content, binding, entry_binding, *, maximum_bytes, maximum_entries):
    binding = validate_binding(binding, entry_binding['runId'], maximum_bytes=maximum_bytes)
    _require(type(content) is bytes and len(content) == binding['byteCount']
             and hashlib.sha256(content).hexdigest() == binding['sha256'],
             'loader policy bytes differ from daemon binding')
    policy = json.loads(content, object_pairs_hook=_unique, parse_constant=_nonfinite)
    fields = {'schema', 'runId', 'entrySource', 'stdlib', 'files', 'directories', 'support'}
    _require(type(policy) is dict and set(policy) in (fields, fields | {'nativeGuard'}),
             'invalid loader policy fields')
    _require(policy['schema'] == SCHEMA and policy['runId'] == binding['runId']
             and policy['entrySource'] == entry_binding and _path(policy['stdlib'])
             and policy['stdlib'] != '/' and not _inside(policy['stdlib'], VERIFIER_MOUNT)
             and not _inside(VERIFIER_MOUNT, policy['stdlib']), 'invalid loader policy context')
    _require(type(policy['files']) is list and type(policy['directories']) is list,
             'invalid loader inventories')
    if 'nativeGuard' in policy:
        native = policy['nativeGuard']
        _require(type(native) is dict and set(native) == {
            'schema', 'runId', 'path', 'byteCount', 'sha256', 'sourceRecordId', 'buildReceiptSha256'}
            and native['schema'] == 'worldline-examiner-native-v1'
            and native['runId'] == binding['runId'] and native['path'] == NATIVE_MOUNT
            and type(native['byteCount']) is int and 0 < native['byteCount'] <= maximum_bytes
            and type(native['sourceRecordId']) is str and bool(native['sourceRecordId'])
            and all(type(native[key]) is str and _HEX.fullmatch(native[key]) is not None
                    for key in ('sha256', 'buildReceiptSha256')),
            'invalid native artifact binding')
    support = policy['support']
    _require(type(support) is dict and set(support) ==
             {'path', 'byteCount', 'sha256', 'sourceRecordId'}
             and support['path'] == HELPER_MOUNT
             and type(support['byteCount']) is int and 0 <= support['byteCount'] <= maximum_bytes
             and type(support['sha256']) is str and _HEX.fullmatch(support['sha256']) is not None
             and type(support['sourceRecordId']) is str and bool(support['sourceRecordId']),
             'invalid loader support binding')
    seen, roots = set(), {'verifier': VERIFIER_MOUNT, 'stdlib': policy['stdlib']}
    counts = {key: 0 for key in roots}
    sizes = {key: 0 for key in roots}
    for item in policy['directories']:
        _require(type(item) is dict and set(item) == {'path', 'origin', 'object'},
                 'invalid loader directory fields')
        origin, path, identity = item['origin'], item['path'], item['object']
        _require(type(origin) is str and origin in roots and _path(path)
                 and _inside(path, roots[origin]) and path not in seen,
                 'invalid or duplicate loader directory')
        _require(type(identity) is dict and set(identity) == {'device', 'inode', 'mode'}
                 and all(type(value) is int and value >= 0 for value in identity.values())
                 and stat.S_ISDIR(identity['mode']), 'invalid loader directory object')
        seen.add(path)
        counts[origin] += 1
    directory_paths = set(seen)
    _require(all(root in directory_paths for root in roots.values()), 'loader roots are absent')
    for item in policy['files']:
        _require(type(item) is dict and set(item) ==
                 {'path', 'origin', 'kind', 'byteCount', 'sha256', 'sourceRecordId'},
                 'invalid loader file fields')
        path, origin = item['path'], item['origin']
        _require(type(origin) is str and origin in roots and _path(path)
                 and path != roots[origin] and _inside(path, roots[origin]) and path not in seen
                 and str(PurePosixPath(path).parent) in directory_paths
                 and item['kind'] in ('source', 'native', 'data')
                 and type(item['byteCount']) is int and 0 <= item['byteCount'] <= maximum_bytes
                 and type(item['sha256']) is str and _HEX.fullmatch(item['sha256']) is not None
                 and type(item['sourceRecordId']) is str and bool(item['sourceRecordId']),
                 'invalid or duplicate loader file')
        seen.add(path)
        counts[origin] += 1
        sizes[origin] += item['byteCount']
    _require(all(value <= maximum_entries for value in counts.values())
             and all(value <= maximum_bytes for value in sizes.values()),
             'loader inventory exceeds original tree bounds')
    entry = next((item for item in policy['files'] if item['path'] == entry_binding['path']), None)
    _require(entry is not None and entry['origin'] == 'verifier'
             and entry['sha256'] == entry_binding['sha256']
             and entry['byteCount'] == entry_binding['byteCount'], 'loader policy entry differs')
    return policy


class _SourceLoader(importlib.machinery.SourceFileLoader):
    def __init__(self, owner, fullname, binding, package):
        super().__init__(fullname, binding['path'])
        self.owner, self.name, self.binding, self.package = owner, fullname, binding, package
        self.path = binding['path']

    def _name(self, fullname):
        _require(fullname == self.name, 'source loader module identity differs')

    def create_module(self, spec):
        self._name(spec.name)
        return None

    def get_filename(self, fullname):
        self._name(fullname)
        return self.path

    def is_package(self, fullname):
        self._name(fullname)
        return self.package

    def get_source(self, fullname):
        self._name(fullname)
        return importlib.util.decode_source(self.owner.read(self.binding))

    def get_code(self, fullname):
        self._name(fullname)
        source = self.owner.read(self.binding)
        return self.owner.registry.compile_source(source, self.binding)

    def exec_module(self, module):
        self._name(module.__spec__.name)
        _EXEC(self.get_code(self.name), module.__dict__)


class _FrozenLoader:
    """Register the actual frozen object used for execution, without source claims."""
    def __init__(self, owner, delegate, name):
        self.owner, self.delegate, self.name = owner, delegate, name

    def create_module(self, spec):
        return self.delegate.create_module(spec)

    def get_code(self, fullname):
        _require(fullname == self.name, 'frozen module identity differs')
        acquire = getattr(self.owner.registry, 'acquire_frozen', None)
        if acquire is not None:
            # Native acquisition owns the actual object. Python cannot register
            # an arbitrary deserialized or merely equal object on this route.
            code = acquire(fullname)
            _require(type(code) is types.CodeType, 'native frozen provider returned no code')
            return code
        code = self.delegate.get_code(fullname)
        _require(type(code) is types.CodeType, 'frozen importer returned no code')
        self.owner.registry.register(code, {'origin': 'frozen', 'module': fullname})
        return code

    def exec_module(self, module):
        _EXEC(self.get_code(module.__spec__.name), module.__dict__)

    def __getattr__(self, name):
        return getattr(self.delegate, name)


class _NativeFrozenLoader:
    """Owned frozen metadata and code; ordinary module attributes remain mutable."""
    _ORIGIN = 'frozen'
    _SEP = '/'

    def __init__(self, owner, name):
        self.owner, self.name = owner, name

    def _metadata(self, fullname, *, required=False):
        info = self.owner.registry.frozen_metadata(fullname)
        if info is None and required:
            raise ImportError(f'{fullname!r} is not a frozen module', name=fullname)
        return info

    def _resolve_filename(self, fullname, alias=None, ispkg=False):
        library = self.owner.frozen_stdlib_context['value']
        if not fullname or not library:
            return None, None
        if fullname != alias:
            if fullname.startswith('<'):
                fullname = fullname[1:]
                if not ispkg:
                    fullname = f'{fullname}.__init__'
            else:
                ispkg = False
        relative = fullname.replace('.', self._SEP)
        if ispkg:
            directory = f'{library}{self._SEP}{relative}'
            return f'{directory}{self._SEP}__init__.py', directory
        return f'{library}{self._SEP}{relative}.py', None

    def find_spec(self, fullname, path=None, target=None):
        info = self._metadata(fullname)
        if info is None:
            return None
        spec = importlib.machinery.ModuleSpec(fullname, self, origin=self._ORIGIN,
                                             is_package=info['isPackage'])
        filename, directory = self._resolve_filename(info['originalName'], fullname,
                                                     info['isPackage'])
        spec.loader_state = types.SimpleNamespace(filename=filename, origname=info['originalName'])
        if directory:
            spec.submodule_search_locations.insert(0, directory)
        self.owner.observations.append({'kind': 'native-frozen-metadata', 'metadata': dict(info),
                                        'stdlibContext': dict(self.owner.frozen_stdlib_context),
                                        'filename': filename, 'packageDirectory': directory})
        return spec

    def create_module(self, spec):
        module = types.ModuleType(spec.name)
        try:
            filename = spec.loader_state.filename
        except AttributeError:
            pass
        else:
            if filename:
                module.__file__ = filename
        return module

    def get_code(self, fullname):
        _require(fullname == self.name, 'frozen module identity differs')
        self._metadata(fullname, required=True)
        code = self.owner.registry.acquire_frozen(fullname)
        _require(type(code) is types.CodeType, 'native frozen provider returned no code')
        return code

    def exec_module(self, module):
        _EXEC(self.get_code(module.__spec__.name), module.__dict__)

    def get_source(self, fullname):
        self._metadata(fullname, required=True)
        return None

    def is_package(self, fullname):
        return self._metadata(fullname, required=True)['isPackage']

    def _fix_up_module(self, module):
        spec, state = module.__spec__, module.__spec__.loader_state
        if state is None:
            original = vars(module).pop('__origname__', None)
            assert original, 'see PyImport_ImportFrozenModuleObject()'
            package = hasattr(module, '__path__')
            assert self.is_package(module.__name__) == package
            filename, directory = self._resolve_filename(original, spec.name, package)
            spec.loader_state = types.SimpleNamespace(filename=filename, origname=original)
            locations = spec.submodule_search_locations
            if package:
                assert locations == [], locations
                if directory:
                    locations.insert(0, directory)
            else:
                assert locations is None, locations
            assert not hasattr(module, '__file__'), module.__file__
            if filename:
                try:
                    module.__file__ = filename
                except AttributeError:
                    pass
            if package and module.__path__ != locations:
                assert module.__path__ == [], module.__path__
                module.__path__.extend(locations)
        else:
            locations = spec.submodule_search_locations
            package = locations is not None
            assert sorted(vars(state)) == ['filename', 'origname'], state
            if state.origname:
                filename, directory = self._resolve_filename(state.origname, spec.name, package)
                assert state.filename == filename, (state.filename, filename)
                assert locations == ([directory] if directory else ([] if package else None))
            else:
                filename = None
                assert state.filename is None, state.filename
                assert locations == ([] if package else None), locations
            if filename:
                assert hasattr(module, '__file__')
                assert module.__file__ == filename, (module.__file__, filename)
            else:
                assert not hasattr(module, '__file__'), module.__file__
            if package:
                assert hasattr(module, '__path__')
                assert module.__path__ == locations, (module.__path__, locations)
            else:
                assert not hasattr(module, '__path__'), module.__path__
        assert not spec.has_location

    def load_module(self, fullname):
        module = _FROZEN_LOAD_SHIM(self, fullname)
        info = self._metadata(fullname, required=True)
        module.__origname__ = info['originalName']
        vars(module).pop('__file__', None)
        if info['isPackage']:
            module.__path__ = []
        self._fix_up_module(module)
        return module


class BoundImports:
    def __init__(self, policy, registry, read_source):
        self.policy, self.registry, self.read_source = policy, registry, read_source
        self.files = {item['path']: item for item in policy['files']}
        self.directories = {item['path']: item for item in policy['directories']}
        self.observations = []
        self.preloaded = []
        self.generators = []
        self._restores = []
        self._previous_meta = None
        self.frozen_stdlib_context = {'present': hasattr(sys, '_stdlib_dir'),
                                     'value': getattr(sys, '_stdlib_dir', None)}

    def read(self, binding):
        record = {'kind': 'examiner-loader-read', 'binding': dict(binding), 'read': {},
                  'exception': None, 'returned': False}
        self.observations.append(record)
        try:
            _require(self.files.get(binding['path']) is binding, 'source binding is not owned by this inventory')
            content = self.read_source(Path(binding['path']), record['read'])
            _require(len(content) == binding['byteCount']
                     and hashlib.sha256(content).hexdigest() == binding['sha256'],
                     'import source differs from daemon inventory')
            record['returned'] = True
            return content
        except BaseException as error:
            record['exception'] = _error(error)
            raise

    def directory(self, path):
        _require(_path(path) and path in self.directories, 'unbound module search directory')
        descriptor = _open_directory(path)
        primary = None
        try:
            _require(_identity(os.fstat(descriptor)) == self.directories[path]['object'],
                     'module search directory identity differs')
        except BaseException as error:
            primary = error
            raise
        finally:
            _close(descriptor, {}, primary)

    def find_spec(self, fullname, path=None, target=None):
        native_metadata = getattr(self.registry, 'frozen_metadata', None) is not None
        if path is not None and not native_metadata:
            # Iteration also checks namespace locations recomputed after sys.path changes.
            for location in path:
                self.directory(str(location))
        builtin = importlib.machinery.BuiltinImporter.find_spec(fullname, path, target)
        if builtin is not None:
            return builtin
        if native_metadata:
            frozen = _NativeFrozenLoader(self, fullname).find_spec(fullname, path, target)
            if frozen is not None:
                return frozen
        else:
            frozen = importlib.machinery.FrozenImporter.find_spec(fullname, path, target)
            if frozen is not None:
                frozen.loader = _FrozenLoader(self, frozen.loader, fullname)
                return frozen
        if path is not None and native_metadata:
            # A frozen package can have a virtual stdlib search location with
            # no disk directory. Its owned provider is authoritative for that
            # branch; every filesystem search still requires the bound directory.
            for location in path:
                self.directory(str(location))
        # Reject an unbound executable result, while preserving the normal missing
        # module outcome and namespace search semantics.
        spec = importlib.machinery.PathFinder.find_spec(fullname, path, target)
        if spec is None:
            raise ModuleNotFoundError("No module named " + repr(fullname), name=fullname)
        if spec.loader is None and spec.origin is None and spec.submodule_search_locations is not None:
            for location in spec.submodule_search_locations:
                self.directory(str(location))
            return spec
        _require(_path(spec.origin) and spec.origin in self.files, 'import origin is not in the daemon inventory')
        binding = self.files[spec.origin]
        package = spec.submodule_search_locations is not None
        if package:
            for location in spec.submodule_search_locations:
                self.directory(str(location))
        if type(spec.loader) is importlib.machinery.SourceFileLoader:
            _require(binding['kind'] == 'source', 'source loader kind differs')
            spec.loader = _SourceLoader(self, fullname, binding, package)
            spec.cached = None
            return spec
        _require(type(spec.loader) is importlib.machinery.ExtensionFileLoader
                 and binding['kind'] == 'native' and binding['origin'] == 'stdlib',
                 'bytecode, archive or verifier native loading is refused')
        self.read(binding)
        return spec

    def _generator(self, function, operation, label):
        _require(type(function) is types.FunctionType, 'stdlib generator function is unavailable')
        caller_code, caller_globals = function.__code__, function.__globals__
        source_path = caller_globals.get('__file__')
        binding = self.files.get(source_path)
        _require(binding is not None and binding['origin'] == 'stdlib'
                 and binding['kind'] == 'source', 'stdlib generator source is unbound')
        self.read(binding)
        flags = 0
        for feature in __future__.all_feature_names:
            flags |= getattr(__future__, feature).compiler_flag
        flags &= caller_code.co_flags
        record = {'label': label, 'function': function, 'code': caller_code,
                  'globals': caller_globals, 'binding': binding, 'flags': flags}
        self.generators.append(record)

        def routed(source, globals=None, locals=None):
            caller = sys._getframe(1)
            try:
                _require(caller.f_code is caller_code and caller.f_globals is caller_globals,
                         'unregistered generator caller')
                _require(type(source) in (str, bytes), 'generator did not supply source text')
                # The call-site globals identify the producer; the explicit target
                # globals/locals are the original generator's separate arguments.
                if globals is None:
                    globals = caller.f_globals
                    if locals is None:
                        locals = caller.f_locals
                if locals is None:
                    locals = globals
                provenance = {'origin': 'stdlib-generator', 'generator': label,
                              'sourceBinding': dict(binding), 'source': source,
                              'mode': operation, 'flags': flags}
                code = _COMPILE(source, '<string>', operation, flags=flags, dont_inherit=True)
                self.registry.register(code, provenance)
                self.observations.append({'kind': 'examiner-generated-code', 'provenance': provenance})
                return (_EVAL(code, globals, locals) if operation == 'eval'
                        else _EXEC(code, globals, locals))
            finally:
                del caller

        old = caller_globals.get(operation, _ABSENT)
        self._restores.append((caller_globals, operation, old))
        caller_globals[operation] = routed

    def __enter__(self):
        _require(self._previous_meta is None, 'loader context is already active')
        self._previous_meta = sys.meta_path
        # Cached modules do not visit meta_path. Record that boundary without
        # representing their already-existing objects as new loader output.
        self.preloaded = [
            {'name': name, 'module': module,
             'origin': getattr(getattr(module, '__spec__', None), 'origin', None),
             'visitedBoundLoader': False}
            for name, module in tuple(sys.modules.items())]
        try:
            bind_native = getattr(self.registry, 'bind_native_generators', None)
            if bind_native is not None:
                bind_native()
            else:
                self._generator(collections.namedtuple, 'eval', 'collections.namedtuple')
                builder = getattr(dataclasses, '_FuncBuilder', None)
                if builder is not None:
                    self._generator(builder.add_fns_to_class, 'exec', 'dataclasses._FuncBuilder.add_fns_to_class')
                else:
                    self._generator(dataclasses._create_fn, 'exec', 'dataclasses._create_fn')
            # This finder makes the entire new-import decision. Keeping a later
            # arbitrary finder would turn a missing binding into a fallback path.
            sys.meta_path = [self]
            return self
        except BaseException as error:
            self.__exit__(type(error), error, error.__traceback__)
            raise

    def __exit__(self, kind, primary, traceback):
        failures = []
        for namespace, key, old in reversed(self._restores):
            try:
                if old is _ABSENT:
                    namespace.pop(key, None)
                else:
                    namespace[key] = old
            except BaseException as error:
                failures.append(error)
        self._restores.clear()
        if self._previous_meta is not None:
            sys.meta_path = self._previous_meta
            self._previous_meta = None
        if failures:
            if primary is not None:
                for error in failures:
                    primary.add_note('loader restoration also failed: ' + str(error))
            else:
                raise failures[0]
        return False
