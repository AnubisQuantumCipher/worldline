"""A managed root's content is resolved through the store's own live mapping, never the operator's link.

The registered path (`~/Projects/x`) is a symlink in a directory its operator owns. Under a
dedicated-account daemon that operator is a client, so a client that re-points the link must
not choose what the daemon captures as PRIME, loads policy from, reads for `why`, or keeps
when pruning. The link must still route through the live mapping, or the root is refused.

In client mode the directories between the store and PRIME's content are 0710 with the client
group, so a client can read PRIME through the symlink chain and list or write nothing.
"""
from __future__ import annotations

import os
from pathlib import Path
import stat
import tempfile
import unittest

from worldline.causal import CausalIndexer
from worldline.core import Core
from worldline.errors import NotFound, WorldlineError
from worldline.paths import WorldlinePaths
from worldline.prune import Pruner
from worldline.roots import RootManager
from worldline.store import StateStore


# A supplementary group: files are not created with it, so a missing group change fails.
SUPPLEMENTARY_GID = next((gid for gid in os.getgroups() if gid != os.getgid()), None)


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


class _Registered(unittest.TestCase):
    client_mode = False

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-root-resolution-")
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        extra = ({"WORLDLINE_CLIENT_GID": str(SUPPLEMENTARY_GID), "WORLDLINE_CLIENT_UIDS": str(os.getuid() + 4242)}
                 if self.client_mode else {})
        self.paths = WorldlinePaths.from_environment(environment(root, **extra))
        self.store = StateStore(self.paths, Core.shared())
        self.addCleanup(self.store.close)
        self.manager = RootManager(self.paths, self.store, core=Core.shared(), toolchains=())
        self.work = root / "work"
        self.work.mkdir()
        (self.work / "state.txt").write_bytes(b"prime bytes\n")
        self.work_mode = stat.S_IMODE(self.work.stat().st_mode)
        self.manager.register([self.work], confirmed=True)
        self.root = self.store.roots()[0]
        self.prime = self.store.prime().content_id
        # The client's own directory, which it would like the daemon to adopt as PRIME.
        self.elsewhere = root / "elsewhere"
        self.elsewhere.mkdir()
        (self.elsewhere / "state.txt").write_bytes(b"not reviewed\n")

    def repoint(self, target: Path) -> None:
        self.work.unlink()
        self.work.symlink_to(target)


class RootSourceTests(_Registered):
    def test_intact_routing_resolves_to_the_store_payload(self) -> None:
        source = self.paths.root_source(self.root)
        store = os.path.realpath(os.fsencode(self.paths.data))
        self.assertTrue(source.startswith(store + b"/"))
        self.assertEqual(Path(os.fsdecode(source), "state.txt").read_bytes(), b"prime bytes\n")

    def test_a_repointed_link_is_refused_and_prime_is_not_recaptured(self) -> None:
        self.repoint(self.elsewhere)
        self.store.set_meta("dirty", True)  # what the watcher records for an external change
        with self.assertRaises(WorldlineError) as caught:
            self.manager.reconcile()
        self.assertEqual(caught.exception.code, "LIVE_MAPPING_BROKEN")
        self.assertEqual(self.store.prime().content_id, self.prime)

    def test_a_link_straight_to_the_payload_is_still_not_the_live_mapping(self) -> None:
        # Resolves to the same bytes today, but does not follow the next collapse.
        self.repoint(Path(os.fsdecode(self.paths.root_source(self.root))))
        with self.assertRaises(WorldlineError) as caught:
            self.paths.root_source(self.root)
        self.assertEqual(caught.exception.code, "LIVE_MAPPING_BROKEN")

    def test_equivalent_spellings_of_the_live_entry_still_route(self) -> None:
        live = self.paths.live / self.root["root_key"]
        linked_home = Path(self.temporary.name) / "home-link"
        linked_home.symlink_to(self.paths.data.parent)
        spellings = (
            f"{live}/",                                                    # trailing slash
            str(self.paths.data) + "//live/" + self.root["root_key"],      # doubled slash
            str(linked_home / "worldline" / "live" / self.root["root_key"]),  # through a link
            os.path.relpath(live, self.work.parent),                       # relative
        )
        for spelling in spellings:
            with self.subTest(spelling=spelling):
                self.repoint(Path(spelling))
                self.assertEqual(self.paths.root_source(self.root), os.path.realpath(os.fsencode(live)))

    def test_a_real_directory_at_the_registered_path_is_refused(self) -> None:
        # What an interrupted `root remove` leaves; the doctor already calls it BROKEN.
        self.work.unlink()
        self.work.mkdir()
        (self.work / "state.txt").write_bytes(b"diverged\n")
        with self.assertRaises(WorldlineError) as caught:
            self.manager.capture_current()
        self.assertEqual(caught.exception.code, "LIVE_MAPPING_BROKEN")

    def test_a_live_mapping_that_leaves_the_store_is_refused(self) -> None:
        live = self.paths.live / self.root["root_key"]
        live.unlink()
        live.symlink_to(self.elsewhere)
        with self.assertRaises(WorldlineError) as caught:
            self.paths.root_source(self.root)
        self.assertEqual(caught.exception.code, "LIVE_MAPPING_BROKEN")

    def test_prune_refuses_rather_than_forget_which_payload_is_live(self) -> None:
        self.repoint(self.elsewhere)
        with self.assertRaises(WorldlineError) as caught:
            Pruner(self.paths, self.store).plan(older_than_days=None, keep=None, logs=False)
        self.assertEqual(caught.exception.code, "LIVE_MAPPING_BROKEN")

    def test_why_does_not_leave_the_root(self) -> None:
        outside = Path(self.temporary.name) / "secret.txt"
        outside.write_bytes(b"daemon-only line\n")
        climbing = f"{self.work}/../secret.txt"
        with self.assertRaises(NotFound):
            CausalIndexer(self.store).why(climbing, 1)


@unittest.skipIf(SUPPLEMENTARY_GID is None, "needs a supplementary group")
class ClientModePrimeChainTests(_Registered):
    client_mode = True

    def _mode_and_group(self, path: Path) -> tuple[int, int]:
        info = path.lstat()
        return stat.S_IMODE(info.st_mode), info.st_gid

    def test_the_data_directory_is_a_gate_opened_only_after_the_check(self) -> None:
        self.assertEqual(stat.S_IMODE(self.paths.data.stat().st_mode), 0o700)   # created closed
        self.paths.share_live_chain()
        self.assertEqual(self._mode_and_group(self.paths.data), (0o710, SUPPLEMENTARY_GID))
        self.paths.ensure()                                                       # leaves it open
        self.assertEqual(self._mode_and_group(self.paths.data)[0], 0o710)
        self.paths.close_client_gate()
        self.assertEqual(stat.S_IMODE(self.paths.data.stat().st_mode), 0o700)
        self.paths.ensure()                                                       # leaves it closed
        self.assertEqual(stat.S_IMODE(self.paths.data.stat().st_mode), 0o700)

    def test_unsafe_live_content_found_while_running_closes_the_gate(self) -> None:
        self.paths.share_live_chain()
        content = Path(os.fsdecode(self.paths.root_source(self.root)))
        os.chmod(content, 0o777)
        self.store.set_meta("dirty", True)
        with self.assertRaises(WorldlineError) as caught:
            self.manager.reconcile()
        self.assertEqual(caught.exception.code, "CLIENT_MODE_UNSAFE_CONTENT")
        self.assertEqual(stat.S_IMODE(self.paths.data.stat().st_mode), 0o700)

    def test_the_chain_to_prime_is_traverse_only_for_the_client_group(self) -> None:
        self.paths.share_live_chain()  # what daemon start does
        source = Path(os.fsdecode(self.paths.root_source(self.root)))
        chain = [self.paths.data, self.paths.live]
        current = Path(os.path.realpath(self.paths.data))
        for part in source.relative_to(current).parts[:-1]:
            current = current / part
            chain.append(current)
        self.assertIn(self.paths.generations, [Path(p) for p in chain])
        for directory in chain:
            with self.subTest(directory=str(directory)):
                self.assertEqual(self._mode_and_group(directory), (0o710, SUPPLEMENTARY_GID))
        # The root's own directory keeps the mode its manifest records; manifests stay private.
        self.assertEqual(stat.S_IMODE(source.stat().st_mode), self.work_mode)
        self.assertEqual(stat.S_IMODE((source.parent / "manifests").stat().st_mode), 0o700)
        for private in (self.paths.state, self.paths.worlds, self.paths.overlays, self.paths.config):
            with self.subTest(private=str(private)):
                self.assertEqual(stat.S_IMODE(private.stat().st_mode), 0o700)

    def test_share_live_chain_opens_a_store_written_before_client_mode(self) -> None:
        source = Path(os.fsdecode(self.paths.root_source(self.root)))
        generation = source.parent.parent
        for directory in (generation, source.parent):
            directory.chmod(0o700)
        self.paths.share_live_chain()
        for directory in (generation, source.parent):
            with self.subTest(directory=str(directory)):
                self.assertEqual(self._mode_and_group(directory), (0o710, SUPPLEMENTARY_GID))

    def test_without_client_mode_every_store_directory_stays_0700(self) -> None:
        owner_only = WorldlinePaths.from_environment(environment(Path(self.temporary.name) / "plain"))
        store = StateStore(owner_only, Core.shared())
        self.addCleanup(store.close)
        for directory in (owner_only.data, owner_only.live, owner_only.generations):
            with self.subTest(directory=str(directory)):
                self.assertEqual(stat.S_IMODE(directory.stat().st_mode), 0o700)


if __name__ == "__main__":
    unittest.main()
