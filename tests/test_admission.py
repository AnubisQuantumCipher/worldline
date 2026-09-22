"""Controls for the resource admission authority.

The one that matters most is `test_two_simultaneous_admissions_cannot_both_take_the_same_memory`:
it runs two real processes against one real ledger, because the failure this module exists to
prevent is exactly the one a single-threaded test cannot see.

Nothing here touches the real disk's free space or another session's processes. Disk pressure is
tested by raising the floor, not by filling a filesystem; the machine's `/proc` is replaced by a
fixture root wherever a reading has to be made to fail.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "runtime"))

from worldline.admission import (  # noqa: E402
    ADMITTED, GIB, MIB, RESOURCES_UNAVAILABLE, RESOURCE_POLICY_INVALID, RESOURCE_STATE_UNKNOWN,
    AdmissionAuthority, AdmissionState, Floors, Ledger, Reservation, ResourcePolicy, observe,
)
from worldline.errors import WorldlineError  # noqa: E402

MEMINFO = """MemTotal:       32798844 kB
MemFree:         1000000 kB
MemAvailable:   {available} kB
SwapTotal:      32798716 kB
SwapFree:       23225108 kB
"""
PRESSURE = "some avg10={avg10} avg60=0.00 avg300=0.00 total=1\nfull avg10=0.00 avg60=0.00 avg300=0.00 total=0\n"


def fixture_root(directory: Path, *, available_kb: int = 20_000_000, memory_avg10: str = "0.00",
                 meminfo: str | None = None, pressure: str | None = None,
                 omit: tuple[str, ...] = ()) -> Path:
    (directory / "proc/pressure").mkdir(parents=True, exist_ok=True)
    if "meminfo" not in omit:
        (directory / "proc/meminfo").write_text(meminfo if meminfo is not None
                                                else MEMINFO.format(available=available_kb), encoding="utf-8")
    for name in ("memory", "cpu", "io"):
        if name in omit:
            continue
        (directory / f"proc/pressure/{name}").write_text(
            pressure if pressure is not None and name == "memory" else PRESSURE.format(avg10=memory_avg10),
            encoding="utf-8")
    return directory


class AdmissionControls(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-admission-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root = fixture_root(self.base / "root")
        self.ledger = Ledger(self.base / "runtime")

    def authority(self, *, floors: Floors | None = None, root: Path | None = None,
                  usage=None, is_live=None, paths=None) -> AdmissionAuthority:
        return AdmissionAuthority(
            self.ledger, floors or Floors(min_free_memory_bytes=2 * GIB),
            paths=paths or {},
            observer=lambda: observe(paths or {}, root=root or self.root),
            usage=usage, is_live=is_live)

    def policy(self, **overrides) -> ResourcePolicy:
        return ResourcePolicy.from_mapping({"memoryMaxBytes": 12 * GIB, "tasksMax": 4096, **overrides})

    # ---- the motivating scenario ---------------------------------------------------------------
    def test_the_second_expensive_world_is_refused_with_the_arithmetic_recorded(self) -> None:
        """Terra 12 GiB, Claude 12 GiB, ~20 GiB available: one starts, one is told why it cannot."""
        authority = self.authority()
        first = authority.admit(workload="terra", policy=self.policy())
        self.assertEqual(first.outcome, ADMITTED, first.reason)
        second = authority.admit(workload="claude", policy=self.policy())
        self.assertEqual(second.outcome, RESOURCES_UNAVAILABLE)
        self.assertEqual(second.arithmetic["requestedBytes"], 12 * GIB)
        self.assertEqual(second.arithmetic["withheldByReservationsBytes"], 12 * GIB)
        self.assertEqual(second.arithmetic["outstandingCount"], 1)
        self.assertLess(second.arithmetic["headroomBytes"], 12 * GIB)
        self.assertIn("terra", json.dumps(second.arithmetic))

    def test_releasing_the_first_admits_the_second(self) -> None:
        authority = self.authority()
        first = authority.admit(workload="terra", policy=self.policy())
        self.assertTrue(authority.release(first.reservation_id))
        self.assertEqual(authority.admit(workload="claude", policy=self.policy()).outcome, ADMITTED)

    def test_a_running_workloads_used_memory_is_not_withheld_twice(self) -> None:
        """MemAvailable already reflects what a running workload took. Withholding its whole
        reservation on top of that would refuse work the machine can actually do."""
        authority = self.authority(usage=lambda r: 11 * GIB)
        first = authority.admit(workload="terra", policy=self.policy())
        self.assertEqual(first.outcome, ADMITTED)
        second = authority.admit(workload="claude", policy=self.policy(memoryMaxBytes=5 * GIB))
        self.assertEqual(second.outcome, ADMITTED, second.reason)
        self.assertEqual(second.arithmetic["withheldByReservationsBytes"], 1 * GIB)

    # ---- the race this module exists to prevent ------------------------------------------------
    def test_two_simultaneous_admissions_cannot_both_take_the_same_memory(self) -> None:
        program = textwrap.dedent(f"""
            import json, sys, time
            sys.path.insert(0, {str(REPO / 'runtime')!r})
            from pathlib import Path
            from worldline.admission import AdmissionAuthority, Floors, Ledger, ResourcePolicy, observe, GIB
            root = Path({str(self.root)!r})
            authority = AdmissionAuthority(Ledger(Path({str(self.base / 'runtime')!r})),
                                           Floors(min_free_memory_bytes=2 * GIB),
                                           observer=lambda: observe({{}}, root=root))
            policy = ResourcePolicy.from_mapping({{"memoryMaxBytes": 12 * GIB}})
            start = float(sys.argv[2])
            while time.time() < start:
                time.sleep(0.001)
            decision = authority.admit(workload=sys.argv[1], policy=policy)
            print(json.dumps({{"outcome": decision.outcome, "reason": decision.reason}}))
        """)
        script = self.base / "race.py"
        script.write_text(program, encoding="utf-8")
        start = time.time() + 1.0
        processes = [subprocess.Popen([sys.executable, str(script), name, str(start)],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                     for name in ("terra", "claude")]
        outcomes = []
        for process in processes:
            out, err = process.communicate(timeout=120)
            self.assertEqual(process.returncode, 0, err)
            outcomes.append(json.loads(out.strip())["outcome"])
        self.assertEqual(sorted(outcomes), [ADMITTED, RESOURCES_UNAVAILABLE],
                         f"both admissions succeeded against the same memory: {outcomes}")
        self.assertEqual(len(self.ledger.outstanding()), 1, "exactly one reservation should exist")

    # ---- unknown is not insufficient -----------------------------------------------------------
    def test_unreadable_meminfo_refuses_as_unknown_not_as_insufficient(self) -> None:
        root = fixture_root(self.base / "nomem", omit=("meminfo",))
        decision = self.authority(root=root).admit(workload="terra", policy=self.policy())
        self.assertEqual(decision.outcome, RESOURCE_STATE_UNKNOWN)
        self.assertIn("meminfo", decision.reason)
        self.assertEqual(self.ledger.outstanding(), [], "an unobservable machine must reserve nothing")

    def test_malformed_pressure_refuses_as_unknown(self) -> None:
        root = fixture_root(self.base / "badpsi", pressure="this is not pressure data\n")
        decision = self.authority(root=root).admit(workload="terra", policy=self.policy())
        self.assertEqual(decision.outcome, RESOURCE_STATE_UNKNOWN)
        self.assertIn("pressure", decision.reason)

    def test_absent_memory_pressure_accounting_refuses_as_unknown(self) -> None:
        root = fixture_root(self.base / "nopsi", omit=("memory",))
        decision = self.authority(root=root).admit(workload="terra", policy=self.policy())
        self.assertEqual(decision.outcome, RESOURCE_STATE_UNKNOWN)

    def test_absent_cpu_and_io_pressure_are_tolerated(self) -> None:
        """Only memory pressure gates admission, so a kernel without the others still works."""
        root = fixture_root(self.base / "memonly", omit=("cpu", "io"))
        state = observe({}, root=root)
        self.assertEqual(state.state, "OBSERVED")
        self.assertIsNone(state.cpu_pressure_avg10)

    def test_a_corrupt_ledger_is_unknown_rather_than_empty(self) -> None:
        """An unreadable ledger read as empty would admit everything at exactly the moment the
        accounting broke."""
        self.ledger.path.write_text("{ not json", encoding="utf-8")
        decision = self.authority().admit(workload="terra", policy=self.policy())
        self.assertEqual(decision.outcome, RESOURCE_STATE_UNKNOWN)
        with self.assertRaises(WorldlineError):
            self.ledger.outstanding()

    def test_a_ledger_holding_a_bad_record_is_unknown(self) -> None:
        self.ledger.path.write_text(json.dumps({"schemaVersion": 1, "reservations": [{"nope": 1}]}), encoding="utf-8")
        self.assertEqual(self.authority().admit(workload="t", policy=self.policy()).outcome, RESOURCE_STATE_UNKNOWN)

    # ---- pressure and disk floors --------------------------------------------------------------
    def test_memory_pressure_above_the_ceiling_refuses(self) -> None:
        root = fixture_root(self.base / "hot", memory_avg10="75.00")
        decision = self.authority(root=root).admit(workload="terra", policy=self.policy(memoryMaxBytes=MIB))
        self.assertEqual(decision.outcome, RESOURCES_UNAVAILABLE)
        self.assertIn("pressure", decision.reason)

    def test_disk_below_the_floor_refuses_without_filling_any_filesystem(self) -> None:
        lab = self.base / "lab"
        lab.mkdir()
        floors = Floors(min_free_memory_bytes=2 * GIB, min_free_disk_bytes=1 << 62)
        authority = AdmissionAuthority(self.ledger, floors, paths={"lab": lab},
                                       observer=lambda: observe({"lab": lab}, root=self.root))
        decision = authority.admit(workload="terra", policy=self.policy(memoryMaxBytes=MIB))
        self.assertEqual(decision.outcome, RESOURCES_UNAVAILABLE)
        self.assertIn("lab", decision.reason)
        self.assertIn("below the floor", decision.reason)

    def test_inodes_below_the_floor_refuse(self) -> None:
        lab = self.base / "lab2"
        lab.mkdir()
        floors = Floors(min_free_memory_bytes=2 * GIB, min_free_inodes=1 << 40)
        authority = AdmissionAuthority(self.ledger, floors, paths={"lab": lab},
                                       observer=lambda: observe({"lab": lab}, root=self.root))
        decision = authority.admit(workload="terra", policy=self.policy(memoryMaxBytes=MIB))
        self.assertEqual(decision.outcome, RESOURCES_UNAVAILABLE)
        self.assertIn("inodes", decision.reason)

    # ---- concurrency ceiling --------------------------------------------------------------------
    def test_the_concurrency_ceiling_refuses_even_with_memory_to_spare(self) -> None:
        policy = self.policy(memoryMaxBytes=MIB, maxConcurrentWorkloads=2)
        authority = self.authority()
        self.assertEqual(authority.admit(workload="a", policy=policy).outcome, ADMITTED)
        self.assertEqual(authority.admit(workload="b", policy=policy).outcome, ADMITTED)
        third = authority.admit(workload="c", policy=policy)
        self.assertEqual(third.outcome, RESOURCES_UNAVAILABLE)
        self.assertIn("concurrency ceiling", third.reason)

    # ---- orphans and restart --------------------------------------------------------------------
    def test_a_reservation_whose_workload_is_gone_is_reconciled_away(self) -> None:
        authority = self.authority()
        first = authority.admit(workload="terra", policy=self.policy())
        authority.attach_unit(first.reservation_id, "worldline-dead.service")
        dead = self.authority(is_live=lambda r: False)
        dropped = dead.reconcile()
        self.assertEqual([r.reservation_id for r in dropped], [first.reservation_id])
        self.assertEqual(self.ledger.outstanding(), [])

    def test_admission_ignores_reservations_whose_workload_is_gone(self) -> None:
        """A daemon killed between reserving and releasing must not hold capacity forever."""
        self.authority().admit(workload="terra", policy=self.policy())
        live_again = self.authority(is_live=lambda r: False)
        decision = live_again.admit(workload="claude", policy=self.policy())
        self.assertEqual(decision.outcome, ADMITTED, decision.reason)
        self.assertEqual(decision.arithmetic["outstandingCount"], 0)

    def test_the_ledger_survives_a_new_authority_object(self) -> None:
        self.authority().admit(workload="terra", policy=self.policy())
        self.assertEqual(len(Ledger(self.base / "runtime").outstanding()), 1)

    def test_releasing_an_unknown_reservation_is_false_not_an_error(self) -> None:
        self.assertFalse(self.authority().release("00000000-0000-4000-8000-000000000000"))
        self.assertFalse(self.authority().release(None))

    # ---- policy validation ----------------------------------------------------------------------
    def test_absurd_negative_and_overflowing_limits_are_refused(self) -> None:
        for value in (-1, 0, 1 << 60, True):
            with self.subTest(value=value):
                with self.assertRaises(WorldlineError) as caught:
                    ResourcePolicy.from_mapping({"memoryMaxBytes": value})
                self.assertEqual(caught.exception.args[0], RESOURCE_POLICY_INVALID)

    def test_unknown_policy_fields_are_refused(self) -> None:
        with self.assertRaises(WorldlineError):
            ResourcePolicy.from_mapping({"memoryMaxBytes": GIB, "memoryMaxGB": 12})

    def test_memory_high_above_memory_max_is_refused(self) -> None:
        with self.assertRaises(WorldlineError):
            ResourcePolicy.from_mapping({"memoryMaxBytes": GIB, "memoryHighBytes": 2 * GIB})

    def test_a_workload_with_no_declared_appetite_is_refused(self) -> None:
        decision = self.authority().admit(workload="terra", policy=ResourcePolicy.from_mapping({}))
        self.assertEqual(decision.outcome, RESOURCE_POLICY_INVALID)
        self.assertIn("undeclared", decision.reason)

    # ---- what the policy asks the kernel for -----------------------------------------------------
    def test_the_policy_becomes_cgroup_properties_with_accounting_always_on(self) -> None:
        properties = ResourcePolicy.from_mapping({
            "memoryMaxBytes": 12 * GIB, "memoryHighBytes": 11 * GIB, "memorySwapMaxBytes": GIB,
            "cpuQuotaPercent": 400, "cpuWeight": 200, "tasksMax": 512}).unit_properties()
        self.assertIn("MemoryMax=12884901888", properties)
        self.assertIn("MemoryHigh=11811160064", properties)
        self.assertIn("MemorySwapMax=1073741824", properties)
        self.assertIn("CPUQuota=400%", properties)
        self.assertIn("CPUWeight=200", properties)
        self.assertIn("TasksMax=512", properties)
        for accounting in ("MemoryAccounting=yes", "CPUAccounting=yes", "TasksAccounting=yes", "IOAccounting=yes"):
            self.assertIn(accounting, properties, "telemetry that was never collected is not evidence")

    def test_enforcement_none_asks_the_kernel_for_nothing(self) -> None:
        self.assertEqual(ResourcePolicy.from_mapping({"memoryMaxBytes": GIB, "enforcement": "none"}).unit_properties(), [])

    # ---- the report doctor shows ------------------------------------------------------------------
    def test_the_report_states_headroom_and_whether_work_would_be_admitted(self) -> None:
        authority = self.authority()
        report = authority.report(self.policy())
        self.assertEqual(report["state"]["state"], "OBSERVED")
        self.assertTrue(report["wouldAdmitNow"])
        authority.admit(workload="terra", policy=self.policy())
        after = authority.report(self.policy())
        self.assertFalse(after["wouldAdmitNow"])
        self.assertEqual(after["withheldBytes"], 12 * GIB)

    def test_the_report_says_unknown_rather_than_guessing(self) -> None:
        report = self.authority(root=fixture_root(self.base / "blind", omit=("meminfo",))).report(self.policy())
        self.assertEqual(report["state"]["state"], "UNKNOWN")
        self.assertIsNone(report["wouldAdmitNow"])


if __name__ == "__main__":
    unittest.main()
