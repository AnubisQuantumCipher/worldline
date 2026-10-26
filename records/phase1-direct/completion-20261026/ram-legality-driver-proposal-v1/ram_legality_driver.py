"""SOURCE-ONLY proposal. One target semantic check, never proof/acceptance."""
from pathlib import Path
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tarfile

import ram_qualification_v2 as retained

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CONFIG = HERE / "proposal.json"


def config(expected):
    if retained.digest(CONFIG) != expected:
        raise RuntimeError("reviewed configuration identity mismatch")
    value = json.loads(CONFIG.read_text())
    helper = Path(retained.__file__).resolve()
    if helper != HERE.parent / "ram_qualification_v2.py":
        raise RuntimeError("unexpected retained helper module")
    if retained.digest(helper) != value["helper_sha256"]:
        raise RuntimeError("retained v2 helper changed")
    if (retained.RAM_LIMIT, retained.ARCHIVE_LIMIT, retained.RECEIPT_BUDGET) != (
            32 * 1024**2, 8 * 1024**2, 4 * 1024**2):
        raise RuntimeError("unexpected helper resource ceilings")
    return value


def receipt(base, name, value):
    # All durable receipts are direct children. RAM/restore trees are excluded.
    if not re.fullmatch(r"[a-z-]+\.json", name):
        raise RuntimeError("unexpected receipt name")
    data = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    entries = list(base.iterdir())
    if len(entries) > 20:
        raise RuntimeError("receipt entry ceiling")
    used = sum(p.stat().st_size for p in entries
               if p.is_file() and p.name != "complete-output.tar.gz")
    if len(data) + used > retained.RECEIPT_BUDGET:
        raise RuntimeError("aggregate 4MiB receipt ceiling")
    retained.save(base / name, value)


def source_state(value, target, expected_sources=None):
    private = ROOT / value["private_manifest"]["path"]
    pins = dict(expected_sources or value["sources"])
    if expected_sources is None:
        if retained.digest(private) != value["private_manifest"]["sha256"]:
            raise RuntimeError("private dependency manifest changed")
        rows = json.loads(private.read_text())
        if len(rows) != 134:
            raise RuntimeError("private dependency count changed")
        pins.update({row["path"]: row["sha256"] for row in rows})
        pins[value["private_manifest"]["path"]] = retained.digest(private)
    if len(pins) > 256:
        raise RuntimeError("source count ceiling")
    actual = {name: (retained.digest(ROOT / name) if (ROOT / name).is_file()
                     else "MISSING_OR_NONREGULAR") for name in pins}
    mount = HERE / target["object_mountpoint"]
    valid_mount = (mount.is_dir() and not mount.is_symlink() and
                   mount.resolve().is_relative_to(HERE) and not list(mount.iterdir()))
    if expected_sources is None and (actual != pins or not valid_mount):
        raise RuntimeError("source mismatch or root-prepared empty object mountpoint absent")
    return {"sources": actual, "configuration": retained.digest(CONFIG),
            "object_mountpoint": str(mount), "host_object_mountpoint_empty": valid_mount,
            "read_only_imported_outputs": value["read_only_imported_outputs"]}


def command(target):
    return ["env", "TMP=" + os.environ["TMPDIR"],
            "TEMP=" + os.environ["TMPDIR"], "TEMPDIR=" + os.environ["TMPDIR"],
            "GNAT_TMPDIR=" + os.environ["TMPDIR"],
            "PYTHONDONTWRITEBYTECODE=1", "WORLDLINE_PRIVATE_SPARKLIB_PREBUILT=True",
            "gprbuild", "-c", "-u", "-j1", "-v", "-P", str(HERE / target["project"]),
            "-XWORLDLINE_BUILD=checks", "-XSPARKLIB_MODE=full",
            "-XSPARKLIB_BUILD=Production", "-XSPARKLIB_LIBRARY_TYPE=static",
            "-XSPARKLIB_INSTALLED=True", "-XWORLDLINE_PRIVATE_SPARKLIB_PREBUILT=True",
            target["unit"], "-cargs", "-gnatc", "-gnatwe"]


def tool_evidence(stdout, stderr, target, run):
    commands = []
    for line in (stdout + "\n" + stderr).splitlines():
        if " -c " not in " " + line + " " or ".ad" not in line:
            continue
        try:
            words = shlex.split(line)
        except ValueError:
            continue
        if words and (Path(words[0]).name.endswith("gcc") or
                      Path(words[0]).name.endswith("gnatgcc")):
            commands.append(words)
    required = {"-gnat2022", "-gnatwa", "-gnatwe", "-gnatVa", "-gnatf",
                "-gnata", "-gnatc", "-O2", "-g", "-fPIC"}
    exact = len(commands) == 1 and required.issubset(commands[0])
    if exact:
        units = [Path(w).name for w in commands[0] if w.endswith((".ads", ".adb"))]
        exact = units == [target["unit"]] and "-gnatp" not in commands[0]
    warning = bool(re.search(r"\b(?:warning|error):", stdout + stderr, re.I))
    passed = run["exit_code"] == 0 and run["stop"] is None and exact and not warning
    return {"compiler_commands": commands[:8], "exactly_one_strict_target": exact,
            "diagnostic_warning_or_error": warning, "legality_only_pass": passed,
            "unrecognized_or_response_file_command_is_not_pass": True}


def inside(base, selected, expected):
    value = config(expected)
    target = value["targets"][selected]
    source_state(value, target)
    before = retained.cgroup()
    if before["memory.max"] != str(8 * 1024**3) or before["memory.swap.max"] != "0":
        raise RuntimeError("original 8GiB/swap0 cgroup required")
    ram, restore = base / "ram", base / "restore"
    retained.mount_ram(ram)
    retained.mount_ram(restore)
    for name in ("tmp", "cache", "objects"):
        (ram / name).mkdir()
    mounts = [(ram / "tmp", Path(os.environ["TMPDIR"])),
              (ram / "cache", Path(os.environ["XDG_CACHE_HOME"])),
              (ram / "objects", HERE / target["object_mountpoint"])]
    run = retained.sandbox(command(target), ram, mounts)
    receipt(base, "tool-result.json", run)
    evidence = tool_evidence((ram / "tool.stdout").read_text(),
                             (ram / "tool.stderr").read_text(), target, run)
    files = retained.inventory(ram)
    receipt(base, "output-inventory.json", files)
    archive = retained.retain(base, ram, restore, files)
    receipt(base, "inside-result.json", {
        "tool": run, "evidence": evidence, "archive": archive,
        "cgroup_before": before, "cgroup_after": retained.cgroup(),
        "namespace": os.readlink("/proc/self/ns/mnt"), "phase_acceptance": False})
    return 0


def retained_result(base, target):
    path = base / "inside-result.json"
    if not path.is_file():
        return None
    result = json.loads(path.read_text())
    archive = base / "complete-output.tar.gz"
    if retained.digest(archive) != result["archive"]["sha256"]:
        raise RuntimeError("durable archive identity mismatch")
    if not result["archive"]["full_content_and_metadata_comparison"]:
        raise RuntimeError("complete RAM restore was not verified")
    with tarfile.open(archive, "r:gz") as tar:
        streams = [tar.extractfile("tool.stdout"), tar.extractfile("tool.stderr")]
        if any(stream is None for stream in streams):
            raise RuntimeError("actual tool output missing")
        stdout, stderr = [stream.read(retained.RAM_LIMIT + 1).decode() for stream in streams]
    evidence = tool_evidence(stdout, stderr, target, result["tool"])
    if evidence != result["evidence"]:
        raise RuntimeError("actual archived compiler evidence mismatch")
    return result


def parent(selected, label, expected):
    value = config(expected)
    target = value["targets"][selected]
    if shutil.disk_usage(ROOT).free < retained.RESERVE + retained.ARCHIVE_LIMIT + retained.RECEIPT_BUDGET:
        raise RuntimeError("bounded archive+receipts admission refused; no job credit")
    before = source_state(value, target)
    base = HERE / ("run-" + selected + "-" + label)
    base.mkdir(exist_ok=False)
    for name in ("ram", "restore"):
        (base / name).mkdir()
    receipt(base, "source-before.json", before)
    with (base / "complete-output.tar.gz").open("xb") as stream:
        os.posix_fallocate(stream.fileno(), 0, retained.ARCHIVE_LIMIT)
    retained.negative_writer(base)
    argv = ["unshare", "--user", "--map-root-user", "--mount", "--propagation", "private",
            sys.executable, str(Path(__file__).resolve()), "--inside", selected, str(base), expected]
    receipt(base, "launch.json", {"argv": argv, "tool_argv": command(target),
        "compiler_ram_bytes": retained.RAM_LIMIT, "restore_ram_bytes": retained.RAM_LIMIT,
        "archive_limit_bytes": retained.ARCHIVE_LIMIT, "receipt_limit_bytes": retained.RECEIPT_BUDGET,
        "original_imports_readonly": True, "phase_acceptance": False})
    try:
        code = subprocess.run(argv, check=False, timeout=220).returncode
        stop = None
    except subprocess.TimeoutExpired:
        code, stop = None, "220s collector timeout; no complete-result credit"
    after = source_state(value, target, before["sources"])
    receipt(base, "source-after.json", after)
    result = retained_result(base, target)
    private = not list((base / "ram").iterdir()) and not list((base / "restore").iterdir())
    passed = (code == 0 and stop is None and private and before == after and
              result is not None and result["evidence"]["legality_only_pass"])
    receipt(base, "result.json", {"child_exit": code, "stop": stop,
        "private_mountpoints_empty": private, "sources_unchanged": before == after,
        "retention": "COMPLETE_VERIFIED" if result else "LOST_EPHEMERAL_OUTPUTS",
        "legality_only_pass": passed, "phase_acceptance": False})
    return 0 if passed else 1


def main():
    args = sys.argv[1:]
    if len(args) == 4 and args[0] == "--inside":
        base = Path(args[2]).resolve()
        if not base.is_relative_to(HERE) or args[1] not in ("reservation", "utf8"):
            raise RuntimeError("unexpected child ownership/target")
        try:
            return inside(base, args[1], args[3])
        except Exception as error:
            receipt(base, "inside-failure.json", {"error": repr(error)[:2048],
                "classification": "FAILED_OR_LOST_EPHEMERAL_OUTPUTS", "phase_acceptance": False})
            return 1
    if len(args) == 3 and args[0] in ("reservation", "utf8") and re.fullmatch(r"[a-z0-9-]{1,24}", args[1]):
        return parent(*args)
    raise RuntimeError("expected target, new run label, reviewed proposal SHA256")


if __name__ == "__main__":
    sys.exit(main())
