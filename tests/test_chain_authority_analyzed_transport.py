"""Unrun original chain ABI transport controls, additive to its full value suite.
Uses owned buffers only; no invalid nonnull pointer probes or custody claims.
"""
import ctypes as C
import os
from pathlib import Path
import unittest
from worldline.core import Core, HASH_BYTES
from worldline.chain_authority import _api, _Anchors, _Result, _Row, _digest, REASONS

class AnchorResultAlias(C.Union):
    _fields_ = [('anchors', _Anchors), ('result', _Result)]

class RowResultAlias(C.Union):
    _fields_ = [('row', _Row), ('result', _Result)]

class ChainAnalyzedTransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = Core(Path(os.environ.get('WORLDLINE_CORE_LIB', Path(__file__).resolve().parents[1] / 'lib/libworldline_core.so')))
        cls.replay = _api(cls.core)
        cls.genesis = bytes(HASH_BYTES)

    def anchors(self, head=None):
        return _Anchors(0, _digest(self.genesis), _digest(self.genesis),
                        _digest(self.genesis if head is None else head))

    def test_original_null_and_size_guards(self):
        anchors, result = self.anchors(), _Result()
        empty = (_Row * 0)()
        self.assertNotEqual(self.replay(None, C.sizeof(anchors), empty, 0, 0,
                                       C.byref(result), C.sizeof(result)), 0)
        self.assertNotEqual(self.replay(C.byref(anchors), C.sizeof(anchors), empty, 0, 0,
                                       None, C.sizeof(result)), 0)
        self.assertNotEqual(self.replay(C.byref(anchors), 0, empty, 0, 0,
                                       C.byref(result), C.sizeof(result)), 0)
        self.assertNotEqual(self.replay(C.byref(anchors), C.sizeof(anchors), None, 1, C.sizeof(_Row),
                                       C.byref(result), C.sizeof(result)), 0)

    def test_anchors_are_copied_before_output_alias(self):
        owned = AnchorResultAlias()
        owned.anchors = self.anchors()
        empty = (_Row * 0)()
        self.assertEqual(self.replay(C.byref(owned), C.sizeof(_Anchors), empty, 0, 0,
                                    C.byref(owned), C.sizeof(_Result)), 0)
        self.assertEqual(REASONS[owned.result.disposition], 'READY')
        self.assertEqual(bytes(owned.result.head), self.genesis)
        self.assertEqual(owned.result.accepted_count, 0)

    def test_row_is_copied_before_output_alias(self):
        payload = self.core.hash_bytes(b'original chain transport alias specimen')
        head = self.core.receipt_link(self.genesis, payload)
        owned = RowResultAlias()
        owned.row = _Row(_digest(self.genesis), _digest(payload), _digest(payload), _digest(head))
        anchors = self.anchors(head)
        self.assertEqual(self.replay(C.byref(anchors), C.sizeof(anchors), C.byref(owned), 1, C.sizeof(_Row),
                                    C.byref(owned), C.sizeof(_Result)), 0)
        self.assertEqual(REASONS[owned.result.disposition], 'READY')
        self.assertEqual(bytes(owned.result.head), head)
        self.assertEqual(owned.result.accepted_count, 1)
