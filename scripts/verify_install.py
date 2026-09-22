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
    parser.add_argument("--previous-pid", help="the daemon MainPID before the restart, so a daemon that never restarted is caught")
    parser.add_argument("--main-pid", help="the daemon MainPID the user manager reports now")
    parser.add_argument("--proof-gate", choices=("ran", "skipped"), default="ran",
                        help="whether this install re-proved the kernel or only verified the manifest")
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

    # What the RUNNING process actually loaded. Hashing the file on disk proves nothing about
    # the library in memory: WORLDLINE_CORE_LIB, a unit drop-in or a stale process can all point
    # it somewhere else.
    def loaded_library(pid: str | None) -> str | None:
        if not pid or not pid.isdigit():
            return None
        try:
            maps = Path(f"/proc/{pid}/maps").read_text(encoding="utf-8", errors="replace")
        except OSError:
            return None
        for line in maps.splitlines():
            if "libworldline_core.so" in line:
                return line.split()[-1]
        return None

    # the plugin is pinned, not "whatever main is"
    plugin_head = subprocess.run(["git", "-C", str(PLUGIN), "rev-parse", "HEAD"],
                                 stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True).stdout.strip() or None
    compare("plugin-commit", args.plugin_commit, plugin_head, "the deployed plugin checkout")
    # An unreadable or non-git plugin must not score as "clean"; and untracked files are not a
    # modification of the pinned commit, so only tracked changes fail.
    tracked = subprocess.run(["git", "-C", str(PLUGIN), "status", "--porcelain", "--untracked-files=no"],
                             env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if tracked.returncode != 0:
        checks.append({"check": "plugin-clean", "ok": False, "expected": "a readable git checkout",
                       "actual": f"git exited {tracked.returncode}", "detail": tracked.stderr.strip()[-160:]})
    else:
        dirty = tracked.stdout.strip()
        checks.append({"check": "plugin-clean", "ok": dirty == "", "expected": "no tracked modifications",
                       "actual": dirty[:300]})

    # what the RUNNING daemon answers, not what the files say
    daemon_version = None
    daemon_pid = None
    daemon_ok = False
    detail = ""
    try:
        proc = subprocess.run([str(HOME / ".local/bin/worldline"), "--json", "status"],
                              stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
        detail = proc.stderr.decode("utf-8", "replace")[-200:]
        if proc.returncode == 0:
            document = json.loads(proc.stdout)
            daemon = document.get("daemon") or {}
            daemon_version, daemon_pid = daemon.get("version"), daemon.get("pid")
            daemon_ok = True
        actual = f"exit {proc.returncode}"
    except Exception as exc:  # recorded as a failed check; the receipt is still written
        actual, detail = f"{type(exc).__name__}", str(exc)[:200]
    checks.append({"check": "daemon-answers", "ok": daemon_ok, "expected": "a parseable status document",
                   "actual": actual, "detail": detail})

    source_version = None
    try:
        text = (source / "runtime/worldline/__init__.py").read_text(encoding="utf-8")
        for line in text.splitlines():
            if line.startswith("__version__"):
                source_version = line.split('"')[1]
                break
    except OSError as exc:
        checks.append({"check": "source-version-readable", "ok": False, "expected": "a __version__ line",
                       "actual": str(exc)[:160]})
    compare("running-version", source_version, daemon_version, "the version the live daemon reports")

    # a daemon that never restarted would still answer, with the OLD runtime in memory
    if args.previous_pid or args.main_pid:
        reported = str(daemon_pid) if daemon_pid is not None else None
        checks.append({"check": "daemon-is-a-new-process",
                       "ok": bool(reported) and reported != str(args.previous_pid or ""),
                       "expected": f"a pid other than the pre-stop {args.previous_pid}", "actual": reported,
                       "detail": "a daemon that never restarted keeps the previous runtime in memory"})
        if args.main_pid:
            checks.append({"check": "daemon-is-the-units-process", "ok": reported == str(args.main_pid),
                           "expected": f"MainPID {args.main_pid}", "actual": reported,
                           "detail": "the process that answered is the one the user manager supervises"})
    mapped = loaded_library(str(daemon_pid) if daemon_pid is not None else args.main_pid)
    checks.append({"check": "loaded-library", "ok": mapped == str(DEST / "libworldline_core.so"),
                   "expected": str(DEST / "libworldline_core.so"), "actual": mapped,
                   "detail": "the kernel library the running daemon actually mapped, from /proc/<pid>/maps"})

    ok = all(c["ok"] for c in checks)
    receipt = {
        "schemaVersion": 1,
        "installedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "verified": ok,
        "engineCommit": args.engine_commit,
        "pluginCommit": args.plugin_commit,
        "runtimeVersion": source_version,
        "proofGate": args.proof_gate,
        "source": str(source),
        "destination": str(DEST),
        "checks": checks,
        "nonClaims": [
            "This records that the installed files and the running daemon match what was built here.",
            "It does not re-prove the kernel; proofGate records whether that gate ran in this install"
            " or was skipped with WORLDLINE_SKIP_PROOF=1, in which case only the manifest was verified.",
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
