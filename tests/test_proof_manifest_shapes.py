"""Local JSON-shape and CLI-mode contracts for the proof gate.

These fixtures exercise data validation only; they do not substitute a library,
run a daemon, or establish proof provenance.
"""
from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from worldline import proof_manifest as checks

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("proof_gate_cli_shapes", ROOT / "verify_proof_manifest.py")
cli = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(cli)


class ManifestShapes(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.good = json.loads((ROOT / "proof-manifest.json").read_text())

    def findings(self, value):
        return checks.manifest_findings(value, ROOT)

    def test_current_manifest_source_checks_pass(self) -> None:
        self.assertEqual(self.findings(self.good), [])

    def test_non_object_manifest_and_coverage_are_named(self) -> None:
        for value in (None, [], "manifest"):
            with self.subTest(value=value):
                self.assertIn("manifest", [name for name, _ in self.findings(value)])
        for value in (None, [], "coverage"):
            with self.subTest(coverage=value):
                manifest = copy.deepcopy(self.good)
                manifest["coverage"] = value
                self.assertIn("coverage", [name for name, _ in self.findings(manifest)])

    def test_boundary_is_a_unique_string_list(self) -> None:
        boundary = self.good["coverage"]["unanalyzedBoundary"]
        for value in (None, {"worldline-c_api": True}, [None], [[]], boundary + boundary):
            with self.subTest(value=value):
                manifest = copy.deepcopy(self.good)
                manifest["coverage"]["unanalyzedBoundary"] = value
                self.assertIn("coverage", [name for name, _ in self.findings(manifest)])

    def test_unit_counts_are_nonnegative_integers(self) -> None:
        unit = next(iter(self.good["coverage"]["units"]))
        for value in (True, "1", None, -1):
            with self.subTest(value=value):
                manifest = copy.deepcopy(self.good)
                manifest["coverage"]["units"][unit] = {"analyzed": value, "available": value}
                self.assertIn("coverage", [name for name, _ in self.findings(manifest)])

    def test_subprogram_counts_are_nonnegative_integers(self) -> None:
        name = next(iter(self.good["coverage"]["subprograms"]))
        for value in (True, "1", None, -1):
            with self.subTest(value=value):
                manifest = copy.deepcopy(self.good)
                manifest["coverage"]["subprograms"][name]["checks"] = value
                self.assertIn("coverage", [kind for kind, _ in self.findings(manifest)])

    def test_print_pins_cannot_replace_requested_verification(self) -> None:
        for options in (["--print-contract-pins", "--require-summary"],
                        ["--sources-only", "--print-contract-pins"],
                        ["--print-contract-pins", "--unknown"]):
            with self.subTest(options=options), patch.object(sys, "argv", ["gate", *options]), \
                    patch.object(cli, "contract_pin") as pin, \
                    contextlib.redirect_stderr(io.StringIO()) as errors:
                self.assertEqual(cli.main(), 2)
                self.assertIn("cannot be combined", errors.getvalue())
                pin.assert_not_called()

    def test_library_record_is_checked_before_path_use(self) -> None:
        for value in (None, [], "library", {"path": None}, {"path": "other.so"}):
            with self.subTest(value=value), patch.object(sys, "argv", ["gate"]), \
                    patch.object(cli, "contract_problems", return_value=[]), \
                    patch.object(Path, "is_file", return_value=True), \
                    patch.object(Path, "read_text", return_value=json.dumps({"library": value})), \
                    patch.object(cli, "manifest_problems") as validate, \
                    contextlib.redirect_stderr(io.StringIO()) as errors:
                self.assertEqual(cli.main(), 1)
                self.assertIn("expected library path", errors.getvalue())
                validate.assert_not_called()


if __name__ == "__main__":
    unittest.main()
