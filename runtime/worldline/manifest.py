from __future__ import annotations

import base64
from dataclasses import dataclass
import errno
import os
import posixpath
import shutil
import stat
from pathlib import Path
from typing import Any, Iterable

from . import SCHEMA_VERSION
from .canonical import atomic_write, canonical_bytes, parse_canonical
from .core import Core, hash_id
from .errors import WorldlineError

_ACL_NAMES = {b"system.posix_acl_access", b"system.posix_acl_default"}


def path_b64(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii")


def path_from_b64(value: str) -> bytes:
    try:
        raw = base64.b64decode(value.encode("ascii"), validate=True)
    except (UnicodeEncodeError, ValueError) as exc:
        raise WorldlineError("INVALID_PATH_ENCODING", "path is not canonical base64") from exc
    validate_relative(raw)
    return raw


def display_path(value: bytes) -> str:
    return value.decode("utf-8", "replace") if value else "."


def validate_relative(value: bytes) -> None:
    if b"\x00" in value or value.startswith(b"/"):
        raise WorldlineError("PATH_ESCAPE", "manifest path is absolute or contains NUL")
    if not value:
        return
    parts = value.split(b"/")
    if any(part in (b"", b".", b"..") for part in parts):
        raise WorldlineError("PATH_ESCAPE", f"manifest path is not normalized: {display_path(value)}")


def _xattrs(path: bytes) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    try:
        names = os.listxattr(path, follow_symlinks=False)
    except OSError as exc:
        if exc.errno in (errno.ENOTSUP, errno.EOPNOTSUPP):
            raise WorldlineError("XATTR_UNAVAILABLE", f"filesystem cannot enumerate xattrs: {display_path(path)}") from exc
        raise
    encoded: list[dict[str, str]] = []
    acls: list[dict[str, str]] = []
    normalized = sorted(os.fsencode(name) for name in names)
    for name in normalized:
        value = os.getxattr(path, name, follow_symlinks=False)
        item = {"nameB64": path_b64(name), "valueB64": path_b64(value)}
        encoded.append(item)
        if name in _ACL_NAMES:
            acls.append(item.copy())
    return encoded, acls


def _metadata(info: os.stat_result, xattrs: list[dict[str, str]], acls: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "mode": stat.S_IMODE(info.st_mode),
        "mtimeNs": info.st_mtime_ns,
        "xattrs": xattrs,
        "acls": acls,
    }


def _safe_symlink_target(relative: bytes, target: bytes) -> None:
    if b"\x00" in target or target.startswith(b"/"):
        raise WorldlineError(
            "EXTERNAL_SYMLINK",
            f"symlink leaves registered root: {display_path(relative)} -> {display_path(target)}",
        )
    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(relative), target))
    if resolved == b".." or resolved.startswith(b"../") or resolved.startswith(b"/"):
        raise WorldlineError(
            "EXTERNAL_SYMLINK",
            f"symlink leaves registered root: {display_path(relative)} -> {display_path(target)}",
        )


@dataclass(frozen=True, slots=True)
class CapturedManifest:
    value: dict[str, Any]
    canonical: bytes
    root_hash: str

    def entry_map(self) -> dict[bytes, dict[str, Any]]:
        return {path_from_b64(entry["pathB64"]): entry for entry in self.value["entries"]}

    def save(self, path: Path) -> None:
        atomic_write(path, self.canonical)


class Manifest:
    @staticmethod
    def load(path: Path, core: Core | None = None) -> CapturedManifest:
        verifier = core or Core.shared()
        data = path.read_bytes()
        value = parse_canonical(data)
        if not isinstance(value, dict) or value.get("schemaVersion") != SCHEMA_VERSION:
            raise WorldlineError("INVALID_MANIFEST", f"manifest schema is invalid: {path}")
        required = {
            "schemaVersion", "rootKey", "kind", "rootPathB64", "rootPathDisplay",
            "rootMetadata", "entries", "repository",
        }
        if set(value) != required or not isinstance(value["entries"], list):
            raise WorldlineError("INVALID_MANIFEST", f"manifest fields are invalid: {path}")
        for entry in value["entries"]:
            path_from_b64(entry["pathB64"])
        root_hash = hash_id(verifier.hash_bytes(b"worldline-manifest-v1" + data))
        return CapturedManifest(value=value, canonical=data, root_hash=root_hash)

    @staticmethod
    def verify_content(
        manifest: CapturedManifest,
        root: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        core: Core | None = None,
    ) -> None:
        verifier = core or Core.shared()
        raw_root = os.path.abspath(os.fsencode(root))
        expected = manifest.entry_map()
        observed: dict[bytes, os.stat_result] = {}
        for current, directories, files in os.walk(raw_root, followlinks=False):
            current_bytes = os.fsencode(current)
            for name in sorted([*directories, *files], key=os.fsencode):
                absolute = os.path.join(current_bytes, os.fsencode(name))
                relative = os.path.relpath(absolute, raw_root)
                observed[relative] = os.lstat(absolute)
            directories[:] = [
                name for name in directories
                if not stat.S_ISLNK(os.lstat(os.path.join(current_bytes, os.fsencode(name))).st_mode)
            ]
        if set(observed) != set(expected):
            raise WorldlineError("PAYLOAD_INTEGRITY_FAILED", "candidate payload path set differs from its manifest")
        groups: dict[str, tuple[int, int]] = {}
        for relative, entry in expected.items():
            absolute = os.path.join(raw_root, relative)
            info = observed[relative]
            if entry["type"] == "file":
                if not stat.S_ISREG(info.st_mode) or hash_id(verifier.hash_file(absolute)) != entry["contentHash"]:
                    raise WorldlineError("PAYLOAD_INTEGRITY_FAILED", f"candidate file changed: {entry['pathDisplay']}")
                group = entry["hardLinkGroup"]
                if group is not None:
                    inode = (info.st_dev, info.st_ino)
                    if group in groups and groups[group] != inode:
                        raise WorldlineError("PAYLOAD_INTEGRITY_FAILED", f"candidate hard-link group broke: {entry['pathDisplay']}")
                    groups[group] = inode
            elif entry["type"] == "directory":
                if not stat.S_ISDIR(info.st_mode):
                    raise WorldlineError("PAYLOAD_INTEGRITY_FAILED", f"candidate directory changed type: {entry['pathDisplay']}")
            elif entry["type"] == "symlink":
                target = os.fsencode(os.readlink(absolute))
                if not stat.S_ISLNK(info.st_mode) or path_b64(target) != entry["targetB64"]:
                    raise WorldlineError("PAYLOAD_INTEGRITY_FAILED", f"candidate symlink changed: {entry['pathDisplay']}")
            else:
                raise WorldlineError("INVALID_MANIFEST", f"unknown manifest entry type: {entry['type']}")

    @staticmethod
    def capture(
        root: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        logical_root: str | bytes | os.PathLike[str] | os.PathLike[bytes] | None = None,
        *,
        root_key: str,
        kind: str,
        core: Core | None = None,
        repository: dict[str, Any] | None = None,
    ) -> CapturedManifest:
        verifier = core or Core.shared()
        raw_root = os.path.abspath(os.fsencode(root))
        raw_logical_root = raw_root if logical_root is None else os.path.abspath(os.fsencode(logical_root))
        root_info = os.lstat(raw_root)
        if not stat.S_ISDIR(root_info.st_mode):
            raise WorldlineError("UNSUPPORTED_ROOT", f"registered root is not a directory: {display_path(raw_root)}")
        root_xattrs, root_acls = _xattrs(raw_root)
        entries: list[dict[str, Any]] = []
        hard_links: dict[tuple[int, int], list[tuple[bytes, dict[str, Any], int]]] = {}
        directories: list[bytes] = [b""]

        while directories:
            relative_directory = directories.pop()
            absolute_directory = raw_root if not relative_directory else os.path.join(raw_root, relative_directory)
            with os.scandir(absolute_directory) as iterator:
                children = sorted(iterator, key=lambda item: os.fsencode(item.name))
            next_directories: list[bytes] = []
            for child in children:
                name = os.fsencode(child.name)
                if name in (b"", b".", b"..") or b"/" in name or b"\x00" in name:
                    raise WorldlineError("PATH_ESCAPE", "filesystem returned an invalid directory entry")
                relative = name if not relative_directory else relative_directory + b"/" + name
                validate_relative(relative)
                absolute = os.path.join(raw_root, relative)
                info = os.lstat(absolute)
                if info.st_dev != root_info.st_dev:
                    raise WorldlineError(
                        "CROSS_DEVICE_ENTRY",
                        f"entry crosses a filesystem boundary: {display_path(relative)}",
                    )
                xattrs, acls = _xattrs(absolute)
                entry: dict[str, Any] = {
                    "pathB64": path_b64(relative),
                    "pathDisplay": display_path(relative),
                    **_metadata(info, xattrs, acls),
                }
                if stat.S_ISREG(info.st_mode):
                    entry.update(
                        {
                            "type": "file",
                            "size": info.st_size,
                            "contentHash": hash_id(verifier.hash_file(absolute)),
                            "hardLinkGroup": None,
                        }
                    )
                    hard_links.setdefault((info.st_dev, info.st_ino), []).append((relative, entry, info.st_nlink))
                elif stat.S_ISDIR(info.st_mode):
                    entry["type"] = "directory"
                    next_directories.append(relative)
                elif stat.S_ISLNK(info.st_mode):
                    target = os.readlink(absolute)
                    target_bytes = os.fsencode(target)
                    _safe_symlink_target(relative, target_bytes)
                    entry.update(
                        {
                            "type": "symlink",
                            "targetB64": path_b64(target_bytes),
                            "targetDisplay": display_path(target_bytes),
                        }
                    )
                else:
                    raise WorldlineError(
                        "UNSUPPORTED_SPECIAL_FILE",
                        f"device, socket, or FIFO cannot enter a world: {display_path(relative)}",
                    )
                entries.append(entry)
            directories.extend(reversed(next_directories))

        for members in hard_links.values():
            observed_links = members[0][2]
            if observed_links != len(members):
                raise WorldlineError(
                    "EXTERNAL_HARDLINK",
                    f"hard-linked file has links outside the registered root: {display_path(members[0][0])}",
                )
            if len(members) > 1:
                member_names = [path_b64(relative) for relative, _entry, _count in sorted(members)]
                group = hash_id(
                    verifier.hash_bytes(b"worldline-hardlink-v1" + canonical_bytes(member_names))
                )
                for _relative, entry, _count in members:
                    entry["hardLinkGroup"] = group

        entries.sort(key=lambda entry: path_from_b64(entry["pathB64"]))
        value: dict[str, Any] = {
            "schemaVersion": SCHEMA_VERSION,
            "rootKey": root_key,
            "kind": kind,
            "rootPathB64": path_b64(raw_logical_root),
            "rootPathDisplay": display_path(raw_logical_root),
            "rootMetadata": _metadata(root_info, root_xattrs, root_acls),
            "entries": entries,
            "repository": repository,
        }
        encoded = canonical_bytes(value)
        root_hash = hash_id(verifier.hash_bytes(b"worldline-manifest-v1" + encoded))
        return CapturedManifest(value=value, canonical=encoded, root_hash=root_hash)

    @staticmethod
    def component_roots(manifests: Iterable[CapturedManifest], core: Core | None = None) -> dict[str, str]:
        verifier = core or Core.shared()
        grouped: dict[str, list[dict[str, str]]] = {"filesystem": [], "config": [], "repository": []}
        kind_to_component = {"filesystem": "filesystem", "config": "config", "repo": "repository"}
        for manifest in manifests:
            component = kind_to_component[manifest.value["kind"]]
            grouped[component].append(
                {"rootKey": manifest.value["rootKey"], "manifestRoot": manifest.root_hash}
            )
        result: dict[str, str] = {}
        for component, values in grouped.items():
            values.sort(key=lambda item: item["rootKey"])
            result[component] = hash_id(
                verifier.hash_bytes(
                    f"worldline-{component}-component-v1".encode("ascii") + canonical_bytes(values)
                )
            )
        return result

    @staticmethod
    def root_set_hash(manifests: Iterable[CapturedManifest], core: Core | None = None) -> str:
        verifier = core or Core.shared()
        values = sorted(
            (
                {"rootKey": manifest.value["rootKey"], "manifestRoot": manifest.root_hash}
                for manifest in manifests
            ),
            key=lambda item: item["rootKey"],
        )
        return hash_id(verifier.hash_bytes(b"worldline-root-manifests-v1" + canonical_bytes(values)))

    @staticmethod
    def materialize(
        manifest: CapturedManifest,
        source_root: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        destination_root: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        *,
        core: Core | None = None,
        verify: bool = True,
    ) -> CapturedManifest:
        verifier = core or Core.shared()
        source = os.path.abspath(os.fsencode(source_root))
        destination = os.path.abspath(os.fsencode(destination_root))
        if os.path.lexists(destination):
            if not stat.S_ISDIR(os.lstat(destination).st_mode) or os.listdir(destination):
                raise WorldlineError("DESTINATION_NOT_EMPTY", f"materialization destination is not empty: {display_path(destination)}")
        else:
            os.makedirs(destination, mode=0o700)

        entries = manifest.value["entries"]
        directories = [entry for entry in entries if entry["type"] == "directory"]
        files = [entry for entry in entries if entry["type"] == "file"]
        symlinks = [entry for entry in entries if entry["type"] == "symlink"]
        directories.sort(key=lambda item: (path_from_b64(item["pathB64"]).count(b"/"), path_from_b64(item["pathB64"])))
        hard_link_targets: dict[str, bytes] = {}

        for entry in directories:
            relative = path_from_b64(entry["pathB64"])
            os.mkdir(os.path.join(destination, relative), mode=entry["mode"])

        for entry in files:
            relative = path_from_b64(entry["pathB64"])
            source_path = os.path.join(source, relative)
            destination_path = os.path.join(destination, relative)
            group = entry["hardLinkGroup"]
            if group is not None and group in hard_link_targets:
                os.link(hard_link_targets[group], destination_path, follow_symlinks=False)
            else:
                with open(source_path, "rb", buffering=0) as input_stream, open(destination_path, "xb", buffering=0) as output_stream:
                    shutil.copyfileobj(input_stream, output_stream, length=1024 * 1024)
                    output_stream.flush()
                    os.fsync(output_stream.fileno())
                if hash_id(verifier.hash_file(destination_path)) != entry["contentHash"]:
                    raise WorldlineError("COPY_VERIFICATION_FAILED", f"file bytes changed during materialization: {entry['pathDisplay']}")
                if group is not None:
                    hard_link_targets[group] = destination_path
            Manifest._apply_metadata(destination_path, entry, symlink=False)

        for entry in symlinks:
            relative = path_from_b64(entry["pathB64"])
            target = base64.b64decode(entry["targetB64"].encode("ascii"), validate=True)
            _safe_symlink_target(relative, target)
            destination_path = os.path.join(destination, relative)
            os.symlink(target, destination_path)
            Manifest._apply_metadata(destination_path, entry, symlink=True)

        for entry in sorted(
            directories,
            key=lambda item: (path_from_b64(item["pathB64"]).count(b"/"), path_from_b64(item["pathB64"])),
            reverse=True,
        ):
            Manifest._apply_metadata(
                os.path.join(destination, path_from_b64(entry["pathB64"])),
                entry,
                symlink=False,
            )
        Manifest._apply_metadata(destination, manifest.value["rootMetadata"], symlink=False)

        captured = Manifest.capture(
            destination,
            logical_root=base64.b64decode(manifest.value["rootPathB64"].encode("ascii"), validate=True),
            root_key=manifest.value["rootKey"],
            kind=manifest.value["kind"],
            core=verifier,
            repository=manifest.value.get("repository"),
        )
        if verify and captured.root_hash != manifest.root_hash:
            raise WorldlineError(
                "COPY_VERIFICATION_FAILED",
                "materialized root does not match its source manifest",
                {"expected": manifest.root_hash, "actual": captured.root_hash},
            )
        return captured

    @staticmethod
    def _apply_metadata(path: bytes, metadata: dict[str, Any], *, symlink: bool) -> None:
        expected_names: set[bytes] = set()
        for item in metadata.get("xattrs", []):
            name = base64.b64decode(item["nameB64"].encode("ascii"), validate=True)
            value = base64.b64decode(item["valueB64"].encode("ascii"), validate=True)
            expected_names.add(name)
            os.setxattr(path, name, value, follow_symlinks=not symlink)
        existing = {os.fsencode(name) for name in os.listxattr(path, follow_symlinks=not symlink)}
        for name in existing - expected_names:
            os.removexattr(path, name, follow_symlinks=not symlink)
        if not symlink:
            os.chmod(path, metadata["mode"], follow_symlinks=False)
        os.utime(
            path,
            ns=(metadata["mtimeNs"], metadata["mtimeNs"]),
            follow_symlinks=not symlink,
        )
