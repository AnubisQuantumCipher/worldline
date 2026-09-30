from __future__ import annotations

import os
from pathlib import Path
import tempfile
from threading import Event
import time
import unittest

from worldline.errors import WorldlineError
from worldline.linux.inotify import InotifyWatcher, stable_capture


class InotifyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-inotify-")
        self.root = Path(self.temporary.name) / "root"
        self.root.mkdir()
        self.events: list[dict[str, object]] = []
        self.received = Event()

        def callback(event: dict[str, object]) -> None:
            self.events.append(event)
            self.received.set()

        self.watcher = InotifyWatcher([("fixture", self.root)], callback)

    def tearDown(self) -> None:
        self.watcher.close()
        self.temporary.cleanup()

    def settle(self) -> None:
        """Wait until the watcher has been quiet for a while. One write raises several events
        (create, modify, close); reconciling after only the first let a late event from the
        SAME external write mark PRIME dirty again, a hosted-runner flake."""
        while True:
            self.received.clear()
            if not self.received.wait(0.3):
                return

    def test_external_changes_dirty_prime_but_owned_writes_do_not(self) -> None:
        (self.root / "external.txt").write_text("outside", encoding="utf-8")
        self.assertTrue(self.received.wait(2))
        self.settle()
        self.assertTrue(self.watcher.dirty)
        self.watcher.mark_reconciled()
        self.events.clear()
        self.received.clear()

        with self.watcher.owned_writes():
            (self.root / "owned.txt").write_text("inside", encoding="utf-8")
        self.assertFalse(self.watcher.dirty)
        self.assertEqual(self.events, [])

    def test_stable_capture_rejects_concurrent_change(self) -> None:
        with self.assertRaises(WorldlineError) as caught:
            stable_capture(
                self.watcher,
                lambda: (self.root / "raced.txt").write_text("changed", encoding="utf-8"),
            )
        self.assertEqual(caught.exception.code, "PRIME_CHANGED_DURING_CAPTURE")


class WatchCoverageTests(unittest.TestCase):
    """What watched_roots reports is what the collapse decision compares with the registered
    roots (1.9.0): a root the watcher does not fully cover must not be reported as watched."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-inotify-coverage-")
        self.root = Path(self.temporary.name) / "root"
        self.root.mkdir()
        self.watcher = InotifyWatcher([("fixture", self.root)], lambda _event: None)

    def tearDown(self) -> None:
        self.watcher.close()
        self.temporary.cleanup()

    def watched(self) -> list[str]:
        self.watcher.synchronized_generation()  # drain what the kernel has queued
        return [key for key, _path in self.watcher.watched_roots()]

    def eventually(self, condition) -> None:
        for _ in range(100):
            if condition():
                return
            time.sleep(0.02)
        self.fail("condition never held")

    def test_a_removed_root_is_not_watched(self) -> None:
        self.assertEqual(self.watched(), ["fixture"])
        self.root.rmdir()
        self.eventually(lambda: self.watched() == [])

    def test_a_moved_and_replaced_root_is_not_watched_until_reconciled(self) -> None:
        self.root.rename(Path(self.temporary.name) / "old")
        self.root.mkdir()
        self.eventually(lambda: self.watched() == [])
        self.assertIn("fixture", self.watcher.coverage_faults())
        self.watcher.mark_reconciled()  # a reconcile re-captured PRIME: coverage is restored
        self.assertEqual(self.watched(), ["fixture"])
        self.assertEqual(self.watcher.coverage_faults(), {})

    def test_a_directory_created_after_start_is_watched_to_its_depth(self) -> None:
        nested = self.root / "a" / "b"
        nested.mkdir(parents=True)
        self.eventually(lambda: any(relative == b"a/b" for _key, _root, relative in self.watcher._watches.values()))
        before = self.watcher.synchronized_generation()
        (nested / "file.txt").write_text("x", encoding="utf-8")
        self.eventually(lambda: self.watcher.synchronized_generation() > before)
        self.assertEqual(self.watched(), ["fixture"])

    def test_a_dead_reader_thread_leaves_nothing_watched(self) -> None:
        def broken(*_args):
            raise RuntimeError("reader failure")
        self.watcher._consume = broken
        (self.root / "trigger.txt").write_text("x", encoding="utf-8")
        self.eventually(lambda: "*" in self.watcher.coverage_faults())
        self.assertEqual(self.watcher.watched_roots(), [])


class WatchFaultTests(unittest.TestCase):
    """A root the watcher cannot cover completely is reported, never fatal (review of 0ee1112:
    an unreadable directory made the daemon unable to start)."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-inotify-faults-")
        self.root = Path(self.temporary.name) / "root"
        (self.root / "locked").mkdir(parents=True)

    def tearDown(self) -> None:
        os.chmod(self.root / "locked", 0o700)
        self.temporary.cleanup()

    def test_an_unreadable_directory_faults_its_root_and_is_restored_by_a_reconcile(self) -> None:
        os.chmod(self.root / "locked", 0)
        watcher = InotifyWatcher([("fixture", self.root)], lambda _event: None)
        try:
            watcher.synchronized_generation()
            self.assertEqual(watcher.watched_roots(), [])
            self.assertIn("fixture", watcher.coverage_faults())
            os.chmod(self.root / "locked", 0o700)
            watcher.mark_reconciled()
            self.assertEqual([key for key, _path in watcher.watched_roots()], ["fixture"])
        finally:
            watcher.close()

    def test_an_overflowed_queue_faults_every_root_until_the_next_reconcile(self) -> None:
        from worldline.linux.inotify import _IN_Q_OVERFLOW
        watcher = InotifyWatcher([("fixture", self.root)], lambda _event: None)
        try:
            descriptors = set(watcher._watches)
            watcher._consume(-1, _IN_Q_OVERFLOW, 0, b"")
            self.assertEqual(watcher.watched_roots(), [])
            self.assertTrue(watcher.dirty)
            watcher.mark_reconciled()
            self.assertEqual([key for key, _path in watcher.watched_roots()], ["fixture"])
            # The rebuild re-confirms the existing watches instead of dropping and re-adding
            # them, so no write lands in an unwatched window (review of 19d0297).
            self.assertEqual(set(watcher._watches), descriptors)
        finally:
            watcher.close()


if __name__ == "__main__":
    unittest.main()
