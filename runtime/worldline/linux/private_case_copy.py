"""Copy one disposable verifier case tree between separate private role views.

The caller supplies a fresh destination under a broker-owned directory. It must
not expose that destination until this function returns. The worker and candidate
views are mounted at ``logical_root`` in their respective mount namespaces, so
absolute links have the same meaning in each view. This module never follows a
source link. It permits only links whose lexical target stays in that case tree.

The caller must also hold an exclusive case lease. Metadata comparisons detect
changes during a copy, but cannot replace a filesystem snapshot against a writer
that deliberately races and restores metadata.
"""

from __future__ import annotations

import hashlib
import json
import os
import posixpath
import stat
from pathlib import Path
from typing import Any


MAX_CASE_BYTES = 268_435_456
MAX_CASE_ENTRIES = 100_000
MAX_CASE_DEPTH = 128
_DIR_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
_FILE_FLAGS = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK
_LINK_FLAGS = os.O_PATH | os.O_NOFOLLOW | os.O_CLOEXEC


class CaseCopyError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _refuse(code: str, message: str) -> None:
    raise CaseCopyError(code, message)


def _absolute(path: Path | str) -> Path:
    value = str(path)
    if (not value.startswith("/") or value == "/" or "\0" in value
            or posixpath.normpath(value) != value or value.startswith("//")):
        _refuse("CASE_COPY_PATH", "path must be absolute and normalized")
    return Path(value)


def _open_directory(path: Path) -> int:
    descriptor = os.open("/", _DIR_FLAGS)
    try:
        for part in path.parts[1:]:
            child = os.open(part, _DIR_FLAGS, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def _signature(info: os.stat_result) -> tuple[int, ...]:
    return (info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns, info.st_nlink)


def _mount_id(descriptor: int) -> str:
    try:
        lines = Path(f"/proc/self/fdinfo/{descriptor}").read_text().splitlines()
    except OSError as exc:
        _refuse("CASE_COPY_MOUNT_ID", f"mount identity unavailable: {exc}")
    values = [line.partition(":")[2].strip() for line in lines
              if line.startswith("mnt_id:")]
    if len(values) != 1 or not values[0].isdigit():
        _refuse("CASE_COPY_MOUNT_ID", "mount identity unavailable")
    return values[0]


def _check_entry(descriptor: int, before: os.stat_result,
                 source_mount: str, *, link_path: str | None = None) -> None:
    if _mount_id(descriptor) != source_mount or before.st_mode & 0o7000:
        _refuse("CASE_COPY_UNSUPPORTED", "mount or special permission bits in case tree")
    if link_path is None:
        attributes = os.listxattr(descriptor)
    else:
        # A pinned O_PATH descriptor supplies the parent. llistxattr examines
        # the link itself, rather than following its target.
        attributes = os.listxattr(link_path, follow_symlinks=False)
    if attributes:
        _refuse("CASE_COPY_UNSUPPORTED", "extended attributes in case tree")


def _check_link_target(parent: str, target: str, logical_root: str) -> None:
    if not target or "\0" in target:
        _refuse("CASE_COPY_LINK_ESCAPE", "invalid link target")
    resolved = posixpath.normpath(posixpath.join(parent, target))
    if resolved != logical_root and not resolved.startswith(logical_root + "/"):
        _refuse("CASE_COPY_LINK_ESCAPE", "link target escapes the case tree")


def copy_case_tree(source: Path | str, destination: Path | str, *,
                   logical_root: str, max_bytes: int = MAX_CASE_BYTES,
                   max_entries: int = MAX_CASE_ENTRIES,
                   max_depth: int = MAX_CASE_DEPTH) -> dict[str, Any]:
    """Copy a quiescent scoped tree; return a content and metadata manifest.

    Only ordinary files, directories, and internal symlinks are accepted.
    Hardlinks, special files, nested mounts (including same-device bind mounts),
    xattrs, special permission bits, and observed mutations cause refusal. The
    destination must not exist. A refused partial destination is never published;
    its cleanup is the responsibility of the broker-owned staging caller.
    """
    src = _absolute(source)
    dst = _absolute(destination)
    logical = str(_absolute(logical_root))
    if (src == dst or src in dst.parents or dst in src.parents):
        _refuse("CASE_COPY_PATH", "source and destination overlap")
    if any(type(limit) is not int or limit < 1
           for limit in (max_bytes, max_entries, max_depth)):
        _refuse("CASE_COPY_LIMIT", "copy limits must be positive integers")

    src_fd = _open_directory(src)
    try:
        parent_fd = _open_directory(dst.parent)
    except BaseException:
        os.close(src_fd)
        raise
    records: list[dict[str, Any]] = []
    budget = {"bytes": 0, "entries": 0}
    try:
        source_mount = _mount_id(src_fd)
        try:
            os.mkdir(dst.name, mode=0o700, dir_fd=parent_fd)
        except FileExistsError:
            _refuse("CASE_COPY_PATH", "destination already exists")
        dst_fd = os.open(dst.name, _DIR_FLAGS, dir_fd=parent_fd)
        try:
            def copy_entry(source_fd: int, target_fd: int, relative: str,
                           depth: int) -> None:
                before = os.fstat(source_fd)
                budget["entries"] += 1
                if budget["entries"] > max_entries or depth > max_depth:
                    _refuse("CASE_COPY_LIMIT", "case tree exceeds entry or depth limit")
                _check_entry(source_fd, before, source_mount)
                if not stat.S_ISDIR(before.st_mode):
                    _refuse("CASE_COPY_UNSUPPORTED", "case tree root is not a directory")
                first_names = sorted(os.listdir(source_fd))
                for name in first_names:
                    if name in (".", "..") or "/" in name or "\0" in name:
                        _refuse("CASE_COPY_PATH", "invalid case entry name")
                    prior = os.stat(name, dir_fd=source_fd, follow_symlinks=False)
                    child_relative = name if relative == "." else relative + "/" + name
                    child_logical = posixpath.join(logical, child_relative)
                    if stat.S_ISDIR(prior.st_mode):
                        child_src = os.open(name, _DIR_FLAGS, dir_fd=source_fd)
                        try:
                            if _signature(prior) != _signature(os.fstat(child_src)):
                                _refuse("CASE_COPY_CHANGED", "directory changed while opening")
                            os.mkdir(name, mode=0o700, dir_fd=target_fd)
                            child_dst = os.open(name, _DIR_FLAGS, dir_fd=target_fd)
                            try:
                                copy_entry(child_src, child_dst, child_relative, depth + 1)
                            finally:
                                os.close(child_dst)
                        finally:
                            os.close(child_src)
                    elif stat.S_ISREG(prior.st_mode):
                        if prior.st_nlink != 1:
                            _refuse("CASE_COPY_HARDLINK", "hardlinked file in case tree")
                        child_src = os.open(name, _FILE_FLAGS, dir_fd=source_fd)
                        try:
                            before_file = os.fstat(child_src)
                            if _signature(prior) != _signature(before_file):
                                _refuse("CASE_COPY_CHANGED", "file changed while opening")
                            budget["entries"] += 1
                            budget["bytes"] += before_file.st_size
                            if (budget["entries"] > max_entries or
                                    budget["bytes"] > max_bytes or depth + 1 > max_depth):
                                _refuse("CASE_COPY_LIMIT", "case tree exceeds copy limit")
                            _check_entry(child_src, before_file, source_mount)
                            child_dst = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                                                os.O_NOFOLLOW | os.O_CLOEXEC, 0o600,
                                                dir_fd=target_fd)
                            digest = hashlib.sha256()
                            count = 0
                            try:
                                while True:
                                    chunk = os.read(child_src, 65536)
                                    if not chunk:
                                        break
                                    count += len(chunk)
                                    if count > before_file.st_size:
                                        _refuse("CASE_COPY_CHANGED", "file grew during copy")
                                    digest.update(chunk)
                                    view = memoryview(chunk)
                                    while view:
                                        written = os.write(child_dst, view)
                                        if written <= 0:
                                            _refuse("CASE_COPY_IO", "destination write did not progress")
                                        view = view[written:]
                                if count != before_file.st_size or _signature(before_file) != _signature(os.fstat(child_src)):
                                    _refuse("CASE_COPY_CHANGED", "file changed during copy")
                                os.fchmod(child_dst, stat.S_IMODE(before_file.st_mode))
                            finally:
                                os.close(child_dst)
                            records.append({"path": child_relative, "kind": "file",
                                            "mode": stat.S_IMODE(before_file.st_mode),
                                            "sha256": digest.hexdigest()})
                        finally:
                            os.close(child_src)
                    elif stat.S_ISLNK(prior.st_mode):
                        child_src = os.open(name, _LINK_FLAGS, dir_fd=source_fd)
                        try:
                            before_link = os.fstat(child_src)
                            if _signature(prior) != _signature(before_link):
                                _refuse("CASE_COPY_CHANGED", "link changed while opening")
                            if before_link.st_nlink != 1:
                                _refuse("CASE_COPY_HARDLINK", "hardlinked link in case tree")
                            budget["entries"] += 1
                            if budget["entries"] > max_entries or depth + 1 > max_depth:
                                _refuse("CASE_COPY_LIMIT", "case tree exceeds entry or depth limit")
                            _check_entry(child_src, before_link, source_mount,
                                         link_path=f"/proc/self/fd/{source_fd}/{name}")
                            target = os.readlink("", dir_fd=child_src)
                            _check_link_target(posixpath.dirname(child_logical), target, logical)
                            if _signature(before_link) != _signature(os.fstat(child_src)):
                                _refuse("CASE_COPY_CHANGED", "link changed during copy")
                            os.symlink(target, name, dir_fd=target_fd)
                            records.append({"path": child_relative, "kind": "symlink",
                                            "target": target})
                        finally:
                            os.close(child_src)
                    else:
                        _refuse("CASE_COPY_UNSUPPORTED", "special file in case tree")
                    if _signature(prior) != _signature(os.stat(name, dir_fd=source_fd, follow_symlinks=False)):
                        _refuse("CASE_COPY_CHANGED", "case entry changed during copy")
                if (first_names != sorted(os.listdir(source_fd)) or
                        _signature(before) != _signature(os.fstat(source_fd))):
                    _refuse("CASE_COPY_CHANGED", "case directory changed during copy")
                os.fchmod(target_fd, stat.S_IMODE(before.st_mode))
                records.append({"path": relative, "kind": "directory",
                                "mode": stat.S_IMODE(before.st_mode)})

            copy_entry(src_fd, dst_fd, ".", 0)
        finally:
            os.close(dst_fd)
    finally:
        os.close(parent_fd)
        os.close(src_fd)
    digest = hashlib.sha256(json.dumps(records, sort_keys=True,
                                       separators=(",", ":")).encode()).hexdigest()
    return {"sha256": digest, "bytes": budget["bytes"],
            "entries": budget["entries"]}
