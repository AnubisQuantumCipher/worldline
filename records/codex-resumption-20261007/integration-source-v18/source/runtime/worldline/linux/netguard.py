"""Per-world network containment.

A world normally shares the host network namespace: that is what lets an agent reach its model
provider, and it is exactly what the isolation claim never covered (SECURITY.md). With the
``allowlist`` policy the world gets an empty network namespace instead, plus one door: an HTTP
proxy the daemon runs on a Unix socket inside the world's runtime directory. Inside the world a
tiny forwarder listens on loopback and relays to that socket, and the agent is told to use it via
the proxy environment variables every CLI in use honours. The proxy connects only to hosts on the
allowlist (the adapter's provider hosts plus ``network.allow``); everything else is answered 403
and recorded, so a refusal is evidence rather than a silent failure.

The ``none`` policy is the same namespace without the door: useful for checks and for agents
that must not talk to anything.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path
import select
import socket
import socketserver
import sys
import threading
import time
from typing import Any, Iterable
from urllib.parse import urlsplit

from ..errors import WorldlineError

_MAX_HEADER = 64 * 1024
_RELAY_CHUNK = 65536

FORWARDER_PORT = 3128

# Runs inside the world (only /usr is visible there, so it is a self-contained script written into
# the runtime directory). Listens on loopback, relays every connection to the proxy socket, and
# runs the agent with the proxy environment set; the agent's exit code is the script's.
FORWARDER_SOURCE = r'''
import os, select, socket, subprocess, sys, threading

def relay(a, b):
    try:
        while True:
            r, _, _ = select.select([a, b], [], [], 30)
            if not r:
                continue
            for s in r:
                data = s.recv(65536)
                other = b if s is a else a
                if not data:
                    return
                other.sendall(data)
    except OSError:
        return
    finally:
        for s in (a, b):
            try:
                s.close()
            except OSError:
                pass

def serve(listener, socket_path):
    while True:
        try:
            client, _ = listener.accept()
        except OSError:
            return
        upstream = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            upstream.connect(socket_path)
        except OSError:
            client.close()
            continue
        threading.Thread(target=relay, args=(client, upstream), daemon=True).start()

def main():
    args = sys.argv[1:]
    socket_path = args[args.index("--socket") + 1]
    port = int(args[args.index("--port") + 1])
    argv = args[args.index("--") + 1:]
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(("127.0.0.1", port))
    listener.listen(64)
    threading.Thread(target=serve, args=(listener, socket_path), daemon=True).start()
    proxy = "http://127.0.0.1:%d" % port
    env = dict(os.environ)
    for name in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
        env[name] = proxy
    env["NO_PROXY"] = env["no_proxy"] = "127.0.0.1,localhost"
    env["NODE_USE_ENV_PROXY"] = "1"
    completed = subprocess.run(argv, env=env)
    sys.exit(completed.returncode)

main()
'''


def host_allowed(host: str, allowed: Iterable[str]) -> bool:
    candidate = host.lower().rstrip(".")
    for rule in allowed:
        pattern = rule.lower().rstrip(".")
        if pattern.startswith("."):
            if candidate == pattern[1:] or candidate.endswith(pattern):
                return True
        elif candidate == pattern:
            return True
    return False


@dataclass
class ProxyStats:
    allowed: int = 0
    refused: dict[tuple[str, int], int] = field(default_factory=dict)
    lock: threading.Lock = field(default_factory=threading.Lock)

    def record_allowed(self) -> None:
        with self.lock:
            self.allowed += 1

    def record_refused(self, host: str, port: int) -> None:
        with self.lock:
            self.refused[(host, port)] = self.refused.get((host, port), 0) + 1

    def summary(self) -> dict[str, Any]:
        with self.lock:
            return {
                "connections": self.allowed,
                "refused": [
                    {"host": host, "port": port, "count": count}
                    for (host, port), count in sorted(self.refused.items())
                ],
            }


class _Handler(socketserver.BaseRequestHandler):
    server: "AllowlistProxy"

    def handle(self) -> None:  # noqa: C901 - one small state machine
        client: socket.socket = self.request
        client.settimeout(30)
        try:
            head = self._read_head(client)
        except OSError:
            return
        if head is None:
            return
        request_line, _, rest = head.partition(b"\r\n")
        parts = request_line.split(b" ")
        if len(parts) < 3:
            self._refuse(client, "malformed request")
            return
        method, target = parts[0].decode("ascii", "replace"), parts[1].decode("ascii", "replace")
        if method == "CONNECT":
            host, _, port_text = target.rpartition(":")
            try:
                port = int(port_text)
            except ValueError:
                self._refuse(client, "malformed CONNECT target")
                return
            if not host_allowed(host, self.server.allowed):
                self.server.stats.record_refused(host, port)
                self._refuse(client, f"host not allowed by the world's network policy: {host}")
                return
            try:
                upstream = socket.create_connection((host, port), timeout=20)
            except OSError as exc:
                client.sendall(b"HTTP/1.1 502 Bad Gateway\r\nContent-Length: 0\r\n\r\n")
                self.server.stats.record_refused(host, port)
                return
            if not self.server.own_socket(upstream):
                return
            try:
                self.server.stats.record_allowed()
                client.sendall(b"HTTP/1.1 200 Connection established\r\n\r\n")
                self._relay(client, upstream)
            finally:
                from ..raw_observation import cleanup_call
                cleanup_call(lambda: self.server.release_socket(upstream))
            return
        # Plain HTTP through a proxy arrives with an absolute URI.
        split = urlsplit(target)
        if not split.scheme or not split.hostname:
            self._refuse(client, "proxy requests must carry an absolute URI")
            return
        host = split.hostname
        port = split.port or (443 if split.scheme == "https" else 80)
        if not host_allowed(host, self.server.allowed):
            self.server.stats.record_refused(host, port)
            self._refuse(client, f"host not allowed by the world's network policy: {host}")
            return
        try:
            upstream = socket.create_connection((host, port), timeout=20)
        except OSError:
            client.sendall(b"HTTP/1.1 502 Bad Gateway\r\nContent-Length: 0\r\n\r\n")
            self.server.stats.record_refused(host, port)
            return
        if not self.server.own_socket(upstream):
            return
        try:
            self.server.stats.record_allowed()
            path = split.path or "/"
            if split.query:
                path += "?" + split.query
            headers = [line for line in rest.split(b"\r\n") if line and not line.lower().startswith(b"proxy-")]
            rewritten = b" ".join((parts[0], path.encode("ascii", "replace"), parts[2])) + b"\r\n" + b"\r\n".join(headers) + b"\r\n\r\n"
            upstream.sendall(rewritten + self._body_prefix)
            self._relay(client, upstream)
        finally:
            from ..raw_observation import cleanup_call
            cleanup_call(lambda: self.server.release_socket(upstream))

    _body_prefix = b""

    def _read_head(self, client: socket.socket) -> bytes | None:
        buffer = b""
        while b"\r\n\r\n" not in buffer:
            chunk = client.recv(4096)
            if not chunk:
                return None
            buffer += chunk
            if len(buffer) > _MAX_HEADER:
                return None
        head, _, body = buffer.partition(b"\r\n\r\n")
        self._body_prefix = body
        return head

    @staticmethod
    def _refuse(client: socket.socket, reason: str) -> None:
        body = f"WORLDLINE network policy: {reason}\n".encode("utf-8")
        try:
            client.sendall(
                b"HTTP/1.1 403 Forbidden\r\nContent-Type: text/plain\r\nConnection: close\r\nContent-Length: "
                + str(len(body)).encode("ascii") + b"\r\n\r\n" + body
            )
        except OSError:
            pass

    @staticmethod
    def _relay(client: socket.socket, upstream: socket.socket) -> None:
        client.settimeout(None)
        upstream.settimeout(None)
        sockets = [client, upstream]
        try:
            while True:
                readable, _, _ = select.select(sockets, [], [], 60)
                if not readable:
                    continue
                for source in readable:
                    data = source.recv(_RELAY_CHUNK)
                    destination = upstream if source is client else client
                    if not data:
                        return
                    destination.sendall(data)
        except OSError:
            return
        finally:
            for item in sockets:
                try:
                    item.close()
                except OSError:
                    pass


class AllowlistProxy(socketserver.ThreadingUnixStreamServer):
    """CONNECT/absolute-URI proxy on a Unix socket that only reaches allowlisted hosts."""

    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, socket_path: Path, allowed: Iterable[str]) -> None:
        self.socket_path = Path(socket_path)
        self.allowed = tuple(sorted({item for item in allowed if item}))
        self.stats = ProxyStats()
        self._owned_lock = threading.RLock()
        self._owned_threads: set[threading.Thread] = set()
        self._owned_sockets: set[socket.socket] = set()
        self._handler_errors: list[BaseException] = []
        self._stopping = False
        if self.socket_path.exists():
            self.socket_path.unlink()
        super().__init__(str(self.socket_path), _Handler)
        os.chmod(self.socket_path, 0o600)
        self._thread = threading.Thread(target=self.serve_forever, name="worldline-netguard", daemon=True)

    def start(self) -> None:
        self._thread.start()

    def own_socket(self, stream: socket.socket) -> bool:
        with self._owned_lock:
            if not self._stopping:
                self._owned_sockets.add(stream)
                return True
        stream.close()
        return False

    def release_socket(self, stream: socket.socket) -> None:
        try:
            stream.close()
        finally:
            with self._owned_lock:
                if stream.fileno() == -1:
                    self._owned_sockets.discard(stream)

    def process_request(self, request, client_address):
        # Keep the original daemon status, but explicitly own these threads:
        # socketserver deliberately excludes daemon threads from server_close.
        with self._owned_lock:
            if self._stopping:
                self.shutdown_request(request)
                return
            self._owned_sockets.add(request)
            thread = threading.Thread(target=self._owned_request,
                                      args=(request, client_address), daemon=self.daemon_threads)
            self._owned_threads.add(thread)
            try:
                thread.start()
            except BaseException:
                self._owned_threads.discard(thread)
                from ..raw_observation import cleanup_call
                cleanup_call(lambda: self.release_socket(request))
                raise

    def _owned_request(self, request, client_address):
        try:
            try:
                self.process_request_thread(request, client_address)
            finally:
                # Keep the actual thread object until stop has observed its exit.
                # Removing it from inside its own finally would precede termination.
                from ..raw_observation import cleanup_call
                cleanup_call(lambda: self.release_socket(request))
        except BaseException as error:
            with self._owned_lock:
                self._handler_errors.append(error)
            raise

    def handle_error(self, request, client_address):
        error = sys.exception()
        if error is not None:
            with self._owned_lock:
                self._handler_errors.append(error)
        return super().handle_error(request, client_address)

    def quiescence_observation(self):
        from ..raw_observation import exception_observation
        with self._owned_lock:
            return {'stopping': self._stopping,
                'listenerAlive': self._thread.is_alive(),
                'handlers': [{'name': item.name, 'ident': item.ident,
                              'alive': item.is_alive()} for item in self._owned_threads],
                'sockets': [{'fileno': item.fileno()} for item in self._owned_sockets],
                'handlerErrors': [exception_observation(item) for item in self._handler_errors]}

    def quiescent(self) -> bool:
        with self._owned_lock:
            return (self._stopping and not self._thread.is_alive()
                    and all(not item.is_alive() for item in self._owned_threads)
                    and all(item.fileno() == -1 for item in self._owned_sockets))

    def stop(self) -> None:
        # This is a bounded teardown grace, not a new active connection timer.
        # A DNS/kernel/provider operation that does not end remains explicitly
        # owned and unclosed; it is not promoted to quiescent by this timeout.
        with self._owned_lock:
            self._stopping = True
        failure = None
        def attempt(action):
            nonlocal failure
            try:
                action()
            except BaseException as error:
                if failure is None:
                    failure = error
                elif error is not failure:
                    failure.add_note('owned proxy cleanup also failed: ' + repr(error))
        if self._thread.is_alive():
            attempt(self.shutdown)
        attempt(self.server_close)
        with self._owned_lock:
            streams = tuple(self._owned_sockets)
        for stream in streams:
            try:
                stream.shutdown(socket.SHUT_RDWR)
            except OSError:
                # Disconnected/already-closed sockets need no shutdown. Actual
                # close and handler termination below remain separate facts.
                pass
            attempt(lambda stream=stream: self.release_socket(stream))
        deadline = time.monotonic() + 5
        with self._owned_lock:
            threads = tuple(self._owned_threads)
        for thread in threads:
            attempt(lambda thread=thread: thread.join(timeout=max(0, deadline - time.monotonic())))
        if self._thread.ident is not None:
            attempt(lambda: self._thread.join(timeout=max(0, deadline - time.monotonic())))
        try:
            self.socket_path.unlink()
        except OSError:
            pass
        if not self.quiescent():
            error = WorldlineError('AGENT_PROXY_NOT_QUIESCENT',
                'owned proxy work remains live after bounded teardown', self.quiescence_observation())
            if failure is None:
                failure = error
            else:
                failure.add_note(str(error))
        if failure is not None:
            raise failure

    def summary(self) -> dict[str, Any]:
        return {"policy": "allowlist", "allowed": list(self.allowed), **self.stats.summary()}


def write_forwarder(runtime: Path) -> Path:
    path = runtime / "netguard.py"
    path.write_text(FORWARDER_SOURCE, encoding="utf-8")
    os.chmod(path, 0o600)
    return path
