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
# Optional blocks (1.2.0). Absent means the documented default; present means validated.
_OPTIONAL_FIELDS = {"limits", "network", "anchor", "adapterOptions"}
_BUILTIN_ADAPTERS = ("claude", "codex", "omp", "pi")
_NETWORK_POLICIES = ("shared", "allowlist", "none")


@dataclass(frozen=True, slots=True)
class GenericAgentCommand:
    name: str
    argv: tuple[str, ...]
    credential_mounts: tuple[tuple[Path, Path], ...]
    event_format: str
    network_hosts: tuple[str, ...] = ()

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
            "limits": {"defaultTimeoutSeconds": None},
            "network": {"policy": "shared", "allow": []},
            "anchor": {"exportPath": None},
            "adapterOptions": {},
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
        if not isinstance(self.value, dict) or not (_TOP_LEVEL_FIELDS <= set(self.value) <= _TOP_LEVEL_FIELDS | _OPTIONAL_FIELDS):
            raise WorldlineError(
                "INVALID_CONFIG",
                "global config must have schemaVersion, readonlyHomePaths, agentCommands, and ghosts, "
                "optionally limits, network, and anchor",
            )
        self._validate_optional()
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

    def _validate_optional(self) -> None:
        limits = self.value.get("limits", {"defaultTimeoutSeconds": None})
        if not isinstance(limits, dict) or set(limits) != {"defaultTimeoutSeconds"}:
            raise WorldlineError("INVALID_CONFIG", "limits must have exactly defaultTimeoutSeconds")
        timeout = limits["defaultTimeoutSeconds"]
        if timeout is not None and (isinstance(timeout, bool) or not isinstance(timeout, int) or timeout <= 0):
            raise WorldlineError("INVALID_CONFIG", "limits.defaultTimeoutSeconds must be null or a positive integer")
        network = self.value.get("network", {"policy": "shared", "allow": []})
        if not isinstance(network, dict) or set(network) != {"policy", "allow"}:
            raise WorldlineError("INVALID_CONFIG", "network must have exactly policy and allow")
        if network["policy"] not in _NETWORK_POLICIES:
            raise WorldlineError("INVALID_CONFIG", f"network.policy must be one of {', '.join(_NETWORK_POLICIES)}")
        allow = network["allow"]
        if not isinstance(allow, list) or not all(isinstance(item, str) and item and " " not in item for item in allow):
            raise WorldlineError("INVALID_CONFIG", "network.allow must be a list of host names (a leading dot allows a whole domain)")
        anchor = self.value.get("anchor", {"exportPath": None})
        if not isinstance(anchor, dict) or set(anchor) != {"exportPath"}:
            raise WorldlineError("INVALID_CONFIG", "anchor must have exactly exportPath")
        export = anchor["exportPath"]
        if export is not None:
            if not isinstance(export, str) or not Path(export).expanduser().is_absolute():
                raise WorldlineError("INVALID_CONFIG", "anchor.exportPath must be null or an absolute path")
            self._reject_worldline_storage(Path(export).expanduser())
        options = self.value.get("adapterOptions", {})
        if not isinstance(options, dict):
            raise WorldlineError("INVALID_CONFIG", "adapterOptions must be a map of builtin adapter name to options")
        for name, option in options.items():
            if name not in _BUILTIN_ADAPTERS:
                raise WorldlineError("INVALID_CONFIG", f"adapterOptions names an unknown builtin adapter: {name} (generic adapters carry their own argv)")
            if not isinstance(option, dict) or set(option) != {"argv"}:
                raise WorldlineError("INVALID_CONFIG", f"adapterOptions.{name} must have exactly argv")
            argv = option["argv"]
            if not isinstance(argv, list) or not all(isinstance(item, str) and item and "\x00" not in item for item in argv):
                raise WorldlineError("INVALID_CONFIG", f"adapterOptions.{name}.argv must be a list of nonempty strings")

    def adapter_argv(self, name: str) -> tuple[str, ...]:
        """Extra argv a builtin adapter inserts before the mission (e.g. codex `-c model_reasoning_effort=high`)."""
        option = self.value.get("adapterOptions", {}).get(name)
        return tuple(option["argv"]) if isinstance(option, dict) else ()

    @property
    def default_timeout_seconds(self) -> int | None:
        return self.value.get("limits", {}).get("defaultTimeoutSeconds")

    @property
    def network_policy(self) -> str:
        return str(self.value.get("network", {}).get("policy", "shared"))

    @property
    def network_allow(self) -> tuple[str, ...]:
        return tuple(self.value.get("network", {}).get("allow", ()))

    @property
    def anchor_export_path(self) -> Path | None:
        export = self.value.get("anchor", {}).get("exportPath")
        return None if export is None else Path(export).expanduser()

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
        if not isinstance(value, dict) or not ({"argv", "credentialMounts", "eventFormat"} <= set(value) <= {"argv", "credentialMounts", "eventFormat", "networkHosts"}):
            raise WorldlineError("INVALID_CONFIG", f"agent command {name} has invalid fields")
        hosts = value.get("networkHosts", [])
        if not isinstance(hosts, list) or not all(isinstance(item, str) and item for item in hosts):
            raise WorldlineError("INVALID_CONFIG", f"agent command {name} networkHosts must be a list of host names")
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
        return GenericAgentCommand(name, tuple(argv), tuple(mounts), event_format, tuple(hosts))

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
