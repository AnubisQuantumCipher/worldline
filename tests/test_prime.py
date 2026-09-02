from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
import uuid

from worldline.core import Core, hash_id
from worldline.paths import WorldlinePaths
from worldline.prime import Generation, PrimeManager
from worldline.status import StatusPublisher
from worldline.store import StateStore


class PrimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-prime-")
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
        self.core = Core.shared()
        self.store = StateStore(self.paths, self.core)
        self.prime = PrimeManager(self.paths, self.store, self.core)

    def tearDown(self) -> None:
        self.store.close()
        self.temporary.cleanup()

    def test_prime_is_symbolic_reference_to_content_identity(self) -> None:
        generation_id = str(uuid.uuid4())
        payload = self.prime.new_generation(generation_id=generation_id)
        empty = hash_id(self.core.hash_bytes(b""))
        world = self.prime.publish_checkpoint(
            generation=Generation(
                generation_id=generation_id,
                payload=payload,
                root_set_hash=empty,
                state_root=empty,
                component_roots={"filesystem": empty, "config": empty, "repository": empty},
            ),
            cause="initial capture",
            environment_root=empty,
            evidence_root=empty,
        )
        self.assertTrue(world.content_id.startswith("sha256:"))
        self.assertNotEqual(world.alias, "PRIME")
        status = StatusPublisher(self.paths, self.store).snapshot()
        self.assertEqual(status["prime"]["alias"], "PRIME")
        self.assertEqual(status["prime"]["id"], world.content_id)


if __name__ == "__main__":
    unittest.main()
