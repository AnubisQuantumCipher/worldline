"""A promotion decision must read its freshness half and its execution half from ONE evaluation.

Campaign F5/F6. Two defects around revalidation:

F5  A revalidation stores a fresh context but the promotion path read the execution identity
    from the world's FINALIZATION evidence, assembling one apparently complete evaluation from
    two runs -- run 2's freshness over run 1's execution binding. The revalidation entry also
    projected its own results down to {id, status, required, reason}, discarding the execution
    facts, so even reading the right entry would have found nothing.

F6  Revalidation built its evaluation overlays from the candidate's payload and then staged the
    examiner from that SAME lower layer -- so the candidate's own bytes supplied the examiner
    that judged it. The trusted evaluator snapshot must be current PRIME, named separately from
    the tree under evaluation.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "runtime"))

from worldline.validation import effective_evidence  # noqa: E402


class _World:
    def __init__(self, instance_id, content_id, evidence):
        self.instance_id = instance_id
        self.content_id = content_id
        self.evidence = evidence


class _Store:
    def __init__(self, meta):
        self._meta = meta

    def get_meta(self, key, default=None):
        return self._meta.get(key, default)


FORK_EXEC = {"id": "exam", "executedVerifierSet": {"identity": "sha256:FORK", "stable": True},
             "executionBinding": "BOUND", "evaluation": {"executionStatus": "COMPLETED"}}
REVAL_EXEC = {"id": "exam", "executedVerifierSet": {"identity": "sha256:REVAL", "stable": True},
              "executionBinding": "BOUND", "evaluation": {"executionStatus": "COMPLETED"}}


class OneCoherentEvaluation(unittest.TestCase):
    def test_finalization_speaks_when_there_is_no_revalidation(self) -> None:
        world = _World("w1", "c1", {"validationContext": {"contextHash": "ctxF"},
                                    "checks": [FORK_EXEC]})
        store = _Store({})
        context, source, records = effective_evidence(store, world)
        self.assertEqual(source, "finalization")
        self.assertEqual(records[0]["executedVerifierSet"]["identity"], "sha256:FORK")

    def test_a_passing_revalidation_supplies_BOTH_halves(self) -> None:
        # The heart of F5: if the revalidation's context speaks, its records must too.
        world = _World("w1", "c1", {"validationContext": {"contextHash": "ctxF"},
                                    "checks": [FORK_EXEC]})
        store = _Store({"validation:w1": [
            {"validationId": "B", "outcome": "PASS", "worldContentId": "c1",
             "context": {"contextHash": "ctxB"}, "results": [REVAL_EXEC]},
        ]})
        context, source, records = effective_evidence(store, world)
        self.assertEqual(source, "revalidation:B")
        self.assertEqual(context["contextHash"], "ctxB")
        # NOT the fork's execution identity.
        self.assertEqual(records[0]["executedVerifierSet"]["identity"], "sha256:REVAL")

    def test_a_failed_revalidation_does_not_speak(self) -> None:
        world = _World("w1", "c1", {"validationContext": {"contextHash": "ctxF"}, "checks": [FORK_EXEC]})
        store = _Store({"validation:w1": [
            {"validationId": "B", "outcome": "FAIL", "worldContentId": "c1",
             "context": {"contextHash": "ctxB"}, "results": [REVAL_EXEC]},
        ]})
        _c, source, records = effective_evidence(store, world)
        self.assertEqual(source, "finalization")
        self.assertEqual(records[0]["executedVerifierSet"]["identity"], "sha256:FORK")

    def test_a_revalidation_for_different_content_does_not_speak(self) -> None:
        world = _World("w1", "c1", {"validationContext": {"contextHash": "ctxF"}, "checks": [FORK_EXEC]})
        store = _Store({"validation:w1": [
            {"validationId": "B", "outcome": "PASS", "worldContentId": "OTHER",
             "context": {"contextHash": "ctxB"}, "results": [REVAL_EXEC]},
        ]})
        _c, source, _r = effective_evidence(store, world)
        self.assertEqual(source, "finalization")

    def test_a_revalidation_missing_execution_facts_cannot_borrow_them(self) -> None:
        # The exact scenario: revalidation B reports PASS but its records lack the execution
        # binding. effective_evidence returns B's (empty) records; it must NOT hand back the
        # fork's, which is what let promotion look complete.
        world = _World("w1", "c1", {"validationContext": {"contextHash": "ctxF"}, "checks": [FORK_EXEC]})
        store = _Store({"validation:w1": [
            {"validationId": "B", "outcome": "PASS", "worldContentId": "c1",
             "context": {"contextHash": "ctxB"},
             "results": [{"id": "exam", "status": "PASS"}]},  # no executedVerifierSet
        ]})
        _c, source, records = effective_evidence(store, world)
        self.assertEqual(source, "revalidation:B")
        self.assertIsNone(records[0].get("executedVerifierSet"))


class RevalidationStoresExecutionFacts(unittest.TestCase):
    """The stored revalidation entry keeps the execution-identity fields, not just id/status."""

    def test_the_projection_preserves_the_execution_fields(self) -> None:
        source = (REPO / "runtime/worldline/revalidate.py").read_text(encoding="utf-8")
        # The stored results projection names each field promotion reads.
        self.assertIn('"executedVerifierSet": r.get("executedVerifierSet")', source)
        self.assertIn('"executionBinding": r.get("executionBinding")', source)
        self.assertIn('"evaluation": r.get("evaluation")', source)

    def test_the_examiner_is_staged_from_current_prime_not_the_candidate(self) -> None:
        # F6: the trusted evaluator snapshot is the realpath of each registered root (current
        # PRIME), passed as verifier_sources -- never the overlay lower (the candidate payload).
        source = (REPO / "runtime/worldline/revalidate.py").read_text(encoding="utf-8")
        self.assertIn("evaluator_sources = {r[\"root_key\"]: Path(os.path.realpath(", source)
        self.assertIn("verifier_sources=evaluator_sources", source)
        # And it is NOT read from r.lower anywhere in _evaluate.
        evaluate = source[source.index("def _evaluate"):]
        self.assertNotIn("r.lower for r in overlays", evaluate)


if __name__ == "__main__":
    unittest.main()
