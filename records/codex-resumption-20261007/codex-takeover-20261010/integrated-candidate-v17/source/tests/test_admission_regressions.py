"""Regression controls for what the adversarial campaign broke.

Each one names the attack it came from. They exist because every defect below was found by
execution rather than by reading, and a fix without a control is a fix that can be undone by the
next refactor without anyone noticing.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "runtime"))

from worldline.admission import (  # noqa: E402
    ADMITTED, GIB, MIB, RESOURCES_UNAVAILABLE, RESOURCE_STATE_UNKNOWN,
    AdmissionAuthority, Floors, Ledger, Reservation, ResourcePolicy, observe,
)
from worldline.errors import WorldlineError  # noqa: E402

from test_admission import fixture_root  # noqa: E402


class CampaignRegressions(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-admission-regress-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root = fixture_root(self.base / "root")
        self.ledger = Ledger(self.base / "runtime")

    def authority(self, *, root=None, is_live=None, floors=None) -> AdmissionAuthority:
        return AdmissionAuthority(self.ledger, floors or Floors(min_free_memory_bytes=2 * GIB),
                                  observer=lambda: observe({}, root=root or self.root), is_live=is_live)

    # ---- blocking: the floor did not apply to unmetered work, and the default is unmetered ----
    def test_a_starved_machine_refuses_unmetered_work_too(self) -> None:
        """128 MiB free against a 2 GiB floor. The shipped default declares no ceiling, so this
        was every admission on every default installation."""
        starved = fixture_root(self.base / "starved", available_kb=131072)
        decision = self.authority(root=starved).admit(workload="terra", policy=ResourcePolicy.from_mapping({}))
        self.assertEqual(decision.outcome, RESOURCES_UNAVAILABLE)
        self.assertLess(decision.arithmetic["headroomBytes"], 0)

    def test_doctor_does_not_promise_what_admission_would_refuse(self) -> None:
        starved = fixture_root(self.base / "starved2", available_kb=131072)
        report = self.authority(root=starved).report(ResourcePolicy.from_mapping({}))
        self.assertFalse(report["wouldAdmitNow"], "the report said yes while headroom was negative")

    # ---- blocking: corrupt ledgers escaped as tracebacks rather than refusals -----------------
    def test_every_corrupt_ledger_shape_refuses_rather_than_raising_something_else(self) -> None:
        shapes = {
            "invalid utf-8": b"\xff\xfe\x00 not text",
            "json infinity": b'{"schemaVersion": 1, "reservations": [{"reservationId": "a", "memoryBytes": Infinity}]}',
            "deeply nested": b'{"schemaVersion": 1, "reservations": ' + b"[" * 4000 + b"]" * 4000 + b"}",
            "truncated": b'{"schemaVersion": 1, "reser',
            "wrong shape": b'["not", "a", "document"]',
        }
        for name, payload in shapes.items():
            with self.subTest(shape=name):
                self.ledger.path.write_bytes(payload)
                decision = self.authority().admit(workload="terra", policy=ResourcePolicy.from_mapping({"memoryMaxBytes": GIB}))
                self.assertEqual(decision.outcome, RESOURCE_STATE_UNKNOWN,
                                 f"{name} did not produce a refusal")
                with self.assertRaises(WorldlineError):
                    self.ledger.outstanding()

    def test_a_negative_reservation_cannot_manufacture_headroom(self) -> None:
        """withholding -12 GiB turned a correct refusal into an admission."""
        self.ledger.path.write_text(json.dumps({"schemaVersion": 1, "reservations": [
            {"reservationId": "a", "workload": "poison", "unit": None, "memoryBytes": -12 * GIB,
             "tasks": 0, "createdAtMs": 0, "ownerPid": 1}]}), encoding="utf-8")
        decision = self.authority().admit(workload="terra", policy=ResourcePolicy.from_mapping({"memoryMaxBytes": 12 * GIB}))
        self.assertEqual(decision.outcome, RESOURCE_STATE_UNKNOWN)

    def test_duplicate_reservation_ids_are_refused(self) -> None:
        """Releasing one of two records with the same id released both."""
        record = {"reservationId": "dup", "workload": "a", "unit": None, "memoryBytes": GIB,
                  "tasks": 0, "createdAtMs": 0, "ownerPid": 1}
        self.ledger.path.write_text(json.dumps({"schemaVersion": 1, "reservations": [record, dict(record)]}), encoding="utf-8")
        with self.assertRaises(WorldlineError):
            self.ledger.outstanding()

    # ---- blocking: a manager that cannot answer must not free a running workload --------------
    def test_an_unanswerable_manager_holds_capacity_rather_than_promising_it_twice(self) -> None:
        """Reading "cannot answer" as "not running" deleted the accounting for live workloads."""
        first = self.authority().admit(workload="terra", policy=ResourcePolicy.from_mapping({"memoryMaxBytes": 12 * GIB}))
        self.authority().ledger.attach_unit(first.reservation_id, "worldline-x.service")
        blind = self.authority(is_live=lambda r: None)
        second = blind.admit(workload="claude", policy=ResourcePolicy.from_mapping({"memoryMaxBytes": 12 * GIB}))
        self.assertEqual(second.outcome, RESOURCES_UNAVAILABLE,
                         "capacity held by a workload we could not ask about was promised again")
        self.assertEqual(second.arithmetic["outstandingCount"], 1)

    def test_an_unanswerable_manager_does_not_delete_the_ledger(self) -> None:
        first = self.authority().admit(workload="terra", policy=ResourcePolicy.from_mapping({"memoryMaxBytes": GIB}))
        self.authority().ledger.attach_unit(first.reservation_id, "worldline-x.service")
        blind = self.authority(is_live=lambda r: None)
        blind.admit(workload="claude", policy=ResourcePolicy.from_mapping({"memoryMaxBytes": GIB}))
        self.assertEqual(len(self.ledger.outstanding()), 2,
                         "an admission during an outage destroyed a live workload's record")
        self.assertEqual(blind.reconcile(), [], "reconcile removed a reservation it could not ask about")

    def test_a_callback_that_raises_is_treated_as_unknown_not_as_dead(self) -> None:
        """A foreign unit name in the ledger used to wedge reconcile permanently."""
        first = self.authority().admit(workload="terra", policy=ResourcePolicy.from_mapping({"memoryMaxBytes": GIB}))
        self.ledger._store([Reservation(first.reservation_id, "terra", "sshd.service", GIB, 0, 0, 1)])

        def explode(_reservation):
            raise WorldlineError("FOREIGN_SYSTEMD_UNIT", "refusing to manage a non-WORLDLINE unit")

        authority = self.authority(is_live=explode)
        self.assertEqual(authority.reconcile(), [])
        self.assertEqual(len(self.ledger.outstanding()), 1)

    def test_a_reservation_cannot_name_something_that_is_not_a_unit(self) -> None:
        first = self.authority().admit(workload="terra", policy=ResourcePolicy.from_mapping({"memoryMaxBytes": GIB}))
        for bad in ("../../etc/passwd", "a\nb", ""):
            with self.subTest(unit=bad):
                with self.assertRaises(WorldlineError):
                    self.ledger.attach_unit(first.reservation_id, bad)

    # ---- major: observation accepted impossible and non-finite readings -----------------------
    def test_an_impossible_meminfo_is_not_a_measurement(self) -> None:
        """A corrupt MemAvailable of 1 PiB licensed an 8 TiB admission on a 31 GiB machine."""
        root = fixture_root(self.base / "impossible", available_kb=9_007_199_254_740_992)
        self.assertEqual(observe({}, root=root).state, "UNKNOWN")
        self.assertEqual(self.authority(root=root).admit(
            workload="terra", policy=ResourcePolicy.from_mapping({"memoryMaxBytes": 8 * 1024 * GIB})).outcome,
            RESOURCE_STATE_UNKNOWN)

    def test_non_finite_pressure_refuses_instead_of_raising(self) -> None:
        for value in ("inf", "-inf", "nan", "1e400", "-50.00", "200.00"):
            with self.subTest(pressure=value):
                root = fixture_root(self.base / f"psi-{value}", pressure=f"some avg10={value} avg60=0.00 avg300=0.00 total=1\n")
                self.assertEqual(observe({}, root=root).state, "UNKNOWN")

    # ---- major: a memoryHigh-only policy was unmetered while the kernel throttled it ----------
    def test_a_memory_high_only_policy_is_accounted_and_says_it_is_enforced(self) -> None:
        policy = ResourcePolicy.from_mapping({"memoryHighBytes": 12 * GIB})
        self.assertIn("MemoryHigh=12884901888", policy.unit_properties())
        decision = self.authority().admit(workload="terra", policy=policy)
        self.assertEqual(decision.outcome, ADMITTED)
        self.assertTrue(decision.arithmetic["accounted"], "a real ceiling was reached with nothing reserved")
        self.assertNotIn("UNMETERED", decision.reason)
        self.assertEqual(self.authority().admit(workload="claude", policy=policy).outcome, RESOURCES_UNAVAILABLE)

    def test_enforcement_none_says_nothing_is_enforced(self) -> None:
        policy = ResourcePolicy.from_mapping({"memoryMaxBytes": 4 * GIB, "enforcement": "none"})
        decision = self.authority().admit(workload="terra", policy=policy)
        self.assertEqual(decision.outcome, ADMITTED)
        self.assertIn("NOTHING is enforced", decision.reason)
        self.assertFalse(self.authority().report(policy)["enforced"])


if __name__ == "__main__":
    unittest.main()
