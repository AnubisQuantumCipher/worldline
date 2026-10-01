"""Ordinary owned complete-history controls against the selected real library."""
from __future__ import annotations

import ctypes
from dataclasses import replace
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
from worldline.core import Core
from worldline.errors import CoreUnavailable, WorldlineError
from worldline.evaluation_history import (
    EvaluationCursor as Cursor, EvaluationQuery as Query, EvaluationRecord as Row,
    RecordReference, select_history, _api, _Row, _Query, _Selection,
    _Identity, _Epoch, _Cursor, REASONS,
)
from worldline.validation import effective_evidence_at_cursor


class EvaluationHistoryControls(unittest.TestCase):
    def row(self, *, epoch=0, run="final-run", requirement="policy", state="COMPLETED", outcome="PASS"):
        return Row("subject", "content", requirement, run, epoch, state, outcome)

    def query(self, *, epoch=0, run="final-run", requirement="policy"):
        return Query("subject", "content", requirement, Cursor(epoch, run), Cursor(epoch, run))

    def test_actual_finalization_and_absent_evidence(self):
        answer = select_history([], self.row(), self.query())
        self.assertEqual(answer.reason, "READY")
        self.assertEqual(answer.head, RecordReference("FINALIZATION"))
        self.assertEqual(answer.completed_failure, RecordReference("ABSENT"))
        self.assertEqual(select_history([], None, self.query()).reason, "EVIDENCE_ABSENT")

    def test_complete_string_identity_not_digest_or_prefix(self):
        for subject in ("", "a\x00b", "é", "e\u0301", "\ud800", "世界🌍" * 20):
            with self.subTest(subject=repr(subject)):
                final = replace(self.row(), subject=subject, content=subject, run=subject, requirement=subject)
                query = Query(subject, subject, subject, Cursor(0, subject), Cursor(0, subject))
                self.assertEqual(select_history([], final, query).reason, "READY")
                changed = replace(query, current_head=Cursor(0, subject + "suffix"))
                self.assertEqual(select_history([], final, changed).reason, "EVIDENCE_SUPERSEDED")

    def test_same_full_identity_at_separate_arena_offsets_matches(self):
        run = "a long complete run identity with a shared prefix:" + "tail"
        row = self.row(epoch=1, run=run)
        q = self.query(epoch=1, run=run)
        answer = select_history([row], self.row(), q)
        self.assertEqual(answer.reason, "READY")
        self.assertEqual(answer.head, RecordReference("HISTORY_ENTRY", 0))

    def test_newest_completed_fail_supersedes_old_pass(self):
        failed = self.row(epoch=1, run="run-one", outcome="FAIL")
        answer = select_history([failed], self.row(), self.query(epoch=1, run="run-one"))
        self.assertEqual(answer.reason, "EVIDENCE_FAIL_TERMINAL")
        self.assertEqual(answer.head, RecordReference("HISTORY_ENTRY", 0))
        self.assertEqual(answer.completed_failure, RecordReference("HISTORY_ENTRY", 0))

    def test_later_pass_cannot_clear_same_requirement_fail(self):
        failed = self.row(epoch=1, run="run-one", outcome="FAIL")
        passed = self.row(epoch=2, run="run-two")
        answer = select_history([failed, passed], self.row(), self.query(epoch=2, run="run-two"))
        self.assertEqual(answer.reason, "EVIDENCE_FAIL_TERMINAL")
        self.assertEqual(answer.head, RecordReference("HISTORY_ENTRY", 1))
        self.assertEqual(answer.completed_failure, RecordReference("HISTORY_ENTRY", 0))

    def test_changed_requirement_and_switchback_do_not_search_backward(self):
        failed = self.row(epoch=1, run="run-one", outcome="FAIL")
        passed = self.row(epoch=2, run="run-two", requirement="new-policy")
        new = self.query(epoch=2, run="run-two", requirement="new-policy")
        self.assertEqual(select_history([failed, passed], self.row(), new).reason, "READY")
        old = replace(new, requirement="policy")
        self.assertEqual(select_history([failed, passed], self.row(), old).reason, "REQUIREMENT_CHANGED")

    def test_retained_pending_error_and_fence_never_revive_finalization(self):
        for state, reason in (("PENDING", "EVALUATION_INCOMPLETE"),
                              ("ERROR", "EVALUATION_INCOMPLETE"),
                              ("ROLLBACK_FENCE", "EVIDENCE_FENCED")):
            with self.subTest(state=state):
                row = self.row(epoch=1, run="run-one", state=state, outcome=None)
                answer = select_history([row], self.row(), self.query(epoch=1, run="run-one"))
                self.assertEqual(answer.reason, reason)
                self.assertEqual(answer.head, RecordReference("HISTORY_ENTRY", 0))
                self.assertEqual(answer.completed_failure.kind, "ABSENT")

    def test_missing_epochs_are_absent_not_zero_or_list_position(self):
        row = self.row(epoch=None, run="run-one")
        self.assertEqual(select_history([row], self.row(), self.query(epoch=1, run="run-one")).reason,
                         "HISTORY_INVALID")
        q = replace(self.query(), current_head=Cursor(None, "final-run"))
        self.assertEqual(select_history([], self.row(), q).reason, "INPUT_ABSENT")
        self.assertEqual(select_history([], self.row(epoch=None), self.query()).reason, "FINALIZATION_INVALID")

    def test_every_row_subject_content_order_and_run_is_validated(self):
        q = self.query(epoch=1, run="run-one")
        first = self.row(epoch=1, run="run-one")
        for row in (replace(first, subject="other"), replace(first, content="other"),
                    replace(first, epoch=2), replace(first, run="final-run"),
                    replace(first, state="PENDING"), replace(first, outcome=None)):
            self.assertEqual(select_history([row], self.row(), q).reason, "HISTORY_INVALID")
        duplicate = replace(first, epoch=2)
        self.assertEqual(select_history([first, duplicate], self.row(), q).reason, "HISTORY_INVALID")

    def test_finalization_fail_latch_precedes_history_failure(self):
        final = self.row(outcome="FAIL")
        row = self.row(epoch=1, run="run-one", outcome="FAIL")
        answer = select_history([row], final, self.query(epoch=1, run="run-one"))
        self.assertEqual(answer.reason, "EVIDENCE_FAIL_TERMINAL")
        self.assertEqual(answer.completed_failure, RecordReference("FINALIZATION"))

    def test_both_complete_cursor_identities_must_match(self):
        q = self.query()
        for changed in (replace(q, current_head=Cursor(1, "final-run")),
                        replace(q, prepared_evidence=Cursor(0, "final-run-suffix"))):
            self.assertEqual(select_history([], self.row(), changed).reason, "EVIDENCE_SUPERSEDED")

    def test_arbitrary_magnitude_epoch_reaches_typed_selector_without_truncation(self):
        # JACKAL status=exact parsed=2^128; informational fixture, not proof.
        huge = 340282366920938463463374607431768211456
        q = replace(self.query(), current_head=Cursor(huge, "final-run"))
        self.assertEqual(select_history([], self.row(), q).reason, "EVIDENCE_SUPERSEDED")
        # A huge first epoch is invalid history, not a transport-width failure.
        self.assertEqual(select_history([self.row(epoch=huge, run="run-one")],
            self.row(), self.query(epoch=huge, run="run-one")).reason, "HISTORY_INVALID")

    def test_owned_transport_absence_and_invalid_span(self):
        raw = (ctypes.c_uint8 * 1)(0)
        q, final, answer = _Query(), _Row(), _Selection()
        # Ordinary typed absent inputs ignore unused extent fields.
        q.subject.first = ctypes.c_size_t(-1).value
        code = _api(Core.shared())(raw, len(raw), (_Row * 0)(), 0,
                                  0, ctypes.byref(final), ctypes.byref(q), ctypes.byref(answer))
        self.assertEqual(code, 0)
        self.assertEqual(answer.reason, 0)  # INPUT_ABSENT, no ignored payload read.
        present = _Identity(1, 1, 1)
        observed = _Cursor(1, _Epoch(1, 1, 0), present)
        q = _Query(_Identity(1, 2, 1), present, present, observed, observed)
        final = _Row(present, present, present, present, _Epoch(1, 1, 0), 3, 1)
        code = _api(Core.shared())(raw, len(raw), (_Row * 0)(), 0,
                                  1, ctypes.byref(final), ctypes.byref(q), ctypes.byref(answer))
        self.assertEqual(code, 0)
        self.assertEqual(REASONS[answer.reason], "INPUT_INVALID")

    def test_no_api_schema_or_counter_fallback(self):
        with self.assertRaises(CoreUnavailable):
            select_history([], self.row(), self.query(), core=SimpleNamespace(_lib=object()))
        for epoch in (-1, True):
            with self.assertRaises(CoreUnavailable):
                select_history([], self.row(epoch=epoch), self.query())
        with self.assertRaises(CoreUnavailable):
            select_history([object()], self.row(), self.query())

    def snapshot_row(self, row):
        return {"worldInstance": row.subject, "worldContentId": row.content,
                "requirementHash": row.requirement, "validationId": row.run,
                "evaluationEpoch": row.epoch, "evaluationState": row.state,
                "outcome": row.outcome, "context": {"run": row.run},
                "results": [{"id": "check", "fromRun": row.run, "extra": ["retained"]}]}

    def test_additive_real_caller_returns_only_coherent_selected_payload(self):
        row = self.snapshot_row(self.row(epoch=1, run="new-run"))
        snapshot = {"schemaVersion": 1, "finalization": self.snapshot_row(self.row()), "history": [row]}
        reads = []
        def get_meta(key, default):
            reads.append(key); return snapshot
        store = SimpleNamespace(get_meta=get_meta)
        world = SimpleNamespace(instance_id="subject", content_id="content")
        context, source, results = effective_evidence_at_cursor(store, world, requirement_hash="policy",
            current_head=Cursor(1, "new-run"), prepared_evidence=Cursor(1, "new-run"))
        self.assertIs(context, row["context"])
        self.assertIs(results, row["results"])
        self.assertEqual(source, "revalidation:new-run")
        self.assertEqual(reads, ["evaluation-history-v1:subject"])

    def test_additive_real_caller_does_not_fallback_on_fail_or_missing_schema(self):
        world = SimpleNamespace(instance_id="subject", content_id="content")
        snapshot = {"schemaVersion": 1, "finalization": self.snapshot_row(self.row()),
                    "history": [self.snapshot_row(self.row(epoch=1, run="new-run", outcome="FAIL"))]}
        store = SimpleNamespace(get_meta=lambda key, default: snapshot)
        with self.assertRaises(WorldlineError) as caught:
            effective_evidence_at_cursor(store, world, requirement_hash="policy",
                current_head=Cursor(1, "new-run"), prepared_evidence=Cursor(1, "new-run"))
        self.assertEqual(caught.exception.code, "EVIDENCE_FAIL_TERMINAL")
        store.get_meta = lambda key, default: None
        with self.assertRaises(WorldlineError) as caught:
            effective_evidence_at_cursor(store, world, requirement_hash="policy",
                current_head=None, prepared_evidence=None)
        self.assertEqual(caught.exception.code, "EVALUATION_HISTORY_UNAVAILABLE")


if __name__ == "__main__":
    unittest.main()
