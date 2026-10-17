"""JSON-shape, CLI-mode and isolated source-annotation proof gate controls.

No compiler, prover, kernel or daemon is run. Synthetic summary/digest fixtures
exercise admission behavior only and do not establish proof provenance.
"""
from __future__ import annotations

import ast
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
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


class ProveSourceGate(unittest.TestCase):
    """Execute prove.sh's Python gate with owned inputs, never its build/proof commands."""

    @classmethod
    def setUpClass(cls) -> None:
        gate = (ROOT / "prove.sh").read_text(encoding="utf-8")
        program = gate.partition("<<'PY'\n")[2].partition("\nPY\n")[0]
        cls.program = compile(program, str(ROOT / "prove.sh") + ":python", "exec")
        cls.options = ["owned-source-screen-fixture"]

    def summary(self, *, total=None, justified=0, unproved=0, omitted=None, extra_available=0) -> str:
        total = checks.MINIMUM_CHECKS if total is None else total
        names = [name for name in checks.REQUIRED_PROVED if name != omitted]
        rows = [
            "==========", "Summary of SPARK analysis", "==========",
            "SPARK Analysis results Total Flow Provers Justified Unproved",
            f"Assertions {total} 0 {total - justified - unproved} {justified} {unproved}",
            f"Total {total} 0 {total - justified - unproved} {justified} {unproved}",
            "==========", "Detailed analysis report", "==========",
            f"Analyzed {1 + len(checks.UNANALYZED_BOUNDARY)} units",
            f"in unit annotation-fixture, {len(names)} subprograms and packages "
            f"out of {len(names) + extra_available} analyzed",
        ]
        rows.extend(
            f"  {name} at owned-fixture.ads:{index + 1}:1 flow analyzed "
            f"(0 errors, 0 checks, 0 warnings and 0 pragma Assume statements) "
            f"and proved ({total if index == 0 else 0} checks)"
            for index, name in enumerate(names))
        rows.extend(f"in unit {unit}, 0 subprograms and packages out of 0 analyzed"
                    for unit in sorted(checks.UNANALYZED_BOUNDARY))
        return "\n".join(rows) + "\n"

    def run_gate(self, source: str = "", *, sources=None, summary=None, extra_files=None,
                 check_contracts=False):
        with tempfile.TemporaryDirectory(prefix="worldline-proof-source-gate-") as temporary:
            root = Path(temporary)
            paths = {}
            for relative, text in (sources if sources is not None else {
                    "core/annotation-fixture.ads": source}).items():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                if isinstance(text, bytes):
                    path.write_bytes(text)
                else:
                    path.write_text(text, encoding="utf-8")
                paths[relative] = path
            for relative, text in (extra_files or {}).items():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(text if isinstance(text, bytes) else text.encode("utf-8"))
            (root / "summary.fixture").write_text(
                self.summary() if summary is None else summary, encoding="utf-8")
            # A digest input only: never a compiled or loaded shared library.
            (root / "library.fixture").write_bytes(b"owned source-gate digest fixture\n")
            arguments = ["prove-source-gate", str(root), "summary.fixture", "library.fixture", *self.options]
            output = io.StringIO()
            failure = None
            contract_guard = cli.contract_problems if check_contracts else lambda _root: []
            with patch.object(sys, "argv", arguments), \
                    patch.object(sys, "path", list(sys.path)), \
                    patch.object(sys, "dont_write_bytecode", True), \
                    patch.dict(sys.modules, {"verify_proof_manifest": cli}), \
                    patch.object(cli, "contract_problems", side_effect=contract_guard), \
                    patch.object(cli, "source_paths", return_value=paths), \
                    patch("subprocess.run") as version, \
                    contextlib.redirect_stdout(output):
                version.return_value.stdout = "owned-fixture-version\n"
                try:
                    exec(self.program, {"__name__": "owned_proof_source_gate"})
                except SystemExit as exc:
                    failure = str(exc)
            manifest_path = root / "proof-manifest.json"
            if failure is not None:
                self.assertFalse(manifest_path.exists(), failure)
                return failure, output.getvalue(), None
            self.assertTrue(manifest_path.is_file(), output.getvalue())
            return None, output.getvalue(), json.loads(manifest_path.read_text(encoding="utf-8"))

    def test_supported_inline_forms_keep_full_proof_admission(self) -> None:
        sources = (
            "function F return Boolean is (True) "
            "with Annotate => (GNATprove, Inline_For_Proof);",
            "function F return Boolean with "
            "Annotate => (GNATprove, Inline_For_Proof) is (True);",
            "function F return Boolean is (True);\n"
            "pragma Annotate (GNATprove, Inline_For_Proof, Entity => F);",
            'pragma Annotate (GNATprove, Inline_For_Proof, Entity => "<=");',
            'pragma Annotate (GNATprove, Inline_For_Proof, Entity => Relations."<");',
            "pragma Annotate (GNATprove, Inline_For_Proof, Entity => %<=%);",
            "pragma Annotate (GNATprove, Inline_For_Proof, Entity => Relations.%and%);",
            "PrAgMa\nAnNoTaTe -- layout does not change the annotation\n"
            "(gNaTpRoVe,\n InLiNe_FoR_PrOoF,\n EnTiTy => Relations . F);",
        )
        for source in sources:
            with self.subTest(source=source):
                failure, output, manifest = self.run_gate(source)
                self.assertIsNone(failure, failure)
                self.assertIn("PROOF GATE PASSED", output)
                self.assertEqual(manifest["proof"]["minimumChecks"], checks.MINIMUM_CHECKS)
                self.assertEqual(manifest["coverage"]["requiredProved"], checks.REQUIRED_PROVED)

    def test_justifications_exclusions_models_and_unknown_tags_refuse(self) -> None:
        tags = (
            "False_Positive", "Intentional", "Skip_Proof", "Skip_Flow_And_Proof",
            "Iterable_For_Proof", "Logical_Equal", "Automatic_Instantiation",
            "Container_Aggregates", "At_End_Borrow", "Predefined_Equality",
            "Ownership", "Future_Proof_Annotation", "Inline_For_Proof_Extra",
        )
        for tag in tags:
            for source in (f"pragma Annotate (GNATprove, {tag});",
                           f"function F return Boolean with Annotate => (GNATprove, {tag});"):
                with self.subTest(source=source):
                    failure, _, _ = self.run_gate(source)
                    self.assertIsNotNone(failure)
                    self.assertIn("unsupported GNATprove annotation", failure)
                    self.assertIn("core/annotation-fixture.ads", failure)

    def test_malformed_or_nested_annotations_cannot_launder_an_inline_prefix(self) -> None:
        sources = (
            "pragma Annotate (GNATprove, Inline_For_Proof);",
            "pragma Annotate (GNATprove, Inline_For_Proof, Entity => F, Skip_Proof);",
            "pragma Annotate (GNATprove, Inline_For_Proof, Entity => (F));",
            "pragma Annotate (GNATprove, Inline_For_Proof, Entity => F)) ;",
            "pragma Annotate (GNATprove, Inline_For_Proof, Entity => F), Skip_Proof);",
            "pragma Annotate (GNATprove, Inline_For_Proof, Entity => F)",
            "pragma Annotate (GNATprove, Inline_For_Proof, Entity => F",
            "pragma Annotate GNATprove, Inline_For_Proof, Entity => F;",
            "Annotate => GNATprove, Inline_For_Proof;",
            "Annotate => (GNATprove, Inline_For_Proof, Entity => F);",
            "Annotate => (GNATprove, Inline_For_Proof, Skip_Proof);",
            "Annotate => (GNATprove, Inline_For_Proof)) ;",
            "Annotate => (GNATprove, Inline_For_Proof) & (GNATprove, Skip_Proof);",
            "Annotate => ((GNATprove, Inline_For_Proof), (GNATprove, Skip_Proof));",
            "pragma Annotate (CodePeer, (GNATprove, Skip_Proof));",
            'pragma Annotate (GNATprove, "Inline_For_Proof", Entity => F);',
        )
        for source in sources:
            with self.subTest(source=source):
                failure, _, _ = self.run_gate(source)
                self.assertIsNotNone(failure)
                self.assertIn("PROOF GATE FAILED", failure)

    def test_permitted_inline_does_not_mask_a_second_annotation_or_assumption(self) -> None:
        inline = "pragma Annotate (GNATprove, Inline_For_Proof, Entity => F);\n"
        for suffix in (
                "pragma Annotate (GNATprove, False_Positive, \"check\", \"reason\");",
                "Annotate => (GNATprove, Skip_Proof);",
                "PrAgMa -- comment between tokens\n aSsUmE (True);"):
            with self.subTest(suffix=suffix):
                failure, _, _ = self.run_gate(inline + suffix)
                self.assertIsNotNone(failure)

    def test_comments_and_literal_prose_are_not_proof_annotations(self) -> None:
        source = r'''
-- pragma Assume (True); Annotate => (GNATprove, Skip_Proof); SPARK_Mode => Off
Message : constant String :=
  "pragma Assume (True); Annotate => (GNATprove, Skip_Proof); SPARK_Mode => Off";
Quoted : constant String := "double ""quotes"" and -- still a string";
function Quote return Character is
begin
   return '"';
end Quote;
Qualified : Character := Character '('"');
pragma Annotate (GNATcheck, Exempt_On, "GNATprove Skip_Proof");
'''
        failure, _, _ = self.run_gate(source)
        self.assertIsNone(failure, failure)

    def test_multiline_qualified_characters_are_legal_across_comment_separators(self) -> None:
        for separator in ("\n", ' -- a comment containing "\n', '\n-- another "\n\n'):
            with self.subTest(separator=separator):
                source = "C : constant Character := Character" + separator + """  '('"');
function Quote return Character is
begin
   return -- a reserved word remains distinct from a name across a comment "
     '"';
end Quote;
pragma Annotate (GNATprove, Inline_For_Proof, Entity => F);
"""
                failure, _, _ = self.run_gate(source)
                self.assertIsNone(failure, failure)

    def test_multiline_qualified_characters_keep_live_annotations_visible(self) -> None:
        for separator in ("\n", ' -- a quote in a comment "\n', '\n-- another "\n\n'):
            prefix = "C : constant Character := Character" + separator + """  '('"'); """
            for annotation in (
                    "function F (L, R : Integer) return Boolean is (L = R) "
                    "with Annotate => (GNATprove, Logical_Equal);",
                    "pragma Annotate (GNATprove, Logical_Equal);"):
                with self.subTest(separator=separator, annotation=annotation):
                    failure, _, _ = self.run_gate(prefix + annotation + ' -- "\n')
                    self.assertIsNotNone(failure)
                    self.assertIn("unsupported GNATprove annotation", failure)
                    self.assertIn("Logical_Equal", failure)

    def test_percent_delimited_literal_payloads_are_not_annotations(self) -> None:
        for literal in (
                "%%", "%%%%", "%--%", "%--%%--%", "%escaped %%%% -- percent%",
                "%pragma Assume (True); Annotate => (GNATprove, Logical_Equal); SPARK_Mode => Off%"):
            with self.subTest(literal=literal):
                source = f"Noise : constant String := {literal}; -- a quote in a comment \"\n"
                source += """Percent : constant Character := '%';
pragma Annotate (GNATprove, Inline_For_Proof, Entity => F);
"""
                failure, _, _ = self.run_gate(source)
                self.assertIsNone(failure, failure)

    def test_percent_delimited_strings_keep_live_annotations_visible(self) -> None:
        for literal in ("%--%", "%--%%--%", "%escaped %%%% -- percent%"):
            for annotation in (
                    "function F (L, R : Integer) return Boolean is (L = R) "
                    "with Annotate => (GNATprove, Logical_Equal);",
                    "pragma Annotate (GNATprove, Logical_Equal);"):
                with self.subTest(literal=literal, annotation=annotation):
                    source = f"Noise : constant String := {literal}; " + annotation + ' -- "\n'
                    failure, _, _ = self.run_gate(source)
                    self.assertIsNotNone(failure)
                    self.assertIn("unsupported GNATprove annotation", failure)
                    self.assertIn("Logical_Equal", failure)

    def test_quotes_characters_and_qualifications_do_not_hide_following_syntax(self) -> None:
        prefixes = (
            'Message := "--"; ',
            'Message := "double ""quotes"" --"; ',
            """Quote := '"'; """,
            """return '"'; """,
            """Qualified := Character '('"'); """,
            """Dash := Character '('-'); """,
            """Qualified := Character\n  '('"'); """,
            """Qualified := Character -- a quote in a comment "\n  '('"'); """,
            "Message := %--%; ",
            "Message := %--%%--%; ",
            """Percent := '%'; """,
        )
        for prefix in prefixes:
            for forbidden in ("pragma Assume (True);",
                              "pragma Annotate (GNATprove, Skip_Flow_And_Proof);",
                              "pragma SPARK_Mode (Off);"):
                with self.subTest(prefix=prefix, forbidden=forbidden):
                    failure, _, _ = self.run_gate(prefix + forbidden)
                    self.assertIsNotNone(failure)

    def test_unicode_qualification_and_entities_preserve_admission_boundaries(self) -> None:
        for name in ("Café", "Cafe\u0301", "Π"):
            prefix = (
                "\ufeffsubtype " + name + " is Character;\n"
                "C : constant Character := " + name + "\n"
                """  '('"'); Noise : constant String := "--"; """)
            for annotation, accepted in (
                    (f"pragma Annotate (GNATprove, Inline_For_Proof, Entity => {name});", True),
                    ("function F (L, R : Integer) return Boolean is (L = R) "
                     "with Annotate => (GNATprove, Logical_Equal);", False)):
                with self.subTest(name=name, accepted=accepted):
                    failure, _, _ = self.run_gate(prefix + annotation)
                    if accepted:
                        self.assertIsNone(failure, failure)
                    else:
                        self.assertIn("unsupported GNATprove annotation", failure)
            # Default GNAT input is Latin-1; a UTF-8 BOM selects the wider set.
        latin1 = ("subtype Café is Character;\n"
                  """C : constant Character := Café '('"'); """
                  "pragma Assume (True);").encode("latin-1")
        failure, _, _ = self.run_gate(sources={"core/latin1.ads": latin1})
        self.assertIsNotNone(failure)

    def test_unicode_comment_endings_and_spaces_cannot_hide_forbidden_tokens(self) -> None:
        for ending in ("\x85", "\u2028", "\u2029", "\r", "\n", "\v", "\f"):
            for forbidden in (
                    "pragma\u00a0Assume (True);",
                    "pragma\u2003Annotate (GNATprove, Logical_Equal, Entity => F);",
                    "pragma\u00a0SPARK_Mode\u00a0(Off);"):
                with self.subTest(ending=repr(ending), forbidden=forbidden):
                    failure, _, _ = self.run_gate("\ufeff-- ordinary comment" + ending + forbidden)
                    self.assertIsNotNone(failure)
            failure, _, _ = self.run_gate(
                "\ufeff-- ordinary comment" + ending +
                "pragma\u00a0Annotate (GNATprove,\u2003Inline_For_Proof, Entity => Café);")
            self.assertIsNone(failure, failure)

    def test_identifier_substrings_are_not_keywords_or_annotation_namespaces(self) -> None:
        source = (
            "\ufefffunction x\u0301pragma return Boolean is (True);\n"
            "pragma Annotate (GNATprove\u0301Tool, Tag, Entity => x\u0301pragma);\n"
            "pragma Annotate (GNATprove, Inline_For_Proof, Entity => x\u0301pragma);")
        failure, _, _ = self.run_gate(source)
        self.assertIsNone(failure, failure)

    def test_malformed_bom_selected_utf8_refuses_before_manifest(self) -> None:
        failure, _, _ = self.run_gate(sources={"core/broken.ads": b"\xef\xbb\xbf\xff"})
        self.assertIn("PROOF GATE FAILED", failure)

    def test_only_exact_declared_boundary_spec_and_body_may_leave_spark(self) -> None:
        sources = {
            f"core/{unit}{suffix}": "pragma SPARK_Mode (Off);"
            for unit in checks.UNANALYZED_BOUNDARY for suffix in (".ads", ".adb")
        }
        sources["core/annotation-fixture.ads"] = "pragma SPARK_Mode (On);"
        failure, _, _ = self.run_gate(sources=sources)
        self.assertIsNone(failure, failure)

    def test_c_api_substrings_and_same_named_nested_paths_are_not_boundaries(self) -> None:
        for relative in (
                "core/ordinary_c_api.ads", "core/worldline-recovery_authorization_c_api.adb",
                "core/worldline-c_api_shadow.ads", "core/nested/worldline-c_api.ads",
                "attest/worldline-c_api.adb", "imported/worldline-c_api.ads"):
            with self.subTest(relative=relative):
                failure, _, _ = self.run_gate(sources={relative: "SPARK_Mode =>\n Off"})
                self.assertIsNotNone(failure)
                self.assertIn("outside the declared boundary", failure)
                self.assertIn(relative, failure)

    def test_boundary_cannot_justify_skip_assume_or_admit_inline_on_an_unproved_body(self) -> None:
        for unit in checks.UNANALYZED_BOUNDARY:
            for directive in (
                    "pragma Assume (True);",
                    "pragma Annotate (GNATprove, False_Positive, \"check\", \"reason\");",
                    "Annotate => (GNATprove, Skip_Proof);",
                    "pragma Annotate (GNATprove, Inline_For_Proof, Entity => F);"):
                with self.subTest(unit=unit, directive=directive):
                    failure, _, _ = self.run_gate(sources={f"core/{unit}.adb": directive})
                    self.assertIsNotNone(failure)

    def test_inline_cannot_lower_floors_drop_required_bodies_or_accept_failed_checks(self) -> None:
        inline = "function F return Boolean is (True) with Annotate => (GNATprove, Inline_For_Proof);"
        cases = {
            "floor": self.summary(total=checks.MINIMUM_CHECKS - 1),
            "required": self.summary(omitted=checks.REQUIRED_PROVED[-1]),
            "partial body": self.summary(extra_available=1),
            "justified": self.summary(justified=1),
            "unproved": self.summary(unproved=1),
        }
        for label, summary in cases.items():
            with self.subTest(label=label):
                failure, _, _ = self.run_gate(inline, summary=summary)
                self.assertIsNotNone(failure)
                self.assertIn("PROOF GATE FAILED", failure)

    def test_aliases_allow_inline_and_harmless_pragmas_including_alias_chains(self) -> None:
        declarations = (
            "pragma Rename_Pragma (Mark, Annotate);",
            "pragma Rename_Pragma (New_Name => Mark, Renamed => Annotate);",
            "pragma Rename_Pragma (Mark, Renamed => Annotate);",
            "pragma Rename_Pragma (Renamed => Annotate, New_Name => Mark);",
            "pragma Rename_Pragma (First, Annotate);\n"
            "pragma Rename_Pragma (Mark, First);",
            "pragma Rename_Pragma (Rename, Rename_Pragma);\n"
            "pragma Rename (Again, Rename);\n"
            "pragma Again (Mark, Annotate);",
        )
        for declaration in declarations:
            with self.subTest(declaration=declaration):
                source = declaration + "\nfunction F return Boolean is (True);\n"
                source += "pragma Mark (GNATprove, Inline_For_Proof, Entity => F);"
                failure, output, manifest = self.run_gate(source)
                self.assertIsNone(failure, failure)
                self.assertIn("PROOF GATE PASSED", output)
                self.assertEqual(manifest["proof"]["minimumChecks"], checks.MINIMUM_CHECKS)
        failure, _, _ = self.run_gate(
            "pragma Rename_Pragma (Inline_Only, Inline_Always);\n"
            "pragma Rename_Pragma (Inline_Again, Inline_Only);\n"
            "function F return Boolean is (True);\npragma Inline_Again (F);")
        self.assertIsNone(failure, failure)

    def test_aliases_cannot_hide_annotations_assumptions_or_spark_off(self) -> None:
        for target, directive, diagnostic in (
                ("Annotate", "(GNATprove, Logical_Equal, Entity => F)",
                 "unsupported GNATprove annotation"),
                ("Assume", "(True)", "PROOF GATE FAILED"),
                ("SPARK_Mode", "(Off)", "outside the declared boundary")):
            for chain in (False, True):
                declaration = f"pragma Rename_Pragma (First, {target});\n"
                if chain:
                    declaration += ("pragma Rename_Pragma (Rename, Rename_Pragma);\n"
                                    "pragma Rename (Mark, First);\n")
                else:
                    declaration += "pragma Rename_Pragma (Mark, First);\n"
                with self.subTest(target=target, chain=chain):
                    failure, _, _ = self.run_gate(declaration + f"pragma Mark {directive};")
                    self.assertIsNotNone(failure)
                    self.assertIn(diagnostic, failure)

    def test_aliases_preserve_the_exact_c_boundary_and_never_admit_boundary_inline(self) -> None:
        declaration = ("pragma Rename_Pragma (First, SPARK_Mode);\n"
                       "pragma Rename_Pragma (Mode, First);\n")
        boundary = {
            f"core/{unit}{suffix}": declaration + "pragma Mode (Off);"
            for unit in checks.UNANALYZED_BOUNDARY for suffix in (".ads", ".adb")
        }
        failure, _, _ = self.run_gate(sources=boundary)
        self.assertIsNone(failure, failure)
        for relative in ("core/ordinary_c_api.ads", "core/worldline-c_api_shadow.ads",
                         "core/nested/worldline-c_api.ads", "imported/worldline-c_api.adb"):
            with self.subTest(relative=relative):
                failure, _, _ = self.run_gate(sources={relative: declaration + "pragma Mode (Off);"})
                self.assertIn("outside the declared boundary", failure)
        for unit in checks.UNANALYZED_BOUNDARY:
            for target, arguments in (
                    ("Annotate", "(GNATprove, Inline_For_Proof, Entity => F)"),
                    ("Annotate", "(GNATprove, Skip_Proof)"), ("Assume", "(True)")):
                with self.subTest(unit=unit, target=target, arguments=arguments):
                    source = f"pragma Rename_Pragma (Mark, {target});\npragma Mark {arguments};"
                    failure, _, _ = self.run_gate(sources={f"core/{unit}.adb": source})
                    self.assertIsNotNone(failure)

    def test_alias_declarations_are_sequential_and_never_rewrite_prose_or_entities(self) -> None:
        source = (
            "function Mark return Boolean is (True);\n"
            "pragma Rename_Pragma (Mark, Annotate);\n"
            'Noise : String := "pragma Mark (GNATprove, Skip_Proof);  -- unchanged";\n'
            "-- pragma Mark (GNATprove, Logical_Equal);\n"
            "pragma Mark (GNATprove, Inline_For_Proof, Entity => Mark);")
        tokens = [token for token in checks.ada_tokens(source, canonical_pragmas=True)
                  if token[0] != "layout"]
        names = [tokens[index + 1][1] for index, token in enumerate(tokens)
                 if token == ("identifier", "pragma")]
        self.assertEqual(names, ["RENAME_PRAGMA", "ANNOTATE"])
        self.assertIn(("identifier", "Mark"), tokens)
        self.assertIn(("string", '"pragma Mark (GNATprove, Skip_Proof);  -- unchanged"'), tokens)
        failure, _, _ = self.run_gate(source)
        self.assertIsNone(failure, failure)

    def test_malformed_aliases_and_ambiguous_redefinitions_refuse_before_manifest(self) -> None:
        sources = (
            "pragma Rename_Pragma (Mark);",
            "pragma Rename_Pragma (Mark, Annotate, Assume);",
            "pragma Rename_Pragma (New_Name => Mark, New_Name => Annotate);",
            "pragma Rename_Pragma (Renamed => Annotate, Mark);",
            'pragma Rename_Pragma ("Mark", Annotate);',
            "pragma Rename_Pragma (Mark, Annotate",
            "pragma Rename_Pragma (Mark, Annotate)",
            "pragma Rename_Pragma (Mark, (Annotate));",
            "pragma Rename_Pragma (Annotate, Assert);",
            "pragma Rename_Pragma (Wide_Character_Encoding, Assert);",
            "pragma Rename_Pragma (Mark, Mark);",
            "pragma Rename_Pragma (Mark, Annotate); pragma Rename_Pragma (Mark, Assume);",
            "pragma Rename_Pragma (Mark, Future); pragma Rename_Pragma (Future, Assume);",
            "pragma Mark (True); pragma Rename_Pragma (Mark, Assume);",
        )
        for source in sources:
            with self.subTest(source=source):
                failure, _, _ = self.run_gate(source)
                self.assertIn("PROOF GATE FAILED", failure)

    def test_source_utf8_without_bom_preserves_qualification_and_live_directives(self) -> None:
        for control in (
                "pragma Wide_Character_Encoding (UTF8);",
                "pragma Wide_Character_Encoding ('8');",
                "pragma Rename_Pragma (Encoding, Wide_Character_Encoding);\n"
                "pragma Rename_Pragma (Again, Encoding);\npragma Again ('8');"):
            for name in ("Café", "Cafe\u0301", "Π"):
                prefix = (
                    control + "\npackage Lexical_Fixture with SPARK_Mode is\n"
                    f"subtype {name}_Char is Character;\nC : constant Character := {name}_Char\n"
                    """  '('"'); Noise : constant String := "--"; """)
                for suffix, accepted in (
                        (f"function {name} (L, R : Integer) return Boolean is (L = R);\n"
                         f"pragma Annotate (GNATprove, Inline_For_Proof, Entity => {name});", True),
                        ("function F (L, R : Integer) return Boolean is (L = R) "
                         "with Annotate => (GNATprove, Logical_Equal);", False),
                        ("pragma Assume (True);", False), ("pragma SPARK_Mode (Off);", False)):
                    with self.subTest(control=control, name=name, accepted=accepted, suffix=suffix):
                        raw = (prefix + suffix + "\nend Lexical_Fixture;").encode("utf-8")
                        failure, _, _ = self.run_gate(sources={"core/utf8.ads": raw})
                        if accepted:
                            self.assertIsNone(failure, failure)
                        else:
                            self.assertIsNotNone(failure)
                            self.assertIn("PROOF GATE FAILED", failure)

    def test_source_encoding_changes_are_local_and_preserve_each_decoded_segment(self) -> None:
        before = "package Lexical_Fixture with SPARK_Mode is\nsubtype Café_Char is Character;\n"
        middle = ("pragma Wide_Character_Encoding (UTF8);\nsubtype Π_Char is Character;\n"
                  "pragma Wide_Character_Encoding ('b');\n")
        after = ("subtype Après_Char is Character;\nC : constant Character := Après_Char\n"
                 """  '('"'); Noise : constant String := "--"; """)
        for suffix, accepted in (
                ("function Après return Boolean is (True);\n"
                 "pragma Annotate (GNATprove, Inline_For_Proof, Entity => Après);", True),
                ("pragma Annotate (GNATprove, Logical_Equal, Entity => F);", False)):
            with self.subTest(accepted=accepted):
                tail = after + suffix + "\nend Lexical_Fixture;"
                raw = before.encode("latin-1") + middle.encode("utf-8") + tail.encode("latin-1")
                self.assertEqual(checks.ada_source_text(raw), before + middle + tail)
                self.assertEqual(checks.normalized_ada(raw), checks.normalized_ada(before + middle + tail))
                failure, _, _ = self.run_gate(sources={"core/mixed.ads": raw})
                if accepted:
                    self.assertIsNone(failure, failure)
                else:
                    self.assertIn("unsupported GNATprove annotation", failure)
        # One file's encoding pragma does not configure another source.
        failure, _, _ = self.run_gate(sources={
            "core/utf8.ads": b"pragma Wide_Character_Encoding ('8');\npackage A is end A;",
            "core/latin1.ads": (
                "subtype Café is Character;\nC : Character := Café\n"
                """  '('"'); pragma Assume (True);""").encode("latin-1"),
        })
        self.assertIsNotNone(failure)

    def test_source_language_modes_and_aliases_keep_parallel_and_older_names_visible(self) -> None:
        for control, name in (
                ("pragma Ada_2012;", "Parallel"), ("pragma Ada_12;", "Parallel"),
                ("pragma Ada_2005;", "Some"), ("pragma Ada_05;", "Some"),
                ("pragma Ada_95;", "Interface"), ("pragma Ada_83;", "Tagged"),
                ("pragma Rename_Pragma (Version, Ada_2012);\npragma Version;", "Parallel")):
            prefix = (control + "\npackage Lexical_Fixture is\npragma SPARK_Mode (On);\n"
                      f"subtype {name} is Character;\nC : constant Character := {name}\n"
                      """  '('"'); Noise : constant String := "--"; """)
            for suffix, accepted in (
                    ("function F return Boolean;\n"
                     "pragma Annotate (GNATprove, Inline_For_Proof, Entity => F);", True),
                    ("pragma Annotate (GNATprove, Logical_Equal, Entity => F);", False),
                    ("pragma Assume (True);", False), ("pragma SPARK_Mode (Off);", False)):
                with self.subTest(control=control, name=name, accepted=accepted, suffix=suffix):
                    failure, _, _ = self.run_gate(prefix + suffix + "\nend Lexical_Fixture;")
                    if accepted:
                        self.assertIsNone(failure, failure)
                    else:
                        self.assertIsNotNone(failure)
            if name == "Parallel":
                failure, _, _ = self.run_gate(
                    prefix + "function F (L, R : Integer) return Boolean is (L = R) "
                    "with Annotate => (GNATprove, Logical_Equal);\nend Lexical_Fixture;")
                self.assertIn("unsupported GNATprove annotation", failure)

    def test_unsupported_source_profiles_refuse_visibly_without_decoding_fallback(self) -> None:
        for method in ("HEX", "UPPER", "SHIFT_JIS", "EUC", "'h'", "'u'", "'s'", "'e'",
                       "Unknown", '"UTF8"', "'B'"):
            with self.subTest(method=method):
                failure, _, _ = self.run_gate(f"pragma Wide_Character_Encoding ({method});")
                self.assertIn("unsupported Wide_Character_Encoding", failure)
        for control in ("Ignore_Pragma (Wide_Character_Encoding)", "Extensions_Allowed (On)",
                        "User_Aspect_Definition (Hidden, Annotate)"):
            for aliased in (False, True):
                name, arguments = control.split(" ", 1)
                source = (f"pragma Rename_Pragma (Control, {name});\npragma Control {arguments};"
                          if aliased else f"pragma {control};")
                with self.subTest(control=control, aliased=aliased):
                    failure, _, _ = self.run_gate(source)
                    self.assertIn("unsupported source-effective control", failure)
        for raw in (
                b"pragma Wide_Character_Encoding ('8');\npackage P is \xff end P;",
                "pragma Wide_Character_Encoding ('8');\nCafé".encode("utf-8"),
                b'subtype Caf["00E9"] is Character;',
                b'X : String := "["00E9"]";', b"X : Character := '\x1b00E9';"):
            with self.subTest(raw=raw):
                failure, _, _ = self.run_gate(sources={"core/unsupported.ads": raw})
                self.assertIn("PROOF GATE FAILED", failure)
        # Unsupported-looking prose is still inert; do not replace it globally.
        failure, _, _ = self.run_gate(
            '-- pragma Wide_Character_Encoding (UPPER); ["00E9"]\n'
            'X : String := "pragma Wide_Character_Encoding (UPPER);  -- unchanged";')
        self.assertIsNone(failure, failure)

    def test_extra_configuration_files_and_project_overrides_refuse_at_the_actual_gate(self) -> None:
        for relative in ("gnat.adc", "core/local.adc", "obj/core/gnat.adc"):
            with self.subTest(relative=relative):
                failure, _, _ = self.run_gate(
                    extra_files={relative: "pragma Wide_Character_Encoding (UTF8);"})
                self.assertIn("unsupported additional configuration pragma file", failure)
        for setting in (
                'for Global_Configuration_Pragmas use "external.config";',
                'for Local_Configuration_Pragmas use "external.config";',
                'for Default_Switches ("Ada") use ("-gnatec=external.config");',
                'for Default_Switches ("Ada") use ("-gnatepexternal.prep");',
                'for Default_Switches ("Ada") use ("-gnatW8");',
                'for Default_Switches ("Ada") use ("-gnatqW8");',
                'for Default_Switches ("Ada") use ("-gnatqec=external.config");',
                'for Default_Switches ("Ada") use ("-gnati2");',
                'for Default_Switches ("Ada") use ("-gnat12");',
                'for Default_Switches ("Ada") use ("-gnatX");'):
            with self.subTest(setting=setting):
                failure, _, _ = self.run_gate(sources={
                    "core/fixture.ads": "package Fixture is end Fixture;",
                    "core/fixture.gpr": "project Fixture is " + setting + " end Fixture;"})
                self.assertIn("unsupported project", failure)


    def test_changed_real_contract_refuses_before_any_manifest_is_published(self) -> None:
        sources = {path.relative_to(ROOT).as_posix(): path.read_bytes()
                   for path in checks.source_paths(ROOT).values()}
        extra_files = {relative: (ROOT / relative).read_bytes()
                       for relative in checks.proof_source_files(ROOT)
                       if relative not in sources}
        failure, _, manifest = self.run_gate(
            sources=sources, extra_files=extra_files, check_contracts=True)
        self.assertIsNone(failure)
        self.assertIsNotNone(manifest)
        path = "core/worldline-producer_render.adb"
        original = sources[path]
        changed = original.replace(b'"0123456789abcdef"', b'"0123456789abcdeg"', 1)
        self.assertNotEqual(changed, original)
        sources[path] = changed
        failure, _, manifest = self.run_gate(
            sources=sources, extra_files=extra_files, check_contracts=True)
        self.assertIsNotNone(failure)
        self.assertIsNone(manifest)


    def test_older_mode_aliases_preserve_permitted_and_forbidden_targets(self) -> None:
        for language, name in (("Ada_2012", "Parallel"), ("Ada_2005", "Some")):
            for target, invocation, refused in (
                    ("Inline", "F", False),
                    ("Annotate", "GNATprove, Logical_Equal, Entity => F", True),
                    ("Assume", "True", True),
                    ("SPARK_Mode", "Off", True)):
                with self.subTest(language=language, alias=name, target=target):
                    source = (
                        f"pragma {language};\n"
                        f"pragma Rename_Pragma (New_Name => {name}, Renamed => {target});\n"
                        "package Lexical_Fixture is\npragma SPARK_Mode (On);\n"
                        "function F return Boolean;\n"
                        f"pragma {name} ({invocation});\nend Lexical_Fixture;")
                    failure, _, manifest = self.run_gate(source)
                    if refused:
                        self.assertIsNotNone(failure)
                        self.assertIsNone(manifest)
                    else:
                        self.assertIsNone(failure)
                        self.assertIsNotNone(manifest)

    def test_simple_case_identifiers_keep_qualified_characters_and_live_directives_visible(self) -> None:
        for name, encoding, prefix in (
                ("Acceß", "latin-1", b""),
                ("Acceß", "utf-8", b"\xef\xbb\xbf"),
                ("Begın", "utf-8", b"\xef\xbb\xbf")):
            head = ("package Lexical_Fixture with SPARK_Mode is\n"
                    f"subtype {name} is Character;\nC : Character := {name}\n"
                    """  '('"'); Noise : String := "--"; """)
            tails = (
                ("function F return Boolean is (True) with "
                 "Annotate => (GNATprove, Inline_For_Proof);", False),
                ("function F return Boolean is (True) with "
                 "Annotate => (GNATprove, Logical_Equal);", True),
                ("pragma Assume (True);", True),
                ("pragma SPARK_Mode (Off);", True),
            )
            for tail, refused in tails:
                with self.subTest(name=name, encoding=encoding, tail=tail):
                    raw = prefix + (head + tail + "\nend Lexical_Fixture;").encode(encoding)
                    failure, _, manifest = self.run_gate(sources={"core/lexical_fixture.ads": raw})
                    if refused:
                        self.assertIsNotNone(failure)
                        self.assertIn("PROOF GATE FAILED", failure)
                    else:
                        self.assertIsNone(failure)
                        self.assertIsNotNone(manifest)

    def test_simple_case_pragma_alias_does_not_expand_to_a_monitored_name(self) -> None:
        raw = ("pragma Rename_Pragma (New_Name => Aßume, Renamed => Inline);\n"
               "package Lexical_Fixture with SPARK_Mode is\n"
               "function F return Boolean is (True);\n"
               "pragma Aßume (F);\nend Lexical_Fixture;").encode("latin-1")
        failure, _, manifest = self.run_gate(sources={"core/lexical_fixture.ads": raw})
        self.assertIsNone(failure)
        self.assertIsNotNone(manifest)


class SourceEffectivePins(unittest.TestCase):
    """Bind code after each source-effective lexical witness, without compiling."""

    def test_byte_pins_and_ast_loaded_definitions_share_source_effective_lexing(self) -> None:
        spec = importlib.util.spec_from_file_location("source_effective_pin_loader",
                                                      ROOT / "refresh_contract_pins.py")
        loader = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(loader)
        path = ROOT / "runtime/worldline/proof_manifest.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        tree.body += ast.parse("raise AssertionError('target module must not execute')").body
        isolated_pin, isolated_profile = loader._pin_normalizer(tree, path)
        prefixes = (
            "pragma Wide_Character_Encoding (UTF8);\npackage P is\n"
            """subtype Café is Character;\nC : Character := Café\n  '('"'); Noise : String := "--"; """,
            "pragma Rename_Pragma (Encoding, Wide_Character_Encoding);\n"
            "pragma Encoding ('8');\npackage P is\n"
            """subtype Π is Character;\nC : Character := Π\n  '('"'); Noise : String := "--"; """,
            "pragma Ada_2012;\npackage P is\n"
            """subtype Parallel is Character;\nC : Character := Parallel\n  '('"'); Noise : String := "--"; """,
            "pragma Ada_2012;\npackage P is\n"
            "function Marked return Boolean;\npragma Ada_2022 (Marked);\n"
            """subtype Parallel is Character;\nC : Character := Parallel\n  '('"'); Noise : String := "--"; """,
            "pragma Rename_Pragma (Version, Ada_12);\npragma Version;\npackage P is\n"
            """subtype Parallel is Character;\nC : Character := Parallel\n  '('"'); Noise : String := %--%%--%; """,
            "pragma Wide_Character_Encoding (UTF8);\npackage P is\n"
            """subtype Acceß is Character;\nC : Character := Acceß\n  '('"'); Noise : String := "--"; """,
            "\ufeffpackage P is\n"
            """subtype Begın is Character;\nC : Character := Begın\n  '('"'); Noise : String := "--"; """,
        )
        with tempfile.TemporaryDirectory(prefix="worldline-source-effective-pins-") as temporary:
            root = Path(temporary)
            key = "fixture.ads"
            target = root / key
            code = "function F return Boolean is (True);\nend P;"
            for prefix in prefixes:
                with self.subTest(prefix=prefix):
                    raw = (prefix + code + ' -- original comment "\n').encode("utf-8")
                    target.write_bytes(raw)
                    pin = checks.contract_pin(root, key)
                    self.assertEqual(isolated_pin(root, key), pin)
                    self.assertEqual(checks.normalized_ada(raw),
                                     checks.normalized_ada(checks.ada_source_text(raw)))
                    target.write_bytes(raw.replace(b"(True)", b"(False)"))
                    self.assertNotEqual(checks.contract_pin(root, key), pin)
                    self.assertEqual(isolated_pin(root, key), checks.contract_pin(root, key))
                    target.write_bytes(raw.replace(b'original comment "', b'different comment % "'))
                    self.assertEqual(checks.contract_pin(root, key), pin)
            project = root / "fixture.gpr"
            project.write_text('project P is for Local_Configuration_Pragmas use "p.cfg"; end P;',
                               encoding="utf-8")
            self.assertEqual(isolated_profile(root, [project]),
                             checks.source_profile_problems(root, [project]))
            self.assertTrue(isolated_profile(root, [project]))

    def test_mixed_encoding_pins_bind_following_code_and_literal_whitespace(self) -> None:
        prefix = (b"pragma Wide_Character_Encoding ('8');\npackage P is\n"
                  + "subtype Π is Character;\n".encode("utf-8")
                  + b"pragma Wide_Character_Encoding (BRACKETS);\n"
                  + """subtype Café is Character;\nC : Character := Café\n  '('"'); """.encode("latin-1"))
        with tempfile.TemporaryDirectory(prefix="worldline-mixed-source-pins-") as temporary:
            root = Path(temporary)
            target = root / "fixture.ads"
            for delimiter in (b'"', b"%"):
                with self.subTest(delimiter=delimiter):
                    raw = (prefix + b"Noise : String := " + delimiter + b"a -- b" + delimiter
                           + b"; function F return Boolean is (True); end P;")
                    target.write_bytes(raw)
                    pin = checks.contract_pin(root, "fixture.ads")
                    for changed in (raw.replace(b"(True)", b"(False)"),
                                    raw.replace(b"a -- b", b"a  -- b")):
                        target.write_bytes(changed)
                        self.assertNotEqual(checks.contract_pin(root, "fixture.ads"), pin)
                    target.write_bytes(raw + b' -- harmless comment "\n')
                    self.assertEqual(checks.contract_pin(root, "fixture.ads"), pin)



if __name__ == "__main__":
    unittest.main()
