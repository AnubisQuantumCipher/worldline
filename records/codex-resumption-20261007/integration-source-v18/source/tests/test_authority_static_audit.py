"""Static audit (1.8.0, 1.9.0): the promotion decision has no independent Python definition,
and (1.9.0) no module that feeds it states an absent identity as a value.

Every comparison with a verdict ("PASS" or "COMPLETED") in the modules that decide or feed
promotion, and every read of a saved verdict field, is listed below per function with a count
and the reason it is not an authorization. A new one fails this test until it is removed or
listed. Verdicts are recognised as string constants, as containers of them, as names bound to
them, and as `match` patterns.

This is a syntactic audit and a tripwire, not a proof: it cannot see a verdict computed some
other way. The property that promotion recomputes every check from its raw record is enforced
behaviourally (tests/test_evaluation_authority.py: a forged saved evaluation is refused).
"""
from __future__ import annotations

import ast
from collections import Counter
from pathlib import Path
import unittest

RUNTIME = Path(__file__).resolve().parents[1] / "runtime" / "worldline"
AUDITED = ("finalize.py", "revalidate.py", "transaction.py", "simulation.py", "validation.py", "returning.py")
VERDICTS = {"PASS", "COMPLETED"}
SAVED_FIELDS = {"admissibleForPromotion", "executionStatus", "evaluationOutcome", "bundleIntegrity", "reportIntegrity"}

# (module, enclosing function) -> (how many, why it is not an authorization).
ALLOWED_COMPARISONS = {
    ("finalize.py", "_private_report_verified"): (1,
        "report integrity is an input fact to Evaluation.Admissible; requiring the kernel's own"
        " COMPLETED classification here can only make a report less trusted"),
    ("finalize.py", "refusal_reason"): (2, "diagnostic text for a check the kernel already refused"),
    ("finalize.py", "evaluation_record"): (1,
        "the Python mapping of raw fields to the kernel's finite categories (the declared"
        " unproved boundary)"),
    ("validation.py", "effective_evidence"): (1,
        "selects which evaluation speaks for a world (Phase 1 item 5, one effective evaluation);"
        " promotion still recomputes every check of the selected evaluation in the kernel"),
    ("simulation.py", "run"): (1,
        "the health report of a system future, which prepare refuses as a collapse candidate and"
        " as a return subject"),
}
ALLOWED_SAVED_READS = {
    ("finalize.py", "roster_decision"): (1, "reads the evaluation it has just recomputed, never a saved one"),
    ("finalize.py", "refusal_reason"): (7, "diagnostic text for a check the kernel already refused"),
}
KERNEL_DECISION_SITES = {
    "finalize.py": "finalize",
    "revalidate.py": "_evaluate_tree",
    "transaction.py": "_execution_identity",
}


def _verdict_names(tree: ast.AST) -> set[str]:
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            value = node.value
            if isinstance(value, ast.Constant) and value.value in VERDICTS:
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                names |= {target.id for target in targets if isinstance(target, ast.Name)}
    return names


def _is_verdict(node: ast.AST, names: set[str]) -> bool:
    if isinstance(node, ast.Constant):
        return node.value in VERDICTS
    if isinstance(node, ast.Name):
        return node.id in names
    if isinstance(node, (ast.Tuple, ast.Set, ast.List)):
        return any(_is_verdict(element, names) for element in node.elts)
    return False


def _saved_read(node: ast.AST) -> bool:
    if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
        return node.slice.value in SAVED_FIELDS
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "get"
            and node.args and isinstance(node.args[0], ast.Constant)):
        return node.args[0].value in SAVED_FIELDS
    return False


def scan(module: str, root: Path = RUNTIME) -> tuple[Counter, Counter]:
    tree = ast.parse((root / module).read_text(encoding="utf-8"))
    names = _verdict_names(tree)
    comparisons: Counter = Counter()
    reads: Counter = Counter()

    def visit(node: ast.AST, function: str) -> None:
        for child in ast.iter_child_nodes(node):
            name = child.name if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) else function
            if isinstance(child, ast.Compare) and any(_is_verdict(operand, names) for operand in [child.left, *child.comparators]):
                comparisons[(module, name)] += 1
            if isinstance(child, ast.match_case) and any(
                    isinstance(pattern, ast.MatchValue) and _is_verdict(pattern.value, names)
                    for pattern in ast.walk(child.pattern)):
                comparisons[(module, name)] += 1
            if _saved_read(child) and isinstance(getattr(child, "ctx", ast.Load()), ast.Load):
                reads[(module, name)] += 1
            visit(child, name)

    visit(tree, "<module>")
    return comparisons, reads


def calls(module: str, function: str) -> set[str]:
    tree = ast.parse((RUNTIME / module).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function:
            return {getattr(call.func, "id", getattr(call.func, "attr", ""))
                    for call in ast.walk(node) if isinstance(call, ast.Call)}
    return set()


class NoPythonAdmissibility(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.comparisons, cls.reads = Counter(), Counter()
        for module in AUDITED:
            comparisons, reads = scan(module)
            cls.comparisons.update(comparisons)
            cls.reads.update(reads)

    def test_every_verdict_comparison_is_listed_with_its_count_and_reason(self) -> None:
        self.assertEqual(dict(self.comparisons), {key: count for key, (count, _why) in ALLOWED_COMPARISONS.items()})

    def test_every_saved_verdict_read_is_listed_with_its_count_and_reason(self) -> None:
        self.assertEqual(dict(self.reads), {key: count for key, (count, _why) in ALLOWED_SAVED_READS.items()})

    def test_the_audit_sees_the_spellings_it_claims_to(self) -> None:
        import tempfile
        source = (
            "_OK = 'PASS'\n"
            "def a(item):\n    return item.get('status') == _OK\n"
            "def b(item):\n    match item:\n        case 'COMPLETED':\n            return True\n"
            "def c(item):\n    return item['evaluation']['admissibleForPromotion']\n"
            "def d(item):\n    return item.get('executionStatus') in ('COMPLETED',)\n"
        )
        with tempfile.TemporaryDirectory() as temporary:
            probe = Path(temporary) / "probe.py"
            probe.write_text(source, encoding="utf-8")
            comparisons, reads = scan(probe.name, Path(temporary))
        self.assertEqual(comparisons[(probe.name, "a")], 1)
        self.assertEqual(comparisons[(probe.name, "b")], 1)
        self.assertEqual(comparisons[(probe.name, "d")], 1)
        self.assertEqual(reads[(probe.name, "c")], 1)
        self.assertEqual(reads[(probe.name, "d")], 1)

    def test_each_decision_site_asks_the_kernel(self) -> None:
        for module, function in KERNEL_DECISION_SITES.items():
            with self.subTest(module=module):
                self.assertIn("roster_decision", calls(module, function))

    def test_the_roster_and_the_per_check_verdict_are_kernel_calls(self) -> None:
        self.assertIn("evaluation_roster_complete", calls("finalize.py", "roster_decision"))
        self.assertIn("evaluation_admissible", calls("finalize.py", "evaluation_record"))
        self.assertIn("evaluation_classify", calls("finalize.py", "evaluation_record"))


# 1.9.0 (typed absence): the modules that produce collapse inputs never state "nothing" as a
# value. An identity that could not be established is None and reaches the kernel as absent.
PROMOTION_MODULES = ("transaction.py", "finalize.py", "revalidate.py", "validation.py", "returning.py",
                     "checkpoint.py", "executed.py", "core.py")


# (module, enclosing function) -> (how many, why it is not a stand-in identity).
ALLOWED_SENTINELS = {
    ("executed.py", "bundle_identity"): (1,
        "the input encoding of the verifier-set digest: a member with empty content hashes as 32"
        " zero bytes inside the digest, never a value handed to the kernel; the formula is the"
        " released identity of every recorded executedVerifierSet"),
}


def sentinels(module: str, root: Path = RUNTIME) -> list[tuple[str, str, int, str]]:
    """Every spelling of a stand-in identity, in source order: a zero or 0xff digest
    (bytes(32), b"\\x00" * 32, "0" * 64), a fallback to the no-bundle token
    (`x or NO_BUNDLE_IDENTITY`), and a defaulted evidence profile (`.get("profile", ...)`)."""
    tree = ast.parse((root / module).read_text(encoding="utf-8"))
    found: list[tuple[str, str, int, str]] = []

    def width(node: ast.AST) -> int | None:
        # A digest width spelled as a literal or as the runtime's own constant (review of
        # a23c265: `bytes(HASH_BYTES)` escaped the literal-only match).
        if isinstance(node, ast.Constant) and node.value in (32, 64):
            return node.value
        if isinstance(node, (ast.Name, ast.Attribute)) and getattr(node, "id", getattr(node, "attr", None)) == "HASH_BYTES":
            return 32
        return None

    def profile_get(node: ast.AST) -> bool:
        return (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "get"
                and node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value == "profile")

    def spelling(node: ast.AST) -> str | None:
        if (isinstance(node, ast.Call) and getattr(node.func, "id", None) == "bytes" and len(node.args) == 1
                and width(node.args[0]) is not None):
            return "bytes(32)"
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
            for unit, count in ((node.left, node.right), (node.right, node.left)):
                if (isinstance(unit, ast.Constant) and isinstance(unit.value, (bytes, str)) and len(unit.value) == 1
                        and width(count) is not None):
                    return f"{unit.value!r} * {width(count)}"
        if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or) and profile_get(node.values[0]):
            return ".get('profile', default)"
        if isinstance(node, ast.IfExp) and (profile_get(node.test) or profile_get(node.body)) and isinstance(node.orelse, ast.Constant):
            return ".get('profile', default)"
        if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or) and any(
                isinstance(value, ast.Name) and value.id == "NO_BUNDLE_IDENTITY" for value in node.values[1:]):
            return "or NO_BUNDLE_IDENTITY"
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "get"
                and len(node.args) == 2 and isinstance(node.args[0], ast.Constant) and node.args[0].value == "profile"):
            return ".get('profile', default)"
        return None

    def visit(node: ast.AST, function: str) -> None:
        for child in ast.iter_child_nodes(node):
            name = child.name if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) else function
            text = spelling(child)
            if text is not None:
                found.append((module, name, child.lineno, text))
            visit(child, name)

    visit(tree, "<module>")
    return sorted(found, key=lambda hit: hit[2])


class NoSentinelIdentities(unittest.TestCase):
    def test_promotion_modules_state_no_identity_as_a_value(self) -> None:
        sites = Counter((module, function) for name in PROMOTION_MODULES for module, function, _line, _text in sentinels(name))
        self.assertEqual(dict(sites), {key: count for key, (count, _why) in ALLOWED_SENTINELS.items()})

    def test_the_audit_sees_the_spellings_it_claims_to(self) -> None:
        import tempfile
        source = (
            "def a():\n    return hash_id(bytes(32))\n"
            "def b():\n    return b'\\xff' * 32\n"
            "def c():\n    return 'sha256:' + '0' * 64\n"
            "def d(x):\n    return x or NO_BUNDLE_IDENTITY\n"
            "def e(item):\n    return item.get('profile', 'legacy')\n"
            "def f(item):\n    return item.get('profile')\n"
            "def g():\n    return bytes(HASH_BYTES)\n"
            "def h():\n    return b'\\x00' * core.HASH_BYTES\n"
            "def i(item):\n    return item.get('profile') or 'legacy'\n"
            "def j(item):\n    return item.get('profile') if item.get('profile') else 'legacy'\n"
        )
        with tempfile.TemporaryDirectory() as temporary:
            probe = Path(temporary) / "probe.py"
            probe.write_text(source, encoding="utf-8")
            hits = sentinels(probe.name, Path(temporary))
        self.assertEqual([text for _module, _function, _line, text in hits],
                         ["bytes(32)", "b'\\xff' * 32", "'0' * 64", "or NO_BUNDLE_IDENTITY", ".get('profile', default)",
                          "bytes(32)", "b'\\x00' * 32", ".get('profile', default)", ".get('profile', default)"])

    def test_collapse_input_has_no_defaults(self) -> None:
        import dataclasses
        from worldline.core import CollapseInput
        fields = dataclasses.fields(CollapseInput)
        self.assertTrue(fields)
        for field in fields:
            with self.subTest(field=field.name):
                self.assertIs(field.default, dataclasses.MISSING)
                self.assertIs(field.default_factory, dataclasses.MISSING)
        with self.assertRaises(TypeError):
            CollapseInput(candidate_state="VALID")  # every other input missing


ROOT = Path(__file__).resolve().parents[1]


class ContractPins(unittest.TestCase):
    """The contracts this release claims are pinned in verify_proof_manifest.CONTRACT_PINS
    (review of a23c265: the check floor cannot see a deleted Post clause, and the C boundary
    is exempt from the SPARK_Mode screen)."""

    def setUp(self) -> None:
        import importlib.util
        spec = importlib.util.spec_from_file_location("verify_proof_manifest", ROOT / "verify_proof_manifest.py")
        self.verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.verifier)

    def test_the_tree_matches_every_pin(self) -> None:
        for key, pinned in self.verifier.CONTRACT_PINS.items():
            with self.subTest(key=key):
                self.assertEqual(self.verifier.contract_pin(ROOT, key), pinned)

    def test_collapse_decide_is_only_the_null_check_and_the_proved_call(self) -> None:
        body = self.verifier.contract_text(ROOT, "core/worldline-c_api.adb#Collapse_Decide")
        self.assertEqual(body, (
            "function Collapse_Decide (Request : C_Collapse_Request_Access) return Interfaces.Unsigned_8 is "
            "begin if Request = null then return Collapse_Wire.Invalid_Request; end if; "
            "return Collapse_Wire.Decide_Wire (Request.all); "
            "exception when others => return Collapse_Wire.Invalid_Request; end Collapse_Decide;"))

    def test_a_weakened_postcondition_or_a_shortcut_changes_its_pin(self) -> None:
        import shutil
        import tempfile
        edits = {
            "core/worldline-collapse.ads": ("and then Decide'Result /= Owner_Mismatch", "and then True"),
            "core/worldline-collapse_wire.ads": ("and then (if R.Phase = 1 then R.Actual_Staged_Root.Present = 0)", ""),
            "core/worldline-c_api.adb": ("return Collapse_Wire.Decide_Wire (Request.all);", "return 0;"),
        }
        for key, (old, new) in edits.items():
            relative = key.partition("#")[0]
            with self.subTest(key=key), tempfile.TemporaryDirectory() as temporary:
                target = Path(temporary) / relative
                target.parent.mkdir(parents=True)
                shutil.copy2(ROOT / relative, target)
                text = target.read_text(encoding="utf-8")
                self.assertIn(old, text)
                target.write_text(text.replace(old, new, 1), encoding="utf-8")
                self.assertNotEqual(self.verifier.contract_pin(Path(temporary), key), self.verifier.CONTRACT_PINS[key])

    def test_the_pinned_set_is_exactly_the_claimed_contracts(self) -> None:
        self.assertEqual(set(self.verifier.CONTRACT_PINS), {
            "worldline.gpr", "core/worldline_core.gpr", "core/worldline_core_sources.gpr", "core/attest_sha256.gpr",
            "tests/worldline_tests.gpr",
            "core/worldline.ads", "core/attest/attest.ads", "core/attest/attest-sha256.ads",
            "core/worldline-c_api.ads", "core/worldline-c_api.adb",
            "core/worldline-collapse.ads", "core/worldline-collapse_wire.ads", "core/worldline-identities.ads",
            "core/worldline-evaluation.ads", "core/worldline-transitions.ads"})

    def test_a_declaration_shadowing_the_proved_call_changes_the_boundary_pin(self) -> None:
        import shutil
        import tempfile
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "core/worldline-c_api.adb"
            target.parent.mkdir(parents=True)
            shutil.copy2(ROOT / "core/worldline-c_api.adb", target)
            text = target.read_text(encoding="utf-8")
            marker = "   function Collapse_Decide"
            self.assertIn(marker, text)
            target.write_text(text.replace(marker, "   package Collapse_Wire renames Worldline.Collapse_Wire;\n" + marker, 1), encoding="utf-8")
            self.assertNotEqual(self.verifier.contract_pin(Path(temporary), "core/worldline-c_api.adb"),
                                self.verifier.CONTRACT_PINS["core/worldline-c_api.adb"])

    def test_the_export_must_be_bound_once_to_collapse_decide(self) -> None:
        import shutil
        import tempfile
        self.assertEqual(self.verifier.export_problems(ROOT), [])
        original = (ROOT / "core/worldline-c_api.ads").read_text(encoding="utf-8")
        binding = 'External_Name => "wl_collapse_decide"'
        cases = {
            "moved": original.replace(binding, 'External_Name => "wl_collapse_decide_old"').replace(
                'External_Name => "wl_transaction_transition_allowed"', binding),
            "duplicated": original.replace('External_Name => "wl_transaction_transition_allowed"', binding),
        }
        for label, text in cases.items():
            with self.subTest(label), tempfile.TemporaryDirectory() as temporary:
                target = Path(temporary) / "core/worldline-c_api.ads"
                target.parent.mkdir(parents=True)
                target.write_text(text, encoding="utf-8")
                self.assertTrue(self.verifier.export_problems(Path(temporary)))

    def test_the_gate_checks_the_pins_before_it_writes_the_manifest(self) -> None:
        gate = (ROOT / "prove.sh").read_text(encoding="utf-8")
        check = gate.index("if contract_problems(root):")
        self.assertLess(check, gate.index("manifest_path.write_text("))
        self.assertLess(check, gate.index("PROOF GATE PASSED"))
        verifier = (ROOT / "verify_proof_manifest.py").read_text(encoding="utf-8")
        self.assertIn("problems = contract_problems(root)", verifier)

    def test_a_project_file_that_redirects_a_unit_or_a_stray_source_is_refused(self) -> None:
        import shutil
        import tempfile
        with tempfile.TemporaryDirectory() as temporary:
            tree = Path(temporary)
            shutil.copytree(ROOT / "core", tree / "core")
            shutil.copy2(ROOT / "worldline.gpr", tree / "worldline.gpr")
            (tree / "tests").mkdir()
            shutil.copy2(ROOT / "tests/worldline_tests.gpr", tree / "tests/worldline_tests.gpr")
            self.assertEqual(self.verifier.contract_problems(tree), [])
            sources = tree / "core/worldline_core_sources.gpr"
            sources.write_text(sources.read_text(encoding="utf-8").replace('for Source_Dirs use (".");', 'for Source_Dirs use ("boundary", ".");'), encoding="utf-8")
            (tree / "core/boundary").mkdir()
            shutil.copy2(ROOT / "core/worldline-c_api.adb", tree / "core/boundary/worldline-c_api.adb")
            problems = self.verifier.contract_problems(tree)
            self.assertTrue(any("core/worldline_core_sources.gpr" in problem for problem in problems), problems)
            self.assertTrue(any("core/boundary/worldline-c_api.adb" in problem for problem in problems), problems)

    def test_the_verifier_refuses_a_changed_contract(self) -> None:
        import shutil
        import subprocess
        import sys
        import tempfile
        with tempfile.TemporaryDirectory() as temporary:
            tree = Path(temporary)
            for name in ("verify_proof_manifest.py", "proof-manifest.json", "worldline.gpr"):
                shutil.copy2(ROOT / name, tree / name)
            shutil.copytree(ROOT / "core", tree / "core")
            (tree / "tests").mkdir()
            shutil.copy2(ROOT / "tests/worldline_tests.gpr", tree / "tests/worldline_tests.gpr")
            run = lambda: subprocess.run([sys.executable, "verify_proof_manifest.py", "--sources-only"], cwd=tree,
                                         capture_output=True, text=True, env={"PYTHONDONTWRITEBYTECODE": "1"})
            self.assertEqual(run().returncode, 0)
            spec = tree / "core/worldline-collapse.ads"
            spec.write_text(spec.read_text(encoding="utf-8").replace("and then Decide'Result /= Owner_Mismatch", "and then True", 1), encoding="utf-8")
            refused = run()
            self.assertNotEqual(refused.returncode, 0)
            self.assertIn("pinned contract changed: core/worldline-collapse.ads", refused.stderr)

    def test_comments_and_layout_do_not_move_a_pin(self) -> None:
        text = "function F return Boolean   -- a comment\n  is (True);\n"
        self.assertEqual(self.verifier.normalized_ada(text), "function F return Boolean is (True);")
        self.assertEqual(self.verifier.normalized_ada('X : String := "a -- b"; -- note'), 'X : String := "a -- b";')


if __name__ == "__main__":
    unittest.main()
