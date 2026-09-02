from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from worldline.core import Core
from worldline.errors import WorldlineError
from worldline.linux.namespaces import BubblewrapSandbox
from worldline.linux.systemd import SystemdAdapter
from worldline.model import WorldState
from worldline.paths import WorldlinePaths
from worldline.roots import RootManager
from worldline.simulation import SystemSimulation
from worldline.store import StateStore
from worldline.transaction import CollapseTransaction


class SimulationTests(unittest.TestCase):
    def test_system_future_runs_without_system_collapse(self) -> None:
        capability = SystemdAdapter.capability()
        if capability["state"] != "AVAILABLE":
            self.skipTest(capability["reason"])
        with tempfile.TemporaryDirectory(prefix="worldline-simulation-") as temporary:
            root = Path(temporary)
            env = {
                "HOME": str(root / "home"),
                "XDG_DATA_HOME": str(root / "data"),
                "XDG_STATE_HOME": str(root / "state"),
                "XDG_CONFIG_HOME": str(root / "config"),
                "XDG_RUNTIME_DIR": str(root / "runtime"),
            }
            for value in env.values():
                Path(value).mkdir(mode=0o700, parents=True, exist_ok=True)
            paths = WorldlinePaths.from_environment(env)
            core = Core.shared()
            store = StateStore(paths, core)
            try:
                work = root / "work"
                work.mkdir()
                (work / "state.txt").write_text("prime", encoding="utf-8")
                RootManager(paths, store, core=core, toolchains=()).register([work], confirmed=True)
                simulation = SystemSimulation(
                    paths,
                    store,
                    BubblewrapSandbox(paths),
                    SystemdAdapter(),
                    core=core,
                )
                future = simulation.run(
                    ["/usr/bin/pacman", "-Q"],
                    health_checks=[
                        {
                            "id": "os-release",
                            "kind": "health",
                            "argv": ["/usr/bin/test", "-f", "/etc/os-release"],
                            "required": True,
                        }
                    ],
                    timeout=60,
                )
                self.assertEqual(future.world_kind, "system")
                self.assertEqual(future.state, WorldState.VALID)
                self.assertEqual((work / "state.txt").read_text(encoding="utf-8"), "prime")
                with self.assertRaises(WorldlineError) as denied:
                    CollapseTransaction(paths, store, core=core).prepare(future.alias)
                self.assertEqual(denied.exception.code, "SYSTEM_ROOT_COLLAPSE_UNSUPPORTED")
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
