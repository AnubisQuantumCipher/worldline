"""Execute the complete isolated cursor candidate closure, preserving failures."""
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

CANDIDATE = Path(__file__).resolve().parent
ROOT = CANDIDATE.parents[3]
OUT = CANDIDATE / "results"
OUT.mkdir(exist_ok=False)
if (CANDIDATE / "obj").exists() or (CANDIDATE / "bin").exists():
    raise SystemExit("Refuse nonfresh compiler outputs")
PRIVATE = ROOT / "scratch/old-analysis/private-sparklib-experiment/lib/gnat"

def stamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

def sources():
    return {str(p.relative_to(CANDIDATE)): digest(p)
            for directory in (CANDIDATE, CANDIDATE / "dependencies")
            for p in directory.iterdir() if p.is_file()}

watched = [p for name in ("sparklib_obj", "sparklib_lib")
           for p in (PRIVATE / name).rglob("*") if p.is_file()]
if not watched:
    raise SystemExit("Private prebuilt dependency identity missing")

def dependency_identity():
    return {str(p.relative_to(ROOT)): digest(p) for p in watched}

env = dict(os.environ)
env["GPR_PROJECT_PATH"] = str(PRIVATE) + ":" + env.get("GPR_PROJECT_PATH", "")
env.pop("GPR_TOOL", None)
env["PYTHONDONTWRITEBYTECODE"] = "1"
receipt = {
    "started_utc": stamp(), "cwd": str(CANDIDATE),
    "base_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "source_before": sources(), "dependency_before": dependency_identity(),
    "environment": {key: env.get(key) for key in ("PATH", "LANG", "LC_ALL", "GPR_PROJECT_PATH", "GPR_TOOL", "TMPDIR", "XDG_CACHE_HOME")},
    "scope": "Complete cursor candidate only; no production integration, JSON grammar, full WORLDLINE or acquisition acceptance",
    "steps": [],
}

def retain():
    (OUT / "result.json").write_text(json.dumps(receipt, indent=2) + "\n")

for name in ("gnatls", "gprbuild", "gnatprove"):
    path = Path(shutil.which(name)).resolve()
    version = subprocess.run([str(path), "--version"], capture_output=True, text=True, env=env)
    receipt[name] = {"path": str(path), "sha256": digest(path), "exit_code": version.returncode, "stdout": version.stdout, "stderr": version.stderr}
    if version.returncode:
        retain()
        raise SystemExit("Tool version query failed")

def run(name, command):
    argv = ["bwrap", "--die-with-parent", "--ro-bind", "/", "/", "--dev", "/dev", "--proc", "/proc",
            "--bind", str(ROOT), str(ROOT), "--bind", env["TMPDIR"], "/tmp", "--chdir", str(CANDIDATE), *command]
    item = {"name": name, "argv": argv, "payload_argv": command, "started_utc": stamp()}
    receipt["steps"].append(item)
    retain()
    with (OUT / (name + ".stdout")).open("xb") as stdout, (OUT / (name + ".stderr")).open("xb") as stderr:
        result = subprocess.run(argv, cwd=CANDIDATE, env=env, stdout=stdout, stderr=stderr)
    item.update(ended_utc=stamp(), exit_code=result.returncode,
                stdout_sha256=digest(OUT / (name + ".stdout")), stderr_sha256=digest(OUT / (name + ".stderr")))
    retain()
    return result.returncode

externals = ["-XSPARKLIB_MODE=full", "-XSPARKLIB_BUILD=Production", "-XSPARKLIB_LIBRARY_TYPE=static", "-XSPARKLIB_INSTALLED=True", "-XWORLDLINE_PRIVATE_SPARKLIB_PREBUILT=True"]
build = run("build", ["gprbuild", "-p", "-P", "decoder_cursor_candidate.gpr", "-j2", *externals])
proof = run("proof", ["gnatprove", "-P", "decoder_cursor_candidate.gpr", "-U", "--mode=all", "--level=3", "--report=all", "--checks-as-errors=on", "--proof-warnings=on", "--memlimit=1024", "--timeout=60", "-j2", *externals])
runtime = run("runtime", [str(CANDIDATE / "bin/decoder_cursor_controls")]) if build == 0 else None
receipt.update(ended_utc=stamp(), build_exit=build, proof_exit=proof, runtime_exit=runtime,
               source_after=sources(), dependency_after=dependency_identity())
receipt["sources_unchanged"] = receipt["source_before"] == receipt["source_after"]
receipt["dependency_unchanged"] = receipt["dependency_before"] == receipt["dependency_after"]
ali = CANDIDATE / "obj/decoder_cursor_controls.ali"
receipt["assertions_enabled_ali"] = "A -gnata" in ali.read_text().splitlines() if ali.is_file() else None
report = CANDIDATE / "obj/gnatprove/gnatprove.out"
receipt["complete_report"] = {"path": str(report), "sha256": digest(report)} if report.is_file() else None
retain()
print(json.dumps({"result": str(OUT / "result.json"), "build_exit": build, "proof_exit": proof, "runtime_exit": runtime,
                  "sources_unchanged": receipt["sources_unchanged"], "dependency_unchanged": receipt["dependency_unchanged"], "assertions_enabled_ali": receipt["assertions_enabled_ali"]}))
ok = build == proof == runtime == 0 and receipt["sources_unchanged"] and receipt["dependency_unchanged"] and receipt["assertions_enabled_ali"] is True and receipt["complete_report"] is not None
raise SystemExit(0 if ok else 1)
