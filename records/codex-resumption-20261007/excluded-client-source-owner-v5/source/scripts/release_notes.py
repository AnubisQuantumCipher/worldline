#!/usr/bin/env python3
"""Release notes from the CHANGELOG section plus numbers read from the assurance report.

Nothing here is typed from memory: proof counts, test counts and identities come from
assurance.json for the exact release commit.

    scripts/release_notes.py --version 1.3.0 --changelog CHANGELOG.md --assurance assurance.json --release-manifest release-manifest.json
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def section(changelog: str, version: str) -> str:
    lines = changelog.splitlines()
    out: list[str] = []
    active = False
    for line in lines:
        if line.startswith("## "):
            if active:
                break
            active = line.startswith(f"## {version} ")
            if active:
                out.append(line)
            continue
        if active:
            out.append(line)
    return "\n".join(out).strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--changelog", required=True)
    parser.add_argument("--assurance", required=True)
    parser.add_argument("--release-manifest", required=True)
    args = parser.parse_args()
    assurance = json.loads(Path(args.assurance).read_text(encoding="utf-8"))
    manifest = json.loads(Path(args.release_manifest).read_text(encoding="utf-8"))
    proof = manifest["proof"]
    tests = assurance.get("pythonTests") or {}
    checkout = assurance.get("checkout") or {}
    host = assurance.get("host") or {}
    run_url = None
    if host.get("githubServer") and host.get("githubRepository") and host.get("githubRunId"):
        run_url = f"{host['githubServer']}/{host['githubRepository']}/actions/runs/{host['githubRunId']}"
    steps = ", ".join(f"{s['name']}={s['status']}" for s in manifest["assurance"]["steps"])
    body = section(Path(args.changelog).read_text(encoding="utf-8"), args.version) or f"## {args.version}"
    body += "\n\n### Assurance of this exact commit\n"
    body += f"- Release commit: `{manifest['commit']}` (tree `{manifest['tree']}`)\n"
    body += f"- Assurance run: {run_url or 'local'}; result {manifest['assurance']['result']}; steps: {steps}\n"
    body += f"- Python suite: {tests.get('ran')} tests, failures {tests.get('failures')}, errors {tests.get('errors')} ({tests.get('verdictLine')})\n"
    body += f"- Proof gate on this build: {proof['total']} checks (floor {proof['minimumChecks']}), unproved {proof['unproved']}, justified {proof['justified']}, pragma Assume {proof['pragmaAssume']}; library sha256 `{proof['librarySha256']}`\n"
    toolchain = assurance.get("toolchain") or {}
    body += "- Toolchain: " + "; ".join(f"{k}: {v}" for k, v in toolchain.items() if v) + "\n"
    body += "- Artifacts (source-only archive; the proved library is rebuilt by the installer):\n"
    for item in manifest["artifacts"]:
        body += f"  - `{item['name']}` sha256 `{item['sha256']}`\n"
    body += f"- Signing: {manifest['signing'].get('method')}\n"
    body += "- Publication does not authorize installation into any production instance.\n"
    print(body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
