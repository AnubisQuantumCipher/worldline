"""Ordinary offline key rotation over an intact temporary store.

The fixture supplies file-protection observations. This checks rotation/verification
integration, not enforcement of protection by the operating system.
"""
from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
import unittest
from unittest.mock import patch

from anchor_support import AnchoredLab
from worldline.cli_main import main


class AnchorRotationControl(unittest.TestCase):
    def test_offline_rotations_keep_intact_history_verifiable(self) -> None:
        lab = AnchoredLab(self)
        lab.commit("alpha", {"state.txt": "alpha"})
        for alias in ("beta", "gamma"):
            lab.close()
            output, error = io.StringIO(), io.StringIO()
            with patch.dict(os.environ, lab.env), redirect_stdout(output), redirect_stderr(error):
                code = main(["anchor", "rotate", "--json"])
            self.assertEqual(code, 0, error.getvalue())
            rotated = json.loads(output.getvalue())
            self.assertFalse(rotated["ownerRecordedRetirement"])
            self.assertNotEqual(rotated["publicKey"], rotated["retiredPublicKey"])
            lab.pin_path.write_text(json.dumps(rotated["pin"]), encoding="utf-8")
            lab.start()
            lab.controller._refresh_watcher()
            result = lab.commit(alias, {"state.txt": alias})
            self.assertEqual(result["state"], "COMMITTED")
            for command in (("log", "--verify", "--json"), ("anchor", "--json")):
                with self.subTest(alias=alias, command=command):
                    status, report, diagnostic = lab.cli(*command)
                    self.assertEqual(status, 0, diagnostic + report)


if __name__ == "__main__":
    unittest.main()
