"""Real-library complete-row Append/replay controls; custody remains separate."""
import os
from pathlib import Path
from dataclasses import replace
import unittest
from worldline.core import Core, HASH_BYTES
from worldline.chain_authority import ChainAnchors, ChainRow, replay_chain

class NativeChainAuthorityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = Core(Path(os.environ.get('WORLDLINE_CORE_LIB', Path(__file__).resolve().parents[1] / 'lib/libworldline_core.so')))
        cls.genesis = bytes(HASH_BYTES)

    def material(self, kind):
        link = self.core.receipt_link if kind == 'RECEIPT' else self.core.causal_link
        first_root = self.core.hash_bytes(b'first canonical control payload')
        first_head = link(self.genesis, first_root)
        second_root = self.core.hash_bytes(b'second canonical control payload')
        second_head = link(first_head, second_root)
        rows = [ChainRow(self.genesis, first_root, first_root, first_head),
                ChainRow(first_head, second_root, second_root, second_head)]
        return rows, ChainAnchors(kind, self.genesis, self.genesis, second_head)

    def test_full_positive_replay_and_empty_present_genesis(self):
        for kind in ('RECEIPT', 'CAUSAL'):
            rows, anchors = self.material(kind)
            result = replay_chain(rows, anchors, core=self.core)
            self.assertEqual(result.disposition, 'READY')
            self.assertEqual(result.head, anchors.witnessed_head)
            self.assertEqual(result.accepted_count, len(rows))
            empty = replay_chain([], replace(anchors, witnessed_head=self.genesis), core=self.core)
            self.assertEqual(empty.disposition, 'READY')
            self.assertEqual(empty.head, self.genesis)

    def test_deleted_tail_refuses_against_retained_head(self):
        for kind in ('RECEIPT', 'CAUSAL'):
            rows, anchors = self.material(kind)
            result = replay_chain(rows[:-1], anchors, core=self.core)
            self.assertEqual(result.disposition, 'TAIL_MISMATCH')

    def test_independent_anchor_absence_or_genesis_mismatch(self):
        rows, anchors = self.material('RECEIPT')
        for name in ('observed_genesis', 'witnessed_genesis', 'witnessed_head'):
            result = replay_chain(rows, replace(anchors, **{name: None}), core=self.core)
            self.assertEqual(result.disposition, 'ANCHOR_ABSENT')
        different = self.core.hash_bytes(b'different genesis')
        self.assertEqual(replay_chain(rows, replace(anchors, witnessed_genesis=different),
                                     core=self.core).disposition, 'GENESIS_MISMATCH')

    def test_each_required_row_absence_and_actual_payload_substitution(self):
        for kind in ('RECEIPT', 'CAUSAL'):
            rows, anchors = self.material(kind)
            for name in ('previous', 'actual_payload_root', 'stored_payload_root', 'stored_head'):
                altered = [replace(rows[0], **{name: None}), rows[1]]
                self.assertEqual(replay_chain(altered, anchors, core=self.core).disposition, 'ROW_ABSENT')
            changed = self.core.hash_bytes(b'changed canonical bytes')
            altered = [replace(rows[0], actual_payload_root=changed), rows[1]]
            self.assertEqual(replay_chain(altered, anchors, core=self.core).disposition, 'PAYLOAD_MISMATCH')

    def test_native_append_refuses_foreign_predecessor_and_stored_head(self):
        for kind in ('RECEIPT', 'CAUSAL'):
            rows, anchors = self.material(kind)
            different = self.core.hash_bytes(b'foreign chain value')
            altered = [rows[0], replace(rows[1], previous=different)]
            self.assertEqual(replay_chain(altered, anchors, core=self.core).disposition, 'PREDECESSOR_MISMATCH')
            altered = [replace(rows[0], stored_head=different), rows[1]]
            self.assertEqual(replay_chain(altered, anchors, core=self.core).disposition, 'STORED_HEAD_MISMATCH')

if __name__ == '__main__':
    unittest.main()
