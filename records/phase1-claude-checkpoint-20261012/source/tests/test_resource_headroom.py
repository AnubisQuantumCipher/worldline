"""Ordinary owned-buffer headroom controls against the real selected library.

Retained JACKAL exact arithmetic is an informational expected-value source, not
proof of the code, the full representation domain, native custody or storage.
"""
import ctypes
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
from worldline.resource_ledger import (
    _Quantity, _Result, _headroom_api, _decode_headroom, compute_headroom,
)


class ResourceHeadroomTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = Core(Path(os.environ['WORLDLINE_CORE_LIB']))
        rows = json.loads((Path(__file__).parent / 'fixtures/headroom-oracles-v1.json').read_text())['receipts']
        cls.exact = {}
        for row in rows:
            receipt = row['receipt']['structuredContent']
            assert receipt['status'] == 'exact' and receipt['fields']['status'] == 'exact'
            assert receipt['fields']['parsed'] and receipt['non_claims'] and receipt['formal'] is False
            cls.exact[row['expression']] = int(receipt['fields']['exact'])

    def wire(self, raw, available, withheld, floor, capacity):
        # Every pointer refers to a real privately owned extent. Quantity spans
        # and capacity values below are the ordinary total typed API cases.
        data = (ctypes.c_uint8 * len(raw)).from_buffer_copy(raw)
        output = (ctypes.c_uint8 * capacity)()
        result = _Result()
        code = _headroom_api(self.core)(
            ctypes.cast(data, ctypes.c_void_p), len(data),
            ctypes.byref(available), ctypes.byref(withheld), ctypes.byref(floor),
            ctypes.cast(output, ctypes.c_void_p), len(output), ctypes.byref(result))
        self.assertEqual(code, 0)
        return result, bytes(output)

    def test_real_signed_exact_values(self):
        cases = [((120, 30, 10), '120-30-10'), ((20, 30, 10), '20-30-10'),
                 ((0, 0, 0), '0-0-0'), ((5, 8, -3), '5-8-(-3)'),
                 ((-5, -12, 4), '-5-(-12)-4'), ((-5, 7, -20), '-5-7-(-20)')]
        for values, expression in cases:
            with self.subTest(expression=expression):
                self.assertEqual(compute_headroom(*values, core=self.core), self.exact[expression])

    def test_real_full_signed_magnitudes(self):
        huge, word_boundary = self.exact['2^128'], self.exact['2^64']
        cases = [((huge, word_boundary, 17), '(2^128)-(2^64)-17'),
                 ((-huge, huge, huge), '-(2^128)-(2^128)-(2^128)'),
                 ((huge, -huge, huge), '(2^128)-(-(2^128))-(2^128)')]
        for values, expression in cases:
            with self.subTest(expression=expression):
                self.assertEqual(compute_headroom(*values, core=self.core), self.exact[expression])

    def test_real_bool_integer_compatibility(self):
        self.assertEqual(compute_headroom(True, False, True, core=self.core), self.exact['1-0-1'])

    def test_real_empty_and_leading_zero_inputs_are_canonicalized(self):
        result, output = self.wire(b'', _Quantity(1, 0, 1), _Quantity(1, 0, 0),
                                   _Quantity(1, 0, 1), 0)
        self.assertEqual(result.status, 0)
        self.assertEqual((result.total.first, result.total.length, result.total.negative), (1, 0, 0))
        self.assertEqual(_decode_headroom(result, output), self.exact['0-0-0'])
        result, output = self.wire(b'\x78\x00\x1e\x00\x0a\x00', _Quantity(1, 2, 0),
                                   _Quantity(3, 2, 0), _Quantity(5, 2, 0), 4)
        self.assertEqual(result.status, 0)
        self.assertEqual(_decode_headroom(result, output), self.exact['120-30-10'])
        self.assertEqual((result.total.first, result.total.length, result.total.negative), (1, 1, 0))
        self.assertEqual(output[1:], b'\x00\x00\x00')

    def test_real_storage_boundary_and_intermediate_refusal(self):
        empty = _Quantity(1, 0, 0)
        result, output = self.wire(b'\xff', _Quantity(1, 1, 0), empty, empty, 1)
        self.assertEqual(_decode_headroom(result, output), self.exact['255-0-0'])
        result, output = self.wire(b'\x00\x01', _Quantity(1, 2, 0), empty, empty, 1)
        self.assertEqual(result.status, 3)
        self.assertEqual(output, b'\x00')
        self.assertEqual((result.total.first, result.total.length, result.total.negative), (1, 0, 0))
        raw = b'\xff\x01\x00\x01'
        quantities = (_Quantity(1, 1, 0), _Quantity(2, 1, 1), _Quantity(3, 2, 0))
        result, output = self.wire(raw, *quantities, 1)
        self.assertEqual(result.status, 3)  # Final cancellation does not waive intermediate storage.
        self.assertEqual(output, b'\x00')
        self.assertEqual((result.total.first, result.total.length, result.total.negative), (1, 0, 0))
        result, output = self.wire(raw, *quantities, 2)
        self.assertEqual(_decode_headroom(result, output), self.exact['255-(-1)-256'])
        self.assertEqual(output, b'\x00\x00')

    def test_real_invalid_span_refuses_before_arithmetic(self):
        empty = _Quantity(1, 0, 0)
        result, output = self.wire(b'\x01', _Quantity(2, 1, 0), empty, empty, 2)
        self.assertEqual(result.status, 1)
        self.assertEqual(output, b'\x00\x00')
        self.assertEqual((result.total.first, result.total.length, result.total.negative), (1, 0, 0))

    def test_missing_api_and_noninteger_have_no_fallback(self):
        actual = self.core._lib
        class LegacyLibrary:
            def __getattr__(self, name):
                if name == 'wl_resource_ledger_headroom':
                    raise AttributeError(name)
                return getattr(actual, name)
        with self.assertRaises(CoreUnavailable) as caught:
            compute_headroom(120, 30, 10, core=SimpleNamespace(_lib=LegacyLibrary()))
        self.assertEqual(caught.exception.message, 'the selected kernel has no resource headroom API')
        with self.assertRaises(CoreUnavailable) as caught:
            compute_headroom('unknown', 30, 10, core=self.core)
        self.assertEqual(caught.exception.message, 'resource headroom quantities must be integers')

    def test_actual_admission_and_read_only_report_use_signed_kernel_result(self):
        for available, expected, outcome in [(120, '120-30-10', ADMITTED),
                                             (20, '20-30-10', RESOURCES_UNAVAILABLE)]:
            with self.subTest(available=available), TemporaryDirectory() as directory, \
                 patch.object(Core, '_shared', self.core):
                ledger = Ledger(Path(directory))
                with ledger.locked():
                    ledger._store([Reservation('retained', 'ordinary', None, 30, 0, 0, owner_pid=0)])
                before = ledger.path.read_bytes()
                authority = AdmissionAuthority(ledger, Floors(10, 0, 0, 0),
                    observer=lambda: AdmissionState('OBSERVED', mem_available_bytes=available),
                    usage=lambda _: None, is_live=lambda _: True)
                policy = ResourcePolicy(memory_max_bytes=1)
                report = authority.report(policy)
                self.assertEqual(report['headroomBytes'], self.exact[expected])
                self.assertEqual(ledger.path.read_bytes(), before)
                decision = authority.admit(workload='new', policy=policy)
                self.assertEqual(decision.outcome, outcome)
                self.assertEqual(decision.arithmetic['headroomBytes'], self.exact[expected])
                if outcome == RESOURCES_UNAVAILABLE:
                    self.assertEqual(ledger.path.read_bytes(), before)

    def test_headroom_unavailable_stops_policy_and_write_without_fallback(self):
        with TemporaryDirectory() as directory, patch.object(Core, '_shared', self.core):
            ledger = Ledger(Path(directory))
            with ledger.locked():
                ledger._store([Reservation('retained', 'ordinary', None, 30, 0, 0, owner_pid=0)])
            before = ledger.path.read_bytes()
            authority = AdmissionAuthority(ledger, Floors(10, 0, 0, 0),
                observer=lambda: AdmissionState('OBSERVED', mem_available_bytes=120),
                usage=lambda _: None, is_live=lambda _: True)
            with (patch('worldline.admission.kernel_compute_headroom', side_effect=CoreUnavailable('unavailable')),
                  patch.object(authority, '_numeric_policy') as policy_call,
                  patch.object(ledger, '_store') as store):
                report = authority.report(ResourcePolicy())
                decision = authority.admit(workload='new', policy=ResourcePolicy())
                self.assertEqual(decision.outcome, RESOURCE_STATE_UNKNOWN)
                self.assertIsNone(report['headroomBytes'])
                self.assertIsNone(decision.arithmetic['headroomBytes'])
                self.assertIsNone(report['wouldAdmitNow'])
                self.assertEqual(report['withheldBytes'], 30)
                self.assertEqual(decision.arithmetic['withheldByReservationsBytes'], 30)
                self.assertEqual(report['resourceDecisionError'], decision.arithmetic['kernelError'])
                policy_call.assert_not_called()
                store.assert_not_called()
                self.assertEqual(ledger.path.read_bytes(), before)

    def test_unreadable_ledger_keeps_all_numeric_reporting_unknown(self):
        with TemporaryDirectory() as directory, patch.object(Core, '_shared', self.core):
            ledger = Ledger(Path(directory))
            ledger.path.parent.mkdir(parents=True, exist_ok=True)
            ledger.path.write_bytes(b'{"reservations": "unavailable"}')
            before = ledger.path.read_bytes()
            authority = AdmissionAuthority(ledger, Floors(10, 0, 0, 0),
                observer=lambda: AdmissionState('OBSERVED', mem_available_bytes=120))
            with (patch.object(authority, 'outstanding_withheld') as accounting,
                  patch('worldline.admission.kernel_compute_headroom') as headroom,
                  patch.object(authority, '_numeric_policy') as policy,
                  patch.object(ledger, '_store') as store):
                report = authority.report(ResourcePolicy())
                self.assertIn('unexpected shape', report['ledgerError'])
                self.assertIsNone(report['withheldBytes'])
                self.assertIsNone(report['headroomBytes'])
                self.assertIsNone(report['wouldAdmitNow'])
                self.assertIsNone(report['resourceDecisionError'])
                accounting.assert_not_called()
                headroom.assert_not_called()
                policy.assert_not_called()
                store.assert_not_called()
                self.assertEqual(ledger.path.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
