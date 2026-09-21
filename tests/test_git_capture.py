from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import unittest

from worldline.linux.git import GitAdapter


def _git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.email=t@example.invalid", "-c", "user.name=t", "-C", str(root), *args],
        check=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
    )


def _tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.is_file():
            digest.update(str(path.relative_to(root)).encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


class GitCaptureIsReadOnly(unittest.TestCase):
    """Capturing a repository must not change it. A materialized copy has fresh stat data, which
    makes `git diff` rewrite the index; that rewrite changed the staged tree between prepare and
    commit and denied every repository-root collapse (STAGED_ROOT_MISMATCH)."""

    def test_capture_leaves_a_fresh_copy_byte_identical_and_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory(prefix="worldline-git-capture-") as temporary:
            source = Path(temporary) / "source"
            source.mkdir()
            _git(source, "init", "-q", "-b", "main")
            (source / "a.txt").write_text("x\n", encoding="utf-8")
            _git(source, "add", "a.txt")
            _git(source, "commit", "-q", "-m", "one")
            copy = Path(temporary) / "copy"
            shutil.copytree(source, copy, symlinks=True)
            time.sleep(1.1)  # cross a whole-second boundary so index stat data is racy
            os.utime(copy / "a.txt", None)
            before = _tree_digest(copy)
            index_before = (copy / ".git/index").read_bytes()
            adapter = GitAdapter()
            first = adapter.capture(copy)
            self.assertEqual((copy / ".git/index").read_bytes(), index_before)
            self.assertEqual(_tree_digest(copy), before)
            second = adapter.capture(copy)
            self.assertEqual(first, second)
            self.assertEqual(first["state"], "CAPTURED")
            self.assertEqual(first["branch"], "main")
            self.assertIsNotNone(first["head"])


if __name__ == "__main__":
    unittest.main()
