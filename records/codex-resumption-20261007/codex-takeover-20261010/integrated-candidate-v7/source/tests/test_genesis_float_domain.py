"""Additive producer/native controls; no mock, authorized flag or fallback.

All arithmetic below creates oracle INPUTS or obtains actual original producer
outputs. It is not a Python authority path. Parent enrolls this module unchanged
in the same-source guarded runtime campaign and retains terminal/raw evidence.
"""
from __future__ import annotations

import ast
import ctypes as C
from fractions import Fraction
import hashlib
import importlib
import inspect
import json
import math
import os
from pathlib import Path
import random
import struct
import sys
import textwrap
import unittest

from worldline import protected_startup as producer
from worldline import root_worker_codec as codec
from worldline import resource_scoped_run_ledger as scoped
from worldline.operation_capture import archive as original_archive


class GenesisFloatDomainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pins = json.loads(Path(__file__).with_name('genesis_float_producer_pins.json').read_text())
        if list(sys.version_info[:3]) != pins['python_version']:
            raise AssertionError('pinned original Python producer version differs')
        for pin in pins['files']:
            path = Path(pin['path'])
            if hashlib.sha256(path.read_bytes()).hexdigest() != pin['sha256']:
                raise AssertionError(f'pinned producer identity differs: {path}')
        if Path(sys.executable).resolve() != Path('/usr/bin/python3.14').resolve():
            raise AssertionError('runtime is not the pinned Python executable')
        import _json
        expected_accelerator = '/usr/lib/python3.14/lib-dynload/_json.cpython-314-aarch64-linux-gnu.so'
        if Path(_json.__file__).resolve() != Path(expected_accelerator).resolve():
            raise AssertionError('actual accelerated JSON producer differs')
        if (sys.float_info.radix, sys.float_info.mant_dig, sys.float_info.max_exp,
                sys.float_info.min_exp, sys.float_info.rounds) != (2, 53, 1024, -1021, 1):
            raise AssertionError('pinned binary64 nearest-rounding producer premise differs')
        for pin in pins['functions']:
            function = getattr(importlib.import_module(pin['module']), pin['name'])
            node = ast.parse(textwrap.dedent(inspect.getsource(function))).body[0]
            digest = hashlib.sha256(ast.dump(node, include_attributes=False).encode()).hexdigest()
            if digest != pin['ast_sha256']:
                raise AssertionError(f'original producer function changed: {pin["module"]}.{pin["name"]}')
        library = Path(os.environ.get('WORLDLINE_CORE_LIB',
            str(Path(__file__).resolve().parents[1] / 'lib/libworldline_core.so'))).resolve(strict=True)
        cls.library = C.CDLL(str(library), use_errno=True)
        cls.decimal = cls.library.wl_decimal_binary64_v1
        cls.decimal.argtypes = [C.c_uint8, C.c_void_p, C.c_size_t, C.c_void_p, C.c_size_t]
        cls.decimal.restype = C.c_int
        cls.genesis = cls.library.wl_genesis_archive_matches_v1
        cls.genesis.argtypes = [C.c_void_p, C.c_size_t] + [C.c_int64] * 4
        cls.genesis.restype = C.c_int
        cls.operation = cls.library.wl_operation_archive_json_matches_v1
        cls.operation.argtypes = [C.c_void_p, C.c_size_t, C.c_void_p, C.c_size_t]
        cls.operation.restype = C.c_int
        cls.scoped = cls.library.wl_scoped_archive_json_matches_v1
        cls.scoped.argtypes = cls.operation.argtypes
        cls.scoped.restype = C.c_int

    def native_decimal(self, token: bytes, *, canonical: bool):
        # Exclusive separate allocations stay strongly referenced and unchanged
        # through the synchronous call. No aliases, concurrent mutation or UAF.
        data = C.create_string_buffer(token, max(1, len(token)))
        output = (C.c_uint8 * 8)(*([0xA5] * 8))
        before = bytes(data)
        code = self.decimal(int(canonical), data, len(token), output, C.sizeof(output))
        self.assertEqual(bytes(data), before, 'native conversion modified read-only input')
        self.assertIn(code, (0, 1))
        if code:
            self.assertEqual(bytes(output), b'\xa5' * 8, 'refusal mutated output')
        return code, bytes(output)

    def differential(self, token: bytes, *, canonical: bool):
        try:
            value = producer.exact_json(token, canonical_required=canonical)
            accepted = type(value) is float and math.isfinite(value)
        except (producer.StartupRefusal, ValueError, UnicodeError, OverflowError):
            accepted, value = False, None
        # A trailing LF is a GENESIS file convention, not float repr spelling.
        if canonical and token.endswith(b'\n'):
            accepted = False
        code, bits = self.native_decimal(token, canonical=canonical)
        self.assertEqual(code == 0, accepted, token[:160])
        if accepted:
            self.assertEqual(bits, struct.pack('!d', value), token[:160])

    def correspondence(self, raw: bytes, value, *, encoded=None):
        row = codec.archive(value) if encoded is None else encoded
        data_bytes = raw + row
        data = C.create_string_buffer(data_bytes, max(1, len(data_bytes)))
        before = bytes(data)
        code = self.genesis(data, len(data_bytes), 1, len(raw), len(raw) + 1, len(row))
        self.assertEqual(bytes(data), before, 'native correspondence modified DATA')
        self.assertIn(code, (0, 1, 2, 3))
        return code

    def operation_correspondence(self, raw: bytes, archive: bytes):
        # Separate original allocations, no concatenation/doubled extent cap.
        json_data = C.create_string_buffer(raw, max(1, len(raw)))
        archive_data = C.create_string_buffer(archive, max(1, len(archive)))
        before_json, before_archive = bytes(json_data), bytes(archive_data)
        code = self.operation(json_data, len(raw), archive_data, len(archive))
        self.assertEqual(bytes(json_data), before_json)
        self.assertEqual(bytes(archive_data), before_archive)
        self.assertIn(code, (0, 1))
        return code

    def separate_scoped_correspondence(self, raw: bytes, value, *, encoded=None):
        archive = codec.archive(value) if encoded is None else encoded
        json_data = C.create_string_buffer(raw, max(1, len(raw)))
        archive_data = C.create_string_buffer(archive, max(1, len(archive)))
        before_json, before_archive = bytes(json_data), bytes(archive_data)
        code = self.scoped(json_data, len(raw), archive_data, len(archive))
        self.assertEqual(bytes(json_data), before_json)
        self.assertEqual(bytes(archive_data), before_archive)
        self.assertIn(code, (0, 1, 2, 3))
        return code

    @staticmethod
    def from_bits(bits):
        return struct.unpack('!d', bits.to_bytes(8, 'big'))[0]

    @staticmethod
    def exact_decimal(value: Fraction):
        # Binary rationals have terminating decimal expansions. This computes
        # exact oracle input bytes, not an expected native conversion answer.
        negative = value < 0
        value = abs(value)
        denominator = value.denominator
        twos = 0
        while denominator % 2 == 0:
            denominator //= 2
            twos += 1
        if denominator != 1:
            raise AssertionError('test input is not a binary rational')
        digits = str(value.numerator * 5 ** twos)
        if twos:
            digits = digits.zfill(twos + 1)
            token = digits[:-twos] + '.' + digits[-twos:]
        else:
            token = digits + '.0'
        return (('-' if negative else '') + token).encode('ascii')

    def test_original_shortest_values_every_binary_binade(self):
        # Covers every finite exponent field, both signs, exact powers of two,
        # odd mantissas, and the value immediately preceding a binade boundary.
        for exponent in range(2047):
            for fraction in (0, 1, (1 << 52) - 1):
                for sign in (0, 1 << 63):
                    bits = sign | (exponent << 52) | fraction
                    value = self.from_bits(bits)
                    token = producer.canonical(value)
                    with self.subTest(bits=f'{bits:016x}'):
                        self.differential(token, canonical=True)
        rng = random.Random(0x574C464C4F4154)
        for _ in range(1024):
            bits = rng.getrandbits(64)
            if (bits >> 52) & 2047 == 2047:
                continue
            with self.subTest(random_bits=f'{bits:016x}'):
                self.differential(producer.canonical(self.from_bits(bits)), canonical=True)

    def test_nearest_even_halfway_underflow_and_overflow(self):
        neighbours = {0, 1, 2, (1 << 52) - 1, 1 << 52,
                      (0x7FE << 52) | ((1 << 52) - 2),
                      (0x7FE << 52) | ((1 << 52) - 1)}
        for exponent in (1, 2, 1022, 1023, 1024, 2045, 2046):
            neighbours.update((exponent << 52) | fraction
                              for fraction in (0, 1, (1 << 52) - 2, (1 << 52) - 1))
        for bits in sorted(neighbours):
            low = Fraction.from_float(self.from_bits(bits))
            high = (Fraction(1 << 1024) if bits == 0x7FEFFFFFFFFFFFFF
                    else Fraction.from_float(self.from_bits(bits + 1)))
            halfway = (low + high) / 2
            # Perturbation is exact and stays strictly between the neighbours.
            epsilon = (high - low) / (1 << 80)
            for operand in (halfway - epsilon, halfway, halfway + epsilon):
                for signed in (operand, -operand):
                    token = self.exact_decimal(signed)
                    with self.subTest(neighbour=f'{bits:016x}', token=token[:60]):
                        self.differential(token, canonical=False)
                        self.differential(token, canonical=True)

    def test_unbounded_tokens_and_cancelling_exponents(self):
        n = 10000
        tokens = (
            b'1' + b'0' * n + b'e-' + str(n).encode(),
            b'0.' + b'0' * n + b'1e+' + str(n).encode(),
            b'1.0e-' + b'9' * n,
            b'-1.0e-' + b'9' * n,
            b'1.0e+' + b'9' * n,
            b'0.0e+' + b'9' * n,
            b'-0.0e-' + b'9' * n,
            b'1.0e+' + b'0' * n + b'0',
            b'1.00000000000000011102230246251565404236316680908203125',
            b'1.00000000000000033306690738754696212708950042724609375',
            b'2.2250738585072014e-308', b'2.2250738585072011e-308',
            b'4.9406564584124654e-324', b'2.4703282292062327e-324',
            b'1.7976931348623157e+308', b'1.7976931348623159e+308')
        for token in tokens:
            with self.subTest(token=token[:120], length=len(token)):
                self.differential(token, canonical=False)
                self.differential(token, canonical=True)

    def test_canonical_spelling_and_malformed_original_domain(self):
        tokens = (b'0.0', b'-0.0', b'1.0', b'-1.0', b'0.0001', b'1e-05',
                  b'1000000000000000.0', b'1e+16', b'1e+23', b'1e+20',
                  b'1.0e+20', b'1E+20', b'1e20', b'1e+020', b'1e-5',
                  b'0e0', b'-0e0', b'-0', b'1', b'1.00', b'1e0',
                  b' 1.0', b'1.0 ', b'+1.0', b'01.0', b'.1', b'1.',
                  b'1e', b'1e+', b'1e-', b'--1.0', b'1.0x', b'1.0\x00',
                  b'NaN', b'Infinity', b'-Infinity', b'nan', b'inf',
                  b'[]', b'{}', b'true', b'null', b'', b'1.0\n')
        for token in tokens:
            with self.subTest(token=token):
                # Python json.loads admits surrounding whitespace but the
                # native decimal unit consumes exactly one number token.
                if not token or token.strip() == token:
                    self.differential(token, canonical=False)
                self.differential(token, canonical=True)

    def test_nested_tree_type_signed_zero_unicode_order_and_lf(self):
        value = {'z': [0.0, -0.0, 0, True, None, {'\U0001f40d': [1e-5, 1e23]}],
                 '\n': {'\u00e9': '\x00\b\t\n\f\r', '\u03bb': 5e-324},
                 'boundary': [self.from_bits(0x0010000000000000),
                              self.from_bits(0x7FEFFFFFFFFFFFFF)]}
        raw = producer.canonical(value)
        parsed = producer.exact_json(raw)
        self.assertEqual(self.correspondence(raw, parsed), 3)
        self.assertEqual(self.correspondence(raw + b'\n', parsed), 3)
        self.assertEqual(self.correspondence(raw + b'\n\n', parsed), 0)
        self.assertEqual(self.correspondence(raw + b' ', parsed), 0)
        self.assertEqual(self.correspondence(b' ' + raw, parsed), 0)
        for raw, parsed in ((b'0.0', 0), (b'0', 0.0), (b'-0.0', 0.0),
                            (b'0.0', -0.0), (b'1.0', 1), (b'1', 1.0)):
            with self.subTest(raw=raw, value=repr(parsed)):
                self.assertEqual(self.correspondence(raw, parsed), 2)
        for raw in (b'{"z":0.0,"a":1.0}', b'{"a":0.0,"a":1.0}',
                    b'[1e-5]', b'{"a":1.00}', b'[-0]', b'[1e9999]',
                    b'[[NaN]]', b'{"a":Infinity}'):
            with self.subTest(noncanonical=raw):
                self.assertEqual(self.correspondence(raw, {}), 0)

    def test_exact_float_archive_bit_join_and_malformed_rows(self):
        good = scoped.record(-0.0)
        self.assertEqual(good, {'type': 'float', 'bits': '8000000000000000'})
        for changed in ({'type': 'float', 'bits': '0000000000000000'},
                        {'type': 'float', 'bits': '7ff0000000000000'},
                        {'type': 'float', 'bits': '7ff8000000000000'},
                        {'type': 'integer', 'negative': False, 'magnitude': ''}):
            with self.subTest(row=changed):
                self.assertEqual(self.correspondence(b'-0.0', -0.0,
                    encoded=original_archive(changed)), 2)
        for changed in ({'type': 'float', 'bits': '800000000000000'},
                        {'type': 'float', 'bits': '80000000000000000'},
                        {'type': 'float', 'bits': '7FF0000000000000'},
                        {'type': 'float', 'bits': 'x000000000000000'},
                        {'type': 'float', 'bits': 0},
                        {'type': 'float', 'bits': good['bits'], 'extra': 1}):
            with self.subTest(malformed=changed):
                self.assertEqual(self.correspondence(b'-0.0', -0.0,
                    encoded=original_archive(changed)), 1)

    def test_original_complete_record_projection_across_separate_arrays(self):
        values = (None, False, True, 0, 1, -1, 0.0, -0.0, 1.0, 5e-324,
                  self.from_bits(0x7FEFFFFFFFFFFFFF), 1 << 10000,
                  '\u03bb\u00e9\U0001f40d\x00\n',
                  {'z': [-0.0, 0, False, {'\U0001f40d': 1e23}], 'a': 1e-5},
                  (1, -0.0, b'\x00\xff'))
        for value in values:
            complete = producer.canonical(scoped.record(value))
            actual_original = codec.archive(value)
            with self.subTest(value=repr(value)[:100]):
                self.assertEqual(self.operation_correspondence(complete, actual_original), 1)
                self.assertEqual(self.operation_correspondence(complete + b'\n', actual_original), 0)
        # The generic primitive tree relation retains original scalar tags,
        # even where Python == would equate bool/integer/float or signed zeros.
        for value in (None, False, True, 0, -1, 0.0, -0.0, 1.0, 1e23,
                      {'z': 0.0, 'a': -0.0}, [True, 1, 1.0, -0.0]):
            with self.subTest(primitive=repr(value)):
                self.assertEqual(self.operation_correspondence(
                    producer.canonical(value), original_archive(value)), 1)
        for raw, other in ((b'1', True), (b'true', 1), (b'1.0', 1),
                           (b'1', 1.0), (b'-0.0', 0.0), (b'0.0', -0.0),
                           (b'[1,2]', [2, 1]), (b'[]', ()),
                           (b'{}', {'extra': 0}), (b'{"a":1}', {'a': 1, 'b': 2})):
            with self.subTest(raw=raw, other=repr(other)):
                self.assertEqual(self.operation_correspondence(raw, original_archive(other)), 0)
        archive = original_archive({'type': 'float', 'bits': '8000000000000000'})
        for noncanonical in (b' {"bits":"8000000000000000","type":"float"}',
                             b'{"type":"float","bits":"8000000000000000"}',
                             b'{"bits":"8000000000000000","bits":"0000000000000000","type":"float"}'):
            self.assertEqual(self.operation_correspondence(noncanonical, archive), 0)
        self.assertEqual(self.operation_correspondence(b'1.0', b'[]'), 0)

    def test_separate_scoped_journal_original_file_and_typed_tree(self):
        body = {'schemaVersion': 1, 'events': [
            {'z': [-0.0, 1e23, False, {'\U0001f40d': 5e-324}], 'a': 1 << 10000}],
            'nonce': '\x00\n\u03bb'}
        original_envelope = {'body': body, 'mac': 'source-custody-is-separate'}
        original_raw = producer.canonical(original_envelope)
        # Journal load reconstructs the original canonical JSON dict order;
        # scope fields then retain that decoded original order at every depth.
        decoded_original = producer.exact_json(original_raw)
        for raw in (original_raw, original_raw + b'\n'):
            self.assertEqual(self.separate_scoped_correspondence(raw, decoded_original), 3)
            self.assertEqual(self.separate_scoped_correspondence(raw, decoded_original),
                             self.correspondence(raw, decoded_original))
        self.assertEqual(self.separate_scoped_correspondence(
            original_raw + b'\n\n', decoded_original), 0)
        for raw, other in ((b'1.0', 1), (b'-0.0', 0.0), (b'0.0', -0.0),
                           (b'true', 1), (b'[1]', (1,)), (b'[]', [1])):
            self.assertEqual(self.separate_scoped_correspondence(raw, other), 2)
        self.assertEqual(self.separate_scoped_correspondence(b'1.0', 1.0, encoded=b''), 1)
        self.assertEqual(self.separate_scoped_correspondence(b'', 1.0, encoded=b''), 0)

    def test_scoped_canonical_dto_dict_insertion_order_independence(self):
        # Actual canonical encoder sorts keys, while actual codec scope
        # retains constructor insertion order, including nested DTO records.
        dto = {'z': [-0.0, 1e23, {'z': True, 'a': 1, '\U0001f40d': 5e-324}],
               'schemaVersion': 1, 'a': {'origin': 'original', 'epoch': 1 << 10000}}
        raw = producer.canonical(dto)
        self.assertEqual(self.separate_scoped_correspondence(raw, dto), 3)
        self.assertEqual(self.separate_scoped_correspondence(raw + b'\n', dto), 3)
        # The original Genesis API's ordered dictionary guarantee stays
        # intact; the generic source projection does not rewrite its operand.
        self.assertEqual(self.correspondence(raw, dto), 2)
        self.assertEqual(self.correspondence(raw, producer.exact_json(raw)), 3)
        self.assertEqual(self.separate_scoped_correspondence(
            raw, {'schemaVersion': 1, 'a': dto['a']}), 2)
        self.assertEqual(self.separate_scoped_correspondence(
            raw, {**dto, 'extra': None}), 2)
        self.assertEqual(self.separate_scoped_correspondence(
            raw, {**dto, 'schemaVersion': 1.0}), 2)
        self.assertEqual(self.separate_scoped_correspondence(
            b'{"a":0.0,"z":-0.0}', {'z': 0.0, 'a': -0.0}), 2)
        self.assertEqual(self.separate_scoped_correspondence(
            b'[[0.0,-0.0]]', [[-0.0, 0.0]]), 2)

    def test_owned_wire_extent_output_alias_and_readonly_input(self):
        token = C.create_string_buffer(b'1.0', 3)
        output = (C.c_uint8 * 8)(*([0xA5] * 8))
        self.assertEqual(self.decimal(2, token, 3, output, 8), 255)
        self.assertEqual(self.decimal(0, None, 3, output, 8), 255)
        self.assertEqual(self.decimal(0, token, 3, None, 8), 255)
        self.assertEqual(self.decimal(0, token, 3, output, 7), 255)
        alias = C.create_string_buffer(b'1.0' + b'\xa5' * 8, 11)
        before = bytes(alias)
        self.assertEqual(self.decimal(0, alias, 3, alias, 8), 255)
        self.assertEqual(bytes(alias), before)
        self.assertEqual(bytes(output), b'\xa5' * 8)
        self.assertEqual(self.genesis(None, 1, 1, 1, 1, 1), 255)
        self.assertEqual(self.genesis(token, 3, 0, 1, 1, 1), 255)
        self.assertEqual(self.genesis(token, 3, 1, -1, 1, 1), 255)
        self.assertEqual(self.genesis(token, 3, 1, 4, 1, 1), 0)
        # Safe read-only aliasing is allowed; the malformed overlapping row
        # cannot be mistaken for successful typed correspondence.
        self.assertEqual(self.genesis(token, 3, 1, 3, 1, 3), 1)
        self.assertEqual(self.decimal(0, None, 0, output, 8), 1)
        self.assertEqual(self.genesis(None, 0, 1, 0, 1, 0), 0)
        self.assertEqual(self.operation(None, 0, None, 0), 0)
        self.assertEqual(self.operation(None, 1, None, 0), 255)
        self.assertEqual(self.operation(token, 3, None, 1), 255)
        self.assertEqual(self.scoped(None, 0, None, 0), 0)
        self.assertEqual(self.scoped(token, 3, None, 0), 1)
        self.assertEqual(self.scoped(None, 1, None, 0), 255)


if __name__ == '__main__':
    unittest.main()
