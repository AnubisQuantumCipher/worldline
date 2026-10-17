"""Real-library value controls with explicitly synthetic custody/journal values.
No owner, authenticated history, X4 MAC, durable fold or startup acceptance.
Only execute in an admitted checked frame with the complete original roster.
"""
import ctypes as C
import hashlib
from pathlib import Path
import unittest
from worldline.core import Core
from worldline.errors import CoreUnavailable
from worldline.operation_capture import archive
from worldline.root_worker_codec import archive as custody_archive
from worldline.operation_authority_kernel import OperationAuthorityKernel, FIELDS
from worldline.protected_operations import empty_evidence, quantity, clone
from worldline.root_worker_prepared_inputs import PreparedInputs
from worldline.root_worker_prepared_wire import PreparedWire, _prepare_pair
from worldline.custody_prepared_kernel import (
    Span, Root, Event, CustodyValueInput, _symbols, _invoke)
from worldline import operation_authority_kernel as OW

class PreparedStepAbiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = Core(Path(__file__).resolve().parents[1] / 'lib/libworldline_core.so')

    def fixture(self, *, missing_intent=False, revoked=False):
        # Original Operation_Authority_Controls fixture domain/identities.
        ident = bytes([1] * 32).hex()
        bound = dict(action='fork', id=dict.fromkeys(FIELDS, ident), peer=7, preparer=7,
                     owner=7, target_owner=7, policy_epoch=quantity(0), resource_epoch=quantity(0))
        grant = dict(id=ident, parent=None, issuer=ident, instance=ident, root_set=ident,
                     policy=ident, subject=7, owner=7, allowed=[True for _ in OW.OPS],
                     state='REVOKED' if revoked else 'ACTIVE', epoch=quantity(0),
                     ceiling=quantity(16), issued_at=quantity(0), expires_at=quantity(16))
        before = dict(binding=bound, grants=[grant], uses=[], now=quantity(0),
                      evidence=empty_evidence(), receipts=[], events=[])
        intent = clone(before)
        intent['uses'] = [] if missing_intent else [dict(bound=clone(bound), state='RESERVED')]
        record = {}
        base = dict(previous=bytes(32).hex(), generation=b'\x01', operation=ident,
                    subject_kind='ROOT', subject='', subgeneration=b'', kind='PREPARED',
                    actor='FRONT', record=record)
        encoded = custody_archive(base)
        arena = bytearray()
        def span(raw):
            first = len(arena) + 1
            arena.extend(raw)
            return Span(first if raw else 1, len(raw))
        values = dict(event_id=hashlib.sha256(encoded).hexdigest().encode('ascii'),
                      previous=base['previous'].encode('ascii'), generation=base['generation'],
                      operation=ident.encode('ascii'), subject_kind=b'ROOT', subject=b'',
                      subgeneration=b'', kind=b'PREPARED', actor=b'FRONT',
                      record_archive=custody_archive(record), base_archive=encoded, mac=b'')
        event = Event(**{name: span(values[name]) for name, _ in Event._fields_})
        root = Root()
        root.generation = OW.Quantity(1, 0, event.generation.first, event.generation.length)
        root.operation = OW.Quantity(0, 0, 1, 0)
        root.owners_open = 1
        root.reattach_epoch = OW.Quantity(1, 0, 1, 0)
        custody = CustodyValueInput(bytes(arena), bytes(event), bytes(root))
        reserve_raw, intent_raw = archive(before), archive(intent)
        value_encoder = object.__new__(OperationAuthorityKernel)
        data, reserve, intent_wire = _prepare_pair(value_encoder, reserve_raw, intent_raw, custody.prefix)
        # Explicit simulated retained envelope. Private value invocation does
        # not run the authenticated owner wrapper or manufacture provenance.
        retained = PreparedInputs(ident, b'', (), b'', b'', reserve_raw, intent_raw, b'')
        return PreparedWire(retained, data, reserve, intent_wire), custody

    def test_real_layout_and_positive_prepared_value_step(self):
        prepared, custody = self.fixture()
        result = _invoke(_symbols(self.core._lib), prepared, custody)
        self.assertEqual(result.state, 'Prepared_Value_Step_Only')

    def test_missing_intent_refuses_and_preserves_root(self):
        prepared, custody = self.fixture(missing_intent=True)
        result = _invoke(_symbols(self.core._lib), prepared, custody)
        self.assertEqual(result.state, 'Native_Prepared_Refused')

    def test_revoked_grant_refuses_and_preserves_root(self):
        prepared, custody = self.fixture(revoked=True)
        result = _invoke(_symbols(self.core._lib), prepared, custody)
        self.assertEqual(result.state, 'Native_Prepared_Refused')

    def test_unknown_root_phase_transport_refuses(self):
        prepared, custody = self.fixture()
        root = Root.from_buffer_copy(custody.before_root)
        root.phase = 255
        with self.assertRaises(CoreUnavailable):
            _invoke(_symbols(self.core._lib), prepared,
                    CustodyValueInput(custody.prefix, custody.event, bytes(root)))
