"""Static audit (1.8.0): the promotion decision has no independent Python definition.

Every comparison of a verdict-like field with "PASS" or "COMPLETED" in the modules that decide
or feed promotion is listed below with the reason it is not an authorization. A new one fails
this test until it is either removed or added here with a reason a reviewer can check. The
decision sites themselves must reach the kernel through `roster_decision`.

This is a syntactic audit: it proves the listed comparisons are the only ones spelled this way,
not that no other Python expression influences a decision.
"""
from __future__ import annotations

import ast
from pathlib import Path
import unittest

RUNTIME = Path(__file__).resolve().parents[1] / "runtime" / "worldline"
AUDITED = ("finalize.py", "revalidate.py", "transaction.py", "simulation.py", "validation.py", "returning.py")
VERDICTS = {"PASS", "COMPLETED"}

# (module, enclosing function) -> why the comparison is not an authorization.
ALLOWED = {
    ("finalize.py", "_private_report_verified"):
        "report integrity is an input fact to Evaluation.Admissible; requiring the kernel's own"
        " COMPLETED classification here can only make a report less trusted",
    ("finalize.py", "refusal_reason"): "diagnostic text for a check the kernel already refused",
    ("finalize.py", "evaluation_record"):
        "the Python mapping of raw fields to the kernel's finite categories (the declared"
        " unproved boundary)",
    ("transaction.py", "prepare"):
        "staged-merge revalidation outcome selects tested_root := staged_content_root; the outcome"
        " is itself the kernel roster verdict of revalidate._evaluate, and the tested=staged"
        " obligation is Phase 1 item 1 (recorded in docs/phase1-evaluation-lifecycle.md)",
    ("validation.py", "effective_evidence"):
        "selects which evaluation speaks for a world (Phase 1 item 5, one effective evaluation);"
        " promotion still recomputes every check of the selected evaluation in the kernel",
    ("simulation.py", "run"):
        "the health report of a system future, which prepare refuses as a collapse candidate and"
        " as a return subject",
}
KERNEL_DECISION_SITES = {
    "finalize.py": "finalize",
    "revalidate.py": "_evaluate",
    "transaction.py": "_execution_identity",
}


def comparisons(module: str) -> list[tuple[str, int]]:
    tree = ast.parse((RUNTIME / module).read_text(encoding="utf-8"))
    found: list[tuple[str, int]] = []

    def visit(node: ast.AST, function: str) -> None:
        for child in ast.iter_child_nodes(node):
            name = child.name if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) else function
            if isinstance(child, ast.Compare):
                operands = [child.left, *child.comparators]
                constants = {operand.value for operand in operands
                             if isinstance(operand, ast.Constant) and isinstance(operand.value, str)}
                tuples = {element.value for operand in operands if isinstance(operand, (ast.Tuple, ast.Set, ast.List))
                          for element in operand.elts if isinstance(element, ast.Constant)}
                if (constants | tuples) & VERDICTS:
                    found.append((name, child.lineno))
            visit(child, name)

    visit(tree, "<module>")
    return found


def calls(module: str, function: str) -> set[str]:
    tree = ast.parse((RUNTIME / module).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function:
            return {getattr(call.func, "id", getattr(call.func, "attr", ""))
                    for call in ast.walk(node) if isinstance(call, ast.Call)}
    return set()


class NoPythonAdmissibility(unittest.TestCase):
    def test_every_verdict_comparison_is_listed_with_a_reason(self) -> None:
        unlisted = [(module, function, line) for module in AUDITED
                    for function, line in comparisons(module) if (module, function) not in ALLOWED]
        self.assertEqual(unlisted, [], "a verdict comparison outside the kernel; remove it or list it with a reason")

    def test_the_allowlist_has_no_stale_entries(self) -> None:
        present = {(module, function) for module in AUDITED for function, _line in comparisons(module)}
        self.assertEqual(sorted(set(ALLOWED) - present), [])

    def test_each_decision_site_asks_the_kernel(self) -> None:
        for module, function in KERNEL_DECISION_SITES.items():
            with self.subTest(module=module):
                self.assertIn("roster_decision", calls(module, function))

    def test_the_roster_and_the_per_check_verdict_are_kernel_calls(self) -> None:
        self.assertIn("evaluation_roster_complete", calls("finalize.py", "roster_decision"))
        self.assertIn("evaluation_admissible", calls("finalize.py", "evaluation_record"))
        self.assertIn("evaluation_classify", calls("finalize.py", "evaluation_record"))

    def test_saved_verdicts_are_not_read_at_the_promotion_boundary(self) -> None:
        # The promotion boundary recomputes; it never reads a stored admissibleForPromotion or
        # executionStatus back as authority.
        for module in ("transaction.py", "revalidate.py"):
            source = (RUNTIME / module).read_text(encoding="utf-8")
            with self.subTest(module=module):
                self.assertNotIn('get("admissibleForPromotion")', source)
                self.assertNotIn('get("executionStatus")', source)


if __name__ == "__main__":
    unittest.main()
