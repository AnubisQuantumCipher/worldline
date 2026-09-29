"""A managed root's content is resolved through the store's own live mapping, never the operator's link.

The registered path (`~/Projects/x`) is a symlink in a directory its operator owns. Under a
dedicated-account daemon that operator is a client, so a client that re-points the link must
not choose what the daemon captures as PRIME, loads policy from, reads for `why`, or keeps
when pruning. The link must still route through the live mapping, or the root is refused.

In client mode the directories between the store and PRIME's content are 0710 with the client
group, so a client can read PRIME through the symlink chain and list or write nothing.
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import stat
import tempfile
import unittest
from unittest import mock

from worldline.causal import CausalIndexer
from worldline.core import Core
from worldline.errors import NotFound, WorldlineError
from worldline.paths import WorldlinePaths
from worldline.prune import Pruner
from worldline.roots import RootManager
from worldline.store import StateStore


# A supplementary group: files are not created with it, so a missing group change fails.
SUPPLEMENTARY_GID = next((gid for gid in os.getgroups() if gid != os.getgid()), None)


def environment(root: Path, **extra: str) -> dict[str, str]:
    env = {
        "HOME": str(root / "home"),
        "XDG_DATA_HOME": str(root / "data"),
        "XDG_STATE_HOME": str(root / "state"),
        "XDG_CONFIG_HOME": str(root / "config"),
        "XDG_RUNTIME_DIR": str(root / "runtime"),
        **extra,
    }
    for name in ("HOME", "XDG_DATA_HOME", "XDG_STATE_HOME", "XDG_CONFIG_HOME", "XDG_RUNTIME_DIR"):
        Path(env[name]).mkdir(mode=0o700, parents=True, exist_ok=True)
    return env


class _Registered(unittest.TestCase):
    client_mode = False

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-root-resolution-")
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        extra = ({"WORLDLINE_CLIENT_GID": str(SUPPLEMENTARY_GID), "WORLDLINE_CLIENT_UIDS": str(os.getuid() + 4242)}
                 if self.client_mode else {})
        self.paths = WorldlinePaths.from_environment(environment(root, **extra))
        self.store = StateStore(self.paths, Core.shared())
        self.addCleanup(self.store.close)
        self.manager = RootManager(self.paths, self.store, core=Core.shared(), toolchains=())
        self.work = root / "work"
        self.work.mkdir()
        (self.work / "state.txt").write_bytes(b"prime bytes\n")
        self.work_mode = stat.S_IMODE(self.work.stat().st_mode)
        self.manager.register([self.work], confirmed=True)
        self.root = self.store.roots()[0]
        self.prime = self.store.prime().content_id
        # The client's own directory, which it would like the daemon to adopt as PRIME.
        self.elsewhere = root / "elsewhere"
        self.elsewhere.mkdir()
        (self.elsewhere / "state.txt").write_bytes(b"not reviewed\n")

    def repoint(self, target: Path) -> None:
        self.work.unlink()
        self.work.symlink_to(target)


class RootSourceTests(_Registered):
    def test_intact_routing_resolves_to_the_store_payload(self) -> None:
        source = self.paths.root_source(self.root)
        store = os.path.realpath(os.fsencode(self.paths.data))
        self.assertTrue(source.startswith(store + b"/"))
        self.assertEqual(Path(os.fsdecode(source), "state.txt").read_bytes(), b"prime bytes\n")

    def test_a_repointed_link_is_refused_and_prime_is_not_recaptured(self) -> None:
        self.repoint(self.elsewhere)
        self.store.set_meta("dirty", True)  # what the watcher records for an external change
        with self.assertRaises(WorldlineError) as caught:
            self.manager.reconcile()
        self.assertEqual(caught.exception.code, "LIVE_MAPPING_BROKEN")
        self.assertEqual(self.store.prime().content_id, self.prime)

    def test_a_link_straight_to_the_payload_is_still_not_the_live_mapping(self) -> None:
        # Resolves to the same bytes today, but does not follow the next collapse.
        self.repoint(Path(os.fsdecode(self.paths.root_source(self.root))))
        with self.assertRaises(WorldlineError) as caught:
            self.paths.root_source(self.root)
        self.assertEqual(caught.exception.code, "LIVE_MAPPING_BROKEN")

    def test_equivalent_spellings_of_the_live_entry_still_route(self) -> None:
        live = self.paths.live / self.root["root_key"]
        linked_home = Path(self.temporary.name) / "home-link"
        linked_home.symlink_to(self.paths.data.parent)
        spellings = (
            f"{live}/",                                                    # trailing slash
            str(self.paths.data) + "//live/" + self.root["root_key"],      # doubled slash
            str(linked_home / "worldline" / "live" / self.root["root_key"]),  # through a link
            os.path.relpath(live, self.work.parent),                       # relative
        )
        for spelling in spellings:
            with self.subTest(spelling=spelling):
                self.repoint(Path(spelling))
                self.assertEqual(self.paths.root_source(self.root), os.path.realpath(os.fsencode(live)))

    def test_a_real_directory_at_the_registered_path_is_refused(self) -> None:
        # What an interrupted `root remove` leaves; the doctor already calls it BROKEN.
        self.work.unlink()
        self.work.mkdir()
        (self.work / "state.txt").write_bytes(b"diverged\n")
        with self.assertRaises(WorldlineError) as caught:
            self.manager.capture_current()
        self.assertEqual(caught.exception.code, "LIVE_MAPPING_BROKEN")

    def test_a_live_mapping_that_leaves_the_store_is_refused(self) -> None:
        live = self.paths.live / self.root["root_key"]
        live.unlink()
        live.symlink_to(self.elsewhere)
        with self.assertRaises(WorldlineError) as caught:
            self.paths.root_source(self.root)
        self.assertEqual(caught.exception.code, "LIVE_MAPPING_BROKEN")

    def test_prune_refuses_rather_than_forget_which_payload_is_live(self) -> None:
        self.repoint(self.elsewhere)
        with self.assertRaises(WorldlineError) as caught:
            Pruner(self.paths, self.store).plan(older_than_days=None, keep=None, logs=False)
        self.assertEqual(caught.exception.code, "LIVE_MAPPING_BROKEN")

    def test_a_root_the_sandbox_cannot_inspect_is_reported_and_still_removable(self) -> None:
        # A repository root registered before 1.7.x whose `.git` became a file (a linked worktree):
        # captures refuse it by name, the doctor must say so, and `root remove` must still work.
        import subprocess
        repo = Path(self.temporary.name) / "repo-root"
        repo.mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
        (repo / "f.txt").write_text("x\n")
        subprocess.run(["git", "-C", str(repo), "add", "f.txt"], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(repo), "-c", "user.email=a@b.c", "-c", "user.name=a",
                        "commit", "-qm", "init"], check=True, capture_output=True)
        self.manager.register([repo], confirmed=True)
        root = next(item for item in self.store.roots() if bytes(item["path"]) == os.fsencode(repo))
        source = Path(os.fsdecode(self.paths.root_source(root)))
        (source / ".git").rename(source / "moved-git")
        (source / ".git").write_text(f"gitdir: {source / 'moved-git'}\n")
        from worldline.controller import RuntimeController
        report = RuntimeController._root_integrity(mock.Mock(store=self.store, paths=self.paths))
        entry = next(item for item in report["roots"] if item["rootKey"] == root["root_key"])
        self.assertEqual(entry["state"], "BROKEN")
        self.assertIn("GIT_LINKED_WORKTREE_UNSUPPORTED", entry["reason"])
        self.manager.remove(root["root_key"], confirmed=True)
        self.assertTrue((repo / "f.txt").is_file())

    def test_a_real_directory_in_live_is_not_a_mapping(self) -> None:
        # Review of 796cb02: a copy that dereferenced links turned the mapping into a directory,
        # which the start check skipped and root_source served.
        live = self.paths.live / self.root["root_key"]
        content = Path(os.path.realpath(live))
        live.unlink()
        shutil.copytree(content, live)
        with self.assertRaises(WorldlineError) as caught:
            self.paths.root_source(self.root)
        self.assertEqual(caught.exception.code, "LIVE_MAPPING_BROKEN")

    def test_a_refused_capture_leaves_no_copy_behind(self) -> None:
        # Review of 796cb02: every refused reconcile left a full copy of the roots before it.
        before = sorted(item.name for item in self.paths.generations.iterdir())
        source = Path(os.fsdecode(self.paths.root_source(self.root)))
        os.mkfifo(source / "fifo")
        self.store.set_meta("dirty", True)
        for _attempt in range(3):
            with self.assertRaises(WorldlineError) as caught:
                self.manager.reconcile()
            self.assertEqual(caught.exception.code, "UNSUPPORTED_SPECIAL_FILE")
        self.assertEqual(sorted(item.name for item in self.paths.generations.iterdir()), before)

    def test_a_root_whose_git_is_a_link_outside_it_can_still_be_removed(self) -> None:
        # Review of 796cb02: the doctor called it BROKEN and said remove it; remove refused
        # EXTERNAL_SYMLINK on the `.git` link.
        import subprocess
        repo = Path(self.temporary.name) / "linked-repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
        (repo / "f.txt").write_text("x\n")
        self.manager.register([repo], confirmed=True)
        root = next(item for item in self.store.roots() if bytes(item["path"]) == os.fsencode(repo))
        source = Path(os.fsdecode(self.paths.root_source(root)))
        elsewhere = Path(self.temporary.name) / "elsewhere.git"
        (source / ".git").rename(elsewhere)
        (source / ".git").symlink_to(elsewhere)
        self.manager.remove(root["root_key"], confirmed=True)
        self.assertTrue(repo.is_dir() and not repo.is_symlink())
        self.assertEqual((repo / ".git").readlink(), elsewhere)
        self.assertEqual((repo / "f.txt").read_text(), "x\n")

    def _repository_root(self, name: str) -> tuple[Path, dict]:
        import subprocess
        repo = Path(self.temporary.name) / name
        repo.mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
        (repo / "f.txt").write_text("x\n")
        subprocess.run(["git", "-C", str(repo), "add", "f.txt"], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(repo), "-c", "user.email=a@b.c", "-c", "user.name=a",
                        "commit", "-qm", "init"], check=True, capture_output=True)
        self.manager.register([repo], confirmed=True)
        root = next(item for item in self.store.roots() if bytes(item["path"]) == os.fsencode(repo))
        return repo, root

    def _break_repository(self, root: dict) -> None:
        source = Path(os.fsdecode(self.paths.root_source(root)))
        with open(source / ".git" / "config", "a", encoding="utf-8") as stream:
            stream.write("[core\n")   # git refuses the whole repository: bad config line

    def test_a_root_whose_repository_git_refuses_can_still_be_removed(self) -> None:
        # Review of 300543c: its own repository facts are never published again, yet a git refusal
        # of them refused its removal.
        repo, root = self._repository_root("bad-config")
        self._break_repository(root)
        self.manager.remove(root["root_key"], confirmed=True)
        self.assertTrue(repo.is_dir() and not repo.is_symlink())
        self.assertEqual((repo / "f.txt").read_text(), "x\n")

    def test_a_remaining_root_git_refuses_is_named_by_its_path(self) -> None:
        # Review of 300543c: the refusal named the store's payload path, not the root to repair.
        _repo, other = self._repository_root("bad-other")
        self._break_repository(other)
        with self.assertRaises(WorldlineError) as caught:
            self.manager.remove(self.root["root_key"], confirmed=True)
        self.assertEqual(caught.exception.code, "GIT_INSPECTION_FAILED")
        self.assertEqual(caught.exception.details["root"], other["display_path"])
        self.assertTrue(self.work.is_symlink())

    def test_a_refused_publish_leaves_no_copy_behind(self) -> None:
        # Review of 300543c: status reconciles while the store is dirty, and each reconcile whose
        # publication refused kept a full copy of every root.
        before = sorted(item.name for item in self.paths.generations.iterdir())
        self.store.set_meta("dirty", True)
        with mock.patch.object(self.manager.environment, "capture", side_effect=RuntimeError("refused late")):
            for _attempt in range(2):
                with self.assertRaises(RuntimeError):
                    self.manager.reconcile()
        self.assertEqual(sorted(item.name for item in self.paths.generations.iterdir()), before)

    def test_a_dependency_file_nested_too_deep_is_recorded_not_raised(self) -> None:
        # Review of 300543c: the parser's RecursionError escaped every capture of the store.
        source = Path(os.fsdecode(self.paths.root_source(self.root)))
        (source / "package.json").write_text('{"dependencies": ' + "[" * 100000 + "]" * 100000 + "}")
        self.store.set_meta("dirty", True)
        world = self.manager.reconcile()
        self.assertNotEqual(world.content_id, self.prime)

    def test_declared_dependencies_that_cannot_be_recorded_are_unavailable(self) -> None:
        # Review of 8ff1903: a float refused every capture NON_CANONICAL_JSON, and one nested past the
        # canonicaliser's recursion raised a bare RecursionError out of reconcile and removal.
        source = Path(os.fsdecode(self.paths.root_source(self.root)))
        for text in ('{"dependencies": {"x": 1.5}}',
                     '{"dependencies": {"x": ' + "[" * 3000 + "]" * 3000 + "}}"):
            with self.subTest(text=text[:40]):
                (source / "package.json").write_text(text)
                self.store.set_meta("dirty", True)
                world = self.manager.reconcile()
                self.assertEqual(self.store.prime().content_id, world.content_id)

    def test_a_remaining_root_refused_for_its_own_files_is_named_in_the_message(self) -> None:
        # Review of 8ff1903: a FIFO or outside hard link in another root refused a removal with a
        # message that named neither that root nor anything the operator could find.
        other = self._second_root("fifo-root")
        os.mkfifo(Path(os.fsdecode(self.paths.root_source(other))) / "fifo")
        with self.assertRaises(WorldlineError) as caught:
            self.manager.remove(self.root["root_key"], confirmed=True)
        self.assertEqual(caught.exception.code, "UNSUPPORTED_SPECIAL_FILE")
        self.assertTrue(caught.exception.message.startswith(other["display_path"] + ": "), caught.exception.message)
        self.assertEqual(caught.exception.details["root"], other["display_path"])

    def test_a_failure_that_is_not_a_refusal_still_reports_the_kept_copy(self) -> None:
        # Review of 8ff1903: a disk-full OSError after the swap kept what was written at the path,
        # but said so only in the daemon's log.
        def write_then_fail(root_key):
            (self.work / "written-meanwhile.txt").write_text("keep me\n")
            raise OSError(28, "No space left on device")

        with mock.patch.object(self.store, "remove_root", side_effect=write_then_fail):
            with self.assertRaises(WorldlineError) as caught:
                self.manager.remove(self.root["root_key"], confirmed=True)
        self.assertEqual(caught.exception.code, "ROOT_REMOVAL_ROLLED_BACK")
        kept = Path(caught.exception.details["keptAt"])
        self.assertEqual((kept / "written-meanwhile.txt").read_text(), "keep me\n")
        self.assertIn(str(kept), caught.exception.message)
        self.assertTrue(self.work.is_symlink())

    def test_a_removal_whose_publication_failed_after_recording_keeps_that_payload(self) -> None:
        # Review of f50bbb1: only reconcile kept a payload a recorded world names; removal still
        # deleted it when PRIME could not be moved (a full disk).
        import sqlite3
        other = self._second_root("stays")
        before = {world.instance_id for world in self.store.worlds()}
        with mock.patch.object(self.store, "set_prime", side_effect=sqlite3.OperationalError("database or disk is full")):
            with self.assertRaises(sqlite3.OperationalError):
                self.manager.remove(self.root["root_key"], confirmed=True)
        recorded = [world for world in self.store.worlds() if world.instance_id not in before]
        self.assertEqual(len(recorded), 1)
        self.assertTrue(Path(recorded[0].payload_path).is_dir())
        self.assertIn(other["root_key"], {item["root_key"] for item in self.store.roots()})

    def test_a_kept_copy_under_a_name_that_is_not_utf8_can_be_reported(self) -> None:
        # Review of f50bbb1: the kept path went into the reply undecoded and could not be sent.
        import json
        parent = Path(os.fsdecode(os.fsencode(self.temporary.name) + b"/odd-\xff"))
        parent.mkdir()
        odd = parent / "root"
        odd.mkdir()
        (odd / "state.txt").write_text("odd\n")
        self.manager.register([odd], confirmed=True)
        root = next(item for item in self.store.roots() if bytes(item["path"]) == os.fsencode(odd))

        def write_then_fail(root_key):
            (odd / "written-meanwhile.txt").write_text("keep me\n")
            raise OSError(28, "No space left on device")

        with mock.patch.object(self.store, "remove_root", side_effect=write_then_fail):
            with self.assertRaises(WorldlineError) as caught:
                self.manager.remove(root["root_key"], confirmed=True)
        json.dumps(caught.exception.as_dict(), ensure_ascii=False).encode("utf-8")
        self.assertIn("\\xff", caught.exception.details["keptAt"])

    def test_the_removed_root_needs_no_repository_sandbox(self) -> None:
        # Review of 8ff1903: a missing bwrap, prlimit or choom still refused removing a repository
        # root, whose facts removal never uses.
        repo, root = self._repository_root("no-sandbox")
        with mock.patch.object(self.manager.git, "capture",
                               side_effect=WorldlineError("BUBBLEWRAP_UNAVAILABLE", "bwrap is not installed")):
            self.manager.remove(root["root_key"], confirmed=True)
        self.assertTrue(repo.is_dir() and not repo.is_symlink())

    def test_a_publish_that_failed_after_recording_its_world_keeps_that_payload(self) -> None:
        # Review of 8ff1903: publication records the world before it moves PRIME; a failure in
        # between (a full disk) had the reconcile discard delete the payload the world names.
        import sqlite3
        source = Path(os.fsdecode(self.paths.root_source(self.root)))
        (source / "state.txt").write_bytes(b"changed\n")
        self.store.set_meta("dirty", True)
        before = {world.instance_id for world in self.store.worlds()}
        with mock.patch.object(self.store, "set_prime", side_effect=sqlite3.OperationalError("database or disk is full")):
            with self.assertRaises(sqlite3.OperationalError):
                self.manager.reconcile()
        recorded = [world for world in self.store.worlds() if world.instance_id not in before]
        self.assertEqual(len(recorded), 1)
        self.assertTrue(Path(recorded[0].payload_path).is_dir())

    def _second_root(self, name: str) -> dict:
        other = Path(self.temporary.name) / name
        other.mkdir()
        (other / "state.txt").write_text(name + "\n")
        self.manager.register([other], confirmed=True)
        return next(item for item in self.store.roots() if bytes(item["path"]) == os.fsencode(other))

    def test_a_removal_the_remaining_roots_refuse_changes_nothing(self) -> None:
        # Review of 09f5c0b: another root's capture refusing after the operator's path had been
        # swapped left the primary root half-removed (ROOT_CONFLICT on the rollback's re-add).
        other = self._second_root("other")
        self.store.set_primary_root(self.root["root_key"])
        fifo = Path(os.fsdecode(self.paths.root_source(other))) / "fifo"
        os.mkfifo(fifo)
        with self.assertRaises(WorldlineError) as caught:
            self.manager.remove(self.root["root_key"], confirmed=True)
        self.assertEqual(caught.exception.code, "UNSUPPORTED_SPECIAL_FILE")
        roots = {item["root_key"]: item for item in self.store.roots()}
        self.assertIn(self.root["root_key"], roots)
        self.assertTrue(roots[self.root["root_key"]]["primary_root"])
        self.assertTrue(self.work.is_symlink())
        self.assertEqual(sorted(p.name for p in self.work.parent.iterdir() if p.name.startswith(".worldline-materialize-")), [])
        fifo.unlink()
        self.manager.remove(self.root["root_key"], confirmed=True)
        self.assertFalse(self.work.is_symlink())
        self.assertEqual((self.work / "state.txt").read_bytes(), b"prime bytes\n")

    def test_a_root_written_to_during_removal_is_not_dropped(self) -> None:
        # Review of c7d89f1: a file written into the root after its capture was lost.
        from worldline.manifest import Manifest
        real = Manifest.materialize
        source = Path(os.fsdecode(self.paths.root_source(self.root)))

        def and_meanwhile(*args, **kwargs):
            result = real(*args, **kwargs)
            (source / "late.txt").write_text("written during the removal\n")
            return result

        with mock.patch("worldline.roots.Manifest.materialize", side_effect=and_meanwhile):
            with self.assertRaises(WorldlineError) as caught:
                self.manager.remove(self.root["root_key"], confirmed=True)
        self.assertEqual(caught.exception.code, "ROOT_CHANGED_DURING_REMOVAL")
        self.assertTrue(self.work.is_symlink())
        self.assertEqual((self.work / "late.txt").read_text(), "written during the removal\n")

    def test_a_rollback_keeps_what_was_written_at_the_path_meanwhile(self) -> None:
        # Review of c7d89f1: the rollback deleted the copy that stood at the operator's path,
        # with anything an editor had written into it.
        other = self._second_root("other-kept")
        real = self.manager._publish_generation

        def written_then_refused(**kwargs):
            (self.work / "edited.txt").write_text("an editor saved this\n")
            raise WorldlineError("SIMULATED", "publication refused after the swap")

        with mock.patch.object(self.manager, "_publish_generation", side_effect=written_then_refused):
            with self.assertRaises(WorldlineError):
                self.manager.remove(self.root["root_key"], confirmed=True)
        self.assertTrue(self.work.is_symlink())
        kept = [p for p in self.work.parent.iterdir() if p.name.startswith(".worldline-removal-kept-")]
        self.assertEqual(len(kept), 1)
        self.assertEqual((kept[0] / "edited.txt").read_text(), "an editor saved this\n")
        self.assertIn(other["root_key"], {item["root_key"] for item in self.store.roots()})

    def test_a_remaining_repository_refused_for_its_content_still_refuses(self) -> None:
        # Review of c7d89f1: removal tolerated NOT_A_GIT_ROOT from content (core.bare) in another
        # root and published it without its facts.
        import subprocess
        repo = Path(self.temporary.name) / "bare-flagged"
        repo.mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
        (repo / "f.txt").write_text("x\n")
        self.manager.register([repo], confirmed=True)
        root = next(item for item in self.store.roots() if bytes(item["path"]) == os.fsencode(repo))
        source = Path(os.fsdecode(self.paths.root_source(root)))
        subprocess.run(["git", "-C", str(source), "config", "core.bare", "true"], check=True, capture_output=True)
        with self.assertRaises(WorldlineError) as caught:
            self.manager.remove(self.root["root_key"], confirmed=True)
        self.assertEqual(caught.exception.code, "NOT_A_GIT_ROOT")
        self.assertTrue(self.work.is_symlink())

    def test_two_roots_the_sandbox_cannot_inspect_can_both_be_removed(self) -> None:
        # Review of 09f5c0b: each removal was refused by the other root's capture.
        import subprocess
        repos = []
        for name in ("first-linked", "second-linked"):
            repo = Path(self.temporary.name) / name
            repo.mkdir()
            subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
            (repo / "f.txt").write_text(name + "\n")
            repos.append(repo)
        self.manager.register(repos, confirmed=True)   # registered while their layout was supported
        linked = []
        for repo in repos:
            root = next(item for item in self.store.roots() if bytes(item["path"]) == os.fsencode(repo))
            source = Path(os.fsdecode(self.paths.root_source(root)))
            elsewhere = Path(self.temporary.name) / f"{repo.name}.git"
            (source / ".git").rename(elsewhere)
            (source / ".git").symlink_to(elsewhere)
            linked.append((repo, root, elsewhere))
        for repo, root, elsewhere in linked:
            self.manager.remove(root["root_key"], confirmed=True)
            self.assertTrue(repo.is_dir() and not repo.is_symlink())
            self.assertEqual((repo / ".git").readlink(), elsewhere)

    def test_why_does_not_leave_the_root(self) -> None:
        outside = Path(self.temporary.name) / "secret.txt"
        outside.write_bytes(b"daemon-only line\n")
        climbing = f"{self.work}/../secret.txt"
        with self.assertRaises(NotFound):
            CausalIndexer(self.store).why(climbing, 1)


class StatusReportsAnyRecaptureFailure(unittest.TestCase):
    def test_an_unexpected_recapture_failure_degrades_status_instead_of_failing_it(self) -> None:
        # Review of 8ff1903: status caught only refusals, so any other failure of the re-capture
        # answered INTERNAL_ERROR on every request while the store stayed dirty.
        from worldline.daemon import WorldlineDaemon
        meta = {"dirty": True}
        store = mock.Mock()
        store.get_meta.side_effect = lambda key, default=None: meta.get(key, default)
        store.set_meta.side_effect = lambda key, value: meta.__setitem__(key, value)
        daemon = mock.Mock(store=store, _reconcile_status=mock.Mock(side_effect=RecursionError("too deep")))
        daemon.publisher.publish.return_value = {"published": True}
        self.assertEqual(WorldlineDaemon._status(daemon, {}, None), {"published": True})
        self.assertEqual(meta["watchState"], "DEGRADED")
        self.assertEqual(meta["watchError"]["code"], "RECAPTURE_FAILED")
        self.assertIn("RecursionError", meta["watchError"]["message"])

    def test_a_storage_failure_of_the_recapture_keeps_its_name(self) -> None:
        # Review of f50bbb1: a full disk had been answered DISK_FULL with its errno, and the
        # catch-all renamed it RECAPTURE_FAILED; review of 0fa069c: failing the request instead
        # left status unreadable while the store stayed dirty. It is recorded by its own name.
        from worldline.daemon import WorldlineDaemon
        for error, code in ((OSError(28, "No space left on device"), "DISK_FULL"),
                            (PermissionError(13, "Permission denied", "/store/x"), "STORAGE_ERROR")):
            with self.subTest(code=code):
                meta = {"dirty": True}
                store = mock.Mock()
                store.get_meta.side_effect = lambda key, default=None: meta.get(key, default)
                store.set_meta.side_effect = lambda key, value: meta.__setitem__(key, value)
                daemon = mock.Mock(store=store, _reconcile_status=mock.Mock(side_effect=error))
                daemon.publisher.publish.return_value = {"published": True}
                self.assertEqual(WorldlineDaemon._status(daemon, {}, None), {"published": True})
                self.assertEqual(meta["watchState"], "DEGRADED")
                self.assertEqual(meta["watchError"]["code"], code)


@unittest.skipIf(SUPPLEMENTARY_GID is None, "needs a supplementary group")
class ClientModePrimeChainTests(_Registered):
    client_mode = True

    def _mode_and_group(self, path: Path) -> tuple[int, int]:
        info = path.lstat()
        return stat.S_IMODE(info.st_mode), info.st_gid

    def test_the_data_directory_is_a_gate_opened_only_after_the_check(self) -> None:
        self.assertEqual(stat.S_IMODE(self.paths.data.stat().st_mode), 0o700)   # created closed
        self.paths.share_live_chain()
        self.assertEqual(self._mode_and_group(self.paths.data), (0o710, SUPPLEMENTARY_GID))
        self.paths.ensure()                                                       # leaves it open
        self.assertEqual(self._mode_and_group(self.paths.data)[0], 0o710)
        self.paths.close_client_gate()
        self.assertEqual(stat.S_IMODE(self.paths.data.stat().st_mode), 0o700)
        self.paths.ensure()                                                       # leaves it closed
        self.assertEqual(stat.S_IMODE(self.paths.data.stat().st_mode), 0o700)

    def test_unsafe_live_content_found_while_running_closes_the_gate(self) -> None:
        self.paths.share_live_chain()
        content = Path(os.fsdecode(self.paths.root_source(self.root)))
        os.chmod(content, 0o777)
        self.store.set_meta("dirty", True)
        generations = sorted(p.name for p in self.paths.generations.iterdir())
        with self.assertRaises(WorldlineError) as caught:
            self.manager.reconcile()
        self.assertEqual(caught.exception.code, "CLIENT_MODE_UNSAFE_CONTENT")
        self.assertEqual(stat.S_IMODE(self.paths.data.stat().st_mode), 0o700)
        # The refused copy is not kept (review of ad64cd2: each refusal left a full copy behind).
        self.assertEqual(sorted(p.name for p in self.paths.generations.iterdir()), generations)

    def test_the_chain_to_prime_is_traverse_only_for_the_client_group(self) -> None:
        self.paths.share_live_chain()  # what daemon start does
        source = Path(os.fsdecode(self.paths.root_source(self.root)))
        chain = [self.paths.data, self.paths.live]
        current = Path(os.path.realpath(self.paths.data))
        for part in source.relative_to(current).parts[:-1]:
            current = current / part
            chain.append(current)
        self.assertIn(self.paths.generations, [Path(p) for p in chain])
        for directory in chain:
            with self.subTest(directory=str(directory)):
                self.assertEqual(self._mode_and_group(directory), (0o710, SUPPLEMENTARY_GID))
        # The root's own directory keeps the mode its manifest records; manifests stay private.
        self.assertEqual(stat.S_IMODE(source.stat().st_mode), self.work_mode)
        self.assertEqual(stat.S_IMODE((source.parent / "manifests").stat().st_mode), 0o700)
        for private in (self.paths.state, self.paths.worlds, self.paths.overlays, self.paths.config):
            with self.subTest(private=str(private)):
                self.assertEqual(stat.S_IMODE(private.stat().st_mode), 0o700)

    def test_anything_in_live_but_mapping_links_refuses_the_start(self) -> None:
        live = self.paths.live / self.root["root_key"]
        content = Path(os.path.realpath(live))
        live.unlink()
        shutil.copytree(content, live)
        with self.assertRaises(WorldlineError) as caught:
            self.paths.share_live_chain()
        self.assertEqual(caught.exception.code, "LIVE_MAPPING_BROKEN")
        self.assertEqual(stat.S_IMODE(self.paths.data.stat().st_mode), 0o700)   # the gate stays shut

    def test_a_mapping_must_name_a_payload(self) -> None:
        # Review of 4490013: the start check accepted any directory inside the store as a
        # mapping target while routing accepted payloads only.
        live = self.paths.live / self.root["root_key"]
        stray = self.paths.worlds / "not-a-payload"
        stray.mkdir()
        live.unlink()
        live.symlink_to(stray)
        with self.assertRaises(WorldlineError) as caught:
            self.paths.share_live_chain()
        self.assertEqual(caught.exception.code, "LIVE_MAPPING_BROKEN")

    def test_a_removal_is_refused_before_the_swap_when_the_rest_is_unsafe_for_clients(self) -> None:
        # Review of c7d89f1: the client-content check ran after the operator's path was swapped.
        other = Path(self.temporary.name) / "unsafe-other"
        other.mkdir()
        (other / "state.txt").write_text("other\n")
        self.manager.register([other], confirmed=True)
        record = next(item for item in self.store.roots() if bytes(item["path"]) == os.fsencode(other))
        os.chmod(Path(os.fsdecode(self.paths.root_source(record))) / "state.txt", 0o666)
        with mock.patch.object(self.manager.atomic, "exchange", wraps=self.manager.atomic.exchange) as exchange:
            with self.assertRaises(WorldlineError) as caught:
                self.manager.remove(self.root["root_key"], confirmed=True)
        self.assertEqual(caught.exception.code, "CLIENT_MODE_UNSAFE_CONTENT")
        self.assertEqual(exchange.call_count, 0)   # refused before the operator's path was touched
        self.assertTrue(self.work.is_symlink())
        self.assertEqual([p.name for p in self.work.parent.iterdir()
                          if p.name.startswith((".worldline-materialize-", ".worldline-removal-kept-"))], [])

    def test_share_live_chain_opens_a_store_written_before_client_mode(self) -> None:
        source = Path(os.fsdecode(self.paths.root_source(self.root)))
        generation = source.parent.parent
        for directory in (generation, source.parent):
            directory.chmod(0o700)
        self.paths.share_live_chain()
        for directory in (generation, source.parent):
            with self.subTest(directory=str(directory)):
                self.assertEqual(self._mode_and_group(directory), (0o710, SUPPLEMENTARY_GID))

    def test_without_client_mode_every_store_directory_stays_0700(self) -> None:
        owner_only = WorldlinePaths.from_environment(environment(Path(self.temporary.name) / "plain"))
        store = StateStore(owner_only, Core.shared())
        self.addCleanup(store.close)
        for directory in (owner_only.data, owner_only.live, owner_only.generations):
            with self.subTest(directory=str(directory)):
                self.assertEqual(stat.S_IMODE(directory.stat().st_mode), 0o700)


if __name__ == "__main__":
    unittest.main()
