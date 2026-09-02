from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from worldline.agents.base import AgentContext
from worldline.agents.claude import ClaudeAdapter
from worldline.agents.codex import CodexAdapter
from worldline.agents.omp import OmpAdapter
from worldline.agents.pi import PiAdapter
from worldline.config import GenericAgentCommand
from worldline.agents.generic import GenericAdapter


class AgentAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.context = AgentContext(
            primary_root=Path("/work"),
            workspace=Path("/work"),
            mission_file=Path("/run/mission"),
            world_state=Path("/run/world.json"),
            home=Path("/home/sicarii"),
            is_git_root=True,
        )

    def test_builtin_cli_contracts_are_exact_argv_without_shells(self) -> None:
        codex = CodexAdapter("codex")
        self.assertEqual(
            codex.build_argv(self.context, "mission"),
            (
                "codex", "exec", "--json", "--ephemeral",
                "--dangerously-bypass-approvals-and-sandbox", "-C", "/work", "-",
            ),
        )
        claude = ClaudeAdapter("claude")
        self.assertEqual(
            claude.build_argv(self.context, "mission"),
            (
                "claude", "-p", "--output-format", "stream-json", "--include-hook-events",
                "--no-session-persistence", "--dangerously-skip-permissions", "mission",
            ),
        )
        omp = OmpAdapter("omp")
        self.assertEqual(
            omp.build_argv(self.context, "mission"),
            (
                "omp", "-p", "--mode", "json", "--no-session", "--cwd", "/work",
                "--approval-mode", "yolo", "mission",
            ),
        )
        pi = PiAdapter("pi")
        self.assertEqual(
            pi.build_argv(self.context, "mission"),
            ("pi", "-p", "--mode", "json", "--no-session", "--approve", "mission"),
        )

    def test_unknown_event_fields_are_tolerated_without_attribution_invention(self) -> None:
        event = CodexAdapter("codex").parse_event({"futureField": {"nested": True}})
        self.assertEqual(event, {"kind": "agent-event"})


if __name__ == "__main__":
    unittest.main()
