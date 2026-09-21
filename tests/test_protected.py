"""PRIME-owned protected paths, enforced by the engine's own delta (worldline-lab F5)."""
from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import unittest

from worldline.core import Core, hash_id
from worldline.errors import WorldlineError
from worldline.finalize import Finalizer
from worldline.linux.namespaces import BubblewrapSandbox, SandboxSpec
from worldline.manifest import Manifest
from worldline.model import World, WorldState
from worldline.paths import WorldlinePaths
from worldline.project import ProjectConfig, protected_matches
from worldline.roots import RootManager
from worldline.store import StateStore


class ProtectedPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-protected-")
        root = Path(self.temporary.name)
        env = {name: str(root / part) for name, part in (("HOME", "home"), ("XDG_DATA_HOME", "data"), ("XDG_STATE_HOME", "state"), ("XDG_CONFIG_HOME", "config"), ("XDG_RUNTIME_DIR", "runtime"))}
        for value in env.values():
            Path(value).mkdir(mode=0o700, parents=True, exist_ok=True)
        self.paths = WorldlinePaths.from_environment(env)
        self.core = Core.shared()
        self.store = StateStore(self.paths, self.core)
        self.work = root / "work"
        self.work.mkdir()

    def tearDown(self) -> None:
        self.store.close()
        self.temporary.cleanup()

    def policy(self, protected):
        value = {"schemaVersion": 1, "generated": [], "checks": [], "services": []}
        if protected is not None:
            value["protected"] = protected
        (self.work / ".worldline.json").write_text(json.dumps(value), encoding="utf-8")
        return ProjectConfig.load(self.work, self.store)

    def test_protected_is_optional_relative_and_validated(self) -> None:
        self.assertEqual(self.policy(None).protected, ())
        self.assertEqual(self.policy([".worldline.json", "evaluator/*"]).protected, (".worldline.json", "evaluator/*"))
        for bad in (["/etc/passwd"], ["../x"], "not-a-list", [""]):
            with self.assertRaises(WorldlineError) as refused:
                self.policy(bad)
            self.assertEqual(refused.exception.code, "INVALID_PROJECT_CONFIG")

    def test_matching(self) -> None:
        protected = (".worldline.json", "evaluator/*", "docs")
        self.assertTrue(protected_matches(protected, ".worldline.json"))
        self.assertTrue(protected_matches(protected, "evaluator/run.py"))
        self.assertTrue(protected_matches(protected, "docs/manual.md"))
        self.assertTrue(protected_matches(protected, "docs"))
        self.assertFalse(protected_matches(protected, "afterimage/bundle.py"))
        self.assertFalse(protected_matches(protected, "evaluator"))  # the directory itself is not a file change
        self.assertFalse(protected_matches(protected, "docsx/manual.md"))


class ProtectedFinalizeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-protected-finalize-")
        root = Path(self.temporary.name)
        env = {name: str(root / part) for name, part in (("HOME", "home"), ("XDG_DATA_HOME", "data"), ("XDG_STATE_HOME", "state"), ("XDG_CONFIG_HOME", "config"), ("XDG_RUNTIME_DIR", "runtime"))}
        for value in env.values():
            Path(value).mkdir(mode=0o700, parents=True, exist_ok=True)
        self.paths = WorldlinePaths.from_environment(env)
        self.core = Core.shared()
        self.store = StateStore(self.paths, self.core)
        self.work = root / "work"
        self.work.mkdir()
        (self.work / "value.txt").write_text("prime", encoding="utf-8")
        (self.work / "policy.json").write_text("{}", encoding="utf-8")
        RootManager(self.paths, self.store, core=self.core, toolchains=()).register([self.work], confirmed=True)
        self.sandbox = BubblewrapSandbox(self.paths)

    def tearDown(self) -> None:
        self.store.close()
        self.temporary.cleanup()

    def finalize_after(self, script: str, protected: tuple[str, ...]) -> World:
        root = self.store.roots()[0]
        root_key = root["root_key"]
        logical = bytes(root["path"])
        current_source = Path(os.fsdecode(os.path.realpath(logical)))
        base = self.paths.worlds / "fixture" / "base"
        manifest = Manifest.capture(current_source, logical_root=logical, root_key=root_key, kind=root["kind"], core=self.core)
        Manifest.materialize(manifest, current_source, base / root_key, core=self.core)
        (base / "manifests").mkdir()
        manifest.save(base / "manifests" / f"{root_key}.json")
        parent = self.store.prime()
        world = World.create(
            alias="alpha", parent_instance=parent.instance_id, parent_content=parent.content_id, cause="fixture change",
            actor="fixture", payload_path=self.paths.worlds / "fixture" / "payload", base_payload_path=base,
            base_root=Manifest.root_set_hash([manifest], self.core), root_set_hash=parent.root_set_hash,
            mission_hash=hash_id(self.core.hash_bytes(b"fixture")),
        )
        self.store.insert_world(world)
        overlays = self.sandbox.overlay_roots(world.instance_id, [(root_key, base / root_key, Path(os.fsdecode(logical)))])
        runtime = self.paths.overlays / world.instance_id / "runtime"
        spec = SandboxSpec(instance_id=world.instance_id, argv=("/usr/bin/python3", "-c", script), cwd=Path(os.fsdecode(logical)), environment={"PATH": "/usr/bin"}, roots=overlays, runtime=runtime)
        process = self.sandbox.launch_world(spec)
        _stdout, stderr = process.process.communicate(timeout=15)
        self.assertEqual(process.process.returncode, 0, stderr.decode("utf-8", "replace"))
        return Finalizer(self.paths, self.store, self.sandbox, core=self.core).finalize(
            world.alias, overlays, check_results=[], required_checks=[], protected=protected,
            agent_manifest={"adapter": "fixture", "sessionReference": None, "rawEventHash": None},
        )

    def test_changing_a_protected_path_degrades_the_world_by_name(self) -> None:
        logical = Path(os.fsdecode(bytes(self.store.roots()[0]["path"])))
        script = f"from pathlib import Path; Path({str(logical / 'policy.json')!r}).write_text('{{\"forged\": true}}', encoding='utf-8'); Path({str(logical / 'value.txt')!r}).write_text('candidate', encoding='utf-8')"
        finalized = self.finalize_after(script, ("policy.json",))
        self.assertEqual(finalized.state, WorldState.DEGRADED)
        check = next(item for item in finalized.evidence["checks"] if item["id"] == "protected-paths")
        self.assertEqual((check["status"], check["touched"], check["required"], check["format"]), ("FAIL", ["policy.json"], True, "engine"))
        self.assertEqual(finalized.risk, "HIGH")

    def test_untouched_protected_paths_pass_and_stay_valid(self) -> None:
        logical = Path(os.fsdecode(bytes(self.store.roots()[0]["path"])))
        script = f"from pathlib import Path; Path({str(logical / 'value.txt')!r}).write_text('candidate', encoding='utf-8')"
        finalized = self.finalize_after(script, ("policy.json",))
        self.assertEqual(finalized.state, WorldState.VALID)
        check = next(item for item in finalized.evidence["checks"] if item["id"] == "protected-paths")
        self.assertEqual((check["status"], check["touched"]), ("PASS", []))


if __name__ == "__main__":
    unittest.main()
