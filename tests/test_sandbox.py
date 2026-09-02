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


if __name__ == "__main__":
    unittest.main()
