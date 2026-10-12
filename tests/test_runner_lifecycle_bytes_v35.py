"""UNRUN source controls for the selected native lossless borrowed ABI.

No native decision is mocked. Fixtures retain original arbitrary magnitudes,
binary64 payloads, surrogatepass strings, subclass strings, tuples and bytes.
"""
from __future__ import annotations

import math
import struct
import unittest

from worldline.core import Core
from worldline.evaluation_policy import acquisitions_closed
from worldline.runner import _timer_capture
from worldline.runner_lifecycle import allowed, membership_capture


class BorrowedLifecycleNativeV35(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = Core.shared()

    def owner(self, **changes):
        result = dict(activeControllerCalls=[], cleanupStarted=True,
            controllerCallsAfterClosure=[], guardPresent=False,
            launcherPresent=False, proxyPresent=False, samplerAlive=False,
            streamEofObserved=None, streams=[], tailDrains=[], timerAlive=False,
            unclosedCommands=[], threadErrors=[])
        result.update(changes)
        return result

    def gate(self, action, value):
        return allowed(action, value, core=self.core)

    def test_full_original_value_codec_not_json_projection(self):
        class Text(str):
            pass
        actual = self.owner(retainedOriginal={
            'positive': 1 << 20000, 'negative': -(1 << 20000),
            'values': (b'\x00\xff', [Text('surrogate\ud800'), -0.0,
                float('inf'), float('-inf'), float('nan')]),
            Text('subclass-key'): Text('subclass-value')})
        self.assertTrue(self.gate('quiescent', actual))
        self.assertTrue(self.gate('finished', actual))
        self.assertTrue(acquisitions_closed(self.core, None, [actual], []))
        actual['controllerCallsAfterClosure'] = [{'callbackReturned': True,
            'exception': 'complete original post-closure failure'}]
        self.assertFalse(acquisitions_closed(self.core, None, [actual], []))

    def test_native_cleanup_action_plan_and_owned_rosters(self):
        owner = self.owner(launcherPresent=True, launcherWaitObserved=True,
            launcherStreamsClosed=True, launcherStreams=[{'present': True, 'closed': True}],
            guardPresent=True, guardReleased=False, guardReleaseAttempted=False,
            launcherCleanupAttempted=False, managerAttempted=False,
            guardReleaseReturnObserved=True, guardOwned=False,
            streamEofObserved={'stdout': True, 'stderr': True})
        for action in ('quiescent', 'drain-tails', 'close-streams', 'release-guard',
                       'observe-manager', 'streams-closed', 'guard-released'):
            with self.subTest(action=action):
                self.assertTrue(self.gate(action, owner))
        self.assertFalse(self.gate('finished', owner))
        self.assertFalse(self.gate('stop-launcher', owner))
        owner['launcherWaitObserved'] = False
        self.assertTrue(self.gate('stop-launcher', owner))
        self.assertFalse(self.gate('drain-tails', owner))
        owner.update(launcherWaitObserved=True, guardReleased=True)
        self.assertTrue(self.gate('finished', owner))
        self.assertTrue(self.gate('forget-owner', owner))
        owner['streams'] = [{'alive': False}, {'alive': True}]
        self.assertFalse(self.gate('quiescent', owner))
        self.assertFalse(self.gate('close-streams', owner))
        self.assertFalse(self.gate('release-guard', owner))

    def test_original_proxy_command_and_cancellation_observations(self):
        proxy = {'stopping': True, 'listenerAlive': False,
            'handlers': [{'alive': False}], 'sockets': [{'fileno': -1}, {'fileno': -1}]}
        self.assertTrue(self.gate('proxy-ended', proxy))
        proxy['sockets'][1]['fileno'] = 7
        self.assertFalse(self.gate('proxy-ended', proxy))
        command = dict(processCreatedObserved=True, processWaitReturnObserved=True,
            processWaitReturncode=1 << 20000, stdoutReachedEof=True, stderrReachedEof=True)
        self.assertTrue(self.gate('command-ended', command))
        self.assertTrue(self.gate('cancellation-complete', command))
        command['stderrReachedEof'] = False
        self.assertFalse(self.gate('command-ended', command))
        self.assertFalse(self.gate('cancellation-complete', command))
        self.assertTrue(self.gate('command-ended', {'processCreatedObserved': False,
            'processCreateException': 'actual original failed acquisition'}))

    def test_world_action_order_and_complete_thread_errors(self):
        self.assertTrue(self.gate('query-publication', {'worldState': 'VALID'}))
        self.assertTrue(self.gate('query-publication', {'worldState': 'DEGRADED'}))
        self.assertTrue(self.gate('recover-run', {'worldState': 'FINALIZING'}))
        self.assertTrue(self.gate('recover-run', {'worldState': 'VALID', 'publicationPending': (b'x',)}))
        self.assertFalse(self.gate('recover-run', {'worldState': 'VALID', 'publicationPending': -0.0}))
        self.assertTrue(self.gate('start-run', {'worldState': 'MUTABLE'}))
        errors = ['actual complete error', 'actual duplicate error', 'actual duplicate error']
        self.assertTrue(self.gate('mark-world-dead', {'worldState': 'MUTABLE', 'threadErrors': errors}))
        self.assertTrue(self.gate('mark-job-dead', {'threadErrors': errors}))
        self.assertFalse(self.gate('mark-world-dead', {'worldState': 'VALID', 'threadErrors': errors}))
        self.assertFalse(self.gate('mark-job-dead', {'threadErrors': []}))

    def test_membership_and_exact_controller_type_identity(self):
        captured = membership_capture({'other', 'requested'}, 'requested', core=self.core)
        self.assertTrue(self.gate('membership', captured))
        self.assertFalse(self.gate('capture-membership-protocol', captured))
        self.assertTrue(self.gate('stopped', {'stopMembership': {'cancelled': captured,
            'timedOut': membership_capture(set(), 'requested', core=self.core)}}))
        class Foreign:
            def __contains__(self, requested):
                self.requested = requested
                return True
            def __iter__(self):
                return iter(())
        requested = object()
        foreign = Foreign()
        observed = membership_capture(foreign, requested, core=self.core)
        self.assertIs(foreign.requested, requested)
        self.assertTrue(self.gate('membership', observed))
        route = dict(ownerPresent=True, ownerUnitType=id(Foreign), systemdProcessType=id(Foreign),
            requestedType=id(str), stringType=id(str), ownerUnitNameType=id(str),
            ownerUnitName='exact-unit', requestedUnit='exact-unit')
        self.assertTrue(self.gate('route-controller', route))
        route['requestedType'] = id(Foreign)
        self.assertFalse(self.gate('route-controller', route))

    def test_original_timer_full_int_binary64_and_requested_protocol(self):
        for value in (None, False, 0, -(1 << 20000), 0.0, -0.0,
                      float('-inf'), float('nan')):
            with self.subTest(value=value):
                self.assertFalse(self.gate('activate-timer', _timer_capture(value, core=self.core)))
        for value in (True, 1 << 20000, math.ulp(0.0), 1.0, float('inf')):
            with self.subTest(value=value):
                self.assertTrue(self.gate('activate-timer', _timer_capture(value, core=self.core)))
        for value in (0.0, -0.0, math.ulp(0.0), 1.0, float('inf'), float('-inf'), float('nan')):
            with self.subTest(hex=value.hex()):
                self.assertEqual(self.gate('activate-timer',
                    {'timeoutType': 'float', 'timeoutFloatHex': value.hex()}), value > 0)
        nan = struct.unpack('>d', bytes.fromhex('7ff0000000000001'))[0]
        self.assertFalse(self.gate('activate-timer', _timer_capture(nan, core=self.core)))
        class Timer:
            def __gt__(self, operand):
                self.operand = operand
                return True
        value = Timer()
        capture = _timer_capture(value, core=self.core)
        self.assertEqual(value.operand, 0)
        self.assertTrue(self.gate('activate-timer', capture))
        self.assertFalse(self.gate('capture-timer-protocol', capture))
        class Failure:
            def __gt__(self, operand):
                raise RuntimeError('original comparator exception')
        with self.assertRaisesRegex(RuntimeError, 'original comparator exception'):
            _timer_capture(Failure(), core=self.core)

    def test_controller_stop_uses_original_full_primitive_truth(self):
        for value in (None, False, 0, 0.0, -0.0, '', b''):
            kind = {type(None): 'NoneType', bool: 'bool', int: 'int', float: 'float', str: 'str', bytes: 'bytes'}[type(value)]
            self.assertFalse(self.gate('stop-controller', {'controllerUnit': {'type': kind, 'value': value}}))
        for value in (True, 1 << 20000, -(1 << 20000), float('nan'), float('inf'), '\ud800', b'\x00'):
            kind = {bool: 'bool', int: 'int', float: 'float', str: 'str', bytes: 'bytes'}[type(value)]
            self.assertTrue(self.gate('stop-controller', {'controllerUnit': {'type': kind, 'value': value}}))
        foreign = object()
        capture = {'controllerUnit': {'type': 'python-actual-reference-v1',
            'reference': id(foreign), 'typeReference': id(type(foreign))}}
        self.assertTrue(self.gate('capture-controller-stop-protocol', capture))
        capture['controllerUnitProtocol'] = {'operator': 'truth', 'returnedTruth': bool(foreign)}
        self.assertTrue(self.gate('stop-controller', capture))
        self.assertFalse(self.gate('capture-controller-stop-protocol', capture))

    def test_full_original_wait_and_all_duplicate_control_error_rows(self):
        code = 1 << 20000
        owner = self.owner(launcherPresent=True, launcherWaitObserved=True,
            launcherStreamsClosed=True, launcherStreams=[], actualUnit='actual-unit',
            launcherReturncode=code, streamEofObserved={'stream\ud800': True})
        acquired = [
            {'kind': 'agent-launcher-wait', 'observation': {'unit': 'actual-unit',
                'waitReturnObserved': True, 'returncode': code}},
            {'kind': 'agent-stream-tail-read', 'observation': {'stream': 'stream\ud800',
                'readReturned': True, 'readReachedEof': True, 'exception': None, 'bytes': b''}},
            {'kind': 'agent-control-acquisition', 'observation': {'processCreatedObserved': False,
                'processCreateException': 'original failed command'}},
            {'kind': 'agent-control-acquisition', 'observation': {'processCreatedObserved': True,
                'processWaitReturnObserved': True, 'processWaitReturncode': -code,
                'stdoutReachedEof': True, 'stderrReachedEof': True}},
        ]
        self.assertTrue(acquisitions_closed(self.core, None, [owner], acquired))
        acquired.append({'kind': 'agent-control-acquisition', 'observation': {
            **acquired[-1]['observation'], 'stderrReachedEof': False,
            'stderrException': 'original duplicate incomplete command'}})
        self.assertFalse(acquisitions_closed(self.core, None, [owner], acquired))
        acquired.pop()
        acquired[0]['observation']['returncode'] = code + 1
        self.assertFalse(acquisitions_closed(self.core, None, [owner], acquired))

    def test_supported_str_subclass_wait_keeps_genuine_reference_join(self):
        class First(str):
            pass
        class Second(str):
            pass
        raw = First('original accepted raw wait')
        captured = {'type': 'python-actual-reference-v1',
            'reference': id(raw), 'typeReference': id(First)}
        owner = self.owner(launcherPresent=True, launcherWaitObserved=True,
            launcherStreamsClosed=True, launcherStreams=[], actualUnit='actual-unit',
            launcherReturncode=captured, launcherReturncodeCapture=captured)
        raw.__class__ = Second
        acquired = [{'kind': 'agent-launcher-wait', 'observation': {
            'unit': 'actual-unit', 'waitReturnObserved': True,
            'returncode': raw, 'returncodeCapture': {
                **captured, 'typeReference': id(type(raw))}}}]
        self.assertTrue(acquisitions_closed(self.core, None, [owner], acquired))
        acquired[0]['observation']['returncodeCapture']['reference'] += 1
        self.assertFalse(acquisitions_closed(self.core, None, [owner], acquired))

    def test_primitive_capture_values_crossjoin_both_original_raw_waits(self):
        captured = {'type': 'int', 'value': 1 << 20000}
        owner = self.owner(launcherPresent=True, launcherWaitObserved=True,
            launcherStreamsClosed=True, launcherStreams=[], actualUnit='actual-unit',
            launcherReturncode=captured['value'], launcherReturncodeCapture=captured)
        acquired = [{'kind': 'agent-launcher-wait', 'observation': {
            'unit': 'actual-unit', 'waitReturnObserved': True,
            'returncode': captured['value'], 'returncodeCapture': dict(captured)}}]
        self.assertTrue(acquisitions_closed(self.core, None, [owner], acquired))
        acquired[0]['observation']['returncode'] += 1
        self.assertFalse(acquisitions_closed(self.core, None, [owner], acquired))


if __name__ == '__main__':
    unittest.main()
