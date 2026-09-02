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
        for root_key, root in roots:
            self._add_tree(root_key, os.path.abspath(os.fsencode(root)))
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

    def _add_tree(self, root_key: str, root: bytes, start: bytes = b"") -> None:
        absolute_start = root if not start else os.path.join(root, start)
        if not os.path.isdir(absolute_start):
            raise WorldlineError("INOTIFY_WATCH_FAILED", f"watch root is not a directory: {display_path(absolute_start)}")
        for current, directories, _files in os.walk(absolute_start, followlinks=False):
            current_bytes = os.fsencode(current)
            relative = os.path.relpath(current_bytes, root)
            if relative == b".":
                relative = b""
            self._add_watch(root_key, root, relative)
            directories[:] = sorted(
                name for name in directories if not os.path.islink(os.path.join(current_bytes, os.fsencode(name)))
            )

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
            with self._read_lock:
                self._drain()

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
                if mask & _IN_ISDIR and mask & (_IN_CREATE | _IN_MOVED_TO):
                    absolute = os.path.join(root, relative)
                    if os.path.isdir(absolute) and not os.path.islink(absolute):
                        self._add_tree(root_key, root, relative)
            external = not owned
        if external:
            self._callback(event)

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
