"""Simulated DTO controls only; no owner authenticity or startup acceptance."""
import unittest
from worldline.operation_capture import archive
from worldline.operation_authority_kernel import OperationAuthorityKernel
from worldline.protected_operations import empty_binding, empty_evidence, quantity
from worldline.root_worker_prepared_wire import _prepare_pair
from worldline.errors import WorldlineError
from worldline.protected_startup import StartupRefusal
from worldline.evaluation_terminal import TerminalRefused

class PreparedWireValues(unittest.TestCase):
    def setUp(self):
        # prepare is the original pure marshaler; construction normally queries
        # the native layout and remains a separate admitted real-library gate.
        self.kernel = object.__new__(OperationAuthorityKernel)
        self.snapshot = dict(binding=empty_binding(), grants=[], uses=[],
                             now=quantity(0), evidence=empty_evidence(), receipts=[], events=[])

    def test_complete_simulated_snapshot_maps_without_authority(self):
        raw = archive(self.snapshot)
        arena, before, intent = _prepare_pair(self.kernel, raw, raw, b'custody-prefix')
        self.assertTrue(arena.startswith(b'custody-prefix'))
        self.assertEqual(before.counts, (0, 0, 0, 0))
        self.assertEqual(intent.counts, before.counts)
        # Empty binding is encodable but cannot satisfy native PREPARED.
        self.assertEqual(self.snapshot['binding']['owner'], None)

    def test_absent_and_malformed_are_refused(self):
        raw = archive(self.snapshot)
        for invalid in (b'', b'not-an-archive', archive(None), archive({})):
            with self.subTest(raw=invalid), self.assertRaises((WorldlineError, ValueError)):
                _prepare_pair(self.kernel, invalid, raw, b'')

    def test_changed_complete_binding_refused(self):
        raw = archive(self.snapshot)
        self.snapshot['binding']['action'] = 'fork'
        with self.assertRaises(WorldlineError):
            _prepare_pair(self.kernel, raw, archive(self.snapshot), b'')

    def test_internal_refusals_keep_their_cause(self):
        raw = archive(self.snapshot)
        for invalid, cause in ((b'', StartupRefusal),
                               (b'not-an-archive', TerminalRefused)):
            with self.subTest(raw=invalid), self.assertRaises(WorldlineError) as caught:
                _prepare_pair(self.kernel, invalid, raw, b'')
            self.assertEqual(caught.exception.code, 'PREPARED_SNAPSHOT_MALFORMED')
            self.assertIsInstance(caught.exception.__cause__, cause)

    def test_unknown_action_never_defaults(self):
        self.snapshot['binding']['action'] = 'UNKNOWN'
        raw = archive(self.snapshot)
        with self.assertRaises(WorldlineError):
            _prepare_pair(self.kernel, raw, raw, b'')

    def test_present_noncanonical_quantity_refused(self):
        self.snapshot['now'] = dict(negative=False, raw='AA')
        raw = archive(self.snapshot)
        with self.assertRaises(WorldlineError):
            _prepare_pair(self.kernel, raw, raw, b'')
