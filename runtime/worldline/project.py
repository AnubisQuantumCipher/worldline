from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any, Mapping

from . import SCHEMA_VERSION
from .errors import WorldlineError
from .store import StateStore

_SECRET_NAME = re.compile(r"(?:TOKEN|KEY|PASSWORD|PASSWD|SECRET|CREDENTIAL|AUTH|COOKIE)", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class GeneratedClassifier:
    root_key: str
    glob: str


@dataclass(frozen=True, slots=True)
class CheckSpec:
    id: str
    kind: str
    argv: tuple[str, ...]
    cwd: str | None
    required: bool
    format: str
    result: str | None
    covers: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ServiceSpec:
    id: str
    argv: tuple[str, ...]
    cwd: str
    env: dict[str, str]
    health_argv: tuple[str, ...]
    restart: str


class ProjectConfig:
    def __init__(
        self,
        *,
        generated: tuple[GeneratedClassifier, ...],
        checks: tuple[CheckSpec, ...],
        services: tuple[ServiceSpec, ...],
    ) -> None:
        self.generated = generated
        self.checks = checks
        self.services = services

    @classmethod
    def load(cls, primary_root: Path, store: StateStore) -> "ProjectConfig":
        path = primary_root / ".worldline.json"
        if not path.is_file():
            return cls(generated=(), checks=(), services=())
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise WorldlineError("INVALID_PROJECT_CONFIG", f"{path}: {exc}") from exc
        if not isinstance(value, dict) or set(value) != {"schemaVersion", "generated", "checks", "services"}:
            raise WorldlineError("INVALID_PROJECT_CONFIG", "project config fields must be schemaVersion, generated, checks, and services")
        if value["schemaVersion"] != SCHEMA_VERSION:
            raise WorldlineError("INVALID_PROJECT_CONFIG", "project config schemaVersion must be literal 1")
        roots = store.roots()
        root_aliases: dict[str, str] = {}
        for root in roots:
            root_aliases[root["root_key"]] = root["root_key"]
            root_aliases[root["display_path"]] = root["root_key"]
        generated: list[GeneratedClassifier] = []
        for item in value["generated"]:
            if not isinstance(item, dict) or set(item) != {"root", "glob"}:
                raise WorldlineError("INVALID_PROJECT_CONFIG", "generated classifiers require root and glob")
            try:
                root_key = root_aliases[item["root"]]
            except (KeyError, TypeError) as exc:
                raise WorldlineError("INVALID_PROJECT_CONFIG", f"generated classifier names unmanaged root: {item.get('root')}") from exc
            cls._relative(item["glob"], "generated glob", allow_glob=True)
            generated.append(GeneratedClassifier(root_key, item["glob"]))

        checks: list[CheckSpec] = []
        check_ids: set[str] = set()
        allowed_check_fields = {"id", "kind", "argv", "cwd", "required", "format", "result", "covers"}
        for item in value["checks"]:
            if not isinstance(item, dict) or not {"id", "kind", "argv", "required", "format"} <= set(item) or not set(item) <= allowed_check_fields:
                raise WorldlineError("INVALID_PROJECT_CONFIG", "check fields are invalid")
            identifier = cls._identifier(item["id"], check_ids, "check")
            if item["kind"] not in {"build", "tests", "proofs", "benchmark", "health"}:
                raise WorldlineError("INVALID_PROJECT_CONFIG", f"invalid check kind: {item['kind']}")
            argv = cls._argv(item["argv"], f"check {identifier}")
            cwd = item.get("cwd")
            if cwd is not None:
                cls._relative(cwd, f"check {identifier} cwd")
            if not isinstance(item["required"], bool):
                raise WorldlineError("INVALID_PROJECT_CONFIG", f"check {identifier} required must be boolean")
            if item["format"] not in {"exit", "junit", "gnatprove", "worldline-benchmark-v1"}:
                raise WorldlineError("INVALID_PROJECT_CONFIG", f"invalid check format: {item['format']}")
            result = item.get("result")
            if result is not None:
                cls._relative(result, f"check {identifier} result")
            covers = item.get("covers", [])
            if not isinstance(covers, list):
                raise WorldlineError("INVALID_PROJECT_CONFIG", f"check {identifier} covers must be an array")
            for pattern in covers:
                cls._relative(pattern, f"check {identifier} covers", allow_glob=True)
            checks.append(
                CheckSpec(identifier, item["kind"], argv, cwd, item["required"], item["format"], result, tuple(covers))
            )

        services: list[ServiceSpec] = []
        service_ids: set[str] = set()
        for item in value["services"]:
            if not isinstance(item, dict) or set(item) != {"id", "argv", "cwd", "env", "healthArgv", "restart"}:
                raise WorldlineError("INVALID_PROJECT_CONFIG", "service fields are invalid")
            identifier = cls._identifier(item["id"], service_ids, "service")
            argv = cls._argv(item["argv"], f"service {identifier}")
            health = cls._argv(item["healthArgv"], f"service {identifier} health")
            cls._relative(item["cwd"], f"service {identifier} cwd")
            environment = item["env"]
            if not isinstance(environment, dict) or not all(isinstance(key, str) and isinstance(val, str) for key, val in environment.items()):
                raise WorldlineError("INVALID_PROJECT_CONFIG", f"service {identifier} env must map strings")
            if any(_SECRET_NAME.search(key) for key in environment):
                raise WorldlineError("INVALID_PROJECT_CONFIG", f"service {identifier} env contains a credential-like key")
            if item["restart"] not in {"never", "on-failure"}:
                raise WorldlineError("INVALID_PROJECT_CONFIG", f"service {identifier} restart is invalid")
            services.append(ServiceSpec(identifier, argv, item["cwd"], dict(environment), health, item["restart"]))
        return cls(generated=tuple(generated), checks=tuple(checks), services=tuple(services))

    @staticmethod
    def _relative(value: Any, label: str, *, allow_glob: bool = False) -> str:
        if not isinstance(value, str) or not value or "\x00" in value:
            raise WorldlineError("INVALID_PROJECT_CONFIG", f"{label} must be a nonempty string")
        if value == ".":
            return value
        path = PurePosixPath(value)
        if path.is_absolute() or any(part in {"", ".", ".."} for part in value.split("/")):
            raise WorldlineError("INVALID_PROJECT_CONFIG", f"{label} escapes its root: {value}")
        return value

    @staticmethod
    def _argv(value: Any, label: str) -> tuple[str, ...]:
        if not isinstance(value, list) or not value or not all(isinstance(item, str) and item and "\x00" not in item for item in value):
            raise WorldlineError("INVALID_PROJECT_CONFIG", f"{label} argv must be nonempty strings")
        return tuple(value)

    @staticmethod
    def _identifier(value: Any, seen: set[str], label: str) -> str:
        if not isinstance(value, str) or not value or value in seen:
            raise WorldlineError("INVALID_PROJECT_CONFIG", f"{label} id is empty or duplicated: {value}")
        seen.add(value)
        return value
