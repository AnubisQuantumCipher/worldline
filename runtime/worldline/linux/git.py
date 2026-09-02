from __future__ import annotations

import base64
import os
from pathlib import Path
import subprocess
import shutil
from typing import Any

from ..core import Core, hash_id
from ..errors import WorldlineError


class GitAdapter:
    def __init__(self, core: Core | None = None, executable: str = "git") -> None:
        self.core = core or Core.shared()
        self.executable = executable

    def _run(self, root: bytes, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
        try:
            result = subprocess.run(
                [self.executable, "-C", os.fsdecode(root), *args],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=15,
                env={"PATH": os.environ.get("PATH", ""), "LC_ALL": "C", "HOME": os.environ.get("HOME", "")},
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            raise WorldlineError("GIT_UNAVAILABLE", f"Git could not inspect {os.fsdecode(root)}", {"error": str(exc)}) from exc
        if check and result.returncode != 0:
            raise WorldlineError(
                "GIT_INSPECTION_FAILED",
                f"Git inspection failed for {os.fsdecode(root)}",
                {"argv": list(args), "stderr": result.stderr.decode("utf-8", "replace")},
            )
        return result

    def capture(self, root: str | bytes | os.PathLike[str] | os.PathLike[bytes]) -> dict[str, Any]:
        raw_root = os.path.abspath(os.fsencode(root))
        inside = self._run(raw_root, "rev-parse", "--is-inside-work-tree")
        if inside.stdout.strip() != b"true":
            raise WorldlineError("NOT_A_GIT_ROOT", f"registered repository is not a Git worktree: {os.fsdecode(raw_root)}")

        head_result = self._run(raw_root, "rev-parse", "--verify", "HEAD", check=False)
        head = head_result.stdout.strip().decode("ascii") if head_result.returncode == 0 else None
        branch_result = self._run(raw_root, "symbolic-ref", "--quiet", "--short", "HEAD", check=False)
        branch = branch_result.stdout.rstrip(b"\n").decode("utf-8", "replace") if branch_result.returncode == 0 else None
        index_result = self._run(raw_root, "rev-parse", "--git-path", "index")
        index_name = index_result.stdout.rstrip(b"\n")
        index_path = index_name if os.path.isabs(index_name) else os.path.join(raw_root, index_name)
        index_hash = hash_id(self.core.hash_file(index_path)) if os.path.isfile(index_path) else None

        status = self._run(raw_root, "status", "--porcelain=v2", "--branch", "-z").stdout
        staged = self._run(raw_root, "diff", "--cached", "--binary", "--no-ext-diff").stdout
        worktree = self._run(raw_root, "diff", "--binary", "--no-ext-diff").stdout
        submodules = self._run(raw_root, "submodule", "status", "--recursive", check=False)
        submodule_bytes = submodules.stdout if submodules.returncode == 0 else b""

        return {
            "state": "CAPTURED",
            "head": head,
            "branch": branch,
            "indexHash": index_hash,
            "statusHash": hash_id(self.core.hash_bytes(status)),
            "statusRawB64": base64.b64encode(status).decode("ascii"),
            "stagedDiffHash": hash_id(self.core.hash_bytes(staged)),
            "stagedDiffRawB64": base64.b64encode(staged).decode("ascii"),
            "worktreeDiffHash": hash_id(self.core.hash_bytes(worktree)),
            "worktreeDiffRawB64": base64.b64encode(worktree).decode("ascii"),
            "submoduleHash": hash_id(self.core.hash_bytes(submodule_bytes)),
            "submoduleRawB64": base64.b64encode(submodule_bytes).decode("ascii"),
        }

    @classmethod
    def capability(cls) -> dict[str, Any]:
        executable = shutil.which("git")
        if executable is None:
            return {"state": "UNAVAILABLE", "reason": "git is not installed"}
        result = subprocess.run(
            [executable, "--version"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=5,
        )
        if result.returncode != 0:
            return {"state": "UNAVAILABLE", "reason": result.stderr.decode("utf-8", "replace").strip()}
        return {"state": "AVAILABLE", "version": result.stdout.decode("utf-8", "replace").strip()}
