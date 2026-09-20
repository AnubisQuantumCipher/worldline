from __future__ import annotations

import json
import shutil
from pathlib import Path
import uuid

from .checkpoint import CheckpointManager
from .core import Core, hash_id
from .delta import Delta
from .errors import WorldlineError
from .manifest import CapturedManifest, Manifest
from .model import World, WorldState
from .paths import WorldlinePaths
from .store import StateStore
from .transaction import CollapseTransaction


class ReturnManager:
    def __init__(
        self,
        paths: WorldlinePaths,
        store: StateStore,
        checkpoint: CheckpointManager,
        transaction: CollapseTransaction,
        *,
        core: Core | None = None,
    ) -> None:
        self.paths = paths
        self.store = store
        self.checkpoint = checkpoint
        self.transaction = transaction
        self.core = core or Core.shared()

    def select(self, value: str | None) -> World:
        if value is not None:
            selected = self.store.world(value)
        else:
            current = self.store.prime()
            if current is None or current.parent_instance is None:
                raise WorldlineError("NO_RETURN_POINT", "no checkpoint precedes current PRIME")
            selected = self.store.world(current.parent_instance)
        if selected.state not in {
            WorldState.ARCHIVED,
            WorldState.COLLAPSED,
            WorldState.VALID,
        }:
            raise WorldlineError("INVALID_RETURN_POINT", f"world cannot be returned: {selected.state.value}")
        return selected

    def prepare_candidate(self, selected: World) -> World:
        frozen = self.checkpoint.freeze()
        identifier = str(uuid.uuid4())
        payload = self.paths.worlds / identifier / "payload"
        manifests_directory = payload / "manifests"
        manifests_directory.mkdir(mode=0o700, parents=True)
        selected_payload = Path(selected.payload_path)
        roots = self.store.roots()
        base_manifests: dict[str, CapturedManifest] = {}
        selected_manifests = self.return_point_manifests(selected, roots)
        for root in roots:
            root_key = root["root_key"]
            base_manifest = Manifest.load(frozen.payload / "manifests" / f"{root_key}.json", self.core)
            selected_manifest = selected_manifests[root_key]
            selected_source = selected_payload / root_key
            Manifest.materialize(selected_manifest, selected_source, payload / root_key, core=self.core)
            selected_manifest.save(manifests_directory / f"{root_key}.json")
            base_manifests[root_key] = base_manifest
        for name in ("environment.json", "evidence.json", "agent.json"):
            source = selected_payload / "manifests" / name
            if source.is_file():
                shutil.copy2(source, manifests_directory / name)
        delta = Delta.compute_all(base_manifests, selected_manifests, self.core)
        alias = f"return-{selected.alias}-{identifier[:8]}"
        world = World.create(
            alias=alias,
            parent_instance=frozen.parent_instance,
            parent_content=frozen.parent_content,
            cause=f"Return to {selected.alias}",
            actor="worldline",
            payload_path=payload,
            base_payload_path=frozen.payload,
            base_root=frozen.state_root,
            root_set_hash=frozen.root_set_hash,
            mission_hash=hash_id(self.core.hash_bytes(b"worldline-return-v1" + selected.instance_id.encode("ascii"))),
            workspace=selected.workspace,
        )
        world.instance_id = identifier
        world.components = {
            **Manifest.component_roots(selected_manifests.values(), self.core),
            "environment": selected.components["environment"],
            "evidence": selected.components["evidence"],
        }
        world.evidence = selected.evidence
        world.delta_hash = delta.delta_hash
        world.delta = {**delta.value["summary"], "files": delta.value["operations"]}
        world.transition(WorldState.FINALIZING, self.core)
        world.establish_identity(self.core)
        world.transition(WorldState.VALID, self.core)
        self.store.insert_world(world)
        return world

    def return_point_manifests(self, selected: World, roots: list[dict]) -> dict[str, CapturedManifest]:
        """Manifests that describe the return point as it is on disk, verified.

        A checkpoint's stored manifest describes it as it was committed. A checkpoint that has
        since been live is legitimately different: the project wrote generated outputs into it,
        the operator edited it, tools left artifacts. What ``return`` restores is the reality at
        the instant that checkpoint was displaced, and every committed exchange recorded exactly
        that as its receipt's ``beforeRoot``. So: accept the stored manifest when it still
        matches; otherwise capture the payload fresh and accept it only if it hashes to a
        ``beforeRoot`` some committed receipt recorded. Anything else is a payload that changed
        after it left reality, and that is refused.
        """
        selected_payload = Path(selected.payload_path)
        stored: dict[str, CapturedManifest] = {}
        stale_reason: str | None = None
        for root in roots:
            root_key = root["root_key"]
            source = selected_payload / root_key
            if not source.is_dir():
                raise WorldlineError("RETURN_POINT_INCOMPLETE", f"selected checkpoint does not contain root {root_key}")
            manifest_path = selected_payload / "manifests" / f"{root_key}.json"
            if not manifest_path.is_file():
                stale_reason = f"no stored manifest for root {root_key}"
                break
            manifest = Manifest.load(manifest_path, self.core)
            try:
                Manifest.verify_content(manifest, source, self.core)
            except WorldlineError as exc:
                if exc.code != "PAYLOAD_INTEGRITY_FAILED":
                    raise
                stale_reason = exc.message
                break
            stored[root_key] = manifest
        if stale_reason is None:
            return stored
        fresh: dict[str, CapturedManifest] = {}
        for root in roots:
            root_key = root["root_key"]
            fresh[root_key] = Manifest.capture(
                selected_payload / root_key,
                logical_root=bytes(root["path"]),
                root_key=root_key,
                kind=root["kind"],
                core=self.core,
            )
        observed = Manifest.root_set_hash(fresh.values(), self.core)
        displacing = self._receipt_with_before_root(observed)
        if displacing is None:
            raise WorldlineError(
                "PAYLOAD_INTEGRITY_FAILED",
                "return point changed after it was displaced: it matches neither its stored manifest "
                "nor the pre-exchange state any committed receipt recorded",
                {"returnPoint": selected.alias, "storedManifest": stale_reason, "observedRoot": observed},
            )
        return fresh

    def _receipt_with_before_root(self, root_hash: str) -> str | None:
        for row in reversed(self.store.receipts()):
            try:
                receipt = json.loads(Path(row["canonical_path"]).read_text(encoding="utf-8"))
            except (OSError, ValueError, KeyError):
                continue
            if isinstance(receipt, dict) and receipt.get("beforeRoot") == root_hash:
                return str(receipt.get("receiptId") or row.get("transaction_id"))
        return None

    def execute(self, value: str | None = None) -> dict[str, object]:
        selected = self.select(value)
        candidate = self.prepare_candidate(selected)
        prepared = self.transaction.prepare(candidate.instance_id, kind="return")
        return self.transaction.commit(prepared.transaction_id)
