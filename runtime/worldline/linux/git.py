from __future__ import annotations

import base64
import os
import re
from pathlib import Path
import subprocess
import shutil
import stat
import tempfile
from typing import Any, Mapping

from ..core import Core, hash_id
from ..errors import WorldlineError


# git's own words for a fork, allocation or descriptor it could not get (bash's for its scripts).
_RESOURCE_FAILURE = re.compile(r"cannot fork|fork: |Resource temporarily unavailable|Cannot allocate memory|"
                               r"Too many open files|out of memory", re.IGNORECASE)
# git's report that a process it started was killed: run-command's wait_or_whine prints exactly
# `error: <command> died of signal <n>` on a line of its own (C locale). Matched as a whole line:
# a warning that quotes a file named "died of signal 9.txt" set off an unanchored match (review of
# 8ff1903). The command may itself hold quotes: a filter's `%f` is quoted there (review of f50bbb1).
_CHILD_KILLED = re.compile(rb"^error: .* died of signal [0-9]+$", re.MULTILINE)


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

    # The `-c` list above is a denylist, and git has exec-capable settings no denylist can name:
    # a repository defines `filter.<any name>.clean` in its own config and applies it through
    # .gitattributes, so `status` and `diff` run it. Review of ff201cd demonstrated a world whose
    # repository did that and ran commands as the daemon account, outside any sandbox, able to
    # rewrite PRIME, the policy and the store with no transaction. Every git process therefore
    # runs in its own bubblewrap sandbox: no network, the system directories read-only, a fresh
    # /tmp, and nothing of the host besides the inspected root (read-only) and a private scratch
    # directory. Git behaves exactly as before, so the captured facts do not change; whatever
    # a hostile configuration makes it run can reach nothing.
    _SANDBOX_SYSTEM = ("/usr", "/bin", "/sbin", "/lib", "/lib64", "/etc")
    # Whatever a repository makes git run gets this many tasks beyond what the daemon's uid
    # already has (RLIMIT_NPROC counts threads per real uid, and the kernel applies it to the
    # namespace creation itself), no user namespace of its own to escape that count
    # (--disable-userns), a tmpfs of this size, and the 15 s timeout. Memory and a hard task
    # ceiling come from the daemon unit's cgroup (MemoryMax=, TasksMax=; the shipped unit sets both).
    _EXTRA_TASKS = 2048
    _TMPFS_BYTES = 256 * 1024 * 1024

    def __init__(self, core: Core | None = None, executable: str = "git") -> None:
        self.core = core or Core.shared()
        self.executable = executable

    @staticmethod
    def _uid_tasks(uid: int) -> int:
        """Threads of every process whose real uid is `uid`: what RLIMIT_NPROC is charged with."""
        tasks = 0
        for entry in os.scandir("/proc"):
            if not entry.name.isdigit():
                continue
            try:
                with open(f"/proc/{entry.name}/status", "rb") as stream:
                    status = stream.read(4096)
            except OSError:
                continue
            real_uid = threads = None
            for line in status.splitlines():
                if line.startswith(b"Uid:"):
                    real_uid = int(line.split()[1])
                elif line.startswith(b"Threads:"):
                    threads = int(line.split()[1])
            if real_uid == uid and threads:
                tasks += threads
        return tasks

    @classmethod
    def _task_limit(cls) -> int:
        return cls._uid_tasks(os.getuid()) + cls._EXTRA_TASKS

    @staticmethod
    def _require_top_level_repository(root: bytes) -> None:
        """Only a repository's own top-level directory, with its `.git` a real directory inside it.

        A linked worktree's `.git` is a file naming a directory elsewhere, and a subdirectory of a
        repository finds its `.git` above itself. Either way git would need host directories
        outside the inspected root, and those are named by the content being inspected, which a
        candidate controls: a `.git` file naming another world's or PRIME's repository once put
        that repository's committed content into a world's recorded facts (review of ad64cd2).
        Such roots are refused by name instead; register the main checkout, or the directory with
        --kind filesystem."""
        try:
            info = os.lstat(os.path.join(root, b".git"))
        except FileNotFoundError:
            raise WorldlineError(
                "NOT_A_GIT_ROOT",
                f"not the top of a Git repository (no .git directory): {os.fsdecode(root)}; register the "
                "repository's top-level directory, or this directory with --kind filesystem") from None
        if not stat.S_ISDIR(info.st_mode):
            raise WorldlineError(
                "GIT_LINKED_WORKTREE_UNSUPPORTED",
                f"{os.fsdecode(root)}/.git is not a directory (a linked worktree or a link); register the "
                "main checkout, or this directory with --kind filesystem")

    @classmethod
    def _sandbox(cls, root: bytes, scratch: str | None, task_limit: int, status_fd: int | None = None) -> list[str]:
        bwrap = shutil.which("bwrap")
        prlimit = shutil.which("prlimit")
        choom = shutil.which("choom")
        if bwrap is None or prlimit is None or choom is None:
            raise WorldlineError("BUBBLEWRAP_UNAVAILABLE", "bwrap, prlimit and choom are required to inspect a repository")
        # Inspection runs in the daemon's own cgroup, so the unit's limits bound it together with
        # the daemon; an OOM score of 1000 makes the kernel kill inspection first, not the daemon
        # (review of 796cb02). Raising one's own score needs no privilege.
        argv = [choom, "-n", "1000", "--", prlimit, f"--nproc={task_limit}:{task_limit}", "--",
                bwrap, "--unshare-all", "--unshare-user", "--disable-userns", "--cap-drop", "ALL",
                "--die-with-parent", "--new-session", "--clearenv"]
        if status_fd is not None:
            argv += ["--json-status-fd", str(status_fd)]
        for path in cls._SANDBOX_SYSTEM:
            if os.path.islink(path):
                argv += ["--symlink", os.readlink(path), path]
            elif os.path.isdir(path):
                argv += ["--ro-bind", path, path]
        argv += ["--dev", "/dev", "--proc", "/proc", "--size", str(cls._TMPFS_BYTES), "--tmpfs", "/tmp"]
        root_text = os.fsdecode(root)
        argv += ["--ro-bind", root_text, root_text]
        if scratch is not None:
            argv += ["--bind", scratch, scratch]
        return argv

    @staticmethod
    def _read_index(root: bytes) -> bytes | None:
        """The index at `<root>/.git/index`, read on the host through one descriptor that refuses
        links at every step, or None when there is none. The path is fixed here rather than taken
        from git's output about a repository the candidate controls, and the bytes that are hashed
        are the bytes that are copied, so nothing can be swapped between the two."""
        flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | getattr(os, "O_DIRECTORY", 0)
        try:
            directory = os.open(os.path.join(root, b".git"), flags)
        except OSError:
            return None
        try:
            try:
                descriptor = os.open(b"index", os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=directory)
            except OSError:
                return None
            try:
                if not stat.S_ISREG(os.fstat(descriptor).st_mode):
                    return None
                chunks = []
                while True:
                    chunk = os.read(descriptor, 1 << 20)
                    if not chunk:
                        break
                    chunks.append(chunk)
                return b"".join(chunks)
            finally:
                os.close(descriptor)
        finally:
            os.close(directory)

    def _run(
        self, root: bytes, *args: str, check: bool = True, extra_env: Mapping[str, str] | None = None,
        scratch: str | None = None, task_limit: int | None = None,
    ) -> subprocess.CompletedProcess[bytes]:
        executable = self._sandboxed_git()
        environment = {
            **(extra_env or {}),
            "PATH": "/usr/bin:/bin",
            "LC_ALL": "C",
            # Ignore ~/.gitconfig and /etc/gitconfig so only the (overridden) repo config is
            # consulted; block terminal/credential prompts and optional index-lock writers;
            # restrict any protocol handler to inert local files.
            "HOME": "/tmp",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_SYSTEM": os.devnull,
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_OPTIONAL_LOCKS": "0",
            "GIT_ALLOW_PROTOCOL": "file",
            "GIT_ATTR_NOSYSTEM": "1",
        }
        status_read, status_write = os.pipe()
        try:
            argv = self._sandbox(root, scratch, self._task_limit() if task_limit is None else task_limit, status_write)
            for key, value in sorted(environment.items()):
                argv += ["--setenv", key, value]
            argv += [executable, *self._HARDENING, "-C", os.fsdecode(root), *args]
            try:
                result = subprocess.run(
                    argv,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                    timeout=15,
                    env={"PATH": "/usr/bin:/bin"},
                    pass_fds=(status_write,),
                )
            except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
                raise WorldlineError("GIT_UNAVAILABLE", f"Git could not inspect {os.fsdecode(root)}", {"error": str(exc)}) from exc
            os.close(status_write)
            status_write = -1
            status = b""
            while chunk := os.read(status_read, 4096):
                status += chunk
        finally:
            for descriptor in (status_read, status_write):
                if descriptor >= 0:
                    os.close(descriptor)
        # bwrap reports the child's exit code only when the sandbox set up and ran it. Without that
        # report the sandbox did not start, and git's exit code must not be read as a repository
        # fact: a launch failure once recorded head=None for a repository that has a HEAD (review
        # of ad64cd2). With it, the code is git's, whatever git's stderr says: a repository's
        # filter can print anything there, and a `bwrap:` prefix once made it refuse its own
        # captures as a broken sandbox (review of 796cb02). The one exception is bwrap's own
        # report that exec failed, exit 1 and `bwrap: execvp`, which git never produces; git is
        # checked beforehand to lie inside what the sandbox binds, so that should not happen.
        exec_failed = result.returncode == 1 and result.stderr.startswith(b"bwrap: execvp ")
        # A negative code: the sandbox launcher itself was killed by a signal (review of 09f5c0b).
        if b'"exit-code"' not in status or exec_failed or result.returncode < 0:
            raise WorldlineError(
                "GIT_SANDBOX_UNAVAILABLE",
                f"the repository sandbox did not start for {os.fsdecode(root)}",
                {"stderr": result.stderr.decode("utf-8", "replace")[:2000]},
            )
        if result.returncode > 128:
            # Killed by a signal (the OOM killer, a task limit, a timeout), not a git answer: a
            # `check=False` read such as `rev-parse --verify HEAD` must not record it as "no HEAD"
            # (review of 4490013). git's own failures exit 128 or less.
            raise WorldlineError(
                "GIT_INSPECTION_FAILED",
                f"git was stopped by signal {result.returncode - 128} while inspecting {os.fsdecode(root)}",
                {"argv": list(args), "stderr": result.stderr.decode("utf-8", "replace")[:2000]},
            )
        killed = _CHILD_KILLED.search(result.stderr)
        if killed:
            # A process git started was killed (inspection runs at OOM score 1000). git says so and
            # exits 128, or exits 0 after trying another way, which changes what it prints:
            # `submodule status` retries `describe` with other options. Either would be recorded
            # as a fact about the repository (review of 300543c).
            raise WorldlineError(
                "GIT_INSPECTION_FAILED",
                f"a process git started was stopped by a signal while inspecting {os.fsdecode(root)} "
                f"({killed.group(0).decode('utf-8', 'replace')})",
                {"argv": list(args), "stderr": result.stderr.decode("utf-8", "replace")[:2000]},
            )
        if check and result.returncode != 0:
            raise WorldlineError(
                "GIT_INSPECTION_FAILED",
                f"Git inspection failed for {os.fsdecode(root)}",
                {"argv": list(args), "stderr": result.stderr.decode("utf-8", "replace")},
            )
        return result

    def _sandboxed_git(self) -> str:
        """git's absolute path, which must lie inside the system directories the sandbox binds
        (by its spelling and by its resolved path), or it could not run there."""
        found = shutil.which(self.executable, path="/usr/bin:/bin")
        if found is None:
            raise WorldlineError("GIT_UNAVAILABLE", f"{self.executable} is not in /usr/bin or /bin")
        bound = tuple(os.path.realpath(path) for path in self._SANDBOX_SYSTEM)
        real = os.path.realpath(found)
        if not any(real == base or real.startswith(base + os.sep) for base in bound):
            raise WorldlineError(
                "GIT_SANDBOX_UNAVAILABLE",
                f"git at {found} resolves to {real}, outside the directories the repository sandbox binds "
                f"({', '.join(self._SANDBOX_SYSTEM)})")
        return found

    def capture(self, root: str | bytes | os.PathLike[str] | os.PathLike[bytes]) -> dict[str, Any]:
        raw_root = os.path.abspath(os.fsencode(root))
        self._require_top_level_repository(raw_root)
        task_limit = self._task_limit()  # once per capture
        run = lambda *args, **kwargs: self._run(raw_root, *args, task_limit=task_limit, **kwargs)
        inside = run("rev-parse", "--is-inside-work-tree")
        if inside.stdout.strip() != b"true":
            raise WorldlineError("NOT_A_GIT_ROOT", f"registered repository is not a Git worktree: {os.fsdecode(raw_root)}")

        head_result = run("rev-parse", "--verify", "HEAD", check=False)
        head = head_result.stdout.strip().decode("ascii") if head_result.returncode == 0 else None
        branch_result = run("symbolic-ref", "--quiet", "--short", "HEAD", check=False)
        branch = branch_result.stdout.rstrip(b"\n").decode("utf-8", "replace") if branch_result.returncode == 0 else None
        index = self._read_index(raw_root)
        index_hash = hash_id(self.core.hash_bytes(index)) if index is not None else None

        # Inspection must not touch the repository. `git diff` refreshes the index and writes it
        # back whenever stat data looks racy, which a freshly materialized copy always does, and
        # GIT_OPTIONAL_LOCKS does not cover that write. It changed the staged tree between prepare
        # and commit, so every repository-root collapse was denied STAGED_ROOT_MISMATCH. Every
        # index-reading command below runs against a private copy of the index instead.
        with tempfile.TemporaryDirectory(prefix="worldline-git-") as scratch:
            private_index = os.path.join(scratch, "index")
            if index is not None:
                with open(private_index, "xb") as stream:
                    stream.write(index)
            private = {"GIT_INDEX_FILE": private_index}
            status = run("status", "--porcelain=v2", "--branch", "-z", extra_env=private, scratch=scratch).stdout
            staged = run("diff", "--cached", "--binary", "--no-ext-diff", "--no-textconv", extra_env=private, scratch=scratch).stdout
            worktree = run("diff", "--binary", "--no-ext-diff", "--no-textconv", extra_env=private, scratch=scratch).stdout
            submodules = run("submodule", "status", "--recursive", check=False, extra_env=private, scratch=scratch)
        listing: dict[str, Any] | None = None
        if submodules.returncode != 0:
            refusal = submodules.stderr.decode("utf-8", "replace")
            if _RESOURCE_FAILURE.search(refusal):
                # A fork or allocation refused inside the sandbox is not a fact about the
                # repository: recorded as "no submodules" before (review of 09f5c0b).
                raise WorldlineError(
                    "GIT_INSPECTION_FAILED",
                    f"git could not list the submodules of {os.fsdecode(raw_root)} for want of resources",
                    {"stderr": refusal[:2000]})
            # git's own refusal of the listing (a gitlink with no .gitmodules mapping, which
            # `git add -A` over a nested checkout makes) is a fact about the repository: recorded
            # as unreadable, not as "no submodules", and not refused, since the repository is
            # otherwise ordinary (review of c7d89f1).
            listing = {"state": "UNREADABLE", "reason": (refusal.strip().splitlines() or [""])[0][:200]}
        submodule_bytes = submodules.stdout if submodules.returncode == 0 else b""

        facts = {
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
        if listing is not None:
            facts["submoduleListing"] = listing
        return facts

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
        version = result.stdout.decode("utf-8", "replace").strip()
        # Repository inspection needs its sandbox, not only git: probe the exact sandbox.
        try:
            with tempfile.TemporaryDirectory(prefix="worldline-git-probe-") as probe_root:
                subprocess.run(["git", "init", "-q", probe_root], capture_output=True, check=True, timeout=15,
                               env={"PATH": "/usr/bin:/bin", "HOME": probe_root,
                                    "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull})
                cls(core=_ProbeCore())._run(os.fsencode(probe_root), "rev-parse", "--is-inside-work-tree")
        except WorldlineError as exc:
            return {"state": "UNAVAILABLE", "version": version,
                    "reason": f"repository sandbox unavailable: {exc.code}: {exc.message}",
                    "details": exc.details}
        except (OSError, subprocess.SubprocessError) as exc:
            return {"state": "UNAVAILABLE", "version": version, "reason": f"repository sandbox probe failed: {exc}"}
        return {"state": "AVAILABLE", "version": version, "sandbox": "AVAILABLE"}


class _ProbeCore:
    """The capability probe runs git only; it never hashes."""
