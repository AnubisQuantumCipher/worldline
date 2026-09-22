#!/usr/bin/env python3
"""Full assurance of ONE exact commit, recorded from actual outcomes.

Runs, in order and without skipping: the kernel/test build, the Ada behaviour tests, the Ada
fuzz run, the Python suite (which includes the deterministic freshness regressions), the SPARK
proof gate (re-proving every unit on this build) and the proof-manifest verification with the
library checked. Every step's exit status, duration and log digest is recorded, together with
the checkout identity (commit, tree, cleanliness), the runtime version and the toolchain
identities, in `<out>/assurance.json`. The result is PASS only if every required step
succeeded and the checkout is the expected commit with a clean tree.

The report is what a release may rely on. It never says more than it measured: a PASS names
the commit and tree it ran on, the toolchain that built and proved it, and the counts it read
back from the tools.

    scripts/assurance.py run --out assurance [--expect-sha <full sha>]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = 1

REQUIRED_STEPS = ("checkout-identity", "clean-build-tree", "build", "ada-tests", "ada-fuzz", "python-tests", "evaluation-domain", "proof-gate", "proof-manifest")


def _utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _run(argv: list[str], *, env: dict[str, str] | None = None, cwd: Path = ROOT) -> tuple[int, bytes]:
    process = subprocess.run(argv, cwd=cwd, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return process.returncode, process.stdout


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()


def _version_line(argv: list[str]) -> str | None:
    try:
        code, out = _run(argv)
    except OSError:
        return None
    if code != 0:
        return None
    return out.decode("utf-8", "replace").splitlines()[0].strip() if out.strip() else None


def runtime_version() -> str:
    text = (ROOT / "runtime/worldline/__init__.py").read_text(encoding="utf-8")
    match = re.search(r'^__version__\s*=\s*"([^"]+)"', text, re.M)
    if match is None:
        raise SystemExit("assurance: runtime version not found")
    return match.group(1)


def parse_unittest(output: str) -> dict[str, Any]:
    ran = re.search(r"^Ran (\d+) tests? in", output, re.M)
    tail = output.strip().splitlines()[-1] if output.strip() else ""
    counts = {"failures": 0, "errors": 0, "skipped": 0, "expectedFailures": 0, "unexpectedSuccesses": 0}
    for key, name in (("failures", "failures"), ("errors", "errors"), ("skipped", "skipped"), ("expectedFailures", "expected failures"), ("unexpectedSuccesses", "unexpected successes")):
        found = re.search(rf"{name}=(\d+)", tail)
        if found:
            counts[key] = int(found.group(1))
    ok = tail.startswith("OK") and ran is not None
    return {"ran": int(ran.group(1)) if ran else None, "ok": ok, "verdictLine": tail, **counts}


def proof_facts(manifest_path: Path) -> dict[str, Any]:
    if not manifest_path.is_file():
        return {"present": False}
    raw = manifest_path.read_bytes()
    manifest = json.loads(raw.decode("utf-8"))
    proof = manifest.get("proof", {})
    return {
        "present": True,
        "manifestSha256": hashlib.sha256(raw).hexdigest(),
        "total": proof.get("total"),
        "minimumChecks": proof.get("minimumChecks"),
        "unproved": proof.get("unproved"),
        "justified": proof.get("justified"),
        "pragmaAssume": proof.get("pragmaAssume"),
        "librarySha256": (manifest.get("library") or {}).get("sha256"),
        "sourceHashes": manifest.get("sourceHashes"),
        "claim": manifest.get("claim"),
    }


class Runner:
    def __init__(self, out: Path) -> None:
        self.out = out
        self.out.mkdir(parents=True, exist_ok=True)
        self.steps: list[dict[str, Any]] = []

    def step(self, name: str, argv: list[str] | None = None, *, env: dict[str, str] | None = None, check=None, action=None) -> bool:
        started = time.monotonic()
        log_path = self.out / f"{name}.log"
        status, code, output, summary = "success", 0, b"", None
        try:
            if action is not None:
                summary = action()
            else:
                assert argv is not None
                code, output = _run(argv, env=env)
                if code != 0:
                    status = "failure"
                elif check is not None:
                    summary = check(output.decode("utf-8", "replace"))
                    if summary is not None and summary.get("ok") is False:
                        status = "failure"
        except Exception as exc:  # recorded, never hidden
            status, summary = "failure", {"exception": f"{type(exc).__name__}: {exc}"}
        log_path.write_bytes(output)
        record = {
            "name": name,
            "status": status,
            "exitCode": code,
            "durationSeconds": round(time.monotonic() - started, 3),
            "argv": argv,
            "logSha256": hashlib.sha256(output).hexdigest(),
            "logPath": str(log_path.relative_to(self.out)),
            "summary": summary,
        }
        self.steps.append(record)
        print(f"[assurance] {name}: {status} ({record['durationSeconds']}s)", flush=True)
        return status == "success"


def run(out: Path, expect_sha: str | None) -> int:
    started_at = _utc()
    runner = Runner(out)
    env = {**os.environ, "PYTHONPATH": str(ROOT / "runtime"), "PYTHONDONTWRITEBYTECODE": "1"}

    identity: dict[str, Any] = {}

    def checkout_identity() -> dict[str, Any]:
        sha = _git("rev-parse", "HEAD")
        tree = _git("rev-parse", "HEAD^{tree}")
        dirty = _git("status", "--porcelain", "--untracked-files=no")
        identity.update({"sha": sha, "tree": tree, "dirty": bool(dirty), "dirtyPaths": dirty.splitlines()[:50], "expectedSha": expect_sha})
        ok = not dirty and (expect_sha is None or expect_sha == sha)
        return {"ok": ok, **identity, "reason": None if ok else ("dirty checkout" if dirty else "HEAD is not the expected commit")}

    committed_manifest = proof_facts(ROOT / "proof-manifest.json")
    ok = runner.step("checkout-identity", action=checkout_identity)

    def clean_build_tree() -> dict[str, Any]:
        # A stale object directory lets gprbuild skip compilation and lets gnatprove replay its
        # session instead of re-proving; assurance rebuilds and re-proves from nothing.
        removed = []
        for rel in ("obj", "bin", "lib/gnatprove"):
            target = ROOT / rel
            if target.exists():
                shutil.rmtree(target)
                removed.append(rel)
        for library in (ROOT / "lib").glob("*.so"):
            library.unlink()
            removed.append(str(library.relative_to(ROOT)))
        return {"ok": True, "removed": removed}

    ok = runner.step("clean-build-tree", action=clean_build_tree) and ok
    ok = runner.step("build", ["gprbuild", "-q", "-P", "worldline.gpr"]) and ok
    ok = runner.step("ada-tests", ["./bin/worldline_core_tests"], check=lambda o: {"ok": "PASS" in o, "line": o.strip().splitlines()[-1] if o.strip() else ""}) and ok
    ok = runner.step("ada-fuzz", ["./bin/worldline_core_fuzz"], check=lambda o: {"ok": "PASS" in o, "line": o.strip().splitlines()[-1] if o.strip() else ""}) and ok
    ok = runner.step("python-tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"], env=env, check=parse_unittest) and ok
    # The evaluation-domain gate is REQUIRED, not advisory, and it runs two arms. The candidate
    # build must hold every property including positive evidence that the intended examiner ran;
    # the preserved counterexample must FAIL, because a gate that only checks the candidate
    # cannot tell "the vulnerability is fixed" from "the instrument stopped working". Keeping
    # this out of the release decision until it passed would be the missing-roster problem in
    # another form: the ordinary suite stays green while the most important known security
    # requirement is absent from the decision.
    def evaluation_domain() -> dict[str, Any]:
        counterexample = ROOT / "assurance" / "counterexample-runtime"
        tag = "counterexample/verifier-bytes-without-evaluation-domain"
        materialised = False
        try:
            counterexample.mkdir(parents=True, exist_ok=True)
            archive = subprocess.run(["git", "-C", str(ROOT), "archive", "--format=tar", tag, "runtime"],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            if archive.returncode == 0 and archive.stdout:
                subprocess.run(["tar", "-x", "-C", str(counterexample)], input=archive.stdout, check=True)
                materialised = (counterexample / "runtime" / "worldline").is_dir()
        except (OSError, subprocess.SubprocessError):
            materialised = False
        command = [sys.executable, str(ROOT / "scripts/evaluation_domain_gate.py"),
                   "--engine", str(ROOT / "runtime"),
                   "--core-lib", str(ROOT / "lib/libworldline_core.so")]
        if materialised:
            command += ["--counterexample", str(counterexample / "runtime")]
        proc = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              text=True, timeout=1800, env=env)
        return {"ok": proc.returncode == 0,
                "counterexampleControl": "ran" if materialised else
                                         "UNAVAILABLE — the preserved tag could not be materialised,"
                                         " so only the candidate arm was checked",
                "tail": proc.stdout[-4000:]}

    ok = runner.step("evaluation-domain", action=evaluation_domain) and ok
    ok = runner.step("proof-gate", ["./prove.sh"]) and ok
    ok = runner.step("proof-manifest", [sys.executable, "verify_proof_manifest.py"]) and ok
    regenerated = proof_facts(ROOT / "proof-manifest.json")

    # The proof gate regenerates the manifest on this build. The proved source set must be the
    # committed one; the library hash may legitimately differ per toolchain/architecture.
    proof_consistent = (
        committed_manifest.get("present") and regenerated.get("present")
        and committed_manifest.get("sourceHashes") == regenerated.get("sourceHashes")
        and regenerated.get("unproved") == 0 and regenerated.get("justified") == 0 and regenerated.get("pragmaAssume") == 0
        and isinstance(regenerated.get("total"), int) and isinstance(regenerated.get("minimumChecks"), int)
        and regenerated["total"] >= regenerated["minimumChecks"]
    )
    steps_ok = all(any(s["name"] == name and s["status"] == "success" for s in runner.steps) for name in REQUIRED_STEPS)
    result = "PASS" if ok and steps_ok and proof_consistent else "FAIL"
    report = {
        "schemaVersion": SCHEMA,
        "result": result,
        "startedAt": started_at,
        "finishedAt": _utc(),
        "checkout": identity,
        "runtimeVersion": runtime_version(),
        "toolchain": {
            "gnat": _version_line(["gnat", "--version"]),
            "gprbuild": _version_line(["gprbuild", "--version"]),
            "gnatprove": _version_line(["gnatprove", "--version"]),
            "python": sys.version.split()[0],
            "bubblewrap": _version_line(["bwrap", "--version"]),
            "systemd": _version_line(["systemctl", "--version"]),
        },
        "host": {"machine": platform.machine(), "system": platform.system(), "release": platform.release(), "githubRunId": os.environ.get("GITHUB_RUN_ID"), "githubRunAttempt": os.environ.get("GITHUB_RUN_ATTEMPT"), "githubRepository": os.environ.get("GITHUB_REPOSITORY"), "githubServer": os.environ.get("GITHUB_SERVER_URL")},
        "requiredSteps": list(REQUIRED_STEPS),
        "steps": runner.steps,
        "pythonTests": next((s["summary"] for s in runner.steps if s["name"] == "python-tests"), None),
        "proof": {"committedManifest": committed_manifest, "regeneratedManifest": regenerated, "consistent": bool(proof_consistent)},
    }
    (out / "assurance.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[assurance] result {result} for {identity.get('sha')} (tree {identity.get('tree')})", flush=True)
    return 0 if result == "PASS" else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    runp = sub.add_parser("run")
    runp.add_argument("--out", required=True)
    runp.add_argument("--expect-sha")
    args = parser.parse_args()
    if args.command == "run":
        expect = args.expect_sha
        if expect is not None and not re.fullmatch(r"[0-9a-f]{40}", expect):
            print("assurance: --expect-sha must be a full 40-hex commit id", file=sys.stderr)
            return 2
        return run(Path(args.out).resolve(), expect)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
