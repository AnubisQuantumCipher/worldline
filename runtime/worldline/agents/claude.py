from __future__ import annotations

from .base import AgentAdapter, AgentContext
from ..linux.namespaces import CredentialProjection


class ClaudeAdapter(AgentAdapter):
    name = "claude"
    executable_name = "claude"

    def build_argv(self, context: AgentContext, mission: str) -> tuple[str, ...]:
        del context
        # Claude Code ≥ 2.1 refuses `--print --output-format stream-json` without `--verbose`
        # ("requires --verbose"), which is how every builtin claude world on this machine had
        # been dying at launch; the events are what WORLDLINE parses, so verbose is the point.
        #
        # The operator's settings.json is projected so model choice, env, and the credential
        # helper carry into the world, but its hooks are desktop integrations that reference
        # host scripts and host state (on this machine a cockpit tracker on every event). Inside
        # a world they cannot run, and a hook that exits 2 BLOCKS the prompt, so the agent
        # "succeeds" having done nothing. Hooks are disabled in-world; `--bare` is not used
        # because it also refuses the operator's OAuth credential.
        return (
            self.executable,
            "-p",
            "--verbose",
            "--output-format",
            "stream-json",
            "--include-hook-events",
            "--no-session-persistence",
            "--dangerously-skip-permissions",
            "--settings",
            '{"disableAllHooks":true}',
            mission,
        )

    def credential_mounts(self, context: AgentContext) -> tuple[CredentialProjection, ...]:
        directory = context.home / ".claude"
        mounts = [self.required_projection(directory / ".credentials.json")]
        for source in (directory / "settings.json", context.home / ".claude.json"):
            if source.is_file():
                mounts.append(CredentialProjection(source.resolve(strict=True), source))
        return tuple(mounts)
