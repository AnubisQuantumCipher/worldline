from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from worldline.install_config import patch_bindings, patch_shell


class InstallConfigTests(unittest.TestCase):
    def test_shell_and_bindings_patches_are_idempotent(self) -> None:
        with tempfile.TemporaryDirectory(prefix="worldline-install-config-") as temporary:
            root = Path(temporary)
            shell = root / "shell.json"
            shell.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "bar": {
                            "layout": {
                                "left": [],
                                "center": [],
                                "right": [
                                    {"id": "khephri.jackal", "setting": "preserved"},
                                    {"id": "omarchy.indicators"},
                                ],
                            }
                        },
                        "unrelated": {"preserved": True},
                    }
                ),
                encoding="utf-8",
            )
            bindings = root / "bindings.lua"
            bindings.write_text("o.bind(\"SUPER + A\", \"Keep\", \"true\")\n", encoding="utf-8")
            patch_shell(shell)
            patch_shell(shell)
            patch_bindings(bindings)
            patch_bindings(bindings)
            value = json.loads(shell.read_text(encoding="utf-8"))
            ids = [item["id"] for item in value["bar"]["layout"]["right"]]
            self.assertEqual(ids, ["khephri.jackal", "khephri.worldline", "omarchy.indicators"])
            self.assertTrue(value["unrelated"]["preserved"])
            text = bindings.read_text(encoding="utf-8")
            self.assertEqual(text.count("BEGIN WORLDLINE"), 1)
            self.assertIn("Omawrite", text)
            self.assertIn("Network", text)
            self.assertIn("Move window to group on right", text)
            self.assertIn("o.bind(\"SUPER + A\"", text)
            self.assertIn("'{\\\"mode\\\":\\\"fork\\\"}'", text)


if __name__ == "__main__":
    unittest.main()
