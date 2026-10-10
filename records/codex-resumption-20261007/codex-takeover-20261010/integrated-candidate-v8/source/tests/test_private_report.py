from __future__ import annotations

import hashlib
import errno
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from worldline.errors import WorldlineError
from worldline.report import MAX_REPORT_BYTES, collect_private_report, prepare_private_report


class PrivateReportCollection(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="worldline-private-report-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.private = prepare_private_report(
            self.root, run_id="run-a", check_id="proof",
            candidate_identity="candidate-a", verifier_identity="verifier-a")

    def collect(self, directory: Path | None = None):
        return collect_private_report(directory or self.private, run_id="run-a", check_id="proof",
                                      candidate_identity="candidate-a", verifier_identity="verifier-a")

    def test_report_bytes_are_bound_to_the_invocation(self) -> None:
        payload = b"Total 1 1 . . .\n"
        (self.private / "report").write_bytes(payload)
        observed, identity = self.collect()
        self.assertEqual(observed, payload)
        self.assertEqual(identity["sha256"], hashlib.sha256(payload).hexdigest())
        self.assertEqual(identity["runId"], "run-a")
        self.assertEqual(identity["checkId"], "proof")
        self.assertEqual(identity["candidateIdentity"], "candidate-a")
        self.assertEqual(identity["verifierIdentity"], "verifier-a")

    def test_missing_report_is_a_named_refusal(self) -> None:
        with self.assertRaises(WorldlineError) as raised:
            self.collect()
        self.assertEqual(raised.exception.code, "REPORT_MISSING")

    def test_a_previous_invocation_cannot_be_relabelled(self) -> None:
        (self.private / "report").write_text("prior run", encoding="utf-8")
        with self.assertRaises(WorldlineError) as raised:
            collect_private_report(self.private, run_id="run-b", check_id="proof",
                                   candidate_identity="candidate-a", verifier_identity="verifier-a")
        self.assertEqual(raised.exception.code, "REPORT_BINDING_INVALID")
        with self.assertRaises(WorldlineError) as raised:
            prepare_private_report(self.root, run_id="run-a", check_id="proof",
                                   candidate_identity="candidate-a", verifier_identity="verifier-a")
        self.assertEqual(raised.exception.code, "REPORT_PATH_INVALID")

    def test_final_and_parent_symlinks_are_refused(self) -> None:
        elsewhere = self.root / "elsewhere"
        elsewhere.mkdir()
        (elsewhere / "report").write_text("forged", encoding="utf-8")
        (self.private / "report").symlink_to(elsewhere / "report")
        with self.assertRaises(WorldlineError) as raised:
            self.collect()
        self.assertEqual(raised.exception.code, "REPORT_PATH_INVALID")
        alias = self.root / "alias"
        alias.symlink_to(elsewhere, target_is_directory=True)
        with self.assertRaises(WorldlineError) as raised:
            self.collect(alias)
        self.assertEqual(raised.exception.code, "REPORT_PATH_INVALID")

    def test_fifo_and_hardlink_are_refused_without_blocking(self) -> None:
        path = self.private / "report"
        os.mkfifo(path)
        with self.assertRaises(WorldlineError) as raised:
            self.collect()
        self.assertEqual(raised.exception.code, "REPORT_PATH_INVALID")
        path.unlink()
        path.write_text("data", encoding="utf-8")
        os.link(path, self.root / "link")
        with self.assertRaises(WorldlineError) as raised:
            self.collect()
        self.assertEqual(raised.exception.code, "REPORT_PATH_INVALID")

    def test_oversized_report_is_refused(self) -> None:
        with (self.private / "report").open("wb") as stream:
            stream.truncate(MAX_REPORT_BYTES + 1)
        with self.assertRaises(WorldlineError) as raised:
            self.collect()
        self.assertEqual(raised.exception.code, "REPORT_TOO_LARGE")

    def test_read_fault_is_a_named_refusal(self) -> None:
        (self.private / "report").write_text("data", encoding="utf-8")
        actual_read = os.read
        reads = 0

        def fault_on_report(descriptor: int, size: int) -> bytes:
            nonlocal reads
            reads += 1
            if reads == 2:
                raise OSError(errno.EIO, "injected read failure")
            return actual_read(descriptor, size)

        with patch("worldline.report.os.read", side_effect=fault_on_report):
            with self.assertRaises(WorldlineError) as raised:
                self.collect()
        self.assertEqual(raised.exception.code, "REPORT_READ_FAILED")


if __name__ == "__main__":
    unittest.main()
