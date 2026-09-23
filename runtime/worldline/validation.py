"""Evidence freshness: the validation context (schema 1).

A world's acceptance evidence is bound to the exact content it evaluated, the authoritative
policy in force, the required checks and their semantics, the executable verifiers those
checks ran, the engine and its security-relevant execution configuration, and the PRIME the
world was forked from. The context is computed at finalization (or by an explicit
revalidation), stored inside the evidence manifest (so the world's identity covers it), and
compared at every promotion boundary against the requirements the CURRENT PRIME imposes.

Two identities matter and are kept apart:

* ``contextHash`` — everything the evaluation bound, including the candidate's own identity.
  It is what a transaction record and a receipt name.
* ``requirementHash`` — only the *requirements* part (policy, checks, verifiers, protected
  paths, execution configuration, engine). The current PRIME's requirement hash is recomputed
  at prepare and at commit; the candidate's evidence is fresh iff its requirement hash equals
  the current one. This is the pair handed to the proved kernel
  (``expected_validation_context`` / ``candidate_validation_context``).

Enforcement of the comparison lives in Python (transaction.py); the kernel proves only that a
mismatching pair is never AUTHORIZED. Nothing here reads secrets: policy bytes, verifier bytes
and configuration values are hashed, credential paths are recorded by name only.
"""
from __future__ import annotations

import fnmatch
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping, Sequence

from . import SCHEMA_VERSION, __version__
from .resolution import resolve_token, root_prefixes
from .trusted import ISOLATION_FLAGS, TRUSTED_INTERPRETER
from .canonical import canonical_bytes
from .core import Core, hash_id
from .environment import safe_environment
from .errors import WorldlineError
from .project import CheckSpec, ProjectConfig

VALIDATION_CONTEXT_SCHEMA = 1
CHECK_RUNNER_TIMEOUT_SECONDS = 600  # checks.py: launcher.communicate(timeout=600)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any, core: Core | None = None) -> str:
    verifier = core or Core.shared()
    return hash_id(verifier.hash_bytes(b"worldline-validation-v1" + canonical_bytes(value)))


_RUNTIME_TREE_CACHE: dict[str, str] = {}


def runtime_tree_sha256() -> str:
    """Identity of the running engine's Python runtime (every module file, by path and bytes)."""
    package = Path(__file__).resolve().parent
    key = str(package)
    if key not in _RUNTIME_TREE_CACHE:
        digest = hashlib.sha256()
        for path in sorted(p for p in package.rglob("*.py") if "__pycache__" not in p.parts):
            digest.update(str(path.relative_to(package)).encode()); digest.update(b"\0")
            digest.update(hashlib.sha256(path.read_bytes()).digest())
        _RUNTIME_TREE_CACHE[key] = digest.hexdigest()
    return _RUNTIME_TREE_CACHE[key]


def canonical_checks(checks: Sequence[CheckSpec]) -> list[dict[str, Any]]:
    """Checks in canonical form: sorted by id, every semantic field present. Declaration order
    in .worldline.json does not change the identity; argv order, flags and settings do."""
    return sorted(
        (
            {
                "id": check.id,
                "kind": check.kind,
                "argv": list(check.argv),
                "cwd": check.cwd,
                "required": bool(check.required),
                "format": check.format,
                "result": check.result,
                "covers": sorted(check.covers),
                "verifiers": sorted(check.verifiers),
            }
            for check in checks
        ),
        key=lambda item: item["id"],
    )


def canonical_policy(project: ProjectConfig) -> dict[str, Any]:
    return {
        "schemaVersion": SCHEMA_VERSION,
        "checks": canonical_checks(project.checks),
        "protected": sorted(project.protected),
        "generated": sorted(({"root": g.root_key, "glob": g.glob} for g in project.generated), key=lambda g: (g["root"], g["glob"])),
        # A declared service is started in PRIME after a collapse: what it runs, where, with
        # which environment, health probe and restart policy is part of the requirement.
        "services": sorted(
            ({"id": s.id, "argv": list(s.argv), "cwd": s.cwd, "env": dict(sorted(s.env.items())), "healthArgv": list(s.health_argv), "restart": s.restart} for s in project.services),
            key=lambda s: s["id"],
        ),
    }


_WALK_SKIP = {".git", ".hg", ".svn", "__pycache__", "node_modules", ".venv"}


def _static_prefix(pattern: str) -> str:
    """The directory part of a glob before its first wildcard ('evaluator/*' -> 'evaluator')."""
    parts = pattern.split("/")
    fixed: list[str] = []
    for part in parts:
        if any(ch in part for ch in "*?["):
            break
        fixed.append(part)
    if fixed and fixed == parts:
        fixed = fixed[:-1]  # a literal file path: its directory
    return "/".join(fixed)


def _glob_match(relative: str, pattern: str) -> bool:
    return fnmatch.fnmatchcase(relative, pattern) or relative.startswith(pattern.rstrip("*").rstrip("/") + "/")


def resolve_verifiers(
    project: ProjectConfig,
    roots: Sequence[Mapping[str, Any]],
    sources: Mapping[str, Path],
) -> list[dict[str, Any]]:
    """The authoritative verifier files a policy's checks execute or read, hashed from
    `sources` (root_key -> directory holding that root's tree).

    For every check: the regular files its argv or cwd name (`source: argv`), and then either
    the files matched by the check's declared `verifiers` globs (`source: declared`) or, when
    none are declared, every regular file under each named file's directory
    (`source: directory`) — a verifier's helpers and data live beside it and are as
    authoritative as the file argv names. An argv operand inside the check's own `covers` is
    candidate data, not a verifier (`policy_warnings` names it); declared verifiers are never
    excluded (a declared verifier inside covers is refused at policy load). Symlinks and
    directories are not verifiers. Entries are sorted so the identity is canonical.
    """
    primary = next((r for r in roots if r.get("primary_root") or r.get("primary")), None)
    if primary is None:
        return []
    logical_by_key: dict[str, str] = {}
    for root in roots:
        logical = os.fsdecode(bytes(root["path"])) if isinstance(root["path"], (bytes, bytearray, memoryview)) else str(root["path"])
        logical_by_key[root["root_key"]] = logical
    prefixes = root_prefixes(logical_by_key)
    found: dict[tuple[str, str, str], dict[str, Any]] = {}
    primary_key = primary["root_key"]

    def add(check_id: str, root_key: str, relative: str, source: str) -> None:
        base = sources.get(root_key)
        if base is None:
            return
        path = base / relative
        if path.is_symlink() or not path.is_file():
            return
        key = (check_id, root_key, relative)
        if key not in found:
            found[key] = {"checkId": check_id, "rootKey": root_key, "path": relative, "sha256": _sha256_file(path), "source": source}

    def add_tree(check_id: str, root_key: str, directory: str, source: str, pattern: str | None = None) -> None:
        base = sources.get(root_key)
        if base is None:
            return
        top = base / directory if directory else base
        if not top.is_dir() or top.is_symlink():
            return
        for current, dirs, files in os.walk(top, followlinks=False):
            dirs[:] = sorted(d for d in dirs if d not in _WALK_SKIP)
            for name in sorted(files):
                relative = os.path.normpath(os.path.relpath(Path(current) / name, base))
                if pattern is None or _glob_match(relative, pattern):
                    add(check_id, root_key, relative, source)

    for check in project.checks:
        named: list[tuple[str, str]] = []
        cwd_rel = check.cwd or ""
        for token in check.argv:
            # One resolution rule, shared with rewrite_argv (runtime/worldline/executed.py). A
            # token that addresses a managed root but cannot be bound cleanly to a member is an
            # "escape" -- it contributes no verifier here, and the check runner refuses it rather
            # than executing it as candidate bytes.
            kind, root_key, relative = resolve_token(token, prefixes, primary_root_key=primary_key, cwd=cwd_rel)
            if kind != "member" or root_key is None or relative is None or root_key not in sources:
                continue
            path = sources[root_key] / relative
            if path.is_symlink() or not path.is_file():
                continue
            if check.covers_path(relative):
                # Candidate-owned data the check reads (its covers say so): not a verifier.
                # policy_warnings names it; `verifiers` binds an examiner explicitly.
                continue
            named.append((root_key, relative))
            add(check.id, root_key, relative, "argv")
        if check.verifiers:
            for pattern in check.verifiers:
                add_tree(check.id, primary_key, _static_prefix(pattern), "declared", pattern)
        else:
            for root_key, relative in named:
                directory = os.path.dirname(relative)
                if directory and directory != ".":
                    add_tree(check.id, root_key, directory, "directory")
    return [found[k] for k in sorted(found)]


_KERNEL_LIBRARY_CACHE: dict[str, str] = {}


def _kernel_library_sha256() -> str | None:
    try:
        path = Path(Core.shared().library_path)
    except Exception:  # noqa: BLE001 - the identity records absence rather than failing evidence
        return None
    key = str(path)
    if key not in _KERNEL_LIBRARY_CACHE:
        try:
            _KERNEL_LIBRARY_CACHE[key] = _sha256_file(path)
        except OSError:
            return None
    return _KERNEL_LIBRARY_CACHE[key]


def execution_context(config: Any, adapter_name: str | None = None) -> dict[str, Any]:
    """Security-relevant execution configuration that affects what evidence means."""
    # The environment the check runner forwards into the sandbox (safe_environment: PATH, LANG,
    # toolchain selectors …) governs what a check resolves and runs; session-specific names are
    # left out so a re-login does not stale evidence for no semantic reason.
    check_environment = {k: v for k, v in safe_environment().items() if k not in ("XDG_RUNTIME_DIR",)}
    return {
        "engineVersion": __version__,
        "runtimeTreeSha256": runtime_tree_sha256(),
        "kernelLibrarySha256": _kernel_library_sha256(),
        "checkRunnerInterpreter": TRUSTED_INTERPRETER,
        # The startup policy of the TRUSTED processes, not decoration: it decides whether the
        # candidate can supply the imports of the process that attests its examination. Evidence
        # recorded under a weaker policy is not the same evidence, so it belongs in the identity
        # and a change to it must stale what came before.
        "trustedStartupFlags": list(ISOLATION_FLAGS),
        "checkEnvironment": check_environment,
        "checkRunnerTimeoutSeconds": CHECK_RUNNER_TIMEOUT_SECONDS,
        "network": {"policy": getattr(config, "network_policy", None), "allow": sorted(getattr(config, "network_allow", ()) or ())},
        "readonlyHomePaths": sorted(str(p) for p in (getattr(config, "readonly_home_paths", ()) or ())),
        "sandbox": {"backend": "bubblewrap", "namespaces": ["--unshare-all", "--unshare-user"], "systemImageReadOnly": True},
        # The ceilings the workload was PERMITTED. This belongs in the requirement identity
        # because changing what a run was allowed to consume changes what its result means: a
        # suite that passed under 32 GB is not the same evidence as one that passed under 2 GB.
        # The machine's free memory at the time is deliberately NOT here — that is admission
        # state, and hashing it would stale every world whenever the host got busier.
        "resourcePolicy": _resource_policy_canonical(config),
    }


def _resource_policy_canonical(config: Any) -> dict[str, Any] | None:
    try:
        policy = getattr(config, "resource_policy", None)
    except Exception:  # noqa: BLE001 - an unreadable policy must not break the identity
        return None
    return policy.canonical() if policy is not None else None


def requirements(project: ProjectConfig, roots: Sequence[Mapping[str, Any]], sources: Mapping[str, Path], config: Any, policy_source_sha256: str | None, core: Core | None = None) -> dict[str, Any]:
    """The requirement half of a context: what a candidate must have been evaluated against."""
    value = {
        "schemaVersion": VALIDATION_CONTEXT_SCHEMA,
        "policy": {"canonical": canonical_policy(project), "sourceSha256": policy_source_sha256, "requiredChecks": sorted(c.id for c in project.checks if c.required), "warnings": policy_warnings(project, _primary_source(roots, sources))},
        "verifiers": resolve_verifiers(project, roots, sources),
        "execution": execution_context(config),
    }
    value["requirementHash"] = requirement_hash(value, core)
    return value


def _primary_source(roots: Sequence[Mapping[str, Any]], sources: Mapping[str, Path]) -> Path:
    primary = next((r for r in roots if r.get("primary_root") or r.get("primary")), None)
    if primary is None or primary["root_key"] not in sources:
        raise WorldlineError("NO_PRIMARY_ROOT", "the primary root's tree is not available for verifier resolution")
    return Path(sources[primary["root_key"]])


def policy_warnings(project: ProjectConfig, primary_source: Path) -> list[str]:
    """Documented limits of the default verifier scope, stated per check against the actual
    tree: a check whose argv names no existing file (`make test`, `-m pytest`, `npm test`,
    `bash -c …`) binds NO verifier; a top-level verifier without a `verifiers` declaration
    binds only itself; an argv operand under the check's own covers is candidate data.
    Declaring `verifiers` closes every one of these."""
    out: list[str] = []

    def exists(relative: str) -> bool:
        path = Path(primary_source) / relative
        return path.is_file() and not path.is_symlink()

    for check in project.checks:
        named_existing: list[str] = []
        for named in check.named_paths():
            if not exists(named):
                continue
            if check.covers_path(named):
                out.append(f"check {check.id}: argv names {named}, which its covers globs match; it is treated as candidate-owned data, not as a verifier — declare `verifiers` if it is the examiner")
                continue
            named_existing.append(named)
        if check.verifiers:
            continue
        if not named_existing:
            out.append(f"check {check.id}: argv names no file in the root, so no verifier is bound (a Makefile, conftest.py, package.json or an inline script escapes the evidence identity) — declare `verifiers` to bind its examiner")
            continue
        for named in named_existing:
            if os.path.dirname(named) in ("", "."):
                # This used to be a warned LIMIT: the unbound sibling stayed importable, so the
                # check passed while a forged helper went undetected. Verifiers are now staged
                # from PRIME and executed from the staging directory, so an undeclared helper is
                # not there at all and the check FAILS. That is the right posture -- an
                # undeclared dependency is not authoritative, and running it anyway was the
                # hole -- but the warning has to say what will actually happen.
                out.append(f"check {check.id}: only the named top-level verifier {named} is bound, so it is the only file staged; anything it imports from beside it will NOT be found and the check will FAIL — declare `verifiers` to bind and stage them")
    return out


def requirement_hash(value: Mapping[str, Any], core: Core | None = None) -> str:
    """Identity of a requirement. Semantic, not byte-level: the policy enters through its
    canonical form (checks sorted by id, keys ordered, defaults applied), so two policy files
    that mean the same thing (reordered checks, whitespace, key order) share one identity, while
    any change to a check's id, argv, cwd, required flag, result format, covered paths or the
    protected list changes it. The raw policy digest is carried for diagnosis only."""
    hashed = {k: v for k, v in value.items() if k != "requirementHash"}
    hashed["policy"] = {k: v for k, v in dict(value.get("policy") or {}).items() if k not in ("sourceSha256", "warnings")}
    return _digest(hashed, core)


def build_context(
    *,
    requirement: Mapping[str, Any],
    candidate: Mapping[str, Any],
    prime_at_fork: Mapping[str, Any],
    roots: Sequence[Mapping[str, Any]],
    results: Sequence[Mapping[str, Any]],
    candidate_verifiers: Sequence[Mapping[str, Any]],
    adapter: Mapping[str, Any],
    evaluated_at: str,
    core: Core | None = None,
    source: str = "finalization",
) -> dict[str, Any]:
    """The full context bound to one evaluation. Informational fields (adapter, model argv,
    times) are recorded but are NOT part of the requirement hash."""
    # A verifier the candidate rewrote, deleted, or redirected (turned into a symlink or other
    # non-regular file, which resolve_verifiers leaves out) is named here, and so is any file
    # the candidate ADDED inside a verifier scope (a shadow package or module beside the exam
    # changes what the exam imports without touching a byte of it). Either way the evidence
    # came from something other than the authoritative verifier tree.
    expected = {(v["rootKey"], v["path"]): v["sha256"] for v in requirement.get("verifiers", [])}
    present = {(c["rootKey"], c["path"]): c["sha256"] for c in candidate_verifiers}
    modified = sorted(
        {f"{key[0]}:{key[1]}" for key, digest in expected.items() if present.get(key) != digest}
        | {f"{key[0]}:{key[1]} (added)" for key in present if key not in expected}
    )
    value = {
        "schemaVersion": VALIDATION_CONTEXT_SCHEMA,
        "requirement": dict(requirement),
        "requirementHash": requirement["requirementHash"],
        "candidate": dict(candidate),
        "primeAtFork": dict(prime_at_fork),
        "roots": sorted(({"rootKey": r["root_key"], "path": (os.fsdecode(bytes(r["path"])) if isinstance(r["path"], (bytes, bytearray)) else str(r["path"])), "kind": r["kind"]} for r in roots), key=lambda r: r["rootKey"]),
        "results": [{"id": r.get("id"), "status": r.get("status"), "required": r.get("required"), "exitCode": r.get("exitCode")} for r in results],
        "candidateVerifiers": list(candidate_verifiers),
        "verifiersModifiedByCandidate": modified,
        "adapter": dict(adapter),
        "evaluatedAt": evaluated_at,
        "source": source,
    }
    value["contextHash"] = _digest({k: v for k, v in value.items() if k != "contextHash"}, core)
    return value


def verify_context(context: Any, *, candidate_instance: str, core: Core | None = None) -> dict[str, Any]:
    """Structural and integrity verification of a stored context. Raises with a stable code."""
    if context is None:
        raise WorldlineError("EVIDENCE_CONTEXT_MISSING", "the candidate's evidence carries no validation context; run `worldline revalidate` or fork a new candidate")
    if not isinstance(context, dict) or context.get("schemaVersion") != VALIDATION_CONTEXT_SCHEMA:
        raise WorldlineError("EVIDENCE_CONTEXT_INVALID", "the validation context is malformed or of an unsupported schema", {"schemaVersion": None if not isinstance(context, dict) else context.get("schemaVersion")})
    expected = _digest({k: v for k, v in context.items() if k != "contextHash"}, core)
    if context.get("contextHash") != expected:
        raise WorldlineError("EVIDENCE_CONTEXT_INVALID", "the validation context does not hash to its recorded identity", {"recorded": context.get("contextHash"), "computed": expected})
    requirement = context.get("requirement") or {}
    if not isinstance(requirement, dict) or requirement_hash(requirement, core) != requirement.get("requirementHash") or context.get("requirementHash") != requirement.get("requirementHash"):
        raise WorldlineError("EVIDENCE_CONTEXT_INVALID", "the requirement half of the validation context does not hash to its recorded identity")
    bound = (context.get("candidate") or {}).get("instanceId")
    if bound != candidate_instance:
        raise WorldlineError("EVIDENCE_CONTEXT_INVALID", "the validation context belongs to a different world", {"boundTo": bound, "candidate": candidate_instance})
    return context


def differences(candidate_requirement: Mapping[str, Any], current_requirement: Mapping[str, Any]) -> list[str]:
    """Human- and machine-readable list of what changed between two requirement halves."""
    out: list[str] = []
    a, b = candidate_requirement, current_requirement
    if (a.get("policy") or {}).get("canonical") != (b.get("policy") or {}).get("canonical"):
        ca = {c["id"]: c for c in (a.get("policy") or {}).get("canonical", {}).get("checks", [])}
        cb = {c["id"]: c for c in (b.get("policy") or {}).get("canonical", {}).get("checks", [])}
        for cid in sorted(set(ca) | set(cb)):
            if cid not in ca:
                out.append(f"check added: {cid}")
            elif cid not in cb:
                out.append(f"check removed: {cid}")
            elif ca[cid] != cb[cid]:
                fields = [f for f in ca[cid] if ca[cid].get(f) != cb[cid].get(f)]
                out.append(f"check changed: {cid} ({', '.join(fields)})")
        pa = (a.get("policy") or {}).get("canonical", {}).get("protected"); pb = (b.get("policy") or {}).get("canonical", {}).get("protected")
        if pa != pb:
            out.append("protected paths changed")
        sa = {s["id"]: s for s in (a.get("policy") or {}).get("canonical", {}).get("services", []) if isinstance(s, dict)}
        sb = {s["id"]: s for s in (b.get("policy") or {}).get("canonical", {}).get("services", []) if isinstance(s, dict)}
        for sid in sorted(set(sa) | set(sb)):
            if sid not in sa:
                out.append(f"service added: {sid}")
            elif sid not in sb:
                out.append(f"service removed: {sid}")
            elif sa[sid] != sb[sid]:
                out.append(f"service changed: {sid} ({', '.join(f for f in sa[sid] if sa[sid].get(f) != sb[sid].get(f))})")
        if not out:
            out.append("policy changed")
    va = {(v["rootKey"], v["path"]): v["sha256"] for v in a.get("verifiers", [])}
    vb = {(v["rootKey"], v["path"]): v["sha256"] for v in b.get("verifiers", [])}
    for key in sorted(set(va) | set(vb)):
        if key not in va:
            out.append(f"verifier added: {key[1]}")
        elif key not in vb:
            out.append(f"verifier removed: {key[1]}")
        elif va[key] != vb[key]:
            out.append(f"verifier changed: {key[1]}")
    ea, eb = a.get("execution") or {}, b.get("execution") or {}
    for field in sorted(set(ea) | set(eb)):
        if ea.get(field) != eb.get(field):
            if field == "checkEnvironment" and isinstance(ea.get(field), dict) and isinstance(eb.get(field), dict):
                names = sorted(k for k in set(ea[field]) | set(eb[field]) if ea[field].get(k) != eb[field].get(k))
                out.append(f"execution changed: checkEnvironment ({', '.join(names)})")
            else:
                out.append(f"execution changed: {field}")
    return out


# ----- tested bytes vs staged bytes -----------------------------------------------------------

_CONTENT_FIELDS = ("pathB64", "type", "mode", "contentHash", "size", "target", "xattrs", "acls")


def content_entries(manifest: Any) -> list[dict[str, Any]]:
    """The content-bearing part of a manifest: every entry's path, type, mode, bytes identity,
    symlink target and security attributes. Timestamps, hard-link grouping, root-directory
    metadata and repository facts are excluded: they differ between a payload and a staged copy
    of the same bytes."""
    return [{k: e[k] for k in _CONTENT_FIELDS if k in e} for e in manifest.value["entries"]]


def content_root_set(manifests: Mapping[str, Any], core: Core | None = None) -> str:
    """One identity for the content of a whole root set (root key -> manifest)."""
    verifier = core or Core.shared()
    value = {root_key: content_entries(manifests[root_key]) for root_key in sorted(manifests)}
    return hash_id(verifier.hash_bytes(b"worldline-content-root-set-v1" + canonical_bytes(value)))


def content_differences(candidate: Mapping[str, Any], staged: Mapping[str, Any]) -> list[str]:
    """Paths whose content-bearing entry differs between the tested candidate and the staged
    result, as `rootKey:path`."""
    out: list[str] = []
    for root_key in sorted(set(candidate) | set(staged)):
        a = {e["pathB64"]: e for e in content_entries(candidate[root_key])} if root_key in candidate else {}
        b = {e["pathB64"]: e for e in content_entries(staged[root_key])} if root_key in staged else {}
        for key in sorted(set(a) | set(b)):
            if a.get(key) != b.get(key):
                import base64
                out.append(f"{root_key[:12]}:{base64.b64decode(key).decode('utf-8', 'replace')}")
    return out


def current_requirements(store: Any, config: Any, core: Core | None = None) -> dict[str, Any]:
    """The requirement half imposed by the CURRENT PRIME: its live policy and verifier bytes."""
    roots = store.roots()
    primary = next((r for r in roots if r["primary_root"]), None)
    if primary is None:
        raise WorldlineError("NO_PRIMARY_ROOT", "no primary root is registered")
    live_sources = {r["root_key"]: Path(os.path.realpath(os.fsdecode(bytes(r["path"])))) for r in roots}
    project = ProjectConfig.load(Path(os.fsdecode(bytes(primary["path"]))), store)
    return requirements(project, roots, live_sources, config, project.source_sha256, core)


def effective_evidence(store: Any, world: Any) -> tuple[dict[str, Any] | None, str, list[dict[str, Any]]]:
    """The evaluation that currently speaks for a world, as ONE coherent unit: the freshness
    context, its source, and the check records FROM THE SAME EVALUATION.

    The freshness half and the execution half must come from the same evaluation. A revalidation
    re-runs the checks and stores their records (with the executedVerifierSet the runner wrote);
    its context is what `effective_context` returned. Reading the context from the revalidation
    but the execution records from the world's FINALIZATION evidence assembled one apparently
    complete evaluation from two different runs -- run 2's freshness over run 1's execution
    identity (campaign F5). This returns both halves of whichever evaluation speaks, together.
    """
    for entry in reversed(store.get_meta(f"validation:{world.instance_id}", []) or []):
        ctx = entry.get("context") if isinstance(entry, dict) else None
        if isinstance(ctx, dict) and entry.get("outcome") == "PASS" and entry.get("worldContentId") == world.content_id:
            records = [r for r in (entry.get("results") or []) if isinstance(r, dict)]
            return ctx, f"revalidation:{entry.get('validationId')}", records
    evidence = world.evidence if isinstance(world.evidence, dict) else {}
    ctx = evidence.get("validationContext")
    records = [r for r in (evidence.get("checks") or []) if isinstance(r, dict)]
    return (ctx if isinstance(ctx, dict) else None), "finalization", records


def effective_context(store: Any, world: Any) -> tuple[dict[str, Any] | None, str]:
    """The freshness context and its source. See `effective_evidence` for the coherent records."""
    context, source, _records = effective_evidence(store, world)
    return context, source
