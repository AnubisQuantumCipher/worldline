from __future__ import annotations

import unittest

from worldline.checks import CheckRunner
from worldline.project import CheckSpec


class ReportParserBoundaries(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = object.__new__(CheckRunner)

    @staticmethod
    def check(format_name: str, profile: str = "legacy") -> CheckSpec:
        return CheckSpec("exam", "tests", ("/usr/bin/true",), None, True,
                         format_name, None, (), (), profile)

    def test_junit_requires_a_nonempty_consistent_suite_without_dtd(self) -> None:
        check = self.check("junit")
        passing = b'<testsuite tests="1" failures="0" errors="0" skipped="0"/>'
        self.assertEqual(self.parser._parse(check, 0, b"", b"", passing)["status"], "PASS")
        for report in (
            b"<other/>",
            b"<testsuites/>",
            b'<testsuite tests="0" failures="0" errors="0" skipped="0"/>',
            b'<testsuite tests="1" failures="2" errors="0" skipped="0"/>',
            b'<!DOCTYPE testsuite [<!ENTITY pass "ok">]><testsuite tests="1"/>',
        ):
            with self.subTest(report=report):
                self.assertEqual(self.parser._parse(check, 0, b"", b"", report)["status"], "FAIL")

    def test_gnatprove_requires_finite_nonempty_consistent_total_and_private_report(self) -> None:
        check = self.check("gnatprove", "private-evaluator-v1")
        passing = b"Total 7 2 (29%) 5 (71%) . .\n"
        self.assertEqual(self.parser._parse(check, 0, b"", b"", passing)["status"], "PASS")
        self.assertEqual(self.parser._parse(check, 0, passing, b"", None)["status"], "FAIL")
        for report in (
            b"Total 0 . . . .\n",
            b"Total 7 2 4 . .\n",
            b"Total 7 not-a-number 5 . .\n",
            b"Total -1 . . . .\n",
        ):
            with self.subTest(report=report):
                self.assertEqual(self.parser._parse(check, 0, b"", b"", report)["status"], "FAIL")

    def test_benchmark_rejects_nonfinite_and_empty_metric(self) -> None:
        check = self.check("worldline-benchmark-v1")
        for report in (
            b'{"metric":"time","unit":"ns","baseline":NaN,"candidate":1,"direction":"lower-is-better"}',
            b'{"metric":"","unit":"ns","baseline":2,"candidate":1,"direction":"lower-is-better"}',
        ):
            with self.subTest(report=report):
                self.assertEqual(self.parser._parse(check, 0, b"", b"", report)["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
