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

from worldline.errors import WorldlineError
from worldline.client import DaemonClient
from worldline.paths import WorldlinePaths


class EndToEndTests(unittest.TestCase):
    def test_generic_agent_fork_isolated_and_evidenced(self) -> None:
        with tempfile.TemporaryDirectory(prefix="worldline-e2e-") as temporary:
            root = Path(temporary)
            home = root / "home"
            env_paths = {
                "HOME": str(home),
                "XDG_DATA_HOME": str(root / "data"),
                "XDG_STATE_HOME": str(root / "state"),
                "XDG_CONFIG_HOME": str(root / "config"),
                "XDG_RUNTIME_DIR": str(root / "runtime"),
            }
            for value in env_paths.values():
                Path(value).mkdir(mode=0o700, parents=True, exist_ok=True)
            work = root / "fixture"
            work.mkdir()
            (work / "prime.txt").write_text("prime", encoding="utf-8")
            (work / "pyproject.toml").write_text(
                "[project]\nname='fixture'\ndependencies=['alpha==1']\n",
                encoding="utf-8",
            )
            secondary = root / "secondary"
            secondary.mkdir()
            (secondary / "secondary.txt").write_text("secondary prime", encoding="utf-8")
            agent_script = work / "fixture_agent.py"
            agent_script.write_text(
                """import json
from pathlib import Path
import sys
workspace = Path(sys.argv[1])
(workspace / 'candidate.txt').write_text('candidate', encoding='utf-8')
print(json.dumps({'type':'tool-event','actor':'fixture','path':str(workspace / 'candidate.txt'),'line':1,'reason':'deterministic fixture change','session_id':'fixture-session'}), flush=True)
(workspace / 'pyproject.toml').write_text(\"[project]\\nname='fixture'\\ndependencies=['alpha==2', 'beta']\\n\", encoding='utf-8')
""",
                encoding="utf-8",
            )
            (work / ".worldline.json").write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "generated": [{"root": str(work), "glob": "candidate.txt"}],
                        "checks": [
                            {
                                "id": "candidate-exists",
                                "kind": "tests",
                                "argv": ["/usr/bin/test", "-f", "candidate.txt"],
                                "required": True,
                                "format": "exit",
                                "covers": ["candidate.txt"],
                            }
                        ],
                        "services": [],
                    }
                ),
                encoding="utf-8",
            )
            config_dir = Path(env_paths["XDG_CONFIG_HOME"]) / "worldline"
            config_dir.mkdir(mode=0o700)
            (config_dir / "config.json").write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "readonlyHomePaths": [],
                        "agentCommands": {
                            "fixture": {
                                "argv": [
                                    "/usr/bin/python3",
                                    str(agent_script),
                                    "{workspace}",
                                    "{missionFile}",
                                    "{worldState}",
                                ],
                                "credentialMounts": [],
                                "eventFormat": "jsonl",
                            }
                        },
                        "ghosts": {"enabled": False, "agent": None},
                    }
                ),
                encoding="utf-8",
            )
            os.chmod(config_dir / "config.json", 0o600)
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
                    [sys.executable, "-m", "worldline.daemon_main", "--log-level", "DEBUG"],
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
                    initialized = client.request(
                        "init",
                        {
                            "roots": [str(work), str(secondary)],
                            "kind": None,
                            "primary": str(work),
                            "confirmed": True,
                        },
                    )
                    self.assertTrue(initialized["prime"].startswith("sha256:"))
                    result = client.request(
                        "fork",
                        {"name": "alpha", "mission": "make deterministic candidate", "agent": "fixture", "wait": True},
                    )
                    self.assertEqual(result["state"], "VALID")
                    self.assertFalse((work / "candidate.txt").exists())
                    self.assertEqual((secondary / "secondary.txt").read_text(encoding="utf-8"), "secondary prime")
                    shown = client.request("show", {"world": "alpha"})
                    self.assertEqual(shown["evidence"]["summary"], "PASS")
                    self.assertEqual(shown["agent_reference"], "fixture-session")
                    self.assertGreater(len(shown["delta"]["files"]), 0)
                    self.assertGreater(len(client.request("log", {"verify": True})["events"]), 0)
                    environment_manifest = json.loads(
                        (
                            Path(shown["payload_path"])
                            / "manifests"
                            / "environment.json"
                        ).read_text(encoding="utf-8")
                    )
                    self.assertEqual(
                        environment_manifest["processes"][0]["argvDisplay"][0],
                        "/usr/bin/python3",
                    )
                    self.assertTrue(
                        environment_manifest["processes"][0]["safeEnvHash"].startswith("sha256:")
                    )

                    (work / "candidate.txt").write_text("prime conflict", encoding="utf-8")
                    time.sleep(0.05)
                    with self.assertRaises(WorldlineError) as conflict:
                        client.request("collapse.prepare", {"world": "alpha"})
                    self.assertEqual(conflict.exception.code, "CONFLICT")
                    self.assertEqual((work / "candidate.txt").read_text(encoding="utf-8"), "prime conflict")

                    (work / "candidate.txt").unlink()
                    time.sleep(0.05)
                    client.request("status")
                    beta = client.request(
                        "fork",
                        {"name": "beta", "mission": "make clean candidate", "agent": "fixture", "wait": True},
                    )
                    self.assertEqual(beta["state"], "VALID")
                    prepared = client.request("collapse.prepare", {"world": "beta"})
                    collapsed = client.request(
                        "collapse.commit",
                        {"transactionId": prepared["transaction_id"]},
                    )
                    self.assertEqual(collapsed["state"], "COMMITTED")
                    self.assertEqual((work / "candidate.txt").read_text(encoding="utf-8"), "candidate")
                    self.assertEqual((secondary / "secondary.txt").read_text(encoding="utf-8"), "secondary prime")
                    receipt = collapsed["receipt"]
                    self.assertEqual(
                        [item["path"] for item in receipt["mergeSet"]["generatedArtifacts"]],
                        ["candidate.txt"],
                    )
                    self.assertEqual(
                        {(item["name"], item["change"]) for item in receipt["mergeSet"]["dependencyChanges"]},
                        {("alpha", "MODIFY"), ("beta", "ADD")},
                    )
                    why = client.request("why", {"path": str(work / "candidate.txt"), "line": 1})
                    self.assertEqual(why["world"], "beta")
                    self.assertEqual(why["actor"], "fixture")
                    self.assertEqual(why["reason"], "deterministic fixture change")
                    self.assertIsNotNone(why["receipt"])
                    verification = client.request("log", {"verify": True})["verification"]
                    self.assertGreaterEqual(verification["receipts"], 1)

                    return_prepared = client.request("return.prepare", {"world": None})
                    returned = client.request(
                        "collapse.commit",
                        {"transactionId": return_prepared["transaction_id"]},
                    )
                    self.assertEqual(returned["state"], "COMMITTED")
                    self.assertFalse((work / "candidate.txt").exists())
                    self.assertEqual((secondary / "secondary.txt").read_text(encoding="utf-8"), "secondary prime")
                    self.assertIn("alpha==1", (work / "pyproject.toml").read_text(encoding="utf-8"))
                finally:
                    if daemon.poll() is None:
                        daemon.send_signal(signal.SIGTERM)
                        daemon.wait(timeout=15)
                if daemon.returncode != 0:
                    self.fail(error_log.read_text(encoding="utf-8", errors="replace"))


if __name__ == "__main__":
    unittest.main()
