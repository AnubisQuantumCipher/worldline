from __future__ import annotations

from pathlib import Path
import stat
import tempfile
import unittest

from worldline.config import GlobalConfig
from worldline.errors import WorldlineError
from worldline.paths import WorldlinePaths


class ConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-config-")
        root = Path(self.temporary.name)
        env = {
            "HOME": str(root / "home"),
            "XDG_DATA_HOME": str(root / "data"),
            "XDG_STATE_HOME": str(root / "state"),
            "XDG_CONFIG_HOME": str(root / "config"),
            "XDG_RUNTIME_DIR": str(root / "runtime"),
        }
        for value in env.values():
            Path(value).mkdir(mode=0o700, parents=True, exist_ok=True)
        self.paths = WorldlinePaths.from_environment(env)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_default_schema_is_owner_only_and_ghosts_are_disabled(self) -> None:
        config = GlobalConfig.load(self.paths)
        self.assertEqual(
            set(config.value),
            {"schemaVersion", "readonlyHomePaths", "agentCommands", "ghosts", "limits", "network", "anchor"},
        )
        self.assertFalse(config.value["ghosts"]["enabled"])
        self.assertEqual(stat.S_IMODE(self.paths.config_file.stat().st_mode), 0o600)

    def test_generic_adapter_accepts_only_declared_placeholders(self) -> None:
        config = GlobalConfig.default(self.paths)
        config.value["agentCommands"] = {
            "fixture": {
                "argv": ["fixture-agent", "{workspace}", "{missionFile}", "{worldState}"],
                "credentialMounts": [],
                "eventFormat": "jsonl",
            }
        }
        config.save()
        command = config.generic_agent("fixture")
        self.assertEqual(
            command.expand({"workspace": "/work", "missionFile": "/mission", "worldState": "/state"}),
            ("fixture-agent", "/work", "/mission", "/state"),
        )
        config.value["agentCommands"]["fixture"]["argv"] = ["{unsupported}"]
        with self.assertRaises(WorldlineError):
            config.save()


if __name__ == "__main__":
    unittest.main()
