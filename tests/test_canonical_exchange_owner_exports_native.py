"""Additive actual-native ABI controls; synthetic owned bytes, no custody claim.
Original full positive/refusal semantic controls are separately retained unchanged.
"""
import ctypes as C
import os
from pathlib import Path
import unittest
from worldline.core import Core
from worldline.canonical_exchange_kernel import CanonicalExchangeKernel, Input as ExchangeInput, Result as ExchangeResult, PHASES
from worldline.canonical_owner_completion_kernel import CanonicalOwnerCompletionKernel, Input as OwnerInput, Result as OwnerResult


class CanonicalExchangeOwnerExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = Core(Path(os.environ.get('WORLDLINE_CORE_LIB', Path(__file__).resolve().parents[1] / 'lib/libworldline_core.so')))

    def families(self):
        # Constructor checks every version, size, alignment and field position,
        # including all underlying original operation/resource/recovery layouts.
        yield CanonicalExchangeKernel(self.core), ExchangeInput, ExchangeResult
        yield CanonicalOwnerCompletionKernel(self.core), OwnerInput, OwnerResult

    def test_complete_layouts(self):
        for kernel, input_type, result_type in self.families():
            self.assertIsNotNone(kernel.call)

    def test_null_nonempty_input_refuses_before_dereference(self):
        for kernel, input_type, result_type in self.families():
            output = result_type(7)
            arguments = [None if typ is C.c_void_p else 0 for typ in kernel.call.argtypes]
            arguments[1] = C.sizeof(input_type)
            arguments[-2:] = [C.byref(output), C.sizeof(output)]
            self.assertEqual(kernel.call(*arguments), -1)
            self.assertEqual(output.disposition, 7)

    def test_owned_invalid_phase_and_output_alias_refuse(self):
        for kernel, input_type, result_type in self.families():
            raw = input_type()
            if input_type is ExchangeInput:
                raw.before = len(PHASES)
            else:
                raw.historical.before = len(PHASES)
            original = C.string_at(C.byref(raw), C.sizeof(raw))
            arguments = [None if typ is C.c_void_p else 0 for typ in kernel.call.argtypes]
            arguments[:2] = [C.byref(raw), C.sizeof(raw)]
            # Input storage is aligned and large enough for the result. All
            # raw decoding must refuse before touching this aliased output.
            arguments[-2:] = [C.byref(raw), C.sizeof(result_type)]
            self.assertEqual(kernel.call(*arguments), -1)
            self.assertEqual(C.string_at(C.byref(raw), C.sizeof(raw)), original)

    def test_nonempty_null_roster_refuses(self):
        for kernel, input_type, result_type in self.families():
            raw = input_type()
            output = result_type(7)
            arguments = [None if typ is C.c_void_p else 0 for typ in kernel.call.argtypes]
            arguments[:2] = [C.byref(raw), C.sizeof(raw)]
            arguments[-2:] = [C.byref(output), C.sizeof(output)]
            # First complete roster: a claimed element with absent bytes.
            arguments[5] = 1
            self.assertEqual(kernel.call(*arguments), -1)
            self.assertEqual(output.disposition, 7)
