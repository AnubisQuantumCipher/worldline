"""UNEXECUTED proposal: complete shared-parser candidate, immutable inputs.

No top-level payload. The companion parent also uses these identity routines
after an interrupted child, without importing any Ada/product implementation.
"""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import traceback

ROOT = Path("/home/sicarii/Work/worldline-phase1-blockers-20261013T165716Z")
EPOCH = "4ff3bf48b4323c051ffa8cf04ba4787982111f6d"
BUNDLE_SHA = "a23767c48c8c8c1b5677d53fac5ae79632407bd425a9329de06962016df62a98"
ROOT_FORMATION_SHA = "ff532976bc1422100e5d17193c572eb97af177deff62c38ad4f411d28801e788"
REFERENCE = ROOT / "scratch/old-analysis/sparklib-standalone-final-v5/result.json"
REFERENCE_SHA = "9e2db83e321d936a3eca04f82f185403ed39a3893e295ac3936bce774ca311af"
SOURCE_MANIFEST = ROOT / "scratch/old-analysis/evidence/private-sparklib-experiment-source-v1.json"
PRIVATE_ROOT = ROOT / "scratch/old-analysis/private-sparklib-experiment"
PRIVATE = PRIVATE_ROOT / "lib/gnat"
DESTINATION = ROOT / "records/phase1-blockers/resume-20261015-v1/shared-json-parser-v1"
OUTPUT_NAMES = {"obj-current-D56", "bin-current-D56", "results", "parent", "scope"}
EXTERNALS = ["-XWORLDLINE_PARSER_RESOURCE_BODY=current_D56", "-XSPARKLIB_MODE=full",
             "-XSPARKLIB_BUILD=Production", "-XSPARKLIB_LIBRARY_TYPE=static",
             "-XSPARKLIB_INSTALLED=True", "-XWORLDLINE_PRIVATE_SPARKLIB_PREBUILT=True"]
MAINS = ("string_parser_controls", "wide_parser_controls")


def stamp():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_json(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def event(path, value):
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(dict(utc=stamp(), **value), sort_keys=True) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def no_symlink(path, boundary=ROOT):
    if not path.is_relative_to(boundary):
        raise RuntimeError("Path escapes permitted boundary: " + str(path))
    current = path
    while True:
        if current.is_symlink():
            raise RuntimeError("Symlink in controlled path: " + str(current))
        if current == boundary:
            break
        current = current.parent


def files_under(directory):
    no_symlink(directory)
    if not directory.is_dir():
        raise RuntimeError("Missing expected directory: " + str(directory))
    paths = []
    for base, directories, files in os.walk(directory, followlinks=False):
        for name in [*directories, *files]:
            if (Path(base) / name).is_symlink():
                raise RuntimeError("Symlink in expected regular tree: " + str(Path(base) / name))
        paths.extend(Path(base) / name for name in files)
    return sorted(paths)


def candidate_identity(candidate):
    no_symlink(candidate)
    result = {}
    for base, directories, files in os.walk(candidate, followlinks=False):
        if Path(base) == candidate:
            directories[:] = [name for name in directories if name not in OUTPUT_NAMES]
        for name in [*directories, *files]:
            path = Path(base) / name
            if path.is_symlink():
                raise RuntimeError("Candidate input symlink: " + str(path))
        for name in files:
            path = Path(base) / name
            result[str(path.relative_to(candidate))] = digest(path)
    return result


def verify_bundle(candidate):
    receipt = candidate / "preparation-receipt.json"
    if digest(receipt) != BUNDLE_SHA:
        raise RuntimeError("Immutable controls receipt mismatch")
    if digest(candidate / "coordinator-formation.json") != ROOT_FORMATION_SHA:
        raise RuntimeError("Root immutable-copy formation identity mismatch")
    manifest = json.loads(receipt.read_text())
    if manifest["explicit_current_source_epoch"] != EPOCH:
        raise RuntimeError("Unexpected controls source epoch")
    for row in manifest["artifacts"]:
        path = candidate / row["path"]
        no_symlink(path, candidate)
        if digest(path) != row["sha256"]:
            raise RuntimeError("Immutable controls source changed: " + row["path"])
    known_ada = {row["path"] for row in manifest["artifacts"]
                 if Path(row["path"]).suffix in {".ads", ".adb", ".gpr"}}
    actual_ada = {path for path in candidate_identity(candidate)
                  if Path(path).suffix in {".ads", ".adb", ".gpr"}}
    if actual_ada != known_ada:
        raise RuntimeError("Unexpected Ada/project source inventory")
    return manifest


def private_identity(candidate):
    if digest(REFERENCE) != REFERENCE_SHA:
        raise RuntimeError("Original standalone-v5 receipt identity changed")
    verified = json.loads(REFERENCE.read_text())
    if digest(SOURCE_MANIFEST) != verified["source_manifest_sha256"]:
        raise RuntimeError("Original private source manifest identity changed")
    if verified["exit_code"] != 0 or verified["artifact_completeness"]["status"] != "TESTED complete GPR/ALI/source/archive correspondence":
        raise RuntimeError("Original complete private dependency validation absent")
    expected_sources = json.loads(SOURCE_MANIFEST.read_text())["source_hashes"]
    sources = {}
    for relative, expected in expected_sources.items():
        path = PRIVATE_ROOT / relative
        no_symlink(path, PRIVATE_ROOT)
        sources[relative] = digest(path)
        if sources[relative] != expected:
            raise RuntimeError("Private source/project mismatch: " + relative)
    # Refuse new source/project files as well as changed expected bytes.
    current_source_paths = {str(path.relative_to(PRIVATE_ROOT))
                            for path in files_under(PRIVATE_ROOT / "include")
                            if path.suffix in {".ads", ".adb"}}
    expected_source_paths = {name for name in expected_sources
                             if Path(name).suffix in {".ads", ".adb"}}
    if current_source_paths != expected_source_paths:
        raise RuntimeError("Private source/project inventory changed")
    private_output_files = [path for name in ("sparklib_obj", "sparklib_lib")
                            for path in files_under(PRIVATE / name)]
    artifacts = {str(path.relative_to(ROOT)): digest(path) for path in private_output_files
                 if path.suffix in {".o", ".ali", ".a", ".so"}}
    if artifacts != verified["dependency_artifacts"]:
        raise RuntimeError("Private object/ALI/archive inventory or bytes changed")
    # Standalone-v5 source manifest binds its modified library project; the
    # companion common project is independently pinned by the controls bundle.
    source_manifest_value = json.loads(SOURCE_MANIFEST.read_text())
    if digest(PRIVATE / "sparklib.gpr") != source_manifest_value["modified_project_sha256"]:
        raise RuntimeError("Original modified private library project changed")
    external = json.loads((candidate / "external-source-identities.json").read_text())
    projects = {}
    for row in external["project_files"]:
        path = Path(row["path"])
        no_symlink(path, PRIVATE)
        projects[str(path)] = digest(path)
        if projects[str(path)] != row["sha256"]:
            raise RuntimeError("Controls-pinned private project changed: " + str(path))
    incidental = {str(path.relative_to(ROOT)): digest(path) for path in private_output_files
                  if path.suffix not in {".o", ".ali", ".a", ".so"}}
    return {"reference_sha256": digest(REFERENCE), "source_manifest_sha256": digest(SOURCE_MANIFEST),
            "sources": sources, "projects": projects, "artifacts": artifacts,
            "incidental_output_files_observed_not_standalone_pins": incidental,
            "matches_standalone_v5": True}


def cgroup_identity():
    line = next(line for line in Path("/proc/self/cgroup").read_text().splitlines() if line.startswith("0::"))
    group = Path("/sys/fs/cgroup") / line[3:].lstrip("/")
    return {"path": str(group), **{name: (group / name).read_text().strip()
                                  for name in ("memory.max", "memory.swap.max", "memory.events", "cgroup.events")}}


def sandbox(candidate, carrier_tmp, carrier_cache, payload):
    argv = ["bwrap", "--die-with-parent", "--unshare-pid", "--ro-bind", "/", "/",
            "--dev", "/dev", "--proc", "/proc"]
    for path in (candidate / "obj-current-D56", candidate / "bin-current-D56", candidate / "results",
                 carrier_tmp, carrier_cache):
        argv += ["--bind", str(path), str(path)]
    argv += ["--bind", str(carrier_tmp), "/tmp", "--chdir", str(candidate), *payload]
    return argv


def main():
    candidate = Path(__file__).resolve().parent
    if candidate != DESTINATION:
        raise SystemExit("Execute only the exact reviewed fresh records candidate copy")
    no_symlink(candidate)
    out = candidate / "results"
    obj = candidate / "obj-current-D56"
    binary = candidate / "bin-current-D56"
    for path in (out, obj, binary):
        no_symlink(path)
        if path.exists():
            raise SystemExit("Refuse stale output: " + str(path))
    out.mkdir()
    receipt = {"started_utc": stamp(), "status": "UNVERIFIED", "source_epoch": EPOCH,
               "cwd": str(candidate), "steps": [], "errors": [],
               "scope": "Complete shared-parser candidate project only; no full WORLDLINE, integration or acceptance claim"}
    write_json(out / "started.json", receipt)
    okay = False
    try:
        observed = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        receipt["observed_head"] = observed
        if observed != EPOCH:
            raise RuntimeError("Current source epoch changed; explicit new review required")
        verify_bundle(candidate)
        receipt["source_before"] = candidate_identity(candidate)
        receipt["private_before"] = private_identity(candidate)
        receipt["cgroup_before"] = cgroup_identity()
        if receipt["cgroup_before"]["memory.max"] != "8589934592" or receipt["cgroup_before"]["memory.swap.max"] != "0":
            raise RuntimeError("Actual own cgroup cap differs from unchanged 8G/swap0")
        carrier_tmp = Path(os.environ["TMPDIR"])
        carrier_cache = Path(os.environ["XDG_CACHE_HOME"])
        if carrier_tmp != candidate / "scope/tmp" or carrier_cache != candidate / "scope/cache":
            raise RuntimeError("Unexpected carrier temporary/cache directories")
        for path in (carrier_tmp, carrier_cache):
            no_symlink(path)
            if not path.is_dir():
                raise RuntimeError("Missing owned carrier directory")
        obj.mkdir()
        binary.mkdir()
        env = dict(os.environ)
        env.update(GPR_PROJECT_PATH=str(PRIVATE), WORLDLINE_BUILD="checks",
                   WORLDLINE_PARSER_RESOURCE_BODY="current_D56", PYTHONDONTWRITEBYTECODE="1")
        for name in ("GPR_TOOL", "PYTHONOPTIMIZE", "ADA_INCLUDE_PATH", "ADA_OBJECTS_PATH",
                     "GPR_CONFIG", "GPR_CONFIG_PATH", "LD_PRELOAD"):
            env.pop(name, None)
        receipt["environment"] = {name: env.get(name) for name in
                                  ("PATH", "LANG", "LC_ALL", "GPR_PROJECT_PATH", "GPR_TOOL", "WORLDLINE_BUILD",
                                   "WORLDLINE_PARSER_RESOURCE_BODY", "TMPDIR", "XDG_CACHE_HOME", "PYTHONOPTIMIZE",
                                   "ADA_INCLUDE_PATH", "ADA_OBJECTS_PATH", "GPR_CONFIG", "GPR_CONFIG_PATH",
                                   "LD_LIBRARY_PATH", "LD_PRELOAD", "PYTHONDONTWRITEBYTECODE")}
        receipt["writable_mounts"] = [str(path) for path in (obj, binary, out, carrier_tmp, carrier_cache)]
        receipt["tools"] = {}

        def run(name, command):
            argv = sandbox(candidate, carrier_tmp, carrier_cache, command)
            row = {"name": name, "argv": argv, "payload_argv": command, "started_utc": stamp()}
            receipt["steps"].append(row)
            event(out / "events.jsonl", {"event": "phase_started", **row})
            with (out / (name + ".stdout")).open("xb") as stdout, (out / (name + ".stderr")).open("xb") as stderr:
                result = subprocess.run(argv, cwd=candidate, env=env, stdout=stdout, stderr=stderr)
            row.update(ended_utc=stamp(), exit_code=result.returncode,
                       stdout_sha256=digest(out / (name + ".stdout")), stderr_sha256=digest(out / (name + ".stderr")))
            event(out / "events.jsonl", {"event": "phase_finished", **row})
            write_json(out / (name + ".result.json"), row)
            return result.returncode

        for name in ("gnatls", "gprbuild", "gnatprove", "gcc", "bwrap"):
            found = shutil.which(name, path=env["PATH"])
            if found is None:
                raise RuntimeError("Required tool missing: " + name)
            path = Path(found).resolve()
            receipt["tools"][name] = {"path": str(path), "sha256": digest(path)}
            if run("version-" + name, [str(path), "--version"]) != 0:
                raise RuntimeError("Tool version query failed: " + name)
        write_json(out / "launch.json", receipt)
        build = run("build", [receipt["tools"]["gprbuild"]["path"], "-p", "-P", "shared_json_parser_controls.gpr", "-j2", *EXTERNALS])
        receipt["build_exit"] = build
        # Preserve complete configured proof diagnostics even when build failed.
        proof = run("proof", [receipt["tools"]["gnatprove"]["path"], "-P", "shared_json_parser_controls.gpr",
                              "-U", "--mode=all", "--level=3", "--report=all", "--checks-as-errors=on",
                              "--proof-warnings=on", "--memlimit=1024", "--timeout=60", "-j2", *EXTERNALS])
        receipt["proof_exit"] = proof
        receipt["runtime_exits"] = {}
        for name in MAINS:
            if build == 0:
                receipt["runtime_exits"][name] = run(name, [str(binary / name)])
            else:
                receipt["runtime_exits"][name] = None
                event(out / "events.jsonl", {"event": "runtime_not_performed", "name": name, "reason": "build did not succeed"})
        receipt["assertion_alis"] = {}
        for name in MAINS:
            path = obj / (name + ".ali")
            receipt["assertion_alis"][name] = ({"path": str(path), "sha256": digest(path),
                                                "gnata": "A -gnata" in path.read_text().splitlines()}
                                               if path.is_file() and not path.is_symlink() else None)
        report = obj / "gnatprove/gnatprove.out"
        receipt["complete_report"] = ({"path": str(report), "sha256": digest(report)}
                                       if report.is_file() and not report.is_symlink() else None)
        proof_dir = obj / "gnatprove"
        receipt["proof_output_inventory"] = ({str(path.relative_to(obj)): digest(path) for path in files_under(proof_dir)}
                                               if proof_dir.is_dir() else None)
        okay = (build == proof == 0 and all(value == 0 for value in receipt["runtime_exits"].values())
                and all(value is not None and value["gnata"] for value in receipt["assertion_alis"].values())
                and receipt["complete_report"] is not None)
    except BaseException as error:
        receipt["errors"].append({"type": type(error).__name__, "message": str(error), "traceback": traceback.format_exc()})
        okay = False
    finally:
        for label, function in (("source_after", lambda: candidate_identity(candidate)),
                                ("private_after", lambda: private_identity(candidate)), ("cgroup_after", cgroup_identity)):
            try:
                receipt[label] = function()
            except BaseException as error:
                receipt[label] = None
                receipt["errors"].append({"phase": label, "type": type(error).__name__, "message": str(error)})
                okay = False
        receipt["sources_unchanged"] = receipt.get("source_before") is not None and receipt.get("source_before") == receipt["source_after"]
        receipt["private_unchanged"] = receipt.get("private_before") is not None and receipt.get("private_before") == receipt["private_after"]
        okay = okay and receipt["sources_unchanged"] and receipt["private_unchanged"] and not receipt["errors"]
        receipt.update(ended_utc=stamp(), mechanically_complete=okay,
                       status="RECORDED; complete raw proof review still required" if okay else "FAILED-OPEN candidate execution")
        write_json(out / "result.json", receipt)
    print(json.dumps({"result": str(out / "result.json"), "mechanically_complete": okay}))
    return 0 if okay else 1


if __name__ == "__main__":
    raise SystemExit(main())
