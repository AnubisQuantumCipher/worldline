"""Genuine full raw policy/run mutation controls; source enrollment is UNRUN."""
import copy
import unittest
from worldline.core import Core
from worldline.errors import WorldlineError
from worldline.evaluation_policy import project, capture_plan


class RawPolicyProducer(unittest.TestCase):
    def setUp(self):
        self.core = Core.shared()
        self.requirement = {'policy': {'requiredChecks': ['z', 'a', 'z'],
            'sourceSha256': 'policy-identity', 'canonical': {'checks': [
                {'id': 'a', 'format': 'junit', 'profile': 'private-evaluator-v1'},
                {'id': 'z', 'format': 'exit', 'profile': 'legacy'}], 'protected': []}},
            'verifiers': [{'checkId': 'a', 'rootKey': 'root', 'path': 'exam.py', 'sha256': 'expected'}]}

    def test_native_roster_preserves_original_sorted_unique_and_declared_empty(self):
        required, empty, declarations = project(self.requirement, core=self.core)
        self.assertEqual(required, ['a', 'z'])
        self.assertTrue(empty)
        self.assertTrue(declarations['a'].bundle_declared)
        empty_policy = copy.deepcopy(self.requirement)
        empty_policy['policy']['requiredChecks'] = []
        self.assertEqual(project(empty_policy, core=self.core)[0:2], ([], True))
        empty_policy['policy']['sourceSha256'] = None
        self.assertEqual(project(empty_policy, core=self.core)[0:2], ([], False))
        self.assertEqual(project(None, core=self.core), ([], False, {}))

    def test_native_missing_profile_and_duplicate_declarations_follow_original(self):
        policy = copy.deepcopy(self.requirement)
        policy['policy']['canonical']['checks'].extend([
            {'id': 'a', 'format': 'exit', 'profile': 'legacy'},
            {'id': 'a', 'format': 'junit'}, {'id': 'missing', 'format': 'exit'}])
        declarations = project(policy, core=self.core)[2]
        self.assertEqual(declarations['a'].format, 'exit')
        self.assertEqual(declarations['a'].profile, 'legacy')
        self.assertNotIn('missing', declarations)

    def test_native_mandatory_agent_engine_and_protected_roster_before_effects(self):
        policy = copy.deepcopy(self.requirement)
        policy['policy']['canonical']['protected'] = ['private/**']
        required, _empty, declarations = project(policy, core=self.core,
            additional=['agent', 'agent'], finalization=True)
        self.assertEqual(required, ['a', 'z', 'protected-paths', 'agent', 'verifiers-modified'])
        self.assertEqual(declarations['agent'].origin, 'agent')
        self.assertEqual(declarations['protected-paths'].origin, 'engine')
        self.assertEqual(declarations['evaluation-complete'].origin, 'engine')

    def test_original_nonactor_additional_roster_does_not_invent_agent_requirement(self):
        required, _empty, declarations = project(self.requirement, core=self.core,
            additional=['custom', 'custom'], finalization=True)
        self.assertEqual(required, ['a', 'z', 'custom', 'verifiers-modified'])
        self.assertEqual(declarations['agent'].origin, 'agent')

    def fixture(self):
        start1 = {'checkId': 'a', 'invocationId': 'first'}
        start2 = {'checkId': 'a', 'invocationId': 'second'}
        failed = {'id': 'a', 'status': 'FAIL', 'exitCode': 1, 'hidden': None}
        passed = {'id': 'a', 'status': 'PASS', 'exitCode': 0, 'hidden': None}
        return ([copy.deepcopy(failed), copy.deepcopy(passed)],
            [('first', start1), ('second', start2)],
            {'first': {'started': start1, 'result': failed},
             'second': {'started': start2, 'result': passed}},
            {'candidateVerifiers': [{'rootKey': 'root', 'path': 'exam.py', 'sha256': 'expected'}],
             'verifiersModifiedByCandidate': []})

    def plan(self, rows, invocations, returns, context):
        return capture_plan(self.core, rows=rows, invocations=invocations,
            returns=returns, expected_requirement=self.requirement, context=context)

    def test_native_ordered_duplicate_failure_rows_not_filtered(self):
        rows, invocations, returns, context = self.fixture()
        plan = self.plan(rows, invocations, returns, context)
        self.assertEqual(plan['returnRows'], [1, 2])
        self.assertFalse(plan['verifiersModified'])

    def test_native_original_prefix_mutation_and_null_absence_refuse(self):
        rows, invocations, returns, context = self.fixture()
        rows[0]['exitCode'] = 0
        with self.assertRaises(WorldlineError) as error:
            self.plan(rows, invocations, returns, context)
        self.assertEqual(error.exception.code, 'FINALIZATION_RETURN_PREFIX_CHANGED')
        rows, invocations, returns, context = self.fixture()
        del rows[0]['hidden']
        with self.assertRaises(WorldlineError) as error:
            self.plan(rows, invocations, returns, context)
        self.assertEqual(error.exception.code, 'FINALIZATION_RETURN_PREFIX_CHANGED')

    def test_native_prefix_preserves_original_json_python_equality(self):
        rows, invocations, returns, context = self.fixture()
        returns['first']['result']['metadata'] = {'count': True, 'zero': -0.0,
                                                'nested': {'a': 1, 'b': 2}}
        rows[0]['metadata'] = {'nested': {'b': 2, 'a': 1}, 'zero': 0,
                               'count': 1.0}
        self.assertEqual(self.plan(rows, invocations, returns, context)['returnRows'], [1, 2])
        rows[0]['metadata']['count'] = 2
        with self.assertRaises(WorldlineError) as error:
            self.plan(rows, invocations, returns, context)
        self.assertEqual(error.exception.code, 'FINALIZATION_RETURN_PREFIX_CHANGED')

    def test_native_no_return_never_reuses_older_pass(self):
        rows, invocations, returns, context = self.fixture()
        del returns['second']
        with self.assertRaises(WorldlineError) as error:
            self.plan(rows, invocations, returns, context)
        self.assertEqual(error.exception.code, 'FINALIZATION_INVOCATION_HAS_NO_RETURN')

    def test_native_verifier_current_expected_sides_are_independent_of_label(self):
        rows, invocations, returns, context = self.fixture()
        context['candidateVerifiers'][0]['sha256'] = 'changed'
        self.assertTrue(self.plan(rows, invocations, returns, context)['verifiersModified'])
        context['candidateVerifiers'] = []
        self.assertTrue(self.plan(rows, invocations, returns, context)['verifiersModified'])
        rows, invocations, returns, context = self.fixture()
        context['verifiersModifiedByCandidate'] = ['forged-diagnostic']
        self.assertFalse(self.plan(rows, invocations, returns, context)['verifiersModified'])
        context['candidateVerifiers'].append({'rootKey': 'root', 'path': 'shadow.py', 'sha256': 'added'})
        self.assertTrue(self.plan(rows, invocations, returns, context)['verifiersModified'])
