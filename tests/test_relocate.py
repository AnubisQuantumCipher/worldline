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

    def test_a_database_shared_with_the_old_store_is_refused(self) -> None:
        # A hard-linked copy (cp -al, rsync --link-dest) would rewrite the OLD store in place.
        self.new.database.unlink()
        os.link(self.old.database, self.new.database)
        with self.assertRaises(WorldlineError) as caught:
            self.relocation()
        self.assertIn("linked elsewhere", caught.exception.message)

    def test_a_dry_run_with_a_hot_wal_changes_no_byte(self) -> None:
        holder = sqlite3.connect(self.new.database)  # this process: not a holder the check excludes wrongly
        holder.execute("PRAGMA journal_mode=WAL")
        holder.execute("INSERT OR REPLACE INTO meta(key, value) VALUES ('hot', x'00')")
        holder.commit()
        self.assertTrue(Path(str(self.new.database) + "-wal").exists())
        before = (_tree_digest(self.new.state), os.stat(self.new.state).st_mtime_ns)
        self.relocation().run(dry_run=True)
        self.assertEqual((_tree_digest(self.new.state), os.stat(self.new.state).st_mtime_ns), before)
        holder.close()

    def test_install_backups_are_kept_content(self) -> None:
        backup = self.new.state / "install-backups" / "20260101T000000Z-1" / "state"
        backup.mkdir(parents=True)
        (backup / "copy.json").write_text(json.dumps({"payload": str(self.old.data / "worlds")}))
        result = self.relocation().run(dry_run=True)
        self.assertEqual(result["refusedFiles"], [])
        self.assertEqual(result["mentions"].get("install backup"), 1)

    def test_a_payload_that_resolves_into_the_old_store_is_refused(self) -> None:
        with sqlite3.connect(self.new.database) as connection:
            instance, payload = connection.execute(
                "SELECT instance_id, payload_path FROM worlds WHERE alias='sibling'").fetchone()
        copied = Path(payload.replace(str(self.old.data), str(self.new.data), 1))
        shutil.rmtree(copied)
        copied.symlink_to(payload)  # the new spelling, pointing back into the old store
        with self.assertRaises(WorldlineError) as caught:
            self.relocation().run()
        self.assertEqual(caught.exception.code, "RELOCATION_REFUSED")

    def test_a_stale_temporary_link_from_an_interrupted_run_is_cleared(self) -> None:
        live = next(p for p in sorted(self.new.live.iterdir()) if p.is_symlink())
        stale = live.with_name(f".{live.name}.relocate")
        stale.symlink_to(os.readlink(live))
        result = self.relocation().run()
        self.assertEqual(result["state"], "RELOCATED")
        self.assertFalse(stale.is_symlink())

    def test_unsafe_prime_content_is_reported(self) -> None:
        live = next(p for p in sorted(self.new.live.iterdir()) if p.is_symlink())
        os.chmod(os.path.realpath(live), 0o777)
        result = self.relocation().run(dry_run=True)
        self.assertGreaterEqual(result["liveContentUnsafeForClients"]["count"], 1)

    def test_group_write_outside_the_accounts_group_is_reported(self) -> None:
        other = next((gid for gid in os.getgroups() if gid != os.getegid()), None)
        if other is None:
            self.skipTest("needs a supplementary group")
        live = next(p for p in sorted(self.new.live.iterdir()) if p.is_symlink())
        target = Path(os.path.realpath(live))
        victim = next(p for p in sorted(target.iterdir()) if p.is_file())
        os.chown(victim, -1, other)
        os.chmod(victim, 0o664)
        result = self.relocation().run(dry_run=True)
        self.assertEqual(result["liveContentUnsafeForClients"]["count"], 1)

    def test_sockets_and_fifos_in_the_copy_are_skipped_not_fatal(self) -> None:
        # Relocating production's copy crashed on a dead world's socket (ENXIO on open).
        import socket as socket_module
        runtime = self.new.data / "overlays" / "dead-world" / "agent-runtime"
        runtime.mkdir(parents=True)
        server = socket_module.socket(socket_module.AF_UNIX, socket_module.SOCK_STREAM)
        self.addCleanup(server.close)
        previous = os.getcwd()
        os.chdir(runtime)  # a relative bind: the absolute path is longer than AF_UNIX allows
        try:
            server.bind("4.sock")
        finally:
            os.chdir(previous)
        os.mkfifo(runtime / "pipe")
        result = self.relocation().run(dry_run=True)
        self.assertEqual(result["refusedFiles"], [])

    def test_a_copy_reached_through_a_symlinked_directory_is_refused(self) -> None:
        # Review of ad64cd2: a "copy" that was the old store behind a link got the old store
        # rewritten in place. A link as the directory itself, and a link as one of its parents.
        alias = self.destination / "alias-state"
        alias.symlink_to(self.old.state, target_is_directory=True)
        with self.assertRaises(WorldlineError) as caught:
            Relocation(old_data=self.old.data, old_state=self.old.state, new_data=self.new.data, new_state=alias)
        self.assertIn("not a real directory", caught.exception.message)
        parent = self.destination / "alias-parent"
        parent.symlink_to(self.old.state.parent, target_is_directory=True)
        with self.assertRaises(WorldlineError) as caught:
            Relocation(old_data=self.old.data, old_state=self.old.state, new_data=self.new.data,
                       new_state=parent / self.old.state.name)
        self.assertIn("spelled by its real path", caught.exception.message)
        self.assertEqual((_tree_digest(self.old.data), _tree_digest(self.old.state)), self.old_digest)

    def test_the_copy_may_not_overlap_the_old_store(self) -> None:
        inner = self.old.data / "generations" / "nested-copy"
        inner.mkdir()
        self.addCleanup(inner.rmdir)
        with self.assertRaises(WorldlineError) as caught:
            Relocation(old_data=self.old.data, old_state=self.old.state, new_data=inner, new_state=self.new.state)
        # One prefix inside another is refused by name before the real paths are compared.
        self.assertIn("contain one another", caught.exception.message)
        # Spelled apart (the old store through a link), the real paths still overlap.
        alias = self.destination / "old-alias"
        alias.symlink_to(self.old.data.parent, target_is_directory=True)
        with self.assertRaises(WorldlineError) as caught:
            Relocation(old_data=alias / self.old.data.name, old_state=self.old.state,
                       new_data=inner, new_state=self.new.state)
        self.assertIn("overlap", caught.exception.message)

    def test_a_bind_mounted_copy_is_refused_by_identity(self) -> None:
        # A bind mount is the same directory under another name; realpath cannot see it. The
        # identity check is exercised here by making os.stat report the old store's identity.
        real_stat = os.stat

        def same_identity(path, *args, **kwargs):
            if os.fspath(path) == str(self.new.state):
                return real_stat(self.old.state, *args, **kwargs)
            return real_stat(path, *args, **kwargs)

        with mock.patch("worldline.relocate.os.stat", side_effect=same_identity):
            with self.assertRaises(WorldlineError) as caught:
                self.relocation()
        self.assertIn("under another name", caught.exception.message)

    def test_a_recorded_location_that_links_back_into_the_old_store_is_refused_while_planning(self) -> None:
        # The events file is recorded in causal_events.canonical_path; a link there would have the
        # relocated daemon read the old store's file. Refused before anything is written.
        events = self.new.state / "events"
        victim = next(p for p in sorted(events.iterdir()) if p.is_file())
        victim.unlink()
        victim.symlink_to(self.old.state / "events" / victim.name)
        database = (self.new.state / "worldline.sqlite3").read_bytes()
        with self.assertRaises(WorldlineError) as caught:
            self.relocation().run()
        self.assertIn("resolves outside the new store", caught.exception.message)
        self.assertEqual((self.new.state / "worldline.sqlite3").read_bytes(), database)
        self.assertEqual((_tree_digest(self.old.data), _tree_digest(self.old.state)), self.old_digest)

    def _set_column(self, alias: str, column: str, transform) -> bytes:
        connection = sqlite3.connect(self.new.state / "worldline.sqlite3")
        try:
            (value,) = connection.execute(f"SELECT {column} FROM worlds WHERE alias=?", (alias,)).fetchone()
            changed = transform(value)
            connection.execute(f"UPDATE worlds SET {column}=? WHERE alias=?", (changed, alias))
            connection.commit()
        finally:
            connection.close()
        return changed

    def test_a_world_evidence_record_that_names_the_old_store_is_kept_byte_for_byte(self) -> None:
        # Production's store holds one: a private evaluator's check recorded its sandbox command
        # line, with bind sources in the world's overlay. The evidence is hashed into the world's
        # identity; it is a record of where the check ran, not a location anything opens.
        recorded = str(self.old.data / "overlays" / "x" / "checks" / "exam" / "frozen" / "0")
        evidence = self._set_column("sibling", "evidence",
                                    lambda value: json.dumps({**json.loads(value), "recordedBind": recorded}).encode())
        plan = self.relocation().run(dry_run=True)
        self.assertEqual(plan["refusedDatabaseColumns"], {})
        self.assertEqual(plan["recordColumnsKept"], {"worlds.evidence": 1})
        result = self.relocation().run()
        self.assertEqual(result["state"], "RELOCATED")
        self.assertEqual(result["recordColumnsKept"], {"worlds.evidence": 1})
        connection = sqlite3.connect(f"file:{self.new.state / 'worldline.sqlite3'}?mode=ro", uri=True)
        try:
            (kept,) = connection.execute("SELECT evidence FROM worlds WHERE alias='sibling'").fetchone()
        finally:
            connection.close()
        self.assertEqual(kept, evidence)

    def test_any_other_column_that_names_the_old_store_refuses(self) -> None:
        self._set_column("sibling", "cause", lambda value: f"{value} {self.old.state}/elsewhere")
        plan = self.relocation().run(dry_run=True)
        self.assertEqual(plan["refusedDatabaseColumns"], {"worlds.cause": 1})
        self.assertEqual(plan["recordColumnsKept"], {})
        with self.assertRaises(WorldlineError):
            self.relocation().run()
        self.assertEqual((_tree_digest(self.old.data), _tree_digest(self.old.state)), self.old_digest)

    def test_links_where_the_daemon_makes_none_are_refused(self) -> None:
        manifests = sorted(path for path in (self.new.data / "generations").glob("*/manifests/*") if path.is_file())
        self.assertTrue(manifests)
        victim = manifests[0]
        outside = self.destination / "outside" / victim.name
        outside.parent.mkdir()
        shutil.copy2(victim, outside)
        victim.unlink()
        victim.symlink_to(outside)
        refused = self.relocation().run(dry_run=True)["refusedFiles"]
        self.assertTrue(any(victim.name in entry and "where the daemon makes none" in entry for entry in refused), refused)
        with self.assertRaises(WorldlineError):
            self.relocation().run()
        self.assertEqual((_tree_digest(self.old.data), _tree_digest(self.old.state)), self.old_digest)

    def test_a_content_link_into_the_old_store_is_refused_and_a_harmless_one_kept(self) -> None:
        # Before relocation the copy's live links still name the old store: map the target.
        live = next(p for p in sorted(self.new.live.iterdir()) if p.is_symlink())
        target = os.readlink(live)
        self.assertTrue(target.startswith(str(self.old.data) + "/"), target)
        content = Path(str(self.new.data) + target[len(str(self.old.data)):])
        self.assertTrue(content.is_dir())
        (content / "harmless").symlink_to("/usr/bin/true")
        self.assertEqual(self.relocation().run(dry_run=True)["refusedFiles"], [])
        (content / "sneaky").symlink_to(os.path.relpath(self.old.data / "live", content))
        refused = self.relocation().run(dry_run=True)["refusedFiles"]
        self.assertTrue(any("sneaky" in entry and "resolves into the old store" in entry for entry in refused), refused)
        self.assertFalse(any("harmless" in entry for entry in refused), refused)

    def test_each_entry_is_counted_once(self) -> None:
        relocation = self.relocation()
        walked = 0
        for root in (self.new.data, self.new.state):
            for directory, subdirectories, files in os.walk(root):
                walked += len(subdirectories) + len(files)
                subdirectories[:] = [d for d in subdirectories if not os.path.islink(os.path.join(directory, d))
                                     and os.access(os.path.join(directory, d), os.R_OK | os.X_OK)]
            walked += 1  # the root itself
        with mock.patch("worldline.relocate.os.geteuid", return_value=os.getuid() + 1):
            count, _sample, _undescended = relocation._foreign_entries()
        self.assertEqual(count, walked)

    def test_a_held_daemon_lock_refuses_the_run(self) -> None:
        import fcntl
        from worldline.relocate import main
        lock_path = self.destination / "worldlined.lock"
        holder = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o600)
        self.addCleanup(os.close, holder)
        fcntl.flock(holder, fcntl.LOCK_EX)
        code = main(["--from-data", str(self.old.data), "--from-state", str(self.old.state),
                     "--to-data", str(self.new.data), "--to-state", str(self.new.state),
                     "--dry-run", "--daemon-lock", str(lock_path)])
        self.assertEqual(code, 1)

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
