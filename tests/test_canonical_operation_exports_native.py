"""Unrun real native conjunction controls using synthetic complete value inputs.
No protected producer, issuer, full custody-v2 fold or startup claim.
"""
import os
from pathlib import Path
from dataclasses import replace
import unittest
from worldline.core import Core, HASH_BYTES
from worldline.canonical_operation_kernel import CanonicalOperationKernel
from worldline.operation_authority_kernel import FIELDS, OPS
from worldline.protected_operations import empty_evidence, quantity, clone
from worldline.resource_run_ledger import (RunContext, RunBinding, RunState,
    RunRow, RunObservation, RunRequest)

class CanonicalOperationExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kernel = CanonicalOperationKernel(Core(Path(os.environ['WORLDLINE_CORE_LIB'])))

    def fixture(self):
        # Operation fixture identities/quantities retain the prior native control
        # vocabulary; resource amount/held/capacity retain original ledger controls.
        ident = bytes([1] * HASH_BYTES)
        binding = dict(action='fork', id=dict.fromkeys(FIELDS, ident.hex()), peer=7,
                       preparer=7, owner=7, target_owner=7, policy_epoch=quantity(0),
                       resource_epoch=quantity(0))
        grant = dict(id=ident.hex(), parent=None, issuer=ident.hex(), instance=ident.hex(),
                     root_set=ident.hex(), policy=ident.hex(), subject=7, owner=7,
                     allowed=[True for _ in OPS], state='ACTIVE', epoch=quantity(0),
                     ceiling=quantity(16), issued_at=quantity(0), expires_at=quantity(16))
        snapshot = dict(binding=binding, grants=[grant],
                        uses=[dict(bound=clone(binding), state='RESERVED')], now=quantity(0),
                        evidence=empty_evidence(), receipts=[], events=[])
        scope = RunContext(universe=b'universe', policy=ident, resource=b'memory', unit=b'bytes',
                           instance=ident, host=b'host', boot=b'boot', authority=b'authority', policy_epoch=0)
        bound = RunBinding(reservation=ident, operation=ident, owner=b'owner', workload=ident,
                           universe_head=ident, capability=ident, grant_use=ident, payload=b'payload',
                           provenance=ident, resource_epoch=0)
        state = RunState(scope=scope, resource_epoch=0, universe_head=ident, ledger_head=b'head',
                         capacity=20, held_total=10, charged_total=0)
        row = RunRow(scope=scope, bound=bound, parent=None, kind='HELD_CAPACITY', state='RESERVED',
                     amount=10, observed_usage=None, planned_unit=None, actual_unit=None,
                     cgroup=None, invocation=None)
        observed = RunObservation(scope=scope, resource_epoch=0, bound=bound, actual_unit=None,
                                  cgroup=None, invocation=None, observation_head=b'observation', observed='UNKNOWN')
        request = RunRequest(kind='RESERVE', scope=scope, expected_epoch=0, expected_ledger_head=b'head',
                             request_id=b'request', reservation=ident, operation_id=ident,
                             requester=b'owner', bound=bound, new_row=None)
        return snapshot, state, (row,), (observed,), request

    def decide(self, values):
        return self.kernel.observe(*values, 7, None)['decision']

    def test_complete_positive_value_conjunction(self):
        self.assertEqual(self.decide(self.fixture()), 'READY')

    def test_revocation_is_native_authority_refusal(self):
        values = self.fixture()
        values[0]['grants'][0]['state'] = 'REVOKED'
        self.assertEqual(self.decide(values), 'AUTHORITY_REFUSED')

    def test_missing_native_roster_is_resource_refusal(self):
        snapshot, state, rows, observed, request = self.fixture()
        self.assertEqual(self.decide((snapshot, state, rows, (), request)), 'RESOURCE_REFUSED')

    def test_requester_split_is_binding_refusal(self):
        snapshot, state, rows, observed, request = self.fixture()
        request = replace(request, requester=b'other')
        self.assertEqual(self.decide((snapshot, state, rows, observed, request)), 'BINDING_MISMATCH')
