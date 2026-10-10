"""Additive native controls; original manager/restart tests remain mandatory unchanged.

Authored source-only. Fixture manager transports are not custody evidence.
"""
import unittest
import json
from unittest.mock import patch
from pathlib import Path
from types import SimpleNamespace

from worldline.linux.systemd import SystemdAdapter
from worldline.controller import RuntimeController
from worldline.manager_resource_lifecycle import capture_json, decide, pipe_capture, terminal_decide
from worldline.resource_ledger import compute_ledger
from test_admission_terminal_repair import manager_process, shown, UNIT, INVOCATION, IDENTITY


class ManagerResourceLifecycleNative(unittest.TestCase):
    def test_normal_pipe_retained_capture_replays_without_query(self):
        manager, process = manager_process(returncode=0)
        observed = manager.terminal_observation(process)
        manager._show.assert_not_called()
        self.assertEqual(observed.state, 'NORMAL_PIPE_COMPLETION')
        self.assertTrue(terminal_decide(observed.raw_capture)['accepted'])
        failed = dict(observed.raw_capture, afterFailure=True, afterFailureTruth=True)
        self.assertFalse(terminal_decide(failed)['accepted'])

    def test_original_unused_launcher_and_identity_fields_remain_unread(self):
        manager, process = manager_process(returncode=0)
        process.manager = object()
        process.launcher = SimpleNamespace(returncode=0)
        self.assertEqual(manager.terminal_observation(process).state, 'UNKNOWN')
        manager._show.assert_not_called()
        manager, process = manager_process(returncode=0)
        opaque = object()
        process.workload_identity = opaque
        observed = manager.terminal_observation(process)
        self.assertEqual(observed.state, 'NORMAL_PIPE_COMPLETION')
        self.assertIs(observed.identity, opaque)
        self.assertNotIn('identity', observed.raw_capture)
        self.assertTrue(terminal_decide(observed.raw_capture)['accepted'])
        self.assertEqual(manager.workload_identity(process), IDENTITY)
        manager._show.return_value = None
        observed = manager._workload_observation(UNIT, opaque, 1)
        self.assertEqual(observed.state, 'UNKNOWN')
        self.assertIs(observed.identity, opaque)
        process.launcher.args = []
        del process.launched_at_us
        del manager.systemd_run
        self.assertFalse(manager._owns_pipe_launcher(process))

    def test_after_failure_original_truth_protocol_and_unbounded_int(self):
        manager, process = manager_process(returncode=0)
        class OriginalTruth:
            def __init__(self):
                self.calls = 0
            def __bool__(self):
                self.calls += 1
                return False
        truth = OriginalTruth()
        observed = manager.terminal_observation(process, after_failure=truth)
        self.assertEqual(truth.calls, 1)
        self.assertEqual(observed.state, 'NORMAL_PIPE_COMPLETION')
        self.assertTrue(terminal_decide(observed.raw_capture)['accepted'])
        process.workload_identity = IDENTITY
        observed = manager.terminal_observation(process, after_failure=1 << 20000)
        self.assertEqual(observed.state, 'MANAGER_WORKLOAD_LIVE')
        self.assertEqual(observed.raw_capture['afterFailure']['hex'], hex(1 << 20000))
        process.launcher.args = []
        truth = OriginalTruth()
        self.assertEqual(manager.terminal_observation(process, after_failure=truth).state, 'UNKNOWN')
        self.assertEqual(truth.calls, 0)

    def test_actual_pipe_arguments_and_wait_type_are_not_state_flags(self):
        manager, process = manager_process(returncode=0)
        for args in ([manager.systemd_run, '--pipe'],
                     list(process.launcher.args) + ['--unit=ignored-after-separator']):
            process.launcher.args = args
            capture = pipe_capture(manager, process, returncode=0)
            result = terminal_decide(capture)
            self.assertEqual(result['accepted'], len(args) > 2)
        capture = pipe_capture(manager, process, returncode=True)
        self.assertFalse(terminal_decide(capture)['accepted'])
        capture['returncode'] = 0.0
        self.assertFalse(terminal_decide(capture)['accepted'])

    def test_unbounded_launcher_integers_never_enter_decimal_json(self):
        manager, process = manager_process(returncode=0)
        process.launched_at_us = 1 << 20000
        observed = manager.terminal_observation(process)
        self.assertEqual(observed.state, 'NORMAL_PIPE_COMPLETION')
        self.assertEqual(observed.raw_capture['launchedAtUs']['hex'], hex(1 << 20000))
        process.workload_identity = IDENTITY
        process.launcher.returncode = -(1 << 20000)
        observed = manager.terminal_observation(process)
        self.assertEqual(observed.state, 'MANAGER_WORKLOAD_LIVE')
        self.assertEqual(observed.raw_capture['returncode']['hex'], hex(-(1 << 20000)))

    def test_original_nonstring_prefix_errors_and_short_circuit_order(self):
        for value in (None, 1, False):
            manager, process = manager_process(returncode=0)
            process.launcher.args.insert(2, value)
            with self.assertRaises(AttributeError):
                manager.terminal_observation(process)
        manager, process = manager_process(returncode=0)
        process.launcher.args.insert(2, None)
        process.launcher.args.remove('--unit=' + UNIT)
        self.assertEqual(manager.terminal_observation(process).state, 'UNKNOWN')
        manager, process = manager_process(returncode=0)
        process.launcher.args.append(None)
        self.assertEqual(manager.terminal_observation(process).state, 'NORMAL_PIPE_COMPLETION')
        primary = RuntimeError('original startswith failure')
        class OriginalOption:
            def startswith(self, prefix):
                raise primary
        manager, process = manager_process(returncode=0)
        process.launcher.args.insert(2, OriginalOption())
        with self.assertRaises(RuntimeError) as caught:
            manager.terminal_observation(process)
        self.assertIs(caught.exception, primary)

    def test_canonical_uuid_and_complete_posix_path_domain(self):
        for prefix in ('/', '//', '/a/', '/é/', '/a\x00b/'):
            value = {'unit': UNIT, 'invocationId': INVOCATION, 'controlGroup': prefix + UNIT}
            self.assertIsNotNone(SystemdAdapter.persisted_workload_identity(UNIT, value))
        for group in ('///' + UNIT, '/a//'+UNIT, '/a/./'+UNIT, '/a/../'+UNIT,
                      '/' + UNIT + '/', UNIT):
            value = {'unit': UNIT, 'invocationId': INVOCATION, 'controlGroup': group}
            self.assertIsNone(SystemdAdapter.persisted_workload_identity(UNIT, value))
        for invocation in ('0'*32, 'A' + INVOCATION[1:], '11111111-1111-4111-8111-111111111111'):
            value = {'unit': UNIT, 'invocationId': invocation, 'controlGroup': IDENTITY.control_group}
            self.assertIsNone(SystemdAdapter.persisted_workload_identity(UNIT, value))

    def test_ascii_events_grammar_and_precedence_from_retained_adapter(self):
        manager, process = manager_process(returncode=-9)
        process.workload_identity = IDENTITY
        manager._show.return_value = shown(active='inactive', group='')
        for events, expected in (
            ('populated\t0\nfrozen 000\n', 'MANAGER_CGROUP_EMPTY'),
            ('populated 0\vfrozen 0\f', 'MANAGER_CGROUP_EMPTY'),
            ('populated 0\x1cfrozen 0\x1d', 'MANAGER_CGROUP_EMPTY'),
            ('populated\x1f0\n', 'MANAGER_CGROUP_EMPTY'),
            ('populated 00\n', 'UNKNOWN'), ('populated 1\n', 'UNKNOWN'),
            ('populated 0\npopulated 0\n', 'UNKNOWN'), ('\n', 'UNKNOWN'),
            ('populated +0\n', 'UNKNOWN'), ('populated 0 extra\n', 'UNKNOWN')):
            with self.subTest(events=events), patch.object(Path, 'read_text', return_value=events):
                observed = manager.terminal_observation(process, after_failure=True)
                self.assertEqual(observed.state, expected)
                self.assertEqual(terminal_decide(observed.raw_capture)['state'], expected)
        manager._show.return_value = shown(active='inactive', invocation='2'*32)
        with patch.object(Path, 'read_text', side_effect=AssertionError('conflict must not read events')):
            self.assertEqual(manager.terminal_observation(process).state, 'CONFLICT')

    def test_directory_missing_is_distinct_from_missing_events(self):
        manager, process = manager_process(returncode=1)
        process.workload_identity = IDENTITY
        manager._show.return_value = shown(active='inactive', group='')
        with patch.object(Path, 'read_text', side_effect=FileNotFoundError('events')), \
             patch.object(Path, 'lstat', side_effect=FileNotFoundError('directory')):
            observed = manager.terminal_observation(process)
        self.assertEqual(observed.state, 'MANAGER_CGROUP_REMOVED')
        self.assertTrue(terminal_decide(observed.raw_capture)['accepted'])
        with patch.object(Path, 'read_text', side_effect=PermissionError('original')):
            with self.assertRaises(PermissionError): manager.terminal_observation(process)

    def test_restart_usage_exact_original_identity_equality(self):
        identity = {'unit': UNIT, 'invocationId': INVOCATION, 'controlGroup': IDENTITY.control_group}
        capture = {'op': 'usage', 'unit': UNIT, 'workload': 'check:ordinary', 'identity': identity,
                   'reading': {'state': 'OBSERVED', 'currentMemoryBytes': 13, 'workloadIdentity': dict(identity)}}
        self.assertEqual(decide(capture)['value'], 13)
        capture['reading']['workloadIdentity']['extra'] = 1
        self.assertIsNone(decide(capture)['value'])
        capture['workload'] = 'ordinary'
        self.assertEqual(decide(capture)['value'], 13)
        capture['reading']['state'] = 'UNAVAILABLE'
        self.assertIsNone(decide(capture)['value'])

    def test_restart_usage_full_magnitude_and_unrelated_capture_fields(self):
        quantity = 1 << 20000
        reading = {'state': 'OBSERVED', 'currentMemoryBytes': quantity,
                   'unrelated': {'positive': quantity, 'negative': -quantity, 'nested': [quantity]}}
        capture = {'op': 'usage', 'unit': UNIT, 'workload': 'ordinary', 'reading': reading}
        self.assertEqual(decide(capture)['value'], quantity)
        controller = object.__new__(RuntimeController)
        controller.systemd = SimpleNamespace(resource_telemetry=lambda unit: reading)
        row = SimpleNamespace(unit=UNIT, workload='ordinary', workload_identity=None)
        self.assertEqual(controller._reservation_usage(row), quantity)
        identity = {'unit': UNIT, 'invocationId': INVOCATION, 'controlGroup': IDENTITY.control_group}
        reading['workloadIdentity'] = dict(identity)
        row.workload = 'check:ordinary'
        row.workload_identity = identity
        self.assertEqual(controller._reservation_usage(row), quantity)
        reading['workloadIdentity']['invocationId'] = 'conflict'
        self.assertIsNone(controller._reservation_usage(row))

    def test_scalar_subclasses_preserve_original_json_base_protocols(self):
        def forbidden(*args, **kwargs):
            raise AssertionError('scalar formatting/metaclass override must remain unused')
        class NoisyMeta(type):
            def __getattribute__(cls, name):
                if name in ('__mro__', '__name__', '__qualname__', '__module__'):
                    return forbidden()
                return type.__getattribute__(cls, name)
            __eq__ = forbidden
        class Quantity(int, metaclass=NoisyMeta):
            __int__ = forbidden
            __index__ = forbidden
            __repr__ = forbidden
            __str__ = forbidden
            __lt__ = forbidden
            __abs__ = forbidden
            __divmod__ = forbidden
        class Measurement(float, metaclass=NoisyMeta):
            __float__ = forbidden
            __repr__ = forbidden
            __str__ = forbidden
            __eq__ = forbidden
        class Text(str, metaclass=NoisyMeta):
            __str__ = forbidden
            __repr__ = forbidden
        ordinary = {'state': Text('OBSERVED'), 'currentMemoryBytes': Quantity(13),
                    'nested': [Text('value'), Measurement(13.5)]}
        self.assertEqual(capture_json(ordinary),
                         json.dumps(ordinary, ensure_ascii=True, separators=(',', ':')))
        quantity = Quantity(1 << 20000)
        ordinary['currentMemoryBytes'] = quantity
        ordinary['nested'].append(quantity)
        controller = object.__new__(RuntimeController)
        controller.systemd = SimpleNamespace(resource_telemetry=lambda unit: ordinary)
        row = SimpleNamespace(unit=UNIT, workload='ordinary', workload_identity=None)
        self.assertEqual(controller._reservation_usage(row), 1 << 20000)
        value = {'unit': Text(UNIT), 'invocationId': Text(INVOCATION),
                 'controlGroup': Text(IDENTITY.control_group)}
        restored = SystemdAdapter.persisted_workload_identity(Text(UNIT), value)
        self.assertIsNotNone(restored)
        self.assertIs(restored.invocation_id, value['invocationId'])
        self.assertIs(restored.control_group, value['controlGroup'])

    def test_json_keys_duplicates_and_original_key_value_error_order(self):
        class IndependentText(str):
            def __hash__(self):
                return object.__hash__(self)
            def __eq__(self, other):
                return self is other
            def __str__(self):
                raise AssertionError('C JSON does not invoke custom string conversion')
        first, second = IndependentText('same'), IndependentText('same')
        tree = {first: 1, second: 2, 3: 'integer key', 4.5: 'float key',
                True: 'boolean key', None: 'null key'}
        encoded = capture_json(tree)
        self.assertEqual(encoded, json.dumps(tree, ensure_ascii=True, separators=(',', ':')))
        self.assertEqual(encoded.count('\"same\":'), 2)
        primary = RuntimeError('original unsupported-value default error')
        class Unsupported:
            @property
            def __class__(self):
                raise primary
        tree = {'first': Unsupported(), object(): 1}
        for encoder in (capture_json, json.dumps):
            with self.assertRaises(RuntimeError) as caught:
                encoder(tree)
            self.assertIs(caught.exception, primary)
        with self.assertRaises(TypeError):
            capture_json({object(): 1})

    def test_original_usage_object_reaches_ledger_int_protocol_once(self):
        conversions = []
        class Quantity(int):
            def __int__(self):
                conversions.append(self)
                return 100
        original = Quantity(13)
        reading = {'state': 'OBSERVED', 'currentMemoryBytes': original,
                   'unrelated': [original]}
        controller = object.__new__(RuntimeController)
        controller.systemd = SimpleNamespace(resource_telemetry=lambda unit: reading)
        row = SimpleNamespace(unit=UNIT, workload='ordinary', workload_identity=None)
        used = controller._reservation_usage(row)
        self.assertIs(used, original)
        self.assertEqual(conversions, [])
        self.assertEqual(decide({'op': 'usage', 'unit': UNIT, 'workload': 'ordinary',
                                 'reading': reading})['action'], 'select_current_memory')
        self.assertEqual(conversions, [])
        projection = compute_ledger([(150, used)])
        self.assertEqual(projection.total, 50)
        self.assertEqual(projection.withheld, (50,))
        self.assertEqual(len(conversions), 1)
        self.assertIs(conversions[0], original)

    def test_original_usage_int_exception_reaches_ledger_unchanged(self):
        conversions = []
        primary = RuntimeError('original quantity __int__ failed')
        class Quantity(int):
            def __int__(self):
                conversions.append(self)
                raise primary
        original = Quantity(13)
        reading = {'state': 'OBSERVED', 'currentMemoryBytes': original}
        controller = object.__new__(RuntimeController)
        controller.systemd = SimpleNamespace(resource_telemetry=lambda unit: reading)
        row = SimpleNamespace(unit=UNIT, workload='ordinary', workload_identity=None)
        used = controller._reservation_usage(row)
        self.assertIs(used, original)
        self.assertEqual(conversions, [])
        with self.assertRaises(RuntimeError) as caught:
            compute_ledger([(150, used)])
        self.assertIs(caught.exception, primary)
        self.assertEqual(len(conversions), 1)
        self.assertIs(conversions[0], original)

    def test_restart_replays_retained_raw_manager_and_identity_joins(self):
        manager, process = manager_process(returncode=1)
        process.workload_identity = IDENTITY
        manager._show.return_value = shown(active='inactive', group='')
        with patch.object(Path, 'read_text', return_value='populated 0\n'):
            observed = manager.terminal_observation(process)
        identity = {'unit': UNIT, 'invocationId': INVOCATION, 'controlGroup': IDENTITY.control_group}
        capture = {'op': 'live', 'unit': UNIT, 'workload': 'check:ordinary',
                   'identity': identity, 'observationType': True,
                   'reading': {'unit': observed.unit, 'state': observed.state, 'identity': dict(identity)},
                   'terminalCapture': dict(observed.raw_capture)}
        self.assertIs(decide(capture)['live'], False)
        capture['terminalCapture']['shown'] = shown()
        self.assertIsNone(decide(capture)['live'])
        capture['reading']['state'] = 'MANAGER_WORKLOAD_LIVE'
        self.assertIs(decide(capture)['live'], True)
        capture['reading']['identity']['invocationId'] = 'conflict'
        self.assertIsNone(decide(capture)['live'])
        capture['reading']['identity'] = dict(identity)
        capture['reading']['state'] = 'MANAGER_CGROUP_EMPTY'
        capture['terminalCapture']['shown'] = shown(active='inactive', group='')
        capture['terminalCapture']['events'] = 'populated 1\n'
        self.assertIsNone(decide(capture)['live'])
        capture['terminalCapture'] = None
        self.assertIsNone(decide(capture)['live'])

    def test_restart_manager_three_way_preserves_unknown_capacity(self):
        for state, expected in ((None, None), ('', None), ('active', True), ('activating', True),
                                ('reloading', True), ('deactivating', True), ('inactive', False),
                                ('failed', False), ('unrecognized', False)):
            capture = {'op': 'live', 'unit': UNIT, 'workload': 'ordinary',
                       'reading': {'state': 'CAPTURED', 'ActiveState': state}}
            self.assertIs(decide(capture)['live'], expected)
        self.assertIs(decide({'op': 'live', 'unit': None})['live'], True)


if __name__ == '__main__':
    unittest.main()
