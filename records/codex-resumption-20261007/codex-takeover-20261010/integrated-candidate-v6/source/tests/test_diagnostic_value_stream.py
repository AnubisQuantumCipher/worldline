"""Additive real serializer controls; original target fixture bytes stay fixed."""
import ctypes
from dataclasses import dataclass
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import diagnostic_value_stream as stream
import revalidation_diagnostic as original


@dataclass
class Nested:
    a: object
    b: object


class Abi(ctypes.Structure):
    _fields_ = [('pointer_address', ctypes.c_void_p),
                ('count', ctypes.c_uint32), ('payload', ctypes.c_ubyte * 17)]


class SerializerControls(unittest.TestCase):
    def equal_original(self, value, site='site'):
        # The retained original recursive encoder is a format oracle only.
        # Neither this module nor these tests enter the observed target runtime.
        expected = 'WORLDLINE_DIAGNOSTIC ' + json.dumps(
            {'site': site, 'values': original._owned(value)},
            ensure_ascii=True, allow_nan=False, separators=(',', ':')) + '\n'
        out = io.StringIO()
        stream.write_record(out, site, value)
        self.assertEqual(out.getvalue(), expected)

    def test_complete_original_scalar_container_path_dataclass_grammar(self):
        value = {None: [True, False, 0, -1, 1.5, -0.0, ''],
                 'nested': Nested(a=(b'\0\xff', Path('a\udcff')),
                                  b=Nested(a={'a': '"\\\n\t'}, b=[]))}
        self.equal_original(value)

    def test_full_base64_chunk_boundaries_no_padding_join_change(self):
        for length in [0, 1, 2, 3, stream._BYTE_BLOCK - 1,
                       stream._BYTE_BLOCK, stream._BYTE_BLOCK + 1,
                       stream._BYTE_BLOCK + 2, stream._BYTE_BLOCK * 2 + 5]:
            with self.subTest(length=length):
                self.equal_original(bytes(range(256)) * (length // 256) +
                                    bytes(range(length % 256)))

    def test_whole_unicode_escaping_and_surrogates_across_chunks(self):
        self.equal_original(('a' * (stream._TEXT_BLOCK - 1)) +
                            '\U0001f600\ud800\udfff\"\\\n\0\u2028' +
                            'z' * stream._TEXT_BLOCK)

    def test_complete_owned_abi_snapshot_pointer_address_no_dereference(self):
        val = Abi()
        val.pointer_address = 1
        val.count = 17
        for index in range(17):
            val.payload[index] = index
        self.equal_original({'one': val, 'repeated': [val, val],
                             'array': (ctypes.c_ubyte * 7)(1, 2, 3, 4, 5, 6, 7)})

    def test_invalid_late_value_has_no_partial_row(self):
        out = io.StringIO()
        with self.assertRaises(TypeError):
            stream.write_record(out, 'site', [b'accepted', object()])
        self.assertEqual(out.getvalue(), '')

    def test_nan_refuses_without_partial_row(self):
        out = io.StringIO()
        with self.assertRaises(ValueError):
            stream.write_record(out, 'site', [b'accepted', float('nan')])
        self.assertEqual(out.getvalue(), '')

    def test_cycle_refuses_without_partial_row(self):
        val = []
        val.append(val)
        out = io.StringIO()
        with self.assertRaises(RecursionError):
            stream.write_record(out, 'site', val)
        self.assertEqual(out.getvalue(), '')

    def test_nonstring_site_keeps_original_json_site_semantics(self):
        self.equal_original({'a': b'v'}, site={'arbitrary': [None, 3, 'x']})

    def test_original_record_latches_failure_preserves_caller_outcome(self):
        before = list(original._refusals)
        try:
            with patch.object(original.sys, 'stderr', io.StringIO()):
                original._record('site', [object()])
            self.assertEqual(original._refusals[:-1], before)
            self.assertTrue(original._refusals[-1].startswith('TypeError:'))
        finally:
            original._refusals[:] = before

    def test_stream_failure_first_error_retained(self):
        class FailedStream:
            def write(self, value):
                raise OSError('retained actual stream failure')
            def flush(self):
                raise AssertionError('write already refused')
        with self.assertRaisesRegex(OSError, 'retained actual stream failure'):
            stream.write_record(FailedStream(), 'site', b'full value')

    def test_captured_stream_writes_are_chunked_with_complete_output(self):
        class CapturedStream(io.StringIO):
            largest_write = 0
            def write(self, value):
                self.largest_write = max(self.largest_write, len(value))
                return super().write(value)
        val = b'\0\xff' * stream._BYTE_BLOCK
        out = CapturedStream()
        stream.write_record(out, 'site', val)
        self.assertLessEqual(out.largest_write, stream._OUTPUT_BLOCK)
        expected = 'WORLDLINE_DIAGNOSTIC ' + json.dumps(
            {'site': 'site', 'values': original._owned(val)}, ensure_ascii=True,
            allow_nan=False, separators=(',', ':')) + '\n'
        self.assertEqual(out.getvalue(), expected)


if __name__ == '__main__':
    unittest.main()
