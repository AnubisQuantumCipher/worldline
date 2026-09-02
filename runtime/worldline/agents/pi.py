from __future__ import annotations

from .base import AgentAdapter, AgentContext
from ..linux.namespaces import CredentialProjection


class PiAdapter(AgentAdapter):
    name = "pi"
    executable_name = "pi"

    def build_argv(self, context: AgentContext, mission: str) -> tuple[str, ...]:
        del context
        return (
            self.executable,
            "-p",
            "--mode",
            "json",
            "--no-session",
            "--approve",
            mission,
        )

    def credential_mounts(self, context: AgentContext) -> tuple[CredentialProjection, ...]:
        directory = context.home / ".pi/agent"
        mounts = [self.required_projection(directory / "auth.json")]
        settings = directory / "settings.json"
        if settings.is_file():
            mounts.append(CredentialProjection(settings.resolve(strict=True), settings))
        return tuple(mounts)
