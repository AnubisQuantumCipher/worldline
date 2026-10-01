"""Ordinary owned data and temporary ledgers; no host workload or proof claim."""
import ctypes
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from worldline.admission import AdmissionAuthority, Floors, Ledger, Reservation
from worldline.core import Core
from worldline.errors import CoreUnavailable, WorldlineError
from worldline.reservation_lifecycle import _Row, _api, release_plan, reconcile_plan


class ReservationLifecycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = Core(Path(os.environ['WORLDLINE_CORE_LIB']))

    def wire(self, raw, rows, mode, present, first, length, mask):
        arena = (ctypes.c_uint8 * len(raw)).from_buffer_copy(raw)
        entries = (_Row * len(rows))(*rows)
        output = (ctypes.c_uint8 * len(mask))(*mask)
        status = _api(self.core)(arena, len(raw), entries, len(rows),
                                 mode, present, first, length, output, len(mask))
        return status, tuple(output)

    def test_exact_identity_no_prefix_or_digest_matching(self):
        self.assertEqual(release_plan(['left', 'chosen', 'right'], 'chosen', core=self.core),
                         (False, True, False))
        self.assertEqual(release_plan(['chosen-more', 'left'], 'chosen', core=self.core),
                         (False, False))
        self.assertEqual(release_plan([], '', core=self.core), ())

    def test_empty_nul_unicode_and_surrogate_are_exact_owned_bytes(self):
        names = ['', '\0', 'é', 'e\u0301', '\ud800']
        cases = [('', (True, False, False, False, False)),
                 ('\0', (False, True, False, False, False)),
                 ('é', (False, False, True, False, False)),
                 ('e\u0301', (False, False, False, True, False)),
                 ('\ud800', (False, False, False, False, True))]
        for selected, expected in cases:
            with self.subTest(selected=repr(selected)):
                self.assertEqual(release_plan(names, selected, core=self.core), expected)

    def test_reconcile_only_literal_false_without_truth_or_equality_calls(self):
        class Opaque:
            def __bool__(self):
                raise AssertionError('observation truth must not be invoked')
            def __eq__(self, other):
                raise AssertionError('observation equality must not be invoked')
        self.assertEqual(reconcile_plan(['live', 'gone', 'unknown', 'zero', 'opaque'],
                                        [True, False, None, 0, Opaque()], core=self.core),
                         (False, True, False, False, False))

    def test_total_span_duplicate_mode_and_layout_refusals_preserve_output(self):
        cases = [(b'a', [_Row(2, 1, 0)], 1, 1, 1, 1, (9,), 0),
                 (b'a', [_Row(1, 1, 0), _Row(1, 1, 0)], 1, 1, 1, 1, (9, 8), 0),
                 (b'a', [_Row(1, 1, 0)], 0, 1, 1, 1, (9,), 0),
                 (b'a', [_Row(1, 1, 0)], 1, 0, 1, 0, (9,), 0),
                 (b'a', [_Row(1, 1, 0)], 1, 1, 1, 1, (), 1)]
        for raw, rows, mode, present, first, length, mask, expected in cases:
            with self.subTest(mode=mode, mask=mask):
                self.assertEqual(self.wire(raw, rows, mode, present, first, length, mask),
                                 (expected, mask))

    def test_absent_request_payload_is_ignored_for_reconciliation(self):
        self.assertEqual(self.wire(b'a', [_Row(1, 1, 2)], 2, 0, 0, 0, (9,)), (3, (1,)))
        self.assertEqual(self.wire(b'', [], 2, 0, 0, 0, ()), (2, ()))

    def test_no_api_or_typed_input_refusal_has_no_python_selection_fallback(self):
        with self.assertRaises(CoreUnavailable):
            release_plan(['a'], 'a', core=SimpleNamespace(_lib=object()))
        with self.assertRaises(CoreUnavailable):
            release_plan(['a', 'a'], 'a', core=self.core)
        with self.assertRaises(CoreUnavailable):
            reconcile_plan(['a'], [], core=self.core)

    def reservations(self, ledger):
        rows = [Reservation('left', 'first', None, 0, 0, 0, 0),
                Reservation('chosen', 'second', 'test.service', 1, 1, 1, 1),
                Reservation('right', 'last', None, 0, 0, 0, 0)]
        for row in rows:
            ledger.add(row)
        return rows

    def test_authority_release_and_repeated_release_preserve_all_survivor_fields(self):
        with TemporaryDirectory() as directory, patch.object(Core, 'shared', return_value=self.core):
            ledger = Ledger(Path(directory)); rows = self.reservations(ledger)
            authority = AdmissionAuthority(ledger, Floors())
            self.assertTrue(authority.release('chosen'))
            self.assertEqual(ledger.outstanding(), [rows[0], rows[2]])
            before = ledger.path.read_bytes()
            self.assertFalse(authority.release('chosen'))
            self.assertEqual(ledger.path.read_bytes(), before)

    def test_authority_original_truth_then_string_conversion_order(self):
        calls = []
        class Identity:
            def __bool__(self):
                calls.append('truth'); return True
            def __str__(self):
                calls.append('string'); return 'chosen'
        with TemporaryDirectory() as directory, patch.object(Core, 'shared', return_value=self.core):
            ledger = Ledger(Path(directory)); rows = self.reservations(ledger)
            self.assertTrue(AdmissionAuthority(ledger, Floors()).release(Identity()))
            self.assertEqual(calls, ['truth', 'string'])
            self.assertEqual(ledger.outstanding(), [rows[0], rows[2]])

    def test_authority_preserves_custom_string_subclass_comparison(self):
        calls = []
        class Selected(str):
            def __ne__(self, value):
                calls.append(value)
                return value != 'chosen'
        class Identity:
            def __str__(self):
                return Selected('custom-comparison')
        with TemporaryDirectory() as directory:
            ledger = Ledger(Path(directory)); rows = self.reservations(ledger)
            self.assertTrue(AdmissionAuthority(ledger, Floors()).release(Identity()))
            self.assertEqual(calls, ['left', 'chosen', 'right'])
            self.assertEqual(ledger.outstanding(), [rows[0], rows[2]])

    def test_legacy_direct_custom_comparison_behavior_remains_unchanged(self):
        class Identity:
            def __eq__(self, value):
                return value == 'chosen'
        with TemporaryDirectory() as directory:
            ledger = Ledger(Path(directory)); rows = self.reservations(ledger)
            self.assertTrue(ledger.release(Identity()))
            self.assertEqual(ledger.outstanding(), [rows[0], rows[2]])

    def test_reconcile_callback_order_exception_and_whole_record_preservation(self):
        with TemporaryDirectory() as directory, patch.object(Core, 'shared', return_value=self.core):
            ledger = Ledger(Path(directory)); rows = self.reservations(ledger)
            calls = []
            def observation(row):
                calls.append(row)
                if row.reservation_id == 'left':
                    raise RuntimeError('ordinary unavailable observation')
                return False if row.reservation_id == 'chosen' else True
            self.assertEqual(ledger.reconcile(observation), [rows[1]])
            self.assertEqual(calls, rows)
            self.assertEqual(ledger.outstanding(), [rows[0], rows[2]])

    def test_original_duplicate_normalized_ids_refuse_before_callback_or_removal(self):
        with TemporaryDirectory() as directory:
            ledger = Ledger(Path(directory))
            row = Reservation('chosen', 'ordinary', None, 0, 0, 0, 0).as_dict()
            ledger.path.write_text(json.dumps({'reservations': [row, row]}))
            before = ledger.path.read_bytes(); calls = []
            def observation(value):
                calls.append(value); return False
            for action in (lambda: ledger.release('chosen'),
                           lambda: ledger.release_exact('chosen'),
                           lambda: ledger.reconcile(observation)):
                with self.assertRaises(WorldlineError) as caught:
                    action()
                self.assertIn('duplicate reservation ids', str(caught.exception))
                self.assertEqual(ledger.path.read_bytes(), before)
            self.assertEqual(calls, [])

    def test_kernel_unavailability_keeps_ledger_and_all_observer_calls(self):
        with TemporaryDirectory() as directory:
            ledger = Ledger(Path(directory)); rows = self.reservations(ledger)
            before = ledger.path.read_bytes(); calls = []
            def observation(row):
                calls.append(row); return False
            with patch.object(Core, 'shared', return_value=SimpleNamespace(_lib=object())):
                with self.assertRaises(WorldlineError):
                    ledger.reconcile(observation)
                self.assertEqual(calls, rows)
                self.assertEqual(ledger.path.read_bytes(), before)
                with self.assertRaises(WorldlineError):
                    AdmissionAuthority(ledger, Floors()).release('chosen')
                self.assertEqual(ledger.path.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
