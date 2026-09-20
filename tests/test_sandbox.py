from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
import uuid

from worldline.linux.namespaces import BubblewrapSandbox, SandboxSpec
from worldline.paths import WorldlinePaths


class SandboxTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-sandbox-")
        root = Path(self.temporary.name)
        env = {
            "HOME": str(root / "home"),
            "XDG_DATA_HOME": str(root / "data"),
            "XDG_STATE_HOME": str(root / "state"),
            "XDG_CONFIG_HOME": str(root / "config"),
            "XDG_RUNTIME_DIR": str(root / "runtime"),
        }
        for value in env.values():
            Path(value).mkdir(mode=0o700, parents=True, exist_ok=True)
        self.paths = WorldlinePaths.from_environment(env)
        self.paths.ensure()
        self.sandbox = BubblewrapSandbox(self.paths)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_managed_write_lands_only_in_upper_and_host_write_is_hidden(self) -> None:
        lower = Path(self.temporary.name) / "lower"
        lower.mkdir()
        (lower / "managed.txt").write_text("prime", encoding="utf-8")
        identifier = str(uuid.uuid4())
        target = Path(f"/tmp/worldline-managed-{identifier}")
        unregistered = Path(f"/tmp/worldline-unregistered-{identifier}")
        unregistered.unlink(missing_ok=True)
        roots = self.sandbox.overlay_roots(identifier, [("fixture", lower, target)])
        runtime = self.paths.overlays / identifier / "runtime"
        script = (
            "from pathlib import Path; "
            f"Path({str(target / 'managed.txt')!r}).write_text('candidate', encoding='utf-8'); "
            f"Path({str(unregistered)!r}).write_text('sandbox-only', encoding='utf-8')"
        )
        spec = SandboxSpec(
            instance_id=identifier,
            argv=("/usr/bin/python3", "-c", script),
            cwd=target,
            environment={"PATH": "/usr/bin"},
            roots=roots,
            runtime=runtime,
        )
        process = self.sandbox.launch_world(spec)
        stdout, stderr = process.process.communicate(timeout=15)
        self.assertEqual(process.process.returncode, 0, stderr.decode("utf-8", "replace"))
        self.assertEqual((lower / "managed.txt").read_text(encoding="utf-8"), "prime")
        self.assertEqual((roots[0].upper / "managed.txt").read_text(encoding="utf-8"), "candidate")
        self.assertFalse(unregistered.exists())

    def test_system_root_overlay_is_writable_only_in_future(self) -> None:
        identifier = str(uuid.uuid4())
        roots = self.sandbox.overlay_roots(
            identifier,
            [("system-usr", Path("/usr"), Path("/usr"))],
            allow_system_roots=True,
        )
        runtime = self.paths.overlays / identifier / "runtime"
        spec = SandboxSpec(
            instance_id=identifier,
            argv=("/usr/bin/test", "-x", "/usr/bin/pacman"),
            cwd=Path("/usr"),
            environment={"PATH": "/usr/bin"},
            roots=roots,
            runtime=runtime,
        )
        process = self.sandbox.launch_world(spec)
        _stdout, stderr = process.process.communicate(timeout=15)
        self.assertEqual(process.process.returncode, 0, stderr.decode("utf-8", "replace"))


    def test_argv_binds_resolver_directory_and_refuses_writable_host_credentials(self) -> None:
        from worldline.linux.namespaces import CredentialProjection
        from worldline.errors import WorldlineError

        identifier = str(uuid.uuid4())
        lower = Path(self.temporary.name) / "lower"
        lower.mkdir()
        target = Path(f"/tmp/worldline-managed-{identifier}")
        roots = self.sandbox.overlay_roots(identifier, [("fixture", lower, target)])
        runtime = self.paths.overlays / identifier / "runtime"
        host_secret = Path(self.temporary.name) / "secret.db"
        host_secret.write_bytes(b"host")
        home = Path(self.temporary.name) / "home"
        spec = SandboxSpec(
            instance_id=identifier, argv=("/usr/bin/true",), cwd=target, environment={"PATH": "/usr/bin"},
            roots=roots, runtime=runtime, operator_home=home,
            credential_mounts=(CredentialProjection(host_secret, home / ".x/secret.db", private_copy=True),),
        )
        with self.assertRaises(WorldlineError) as caught:
            self.sandbox.build_argv(spec)
        self.assertEqual(caught.exception.code, "INVALID_CREDENTIAL_PROJECTION")

        runtime.mkdir(parents=True, exist_ok=True)
        private = runtime / "private-credentials" / "0-secret.db"
        private.parent.mkdir(parents=True)
        private.write_bytes(b"copy")
        spec = SandboxSpec(
            instance_id=identifier, argv=("/usr/bin/true",), cwd=target, environment={"PATH": "/usr/bin"},
            roots=roots, runtime=runtime, operator_home=home,
            credential_mounts=(CredentialProjection(private, home / ".x/secret.db", private_copy=True),),
        )
        argv = self.sandbox.build_argv(spec)
        self.assertIn(("--bind", str(private), str(home / ".x/secret.db")), list(zip(argv, argv[1:], argv[2:])))
        resolv = Path("/etc/resolv.conf")
        if resolv.is_symlink() and resolv.resolve().is_relative_to("/run"):
            directory = str(resolv.resolve().parent)
            self.assertIn(("--ro-bind", directory, directory), list(zip(argv, argv[1:], argv[2:])))
            self.assertGreater(argv.index("--ro-bind", argv.index("/run") + 1), argv.index("--tmpfs"))

    def test_world_resolves_dns_names_like_the_host(self) -> None:
        import socket

        try:
            socket.getaddrinfo("api.anthropic.com", 443)
        except OSError:
            self.skipTest("host has no DNS")
        identifier = str(uuid.uuid4())
        lower = Path(self.temporary.name) / "lower"
        lower.mkdir()
        target = Path(f"/tmp/worldline-managed-{identifier}")
        roots = self.sandbox.overlay_roots(identifier, [("fixture", lower, target)])
        runtime = self.paths.overlays / identifier / "runtime"
        spec = SandboxSpec(
            instance_id=identifier,
            argv=("/usr/bin/python3", "-c", "import socket; socket.getaddrinfo('api.anthropic.com', 443)"),
            cwd=target, environment={"PATH": "/usr/bin"}, roots=roots, runtime=runtime,
        )
        process = self.sandbox.launch_world(spec)
        _stdout, stderr = process.process.communicate(timeout=30)
        self.assertEqual(process.process.returncode, 0, stderr.decode("utf-8", "replace"))


if __name__ == "__main__":
    unittest.main()
