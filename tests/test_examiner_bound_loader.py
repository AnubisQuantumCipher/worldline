"""Additive bound-loader controls, without a native confinement/proof claim."""
from __future__ import annotations

import base64
import collections
from contextlib import contextmanager
import dataclasses
import hashlib
import importlib
import importlib.machinery
import json
import os
from pathlib import Path
import sys
import sysconfig
import tempfile
import types
import unittest
from unittest.mock import patch
import uuid
import zipfile

from worldline.linux import examiner_loader as loader
from worldline.linux import private_evaluator as evaluator
from worldline.linux.kernel_role_observer import KernelRoleObserver
from worldline.raw_observation import retention_failed


def entry_binding(source, run='loader-control'):
    return {'schemaVersion': 1, 'runId': run, 'sourceRecordId': 'entry-control',
            'path': evaluator.VERIFIER_MOUNT + '/entry.py', 'byteCount': len(source),
            'sha256': hashlib.sha256(source).hexdigest()}


def support_binding():
    content = Path(loader.__file__).read_bytes()
    return {'path': loader.HELPER_MOUNT, 'byteCount': len(content),
            'sha256': hashlib.sha256(content).hexdigest(), 'sourceRecordId': 'support-control'}


def encoded_policy(policy):
    content = json.dumps(policy, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
    binding = {'schema': loader.SCHEMA, 'runId': policy['runId'],
               'path': loader.POLICY_MOUNT, 'byteCount': len(content),
               'sha256': hashlib.sha256(content).hexdigest()}
    return content, binding


class LoaderPolicyControls(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='worldline-loader-policy-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.verifiers = self.root / 'verifiers'
        self.library = self.root / 'stdlib'
        self.verifiers.mkdir()
        self.library.mkdir()
        self.source = b'pass\n'
        (self.verifiers / 'entry.py').write_bytes(self.source)
        (self.library / 'ordinary.py').write_bytes(b'value = 1\n')
        self.binding = entry_binding(self.source)

    def capture(self, retain=None, read=evaluator._read_examiner_source):
        policy, records = loader.capture_policy(
            self.verifiers, self.binding['runId'], self.binding, read,
            maximum_bytes=evaluator.MAX_TREE_BYTES, maximum_entries=evaluator.MAX_TREE_ENTRIES,
            retain=retain, stdlib=self.library)
        policy['support'] = support_binding()
        return policy, records

    def decode(self, policy, binding=None, content=None):
        original, bound = encoded_policy(policy)
        return loader.decode_policy(original if content is None else content,
            bound if binding is None else binding, self.binding,
            maximum_bytes=evaluator.MAX_TREE_BYTES, maximum_entries=evaluator.MAX_TREE_ENTRIES)

    def test_complete_capture_retains_empty_binary_source_and_directory_objects(self):
        (self.verifiers / 'empty.py').write_bytes(b'')
        (self.verifiers / 'binary.py').write_bytes(b'\0\xff\r\n')
        (self.verifiers / 'namespace').mkdir()
        retained = []
        policy, records = self.capture(lambda index, record: retained.append((index, record)))
        self.assertEqual([record for _, record in retained], records)
        self.assertEqual([index for index, _ in retained], list(range(len(records))))
        self.assertEqual(self.decode(policy), policy)
        files = {row['path']: row for row in records if row['kind'] == 'loader-file'}
        for name, expected in [('empty.py', b''), ('binary.py', b'\0\xff\r\n')]:
            row = files[evaluator.VERIFIER_MOUNT + '/' + name]
            self.assertTrue(row['read']['readReturned'])
            self.assertTrue(row['read']['readReachedEof'])
            self.assertEqual(base64.b64decode(row['read']['bytes']['payload']), expected)
        directories = [row for row in records if row['kind'] == 'loader-directory']
        self.assertTrue(directories)
        for row in directories:
            self.assertTrue(row['returned'])
            self.assertTrue(row['closeReturned'])
            self.assertEqual(row['namesBefore'], row['namesAfter'])
            self.assertEqual(row['before'], row['after'])

    def test_policy_binding_refuses_changed_bytes_run_entry_and_duplicate_fields(self):
        policy, _ = self.capture()
        content, binding = encoded_policy(policy)
        for changed in (content + b' ', content.replace(b'ordinary', b'changedx')):
            with self.subTest(content=changed), self.assertRaises(loader.LoaderRefusal):
                self.decode(policy, content=changed)
        for changed in ({**binding, 'runId': 'different'}, {**binding, 'byteCount': True},
                        {**binding, 'sha256': 'bad'}, {**binding, 'extra': None}):
            with self.subTest(binding=changed), self.assertRaises(loader.LoaderRefusal):
                self.decode(policy, binding=changed)
        for raw in (content[:-1] + b',"runId":"loader-control"}',
                    content.replace(b'"byteCount":5', b'"byteCount":NaN', 1)):
            bound = {**binding, 'byteCount': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
            with self.subTest(raw=raw), self.assertRaises((ValueError, loader.LoaderRefusal)):
                self.decode(policy, binding=bound, content=raw)
        wrong = {**policy, 'entrySource': {**self.binding, 'sourceRecordId': 'another'}}
        with self.assertRaises(loader.LoaderRefusal):
            self.decode(wrong)

    def test_duplicate_unbound_malformed_files_and_namespace_objects_refuse(self):
        policy, _ = self.capture()
        for mutate in (
                lambda p: p['files'].append(dict(p['files'][0])),
                lambda p: p['files'][0].update(path='/candidate/unbound.py'),
                lambda p: p['files'][0].update(byteCount=True),
                lambda p: p['directories'][0]['object'].update(mode=0),
                lambda p: p.update(support={}),
                lambda p: p.update(directories=[])):
            changed = json.loads(json.dumps(policy))
            mutate(changed)
            with self.subTest(policy=changed), self.assertRaises(loader.LoaderRefusal):
                self.decode(changed)

    def test_site_packages_and_bytecode_are_not_executable_inventory(self):
        for name in ('site-packages', 'dist-packages', '__pycache__'):
            directory = self.library / name
            directory.mkdir()
            (directory / 'candidate.py').write_text('raise AssertionError("must not execute")\n')
        (self.library / 'ordinary.pyc').write_bytes(b'not bytecode')
        policy, records = self.capture()
        self.assertEqual([row['path'] for row in policy['files'] if row['origin'] == 'stdlib'],
                         [str(self.library / 'ordinary.py')])
        directory = next(row for row in records if row.get('physicalPath') == str(self.library))
        self.assertEqual(set(directory['excluded']), {'site-packages', 'dist-packages', '__pycache__'})

    def test_missing_and_retention_failures_keep_the_original_primary(self):
        original = FileNotFoundError('controlled original read failure')
        retained = []

        def read(path, record):
            if path.name == 'entry.py':
                record['readReturned'] = False
                record['bytes'] = None
                raise original
            return evaluator._read_examiner_source(path, record)

        def retain(index, record):
            retained.append(record)
            if record['kind'] == 'loader-file':
                raise OSError('controlled retention failure')

        with self.assertRaises(FileNotFoundError) as caught:
            self.capture(retain, read)
        self.assertIs(caught.exception, original)
        self.assertTrue(retention_failed(original))
        row = next(row for row in retained if row['kind'] == 'loader-file')
        self.assertIsNone(row['read']['bytes'])
        self.assertFalse(row['read']['readReturned'])
        self.assertTrue(all(row['closeReturned'] for row in retained if row['kind'] == 'loader-directory'))

    def test_retention_failure_on_success_prevents_a_policy_result(self):
        def retain(index, record):
            raise OSError('controlled successful-read retention refusal')
        with self.assertRaises(OSError) as caught:
            self.capture(retain)
        self.assertTrue(caught.exception.examiner_loader_observations)

    def test_daemon_acknowledgement_binds_policy_and_live_role_requires_it(self):
        policy, _ = self.capture()
        _content, binding = encoded_policy(policy)
        argv = ['/usr/bin/python3', self.binding['path']]
        observer = KernelRoleObserver(
            {'runId': self.binding['runId'], 'runtime': str(self.root), 'argv': argv,
             'examinerEntryBinding': self.binding, 'loaderPolicy': str(self.root / 'policy'),
             'examinerLoaderBinding': binding}, maximum_bytes=evaluator.MAX_TREE_BYTES,
            maximum_request=evaluator.MAX_REQUEST_BYTES, handshake_seconds=60)
        record = {'recordId': 'role-observation'}
        response = json.loads(observer._acknowledgement('examiner', record))
        self.assertEqual(record['examinerLoaderBinding'], binding)
        self.assertEqual(response['loaderPolicy'], binding)
        self.assertEqual(evaluator._role_acknowledgement(
            response, 'examiner', argv, self.binding['runId'], require_loader=True), self.binding)
        legacy = {key: value for key, value in response.items() if key != 'loaderPolicy'}
        with self.assertRaises(evaluator.BackendFailure):
            evaluator._role_acknowledgement(legacy, 'examiner', argv, self.binding['runId'], require_loader=True)
        for role in ('worker', 'candidate'):
            self.assertEqual(json.loads(observer._acknowledgement(role, {'recordId': 'worker'})),
                             {'recordId': 'worker'})


class LoaderProducerFailures(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='worldline-loader-producer-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.library = self.root / 'stdlib'
        self.library.mkdir()
        (self.library / 'ordinary.py').write_bytes(b'pass\n')
        actual_capture = loader.capture_policy

        def capture(*args, **kwargs):
            return actual_capture(*args, **kwargs, stdlib=self.library)

        self.capture_patch = patch.object(loader, 'capture_policy', side_effect=capture)
        self.capture_patch.start()
        self.addCleanup(self.capture_patch.stop)

    def spec(self):
        runtime = self.root / uuid.uuid4().hex
        verifiers = runtime / 'verifiers'
        verifiers.mkdir(parents=True)
        (verifiers / 'entry.py').write_bytes(b'pass\n')
        return types.SimpleNamespace(runtime=runtime, run_id='loader-control')

    def test_serialization_and_binding_failures_retain_completed_acquisitions_without_callback(self):
        cases = (('serialization', patch.object(evaluator.json, 'dumps',
                   side_effect=ValueError('controlled policy serialization failure'))),
                 ('binding', patch.object(loader, 'validate_binding',
                   side_effect=loader.LoaderRefusal('controlled oversized policy binding'))))
        for stage, fault in cases:
            with self.subTest(stage=stage), fault, self.assertRaises((ValueError, loader.LoaderRefusal)) as caught:
                evaluator.PrivateEvaluator._loader_policy(self.spec(), entry_binding(b'pass\n'), None)
            records = caught.exception.examiner_loader_observations
            self.assertTrue(any(row['kind'] == 'loader-file' for row in records))
            self.assertTrue(records[-2]['writeReturned'])
            self.assertTrue(records[-2]['closeReturned'])
            self.assertEqual(records[-1]['kind'], 'examiner-loader-policy')
            self.assertEqual(records[-1]['serializationReturned'], stage != 'serialization')
            self.assertIsNone(records[-1]['binding'])
            self.assertEqual(records[-1]['exception']['message'], str(caught.exception))

    def test_support_and_policy_write_close_and_retention_failures_preserve_original_primary(self):
        actual_write = evaluator._write_loader_artifact
        for filename, kind in (('examiner_loader.py', 'private-examiner-loader-support'),
                               ('loader-policy.json', 'private-examiner-loader-policy')):
            for failure in (OSError('original write failure'), KeyboardInterrupt('original interruption')):
                retained, closes = [], []
                secondary = OSError('secondary close failure')

                def write(path, content, record):
                    if path.name != filename:
                        return actual_write(path, content, record)

                    def fail_write(_content):
                        raise failure

                    def fail_close():
                        closes.append(True)
                        raise secondary

                    stream = types.SimpleNamespace(write=fail_write, close=fail_close)
                    return actual_write(types.SimpleNamespace(open=lambda _mode: stream), content, record)

                def retain(site, occurrence, record):
                    retained.append(record)
                    if site == kind:
                        raise OSError('secondary retention failure')

                with self.subTest(filename=filename, failure=type(failure)), \
                        patch.object(evaluator, '_write_loader_artifact', side_effect=write), \
                        self.assertRaises(type(failure)) as caught:
                    evaluator.PrivateEvaluator._loader_policy(self.spec(), entry_binding(b'pass\n'), retain)
                self.assertIs(caught.exception, failure)
                self.assertTrue(retention_failed(failure))
                self.assertEqual(closes, [True])
                record = failure.examiner_loader_observations[-1]
                self.assertIs(retained[-1], record)
                self.assertFalse(record['writeReturned'])
                self.assertFalse(record['closeReturned'])
                self.assertEqual(record['writeException']['message'], str(failure))
                self.assertEqual(record['closeException']['message'], str(secondary))
                self.assertEqual(record['exception']['message'], str(failure))
                self.assertTrue(any('close also failed' in note for note in failure.__notes__))

    def test_close_failure_after_returned_write_refuses_and_short_write_keeps_its_primary(self):
        for short in (False, True):
            record, closes, chmods = {}, [], []
            close_failure = OSError('close failed after returned write')

            def close():
                closes.append(True)
                raise close_failure

            content = b'actual artifact bytes\n'
            stream = types.SimpleNamespace(write=lambda data: 0 if short else len(data), close=close)
            path = types.SimpleNamespace(open=lambda mode: stream, chmod=lambda mode: chmods.append(mode))
            with self.subTest(short=short), self.assertRaises((OSError, evaluator.BackendFailure)) as caught:
                evaluator._write_loader_artifact(path, content, record)
            if short:
                self.assertIsInstance(caught.exception, evaluator.BackendFailure)
                self.assertEqual(caught.exception.code, 'PRIVATE_EXAMINER_LOADER_INVALID')
                self.assertTrue(any('close also failed' in note for note in caught.exception.__notes__))
            else:
                self.assertIs(caught.exception, close_failure)
            self.assertTrue(record['writeReturned'])
            self.assertFalse(record['closeReturned'])
            self.assertEqual(record['closeException']['message'], str(close_failure))
            self.assertEqual(closes, [True])
            self.assertEqual(chmods, [])


class BoundImportControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # One actual interpreter-source acquisition is reused within this action;
        # every loaded file is independently reread and checked against it.
        with tempfile.TemporaryDirectory(prefix='worldline-loader-stdlib-') as temporary:
            root = Path(temporary)
            (root / 'entry.py').write_bytes(b'pass\n')
            policy, _records = loader.capture_policy(root, 'loader-control', entry_binding(b'pass\n'),
                evaluator._read_examiner_source, maximum_bytes=evaluator.MAX_TREE_BYTES,
                maximum_entries=evaluator.MAX_TREE_ENTRIES)
        cls.library_files = [row for row in policy['files'] if row['origin'] == 'stdlib']
        cls.library_directories = [row for row in policy['directories'] if row['origin'] == 'stdlib']

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='worldline-bound-import-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.namespace = 'worldline_loader_' + uuid.uuid4().hex

    def source(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def imports(self):
        # A synthetic local-path routing fixture, not the production policy decoder
        # or a claim that /tmp is an authorized production verifier origin.
        files = list(self.library_files)
        directories = list(self.library_directories)
        for root, _dirs, names in os.walk(self.root):
            path = Path(root)
            info = path.stat()
            directories.append({'path': str(path), 'origin': 'verifier',
                                'object': {'device': info.st_dev, 'inode': info.st_ino, 'mode': info.st_mode}})
            for name in names:
                current = path / name
                if not current.is_file() or current.is_symlink():
                    continue
                content = current.read_bytes()
                kind = ('source' if name.endswith('.py') else
                        'native' if name.endswith('.so') else 'data')
                files.append({'path': str(current), 'origin': 'verifier', 'kind': kind,
                              'byteCount': len(content), 'sha256': hashlib.sha256(content).hexdigest(),
                              'sourceRecordId': 'local-control-' + str(current.relative_to(self.root))})
        registry = evaluator._RegisteredExaminerCode()
        return loader.BoundImports({'files': files, 'directories': directories}, registry,
                                   evaluator._read_examiner_source)

    @contextmanager
    def active(self, imports):
        previous = sys.path
        modules = set(sys.modules)
        sys.path = [str(self.root), *previous]
        try:
            with imports:
                yield imports
        finally:
            sys.path = previous
            for name in tuple(sys.modules):
                if name not in modules and (name == self.namespace or name.startswith(self.namespace + '.')):
                    sys.modules.pop(name, None)
            importlib.invalidate_caches()

    def test_package_relative_and_cyclic_imports_register_actual_code(self):
        package = self.namespace
        self.source(package + '/__init__.py', b'value = "package"\nfrom . import helper\n')
        self.source(package + '/helper.py', b'from . import value\ndef ordinary():\n return value\n')
        imports = self.imports()
        with self.active(imports):
            module = importlib.import_module(package)
            self.assertEqual(module.helper.ordinary(), 'package')
            self.assertEqual(module.__package__, package)
            self.assertEqual(module.__spec__.name, package)
            self.assertEqual(module.__file__, str(self.root / package / '__init__.py'))
            self.assertTrue(imports.registry.contains(module.helper.ordinary.__code__))
            self.assertFalse(imports.registry.contains(module.helper.ordinary.__code__.replace()))
            self.assertIsInstance(module.__loader__, importlib.machinery.SourceFileLoader)
            self.assertIn('from . import helper', module.__loader__.get_source(package))
            with self.assertRaises(loader.LoaderRefusal):
                module.__loader__.get_code('different_module')

    def test_namespace_locations_and_later_unbound_location_are_checked(self):
        package = self.namespace
        self.source(package + '/helper.py', b'value = "namespace"\n')
        imports = self.imports()
        with self.active(imports):
            module = importlib.import_module(package + '.helper')
            self.assertEqual(module.value, 'namespace')
            namespace = sys.modules[package]
            self.assertIsNone(namespace.__spec__.origin)
            with tempfile.TemporaryDirectory(prefix='worldline-unbound-namespace-') as temporary:
                candidate = Path(temporary) / package
                candidate.mkdir()
                (candidate / 'another.py').write_text('value = "unbound"\n')
                sys.path.insert(0, temporary)
                with self.assertRaises(loader.LoaderRefusal):
                    importlib.import_module(package + '.another')

    def test_encoding_cookie_empty_source_and_future_semantics(self):
        self.source(self.namespace + '/__init__.py', b'')
        self.source(self.namespace + '/latin.py', b'# coding: latin-1\nvalue = "caf\xe9"\n')
        self.source(self.namespace + '/annotations.py',
                    b'from __future__ import annotations\ndef f(value: int) -> int:\n return value\n')
        imports = self.imports()
        with self.active(imports):
            self.assertEqual(importlib.import_module(self.namespace + '.latin').value, 'caf\xe9')
            module = importlib.import_module(self.namespace + '.annotations')
            self.assertEqual(module.f.__annotations__['value'], 'int')
            self.assertTrue(imports.registry.contains(module.f.__code__))

    def test_changed_deleted_or_unbound_source_never_executes(self):
        path = self.source(self.namespace + '.py', b'raise AssertionError("should not execute")\n')
        imports = self.imports()
        path.write_bytes(b'value = "changed"\n')
        with self.active(imports), self.assertRaises(loader.LoaderRefusal):
            importlib.import_module(self.namespace)
        binding = imports.files[str(path)]
        path.unlink()
        with self.assertRaises(FileNotFoundError):
            imports.read(binding)
        row = imports.observations[-1]
        self.assertFalse(row['returned'])
        self.assertIsNone(row['read']['bytes'])
        path.write_text('value = "new unbound path"\n')
        other = self.source('unbound.py', b'value = "unbound"\n')
        with self.active(imports), self.assertRaises(loader.LoaderRefusal):
            imports.find_spec('unbound')
        self.assertTrue(other.exists())

    def test_bytecode_archive_and_verifier_native_origins_refuse(self):
        native = self.source(self.namespace + '.so', b'not an extension')
        imports = self.imports()
        with self.active(imports), self.assertRaises(loader.LoaderRefusal):
            imports.find_spec(self.namespace)
        native.unlink()
        self.source(self.namespace + '.pyc', b'not bytecode')
        imports = self.imports()
        with self.active(imports), self.assertRaises(loader.LoaderRefusal):
            imports.find_spec(self.namespace)
        archive = self.root / 'modules.zip'
        with zipfile.ZipFile(archive, 'w') as stream:
            stream.writestr(self.namespace + '_archive.py', 'value = "archive"\n')
        imports = self.imports()
        with self.active(imports):
            sys.path.insert(0, str(archive))
            with self.assertRaises(loader.LoaderRefusal):
                imports.find_spec(self.namespace + '_archive')

    def test_builtin_frozen_and_preloaded_module_boundaries_remain_explicit(self):
        imports = self.imports()
        with self.active(imports):
            spec = imports.find_spec('_ast')
            self.assertIs(spec.loader, importlib.machinery.BuiltinImporter)
            frozen = imports.find_spec('__hello__')
            code = frozen.loader.get_code('__hello__')
            self.assertTrue(imports.registry.contains(code))
            self.assertFalse(imports.registry.contains(code.replace()))
            self.assertIs(importlib.import_module('collections'), collections)
            row = next(row for row in imports.preloaded if row['name'] == 'collections')
            self.assertIs(row['module'], collections)
            self.assertFalse(row['visitedBoundLoader'])

    def test_generators_preserve_target_globals_and_register_actual_nested_objects(self):
        source = (b'from collections import namedtuple\nfrom dataclasses import dataclass\n'
                  b'from typing import NamedTuple\nfrom enum import Enum\n'
                  b'Point = namedtuple("Point", "value", defaults=["default"])\n'
                  b'@dataclass\nclass Box:\n value: str\n'
                  b'class Typed(NamedTuple):\n value: str\n'
                  b'class Choice(Enum):\n item = "item"\n')
        self.source(self.namespace + '.py', source)
        imports = self.imports()
        with self.active(imports):
            module = importlib.import_module(self.namespace)
            self.assertEqual(module.Point().value, 'default')
            self.assertEqual(module.Box('box').value, 'box')
            self.assertEqual(module.Typed('typed').value, 'typed')
            self.assertEqual(module.Choice.item.value, 'item')
            self.assertTrue(imports.registry.contains(module.Point.__new__.__code__))
            self.assertTrue(imports.registry.contains(module.Box.__init__.__code__))
            self.assertTrue(imports.registry.contains(module.Typed.__new__.__code__))
            self.assertIs(module.Box.__init__.__globals__, module.__dict__)
            self.assertIsNot(module.Point.__new__.__globals__, collections.__dict__)
            with self.assertRaises(loader.LoaderRefusal):
                collections.__dict__['eval']('1', {})
            with self.assertRaises(loader.LoaderRefusal):
                dataclasses.__dict__['exec']('value = 1', {}, {})

    def test_module_state_and_meta_path_restore_after_normal_and_base_exception_exits(self):
        original_meta = sys.meta_path
        absent = object()
        original_eval = collections.__dict__.get('eval', absent)
        original_exec = dataclasses.__dict__.get('exec', absent)
        for failure in (None, KeyboardInterrupt('controlled interruption'), SystemExit(0)):
            imports = self.imports()
            try:
                with self.active(imports):
                    if failure is not None:
                        raise failure
            except BaseException as error:
                self.assertIs(error, failure)
            self.assertIs(sys.meta_path, original_meta)
            self.assertIs(collections.__dict__.get('eval', absent), original_eval)
            self.assertIs(dataclasses.__dict__.get('exec', absent), original_exec)

    def test_direct_candidate_data_reads_remain_available(self):
        data = self.root / 'candidate.data'
        data.write_bytes(b'ordinary candidate bytes\n')
        self.source(self.namespace + '.py',
                    ('from pathlib import Path\nvalue = Path(' + repr(str(data)) + ').read_bytes()\n').encode())
        imports = self.imports()
        with self.active(imports):
            module = importlib.import_module(self.namespace)
            self.assertEqual(module.value, data.read_bytes())


class NativeArtifactLayoutControls(unittest.TestCase):
    """File-only selection controls; fixture bytes are never loaded as native code."""
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='worldline-native-layout-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.package = self.root / 'source'
        self.module = self.package / 'runtime/worldline/linux/private_evaluator.py'
        self.module.parent.mkdir(parents=True)
        self.module.write_text('# file-only package-location fixture\n')
        self.runtime = self.root / 'invocation'
        self.runtime.mkdir()
        self.spec = evaluator.PrivateEvaluationSpec('layout-control', {}, self.package,
            ('/usr/bin/python3', evaluator.VERIFIER_MOUNT + '/entry.py'), '/work',
            self.runtime / 'report', self.runtime)

    def artifact(self, directory, receipt_name='build.json'):
        directory.mkdir(exist_ok=True)
        library = directory / 'libworldline_examiner_guard.so'
        library.write_bytes(b'file-only native selection fixture; never loaded\x00\xff')
        (directory / receipt_name).write_text(json.dumps({
            'artifact': str(library), 'bytes': library.stat().st_size,
            'sha256': hashlib.sha256(library.read_bytes()).hexdigest(),
            'compilerReturncode': 0, 'confinementAcceptance': False, 'phaseAcceptance': False}))
        return library

    def test_development_core_under_lib_keeps_reviewed_sibling_artifact_selection(self):
        (self.package / 'lib').mkdir()
        (self.package / 'lib/libworldline_core.so').write_bytes(b'file-only checked core placeholder')
        library = self.artifact(self.root / 'native-artifacts')
        with patch.object(evaluator, '__file__', str(self.module)):
            copied, _binding, record = evaluator.PrivateEvaluator._native_artifact(self.spec, None)
        self.assertEqual(record['selection'], 'reviewed-development-frame')
        self.assertEqual(record['artifactRead']['path'], str(library))
        self.assertEqual(Path(copied).read_bytes(), library.read_bytes())

    def test_installed_core_selects_adjacent_artifact_and_never_falls_back_when_missing(self):
        (self.package / 'libworldline_core.so').write_bytes(b'file-only installed core placeholder')
        self.artifact(self.root / 'native-artifacts')
        observed = []
        with patch.object(evaluator, '__file__', str(self.module)), self.assertRaises(FileNotFoundError):
            evaluator.PrivateEvaluator._native_artifact(self.spec,
                lambda _kind, _occurrence, record: observed.append(record))
        self.assertEqual(observed[0]['selection'], 'installed-package')
        self.assertEqual(observed[0]['artifactRead']['path'],
                         str(self.package / 'libworldline_examiner_guard.so'))
        self.assertIsNone(observed[0]['artifactRead']['bytes'])
        library = self.artifact(self.package, 'native-build.json')
        with patch.object(evaluator, '__file__', str(self.module)):
            copied, _binding, record = evaluator.PrivateEvaluator._native_artifact(self.spec, None)
        self.assertEqual(record['selection'], 'installed-package')
        self.assertEqual(Path(copied).read_bytes(), library.read_bytes())

    def test_actual_receipt_mismatch_and_retention_failure_keep_complete_acquisition(self):
        library = self.artifact(self.root / 'native-artifacts')
        receipt = library.parent / 'build.json'
        value = json.loads(receipt.read_text())
        value['sha256'] = '0' * 64
        receipt.write_text(json.dumps(value))
        observed = []
        def refuse(_kind, _occurrence, record):
            observed.append(record)
            raise OSError('controlled native acquisition retention failure')
        with patch.object(evaluator, '__file__', str(self.module)), \
                self.assertRaises(evaluator.BackendFailure) as caught:
            evaluator.PrivateEvaluator._native_artifact(self.spec, refuse)
        self.assertTrue(retention_failed(caught.exception))
        self.assertEqual(observed[0]['artifactRead']['bytes'],
            {'encoding': 'base64', 'payload': base64.b64encode(library.read_bytes()).decode('ascii')})
        self.assertIsNotNone(observed[0]['buildReceiptRead']['bytes'])
        self.assertFalse((self.runtime / 'examiner-guard.so').exists())


class LoaderOwnedJournal(unittest.TestCase):
    def setUp(self):
        from test_private_acquisition_terminal import PrivateAcquisitionTerminal
        PrivateAcquisitionTerminal.setUp(self)
        self.control = PrivateAcquisitionTerminal

    def test_actual_source_support_and_policy_callbacks_retain_through_legacy_writer(self):
        from worldline.evaluation_terminal import value_bytes
        writer = self.control.writer(self)
        runtime = self.root / 'loader-owned'
        verifiers = runtime / 'verifiers'
        verifiers.mkdir(parents=True)
        (verifiers / 'entry.py').write_bytes(b'pass\n')
        spec = evaluator.PrivateEvaluationSpec(
            run_id='private-invocation', roots={'/work': self.root / 'candidate'},
            verifier_directory=verifiers,
            argv=('/usr/bin/python3', evaluator.VERIFIER_MOUNT + '/entry.py'), cwd='/work',
            report_directory=runtime / 'report', runtime=runtime)
        expected = []

        def retain(kind, occurrence, record):
            self.control.retain(self, writer, kind, occurrence, record)
            expected.append(('private-invocation', kind, occurrence, record))

        path, binding, records = evaluator.PrivateEvaluator._loader_policy(
            spec, entry_binding(b'pass\n', 'private-invocation'), retain)
        actual = self.terminal.captured_observation_events(writer.bound)
        self.assertEqual(value_bytes(actual), value_bytes(tuple(expected)))
        self.assertEqual([row[3] for row in actual], records)
        self.assertTrue(any(row[1] == 'private-examiner-loader-source' for row in actual))
        self.assertEqual([row[1:3] for row in actual[-2:]], [
            ('private-examiner-loader-support', 0), ('private-examiner-loader-policy', 0)])
        self.assertEqual(hashlib.sha256(Path(path).read_bytes()).hexdigest(), binding['sha256'])
        self.assertTrue(records[-1]['readback']['readReturned'])
        stored = self.control.rows(self)
        self.assertEqual([row[3] for row in stored], [value_bytes(row[2]) for row in expected])
        self.assertEqual([row[4] for row in stored], [value_bytes(row[3]) for row in expected])

    def test_actual_native_artifact_acquisition_retains_complete_bytes_in_original_writer(self):
        from worldline.evaluation_terminal import value_bytes
        writer = self.control.writer(self)
        runtime = self.root / 'native-artifact-owned'
        runtime.mkdir()
        spec = evaluator.PrivateEvaluationSpec(
            run_id='private-invocation', roots={'/work': self.root / 'candidate'},
            verifier_directory=runtime / 'verifiers',
            argv=('/usr/bin/python3', evaluator.VERIFIER_MOUNT + '/entry.py'), cwd='/work',
            report_directory=runtime / 'report', runtime=runtime)
        retained = []
        def retain(kind, occurrence, record):
            self.control.retain(self, writer, kind, occurrence, record)
            retained.append(('private-invocation', kind, occurrence, record))
        copied, binding, record = evaluator.PrivateEvaluator._native_artifact(spec, retain)
        actual = self.terminal.captured_observation_events(writer.bound)
        self.assertEqual(value_bytes(actual), value_bytes(tuple(retained)))
        self.assertEqual([item[1:3] for item in actual], [('private-examiner-native-artifact', 0)])
        self.assertTrue(record['returned'])
        self.assertTrue(record['artifactRead']['readReturned'])
        self.assertTrue(record['buildReceiptRead']['readReturned'])
        self.assertEqual(record['artifactRead']['bytes'], record['readback']['bytes'])
        self.assertEqual(hashlib.sha256(Path(copied).read_bytes()).hexdigest(), binding['sha256'])
        self.assertEqual(binding['buildReceiptSha256'], hashlib.sha256(
            base64.b64decode(record['buildReceiptRead']['bytes']['payload'])).hexdigest())

    def test_native_artifact_observation_rejects_all_wrong_occurrence_types_and_values(self):
        from worldline.evaluation_terminal import TerminalRefused
        writer = self.control.writer(self)
        for occurrence in (None, True, False, '0', -1, 1, 0.0, [], {}):
            with self.subTest(occurrence=occurrence), self.assertRaises(TerminalRefused) as caught:
                self.control.retain(self, writer, 'private-examiner-native-artifact', occurrence,
                                    {'bytes': None})
            self.assertEqual(str(caught.exception), 'RAW_CAPTURE_OCCURRENCE_INVALID')
        self.assertEqual(self.control.rows(self), [])

    def test_loader_domains_keep_boolean_string_absence_and_wrong_ordinal_refusals(self):
        from worldline.evaluation_terminal import TerminalRefused
        writer = self.control.writer(self)
        for kind in ('private-examiner-loader-source', 'private-examiner-loader-support',
                     'private-examiner-loader-policy'):
            invalid = [None, True, False, '0', -1, 0.0]
            if kind != 'private-examiner-loader-source':
                invalid.append(1)
            for occurrence in invalid:
                with self.subTest(kind=kind, occurrence=occurrence):
                    with self.assertRaises(TerminalRefused) as caught:
                        self.control.retain(self, writer, kind, occurrence, {'present': False})
                    self.assertEqual(str(caught.exception), 'RAW_CAPTURE_OCCURRENCE_INVALID')
        self.assertEqual(self.control.rows(self), [])


@unittest.skipUnless(os.environ.get('WORLDLINE_PRIVATE_EVALUATOR_TEST') == '1',
                     'original controlled user-systemd integration prerequisite')
class BoundLoaderOriginalIntegration(unittest.TestCase):
    def setUp(self):
        from test_private_evaluator import PrivateEvaluatorIntegration
        PrivateEvaluatorIntegration.setUp(self)

    def _run_retention_diagnostic(self, method_name):
        """Retain actual failed-control values, then re-raise its assertion.

        This invokes the unchanged original method with this test's ordinary
        fixture. It neither wraps the evaluator nor changes its observer. The
        controlled action retains stdout before unittest cleans up the fixture.
        A diagnostic failure cannot turn the original assertion into success.
        """
        from worldline.raw_observation import exception_observation
        try:
            getattr(self, method_name)()
        except AssertionError as assertion:
            try:
                frames = []
                traceback = assertion.__traceback__
                while traceback is not None:
                    frame = traceback.tb_frame
                    if frame.f_code.co_name == method_name:
                        caught = frame.f_locals.get('caught')
                        error = None if caught is None else getattr(caught, 'exception', None)
                        pending = [] if error is None else [error]
                        seen = set()
                        errors = []
                        for item in pending:
                            if id(item) in seen:
                                continue
                            seen.add(id(item))
                            errors.append({
                                'module': type(item).__module__,
                                'graph': exception_observation(item),
                                'retentionFailed': retention_failed(item),
                                'attributes': {
                                    name: {'present': hasattr(item, name),
                                           'value': getattr(item, name, None)}
                                    for name in ('code', 'details', '_worldline_retention_failed',
                                                 'kernel_role_observations',
                                                 'examiner_entry_observation',
                                                 'examiner_loader_observations',
                                                 'examiner_native_observations')},
                            })
                            for name in ('__cause__', '__context__'):
                                linked = getattr(item, name, None)
                                if linked is not None and id(linked) not in seen:
                                    pending.append(linked)
                        frames.append({'caughtExceptionPresent': error is not None,
                                       'exceptions': errors,
                                       'observerRecordsPresent': 'retained' in frame.f_locals,
                                       'observerRecords': frame.f_locals.get('retained')})
                    traceback = traceback.tb_next
                print('WORLDLINE_RETENTION_DIAGNOSTIC ' + json.dumps({
                    'method': method_name, 'assertion': exception_observation(assertion),
                    'frames': frames,
                }, ensure_ascii=True, allow_nan=False, separators=(',', ':')), flush=True)
            except BaseException as diagnostic_error:
                # Keep the original failure even if diagnostic serialization or
                # retention fails. Such an attempt supplies no complete receipt.
                try:
                    print('WORLDLINE_RETENTION_DIAGNOSTIC_REFUSED ' +
                          type(diagnostic_error).__qualname__ + ': ' + str(diagnostic_error),
                          flush=True)
                except BaseException:
                    pass
            raise

    def test_diagnostic_native_source_retention_failure(self):
        self._run_retention_diagnostic(
            'test_native_retention_failure_prevents_entry_and_retains_the_full_read')

    def test_diagnostic_native_terminal_retention_failure(self):
        self._run_retention_diagnostic(
            'test_native_terminal_retention_failure_stays_failed_with_raw_record_and_cleanup')

    def test_long_runtime_path_retains_native_budget_and_reaches_actual_terminal(self):
        from worldline.trusted import TRUSTED_INTERPRETER
        (self.verifier / 'exam.py').write_text(
            'from pathlib import Path\n'
            'Path("/run/worldline-report/report").write_text("long runtime completed")\n')
        report = self.base / 'long-path-report'
        report.mkdir(mode=0o700)
        runtime = self.base / ('ordinary-runtime-' * 10)
        spec = evaluator.PrivateEvaluationSpec(
            str(uuid.uuid4()), {'/logical/private-check': self.source}, self.verifier,
            (TRUSTED_INTERPRETER, evaluator.VERIFIER_MOUNT + '/exam.py'), '/logical/private-check',
            report, runtime, timeout_seconds=60)
        retained = []
        def observe(kind, occurrence, value):
            if kind == 'private-kernel-role-observation':
                retained.append(value)
        original_cwd = os.getcwd()
        result = evaluator.PrivateEvaluator(self.adapter).run(spec,
            resource_properties=('MemoryMax=1G', 'TasksMax=64', 'CPUQuota=100%', 'IOAccounting=yes'),
            _acquisition_observer=observe)
        self.assertEqual(result['exitCode'], 0, result['stdout'] + result['stderr'])
        self.assertEqual((report / 'report').read_text(), 'long runtime completed')
        self.assertEqual(os.getcwd(), original_cwd)
        records = result['boundary']['daemonRoleObservations']
        budget = next(row for row in records if row['kind'] == 'native-lifetime-budget')
        terminal = next(row for row in records if row['kind'] == 'native-lifetime-terminal')
        outcome = next(row for row in records if row['kind'] == 'native-lifetime-process-outcome')
        self.assertIn(budget, retained)
        self.assertIn(terminal, retained)
        self.assertTrue(terminal['trueEof'] and terminal['terminal']['cleanReportedTerminal'])
        self.assertEqual(outcome['nativeTerminal']['recordId'], terminal['recordId'])
        self.assertEqual(outcome['fixedBootstrapExaminerWait'], 0)
        self.assertEqual(outcome['actualBootstrapWait'], 0)
        self.assertTrue(outcome['observerServicesJoined'] and outcome['cleanReportedProcess'])
        self.assertEqual((self.source / 'source.txt').read_text(), 'ordinary source\n')

    def test_native_lifetime_joins_late_acquisition_terminal_and_actual_process_wait(self):
        from worldline.linux import native_lifetime as wire
        from worldline.trusted import TRUSTED_INTERPRETER
        late_source = (b'from pathlib import Path\n'
                       b'Path("/run/worldline-report/finalized").write_text("late owned code")\n')
        (self.verifier / 'final.py').write_bytes(late_source)
        (self.verifier / 'exam.py').write_text(
            'import atexit\nimport _worldline_examiner_guard as guard\n'
            'def finalizer():\n'
            '    guard.frozen_metadata("__hello__")\n'
            '    exec(guard.compile_source("/run/worldline-verifiers/final.py"), {})\n'
            'atexit.register(finalizer)\n')
        report = self.base / 'lifetime-report'
        report.mkdir(mode=0o700)
        spec = evaluator.PrivateEvaluationSpec(
            str(uuid.uuid4()), {'/logical/private-check': self.source}, self.verifier,
            (TRUSTED_INTERPRETER, evaluator.VERIFIER_MOUNT + '/exam.py'), '/logical/private-check',
            report, self.base / 'lifetime-run', timeout_seconds=60)
        result = evaluator.PrivateEvaluator(self.adapter).run(spec,
            resource_properties=('MemoryMax=1G', 'TasksMax=64', 'CPUQuota=100%', 'IOAccounting=yes'))
        self.assertEqual(result['exitCode'], 0, result['stdout'] + result['stderr'])
        self.assertEqual((report / 'finalized').read_text(), 'late owned code')
        records = result['boundary']['daemonRoleObservations']
        startup = next(row for row in records if row['kind'] == 'role-startup'
                       and row['roleClaim'] == 'examiner')
        budget = next(row for row in records if row['kind'] == 'native-lifetime-budget')
        opened = next(row for row in records if row['kind'] == 'native-lifetime-open')
        self.assertEqual(opened['startupRecordId'], startup['recordId'])
        self.assertEqual(opened['identity'], startup['identity'])
        self.assertEqual(opened['nativeGuard'], result['boundary']['daemonExaminerNativeObservations'][0]['binding'])
        packets = [row for row in records if row['kind'] in ('native-lifetime-receive', 'native-lifetime-terminal')]
        self.assertEqual([row['sequence'] for row in packets], list(range(len(packets))))
        decoded = []
        for row in packets:
            obj, = row['transferObjects']
            self.assertEqual(obj['name'], 'native-record')
            self.assertTrue(obj['eof'] and obj['returned'])
            self.assertEqual(obj['before'], obj['after'])
            self.assertEqual(obj['sealsBefore'], obj['sealsAfter'])
            self.assertTrue(row['transferDescriptorsClosed'])
            self.assertTrue(all(item['closed'] for item in row['descriptorCloses']))
            decoded.append(wire.decode_record(base64.b64decode(obj['bytes']['payload'])))
            ack = wire.ACK.unpack(base64.b64decode(row['acknowledgementBytes']['payload']))
            self.assertEqual(ack[3], budget['actualRoleDeadlineClaim'])
            self.assertTrue(any(item['kind'] == 'native-lifetime-acknowledgement'
                                and item['retainedRecordId'] == row['recordId'] and item['sent']
                                for item in records))
        context = decoded[0][1]
        self.assertEqual(context[0], spec.run_id)
        self.assertEqual(context[1], startup['recordId'])
        self.assertEqual(context[-1], budget['actualRoleDeadlineClaim'])
        late = [(row, value) for row, value in zip(packets, decoded)
                if row['eventKind'] == wire.ATTEMPT and value[0] == 'source-compile'
                and value[5] == evaluator.VERIFIER_MOUNT + '/final.py']
        self.assertTrue(late)
        self.assertTrue(all(value[1] == 3 and value[6] == late_source for _, value in late))
        terminal = packets[-1]
        self.assertEqual(terminal['kind'], 'native-lifetime-terminal')
        self.assertTrue(terminal['trueEof'])
        self.assertTrue(terminal['terminal']['cleanReportedTerminal'])
        outcome = next(row for row in records if row['kind'] == 'native-lifetime-process-outcome')
        self.assertEqual(outcome['nativeTerminal']['recordId'], terminal['recordId'])
        self.assertEqual(outcome['fixedBootstrapExaminerWait'], 0)
        self.assertEqual(outcome['actualBootstrapWait'], 0)
        self.assertTrue(outcome['observerServicesJoined'] and outcome['cleanReportedProcess'])
        self.assertFalse(outcome['protectedCustody'])
        self.assertFalse(outcome['nativeTerminal']['primaryWorkloadFailurePreservationEstablished'])
        self.assertEqual((self.source / 'source.txt').read_text(), 'ordinary source\n')

    def test_native_terminal_retention_failure_stays_failed_with_raw_record_and_cleanup(self):
        from worldline.trusted import TRUSTED_INTERPRETER
        (self.verifier / 'exam.py').write_text('pass\n')
        report = self.base / 'lifetime-refusal-report'
        report.mkdir(mode=0o700)
        spec = evaluator.PrivateEvaluationSpec(
            str(uuid.uuid4()), {'/logical/private-check': self.source}, self.verifier,
            (TRUSTED_INTERPRETER, evaluator.VERIFIER_MOUNT + '/exam.py'), '/logical/private-check',
            report, self.base / 'lifetime-refusal-run', timeout_seconds=60)
        retained = []
        def observe(kind, occurrence, value):
            if kind == 'private-kernel-role-observation':
                retained.append(value)
                if value['kind'] == 'native-lifetime-terminal':
                    raise OSError('controlled native terminal-retention failure')
        with self.assertRaises(Exception) as caught:
            evaluator.PrivateEvaluator(self.adapter).run(spec,
                resource_properties=('MemoryMax=1G', 'TasksMax=64', 'CPUQuota=100%', 'IOAccounting=yes'),
                _acquisition_observer=observe)
        self.assertTrue(retention_failed(caught.exception))
        terminal = next(row for row in retained if row['kind'] == 'native-lifetime-terminal')
        self.assertTrue(terminal['trueEof'] and terminal['transferDescriptorsClosed'])
        self.assertIsNotNone(terminal['transferObjects'][0]['bytes'])
        self.assertFalse(any(row['kind'] == 'native-lifetime-acknowledgement'
                             and row['retainedRecordId'] == terminal['recordId'] for row in retained))
        cleanups = [row for row in retained if row['kind'] == 'native-lifetime-held-descriptor-cleanup']
        self.assertTrue(cleanups)
        self.assertTrue(all(item['closed'] for row in cleanups for item in row['descriptorCloses']))
        self.assertEqual((self.source / 'source.txt').read_text(), 'ordinary source\n')

    def test_actual_native_alias_and_package_metadata_match_installed_importer(self):
        import importlib.machinery
        import importlib.util
        from worldline.trusted import TRUSTED_INTERPRETER
        names = ('__hello_alias__', '__phello_alias__', '__phello_alias__.spam',
                 '__phello__', '__phello__.__init__', '__phello__.ham',
                 '__phello__.ham.__init__', '__phello__.ham.eggs', '__hello_only__')
        expected = {}
        for name in names:
            spec = importlib.machinery.FrozenImporter.find_spec(name)
            module = importlib.util.module_from_spec(spec)
            expected[name] = {'name': module.__name__, 'package': module.__package__,
                              'file': getattr(module, '__file__', None),
                              'path': getattr(module, '__path__', None),
                              'origin': spec.origin, 'hasLocation': spec.has_location,
                              'state': vars(spec.loader_state)}
        (self.verifier / 'exam.py').write_text('\n'.join([
            'from pathlib import Path', 'import json, importlib',
            'import _worldline_examiner_guard as guard',
            'names = ' + repr(names), 'actual = {}', 'owned = {}',
            'for name in names:',
            '    module = importlib.import_module(name)',
            '    spec = module.__spec__',
            '    actual[name] = {"name": module.__name__, "package": module.__package__,',
            '                    "file": getattr(module, "__file__", None),',
            '                    "path": getattr(module, "__path__", None),',
            '                    "origin": spec.origin, "hasLocation": spec.has_location,',
            '                    "state": vars(spec.loader_state)}',
            '    code = spec.loader.get_code(name)',
            '    owned[name] = guard.contains(code)',
            'Path("/run/worldline-report/report").write_text(json.dumps({',
            '    "actual": actual, "owned": owned, "state": guard.status(),',
            '    "observations": guard.frozen_metadata_observations()}))', '']))
        report = self.base / 'alias-report'
        report.mkdir(mode=0o700)
        spec = evaluator.PrivateEvaluationSpec(
            str(uuid.uuid4()), {'/logical/private-check': self.source}, self.verifier,
            (TRUSTED_INTERPRETER, evaluator.VERIFIER_MOUNT + '/exam.py'), '/logical/private-check',
            report, self.base / 'alias-run', timeout_seconds=60)
        result = evaluator.PrivateEvaluator(self.adapter).run(spec,
            resource_properties=('MemoryMax=1G', 'TasksMax=64', 'CPUQuota=100%', 'IOAccounting=yes'))
        self.assertEqual(result['exitCode'], 0, result['stdout'] + result['stderr'])
        actual = json.loads((report / 'report').read_text())
        self.assertEqual(actual['actual'], expected)
        self.assertEqual(set(actual['owned']), set(names))
        self.assertTrue(all(actual['owned'].values()))
        self.assertTrue(actual['state']['frozenMetadata']['providerCaptured'])
        self.assertFalse(actual['state']['violated'])
        self.assertFalse(actual['state']['confinementEstablished'])
        returned = {row['name'] for row in actual['observations'] if row['outcome'] == 'returned'}
        self.assertTrue(set(names).issubset(returned))
        self.assertEqual((self.source / 'source.txt').read_text(), 'ordinary source\n')

    def test_actual_native_kernel_filter_preserves_threads_reads_and_retained_subject(self):
        from worldline.trusted import TRUSTED_INTERPRETER
        (self.verifier / 'exam.py').write_text(
            'from pathlib import Path\nimport json, threading\n'
            'import _worldline_examiner_guard as guard\n'
            'rows = []\n'
            'def worker():\n rows.append(Path("source.txt").read_text())\n'
            'thread = threading.Thread(target=worker)\nthread.start()\nthread.join()\n'
            'Path("/run/worldline-report/report").write_text(json.dumps({"rows": rows, "state": guard.status()}))\n')
        report = self.base / 'filter-report'
        report.mkdir(mode=0o700)
        spec = evaluator.PrivateEvaluationSpec(
            str(uuid.uuid4()), {'/logical/private-check': self.source}, self.verifier,
            (TRUSTED_INTERPRETER, evaluator.VERIFIER_MOUNT + '/exam.py'), '/logical/private-check',
            report, self.base / 'filter-run', timeout_seconds=60)
        result = evaluator.PrivateEvaluator(self.adapter).run(spec,
            resource_properties=('MemoryMax=1G', 'TasksMax=64', 'CPUQuota=100%', 'IOAccounting=yes'))
        self.assertEqual(result['exitCode'], 0, result['stdout'] + result['stderr'])
        actual = json.loads((report / 'report').read_text())
        self.assertEqual(actual['rows'], ['ordinary source\n'])
        self.assertTrue(actual['state']['syscallPolicy']['installed'])
        self.assertEqual(actual['state']['phase'], 'active')
        self.assertFalse(actual['state']['confinementEstablished'])
        records = result['boundary']['daemonRoleObservations']
        startup = next(row for row in records if row['kind'] == 'role-startup'
                       and row['roleClaim'] == 'examiner')
        sample = startup['nativeKernelFilter']
        self.assertEqual(sample['NoNewPrivs'], '1')
        self.assertEqual(sample['Seccomp'], '2')
        self.assertRegex(sample['Seccomp_filters'], r'^[1-9][0-9]*$')
        self.assertEqual(sample['scope'], 'held-proc-status-sample-only')
        self.assertFalse(sample['independentKernelProgramObservation'])
        self.assertTrue(startup['nativeArtifactMapping']['mappings'])
        opened = next(row for row in records if row['kind'] == 'native-preparation-open')
        self.assertEqual(opened['startupRecordId'], startup['recordId'])
        self.assertEqual(opened['identity'], startup['identity'])
        self.assertEqual(opened['nativeKernelFilter'], sample)
        terminal = next(row for row in records if row['kind'] == 'native-preparation-terminal')
        self.assertEqual(terminal['request']['nativeStatus']['syscallPolicy'],
                         actual['state']['syscallPolicy'])
        self.assertTrue(terminal['trueEof'])
        self.assertFalse(terminal['failed'])
        self.assertEqual((self.source / 'source.txt').read_text(), 'ordinary source\n')

    def test_native_live_role_retains_full_preparation_and_active_actual_code(self):
        from worldline.trusted import TRUSTED_INTERPRETER
        (self.verifier / 'exam.py').write_text(
            'from pathlib import Path\nimport json, __hello__\n'
            'import _worldline_examiner_guard as guard\n'
            'def original_entry():\n return "actual code"\n'
            'state = guard.status()\n'
            'assert state["phase"] == "active" and not state["violated"]\n'
            'assert guard.contains(original_entry.__code__)\n'
            'assert guard.contains(__hello__.main.__code__)\n'
            'Path("/run/worldline-report/report").write_text(json.dumps(state))\n')
        report = self.base / 'native-report'
        report.mkdir(mode=0o700)
        spec = evaluator.PrivateEvaluationSpec(
            str(uuid.uuid4()), {'/logical/private-check': self.source}, self.verifier,
            (TRUSTED_INTERPRETER, evaluator.VERIFIER_MOUNT + '/exam.py'), '/logical/private-check',
            report, self.base / 'native-run', timeout_seconds=60)
        result = evaluator.PrivateEvaluator(self.adapter).run(spec,
            resource_properties=('MemoryMax=1G', 'TasksMax=64', 'CPUQuota=100%', 'IOAccounting=yes'))
        self.assertEqual(result['exitCode'], 0, result['stdout'] + result['stderr'])
        state = json.loads((report / 'report').read_text())
        self.assertTrue(state['preinitializationInstalled'])
        self.assertEqual(state['phase'], 'active')
        self.assertFalse(state['confinementEstablished'])
        records = result['boundary']['daemonRoleObservations']
        role = next(row for row in records if row['kind'] == 'role-startup' and row['roleClaim'] == 'examiner')
        native = result['boundary']['daemonExaminerNativeObservations'][0]
        self.assertEqual(role['nativeArtifactMapping']['binding'], native['binding'])
        self.assertTrue(any('x' in row['permissions'] for row in role['nativeArtifactMapping']['mappings']))
        reads = [row for row in records if row['kind'] == 'native-preparation-receive']
        self.assertTrue(reads)
        self.assertEqual([row['sequence'] for row in reads], list(range(len(reads))))
        for row in reads:
            self.assertTrue(row['transferDescriptorsClosed'])
            self.assertTrue(row['helperRead']['readReturned'])
            self.assertIsNotNone(row['helperRead']['bytes'])
            self.assertTrue(all(item['closed'] for item in row['descriptorCloses']))
        terminal = next(row for row in records if row['kind'] == 'native-preparation-terminal')
        self.assertTrue(terminal['trueEof'])
        self.assertFalse(terminal['failed'])
        entry = next(row for row in records if row['kind'] == 'examiner-entry-preparation-receive')
        self.assertEqual(entry['nativePreparation']['recordId'], terminal['recordId'])
        self.assertEqual(set(entry['helperReport']), {
            'schemaVersion', 'kind', 'runId', 'producer', 'binding', 'read', 'compile', 'exception'})
        self.assertEqual((self.source / 'source.txt').read_text(), 'ordinary source\n')

    def test_native_retention_failure_prevents_entry_and_retains_the_full_read(self):
        from worldline.trusted import TRUSTED_INTERPRETER
        (self.verifier / 'exam.py').write_text(
            'from pathlib import Path\n'
            'Path("/run/worldline-report/report").write_text("entry must not execute")\n')
        report = self.base / 'native-refusal-report'
        report.mkdir(mode=0o700)
        spec = evaluator.PrivateEvaluationSpec(
            str(uuid.uuid4()), {'/logical/private-check': self.source}, self.verifier,
            (TRUSTED_INTERPRETER, evaluator.VERIFIER_MOUNT + '/exam.py'), '/logical/private-check',
            report, self.base / 'native-refusal-run', timeout_seconds=60)
        retained = []
        def observe(kind, occurrence, value):
            if kind == 'private-kernel-role-observation' and value['kind'] == 'native-preparation-receive':
                retained.append(value)
                raise OSError('controlled native source-retention failure')
        with self.assertRaises(Exception) as caught:
            evaluator.PrivateEvaluator(self.adapter).run(spec,
                resource_properties=('MemoryMax=1G', 'TasksMax=64', 'CPUQuota=100%', 'IOAccounting=yes'),
                _acquisition_observer=observe)
        self.assertTrue(retention_failed(caught.exception))
        self.assertFalse((report / 'report').exists())
        self.assertTrue(retained)
        self.assertIsNotNone(retained[0]['helperRead']['bytes'])
        self.assertTrue(retained[0]['transferDescriptorsClosed'])

    def test_later_backend_failure_keeps_all_loader_records_in_public_error_details(self):
        from worldline.errors import WorldlineError
        from worldline.trusted import TRUSTED_INTERPRETER
        (self.verifier / 'exam.py').write_text('pass\n')
        report = self.base / 'failure-report'
        report.mkdir(mode=0o700)
        spec = evaluator.PrivateEvaluationSpec(
            str(uuid.uuid4()), {'/logical/private-check': self.source}, self.verifier,
            (TRUSTED_INTERPRETER, evaluator.VERIFIER_MOUNT + '/exam.py'), '/logical/private-check',
            report, self.base / 'failure-run', timeout_seconds=60)
        original = OSError('controlled later launch preparation failure')
        with patch('worldline.linux.kernel_role_observer.KernelRoleObserver', side_effect=original), \
                self.assertRaises(WorldlineError) as caught:
            evaluator.PrivateEvaluator(self.adapter).run(spec)
        self.assertIs(caught.exception.__cause__, original)
        self.assertIn('examinerEntrySource', caught.exception.details)
        records = caught.exception.details['examinerLoaderObservations']
        self.assertIs(records, original.examiner_loader_observations)
        self.assertTrue(any(row['kind'] == 'loader-file' for row in records))
        self.assertEqual(records[-2]['kind'], 'examiner-loader-support')
        self.assertTrue(records[-2]['closeReturned'])
        self.assertEqual(records[-1]['kind'], 'examiner-loader-policy')
        self.assertTrue(records[-1]['readback']['readReturned'])

    def test_original_backend_runs_pinned_helpers_generators_and_direct_reads(self):
        from worldline.trusted import TRUSTED_INTERPRETER
        package = self.verifier / 'helpers'
        package.mkdir()
        (package / '__init__.py').write_text('from .values import value\n')
        (package / 'values.py').write_text('value = "ordinary source\\n"\n')
        (self.verifier / 'exam.py').write_text(
            'from pathlib import Path\nfrom collections import namedtuple\n'
            'from dataclasses import dataclass\nfrom typing import NamedTuple\n'
            'import xml.sax.saxutils, tempfile\nfrom helpers import value\n'
            'Point = namedtuple("Point", "text")\n'
            '@dataclass\nclass Box:\n text: str\n'
            'class Typed(NamedTuple):\n text: str\n'
            'assert Point(value).text == Box(value).text == Typed(value).text\n'
            'assert Path("source.txt").read_text() == value\n'
            'Path("/run/worldline-report/report").write_text("bound helpers completed")\n')
        report = self.base / 'loader-report'
        report.mkdir(mode=0o700)
        spec = evaluator.PrivateEvaluationSpec(
            str(uuid.uuid4()), {'/logical/private-check': self.source}, self.verifier,
            (TRUSTED_INTERPRETER, evaluator.VERIFIER_MOUNT + '/exam.py'), '/logical/private-check',
            report, self.base / 'loader-run', timeout_seconds=60)
        result = evaluator.PrivateEvaluator(self.adapter).run(spec,
            resource_properties=('MemoryMax=1G', 'TasksMax=64', 'CPUQuota=100%', 'IOAccounting=yes'))
        self.assertEqual(result['exitCode'], 0, result['stdout'] + result['stderr'])
        self.assertEqual((report / 'report').read_text(), 'bound helpers completed')
        self.assertEqual((self.source / 'source.txt').read_text(), 'ordinary source\n')
        records = result['boundary']['daemonExaminerLoaderObservations']
        policy = next(row for row in records if row['kind'] == 'examiner-loader-policy')
        self.assertTrue(policy['writeReturned'])
        self.assertTrue(policy['readback']['readReturned'])
        roles = [row for row in result['boundary']['daemonRoleObservations']
                 if row['kind'] == 'role-startup' and row['roleClaim'] == 'examiner']
        self.assertEqual(len(roles), 1)
        self.assertEqual(roles[0]['examinerLoaderBinding'], policy['binding'])
        self.assertFalse(roles[0]['confinementEstablished'])
        self.assertFalse(result['examinerAudit']['before']['clean'])


if __name__ == '__main__':
    unittest.main()
