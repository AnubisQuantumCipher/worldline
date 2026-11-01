"""Fixed DEBUG/static build and twice-generation recipe. FUTURE UNADMITTED."""
from pathlib import Path
import os
import re
import resource
import subprocess
import sys
import time
from xgen_common import (HERE, ROOT, WORK, LIVE_ROOT, JOB, G, P, FILE,
                         bounded_read, digest, inventory, isolated, load_json,
                         relative, verify_pins, write_json)
from xgen_recovery import recover


def child_limits():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_FSIZE, (FILE, FILE))


def environment():
    return {"PATH": str(G / "bin") + ":" + str(P / "bin") + ":/usr/bin",
            "HOME": str(LIVE_ROOT / "home"), "TMPDIR": str(LIVE_ROOT / "tmp"),
            "XDG_CACHE_HOME": str(LIVE_ROOT / "cache"), "LC_ALL": "C",
            "TZ": "UTC", "PYTHONOPTIMIZE": "0", "PYTHONDONTWRITEBYTECODE": "1",
            "GPR_PROJECT_PATH": ":".join(str(LIVE_ROOT / "source/gnatcoll" / x)
                                         for x in ("core", "minimal"))}


def stage_inputs(rows):
    if len(rows) != 342 or sum(x["family"] == "gnatcoll" for x in rows) != 278:
        raise RuntimeError("exact 278+64 input count required")
    for row in rows:
        target = LIVE_ROOT / relative(row["destination"])
        target.parent.mkdir(parents=True, exist_ok=True)
        raw = bounded_read(Path(row["path"]), FILE)
        if digest(Path(row["path"])) != row["identity"]:
            raise RuntimeError("input changed before copy")
        with target.open("xb") as stream:
            if stream.write(raw) != len(raw):
                raise RuntimeError("short source copy")
        if digest(target) != row["identity"]:
            raise RuntimeError("copy identity mismatch")


def static_templates(xtree, templates, roster):
    text = bounded_read(xtree, FILE).decode("ascii")
    calls = re.findall(r'Process\s*\("([a-z_.-]+)"\);', text)
    added = re.findall(r'Add\s*\("([A-Za-z_]+)"\s*,', text)
    if calls != roster or len(calls) != 21 or len(set(calls)) != 21:
        raise RuntimeError("output roster mismatch")
    if len(added) != 35 or len(set(added)) != 35:
        raise RuntimeError("callback count/duplicate")
    found = []
    for name in roster:
        raw = bounded_read(templates / (name + "-tmpl"), FILE)
        found.extend(re.findall(rb'_@([A-Za-z_]+)@_', raw))
    if len(found) != 35 or set(found) != {x.encode("ascii") for x in added}:
        raise RuntimeError("template/callback join mismatch")


def stage_command(name, argv, cwd, seconds, deadline, receipts):
    remaining = min(seconds, deadline - time.monotonic())
    if remaining <= 0:
        raise TimeoutError("global worker deadline")
    out, err = LIVE_ROOT / "logs" / (name + ".stdout"), LIVE_ROOT / "logs" / (name + ".stderr")
    command = isolated(argv, cwd)
    item = {"stage": name, "argv": command, "limit_seconds": seconds, "exit": None}
    receipts.append(item)
    with out.open("xb") as stdout, err.open("xb") as stderr:
        try:
            result = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=stdout,
                                    stderr=stderr, env=environment(), timeout=remaining,
                                    check=False, preexec_fn=child_limits)
        except subprocess.TimeoutExpired:
            item["failure"] = "TIMEOUT; partial full logs retained"
            raise
    item["exit"] = result.returncode
    item["stdout"], item["stderr"] = digest(out), digest(err)
    if result.returncode != 0:
        raise RuntimeError("stage failed: " + name)
    # An exact-limit stream is conservatively ambiguous: fail, never truncate.
    if any(item[x]["bytes"] >= FILE for x in ("stdout", "stderr")):
        raise RuntimeError("capture limit reached; possible evidence loss")
    inventory(LIVE_ROOT)
    return out, err


def scenarios(external):
    values = {"GNATCOLL_BUILD_MODE": "DEBUG", "LIBRARY_TYPE": "static",
              "GNATCOLL_VERSION": "25.0", "GNATCOLL_OS": "unix",
              "GNATCOLL_MMAP": "yes", "GNATCOLL_MADVISE": "yes",
              "GNATCOLL_XXHASH_ARCH": "generic", "GNATCOLL_BLAKE3_ARCH": "aarch64-linux",
              "GNATCOLL_OBJECT_ROOT": str(LIVE_ROOT / "gnatcoll") + "/",
              "EXTERNALLY_BUILT": external}
    return ["-X" + key + "=" + value for key, value in values.items()]


def build_commands():
    base = [str(P / "bin/gprbuild"), "-p", "-j2"]
    gnatcoll = LIVE_ROOT / "source/gnatcoll"
    warnings = ["-cargs:Ada", "-gnatwa", "-gnatwe", "-gnatVa",
                "-cargs:C", "-Wall", "-Wextra", "-Werror"]
    minimal = base + ["-P", str(gnatcoll / "minimal/gnatcoll_minimal.gpr")]
    core = base + ["-P", str(gnatcoll / "core/gnatcoll_core.gpr")]
    xgen = LIVE_ROOT / "source/spark/src/why/xgen"
    helper = base + ["-P", str(xgen / "helpers.gpr"), "xtree"]
    return [("minimal", minimal + scenarios("false") + warnings, 300),
            ("core", core + scenarios("false") + warnings, 600),
            ("helpers", helper + scenarios("true") +
             ["-cargs:Ada", "-gnata", "-gnatVa", "-gnatwa", "-gnatwe"], 300)]


def verify_outputs(directory, roster):
    rows, _ = inventory(directory)
    expected = set(roster) | {x + "-tmpl" for x in roster}
    if set(rows) != expected:
        raise RuntimeError("generation inventory mismatch")
    result = {}
    for name in roster:
        raw = bounded_read(directory / name, FILE)
        if not raw or b"_@" in raw or b"@_" in raw:
            raise RuntimeError("empty output or unresolved template delimiter")
        result[name] = digest(directory / name)
    return result


def generations(xgen, roster, deadline, receipts):
    executable = xgen / "xtree"
    executable_id, outputs = digest(executable), []
    for label in ("generation-a", "generation-b"):
        directory = LIVE_ROOT / label
        directory.mkdir()
        for name in roster:
            raw = bounded_read(xgen / (name + "-tmpl"), FILE)
            with (directory / (name + "-tmpl")).open("xb") as stream:
                if stream.write(raw) != len(raw):
                    raise RuntimeError("short template copy")
        out, err = stage_command(label, [str(executable)], directory, 30, deadline, receipts)
        # This producer has no expected normal diagnostics. Capture then reject any.
        if bounded_read(out, FILE) or bounded_read(err, FILE):
            raise RuntimeError("generator diagnostics; warnings cannot qualify")
        if digest(executable) != executable_id:
            raise RuntimeError("executable changed between generations")
        outputs.append(verify_outputs(directory, roster))
    if outputs[0] != outputs[1]:
        raise RuntimeError("nondeterministic generation")
    return {"executable": executable_id, "outputs": outputs[0]}


def prepare():
    if sys.flags.optimize != 0 or os.environ.get("PYTHONOPTIMIZE") != "0":
        raise RuntimeError("assertions/configuration mismatch")
    if Path(sys.executable).resolve() != Path("/usr/bin/python3").resolve():
        raise RuntimeError("unregistered Python interpreter")
    if WORK.is_symlink() or not WORK.is_dir() or LIVE_ROOT.exists():
        raise RuntimeError("guard-created fresh work root required")
    LIVE_ROOT.mkdir()
    for name in ("logs", "tmp", "cache", "home"):
        (LIVE_ROOT / name).mkdir()
    pins = load_json(HERE / "tool-runtime-pins.json")
    inputs = load_json(HERE / "input-pins.json")
    verify_pins(pins)
    verify_pins(inputs)
    stage_inputs(inputs)
    return inputs, load_json(HERE / "template-roster.json")


def run():
    receipts, code, result = [], 125, {"execution": "FAILED", "qualification": "UNPROVEN"}
    result.update(source_validation="UNRUN", build="UNRUN", generation="UNRUN",
                  determinism="UNRUN", recovery="UNRUN", terminal="UNKNOWN")
    deadline = time.monotonic() + 1500
    try:
        result["source_validation"] = "RUNNING"
        inputs, roster = prepare()
        xgen = LIVE_ROOT / "source/spark/src/why/xgen"
        static_templates(xgen / "xtree.adb", xgen, roster)
        result["source_validation"] = "OBSERVED"
        out, _ = stage_command("target", [str(G / "bin/gcc"), "-dumpmachine"], LIVE_ROOT, 5, deadline, receipts)
        if bounded_read(out, 8192).strip() != b"aarch64-linux-gnu":
            raise RuntimeError("unsupported compiler target")
        out, _ = stage_command("version", [str(G / "bin/gcc"), "-dumpfullversion"], LIVE_ROOT, 5, deadline, receipts)
        if bounded_read(out, 8192).strip() != b"16.1.0":
            raise RuntimeError("unsupported compiler version")
        result["build"] = "RUNNING"
        for name, argv, seconds in build_commands():
            stage_command(name, argv, LIVE_ROOT, seconds, deadline, receipts)
        result["build"] = "OBSERVED"
        result["generation"], result["determinism"] = "RUNNING", "RUNNING"
        result["generation_evidence"] = generations(xgen, roster, deadline, receipts)
        result["generation"], result["determinism"] = "OBSERVED", "OBSERVED"
        for row in inputs:
            if digest(LIVE_ROOT / row["destination"]) != row["identity"]:
                raise RuntimeError("staged original source changed")
        verify_pins(load_json(HERE / "tool-runtime-pins.json"))
        inventory(LIVE_ROOT)
        result["recovery"] = "RUNNING"
        result["recovery_evidence"] = recover(deadline)
        result["recovery"] = "OBSERVED"
        code, result["execution"] = 0, "OBSERVED_TERMINAL_PENDING"
    except (OSError, ValueError, TypeError, KeyError, RuntimeError, subprocess.SubprocessError) as error:
        for key in ("source_validation", "build", "generation", "determinism", "recovery"):
            if result[key] == "RUNNING":
                result[key] = "FAILED"
        result["failure"] = type(error).__name__ + ": " + str(error)[:1024]
    finally:
        result.update(stages=receipts, exit=code, acceptance_credit=False)
        write_json(JOB / "xgen-worker-result.json", result)
    return code


if __name__ == "__main__":
    raise SystemExit(run())
