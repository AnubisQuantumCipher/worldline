"""Prospective real C ABI overlap/refusal controls; no custody acceptance."""
import ctypes as C
import unittest
from worldline.core import Core
from worldline.recovery_protocol_kernel import RecoveryProtocolKernel, Request, Result, STATES, EVENTS

class ProtocolAdapterTransportControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kernel = RecoveryProtocolKernel(Core.shared())

    def test_owned_same_buffer_retains_input_snapshot(self):
        for before, state in enumerate(STATES):
            for cause, event in enumerate(EVENTS):
                expected = self.kernel.advance(state, event)
                request = Request(before, cause)
                # Both original raw fields are captured before the result write.
                status = self.kernel.call(C.byref(request), C.sizeof(request),
                                          C.byref(request), C.sizeof(Result))
                self.assertEqual(status, 0)
                self.assertEqual(request.before, STATES.index(expected))
                self.assertEqual(request.cause, cause)

    def test_malformed_and_shape_refusal_leave_output_untouched(self):
        output = Result(0xa5)
        request = Request(0xff, 0xff)
        status = self.kernel.call(C.byref(request), C.sizeof(request),
                                  C.byref(output), C.sizeof(output))
        self.assertEqual(status, -1)
        self.assertEqual(output.after, 0xa5)
        request = Request(0, 0)
        for pointer, length in ((None, C.sizeof(request)), (C.byref(request), 0)):
            status = self.kernel.call(pointer, length, C.byref(output), C.sizeof(output))
            self.assertEqual(status, -1)
            self.assertEqual(output.after, 0xa5)
        status = self.kernel.call(C.byref(request), C.sizeof(request), None, C.sizeof(output))
        self.assertEqual(status, -1)
        self.assertEqual(output.after, 0xa5)
