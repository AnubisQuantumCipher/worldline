from __future__ import annotations

from dataclasses import dataclass, field
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
