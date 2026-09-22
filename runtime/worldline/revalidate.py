"""Revalidation: fresh evidence for an intact, already-finalized candidate.

A candidate whose finalization evidence no longer matches the requirements the current PRIME
imposes (policy edited, verifier rewritten, engine upgraded, configuration changed) is refused
at promotion with ``EVIDENCE_STALE``. Revalidation is the documented way back: the CURRENT
PRIME's checks are run again, inside a sandbox, over the candidate's own finalized bytes, and
the resulting validation context is stored beside the world (store meta
``validation:<instance>``), bound to the world's content identity. Only a ``PASS`` outcome
speaks for the world afterwards; a ``FAIL`` leaves the stale finalization context in force,
so the world remains refused until a fresh candidate is forked.

Revalidation never changes the world's state, payload or evidence manifest: those are the
finalization's. The candidate's ``agent`` check is not re-run; it is a property of the run
that produced the bytes, and the world's VALID state already records it.
"""
from __future__ import annotations

import os
import shutil
import uuid
from pathlib import Path
from typing import Any

from . import SCHEMA_VERSION
from .core import Core
from .delta import Delta
from .errors import WorldlineError
from .finalize import protected_matches
from .linux.git import GitAdapter
from .manifest import CapturedManifest, Manifest
from .model import WorldState, utc_now
from .project import ProjectConfig
from .store import StateStore
from .validation import build_context, current_requirements, resolve_verifiers


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

    def _evaluate(self, *, source_dir: Path, subject: dict[str, Any], prime_at_fork: dict[str, Any], protected_delta: Any, source: str) -> dict[str, Any]:
        roots = self.store.roots()
        primary = next((r for r in roots if r["primary_root"]), None)
        if primary is None:
            raise WorldlineError("NO_PRIMARY_ROOT", "no primary root is registered")
        current = current_requirements(self.store, self.config, self.core)
        project = ProjectConfig.load(Path(os.fsdecode(bytes(primary["path"]))), self.store)
        # The tree under evaluation is the read-only lower layer of a scratch overlay; nothing a
        # check writes reaches it.
        validation_id = str(uuid.uuid4())
        overlays = self.sandbox.overlay_roots(
            validation_id,
            [(root["root_key"], source_dir / root["root_key"], Path(os.fsdecode(bytes(root["path"])))) for root in roots],
        )
        primary_target = Path(os.fsdecode(bytes(primary["path"])))
        try:
            # Revalidation re-runs the CURRENT PRIME's checks, so the examiner it stages is
            # current PRIME's too — the same lower layer the overlays were built from.
            verifier_roots = [{"root_key": r.root_key, "path": str(r.target),
                               "primary": str(r.target) == str(primary_target)} for r in overlays]
            prime_verifiers = resolve_verifiers(project, verifier_roots,
                                                {r.root_key: r.lower for r in overlays})
            results = list(self.checks.run(
                world_instance=validation_id, overlays=overlays, primary_target=primary_target,
                checks=project.checks, verifiers=prime_verifiers,
                logical_roots={r.root_key: str(r.target) for r in overlays}))
        finally:
            self._discard(self.paths.overlays / validation_id)
        required = [check.id for check in project.checks if check.required]
        if project.protected:
            delta = protected_delta()
            touched = sorted({op["pathDisplay"] for op in delta.value["operations"] if protected_matches(tuple(project.protected), op["pathDisplay"])})
            results.append({"id": "protected-paths", "kind": "policy", "required": True, "format": "engine", "covers": list(project.protected), "status": "FAIL" if touched else "PASS", "touched": touched, "reason": ("protected paths would change: " + ", ".join(touched)) if touched else "no protected path changed"})
            required.append("protected-paths")
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
        )
        statuses = {r["id"]: r.get("status") for r in results}
        failed = [check_id for check_id in required if statuses.get(check_id) != "PASS"]
        if context["verifiersModifiedByCandidate"]:
            failed.append("verifiers-modified")
        return {
            "schemaVersion": SCHEMA_VERSION,
            "validationId": validation_id,
            "source": source,
            "outcome": "FAIL" if failed else "PASS",
            "summary": "UNASSESSED" if not results else ("PASS" if all(r.get("status") == "PASS" for r in results) else "FAIL"),
            "failed": failed,
            "evaluatedAt": context["evaluatedAt"],
            "requirementHash": current["requirementHash"],
            "contextHash": context["contextHash"],
            "results": [{"id": r.get("id"), "status": r.get("status"), "required": r.get("required"), "reason": r.get("reason")} for r in results],
            "verifiersModifiedByCandidate": context["verifiersModifiedByCandidate"],
            "context": context,
        }

    @staticmethod
    def _discard(directory: Path) -> None:
        if not directory.exists():
            return
        for root_dir, dirs, _files in os.walk(directory):
            for name in dirs:
                try:
                    os.chmod(os.path.join(root_dir, name), 0o700)
                except OSError:
                    pass
        shutil.rmtree(directory, ignore_errors=True)
