"""Finite transport simulations; no native/protected authority or startup claim.

Exercises actual _invoke and _pack with owned ctypes arenas and a simulated
native output. Run only in the parent's admitted ordinary control frame.
"""
import ctypes as C
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'runtime'))
from worldline import retained_chain_kernel as K
from worldline.root_worker_retained_inputs import RetainedInputs
from worldline.errors import CoreUnavailable

class Function:
    def __init__(self, call): self.call = call
    def __call__(self, *args): return self.call(*args)

class RetainedObservationControls(unittest.TestCase):
    def inputs(self, rows):
        span = (1, 0)
        return RetainedInputs(b'', span, span, span, (),
                              tuple((span,) * 7 for _ in range(rows)), (),
                              b'', b'', b'')

    def observe(self, status, index, rows):
        def layout(kind, field):
            typ = {1: K._Span, 2: K._Output}[kind]
            values = [C.sizeof(typ), C.alignment(typ)]
            values.extend(getattr(typ, name).offset for name, _ in typ._fields_)
            return values[field]
        def verify(data, size, spans, span_count, genesis, events, heads, output, output_size):
            value = C.cast(output, C.POINTER(K._Output)).contents
            value.status = K._STATES.index(status)
            value.failing_row = index
            value.origin[:] = bytes(range(len(value.origin)))
            value.head[:] = bytes(reversed(range(len(value.head))))
            return 0
        inputs = self.inputs(rows)
        result = K._invoke((Function(lambda: 1), Function(layout), Function(verify)), inputs)
        self.assertIs(result.inputs, inputs)
        self.assertEqual(result.origin, bytes(range(len(result.origin))))
        self.assertEqual(result.head, bytes(reversed(range(len(result.head)))))
        return result

    def test_nonrow_states_keep_zero_location(self):
        for state in K._STATES:
            if state.startswith('Row_'): continue
            with self.subTest(state=state):
                result = self.observe(state, 0, 0)
                self.assertEqual((result.state, result.failing_row), (state, 0))

    def test_every_row_failure_keeps_original_index(self):
        for state in K._STATES:
            if not state.startswith('Row_'): continue
            for index in (1, 2):
                with self.subTest(state=state, index=index):
                    self.assertEqual(self.observe(state, index, 2).failing_row, index)

    def test_row_failure_without_row_refused(self):
        for state in K._STATES:
            if not state.startswith('Row_'): continue
            for rows in (0, 2):
                with self.subTest(state=state, rows=rows):
                    with self.assertRaises(CoreUnavailable): self.observe(state, 0, rows)

    def test_nonrow_failure_and_success_with_row_refused(self):
        for state in K._STATES:
            if state.startswith('Row_'): continue
            with self.subTest(state=state):
                with self.assertRaises(CoreUnavailable): self.observe(state, 1, 2)

    def test_original_out_of_range_refusals_retained(self):
        for index in (-1, 3):
            with self.subTest(index=index):
                with self.assertRaises(CoreUnavailable): self.observe('Row_Mac', index, 2)

if __name__ == '__main__': unittest.main()
