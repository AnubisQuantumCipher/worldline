"""Ordinary real-library resource binding and admission checks.

Arithmetic oracle receipts are exact, outside formal proof. These checks do not
discharge the kernel contracts, pointer correspondence or complete lifecycle.
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
    AdmissionAuthority, AdmissionState, Floors, Ledger, ResourcePolicy,
)
from worldline.core import Core
from worldline.errors import CoreUnavailable
from worldline.resource_kernel import can_reserve


class ResourceKernelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = Core(Path(os.environ['WORLDLINE_CORE_LIB']))
        root = Path(__file__).resolve().parents[1]
        cls.oracle = json.loads((root / 'resource-evidence/binding-oracle-v1.json').read_text())

    def test_real_kernel_matches_exact_arithmetic_fixtures(self):
        for case in self.oracle['cases']:
            with self.subTest(case=case['name']):
                self.assertEqual(case['jackal']['status'], 'exact')
                args = [int(x) for x in case['inputs']]
                expected = int(case['jackal']['fields']['exact']) >= 0
                self.assertEqual(can_reserve(*args, core=self.core), expected)

    def test_no_kernel_api_cannot_grant(self):
        with self.assertRaises(CoreUnavailable):
            can_reserve(10, 3, 2, 5, core=SimpleNamespace(_lib=object()))

    def test_negative_magnitudes_and_booleans_are_not_encoded(self):
        with self.assertRaises(ValueError):
            can_reserve(10, -1, 2, 5, core=self.core)
        with self.assertRaises(ValueError):
            can_reserve(True, 3, 2, 5, core=self.core)

    def test_actual_admission_uses_kernel_before_ledger_write(self):
        with TemporaryDirectory() as directory, patch.object(Core, '_shared', self.core):
            ledger = Ledger(Path(directory))
            state = AdmissionState('OBSERVED', mem_available_bytes=10)
            authority = AdmissionAuthority(
                ledger, Floors(min_free_memory_bytes=2), observer=lambda: state)
            first = authority.admit(workload='ordinary', policy=ResourcePolicy(), memory_bytes=5)
            self.assertEqual(first.outcome, ADMITTED)
            before = ledger.path.read_bytes()
            second = authority.admit(workload='ordinary', policy=ResourcePolicy(), memory_bytes=5)
            self.assertEqual(second.outcome, RESOURCES_UNAVAILABLE)
            self.assertEqual(ledger.path.read_bytes(), before)

    def test_unmetered_still_obeys_floor(self):
        with TemporaryDirectory() as directory, patch.object(Core, '_shared', self.core):
            ledger = Ledger(Path(directory))
            authority = AdmissionAuthority(
                ledger, Floors(min_free_memory_bytes=2),
                observer=lambda: AdmissionState('OBSERVED', mem_available_bytes=0))
            decision = authority.admit(workload='ordinary', policy=ResourcePolicy())
            self.assertEqual(decision.outcome, RESOURCES_UNAVAILABLE)
            self.assertFalse(ledger.path.exists())

    def test_kernel_failure_leaves_ledger_unchanged(self):
        with TemporaryDirectory() as directory:
            ledger = Ledger(Path(directory))
            authority = AdmissionAuthority(
                ledger, Floors(min_free_memory_bytes=2),
                observer=lambda: AdmissionState('OBSERVED', mem_available_bytes=10))
            with patch('worldline.admission.kernel_can_reserve', side_effect=CoreUnavailable('unavailable')):
                decision = authority.admit(workload='ordinary', policy=ResourcePolicy(), memory_bytes=5)
            self.assertEqual(decision.outcome, RESOURCE_STATE_UNKNOWN)
            self.assertFalse(ledger.path.exists())

    def test_report_uses_actual_kernel_decision(self):
        with TemporaryDirectory() as directory, patch.object(Core, '_shared', self.core):
            ledger = Ledger(Path(directory))
            authority = AdmissionAuthority(
                ledger, Floors(min_free_memory_bytes=2),
                observer=lambda: AdmissionState('OBSERVED', mem_available_bytes=10))
            policy = ResourcePolicy(memory_max_bytes=5)
            before = authority.report(policy)
            self.assertTrue(before['wouldAdmitNow'])
            self.assertIsNone(before['resourceDecisionError'])
            decision = authority.admit(workload='ordinary', policy=policy)
            self.assertEqual(decision.outcome, ADMITTED)
            retained = ledger.path.read_bytes()
            after = authority.report(policy)
            self.assertFalse(after['wouldAdmitNow'])
            self.assertIsNone(after['resourceDecisionError'])
            self.assertEqual(ledger.path.read_bytes(), retained)

    def test_report_kernel_failure_is_unknown_and_preserves_ledger(self):
        with TemporaryDirectory() as directory:
            ledger = Ledger(Path(directory))
            ledger._store([])
            retained = ledger.path.read_bytes()
            authority = AdmissionAuthority(
                ledger, Floors(min_free_memory_bytes=2),
                observer=lambda: AdmissionState('OBSERVED', mem_available_bytes=10))
            with patch('worldline.admission.kernel_can_reserve', side_effect=CoreUnavailable('unavailable')):
                report = authority.report(ResourcePolicy(memory_max_bytes=5))
            self.assertIsNone(report['wouldAdmitNow'])
            self.assertEqual(report['resourceDecisionError'], str(CoreUnavailable('unavailable')))
            self.assertEqual(ledger.path.read_bytes(), retained)


if __name__ == '__main__':
    unittest.main()
