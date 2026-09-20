from __future__ import annotations

from pathlib import Path
import contextlib
import json
import sqlite3
import tempfile
import unittest

from worldline.agents.base import AgentContext
from worldline.agents.claude import ClaudeAdapter
from worldline.agents.codex import CodexAdapter
from worldline.agents.omp import OmpAdapter
from worldline.agents.pi import PiAdapter
from worldline.config import GenericAgentCommand
from worldline.agents.generic import GenericAdapter
from worldline.errors import WorldlineError
from worldline.runner import materialize_private_copies


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
                "claude", "-p", "--verbose", "--output-format", "stream-json", "--include-hook-events",
                "--no-session-persistence", "--dangerously-skip-permissions",
                "--settings", '{"disableAllHooks":true}', "mission",
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

    def test_pi_refuses_an_auth_file_with_no_providers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            agent = home / ".pi/agent"
            agent.mkdir(parents=True)
            (agent / "auth.json").write_text("{}", encoding="utf-8")
            context = AgentContext(
                primary_root=Path("/work"), workspace=Path("/work"), mission_file=Path("/run/mission"),
                world_state=Path("/run/world.json"), home=home, is_git_root=True,
            )
            pi = PiAdapter("pi")
            with self.assertRaises(WorldlineError) as caught:
                pi.credential_mounts(context)
            self.assertEqual(caught.exception.code, "ADAPTER_AUTH_UNAVAILABLE")
            self.assertEqual(pi.capability(context)["state"], "UNAVAILABLE")
            (agent / "auth.json").write_text(json.dumps({"anthropic": {"type": "api_key", "key": "x"}}), encoding="utf-8")
            self.assertEqual(pi.credential_mounts(context)[0].target, agent / "auth.json")

    def test_omp_database_is_projected_as_a_private_sqlite_copy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            agent = home / ".omp/agent"
            agent.mkdir(parents=True)
            with contextlib.closing(sqlite3.connect(agent / "agent.db")) as db, db:
                db.execute("pragma journal_mode=wal")
                db.execute("create table auth_credentials (id integer primary key, secret text)")
                db.execute("insert into auth_credentials (secret) values ('host-only')")
            context = AgentContext(
                primary_root=Path("/work"), workspace=Path("/work"), mission_file=Path("/run/mission"),
                world_state=Path("/run/world.json"), home=home, is_git_root=True,
            )
            mounts = OmpAdapter("omp").credential_mounts(context)
            self.assertTrue(mounts[0].private_copy)
            self.assertEqual(mounts[0].target, agent / "agent.db")
            copies = materialize_private_copies(mounts, home / "runtime" / "private-credentials")
            copy = copies[0].source
            self.assertNotEqual(copy, mounts[0].source)
            self.assertTrue(copy.is_relative_to(home / "runtime"))
            self.assertEqual(copy.stat().st_mode & 0o777, 0o600)
            with contextlib.closing(sqlite3.connect(copy)) as db, db:
                db.execute("update auth_credentials set secret = 'world-only'")
                self.assertEqual(db.execute("select secret from auth_credentials").fetchone()[0], "world-only")
            with contextlib.closing(sqlite3.connect(agent / "agent.db")) as db:
                self.assertEqual(db.execute("select secret from auth_credentials").fetchone()[0], "host-only")

    def test_unknown_event_fields_are_tolerated_without_attribution_invention(self) -> None:
        event = CodexAdapter("codex").parse_event({"futureField": {"nested": True}})
        self.assertEqual(event, {"kind": "agent-event"})


if __name__ == "__main__":
    unittest.main()
