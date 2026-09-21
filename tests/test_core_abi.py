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
        good = bytes([1]) * 32
        bad = bytes([2]) * 32
        request = CollapseInput(
            candidate_state="VALID",
            has_conflicts=False,
            has_foreign_managed_writes=False,
            expected_parent=good,
            candidate_parent=good,
            expected_owner=good,
            candidate_owner=good,
            expected_base=good,
            candidate_base=good,
            expected_delta=good,
            candidate_delta=good,
            expected_root_set=good,
            candidate_root_set=good,
            expected_staged_root=good,
            actual_staged_root=good,
        )
        self.assertEqual(self.core.collapse_decide(request), "AUTHORIZED")
        cases = (
            (replace(request, candidate_state="DEAD"), "INVALID_CANDIDATE"),
            (replace(request, candidate_parent=bad), "PARENT_MISMATCH"),
            (replace(request, candidate_owner=bad), "OWNER_MISMATCH"),
            (replace(request, candidate_base=bad), "BASE_MISMATCH"),
            (replace(request, candidate_delta=bad), "DELTA_MISMATCH"),
            (replace(request, candidate_root_set=bad), "ROOT_SET_MISMATCH"),
            (replace(request, actual_staged_root=bad), "STAGED_ROOT_MISMATCH"),
            (replace(request, candidate_validation_context=bad), "VALIDATION_CONTEXT_MISMATCH"),
            (replace(request, staged_content_root=bad), "STAGED_UNTESTED"),
            (replace(request, has_conflicts=True), "CONFLICT"),
            (replace(request, has_foreign_managed_writes=True), "FOREIGN_MANAGED_WRITE"),
        )
        for supplied, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(self.core.collapse_decide(supplied), expected)
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


if __name__ == "__main__":
    unittest.main()
