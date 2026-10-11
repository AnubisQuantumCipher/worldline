#!/usr/bin/env python3
"""Root supervisor that seals one installed WORLDLINE lab daemon socket."""

from __future__ import annotations

import sys
_approved = sys.modules.get('_worldline_approved_source_loader')
if _approved is None:
    raise RuntimeError('AUTHORITY_SHARED_EARLY_SOURCE_REQUIRED')
_source_lease = _approved.current()
if type(_source_lease) is not _approved.ApprovedSourceLease:
    raise RuntimeError('AUTHORITY_SHARED_ACTUAL_SOURCE_LEASE_REQUIRED')
_source_lease.check()
_source_lease.file(__file__, ('SOURCE',))

import argparse
import fcntl
from hashlib import sha256
import json
import os
from pathlib import Path
import secrets
import signal
import socket
import stat
import subprocess
import sys
import threading
import time
import uuid

from daemon_endpoint import (EndpointRefusal, check_entry, check_process, read_seal,
                             peer_credentials, process_identity, protected_directory,
                             require)


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def fsync_directory(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def publish(path: Path, record: dict) -> None:
    temporary = path.parent / (".daemon-seal." + secrets.token_hex(12))
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, "wb") as output:
            output.write(canonical(record) + b"\n")
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
        fsync_directory(path.parent)
    finally:
        temporary.unlink(missing_ok=True)


def ping(connection: socket.socket) -> int:
    request_id = str(uuid.uuid4())
    connection.sendall(canonical({"id": request_id, "op": "ping", "args": {}}) + b"\n")
    with connection.makefile("rb") as reader:
        raw = reader.readline()
    require(bool(raw), "DAEMON_HANDOFF_PING_DISCONNECTED")
    response = json.loads(raw)
    require(response.get("id") == request_id and response.get("ok") is True,
            "DAEMON_HANDOFF_PING_REFUSED")
    # Returned PID is a consistency check only; the kernel peer is the identity.
    return response["result"]["pid"]


def connect_checked(path: Path, child: subprocess.Popen[bytes], uid: int,
                    gid: int, start_ticks: int) -> tuple[socket.socket, os.stat_result]:
    entry = path.lstat()
    require(stat.S_ISSOCK(entry.st_mode) and entry.st_uid == uid and
            entry.st_gid == gid and stat.S_IMODE(entry.st_mode) == 0o600,
            "DAEMON_HANDOFF_SOCKET_UNTRUSTED")
    connection = socket.socket(socket.AF_UNIX)
    connection.settimeout(5)
    try:
        connection.connect(str(path))
        require(peer_credentials(connection) == (child.pid, uid, gid),
                "DAEMON_HANDOFF_PEER_MISMATCH")
        parent, current_start, state = process_identity(child.pid)
        require(parent == os.getpid() and current_start == start_ticks and
                state not in ("Z", "X"), "DAEMON_HANDOFF_PROCESS_CHANGED")
        current = path.lstat()
        require((current.st_dev, current.st_ino) == (entry.st_dev, entry.st_ino),
                "DAEMON_HANDOFF_SOCKET_CHANGED")
        return connection, entry
    except Exception:
        connection.close()
        raise


def daemon_environment(root: Path, lease_fd: int) -> dict[str, str]:
    install = root / "install"
    store = root / "daemon"
    return {
        "PATH": "/usr/bin:/bin", "HOME": str(root / "daemon-home"),
        "XDG_DATA_HOME": str(store / "data"),
        "XDG_STATE_HOME": str(store / "state"),
        "XDG_CONFIG_HOME": str(store / "config"),
        "XDG_RUNTIME_DIR": str(store / "runtime"),
        "PYTHONPATH": str(install / "runtime"),
        "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1",
        "WORLDLINE_CORE_LIB": str(install / "lib/libworldline_core.so"),
        "WORLDLINE_PROTECTED_SERVICE": str(install / "bin/worldline-protected-service"),
        "WORLDLINE_PROTECTED_ROOT": str(install / "bin/worldline-protected-root"),
        "WORLDLINE_PROTECTED_REGISTER": str(install / "bin/worldline-protected-register"),
        "WORLDLINE_AUTHORITY_V1": "1",
        "WORLDLINE_AUTHORITY_SOCKET": str(root / "authority/authority.sock"),
        "WORLDLINE_MANAGED_LOCK_FD": str(lease_fd),
    }


def selected_daemon_environment(root: Path, lease_fd: int, config: dict) -> dict[str, str]:
    environment = daemon_environment(root, lease_fd)
    if "shared_source_binding" not in config:
        return environment
    from worldline.protected_shared_source import from_path
    shared = from_path(config["shared_source_binding"], mutable_root=root)
    require(Path(__file__).resolve(strict=True) ==
            shared.root / "protected-authority/daemon_supervisor.py" and
            Path(config["worldline_library"]) == shared.library and
            config["worldline_library_sha256"] ==
            shared.inventory[shared.library.relative_to(shared.root).as_posix()]["sha256"] and
            Path(config["daemon_source_path"]) == shared.root / "runtime/worldline/daemon.py" and
            config["daemon_source_sha256"] == shared.inventory["runtime/worldline/daemon.py"]["sha256"],
            "SHARED_SUPERVISOR_NATIVE_DAEMON_SOURCE_SPLIT")
    _source_lease.directory_or_absent(str(shared.root / "runtime"))
    shared.check()
    _source_lease.check()
    environment["PYTHONPATH"] = str(shared.root / "runtime")
    environment["WORLDLINE_CORE_LIB"] = str(shared.library)
    return environment


def checked_config(root: Path) -> dict:
    require(os.geteuid() == 0 and root.parent == Path("/srv") and
            root.name.startswith("cosmogony-canonical-v1."),
            "DAEMON_SUPERVISOR_LAB_ROOT_REQUIRED")
    protected_directory(root)
    path = root / "authority/config.json"
    info = path.lstat()
    require(stat.S_ISREG(info.st_mode) and info.st_uid == 0 and
            stat.S_IMODE(info.st_mode) == 0o600,
            "DAEMON_SUPERVISOR_CONFIG_UNTRUSTED")
    config = json.loads(path.read_text())
    require(config["daemon_socket"] ==
            str(root / "authority/daemon-endpoint/worldlined.sock") and
            config["daemon_seal_record"] ==
            str(root / "authority/state/daemon-endpoint.json"),
            "DAEMON_SUPERVISOR_CONFIG_PATH")
    protected_directory(Path(config["daemon_socket"]).parent)
    protected_directory(Path(config["daemon_seal_record"]).parent)
    return config


def hold_broker_quiescence(root: Path) -> int:
    lock_path = root / "authority/state/broker.lock"
    fd = os.open(lock_path, os.O_RDWR | os.O_CREAT | os.O_CLOEXEC | os.O_NOFOLLOW,
                 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        os.close(fd)
        raise EndpointRefusal("DAEMON_RESEAL_BROKER_NOT_QUIESCED") from exc
    return fd


def temporary_refusal_listener(path: Path) -> tuple[socket.socket, threading.Event,
                                                   threading.Thread, tuple[int, int]]:
    require(not path.exists(), "DAEMON_HANDOFF_AUTHORITY_SOCKET_PRESENT")
    listener = socket.socket(socket.AF_UNIX)
    try:
        listener.bind(str(path))
        os.chmod(path, 0o666)
        listener.listen(8)
        listener.settimeout(0.2)
        info = path.lstat()
        stop = threading.Event()

        def refuse() -> None:
            while not stop.is_set():
                try:
                    connection, _ = listener.accept()
                except socket.timeout:
                    continue
                except OSError:
                    break
                with connection:
                    connection.settimeout(1)
                    try:
                        connection.recv(65536)
                        connection.sendall(canonical({"state": "REFUSED",
                                                      "code": "AUTHORITY_NOT_ACTIVE"}) + b"\n")
                    except OSError:
                        pass

        thread = threading.Thread(target=refuse, name="temporary-authority-refusal",
                                  daemon=True)
        thread.start()
        return listener, stop, thread, (info.st_dev, info.st_ino)
    except BaseException:
        listener.close()
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        raise


def close_refusal_listener(path: Path, listener: socket.socket,
                           stop: threading.Event, thread: threading.Thread,
                           identity: tuple[int, int]) -> None:
    stop.set()
    listener.close()
    thread.join(timeout=2)
    try:
        info = path.lstat()
    except FileNotFoundError:
        return
    require((info.st_dev, info.st_ino) == identity and info.st_uid == 0 and
            stat.S_ISSOCK(info.st_mode), "DAEMON_HANDOFF_AUTHORITY_SOCKET_CHANGED")
    path.unlink()
    fsync_directory(path.parent)


def cleanup_stale(root: Path, config: dict) -> None:
    record_path = Path(config["daemon_seal_record"])
    endpoint = Path(config["daemon_socket"])
    broker_guard = hold_broker_quiescence(root)
    try:
        require(not (root / "authority/authority.sock").exists(),
                "DAEMON_RESEAL_BROKER_SOCKET_PRESENT")
        if not record_path.exists():
            require(not endpoint.exists(), "DAEMON_RESEAL_UNRECORDED_ENDPOINT")
            return
        info = record_path.lstat()
        require(stat.S_ISREG(info.st_mode) and info.st_uid == 0 and
                stat.S_IMODE(info.st_mode) == 0o600,
                "DAEMON_RESEAL_RECORD_UNTRUSTED")
        record = json.loads(record_path.read_text())
        for name, ticks in (("pid", "start_ticks"),
                            ("supervisor_pid", "supervisor_start_ticks")):
            try:
                _, current_ticks, state = process_identity(record[name])
            except EndpointRefusal:
                continue
            require(current_ticks != record[ticks] or state in ("Z", "X"),
                    "DAEMON_RESEAL_OLD_PROCESS_ALIVE")
        if endpoint.exists():
            check_entry(config, record)
            endpoint.unlink()
            fsync_directory(endpoint.parent)
        record_path.unlink()
        fsync_directory(record_path.parent)
    finally:
        os.close(broker_guard)


def clear_stale_broker_socket(root: Path) -> None:
    guard = hold_broker_quiescence(root)
    try:
        path = root / "authority/authority.sock"
        if path.exists():
            info = path.lstat()
            require(stat.S_ISSOCK(info.st_mode) and info.st_uid == 0 and
                    stat.S_IMODE(info.st_mode) == 0o666,
                    "BROKER_SOCKET_UNTRUSTED")
            path.unlink()
            fsync_directory(path.parent)
    finally:
        os.close(guard)


def stop_sealed(config: dict) -> dict:
    require(hasattr(os, "pidfd_open") and hasattr(signal, "pidfd_send_signal"),
            "DAEMON_STOP_PIDFD_REQUIRED")
    record = read_seal(config)
    pidfd = os.pidfd_open(record["pid"])
    try:
        check_entry(config, record)
        check_process(record)
        require(Path(f"/proc/{record['pid']}").stat().st_uid == record["uid"],
                "DAEMON_STOP_PRINCIPAL_CHANGED")
        signal.pidfd_send_signal(pidfd, signal.SIGTERM)
    finally:
        os.close(pidfd)
    path = Path(config["daemon_seal_record"])
    deadline = time.monotonic() + 10
    while path.exists() and time.monotonic() < deadline:
        time.sleep(0.05)
    require(not path.exists(), "DAEMON_STOP_SUPERVISOR_DID_NOT_CLEAN")
    return {"state": "STOPPED", "sealed_pid": record["pid"],
            "sealed_start_ticks": record["start_ticks"],
            "generation": record["generation"]}


def stop_bootstrap(root: Path, config: dict) -> dict:
    require(hasattr(os, "pidfd_open") and hasattr(signal, "pidfd_send_signal"),
            "DAEMON_STOP_PIDFD_REQUIRED")
    marker = root / "install/managed-realm.json"
    require(marker.lstat().st_uid == 0 and
            json.loads(marker.read_text()).get("phase") == "BOOTSTRAP",
            "DAEMON_BOOTSTRAP_PHASE_REQUIRED")
    path = root / "daemon/runtime/worldline/worldlined.sock"
    entry = path.lstat()
    require(stat.S_ISSOCK(entry.st_mode) and
            (entry.st_uid, entry.st_gid) ==
            (config["daemon_uid"], config["daemon_gid"]),
            "DAEMON_BOOTSTRAP_SOCKET_UNTRUSTED")
    with socket.socket(socket.AF_UNIX) as connection:
        connection.settimeout(3)
        connection.connect(str(path))
        pid, uid, gid = peer_credentials(connection)
    require((uid, gid) == (config["daemon_uid"], config["daemon_gid"]),
            "DAEMON_BOOTSTRAP_PEER_CHANGED")
    pidfd = os.pidfd_open(pid)
    try:
        _parent, started, state = process_identity(pid)
        argv = Path(f"/proc/{pid}/cmdline").read_bytes().split(b"\x00")
        require(state not in ("Z", "X") and
                Path(f"/proc/{pid}").stat().st_uid == uid and
                b"worldline.daemon_main" in argv,
                "DAEMON_BOOTSTRAP_PROCESS_CHANGED")
        signal.pidfd_send_signal(pidfd, signal.SIGTERM)
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            try:
                _, current, current_state = process_identity(pid)
            except EndpointRefusal:
                break
            if current != started or current_state in ("Z", "X"):
                break
            time.sleep(0.05)
        else:
            signal.pidfd_send_signal(pidfd, signal.SIGKILL)
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline:
                try:
                    _, current, current_state = process_identity(pid)
                except EndpointRefusal:
                    break
                if current != started or current_state in ("Z", "X"):
                    break
                time.sleep(0.05)
            else:
                raise EndpointRefusal("DAEMON_BOOTSTRAP_DID_NOT_EXIT")
    finally:
        os.close(pidfd)
    if path.exists():
        current = path.lstat()
        require((current.st_dev, current.st_ino) ==
                (entry.st_dev, entry.st_ino),
                "DAEMON_BOOTSTRAP_SOCKET_CHANGED")
        path.unlink()
        fsync_directory(path.parent)
    return {"state": "BOOTSTRAP_STOPPED", "daemon_pid": pid,
            "daemon_start_ticks": started}


def stop_broker(root: Path, config: dict) -> dict:
    require(hasattr(os, "pidfd_open") and hasattr(signal, "pidfd_send_signal"),
            "BROKER_STOP_PIDFD_REQUIRED")
    identity_path = root / "authority/state/broker-identity.json"
    info = identity_path.lstat()
    require(stat.S_ISREG(info.st_mode) and info.st_uid == 0 and
            stat.S_IMODE(info.st_mode) == 0o600,
            "BROKER_STOP_IDENTITY_UNTRUSTED")
    record = json.loads(identity_path.read_text())
    source = root / "install/authority_service.py"
    require(record.get("schema") == "cosmogony.authority-v1.broker-process" and
            record.get("service_source_sha256") == sha256(source.read_bytes()).hexdigest(),
            "BROKER_STOP_SOURCE_CHANGED")
    socket_path = root / "authority/authority.sock"
    before_socket: tuple[int, int] | None = None
    if socket_path.exists():
        socket_info = socket_path.lstat()
        require(stat.S_ISSOCK(socket_info.st_mode) and socket_info.st_uid == 0 and
                stat.S_IMODE(socket_info.st_mode) == 0o666,
                "BROKER_STOP_SOCKET_UNTRUSTED")
        before_socket = (socket_info.st_dev, socket_info.st_ino)
    try:
        pidfd = os.pidfd_open(record["pid"])
    except ProcessLookupError:
        pidfd = None
    if pidfd is not None:
        try:
            _parent, started, state = process_identity(record["pid"])
            argv = Path(f"/proc/{record['pid']}/cmdline").read_bytes().split(b"\x00")
            require(started == record["start_ticks"] and state not in ("Z", "X") and
                    Path(f"/proc/{record['pid']}").stat().st_uid == 0 and
                    str(source).encode() in argv,
                    "BROKER_STOP_PROCESS_CHANGED")
            if Path(config["daemon_seal_record"]).exists():
                seal = read_seal(config)
                require(record.get("endpoint_generation") == seal["generation"],
                        "BROKER_STOP_GENERATION_CHANGED")
            signal.pidfd_send_signal(pidfd, signal.SIGTERM)
        finally:
            os.close(pidfd)
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        try:
            guard = hold_broker_quiescence(root)
        except EndpointRefusal:
            time.sleep(0.05)
            continue
        break
    else:
        raise EndpointRefusal("BROKER_STOP_LOCK_HELD")
    try:
        if socket_path.exists():
            after = socket_path.lstat()
            require(before_socket is not None and
                    (after.st_dev, after.st_ino) == before_socket and
                    stat.S_ISSOCK(after.st_mode) and after.st_uid == 0,
                    "BROKER_STOP_SOCKET_CHANGED")
            socket_path.unlink()
            fsync_directory(socket_path.parent)
    finally:
        os.close(guard)
    return {"state": "BROKER_STOPPED", "broker_pid": record["pid"],
            "broker_start_ticks": record["start_ticks"]}


def supervise(root: Path, config: dict) -> None:
    def terminating(_signum: int, _frame: object) -> None:
        raise SystemExit("DAEMON_SUPERVISOR_STOPPED")

    signal.signal(signal.SIGTERM, terminating)
    signal.signal(signal.SIGINT, terminating)
    broker_guard = hold_broker_quiescence(root)
    endpoint = Path(config["daemon_socket"])
    record_path = Path(config["daemon_seal_record"])
    bootstrap = root / "daemon/runtime/worldline/worldlined.sock"
    require(not endpoint.exists() and not record_path.exists(),
            "DAEMON_ENDPOINT_ALREADY_SEALED")
    lock_path = record_path.parent / "daemon-supervisor.lock"
    lock = os.open(lock_path, os.O_RDWR | os.O_CREAT | os.O_CLOEXEC | os.O_NOFOLLOW,
                   0o600)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BaseException:
        os.close(lock)
        os.close(broker_guard)
        raise
    lock_info = os.fstat(lock)
    require(stat.S_ISREG(lock_info.st_mode) and lock_info.st_uid == 0 and
            stat.S_IMODE(lock_info.st_mode) == 0o600 and lock_info.st_nlink == 1 and
            (lock_info.st_dev, lock_info.st_ino) ==
            (lock_path.lstat().st_dev, lock_path.lstat().st_ino),
            "DAEMON_SUPERVISOR_LEASE_UNTRUSTED")
    authority_socket = root / "authority/authority.sock"
    try:
        listener, refusal_stop, refusal_thread, refusal_identity = temporary_refusal_listener(
            authority_socket)
    except BaseException:
        os.close(lock)
        os.close(broker_guard)
        raise
    refusal_closed = False
    daemon_uid = config["daemon_uid"]
    daemon_gid = config["daemon_gid"]
    install = root / "install"
    try:
        child = subprocess.Popen(
            ["/usr/bin/python3", "-P", "-m", "worldline.daemon_main"],
            cwd=install, env=selected_daemon_environment(root, lock, config),
            pass_fds=(lock,), stdin=subprocess.DEVNULL,
            user=daemon_uid, group=daemon_gid, extra_groups=(),
            stdout=sys.stdout.buffer, stderr=sys.stderr.buffer)
    except BaseException:
        try:
            close_refusal_listener(authority_socket, listener, refusal_stop,
                                   refusal_thread, refusal_identity)
        finally:
            os.close(lock)
            os.close(broker_guard)
        raise
    pidfd = None
    moved_identity: tuple[int, int] | None = None
    try:
        if hasattr(os, "pidfd_open"):
            pidfd = os.pidfd_open(child.pid)
        parent, start_ticks, state = process_identity(child.pid)
        require(parent == os.getpid() and state not in ("Z", "X"),
                "DAEMON_SUPERVISOR_CHILD_CHANGED")
        deadline = time.monotonic() + 60
        while not bootstrap.exists():
            require(child.poll() is None, "DAEMON_SUPERVISOR_CHILD_EXITED")
            require(time.monotonic() < deadline, "DAEMON_SUPERVISOR_BIND_TIMEOUT")
            time.sleep(0.05)
        before, initial = connect_checked(bootstrap, child, daemon_uid,
                                          daemon_gid, start_ticks)
        before.close()
        # Review C9: like every other lab hook, honored only in a protected fault laboratory.
        if (config.get("fault_laboratory") is True and
                os.environ.get("COSMOGONY_TEST_PREHANDOFF_GATE") == "1"):
            # Isolated lab fault schedule. Keep the checked listener stationary
            # until the adversary has replaced its daemon-owned pathname.
            entered = root / "authority/state/test-prehandoff-entered"
            released = root / "authority/state/test-prehandoff-release"
            require(not entered.exists() and not released.exists(),
                    "DAEMON_TEST_PREHANDOFF_GATE_DIRTY")
            fd = os.open(entered, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                         os.O_NOFOLLOW, 0o600)
            try:
                os.write(fd, b"entered\n")
                os.fsync(fd)
            finally:
                os.close(fd)
            fsync_directory(entered.parent)
            deadline = time.monotonic() + 30
            while not released.exists():
                require(child.poll() is None,
                        "DAEMON_TEST_PREHANDOFF_CHILD_EXITED")
                require(time.monotonic() < deadline,
                        "DAEMON_TEST_PREHANDOFF_GATE_TIMEOUT")
                time.sleep(0.05)
        require(not endpoint.exists(), "DAEMON_ENDPOINT_ALREADY_SEALED")
        os.rename(bootstrap, endpoint)
        moved = endpoint.lstat()
        moved_identity = (moved.st_dev, moved.st_ino)
        fsync_directory(bootstrap.parent)
        fsync_directory(endpoint.parent)
        require((moved.st_dev, moved.st_ino) == (initial.st_dev, initial.st_ino),
                "DAEMON_HANDOFF_SOCKET_CHANGED")
        after, final = connect_checked(endpoint, child, daemon_uid,
                                       daemon_gid, start_ticks)
        try:
            require(ping(after) == child.pid, "DAEMON_HANDOFF_PING_PID_MISMATCH")
        finally:
            after.close()
        require((final.st_dev, final.st_ino) == (initial.st_dev, initial.st_ino),
                "DAEMON_HANDOFF_SOCKET_CHANGED")
        os.chown(endpoint, 0, 0)
        os.chmod(endpoint, 0o600)
        os.chmod(endpoint.parent, 0o700)
        fsync_directory(endpoint.parent)
        sealed_entry = endpoint.lstat()
        require((sealed_entry.st_dev, sealed_entry.st_ino) ==
                (initial.st_dev, initial.st_ino) and
                sealed_entry.st_uid == 0 and sealed_entry.st_gid == 0 and
                stat.S_IMODE(sealed_entry.st_mode) == 0o600,
                "DAEMON_HANDOFF_ROOT_OWNERSHIP_FAILED")
        _, supervisor_start, supervisor_state = process_identity(os.getpid())
        require(supervisor_state not in ("Z", "X"), "DAEMON_SUPERVISOR_CHANGED")
        record = {
            "schema": "cosmogony.authority-v1.daemon-endpoint-seal",
            "generation": secrets.token_hex(32), "socket": str(endpoint),
            "device": final.st_dev, "inode": final.st_ino,
            "pid": child.pid, "uid": daemon_uid, "gid": daemon_gid,
            "start_ticks": start_ticks,
            "supervisor_pid": os.getpid(),
            "supervisor_start_ticks": supervisor_start,
            "pidfd_held": pidfd is not None,
        }
        check_process(record)
        check_entry(config, record)
        with socket.socket(socket.AF_UNIX) as sealed_connection:
            sealed_connection.settimeout(5)
            sealed_connection.connect(str(endpoint))
            require(peer_credentials(sealed_connection) ==
                    (child.pid, daemon_uid, daemon_gid),
                    "DAEMON_HANDOFF_PEER_MISMATCH")
            require(ping(sealed_connection) == child.pid,
                    "DAEMON_HANDOFF_PING_PID_MISMATCH")
        close_refusal_listener(authority_socket, listener, refusal_stop,
                               refusal_thread, refusal_identity)
        refusal_closed = True
        publish(record_path, record)
        os.close(broker_guard)
        broker_guard = -1
        print(json.dumps({"state": "SEALED", **record}, sort_keys=True), flush=True)
        child.wait()
    finally:
        if broker_guard >= 0:
            os.close(broker_guard)
        if not refusal_closed:
            try:
                close_refusal_listener(authority_socket, listener, refusal_stop,
                                       refusal_thread, refusal_identity)
            except Exception as exc:
                print("DAEMON_HANDOFF_REFUSAL_CLEANUP_FAILED:" + str(exc),
                      file=sys.stderr, flush=True)
        try:
            if child.poll() is None:
                child.terminate()
                try:
                    child.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait()
        finally:
            try:
                if record_path.exists():
                    current = json.loads(record_path.read_text())
                    if (current.get("supervisor_pid") == os.getpid() and
                            current.get("pid") == child.pid):
                        if endpoint.exists():
                            entry = endpoint.lstat()
                            if ((entry.st_dev, entry.st_ino) ==
                                    (current["device"], current["inode"])):
                                endpoint.unlink()
                                fsync_directory(endpoint.parent)
                        record_path.unlink()
                        fsync_directory(record_path.parent)
                elif moved_identity is not None and endpoint.exists():
                    entry = endpoint.lstat()
                    if (entry.st_dev, entry.st_ino) == moved_identity:
                        endpoint.unlink()
                        fsync_directory(endpoint.parent)
            finally:
                if pidfd is not None:
                    os.close(pidfd)
                os.close(lock)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("action", choices=("start", "cleanup-stale",
                                           "clear-broker-socket", "stop-sealed",
                                           "stop-broker", "stop-bootstrap"))
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    config = checked_config(root)
    if args.action == "cleanup-stale":
        cleanup_stale(root, config)
        print(json.dumps({"state": "CLEANED", "root": str(root)}, sort_keys=True))
    elif args.action == "clear-broker-socket":
        clear_stale_broker_socket(root)
        print(json.dumps({"state": "BROKER_SOCKET_CLEARED",
                          "root": str(root)}, sort_keys=True))
    elif args.action == "stop-sealed":
        print(json.dumps(stop_sealed(config), sort_keys=True))
    elif args.action == "stop-bootstrap":
        print(json.dumps(stop_bootstrap(root, config), sort_keys=True))
    elif args.action == "stop-broker":
        print(json.dumps(stop_broker(root, config), sort_keys=True))
    else:
        supervise(root, config)


if __name__ == "__main__":
    main()
