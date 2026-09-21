"""`status` must answer while PRIME cannot be re-captured (worldline-lab D7, 2026-09-21)."""
from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from worldline.core import Core
from worldline.daemon import WorldlineDaemon
from worldline.errors import WorldlineError
from worldline.paths import WorldlinePaths
from worldline.status import StatusPublisher
from worldline.store import StateStore


class StatusDegradedTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-status-degraded-")
        root = Path(self.temporary.name)
        env = {name: str(root / part) for name, part in (("HOME", "home"), ("XDG_DATA_HOME", "data"), ("XDG_STATE_HOME", "state"), ("XDG_CONFIG_HOME", "config"), ("XDG_RUNTIME_DIR", "runtime"))}
        for value in env.values():
            Path(value).mkdir(mode=0o700, parents=True, exist_ok=True)
        self.paths = WorldlinePaths.from_environment(env)
        self.store = StateStore(self.paths, Core.shared())
        self.publisher = StatusPublisher(self.paths, self.store, lambda: {})

    def tearDown(self) -> None:
        self.store.close()
        self.temporary.cleanup()

    def test_capture_refusal_degrades_status_instead_of_failing_it(self) -> None:
        calls: list[str] = []

        def refusing() -> None:
            calls.append("refused")
            raise WorldlineError("EXTERNAL_HARDLINK", "hard-linked file has links outside the registered root: SECURITY.md", {"path": "SECURITY.md"})

        daemon = WorldlineDaemon(self.paths, self.store, self.publisher, reconcile_status=refusing)
        self.store.set_meta("dirty", True)
        snapshot = daemon._status({}, None)  # noqa: SLF001 - the handler is the unit under test
        self.assertEqual(calls, ["refused"])
        self.assertIn("schemaVersion", snapshot)
        self.assertEqual(self.store.get_meta("watchState"), "DEGRADED")
        self.assertEqual(self.store.get_meta("watchError")["code"], "EXTERNAL_HARDLINK")
        self.assertTrue(self.store.get_meta("dirty"), "dirty must stay set so mutations keep refusing by name")

        def healed() -> None:
            calls.append("captured")
            self.store.set_meta("dirty", False)

        daemon._reconcile_status = healed  # noqa: SLF001
        daemon._status({}, None)  # noqa: SLF001
        self.assertEqual(calls, ["refused", "captured"])
        self.assertIsNone(self.store.get_meta("watchError"))
        self.assertEqual(self.store.get_meta("watchState"), "HEALTHY")


if __name__ == "__main__":
    unittest.main()
