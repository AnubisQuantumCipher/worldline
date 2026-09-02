from __future__ import annotations

import os
from pathlib import Path
import tempfile
import subprocess
import unittest
from unittest.mock import patch

from worldline.core import Core
from worldline.canonical import canonical_bytes
from worldline.environment import (
    EnvironmentCapture,
    OwnedProcess,
    capture_dependencies,
    capture_processes,
    capture_workspace,
    evidence_manifest,
    safe_environment,
)


class EnvironmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-environment-")
        self.root = Path(self.temporary.name)
        self.core = Core.shared()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_safe_environment_never_captures_credentials(self) -> None:
        captured = safe_environment(
            {
                "LANG": "en_US.UTF-8",
                "PATH": "/usr/bin",
                "XDG_CONFIG_HOME": "/tmp/config",
                "API_TOKEN": "secret",
                "SSH_AUTH_SOCK": "/tmp/agent",
                "DATABASE_PASSWORD": "secret",
            }
        )
        self.assertEqual(set(captured), {"LANG", "PATH", "XDG_CONFIG_HOME"})

    def test_dependency_names_and_unassessed_evidence_are_observed(self) -> None:
        (self.root / "pyproject.toml").write_text(
            "[project]\nname='fixture'\ndependencies=['alpha>=1', 'beta']\n",
            encoding="utf-8",
        )
        dependencies = capture_dependencies([("fixture", self.root)], self.core)
        python = next(item for item in dependencies if item["format"] == "python")
        self.assertEqual([item["name"] for item in python["declared"]], ["alpha", "beta"])
        evidence = evidence_manifest([], self.core)
        self.assertEqual(evidence["summary"], "UNASSESSED")
        self.assertEqual(evidence["checks"], [])

        snapshot = EnvironmentCapture(self.core).capture(
            processes=[],
            toolchains=["python3"],
            dependency_roots=[("fixture", self.root)],
            agent={"adapter": "fixture", "sessionReference": None},
            evidence=evidence,
            environment={"PATH": os.environ.get("PATH", "")},
            workspace={"state": "UNAVAILABLE", "reason": "test fixture"},
        )
        self.assertTrue(snapshot.root_hash.startswith("sha256:"))
        self.assertEqual(snapshot.value["evidence"]["summary"], "UNASSESSED")

    def test_workspace_numbers_and_exited_processes_remain_canonical(self) -> None:
        response = subprocess.CompletedProcess(
            [],
            0,
            stdout=b'[{\"scale\":1.25,\"address\":\"0x1\"}]',
            stderr=b"",
        )
        with patch(
            "worldline.environment.subprocess.run",
            side_effect=[response, response, response, response],
        ):
            workspace = capture_workspace()
        self.assertEqual(workspace["monitors"]["value"][0]["scale"], "1.25")
        canonical_bytes(workspace)

        process = capture_processes(
            [
                OwnedProcess(
                    pid=None,
                    world_instance="world",
                    systemd_unit="worldline-fixture.service",
                    role="agent",
                    argv=("/usr/bin/fixture", "--json"),
                    cwd=b"/work",
                )
            ]
        )[0]
        self.assertEqual(process["state"], "EXITED")
        self.assertEqual(process["argvDisplay"], ["/usr/bin/fixture", "--json"])
        self.assertEqual(process["cwdDisplay"], "/work")


if __name__ == "__main__":
    unittest.main()
