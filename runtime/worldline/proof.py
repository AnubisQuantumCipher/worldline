"""What a receipt's `invariantPreservation` states (1.9.2, OB-084).

PROVED means: the library this process has mapped is the one a zero-exception proof at or
above the floor was run for, with every pinned contract and every proof source as the manifest
records them -- recomputed here from the proof sources installed beside the library, not taken
from the manifest's word -- and the proof actually ran for this installation. Anything less has
its own name:

* MANIFEST_ONLY -- every manifest check passes, but the install skipped the proof
  (WORLDLINE_SKIP_PROOF=1) or did not record that it ran;
* TEST_LIBRARY -- the library was chosen by WORLDLINE_CORE_LIB, a test build's seam;
* UNVERIFIED -- a check failed, or could not be made; the failing check is named.

`inspect` never raises: a malformed manifest used to fail after COMMITTED was written. When the
manifest cannot be evaluated at all it says so (`evaluable: false`), and the promotion guard
refuses BEFORE any exchange (transaction._pre_exchange_guards).

What this does not do (OB-039): authenticate the manifest. A same-account writer who replaces
the manifest, the installed proof sources and the library consistently still reads PROVED.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from . import proof_manifest
from .core import Core, hash_id

SCHEMA = "worldline-proof-status-v2"
SUMMARY_NAME = "proof-summary.out"
GATE_NAME = "proof-gate.json"
SOURCES_NAME = "proof-sources"
SOURCE_TREE_SUMMARY = "obj/core-library/gnatprove/gnatprove.out"


def _mapped_identity(path: Path) -> tuple[int, int] | None:
    """(device, inode) of `path` as this process has it mapped, from /proc/self/maps."""
    try:
        text = Path("/proc/self/maps").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    wanted = str(path)
    for line in text.splitlines():
        parts = line.split(None, 5)
        if len(parts) == 6 and parts[5] == wanted:
            major, _, minor = parts[3].partition(":")
            try:
                return os.makedev(int(major, 16), int(minor, 16)), int(parts[4])
            except ValueError:
                return None
    return None


def _hash_mapped(path: Path) -> tuple[str | None, str | None]:
    """The digest of the library through a descriptor whose inode must be the mapped object's,
    so what is hashed is what was loaded (a replaced file at the same path is a different
    inode). Returns (sha256, problem)."""
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    except OSError as exc:
        return None, f"the library cannot be opened: {exc}"
    try:
        info = os.fstat(descriptor)
        mapped = _mapped_identity(path)
        if mapped is None:
            return None, "the library is not mapped by this process under its path"
        if mapped != (info.st_dev, info.st_ino):
            return None, "the file at the library's path is not the object this process mapped"
        digest = hashlib.sha256()
        with os.fdopen(os.dup(descriptor), "rb") as handle:
            for block in iter(lambda: handle.read(1 << 20), b""):
                digest.update(block)
        return digest.hexdigest(), None
    except OSError as exc:
        return None, f"the library cannot be read: {exc}"
    finally:
        os.close(descriptor)


class ProofStatus:
    @staticmethod
    def locate(library: Path) -> dict[str, Any]:
        """Where the manifest, the proof sources, the summary and the gate record are: beside
        an installed library, or in the source tree this runtime belongs to."""
        project_root = Path(__file__).resolve().parents[2]
        if (library.parent / "proof-manifest.json").is_file():
            base = library.parent
            return {"layout": "installed", "manifest": base / "proof-manifest.json", "sources": base / SOURCES_NAME,
                    "summary": base / SUMMARY_NAME, "gate": base / GATE_NAME}
        return {"layout": "source-tree", "manifest": project_root / "proof-manifest.json", "sources": project_root,
                "summary": project_root / SOURCE_TREE_SUMMARY, "gate": None}

    @staticmethod
    def inspect(core: Core | None = None) -> dict[str, Any]:
        try:
            return ProofStatus._inspect(core or Core.shared())
        except Exception as exc:  # noqa: BLE001 - total by design: never raise after COMMITTED
            return {"state": "UNVERIFIED", "evaluable": False, "reason": f"the proof status could not be evaluated: {type(exc).__name__}: {exc}",
                    "manifest": None, "verification": {"schema": SCHEMA, "checks": [{"name": "evaluation", "ok": False, "detail": str(exc)}]}}

    @staticmethod
    def _inspect(verifier: Core) -> dict[str, Any]:
        library = Path(verifier.library_path)
        source = getattr(verifier, "library_source", "explicit")
        where = ProofStatus.locate(library)
        checks: list[dict[str, Any]] = []

        def record(name: str, ok: bool, detail: Any = None) -> bool:
            checks.append({"name": name, "ok": bool(ok), **({"detail": detail} if detail is not None else {})})
            return ok

        base: dict[str, Any] = {"manifest": str(where["manifest"]), "library": {"path": str(library), "source": source},
                                "layout": where["layout"]}
        record("library-selection", source != "environment",
               "chosen by WORLDLINE_CORE_LIB (a test build's seam)" if source == "environment" else source)

        # -- evaluable at all?
        manifest: Any = None
        manifest_bytes: bytes | None = None
        problem: str | None = None
        if not where["manifest"].is_file():
            problem = "proof-manifest.json is missing"
        else:
            try:
                manifest_bytes = where["manifest"].read_bytes()
                manifest = json.loads(manifest_bytes.decode("utf-8"))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                problem = f"proof manifest is invalid: {exc}"
            else:
                if not isinstance(manifest, dict) or not isinstance(manifest.get("proof"), dict) \
                        or not isinstance(manifest.get("library"), dict) or not isinstance(manifest.get("coverage"), dict) \
                        or not isinstance(manifest.get("sourceHashes"), dict):
                    problem = "proof manifest is malformed: proof, library, coverage and sourceHashes must be objects"
        record("manifest-readable", problem is None, problem)
        if problem is not None:
            return {**base, "state": "UNVERIFIED", "evaluable": False, "reason": problem,
                    "verification": {"schema": SCHEMA, "checks": checks}}

        # -- the gate's own checks, against the proof sources beside the library
        sources: Path = where["sources"]
        record("proof-sources-present", sources.is_dir(), str(sources))
        library_sha, library_problem = _hash_mapped(library)
        record("library-identity", library_problem is None and library_sha is not None, library_problem or library_sha)
        summary_bytes: bytes | None = None
        if where["summary"].is_file():
            try:
                summary_bytes = where["summary"].read_bytes()
            except OSError:
                summary_bytes = None
        findings = proof_manifest.manifest_findings(manifest, sources, library_sha256=library_sha or "unavailable")
        for name in proof_manifest.CHECK_NAMES:
            if name == "summary":
                continue
            failed = [text for check, text in findings if check == name]
            record(name, not failed, failed[0] if failed else None)
        manifest_ok = not findings and library_problem is None and sources.is_dir()

        # -- did the proof run for this installation?
        if where["layout"] == "installed":
            gate = "unrecorded"
            try:
                recorded_gate = json.loads(where["gate"].read_text(encoding="utf-8"))
                if isinstance(recorded_gate, dict) and recorded_gate.get("proofGate") in ("ran", "skipped"):
                    gate = recorded_gate["proofGate"]
            except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                gate = "unrecorded"
        else:
            gate = "ran" if summary_bytes is not None else "unrecorded"
        record("proof-gate", gate == "ran", gate)
        summary_ok = False
        if summary_bytes is None:
            record("summary", False, "no proof summary beside the manifest")
        else:
            summary_found = proof_manifest.summary_problems(manifest, summary_bytes)
            summary_ok = record("summary", not summary_found, summary_found[0] if summary_found else "digest and counts re-derived")

        proof = manifest["proof"]
        facts = {**base, "evaluable": True, "proofGate": gate,
                 "manifestHash": hash_id(verifier.hash_bytes(manifest_bytes)) if manifest_bytes is not None else None,
                 "checks": proof.get("total"), "boundary": manifest.get("boundary"),
                 "library": {**base["library"], "sha256": library_sha},
                 "verification": {"schema": SCHEMA, "checks": checks}}
        if source == "environment":
            return {**facts, "state": "TEST_LIBRARY", "reason": "the library was chosen by WORLDLINE_CORE_LIB"}
        if not manifest_ok:
            failed = next(item for item in checks if not item["ok"] and item["name"] not in ("proof-gate", "summary"))
            return {**facts, "state": "UNVERIFIED", "reason": f"{failed['name']}: {failed.get('detail')}"}
        if gate == "ran" and summary_ok:
            return {**facts, "state": "PROVED"}
        if gate == "ran":
            return {**facts, "state": "UNVERIFIED", "reason": "the install records that the proof ran, but its summary does not verify"}
        return {**facts, "state": "MANIFEST_ONLY",
                "reason": "every manifest check passes, but the proof was not run for this installation" if gate == "skipped"
                else "every manifest check passes, but nothing records that the proof ran for this installation"}
