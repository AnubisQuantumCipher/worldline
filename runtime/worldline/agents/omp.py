from __future__ import annotations

from .base import AgentAdapter, AgentContext
from ..linux.namespaces import CredentialProjection


class OmpAdapter(AgentAdapter):
    name = "omp"
    executable_name = "omp"

    def build_argv(self, context: AgentContext, mission: str) -> tuple[str, ...]:
        return (
            self.executable,
            "-p",
            "--mode",
            "json",
            "--no-session",
            "--cwd",
            str(context.primary_root),
            "--approval-mode",
            "yolo",
            *self.extra_argv,
            mission,
        )

    def network_hosts(self) -> tuple[str, ...]:
        return ("api.anthropic.com", "api.openai.com", "chatgpt.com", "auth.openai.com", "generativelanguage.googleapis.com", "openrouter.ai")

    def credential_mounts(self, context: AgentContext) -> tuple[CredentialProjection, ...]:
        directory = context.home / ".omp/agent"
        # omp keeps credentials, settings, and usage in one SQLite database that it opens
        # read-write at startup (it stamps schema_version before doing anything else), so a
        # read-only bind of the host file makes every omp world die with SQLITE_READONLY. The
        # world gets a consistent private copy instead (materialized by the runner through the
        # SQLite backup API, so the WAL is folded in); the host database is never mounted.
        source = self.required_projection(directory / "agent.db")
        mounts = [CredentialProjection(source.source, source.target, private_copy=True)]
        for name in ("config.yml", "models.yml"):
            candidate = directory / name
            if candidate.is_file():
                mounts.append(CredentialProjection(candidate.resolve(strict=True), candidate))
        return tuple(mounts)
