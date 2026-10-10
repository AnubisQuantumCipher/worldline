"""Ordinary real-library accounting and isolated authority controls.

Finite controls only; no full proof, native custody or producer/lifecycle claim.
Malformed result controls use typed Python records, never invalid native memory.
"""
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from worldline.admission import (
    ADMITTED, RESOURCE_STATE_UNKNOWN, AdmissionAuthority, AdmissionState,
    Floors, Ledger, Reservation, ResourcePolicy,
)
from worldline.core import Core
from worldline.errors import CoreUnavailable
from worldline.resource_ledger import (
    _Quantity, _Result, _decode, compute_ledger,
)


# Complete retained MCP receipts, with parsed/status/formal/non_claims intact.
# Public ordinary fixture data only; no private workspace or evidence paths.
_JACKAL_RECEIPTS = json.loads(r'''
[
  {
    "expression": "3-2",
    "receipt": {
      "content": [
        {
          "type": "text",
          "text": "{\"assurance\":\"exact rational arithmetic (not yet checker-covered)\",\"engine_output\":\"status=exact parsed=3-2 exact=1 approx=1\",\"fields\":{\"approx\":\"1\",\"exact\":\"1\",\"parsed\":\"3-2\",\"status\":\"exact\"},\"formal\":false,\"identities\":{\"evaluator_sha256\":\"4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872\"},\"lane\":\"rat\",\"non_claims\":[\"NOT formal-bounded: this lane carries no Lean-checked certificate\",\"The epistemic class above is the STRONGEST claim this result supports\",\"exact rational arithmetic (not yet checker-covered)\"],\"status\":\"exact\"}"
        }
      ],
      "structuredContent": {
        "assurance": "exact rational arithmetic (not yet checker-covered)",
        "engine_output": "status=exact parsed=3-2 exact=1 approx=1",
        "fields": {
          "approx": "1",
          "exact": "1",
          "parsed": "3-2",
          "status": "exact"
        },
        "formal": false,
        "identities": {
          "evaluator_sha256": "4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872"
        },
        "lane": "rat",
        "non_claims": [
          "NOT formal-bounded: this lane carries no Lean-checked certificate",
          "The epistemic class above is the STRONGEST claim this result supports",
          "exact rational arithmetic (not yet checker-covered)"
        ],
        "status": "exact"
      }
    }
  },
  {
    "expression": "1-2",
    "receipt": {
      "content": [
        {
          "type": "text",
          "text": "{\"assurance\":\"exact rational arithmetic (not yet checker-covered)\",\"engine_output\":\"status=exact parsed=1-2 exact=-1 approx=-1\",\"fields\":{\"approx\":\"-1\",\"exact\":\"-1\",\"parsed\":\"1-2\",\"status\":\"exact\"},\"formal\":false,\"identities\":{\"evaluator_sha256\":\"4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872\"},\"lane\":\"rat\",\"non_claims\":[\"NOT formal-bounded: this lane carries no Lean-checked certificate\",\"The epistemic class above is the STRONGEST claim this result supports\",\"exact rational arithmetic (not yet checker-covered)\"],\"status\":\"exact\"}"
        }
      ],
      "structuredContent": {
        "assurance": "exact rational arithmetic (not yet checker-covered)",
        "engine_output": "status=exact parsed=1-2 exact=-1 approx=-1",
        "fields": {
          "approx": "-1",
          "exact": "-1",
          "parsed": "1-2",
          "status": "exact"
        },
        "formal": false,
        "identities": {
          "evaluator_sha256": "4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872"
        },
        "lane": "rat",
        "non_claims": [
          "NOT formal-bounded: this lane carries no Lean-checked certificate",
          "The epistemic class above is the STRONGEST claim this result supports",
          "exact rational arithmetic (not yet checker-covered)"
        ],
        "status": "exact"
      }
    }
  },
  {
    "expression": "2-(-1)",
    "receipt": {
      "content": [
        {
          "type": "text",
          "text": "{\"assurance\":\"exact rational arithmetic (not yet checker-covered)\",\"engine_output\":\"status=exact parsed=2--1 exact=3 approx=3\",\"fields\":{\"approx\":\"3\",\"exact\":\"3\",\"parsed\":\"2--1\",\"status\":\"exact\"},\"formal\":false,\"identities\":{\"evaluator_sha256\":\"4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872\"},\"lane\":\"rat\",\"non_claims\":[\"NOT formal-bounded: this lane carries no Lean-checked certificate\",\"The epistemic class above is the STRONGEST claim this result supports\",\"exact rational arithmetic (not yet checker-covered)\"],\"status\":\"exact\"}"
        }
      ],
      "structuredContent": {
        "assurance": "exact rational arithmetic (not yet checker-covered)",
        "engine_output": "status=exact parsed=2--1 exact=3 approx=3",
        "fields": {
          "approx": "3",
          "exact": "3",
          "parsed": "2--1",
          "status": "exact"
        },
        "formal": false,
        "identities": {
          "evaluator_sha256": "4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872"
        },
        "lane": "rat",
        "non_claims": [
          "NOT formal-bounded: this lane carries no Lean-checked certificate",
          "The epistemic class above is the STRONGEST claim this result supports",
          "exact rational arithmetic (not yet checker-covered)"
        ],
        "status": "exact"
      }
    }
  },
  {
    "expression": "3+1+0-1+3",
    "receipt": {
      "content": [
        {
          "type": "text",
          "text": "{\"assurance\":\"exact rational arithmetic (not yet checker-covered)\",\"engine_output\":\"status=exact parsed=3+1+0-1+3 exact=6 approx=6\",\"fields\":{\"approx\":\"6\",\"exact\":\"6\",\"parsed\":\"3+1+0-1+3\",\"status\":\"exact\"},\"formal\":false,\"identities\":{\"evaluator_sha256\":\"4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872\"},\"lane\":\"rat\",\"non_claims\":[\"NOT formal-bounded: this lane carries no Lean-checked certificate\",\"The epistemic class above is the STRONGEST claim this result supports\",\"exact rational arithmetic (not yet checker-covered)\"],\"status\":\"exact\"}"
        }
      ],
      "structuredContent": {
        "assurance": "exact rational arithmetic (not yet checker-covered)",
        "engine_output": "status=exact parsed=3+1+0-1+3 exact=6 approx=6",
        "fields": {
          "approx": "6",
          "exact": "6",
          "parsed": "3+1+0-1+3",
          "status": "exact"
        },
        "formal": false,
        "identities": {
          "evaluator_sha256": "4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872"
        },
        "lane": "rat",
        "non_claims": [
          "NOT formal-bounded: this lane carries no Lean-checked certificate",
          "The epistemic class above is the STRONGEST claim this result supports",
          "exact rational arithmetic (not yet checker-covered)"
        ],
        "status": "exact"
      }
    }
  },
  {
    "expression": "1+0+1",
    "receipt": {
      "content": [
        {
          "type": "text",
          "text": "{\"assurance\":\"exact rational arithmetic (not yet checker-covered)\",\"engine_output\":\"status=exact parsed=1+0+1 exact=2 approx=2\",\"fields\":{\"approx\":\"2\",\"exact\":\"2\",\"parsed\":\"1+0+1\",\"status\":\"exact\"},\"formal\":false,\"identities\":{\"evaluator_sha256\":\"4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872\"},\"lane\":\"rat\",\"non_claims\":[\"NOT formal-bounded: this lane carries no Lean-checked certificate\",\"The epistemic class above is the STRONGEST claim this result supports\",\"exact rational arithmetic (not yet checker-covered)\"],\"status\":\"exact\"}"
        }
      ],
      "structuredContent": {
        "assurance": "exact rational arithmetic (not yet checker-covered)",
        "engine_output": "status=exact parsed=1+0+1 exact=2 approx=2",
        "fields": {
          "approx": "2",
          "exact": "2",
          "parsed": "1+0+1",
          "status": "exact"
        },
        "formal": false,
        "identities": {
          "evaluator_sha256": "4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872"
        },
        "lane": "rat",
        "non_claims": [
          "NOT formal-bounded: this lane carries no Lean-checked certificate",
          "The epistemic class above is the STRONGEST claim this result supports",
          "exact rational arithmetic (not yet checker-covered)"
        ],
        "status": "exact"
      }
    }
  },
  {
    "expression": "3-1-0-2",
    "receipt": {
      "content": [
        {
          "type": "text",
          "text": "{\"assurance\":\"exact rational arithmetic (not yet checker-covered)\",\"engine_output\":\"status=exact parsed=3-1-0-2 exact=0 approx=0\",\"fields\":{\"approx\":\"0\",\"exact\":\"0\",\"parsed\":\"3-1-0-2\",\"status\":\"exact\"},\"formal\":false,\"identities\":{\"evaluator_sha256\":\"4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872\"},\"lane\":\"rat\",\"non_claims\":[\"NOT formal-bounded: this lane carries no Lean-checked certificate\",\"The epistemic class above is the STRONGEST claim this result supports\",\"exact rational arithmetic (not yet checker-covered)\"],\"status\":\"exact\"}"
        }
      ],
      "structuredContent": {
        "assurance": "exact rational arithmetic (not yet checker-covered)",
        "engine_output": "status=exact parsed=3-1-0-2 exact=0 approx=0",
        "fields": {
          "approx": "0",
          "exact": "0",
          "parsed": "3-1-0-2",
          "status": "exact"
        },
        "formal": false,
        "identities": {
          "evaluator_sha256": "4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872"
        },
        "lane": "rat",
        "non_claims": [
          "NOT formal-bounded: this lane carries no Lean-checked certificate",
          "The epistemic class above is the STRONGEST claim this result supports",
          "exact rational arithmetic (not yet checker-covered)"
        ],
        "status": "exact"
      }
    }
  }
]
''')


class ResourceLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = Core(Path(os.environ['WORLDLINE_CORE_LIB']))
        cls.exact = {}
        receipts = json.loads((Path(__file__).parent / 'fixtures/policy-oracles-v1.json').read_text())
        for row in [*receipts['receipts'], *_JACKAL_RECEIPTS]:
            result = row['receipt']['structuredContent']
            assert result['status'] == 'exact' and result['fields']['status'] == 'exact'
            assert result['fields']['parsed'] and result['non_claims'] and result['formal'] is False
            cls.exact[row['expression']] = int(result['fields']['exact'])

    def test_real_ordered_signed_and_absent_usage(self):
        projection = compute_ledger([(3, None), (3, 2), (1, 2), (-1, None), (2, -1)], core=self.core)
        self.assertEqual(projection.withheld,
                         (3, self.exact['3-2'], 0, -1, self.exact['2-(-1)']))
        self.assertEqual(projection.total, self.exact['3+1+0-1+3'])

    def test_real_bool_zero_and_empty_domain(self):
        projection = compute_ledger([(True, None), (False, True), (True, False)], core=self.core)
        self.assertEqual(projection.withheld, (1, 0, 1))
        self.assertEqual(projection.total, self.exact['1+0+1'])
        empty = compute_ledger([], core=self.core)
        self.assertEqual((empty.total, empty.withheld), (0, ()))
        zero = compute_ledger([(0, None), (0, 0)], core=self.core)
        self.assertEqual((zero.total, zero.withheld), (0, (0, 0)))

    def test_real_full_magnitude_and_intermediate_total(self):
        huge = self.exact['2^128']
        projection = compute_ledger([(huge, None), (-huge, None), (huge, huge)], core=self.core)
        self.assertEqual(projection.withheld, (huge, -huge, 0))
        self.assertEqual(projection.total, self.exact['(2^128)-(2^128)'])

    def test_missing_api_and_noninteger_have_no_python_fallback(self):
        with self.assertRaises(CoreUnavailable) as caught:
            compute_ledger([(1, None)], core=SimpleNamespace(_lib=object()))
        self.assertEqual(caught.exception.message, 'the selected kernel has no resource ledger API')
        with self.assertRaises(CoreUnavailable) as caught:
            compute_ledger([(1, 'unavailable')], core=self.core)
        self.assertEqual(caught.exception.message, 'resource ledger quantities must be integers')

    def test_declared_output_schema_controls(self):
        # Ordinary declared schemas: valid gapped arena, then each independent
        # representation condition. These records are not sent across the ABI.
        ready = _Result(0, _Quantity(1, 1, 0))
        detail = _Quantity(2, 1, 0)
        valid = _decode(ready, b'\x00\x01\x00', b'\x01\x00', [detail], [(2, 2)])
        self.assertEqual((valid.total, valid.withheld), (1, (1,)))
        cases = [
            ('typed refusal', _Result(1, _Quantity(1, 0, 0)), b'\x00\x01\x00', b'\x01\x00', detail),
            ('unknown status', _Result(255, _Quantity(1, 0, 0)), b'\x00\x01\x00', b'\x01\x00', detail),
            ('sign', ready, b'\x00\x01\x00', b'\x01\x00', _Quantity(2, 1, 2)),
            ('noncanonical zero', ready, b'\x00\x00\x00', b'\x01\x00', _Quantity(2, 0, 0)),
            ('negative zero', ready, b'\x00\x00\x00', b'\x01\x00', _Quantity(1, 0, 1)),
            ('slot extent', ready, b'\x00\x01\x00', b'\x01\x00', _Quantity(2, 3, 0)),
            ('slot start', ready, b'\x00\x01\x00', b'\x01\x00', _Quantity(1, 1, 0)),
            ('high zero digit', ready, b'\x00\x01\x00', b'\x01\x00', _Quantity(2, 2, 0)),
            ('slot padding', ready, b'\x00\x01\x01', b'\x01\x00', detail),
            ('outside frame', ready, b'\x01\x01\x00', b'\x01\x00', detail),
            ('trailing frame', ready, b'\x00\x01\x00\x01', b'\x01\x00', detail),
            ('total padding', ready, b'\x00\x01\x00', b'\x01\x01', detail),
        ]
        for name, result, detail_bytes, total_bytes, descriptor in cases:
            with self.subTest(case=name), self.assertRaises(CoreUnavailable):
                _decode(result, detail_bytes, total_bytes, [descriptor], [(2, 2)])

    def test_actual_authority_observes_once_and_retains_metadata(self):
        with TemporaryDirectory() as directory, patch.object(Core, '_shared', self.core):
            authority = AdmissionAuthority(Ledger(Path(directory)), Floors(),
                                           observer=lambda: AdmissionState('OBSERVED', mem_available_bytes=3))
            reservations = [Reservation('absent', 'a', None, 1, 0, 0, owner_pid=0),
                            Reservation('zero', 'b', None, 1, 0, 0, owner_pid=0)]
            calls = []
            def usage(row):
                calls.append(row.reservation_id)
                return None if row.reservation_id == 'absent' else 0
            authority._usage = usage
            total, detail = authority.outstanding_withheld(reservations)
            self.assertEqual(calls, ['absent', 'zero'])
            self.assertEqual(total, self.exact['1+0+1'])
            self.assertEqual([r['reservationId'] for r in detail], calls)
            self.assertEqual([r['workload'] for r in detail], ['a', 'b'])
            self.assertEqual([r['observedUsageBytes'] for r in detail], [None, 0])
            self.assertEqual([r['reservedBytes'] for r in detail], [1, 1])
            self.assertEqual([r['withheldBytes'] for r in detail], [1, 1])

    def test_actual_admission_keeps_liveness_and_appends_after_ready(self):
        with TemporaryDirectory() as directory, patch.object(Core, '_shared', self.core):
            ledger = Ledger(Path(directory))
            retained = [Reservation('inactive', 'a', None, 1, 0, 0, owner_pid=0),
                        Reservation('active', 'b', None, 1, 0, 0, owner_pid=0)]
            with ledger.locked():
                ledger._store(retained)
            before = ledger.path.read_bytes()
            calls = []
            def usage(row):
                calls.append(row.reservation_id)
                return 0
            authority = AdmissionAuthority(ledger, Floors(0, 0, 0, 0), usage=usage,
                observer=lambda: AdmissionState('OBSERVED', mem_available_bytes=3),
                is_live=lambda row: row.reservation_id != 'inactive')
            policy = ResourcePolicy(memory_max_bytes=2)
            report = authority.report(policy)
            self.assertTrue(report['wouldAdmitNow'])
            self.assertIsNone(report['resourceDecisionError'])
            self.assertEqual(report['withheldBytes'], 1)
            self.assertEqual(ledger.path.read_bytes(), before)
            calls.clear()
            decision = authority.admit(workload='new', policy=policy)
            self.assertEqual(decision.outcome, ADMITTED)
            self.assertEqual(calls, ['active'])
            self.assertEqual(self.exact['3-1-0-2'], 0)
            self.assertEqual([r.reservation_id for r in ledger.outstanding()],
                             ['inactive', 'active', decision.reservation_id])

    def test_accounting_errors_keep_metadata_unknown_and_never_write(self):
        with TemporaryDirectory() as directory, patch.object(Core, '_shared', self.core):
            ledger = Ledger(Path(directory))
            reservation = Reservation('retained', 'ordinary', None, 1, 0, 0, owner_pid=0)
            with ledger.locked():
                ledger._store([reservation])
            before = ledger.path.read_bytes()
            authority = AdmissionAuthority(ledger, Floors(0, 0, 0, 0),
                observer=lambda: AdmissionState('OBSERVED', mem_available_bytes=3), usage=lambda _: None)
            def missing(_):
                return compute_ledger([(1, None)], core=SimpleNamespace(_lib=object()))
            def refused(_):
                return _decode(_Result(3, _Quantity(1, 0, 0)), b'', b'', [], [])
            for name, unavailable in [('missing API', missing), ('refused schema', refused)]:
                with self.subTest(case=name), patch('worldline.admission.kernel_compute_ledger', side_effect=unavailable), \
                     patch.object(authority, '_numeric_policy') as policy_call, patch.object(ledger, '_store') as store:
                    report = authority.report(ResourcePolicy())
                    decision = authority.admit(workload='ordinary', policy=ResourcePolicy())
                    self.assertEqual(decision.outcome, RESOURCE_STATE_UNKNOWN)
                    self.assertIsNone(report['wouldAdmitNow'])
                    self.assertIsNone(report['withheldBytes'])
                    self.assertIsNone(report['headroomBytes'])
                    self.assertEqual(report['resourceDecisionError'], decision.arithmetic['kernelError'])
                    self.assertIn(report['resourceDecisionError'], decision.reason)
                    self.assertEqual(report['outstandingReservations'],
                                     decision.arithmetic['reservations'])
                    self.assertEqual(report['outstandingReservations'][0]['reservationId'], 'retained')
                    self.assertIsNone(report['outstandingReservations'][0]['withheldBytes'])
                    self.assertIsNone(report['outstandingReservations'][0]['observedUsageBytes'])
                    policy_call.assert_not_called()
                    store.assert_not_called()
                    self.assertEqual(ledger.path.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
