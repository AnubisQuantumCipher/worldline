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
            mission,
        )

    def credential_mounts(self, context: AgentContext) -> tuple[CredentialProjection, ...]:
        directory = context.home / ".omp/agent"
        mounts = [self.required_projection(directory / "agent.db")]
        for source in (
            directory / "agent.db-wal",
            directory / "agent.db-shm",
            directory / "config.yml",
            directory / "models.yml",
        ):
            if source.is_file():
                mounts.append(CredentialProjection(source.resolve(strict=True), source))
        return tuple(mounts)
