"""Executable original terminal-domain/precedence controls; authored UNRUN."""
from __future__ import annotations

import struct
import unittest

from worldline.core import Core
from worldline.runner_outcome import terminal_outcome


class RunnerOutcomeNativeV35(unittest.TestCase):
    def decide(self, *, cancelled=False, timed_out=False, exit_code=0,
               supervision=None, observed=None, resources=None, prepare_agent_result=None,
               prepare_agent_prefix=None):
        membership = {
            'cancelled': {'profile': 'builtin-set-string-v1', 'requested': 'job',
                          'roster': ['other', 'job'] if cancelled else ['other']},
            'timedOut': {'profile': 'builtin-set-string-v1', 'requested': 'job',
                        'roster': ['other', 'job'] if timed_out else ['other']}}
        return terminal_outcome(Core.shared(), cancelled=cancelled, timed_out=timed_out,
            exit_code=exit_code, supervision=({'kind': 'SUPERVISED', 'result': 'success'}
                if supervision is None else supervision),
            resources=({'observed': {'state': 'OBSERVED', 'hitMemoryCeiling': False,
                                    'oomKilled': False} if observed is None else observed}
                       if resources is None else resources),
            stop_membership=membership, prepare_agent_result=prepare_agent_result,
            prepare_agent_prefix=prepare_agent_prefix)

    @staticmethod
    def fixture_agent_prefix():
        argv = ('worldline', 'runner-outcome-control')
        return list(argv)

    def test_cancel_timeout_and_ceiling_keep_original_reason_precedence(self):
        observed = {'state': 'OBSERVED', 'hitMemoryCeiling': True, 'oomKilled': True,
                    'memoryEvents': {'max': 1, 'oom_kill': 1}}
        cancelled = self.decide(cancelled=True, timed_out=True, observed=observed)
        self.assertEqual(cancelled['agentStatus'], 'FAIL')
        self.assertEqual(cancelled['reason'], 'USER_CANCELLED')
        timeout = self.decide(timed_out=True, observed=observed)
        self.assertEqual(timeout['reason'], 'TIMEOUT')
        ceiling = self.decide(observed=observed)
        self.assertEqual(ceiling['reason'], 'RESOURCE_LIMIT_EXCEEDED')
        self.assertTrue(ceiling['ceilingFired'])
        # A resource reason does not rewrite the original exit-based PASS status.
        self.assertEqual(ceiling['agentStatus'], 'PASS')

    def test_unknown_measurement_is_not_manufactured_as_clean_or_successful(self):
        value = self.decide(supervision={'kind': 'INDETERMINATE'},
                            observed={'state': 'UNAVAILABLE'})
        self.assertIsNone(value['ceilingFired'])
        self.assertEqual(value['ceilingEvidence'], 'nothing was measured')
        self.assertEqual(value['reason'], 'SUPERVISION_INDETERMINATE')
        self.assertEqual(value['agentStatus'], 'FAIL')

    def test_original_full_integer_bool_and_binary64_zero_domain(self):
        for value in (0, False, 0.0, -0.0):
            with self.subTest(value=value):
                self.assertEqual(self.decide(exit_code=value)['agentStatus'], 'PASS')
        for value in (True, 1 << 50000, -(1 << 50000), float('inf'), float('-inf'), float('nan')):
            with self.subTest(kind=type(value).__name__):
                self.assertEqual(self.decide(exit_code=value)['agentStatus'], 'FAIL')

    def test_actual_custom_exit_equality_is_requested_only_on_original_branch(self):
        calls = []
        class Exit:
            def __eq__(self, other):
                calls.append(('eq', other))
                return True
        value = self.decide(exit_code=Exit())
        self.assertEqual(value['agentStatus'], 'PASS')
        self.assertEqual(calls, [('eq', 0)])
        calls.clear()
        stopped = self.decide(cancelled=True, exit_code=Exit())
        self.assertEqual(stopped['agentStatus'], 'FAIL')
        self.assertEqual(calls, [])

    def test_custom_supervisor_keeps_original_ne_operator_and_order(self):
        calls = []
        class Kind:
            def __eq__(self, other):
                calls.append(('eq', other))
                return False
            def __ne__(self, other):
                calls.append(('ne', other))
                return False
        value = self.decide(supervision={'kind': Kind(), 'result': 'success'})
        self.assertEqual(value['agentStatus'], 'PASS')
        self.assertEqual(calls, [('eq', 'LAUNCH_FAILED'), ('ne', 'SUPERVISED'),
                                 ('eq', 'INDETERMINATE')])

    def test_launch_failure_does_not_invoke_later_original_protocols(self):
        calls = []
        class Kind:
            def __eq__(self, other):
                calls.append(('eq', other))
                return True
            def __ne__(self, other):
                calls.append(('ne', other))
                raise AssertionError('original LAUNCH_FAILED branch must not reach !=')
        value = self.decide(supervision={'kind': Kind(), 'result': 'oom-kill'})
        self.assertTrue(value['launchFailed'])
        self.assertTrue(value['ceilingFired'])
        self.assertEqual(calls, [('eq', 'LAUNCH_FAILED')])

    def test_exact_binary64_zero_and_nonzero_bit_patterns(self):
        for bits in ('0000000000000000', '8000000000000000',
                     '0000000000000001', '8000000000000001',
                     '7ff0000000000000', 'fff0000000000000',
                     '7ff0000000000001', 'fff8000000000011'):
            value = struct.unpack('>d', bytes.fromhex(bits))[0]
            with self.subTest(bits=bits):
                result = self.decide(exit_code=value)
                self.assertEqual(result['agentStatus'],
                                 'PASS' if bits in ('0000000000000000', '8000000000000000')
                                 else 'FAIL')
                self.assertEqual(struct.pack('>d', value).hex(), bits)

    def test_original_foreign_getter_truth_comparison_order_and_counts(self):
        calls = []
        class Truth:
            def __init__(self, name, value=False):
                self.name, self.value = name, value
            def __bool__(self):
                calls.append(('truth', self.name))
                return self.value
        class State(str):
            def __ne__(self, other):
                calls.append(('state-ne', other))
                return Truth('state')
        class Manager(str):
            def __eq__(self, other):
                calls.append(('manager-eq', other))
                return Truth('manager')
        class Kind(str):
            def __eq__(self, other):
                calls.append(('kind-eq', other))
                return Truth(other)
            def __ne__(self, other):
                calls.append(('kind-ne', other))
                return Truth(other)
        class Exit:
            def __eq__(self, other):
                calls.append(('exit-eq', other))
                return Truth('exit', True)
        class Observed(dict):
            def get(self, key, default=None):
                calls.append(('get', key))
                return super().get(key, default)
        class Supervisor(dict):
            def __getitem__(self, key):
                calls.append(('getitem', key))
                return super().__getitem__(key)
        result = self.decide(exit_code=Exit(),
            supervision=Supervisor(kind=Kind('SUPERVISED'), result=Manager('success')),
            observed=Observed(state=State('OBSERVED'), hitMemoryCeiling=Truth('hit'),
                              oomKilled=Truth('oom')))
        self.assertEqual(result['agentStatus'], 'PASS')
        self.assertEqual(calls, [
            ('get', 'hitMemoryCeiling'), ('truth', 'hit'),
            ('get', 'oomKilled'), ('truth', 'oom'),
            ('manager-eq', 'oom-kill'), ('truth', 'manager'),
            ('get', 'state'), ('state-ne', 'OBSERVED'), ('truth', 'state'),
            ('get', 'hitMemoryCeiling'), ('truth', 'hit'),
            ('manager-eq', 'oom-kill'), ('truth', 'manager'),
            ('getitem', 'kind'), ('kind-eq', 'LAUNCH_FAILED'), ('truth', 'LAUNCH_FAILED'),
            ('getitem', 'kind'), ('kind-ne', 'SUPERVISED'), ('truth', 'SUPERVISED'),
            ('exit-eq', 0), ('truth', 'exit'),
            ('getitem', 'kind'), ('kind-eq', 'INDETERMINATE'), ('truth', 'INDETERMINATE')])

    def test_repeated_hit_lookup_is_not_cached_as_evidence(self):
        calls = []
        class Observed(dict):
            def get(self, key, default=None):
                calls.append(key)
                if key == 'hitMemoryCeiling':
                    return calls.count(key) == 1
                raise AssertionError('short circuit must skip other observed lookups')
        value = self.decide(observed=Observed())
        self.assertTrue(value['ceilingFired'])
        self.assertEqual(value['ceilingEvidence'], 'no ceiling event was recorded')
        self.assertEqual(calls, ['hitMemoryCeiling', 'hitMemoryCeiling'])

    def test_foreign_manager_mutation_preserves_prior_builtin_dict_lookups(self):
        observed = {'state': 'OBSERVED', 'hitMemoryCeiling': False, 'oomKilled': False}
        calls = []
        class Manager:
            def __eq__(self, other):
                calls.append(other)
                observed['hitMemoryCeiling'] = True
                return False
        value = self.decide(observed=observed,
                            supervision={'kind': 'SUPERVISED', 'result': Manager()})
        self.assertFalse(value['ceilingFired'])
        self.assertEqual(value['ceilingEvidence'], 'cgroup memory.events sampled during the run')
        self.assertEqual(value['reason'], 'NONE')
        self.assertEqual(calls, ['oom-kill'])

    def test_native_stages_retain_original_finalization_codec(self):
        from worldline.finalization_journal import encode, decode
        value = self.decide(exit_code=-(1 << 50000))
        capture = value['capture']
        self.assertEqual(capture['schema'], 'worldline.runner-terminal-v2')
        self.assertEqual(decode(encode(capture)), capture)
        self.assertEqual(capture['exitCode']['value'], -(1 << 50000))
        self.assertEqual([name for name in capture if name in (
            'ceilingHitLookup1', 'ceilingOomLookup1', 'observedStateComparison',
            'ceilingHitLookup2', 'launchComparison', 'supervisedComparison',
            'indeterminateComparison')],
            ['ceilingHitLookup1', 'ceilingOomLookup1', 'observedStateComparison',
             'ceilingHitLookup2', 'launchComparison', 'supervisedComparison',
             'indeterminateComparison'])

    def test_missing_kind_error_occurs_only_after_ceiling_evidence(self):
        calls = []
        class Observed(dict):
            def get(self, key, default=None):
                calls.append(key)
                return super().get(key, default)
        with self.assertRaises(KeyError):
            self.decide(supervision={'result': 'success'},
                        observed=Observed(state='OBSERVED'))
        self.assertEqual(calls, ['hitMemoryCeiling', 'oomKilled', 'state', 'hitMemoryCeiling'])

    def test_original_truth_exception_stops_before_kind_getter(self):
        calls = []
        failure = RuntimeError('original external truth failure')
        class Truth:
            def __bool__(self):
                calls.append('truth')
                raise failure
        class Supervisor(dict):
            def __getitem__(self, key):
                calls.append('kind')
                return super().__getitem__(key)
        with self.assertRaises(RuntimeError) as raised:
            self.decide(supervision=Supervisor(kind='SUPERVISED'),
                        observed={'hitMemoryCeiling': Truth()})
        self.assertIs(raised.exception, failure)
        self.assertEqual(calls, ['truth'])

    def test_incidental_type_metadata_never_calls_metaclass_reflection(self):
        calls = []
        class Meta(type):
            def __getattribute__(cls, name):
                if name in ('__module__', '__qualname__'):
                    raise AssertionError('type metadata lookup was not an original operation')
                return super().__getattribute__(name)
        class Truth(metaclass=Meta):
            __module__ = None
            def __init__(self, value):
                self.value = value
            def __bool__(self):
                return self.value
        class Manager(metaclass=Meta):
            __module__ = None
            def __eq__(self, other):
                calls.append(('manager', other))
                return Truth(False)
        class Kind(metaclass=Meta):
            __module__ = None
            def __eq__(self, other):
                calls.append(('kind-eq', other))
                return Truth(False)
            def __ne__(self, other):
                calls.append(('kind-ne', other))
                return Truth(False)
        class Exit(metaclass=Meta):
            __module__ = None
            def __eq__(self, other):
                calls.append(('exit', other))
                return Truth(True)
        value = self.decide(exit_code=Exit(),
            supervision={'kind': Kind(), 'result': Manager()})
        self.assertEqual(value['agentStatus'], 'PASS')
        self.assertEqual(calls, [('manager', 'oom-kill'), ('manager', 'oom-kill'),
                                 ('kind-eq', 'LAUNCH_FAILED'), ('kind-ne', 'SUPERVISED'),
                                 ('exit', 0), ('kind-eq', 'INDETERMINATE')])

    def test_actual_callback_class_mutation_is_not_an_identity_refusal(self):
        calls = []
        class Second:
            def __eq__(self, other):
                calls.append(('second', other))
                return False
        class First:
            def __eq__(self, other):
                calls.append(('first', other))
                self.__class__ = Second
                return False
        manager = First()
        value = self.decide(supervision={'kind': 'SUPERVISED', 'result': manager})
        self.assertEqual(value['agentStatus'], 'PASS')
        self.assertEqual(calls, [('first', 'oom-kill'), ('second', 'oom-kill')])
        capture = value['capture']
        self.assertEqual(capture['managerResult']['typeReference'], str(id(First)))
        self.assertEqual(capture['managerOomComparison1']['leftTypeReference'], str(id(First)))
        self.assertEqual(capture['managerOomComparison2']['leftTypeReference'], str(id(Second)))
        self.assertEqual(capture['managerOomComparison1']['leftReference'], str(id(manager)))
        self.assertEqual(capture['managerOomComparison2']['leftReference'], str(id(manager)))

    def test_original_resource_publication_and_getter_effect_order(self):
        calls = []
        class Resources(dict):
            def get(self, key, default=None):
                calls.append(('resources-get', key))
                return super().get(key, default)
            def __getitem__(self, key):
                calls.append(('resources-getitem', key))
                return super().__getitem__(key)
            def __setitem__(self, key, value):
                calls.append(('resources-set', key, value))
                return super().__setitem__(key, value)
        class Observed(dict):
            def get(self, key, default=None):
                calls.append(('observed-get', key))
                if key == 'hitMemoryCeiling' and calls.count(('observed-get', key)) == 2:
                    self_resource = dict.__getitem__(resources, 'ceilingFired')
                    self.assert_published(self_resource)
                return super().get(key, default)
            @staticmethod
            def assert_published(value):
                if value is not False:
                    raise AssertionError('ceilingFired must be published before lookup2')
        class Supervisor(dict):
            def __getitem__(self, key):
                calls.append(('supervisor-getitem', key))
                if 'ceilingEvidence' not in resources:
                    raise AssertionError('ceilingEvidence must be published before first kind lookup')
                return super().__getitem__(key)
        resources = Resources(observed=Observed(state='OBSERVED'))
        value = self.decide(resources=resources,
                            supervision=Supervisor(kind='SUPERVISED', result='success'))
        self.assertEqual(value['agentStatus'], 'PASS')
        self.assertEqual(calls, [
            ('resources-get', 'observed'), ('resources-get', 'observed'),
            ('observed-get', 'hitMemoryCeiling'), ('observed-get', 'oomKilled'),
            ('observed-get', 'state'), ('resources-set', 'ceilingFired', False),
            ('observed-get', 'hitMemoryCeiling'), ('resources-getitem', 'ceilingFired'),
            ('resources-set', 'ceilingEvidence', 'no ceiling event was recorded'),
            ('supervisor-getitem', 'kind'), ('supervisor-getitem', 'kind'),
            ('resources-get', 'ceilingFired'), ('supervisor-getitem', 'kind')])

    def test_second_lookup_error_retains_completed_first_publication(self):
        failure = RuntimeError('second original hit getter')
        class Observed(dict):
            count = 0
            def get(self, key, default=None):
                if key == 'hitMemoryCeiling':
                    self.count += 1
                    if self.count == 2:
                        raise failure
                return super().get(key, default)
        resources = {'observed': Observed(state='OBSERVED')}
        with self.assertRaises(RuntimeError) as raised:
            self.decide(resources=resources)
        self.assertIs(raised.exception, failure)
        self.assertIs(resources['ceilingFired'], False)
        self.assertNotIn('ceilingEvidence', resources)

    def test_kind_getter_error_retains_both_completed_publications(self):
        failure = LookupError('original kind lookup')
        class Supervisor(dict):
            def __getitem__(self, key):
                raise failure
        resources = {'observed': {'state': 'OBSERVED'}}
        with self.assertRaises(LookupError) as raised:
            self.decide(resources=resources, supervision=Supervisor(result='success'))
        self.assertIs(raised.exception, failure)
        self.assertIs(resources['ceilingFired'], False)
        self.assertEqual(resources['ceilingEvidence'], 'no ceiling event was recorded')

    def test_setitem_post_effect_exception_is_not_retried_or_rolled_back(self):
        calls = []
        failure = RuntimeError('original setter failed after storing')
        class Resources(dict):
            def __setitem__(self, key, value):
                calls.append(key)
                super().__setitem__(key, value)
                raise failure
        resources = Resources(observed={'state': 'OBSERVED'})
        with self.assertRaises(RuntimeError) as raised:
            self.decide(resources=resources)
        self.assertIs(raised.exception, failure)
        self.assertEqual(calls, ['ceilingFired'])
        self.assertIs(resources['ceilingFired'], False)
        self.assertNotIn('ceilingEvidence', resources)

    def test_published_field_mutation_drives_original_evidence_identity(self):
        class Resources(dict):
            def __setitem__(self, key, value):
                super().__setitem__(key, None if key == 'ceilingFired' else value)
        resources = Resources(observed={'state': 'OBSERVED'})
        value = self.decide(resources=resources)
        self.assertFalse(value['ceilingFired'])  # Audit of native initial derivation.
        self.assertIsNone(resources['ceilingFired'])
        self.assertEqual(resources['ceilingEvidence'], 'nothing was measured')
        self.assertEqual(value['ceilingEvidence'], 'nothing was measured')
        self.assertEqual(value['reason'], 'NONE')

    def test_kind_callback_mutation_drives_actual_later_reason_lookup(self):
        resources = {'observed': {'state': 'OBSERVED'}}
        class Kind:
            def __eq__(self, other):
                return False
            def __ne__(self, other):
                resources['ceilingFired'] = True
                return False
        value = self.decide(resources=resources,
                            supervision={'kind': Kind(), 'result': 'success'})
        self.assertFalse(value['ceilingFired'])  # Initially published native audit.
        self.assertTrue(resources['ceilingFired'])
        self.assertEqual(value['reason'], 'RESOURCE_LIMIT_EXCEEDED')
        self.assertEqual(value['agentStatus'], 'PASS')
        self.assertNotIn('indeterminateComparison', value['capture'])

    def test_actual_result_body_effects_precede_reason_and_keep_native_status(self):
        resources = {'observed': {'state': 'OBSERVED'}}
        held_results = []
        def prepare(status):
            self.assertIs(resources['ceilingFired'], False)
            self.assertEqual(resources['ceilingEvidence'], 'no ceiling event was recorded')
            resources['ceilingFired'] = True
            result = {'status': status, 'resources': resources}
            held_results.append(result)
            return result
        value = self.decide(resources=resources, prepare_agent_result=prepare,
                            prepare_agent_prefix=self.fixture_agent_prefix)
        self.assertEqual(value['agentStatus'], 'PASS')
        self.assertEqual(value['reason'], 'RESOURCE_LIMIT_EXCEEDED')
        self.assertEqual(len(held_results), 1)
        capture = value['capture']
        self.assertEqual(capture['mode'], 'runner-owner-v1')
        self.assertEqual(capture['prepareAgentResult']['reference'], str(id(held_results[0])))
        self.assertEqual(capture['prepareAgentResult']['nativeStatus'], 'PASS')
        self.assertNotIn('indeterminateComparison', capture)

    def test_actual_result_body_exception_preserves_publications_and_skips_reason(self):
        failure = OSError('original hash_file or proxy summary callback')
        calls = []
        class Resources(dict):
            def get(self, key, default=None):
                if key == 'ceilingFired':
                    raise AssertionError('reason lookup cannot precede failed result construction')
                return super().get(key, default)
        resources = Resources(observed={'state': 'OBSERVED'})
        def prepare(status):
            calls.append(status)
            raise failure
        with self.assertRaises(OSError) as raised:
            self.decide(resources=resources, prepare_agent_result=prepare,
                        prepare_agent_prefix=self.fixture_agent_prefix)
        self.assertIs(raised.exception, failure)
        self.assertEqual(calls, ['PASS'])
        self.assertIs(resources['ceilingFired'], False)
        self.assertEqual(resources['ceilingEvidence'], 'no ceiling event was recorded')

    def test_launch_failure_never_materializes_original_agent_result(self):
        calls = []
        def prepare(status):
            calls.append(status)
            return {'status': status}
        value = self.decide(supervision={'kind': 'LAUNCH_FAILED', 'result': 'success'},
                            prepare_agent_result=prepare,
                            prepare_agent_prefix=self.fixture_agent_prefix)
        self.assertTrue(value['launchFailed'])
        self.assertEqual(calls, [])
        self.assertNotIn('prepareAgentResult', value['capture'])
        self.assertNotIn('prepareAgentPrefix', value['capture'])

    def test_stopped_materializes_fail_before_original_cancelled_reason(self):
        held_results = []
        def prepare(status):
            result = {'status': status}
            held_results.append(result)
            return result
        value = self.decide(cancelled=True, prepare_agent_result=prepare,
                            prepare_agent_prefix=self.fixture_agent_prefix)
        self.assertEqual([result['status'] for result in held_results], ['FAIL'])
        self.assertEqual(value['agentStatus'], 'FAIL')
        self.assertEqual(value['reason'], 'USER_CANCELLED')
        self.assertNotIn('ceilingReasonLookup', value['capture'])

    def test_production_result_observation_cannot_supply_agent_status(self):
        from worldline.runner_outcome import _decide
        held_results = []
        def prepare(status):
            result = {'status': status}
            held_results.append(result)
            return result
        value = self.decide(prepare_agent_result=prepare,
                            prepare_agent_prefix=self.fixture_agent_prefix)
        capture = dict(value['capture'])
        changed = dict(capture['prepareAgentResult'])
        changed['nativeStatus'] = 'FAIL'
        capture['prepareAgentResult'] = changed
        self.assertEqual(_decide(Core.shared(), capture)['status'], 'INVALID_CAPTURE')
        del capture['prepareAgentResult']
        requested = _decide(Core.shared(), capture)
        self.assertEqual(requested['status'], 'CAPTURE_REQUIRED')
        self.assertEqual(requested['operation'], 'prepareAgentResult')
        self.assertEqual(requested['agentStatus'], 'PASS')
        del capture['prepareAgentPrefix']
        requested = _decide(Core.shared(), capture)
        self.assertEqual(requested['status'], 'CAPTURE_REQUIRED')
        self.assertEqual(requested['operation'], 'prepareAgentPrefix')

    def test_original_argv_iteration_error_precedes_status_protocols(self):
        calls = []
        failure = RuntimeError('original argv iterator')
        resources = {'observed': {'state': 'OBSERVED'}}
        class Kind:
            def __eq__(self, other):
                calls.append(('kind-eq', other))
                return False
            def __ne__(self, other):
                raise AssertionError('supervised comparison followed failed list(argv)')
        class Exit:
            def __eq__(self, other):
                raise AssertionError('exit comparison followed failed list(argv)')
        class Argv:
            def __iter__(self):
                calls.append(('argv-iter',))
                raise failure
        argv = Argv()
        def prefix():
            return list(argv)
        def result(status):
            raise AssertionError('remaining result body followed failed list(argv)')
        with self.assertRaises(RuntimeError) as raised:
            self.decide(resources=resources, supervision={'kind': Kind(), 'result': 'success'},
                        exit_code=Exit(), prepare_agent_prefix=prefix, prepare_agent_result=result)
        self.assertIs(raised.exception, failure)
        self.assertEqual(calls, [('kind-eq', 'LAUNCH_FAILED'), ('argv-iter',)])
        self.assertIs(resources['ceilingFired'], False)
        self.assertEqual(resources['ceilingEvidence'], 'no ceiling event was recorded')

    def test_original_argv_iteration_mutation_precedes_kind_and_exit_status(self):
        calls = []
        held_prefix = []
        resources = {'observed': {'state': 'OBSERVED'}}
        exit_ready = False
        class Kind:
            def __eq__(self, other):
                calls.append(('old-kind-eq', other))
                return False
            def __ne__(self, other):
                raise AssertionError('status used kind from before actual argv iteration')
        class Exit:
            def __eq__(self, other):
                calls.append(('exit-eq', other))
                if not exit_ready:
                    raise AssertionError('status comparison preceded actual argv iteration')
                return True
        supervision = {'kind': Kind(), 'result': 'success'}
        class Argv:
            def __iter__(self):
                nonlocal exit_ready
                calls.append(('argv-iter',))
                supervision['kind'] = 'SUPERVISED'
                exit_ready = True
                return iter(('worldline', 'actual-prefix-fixture'))
        argv = Argv()
        def prefix():
            actual = list(argv)
            held_prefix.append(actual)
            return actual
        def result(status):
            calls.append(('result-body', status))
            return {'status': status, 'argv': held_prefix[0], 'resources': resources}
        value = self.decide(resources=resources, supervision=supervision, exit_code=Exit(),
                            prepare_agent_prefix=prefix, prepare_agent_result=result)
        self.assertEqual(value['agentStatus'], 'PASS')
        self.assertEqual(calls, [('old-kind-eq', 'LAUNCH_FAILED'), ('argv-iter',),
                                 ('exit-eq', 0), ('result-body', 'PASS')])
        self.assertEqual(held_prefix[0], ['worldline', 'actual-prefix-fixture'])
        self.assertEqual(value['capture']['prepareAgentPrefix']['reference'], str(id(held_prefix[0])))

    def test_complete_roster_overrides_non_authoritative_flags(self):
        from worldline.runner_outcome import terminal_outcome
        result = terminal_outcome(Core.shared(), cancelled=False, timed_out=False,
            exit_code=0, supervision={'kind': 'SUPERVISED', 'result': 'success'},
            resources={'observed': {'state': 'OBSERVED'}},
            stop_membership={
                'cancelled': {'profile': 'builtin-set-string-v1',
                              'requested': 'job', 'roster': ['other', 'job']},
                'timedOut': {'profile': 'builtin-set-string-v1',
                            'requested': 'job', 'roster': []}})
        self.assertTrue(result['stopped'])
        self.assertEqual(result['agentStatus'], 'FAIL')
        self.assertEqual(result['reason'], 'USER_CANCELLED')


if __name__ == '__main__':
    unittest.main()
