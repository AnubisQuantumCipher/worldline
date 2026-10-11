from __future__ import annotations

import json
from pathlib import Path

from .base import AgentAdapter, AgentContext
from ..errors import WorldlineError
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
            *self.extra_argv,
            mission,
        )

    def network_hosts(self) -> tuple[str, ...]:
        return ("api.anthropic.com", "api.openai.com", "chatgpt.com", "auth.openai.com", "generativelanguage.googleapis.com", "openrouter.ai", "api.x.ai")

    def credential_mounts(self, context: AgentContext) -> tuple[CredentialProjection, ...]:
        directory = context.home / ".pi/agent"
        auth = self.required_projection(directory / "auth.json")
        # pi resolves its model key from auth.json (or a provider key in its environment, which
        # the sandbox clears). An auth file with no providers is the "installed but never logged
        # in" state; a world launched into it dies with "No API key found", so refuse up front
        # with the reason the operator needs, without reading any credential value.
        if not self._declares_provider(auth.source):
            raise WorldlineError(
                "ADAPTER_AUTH_UNAVAILABLE",
                f"pi has no provider credentials in {auth.source} (run `pi login` or `pi auth` first)",
            )
        mounts = [auth]
        settings = directory / "settings.json"
        if settings.is_file():
            mounts.append(CredentialProjection(settings.resolve(strict=True), settings))
        return tuple(mounts)

    @staticmethod
    def _declares_provider(auth_path: Path) -> bool:
        try:
            value = json.loads(auth_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return False
        return isinstance(value, dict) and any(isinstance(item, dict) and item for item in value.values())
