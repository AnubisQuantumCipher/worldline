"""Additive real-interpreter controls; a supplied native build is mandatory.

Run only through the existing reviewed Root control route. These are native
dependency controls, not WORLDLINE world actors or complete confinement tests.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import textwrap
import unittest


ARTIFACT = (Path(__file__).resolve().parents[2] / 'native-artifacts' /
            'libworldline_examiner_guard.so')
BOOTSTRAP = '''\
from __future__ import annotations
import json, sys, types, threading, gc, marshal, encodings.latin_1, unicodedata
import _worldline_examiner_guard as guard
def emit(value):
    print(json.dumps(value, sort_keys=True), flush=True)
def configured(source=b'value = "retained"\\n'):
    guard.configure('native-component-control', (('/verifier/entry.py', source),))
def prepared(source=b'value = "retained"\\n'):
    configured(source)
    code = guard.compile_source('/verifier/entry.py')
    guard.activate()
    return code
'''


class NativeGuardControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Deliberately fail, never skip, if the required build is missing.
        cls.artifact_bytes = ARTIFACT.read_bytes()
        cls.artifact_hash = hashlib.sha256(cls.artifact_bytes).hexdigest()
        receipt = json.loads((ARTIFACT.parent / 'build.json').read_text())
        if receipt['sha256'] != cls.artifact_hash or receipt['artifact'] != str(ARTIFACT):
            raise AssertionError('native artifact differs from its build receipt')

    def child(self, body, *, preload=True):
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), self.artifact_hash)
        environment = {key: value for key, value in os.environ.items()
                       if not key.startswith(('LD_', 'PYTHON'))}
        argv = ['/usr/bin/python3', '-I', '-S', '-c', BOOTSTRAP + textwrap.dedent(body)]
        if preload:
            argv = ['/usr/bin/env', 'LD_PRELOAD=' + str(ARTIFACT), *argv]
        result = subprocess.run(argv, env=environment, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, timeout=30, check=False)
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), self.artifact_hash)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors='replace'))
        self.assertEqual(result.stderr, b'')
        return json.loads(result.stdout)

    def test_constructor_installed_before_runtime_and_no_confinement_claim(self):
        result = self.child('emit(guard.status())')
        self.assertTrue(result['preinitializationInstalled'])
        self.assertEqual(result['phase'], 'bootstrap')
        self.assertGreater(result['bootstrapEvents'], 0)
        self.assertFalse(result['violated'])
        self.assertFalse(result['confinementEstablished'])

    def test_exact_owned_source_executes_after_activation(self):
        result = self.child(r'''
            code = prepared()
            namespace = {}
            exec(code, namespace)
            emit({'value': namespace['value'], 'code': guard.contains(code), 'state': guard.status()})
        ''')
        self.assertEqual(result['value'], 'retained')
        self.assertTrue(result['code'])
        self.assertFalse(result['state']['violated'])

    def test_nested_code_is_strongly_retained_and_callable(self):
        result = self.child(r'''
            code = prepared(b'def outer():\n    def inner():\n        return "nested"\n    return inner\n')
            namespace = {}
            exec(code, namespace)
            outer = namespace['outer']
            inner = outer()
            del code
            gc.collect()
            emit({'outer': guard.contains(outer.__code__), 'inner': guard.contains(inner.__code__),
                  'value': inner(), 'state': guard.status()})
        ''')
        self.assertTrue(result['outer'])
        self.assertTrue(result['inner'])
        self.assertEqual(result['value'], 'nested')
        self.assertFalse(result['state']['violated'])

    def test_identity_does_not_admit_a_distinct_equal_code_object(self):
        result = self.child(r'''
            earlier = compile(b'value = "retained"\n', '/verifier/entry.py', 'exec', dont_inherit=True)
            code = prepared()
            emit({'equal': earlier == code, 'identical': earlier is code,
                  'earlier': guard.contains(earlier), 'owned': guard.contains(code)})
        ''')
        self.assertTrue(result['equal'])
        self.assertFalse(result['identical'])
        self.assertFalse(result['earlier'])
        self.assertTrue(result['owned'])

    def test_future_flags_are_not_inherited_from_caller(self):
        result = self.child(r'''
            namespace = {}
            code = prepared(b'def value(x: int):\n    return x\n')
            exec(code, namespace)
            emit(namespace['value'].__annotations__['x'] is int)
        ''')
        self.assertTrue(result)

    def test_declared_future_encoding_cookie_and_unicode_survive(self):
        result = self.child(r'''
            source = '# coding: latin-1\nfrom __future__ import annotations\ndef café(x: Missing):\n    return "café"\n'.encode('latin-1')
            code = prepared(source)
            namespace = {}
            exec(code, namespace)
            emit({'value': namespace['café'](None),
                  'annotation': namespace['café'].__annotations__['x'], 'state': guard.status()})
        ''')
        self.assertEqual(result['value'], 'café')
        self.assertEqual(result['annotation'], 'Missing')
        self.assertFalse(result['state']['violated'])

    def test_compilation_can_use_owned_source_on_a_later_thread(self):
        result = self.child(r'''
            prepared()
            rows = []
            def worker():
                try:
                    code = guard.compile_source('/verifier/entry.py')
                    namespace = {}
                    exec(code, namespace)
                    rows.append(namespace['value'])
                except BaseException as error:
                    rows.append(type(error).__name__)
            thread = threading.Thread(target=worker)
            thread.start()
            thread.join()
            emit({'rows': rows, 'state': guard.status()})
        ''')
        self.assertEqual(result['rows'], ['retained'])
        self.assertFalse(result['state']['violated'])

    def test_unbound_compile_refuses_and_violation_stays_after_catch(self):
        result = self.child(r'''
            code = prepared()
            outcomes = []
            try:
                compile(b'pass', '/unbound.py', 'exec')
            except PermissionError:
                outcomes.append('compile refused')
            try:
                exec(code, {})
            except PermissionError:
                outcomes.append('later execution refused')
            emit({'outcomes': outcomes, 'state': guard.status()})
        ''')
        self.assertEqual(result['outcomes'], ['compile refused', 'later execution refused'])
        self.assertTrue(result['state']['violated'])
        self.assertEqual(result['state']['firstFailure'], 'compilation has no matching native permit')

    def test_unregistered_startup_code_does_not_become_registered(self):
        result = self.child(r'''
            prior = compile(b'pass', '/startup.py', 'exec')
            prepared()
            try:
                exec(prior, {})
            except PermissionError:
                pass
            emit({'prior': guard.contains(prior), 'state': guard.status()})
        ''')
        self.assertFalse(result['prior'])
        self.assertTrue(result['state']['violated'])

    def test_unknown_selector_fails_without_new_authority(self):
        result = self.child(r'''
            configured()
            try:
                guard.compile_source('/other.py')
            except PermissionError:
                pass
            emit(guard.status())
        ''')
        self.assertTrue(result['violated'])
        self.assertEqual(result['registeredCodeCount'], 0)

    def test_malformed_configuration_is_sticky_and_not_recoverable(self):
        result = self.child(r'''
            outcomes = []
            try:
                guard.configure('run', [('/verifier/entry.py', b'pass')])
            except PermissionError:
                outcomes.append('malformed refused')
            try:
                configured()
            except PermissionError:
                outcomes.append('retry refused')
            emit({'outcomes': outcomes, 'state': guard.status()})
        ''')
        self.assertEqual(result['outcomes'], ['malformed refused', 'retry refused'])
        self.assertEqual(result['state']['phase'], 'failed')
        self.assertTrue(result['state']['violated'])

    def test_duplicate_inventory_path_refuses(self):
        result = self.child(r'''
            try:
                guard.configure('run', (('/same.py', b'pass'), ('/same.py', b'pass')))
            except PermissionError:
                pass
            emit(guard.status())
        ''')
        self.assertEqual(result['firstFailure'], 'duplicate native source path')
        self.assertEqual(result['phase'], 'failed')

    def test_subclass_input_is_not_converted_or_executed(self):
        result = self.child(r'''
            called = []
            class Source(bytes):
                def __bytes__(self):
                    called.append('conversion')
                    return b'pass'
            try:
                guard.configure('run', (('/entry.py', Source(b'pass')),))
            except PermissionError:
                pass
            emit({'called': called, 'state': guard.status()})
        ''')
        self.assertEqual(result['called'], [])
        self.assertTrue(result['state']['violated'])

    def test_configuration_requires_sole_bootstrap_thread(self):
        result = self.child(r'''
            ready = threading.Event()
            release = threading.Event()
            def waiting():
                ready.set()
                release.wait()
            thread = threading.Thread(target=waiting)
            thread.start()
            ready.wait()
            try:
                configured()
            except PermissionError:
                pass
            finally:
                release.set()
                thread.join()
            emit(guard.status())
        ''')
        self.assertTrue(result['violated'])
        self.assertEqual(result['phase'], 'failed')

    def test_compiler_error_preserves_exception_and_clears_permit(self):
        result = self.child(r'''
            configured(b'def broken(:\n')
            error_type = None
            try:
                guard.compile_source('/verifier/entry.py')
            except BaseException as error:
                error_type = type(error).__name__
            emit({'error': error_type, 'state': guard.status()})
        ''')
        self.assertEqual(result['error'], 'SyntaxError')
        self.assertTrue(result['state']['violated'])
        self.assertEqual(result['state']['registeredCodeCount'], 0)
        self.assertFalse(result['state']['permitActive'])

    def test_nul_source_has_original_syntax_error_without_truncation(self):
        result = self.child(r'''
            configured(b'pass\x00unparsed')
            outcome = None
            try:
                guard.compile_source('/verifier/entry.py')
            except SyntaxError as error:
                outcome = str(error)
            emit({'error': outcome, 'state': guard.status()})
        ''')
        self.assertEqual(result['error'], 'source code string cannot contain null bytes')
        self.assertTrue(result['state']['violated'])
        self.assertEqual(result['state']['registeredCodeCount'], 0)

    def test_successful_configuration_cannot_be_replaced(self):
        result = self.child(r'''
            configured()
            try:
                guard.configure('different', (('/different.py', b'pass'),))
            except PermissionError:
                pass
            emit(guard.status())
        ''')
        self.assertEqual(result['runId'], 'native-component-control')
        self.assertTrue(result['violated'])
        self.assertEqual(result['firstFailure'], 'native configuration is one-shot')

    def test_activation_requires_prepared_code(self):
        result = self.child(r'''
            configured()
            try:
                guard.activate()
            except PermissionError:
                pass
            emit(guard.status())
        ''')
        self.assertTrue(result['violated'])
        self.assertEqual(result['phase'], 'configured')
        self.assertEqual(result['registeredCodeCount'], 0)

    def test_function_construction_accepts_actual_registered_function_code(self):
        result = self.child(r'''
            code = prepared(b'def value():\n    return "function"\n')
            namespace = {}
            exec(code, namespace)
            function = types.FunctionType(namespace['value'].__code__, {})
            emit({'value': function(), 'state': guard.status()})
        ''')
        self.assertEqual(result['value'], 'function')
        self.assertFalse(result['state']['violated'])

    def test_direct_code_replacement_refuses(self):
        result = self.child(r'''
            code = prepared()
            refused = False
            try:
                code.replace(co_name='replacement')
            except PermissionError:
                refused = True
            emit({'refused': refused, 'state': guard.status()})
        ''')
        self.assertTrue(result['refused'])
        self.assertTrue(result['state']['violated'])

    def test_deserialization_cannot_register_code(self):
        result = self.child(r'''
            code = prepared()
            payload = marshal.dumps(code)
            refused = False
            try:
                marshal.loads(payload)
            except PermissionError:
                refused = True
            emit({'refused': refused, 'state': guard.status()})
        ''')
        self.assertTrue(result['refused'])
        self.assertTrue(result['state']['violated'])

    def test_reentrant_compilation_fails_sticky_and_clears_permit(self):
        result = self.child(r'''
            callbacks = []
            def callback(event, arguments):
                if event == 'compile':
                    try:
                        guard.compile_source('/verifier/entry.py')
                    except PermissionError:
                        callbacks.append('reentry refused')
            sys.addaudithook(callback)
            configured()
            refused = False
            try:
                guard.compile_source('/verifier/entry.py')
            except PermissionError:
                refused = True
            emit({'callbacks': callbacks, 'refused': refused, 'state': guard.status()})
        ''')
        self.assertEqual(result['callbacks'], ['reentry refused'])
        self.assertTrue(result['refused'])
        self.assertTrue(result['state']['violated'])
        self.assertFalse(result['state']['permitActive'])
        self.assertEqual(result['state']['registeredCodeCount'], 0)


if __name__ == '__main__':
    unittest.main()
