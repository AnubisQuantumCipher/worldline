from __future__ import annotations

import os
from pathlib import Path
import time
import unittest
import uuid

from worldline.linux.cgroups import CgroupAdapter
from worldline.linux.systemd import SystemdAdapter


class SystemdTests(unittest.TestCase):
    def test_stop_kills_complete_worldline_process_tree(self) -> None:
        capability = SystemdAdapter.capability()
        if capability["state"] != "AVAILABLE":
            self.skipTest(capability["reason"])
        adapter = SystemdAdapter()
        instance = str(uuid.uuid4())
        script = (
            "import subprocess; "
            "child=subprocess.Popen(['/usr/bin/sleep','60']); "
            "print(child.pid, flush=True); child.wait()"
        )
        process = adapter.launch(
            instance,
            ["/usr/bin/python3", "-c", script],
            description="WORLDLINE process tree test",
        )
        assert process.launcher.stdout is not None
        child_pid = int(process.launcher.stdout.readline().decode("ascii").strip())
        metadata = adapter.metadata(process.unit)
        self.assertEqual(metadata["ActiveState"], "active")
        cgroup = CgroupAdapter(adapter).capture(process.unit)
        self.assertIn(child_pid, cgroup["pids"])
        process.stop()
        process.launcher.communicate(timeout=15)
        deadline = time.monotonic() + 2
        while Path(f"/proc/{child_pid}").exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        self.assertFalse(Path(f"/proc/{child_pid}").exists())


if __name__ == "__main__":
    unittest.main()
