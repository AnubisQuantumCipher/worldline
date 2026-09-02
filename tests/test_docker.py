from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import uuid

from worldline.core import Core
from worldline.errors import WorldlineError
from worldline.linux.docker import DockerAdapter


class DockerAdapterTests(unittest.TestCase):
    def _adapter(self) -> DockerAdapter:
        adapter = object.__new__(DockerAdapter)
        adapter.executable = "/usr/bin/docker"
        adapter.core = Core.shared()
        adapter.server_version = "fixture"
        return adapter

    def test_capture_retains_only_scoped_reconstructable_state(self) -> None:
        with tempfile.TemporaryDirectory(prefix="worldline-docker-") as temporary:
            root = Path(temporary) / "root"
            source = root / "subdirectory"
            source.mkdir(parents=True)
            world = str(uuid.uuid4())
            inspection = [
                {
                    "Id": "container-id",
                    "Name": "/fixture",
                    "Config": {
                        "Image": "fixture:latest",
                        "Cmd": ["serve"],
                        "Entrypoint": ["/entry"],
                        "WorkingDir": "/work",
                        "User": "1000",
                        "Env": ["LANG=C", "API_TOKEN=must-not-leak"],
                        "Labels": {
                            "worldline.instance": world,
                            "worldline.service": "fixture",
                            "worldline.secret-token": "must-not-leak",
                            "foreign": "ignored",
                        },
                    },
                    "Mounts": [
                        {
                            "Type": "bind",
                            "Source": str(source),
                            "Destination": "/work",
                            "RW": True,
                        }
                    ],
                    "State": {"Status": "running"},
                }
            ]
            responses = [
                subprocess.CompletedProcess([], 0, stdout=b"container-id\n", stderr=b""),
                subprocess.CompletedProcess([], 0, stdout=json.dumps(inspection).encode("utf-8"), stderr=b""),
            ]
            with patch("worldline.linux.docker.subprocess.run", side_effect=responses):
                manifest = self._adapter().capture(world, world_roots={"root": root})[0]
            self.assertEqual(manifest["environment"], {"LANG": "C"})
            self.assertEqual(manifest["labels"], {"worldline.instance": world, "worldline.service": "fixture"})
            self.assertEqual(manifest["mounts"][0]["rootKey"], "root")
            self.assertEqual(manifest["mounts"][0]["sourceRelative"], "subdirectory")
            self.assertNotIn("inspectRawB64", manifest)
            self.assertNotIn("must-not-leak", json.dumps(manifest))

    def test_capture_rejects_mount_outside_world_roots(self) -> None:
        with tempfile.TemporaryDirectory(prefix="worldline-docker-scope-") as temporary:
            root = Path(temporary) / "root"
            outside = Path(temporary) / "outside"
            root.mkdir()
            outside.mkdir()
            world = str(uuid.uuid4())
            inspection = [
                {
                    "Id": "container-id",
                    "Config": {
                        "Image": "fixture:latest",
                        "Labels": {"worldline.instance": world},
                    },
                    "Mounts": [
                        {
                            "Type": "bind",
                            "Source": str(outside),
                            "Destination": "/outside",
                            "RW": False,
                        }
                    ],
                    "State": {"Status": "running"},
                }
            ]
            responses = [
                subprocess.CompletedProcess([], 0, stdout=b"container-id\n", stderr=b""),
                subprocess.CompletedProcess([], 0, stdout=json.dumps(inspection).encode("utf-8"), stderr=b""),
            ]
            with patch("worldline.linux.docker.subprocess.run", side_effect=responses):
                with self.assertRaises(WorldlineError) as caught:
                    self._adapter().capture(world, world_roots={"root": root})
            self.assertEqual(caught.exception.code, "DOCKER_SCOPE_VIOLATION")


if __name__ == "__main__":
    unittest.main()
