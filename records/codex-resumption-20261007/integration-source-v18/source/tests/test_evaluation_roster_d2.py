"""Unexecuted ordinary D2 controls using the real classifier and completion ABI.

All input facts are TEST_ONLY supplied values. No mocks, Python admission
fallback, protected-producer claim, or finite-control proof claim is made.
"""
from dataclasses import replace
import os
from pathlib import Path
import unittest

from worldline.core import (
    Core, EvaluationFacts, EVALUATION_ORIGINS, EVALUATION_STATUSES,
    EVALUATION_CHANNELS, EVALUATION_STAGES, EVALUATION_SUPERVISION,
)
from worldline.completion_kernel import (
    BoundValue, CaptureValue, CheckValue, CompletionKernel, EXECUTION,
)
from worldline.pending_kernel_v2 import Intent


class RequiredFailureControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        library = Path(os.environ['WORLDLINE_CORE_LIB']).resolve(strict=True)
        cls.core = Core(library)
        cls.kernel = CompletionKernel(library)

    def setUp(self):
        # The initial epoch byte is the same ordinary first-epoch input used
        # by the retained completion/pending controls, not a numerical cap.
        self.bound = BoundValue(b'store', b'world', b'content', b'run', b'\x01', b'requirement')
        self.journal = (Intent(self.bound.store_id, self.bound.subject,
            self.bound.content, self.bound.run, self.bound.epoch, None, True,
            self.bound.requirement),)
        self.capture = CaptureValue(self.bound, b'owned-test-input', b'context-input',
                                    'Incomplete_Unknown', None)
        self.declaration = b'engine-declaration'

    def measured(self, check, status):
        facts = EvaluationFacts('engine', status, 'ABSENT', 'ABSENT', False,
            False, 'ABSENT', False, False, False, False, False, False)
        actual = self.core.evaluation_classify(facts)
        self.assertEqual(actual.execution, 'COMPLETED')
        self.assertEqual(actual.outcome, status)
        wire = (EVALUATION_ORIGINS[facts.source], EVALUATION_STATUSES[facts.status],
            EVALUATION_CHANNELS[facts.channel], EVALUATION_STAGES[facts.stage],
            int(facts.exit_present), int(facts.exit_integer),
            EVALUATION_SUPERVISION[facts.supervisor], int(facts.supervisor_stopped),
            int(facts.bundle_present), int(facts.bundle_is_mapping),
            int(facts.bundle_stable), int(facts.bundle_changed),
            int(facts.unsatisfied_imports))
        execution = {name.upper(): name for name in EXECUTION}[actual.execution]
        return CheckValue(self.bound, check, b'owned-test-input', None, None,
            execution, actual.outcome, status.encode('ascii'), wire,
            'NOT_APPLICABLE', (True, True, True, True, True), self.declaration)

    def classify(self, rows):
        original = tuple(rows)
        result = self.kernel.decide(self.journal,
            current=(self.bound.epoch, self.bound.run), capture=self.capture,
            results=original, required=((b'required-check', self.declaration),),
            policy='Required_Checks', measured_roots=(b'same-root', b'same-root'),
            completion=(b'evaluation-complete', self.declaration),
            measured_binding=replace(self.bound))
        self.assertEqual(tuple(rows), original)
        self.assertEqual(result.reason, 'Retain_Terminal')
        self.assertEqual(result.selected, len(self.journal))
        self.assertIsNone(result.summary)
        self.assertIsNotNone(result.classification)
        return result.classification

    def test_required_fail_then_duplicate_pass_with_final_completion(self):
        rows = (self.measured(b'required-check', 'FAIL'),
                self.measured(b'required-check', 'PASS'),
                self.measured(b'evaluation-complete', 'PASS'))
        self.assertEqual(self.classify(rows), ('Completed', 'FAIL', False))

    def test_missing_final_completion_retains_incomplete(self):
        rows = (self.measured(b'required-check', 'FAIL'),
                self.measured(b'required-check', 'PASS'))
        self.assertEqual(self.classify(rows), ('Incomplete_Unknown', None, False))

    def test_nonrequired_failure_is_not_required_failure_latch(self):
        rows = (self.measured(b'unrelated-check', 'FAIL'),
                self.measured(b'required-check', 'PASS'),
                self.measured(b'evaluation-complete', 'PASS'))
        self.assertEqual(self.classify(rows), ('Completed', 'PASS', True))

    def test_original_required_pass_remains_admitted(self):
        rows = (self.measured(b'required-check', 'PASS'),
                self.measured(b'evaluation-complete', 'PASS'))
        self.assertEqual(self.classify(rows), ('Completed', 'PASS', True))


if __name__ == '__main__':
    unittest.main()
