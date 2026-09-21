from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path, PurePosixPath
import re
import fnmatch
import os
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
    # Globs (relative to the primary root) naming the authoritative verifier files this check
    # executes or reads. Empty means: the files argv/cwd name, plus every file under each named
    # file's directory (a verifier's helpers live beside it). Never candidate-owned.
    verifiers: tuple[str, ...] = ()

    def covers_path(self, relative: str) -> bool:
        return any(
            fnmatch.fnmatchcase(relative, pattern) or relative.startswith(pattern.rstrip("*").rstrip("/") + "/")
            for pattern in self.covers if pattern
        )

    def named_paths(self) -> list[str]:
        """Relative paths that argv names (option-looking tokens and escapes excluded)."""
        out: list[str] = []
        for token in self.argv:
            if not token or token.startswith("-") or token.startswith("/"):
                continue
            relative = os.path.normpath(os.path.join(self.cwd, token)) if self.cwd else os.path.normpath(token)
            if relative.startswith("..") or os.path.isabs(relative) or relative == ".":
                continue
            out.append(relative)
        return out


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
        protected: tuple[str, ...] = (),
        source_sha256: str | None = None,
        source_path: str | None = None,
    ) -> None:
        self.generated = generated
        self.checks = checks
        self.services = services
        # Identity of the policy bytes this configuration was parsed from (None when the root
        # has no .worldline.json). Recorded in every validation context.
        self.source_sha256 = source_sha256
        self.source_path = source_path
        # Paths (relative, globs allowed) a candidate may not change. The list lives in PRIME's
        # policy, which is the only policy ever consulted, and the comparison is the engine's
        # own delta, so no in-tree rewrite can lift it (worldline-lab D10, 2026-09-21).
        self.protected = protected

    @classmethod
    def load(cls, primary_root: Path, store: StateStore) -> "ProjectConfig":
        path = primary_root / ".worldline.json"
        if not path.is_file():
            return cls(generated=(), checks=(), services=())
        try:
            raw = path.read_bytes()
            value = json.loads(raw.decode("utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise WorldlineError("INVALID_PROJECT_CONFIG", f"{path}: {exc}") from exc
        import hashlib
        source_sha256 = hashlib.sha256(raw).hexdigest()
        required_fields = {"schemaVersion", "generated", "checks", "services"}
        if not isinstance(value, dict) or not required_fields <= set(value) or not set(value) <= required_fields | {"protected"}:
            raise WorldlineError("INVALID_PROJECT_CONFIG", "project config fields must be schemaVersion, generated, checks, and services, optionally protected")
        protected_value = value.get("protected", [])
        if not isinstance(protected_value, list) or not all(isinstance(item, str) and item for item in protected_value):
            raise WorldlineError("INVALID_PROJECT_CONFIG", "protected must be a list of relative paths or globs")
        protected: list[str] = []
        for item in protected_value:
            cls._relative(item, "protected path", allow_glob=True)
            protected.append(item)
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
        allowed_check_fields = {"id", "kind", "argv", "cwd", "required", "format", "result", "covers", "verifiers"}
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
            verifiers = item.get("verifiers", [])
            if not isinstance(verifiers, list):
                raise WorldlineError("INVALID_PROJECT_CONFIG", f"check {identifier} verifiers must be an array")
            for pattern in verifiers:
                cls._relative(pattern, f"check {identifier} verifiers", allow_glob=True)
            spec = CheckSpec(identifier, item["kind"], argv, cwd, item["required"], item["format"], result, tuple(covers), tuple(verifiers))
            # A declared verifier the candidate is allowed to rewrite is a contradiction and is
            # refused. (An argv operand under covers is candidate data — `test -f candidate.txt`
            # — not an examiner; it is left out of the verifier set and named in the policy
            # warnings so the omission is never silent.)
            for pattern in spec.verifiers:
                # A literal path is probed as itself; a glob is probed by a representative file
                # under its static prefix (`evaluator/*` -> `evaluator/__probe__`).
                if any(ch in pattern for ch in "*?["):
                    prefix = "/".join(part for part in pattern.split("/") if not any(ch in part for ch in "*?["))
                    probe = f"{prefix}/__probe__" if prefix else "__probe__"
                else:
                    probe = os.path.normpath(pattern)
                if spec.covers_path(probe) or pattern in spec.covers:
                    raise WorldlineError("INVALID_PROJECT_CONFIG", f"check {identifier} declares verifier {pattern} inside its own covers; a verifier cannot be candidate-owned")
            checks.append(spec)

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
        return cls(generated=tuple(generated), checks=tuple(checks), services=tuple(services), protected=tuple(protected), source_sha256=source_sha256, source_path=str(path))

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


def protected_matches(protected: tuple[str, ...] | list[str], path_display: str) -> bool:
    """True when a delta path is covered by a protected pattern: exact, glob, or under a
    protected directory."""
    for pattern in protected:
        base = pattern.rstrip("/")
        if path_display == base or fnmatch.fnmatchcase(path_display, pattern) or path_display.startswith(base + "/"):
            return True
    return False
