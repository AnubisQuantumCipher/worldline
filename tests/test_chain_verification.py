"""OB-196 and OB-090 (interim): a verification command exits with a distinct nonzero status
whenever anything it verifies is not intact, and chain checks read only the store's own files.

Each case tampers with a store that verified clean, then runs `worldline log --verify` and
`worldline anchor` through the CLI's real `main`, answered by the controller's own handlers.
1.9.1 printed a BROKEN or ROLLED_BACK anchor as data and exited 0, verified a receipt row
re-pointed at a copy outside the store, and read a store whose last anchored receipt was
deleted as complete.
"""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from anchor_support import AnchoredLab

VERIFICATION_FAILED = 3


class VerificationExitsNonzero(unittest.TestCase):
    def setUp(self) -> None:
        self.lab = AnchoredLab(self)
        self.lab.commit("alpha", {"state.txt": "alpha"})
        self.lab.commit("beta", {"state.txt": "beta"})

    def verify_both(self) -> dict[str, tuple[int, str, str]]:
        return {"log": self.lab.cli("log", "--verify", "--json"), "anchor": self.lab.cli("anchor", "--json")}

    def assert_fails_with(self, state: str) -> None:
        for command, (code, out, err) in self.verify_both().items():
            with self.subTest(command=command):
                self.assertEqual(code, VERIFICATION_FAILED, f"{command} exited {code} over a store that is not intact\n{err}")
                self.assertIn(state, out + err, f"{command} did not name {state}")

    def test_an_intact_store_verifies_with_exit_zero(self) -> None:
        for command, (code, out, err) in self.verify_both().items():
            with self.subTest(command=command):
                self.assertEqual(code, 0, f"{command}: {err}\n{out[-2000:]}")

    def test_a_truncated_anchor_tail_exits_nonzero_rolled_back(self) -> None:
        lines = self.lab.ledger_lines()
        (self.lab.paths.state / "anchor.tsv").write_text("".join(line + "\n" for line in lines[:-1]), encoding="utf-8")
        self.assert_fails_with("ROLLED_BACK")

    def test_a_corrupted_signature_exits_nonzero_broken(self) -> None:
        lines = self.lab.ledger_lines()
        fields = lines[0].split("\t")
        fields[8] = ("0" if fields[8][0] != "0" else "1") + fields[8][1:]
        lines[0] = "\t".join(fields)
        (self.lab.paths.state / "anchor.tsv").write_text("".join(line + "\n" for line in lines), encoding="utf-8")
        self.assert_fails_with("BROKEN")

    def test_a_canonical_path_repointed_outside_the_store_exits_nonzero(self) -> None:
        # An IDENTICAL copy, so the only thing wrong is where the row points: 1.9.1 verified it.
        row = self.lab.store.receipts()[-1]
        outside = self.lab.root / "outside"
        outside.mkdir()
        copy = outside / Path(row["canonical_path"]).name
        shutil.copy2(row["canonical_path"], copy)
        connection = self.lab.database()
        connection.execute("UPDATE receipts SET canonical_path=? WHERE receipt_id=?", (str(copy), row["receipt_id"]))
        connection.close()
        self.assert_fails_with("CANONICAL_PATH_OUTSIDE_STORE")

    def test_one_flipped_event_byte_exits_nonzero_with_the_chain_code(self) -> None:
        row = self.lab.database().execute("SELECT canonical_path FROM causal_events ORDER BY rowid DESC LIMIT 1").fetchone()
        path = Path(row["canonical_path"])
        data = bytearray(path.read_bytes())
        position = data.index(b'"worldline"')  # inside a string value: still valid JSON
        data[position + 1] = ord("W")
        path.write_bytes(bytes(data))
        code, out, err = self.lab.cli("log", "--verify", "--json")
        self.assertEqual(code, VERIFICATION_FAILED, err)
        self.assertIn("CAUSAL_CHAIN_INVALID", out)
        code, out, err = self.lab.cli("anchor", "--json")
        self.assertEqual(code, VERIFICATION_FAILED, err)
        self.assertIn("COVERAGE_MISMATCH", out)

    def test_deleting_an_anchored_receipt_is_truncation(self) -> None:
        # OB-090 interim: the last receipt, after it was anchored. The store's own chain is
        # shorter but self-consistent, which 1.9.1 read as complete.
        row = self.lab.store.receipts()[-1]
        connection = self.lab.database()
        connection.execute("DELETE FROM receipts WHERE receipt_id=?", (row["receipt_id"],))
        connection.close()
        Path(row["canonical_path"]).unlink()
        self.assert_fails_with("RECEIPT_CHAIN_TRUNCATED")


if __name__ == "__main__":
    unittest.main()
