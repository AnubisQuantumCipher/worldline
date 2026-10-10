"""Run retained original assertions in their own exact qualified source closure."""
from __future__ import annotations
import sys
_approved = sys.modules.get('_worldline_approved_source_loader')
if _approved is None:
    raise SystemExit('ORIGINAL_ASSERTION_EARLY_SOURCE_REQUIRED')
_lease = _approved.current()
_lease.check()
import argparse
import hashlib
import json
import os
import importlib.util
import unittest
from pathlib import Path
_lease.directory_or_absent(str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent))
from assertion_registry import validate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec', required=True)
    args = parser.parse_args()
    spec = json.loads(_lease.file(args.spec, ('DATA',)))
    raw = _lease.file(spec['source'], ('SOURCE',))
    methods = validate(spec, raw)
    for root in spec['import_roots']:
        _lease.directory_or_absent(root)
    sys.path[:0] = spec['import_roots']
    os.environ.update(spec['environment'])
    module = importlib.util.module_from_spec(importlib.util.spec_from_file_location(
        'worldline_original_retained_assertions', spec['source']))
    sys.modules[module.__name__] = module
    exec(_lease.compile_source(spec['source'], module.__name__), module.__dict__)
    if spec['suite'] == 'approved-loader':
        # This is the original main's genuine DATA acquisition, not authority
        # state. All five unchanged original assertion bodies still run.
        module.fixture = json.loads(_lease.file(spec['fixture'], ('DATA',)))
        if set(module.fixture) != {'source', 'faithful_cache', 'unfaithful_cache'}:
            raise RuntimeError('ORIGINAL_ASSERTION_LOADER_FIXTURE_DOMAIN_CHANGED')
    suite = unittest.defaultTestLoader.loadTestsFromNames(methods, module)
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(suite)
    passed = bool(methods) and result.wasSuccessful() and result.testsRun == len(methods) and not (
        result.skipped or result.expectedFailures or result.unexpectedSuccesses)
    closure = _lease.check()
    print(json.dumps({'schema': 'worldline.original-custody-assertion-result-v1',
        'suite': spec['suite'], 'source': spec['source'], 'sha256': spec['sha256'], 'methods': methods,
        'actual_tests_run': result.testsRun, 'actual_original_assertions_pass': passed,
        'executed_source': closure, 'phase_acceptance': False}), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
