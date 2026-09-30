from __future__ import annotations

import logging

import base64
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import shutil
import uuid
from typing import Any, Callable, Mapping, Sequence

from . import SCHEMA_VERSION
from .canonical import atomic_write_json, canonical_bytes, fsync_directory
from .core import CollapseInput, Core, hash_bytes_from_id, hash_id
from .delta import Delta
from .validation import content_differences, content_root_set, current_requirements, differences, effective_context, effective_evidence, verify_context
from .errors import ConflictError, WorldlineError
from .executed import NO_BUNDLE_IDENTITY, bundle_identity
from .finalize import ENGINE_DECLARATIONS, check_declarations, required_roster, roster_decision, runner_agent_record
from .environment import capture_dependencies
from .linux.atomic import AtomicExchange
from .linux.git import GitAdapter
from .linux.inotify import InotifyWatcher
from .manifest import CapturedManifest, Manifest
from .model import TERMINAL_STATES, World, WorldState, utc_now
from .paths import WorldlinePaths
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
    #: What the policy declared each required check should have executed, and what the runner
    #: recorded it was given. Carried on the prepared transaction so the commit decides on the
    #: same established facts rather than recomputing them from a tree that has since moved.
    execution: dict[str, Any] = field(default_factory=dict)
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
        self.paths.prime_directory(self.data_transactions)
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
        # Drain the watcher first: a write it has already seen marks PRIME dirty only when its
        # events are consumed, and such a write is reconciled into a generation, never refused
        # as unaccounted (review of a23c265).
        self._generation()
        if self.reconcile_prime is not None and self.store.get_meta("dirty", False):
            self.reconcile_prime()
        candidate = self.store.world(candidate_value)
        subject_kind = self.store.world(return_of).world_kind if return_of else candidate.world_kind
        if candidate.world_kind == "system" or subject_kind == "system":
            # A system future's verdicts come from a runner inside the future itself; it is not
            # an evaluation and can never become PRIME, neither by collapse nor by `return`.
            raise WorldlineError(
                "SYSTEM_ROOT_COLLAPSE_UNSUPPORTED",
                "system futures on this backend are inspectable but cannot collapse or be returned to",
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
        # PRIME stability (1.9.0): the watcher's generation is read BEFORE the requirement read
        # and again just before the decision, and the kernel compares the two. A missing
        # watcher is an absent measurement, which the kernel refuses; it is no longer a skipped
        # guard.
        generation_before = self._generation()
        # Evidence freshness (1.3.0): before anything is staged, the candidate's evidence must
        # have been evaluated against exactly the requirements the CURRENT PRIME imposes. A
        # refusal here is recorded on the causal log and never creates a transaction.
        freshness = self._freshness(candidate, kind=kind, return_of=return_of)
        root_set = self.prime.root_set_hash(roots)
        transaction_id = str(uuid.uuid4())
        transaction_directory = self.data_transactions / transaction_id
        payload = transaction_directory / "payload"
        mapping = transaction_directory / "mapping"
        # A committed transaction's payload IS PRIME, and its mapping becomes `live`.
        self.paths.prime_directory(transaction_directory)
        self.paths.prime_directory(payload)
        self.paths.prime_directory(mapping)

        base_manifests: dict[str, CapturedManifest] = {}
        current_manifests: dict[str, CapturedManifest] = {}
        candidate_manifests: dict[str, CapturedManifest] = {}
        staged_manifests: dict[str, CapturedManifest] = {}
        conflicts: list[dict[str, Any]] = []
        candidate_declared = True
        try:
            for root in roots:
                root_key = root["root_key"]
                logical = bytes(root["path"])
                base_source = os.fsencode(Path(candidate.base_payload_path) / root_key)
                candidate_source = os.fsencode(Path(candidate.payload_path) / root_key)
                current_source = self.paths.root_source(root)
                for label, source in (("base", base_source), ("candidate", candidate_source), ("current", current_source)):
                    if not os.path.isdir(source):
                        raise WorldlineError(
                            "INCOMPLETE_WORLD",
                            f"{label} payload is missing root {root_key}",
                            {"path": os.fsdecode(source)},
                        )
                # The candidate's finalization declared a manifest for each root; one that is
                # missing is not silently re-captured into "tested" bytes (1.9.0).
                candidate_declared = candidate_declared and self._declared_manifest_present(candidate_source, root)
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

            # Client mode: the staged payload becomes PRIME, which clients can reach. Its modes
            # are the candidate's; refuse any a client could write through before a transaction
            # exists (the staging is removed by the handler below).
            if not conflicts:
                for root_key in staged_manifests:
                    self.paths.assert_client_safe(payload / root_key)

            delta = Delta.compute_all(base_manifests, candidate_manifests, self.core)
            base_root = Manifest.root_set_hash(base_manifests.values(), self.core)
            before_root = Manifest.root_set_hash(current_manifests.values(), self.core)
            candidate_root = Manifest.root_set_hash(candidate_manifests.values(), self.core)
            # A conflicted merge has no staged tree: absent, never a zero digest. The kernel
            # reports CONFLICT before it looks for the staged identities.
            staged_root = None if conflicts else Manifest.root_set_hash(staged_manifests.values(), self.core)
            staged_content_root = None if conflicts else content_root_set(staged_manifests, self.core)
            tested_root, tested_manifests, tested_source = self._tested_root(
                freshness, candidate, candidate_manifests, candidate_declared, roots)
            untested_paths = [] if conflicts else content_differences(tested_manifests or {}, staged_manifests)
            staged_validation: dict[str, Any] | None = None
            if not conflicts and staged_content_root != tested_root and self.validator is not None:
                # The bytes that would go live are not the bytes the evidence examined (PRIME
                # moved under the candidate, or the examined bytes are unknown). The current
                # checks run over the staged tree itself; the kernel then decides whether THAT
                # evaluation covers the staged bytes. Nothing here promotes its outcome.
                staged_validation = self.validator(payload, candidate, current_manifests, staged_manifests, staged_content_root)
                if (staged_validation.get("context") or {}).get("verifiersModifiedByCandidate"):
                    raise WorldlineError("VERIFIER_MODIFIED_BY_CANDIDATE", "the staged merge result carries a rewritten authoritative verifier",
                                         {"verifiers": staged_validation["context"]["verifiersModifiedByCandidate"]})
            if not conflicts:
                self._create_mapping(mapping, payload, roots, transaction_id)
                # The staged tree as the merge captured it, kept beside (never inside) the roots,
                # so a recovery after the exchange can publish what was committed even if the live
                # tree moved while the daemon was down (review of 0ee1112).
                # Named `manifests` so relocation classifies it as the hashed record it is.
                staged_record = transaction_directory / "manifests"
                staged_record.mkdir(mode=0o700)
                for root_key, manifest in staged_manifests.items():
                    manifest.save(staged_record / f"{root_key}.json")

            subject = self.store.world(return_of) if return_of else candidate
            current = freshness["current"]
            staged_block = self._staged_block(subject, current, staged_validation)
            foreign_state, foreign_detail = self._foreign_writes(current_manifests, current_prime, candidate)
            registered_watch, watched = self._watch_sets()
            expected_subject, claimed_subject = self._subject_pair(freshness, candidate, return_of)
            decision_inputs = {
                "schemaVersion": 1,
                "expectedSubject": expected_subject,
                "evidenceSubject": claimed_subject,
                "stagedRoot": staged_root,
                "testedRoot": tested_root,
                "testedRootSource": tested_source,
                "primary": {
                    "evaluatedRequirement": freshness.get("candidateRequirementHash"),
                    "rosterComplete": freshness["execution"].get("complete") is True,
                    "declaredVerifiers": freshness["execution"].get("expected"),
                    "executedVerifiers": freshness["execution"].get("actual"),
                },
                "staged": staged_block,
                "conflictsMeasured": True,
                "foreignWrites": {"state": foreign_state, **foreign_detail},
                "watchSets": {"registered": registered_watch, "watched": watched},
            }
            decision_inputs["generations"] = {"before": generation_before, "after": self._generation()}
            decision = self._decide(
                phase="PREPARE", kind_mode=freshness["mode"], candidate=candidate, subject=subject,
                expected_parent=expected_parent_content, base_root=base_root, delta_hash=delta.delta_hash,
                root_set=root_set, expected_staged_root=staged_root, actual_staged_root=None,
                staged_content_root=staged_content_root, conflicts=bool(conflicts),
                current_requirement=current["requirementHash"], inputs=decision_inputs,
                witness=freshness.get("witness"),
            )
            if decision == "FOREIGN_MANAGED_WRITE":
                self._note_unaccounted_write(current_prime, decision_inputs["foreignWrites"])
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
                # The transactions table column is NOT NULL: a conflicted merge's absent staged
                # root is stored as the literal "absent" there (1.9.0) and as null here.
                "stagedRoot": staged_root,
                "rootSetHash": root_set,
                "conflicts": conflicts,
                "contamination": candidate.contamination,
                "validation": {k: v for k, v in freshness.items() if k != "current"},
                "testedRoot": tested_root,
                "stagedContentRoot": staged_content_root,
                "recordSchema": 2,
                "decisionInputs": decision_inputs,
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
                if decision == "PRIME_CHANGED":
                    # The operator-visible code 1.8.0 raised for the same fact; the kernel decided it.
                    raise WorldlineError("PRIME_CHANGED_DURING_CAPTURE", "PRIME changed while collapse staging was copied and hashed",
                                         {"decision": decision, "transactionId": transaction_id,
                                          "beforeGeneration": decision_inputs["generations"]["before"],
                                          "afterGeneration": decision_inputs["generations"]["after"]})
                raise ConflictError(
                    f"collapse denied: {decision}",
                    transactionId=transaction_id,
                    decision=decision,
                    conflicts=conflicts,
                    contamination=self._reported_contamination(candidate, decision_inputs["foreignWrites"]),
                    untestedPaths=untested_paths[:50],
                    validation={k: freshness.get(k) for k in ("mode", "requirementHash", "candidateRequirementHash", "witness")},
                    absentInputs=decision_inputs.get("absent", []),
                    foreignWrites=decision_inputs["foreignWrites"],
                    execution={k: (freshness.get("execution") or {}).get(k)
                               for k in ("complete", "expected", "actual", "mode", "problems")},
                    stagedValidation=None if staged_validation is None else {k: staged_validation.get(k) for k in ("validationId", "outcome", "summary", "failed", "examinedContentRoot", "results")},
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
                validation={k: freshness.get(k) for k in ("mode", "source", "requirementHash", "candidateRequirementHash", "contextHash", "policySourceSha256", "evaluatedAt", "witness")},
                execution=dict(freshness.get("execution") or {}),
                tested_root=tested_root,
                staged_content_root=staged_content_root,
                untested_paths=untested_paths[:50],
                staged_validation=None if staged_validation is None else {k: staged_validation.get(k) for k in ("validationId", "outcome", "summary", "failed", "requirementHash", "contextHash", "examinedContentRoot", "results")},
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
        if not isinstance(record.get("decisionInputs"), Mapping) or "validation" not in record:
            self._set_state(record, "DENIED", error={"code": "TRANSACTION_RECORD_LEGACY"})
            raise WorldlineError("TRANSACTION_RECORD_LEGACY", "this transaction was prepared by an earlier runtime; abort it and prepare again")
        candidate = self.store.world(record["candidateWorld"])
        self.stop_writers(candidate)
        generation_before = self._generation()
        current_manifests = self._capture_current_roots()
        if Manifest.root_set_hash(current_manifests.values(), self.core) != record["beforeRoot"]:
            self._set_state(record, "DENIED", error={"code": "PRIME_CHANGED_AFTER_PREPARE"})
            raise WorldlineError(
                "PRIME_CHANGED_AFTER_PREPARE",
                "PRIME changed after collapse preparation; prepare again",
            )
        # The staged tree is recaptured; the kernel compares it with the merge's capture recorded
        # at prepare (Staged_Root_Mismatch). No Python comparison stands in for that.
        staged_manifests = self._capture_staged(record)
        staged_root = Manifest.root_set_hash(staged_manifests.values(), self.core)
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
        current_requirement = current_requirements(self.store, self.config, self.core)
        decision = self._authorize(record, candidate, current_manifests=current_manifests,
                                   staged_root=staged_root,
                                   staged_content_root=content_root_set(staged_manifests, self.core),
                                   current_requirement=current_requirement,
                                   generation_before=generation_before)
        if decision != "AUTHORIZED":
            self._set_state(record, "DENIED", error={"code": decision})
            if decision == "FOREIGN_MANAGED_WRITE":
                self._note_unaccounted_write(self.store.prime(), (record.get("decisionInputsAtCommit") or {}).get("foreignWrites") or {})
            inputs_at_commit = record.get("decisionInputsAtCommit") or {}
            details = {"decision": decision, "transactionId": transaction_id,
                       "absentInputs": inputs_at_commit.get("absent", []),
                       "foreignWrites": inputs_at_commit.get("foreignWrites"),
                       "contamination": self._reported_contamination(candidate, inputs_at_commit.get("foreignWrites") or {})}
            if decision == "VALIDATION_CONTEXT_MISMATCH":
                raise WorldlineError("EVIDENCE_STALE", "the requirements changed between preparation and commit; the prepared evidence no longer applies", {**details, "preparedRequirementHash": record["validation"].get("requirementHash"), "currentRequirementHash": current_requirement["requirementHash"]})
            if decision == "PRIME_CHANGED":
                raise WorldlineError("PRIME_CHANGED_DURING_CAPTURE", "PRIME changed during collapse authorization", details)
            raise WorldlineError(decision, f"proved core denied collapse: {decision}", details)
        colliding = self._checkpoint_collision(record, candidate, staged_manifests)
        if colliding is not None:
            self._set_state(record, "ABORTED", error={"code": "CHECKPOINT_IDENTITY_TAKEN"})
            raise WorldlineError("CHECKPOINT_IDENTITY_TAKEN",
                                 f"the PRIME generation this commit would publish has the identity of existing world {colliding.alias}; "
                                 "nothing was changed (a declined return leaves its vehicle holding that identity)",
                                 {"transactionId": transaction_id, "world": colliding.alias})
        record["commitRequirementHash"] = current_requirement["requirementHash"]
        self._set_state(record, "AUTHORIZED")
        # File contents were fsynced during staging, but the directory entries that link them
        # into the payload tree were not. Flush every staged directory before the exchange so a
        # power loss immediately after the (durable) rename cannot leave PRIME pointing at a tree
        # whose dirents never reached disk — recovery re-hashes survivors and would enshrine a
        # torn tree as COMMITTED otherwise.
        self._fsync_payload_tree(Path(record["stagingPayload"]))
        # The kernel's generation pair ends at the decision; the fsync above takes time in
        # proportion to the tree. PRIME must still be at the generation the decision saw, or a
        # write in between would be displaced without being recorded (review of a23c265). What
        # remains is the moment between this read and the exchange.
        decided = ((record.get("decisionInputsAtCommit") or {}).get("generations") or {}).get("after")
        now = self._generation()
        if now is None or now != decided:
            code = "PRIME_WATCH_UNAVAILABLE" if now is None else "PRIME_CHANGED_DURING_CAPTURE"
            self._set_state(record, "ABORTED", error={"code": code})
            raise WorldlineError(code, "PRIME changed between the collapse decision and the exchange; prepare again",
                                 {"refusedBy": "exchange-guard", "transactionId": transaction_id,
                                  "decidedGeneration": decided, "generationNow": now})
        exchanged = False
        try:
            # Checked just above; stated as a refusal rather than an assert, which -O removes.
            if self.watcher is None:
                raise WorldlineError("PRIME_WATCH_UNAVAILABLE", "no PRIME watcher; the exchange cannot be attributed")
            with self.watcher.owned_writes():
                self.atomic.exchange(self.paths.live, Path(record["preparedMapping"]))
            exchanged = True
            return self._finish_committed(record, staged_manifests)
        except BaseException:
            # The rename is the commit point. If it happened (the live marker names this
            # transaction) and something after it failed -- the directory fsync, say -- the
            # record stays AUTHORIZED for recovery to finish; ABORTED would say refused while the
            # bytes are live (review of 19d0297).
            try:
                live_is_this = self._marker(self.paths.live) == transaction_id
            except WorldlineError:
                live_is_this = True  # unknown: leave it to recovery, which quarantines ambiguity
            if not exchanged and not live_is_this:
                self._set_state(record, "ABORTED", error={"code": "ATOMIC_EXCHANGE_FAILED"})
            raise

    def _authorize(self, record: dict[str, Any], candidate: World, *, current_manifests: Mapping[str, CapturedManifest],
                   staged_root: str, staged_content_root: str, current_requirement: Mapping[str, Any],
                   generation_before: int | None) -> str:
        """The commit's decision: every input recomputed now from the store and the live tree,
        except the facts only prepare observed (the evidence subject the speaking evaluation was
        bound to, the tested root, the evaluations' verdicts), which come from the prepared
        record. Nothing absent is filled in: a missing field is passed as absent."""
        inputs = dict(record["decisionInputs"])
        validation = record.get("validation") or {}
        return_of = record.get("returnOf")
        subject = self.store.world(return_of) if return_of else candidate
        primary = inputs.get("primary") if isinstance(inputs.get("primary"), Mapping) else {}
        prime = self.store.prime()
        foreign_state, foreign_detail = self._foreign_writes(current_manifests, prime, candidate)
        registered_watch, watched = self._watch_sets()
        expected_subject, _unused = self._subject_pair(validation, candidate, return_of)
        witness = self._checkpoint_witness(subject) if validation.get("mode") == "checkpoint-return" else None
        inputs.update({
            "expectedSubject": expected_subject,
            "foreignWrites": {"state": foreign_state, **foreign_detail},
            "watchSets": {"registered": registered_watch, "watched": watched},
            "primary": {**primary, "declaredVerifiers": self._declared_verifiers(current_requirement)},
        })
        inputs["generations"] = {"before": generation_before, "after": self._generation()}
        record["decisionInputsAtCommit"] = {k: inputs[k] for k in ("expectedSubject", "foreignWrites", "watchSets", "generations")}
        decision = self._decide(
            phase="COMMIT", kind_mode=validation.get("mode"), candidate=candidate, subject=subject,
            expected_parent=record.get("parentContentExpected"), base_root=record.get("baseRoot"),
            delta_hash=record.get("deltaHash"), root_set=self.prime.root_set_hash(self.store.roots()),
            expected_staged_root=inputs.get("stagedRoot"), actual_staged_root=staged_root,
            staged_content_root=staged_content_root, conflicts=bool(record.get("conflicts")),
            current_requirement=current_requirement["requirementHash"], inputs=inputs, witness=witness,
        )
        record["decisionInputsAtCommit"]["absent"] = inputs.get("absent", [])
        return decision

    # -- 1.9.0 decision inputs: every identity from a named producer, absent as None ---------

    def _note_unaccounted_write(self, prime: World | None, measurement: Mapping[str, Any]) -> None:
        """Live PRIME differs from its record and nothing reported it. The refusal stands; the
        change is recorded and PRIME marked dirty, so the next status or prepare reconciles it
        into a PRIME generation and a retry can proceed."""
        if prime is None or measurement.get("measuredBy") != "live-capture-vs-prime-record":
            return
        self.store.set_meta("dirty", True)
        self.store.append_causal_event({"schemaVersion": SCHEMA_VERSION, "worldInstance": prime.instance_id,
                                        "kind": "unaccounted-write", "actor": "worldline",
                                        "reason": "live PRIME differs from its record: " + ", ".join(measurement.get("differing") or [])})

    @staticmethod
    def _identity(value: Any) -> bytes | None:
        """A sha256:<hex> identity as its 32 bytes; anything else is absent."""
        if not isinstance(value, str) or not value.startswith("sha256:"):
            return None
        return hash_bytes_from_id(value)

    def _generation(self) -> int | None:
        return None if self.watcher is None else int(self.watcher.synchronized_generation())

    def _watch_set_digest(self, pairs: Sequence[tuple[str, bytes]]) -> str:
        value = sorted([str(key), base64.b64encode(bytes(path)).decode("ascii")] for key, path in pairs)
        return hash_id(self.core.hash_bytes(b"worldline-watch-set-v1" + canonical_bytes(value)))

    def _watch_sets(self) -> tuple[str | None, str | None]:
        """The registered roots, and the roots the PRIME watcher is actually watching, each as a
        digest over (root key, resolved source path). An unresolvable root leaves the registered
        side absent; no watcher leaves the watched side absent. The kernel decides."""
        registered: list[tuple[str, bytes]] = []
        for root in self.store.roots():
            try:
                registered.append((root["root_key"], os.fsencode(self.paths.root_source(root))))
            except WorldlineError:
                return None, (None if self.watcher is None else self._watch_set_digest(self.watcher.watched_roots()))
        watched = None if self.watcher is None else self._watch_set_digest(self.watcher.watched_roots())
        return self._watch_set_digest(registered), watched

    @staticmethod
    def _reported_contamination(candidate: World, foreign: Mapping[str, Any]) -> list[Any]:
        """What a refusal reports as contamination: the candidate's recorded entries, plus the
        measured foreign write, so a consumer that reads only `contamination` does not show
        "none" for a FOREIGN_MANAGED_WRITE refusal (review of a23c265)."""
        reported = list(candidate.contamination or [])
        if foreign.get("state") == "FOUND" and foreign.get("measuredBy") == "live-capture-vs-prime-record":
            reported.append({"measuredBy": foreign["measuredBy"], "differing": list(foreign.get("differing") or [])})
        return reported

    def readiness(self, *, measure_foreign: bool) -> dict[str, Any]:
        """The promotion inputs doctor reports without deciding anything (1.9.0): watch coverage,
        and -- only when asked, since it captures every live root -- the foreign-write
        measurement a prepare would take now."""
        registered, watched = self._watch_sets()
        root_keys = sorted(root["root_key"] for root in self.store.roots())
        watched_keys = sorted({key for key, _path in self.watcher.watched_roots()}) if self.watcher is not None else []
        coverage = {
            "state": ("NO_WATCHER" if self.watcher is None else
                      "COMPLETE" if registered is not None and registered == watched else "INCOMPLETE"),
            "unwatchedRoots": [key for key in root_keys if key not in watched_keys],
            "faults": dict(getattr(self.watcher, "coverage_faults", dict)()) if self.watcher is not None else {},
            "generation": self._generation(),
        }
        foreign: dict[str, Any] = {"state": None, "measuredWith": "doctor --refresh"}
        if measure_foreign:
            try:
                state, detail = self._foreign_writes(self._capture_current_roots(), self.store.prime(), None)
                foreign = {"state": state, **detail}
            except WorldlineError as exc:
                # The live capture refused (a special file, a broken mapping, ...): the report
                # says so instead of failing, since that is when the operator needs doctor.
                foreign = {"state": "UNMEASURED", "measuredBy": "live-capture-vs-prime-record", "error": exc.as_dict()}
            except OSError as exc:  # an unreadable directory, and the like (review of 0ee1112)
                foreign = {"state": "UNMEASURED", "measuredBy": "live-capture-vs-prime-record",
                           "error": {"code": "CAPTURE_FAILED", "message": str(exc), "details": {"errno": exc.errno}}}
        # A reported write not yet reconciled also differs from the record; the next status or
        # prepare records it as a PRIME generation, so it is not a foreign write.
        foreign["primeDirty"] = bool(self.store.get_meta("dirty", False))
        return {"watchCoverage": coverage, "foreignWrites": foreign}

    def _foreign_writes(self, live: Mapping[str, CapturedManifest], prime: World | None, candidate: World | None) -> tuple[str, dict[str, Any]]:
        """Foreign managed writes, measured (whitepaper 8.1: a change in PRIME made by something
        other than a WORLDLINE commit). The component roots of the capture of live PRIME just
        taken are compared with the components the PRIME record states. A PRIME record without
        them is UNMEASURED. A candidate carrying recorded contamination is FOUND."""
        if candidate is not None and candidate.contamination:
            return "FOUND", {"measuredBy": "recorded-contamination", "differing": ["contamination"]}
        recorded = (prime.components or {}) if prime is not None else {}
        keys = ("filesystem", "config", "repository")
        if prime is None or any(not isinstance(recorded.get(key), str) for key in keys):
            return "UNMEASURED", {"measuredBy": "live-capture-vs-prime-record", "differing": []}
        live_components = Manifest.component_roots(live.values(), self.core)
        differing = [key for key in keys if live_components.get(key) != recorded.get(key)]
        return ("FOUND" if differing else "NONE_FOUND"), {"measuredBy": "live-capture-vs-prime-record", "differing": differing}

    def _subject_digest(self, instance: Any, binding: str) -> str | None:
        if not isinstance(instance, str) or not instance:
            return None
        return hash_id(self.core.hash_bytes(b"worldline-subject-v1" + canonical_bytes([instance, binding])))

    def _return_binding(self, return_of: str) -> str:
        # The formula returning.prepare_candidate uses for the vehicle's mission hash.
        return hash_id(self.core.hash_bytes(b"worldline-return-v1" + return_of.encode("ascii")))

    def _subject_pair(self, freshness: Mapping[str, Any], candidate: World, return_of: str | None) -> tuple[str | None, str | None]:
        """The world the promotion is about, and the world the speaking evidence -- or the return
        vehicle -- is bound to. Different records produce the two sides: the promotion's own
        arguments on one, the evidence context's binding and the vehicle's mission hash on the
        other. (1.9.0 replaces the owner pair, which had one producer.)"""
        if return_of:
            expected = self._subject_digest(return_of, self._return_binding(return_of))
            evidence_instance = return_of if freshness.get("mode") == "checkpoint-return" else freshness.get("evidenceInstance")
            claimed = self._subject_digest(evidence_instance, candidate.mission_hash or "")
        else:
            expected = self._subject_digest(candidate.instance_id, "")
            claimed = self._subject_digest(freshness.get("evidenceInstance"), "")
        return expected, claimed

    def _declared_manifest_present(self, source: bytes, root: Mapping[str, Any]) -> bool:
        manifest_path = Path(os.fsdecode(os.path.dirname(source))) / "manifests" / f"{root['root_key']}.json"
        return manifest_path.is_file()

    def _tested_root(self, freshness: Mapping[str, Any], candidate: World,
                     candidate_manifests: Mapping[str, CapturedManifest], candidate_declared: bool,
                     roots: list[dict[str, Any]]) -> tuple[str | None, Mapping[str, CapturedManifest] | None, str]:
        """What the speaking evaluation examined, or absent. A revalidation records the content
        root it examined; otherwise the finalization's declared manifests (verified against the
        payload) stand for it, and a missing one leaves the tested root absent."""
        examined = freshness.get("examinedContentRoot")
        if isinstance(examined, str):
            # A revalidation examines its world's declared manifests; when they are the bytes it
            # names, they also say path by path what it examined (for untestedPaths).
            declared = candidate_manifests if candidate_declared and content_root_set(candidate_manifests, self.core) == examined else None
            return examined, declared, "evaluation-examined-root"
        if freshness.get("mode") == "re-application":
            finalized = self._finalized_manifests(self.store.world(freshness["subject"]), roots)
            if finalized is None:
                return None, None, "finalized-manifests-missing"
            return content_root_set(finalized, self.core), finalized, "finalized-manifests"
        if not candidate_declared:
            return None, None, "declared-manifests-missing"
        return content_root_set(candidate_manifests, self.core), candidate_manifests, "declared-manifests"

    def _declared_verifiers(self, current: Mapping[str, Any]) -> str:
        required, _declared_empty = required_roster(current)
        bundles: dict[str, list[tuple[str, str, str]]] = {}
        for entry in current.get("verifiers") or ():
            bundles.setdefault(str(entry.get("checkId")), []).append(
                (str(entry.get("rootKey")), str(entry.get("path")), str(entry.get("sha256"))))
        return bundle_identity([("", check_id, bundle_identity(bundles[check_id]) if bundles.get(check_id) else NO_BUNDLE_IDENTITY)
                                for check_id in required])

    def _staged_block(self, subject: World, current: Mapping[str, Any], staged: Mapping[str, Any] | None) -> dict[str, Any]:
        """The staged-merge evaluation as the kernel reads it: the requirement it ran against,
        the kernel's roster verdict over its records (the agent judged from the subject's
        finalization), the verifier set it executed, and the content root it examined."""
        if staged is None:
            return {"ran": False, "evaluatedRequirement": None, "rosterComplete": False,
                    "executedVerifiers": None, "examinedRoot": None}
        identity = self._execution_identity(subject, current, recorded_checks=staged.get("results") or [])
        return {"ran": True, "validationId": staged.get("validationId"),
                "evaluatedRequirement": staged.get("requirementHash"),
                "rosterComplete": identity["complete"] is True,
                "executedVerifiers": identity["actual"],
                "examinedRoot": staged.get("examinedContentRoot"),
                "problems": identity["problems"]}

    def _decide(self, *, phase: str, kind_mode: Any, candidate: World, subject: World, expected_parent: Any,
                base_root: Any, delta_hash: Any, root_set: Any, expected_staged_root: Any, actual_staged_root: Any,
                staged_content_root: Any, conflicts: bool, current_requirement: Any, inputs: dict[str, Any],
                witness: Mapping[str, Any] | None) -> str:
        checkpoint = kind_mode == "checkpoint-return"
        primary = inputs.get("primary") if isinstance(inputs.get("primary"), Mapping) else {}
        staged = inputs.get("staged") if isinstance(inputs.get("staged"), Mapping) else {}
        generations = inputs.get("generations") if isinstance(inputs.get("generations"), Mapping) else {}
        watch = inputs.get("watchSets") if isinstance(inputs.get("watchSets"), Mapping) else {}
        values = CollapseInput(
            candidate_state=candidate.state.value,
            phase=phase,
            mode="CHECKPOINT_RETURN" if checkpoint else "CANDIDATE_EVALUATION",
            # The merge measured conflicts only if the record says so; a record without that
            # statement is unmeasured, never "none found".
            conflicts="FOUND" if conflicts else ("NONE_FOUND" if inputs.get("conflictsMeasured") is True else "UNMEASURED"),
            foreign_writes=str((inputs.get("foreignWrites") or {}).get("state") or "UNMEASURED"),
            roster_complete=False if checkpoint else primary.get("rosterComplete") is True,
            staged_roster_complete=staged.get("rosterComplete") is True,
            expected_parent=self._identity(expected_parent),
            candidate_parent=self._identity(candidate.parent_content),
            expected_subject=self._identity(inputs.get("expectedSubject")),
            evidence_subject=self._identity(inputs.get("evidenceSubject")),
            expected_base=self._identity(candidate.base_root),
            candidate_base=self._identity(base_root),
            expected_delta=self._identity(candidate.delta_hash),
            candidate_delta=self._identity(delta_hash),
            expected_root_set=self._identity(root_set),
            candidate_root_set=self._identity(candidate.root_set_hash),
            expected_staged_root=self._identity(expected_staged_root),
            actual_staged_root=None if phase == "PREPARE" else self._identity(actual_staged_root),
            staged_content_root=self._identity(staged_content_root),
            tested_root=self._identity(inputs.get("testedRoot")),
            current_requirement=self._identity(current_requirement),
            evaluated_requirement=None if checkpoint else self._identity(primary.get("evaluatedRequirement")),
            declared_verifiers=self._identity(primary.get("declaredVerifiers")),
            executed_verifiers=None if checkpoint else self._identity(primary.get("executedVerifiers")),
            staged_evaluated_requirement=self._identity(staged.get("evaluatedRequirement")),
            staged_executed_verifiers=self._identity(staged.get("executedVerifiers")),
            staged_examined_root=self._identity(staged.get("examinedRoot")),
            expected_checkpoint=self._identity(subject.content_id) if checkpoint else None,
            witnessed_checkpoint=self._identity((witness or {}).get("witnessed")) if checkpoint else None,
            registered_watch_set=self._identity(watch.get("registered")),
            watched_set=self._identity(watch.get("watched")),
            generation_before=generations.get("before") if type(generations.get("before")) is int else None,
            generation_after=generations.get("after") if type(generations.get("after")) is int else None,
        )
        inputs["absent"] = sorted(name for name in CollapseInput.__slots__
                                  if getattr(values, name) is None)
        return self.core.collapse_decide(values)

    # Far beyond any real store; a longer walk is treated as no witness rather than as a pass.
    _LINEAGE_LIMIT = 1_000_000

    def _checkpoint_witness(self, subject: World) -> dict[str, Any] | None:
        """Whether `subject` was a previous reality, established from records other than its own.

        Every PRIME names the PRIME it displaced as its parent: publish_checkpoint parents the
        new generation on the current PRIME, a committed collapse makes the candidate PRIME only
        when it was forked from the current PRIME, and a committed return is parented on the
        PRIME it replaced. So the parent chain from the current PRIME visits exactly the
        realities WORLDLINE has made live. The subject is one of them when the walk reaches it.

        The witness is the content identity a DIFFERENT record states for the subject: the
        `parent_content` its child in the lineage recorded when it was created from the frozen
        PRIME, or the PRIME register's `primeContent` when the subject is the current PRIME. The
        kernel compares it with the subject's own `content_id`.

        What this establishes, stated exactly: that the subject ROW was once live. Finding the
        walk hit is Python's decision (Checkpoint_Witnessed); the kernel's equality only checks
        that the two records agree, which they do unless one of them was altered. Neither value
        is computed from the bytes being restored: those are bound separately, by
        ReturnManager.return_point_manifests (the stored manifest, or a committed receipt's
        beforeRoot). Removing the last root starts a new lineage, so checkpoints from before
        such a reset have no witness.

        A WORLDLINE-made world that never became live -- the synthetic candidate left behind by
        a refused `return` -- is not on the walk, so it has no witness, and returning to it is
        refused instead of passing as a checkpoint with nothing to check.
        """
        if subject.content_id is None:
            return None
        prime = self.store.prime()
        if prime is None:
            return None
        if prime.instance_id == subject.instance_id:
            recorded = self.store.get_meta("primeContent")
            return {"source": "prime-register", "expected": subject.content_id,
                    "witnessed": recorded if isinstance(recorded, str) else None}
        # One indexed row per step (store.lineage_link), not a full world load: this runs inside
        # a mutating request, and a return that is refused walks all the way to genesis.
        link = self.store.lineage_link(prime.instance_id)
        seen: set[str] = set()
        while link is not None and link["parent_instance"] is not None and link["instance_id"] not in seen:
            if len(seen) >= self._LINEAGE_LIMIT:
                return None
            seen.add(link["instance_id"])
            if link["parent_instance"] == subject.instance_id:
                return {"source": f"lineage:{link['instance_id']}", "expected": subject.content_id,
                        "witnessed": link["parent_content"]}
            link = self.store.lineage_link(link["parent_instance"])
        return None

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
            "stagedValidation": None if not isinstance(staged, dict) else {k: staged.get(k) for k in ("validationId", "outcome", "summary", "requirementHash", "contextHash", "evaluatedAt", "examinedContentRoot")},
            "untestedPathCount": len(record.get("untestedPaths") or []),
        }

    def _execution_identity(self, subject: World, current: Mapping[str, Any], *,
                            recorded_checks: Sequence[Mapping[str, Any]] = ()) -> dict[str, Any]:
        """What the policy declares each required check should have run, and what the runner
        recorded it was given -- and whether the kernel admits the roster.

        The two identity sides are produced from different data by different code on purpose.
        The expected side is built here from `current_requirements`' resolved verifier list --
        the trusted evaluator specification. The actual side is read from the world's evidence,
        where the check runner wrote what it staged and identified. If one function produced
        both, the equality the kernel proves would be an equality of a value with itself.

        Completeness is the kernel's roster rule (Evaluation.Roster_Complete over one
        Evaluation.Admissible verdict per required check), recomputed here from each raw record
        against the CURRENT policy's declaration. A saved classification is not authority, a
        completed FAIL is not a pass, a record with no execution status is not a completed one,
        and an empty roster counts only when the policy declared it.
        """
        required, empty_declared = required_roster(current)
        declarations = check_declarations(current)
        # The agent's own exit is on every finalization roster and no revalidation re-runs it, so
        # it is judged from the subject's FINALIZATION record, whichever evaluation speaks for the
        # policy checks. Without this, a world DEGRADED by its agent's failure and then ARCHIVED
        # by a sibling's collapse could be re-applied with `return` (the ARCHIVED state erases
        # the DEGRADED one). A subject with no finalization agent record is refused.
        finalization = subject.evidence.get("checks") if subject is not None and isinstance(subject.evidence, dict) else None
        agent_record = next((item for item in (finalization or ()) if isinstance(item, Mapping) and item.get("id") == "agent"), None)
        # Worlds forked before 1.5.0 carry the runner's agent record without `origin`.
        agent_record, legacy_agent = runner_agent_record(agent_record)
        # The slot holds the runner's own agent record and nothing else: a record of another
        # origin (a 1.7.3 policy check that took the id `agent`, say) is not the agent's exit.
        if isinstance(agent_record, Mapping) and agent_record.get("origin") != "agent":
            agent_record = None
        agent = roster_decision(["agent"], {"agent": agent_record} if agent_record is not None else {},
                                {"agent": ENGINE_DECLARATIONS["agent"]}, empty_declared=False, core=self.core)
        declared_bundles: dict[str, list[tuple[str, str, str]]] = {}
        for entry in current.get("verifiers") or ():
            declared_bundles.setdefault(str(entry.get("checkId")), []).append(
                (str(entry.get("rootKey")), str(entry.get("path")), str(entry.get("sha256"))))
        # The execution records of the SAME evaluation whose freshness context speaks for this
        # world -- passed in by the caller from `effective_evidence`, NOT read from the world's
        # finalization evidence. A revalidation carries its own re-run records; using the
        # finalization's here bound run 2's freshness to run 1's execution identity (F5).
        recorded = {str(item.get("id")): item
                    for item in recorded_checks if isinstance(item, Mapping)}
        roster = roster_decision(required, recorded, declarations,
                                 empty_declared=empty_declared, core=self.core)
        refused = {item["id"]: item["reason"] for item in roster["refused"]}
        agent_refused = {item["id"]: item["reason"] for item in agent["refused"]}
        expected_members: list[tuple[str, str, str]] = []
        actual_members: list[tuple[str, str, str]] = []
        # A member the records cannot state is ABSENT, and one absent member makes the whole
        # executed identity absent (1.9.0): no "" or placeholder stands in for it. "Ran no bundle"
        # is a stated fact only when the record carries the executedVerifierSet key with null, or
        # the result is the engine's own.
        actual_absent = False
        for check_id in required:
            bundle = declared_bundles.get(check_id, [])
            expected_members.append(("", check_id, bundle_identity(bundle) if bundle else NO_BUNDLE_IDENTITY))
            record_ = recorded.get(check_id)
            if check_id in refused or not isinstance(record_, Mapping):
                actual_absent = True
                continue
            executed = record_.get("executedVerifierSet")
            if isinstance(executed, Mapping):
                identity = executed.get("identity")
                if isinstance(identity, str) and identity:
                    actual_members.append(("", check_id, identity))
                else:
                    actual_absent = True
            elif ("executedVerifierSet" in record_ and executed is None) or record_.get("origin") == "engine":
                actual_members.append(("", check_id, NO_BUNDLE_IDENTITY))
            else:
                actual_absent = True
        problems = [f"{check_id}: {reason}" for check_id, reason in {**agent_refused, **refused}.items()]
        if not roster["complete"] and not required:
            problems.append("no .worldline.json declares what a collapse requires; add one"
                            " (\"checks\": [] declares that nothing is required)")
        # Two kernel verdicts, both required: the policy roster (which may be empty only when
        # declared) and the agent's own finalization exit.
        complete = roster["complete"] is True and agent["complete"] is True
        return {"complete": complete, "expected": bundle_identity(expected_members),
                "actual": None if actual_absent else bundle_identity(actual_members), "mode": "candidate-evaluation",
                "problems": problems, "requiredChecks": ["agent", *required], "emptyDeclared": empty_declared,
                "legacyAgentRecord": legacy_agent}

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
        #
        # 1.8.0: the actor string alone no longer selects this path. The case is explicit in the
        # kernel (Evaluation_Mode = Checkpoint_Return) and must carry a lineage witness; a
        # WORLDLINE-made world that never became live is refused there as CHECKPOINT_UNWITNESSED.
        checkpoint_return = kind == "return" and subject.actor == "worldline"
        if checkpoint_return:
            return {"mode": "checkpoint-return", "requirementHash": current["requirementHash"], "candidateRequirementHash": None, "policySourceSha256": current["policy"].get("sourceSha256"), "subject": subject.instance_id, "contextHash": None, "source": None,
                    "witness": self._checkpoint_witness(subject), "current": current,
                    # No candidate evaluation exists, and none is claimed: absent, not "complete"
                    # and not a token. The declared verifiers are kept: a staged-merge evaluation
                    # may still have to cover the staged bytes.
                    "execution": {"complete": False, "expected": self._declared_verifiers(current), "actual": None,
                                  "mode": "no-candidate-evaluation", "problems": [], "requiredChecks": []}}
        context, source, recorded_checks = effective_evidence(self.store, subject)
        try:
            # 1.9.0: which world the context is bound to is not decided here; it is carried to
            # the kernel as the evidence subject (EVIDENCE_SUBJECT_MISMATCH).
            context = verify_context(context, candidate_instance=None, core=self.core)
            if context.get("verifiersModifiedByCandidate"):
                raise WorldlineError("VERIFIER_MODIFIED_BY_CANDIDATE", "the candidate changed an authoritative verifier its own evidence depends on", {"verifiers": context["verifiersModifiedByCandidate"]})
            if context["requirementHash"] != current["requirementHash"]:
                raise WorldlineError("EVIDENCE_STALE", "the candidate's evidence was evaluated against different requirements than the current PRIME imposes; revalidate or fork a new candidate", {"differences": differences(context["requirement"], current), "candidateRequirementHash": context["requirementHash"], "currentRequirementHash": current["requirementHash"], "evaluatedAt": context.get("evaluatedAt"), "evidenceSource": source})
        except WorldlineError as exc:
            self.store.append_causal_event({"schemaVersion": SCHEMA_VERSION, "worldInstance": subject.instance_id, "kind": "promotion-refused", "actor": "worldline", "reason": exc.code, "details": exc.details if hasattr(exc, "details") else None, "transactionKind": kind})
            raise
        return {"mode": "re-application" if kind == "return" else "collapse", "requirementHash": current["requirementHash"], "candidateRequirementHash": context["requirementHash"], "contextHash": context["contextHash"], "source": source, "policySourceSha256": current["policy"].get("sourceSha256"), "subject": subject.instance_id, "evaluatedAt": context.get("evaluatedAt"),
                "evidenceInstance": (context.get("candidate") or {}).get("instanceId"),
                "examinedContentRoot": context.get("examinedContentRoot"),
                "current": current,
                "execution": self._execution_identity(subject, current, recorded_checks=recorded_checks)}

    def _finish_committed(
        self,
        record: dict[str, Any],
        staged_manifests: Mapping[str, CapturedManifest] | None = None,
    ) -> dict[str, Any]:
        candidate = self.store.world(record["candidateWorld"])
        moved_offline = False
        if staged_manifests is not None:
            manifests = dict(staged_manifests)
        else:
            manifests, moved_offline = self._recovered_manifests(record)
        manifests_directory = Path(record["stagingPayload"]) / "manifests"
        manifests_directory.mkdir(mode=0o700, exist_ok=True)
        for root_key, manifest in manifests.items():
            manifest.save(manifests_directory / f"{root_key}.json")
        candidate_state = Path(candidate.payload_path) / "manifests"
        for name in ("environment.json", "evidence.json", "agent.json"):
            source = candidate_state / name
            if source.is_file():
                destination = manifests_directory / name
                if destination.exists() and (os.path.samefile(source, destination)
                                             or destination.read_bytes() == source.read_bytes()):
                    continue  # a replay (recovery), or the candidate that became PRIME itself
                # A replay finds the read-only copy it made the first time; replace it rather
                # than open it for writing (review of 19d0297).
                destination.unlink(missing_ok=True)
                shutil.copy2(source, destination)
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
            staged_identity = self._staged_identity(candidate, components, current_prime)
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
        if moved_offline:
            # Live PRIME is not the tree that was committed: something wrote to it while no
            # daemon ran. PRIME records the committed tree; the difference is recorded and PRIME
            # marked dirty, so the next status or prepare reconciles it into its own generation
            # instead of folding it into this collapse.
            prime_now = self.store.prime()
            self.store.set_meta("dirty", True)
            self.store.append_causal_event({"schemaVersion": SCHEMA_VERSION,
                                            "worldInstance": prime_now.instance_id if prime_now is not None else candidate.instance_id,
                                            "kind": "unaccounted-write", "actor": "worldline",
                                            "reason": "live PRIME differed from the committed staged tree at recovery",
                                            "transactionId": record["transactionId"]})
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
                foreign_measurement=(record.get("decisionInputsAtCommit") or record.get("decisionInputs") or {}).get("foreignWrites"),
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
            except OSError as exc:  # as promised above: quarantined, never raised (review of 19d0297)
                error = {"code": "RECOVERY_IO_FAILED", "message": str(exc), "details": {"errno": exc.errno}}
                self.unrecoverable[transaction_id] = error
                recovered.append({"transactionId": transaction_id, "state": "UNRECOVERABLE", "error": error})
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
            except OSError as exc:
                error = {"code": "RECOVERY_IO_FAILED", "message": str(exc), "details": {"errno": exc.errno}}
                self.unrecoverable[transaction_id] = error
                recovered.append({"transactionId": transaction_id, "state": "RECEIPT_UNRECOVERABLE", "error": error})
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
                source=self.paths.root_source(root), logical=bytes(root["path"]), root=root
            )
            for root in self.store.roots()
        }

    def _staged_identity(self, candidate: World, components: Mapping[str, str], current_prime: World) -> str:
        """The content identity the committed tree gets as PRIME: the candidate's own when it is
        the same world, otherwise the checkpoint _finish_committed publishes."""
        return hash_id(
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

    def _checkpoint_collision(self, record: Mapping[str, Any], candidate: World,
                              staged_manifests: Mapping[str, CapturedManifest]) -> World | None:
        """A world that already holds the identity the commit would publish, or None. World
        content ids are unique; a leftover return vehicle can hold exactly that id, and a
        publish that collides after the exchange would leave reality changed with no record
        (review of 19d0297). Checked before the exchange instead."""
        current_prime = self.store.prime()
        if current_prime is None or current_prime.content_id is None:
            return None
        identity = self._staged_identity(candidate, Manifest.component_roots(staged_manifests.values(), self.core), current_prime)
        if identity == candidate.content_id:
            return None  # the candidate itself becomes PRIME; nothing new is published
        try:
            existing = self.store.world(identity)
        except WorldlineError:
            return None
        return None if existing.alias == f"prime-{record['transactionId']}" else existing

    def _recovered_manifests(self, record: Mapping[str, Any]) -> tuple[dict[str, CapturedManifest], bool]:
        """The committed staged tree, for a recovery that finishes an exchange which already
        happened. The live tree IS the staging payload by then; if it still has the staged root
        prepare recorded, it is used. Otherwise the manifests prepare persisted are, when they
        state that root, and the caller records the difference (moved_offline)."""
        live = self._capture_staged(record)
        expected = record.get("stagedRoot")
        if Manifest.root_set_hash(live.values(), self.core) == expected:
            return live, False
        persisted_directory = Path(record["stagingPayload"]).parent / "manifests"
        persisted: dict[str, CapturedManifest] = {}
        for root in self.store.roots():
            path = persisted_directory / f"{root['root_key']}.json"
            if not path.is_file():
                return live, True  # nothing states the committed tree; keep what is live, recorded
            persisted[root["root_key"]] = Manifest.load(path, self.core)
        if Manifest.root_set_hash(persisted.values(), self.core) != expected:
            return live, True
        return persisted, True

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
        # The store records absolute paths. A copy of a store that was not relocated still names
        # the ORIGINAL store's files, and recovery on it would abort the original's transaction and
        # delete its staging (review of a23c265). Nothing outside this store is read or written.
        self._require_own(path, self.paths.transactions, transaction_id, "preparedPath")
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise WorldlineError("TRANSACTION_RECORD_INVALID", f"cannot read prepared transaction {transaction_id}") from exc
        if record.get("schemaVersion") != SCHEMA_VERSION or record.get("transactionId") != transaction_id:
            raise WorldlineError("TRANSACTION_RECORD_INVALID", f"prepared transaction identity mismatch: {transaction_id}")
        self._require_own(Path(str(record.get("preparedPath") or "")), self.paths.transactions, transaction_id, "preparedPath")
        for key in ("stagingPayload", "preparedMapping"):
            if record.get(key) is not None:
                self._require_own(Path(str(record[key])), self.data_transactions / transaction_id, transaction_id, key)
        if row["state"] != record.get("state"):
            raise WorldlineError("TRANSACTION_RECORD_INVALID", f"database and prepared transaction state differ: {transaction_id}")
        return record

    @staticmethod
    def _require_own(path: Path, directory: Path, transaction_id: str, field: str) -> None:
        """Refuse a record path that is not inside this store's own directory for it. Compared
        resolved, so the same store reached through a symlink is still its own (review of
        0ee1112), while a copy's paths resolve into the original and are refused."""
        try:
            own = os.path.realpath(directory)
            inside = os.path.commonpath([os.path.realpath(path), own]) == own
        except ValueError:
            inside = False
        if not path.is_absolute() or not inside:
            raise WorldlineError("TRANSACTION_RECORD_FOREIGN",
                                 f"transaction {transaction_id} names a {field} outside this store; was the store copied without relocating it?",
                                 {"transactionId": transaction_id, "field": field, "path": str(path), "expectedUnder": str(directory)})

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
