from __future__ import annotations

import os
from pathlib import Path
import stat
import tempfile
import unittest

from worldline.core import Core, hash_id
from worldline.finalize import Finalizer
from worldline.linux.namespaces import BubblewrapSandbox, SandboxSpec
from worldline.linux.systemd import SystemdAdapter
from worldline.manifest import Manifest
from worldline.model import World, WorldState
from worldline.paths import WorldlinePaths
from worldline.project import ProjectConfig, ServiceSpec
from worldline.roots import RootManager
from worldline.services import ServiceManager
from worldline.store import StateStore


class FinalizerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-finalize-")
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
        self.core = Core.shared()
        self.store = StateStore(self.paths, self.core)
        self.work = root / "work"
        self.work.mkdir()
        (self.work / "value.txt").write_text("prime", encoding="utf-8")
        RootManager(self.paths, self.store, core=self.core, toolchains=()).register([self.work], confirmed=True)
        self.sandbox = BubblewrapSandbox(self.paths)

    def tearDown(self) -> None:
        self.store.close()
        self.temporary.cleanup()

    def test_overlay_is_materialized_hashed_and_made_readonly(self) -> None:
        root = self.store.roots()[0]
        root_key = root["root_key"]
        logical = bytes(root["path"])
        current_source = Path(os.fsdecode(os.path.realpath(logical)))
        base = self.paths.worlds / "fixture" / "base"
        manifest = Manifest.capture(
            current_source,
            logical_root=logical,
            root_key=root_key,
            kind=root["kind"],
            core=self.core,
        )
        Manifest.materialize(manifest, current_source, base / root_key, core=self.core)
        (base / "manifests").mkdir()
        manifest.save(base / "manifests" / f"{root_key}.json")
        parent = self.store.prime()
        world = World.create(
            alias="alpha",
            parent_instance=parent.instance_id,
            parent_content=parent.content_id,
            cause="fixture change",
            actor="fixture",
            payload_path=self.paths.worlds / "fixture" / "payload",
            base_payload_path=base,
            base_root=Manifest.root_set_hash([manifest], self.core),
            root_set_hash=parent.root_set_hash,
            mission_hash=hash_id(self.core.hash_bytes(b"fixture")),
        )
        self.store.insert_world(world)
        overlays = self.sandbox.overlay_roots(
            world.instance_id,
            [(root_key, base / root_key, Path(os.fsdecode(logical)))],
        )
        runtime = self.paths.overlays / world.instance_id / "runtime"
        script = f"from pathlib import Path; Path({str(Path(os.fsdecode(logical)) / 'value.txt')!r}).write_text('candidate', encoding='utf-8')"
        spec = SandboxSpec(
            instance_id=world.instance_id,
            argv=("/usr/bin/python3", "-c", script),
            cwd=Path(os.fsdecode(logical)),
            environment={"PATH": "/usr/bin"},
            roots=overlays,
            runtime=runtime,
        )
        process = self.sandbox.launch_world(spec)
        _stdout, stderr = process.process.communicate(timeout=15)
        self.assertEqual(process.process.returncode, 0, stderr.decode("utf-8", "replace"))

        finalized = Finalizer(self.paths, self.store, self.sandbox, core=self.core).finalize(
            world.alias,
            overlays,
            check_results=[],
            required_checks=[],
            agent_manifest={"adapter": "fixture", "sessionReference": None, "rawEventHash": None},
        )
        payload_file = Path(finalized.payload_path) / root_key / "value.txt"
        self.assertEqual(finalized.state, WorldState.VALID)
        self.assertEqual(payload_file.read_text(encoding="utf-8"), "candidate")
        self.assertNotIn("", [item["pathB64"] for item in finalized.delta["files"]])
        self.assertFalse(stat.S_IMODE(payload_file.stat().st_mode) & 0o222)
        self.assertEqual((self.work / "value.txt").read_text(encoding="utf-8"), "prime")
        self.assertEqual((base / root_key / "value.txt").read_text(encoding="utf-8"), "prime")

        services = ServiceManager(
            self.paths,
            self.store,
            self.sandbox,
            SystemdAdapter(),
        )
        project = ProjectConfig(
            generated=(),
            checks=(),
            services=(
                ServiceSpec(
                    id="fixture-service",
                    argv=("/usr/bin/sleep", "5"),
                    cwd=".",
                    env={},
                    health_argv=("/usr/bin/true",),
                    restart="never",
                ),
            ),
        )
        started = services.start_declared(finalized, project)
        self.assertEqual(started[0]["health"]["status"], "PASS")
        services.stop_world(finalized.instance_id)


if __name__ == "__main__":
    unittest.main()
