from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from worldline.causal import CausalIndexer
from worldline.core import Core, hash_id
from worldline.delta import Delta
from worldline.linux.git import GitAdapter
from worldline.manifest import Manifest, path_b64
from worldline.model import World, WorldState
from worldline.paths import WorldlinePaths
from worldline.project import ProjectConfig
from worldline.roots import RootManager
from worldline.store import StateStore


class CausalRootCoverageTests(unittest.TestCase):
    """Valid base snapshots must remain indexable across root kinds and layouts.

    These are local causal-index tests using the real native core and store. The
    explicit COLLAPSED transition below is a fixture for attribution, not a run
    of the collapse transaction or evidence that its acceptance gates passed.
    """

    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="worldline-causal-roots-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        environment = {
            "HOME": str(self.root / "home"),
            "XDG_DATA_HOME": str(self.root / "data"),
            "XDG_STATE_HOME": str(self.root / "state"),
            "XDG_CONFIG_HOME": str(self.root / "config"),
            "XDG_RUNTIME_DIR": str(self.root / "runtime"),
        }
        for value in environment.values():
            Path(value).mkdir(mode=0o700, parents=True)
        self.paths = WorldlinePaths.from_environment(environment)
        self.core = Core.shared()
        self.store = StateStore(self.paths, self.core)
        self.addCleanup(self.store.close)

    @staticmethod
    def _git(root: Path, *arguments: str) -> str:
        # All repository writes are to this test's newly created temporary root.
        # Ignore host Git configuration and disable detached maintenance, hooks
        # and signing so fixture creation cannot depend on the user's settings.
        environment = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        environment.update({
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_SYSTEM": os.devnull,
            "GIT_TERMINAL_PROMPT": "0",
            "LC_ALL": "C",
        })
        result = subprocess.run(
            ["git", "-c", "user.email=fixture@example.invalid", "-c", "user.name=fixture",
             "-c", "maintenance.auto=false", "-c", "gc.auto=0", "-c", "core.hooksPath=/dev/null",
             "-c", "commit.gpgSign=false", "-c", "init.templateDir=", "-C", str(root), *arguments],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            check=True, timeout=15, env=environment,
        )
        return result.stdout.decode("utf-8").strip()

    def _check_indexing(self, kinds: dict[str, str], saved: frozenset[str]) -> None:
        work_roots = {}
        heads = {}
        for name, kind in kinds.items():
            root = self.root / name
            root.mkdir()
            (root / "code.txt").write_text("base\nunchanged\n", encoding="utf-8")
            if kind == "repo":
                self._git(root, "init", "-q", "-b", "main")
                self._git(root, "add", "code.txt")
                self._git(root, "commit", "-q", "-m", "causal fixture")
                heads[name] = self._git(root, "rev-parse", "HEAD")
            work_roots[name] = root
        RootManager(self.paths, self.store, core=self.core, toolchains=()).register(
            list(work_roots.values()), confirmed=True)

        base = self.paths.worlds / "causal-roots" / "base"
        payload = self.paths.worlds / "causal-roots" / "payload"
        base_manifests = {}
        candidate_manifests = {}
        registered = {}
        for row in self.store.roots():
            logical = bytes(row["path"])
            name = Path(os.fsdecode(logical)).name
            key = row["root_key"]
            self.assertEqual(row["kind"], kinds[name])
            source = Path(os.fsdecode(os.path.realpath(logical)))
            repository = GitAdapter(self.core).capture(source) if row["kind"] == "repo" else None
            if repository is not None:
                self.assertEqual(repository["state"], "CAPTURED")
                self.assertEqual(repository["head"], heads[name])
            original = Manifest.capture(source, logical_root=logical, root_key=key,
                                        kind=row["kind"], core=self.core, repository=repository)
            Manifest.materialize(original, source, base / key, core=self.core)
            Manifest.materialize(original, source, payload / key, core=self.core)
            base_repository = GitAdapter(self.core).capture(base / key) if row["kind"] == "repo" else None
            self.assertEqual(base_repository, repository)
            actual_base = Manifest.capture(base / key, logical_root=logical, root_key=key,
                                           kind=row["kind"], core=self.core, repository=base_repository)
            self.assertEqual(actual_base.root_hash, original.root_hash)
            if name in saved:
                actual_base.save(base / "manifests" / f"{key}.json")
            (payload / key / "code.txt").write_text(f"changed {name}\nunchanged\n", encoding="utf-8")
            candidate_repository = (
                GitAdapter(self.core).capture(payload / key) if row["kind"] == "repo" else None)
            changed = Manifest.capture(payload / key, logical_root=logical, root_key=key,
                                       kind=row["kind"], core=self.core, repository=candidate_repository)
            changed.save(payload / "manifests" / f"{key}.json")
            base_manifests[key] = actual_base
            candidate_manifests[key] = changed
            registered[name] = row

        delta = Delta.compute_all(base_manifests, candidate_manifests, self.core)
        expected_paths = {(row["root_key"], path_b64(b"code.txt")) for row in registered.values()}
        self.assertEqual(
            {(operation["rootKey"], operation["pathB64"])
             for operation in delta.value["operations"] if operation["pathB64"]},
            expected_paths,
        )
        parent = self.store.prime()
        world = World.create(
            alias="causal-roots", parent_instance=parent.instance_id, parent_content=parent.content_id,
            cause="causal root fixture", actor="fixture", payload_path=payload, base_payload_path=base,
            base_root=Manifest.root_set_hash(base_manifests.values(), self.core),
            root_set_hash=parent.root_set_hash, mission_hash=hash_id(self.core.hash_bytes(b"causal root fixture")),
        )
        world.components = {
            **Manifest.component_roots(candidate_manifests.values(), self.core),
            "environment": parent.components["environment"], "evidence": parent.components["evidence"],
        }
        world.delta_hash = delta.delta_hash
        world.delta = {**delta.value["summary"], "files": delta.value["operations"]}
        world.evidence = {"summary": "PASS", "checks": []}
        world.transition(WorldState.FINALIZING, self.core)
        world.establish_identity(self.core)
        world.transition(WorldState.VALID, self.core)
        self.store.insert_world(world)
        for name, row in registered.items():
            self.store.append_causal_event({
                "schemaVersion": 1, "worldInstance": world.instance_id, "kind": "tool-event",
                "actor": f"fixture-{name}", "reason": f"change {name}", "rootKey": row["root_key"],
                "pathB64": path_b64(b"code.txt"), "pathDisplay": "code.txt", "lineStart": 1, "lineEnd": 1,
            })

        # Check the manifest directory itself as well as bytes: absence is an
        # accepted base layout, not permission for indexing to create it.
        manifests_directory = base / "manifests"
        directory_existed = manifests_directory.exists()
        saved_bytes = {p.name: p.read_bytes() for p in manifests_directory.glob("*.json")}
        indexer = CausalIndexer(self.store)
        self.assertEqual(indexer.index(world, ProjectConfig(generated=(), checks=(), services=())),
                         len(expected_paths))
        self.assertEqual(manifests_directory.exists(), directory_existed)
        self.assertEqual({p.name: p.read_bytes() for p in manifests_directory.glob("*.json")}, saved_bytes)
        events = [row["event"] for row in self.store.causal_events_for_world(world.instance_id)
                  if row["event"]["kind"] == "file-delta"]
        self.assertEqual(len(events), len(expected_paths))
        self.assertEqual({(event["rootKey"], event["pathB64"]) for event in events}, expected_paths)

        for name, row in registered.items():
            key = row["root_key"]
            # Independently recapture the actual base after indexing, including
            # repository facts, so the read-only assertion covers the payload
            # as well as the saved-manifest directory.
            base_repository = GitAdapter(self.core).capture(base / key) if row["kind"] == "repo" else None
            after = Manifest.capture(base / key, logical_root=bytes(row["path"]), root_key=key,
                                     kind=row["kind"], core=self.core, repository=base_repository)
            self.assertEqual(after.canonical, base_manifests[key].canonical)
            event = next(event for event in events if event["rootKey"] == key)
            self.assertEqual(event["actor"], f"fixture-{name}")
            self.assertEqual(event["reason"], f"change {name}")
            changed_line = self.store.newest_line_event(key, path_b64(b"code.txt"), 1)
            self.assertIsNotNone(changed_line)
            self.assertEqual(changed_line["world_instance"], world.instance_id)
            self.assertEqual(changed_line["start_line"], 1)
            self.assertEqual(changed_line["end_line"], 1)
            self.assertEqual(changed_line["granularity"], "line")
            self.assertIsNone(self.store.newest_line_event(key, path_b64(b"code.txt"), 2))
            self.assertEqual(indexer.why(str(work_roots[name] / "code.txt"), 1)["attribution"], "checkpoint")

        # Same fixture technique as test_causal.py: attribution is checked only
        # after making the world an ancestor and matching PRIME's visible bytes.
        world.transition(WorldState.COLLAPSED, self.core)
        self.store.save_world(world)
        for name, root in work_roots.items():
            (root / "code.txt").write_text(f"changed {name}\nunchanged\n", encoding="utf-8")
            why = indexer.why(str(root / "code.txt"), 1)
            self.assertEqual(why["world"], world.alias)
            self.assertEqual(why["actor"], f"fixture-{name}")
            self.assertEqual(why["reason"], f"change {name}")
            self.assertEqual(why["attribution"], "world")
            self.assertEqual(why["granularity"], "line")
            self.assertEqual(indexer.why(str(root / "code.txt"), 2)["attribution"], "checkpoint")

    def test_repository_base_without_saved_manifest(self) -> None:
        self._check_indexing({"repository": "repo"}, frozenset())

    def test_repository_base_with_saved_manifest(self) -> None:
        self._check_indexing({"repository": "repo"}, frozenset({"repository"}))

    def test_multiple_roots_without_saved_manifests(self) -> None:
        self._check_indexing({"alpha": "filesystem", "beta": "filesystem"}, frozenset())

    def test_multiple_roots_with_saved_manifests(self) -> None:
        self._check_indexing({"alpha": "filesystem", "beta": "filesystem"}, frozenset({"alpha", "beta"}))

    def test_multiple_roots_with_mixed_manifest_availability(self) -> None:
        self._check_indexing({"alpha": "filesystem", "beta": "filesystem"}, frozenset({"alpha"}))

    def test_repository_and_filesystem_roots_with_mixed_manifests(self) -> None:
        self._check_indexing({"alpha": "repo", "beta": "filesystem"}, frozenset({"alpha"}))


if __name__ == "__main__":
    unittest.main()
