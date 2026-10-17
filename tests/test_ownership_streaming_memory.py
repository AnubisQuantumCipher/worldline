"""Finite ownership-memory and fast-route interruption regression controls.

The fixed-fixture RSS limit is an engineering regression threshold. It does not
replace the unchanged campaign MemoryMax or establish a universal memory bound.
"""
from pathlib import Path
import sys
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'runtime'))
import hashlib
import json
import os
import resource
import subprocess
import unittest
import traceback
from worldline import evaluation_terminal as terminal
from worldline import finalization_writer as writer


def memory_observation():
    status = Path('/proc/self/status').read_text()
    return {'ru_maxrss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'status': [line for line in status.splitlines()
                       if line.startswith(('VmRSS:', 'VmHWM:'))]}


def measure_owned(launcher_memory):
    initial_memory = memory_observation()
    value = [{'kind': 'call', 'name': 'fixture',
              'args': ['full-original-text', None, True],
              'position': index, 'negative': -index, 'float': -0.0}
             for index in range(30000)]
    result = writer._owned(value)
    membership = Path('/proc/self/cgroup').read_text()
    relative = next(line.split(':', 2)[2] for line in membership.splitlines()
                    if line.startswith('0::'))
    group = Path('/sys/fs/cgroup') / relative.lstrip('/')
    print(json.dumps({'equal': result == value,
        'detached': result is not value and result[0] is not value[0],
        'width': 30000,
        'ru_maxrss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'memory_observation': memory_observation(),
        'worker_initial_memory': initial_memory,
        'launcher_memory': launcher_memory,
        'observer': 'fresh post-exec fork worker RUSAGE_SELF',
        'python_version': sys.version,
        'writer_sha256': hashlib.sha256(Path(writer.__file__).read_bytes()).hexdigest(),
        'cgroup': membership,
        'memory.max': (group / 'memory.max').read_text().strip(),
        'claim': 'finite fixed-fixture regression only'}), flush=True)


def run_fresh_measurement_worker():
    # getrusage metrics survive execve. A suite's resident pages can therefore
    # contaminate its subprocess's lifetime high-water mark. Start measurement
    # in a fresh fork of this already-execed, small launcher. The fixture, metric,
    # and threshold stay unchanged; retain both observers for diagnosis.
    launcher_memory = memory_observation()
    sys.stdout.flush()
    sys.stderr.flush()
    child = os.fork()
    if child == 0:
        try:
            measure_owned(launcher_memory)
        except BaseException:
            traceback.print_exc()
            sys.stderr.flush()
            os._exit(1)
        os._exit(0)
    _, status = os.waitpid(child, 0)
    if status != 0:
        print('WORLDLINE_MEMORY_WORKER_STATUS ' + str(status), file=sys.stderr)
    return os.waitstatus_to_exitcode(status)


class OwnershipStreamingMemory(unittest.TestCase):
    def test_fixed_breadth_fixture_stays_within_declared_rss_bound(self):
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1',
                           PYTHONPATH=str(REPO / 'runtime'))
        completed = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()),
                                    '--measure-owned'], env=environment,
                                   capture_output=True, text=True, timeout=120)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        measured = json.loads(completed.stdout)
        print('WORLDLINE_OWNERSHIP_MEMORY ' + json.dumps(measured), flush=True)
        self.assertTrue(measured['equal'])
        self.assertTrue(measured['detached'])
        self.assertEqual(measured['width'], 30000)
        # Chosen after the unchanged fixture measured original peak163996KiB
        # and private prototype peak52032KiB. Preserve the separate 8G gate.
        self.assertLessEqual(measured['ru_maxrss_kib'], 100000)

    def test_fast_route_interruption_retires_codec_temporary_without_retry(self):
        for target, event in ((terminal.value_bytes, 'return'),
                              (terminal.bytes_value, 'call'),
                              (terminal.bytes_value, 'return')):
            with self.subTest(target=target.__name__, event=event):
                original = KeyboardInterrupt('actual fast-route interruption')
                calls, fired = [], False
                def trace(frame, kind, arg):
                    nonlocal fired
                    if kind == 'call' and frame.f_code in (terminal.value_bytes.__code__, terminal.bytes_value.__code__):
                        calls.append(frame.f_code.co_name)
                    if not fired and frame.f_code is target.__code__ and kind == event:
                        fired = True
                        raise original
                    return trace
                previous = sys.gettrace()
                observed = captured = None
                try:
                    sys.settrace(trace)
                    try:
                        writer._owned({'values': [1, 'full', -0.0]})
                    except KeyboardInterrupt as error:
                        observed, captured = error, error.__traceback__
                finally:
                    sys.settrace(previous)
                self.assertTrue(fired)
                self.assertIs(observed, original)
                self.assertEqual(calls.count('value_bytes'), 1)
                self.assertEqual(calls.count('bytes_value'), 0 if target is terminal.value_bytes else 1)
                frames = []
                while captured is not None:
                    if captured.tb_frame.f_code is writer._owned.__code__:
                        frames.append(captured.tb_frame)
                    captured = captured.tb_next
                self.assertEqual(len(frames), 1)
                self.assertIsNone(frames[0].f_locals.get('encoded'))
                if target is terminal.bytes_value:
                    self.assertIsNone(frames[0].f_locals.get('candidate'))
                    self.assertIsNone(frames[0].f_locals.get('normalized'))


if __name__ == '__main__':
    if sys.argv[1:] == ['--measure-owned']:
        raise SystemExit(run_fresh_measurement_worker())
    else:
        unittest.main()
