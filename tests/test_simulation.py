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
from worldline.admission import AdmissionAuthority, Floors, Gate, Ledger, ResourcePolicy
from worldline.simulation import SystemSimulation
from worldline.store import StateStore
from worldline.transaction import CollapseTransaction


def _system_roots_overlayable(paths: WorldlinePaths) -> str | None:
    """Probe: can every system root the simulation overlays be a lower layer on this host?
    (A vfat /boot or an EFI partition cannot; the engine reports SIMULATION_FAILED there.)
    Returns bubblewrap's message when one cannot, else None."""
    import uuid
    from worldline.linux.namespaces import SandboxSpec
    from worldline.simulation import _SYSTEM_ROOTS
    sandbox = BubblewrapSandbox(paths)
    identifier = str(uuid.uuid4())
    roots = sandbox.overlay_roots(identifier, [(f"system-{p.name}", p, p) for p in _SYSTEM_ROOTS if p.is_dir()], allow_system_roots=True)
    runtime = paths.overlays / identifier / "runtime"
    process = sandbox.launch_world(SandboxSpec(instance_id=identifier, argv=("/usr/bin/true",), cwd=Path("/usr"), environment={"PATH": "/usr/bin"}, roots=roots, runtime=runtime))
    _out, err = process.process.communicate(timeout=60)
    if process.process.returncode != 0 and b"overlay" in err:
        return err.decode("utf-8", "replace").strip()[-300:]
    return None


class SimulationTests(unittest.TestCase):
    def test_system_future_runs_without_system_collapse(self) -> None:
        capability = SystemdAdapter.capability()
        if capability["state"] != "AVAILABLE":
            self.skipTest(capability["reason"])
        with tempfile.TemporaryDirectory(prefix="worldline-simulation-probe-") as probe:
            root = Path(probe)
            env = {name: str(root / name.lower()) for name in ("HOME", "XDG_DATA_HOME", "XDG_STATE_HOME", "XDG_CONFIG_HOME", "XDG_RUNTIME_DIR")}
            for value in env.values():
                Path(value).mkdir(mode=0o700, parents=True, exist_ok=True)
            reason = _system_roots_overlayable(WorldlinePaths.from_environment(env))
            if reason is not None:
                self.skipTest(f"a system root cannot be an overlay lower layer on this host: {reason}")
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
                    Gate(AdmissionAuthority(Ledger(paths.runtime), Floors()), ResourcePolicy.from_mapping({})),
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
