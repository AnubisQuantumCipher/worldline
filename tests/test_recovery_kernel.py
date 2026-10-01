"""Ordinary real-library marker selection and isolated action dispatch.

Finite controls only; marker custody, protected effects, crash recovery and the
complete recovery state-machine proof remain separate required obligations.
"""
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from worldline.core import Core
from worldline.errors import CoreUnavailable, WorldlineError
from worldline.recovery_kernel import select_action
from worldline.transaction import CollapseTransaction


class RecoveryKernelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = Core(Path(os.environ['WORLDLINE_CORE_LIB']))

    def test_original_marker_relation_in_the_real_library(self):
        cases = [
            ('ordinary', 'ordinary', None, 'FINISH_COMMITTED'),
            ('ordinary', 'ordinary', 'other', 'FINISH_COMMITTED'),
            ('ordinary', None, 'ordinary', 'ABORT_PREPARED'),
            ('ordinary', 'other', 'ordinary', 'ABORT_PREPARED'),
            ('ordinary', 'ordinary', 'ordinary', 'AMBIGUOUS'),
            ('ordinary', None, None, 'AMBIGUOUS'),
            ('ordinary', 'other', 'other', 'AMBIGUOUS'),
            ('', '', None, 'FINISH_COMMITTED'),
            ('', None, '', 'ABORT_PREPARED'),
            ('', '', '', 'AMBIGUOUS'),
            ('世界', '世界', None, 'FINISH_COMMITTED'),
            ('\ud800', None, '\ud800', 'ABORT_PREPARED'),
            ('\ud800', '\ufffd', None, 'AMBIGUOUS'),
        ]
        for expected, live, prepared, action in cases:
            with self.subTest(expected=repr(expected), live=repr(live), prepared=repr(prepared)):
                self.assertEqual(select_action(expected, live, prepared, core=self.core), action)

    def test_missing_kernel_has_no_python_selector_fallback(self):
        with self.assertRaises(CoreUnavailable):
            select_action('ordinary', 'ordinary', None, core=SimpleNamespace(_lib=object()))

    def context(self, live, prepared, *, core=None):
        record = {'preparedMapping': 'prepared'}
        value = SimpleNamespace(
            core=self.core if core is None else core,
            paths=SimpleNamespace(live=Path('live')),
            _load_record=Mock(return_value=record),
            _marker=Mock(side_effect=[live, prepared]),
            _finish_committed=Mock(return_value={'state': 'COMMITTED'}),
            _set_state=Mock())
        return value, record

    def test_finish_uses_the_kernel_action(self):
        context, record = self.context('ordinary', None)
        self.assertEqual(CollapseTransaction._recover_one(context, 'ordinary'), {'state': 'COMMITTED'})
        context._finish_committed.assert_called_once_with(record)
        context._set_state.assert_not_called()

    def test_abort_uses_the_kernel_action(self):
        context, record = self.context(None, 'ordinary')
        self.assertEqual(CollapseTransaction._recover_one(context, 'ordinary'),
                         {'transactionId': 'ordinary', 'state': 'ABORTED'})
        context._set_state.assert_called_once_with(record, 'ABORTED',
                                                  error={'code': 'RECOVERED_BEFORE_COMMIT'})
        context._finish_committed.assert_not_called()

    def test_ambiguous_markers_perform_no_action(self):
        context, _ = self.context('ordinary', 'ordinary')
        with self.assertRaises(WorldlineError) as caught:
            CollapseTransaction._recover_one(context, 'ordinary')
        self.assertEqual(caught.exception.code, 'RECOVERY_AMBIGUOUS')
        context._finish_committed.assert_not_called()
        context._set_state.assert_not_called()

    def test_missing_api_performs_no_action(self):
        context, _ = self.context('ordinary', None, core=SimpleNamespace(_lib=object()))
        with self.assertRaises(CoreUnavailable):
            CollapseTransaction._recover_one(context, 'ordinary')
        context._finish_committed.assert_not_called()
        context._set_state.assert_not_called()


if __name__ == '__main__':
    unittest.main()
