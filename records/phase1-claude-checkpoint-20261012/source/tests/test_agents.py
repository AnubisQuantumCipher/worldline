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

    def test_adapter_options_argv_is_inserted_before_the_mission(self) -> None:
        import shutil
        for name in ("codex", "claude", "omp"):
            if shutil.which(name) is None:
                self.skipTest(f"{name} is not installed on this host; resolving a builtin adapter needs its executable")
        from worldline.agents import adapter as resolve_adapter
        from worldline.config import GlobalConfig
        from worldline.paths import WorldlinePaths

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            env = {"HOME": str(root / "home"), "XDG_DATA_HOME": str(root / "data"), "XDG_STATE_HOME": str(root / "state"), "XDG_CONFIG_HOME": str(root / "config"), "XDG_RUNTIME_DIR": str(root / "runtime")}
            for value in env.values():
                Path(value).mkdir(mode=0o700, parents=True, exist_ok=True)
            paths = WorldlinePaths.from_environment(env)
            paths.ensure()
            config = GlobalConfig.default(paths)
            config.value["adapterOptions"] = {"codex": {"argv": ["-c", "model_reasoning_effort=high"]}, "claude": {"argv": ["--model", "opus"]}}
            config.save()
            argv = resolve_adapter("codex", config).build_argv(self.context, "mission")
            self.assertEqual(argv[-5:], ("-c", "model_reasoning_effort=high", "-C", "/work", "-"))
            self.assertEqual(resolve_adapter("claude", config).build_argv(self.context, "mission")[-3:], ("--model", "opus", "mission"))
            self.assertEqual(resolve_adapter("omp", config).extra_argv, ())
            for bad in ({"nope": {"argv": ["x"]}}, {"codex": {"argv": [""]}}, {"codex": {"model": "x"}}):
                config.value["adapterOptions"] = bad
                with self.assertRaises(WorldlineError):
                    config.save()

    def test_codex_items_become_tool_events_with_paths_commands_and_messages(self) -> None:
        codex = CodexAdapter("codex")
        change = codex.parse_event({"type": "item.completed", "item": {"type": "file_change", "changes": [
            {"path": "/work/a.py", "kind": "add"}, {"path": "/work/b.py", "kind": "update"}, {"nope": 1}]}})
        self.assertEqual(change["kind"], "tool-event")
        self.assertEqual([piece["path"] for piece in change["expand"]], ["/work/a.py", "/work/b.py"])
        self.assertEqual(change["expand"][1]["reason"], "file update")
        command = codex.parse_event({"type": "item.completed", "item": {"type": "command_execution", "command": "/bin/bash -lc 'ls'", "exit_code": 0}})
        self.assertEqual((command["tool"], command["reason"], command["exitCode"]), ("shell", "/bin/bash -lc 'ls'", 0))
        message = codex.parse_event({"type": "item.completed", "item": {"type": "agent_message", "text": "done"}})
        self.assertEqual((message["kind"], message["reason"]), ("agent-message", "done"))
        started = codex.parse_event({"type": "item.started", "item": {"type": "file_change", "changes": [{"path": "/x", "kind": "add"}]}})
        self.assertNotIn("expand", started)

    def test_unknown_event_fields_are_tolerated_without_attribution_invention(self) -> None:
        event = CodexAdapter("codex").parse_event({"futureField": {"nested": True}})
        self.assertEqual(event, {"kind": "agent-event"})


if __name__ == "__main__":
    unittest.main()
