from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
import uuid

from worldline.checks import CheckRunner
from worldline.core import Core
from worldline.paths import WorldlinePaths
from worldline.project import CheckSpec, ProjectConfig
from worldline.store import StateStore
from worldline.validation import canonical_checks, canonical_policy
from worldline.errors import WorldlineError


class ProjectConfigTests(unittest.TestCase):
    def test_policy_ids_cannot_redirect_check_runtime_cleanup(self) -> None:
        with tempfile.TemporaryDirectory(prefix="worldline-policy-id-") as temporary:
            root = Path(temporary)
            victim = root / "victim"
            victim.mkdir()
            marker = victim / "keep"
            marker.write_text("keep")
            env = {name: str(root / name.lower()) for name in (
                "HOME", "XDG_DATA_HOME", "XDG_STATE_HOME", "XDG_CONFIG_HOME", "XDG_RUNTIME_DIR")}
            for value in env.values():
                Path(value).mkdir(mode=0o700, parents=True, exist_ok=True)
            paths = WorldlinePaths.from_environment(env)
            paths.ensure()
            store = StateStore(paths, Core.shared())
            primary = root / "work"
            primary.mkdir()
            try:
                for malicious in (str(victim), "../victim", "nested/victim", ".", "..", "a\nname"):
                    with self.subTest(malicious=malicious):
                        (primary / ".worldline.json").write_text(json.dumps({
                            "schemaVersion": 1, "generated": [], "services": [],
                            "checks": [{"id": malicious, "kind": "tests", "argv": ["/usr/bin/true"],
                                        "required": True, "format": "exit"}],
                        }))
                        with self.assertRaises(WorldlineError) as raised:
                            ProjectConfig.load(primary, store)
                        self.assertEqual(raised.exception.code, "INVALID_PROJECT_CONFIG")
                        self.assertTrue(marker.is_file())
                # Direct callers may construct a CheckSpec; the runner must guard the deletion
                # site independently of the policy parser.
                runner = object.__new__(CheckRunner)
                runner.paths = paths
                malicious_check = CheckSpec(str(victim), "tests", ("/usr/bin/true",),
                                            None, True, "exit", None, ())
                with self.assertRaises(WorldlineError) as raised:
                    runner._run_one(world_instance=str(uuid.uuid4()), overlays=(),
                                    primary_target=primary, check=malicious_check,
                                    verifier_sources={})
                self.assertEqual(raised.exception.code, "INVALID_CHECK_ID")
                self.assertEqual(marker.read_text(), "keep")
            finally:
                store.close()

    def test_check_declaration_order_is_policy_identity(self) -> None:
        legacy = CheckSpec("build", "build", ("/usr/bin/true",), None, True,
                           "exit", None, (), (), "legacy")
        private = CheckSpec("exam", "tests", ("/usr/bin/python3", "exam.py"),
                            None, True, "junit", None, (), ("exam.py",),
                            "private-evaluator-v1")
        first = ProjectConfig(generated=(), checks=(legacy, private), services=())
        reversed_policy = ProjectConfig(generated=(), checks=(private, legacy), services=())
        self.assertNotEqual(canonical_policy(first), canonical_policy(reversed_policy))
        with tempfile.TemporaryDirectory(prefix="worldline-policy-order-") as temporary:
            root = Path(temporary)
            env = {name: str(root / name.lower()) for name in (
                "HOME", "XDG_DATA_HOME", "XDG_STATE_HOME", "XDG_CONFIG_HOME", "XDG_RUNTIME_DIR")}
            for value in env.values():
                Path(value).mkdir(mode=0o700, parents=True, exist_ok=True)
            store = StateStore(WorldlinePaths.from_environment(env), Core.shared())
            try:
                primary = root / "work"
                primary.mkdir()
                (primary / ".worldline.json").write_text(json.dumps({
                    "schemaVersion": 1, "generated": [], "services": [], "checks": [
                        {"id": "exam", "kind": "tests", "argv": ["/usr/bin/python3", "exam.py"],
                         "required": True, "format": "junit", "verifiers": ["exam.py"],
                         "profile": "private-evaluator-v1"},
                        {"id": "build", "kind": "build", "argv": ["/usr/bin/true"],
                         "required": True, "format": "exit"},
                    ],
                }))
                with self.assertRaises(WorldlineError) as raised:
                    ProjectConfig.load(primary, store)
                self.assertEqual(raised.exception.code, "CHECK_PROFILE_ORDER_INVALID")
            finally:
                store.close()

    def test_private_evaluator_profile_changes_policy_identity_and_rejects_legacy_report_path(self) -> None:
        with tempfile.TemporaryDirectory(prefix="worldline-private-policy-") as temporary:
            root = Path(temporary)
            env = {name: str(root / name.lower()) for name in (
                "HOME", "XDG_DATA_HOME", "XDG_STATE_HOME", "XDG_CONFIG_HOME", "XDG_RUNTIME_DIR")}
            for value in env.values():
                Path(value).mkdir(mode=0o700, parents=True, exist_ok=True)
            store = StateStore(WorldlinePaths.from_environment(env), Core.shared())
            try:
                primary = root / "work"
                primary.mkdir()
                check = {"id": "exam", "kind": "tests", "argv": ["/usr/bin/python3", "exam.py"],
                         "required": True, "format": "junit", "verifiers": ["exam.py"]}
                def load(value: dict) -> ProjectConfig:
                    (primary / ".worldline.json").write_text(json.dumps({
                        "schemaVersion": 1, "generated": [], "services": [], "checks": [value]}))
                    return ProjectConfig.load(primary, store)
                legacy = load(check)
                private = load({**check, "profile": "private-evaluator-v1"})
                self.assertEqual(legacy.checks[0].profile, "legacy")
                self.assertEqual(private.checks[0].profile, "private-evaluator-v1")
                self.assertNotEqual(canonical_checks(legacy.checks), canonical_checks(private.checks))
                for invalid in (
                    {**check, "profile": "private-evaluator-v1", "result": "report.xml"},
                    {**check, "profile": "private-evaluator-v1", "verifiers": []},
                    {**check, "profile": "private-evaluator-v1", "format": "exit"},
                    {**check, "profile": "unknown"},
                ):
                    with self.assertRaises(WorldlineError):
                        load(invalid)
            finally:
                store.close()

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
