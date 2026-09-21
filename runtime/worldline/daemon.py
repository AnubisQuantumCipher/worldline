from __future__ import annotations

import asyncio
import sqlite3
import errno
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
import fcntl
import inspect
import json
import logging
import os
from pathlib import Path
import socket
import stat
import struct
from typing import Any

from . import __version__
from .canonical import canonical_bytes
from .errors import InvalidRequest, WorldlineError
from .manifest import repository_facts
from .paths import WorldlinePaths
from .status import StatusPublisher
from .store import StateStore

_LOG = logging.getLogger("worldline.daemon")
_MAX_REQUEST_BYTES = 16 * 1024 * 1024

Progress = Callable[[str, dict[str, Any]], Awaitable[None]]
Handler = Callable[[dict[str, Any], "RequestContext"], Any]


@dataclass(slots=True)
class RequestContext:
    daemon: "WorldlineDaemon"
    request_id: str | int
    progress: Progress


@dataclass(slots=True)
class Operation:
    handler: Handler
    mutating: bool


def storage_error(exc: BaseException) -> WorldlineError:
    """Name a storage failure. ENOSPC/EDQUOT (and SQLite's "disk is full") become DISK_FULL;
    any other OSError or SQLite error becomes STORAGE_ERROR with the errno name and path."""
    if isinstance(exc, sqlite3.Error):
        text = str(exc)
        code = "DISK_FULL" if "full" in text.lower() else "STORAGE_ERROR"
        return WorldlineError(code, f"store: {text}", {"backend": "sqlite"})
    assert isinstance(exc, OSError)
    name = errno.errorcode.get(exc.errno or 0, f"errno {exc.errno}")
    code = "DISK_FULL" if exc.errno in (errno.ENOSPC, errno.EDQUOT) else "STORAGE_ERROR"
    details: dict[str, Any] = {"errno": name}
    path = exc.filename
    if path is not None:
        path_text = os.fsdecode(path) if isinstance(path, (bytes, bytearray)) else str(path)
        details["path"] = path_text
    message = f"{name}: {exc.strerror or 'storage operation failed'}"
    if "path" in details:
        message += f": {details['path']}"
    return WorldlineError(code, message, details)


class WorldlineDaemon:
    def __init__(
        self,
        paths: WorldlinePaths,
        store: StateStore,
        publisher: StatusPublisher,
        *,
        recover: Callable[[], Any] | None = None,
        reconcile_status: Callable[[], Any] | None = None,
    ) -> None:
        self.paths = paths
        self.store = store
        self.publisher = publisher
        self._recover = recover
        self._reconcile_status = reconcile_status
        self._operations: dict[str, Operation] = {}
        self._mutation_lock = asyncio.Lock()
        self._server: asyncio.AbstractServer | None = None
        self._background: dict[str, asyncio.Task[Any]] = {}
        self._heartbeat_task: asyncio.Task[None] | None = None
        self._lock_fd: int | None = None
        self._stopping = False
        self.register("ping", self._ping)
        self.register("status", self._status, mutating=True)
        self.register("list", self._list)
        self.register("show", self._show)
        self.register("log.verify", self._verify_log)

    def register(self, name: str, handler: Handler, *, mutating: bool = False) -> None:
        if not name or name in self._operations:
            raise ValueError(f"duplicate or empty operation: {name}")
        self._operations[name] = Operation(handler=handler, mutating=mutating)

    def spawn_background(self, key: str, awaitable: Awaitable[Any]) -> asyncio.Task[Any]:
        if key in self._background and not self._background[key].done():
            raise WorldlineError("JOB_ALREADY_RUNNING", f"background job is already running: {key}")
        task = asyncio.create_task(awaitable, name=f"worldline:{key}")
        self._background[key] = task

        def finished(done: asyncio.Task[Any]) -> None:
            self._background.pop(key, None)
            if not done.cancelled() and done.exception() is not None:
                _LOG.error("background job %s failed", key, exc_info=done.exception())
            try:
                self.publisher.publish()
            except Exception:
                _LOG.exception("status publication failed after job %s", key)

        task.add_done_callback(finished)
        return task

    async def start(self) -> None:
        if self._server is not None:
            raise RuntimeError("daemon is already started")
        os.umask(0o077)
        self.paths.ensure()
        self._acquire_singleton_lock()
        if self._recover is not None:
            result = self._recover()
            if inspect.isawaitable(result):
                await result
        swept = self.store.sweep_unsupervised()
        if swept["jobs"] or swept["worlds"]:
            _LOG.warning("startup sweep: %d orphaned job(s), %d unsupervised world(s) marked DEAD", swept["jobs"], swept["worlds"])
        self._remove_stale_socket()
        self._server = await asyncio.start_unix_server(
            self._handle_client,
            path=self.paths.socket,
            limit=_MAX_REQUEST_BYTES,
        )
        os.chmod(self.paths.socket, 0o600)
        self._verify_socket()
        self.publisher.publish(daemon_state="RUNNING")
        self._heartbeat_task = asyncio.create_task(self._heartbeat(), name="worldline:status-heartbeat")

    async def _heartbeat(self) -> None:
        while True:
            await asyncio.sleep(5)
            try:
                self.publisher.publish(daemon_state="RUNNING")
            except Exception:
                _LOG.exception("status heartbeat publication failed")

    async def serve_forever(self) -> None:
        if self._server is None:
            await self.start()
        assert self._server is not None
        async with self._server:
            await self._server.serve_forever()

    async def stop(self) -> None:
        if self._stopping:
            return
        self._stopping = True
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
            self._server = None
        if self._heartbeat_task is not None:
            self._heartbeat_task.cancel()
            await asyncio.gather(self._heartbeat_task, return_exceptions=True)
            self._heartbeat_task = None
        tasks = tuple(self._background.values())
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        try:
            self.publisher.publish(daemon_state="STOPPED")
        finally:
            self.paths.socket.unlink(missing_ok=True)
            if self._lock_fd is not None:
                os.close(self._lock_fd)
                self._lock_fd = None

    def _acquire_singleton_lock(self) -> None:
        # A single mutation lock inside one process is not enough: a second worldlined would
        # unlink this daemon's socket, bind its own, and run collapses concurrently against the
        # same store (SQLite WAL serves both), so two self-consistent exchanges could race and
        # violate "exactly one world commits." An advisory flock held for the daemon's lifetime
        # makes a second daemon fail fast instead.
        lock_path = self.paths.socket.parent / "worldlined.lock"
        fd = os.open(lock_path, os.O_RDWR | os.O_CREAT | os.O_CLOEXEC, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            os.close(fd)
            raise WorldlineError(
                "DAEMON_ALREADY_RUNNING",
                f"another worldlined already holds {lock_path}",
            ) from exc
        os.ftruncate(fd, 0)
        os.write(fd, f"{os.getpid()}\n".encode("ascii"))
        self._lock_fd = fd

    def _remove_stale_socket(self) -> None:
        try:
            info = self.paths.socket.lstat()
        except FileNotFoundError:
            return
        if info.st_uid != os.getuid() or not stat.S_ISSOCK(info.st_mode):
            raise WorldlineError("UNSAFE_SOCKET", f"refusing to replace unsafe socket path: {self.paths.socket}")
        self.paths.socket.unlink()

    def _verify_socket(self) -> None:
        info = self.paths.socket.lstat()
        if info.st_uid != os.getuid() or not stat.S_ISSOCK(info.st_mode):
            raise WorldlineError("UNSAFE_SOCKET", f"daemon socket failed ownership validation: {self.paths.socket}")
        if stat.S_IMODE(info.st_mode) != 0o600:
            raise WorldlineError("UNSAFE_SOCKET", f"daemon socket mode is not 0600: {self.paths.socket}")

    @staticmethod
    def _peer_uid(writer: asyncio.StreamWriter) -> int:
        transport_socket = writer.get_extra_info("socket")
        if transport_socket is None:
            raise WorldlineError("PEER_CREDENTIALS_UNAVAILABLE", "Unix peer socket is unavailable")
        credentials = transport_socket.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i"))
        _pid, uid, _gid = struct.unpack("3i", credentials)
        return uid

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            if self._peer_uid(writer) != os.getuid():
                await self._send(writer, {"id": None, "ok": False, "result": None, "error": {
                    "code": "PEER_UID_MISMATCH", "message": "peer uid does not own this daemon", "details": {}
                }})
                return
            while not reader.at_eof():
                try:
                    line = await reader.readline()
                except (ValueError, asyncio.LimitOverrunError) as exc:
                    raise InvalidRequest("request exceeds maximum NDJSON line size") from exc
                if not line:
                    break
                if len(line) > _MAX_REQUEST_BYTES:
                    raise InvalidRequest("request exceeds maximum NDJSON line size")
                await self._dispatch_line(line, writer)
        except WorldlineError as exc:
            await self._send(
                writer,
                {"id": None, "ok": False, "result": None, "error": exc.as_dict()},
            )
        except (ConnectionError, BrokenPipeError):
            pass
        except Exception:
            _LOG.exception("client handler failed")
            try:
                await self._send(writer, {"id": None, "ok": False, "result": None, "error": {
                    "code": "INTERNAL_ERROR", "message": "daemon request handler failed", "details": {}
                }})
            except ConnectionError:
                pass
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except ConnectionError:
                pass

    async def _dispatch_line(self, line: bytes, writer: asyncio.StreamWriter) -> None:
        request_id: str | int | None = None
        try:
            try:
                request = json.loads(line.decode("utf-8", "strict"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise InvalidRequest("request is not UTF-8 JSON") from exc
            if not isinstance(request, dict) or set(request) != {"id", "op", "args"}:
                raise InvalidRequest("request must have exactly id, op, and args fields")
            request_id = request["id"]
            if isinstance(request_id, bool) or not isinstance(request_id, (str, int)):
                raise InvalidRequest("request id must be a string or integer")
            operation_name = request["op"]
            args = request["args"]
            if not isinstance(operation_name, str) or not isinstance(args, dict):
                raise InvalidRequest("op must be a string and args must be an object")
            operation = self._operations.get(operation_name)
            if operation is None:
                raise WorldlineError("UNKNOWN_OPERATION", f"unknown daemon operation: {operation_name}")

            async def progress(event: str, data: dict[str, Any]) -> None:
                await self._send(writer, {"id": request_id, "event": event, "data": data})

            context = RequestContext(self, request_id, progress)
            if operation.mutating:
                async with self._mutation_lock:
                    result = await self._invoke(operation.handler, args, context)
                    self.publisher.publish()
            else:
                result = await self._invoke(operation.handler, args, context)
            await self._send(writer, {"id": request_id, "ok": True, "result": result, "error": None})
        except WorldlineError as exc:
            await self._send(writer, {"id": request_id, "ok": False, "result": None, "error": exc.as_dict()})
        except (OSError, sqlite3.Error) as exc:
            # Storage failed underneath a handler (disk full is the one that happens): name it,
            # so the operator sees DISK_FULL with the errno and path instead of INTERNAL_ERROR.
            _LOG.exception("operation failed on storage")
            await self._send(writer, {"id": request_id, "ok": False, "result": None, "error": storage_error(exc).as_dict()})
        except Exception:
            _LOG.exception("operation failed")
            await self._send(writer, {"id": request_id, "ok": False, "result": None, "error": {
                "code": "INTERNAL_ERROR", "message": "daemon operation failed", "details": {}
            }})

    @staticmethod
    async def _invoke(handler: Handler, args: dict[str, Any], context: RequestContext) -> Any:
        result = handler(args, context)
        return await result if inspect.isawaitable(result) else result

    @staticmethod
    async def _send(writer: asyncio.StreamWriter, value: dict[str, Any]) -> None:
        # A detached fork/race returns immediately while its background job keeps reporting
        # progress to the request that started it; once that client has gone, the events have
        # nowhere to go. Dropping them is correct (the durable record is the causal chain) and
        # keeps asyncio from logging "socket.send() raised exception" every few seconds.
        if writer.is_closing():
            return
        try:
            writer.write(canonical_bytes(value) + b"\n")
            await writer.drain()
        except (ConnectionError, BrokenPipeError, RuntimeError):
            return

    def _ping(self, args: dict[str, Any], _context: RequestContext) -> dict[str, Any]:
        if args:
            raise InvalidRequest("ping takes no arguments")
        return {"version": __version__, "pid": os.getpid()}

    def _status(self, args: dict[str, Any], _context: RequestContext) -> dict[str, Any]:
        if args:
            raise InvalidRequest("status takes no arguments")
        if self._reconcile_status is not None and self.store.get_meta("dirty", False):
            self._reconcile_status()
        return self.publisher.publish()

    def _list(self, args: dict[str, Any], _context: RequestContext) -> list[dict[str, Any]]:
        if args:
            raise InvalidRequest("list takes no arguments")
        return [world.summary() for world in self.store.worlds()]

    def _show(self, args: dict[str, Any], _context: RequestContext) -> dict[str, Any]:
        if set(args) != {"world"} or not isinstance(args["world"], str):
            raise InvalidRequest("show requires one string world argument")
        world = self.store.world(args["world"])
        record = world.record()
        record["repository"] = None if world.payload_pruned else repository_facts(world.payload_path, self.store.roots())
        return record

    def _verify_log(self, args: dict[str, Any], _context: RequestContext) -> dict[str, int]:
        if args:
            raise InvalidRequest("log.verify takes no arguments")
        return self.store.verify_chains()
