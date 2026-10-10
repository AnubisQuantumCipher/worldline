"""Simulation of ordering only: fake symbols/kernel, no owner-custody claim."""
from types import SimpleNamespace
from unittest.mock import patch
import unittest
from worldline import operation_owner_kernel as owner
from worldline.errors import CoreUnavailable


class CanonicalOwnerMappingOrderTests(unittest.TestCase):
    def test_exchange_maps_before_constructor_and_observation(self):
        events = []
        principal = SimpleNamespace(core=object())
        argument = object()
        class Kernel:
            def __init__(self, core):
                self.core = core
                events.append('constructor')
            def observe(self, *args):
                events.append(('observe', args))
                return argument
        def mapped(p, symbols):
            self.assertIs(p, principal)
            self.assertEqual(symbols, owner.RESOURCE_SYMBOLS + owner.EXCHANGE_SYMBOLS)
            events.append('mapped')
        with patch.object(owner, '_owner_mapping', mapped), patch(
                'worldline.canonical_exchange_kernel.CanonicalExchangeKernel', Kernel):
            self.assertIs(owner.observe_exchange(principal, argument), argument)
        self.assertEqual(events, ['mapped', 'mapped', 'constructor', 'mapped',
                                  ('observe', (argument,)), 'mapped'])

    def test_owner_mapping_refusal_prevents_any_constructor_query(self):
        failure = CoreUnavailable('simulated owner mapping failure')
        with patch.object(owner, '_owner_mapping', side_effect=failure), patch(
                'worldline.canonical_owner_completion_kernel.CanonicalOwnerCompletionKernel') as constructor:
            with self.assertRaises(CoreUnavailable) as raised:
                owner.observe_owner_completion(object(), object(), object())
            self.assertIs(raised.exception, failure)
            constructor.assert_not_called()

    def test_owner_complete_argument_objects_and_result_are_retained(self):
        events = []
        principal = SimpleNamespace(core=object())
        historical, current, result = object(), object(), object()
        class Kernel:
            def __init__(self, core):
                self.core = core
                events.append('constructor')
            def observe(self, h, c):
                self_test.assertIs(h, historical)
                self_test.assertIs(c, current)
                events.append('observe')
                return result
        self_test = self
        with patch.object(owner, '_owner_mapping', side_effect=lambda *a: events.append('mapped')), patch(
                'worldline.canonical_owner_completion_kernel.CanonicalOwnerCompletionKernel', Kernel):
            self.assertIs(owner.observe_owner_completion(principal, historical, current), result)
        self.assertEqual(events, ['mapped', 'constructor', 'mapped', 'observe', 'mapped'])
