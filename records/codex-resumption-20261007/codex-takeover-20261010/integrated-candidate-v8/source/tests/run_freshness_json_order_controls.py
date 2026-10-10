"""Explicit additive runner for the existing TEST_ONLY producer fixture.

Execute only inside an admitted frame, with its selected runtime/tests on
PYTHONPATH and its matching WORLDLINE_CORE_LIB. Does not replace or discover the
original suite, widen a timeout, or claim production custody/phase acceptance.
"""
from __future__ import annotations

import json
import unittest

from test_raw_evaluation_default import RawRequiredFailureControls
from freshness_json_order_controls import exercise_freshness_json_order_controls


class FreshnessJSONObjectOrderProbe(RawRequiredFailureControls):
    def runTest(self):
        manager, _subject, policy, chosen, _request, _agent = self.producer_case()
        result = exercise_freshness_json_order_controls(
            manager.core, chosen.context, policy)
        result['input_kind'] = 'unchanged-original-TEST_ONLY-producer_case'
        result['production_custody_established'] = False
        print('FRESHNESS_JSON_ORDER_RESULT ' + json.dumps(result, sort_keys=True),
              flush=True)


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('native regression controls require assertions enabled')
    # Explicitly run this additive probe only. The lead must run its original
    # unchanged suite separately under the original roster and limits.
    suite = unittest.TestSuite([FreshnessJSONObjectOrderProbe('runTest')])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
