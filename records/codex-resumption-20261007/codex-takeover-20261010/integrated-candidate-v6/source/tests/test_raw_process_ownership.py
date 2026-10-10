"""Real owned-command completion; these controls do not establish formal proof."""
from __future__ import annotations

import base64
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest

from worldline.raw_observation import (
    ProcessAcquisitionCancelled, observed_process_run, retention_failed,
)


def decoded(value):
    return None if value is None else base64.b64decode(value['payload'], validate=True)


class RawProcessOwnershipTests(unittest.TestCase):
    def test_actual_nonzero_command_retains_exact_streams_and_wait(self):
        observations = []
        command = [sys.executable, '-c',
            "import os; os.write(1, b'actual\\x00out'); "
            "os.write(2, b'actual\\xfferr'); raise SystemExit(7)"]
        result = observed_process_run(command, timeout=10,
            observer=observations.append, details={'site': 'owned-test-command'})
        self.assertEqual(result.stdout, b'actual\x00out')
        self.assertEqual(result.stderr, b'actual\xfferr')
        self.assertEqual(result.returncode, 7)
        raw, = observations
        self.assertTrue(raw['processReturnObserved'])
        self.assertTrue(raw['processWaitReturnObserved'])
        self.assertEqual(raw['processWaitReturncode'], result.returncode)
        self.assertTrue(raw['stdoutReachedEof'])
        self.assertTrue(raw['stderrReachedEof'])
        self.assertEqual(decoded(raw['stdout']), result.stdout)
        self.assertEqual(decoded(raw['stderr']), result.stderr)

    def test_check_failure_retains_streams_and_actual_wait_before_raising(self):
        observations = []
        command = [sys.executable, '-c',
            "import os; os.write(1, b'failed-out'); "
            "os.write(2, b'failed-err'); raise SystemExit(7)"]
        with self.assertRaises(subprocess.CalledProcessError) as caught:
            observed_process_run(command, check=True, timeout=10,
                observer=observations.append)
        raw, = observations
        self.assertFalse(raw['processReturnObserved'])
        self.assertTrue(raw['processWaitReturnObserved'])
        self.assertEqual(raw['processWaitReturncode'], caught.exception.returncode)
        self.assertEqual(decoded(raw['stdout']), b'failed-out')
        self.assertEqual(decoded(raw['stderr']), b'failed-err')
        self.assertTrue(raw['stdoutReachedEof'])
        self.assertTrue(raw['stderrReachedEof'])

    def test_timeout_drains_bytes_written_after_the_owned_parent_is_killed(self):
        self.assertTrue(hasattr(os, 'fork') and Path('/proc/self/stat').exists(),
                        'this required ownership control needs the Linux runtime')
        # The descendant is also this test's own finite fixture. It observes
        # its parent's actual zombie state, then writes the trailing bytes and
        # exits. No arbitrary sleep is used to pretend the timeout happened.
        script = r'''
import os, time
from pathlib import Path
parent = os.getpid()
descendant = os.fork()
if descendant == 0:
    deadline = time.monotonic() + 20
    try:
        while time.monotonic() < deadline:
            try:
                fields = Path(f'/proc/{parent}/stat').read_text().rsplit(')', 1)[1].split()
            except FileNotFoundError:
                break
            if fields[0] == 'Z':
                os.write(1, b'late-out')
                os.write(2, b'late-err')
                break
            time.sleep(0.1)
    finally:
        os._exit(0)
os.write(1, b'initial-out')
os.write(2, b'initial-err')
while True:
    time.sleep(0.1)
'''
        observations = []
        with self.assertRaises(subprocess.TimeoutExpired) as caught:
            observed_process_run([sys.executable, '-c', script], timeout=10,
                observer=observations.append)
        self.assertEqual(caught.exception.timeout, 10)
        self.assertEqual(caught.exception.output, b'initial-outlate-out')
        self.assertEqual(caught.exception.stderr, b'initial-errlate-err')
        raw, = observations
        self.assertFalse(raw['processReturnObserved'])
        self.assertTrue(raw['processWaitReturnObserved'])
        self.assertTrue(raw['stdoutReachedEof'])
        self.assertTrue(raw['stderrReachedEof'])
        self.assertEqual(decoded(raw['stdout']), caught.exception.output)
        self.assertEqual(decoded(raw['stderr']), caught.exception.stderr)
        self.assertFalse(raw['cancellationObserved'])

    def test_cancel_is_distinct_and_retention_failure_preserves_primary(self):
        with tempfile.TemporaryDirectory(prefix='worldline-owned-query-') as directory:
            ready = Path(directory) / 'ready'
            cancellation = threading.Event()
            controller_failure = []
            def cancel_after_actual_start():
                deadline = time.monotonic() + 10
                while not ready.exists() and time.monotonic() < deadline:
                    cancellation.wait(0.1)
                if not ready.exists():
                    controller_failure.append('owned command never recorded its actual start')
                cancellation.set()
            controller = threading.Thread(target=cancel_after_actual_start)
            controller.start()
            observations = []
            refusal = OSError('injected owned observation storage failure')
            def retain_then_refuse(raw):
                observations.append(raw)
                raise refusal
            script = "import os,sys,time; from pathlib import Path; " \
                "os.write(1,b'cancel-out'); os.write(2,b'cancel-err'); " \
                "Path(sys.argv[1]).touch(); time.sleep(20)"
            try:
                with self.assertRaises(ProcessAcquisitionCancelled) as caught:
                    observed_process_run([sys.executable, '-c', script, str(ready)],
                        timeout=10, cancel_event=cancellation,
                        observer=retain_then_refuse)
            finally:
                cancellation.set()
                controller.join(timeout=10)
            self.assertFalse(controller.is_alive())
            self.assertEqual(controller_failure, [])
            primary = caught.exception
            self.assertTrue(retention_failed(primary))
            self.assertEqual(primary.output, b'cancel-out')
            self.assertEqual(primary.stderr, b'cancel-err')
            raw, = observations
            self.assertTrue(raw['cancellationObserved'])
            self.assertTrue(raw['processWaitReturnObserved'])
            self.assertEqual(raw['processWaitReturncode'], primary.returncode)
            self.assertTrue(raw['stdoutReachedEof'])
            self.assertTrue(raw['stderrReachedEof'])
            self.assertEqual(raw['exception']['exceptionType'],
                             'ProcessAcquisitionCancelled')
            self.assertTrue(any('retention also failed' in note
                                for note in primary.__notes__))


if __name__ == '__main__':
    unittest.main()
