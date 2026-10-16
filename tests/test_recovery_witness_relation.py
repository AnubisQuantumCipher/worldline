"""Additive real-library controls for recovery authorization ABI v2.

These finite cases test the pure relation and wire/caller correspondence.
They do not establish protected producers, actual crash consistency, issuer
use ceilings, authentic receipts or independent acceptance. Original recovery
fixtures and their assertions must run unchanged in addition to this module.
"""
from __future__ import annotations

import ctypes as C
from dataclasses import replace
import hashlib
import os
from pathlib import Path
import unittest

from worldline.core import Core
from worldline.recovery_authority_kernel import (
    HASH_FIELDS, MODES, BoundUse, NativeObservation,
    RecoveryAuthorityKernel, Result, binding_record, restore_binding,
)


def identity(label):
    return hashlib.sha256(label.encode('ascii')).digest()


def binding():
    # Synthetic domain controls, not observations or an authentic issuer.
    return BoundUse(mode='CANDIDATE', **{name: identity(name) for name in HASH_FIELDS},
                    policy_epoch=0, resource_epoch=0)


class RecoveryRelationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = Core(Path(os.environ.get('WORLDLINE_CORE_LIB', Path(__file__).resolve().parents[1] / 'lib/libworldline_core.so')))
        cls.kernel = RecoveryAuthorityKernel(cls.core)

    def setUp(self):
        self.issued = binding()
        self.before = NativeObservation(live_mapping=self.issued.before_mapping,
                                        live_root=self.issued.before_root)
        self.after = NativeObservation(live_mapping=self.issued.staged_mapping,
                                       live_root=self.issued.staged_root)

    def observations(self, **changes):
        value = dict(state='ISSUED', issued=self.issued, recovered=self.issued,
                     fresh='AUTHORIZED', historical='UNESTABLISHED',
                     grant_eligible=True, native=self.before)
        value.update(changes)
        return value

    def decide(self, **changes):
        observations = self.observations()
        observations.update(changes)
        return self.kernel.decide(**observations)

    def test_original_before_effect_positive_and_reconcile_paths(self):
        self.assertEqual(self.decide(), ('INVOKE_ACTUATOR', 'CLAIMED'))
        self.assertEqual(self.decide(state='CLAIMED'), ('RECONCILE_ACTUATOR', 'CLAIMED'))

    def test_fresh_denial_or_revocation_prevents_each_before_effect_path(self):
        for state in ('ISSUED', 'CLAIMED'):
            with self.subTest(state=state):
                self.assertEqual(self.decide(state=state, fresh='REFUSED'),
                                 ('ABORT_USE', 'DENIED'))
                self.assertEqual(self.decide(state=state, grant_eligible=False),
                                 ('ABORT_USE', 'DENIED'))

    def test_ob076_settles_historically_authorized_exchange_despite_current_denial(self):
        self.assertEqual(self.decide(state='CLAIMED', native=self.after,
            fresh='REFUSED', grant_eligible=False, historical='HISTORICALLY_AUTHORIZED'),
            ('SETTLE', 'COMPLETED'))

    def test_completed_replay_is_idempotent_and_cannot_authorize_another_exchange(self):
        first = self.decide(state='COMPLETED', native=self.after,
            fresh='REFUSED', grant_eligible=False, historical='HISTORICALLY_AUTHORIZED')
        repeated = self.decide(state=first[1], native=self.after,
            fresh='REFUSED', grant_eligible=False, historical='HISTORICALLY_AUTHORIZED')
        self.assertEqual(first, ('REPLAY', 'COMPLETED'))
        self.assertEqual(repeated, first)
        self.assertEqual(self.decide(state='COMPLETED', native=self.before,
            historical='HISTORICALLY_AUTHORIZED'), ('REFUSE', 'COMPLETED'))

    def test_fresh_permission_cannot_supply_missing_historical_authorization(self):
        for state in ('CLAIMED', 'COMPLETED'):
            with self.subTest(state=state):
                self.assertEqual(self.decide(state=state, native=self.after),
                                 ('REFUSE', state))

    def test_unclaimed_or_denied_use_cannot_settle_observed_effect(self):
        for state in ('ISSUED', 'DENIED'):
            with self.subTest(state=state):
                self.assertEqual(self.decide(state=state, native=self.after,
                    historical='HISTORICALLY_AUTHORIZED'), ('REFUSE', state))

    def test_each_original_and_added_binding_field_mismatch_refuses(self):
        for name in HASH_FIELDS:
            with self.subTest(field=name):
                recovered = replace(self.issued, **{name: identity('substitution-' + name)})
                self.assertEqual(self.decide(recovered=recovered), ('REFUSE', 'ISSUED'))
                self.assertEqual(self.decide(state='CLAIMED', native=self.after,
                    historical='HISTORICALLY_AUTHORIZED', recovered=recovered),
                    ('REFUSE', 'CLAIMED'))
        for name in ('policy_epoch', 'resource_epoch'):
            with self.subTest(field=name):
                self.assertEqual(self.decide(recovered=replace(self.issued, **{name: 1})),
                                 ('REFUSE', 'ISSUED'))
        for mode in MODES:
            if mode != self.issued.mode:
                with self.subTest(mode=mode):
                    self.assertEqual(self.decide(recovered=replace(self.issued, mode=mode)),
                                     ('REFUSE', 'ISSUED'))

    def test_absence_on_either_side_or_both_never_supplies_equality(self):
        for name in HASH_FIELDS + ['policy_epoch', 'resource_epoch']:
            missing = replace(self.issued, **{name: None})
            for issued, recovered in ((missing, self.issued), (self.issued, missing),
                                      (missing, missing)):
                with self.subTest(field=name, issued=issued, recovered=recovered):
                    self.assertEqual(self.decide(issued=issued, recovered=recovered),
                                     ('REFUSE', 'ISSUED'))

    def test_mapping_root_missing_changed_mixed_or_ambiguous_refuses(self):
        invalid = (
            NativeObservation(live_mapping=None, live_root=self.issued.staged_root),
            NativeObservation(live_mapping=self.issued.staged_mapping, live_root=None),
            NativeObservation(live_mapping=identity('foreign'), live_root=self.issued.staged_root),
            NativeObservation(live_mapping=self.issued.staged_mapping, live_root=identity('foreign')),
            NativeObservation(live_mapping=self.issued.before_mapping, live_root=self.issued.staged_root),
        )
        for native in invalid:
            with self.subTest(native=native):
                self.assertEqual(self.decide(state='CLAIMED', native=native,
                    historical='HISTORICALLY_AUTHORIZED'), ('REFUSE', 'CLAIMED'))
        ambiguous = replace(self.issued, staged_mapping=self.issued.before_mapping,
                            staged_root=self.issued.before_root)
        self.assertEqual(self.decide(issued=ambiguous, recovered=ambiguous,
            state='CLAIMED', native=self.before, historical='HISTORICALLY_AUTHORIZED'),
            ('REFUSE', 'CLAIMED'))

    def test_each_promotion_mode_keeps_positive_paths(self):
        for mode in MODES:
            issued = replace(self.issued, mode=mode)
            with self.subTest(mode=mode):
                self.assertEqual(self.decide(issued=issued, recovered=issued),
                                 ('INVOKE_ACTUATOR', 'CLAIMED'))

    def test_present_zero_genesis_is_distinct_from_absence(self):
        issued = replace(self.issued, universe_head=bytes(len(self.issued.universe_head)))
        self.assertEqual(self.decide(issued=issued, recovered=issued),
                         ('INVOKE_ACTUATOR', 'CLAIMED'))

    def test_lossless_binding_transport_keeps_every_field_and_typed_absence(self):
        for value in (self.issued, replace(self.issued, resource_epoch=None),
                      replace(self.issued, kernel_mapping=None)):
            self.assertEqual(restore_binding(binding_record(value)), value)
        raw = binding_record(self.issued)
        del raw['kernel_mapping']
        with self.assertRaises(ValueError):
            restore_binding(raw)

    def test_caller_rejects_unknown_categories_and_noncanonical_epoch_types(self):
        for changes in ({'fresh': 'PASS'}, {'historical': 'AUTHORIZED'},
                        {'state': 'UNKNOWN'}, {'grant_eligible': 1},
                        {'recovered': replace(self.issued, policy_epoch=True)},
                        {'native': 'AFTER_EFFECT'}):
            observations = self.observations()
            observations.update(changes)
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.kernel.decide(**observations)

    def assert_transport_refused_without_output(self, request):
        result = Result(255, 255)
        status = self.kernel.call(C.byref(request), C.sizeof(request),
                                  C.byref(result), C.sizeof(result))
        self.assertEqual(status, -1)
        self.assertEqual(bytes(result), bytes(Result(255, 255)))

    def test_raw_unknown_categories_refuse_without_publishing_a_result(self):
        for field in ('state', 'fresh', 'historical', 'grant_eligible'):
            request = self.kernel.prepare(**self.observations())
            setattr(request, field, 255)
            with self.subTest(field=field):
                self.assert_transport_refused_without_output(request)
        request = self.kernel.prepare(**self.observations())
        request.issued_binding.mode = 255
        self.assert_transport_refused_without_output(request)

    def test_raw_presence_and_absent_payload_are_canonical_for_every_field(self):
        for side in ('issued_binding', 'recovered_binding'):
            for name in HASH_FIELDS + ['policy_epoch', 'resource_epoch']:
                for presence in (0, 255):
                    request = self.kernel.prepare(**self.observations())
                    raw = getattr(getattr(request, side), name)
                    raw.present = presence
                    if name in HASH_FIELDS:
                        raw.value[0] = 1
                    else:
                        raw.value = 1
                    with self.subTest(side=side, field=name, presence=presence):
                        self.assert_transport_refused_without_output(request)
        for name in ('live_mapping', 'live_root'):
            request = self.kernel.prepare(**self.observations())
            raw = getattr(request.native, name)
            raw.present, raw.value[0] = 0, 1
            with self.subTest(native_field=name):
                self.assert_transport_refused_without_output(request)

    def test_real_abi_short_or_unaligned_input_refuses(self):
        request = self.kernel.prepare(**self.observations())
        result = Result(255, 255)
        self.assertEqual(self.kernel.call(C.byref(request), C.sizeof(request) - 1,
            C.byref(result), C.sizeof(result)), -1)
        self.assertEqual(self.kernel.call(C.byref(request, 1), C.sizeof(request),
            C.byref(result), C.sizeof(result)), -1)
        self.assertEqual(bytes(result), bytes(Result(255, 255)))


if __name__ == '__main__':
    unittest.main()
