from __future__ import annotations

import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest

from worldline.client import DaemonClient
from worldline.paths import WorldlinePaths


class RaceTests(unittest.TestCase):
    def test_three_agents_share_parent_but_not_upper_directories(self) -> None:
        with tempfile.TemporaryDirectory(prefix="worldline-race-") as temporary:
            root = Path(temporary)
            env_paths = {
                "HOME": str(root / "home"),
                "XDG_DATA_HOME": str(root / "data"),
                "XDG_STATE_HOME": str(root / "state"),
                "XDG_CONFIG_HOME": str(root / "config"),
                "XDG_RUNTIME_DIR": str(root / "runtime"),
            }
            for value in env_paths.values():
                Path(value).mkdir(mode=0o700, parents=True, exist_ok=True)
            work = root / "fixture"
            work.mkdir()
            (work / "base.txt").write_text("prime", encoding="utf-8")
            agent_script = work / "race_agent.py"
            agent_script.write_text(
                """import json
from pathlib import Path
import sys
workspace = Path(sys.argv[1])
label = sys.argv[4]
(workspace / ('candidate-' + label + '.txt')).write_text(label, encoding='utf-8')
print(json.dumps({'type':'tool-event','actor':label,'path':str(workspace / ('candidate-' + label + '.txt')),'line':1}), flush=True)
""",
                encoding="utf-8",
            )
            config_dir = Path(env_paths["XDG_CONFIG_HOME"]) / "worldline"
            config_dir.mkdir(mode=0o700)
            commands = {}
            for name in ("fixture-a", "fixture-b", "fixture-c"):
                commands[name] = {
                    "argv": [
                        "/usr/bin/python3",
                        str(agent_script),
                        "{workspace}",
                        "{missionFile}",
                        "{worldState}",
                        name,
                    ],
                    "credentialMounts": [],
                    "eventFormat": "jsonl",
                }
            config_file = config_dir / "config.json"
            config_file.write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "readonlyHomePaths": [],
                        "agentCommands": commands,
                        "ghosts": {"enabled": False, "agent": None},
                    }
                ),
                encoding="utf-8",
            )
            os.chmod(config_file, 0o600)
            paths = WorldlinePaths.from_environment(env_paths)
            daemon_env = {
                **os.environ,
                **env_paths,
                "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "runtime"),
                "PYTHONDONTWRITEBYTECODE": "1",
                "WORLDLINE_CORE_LIB": str(Path(__file__).resolve().parents[1] / "lib/libworldline_core.so"),
            }
            error_log = root / "worldlined.stderr"
            with error_log.open("wb") as errors:
                daemon = subprocess.Popen(
                    [sys.executable, "-m", "worldline.daemon_main"],
                    env=daemon_env,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=errors,
                )
                try:
                    deadline = time.monotonic() + 15
                    while not paths.socket.exists() and daemon.poll() is None and time.monotonic() < deadline:
                        time.sleep(0.02)
                    if daemon.poll() is not None or not paths.socket.exists():
                        self.fail(error_log.read_text(encoding="utf-8", errors="replace"))
                    client = DaemonClient(paths, timeout=120)
                    client.request("init", {"roots": [str(work)], "kind": None, "primary": None, "confirmed": True})
                    race = client.request(
                        "race",
                        {
                            "agents": ["fixture-a", "fixture-b", "fixture-c"],
                            "mission": "build three independent candidates",
                            "detach": False,
                        },
                    )
                    self.assertEqual([item["alias"] for item in race], ["alpha", "beta", "gamma"])
                    self.assertEqual({item["state"] for item in race}, {"VALID"})
                    records = [client.request("show", {"world": alias}) for alias in ("alpha", "beta", "gamma")]
                    self.assertEqual(len({item["parent_instance"] for item in records}), 1)
                    self.assertEqual(len({item["base_payload_path"] for item in records}), 1)
                    upper_directories = [
                        Path(env_paths["XDG_DATA_HOME"]) / "worldline/overlays" / item["instance_id"]
                        for item in records
                    ]
                    self.assertEqual(len({str(path) for path in upper_directories}), 3)
                    self.assertTrue(all(path.is_dir() for path in upper_directories))
                finally:
                    if daemon.poll() is None:
                        daemon.send_signal(signal.SIGTERM)
                        daemon.wait(timeout=15)
                if daemon.returncode != 0:
                    self.fail(error_log.read_text(encoding="utf-8", errors="replace"))


if __name__ == "__main__":
    unittest.main()
