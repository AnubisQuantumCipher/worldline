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
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

from worldline.canonical import canonical_bytes
from worldline.client import DaemonClient
from worldline.errors import WorldlineError
from worldline.paths import STORE_LOCK_NAME, WorldlinePaths
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

    def copy_content(self) -> Path:
        """The copy's PRIME content for the first root. Before relocation the copy's live links
        still name the old store; following them would reach the OLD store's content."""
        live = next(p for p in sorted(self.new.live.iterdir()) if p.is_symlink())
        target = os.readlink(live)
        self.assertTrue(target.startswith(str(self.old.data) + "/"), target)
        return Path(str(self.new.data) + target[len(str(self.old.data)):])

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
        os.chmod(self.copy_content(), 0o777)
        result = self.relocation().run(dry_run=True)
        self.assertGreaterEqual(result["liveContentUnsafeForClients"]["count"], 1)

    def test_the_report_reads_the_copy_not_the_old_store(self) -> None:
        # Review of 796cb02: the report followed the copy's unrewritten links into the old store.
        old_content = Path(os.path.realpath(next(p for p in sorted(self.old.live.iterdir()) if p.is_symlink())))
        os.chmod(old_content, 0o777)
        self.addCleanup(os.chmod, old_content, 0o755)
        self.assertEqual(self.relocation().run(dry_run=True)["liveContentUnsafeForClients"]["count"], 0)

    def test_group_write_outside_the_accounts_group_is_reported(self) -> None:
        other = next((gid for gid in os.getgroups() if gid != os.getegid()), None)
        if other is None:
            self.skipTest("needs a supplementary group")
        target = self.copy_content()
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
            count = relocation._walk_copy()["foreignOwned"]["count"]
        self.assertEqual(count, walked)

    def test_a_held_store_lock_refuses_the_run(self) -> None:
        # The copy's own lock, which worldlined takes before it opens anything.
        from worldline.paths import acquire_store_lock
        lock = acquire_store_lock(self.new.state, holder="a daemon", create_directory=False)
        self.addCleanup(os.close, lock)
        database = (self.new.state / "worldline.sqlite3").read_bytes()
        for dry_run in (True, False):
            with self.subTest(dry_run=dry_run):
                with self.assertRaises(WorldlineError) as caught:
                    self.relocation().run(dry_run=dry_run)
                self.assertIn("store lock is held", caught.exception.message)
        self.assertEqual((self.new.state / "worldline.sqlite3").read_bytes(), database)

    def test_a_daemon_cannot_start_on_the_copy_while_the_relocation_holds_its_lock(self) -> None:
        # Review of 796cb02: a refused daemon had already migrated the database, reset meta rows
        # and changed directory modes; and a restarted unit took a fresh lock file. The lock is
        # taken here with flock directly, as the relocation does, at <state>/<the store lock>.
        import fcntl
        lock = os.open(self.new.state / STORE_LOCK_NAME, os.O_RDWR | os.O_CREAT | os.O_CLOEXEC, 0o600)
        self.addCleanup(os.close, lock)
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        before = (_tree_digest(self.new.data), (self.new.state / "worldline.sqlite3").read_bytes(),
                  os.stat(self.new.generations).st_mode)
        env = {**os.environ, **self.env, "PYTHONPATH": str(REPO / "runtime"), "PYTHONDONTWRITEBYTECODE": "1"}
        result = subprocess.run([sys.executable, "-B", "-m", "worldline.daemon_main"], env=env,
                                capture_output=True, timeout=60)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn(b"DAEMON_ALREADY_RUNNING", result.stderr)
        self.assertEqual((_tree_digest(self.new.data), (self.new.state / "worldline.sqlite3").read_bytes(),
                          os.stat(self.new.generations).st_mode), before)

    def test_a_file_linked_outside_the_copy_refuses(self) -> None:
        # Review of 796cb02: a `cp -al` copy shares inodes with the old store.
        events = self.new.state / "events"
        victim = next(p for p in sorted(events.iterdir()) if p.is_file())
        outside = self.destination / "outside-link"
        os.link(victim, outside)
        report = self.relocation().run(dry_run=True)
        self.assertEqual(report["linkedOutsideCopy"]["count"], 1)
        with self.assertRaises(WorldlineError):
            self.relocation().run()

    def test_directories_it_cannot_read_refuse_unless_they_are_overlay_work_directories(self) -> None:
        work = self.new.data / "overlays" / "3d55cbbf-955c-4fd0-951b-adee9d9daf09" / ("b" * 64) / "work" / "work"
        work.mkdir(parents=True)
        os.chmod(work, 0)
        self.addCleanup(os.chmod, work, 0o700)
        report = self.relocation().run(dry_run=True)
        self.assertEqual(report["unreadableDirectories"], [])
        self.assertGreaterEqual(report["foreignOwned"]["overlayWorkDirectoriesNotDescended"], 1)
        other = self.new.data / "worlds" / "sealed"
        other.mkdir(parents=True)
        os.chmod(other, 0)
        self.addCleanup(os.chmod, other, 0o700)
        report = self.relocation().run(dry_run=True)
        self.assertEqual(report["unreadableDirectories"], ["data/worlds/sealed"])
        with self.assertRaises(WorldlineError):
            self.relocation().run()

    def test_a_mount_inside_the_copy_refuses(self) -> None:
        # Review of 796cb02: a bind of the old `live` inside the copy had the old store rewritten.
        # Simulated: the walk sees a different device for the copy's `live`.
        real_lstat = os.lstat
        target = str(self.new.live)

        def lstat(path, *args, **kwargs):
            info = real_lstat(path, *args, **kwargs)
            if os.fsdecode(path) == target:
                values = list(info)
                values[2] = info.st_dev + 1
                return os.stat_result(values)
            return info

        with mock.patch("worldline.relocate.os.lstat", side_effect=lstat):
            report = self.relocation().run(dry_run=True)
        self.assertEqual(report["mountsInsideCopy"], ["data/live"])

    def test_a_real_bind_mount_inside_the_copy_refuses(self) -> None:
        # Review of 4490013: a bind mount on the same filesystem has the same device number;
        # the old store's `live` bound over the copy's got the old store rewritten.
        bwrap = shutil.which("bwrap")
        if bwrap is None:
            self.skipTest("bwrap is required to make a mount without privileges")
        old_live = _tree_digest(self.old.data / "live")
        code = ("import sys; from worldline.relocate import main; "
                "sys.exit(main(sys.argv[1:]))")
        arguments = ["--from-data", str(self.old.data), "--from-state", str(self.old.state),
                     "--to-data", str(self.new.data), "--to-state", str(self.new.state)]
        result = subprocess.run(
            [bwrap, "--dev-bind", "/", "/", "--bind", str(self.old.data / "live"), str(self.new.data / "live"),
             "--", sys.executable, "-B", "-c", code, *arguments],
            env={**os.environ, "PYTHONPATH": str(REPO / "runtime"), "PYTHONDONTWRITEBYTECODE": "1"},
            capture_output=True, timeout=120)
        if b"No permissions to creating new namespace" in result.stderr or b"setting up uid map" in result.stderr:
            self.skipTest("unprivileged user namespaces are not available")
        self.assertEqual(result.returncode, 1, result.stderr.decode(errors="replace")[-2000:])
        self.assertIn(b"data/live", result.stderr)
        self.assertEqual(_tree_digest(self.old.data / "live"), old_live)

    def test_a_work_directory_outside_the_overlay_layout_refuses(self) -> None:
        # Review of 4490013: any unreadable `work/work` was exempt, even inside PRIME's content.
        planted = self.copy_content() / "work" / "work"
        planted.mkdir(parents=True)
        os.chmod(planted, 0)
        self.addCleanup(os.chmod, planted, 0o700)
        report = self.relocation().run(dry_run=True)
        self.assertEqual(len(report["unreadableDirectories"]), 1, report["unreadableDirectories"])

    def test_work_directories_an_agent_can_make_are_not_overlayfs_ones(self) -> None:
        # Review of 09f5c0b: `agent-runtime/work/work` and a check named `work` matched the rule.
        world = "3d55cbbf-955c-4fd0-951b-adee9d9daf09"
        made = []
        for layout in ((world, "agent-runtime"), (world, "checks", "work")):
            planted = self.new.data.joinpath("overlays", *layout, "work", "work") if layout[1] == "agent-runtime" \
                else self.new.data.joinpath("overlays", *layout, "work")
            planted.mkdir(parents=True)
            os.chmod(planted, 0)
            self.addCleanup(os.chmod, planted, 0o700)
            made.append(planted)
        genuine = self.new.data / "overlays" / world / ("a" * 64) / "work" / "work"
        genuine.mkdir(parents=True)
        os.chmod(genuine, 0)
        self.addCleanup(os.chmod, genuine, 0o700)
        report = self.relocation().run(dry_run=True)
        self.assertEqual(len(report["unreadableDirectories"]), 2, report["unreadableDirectories"])
        self.assertGreaterEqual(report["foreignOwned"]["overlayWorkDirectoriesNotDescended"], 1)

    def test_a_bind_mounted_lock_file_is_refused_before_it_is_written(self) -> None:
        # Review of 09f5c0b: the lock was written before the mount table was read.
        bwrap = shutil.which("bwrap")
        if bwrap is None:
            self.skipTest("bwrap is required to make a mount without privileges")
        old_lock = self.old.state / STORE_LOCK_NAME
        old_lock.write_text("4242 worldlined\n")
        new_lock = self.new.state / STORE_LOCK_NAME
        new_lock.write_text("placeholder\n")
        code = "import sys; from worldline.relocate import main; sys.exit(main(sys.argv[1:]))"
        arguments = ["--from-data", str(self.old.data), "--from-state", str(self.old.state),
                     "--to-data", str(self.new.data), "--to-state", str(self.new.state)]
        result = subprocess.run(
            [bwrap, "--dev-bind", "/", "/", "--bind", str(old_lock), str(new_lock), "--", sys.executable, "-B", "-c", code, *arguments],
            env={**os.environ, "PYTHONPATH": str(REPO / "runtime"), "PYTHONDONTWRITEBYTECODE": "1"},
            capture_output=True, timeout=120)
        self.assertEqual(result.returncode, 1, result.stderr.decode(errors="replace")[-2000:])
        self.assertEqual(old_lock.read_text(), "4242 worldlined\n")

    def test_a_view_of_the_old_store_at_the_copys_path_refuses(self) -> None:
        # Review of 09f5c0b: a FUSE or network view has a device of its own. Simulated: the
        # canary made in the copy shows up in the old store.
        real = os.path.lexists

        def lexists(path):
            return True if ".worldline-relocate-canary-" in os.fsdecode(path) else real(path)

        with mock.patch("worldline.relocate.os.path.lexists", side_effect=lexists):
            with self.assertRaises(WorldlineError) as caught:
                self.relocation().run()
        self.assertIn("another filesystem", caught.exception.message)
        self.assertEqual([p.name for p in self.new.data.iterdir() if "canary" in p.name], [])

    def test_verification_requires_mapping_links_like_the_daemon(self) -> None:
        # Review of 09f5c0b: a dereferenced live mapping passed verification and the daemon then
        # refused it.
        relocation = self.relocation()
        relocation.run()
        live = next(p for p in sorted(self.new.live.iterdir()) if p.is_symlink())
        content = Path(os.path.realpath(live))
        live.unlink()
        shutil.copytree(content, live, symlinks=True)
        with self.assertRaises(WorldlineError) as caught:
            relocation.verify()
        self.assertIn("not a link to a payload", caught.exception.message)

    def test_a_hard_linked_lock_fails_the_dry_run_by_name(self) -> None:
        old_lock = self.old.state / STORE_LOCK_NAME
        old_lock.write_text("4242 worldlined\n")
        new_lock = self.new.state / STORE_LOCK_NAME
        new_lock.unlink(missing_ok=True)
        os.link(old_lock, new_lock)
        with self.assertRaises(WorldlineError) as caught:
            self.relocation().run(dry_run=True)
        self.assertNotIn("a daemon is using", caught.exception.message)

    def test_a_lock_its_owner_cannot_write_fails_the_dry_run(self) -> None:
        lock = self.new.state / STORE_LOCK_NAME
        lock.unlink(missing_ok=True)
        lock.write_text("")
        os.chmod(lock, 0o400)
        with self.assertRaises(WorldlineError):
            self.relocation().run(dry_run=True)

    def test_a_view_of_an_old_store_it_cannot_see_is_refused(self) -> None:
        # Review of c7d89f1: with the old store unreadable to the relocating account (the
        # dedicated-account migration), every identity check was skipped and the old store was
        # rewritten through a bind of it at the copy's path.
        bwrap = shutil.which("bwrap")
        if bwrap is None:
            self.skipTest("bwrap is required to make a mount without privileges")
        old_live = _tree_digest(self.old.data / "live")
        hidden = self.old.data.parent
        code = ("import os, sys; os.chmod(sys.argv[1], 0); "
                "from worldline.relocate import main; code = main(sys.argv[2:]); "
                "os.chmod(sys.argv[1], 0o700); sys.exit(code)")
        arguments = ["--from-data", str(self.old.data), "--from-state", str(self.old.state),
                     "--to-data", str(self.new.data), "--to-state", str(self.new.state)]
        result = subprocess.run(
            [bwrap, "--dev-bind", "/", "/", "--bind", str(self.old.data), str(self.new.data),
             "--", sys.executable, "-B", "-c", code, str(hidden), *arguments],
            env={**os.environ, "PYTHONPATH": str(REPO / "runtime"), "PYTHONDONTWRITEBYTECODE": "1"},
            capture_output=True, timeout=120)
        os.chmod(hidden, 0o700)
        self.assertEqual(result.returncode, 1, result.stderr.decode(errors="replace")[-2000:])
        self.assertIn(b"seen through a mount", result.stderr)
        self.assertEqual(_tree_digest(self.old.data / "live"), old_live)

    def test_a_holder_in_another_mount_namespace_is_found(self) -> None:
        # Review of c7d89f1: mount ids differ between namespaces, so matching them missed it.
        unshare = shutil.which("unshare")
        if unshare is None:
            self.skipTest("unshare is required")
        ready = self.destination / "holder-ready"
        holder = subprocess.Popen(
            [unshare, "--user", "--map-current-user", "--mount", sys.executable, "-c",
             "import sys, time; f = open(sys.argv[1], 'rb'); open(sys.argv[2], 'w').close(); time.sleep(60)",
             str(self.new.state / "worldline.sqlite3"), str(ready)])
        self.addCleanup(lambda: (holder.kill(), holder.wait()))
        for _ in range(100):
            if ready.exists():
                break
            time.sleep(0.05)
        if holder.poll() is not None:
            self.skipTest("unprivileged mount namespaces are not available")
        with self.assertRaises(WorldlineError) as caught:
            self.relocation().run(dry_run=True)
        self.assertIn("open in another process", caught.exception.message)

    def _world_without_payload(self, alias: str, state: str = "DEAD", *, old_too: bool = True,
                               identity: bool = True) -> Path:
        """Make `alias` a retained world in `state` whose payload is absent from the copy and, with
        `old_too`, from the old store as well; without `identity`, one that never received its
        content id. Returns where the copy's payload would be."""
        for database in (self.new.database, self.old.database):
            connection = sqlite3.connect(database)
            try:
                (payload,) = connection.execute("SELECT payload_path FROM worlds WHERE alias=?", (alias,)).fetchone()
                connection.execute("UPDATE worlds SET state=? WHERE alias=?", (state, alias))
                if not identity:
                    connection.execute("UPDATE worlds SET content_id=NULL WHERE alias=?", (alias,))
                connection.commit()
            finally:
                connection.close()
        copy = Path(str(self.new.data) + payload[len(str(self.old.data)):])
        for directory in (copy, Path(payload)) if old_too else (copy,):
            if directory.exists():
                _open_directories(directory)
                shutil.rmtree(directory)
        return copy

    def _hide_old_data(self) -> None:
        """What the operator's 0700 home is to a dedicated account: the old store cannot be searched."""
        mode = stat.S_IMODE(self.old.data.stat().st_mode)
        os.chmod(self.old.data, 0)
        self.addCleanup(os.chmod, self.old.data, mode)

    def _payload_rows(self) -> list[str]:
        connection = sqlite3.connect(f"file:{self.new.database}?mode=ro", uri=True)
        try:
            return [row[0] for row in connection.execute("SELECT payload_path FROM worlds ORDER BY rowid")]
        finally:
            connection.close()

    def test_a_retained_world_that_never_had_a_payload_is_reported_not_refused(self) -> None:
        # Rehearsal of 1.7.1 on a copy of a production store: six retained worlds without a payload
        # (in the old store too) made verification refuse, after the copy had been rewritten; the
        # dry run had said nothing.
        self._world_without_payload("sibling", "DEAD")
        planned = self.relocation().run(dry_run=True)
        self.assertEqual(planned["payloadsAbsentBeforeRelocation"]["count"], 1)
        entry = planned["payloadsAbsentBeforeRelocation"]["sample"][0]
        self.assertEqual((entry["alias"], entry["state"], entry["basis"], entry["oldStoreChecked"]),
                         ("sibling", "DEAD", "absent-in-old-store", True))
        self.assertEqual(planned["payloadsMissingFromCopy"]["count"], 0)
        result = self.relocation().run()
        self.assertEqual(result["state"], "RELOCATED")
        self.assertEqual(result["payloadsAbsentBeforeRelocation"]["count"], 1)
        self.assertEqual(result["verification"]["payloads"], "PRESENT_EXCEPT_ABSENT_FROM_OLD_STORE")
        self.assertEqual(result["verification"]["payloadsAbsentBeforeRelocation"], 1)

    def test_state_decides_nothing(self) -> None:
        # Review of 3416f89: a payload-less DEAD world is archived when a sibling collapses, and
        # the state rule then refused the whole store; production's four DEGRADED payload-less
        # worlds had identities, so no state or identity rule fits either.
        for state in ("ARCHIVED", "DEGRADED", "VALID"):
            with self.subTest(state=state):
                self._world_without_payload("sibling", state)
                entry = self.relocation().run(dry_run=True)["payloadsAbsentBeforeRelocation"]["sample"][0]
                self.assertEqual((entry["state"], entry["basis"]), (state, "absent-in-old-store"))

    def test_a_payload_the_old_store_still_has_refuses_before_anything_is_written(self) -> None:
        # Review of 24b511d: a VALID world's payload missing from the copy only was relocated and
        # reported PRESENT; revalidate and collapse then failed on it.
        self._world_without_payload("sibling", "VALID", old_too=False)
        planned = self.relocation().run(dry_run=True)
        self.assertEqual(planned["payloadsAbsentBeforeRelocation"]["count"], 0)
        self.assertEqual(planned["payloadsMissingFromCopy"]["count"], 1)
        self.assertEqual(planned["payloadsMissingFromCopy"]["sample"][0]["reason"], "present in the old store")
        before = self._payload_rows()
        with self.assertRaises(WorldlineError) as caught:
            self.relocation().run()
        self.assertIn("missing from the copy", caught.exception.message)
        self.assertEqual(self._payload_rows(), before)                # nothing rewritten

    def test_an_old_store_it_cannot_see_needs_evidence(self) -> None:
        # Review of 3416f89: where the old store was not visible, a DEGRADED payload lost by the
        # copy was exempted as never created. Without sight of it, only an attestation from a
        # caller who can see it, or a world that never received its identity, exempts.
        self._world_without_payload("sibling", "DEGRADED", old_too=False)
        self._hide_old_data()
        planned = self.relocation().run(dry_run=True)
        self.assertEqual(planned["payloadsAbsentBeforeRelocation"]["count"], 0)
        missing = planned["payloadsMissingFromCopy"]["sample"][0]
        self.assertFalse(missing["oldStoreChecked"])
        self.assertIn("--absent-in-old-store", missing["reason"])
        instance = missing["instanceId"]
        attested = Relocation(old_data=self.old.data, old_state=self.old.state, new_data=self.new.data,
                              new_state=self.new.state, absent_in_old_store=frozenset({instance})).run(dry_run=True)
        self.assertEqual(attested["payloadsAbsentBeforeRelocation"]["sample"][0]["basis"], "attested-absent-in-old-store")
        self.assertEqual(attested["payloadsMissingFromCopy"]["count"], 0)

    def test_a_missing_identity_is_not_evidence(self) -> None:
        # Review of ac9f621: finalization writes the payload before the identity, so a world whose
        # finalization was interrupted has a payload and no identity; "never created" exempted a
        # payload the old store still had.
        self._world_without_payload("sibling", "DEAD", old_too=False, identity=False)
        self._hide_old_data()
        planned = self.relocation().run(dry_run=True)
        self.assertEqual(planned["payloadsAbsentBeforeRelocation"]["count"], 0)
        self.assertIn("no evidence", planned["payloadsMissingFromCopy"]["sample"][0]["reason"])

    def test_an_old_store_that_is_not_there_is_no_evidence(self) -> None:
        # Review of ac9f621: with the old store moved away, or an empty directory at its path, a
        # missing path read as "seen absent", and a VALID payload lost by the copy was relocated.
        self._world_without_payload("sibling", "VALID", old_too=False)
        for case in ("moved away", "empty directory"):
            with self.subTest(case=case):
                aside = self.old.data.with_name(self.old.data.name + ".aside")
                os.rename(self.old.data, aside)
                self.addCleanup(lambda aside=aside: (shutil.rmtree(self.old.data, True) if self.old.data.exists() and not any(self.old.data.iterdir()) else None, os.rename(aside, self.old.data) if aside.exists() else None))
                if case == "empty directory":
                    self.old.data.mkdir()
                planned = self.relocation().run(dry_run=True)
                self.assertEqual(planned["payloadsAbsentBeforeRelocation"]["count"], 0)
                self.assertEqual(planned["payloadsMissingFromCopy"]["count"], 1)
                self.assertFalse(planned["payloadsMissingFromCopy"]["sample"][0]["oldStoreChecked"])
                if case == "empty directory":
                    self.old.data.rmdir()
                os.rename(aside, self.old.data)

    def test_a_link_on_the_old_payload_path_is_no_evidence(self) -> None:
        # Only a component that does not exist, reached without following a link, is absence.
        self._world_without_payload("sibling", "VALID")
        connection = sqlite3.connect(f"file:{self.old.database}?mode=ro", uri=True)
        try:
            (payload,) = connection.execute("SELECT payload_path FROM worlds WHERE alias='sibling'").fetchone()
        finally:
            connection.close()
        world_directory = Path(payload).parent
        elsewhere = self.destination / "elsewhere"
        elsewhere.mkdir()
        _open_directories(world_directory)
        shutil.rmtree(world_directory)
        world_directory.symlink_to(elsewhere, target_is_directory=True)
        planned = self.relocation().run(dry_run=True)
        self.assertEqual(planned["payloadsAbsentBeforeRelocation"]["count"], 0)
        self.assertFalse(planned["payloadsMissingFromCopy"]["sample"][0]["oldStoreChecked"])

    def test_the_attestation_is_accounted_for(self) -> None:
        from worldline.relocate import main
        self._world_without_payload("sibling", "DEGRADED", old_too=False)
        self._hide_old_data()
        planned = self.relocation().run(dry_run=True)
        instance = planned["payloadsMissingFromCopy"]["sample"][0]["instanceId"]
        attestation = self.destination / "attested.json"
        attestation.write_text(json.dumps([instance, "not-a-world"]))
        arguments = ["--from-data", str(self.old.data), "--from-state", str(self.old.state),
                     "--to-data", str(self.new.data), "--to-state", str(self.new.state),
                     "--absent-in-old-store", str(attestation), "--dry-run"]
        output = []
        with mock.patch("builtins.print", side_effect=lambda text, **kwargs: output.append(text)):
            self.assertEqual(main(arguments), 0)
        report = json.loads(output[0])["attestation"]
        self.assertEqual(report["sha256"], hashlib.sha256(attestation.read_bytes()).hexdigest())
        self.assertEqual((report["ids"], report["used"], report["unused"]), (2, 1, ["not-a-world"]))

    def test_the_attestation_can_arrive_on_standard_input(self) -> None:
        # Opening /dev/stdin reopens the pipe by path, which the relocating account may not do for
        # a pipe the operator created (rehearsal of 1.7.2); `-` reads the open descriptor.
        import io
        from worldline.relocate import main
        arguments = ["--from-data", str(self.old.data), "--from-state", str(self.old.state),
                     "--to-data", str(self.new.data), "--to-state", str(self.new.state),
                     "--absent-in-old-store", "-", "--dry-run"]
        stdin = io.TextIOWrapper(io.BytesIO(b'["not-a-world"]'))
        output = []
        with mock.patch("sys.stdin", stdin), mock.patch("builtins.print", side_effect=lambda text, **kwargs: output.append(text)):
            self.assertEqual(main(arguments), 0)
        self.assertEqual(json.loads(output[0])["attestation"]["unused"], ["not-a-world"])

    def test_the_attestation_must_be_a_list_of_ids(self) -> None:
        from worldline.relocate import main
        attestation = self.destination / "attested.json"
        attestation.write_text('{"not": "a list"}')
        arguments = ["--from-data", str(self.old.data), "--from-state", str(self.old.state),
                     "--to-data", str(self.new.data), "--to-state", str(self.new.state),
                     "--absent-in-old-store", str(attestation), "--dry-run"]
        with mock.patch("sys.stderr"), mock.patch("sys.stdout"):
            self.assertEqual(main(arguments), 1)

    def test_a_rerun_exempts_nothing(self) -> None:
        # Review of 24b511d: a rerun re-measured the rewritten copy, so a payload the first run
        # lost read as never there.
        self._world_without_payload("sibling", "DEAD")
        self.assertEqual(self.relocation().run()["state"], "RELOCATED")
        planned = self.relocation().run(dry_run=True)
        self.assertEqual(planned["payloadsAbsentBeforeRelocation"]["count"], 0)
        self.assertEqual(planned["payloadsMissingFromCopy"]["sample"][0]["reason"], "rerun on a rewritten copy")

    def test_a_payload_lost_after_planning_still_refuses(self) -> None:
        # What was absent is measured before anything is rewritten; a payload that disappears
        # after that (here, just before verification) is a relocation loss.
        connection = sqlite3.connect(f"file:{self.new.database}?mode=ro", uri=True)
        try:
            (payload,) = connection.execute("SELECT payload_path FROM worlds WHERE alias='sibling'").fetchone()
        finally:
            connection.close()
        copy = Path(str(self.new.data) + payload[len(str(self.old.data)):])
        real_verify = Relocation.verify

        def lose_then_verify(relocation, *args, **kwargs):
            _open_directories(copy)
            shutil.rmtree(copy)
            return real_verify(relocation, *args, **kwargs)

        with mock.patch.object(Relocation, "verify", lose_then_verify):
            with self.assertRaises(WorldlineError) as caught:
                self.relocation().run()
        self.assertIn("retained world payloads are missing from the new store", caught.exception.message)
        self.assertEqual(caught.exception.details["worlds"], ["sibling"])

    def test_a_store_before_payload_pruning_is_read(self) -> None:
        # Review of 24b511d: the check queried payload_pruned, which a store that never ran 1.2.0
        # or later does not have, and refused it with an OperationalError.
        connection = sqlite3.connect(":memory:")
        connection.execute("CREATE TABLE worlds (instance_id TEXT, alias TEXT, state TEXT, payload_path TEXT)")
        connection.execute("INSERT INTO worlds VALUES ('i', 'gone', 'DEAD', ?)",
                           (str(self.old.data / "worlds" / "i" / "payload"),))
        exempt, missing = self.relocation()._payloads_absent(connection)
        self.assertEqual([item["alias"] for item in exempt + missing], ["gone"])

    def test_a_fifo_named_like_the_wal_is_refused_at_once(self) -> None:
        # Review of c7d89f1: the holder check blocked opening it.
        wal = self.new.state / "worldline.sqlite3-wal"
        wal.unlink(missing_ok=True)
        os.mkfifo(wal)
        with self.assertRaises(WorldlineError) as caught:
            self.relocation()
        self.assertIn("not a regular file", caught.exception.message)

    def test_a_fifo_named_like_the_journal_is_refused_at_once(self) -> None:
        # Review of 300543c: SQLite looks for a rollback journal before it learns the database is
        # in WAL mode, so a FIFO there passed the dry run and hung the real run under the lock.
        journal = self.new.state / "worldline.sqlite3-journal"
        journal.unlink(missing_ok=True)
        os.mkfifo(journal)
        with self.assertRaises(WorldlineError) as caught:
            self.relocation()
        self.assertIn("worldline.sqlite3-journal in the copy is not a regular file", caught.exception.message)

    def test_a_held_copy_refuses_before_anything_is_written_into_it(self) -> None:
        # Review of 300543c: the canary was written into the copy's data and state directories
        # before the lock refused, so a kill in between left it in a live store.
        from worldline.paths import acquire_store_lock
        (self.new.state / STORE_LOCK_NAME).unlink(missing_ok=True)
        held = acquire_store_lock(self.new.state, holder="a daemon on the copy", create_directory=False)
        self.addCleanup(os.close, held)
        relocation = self.relocation()
        with mock.patch.object(Relocation, "_refuse_views_of_the_old_store") as canary:
            with self.assertRaises(WorldlineError) as caught:
                relocation.run()
        self.assertIn("a daemon is using the copy", caught.exception.message)
        canary.assert_not_called()

    def test_a_holder_is_found_when_stat_reports_another_device(self) -> None:
        # Review of 300543c: on btrfs, stat reports a subvolume's own device and mountinfo the
        # filesystem's, so matching the copy's stat identity against holders' mount tables never
        # matched. Simulated by a stat that reports another device for the copy's database.
        holder = subprocess.Popen(
            [sys.executable, "-c", "import sys, time; f = open(sys.argv[1], 'rb'); print('open', flush=True); time.sleep(60)",
             str(self.new.database)], stdout=subprocess.PIPE, text=True)
        self.addCleanup(holder.wait)
        self.addCleanup(holder.kill)
        self.assertEqual(holder.stdout.readline().strip(), "open")
        relocation = self.relocation()
        real_lstat = os.lstat
        database = str(self.new.database)

        def subvolume_lstat(path, *args, **kwargs):
            info = real_lstat(path, *args, **kwargs)
            if os.fsdecode(path).startswith(database):
                values = list(info[:10])
                values[2] = os.makedev(0, 4242)
                return os.stat_result(values)
            return info

        with mock.patch("worldline.relocate.os.lstat", side_effect=subvolume_lstat):
            holders = relocation._holders()
        self.assertIn(holder.pid, holders)

    def test_a_link_named_like_the_database_is_still_checked(self) -> None:
        # Since the review of 300543c the -journal gets the database's own checks, so a link there
        # refuses the relocation at once instead of being listed among the refused files.
        journal = self.new.state / "worldline.sqlite3-journal"
        journal.symlink_to(self.old.state / "worldline.sqlite3")
        with self.assertRaises(WorldlineError) as caught:
            self.relocation()
        self.assertIn("worldline.sqlite3-journal in the copy is linked elsewhere", caught.exception.message)

    def test_a_directory_at_the_lock_path_refuses_by_name(self) -> None:
        lock = self.new.state / STORE_LOCK_NAME
        lock.unlink(missing_ok=True)   # the copy carries the fixture daemon's lock file
        lock.mkdir()
        with self.assertRaises(WorldlineError) as caught:
            self.relocation().run()
        # Refused by the read-only check that now runs before anything is written into the copy
        # (review of 300543c), rather than by the lock's own open.
        self.assertEqual(caught.exception.code, "RELOCATION_REFUSED")
        self.assertIn("the store lock is not a regular", caught.exception.message)

    def test_a_deeply_nested_record_is_refused_by_name(self) -> None:
        from worldline.relocate import main
        record = next(iter(sorted((self.new.state / "transactions").glob("*.json"))))
        record.write_bytes(b"[" * 100000 + os.fsencode(self.old.data) + b"]" * 100000)
        self.assertEqual(main(["--from-data", str(self.old.data), "--from-state", str(self.old.state),
                               "--to-data", str(self.new.data), "--to-state", str(self.new.state), "--dry-run"]), 1)

    def test_revalidation_records_are_kept_and_other_meta_rows_refused(self) -> None:
        connection = sqlite3.connect(self.new.state / "worldline.sqlite3")
        try:
            record = json.dumps([{"results": [{"evaluatorBoundary": {"inputs": [
                {"frozen": f"{self.old.data}/overlays/w/checks/c/private-backend/frozen/0"}]}}]}]).encode()
            connection.execute("INSERT INTO meta(key, value) VALUES (?, ?)", ("validation:w", record))
            connection.commit()
            report = self.relocation().run(dry_run=True)
            self.assertEqual(report["recordColumnsKept"], {"meta.value (validation:*)": 1})
            self.assertEqual(report["refusedDatabaseColumns"], {})
            connection.execute("INSERT INTO meta(key, value) VALUES (?, ?)", ("other", f"{self.old.state}/x".encode()))
            connection.commit()
        finally:
            connection.close()
        self.assertEqual(self.relocation().run(dry_run=True)["refusedDatabaseColumns"], {"meta.value": 1})

    def test_a_corrupt_database_or_record_is_refused_by_name(self) -> None:
        # Review of 796cb02: both escaped as tracebacks.
        from worldline.relocate import main
        arguments = ["--from-data", str(self.old.data), "--from-state", str(self.old.state),
                     "--to-data", str(self.new.data), "--to-state", str(self.new.state)]
        record = next(iter(sorted((self.new.state / "transactions").glob("*.json"))))
        saved = record.read_bytes()
        record.write_bytes(b"not json " + os.fsencode(self.old.data))
        self.assertEqual(main([*arguments, "--dry-run"]), 1)
        record.write_bytes(saved)
        (self.new.state / "worldline.sqlite3").write_bytes(b"this is not a database" * 100)
        self.assertEqual(main([*arguments, "--dry-run"]), 1)

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


class RelocationMountRoots(unittest.TestCase):
    def test_a_whole_btrfs_subvolume_is_not_a_bind(self) -> None:
        # Review of f50bbb1: a root filesystem that is a btrfs subvolume records `/@` as its mount
        # root, and the hidden-old-store rule read every such system as bound.
        from worldline.relocate import _bind_of_a_directory, _mount_table
        line = "29 1 0:26 {root} / rw,relatime shared:1 - btrfs /dev/vda2 rw,ssd,space_cache=v2,subvolid=256,subvol={subvol}\n"
        # Review of 0fa069c: both fields are escaped as the kernel escapes paths (a space is \\040).
        cases = {("/", "/"): False, ("/@", "/@"): False, ("/@/var/lib", "/@"): True,
                 ("/my\\040vol", "/my\\040vol"): False}
        with tempfile.TemporaryDirectory(prefix="worldline-mountinfo-") as temporary:
            for (root, subvol), bound in cases.items():
                with self.subTest(root=root, subvol=subvol):
                    table = Path(temporary) / "mountinfo"
                    table.write_text(line.format(root=root, subvol=subvol))
                    (entry,) = _mount_table(str(table))
                    self.assertIn(f"subvol={subvol}", entry["super"])   # as the kernel wrote it
                    self.assertEqual(_bind_of_a_directory(entry), bound)
        ext4 = {"root": "/var/lib/other", "fstype": "ext4", "super": ["rw"]}
        self.assertTrue(_bind_of_a_directory(ext4))


class RelocationViewsThroughSymlinks(unittest.TestCase):
    def test_a_view_of_an_old_store_named_through_a_symlink_is_refused(self) -> None:
        # Review of 300543c: the old store is recorded by the path its daemon was given, and the
        # mount-table check looked that path up lexically; under a symlinked home (/home ->
        # var/home) it found the wrong mount, and a bind of the old data at the copy's path was
        # relocated in place, rewriting the old store.
        from worldline.store import StateStore
        bwrap = shutil.which("bwrap")
        if bwrap is None:
            self.skipTest("bwrap is required to make a mount without privileges")
        with tempfile.TemporaryDirectory(prefix="worldline-view-symlinked-") as temporary:
            base = Path(temporary)
            (base / "hidden").mkdir()
            (base / "link").symlink_to("hidden")
            old = base / "link" / "old"
            paths = WorldlinePaths(home=base / "home", data=old / "data", state=old / "state",
                                   runtime=base / "runtime", config=base / "config")
            StateStore(paths).close()
            content = old / "data" / "generations" / "g1" / "payload" / "rk1"
            (content / "sub").mkdir(parents=True)
            (content / "f.txt").write_text("prime content\n")
            (old / "data" / "live" / "rk1").symlink_to(content, target_is_directory=True)
            new = base / "new"
            new.mkdir()
            shutil.copytree(old / "state", new / "state", symlinks=True)
            (new / "data").mkdir()
            mapping = base / "hidden" / "old" / "data" / "live" / "rk1"
            before = os.readlink(mapping)
            code = ("import os, sys; os.chmod(sys.argv[1], 0); "
                    "from worldline.relocate import main; code = main(sys.argv[2:]); "
                    "os.chmod(sys.argv[1], 0o755); sys.exit(code)")
            arguments = ["--from-data", str(old / "data"), "--from-state", str(old / "state"),
                         "--to-data", str(new / "data"), "--to-state", str(new / "state")]
            try:
                result = subprocess.run(
                    [bwrap, "--dev-bind", "/", "/", "--bind", str(base / "hidden" / "old" / "data"), str(new / "data"),
                     "--", sys.executable, "-B", "-c", code, str(base / "hidden"), *arguments],
                    env={**os.environ, "PYTHONPATH": str(REPO / "runtime"), "PYTHONDONTWRITEBYTECODE": "1"},
                    capture_output=True, timeout=120)
            finally:
                os.chmod(base / "hidden", 0o755)
            self.assertEqual(result.returncode, 1, result.stderr.decode(errors="replace")[-2000:])
            self.assertIn(b"seen through a mount", result.stderr)
            self.assertEqual(os.readlink(mapping), before)

    def test_a_bound_copy_is_refused_when_a_hidden_link_names_the_old_store(self) -> None:
        # Review of 8ff1903: with the link inside a directory the relocating account cannot search
        # (the operator's 0700 home, `~/.local/share` on another disk), the old store could not be
        # located, and a bind of it at the copy's path was relocated in place.
        from worldline.store import StateStore
        bwrap = shutil.which("bwrap")
        if bwrap is None:
            self.skipTest("bwrap is required to make a mount without privileges")
        with tempfile.TemporaryDirectory(prefix="worldline-view-hidden-link-") as temporary:
            base = Path(temporary)
            (base / "opshome").mkdir()
            (base / "otherdisk").mkdir()
            (base / "opshome" / "share").symlink_to(base / "otherdisk")
            old = base / "opshome" / "share" / "old"
            paths = WorldlinePaths(home=base / "home", data=old / "data", state=old / "state",
                                   runtime=base / "runtime", config=base / "config")
            StateStore(paths).close()
            content = old / "data" / "generations" / "g1" / "payload" / "rk1"
            (content / "sub").mkdir(parents=True)
            (content / "f.txt").write_text("prime content\n")
            (old / "data" / "live" / "rk1").symlink_to(content, target_is_directory=True)
            new = base / "new"
            new.mkdir()
            shutil.copytree(old / "state", new / "state", symlinks=True)
            (new / "data").mkdir()
            mapping = base / "otherdisk" / "old" / "data" / "live" / "rk1"
            before = os.readlink(mapping)
            code = ("import os, sys; os.chmod(sys.argv[1], 0); "
                    "from worldline.relocate import main; code = main(sys.argv[2:]); "
                    "os.chmod(sys.argv[1], 0o755); sys.exit(code)")
            arguments = ["--from-data", str(old / "data"), "--from-state", str(old / "state"),
                         "--to-data", str(new / "data"), "--to-state", str(new / "state")]
            try:
                result = subprocess.run(
                    [bwrap, "--dev-bind", "/", "/", "--bind", str(base / "otherdisk" / "old" / "data"), str(new / "data"),
                     "--", sys.executable, "-B", "-c", code, str(base / "opshome"), *arguments],
                    env={**os.environ, "PYTHONPATH": str(REPO / "runtime"), "PYTHONDONTWRITEBYTECODE": "1"},
                    capture_output=True, timeout=120)
            finally:
                os.chmod(base / "opshome", 0o755)
            self.assertEqual(result.returncode, 1, result.stderr.decode(errors="replace")[-2000:])
            self.assertIn(b"cannot resolve the old store", result.stderr)
            self.assertEqual(os.readlink(mapping), before)


    def test_a_moved_store_can_be_relocated_from_a_bind(self) -> None:
        # Review of 0fa069c: counting a missing old path as unresolvable refused the copy of a store
        # that was moved rather than copied, when the copy sits on a bind (ostree's /var).
        from worldline.store import StateStore
        bwrap = shutil.which("bwrap")
        if bwrap is None:
            self.skipTest("bwrap is required to make a mount without privileges")
        with tempfile.TemporaryDirectory(prefix="worldline-moved-store-") as temporary:
            base = Path(temporary)
            old = base / "old"
            paths = WorldlinePaths(home=base / "home", data=old / "data", state=old / "state",
                                   runtime=base / "runtime", config=base / "config")
            StateStore(paths).close()
            content = old / "data" / "generations" / "g1" / "payload" / "rk1"
            (content / "sub").mkdir(parents=True)
            (content / "f.txt").write_text("prime content\n")
            (old / "data" / "live" / "rk1").symlink_to(content, target_is_directory=True)
            (base / "vol").mkdir()
            os.rename(old, base / "vol" / "store")      # moved, not copied: the old path is gone
            (base / "mnt").mkdir()
            code = "import sys; from worldline.relocate import main; sys.exit(main(sys.argv[1:]))"
            arguments = ["--from-data", str(old / "data"), "--from-state", str(old / "state"),
                         "--to-data", str(base / "mnt" / "store" / "data"),
                         "--to-state", str(base / "mnt" / "store" / "state"), "--dry-run"]
            result = subprocess.run(
                [bwrap, "--dev-bind", "/", "/", "--bind", str(base / "vol"), str(base / "mnt"),
                 "--", sys.executable, "-B", "-c", code, *arguments],
                env={**os.environ, "PYTHONPATH": str(REPO / "runtime"), "PYTHONDONTWRITEBYTECODE": "1"},
                capture_output=True, timeout=120)
            self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace")[-2000:])
            self.assertIn(b"DRY_RUN", result.stdout)


if __name__ == "__main__":
    unittest.main()
