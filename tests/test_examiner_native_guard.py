"""Additive real-interpreter controls; a supplied native build is mandatory.

Run only through the existing reviewed Root control route. These are native
dependency controls, not WORLDLINE world actors or complete confinement tests.
"""
import hashlib
import json
import os
from pathlib import Path
import re
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


def uapi_integer(header, name):
    """Read the pinned installed UAPI constant without executing header text."""
    content = (Path('/usr/include') / header).read_text()
    found = re.findall(r'^\s*#\s*define\s+' + re.escape(name) +
                       r'\s+(0x[0-9a-fA-F]+|[0-9]+)[uUlL]*(?:\s|$)', content, re.M)
    if len(found) != 1:
        raise AssertionError('expected one literal UAPI constant: ' + name)
    return int(found[0], 0)


def deny_constructor_operation(artifact, operation):
    """A test child adds an irreversible denial, then execs the real artifact."""
    constants = {name: uapi_integer('linux/bpf_common.h', name) for name in
                 ('BPF_LD', 'BPF_W', 'BPF_ABS', 'BPF_JMP', 'BPF_JEQ', 'BPF_K', 'BPF_RET')}
    constants.update({name: uapi_integer('linux/seccomp.h', name) for name in
                      ('SECCOMP_RET_ERRNO', 'SECCOMP_RET_ALLOW', 'SECCOMP_SET_MODE_FILTER')})
    constants['PR_SET_NO_NEW_PRIVS'] = uapi_integer('linux/prctl.h', 'PR_SET_NO_NEW_PRIVS')
    constants['seccomp'] = uapi_integer('asm-generic/unistd.h', '__NR_seccomp')
    constants['denied'] = uapi_integer('asm-generic/unistd.h', '__NR_' + operation)
    source = '''\
import ctypes, errno, json, os, sys
c = json.loads(sys.argv[2])
class Instruction(ctypes.Structure):
    _fields_ = [('code', ctypes.c_ushort), ('jt', ctypes.c_ubyte),
                ('jf', ctypes.c_ubyte), ('k', ctypes.c_uint)]
class Program(ctypes.Structure):
    _fields_ = [('len', ctypes.c_ushort), ('filter', ctypes.POINTER(Instruction))]
class Data(ctypes.Structure):
    _fields_ = [('nr', ctypes.c_int), ('arch', ctypes.c_uint),
                ('ip', ctypes.c_ulonglong), ('args', ctypes.c_ulonglong * 6)]
rows = (Instruction * 4)(
    Instruction(c['BPF_LD'] | c['BPF_W'] | c['BPF_ABS'], 0, 0, Data.nr.offset),
    Instruction(c['BPF_JMP'] | c['BPF_JEQ'] | c['BPF_K'], 0, 1, c['denied']),
    Instruction(c['BPF_RET'] | c['BPF_K'], 0, 0, c['SECCOMP_RET_ERRNO'] | errno.EACCES),
    Instruction(c['BPF_RET'] | c['BPF_K'], 0, 0, c['SECCOMP_RET_ALLOW']))
program = Program(len(rows), rows)
libc = ctypes.CDLL(None, use_errno=True)
libc.syscall.restype = ctypes.c_long
assert libc.prctl(c['PR_SET_NO_NEW_PRIVS'], ctypes.c_ulong(1),
                  ctypes.c_ulong(0), ctypes.c_ulong(0), ctypes.c_ulong(0)) == 0
assert libc.syscall(ctypes.c_long(c['seccomp']), ctypes.c_uint(c['SECCOMP_SET_MODE_FILTER']),
                    ctypes.c_uint(0), ctypes.byref(program)) == 0
environment = dict(os.environ, LD_PRELOAD=sys.argv[1])
os.execve('/usr/bin/python3', ['/usr/bin/python3', '-I', '-S', '-c',
          'print("ENTRY_MUST_NOT_RUN")'], environment)
'''
    environment = {key: value for key, value in os.environ.items()
                   if not key.startswith(('LD_', 'PYTHON'))}
    return subprocess.run(['/usr/bin/python3', '-I', '-S', '-c', source,
                           str(artifact), json.dumps(constants)], env=environment,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, check=False)


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


    def test_kernel_process_filter_is_installed_before_interpreter_and_retains_program(self):
        result = self.child(r'''
            import pathlib
            fields = dict(line.split(':', 1) for line in pathlib.Path('/proc/self/status').read_text().splitlines())
            emit({'state': guard.status(), 'kernel': {key: fields[key].strip() for key in
                  ('NoNewPrivs', 'Seccomp', 'Seccomp_filters')}})
        ''')
        self.assertEqual(result['kernel']['NoNewPrivs'], '1')
        self.assertEqual(result['kernel']['Seccomp'], '2')
        self.assertRegex(result['kernel']['Seccomp_filters'], r'^[1-9][0-9]*$')
        policy = result['state']['syscallPolicy']
        self.assertEqual(policy['policyId'], 'worldline-examiner-thread-group-only-v1')
        self.assertEqual(policy['architecture'], 'linux-aarch64-little-endian-lp64')
        self.assertTrue(policy['installed'])
        self.assertTrue(policy['threadSync'])
        self.assertEqual(policy['noNewPrivsResult'], 0)
        self.assertEqual(policy['seccompResult'], 0)
        self.assertTrue(policy['instructions'])
        self.assertTrue(all(len(row) == 4 and all(type(value) is int for value in row)
                            for row in policy['instructions']))
        self.assertFalse(policy['independentKernelProgramObservation'])
        self.assertFalse(result['state']['confinementEstablished'])

    def test_ordinary_fork_is_refused_in_bootstrap_and_active_phases(self):
        result = self.child(r'''
            import errno, os
            results = []
            for phase in ('bootstrap', 'active'):
                if phase == 'active':
                    prepared()
                try:
                    pid = os.fork()
                except OSError as error:
                    results.append([phase, error.errno == errno.EPERM])
                else:
                    if pid == 0:
                        os._exit(99)
                    os.waitpid(pid, 0)
                    results.append([phase, False])
            emit(results)
        ''')
        self.assertEqual(result, [['bootstrap', True], ['active', True]])

    def test_ordinary_exec_is_refused_without_replacing_the_examiner(self):
        result = self.child(r'''
            import errno, os
            prepared()
            try:
                os.execve('/usr/bin/true', ['true'], {})
            except OSError as error:
                emit({'refused': error.errno == errno.EPERM, 'phase': guard.status()['phase']})
        ''')
        self.assertEqual(result, {'refused': True, 'phase': 'active'})

    def test_clone3_pointer_route_refuses_with_enosys(self):
        number = uapi_integer('asm-generic/unistd.h', '__NR_clone3')
        result = self.child('number = ' + repr(number) + '\n' + textwrap.dedent(r'''
            import ctypes, errno
            libc = ctypes.CDLL(None, use_errno=True)
            libc.syscall.restype = ctypes.c_long
            ctypes.set_errno(0)
            result = libc.syscall(ctypes.c_long(number), ctypes.c_void_p(), ctypes.c_size_t(0))
            emit({'return': result, 'enosys': ctypes.get_errno() == errno.ENOSYS})
        '''))
        self.assertEqual(result, {'return': -1, 'enosys': True})

    def test_execveat_is_refused_without_executing_the_requested_program(self):
        number = uapi_integer('asm-generic/unistd.h', '__NR_execveat')
        result = self.child('number = ' + repr(number) + '\n' + textwrap.dedent(r'''
            import ctypes, errno
            libc = ctypes.CDLL(None, use_errno=True)
            libc.syscall.restype = ctypes.c_long
            arguments = (ctypes.c_char_p * 2)(b'true', None)
            environment = (ctypes.c_char_p * 1)(None)
            ctypes.set_errno(0)
            result = libc.syscall(ctypes.c_long(number), ctypes.c_int(-1),
                                  ctypes.c_char_p(b'/usr/bin/true'), arguments,
                                  environment, ctypes.c_int(0))
            emit({'return': result, 'eperm': ctypes.get_errno() == errno.EPERM})
        '''))
        self.assertEqual(result, {'return': -1, 'eperm': True})

    def test_changing_reported_policy_does_not_change_native_or_kernel_policy(self):
        result = self.child(r'''
            import errno, os
            policy = guard.status()['syscallPolicy']
            before = [list(row) for row in policy['instructions']]
            policy['instructions'].clear()
            policy['installed'] = False
            policy['threadSync'] = False
            try:
                pid = os.fork()
            except OSError as error:
                refused = error.errno == errno.EPERM
            else:
                if pid == 0:
                    os._exit(99)
                os.waitpid(pid, 0)
                refused = False
            actual = guard.status()['syscallPolicy']
            emit({'refused': refused, 'installed': actual['installed'],
                  'threadSync': actual['threadSync'],
                  'unchanged': [list(row) for row in actual['instructions']] == before})
        ''')
        self.assertEqual(result, {'refused': True, 'installed': True,
                                  'threadSync': True, 'unchanged': True})

    def test_ptrace_invalid_subject_control_observes_filter_errno_without_tracing(self):
        import errno
        number = uapi_integer('asm-generic/unistd.h', '__NR_ptrace')
        probe = 'number = ' + repr(number) + '\n' + textwrap.dedent(r'''
            import ctypes, json
            libc = ctypes.CDLL(None, use_errno=True)
            libc.syscall.restype = ctypes.c_long
            ctypes.set_errno(0)
            result = libc.syscall(ctypes.c_long(number), ctypes.c_long(-1),
                                  ctypes.c_long(0), ctypes.c_void_p(), ctypes.c_void_p())
            value = {'return': result, 'errno': ctypes.get_errno()}
        ''')
        # Invalid request and PID zero cannot identify a tracee. The ordinary
        # child's ESRCH control distinguishes the filter's earlier EPERM.
        environment = {key: value for key, value in os.environ.items()
                       if not key.startswith(('LD_', 'PYTHON'))}
        ordinary = subprocess.run(['/usr/bin/python3', '-I', '-S', '-c',
                                   probe + '\nprint(json.dumps(value))'], env=environment,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  timeout=30, check=False)
        self.assertEqual(ordinary.returncode, 0, ordinary.stderr.decode(errors='replace'))
        self.assertEqual(ordinary.stderr, b'')
        self.assertEqual(json.loads(ordinary.stdout), {'return': -1, 'errno': errno.ESRCH})
        guarded = self.child(probe + '\nemit(value)')
        self.assertEqual(guarded, {'return': -1, 'errno': errno.EPERM})

    def test_threads_keep_kernel_filter_and_can_complete_ordinary_io(self):
        result = self.child(r'''
            import pathlib, tempfile
            rows = []
            prepared()
            def worker():
                with tempfile.TemporaryFile() as stream:
                    stream.write(b'permitted thread data')
                    stream.seek(0)
                    value = stream.read().decode()
                fields = dict(line.split(':', 1) for line in pathlib.Path('/proc/thread-self/status').read_text().splitlines())
                rows.append({'value': value, 'mode': fields['Seccomp'].strip(),
                             'count': fields['Seccomp_filters'].strip(),
                             'noNewPrivs': fields['NoNewPrivs'].strip()})
            thread = threading.Thread(target=worker)
            thread.start()
            thread.join()
            emit(rows)
        ''')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['value'], 'permitted thread data')
        self.assertEqual(result[0]['mode'], '2')
        self.assertEqual(result[0]['noNewPrivs'], '1')
        self.assertRegex(result[0]['count'], r'^[1-9][0-9]*$')

    def test_failed_filter_installation_refuses_before_python_entry(self):
        result = deny_constructor_operation(ARTIFACT, 'seccomp')
        self.assertEqual(result.returncode, 125, result.stderr.decode(errors='replace'))
        self.assertEqual(result.stdout, b'')
        self.assertRegex(result.stderr, rb'^WORLDLINE_NATIVE_FILTER_FAILED stage=thread-sync-filter return=-1 errnoValid=1 errno=[0-9]+\n$')

    def test_failed_no_new_privs_refuses_before_python_entry(self):
        result = deny_constructor_operation(ARTIFACT, 'prctl')
        self.assertEqual(result.returncode, 125, result.stderr.decode(errors='replace'))
        self.assertEqual(result.stdout, b'')
        self.assertRegex(result.stderr, rb'^WORLDLINE_NATIVE_FILTER_FAILED stage=no-new-privs return=-1 errnoValid=1 errno=[0-9]+\n$')


from native_lifetime_controls import NativeLifetimeControls


if __name__ == '__main__':
    unittest.main()
