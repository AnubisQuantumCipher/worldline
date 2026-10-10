from __future__ import annotations

import base64
from dataclasses import dataclass
import os
import shutil
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

from . import SCHEMA_VERSION
from .canonical import canonical_bytes
from .core import Core, hash_id
from .errors import WorldlineError
from .manifest import CapturedManifest, Manifest, display_path, path_b64, path_from_b64, validate_relative


@dataclass(frozen=True, slots=True)
class DeltaResult:
    value: dict[str, Any]
    delta_hash: str


@dataclass(frozen=True, slots=True)
class MergeResult:
    staged: CapturedManifest | None
    conflicts: list[dict[str, Any]]
    applied: list[dict[str, Any]]


def _content_hash(entry: dict[str, Any] | None, core: Core) -> str | None:
    if entry is None:
        return None
    if entry["type"] == "file":
        return entry["contentHash"]
    if entry["type"] == "symlink":
        target = base64.b64decode(entry["targetB64"].encode("ascii"), validate=True)
        return hash_id(core.hash_bytes(b"worldline-symlink-target-v1" + target))
    return None


def _metadata_value(entry: dict[str, Any] | None) -> dict[str, Any] | None:
    if entry is None:
        return None
    result = {
        "type": entry["type"],
        "mode": entry["mode"],
        "xattrs": entry["xattrs"],
        "acls": entry["acls"],
    }
    if entry["type"] not in ("directory", "root"):
        result["mtimeNs"] = entry["mtimeNs"]
    if entry["type"] == "file":
        result["hardLinkGroup"] = entry["hardLinkGroup"]
    return result


def _metadata_hash(entry: dict[str, Any] | None, core: Core) -> str | None:
    value = _metadata_value(entry)
    if value is None:
        return None
    return hash_id(core.hash_bytes(b"worldline-entry-metadata-v1" + canonical_bytes(value)))


def _state(entry: dict[str, Any] | None, core: Core) -> dict[str, str | None]:
    return {"content": _content_hash(entry, core), "metadata": _metadata_hash(entry, core)}


def _same(first: dict[str, Any] | None, second: dict[str, Any] | None, core: Core) -> bool:
    return _state(first, core) == _state(second, core)


class Delta:
    @staticmethod
    def compute(
        base: CapturedManifest,
        candidate: CapturedManifest,
        core: Core | None = None,
    ) -> DeltaResult:
        verifier = core or Core.shared()
        if base.value["rootKey"] != candidate.value["rootKey"]:
            raise WorldlineError("ROOT_SET_MISMATCH", "delta manifests name different roots")
        root_key = base.value["rootKey"]
        base_entries = base.entry_map()
        candidate_entries = candidate.entry_map()
        operations: list[dict[str, Any]] = []
        for relative in sorted(set(base_entries) | set(candidate_entries)):
            validate_relative(relative)
            old = base_entries.get(relative)
            new = candidate_entries.get(relative)
            if _same(old, new, verifier):
                continue
            operation = "ADD" if old is None else "DELETE" if new is None else "MODIFY"
            operations.append(
                {
                    "rootKey": root_key,
                    "pathB64": path_b64(relative),
                    "pathDisplay": display_path(relative),
                    "op": operation,
                    "old": _state(old, verifier),
                    "new": _state(new, verifier),
                }
            )
        base_root_metadata = {"type": "root", **base.value["rootMetadata"]}
        candidate_root_metadata = {"type": "root", **candidate.value["rootMetadata"]}
        if _metadata_hash(base_root_metadata, verifier) != _metadata_hash(candidate_root_metadata, verifier):
            operations.insert(
                0,
                {
                    "rootKey": root_key,
                    "pathB64": "",
                    "pathDisplay": ".",
                    "op": "MODIFY",
                    "old": _state(base_root_metadata, verifier),
                    "new": _state(candidate_root_metadata, verifier),
                },
            )
        Delta._validate_operations(operations)
        summary = {
            "added": sum(item["op"] == "ADD" for item in operations),
            "modified": sum(item["op"] == "MODIFY" for item in operations),
            "deleted": sum(item["op"] == "DELETE" for item in operations),
            "files": len(operations),
        }
        value = {
            "schemaVersion": SCHEMA_VERSION,
            "baseRoot": base.root_hash,
            "candidateRoot": candidate.root_hash,
            "rootKey": root_key,
            "operations": operations,
            "summary": summary,
        }
        digest = hash_id(verifier.hash_bytes(b"worldline-delta-v1" + canonical_bytes(value)))
        return DeltaResult(value=value, delta_hash=digest)

    @staticmethod
    def compute_all(
        base: Mapping[str, CapturedManifest],
        candidate: Mapping[str, CapturedManifest],
        core: Core | None = None,
    ) -> DeltaResult:
        verifier = core or Core.shared()
        if set(base) != set(candidate):
            raise WorldlineError("ROOT_SET_MISMATCH", "base and candidate root sets differ")
        operations: list[dict[str, Any]] = []
        roots: list[dict[str, str]] = []
        for root_key in sorted(base):
            result = Delta.compute(base[root_key], candidate[root_key], verifier)
            operations.extend(result.value["operations"])
            roots.append(
                {
                    "rootKey": root_key,
                    "baseRoot": base[root_key].root_hash,
                    "candidateRoot": candidate[root_key].root_hash,
                }
            )
        operations.sort(key=lambda item: (item["rootKey"], path_from_b64(item["pathB64"])))
        Delta._validate_operations(operations)
        value = {
            "schemaVersion": SCHEMA_VERSION,
            "roots": roots,
            "operations": operations,
            "summary": {
                "added": sum(item["op"] == "ADD" for item in operations),
                "modified": sum(item["op"] == "MODIFY" for item in operations),
                "deleted": sum(item["op"] == "DELETE" for item in operations),
                "files": len(operations),
            },
        }
        return DeltaResult(
            value=value,
            delta_hash=hash_id(verifier.hash_bytes(b"worldline-multi-delta-v1" + canonical_bytes(value))),
        )

    @staticmethod
    def _validate_operations(operations: Iterable[dict[str, Any]]) -> None:
        seen: set[tuple[str, bytes]] = set()
        previous: tuple[str, bytes] | None = None
        for operation in operations:
            if operation["op"] not in {"ADD", "MODIFY", "DELETE"}:
                raise WorldlineError("INVALID_DELTA", f"invalid delta operation: {operation['op']}")
            relative = path_from_b64(operation["pathB64"])
            key = (operation["rootKey"], relative)
            if key in seen:
                raise WorldlineError("INVALID_DELTA", f"path occurs more than once: {operation['pathDisplay']}")
            if previous is not None and key < previous:
                raise WorldlineError("INVALID_DELTA", "delta operations are not sorted")
            seen.add(key)
            previous = key

    @staticmethod
    def merge(
        *,
        base: CapturedManifest,
        current: CapturedManifest,
        candidate: CapturedManifest,
        current_source: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        candidate_source: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        stage: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        core: Core | None = None,
        repository_capture: Callable[[bytes], dict[str, Any] | None] | None = None,
    ) -> MergeResult:
        verifier = core or Core.shared()
        root_keys = {base.value["rootKey"], current.value["rootKey"], candidate.value["rootKey"]}
        if len(root_keys) != 1:
            raise WorldlineError("ROOT_SET_MISMATCH", "three-way merge manifests name different roots")
        delta = Delta.compute(base, candidate, verifier)
        base_entries = base.entry_map()
        current_entries = current.entry_map()
        candidate_entries = candidate.entry_map()
        conflicts: list[dict[str, Any]] = []
        touched: set[bytes] = set()
        root_metadata_from_candidate = False

        for operation in delta.value["operations"]:
            relative = path_from_b64(operation["pathB64"])
            if not relative:
                base_root = {"type": "root", **base.value["rootMetadata"]}
                current_root = {"type": "root", **current.value["rootMetadata"]}
                if not _same(base_root, current_root, verifier):
                    conflicts.append(
                        {
                            "rootKey": operation["rootKey"],
                            "pathB64": "",
                            "pathDisplay": ".",
                            "op": operation["op"],
                            "base": _state(base_root, verifier),
                            "current": _state(current_root, verifier),
                            "candidate": operation["new"],
                        }
                    )
                else:
                    root_metadata_from_candidate = True
                continue
            touched.add(relative)
            base_entry = base_entries.get(relative)
            current_entry = current_entries.get(relative)
            if not _same(base_entry, current_entry, verifier):
                conflicts.append(
                    {
                        "rootKey": operation["rootKey"],
                        "pathB64": operation["pathB64"],
                        "pathDisplay": operation["pathDisplay"],
                        "op": operation["op"],
                        "base": _state(base_entry, verifier),
                        "current": _state(current_entry, verifier),
                        "candidate": operation["new"],
                    }
                )
        if conflicts:
            return MergeResult(staged=None, conflicts=conflicts, applied=[])

        final_entries = dict(current_entries)
        sources: dict[bytes, bytes] = {}
        current_root = os.path.abspath(os.fsencode(current_source))
        candidate_root = os.path.abspath(os.fsencode(candidate_source))
        for relative in final_entries:
            sources[relative] = current_root
        for relative in touched:
            candidate_entry = candidate_entries.get(relative)
            if candidate_entry is None:
                final_entries.pop(relative, None)
                sources.pop(relative, None)
            else:
                final_entries[relative] = candidate_entry
                sources[relative] = candidate_root

        destination = os.path.abspath(os.fsencode(stage))
        root_metadata = candidate.value["rootMetadata"] if root_metadata_from_candidate else current.value["rootMetadata"]
        Delta._materialize_merged(final_entries, sources, root_metadata, destination, verifier)
        repository = repository_capture(destination) if repository_capture is not None else candidate.value.get("repository")
        staged = Manifest.capture(
            destination,
            logical_root=base64.b64decode(current.value["rootPathB64"].encode("ascii"), validate=True),
            root_key=current.value["rootKey"],
            kind=current.value["kind"],
            core=verifier,
            repository=repository,
        )
        return MergeResult(staged=staged, conflicts=[], applied=delta.value["operations"])

    @staticmethod
    def _materialize_merged(
        entries: Mapping[bytes, dict[str, Any]],
        sources: Mapping[bytes, bytes],
        root_metadata: dict[str, Any],
        destination: bytes,
        core: Core,
    ) -> None:
        if os.path.lexists(destination):
            if not os.path.isdir(destination) or os.listdir(destination):
                raise WorldlineError("DESTINATION_NOT_EMPTY", f"merge stage is not empty: {display_path(destination)}")
        else:
            os.makedirs(destination, mode=0o700)
        directories = sorted(
            ((relative, entry) for relative, entry in entries.items() if entry["type"] == "directory"),
            key=lambda item: (item[0].count(b"/"), item[0]),
        )
        for relative, entry in directories:
            os.mkdir(os.path.join(destination, relative), mode=entry["mode"])

        hard_links: dict[str, tuple[bytes, bytes]] = {}
        for relative, entry in sorted(entries.items()):
            if entry["type"] != "file":
                continue
            source_root = sources[relative]
            source_path = os.path.join(source_root, relative)
            target_path = os.path.join(destination, relative)
            group = entry["hardLinkGroup"]
            if group is not None and group in hard_links:
                first_target, first_source = hard_links[group]
                if first_source != source_root:
                    raise WorldlineError(
                        "HARDLINK_GROUP_MIXED",
                        f"three-way merge mixed hard-link ownership at {entry['pathDisplay']}",
                    )
                os.link(first_target, target_path, follow_symlinks=False)
            else:
                with open(source_path, "rb", buffering=0) as input_stream, open(target_path, "xb", buffering=0) as output_stream:
                    shutil.copyfileobj(input_stream, output_stream, length=1024 * 1024)
                    output_stream.flush()
                    os.fsync(output_stream.fileno())
                if hash_id(core.hash_file(target_path)) != entry["contentHash"]:
                    raise WorldlineError("COPY_VERIFICATION_FAILED", f"merge source changed: {entry['pathDisplay']}")
                if group is not None:
                    hard_links[group] = (target_path, source_root)
            Manifest._apply_metadata(target_path, entry, symlink=False)

        for relative, entry in sorted(entries.items()):
            if entry["type"] != "symlink":
                continue
            target = base64.b64decode(entry["targetB64"].encode("ascii"), validate=True)
            target_path = os.path.join(destination, relative)
            os.symlink(target, target_path)
            Manifest._apply_metadata(target_path, entry, symlink=True)

        for relative, entry in reversed(directories):
            Manifest._apply_metadata(os.path.join(destination, relative), entry, symlink=False)
        Manifest._apply_metadata(destination, root_metadata, symlink=False)
