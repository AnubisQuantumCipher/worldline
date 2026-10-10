"""Unexecuted ordinary callback/domain controls; no authority mocks."""
from pathlib import Path
from types import SimpleNamespace
import unittest
from worldline.transaction import CollapseTransaction
from worldline.revalidate import Revalidator

class StagedCallbackControls(unittest.TestCase):
    def test_existing_five_argument_callback_keeps_objects_and_return(self):
        seen = []
        result = object()
        def callback(*args, **kwargs):
            seen.append((args, kwargs)); return result
        manager = SimpleNamespace(validator=callback, staged_subject_validator=None)
        original = (Path('owned-payload'), object(), object(), object(), 'full-staged-root')
        observed = CollapseTransaction._run_staged_validation(manager, *original, return_of='original-subject')
        self.assertIs(observed, result)
        self.assertEqual(len(seen), 1)
        self.assertEqual(seen[0][1], {})
        self.assertTrue(all(actual is expected for actual, expected in zip(seen[0][0], original)))

    def test_owned_adapter_keeps_vehicle_and_supplies_distinct_full_subject(self):
        seen = []
        result = object()
        def callback(*args, **kwargs):
            seen.append((args, kwargs)); return result
        def legacy(*args, **kwargs):
            self.fail('owned adapter must not also invoke legacy callback')
        manager = SimpleNamespace(validator=legacy, staged_subject_validator=callback)
        vehicle = SimpleNamespace(instance_id='return-vehicle')
        original = (Path('owned-payload'), vehicle, object(), object(), 'full-staged-root')
        self.assertIs(CollapseTransaction._run_staged_validation(manager, *original,
            return_of='original-subject'), result)
        self.assertEqual(len(seen), 1)
        self.assertTrue(all(actual is expected for actual, expected in zip(seen[0][0], original)))
        self.assertEqual(seen[0][1], {'subject_instance': 'original-subject'})

    def test_default_adapter_resolves_actual_store_subject_before_capture(self):
        seen = []
        vehicle, subject = object(), object()
        result = object()
        def lookup(name):
            seen.append(('lookup', name)); return subject
        def capture(*args):
            seen.append(('capture', args)); return result
        adapter = SimpleNamespace(store=SimpleNamespace(world=lookup), _validate_staged_bound=capture)
        payload, before, staged, root = Path('owned-payload'), object(), object(), 'root'
        self.assertIs(Revalidator.validate_staged_for_subject(adapter, payload, vehicle, before, staged, root,
            subject_instance='full-original-subject'), result)
        self.assertEqual(seen[0], ('lookup', 'full-original-subject'))
        self.assertEqual(seen[1][0], 'capture')
        self.assertTrue(all(actual is expected for actual, expected in zip(seen[1][1],
            (payload, subject, before, staged, root))))

    def test_original_staged_method_keeps_original_candidate_object(self):
        seen = []
        def capture(*args): seen.append(args); return 'ordinary-observation'
        adapter = SimpleNamespace(_validate_staged_bound=capture)
        original = (Path('owned-payload'), object(), object(), object(), 'full-root')
        self.assertEqual(Revalidator.validate_staged(adapter, *original), 'ordinary-observation')
        self.assertTrue(all(actual is expected for actual, expected in zip(seen[0], original)))

    def test_checkpoint_refresh_ignores_all_staged_payloads_and_store(self):
        previous = {'mode': 'checkpoint-return'}
        self.assertIs(CollapseTransaction._freshness_after_staged(object(), object(),
            kind='return', return_of='checkpoint', previous=previous, staged=object()), previous)

if __name__ == '__main__':
    unittest.main()
