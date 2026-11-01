"""UNRUN private-IPC diagnostic; execute only in the reviewed v4 namespace."""
import ctypes
import errno
import hashlib
import json
import os
import re
import signal
import socket
import stat
import sys

SCHEMA = "worldline.private-ipc-probe.v1"
LIBC = "/usr/lib/libc.so.6"
LIBC_SHA256 = "6ab264fb4e8df9942b0fb75b48fcd5c30b2f081d8dfaa6c25d7be1d3fce5b2ab"
WITNESS = b"private IPC witness\n"
MODES = ("normal", "alias-mismatch", "host-mismatch", "namespace-mismatch",
         "leftover-socket", "sigkill")
DIRECTORY = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
NEW_FILE = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC
MAX_RESULT = 8192


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def identity(info):
    return [info.st_dev, info.st_ino]


def validate_aliases(private, alias, host):
    require(private == alias, "alias mismatch")
    require(private != host, "host shm alias")


def validate_namespaces(ipc, mnt, parent_ipc, parent_mnt):
    for value, pattern in ((ipc, r"ipc:\[[0-9]+\]"),
                           (parent_ipc, r"ipc:\[[0-9]+\]"),
                           (mnt, r"mnt:\[[0-9]+\]"),
                           (parent_mnt, r"mnt:\[[0-9]+\]")):
        require(re.fullmatch(pattern, value) is not None, "invalid namespace ID")
    require(ipc != parent_ipc and mnt != parent_mnt, "namespace shared")


def bounded_env(name):
    value = os.environ.get(name, "")
    require(0 < len(value) <= 4096 and "\x00" not in value, "invalid " + name)
    return value


def config():
    token = bounded_env("PROBE_TOKEN")
    require(re.fullmatch("[0-9a-f]{32}", token) is not None, "invalid token")
    paths = {name: bounded_env(name) for name in
             ("PROBE_READONLY", "PROBE_RAM_IPC", "TMPDIR")}
    for value in paths.values():
        require(len(value) <= 1024 and value.startswith("/")
                and ".." not in value.split("/"), "bad path")
    numbers = [bounded_env("PROBE_HOST_SHM_" + name) for name in ("DEV", "INO")]
    require(all(re.fullmatch("[0-9]{1,20}", n) for n in numbers), "bad host identity")
    return dict(paths, token=token, host_identity=[int(n) for n in numbers],
                parent_ipc=bounded_env("PROBE_PARENT_IPC_NS"),
                parent_mnt=bounded_env("PROBE_PARENT_MOUNT_NS"))


def inject_control(cfg, mode, report):
    # Change only expected configuration; the collector's safe mounts stay intact.
    if mode == "alias-mismatch":
        cfg["PROBE_RAM_IPC"] = "/dev"
        report["injection"] = "expected alias changed to distinct private /dev"
    elif mode == "host-mismatch":
        cfg["host_identity"] = identity(os.stat("/dev/shm", follow_symlinks=False))
        report["injection"] = "expected host identity changed to private identity"
    elif mode == "namespace-mismatch":
        cfg["parent_ipc"] = os.readlink("/proc/self/ns/ipc")
        report["injection"] = "expected parent IPC changed to child IPC"


def read_limited(path, limit):
    with open(path, "rb") as stream:
        value = stream.read(limit + 1)
    require(len(value) <= limit, "OS evidence byte bound")
    return value.decode("ascii")


def mount_record(path, lines):
    chosen = None
    for line in lines:
        require(len(line) <= 2048, "mountinfo line bound")
        fields = line.split()
        require(len(fields) >= 10 and "-" in fields[6:], "bad mountinfo record")
        target = fields[4]
        if path == target or path.startswith(target.rstrip("/") + "/"):
            if chosen is None or len(target) > len(chosen["mountpoint"]):
                sep = fields.index("-", 6)
                require(len(fields) >= sep + 4, "short mountinfo filesystem")
                chosen = dict(mount_id=fields[0], device=fields[2], root=fields[3],
                              mountpoint=target, options=fields[5],
                              filesystem=fields[sep + 1], super_options=fields[sep + 3])
    require(chosen is not None, "mountinfo target absent")
    return chosen


def record_os_evidence(cfg, report):
    lines = read_limited("/proc/self/mountinfo", 65536).splitlines()
    require(len(lines) <= 512, "mountinfo entry bound")
    mounts = {name: mount_record(path, lines) for name, path in
              (("dev", "/dev"), ("shm", "/dev/shm"),
               ("alias", cfg["PROBE_RAM_IPC"]), ("tmp", cfg["TMPDIR"]))}
    require(mounts["dev"]["mountpoint"] == "/dev"
            and "ro" in mounts["dev"]["options"].split(","), "dev parent writable")
    require(mounts["shm"]["mountpoint"] == "/dev/shm"
            and "rw" in mounts["shm"]["options"].split(",")
            and mounts["shm"]["filesystem"] == "tmpfs", "private shm mount mismatch")
    require("ro" in mounts["alias"]["options"].split(","), "RAM alias writable")
    report.update(uid_map=read_limited("/proc/self/uid_map", 256),
                  gid_map=read_limited("/proc/self/gid_map", 256), mounts=mounts)


def open_context(cfg, context, report):
    ipc = os.readlink("/proc/self/ns/ipc")
    mnt = os.readlink("/proc/self/ns/mnt")
    report.update(ipc_namespace=ipc, mount_namespace=mnt, uid=os.getuid(),
                  euid=os.geteuid())
    validate_namespaces(ipc, mnt, cfg["parent_ipc"], cfg["parent_mnt"])
    for key, path in (("ipc", "/dev/shm"), ("alias", cfg["PROBE_RAM_IPC"]),
                      ("tmp", cfg["TMPDIR"])):
        context[key] = os.open(path, DIRECTORY)
    info = os.fstat(context["ipc"])
    report.update(private_identity=identity(info), host_identity=cfg["host_identity"])
    require(stat.S_ISDIR(info.st_mode) and stat.S_IMODE(info.st_mode) == 0o700,
            "private IPC directory mode")
    validate_aliases(identity(info), identity(os.fstat(context["alias"])),
                     cfg["host_identity"])
    require(os.fstat(context["tmp"]).st_dev == info.st_dev, "tmp outside RAM")
    require(info.st_uid == os.geteuid(), "IPC directory owner")
    fs = os.fstatvfs(context["ipc"])
    require(fs.f_blocks * fs.f_frsize == 33554432 and fs.f_files <= 1024,
            "existing RAM quota mismatch")
    report.update(output_bytes=33554432, output_inodes=fs.f_files)
    record_os_evidence(cfg, report)
    context["safe_result"] = True


def check_boundaries(cfg, report):
    denied = []
    for path in (cfg["PROBE_READONLY"] + "/forbidden-write", "/dev/forbidden-write"):
        try:
            fd = os.open(path, NEW_FILE, 0o600)
        except OSError as error:
            require(error.errno in (errno.EROFS, errno.ENOENT), "unexpected refusal")
            denied.append(dict(path=path, errno=error.errno))
        else:
            os.close(fd)
            raise RuntimeError("undeclared write succeeded; no deletion attempted")
    fd = os.open("/dev/null", os.O_WRONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        require(os.write(fd, b"device access works") == 19, "short devnull write")
    finally:
        os.close(fd)
    report["write_refusals"] = denied
    report["devnull_write_bytes"] = 19


def load_libc():
    require(ctypes.sizeof(ctypes.c_uint) == 4 and ctypes.sizeof(ctypes.c_int) == 4
            and ctypes.sizeof(ctypes.c_void_p) == 8, "unsupported C ABI")
    digest = hashlib.sha256()
    with open(LIBC, "rb") as stream:
        for _ in range(256):
            data = stream.read(65536)
            if not data:
                break
            digest.update(data)
        require(not stream.read(1), "libc hash size bound")
    require(digest.hexdigest() == LIBC_SHA256, "installed libc changed")
    lib = ctypes.CDLL(LIBC, use_errno=True)
    # sem_open is variadic: only its two fixed parameters belong in argtypes.
    lib.sem_open.argtypes = [ctypes.c_char_p, ctypes.c_int]
    lib.sem_open.restype = ctypes.c_void_p  # Installed glibc SEM_FAILED is NULL.
    lib.sem_trywait.argtypes = [ctypes.c_void_p]
    lib.sem_trywait.restype = ctypes.c_int
    lib.sem_post.argtypes = [ctypes.c_void_p]
    lib.sem_post.restype = ctypes.c_int
    lib.sem_close.argtypes = [ctypes.c_void_p]
    lib.sem_close.restype = ctypes.c_int
    lib.sem_unlink.argtypes = [ctypes.c_char_p]
    lib.sem_unlink.restype = ctypes.c_int
    return lib


def trywait(lib, handle, empty):
    ctypes.set_errno(0)
    result = lib.sem_trywait(handle)
    saved_errno = ctypes.get_errno()
    if empty:
        require(result == -1 and saved_errno == errno.EAGAIN,
                "sem_trywait expected EAGAIN: " + str((result, saved_errno)))
    else:
        require(result == 0, "sem_trywait failed: " + str((result, saved_errno)))


def semaphore(cfg, context, state, report):
    lib = load_libc()
    state.update(lib=lib, name=("/wl-ipc-" + cfg["token"]).encode("ascii"),
                 backing="sem.wl-ipc-" + cfg["token"])
    ctypes.set_errno(0)
    handle = lib.sem_open(state["name"], os.O_CREAT | os.O_EXCL,
                          ctypes.c_uint(0o600), ctypes.c_uint(0))
    saved_errno = ctypes.get_errno()
    require(handle is not None, "sem_open failed: errno=" + str(saved_errno))
    state["handle"] = handle
    state["created"] = True
    info = os.stat(state["backing"], dir_fd=context["ipc"], follow_symlinks=False)
    require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and info.st_size == 32
            and stat.S_IMODE(info.st_mode) == 0o600 and info.st_uid == os.geteuid(),
            "unexpected semaphore backing metadata")
    require(info.st_dev == os.fstat(context["ipc"]).st_dev, "backing filesystem")
    state["identity"] = identity(info)
    ctypes.set_errno(0)
    duplicate = lib.sem_open(state["name"], os.O_CREAT | os.O_EXCL,
                             ctypes.c_uint(0o600), ctypes.c_uint(0))
    saved_errno = ctypes.get_errno()
    if duplicate is not None:
        close_code = lib.sem_close(duplicate)
        close_errno = ctypes.get_errno()
        raise RuntimeError("exclusive reopen succeeded: close=" +
                           str((close_code, close_errno)))
    require(saved_errno == errno.EEXIST, "exclusive reopen did not report EEXIST")
    trywait(lib, handle, True)
    ctypes.set_errno(0)
    code = lib.sem_post(handle)
    saved_errno = ctypes.get_errno()
    require(code == 0, "sem_post failed: " + str((code, saved_errno)))
    trywait(lib, handle, False)
    trywait(lib, handle, True)
    report["semaphore"] = dict(name=state["name"].decode("ascii"),
                               backing=state["backing"], identity=state["identity"],
                               exclusive_reopen_errno=errno.EEXIST,
                               operations=["empty-EAGAIN", "post", "consume", "empty-EAGAIN"])


def close_semaphore(context, state, report):
    cleanup = dict(created=state.get("created", False), close="NOT_OWNED",
                   unlink="NOT_OWNED", errors=[])
    report["semaphore_cleanup"] = cleanup
    if not state.get("created"):
        report["semaphore_cleanup"] = cleanup
        return
    try:
        ctypes.set_errno(0)
        code = state["lib"].sem_close(state["handle"])
        saved_errno = ctypes.get_errno()
        cleanup["close"] = "OK" if code == 0 else "FAILED"
        require(code == 0, "sem_close errno=" + str(saved_errno))
    except Exception as error:
        cleanup["close"] = "FAILED"
        cleanup["errors"].append(str(error)[:512])
    # Unlink is attempted independently of close failure, but never without identity.
    try:
        info = os.stat(state["backing"], dir_fd=context["ipc"], follow_symlinks=False)
        require(state.get("identity") == identity(info) and stat.S_ISREG(info.st_mode)
                and info.st_nlink == 1 and info.st_uid == os.geteuid(),
                "owned semaphore identity changed; no unlink")
        ctypes.set_errno(0)
        code = state["lib"].sem_unlink(state["name"])
        saved_errno = ctypes.get_errno()
        require(code == 0, "sem_unlink errno=" + str(saved_errno))
        cleanup["unlink"] = "OK"
        try:
            os.stat(state["backing"], dir_fd=context["ipc"], follow_symlinks=False)
        except FileNotFoundError:
            cleanup["backing_absent"] = True
        else:
            raise RuntimeError("semaphore backing remains")
    except Exception as error:
        cleanup["unlink"] = "FAILED_OR_UNVERIFIED"
        cleanup["errors"].append(str(error)[:512])
    report["semaphore_cleanup"] = cleanup


def create_witness(cfg, context, report):
    name = "wl-ipc-" + cfg["token"] + ".witness"
    fd = os.open(name, NEW_FILE, 0o600, dir_fd=context["ipc"])
    try:
        require(os.write(fd, WITNESS) == len(WITNESS), "short witness write")
        os.fsync(fd)
        written = identity(os.fstat(fd))
    finally:
        os.close(fd)
    fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC,
                 dir_fd=context["alias"])
    try:
        require(identity(os.fstat(fd)) == written, "witness alias identity")
        require(os.read(fd, len(WITNESS) + 1) == WITNESS, "witness alias content")
    finally:
        os.close(fd)
    report["witness"] = dict(basename=name, bytes=len(WITNESS),
                             sha256=hashlib.sha256(WITNESS).hexdigest())


def leftover_socket(cfg, context, report):
    name = "leftover-" + cfg["token"] + ".sock"
    os.fchdir(context["tmp"])
    # Relative spelling avoids AF_UNIX's short pathname limit for this long carrier.
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.setblocking(False)
        sock.bind(name)
    info = os.stat(name, dir_fd=context["tmp"], follow_symlinks=False)
    require(stat.S_ISSOCK(info.st_mode), "socket fixture type mismatch")
    report["leftover_socket"] = dict(relative_path="tmp/" + name,
                                      identity=identity(info), closed=True,
                                      unlinked=False, expected_archive="NO_COMPLETE_ARCHIVE")


def save_result(context, report):
    data = (json.dumps(report, sort_keys=True, indent=2) + "\n").encode("ascii")
    require(len(data) <= MAX_RESULT, "result byte bound")
    fd = os.open("private-ipc-probe.json", NEW_FILE, 0o600, dir_fd=context["tmp"])
    try:
        require(os.write(fd, data) == len(data), "short result write")
        os.fsync(fd)
    finally:
        os.close(fd)


def success_status(mode):
    if mode == "leftover-socket":
        return "LEFTOVER_SOCKET_CONTROL"
    if mode == "sigkill":
        return "SIGKILL_PREPARED"
    return "PASSED"


def finish(context, state, report):
    close_semaphore(context, state, report)
    if report["semaphore_cleanup"]["errors"]:
        report["status"] = "FAILED"
    errors = []
    for name in ("alias", "ipc"):
        if name in context:
            try:
                os.close(context[name])
            except OSError as error:
                errors.append(name + " close errno=" + str(error.errno))
    report["directory_close_errors"] = errors
    if errors:
        report["status"] = "FAILED"
    try:
        if context.get("safe_result"):
            save_result(context, report)
    finally:
        if "tmp" in context:
            os.close(context["tmp"])


def main():
    report = dict(schema=SCHEMA, status="FAILED", stage="configuration",
                  phase_acceptance=False)
    context, state = {}, {}
    try:
        require(len(sys.argv) == 2 and sys.argv[1] in MODES, "invalid probe mode")
        mode = sys.argv[1]
        report["mode"] = mode
        cfg = config()
        inject_control(cfg, mode, report)
        report["stage"] = "private identity"
        open_context(cfg, context, report)
        require(mode not in ("alias-mismatch", "host-mismatch", "namespace-mismatch"),
                "negative admission unexpectedly succeeded")
        report["stage"] = "host write boundaries"
        check_boundaries(cfg, report)
        report["stage"] = "named semaphore"
        semaphore(cfg, context, state, report)
        report["stage"] = "regular witness"
        create_witness(cfg, context, report)
        if mode == "leftover-socket":
            report["stage"] = "leftover socket control"
            leftover_socket(cfg, context, report)
        report["stage"] = "completed"
        report["status"] = success_status(mode)
    except Exception as error:
        report.update(status="FAILED", error_type=type(error).__name__, error=str(error)[:512])
    finally:
        try:
            finish(context, state, report)
        except Exception as error:
            report.update(status="FAILED", finalization_error=str(error)[:512])
    rendered = json.dumps(report, sort_keys=True)
    if len(rendered.encode("ascii")) > MAX_RESULT:
        report["status"] = "FAILED"
        rendered = '{"schema":"' + SCHEMA + '","status":"FAILED","error":"stdout bound"}'
    print(rendered, flush=True)
    if report["status"] == "SIGKILL_PREPARED":
        os.kill(os.getpid(), signal.SIGKILL)
        return 2  # A return from deliberate self-kill cannot establish the control.
    return 0 if report["status"] in ("PASSED", "LEFTOVER_SOCKET_CONTROL") else 2


if __name__ == "__main__":
    sys.exit(main())
