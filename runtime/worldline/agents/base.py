from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
import shutil
from typing import Any, Mapping

from ..errors import WorldlineError
from ..linux.namespaces import CredentialProjection


@dataclass(frozen=True, slots=True)
class AgentContext:
    primary_root: Path
    workspace: Path
    mission_file: Path
    world_state: Path
    home: Path
    is_git_root: bool


class AgentAdapter(ABC):
    name: str
    executable_name: str
    mission_via_stdin: bool = False

    def __init__(self, executable: str | None = None) -> None:
        self.executable = executable or shutil.which(self.executable_name)
        if self.executable is None:
            raise WorldlineError("ADAPTER_UNAVAILABLE", f"{self.executable_name} is not installed", {"adapter": self.name})

    @abstractmethod
    def build_argv(self, context: AgentContext, mission: str) -> tuple[str, ...]:
        raise NotImplementedError

    @abstractmethod
    def credential_mounts(self, context: AgentContext) -> tuple[CredentialProjection, ...]:
        raise NotImplementedError

    def parse_event(self, value: Mapping[str, Any]) -> dict[str, Any]:
        event: dict[str, Any] = {"kind": self._first_string(value, "type", "event", "kind") or "agent-event"}
        actor = self._first_string(value, "actor", "agent")
        if actor is not None:
            event["actor"] = actor
        tool = self._first_string(value, "tool", "tool_name", "toolName")
        if tool is not None:
            event["tool"] = tool
        reason = self._first_string(value, "reason", "explanation", "rationale")
        if reason is not None:
            event["reason"] = reason
        path = self._first_string(value, "path", "file", "file_path", "filePath")
        if path is not None:
            event["path"] = path
        line = self._first_integer(value, "line", "line_number", "lineNumber")
        if line is not None:
            event["line"] = line
        session = self.session_reference(value)
        if session is not None:
            event["sessionReference"] = session
        return event

    def session_reference(self, value: Mapping[str, Any]) -> str | None:
        return self._first_string(
            value,
            "session_id",
            "sessionId",
            "thread_id",
            "threadId",
            "conversation_id",
            "conversationId",
        )

    @staticmethod
    def _first_string(value: Mapping[str, Any], *names: str) -> str | None:
        for name in names:
            candidate = value.get(name)
            if isinstance(candidate, str) and candidate:
                return candidate
        return None

    @staticmethod
    def _first_integer(value: Mapping[str, Any], *names: str) -> int | None:
        for name in names:
            candidate = value.get(name)
            if isinstance(candidate, int) and not isinstance(candidate, bool):
                return candidate
        return None

    @staticmethod
    def required_projection(source: Path, target: Path | None = None) -> CredentialProjection:
        if not source.is_file():
            raise WorldlineError(
                "ADAPTER_AUTH_UNAVAILABLE",
                f"declared authentication projection is missing: {source}",
            )
        return CredentialProjection(source.resolve(strict=True), target or source)

    def capability(self, context: AgentContext) -> dict[str, Any]:
        try:
            mounts = self.credential_mounts(context)
        except WorldlineError as exc:
            return {
                "name": self.name,
                "state": "UNAVAILABLE",
                "executable": self.executable,
                "reason": exc.message,
            }
        return {
            "name": self.name,
            "state": "AVAILABLE",
            "executable": self.executable,
            "missionViaStdin": self.mission_via_stdin,
            "credentialMounts": [
                {"source": str(item.source), "target": str(item.target)} for item in mounts
            ],
        }
