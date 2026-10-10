from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from worldline.anchor import GENESIS, AnchorLedger
from worldline.paths import WorldlinePaths


def _paths(root: Path) -> WorldlinePaths:
    env = {
        "HOME": str(root / "home"), "XDG_DATA_HOME": str(root / "data"), "XDG_STATE_HOME": str(root / "state"),
        "XDG_CONFIG_HOME": str(root / "config"), "XDG_RUNTIME_DIR": str(root / "runtime"),
    }
    for value in env.values():
        Path(value).mkdir(mode=0o700, parents=True, exist_ok=True)
    paths = WorldlinePaths.from_environment(env)
    paths.ensure()
    return paths


class AnchorLedgerTests(unittest.TestCase):
    def test_entries_link_verify_export_and_detect_tampering_and_rollback(self) -> None:
        with tempfile.TemporaryDirectory(prefix="worldline-anchor-") as temporary:
            root = Path(temporary)
            paths = _paths(root)
            export = root / "external"
            ledger = AnchorLedger(paths, export)
            self.assertEqual(ledger.verify()["state"], "EMPTY")
            first = ledger.append(action="collapse", receipt_id="WL:aaa", canonical=b'{"receipt":1}')
            second = ledger.append(action="return", receipt_id="WL:bbb", canonical=b'{"receipt":2}')
            self.assertEqual(first["seq"], 0)
            self.assertEqual(second["seq"], 1)
            self.assertEqual(first["export"]["state"], "EXPORTED")
            self.assertEqual((ledger.secret_path.stat().st_mode & 0o777), 0o600)
            lines = ledger.entries()
            self.assertEqual(len(lines), 2)
            fields = lines[0].split("\t")
            self.assertEqual(len(fields), 9)
            self.assertEqual(fields[7], GENESIS)
            self.assertEqual(fields[5], hashlib.sha256(b'{"receipt":1}').hexdigest())
            self.assertEqual(lines[1].split("\t")[7], hashlib.sha256(lines[0].encode()).hexdigest())

            report = ledger.verify(receipts_known=2)
            self.assertEqual(report["state"], "OK")
            self.assertEqual(report["entries"], 2)
            self.assertEqual(report["unanchoredReceipts"], 0)
            self.assertEqual(report["external"]["state"], "MATCH")
            self.assertIn(report["attest"]["state"], ("VERIFIED", "UNAVAILABLE"))
            if report["attest"]["state"] == "VERIFIED":
                self.assertEqual(report["attest"]["exitCode"], 0)

            # A third receipt exists but was never anchored: coverage says so.
            self.assertEqual(ledger.verify(receipts_known=3)["unanchoredReceipts"], 1)

            # Tamper with the first entry's action: chain breaks (its line hash feeds entry 1) and
            # the signature no longer matches.
            original = ledger.ledger_path.read_text("utf-8")
            ledger.ledger_path.write_text(original.replace("collapse", "COLLAPSE", 1), encoding="utf-8")
            broken = ledger.verify()
            self.assertEqual(broken["state"], "BROKEN")
            self.assertGreaterEqual(broken["badSignature"] + broken["badChain"], 1)
            self.assertEqual(broken["external"]["state"], "MISMATCH")
            if broken["attest"]["state"] != "UNAVAILABLE":
                self.assertEqual(broken["attest"]["state"], "FAILED")
            ledger.ledger_path.write_text(original, encoding="utf-8")

            # Roll the local ledger back by one entry: the export still has both.
            ledger.ledger_path.write_text(lines[0] + "\n", encoding="utf-8")
            rolled = ledger.verify()
            self.assertEqual(rolled["state"], "OK")
            self.assertEqual(rolled["external"]["state"], "ROLLED_BACK")
            ledger.ledger_path.write_text(original, encoding="utf-8")

            # Backfill skips receipts already anchored and adds the missing one.
            canonical = root / "r3.json"
            canonical.write_text('{"receipt":3}', encoding="utf-8")
            rows = [
                {"receipt": {"receiptId": "WL:aaa"}, "canonical_path": str(canonical)},
                {"receipt": {"receiptId": "WL:ccc"}, "canonical_path": str(canonical)},
            ]
            self.assertEqual(ledger.backfill(rows), 1)
            self.assertEqual(ledger.verify(receipts_known=3)["unanchoredReceipts"], 0)
            self.assertEqual(ledger.entries()[2].split("\t")[2], "backfill")

    def test_unsafe_key_mode_is_refused(self) -> None:
        with tempfile.TemporaryDirectory(prefix="worldline-anchor-") as temporary:
            paths = _paths(Path(temporary))
            ledger = AnchorLedger(paths, None)
            ledger.ensure_keys()
            ledger.secret_path.chmod(0o644)
            with self.assertRaises(Exception) as caught:
                ledger.append(action="collapse", receipt_id="WL:x", canonical=b"{}")
            self.assertEqual(getattr(caught.exception, "code", None), "UNSAFE_ANCHOR_KEY")


if __name__ == "__main__":
    unittest.main()
