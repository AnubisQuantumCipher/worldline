#!/usr/bin/env python3
"""Bind this workflow's validated immutable pair to its final release manifest.

The read-only pair job validates source archives and code inventories. This small check
runs before publication and consumes that same run's report; it never executes plugin code.
It does not authenticate an arbitrary report supplied outside that workflow.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


def problems(report: object, manifest: object, engine_commit: str, engine_tree: str) -> list[str]:
    failures: list[str] = []
    for label, value in (("expected engine commit", engine_commit), ("expected engine tree", engine_tree)):
        if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{40}", value) is None:
            failures.append(f"{label} is not an immutable identity")
    if not isinstance(report, dict) or report.get("schema") != "worldline-release-pair-validation-v1":
        return failures + ["pair report schema is unsupported"]
    if not isinstance(manifest, dict) or type(manifest.get("schemaVersion")) is not int or manifest.get("schemaVersion") != 1:
        return failures + ["release manifest schema is unsupported"]
    if report.get("accepted") is not True or manifest.get("accepted") is not True:
        failures.append("pair report and release manifest must both accept")
    for key, expected in (("engineCommit", engine_commit), ("engineTree", engine_tree)):
        if report.get(key) != expected:
            failures.append(f"pair report {key} differs from this workflow")
    if manifest.get("commit") != engine_commit or manifest.get("tree") != engine_tree:
        failures.append("release manifest engine identity differs from this workflow")
    compatibility = manifest.get("pluginCompatibility")
    if not isinstance(compatibility, dict) or compatibility.get("schema") != "worldline-plugin-compatibility-v1":
        return failures + ["release manifest has no supported plugin compatibility record"]
    encoded = json.dumps(compatibility, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    if report.get("pluginCompatibilitySha256") != hashlib.sha256(encoded).hexdigest():
        failures.append("complete plugin compatibility record differs from the validated pair")
    plugin = compatibility.get("plugin")
    if not isinstance(plugin, dict):
        return failures + ["release manifest has no plugin identity"]
    for key, expected, width in (
        ("pluginCommit", plugin.get("commit"), 40),
        ("pluginArchiveSha256", plugin.get("archiveSha256"), 64),
        ("codeSetSha256", compatibility.get("codeSetSha256"), 64),
    ):
        value = report.get(key)
        if not isinstance(value, str) or re.fullmatch(rf"[0-9a-f]{{{width}}}", value) is None or value != expected:
            failures.append(f"release manifest {key} differs from the validated pair")
    version = manifest.get("version")
    if not isinstance(version, str) or re.fullmatch(r"\d+\.\d+\.\d+", version) is None:
        failures.append("release manifest engine version is missing or malformed")
    if compatibility.get("engine") != version:
        failures.append("release manifest pairing version differs from engine version")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--engine-commit", required=True)
    parser.add_argument("--engine-tree", required=True)
    args = parser.parse_args()
    try:
        failures = problems(json.loads(args.report.read_text()), json.loads(args.manifest.read_text()),
                            args.engine_commit, args.engine_tree)
    except (OSError, ValueError) as exc:
        failures = [f"pair evidence is unavailable: {exc}"]
    print(json.dumps({"accepted": not failures, "reasons": failures}, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
