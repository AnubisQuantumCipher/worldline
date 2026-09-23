"""The identity of the verifier bytes a check actually executed.

1.3.x binds `verifier at base == expected` and `verifier at finalization == expected`. Neither
establishes `verifier actually executed == expected`, and the difference is a whole attack:

    expected verifier -> temporarily replace -> execute replacement -> restore -> finalize

Both ends look perfect while the thing that produced PASS was different. Worse, until this module
a check executed its verifier **from inside the world's writable overlay** — the file the check
ran was a file the candidate owned.

Hashing a path and then executing that path narrows the window; it does not close it. So the
object whose identity is established here is the object execution consumes:

1. the declared verifier set is copied out of the overlays into a staging directory the candidate
   has no path to, owned by the daemon and mode 0500;
2. each staged file is opened, and its identity is computed by reading **through that descriptor**
   rather than through its name;
3. the staging directory is bind-mounted **read-only** into the sandbox, and the check's argv is
   rewritten to run from there — so a candidate that swaps the original swaps something the check
   does not execute;
4. after execution every identity is recomputed through the *same descriptors*, which are held
   open throughout, **and** the staged pathname is re-stated to prove it still resolves to the
   inode those descriptors hold.

Step 4 needs both halves, and this is worth spelling out because the first half alone looks like
enough and is not. A held descriptor keeps referring to its original open file description even
after the pathname is removed or re-pointed — which means an unchanged descriptor hash is
perfectly compatible with the interpreter having opened a *different* file through the same name.
Descriptor stability proves the bytes we measured did not change. It does not prove they are the
bytes that ran. Only comparing the name's (device, inode) against the descriptor's closes that,
and a rebound pathname is refused rather than reported.

What this establishes, stated exactly: **this declared verifier bundle was made available for
execution under these identities, from a location the workload cannot write, and the pathnames
the interpreter was given still resolved to those exact objects afterwards.**

What it does NOT establish, equally exactly:

* that every file in the bundle was read — staging ten files identifies ten files, it does not
  trace which the interpreter opened;
* that every input influencing the execution was captured — an interpreter reads more than a
  policy declares;
* anything about an adversary with host-side write access to the daemon's own staging directory.
  That is outside the threat model this module addresses, which is a workload inside a WORLDLINE
  sandbox. A privileged test harness altering a host file is not a sandbox escape, and this
  module does not pretend otherwise.
"""
from __future__ import annotations

import ast
import hashlib
import os
import posixpath
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from .errors import WorldlineError
from .resolution import resolve_token, root_prefixes

VERIFIER_MOUNT = "/run/worldline-verifiers"
MISMATCH = "VERIFIER_EXECUTION_IDENTITY_MISMATCH"
UNIDENTIFIED = "VERIFIER_EXECUTION_UNIDENTIFIED"




def bundle_identity(members: Sequence[tuple[str, str, str]]) -> str:
    """One digest over (root, path, content) triples, in order.

    Deliberately a free function. The expected side is built from the policy's resolved verifier
    list and the actual side from the runner's execution records — two different producers that
    must agree. If one function computed both, the equality the kernel proves would be an
    equality of a value with itself, which assures nothing.
    """
    digest = hashlib.sha256()
    digest.update(b"worldline-execution-verifier-set-v1\0")
    for root_key, relative, content in sorted(members):
        digest.update(root_key.encode()); digest.update(b"\0")
        digest.update(relative.encode()); digest.update(b"\0")
        # A member's content may be a bare file digest or another bundle identity; both are
        # sha256, and an empty one is 32 zero bytes rather than an absent member, so "nothing
        # measured" never collides with "measured as empty".
        raw = content.removeprefix("sha256:") if content else ""
        digest.update(bytes.fromhex(raw) if raw else b"\0" * 32); digest.update(b"\0")
    # Prefixed, like every other identity in this system, so it can be handed to the kernel
    # boundary without an ad-hoc conversion at the call site.
    return "sha256:" + digest.hexdigest()


#: The identity of an empty bundle. Used on BOTH sides for a check that declares no verifiers and
#: for a promotion with no candidate evaluation, so "nothing to bind" is symmetric rather than a
#: special case that could drift apart.
NO_BUNDLE_IDENTITY = bundle_identity([])


def _digest_fd(fd: int) -> tuple[str, int]:
    """Hash by descriptor, never by name. The point of the whole module is in this function."""
    os.lseek(fd, 0, os.SEEK_SET)
    digest = hashlib.sha256()
    size = 0
    while True:
        block = os.read(fd, 1 << 20)
        if not block:
            break
        size += len(block)
        digest.update(block)
    return digest.hexdigest(), size



def _remove_staging(path: Path) -> None:
    """Remove a previous staging directory, including one this module locked down.

    Staging ends at mode 0500 -- readable and traversable, not writable -- so nothing writes
    there again. A plain `rmtree` cannot delete entries inside such a directory, which made the
    reuse branch below raise PermissionError instead of doing the one job it exists for. Today
    every (world instance, check) pair gets a fresh path so the branch is not reached, but a
    recovery path that cannot recover is not a recovery path.
    """
    if not path.exists():
        return
    for directory in (p for p in [path, *path.rglob("*")] if p.is_dir()):
        try:
            os.chmod(directory, 0o700)
        except OSError:
            pass
    shutil.rmtree(path)


@dataclass(slots=True)
class StagedVerifier:
    root_key: str
    relative: str            # path inside its root, as the policy names it
    staged: str              # path inside the sandbox
    source: str              # how the policy bound it: argv or declared or directory
    fd: int                  # held open for the whole evaluation
    sha256: str
    bytes: int
    # The object the name resolved to at capture. Compared afterwards against the name, because
    # a descriptor that still holds the right bytes says nothing about what the name now points
    # at — and the name is what the interpreter was given.
    device: int
    inode: int
    host_path: str

    def as_dict(self) -> dict[str, Any]:
        return {"rootKey": self.root_key, "path": self.relative, "executedAs": self.staged,
                "source": self.source, "sha256": self.sha256, "bytes": self.bytes,
                "device": self.device, "inode": self.inode}


@dataclass(slots=True)
class ArgvPlan:
    """The resolved execution plan for one check's argv.

    argv            the rewritten command: verifier tokens point at the staged copies.
    rewrites        one entry per token bound to a staged member.
    escapes         tokens that address a managed root but bind to no clean member.
    unbound_members clean in-root paths that resolved to no staged member (covers operands,
                    symlinks, non-regular files) -- the runner decides which are data.
    """
    argv: list[str]
    rewrites: list[dict[str, str]]
    escapes: list[str]
    unbound_members: list[dict[str, str]]


class ExecutionVerifierSet:
    """The declared verifier artifacts for one check, staged and held open.

    Use as a context manager: the descriptors are what make the post-execution comparison mean
    anything, so they are closed exactly once, at the end of the evaluation.
    """

    def __init__(self, check_id: str, staging: Path) -> None:
        self.check_id = check_id
        self.staging = staging
        self.items: list[StagedVerifier] = []
        self._closed = False

    # -- construction ---------------------------------------------------------------------------
    @classmethod
    def stage(cls, *, check_id: str, entries: Sequence[Mapping[str, Any]],
              sources: Mapping[str, Path], staging: Path) -> "ExecutionVerifierSet":
        """Copy the declared set out of the overlays and identify it by descriptor."""
        staged = cls(check_id, staging)
        try:
            _remove_staging(staging)
            staging.mkdir(parents=True)
            os.chmod(staging, 0o700)
            for entry in sorted(entries, key=lambda item: (item["rootKey"], item["path"])):
                root_key, relative = str(entry["rootKey"]), str(entry["path"])
                base = sources.get(root_key)
                if base is None:
                    raise WorldlineError(UNIDENTIFIED,
                                         f"check {check_id} names a verifier in an unknown root: {root_key}")
                source = base / relative
                if source.is_symlink() or not source.is_file():
                    # A symlink is a name, and a name is exactly what this module refuses to
                    # trust. A verifier that is not a regular file cannot be identified.
                    raise WorldlineError(UNIDENTIFIED,
                                         f"check {check_id}: {relative} in {root_key[:12]} is not a regular file")
                target = staging / root_key / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
                os.chmod(target, 0o444)
                handle = os.open(target, os.O_RDONLY | os.O_CLOEXEC)
                digest, size = _digest_fd(handle)
                stat = os.fstat(handle)
                staged.items.append(StagedVerifier(
                    root_key=root_key, relative=relative,
                    staged=f"{VERIFIER_MOUNT}/{root_key}/{relative}",
                    source=str(entry.get("source", "unknown")),
                    fd=handle, sha256=digest, bytes=size,
                    device=stat.st_dev, inode=stat.st_ino, host_path=str(target)))
            # Read-only for the owner too: the daemon has no reason to write here again, and a
            # directory nobody may write is one fewer thing to reason about.
            for directory in sorted((p for p in staging.rglob("*") if p.is_dir()), reverse=True):
                os.chmod(directory, 0o500)
            os.chmod(staging, 0o500)
        except BaseException:
            staged.close()
            raise
        return staged

    # -- identity ---------------------------------------------------------------------------------
    def identity(self) -> str:
        """One digest over the whole set: every member's root, path and content, in order.

        A set identity rather than a file identity, because a verifier is rarely one file and a
        helper swapped beside the entry point must change the answer.
        """
        return bundle_identity([(i.root_key, i.relative, i.sha256) for i in self.items])

    def reread(self) -> tuple[str, list[dict[str, Any]]]:
        """Recompute every identity through the same descriptors, AND re-state every pathname.

        Two questions, and the second is the one that is easy to forget. The descriptors answer
        "did the bytes we measured change?". The pathnames answer "does the name the interpreter
        was given still resolve to the object we measured?". A held descriptor survives its name
        being re-pointed, so without the second question an unchanged hash is compatible with a
        substituted examiner having run.
        """
        changes: list[dict[str, Any]] = []
        members: list[tuple[str, str, str]] = []
        for item in sorted(self.items, key=lambda i: (i.root_key, i.relative)):
            try:
                now, size = _digest_fd(item.fd)
            except OSError as exc:
                changes.append({"path": item.relative, "rootKey": item.root_key,
                                "before": item.sha256, "after": None, "error": str(exc)})
                now = ""
            if now != item.sha256:
                changes.append({"path": item.relative, "rootKey": item.root_key, "kind": "content",
                                "before": item.sha256, "after": now or None})
            # The name, not the descriptor. A rebound pathname means the interpreter may have
            # opened something else entirely, and an unchanged descriptor would never show it.
            try:
                named = os.stat(item.host_path)
                if (named.st_dev, named.st_ino) != (item.device, item.inode):
                    changes.append({"path": item.relative, "rootKey": item.root_key,
                                    "kind": "pathname-rebound",
                                    "before": f"{item.device}:{item.inode}",
                                    "after": f"{named.st_dev}:{named.st_ino}"})
            except OSError as exc:
                changes.append({"path": item.relative, "rootKey": item.root_key,
                                "kind": "pathname-gone", "before": f"{item.device}:{item.inode}",
                                "after": None, "error": str(exc)})
            members.append((item.root_key, item.relative, now))
        return bundle_identity(members), changes

    def rewrite_argv(self, argv: Sequence[str], roots: Mapping[str, str], *,
                     primary_root_key: str | None = None,
                     cwd: str = "") -> "ArgvPlan":
        """Resolve every argv token to its role and point verifier tokens at the staged copies.

        Resolution is the ONE rule in runtime/worldline/resolution.py, shared with
        `resolve_verifiers` -- two resolvers disagreeing is the same defect as two checks
        disagreeing. The earlier version had its own copy that normalised where the membership
        side did not, and a campaign walked through the seam (`/root/./gate.py`,
        `/root//gate.py`, `/root/../root/x`): the forged overlay examiner ran while the evidence
        recorded PRIME's bundle identity as BOUND.

        The returned plan names, per token, whether it is a staged verifier (rewritten), a token
        that addresses a managed root but binds to no staged member (`escapes`), or a token
        outside every root -- the interpreter, a flag, candidate-data operands. The check runner
        refuses on `escapes` and on any in-root member that was not rewritten, instead of the old
        "at least one token rewrote" test that a single unrelated operand satisfied.
        """
        by_member: dict[tuple[str, str], StagedVerifier] = {
            (item.root_key, item.relative): item for item in self.items}
        prefixes = root_prefixes(roots)

        out: list[str] = []
        rewrites: list[dict[str, str]] = []
        escapes: list[str] = []
        unbound_members: list[dict[str, str]] = []
        for token in argv:
            kind, root_key, relative = resolve_token(
                token, prefixes, primary_root_key=primary_root_key, cwd=cwd)
            if kind == "escape":
                # Addresses a root but resolves to no clean member: absolute remainder, a `..`
                # climbing out, or the root itself. Never executed as a verifier and never
                # silently passed through as candidate bytes.
                escapes.append(token)
                out.append(token)
                continue
            if kind == "member":
                item = by_member.get((root_key, relative))
                if item is not None:
                    out.append(item.staged)
                    rewrites.append({"from": token, "to": item.staged, "sha256": item.sha256})
                    continue
                # A clean in-root path that is not in the staged set. It named a file the
                # verifier resolution did not bind (a symlink, a covers-operand, or a
                # non-regular file). Recorded so the runner can tell a data operand apart from
                # an unbindable examiner.
                unbound_members.append({"token": token, "rootKey": root_key or "", "path": relative or ""})
            out.append(token)
        return ArgvPlan(argv=out, rewrites=rewrites, escapes=escapes, unbound_members=unbound_members)


    # -- is the staged bundle self-sufficient? ----------------------------------------------------

    def unsatisfied_imports(self) -> list[dict[str, Any]]:
        """Module-level imports of staged Python verifiers that the staged bundle cannot satisfy.

        This exists to keep two very different things from telling the operator the same story:

            the candidate failed a valid examination
            the examination could not complete because its trusted dependencies were incomplete

        Both block promotion. Only one of them is about the candidate.

        The check runs over the STAGED bytes -- trusted content, copied from PRIME, identified by
        the descriptors held open here -- and it runs BEFORE anything executes. It is therefore a
        supervisor-owned fact, not an inference from what the examination printed. That matters:
        an examiner's stderr passes through processes the candidate can reach, so a traceback is
        not evidence of anything.

        Deliberately conservative, because a false positive would blame the evaluator for a
        candidate's genuine failure:

        - only imports at the top level of the module body, so anything guarded by `try` or
          deferred into a function is left alone;
        - only absolute imports, since a relative one is a statement about package structure
          rather than about a missing file;
        - satisfied by the standard library, or by a sibling `X.py` or `X/__init__.py` staged in
          the same directory as the importing verifier -- which is where an examiner that adds
          its own directory to `sys.path` will look.

        It is not a complete dependency analysis and does not claim to be. A bundle it passes can
        still fail on a dynamic import; that is a missing detection, never a false accusation.
        """
        staged_paths = {(item.root_key, item.relative) for item in self.items}
        gaps: list[dict[str, Any]] = []
        for item in sorted(self.items, key=lambda i: (i.root_key, i.relative)):
            if not item.relative.endswith(".py"):
                continue
            try:
                tree = ast.parse(os.pread(item.fd, item.bytes, 0).decode("utf-8"))
            except (OSError, SyntaxError, UnicodeDecodeError):
                # A verifier this module cannot read or parse is not a verifier this module will
                # make claims about. Silence here is the honest answer.
                continue
            directory = posixpath.dirname(item.relative)
            for node in tree.body:
                if isinstance(node, ast.Import):
                    roots = [alias.name.split(".")[0] for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    roots = [node.module.split(".")[0]]
                else:
                    continue
                for root in roots:
                    if root in sys.stdlib_module_names:
                        continue
                    candidates = {posixpath.normpath(posixpath.join(directory, f"{root}.py")),
                                  posixpath.normpath(posixpath.join(directory, root, "__init__.py"))}
                    if any((item.root_key, c) in staged_paths for c in candidates):
                        continue
                    gap = {"verifier": item.relative, "rootKey": item.root_key, "module": root}
                    if gap not in gaps:
                        gaps.append(gap)
        return gaps

    def as_evidence(self) -> dict[str, Any]:
        gaps = self.unsatisfied_imports()
        return {
            "mount": VERIFIER_MOUNT,
            "identity": self.identity(),
            "members": [item.as_dict() for item in self.items],
            # Established over trusted bytes before execution. A check that fails with a gap
            # recorded here did not necessarily fail on its merits.
            "unsatisfiedImports": gaps,
            "nonClaims": [
                "This identifies the declared verifier BUNDLE that was made available for"
                " execution. It does not trace which of its files the interpreter actually read:"
                " staging ten files identifies ten files.",
                "An interpreter reads more than a policy declares, so this is not a complete"
                " account of everything that influenced the result.",
                "Descriptor stability alone would not establish execution identity — a held"
                " descriptor survives its pathname being re-pointed. The pathname is re-stated"
                " against the descriptor's (device, inode) for exactly that reason.",
                "This addresses a workload inside a WORLDLINE sandbox. It says nothing about an"
                " adversary with host-side write access to the daemon's staging directory.",
                "unsatisfiedImports reports module-level, absolute imports only. An empty list"
                " does not establish that the bundle is complete — a dynamic or guarded import"
                " can still fail at runtime. It is built to avoid blaming the evaluator for a"
                " candidate's genuine failure, so it misses rather than over-reports.",
            ],
        }

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        for item in self.items:
            try:
                os.close(item.fd)
            except OSError:
                pass

    def __enter__(self) -> "ExecutionVerifierSet":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()
