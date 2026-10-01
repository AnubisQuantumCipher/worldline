from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location("pair_report", Path(__file__).resolve().parents[1] / "scripts/verify_release_pair_report.py")
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)

COMMIT, TREE = "a" * 40, "b" * 40
REPORT = {"schema": "worldline-release-pair-validation-v1", "accepted": True,
          "engineCommit": COMMIT, "engineTree": TREE, "pluginCommit": "c" * 40,
          "pluginArchiveSha256": "d" * 64, "codeSetSha256": "e" * 64}
MANIFEST = {"schemaVersion": 1, "accepted": True, "commit": COMMIT, "tree": TREE, "version": "1.9.2",
            "pluginCompatibility": {"schema": "worldline-plugin-compatibility-v1", "engine": "1.9.2",
                                    "codeSetSha256": REPORT["codeSetSha256"],
                                    "plugin": {"commit": REPORT["pluginCommit"],
                                               "archiveSha256": REPORT["pluginArchiveSha256"]}}}
REPORT["pluginCompatibilitySha256"] = hashlib.sha256(json.dumps(
    MANIFEST["pluginCompatibility"], sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")).hexdigest()


class ReleasePairReportTests(unittest.TestCase):
    def test_complete_same_run_pair_binds(self) -> None:
        self.assertEqual(checker.problems(REPORT, MANIFEST, COMMIT, TREE), [])

    def test_missing_identity_refuses(self) -> None:
        for key in ("engineCommit", "engineTree", "pluginCommit", "pluginArchiveSha256", "codeSetSha256", "pluginCompatibilitySha256"):
            with self.subTest(key=key):
                report = dict(REPORT)
                del report[key]
                self.assertTrue(checker.problems(report, MANIFEST, COMMIT, TREE))

    def test_unaccepted_or_absent_documents_refuse(self) -> None:
        for report, manifest in ((None, MANIFEST), (REPORT, None), ({**REPORT, "accepted": False}, MANIFEST)):
            self.assertTrue(checker.problems(report, manifest, COMMIT, TREE))

    def test_other_workflow_identity_refuses(self) -> None:
        self.assertTrue(checker.problems(REPORT, MANIFEST, "f" * 40, TREE))
        self.assertTrue(checker.problems(REPORT, MANIFEST, COMMIT, "f" * 40))

    def test_other_pair_version_refuses(self) -> None:
        manifest = copy.deepcopy(MANIFEST)
        manifest["pluginCompatibility"]["engine"] = "1.9.1"
        self.assertTrue(checker.problems(REPORT, manifest, COMMIT, TREE))

    def test_complete_compatibility_record_is_bound(self) -> None:
        manifest = copy.deepcopy(MANIFEST)
        manifest["pluginCompatibility"]["plugin"]["tag"] = "v1.3.5"
        self.assertIn("complete plugin compatibility record differs from the validated pair",
                      checker.problems(REPORT, manifest, COMMIT, TREE))


if __name__ == "__main__":
    unittest.main()
