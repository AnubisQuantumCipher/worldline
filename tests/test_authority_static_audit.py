"""Static audit (1.8.0): the promotion decision has no independent Python definition.

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
    ("transaction.py", "prepare"): (1,
        "staged-merge revalidation outcome selects tested_root := staged_content_root; the outcome"
        " is itself the kernel roster verdict of revalidate._evaluate, and the tested=staged"
        " obligation is Phase 1 item 1"),
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
    "revalidate.py": "_evaluate",
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


if __name__ == "__main__":
    unittest.main()
