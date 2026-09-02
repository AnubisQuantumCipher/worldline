from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any, Mapping
import uuid

from .. import SCHEMA_VERSION
from ..canonical import canonical_bytes
from ..core import Core, hash_id
from ..errors import WorldlineError
from ..environment import safe_environment
_SECRET_LABEL = re.compile(r"(?:TOKEN|KEY|PASSWORD|PASSWD|SECRET|CREDENTIAL|AUTH|COOKIE)", re.IGNORECASE)


class DockerAdapter:
    def __init__(self, core: Core | None = None) -> None:
        self.executable = shutil.which("docker")
        self.core = core or Core.shared()
        if self.executable is None:
            raise WorldlineError("DOCKER_UNAVAILABLE", "docker is not installed")
        probe = subprocess.run(
            [self.executable, "info", "--format", "{{json .ServerVersion}}"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=10,
        )
        if probe.returncode != 0:
            raise WorldlineError("DOCKER_UNAVAILABLE", probe.stderr.decode("utf-8", "replace").strip() or "Docker daemon is unavailable")
        self.server_version = probe.stdout.decode("utf-8", "replace").strip().strip('"')

    @staticmethod
    def _world_id(value: str) -> str:
        try:
            parsed = uuid.UUID(value)
        except ValueError as exc:
            raise WorldlineError("INVALID_WORLD_INSTANCE", f"world instance is not a UUIDv4: {value}") from exc
        if parsed.version != 4 or str(parsed) != value:
            raise WorldlineError("INVALID_WORLD_INSTANCE", f"world instance is not a UUIDv4: {value}")
        return value

    def capture(
        self,
        world_instance: str,
        *,
        world_roots: Mapping[str, Path],
    ) -> list[dict[str, Any]]:
        world_instance = self._world_id(world_instance)
        resolved_roots = {
            root_key: path.resolve(strict=True)
            for root_key, path in world_roots.items()
        }
        listing = subprocess.run(
            [
                self.executable,
                "ps",
                "-aq",
                "--filter",
                f"label=worldline.instance={world_instance}",
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=15,
        )
        if listing.returncode != 0:
            raise WorldlineError("DOCKER_INSPECTION_FAILED", listing.stderr.decode("utf-8", "replace").strip())
        identifiers = [line for line in listing.stdout.decode("ascii", "strict").splitlines() if line]
        if not identifiers:
            return []
        inspection = subprocess.run(
            [self.executable, "inspect", *identifiers],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=30,
        )
        if inspection.returncode != 0:
            raise WorldlineError("DOCKER_INSPECTION_FAILED", inspection.stderr.decode("utf-8", "replace").strip())
        parsed = json.loads(inspection.stdout.decode("utf-8", "strict"))
        captured: list[dict[str, Any]] = []
        for item in parsed:
            config = item.get("Config", {})
            labels = config.get("Labels") or {}
            if labels.get("worldline.instance") != world_instance:
                raise WorldlineError("DOCKER_SCOPE_VIOLATION", f"container lost WORLDLINE label: {item.get('Id')}")
            scoped_labels = {
                key: str(value)
                for key, value in labels.items()
                if (
                    isinstance(key, str)
                    and key.startswith("worldline.")
                    and not _SECRET_LABEL.search(key)
                )
            }
            mounts: list[dict[str, Any]] = []
            for mount in item.get("Mounts", []):
                if mount.get("Type") != "bind":
                    raise WorldlineError(
                        "DOCKER_SCOPE_VIOLATION",
                        f"container uses a non-bind mount: {item.get('Id')}",
                    )
                source = Path(str(mount.get("Source", ""))).resolve(strict=True)
                matched_root = None
                for root_key, root_path in resolved_roots.items():
                    try:
                        source.relative_to(root_path)
                    except ValueError:
                        continue
                    matched_root = root_key
                    break
                if matched_root is None:
                    raise WorldlineError(
                        "DOCKER_SCOPE_VIOLATION",
                        f"container bind mount is outside this world's roots: {source}",
                    )
                mounts.append(
                    {
                        "rootKey": matched_root,
                        "sourceRelative": str(source.relative_to(resolved_roots[matched_root])),
                        "target": str(mount.get("Destination", "")),
                        "readOnly": not bool(mount.get("RW", False)),
                    }
                )
            environment_values: dict[str, str] = {}
            for item_value in config.get("Env") or []:
                name, separator, value = str(item_value).partition("=")
                if separator:
                    environment_values[name] = value
            sanitized: dict[str, Any] = {
                "schemaVersion": SCHEMA_VERSION,
                "id": item.get("Id"),
                "name": str(item.get("Name", "")).removeprefix("/"),
                "image": config.get("Image"),
                "command": list(config.get("Cmd") or []),
                "entrypoint": list(config.get("Entrypoint") or []),
                "workingDir": str(config.get("WorkingDir") or ""),
                "user": str(config.get("User") or ""),
                "environment": safe_environment(environment_values),
                "mounts": mounts,
                "state": item.get("State", {}).get("Status"),
                "labels": scoped_labels,
            }
            sanitized["inspectHash"] = hash_id(
                self.core.hash_bytes(
                    b"worldline-docker-inspect-v1" + canonical_bytes(sanitized)
                )
            )
            captured.append(sanitized)
        return captured

    def recreate(
        self,
        manifest: Mapping[str, Any],
        *,
        world_instance: str,
        world_roots: Mapping[str, Path],
    ) -> str:
        world_instance = self._world_id(world_instance)
        if manifest.get("schemaVersion") != SCHEMA_VERSION or manifest.get("labels", {}).get("worldline.instance") != world_instance:
            raise WorldlineError("DOCKER_SCOPE_VIOLATION", "container manifest is not owned by this world")
        image = manifest.get("image")
        command = manifest.get("command", [])
        entrypoint = manifest.get("entrypoint", [])
        mounts = manifest.get("mounts", [])
        environment = manifest.get("environment", {})
        working_directory = manifest.get("workingDir", "")
        user = manifest.get("user", "")
        if (
            not isinstance(image, str)
            or not image
            or not isinstance(command, list)
            or not all(isinstance(item, str) for item in command)
            or not isinstance(entrypoint, list)
            or not all(isinstance(item, str) for item in entrypoint)
            or not isinstance(environment, dict)
            or not all(isinstance(key, str) and isinstance(value, str) for key, value in environment.items())
        ):
            raise WorldlineError("DOCKER_MANIFEST_UNSUPPORTED", "container image, command, entrypoint, or environment is not reconstructable")
        argv = [
            self.executable,
            "create",
            "--label",
            f"worldline.instance={world_instance}",
            "--network",
            "bridge",
            "--name",
            f"worldline-{world_instance}-{str(uuid.uuid4())[:8]}",
        ]
        for key, value in sorted(manifest.get("labels", {}).items()):
            if key == "worldline.instance":
                continue
            if not isinstance(key, str) or not key.startswith("worldline.") or not isinstance(value, str):
                raise WorldlineError("DOCKER_SCOPE_VIOLATION", "container manifest contains an unscoped label")
            argv.extend(("--label", f"{key}={value}"))
        if entrypoint:
            argv.extend(("--entrypoint", entrypoint[0]))
            command = [*entrypoint[1:], *command]
        if working_directory:
            argv.extend(("--workdir", str(working_directory)))
        if user:
            argv.extend(("--user", str(user)))
        for key, value in sorted(environment.items()):
            argv.extend(("--env", f"{key}={value}"))
        for mount in mounts:
            if not isinstance(mount, dict) or set(mount) != {"rootKey", "sourceRelative", "target", "readOnly"}:
                raise WorldlineError("DOCKER_MANIFEST_UNSUPPORTED", "container mount schema is unsupported")
            try:
                source = (
                    world_roots[mount["rootKey"]].resolve(strict=True)
                    / str(mount["sourceRelative"])
                ).resolve(strict=True)
                source.relative_to(world_roots[mount["rootKey"]].resolve(strict=True))
            except (KeyError, ValueError, FileNotFoundError) as exc:
                raise WorldlineError("DOCKER_SCOPE_VIOLATION", f"container mount names unmanaged path: {mount.get('rootKey')}:{mount.get('sourceRelative')}") from exc
            option = f"type=bind,src={source},dst={mount['target']}"
            if mount["readOnly"]:
                option += ",readonly"
            argv.extend(("--mount", option))
        argv.extend((image, *command))
        result = subprocess.run(
            argv,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=60,
        )
        if result.returncode != 0:
            raise WorldlineError("DOCKER_RECREATE_FAILED", result.stderr.decode("utf-8", "replace").strip())
        container_id = result.stdout.decode("ascii", "strict").strip()
        started = subprocess.run(
            [self.executable, "start", container_id],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=60,
        )
        if started.returncode != 0:
            subprocess.run(
                [self.executable, "rm", container_id],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=30,
            )
            raise WorldlineError("DOCKER_RECREATE_FAILED", started.stderr.decode("utf-8", "replace").strip())
        return container_id

    @classmethod
    def capability(cls) -> dict[str, Any]:
        try:
            adapter = cls()
        except (WorldlineError, subprocess.TimeoutExpired) as exc:
            reason = exc.message if isinstance(exc, WorldlineError) else str(exc)
            return {"state": "UNAVAILABLE", "reason": reason}
        return {"state": "AVAILABLE", "serverVersion": adapter.server_version, "scope": "worldline-labelled-only"}
