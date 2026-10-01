from __future__ import annotations

from dataclasses import dataclass, field
import errno
import os
import sqlite3
from typing import Any


@dataclass(slots=True)
class WorldlineError(Exception):
    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"

    def as_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}


class CoreUnavailable(WorldlineError):
    def __init__(self, message: str, **details: Any) -> None:
        super().__init__("CORE_UNAVAILABLE", message, details)


class InvalidRequest(WorldlineError):
    def __init__(self, message: str, **details: Any) -> None:
        super().__init__("INVALID_REQUEST", message, details)


class NotFound(WorldlineError):
    def __init__(self, subject: str, value: str) -> None:
        super().__init__("NOT_FOUND", f"{subject} not found: {value}", {"subject": subject, "value": value})


class ConflictError(WorldlineError):
    def __init__(self, message: str, **details: Any) -> None:
        super().__init__("CONFLICT", message, details)


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
