"""Raw byte/source/default/identity mutations; native execution is required."""
import base64
import copy
import hashlib
import json
import unittest
from worldline.core import Core
from worldline.errors import WorldlineError
from worldline.evaluation_policy import project


class NativePolicySource(unittest.TestCase):
    def setUp(self):
        self.core = Core.shared()
        self.raw = {'schemaVersion': 1, 'generated': [], 'services': [],
            'checks': [{'id': 'check', 'kind': 'tests', 'argv': ['/usr/bin/true'],
                        'required': True, 'format': 'exit'}]}
        self.requirement = {'policy': {'requiredChecks': ['check'],
            'canonical': {'schemaVersion': 1, 'generated': [], 'services': [],
                'protected': [], 'checks': [{'id': 'check', 'kind': 'tests',
                    'argv': ['/usr/bin/true'], 'cwd': None, 'required': True,
                    'format': 'exit', 'result': None, 'covers': [],
                    'verifiers': [], 'profile': 'legacy'}]}}, 'verifiers': []}
        self.bind(self.raw)

    def bind(self, raw):
        acquired = json.dumps(raw, ensure_ascii=False).encode('utf-8')
        expected_identity = hashlib.sha256(acquired).hexdigest()
        self.requirement['policy']['sourceSha256'] = expected_identity
        self.requirement['policy']['sourceObservation'] = {
            'payloadB64': base64.b64encode(acquired).decode('ascii'),
            'expectedSourceSha256': expected_identity, 'rawRoots': []}

    def native(self):
        return project(self.requirement, core=self.core)

    def refused(self):
        with self.assertRaises(WorldlineError) as error:
            self.native()
        self.assertEqual(error.exception.code, 'EVALUATION_POLICY_SOURCE_CONFLICT')

    def test_actual_source_default_profile_and_complete_required_correspondence(self):
        required, empty, declarations = self.native()
        self.assertEqual(required, ['check'])
        self.assertFalse(empty)
        self.assertEqual(declarations['check'].profile, 'legacy')
        self.requirement['policy']['requiredChecks'] = []
        self.refused()

    def test_explicit_empty_policy_and_absent_declaration_are_distinct(self):
        self.raw['checks'] = []
        self.requirement['policy']['requiredChecks'] = []
        self.requirement['policy']['canonical']['checks'] = []
        self.bind(self.raw)
        required, empty, _ = self.native()
        self.assertEqual(required, [])
        self.assertTrue(empty)
        del self.requirement['policy']['sourceObservation']
        del self.requirement['policy']['sourceSha256']
        required, empty, _ = self.native()
        self.assertEqual(required, [])
        self.assertFalse(empty)

    def test_expected_identity_is_not_cloned_from_observed_changed_source(self):
        observed = copy.deepcopy(self.raw)
        observed['checks'][0]['argv'] = ['/usr/bin/false']
        changed = json.dumps(observed).encode()
        self.requirement['policy']['sourceObservation']['payloadB64'] = base64.b64encode(changed).decode()
        self.requirement['policy']['sourceSha256'] = hashlib.sha256(changed).hexdigest()
        self.refused()

    def test_changed_ordered_canonical_caller_fields_cannot_authorize(self):
        for field, value in [('argv', ['/usr/bin/false']), ('format', 'junit'),
                             ('profile', 'private-evaluator-v1'), ('required', False)]:
            saved = copy.deepcopy(self.requirement)
            self.requirement['policy']['canonical']['checks'][0][field] = value
            self.refused()
            self.requirement = saved

    def test_missing_null_and_present_empty_policy_source_are_not_equal(self):
        saved = copy.deepcopy(self.requirement)
        self.requirement['policy']['sourceObservation']['payloadB64'] = None
        self.refused()
        self.requirement = saved
        self.requirement['policy']['sourceObservation']['payloadB64'] = ''
        self.refused()
        self.requirement = saved
        del self.requirement['policy']['sourceObservation']
        # Original explicit historical model input stays historical, rather
        # than falsely being relabelled as a present authenticated source.
        self.assertEqual(self.native()[0], ['check'])

    def test_original_boolean_and_binary64_schema_one_domains_are_preserved(self):
        for value in (True, 1.0):
            source = copy.deepcopy(self.raw)
            source['schemaVersion'] = value
            self.bind(source)
            self.assertEqual(self.native()[0], ['check'])
        source['schemaVersion'] = 2
        self.bind(source)
        self.refused()

    def test_glob_verifier_probe_preserves_separation(self):
        for pattern, cover, accepted in (
            ('exam/*.py', 'src/**', True),
            ('exam/*.py', 'exam/**', False),
            ('exam/**/case?.py', 'src/**', True),
            ('exam/[ab].py', 'exam/**', False),
            ('*.py', 'src/**', True),
            ('exam/*.py', 'exam/*.py', False),
        ):
            with self.subTest(pattern=pattern, cover=cover):
                self.raw['checks'][0].update(verifiers=[pattern], covers=[cover])
                self.requirement['policy']['canonical']['checks'][0].update(
                    verifiers=[pattern], covers=[cover])
                self.bind(self.raw)
                if accepted:
                    self.assertEqual(self.native()[0], ['check'])
                else:
                    self.refused()

    def test_actual_source_refusals_are_native_not_canonical_success_flags(self):
        baseline = copy.deepcopy(self.requirement)
        mutations = [
            {'extra': True},
            {'checks': [{'id': 'agent', 'kind': 'tests', 'argv': ['true'],
                         'required': True, 'format': 'exit'}]},
            {'checks': [{'id': 'check', 'kind': 'tests', 'argv': [],
                         'required': True, 'format': 'exit'}]},
            {'checks': [{'id': 'check', 'kind': 'tests', 'argv': ['true'],
                         'required': True, 'format': 'junit',
                         'profile': 'private-evaluator-v1', 'verifiers': []}]},
            {'protected': ['../escape']},
            {'services': [{'id': 'service', 'argv': ['true'], 'cwd': '.',
                'env': {'APİ_KEY': 'value'}, 'healthArgv': ['true'], 'restart': 'never'}]},
        ]
        for fields in mutations:
            self.requirement = copy.deepcopy(baseline)
            source = copy.deepcopy(self.raw)
            source.update(fields)
            self.bind(source)
            self.refused()
