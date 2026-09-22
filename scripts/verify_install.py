#!/usr/bin/env python3
"""Prove that the WORLDLINE installation now running is the one that was just built.

The released installer printed the version, the plugin short commit and the library hash, but
compared none of them: a runtime that failed to replace, a stale launcher, or a plugin left on
a different commit all printed a cheerful success line. This compares each installed artefact
with its source and with what the daemon actually answers, and writes a receipt.

    verify_install.py --engine-commit <sha> --plugin-commit <sha> --source <repo> --receipt <path>

Exit 0 only when every identity matches.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HOME = Path.home()
DEST = HOME / ".local/lib/worldline"
PLUGIN = HOME / ".config/omarchy/plugins/khephri.worldline"
SERVICE = HOME / ".config/systemd/user/worldlined.service"


def sha_file(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def tree_sha(root: Path) -> str | None:
    """sha256 over (relative path, bytes) of every .py file, bytecode excluded."""
    if not root.is_dir():
        return None
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*.py") if p.is_file()):
        if "__pycache__" in path.parts:
            continue
        digest.update(str(path.relative_to(root)).encode())
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--engine-commit", required=True)
    parser.add_argument("--plugin-commit", required=True)
    parser.add_argument("--source", required=True, help="the engine repository that was built")
    parser.add_argument("--receipt", help="write the install receipt here")
    args = parser.parse_args()
    source = Path(args.source)

    checks: list[dict] = []

    def compare(name: str, expected, actual, detail: str = "") -> None:
        checks.append({"check": name, "ok": expected is not None and expected == actual,
                       "expected": expected, "actual": actual, "detail": detail})

    # runtime tree, library, manifest, header
    compare("runtime-tree", tree_sha(source / "runtime/worldline"), tree_sha(DEST / "runtime/worldline"),
            "every runtime .py file, by path and content")
    compare("library", sha_file(source / "lib/libworldline_core.so"), sha_file(DEST / "libworldline_core.so"),
            "the proved kernel actually in place")
    compare("proof-manifest", sha_file(source / "proof-manifest.json"), sha_file(DEST / "proof-manifest.json"))
    compare("core-header", sha_file(source / "core/worldline_core.h"), sha_file(DEST / "worldline_core.h"))

    # launchers and unit
    compare("launcher-worldline", sha_file(source / "cli/worldline"), sha_file(HOME / ".local/bin/worldline"))
    compare("launcher-worldlined", sha_file(source / "daemon/worldlined"), sha_file(HOME / ".local/bin/worldlined"))
    compare("systemd-unit", sha_file(source / "daemon/worldlined.service"), sha_file(SERVICE))

    # the plugin is pinned, not "whatever main is"
    plugin_head = subprocess.run(["git", "-C", str(PLUGIN), "rev-parse", "HEAD"],
                                 stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True).stdout.strip() or None
    compare("plugin-commit", args.plugin_commit, plugin_head, "the deployed plugin checkout")
    plugin_dirty = subprocess.run(["git", "-C", str(PLUGIN), "status", "--porcelain"],
                                  env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
                                  stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True).stdout.strip()
    checks.append({"check": "plugin-clean", "ok": plugin_dirty == "", "expected": "", "actual": plugin_dirty[:300]})

    # what the RUNNING daemon answers, not what the files say
    proc = subprocess.run([str(HOME / ".local/bin/worldline"), "--json", "status"],
                          stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
    daemon_version = None
    daemon_ok = proc.returncode == 0
    if daemon_ok:
        try:
            daemon_version = (json.loads(proc.stdout).get("daemon") or {}).get("version")
        except json.JSONDecodeError:
            daemon_ok = False
    checks.append({"check": "daemon-answers", "ok": daemon_ok, "expected": "a parseable status document",
                   "actual": f"exit {proc.returncode}", "detail": proc.stderr.decode("utf-8", "replace")[-200:]})

    source_version = None
    text = (source / "runtime/worldline/__init__.py").read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("__version__"):
            source_version = line.split('"')[1]
            break
    compare("running-version", source_version, daemon_version, "the version the live daemon reports")

    ok = all(c["ok"] for c in checks)
    receipt = {
        "schemaVersion": 1,
        "installedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "verified": ok,
        "engineCommit": args.engine_commit,
        "pluginCommit": args.plugin_commit,
        "runtimeVersion": source_version,
        "source": str(source),
        "destination": str(DEST),
        "checks": checks,
        "nonClaims": [
            "This records that the installed files and the running daemon match what was built here.",
            "It does not re-prove the kernel; that is the proof gate run earlier in the same install.",
            "It says nothing about whether existing worlds remain promotable under the new engine.",
        ],
    }
    if args.receipt:
        Path(args.receipt).parent.mkdir(parents=True, exist_ok=True)
        Path(args.receipt).write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    for c in checks:
        if not c["ok"]:
            print(f"verify-install: MISMATCH {c['check']}: expected {c['expected']!r}, found {c['actual']!r}", file=sys.stderr)
    print(f"verify-install: {'every identity matches' if ok else 'IDENTITIES DO NOT MATCH'}"
          f" (engine {args.engine_commit[:12]}, plugin {args.plugin_commit[:12]}, version {source_version})")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
