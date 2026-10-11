"""Actual native calls with a small explicit helper/protocol fixture.

Real private-backend tests separately use the complete owned loader helper and
daemon. These controls never claim that this component peer supplies custody.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import unittest
import uuid

from native_lifetime_controls import NativeLifetimeControls
from worldline.linux import native_lifetime as wire


HELPER_PATH = '/run/worldline-examiner-loader.py'
ENTRY_PATH = '/verifier/entry.py'
HELPER = b'''class CleanupError(LookupError):
    def __del__(self):
        self.__context__.args = ('changed by secondary finalizer',)
        self.__context__.add_note('actual secondary finalizer note')
        print('actual secondary finalizer ran')

def _native_workload(guard, registry, code, path, read_source):
    if not registry.get('activated', False):
        imports = BoundImports(registry['native'].loader_policy, registry['native'], read_source)
        imports.__enter__()
        guard.activate()
        registry['activated'] = True
    reenter = registry.pop('reenter', None)
    if reenter is not None:
        reenter(guard, registry, code, path, read_source)
        return
    namespace = {'__name__': '__main__', '__file__': path}
    try:
        guard.run_entry(namespace)
        if registry.get('repeat_entry', False):
            guard.run_entry(namespace)
    except BaseException as primary:
        if registry.get('mutate', False):
            primary.args = ('changed by actual cleanup',)
            primary.add_note('actual cleanup note')
        raise
    finally:
        if registry.get('finalizer_mutates', False):
            raise CleanupError('actual finalizable secondary')
        if registry['cleanup']:
            raise LookupError('actual secondary restoration failure')

def alternate(guard, registry, code, path, read_source):
    raise AssertionError('alternate must not run')
'''

CASES = {
    'return': 'print("complete stdout")\n',
    'ordinary': 'print("complete stdout")\nraise ValueError("original primary")\n',
    'exit-none': 'raise SystemExit(None)\n',
    'exit-bare': 'raise SystemExit()\n',
    'exit-zero': 'raise SystemExit(0)\n',
    'exit-boolean': 'raise SystemExit(True)\n',
    'exit-false': 'raise SystemExit(False)\n',
    'exit-positive': 'raise SystemExit(7)\n',
    'exit-negative': 'raise SystemExit(-7)\n',
    'exit-large': 'raise SystemExit(1 << 100)\n',
    'exit-byte-wrap': 'raise SystemExit(256)\n',
    'exit-negative-wrap': 'raise SystemExit(-256)\n',
    'exit-multiple-args': 'raise SystemExit(1, 2)\n',
    'exit-text': 'raise SystemExit("original text\\x00retained")\n',
    'exit-absent-code': 'error = SystemExit("original args")\ndel error.code\nraise error\n',
    'exit-int-subclass': 'class Number(int):\n def __int__(self):\n  raise AssertionError("not an observation conversion")\nraise SystemExit(Number(7))\n',
    'exit-custom-attribute': 'class Exit(SystemExit):\n def __getattribute__(self, name):\n  if name == "code": return 13\n  return object.__getattribute__(self, name)\nraise Exit(7)\n',
    'exit-attribute-failure': 'class Exit(SystemExit):\n def __getattribute__(self, name):\n  if name == "code": raise ValueError("actual attribute failure")\n  return object.__getattribute__(self, name)\nraise Exit("original args")\n',
    'exit-printable': 'class Value:\n def __str__(self):\n  print("actual interpreter conversion")\n  return "printed primary value"\nraise SystemExit(Value())\n',
    'exit-print-failure': 'class Value:\n def __str__(self):\n  print("actual failing conversion")\n  raise ValueError("actual printing failure")\nraise SystemExit(Value())\n',
}


def retained(label, result):
    status, stdout, stderr, rows, terminals = result
    print('WORLDLINE_PRIMARY_CONTROL ' + json.dumps({
        'case': label, 'returncode': status,
        'stdoutBase64': base64.b64encode(stdout).decode('ascii'),
        'stderrBase64': base64.b64encode(stderr).decode('ascii'),
        'records': [{'kind': row['kind'], 'sequence': row['sequence'],
                     'peer': row['peer'], 'rawBase64': base64.b64encode(row['raw']).decode('ascii')}
                    for row in rows],
        'terminals': terminals, 'protectedCustody': False,
    }, sort_keys=True), flush=True)


class NativeWorkloadControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        NativeLifetimeControls.setUpClass.__func__(cls)
        from worldline.linux import examiner_loader, private_evaluator
        # A real owned stdlib inventory is necessary even for this component
        # fixture: CPython imports traceback after the native helper returns.
        # Keep the complete capture in the action receipt; never warm traceback
        # or substitute an exception printer to avoid the actual import route.
        cls.fixture = Path(__file__).resolve().parents[2] / 'evidence' / 'native-component-tests-v1' / 'workload-stdlib-fixture'
        cls.fixture.mkdir(exist_ok=False)
        verifiers = cls.fixture / 'empty-verifiers'
        verifiers.mkdir()
        run_id = str(uuid.uuid4())
        with (cls.fixture / 'acquisitions.jsonl').open('x') as records:
            def retain(index, value):
                records.write(json.dumps({'index': index, 'record': value}, sort_keys=True) + '\n')
                records.flush()
            policy, _records = examiner_loader.capture_policy(
                verifiers, run_id, {}, private_evaluator._read_examiner_source,
                maximum_bytes=private_evaluator.MAX_TREE_BYTES,
                maximum_entries=private_evaluator.MAX_TREE_ENTRIES, retain=retain)
        cls.fixture_policy = cls.fixture / 'policy.json'
        cls.fixture_policy.write_text(json.dumps(policy, sort_keys=True) + '\n')
        cls.fixture_policy_hash = hashlib.sha256(cls.fixture_policy.read_bytes()).hexdigest()
        cls.support = (Path(__file__).resolve().parents[1] / 'runtime/worldline/linux/examiner_loader.py').read_bytes()
        cls.runtime = Path(__file__).resolve().parents[1] / 'runtime'

    child = NativeLifetimeControls.child

    def prepared_body(self, source, *, cleanup=False, between=''):
        return f'''
sys.dont_write_bytecode = True
sys.path.insert(0, {str(self.runtime)!r})
from worldline.linux.private_evaluator import _NativeExaminerCode, _read_examiner_source
from pathlib import Path
import hashlib
source = {source.encode()!r}
support = {self.support + b'\n' + HELPER!r}
bootstrap = {{'__name__': '_fixture_loader', '__file__': {HELPER_PATH!r}}}
exec(compile(support, {HELPER_PATH!r}, 'exec', dont_inherit=True), bootstrap)
policy_bytes = Path({str(self.fixture_policy)!r}).read_bytes()
assert hashlib.sha256(policy_bytes).hexdigest() == {self.fixture_policy_hash!r}
policy = json.loads(policy_bytes)
native = _NativeExaminerCode(policy['runId'], {{}})
native.sources = {{{HELPER_PATH!r}: support, {ENTRY_PATH!r}: source}}
for item in policy['files']:
    if item['kind'] == 'source':
        content = _read_examiner_source(Path(item['path']), {{}})
        assert len(content) == item['byteCount']
        assert hashlib.sha256(content).hexdigest() == item['sha256']
        native.sources[item['path']] = content
# Make the reporting dependency genuinely cold. It must be acquired through
# the owned source/frozen/native routes after the workload result is retained.
sys.modules.pop('traceback', None)
guard.configure(policy['runId'], tuple(native.sources.items()))
native.guard = guard
for label in native._GENERATORS:
    guard.bind_cached_generator(label)
native.generators_bound = True
native.loader_policy = policy
namespace = {{}}
exec(guard.compile_source({HELPER_PATH!r}), namespace)
entry = guard.compile_source({ENTRY_PATH!r})
path = {ENTRY_PATH!r}
function = namespace['_native_workload']
arguments = (guard, {{'cleanup': {cleanup!r}, 'native': native}}, entry, path, _read_examiner_source)
guard.bind_workload(function, arguments, entry, path)
{between}
guard.run_workload()
'''

    def reference(self, source, label):
        environment = {key: value for key, value in os.environ.items()
                       if not key.startswith(('LD_', 'PYTHON'))}
        command = 'exec(compile(' + repr(source) + ', ' + repr(ENTRY_PATH) + ", 'exec'), {'__name__':'__main__', '__file__':" + repr(ENTRY_PATH) + '})'
        result = subprocess.run(['/usr/bin/python3', '-I', '-S', '-c', command],
            env=environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, check=False)
        print('WORLDLINE_PRIMARY_REFERENCE ' + json.dumps({
            'case': label, 'returncode': result.returncode,
            'stdoutBase64': base64.b64encode(result.stdout).decode('ascii'),
            'stderrBase64': base64.b64encode(result.stderr).decode('ascii')}, sort_keys=True), flush=True)
        return result

    def test_actual_workload_exit_domains_with_terminal_ack_and_peer_failures(self):
        suffix = b'WORLDLINE_NATIVE_LIFETIME_FAILED at native finalization\n'
        for label, source in CASES.items():
            with self.subTest(case=label):
                reference = self.reference(source, label)
                body = self.prepared_body(source)
                baseline = self.child(body)
                retained(label + ':baseline', baseline)
                self.assertEqual(baseline[0], reference.returncode)
                self.assertEqual(baseline[1], reference.stdout)
                if label != 'ordinary':
                    self.assertEqual(baseline[2], reference.stderr)
                else:
                    # Both complete tracebacks are retained. The native helper
                    # necessarily has its actual frames, not the reference's.
                    self.assertTrue(baseline[2].endswith(b'ValueError: original primary\n'))
                    self.assertTrue(reference.stderr.endswith(b'ValueError: original primary\n'))
                outcomes = [row for row in baseline[3] if row['kind'] == wire.WORKLOAD_OUTCOME]
                self.assertEqual(len(outcomes), 1)
                outcome = outcomes[0]['value']
                self.assertTrue(outcome[3])
                self.assertEqual(outcome[4], label == 'return')
                self.assertEqual(outcome[8], 'none' if label == 'return' else 'entry')
                exits = [row for row in baseline[3] if row['kind'] == wire.PROCESS_EXIT]
                self.assertEqual(len(exits), 1)
                self.assertGreater(exits[0]['sequence'], outcomes[0]['sequence'])
                terminal = next(row for row in baseline[3] if row['kind'] == wire.TERMINAL)
                self.assertGreater(terminal['sequence'], exits[0]['sequence'])
                for failure in ('bad_ack', 'close_before'):
                    actual = self.child(body, **{failure: terminal['sequence']})
                    retained(label + ':' + failure, actual)
                    self.assertEqual(actual[0], reference.returncode if exits[0]['value'][2] != 0 else 125)
                    self.assertEqual(actual[1], baseline[1])
                    self.assertEqual(actual[2], baseline[2] + suffix)
                    original_exit = next(row for row in actual[3] if row['kind'] == wire.PROCESS_EXIT)
                    self.assertEqual(original_exit['value'], exits[0]['value'])
                    self.assertEqual(len([row for row in actual[3] if row['kind'] == wire.WORKLOAD_OUTCOME]), 1)

    def test_actual_entry_primary_survives_real_restoration_failure(self):
        for label in ('return', 'ordinary', 'exit-positive', 'exit-zero'):
            with self.subTest(case=label):
                actual = self.child(self.prepared_body(CASES[label], cleanup=True))
                retained(label + ':cleanup', actual)
                outcome = next(row['value'] for row in actual[3] if row['kind'] == wire.WORKLOAD_OUTCOME)
                self.assertFalse(outcome[6])
                self.assertEqual(outcome[7][0], b'LookupError')
                self.assertEqual(outcome[8], 'helper' if label == 'return' else 'entry')
                if label == 'return':
                    self.assertNotEqual(actual[0], 0)
                    self.assertIn(b'actual secondary restoration failure', actual[2])
                else:
                    reference = self.reference(CASES[label], label + ':cleanup-reference')
                    self.assertEqual(actual[0], reference.returncode)
                    self.assertNotIn(b'LookupError: actual secondary restoration failure', actual[2])

    def test_held_function_mutation_and_wrong_frame_refuse_with_positive_companion(self):
        for label, mutation in (
            ('changed-code', "function.__code__ = namespace['alternate'].__code__"),
            ('changed-defaults', "function.__defaults__ = (None,)"),
            ('wrong-frame', "def wrong_frame(): guard.run_workload()\nwrong_frame()"),
        ):
            with self.subTest(case=label):
                actual = self.child(self.prepared_body('print("ENTRY_MUST_NOT_RUN")\n', between=mutation))
                retained(label, actual)
                self.assertNotEqual(actual[0], 0)
                self.assertNotIn(b'ENTRY_MUST_NOT_RUN', actual[1])
                self.assertFalse(any(row['kind'] == wire.WORKLOAD_OUTCOME for row in actual[3]))
        positive = self.child(self.prepared_body(CASES['return']))
        retained('binding-positive', positive)
        self.assertEqual(positive[0], 0)
        self.assertEqual(positive[1], b'complete stdout\n')

    def test_recursive_and_cloned_helper_cannot_consume_direct_entry_binding(self):
        for label, target in (('recursive', 'function'),
                              ('cloned', 'types.FunctionType(function.__code__, namespace)')):
            with self.subTest(case=label):
                actual = self.child(self.prepared_body('print("ENTRY_MUST_NOT_RUN")\n',
                    between="arguments[1]['reenter'] = " + target))
                retained(label + ':same-code-frame', actual)
                self.assertNotEqual(actual[0], 0)
                self.assertNotIn(b'ENTRY_MUST_NOT_RUN', actual[1])
                self.assertFalse(any(row['kind'] == wire.ATTEMPT and row['value'][0] == 'workload-entry'
                                     for row in actual[3]))
        positive = self.child(self.prepared_body(CASES['return']))
        retained('direct-frame-positive', positive)
        self.assertEqual(positive[0], 0)
        self.assertEqual(positive[1], b'complete stdout\n')

    def test_foreign_thread_and_repeated_invocations_refuse(self):
        foreign = self.child(self.prepared_body('print("ENTRY_MUST_NOT_RUN")\n',
            between='thread = threading.Thread(target=guard.run_workload)\nthread.start()\nthread.join()'))
        retained('foreign-thread', foreign)
        self.assertNotEqual(foreign[0], 0)
        self.assertNotIn(b'ENTRY_MUST_NOT_RUN', foreign[1])
        for label, body in (
            ('repeat-workload', self.prepared_body(CASES['return']) + '\nguard.run_workload()\n'),
            ('repeat-entry', self.prepared_body(CASES['return'], between="arguments[1]['repeat_entry'] = True")),
        ):
            with self.subTest(case=label):
                actual = self.child(body)
                retained(label, actual)
                self.assertNotEqual(actual[0], 0)
                self.assertEqual(actual[1], b'complete stdout\n')
                self.assertEqual(len([row for row in actual[3] if row['kind'] == wire.ATTEMPT
                                      and row['value'][0] == 'workload-entry']), 1)
        positive = self.child(self.prepared_body(CASES['return']))
        retained('single-invocation-positive', positive)
        self.assertEqual(positive[0], 0)

    def test_same_primary_object_mutation_has_distinct_before_and_after_cleanup_facts(self):
        actual = self.child(self.prepared_body(CASES['ordinary'], cleanup=True,
            between="arguments[1]['mutate'] = True"))
        retained('primary-mutation-and-secondary', actual)
        self.assertNotEqual(actual[0], 0)
        entry = next(row['value'] for row in actual[3] if row['kind'] == wire.RESULT
                     and row['value'][5] is not None and row['value'][5][0] == b'ValueError')
        outcome = next(row['value'] for row in actual[3] if row['kind'] == wire.WORKLOAD_OUTCOME)
        self.assertEqual(entry[5][2][0], (True, ('original primary',)))
        self.assertEqual(outcome[5][2][0], (True, ('changed by actual cleanup',)))
        self.assertEqual(outcome[7][0], b'LookupError')
        self.assertEqual(outcome[8], 'entry')
        self.assertTrue(actual[4][0]['entryPrimarySnapshotsDifferAcrossCleanup'])
        self.assertIn(b'ValueError: changed by actual cleanup\n', actual[2])
        self.assertNotIn(b'LookupError: actual secondary restoration failure', actual[2])

    def test_abrupt_exit_and_keyboard_interrupt_cannot_invent_a_terminal(self):
        for label, source in (('abrupt', 'import os\nos._exit(19)\n'),
                              ('keyboard', 'raise KeyboardInterrupt("actual interrupt")\n')):
            with self.subTest(case=label):
                reference = self.reference(source, label)
                actual = self.child(self.prepared_body(source))
                retained(label, actual)
                self.assertEqual(actual[0], reference.returncode)
                self.assertFalse(any(row['kind'] in (wire.PROCESS_EXIT, wire.TERMINAL) for row in actual[3]))
                self.assertEqual(bool([row for row in actual[3] if row['kind'] == wire.WORKLOAD_OUTCOME]),
                                 label == 'keyboard')

    def test_secondary_finalizer_preserves_identity_across_final_result_epoch(self):
        for mutate in (False, True):
            with self.subTest(finalizer_mutates=mutate):
                actual = self.child(self.prepared_body(CASES['ordinary'], cleanup=True,
                    between=f"arguments[1]['finalizer_mutates'] = {mutate!r}"))
                retained('reference-release-mutation:' + str(mutate), actual)
                outcome = next(row['value'] for row in actual[3] if row['kind'] == wire.WORKLOAD_OUTCOME)
                entry = next(row['value'] for row in actual[3]
                             if row['kind'] == wire.RESULT and row['value'][0] == outcome[2])
                final = next(row['value'] for row in actual[3]
                             if row['kind'] == wire.RESULT and row['value'][0] == outcome[1])
                self.assertEqual(entry[5][2][0], (True, ('original primary',)))
                self.assertEqual(outcome[5][2][0], (True, ('original primary',)))
                expected = 'changed by secondary finalizer' if mutate else 'original primary'
                self.assertEqual(final[5][2][0], (True, (expected,)))
                self.assertEqual(entry[9][1], outcome[10][0])
                self.assertEqual(outcome[10][0], outcome[10][2])
                self.assertEqual(final[9][1], outcome[10][2])
                self.assertEqual(outcome[7][0], b'CleanupError' if mutate else b'LookupError')
                self.assertNotEqual(outcome[10][1], outcome[10][2])
                self.assertEqual(actual[0], 1)
                self.assertIn(('ValueError: ' + expected + '\n').encode(), actual[2])
                self.assertEqual(b'actual secondary finalizer ran\n' in actual[1], mutate)
                # Replay only edits retained data. Actual native production and
                # real primary/object/wait observations above remain unchanged.
                events = [(row['kind'], row['sequence'], row['value']) for row in actual[3]
                          if row['kind'] != wire.HELLO]
                def replay(rows):
                    roster = wire.OperationRoster(require_workload=True)
                    return [roster.accept(*row) for row in rows][-1]
                self.assertIsNotNone(replay(events))
                outer = next(row for row in events if row[0] == wire.RESULT and row[2][0] == outcome[1])
                for label, replacement in (
                    ('missing-identity', outer[2][:9]),
                    ('boolean-identity', (*outer[2][:9], (outer[2][9][0], True))),
                    ('secondary-substitution', (*outer[2][:9], (outer[2][9][0], outcome[10][1]))),
                ):
                    with self.subTest(refusal=label), self.assertRaises(wire.NativeLifetimeFormatError):
                        replay([(row[0], row[1], replacement) if row is outer else row for row in events])

    def test_cold_interpreter_reporting_uses_owned_import_after_workload_result(self):
        actual = self.child(self.prepared_body(CASES['ordinary']))
        retained('cold-reporting-after-workload-result', actual)
        self.assertEqual(actual[0], 1)
        self.assertEqual(actual[1], b'complete stdout\n')
        self.assertTrue(actual[2].endswith(b'ValueError: original primary\n'))
        outcome = next(row['value'] for row in actual[3] if row['kind'] == wire.WORKLOAD_OUTCOME)
        result = next(row for row in actual[3] if row['kind'] == wire.RESULT and row['value'][0] == outcome[1])
        reporting = [row for row in actual[3] if row['kind'] == wire.ATTEMPT
                     and row['sequence'] > result['sequence']
                     and ((row['value'][0] == 'source-compile' and row['value'][5].endswith('/traceback.py'))
                          or (row['value'][0] == 'frozen-code' and row['value'][4] == ('traceback',)))]
        self.assertTrue(reporting, 'cold traceback must be acquired through the native owned loader')
        self.assertTrue(all(type(row['value'][6]) is bytes and row['value'][6] for row in reporting))
        self.assertFalse(actual[4][0]['nativeViolationObserved'])
        self.assertEqual(actual[4][0]['interpreterOriginalStatus'], 1)

    def test_actual_roster_rejects_missing_duplicate_and_conflicting_workload_outcomes(self):
        actual = self.child(self.prepared_body(CASES['return']))
        retained('typed-roster-positive', actual)
        self.assertEqual(actual[0], 0)
        events = [(row['kind'], row['sequence'], row['value']) for row in actual[3]
                  if row['kind'] != wire.HELLO]
        def replay(rows):
            roster = wire.OperationRoster(require_workload=True)
            results = [roster.accept(*row) for row in rows]
            return results[-1]
        positive = replay(events)
        self.assertTrue(positive['cleanReportedTerminal'])
        self.assertEqual(positive['workloadPrimaryOrigin'], 'none')
        self.assertEqual(positive['interpreterOriginalStatus'], 0)
        outcome = next(row for row in events if row[0] == wire.WORKLOAD_OUTCOME)
        process_exit = next(row for row in events if row[0] == wire.PROCESS_EXIT)
        mutations = {
            'missing-outcome': [row for row in events if row is not outcome],
            'duplicate-outcome': [item for row in events for item in
                                  ((row, row) if row is outcome else (row,))],
            'missing-interpreter-exit': [row for row in events if row is not process_exit],
            'duplicate-interpreter-exit': [item for row in events for item in
                                          ((row, row) if row is process_exit else (row,))],
            'boolean-original-status': [(row[0], row[1], (*row[2][:2], False, *row[2][3:]))
                                        if row is process_exit else row for row in events],
            'foreign-workload-identity': [(row[0], row[1], (row[2][0], None, *row[2][2:]))
                                          if row is outcome else row for row in events],
            'invented-primary': [(row[0], row[1], (*row[2][:8], 'entry', *row[2][9:]))
                                  if row is outcome else row for row in events],
        }
        for label, rows in mutations.items():
            with self.subTest(case=label), self.assertRaises(wire.NativeLifetimeFormatError):
                replay(rows)


if __name__ == '__main__':
    unittest.main()
