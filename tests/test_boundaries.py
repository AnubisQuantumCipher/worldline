from __future__ import annotations

import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import sys
import tempfile
import time
import unittest

from worldline.client import DaemonClient
from worldline.errors import WorldlineError
from worldline.paths import WorldlinePaths

RUNTIME = Path(__file__).resolve().parents[1] / "runtime"
LIBRARY = Path(__file__).resolve().parents[1] / "lib/libworldline_core.so"

_AGENT = """import json, os
from pathlib import Path
import sys
workspace = Path(sys.argv[1])
# touch the hostile names the root already has, and add a few more of our own
(workspace / "spaced name.txt").write_text("edited by agent\\n", encoding="utf-8")
(workspace / "uni-ünïcødé-日本.txt").write_text("unicode edited\\n", encoding="utf-8")
(workspace / "new file with $(echo shell) `meta` ;chars.txt").write_text("metacharacters are data\\n", encoding="utf-8")
(workspace / "dash-first").mkdir(exist_ok=True)
(workspace / "dash-first" / "-leading-dash.txt").write_text("leading dash\\n", encoding="utf-8")
os.symlink("base.txt", workspace / "link-to-base")
print(json.dumps({"type": "tool-event", "actor": "hostile", "path": str(workspace / "spaced name.txt"), "line": 1}), flush=True)
"""


def _paths(root: Path) -> tuple[WorldlinePaths, dict[str, str]]:
    env = {
        "HOME": str(root / "home"),
        "XDG_DATA_HOME": str(root / "data"),
        "XDG_STATE_HOME": str(root / "state"),
        "XDG_CONFIG_HOME": str(root / "config"),
        "XDG_RUNTIME_DIR": str(root / "runtime"),
    }
    for value in env.values():
        Path(value).mkdir(mode=0o700, parents=True, exist_ok=True)
    return WorldlinePaths.from_environment(env), env


class _Daemon:
    def __init__(self, test: unittest.TestCase, root: Path, env: dict[str, str], *, log_name: str = "daemon.stderr") -> None:
        self.test = test
        self.env = {
            **os.environ, **env,
            "PYTHONPATH": str(RUNTIME), "PYTHONDONTWRITEBYTECODE": "1", "WORLDLINE_CORE_LIB": str(LIBRARY),
        }
        self.paths = WorldlinePaths.from_environment(env)
        self.log = root / log_name
        self.errors = self.log.open("ab")
        self.process = subprocess.Popen([sys.executable, "-m", "worldline.daemon_main"], env=self.env, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=self.errors)
        # Readiness means the daemon answers, not that a socket path exists: after a SIGKILL the
        # previous instance's socket file is still there while the new one is still recovering.
        self.client = DaemonClient(self.paths, timeout=120)
        deadline = time.monotonic() + 30
        ready = False
        while self.process.poll() is None and time.monotonic() < deadline:
            try:
                self.client.request("ping")
                ready = True
                break
            except WorldlineError:
                time.sleep(0.05)
        if not ready:
            test.fail(self.log.read_text(encoding="utf-8", errors="replace"))

    def kill9(self) -> None:
        self.process.kill()
        self.process.wait(timeout=10)
        self.errors.close()

    def stop(self) -> int:
        if self.process.poll() is None:
            self.process.send_signal(signal.SIGTERM)
            self.process.wait(timeout=15)
        self.errors.close()
        return self.process.returncode


_SLOW = "import time, sys\nopen(sys.argv[1] + '/partial.txt', 'w').write('x')\ntime.sleep(300)\n"
_JUNK = (
    "import sys\n"
    "sys.stdout.buffer.write(b'\\xff\\xfe not json\\n')\n"
    "sys.stdout.buffer.write(b'{\"unterminated\": \\n')\n"
    "sys.stdout.buffer.write(b'x' * 100000 + b'\\n')\n"
    "sys.stdout.buffer.write(b'{\"type\":\"tool-event\",\"path\":\"' + sys.argv[1].encode() + b'/junk.txt\",\"line\":1}\\n')\n"
    "sys.stdout.flush()\n"
    "open(sys.argv[1] + '/junk.txt', 'w').write('ok')\n"
)


def _config(env: dict[str, str], hostile_source: str = _AGENT, extra: dict | None = None, top: dict | None = None) -> None:
    config_dir = Path(env["XDG_CONFIG_HOME"]) / "worldline"
    config_dir.mkdir(mode=0o700, exist_ok=True)
    # Agent scripts live in their own directory: readonlyHomePaths may not overlap WORLDLINE's
    # own storage, and the scripts must be visible inside the world's masked home.
    scripts = Path(env["HOME"]).parent / "agents"
    scripts.mkdir(mode=0o755, exist_ok=True)
    (scripts / "hostile.py").write_text(hostile_source, encoding="utf-8")
    (scripts / "slow.py").write_text(_SLOW, encoding="utf-8")
    (scripts / "junk.py").write_text(_JUNK, encoding="utf-8")
    commands = {
        "hostile": {"argv": ["/usr/bin/python3", str(scripts / "hostile.py"), "{workspace}"], "credentialMounts": [], "eventFormat": "jsonl"},
        "slow": {"argv": ["/usr/bin/python3", str(scripts / "slow.py"), "{workspace}"], "credentialMounts": [], "eventFormat": "jsonl"},
        "junk": {"argv": ["/usr/bin/python3", str(scripts / "junk.py"), "{workspace}"], "credentialMounts": [], "eventFormat": "jsonl"},
    }
    commands.update(extra or {})
    # Agent scripts must be visible inside the world: the sandbox masks the home, so project
    # the directory holding them read-only (the same seam the health check uses).
    document = {"schemaVersion": 1, "readonlyHomePaths": [str(scripts)], "agentCommands": commands, "ghosts": {"enabled": False, "agent": None}}
    document.update(top or {})
    (config_dir / "config.json").write_text(json.dumps(document), encoding="utf-8")
    os.chmod(config_dir / "config.json", 0o600)


class HostileRootContents(unittest.TestCase):
    """Names and objects that break naive tooling must round-trip through capture, fork, collapse, return, and remove."""

    def test_unicode_spaces_metachars_symlinks_hardlinks_and_modes_survive_the_cycle(self) -> None:
        with tempfile.TemporaryDirectory(prefix="worldline-hostile-") as temporary:
            root = Path(temporary)
            paths, env = _paths(root)
            work = root / "proj with space & ünïcode"
            work.mkdir()
            (work / "base.txt").write_text("base\n", encoding="utf-8")
            (work / "spaced name.txt").write_text("spaced\n", encoding="utf-8")
            (work / "uni-ünïcødé-日本.txt").write_text("unicode\n", encoding="utf-8")
            (work / "$(echo injected).txt").write_text("literal\n", encoding="utf-8")
            (work / "-starts-with-dash.txt").write_text("dash\n", encoding="utf-8")
            (work / "secret.txt").write_text("0600\n", encoding="utf-8")
            os.chmod(work / "secret.txt", 0o600)
            (work / "exec.sh").write_text("#!/bin/sh\n", encoding="utf-8")
            os.chmod(work / "exec.sh", 0o755)
            (work / "nested" / "deeper").mkdir(parents=True)
            (work / "nested" / "deeper" / "x").write_text("x", encoding="utf-8")
            (work / "empty-dir").mkdir()
            os.symlink("base.txt", work / "rel-link")
            os.symlink("nested/deeper/x", work / "deep-link")
            os.link(work / "base.txt", work / "hard-link-of-base")
            _config(env)
            daemon = _Daemon(self, root, env)
            try:
                client = daemon.client
                # An external symlink is refused at registration; the directory is untouched.
                os.symlink("/etc/passwd", work / "escape-link")
                with self.assertRaises(WorldlineError) as refused:
                    client.request("init", {"roots": [str(work)], "kind": None, "primary": None, "confirmed": True})
                self.assertEqual(refused.exception.code, "EXTERNAL_SYMLINK")
                self.assertFalse(work.is_symlink())
                (work / "escape-link").unlink()
                # A FIFO is refused too.
                os.mkfifo(work / "pipe")
                with self.assertRaises(WorldlineError) as fifo:
                    client.request("init", {"roots": [str(work)], "kind": None, "primary": None, "confirmed": True})
                self.assertEqual(fifo.exception.code, "UNSUPPORTED_SPECIAL_FILE")
                (work / "pipe").unlink()

                client.request("init", {"roots": [str(work)], "kind": None, "primary": None, "confirmed": True})
                self.assertTrue(work.is_symlink())
                self.assertEqual(stat.S_IMODE((work / "secret.txt").stat().st_mode), 0o600)
                self.assertEqual(stat.S_IMODE((work / "exec.sh").stat().st_mode), 0o755)
                self.assertEqual(os.readlink(work / "rel-link"), "base.txt")
                self.assertEqual((work / "base.txt").stat().st_ino, (work / "hard-link-of-base").stat().st_ino)

                world = client.request("fork", {"name": "hostile", "mission": "touch hostile names", "agent": "hostile", "wait": True})
                self.assertEqual(world["state"], "VALID", world)
                names = {op["pathDisplay"] for op in world["delta"]["files"]}
                self.assertIn("spaced name.txt", names)
                self.assertIn("uni-ünïcødé-日本.txt", names)
                self.assertIn("new file with $(echo shell) `meta` ;chars.txt", names)
                self.assertIn("dash-first/-leading-dash.txt", names)
                self.assertIn("link-to-base", names)
                # A world alias that looks like an option is data, not an option.
                shown = client.request("show", {"world": "hostile"})
                self.assertEqual(shown["state"], "VALID")

                prepared = client.request("collapse.prepare", {"world": "hostile"})
                self.assertEqual(prepared["decision"], "AUTHORIZED")
                committed = client.request("collapse.commit", {"transactionId": prepared["transaction_id"]})
                self.assertEqual(committed["state"], "COMMITTED")
                self.assertEqual((work / "uni-ünïcødé-日本.txt").read_text(encoding="utf-8"), "unicode edited\n")
                self.assertEqual((work / "new file with $(echo shell) `meta` ;chars.txt").read_text(encoding="utf-8"), "metacharacters are data\n")
                self.assertEqual(os.readlink(work / "link-to-base"), "base.txt")
                self.assertEqual((work / "$(echo injected).txt").read_text(encoding="utf-8"), "literal\n")
                self.assertEqual(stat.S_IMODE((work / "secret.txt").stat().st_mode), 0o600)
                self.assertEqual(stat.S_IMODE((work / "exec.sh").stat().st_mode), 0o755)
                self.assertTrue((work / "empty-dir").is_dir())
                self.assertEqual((work / "base.txt").stat().st_ino, (work / "hard-link-of-base").stat().st_ino)
                why = client.request("why", {"path": str(work / "spaced name.txt"), "line": 1})
                self.assertEqual(why["world"], "hostile")
                self.assertEqual(client.request("log", {"verify": True})["verification"]["receipts"], 1)

                returned = client.request("return.prepare", {"world": None})
                client.request("collapse.commit", {"transactionId": returned["transaction_id"]})
                self.assertEqual((work / "uni-ünïcødé-日本.txt").read_text(encoding="utf-8"), "unicode\n")
                self.assertFalse((work / "link-to-base").exists())

                client.request("root.remove", {"root": str(work), "confirmed": True})
                self.assertFalse(work.is_symlink())
                self.assertEqual(os.readlink(work / "deep-link"), "nested/deeper/x")
                self.assertEqual((work / "base.txt").stat().st_ino, (work / "hard-link-of-base").stat().st_ino)
                self.assertEqual(client.request("doctor", {})["storeIntegrity"]["state"], "OK")
            finally:
                self.assertEqual(daemon.stop(), 0, daemon.log.read_text(encoding="utf-8", errors="replace"))


class MalformedAgentOutput(unittest.TestCase):
    def test_binary_junk_and_oversized_lines_do_not_break_the_run(self) -> None:
        with tempfile.TemporaryDirectory(prefix="worldline-junk-") as temporary:
            root = Path(temporary)
            paths, env = _paths(root)
            work = root / "proj"
            work.mkdir()
            (work / "base.txt").write_text("base\n", encoding="utf-8")
            _config(env)
            daemon = _Daemon(self, root, env)
            try:
                client = daemon.client
                client.request("init", {"roots": [str(work)], "kind": None, "primary": None, "confirmed": True})
                world = client.request("fork", {"name": "junky", "mission": "emit junk", "agent": "junk", "wait": True})
                self.assertEqual(world["state"], "VALID", world)
                self.assertEqual([op["pathDisplay"] for op in world["delta"]["files"]], ["junk.txt"])
                events = client.request("log", {"verify": True})["events"]
                kinds = [event["kind"] for event in events if event.get("worldInstance") == world["instanceId"]]
                self.assertIn("tool-event", kinds)
                self.assertNotIn("agent-invocation-result", kinds)  # a parsed event means no fallback record
            finally:
                self.assertEqual(daemon.stop(), 0, daemon.log.read_text(encoding="utf-8", errors="replace"))


class DaemonCrashRecovery(unittest.TestCase):
    def test_sigkill_during_a_run_and_after_a_prepare_recovers_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="worldline-crash-") as temporary:
            root = Path(temporary)
            paths, env = _paths(root)
            work = root / "proj"
            work.mkdir()
            (work / "base.txt").write_text("base\n", encoding="utf-8")
            _config(env, hostile_source="import sys; from pathlib import Path; Path(sys.argv[1], 'made.txt').write_text('made')\n")
            first = _Daemon(self, root, env, log_name="first.stderr")
            client = first.client
            client.request("init", {"roots": [str(work)], "kind": None, "primary": None, "confirmed": True})
            good = client.request("fork", {"name": "good", "mission": "make", "agent": "hostile", "wait": True})
            self.assertEqual(good["state"], "VALID")
            slow = client.request("fork", {"name": "slow", "mission": "sleep", "agent": "slow", "wait": False})
            deadline = time.monotonic() + 20
            while time.monotonic() < deadline:
                jobs = [job for job in client.request("status")["jobs"] if job["world"] == slow["instanceId"] and job["state"] == "RUNNING"]
                if jobs:
                    break
                time.sleep(0.1)
            else:
                self.fail("slow job never reached RUNNING")
            prepared = client.request("collapse.prepare", {"world": "good"})
            self.assertEqual(prepared["decision"], "AUTHORIZED")
            # Crash the daemon with a running agent and a PREPARED transaction outstanding.
            first.kill9()
            self.assertFalse((work / "made.txt").exists())

            second = _Daemon(self, root, env, log_name="second.stderr")
            try:
                client = second.client
                shown = client.request("show", {"world": "slow"})
                self.assertEqual(shown["state"], "DEAD")
                self.assertEqual(shown["evidence"]["supervision"]["code"], "DAEMON_RESTART")
                job = next(job for job in client.request("status")["jobs"] if job["world"] == slow["instanceId"])
                self.assertEqual(job["state"], "DEGRADED")
                self.assertEqual(job["error"]["code"], "DAEMON_RESTART")
                # The orphaned transient unit was stopped by recovery: partial work stays out of PRIME.
                self.assertFalse((work / "partial.txt").exists())
                transactions = client.request("transaction.list")
                self.assertEqual([(t["state"], t["error"]["code"] if t["error"] else None) for t in transactions], [("ABORTED", "RECOVERED_BEFORE_COMMIT")])
                doctor = client.request("doctor", {})
                self.assertEqual(doctor["recovery"]["state"], "OK")
                self.assertEqual(doctor["openTransactions"], [])
                self.assertEqual(doctor["storeIntegrity"]["state"], "OK")
                self.assertEqual(doctor["unsupervisedWorlds"], [])
                # PRIME untouched, and a fresh review still works afterwards.
                self.assertFalse((work / "made.txt").exists())
                fresh = client.request("collapse.prepare", {"world": "good"})
                self.assertEqual(client.request("collapse.commit", {"transactionId": fresh["transaction_id"]})["state"], "COMMITTED")
                self.assertEqual((work / "made.txt").read_text(encoding="utf-8"), "made")
            finally:
                self.assertEqual(second.stop(), 0, second.log.read_text(encoding="utf-8", errors="replace"))


class ReturnAfterTheCheckpointWasLive(unittest.TestCase):
    """A checkpoint that was PRIME changes while it is PRIME (generated outputs, edits made while
    the daemon was down). Its stored manifest predates those changes, and `return` used to refuse
    PAYLOAD_INTEGRITY_FAILED — the live machine hit exactly this after weeks of use. What return
    restores is the state at the instant of displacement, which the displacing receipt recorded as
    beforeRoot; that is what the return point is now verified against."""

    def test_return_restores_the_displaced_state_and_refuses_a_tampered_one(self) -> None:
        with tempfile.TemporaryDirectory(prefix="worldline-return-live-") as temporary:
            root = Path(temporary)
            paths, env = _paths(root)
            work = root / "proj"
            work.mkdir()
            (work / "base.txt").write_text("base\n", encoding="utf-8")
            scripts = Path(env["HOME"]).parent / "agents"
            scripts.mkdir(mode=0o755, exist_ok=True)
            (scripts / "second.py").write_text(
                "import sys; from pathlib import Path; Path(sys.argv[1], 'second.txt').write_text('second')\n", encoding="utf-8"
            )
            _config(
                env,
                hostile_source="import sys; from pathlib import Path; Path(sys.argv[1], 'made.txt').write_text('made')\n",
                extra={"second": {"argv": ["/usr/bin/python3", str(scripts / "second.py"), "{workspace}"], "credentialMounts": [], "eventFormat": "jsonl"}},
            )
            first = _Daemon(self, root, env, log_name="first.stderr")
            try:
                client = first.client
                client.request("init", {"roots": [str(work)], "kind": None, "primary": None, "confirmed": True})
                self.assertEqual(client.request("fork", {"name": "made", "mission": "make", "agent": "hostile", "wait": True})["state"], "VALID")
                prepared = client.request("collapse.prepare", {"world": "made"})
                self.assertEqual(client.request("collapse.commit", {"transactionId": prepared["transaction_id"]})["state"], "COMMITTED")
                self.assertEqual((work / "made.txt").read_text(encoding="utf-8"), "made")
            finally:
                first.stop()
            # Reality moves on while nobody is watching: a build writes generated output into the
            # live root with the daemon stopped, so nothing marks PRIME dirty.
            (work / "out").mkdir()
            (work / "out" / "artifact.bin").write_bytes(b"\x00generated\xff")
            (work / "base.txt").write_text("base, edited by hand\n", encoding="utf-8")

            second = _Daemon(self, root, env, log_name="second.stderr")
            try:
                client = second.client
                self.assertEqual(client.request("fork", {"name": "second", "mission": "again", "agent": "second", "wait": True})["state"], "VALID")
                prepared = client.request("collapse.prepare", {"world": "second"})
                self.assertEqual(prepared["decision"], "AUTHORIZED")
                committed = client.request("collapse.commit", {"transactionId": prepared["transaction_id"]})
                self.assertEqual(committed["state"], "COMMITTED")
                displacing_before_root = committed["beforeRoot"]
                self.assertEqual((work / "second.txt").read_text(encoding="utf-8"), "second")
                self.assertTrue((work / "out" / "artifact.bin").exists())

                # Return to the checkpoint that was live: its stored manifest knows nothing of
                # out/ or the edit, but the receipt that displaced it recorded that exact state.
                returned = client.request("return.prepare", {"world": None})
                self.assertEqual(returned["decision"], "AUTHORIZED")
                result = client.request("collapse.commit", {"transactionId": returned["transaction_id"]})
                self.assertEqual(result["state"], "COMMITTED")
                self.assertEqual(result["afterRoot"], displacing_before_root)
                self.assertEqual(result["receipt"]["afterRoot"], displacing_before_root)
                self.assertFalse((work / "second.txt").exists())
                self.assertEqual((work / "made.txt").read_text(encoding="utf-8"), "made")
                self.assertEqual((work / "base.txt").read_text(encoding="utf-8"), "base, edited by hand\n")
                self.assertEqual((work / "out" / "artifact.bin").read_bytes(), b"\x00generated\xff")
                verification = client.request("log", {"verify": True})["verification"]
                self.assertEqual(verification["receipts"], 3)
                self.assertEqual(client.request("doctor", {})["storeIntegrity"]["state"], "OK")

                # A return point that changed AFTER it was displaced matches neither its manifest
                # nor any receipt, and is refused with the reason.
                probe = client.request("return.prepare", {"world": None})
                self.assertEqual(probe["decision"], "AUTHORIZED")
                client.request("transaction.abort", {"transactionId": probe["transaction_id"]})
                return_point = probe["returnWorld"]
                payload_root = Path(client.request("show", {"world": return_point})["payload_path"])
                root_key = client.request("root.list", {})[0]["rootKey"]
                victim = payload_root / root_key / "second.txt"
                os.chmod(victim, 0o600)  # archived payloads are stored read-only; a tamperer would do this too
                victim.write_text("tampered after displacement", encoding="utf-8")
                with self.assertRaises(WorldlineError) as refused:
                    client.request("return.prepare", {"world": None})
                self.assertEqual(refused.exception.code, "PAYLOAD_INTEGRITY_FAILED")
                self.assertIn("changed after it was displaced", refused.exception.message)
                self.assertEqual(refused.exception.details.get("returnPoint"), return_point)
                self.assertEqual(client.request("doctor", {})["openTransactions"], [])
            finally:
                second.stop()


class RepositoryRootCollapse(unittest.TestCase):
    """A git repository registered as a `repo` root: the agent commits inside its world, the
    collapse carries the commit into the live repository through the same atomic exchange, and
    return takes it out again. Before the git-capture fix this cycle died at commit with
    STAGED_ROOT_MISMATCH because inspecting the staged tree rewrote its index."""

    def test_commit_made_in_a_world_lands_in_the_live_repository_and_returns(self) -> None:
        with tempfile.TemporaryDirectory(prefix="worldline-repo-root-") as temporary:
            root = Path(temporary)
            paths, env = _paths(root)
            work = root / "repo"
            work.mkdir()
            git = ["git", "-c", "user.email=t@example.invalid", "-c", "user.name=t", "-C", str(work)]
            subprocess.run([*git, "init", "-q", "-b", "main"], check=True)
            (work / "greet.py").write_text('def greet(name):\n    return "Hello, " + name\n', encoding="utf-8")
            subprocess.run([*git, "add", "greet.py"], check=True)
            subprocess.run([*git, "commit", "-q", "-m", "initial"], check=True)
            initial = subprocess.run([*git, "rev-parse", "HEAD"], check=True, stdout=subprocess.PIPE).stdout.decode().strip()
            committer = (
                "import subprocess, sys\n"
                "from pathlib import Path\n"
                "w = Path(sys.argv[1])\n"
                "(w / 'greet.py').write_text('def greet(name):\\n    return \"Hello, \" + name + \"!\"\\n')\n"
                "g = ['git', '-c', 'user.email=a@example.invalid', '-c', 'user.name=agent', '-C', str(w)]\n"
                "subprocess.run(g + ['add', 'greet.py'], check=True)\n"
                "subprocess.run(g + ['commit', '-q', '-m', 'greet: exclaim'], check=True)\n"
            )
            _config(env, hostile_source=committer)
            daemon = _Daemon(self, root, env)
            try:
                client = daemon.client
                client.request("init", {"roots": [str(work)], "kind": "repo", "primary": None, "confirmed": True})
                self.assertEqual(client.request("root.list", {})[0]["kind"], "repo")
                world = client.request("fork", {"name": "exclaim", "mission": "add !", "agent": "hostile", "wait": True})
                self.assertEqual(world["state"], "VALID")
                prepared = client.request("collapse.prepare", {"world": "exclaim"})
                self.assertEqual(prepared["decision"], "AUTHORIZED")
                committed = client.request("collapse.commit", {"transactionId": prepared["transaction_id"]})
                self.assertEqual(committed["state"], "COMMITTED")
                head = subprocess.run([*git, "rev-parse", "HEAD"], check=True, stdout=subprocess.PIPE).stdout.decode().strip()
                self.assertNotEqual(head, initial)
                subject = subprocess.run([*git, "log", "-1", "--format=%s"], check=True, stdout=subprocess.PIPE).stdout.decode().strip()
                self.assertEqual(subject, "greet: exclaim")
                self.assertEqual(subprocess.run([*git, "status", "--porcelain"], check=True, stdout=subprocess.PIPE).stdout, b"")
                self.assertIn('"!"', (work / "greet.py").read_text(encoding="utf-8"))
                shown = client.request("show", {"world": "exclaim"})
                self.assertEqual(shown["repository"]["head"], head)
                returned = client.request("return.prepare", {"world": None})
                self.assertEqual(returned["decision"], "AUTHORIZED")
                self.assertEqual(client.request("collapse.commit", {"transactionId": returned["transaction_id"]})["state"], "COMMITTED")
                back = subprocess.run([*git, "rev-parse", "HEAD"], check=True, stdout=subprocess.PIPE).stdout.decode().strip()
                self.assertEqual(back, initial)
                self.assertNotIn('"!"', (work / "greet.py").read_text(encoding="utf-8"))
                self.assertEqual(client.request("log", {"verify": True})["verification"]["receipts"], 2)
            finally:
                daemon.stop()


class NetworkPolicy(unittest.TestCase):
    """allowlist: the world has no network of its own; the only door is the daemon's proxy, which
    reaches allowlisted hosts and refuses everything else by name. none: no door at all."""

    def _serve(self) -> tuple[int, Any]:
        from http.server import BaseHTTPRequestHandler, HTTPServer
        import threading

        class Ok(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802
                self.send_response(200); self.send_header("Content-Length", "2"); self.end_headers(); self.wfile.write(b"ok")
            def log_message(self, *_a) -> None:
                return

        # 127.0.0.2: still loopback on the host, but not on the forwarder's NO_PROXY list
        # (127.0.0.1 and localhost bypass the proxy so an agent can reach services it starts).
        server = HTTPServer(("127.0.0.2", 0), Ok)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        return server.server_address[1], server

    def test_allowlist_reaches_allowed_hosts_refuses_others_and_none_has_no_door(self) -> None:
        port, server = self._serve()
        try:
            with tempfile.TemporaryDirectory(prefix="worldline-net-") as temporary:
                root = Path(temporary)
                paths, env = _paths(root)
                work = root / "proj"
                work.mkdir()
                (work / "base.txt").write_text("base\n", encoding="utf-8")
                prober = (
                    "import json, os, sys, urllib.request, urllib.error\n"
                    "from pathlib import Path\n"
                    "out = {'proxy': os.environ.get('HTTPS_PROXY')}\n"
                    f"for name, url in (('allowed', 'http://127.0.0.2:{port}/x'), ('blocked', 'http://blocked.invalid:{port}/y')):\n"
                    "    try:\n"
                    "        out[name] = urllib.request.urlopen(url, timeout=15).read().decode()\n"
                    "    except urllib.error.HTTPError as e:\n"
                    "        out[name] = 'HTTP %d' % e.code\n"
                    "    except Exception as e:\n"
                    "        out[name] = 'ERR ' + type(e).__name__\n"
                    "Path(sys.argv[1], 'probe.json').write_text(json.dumps(out))\n"
                    "print(json.dumps({'type': 'probe', **out}), flush=True)\n"
                )
                _config(
                    env, hostile_source=prober,
                    extra={"probe": {"argv": ["/usr/bin/python3", str(Path(env["HOME"]).parent / "agents" / "hostile.py"), "{workspace}"], "credentialMounts": [], "eventFormat": "jsonl", "networkHosts": ["127.0.0.2"]}},
                    top={"network": {"policy": "allowlist", "allow": []}},
                )
                daemon = _Daemon(self, root, env)
                try:
                    client = daemon.client
                    client.request("init", {"roots": [str(work)], "kind": None, "primary": None, "confirmed": True})
                    world = client.request("fork", {"name": "guarded", "mission": "probe", "agent": "probe", "wait": True})
                    self.assertEqual(world["state"], "VALID", world)
                    agent = next(check for check in world["checks"] if check["id"] == "agent")
                    self.assertEqual(agent["network"]["policy"], "allowlist")
                    self.assertIn("127.0.0.2", agent["network"]["allowed"])
                    self.assertEqual(agent["network"]["connections"], 1)
                    self.assertEqual(agent["network"]["refused"], [{"host": "blocked.invalid", "port": port, "count": 1}])
                    shown = client.request("show", {"world": "guarded"})
                    probe = json.loads((Path(shown["payload_path"]) / client.request("root.list", {})[0]["rootKey"] / "probe.json").read_text())
                    self.assertEqual(probe["allowed"], "ok")
                    self.assertEqual(probe["blocked"], "HTTP 403")
                    self.assertEqual(probe["proxy"], "http://127.0.0.1:3128")
                finally:
                    daemon.stop()
                # Now the same world under policy none: nothing is reachable and there is no proxy.
                config_path = Path(env["XDG_CONFIG_HOME"]) / "worldline" / "config.json"
                document = json.loads(config_path.read_text())
                document["network"] = {"policy": "none", "allow": []}
                config_path.write_text(json.dumps(document))
                daemon = _Daemon(self, root, env, log_name="none.stderr")
                try:
                    client = daemon.client
                    world = client.request("fork", {"name": "dark", "mission": "probe", "agent": "probe", "wait": True})
                    agent = next(check for check in world["checks"] if check["id"] == "agent")
                    self.assertEqual(agent["network"], {"policy": "none"})
                    shown = client.request("show", {"world": "dark"})
                    probe = json.loads((Path(shown["payload_path"]) / client.request("root.list", {})[0]["rootKey"] / "probe.json").read_text())
                    self.assertIsNone(probe["proxy"])
                    self.assertTrue(probe["allowed"].startswith("ERR"), probe)
                    self.assertTrue(probe["blocked"].startswith("ERR"), probe)
                finally:
                    daemon.stop()
        finally:
            server.shutdown()


class TimeoutStopsAWorld(unittest.TestCase):
    def test_explicit_and_default_timeouts_end_the_world_honestly(self) -> None:
        with tempfile.TemporaryDirectory(prefix="worldline-timeout-") as temporary:
            root = Path(temporary)
            paths, env = _paths(root)
            work = root / "proj"
            work.mkdir()
            (work / "base.txt").write_text("base\n", encoding="utf-8")
            (work / ".worldline.json").write_text(json.dumps({"schemaVersion": 1, "generated": [], "services": [], "checks": [
                {"id": "always", "kind": "tests", "argv": ["/usr/bin/true"], "required": True, "format": "exit"}
            ]}), encoding="utf-8")
            _config(env, top={"limits": {"defaultTimeoutSeconds": 2}})
            daemon = _Daemon(self, root, env)
            try:
                client = daemon.client
                client.request("init", {"roots": [str(work)], "kind": None, "primary": None, "confirmed": True})
                started = time.monotonic()
                world = client.request("fork", {"name": "slowpoke", "mission": "sleep", "agent": "slow", "wait": True, "timeoutSeconds": 3})
                elapsed = time.monotonic() - started
                self.assertLess(elapsed, 25, "the timeout did not stop the world")
                self.assertEqual(world["state"], "DEGRADED")
                agent = next(check for check in world["checks"] if check["id"] == "agent")
                self.assertEqual(agent["status"], "FAIL")
                self.assertTrue(agent["reason"].startswith("TIMEOUT: the agent exceeded the 3 s limit"), agent["reason"])
                project = next(check for check in world["checks"] if check["id"] == "always")
                self.assertEqual(project["status"], "UNASSESSED")
                self.assertIn("timed out", project["reason"])
                job = next(job for job in client.request("status")["jobs"] if job["world"] == world["instanceId"])
                self.assertEqual(job["state"], "TIMED_OUT")
                self.assertEqual(job["error"]["code"], "TIMEOUT")
                self.assertEqual(job["error"]["seconds"], 3)
                # The configured default applies when the request names no timeout.
                world = client.request("fork", {"name": "slowpoke-2", "mission": "sleep", "agent": "slow", "wait": True})
                agent = next(check for check in world["checks"] if check["id"] == "agent")
                self.assertTrue(agent["reason"].startswith("TIMEOUT: the agent exceeded the 2 s limit"), agent["reason"])
                self.assertEqual(client.request("doctor", {})["unsupervisedWorlds"], [])
                with self.assertRaises(Exception):
                    client.request("fork", {"name": "bad", "mission": "x", "agent": "slow", "wait": False, "timeoutSeconds": -1})
            finally:
                daemon.stop()


class CompetingDaemon(unittest.TestCase):
    def test_second_instance_is_refused_and_the_first_keeps_serving(self) -> None:
        with tempfile.TemporaryDirectory(prefix="worldline-compete-") as temporary:
            root = Path(temporary)
            paths, env = _paths(root)
            _config(env)
            first = _Daemon(self, root, env, log_name="first.stderr")
            try:
                second_log = root / "second.stderr"
                with second_log.open("wb") as errors:
                    second = subprocess.run([sys.executable, "-m", "worldline.daemon_main"], env=first.env, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=errors, timeout=30)
                self.assertEqual(second.returncode, 1)
                self.assertIn("DAEMON_ALREADY_RUNNING", second_log.read_text(encoding="utf-8", errors="replace"))
                self.assertIn("version", first.client.request("ping"))
                self.assertTrue(paths.socket.exists())
            finally:
                self.assertEqual(first.stop(), 0, first.log.read_text(encoding="utf-8", errors="replace"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
