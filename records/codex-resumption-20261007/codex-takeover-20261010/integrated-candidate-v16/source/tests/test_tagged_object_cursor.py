"""Actual native artifact correspondence controls; no custody/proof claim.

These use the existing selected-library fixture helpers. All original tests
remain separate and unchanged. Run only through the reviewed controlled route.
"""
import copy
from dataclasses import replace
import json
import unittest

import test_finalization_kernel as native_fixtures
from worldline.canonical import canonical_bytes
from worldline.completion_kernel import KernelRefused
from worldline.evaluation_terminal import value_bytes


class TaggedObjectCursorControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        native_fixtures.FinalizationNativeControls.setUpClass()

    def setUp(self):
        self.fixture = native_fixtures.FinalizationNativeControls()

    def prepared(self, context):
        capture = replace(self.fixture.capture(), context=value_bytes(context))
        return self.fixture.sealed(capture)

    def changed_context(self, sealed, tagged):
        return replace(sealed, capture=replace(sealed.capture,
            context=canonical_bytes(tagged)))

    def assert_accepted(self, sealed):
        result = self.fixture.kernel.seal(sealed)
        self.assertEqual((result.classification.state,
                          result.classification.outcome,
                          result.classification.promotion),
                         ('Completed', 'PASS', True))

    def test_empty_objects_and_arrays_are_preserved(self):
        for context in ({}, {'empty': {}, 'array': [{}, [], {'nested': {}}]}):
            with self.subTest(context=context):
                self.assert_accepted(self.prepared(context))

    def test_all_pair_orders_match_the_same_artifact(self):
        import itertools
        sealed = self.prepared({'z': 'last', 'a': {'nested': True}, 'm': [None, 7]})
        tagged = json.loads(sealed.capture.context)
        for pairs in itertools.permutations(tagged[1]):
            with self.subTest(order=[pair[0] for pair in pairs]):
                self.assert_accepted(self.changed_context(sealed, ['object', list(pairs)]))

    def test_large_unrelated_value_and_nested_reversed_pairs(self):
        context = {'z-large': 'payload\u0000\u2028é' * 16384,
                   'a-small': {'é': 'unicode', 'a\"\\\n': [None, {}, -7]},
                   'middle': True}
        sealed = self.prepared(context)
        tagged = json.loads(sealed.capture.context)

        def reverse_objects(value):
            if value[0] == 'object':
                value[1].reverse()
                for pair in value[1]:
                    reverse_objects(pair[1])
            elif value[0] == 'array':
                for child in value[1]:
                    reverse_objects(child)

        reverse_objects(tagged)
        self.assert_accepted(self.changed_context(sealed, tagged))

    def test_duplicate_missing_extra_and_malformed_pairs_refuse(self):
        sealed = self.prepared({'a': 'alpha', 'b': {'inside': 'beta'}, 'z': None})
        tagged = json.loads(sealed.capture.context)
        variants = {}
        pairs = copy.deepcopy(tagged[1])
        pairs[1] = copy.deepcopy(pairs[0])
        variants['duplicate-in-place'] = pairs
        variants['missing-last'] = copy.deepcopy(tagged[1][:-1])
        pairs = copy.deepcopy(tagged[1])
        pairs.append(json.loads(value_bytes({'extra': False}))[1][0])
        variants['extra-valid-pair'] = pairs
        pairs = copy.deepcopy(tagged[1])
        pairs[-1].append(['null'])
        variants['extra-pair-field'] = pairs
        pairs = copy.deepcopy(tagged[1])
        pairs[-1].pop()
        variants['missing-pair-value'] = pairs
        pairs = copy.deepcopy(tagged[1])
        pairs[-1] = None
        variants['non-array-pair'] = pairs
        pairs = copy.deepcopy(tagged[1])
        pairs[0][0] = '!invalid-base64!'
        variants['invalid-key'] = pairs
        pairs = copy.deepcopy(tagged[1])
        pairs[0][1] = ['bool', True]
        variants['different-value'] = pairs
        for label, changed in variants.items():
            with self.subTest(case=label):
                with self.assertRaises(KernelRefused):
                    self.fixture.kernel.seal(self.changed_context(sealed,
                        ['object', changed]))

    def test_malformed_or_incomplete_array_bytes_refuse(self):
        sealed = self.prepared({'a': 'alpha', 'b': 'beta'})
        for raw in (sealed.capture.context[:-1],
                    sealed.capture.context + b' ',
                    sealed.capture.context.replace(b'],[', b'][', 1)):
            with self.subTest(raw=raw):
                self.assertNotEqual(raw, sealed.capture.context)
                with self.assertRaises(KernelRefused):
                    self.fixture.kernel.seal(replace(sealed,
                        capture=replace(sealed.capture, context=raw)))


if __name__ == '__main__':
    unittest.main()
