from __future__ import annotations

import base64
import os
from pathlib import Path
import subprocess
import shutil
import tempfile
from typing import Any, Mapping

from ..core import Core, hash_id
from ..errors import WorldlineError


class GitAdapter:
    # A registered root is untrusted repo content, and `git` executes commands named in the
    # repo's own `.git/config` during ordinary inspection: `core.fsmonitor` fires on `status`,
    # hooks fire on index-refreshing operations, and `diff.external`/textconv drivers fire on
    # `diff`. These inspections run host-side (outside the world sandbox) and, for `root add` /
    # `init`, BEFORE the operator confirms, so a hostile repo would get code execution as the
    # operator. Command-line `-c` has the highest config precedence and overrides the repo's
    # values, so every exec-capable knob is neutralized here. (`capture` also passes
    # `--no-ext-diff`, which already blocks `diff.external`; this is defense in depth plus
    # coverage for fsmonitor/hooks/credential-helper/pager vectors that `--no-ext-diff` misses.)
    _HARDENING = (
        "-c", "core.fsmonitor=",
        "-c", "core.hooksPath=/dev/null",
        "-c", "diff.external=",
        "-c", "core.sshCommand=",
        "-c", "core.pager=cat",
        "-c", "core.editor=false",
        "-c", "core.askPass=",
        "-c", "credential.helper=",
        "-c", "uploadpack.packObjectsHook=",
        "-c", "protocol.ext.allow=never",
        "-c", "protocol.file.allow=user",
    )

    def __init__(self, core: Core | None = None, executable: str = "git") -> None:
        self.core = core or Core.shared()
        self.executable = executable

    def _run(
        self, root: bytes, *args: str, check: bool = True, extra_env: Mapping[str, str] | None = None
    ) -> subprocess.CompletedProcess[bytes]:
        try:
            result = subprocess.run(
                [self.executable, *self._HARDENING, "-C", os.fsdecode(root), *args],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=15,
                env={
                    **(extra_env or {}),
                    "PATH": os.environ.get("PATH", ""),
                    "LC_ALL": "C",
                    # Ignore ~/.gitconfig and /etc/gitconfig so only the (overridden) repo
                    # config is consulted; block terminal/credential prompts and optional
                    # index-lock writers; restrict any protocol handler to inert local files.
                    "HOME": os.environ.get("HOME", ""),
                    "GIT_CONFIG_GLOBAL": os.devnull,
                    "GIT_CONFIG_SYSTEM": os.devnull,
                    "GIT_TERMINAL_PROMPT": "0",
                    "GIT_OPTIONAL_LOCKS": "0",
                    "GIT_ALLOW_PROTOCOL": "file",
                    "GIT_ATTR_NOSYSTEM": "1",
                },
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

        # Inspection must not touch the repository. `git diff` refreshes the index and writes it
        # back whenever stat data looks racy, which a freshly materialized copy always does, and
        # GIT_OPTIONAL_LOCKS does not cover that write. It changed the staged tree between prepare
        # and commit, so every repository-root collapse was denied STAGED_ROOT_MISMATCH. Every
        # index-reading command below runs against a private copy of the index instead.
        with tempfile.TemporaryDirectory(prefix="worldline-git-") as scratch:
            private_index = os.path.join(scratch, "index")
            if os.path.isfile(index_path):
                shutil.copyfile(index_path, private_index)
            private = {"GIT_INDEX_FILE": private_index}
            status = self._run(raw_root, "status", "--porcelain=v2", "--branch", "-z", extra_env=private).stdout
            staged = self._run(raw_root, "diff", "--cached", "--binary", "--no-ext-diff", "--no-textconv", extra_env=private).stdout
            worktree = self._run(raw_root, "diff", "--binary", "--no-ext-diff", "--no-textconv", extra_env=private).stdout
            submodules = self._run(raw_root, "submodule", "status", "--recursive", check=False, extra_env=private)
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
