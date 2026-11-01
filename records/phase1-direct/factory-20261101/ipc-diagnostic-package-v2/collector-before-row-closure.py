"""Bounded, non-acceptance compiler qualification with read-only disk inputs."""
from pathlib import Path
import datetime
import errno
import hashlib
import json
import math
import zlib
import os
import re
import shutil
import signal
import stat as file_kind
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
PROBE_SOURCE = ROOT / "records/phase1-direct/factory-20261101/private-ipc-probe-v3/probe.py"
PROBE_SHA256 = "8d7816d6a37ed353c6682dd27b97c4b7cbbc95f7e20282cb84a4c10177b16260"
IPC_MODES = {"ipc-probe": "normal", "ipc-alias-mismatch": "alias-mismatch",
             "ipc-namespace-mismatch": "namespace-mismatch",
             "ipc-leftover-socket": "leftover-socket", "ipc-sigkill": "sigkill"}
MODES = (*IPC_MODES, "ipc-cap-controls", "chunk")
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


class UnsupportedArchiveEntry(RuntimeError):
    def __init__(self, entry):
        self.entry = entry
        super().__init__("unsupported archive entry: " + json.dumps(entry, sort_keys=True))


def entry_details(base, path, initial):
    def snapshot(item):
        return {"mode": item.st_mode, "type": file_kind.S_IFMT(item.st_mode),
                "dev": item.st_dev, "ino": item.st_ino, "nlink": item.st_nlink,
                "size": item.st_size, "uid": item.st_uid, "gid": item.st_gid,
                "rdev": item.st_rdev, "mtime_ns": item.st_mtime_ns}
    result = {"relative_path": str(path.relative_to(base)), "base": str(base),
              "initial_lstat": snapshot(initial), "target_followed": False}
    latest = None
    try:
        latest = path.lstat()
        result["followup_lstat"] = snapshot(latest)
    except OSError as error:
        result["followup_errno"] = error.errno
        result["followup_error"] = str(error)[:1024]
    if file_kind.S_ISLNK(initial.st_mode) or (latest and file_kind.S_ISLNK(latest.st_mode)):
        try:
            target = os.readlink(path)
            result["readlink"] = target[:16384]
            result["readlink_truncated"] = len(target) > 16384
        except OSError as error:
            result["readlink_errno"] = error.errno
    return result


def receipt_bytes(base):
    entries = list(base.iterdir())
    if len(entries) > 32:
        raise RuntimeError("diagnostic direct-entry bound exceeded")
    return sum(path.lstat().st_size for path in entries
               if path.name != "complete-output.tar.gz" and
               file_kind.S_ISREG(path.lstat().st_mode))


def failure_log(source, destination, limit):
    result = {"source": str(source), "retained": str(destination), "bytes": 0}
    descriptor = None
    try:
        descriptor = os.open(source, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        before = os.fstat(descriptor)
        if not file_kind.S_ISREG(before.st_mode):
            return dict(result, status="NONREGULAR_NOT_READ", mode=before.st_mode)
        count = min(before.st_size, max(0, limit))
        hashed = hashlib.sha256()
        with destination.open("xb") as output:
            for _ in range((count + 65535) // 65536):
                data = os.read(descriptor, min(65536, count - result["bytes"]))
                if not data:
                    break
                if output.write(data) != len(data):
                    raise OSError(errno.EIO, "short failure-log write")
                hashed.update(data)
                result["bytes"] += len(data)
            output.flush()
            os.fsync(output.fileno())
        after = os.fstat(descriptor)
        changed = (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns)
        complete = not changed and result["bytes"] == before.st_size
        result.update(status="EXACT_BYTES" if complete else "PREFIX_ONLY_OR_CHANGED",
                      initial_bytes=before.st_size, final_bytes=after.st_size,
                      truncated=not complete, changed_during_copy=changed,
                      sha256=hashed.hexdigest())
    except OSError as error:
        result.update(status="ABSENT" if error.errno == errno.ENOENT else "NOT_FULLY_RETAINED",
                      errno=error.errno, error=str(error)[:1024], truncated=True)
    finally:
        if descriptor is not None:
            os.close(descriptor)
    return result


def failure_record(base, name, value):
    data = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    if len(data) > 65536 or receipt_bytes(base) + len(data) + 512 * 1024 > RECEIPT_BUDGET:
        raise RuntimeError("failure metadata/parent-receipt bound exceeded")
    save(base / name, value)


def retain_failure(base, ram, error, stage):
    facts = {"classification": "FAILED_INCOMPLETE_ARCHIVE_NO_PROOF_CREDIT",
             "stage": stage, "error_type": type(error).__name__, "error": str(error)[:4096],
             "error_text_truncated": len(str(error)) > 4096,
             "unsupported_entry": getattr(error, "entry", None),
             "full_archive_verified": False, "other_ephemeral_output": "NOT_FULLY_RETAINED",
             "tool_run_receipt": "tool-result.json" if (base / "tool-result.json").is_file() else None,
             "phase_acceptance": False}
    failure_record(base, "failure-entry.json", facts)
    facts["logs"] = {}
    for name in ("stdout", "stderr"):
        # Reserve 64KiB final metadata and 512KiB original parent result budget.
        room = max(0, RECEIPT_BUDGET - receipt_bytes(base) - 576 * 1024)
        facts["logs"][name] = failure_log(ram / ("tool." + name),
                                          base / ("failure-tool." + name), room)
    failure_record(base, "failure.json", facts)


def inventory(base):
    entries = sorted(base.rglob("*"))
    if len(entries) >= ENTRY_LIMIT:
        raise RuntimeError("entry bound exceeded")
    result, total = {}, 0
    for path in entries:
        name, stat = str(path.relative_to(base)), path.lstat()
        if path.is_symlink() or not (path.is_file() or path.is_dir()):
            raise UnsupportedArchiveEntry(entry_details(base, path, stat))
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
    argv = ["bwrap", "--die-with-parent", "--unshare-pid", "--unshare-net", "--unshare-ipc",
            "--ro-bind", "/", "/", "--proc", "/proc", "--dev", "/dev",
            "--dir", "/dev/shm", "--bind", str(ram / "ipc"), "/dev/shm",
            "--remount-ro", "/dev"]
    for source, target in mounts:
        argv.extend(("--bind", str(source), str(target)))
    for name, value in ipc_environment(ram.parent).items():
        argv.extend(("--setenv", name, value))
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
    ram = base / "ram"
    stage = "setup"
    try:
        before = cgroup()
        if before["memory.max"] != str(8 * 1024**3) or before["memory.swap.max"] != "0":
            raise RuntimeError("original memory boundary absent")
        ram, restore = base / "ram", base / "restore"
        mount_ram(ram)
        mount_ram(restore)
        for name in ("tmp", "cache", "ipc"):
            (ram / name).mkdir(mode=0o700)
        mounts = [(ram / "tmp", Path(os.environ["TMPDIR"])),
                  (ram / "cache", Path(os.environ["XDG_CACHE_HOME"]))]
        if mode == "chunk":
            for name, source in OBJECTS.items():
                shutil.copytree(source, ram / name)
                mounts.append((ram / name, source))
            command = chunk_command()
        else:
            command = ipc_command(mode)
        stage = "seed inventory"
        inventory(ram)  # Reject seeds exceeding retention limits before launching.
        stage = "tool"
        run = sandbox(command, ram, mounts)
        save(base / "tool-result.json", run)
        stage = "post-tool inventory"
        files = inventory(ram)
        save(base / "output-inventory.json", files)
        stage = "archive and restore"
        archive = retain(base, ram, restore, files)
        facts = dict(mode=mode, tool=run, files=files, archive=archive,
                     before=before, after=cgroup(), phase_acceptance=False,
                     mount_namespace=os.readlink("/proc/self/ns/mnt"))
        save(base / "inside-result.json", facts)
        return 0

    except Exception as error:
        retain_failure(base, ram, error, stage)
        return 1


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
        if mode in IPC_MODES and (PROBE_SOURCE.resolve() != PROBE_SOURCE or
                PROBE_SOURCE.is_symlink() or
                not PROBE_SOURCE.is_file() or digest(PROBE_SOURCE) != PROBE_SHA256):
            raise RuntimeError("exact fixed IPC probe source changed")
        return {"driver": digest(Path(__file__)), "probe":
                PROBE_SHA256 if mode in IPC_MODES else None}
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
    base = HERE / ("ram-qualification-" + mode + "-v6")
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
    boundary = host_boundary(base)
    save(base / "host-boundary-before.json", boundary)
    require(all(boundary["host_absent"].values()), "owned host names already present")
    save(base / "launch.json", {"mode": mode, "source": digest(Path(__file__)),
         "archive_reserved_bytes": ARCHIVE_LIMIT, "other_receipt_budget": RECEIPT_BUDGET,
         "ram_bytes_each": RAM_LIMIT, "entries_each": ENTRY_LIMIT,
         "archive_capacity_rule": "Compression may exceed ceiling: retain partial archive/inventory, fail closed; no success credit",
         "failure_rule": "LOST_EPHEMERAL_OUTPUTS if no complete verified inside-result",
         "parent_mount_namespace": os.readlink("/proc/self/ns/mnt"), "phase_acceptance": False})
    argv = ["unshare", "--user", "--map-root-user", "--mount", "--propagation", "private",
            sys.executable, "-B", str(Path(__file__).resolve()), "--inside", mode, str(base)]
    try:
        code = subprocess.run(argv, check=False, timeout=220).returncode
        stop = None
    except subprocess.TimeoutExpired:
        code, stop = None, "220s collector deadline; incomplete evidence"
    private = not list((base / "ram").iterdir()) and not list((base / "restore").iterdir())
    complete = (base / "inside-result.json").is_file()
    tool = check_retained(base, mode) if complete else (
        json.loads((base / "tool-result.json").read_text())
        if (base / "tool-result.json").is_file() else None)
    unchanged = source_state(mode) == pins
    after = host_boundary(base)
    save(base / "host-boundary-after.json", after)
    host_ok = after == boundary and all(after["host_absent"].values())
    try:
        control = check_ipc_retained(base, mode, complete, tool, boundary)
    except Exception as error:
        control = dict(observed=False, error=str(error)[:4096])
    save(base / "ipc-profile-check.json", control)
    diagnostic = diagnostic_write(base, complete, tool) if mode == "ipc-probe" else None
    save(base / "result.json", {"child_exit": code, "stop": stop, "private_mounts": private,
         "retention": "COMPLETE_VERIFIED" if complete else "LOST_EPHEMERAL_OUTPUTS",
         "sources_and_original_objects_unchanged": unchanged, "tool": tool,
         "host_boundary_unchanged_and_owned_names_absent": host_ok,
         "private_ipc_control": control,
         "mount_diagnostic_receipt": diagnostic,
         "phase_acceptance": False, "argv": argv})
    tool_ok = tool is not None and (tool["exit_code"] == 0 or
              (mode == "ipc-sigkill" and tool["exit_code"] in (-9, 137)))
    return 0 if (code == 0 and private and complete and unchanged and tool_ok
                 and host_ok and control["observed"]) else 1


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def identity(info):
    return [info.st_dev, info.st_ino]


def host_boundary(base):
    host = Path("/dev/shm")
    info = host.lstat()
    require(file_kind.S_ISDIR(info.st_mode), "host shm must be a real directory")
    token = hashlib.sha256(str(base).encode("utf-8")).hexdigest()[:32]
    absent = {}
    for name in ("wl-ipc-" + token + ".witness", "sem.wl-ipc-" + token):
        try:
            (host / name).lstat()
        except FileNotFoundError:
            absent[name] = True
        else:
            absent[name] = False
    return dict(host_identity=identity(info), token=token, host_absent=absent,
                parent_ipc=os.readlink("/proc/self/ns/ipc"),
                parent_mnt=os.readlink("/proc/self/ns/mnt"))


def ipc_environment(base):
    data = json.loads((base / "host-boundary-before.json").read_text())
    return {"PROBE_READONLY": str(base), "PROBE_RAM_IPC": str(base / "ram/ipc"),
            "PROBE_TOKEN": data["token"], "PROBE_HOST_SHM_DEV": str(data["host_identity"][0]),
            "PROBE_HOST_SHM_INO": str(data["host_identity"][1]),
            "PROBE_PARENT_IPC_NS": data["parent_ipc"],
            "PROBE_PARENT_MOUNT_NS": data["parent_mnt"]}


def ipc_command(mode):
    if mode == "ipc-cap-controls":
        return [sys.executable, "-B", str(Path(__file__).resolve()), "--cap-controls"]
    require(mode in IPC_MODES, "unsupported private IPC mode")
    require(PROBE_SOURCE.resolve() == PROBE_SOURCE and
            not PROBE_SOURCE.is_symlink() and PROBE_SOURCE.is_file() and
            digest(PROBE_SOURCE) == PROBE_SHA256, "exact IPC source pin mismatch")
    return [sys.executable, "-B", str(PROBE_SOURCE), IPC_MODES[mode]]


def owned_remove(path, expected):
    info = path.lstat()
    require(identity(info) == expected and file_kind.S_ISREG(info.st_mode)
            and info.st_nlink == 1 and info.st_uid == os.geteuid(),
            "owned fixture identity changed; no unlink")
    path.unlink()
    try:
        path.lstat()
    except FileNotFoundError:
        return
    raise RuntimeError("owned fixture remains")


def byte_cap(directory, token):
    path = directory / ("quota-bytes-" + token)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    expected = identity(os.fstat(fd))
    written, attempts, refusal, errors = 0, 0, None, []
    try:
        block = b"Q" * 4096
        for _ in range(RAM_LIMIT // len(block) + 1):
            attempts += 1
            try:
                count = os.write(fd, block)
            except OSError as error:
                refusal = error.errno
                break
            require(0 < count <= len(block), "invalid quota fixture write")
            written += count
    except Exception as error:
        errors.append(str(error)[:512])
    finally:
        try:
            os.close(fd)
        except OSError as error:
            errors.append("close: " + str(error)[:512])
        try:
            owned_remove(path, expected)
        except Exception as error:
            errors.append("cleanup: " + str(error)[:512])
    passed = refusal == errno.ENOSPC and written <= RAM_LIMIT and not errors
    return dict(passed=passed, written_bytes=written, attempts=attempts,
                attempt_bytes=4096, refusal_errno=refusal, cleanup_ok=not errors,
                errors=errors, maximum_attempts=RAM_LIMIT // 4096 + 1)


def cleanup_inode_fixtures(directory, expected, files):
    errors = []
    count = 0
    for name, file_id in files:
        try:
            owned_remove(directory / name, file_id)
        except Exception as error:
            count += 1
            if len(errors) < 8:
                errors.append(str(error)[:512])
    try:
        info = directory.lstat()
        require(identity(info) == expected and file_kind.S_ISDIR(info.st_mode)
                and info.st_uid == os.geteuid(), "owned fixture directory changed")
        directory.rmdir()  # Empty, owned fixture only; never recursive deletion.
        try:
            directory.lstat()
        except FileNotFoundError:
            pass
        else:
            raise RuntimeError("owned fixture directory remains")
    except Exception as error:
        count += 1
        if len(errors) < 8:
            errors.append(str(error)[:512])
    return dict(ok=count == 0, error_count=count, errors=errors)


def inode_cap(directory, token):
    path = directory / ("quota-inodes-" + token)
    path.mkdir(mode=0o700)
    expected = identity(path.lstat())
    files, refusal, errors, attempts = [], None, [], 0
    try:
        for number in range(ENTRY_LIMIT):
            name = "entry-" + str(number)
            attempts += 1
            try:
                fd = os.open(path / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                             os.O_NOFOLLOW, 0o600)
            except OSError as error:
                refusal = error.errno
                break
            try:
                files.append((name, identity(os.fstat(fd))))
            finally:
                os.close(fd)
    except Exception as error:
        errors.append(str(error)[:512])
    cleanup = cleanup_inode_fixtures(path, expected, files)
    return dict(passed=refusal == errno.ENOSPC and not errors and cleanup["ok"],
                created_files=len(files), attempts=attempts, refusal_errno=refusal,
                directory_inodes=1, maximum_file_attempts=ENTRY_LIMIT,
                cleanup=cleanup, errors=errors)


def bounded_text(path, limit):
    with path.open("r") as stream:
        data = stream.read(limit + 1)
    require(len(data) <= limit, "bounded text exceeded: " + str(path))
    return data


def quota_context():
    token = os.environ.get("PROBE_TOKEN", "")
    require(re.fullmatch("[0-9a-f]{32}", token) is not None, "invalid quota token")
    names = ("PROBE_RAM_IPC", "TMPDIR")
    paths = [os.environ.get(name, "") for name in names]
    require(all(0 < len(p) <= 1024 and p.startswith("/") and
                ".." not in p.split("/") for p in paths), "invalid quota paths")
    descriptors = []
    try:
        for path in ("/dev/shm", *paths):
            descriptors.append(os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW))
        ipc, alias, tmp = [os.fstat(fd) for fd in descriptors]
        require(identity(ipc) == identity(alias), "quota alias mismatch")
        host = [os.environ.get("PROBE_HOST_SHM_" + n, "") for n in ("DEV", "INO")]
        require(all(re.fullmatch("[0-9]{1,20}", n) is not None for n in host), "bad host ID")
        require(identity(ipc) != [int(n) for n in host], "quota host alias")
        require(ipc.st_dev == tmp.st_dev and ipc.st_uid == os.geteuid() and
                file_kind.S_IMODE(ipc.st_mode) == 0o700, "quota filesystem identity")
        fs = os.fstatvfs(descriptors[0])
        require(fs.f_blocks * fs.f_frsize == RAM_LIMIT and 0 < fs.f_files <= ENTRY_LIMIT,
                "quota filesystem caps changed")
        namespaces = {n: os.readlink("/proc/self/ns/" + n) for n in ("ipc", "mnt")}
        for n, env in (("ipc", "PROBE_PARENT_IPC_NS"), ("mnt", "PROBE_PARENT_MOUNT_NS")):
            require(namespaces[n] != os.environ.get(env) and
                    re.fullmatch(n + r":\[[0-9]+\]", os.environ.get(env, "")) is not None,
                    "quota namespace shared/invalid")
        return dict(token=token, private_identity=identity(ipc), uid=os.getuid(),
                    euid=os.geteuid(), namespaces=namespaces, bytes=RAM_LIMIT,
                    inodes=fs.f_files, uid_map=bounded_text(Path("/proc/self/uid_map"), 1024))
    finally:
        for fd in reversed(descriptors):
            os.close(fd)


def cap_controls():
    facts = dict(schema="worldline.private-ipc-cap-controls.v1", status="FAILED",
                 phase_acceptance=False)
    try:
        context = quota_context()  # Fail before fixture creation on a wrong topology.
        facts["context"] = context
        facts["bytes"] = byte_cap(Path("/dev/shm"), context["token"])
        require(facts["bytes"]["passed"], "byte quota or owned cleanup failed")
        facts["inodes"] = inode_cap(Path("/dev/shm"), context["token"])
        require(facts["bytes"]["passed"] and facts["inodes"]["passed"], "quota control failed")
        facts["status"] = "PASSED"
    except Exception as error:
        facts["error"] = str(error)[:2048]
    save(Path(os.environ["TMPDIR"]) / "private-ipc-cap-controls.json", facts)
    print(json.dumps(facts, sort_keys=True), flush=True)
    return 0 if facts["status"] == "PASSED" else 2


def archived_json(base, name):
    with tarfile.open(base / "complete-output.tar.gz", "r:gz") as tar:
        member = tar.getmember(name)
        require(member.isfile() and member.size <= 16384, "bounded report absent/nonregular")
        with tar.extractfile(member) as stream:
            data = stream.read(16385)
    require(len(data) <= 16384, "report read exceeds bound")
    return json.loads(data)


def check_ipc_retained(base, mode, complete, tool, boundary):
    if mode == "chunk":
        return dict(observed=True, claim="No mechanism qualification or proof credit from this flag")
    require(tool is not None and tool["stop"] is None, "tool outcome absent or deadline")
    if mode == "ipc-leftover-socket":
        facts = json.loads((base / "failure-entry.json").read_text())
        entry = facts["unsupported_entry"]
        expected = "tmp/leftover-" + boundary["token"] + ".sock"
        require(not complete and tool["exit_code"] == 0 and entry["relative_path"] == expected
                and entry["initial_lstat"]["type"] == file_kind.S_IFSOCK,
                "leftover socket rejection not observed")
        return dict(observed=True, expected="NO_COMPLETE_ARCHIVE", proof_credit=False)
    require(complete, "complete archive and restore absent")
    result = json.loads((base / "inside-result.json").read_text())
    if mode == "ipc-cap-controls":
        facts = archived_json(base, "tmp/private-ipc-cap-controls.json")
        require(tool["exit_code"] == 0 and facts["status"] == "PASSED" and
                facts["schema"] == "worldline.private-ipc-cap-controls.v1" and
                facts["bytes"]["passed"] is True and facts["inodes"]["passed"] is True and
                facts["bytes"]["cleanup_ok"] is True and facts["inodes"]["cleanup"]["ok"] is True and
                not any(n.startswith("ipc/") for n in result["files"]),
                "aggregate quota controls absent")
        return dict(observed=True, report=facts, proof_credit=False)
    negative = {"ipc-alias-mismatch": "alias mismatch", "ipc-namespace-mismatch": "namespace shared"}
    if mode in negative:
        facts = archived_json(base, "tool.stdout")
        require(tool["exit_code"] == 2 and facts["status"] == "FAILED" and
                facts["stage"] == "private identity" and facts["error"] == negative[mode]
                and facts["semaphore_cleanup"]["created"] is False and
                facts["schema"] == "worldline.private-ipc-probe.v1" and
                facts["mode"] == IPC_MODES[mode],
                "identity/namespace negative outcome absent")
        require("tmp/private-ipc-probe.json" not in result["files"] and
                not any(n.startswith("ipc/") for n in result["files"]),
                "negative control created private IPC artifacts")
        return dict(observed=True, expected="REFUSED_BEFORE_IPC_CREATION", report=facts,
                    proof_credit=False)
    return check_positive_ipc(base, mode, tool, boundary, result)


def check_positive_ipc(base, mode, tool, boundary, result):
    facts = archived_json(base, "tmp/private-ipc-probe.json")
    expected_status = "SIGKILL_PREPARED" if mode == "ipc-sigkill" else "PASSED"
    require(facts["schema"] == "worldline.private-ipc-probe.v1" and
            facts["mode"] == IPC_MODES[mode] and facts["status"] == expected_status and
            facts["stage"] == "completed", "positive IPC report absent")
    require(tool["exit_code"] in ((-9, 137) if mode == "ipc-sigkill" else (0,)),
            "positive IPC tool status mismatch")
    require(facts["ipc_namespace"] != boundary["parent_ipc"] and
            facts["mount_namespace"] != boundary["parent_mnt"] and
            facts["host_identity"] == boundary["host_identity"] and
            facts["private_identity"] != boundary["host_identity"], "IPC identity mismatch")
    require(facts["output_bytes"] == RAM_LIMIT and 0 < facts["output_inodes"] <= ENTRY_LIMIT,
            "IPC quota report mismatch")
    cleanup = facts["semaphore_cleanup"]
    require(cleanup == dict(created=True, close="OK", unlink="OK", errors=[], backing_absent=True)
            and facts["directory_close_errors"] == [], "semaphore cleanup incomplete")
    witness = b"private IPC witness\n"
    name = "wl-ipc-" + boundary["token"] + ".witness"
    expected = hashlib.sha256(witness).hexdigest()
    require(facts["witness"] == dict(basename=name, bytes=len(witness), sha256=expected) and
            result["files"].get("ipc/" + name, {}).get("sha256") == expected,
            "private witness missing from complete archive")
    sem = facts["semaphore"]
    require(sem["name"] == "/wl-ipc-" + boundary["token"] and
            sem["backing"] == "sem.wl-ipc-" + boundary["token"] and
            sem["exclusive_reopen_errno"] == errno.EEXIST and sem["operations"] ==
            ["empty-EAGAIN", "post", "consume", "empty-EAGAIN"] and
            "ipc/" + sem["backing"] not in result["files"], "semaphore operations mismatch")
    refused = facts["write_refusals"]
    require([r["path"] for r in refused] == [str(base / "forbidden-write"), "/dev/forbidden-write"]
            and all(r["errno"] in (errno.EROFS, errno.ENOENT) for r in refused)
            and facts["devnull_write_bytes"] == 19 and not (base / "forbidden-write").exists(),
            "original root/device controls absent")
    return dict(observed=True, report=facts, proof_credit=False)


def diagnostic_object(pairs):
    require(len(pairs) <= 512, "diagnostic object member bound")
    result = {}
    for key, value in pairs:
        require(key not in result, "diagnostic duplicate JSON key")
        result[key] = value
    return result


def diagnostic_constant(value):
    raise ValueError("nonfinite diagnostic JSON constant: " + value)


def diagnostic_float(value):
    result = float(value)
    require(math.isfinite(result), "nonfinite diagnostic JSON float")
    return result


def diagnostic_json(raw, limit):
    require(isinstance(raw, bytes) and len(raw) <= limit, "diagnostic JSON byte bound")
    result = json.loads(raw.decode("ascii"), object_pairs_hook=diagnostic_object,
                        parse_constant=diagnostic_constant, parse_float=diagnostic_float)
    require(type(result) is dict, "diagnostic JSON object required")
    return result


def diagnostic_archive(base, complete, tool):
    require(complete is True, "diagnostic complete archive absent")
    raw = bounded_text(base / "inside-result.json", 512 * 1024).encode("ascii")
    result = diagnostic_json(raw, 512 * 1024)
    archive = result["archive"]
    size = (base / "complete-output.tar.gz").stat().st_size
    require(type(archive["bytes"]) is int and 0 < size == archive["bytes"] <= ARCHIVE_LIMIT,
            "diagnostic archive byte bound/mismatch")
    require(archive["full_content_and_metadata_comparison"] is True and
            digest(base / "complete-output.tar.gz") == archive["sha256"],
            "diagnostic archive identity/restore mismatch")
    require(tool is not None and result["tool"] == tool, "diagnostic tool receipt mismatch")
    require(type(result["files"]) is dict and len(result["files"]) < ENTRY_LIMIT,
            "diagnostic inventory bound")
    return result["files"], archive


class DiagnosticInflater:
    # Existing payload cap plus <=1023 headers, per-file padding and record tail.
    LIMIT = RAM_LIMIT + (ENTRY_LIMIT - 1) * (512 + 511) + 1024 + 10239

    def __init__(self, source):
        self.source, self.decoder = source, zlib.decompressobj(31)
        self.pending, self.compressed, self.expanded = b"", 0, 0
        self.hashed = hashlib.sha256()

    def read(self, size):
        require(type(size) is int and 0 < size <= 65536, "diagnostic read request bound")
        output = bytearray()
        for _ in range(size + ARCHIVE_LIMIT // 65536 + 2):
            if len(output) == size:
                return bytes(output)
            if self.decoder.eof:
                require(not self.decoder.unused_data and not self.pending and
                        not self.source.read(1), "diagnostic gzip trailing/concatenated data")
                return bytes(output)
            if self.pending:
                data, self.pending = self.pending, b""
            else:
                data = self.source.read(min(65536, ARCHIVE_LIMIT + 1 - self.compressed))
                self.compressed += len(data)
                require(self.compressed <= ARCHIVE_LIMIT and data, "diagnostic compressed bound/EOF")
                self.hashed.update(data)
            chunk = self.decoder.decompress(data, size - len(output))
            self.pending = self.decoder.unconsumed_tail
            require(chunk or len(self.pending) < len(data) or self.decoder.eof,
                    "diagnostic inflater made no progress")
            output.extend(chunk)
            self.expanded += len(chunk)
            require(self.expanded <= self.LIMIT, "diagnostic expanded framing bound")
        raise RuntimeError("diagnostic inflater iteration bound")


def diagnostic_octal(raw):
    value = raw.strip(b"\0 ")
    require(value and re.fullmatch(b"[0-7]+", value) is not None,
            "diagnostic unsupported numeric encoding")
    return int(value, 8)


def diagnostic_header_text(raw):
    value, separator, rest = raw.partition(b"\0")
    require(not separator or not rest.strip(b"\0"), "diagnostic header string padding")
    require(all(32 <= value <= 126 for value in value), "diagnostic header text encoding")
    return value.decode("ascii")


def diagnostic_header(header):
    require(len(header) == 512 and header[257:265] == b"ustar\00000",
            "diagnostic unsupported archive format")
    expected = sum(header[:148]) + 8 * 32 + sum(header[156:])
    require(diagnostic_octal(header[148:156]) == expected, "diagnostic USTAR checksum")
    require(header[156:157] in (b"0", b"5"), "diagnostic unsupported archive entry/extension")
    require(not header[157:257].strip(b"\0") and not header[265:329].strip(b"\0")
            and not header[500:].strip(b"\0"), "diagnostic noncanonical link/names/reserved")
    for field in (header[329:337], header[337:345]):
        require(not field.strip(b"\0 ") or diagnostic_octal(field) == 0,
                "diagnostic device metadata")
    name = diagnostic_header_text(header[:100])
    prefix = diagnostic_header_text(header[345:500])
    name = prefix + "/" + name if prefix else name
    kind = "file" if header[156:157] == b"0" else "directory"
    name = name[:-1] if kind == "directory" and name.endswith("/") else name
    require(name and not name.startswith("/") and len(name) <= 240 and
            all(part not in ("", ".", "..") for part in name.split("/")) and
            len(name.split("/")[-1]) <= 100, "diagnostic archive path")
    return dict(name=name, kind=kind, bytes=diagnostic_octal(header[124:136]),
                mode=diagnostic_octal(header[100:108]), uid=diagnostic_octal(header[108:116]),
                gid=diagnostic_octal(header[116:124]), mtime=diagnostic_octal(header[136:148]))


def diagnostic_inventory_member(item, files, seen, logical):
    name, size = item["name"], item["bytes"]
    require(name not in seen and name in files, "diagnostic duplicate/unlisted archive member")
    expected = files[name]
    require(type(expected) is dict and expected["kind"] == item["kind"],
            "diagnostic inventory kind mismatch")
    for key in ("mode", "uid", "gid", "mtime_ns"):
        require(type(expected[key]) is int and expected[key] >= 0, "diagnostic metadata type/range")
    require(item["mode"] == expected["mode"] and item["uid"] == item["gid"] == 0
            and item["mtime"] == expected["mtime_ns"] // 1_000_000_000,
            "diagnostic normalized archive metadata mismatch")
    if item["kind"] == "directory":
        require(size == 0, "diagnostic directory payload")
    else:
        require(type(expected["bytes"]) is int and 0 <= size == expected["bytes"]
                and logical + size <= RAM_LIMIT, "diagnostic logical payload bound/mismatch")
        require(type(expected["sha256"]) is str and
                re.fullmatch(r"[0-9a-f]{64}", expected["sha256"]) is not None,
                "diagnostic inventory digest format")
    return logical + size


def diagnostic_payload(reader, item, expected, streams):
    size, name = item["bytes"], item["name"]
    capture = name in ("tool.stdout", "tmp/private-ipc-probe.json")
    if capture:
        require(size <= (8193 if name == "tool.stdout" else 8192),
                "diagnostic captured stream byte bound")
    hashed, captured = hashlib.sha256(), bytearray()
    for _ in range((size + 65535) // 65536):
        block = reader.read(min(65536, size))
        require(len(block) == min(65536, size), "diagnostic truncated payload")
        size -= len(block)
        hashed.update(block)
        if capture:
            captured.extend(block)
    if item["kind"] == "file":
        require(hashed.hexdigest() == expected["sha256"], "diagnostic stream digest mismatch")
    padding = (-item["bytes"]) % 512
    require(not padding or reader.read(padding) == b"\0" * padding,
            "diagnostic payload padding")
    if capture:
        streams[name] = bytes(captured)


def diagnostic_scan_stream(source, files, archive):
    require(type(files) is dict and len(files) < ENTRY_LIMIT, "diagnostic inventory bound")
    reader, seen, logical, streams = DiagnosticInflater(source), set(), 0, {}
    for count in range(ENTRY_LIMIT + 1):
        header = reader.read(512)
        require(len(header) == 512, "diagnostic truncated USTAR header")
        if header == b"\0" * 512:
            require(reader.read(512) == b"\0" * 512, "diagnostic second end record")
            padding = (-reader.expanded) % 10240
            require(not padding or reader.read(padding) == b"\0" * padding,
                    "diagnostic USTAR record padding")
            require(reader.read(1) == b"" and seen == set(files),
                    "diagnostic EOF/inventory mismatch")
            require(reader.compressed == archive["bytes"] and
                    reader.hashed.hexdigest() == archive["sha256"], "diagnostic scanned archive changed")
            return streams
        require(count < ENTRY_LIMIT - 1, "diagnostic archive entry bound before payload")
        item = diagnostic_header(header)
        logical = diagnostic_inventory_member(item, files, seen, logical)
        seen.add(item["name"])
        diagnostic_payload(reader, item, files[item["name"]], streams)
    raise RuntimeError("diagnostic archive scan bound")


def diagnostic_scan(base, files, archive):
    with (base / "complete-output.tar.gz").open("rb") as source:
        return diagnostic_scan_stream(source, files, archive)


def diagnostic_row(item, previous):
    require(type(item) is dict and type(item["line_index"]) is int and
            previous < item["line_index"] < 512, "diagnostic row index/order")
    raw = item["raw"]
    require(type(raw) is str and raw.isascii() and len(raw) <= 2048 and
            all(ord(value) >= 32 or value == "\t" for value in raw) and "\x7f" not in raw,
            "diagnostic raw row bound")
    fields = raw.split()
    require(len(fields) >= 10 and "-" in fields[6:], "diagnostic mount row malformed")
    sep = fields.index("-", 6)
    require(len(fields) >= sep + 4 and re.fullmatch(r"[0-9]{1,64}", fields[0]) is not None,
            "diagnostic mount row ID/filesystem")
    target = fields[4]
    require(target == "/dev/shm" or "/dev/shm".startswith(target.rstrip("/") + "/"),
            "diagnostic retained row does not cover shm")
    return dict(mount_id=fields[0], device=fields[2], root=fields[3], mountpoint=target,
                options=fields[5], filesystem=fields[sep + 1], super_options=fields[sep + 3])


def diagnostic_rows(evidence):
    require(type(evidence) is dict and len(json.dumps(evidence, sort_keys=True).encode("ascii"))
            <= 3072, "diagnostic evidence byte bound")
    rows, count = evidence["rows"], evidence["candidate_count"]
    require(type(rows) is list and type(count) is int and 0 < count <= 512,
            "diagnostic candidate count/type")
    kept, omitted = evidence["retained_rows"], evidence["omitted_rows"]
    require(type(kept) is int and type(omitted) is int and
            0 <= kept == len(rows) <= count and omitted == count - kept,
            "diagnostic candidate accounting")
    require(type(evidence["complete"]) is bool and type(evidence["selected_id_exact"]) is bool
            and evidence["complete"] == (kept == count and evidence["selected_id_exact"]),
            "diagnostic completeness accounting")
    require(re.fullmatch(r"[0-9a-f]{64}", evidence["candidate_lines_joined_LF_sha256"])
            is not None, "diagnostic candidate digest format")
    parsed, previous = [], -1
    for row in rows:
        parsed.append(diagnostic_row(row, previous))
        previous = row["line_index"]
    return rows, parsed


def diagnostic_complete(facts, evidence, rows, parsed):
    require(evidence["complete"] is True, "diagnostic candidates incomplete: hash/join UNPROVEN")
    joined = "\n".join(item["raw"] for item in rows).encode("ascii")
    require(hashlib.sha256(joined).hexdigest() == evidence["candidate_lines_joined_LF_sha256"],
            "diagnostic complete candidate digest mismatch")
    require(evidence["selection_rule"] == "first_longest_covering_row_in_file_order",
            "diagnostic selector identity mismatch")
    longest = max(len(item["mountpoint"]) for item in parsed)
    best = [i for i, item in enumerate(parsed) if len(item["mountpoint"]) == longest]
    selected = best[0]
    require(type(evidence["selected_line_index"]) is int and
            evidence["selected_line_index"] == rows[selected]["line_index"] and
            evidence["selected_mount_id"] == parsed[selected]["mount_id"] and
            facts["mounts"]["shm"] == parsed[selected], "diagnostic selected row mismatch")
    require(type(evidence["equal_longest_count"]) is int and
            evidence["equal_longest_count"] == len(best) and
            type(evidence["ambiguous"]) is bool and evidence["ambiguous"] == (len(best) > 1),
            "diagnostic tie accounting")
    require(hashlib.sha256(evidence["selected_mount_id"].encode("ascii")).hexdigest() ==
            evidence["selected_mount_id_sha256"], "diagnostic selected ID digest mismatch")


def diagnostic_fd_join(facts, evidence, rows, parsed):
    fdinfo = facts["shm_fdinfo"]
    require(type(fdinfo) is str and fdinfo.isascii() and len(fdinfo) <= 1024,
            "diagnostic fdinfo bound/type")
    ids = [line.split(":", 1)[1].strip() for line in fdinfo.splitlines()
           if line.startswith("mnt_id:")]
    require(len(ids) == 1 and re.fullmatch(r"[0-9]{1,20}", ids[0]) is not None and
            evidence["opened_fd_mount_id"] == ids[0], "diagnostic opened FD ID mismatch")
    matches = [i for i, item in enumerate(parsed) if item["mount_id"] == ids[0]]
    require(len(matches) == 1, "diagnostic opened FD ID missing/ambiguous among complete candidates")
    selected = matches[0]
    return dict(opened_fd_mount_id=ids[0], retained_line_index=rows[selected]["line_index"],
                retained_row=parsed[selected], selected_matches_opened=
                evidence["selected_line_index"] == rows[selected]["line_index"])


def diagnostic_optional(streams, facts):
    name = "tmp/private-ipc-probe.json"
    if name not in streams:
        return "ABSENT"
    optional = diagnostic_json(streams[name], 8192)
    left = json.dumps(optional, sort_keys=True, allow_nan=False, separators=(",", ":"))
    right = json.dumps(facts, sort_keys=True, allow_nan=False, separators=(",", ":"))
    return "IDENTICAL" if left == right else "DIFFERENT"


def diagnostic_summary(tool):
    valid = type(tool) is dict
    code = tool.get("exit_code") if valid else None
    code = code if type(code) is int and -(2**31) <= code < 2**31 else "MALFORMED_OR_ABSENT"
    stop = tool.get("stop") if valid else "MALFORMED_OR_ABSENT"
    stop = stop if stop is None or type(stop) is str and len(stop) <= 256 else "MALFORMED"
    return dict(schema="worldline.private-ipc-mount-diagnostic.v1", interpretation="UNPROVEN",
                candidate_digest_verified=False, fd_join="UNPROVEN", tool_exit=code,
                tool_stop=stop, terminal_tool_failure=code != 0 or stop is not None,
                optional_result="NOT_CHECKED", mechanism_qualified=False,
                proof_credit=False, phase_acceptance=False)


def diagnostic_text(facts, name, limit):
    value = facts.get(name)
    require(value is None or type(value) is str and len(value) <= limit,
            "diagnostic copied field type/length: " + name)
    return value


def mount_diagnostic(base, complete, tool):
    summary = diagnostic_summary(tool)
    try:
        files, archive = diagnostic_archive(base, complete, tool)
        streams = diagnostic_scan(base, files, archive)
        raw = streams["tool.stdout"]
        facts = diagnostic_json(raw, 8193)
        require(len(raw.rstrip(b"\n")) <= 8192, "diagnostic compact stdout bound")
        require(facts["schema"] == "worldline.private-ipc-probe.v1" and
                facts["mode"] == "normal" and facts["status"] in ("PASSED", "FAILED"),
                "diagnostic nominal report identity")
        summary.update(stdout_sha256=hashlib.sha256(raw).hexdigest(),
                       stdout_status=facts["status"], stdout_stage=diagnostic_text(facts, "stage", 128),
                       stdout_error=diagnostic_text(facts, "error", 512),
                       optional_result=diagnostic_optional(streams, facts))
        evidence = facts["mount_evidence"]
        rows, parsed = diagnostic_rows(evidence)
        summary.update(candidate_count=evidence["candidate_count"],
                       retained_rows=evidence["retained_rows"],
                       candidate_digest_declared=evidence["candidate_lines_joined_LF_sha256"])
        diagnostic_complete(facts, evidence, rows, parsed)
        summary["candidate_digest_verified"] = True
        summary["fd_join"] = diagnostic_fd_join(facts, evidence, rows, parsed)
        require(summary["optional_result"] != "DIFFERENT", "diagnostic result/stdout disagreement")
        summary["interpretation"] = "UNIQUE_RETAINED_FD_JOIN_ONLY_NOT_QUALIFICATION"
    except Exception as error:
        summary["error_type"] = type(error).__name__
        summary["error"] = str(error)[:512]
    if len(json.dumps(summary, sort_keys=True).encode("ascii")) > 8192:
        summary = diagnostic_summary(tool)
        summary["error"] = "diagnostic summary byte bound: mandatory fields not copied"
    return summary


def diagnostic_write(base, complete, tool):
    name = "mount-diagnostic-check.json"
    try:
        try:
            summary = mount_diagnostic(base, complete, tool)
        except Exception as error:
            summary = diagnostic_summary(tool)
            summary["error"] = "diagnostic containment: " + type(error).__name__[:128]
        save(base / name, summary)
        return dict(path=name, written=True, interpretation=summary["interpretation"])
    except Exception as error:
        # Optional diagnostic failure cannot skip the mandatory parent result attempt.
        return dict(path=name, written=False, interpretation="UNPROVEN",
                    error_type=type(error).__name__[:128], qualification=False)


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--cap-controls":
        sys.exit(cap_controls())
    if len(sys.argv) == 4 and sys.argv[1] == "--inside" and sys.argv[2] in MODES:
        sys.exit(inside(Path(sys.argv[3]), sys.argv[2]))
    if len(sys.argv) == 2 and sys.argv[1] in MODES:
        sys.exit(parent(sys.argv[1]))
    raise SystemExit("expected one fixed v4 mode")
