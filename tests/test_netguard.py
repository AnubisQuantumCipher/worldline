from __future__ import annotations

from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import socket
import tempfile
import threading
import unittest

from worldline.linux.netguard import AllowlistProxy, host_allowed


class _Ok(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        body = b"ok:" + self.path.encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args) -> None:
        return


def _http(sock: socket.socket, request: bytes) -> bytes:
    sock.sendall(request)
    chunks = []
    while True:
        data = sock.recv(65536)
        if not data:
            break
        chunks.append(data)
        if b"\r\n\r\n" in b"".join(chunks):
            head, _, body = b"".join(chunks).partition(b"\r\n\r\n")
            for line in head.split(b"\r\n"):
                if line.lower().startswith(b"content-length:"):
                    if len(body) >= int(line.split(b":")[1]):
                        return b"".join(chunks)
    return b"".join(chunks)


class NetguardProxyTests(unittest.TestCase):
    def test_host_rules(self) -> None:
        self.assertTrue(host_allowed("api.anthropic.com", ("api.anthropic.com",)))
        self.assertTrue(host_allowed("o1.ingest.sentry.io", (".sentry.io",)))
        self.assertTrue(host_allowed("sentry.io", (".sentry.io",)))
        self.assertFalse(host_allowed("evil-sentry.io", (".sentry.io",)))
        self.assertFalse(host_allowed("api.anthropic.com.attacker.example", ("api.anthropic.com",)))
        self.assertTrue(host_allowed("API.OPENAI.COM.", ("api.openai.com",)))

    def test_proxy_forwards_allowed_hosts_and_refuses_others_with_a_record(self) -> None:
        server = HTTPServer(("127.0.0.1", 0), _Ok)
        port = server.server_address[1]
        threading.Thread(target=server.serve_forever, daemon=True).start()
        with tempfile.TemporaryDirectory(prefix="worldline-netguard-") as temporary:
            proxy = AllowlistProxy(Path(temporary) / "guard.sock", ("127.0.0.1",))
            proxy.start()
            try:
                # Plain HTTP through the proxy: absolute URI, allowed host.
                client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                client.connect(str(proxy.socket_path))
                reply = _http(client, f"GET http://127.0.0.1:{port}/hello HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n".encode())
                client.close()
                self.assertIn(b"200 OK", reply)
                self.assertTrue(reply.endswith(b"ok:/hello"))
                # CONNECT to an allowed host establishes a tunnel.
                client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                client.connect(str(proxy.socket_path))
                client.sendall(f"CONNECT 127.0.0.1:{port} HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n".encode())
                established = client.recv(1024)
                self.assertIn(b"200 Connection established", established)
                reply = _http(client, b"GET /tunnel HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n")
                client.close()
                self.assertTrue(reply.endswith(b"ok:/tunnel"))
                # A host outside the allowlist is refused by name and recorded.
                client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                client.connect(str(proxy.socket_path))
                reply = _http(client, b"CONNECT blocked.invalid:443 HTTP/1.1\r\nHost: blocked.invalid\r\n\r\n")
                client.close()
                self.assertIn(b"403 Forbidden", reply)
                self.assertIn(b"blocked.invalid", reply)
                summary = proxy.summary()
                self.assertEqual(summary["policy"], "allowlist")
                self.assertEqual(summary["connections"], 2)
                self.assertEqual(summary["refused"], [{"host": "blocked.invalid", "port": 443, "count": 1}])
            finally:
                proxy.stop()
                server.shutdown()
            self.assertFalse(proxy.socket_path.exists())


if __name__ == "__main__":
    unittest.main()
