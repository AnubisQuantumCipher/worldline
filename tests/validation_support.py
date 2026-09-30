"""Test support: give a synthetic (never finalized) candidate a validation context that is
fresh against the CURRENT PRIME, so tests that exercise the transaction boundary with
hand-built worlds pass the evidence-freshness gate the way a really finalized world would."""
from __future__ import annotations

from typing import Any

from worldline.finalize import CheckDeclaration, evaluation_record
from worldline.model import World, utc_now
from worldline.store import StateStore
from worldline.validation import build_context, current_requirements


def attach_fresh_context(store: StateStore, world: World, *, config: Any | None = None, core: Any | None = None, results: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    current = current_requirements(store, config, core)
    context = build_context(
        requirement=current,
        candidate={"instanceId": world.instance_id, "alias": world.alias, "baseRoot": world.base_root, "rootSetHash": world.root_set_hash, "missionHash": world.mission_hash},
        prime_at_fork={"instanceId": world.parent_instance, "contentId": world.parent_content, "generation": None},
        roots=store.roots(),
        results=list(results or []),
        candidate_verifiers=[],
        adapter={"name": "fixture", "argv": [], "sessionReference": None, "supervision": None},
        evaluated_at=utc_now(),
        core=core,
    )
    evidence = dict(world.evidence) if isinstance(world.evidence, dict) else {}
    # A really finalized world always carries its agent's own exit, and promotion (1.8.0) judges
    # it from there; a hand-built candidate gets the same passing record.
    checks = [item for item in (evidence.get("checks") or []) if isinstance(item, dict)]
    if not any(item.get("id") == "agent" for item in checks):
        checks = [agent_pass_result(), *checks]
    world.evidence = {**evidence, "checks": checks, "validationContext": context}
    store.save_world(world)
    return context


# A policy that explicitly declares no checks. From 1.8.0 an empty promotion roster counts only
# when a policy declared it; a project with no .worldline.json has declared nothing.
DECLARED_EMPTY_POLICY: dict[str, Any] = {"schemaVersion": 1, "generated": [], "checks": [], "services": []}


def matching_declaration(result: dict[str, Any]) -> CheckDeclaration:
    """The declaration a policy would have made for exactly this record.

    For unit tests of classification and report integrity, which are about the record, not
    about whether it matches a policy. Declaration mismatch has its own tests. WORLDLINE's own
    results (origin agent or engine) are declared by origin with no profile (1.9.0).
    """
    if result.get("origin") in ("agent", "engine"):
        return CheckDeclaration(result.get("format"), None, False, origin=result["origin"])
    return CheckDeclaration(result.get("format"), result.get("profile", "legacy"),
                            result.get("executedVerifierSet") is not None)


def evaluate(result: dict[str, Any]) -> dict[str, Any]:
    """evaluation_record against the record's own matching declaration (see above). A policy
    record states its profile, as the runner always writes it (1.9.0 no longer defaults it)."""
    if result.get("origin") not in ("agent", "engine") and "profile" not in result:
        result = {**result, "profile": "legacy"}
    return evaluation_record(result, declared=matching_declaration(result))


def agent_pass_result() -> dict[str, Any]:
    """The agent's own supervised exit-0 record, as the runner writes it (the kernel classifies
    it COMPLETED/PASS). For finalization unit tests, whose roster always holds the agent."""
    return {"id": "agent", "kind": "build", "required": True, "format": "exit", "covers": [],
            "argv": [], "exitCode": 0, "origin": "agent", "status": "PASS",
            "supervision": {"kind": "SUPERVISED"}}
