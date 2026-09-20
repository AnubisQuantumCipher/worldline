from __future__ import annotations

import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest

from worldline.capabilities import CapabilityRegistry
from worldline.client import DaemonClient
from worldline.controller import RuntimeController
from worldline.core import Core, TRANSACTION_STATE_CODES, hash_id
from worldline.delta import Delta
from worldline.errors import ConflictError, WorldlineError
from worldline.manifest import Manifest
from worldline.model import World, WorldState
from worldline.paths import WorldlinePaths
from worldline.roots import RootManager
from worldline.store import StateStore
from worldline.transaction import CollapseTransaction

_TRANSACTION_TABLE = {
    "PREPARED": {"AUTHORIZED", "DENIED", "ABORTED"},
    "AUTHORIZED": {"COMMITTED", "ABORTED"},
    "DENIED": {"ABORTED"},
    "COMMITTED": set(),
    "ABORTED": set(),
}


def _isolated_paths(root: Path) -> tuple[WorldlinePaths, dict[str, str]]:
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


class TransactionLifecycleThroughKernel(unittest.TestCase):
    """The proved Transitions.Transaction_Allowed is what the runtime consults, not a mirror."""

    def test_c_export_matches_runtime_table_for_every_pair(self) -> None:
        core = Core.shared()
        for source in TRANSACTION_STATE_CODES:
            for target in TRANSACTION_STATE_CODES:
                with self.subTest(source=source, target=target):
                    self.assertEqual(
                        core.transaction_transition_allowed(source, target),
                        target in _TRANSACTION_TABLE[source],
                    )

    def test_unknown_state_is_refused_not_guessed(self) -> None:
        with self.assertRaises(WorldlineError) as raised:
            Core.shared().transaction_transition_allowed("PREPARED", "SHIPPED")
        self.assertEqual(raised.exception.code, "INVALID_TRANSACTION_STATE")


class CapabilityReprobe(unittest.TestCase):
    """An UNAVAILABLE probe is re-run after the TTL; an AVAILABLE one stays cached."""

    def test_transient_unavailable_heals_without_refresh(self) -> None:
        with tempfile.TemporaryDirectory(prefix="worldline-cap-") as temporary:
            paths, _env = _isolated_paths(Path(temporary))
            now = [1000.0]
            registry = CapabilityRegistry(paths, reprobe_seconds=30.0, clock=lambda: now[0])
            answers = iter([
                {"state": "UNAVAILABLE", "reason": "starting"},
                {"state": "AVAILABLE", "managerState": "running"},
                {"state": "UNAVAILABLE", "reason": "must not be reached"},
            ])
            calls = {"systemd": 0}

            def systemd_probe() -> dict:
                calls["systemd"] += 1
                return next(answers)

            # Replace every probe with a cheap stub so the test measures caching, not the host.
            for name in list(registry._probes):
                registry._probes[name] = (lambda n=name: {"state": "AVAILABLE", "stub": n})
            registry._probes["systemd"] = systemd_probe

            first = registry.snapshot()
            self.assertEqual(first["systemd"]["state"], "UNAVAILABLE")
            self.assertIn("probedAt", first["systemd"])
            self.assertEqual(calls["systemd"], 1)

            now[0] += 5
            self.assertEqual(registry.snapshot()["systemd"]["state"], "UNAVAILABLE", "re-probed before TTL")
            self.assertEqual(calls["systemd"], 1)

            now[0] += 30
            healed = registry.snapshot()
            self.assertEqual(healed["systemd"]["state"], "AVAILABLE")
            self.assertEqual(calls["systemd"], 2)

            now[0] += 3600
            self.assertEqual(registry.snapshot()["systemd"]["state"], "AVAILABLE", "AVAILABLE must stay cached")
            self.assertEqual(calls["systemd"], 2)
            self.assertEqual(registry.snapshot()["overlay"]["stub"], "overlay")


class UnsupervisedWorldSweep(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-sweep-")
        self.paths, _env = _isolated_paths(Path(self.temporary.name))
        self.core = Core.shared()
        self.store = StateStore(self.paths, self.core)

    def tearDown(self) -> None:
        self.store.close()
        self.temporary.cleanup()

    def _world(self, alias: str, state: WorldState = WorldState.MUTABLE) -> World:
        zero = hash_id(bytes(32))
        world = World.create(
            alias=alias,
            parent_instance=None,
            parent_content=zero,
            cause="fixture",
            actor="fixture",
            payload_path=self.paths.worlds / alias / "payload",
            base_payload_path=self.paths.generations / "base",
            base_root=zero,
            root_set_hash=zero,
            mission_hash=zero,
        )
        if state is WorldState.FINALIZING:
            world.transition(WorldState.FINALIZING, self.core)
        self.store.insert_world(world)
        return world

    def test_world_without_any_job_becomes_dead_with_reason(self) -> None:
        orphan = self._world("orphan")
        swept = self.store.sweep_unsupervised()
        self.assertEqual(swept, {"jobs": 0, "worlds": 1})
        after = self.store.world(orphan.instance_id)
        self.assertEqual(after.state, WorldState.DEAD)
        self.assertIsNotNone(after.ended)
        self.assertEqual(after.evidence["supervision"]["code"], "NO_SUPERVISING_JOB")
        self.assertEqual(after.evidence["summary"], "FAIL")

    def test_running_job_is_degraded_and_its_world_dead_via_kernel(self) -> None:
        world = self._world("lost", WorldState.FINALIZING)
        self.store.create_job(
            job_id="job-1", world_instance=world.instance_id, state="RUNNING",
            raw_event_path=self.paths.logs / "x.jsonl", sandbox={},
        )
        swept = self.store.sweep_unsupervised()
        self.assertEqual(swept, {"jobs": 1, "worlds": 1})
        job = next(item for item in self.store.jobs() if item["job_id"] == "job-1")
        self.assertEqual(job["state"], "DEGRADED")
        self.assertEqual(job["error"]["code"], "DAEMON_RESTART")
        after = self.store.world(world.instance_id)
        self.assertEqual(after.state, WorldState.DEAD)
        self.assertEqual(after.evidence["supervision"]["code"], "DAEMON_RESTART")
        # The kernel forbids MUTABLE/FINALIZING -> DEGRADED, which the old SQL sweep produced.
        self.assertFalse(self.core.transition_allowed("MUTABLE", "DEGRADED"))

    def test_terminal_worlds_are_left_alone(self) -> None:
        self._world("done").transition  # noqa: B018 - existence check only
        done = self.store.world("done")
        done.transition(WorldState.FINALIZING, self.core)
        done.transition(WorldState.VALID, self.core)
        self.store.save_world(done)
        self.assertEqual(self.store.sweep_unsupervised(), {"jobs": 0, "worlds": 0})
        self.assertEqual(self.store.world("done").state, WorldState.VALID)


class StoreIntegrityBasePayload(unittest.TestCase):
    def test_fork_checkpoint_referenced_only_as_base_is_not_an_orphan(self) -> None:
        with tempfile.TemporaryDirectory(prefix="worldline-integ-") as temporary:
            paths, _env = _isolated_paths(Path(temporary))
            paths.ensure()
            store = StateStore(paths, Core.shared())
            try:
                checkpoint = paths.generations / "checkpoint" / "payload"
                (checkpoint / ("b" * 64)).mkdir(mode=0o700, parents=True)
                (checkpoint / "manifests").mkdir(mode=0o700)
                zero = hash_id(bytes(32))
                world = World.create(
                    alias="zeta", parent_instance=None, parent_content=zero, cause="x", actor="fixture",
                    payload_path=paths.worlds / "zeta" / "payload",
                    base_payload_path=checkpoint,   # only reference to the checkpoint
                    base_root=zero, root_set_hash=zero, mission_hash=zero,
                )
                store.insert_world(world)
                controller = object.__new__(RuntimeController)
                controller.store = store
                controller.paths = paths
                report = RuntimeController._store_integrity(controller)
                self.assertEqual(report["state"], "OK", report["findings"])
            finally:
                store.close()


class MeaningfulParentCheck(unittest.TestCase):
    """The kernel's PARENT_MISMATCH must be reachable: the store's parent identity vs the claim."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-parent-")
        self.paths, _env = _isolated_paths(Path(self.temporary.name))
        self.core = Core.shared()
        self.store = StateStore(self.paths, self.core)
        self.roots = RootManager(self.paths, self.store, core=self.core, toolchains=())
        self.work = Path(self.temporary.name) / "work"
        self.work.mkdir()
        (self.work / "state.txt").write_text("prime", encoding="utf-8")
        self.roots.register([self.work], confirmed=True)
        self.transaction = CollapseTransaction(self.paths, self.store, core=self.core)

    def tearDown(self) -> None:
        self.store.close()
        self.temporary.cleanup()

    def _candidate(self, value: str, *, claimed_parent: str | None = None) -> World:
        root = self.store.roots()[0]
        root_key = root["root_key"]
        logical = bytes(root["path"])
        current_source = Path(os.fsdecode(os.path.realpath(logical)))
        base_directory = self.paths.worlds / "cand" / "base"
        candidate_directory = self.paths.worlds / "cand" / "payload"
        base_directory.parent.mkdir(mode=0o700, parents=True)
        current_manifest = Manifest.capture(current_source, logical_root=logical, root_key=root_key, kind=root["kind"], core=self.core)
        Manifest.materialize(current_manifest, current_source, base_directory / root_key, core=self.core)
        Manifest.materialize(current_manifest, current_source, candidate_directory / root_key, core=self.core)
        (candidate_directory / root_key / "state.txt").write_text(value, encoding="utf-8")
        base_manifest = Manifest.capture(base_directory / root_key, logical_root=logical, root_key=root_key, kind=root["kind"], core=self.core)
        candidate_manifest = Manifest.capture(candidate_directory / root_key, logical_root=logical, root_key=root_key, kind=root["kind"], core=self.core)
        delta = Delta.compute_all({root_key: base_manifest}, {root_key: candidate_manifest}, self.core)
        parent = self.store.prime()
        world = World.create(
            alias="cand",
            parent_instance=parent.instance_id,
            parent_content=claimed_parent or parent.content_id,
            cause="set", actor="fixture",
            payload_path=candidate_directory, base_payload_path=base_directory,
            base_root=Manifest.root_set_hash([base_manifest], self.core),
            root_set_hash=parent.root_set_hash,
            mission_hash=hash_id(self.core.hash_bytes(value.encode("utf-8"))),
        )
        world.components = {
            **Manifest.component_roots([candidate_manifest], self.core),
            "environment": parent.components["environment"],
            "evidence": parent.components["evidence"],
        }
        world.delta_hash = delta.delta_hash
        world.delta = {**delta.value["summary"], "files": delta.value["operations"]}
        world.transition(WorldState.FINALIZING, self.core)
        world.establish_identity(self.core)
        world.transition(WorldState.VALID, self.core)
        self.store.insert_world(world)
        return world

    def test_forged_parent_claim_is_denied_by_the_kernel(self) -> None:
        forged = hash_id(bytes([7]) * 32)
        candidate = self._candidate("forged", claimed_parent=forged)
        with self.assertRaises(ConflictError) as caught:
            self.transaction.prepare(candidate.alias)
        self.assertEqual(caught.exception.details["decision"], "PARENT_MISMATCH")
        self.assertEqual((self.work / "state.txt").read_text(encoding="utf-8"), "prime")

    def test_honest_parent_claim_is_authorized_and_recorded(self) -> None:
        candidate = self._candidate("honest")
        prepared = self.transaction.prepare(candidate.alias)
        self.assertEqual(prepared.decision, "AUTHORIZED")
        self.assertEqual(prepared.candidate_alias, "cand")
        self.assertEqual(prepared.kind, "collapse")
        record = self.transaction._load_record(prepared.transaction_id)
        self.assertEqual(record["parentContentExpected"], self.store.prime().content_id)
        listing = self.transaction.listing()
        self.assertEqual([item["state"] for item in listing], ["PREPARED"])
        self.assertEqual(listing[0]["candidateAlias"], "cand")
        described = self.transaction.describe(prepared.transaction_id)
        self.assertEqual(described["decision"], "AUTHORIZED")
        self.assertNotIn("stagingPayload", described)
        # A denied record can never be driven to COMMITTED: the kernel refuses, and the runtime
        # table must agree (a disagreement is its own loud error).
        self.transaction._set_state(record, "DENIED", error={"code": "TEST"})
        with self.assertRaises(WorldlineError) as raised:
            self.transaction._set_state(record, "COMMITTED", committed=True)
        self.assertEqual(raised.exception.code, "INVALID_TRANSACTION_STATE")


class _FixtureDaemon:
    """A private daemon over a throwaway root and a scriptable generic adapter."""

    def __init__(
        self, test: unittest.TestCase, agent_source: str, *, project: dict | None = None, extra_agents: dict | None = None
    ) -> None:
        self.test = test
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-fixture-")
        root = Path(self.temporary.name)
        self.paths, self.env = _isolated_paths(root)
        self.work = root / "fixture"
        self.work.mkdir()
        (self.work / "prime.txt").write_text("prime", encoding="utf-8")
        agent_script = self.work / "fixture_agent.py"
        agent_script.write_text(agent_source, encoding="utf-8")
        if project is not None:
            (self.work / ".worldline.json").write_text(json.dumps(project), encoding="utf-8")
        config_dir = Path(self.env["XDG_CONFIG_HOME"]) / "worldline"
        config_dir.mkdir(mode=0o700)
        (config_dir / "config.json").write_text(json.dumps({
            "schemaVersion": 1,
            "readonlyHomePaths": [],
            "agentCommands": {
                "fixture": {
                    "argv": ["/usr/bin/python3", str(agent_script), "{workspace}", "{missionFile}", "{worldState}"],
                    "credentialMounts": [],
                    "eventFormat": "jsonl",
                },
                **(extra_agents or {}),
            },
            "ghosts": {"enabled": False, "agent": None},
        }), encoding="utf-8")
        os.chmod(config_dir / "config.json", 0o600)
        self.daemon_env = {
            **os.environ,
            **self.env,
            "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "runtime"),
            "PYTHONDONTWRITEBYTECODE": "1",
            "WORLDLINE_CORE_LIB": str(Path(__file__).resolve().parents[1] / "lib/libworldline_core.so"),
        }
        self.error_log = root / "worldlined.stderr"
        self.errors = self.error_log.open("wb")
        self.process = subprocess.Popen(
            [sys.executable, "-m", "worldline.daemon_main"],
            env=self.daemon_env, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=self.errors,
        )
        deadline = time.monotonic() + 15
        while not self.paths.socket.exists() and self.process.poll() is None and time.monotonic() < deadline:
            time.sleep(0.02)
        if self.process.poll() is not None or not self.paths.socket.exists():
            test.fail(self.error_log.read_text(encoding="utf-8", errors="replace"))
        self.client = DaemonClient(self.paths, timeout=120)

    def cli(self, *argv: str) -> subprocess.CompletedProcess:
        binary = Path(__file__).resolve().parents[1] / "cli/worldline"
        return subprocess.run([sys.executable, str(binary), *argv], env=self.daemon_env, capture_output=True, text=True, stdin=subprocess.DEVNULL)

    def close(self) -> None:
        if self.process.poll() is None:
            self.process.send_signal(signal.SIGTERM)
            self.process.wait(timeout=15)
        self.errors.close()
        if self.process.returncode != 0:
            self.test.fail(self.error_log.read_text(encoding="utf-8", errors="replace"))
        self.temporary.cleanup()


_QUICK_AGENT = """import json
from pathlib import Path
import sys
workspace = Path(sys.argv[1])
(workspace / 'candidate.txt').write_text('candidate', encoding='utf-8')
print(json.dumps({'type': 'tool-event', 'actor': 'fixture', 'path': str(workspace / 'candidate.txt'), 'line': 1}), flush=True)
"""

_SLOW_AGENT = """import json, time
from pathlib import Path
import sys
workspace = Path(sys.argv[1])
(workspace / 'partial.txt').write_text('partial', encoding='utf-8')
print(json.dumps({'type': 'tool-event', 'actor': 'fixture', 'path': str(workspace / 'partial.txt'), 'line': 1}), flush=True)
time.sleep(120)
"""


class PreparedTransactionBoundary(unittest.TestCase):
    """Review and commit refer to one prepared transaction; changed facts are refused."""

    def test_prepare_review_abort_and_changed_prime_refusal(self) -> None:
        fixture = _FixtureDaemon(self, _QUICK_AGENT)
        try:
            work, client = fixture.work, fixture.client
            client.request("init", {"roots": [str(work)], "kind": None, "primary": None, "confirmed": True})
            alpha = client.request("fork", {"name": "alpha", "mission": "add candidate", "agent": "fixture", "wait": True})
            self.assertEqual(alpha["state"], "VALID")

            # --prepare through the CLI leaves the transaction PREPARED and hands back the facts.
            prepared = fixture.cli("collapse", "alpha", "--prepare", "--json")
            self.assertEqual(prepared.returncode, 0, prepared.stderr)
            facts = json.loads(prepared.stdout)
            self.assertEqual(facts["decision"], "AUTHORIZED")
            self.assertEqual(facts["candidate_alias"], "alpha")
            self.assertEqual(facts["kind"], "collapse")
            self.assertEqual([op["pathDisplay"] for op in facts["delta"]["operations"]], ["candidate.txt"])
            self.assertEqual(facts["conflicts"], [])
            listed = client.request("transaction.list")
            self.assertEqual([(item["state"], item["candidateAlias"]) for item in listed], [("PREPARED", "alpha")])
            self.assertEqual(client.request("doctor", {})["openTransactions"][0]["transactionId"], facts["transaction_id"])

            # The root set is frozen while a review is open; abort releases it.
            with self.assertRaises(WorldlineError) as busy:
                client.request("root.add", {"roots": [str(work.parent / "other")], "kind": None, "primary": None, "confirmed": False})
            self.assertEqual(busy.exception.code, "ROOT_SET_BUSY")
            aborted = fixture.cli("transaction", "abort", facts["transaction_id"], "--json")
            self.assertEqual(aborted.returncode, 0, aborted.stderr)
            self.assertEqual(json.loads(aborted.stdout)["state"], "ABORTED")
            self.assertFalse((work / "candidate.txt").exists())
            self.assertEqual(client.request("doctor", {})["openTransactions"], [])

            # Prepare again, then change PRIME between review and commit: refused, nothing written.
            facts = json.loads(fixture.cli("collapse", "alpha", "--prepare", "--json").stdout)
            (work / "prime.txt").write_text("edited after review", encoding="utf-8")
            time.sleep(0.05)
            with self.assertRaises(WorldlineError) as changed:
                client.request("transaction.commit", {"transactionId": facts["transaction_id"]})
            self.assertEqual(changed.exception.code, "PRIME_CHANGED_AFTER_PREPARE")
            self.assertFalse((work / "candidate.txt").exists())
            self.assertEqual((work / "prime.txt").read_text(encoding="utf-8"), "edited after review")
            shown = client.request("transaction.show", {"transactionId": facts["transaction_id"]})
            self.assertEqual(shown["state"], "DENIED")
            self.assertEqual(shown["error"]["code"], "PRIME_CHANGED_AFTER_PREPARE")
            # The listing must survive a row whose error column is populated (a JSON blob).
            denied_rows = [item for item in client.request("transaction.list") if item["state"] == "DENIED"]
            self.assertEqual(denied_rows[0]["error"]["code"], "PRIME_CHANGED_AFTER_PREPARE")
            listed_cli = fixture.cli("transaction", "list", "--json")
            self.assertEqual(listed_cli.returncode, 0, listed_cli.stderr)
            # A denied transaction never commits, and a fresh review is the only way forward.
            with self.assertRaises(WorldlineError) as denied:
                client.request("transaction.commit", {"transactionId": facts["transaction_id"]})
            self.assertEqual(denied.exception.code, "TRANSACTION_DENIED")

            # Fresh prepare against the edited PRIME, commit once, duplicate commit refused.
            client.request("status")
            facts = json.loads(fixture.cli("collapse", "alpha", "--prepare", "--json").stdout)
            committed = fixture.cli("transaction", "commit", facts["transaction_id"], "--yes", "--json")
            self.assertEqual(committed.returncode, 0, committed.stderr)
            self.assertEqual(json.loads(committed.stdout)["state"], "COMMITTED")
            self.assertEqual((work / "candidate.txt").read_text(encoding="utf-8"), "candidate")
            with self.assertRaises(WorldlineError) as duplicate:
                client.request("transaction.commit", {"transactionId": facts["transaction_id"]})
            self.assertEqual(duplicate.exception.code, "INVALID_TRANSACTION_STATE")
            self.assertEqual(client.request("doctor", {})["receiptCoverage"]["state"], "OK")
            self.assertEqual(client.request("doctor", {})["storeIntegrity"]["state"], "OK")

            # Managed-root dry run: facts only, nothing moved.
            other = work.parent / "other"
            other.mkdir()
            dry = fixture.cli("root", "add", "--dry-run", "--json", str(other))
            self.assertEqual(dry.returncode, 0, dry.stderr)
            self.assertEqual(json.loads(dry.stdout)["state"], "DRY_RUN")
            self.assertEqual(json.loads(dry.stdout)["roots"][0]["path"], str(other))
            self.assertFalse(other.is_symlink())
            self.assertEqual(len(client.request("root.list")), 1)
        finally:
            fixture.close()


class CancellationAndFailedStart(unittest.TestCase):
    def test_cancel_stops_the_agent_and_records_it_honestly(self) -> None:
        project = {
            "schemaVersion": 1, "generated": [], "services": [],
            "checks": [{"id": "never-runs", "kind": "tests", "argv": ["/usr/bin/false"], "required": True, "format": "exit"}],
        }
        fixture = _FixtureDaemon(self, _SLOW_AGENT, project=project)
        try:
            work, client = fixture.work, fixture.client
            client.request("init", {"roots": [str(work)], "kind": None, "primary": None, "confirmed": True})
            world = client.request("fork", {"name": "slow", "mission": "sleep", "agent": "fixture", "wait": False})
            deadline = time.monotonic() + 20
            while time.monotonic() < deadline:
                jobs = [job for job in client.request("status")["jobs"] if job["world"] == world["instanceId"]]
                if jobs and jobs[0]["state"] == "RUNNING":
                    break
                time.sleep(0.1)
            else:
                self.fail("agent job never reached RUNNING")
            cancelled = fixture.cli("cancel", "slow", "--json")
            self.assertEqual(cancelled.returncode, 0, cancelled.stderr)
            self.assertEqual(len(json.loads(cancelled.stdout)["cancelled"]), 1)
            deadline = time.monotonic() + 60
            while time.monotonic() < deadline:
                shown = client.request("show", {"world": "slow"})
                if shown["state"] not in {"MUTABLE", "FINALIZING"}:
                    break
                time.sleep(0.2)
            self.assertEqual(shown["state"], "DEGRADED")
            checks = {item["id"]: item for item in shown["evidence"]["checks"]}
            self.assertEqual(checks["agent"]["status"], "FAIL")
            self.assertIn("USER_CANCELLED", checks["agent"]["reason"])
            self.assertEqual(checks["never-runs"]["status"], "UNASSESSED")
            job = next(job for job in client.request("status")["jobs"] if job["world"] == world["instanceId"])
            self.assertEqual(job["state"], "CANCELLED")
            self.assertEqual(job["error"]["code"], "USER_CANCELLED")
            self.assertFalse((work / "partial.txt").exists(), "cancelled work reached PRIME")
            with self.assertRaises(WorldlineError) as nothing:
                client.request("job.cancel", {"world": "slow"})
            self.assertEqual(nothing.exception.code, "NO_ACTIVE_JOB")
            self.assertEqual(client.request("doctor", {})["unsupervisedWorlds"], [])
        finally:
            fixture.close()

    def test_unauthenticated_adapter_is_refused_before_any_checkpoint(self) -> None:
        # The credential file is declared but absent: the adapter is installed and would start,
        # then die. fork and race must refuse at the prompt with ADAPTER_AUTH_UNAVAILABLE and
        # leave no world and no frozen generation behind; the adapters listing says why.
        locked = {
            "locked": {
                "argv": ["/usr/bin/true"],
                "credentialMounts": [{"source": "/nonexistent/worldline-locked-credential", "target": "/home/x/.locked"}],
                "eventFormat": "jsonl",
            }
        }
        fixture = _FixtureDaemon(self, _QUICK_AGENT, extra_agents=locked)
        try:
            work, client = fixture.work, fixture.client
            client.request("init", {"roots": [str(work)], "kind": None, "primary": None, "confirmed": True})
            generations_before = sorted(p.name for p in fixture.paths.generations.iterdir())
            with self.assertRaises(WorldlineError) as refused:
                client.request("fork", {"name": "locked-out", "mission": "x", "agent": "locked", "wait": False})
            self.assertEqual(refused.exception.code, "ADAPTER_AUTH_UNAVAILABLE")
            with self.assertRaises(WorldlineError) as race_refused:
                client.request("race", {"agents": ["fixture", "locked", "fixture"], "mission": "x", "detach": True})
            self.assertEqual(race_refused.exception.code, "ADAPTER_AUTH_UNAVAILABLE")
            self.assertEqual(sorted(p.name for p in fixture.paths.generations.iterdir()), generations_before)
            aliases = [w["alias"] for w in client.request("list")]
            self.assertNotIn("locked-out", aliases)
            self.assertEqual([a for a in aliases if a in ("alpha", "beta", "gamma")], [])
            adapters = {item["name"]: item for item in client.request("adapters", {})}
            self.assertEqual(adapters["locked"]["state"], "UNAVAILABLE")
            self.assertIn("locked-credential", adapters["locked"]["reason"])
            self.assertEqual(client.request("doctor", {})["unsupervisedWorlds"], [])
        finally:
            fixture.close()

    def test_unknown_adapter_leaks_no_checkpoint_and_failed_start_is_dead(self) -> None:
        fixture = _FixtureDaemon(self, _QUICK_AGENT)
        try:
            work, client = fixture.work, fixture.client
            client.request("init", {"roots": [str(work)], "kind": None, "primary": None, "confirmed": True})
            generations_before = sorted(p.name for p in fixture.paths.generations.iterdir())
            with self.assertRaises(WorldlineError) as unknown:
                client.request("fork", {"name": "ghostly", "mission": "x", "agent": "no-such-agent", "wait": False})
            self.assertEqual(unknown.exception.code, "UNKNOWN_ADAPTER")
            self.assertEqual(sorted(p.name for p in fixture.paths.generations.iterdir()), generations_before)
            self.assertEqual([w["alias"] for w in client.request("list") if w["alias"] == "ghostly"], [])

            # A world whose run fails after creation must end DEAD, not linger MUTABLE: break the
            # adapter binary between create and run by pointing the project at an invalid config.
            (work / ".worldline.json").write_text("{not json", encoding="utf-8")
            time.sleep(0.05)
            client.request("status")
            with self.assertRaises(WorldlineError) as broken:
                client.request("fork", {"name": "broken", "mission": "x", "agent": "fixture", "wait": True})
            self.assertEqual(broken.exception.code, "INVALID_PROJECT_CONFIG")
            shown = client.request("show", {"world": "broken"})
            self.assertEqual(shown["state"], "DEAD")
            self.assertEqual(shown["evidence"]["supervision"]["code"], "INVALID_PROJECT_CONFIG")
            self.assertEqual(client.request("doctor", {})["unsupervisedWorlds"], [])
            # And the root set is no longer held hostage by a phantom nonterminal world.
            (work / ".worldline.json").unlink()
            other = work.parent / "other"
            other.mkdir()
            with self.assertRaises(WorldlineError) as confirm:
                client.request("root.add", {"roots": [str(other)], "kind": None, "primary": None, "confirmed": False})
            self.assertEqual(confirm.exception.code, "CONFIRMATION_REQUIRED")
        finally:
            fixture.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
