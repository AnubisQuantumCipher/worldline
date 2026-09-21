"""Test support: give a synthetic (never finalized) candidate a validation context that is
fresh against the CURRENT PRIME, so tests that exercise the transaction boundary with
hand-built worlds pass the evidence-freshness gate the way a really finalized world would."""
from __future__ import annotations

from typing import Any

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
    world.evidence = {**(world.evidence if isinstance(world.evidence, dict) else {}), "validationContext": context}
    store.save_world(world)
    return context
