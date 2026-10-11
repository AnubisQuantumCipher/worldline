from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

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
            *self.extra_argv,
            "-C",
            str(context.primary_root),
        ]
        if not context.is_git_root:
            argv.append("--skip-git-repo-check")
        argv.append("-")
        return tuple(argv)

    def network_hosts(self) -> tuple[str, ...]:
        return ("api.openai.com", "chatgpt.com", "auth.openai.com", ".openai.com")

    def parse_event(self, value: Mapping[str, Any]) -> dict[str, Any]:
        # `codex exec --json` nests what happened under `item`: a file_change carries every
        # touched path in `changes[]`, a command_execution carries the command. Surfacing those
        # as tool events is what gives `why` file-level provenance for codex worlds.
        item = value.get("item")
        if value.get("type") == "item.completed" and isinstance(item, dict):
            kind = item.get("type")
            if kind == "file_change":
                expanded = [
                    {"kind": "tool-event", "actor": self.name, "tool": "apply_patch", "path": change["path"], "reason": f"file {change.get('kind', 'change')}"}
                    for change in item.get("changes", [])
                    if isinstance(change, dict) and isinstance(change.get("path"), str) and change["path"]
                ]
                if expanded:
                    return {"kind": "tool-event", "actor": self.name, "tool": "apply_patch", "expand": expanded}
            if kind == "command_execution":
                command = item.get("command")
                event: dict[str, Any] = {"kind": "tool-event", "actor": self.name, "tool": "shell"}
                if isinstance(command, str) and command:
                    event["reason"] = command[:200]
                exit_code = item.get("exit_code")
                if isinstance(exit_code, int) and not isinstance(exit_code, bool):
                    event["exitCode"] = exit_code
                return event
            if kind == "agent_message" and isinstance(item.get("text"), str):
                return {"kind": "agent-message", "actor": self.name, "reason": item["text"][:400]}
        return super().parse_event(value)

    def credential_mounts(self, context: AgentContext) -> tuple[CredentialProjection, ...]:
        directory = context.home / ".codex"
        mounts = [self.required_projection(directory / "auth.json")]
        config = directory / "config.toml"
        if config.is_file():
            mounts.append(CredentialProjection(config.resolve(strict=True), config))
        return tuple(mounts)
