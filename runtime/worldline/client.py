from __future__ import annotations

import json
import socket
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
            connection.sendall(canonical_bytes(request) + b"\n")
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
        finally:
            connection.close()
