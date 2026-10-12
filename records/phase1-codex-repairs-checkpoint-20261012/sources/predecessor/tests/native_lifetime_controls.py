"""Additive native transport/typed-record controls, run by the reviewed batch.

The component peer below is an explicit protocol fixture. It does not assert
daemon kernel joins or custody; real private integration covers those joins.
"""
import array
import fcntl
import hashlib
import json
import os
from pathlib import Path
import socket
import struct
import subprocess
import textwrap
import threading
import time
import unittest

from worldline.linux import native_lifetime as wire


def encode(value):
    """Independent small fixture encoder; never used by the actual producer."""
    if value is None:
        return bytes([wire.NONE])
    if type(value) is bool:
        return bytes([wire.TRUE if value else wire.FALSE])
    if type(value) is int:
        size = max(1, (value.bit_length() + 8) // 8)
        raw = value.to_bytes(size, 'little', signed=True)
        while len(raw) > 1 and ((raw[-1] == 0 and not raw[-2] & 0x80)
                                or (raw[-1] == 0xff and raw[-2] & 0x80)):
            raw = raw[:-1]
        tag = wire.INTEGER
    elif type(value) is bytes:
        tag, raw = wire.BYTES, value
    elif type(value) is str:
        tag, raw = wire.TEXT, value.encode('utf-32-le', 'surrogatepass')
    elif type(value) is tuple:
        return bytes([wire.TUPLE]) + struct.pack('<Q', len(value)) + b''.join(map(encode, value))
    else:
        raise TypeError(type(value))
    return bytes([tag]) + struct.pack('<Q', len(raw)) + raw


class NativeLifetimeControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_examiner_native_guard import NativeGuardControls
        NativeGuardControls.setUpClass.__func__(cls)

    def child(self, body, *, prefix='', bad_ack=None, close_before=None):
        from test_examiner_native_guard import ARTIFACT, BOOTSTRAP
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), self.artifact_hash)
        parent, child = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        parent.setsockopt(socket.SOL_SOCKET, socket.SO_PASSCRED, 1)
        parent.settimeout(30)
        rows, errors = [], []
        terminal = []
        command = BOOTSTRAP + prefix + '''\nimport os, time, atexit
descriptor = int(sys.argv[1])
deadline = time.monotonic_ns() + 25 * 1_000_000_000
guard.attach_lifetime(descriptor, ('component-fixture',), deadline)
os.close(descriptor)
''' + textwrap.dedent(body)
        environment = {key: value for key, value in os.environ.items()
                       if not key.startswith(('LD_', 'PYTHON'))}
        process = subprocess.Popen(['/usr/bin/env', 'LD_PRELOAD=' + str(ARTIFACT),
                                    '/usr/bin/python3', '-I', '-S', '-c', command, str(child.fileno())],
            pass_fds=(child.fileno(),), env=environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        child.close()

        def peer():
            expected_sequence, previous, deadline = 0, bytes(wire.TOKEN_BYTES), None
            roster = wire.OperationRoster()
            try:
                while True:
                    packet, ancillary, flags, _ = parent.recvmsg(65537, 65536, socket.MSG_CMSG_CLOEXEC)
                    delivered, credentials = [], []
                    try:
                        for level, kind, data in ancillary:
                            if level == socket.SOL_SOCKET and kind == socket.SCM_RIGHTS:
                                values = array.array('i')
                                values.frombytes(data[:len(data) - len(data) % values.itemsize])
                                delivered.extend(values)
                            elif level == socket.SOL_SOCKET and kind == socket.SCM_CREDENTIALS:
                                credentials.append(struct.unpack('=iII', data))
                            else:
                                raise AssertionError('unexpected fixture ancillary record')
                        if not packet:
                            self.assertEqual(delivered, [])
                            return
                        self.assertEqual(flags & ~(socket.MSG_EOR | socket.MSG_CMSG_CLOEXEC), 0)
                        self.assertEqual(len(delivered), 1)
                        self.assertEqual(len(credentials), 1)
                        self.assertEqual(credentials[0][0], process.pid)
                        event, sequence, extent, prior = wire.parse_header(packet)
                        self.assertEqual(sequence, expected_sequence)
                        self.assertEqual(prior, previous)
                        descriptor = delivered[0]
                        before = os.fstat(descriptor)
                        self.assertEqual(before.st_size, extent)
                        required = fcntl.F_SEAL_WRITE | fcntl.F_SEAL_GROW | fcntl.F_SEAL_SHRINK | fcntl.F_SEAL_SEAL
                        self.assertEqual(fcntl.fcntl(descriptor, fcntl.F_GET_SEALS) & required, required)
                        raw = bytearray()
                        while True:
                            part = os.pread(descriptor, 65536, len(raw))
                            if not part:
                                break
                            raw.extend(part)
                        self.assertEqual(len(raw), extent)
                        after = os.fstat(descriptor)
                        self.assertEqual((before.st_dev, before.st_ino, before.st_size),
                                         (after.st_dev, after.st_ino, after.st_size))
                        raw = bytes(raw)
                        value = wire.decode_record(raw)
                        rows.append({'kind': event, 'sequence': sequence, 'raw': raw,
                                     'value': value, 'peer': credentials[0]})
                        if event == wire.HELLO:
                            self.assertEqual(value[:2], ('native-lifetime-open', ('component-fixture',)))
                            # Fixture chooses a stricter sub-deadline only for its
                            # own child; production uses the original role deadline.
                            deadline = time.monotonic_ns() + 20 * 1_000_000_000
                        else:
                            result = roster.accept(event, sequence, value)
                            if result is not None:
                                terminal.append(result)
                                self.assertEqual(parent.recv(65537), b'')
                        if close_before == sequence:
                            return
                        token = hashlib.sha256(previous + packet + raw).digest()
                        ack = wire.acknowledgement(event, sequence, deadline, previous, token)
                        if bad_ack == sequence:
                            ack = ack[:-1]
                        parent.sendall(ack)
                        expected_sequence += 1
                        previous = token
                        if event == wire.TERMINAL:
                            return
                    finally:
                        for descriptor in delivered:
                            os.close(descriptor)
            except BaseException as error:
                errors.append(error)
            finally:
                parent.close()

        thread = threading.Thread(target=peer, name='native-lifetime-component-peer')
        thread.start()
        try:
            stdout, stderr = process.communicate(timeout=30)
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=10)
            thread.join(timeout=10)
            parent.close()
        self.assertFalse(thread.is_alive())
        self.assertEqual(errors, [], str(errors))
        self.assertEqual(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(), self.artifact_hash)
        return process.returncode, stdout, stderr, rows, terminal

    def test_live_native_records_raw_source_and_active_acquisition_before_terminal(self):
        result, stdout, stderr, rows, terminal = self.child(r'''
            source = b'value = "after activation"\n'
            configured(source)
            first = guard.compile_source('/verifier/entry.py')
            guard.activate()
            actual = guard.compile_source('/verifier/entry.py')
            namespace = {}
            exec(actual, namespace)
            emit({'value': namespace['value'], 'state': guard.status()})
        ''')
        self.assertEqual(result, 0, stderr)
        self.assertEqual(stderr, b'')
        self.assertEqual(json.loads(stdout)['value'], 'after activation')
        attempts = [row for row in rows if row['kind'] == wire.ATTEMPT and row['value'][0] == 'source-compile']
        self.assertEqual([row['value'][1] for row in attempts], [2, 3])
        self.assertTrue(all(row['value'][6] == b'value = "after activation"\n' for row in attempts))
        self.assertTrue(terminal[0]['cleanReportedTerminal'])
        self.assertFalse(terminal[0]['protectedCustody'])

    def test_frozen_alias_metadata_and_code_have_real_nested_pairs(self):
        result, stdout, stderr, rows, terminal = self.child(r'''
            prepared()
            metadata = guard.frozen_metadata('__phello__.spam')
            code = guard.frozen_code('__phello__.spam')
            emit({'metadata': metadata, 'owned': guard.contains(code)})
        ''')
        self.assertEqual(result, 0, stderr)
        self.assertTrue(json.loads(stdout)['owned'])
        frozen = next(row for row in rows if row['kind'] == wire.ATTEMPT and row['value'][0] == 'frozen-code')
        nested = [row for row in rows if row['kind'] == wire.ATTEMPT and row['value'][3] == frozen['sequence']]
        self.assertEqual([row['value'][0] for row in nested], ['frozen-metadata'])
        self.assertTrue(frozen['value'][6])
        self.assertTrue(terminal[0]['cleanReportedTerminal'])

    def test_returned_tree_retains_nested_constant_edges_and_source_identity(self):
        result, stdout, stderr, rows, terminal = self.child(r'''
            source = b'def outer():\n    def inner():\n        return "nested"\n    return inner\n'
            code = prepared(source)
            namespace = {}
            exec(code, namespace)
            emit({'value': namespace['outer']()()})
        ''')
        self.assertEqual(result, 0, stderr)
        self.assertEqual(json.loads(stdout)['value'], 'nested')
        attempt = next(row for row in rows if row['kind'] == wire.ATTEMPT
                       and row['value'][0] == 'source-compile')
        returned = next(row['value'] for row in rows if row['kind'] == wire.RESULT
                        and row['value'][0] == attempt['sequence'])
        tree = returned[4]
        nodes = {node[3]: node for node in tree[2]}
        self.assertEqual(set(nodes), {'<module>', 'outer', 'outer.<locals>.inner'})
        self.assertEqual(tree[1], nodes['<module>'][0])
        self.assertTrue(all(node[1] == '/verifier/entry.py' and node[2] is None for node in nodes.values()))
        self.assertIn(nodes['outer'][0], [edge[1] for edge in nodes['<module>'][5]])
        self.assertIn(nodes['outer.<locals>.inner'][0], [edge[1] for edge in nodes['outer'][5]])
        self.assertEqual(nodes['outer.<locals>.inner'][5], ())
        self.assertTrue(terminal[0]['cleanReportedTerminal'])

    def test_actual_generator_binding_and_ast_normalized_compiler_are_retained(self):
        from test_examiner_native_generators import GENERATOR_BOOTSTRAP
        result, stdout, stderr, rows, terminal = self.child(r'''
            collections, dataclasses, code = generators()
            ast = sys.modules['ast']
            guard.activate()
            Point = collections.namedtuple('Point', 'label')
            tree = ast.parse(b"# coding: latin-1\nvalue = 'caf\xe9'\n", filename='typed.py', optimize=True)
            emit({'value': Point('retained').label, 'parsed': tree.body[0].value.value,
                  'minor': sys.version_info.minor, 'globals': id(ast.parse.__globals__)})
        ''', prefix=GENERATOR_BOOTSTRAP)
        self.assertEqual(result, 0, stderr)
        actual = json.loads(stdout)
        self.assertEqual(actual['value'], 'retained')
        self.assertEqual(actual['parsed'], 'café')
        attempts = {row['sequence']: row['value'] for row in rows if row['kind'] == wire.ATTEMPT}
        bindings = [row['value'][4] for row in rows if row['kind'] == wire.RESULT
                    and attempts[row['value'][0]][0] == 'bind-generator']
        ast_binding = next(value for value in bindings if value[1] == 'ast.parse')
        self.assertEqual(ast_binding[4], actual['globals'])
        self.assertIsNone(ast_binding[5])
        generated = next(value for value in attempts.values() if value[0] == 'validated-generator-source')
        self.assertEqual(generated[4][1][1], 'collections.namedtuple')
        self.assertEqual(generated[4][1][3], generated[6])
        inner = next(value for value in attempts.values() if value[0] == 'ast-compiler')
        outer = attempts[inner[3]]
        self.assertEqual(outer[0], 'ast-parse')
        self.assertEqual(outer[4][0][0], b"# coding: latin-1\nvalue = 'caf\xe9'\n")
        self.assertEqual(dict(outer[4][1][1]), {'_feature_version': -1, 'optimize': True})
        self.assertEqual(inner[5:7], ('typed.py', outer[4][0][0]))
        self.assertEqual(inner[7][2:], (actual['minor'], 1))
        self.assertIs(type(inner[7][3]), int)
        self.assertTrue(terminal[0]['cleanReportedTerminal'])

    def test_actual_cached_generator_records_selected_code_and_held_globals(self):
        from test_examiner_native_generators import CACHED_BOOTSTRAP
        result, stdout, stderr, rows, terminal = self.child(r'''
            function = collections.namedtuple
            guard.configure('native-cached-lifetime-control', cached_rows())
            cached_bind_all()
            code = guard.compile_source('/verifier/entry.py')
            guard.activate()
            Point = function('Point', 'value')
            emit({'value': Point('cached').value, 'function': id(function), 'globals': id(function.__globals__)})
        ''', prefix=CACHED_BOOTSTRAP)
        self.assertEqual(result, 0, stderr)
        actual = json.loads(stdout)
        self.assertEqual(actual['value'], 'cached')
        attempts = {row['sequence']: row['value'] for row in rows if row['kind'] == wire.ATTEMPT}
        binding = next(row['value'][4] for row in rows if row['kind'] == wire.RESULT
                       and attempts[row['value'][0]][0] == 'bind-cached-generator'
                       and attempts[row['value'][0]][4][0] == 'collections.namedtuple')
        self.assertEqual(binding[4], actual['globals'])
        self.assertEqual(binding[5][4:6], (actual['function'], actual['globals']))
        self.assertEqual(binding[5][3], binding[6][1])
        self.assertTrue(all(node[2] == binding[5] for node in binding[6][2]))
        self.assertTrue(terminal[0]['cleanReportedTerminal'])

    def test_parallel_owned_compilation_retains_per_thread_rosters(self):
        result, stdout, stderr, rows, terminal = self.child(r'''
            source = b'import _worldline_examiner_guard as guard\ndef worker():\n    guard.compile_source("/verifier/entry.py")\n'
            code = prepared(source)
            namespace = {}
            exec(code, namespace)
            threads = [threading.Thread(target=namespace['worker']) for _ in range(3)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            emit({'done': True})
        ''')
        self.assertEqual(result, 0, stderr)
        self.assertTrue(json.loads(stdout)['done'])
        active = [row['value'] for row in rows if row['kind'] == wire.ATTEMPT
                  and row['value'][0] == 'source-compile' and row['value'][1] == 3]
        self.assertEqual(len(active), 3)
        self.assertEqual(len({value[2] for value in active}), 3)
        self.assertTrue(terminal[0]['cleanReportedTerminal'])

    def test_real_python_finalizer_acquisition_precedes_native_terminal(self):
        result, stdout, stderr, rows, terminal = self.child(r'''
            source = b'import _worldline_examiner_guard as guard\ndef finalizer():\n    guard.frozen_metadata("__hello__")\n'
            code = prepared(source)
            namespace = {}
            exec(code, namespace)
            atexit.register(namespace['finalizer'])
            emit({'registered': True})
        ''')
        self.assertEqual(result, 0, stderr)
        self.assertTrue(json.loads(stdout)['registered'])
        metadata = [row for row in rows if row['kind'] == wire.ATTEMPT and row['value'][0] == 'frozen-metadata']
        self.assertTrue(metadata)
        self.assertLess(metadata[-1]['sequence'], rows[-1]['sequence'])
        self.assertEqual(rows[-1]['kind'], wire.TERMINAL)
        self.assertTrue(terminal[0]['cleanReportedTerminal'])

    def test_interrupted_native_producer_has_no_terminal(self):
        result, stdout, stderr, rows, terminal = self.child("prepared(); os._exit(19)")
        self.assertEqual(result, 19)
        self.assertEqual(stdout, b'')
        self.assertEqual(stderr, b'')
        self.assertEqual(terminal, [])
        self.assertTrue(rows)
        self.assertNotEqual(rows[-1]['kind'], wire.TERMINAL)

    def test_truncated_ack_refuses_before_code_registration(self):
        result, stdout, stderr, rows, terminal = self.child(r'''
            configured()
            try:
                guard.compile_source('/verifier/entry.py')
            except BaseException as error:
                emit({'error': type(error).__name__, 'state': guard.status()})
        ''', bad_ack=1)
        self.assertNotEqual(result, 0)
        value = json.loads(stdout)
        self.assertEqual(value['error'], 'PermissionError')
        self.assertEqual(value['state']['registeredCodeCount'], 0)
        self.assertTrue(value['state']['nativeLifetime']['transportFailed'])
        self.assertEqual(terminal, [])

    def test_closed_retention_peer_refuses_before_code_registration(self):
        result, stdout, stderr, rows, terminal = self.child(r'''
            configured()
            try:
                guard.compile_source('/verifier/entry.py')
            except BaseException as error:
                emit({'error': type(error).__name__, 'state': guard.status()})
        ''', close_before=1)
        self.assertNotEqual(result, 0)
        self.assertEqual(json.loads(stdout)['state']['registeredCodeCount'], 0)
        self.assertEqual(terminal, [])

    def test_real_compiler_failure_retains_raw_attempt_and_primary(self):
        result, stdout, stderr, rows, terminal = self.child(r'''
            configured(b'def incomplete(:\n')
            try:
                guard.compile_source('/verifier/entry.py')
            except SyntaxError as error:
                emit({'error': type(error).__name__, 'filename': error.filename})
        ''')
        self.assertNotEqual(result, 0)
        self.assertEqual(json.loads(stdout)['filename'], '/verifier/entry.py')
        attempt = next(row for row in rows if row['kind'] == wire.ATTEMPT)
        self.assertEqual(attempt['value'][6], b'def incomplete(:\n')
        failed = next(row for row in rows if row['kind'] == wire.RESULT)
        self.assertFalse(failed['value'][1])
        self.assertEqual(failed['value'][5][0], b'SyntaxError')
        self.assertTrue(failed['value'][7])
        self.assertFalse(terminal[0]['cleanReportedTerminal'])

    def test_compiler_primary_survives_result_acknowledgement_failure(self):
        result, stdout, stderr, rows, terminal = self.child(r'''
            configured(b'def incomplete(:\n')
            try:
                guard.compile_source('/verifier/entry.py')
            except BaseException as error:
                emit({'error': type(error).__name__, 'filename': error.filename,
                      'transportFailed': guard.status()['nativeLifetime']['transportFailed']})
        ''', bad_ack=2)
        self.assertNotEqual(result, 0)
        self.assertEqual(json.loads(stdout), {'error': 'SyntaxError',
            'filename': '/verifier/entry.py', 'transportFailed': True})
        self.assertEqual(rows[-1]['kind'], wire.RESULT)
        self.assertEqual(rows[-1]['value'][5][0], b'SyntaxError')
        self.assertEqual(terminal, [])

    def test_wire_roundtrip_preserves_original_typed_values(self):
        value = (None, False, True, 0, -1, 255, -129, 1 << 4096,
                 -(1 << 4096), '', 'NUL\0lone\ud800astral\U0001f600', b'\0\xff', ())
        actual = wire.decode_record(encode(value))
        self.assertTrue(wire.exact_context(actual, value))
        self.assertNotEqual(type(actual[1]), type(actual[3]))

    def test_wire_rejects_malformed_noncanonical_and_trailing_inputs(self):
        values = (b'', b'\xff', encode(None) + encode(None),
                  bytes([wire.INTEGER]) + struct.pack('<Q', 0),
                  bytes([wire.INTEGER]) + struct.pack('<Q', 2) + b'\0\0',
                  bytes([wire.TEXT]) + struct.pack('<Q', 1) + b'x',
                  bytes([wire.TEXT]) + struct.pack('<Q', 4) + struct.pack('<I', 0x110000),
                  bytes([wire.TUPLE]) + struct.pack('<Q', 5) + encode(None))
        for payload in values:
            with self.subTest(payload=payload), self.assertRaises(wire.NativeLifetimeFormatError):
                wire.decode_record(payload)

    def test_decoder_and_index_observe_cancellation_during_work(self):
        count = 0
        def stop():
            nonlocal count
            count += 1
            if count == 7:
                raise TimeoutError('original deadline control')
        payload = encode(tuple(range(100)))
        with self.assertRaisesRegex(TimeoutError, 'original deadline'):
            wire.decode_record(payload, _check=stop)
        self.assertEqual(count, 7)
        count = 0
        with self.assertRaisesRegex(TimeoutError, 'original deadline'):
            wire.observation_value(tuple(range(100)), _check=stop)
        self.assertEqual(count, 7)

    def test_context_rejects_boolean_integer_substitution(self):
        self.assertTrue(wire.exact_context(('run', ('native', 1)), ('run', ('native', 1))))
        self.assertFalse(wire.exact_context(('run', ('native', True)), ('run', ('native', 1))))

    def test_roster_rejects_success_in_bootstrap_and_contradictory_sticky_state(self):
        for phase, violated, first in ((0, False, None), (2, False, 'failure'), (2, True, None)):
            with self.subTest(phase=phase, violated=violated, first=first):
                roster = wire.OperationRoster()
                roster.accept(wire.ATTEMPT, 1, ('source-compile', phase, 1, None, (), '/owned', b'pass', (257, 0, -1, 0), 0))
                with self.assertRaises(wire.NativeLifetimeFormatError):
                    roster.accept(wire.RESULT, 2, (1, True, phase, 1,
                        ('owned-code-identity', 1), None, True, violated, first))

    def test_roster_rejects_malformed_failure_and_result_payload(self):
        for returned, value, primary in ((False, None, ()), (True, (), None), (True, True, None)):
            with self.subTest(returned=returned, value=value, primary=primary):
                roster = wire.OperationRoster()
                roster.accept(wire.ATTEMPT, 1, ('source-compile', 2, 1, None, (), '/owned', b'pass', (257, 0, -1, 0), 0))
                with self.assertRaises(wire.NativeLifetimeFormatError):
                    roster.accept(wire.RESULT, 2, (1, returned, 2, 1, value, primary, True, False, None))

    def test_roster_rejects_unlinked_and_duplicate_code_tree_nodes(self):
        root = (1, '/owned', None, '<module>', 1, ((0, 2),))
        child = (2, '/owned', None, 'inner', 0, ())
        values = (('owned-code-tree', 1, (root,)),
                  ('owned-code-tree', 1, (root, child, child)),
                  ('owned-code-tree', 1, ((1, '/owned', None, '<module>', 0, ()), child)))
        for value in values:
            with self.subTest(value=value):
                roster = wire.OperationRoster()
                roster.accept(wire.ATTEMPT, 1, ('source-compile', 2, 1, None, (), '/owned', b'pass', (257, 0, -1, 0), 0))
                with self.assertRaises(wire.NativeLifetimeFormatError):
                    roster.accept(wire.RESULT, 2, (1, True, 2, 2, value, None, True, False, None))

    def test_roster_tree_processing_observes_cancellation(self):
        def stop():
            raise TimeoutError('original deadline during code-tree validation')
        roster = wire.OperationRoster()
        roster.accept(wire.ATTEMPT, 1, ('source-compile', 2, 1, None, (), '/owned', b'pass', (257, 0, -1, 0), 0))
        # Entry checks pass; cancellation happens within the tree walk itself.
        calls = 0
        def check():
            nonlocal calls
            calls += 1
            if calls > 1:
                stop()
        roster.check = check
        with self.assertRaisesRegex(TimeoutError, 'code-tree validation'):
            roster.accept(wire.RESULT, 2, (1, True, 2, 1,
                ('owned-code-tree', 1, ((1, '/owned', None, '<module>', 0, ()),)),
                None, True, False, None))

    def test_every_success_requires_complete_native_facts(self):
        operations = (
            ('activate', (), None, 3),
            ('frozen-metadata', ('absent',), None, 2),
            ('ast-parse', (('pass', '<unknown>', 'exec', 1024),
                           ('exact-dict-entries', (('_feature_version', -1), ('optimize', -1)))),
             ('non-executable-result-not-snapshotted', b'Module'), 2))
        for name, inputs, result, phase in operations:
            for complete in (False, True):
                with self.subTest(name=name, complete=complete):
                    roster = wire.OperationRoster()
                    roster.accept(wire.ATTEMPT, 1, (name, 2, 1, None, inputs, None, None, (), 0))
                    payload = (1, True, phase, 0, result, None, complete, False, None)
                    if complete:
                        self.assertIsNone(roster.accept(wire.RESULT, 2, payload))
                    else:
                        with self.assertRaisesRegex(wire.NativeLifetimeFormatError, 'incomplete facts'):
                            roster.accept(wire.RESULT, 2, payload)
