"""Owned lifecycle controls; no formal, native-authority or custody claim."""
from __future__ import annotations

import base64
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from worldline.errors import WorldlineError
from worldline.finalization_journal import (FinalizationJournal, encode, decode,
    acquisitions_payload, payload_acquisitions)
from worldline.evaluation_terminal import value_bytes, bytes_value
from worldline.finalization_writer import EngineFinalizationWriter
from worldline.linux.netguard import AllowlistProxy, _Handler
from worldline.linux.systemd import SystemdAdapter, SystemdProcess
from worldline.raw_observation import ProcessAcquisitionCancelled
from worldline.runner import AgentRunner, _AgentAcquisition


class _ObservedThread:
    """Transport-only lifecycle fixture; never presented as actual OS evidence."""
    def __init__(self):
        self.alive = True
        self.joins = []
        self.name = 'explicitly-controlled-lifecycle-fixture'
        self.ident = None

    def is_alive(self):
        return self.alive

    def join(self, timeout=None):
        self.joins.append(timeout)


class AgentAcquisitionOwnershipTests(unittest.TestCase):
    def test_binary_acquisition_envelope_preserves_full_values_and_json_row_domain(self):
        original = [{'kind': 'explicit-transport-control', 'occurrence': 0,
            'observation': {'bytes': b'\x00\xfffull',
                            'identity': (b'whole', [None, b''])}}]
        envelope = acquisitions_payload(original)
        transported = bytes_value(value_bytes({'engineRawObservations': envelope}))
        self.assertEqual(encode(payload_acquisitions(transported['engineRawObservations'])),
                         encode(original))
        original[0]['observation']['identity'][1].append('later mutation')
        self.assertNotEqual(encode(payload_acquisitions(envelope)), encode(original))
        self.assertIsNone(payload_acquisitions(None))
        self.assertEqual(payload_acquisitions(acquisitions_payload([])), [])
        legacy = [{'kind': 'legacy-json-control', 'observation': {'value': [None, '']}}]
        self.assertEqual(payload_acquisitions(legacy), legacy)

    def test_malformed_acquisition_envelope_never_falls_back_to_legacy_values(self):
        valid = acquisitions_payload([])
        malformed = [dict(valid, encoding='unknown'), dict(valid, extra=True),
                     {'encoding': valid['encoding']}, dict(valid, payload='not base64!'),
                     dict(valid, payload=valid['payload'] + '\n'),
                     dict(valid, payload=base64.b64encode(encode(('tuple-not-list',))).decode('ascii'))]
        for value in malformed:
            with self.subTest(value=value), self.assertRaises(WorldlineError):
                payload_acquisitions(value)

    def _failed_reader_tail(self, *, refuse_tail):
        process = subprocess.Popen(['/usr/bin/python3', '-c',
            "import sys; sys.stdout.buffer.write(b'first\\nremaining\\n'); "
            "sys.stderr.buffer.write(b'original outcome stderr')"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for stream in (process.stdin, process.stdout, process.stderr):
            self.addCleanup(stream.close)
        journal = object.__new__(FinalizationJournal)
        journal.lock = threading.RLock()
        persisted = []
        retention_error = OSError('actual tail observation store refusal')
        def observe(*args):
            if refuse_tail and args[3] == 'raw-acquisition':
                # Use the actual writer record's kind, not a manufactured EOF.
                value = args[4]
                if value['kind'] == 'agent-stream-tail-read':
                    raise retention_error
            persisted.append(args)
        journal.observe = observe
        writer = EngineFinalizationWriter(journal, None)
        writer.start = SimpleNamespace(run=b'owned-tail-run')
        writer.invocations[('subject', 'agent')] = ('owned-invocation', {})
        order = []
        primary = RuntimeError('original reader progress callback failed')
        def outcome(unit, code, **kwargs):
            self.assertFalse(process.stderr.closed)
            self.assertFalse(owner._tail_threads)
            stderr = process.stderr.read()
            order.append(('outcome', stderr))
            kwargs['_raw_observer']('original-stderr', {
                'site': 'launcher-stderr-reread', 'readReturned': True,
                'stderr': {'encoding': 'base64',
                           'payload': base64.b64encode(stderr).decode('ascii')}})
            return {'kind': 'TRANSPORT_CONTROL_ONLY'}
        owner = _AgentAcquisition(SimpleNamespace(systemd=SimpleNamespace(outcome=outcome)), writer, 'subject')
        owner.unit = SimpleNamespace(launcher=process, unit='owned-tail-fixture')
        owner._stream_eof = {'stdout': False, 'stderr': False}
        released = []
        owner.guard = SimpleNamespace(release=lambda: released.append('released'))
        def reader():
            line = process.stdout.readline()
            writer.invocation_raw(world_instance='subject', check='agent',
                kind='agent-stdout-read', observed={'bytes': line})
            order.append(('reader', line))
            try:
                raise primary
            except BaseException as failure:
                owner.thread_errors.append(failure)
        thread = threading.Thread(target=reader)
        owner.threads.append(thread)
        thread.start()
        process.stdin.close()
        owner.wait()
        with self.assertRaises(RuntimeError) as found:
            owner.finish()
        self.assertIs(found.exception, primary)
        self.assertEqual(order, [('reader', b'first\n'), ('outcome', b'original outcome stderr')])
        tails = owner._tail_observations
        self.assertEqual(b''.join(base64.b64decode(row['bytes']['payload'])
            for row in tails if row['stream'] == 'stdout' and row['readReturned']), b'remaining\n')
        self.assertEqual(b''.join(base64.b64decode(row['bytes']['payload'])
            for row in tails if row['stream'] == 'stderr' and row['readReturned']), b'')
        self.assertTrue(all(owner._stream_eof.values()))
        self.assertTrue(all(not item.is_alive() for item in owner._tail_threads))
        self.assertTrue(all(stream.closed for stream in (process.stdin, process.stdout, process.stderr)))
        self.assertTrue(owner.finished)
        self.assertTrue(owner.quiescent())
        self.assertEqual(released, ['released'])
        if refuse_tail:
            self.assertIs(writer._acquisition_failure, retention_error)
            with self.assertRaises(WorldlineError):
                writer._close_acquisitions()
            self.assertIsNone(writer._acquisition_generation)
        else:
            self.assertIsNone(writer._acquisition_failure)

    def test_failed_reader_preserves_original_outcome_read_then_drains_real_tail(self):
        self._failed_reader_tail(refuse_tail=False)

    def test_tail_retention_failure_latches_capture_but_closes_ended_os_ownership(self):
        self._failed_reader_tail(refuse_tail=True)

    def test_owned_launcher_streams_close_after_actual_readers_and_outcome(self):
        process = subprocess.Popen(['/usr/bin/python3', '-c',
            "import sys; sys.stdout.buffer.write(b'owned-out'); sys.stderr.buffer.write(b'owned-err')"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for stream in (process.stdin, process.stdout, process.stderr):
            self.addCleanup(stream.close)
        data = {}
        primary = OSError('retaining actual launcher wait refused')
        def observed(**record):
            if record['kind'] == 'agent-launcher-wait':
                raise primary
        def outcome(unit, code, **kwargs):
            self.assertFalse(process.stderr.closed)
            self.assertEqual(process.stderr.read(), b'')
            return {'kind': 'TRANSPORT_CONTROL_ONLY'}
        owner = _AgentAcquisition(SimpleNamespace(systemd=SimpleNamespace(outcome=outcome)),
            SimpleNamespace(invocation_raw=observed), 'subject')
        owner.unit = SimpleNamespace(launcher=process, unit='owned-fixture')
        owner._stream_eof = {'stdout': False, 'stderr': False}
        def read_stream(name, stream):
            data[name] = stream.read()
            owner._observe_stream_eof(name)
        for name, stream in (('stdout', process.stdout), ('stderr', process.stderr)):
            thread = threading.Thread(target=read_stream, args=(name, stream))
            owner.threads.append(thread)
            thread.start()
        process.stdin.close()
        with self.assertRaises(OSError) as wait_error:
            owner.wait()
        self.assertIs(wait_error.exception, primary)
        with self.assertRaises(OSError) as cleanup_error:
            owner.finish(primary)
        self.assertIs(cleanup_error.exception, primary)
        self.assertEqual(data, {'stdout': b'owned-out', 'stderr': b'owned-err'})
        self.assertTrue(all(stream.closed for stream in (process.stdin, process.stdout, process.stderr)))
        self.assertTrue(owner.finished)
        self.assertTrue(owner.quiescent())

    def test_live_sampler_retains_guard_and_does_not_repeat_original_join_grace(self):
        released = []
        owner = _AgentAcquisition(SimpleNamespace(systemd=SimpleNamespace()),
                                 SimpleNamespace(invocation_raw=lambda **record: None), 'subject')
        owner.guard = SimpleNamespace(release=lambda: released.append('released'))
        owner.sampling = threading.Event()
        owner.sampler = _ObservedThread()
        with self.assertRaises(WorldlineError) as first:
            owner.finish()
        self.assertEqual(first.exception.code, 'AGENT_ACQUISITION_NOT_QUIESCENT')
        self.assertTrue(owner.sampling.is_set())
        self.assertFalse(owner.finished)
        self.assertFalse(owner.quiescent())
        self.assertEqual(released, [])
        self.assertEqual(owner.sampler.joins, [5])
        with self.assertRaises(WorldlineError):
            owner.finish()
        self.assertEqual(owner.sampler.joins, [5])
        # A genuinely changed observation can complete cleanup; elapsed grace
        # alone never does. This does not fabricate completion of the agent run.
        owner.sampler.alive = False
        owner.finish()
        self.assertTrue(owner.finished)
        self.assertEqual(released, ['released'])

    def test_injected_provider_keeps_original_arguments_and_exception_identity(self):
        calls = []
        original = RuntimeError('actual original provider exception')
        def provider(unit):
            calls.append(unit)
            raise original
        owner = _AgentAcquisition(SimpleNamespace(systemd=SimpleNamespace()),
                                 SimpleNamespace(invocation_raw=lambda **record: None), 'subject')
        with self.assertRaises(RuntimeError) as found:
            owner.systemd_call(provider, 'original-unit', cancel_event=threading.Event())
        self.assertIs(found.exception, original)
        self.assertEqual(calls, ['original-unit'])

    def test_unclosed_query_blocks_owner_even_with_no_live_sampler(self):
        adapter = object.__new__(SystemdAdapter)
        adapter.environment = {}
        observations = []
        owner = _AgentAcquisition(SimpleNamespace(systemd=adapter),
            SimpleNamespace(invocation_raw=lambda **record: observations.append(record)), 'subject')
        def incomplete(argv, *, observer, **kwargs):
            observer({'site': 'explicit-transport-fixture', 'argv': list(argv),
                'processCreatedObserved': True, 'processPidObserved': os.getpid(),
                'processWaitReturnObserved': True, 'processWaitReturncode': 0,
                'stdoutReachedEof': False, 'stderrReachedEof': True})
            return subprocess.CompletedProcess(argv, 0, b'', b'')
        with patch('worldline.raw_observation.observed_process_run', side_effect=incomplete):
            owner.systemd_call(adapter._query, ['fixture-only'], timeout=10, site='fixture-only')
        with self.assertRaises(WorldlineError):
            owner.finish()
        self.assertFalse(owner.finished)
        self.assertFalse(owner.quiescent())
        self.assertTrue(owner.quiescence_observation()['unclosedCommands'])
        self.assertEqual(observations[0]['observed']['stdoutReachedEof'], False)

    def test_builtin_cancellation_binds_actual_complete_drain_and_keeps_explicit_observer(self):
        adapter = object.__new__(SystemdAdapter)
        adapter.environment = {}
        event = threading.Event()
        event.set()
        observations, lifecycle = [], []
        original = ProcessAcquisitionCancelled(['fixture-only'])
        def completed_cancel(argv, *, observer, **kwargs):
            observer({'processCreatedObserved': True, 'processPidObserved': os.getpid(),
                'processWaitReturnObserved': True, 'stdoutReachedEof': True,
                'stderrReachedEof': True, 'cancellationObserved': True})
            raise original
        with patch('worldline.raw_observation.observed_process_run', side_effect=completed_cancel):
            with adapter.acquisition_scope(lambda record: self.fail('explicit observer was replaced'),
                    cancel_event=event, _ownership_observer=lifecycle.append):
                with self.assertRaises(ProcessAcquisitionCancelled) as found:
                    adapter._query(['fixture-only'], timeout=10, site='fixture-only',
                                   observer=observations.append)
        self.assertIs(found.exception, original)
        self.assertIs(original._worldline_systemd_cancel_event, event)
        self.assertTrue(original._worldline_systemd_cancel_complete)
        self.assertEqual(observations, lifecycle)

    def test_cgroup_raw_precedes_unchanged_text_projection(self):
        adapter = object.__new__(SystemdAdapter)
        observations = []
        with patch.object(Path, 'read_bytes', return_value=b'max\r\n'):
            with adapter.acquisition_scope(observations.append):
                result = adapter._cgroup_value('/owned-fixture', 'memory.max')
        self.assertEqual(result, 'max')
        self.assertEqual(observations[0]['bytes'], {'encoding': 'base64', 'payload': 'bWF4DQo='})
        self.assertTrue(observations[0]['readReturned'])


class AcquisitionGenerationTests(unittest.TestCase):
    def test_controller_cancel_registers_before_original_callback_and_preserves_exception(self):
        journal = object.__new__(FinalizationJournal)
        journal.lock = threading.RLock()
        journal.observe = lambda *args: None
        writer = EngineFinalizationWriter(journal, None)
        writer.start = SimpleNamespace(run=b'owned-run')
        runner = object.__new__(AgentRunner)
        runner._cancel_lock = threading.Lock()
        runner._cancelled = set()
        runner._acquisitions_by_job = {}
        original = RuntimeError('actual controller provider exception')
        calls = []
        def stop(unit):
            calls.append(unit)
            self.assertTrue(owner.quiescence_observation()['activeControllerCalls'])
            self.assertFalse(owner.quiescent())
            with self.assertRaises(WorldlineError):
                writer._close_acquisitions()
            raise original
        runner.systemd = SimpleNamespace(stop=stop)
        owner = _AgentAcquisition(runner, writer, 'subject')
        owner.unit = SystemdProcess(unit='owned-controller-unit', launcher=None, manager=runner.systemd)
        runner._acquisitions_by_job['owned-job'] = owner
        with self.assertRaises(RuntimeError) as error:
            runner.cancel('owned-job', 'owned-controller-unit')
        self.assertIs(error.exception, original)
        self.assertEqual(calls, ['owned-controller-unit'])
        self.assertIn('owned-job', runner._cancelled)
        self.assertEqual(owner.quiescence_observation()['activeControllerCalls'], [])

    def test_actual_owner_state_and_retention_precede_irreversible_generation_close(self):
        # This ordinary control isolates the writer lifecycle. The explicit
        # storage transport stub establishes no native or journal durability.
        journal = object.__new__(FinalizationJournal)
        journal.lock = threading.RLock()
        observed = []
        journal.observe = lambda *args: observed.append(args)
        writer = EngineFinalizationWriter(journal, None)
        writer.start = SimpleNamespace(run=b'owned-run')
        writer.invocations[('subject', 'agent')] = ('owned-invocation', {})
        owner = _AgentAcquisition(SimpleNamespace(systemd=SimpleNamespace()), writer, 'subject')
        with self.assertRaises(WorldlineError):
            writer._close_acquisitions()
        self.assertIsNone(writer._acquisition_generation)
        writer.invocation_raw(world_instance='subject', check='agent', kind='retained-control',
                              observed={'bytes': b'full raw observation'})
        owner.finish()
        writer._close_acquisitions()
        self.assertEqual(observed[-1][3], 'acquisition-generation-closed')
        frontier = list(writer._raw_events)
        with self.assertRaises(WorldlineError):
            writer.invocation_raw(world_instance='subject', check='agent', kind='late-control',
                                  observed={'bytes': b'must not enter frozen capture'})
        self.assertEqual(writer._raw_events, frontier)
        writer._require_acquisitions_closed()

    def test_generation_retains_binary_run_event_and_observation_values(self):
        # Explicit storage transport fixture; no durability/native truth claim.
        journal = object.__new__(FinalizationJournal)
        journal.lock = threading.RLock()
        retained = []
        journal.observe = lambda *args: retained.append(args)
        writer = EngineFinalizationWriter(journal, None)
        writer.start = SimpleNamespace(run=b'owned-\x00\xff-run')
        writer.invocations[('subject', 'agent')] = ('owned-invocation', {})
        owner = _AgentAcquisition(SimpleNamespace(systemd=SimpleNamespace()), writer, 'subject')
        source = {'bytes': b'full\x00\xffobservation',
                  'nested': [(b'\xfe', [b'\x00', None])]} 
        expected = {'bytes': b'full\x00\xffobservation',
                    'nested': [(b'\xfe', [b'\x00', None])]}
        writer.invocation_raw(world_instance='subject', check='agent',
                              kind='binary-raw-control', observed=source)
        source['bytes'] = b'later mutation'
        source['nested'][0][1].append(b'later nested mutation')
        self.assertEqual(writer.raw_observations['owned-invocation'][0]['observation'], expected)
        self.assertEqual(retained[-1][4]['observation'], expected)
        owner.finish()
        events = tuple(writer._raw_events)
        writer._close_acquisitions()
        generation = writer._acquisition_generation
        self.assertEqual(generation['run'], b'owned-\x00\xff-run')
        self.assertEqual(tuple(generation['rawEvents']), events)
        self.assertTrue(all(type(invocation) is bytes and type(event) is bytes
                            for invocation, event in generation['rawEvents']))
        self.assertEqual(retained[-1][3], 'acquisition-generation-closed')
        self.assertEqual(retained[-1][4], generation)
        writer._require_acquisitions_closed()

    def test_retention_refusal_does_not_close_generation(self):
        journal = object.__new__(FinalizationJournal)
        journal.lock = threading.RLock()
        original = OSError('original raw store refusal')
        def refuse(*args):
            raise original
        journal.observe = refuse
        writer = EngineFinalizationWriter(journal, None)
        writer.start = SimpleNamespace(run=b'owned-run')
        writer.invocations[('subject', 'agent')] = ('owned-invocation', {})
        with self.assertRaises(OSError) as found:
            writer.invocation_raw(world_instance='subject', check='agent', kind='raw-control',
                                  observed={'bytes': b'available despite failed persistence'})
        self.assertIs(found.exception, original)
        journal.observe = lambda *args: None
        with self.assertRaises(WorldlineError):
            writer._close_acquisitions()
        self.assertIsNone(writer._acquisition_generation)
        self.assertEqual(writer.raw_observations['owned-invocation'][0]['observation']['bytes'],
                         b'available despite failed persistence')


class ProxyOwnershipTests(unittest.TestCase):
    def test_owned_live_header_reader_is_ended_before_stop_returns(self):
        entered = threading.Event()
        original = _Handler._read_head
        def read_head(handler, client):
            entered.set()
            return original(handler, client)
        with tempfile.TemporaryDirectory(prefix='worldline-proxy-ownership-') as temporary:
            proxy = AllowlistProxy(Path(temporary) / 'proxy.sock', ())
            proxy.start()
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            try:
                with patch.object(_Handler, '_read_head', read_head):
                    client.connect(str(proxy.socket_path))
                    self.assertTrue(entered.wait(5))
                    self.assertFalse(proxy.quiescent())
                    proxy.stop()
                    self.assertTrue(proxy.quiescent())
                    self.assertFalse(any(row['alive'] for row in
                        proxy.quiescence_observation()['handlers']))
                    self.assertFalse(proxy._thread.is_alive())
                    self.assertEqual(proxy.summary()['connections'], 0)
            finally:
                client.close()
                proxy.stop()


if __name__ == '__main__':
    unittest.main()
