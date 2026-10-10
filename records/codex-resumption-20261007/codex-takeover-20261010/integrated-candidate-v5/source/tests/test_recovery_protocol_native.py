"""Additive native order controls. No root custody/positive effect claim."""
import unittest
from worldline.core import Core
from worldline.recovery_protocol_kernel import RecoveryProtocolKernel,STATES,EVENTS

class NativeProtocolControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.kernel=RecoveryProtocolKernel(Core.shared())
    def test_positive_effect_settlement_and_replay(self):
        state=self.kernel.advance('ISSUED','FRESH_CLAIM')
        self.assertEqual(state,'EFFECT_INTENT')
        state=self.kernel.advance(state,'HISTORICAL_EFFECT')
        self.assertEqual(state,'EFFECT_OBSERVED')
        state=self.kernel.advance(state,'SETTLEMENT_COMPLETE')
        self.assertEqual(state,'SETTLED')
        self.assertEqual(self.kernel.advance(state,'REPLAY'),'SETTLED')
    def test_no_redispatch_or_unowned_quarantine_escape(self):
        self.assertEqual(self.kernel.advance('EFFECT_INTENT','FRESH_CLAIM'),'EFFECT_INTENT')
        for event in EVENTS:
            if event not in ('OWNER_EFFECT_RESOLUTION','OWNER_NO_EFFECT_RESOLUTION'):
                self.assertEqual(self.kernel.advance('QUARANTINED',event),'QUARANTINED')
    def test_unknown_always_quarantines_and_before_effect_aborts(self):
        for state in STATES:
            self.assertEqual(self.kernel.advance(state,'UNKNOWN_OBSERVATION'),'QUARANTINED')
        self.assertEqual(self.kernel.advance('ISSUED','NO_EFFECT_RELEASED'),'ABORTED')
        self.assertEqual(self.kernel.advance('EFFECT_INTENT','NO_EFFECT_RELEASED'),'ABORTED')
    def test_wire_refuses_noncanonical_categories(self):
        for state,event in ((None,'REPLAY'),('ISSUED',True),('settled','REPLAY'),('ISSUED','unknown')):
            with self.assertRaises(ValueError): self.kernel.advance(state,event)
