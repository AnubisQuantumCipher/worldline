from __future__ import annotations

import base64
from dataclasses import dataclass
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import tomllib
from typing import Any, Iterable, Mapping, Sequence

from . import SCHEMA_VERSION
from .canonical import atomic_write_json, canonical_bytes
from .core import Core, hash_id
from .manifest import display_path, path_b64

_SECRET_NAME = re.compile(r"(?:TOKEN|KEY|PASSWORD|PASSWD|SECRET|CREDENTIAL|AUTH|COOKIE)", re.IGNORECASE)
_SAFE_EXACT = {
    "LANG", "LANGUAGE", "TERM", "COLORTERM", "EDITOR", "VISUAL", "PAGER", "PATH",
    "XDG_DATA_HOME", "XDG_CONFIG_HOME", "XDG_CACHE_HOME", "XDG_STATE_HOME", "XDG_RUNTIME_DIR",
    "RUSTUP_TOOLCHAIN", "GPR_PROJECT_PATH", "ADA_PROJECT_PATH", "VIRTUAL_ENV", "CONDA_DEFAULT_ENV",
}
_SAFE_PREFIXES = ("LC_", "MISE_", "ASDF_", "GNAT_", "PYENV_", "NVM_")
_SKIP_DEPENDENCY_DIRS = {b".git", b".hg", b".svn", b"node_modules", b"target", b"dist", b"build", b".venv"}

@dataclass(frozen=True, slots=True)
class OwnedProcess:
    pid: int | None
    world_instance: str
    systemd_unit: str | None
    role: str
    argv: tuple[str, ...] = ()
    cwd: bytes = b""


@dataclass(frozen=True, slots=True)
class EnvironmentSnapshot:
    value: dict[str, Any]
    root_hash: str

    def save(self, path: Path) -> None:
        atomic_write_json(path, self.value)


def safe_environment(environment: Mapping[str, str] | None = None) -> dict[str, str]:
    source = os.environ if environment is None else environment
    result: dict[str, str] = {}
    for name, value in source.items():
        if _SECRET_NAME.search(name):
            continue
        if name in _SAFE_EXACT or any(name.startswith(prefix) for prefix in _SAFE_PREFIXES):
            result[name] = value
    return dict(sorted(result.items()))


def capture_processes(processes: Iterable[OwnedProcess]) -> list[dict[str, Any]]:
    captured: list[dict[str, Any]] = []
    for process in sorted(processes, key=lambda item: (item.world_instance, item.pid if item.pid is not None else -1)):
        proc = None if process.pid is None else Path("/proc") / str(process.pid)
        try:
            if proc is None:
                raise FileNotFoundError
            raw_argv = (proc / "cmdline").read_bytes()
            argv = [item for item in raw_argv.split(b"\x00") if item]
            cwd = os.readlink(os.fsencode(proc / "cwd"))
            cwd_bytes = os.fsencode(cwd)
            cgroup = (proc / "cgroup").read_bytes()
            state = "RUNNING"
        except (FileNotFoundError, ProcessLookupError):
            argv = [item.encode("utf-8", "strict") for item in process.argv]
            cwd_bytes = process.cwd
            cgroup = b""
            state = "EXITED"
        captured.append(
            {
                "pid": process.pid,
                "worldInstance": process.world_instance,
                "systemdUnit": process.systemd_unit,
                "role": process.role,
                "state": state,
                "argvB64": [path_b64(item) for item in argv],
                "argvDisplay": [item.decode("utf-8", "replace") for item in argv],
                "cwdB64": path_b64(cwd_bytes),
                "cwdDisplay": display_path(cwd_bytes),
                "cgroupB64": path_b64(cgroup),
            }
        )
    return captured


def _canonical_external_json(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite external number")
        return repr(value)
    if isinstance(value, list):
        return [_canonical_external_json(item) for item in value]
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise ValueError("external JSON map key is not a string")
        return {
            key: _canonical_external_json(item)
            for key, item in sorted(value.items())
        }
    raise ValueError(f"unsupported external JSON value: {type(value).__name__}")


def capture_workspace() -> dict[str, Any]:
    sections = ("clients", "workspaces", "monitors", "activeworkspace")
    result: dict[str, Any] = {"state": "CAPTURED"}
    for section in sections:
        try:
            completed = subprocess.run(
                ["hyprctl", "-j", section],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=5,
            )
        except FileNotFoundError:
            return {"state": "UNAVAILABLE", "reason": "hyprctl is not installed"}
        except subprocess.TimeoutExpired:
            return {"state": "UNAVAILABLE", "reason": f"hyprctl {section} timed out"}
        if completed.returncode != 0:
            return {
                "state": "UNAVAILABLE",
                "reason": completed.stderr.decode("utf-8", "replace").strip() or f"hyprctl {section} failed",
            }
        try:
            parsed = json.loads(completed.stdout.decode("utf-8", "strict"))
            normalized = _canonical_external_json(parsed)
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
            return {"state": "UNAVAILABLE", "reason": f"hyprctl {section} returned invalid JSON"}
        result[section] = {
            "rawB64": base64.b64encode(completed.stdout).decode("ascii"),
            "value": normalized,
        }
    return result


def capture_toolchains(executables: Sequence[str], core: Core | None = None) -> list[dict[str, Any]]:
    verifier = core or Core.shared()
    result: list[dict[str, Any]] = []
    for requested in sorted(set(executables)):
        resolved = shutil.which(requested)
        if resolved is None:
            result.append({"requested": requested, "state": "UNAVAILABLE", "reason": "executable not found"})
            continue
        path = Path(resolved).resolve()
        try:
            completed = subprocess.run(
                [str(path), "--version"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
                timeout=10,
                env={"PATH": os.environ.get("PATH", ""), "LC_ALL": "C", "HOME": os.environ.get("HOME", "")},
            )
            version = completed.stdout
            state = "CAPTURED" if completed.returncode == 0 else "DEGRADED"
            reason = None if completed.returncode == 0 else f"--version exited {completed.returncode}"
        except subprocess.TimeoutExpired:
            version = b""
            state = "DEGRADED"
            reason = "--version timed out"
        result.append(
            {
                "requested": requested,
                "state": state,
                "reason": reason,
                "path": str(path),
                "digest": hash_id(verifier.hash_file(path)),
                "versionHash": hash_id(verifier.hash_bytes(version)),
                "versionRawB64": base64.b64encode(version).decode("ascii"),
                "versionDisplay": version.decode("utf-8", "replace"),
            }
        )
    return result


def _file_record(path: bytes, root: bytes, core: Core) -> dict[str, str]:
    relative = os.path.relpath(path, root)
    return {
        "pathB64": path_b64(relative),
        "pathDisplay": display_path(relative),
        "hash": hash_id(core.hash_file(path)),
    }



def _dependency_spec(specification: str) -> tuple[str, str | None]:
    match = re.match(r"\s*([A-Za-z0-9_.-]+)", specification)
    if match is None:
        return specification.strip(), None
    remainder = specification[match.end() :].strip()
    return match.group(1), remainder or None



def _parse_dependency_group(format_name: str, files: list[bytes]) -> list[dict[str, str | None]] | None:
    by_name = {os.path.basename(path): path for path in files}
    if format_name == "cargo":
        descriptor = by_name.get(b"Cargo.toml")
        if descriptor is None:
            return None
        value = tomllib.loads(Path(os.fsdecode(descriptor)).read_text(encoding="utf-8"))
        declared: dict[str, str | None] = {}
        for table_name in ("dependencies", "dev-dependencies", "build-dependencies"):
            for name, details in value.get(table_name, {}).items():
                declared[name] = details if isinstance(details, str) else details.get("version")
        return [{"name": name, "version": declared[name]} for name in sorted(declared)]
    if format_name == "npm":
        descriptor = by_name.get(b"package.json")
        if descriptor is None:
            return None
        value = json.loads(Path(os.fsdecode(descriptor)).read_text(encoding="utf-8"))
        declared: dict[str, str] = {}
        for table_name in ("dependencies", "devDependencies", "optionalDependencies", "peerDependencies"):
            declared.update(value.get(table_name, {}))
        return [{"name": name, "version": declared[name]} for name in sorted(declared)]
    if format_name == "python":
        descriptor = by_name.get(b"pyproject.toml")
        if descriptor is None:
            return None
        value = tomllib.loads(Path(os.fsdecode(descriptor)).read_text(encoding="utf-8"))
        specifications: list[str] = list(value.get("project", {}).get("dependencies", []))
        for group in value.get("project", {}).get("optional-dependencies", {}).values():
            specifications.extend(group)
        declared = dict(_dependency_spec(item) for item in specifications)
        return [{"name": name, "version": declared[name]} for name in sorted(declared)]
    if format_name == "go":
        descriptor = by_name.get(b"go.mod")
        if descriptor is None:
            return None
        text = Path(os.fsdecode(descriptor)).read_text(encoding="utf-8")
        declared: dict[str, str | None] = {}
        in_block = False
        for raw_line in text.splitlines():
            line = raw_line.split("//", 1)[0].strip()
            if line == "require (":
                in_block = True
                continue
            if in_block and line == ")":
                in_block = False
                continue
            if line.startswith("require "):
                line = line.removeprefix("require ").strip()
            elif not in_block:
                continue
            fields = line.split()
            if fields:
                declared[fields[0]] = fields[1] if len(fields) > 1 else None
        return [{"name": name, "version": declared[name]} for name in sorted(declared)]
    if format_name == "ruby":
        lock = by_name.get(b"Gemfile.lock")
        if lock is None:
            return None
        text = Path(os.fsdecode(lock)).read_text(encoding="utf-8")
        declared: dict[str, str | None] = {}
        in_specs = False
        for line in text.splitlines():
            if line == "  specs:":
                in_specs = True
                continue
            if in_specs and line and not line.startswith("    "):
                in_specs = False
            if in_specs:
                match = re.match(r"^    ([A-Za-z0-9_.-]+) \(([^)]+)\)$", line)
                if match:
                    declared[match.group(1)] = match.group(2)
        return [{"name": name, "version": declared[name]} for name in sorted(declared)]
    if format_name == "gpr":
        declared: set[str] = set()
        expression = re.compile(r"^\s*(?:limited\s+)?with\s+\"([^\"]+)\"", re.MULTILINE | re.IGNORECASE)
        for path in files:
            text = Path(os.fsdecode(path)).read_text(encoding="utf-8")
            declared.update(expression.findall(text))
        return [{"name": name, "version": None} for name in sorted(declared)]
    return None


def capture_dependencies(
    roots: Sequence[tuple[str, str | bytes | os.PathLike[str] | os.PathLike[bytes]]],
    core: Core | None = None,
) -> list[dict[str, Any]]:
    verifier = core or Core.shared()
    records: list[dict[str, Any]] = []
    for root_key, root_value in sorted(roots):
        root = os.path.abspath(os.fsencode(root_value))
        for current, directory_names, file_names in os.walk(root):
            directory_names[:] = sorted(name for name in directory_names if os.fsencode(name) not in _SKIP_DEPENDENCY_DIRS)
            names = {os.fsencode(name) for name in file_names}
            groups: list[tuple[str, set[bytes]]] = [
                ("cargo", {b"Cargo.toml", b"Cargo.lock"}),
                ("npm", {b"package.json", b"package-lock.json", b"npm-shrinkwrap.json"}),
                ("python", {b"pyproject.toml", b"poetry.lock"}),
                ("go", {b"go.mod", b"go.sum"}),
                ("ruby", {b"Gemfile", b"Gemfile.lock"}),
            ]
            for format_name, candidates in groups:
                selected = sorted(os.path.join(os.fsencode(current), name) for name in names & candidates)
                if selected:
                    records.append(_dependency_record(root_key, root, format_name, selected, verifier))
            gpr_files = sorted(os.path.join(os.fsencode(current), name) for name in names if name.endswith(b".gpr"))
            if gpr_files:
                records.append(_dependency_record(root_key, root, "gpr", gpr_files, verifier))
            unsupported = sorted(
                os.path.join(os.fsencode(current), name)
                for name in names & {b"pnpm-lock.yaml", b"yarn.lock"}
            )
            if unsupported:
                records.append(_dependency_record(root_key, root, "unsupported-lock", unsupported, verifier))
    records.sort(key=lambda item: (item["rootKey"], item["format"], item["directoryB64"]))
    return records


def _dependency_record(root_key: str, root: bytes, format_name: str, files: list[bytes], core: Core) -> dict[str, Any]:
    directory = os.path.relpath(os.path.dirname(files[0]), root)
    if directory == b".":
        directory = b""
    hashes = [_file_record(path, root, core) for path in files]
    try:
        declared = _parse_dependency_group(format_name, files)
        state = "PARSED" if declared is not None else "UNAVAILABLE"
        reason = None if declared is not None else "format parser unavailable"
    except (OSError, UnicodeError, json.JSONDecodeError, tomllib.TOMLDecodeError, TypeError, ValueError) as exc:
        declared = None
        state = "UNAVAILABLE"
        reason = str(exc)
    return {
        "rootKey": root_key,
        "directoryB64": path_b64(directory),
        "directoryDisplay": display_path(directory),
        "format": format_name,
        "state": state,
        "reason": reason,
        "files": hashes,
        "declared": declared,
        "count": None if declared is None else len(declared),
    }


def evidence_manifest(
    results: Sequence[dict[str, Any]],
    core: Core | None = None,
    *,
    metrics: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    verifier = core or Core.shared()
    checks = [dict(result) for result in results]
    summary = "UNASSESSED" if not checks else ("PASS" if all(item.get("status") == "PASS" for item in checks) else "FAIL")
    value = {"schemaVersion": SCHEMA_VERSION, "summary": summary, "checks": checks, "metrics": dict(metrics or {})}
    value["root"] = hash_id(verifier.hash_bytes(b"worldline-evidence-v1" + canonical_bytes(value)))
    return value


class EnvironmentCapture:
    def __init__(self, core: Core | None = None) -> None:
        self.core = core or Core.shared()

    def capture(
        self,
        *,
        processes: Iterable[OwnedProcess],
        toolchains: Sequence[str],
        dependency_roots: Sequence[tuple[str, str | bytes | os.PathLike[str] | os.PathLike[bytes]]],
        agent: dict[str, Any],
        evidence: dict[str, Any],
        environment: Mapping[str, str] | None = None,
        workspace: dict[str, Any] | None = None,
        containers: Sequence[dict[str, Any]] = (),
    ) -> EnvironmentSnapshot:
        safe = safe_environment(environment)
        safe_hash = hash_id(
            self.core.hash_bytes(b"worldline-safe-environment-v1" + canonical_bytes(safe))
        )
        process_values = capture_processes(processes)
        for process in process_values:
            process["safeEnvHash"] = safe_hash
        value: dict[str, Any] = {
            "schemaVersion": SCHEMA_VERSION,
            "processes": process_values,
            "workspace": capture_workspace() if workspace is None else workspace,
            "safeEnvironment": safe,
            "safeEnvironmentHash": safe_hash,
            "toolchains": capture_toolchains(toolchains, self.core),
            "containers": list(containers),
            "agent": agent,
            "externalDependencies": capture_dependencies(dependency_roots, self.core),
            "evidence": evidence,
        }
        root = hash_id(self.core.hash_bytes(b"worldline-environment-v1" + canonical_bytes(value)))
        return EnvironmentSnapshot(value=value, root_hash=root)
