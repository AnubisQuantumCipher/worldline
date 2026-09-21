#!/usr/bin/env python3
"""The release gate: may THIS exact commit be published as THIS version?

Pure decision logic over facts the workflow gathers (assurance report, tag, version file,
changelog, remote tag target, existing release, proof manifest, built artifacts). It is
imported by the dry-run tests and executed by release.yml. It rejects, by name:

  * an assurance run for another commit or tree, a dirty checkout, or a run that is not PASS;
  * any required step missing, skipped, cancelled, timed out or failed (no partial credit);
  * a tag that does not match the runtime version, or a version without a changelog section;
  * proof evidence that is missing, has exceptions, is below the floor, or covers other sources
    than the committed manifest;
  * a remote tag that already points elsewhere, or an already published release (published
    versions never move);
  * an artifact whose digest is not the one computed from the release tree, or an artifact set
    that differs from the expected one.

It never consults "latest green CI on main": the only run it accepts is the one whose report
names the release commit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

REQUIRED_STEPS = ("checkout-identity", "clean-build-tree", "build", "ada-tests", "ada-fuzz", "python-tests", "proof-gate", "proof-manifest")
SCHEMA = 1


@dataclass
class Verdict:
    accepted: bool
    reasons: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {"accepted": self.accepted, "reasons": list(self.reasons)}


def _sha(value: Any) -> str | None:
    return value if isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value) else None


def evaluate(
    *,
    release_sha: str,
    release_tree: str,
    tag: str,
    tag_target_sha: str,
    version: str,
    changelog: str,
    assurance: Mapping[str, Any] | None,
    committed_proof_manifest: Mapping[str, Any] | None,
    remote_tag_sha: str | None,
    release_exists: bool,
    artifacts: Mapping[str, str],
    expected_artifacts: Mapping[str, str],
    max_skipped: int = 3,
) -> Verdict:
    reasons: list[str] = []

    # -- identity of what is being released
    if _sha(release_sha) is None:
        reasons.append("release commit is not a full 40-hex sha")
    if _sha(tag_target_sha) != release_sha:
        reasons.append(f"tag {tag} resolves to {tag_target_sha}, not the release commit {release_sha}")
    if not re.fullmatch(r"v\d+\.\d+\.\d+", tag):
        reasons.append(f"tag {tag} is not a vMAJOR.MINOR.PATCH release tag")
    elif tag[1:] != version:
        reasons.append(f"tag {tag} does not match the runtime version {version}")
    if not re.search(rf"^## {re.escape(version)} ", changelog, re.M):
        reasons.append(f"CHANGELOG.md has no section for {version}")

    # -- the assurance run must be THIS commit's, complete, and PASS
    if not isinstance(assurance, Mapping):
        reasons.append("assurance report is missing")
    else:
        checkout = assurance.get("checkout") or {}
        if checkout.get("sha") != release_sha:
            reasons.append(f"assurance run belongs to {checkout.get('sha')}, not the release commit {release_sha}")
        if checkout.get("tree") != release_tree:
            reasons.append(f"assurance tree {checkout.get('tree')} differs from the release tree {release_tree}")
        if checkout.get("dirty") is not False:
            reasons.append("assurance ran on a dirty or unrecorded checkout")
        if checkout.get("expectedSha") not in (None, release_sha):
            reasons.append("assurance was asked to verify a different commit")
        if assurance.get("result") != "PASS":
            reasons.append(f"assurance result is {assurance.get('result')!r}, not PASS")
        steps = {s.get("name"): s for s in assurance.get("steps") or [] if isinstance(s, Mapping)}
        for name in REQUIRED_STEPS:
            step = steps.get(name)
            if step is None:
                reasons.append(f"required step missing from the assurance run: {name}")
            elif step.get("status") != "success":
                reasons.append(f"required step {name} is {step.get('status')!r}, not success")
        recorded_required = assurance.get("requiredSteps")
        if recorded_required is not None and set(recorded_required) != set(REQUIRED_STEPS):
            reasons.append("the assurance run's required-step list differs from this gate's")
        python_tests = assurance.get("pythonTests") or {}
        if not python_tests.get("ok") or (python_tests.get("failures") or 0) or (python_tests.get("errors") or 0) or not python_tests.get("ran"):
            reasons.append("python tests did not pass cleanly in the assurance run")
        if (python_tests.get("skipped") or 0) > max_skipped:
            reasons.append(f"python tests skipped {python_tests.get('skipped')} cases, more than the allowed {max_skipped}; a host that cannot run the suite cannot assure a release")
        if assurance.get("runtimeVersion") != version:
            reasons.append(f"assurance recorded runtime version {assurance.get('runtimeVersion')}, release is {version}")

        # -- proof evidence: fresh, complete, and about the committed sources
        proof = assurance.get("proof") or {}
        regenerated = proof.get("regeneratedManifest") or {}
        if not regenerated.get("present"):
            reasons.append("assurance run has no regenerated proof manifest (proof gate did not run)")
        else:
            for key in ("unproved", "justified", "pragmaAssume"):
                if regenerated.get(key) != 0:
                    reasons.append(f"proof manifest records {key}={regenerated.get(key)}")
            total, floor = regenerated.get("total"), regenerated.get("minimumChecks")
            if not isinstance(total, int) or not isinstance(floor, int) or total < floor:
                reasons.append(f"proof total {total} is below the floor {floor}")
            if not isinstance(committed_proof_manifest, Mapping):
                reasons.append("committed proof manifest is missing")
            elif committed_proof_manifest.get("sourceHashes") != regenerated.get("sourceHashes"):
                reasons.append("the proof re-run covers different sources than the committed proof manifest")
        if proof.get("consistent") is not True:
            reasons.append("assurance did not record a consistent proof")

    # -- never move a published version
    if remote_tag_sha is not None and remote_tag_sha != release_sha:
        reasons.append(f"tag {tag} already exists on the remote at {remote_tag_sha}")
    if release_exists:
        reasons.append(f"a release for {tag} already exists; published versions are never replaced")

    # -- artifacts are exactly what the release tree produced
    if set(artifacts) != set(expected_artifacts):
        reasons.append(f"artifact set differs: have {sorted(artifacts)}, expected {sorted(expected_artifacts)}")
    for name, digest in sorted(expected_artifacts.items()):
        if name in artifacts and artifacts[name] != digest:
            reasons.append(f"artifact {name} digest {artifacts[name]} differs from the expected {digest}")

    return Verdict(accepted=not reasons, reasons=reasons)


def release_manifest(*, verdict: Verdict, release_sha: str, release_tree: str, tag: str, version: str, assurance: Mapping[str, Any], artifacts: Mapping[str, str], notes_sha256: str | None, signing: Mapping[str, Any]) -> dict[str, Any]:
    proof = (assurance.get("proof") or {}).get("regeneratedManifest") or {}
    return {
        "schemaVersion": SCHEMA,
        "accepted": verdict.accepted,
        "reasons": list(verdict.reasons),
        "tag": tag,
        "version": version,
        "commit": release_sha,
        "tree": release_tree,
        "sourceOnly": True,
        "assurance": {
            "result": assurance.get("result"),
            "startedAt": assurance.get("startedAt"),
            "finishedAt": assurance.get("finishedAt"),
            "host": assurance.get("host"),
            "toolchain": assurance.get("toolchain"),
            "steps": [{"name": s.get("name"), "status": s.get("status"), "durationSeconds": s.get("durationSeconds"), "logSha256": s.get("logSha256")} for s in assurance.get("steps") or []],
            "pythonTests": assurance.get("pythonTests"),
        },
        "proof": {k: proof.get(k) for k in ("total", "minimumChecks", "unproved", "justified", "pragmaAssume", "librarySha256", "manifestSha256")},
        "artifacts": [{"name": name, "sha256": digest} for name, digest in sorted(artifacts.items())],
        "notesSha256": notes_sha256,
        "signing": dict(signing),
        "nonClaims": [
            "A source-only archive: the proved library is rebuilt by the installer; its hash on another machine may differ from the one recorded here.",
            "Assurance covers the listed steps on the listed host; it is not a statement about other environments.",
            "Publication does not authorize installation into any production instance.",
        ],
    }


def _digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--release-sha", required=True)
    parser.add_argument("--release-tree", required=True)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--tag-target-sha", required=True)
    parser.add_argument("--version-file", required=True)
    parser.add_argument("--changelog", required=True)
    parser.add_argument("--assurance", required=True, help="assurance.json (or a path that does not exist, to record its absence)")
    parser.add_argument("--proof-manifest", required=True)
    parser.add_argument("--remote-tag-sha", default="none", help="dereferenced commit the remote tag points to, or 'none'")
    parser.add_argument("--release-exists", choices=("yes", "no"), required=True)
    parser.add_argument("--artifact", action="append", default=[], help="NAME=PATH (digest computed)")
    parser.add_argument("--expected-artifact", action="append", default=[], help="NAME=SHA256 (independently computed)")
    parser.add_argument("--notes", help="release notes file (its digest is recorded)")
    parser.add_argument("--signing", default="unsigned", help="how the tag/assets are signed (recorded verbatim; 'unsigned' is an honest value)")
    parser.add_argument("--max-skipped", type=int, default=3, help="most skipped python tests an assurance run may have and still be accepted")
    parser.add_argument("--write-manifest", help="write release-manifest.json here")
    args = parser.parse_args()

    version_text = Path(args.version_file).read_text(encoding="utf-8")
    match = re.search(r'^__version__\s*=\s*"([^"]+)"', version_text, re.M)
    version = match.group(1) if match else ""
    assurance = json.loads(Path(args.assurance).read_text(encoding="utf-8")) if Path(args.assurance).is_file() else None
    manifest = json.loads(Path(args.proof_manifest).read_text(encoding="utf-8")) if Path(args.proof_manifest).is_file() else None
    artifacts = {}
    for item in args.artifact:
        name, _, path = item.partition("=")
        artifacts[name] = _digest_file(Path(path))
    expected = {}
    for item in args.expected_artifact:
        name, _, digest = item.partition("=")
        expected[name] = digest
    verdict = evaluate(
        release_sha=args.release_sha, release_tree=args.release_tree, tag=args.tag, tag_target_sha=args.tag_target_sha,
        version=version, changelog=Path(args.changelog).read_text(encoding="utf-8"), assurance=assurance,
        committed_proof_manifest=manifest, remote_tag_sha=None if args.remote_tag_sha == "none" else args.remote_tag_sha,
        release_exists=args.release_exists == "yes", artifacts=artifacts, expected_artifacts=expected, max_skipped=args.max_skipped,
    )
    if args.write_manifest:
        notes_sha = _digest_file(Path(args.notes)) if args.notes and Path(args.notes).is_file() else None
        document = release_manifest(verdict=verdict, release_sha=args.release_sha, release_tree=args.release_tree, tag=args.tag, version=version, assurance=assurance or {}, artifacts=artifacts, notes_sha256=notes_sha, signing={"method": args.signing})
        Path(args.write_manifest).write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(verdict.as_dict(), indent=2))
    return 0 if verdict.accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
