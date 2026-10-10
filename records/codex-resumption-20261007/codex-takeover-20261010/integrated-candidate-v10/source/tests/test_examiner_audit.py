"""D21's positive source domain and refusal controls over real staged files.

The source strings are parsed as data, never executed. These tests establish no
confinement, native authority, formal proof, or phase acceptance.
"""
from __future__ import annotations

import base64
import copy
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
from worldline.examiner_audit import audit, replay, report_audit_clean


class ExaminerAuditTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-examiner-audit-")
        self.addCleanup(self.temporary.cleanup)
        self.bundle = Path(self.temporary.name)
        self.pins = {}
        self.entry = "root/exam.py"

    def source(self, path, source):
        data = source.encode() if isinstance(source, str) else source
        target = self.bundle / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        self.pins[path] = hashlib.sha256(data).hexdigest()

    def observe(self):
        return audit(self.bundle, self.entry, self.pins)

    def assert_clean(self, observation):
        self.assertIs(observation["clean"], True, observation["findings"])
        self.assertTrue(replay(observation, entry=self.entry, executed_digests=self.pins))

    def test_stdlib_generators_and_candidate_program_strings_remain_data(self):
        self.source(self.entry, '''import candidate
from collections import namedtuple
from dataclasses import dataclass
import enum, typing, tempfile
from xml.sax import saxutils
T = namedtuple('T', 'field')
@dataclass
class Value:
    field: int
candidate.run(['/usr/bin/python3', '-c', 'exec(compile("pass", "data", "exec"))'])
''')
        self.assert_clean(self.observe())

    def test_regular_relative_and_cyclic_closure(self):
        self.source(self.entry, 'import pkg.child\nfrom pkg import child\n')
        self.source('root/pkg/__init__.py', 'from . import child\n')
        self.source('root/pkg/child.py', 'from . import sibling\n')
        self.source('root/pkg/sibling.py', 'from . import child\n')
        observation = self.observe()
        self.assert_clean(observation)
        self.assertEqual({row['path'] for row in observation['closure']}, set(self.pins))

    def test_verifier_root_precedes_entry_directory(self):
        self.source(self.entry, 'import helper\n')
        self.source('helper.py', 'VALUE = "root"\n')
        self.source('root/helper.py', 'import pickle\n')
        observation = self.observe()
        self.assert_clean(observation)
        self.assertEqual({row['path'] for row in observation['closure']}, {self.entry, 'helper.py'})

    def test_bundle_shadow_of_stdlib_is_audited(self):
        self.source(self.entry, 'import json\n')
        self.source('root/json.py', 'import pickle\n')
        observation = self.observe()
        self.assertFalse(observation['clean'])
        self.assertTrue(any(row['file'] == 'root/json.py' for row in observation['findings']))

    def test_namespace_package_can_span_search_roots(self):
        self.source(self.entry, 'import ns.left\nimport ns.right\n')
        self.source('ns/left.py', 'VALUE = 1\n')
        self.source('root/ns/right.py', 'VALUE = 2\n')
        observation = self.observe()
        self.assert_clean(observation)
        self.assertEqual({row['path'] for row in observation['closure']}, set(self.pins))

    def test_imports_inside_functions_and_handlers_are_in_closure(self):
        self.source(self.entry, 'def later():\n import helper\ntry:\n import missing\nexcept ImportError:\n pass\n')
        self.source('root/helper.py', 'import marshal\n')
        observation = self.observe()
        self.assertFalse(observation['clean'])
        self.assertTrue(any('missing' in row['detail'] for row in observation['findings']))
        self.assertTrue(any(row['file'] == 'root/helper.py' for row in observation['findings']))

    def test_all_original_refusal_categories_and_aliases(self):
        cases = (
            'import importlib.util\n', 'from logging import config\n',
            'from http import server\n', 'import ctypes\n',
            'x = exec\n', 'x = __builtins__\n',
            'import os as system\nsystem.spawnv(0, "x", [])\n',
            'from os import system as start\nstart("x")\n',
            'from concurrent.futures import ProcessPoolExecutor as Pool\n',
            'import sqlite3\nsqlite3.Connection.enable_load_extension(None, True)\n',
            'import sqlite3\nconnection = sqlite3.connect(":memory:")\nconnection.enable_load_extension(True)\n',
            'import sqlite3\nsqlite3.connect(":memory:").load_extension("data")\n',
            'import os\napi = os\napi.system("x")\n',
            'import sys as runtime\nruntime.path.append("x")\n',
            'from sys import modules as modules\nmodules.clear()\n',
            'import sys\nmodules = sys.modules\nmodules.__init__()\n',
            'import sys\nsys.path[:] = []\n', 'import sys\ndel sys.modules["x"]\n',
        )
        for source in cases:
            with self.subTest(source=source):
                self.source(self.entry, source)
                observation = self.observe()
                self.assertFalse(observation['clean'])
                self.assertTrue(observation['findings'])
                self.assertFalse(replay(observation, entry=self.entry, executed_digests=self.pins))

    def test_read_only_import_state_operations_are_allowed(self):
        self.source(self.entry, 'import sys\na = sys.path.copy()\nb = sys.modules.get("json")\n')
        self.assert_clean(self.observe())

    def test_later_alias_reuse_and_sibling_import_do_not_erase_operations(self):
        cases = (
            'import os as api\napi.system("x")\nimport json as api\n',
            'import sys as api\napi.path.clear()\nimport json as api\n',
            'def first():\n import os as api\n api.system("x")\ndef second():\n import json as api\n',
        )
        for source in cases:
            with self.subTest(source=source):
                self.source(self.entry, source)
                self.assertFalse(self.observe()['clean'])

    def test_sibling_scope_does_not_inherit_another_functions_alias(self):
        self.source(self.entry, 'def first():\n import os as api\n api.readlink("x")\ndef second():\n import json as api\n api.system("data")\n')
        self.assert_clean(self.observe())

    def test_definition_headers_and_method_globals_use_enclosing_scope(self):
        cases = (
            'import os\ndef f(os=os.system("data")):\n pass\n',
            'import os\n@os.system("data")\ndef f(os=None):\n pass\n',
            'import os\nclass C:\n import json as os\n def f(self):\n  os.system("data")\n',
            'import os\nvalues = [os for os in os.popen("data")]\n',
        )
        for source in cases:
            with self.subTest(source=source):
                self.source(self.entry, source)
                self.assertFalse(self.observe()['clean'])
        self.source(self.entry, 'import json as api\ndef f(api=None, value=api.system("data")):\n import os as api\n api.readlink("x")\n')
        self.assert_clean(self.observe())

    def test_package_wildcard_includes_declared_child_source(self):
        self.source(self.entry, 'from pkg import *\n')
        self.source('root/pkg/__init__.py', '__all__ = ["child"]\n')
        self.source('root/pkg/child.py', 'import pickle\n')
        observation = self.observe()
        self.assertFalse(observation['clean'])
        self.assertTrue(any(row['file'] == 'root/pkg/child.py' for row in observation['findings']))
        self.source('root/pkg/child.py', 'VALUE = 1\n')
        self.assert_clean(self.observe())

    def test_unresolved_wildcard_exports_do_not_create_a_clean_observation(self):
        self.source(self.entry, 'from pkg import *\n')
        self.source('root/pkg/__init__.py', '__all__ = list("child")\n')
        self.assertFalse(self.observe()['clean'])

    def test_wildcard_export_mutations_and_imported_exports(self):
        self.source(self.entry, 'from pkg import *\n')
        self.source('root/pkg/child.py', 'import pickle\n')
        cases = (
            '__all__ = []\n__all__[:] = ["child"]\n',
            '__all__ = []\nalias = __all__\nalias.append("child")\n',
            '__all__ = []\nalias = __all__\nalias += ["child"]\n',
            '__all__ = []\ndel __all__\nfrom helper import __all__\n',
        )
        self.source('root/helper.py', '__all__ = ["child"]\n')
        for source in cases:
            with self.subTest(source=source):
                self.source('root/pkg/__init__.py', source)
                self.assertFalse(self.observe()['clean'])

    def test_function_local_exports_do_not_change_package_wildcard(self):
        self.source(self.entry, 'from pkg import *\n')
        self.source('root/pkg/__init__.py', '__all__ = []\ndef f():\n __all__ = list("child")\n return __all__\n')
        self.source('root/pkg/child.py', 'import pickle\n')
        self.assert_clean(self.observe())

    def test_import_state_mutating_special_methods_are_in_scope(self):
        for source in ('import sys\nsys.modules.__ior__({})\n',
                       'from sys import path as names\nnames.__init__([])\n'):
            with self.subTest(source=source):
                self.source(self.entry, source)
                self.assertFalse(self.observe()['clean'])

    def test_non_source_imports_are_refused_but_unimported_data_is_preserved(self):
        self.source(self.entry, 'import helper\n')
        self.source('root/helper.pyc', b'not executable bytecode')
        self.assertFalse(self.observe()['clean'])
        self.source(self.entry, 'DATA = "helper.pyc is data here"\n')
        self.assert_clean(self.observe())

    def test_digest_mismatch_missing_member_and_extra_member_refuse(self):
        self.source(self.entry, 'VALUE = 1\n')
        (self.bundle / self.entry).write_text('VALUE = 2\n')
        self.assertFalse(self.observe()['clean'])
        self.source(self.entry, 'VALUE = 1\n')
        (self.bundle / 'extra.py').write_text('VALUE = 3\n')
        self.assertFalse(self.observe()['clean'])
        (self.bundle / 'extra.py').unlink()
        (self.bundle / self.entry).unlink()
        self.assertFalse(self.observe()['clean'])

    def test_symlink_member_is_not_followed(self):
        self.source(self.entry, 'VALUE = 1\n')
        self.source('root/helper.py', 'VALUE = 2\n')
        (self.bundle / 'root/helper.py').unlink()
        (self.bundle / 'root/helper.py').symlink_to('exam.py')
        self.assertFalse(self.observe()['clean'])

    def test_replay_uses_bytes_and_independent_expected_pins(self):
        self.source(self.entry, 'VALUE = 1\n')
        original = self.observe()
        self.assert_clean(original)
        forged = copy.deepcopy(original)
        forged['files'][0]['payloadB64'] = base64.b64encode(b'import pickle\n').decode()
        self.assertFalse(replay(forged, entry=self.entry, executed_digests=self.pins))
        forged['executedDigests'][self.entry] = hashlib.sha256(b'import pickle\n').hexdigest()
        self.assertFalse(replay(forged, entry=self.entry, executed_digests=self.pins))
        self.assertFalse(replay(forged, entry=self.entry, executed_digests=forged['executedDigests']))
        forged = copy.deepcopy(original)
        forged['closure'] = []
        self.assertFalse(replay(forged, entry=self.entry, executed_digests=self.pins))

    def test_report_fact_requires_both_actual_copy_observations_and_entry_binding(self):
        self.source(self.entry, 'VALUE = 1\n')
        observation = self.observe()
        executed = {'members': [{'rootKey': 'root', 'path': 'exam.py',
                     'executedAs': '/run/worldline-verifiers/root/exam.py',
                     'sha256': self.pins[self.entry]}], 'stable': True,
                    'identity': 'same measured identity', 'identityAfterExecution': 'same measured identity',
                    'argvRewrites': [{'from': 'exam.py', 'to': '/run/worldline-verifiers/root/exam.py'}]}
        result = {'argv': ['/usr/bin/python3', 'exam.py'], 'executedVerifierSet': executed,
                  'examinerAudit': {'before': observation, 'after': copy.deepcopy(observation),
                                    'mount': '/run/worldline-verifiers'}}
        self.assertTrue(report_audit_clean(result))
        bad = copy.deepcopy(result)
        bad['examinerAudit']['after']['files'] = []
        self.assertFalse(report_audit_clean(bad))
        bad = copy.deepcopy(result)
        bad['argv'][1] = 'different.py'
        self.assertFalse(report_audit_clean(bad))
        bad = copy.deepcopy(result)
        bad['executedVerifierSet']['stable'] = False
        self.assertFalse(report_audit_clean(bad))
        self.assertFalse(report_audit_clean({'examinerAudit': {'clean': True}}))


if __name__ == '__main__':
    unittest.main()
