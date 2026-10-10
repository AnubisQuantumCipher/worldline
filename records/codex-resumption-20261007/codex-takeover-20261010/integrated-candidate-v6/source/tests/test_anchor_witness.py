"""The anchor's witness and key pin (1.9.2): OB-083, OB-087, OB-088 and OB-086 (interim).

1.9.1 copied the local ledger over the external one at every start and commit, with no
comparison first, so a rolled-back or rewritten local ledger destroyed the only evidence of
the rollback. It left the export unset by default and anchored receipts only, and a store
rewritten consistently and re-signed with a new key read as intact.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import threading
import time
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

from anchor_support import AnchoredLab
from worldline.errors import WorldlineError

VERIFICATION_FAILED = 3


class WitnessIsNeverOverwritten(unittest.TestCase):
    def test_rollback_is_detected_before_export_and_the_witness_is_unchanged(self) -> None:
        # OB-083. Two commits, a local rollback of the ledger's tail, then a start.
        lab = AnchoredLab(self)
        lab.commit("alpha", {"state.txt": "alpha"})
        lab.commit("beta", {"state.txt": "beta"})
        witness_before = lab.witness.read_bytes()
        lines = lab.ledger_lines()
        self.assertGreaterEqual(len(lines), 2)
        (lab.paths.state / "anchor.tsv").write_text("".join(line + "\n" for line in lines[:-2]), encoding="utf-8")
        lab.restart()
        self.assertEqual(lab.witness.read_bytes(), witness_before, "a start overwrote the witness of a rolled-back ledger")
        code, out, _err = lab.cli("anchor", "--json")
        self.assertEqual(code, VERIFICATION_FAILED)
        self.assertEqual(json.loads(out)["state"], "ROLLED_BACK")
        doctor = lab.controller._doctor({}, lab.context())["anchor"]
        self.assertEqual((doctor["alarm"] or {}).get("code"), "ANCHOR_WITNESS_DISAGREES", doctor)
        with self.assertRaises(WorldlineError) as refused:
            lab.prepare("gamma", {"state.txt": "gamma"})
        self.assertEqual(refused.exception.code, "ANCHOR_WITNESS_DISAGREES")
        self.assertEqual(lab.witness.read_bytes(), witness_before)

    def test_export_failure_at_commit_is_reported(self) -> None:
        # OB-083: 1.9.1 dropped the export's result at commit.
        lab = AnchoredLab(self)
        from worldline.anchor import AnchorLedger
        failed = {"state": "FAILED", "path": str(lab.witness), "reason": "EIO (injected)"}
        with mock.patch.object(AnchorLedger, "export", return_value=failed):
            result = lab.commit("alpha", {"state.txt": "alpha"})
        self.assertEqual(result["state"], "COMMITTED")
        warnings = (result.get("postCommit") or {}).get("warnings") or []
        self.assertTrue(any(item.get("step") == "anchor-export" and "EIO" in json.dumps(item) for item in warnings), result.get("postCommit"))


class AWitnessAlwaysExists(unittest.TestCase):
    def test_no_export_path_refuses_promotion_and_fails_doctor(self) -> None:
        # OB-087: a fresh configuration without anchor.exportPath.
        lab = AnchoredLab(self, witness=False)
        doctor = lab.controller._doctor({}, lab.context())["anchor"]
        self.assertEqual(doctor["state"], "WITNESS_UNCONFIGURED", doctor)
        self.assertTrue(doctor.get("missing"), "doctor must say what to provision")
        with self.assertRaises(WorldlineError) as refused:
            lab.prepare("alpha", {"state.txt": "alpha"})
        self.assertEqual(refused.exception.code, "ANCHOR_WITNESS_UNAVAILABLE")
        self.assertEqual(lab.store.transactions_in_state(("PREPARED",)), [], "a refused prepare created a transaction")

    def test_an_unprotected_witness_refuses_promotion(self) -> None:
        lab = AnchoredLab(self, protected=False)
        with self.assertRaises(WorldlineError) as refused:
            lab.prepare("alpha", {"state.txt": "alpha"})
        self.assertIn(refused.exception.code, ("ANCHOR_WITNESS_UNAVAILABLE", "ANCHOR_KEY_UNPINNED"))

    def test_store_rewrite_is_detected_against_the_witness(self) -> None:
        # OB-087: one receipt rewritten consistently, the count kept. 1.9.1: OK, 0 unanchored.
        lab = AnchoredLab(self)
        lab.commit("alpha", {"state.txt": "alpha"})
        lab.commit("beta", {"state.txt": "beta"})
        lab.rewrite_receipt_consistently(0, lambda receipt: receipt["mergeSet"].update(files=[]))
        self.assertEqual(lab.store.verify_chains()["receipts"], 2, "the rewrite must leave the store's own chain valid")
        code, out, _err = lab.cli("anchor", "--json")
        self.assertEqual(code, VERIFICATION_FAILED)
        self.assertIn("COVERAGE_MISMATCH", out)
        code, _out, _err = lab.cli("log", "--verify", "--json")
        self.assertEqual(code, VERIFICATION_FAILED)


class CausalEventsAreAnchored(unittest.TestCase):
    def test_rewritten_causal_event_fails_anchor_verification(self) -> None:
        # OB-088: a CONSISTENT rewrite (event root and chain recomputed for it and every later
        # event); a one-byte flip is caught by the store's own chain already.
        lab = AnchoredLab(self)
        lab.commit("alpha", {"state.txt": "alpha"})
        connection = lab.database()
        row = connection.execute("SELECT event_id FROM causal_events WHERE kind='collapse-receipt' ORDER BY rowid LIMIT 1").fetchone()
        connection.close()
        lab.rewrite_event_consistently(row["event_id"], lambda event: event.update(reason="rewritten afterwards"))
        self.assertGreater(lab.store.verify_chains()["causalEvents"], 0, "the rewrite must leave the store's own chain valid")
        code, out, _err = lab.cli("anchor", "--json")
        self.assertEqual(code, VERIFICATION_FAILED)
        self.assertIn("CAUSAL_CHAIN_TRUNCATED", out)
        code, _out, _err = lab.cli("log", "--verify", "--json")
        self.assertEqual(code, VERIFICATION_FAILED)

    def test_every_causal_event_is_anchored_by_identity_and_hash(self) -> None:
        lab = AnchoredLab(self)
        lab.commit("alpha", {"state.txt": "alpha"})
        anchored = {line.split("\t")[3]: line.split("\t")[5] for line in lab.ledger_lines()}
        connection = lab.database()
        rows = connection.execute("SELECT event_id,canonical_path FROM causal_events").fetchall()
        connection.close()
        self.assertTrue(rows)
        for row in rows:
            self.assertEqual(anchored.get(row["event_id"]), hashlib.sha256(Path(row["canonical_path"]).read_bytes()).hexdigest())

    def test_concurrent_event_and_receipt_anchoring_do_not_fork_the_ledger(self) -> None:
        # Commit, recovery and agent ingestion (worker threads) all append: seq and prev are read
        # and then written, so two appends at once must not both take the same seq.
        lab = AnchoredLab(self)
        ledger = lab.controller.anchors
        real_time = time.time

        def slow_time() -> float:
            time.sleep(0.02)
            return real_time()

        with mock.patch("worldline.anchor.time.time", side_effect=slow_time):
            threads = [threading.Thread(target=ledger.append, kwargs={"action": "collapse", "receipt_id": f"WL:race-{index}",
                                                                      "canonical": f"{index}".encode()}) for index in range(6)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
        lines = lab.ledger_lines()
        self.assertEqual([line.split("\t")[0] for line in lines], [str(index) for index in range(len(lines))])
        self.assertEqual(ledger.verify()["badChain"], 0)


class RewrittenAndResignedStore(unittest.TestCase):
    def test_rewritten_and_resigned_store_is_mismatch_against_the_witness(self) -> None:
        # OB-086 interim: rewrite the store, re-sign the whole local ledger with a NEW key, start.
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import ed25519
        lab = AnchoredLab(self)
        lab.commit("alpha", {"state.txt": "alpha"})
        lab.commit("beta", {"state.txt": "beta"})
        lab.close()
        witness_before = lab.witness.read_bytes()
        lab.rewrite_receipt_consistently(0, lambda receipt: receipt["mergeSet"].update(files=[]))
        key = ed25519.Ed25519PrivateKey.generate()
        directory = lab.paths.config / "anchor"
        (directory / "secret.key").write_text(key.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw,
                                                                 serialization.NoEncryption()).hex() + "\n", encoding="ascii")
        (directory / "public.hex").write_text(key.public_key().public_bytes_raw().hex() + "\n", encoding="ascii")
        # Re-sign every entry, with the rewritten receipts' hashes, from genesis.
        store_hash = {}
        connection = lab.database()
        for row in connection.execute("SELECT receipt_id,canonical_path FROM receipts"):
            store_hash[row["receipt_id"]] = hashlib.sha256(Path(row["canonical_path"]).read_bytes()).hexdigest()
        connection.close()
        previous = hashlib.sha256(b"custos-genesis-v1").hexdigest()
        rewritten = []
        for index, line in enumerate(lab.ledger_lines()):
            fields = line.split("\t")[:8]
            fields[0] = str(index)
            fields[5] = store_hash.get(fields[3], fields[5])
            fields[7] = previous
            message = ("custos-v1\t" + "\t".join(fields)).encode()
            entry = "\t".join([*fields, key.sign(message).hex()])
            rewritten.append(entry)
            previous = hashlib.sha256(entry.encode()).hexdigest()
        (lab.paths.state / "anchor.tsv").write_text("".join(entry + "\n" for entry in rewritten), encoding="utf-8")
        lab.start()
        self.assertEqual(lab.witness.read_bytes(), witness_before, "the start overwrote the witness")
        verdict = lab.controller._anchor_status({}, lab.context())
        states = {item["state"] for item in verdict["problems"]}
        self.assertIn("MISMATCH", states, verdict["problems"])
        self.assertIn("KEY_MISMATCH", states, verdict["problems"])
        self.assertNotEqual(verdict["state"], "OK")

    def test_a_replaced_key_is_broken_against_the_pin(self) -> None:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import ed25519
        lab = AnchoredLab(self)
        lab.commit("alpha", {"state.txt": "alpha"})
        key = ed25519.Ed25519PrivateKey.generate()
        directory = lab.paths.config / "anchor"
        (directory / "secret.key").write_text(key.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw,
                                                                 serialization.NoEncryption()).hex() + "\n", encoding="ascii")
        (directory / "public.hex").write_text(key.public_key().public_bytes_raw().hex() + "\n", encoding="ascii")
        with self.assertRaises(WorldlineError) as refused:
            lab.controller.anchors.append(action="collapse", receipt_id="WL:forged", canonical=b"{}")
        self.assertEqual(refused.exception.code, "ANCHOR_KEY_MISMATCH")
        # The writer appends an entry signed with the replaced key itself.
        lines = lab.ledger_lines()
        fields = [str(len(lines)), "0", "collapse", "WL:forged", "-", hashlib.sha256(b"{}").hexdigest(), "2",
                  hashlib.sha256(lines[-1].encode()).hexdigest()]
        entry = "\t".join([*fields, key.sign(("custos-v1\t" + "\t".join(fields)).encode()).hex()])
        with (lab.paths.state / "anchor.tsv").open("a", encoding="utf-8") as handle:
            handle.write(entry + "\n")
        verdict = lab.controller._anchor_status({}, lab.context())
        states = {item["state"] for item in verdict["problems"]}
        self.assertEqual(verdict["state"], "BROKEN", verdict["problems"])
        self.assertIn("KEY_MISMATCH", states)


if __name__ == "__main__":
    unittest.main()
