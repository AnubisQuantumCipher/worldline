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

import hashlib
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from .errors import WorldlineError

VERIFIER_MOUNT = "/run/worldline-verifiers"
MISMATCH = "VERIFIER_EXECUTION_IDENTITY_MISMATCH"
UNIDENTIFIED = "VERIFIER_EXECUTION_UNIDENTIFIED"


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
            if staging.exists():
                shutil.rmtree(staging)
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
        digest = hashlib.sha256()
        digest.update(b"worldline-execution-verifier-set-v1\0")
        for item in sorted(self.items, key=lambda i: (i.root_key, i.relative)):
            digest.update(item.root_key.encode()); digest.update(b"\0")
            digest.update(item.relative.encode()); digest.update(b"\0")
            digest.update(bytes.fromhex(item.sha256)); digest.update(b"\0")
        return digest.hexdigest()

    def reread(self) -> tuple[str, list[dict[str, Any]]]:
        """Recompute every identity through the same descriptors, AND re-state every pathname.

        Two questions, and the second is the one that is easy to forget. The descriptors answer
        "did the bytes we measured change?". The pathnames answer "does the name the interpreter
        was given still resolve to the object we measured?". A held descriptor survives its name
        being re-pointed, so without the second question an unchanged hash is compatible with a
        substituted examiner having run.
        """
        changes: list[dict[str, Any]] = []
        digest = hashlib.sha256()
        digest.update(b"worldline-execution-verifier-set-v1\0")
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
            digest.update(item.root_key.encode()); digest.update(b"\0")
            digest.update(item.relative.encode()); digest.update(b"\0")
            digest.update(bytes.fromhex(now) if now else b"\0" * 32); digest.update(b"\0")
        return digest.hexdigest(), changes

    def rewrite_argv(self, argv: Sequence[str], roots: Mapping[str, str]) -> tuple[list[str], list[dict[str, str]]]:
        """Point the check at the staged copies. A token that named a verifier now names the one
        that was identified, so the swap a candidate can still perform is a swap of something the
        check does not execute."""
        by_logical: dict[str, StagedVerifier] = {}
        for item in self.items:
            logical = roots.get(item.root_key)
            if logical:
                by_logical[str(Path(logical) / item.relative)] = item
        out: list[str] = []
        rewrites: list[dict[str, str]] = []
        for token in argv:
            item = by_logical.get(token)
            if item is None:
                out.append(token)
                continue
            out.append(item.staged)
            rewrites.append({"from": token, "to": item.staged, "sha256": item.sha256})
        return out, rewrites

    def as_evidence(self) -> dict[str, Any]:
        return {
            "mount": VERIFIER_MOUNT,
            "identity": self.identity(),
            "members": [item.as_dict() for item in self.items],
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
