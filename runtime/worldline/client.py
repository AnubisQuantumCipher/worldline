from __future__ import annotations

import json
import os
import socket
import struct
from pathlib import Path
from typing import Any, Callable
import uuid

from .canonical import canonical_bytes
from .errors import WorldlineError
from .paths import WorldlinePaths

ProgressCallback = Callable[[str, dict[str, Any]], None]


class DaemonClient:
    def __init__(self, paths: WorldlinePaths | None = None, *, timeout: float = 30.0) -> None:
        self.paths = paths or WorldlinePaths.from_environment()
        self.timeout = timeout

    def request(
        self,
        operation: str,
        args: dict[str, Any] | None = None,
        *,
        progress: ProgressCallback | None = None,
    ) -> Any:
        request_id = str(uuid.uuid4())
        request = {"id": request_id, "op": operation, "args": args or {}}
        connection = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        connection.settimeout(self.timeout)
        try:
            connection.connect(str(self.paths.socket))
            # The daemon must be the expected principal: this user, or the dedicated account
            # WORLDLINE_DAEMON_UID names. A socket someone else bound is not the daemon.
            _pid, peer_uid, _gid = struct.unpack("3i", connection.getsockopt(
                socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i")))
            expected_uid = os.getuid() if self.paths.daemon_uid is None else self.paths.daemon_uid
            if peer_uid != expected_uid:
                raise WorldlineError(
                    "DAEMON_PEER_UNEXPECTED",
                    f"worldlined socket is served by uid {peer_uid}, expected {expected_uid}")
            try:
                connection.sendall(canonical_bytes(request) + b"\n")
            except (BrokenPipeError, ConnectionResetError):
                # A daemon that refuses this peer answers and closes before reading anything;
                # its refusal is already in our receive buffer, so read it instead of failing
                # on the send. A daemon that closed without answering shows as DAEMON_DISCONNECTED.
                pass
            stream = connection.makefile("rb")
            while True:
                line = stream.readline()
                if not line:
                    raise WorldlineError("DAEMON_DISCONNECTED", "daemon closed the request before a terminal response")
                try:
                    message = json.loads(line.decode("utf-8", "strict"))
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise WorldlineError("INVALID_DAEMON_RESPONSE", "daemon emitted invalid NDJSON") from exc
                if message.get("id") not in (request_id, None):
                    raise WorldlineError("INVALID_DAEMON_RESPONSE", "daemon response id did not match request")
                if "event" in message:
                    if progress is not None:
                        progress(str(message["event"]), message.get("data", {}))
                    continue
                if set(message) != {"id", "ok", "result", "error"}:
                    raise WorldlineError("INVALID_DAEMON_RESPONSE", "terminal response schema drifted")
                if message["ok"]:
                    return message["result"]
                error = message.get("error") or {}
                raise WorldlineError(
                    str(error.get("code", "DAEMON_ERROR")),
                    str(error.get("message", "daemon operation failed")),
                    error.get("details", {}),
                )
        except FileNotFoundError as exc:
            raise WorldlineError("DAEMON_UNAVAILABLE", f"worldlined socket is missing: {self.paths.socket}") from exc
        except ConnectionRefusedError as exc:
            raise WorldlineError("DAEMON_UNAVAILABLE", f"worldlined is not accepting requests: {self.paths.socket}") from exc
        except PermissionError as exc:
            # A dedicated-account daemon's socket admits only its client group.
            raise WorldlineError("DAEMON_ACCESS_DENIED", f"no permission to reach worldlined: {self.paths.socket}") from exc
        finally:
            connection.close()
