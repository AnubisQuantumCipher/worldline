"""Unexecuted ordinary owned v2 controls, retaining the unchanged v1 module."""
import ctypes
import os
import pathlib
import tempfile
import unittest

from worldline.evaluation_pending import PendingJournal
from worldline.pending_kernel import PendingKernel as LegacyKernel, Reason as LegacyReason
from worldline.pending_kernel_v2 import (
    PendingKernel, Intent, Reason, Span, Cursor, Row, Request, Result,
    OptionalRequirement,
)

LIBRARY = pathlib.Path(os.environ["WORLDLINE_CORE_LIB"]).resolve()


class PendingRequirementControls(unittest.TestCase):
    def test_additive_layout_and_legacy_api(self):
        kernel = PendingKernel(LIBRARY)
        self.assertEqual(kernel.library.wl_pending_abi_version_v2(), 2)
        for kind, record in enumerate(
                (Span, Cursor, Row, Request, Result, OptionalRequirement), 1):
            self.assertEqual(kernel.library.wl_pending_layout_size_v2(kind),
                             ctypes.sizeof(record))
            self.assertEqual(kernel.library.wl_pending_layout_alignment_v2(kind),
                             ctypes.alignment(record))
            for field, (name, _) in enumerate(record._fields_, 1):
                self.assertEqual(kernel.library.wl_pending_layout_offset_v2(kind, field),
                                 getattr(record, name).offset)
        legacy = LegacyKernel(LIBRARY)
        plan = legacy.decide([], store_id=b"", subject=b"", content=b"", run=b"",
            authority=None, target=None, proposed_epoch=b"\x01", replay=False)
        self.assertIs(plan.reason, LegacyReason.RESERVE_NEW)

    def test_exact_nullable_requirement_plan_and_replay(self):
        kernel = PendingKernel(LIBRARY)
        for requirement in (None, b"", b"requirement\x00", b"surrogate\xed\xa0\x80"):
            with self.subTest(requirement=requirement):
                plan = kernel.decide([], store_id=b"s", subject=b"w", content=b"c", run=b"r",
                    authority=None, target=None, proposed_epoch=b"\x01", replay=False,
                    requirement=requirement)
                self.assertIs(plan.reason, Reason.RESERVE_NEW)
                self.assertEqual(plan.requirement, requirement)
                row = Intent(b"s", b"w", b"c", b"r", b"\x01", None, True, requirement)
                replay = kernel.decide([row], store_id=b"s", subject=b"w", content=b"c", run=b"r",
                    authority=(b"\x01", b"r"), target=(b"\x01", b"r"), proposed_epoch=b"",
                    replay=True, requirement=requirement)
                self.assertIs(replay.reason, Reason.ALREADY_LINKED)
                self.assertEqual(replay.requirement, requirement)
                other = b"" if requirement is None else None
                refused = kernel.decide([row], store_id=b"s", subject=b"w", content=b"c", run=b"r",
                    authority=(b"\x01", b"r"), target=(b"\x01", b"r"), proposed_epoch=b"",
                    replay=True, requirement=other)
                self.assertIs(refused.reason, Reason.REQUIREMENT_CONFLICT)

    def test_actual_producer_retains_distinct_requirement_values(self):
        with tempfile.TemporaryDirectory(prefix="worldline-requirement-ordinary-") as temp:
            root = pathlib.Path(temp)
            p = PendingJournal(root / "journal.db", root / "target.db", store_id="s",
                               library=LIBRARY, create=True)
            try:
                requirements = (None, "", "requirement\x00\ud800")
                handles = [p.begin("world", "content", value) for value in requirements]
                for handle in handles:
                    self.assertEqual(p.replay(handle.run), handle)
                rows = p.pending_snapshot("world")["history"]
                self.assertEqual(tuple(row["requirementHash"] for row in rows), requirements)
                self.assertEqual([row["validationId"] for row in rows],
                                 [handle.run for handle in handles])
            finally:
                p.close()
