"""Bounded, non-acceptance compiler qualification with read-only disk inputs."""
from pathlib import Path
import datetime
import errno
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RAM_LIMIT = 32 * 1024**2
ARCHIVE_LIMIT = 8 * 1024**2
RECEIPT_BUDGET = 4 * 1024**2
RESERVE = 10_000_000_000
ENTRY_LIMIT = 1024
CHUNK = HERE / "utf8-budgeted-chunks-v1/qualification-v2"
OBJECTS = {"objects": CHUNK / "qualification-obj",
           "attest": ROOT / "obj/attest-sha256",
           "sparklib": ROOT / "scratch/phase1-direct/private-sparklib/lib/gnat/sparklib_obj"}


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for _ in range((path.stat().st_size + 65535) // 65536):
            result.update(stream.read(65536))
    return result.hexdigest()


def save(path, value):
    data = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    if len(data) > 512 * 1024:
        raise RuntimeError("receipt size bound exceeded")
    with path.open("xb") as stream:
        if stream.write(data) != len(data):
            raise RuntimeError("short receipt write")


def cgroup():
    group = next(line[3:] for line in Path("/proc/self/cgroup").read_text().splitlines()
                 if line.startswith("0::"))
    base = Path("/sys/fs/cgroup") / group.lstrip("/")
    return {"path": str(base), **{name: (base / name).read_text().strip()
            for name in ("memory.max", "memory.swap.max", "memory.current",
                         "memory.peak", "memory.events", "memory.stat")}}


def inventory(base):
    entries = sorted(base.rglob("*"))
    if len(entries) >= ENTRY_LIMIT:
        raise RuntimeError("entry bound exceeded")
    result, total = {}, 0
    for path in entries:
        name, stat = str(path.relative_to(base)), path.lstat()
        if path.is_symlink() or not (path.is_file() or path.is_dir()):
            raise RuntimeError("unsupported archive entry")
        # USTAR has a 100-byte name and an optional 155-byte prefix.
        if not name.isascii() or len(name) > 240 or len(path.name) > 100:
            raise RuntimeError("USTAR pathname bound exceeded")
        item = {"mode": stat.st_mode & 0o7777, "mtime_ns": stat.st_mtime_ns,
                "uid": stat.st_uid, "gid": stat.st_gid,
                "kind": "file" if path.is_file() else "directory"}
        if path.is_file():
            total += stat.st_size
            if total > RAM_LIMIT:
                raise RuntimeError("logical data size exceeds archive budget")
            item.update(bytes=stat.st_size, sha256=digest(path))
        result[name] = item
    return result


class LimitedWriter:
    def __init__(self, stream, limit):
        self.stream, self.limit, self.position = stream, limit, 0

    def write(self, data):
        if len(data) > self.limit - self.position:
            raise OSError(errno.ENOSPC, "retained archive byte ceiling")
        count = self.stream.write(data)
        if count != len(data):
            raise OSError(errno.EIO, "short retained archive write")
        self.position += count
        return count

    def tell(self):
        return self.position

    def flush(self):
        self.stream.flush()


def retain(base, ram, restore, before):
    archive = base / "complete-output.tar.gz"
    with archive.open("r+b") as raw:
        writer = LimitedWriter(raw, ARCHIVE_LIMIT)
        with tarfile.open(fileobj=writer, mode="w|gz", format=tarfile.USTAR_FORMAT) as tar:
            for name, item in before.items():
                info = tar.gettarinfo(str(ram / name), arcname=name)
                info.uid, info.gid, info.uname, info.gname = 0, 0, "", ""
                info.mtime = item["mtime_ns"] // 1_000_000_000
                if item["kind"] == "file":
                    with (ram / name).open("rb") as source:
                        tar.addfile(info, source)
                else:
                    tar.addfile(info)
        raw.flush()
        os.fsync(raw.fileno())
        raw.truncate(writer.position)  # Release only unwritten reservation bytes.
        os.fsync(raw.fileno())
    with tarfile.open(archive, "r:gz") as tar:
        members = tar.getmembers()
        if len(members) != len(before) or {m.name.rstrip("/") for m in members} != set(before):
            raise RuntimeError("archive entry mismatch")
        tar.extractall(restore, filter="data")
    for name, item in sorted(before.items(), reverse=True):
        path = restore / name
        os.chmod(path, item["mode"])
        os.utime(path, ns=(item["mtime_ns"], item["mtime_ns"]))
    if inventory(restore) != before or inventory(ram) != before:
        raise RuntimeError("full restore or original comparison failed")
    return {"sha256": digest(archive), "bytes": archive.stat().st_size,
            "full_content_and_metadata_comparison": True}


def sandbox(command, ram, mounts):
    argv = ["bwrap", "--die-with-parent", "--unshare-pid", "--unshare-net",
            "--ro-bind", "/", "/", "--proc", "/proc", "--dev", "/dev",
            "--remount-ro", "/dev"]
    for source, target in mounts:
        argv.extend(("--bind", str(source), str(target)))
    argv.extend(("--", *command))
    with (ram / "tool.stdout").open("xb") as stdout, (ram / "tool.stderr").open("xb") as stderr:
        process = subprocess.Popen(argv, stdout=stdout, stderr=stderr, start_new_session=True)
        try:
            code = process.wait(timeout=180)
            stop = None
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            code, stop = process.wait(timeout=10), "180s tool deadline"
    return {"argv": argv, "exit_code": code, "stop": stop}


def chunk_command():
    return ["gnatprove", "-P", str(CHUNK / "utf8_chunk_qualification.gpr"),
            "--no-inlining", "--mode=all", "--level=3", "--report=all",
            "--checks-as-errors=on", "--proof-warnings=on", "--warnings=error",
            "--memlimit=1024", "--timeout=5", "-j2", "-XWORLDLINE_BUILD=checks",
            "-XSPARKLIB_MODE=full", "-XSPARKLIB_BUILD=Production",
            "-XSPARKLIB_LIBRARY_TYPE=static", "-XSPARKLIB_INSTALLED=True",
            "-u", "utf8_chunk_proposal.adb"]


def probe_command(base, ram):
    code = """from pathlib import Path
import errno, os, signal
root, writable = Path(os.environ['PROBE_READONLY']), Path(os.environ['TMPDIR'])
for path in (root / 'forbidden-write', Path('/dev/forbidden-write'), Path('/dev/shm/forbidden-write')):
    try:
        path.write_text('must not reach disk')
    except OSError as error:
        assert error.errno in (errno.EROFS, errno.ENOENT), error
    else:
        raise RuntimeError('read-only boundary absent')
with Path('/dev/null').open('wb') as null:
    assert null.write(b'device access works') == 19
(writable / 'before-kill.txt').write_text('retained after child SIGKILL\\n')
print('readonly boundary rejected write', flush=True)
os.kill(os.getpid(), signal.SIGKILL)
"""
    os.environ["PROBE_READONLY"] = str(base)
    return [sys.executable, "-c", code]


def mount_ram(path):
    if path.is_symlink() or list(path.iterdir()):
        raise RuntimeError("RAM mountpoint must be new, empty and nonsymlink")
    subprocess.run(["mount", "-t", "tmpfs", "-o",
                    "size=33554432,nr_inodes=1024,mode=0700,nodev,nosuid", "tmpfs", str(path)],
                   check=True, timeout=5)
    stat = os.statvfs(path)
    if stat.f_blocks * stat.f_frsize != RAM_LIMIT or stat.f_files > ENTRY_LIMIT:
        raise RuntimeError("actual RAM filesystem bounds mismatch")


def inside(base, mode):
    before = cgroup()
    if before["memory.max"] != str(8 * 1024**3) or before["memory.swap.max"] != "0":
        raise RuntimeError("original memory boundary absent")
    ram, restore = base / "ram", base / "restore"
    mount_ram(ram)
    mount_ram(restore)
    for name in ("tmp", "cache"):
        (ram / name).mkdir()
    mounts = [(ram / "tmp", Path(os.environ["TMPDIR"])),
              (ram / "cache", Path(os.environ["XDG_CACHE_HOME"]))]
    if mode == "chunk":
        for name, source in OBJECTS.items():
            shutil.copytree(source, ram / name)
            mounts.append((ram / name, source))
        command = chunk_command()
    else:
        command = probe_command(base, ram)
    inventory(ram)  # Reject seeds exceeding retention limits before launching.
    run = sandbox(command, ram, mounts)
    files = inventory(ram)
    save(base / "output-inventory.json", files)
    archive = retain(base, ram, restore, files)
    facts = dict(mode=mode, tool=run, files=files, archive=archive,
                 before=before, after=cgroup(), phase_acceptance=False,
                 mount_namespace=os.readlink("/proc/self/ns/mnt"))
    save(base / "inside-result.json", facts)
    return 0


def negative_writer(base):
    path = base / "writer-limit-negative.bin"
    with path.open("xb") as raw:
        limited = LimitedWriter(raw, 1024)
        limited.write(b"A" * 1024)
        try:
            limited.write(b"B")
        except OSError as error:
            if error.errno != errno.ENOSPC or limited.tell() != 1024:
                raise
        else:
            raise RuntimeError("archive limit not enforced before write")
    if path.stat().st_size != 1024:
        raise RuntimeError("archive limit overflow reached disk")


def source_state(mode):
    if mode != "chunk":
        return {"driver": digest(Path(__file__))}
    import utf8_chunk_proof_v2 as recipe
    if digest(recipe.RECIPE) != "a18d6f432295f22618a3938e82b6b84f69b677fcc5348773623ebf2d95c94dfc":
        raise RuntimeError("reviewed recipe changed")
    data = json.loads(recipe.RECIPE.read_text())
    if digest(recipe.PROJECT) != data["project_sha256"]:
        raise RuntimeError("reviewed project changed")
    pins = recipe.source_pins(data)
    return {"sources": pins, "original_object_trees":
            {name: inventory(path) for name, path in OBJECTS.items()},
            "driver": digest(Path(__file__))}


def check_retained(base, mode):
    result = json.loads((base / "inside-result.json").read_text())
    if digest(base / "complete-output.tar.gz") != result["archive"]["sha256"]:
        raise RuntimeError("durable archive changed")
    if mode == "probe":
        if result["tool"]["exit_code"] not in (-signal.SIGKILL, 128 + signal.SIGKILL):
            raise RuntimeError("expected killed probe child")
        expected = hashlib.sha256(b"retained after child SIGKILL\n").hexdigest()
        if result["files"].get("tmp/before-kill.txt", {}).get("sha256") != expected:
            raise RuntimeError("child failure evidence absent")
        stdout = hashlib.sha256(b"readonly boundary rejected write\n").hexdigest()
        if result["files"].get("tool.stdout", {}).get("sha256") != stdout:
            raise RuntimeError("read-only negative-control outcome absent")
        if (base / "forbidden-write").exists():
            raise RuntimeError("read-only negative control wrote to disk")
    return result["tool"]


def parent(mode):
    base = HERE / ("ram-qualification-" + mode + "-v2")
    if shutil.disk_usage(ROOT).free < RESERVE + ARCHIVE_LIMIT + RECEIPT_BUDGET:
        raise RuntimeError("insufficient bounded qualification disk budget")
    base.mkdir(exist_ok=False)
    for name in ("ram", "restore"):
        (base / name).mkdir()
    pins = source_state(mode)
    save(base / "source-before.json", pins)
    with (base / "complete-output.tar.gz").open("xb") as stream:
        os.posix_fallocate(stream.fileno(), 0, ARCHIVE_LIMIT)
    negative_writer(base)
    save(base / "launch.json", {"mode": mode, "source": digest(Path(__file__)),
         "archive_reserved_bytes": ARCHIVE_LIMIT, "other_receipt_budget": RECEIPT_BUDGET,
         "ram_bytes_each": RAM_LIMIT, "entries_each": ENTRY_LIMIT,
         "archive_capacity_rule": "Compression may exceed ceiling: retain partial archive/inventory, fail closed; no success credit",
         "failure_rule": "LOST_EPHEMERAL_OUTPUTS if no complete verified inside-result",
         "parent_mount_namespace": os.readlink("/proc/self/ns/mnt"), "phase_acceptance": False})
    argv = ["unshare", "--user", "--map-root-user", "--mount", "--propagation", "private",
            sys.executable, str(Path(__file__).resolve()), "--inside", mode, str(base)]
    try:
        code = subprocess.run(argv, check=False, timeout=220).returncode
        stop = None
    except subprocess.TimeoutExpired:
        code, stop = None, "220s collector deadline; incomplete evidence"
    private = not list((base / "ram").iterdir()) and not list((base / "restore").iterdir())
    complete = (base / "inside-result.json").is_file()
    tool = check_retained(base, mode) if complete else None
    unchanged = source_state(mode) == pins
    save(base / "result.json", {"child_exit": code, "stop": stop, "private_mounts": private,
         "retention": "COMPLETE_VERIFIED" if complete else "LOST_EPHEMERAL_OUTPUTS",
         "sources_and_original_objects_unchanged": unchanged, "tool": tool,
         "phase_acceptance": False, "argv": argv})
    tool_ok = tool is not None and (mode == "probe" or tool["exit_code"] == 0)
    return 0 if code == 0 and private and complete and unchanged and tool_ok else 1


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--inside" and sys.argv[2] in ("probe", "chunk"):
        sys.exit(inside(Path(sys.argv[3]), sys.argv[2]))
    if len(sys.argv) == 2 and sys.argv[1] in ("probe", "chunk"):
        sys.exit(parent(sys.argv[1]))
    raise SystemExit("expected probe or chunk")
