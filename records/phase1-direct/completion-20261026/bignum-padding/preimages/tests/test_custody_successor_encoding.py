"""Real-library encoding controls, not custody authorization or full-domain proof.

Expected quantities are JACKAL exact receipts, outside the Lean certificate chain.
"""
import ctypes as C
import json
import os
from pathlib import Path
import unittest

from worldline.core import Core


class CustodySuccessorEncoding(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = Core(Path(os.environ['WORLDLINE_CORE_LIB']))
        cls.function = cls.core._lib.wl_custody_successor_le_v2
        cls.function.argtypes = [C.c_void_p, C.c_size_t, C.c_void_p,
                                 C.c_size_t, C.POINTER(C.c_uint64)]
        cls.function.restype = C.c_int
        path = Path(__file__).parent / 'fixtures/custody-successor-oracles-v1.json'
        cls.cases = json.loads(path.read_text())['cases']

    def test_exact_oracles_sizing_truncation_padding_and_owned_bounds(self):
        for case in self.cases:
            receipt = case['receipt']['structuredContent']
            self.assertEqual(receipt['status'], 'exact')
            self.assertFalse(receipt['formal'])
            self.assertEqual(receipt['fields']['parsed'], case['expression'])
            number = int(receipt['fields']['exact'])
            expected = number.to_bytes((number.bit_length() + 7) // 8, 'little')
            for zeros in (0, 1, 4096):
                raw = bytes.fromhex(case['input_hex']) + bytes(zeros)
                for capacity in sorted({0, len(expected)-1, len(expected), len(expected)+3}):
                    with self.subTest(expression=case['expression'], zeros=zeros,
                                      capacity=capacity):
                        self.check_call(raw, expected, capacity)

    def check_call(self, raw, expected, capacity):
        data = (C.c_ubyte * len(raw)).from_buffer_copy(raw)
        storage = (C.c_ubyte * (capacity + 2))(*([165] * (capacity + 2)))
        needed = C.c_uint64(999)
        code = self.function(data if raw else None, len(raw),
                             C.byref(storage, 1) if capacity else None,
                             capacity, C.byref(needed))
        self.assertEqual(code, 3 if 0 < capacity < len(expected) else 0)
        self.assertEqual(needed.value, len(expected))
        self.assertEqual(bytes(data), raw)
        self.assertEqual(storage[0], 165)
        self.assertEqual(storage[-1], 165)
        if capacity:
            self.assertEqual(bytes(storage)[1:-1],
                             expected[:capacity] + bytes(max(0, capacity-len(expected))))


if __name__ == '__main__':
    unittest.main()
