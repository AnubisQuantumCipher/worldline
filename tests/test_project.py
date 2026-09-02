from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from worldline.checks import CheckRunner
from worldline.core import Core
from worldline.paths import WorldlinePaths
from worldline.project import CheckSpec, ProjectConfig
from worldline.store import StateStore


class ProjectConfigTests(unittest.TestCase):
    def test_exact_project_schema_and_benchmark_observations(self) -> None:
        with tempfile.TemporaryDirectory(prefix="worldline-project-") as temporary:
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
            store = StateStore(paths, Core.shared())
            try:
                primary = root / "work"
                primary.mkdir()
                (primary / ".worldline.json").write_text(
                    json.dumps(
                        {
                            "schemaVersion": 1,
                            "generated": [],
                            "checks": [
                                {
                                    "id": "tests",
                                    "kind": "tests",
                                    "argv": ["/usr/bin/true"],
                                    "required": True,
                                    "format": "exit",
                                    "covers": ["src/**"],
                                }
                            ],
                            "services": [
                                {
                                    "id": "fixture-service",
                                    "argv": ["/usr/bin/sleep", "1"],
                                    "cwd": ".",
                                    "env": {"LANG": "C"},
                                    "healthArgv": ["/usr/bin/true"],
                                    "restart": "never",
                                }
                            ],
                        }
                    ),
                    encoding="utf-8",
                )
                config = ProjectConfig.load(primary, store)
                self.assertEqual(config.checks[0].id, "tests")
                self.assertEqual(config.services[0].cwd, ".")
                parser = object.__new__(CheckRunner)
                benchmark = CheckSpec(
                    "perf", "benchmark", ("bench",), None, False,
                    "worldline-benchmark-v1", "result.json", (),
                )
                parsed = parser._parse(
                    benchmark,
                    0,
                    b"",
                    b"",
                    b'{"metric":"throughput","unit":"ops/s","baseline":100,"candidate":125,"direction":"higher-is-better"}',
                )
                self.assertEqual(parsed["status"], "PASS")
                self.assertEqual(parsed["percentage"], "25")
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
