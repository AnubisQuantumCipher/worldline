"""Dry-run rejection tests for the release gate (JANUS II §8). No network, no GitHub: the
gate is a pure function over gathered facts, and every rejection the mission names is
exercised here against a known-good baseline that the gate accepts."""
from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("release_gate", REPO / "scripts" / "release_gate.py")
gate = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["release_gate"] = gate  # dataclasses resolve annotations through sys.modules
spec.loader.exec_module(gate)

SHA = "a" * 40
OTHER = "b" * 40
TREE = "c" * 40
SOURCES = {"core/worldline-collapse.ads": "11", "core/worldline-collapse.adb": "22"}


def good_assurance() -> dict:
    return {
        "schemaVersion": 1,
        "result": "PASS",
        "checkout": {"sha": SHA, "tree": TREE, "dirty": False, "expectedSha": SHA},
        "runtimeVersion": "1.3.0",
        "requiredSteps": list(gate.REQUIRED_STEPS),
        "steps": [{"name": name, "status": "success", "durationSeconds": 1.0, "logSha256": "0" * 64} for name in gate.REQUIRED_STEPS],
        "pythonTests": {"ran": 167, "ok": True, "failures": 0, "errors": 0, "skipped": 0, "verdictLine": "OK"},
        "proof": {
            "committedManifest": {"present": True, "sourceHashes": SOURCES},
            "regeneratedManifest": {"present": True, "total": 130, "minimumChecks": 130, "unproved": 0, "justified": 0, "pragmaAssume": 0, "sourceHashes": SOURCES, "librarySha256": "d" * 64, "manifestSha256": "e" * 64},
            "consistent": True,
        },
        "toolchain": {"gnat": "GNAT 16.1.0"},
        "host": {},
    }


def good_facts() -> dict:
    return {
        "release_sha": SHA,
        "release_tree": TREE,
        "tag": "v1.3.0",
        "tag_target_sha": SHA,
        "version": "1.3.0",
        "changelog": "# Changelog\n\n## 1.3.0 — 2026-09-21 · evidence freshness\n\n- things\n\n## 1.2.2 — old\n",
        "assurance": good_assurance(),
        "committed_proof_manifest": {"sourceHashes": SOURCES, "proof": {"total": 130}},
        "remote_tag_sha": None,
        "release_exists": False,
        "artifacts": {"worldline-v1.3.0.tar.gz": "f" * 64, "worldline-v1.3.0.tar.gz.sha256": "1" * 64, "release-manifest.json": "2" * 64},
        "expected_artifacts": {"worldline-v1.3.0.tar.gz": "f" * 64, "worldline-v1.3.0.tar.gz.sha256": "1" * 64, "release-manifest.json": "2" * 64},
    }


class ReleaseGateAcceptsOnlyTheExactAssuredCommit(unittest.TestCase):
    def test_known_good_control_is_accepted(self) -> None:
        verdict = gate.evaluate(**good_facts())
        self.assertTrue(verdict.accepted, verdict.reasons)

    def _rejected(self, mutate, needle: str) -> list[str]:
        facts = good_facts()
        mutate(facts)
        verdict = gate.evaluate(**facts)
        self.assertFalse(verdict.accepted, "the defective control was accepted")
        self.assertTrue(any(needle in r for r in verdict.reasons), (needle, verdict.reasons))
        return verdict.reasons

    def test_successful_ci_of_the_wrong_commit(self) -> None:
        def mutate(f):
            f["assurance"]["checkout"]["sha"] = OTHER
        self._rejected(mutate, "belongs to")

    def test_successful_ci_of_the_wrong_tree(self) -> None:
        def mutate(f):
            f["assurance"]["checkout"]["tree"] = "9" * 40
        self._rejected(mutate, "differs from the release tree")

    def test_dirty_checkout(self) -> None:
        def mutate(f):
            f["assurance"]["checkout"]["dirty"] = True
        self._rejected(mutate, "dirty")

    def test_missing_assurance_report(self) -> None:
        def mutate(f):
            f["assurance"] = None
        self._rejected(mutate, "missing")

    def test_failed_skipped_cancelled_timed_out_and_missing_required_steps(self) -> None:
        for status in ("failure", "skipped", "cancelled", "timed_out", "in_progress"):
            def mutate(f, status=status):
                step = next(s for s in f["assurance"]["steps"] if s["name"] == "python-tests")
                step["status"] = status
            self._rejected(mutate, f"python-tests is {status!r}")
        def missing(f):
            f["assurance"]["steps"] = [s for s in f["assurance"]["steps"] if s["name"] != "proof-gate"]
        self._rejected(missing, "missing from the assurance run: proof-gate")
        def partial(f):
            f["assurance"]["steps"] = f["assurance"]["steps"][:3]  # only some jobs succeeded
        self._rejected(partial, "missing from the assurance run")
        def overall(f):
            f["assurance"]["result"] = "FAIL"
        self._rejected(overall, "not PASS")

    def test_a_run_that_collected_almost_nothing_is_rejected(self) -> None:
        def mutate(f):
            f["assurance"]["pythonTests"] = {"ran": 1, "ok": True, "failures": 0, "errors": 0, "skipped": 0, "verdictLine": "OK"}
        self._rejected(mutate, "below the floor")

    def test_unbounded_skips_are_rejected(self) -> None:
        def mutate(f):
            f["assurance"]["pythonTests"] = {"ran": 161, "ok": True, "failures": 0, "errors": 0, "skipped": 40, "verdictLine": "OK (skipped=40)"}
        self._rejected(mutate, "skipped 40")
        facts = good_facts(); facts["assurance"]["pythonTests"]["skipped"] = 2
        self.assertTrue(gate.evaluate(**facts).accepted)

    def test_python_failures_reject_even_if_steps_claim_success(self) -> None:
        def mutate(f):
            f["assurance"]["pythonTests"] = {"ran": 142, "ok": False, "failures": 1, "errors": 0, "verdictLine": "FAILED (failures=1)"}
        self._rejected(mutate, "python tests")

    def test_version_tag_mismatch(self) -> None:
        self._rejected(lambda f: f.update(tag="v1.3.1", tag_target_sha=SHA), "does not match the runtime version")
        self._rejected(lambda f: f.update(version="1.4.0"), "does not match the runtime version")
        self._rejected(lambda f: f.update(tag="latest"), "not a vMAJOR.MINOR.PATCH")
        self._rejected(lambda f: f.update(changelog="# Changelog\n\n## 1.2.2 — old\n"), "CHANGELOG.md has no section")
        def assured_other_version(f):
            f["assurance"]["runtimeVersion"] = "1.2.2"
        self._rejected(assured_other_version, "recorded runtime version")

    def test_tag_pointing_elsewhere(self) -> None:
        self._rejected(lambda f: f.update(tag_target_sha=OTHER), "resolves to")
        self._rejected(lambda f: f.update(remote_tag_sha=OTHER), "already exists on the remote")

    def test_existing_release_is_never_replaced(self) -> None:
        self._rejected(lambda f: f.update(release_exists=True), "already exists")

    def test_missing_or_mismatched_proof_evidence(self) -> None:
        def absent(f):
            f["assurance"]["proof"]["regeneratedManifest"] = {"present": False}
        self._rejected(absent, "no regenerated proof manifest")
        def unproved(f):
            f["assurance"]["proof"]["regeneratedManifest"]["unproved"] = 1
        self._rejected(unproved, "unproved=1")
        def assumed(f):
            f["assurance"]["proof"]["regeneratedManifest"]["pragmaAssume"] = 2
        self._rejected(assumed, "pragmaAssume=2")
        def below_floor(f):
            f["assurance"]["proof"]["regeneratedManifest"]["total"] = 129
        self._rejected(below_floor, "below the floor")
        def other_sources(f):
            f["assurance"]["proof"]["regeneratedManifest"]["sourceHashes"] = {"core/x.ads": "zz"}
        self._rejected(other_sources, "different sources")
        def no_committed(f):
            f["committed_proof_manifest"] = None
        self._rejected(no_committed, "committed proof manifest is missing")
        def inconsistent(f):
            f["assurance"]["proof"]["consistent"] = False
        self._rejected(inconsistent, "consistent proof")

    def test_source_only_manifest_check_is_not_a_fresh_proof(self) -> None:
        # A run whose only proof evidence is the committed manifest (no regeneration): rejected.
        def mutate(f):
            f["assurance"]["proof"] = {"committedManifest": {"present": True, "sourceHashes": SOURCES}, "regeneratedManifest": {"present": False}, "consistent": False}
            f["assurance"]["steps"] = [s for s in f["assurance"]["steps"] if s["name"] != "proof-gate"]
        reasons = self._rejected(mutate, "proof-gate")
        self.assertTrue(any("regenerated" in r for r in reasons), reasons)

    def test_artifact_substitution(self) -> None:
        def swapped(f):
            f["artifacts"]["worldline-v1.3.0.tar.gz"] = "0" * 64
        self._rejected(swapped, "digest")
        def extra(f):
            f["artifacts"]["evil.tar.gz"] = "0" * 64
        self._rejected(extra, "artifact set differs")
        def missing(f):
            del f["artifacts"]["release-manifest.json"]
        self._rejected(missing, "artifact set differs")

    def test_command_line_dry_run_with_real_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "version.py").write_text('__version__ = "1.3.0"\n', encoding="utf-8")
            (root / "CHANGELOG.md").write_text(good_facts()["changelog"], encoding="utf-8")
            (root / "assurance.json").write_text(json.dumps(good_assurance()), encoding="utf-8")
            (root / "proof-manifest.json").write_text(json.dumps({"sourceHashes": SOURCES}), encoding="utf-8")
            (root / "worldline-v1.3.0.tar.gz").write_bytes(b"archive")
            import hashlib
            digest = hashlib.sha256(b"archive").hexdigest()
            base = [sys.executable, str(REPO / "scripts" / "release_gate.py"), "--release-sha", SHA, "--release-tree", TREE, "--tag", "v1.3.0", "--tag-target-sha", SHA,
                    "--version-file", str(root / "version.py"), "--changelog", str(root / "CHANGELOG.md"), "--assurance", str(root / "assurance.json"),
                    "--proof-manifest", str(root / "proof-manifest.json"), "--release-exists", "no",
                    "--artifact", f"worldline-v1.3.0.tar.gz={root / 'worldline-v1.3.0.tar.gz'}", "--expected-artifact", f"worldline-v1.3.0.tar.gz={digest}"]
            accepted = subprocess.run([*base, "--write-manifest", str(root / "release-manifest.json")], capture_output=True, text=True)
            self.assertEqual(accepted.returncode, 0, accepted.stdout + accepted.stderr)
            manifest = json.loads((root / "release-manifest.json").read_text(encoding="utf-8"))
            self.assertTrue(manifest["accepted"])
            self.assertEqual(manifest["proof"]["total"], 130)
            self.assertEqual(manifest["artifacts"], [{"name": "worldline-v1.3.0.tar.gz", "sha256": digest}])
            self.assertEqual(manifest["signing"], {"method": "unsigned"})
            # wrong commit on the command line: the assurance report names SHA, the release is OTHER
            wrong = subprocess.run([arg if arg != SHA else OTHER for arg in base], capture_output=True, text=True)
            self.assertEqual(wrong.returncode, 1)
            self.assertIn("belongs to", wrong.stdout)
            substituted = subprocess.run([*base[:-1], "worldline-v1.3.0.tar.gz=" + "0" * 64], capture_output=True, text=True)
            self.assertEqual(substituted.returncode, 1)
            self.assertIn("digest", substituted.stdout)
            no_report = subprocess.run([arg if arg != str(root / "assurance.json") else str(root / "absent.json") for arg in base], capture_output=True, text=True)
            self.assertEqual(no_report.returncode, 1)
            self.assertIn("missing", no_report.stdout)


if __name__ == "__main__":
    unittest.main()
