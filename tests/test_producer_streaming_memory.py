"""Finite private producer codec and whole-operation memory regression.

The RSS threshold is for this fixed fixture only. It leaves the separate 8G
campaign limit and the earlier ownership fixture's 100000 KiB bound unchanged.
"""
from pathlib import Path
import sys
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'runtime'))
import collections.abc
import hashlib
import inspect
import json
import os
import resource
import subprocess
import traceback
import unittest
from unittest.mock import patch
from worldline import evaluation_producer as producer
from worldline import evaluation_policy as policy


def original_encode(value):
    from worldline.evaluation_policy import raw_json
    return raw_json(producer.capture(value)).encode('ascii')


def fixture():
    leaf = 'x' * 1024
    return {'phases': {phase: {
        'request': {'phase': phase},
        'acquisitions': [{'kind': 'private-kernel-role-observation', 'occurrence': i,
                          'observation': {'source': {'bytes': leaf}, 'status': [True, None, i]}}
                         for i in range(30000)],
        'result': {'profileId': 'private-evaluator-v1', 'report': {'bytes': leaf}},
        'artifact': {'payload': leaf}}
        for phase in ('before', 'after')}}


def memory_worker():
    initial = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    value = fixture()
    raw = producer.encode(value)
    # Sample before oracle output is allocated. Full equality is checked after
    # measurement; the second output is outside the measured operation boundary.
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    status = Path('/proc/self/status').read_text()
    membership = Path('/proc/self/cgroup').read_text()
    relative = next(line.split(':', 2)[2] for line in membership.splitlines()
                    if line.startswith('0::'))
    group = Path('/sys/fs/cgroup') / relative.lstrip('/')
    expected = original_encode(value)
    print(json.dumps({'complete_output_equal': raw == expected,
        'output_bytes': len(raw), 'output_sha256': hashlib.sha256(raw).hexdigest(),
        'width': 30000, 'leaf_bytes': 1024, 'initial_ru_maxrss_kib': initial,
        'ru_maxrss_kib': peak, 'proc_status_before_oracle': status,
        'observer': 'fresh post-exec fork; whole fixture and capture+encode before oracle allocation',
        'python': sys.version, 'cgroup': membership,
        'memory.max': (group / 'memory.max').read_text().strip(),
        'producer_sha256': hashlib.sha256(Path(producer.__file__).read_bytes()).hexdigest(),
        'policy_sha256': hashlib.sha256(Path(policy.__file__).read_bytes()).hexdigest(),
        'claim': 'finite fixed-fixture regression only'}), flush=True)


def fresh_worker():
    sys.stdout.flush()
    sys.stderr.flush()
    child = os.fork()
    if child == 0:
        try:
            memory_worker()
        except BaseException:
            traceback.print_exc()
            sys.stderr.flush()
            os._exit(1)
        os._exit(0)
    _, status = os.waitpid(child, 0)
    return os.waitstatus_to_exitcode(status)


class ProducerStreamingMemory(unittest.TestCase):
    def test_fixed_controller_fixture_encoder_peak(self):
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1',
                           PYTHONPATH=str(REPO / 'runtime'))
        result = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()),
                                 '--measure-producer'], env=environment,
                                capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stderr)
        measured = json.loads(result.stdout)
        print('WORLDLINE_PRODUCER_MEMORY ' + json.dumps(measured), flush=True)
        self.assertTrue(measured['complete_output_equal'])
        self.assertEqual(measured['width'], 30000)
        self.assertEqual(measured['leaf_bytes'], 1024)
        # Engineering threshold selected after paired original234412KiB and
        # private prototype166372KiB measurements with complete wire comparison.
        self.assertLessEqual(measured['ru_maxrss_kib'], 200000)

    def test_complete_scalar_and_container_bytes(self):
        for value in (None, True, False, 1 << 20000, -(1 << 20000), -0.0,
                      float('nan'), float('inf'), -float('inf'), '\ud800',
                      b'\x00\xff', {'é': [None, 1, -0.0, b'full', '\udfff']},
                      [], {}, (1, 'full')):
            with self.subTest(kind=type(value).__name__):
                self.assertEqual(producer.encode(value), original_encode(value))

    def test_mutated_default_encoder_preserves_hook_calls(self):
        previous = json._default_encoder
        observed = []
        for function in (original_encode, producer.encode):
            calls = []
            class WatchedEncoder:
                def encode(self, value):
                    calls.append(type(value).__name__)
                    return previous.encode(value)
            with patch.object(json, '_default_encoder', WatchedEncoder()):
                raw = function({'key': ['full', None]})
            observed.append((raw, calls))
        self.assertEqual(*observed)

    def test_effectful_capture_preserves_imported_formatter(self):
        original = policy.raw_json
        observed = []
        class MutatingMap(collections.abc.Mapping):
            def __init__(self, calls): self.calls = calls
            def __iter__(self): self.calls.append('iter'); return iter(('x',))
            def __len__(self): return 1
            def __getitem__(self, key):
                self.calls.append(('get', key))
                def replacement(value):
                    self.calls.append(('replacement', type(value).__name__))
                    return '"mutated"'
                policy.raw_json = replacement
                return 1
        for function in (original_encode, producer.encode):
            calls = []
            try:
                policy.raw_json = original
                raw = function(MutatingMap(calls))
                observed.append((raw, calls))
            finally:
                policy.raw_json = original
        self.assertEqual(*observed)

    def test_fast_interruption_clears_owned_encoder_locals(self):
        lines, first = inspect.getsourcelines(producer.encode)
        target = next(first + i for i, line in enumerate(lines)
                      if 'return output.getvalue()' in line)
        interruption = KeyboardInterrupt('private producer interruption')
        def trace(frame, event, arg):
            if frame.f_code is producer.encode.__code__ and event == 'line' and frame.f_lineno == target:
                raise interruption
            return trace
        previous = sys.gettrace()
        error = None
        try:
            sys.settrace(trace)
            try:
                producer.encode({'full': ['value']})
            except BaseException as caught:
                error = caught
        finally:
            sys.settrace(previous)
        self.assertIs(error, interruption)
        frame = error.__traceback__
        while frame is not None and frame.tb_frame.f_code is not producer.encode.__code__:
            frame = frame.tb_next
        self.assertIsNotNone(frame)
        for name in ('captured', 'shadow', 'output', 'pending', 'item', 'iterator', 'child', 'key'):
            self.assertIn(name, frame.tb_frame.f_locals)
            self.assertIsNone(frame.tb_frame.f_locals[name])


if __name__ == '__main__':
    if sys.argv[1:] == ['--measure-producer']:
        raise SystemExit(fresh_worker())
    unittest.main()
