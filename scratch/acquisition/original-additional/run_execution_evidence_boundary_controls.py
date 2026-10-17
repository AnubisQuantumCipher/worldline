"""Explicit additive evidence-observation controls, unexecuted by the author.

Run only in a separately qualified frame with its selected runtime/tests on
PYTHONPATH and matching WORLDLINE_CORE_LIB. The unchanged original producer_case
and staged_journal supply all subject, agent, store and selected-row inputs.
These ordinary fixtures establish no protected production custody. No original
case, assertion, suite discovery, deadline or operator boundary is replaced.
"""
from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
import json
import unittest

from test_raw_evaluation_default import RawRequiredFailureControls
from worldline.evaluation_authority import read
from worldline.transaction import CollapseTransaction
from worldline.transaction_relation import execution

if not __debug__:
    raise RuntimeError('evidence boundary controls require original assertions enabled')


class _ReplacementMapping(Mapping):
    """An admitted input protocol, not a mock of any producer or native call."""

    def __init__(self, subject, replacement, trigger):
        self._payload = {'id': 'ordinary-evidence-boundary-extra'}
        self._subject = subject
        self._replacement = replacement
        self._trigger = trigger
        self.replaced = False

    def _replace(self, trigger):
        if self._trigger == trigger and not self.replaced:
            self._subject.evidence = self._replacement
            self.replaced = True

    def __getitem__(self, key):
        return self._payload[key]

    def __iter__(self):
        self._replace('row-copy')
        return iter(self._payload)

    def __len__(self):
        return len(self._payload)

    def get(self, key, default=None):
        if key == 'id':
            self._replace('id-lookup')
        return self._payload.get(key, default)


class ExecutionEvidenceBoundaryProbe(RawRequiredFailureControls):
    def _replacement_control(self, trigger):
        with self.staged_journal() as (manager, subject, policy, previous, _append, _terminal):
            # The original setup must actually succeed before this negative is
            # exercised. Do not skip its reader/freshness/native calls.
            self.assertTrue(previous['execution']['complete'])
            selected = read(manager.store, subject, policy['requirementHash'],
                            prepared=previous['evaluationCursor'], core=self.core)
            original = subject.evidence
            replacement = deepcopy(original)
            first_agent = next(row for row in replacement['checks']
                               if isinstance(row, Mapping) and row.get('id') == 'agent')
            # A negative mutation of the original fixture's actual input, not a
            # new successful agent or a selected-policy substitute for it.
            first_agent.update(status='FAIL', exitCode=1)
            # The identical extra Mapping row must not itself explain refusal.
            baseline_row = _ReplacementMapping(subject, replacement, 'never')
            baseline = manager._execution_identity(subject, policy,
                recorded_checks=[*selected.results, baseline_row])
            self.assertFalse(baseline_row.replaced)
            self.assertIs(subject.evidence, original)
            self.assertTrue(baseline['complete'])
            row = _ReplacementMapping(subject, replacement, trigger)
            identity = manager._execution_identity(subject, policy,
                recorded_checks=[*selected.results, row])
            self.assertTrue(row.replaced)
            self.assertIs(subject.evidence, replacement)
            self.assertIsNot(subject.evidence, original)
            self.assertFalse(identity['complete'])

    def _explicit_absence_control(self):
        with self.staged_journal() as (manager, subject, policy, previous, _append, _terminal):
            self.assertTrue(previous['execution']['complete'])
            selected = read(manager.store, subject, policy['requirementHash'],
                            prepared=previous['evaluationCursor'], core=self.core)
            subject.evidence = None
            identity = manager._execution_identity(subject, policy,
                                                   recorded_checks=selected.results)
            self.assertFalse(identity['complete'])

    def _missing_prerequisite_controls(self):
        manager, bare_subject, policy, chosen, _request, _agent = self.producer_case()
        # producer_case intentionally has no evidence attribute. Never fill it
        # with the separately returned ordinary agent wire.
        for label, subject in (('missing-subject', None),
                               ('unchanged-bare-producer', bare_subject)):
            with self.subTest(prerequisite=label, consumer='execution-identity'):
                with self.assertRaises(AttributeError):
                    CollapseTransaction._execution_identity(manager, subject, policy,
                                                            recorded_checks=chosen.results)
            with self.subTest(prerequisite=label, consumer='native-wrapper'):
                with self.assertRaises(AttributeError):
                    execution(self.core, subject, policy, chosen.results)

    def runTest(self):
        self._replacement_control('id-lookup')
        self._replacement_control('row-copy')
        self._explicit_absence_control()
        self._missing_prerequisite_controls()
        print('EXECUTION_EVIDENCE_BOUNDARY_RESULT ' + json.dumps({
            'controls': ['outer-id-lookup-replacement',
                         'helper-row-copy-replacement-before-archive',
                         'existing-subject-explicit-evidence-absence',
                         'missing-subject-errors-in-both-consumers',
                         'unchanged-bare-producer-errors-in-both-consumers'],
            'input_kind': 'unchanged-original-TEST_ONLY-producer_case-and-staged_journal',
            'production_custody_established': False,
        }, sort_keys=True), flush=True)


if __name__ == '__main__':
    # Explicit additive probe only: inherited original tests are not discovered
    # or replaced. Main must preserve and run its entire original suite too.
    suite = unittest.TestSuite([ExecutionEvidenceBoundaryProbe('runTest')])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
