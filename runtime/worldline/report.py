"""Private report collection for a future separated examiner domain.

This collector only authenticates bytes written into an already isolated directory. It does
not establish that the writer was isolated: the caller must prove the report mount, process
identity and lifetime boundary before marking a report admissible.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat
from typing import Any

from .errors import WorldlineError


MAX_REPORT_BYTES = 10_000_000
REPORT_NAME = "report"
_BINDING_NAME = ".binding"
_DIRECTORY_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW
_FILE_FLAGS = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK


def _open_directory_no_symlinks(directory: Path) -> int:
    """Open every path component from /, refusing a substituted parent symlink."""
    if not directory.is_absolute():
        raise WorldlineError("REPORT_PATH_INVALID", "private report directory is not absolute")
    if any(component in ("", ".", "..") for component in directory.parts[1:]):
        raise WorldlineError("REPORT_PATH_INVALID", "private report directory contains traversal")
    descriptor = os.open("/", _DIRECTORY_FLAGS)
    try:
        for component in directory.parts[1:]:
            next_descriptor = os.open(component, _DIRECTORY_FLAGS, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = next_descriptor
        return descriptor
    except OSError as exc:
        os.close(descriptor)
        raise WorldlineError("REPORT_PATH_INVALID", f"private report directory is not securely reachable: {exc}") from exc


def _binding(run_id: str, check_id: str, candidate_identity: str,
             verifier_identity: str) -> dict[str, str]:
    if (not isinstance(run_id, str) or not run_id or run_id in (".", "..")
            or "/" in run_id or "\x00" in run_id
            or any(not isinstance(value, str) or not value or "\x00" in value
                   for value in (check_id, candidate_identity, verifier_identity))):
        raise WorldlineError("REPORT_BINDING_INVALID", "private report invocation identities are invalid")
    return {"runId": run_id, "checkId": check_id,
            "candidateIdentity": candidate_identity,
            "verifierIdentity": verifier_identity}


def prepare_private_report(base: Path, *, run_id: str, check_id: str,
                           candidate_identity: str, verifier_identity: str) -> Path:
    """Create one private report directory for a new invocation, refusing reuse."""
    binding = _binding(run_id, check_id, candidate_identity, verifier_identity)
    base_fd = _open_directory_no_symlinks(base)
    try:
        base_stat = os.fstat(base_fd)
        if base_stat.st_uid != os.getuid() or base_stat.st_mode & 0o077:
            raise WorldlineError("REPORT_PATH_INVALID", "private report base is not owner-only")
        try:
            os.mkdir(run_id, 0o700, dir_fd=base_fd)
            directory_fd = os.open(run_id, _DIRECTORY_FLAGS, dir_fd=base_fd)
        except OSError as exc:
            raise WorldlineError("REPORT_PATH_INVALID", f"private report invocation cannot be created: {exc}") from exc
        try:
            marker_fd = os.open(_BINDING_NAME, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                                os.O_CLOEXEC | os.O_NOFOLLOW, 0o600, dir_fd=directory_fd)
            try:
                marker = json.dumps(binding, sort_keys=True, separators=(",", ":")).encode("utf-8")
                written = 0
                while written < len(marker):
                    count = os.write(marker_fd, marker[written:])
                    if count <= 0:
                        raise OSError("private report binding write made no progress")
                    written += count
                os.fsync(marker_fd)
            finally:
                os.close(marker_fd)
            os.fsync(directory_fd)
        except OSError as exc:
            raise WorldlineError("REPORT_PATH_INVALID", f"private report binding cannot be written: {exc}") from exc
        finally:
            os.close(directory_fd)
        return base / run_id
    finally:
        os.close(base_fd)


def collect_private_report(directory: Path, *, run_id: str, check_id: str,
                           candidate_identity: str, verifier_identity: str, _raw_observer=None) -> tuple[bytes, dict[str, Any]]:
    """Read a fixed-name regular report from a private examiner directory.

    The caller must wait until the examiner and its entire supervised process group are
    quiescent. The returned identity binds the collected bytes to that invocation; it is
    descriptive until the caller establishes the separate examiner/candidate domains.
    """
    if _raw_observer is not None:
        return _collect_private_report_observed(directory, run_id=run_id, check_id=check_id,
            candidate_identity=candidate_identity, verifier_identity=verifier_identity,
            observer=_raw_observer)
    binding = _binding(run_id, check_id, candidate_identity, verifier_identity)
    directory_fd = _open_directory_no_symlinks(directory)
    try:
        try:
            marker_fd = os.open(_BINDING_NAME, _FILE_FLAGS, dir_fd=directory_fd)
            try:
                marker = os.read(marker_fd, 4097)
                marker_info = os.fstat(marker_fd)
            finally:
                os.close(marker_fd)
            if (len(marker) > 4096 or not stat.S_ISREG(marker_info.st_mode)
                    or marker_info.st_nlink != 1 or marker_info.st_size != len(marker)
                    or json.loads(marker.decode("utf-8", "strict")) != binding):
                raise WorldlineError("REPORT_BINDING_INVALID", "private report invocation binding does not match")
        except (OSError, ValueError, UnicodeError) as exc:
            raise WorldlineError("REPORT_BINDING_INVALID", f"private report invocation binding is unreadable: {exc}") from exc
        try:
            report_fd = os.open(REPORT_NAME, _FILE_FLAGS, dir_fd=directory_fd)
        except FileNotFoundError as exc:
            raise WorldlineError("REPORT_MISSING", "the isolated examiner produced no report") from exc
        except OSError as exc:
            raise WorldlineError("REPORT_PATH_INVALID", f"the isolated report cannot be opened: {exc}") from exc
        try:
            before = os.fstat(report_fd)
            if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
                raise WorldlineError("REPORT_PATH_INVALID", "the isolated report is not a singly linked regular file")
            if before.st_size > MAX_REPORT_BYTES:
                raise WorldlineError("REPORT_TOO_LARGE", "the isolated report exceeds the size limit")
            content = bytearray()
            while len(content) <= MAX_REPORT_BYTES:
                chunk = os.read(report_fd, min(65536, MAX_REPORT_BYTES + 1 - len(content)))
                if not chunk:
                    break
                content.extend(chunk)
            if len(content) > MAX_REPORT_BYTES:
                raise WorldlineError("REPORT_TOO_LARGE", "the isolated report exceeds the size limit")
            after = os.fstat(report_fd)
            if len(content) != after.st_size or (
                    before.st_dev, before.st_ino, before.st_size,
                    before.st_mtime_ns, before.st_ctime_ns) != (
                    after.st_dev, after.st_ino, after.st_size,
                    after.st_mtime_ns, after.st_ctime_ns):
                raise WorldlineError("REPORT_CHANGED", "the isolated report changed during collection")
            payload = bytes(content)
            return payload, {
                "collection": "private-directory",
                **binding,
                "sha256": hashlib.sha256(payload).hexdigest(),
                "sizeBytes": len(payload),
            }
        except OSError as exc:
            raise WorldlineError("REPORT_READ_FAILED", f"isolated report could not be read: {exc}") from exc
        finally:
            os.close(report_fd)
    finally:
        os.close(directory_fd)


def _collect_private_report_observed(directory: Path, *, run_id: str, check_id: str,
                           candidate_identity: str, verifier_identity: str, observer) -> tuple[bytes, dict[str, Any]]:
    """Read a fixed-name regular report from a private examiner directory.

    The caller must wait until the examiner and its entire supervised process group are
    quiescent. The returned identity binds the collected bytes to that invocation; it is
    descriptive until the caller establishes the separate examiner/candidate domains.
    """
    from .raw_observation import retain_read, retain_during_unwind, cleanup_call, retention_failed
    binding = _binding(run_id, check_id, candidate_identity, verifier_identity)
    directory_fd = _open_directory_no_symlinks(directory)
    try:
        try:
            marker_fd = os.open(_BINDING_NAME, _FILE_FLAGS, dir_fd=directory_fd)
            try:
                marker = None
                marker_read = False
                try:
                    marker = os.read(marker_fd, 4097)
                    marker_read = True
                finally:
                    retain_during_unwind(lambda: retain_read(lambda record: observer('private-report-binding', record),
                        marker, reached_eof=False, acquired=marker_read,
                        details={'file': _BINDING_NAME, 'binding': binding}))
                marker_info = os.fstat(marker_fd)
            finally:
                cleanup_call(lambda: os.close(marker_fd))
            if (len(marker) > 4096 or not stat.S_ISREG(marker_info.st_mode)
                    or marker_info.st_nlink != 1 or marker_info.st_size != len(marker)
                    or json.loads(marker.decode("utf-8", "strict")) != binding):
                raise WorldlineError("REPORT_BINDING_INVALID", "private report invocation binding does not match")
        except (OSError, ValueError, UnicodeError) as exc:
            if retention_failed(exc): raise
            raise WorldlineError("REPORT_BINDING_INVALID", f"private report invocation binding is unreadable: {exc}") from exc
        try:
            report_fd = os.open(REPORT_NAME, _FILE_FLAGS, dir_fd=directory_fd)
        except FileNotFoundError as exc:
            retain_during_unwind(lambda: retain_read(lambda record: observer('private-report', record), None,
                        reached_eof=False, acquired=False,
                        details={'fileOpened': False, 'openOutcome': 'FileNotFoundError', 'binding': binding}))
            raise WorldlineError("REPORT_MISSING", "the isolated examiner produced no report") from exc
        except OSError as exc:
            if retention_failed(exc): raise
            raise WorldlineError("REPORT_PATH_INVALID", f"the isolated report cannot be opened: {exc}") from exc
        content = None
        acquired = False
        reached_eof = False
        emitted = False
        def emit():
            nonlocal emitted
            if not emitted:
                emitted = True
                retain_during_unwind(lambda: retain_read(lambda record: observer('private-report', record),
                    content if acquired else None, reached_eof=reached_eof,
                    acquired=acquired, details={'fileOpened': True, 'binding': binding}))
        try:
            before = os.fstat(report_fd)
            if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
                raise WorldlineError("REPORT_PATH_INVALID", "the isolated report is not a singly linked regular file")
            if before.st_size > MAX_REPORT_BYTES:
                raise WorldlineError("REPORT_TOO_LARGE", "the isolated report exceeds the size limit")
            content = bytearray()
            try:
                while len(content) <= MAX_REPORT_BYTES:
                    chunk = os.read(report_fd, min(65536, MAX_REPORT_BYTES + 1 - len(content)))
                    acquired = True
                    if not chunk:
                        reached_eof = True
                        break
                    content.extend(chunk)
            finally:
                # Persist acquired bytes before size/stability validation and
                # later report parsing. A failed read retains only its prefix.
                emit()
            if len(content) > MAX_REPORT_BYTES:
                raise WorldlineError("REPORT_TOO_LARGE", "the isolated report exceeds the size limit")
            after = os.fstat(report_fd)
            if len(content) != after.st_size or (
                    before.st_dev, before.st_ino, before.st_size,
                    before.st_mtime_ns, before.st_ctime_ns) != (
                    after.st_dev, after.st_ino, after.st_size,
                    after.st_mtime_ns, after.st_ctime_ns):
                raise WorldlineError("REPORT_CHANGED", "the isolated report changed during collection")
            payload = bytes(content)
            return payload, {
                "collection": "private-directory",
                **binding,
                "sha256": hashlib.sha256(payload).hexdigest(),
                "sizeBytes": len(payload),
            }
        except OSError as exc:
            if retention_failed(exc): raise
            raise WorldlineError("REPORT_READ_FAILED", f"isolated report could not be read: {exc}") from exc
        finally:
            try:
                emit()
            finally:
                cleanup_call(lambda: os.close(report_fd))
    finally:
        cleanup_call(lambda: os.close(directory_fd))
