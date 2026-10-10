"""Source-authored ordering, persistence and process-custody regressions.

These controls require later authorized execution. They do not stand in for
the original real-kernel/resource/host suites or missing protected bootstrap.
"""
from pathlib import Path
import os
import stat
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from worldline.admission import (
    ADMITTED, RESOURCE_STATE_UNKNOWN, AdmissionAuthority, AdmissionState,
    Decision, Floors, Gate, Ledger, Reservation, ResourcePolicy,
)
from worldline.linux.private_evaluator import PrivateEvaluator
from worldline.linux.systemd import SystemdAdapter, SystemdProcess, WorkloadIdentity
from worldline.controller import RuntimeController


class AdmissionCustodyRepair(unittest.TestCase):
    def test_observation_waits_for_the_accounting_lock(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = Ledger(Path(directory))
            observing = threading.Event()
            entered = threading.Event()
            answer = []
            failures = []
            def observe():
                observing.set()
                return AdmissionState('UNKNOWN', reason='fixture unknown')
            authority = AdmissionAuthority(ledger, Floors(), observer=observe)
            def request():
                entered.set()
                try:
                    answer.append(authority.admit(workload='ordinary', policy=ResourcePolicy()))
                except BaseException as error:
                    failures.append(error)
            with ledger.locked():
                thread = threading.Thread(target=request)
                thread.start()
                self.assertTrue(entered.wait(timeout=20))
                self.assertFalse(observing.wait(timeout=0.1),
                                 'host was observed while another admission held the lock')
            thread.join(timeout=20)
            self.assertFalse(thread.is_alive())
            self.assertEqual(failures, [])
            self.assertTrue(observing.is_set())
            self.assertEqual(answer[0].outcome, RESOURCE_STATE_UNKNOWN)
            self.assertFalse(ledger.path.exists())

    def test_file_is_flushed_before_replacement_directory_is_flushed(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = Ledger(Path(directory))
            events = []
            actual_fsync = os.fsync
            def fsync(descriptor):
                events.append('directory' if stat.S_ISDIR(os.fstat(descriptor).st_mode) else 'file')
                actual_fsync(descriptor)
            row = Reservation('ordinary', 'workload', None, 0, 0, 0, 0)
            with patch('worldline.admission.os.fsync', side_effect=fsync), ledger.locked():
                ledger._store([row])
            self.assertEqual(events, ['file', 'directory'])
            self.assertEqual(ledger.outstanding(), [row])
            self.assertEqual(list(Path(directory).glob('.admission-ledger-*')), [])

    def test_file_fsync_failure_preserves_old_bytes_and_primary_over_close(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = Ledger(Path(directory))
            with ledger.locked():
                ledger._store([])
            old = ledger.path.read_bytes()
            primary = OSError('file flush failed')
            actual_fdopen = os.fdopen
            class Stream:
                def __init__(self, stream): self.stream = stream
                def write(self, value): return self.stream.write(value)
                def flush(self): return self.stream.flush()
                def fileno(self): return self.stream.fileno()
                def close(self):
                    self.stream.close()
                    raise OSError('secondary stream close failed')
            def fdopen(*args, **kwargs): return Stream(actual_fdopen(*args, **kwargs))
            with patch('worldline.admission.os.fdopen', side_effect=fdopen), \
                 patch('worldline.admission.os.fsync', side_effect=primary):
                with self.assertRaises(OSError) as caught:
                    ledger._store([Reservation('new', 'workload', None, 0, 0, 0, 0)])
            self.assertIs(caught.exception, primary)
            self.assertIn('secondary stream close failed', '\n'.join(primary.__notes__))
            self.assertEqual(ledger.path.read_bytes(), old)
            self.assertEqual(list(Path(directory).glob('.admission-ledger-*')), [])

    def test_directory_flush_failure_is_not_returned_as_success(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = Ledger(Path(directory))
            primary = OSError('directory flush failed after replacement')
            actual_fsync = os.fsync
            def fsync(descriptor):
                if stat.S_ISDIR(os.fstat(descriptor).st_mode): raise primary
                actual_fsync(descriptor)
            with patch('worldline.admission.os.fsync', side_effect=fsync):
                with self.assertRaises(OSError) as caught:
                    ledger._store([])
            self.assertIs(caught.exception, primary)
            # A replaced but unconfirmed entry remains for recovery; it is
            # neither a claimed successful reservation nor silently deleted.
            self.assertTrue(ledger.path.exists())
            self.assertEqual(list(Path(directory).glob('.admission-ledger-*')), [])

    def test_unlock_failure_cannot_replace_body_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = Ledger(Path(directory))
            locked = ledger.locked()
            primary = OSError('body write failed')
            locked.__enter__()
            with patch('worldline.admission.fcntl.flock', side_effect=OSError('unlock failed')):
                locked.__exit__(OSError, primary, None)
            self.assertIn('unlock failed', '\n'.join(primary.__notes__))
            self.assertIsNone(locked.handle)


class CheckReservationCustody(unittest.TestCase):
    def guard(self, *, attach_failure=None, release_failure=None):
        authority = SimpleNamespace(
            admit=Mock(return_value=Decision(ADMITTED, 'fixture grant', reservation_id='held')),
            attach_unit=Mock(side_effect=attach_failure),
            attach_process_identity=Mock(),
            release=Mock(side_effect=release_failure),
        )
        return Gate(authority, ResourcePolicy()).guard('check:ordinary'), authority

    def process(self, *, wait_failure=None, stop_failure=None):
        unit = 'worldline-00000000-0000-4000-8000-000000000000.service'
        manager = object.__new__(SystemdAdapter)
        manager.systemd_run = '/usr/bin/systemd-run'
        identity = WorkloadIdentity(unit, '11111111111141118111111111111111', '/fixture/' + unit)
        launcher = SimpleNamespace(returncode=None, args=[manager.systemd_run, '--user',
            '--unit=' + unit, '--pipe', '--service-type=exec', '--property=KillMode=control-group', '--', '/fixture/check'])
        def communicate(*, timeout):
            if wait_failure is not None: raise wait_failure
            launcher.returncode = 0
            return b'', b''
        launcher.communicate = Mock(side_effect=communicate)
        manager.workload_identity = Mock(return_value=identity)
        manager._show = Mock(return_value={'Id': unit, 'LoadState': 'loaded',
            'InvocationID': identity.invocation_id, 'ControlGroup': '',
            'ActiveState': 'inactive', 'SubState': 'dead', 'MainPID': '0'})
        manager.stop = Mock(side_effect=stop_failure)
        return SystemdProcess(unit, launcher, manager, launched_at_us=1)

    def test_acquired_actual_unit_is_attached_and_success_releases(self):
        guard, authority = self.guard()
        process = self.process()
        with guard:
            with guard.owned_process(process):
                authority.attach_unit.assert_called_once_with('held', process.unit)
                authority.release.assert_not_called()
                process.launcher.communicate(timeout=20)
        authority.release.assert_called_once_with('held')

    def test_unsettled_cleanup_retains_capacity_and_primary(self):
        guard, authority = self.guard()
        primary = OSError('primary examiner failure')
        process = self.process(wait_failure=OSError('wait uncertain'),
                               stop_failure=OSError('stop uncertain'))
        with self.assertRaises(OSError) as caught:
            with guard:
                with guard.owned_process(process):
                    raise primary
        self.assertIs(caught.exception, primary)
        authority.attach_unit.assert_called_once_with('held', process.unit)
        authority.release.assert_not_called()
        self.assertIn('stop uncertain', '\n'.join(primary.__notes__))
        self.assertIn('wait uncertain', '\n'.join(primary.__notes__))

    def test_attachment_failure_stops_owned_work_before_release(self):
        primary = OSError('attachment persistence failed')
        guard, authority = self.guard(attach_failure=primary)
        process = self.process()
        with self.assertRaises(OSError) as caught:
            with guard:
                with guard.owned_process(process):
                    self.fail('work result cannot be consumed after failed attachment')
        self.assertIs(caught.exception, primary)
        process.manager.stop.assert_called_once_with(process.unit)
        process.launcher.communicate.assert_called_once_with(timeout=20)
        authority.release.assert_called_once_with('held')

    def test_release_failure_preserves_existing_primary(self):
        primary = OSError('examiner report failed')
        guard, authority = self.guard(release_failure=OSError('release persistence failed'))
        with self.assertRaises(OSError) as caught:
            with guard:
                raise primary
        self.assertIs(caught.exception, primary)
        self.assertIn('release persistence failed', '\n'.join(primary.__notes__))

    def test_private_actual_acquisition_binds_before_collection(self):
        with tempfile.TemporaryDirectory() as directory:
            process = self.process()
            manager = SimpleNamespace(launch_private_evaluator=Mock(return_value=process))
            evaluator = PrivateEvaluator(manager)
            guard, authority = self.guard()
            spec = SimpleNamespace(runtime=Path(directory), run_id='run-id')
            role = SimpleNamespace(plan={})
            plan = {'helper': str(Path(directory) / 'helper.py')}
            def collect(*args, **kwargs):
                authority.attach_unit.assert_called_once_with('held', process.unit)
                authority.release.assert_not_called()
                process.launcher.communicate(timeout=20)
                return {'actual': 'collected'}
            with guard, patch.object(evaluator, '_collect_launched', side_effect=collect):
                result = evaluator._launch_and_collect(spec, plan, (), role, {}, _admission_guard=guard)
            self.assertEqual(result, {'actual': 'collected'})
            authority.release.assert_called_once_with('held')

    def test_restart_uses_the_retained_check_unit_for_liveness(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = Ledger(Path(directory))
            with ledger.locked():
                ledger._store([Reservation('held', 'check:ordinary', None, 0, 0, 0, 0)])
            authority = AdmissionAuthority(ledger, Floors())
            process = self.process()
            authority.attach_unit('held', process.unit)
            process.capture_workload_identity()
            authority.attach_process_identity('held', process.workload_identity)
            retained = Ledger(Path(directory)).outstanding()[0]
            self.assertEqual(retained.unit, process.unit)
            controller = object.__new__(RuntimeController)
            controller.systemd = process.manager
            controller.systemd.metadata = Mock(return_value={
                'state': 'CAPTURED', 'ActiveState': 'inactive'})
            def show(unit, properties):
                metadata = controller.systemd.metadata(unit)
                if metadata.get('state') != 'CAPTURED': return None
                return {'Id': unit, 'LoadState': 'loaded',
                    'InvocationID': process.workload_identity.invocation_id, 'ControlGroup': '',
                    'ActiveState': metadata.get('ActiveState'), 'SubState': 'dead', 'MainPID': '0'}
            controller.systemd._show = Mock(side_effect=show)
            self.assertIs(controller._reservation_is_live(retained), False)
            controller.systemd.metadata.assert_called_once_with(process.unit)
            controller.systemd.metadata.return_value = {'state': 'UNAVAILABLE'}
            self.assertIsNone(controller._reservation_is_live(retained))


if __name__ == '__main__':
    unittest.main()
