"""Authored controls for actual collector cleanup and manager/cgroup uncertainty.

Not executed in the source-only repair lane. Mock host transports exercise
the real adapter/collector/guard branches; they establish no protected custody.
Original frozen suites, fixtures, native predicates and proof floors remain required.
"""
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from worldline.admission import (ADMITTED, RESOURCES_UNAVAILABLE, AdmissionAuthority, AdmissionState,
    Decision, Floors, Gate, Ledger, Reservation, ResourcePolicy)
from worldline.controller import RuntimeController
from worldline.errors import WorldlineError
from worldline.linux.private_evaluator import BackendFailure, PrivateEvaluator
from worldline.linux.systemd import SystemdAdapter, SystemdProcess, WorkloadIdentity


UNIT = 'worldline-00000000-0000-4000-8000-000000000000.service'
INVOCATION = '11111111111141118111111111111111'
IDENTITY = WorkloadIdentity(UNIT, INVOCATION, '/fixture/' + UNIT)


def shown(*, active='active', invocation=INVOCATION, loaded='loaded', group=IDENTITY.control_group):
    return {'Id': UNIT, 'LoadState': loaded, 'InvocationID': invocation, 'ControlGroup': group,
            'ActiveState': active, 'SubState': 'running' if active == 'active' else 'dead',
            'MainPID': '10' if active == 'active' else '0'}


def manager_process(*, returncode=None, stop_failure=None, communicate=None):
    manager = object.__new__(SystemdAdapter)
    manager.systemd_run = '/usr/bin/systemd-run'
    manager._show = Mock(return_value=shown())
    manager.stop = Mock(side_effect=stop_failure)
    launcher = SimpleNamespace(args=[manager.systemd_run, '--user', '--unit=' + UNIT,
        '--pipe', '--service-type=exec', '--property=KillMode=control-group', '--', '/fixture/check'],
        returncode=returncode, poll=Mock(return_value=returncode))
    if communicate is None:
        def communicate(*, timeout):
            launcher.returncode = 0
            return b'', b''
    launcher.communicate = Mock(side_effect=communicate)
    process = SystemdProcess(UNIT, launcher, manager, launched_at_us=1)
    manager.launch_private_evaluator = Mock(return_value=process)
    return manager, process


def guard():
    authority = SimpleNamespace(admit=Mock(return_value=Decision(ADMITTED, 'transport fixture', reservation_id='held')),
        attach_unit=Mock(), attach_process_identity=Mock(), release=Mock())
    return Gate(authority, ResourcePolicy()).guard('check:ordinary'), authority


class ActualPrivateCollectionCleanup(unittest.TestCase):
    def launch_failure(self, *, stop_error=None, wait_error=None):
        primary = OSError('original bootstrap collection error')
        manager, process = manager_process(stop_failure=stop_error,
            communicate=(lambda **kwargs: (_ for _ in ()).throw(wait_error)) if wait_error is not None else None)
        actual_show = manager._show
        def show(unit, properties):
            if 'NoNewPrivileges' in properties:
                return {'NoNewPrivileges': 'no', 'MainPID': '10', 'ControlGroup': IDENTITY.control_group}
            return actual_show(unit, properties)
        manager._show = Mock(side_effect=show)
        evaluator = PrivateEvaluator(manager)
        admitted, authority = guard()
        with tempfile.TemporaryDirectory() as directory:
            runtime = Path(directory)
            (runtime / 'bootstrap-ready').write_text('ready')
            spec = SimpleNamespace(runtime=runtime, run_id='run', timeout_seconds=1)
            role = SimpleNamespace(plan={'bootstrapDeadlineMonotonic': float('inf')},
                                   arm=Mock(side_effect=primary))
            with self.assertRaises(OSError) as caught, admitted:
                evaluator._launch_and_collect(spec, {'helper': str(runtime / 'helper')}, (), role, {},
                                              _admission_guard=admitted)
        self.assertIs(caught.exception, primary)
        manager.stop.assert_called_once_with(UNIT)
        process.launcher.communicate.assert_called_once_with(timeout=20)
        authority.release.assert_not_called()
        return primary

    def test_failed_stop_cannot_replace_primary_or_skip_wait(self):
        primary = self.launch_failure(stop_error=OSError('stop transport failed'))
        self.assertIn('stop transport failed', '\n'.join(primary.__notes__))

    def test_failed_wait_cannot_replace_primary(self):
        primary = self.launch_failure(wait_error=OSError('terminal wait failed'))
        self.assertIn('terminal wait failed', '\n'.join(primary.__notes__))

    def test_both_cleanup_errors_are_attached_to_original(self):
        primary = self.launch_failure(stop_error=OSError('stop transport failed'),
                                      wait_error=OSError('terminal wait failed'))
        self.assertIn('stop transport failed', '\n'.join(primary.__notes__))
        self.assertIn('terminal wait failed', '\n'.join(primary.__notes__))

    def test_timeout_normalization_keeps_timeout_and_cleanup_errors_as_cause(self):
        primary = subprocess.TimeoutExpired('/fixture/check', 1)
        calls = []
        def communicate(*, timeout):
            calls.append(timeout)
            if len(calls) == 1: raise primary
            raise OSError('cleanup wait failed')
        manager, process = manager_process(stop_failure=OSError('cleanup stop failed'), communicate=communicate)
        base_show = manager._show
        manager._show = Mock(side_effect=lambda unit, properties: (
            {'NoNewPrivileges': 'no', 'MainPID': '10', 'ControlGroup': IDENTITY.control_group}
            if 'NoNewPrivileges' in properties else base_show(unit, properties)))
        evaluator = PrivateEvaluator(manager)
        admitted, authority = guard()
        with tempfile.TemporaryDirectory() as directory:
            runtime = Path(directory)
            (runtime / 'bootstrap-ready').write_text('ready')
            spec = SimpleNamespace(runtime=runtime, run_id='run', timeout_seconds=1)
            role = SimpleNamespace(plan={'bootstrapDeadlineMonotonic': float('inf')}, arm=Mock())
            def run(*args, **kwargs):
                return evaluator._launch_and_collect(spec, {'helper': str(runtime / 'helper')}, (), role, {},
                                                     _admission_guard=admitted)
            with patch.object(evaluator, '_run', side_effect=run), self.assertRaises(WorldlineError) as caught, admitted:
                evaluator.run(spec, _admission_guard=admitted)
        self.assertEqual(caught.exception.code, 'PRIVATE_EVALUATOR_TIMEOUT')
        self.assertIsInstance(caught.exception.__cause__, BackendFailure)
        self.assertIs(caught.exception.__cause__.__cause__, primary)
        self.assertIn('cleanup stop failed', '\n'.join(primary.__notes__))
        self.assertIn('cleanup wait failed', '\n'.join(primary.__notes__))
        self.assertEqual(calls, [21, 20])
        authority.release.assert_not_called()

    def test_direct_normal_collection_without_optional_guard_keeps_interface(self):
        manager, process = manager_process()
        manager._show.return_value = {'NoNewPrivileges': 'no', 'MainPID': '10',
                                     'ControlGroup': IDENTITY.control_group}
        manager.outcome = Mock(return_value={'kind': 'SUPERVISED'})
        evaluator = PrivateEvaluator(manager)
        evaluator._audit_copy = Mock(return_value={'audit': 'after'})
        with tempfile.TemporaryDirectory() as directory:
            runtime = Path(directory)
            (runtime / 'bootstrap-ready').write_text('ready')
            (runtime / 'boundary.json').write_text('{}')
            spec = SimpleNamespace(runtime=runtime, run_id='run', timeout_seconds=1,
                                   report_directory=runtime / 'report')
            role = SimpleNamespace(plan={'bootstrapDeadlineMonotonic': float('inf')},
                                   arm=Mock(), finish=Mock(return_value=[]))
            result = evaluator._collect_launched(spec, process, role, {})
        self.assertEqual(result['exitCode'], 0)
        self.assertEqual(result['stdout'], b'')
        self.assertEqual(result['supervision'], {'kind': 'SUPERVISED'})


class ActualTerminalObservation(unittest.TestCase):
    def test_normal_owned_pipe_success_preserves_release_once(self):
        manager, process = manager_process()
        admitted, authority = guard()
        with admitted:
            with admitted.owned_process(process):
                process.launcher.communicate(timeout=20)
        admitted.release()
        authority.release.assert_called_once_with('held')

    def test_failed_stop_with_terminal_launcher_and_live_unit_retains(self):
        for returncode in (-9, 1, 0):
            with self.subTest(returncode=returncode):
                manager, process = manager_process(returncode=returncode, stop_failure=OSError('stop failed'))
                # Terminal launcher status is unchanged through the wait; the
                # actual matching manager unit remains active.
                process.launcher.communicate.side_effect = lambda **kwargs: (b'', b'')
                admitted, authority = guard()
                primary = OSError('collection failed')
                with self.assertRaises(OSError) as caught, admitted:
                    with admitted.owned_process(process): raise primary
                self.assertIs(caught.exception, primary)
                authority.release.assert_not_called()
                process.launcher.communicate.assert_called_once_with(timeout=20)

    def test_nonzero_unknown_missing_or_conflicting_completion_retains(self):
        for terminal in (None, {}, shown(active='inactive', invocation='22222222222242228222222222222222'),
                         shown(active='inactive', loaded='not-found')):
            with self.subTest(terminal=terminal):
                manager, process = manager_process(returncode=1)
                process.workload_identity = IDENTITY
                manager._show.return_value = terminal
                self.assertIn(manager.terminal_observation(process).state, ('UNKNOWN', 'CONFLICT'))

    def test_failed_stop_with_terminal_launcher_and_unavailable_unit_retains(self):
        manager, process = manager_process(returncode=1, stop_failure=OSError('stop failed'))
        process.launcher.communicate.side_effect = lambda **kwargs: (b'', b'')
        manager._show.side_effect = [shown(), None, None]
        admitted, authority = guard()
        primary = OSError('original collection failure')
        with self.assertRaises(OSError) as caught, admitted:
            with admitted.owned_process(process): raise primary
        self.assertIs(caught.exception, primary)
        authority.release.assert_not_called()

    def test_terminal_manager_does_not_override_populated_or_unreadable_cgroup(self):
        manager, process = manager_process(returncode=-9)
        process.workload_identity = IDENTITY
        manager._show.return_value = shown(active='inactive', group='')
        with patch.object(Path, 'read_text', return_value='populated 1\nfrozen 0\n'):
            self.assertEqual(manager.terminal_observation(process, after_failure=True).state, 'UNKNOWN')
        with patch.object(Path, 'read_text', side_effect=PermissionError('cgroup unavailable')):
            admitted, authority = guard()
            with admitted:
                admitted._release_deferred = True
                admitted.process_settled(process, after_failure=True)
            authority.release.assert_not_called()

    def test_matching_terminal_manager_and_empty_cgroup_support_cleanup_release(self):
        manager, process = manager_process(returncode=-9)
        process.workload_identity = IDENTITY
        manager._show.return_value = shown(active='inactive', group='')
        with patch.object(Path, 'read_text', return_value='populated 0\nfrozen 0\n'):
            observation = manager.terminal_observation(process, after_failure=True)
        self.assertEqual(observation.state, 'MANAGER_CGROUP_EMPTY')
        self.assertEqual(observation.identity, IDENTITY)

    def test_missing_cgroup_events_with_existing_directory_is_unknown(self):
        manager, process = manager_process(returncode=1)
        process.workload_identity = IDENTITY
        manager._show.return_value = shown(active='inactive', group='')
        with patch.object(Path, 'read_text', side_effect=FileNotFoundError('events missing')), \
             patch.object(Path, 'lstat', return_value=object()):
            self.assertEqual(manager.terminal_observation(process).state, 'UNKNOWN')

    def test_unknown_launcher_identity_does_not_use_zero_returncode(self):
        manager, process = manager_process(returncode=0)
        process.launcher.args = ['/fixture/unrelated-launcher']
        self.assertEqual(manager.terminal_observation(process).state, 'UNKNOWN')


class RestartAccountingCustody(unittest.TestCase):
    def reservation(self, identity=True):
        return Reservation('held', 'check:ordinary', UNIT, 1, 0, 0, 0,
            {'unit': UNIT, 'invocationId': INVOCATION, 'controlGroup': IDENTITY.control_group} if identity else None)

    def test_persisted_actual_identity_round_trips_without_changing_original_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = Ledger(Path(directory))
            original = Reservation('original', 'ordinary', None, 0, 0, 0, 0)
            with ledger.locked(): ledger._store([original, self.reservation(False)])
            ledger.attach_process_identity('held', IDENTITY)
            restored = Ledger(Path(directory)).outstanding()
            self.assertEqual(restored[0].as_dict(), original.as_dict())
            self.assertEqual(restored[1], self.reservation())

    def test_restart_missing_unknown_conflicting_unit_does_not_drop_or_credit(self):
        manager, _ = manager_process()
        controller = object.__new__(RuntimeController)
        controller.systemd = manager
        manager.resource_telemetry = Mock(return_value={'state': 'OBSERVED', 'currentMemoryBytes': 1,
            'workloadIdentity': {'unit': UNIT, 'invocationId': 'conflict', 'controlGroup': IDENTITY.control_group}})
        for row, terminal in ((self.reservation(False), shown(active='inactive')),
                              (self.reservation(), None), (self.reservation(), {}),
                              (self.reservation(), shown(active='inactive', invocation='22222222222242228222222222222222'))):
            with self.subTest(row=row, terminal=terminal):
                manager._show.return_value = terminal
                self.assertIsNone(controller._reservation_is_live(row))
                self.assertIsNone(controller._reservation_usage(row))

    def test_restart_matching_terminal_identity_and_empty_cgroup_is_dead(self):
        manager, _ = manager_process()
        manager._show.return_value = shown(active='inactive', group='')
        controller = object.__new__(RuntimeController)
        controller.systemd = manager
        with patch.object(Path, 'read_text', return_value='populated 0\nfrozen 0\n'):
            self.assertIs(controller._reservation_is_live(self.reservation()), False)

    def test_actual_admit_report_and_native_reconcile_keep_unknown_check_capacity(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = Ledger(Path(directory))
            with ledger.locked(): ledger._store([self.reservation()])
            manager, _ = manager_process()
            manager._show.return_value = {}
            controller = object.__new__(RuntimeController)
            controller.systemd = manager
            manager.resource_telemetry = Mock(return_value={'state': 'OBSERVED', 'currentMemoryBytes': 1,
                'workloadIdentity': {'unit': UNIT, 'invocationId': 'unknown', 'controlGroup': IDENTITY.control_group}})
            observer = lambda: AdmissionState('OBSERVED', mem_total_bytes=1, mem_available_bytes=1,
                swap_free_bytes=0, memory_pressure_hundredths=0, cpu_pressure_hundredths=0,
                io_pressure_hundredths=0, disk={})
            authority = AdmissionAuthority(ledger, Floors(min_free_memory_bytes=0), observer=observer,
                is_live=controller._reservation_is_live, usage=controller._reservation_usage)
            policy = ResourcePolicy(memory_max_bytes=1)
            decision = authority.admit(workload='next', policy=policy)
            self.assertEqual(decision.outcome, RESOURCES_UNAVAILABLE)
            self.assertEqual(decision.arithmetic['outstandingCount'], 1)
            self.assertEqual(authority.report(policy)['withheldBytes'], 1)
            self.assertEqual(authority.reconcile(), [])
            self.assertEqual(Ledger(Path(directory)).outstanding(), [self.reservation()])


if __name__ == '__main__':
    unittest.main()
