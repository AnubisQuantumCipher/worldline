from __future__ import annotations

import logging

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
from .validation import content_differences, content_root_set, current_requirements, differences, effective_context, verify_context
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

_LOG = logging.getLogger("worldline.transaction")

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
    validation: dict[str, Any] = field(default_factory=dict)
    tested_root: str = ""
    staged_content_root: str = ""
    untested_paths: list[str] = field(default_factory=list)
    staged_validation: dict[str, Any] | None = None


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
        anchor: Any | None = None,
        config: Any | None = None,
        validator: Callable[..., dict[str, Any]] | None = None,
    ) -> None:
        self.paths = paths
        self.store = store
        # Global configuration (network policy, projections): part of every requirement hash.
        self.config = config
        # Evaluates a staged merge result against the current requirements (Revalidator.
        # validate_staged). Without one, staged bytes nobody tested are simply refused.
        self.validator = validator
        self.core = core or Core.shared()
        self.anchor = anchor
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

    def prepare(self, candidate_value: str, *, kind: str = "collapse", return_of: str | None = None) -> PreparedTransaction:
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
        # Evidence freshness (1.3.0): before anything is staged, the candidate's evidence must
        # have been evaluated against exactly the requirements the CURRENT PRIME imposes. A
        # refusal here is recorded on the causal log and never creates a transaction.
        freshness = self._freshness(candidate, kind=kind, return_of=return_of)
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
            # The bytes that will become live must be the bytes that were tested. Candidate-only
            # evidence cannot authorize a staged merge whose content differs from the candidate
            # (the kernel decides STAGED_UNTESTED on this pair); with conflicts the pair is
            # neutral so the more specific CONFLICT decision is reported.
            tested_root = content_root_set(candidate_manifests, self.core)
            tested_manifests = candidate_manifests
            if freshness.get("mode") == "re-application":
                # The evidence being relied on attests to the subject world's FINALIZED bytes.
                # A world that has since been live (it became PRIME and was displaced) carries
                # the displaced state in its payload directory; those bytes were never tested by
                # that evidence. Judge the merge against the declared finalization manifests.
                finalized = self._finalized_manifests(self.store.world(freshness["subject"]), roots)
                if finalized is None:
                    tested_root = hash_id(bytes(32))
                    tested_manifests = {}
                else:
                    tested_root = content_root_set(finalized, self.core)
                    tested_manifests = finalized
            staged_content_root = tested_root if conflicts else content_root_set(staged_manifests, self.core)
            untested_paths = [] if conflicts else content_differences(tested_manifests, staged_manifests)
            staged_validation: dict[str, Any] | None = None
            if not conflicts and staged_content_root != tested_root and self.validator is not None:
                # PRIME moved under the candidate and the merge produced bytes nobody tested.
                # The candidate's evidence cannot speak for them; the current checks run over the
                # staged result itself and, only if they pass, the staged content becomes the
                # tested content. Otherwise the kernel refuses STAGED_UNTESTED.
                staged_validation = self.validator(payload, candidate, current_manifests, staged_manifests, staged_content_root)
                if staged_validation["outcome"] == "PASS":
                    tested_root = staged_content_root
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
                    expected_validation_context=hash_bytes_from_id(freshness["requirementHash"]),
                    candidate_validation_context=hash_bytes_from_id(freshness["candidateRequirementHash"]),
                    tested_root=hash_bytes_from_id(tested_root),
                    staged_content_root=hash_bytes_from_id(staged_content_root),
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
                "validation": freshness,
                "testedRoot": tested_root,
                "stagedContentRoot": staged_content_root,
                "untestedPaths": untested_paths[:200],
                "stagedValidation": staged_validation,
                "returnOf": return_of,
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
                    untestedPaths=untested_paths[:50],
                    validation={k: freshness.get(k) for k in ("mode", "requirementHash", "candidateRequirementHash")},
                    stagedValidation=None if staged_validation is None else {k: staged_validation.get(k) for k in ("validationId", "outcome", "summary", "failed", "results")},
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
                validation={k: freshness.get(k) for k in ("mode", "source", "requirementHash", "candidateRequirementHash", "contextHash", "policySourceSha256", "evaluatedAt")},
                tested_root=tested_root,
                staged_content_root=staged_content_root,
                untested_paths=untested_paths[:50],
                staged_validation=None if staged_validation is None else {k: staged_validation.get(k) for k in ("validationId", "outcome", "summary", "failed", "requirementHash", "contextHash", "results")},
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
        # The candidate payload itself must still be the bytes that were prepared: evidence and
        # receipts name the candidate, so a payload altered after preparation cannot commit
        # even though the staged copy is what would be exchanged.
        candidate_manifests_now = {
            root["root_key"]: self._capture_payload(source=os.fsencode(Path(candidate.payload_path) / root["root_key"]), logical=bytes(root["path"]), root=root)
            for root in self.store.roots()
        }
        if Manifest.root_set_hash(candidate_manifests_now.values(), self.core) != record["candidateRoot"]:
            self._set_state(record, "DENIED", error={"code": "CANDIDATE_CHANGED_AFTER_PREPARE"})
            raise WorldlineError("CANDIDATE_CHANGED_AFTER_PREPARE", "the candidate payload changed after preparation; prepare again")
        if "validation" not in record or "testedRoot" not in record:
            self._set_state(record, "DENIED", error={"code": "TRANSACTION_RECORD_LEGACY"})
            raise WorldlineError("TRANSACTION_RECORD_LEGACY", "this transaction was prepared by a runtime without validation contexts; abort it and prepare again")
        current_requirement = current_requirements(self.store, self.config, self.core)
        if self.watcher is not None and before_generation != self.watcher.synchronized_generation():
            self._set_state(record, "DENIED", error={"code": "PRIME_CHANGED_DURING_CAPTURE"})
            raise WorldlineError("PRIME_CHANGED_DURING_CAPTURE", "PRIME changed during collapse authorization")

        decision = self._authorize(record, candidate, staged_root, current_requirement_hash=current_requirement["requirementHash"], staged_content_root=content_root_set(staged_manifests, self.core))
        if decision != "AUTHORIZED":
            self._set_state(record, "DENIED", error={"code": decision})
            if decision == "VALIDATION_CONTEXT_MISMATCH":
                raise WorldlineError("EVIDENCE_STALE", "the requirements changed between preparation and commit; the prepared evidence no longer applies", {"decision": decision, "preparedRequirementHash": record["validation"].get("requirementHash"), "currentRequirementHash": current_requirement["requirementHash"]})
            raise WorldlineError(decision, f"proved core denied collapse: {decision}")
        record["commitRequirementHash"] = current_requirement["requirementHash"]
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

    def _authorize(self, record: dict[str, Any], candidate: World, staged_root: str, *, current_requirement_hash: str | None = None, staged_content_root: str | None = None) -> str:
        # Records prepared before parentContentExpected existed carry only the claim; for those
        # the comparison degrades to the 1.0 behaviour rather than failing recovery outright.
        expected_parent = record.get("parentContentExpected") or record["parentWorld"]
        validation = record.get("validation") or {}
        # At commit the CURRENT requirement hash is recomputed and compared, by the kernel,
        # with the requirement the candidate's evidence was bound to at preparation. For a
        # checkpoint return both sides are the current hash (documented: no evidence applies).
        expected_context = current_requirement_hash or validation.get("requirementHash") or hash_id(bytes(32))
        candidate_context = validation.get("candidateRequirementHash") if validation.get("mode") != "checkpoint-return" else expected_context
        tested = record.get("testedRoot") or hash_id(bytes(32))
        staged_content = staged_content_root or record.get("stagedContentRoot") or hash_id(bytes(32))
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
                expected_validation_context=hash_bytes_from_id(expected_context),
                candidate_validation_context=hash_bytes_from_id(candidate_context or hash_id(bytes(32))),
                tested_root=hash_bytes_from_id(tested),
                staged_content_root=hash_bytes_from_id(staged_content),
            )
        )

    @staticmethod
    def _evidence_binding(record: Mapping[str, Any]) -> dict[str, Any] | None:
        validation = record.get("validation")
        if not isinstance(validation, dict):
            return None  # prepared by a runtime without validation contexts (never commits; recovery only)
        staged = record.get("stagedValidation")
        return {
            "schemaVersion": 1,
            "mode": validation.get("mode"),
            "evidenceSource": validation.get("source"),
            "candidateContextHash": validation.get("contextHash"),
            "candidateRequirementHash": validation.get("candidateRequirementHash"),
            "prepareRequirementHash": validation.get("requirementHash"),
            "commitRequirementHash": record.get("commitRequirementHash"),
            "policySourceSha256": validation.get("policySourceSha256"),
            "testedRoot": record.get("testedRoot"),
            "stagedContentRoot": record.get("stagedContentRoot"),
            "stagedValidation": None if not isinstance(staged, dict) else {k: staged.get(k) for k in ("validationId", "outcome", "summary", "requirementHash", "contextHash", "evaluatedAt")},
            "untestedPathCount": len(record.get("untestedPaths") or []),
        }

    def _freshness(self, candidate: World, *, kind: str, return_of: str | None) -> dict[str, Any]:
        """Evidence freshness at the promotion boundary (Python-enforced; the kernel proves that
        a mismatching pair is never AUTHORIZED, it does not compute either side).

        Rules:
        * collapse — the candidate's effective validation context must be intact, bound to this
          world, must not name verifiers the candidate rewrote, and its requirement hash must
          equal the current PRIME's requirement hash. Otherwise EVIDENCE_CONTEXT_MISSING /
          EVIDENCE_CONTEXT_INVALID / VERIFIER_MODIFIED_BY_CANDIDATE / EVIDENCE_STALE.
        * return to a PRIME checkpoint (a previous reality, actor `worldline`) — no candidate
          evidence applies; the current requirement hash is recorded as the policy in force.
        * re-application of a candidate world through `return <world>` — the same rules as a
          collapse, checked against the world being re-applied (`return_of`).
        """
        current = current_requirements(self.store, self.config, self.core)
        subject = self.store.world(return_of) if return_of else candidate
        # Every reality WORLDLINE itself published — a PRIME checkpoint (`prime-…`) or an earlier
        # return's result (`return-…`) — is a previous reality: restoring it needs no candidate
        # evidence. A candidate world named in `return WORLD` is a re-application.
        checkpoint_return = kind == "return" and subject.actor == "worldline"
        if checkpoint_return:
            return {"mode": "checkpoint-return", "requirementHash": current["requirementHash"], "candidateRequirementHash": current["requirementHash"], "policySourceSha256": current["policy"].get("sourceSha256"), "subject": subject.instance_id, "contextHash": None, "source": None}
        context, source = effective_context(self.store, subject)
        try:
            context = verify_context(context, candidate_instance=subject.instance_id, core=self.core)
            if context.get("verifiersModifiedByCandidate"):
                raise WorldlineError("VERIFIER_MODIFIED_BY_CANDIDATE", "the candidate changed an authoritative verifier its own evidence depends on", {"verifiers": context["verifiersModifiedByCandidate"]})
            if context["requirementHash"] != current["requirementHash"]:
                raise WorldlineError("EVIDENCE_STALE", "the candidate's evidence was evaluated against different requirements than the current PRIME imposes; revalidate or fork a new candidate", {"differences": differences(context["requirement"], current), "candidateRequirementHash": context["requirementHash"], "currentRequirementHash": current["requirementHash"], "evaluatedAt": context.get("evaluatedAt"), "evidenceSource": source})
        except WorldlineError as exc:
            self.store.append_causal_event({"schemaVersion": SCHEMA_VERSION, "worldInstance": subject.instance_id, "kind": "promotion-refused", "actor": "worldline", "reason": exc.code, "details": exc.details if hasattr(exc, "details") else None, "transactionKind": kind})
            raise
        return {"mode": "re-application" if kind == "return" else "collapse", "requirementHash": current["requirementHash"], "candidateRequirementHash": context["requirementHash"], "contextHash": context["contextHash"], "source": source, "policySourceSha256": current["policy"].get("sourceSha256"), "subject": subject.instance_id, "evaluatedAt": context.get("evaluatedAt")}

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
                evidence_binding=self._evidence_binding(record),
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
            if self.anchor is not None:
                # The exchange is durable already; anchoring must never undo that. A failure
                # here shows up as unanchoredReceipts in doctor and log --verify.
                row = self.store.receipt_for_transaction(record["transactionId"])
                try:
                    if row is not None:
                        self.anchor.append(
                            action=str(record.get("kind") or "collapse"),
                            receipt_id=receipt["receiptId"],
                            canonical=Path(row["canonical_path"]).read_bytes(),
                        )
                except (WorldlineError, OSError) as exc:
                    _LOG.warning("receipt %s was not anchored: %s", receipt["receiptId"], exc)
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

    def _finalized_manifests(self, world: World, roots: list[dict[str, Any]]) -> dict[str, CapturedManifest] | None:
        """The manifests a world's finalization declared (its evidence attests to exactly these
        bytes), or None when any is missing. They are read as declared, not re-captured: the
        payload directory may since have been live."""
        out: dict[str, CapturedManifest] = {}
        for root in roots:
            path = Path(world.payload_path) / "manifests" / f"{root['root_key']}.json"
            if not path.is_file():
                return None
            manifest = Manifest.load(path, self.core)
            if manifest.value.get("rootKey") != root["root_key"]:
                return None
            out[root["root_key"]] = manifest
        return out

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
