"""Owned ABI refusal controls only; this module must never exchange directories."""
import ctypes as C
import os
from pathlib import Path
import unittest
from worldline.core import Core
from worldline.canonical_physical import Entry, Request, Witness
from worldline.canonical_exchange_kernel import CanonicalExchangeKernel, Input

class FullPhysicalExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = Core(Path(os.environ.get('WORLDLINE_CORE_LIB', Path(__file__).resolve().parents[1] / 'lib/libworldline_core.so')))

    def test_physical_layout_and_hidden_helpers(self):
        version = self.core._lib.wl_full_physical_version_v1
        version.argtypes, version.restype = [], C.c_uint32
        self.assertEqual(version(), 1)
        layout = self.core._lib.wl_full_physical_layout_v1
        layout.argtypes, layout.restype = [C.c_uint32, C.c_uint32], C.c_long
        for kind, typ in enumerate((Entry, Request, Witness), 1):
            self.assertEqual(layout(kind, 0), C.sizeof(typ))
            self.assertEqual(layout(kind, 1), C.alignment(typ))
            for field, (name, _) in enumerate(typ._fields_, 2):
                self.assertEqual(layout(kind, field), getattr(typ, name).offset)
        for symbol in ('wl_internal_full_physical_version_v1',
                       'wl_internal_full_physical_layout_v1',
                       'wl_internal_full_physical_exchange_v1', 'wl_internal_full_physical_recover_v1',
                       'wl_actuator_exchange', 'wl_actuator_recover'):
            with self.assertRaises(AttributeError):
                getattr(self.core._lib, symbol)

    def test_invalid_descriptor_cannot_exchange_or_modify_witness(self):
        kernel = CanonicalExchangeKernel(self.core)
        for symbol in ('wl_full_physical_exchange_v1', 'wl_full_physical_recover_v1'):
            call = getattr(self.core._lib, symbol)
            call.argtypes = [C.c_int] * 4 + kernel.call.argtypes[:-2] + [C.c_void_p, C.c_size_t, C.c_void_p, C.c_size_t]
            call.restype = C.c_int
            raw, physical, witness = Input(), Request(), Witness()
            witness.exchange_attempted = 1
            original = C.string_at(C.byref(witness), C.sizeof(witness))
            args = [-1] * 4 + [None if typ is C.c_void_p else 0 for typ in kernel.call.argtypes[:-2]]
            args[4:6] = [C.byref(raw), C.sizeof(raw)]
            args.extend((C.byref(physical), C.sizeof(physical), C.byref(witness), C.sizeof(witness)))
            self.assertEqual(call(*args), 1)
            self.assertEqual(C.string_at(C.byref(witness), C.sizeof(witness)), original)

    def test_null_actuation_request_is_invalid(self):
        call = self.core._lib.wl_actuation_decide
        call.argtypes, call.restype = [C.c_void_p], C.c_ubyte
        self.assertEqual(call(None), 255)
