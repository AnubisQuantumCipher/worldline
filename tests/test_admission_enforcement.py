"""Does the kernel actually take the ceiling, and does it follow the workload's children?

A configured `memoryMaxBytes` is not evidence that Linux enforced anything. These controls launch
real transient units, read the ceiling back out of the kernel's own cgroup files, build a process
tree several levels deep and check every descendant is inside the same accounting boundary, and
drive a workload into its ceiling to see the kernel stop it.

Everything is confined to a WORLDLINE transient unit with its own cgroup. Nothing here can take
memory from the host: that is the whole point of the mechanism under test.
"""
from __future__ import annotations

import os
import subprocess
import sys
import textwrap
import time
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "runtime"))

from worldline.admission import GIB, MIB, ResourcePolicy  # noqa: E402
from worldline.errors import WorldlineError  # noqa: E402
from worldline.linux.systemd import SystemdAdapter  # noqa: E402

import uuid  # noqa: E402


def manager_available() -> str | None:
    try:
        adapter = SystemdAdapter()
        adapter.verify_manager()
    except Exception as exc:  # noqa: BLE001 - any failure means "not testable here"
        return str(exc)
    return None


class Enforcement(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        reason = manager_available()
        if reason:
            raise unittest.SkipTest(f"no reachable user service manager: {reason}")
        if not Path("/sys/fs/cgroup/cgroup.controllers").exists():
            raise unittest.SkipTest("cgroup v2 is not mounted here")
        cls.adapter = SystemdAdapter()

    def setUp(self) -> None:
        self.instance = str(uuid.uuid4())
        self.unit = SystemdAdapter.unit_name(self.instance)
        self.addCleanup(self._cleanup)

    def _cleanup(self) -> None:
        try:
            subprocess.run(["systemctl", "--user", "stop", self.unit], stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, timeout=30, env=self.adapter.environment)
        except Exception:  # noqa: BLE001
            pass

    def _launch(self, script: str, policy: ResourcePolicy):
        return self.adapter.launch(
            self.instance, [sys.executable, "-c", script],
            description="worldline admission enforcement control",
            resource_properties=policy.unit_properties(),
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def _wait_for_cgroup(self, timeout: float = 20.0) -> dict:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            limits = self.adapter.effective_limits(self.unit)
            if limits.get("cgroupReadable"):
                return limits
            time.sleep(0.1)
        return self.adapter.effective_limits(self.unit)

    # ---- requested is not effective ---------------------------------------------------------
    def test_the_kernel_holds_the_ceiling_that_was_requested(self) -> None:
        policy = ResourcePolicy.from_mapping({"memoryMaxBytes": 256 * MIB, "tasksMax": 64, "cpuQuotaPercent": 50})
        process = self._launch("import time; time.sleep(25)", policy)
        try:
            limits = self._wait_for_cgroup()
            self.assertEqual(limits["state"], "OBSERVED", limits)
            self.assertTrue(limits["cgroupReadable"], f"the unit's cgroup could not be read: {limits}")
            self.assertEqual(limits["kernel"]["memory.max"], str(256 * MIB),
                             "the kernel does not hold the ceiling the policy asked for")
            self.assertEqual(limits["kernel"]["pids.max"], "64")
            self.assertEqual(limits["systemd"]["MemoryMax"], str(256 * MIB))
            # CPUQuota 50% of one core, expressed by the kernel as quota/period microseconds.
            quota, _, period = (limits["kernel"]["cpu.max"] or "").partition(" ")
            self.assertTrue(quota.isdigit() and period.isdigit(), limits["kernel"]["cpu.max"])
            self.assertAlmostEqual(int(quota) / int(period), 0.5, places=2)
        finally:
            process.stop()
            process.launcher.wait(timeout=30)

    def test_an_unenforced_policy_is_visible_as_such(self) -> None:
        """enforcement: none asks the kernel for nothing, and the readback shows no ceiling."""
        policy = ResourcePolicy.from_mapping({"memoryMaxBytes": 256 * MIB, "enforcement": "none"})
        process = self._launch("import time; time.sleep(20)", policy)
        try:
            limits = self._wait_for_cgroup()
            self.assertEqual(limits["kernel"]["memory.max"], "max",
                             "a policy that enforces nothing must not look enforced")
        finally:
            process.stop()
            process.launcher.wait(timeout=30)

    # ---- the budget follows the workload tree -------------------------------------------------
    def test_every_descendant_is_inside_the_same_accounting_boundary(self) -> None:
        """agent -> python -> shell -> python -> child. The budget must not escape at the first fork."""
        script = textwrap.dedent("""
            import os, subprocess, sys, time
            def cgroup(pid="self"):
                with open(f"/proc/{pid}/cgroup") as handle:
                    return handle.read().strip().split(":")[-1]
            print("L1", os.getpid(), cgroup(), flush=True)
            inner = "import os,sys,subprocess,time\\n" \\
                    "cg=lambda: open('/proc/self/cgroup').read().strip().split(':')[-1]\\n" \\
                    "print('L3', os.getpid(), cg(), flush=True)\\n" \\
                    "p=subprocess.Popen([sys.executable,'-c'," \\
                    "\\"import os;print('L4',os.getpid(),open('/proc/self/cgroup').read().strip().split(':')[-1],flush=True);import time;time.sleep(6)\\"])\\n" \\
                    "time.sleep(6)\\n"
            shell = subprocess.Popen(["/bin/sh", "-c", f"echo L2 $$ $(cat /proc/self/cgroup | tail -1 | cut -d: -f3); exec {sys.executable} -c \\"$0\\"", inner])
            time.sleep(8)
        """)
        policy = ResourcePolicy.from_mapping({"memoryMaxBytes": 512 * MIB, "tasksMax": 128})
        process = self._launch(script, policy)
        try:
            limits = self._wait_for_cgroup()
            expected = limits.get("controlGroup")
            self.assertTrue(expected, f"no control group for the unit: {limits}")
            output = process.launcher.stdout.read().decode("utf-8", "replace") if process.launcher.stdout else ""
            process.launcher.wait(timeout=60)
            levels = {}
            for line in output.splitlines():
                parts = line.split()
                if len(parts) == 3 and parts[0].startswith("L"):
                    levels[parts[0]] = parts[2]
            self.assertGreaterEqual(len(levels), 4, f"the process tree did not report four levels: {output!r}")
            for name, group in sorted(levels.items()):
                self.assertEqual(group, expected,
                                 f"{name} escaped the unit's cgroup: {group} != {expected}\n{output}")
        finally:
            process.stop()

    # ---- telemetry is measured while the unit lives ---------------------------------------------
    def test_peak_memory_is_measured_for_a_running_workload(self) -> None:
        """Telemetry must be sampled before the unit is collected. `--collect` removes a finished
        unit, and with it the cgroup, so a reading taken after exit measures nothing — which is
        why the runner samples at the end of the run rather than after it."""
        script = "b = bytearray(160 * 1024 * 1024)\nfor i in range(0, len(b), 4096): b[i] = 1\nimport time; time.sleep(20)"
        policy = ResourcePolicy.from_mapping({"memoryMaxBytes": 512 * MIB, "tasksMax": 64})
        process = self._launch(script, policy)
        try:
            peak = None
            deadline = time.monotonic() + 40
            while time.monotonic() < deadline:
                reading = self.adapter.resource_telemetry(self.unit)
                if reading.get("state") == "OBSERVED" and (reading.get("peakMemoryBytes") or 0) > 120 * MIB:
                    peak = reading
                    break
                time.sleep(0.2)
            self.assertIsNotNone(peak, "no peak memory was ever observed for a workload that touched 160 MiB")
            self.assertGreater(peak["peakMemoryBytes"], 120 * MIB)
            self.assertLess(peak["peakMemoryBytes"], 512 * MIB)
            self.assertFalse(peak["hitMemoryCeiling"], "a workload well under its ceiling must not look throttled")
            self.assertIsNotNone(peak["memoryEvents"], "memory.events should be readable while the unit lives")
        finally:
            process.stop()
            process.launcher.wait(timeout=30)

    # ---- the ceiling actually stops a workload -------------------------------------------------
    def test_a_workload_that_allocates_past_its_ceiling_is_stopped_and_recorded(self) -> None:
        """192 MiB ceiling, no swap, and a workload that wants far more. The kernel must stop it
        and leave a record. Sampling starts immediately, because a unit that dies is collected."""
        script = textwrap.dedent("""
            import time
            blocks = []
            try:
                while True:
                    block = bytearray(8 * 1024 * 1024)
                    for i in range(0, len(block), 4096):
                        block[i] = 1
                    blocks.append(block)
                    time.sleep(0.02)
            except MemoryError:
                time.sleep(30)
        """)
        policy = ResourcePolicy.from_mapping({"memoryMaxBytes": 192 * MIB, "memorySwapMaxBytes": 1, "tasksMax": 64})
        process = self._launch(script, policy)
        try:
            hit = None
            deadline = time.monotonic() + 90
            while time.monotonic() < deadline:
                reading = self.adapter.resource_telemetry(self.unit)
                if reading.get("state") == "OBSERVED" and reading.get("hitMemoryCeiling"):
                    hit = reading
                    break
                if process.launcher.poll() is not None and reading.get("state") != "OBSERVED":
                    break
                time.sleep(0.05)
            self.assertIsNotNone(hit, "the workload allocated far past its ceiling and nothing recorded it")
            self.assertTrue(hit["hitMemoryCeiling"])
            self.assertLessEqual(hit["peakMemoryBytes"] or 0, 256 * MIB,
                                 "the kernel let the workload exceed its ceiling by more than slack")
            events = hit["memoryEvents"] or {}
            self.assertTrue(events.get("max", 0) or events.get("oom", 0) or events.get("oom_kill", 0),
                            f"no memory.events counter moved: {events}")
        finally:
            process.stop()

    # ---- telemetry that could not be collected says so ------------------------------------------
    def test_telemetry_for_a_unit_that_does_not_exist_is_unavailable_not_zero(self) -> None:
        reading = self.adapter.resource_telemetry(SystemdAdapter.unit_name(str(uuid.uuid4())))
        self.assertIn(reading.get("state"), ("UNAVAILABLE", "OBSERVED"))
        if reading.get("state") == "OBSERVED":
            self.assertIsNone(reading.get("peakMemoryBytes"),
                              "a peak that was never measured must be absent, not zero")

    def test_a_malformed_resource_property_is_refused_before_launch(self) -> None:
        with self.assertRaises(WorldlineError) as caught:
            self.adapter.launch(self.instance, ["/bin/true"], description="control",
                                resource_properties=["MemoryMax=1\nExecStart=/bin/evil"])
        self.assertEqual(caught.exception.args[0], "RESOURCE_POLICY_INVALID")


if __name__ == "__main__":
    unittest.main()
