from __future__ import annotations

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
        base_manifests: dict[str, CapturedManifest] = {}
        selected_manifests: dict[str, CapturedManifest] = {}
        for root in self.store.roots():
            root_key = root["root_key"]
            logical = bytes(root["path"])
            base_manifest = Manifest.load(frozen.payload / "manifests" / f"{root_key}.json", self.core)
            selected_manifest_path = selected_payload / "manifests" / f"{root_key}.json"
            selected_source = selected_payload / root_key
            if not selected_source.is_dir():
                raise WorldlineError(
                    "RETURN_POINT_INCOMPLETE",
                    f"selected checkpoint does not contain root {root_key}",
                )
            if selected_manifest_path.is_file():
                selected_manifest = Manifest.load(selected_manifest_path, self.core)
                Manifest.verify_content(selected_manifest, selected_source, self.core)
            else:
                selected_manifest = Manifest.capture(
                    selected_source,
                    logical_root=logical,
                    root_key=root_key,
                    kind=root["kind"],
                    core=self.core,
                )
            Manifest.materialize(selected_manifest, selected_source, payload / root_key, core=self.core)
            selected_manifest.save(manifests_directory / f"{root_key}.json")
            base_manifests[root_key] = base_manifest
            selected_manifests[root_key] = selected_manifest
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

    def execute(self, value: str | None = None) -> dict[str, object]:
        selected = self.select(value)
        candidate = self.prepare_candidate(selected)
        prepared = self.transaction.prepare(candidate.instance_id, kind="return")
        return self.transaction.commit(prepared.transaction_id)
