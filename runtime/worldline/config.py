from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import stat
import string
from typing import Any, Mapping

from . import SCHEMA_VERSION
from .canonical import atomic_write_json
from .errors import WorldlineError
from .paths import WorldlinePaths

_ALLOWED_PLACEHOLDERS = {"workspace", "missionFile", "worldState"}
_TOP_LEVEL_FIELDS = {"schemaVersion", "readonlyHomePaths", "agentCommands", "ghosts"}


@dataclass(frozen=True, slots=True)
class GenericAgentCommand:
    name: str
    argv: tuple[str, ...]
    credential_mounts: tuple[tuple[Path, Path], ...]
    event_format: str

    def expand(self, values: Mapping[str, str]) -> tuple[str, ...]:
        missing = _ALLOWED_PLACEHOLDERS - set(values)
        if missing:
            raise WorldlineError("MISSING_AGENT_CONTEXT", "generic adapter context is incomplete", {"missing": sorted(missing)})
        return tuple(item.format_map(values) for item in self.argv)


class GlobalConfig:
    def __init__(self, paths: WorldlinePaths, value: dict[str, Any]) -> None:
        self.paths = paths
        self.value = value
        self._validate()

    @classmethod
    def default(cls, paths: WorldlinePaths) -> "GlobalConfig":
        home = paths.home
        value = {
            "schemaVersion": SCHEMA_VERSION,
            "readonlyHomePaths": [
                str(home / ".local/bin"),
                str(home / ".local/share/mise"),
                str(home / ".config/mise"),
                str(home / "opt/gnat"),
            ],
            "agentCommands": {},
            "ghosts": {"enabled": False, "agent": None},
        }
        return cls(paths, value)

    @classmethod
    def load(cls, paths: WorldlinePaths) -> "GlobalConfig":
        paths.ensure()
        if not paths.config_file.exists():
            configuration = cls.default(paths)
            configuration.save()
            return configuration
        info = paths.config_file.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o077:
            raise WorldlineError("UNSAFE_CONFIG", f"global configuration is not owner-only: {paths.config_file}")
        try:
            value = json.loads(paths.config_file.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise WorldlineError("INVALID_CONFIG", f"global configuration is invalid: {exc}") from exc
        return cls(paths, value)

    def save(self) -> None:
        self._validate()
        atomic_write_json(self.paths.config_file, self.value)

    def _validate(self) -> None:
        if not isinstance(self.value, dict) or set(self.value) != _TOP_LEVEL_FIELDS:
            raise WorldlineError("INVALID_CONFIG", "global config must have exactly schemaVersion, readonlyHomePaths, agentCommands, and ghosts")
        if self.value["schemaVersion"] != SCHEMA_VERSION:
            raise WorldlineError("INVALID_CONFIG", "global config schemaVersion must be literal 1")
        readonly = self.value["readonlyHomePaths"]
        if not isinstance(readonly, list) or not all(isinstance(item, str) for item in readonly):
            raise WorldlineError("INVALID_CONFIG", "readonlyHomePaths must be a string array")
        for item in readonly:
            path = Path(item).expanduser()
            if not path.is_absolute():
                raise WorldlineError("INVALID_CONFIG", f"readonlyHomePaths entry is not absolute: {item}")
            self._reject_worldline_storage(path)
        commands = self.value["agentCommands"]
        if not isinstance(commands, dict) or not all(isinstance(name, str) and name for name in commands):
            raise WorldlineError("INVALID_CONFIG", "agentCommands must be a map")
        for name in commands:
            self._parse_command(name, commands[name])
        ghosts = self.value["ghosts"]
        if not isinstance(ghosts, dict) or set(ghosts) != {"enabled", "agent"}:
            raise WorldlineError("INVALID_CONFIG", "ghosts must have exactly enabled and agent")
        if not isinstance(ghosts["enabled"], bool) or not (ghosts["agent"] is None or isinstance(ghosts["agent"], str)):
            raise WorldlineError("INVALID_CONFIG", "ghost settings have invalid types")
        if ghosts["enabled"] and not ghosts["agent"]:
            raise WorldlineError("INVALID_CONFIG", "enabled ghosts require an agent")

    def _reject_worldline_storage(self, path: Path) -> None:
        absolute = path.absolute()
        for internal in (self.paths.data, self.paths.state, self.paths.runtime, self.paths.config):
            try:
                common = Path(os.path.commonpath((absolute, internal.absolute())))
            except ValueError:
                continue
            if common in (absolute, internal.absolute()):
                raise WorldlineError("INVALID_CONFIG", f"read-only projection overlaps WORLDLINE storage: {path}")

    @staticmethod
    def _validate_template(value: str) -> None:
        formatter = string.Formatter()
        try:
            fields = list(formatter.parse(value))
        except ValueError as exc:
            raise WorldlineError("INVALID_CONFIG", f"invalid adapter template: {value}") from exc
        for _literal, field, format_spec, conversion in fields:
            if field is None:
                continue
            if field not in _ALLOWED_PLACEHOLDERS or format_spec or conversion:
                raise WorldlineError("INVALID_CONFIG", f"unsupported adapter placeholder: {field}")

    def _parse_command(self, name: str, value: Any) -> GenericAgentCommand:
        if not isinstance(value, dict) or set(value) != {"argv", "credentialMounts", "eventFormat"}:
            raise WorldlineError("INVALID_CONFIG", f"agent command {name} has invalid fields")
        argv = value["argv"]
        if not isinstance(argv, list) or not argv or not all(isinstance(item, str) and item for item in argv):
            raise WorldlineError("INVALID_CONFIG", f"agent command {name} argv must be nonempty strings")
        for item in argv:
            self._validate_template(item)
        mounts_value = value["credentialMounts"]
        if not isinstance(mounts_value, list):
            raise WorldlineError("INVALID_CONFIG", f"agent command {name} credentialMounts must be an array")
        mounts: list[tuple[Path, Path]] = []
        for mount in mounts_value:
            if not isinstance(mount, dict) or set(mount) != {"source", "target"}:
                raise WorldlineError("INVALID_CONFIG", f"agent command {name} has an invalid credential mount")
            source = Path(mount["source"]).expanduser()
            target = Path(mount["target"]).expanduser()
            if not source.is_absolute() or not target.is_absolute():
                raise WorldlineError("INVALID_CONFIG", f"agent command {name} credential paths must be absolute")
            self._reject_worldline_storage(source)
            mounts.append((source, target))
        event_format = value["eventFormat"]
        if not isinstance(event_format, str) or not event_format:
            raise WorldlineError("INVALID_CONFIG", f"agent command {name} eventFormat must be nonempty")
        return GenericAgentCommand(name, tuple(argv), tuple(mounts), event_format)

    @property
    def readonly_home_paths(self) -> tuple[Path, ...]:
        return tuple(Path(item) for item in self.value["readonlyHomePaths"] if Path(item).exists())

    def generic_agent(self, name: str) -> GenericAgentCommand:
        try:
            value = self.value["agentCommands"][name]
        except KeyError as exc:
            raise WorldlineError("UNKNOWN_ADAPTER", f"generic adapter is not configured: {name}") from exc
        return self._parse_command(name, value)

    def enable_ghosts(self, agent: str) -> None:
        if not agent:
            raise WorldlineError("INVALID_CONFIG", "ghost agent must be nonempty")
        self.value["ghosts"] = {"enabled": True, "agent": agent}
        self.save()

    def disable_ghosts(self) -> None:
        self.value["ghosts"] = {"enabled": False, "agent": None}
        self.save()
