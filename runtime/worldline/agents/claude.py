from __future__ import annotations

from .base import AgentAdapter, AgentContext
from ..linux.namespaces import CredentialProjection


class ClaudeAdapter(AgentAdapter):
    name = "claude"
    executable_name = "claude"

    def build_argv(self, context: AgentContext, mission: str) -> tuple[str, ...]:
        del context
        return (
            self.executable,
            "-p",
            "--output-format",
            "stream-json",
            "--include-hook-events",
            "--no-session-persistence",
            "--dangerously-skip-permissions",
            mission,
        )

    def credential_mounts(self, context: AgentContext) -> tuple[CredentialProjection, ...]:
        directory = context.home / ".claude"
        mounts = [self.required_projection(directory / ".credentials.json")]
        for source in (directory / "settings.json", context.home / ".claude.json"):
            if source.is_file():
                mounts.append(CredentialProjection(source.resolve(strict=True), source))
        return tuple(mounts)
