"""Removing a tree the daemon made read-only, without ever following a link.

Payloads, staging directories and overlay work directories are stored read-only, some of them
0000, so removing them needs owner access to every directory first. Granting it by path follows
any link the tree holds, and a tree's content is often a candidate's: an agent's upper layer with
a link to PRIME's content had prune set that content to 0700, outside the tree and outside any
transaction (review of 796cb02). Here every directory is opened relative to its parent with
O_NOFOLLOW and changed through its own descriptor, links are left as they are, and the removal is
shutil.rmtree's descriptor-based walk, which does not follow links either.
"""
from __future__ import annotations

import os
import shutil
import stat

_PATH = os.O_PATH | os.O_NOFOLLOW | os.O_DIRECTORY | os.O_CLOEXEC


def _owner_accessible_children(fd: int) -> list[str]:
    """Give the directory behind `fd` owner rwx (through the descriptor, never a name) and list
    the names of its subdirectories that are directories themselves, not links."""
    mode = stat.S_IMODE(os.fstat(fd).st_mode)
    if mode & 0o700 != 0o700:
        os.chmod(f"/proc/self/fd/{fd}", mode | 0o700)
    listing = os.open(".", os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC, dir_fd=fd)
    try:
        with os.scandir(listing) as entries:
            return [entry.name for entry in entries if entry.is_dir(follow_symlinks=False)]
    finally:
        os.close(listing)


def grant_owner_access(path: str | bytes | os.PathLike) -> None:
    """Owner rwx on `path` and every directory below it; a link is never followed, and `path`
    itself must be a real directory."""
    stack: list[tuple[int, list[str]]] = []
    top = os.open(os.fsencode(path), _PATH)
    try:
        stack.append((top, _owner_accessible_children(top)))
    except BaseException:
        os.close(top)
        raise
    try:
        while stack:
            fd, names = stack[-1]
            if not names:
                os.close(fd)
                stack.pop()
                continue
            name = names.pop()
            try:
                child = os.open(name, _PATH, dir_fd=fd)
            except OSError:
                continue  # gone, or replaced by something that is not a directory
            try:
                children = _owner_accessible_children(child)
            except BaseException:
                os.close(child)
                raise
            stack.append((child, children))
    finally:
        for fd, _names in stack:
            os.close(fd)


def remove_tree(path: str | bytes | os.PathLike, *, ignore_errors: bool = False) -> None:
    """Remove a real directory and everything below it without following a link anywhere."""
    if not os.path.lexists(path):
        return
    try:
        grant_owner_access(path)
        shutil.rmtree(path)
    except OSError:
        if not ignore_errors:
            raise
