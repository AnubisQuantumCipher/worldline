"""Unexecuted ordinary controls, always using the explicit real shared library
and fresh caller-owned temporary directories. No fault injection or live paths.
"""
import pathlib
import os
import tempfile
import unittest
import ctypes

from worldline.evaluation_pending import PendingJournal, PendingRefused, previous_cursor
from worldline.pending_kernel import PendingKernel, Intent, Reason, Span, Cursor, Row, Request, Result


LIBRARY = pathlib.Path(os.environ["WORLDLINE_CORE_LIB"]).resolve()


class OrdinaryPending(unittest.TestCase):
    def test_append_and_exact_duplicate_replay(self):
        with tempfile.TemporaryDirectory(prefix="worldline-pending-ordinary-") as temp:
            root = pathlib.Path(temp)
            p = PendingJournal(root / "retained.db", root / "pending.db",
                               store_id="private-test-store", library=LIBRARY, create=True)
            try:
                first = p.begin("subject", "content", "requirement")
                second = p.begin("subject", "content", "requirement")
                self.assertEqual(first.epoch, 1)
                # Retained JACKAL status=exact parsed=1+1 exact=2.
                self.assertEqual(second.epoch, 2)
                self.assertNotEqual(first.run, second.run)
                self.assertEqual(p.replay(first.run), first)
                self.assertEqual(p.replay(second.run), second)
                snapshot = p.pending_snapshot("subject")
                self.assertEqual([r["validationId"] for r in snapshot["history"]],
                                 [first.run, second.run])
                self.assertTrue(all(r["evaluationState"] == "PENDING" and
                                    r["outcome"] is None and r["results"] == []
                                    for r in snapshot["history"]))
                self.assertIsNone(snapshot["finalization"])
            finally:
                p.close()

    def test_lossless_strings_absence_and_reopen(self):
        with tempfile.TemporaryDirectory(prefix="worldline-pending-ordinary-") as temp:
            root = pathlib.Path(temp)
            subject, content = "subject\ud800\x00", "content\U0001d11e"
            p = PendingJournal(root / "retained.db", root / "pending.db",
                               store_id="", library=LIBRARY, create=True)
            handle = p.begin(subject, content, None)
            p.close()
            reopened = PendingJournal(root / "retained.db", root / "pending.db",
                                      store_id="", library=LIBRARY)
            try:
                self.assertEqual(reopened.replay(handle.run), handle)
                row = reopened.pending_snapshot(subject)["history"][0]
                self.assertEqual(row["worldInstance"], subject)
                self.assertEqual(row["worldContentId"], content)
                self.assertIsNone(row["requirementHash"])
                self.assertEqual(row["evaluationEpoch"], handle.epoch)
            finally:
                reopened.close()


    def test_complete_previous_pair_decoder(self):
        self.assertIsNone(previous_cursor(None, None))
        self.assertEqual(previous_cursor(b"", b""), (b"", b""))
        self.assertEqual(previous_cursor(b"\x01", b"run\x00"), (b"\x01", b"run\x00"))
        for epoch, run in ((None, b""), (b"", None)):
            with self.subTest(epoch=epoch, run=run):
                with self.assertRaises(PendingRefused) as caught:
                    previous_cursor(epoch, run)
                self.assertEqual(str(caught.exception), "PREVIOUS_CURSOR_PARTIAL")

    def test_staged_retained_intent_discovered_after_reopen_without_handle(self):
        with tempfile.TemporaryDirectory(prefix="worldline-pending-ordinary-") as temp:
            root = pathlib.Path(temp)
            p = PendingJournal(root / "retained.db", root / "pending.db",
                               store_id="private-test-store", library=LIBRARY, create=True)
            try:
                # Legitimate public journal-only stage, not a failed/crash call.
                # The returned handle is intentionally not used for discovery.
                p.reserve_pending("subject", "content", "requirement")
                with self.assertRaises(PendingRefused):
                    p.pending_snapshot("subject")
            finally:
                p.close()
            reopened = PendingJournal(root / "retained.db", root / "pending.db",
                                      store_id="private-test-store", library=LIBRARY)
            try:
                before = (tuple(reopened.journal.iterdump()), tuple(reopened.target.iterdump()))
                discovered = reopened.discover_pending()
                self.assertEqual([h.subject for h in discovered], ["subject"])
                self.assertEqual([h.content for h in discovered], ["content"])
                self.assertEqual([h.epoch for h in discovered], [1])
                self.assertEqual(reopened.discover_pending(), discovered)
                self.assertEqual((tuple(reopened.journal.iterdump()),
                                  tuple(reopened.target.iterdump())), before)
                handle = discovered[0]
                self.assertEqual(reopened.replay(handle.run), handle)
                self.assertEqual(reopened.discover_pending(), ())
                self.assertEqual(reopened.replay(handle.run), handle)
                snapshot = reopened.pending_snapshot("subject")
                self.assertEqual([r["validationId"] for r in snapshot["history"]], [handle.run])
                self.assertEqual(snapshot["history"][0]["evaluationState"], "PENDING")
            finally:
                reopened.close()

    def test_discovery_is_global_and_retains_every_subject(self):
        with tempfile.TemporaryDirectory(prefix="worldline-pending-ordinary-") as temp:
            root = pathlib.Path(temp)
            p = PendingJournal(root / "retained.db", root / "pending.db",
                               store_id="private-test-store", library=LIBRARY, create=True)
            try:
                self.assertEqual(p.discover_pending(), ())
                first = p.reserve_pending("subject-a", "content", None)
                second = p.reserve_pending("subject-b", "content", "")
                discovered = p.discover_pending()
                self.assertEqual({h.subject: h for h in discovered},
                                 {"subject-a": first, "subject-b": second})
                self.assertEqual(p.replay(first.run), first)
                self.assertEqual(p.discover_pending(), (second,))
                self.assertEqual(p.replay(second.run), second)
                self.assertEqual(p.discover_pending(), ())
                # Existing completed begin/replay path still allocates through
                # the exact kernel relation and does not revive older records.
                next_handle = p.begin("subject-a", "content", None)
                self.assertNotEqual(next_handle.run, first.run)
                self.assertEqual(p.replay(first.run), first)
                self.assertEqual(p.pending_snapshot("subject-a")["history"][-1]["validationId"],
                                 next_handle.run)
            finally:
                p.close()


class OrdinaryOwnedTransport(unittest.TestCase):
    def test_actual_compiler_layout_matches_owned_records(self):
        kernel = PendingKernel(LIBRARY)
        self.assertEqual(kernel.library.wl_pending_abi_version_v1(), 1)
        for kind, record in enumerate((Span, Cursor, Row, Request, Result), 1):
            with self.subTest(record=record.__name__):
                self.assertEqual(kernel.library.wl_pending_layout_size_v1(kind),
                                 ctypes.sizeof(record))
                self.assertEqual(kernel.library.wl_pending_layout_alignment_v1(kind),
                                 ctypes.alignment(record))
                for field, (name, _) in enumerate(record._fields_, 1):
                    self.assertEqual(kernel.library.wl_pending_layout_offset_v1(kind, field),
                                     getattr(record, name).offset)

    def test_owned_empty_arena_is_a_typed_refusal(self):
        kernel = PendingKernel(LIBRARY)
        plan = kernel.decide([], store_id=b"", subject=b"", content=b"", run=b"",
            authority=None, target=None, proposed_epoch=b"", replay=False)
        self.assertIs(plan.reason, Reason.EPOCH_PROPOSAL_INVALID)
        self.assertEqual(plan.epoch, b"")
        self.assertEqual(plan.selected, 0)

    def test_owned_row_stride_preserves_complete_replay_identity(self):
        kernel = PendingKernel(LIBRARY)
        first = Intent(b"store", b"subject", b"content", b"first\x00", b"\x01", None, True)
        # The same ordinary successor values occur in the preserved producer
        # controls; their retained JACKAL receipt is status=exact parsed=1+1.
        second = Intent(b"store", b"subject", b"content", b"second\x00", b"\x02",
                        (first.epoch, first.run), False)
        rows = [first, second]
        plan = kernel.decide(rows, store_id=first.store_id, subject=first.subject,
            content=first.content, run=second.run,
            authority=(second.epoch, second.run), target=(first.epoch, first.run),
            proposed_epoch=b"", replay=True)
        self.assertIs(plan.reason, Reason.WRITE_PENDING)
        self.assertEqual(plan.epoch, second.epoch)
        self.assertEqual(plan.selected, len(rows))
        self.assertEqual(rows, [first, second])


if __name__ == "__main__":
    unittest.main()
