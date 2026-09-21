from __future__ import annotations

from pathlib import Path

from .base import AgentAdapter, AgentContext
from ..linux.namespaces import CredentialProjection


class CodexAdapter(AgentAdapter):
    name = "codex"
    executable_name = "codex"
    mission_via_stdin = True

    def build_argv(self, context: AgentContext, mission: str) -> tuple[str, ...]:
        del mission
        argv = [
            self.executable,
            "exec",
            "--json",
            "--ephemeral",
            "--dangerously-bypass-approvals-and-sandbox",
            "-C",
            str(context.primary_root),
        ]
        if not context.is_git_root:
            argv.append("--skip-git-repo-check")
        argv.append("-")
        return tuple(argv)

    def network_hosts(self) -> tuple[str, ...]:
        return ("api.openai.com", "chatgpt.com", "auth.openai.com", ".openai.com")

    def credential_mounts(self, context: AgentContext) -> tuple[CredentialProjection, ...]:
        directory = context.home / ".codex"
        mounts = [self.required_projection(directory / "auth.json")]
        config = directory / "config.toml"
        if config.is_file():
            mounts.append(CredentialProjection(config.resolve(strict=True), config))
        return tuple(mounts)
