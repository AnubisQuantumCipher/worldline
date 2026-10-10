"""Additive SIMULATIONS of actual donor methods; no native library is loaded.

Not kernel/ELF/custody evidence. Run only after separate source/frame admission.
Actual production class bodies are extracted unchanged from the selected source
tree, avoiding unrelated module import side effects. Fixtures supply their OS,
loader, layout records and authority dependencies. Full real-library controls
remain mandatory. A passing simulation is not proof or production acceptance.
"""
from __future__ import annotations

import ast
import ctypes
import dataclasses
import hashlib
import hmac
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

RUNTIME = Path(__file__).resolve().parents[1] / 'runtime/worldline'
TYPED = ('cosmogony_use_reservation_version_v1',
         'cosmogony_use_reservation_layout_v1',
         'cosmogony_use_reservation_decide_v1')
SIZES = ('cosmogony_revocation_lineage_bytes', 'cosmogony_revocation_link_bytes',
         'cosmogony_universe_record_bytes')
BOUND = TYPED + SIZES + ('cosmogony_revocation_check',)


def actual_classes(path, names, namespace):
    tree = ast.parse(path.read_text(), filename=str(path))
    classes = [node for node in tree.body
               if isinstance(node, ast.ClassDef) and node.name in names]
    if {node.name for node in classes} != set(names):
        raise AssertionError('actual production class roster changed')
    selected = ast.Module(body=classes, type_ignores=[])
    # Execute exact class bodies, never an alternative test implementation.
    exec(compile(selected, str(path), 'exec', dont_inherit=True), namespace)


class SimulatedRefusal(Exception):
    pass


class FakeRecord(ctypes.Structure):
    _fields_ = [('field', ctypes.c_int)]


class Symbol:
    def __init__(self, name, trace, address):
        self.name, self.trace, self.address = name, trace, address

    def __call__(self, *args):
        self.trace.append(('query', self.name))
        if self.name == TYPED[0]:
            return 1
        if self.name == TYPED[1]:
            if args[1] == 0:
                return ctypes.sizeof(FakeRecord)
            if args[1] == 1:
                return ctypes.alignment(FakeRecord)
            return FakeRecord.field.offset
        if self.name in SIZES:
            return ctypes.sizeof(FakeRecord)
        raise AssertionError('simulation must never call a decision or revocation export')


class Native:
    def __init__(self, trace, *, missing=None, wrong=None, lookup_error=None):
        self.trace, self.missing, self.lookup_error = trace, missing, lookup_error
        self.symbols = {name: Symbol(name, trace, 0x3000 if name == wrong else 0x1001)
                        for name in BOUND}

    def __getattr__(self, name):
        self.trace.append(('lookup', name))
        if self.lookup_error is not None and name == TYPED[0]:
            raise self.lookup_error
        if name == self.missing or name not in self.symbols:
            raise AttributeError(name)
        return self.symbols[name]


class NativeBindingSimulations(unittest.TestCase):
    def setup_fixture(self, *, missing=None, wrong=None, maps=True, lookup_error=None):
        temp = tempfile.TemporaryDirectory(prefix='worldline-native-binding-simulation-')
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        library = root / 'install/universe_source/lib/libcosmogony_core.so'
        library.parent.mkdir(parents=True)
        library.write_bytes(b'SIMULATED LIBRARY BYTES: NOT ELF')
        build = root / 'build.json'
        build.write_bytes(b'SIMULATED BUILD RECORD')
        trace = []
        native = Native(trace, missing=missing, wrong=wrong, lookup_error=lookup_error)

        class Gate:
            pass
        class Capture:
            pass
        class Issuer:
            pass
        class Lease:
            def open_journal(self, gate, name, path, envelope):
                trace.append(('lease', name))
                path.write_text(json.dumps(envelope))

        issuer = Issuer()
        issuer.key, issuer.state = b'SIMULATED KEY', root
        gate, capture, lease = Gate(), Capture(), Lease()
        gate.root, gate.issuer, capture.startup_lease = root, issuer, lease
        config = {'schema': 'cosmogony.protected-use-reservation-bind-v1',
                  'library': str(library),
                  'library_sha256': hashlib.sha256(library.read_bytes()).hexdigest(),
                  'source_root': str(root), 'source_inventory': 'SIMULATED',
                  'build': str(build)}

        class Maps:
            def read_text(self):
                trace.append(('maps', 'observed'))
                return ('1000-2000 r-xp 00000000 00:00 1 ' + str(library) + '\n') if maps else ''

        def path(value):
            return Maps() if str(value) == '/proc/self/maps' else Path(value)

        def private_bytes(value):
            if str(value).endswith('use-reservation-bind.json'):
                return json.dumps(config).encode()
            return Path(value).read_bytes()

        def require(condition, code):
            if not condition:
                raise SimulatedRefusal(code)

        def cast(symbol, _ctype):
            trace.append(('cast', symbol.name))
            return types.SimpleNamespace(value=symbol.address)

        fake_c = types.SimpleNamespace(**{name: getattr(ctypes, name) for name in
            ('c_void_p', 'c_size_t', 'c_int32', 'c_uint32', 'c_long', 'sizeof', 'alignment')})
        fake_c.cast = cast
        fake_c.CDLL = lambda _path: (trace.append(('loader', 'simulated')), native)[1]
        fake_os = types.SimpleNamespace(**{name: getattr(os, name) for name in
            ('fstat', 'fdopen', 'dup', 'close', 'fsencode', 'O_RDONLY', 'O_CLOEXEC')})
        fake_os.geteuid = lambda: 0
        fake_os.path = os.path
        fake_os.open = lambda _path, flags: os.open(library, flags)

        ns = {'__name__': 'worldline_binding_simulation', '__package__': 'worldline_binding_simulation',
              'C': fake_c, 'Path': path, 'os': fake_os, 'hashlib': hashlib, 'hmac': hmac,
              'Gate': Gate, 'ProtectedCapture': Capture, 'ProtectedIssuer': Issuer,
              'require': require, 'refuse': lambda code: require(False, code),
              'protected': lambda *args, **kwargs: None, 'private_bytes': private_bytes,
              'exact_json': json.loads, 'canonical': lambda value: json.dumps(value).encode(),
              '_DOMAIN': b'SIMULATED DOMAIN',
              'dataclass': dataclasses.dataclass, 'field': dataclasses.field, 'Any': object}
        # Dataclass processing expects a module entry for its actual class.
        module = types.ModuleType(ns['__name__'])
        modules_patch = patch.dict(sys.modules, {ns['__name__']: module,
            ns['__name__'] + '.protected_startup': types.SimpleNamespace(StartupLease=Lease)})
        modules_patch.start()
        self.addCleanup(modules_patch.stop)
        actual_classes(RUNTIME / 'errors.py', {'WorldlineError', 'CoreUnavailable'}, ns)
        for name in ('Binding', 'Row', 'Input', 'Result'):
            ns[name] = FakeRecord
        ns['capabilities'] = types.SimpleNamespace(**{name: FakeRecord for name in
            ('Capability', 'CheckInput', 'Scope', 'Ceiling', 'Usage', 'Actions')})
        ns['revocation'] = types.SimpleNamespace(Lineage=FakeRecord, Link=FakeRecord)
        ns['universes'] = types.SimpleNamespace(Record=FakeRecord, Policy=FakeRecord)
        ns['genesis'] = types.SimpleNamespace(Universe=FakeRecord, Request=FakeRecord,
                                             Agent=FakeRecord, Digest=FakeRecord)
        actual_classes(RUNTIME / 'capability_use_kernel.py', {'UseReservationKernel'}, ns)
        actual_classes(RUNTIME / 'protected_capability_uses.py', {'ProtectedUseReservations'}, ns)
        owner = ns['ProtectedUseReservations']
        # Explicit exclusions: installation, locks, journal/replay and custody.
        owner._lock_intact = lambda self: None
        owner._source_intact = lambda self: None
        owner._load = lambda self: trace.append(('journal', 'simulated'))
        return ns, trace, lambda: owner(gate, capture, startup_lease=lease)

    def test_complete_simulated_mapping_precedes_actual_adapter_queries(self):
        _ns, trace, construct = self.setup_fixture()
        construct()
        first_query = next(i for i, event in enumerate(trace) if event[0] == 'query')
        for name in BOUND:
            self.assertIn(('cast', name), trace[:first_query])
        self.assertIn(('query', TYPED[0]), trace)
        self.assertIn(('query', TYPED[1]), trace)
        for name in SIZES:
            self.assertIn(('query', name), trace)

    def test_missing_original_api_retains_typed_error_and_cause_without_queries(self):
        for name in TYPED:
            with self.subTest(symbol=name):
                ns, trace, construct = self.setup_fixture(missing=name)
                with self.assertRaises(ns['CoreUnavailable']) as caught:
                    construct()
                self.assertEqual(caught.exception.code, 'CORE_UNAVAILABLE')
                self.assertEqual(caught.exception.message, 'native capability-use reservation unavailable')
                self.assertIsInstance(caught.exception.__cause__, AttributeError)
                self.assertFalse(any(event[0] == 'query' for event in trace))

    def test_missing_dependency_size_retains_attribute_error(self):
        for name in SIZES:
            with self.subTest(symbol=name):
                _ns, trace, construct = self.setup_fixture(missing=name)
                with self.assertRaises(AttributeError):
                    construct()
                self.assertFalse(any(event[0] == 'query' for event in trace))

    def test_each_wrong_mapped_symbol_refuses_before_queries(self):
        for name in BOUND:
            with self.subTest(symbol=name):
                _ns, trace, construct = self.setup_fixture(wrong=name)
                with self.assertRaisesRegex(SimulatedRefusal, 'CAPABILITY_USE_NATIVE_SYMBOL_MAPPING_DIFFERS'):
                    construct()
                self.assertFalse(any(event[0] == 'query' for event in trace))

    def test_missing_mapping_refuses_before_queries(self):
        _ns, trace, construct = self.setup_fixture(maps=False)
        with self.assertRaisesRegex(SimulatedRefusal, 'CAPABILITY_USE_NATIVE_MAPPING_ABSENT'):
            construct()
        self.assertFalse(any(event[0] == 'query' for event in trace))

    def test_unrelated_lookup_error_is_not_translated(self):
        error = RuntimeError('SIMULATED unrelated resolver error')
        _ns, trace, construct = self.setup_fixture(lookup_error=error)
        with self.assertRaises(RuntimeError) as caught:
            construct()
        self.assertIs(caught.exception, error)
        self.assertFalse(any(event[0] == 'query' for event in trace))


if __name__ == '__main__':
    unittest.main()
