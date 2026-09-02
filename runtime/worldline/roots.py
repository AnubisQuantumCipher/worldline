from __future__ import annotations

from contextlib import nullcontext
from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import stat
import uuid
from typing import Any, Iterable, Sequence

from .canonical import atomic_write_json, fsync_directory
from .core import Core, hash_id
from .environment import EnvironmentCapture, evidence_manifest
from .errors import NotFound, WorldlineError
from .linux.atomic import AtomicExchange
from .linux.git import GitAdapter
from .linux.inotify import InotifyWatcher
from .manifest import CapturedManifest, Manifest, display_path
from .model import WorldState
from .paths import WorldlinePaths
from .prime import Generation, PrimeManager
from .store import StateStore


@dataclass(frozen=True, slots=True)
class RootCandidate:
    raw_path: bytes
    display_path: str
    kind: str
    root_key: str
    device: int
    primary: bool
    manifest: CapturedManifest


class RootManager:
    def __init__(
        self,
        paths: WorldlinePaths,
        store: StateStore,
        *,
        core: Core | None = None,
        watcher: InotifyWatcher | None = None,
        toolchains: Sequence[str] = ("git", "python3", "gprbuild", "gnatprove", "bwrap", "systemd-run"),
    ) -> None:
        self.paths = paths
        self.store = store
        self.core = core or Core.shared()
        self.watcher = watcher
        self.toolchains = tuple(toolchains)
        self.git = GitAdapter(self.core)
        self.environment = EnvironmentCapture(self.core)
        self.prime = PrimeManager(paths, store, self.core)
        self.atomic = AtomicExchange()

    def _assert_root_set_mutable(self) -> None:
        nonterminal = self.store.nonterminal_worlds()
        if nonterminal:
            raise WorldlineError(
                "ROOT_SET_BUSY",
                "root set cannot change while a child world is nonterminal",
                {"worlds": [world.alias for world in nonterminal]},
            )
        transactions = self.store.transactions_in_state(("PREPARED", "AUTHORIZED"))
        if transactions:
            raise WorldlineError(
                "ROOT_SET_BUSY",
                "root set cannot change while a transaction is active",
                {"transactions": [item["transaction_id"] for item in transactions]},
            )

    @staticmethod
    def _overlap(first: bytes, second: bytes) -> bool:
        try:
            common = os.path.commonpath((first, second))
        except ValueError:
            return False
        return common in (first, second)

    def _default_kind(self, raw_path: bytes) -> str:
        git_marker = os.path.join(raw_path, b".git")
        if os.path.isdir(git_marker) or os.path.isfile(git_marker):
            return "repo"
        config_home = os.path.abspath(os.fsencode(self.paths.config.parent))
        if self._overlap(config_home, raw_path) and os.path.commonpath((config_home, raw_path)) == config_home:
            return "config"
        return "filesystem"

    def _root_key(self, raw_path: bytes) -> str:
        return self.core.hash_bytes(b"worldline-root-key-v1" + raw_path).hex()

    def validate(
        self,
        roots: Sequence[str | bytes | os.PathLike[str] | os.PathLike[bytes]],
        *,
        kind: str | None = None,
        primary: str | bytes | os.PathLike[str] | os.PathLike[bytes] | None = None,
    ) -> list[RootCandidate]:
        if not roots:
            raise WorldlineError("NO_ROOTS", "at least one root is required")
        if kind is not None and kind not in {"repo", "config", "filesystem"}:
            raise WorldlineError("INVALID_ROOT_KIND", f"unsupported root kind: {kind}")
        self.paths.ensure()
        data_device = self.paths.data.stat().st_dev
        existing = [bytes(item["path"]) for item in self.store.roots()]
        raw_primary = None if primary is None else os.path.abspath(os.fsencode(primary))
        normalized: list[tuple[bytes, str]] = []
        for supplied in roots:
            raw = os.path.abspath(os.fsencode(supplied))
            try:
                info = os.lstat(raw)
            except FileNotFoundError as exc:
                raise WorldlineError("ROOT_NOT_FOUND", f"root does not exist: {display_path(raw)}") from exc
            if stat.S_ISLNK(info.st_mode):
                raise WorldlineError("ROOT_IS_SYMLINK", f"register the real directory, not a symlink: {display_path(raw)}")
            if not stat.S_ISDIR(info.st_mode):
                raise WorldlineError("UNSUPPORTED_ROOT", f"root is not a directory: {display_path(raw)}")
            if info.st_dev != data_device:
                raise WorldlineError(
                    "CROSS_FILESYSTEM_ROOT",
                    f"root and WORLDLINE data store are on different devices: {display_path(raw)}",
                    {"rootDevice": info.st_dev, "dataDevice": data_device},
                )
            normalized.append((raw, kind or self._default_kind(raw)))

        if raw_primary is not None and raw_primary not in {raw for raw, _kind in normalized}:
            raise WorldlineError("INVALID_PRIMARY_ROOT", "--primary must name one of the registered roots")
        if raw_primary is None and not self.store.roots():
            raw_primary = normalized[0][0]

        protected = [
            os.path.abspath(os.fsencode(path))
            for path in (self.paths.data, self.paths.state, self.paths.runtime, self.paths.config)
        ]
        seen = list(existing)
        candidates: list[RootCandidate] = []
        for raw, selected_kind in normalized:
            if any(self._overlap(raw, other) for other in seen):
                raise WorldlineError("OVERLAPPING_ROOT", f"managed roots overlap: {display_path(raw)}")
            if any(self._overlap(raw, internal) for internal in protected):
                raise WorldlineError("WORLDLINE_SELF_CAPTURE", f"root overlaps WORLDLINE state: {display_path(raw)}")
            repository = self.git.capture(raw) if selected_kind == "repo" else None
            root_key = self._root_key(raw)
            manifest = Manifest.capture(
                raw,
                logical_root=raw,
                root_key=root_key,
                kind=selected_kind,
                core=self.core,
                repository=repository,
            )
            candidates.append(
                RootCandidate(
                    raw_path=raw,
                    display_path=display_path(raw),
                    kind=selected_kind,
                    root_key=root_key,
                    device=os.lstat(raw).st_dev,
                    primary=raw == raw_primary,
                    manifest=manifest,
                )
            )
            seen.append(raw)
        return candidates

    def register(
        self,
        roots: Sequence[str | bytes | os.PathLike[str] | os.PathLike[bytes]],
        *,
        kind: str | None = None,
        primary: str | bytes | os.PathLike[str] | os.PathLike[bytes] | None = None,
        confirmed: bool = False,
    ) -> dict[str, Any]:
        self._assert_root_set_mutable()
        candidates = self.validate(roots, kind=kind, primary=primary)
        summary = [{"path": item.display_path, "kind": item.kind, "primary": item.primary} for item in candidates]
        if not confirmed:
            raise WorldlineError(
                "CONFIRMATION_REQUIRED",
                "root registration moves the exact roots behind WORLDLINE live mappings",
                {"roots": summary},
            )

        generation_id = str(uuid.uuid4())
        generation_payload = self.prime.new_generation(generation_id=generation_id)
        manifests_directory = generation_payload.parent / "manifests"
        manifests_directory.mkdir(mode=0o700)
        for candidate in candidates:
            candidate.manifest.save(manifests_directory / f"{candidate.root_key}.json")

        moved: list[tuple[RootCandidate, bytes, bytes]] = []
        context = self.watcher.owned_writes() if self.watcher is not None else nullcontext()
        try:
            with context:
                for candidate in candidates:
                    target = os.fsencode(generation_payload / candidate.root_key)
                    live = os.fsencode(self.paths.live / candidate.root_key)
                    os.rename(candidate.raw_path, target)
                    try:
                        os.symlink(target, live)
                        os.symlink(live, candidate.raw_path)
                    except BaseException:
                        if os.path.lexists(candidate.raw_path):
                            os.unlink(candidate.raw_path)
                        if os.path.lexists(live):
                            os.unlink(live)
                        os.rename(target, candidate.raw_path)
                        raise
                    fsync_directory(Path(os.fsdecode(os.path.dirname(candidate.raw_path))))
                    fsync_directory(self.paths.live)
                    moved.append((candidate, target, live))
        except BaseException:
            self._rollback_registration(moved)
            shutil.rmtree(generation_payload.parent, ignore_errors=True)
            raise

        previous_primary = next((item["root_key"] for item in self.store.roots() if item["primary_root"]), None)
        explicit_primary = next((item.root_key for item in candidates if item.primary), None)
        try:
            with self.store.transaction() as connection:
                if explicit_primary is not None:
                    connection.execute("UPDATE roots SET primary_root=0 WHERE primary_root=1")
                for candidate, _target, _live in moved:
                    self.store.add_root(
                        root_key=candidate.root_key,
                        raw_path=candidate.raw_path,
                        display_path=candidate.display_path,
                        kind=candidate.kind,
                        device=candidate.device,
                        primary=candidate.primary,
                        generation_id=generation_id,
                        manifest_root=candidate.manifest.root_hash,
                    )
        except BaseException:
            self._rollback_registration(moved)
            shutil.rmtree(generation_payload.parent, ignore_errors=True)
            raise

        try:
            world = self._publish_generation(
                generation_id=generation_id,
                generation_payload=generation_payload,
                cause="Register managed roots",
                supplied_manifests=self._capture_all(manifests_directory),
            )
        except BaseException:
            with self.store.transaction() as connection:
                for candidate in candidates:
                    connection.execute("DELETE FROM roots WHERE root_key=?", (candidate.root_key,))
                if previous_primary is not None:
                    connection.execute("UPDATE roots SET primary_root=1 WHERE root_key=?", (previous_primary,))
            self._rollback_registration(moved)
            shutil.rmtree(generation_payload.parent, ignore_errors=True)
            raise
        return {"roots": summary, "prime": world.content_id, "generation": generation_id}

    def _rollback_registration(self, moved: Iterable[tuple[RootCandidate, bytes, bytes]]) -> None:
        for candidate, target, live in reversed(list(moved)):
            if os.path.islink(candidate.raw_path):
                os.unlink(candidate.raw_path)
            if os.path.lexists(live):
                os.unlink(live)
            if os.path.lexists(target) and not os.path.lexists(candidate.raw_path):
                os.rename(target, candidate.raw_path)

    def _capture_all(self, manifests_directory: Path) -> list[CapturedManifest]:
        manifests: list[CapturedManifest] = []
        payload = manifests_directory.parent / "payload"
        internal_manifests = payload / "manifests"
        internal_manifests.mkdir(mode=0o700, exist_ok=True)
        recorded = {item["root_key"]: item for item in self.store.roots()}
        for root_key, root in sorted(recorded.items()):
            logical = bytes(root["path"])
            source = os.path.realpath(logical)
            repository = self.git.capture(source) if root["kind"] == "repo" else None
            manifest = Manifest.capture(
                source,
                logical_root=logical,
                root_key=root_key,
                kind=root["kind"],
                core=self.core,
                repository=repository,
            )
            target = payload / root_key
            if not target.exists():
                Manifest.materialize(manifest, source, target, core=self.core)
            manifest.save(manifests_directory / f"{root_key}.json")
            manifest.save(internal_manifests / f"{root_key}.json")
            self.store.update_root_generation(root_key, root["generation_id"], manifest.root_hash)
            manifests.append(manifest)
        return manifests

    def capture_current(self, *, generation_id: str | None = None) -> tuple[str, Path, list[CapturedManifest]]:
        identifier = generation_id or str(uuid.uuid4())
        payload = self.prime.new_generation(generation_id=identifier)
        manifests_directory = payload.parent / "manifests"
        manifests_directory.mkdir(mode=0o700)
        capture = lambda: self._capture_all(manifests_directory)
        if self.watcher is not None:
            from .linux.inotify import stable_capture

            manifests = stable_capture(self.watcher, capture)
        else:
            manifests = capture()
        return identifier, payload, manifests

    def _publish_generation(
        self,
        *,
        generation_id: str,
        generation_payload: Path,
        cause: str,
        supplied_manifests: list[CapturedManifest] | None = None,
    ):
        manifests = supplied_manifests
        if manifests is None:
            manifests_directory = generation_payload.parent / "manifests"
            manifests = self._capture_all(manifests_directory)
        roots = {item["root_key"]: item for item in self.store.roots()}
        dependency_roots = [
            (root_key, os.path.realpath(bytes(root["path"]))) for root_key, root in sorted(roots.items())
        ]
        evidence = evidence_manifest([], self.core)
        agent = {"adapter": None, "missionHash": None, "sessionReference": None}
        environment = self.environment.capture(
            processes=[],
            toolchains=self.toolchains,
            dependency_roots=dependency_roots,
            agent=agent,
            evidence=evidence,
        )
        state_directory = generation_payload / "manifests"
        state_directory.mkdir(mode=0o700, exist_ok=True)
        environment.save(state_directory / "environment.json")
        atomic_write_json(state_directory / "evidence.json", evidence)
        atomic_write_json(state_directory / "agent.json", agent)
        components = Manifest.component_roots(manifests, self.core)
        root_set = self.prime.root_set_hash(self.store.roots())
        return self.prime.publish_checkpoint(
            generation=Generation(
                generation_id=generation_id,
                payload=generation_payload,
                root_set_hash=root_set,
                state_root=Manifest.root_set_hash(manifests, self.core),
                component_roots=components,
            ),
            cause=cause,
            environment_root=environment.root_hash,
            evidence_root=evidence["root"],
            workspace=environment.value["workspace"],
        )

    def reconcile(self, *, cause: str = "External managed-root change"):
        if not self.store.get_meta("dirty", False):
            return self.store.prime()
        generation_id, payload, manifests = self.capture_current()
        return self._publish_generation(
            generation_id=generation_id,
            generation_payload=payload,
            cause=cause,
            supplied_manifests=manifests,
        )

    def remove(self, value: str, *, confirmed: bool = False) -> dict[str, Any]:
        self._assert_root_set_mutable()
        root = self.store.root(value)
        logical = bytes(root["path"])
        source = os.path.realpath(logical)
        if not os.path.islink(logical):
            raise WorldlineError("LIVE_MAPPING_BROKEN", f"managed root is not a WORLDLINE symlink: {root['display_path']}")
        repository = self.git.capture(source) if root["kind"] == "repo" else None
        manifest = Manifest.capture(
            source,
            logical_root=logical,
            root_key=root["root_key"],
            kind=root["kind"],
            core=self.core,
            repository=repository,
        )
        if not confirmed:
            raise WorldlineError(
                "CONFIRMATION_REQUIRED",
                "root removal materializes the current payload back at the exact path",
                {"roots": [{"path": root["display_path"], "kind": root["kind"]}]},
            )

        stage = os.path.join(os.path.dirname(logical), f".worldline-materialize-{uuid.uuid4()}".encode("ascii"))
        Manifest.materialize(manifest, source, stage, core=self.core)
        with (self.watcher.owned_writes() if self.watcher is not None else nullcontext()):
            self.atomic.exchange(logical, stage)
        try:
            self.store.remove_root(root["root_key"])
            remaining = self.store.roots()
            if remaining and root["primary_root"]:
                self.store.set_primary_root(remaining[0]["root_key"])
            if remaining:
                generation_id, payload, manifests = self.capture_current()
                world = self._publish_generation(
                    generation_id=generation_id,
                    generation_payload=payload,
                    cause="Remove managed root",
                    supplied_manifests=manifests,
                )
                prime_id = world.content_id
            else:
                self.store.set_meta("primeInstance", None)
                self.store.set_meta("primeContent", None)
                self.store.set_meta("primeGeneration", None)
                self.store.set_meta("dirty", False)
                prime_id = None
        except BaseException:
            try:
                self.store.root(root["root_key"])
            except NotFound:
                self.store.add_root(
                    root_key=root["root_key"],
                    raw_path=logical,
                    display_path=root["display_path"],
                    kind=root["kind"],
                    device=root["device"],
                    primary=bool(root["primary_root"]),
                    generation_id=root["generation_id"],
                    manifest_root=root["manifest_root"],
                )
                if root["primary_root"]:
                    self.store.set_primary_root(root["root_key"])
            with (self.watcher.owned_writes() if self.watcher is not None else nullcontext()):
                self.atomic.exchange(logical, stage)
            raise

        os.unlink(stage)
        live = self.paths.live / root["root_key"]
        live.unlink(missing_ok=True)
        fsync_directory(Path(os.fsdecode(os.path.dirname(logical))))
        fsync_directory(self.paths.live)
        return {"path": root["display_path"], "prime": prime_id}
