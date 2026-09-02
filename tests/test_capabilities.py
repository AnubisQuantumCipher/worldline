from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from worldline.capabilities import CapabilityRegistry
from worldline.paths import WorldlinePaths


class CapabilityTests(unittest.TestCase):
    def test_selected_backend_and_unavailable_adapters_are_explicit(self) -> None:
        with tempfile.TemporaryDirectory(prefix="worldline-capabilities-") as temporary:
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
            capabilities = CapabilityRegistry(WorldlinePaths.from_environment(env)).snapshot(refresh=True)
            self.assertEqual(capabilities["selectedBackend"], "overlayfs")
            self.assertEqual(capabilities["overlay"]["state"], "AVAILABLE")
            self.assertIn(capabilities["btrfs"]["state"], {"AVAILABLE", "UNAVAILABLE"})
            if capabilities["btrfs"]["state"] == "UNAVAILABLE":
                self.assertTrue(capabilities["btrfs"]["reason"])
            if capabilities["criu"]["state"] == "UNAVAILABLE":
                self.assertTrue(capabilities["criu"]["reason"])
            self.assertEqual(capabilities["systemRootCollapse"]["state"], "UNAVAILABLE")


if __name__ == "__main__":
    unittest.main()
