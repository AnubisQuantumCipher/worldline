"""Immutable original assertion suites; selected DATA cannot narrow a suite."""
import ast
import hashlib
from pathlib import PurePath

SUITES = {
    'startup': ('protected-startup/controls/test_protected_startup_v1.py', 'a0d2d529aff1322ce11e66d955f5af4161cbdfff59e0c032d770c51e734cdbeb'),
    'resource-replay': ('protected-resource/controls/test_full_resource_replay_v2.py', '6014b1f961dae05226afa23fecf1931d220951c2ec64c5a85c2b40ed8c0a5a4d'),
    'native-lifetime': ('tests/native_lifetime_controls.py', '96c946f0e68c7e9ec0092926943edd432343b466f57f4e31d6518ad1d00cb3ff'),
    'native-workload': ('tests/native_workload_controls.py', '0d0d3dd578002598c0f65f918d25ceecd6757dacc5b46b8ff461c7400191e61b'),
    'native-guard': ('tests/test_examiner_native_guard.py', 'c22926daa78fb1596e86286013a2912e82565c53806e5e7ec5ebedcd5a2ecc14'),
    'revalidation-binding': ('tests/test_revalidation_binding.py', '180988e547c32d75742799da1f43b6867152e9499febb68d358b172e86aa168e'),
    'agent-acquisition': ('tests/test_agent_acquisition_ownership.py', '4454093acfc51ee0de65682d96714195ad42d5183e42b995aa52e704649cc914'),
    'trusted-startup': ('tests/test_trusted_startup.py', '60204983290831b64c03d61348a0c51264e174fce0de3979ae606d8f996c4673'),
    'resource-ledger': ('tests/test_resource_run_ledger_v1.py', 'eff3894460e2407afaeecaef78433f660b4c80a11c621f5a7ef67ac452ac0f63'),
    'approved-loader': ('protected-runtime/controls/loader_probe.py', '783da47ad312fb06b8d57c89de92dbb1a1c36ed522d02f7c5e41fce03854cd5c'),
}
SPEC_KEYS = {'suite', 'source', 'sha256', 'methods', 'environment', 'import_roots', 'fixture'}


def validate(spec, raw):
    if set(spec) != SPEC_KEYS or spec['suite'] not in SUITES:
        raise RuntimeError('ORIGINAL_ASSERTION_COMMITTED_SUITE_REQUIRED')
    suffix, digest = SUITES[spec['suite']]
    if (tuple(PurePath(spec['source']).parts[-len(PurePath(suffix).parts):]) != PurePath(suffix).parts
            or spec['sha256'] != digest or hashlib.sha256(raw).hexdigest() != digest):
        raise RuntimeError('ORIGINAL_ASSERTION_IMMUTABLE_FULL_SOURCE_CHANGED')
    tree = ast.parse(raw, filename=spec['source'])
    methods = [node.name + '.' + method.name for node in tree.body if isinstance(node, ast.ClassDef)
               for method in node.body if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef))
               and method.name.startswith('test')]
    if not methods or spec['methods'] != methods:
        raise RuntimeError('ORIGINAL_ASSERTION_COMPLETE_UNCHANGED_METHOD_ROSTER_REQUIRED')
    if spec['suite'] == 'approved-loader':
        if not isinstance(spec['fixture'], str) or not spec['fixture']:
            raise RuntimeError('ORIGINAL_ASSERTION_GENUINE_LOADER_FIXTURE_REQUIRED')
    elif spec['fixture'] is not None:
        raise RuntimeError('ORIGINAL_ASSERTION_UNDECLARED_FIXTURE_REFUSED')
    return methods


def require_campaign(specs, source_reader):
    seen = set()
    for spec in specs:
        validate(spec, source_reader(spec['source']))
        if spec['suite'] in seen:
            raise RuntimeError('ORIGINAL_ASSERTION_DUPLICATE_SUITE')
        seen.add(spec['suite'])
    if seen != set(SUITES):
        raise RuntimeError('ORIGINAL_ASSERTION_FULL_IMMUTABLE_CAMPAIGN_REQUIRED')
