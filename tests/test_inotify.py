from __future__ import annotations

import os
from pathlib import Path
import tempfile
from threading import Event
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


if __name__ == "__main__":
    unittest.main()
