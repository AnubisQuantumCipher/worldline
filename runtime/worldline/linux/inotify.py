from __future__ import annotations

from contextlib import contextmanager
import ctypes
import errno
import os
import select
import struct
from threading import Event, Lock, RLock, Thread
from typing import Any, Callable, Iterator, Sequence

from ..errors import WorldlineError
from ..manifest import display_path, path_b64

_IN_MODIFY = 0x00000002
_IN_ATTRIB = 0x00000004
_IN_CLOSE_WRITE = 0x00000008
_IN_MOVED_FROM = 0x00000040
_IN_MOVED_TO = 0x00000080
_IN_CREATE = 0x00000100
_IN_DELETE = 0x00000200
_IN_DELETE_SELF = 0x00000400
_IN_MOVE_SELF = 0x00000800
_IN_Q_OVERFLOW = 0x00004000
_IN_IGNORED = 0x00008000
_IN_ISDIR = 0x40000000
_IN_NONBLOCK = os.O_NONBLOCK
_IN_CLOEXEC = os.O_CLOEXEC
_WATCH_MASK = (
    _IN_MODIFY
    | _IN_ATTRIB
    | _IN_CLOSE_WRITE
    | _IN_MOVED_FROM
    | _IN_MOVED_TO
    | _IN_CREATE
    | _IN_DELETE
    | _IN_DELETE_SELF
    | _IN_MOVE_SELF
)
_EVENT_HEADER = struct.Struct("=iIII")


class InotifyWatcher:
    def __init__(
        self,
        roots: Sequence[tuple[str, str | bytes | os.PathLike[str] | os.PathLike[bytes]]],
        callback: Callable[[dict[str, Any]], None],
    ) -> None:
        self._callback = callback
        self._libc = ctypes.CDLL(None, use_errno=True)
        self._libc.inotify_init1.argtypes = [ctypes.c_int]
        self._libc.inotify_init1.restype = ctypes.c_int
        self._libc.inotify_add_watch.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32]
        self._libc.inotify_add_watch.restype = ctypes.c_int
        self._libc.inotify_rm_watch.argtypes = [ctypes.c_int, ctypes.c_int]
        self._libc.inotify_rm_watch.restype = ctypes.c_int
        descriptor = self._libc.inotify_init1(_IN_NONBLOCK | _IN_CLOEXEC)
        if descriptor < 0:
            error = ctypes.get_errno()
            raise WorldlineError("INOTIFY_UNAVAILABLE", os.strerror(error), {"errno": error})
        self._fd = descriptor
        self._state_lock = RLock()
        self._read_lock = Lock()
        self._stop = Event()
        self._owned_depth = 0
        self._generation = 0
        self._dirty = False
        self._overflow = False
        self._watches: dict[int, tuple[str, bytes, bytes]] = {}
        # Coverage (1.9.0): a root whose tree could not be watched completely, and whether the
        # reader thread has died. Either takes the root (or every root) out of watched_roots, so
        # the collapse decision sees WATCH_INCOMPLETE instead of assuming coverage.
        self._roots = {root_key: os.path.abspath(os.fsencode(root)) for root_key, root in roots}
        self._faulted: dict[str, str] = {}
        self._dead = False
        try:
            # A root that cannot be watched completely is a fault the collapse decision sees
            # (WATCH_INCOMPLETE) and doctor reports; it never stops the daemon from starting
            # (review of 0ee1112: an unreadable directory in PRIME made every restart fail).
            for root_key, root in self._roots.items():
                self._add_tree(root_key, root)
        except BaseException:
            os.close(self._fd)
            raise
        self._thread = Thread(target=self._run, name="worldline-inotify", daemon=True)
        self._thread.start()

    @property
    def generation(self) -> int:
        with self._state_lock:
            return self._generation

    def synchronized_generation(self) -> int:
        with self._read_lock:
            self._drain()
            with self._state_lock:
                return self._generation

    @property
    def dirty(self) -> bool:
        with self._state_lock:
            return self._dirty

    @property
    def overflowed(self) -> bool:
        with self._state_lock:
            return self._overflow

    def _add_watch(self, root_key: str, root: bytes, relative: bytes) -> None:
        absolute = root if not relative else os.path.join(root, relative)
        watch = self._libc.inotify_add_watch(self._fd, absolute, _WATCH_MASK)
        if watch < 0:
            error = ctypes.get_errno()
            raise WorldlineError(
                "INOTIFY_WATCH_FAILED",
                f"could not watch {display_path(absolute)}: {os.strerror(error)}",
                {"errno": error},
            )
        self._watches[watch] = (root_key, root, relative)

    def _add_tree(self, root_key: str, root: bytes, start: bytes = b"") -> bool:
        """Watch a directory and everything below it; True when all of it is watched. Each
        directory is watched BEFORE it is listed, so a subdirectory created after the listing is
        reported by its parent's watch (IN_CREATE) rather than missed (review of a23c265). A
        directory that vanished again is skipped (its parent's watch reported that); one that
        cannot be watched or listed faults the root, and the walk goes on (review of 0ee1112)."""
        absolute_start = root if not start else os.path.join(root, start)
        if not os.path.isdir(absolute_start) or os.path.islink(absolute_start):
            if start:
                return True  # replaced by a non-directory since its event: nothing to watch
            self._faulted[root_key] = f"watch root is not a directory: {display_path(absolute_start)}"
            return False
        complete = True
        pending = [start]
        while pending:
            relative = pending.pop()
            absolute = root if not relative else os.path.join(root, relative)
            try:
                self._add_watch(root_key, root, relative)
                with os.scandir(absolute) as entries:
                    names = sorted(entry.name for entry in entries if entry.is_dir(follow_symlinks=False))
            except FileNotFoundError:
                continue
            except WorldlineError as exc:
                if (exc.details or {}).get("errno") == errno.ENOENT:
                    continue
                self._faulted[root_key] = exc.message
                complete = False
                continue
            except OSError as exc:
                self._faulted[root_key] = f"could not list {display_path(absolute)}: {os.strerror(exc.errno or 0)}"
                complete = False
                continue
            pending.extend(name if not relative else relative + b"/" + name for name in reversed(names))
        return complete

    def _run(self) -> None:
        poller = select.poll()
        poller.register(self._fd, select.POLLIN | select.POLLERR | select.POLLHUP)
        while not self._stop.is_set():
            try:
                ready = poller.poll(250)
            except OSError as exc:
                if self._stop.is_set() or exc.errno == errno.EBADF:
                    return
                raise
            if not ready:
                continue
            try:
                with self._read_lock:
                    self._drain()
            except Exception:  # noqa: BLE001 - a dead reader must be visible, not silent
                with self._state_lock:
                    self._dead = True
                    self._dirty = True
                return

    def _drain(self) -> None:
        while True:
            try:
                data = os.read(self._fd, 64 * 1024)
            except BlockingIOError:
                return
            except OSError as exc:
                if self._stop.is_set() or exc.errno == errno.EBADF:
                    return
                raise
            if not data:
                return
            offset = 0
            while offset + _EVENT_HEADER.size <= len(data):
                watch, mask, cookie, name_length = _EVENT_HEADER.unpack_from(data, offset)
                offset += _EVENT_HEADER.size
                raw_name = data[offset : offset + name_length].split(b"\x00", 1)[0]
                offset += name_length
                self._consume(watch, mask, cookie, raw_name)

    def _consume(self, watch: int, mask: int, cookie: int, raw_name: bytes) -> None:
        with self._state_lock:
            self._generation += 1
            owned = self._owned_depth > 0
            if mask & _IN_Q_OVERFLOW:
                self._overflow = True
                self._dirty = True
                # Events were lost, a directory's creation among them perhaps: nothing is known to
                # be completely watched until the next reconcile walks every tree again.
                for root_key in self._roots:
                    self._faulted[root_key] = "the event queue overflowed; the tree must be walked again"
                event = {
                    "kind": "overflow",
                    "generation": self._generation,
                    "owned": owned,
                    "rootKey": None,
                    "pathB64": None,
                    "pathDisplay": None,
                    "mask": mask,
                    "cookie": cookie,
                }
            else:
                metadata = self._watches.get(watch)
                if metadata is None:
                    return
                root_key, root, directory = metadata
                relative = directory
                if raw_name:
                    relative = raw_name if not directory else directory + b"/" + raw_name
                if not owned:
                    self._dirty = True
                event = {
                    "kind": "change",
                    "generation": self._generation,
                    "owned": owned,
                    "rootKey": root_key,
                    "pathB64": path_b64(relative),
                    "pathDisplay": display_path(relative),
                    "mask": mask,
                    "cookie": cookie,
                }
                if mask & _IN_IGNORED:
                    self._watches.pop(watch, None)
                if mask & _IN_MOVE_SELF and directory == b"":
                    # The root directory itself moved away: its watch now follows the old inode,
                    # not the path. Drop it, so the root reports as unwatched.
                    self._watches.pop(watch, None)
                    self._libc.inotify_rm_watch(self._fd, watch)
                    self._faulted[root_key] = "the root directory was moved or replaced"
                if mask & _IN_ISDIR and mask & (_IN_CREATE | _IN_MOVED_TO):
                    if not self._add_tree(root_key, root, relative):
                        self._dirty = True
            external = not owned
        if external:
            self._callback(event)

    def watched_roots(self) -> list[tuple[str, bytes]]:
        """The roots completely watched right now, as (root key, path). Not here: a root whose
        top-level watch was dropped (IN_IGNORED: the directory went away) or that moved
        (IN_MOVE_SELF), a root part of whose tree could not be watched, and every root once the
        reader thread has died. The collapse decision then sees partial coverage (1.9.0)."""
        with self._state_lock:
            if self._dead:
                return []
            return sorted((root_key, root) for root_key, root, relative in self._watches.values()
                          if relative == b"" and root_key not in self._faulted)

    def coverage_faults(self) -> dict[str, str]:
        """Why each unwatched root is not covered, for doctor."""
        with self._state_lock:
            faults = dict(self._faulted)
            if self._dead:
                faults["*"] = "the watcher's reader thread stopped"
            return faults

    @contextmanager
    def owned_writes(self) -> Iterator[None]:
        with self._read_lock:
            with self._state_lock:
                self._owned_depth += 1
            try:
                yield
            finally:
                self._drain()
                with self._state_lock:
                    self._owned_depth -= 1

    def mark_reconciled(self) -> None:
        with self._state_lock:
            self._dirty = False
            self._overflow = False
            # A reconcile re-captured PRIME from disk; try to restore full coverage of each
            # faulted root now. A root that still cannot be watched stays out of watched_roots.
            for root_key in list(self._faulted):
                root = self._roots.get(root_key)
                if root is None or not os.path.isdir(root) or os.path.islink(root):
                    continue
                for watch, (key, _root, _relative) in list(self._watches.items()):
                    if key == root_key:  # stale: they may follow a tree that is no longer here
                        self._watches.pop(watch, None)
                        self._libc.inotify_rm_watch(self._fd, watch)
                reason = self._faulted.pop(root_key)
                if not self._add_tree(root_key, root):
                    self._faulted.setdefault(root_key, reason)

    def close(self) -> None:
        if self._stop.is_set():
            return
        self._stop.set()
        os.close(self._fd)
        self._thread.join(timeout=2)

    @classmethod
    def capability(cls) -> dict[str, Any]:
        libc = ctypes.CDLL(None, use_errno=True)
        function = getattr(libc, "inotify_init1", None)
        if function is None:
            return {"state": "UNAVAILABLE", "reason": "libc does not expose inotify_init1"}
        function.argtypes = [ctypes.c_int]
        function.restype = ctypes.c_int
        descriptor = function(_IN_NONBLOCK | _IN_CLOEXEC)
        if descriptor < 0:
            error = ctypes.get_errno()
            return {"state": "UNAVAILABLE", "reason": os.strerror(error), "errno": error}
        os.close(descriptor)
        return {"state": "AVAILABLE", "backend": "inotify"}


def stable_capture(watcher: InotifyWatcher, capture: Callable[[], Any]) -> Any:
    before = watcher.synchronized_generation()
    result = capture()
    after = watcher.synchronized_generation()
    if before != after:
        raise WorldlineError(
            "PRIME_CHANGED_DURING_CAPTURE",
            "managed roots changed while WORLDLINE copied and hashed PRIME",
            {"beforeGeneration": before, "afterGeneration": after},
        )
    watcher.mark_reconciled()
    return result
