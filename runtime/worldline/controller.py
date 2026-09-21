from __future__ import annotations

import logging

import asyncio
import base64
from dataclasses import asdict
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any, Callable
import uuid

from .agents import adapter_names, adapter as resolve_adapter
from .agents.base import AgentContext
from .capabilities import CapabilityRegistry
from .checkpoint import CheckpointManager
from .config import GlobalConfig
from .core import Core
from .daemon import RequestContext, WorldlineDaemon
from .errors import InvalidRequest, WorldlineError
from .fork import ForkManager
from .ghosts import GhostManager
from .anchor import AnchorLedger
from .prune import Pruner, require_payload
from .linux.hyprland import HyprlandAdapter
from .linux.inotify import InotifyWatcher
from .linux.namespaces import BubblewrapSandbox
from .linux.systemd import SystemdAdapter
from .paths import WorldlinePaths
from .reconcile import PrimeChangeTracker
from .returning import ReturnManager
from .revalidate import Revalidator
from .validation import current_requirements, differences, effective_context, verify_context
from .roots import RootManager
from .runner import AgentRunner
from .simulation import SystemSimulation
from .store import StateStore
from .transaction import CollapseTransaction
from .causal import CausalIndexer
from .project import ProjectConfig

# A managed root is keyed by a 64-hex digest; other entries under a generation payload
# (notably `manifests/`) are structure, not captured roots.
_ROOT_KEY = re.compile(r"[0-9a-f]{64}")


_LOG = logging.getLogger("worldline.controller")

class RuntimeController:
    def __init__(
        self,
        paths: WorldlinePaths,
        store: StateStore,
        config: GlobalConfig,
        capabilities: CapabilityRegistry,
        *,
        core: Core | None = None,
    ) -> None:
        self.paths = paths
        self.store = store
        self.config = config
        self.capabilities = capabilities
        self.core = core or Core.shared()
        self.systemd = SystemdAdapter()
        self.sandbox = BubblewrapSandbox(paths)
        self.watcher: InotifyWatcher | None = None
        self.tracker: PrimeChangeTracker | None = None
        self._refresh_watcher()
        self.roots = RootManager(paths, store, core=self.core, watcher=self.watcher)
        self.checkpoint = CheckpointManager(
            paths,
            store,
            core=self.core,
            watcher=self.watcher,
            reconcile=self.roots.reconcile,
        )
        self.runner = AgentRunner(paths, store, config, self.sandbox, self.systemd, core=self.core)
        self.forks = ForkManager(paths, store, config, self.checkpoint, self.runner, core=self.core)
        self.anchors = AnchorLedger(paths, config.anchor_export_path)
        self.revalidator = Revalidator(paths, store, config, self.sandbox, self.runner.checks, core=self.core)
        self.transactions = CollapseTransaction(
            paths,
            store,
            core=self.core,
            watcher=self.watcher,
            reconcile=self.roots.reconcile,
            stop_writers=self._stop_writers,
            anchor=self.anchors,
            config=config,
            validator=self.revalidator.validate_staged,
        )
        self.pruner = Pruner(paths, store)
        restrictive = config.network_policy != "shared"
        self.runner.checks.network = "none" if restrictive else "shared"
        self.runner.services.network = "none" if restrictive else "shared"
        self.returns = ReturnManager(paths, store, self.checkpoint, self.transactions, core=self.core)
        self.simulation = SystemSimulation(paths, store, self.sandbox, self.systemd, core=self.core)
        self.ghosts = GhostManager(config, store)
        self._last_ghost_generation = self.store.get_meta("primeGeneration")
        # Receipts that predate the anchor ledger are anchored now, in chain order, so coverage
        # is complete from the first receipt rather than from the upgrade.
        try:
            rows = [self.store.receipt_for_transaction(row["transaction_id"]) for row in self.store.receipts()]
            self.anchors.backfill([row for row in rows if row is not None])
            if self.anchors.export_path is not None and self.anchors.ledger_path.is_file():
                exported = self.anchors.export()
                if exported.get("state") == "FAILED":
                    _LOG.warning("anchor export failed: %s", exported.get("reason"))
        except (WorldlineError, OSError) as exc:
            _LOG.warning("anchor backfill skipped: %s", exc)

    def _refresh_watcher(self) -> None:
        if self.watcher is not None:
            self.watcher.close()
            self.watcher = None
        roots = [
            (root["root_key"], os.path.realpath(bytes(root["path"])))
            for root in self.store.roots()
            if os.path.isdir(os.path.realpath(bytes(root["path"])))
        ]
        if roots:
            self.watcher = InotifyWatcher(roots, self._external_event)
            self.tracker = PrimeChangeTracker(self.store, self.watcher)
        else:
            self.tracker = None
        if hasattr(self, "roots"):
            self.roots.watcher = self.watcher
            self.checkpoint.watcher = self.watcher
            self.transactions.watcher = self.watcher

    def _external_event(self, event: dict[str, Any]) -> None:
        if self.tracker is not None:
            self.tracker.external_event(event)

    def close(self) -> None:
        if self.watcher is not None:
            self.watcher.close()

    def recover(self) -> dict[str, Any]:
        stopped = self.runner.services.stop_orphans()
        transactions = self.transactions.recover_all()
        return {"stoppedOrphanJobs": stopped, "transactions": transactions}

    def _stop_writers(self, world) -> None:
        active = [
            job
            for job in self.store.jobs()
            if job["world_instance"] == world.instance_id
            and job["state"] in {"STARTING", "RUNNING", "FINALIZING"}
        ]
        for job in active:
            unit = job.get("systemd_unit")
            if unit:
                self.systemd.stop(unit)
            self.store.update_job(
                job["job_id"],
                state="CANCELLED",
                error={"code": "COLLAPSE_STOPPED_WRITER", "message": "writer stopped before collapse"},
                ended=True,
            )

    def _schedule_automatic_ghosts(self, daemon: WorldlineDaemon) -> None:
        generation = self.store.get_meta("primeGeneration")
        if generation == self._last_ghost_generation:
            return
        self._last_ghost_generation = generation
        status = self.ghosts.status()
        if not status["enabled"] or generation is None:
            return
        frozen = self.checkpoint.freeze()
        for objective, mission in self.ghosts.missions.items():
            alias = f"ghost-{objective}-{str(uuid.uuid4())[:8]}"
            world = self.forks.create_world(alias, mission, status["agent"], frozen=frozen)
            world.evidence["ghostObjective"] = objective
            self.store.save_world(world)
            daemon.spawn_background(
                f"ghost:{world.instance_id}",
                asyncio.to_thread(self._run_ghost, world, mission, objective, None),
            )

    def register(self, daemon: WorldlineDaemon) -> None:
        daemon.register("init", self._register_roots, mutating=True)
        daemon.register("root.add", self._register_roots, mutating=True)
        daemon.register("root.remove", self._remove_root, mutating=True)
        daemon.register("root.list", self._root_list)
        daemon.register("fork", self._fork, mutating=True)
        daemon.register("race", self._race, mutating=True)
        daemon.register("graph", self._graph)
        daemon.register("log", self._log)
        daemon.register("why", self._why)
        daemon.register("inspect", self._inspect, mutating=True)
        daemon.register("switch", self._switch, mutating=True)
        daemon.register("collapse.prepare", self._collapse_prepare, mutating=True)
        daemon.register("collapse.commit", self._collapse_commit, mutating=True)
        daemon.register("transaction.commit", self._collapse_commit, mutating=True)
        daemon.register("transaction.abort", self._transaction_abort, mutating=True)
        daemon.register("transaction.list", self._transaction_list)
        daemon.register("transaction.show", self._transaction_show)
        daemon.register("return.prepare", self._return_prepare, mutating=True)
        daemon.register("job.cancel", self._job_cancel, mutating=True)
        daemon.register("simulate", self._simulate, mutating=True)
        daemon.register("doctor", self._doctor)
        daemon.register("adapters", self._adapters)
        daemon.register("ghost.enable", self._ghost_enable, mutating=True)
        daemon.register("ghost.disable", self._ghost_disable, mutating=True)
        daemon.register("ghost.status", self._ghost_status)
        daemon.register("ghost.run", self._ghost_run, mutating=True)
        daemon.register("shell.info", self._shell_info)
        daemon.register("prune", self._prune, mutating=True)
        daemon.register("anchor.status", self._anchor_status)
        daemon.register("revalidate", self._revalidate, mutating=True)
        daemon.register("validation.status", self._validation_status)

    def _register_roots(self, args: dict[str, Any], context: RequestContext) -> dict[str, Any]:
        allowed = {"roots", "kind", "primary", "confirmed"}
        if not set(args) <= allowed or not isinstance(args.get("roots"), list):
            raise InvalidRequest("init/root.add requires roots and optional kind, primary, confirmed")
        result = self.roots.register(
            args["roots"],
            kind=args.get("kind"),
            primary=args.get("primary"),
            confirmed=bool(args.get("confirmed", False)),
        )
        self._refresh_watcher()
        self._schedule_automatic_ghosts(context.daemon)
        return result

    def _remove_root(self, args: dict[str, Any], context: RequestContext) -> dict[str, Any]:
        if set(args) - {"root", "confirmed"} or not isinstance(args.get("root"), str):
            raise InvalidRequest("root.remove requires root and optional confirmed")
        result = self.roots.remove(args["root"], confirmed=bool(args.get("confirmed", False)))
        self._refresh_watcher()
        self._schedule_automatic_ghosts(context.daemon)
        return result

    def _root_list(self, args: dict[str, Any], _context: RequestContext) -> list[dict[str, Any]]:
        if args:
            raise InvalidRequest("root.list takes no arguments")
        return [
            {
                "rootKey": root["root_key"],
                "path": root["display_path"],
                "kind": root["kind"],
                "primary": bool(root["primary_root"]),
                "manifestRoot": root["manifest_root"],
            }
            for root in self.store.roots()
        ]

    @staticmethod
    def _thread_progress(context: RequestContext) -> Callable[[str, dict[str, Any]], None]:
        loop = asyncio.get_running_loop()

        def report(event: str, data: dict[str, Any]) -> None:
            asyncio.run_coroutine_threadsafe(context.progress(event, data), loop)

        return report

    @staticmethod
    def _timeout_argument(args: dict[str, Any]) -> float | None:
        timeout = args.get("timeoutSeconds")
        if timeout is None:
            return None
        if isinstance(timeout, bool) or not isinstance(timeout, int) or timeout <= 0:
            raise InvalidRequest("timeoutSeconds must be a positive integer")
        return float(timeout)

    async def _fork(self, args: dict[str, Any], context: RequestContext) -> dict[str, Any]:
        required = {"name", "mission", "agent", "wait"}
        if not required <= set(args) <= required | {"timeoutSeconds"} or not isinstance(args["wait"], bool):
            raise InvalidRequest("fork requires name, mission, agent, wait, and optional timeoutSeconds")
        timeout = self._timeout_argument(args)
        progress = self._thread_progress(context)
        if args["wait"]:
            world = await asyncio.to_thread(
                self.forks.fork,
                args["name"],
                args["mission"],
                args["agent"],
                wait=True,
                progress=progress,
                timeout=timeout,
            )
            self._schedule_automatic_ghosts(context.daemon)
            return world.summary()
        world = await asyncio.to_thread(self.forks.create_world, args["name"], args["mission"], args["agent"])
        self._schedule_automatic_ghosts(context.daemon)
        context.daemon.spawn_background(
            f"world:{world.instance_id}",
            asyncio.to_thread(self.forks.run_world, world, args["mission"], progress=progress, timeout=timeout),
        )
        return world.summary()

    async def _race(self, args: dict[str, Any], context: RequestContext) -> list[dict[str, Any]]:
        required = {"agents", "mission", "detach"}
        if not required <= set(args) <= required | {"name", "timeoutSeconds"} or not isinstance(args["agents"], list) or not isinstance(args["detach"], bool):
            raise InvalidRequest("race requires agents, mission, detach, and optional name and timeoutSeconds")
        name = args.get("name")
        if name is not None and not isinstance(name, str):
            raise InvalidRequest("race name must be a string")
        timeout = self._timeout_argument(args)
        progress = self._thread_progress(context)
        worlds = await asyncio.to_thread(
            self.forks.race,
            args["agents"],
            args["mission"],
            wait=not args["detach"],
            progress=progress,
            name=name,
            timeout=timeout,
        )
        self._schedule_automatic_ghosts(context.daemon)
        if args["detach"]:
            for world in worlds:
                context.daemon.spawn_background(
                    f"world:{world.instance_id}",
                    asyncio.to_thread(self.forks.run_world, world, args["mission"], progress=progress, timeout=timeout),
                )
        return [world.summary() for world in worlds]

    def _graph(self, args: dict[str, Any], _context: RequestContext) -> dict[str, Any]:
        if args:
            raise InvalidRequest("graph takes no arguments")
        worlds = self.store.worlds()
        return {
            "nodes": [world.summary() for world in worlds],
            "edges": [
                {"parent": world.parent_instance, "child": world.instance_id}
                for world in worlds
                if world.parent_instance is not None
            ],
        }

    def _log(self, args: dict[str, Any], _context: RequestContext) -> dict[str, Any]:
        if set(args) - {"verify"}:
            raise InvalidRequest("log accepts only verify")
        events = [
            event
            for world in self.store.worlds()
            for event in self.store.causal_events_for_world(world.instance_id)
        ]
        return {
            "events": [item["event"] for item in sorted(events, key=lambda value: value["ordinal"])],
            "receipts": [item["receipt"] for item in [self.store.receipt_for_transaction(row["transaction_id"]) for row in self.store.receipts()] if item],
            "verification": self.store.verify_chains() if args.get("verify") else None,
            "anchor": self.anchors.verify(receipts_known=len(self.store.receipts())) if args.get("verify") else None,
        }

    def _why(self, args: dict[str, Any], _context: RequestContext) -> dict[str, Any]:
        if set(args) != {"path", "line"} or not isinstance(args["path"], str) or not isinstance(args["line"], int):
            raise InvalidRequest("why requires path and line")
        return CausalIndexer(self.store).why(args["path"], args["line"])

    def _inspect(self, args: dict[str, Any], _context: RequestContext) -> dict[str, Any]:
        if set(args) != {"world"} or not isinstance(args["world"], str):
            raise InvalidRequest("inspect requires world")
        if args["world"] == "PRIME":
            world = self.store.prime()
            alias = "PRIME"
        else:
            world = self.store.world(args["world"])
            alias = world.alias
        if world is None:
            raise WorldlineError("NO_PRIME", "no PRIME is initialized")
        require_payload(world)
        self.store.set_meta("activeWorld", alias)
        return world.summary()

    def _switch(self, args: dict[str, Any], _context: RequestContext) -> dict[str, Any]:
        if set(args) != {"target"} or not isinstance(args["target"], str):
            raise InvalidRequest("switch requires target")
        worlds = [world for world in self.store.worlds() if not world.alias.startswith("prime-")]
        if not worlds:
            raise WorldlineError("NO_INSPECTABLE_WORLDS", "no alternate worlds exist")
        active = self.store.get_meta("activeWorld", "PRIME")
        aliases = [world.alias for world in worlds]
        if args["target"] in {"next", "previous"}:
            index = aliases.index(active) if active in aliases else (-1 if args["target"] == "next" else 0)
            offset = 1 if args["target"] == "next" else -1
            selected = worlds[(index + offset) % len(worlds)]
        else:
            selected = self.store.world(args["target"])
        hyprland = HyprlandAdapter()
        hyprland.focus_workspace(selected.instance_id)
        clients = hyprland.query("clients")
        app_id = f"worldline-{selected.instance_id}"
        exists = any(item.get("class") == app_id or item.get("initialClass") == app_id for item in clients)
        if not exists:
            terminal = shutil.which("xdg-terminal-exec")
            if terminal is None:
                raise WorldlineError("TERMINAL_UNAVAILABLE", "xdg-terminal-exec is not installed")
            subprocess.Popen(
                [
                    terminal,
                    f"--app-id={app_id}",
                    f"--title={selected.alias}/{selected.actor}",
                    "--",
                    "worldline",
                    "shell",
                    selected.alias,
                ],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                close_fds=True,
            )
        self.store.set_meta("activeWorld", selected.alias)
        return selected.summary()

    def _collapse_prepare(self, args: dict[str, Any], context: RequestContext) -> dict[str, Any]:
        if set(args) != {"world"} or not isinstance(args["world"], str):
            raise InvalidRequest("collapse.prepare requires world")
        prepared = self.transactions.prepare(args["world"])
        return {
            **asdict(prepared),
            "managedRoots": self._root_list({}, context),
        }

    def _collapse_commit(self, args: dict[str, Any], context: RequestContext) -> dict[str, Any]:
        if set(args) != {"transactionId"} or not isinstance(args["transactionId"], str):
            raise InvalidRequest("collapse.commit requires transactionId")
        transaction = self.store.transaction_record(args["transactionId"])
        result = self.transactions.commit(args["transactionId"])
        # The atomic exchange swapped the `live` mapping, so every inotify watch is now pinned
        # to the pre-collapse payload inodes. Rebuild the watcher against the new PRIME so the
        # PRIME_CHANGED_DURING_CAPTURE generation guard and dirty/reconcile tracking do not go
        # stale after the first collapse or return.
        self._refresh_watcher()
        if transaction["kind"] == "return":
            self._restart_return_context()
        self._schedule_automatic_ghosts(context.daemon)
        return result

    def _restart_return_context(self) -> None:
        prime = self.store.prime()
        if prime is None:
            return
        roots = self.store.roots()
        primary = next((root for root in roots if root["primary_root"]), None)
        if primary is None:
            return
        project = ProjectConfig.load(Path(os.fsdecode(bytes(primary["path"]))), self.store)
        self.runner.services.start_declared(prime, project)
        terminal = shutil.which("xdg-terminal-exec")
        for item in prime.workspace.get("ownedTerminals", []):
            if terminal is None or not isinstance(item, dict):
                break
            subprocess.Popen(
                [
                    terminal,
                    f"--app-id=worldline-{prime.instance_id}",
                    f"--title={item.get('title', 'PRIME')}",
                    "--",
                    "worldline",
                    "shell",
                    "PRIME",
                ],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                close_fds=True,
            )
        clients = prime.workspace.get("clients")
        if isinstance(clients, dict):
            clients = clients.get("value")
        if isinstance(clients, list):
            try:
                HyprlandAdapter().restore_live_clients(
                    HyprlandAdapter.workspace_name(prime.instance_id),
                    clients,
                )
            except WorldlineError:
                pass

    def _transaction_abort(self, args: dict[str, Any], _context: RequestContext) -> dict[str, str]:
        if set(args) != {"transactionId"} or not isinstance(args["transactionId"], str):
            raise InvalidRequest("transaction.abort requires transactionId")
        return self.transactions.abort(args["transactionId"])

    def _transaction_list(self, args: dict[str, Any], _context: RequestContext) -> list[dict[str, Any]]:
        if args:
            raise InvalidRequest("transaction.list takes no arguments")
        return self.transactions.listing()

    def _transaction_show(self, args: dict[str, Any], context: RequestContext) -> dict[str, Any]:
        if set(args) != {"transactionId"} or not isinstance(args["transactionId"], str):
            raise InvalidRequest("transaction.show requires transactionId")
        return {
            **self.transactions.describe(args["transactionId"]),
            "managedRoots": self._root_list({}, context),
        }

    def _job_cancel(self, args: dict[str, Any], _context: RequestContext) -> dict[str, Any]:
        if set(args) != {"world"} or not isinstance(args["world"], str):
            raise InvalidRequest("job.cancel requires world")
        world = self.store.world(args["world"])
        active = self.store.active_jobs_for_world(world.instance_id)
        if not active:
            raise WorldlineError(
                "NO_ACTIVE_JOB",
                f"world {world.alias} has no running agent job to cancel",
                {"world": world.alias, "state": world.state.value},
            )
        cancelled: list[dict[str, Any]] = []
        for job in active:
            self.runner.cancel(job["job_id"], job.get("systemd_unit"))
            cancelled.append({"jobId": job["job_id"], "unit": job.get("systemd_unit"), "state": job["state"]})
        return {"world": world.alias, "cancelled": cancelled}

    def _return_prepare(self, args: dict[str, Any], context: RequestContext) -> dict[str, Any]:
        if set(args) != {"world"} or not (args["world"] is None or isinstance(args["world"], str)):
            raise InvalidRequest("return.prepare requires nullable world")
        selected = self.returns.select(args["world"])
        candidate = self.returns.prepare_candidate(selected)
        prepared = self.transactions.prepare(candidate.instance_id, kind="return", return_of=selected.instance_id)
        return {
            **asdict(prepared),
            "returnWorld": selected.alias,
            "managedRoots": self._root_list({}, context),
        }

    async def _simulate(self, args: dict[str, Any], context: RequestContext) -> dict[str, Any]:
        if set(args) != {"argv"} or not isinstance(args["argv"], list):
            raise InvalidRequest("simulate requires argv")
        roots = self.store.roots()
        primary = next((root for root in roots if root["primary_root"]), None)
        project = ProjectConfig(generated=(), checks=(), services=()) if primary is None else ProjectConfig.load(Path(os.fsdecode(bytes(primary["path"]))), self.store)
        health = [
            {"id": check.id, "kind": check.kind, "argv": list(check.argv), "required": check.required}
            for check in project.checks
            if check.kind == "health"
        ]
        world = await asyncio.to_thread(self.simulation.run, args["argv"], health_checks=health)
        return world.summary()

    def _revalidate(self, args: dict[str, Any], _context: RequestContext) -> dict[str, Any]:
        if set(args) != {"world"} or not isinstance(args["world"], str):
            raise InvalidRequest("revalidate requires world")
        return self.revalidator.revalidate(args["world"])

    def _validation_status(self, args: dict[str, Any], _context: RequestContext) -> dict[str, Any]:
        if set(args) != {"world"} or not isinstance(args["world"], str):
            raise InvalidRequest("validation requires world")
        world = self.store.world(args["world"])
        context, source = effective_context(self.store, world)
        current: dict[str, Any] | None
        try:
            current = current_requirements(self.store, self.config, self.core)
        except WorldlineError as exc:
            current = None
            current_error = exc.as_dict()
        else:
            current_error = None
        problems: list[str] = []
        try:
            verify_context(context, candidate_instance=world.instance_id, core=self.core)
        except WorldlineError as exc:
            problems.append(exc.code)
        fresh = bool(context and current and not problems and context.get("requirementHash") == current["requirementHash"] and not context.get("verifiersModifiedByCandidate"))
        history = self.store.get_meta(f"validation:{world.instance_id}", []) or []
        return {
            "world": world.alias,
            "instanceId": world.instance_id,
            "state": world.state.value,
            "fresh": fresh,
            "effective": None if context is None else {
                "source": source,
                "requirementHash": context.get("requirementHash"),
                "contextHash": context.get("contextHash"),
                "evaluatedAt": context.get("evaluatedAt"),
                "verifiersModifiedByCandidate": context.get("verifiersModifiedByCandidate", []),
                "results": context.get("results", []),
            },
            "problems": problems,
            "current": None if current is None else {"requirementHash": current["requirementHash"], "policySourceSha256": current["policy"].get("sourceSha256"), "checks": [c["id"] for c in current["policy"].get("checks", [])], "protected": current["policy"].get("protected", [])},
            "currentError": current_error,
            "differences": [] if not (context and current and isinstance(context.get("requirement"), dict)) else differences(context["requirement"], current),
            "revalidations": [{"validationId": e.get("validationId"), "outcome": e.get("outcome"), "evaluatedAt": e.get("evaluatedAt"), "requirementHash": e.get("requirementHash"), "boundToCurrentContent": e.get("worldContentId") == world.content_id} for e in history],
        }

    def _doctor(self, args: dict[str, Any], _context: RequestContext) -> dict[str, Any]:
        if set(args) - {"refresh"}:
            raise InvalidRequest("doctor accepts only refresh")
        snapshot = self.capabilities.snapshot(refresh=bool(args.get("refresh", False)))
        snapshot["rootIntegrity"] = self._root_integrity()
        snapshot["storeIntegrity"] = self._store_integrity()
        snapshot["receiptCoverage"] = self._receipt_coverage()
        snapshot["recovery"] = self._recovery_report()
        snapshot["openTransactions"] = self._open_transactions()
        snapshot["unsupervisedWorlds"] = self._unsupervised_worlds()
        snapshot["storeUsage"] = self.pruner.usage()
        snapshot["networkPolicy"] = {"policy": self.config.network_policy, "allow": list(self.config.network_allow)}
        snapshot["limits"] = {"defaultTimeoutSeconds": self.config.default_timeout_seconds}
        try:
            current = current_requirements(self.store, self.config, self.core)
            snapshot["policy"] = {"requirementHash": current["requirementHash"], "policySourceSha256": current["policy"].get("sourceSha256"), "checks": [c["id"] for c in current["policy"].get("checks", [])], "protected": current["policy"].get("protected", []), "verifiers": [f"{v['rootKey'][:12]}:{v['path']}" for v in current.get("verifiers", [])]}
        except WorldlineError as exc:
            snapshot["policy"] = {"requirementHash": None, "error": exc.code}
        anchor = self.anchors.verify(receipts_known=len(self.store.receipts()))
        snapshot["anchor"] = {
            "state": anchor["state"],
            "entries": anchor["entries"],
            "head": anchor["head"],
            "unanchoredReceipts": anchor.get("unanchoredReceipts", 0),
            "attest": anchor["attest"]["state"],
            "external": anchor["external"]["state"],
            "exportPath": None if self.anchors.export_path is None else str(self.anchors.export_path),
        }
        return snapshot

    def _prune(self, args: dict[str, Any], _context: RequestContext) -> dict[str, Any]:
        allowed = {"olderThanDays", "keep", "logs", "dryRun", "confirmed"}
        if not set(args) <= allowed:
            raise InvalidRequest("prune accepts olderThanDays, keep, logs, dryRun, and confirmed")
        for key in ("olderThanDays", "keep"):
            value = args.get(key)
            if value is not None and (isinstance(value, bool) or not isinstance(value, int) or value < 0):
                raise InvalidRequest(f"{key} must be null or a non-negative integer")
        plan = self.pruner.plan(
            older_than_days=args.get("olderThanDays"),
            keep=args.get("keep"),
            logs=bool(args.get("logs", False)),
        )
        if args.get("dryRun", False) or not args.get("confirmed", False):
            return {"state": "DRY_RUN", **plan}
        result = self.pruner.apply(plan)
        return {"state": "PRUNED", **result, "plan": plan}

    def _anchor_status(self, args: dict[str, Any], _context: RequestContext) -> dict[str, Any]:
        if args:
            raise InvalidRequest("anchor.status takes no arguments")
        return self.anchors.verify(receipts_known=len(self.store.receipts()))

    def _recovery_report(self) -> dict[str, Any]:
        # A quarantined transaction blocks every mutation (prepare/commit refuse with
        # RECOVERY_INCOMPLETE) but used to be invisible to doctor; the operator only learned of it
        # from the refusal. Report it where the rest of the integrity picture lives.
        quarantined = dict(getattr(self.transactions, "unrecoverable", {}) or {})
        return {
            "state": "OK" if not quarantined else "INCOMPLETE",
            "quarantined": [
                {"transactionId": transaction_id, "error": error}
                for transaction_id, error in sorted(quarantined.items())
            ],
        }

    def _open_transactions(self) -> list[dict[str, Any]]:
        # A PREPARED transaction holds a staged PRIME-sized payload and blocks root-set changes
        # (ROOT_SET_BUSY) until it is committed or aborted. A review screen that was closed
        # without either leaves one behind; list them so the operator can abort deliberately.
        return [
            item
            for item in self.transactions.listing()
            if item["state"] in {"PREPARED", "AUTHORIZED"}
        ]

    def _unsupervised_worlds(self) -> list[dict[str, Any]]:
        # After the startup sweep this should be empty; if it is not, something created a
        # nonterminal world during this daemon's life and never gave it a job.
        result: list[dict[str, Any]] = []
        for world in self.store.nonterminal_worlds():
            if self.store.active_jobs_for_world(world.instance_id):
                continue
            result.append({"alias": world.alias, "instanceId": world.instance_id, "state": world.state.value, "born": world.born})
        return result

    def _store_integrity(self) -> dict[str, Any]:
        # Registration moves the operator's real directory into the store before any row records
        # where it came from, and the rollbacks are exception-only, so a SIGKILL or power loss
        # can leave the data present but unreferenced. Nothing else scans for that, which made
        # the worst outcome — "my project directory is gone" — completely silent. Report it.
        findings: list[dict[str, Any]] = []
        try:
            # A world references two payloads: the one it produced (payload_path) and the frozen
            # checkpoint it was forked from (base_payload_path). Scanning only the first made every
            # fork checkpoint look orphaned the moment its root was removed -- the health check's
            # final doctor reported DEGRADED over its own perfectly retained history.
            referenced_payloads: set[str] = set()
            for world in self.store.worlds():
                for reference in (world.payload_path, world.base_payload_path):
                    if reference:
                        referenced_payloads.add(os.path.realpath(str(Path(reference))))
        except Exception:  # pragma: no cover - diagnosis must never raise
            referenced_payloads = set()
        root_keys = {root["root_key"] for root in self.store.roots()}

        for generation in sorted(self.paths.generations.glob("*/payload/*")):
            if not generation.is_dir():
                continue
            # Only root-key directories are captured roots; `manifests/` is a legitimate sibling
            # holding each root's manifest JSON, and reporting it would be a false alarm.
            if not _ROOT_KEY.fullmatch(generation.name):
                continue
            if generation.name in root_keys:
                continue
            if os.path.realpath(str(generation)) in referenced_payloads:
                continue
            if os.path.realpath(str(generation.parent)) in referenced_payloads:
                continue
            entry: dict[str, Any] = {
                "kind": "ORPHANED_GENERATION",
                "path": str(generation),
                "reason": "captured payload is referenced by no managed root and no world",
            }
            # register() writes manifests/<root_key>.json before the rename, so the operator's
            # original path is recoverable from disk even when no database row survived.
            manifest = generation.parent / "manifests" / f"{generation.name}.json"
            origin = self._manifest_origin(manifest)
            if origin is not None:
                entry["originalPath"] = origin
            findings.append(entry)

        for mapping in sorted(self.paths.live.glob("*")):
            if mapping.name not in root_keys and mapping.name != ".worldline-generation.json":
                findings.append({
                    "kind": "ORPHANED_LIVE_MAPPING",
                    "path": str(mapping),
                    "reason": "live mapping entry matches no managed root",
                })

        known = {row["transaction_id"] for row in self.store.transactions_in_state(
            ("PREPARED", "AUTHORIZED", "COMMITTED", "DENIED", "ABORTED")
        )}
        for record in sorted(self.paths.transactions.glob("*.json")):
            if record.stem not in known:
                findings.append({
                    "kind": "ORPHANED_PREPARED_RECORD",
                    "path": str(record),
                    "reason": "prepared transaction record has no database row; its staged payload is unreclaimed",
                })

        return {"state": "OK" if not findings else "DEGRADED", "findings": findings}

    @staticmethod
    def _manifest_origin(manifest: Path) -> str | None:
        try:
            value = json.loads(manifest.read_text(encoding="utf-8"))
            encoded = value.get("rootPathB64")
            if isinstance(encoded, str):
                return os.fsdecode(base64.b64decode(encoded.encode("ascii"), validate=True))
        except Exception:  # pragma: no cover - best effort only
            return None
        return None

    def _receipt_coverage(self) -> dict[str, Any]:
        # "Every committed collapse has a receipt in a tamper-evident chain" is the system's
        # central evidence claim, and log --verify cannot detect a receipt that was never
        # written (the chain stays self-consistent, just shorter). Check it directly.
        missing = [
            row["transaction_id"]
            for row in self.store.transactions_in_state(("COMMITTED",))
            if self.store.receipt_for_transaction(row["transaction_id"]) is None
        ]
        return {
            "state": "OK" if not missing else "DEGRADED",
            "committedWithoutReceipt": missing,
        }

    def _root_integrity(self) -> dict[str, Any]:
        # A registered root is healthy only as a symlink chaining through paths.live:
        #   raw_path -> live/<root_key> -> generations/<gen>/payload/<root_key>
        # A crash during `root remove` can leave raw_path as a real directory that no longer
        # routes through live, after which collapses "commit" without touching the user's files.
        # That divergence is otherwise silent, so surface it here.
        roots: list[dict[str, Any]] = []
        healthy = True
        for root in self.store.roots():
            raw = os.fsdecode(bytes(root["path"]))
            expected = os.fsencode(self.paths.live / root["root_key"])
            state = "OK"
            detail: str | None = None
            if not os.path.islink(raw):
                state = "BROKEN"
                detail = (
                    "registered root is a real path, not a WORLDLINE symlink; collapses would "
                    "not reach the user's files (likely an interrupted `root remove`)"
                ) if os.path.exists(raw) else "registered root path is missing"
                healthy = False
            elif os.readlink(os.fsencode(raw)) != expected:
                state = "BROKEN"
                detail = "registered root symlink does not route through the live mapping"
                healthy = False
            roots.append({
                "path": root["display_path"],
                "rootKey": root["root_key"],
                "state": state,
                **({"reason": detail} if detail else {}),
            })
        return {"state": "OK" if healthy else "DEGRADED", "roots": roots}

    def _adapters(self, args: dict[str, Any], _context: RequestContext) -> list[dict[str, Any]]:
        if args:
            raise InvalidRequest("adapters takes no arguments")
        roots = self.store.roots()
        if roots:
            primary = next(root for root in roots if root["primary_root"])
            primary_path = Path(os.fsdecode(bytes(primary["path"])))
            is_git = primary["kind"] == "repo"
        else:
            primary_path = self.paths.home
            is_git = False
        context = AgentContext(
            primary_root=primary_path,
            workspace=primary_path,
            mission_file=Path("/run/worldline-runtime/mission.txt"),
            world_state=Path("/run/worldline-runtime/world.json"),
            home=self.paths.home,
            is_git_root=is_git,
        )
        result: list[dict[str, Any]] = []
        for name in adapter_names(self.config):
            try:
                selected = resolve_adapter(name, self.config)
                item = selected.capability(context)
                item["argvPreview"] = list(selected.build_argv(context, "<mission>"))
            except WorldlineError as exc:
                item = {"name": name, "state": "UNAVAILABLE", "reason": exc.message}
            result.append(item)
        return result

    def _ghost_enable(self, args: dict[str, Any], _context: RequestContext) -> dict[str, Any]:
        if set(args) != {"agent"} or not isinstance(args["agent"], str):
            raise InvalidRequest("ghost.enable requires agent")
        resolve_adapter(args["agent"], self.config)
        return self.ghosts.enable(args["agent"])

    def _ghost_disable(self, args: dict[str, Any], _context: RequestContext) -> dict[str, Any]:
        if args:
            raise InvalidRequest("ghost.disable takes no arguments")
        return self.ghosts.disable()

    def _ghost_status(self, args: dict[str, Any], _context: RequestContext) -> dict[str, Any]:
        if args:
            raise InvalidRequest("ghost.status takes no arguments")
        return self.ghosts.status()

    async def _ghost_run(self, args: dict[str, Any], context: RequestContext) -> dict[str, Any]:
        if set(args) != {"objective", "wait"} or not isinstance(args["objective"], str) or not isinstance(args["wait"], bool):
            raise InvalidRequest("ghost.run requires objective and wait")
        status = self.ghosts.status()
        if not status["enabled"]:
            raise WorldlineError("GHOSTS_DISABLED", "ghosts require explicit ghost enable --agent AGENT")
        try:
            mission = self.ghosts.missions[args["objective"]]
        except KeyError as exc:
            raise WorldlineError("UNKNOWN_GHOST", f"unknown ghost objective: {args['objective']}") from exc
        alias = f"ghost-{args['objective']}-{str(uuid.uuid4())[:8]}"
        world = await asyncio.to_thread(self.forks.create_world, alias, mission, status["agent"])
        world.evidence["ghostObjective"] = args["objective"]
        self.store.save_world(world)
        progress = self._thread_progress(context)
        if args["wait"]:
            completed = await asyncio.to_thread(
                self.forks.run_world,
                world,
                mission,
                progress=progress,
                low_priority=True,
            )
            parent = self.store.world(completed.parent_instance)
            self.ghosts.recommendation(args["objective"], completed, parent)
            return completed.summary()
        context.daemon.spawn_background(
            f"ghost:{world.instance_id}",
            asyncio.to_thread(self._run_ghost, world, mission, args["objective"], progress),
        )
        return world.summary()

    def _run_ghost(self, world, mission: str, objective: str, progress) -> None:
        completed = self.forks.run_world(world, mission, progress=progress, low_priority=True)
        parent = self.store.world(completed.parent_instance)
        self.ghosts.recommendation(objective, completed, parent)

    def _shell_info(self, args: dict[str, Any], _context: RequestContext) -> dict[str, Any]:
        if set(args) != {"world"} or not isinstance(args["world"], str):
            raise InvalidRequest("shell.info requires world")
        world = self.store.prime() if args["world"] == "PRIME" else self.store.world(args["world"])
        if world is None:
            raise WorldlineError("NO_PRIME", "no PRIME is initialized")
        require_payload(world)
        roots = self.store.roots()
        primary = next(root for root in roots if root["primary_root"])
        cwd = world.workspace.get("ownedTerminalCwd")
        if not isinstance(cwd, str) or not Path(cwd).is_dir():
            cwd = primary["display_path"]
        return {
            "world": world.summary(),
            "payload": world.payload_path,
            "cwd": cwd,
            "roots": [
                {"rootKey": root["root_key"], "target": root["display_path"]}
                for root in roots
            ],
        }
