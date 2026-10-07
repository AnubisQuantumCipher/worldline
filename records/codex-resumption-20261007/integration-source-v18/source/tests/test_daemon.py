from __future__ import annotations

import asyncio
from pathlib import Path
import stat
import tempfile
import unittest

from worldline.client import DaemonClient
from worldline.core import Core
from worldline.daemon import WorldlineDaemon
from worldline.paths import WorldlinePaths
from worldline.status import StatusPublisher
from worldline.store import StateStore


class DaemonTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-daemon-")
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
        self.store = StateStore(self.paths, Core.shared())
        self.publisher = StatusPublisher(self.paths, self.store, lambda: {"overlay": {"state": "UNASSESSED"}})
        self.daemon = WorldlineDaemon(self.paths, self.store, self.publisher)
        await self.daemon.start()

    async def asyncTearDown(self) -> None:
        await self.daemon.stop()
        self.store.close()
        self.temporary.cleanup()

    async def test_owner_socket_and_terminal_schema(self) -> None:
        self.assertEqual(stat.S_IMODE(self.paths.socket.stat().st_mode), 0o600)
        client = DaemonClient(self.paths)
        ping = await asyncio.to_thread(client.request, "ping")
        self.assertIn("version", ping)
        status = await asyncio.to_thread(client.request, "status")
        self.assertEqual(
            set(status),
            {
                "schemaVersion", "daemon", "prime", "activeWorld", "worlds", "jobs",
                "capabilities", "lastReceipt", "ghostRecommendation",
            },
        )
        self.assertIsNone(status["prime"])


class StorageErrorNaming(unittest.TestCase):
    def test_disk_full_and_other_os_errors_are_named_not_internal(self) -> None:
        import errno
        import sqlite3

        from worldline.daemon import storage_error

        full = storage_error(OSError(errno.ENOSPC, "No space left on device", "/store/x"))
        self.assertEqual(full.code, "DISK_FULL")
        self.assertEqual(full.details, {"errno": "ENOSPC", "path": "/store/x"})
        self.assertIn("No space left on device: /store/x", full.message)
        quota = storage_error(OSError(errno.EDQUOT, "Disk quota exceeded"))
        self.assertEqual(quota.code, "DISK_FULL")
        self.assertEqual(quota.details, {"errno": "EDQUOT"})
        other = storage_error(OSError(errno.EIO, "Input/output error", b"/bytes/path"))
        self.assertEqual(other.code, "STORAGE_ERROR")
        self.assertEqual(other.details["path"], "/bytes/path")
        db_full = storage_error(sqlite3.OperationalError("database or disk is full"))
        self.assertEqual(db_full.code, "DISK_FULL")
        db_other = storage_error(sqlite3.OperationalError("database is locked"))
        self.assertEqual(db_other.code, "STORAGE_ERROR")
        self.assertEqual(db_other.details, {"backend": "sqlite"})


if __name__ == "__main__":
    unittest.main()
