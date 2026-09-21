from __future__ import annotations

import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest

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
