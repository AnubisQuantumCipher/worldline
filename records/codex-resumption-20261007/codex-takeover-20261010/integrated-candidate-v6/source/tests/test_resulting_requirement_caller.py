"""Commit requirement producer correspondence; no observer result claims authority.

The actual staged policy/verifier producer and native hashing are exercised. The
decision endpoint observes arguments only: native authority and actual exchange
are covered by the original ABI/transaction controls and their positive cases.
"""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from worldline.canonical import canonical_bytes
from worldline.core import Core
from worldline.errors import WorldlineError
from worldline.transaction import CollapseTransaction
from worldline.validation import current_requirements, requirements_for_tree


class ResultingRequirementCaller(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-resulting-caller-")
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        self.live = root / "live"
        self.payload = root / "staged"
        self.staged = self.payload / "primary"
        self.policy = {
            "schemaVersion": 1, "generated": [], "services": [],
            "protected": ["sentinel"], "checks": [{
                "id": "exam", "kind": "tests", "required": True,
                "argv": ["/usr/bin/python3", "evaluator/exam.py"],
                "format": "exit", "covers": ["candidate.txt"],
                "verifiers": ["evaluator/*"],
            }],
        }
        for tree in (self.live, self.staged):
            (tree / "evaluator").mkdir(parents=True)
            (tree / ".worldline.json").write_text(json.dumps(self.policy), encoding="utf-8")
            (tree / "evaluator/exam.py").write_text("raise SystemExit(0)\n", encoding="utf-8")
        self.roots = [{"root_key": "primary", "primary_root": True,
                       "path": os.fsencode(self.live), "display_path": str(self.live)}]
        self.store = SimpleNamespace(
            roots=lambda: self.roots,
            prime=lambda: None,
            paths=SimpleNamespace(root_source=lambda _root: os.fsencode(self.live)),
        )
        self.core = Core.shared()
        self.current = current_requirements(self.store, None, self.core)
        self.calls = []
        self.observer_result = object()

        def observe(**arguments):
            self.calls.append(arguments)
            return self.observer_result

        self.manager = SimpleNamespace(
            store=self.store, config=None, core=self.core,
            prime=SimpleNamespace(root_set_hash=lambda _roots: None),
            _foreign_writes=lambda *_args: ("UNMEASURED", {}),
            _watch_sets=lambda: (None, None),
            _subject_pair=lambda *_args: (None, None),
            _declared_verifiers=lambda _requirement: None,
            _generation=lambda: None,
            _decide=observe,
        )
        self.candidate = object()
        self.record = {
            "decisionInputs": {
                "resultingRequirement": {"requirementHash": "retained-prepare-observation"},
            },
            "validation": {"mode": "collapse"},
            "stagingPayload": str(self.payload),
        }

    def authorize_observation(self):
        return CollapseTransaction._authorize(
            self.manager, self.record, self.candidate, current_manifests={},
            staged_root=None, staged_content_root=None,
            current_requirement=self.current, generation_before=None,
        )

    def assert_actual_requirement_reaches_caller(self) -> None:
        self.assertIs(self.authorize_observation(), self.observer_result)
        arguments, = self.calls
        measured = requirements_for_tree(self.store, None, self.payload, self.roots, self.core)
        self.assertEqual(arguments["current_requirement"], self.current["requirementHash"])
        self.assertIs(arguments["authoritative_requirement"], self.current)
        self.assertEqual(arguments["resulting_requirement"], measured)
        self.assertIs(arguments["inputs"]["resultingRequirement"], arguments["resulting_requirement"])
        # Item7 retains a complete detached canonical snapshot after _decide.
        # The producer mapping must match it without aliasing mutable inputs.
        self.assertEqual(self.record["decisionInputsAtCommit"],
                         json.loads(canonical_bytes(arguments["inputs"])))
        self.assertIsNot(self.record["decisionInputsAtCommit"], arguments["inputs"])
        self.assertEqual(self.record["decisionInputsAtCommit"]["resultingRequirement"],
                         arguments["resulting_requirement"])
        self.assertIsNot(self.record["decisionInputsAtCommit"]["resultingRequirement"],
                         arguments["resulting_requirement"])
        self.assertEqual(self.record["decisionInputs"]["resultingRequirement"],
                         {"requirementHash": "retained-prepare-observation"})

    def test_commit_measures_resulting_requirement_before_retention_and_decision(self) -> None:
        self.assert_actual_requirement_reaches_caller()
        self.assertEqual(self.calls[0]["resulting_requirement"]["requirementHash"],
                         self.current["requirementHash"])

    def test_staged_changes_do_not_alias_live_or_retained_requirement(self) -> None:
        for change in ("loosen-checks", "drop-protected", "rewrite-examiner"):
            with self.subTest(change=change):
                self.calls.clear()
                changed = copy.deepcopy(self.policy)
                examiner = self.staged / "evaluator/exam.py"
                examiner.write_text("raise SystemExit(0)\n", encoding="utf-8")
                if change == "loosen-checks":
                    changed["checks"] = []
                elif change == "drop-protected":
                    changed["protected"] = []
                else:
                    examiner.write_text("# changed examiner\nraise SystemExit(0)\n", encoding="utf-8")
                (self.staged / ".worldline.json").write_text(json.dumps(changed), encoding="utf-8")
                self.assert_actual_requirement_reaches_caller()
                self.assertNotEqual(self.calls[0]["resulting_requirement"]["requirementHash"],
                                    self.current["requirementHash"])
                self.assertEqual(current_requirements(self.store, None, self.core), self.current)

    def test_missing_staged_root_refuses_before_any_decision_observation(self) -> None:
        self.record["stagingPayload"] = str(self.payload / "absent")
        with self.assertRaises(WorldlineError) as raised:
            self.authorize_observation()
        self.assertEqual(raised.exception.code, "STAGED_ROOT_ABSENT")
        self.assertEqual(self.calls, [])
        self.assertNotIn("decisionInputsAtCommit", self.record)


if __name__ == "__main__":
    unittest.main()
