"""A PRIME watcher stand-in for in-process tests (1.9.0).

From 1.9.0 the collapse decision needs a watcher: the kernel compares the watcher's generation
before and after, and the registered roots with the roots actually watched, and refuses
MEASUREMENT_ABSENT without one. The daemon always has a real inotify watcher; tests that build a
CollapseTransaction or CheckpointManager directly use this one, which watches every registered
root and whose generation moves only when a test moves it.
"""
from __future__ import annotations

from contextlib import contextmanager
import os
from typing import Any, Iterator


class FakeWatcher:
    def __init__(self, paths: Any, store: Any) -> None:
        self.paths = paths
        self.store = store
        self.generation = 0
        self.dirty = False
        self.missing: set[str] = set()   # root keys to report as not watched

    def synchronized_generation(self) -> int:
        return self.generation

    def watched_roots(self) -> list[tuple[str, bytes]]:
        return sorted((root["root_key"], os.fsencode(self.paths.root_source(root)))
                      for root in self.store.roots() if root["root_key"] not in self.missing)

    @contextmanager
    def owned_writes(self) -> Iterator[None]:
        yield

    def mark_reconciled(self) -> None:
        self.dirty = False


def watched(manager: Any, paths: Any, store: Any) -> Any:
    """Give a transaction or checkpoint manager a FakeWatcher and return the manager."""
    manager.watcher = FakeWatcher(paths, store)
    return manager
