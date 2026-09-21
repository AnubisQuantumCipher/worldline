from __future__ import annotations

from pathlib import Path
import shutil
from typing import Any, Mapping

from .base import AgentAdapter, AgentContext
from ..config import GenericAgentCommand
from ..errors import WorldlineError
from ..linux.namespaces import CredentialProjection


class GenericAdapter(AgentAdapter):
    executable_name = ""

    def __init__(self, command: GenericAgentCommand) -> None:
        self.command = command
        self.name = command.name
        executable = shutil.which(command.argv[0])
        if executable is None:
            raise WorldlineError("ADAPTER_UNAVAILABLE", f"generic adapter executable is not installed: {command.argv[0]}")
        self.executable = executable

    def build_argv(self, context: AgentContext, mission: str) -> tuple[str, ...]:
        del mission
        expanded = self.command.expand(
            {
                "workspace": str(context.workspace),
                "missionFile": str(context.mission_file),
                "worldState": str(context.world_state),
            }
        )
        return (self.executable, *expanded[1:])

    def network_hosts(self) -> tuple[str, ...]:
        return tuple(self.command.network_hosts)

    def credential_mounts(self, context: AgentContext) -> tuple[CredentialProjection, ...]:
        del context
        mounts: list[CredentialProjection] = []
        for source, target in self.command.credential_mounts:
            if not source.exists():
                raise WorldlineError("ADAPTER_AUTH_UNAVAILABLE", f"generic credential projection is missing: {source}")
            mounts.append(CredentialProjection(source.resolve(strict=True), target))
        return tuple(mounts)
