"""Dedicated-account client mode: a daemon account serving listed client uids.

The root-owned service environment names one client group and the client uids. The socket,
the runtime directory and status.json then open to that group, and the daemon serves only its
own uid and the listed ones. Without that environment nothing changes (owner-only, 0600).
The client refuses a socket served by anyone but the expected daemon uid.
"""
from __future__ import annotations

import asyncio
import os
from pathlib import Path
import socket
import stat
import tempfile
import unittest
from unittest import mock

from worldline import cli_main
from worldline.canonical import atomic_write
from worldline.client import DaemonClient
from worldline.controller import RuntimeController
from worldline.core import Core
from worldline.daemon import WorldlineDaemon
from worldline.errors import WorldlineError
from worldline.paths import WorldlinePaths, secure_directory
from worldline.status import StatusPublisher
from worldline.store import StateStore


def environment(root: Path, **extra: str) -> dict[str, str]:
    env = {
        "HOME": str(root / "home"),
        "XDG_DATA_HOME": str(root / "data"),
        "XDG_STATE_HOME": str(root / "state"),
        "XDG_CONFIG_HOME": str(root / "config"),
        "XDG_RUNTIME_DIR": str(root / "runtime"),
        **extra,
    }
    for name in ("HOME", "XDG_DATA_HOME", "XDG_STATE_HOME", "XDG_CONFIG_HOME", "XDG_RUNTIME_DIR"):
        Path(env[name]).mkdir(mode=0o700, parents=True, exist_ok=True)
    return env


class ClientModeEnvironment(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-client-env-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def test_absent_means_owner_only(self) -> None:
        paths = WorldlinePaths.from_environment(environment(self.root))
        self.assertEqual((paths.client_gid, paths.client_uids, paths.daemon_uid), (None, (), None))

    def test_listed_group_uids_and_daemon_uid_parse(self) -> None:
        paths = WorldlinePaths.from_environment(environment(
            self.root, WORLDLINE_CLIENT_GID="970", WORLDLINE_CLIENT_UIDS="1000,1002",
            WORLDLINE_DAEMON_UID="969"))
        self.assertEqual((paths.client_gid, paths.client_uids, paths.daemon_uid),
                         (970, (1000, 1002), 969))

    def test_malformed_or_incomplete_client_mode_is_refused(self) -> None:
        for extra in ({"WORLDLINE_CLIENT_UIDS": "1000"},  # uids without their group
                      {"WORLDLINE_CLIENT_GID": "970,971"},
                      {"WORLDLINE_CLIENT_GID": "970", "WORLDLINE_CLIENT_UIDS": "1000,1000"},
                      {"WORLDLINE_CLIENT_GID": "970", "WORLDLINE_CLIENT_UIDS": "0"},
                      {"WORLDLINE_CLIENT_GID": "wheel"},
                      {"WORLDLINE_DAEMON_UID": "969,970"}):
            with self.subTest(extra=extra):
                with self.assertRaises(WorldlineError) as caught:
                    WorldlinePaths.from_environment(environment(self.root, **extra))
                self.assertEqual(caught.exception.code, "INVALID_CLIENT_MODE")

    def test_shared_runtime_directory_is_0750_for_its_group_and_status_is_0640(self) -> None:
        shared = self.root / "shared"
        secure_directory(shared, shared_gid=os.getgid())
        info = shared.stat()
        self.assertEqual((stat.S_IMODE(info.st_mode), info.st_gid), (0o750, os.getgid()))
        private = self.root / "private"
        private.mkdir(mode=0o755)
        secure_directory(private)
        self.assertEqual(stat.S_IMODE(private.stat().st_mode), 0o700)  # the default is unchanged
        status = shared / "status.json"
        atomic_write(status, b"{}", mode=0o640, group=os.getgid())
        info = status.stat()
        self.assertEqual((stat.S_IMODE(info.st_mode), info.st_gid), (0o640, os.getgid()))


class ClientModeDaemon(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-client-mode-")
        root = Path(self.temporary.name)
        self.other_uid = os.getuid() + 4242
        self.paths = WorldlinePaths.from_environment(environment(
            root, WORLDLINE_CLIENT_GID=str(os.getgid()),
            WORLDLINE_CLIENT_UIDS=str(self.other_uid)))
        self.store = StateStore(self.paths, Core.shared())
        self.publisher = StatusPublisher(self.paths, self.store, lambda: {})
        self.daemon = WorldlineDaemon(self.paths, self.store, self.publisher)
        await self.daemon.start()

    async def asyncTearDown(self) -> None:
        await self.daemon.stop()
        self.store.close()
        self.temporary.cleanup()

    async def test_socket_runtime_and_status_open_to_the_client_group_only(self) -> None:
        for path, mode in ((self.paths.socket, 0o660), (self.paths.runtime, 0o750),
                           (self.paths.status, 0o640)):
            with self.subTest(path=path.name):
                info = path.stat()
                self.assertEqual((stat.S_IMODE(info.st_mode), info.st_gid), (mode, os.getgid()))
        client = DaemonClient(self.paths)
        self.assertIn("version", await asyncio.to_thread(client.request, "ping"))

    async def test_listed_uid_is_served_and_an_unlisted_uid_is_refused(self) -> None:
        client = DaemonClient(self.paths)
        with mock.patch.object(WorldlineDaemon, "_peer_uid", return_value=self.other_uid):
            self.assertIn("version", await asyncio.to_thread(client.request, "ping"))
        with mock.patch.object(WorldlineDaemon, "_peer_uid", return_value=self.other_uid + 1):
            with self.assertRaises(WorldlineError) as caught:
                await asyncio.to_thread(client.request, "ping")
        self.assertEqual(caught.exception.code, "PEER_UID_MISMATCH")

    async def test_owner_only_operations_refuse_a_listed_client(self) -> None:
        self.daemon.register("probe.owner", lambda _args, _context: {"served": True}, owner_only=True)
        client = DaemonClient(self.paths)
        self.assertEqual(await asyncio.to_thread(client.request, "probe.owner"), {"served": True})
        with mock.patch.object(WorldlineDaemon, "_peer_uid", return_value=self.other_uid):
            self.assertIn("version", await asyncio.to_thread(client.request, "ping"))
            with self.assertRaises(WorldlineError) as caught:
                await asyncio.to_thread(client.request, "probe.owner")
        self.assertEqual(caught.exception.code, "OPERATION_NEEDS_DAEMON_ACCOUNT")

    async def test_client_refuses_a_daemon_that_is_not_the_expected_uid(self) -> None:
        # WORLDLINE_DAEMON_UID names the dedicated account; this daemon runs as the test user.
        expecting_other = WorldlinePaths(
            home=self.paths.home, data=self.paths.data, state=self.paths.state,
            runtime=self.paths.runtime, config=self.paths.config,
            daemon_uid=self.other_uid)
        with self.assertRaises(WorldlineError) as caught:
            await asyncio.to_thread(DaemonClient(expecting_other).request, "ping")
        self.assertEqual(caught.exception.code, "DAEMON_PEER_UNEXPECTED")


class OwnerOnlyRegistrations(unittest.TestCase):
    def test_exactly_the_root_set_changes_are_owner_only(self) -> None:
        # They move directories between the operator and the store, which a dedicated account
        # cannot do on a client's behalf. Everything else stays open to listed clients.
        recorded: dict[str, bool] = {}

        class Recorder:
            def register(self, name, _handler, *, mutating=False, owner_only=False):
                recorded[name] = owner_only

        RuntimeController.register(mock.Mock(), Recorder())
        self.assertEqual({name for name, owner in recorded.items() if owner},
                         {"init", "root.add", "root.remove"})
        self.assertIn("collapse.commit", recorded)


class ClientSideRefusals(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-client-side-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    @unittest.skipIf(os.geteuid() == 0, "root bypasses socket permission bits")
    def test_a_socket_outside_the_callers_group_is_access_denied(self) -> None:
        paths = WorldlinePaths.from_environment(environment(self.root))
        paths.runtime.mkdir(mode=0o700, parents=True, exist_ok=True)
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.addCleanup(server.close)
        server.bind(str(paths.socket))
        server.listen(1)
        paths.socket.chmod(0o000)
        with self.assertRaises(WorldlineError) as caught:
            DaemonClient(paths).request("ping")
        self.assertEqual(caught.exception.code, "DAEMON_ACCESS_DENIED")

    def test_shell_refuses_a_client_of_another_accounts_daemon(self) -> None:
        env = environment(self.root, WORLDLINE_DAEMON_UID=str(os.getuid() + 4242))
        client = mock.Mock(spec=DaemonClient)
        with mock.patch.dict(os.environ, env, clear=True):
            with self.assertRaises(WorldlineError) as caught:
                cli_main._shell(client, "alpha")
        self.assertEqual(caught.exception.code, "SHELL_UNAVAILABLE_TO_CLIENT")
        client.request.assert_not_called()


if __name__ == "__main__":
    unittest.main()
