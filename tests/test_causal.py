from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest

from worldline.core import Core, hash_id
from worldline.causal import CausalIndexer
from worldline.delta import Delta
from worldline.manifest import Manifest, path_b64
from worldline.model import World, WorldState
from worldline.paths import WorldlinePaths
from worldline.project import ProjectConfig
from worldline.roots import RootManager
from worldline.store import StateStore


class CausalTests(unittest.TestCase):
    def test_why_walks_agent_mission_file_and_prime(self) -> None:
        with tempfile.TemporaryDirectory(prefix="worldline-causal-") as temporary:
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
                (work / "code.txt").write_text("base\nsecond\n", encoding="utf-8")
                RootManager(paths, store, core=core, toolchains=()).register([work], confirmed=True)
                registered = store.roots()[0]
                root_key = registered["root_key"]
                logical = bytes(registered["path"])
                source = Path(os.fsdecode(os.path.realpath(logical)))
                base = paths.worlds / "causal" / "base"
                payload = paths.worlds / "causal" / "payload"
                original = Manifest.capture(source, logical_root=logical, root_key=root_key, kind="filesystem", core=core)
                Manifest.materialize(original, source, base / root_key, core=core)
                Manifest.materialize(original, source, payload / root_key, core=core)
                (base / "manifests").mkdir()
                (payload / "manifests").mkdir()
                original.save(base / "manifests" / f"{root_key}.json")
                (payload / root_key / "code.txt").write_text("changed\nsecond\n", encoding="utf-8")
                changed = Manifest.capture(payload / root_key, logical_root=logical, root_key=root_key, kind="filesystem", core=core)
                changed.save(payload / "manifests" / f"{root_key}.json")
                delta = Delta.compute_all({root_key: original}, {root_key: changed}, core)
                parent = store.prime()
                world = World.create(
                    alias="beta",
                    parent_instance=parent.instance_id,
                    parent_content=parent.content_id,
                    cause="change first line",
                    actor="fixture",
                    payload_path=payload,
                    base_payload_path=base,
                    base_root=Manifest.root_set_hash([original], core),
                    root_set_hash=parent.root_set_hash,
                    mission_hash=hash_id(core.hash_bytes(b"change first line")),
                )
                world.components = {
                    **Manifest.component_roots([changed], core),
                    "environment": parent.components["environment"],
                    "evidence": parent.components["evidence"],
                }
                world.delta_hash = delta.delta_hash
                world.delta = {**delta.value["summary"], "files": delta.value["operations"]}
                world.evidence = {
                    "summary": "PASS",
                    "checks": [
                        {"id": "fixture-test", "kind": "tests", "required": True, "status": "PASS", "covers": ["*.txt"]}
                    ],
                }
                world.transition(WorldState.FINALIZING, core)
                world.establish_identity(core)
                world.transition(WorldState.VALID, core)
                store.insert_world(world)
                store.append_causal_event(
                    {
                        "schemaVersion": 1,
                        "worldInstance": world.instance_id,
                        "kind": "tool-event",
                        "actor": "fixture",
                        "reason": "make behavior deterministic",
                        "rootKey": root_key,
                        "pathB64": path_b64(b"code.txt"),
                        "pathDisplay": "code.txt",
                        "lineStart": 1,
                        "lineEnd": 1,
                    }
                )
                CausalIndexer(store).index(world, ProjectConfig(generated=(), checks=(), services=()))
                why = CausalIndexer(store).why(str(work / "code.txt"), 1)
                self.assertEqual(why["world"], "beta")
                self.assertEqual(why["actor"], "fixture")
                self.assertEqual(why["reason"], "make behavior deterministic")
                self.assertEqual(why["granularity"], "line")
                self.assertEqual(why["evidence"][0]["id"], "fixture-test")
                self.assertIn("PRIME", [item["alias"] for item in why["ancestors"]])
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
