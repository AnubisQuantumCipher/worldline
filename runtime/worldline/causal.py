from __future__ import annotations

import difflib
import fnmatch
import json
import os
import time
from pathlib import Path
from typing import Any

from . import SCHEMA_VERSION
from .errors import NotFound, WorldlineError
from .linux.git import GitAdapter
from .manifest import Manifest, path_b64, path_from_b64
from .model import WorldState, World
from .project import ProjectConfig
from .store import StateStore


def claims_of(event: dict[str, Any], default_actor: str) -> dict[str, Any]:
    """The actor, tool and reason an event records, with who made those claims (1.9.2):
    `agent:<adapter>` for anything an agent's stdout supplied (a file-delta carries its source
    event's origin), `worldline` for WORLDLINE's own records, and `not recorded (before 1.9.2)`
    for events chained before origins were recorded, which cannot be authenticated now."""
    origin = event.get("origin")
    if origin == "agent":
        label = f"agent:{event.get('adapter') or 'unknown'}"
    elif origin == "worldline":
        label = "worldline"
    else:
        label = "not recorded (before 1.9.2)"
    return {
        "origin": label,
        "actor": event.get("actor", default_actor),
        "tool": event.get("tool"),
        "reason": event.get("reason") or "not supplied by adapter",
    }


class CausalIndexer:
    def __init__(self, store: StateStore) -> None:
        self.store = store

    def index(self, world: World, project: ProjectConfig) -> int:
        base = Path(world.base_payload_path)
        candidate = Path(world.payload_path)
        registered = self.store.roots()
        base_manifests = {}
        actual_base_manifests = {}
        for root in registered:
            key = root["root_key"]
            manifest_path = base / "manifests" / f"{key}.json"
            if manifest_path.is_file():
                manifest = Manifest.load(manifest_path, self.store.core)
                self._verify_base(manifest, base / key, key)
            else:
                # Finalization also accepts checkpoints without saved manifests.
                # Acquire the same complete manifest from the actual base, using
                # its original repository capture recipe. Do not mutate a shared
                # checkpoint or silently omit its causal index.
                source = base / key
                repository = GitAdapter(self.store.core).capture(source) if root["kind"] == "repo" else None
                manifest = Manifest.capture(source, logical_root=bytes(root["path"]),
                    root_key=key, kind=root["kind"], core=self.store.core,
                    repository=repository)
                actual_base_manifests[key] = manifest
            base_manifests[key] = manifest
        observed_base_root = Manifest.root_set_hash(base_manifests.values(), self.store.core)
        if observed_base_root != world.base_root:
            raise WorldlineError("BASE_ROOT_MISMATCH",
                "causal indexing base checkpoint differs from its claimed base",
                {"claimed": world.base_root, "actual": observed_base_root})
        # Preserve the saved-manifest identity refusal above before acquiring
        # additional facts. Content verification alone omits metadata and repo
        # facts; compare a complete capture of each actual base as well.
        for root in registered:
            key = root["root_key"]
            if key in actual_base_manifests:
                continue
            source = base / key
            repository = GitAdapter(self.store.core).capture(source) if root["kind"] == "repo" else None
            actual_base_manifests[key] = Manifest.capture(source, logical_root=bytes(root["path"]),
                root_key=key, kind=root["kind"], core=self.store.core,
                repository=repository)
        actual_base_root = Manifest.root_set_hash(actual_base_manifests.values(), self.store.core)
        if actual_base_root != world.base_root:
            raise WorldlineError("BASE_ROOT_MISMATCH",
                "causal indexing actual base checkpoint differs from its claimed base",
                {"claimed": world.base_root, "actual": actual_base_root})
        candidate_manifests = {
            root["root_key"]: Manifest.load(candidate / "manifests" / f"{root['root_key']}.json", self.store.core)
            for root in registered
        }
        prior_events = self.store.causal_events_for_world(world.instance_id)
        ranges: list[dict[str, Any]] = []
        indexed = 0
        for operation in world.delta.get("files", []):
            relative = path_from_b64(operation["pathB64"])
            if not relative:
                continue
            root_key = operation["rootKey"]
            display = operation["pathDisplay"]
            source_event = self._source_event(prior_events, root_key, operation["pathB64"])
            source_value = {} if source_event is None else source_event["event"]
            evidence = [
                check
                for check in world.evidence.get("checks", [])
                if any(fnmatch.fnmatchcase(display, pattern) for pattern in check.get("covers", []))
            ]
            event: dict[str, Any] = {
                "schemaVersion": SCHEMA_VERSION,
                "worldInstance": world.instance_id,
                "kind": "file-delta",
                "actor": source_value.get("actor", world.actor),
                "tool": source_value.get("tool"),
                "reason": source_value.get("reason"),
                "sourceEvent": None if source_event is None else source_event["event_id"],
                "rootKey": root_key,
                "pathB64": operation["pathB64"],
                "pathDisplay": display,
                "operation": operation["op"],
                "evidence": evidence,
                # Who made the claims this record carries (actor, tool, reason): the source
                # event's origin, so an agent's statement stays labelled as the agent's (1.9.2).
                **({"origin": source_value["origin"]} if source_value.get("origin") else {}),
                **({"adapter": source_value["adapter"]} if source_value.get("adapter") else {}),
            }
            link = self.store.append_causal_event(event, worldline_authored=True)
            line_ranges = self._ranges(
                operation,
                base_manifests[root_key],
                candidate_manifests[root_key],
                base / root_key,
                candidate / root_key,
            )
            for start, end, granularity in line_ranges:
                ranges.append(
                    {
                        "worldInstance": world.instance_id,
                        "eventId": link["eventId"],
                        "rootKey": root_key,
                        "pathB64": operation["pathB64"],
                        "pathDisplay": display,
                        "startLine": start,
                        "endLine": end,
                        "granularity": granularity,
                    }
                )
            indexed += 1
        if ranges:
            self.store.add_line_ranges(ranges)
        return indexed

    def _verify_base(self, manifest, source: Path, root_key: str) -> None:
        # Match Finalizer's checkpoint verification and original transient-read
        # retry policy before any causal event is appended. Saved manifest bytes
        # alone do not establish that the actual base content is still present.
        last: WorldlineError | None = None
        for attempt in range(3):
            try:
                Manifest.verify_content(manifest, source, self.store.core)
                return
            except WorldlineError as exc:
                last = exc
                if not exc.code.startswith("CORE_"):
                    break
                time.sleep(0.5 * (attempt + 1))
        assert last is not None
        raise WorldlineError(
            "BASE_CHECKPOINT_UNVERIFIED",
            f"the checkpoint this world was forked from could not be verified for root {root_key}: {last.message}",
            {"rootKey": root_key, "base": str(source), "cause": last.as_dict()},
        )

    @staticmethod
    def _source_event(
        events: list[dict[str, Any]], root_key: str, encoded_path: str
    ) -> dict[str, Any] | None:
        matching = [
            item
            for item in events
            if item.get("path_b64") == encoded_path and item["event"].get("rootKey") == root_key
        ]
        if matching:
            return matching[-1]
        invocation = [item for item in events if item["kind"] in {"agent-invocation", "agent-invocation-result"}]
        return invocation[-1] if invocation else None

    @staticmethod
    def _ranges(
        operation: dict[str, Any],
        base_manifest,
        candidate_manifest,
        base_root: Path,
        candidate_root: Path,
    ) -> list[tuple[int, int, str]]:
        relative = path_from_b64(operation["pathB64"])
        base_entry = base_manifest.entry_map().get(relative)
        candidate_entry = candidate_manifest.entry_map().get(relative)
        if candidate_entry is None or candidate_entry.get("type") != "file":
            return [(1, 1, "file")]
        candidate_bytes = (candidate_root / os.fsdecode(relative)).read_bytes()
        try:
            candidate_lines = candidate_bytes.decode("utf-8", "strict").splitlines()
        except UnicodeDecodeError:
            return [(1, 1, "file")]
        if base_entry is None or base_entry.get("type") != "file":
            return [(1, max(1, len(candidate_lines)), "line")]
        base_bytes = (base_root / os.fsdecode(relative)).read_bytes()
        try:
            base_lines = base_bytes.decode("utf-8", "strict").splitlines()
        except UnicodeDecodeError:
            return [(1, 1, "file")]
        result: list[tuple[int, int, str]] = []
        matcher = difflib.SequenceMatcher(a=base_lines, b=candidate_lines, autojunk=False)
        for tag, _i1, _i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                continue
            start = max(1, j1 + 1)
            end = max(start, j2)
            result.append((start, end, "line"))
        return result or [(1, max(1, len(candidate_lines)), "file")]

    def why(self, path_value: str, line: int) -> dict[str, Any]:
        if line < 1:
            raise WorldlineError("INVALID_LINE", "line number must be positive")
        roots = self.store.roots()
        supplied = Path(path_value)
        if not supplied.is_absolute():
            primary = next((root for root in roots if root["primary_root"]), None)
            if primary is None:
                raise WorldlineError("NO_PRIMARY_ROOT", "no primary root is registered")
            supplied = Path(os.fsdecode(bytes(primary["path"]))) / supplied
        absolute = supplied.absolute()
        selected_root = None
        relative = None
        for root in roots:
            logical = Path(os.fsdecode(bytes(root["path"]))).absolute()
            try:
                relative = absolute.relative_to(logical)
            except ValueError:
                continue
            selected_root = root
            break
        if selected_root is None or relative is None:
            raise NotFound("managed path", path_value)
        if ".." in relative.parts:
            # Lexical, so `root/../../x` would otherwise name a file outside every root.
            raise NotFound("managed path", path_value)
        encoded = path_b64(os.fsencode(relative))
        root_key = selected_root["root_key"]
        live_root = Path(os.fsdecode(self.store.paths.root_source(selected_root)))
        live_line = self._line_text(live_root, relative, line)
        prime = self.store.prime()
        # Every world that touched this line has a range row, archived siblings included, and
        # the newest ordinal used to win: a lane that finished last but was never collapsed was
        # credited with a line in PRIME. Only a world in effect can have written PRIME — one that
        # collapsed, or PRIME itself — and its copy of the line must still be what PRIME holds.
        chosen_row = None
        bystanders: list[str] = []
        for candidate_row in self.store.line_events(root_key, encoded, line):
            candidate = self.store.world(candidate_row["world_instance"])
            in_effect = candidate.state is WorldState.COLLAPSED or (prime is not None and candidate.instance_id == prime.instance_id)
            if not in_effect or candidate.payload_pruned:
                bystanders.append(candidate.alias)
                continue
            if live_line is not None and self._line_text(Path(candidate.payload_path) / root_key, relative, line) != live_line:
                bystanders.append(candidate.alias)
                continue
            chosen_row = candidate_row
            break
        if chosen_row is None:
            if live_line is None:
                raise NotFound("causal event", f"{path_value}:{line}")
            return self._checkpoint_attribution(path_value, line, prime, bystanders)
        row = chosen_row
        event = json.loads(self.store.read_canonical("events", row["canonical_path"]).decode("utf-8"))
        world = self.store.world(row["world_instance"])
        ancestors: list[dict[str, Any]] = []
        current = world
        seen: set[str] = set()
        while current.instance_id not in seen:
            seen.add(current.instance_id)
            ancestors.append(
                {
                    "alias": "PRIME" if current.alias.startswith("prime-") else current.alias,
                    "instanceId": current.instance_id,
                    "contentId": current.content_id,
                }
            )
            if current.parent_instance is None:
                break
            current = self.store.world(current.parent_instance)
        receipt = None if world.content_id is None else self.store.receipt_for_candidate(world.content_id)
        claims = claims_of(event, world.actor)
        return {
            "path": path_value,
            "line": line,
            "world": world.alias,
            "mission": world.cause,
            # What an agent said about the change, kept apart from WORLDLINE's facts and labelled
            # with who said it (1.9.2, OB-091).
            "claims": claims,
            # Preserve the original public why fields as aliases of the same
            # explicitly labelled claims; these do not authenticate an agent.
            "claimOrigin": claims["origin"],
            "actor": claims["actor"],
            "tool": claims["tool"],
            "reason": claims["reason"],
            "granularity": row["granularity"],
            "evidence": event.get("evidence", []),
            "ancestors": ancestors,
            "receipt": None if receipt is None else receipt["receipt"],
            "eventId": row["event_id"],
            "attribution": "world",
            # Worlds with a NEWER event on this line that are not in effect (archived siblings,
            # pruned worlds, or a world whose copy of the line no longer matches PRIME). They are
            # named, never credited: attribution stays with the world whose text PRIME holds.
            "bystanders": bystanders,
        }

    @staticmethod
    def _line_text(base: Path, relative: bytes, line: int) -> str | None:
        target = base / os.fsdecode(relative)
        try:
            if not target.is_file() or target.is_symlink():
                return None
            if base.resolve() not in target.resolve().parents:
                return None
            lines = target.read_bytes().decode("utf-8", "strict").splitlines()
        except (OSError, UnicodeDecodeError):
            return None
        return lines[line - 1] if 0 < line <= len(lines) else None

    def _checkpoint_attribution(self, path_value: str, line: int, prime, bystanders: list[str]) -> dict[str, Any]:
        ancestors: list[dict[str, Any]] = []
        current = prime
        seen: set[str] = set()
        while current is not None and current.instance_id not in seen:
            seen.add(current.instance_id)
            ancestors.append({"alias": "PRIME" if current.alias.startswith("prime-") else current.alias, "instanceId": current.instance_id, "contentId": current.content_id})
            current = self.store.world(current.parent_instance) if current.parent_instance else None
        claims = {"origin": "worldline", "actor": "worldline", "tool": None,
                  "reason": "no world in PRIME's lineage changed this line; it dates from a checkpoint (registration or return)"}
        return {
            "path": path_value,
            "line": line,
            "world": "PRIME",
            "mission": None,
            "claims": claims,
            "claimOrigin": claims["origin"],
            "actor": claims["actor"],
            "tool": claims["tool"],
            "reason": claims["reason"],
            "granularity": "checkpoint",
            "evidence": [],
            "ancestors": ancestors,
            "receipt": None,
            "eventId": None,
            "attribution": "checkpoint",
            "bystanders": bystanders,
        }
