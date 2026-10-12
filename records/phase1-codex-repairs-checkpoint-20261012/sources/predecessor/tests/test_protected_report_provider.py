"""Additive, opt-in controls of the real isolated executor and protected provider.

Faults below change real objects/syscall preconditions, never emit an accepted
synthetic capture. Original private-evaluator controls remain enrolled unchanged.
"""
from __future__ import annotations

import base64
import contextlib
import copy
import errno
import hashlib
import json
import os
import signal
import socket
from pathlib import Path
import unittest
from unittest.mock import patch
import uuid

from test_private_evaluator import PrivateEvaluatorIntegration, _EXAMINER, _WORKER
from worldline.errors import WorldlineError
from worldline.linux.private_evaluator import PrivateEvaluationSpec, PrivateEvaluator, VERIFIER_MOUNT
from worldline.linux.protected_report_provider import ProtectedReportProvider, reference_program
from worldline.report import collect_private_report, prepare_private_report
from worldline.raw_observation import ObservationRetentionError, private_return_observation
from worldline.trusted import TRUSTED_INTERPRETER


@unittest.skipUnless(os.environ.get('WORLDLINE_PRIVATE_EVALUATOR_TEST') == '1',
                     'original real user-systemd private evaluator campaign opt-in')
class ProtectedProviderIntegration(unittest.TestCase):
    setUp = PrivateEvaluatorIntegration.setUp

    def execute(self, name, *, fault=None, expected=b'ordinary worker complete\n', observer=None):
        run = str(uuid.uuid4())
        # Both original worker and subordinate candidate actually attempt a write
        # to the examiner-only report mount; pathname absence is the kernel result.
        attack = "\ntry:\n    descriptor = os.open('/run/worldline-report/report', os.O_WRONLY | os.O_CREAT, 0o600)\nexcept FileNotFoundError:\n    pass\nelse:\n    os.close(descriptor)\n    raise AssertionError('candidate reached examiner report')\n"
        (self.source / 'worker.py').write_text(_WORKER + attack)
        script = 'EXPECTED = ' + repr(expected) + '\n' + _EXAMINER
        script = script.replace("raise SystemExit(0 if ok else 1)",
            "second = candidate.run(['/usr/bin/python3', 'worker.py'], timeout=20, principal='candidate')\n"
            "assert second.returncode == 0\nraise SystemExit(0 if ok else 1)")
        (self.verifier / 'exam.py').write_text(script)
        pins = {'exam.py': hashlib.sha256((self.verifier / 'exam.py').read_bytes()).hexdigest()}
        invocation = {'worldInstance': str(uuid.uuid4()), 'checkId': name, 'invocationId': run,
                      'candidateSnapshot': {'rootSetHash': 'fixture-frozen-input'},
                      'verifierEntries': [{'path': 'exam.py', 'sha256': pins['exam.py']}],
                      'evaluationRun': str(uuid.uuid4())}
        report = prepare_private_report(self.base, run_id=run, check_id=name,
            candidate_identity='fixture-frozen-input', verifier_identity=pins['exam.py'])
        spec = PrivateEvaluationSpec(run, {'/logical/private-check': self.source}, self.verifier,
            (TRUSTED_INTERPRETER, VERIFIER_MOUNT + '/exam.py'), '/logical/private-check', report,
            self.base / name, timeout_seconds=60, verifier_digests=pins,
            protected_invocation=invocation)
        captures = []

        def retain(kind, occurrence, record):
            captures.append({'kind': kind, 'occurrence': occurrence, 'observation': copy.deepcopy(record)})
            if observer is not None:
                observer(kind, occurrence, record)
            if fault == 'wait-signal' and record.get('kind') == 'role-startup' and record.get('roleClaim') == 'examiner':
                # Actual live peer, retained before its GO acknowledgement.
                os.kill(record['peerCredentials']['pid'], signal.SIGKILL)

        original_collect = ProtectedReportProvider.collect

        def collect(provider, result, role_observer):
            with contextlib.ExitStack() as cleanup:
                if fault == 'retained-writer':
                    fd = os.open(report / 'report', os.O_WRONLY | os.O_CLOEXEC)
                    cleanup.callback(os.close, fd)
                elif fault == 'source-move':
                    path = spec.runtime / 'verifiers' / 'exam.py'
                    os.rename(path, path.with_name('exam-held.py'))
                    path.write_bytes(b'changed source\n')
                elif fault == 'report-edge-move':
                    os.rename(report / 'report', report / 'report-held')
                    (report / 'report').write_bytes(b'changed report\n')
                elif fault == 'read-error':
                    # A genuine bad descriptor, not a fabricated byte/EOF report.
                    fd = provider.record['report']['directoryFd']
                    os.close(fd)
                    provider.handles.remove(fd)
                return original_collect(provider, result, role_observer)

        original_channel = ProtectedReportProvider.lifecycle_channel

        def channel(provider, event):
            original_channel(provider, event)
            if event.get('scope') != 'native-original-report-transfer':
                return
            if fault == 'premature-eof' and event['operation'] == 'acquire':
                with socket.socket(fileno=os.dup(event['fd'])) as connection:
                    connection.shutdown(socket.SHUT_RDWR)
            elif fault == 'shutdown-error' and event['operation'] == 'read' and event['return'] == 0:
                # The next REAL socket.shutdown and close see EBADF.
                os.close(event['fd'])

        real_memfd = os.memfd_create

        def no_sealing(name, flags):
            # Kernel supplies F_SEAL_SEAL on a non-sealable memfd; ADD_SEALS
            # subsequently fails with its actual EPERM and is retained.
            return real_memfd(name, flags & ~os.MFD_ALLOW_SEALING
                              if name == 'worldline-protected-report' else flags)

        with contextlib.ExitStack() as patches:
            patches.enter_context(patch.object(ProtectedReportProvider, 'collect', collect))
            patches.enter_context(patch.object(ProtectedReportProvider, 'lifecycle_channel', channel))
            if fault == 'seal-error':
                patches.enter_context(patch('worldline.linux.protected_report_provider.os.memfd_create', no_sealing))
            result = PrivateEvaluator(self.adapter).run(spec,
                resource_properties=('MemoryMax=1G', 'TasksMax=64', 'CPUQuota=100%', 'IOAccounting=yes'),
                _acquisition_observer=retain)
        retain('private-process-return', 0, private_return_observation(result))
        payload, metadata = collect_private_report(report, run_id=run, check_id=name,
            candidate_identity='fixture-frozen-input', verifier_identity=pins['exam.py'])
        metadata['payloadB64'] = base64.b64encode(payload).decode('ascii')
        packet = {'engineInvocationObservation': invocation, 'evaluatorBoundary': result['boundary'],
                  'protectedProviderCapture': result['protectedProviderCapture'], 'privateReport': metadata,
                  'examinerAudit': result['examinerAudit'], 'engineRawObservations': captures,
                  'supervision': result['supervision'], 'exitCode': result['exitCode']}
        destination = os.environ.get('WORLDLINE_PRIVATE_EVALUATOR_EVIDENCE')
        if destination:
            path = Path(destination)
            path.mkdir(parents=True, exist_ok=True)
            (path / (name + '-protected-capture.json')).write_text(json.dumps(packet, allow_nan=False))
        return packet

    def test_actual_complete_capture_success_and_failed_examiner_assertion(self):
        for name, expected, code in (('protected-pass', b'ordinary worker complete\n', 0),
                                    ('protected-fail-report', b'wrong expected value\n', 1)):
            with self.subTest(name=name):
                packet = self.execute(name, expected=expected)
                capture = packet['protectedProviderCapture']
                self.assertEqual(packet['exitCode'], code)
                self.assertEqual(capture['lifetime']['failures'], [])
                self.assertEqual(capture['sourceLeaseBreaks'], [])
                self.assertEqual(capture['expected']['invocation'], packet['engineInvocationObservation'])
                self.assertEqual(capture['observed']['invocation'], packet['engineInvocationObservation'])
                self.assertEqual(capture['observed']['filterProgramB64'], reference_program())
                self.assertEqual(capture['report']['reads'][-1]['return'], 0)
                self.assertEqual(capture['report']['sealed']['reads'][-1]['return'], 0)
                self.assertEqual(capture['report']['sealed']['bytes']['payload'], packet['privateReport']['payloadB64'])
                self.assertEqual(capture['report']['writerLease']['acquireReturn'], 0)
                self.assertEqual(capture['report']['writerLease']['getReturn'], 0)
                self.assertEqual(capture['report']['sealed']['sealGetReturn'] & 15, 15)
                self.assertTrue(capture['lifetime']['shutdowns'])
                self.assertTrue(all(row['return'] > 0 for row in capture['lifetime']['waits']))
                self.assertTrue(all(row['return'] > 0 for row in capture['lifetime']['deathPolls']))
                self.assertTrue(all(row['return'] == 0 for row in capture['lifetime']['closes']))
                self.assertTrue(all(row['getReturn'] == 0 for row in capture['sourceLeases']))
                # Historical startup/kernel snapshots never became protection flags.
                outcomes = [row for row in packet['evaluatorBoundary']['daemonRoleObservations']
                            if row['kind'] == 'native-lifetime-process-outcome']
                self.assertTrue(outcomes)
                self.assertTrue(all(row['protectedCustody'] is False for row in outcomes))

    def test_actual_retained_writer_and_kernel_seal_failure_are_not_protection(self):
        for fault in ('retained-writer', 'seal-error'):
            with self.subTest(fault=fault):
                packet = self.execute('protected-' + fault, fault=fault)
                capture = packet['protectedProviderCapture']
                self.assertTrue(capture['lifetime']['failures'])
                if fault == 'retained-writer':
                    self.assertIn(capture['report']['writerLease']['acquireErrno'], (errno.EAGAIN, errno.EACCES))
                else:
                    self.assertEqual(capture['report']['sealed']['addSealErrno'], errno.EPERM)

    def test_actual_source_movement_preserves_full_edge_evidence(self):
        packet = self.execute('protected-source-move', fault='source-move')
        row = next(row for row in packet['protectedProviderCapture']['sourceLeases']
                   if row['member'] == 'exam.py')
        self.assertNotEqual(row['before'], row['edgeAfter'])
        self.assertEqual(row['before']['device'], row['after']['device'])
        self.assertEqual(row['before']['inode'], row['after']['inode'])

    def test_actual_bad_directory_descriptor_retains_read_and_cleanup_failures(self):
        with self.assertRaises((WorldlineError, OSError)):
            self.execute('protected-read-error', fault='read-error')

    def test_actual_observer_retention_error_cannot_return_protected_success(self):
        def refusing(kind, occurrence, record):
            if kind == 'private-protected-provider-capture':
                raise OSError(errno.EIO, 'actual protected capture retention refusal')
        with self.assertRaises(ObservationRetentionError):
            self.execute('protected-observer-error', observer=refusing)

    def test_actual_premature_eof_and_shutdown_error_refuse_complete_custody(self):
        for fault in ('premature-eof', 'shutdown-error'):
            with self.subTest(fault=fault):
                packet = self.execute('protected-' + fault, fault=fault)
                capture = packet['protectedProviderCapture']
                self.assertTrue(capture['lifetime']['failures'])
                self.assertIsNotNone(capture['reportTransfer']['exception'])
                self.assertTrue(any(row['return'] == 0 for row in capture['lifetime']['channelReads']))

    def test_actual_child_signal_and_wait_cannot_return_protected_success(self):
        with self.assertRaises((WorldlineError, OSError)):
            self.execute('protected-wait-signal', fault='wait-signal')


if __name__ == '__main__':
    unittest.main()
