from __future__ import annotations

import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest import mock

from worldline.errors import WorldlineError
from worldline.model import World, WorldState
from worldline.paths import WorldlinePaths
from worldline.store import STORE_SCHEMA_VERSION, StateStore, _SCHEMA

from tests.test_lifecycle_integrity import _FixtureDaemon, _QUICK_AGENT

_FAILING_AGENT = "import sys\nsys.exit(3)\n"


class PruneReclaimsOnlyWhatNothingRefersTo(unittest.TestCase):
    def test_plan_apply_guards_and_records(self) -> None:
        fixture = _FixtureDaemon(self, _QUICK_AGENT)
        try:
            work, client, paths = fixture.work, fixture.client, fixture.paths
            client.request("init", {"roots": [str(work)], "kind": None, "primary": None, "confirmed": True})
            # A collapsed world (becomes PRIME's parent after the next collapse), a second collapse
            # (PRIME), a VALID sibling that stays VALID, and one that finished DEGRADED.
            self.assertEqual(client.request("fork", {"name": "first", "mission": "a", "agent": "fixture", "wait": True})["state"], "VALID")
            prepared = client.request("collapse.prepare", {"world": "first"})
            client.request("collapse.commit", {"transactionId": prepared["transaction_id"]})
            self.assertEqual(client.request("fork", {"name": "second", "mission": "b", "agent": "fixture", "wait": True})["state"], "VALID")
            self.assertEqual(client.request("fork", {"name": "archived", "mission": "c", "agent": "fixture", "wait": True})["state"], "VALID")
            prepared = client.request("collapse.prepare", {"world": "second"})
            client.request("collapse.commit", {"transactionId": prepared["transaction_id"]})
            self.assertEqual(client.request("show", {"world": "archived"})["state"], "ARCHIVED")
            (work / "fixture_agent.py").write_text(_FAILING_AGENT, encoding="utf-8")
            self.assertEqual(client.request("fork", {"name": "broken", "mission": "d", "agent": "fixture", "wait": True})["state"], "DEGRADED")

            plan = client.request("prune", {"dryRun": True})
            self.assertEqual(plan["state"], "DRY_RUN")
            aliases = {item["alias"] for item in plan["worlds"]}
            self.assertIn("archived", aliases)
            self.assertIn("broken", aliases)
            self.assertNotIn("second", aliases)   # PRIME
            # PRIME and the checkpoint `return` goes back to are protected whatever their aliases.
            self.assertEqual(len(plan["protected"]), 2)
            self.assertTrue(all(item["instanceId"] not in plan["protected"] for item in plan["worlds"]))
            parent = client.request("show", {"world": client.request("status")["prime"]["instanceId"]})["parent_instance"]
            self.assertGreater(plan["bytes"], 0)
            self.assertTrue(all(Path(item["path"]).is_dir() for item in plan["directories"]))
            prime_payload = os.path.realpath(client.request("show", {"world": "second"})["payload_path"])
            self.assertTrue(all(os.path.realpath(item["path"]) != prime_payload for item in plan["directories"]))

            # A dry run and an unconfirmed request delete nothing.
            client.request("prune", {"dryRun": False, "confirmed": False})
            self.assertFalse(client.request("show", {"world": "archived"})["payload_pruned"])

            # keep=1 spares the most recently finished prunable world (broken finished last).
            kept = client.request("prune", {"dryRun": True, "keep": 1})
            self.assertEqual(aliases - {item["alias"] for item in kept["worlds"]}, {"broken"})

            result = client.request("prune", {"dryRun": False, "confirmed": True, "logs": True})
            self.assertEqual(result["state"], "PRUNED")
            self.assertEqual(set(result["pruned"]), aliases)
            self.assertLessEqual({"archived", "broken"}, set(result["pruned"]))
            self.assertEqual(result["failures"], [])
            self.assertTrue(all(not Path(item).exists() for item in result["directories"]))
            shown = client.request("show", {"world": "archived"})
            self.assertTrue(shown["payload_pruned"])
            self.assertIsNotNone(shown["pruned_at"])
            self.assertFalse(Path(shown["payload_path"]).exists())
            self.assertTrue(Path(client.request("show", {"world": "second"})["payload_path"]).is_dir())
            self.assertTrue(Path(client.request("show", {"world": parent})["payload_path"]).is_dir())
            self.assertEqual([], list(paths.logs.glob(f"{shown['instance_id']}.*")))

            # Everything that needs the payload refuses by name; everything else still works.
            for operation, args in (("inspect", {"world": "archived"}), ("shell.info", {"world": "archived"}), ("return.prepare", {"world": "archived"})):
                with self.assertRaises(WorldlineError) as refused:
                    client.request(operation, args)
                self.assertEqual(refused.exception.code, "PAYLOAD_PRUNED", operation)
            status = client.request("status")
            self.assertTrue(next(w for w in status["worlds"] if w["alias"] == "archived")["pruned"])
            doctor = client.request("doctor", {})
            self.assertEqual(doctor["storeIntegrity"]["state"], "OK")
            self.assertIn("storeUsage", doctor)
            self.assertEqual(client.request("log", {"verify": True})["verification"]["receipts"], 2)
            events = client.request("log", {})["events"]
            self.assertTrue(any(event["kind"] == "prune" for event in events))
            # A second prune finds nothing left.
            self.assertEqual(client.request("prune", {"dryRun": True})["worlds"], [])
            # Return to the untouched return point still works.
            returned = client.request("return.prepare", {"world": None})
            self.assertEqual(returned["decision"], "AUTHORIZED")
            client.request("transaction.abort", {"transactionId": returned["transaction_id"]})
        finally:
            fixture.close()


class PruneNeverDeletesOutsideTheStore(unittest.TestCase):
    def test_a_payload_that_resolves_outside_the_store_is_kept_and_reported(self) -> None:
        # A recorded location can resolve outside the store through a link planted in a copy, or
        # a relocated store's leftovers. Prune reports it as a failure and deletes nothing there.
        fixture = _FixtureDaemon(self, _QUICK_AGENT)
        try:
            work, client = fixture.work, fixture.client
            client.request("init", {"roots": [str(work)], "kind": None, "primary": None, "confirmed": True})
            for name in ("kept", "archived"):
                self.assertEqual(client.request("fork", {"name": name, "mission": name, "agent": "fixture", "wait": True})["state"], "VALID")
            prepared = client.request("collapse.prepare", {"world": "kept"})
            client.request("collapse.commit", {"transactionId": prepared["transaction_id"]})
            self.assertEqual(client.request("show", {"world": "archived"})["state"], "ARCHIVED")
            payload = Path(client.request("show", {"world": "archived"})["payload_path"])
            outside = Path(fixture.temporary.name) / "outside-the-store"
            # Moving a directory to another parent rewrites its "..": it and its parent must be writable.
            parent_mode, payload_mode = payload.parent.stat().st_mode, payload.stat().st_mode
            os.chmod(payload.parent, parent_mode | 0o700)
            os.chmod(payload, payload_mode | 0o700)
            os.rename(payload, outside)
            os.chmod(outside, payload_mode)
            payload.symlink_to(outside, target_is_directory=True)
            os.chmod(payload.parent, parent_mode)
            before = sorted(str(item.relative_to(outside)) for item in outside.rglob("*"))
            self.assertTrue(before)

            plan = client.request("prune", {"dryRun": True})
            self.assertIn(str(outside), [item["path"] for item in plan["directories"]])
            result = client.request("prune", {"dryRun": False, "confirmed": True})
            self.assertEqual(result["state"], "PRUNED")
            self.assertTrue(any(failure["path"] == str(outside) and "resolves outside the store" in failure["error"]
                                for failure in result["failures"]), result["failures"])
            self.assertNotIn(str(outside), result["directories"])
            self.assertEqual(sorted(str(item.relative_to(outside)) for item in outside.rglob("*")), before)
            # Not recorded as pruned: its payload is not gone (review of 796cb02).
            self.assertNotIn("archived", result["pruned"])
            self.assertFalse(client.request("show", {"world": "archived"})["payload_pruned"])
            self.assertEqual(client.request("doctor", {})["storeIntegrity"]["state"], "OK")

        finally:
            fixture.close()

    def test_a_world_with_any_directory_outside_the_store_keeps_all_of_them(self) -> None:
        # Review of 4490013: the first directories were removed before a later one was refused,
        # losing a payload without a record. Every directory is checked first now.
        fixture = _FixtureDaemon(self, _QUICK_AGENT)
        try:
            work, client, paths = fixture.work, fixture.client, fixture.paths
            client.request("init", {"roots": [str(work)], "kind": None, "primary": None, "confirmed": True})
            for name in ("kept", "archived"):
                self.assertEqual(client.request("fork", {"name": name, "mission": name, "agent": "fixture", "wait": True})["state"], "VALID")
            prepared = client.request("collapse.prepare", {"world": "kept"})
            client.request("collapse.commit", {"transactionId": prepared["transaction_id"]})
            shown = client.request("show", {"world": "archived"})
            overlay = paths.overlays / shown["instance_id"]
            self.assertTrue(overlay.is_dir())
            payload = Path(shown["payload_path"])
            outside = Path(fixture.temporary.name) / "outside-the-store"
            parent_mode, payload_mode = payload.parent.stat().st_mode, payload.stat().st_mode
            os.chmod(payload.parent, parent_mode | 0o700)
            os.chmod(payload, payload_mode | 0o700)
            os.rename(payload, outside)
            os.chmod(outside, payload_mode)
            payload.symlink_to(outside, target_is_directory=True)
            os.chmod(payload.parent, parent_mode)
            result = client.request("prune", {"dryRun": False, "confirmed": True})
            self.assertNotIn("archived", result["pruned"])
            self.assertTrue(overlay.is_dir())          # the directory inside the store was kept too
            self.assertTrue(outside.is_dir())
        finally:
            fixture.close()

    def test_links_in_a_pruned_tree_are_never_followed(self) -> None:
        # Review of 796cb02: making each directory writable before removal followed links, so an
        # agent's upper layer with a link to PRIME's content (or anywhere the account owns) had
        # prune set that directory to 0700. A link inside a 0000 directory was reached too.
        fixture = _FixtureDaemon(self, _QUICK_AGENT)
        try:
            work, client, paths = fixture.work, fixture.client, fixture.paths
            client.request("init", {"roots": [str(work)], "kind": None, "primary": None, "confirmed": True})
            for name in ("kept", "archived"):
                self.assertEqual(client.request("fork", {"name": name, "mission": name, "agent": "fixture", "wait": True})["state"], "VALID")
            prepared = client.request("collapse.prepare", {"world": "kept"})
            client.request("collapse.commit", {"transactionId": prepared["transaction_id"]})
            instance = client.request("show", {"world": "archived"})["instance_id"]
            overlay = paths.overlays / instance
            self.assertTrue(overlay.is_dir())
            victim = Path(fixture.temporary.name) / "victim"
            victim.mkdir(mode=0o755)
            os.chmod(victim, 0o755)
            prime = Path(os.path.realpath(work))
            prime_mode = os.stat(prime).st_mode & 0o7777
            hidden = overlay / "hidden"
            hidden.mkdir()
            (overlay / "to-victim").symlink_to(victim, target_is_directory=True)
            (hidden / "to-prime").symlink_to(prime, target_is_directory=True)
            os.chmod(hidden, 0o000)
            result = client.request("prune", {"dryRun": False, "confirmed": True})
            self.assertEqual(result["failures"], [])
            self.assertIn("archived", result["pruned"])
            self.assertFalse(overlay.exists())
            self.assertEqual(os.stat(victim).st_mode & 0o7777, 0o755)
            self.assertEqual(os.stat(prime).st_mode & 0o7777, prime_mode)
        finally:
            fixture.close()


class PruneRecordsOnlyWhatItRemoved(unittest.TestCase):
    """Review of 09f5c0b: a world was recorded pruned when nothing of it had been removed, and
    what a prune could not remove was never offered again."""

    def test_untouched_worlds_stay_retained_and_leftovers_are_offered_again(self) -> None:
        import signal
        from worldline.core import Core
        from worldline.fstree import NothingRemoved, remove_tree
        from worldline.prune import Pruner

        fixture = _FixtureDaemon(self, _QUICK_AGENT)

        def cleanup() -> None:
            for directory, subdirectories, _files in os.walk(fixture.temporary.name):
                for name in subdirectories:
                    path = os.path.join(directory, name)
                    if not os.path.islink(path):
                        os.chmod(path, os.stat(path).st_mode | 0o700)
            fixture.temporary.cleanup()

        self.addCleanup(cleanup)
        try:
            client = fixture.client
            client.request("init", {"roots": [str(fixture.work)], "kind": None, "primary": None, "confirmed": True})
            for name in ("kept", "archived"):
                self.assertEqual(client.request("fork", {"name": name, "mission": name, "agent": "fixture", "wait": True})["state"], "VALID")
            prepared = client.request("collapse.prepare", {"world": "kept"})
            client.request("collapse.commit", {"transactionId": prepared["transaction_id"]})
            instance = client.request("show", {"world": "archived"})["instance_id"]
        finally:
            fixture.process.send_signal(signal.SIGTERM)
            fixture.process.wait(timeout=15)
            fixture.errors.close()
        store = StateStore(fixture.paths, Core.shared())
        self.addCleanup(store.close)
        pruner = Pruner(fixture.paths, store)
        overlay = os.path.realpath(fixture.paths.overlays / instance)

        def plan() -> dict:
            return pruner.plan(older_than_days=None, keep=None, logs=False)

        # Every removal fails before anything is deleted: nothing is recorded.
        with mock.patch("worldline.prune.remove_tree", side_effect=NothingRemoved(13, "denied", "x")):
            result = pruner.apply(plan())
        self.assertNotIn("archived", result["pruned"])
        self.assertFalse(store.world(instance).payload_pruned)

        # The payload goes, the overlay cannot be opened: recorded as a partial prune.
        def everything_but_the_overlay(path, **kwargs):
            if os.path.realpath(path) == overlay:
                raise NothingRemoved(13, "denied", str(path))
            remove_tree(path, **kwargs)

        with mock.patch("worldline.prune.remove_tree", side_effect=everything_but_the_overlay):
            result = pruner.apply(plan())
        self.assertIn("archived", result["pruned"])
        self.assertTrue(store.world(instance).payload_pruned)
        self.assertTrue(os.path.isdir(overlay))

        # The overlay is offered again, removed, and the world stays pruned.
        leftovers = [entry for entry in plan()["worlds"] if entry.get("leftover")]
        self.assertEqual([entry["instanceId"] for entry in leftovers], [instance])
        result = pruner.apply({"worlds": leftovers})
        self.assertFalse(os.path.exists(overlay))
        self.assertTrue(store.world(instance).payload_pruned)
        self.assertEqual([entry for entry in plan()["worlds"] if entry.get("leftover")], [])


class StoreSchemaMigrations(unittest.TestCase):
    def _paths(self, root: Path) -> WorldlinePaths:
        env = {
            "HOME": str(root / "home"), "XDG_DATA_HOME": str(root / "data"), "XDG_STATE_HOME": str(root / "state"),
            "XDG_CONFIG_HOME": str(root / "config"), "XDG_RUNTIME_DIR": str(root / "runtime"),
        }
        for value in env.values():
            Path(value).mkdir(mode=0o700, parents=True, exist_ok=True)
        paths = WorldlinePaths.from_environment(env)
        paths.ensure()
        return paths

    def test_v1_store_is_migrated_forward_and_a_newer_store_is_refused(self) -> None:
        with tempfile.TemporaryDirectory(prefix="worldline-migrate-") as temporary:
            paths = self._paths(Path(temporary))
            legacy = _SCHEMA.replace(
                "    payload_pruned INTEGER NOT NULL DEFAULT 0 CHECK (payload_pruned IN (0, 1)),\n    pruned_at TEXT\n", "    risk TEXT NOT NULL CHECK (risk IN ('LOW','MEDIUM','HIGH'))\n"
            ).replace("    risk TEXT NOT NULL CHECK (risk IN ('LOW','MEDIUM','HIGH')),\n    risk TEXT", "    risk TEXT")
            self.assertNotIn("payload_pruned", legacy)
            connection = sqlite3.connect(paths.database)
            connection.executescript(legacy)
            connection.execute("PRAGMA user_version=1")
            connection.commit()
            connection.close()
            store = StateStore(paths)
            try:
                columns = {row[1] for row in store._connection.execute("PRAGMA table_info(worlds)")}
                self.assertIn("payload_pruned", columns)
                self.assertIn("pruned_at", columns)
                self.assertEqual(int(store._connection.execute("PRAGMA user_version").fetchone()[0]), STORE_SCHEMA_VERSION)
                history = store.get_meta("schemaMigrations")
                self.assertEqual([(item["from"], item["to"]) for item in history], [(1, 2)])
                # Reopening is idempotent.
            finally:
                store.close()
            again = StateStore(paths)
            try:
                self.assertEqual(len(again.get_meta("schemaMigrations")), 1)
            finally:
                again.close()
            connection = sqlite3.connect(paths.database)
            connection.execute("PRAGMA user_version=99")
            connection.commit()
            connection.close()
            with self.assertRaises(WorldlineError) as refused:
                StateStore(paths)
            self.assertEqual(refused.exception.code, "UNSUPPORTED_SCHEMA")
            self.assertEqual(refused.exception.details, {"found": 99, "supported": STORE_SCHEMA_VERSION})


class StatusDeltaIsBounded(unittest.TestCase):
    def test_summary_truncates_long_file_lists_and_record_keeps_them(self) -> None:
        world = World.create(
            alias="big", parent_instance=None, parent_content="sha256:" + "0" * 64, cause="x", actor="fixture",
            payload_path=Path("/p"), base_payload_path=Path("/b"), base_root="sha256:" + "0" * 64,
            root_set_hash="sha256:" + "0" * 64, mission_hash="sha256:" + "0" * 64,
        )
        files = [{"op": "ADD", "pathDisplay": f"f{i}"} for i in range(250)]
        world.delta = {"files": files, "added": 250, "modified": 0, "deleted": 0}
        summary = world.summary()
        self.assertEqual(len(summary["delta"]["files"]), World.SUMMARY_DELTA_LIMIT)
        self.assertTrue(summary["delta"]["truncated"])
        self.assertEqual(summary["delta"]["total"], 250)
        self.assertEqual(summary["delta"]["added"], 250)
        self.assertEqual(len(world.record()["delta"]["files"]), 250)
        self.assertFalse(summary["pruned"])


if __name__ == "__main__":
    unittest.main()
