"""Client mode: content a client can reach is the daemon's, and read-only to everyone else.

Manifests record modes and materialization re-applies them, so a candidate chooses the modes of
what it stages. Before this check, a world that chmod'ed its root 0777 became a PRIME whose root a
client could write straight into, and the next status request adopted that write as a new PRIME
with no transaction (review of 8102150, N1). Now such content refuses at collapse prepare, at
generation publication and at daemon start (CLIENT_MODE_UNSAFE_CONTENT).
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from worldline.core import Core
from worldline.daemon import WorldlineDaemon
from worldline.errors import WorldlineError
from worldline.paths import WorldlinePaths
from worldline.roots import RootManager
from worldline.status import StatusPublisher
from worldline.store import StateStore

from tests.test_lifecycle_integrity import _FixtureDaemon

SUPPLEMENTARY_GID = next((gid for gid in os.getgroups() if gid != os.getgid()), None)
needs_supplementary = unittest.skipIf(SUPPLEMENTARY_GID is None, "needs a supplementary group")
CLIENT_ENV = {"WORLDLINE_CLIENT_GID": str(SUPPLEMENTARY_GID), "WORLDLINE_CLIENT_UIDS": str(os.getuid() + 4242)}

_OPENING_AGENT = """import json, os, sys
from pathlib import Path
workspace = Path(sys.argv[1])
(workspace / "open").mkdir()
(workspace / "open" / "note.txt").write_text("anyone may write here\\n")
os.chmod(workspace / "open", 0o777)
print(json.dumps({"type": "tool-event", "actor": "fixture", "path": str(workspace / "open"), "line": 1}), flush=True)
"""

_ORDINARY_AGENT = """import json, sys
from pathlib import Path
workspace = Path(sys.argv[1])
(workspace / "result.txt").write_text("ordinary\\n")
print(json.dumps({"type": "tool-event", "actor": "fixture", "path": str(workspace / "result.txt"), "line": 1}), flush=True)
"""


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


@needs_supplementary
class ContentSafety(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-client-content-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.paths = WorldlinePaths.from_environment(environment(self.root / "client", **CLIENT_ENV))
        self.tree = self.root / "tree"
        (self.tree / "sub").mkdir(parents=True)
        (self.tree / "sub" / "file.txt").write_text("fine\n")
        os.chmod(self.tree / "sub" / "file.txt", 0o644)

    def refuses(self) -> dict:
        with self.assertRaises(WorldlineError) as caught:
            self.paths.assert_client_safe(self.tree)
        self.assertEqual(caught.exception.code, "CLIENT_MODE_UNSAFE_CONTENT")
        return caught.exception.details

    def test_ordinary_modes_pass(self) -> None:
        self.paths.assert_client_safe(self.tree)

    def test_other_write_and_special_bits_refuse(self) -> None:
        cases = ((self.tree / "sub" / "file.txt", 0o646),
                 (self.tree / "sub" / "file.txt", 0o4755), (self.tree / "sub" / "file.txt", 0o2755),
                 (self.tree / "sub", 0o1755), (self.tree / "sub", 0o777), (self.tree, 0o777))
        for path, mode in cases:
            with self.subTest(path=path.name, mode=oct(mode)):
                os.chmod(path, mode)
                details = self.refuses()
                self.assertGreaterEqual(details["count"], 1)
                os.chmod(path, 0o755 if path.is_dir() else 0o644)

    def test_group_write_is_allowed_only_in_the_daemons_own_group(self) -> None:
        # A umask-002 host puts g+w on everything a world writes; that grants a client nothing
        # while the entry carries the daemon's own group, which no client may be in. Any other
        # group may hold a client (a migration that chowned only the owner keeps the operator's
        # group, and the operator is a client), so its write bit is refused (review of ad64cd2).
        file = self.tree / "sub" / "file.txt"
        os.chmod(file, 0o664)
        os.chmod(self.tree / "sub", 0o775)
        self.paths.assert_client_safe(self.tree)
        os.chown(file, -1, SUPPLEMENTARY_GID)   # a group other than the daemon's
        details = self.refuses()
        self.assertEqual(details["count"], 1)
        self.assertIn(f"gid={SUPPLEMENTARY_GID}", details["entries"][0])

    @unittest.skipIf(shutil.which("setfacl") is None, "setfacl is unavailable")
    def test_an_extended_acl_refuses_even_when_the_mode_looks_safe(self) -> None:
        file = self.tree / "sub" / "file.txt"
        applied = subprocess.run(["setfacl", "-m", "u:65534:rwx", str(file)], capture_output=True)
        if applied.returncode != 0:
            self.skipTest(f"this filesystem takes no ACLs: {applied.stderr!r}")
        details = self.refuses()
        self.assertTrue(any(" acl " in entry for entry in details["entries"]), details)

    def test_a_file_capability_refuses(self) -> None:
        # Review of 796cb02: manifests record security.capability and materialization re-applies
        # it; a client executing such a file gains the capability. Only a privileged process can
        # set a real one, so its presence is simulated here.
        real = os.listxattr
        target = os.fsencode(self.tree / "sub" / "file.txt")

        def listing(path, *args, **kwargs):
            names = real(path, *args, **kwargs)
            return names + ["security.capability"] if os.fsencode(path) == target else names

        with mock.patch("worldline.paths.os.listxattr", side_effect=listing):
            details = self.refuses()
        self.assertTrue(any("file-capability" in entry for entry in details["entries"]), details)

    def test_xattrs_that_cannot_be_read_refuse_rather_than_read_as_none(self) -> None:
        # Review of 796cb02: any listxattr error read as "no ACL".
        with mock.patch("worldline.paths.os.listxattr", side_effect=OSError(5, "Input/output error")):
            details = self.refuses()
        self.assertTrue(details["unreadable"], details)

    def test_any_system_acl_name_counts(self) -> None:
        from worldline.paths import xattr_risks
        with mock.patch("worldline.paths.os.listxattr", return_value=["system.nfs4_acl"]):
            self.assertEqual(xattr_risks(os.fsencode(self.tree)), (True, False))

    def test_a_client_group_member_in_the_daemons_group_is_refused(self) -> None:
        import grp
        import pwd
        member = "someone-else"
        fake_groups = {SUPPLEMENTARY_GID: grp.struct_group(("clients", "x", SUPPLEMENTARY_GID, [member])),
                       os.getgid(): grp.struct_group(("daemon", "x", os.getgid(), []))}
        fake_user = pwd.struct_passwd((member, "x", os.getuid() + 7, os.getgid(), "", "/", "/bin/sh"))
        with mock.patch("grp.getgrgid", side_effect=lambda gid: fake_groups[gid]), \
                mock.patch("pwd.getpwnam", return_value=fake_user):
            with self.assertRaises(WorldlineError) as caught:
                WorldlinePaths.from_environment(environment(self.root / "overlap", **CLIENT_ENV))
        self.assertEqual(caught.exception.code, "INVALID_CLIENT_MODE")

    def test_content_the_daemon_does_not_own_refuses(self) -> None:
        with mock.patch("worldline.paths.os.getuid", return_value=os.getuid() + 1):
            self.refuses()

    def test_without_client_mode_nothing_is_checked(self) -> None:
        os.chmod(self.tree / "sub", 0o777)
        WorldlinePaths.from_environment(environment(self.root / "plain")).assert_client_safe(self.tree)

    def test_the_daemons_primary_group_cannot_be_the_client_group(self) -> None:
        with self.assertRaises(WorldlineError) as caught:
            WorldlinePaths.from_environment(environment(
                self.root / "primary", WORLDLINE_CLIENT_GID=str(os.getgid()), WORLDLINE_CLIENT_UIDS="4242"))
        self.assertEqual(caught.exception.code, "INVALID_CLIENT_MODE")


@needs_supplementary
class StartupRefusesUnsafePrime(unittest.TestCase):
    def test_a_writable_prime_is_not_opened_to_clients(self) -> None:
        with tempfile.TemporaryDirectory(prefix="worldline-client-start-") as temporary:
            root = Path(temporary)
            owner = WorldlinePaths.from_environment(environment(root))
            store = StateStore(owner, Core.shared())
            work = root / "work"
            work.mkdir()
            (work / "state.txt").write_text("prime\n")
            RootManager(owner, store, core=Core.shared(), toolchains=()).register([work], confirmed=True)
            content = Path(os.path.realpath(owner.live / store.roots()[0]["root_key"]))
            store.close()
            os.chmod(content, 0o777)  # as a pre-1.7.0 collapse could have left it
            client = WorldlinePaths.from_environment(environment(root, **CLIENT_ENV))
            with self.assertRaises(WorldlineError) as caught:
                client.share_live_chain()
            self.assertEqual(caught.exception.code, "CLIENT_MODE_UNSAFE_CONTENT")
            self.assertNotEqual(stat.S_IMODE(content.parent.stat().st_mode), 0o710)  # nothing opened


@needs_supplementary
class DaemonStartClosesTheGate(unittest.IsolatedAsyncioTestCase):
    async def test_a_start_that_refuses_leaves_a_previously_opened_gate_closed(self) -> None:
        # Review of ad64cd2: a start over unsafe content exited with the gate a previous run
        # had opened still open.
        with tempfile.TemporaryDirectory(prefix="worldline-client-gate-start-") as temporary:
            root = Path(temporary)
            owner = WorldlinePaths.from_environment(environment(root))
            store = StateStore(owner, Core.shared())
            work = root / "work"
            work.mkdir()
            (work / "state.txt").write_text("prime\n")
            RootManager(owner, store, core=Core.shared(), toolchains=()).register([work], confirmed=True)
            content = Path(os.path.realpath(owner.live / store.roots()[0]["root_key"]))
            store.close()
            client = WorldlinePaths.from_environment(environment(root, **CLIENT_ENV))
            client.share_live_chain()                      # a previous, healthy start
            self.assertEqual(stat.S_IMODE(client.data.stat().st_mode), 0o710)
            os.chmod(content, 0o777)                       # content turns unsafe while stopped
            store = StateStore(client, Core.shared())
            daemon = WorldlineDaemon(client, store, StatusPublisher(client, store, lambda: {}))
            try:
                with self.assertRaises(WorldlineError) as caught:
                    await daemon.start()
                self.assertEqual(caught.exception.code, "CLIENT_MODE_UNSAFE_CONTENT")
                self.assertEqual(stat.S_IMODE(client.data.stat().st_mode), 0o700)
            finally:
                await daemon.stop()
                store.close()


@needs_supplementary
class CollapseRefusesUnsafeContent(unittest.TestCase):
    def fixture(self, agent: str) -> _FixtureDaemon:
        with mock.patch.dict(os.environ, CLIENT_ENV):
            fixture = _FixtureDaemon(self, agent)
        self.addCleanup(fixture.close)
        fixture.client.request("init", {"roots": [str(fixture.work)], "kind": None, "primary": None, "confirmed": True})
        return fixture

    def test_a_candidate_that_opens_its_modes_is_refused_before_a_transaction_exists(self) -> None:
        fixture = self.fixture(_OPENING_AGENT)
        client = fixture.client
        prime = client.request("status")["prime"]["id"]
        self.assertEqual(client.request("fork", {"name": "opener", "mission": "m", "agent": "fixture", "wait": True})["state"], "VALID")
        with self.assertRaises(WorldlineError) as caught:
            client.request("collapse.prepare", {"world": "opener"})
        self.assertEqual(caught.exception.code, "CLIENT_MODE_UNSAFE_CONTENT")
        self.assertTrue(any("open" in entry for entry in caught.exception.details["entries"]))
        self.assertEqual(client.request("transaction.list"), [])
        self.assertEqual(client.request("status")["prime"]["id"], prime)

    def test_ordinary_content_collapses_in_client_mode(self) -> None:
        fixture = self.fixture(_ORDINARY_AGENT)
        client = fixture.client
        self.assertEqual(client.request("fork", {"name": "ordinary", "mission": "m", "agent": "fixture", "wait": True})["state"], "VALID")
        try:
            prepared = client.request("collapse.prepare", {"world": "ordinary"})
        except WorldlineError as exc:  # name the entries: a CI runner refused here without saying why
            self.fail(f"{exc.code}: {exc.message} {exc.details}")
        client.request("collapse.commit", {"transactionId": prepared["transaction_id"]})
        self.assertEqual((fixture.work / "result.txt").read_text(), "ordinary\n")
        content = Path(os.path.realpath(fixture.work))
        self.assertEqual(stat.S_IMODE(content.parent.stat().st_mode), 0o710)
        self.assertEqual(content.parent.stat().st_gid, SUPPLEMENTARY_GID)


@needs_supplementary
class RefusedRegistrationKeepsTheDirectory(unittest.TestCase):
    """Review of 796cb02 (blocker): the cleanup of a refused generation also ran on registration,
    whose generation holds the operator's own directory, moved in. A refused `init` deleted it."""

    def test_a_refused_registration_moves_the_directory_back_intact(self) -> None:
        import hashlib
        with tempfile.TemporaryDirectory(prefix="worldline-register-refused-") as temporary:
            root = Path(temporary)
            paths = WorldlinePaths.from_environment(environment(root, **CLIENT_ENV))
            store = StateStore(paths, Core.shared())
            self.addCleanup(store.close)
            project = root / "project"
            (project / "src").mkdir(parents=True)
            (project / "README").write_text("the only copy\n")
            (project / "src" / "build.log").write_text("log\n")
            os.chmod(project / "src" / "build.log", 0o666)   # refused in client mode

            def digest() -> str:
                value = hashlib.sha256()
                for directory, _subdirectories, files in sorted(os.walk(project)):
                    for name in sorted(files):
                        path = Path(directory, name)
                        value.update(str(path.relative_to(project)).encode() + b"\0" + path.read_bytes())
                return value.hexdigest()

            before = digest()
            gate_before = stat.S_IMODE(paths.data.stat().st_mode)
            with self.assertRaises(WorldlineError) as caught:
                RootManager(paths, store, core=Core.shared(), toolchains=()).register([project], confirmed=True)
            self.assertEqual(caught.exception.code, "CLIENT_MODE_UNSAFE_CONTENT")
            self.assertTrue(project.is_dir() and not project.is_symlink())
            self.assertEqual(digest(), before)
            self.assertEqual(store.roots(), [])
            self.assertEqual(list(paths.generations.iterdir()), [])
            # Live content was not the unsafe part, so the gate is left as it was.
            self.assertEqual(stat.S_IMODE(paths.data.stat().st_mode), gate_before)


class RegistrationThatFailsMidwayKeepsTheDirectory(unittest.TestCase):
    """Review of 4490013: a failure after the move but before it was recorded (a directory flush
    on a parent the account may write but not read) had the discard delete the only copy."""

    def test_a_flush_that_fails_after_the_move_leaves_the_directory_in_place(self) -> None:
        with tempfile.TemporaryDirectory(prefix="worldline-register-midway-") as temporary:
            root = Path(temporary)
            paths = WorldlinePaths.from_environment(environment(root))
            store = StateStore(paths, Core.shared())
            self.addCleanup(store.close)
            project = root / "project"
            project.mkdir()
            (project / "README").write_text("the only copy\n")
            with mock.patch("worldline.roots.fsync_directory", side_effect=PermissionError(13, "Permission denied")):
                with self.assertRaises(PermissionError):
                    RootManager(paths, store, core=Core.shared(), toolchains=()).register([project], confirmed=True)
            self.assertTrue(project.is_dir() and not project.is_symlink())
            self.assertEqual((project / "README").read_text(), "the only copy\n")
            self.assertEqual(store.roots(), [])


class MaterializationOfReadOnlyDirectories(unittest.TestCase):
    """Review of 4490013: a directory created with its recorded 0555 could not receive its own
    entries, so a root holding one could never be copied again."""

    def test_a_read_only_directory_with_content_is_copied(self) -> None:
        from worldline.manifest import Manifest
        with tempfile.TemporaryDirectory(prefix="worldline-readonly-dir-") as temporary:
            source = Path(temporary) / "source"
            (source / "vendored").mkdir(parents=True)
            (source / "vendored" / "lib.txt").write_text("vendored\n")
            os.chmod(source / "vendored", 0o555)
            copy = Path(temporary) / "copy"
            try:
                manifest = Manifest.capture(source, root_key="k" * 64, kind="filesystem", core=Core.shared())
                Manifest.materialize(manifest, source, copy, core=Core.shared())
                self.assertEqual((copy / "vendored" / "lib.txt").read_text(), "vendored\n")
                self.assertEqual(stat.S_IMODE((copy / "vendored").stat().st_mode), 0o555)
            finally:
                for directory in (source / "vendored", copy / "vendored"):
                    if directory.is_dir():
                        os.chmod(directory, 0o755)


class StoreLockRefusesWhatIsNotItsOwnFile(unittest.TestCase):
    def test_a_directory_link_or_hard_link_at_the_lock_path_refuses_by_name(self) -> None:
        from worldline.paths import acquire_store_lock
        with tempfile.TemporaryDirectory(prefix="worldline-lockfile-") as temporary:
            state = Path(temporary) / "state"
            state.mkdir()
            elsewhere = Path(temporary) / "other-store-lock"
            elsewhere.write_text("4242 worldlined\n")
            for make in ("directory", "symlink", "hardlink"):
                with self.subTest(make=make):
                    lock = state / "worldlined.lock"
                    if make == "directory":
                        lock.mkdir()
                    elif make == "symlink":
                        lock.symlink_to(elsewhere)
                    else:
                        os.link(elsewhere, lock)
                    with self.assertRaises(WorldlineError) as caught:
                        acquire_store_lock(state, holder="test", create_directory=False)
                    self.assertEqual(caught.exception.code, "UNSAFE_STORE")
                    self.assertEqual(elsewhere.read_text(), "4242 worldlined\n")  # never rewritten
                    lock.rmdir() if make == "directory" else lock.unlink()


@needs_supplementary
class StartupOrdersTheGateAfterTheLock(unittest.TestCase):
    """Review of 796cb02: a second start closed a running daemon's gate before its lock refused
    it, and a start refused before the close left a previous run's gate open."""

    def daemon(self, env: dict[str, str]) -> subprocess.CompletedProcess:
        repo = Path(__file__).resolve().parents[1]
        return subprocess.run([sys.executable, "-B", "-m", "worldline.daemon_main"],
                              env={**os.environ, **env, "PYTHONPATH": str(repo / "runtime"),
                                   "PYTHONDONTWRITEBYTECODE": "1"},
                              capture_output=True, timeout=60)

    def test_a_second_start_leaves_the_running_daemons_gate_and_store_alone(self) -> None:
        from worldline.paths import acquire_store_lock
        with tempfile.TemporaryDirectory(prefix="worldline-second-start-") as temporary:
            env = environment(Path(temporary), **CLIENT_ENV)
            paths = WorldlinePaths.from_environment(env)
            paths.ensure()
            paths.share_live_chain()                       # the running daemon opened its gate
            lock = acquire_store_lock(paths.state, holder="running daemon")
            self.addCleanup(os.close, lock)
            result = self.daemon(env)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn(b"DAEMON_ALREADY_RUNNING", result.stderr)
            self.assertEqual(stat.S_IMODE(paths.data.stat().st_mode), 0o710)
            self.assertFalse(paths.database.exists())      # nothing was built

    def test_a_configuration_that_refuses_still_closes_the_gate(self) -> None:
        # Review of 4490013: INVALID_CLIENT_MODE was raised before the store lock, so the gate a
        # previous run opened stayed open while the unit kept failing.
        with tempfile.TemporaryDirectory(prefix="worldline-refused-config-") as temporary:
            env = environment(Path(temporary), **CLIENT_ENV)
            paths = WorldlinePaths.from_environment(env)
            paths.ensure()
            paths.share_live_chain()
            broken = {**env, "WORLDLINE_CLIENT_UIDS": ""}   # client group without uids
            result = self.daemon(broken)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn(b"INVALID_CLIENT_MODE", result.stderr)
            self.assertEqual(stat.S_IMODE(paths.data.stat().st_mode), 0o700)

    def test_a_start_that_refuses_after_the_lock_closes_the_gate(self) -> None:
        with tempfile.TemporaryDirectory(prefix="worldline-refused-start-") as temporary:
            env = environment(Path(temporary), **CLIENT_ENV)
            paths = WorldlinePaths.from_environment(env)
            paths.ensure()
            paths.share_live_chain()
            paths.worlds.rmdir()
            paths.worlds.write_text("not a directory\n")  # ensure() refuses UNSAFE_STORE
            result = self.daemon(env)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn(b"UNSAFE_STORE", result.stderr)
            self.assertEqual(stat.S_IMODE(paths.data.stat().st_mode), 0o700)


class DoctorReportsClientMode(unittest.TestCase):
    """The deployment requirements a client-mode daemon can observe are reported, never assumed."""

    @needs_supplementary
    def test_the_doctor_names_the_gate_and_the_host_facts(self) -> None:
        with mock.patch.dict(os.environ, CLIENT_ENV):
            fixture = _FixtureDaemon(self, _ORDINARY_AGENT)
        self.addCleanup(fixture.close)
        fixture.client.request("init", {"roots": [str(fixture.work)], "kind": None, "primary": None, "confirmed": True})
        report = fixture.client.request("doctor", {})["clientMode"]
        self.assertTrue(report["enabled"])
        self.assertEqual(report["clientGid"], SUPPLEMENTARY_GID)
        self.assertEqual(report["clientUids"], [os.getuid() + 4242])
        self.assertEqual(report["gate"], {"state": "OPEN"})
        self.assertEqual(set(report["deployment"]),
                         {"protectedHardlinks", "storeNosuid", "memoryMax", "memorySwapMax", "tasksMax"})
        for name, fact in report["deployment"].items():
            with self.subTest(fact=name):
                self.assertIn(fact["state"], {"OK", "MISSING", "UNKNOWN"})

    def test_an_owner_only_daemon_reports_client_mode_off(self) -> None:
        with mock.patch.dict(os.environ):
            for name in ("WORLDLINE_CLIENT_GID", "WORLDLINE_CLIENT_UIDS"):
                os.environ.pop(name, None)
            fixture = _FixtureDaemon(self, _ORDINARY_AGENT)
        self.addCleanup(fixture.close)
        self.assertEqual(fixture.client.request("doctor", {})["clientMode"], {"enabled": False})

    def test_each_fact_is_read_and_a_fact_that_cannot_be_read_is_unknown(self) -> None:
        from worldline.paths import deployment_facts
        real_read = Path.read_text

        def host(self, *args, **kwargs):
            name = str(self)
            if name == "/proc/sys/fs/protected_hardlinks":
                return "0\n"
            if name.endswith("/memory.max"):
                return "4294967296\n"
            if name.endswith("/memory.swap.max"):
                return "max\n"
            if name.endswith("/pids.max"):
                raise PermissionError(13, "Permission denied", name)
            return real_read(self, *args, **kwargs)

        with tempfile.TemporaryDirectory() as store, mock.patch.object(Path, "read_text", host):
            facts = deployment_facts(Path(store))
        self.assertEqual(facts["protectedHardlinks"], {"state": "MISSING", "value": "0"})
        self.assertEqual(facts["memoryMax"]["state"], "OK")
        self.assertEqual(facts["memoryMax"]["value"], "4294967296")
        self.assertEqual(facts["memorySwapMax"]["state"], "MISSING")   # memory.max does not cover swap
        self.assertEqual(facts["tasksMax"]["state"], "UNKNOWN")
        self.assertIn(facts["storeNosuid"]["state"], {"OK", "MISSING"})
        self.assertEqual(facts["storeNosuid"]["view"], "host (PID 1's mount table)")
        with mock.patch("worldline.paths._host_mount_options", side_effect=PermissionError(13, "denied")):
            self.assertEqual(deployment_facts(Path("/"))["storeNosuid"]["state"], "UNKNOWN")

    def test_nosuid_is_read_from_the_host_mount_table_not_the_daemons(self) -> None:
        # Review of 796cb02: inside a unit with NoNewPrivileges= and a mount namespace systemd
        # mounts everything nosuid, so the daemon's own view read OK over a suid-capable host mount.
        from worldline.paths import _host_mount_options
        with tempfile.NamedTemporaryFile("w", delete=False, dir=self.scratch()) as table:
            table.write("32 2 253:0 / / rw,relatime shared:1 - ext4 /dev/vda rw\n"
                        "90 32 253:0 /var/lib/x /var/lib/x rw,nosuid,nodev,relatime shared:2 - ext4 /dev/vda rw\n"
                        "91 32 0:40 / /var/lib/x\\040y rw,relatime shared:3 - tmpfs t rw\n")
        self.assertEqual(_host_mount_options("/var/lib/x/xdg-data/worldline", table.name)[1][:3], ["rw", "nosuid", "nodev"])
        self.assertEqual(_host_mount_options("/var/lib/xy", table.name)[0], "/")
        self.assertEqual(_host_mount_options("/var/lib/x y/z", table.name)[0], "/var/lib/x y")
        # A mount covered by a later one is not the mount in use (review of 4490013): a nosuid
        # mount at /var/lib/x, then a suid-capable one at /var/lib on top of the root.
        with tempfile.NamedTemporaryFile("w", delete=False, dir=self.scratch()) as covered:
            covered.write("32 2 253:0 / / rw,relatime shared:1 - ext4 /dev/vda rw\n"
                          "90 32 253:0 /a /var/lib/x rw,nosuid,relatime shared:2 - ext4 /dev/vda rw\n"
                          "95 32 253:0 /b /var/lib rw,relatime shared:3 - ext4 /dev/vda rw\n")
        self.assertEqual(_host_mount_options("/var/lib/x/store", covered.name), ("/var/lib", ["rw", "relatime"]))

    def test_nosuid_is_unknown_when_pid_1_is_not_the_hosts_init(self) -> None:
        from worldline.paths import deployment_facts
        real_read = Path.read_text

        def read(self, *args, **kwargs):
            return "python3\n" if str(self) == "/proc/1/comm" else real_read(self, *args, **kwargs)

        with mock.patch.object(Path, "read_text", read):
            self.assertEqual(deployment_facts(Path("/"))["storeNosuid"]["state"], "UNKNOWN")

    def scratch(self) -> str:
        directory = tempfile.mkdtemp(prefix="worldline-mounts-")
        self.addCleanup(lambda: __import__("shutil").rmtree(directory, ignore_errors=True))
        return directory

    def test_the_gate_names_a_state_that_is_neither_open_nor_closed(self) -> None:
        # Review of 796cb02: 0711, 0755 and a foreign group were all reported CLOSED.
        from worldline.controller import RuntimeController
        with tempfile.TemporaryDirectory(prefix="worldline-gate-") as temporary:
            paths = WorldlinePaths.from_environment(environment(Path(temporary), **CLIENT_ENV))
            paths.ensure()
            controller = mock.Mock(paths=paths)
            self.assertEqual(RuntimeController._client_mode_report(controller)["gate"], {"state": "CLOSED"})
            os.chmod(paths.data, 0o755)
            gate = RuntimeController._client_mode_report(controller)["gate"]
            self.assertEqual((gate["state"], gate["mode"]), ("UNSAFE", "0755"))


if __name__ == "__main__":
    unittest.main()
