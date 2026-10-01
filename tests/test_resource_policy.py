"""Ordinary real-library numeric gates and isolated ledger integration.

Finite fixtures only: no full-domain, pointer, producer, lifecycle or proof claim.
Numeric expectations use retained JACKAL exact receipts (not formal-bounded).
"""
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from worldline.admission import (
    ADMITTED, RESOURCES_UNAVAILABLE, RESOURCE_STATE_UNKNOWN,
    AdmissionAuthority, AdmissionState, Floors, Ledger, Reservation, ResourcePolicy,
)
from worldline.core import Core
from worldline.errors import CoreUnavailable
from worldline.resource_policy import decide_policy


class ResourcePolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = Core(Path(os.environ['WORLDLINE_CORE_LIB']))
        root = Path(__file__).resolve().parents[1]
        receipts = json.loads((root / 'tests/fixtures/policy-oracles-v1.json').read_text())
        cls.exact = {}
        for item in receipts['receipts']:
            result = item['receipt']['structuredContent']
            assert result['status'] == 'exact' and result['fields']['status'] == 'exact'
            assert result['fields']['parsed'] and result['non_claims'] and result['formal'] is False
            cls.exact[item['expression']] = int(result['fields']['exact'])
        admission = json.loads((root / 'tests/fixtures/policy-oracle-admission-v1.json').read_text())
        assert admission['structuredContent']['status'] == 'exact'
        capacity = json.loads((root / 'tests/fixtures/policy-oracle-large-capacity-v1.json').read_text())
        assert capacity['structuredContent']['status'] == 'exact'
        assert capacity['structuredContent']['fields']['parsed'] == '2^128-2^128-0-0'
        assert capacity['structuredContent']['fields']['exact'] == '0'
        cls.huge = cls.exact['2^128']

    def base(self, **overrides):
        args = dict(outstanding_count=0, concurrency_limit=None,
                    memory_pressure=None, memory_pressure_ceiling=2,
                    disks=(), disk_byte_floor=2, disk_inode_floor=2,
                    available_memory=10, withheld_memory=3, memory_floor=2,
                    requested_memory=5)
        args.update(overrides)
        return args

    def test_actual_library_gate_order_and_inclusive_edges(self):
        # Receipt differences determine each local comparison; the policy's
        # specified gate ordering determines which local failure is returned.
        cases = [
            ('capacity equality', {}, None, None, '10-3-2-5'),
            ('concurrency below', dict(outstanding_count=0, concurrency_limit=1), None, None, '0-1'),
            ('concurrency first', dict(outstanding_count=1, concurrency_limit=1,
                memory_pressure=3, disks=((1, 1),), requested_memory=6), 'CONCURRENCY', None, '1-1'),
            ('pressure equality', dict(memory_pressure=2), None, None, '2-2'),
            ('pressure first', dict(memory_pressure=3, disks=((1, 1),), requested_memory=6),
                'PRESSURE', None, '3-2'),
            ('bytes before inodes', dict(disks=((1, 1),), requested_memory=6), 'DISK_BYTES', 0, '1-2'),
            ('inodes after bytes', dict(disks=((2, 1),), requested_memory=6), 'DISK_INODES', 0, '1-2'),
            ('first filesystem', dict(disks=((2, 1), (1, 2))), 'DISK_INODES', 0, '1-2'),
            ('later filesystem', dict(disks=((2, 2), (1, 2))), 'DISK_BYTES', 1, '1-2'),
            ('disk equality', dict(disks=((2, 2),)), None, None, '2-2'),
            ('capacity last', dict(requested_memory=6), 'CAPACITY', None, '10-3-2-6'),
            ('zero request floor', dict(available_memory=0, withheld_memory=0, requested_memory=0),
                'CAPACITY', None, '0-0-2-0'),
            ('negative availability', dict(available_memory=-1, withheld_memory=0,
                memory_floor=0, requested_memory=0), 'CAPACITY', None, '-1-0-0-0'),
            ('signed pressure', dict(memory_pressure=-2, memory_pressure_ceiling=-1),
                None, None, '-2-(-1)'),
            ('signed disk', dict(disks=((-2, 2),), disk_byte_floor=-1),
                'DISK_BYTES', 0, '-2-(-1)'),
            ('absent pressure', dict(memory_pressure=None, memory_pressure_ceiling=-1),
                None, None, '10-3-2-5'),
        ]
        for name, changes, gate, disk_index, receipt in cases:
            with self.subTest(case=name):
                self.assertIn(receipt, self.exact)
                decision = decide_policy(**self.base(**changes), core=self.core)
                self.assertEqual((decision.gate, decision.disk_index), (gate, disk_index))

    def test_full_magnitudes_are_not_machine_word_truncated(self):
        decision = decide_policy(**self.base(outstanding_count=self.huge,
            concurrency_limit=self.huge), core=self.core)
        self.assertEqual(decision.gate, 'CONCURRENCY')
        decision = decide_policy(**self.base(available_memory=self.huge,
            withheld_memory=self.huge, memory_floor=0, requested_memory=0,
            memory_pressure=self.huge, memory_pressure_ceiling=self.huge,
            disks=((self.huge, self.huge),), disk_byte_floor=self.huge,
            disk_inode_floor=self.huge), core=self.core)
        self.assertTrue(decision.ready)
        self.assertEqual(self.exact['(2^128)-(2^128)'], 0)

    def test_actual_kernel_negative_debit_is_unknown(self):
        for field in ('withheld_memory', 'memory_floor', 'requested_memory'):
            with self.subTest(field=field):
                with self.assertRaises(CoreUnavailable) as caught:
                    decide_policy(**self.base(**{field: -1}), core=self.core)
                self.assertEqual(caught.exception.details['status'], 'NEGATIVE_DEBIT')
                self.assertEqual(caught.exception.details['gate'], 'CAPACITY')
                self.assertEqual(caught.exception.details['field'], field.upper())

    def test_unavailable_api_has_no_python_fallback(self):
        with self.assertRaises(CoreUnavailable):
            decide_policy(**self.base(), core=SimpleNamespace(_lib=object()))

    def test_boolean_is_a_representation_error(self):
        with self.assertRaises(ValueError):
            decide_policy(**self.base(memory_pressure=True), core=self.core)

    def test_actual_authority_refusals_and_reports_preserve_ledger(self):
        cases = [
            ('concurrency', dict(max_concurrent_workloads=1),
                dict(memory_pressure_hundredths=3), 'workloads already admitted'),
            ('pressure', {}, dict(memory_pressure_hundredths=3), 'memory pressure avg10'),
            ('bytes', {}, dict(disk={'z-first': {'freeBytes': 1, 'freeInodes': 1},
                                    'a-second': {'freeBytes': 1, 'freeInodes': 1}}), 'z-first has 1 bytes'),
            ('inodes', {}, dict(disk={'z-first': {'freeBytes': 2, 'freeInodes': 1},
                                     'a-second': {'freeBytes': 1, 'freeInodes': 2}}), 'z-first has 1 inodes'),
            ('capacity', {}, dict(mem_available_bytes=0), 'bytes requested but only'),
        ]
        for name, policy_values, state_values, reason in cases:
            with self.subTest(case=name), TemporaryDirectory() as directory, patch.object(Core, '_shared', self.core):
                ledger = Ledger(Path(directory))
                reservation = Reservation('retained', 'ordinary', None, 0, 0, 0, owner_pid=os.getpid())
                with ledger.locked():
                    ledger._store([reservation])
                retained = ledger.path.read_bytes()
                state_args = dict(mem_available_bytes=10)
                state_args.update(state_values)
                state = AdmissionState('OBSERVED', **state_args)
                authority = AdmissionAuthority(ledger, Floors(2, 2, 2, 2), observer=lambda: state)
                policy = ResourcePolicy(**policy_values)
                report = authority.report(policy)
                self.assertFalse(report['wouldAdmitNow'])
                self.assertIsNone(report['resourceDecisionError'])
                decision = authority.admit(workload='ordinary', policy=policy)
                self.assertEqual(decision.outcome, RESOURCES_UNAVAILABLE)
                self.assertIn(reason, decision.reason)
                self.assertEqual(ledger.path.read_bytes(), retained)

    def test_unknown_real_kernel_result_never_writes_ledger(self):
        with TemporaryDirectory() as directory, patch.object(Core, '_shared', self.core):
            ledger = Ledger(Path(directory))
            authority = AdmissionAuthority(ledger, Floors(min_free_memory_bytes=-1),
                observer=lambda: AdmissionState('OBSERVED', mem_available_bytes=10))
            report = authority.report(ResourcePolicy())
            self.assertIsNone(report['wouldAdmitNow'])
            self.assertIn('kernel could not decide the numeric stage', report['resourceDecisionError'])
            decision = authority.admit(workload='ordinary', policy=ResourcePolicy())
            self.assertEqual(decision.outcome, RESOURCE_STATE_UNKNOWN)
            self.assertIn('kernel could not decide the numeric stage', decision.reason)
            self.assertFalse(ledger.path.exists())

    def test_liveness_filter_keeps_records_and_ready_is_required_for_append(self):
        with TemporaryDirectory() as directory, patch.object(Core, '_shared', self.core):
            ledger = Ledger(Path(directory))
            reservation = Reservation('retained', 'ordinary', None, 0, 0, 0, owner_pid=os.getpid())
            with ledger.locked():
                ledger._store([reservation])
            before = ledger.path.read_bytes()
            authority = AdmissionAuthority(ledger, Floors(min_free_memory_bytes=2),
                observer=lambda: AdmissionState('OBSERVED', mem_available_bytes=10),
                is_live=lambda _: False)
            policy = ResourcePolicy(memory_max_bytes=5, max_concurrent_workloads=1)
            report = authority.report(policy)
            self.assertTrue(report['wouldAdmitNow'])
            self.assertEqual(ledger.path.read_bytes(), before)
            decision = authority.admit(workload='ordinary', policy=policy)
            self.assertEqual(decision.outcome, ADMITTED)
            self.assertEqual([r.reservation_id for r in ledger.outstanding()],
                             ['retained', decision.reservation_id])


if __name__ == '__main__':
    unittest.main()
