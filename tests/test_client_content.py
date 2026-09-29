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
import stat
import tempfile
import unittest
from unittest import mock

from worldline.core import Core
from worldline.errors import WorldlineError
from worldline.paths import WorldlinePaths
from worldline.roots import RootManager
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

    def test_group_write_matters_only_for_the_client_group(self) -> None:
        # A umask-002 host puts g+w on everything a world writes; that grants a client nothing
        # while the entry carries the daemon's own group, which clients are never in.
        file = self.tree / "sub" / "file.txt"
        os.chmod(file, 0o664)
        os.chmod(self.tree / "sub", 0o775)
        self.paths.assert_client_safe(self.tree)
        os.chown(file, -1, SUPPLEMENTARY_GID)   # now the client group could write it
        details = self.refuses()
        self.assertEqual(details["count"], 1)
        self.assertIn(f"gid={SUPPLEMENTARY_GID}", details["entries"][0])

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


if __name__ == "__main__":
    unittest.main()
