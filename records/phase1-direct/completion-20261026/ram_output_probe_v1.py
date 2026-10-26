"""Probe private RAM outputs under the original heavy-job cgroup; no product work."""
from pathlib import Path
import datetime
import errno
import hashlib
import json
import os
import subprocess
import sys
import tarfile

BASE = Path(__file__).resolve().parent / "ram-output-probe-v1"
PAYLOAD = BASE / "payload"
RESTORE = BASE / "restore"
LIMIT = 2 * 1024 * 1024


def stamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def save(name, value):
    with (BASE / name).open("x") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def cgroup():
    lines = Path("/proc/self/cgroup").read_text().splitlines()
    group = next(line[3:] for line in lines if line.startswith("0::"))
    path = Path("/sys/fs/cgroup") / group.lstrip("/")
    names = ("memory.max", "memory.swap.max", "memory.peak", "memory.current", "memory.stat")
    return {"path": str(path), **{name: (path / name).read_text().strip() for name in names}}


def inventory(directory):
    files = sorted(directory.iterdir())
    if len(files) != 2 or any(not p.is_file() or p.is_symlink() for p in files):
        raise RuntimeError("unexpected probe file set")
    result = {}
    for path in files:
        s = path.stat()
        result[path.name] = {"bytes": s.st_size, "mode": s.st_mode & 0o7777,
                             "mtime_ns": s.st_mtime_ns, "uid": s.st_uid, "gid": s.st_gid,
                             "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    return result


def fill_and_limit():
    data = bytes(range(256)) * 256
    with (PAYLOAD / "positive.bin").open("xb") as stream:
        for _ in range(16):
            if stream.write(data) != len(data):
                raise RuntimeError("short positive write")
    refused = False
    try:
        with (PAYLOAD / "over-limit.bin").open("xb") as stream:
            for _ in range(32):
                if stream.write(data) != len(data):
                    raise RuntimeError("short negative write without ENOSPC")
    except OSError as exc:
        if exc.errno != errno.ENOSPC:
            raise
        refused = True
    if not refused:
        raise RuntimeError("tmpfs size limit not enforced")
    return refused


def retain_and_restore(before):
    archive = BASE / "complete-payload.tar.gz"
    with archive.open("xb") as raw, tarfile.open(fileobj=raw, mode="w:gz") as tar:
        for name in sorted(before):
            tar.add(PAYLOAD / name, arcname=name, recursive=False)
    if archive.stat().st_size > LIMIT + 65536:
        raise RuntimeError("unexpected archive growth")
    with tarfile.open(archive, "r:gz") as tar:
        members = tar.getmembers()
        if len(members) != 2 or set(m.name for m in members) != set(before):
            raise RuntimeError("archive inventory mismatch")
        if any(not m.isfile() or m.size != before[m.name]["bytes"] for m in members):
            raise RuntimeError("archive metadata mismatch")
        tar.extractall(RESTORE, filter="data")
    for name, item in before.items():
        path = RESTORE / name
        os.chmod(path, item["mode"])
        os.utime(path, ns=(item["mtime_ns"], item["mtime_ns"]))
    if inventory(RESTORE) != before or inventory(PAYLOAD) != before:
        raise RuntimeError("full restore comparison or source recheck failed")
    return {"path": str(archive), "bytes": archive.stat().st_size,
            "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
            "full_file_content_and_metadata_comparison": True}


def inside():
    before = cgroup()
    if before["memory.max"] != str(8 * 1024**3) or before["memory.swap.max"] != "0":
        raise RuntimeError("original job cgroup limits absent")
    for directory in (PAYLOAD, RESTORE):
        subprocess.run(["mount", "-t", "tmpfs", "-o", "size=2m,mode=0700,nodev,nosuid",
                        "tmpfs", str(directory)], check=True, timeout=5)
    if os.statvfs(PAYLOAD).f_blocks * os.statvfs(PAYLOAD).f_frsize != LIMIT:
        raise RuntimeError("wrong actual filesystem size")
    facts = {"utc": stamp(), "user_ns": os.readlink("/proc/self/ns/user"),
             "mount_ns": os.readlink("/proc/self/ns/mnt"), "before": before,
             "memory_backed_limit_bytes": LIMIT, "negative_ENOSPC": fill_and_limit()}
    facts["filled"] = cgroup()
    files = inventory(PAYLOAD)
    facts["files"] = files
    facts["archive"] = retain_and_restore(files)
    facts["after_restore"] = cgroup()
    save("inside-result.json", facts)
    return 0


def main():
    if sys.argv[1:] == ["--inside"]:
        return inside()
    if sys.argv[1:]:
        raise RuntimeError("unexpected arguments")
    BASE.mkdir(exist_ok=False)
    PAYLOAD.mkdir()
    RESTORE.mkdir()
    parent = {"utc": stamp(), "user_ns": os.readlink("/proc/self/ns/user"),
              "mount_ns": os.readlink("/proc/self/ns/mnt"), "scope": cgroup()}
    save("parent-before.json", parent)
    argv = ["unshare", "--user", "--map-root-user", "--mount", "--propagation", "private",
            sys.executable, str(Path(__file__).resolve()), "--inside"]
    run = subprocess.run(argv, check=False, timeout=20)
    private = not list(PAYLOAD.iterdir()) and not list(RESTORE.iterdir())
    result = {"utc": stamp(), "argv": argv, "child_exit": run.returncode,
              "parent_directories_still_empty": private, "phase_acceptance": False}
    save("result.json", result)
    return 0 if run.returncode == 0 and private else 1


if __name__ == "__main__":
    sys.exit(main())
