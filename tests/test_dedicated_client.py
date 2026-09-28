"""Dedicated-account client mode: a daemon account serving listed client uids.

The root-owned service environment names one client group and the client uids. The socket,
the runtime directory and status.json then open to that group, and the daemon serves only its
own uid and the listed ones. Without that environment nothing changes (owner-only, 0600).
The client refuses a socket served by anyone but the expected daemon uid.
"""
from __future__ import annotations

import argparse
import asyncio
import os
from pathlib import Path
import socket
import stat
import subprocess
import tempfile
import unittest
from unittest import mock
import uuid

from worldline import cli_main, daemon_main
from worldline.admission import Ledger
from worldline.canonical import atomic_write
from worldline.client import DaemonClient
from worldline.controller import RuntimeController
from worldline.core import Core
from worldline.daemon import WorldlineDaemon
from worldline.errors import WorldlineError
from worldline.linux.docker import DockerAdapter
from worldline.linux.namespaces import BubblewrapSandbox, OverlayRoot, SandboxSpec
from worldline.paths import WorldlinePaths, secure_directory
from worldline.roots import RootManager
from worldline.status import StatusPublisher
from worldline.store import StateStore


# A supplementary group of this user: files are not created with it, so a test using it
# fails if the group change is missing. The primary group would pass either way.
SUPPLEMENTARY_GID = next((gid for gid in os.getgroups() if gid != os.getgid()), None)
needs_supplementary = unittest.skipIf(SUPPLEMENTARY_GID is None, "needs a supplementary group")


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
                      {"WORLDLINE_CLIENT_GID": "970"},  # a group without uids
                      {"WORLDLINE_CLIENT_GID": "970,971", "WORLDLINE_CLIENT_UIDS": "1000"},
                      {"WORLDLINE_CLIENT_GID": "970", "WORLDLINE_CLIENT_UIDS": "1000,1000"},
                      {"WORLDLINE_CLIENT_GID": "970", "WORLDLINE_CLIENT_UIDS": "0"},
                      {"WORLDLINE_CLIENT_GID": "970", "WORLDLINE_CLIENT_UIDS": "1000,"},
                      {"WORLDLINE_CLIENT_GID": " 970 ", "WORLDLINE_CLIENT_UIDS": "1000"},
                      {"WORLDLINE_CLIENT_GID": "9_70", "WORLDLINE_CLIENT_UIDS": "1000"},
                      {"WORLDLINE_CLIENT_GID": "\u0669\u0667\u0660", "WORLDLINE_CLIENT_UIDS": "1000"},
                      {"WORLDLINE_CLIENT_GID": "wheel", "WORLDLINE_CLIENT_UIDS": "1000"},
                      {"WORLDLINE_DAEMON_UID": "969,970"}):
            with self.subTest(extra=extra):
                with self.assertRaises(WorldlineError) as caught:
                    WorldlinePaths.from_environment(environment(self.root, **extra))
                self.assertEqual(caught.exception.code, "INVALID_CLIENT_MODE")

    def test_a_runtime_directory_inside_the_store_is_refused(self) -> None:
        env = environment(self.root, WORLDLINE_CLIENT_GID="970", WORLDLINE_CLIENT_UIDS="1000")
        env["XDG_RUNTIME_DIR"] = env["XDG_STATE_HOME"]
        with self.assertRaises(WorldlineError) as caught:
            WorldlinePaths.from_environment(env)
        self.assertEqual(caught.exception.code, "INVALID_CLIENT_MODE")

    @unittest.skipIf(os.geteuid() == 0, "root may join any group")
    def test_a_group_the_daemon_is_not_in_is_invalid_client_mode(self) -> None:
        outsider = next(gid for gid in range(60000, 65000) if gid not in os.getgroups())
        with self.assertRaises(WorldlineError) as caught:
            secure_directory(self.root / "shared", shared_gid=outsider)
        self.assertEqual(caught.exception.code, "INVALID_CLIENT_MODE")

    @needs_supplementary
    def test_shared_runtime_directory_is_0750_for_its_group_and_status_is_0640(self) -> None:
        shared = self.root / "shared"
        secure_directory(shared, shared_gid=SUPPLEMENTARY_GID)
        info = shared.stat()
        self.assertEqual((stat.S_IMODE(info.st_mode), info.st_gid), (0o750, SUPPLEMENTARY_GID))
        private = self.root / "private"
        private.mkdir(mode=0o755)
        secure_directory(private)
        self.assertEqual(stat.S_IMODE(private.stat().st_mode), 0o700)  # the default is unchanged
        status = shared / "status.json"
        atomic_write(status, b"{}", mode=0o640, group=SUPPLEMENTARY_GID)
        info = status.stat()
        self.assertEqual((stat.S_IMODE(info.st_mode), info.st_gid), (0o640, SUPPLEMENTARY_GID))


@needs_supplementary
class ClientModeDaemon(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-client-mode-")
        root = Path(self.temporary.name)
        self.other_uid = os.getuid() + 4242
        self.paths = WorldlinePaths.from_environment(environment(
            root, WORLDLINE_CLIENT_GID=str(SUPPLEMENTARY_GID),
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
                self.assertEqual((stat.S_IMODE(info.st_mode), info.st_gid), (mode, SUPPLEMENTARY_GID))
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
    def test_exactly_the_root_set_changes_and_switch_are_owner_only(self) -> None:
        # Root-set changes move directories between the operator and the store, which a
        # dedicated account cannot do on a client's behalf; switch drives the desktop and opens a
        # terminal as the daemon. Everything else stays open to listed clients.
        recorded: dict[str, bool] = {}

        class Recorder:
            def register(self, name, _handler, *, mutating=False, owner_only=False):
                recorded[name] = owner_only

        RuntimeController.register(mock.Mock(), Recorder())
        self.assertEqual({name for name, owner in recorded.items() if owner},
                         {"init", "root.add", "root.remove", "switch"})
        self.assertIn("collapse.commit", recorded)


class ReviewRepairs(unittest.TestCase):
    """Review of 9ddb7bb: m1 umask ordering, m5 docker timeouts, m6 relative roots, M1, M2."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-review-repairs-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def test_the_daemon_sets_its_umask_before_building_anything(self) -> None:
        observed: list[int] = []

        def record(coroutine):
            coroutine.close()
            current = os.umask(0o022)
            os.umask(current)
            observed.append(current)
            return 0

        previous = os.umask(0o022)
        try:
            with mock.patch("worldline.daemon_main.asyncio.run", side_effect=record):
                daemon_main.main([])
        finally:
            os.umask(previous)
        self.assertEqual(observed, [0o077])

    def test_admission_lock_and_ledger_are_owner_only_under_a_permissive_umask(self) -> None:
        previous = os.umask(0o022)
        try:
            ledger = Ledger(self.root / "runtime")
            with ledger.locked():
                ledger._store([])
        finally:
            os.umask(previous)
        for path in (ledger.lock_path, ledger.path):
            with self.subTest(path=path.name):
                self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)

    def test_every_docker_call_that_times_out_is_docker_unavailable(self) -> None:
        adapter = object.__new__(DockerAdapter)
        adapter.executable = "/usr/bin/docker"
        adapter.core = Core.shared()
        adapter.server_version = "fixture"
        timeout = subprocess.TimeoutExpired(["docker", "ps"], 15)
        with mock.patch("worldline.linux.docker.subprocess.run", side_effect=timeout):
            with self.assertRaises(WorldlineError) as caught:
                adapter.capture("0b9e6f4c-8a8e-4d5c-9f3e-2f1a5b7c9d10", world_roots={"r": self.root})
        self.assertEqual(caught.exception.code, "DOCKER_UNAVAILABLE")

    def test_root_paths_are_sent_absolute(self) -> None:
        client = mock.Mock()
        client.request.side_effect = WorldlineError("STOP", "stop here")
        arguments = argparse.Namespace(roots=["relative/dir"], kind=None, primary="relative/dir", yes=False)
        with self.assertRaises(WorldlineError):
            cli_main._root_mutation(client, "root.add", arguments, as_json=True)
        payload = client.request.call_args.args[1]
        self.assertEqual(payload["roots"], [os.path.abspath("relative/dir")])
        self.assertEqual(payload["primary"], os.path.abspath("relative/dir"))

    def test_a_symlinked_parent_does_not_walk_a_root_into_the_store(self) -> None:
        paths = WorldlinePaths.from_environment(environment(self.root))
        store = StateStore(paths, Core.shared())
        self.addCleanup(store.close)
        link = self.root / "projects-link"
        link.symlink_to(paths.state)
        with self.assertRaises(WorldlineError) as caught:
            RootManager(paths, store, core=Core.shared(), toolchains=()).validate([link / "receipts"])
        self.assertEqual(caught.exception.code, "WORLDLINE_SELF_CAPTURE")

    def test_a_store_under_a_system_bind_is_masked_in_every_sandbox(self) -> None:
        home = Path("/home/worldline-mask-test")
        paths = WorldlinePaths(home=home, data=Path("/var/lib/worldline-mask-test/data/worldline"),
                               state=Path("/var/lib/worldline-mask-test/state/worldline"),
                               config=Path("/var/lib/worldline-mask-test/config/worldline"),
                               runtime=Path("/run/worldline-mask-test"))
        sandbox = BubblewrapSandbox(paths, executable="/usr/bin/bwrap")
        target = Path(f"/tmp/worldline-mask-test-{uuid.uuid4()}")
        root = OverlayRoot("fixture", self.root / "lower", self.root / "upper", self.root / "work", target)
        spec = SandboxSpec(instance_id=str(uuid.uuid4()), argv=("/usr/bin/true",), cwd=target,
                           environment={"PATH": "/usr/bin"}, roots=(root,), runtime=self.root, operator_home=home)
        argv = list(sandbox.build_argv(spec))
        masked = {argv[index + 1] for index, value in enumerate(argv) if value == "--tmpfs"}
        for private in (paths.data, paths.state, paths.config):
            with self.subTest(private=str(private)):
                self.assertIn(str(private), masked)
                self.assertGreater(argv.index(str(private)), argv.index("/var"))  # after the /var bind
        # Under /run, which is already a tmpfs: nothing extra is mounted.
        self.assertNotIn(str(paths.runtime), masked)

    def _mask_fixture(self) -> tuple[WorldlinePaths, BubblewrapSandbox, OverlayRoot]:
        paths = WorldlinePaths(home=Path("/var/lib/worldline-mask-test"),
                               data=Path("/var/lib/worldline-mask-test/xdg-data/worldline"),
                               state=Path("/var/lib/worldline-mask-test/xdg-state/worldline"),
                               config=Path("/var/lib/worldline-mask-test/xdg-config/worldline"),
                               runtime=Path("/run/worldline-mask-test"))
        target = Path(f"/tmp/worldline-mask-test-{uuid.uuid4()}")
        root = OverlayRoot("fixture", self.root / "lower", self.root / "upper", self.root / "work", target)
        return paths, BubblewrapSandbox(paths, executable="/usr/bin/bwrap"), root

    def test_simulate_system_overlays_are_mounted_before_the_masks(self) -> None:
        # Review of 8102150, N2: overlays of /var mounted after the masks covered them.
        paths, sandbox, root = self._mask_fixture()
        var = OverlayRoot("system-var", self.root / "vl", self.root / "vu", self.root / "vw", Path("/var"))
        spec = SandboxSpec(instance_id=str(uuid.uuid4()), argv=("/usr/bin/true",), cwd=root.target,
                           environment={"PATH": "/usr/bin"}, roots=(var, root), runtime=self.root)
        argv = list(sandbox.build_argv(spec))
        var_overlay = max(index for index, value in enumerate(argv) if value == "/var" and argv[index - 1] == str(self.root / "vw"))
        tmpfs = {argv[index + 1]: index for index, value in enumerate(argv) if value == "--tmpfs"}
        self.assertGreater(tmpfs[str(paths.home)], var_overlay)  # the daemon HOME covers the store here
        managed = max(index for index, value in enumerate(argv) if value == str(root.target) and argv[index - 1] == str(root.work))
        self.assertGreater(managed, tmpfs[str(paths.home)])  # managed roots after the HOME mask

    def test_every_sandbox_masks_the_daemons_home_by_default(self) -> None:
        # Review of 8102150, N3: checks, services and simulate masked a fixed /home/sicarii.
        paths, sandbox, root = self._mask_fixture()
        spec = SandboxSpec(instance_id=str(uuid.uuid4()), argv=("/usr/bin/true",), cwd=root.target,
                           environment={"PATH": "/usr/bin"}, roots=(root,), runtime=self.root)
        argv = list(sandbox.build_argv(spec))
        masked = {argv[index + 1] for index, value in enumerate(argv) if value == "--tmpfs"}
        self.assertIn(str(paths.home), masked)
        self.assertNotIn("/home/sicarii", masked)
        self.assertEqual(argv[argv.index("HOME") + 1], str(paths.home))

    def test_an_existing_permissive_lock_is_made_owner_only(self) -> None:
        runtime = self.root / "runtime"
        runtime.mkdir()
        (runtime / "admission.lock").write_bytes(b"")
        os.chmod(runtime / "admission.lock", 0o644)
        ledger = Ledger(runtime)
        with ledger.locked():
            pass
        self.assertEqual(stat.S_IMODE(ledger.lock_path.stat().st_mode), 0o600)

    def test_out_of_range_identities_and_a_symlinked_runtime_refuse(self) -> None:
        cases = [environment(self.root / "range", WORLDLINE_CLIENT_GID="4294967295", WORLDLINE_CLIENT_UIDS="1000")]
        linked = environment(self.root / "linked", WORLDLINE_CLIENT_GID="970", WORLDLINE_CLIENT_UIDS="1000")
        (self.root / "linked" / "runtime-link").symlink_to(linked["XDG_STATE_HOME"])
        linked["XDG_RUNTIME_DIR"] = str(self.root / "linked" / "runtime-link")
        cases.append(linked)
        for env in cases:
            with self.subTest(runtime=env["XDG_RUNTIME_DIR"], gid=env["WORLDLINE_CLIENT_GID"]):
                with self.assertRaises(WorldlineError) as caught:
                    WorldlinePaths.from_environment(env)
                self.assertEqual(caught.exception.code, "INVALID_CLIENT_MODE")

    def test_root_remove_sends_a_path_absolute_and_a_key_as_given(self) -> None:
        for given, sent in (("relative/dir", os.path.abspath("relative/dir")), ("a" * 64, "a" * 64)):
            with self.subTest(given=given):
                client = mock.Mock()
                client.request.side_effect = WorldlineError("STOP", "stop here")
                with self.assertRaises(WorldlineError):
                    cli_main._root_mutation(client, "root.remove", argparse.Namespace(root=given, yes=False), as_json=True)
                self.assertEqual(client.request.call_args.args[1]["root"], sent)


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
