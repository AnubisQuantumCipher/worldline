from __future__ import annotations

from dataclasses import replace
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from worldline.core import CollapseInput, Core
from worldline.errors import WorldlineError


class CoreAbiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-core-abi-")
        library = Path(self.temporary.name) / "libworldline_core.so"
        shutil.copy2(Path(__file__).resolve().parents[1] / "lib/libworldline_core.so", library)
        self.core = Core(library)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_published_sha_vectors_and_domain_links(self) -> None:
        self.assertEqual(
            self.core.hash_bytes(b"").hex(),
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        )
        self.assertEqual(
            self.core.hash_bytes(b"abc").hex(),
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
        )
        path = Path(self.temporary.name) / "vector.bin"
        path.write_bytes(b"abc")
        self.assertEqual(self.core.hash_file(path), self.core.hash_bytes(b"abc"))
        hashes = {name: bytes([index]) * 32 for index, name in enumerate(
            ("parent", "filesystem", "config", "repository", "environment", "evidence")
        )}
        expected = hashlib.sha256(
            b"worldline-world-v1" + b"".join(hashes[name] for name in
                ("parent", "filesystem", "config", "repository", "environment", "evidence"))
        ).digest()
        self.assertEqual(self.core.world_id(hashes), expected)
        previous = bytes(32)
        event = bytes([1]) * 32
        self.assertEqual(
            self.core.causal_link(previous, event),
            hashlib.sha256(b"worldline-causal-v1" + previous + event).digest(),
        )
        self.assertEqual(
            self.core.receipt_link(previous, event),
            hashlib.sha256(b"worldline-receipt-v1" + previous + event).digest(),
        )

    def test_every_collapse_denial_and_transition_boundary(self) -> None:
        # ABI generation 6: every identity is typed and optional, and every measurement is
        # tri-state. One good commit-phase request, then each input moved on its own.
        def h(byte: int) -> bytes:
            return bytes([byte]) * 32

        request = CollapseInput(
            candidate_state="VALID", phase="COMMIT", mode="CANDIDATE_EVALUATION",
            conflicts="NONE_FOUND", foreign_writes="NONE_FOUND",
            roster_complete=True, staged_roster_complete=False,
            expected_parent=h(1), candidate_parent=h(1),
            expected_subject=h(2), evidence_subject=h(2),
            expected_base=h(3), candidate_base=h(3),
            expected_delta=h(4), candidate_delta=h(4),
            expected_root_set=h(5), candidate_root_set=h(5),
            expected_staged_root=h(6), actual_staged_root=h(6),
            staged_content_root=h(7), tested_root=h(7),
            current_requirement=h(8), resulting_requirement=h(8), evaluated_requirement=h(8),
            declared_verifiers=h(9), executed_verifiers=h(9),
            staged_evaluated_requirement=None, staged_executed_verifiers=None, staged_examined_root=None,
            expected_checkpoint=None, witnessed_checkpoint=None,
            registered_watch_set=h(10), watched_set=h(10),
            generation_before=41, generation_after=41,
        )
        self.assertEqual(self.core.collapse_decide(request), "AUTHORIZED")
        bad = h(0xEE)
        cases = (
            (replace(request, candidate_state="DEAD"), "INVALID_CANDIDATE"),
            (replace(request, candidate_parent=bad), "PARENT_MISMATCH"),
            (replace(request, evidence_subject=bad), "EVIDENCE_SUBJECT_MISMATCH"),
            (replace(request, candidate_base=bad), "BASE_MISMATCH"),
            (replace(request, candidate_delta=bad), "DELTA_MISMATCH"),
            (replace(request, candidate_root_set=bad), "ROOT_SET_MISMATCH"),
            (replace(request, actual_staged_root=bad), "STAGED_ROOT_MISMATCH"),
            (replace(request, evaluated_requirement=bad), "VALIDATION_CONTEXT_MISMATCH"),
            (replace(request, executed_verifiers=bad), "VERIFIER_EXECUTION_IDENTITY_MISMATCH"),
            (replace(request, roster_complete=False), "EXECUTION_EVIDENCE_INCOMPLETE"),
            (replace(request, staged_content_root=bad), "STAGED_UNTESTED"),
            (replace(request, conflicts="FOUND"), "CONFLICT"),
            (replace(request, foreign_writes="FOUND"), "FOREIGN_MANAGED_WRITE"),
            (replace(request, foreign_writes="UNMEASURED"), "MEASUREMENT_ABSENT"),
            (replace(request, conflicts="UNMEASURED"), "MEASUREMENT_ABSENT"),
            (replace(request, generation_after=None), "MEASUREMENT_ABSENT"),
            (replace(request, watched_set=None), "MEASUREMENT_ABSENT"),
            (replace(request, generation_after=42), "PRIME_CHANGED"),
            (replace(request, watched_set=bad), "WATCH_INCOMPLETE"),
            (replace(request, expected_parent=None), "IDENTITY_ABSENT"),
            (replace(request, expected_parent=None, candidate_parent=None), "IDENTITY_ABSENT"),
            (replace(request, evidence_subject=None), "IDENTITY_ABSENT"),
            (replace(request, actual_staged_root=None), "IDENTITY_ABSENT"),
            (replace(request, tested_root=None), "STAGED_UNTESTED"),
        )
        for supplied, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(self.core.collapse_decide(supplied), expected)
        # Prepare phase: no second capture yet, so the staged-root pair is not compared.
        self.assertEqual(self.core.collapse_decide(replace(request, phase="PREPARE", actual_staged_root=None)), "AUTHORIZED")
        # The staged evaluation covers the staged bytes only when it ran the current
        # requirement, with a complete roster, on exactly those bytes.
        staged = replace(request, tested_root=bad, staged_evaluated_requirement=h(8),
                         staged_roster_complete=True, staged_executed_verifiers=h(9), staged_examined_root=h(7))
        self.assertEqual(self.core.collapse_decide(staged), "AUTHORIZED")
        # The staged block never stands in for the candidate's own evidence.
        self.assertEqual(self.core.collapse_decide(replace(staged, roster_complete=False)), "EXECUTION_EVIDENCE_INCOMPLETE")
        self.assertEqual(self.core.collapse_decide(replace(staged, evaluated_requirement=bad)), "VALIDATION_CONTEXT_MISMATCH")
        for broken in (replace(staged, staged_roster_complete=False), replace(staged, staged_examined_root=bad),
                       replace(staged, staged_evaluated_requirement=bad), replace(staged, staged_executed_verifiers=None)):
            with self.subTest(staged=broken):
                self.assertEqual(self.core.collapse_decide(broken), "STAGED_UNTESTED")
        # Checkpoint return: the witness decides, never a candidate roster.
        checkpoint = replace(request, mode="CHECKPOINT_RETURN", roster_complete=False,
                             resulting_requirement=None,
                             evaluated_requirement=None, executed_verifiers=None,
                             expected_checkpoint=h(11), witnessed_checkpoint=h(11))
        self.assertEqual(self.core.collapse_decide(checkpoint), "AUTHORIZED")
        self.assertEqual(self.core.collapse_decide(replace(checkpoint, witnessed_checkpoint=None)), "CHECKPOINT_UNWITNESSED")
        self.assertEqual(self.core.collapse_decide(replace(checkpoint, witnessed_checkpoint=bad)), "CHECKPOINT_MISMATCH")
        # A witnessed checkpoint still needs evidence of exactly the bytes going live.
        self.assertEqual(self.core.collapse_decide(replace(checkpoint, tested_root=None)), "STAGED_UNTESTED")
        self.assertEqual(self.core.collapse_decide(replace(checkpoint, tested_root=bad)), "STAGED_UNTESTED")
        self.assertEqual(self.core.collapse_decide(replace(checkpoint, expected_checkpoint=None)), "IDENTITY_ABSENT")
        # OWNER_MISMATCH is retired: no request reaches it.
        self.assertNotIn("OWNER_MISMATCH", {self.core.collapse_decide(supplied) for supplied, _ in cases})
        # A zero digest is the old sentinel for "nothing"; the encoder refuses it.
        with self.assertRaises(WorldlineError) as zero:
            self.core.collapse_decide(replace(request, tested_root=bytes(32)))
        self.assertEqual(zero.exception.code, "INVALID_HASH")
        self.assertTrue(self.core.transition_allowed("MUTABLE", "FINALIZING"))
        self.assertTrue(self.core.transition_allowed("FINALIZING", "VALID"))
        self.assertFalse(self.core.transition_allowed("DEAD", "VALID"))
        self.assertFalse(self.core.transition_allowed("DEGRADED", "COLLAPSED"))

    def test_installed_layout_resolves_without_home_or_environment_override(self) -> None:
        # The installed tree keeps the library beside runtime/, the source tree keeps it in
        # lib/. Resolution must not depend on HOME, or any alternate-HOME invocation of the
        # installed daemon fails with CORE_UNAVAILABLE.
        source_library = Path(__file__).resolve().parents[1] / "lib/libworldline_core.so"
        source_package = Path(__file__).resolve().parents[1] / "runtime/worldline"
        for layout, relative in (("installed", "libworldline_core.so"), ("source", "lib/libworldline_core.so")):
            with self.subTest(layout=layout):
                root = Path(self.temporary.name) / layout
                root.mkdir(parents=True)
                # Copy, never symlink: Path(__file__).resolve() would escape the fake layout
                # and find the real source tree, hiding the very defect under test.
                shutil.copytree(source_package, root / "runtime/worldline")
                library = root / relative
                library.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_library, library)
                environment = {
                    "PATH": os.environ.get("PATH", "/usr/bin"),
                    "PYTHONPATH": str(root / "runtime"),
                    "PYTHONDONTWRITEBYTECODE": "1",
                    "HOME": str(Path(self.temporary.name) / "absent-home"),
                }
                completed = subprocess.run(
                    [
                        sys.executable,
                        "-c",
                        "from worldline.core import Core; print(Core.shared().hash_bytes(b'abc').hex())",
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                    env=environment,
                )
                self.assertEqual(completed.returncode, 0, completed.stderr)
                self.assertEqual(
                    completed.stdout.strip(),
                    "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
                )


    def test_checkpoint_resulting_slot_must_be_absent(self) -> None:
        def h(byte: int) -> bytes:
            return bytes([byte]) * 32

        request = CollapseInput(
            candidate_state="VALID", phase="COMMIT", mode="CANDIDATE_EVALUATION",
            conflicts="NONE_FOUND", foreign_writes="NONE_FOUND",
            roster_complete=True, staged_roster_complete=False,
            expected_parent=h(1), candidate_parent=h(1),
            expected_subject=h(2), evidence_subject=h(2),
            expected_base=h(3), candidate_base=h(3),
            expected_delta=h(4), candidate_delta=h(4),
            expected_root_set=h(5), candidate_root_set=h(5),
            expected_staged_root=h(6), actual_staged_root=h(6),
            staged_content_root=h(7), tested_root=h(7),
            current_requirement=h(8), resulting_requirement=h(8), evaluated_requirement=h(8),
            declared_verifiers=h(9), executed_verifiers=h(9),
            staged_evaluated_requirement=None, staged_executed_verifiers=None, staged_examined_root=None,
            expected_checkpoint=None, witnessed_checkpoint=None,
            registered_watch_set=h(10), watched_set=h(10),
            generation_before=41, generation_after=41,
        )
        checkpoint = replace(request, mode="CHECKPOINT_RETURN", roster_complete=False,
                             resulting_requirement=None, evaluated_requirement=None,
                             executed_verifiers=None, expected_checkpoint=h(11), witnessed_checkpoint=h(11))
        self.assertEqual(self.core.collapse_decide(checkpoint), "AUTHORIZED")
        self.assertEqual(self.core.collapse_decide(replace(checkpoint, resulting_requirement=h(8))),
                         "INVALID_REQUEST")

    def test_resulting_requirement_is_present_and_equal_in_each_phase(self) -> None:
        def h(byte: int) -> bytes:
            return bytes([byte]) * 32

        request = CollapseInput(
            candidate_state="VALID", phase="COMMIT", mode="CANDIDATE_EVALUATION",
            conflicts="NONE_FOUND", foreign_writes="NONE_FOUND",
            roster_complete=True, staged_roster_complete=False,
            expected_parent=h(1), candidate_parent=h(1),
            expected_subject=h(2), evidence_subject=h(2),
            expected_base=h(3), candidate_base=h(3),
            expected_delta=h(4), candidate_delta=h(4),
            expected_root_set=h(5), candidate_root_set=h(5),
            expected_staged_root=h(6), actual_staged_root=h(6),
            staged_content_root=h(7), tested_root=h(7),
            current_requirement=h(8), resulting_requirement=h(8), evaluated_requirement=h(8),
            declared_verifiers=h(9), executed_verifiers=h(9),
            staged_evaluated_requirement=None, staged_executed_verifiers=None, staged_examined_root=None,
            expected_checkpoint=None, witnessed_checkpoint=None,
            registered_watch_set=h(10), watched_set=h(10),
            generation_before=41, generation_after=41,
        )
        for phase in ("PREPARE", "COMMIT"):
            positive = replace(request, phase=phase,
                               actual_staged_root=None if phase == "PREPARE" else h(6))
            with self.subTest(phase=phase):
                self.assertEqual(self.core.collapse_decide(positive), "AUTHORIZED")
                self.assertEqual(self.core.collapse_decide(replace(positive, resulting_requirement=h(99))),
                                 "REQUIREMENT_CHANGED")
                self.assertEqual(self.core.collapse_decide(replace(positive, resulting_requirement=None)),
                                 "IDENTITY_ABSENT")
                self.assertEqual(self.core.collapse_decide(replace(positive, current_requirement=None,
                                                                   resulting_requirement=None)),
                                 "IDENTITY_ABSENT")
                with self.assertRaises(WorldlineError):
                    self.core.collapse_decide(replace(positive, resulting_requirement=b"short"))

    def test_staged_tree_policy_and_examiner_changes_reach_native_requirement_guard(self) -> None:
        import copy
        import json
        from types import SimpleNamespace
        from worldline.validation import requirements_for_tree
        def h(byte: int) -> bytes:
            return bytes([byte]) * 32

        request = CollapseInput(
            candidate_state="VALID", phase="COMMIT", mode="CANDIDATE_EVALUATION",
            conflicts="NONE_FOUND", foreign_writes="NONE_FOUND",
            roster_complete=True, staged_roster_complete=False,
            expected_parent=h(1), candidate_parent=h(1),
            expected_subject=h(2), evidence_subject=h(2),
            expected_base=h(3), candidate_base=h(3),
            expected_delta=h(4), candidate_delta=h(4),
            expected_root_set=h(5), candidate_root_set=h(5),
            expected_staged_root=h(6), actual_staged_root=h(6),
            staged_content_root=h(7), tested_root=h(7),
            current_requirement=h(8), resulting_requirement=h(8), evaluated_requirement=h(8),
            declared_verifiers=h(9), executed_verifiers=h(9),
            staged_evaluated_requirement=None, staged_executed_verifiers=None, staged_examined_root=None,
            expected_checkpoint=None, witnessed_checkpoint=None,
            registered_watch_set=h(10), watched_set=h(10),
            generation_before=41, generation_after=41,
        )
        root = {"root_key": "primary", "primary_root": True,
                "path": b"/original/root", "display_path": "/original/root"}
        roots = [root]
        store = SimpleNamespace(roots=lambda: roots)
        payload = Path(self.temporary.name) / "staged"
        source = payload / "primary"
        source.mkdir(parents=True)
        examiner = source / "evaluator" / "exam.py"
        examiner.parent.mkdir()
        examiner.write_text("raise SystemExit(0)\n", encoding="utf-8")
        policy = {"schemaVersion": 1, "generated": [], "services": [],
                  "protected": ["sentinel"], "checks": [{"id": "exam", "kind": "tests",
                  "argv": ["/usr/bin/python3", "evaluator/exam.py"], "required": True,
                  "format": "exit", "covers": ["candidate.txt"], "verifiers": ["evaluator/*"]}]}
        path = source / ".worldline.json"
        path.write_text(json.dumps(policy), encoding="utf-8")
        original = requirements_for_tree(store, None, payload, roots, self.core)
        identity = bytes.fromhex(original["requirementHash"].removeprefix("sha256:"))
        positive = replace(request, current_requirement=identity, evaluated_requirement=identity,
                           resulting_requirement=identity)
        self.assertEqual(self.core.collapse_decide(positive), "AUTHORIZED")
        for change in ("loosen-checks", "drop-protected", "rewrite-examiner"):
            with self.subTest(change=change):
                changed = copy.deepcopy(policy)
                examiner.write_text("raise SystemExit(0)\n", encoding="utf-8")
                if change == "loosen-checks":
                    changed["checks"] = []
                elif change == "drop-protected":
                    changed["protected"] = []
                else:
                    examiner.write_text("# rewritten judge\nraise SystemExit(0)\n", encoding="utf-8")
                path.write_text(json.dumps(changed), encoding="utf-8")
                (source / "candidate.txt").write_text("actual candidate work", encoding="utf-8")
                resulting = requirements_for_tree(store, None, payload, roots, self.core)
                self.assertNotEqual(resulting["requirementHash"], original["requirementHash"])
                result_id = bytes.fromhex(resulting["requirementHash"].removeprefix("sha256:"))
                for phase in ("PREPARE", "COMMIT"):
                    value = replace(positive, phase=phase, resulting_requirement=result_id,
                                    actual_staged_root=None if phase == "PREPARE" else h(6))
                    self.assertEqual(self.core.collapse_decide(value), "REQUIREMENT_CHANGED")
        with self.assertRaises(WorldlineError) as raised:
            requirements_for_tree(store, None, payload / "absent", roots, self.core)
        self.assertEqual(raised.exception.code, "STAGED_ROOT_ABSENT")

if __name__ == "__main__":
    unittest.main()
