"""Relocating a stopped store: its recorded locations follow it, and nothing else changes.

The fixture store has a registered root, two collapses (so PRIME's content lives in a committed
transaction's payload and the previous mapping is kept), an archived world and the canonical
event and receipt files. It is copied to a second location, relocated there, served by a fresh
daemon, and must answer exactly as before and keep working.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

from worldline.canonical import canonical_bytes
from worldline.client import DaemonClient
from worldline.errors import WorldlineError
from worldline.paths import WorldlinePaths
from worldline.relocate import Relocation

from tests.test_lifecycle_integrity import _FixtureDaemon, _QUICK_AGENT

REPO = Path(__file__).resolve().parents[1]


def _tree_digest(root: Path) -> str:
    """Names, link targets, modes and bytes of everything readable under root."""
    digest = hashlib.sha256()
    for directory, subdirectories, files in os.walk(root):
        subdirectories.sort()
        for name in sorted(files + [d for d in subdirectories if os.path.islink(os.path.join(directory, d))]):
            path = os.path.join(directory, name)
            digest.update(os.fsencode(os.path.relpath(path, root)) + b"\0")
            info = os.lstat(path)
            digest.update(str(info.st_mode).encode() + b"\0")
            if os.path.islink(path):
                digest.update(os.fsencode(os.readlink(path)))
            elif os.access(path, os.R_OK):
                with open(path, "rb") as stream:
                    digest.update(stream.read())
        subdirectories[:] = [d for d in subdirectories if not os.path.islink(os.path.join(directory, d))
                             and os.access(os.path.join(directory, d), os.R_OK | os.X_OK)]
    return digest.hexdigest()


def _open_directories(root: Path) -> None:
    # Overlay work directories are 000; the owner may open them (as prune's discard does), and a
    # real migration copies as root instead.
    for directory, subdirectories, _files in os.walk(root):
        for name in subdirectories:
            path = os.path.join(directory, name)
            if not os.path.islink(path):
                os.chmod(path, os.stat(path).st_mode | 0o700)


class RelocateAStore(unittest.TestCase):
    def setUp(self) -> None:
        fixture = _FixtureDaemon(self, _QUICK_AGENT)
        self.addCleanup(lambda: (_open_directories(Path(fixture.temporary.name)), fixture.temporary.cleanup()))
        try:
            client, work = fixture.client, fixture.work
            client.request("init", {"roots": [str(work)], "kind": None, "primary": None, "confirmed": True})
            for name in ("first", "second"):
                self.assertEqual(client.request("fork", {"name": name, "mission": name, "agent": "fixture", "wait": True})["state"], "VALID")
                prepared = client.request("collapse.prepare", {"world": name})
                client.request("collapse.commit", {"transactionId": prepared["transaction_id"]})
            self.assertEqual(client.request("fork", {"name": "sibling", "mission": "s", "agent": "fixture", "wait": True})["state"], "VALID")
            self.status = client.request("status")
            self.log = client.request("log", {"verify": True})
        finally:
            # Stop the daemon but keep its tree: close() would delete the store under test.
            fixture.process.send_signal(signal.SIGTERM)
            fixture.process.wait(timeout=15)
            fixture.errors.close()
        self.assertEqual(fixture.process.returncode, 0, fixture.error_log.read_text(errors="replace"))
        self.fixture = fixture
        self.work = work
        self.old = fixture.paths
        self.destination = Path(tempfile.mkdtemp(prefix="worldline-relocated-"))
        # Overlay work directories are 000: open them, or rmtree leaves the copy behind.
        self.addCleanup(lambda: (_open_directories(self.destination), shutil.rmtree(self.destination, True)))
        self.env = {
            "HOME": str(self.destination / "home"),
            "XDG_DATA_HOME": str(self.destination / "data"),
            "XDG_STATE_HOME": str(self.destination / "state"),
            "XDG_CONFIG_HOME": str(self.destination / "config"),
            "XDG_RUNTIME_DIR": str(self.destination / "runtime"),
        }
        for value in self.env.values():
            Path(value).mkdir(mode=0o700)
        self.new = WorldlinePaths.from_environment(self.env)
        _open_directories(self.old.data)
        for source, target in ((self.old.data, self.new.data), (self.old.state, self.new.state),
                               (self.old.config, self.new.config)):
            shutil.copytree(source, target, symlinks=True)
        self.old_digest = (_tree_digest(self.old.data), _tree_digest(self.old.state))

    def relocation(self) -> Relocation:
        return Relocation(old_data=self.old.data, old_state=self.old.state,
                          new_data=self.new.data, new_state=self.new.state)

    def serve(self) -> tuple[subprocess.Popen, DaemonClient]:
        env = {**os.environ, **self.env, "PYTHONPATH": str(REPO / "runtime"), "PYTHONDONTWRITEBYTECODE": "1",
               "WORLDLINE_CORE_LIB": str(REPO / "lib/libworldline_core.so")}
        errors = (self.destination / "worldlined.stderr").open("wb")
        self.addCleanup(errors.close)
        process = subprocess.Popen([sys.executable, "-m", "worldline.daemon_main"], env=env,
                                   stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=errors)

        def stop() -> None:
            if process.poll() is None:
                process.send_signal(signal.SIGTERM)
                process.wait(timeout=15)
        self.addCleanup(stop)
        deadline = time.monotonic() + 15
        while not self.new.socket.exists() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(0.02)
        if process.poll() is not None or not self.new.socket.exists():
            self.fail((self.destination / "worldlined.stderr").read_text(errors="replace"))
        return process, DaemonClient(self.new, timeout=120)

    def test_a_relocated_store_answers_as_before_and_keeps_working(self) -> None:
        result = self.relocation().run()
        self.assertEqual(result["state"], "RELOCATED")
        rows = result["rewritten"]["databaseRows"]
        self.assertGreater(rows["worlds.payload_path"], 0)
        self.assertGreater(rows["receipts.canonical_path"], 0)
        self.assertGreater(result["rewritten"]["transactionRecords"], 0)
        self.assertGreater(result["rewritten"]["mappingLinks"], 0)
        self.assertEqual(result["verification"]["chains"], {k: self.log["verification"][k] for k in ("causalEvents", "receipts")})
        # The old copy was never written.
        self.assertEqual((_tree_digest(self.old.data), _tree_digest(self.old.state)), self.old_digest)

        # The operator's link is not the tool's to change; the migration re-points it.
        root_key = next(p.name for p in sorted(self.new.live.iterdir()) if p.is_symlink())
        self.work.unlink()
        self.work.symlink_to(self.new.live / root_key)

        _process, client = self.serve()
        status = client.request("status")
        self.assertEqual(status["prime"]["id"], self.status["prime"]["id"])
        verified = client.request("log", {"verify": True})["verification"]
        self.assertEqual(verified, self.log["verification"])
        self.assertEqual((self.work / "prime.txt").read_text(encoding="utf-8"), "prime")
        # And it is a working store: a fork and a collapse on the relocated copy.
        self.assertEqual(client.request("fork", {"name": "after", "mission": "a", "agent": "fixture", "wait": True})["state"], "VALID")
        prepared = client.request("collapse.prepare", {"world": "after"})
        client.request("collapse.commit", {"transactionId": prepared["transaction_id"]})
        self.assertTrue(os.path.realpath(self.work).startswith(os.path.realpath(self.new.data)))

    def test_a_dry_run_changes_nothing_and_names_what_it_would_rewrite(self) -> None:
        before = (_tree_digest(self.new.data), _tree_digest(self.new.state))
        result = self.relocation().run(dry_run=True)
        self.assertEqual(result["state"], "DRY_RUN")
        self.assertGreater(result["locationRows"]["worlds.payload_path"], 0)
        self.assertEqual((result["refusedFiles"], result["refusedDatabaseColumns"]), ([], {}))
        self.assertEqual((_tree_digest(self.new.data), _tree_digest(self.new.state)), before)

    def test_a_store_with_an_open_world_is_not_relocated(self) -> None:
        with sqlite3.connect(self.new.database) as connection:
            connection.execute("UPDATE worlds SET state='MUTABLE' WHERE alias='sibling'")
        with self.assertRaises(WorldlineError) as caught:
            self.relocation().run()
        self.assertEqual(caught.exception.code, "RELOCATION_REFUSED")
        self.assertEqual(caught.exception.details["worlds"], ["sibling"])

    def test_an_unknown_mention_of_the_old_store_refuses(self) -> None:
        (self.new.state / "stray.json").write_text(json.dumps({"path": str(self.old.data / "live")}))
        with self.assertRaises(WorldlineError) as caught:
            self.relocation().run()
        self.assertIn("state/stray.json", caught.exception.details["refusedFiles"])

    def test_a_mention_in_any_other_database_column_refuses(self) -> None:
        with sqlite3.connect(self.new.database) as connection:
            connection.execute("INSERT OR REPLACE INTO meta(key, value) VALUES ('stray', ?)",
                               (json.dumps(str(self.old.state / "x")).encode(),))
        with self.assertRaises(WorldlineError) as caught:
            self.relocation().run()
        self.assertIn("meta.value", caught.exception.details["refusedDatabaseColumns"])

    def test_a_daemon_holding_the_copy_open_refuses(self) -> None:
        holder = subprocess.Popen(
            [sys.executable, "-c", "import sqlite3, sys, time; c = sqlite3.connect(sys.argv[1]); "
             "c.execute('SELECT count(*) FROM worlds').fetchone(); print('open', flush=True); time.sleep(60)",
             str(self.new.database)], stdout=subprocess.PIPE, text=True)
        self.addCleanup(holder.wait)
        self.addCleanup(holder.kill)
        self.assertEqual(holder.stdout.readline().strip(), "open")
        with self.assertRaises(WorldlineError) as caught:
            self.relocation().run()
        self.assertIn(holder.pid, caught.exception.details["pids"])

    def test_a_copy_the_runner_does_not_own_refuses(self) -> None:
        with mock.patch("worldline.relocate.os.geteuid", return_value=os.getuid() + 1):
            with self.assertRaises(WorldlineError) as caught:
                self.relocation().run()
        self.assertIn("not owned by the account", caught.exception.message)

    def test_an_unrewritable_mention_refuses_before_anything_is_written(self) -> None:
        # A canonical record naming the old store mid-string: the first candidate committed the
        # database rewrite before discovering it, leaving the copy half-relocated (review r2).
        record = sorted((self.new.state / "transactions").glob("*.json"))[0]
        value = json.loads(record.read_bytes())
        value["note"] = f"failed near {self.old.data}/live"
        record.write_bytes(canonical_bytes(value))
        with sqlite3.connect(self.new.database) as connection:
            before = connection.execute("SELECT payload_path FROM worlds ORDER BY rowid").fetchall()
        with self.assertRaises(WorldlineError) as caught:
            self.relocation().run()
        self.assertEqual(caught.exception.code, "RELOCATION_REFUSED")
        with sqlite3.connect(self.new.database) as connection:
            self.assertEqual(connection.execute("SELECT payload_path FROM worlds ORDER BY rowid").fetchall(), before)
        live = next(p for p in sorted(self.new.live.iterdir()) if p.is_symlink())
        self.assertTrue(os.readlink(live).startswith(str(self.old.data)))

    def test_nested_or_relative_directories_are_refused(self) -> None:
        for arguments in ({"new_data": self.old.data / "inner"}, {"old_data": Path("relative/data")}):
            with self.subTest(arguments=str(arguments)):
                values = {"old_data": self.old.data, "old_state": self.old.state,
                          "new_data": self.new.data, "new_state": self.new.state, **arguments}
                if values["new_data"] != self.new.data:
                    values["new_data"].mkdir(exist_ok=True)
                with self.assertRaises(WorldlineError) as caught:
                    Relocation(**values)
                self.assertEqual(caught.exception.code, "RELOCATION_REFUSED")


if __name__ == "__main__":
    unittest.main()
