"""Unrun real-library value controls; no owner provisioning/startup claim."""
import os
from pathlib import Path
import unittest
from worldline.core import Core, HASH_BYTES
from worldline.operation_authority_kernel import OperationAuthorityKernel, FIELDS, OPS
from worldline.protected_operations import empty_evidence, quantity, clone

class OperationExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = Core(Path(os.environ.get('WORLDLINE_CORE_LIB', Path(__file__).resolve().parents[1] / 'lib/libworldline_core.so')))
        # Actual original constructor also checks every recovery and chain layout.
        cls.kernel = OperationAuthorityKernel(cls.core)

    def snapshot(self):
        ident = bytes([1] * HASH_BYTES).hex()
        binding = dict(action='fork', id=dict.fromkeys(FIELDS, ident), peer=7, preparer=7,
                       owner=7, target_owner=7, policy_epoch=quantity(0), resource_epoch=quantity(0))
        grant = dict(id=ident, parent=None, issuer=ident, instance=ident, root_set=ident,
                     policy=ident, subject=7, owner=7, allowed=[True for _ in OPS],
                     state='ACTIVE', epoch=quantity(0), ceiling=quantity(16),
                     issued_at=quantity(0), expires_at=quantity(16))
        return dict(binding=binding, grants=[grant], uses=[], now=quantity(0),
                    evidence=empty_evidence(), receipts=[], events=[])

    def test_original_reserve_and_replay(self):
        snapshot = self.snapshot()
        self.assertEqual(self.kernel.observe(snapshot, 'RESERVE_USE')['decision'], 'RESERVED_NEW')
        snapshot['uses'] = [dict(bound=clone(snapshot['binding']), state='RESERVED')]
        self.assertEqual(self.kernel.observe(snapshot, 'RESERVE_USE')['decision'], 'RESERVED_REPLAY')

    def test_original_revocation_and_absent_identity_refusals(self):
        snapshot = self.snapshot()
        snapshot['grants'][0]['state'] = 'REVOKED'
        self.assertEqual(self.kernel.observe(snapshot, 'RESERVE_USE')['decision'], 'REFUSED')
        snapshot = self.snapshot()
        snapshot['binding']['id']['operation_id'] = None
        self.assertEqual(self.kernel.observe(snapshot, 'RESERVE_USE')['decision'], 'REFUSED')
