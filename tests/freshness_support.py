"""Harness for the evidence-freshness regressions (JANUS II, 1.3.0).

A private daemon over a throwaway root, deterministic scripted agents (no model quota), a
project policy with a real verifier file inside the root, and helpers to edit the live PRIME,
restart or SIGKILL the daemon, and compare live bytes before and after a refusal. Nothing here
touches the operator's daemon, roots, config or units: every path is under one temporary
directory and every XDG variable is redirected there.
"""
from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from typing import Any

from worldline.client import DaemonClient
from worldline.core import Core, hash_id
from worldline.delta import Delta
from worldline.errors import WorldlineError
from worldline.manifest import Manifest
from worldline.model import World, WorldState
from worldline.paths import WorldlinePaths
from worldline.store import StateStore

REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime"
LIBRARY = REPO / "lib/libworldline_core.so"

# ---- deterministic agents (argv: workspace, missionFile, worldState) ---------------------

WRITER = """import json, sys
from pathlib import Path
w = Path(sys.argv[1])
(w / 'candidate.txt').write_text('candidate', encoding='utf-8')
print(json.dumps({'type': 'tool-event', 'actor': 'fixture', 'path': str(w / 'candidate.txt'), 'line': 1}), flush=True)
"""

WRITER_BOTH = """import json, sys
from pathlib import Path
w = Path(sys.argv[1])
(w / 'candidate.txt').write_text('candidate', encoding='utf-8')
(w / 'extra.txt').write_text('extra', encoding='utf-8')
print(json.dumps({'type': 'tool-event', 'actor': 'fixture', 'path': str(w / 'candidate.txt'), 'line': 1}), flush=True)
"""

# Rewrites the authoritative exam so that it always passes, and does NOT do the work.
FORGER = """import json, sys
from pathlib import Path
w = Path(sys.argv[1])
(w / 'evaluator' / 'exam.py').write_text('import sys\\nsys.exit(0)\\n', encoding='utf-8')
print(json.dumps({'type': 'tool-event', 'actor': 'fixture', 'path': str(w / 'evaluator' / 'exam.py'), 'line': 1}), flush=True)
"""

# Replaces the exam with a symlink to a permissive script it creates (a redirect, same path).
REDIRECTOR = """import json, os, sys
from pathlib import Path
w = Path(sys.argv[1])
(w / 'evaluator' / 'permissive.py').write_text('import sys\\nsys.exit(0)\\n', encoding='utf-8')
os.unlink(w / 'evaluator' / 'exam.py')
os.symlink('permissive.py', w / 'evaluator' / 'exam.py')
print(json.dumps({'type': 'tool-event', 'actor': 'fixture', 'path': str(w / 'evaluator' / 'exam.py'), 'line': 1}), flush=True)
"""

# Rewrites the project policy inside the world to declare no checks at all.
POLICY_EDITOR = """import json, sys
from pathlib import Path
w = Path(sys.argv[1])
(w / '.worldline.json').write_text(json.dumps({'schemaVersion': 1, 'generated': [], 'checks': [], 'services': []}), encoding='utf-8')
print(json.dumps({'type': 'tool-event', 'actor': 'fixture', 'path': str(w / '.worldline.json'), 'line': 1}), flush=True)
"""

# Rewrites the exam's helper module (not the exam itself) so the exam always passes; no work.
HELPER_FORGER = """import json, sys
from pathlib import Path
w = Path(sys.argv[1])
for rel in ('evaluator/helper.py', 'helper.py'):
    if (w / rel).is_file():
        (w / rel).write_text('def verdict(root):\\n    return 0\\n', encoding='utf-8')
        print(json.dumps({'type': 'tool-event', 'actor': 'fixture', 'path': str(w / rel), 'line': 1}), flush=True)
"""

AGENTS = {"writer": WRITER, "writer_both": WRITER_BOTH, "forger": FORGER, "redirector": REDIRECTOR, "policy_editor": POLICY_EDITOR, "helper_forger": HELPER_FORGER}

# ---- the authoritative verifier, in two versions at the same path ------------------------

EXAM_V1 = """import sys
from pathlib import Path
root = Path.cwd()
ok = (root / 'candidate.txt').is_file() and (root / 'candidate.txt').read_text(encoding='utf-8') == 'candidate'
if (root / 'shared.txt').is_file():
    ok = ok and (root / 'shared.txt').read_text(encoding='utf-8').strip() == 'v1'
sys.exit(0 if ok else 1)
"""

EXAM_V2 = EXAM_V1.replace("sys.exit(0 if ok else 1)", "ok = ok and (root / 'extra.txt').is_file()\nsys.exit(0 if ok else 1)")

SLOW_EXAM = "import time\ntime.sleep(4)\n" + EXAM_V1

# An exam that delegates its verdict to a helper module beside it (R1 layout).
EXAM_IMPORTING = """import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import helper
sys.exit(helper.verdict(Path.cwd()))
"""
HELPER_V1 = """def verdict(root):
    ok = (root / 'candidate.txt').is_file() and (root / 'candidate.txt').read_text(encoding='utf-8') == 'candidate'
    return 0 if ok else 1
"""

EXAM_CHECK = {"id": "exam", "kind": "tests", "argv": ["/usr/bin/python3", "evaluator/exam.py"], "required": True, "format": "exit", "covers": ["candidate.txt"]}
EXTRA_CHECK = {"id": "extra", "kind": "tests", "argv": ["/usr/bin/python3", "-c", "import os, sys; sys.exit(0 if os.path.exists('extra.txt') else 1)"], "required": True, "format": "exit"}


def policy(*checks: dict[str, Any], protected: list[str] | None = None) -> dict[str, Any]:
    value: dict[str, Any] = {"schemaVersion": 1, "generated": [], "checks": list(checks), "services": []}
    if protected is not None:
        value["protected"] = list(protected)
    return value


P0 = policy(EXAM_CHECK)
P0_PROTECTED = policy(EXAM_CHECK, protected=["evaluator/*", ".worldline.json"])
P1 = policy(EXAM_CHECK, EXTRA_CHECK)


def isolated_paths(root: Path) -> tuple[WorldlinePaths, dict[str, str]]:
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


def tree_bytes(root: Path) -> dict[str, bytes]:
    """Every regular file under root (relative path -> bytes), symlinks by target."""
    out: dict[str, bytes] = {}
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d != ".git"]
        for name in files:
            path = Path(current) / name
            rel = str(path.relative_to(root))
            out[rel] = os.readlink(path).encode() if path.is_symlink() else path.read_bytes()
    return out


class FreshnessLab:
    def __init__(self, test: unittest.TestCase, *, policy_value: dict[str, Any] | None = P0, exam: str = EXAM_V1, files: dict[str, str] | None = None, network: dict[str, Any] | None = None) -> None:
        self.test = test
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-freshness-")
        self.root = Path(self.temporary.name)
        self.paths, self.env = isolated_paths(self.root)
        self.work = self.root / "proj"
        self.work.mkdir()
        (self.work / "prime.txt").write_text("prime\n", encoding="utf-8")
        (self.work / "evaluator").mkdir()
        (self.work / "evaluator" / "exam.py").write_text(exam, encoding="utf-8")
        for rel, content in (files or {}).items():
            target = self.work / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        if policy_value is not None:
            self.set_policy(policy_value)
        self.agents = self.root / "agents"
        self.agents.mkdir(mode=0o755)
        for name, source in AGENTS.items():
            (self.agents / f"{name}.py").write_text(source, encoding="utf-8")
        self.config_dir = Path(self.env["XDG_CONFIG_HOME"]) / "worldline"
        self.config_dir.mkdir(mode=0o700)
        self.write_config(network)
        self.daemon_env = {**os.environ, **self.env, "PYTHONPATH": str(RUNTIME), "PYTHONDONTWRITEBYTECODE": "1", "WORLDLINE_CORE_LIB": str(LIBRARY)}
        self.process: subprocess.Popen | None = None
        self.log_index = 0
        self.start()

    # -- daemon lifecycle
    def write_config(self, network: dict[str, Any] | None = None) -> None:
        value: dict[str, Any] = {
            "schemaVersion": 1,
            # The sandbox masks the home; the agent scripts must be projected into the world.
            "readonlyHomePaths": [str(self.agents)],
            "agentCommands": {
                name: {"argv": ["/usr/bin/python3", str(self.agents / f"{name}.py"), "{workspace}", "{missionFile}", "{worldState}"], "credentialMounts": [], "eventFormat": "jsonl"}
                for name in AGENTS
            },
            "ghosts": {"enabled": False, "agent": None},
        }
        if network is not None:
            value["network"] = network
        path = self.config_dir / "config.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        os.chmod(path, 0o600)

    def start(self) -> None:
        self.log_index += 1
        self.log = self.root / f"daemon-{self.log_index}.stderr"
        self.errors = self.log.open("wb")
        self.process = subprocess.Popen([sys.executable, "-m", "worldline.daemon_main"], env=self.daemon_env, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=self.errors)
        # Wait for a daemon that actually answers: after a SIGKILL a stale socket file exists
        # before the new process listens on it.
        self.client = DaemonClient(self.paths, timeout=240)
        deadline = time.monotonic() + 30
        while self.process.poll() is None and time.monotonic() < deadline:
            try:
                self.client.request("status")
                return
            except WorldlineError as exc:
                if exc.code != "DAEMON_UNAVAILABLE":
                    raise
                time.sleep(0.05)
        self.test.fail(self.log.read_text(encoding="utf-8", errors="replace"))

    def stop(self) -> int:
        assert self.process is not None
        if self.process.poll() is None:
            self.process.send_signal(signal.SIGTERM)
            self.process.wait(timeout=20)
        self.errors.close()
        return self.process.returncode

    def kill9(self) -> None:
        assert self.process is not None
        self.process.kill()
        self.process.wait(timeout=10)
        self.errors.close()
        if self.paths.socket.exists():
            self.paths.socket.unlink()

    def restart(self, *, network: dict[str, Any] | None = None) -> None:
        code = self.stop()
        self.test.assertEqual(code, 0, self.log.read_text(encoding="utf-8", errors="replace"))
        if network is not None:
            self.write_config(network)
        self.start()

    def close(self) -> None:
        code = self.stop()
        text = self.log.read_text(encoding="utf-8", errors="replace")
        self.temporary.cleanup()
        if code != 0:
            self.test.fail(text)

    def cli(self, *argv: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(REPO / "cli/worldline"), *argv], env=self.daemon_env, capture_output=True, text=True, stdin=subprocess.DEVNULL)

    # -- operations
    def init(self) -> dict[str, Any]:
        return self.client.request("init", {"roots": [str(self.work)], "kind": None, "primary": None, "confirmed": True})

    def fork(self, name: str, agent: str = "writer", mission: str = "do the work") -> dict[str, Any]:
        return self.client.request("fork", {"name": name, "mission": mission, "agent": agent, "wait": True})

    def prepare(self, world: str) -> dict[str, Any]:
        return self.client.request("collapse.prepare", {"world": world})

    def commit(self, transaction_id: str) -> dict[str, Any]:
        return self.client.request("collapse.commit", {"transactionId": transaction_id})

    def return_prepare(self, world: str | None) -> dict[str, Any]:
        return self.client.request("return.prepare", {"world": world})

    def refusal(self, operation, *args, **kwargs) -> WorldlineError:
        with self.test.assertRaises(WorldlineError) as raised:
            operation(*args, **kwargs)
        return raised.exception

    # -- live PRIME edits (the operator's own edits, outside any world)
    def set_policy(self, value: dict[str, Any] | str) -> None:
        text = value if isinstance(value, str) else json.dumps(value)
        (self.work / ".worldline.json").write_text(text, encoding="utf-8")

    def set_exam(self, source: str) -> None:
        (self.work / "evaluator" / "exam.py").write_text(source, encoding="utf-8")

    def write(self, rel: str, content: str) -> None:
        (self.work / rel).write_text(content, encoding="utf-8")

    def settle(self) -> dict[str, Any]:
        """Let the watcher record the operator's edit as a PRIME checkpoint before the next
        operation, so a prepare sees a synchronized generation."""
        time.sleep(0.4)
        self.client.request("status")
        time.sleep(0.2)
        return self.client.request("status")

    # -- observations
    def prime(self) -> dict[str, Any]:
        return self.client.request("status")["prime"] or {}

    def live(self) -> dict[str, bytes]:
        return tree_bytes(self.work)

    def receipts(self) -> list[dict[str, Any]]:
        return self.client.request("log", {"verify": True})["receipts"]

    def transaction(self, transaction_id: str) -> dict[str, Any]:
        return self.client.request("transaction.show", {"transactionId": transaction_id})

    def validation(self, world: str) -> dict[str, Any]:
        return self.client.request("validation.status", {"world": world})

    def revalidate(self, world: str) -> dict[str, Any]:
        return self.client.request("revalidate", {"world": world})

    def open_store(self) -> StateStore:
        """Direct store access; only while the daemon is stopped."""
        assert self.process is not None and self.process.poll() is not None
        return StateStore(self.paths, Core.shared())


# ---- in-process synthetic candidates (no daemon, no sandbox) -------------------------------

def synthetic_candidate(paths: WorldlinePaths, store: StateStore, core: Core, alias: str, changes: dict[str, str]) -> World:
    """A VALID candidate built directly from the current PRIME plus `changes`, exactly the way
    test_transaction builds one. It has no validation context until one is attached."""
    root = store.roots()[0]
    root_key = root["root_key"]
    logical = bytes(root["path"])
    current_source = Path(os.fsdecode(os.path.realpath(logical)))
    base_directory = paths.worlds / alias / "base"
    candidate_directory = paths.worlds / alias / "payload"
    base_directory.parent.mkdir(mode=0o700, parents=True)
    current_manifest = Manifest.capture(current_source, logical_root=logical, root_key=root_key, kind=root["kind"], core=core)
    Manifest.materialize(current_manifest, current_source, base_directory / root_key, core=core)
    Manifest.materialize(current_manifest, current_source, candidate_directory / root_key, core=core)
    for rel, content in changes.items():
        target = candidate_directory / root_key / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    base_manifest = Manifest.capture(base_directory / root_key, logical_root=logical, root_key=root_key, kind=root["kind"], core=core)
    candidate_manifest = Manifest.capture(candidate_directory / root_key, logical_root=logical, root_key=root_key, kind=root["kind"], core=core)
    delta = Delta.compute_all({root_key: base_manifest}, {root_key: candidate_manifest}, core)
    parent = store.prime()
    world = World.create(
        alias=alias, parent_instance=parent.instance_id, parent_content=parent.content_id, cause="set", actor="fixture",
        payload_path=candidate_directory, base_payload_path=base_directory,
        base_root=Manifest.root_set_hash([base_manifest], core), root_set_hash=parent.root_set_hash,
        mission_hash=hash_id(core.hash_bytes(alias.encode("utf-8"))),
    )
    world.components = {**Manifest.component_roots([candidate_manifest], core), "environment": parent.components["environment"], "evidence": parent.components["evidence"]}
    world.delta_hash = delta.delta_hash
    world.delta = {**delta.value["summary"], "files": delta.value["operations"]}
    world.transition(WorldState.FINALIZING, core)
    world.establish_identity(core)
    world.transition(WorldState.VALID, core)
    store.insert_world(world)
    return world
