"""Same-source native lifecycle controls over genuine owned runtime producers.

Authored source-only. The in-memory writer transport fixture is not a durability
or protected-custody claim; the selected native policy is never mocked.
"""
from __future__ import annotations

from pathlib import Path
import base64
import socket
import subprocess
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from worldline.errors import WorldlineError
from worldline.finalization_journal import FinalizationJournal
from worldline.finalization_writer import EngineFinalizationWriter
from worldline.linux.netguard import AllowlistProxy, _Handler
from worldline.linux.systemd import SystemdAdapter
from worldline.runner import _AgentAcquisition
from worldline.runner_lifecycle import allowed


class RunnerLifecycleNativeV35(unittest.TestCase):
    def owner(self, systemd=None):
        records = []
        writer = SimpleNamespace(invocation_raw=lambda **record: records.append(record))
        runner = SimpleNamespace(systemd=systemd or SimpleNamespace(), core=None)
        return _AgentAcquisition(runner, writer, 'actual-owned-subject'), records

    def test_actual_running_process_retains_capacity_until_wait_and_real_eof(self):
        process = subprocess.Popen(['/usr/bin/python3', '-c',
            "import sys; sys.stdin.buffer.read(1); "
            "sys.stdout.buffer.write(b'actual-tail'); sys.stderr.buffer.write(b'actual-error')"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        def cleanup_process():
            if process.poll() is None:
                process.kill()
            process.wait(timeout=5)
        self.addCleanup(cleanup_process)
        for stream in (process.stdin, process.stdout, process.stderr):
            self.addCleanup(stream.close)
        owner, records = self.owner(SimpleNamespace(outcome=lambda *args, **kwargs: {'kind': 'CONTROL'}))
        owner.unit = SimpleNamespace(launcher=process, unit='real-process-control')
        owner._stream_eof = {'stdout': False, 'stderr': False}
        released = []
        owner.guard = SimpleNamespace(release=lambda: released.append('actual-release-call'))
        owner.cleanup_started = True
        self.assertFalse(owner.quiescent())
        self.assertFalse(allowed('release-guard', owner.quiescence_observation()))
        process.stdin.write(b'x')
        process.stdin.flush()
        owner.wait()
        # Actual launcher return is not an EOF observation and cannot close a generation.
        self.assertFalse(owner.quiescent())
        owner.finish()
        self.assertTrue(owner.finished)
        self.assertTrue(owner.quiescent())
        self.assertEqual(released, ['actual-release-call'])
        self.assertTrue(all(stream.closed for stream in (process.stdin, process.stdout, process.stderr)))
        self.assertEqual(b''.join(base64.b64decode(row['observed']['bytes']['payload'])
            for row in records if row['kind'] == 'agent-stream-tail-read'
            and row['observed']['stream'] == 'stdout'), b'actual-tail')
        owner.finish()
        self.assertEqual(released, ['actual-release-call'])

    def test_actual_owned_thread_refuses_then_retry_observes_real_exit(self):
        entered, release = threading.Event(), threading.Event()
        def sample():
            entered.set()
            release.wait()
        owner, _ = self.owner()
        owner.sampler = threading.Thread(target=sample, name='actual-retained-sampler')
        owner.sampler.start()
        self.addCleanup(lambda: owner.sampler.join(timeout=5))
        self.addCleanup(release.set)
        self.assertTrue(entered.wait(timeout=5))
        owner.cleanup_started = True
        released = []
        owner.guard = SimpleNamespace(release=lambda: released.append('actual-release-call'))
        self.assertFalse(owner.quiescent())
        self.assertFalse(allowed('release-guard', owner.quiescence_observation()))
        release.set()
        owner.sampler.join(timeout=5)
        self.assertFalse(owner.sampler.is_alive())
        owner.finish()
        owner.finish()
        self.assertEqual(released, ['actual-release-call'])

    def test_actual_proxy_listener_handler_and_sockets_are_owned_until_end(self):
        with tempfile.TemporaryDirectory() as directory:
            entered, release = threading.Event(), threading.Event()
            def handle(_handler):
                entered.set()
                release.wait()
            with patch.object(_Handler, 'handle', handle):
                proxy = AllowlistProxy(Path(directory) / 'proxy.sock', ())
                proxy.start()
                client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                try:
                    client.connect(str(proxy.socket_path))
                    self.assertTrue(entered.wait(timeout=5))
                    observation = proxy.quiescence_observation()
                    self.assertTrue(observation['listenerAlive'])
                    self.assertTrue(any(item['alive'] for item in observation['handlers']))
                    self.assertFalse(proxy.quiescent())
                    self.assertFalse(allowed('proxy-ended', observation))
                    release.set()
                    proxy.stop()
                    self.assertTrue(proxy.quiescent())
                finally:
                    release.set()
                    client.close()
                    proxy.stop()

    def test_controller_after_real_native_closure_keeps_callback_but_invalidates_generation(self):
        journal = object.__new__(FinalizationJournal)
        journal.lock = threading.RLock()
        retained = []
        journal.observe = lambda *args: retained.append(args)
        writer = EngineFinalizationWriter(journal, None)
        writer.start = SimpleNamespace(run=b'actual-native-generation-control')
        writer.invocations[('actual-owned-subject', 'agent')] = ('actual-invocation', {})
        adapter = object.__new__(SystemdAdapter)
        adapter.environment = {}
        owner = _AgentAcquisition(SimpleNamespace(systemd=adapter, core=None), writer, 'actual-owned-subject')
        owner.finish()
        writer._close_acquisitions()
        entered, release = threading.Event(), threading.Event()
        results, errors, arguments = [], [], []
        def action(unit):
            arguments.append(unit)
            entered.set()
            release.wait()
            return adapter._query(['/usr/bin/python3', '-c', "print('actual-command')"],
                                  timeout=10, site='actual-late-command-control')
        def run():
            try:
                results.append(owner.controller_call(action, 'exact-original-unit'))
            except BaseException as error:
                errors.append(error)
        thread = threading.Thread(target=run, name='actual-late-controller')
        thread.start()
        try:
            self.assertTrue(entered.wait(timeout=5))
            self.assertFalse(owner.quiescent())
            with self.assertRaises(WorldlineError):
                writer._require_acquisitions_closed()
        finally:
            release.set()
            thread.join(timeout=15)
        self.assertFalse(thread.is_alive())
        self.assertEqual(errors, [])
        self.assertEqual(arguments, ['exact-original-unit'])
        self.assertEqual(results[0].stdout, b'actual-command\n')
        self.assertTrue(owner.quiescent())
        raw = owner.quiescence_observation()['controllerCallsAfterClosure'][0]
        self.assertTrue(raw['callbackReturned'])
        self.assertTrue(raw['controlAcquisitions'][0]['processWaitReturnObserved'])
        self.assertTrue(raw['controlAcquisitions'][0]['stdoutReachedEof'])
        with self.assertRaises(WorldlineError):
            writer._require_acquisitions_closed()

    def test_actual_primary_exception_survives_cleanup_failure(self):
        primary = RuntimeError('actual original primary interruption')
        owner, _ = self.owner()
        owner.guard = SimpleNamespace(release=lambda: (_ for _ in ()).throw(OSError('actual cleanup failure')))
        with self.assertRaises(RuntimeError) as found:
            owner.finish(primary)
        self.assertIs(found.exception, primary)
        self.assertIn('actual cleanup failure', '\n'.join(primary.__notes__))
        self.assertFalse(owner.finished)

    def test_actual_complete_cancel_roster_and_custom_membership_protocol(self):
        from worldline.runner import AgentRunner
        runner = object.__new__(AgentRunner)
        runner._cancel_lock = threading.Lock()
        runner._cancelled = {'held', 'other-live-job'}
        self.assertTrue(runner._was_cancelled('held'))
        observed = runner._cancel_observations['held']
        self.assertEqual(set(observed['roster']), {'held', 'other-live-job'})
        self.assertFalse(runner._was_cancelled('absent'))
        calls = []
        class Job:
            def __init__(self, name):
                self.name = name
            def __hash__(self):
                return 37
            def __eq__(self, other):
                calls.append((self.name, other.name))
                return self.name == other.name
        runner._cancelled = {Job('custom')}
        self.assertTrue(runner._was_cancelled(Job('custom')))
        self.assertEqual(calls, [('custom', 'custom')])

    def test_actual_opaque_wait_retention_failure_still_cleans_real_process(self):
        from worldline.finalization_journal import encode
        class OpaqueReturn:
            pass
        opaque = OpaqueReturn()
        process = subprocess.Popen(['/usr/bin/python3', '-c',
            "import sys; sys.stdout.buffer.write(b'real-tail'); "
            "sys.stderr.buffer.write(b'real-error')"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        def cleanup_process():
            if process.poll() is None:
                process.kill()
            process.wait(timeout=5)
        self.addCleanup(cleanup_process)
        for stream in (process.stdin, process.stdout, process.stderr):
            self.addCleanup(stream.close)
        class ProviderLauncher:
            stdin, stdout, stderr = process.stdin, process.stdout, process.stderr
            def wait(self):
                process.wait(timeout=5)
                return opaque
        owner, _ = self.owner(SimpleNamespace(outcome=lambda *args, **kwargs: {'kind': 'CONTROL'}))
        owner.writer = SimpleNamespace(invocation_raw=lambda **record: encode(record))
        owner.unit = SimpleNamespace(launcher=ProviderLauncher(), unit='actual-provider-process')
        owner._stream_eof = {'stdout': False, 'stderr': False}
        with self.assertRaises(WorldlineError) as retained:
            owner.wait()
        primary = retained.exception
        self.assertEqual(primary.code, 'FINALIZATION_VALUE_UNSUPPORTED')
        self.assertTrue(owner.wait_observed)
        capture = owner.quiescence_observation()['launcherReturncodeCapture']
        self.assertEqual(capture['reference'], id(opaque))
        self.assertEqual(capture['typeReference'], id(type(opaque)))
        with self.assertRaises(WorldlineError) as completed:
            owner.finish(primary)
        self.assertIs(completed.exception, primary)
        self.assertTrue(owner.quiescent())
        self.assertTrue(all(stream.closed for stream in (process.stdin, process.stdout, process.stderr)))

    def test_original_native_timer_full_domain_and_actual_comparison_protocol(self):
        from worldline.runner import _timer_capture
        for value in (None, False, 0, -(1 << 50000), -0.0, float('nan'), float('-inf')):
            with self.subTest(kind=type(value).__name__):
                self.assertFalse(allowed('activate-timer', _timer_capture(value)))
        for value in (True, 1 << 50000, 0.5, float('inf')):
            with self.subTest(kind=type(value).__name__):
                self.assertTrue(allowed('activate-timer', _timer_capture(value)))
        calls = []
        class Truth:
            def __bool__(self):
                calls.append('bool')
                return True
        class Timeout:
            def __gt__(self, other):
                calls.append(('gt', other))
                return Truth()
        self.assertTrue(allowed('activate-timer', _timer_capture(Timeout())))
        self.assertEqual(calls, [('gt', 0), 'bool'])
        original = RuntimeError('actual timer comparison failure')
        class FailingTimeout:
            def __gt__(self, other):
                raise original
        with self.assertRaises(RuntimeError) as failed:
            _timer_capture(FailingTimeout())
        self.assertIs(failed.exception, original)

    def test_original_controller_stop_truth_and_reflection_free_protocol(self):
        from worldline.runner import AgentRunner, _timer_capture
        calls = []
        runner = object.__new__(AgentRunner)
        runner._cancel_lock = threading.Lock()
        runner._cancelled = set()
        runner._acquisitions_by_job = {}
        runner.systemd = SimpleNamespace(stop=lambda unit: calls.append(('stop', unit)))
        runner.cancel('none', None)
        runner.cancel('empty', '')
        self.assertEqual(calls, [])
        class Meta(type):
            def __getattribute__(self, name):
                if name in ('__module__', '__qualname__', '__name__'):
                    raise AssertionError('no incidental reflection protocol')
                return super().__getattribute__(name)
            def __eq__(self, other):
                raise AssertionError('type classification is identity, not equality')
        class Unit(metaclass=Meta):
            def __bool__(self):
                calls.append('truth')
                return True
        unit = Unit()
        runner.cancel('opaque', unit)
        self.assertEqual(calls, ['truth', ('stop', unit)])
        class Timeout(metaclass=Meta):
            def __gt__(self, other):
                calls.append(('gt', other))
                return True
        self.assertTrue(allowed('activate-timer', _timer_capture(Timeout())))
        self.assertEqual(calls[-1], ('gt', 0))
        primary = RuntimeError('actual unit truth failure')
        class Failure:
            def __bool__(self):
                raise primary
        with self.assertRaises(RuntimeError) as found:
            runner.cancel('failure', Failure())
        self.assertIs(found.exception, primary)


if __name__ == '__main__':
    unittest.main()
