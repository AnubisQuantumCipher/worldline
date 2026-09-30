"""Revalidation: fresh evidence for an intact, already-finalized candidate.

A candidate whose finalization evidence no longer matches the requirements the current PRIME
imposes (policy edited, verifier rewritten, engine upgraded, configuration changed) is refused
at promotion with ``EVIDENCE_STALE``. Revalidation is the documented way back: the CURRENT
PRIME's checks are run again, inside a sandbox, over the candidate's own finalized bytes, and
the resulting validation context is stored beside the world (store meta
``validation:<instance>``), bound to the world's content identity. Only a ``PASS`` outcome
speaks for the world afterwards. A ``FAIL`` does not supersede an earlier ``PASS``: when the
requirements changed, the older evidence is stale anyway and the world stays refused; when
they did not, the earlier ``PASS`` (or the finalization's) still speaks. Letting the latest
evaluation speak is Phase 1's "one effective evaluation" item, not this module's behaviour.

Revalidation never changes the world's state, payload or evidence manifest: those are the
finalization's. The candidate's ``agent`` check is not re-run; it is a property of the run
that produced the bytes, and promotion judges it from the finalization record (1.8.0).
"""
from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Any, Mapping

from . import SCHEMA_VERSION
from .core import Core
from .delta import Delta
from .fstree import remove_tree
from .errors import WorldlineError
from .finalize import (_COPY_SCRIPT, check_declarations, evaluation_record, execution_binding,
                       protected_matches, required_roster, roster_decision)
from .linux.git import GitAdapter
from .linux.namespaces import SandboxSpec
from .manifest import CapturedManifest, Manifest
from .model import WorldState, utc_now
from .paths import secure_directory
from .project import ProjectConfig
from .store import StateStore
from .trusted import trusted_inline
from .validation import content_root_set, build_context, current_requirements, readonly_content_entries, resolve_verifiers


class Revalidator:
    def __init__(self, paths: Any, store: StateStore, config: Any, sandbox: Any, checks: Any, *, core: Core | None = None) -> None:
        self.paths = paths
        self.store = store
        self.config = config
        self.sandbox = sandbox
        self.checks = checks
        self.core = core or Core.shared()
        self.git = GitAdapter(self.core)

    def revalidate(self, world_value: str) -> dict[str, Any]:
        world = self.store.world(world_value)
        if world.state is not WorldState.VALID:
            raise WorldlineError("INVALID_CANDIDATE", f"only a VALID world can be revalidated, got {world.state.value}; fork a new candidate")
        roots = self.store.roots()
        primary = next((r for r in roots if r["primary_root"]), None)
        if primary is None:
            raise WorldlineError("NO_PRIMARY_ROOT", "no primary root is registered")
        payload = Path(world.payload_path)
        if not payload.is_dir():
            raise WorldlineError("PAYLOAD_PRUNED", "the candidate payload no longer exists; fork a new candidate")
        base_payload = Path(world.base_payload_path)
        if not base_payload.is_dir():
            raise WorldlineError("BASE_PAYLOAD_MISSING", "the checkpoint the candidate was forked from no longer exists; fork a new candidate")

        # 1. The bytes under evaluation must be exactly the finalized bytes.
        candidate_manifests: dict[str, CapturedManifest] = {}
        base_manifests: dict[str, CapturedManifest] = {}
        for root in roots:
            root_key = root["root_key"]
            manifest_path = payload / "manifests" / f"{root_key}.json"
            if not manifest_path.is_file():
                raise WorldlineError("PAYLOAD_INTEGRITY_FAILED", f"the candidate has no declared manifest for root {root_key}")
            manifest = Manifest.load(manifest_path, self.core)
            if manifest.value["rootKey"] != root_key or manifest.value["kind"] != root["kind"]:
                raise WorldlineError("PAYLOAD_INTEGRITY_FAILED", f"declared manifest identity differs for root {root_key}")
            Manifest.verify_content(manifest, os.fsencode(payload / root_key), self.core)
            candidate_manifests[root_key] = manifest
            base_manifest_path = base_payload / "manifests" / f"{root_key}.json"
            if base_manifest_path.is_file():
                base_manifests[root_key] = Manifest.load(base_manifest_path, self.core)
            else:
                base_manifests[root_key] = Manifest.capture(
                    base_payload / root_key,
                    logical_root=bytes(root["path"]),
                    root_key=root_key,
                    kind=root["kind"],
                    core=self.core,
                    repository=self.git.capture(base_payload / root_key) if root["kind"] == "repo" else None,
                )
        if Manifest.root_set_hash(base_manifests.values(), self.core) != world.base_root:
            raise WorldlineError("BASE_ROOT_MISMATCH", "the candidate's checkpoint bytes differ from its claimed base")

        # 2–4. Evaluate the candidate's bytes against the CURRENT requirements and bind the
        #      resulting context to this exact world.
        parent = self.store.world(world.parent_instance) if world.parent_instance else None
        entry = self._evaluate(
            source_dir=payload,
            subject={"instanceId": world.instance_id, "alias": world.alias, "baseRoot": world.base_root, "rootSetHash": world.root_set_hash, "missionHash": world.mission_hash},
            prime_at_fork={"instanceId": world.parent_instance, "contentId": world.parent_content, "generation": None if parent is None else parent.instance_id},
            protected_delta=lambda: Delta.compute_all(base_manifests, candidate_manifests, self.core),
            source="revalidation",
            declared=candidate_manifests,
        )
        entry = {"worldInstance": world.instance_id, "worldContentId": world.content_id, **entry}
        key = f"validation:{world.instance_id}"
        history = list(self.store.get_meta(key, []) or [])
        history.append(entry)
        self.store.set_meta(key, history)
        self.store.append_causal_event({"schemaVersion": SCHEMA_VERSION, "worldInstance": world.instance_id, "kind": "revalidation", "actor": "worldline", "outcome": entry["outcome"], "validationId": entry["validationId"], "requirementHash": entry["requirementHash"]})
        return {k: v for k, v in entry.items() if k != "context"} | {"world": world.alias, "state": world.state.value, "checks": len(entry["results"])}

    def validate_staged(self, staging_payload: Path, candidate: Any, current_manifests: Any, staged_manifests: Any, staged_content_root: str) -> dict[str, Any]:
        """Evidence for a staged merge result: the bytes that would become PRIME after a
        three-way merge onto a PRIME that moved since the candidate was forked. The candidate's
        own evidence never covered them, so the current checks run over the staged tree and the
        resulting context is bound to the candidate AND to the staged content root. The
        protected-paths check is evaluated on what would change in PRIME (current -> staged).
        Called by the transaction manager during prepare; a FAIL leaves the kernel's
        STAGED_UNTESTED refusal in force."""
        entry = self._evaluate(
            source_dir=staging_payload,
            subject={"instanceId": candidate.instance_id, "alias": candidate.alias, "baseRoot": candidate.base_root, "rootSetHash": candidate.root_set_hash, "missionHash": candidate.mission_hash, "stagedContentRoot": staged_content_root},
            prime_at_fork={"instanceId": candidate.parent_instance, "contentId": candidate.parent_content, "generation": None},
            protected_delta=lambda: Delta.compute_all(current_manifests, staged_manifests, self.core),
            source="staged",
        )
        self.store.append_causal_event({"schemaVersion": SCHEMA_VERSION, "worldInstance": candidate.instance_id, "kind": "staged-validation", "actor": "worldline", "outcome": entry["outcome"], "validationId": entry["validationId"], "requirementHash": entry["requirementHash"], "stagedContentRoot": staged_content_root})
        return {"stagedContentRoot": staged_content_root, **entry}

    def _evaluate(self, *, source_dir: Path, subject: dict[str, Any], prime_at_fork: dict[str, Any], protected_delta: Any, source: str,
                  declared: Mapping[str, CapturedManifest] | None = None) -> dict[str, Any]:
        roots = self.store.roots()
        primary = next((r for r in roots if r["primary_root"]), None)
        if primary is None:
            raise WorldlineError("NO_PRIMARY_ROOT", "no primary root is registered")
        current = current_requirements(self.store, self.config, self.core)
        project = ProjectConfig.load(Path(os.fsdecode(self.paths.root_source(primary))), self.store)
        # The tree under evaluation is the read-only lower layer of a scratch overlay; nothing a
        # check writes reaches it.
        validation_id = str(uuid.uuid4())
        overlays = self.sandbox.overlay_roots(
            validation_id,
            [(root["root_key"], source_dir / root["root_key"], Path(os.fsdecode(bytes(root["path"])))) for root in roots],
        )
        primary_target = Path(os.fsdecode(bytes(primary["path"])))
        private_id: str | None = None
        # What this evaluation examines, identified before any check runs and verified again
        # after the last one (1.9.0). Promotion compares it with the bytes that would go live;
        # a tree that moved under the checks is refused rather than attributed to either state.
        examined = self._source_manifests(source_dir, roots)
        observed_content_root = content_root_set(examined, self.core)
        if declared is None:
            examined_content_root = observed_content_root
        else:
            # A revalidation examines the finalized payload, which is the declared manifests'
            # bytes made read-only. It is identified by those manifests -- the view promotion
            # compares with the staged tree -- after checking the payload is exactly them apart
            # from the write bits finalization cleared (review of a23c265: identified by the
            # read-only capture, no revalidation could ever cover the staged bytes).
            for key in sorted(examined):
                if key not in declared or readonly_content_entries(examined[key]) != readonly_content_entries(declared[key]):
                    raise WorldlineError("PAYLOAD_INTEGRITY_FAILED",
                                         f"the payload under revalidation is not the bytes its declared manifest states (root {key})")
            examined_content_root = content_root_set(declared, self.core)
        try:
            # THREE snapshots, kept apart:
            #   overlays        the bytes UNDER EVALUATION -- source_dir (for a revalidation, the
            #                   candidate's own finalized payload; for a staged merge, the staged
            #                   tree). This is what the checks examine.
            #   evaluator_sources  the TRUSTED EVALUATOR snapshot -- CURRENT PRIME's on-disk tree,
            #                   the realpath of each registered root. The examiner is staged from
            #                   here, NEVER from the overlay lower. The earlier code read the
            #                   examiner from `r.lower`, i.e. source_dir, so a candidate's own
            #                   payload supplied the examiner that judged it (campaign F6).
            #   project         the policy snapshot, loaded from current PRIME above.
            evaluator_sources = {r["root_key"]: Path(os.fsdecode(self.paths.root_source(r)))
                                 for r in roots}
            verifier_roots = [{"root_key": r.root_key, "path": str(r.target),
                               "primary": str(r.target) == str(primary_target)} for r in overlays]
            prime_verifiers = resolve_verifiers(project, verifier_roots, evaluator_sources)
            legacy: list[Any] = []
            private: list[Any] = []
            for check in project.checks:
                if check.profile == "private-evaluator-v1":
                    private.append(check)
                elif private:
                    raise WorldlineError("CHECK_PROFILE_ORDER_INVALID",
                                         "legacy preparation checks must precede private evaluator checks")
                else:
                    legacy.append(check)
            logical_roots = {root.root_key: str(root.target) for root in overlays}
            results = list(self.checks.run(
                world_instance=validation_id, overlays=overlays, primary_target=primary_target,
                checks=legacy, verifier_sources=evaluator_sources, verifiers=prime_verifiers,
                logical_roots=logical_roots)) if legacy else []
            if private:
                # A revalidation cannot silently promote outputs that only exist in its
                # scratch overlay. The private examiner gets a daemon-owned copy of the merged
                # view, and that view must have the same full manifest as the staged or
                # finalized input. Permissions, timestamps, xattrs and repository state can
                # change an examiner's judgment just as file bytes can. Ordinary preparatory
                # checks may run, but their scratch changes cannot be credited to an unchanged
                # source candidate.
                baseline = examined
                private_id = str(uuid.uuid4())
                snapshot, binding, manifests = self._capture_private_input(
                    validation_id, private_id, overlays, roots, primary_target)
                for root in roots:
                    key = root["root_key"]
                    if baseline[key].canonical != manifests[key].canonical:
                        raise WorldlineError(
                            "REVALIDATION_INPUT_CHANGED",
                            "private revalidation snapshot differs from the finalized or staged input",
                            {"rootKey": key, "sourceManifest": baseline[key].root_hash,
                             "examinedManifest": manifests[key].root_hash},
                        )
                private_overlays = self.sandbox.overlay_roots(
                    private_id,
                    [(root["root_key"], snapshot / root["root_key"],
                      Path(os.fsdecode(bytes(root["path"])))) for root in roots],
                )
                results.extend(self.checks.run(
                    world_instance=private_id, overlays=private_overlays,
                    primary_target=primary_target, checks=private,
                    verifier_sources=evaluator_sources, verifiers=prime_verifiers,
                    logical_roots=logical_roots, candidate_snapshot=binding))
                observed = self._source_manifests(snapshot, roots)
                if any(observed[key].canonical != expected.canonical
                       for key, expected in manifests.items()):
                    raise WorldlineError("CANDIDATE_SNAPSHOT_CHANGED",
                                         "private revalidation input changed during examination")
        finally:
            if private_id is not None:
                self._discard(self.paths.overlays / private_id)
            self._discard(self.paths.overlays / validation_id)
        if content_root_set(self._source_manifests(source_dir, roots), self.core) != observed_content_root:
            raise WorldlineError("REVALIDATION_INPUT_CHANGED",
                                 "the tree under evaluation changed while the checks ran")
        # The roster is the one promotion will impose: the current requirement's required checks
        # plus protected-paths when the policy protects anything, judged by the kernel.
        required, empty_declared = required_roster(current)
        declarations = check_declarations(current)
        # Attach the execution-identity facts to each re-run result, exactly as finalization
        # does, so a promotion that later reads THIS evaluation (F5) sees a coherent execution
        # half rather than falling back to the fork-time evidence.
        for item in results:
            item["executionBinding"] = execution_binding(item)
            item["evaluation"] = evaluation_record(
                item, declared=declarations.get(str(item.get("id"))), core=self.core)
        if project.protected:
            delta = protected_delta()
            touched = sorted({op["pathDisplay"] for op in delta.value["operations"] if protected_matches(tuple(project.protected), op["pathDisplay"])})
            protected_result = {"id": "protected-paths", "kind": "policy", "required": True, "format": "engine", "origin": "engine", "covers": list(project.protected), "status": "FAIL" if touched else "PASS", "touched": touched, "reason": ("protected paths would change: " + ", ".join(touched)) if touched else "no protected path changed"}
            protected_result["executionBinding"] = execution_binding(protected_result)
            protected_result["evaluation"] = evaluation_record(
                protected_result, declared=declarations.get("protected-paths"), core=self.core)
            results.append(protected_result)
        context = build_context(
            requirement=current,
            candidate=subject,
            prime_at_fork=prime_at_fork,
            roots=roots,
            results=results,
            candidate_verifiers=resolve_verifiers(project, roots, {root["root_key"]: source_dir / root["root_key"] for root in roots}),
            adapter={"name": source, "argv": [], "sessionReference": None, "supervision": None},
            evaluated_at=utc_now(),
            core=self.core,
            source=source,
            examined_content_root=examined_content_root,
        )
        results_by_id = {r["id"]: r for r in results}
        roster = roster_decision(required, results_by_id, declarations,
                                 empty_declared=empty_declared, core=self.core)
        failed = [item["id"] for item in roster["refused"]]
        if not roster["complete"] and not failed:
            # Nothing was refused and the kernel still said incomplete: the roster was empty and
            # no policy declared it so. Named, because an empty list must not read as a pass.
            failed.append("roster-undeclared")
        if context["verifiersModifiedByCandidate"]:
            failed.append("verifiers-modified")
        return {
            "schemaVersion": SCHEMA_VERSION,
            "validationId": validation_id,
            "source": source,
            "outcome": "FAIL" if failed else "PASS",
            "summary": "UNASSESSED" if not results else ("PASS" if not failed else "FAIL"),
            "failed": failed,
            "evaluatedAt": context["evaluatedAt"],
            "requirementHash": current["requirementHash"],
            "contextHash": context["contextHash"],
            "examinedContentRoot": examined_content_root,
            # Execution-identity fields are preserved, not projected away: promotion reads the
            # executedVerifierSet identity, executionBinding and evaluation from the evaluation
            # that speaks for the world, and for a revalidation that is THIS entry.
            "results": [{"id": r.get("id"), "format": r.get("format"),
                         # Stated only when the record states it; never defaulted (1.9.0).
                         **({"profile": r["profile"]} if "profile" in r else {}),
                         "status": r.get("status"), "required": r.get("required"),
                         "reason": r.get("reason"), "executedVerifierSet": r.get("executedVerifierSet"),
                         "executionBinding": r.get("executionBinding"), "evaluation": r.get("evaluation"),
                         "exitCode": r.get("exitCode"), "origin": r.get("origin"),
                         "resultChannel": r.get("resultChannel"),
                         "evaluationProfile": r.get("evaluationProfile"),
                         "candidateSnapshot": r.get("candidateSnapshot"),
                         "privateReport": r.get("privateReport"),
                         "evaluatorBoundary": r.get("evaluatorBoundary"),
                         "supervision": r.get("supervision")} for r in results],
            "verifiersModifiedByCandidate": context["verifiersModifiedByCandidate"],
            "context": context,
        }

    def _source_manifests(self, directory: Path, roots: list[dict[str, Any]]) -> dict[str, CapturedManifest]:
        result: dict[str, CapturedManifest] = {}
        for root in roots:
            key = root["root_key"]
            source = directory / key
            result[key] = Manifest.capture(
                source, logical_root=bytes(root["path"]), root_key=key,
                kind=root["kind"], core=self.core,
                repository=self.git.capture(source) if root["kind"] == "repo" else None,
            )
        return result

    def _capture_private_input(
        self, validation_id: str, private_id: str, overlays: Any,
        roots: list[dict[str, Any]], primary_target: Path,
    ) -> tuple[Path, dict[str, Any], dict[str, CapturedManifest]]:
        runtime = secure_directory(self.paths.overlays / validation_id / "private-input")
        materialized = secure_directory(runtime / "materialized")
        arguments: list[str] = []
        overlays_by_key = {root.root_key: root for root in overlays}
        for root in roots:
            key = root["root_key"]
            arguments.extend((str(overlays_by_key[key].target),
                              f"/run/worldline-runtime/materialized/{key}"))
        spec = SandboxSpec(
            instance_id=private_id, argv=trusted_inline(_COPY_SCRIPT, *arguments),
            cwd=primary_target, environment={"PATH": "/usr/bin"},
            roots=tuple(overlays), runtime=runtime,
        )
        process = self.sandbox.launch_world(spec)
        _stdout, stderr = process.process.communicate(timeout=300)
        if process.process.returncode != 0:
            raise WorldlineError("MATERIALIZATION_FAILED",
                                 stderr.decode("utf-8", "replace").strip()
                                 or f"private revalidation materializer exited {process.process.returncode}")
        manifests = self._source_manifests(materialized, roots)
        binding = {
            "worldInstance": private_id,
            "rootSetHash": Manifest.root_set_hash(manifests.values(), self.core),
            "rootManifests": {key: value.root_hash for key, value in sorted(manifests.items())},
            "role": "pre-check-input",
        }
        return materialized, binding, manifests

    @staticmethod
    def _discard(directory: Path) -> None:
        # Candidate-written content: never change a mode through a link it holds (review of 796cb02).
        remove_tree(directory, ignore_errors=True)
