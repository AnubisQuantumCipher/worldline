"""Lossless DTO transport controls; decoding is not witness authentication."""
import unittest

from worldline.completion_kernel import BoundValue, CaptureValue
from worldline.errors import WorldlineError
from worldline.finalization_journal import decode, encode
from worldline.model import WorldState
from worldline.recovery_observation import archive, restore_archive


class RecoveryObservationCodecTests(unittest.TestCase):
    def test_full_records_binary_keys_shapes_states_and_absence_round_trip(self):
        bound = BoundValue(b'store', b'subject', b'content', b'run', b'epoch', None)
        capture = CaptureValue(bound, b'producer', b'full raw context', 'COMPLETED', 'PASS')
        original = {b'binary-key': (capture, None, WorldState.VALID),
                    'history': [b'old-failure', b'new-success'], 'empty': {}}
        restored = restore_archive(archive(original))
        self.assertEqual(restored, original)
        self.assertIs(type(restored[b'binary-key']), tuple)
        self.assertIs(type(restored[b'binary-key'][0]), CaptureValue)
        self.assertIs(type(restored[b'binary-key'][0].bound), BoundValue)
        self.assertIs(type(restored['history']), list)

    def test_unknown_record_or_module_does_not_import_or_construct(self):
        for module, name in (('worldline.completion_kernel', 'UnknownValue'),
                             ('operator-supplied-module', 'BoundValue')):
            with self.subTest(module=module, name=name), self.assertRaises(WorldlineError):
                restore_archive(encode(['record', module, name, []]))

    def test_missing_duplicate_or_reordered_record_field_refuses(self):
        bound = BoundValue(b'store', b'subject', b'content', b'run', b'epoch', None)
        tree = decode(archive(bound))
        for changed in (tree[3][:-1], tree[3] + [tree[3][0]], list(reversed(tree[3]))):
            with self.subTest(fields=changed), self.assertRaises(WorldlineError):
                restore_archive(encode([*tree[:3], changed]))

    def test_duplicate_object_key_and_unknown_shape_refuse(self):
        for tree in (['object', [[['atom', b'key'], ['atom', b'value']],
                                [['atom', b'key'], ['atom', b'other']]]],
                     ['atom', {}], ['tuple', {}], ['unknown', None]):
            with self.subTest(tree=tree), self.assertRaises(WorldlineError):
                restore_archive(encode(tree))


if __name__ == '__main__':
    unittest.main()
