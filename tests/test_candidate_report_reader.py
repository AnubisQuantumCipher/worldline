from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest

from worldline.checks import CheckRunner
from worldline.linux.namespaces import OverlayRoot
from worldline.project import CheckSpec
from worldline.report import MAX_REPORT_BYTES


class CandidateReportReader(unittest.TestCase):
    def test_result_lookup_stays_inside_upper_and_is_bounded(self) -> None:
        with tempfile.TemporaryDirectory(prefix="worldline-candidate-report-") as temporary:
            base = Path(temporary)
            upper = base / "upper"
            upper.mkdir()
            outside = base / "outside"
            outside.mkdir()
            (outside / "report.xml").write_bytes(b"outside-content")
            target = Path("/tmp/worldline-candidate-report")
            root = OverlayRoot("root", base, upper, base / "work", target)
            check = CheckSpec("exam", "tests", ("/usr/bin/true",), None, True,
                              "junit", "report.xml", ())
            reader = object.__new__(CheckRunner)

            (upper / "report.xml").write_bytes(b"inside-content")
            self.assertEqual(reader._read_result_file(check, (root,), target), b"inside-content")
            (upper / "report.xml").unlink()

            # A final symlink, a symlinked parent and an external hard link must never make
            # the daemon read an arbitrary host file as a candidate report.
            (upper / "report.xml").symlink_to(outside / "report.xml")
            self.assertIsNone(reader._read_result_file(check, (root,), target))
            (upper / "report.xml").unlink()
            (upper / "nested").symlink_to(outside, target_is_directory=True)
            nested = CheckSpec("exam", "tests", ("/usr/bin/true",), None, True,
                               "junit", "nested/report.xml", ())
            self.assertIsNone(reader._read_result_file(nested, (root,), target))
            (upper / "nested").unlink()
            os.link(outside / "report.xml", upper / "report.xml")
            self.assertIsNone(reader._read_result_file(check, (root,), target))
            (upper / "report.xml").unlink()

            # Large report content is rejected before parsing or allocation.
            with (upper / "report.xml").open("wb") as stream:
                stream.truncate(MAX_REPORT_BYTES + 1)
            self.assertIsNone(reader._read_result_file(check, (root,), target))


if __name__ == "__main__":
    unittest.main()
