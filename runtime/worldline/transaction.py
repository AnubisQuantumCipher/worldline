from __future__ import annotations

import base64
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import shutil
import uuid
from typing import Any, Callable, Mapping

from . import SCHEMA_VERSION
from .canonical import atomic_write_json, fsync_directory
from .core import CollapseInput, Core, hash_bytes_from_id, hash_id
from .delta import Delta
from .errors import ConflictError, WorldlineError
from .environment import capture_dependencies
from .linux.atomic import AtomicExchange
from .linux.git import GitAdapter
from .linux.inotify import InotifyWatcher
from .manifest import CapturedManifest, Manifest
from .model import TERMINAL_STATES, World, WorldState, utc_now
from .paths import WorldlinePaths, secure_directory
from .prime import Generation, PrimeManager
from .receipt import ReceiptBuilder
from .store import StateStore

_MARKER = ".worldline-generation.json"
_TRANSACTION_TRANSITIONS = {
    "PREPARED": {"AUTHORIZED", "DENIED", "ABORTED"},
    "AUTHORIZED": {"COMMITTED", "ABORTED"},
    "DENIED": {"ABORTED"},
    "COMMITTED": set(),
    "ABORTED": set(),
}


@dataclass(frozen=True, slots=True)
class PreparedTransaction:
    transaction_id: str
    decision: str
    before_root: str
    candidate_root: str
    staged_root: str
    delta: dict[str, Any]
    conflicts: list[dict[str, Any]]
    contamination: list[dict[str, Any]]
    kind: str = "collapse"
    candidate_alias: str = ""
    candidate_instance: str = ""
    candidate_content: str = ""
    current_prime: str = ""
    prepared_at: str = ""
    dependency_changes: list[dict[str, Any]] = field(default_factory=list)


class CollapseTransaction:
    def __init__(
        self,
        paths: WorldlinePaths,
        store: StateStore,
        *,
        core: Core | None = None,
        watcher: InotifyWatcher | None = None,
        reconcile: Callable[[], Any] | None = None,
        stop_writers: Callable[[World], None] | None = None,
    ) -> None:
        self.paths = paths
        self.store = store
        self.core = core or Core.shared()
        self.watcher = watcher
        self.reconcile_prime = reconcile
        self.stop_writers = stop_writers or self._require_no_writers
        self.atomic = AtomicExchange()
        self.git = GitAdapter(self.core)
        self.prime = PrimeManager(paths, store, self.core)
        self.receipts = ReceiptBuilder(store, self.core)
        self.data_transactions = self.paths.data / "transactions"
        secure_directory(self.data_transactions)
        # transaction_id -> error dict for transactions recovery could not resolve; populated by
        # recover_all and consulted by prepare()/commit() so a quarantined transaction blocks
        # mutation without blocking diagnosis.
        self.unrecoverable: dict[str, dict[str, Any]] = {}

    def _require_no_writers(self, world: World) -> None:
        active = [
            job["job_id"]
            for job in self.store.jobs()
            if job["world_instance"] == world.instance_id
            and job["state"] in {"STARTING", "RUNNING", "FINALIZING"}
        ]
        if active:
            raise WorldlineError(
                "WRITERS_ACTIVE",
                "WORLDLINE-owned writers must stop before atomic collapse",
                {"jobs": active},
            )

    def prepare(self, candidate_value: str, *, kind: str = "collapse") -> PreparedTransaction:
        self._assert_recovery_complete()
        if kind not in {"collapse", "return"}:
            raise WorldlineError("INVALID_TRANSACTION", f"unsupported transaction kind: {kind}")
        if self.reconcile_prime is not None and self.store.get_meta("dirty", False):
            self.reconcile_prime()
        candidate = self.store.world(candidate_value)
        if candidate.world_kind == "system":
            raise WorldlineError(
                "SYSTEM_ROOT_COLLAPSE_UNSUPPORTED",
                "system futures on this backend are inspectable but cannot collapse",
            )
        if candidate.state is not WorldState.VALID:
            raise WorldlineError(
                "INVALID_CANDIDATE",
                f"collapse requires a VALID candidate, got {candidate.state.value}",
            )
        if candidate.content_id is None or candidate.delta_hash is None:
            raise WorldlineError("INCOMPLETE_WORLD", "candidate identity or delta claim is missing")
        current_prime = self.store.prime()
        if current_prime is None or current_prime.content_id is None:
            raise WorldlineError("NO_PRIME", "no canonical PRIME is registered")
        if not self._is_ancestor(candidate.parent_instance, current_prime.instance_id):
            raise WorldlineError(
                "PARENT_MISMATCH",
                "candidate fork parent is not an ancestor of current PRIME",
                {"candidateParent": candidate.parent_instance, "prime": current_prime.instance_id},
            )
        # The kernel's parent check compares what the store knows the parent's content identity
        # to be against what the candidate row claims. Feeding the claim to both sides (as 1.0
        # did) made the proved comparison tautological.
        parent_world = self.store.world(candidate.parent_instance)
        if parent_world.content_id is None:
            raise WorldlineError("INCOMPLETE_WORLD", "candidate parent has no content identity")
        expected_parent_content = parent_world.content_id

        roots = self.store.roots()
        root_set = self.prime.root_set_hash(roots)
        transaction_id = str(uuid.uuid4())
        transaction_directory = self.data_transactions / transaction_id
        payload = transaction_directory / "payload"
        mapping = transaction_directory / "mapping"
        secure_directory(payload)
        secure_directory(mapping)
        before_generation = self.watcher.synchronized_generation() if self.watcher is not None else None

        base_manifests: dict[str, CapturedManifest] = {}
        current_manifests: dict[str, CapturedManifest] = {}
        candidate_manifests: dict[str, CapturedManifest] = {}
        staged_manifests: dict[str, CapturedManifest] = {}
        conflicts: list[dict[str, Any]] = []
        try:
            for root in roots:
                root_key = root["root_key"]
                logical = bytes(root["path"])
                base_source = os.fsencode(Path(candidate.base_payload_path) / root_key)
                candidate_source = os.fsencode(Path(candidate.payload_path) / root_key)
                current_source = os.path.realpath(logical)
                for label, source in (("base", base_source), ("candidate", candidate_source), ("current", current_source)):
                    if not os.path.isdir(source):
                        raise WorldlineError(
                            "INCOMPLETE_WORLD",
                            f"{label} payload is missing root {root_key}",
                            {"path": os.fsdecode(source)},
                        )
                base_manifest = self._capture_payload(source=base_source, logical=logical, root=root)
                current_manifest = self._capture(source=current_source, logical=logical, root=root)
                candidate_manifest = self._capture_payload(source=candidate_source, logical=logical, root=root)
                base_manifests[root_key] = base_manifest
                current_manifests[root_key] = current_manifest
                candidate_manifests[root_key] = candidate_manifest
                merge = Delta.merge(
                    base=base_manifest,
                    current=current_manifest,
                    candidate=candidate_manifest,
                    current_source=current_source,
                    candidate_source=candidate_source,
                    stage=payload / root_key,
                    core=self.core,
                    repository_capture=(
                        (lambda staged, adapter=self.git: adapter.capture(staged))
                        if root["kind"] == "repo"
                        else None
                    ),
                )
                conflicts.extend(merge.conflicts)
                if merge.staged is not None:
                    staged_manifests[root_key] = merge.staged

            if self.watcher is not None:
                after_generation = self.watcher.synchronized_generation()
                if before_generation != after_generation:
                    raise WorldlineError(
                        "PRIME_CHANGED_DURING_CAPTURE",
                        "PRIME changed while collapse staging was copied and hashed",
                        {"beforeGeneration": before_generation, "afterGeneration": after_generation},
                    )

            delta = Delta.compute_all(base_manifests, candidate_manifests, self.core)
            base_root = Manifest.root_set_hash(base_manifests.values(), self.core)
            before_root = Manifest.root_set_hash(current_manifests.values(), self.core)
            candidate_root = Manifest.root_set_hash(candidate_manifests.values(), self.core)
            staged_root = hash_id(bytes(32)) if conflicts else Manifest.root_set_hash(staged_manifests.values(), self.core)
            if not conflicts:
                self._create_mapping(mapping, payload, roots, transaction_id)

            owner = hash_id(self.core.hash_bytes(b"worldline-mutable-owner-v1" + candidate.instance_id.encode("ascii")))
            decision = self.core.collapse_decide(
                CollapseInput(
                    candidate_state=candidate.state.value,
                    has_conflicts=bool(conflicts),
                    has_foreign_managed_writes=bool(candidate.contamination),
                    expected_parent=hash_bytes_from_id(expected_parent_content),
                    candidate_parent=hash_bytes_from_id(candidate.parent_content),
                    expected_owner=hash_bytes_from_id(owner),
                    candidate_owner=hash_bytes_from_id(owner),
                    expected_base=hash_bytes_from_id(candidate.base_root),
                    candidate_base=hash_bytes_from_id(base_root),
                    expected_delta=hash_bytes_from_id(candidate.delta_hash),
                    candidate_delta=hash_bytes_from_id(delta.delta_hash),
                    expected_root_set=hash_bytes_from_id(root_set),
                    candidate_root_set=hash_bytes_from_id(candidate.root_set_hash),
                    expected_staged_root=hash_bytes_from_id(staged_root),
                    actual_staged_root=hash_bytes_from_id(staged_root),
                )
            )
            generated = candidate.evidence.get("metrics", {}).get("generatedClassifiers", [])
            if not isinstance(generated, list):
                generated = []
            dependency_changes = self._dependency_changes(candidate, roots)
            record = {
                "schemaVersion": SCHEMA_VERSION,
                "transactionId": transaction_id,
                "kind": kind,
                "state": "PREPARED" if decision == "AUTHORIZED" else "DENIED",
                "decision": decision,
                "candidateWorld": candidate.instance_id,
                "candidateAlias": candidate.alias,
                "candidateContent": candidate.content_id,
                "parentWorld": candidate.parent_content,
                "parentContentExpected": expected_parent_content,
                "currentPrime": current_prime.instance_id,
                "currentPrimeContent": current_prime.content_id,
                "beforeRoot": before_root,
                "baseRoot": base_root,
                "candidateRoot": candidate_root,
                "deltaHash": delta.delta_hash,
                "delta": {**delta.value, "deltaHash": delta.delta_hash, "baseRoot": base_root},
                "stagedRoot": staged_root,
                "rootSetHash": root_set,
                "ownerHash": owner,
                "conflicts": conflicts,
                "contamination": candidate.contamination,
                "stagingPayload": str(payload),
                "preparedMapping": str(mapping),
                "generationMarker": transaction_id,
                "createdAt": utc_now(),
                "generated": generated,
                "dependencyChanges": dependency_changes,
            }
            state_path = self.paths.transactions / f"{transaction_id}.json"
            record["preparedPath"] = str(state_path)
            atomic_write_json(state_path, record)
            self.store.create_transaction(record)
            if decision != "AUTHORIZED":
                # A denied transaction is terminal and its staged payload (a full PRIME-sized
                # copy) will never be used; drop it now so repeated conflicted collapses do not
                # grow the store without bound. The signed transaction record itself is kept.
                shutil.rmtree(transaction_directory, ignore_errors=True)
                raise ConflictError(
                    f"collapse denied: {decision}",
                    transactionId=transaction_id,
                    decision=decision,
                    conflicts=conflicts,
                    contamination=candidate.contamination,
                )
            return PreparedTransaction(
                transaction_id=transaction_id,
                decision=decision,
                before_root=before_root,
                candidate_root=candidate_root,
                staged_root=staged_root,
                delta=record["delta"],
                conflicts=conflicts,
                contamination=candidate.contamination,
                kind=kind,
                candidate_alias=candidate.alias,
                candidate_instance=candidate.instance_id,
                candidate_content=candidate.content_id,
                current_prime=current_prime.instance_id,
                prepared_at=record["createdAt"],
                dependency_changes=dependency_changes,
            )
        except BaseException:
            if not (self.paths.transactions / f"{transaction_id}.json").exists():
                shutil.rmtree(transaction_directory, ignore_errors=True)
            raise

    def abort(self, transaction_id: str) -> dict[str, str]:
        record = self._load_record(transaction_id)
        if record["state"] not in {"PREPARED", "AUTHORIZED", "DENIED"}:
            raise WorldlineError("INVALID_TRANSACTION_STATE", f"cannot abort transaction in {record['state']}")
        if self._marker(self.paths.live) == transaction_id:
            raise WorldlineError("TRANSACTION_ALREADY_COMMITTED", "generation marker shows the atomic exchange already committed")
        self._set_state(record, "ABORTED", error={"code": "USER_ABORTED"})
        return {"transactionId": transaction_id, "state": "ABORTED"}

    def describe(self, transaction_id: str) -> dict[str, Any]:
        """The prepared record as the operator may review it (no staging paths or payload bytes)."""
        row = self.store.transaction_record(transaction_id)
        try:
            record = self._load_record(transaction_id)
        except WorldlineError as exc:
            return {
                "transactionId": transaction_id,
                "kind": row["kind"],
                "state": row["state"],
                "error": exc.as_dict(),
                "recordReadable": False,
            }
        public = {
            key: record.get(key)
            for key in (
                "transactionId", "kind", "state", "decision", "candidateWorld", "candidateAlias",
                "candidateContent", "parentWorld", "parentContentExpected", "currentPrime",
                "currentPrimeContent", "beforeRoot", "baseRoot", "candidateRoot", "deltaHash",
                "delta", "stagedRoot", "rootSetHash", "conflicts", "contamination", "createdAt",
                "generated", "dependencyChanges", "error",
            )
        }
        public["committedAt"] = row.get("committed_at")
        public["recordReadable"] = True
        return public

    def listing(self) -> list[dict[str, Any]]:
        rows = self.store.transactions_in_state(("PREPARED", "AUTHORIZED", "DENIED", "COMMITTED", "ABORTED"))
        result: list[dict[str, Any]] = []
        for row in rows:
            try:
                alias = self.store.world(row["candidate_world"]).alias
            except WorldlineError:
                alias = None
            error = row["error"]
            if isinstance(error, (bytes, bytearray)):
                # The column is a canonical-JSON blob; the wire format only carries JSON values.
                try:
                    error = json.loads(bytes(error).decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    error = {"code": "UNREADABLE_ERROR"}
            result.append(
                {
                    "transactionId": row["transaction_id"],
                    "kind": row["kind"],
                    "state": row["state"],
                    "candidateWorld": row["candidate_world"],
                    "candidateAlias": alias,
                    "createdAt": row["created_at"],
                    "committedAt": row["committed_at"],
                    "error": error,
                    "quarantined": row["transaction_id"] in self.unrecoverable,
                }
            )
        return result

    def commit(self, transaction_id: str) -> dict[str, Any]:
        self._assert_recovery_complete()
        record = self._load_record(transaction_id)
        if record["state"] == "DENIED":
            raise WorldlineError("TRANSACTION_DENIED", "a denied transaction can never commit")
        if record["state"] != "PREPARED":
            raise WorldlineError("INVALID_TRANSACTION_STATE", f"cannot commit transaction in {record['state']}")
        candidate = self.store.world(record["candidateWorld"])
        self.stop_writers(candidate)
        before_generation = self.watcher.synchronized_generation() if self.watcher is not None else None
        current_manifests = self._capture_current_roots()
        if Manifest.root_set_hash(current_manifests.values(), self.core) != record["beforeRoot"]:
            self._set_state(record, "DENIED", error={"code": "PRIME_CHANGED_AFTER_PREPARE"})
            raise WorldlineError(
                "PRIME_CHANGED_AFTER_PREPARE",
                "PRIME changed after collapse preparation; prepare again",
            )
        staged_manifests = self._capture_staged(record)
        staged_root = Manifest.root_set_hash(staged_manifests.values(), self.core)
        if staged_root != record["stagedRoot"]:
            self._set_state(record, "DENIED", error={"code": "STAGED_ROOT_MISMATCH"})
            raise WorldlineError("STAGED_ROOT_MISMATCH", "staged collapse payload changed after preparation")
        if self.watcher is not None and before_generation != self.watcher.synchronized_generation():
            self._set_state(record, "DENIED", error={"code": "PRIME_CHANGED_DURING_CAPTURE"})
            raise WorldlineError("PRIME_CHANGED_DURING_CAPTURE", "PRIME changed during collapse authorization")

        decision = self._authorize(record, candidate, staged_root)
        if decision != "AUTHORIZED":
            self._set_state(record, "DENIED", error={"code": decision})
            raise WorldlineError(decision, f"proved core denied collapse: {decision}")
        self._set_state(record, "AUTHORIZED")
        # File contents were fsynced during staging, but the directory entries that link them
        # into the payload tree were not. Flush every staged directory before the exchange so a
        # power loss immediately after the (durable) rename cannot leave PRIME pointing at a tree
        # whose dirents never reached disk — recovery re-hashes survivors and would enshrine a
        # torn tree as COMMITTED otherwise.
        self._fsync_payload_tree(Path(record["stagingPayload"]))
        exchanged = False
        try:
            context = self.watcher.owned_writes() if self.watcher is not None else _NullContext()
            with context:
                self.atomic.exchange(self.paths.live, Path(record["preparedMapping"]))
            exchanged = True
            return self._finish_committed(record, staged_manifests)
        except BaseException:
            if not exchanged:
                self._set_state(record, "ABORTED", error={"code": "ATOMIC_EXCHANGE_FAILED"})
            raise

    def _authorize(self, record: dict[str, Any], candidate: World, staged_root: str) -> str:
        # Records prepared before parentContentExpected existed carry only the claim; for those
        # the comparison degrades to the 1.0 behaviour rather than failing recovery outright.
        expected_parent = record.get("parentContentExpected") or record["parentWorld"]
        return self.core.collapse_decide(
            CollapseInput(
                candidate_state=candidate.state.value,
                has_conflicts=bool(record["conflicts"]),
                has_foreign_managed_writes=bool(record["contamination"]),
                expected_parent=hash_bytes_from_id(expected_parent),
                candidate_parent=hash_bytes_from_id(candidate.parent_content),
                expected_owner=hash_bytes_from_id(record["ownerHash"]),
                candidate_owner=hash_bytes_from_id(record["ownerHash"]),
                expected_base=hash_bytes_from_id(candidate.base_root),
                candidate_base=hash_bytes_from_id(record["baseRoot"]),
                expected_delta=hash_bytes_from_id(candidate.delta_hash or hash_id(bytes(32))),
                candidate_delta=hash_bytes_from_id(record["deltaHash"]),
                expected_root_set=hash_bytes_from_id(record["rootSetHash"]),
                candidate_root_set=hash_bytes_from_id(candidate.root_set_hash),
                expected_staged_root=hash_bytes_from_id(record["stagedRoot"]),
                actual_staged_root=hash_bytes_from_id(staged_root),
            )
        )

    def _finish_committed(
        self,
        record: dict[str, Any],
        staged_manifests: Mapping[str, CapturedManifest] | None = None,
    ) -> dict[str, Any]:
        candidate = self.store.world(record["candidateWorld"])
        manifests = dict(staged_manifests or self._capture_staged(record))
        manifests_directory = Path(record["stagingPayload"]) / "manifests"
        manifests_directory.mkdir(mode=0o700, exist_ok=True)
        for root_key, manifest in manifests.items():
            manifest.save(manifests_directory / f"{root_key}.json")
        candidate_state = Path(candidate.payload_path) / "manifests"
        for name in ("environment.json", "evidence.json", "agent.json"):
            source = candidate_state / name
            if source.is_file():
                shutil.copy2(source, manifests_directory / name)
        for root in self.store.roots():
            self.store.update_root_generation(
                root["root_key"], record["transactionId"], manifests[root["root_key"]].root_hash
            )
        if candidate.state is WorldState.VALID:
            candidate.transition(WorldState.COLLAPSED, self.core)
            self.store.save_world(candidate)
        elif candidate.state is not WorldState.COLLAPSED:
            raise WorldlineError("RECOVERY_STATE_MISMATCH", f"candidate is {candidate.state.value} after committed exchange")
        for sibling in self.store.terminal_siblings(candidate):
            if sibling.state in (WorldState.VALID, WorldState.DEGRADED, WorldState.DEAD, WorldState.COLLAPSED):
                sibling.transition(WorldState.ARCHIVED, self.core)
                self.store.save_world(sibling)

        if self.store.get_meta("primeGeneration") != record["transactionId"]:
            components = Manifest.component_roots(manifests.values(), self.core)
            current_prime = self.store.prime()
            if current_prime is None or current_prime.content_id is None:
                raise WorldlineError("RECOVERY_STATE_MISMATCH", "PRIME identity vanished after committed exchange")
            staged_identity = hash_id(
                self.core.world_id(
                    {
                        "parent": hash_bytes_from_id(current_prime.content_id),
                        "filesystem": hash_bytes_from_id(components["filesystem"]),
                        "config": hash_bytes_from_id(components["config"]),
                        "repository": hash_bytes_from_id(components["repository"]),
                        "environment": hash_bytes_from_id(candidate.components["environment"]),
                        "evidence": hash_bytes_from_id(candidate.components["evidence"]),
                    }
                )
            )
            if staged_identity == candidate.content_id:
                if current_prime.instance_id != candidate.instance_id and current_prime.state in (
                    WorldState.VALID,
                    WorldState.COLLAPSED,
                ):
                    current_prime.transition(WorldState.ARCHIVED, self.core)
                    self.store.save_world(current_prime)
                candidate.payload_path = record["stagingPayload"]
                self.store.save_world(candidate)
                self.store.set_prime(
                    candidate.instance_id,
                    candidate.content_id,
                    record["transactionId"],
                )
                self.store.set_meta("activeWorld", "PRIME")
            else:
                self.prime.publish_checkpoint(
                    generation=Generation(
                        generation_id=record["transactionId"],
                        payload=Path(record["stagingPayload"]),
                        root_set_hash=record["rootSetHash"],
                        state_root=record["stagedRoot"],
                        component_roots=components,
                    ),
                    cause=f"{record['kind'].capitalize()} {candidate.alias} into PRIME",
                    environment_root=candidate.components["environment"],
                    evidence_root=candidate.components["evidence"],
                    workspace=candidate.workspace,
                )
        if record["state"] == "PREPARED":
            self._set_state(record, "AUTHORIZED")
        if record["state"] == "AUTHORIZED":
            self._set_state(record, "COMMITTED", committed=True)
        receipt_row = self.store.receipt_for_transaction(record["transactionId"])
        if receipt_row is None:
            receipt = self.receipts.append(
                transaction_id=record["transactionId"],
                parent_world=record["parentWorld"],
                candidate_world=record["candidateContent"],
                before_root=record["beforeRoot"],
                after_root=record["stagedRoot"],
                delta=record["delta"],
                contamination=record["contamination"],
                generated=record.get("generated", []),
                dependency_changes=record.get("dependencyChanges", []),
            )
            self.store.append_causal_event(
                {
                    "schemaVersion": SCHEMA_VERSION,
                    "worldInstance": candidate.instance_id,
                    "kind": "collapse-receipt",
                    "actor": "worldline",
                    "reason": None,
                    "transactionId": record["transactionId"],
                    "receiptId": receipt["receiptId"],
                    "receiptRoot": receipt["receiptRoot"],
                }
            )
        else:
            receipt = {**receipt_row["receipt"], "receiptRoot": receipt_row["receipt_root"], "chainHash": receipt_row["chain_hash"]}
        return {
            "transactionId": record["transactionId"],
            "state": "COMMITTED",
            "candidate": candidate.alias,
            "beforeRoot": record["beforeRoot"],
            "afterRoot": record["stagedRoot"],
            "receipt": receipt,
        }

    def recover_all(self) -> list[dict[str, Any]]:
        # Recovery must never take the daemon down. A transaction that cannot be resolved (for
        # example a crash between the prepared-record write and its database row, which leaves
        # the two durably disagreeing) is quarantined and reported instead of raised: an
        # unraisable startup would deny every read-only diagnostic — doctor, log, list, why —
        # and leave the operator with no route back except hand-editing JSON and SQLite.
        # Mutations are gated separately in prepare()/commit(), so this is fail-open for
        # diagnosis and fail-closed for anything that could touch PRIME.
        recovered: list[dict[str, Any]] = []
        self.unrecoverable = {}
        for row in self.store.transactions_in_state(("PREPARED", "AUTHORIZED")):
            transaction_id = row["transaction_id"]
            try:
                recovered.append(self._recover_one(transaction_id))
            except WorldlineError as exc:
                self.unrecoverable[transaction_id] = exc.as_dict()
                recovered.append(
                    {"transactionId": transaction_id, "state": "UNRECOVERABLE", "error": exc.as_dict()}
                )
        # A crash between the COMMITTED state write and the receipt append leaves a committed
        # collapse with no receipt and no causal event, permanently: the chains stay internally
        # consistent, so `log --verify` passes over the hole. Replaying _finish_committed for a
        # COMMITTED record is idempotent (both _set_state calls are state-guarded and the
        # checkpoint publish is skipped by the primeGeneration guard), so finish the evidence.
        for row in self.store.transactions_in_state(("COMMITTED",)):
            transaction_id = row["transaction_id"]
            if self.store.receipt_for_transaction(transaction_id) is not None:
                continue
            try:
                record = self._load_record(transaction_id)
                self._finish_committed(record)
                recovered.append({"transactionId": transaction_id, "state": "RECEIPT_RECOVERED"})
            except WorldlineError as exc:
                self.unrecoverable[transaction_id] = exc.as_dict()
                recovered.append(
                    {"transactionId": transaction_id, "state": "RECEIPT_UNRECOVERABLE", "error": exc.as_dict()}
                )
        return recovered

    def _recover_one(self, transaction_id: str) -> dict[str, Any]:
        record = self._load_record(transaction_id)
        live_marker = self._marker(self.paths.live)
        prepared_marker = self._marker(Path(record["preparedMapping"]))
        if live_marker == transaction_id and prepared_marker != transaction_id:
            return self._finish_committed(record)
        if prepared_marker == transaction_id and live_marker != transaction_id:
            self._set_state(record, "ABORTED", error={"code": "RECOVERED_BEFORE_COMMIT"})
            return {"transactionId": transaction_id, "state": "ABORTED"}
        raise WorldlineError(
            "RECOVERY_AMBIGUOUS",
            "transaction generation marker does not identify one commit state",
            {"transactionId": transaction_id, "liveMarker": live_marker, "preparedMarker": prepared_marker},
        )

    def _assert_recovery_complete(self) -> None:
        if getattr(self, "unrecoverable", None):
            raise WorldlineError(
                "RECOVERY_INCOMPLETE",
                "a previous transaction could not be recovered; PRIME must not be mutated until it is resolved",
                {"transactions": sorted(self.unrecoverable)},
            )

    def _dependency_changes(
        self,
        candidate: World,
        roots: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        base_records = capture_dependencies(
            [
                (root["root_key"], Path(candidate.base_payload_path) / root["root_key"])
                for root in roots
            ],
            self.core,
        )
        candidate_records = capture_dependencies(
            [
                (root["root_key"], Path(candidate.payload_path) / root["root_key"])
                for root in roots
            ],
            self.core,
        )

        def flatten(records: list[dict[str, Any]]) -> dict[tuple[str, str, str, str], str | None]:
            values: dict[tuple[str, str, str, str], str | None] = {}
            for record in records:
                declared = record.get("declared")
                if not isinstance(declared, list):
                    continue
                for dependency in declared:
                    name = dependency.get("name")
                    if not isinstance(name, str):
                        continue
                    key = (
                        record["rootKey"],
                        record["directoryB64"],
                        record["format"],
                        name,
                    )
                    version = dependency.get("version")
                    values[key] = None if version is None else str(version)
            return values

        before = flatten(base_records)
        after = flatten(candidate_records)
        changes: list[dict[str, Any]] = []
        for key in sorted(set(before) | set(after)):
            if key in before and key in after and before[key] == after[key]:
                continue
            root_key, directory, format_name, name = key
            changes.append(
                {
                    "rootKey": root_key,
                    "directoryB64": directory,
                    "format": format_name,
                    "name": name,
                    "change": (
                        "ADD" if key not in before
                        else "DELETE" if key not in after
                        else "MODIFY"
                    ),
                    "from": before.get(key),
                    "to": after.get(key),
                }
            )
        return changes

    def _capture(self, *, source: bytes, logical: bytes, root: Mapping[str, Any]) -> CapturedManifest:
        repository = self.git.capture(source) if root["kind"] == "repo" else None
        return Manifest.capture(
            source,
            logical_root=logical,
            root_key=root["root_key"],
            kind=root["kind"],
            core=self.core,
            repository=repository,
        )

    def _capture_payload(
        self,
        *,
        source: bytes,
        logical: bytes,
        root: Mapping[str, Any],
    ) -> CapturedManifest:
        manifest_path = Path(os.fsdecode(os.path.dirname(source))) / "manifests" / f"{root['root_key']}.json"
        if not manifest_path.is_file():
            return self._capture(source=source, logical=logical, root=root)
        manifest = Manifest.load(manifest_path, self.core)
        if (
            manifest.value["rootKey"] != root["root_key"]
            or manifest.value["kind"] != root["kind"]
            or base64.b64decode(manifest.value["rootPathB64"].encode("ascii"), validate=True) != logical
        ):
            raise WorldlineError("PAYLOAD_INTEGRITY_FAILED", f"declared manifest identity differs for root {root['root_key']}")
        Manifest.verify_content(manifest, source, self.core)
        return manifest

    def _capture_current_roots(self) -> dict[str, CapturedManifest]:
        return {
            root["root_key"]: self._capture(
                source=os.path.realpath(bytes(root["path"])), logical=bytes(root["path"]), root=root
            )
            for root in self.store.roots()
        }

    def _capture_staged(self, record: Mapping[str, Any]) -> dict[str, CapturedManifest]:
        payload = Path(record["stagingPayload"])
        return {
            root["root_key"]: self._capture(
                source=os.fsencode(payload / root["root_key"]), logical=bytes(root["path"]), root=root
            )
            for root in self.store.roots()
        }

    def _create_mapping(
        self,
        mapping: Path,
        payload: Path,
        roots: list[dict[str, Any]],
        transaction_id: str,
    ) -> None:
        for root in roots:
            os.symlink(os.fsencode(payload / root["root_key"]), os.fsencode(mapping / root["root_key"]))
        atomic_write_json(
            mapping / _MARKER,
            {"schemaVersion": SCHEMA_VERSION, "transactionId": transaction_id},
        )

    @staticmethod
    def _fsync_payload_tree(payload: Path) -> None:
        if not payload.is_dir():
            return
        for current, directories, _files in os.walk(payload, followlinks=False):
            directories.sort()
            try:
                fsync_directory(Path(current))
            except OSError:
                # A directory that vanished under us cannot be made durable; the pre-exchange
                # staged-root re-hash already guarded content, so best-effort flush is enough.
                pass

    def _marker(self, directory: Path) -> str | None:
        path = directory / _MARKER
        if not path.is_file():
            return None
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise WorldlineError("RECOVERY_AMBIGUOUS", f"invalid generation marker: {path}") from exc
        if value.get("schemaVersion") != SCHEMA_VERSION or not isinstance(value.get("transactionId"), str):
            raise WorldlineError("RECOVERY_AMBIGUOUS", f"invalid generation marker schema: {path}")
        return value["transactionId"]

    def _load_record(self, transaction_id: str) -> dict[str, Any]:
        row = self.store.transaction_record(transaction_id)
        path = Path(row["prepared_path"])
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise WorldlineError("TRANSACTION_RECORD_INVALID", f"cannot read prepared transaction {transaction_id}") from exc
        if record.get("schemaVersion") != SCHEMA_VERSION or record.get("transactionId") != transaction_id:
            raise WorldlineError("TRANSACTION_RECORD_INVALID", f"prepared transaction identity mismatch: {transaction_id}")
        if row["state"] != record.get("state"):
            raise WorldlineError("TRANSACTION_RECORD_INVALID", f"database and prepared transaction state differ: {transaction_id}")
        return record

    def _set_state(
        self,
        record: dict[str, Any],
        target: str,
        *,
        error: dict[str, Any] | None = None,
        committed: bool = False,
    ) -> None:
        source = record["state"]
        # The proved kernel decides the lifecycle; the Python table is kept only as a
        # cross-check so a disagreement is loud instead of one side silently winning.
        kernel_allows = self.core.transaction_transition_allowed(source, target)
        if kernel_allows != (target in _TRANSACTION_TRANSITIONS[source]):
            raise WorldlineError(
                "CORE_DISAGREEMENT",
                f"proved kernel and runtime table disagree on transaction transition {source} -> {target}",
            )
        if not kernel_allows:
            raise WorldlineError(
                "INVALID_TRANSACTION_STATE",
                f"transaction cannot transition from {source} to {target}",
            )
        record["state"] = target
        record["error"] = error
        atomic_write_json(Path(record["preparedPath"]), record)
        self.store.update_transaction(record["transactionId"], target, error=error, committed=committed)
        if target in {"DENIED", "ABORTED"}:
            # Terminal without commit: the staged payload/mapping can never be exchanged, so
            # reclaim the disk it holds. Guard against removing a live/committed generation.
            staging = record.get("stagingPayload")
            if staging and self._marker(self.paths.live) != record["transactionId"]:
                shutil.rmtree(Path(staging).parent, ignore_errors=True)

    def _is_ancestor(self, ancestor: str | None, descendant: str) -> bool:
        if ancestor is None:
            return False
        current: str | None = descendant
        seen: set[str] = set()
        while current is not None and current not in seen:
            if current == ancestor:
                return True
            seen.add(current)
            current = self.store.world(current).parent_instance
        return False


class _NullContext:
    def __enter__(self) -> None:
        return None

    def __exit__(self, _type: Any, _value: Any, _traceback: Any) -> bool:
        return False
