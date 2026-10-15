"""PROPOSAL ONLY: install as tests/test_typed_export_correspondence.py after review.

These are source-mutation controls for the export guard. They neither compile
mutants nor establish ABI/semantic equivalence. Do not run this scratch copy:
ROOT is intentionally the eventual tests-directory layout.
"""
from pathlib import Path
import re
import shutil
import tempfile
import unittest

from worldline import proof_manifest as verifier

ROOT = Path(__file__).resolve().parents[1]


class TypedExportCorrespondence(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='worldline-export-guard-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        # Explicit Ada inventory only: no build trees, evidence or symlinked obj.
        for relative in verifier.DECLARED_CORE_ADA_SOURCES:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        self.assertEqual(verifier.export_problems(self.root), [])

    def replace(self, relative, before, after):
        path = self.root / relative
        text = path.read_text()
        self.assertEqual(text.count(before), 1, (relative, before))
        path.write_text(text.replace(before, after, 1))

    def change_function(self, relative, name, before, after):
        path = self.root / relative
        text = path.read_text()
        matches = list(re.finditer(r'\bfunction\s+' + re.escape(name) + r'\b', text))
        self.assertEqual(len(matches), 1, name)
        start = matches[0].start()
        end = text.index('   end ' + name + ';', start)
        chunk = text[start:end]
        self.assertEqual(chunk.count(before), 1, (relative, name, before))
        path.write_text(text[:start] + chunk.replace(before, after, 1) + text[end:])

    def assert_refused(self, reason):
        problems = verifier.export_problems(self.root)
        self.assertTrue(any(reason in item for item in problems), problems)

    def test_every_profile_is_bound_exactly_and_duplicate_profiles_refuse(self):
        path = self.root / 'core/worldline-c_api.ads'
        original = path.read_text()
        for symbol, declaration in verifier._TYPED_EXPORT_DECLARATIONS.items():
            with self.subTest(symbol=symbol, mutation='profile'):
                # Changing the result ABI leaves the external symbol intact.
                name = declaration.split('(', 1)[0].strip().split()[-1]
                start = original.index('function ' + name)
                end = original.index('External_Name => "' + symbol + '";', start)
                chunk = original[start:end]
                self.assertIn('return Interfaces.', chunk)
                changed = chunk.replace('return Interfaces.', 'return Standard.', 1)
                path.write_text(original[:start] + changed + original[end:])
                self.assert_refused('typed export ABI declaration differs: ' + symbol)
            with self.subTest(symbol=symbol, mutation='duplicate'):
                path.write_text(original + '\n' + declaration + '\n')
                self.assert_refused('typed export binding inventory differs: ' + symbol)
            path.write_text(original)

    def test_rebound_symbol_refuses_even_if_original_profile_name_survives(self):
        self.replace('core/worldline-c_api.ads',
                     'function Finalization_Decide (Input, Output : System.Address)',
                     'function Wrong_Decision (Input, Output : System.Address)')
        self.assert_refused('typed export ABI declaration differs: wl_finalization_decide_v1')

    def test_legacy_and_typed_duplicate_bindings_refuse(self):
        path = self.root / 'core/worldline-recovery_protocol_c_api.ads'
        path.write_text(path.read_text() + '\nfunction Bypass return Interfaces.C.int '
                        'with Export, Convention => C, '
                        'External_Name => "wl_recovery_protocol_decide_v1";\n')
        self.assert_refused('typed export binding inventory differs: wl_recovery_protocol_decide_v1')

    def test_pragma_export_duplicate_in_another_unit_refuses(self):
        path = self.root / 'core/worldline.ads'
        path.write_text(path.read_text() + '\npragma Export '
                        '(C, Bypass, "wl_chain_authority_replay_v1");\n')
        self.assert_refused('typed export binding inventory differs: wl_chain_authority_replay_v1')

    def test_comment_text_cannot_create_a_binding_or_hide_a_body_change(self):
        path = self.root / 'core/worldline-c_api.ads'
        original = path.read_bytes()
        path.write_bytes(original + b'\n-- pragma Export '
                         b'(C, Bypass, "wl_chain_authority_replay_v1");\n')
        problems = verifier.export_problems(self.root)
        self.assertFalse(any('typed export binding inventory differs:' in item
                             for item in problems), problems)
        self.assertEqual(problems, [
            'typed export raw transport bytes differ: core/worldline-c_api.ads'])
        # Restore the exact baseline before the independent body mutation.
        path.write_bytes(original)
        self.assertEqual(verifier.export_problems(self.root), [])
        self.change_function('core/worldline-c_api.adb', 'Owned_recovery_protocol',
                             'if Status = 0 then', 'if True then')
        problems = verifier.export_problems(self.root)
        self.assertIn('typed export raw transport bytes differ: core/worldline-c_api.adb', problems)
        self.assertNotIn('typed export raw transport bytes differ: core/worldline-c_api.ads', problems)

    def test_existing_ada_literal_whitespace_is_bound_by_raw_bytes(self):
        path = self.root / 'core/worldline-c_api.adb'
        original = path.read_bytes()
        before = b'"wl_excluded_source_owner_decide_v1: "'
        after = b'"wl_excluded_source_owner_decide_v1:  "'
        self.assertEqual(original.count(before), 1)
        changed = original.replace(before, after, 1)
        self.assertNotEqual(changed, original)
        # This existing runtime diagnostic literal exposes the inherited
        # normalizer blind spot without changing the normalizer or its pins.
        self.assertEqual(verifier.normalized_ada(original.decode('utf-8')),
                         verifier.normalized_ada(changed.decode('utf-8')))
        path.write_bytes(changed)
        problems = verifier.export_problems(self.root)
        self.assertNotIn(
            'typed export normalized transport projection differs: core/worldline-c_api.adb',
            problems)
        self.assertEqual(problems, [
            'typed export raw transport bytes differ: core/worldline-c_api.adb'])

    def test_transport_check_cannot_be_replaced_by_an_unreachable_guard(self):
        self.change_function('core/worldline-c_api.adb', 'Owned_recovery_protocol',
            'if not Native.Transport_Valid (Input, Input_Length, Output, Output_Length) then',
            'if False then')
        self.assert_refused('typed export raw transport bytes differ: core/worldline-c_api.adb')

    def test_complete_arena_copy_cannot_be_replaced_by_zeroes(self):
        self.replace('core/worldline-recovery_authorization_v3_c_api.adb',
                     'Read_Byte (Arena_View, Position, Data (Position));',
                     'Data (Position) := 0;')
        self.assert_refused('typed export raw transport bytes differ: core/worldline-recovery_authorization_v3_c_api.adb')

    def test_complete_row_copy_cannot_be_replaced_by_an_empty_loop(self):
        self.replace('core/worldline-chain_authority_c_api.adb',
                     "for I in Owned'Range loop", 'for I in 1 .. 0 loop')
        self.assert_refused('typed export raw transport bytes differ: core/worldline-chain_authority_c_api.adb')

    def test_result_write_helper_cannot_discard_typed_result(self):
        self.replace('core/worldline-chain_authority_c_api.adb', 'View.all := Item;', 'null;')
        self.assert_refused('typed export raw transport bytes differ: core/worldline-chain_authority_c_api.adb')

    def test_typed_callee_alias_cannot_be_rebound(self):
        self.change_function('core/worldline-c_api.adb', 'Owned_recovery_protocol',
            'package Native renames Worldline.Recovery_Protocol_C_API;',
            'package Native renames Worldline.Recovery_Authorization_C_API;')
        self.assert_refused('typed export raw transport bytes differ: core/worldline-c_api.adb')

    def test_typed_chain_decision_call_cannot_become_a_dummy_call(self):
        self.replace('core/worldline-chain_authority_c_api.adb',
                     'Write_Result (Output_View, W.Decide (Owned, H));',
                     'if False then Write_Result (Output_View, W.Decide (Owned, H)); end if;')
        self.assert_refused('typed export raw transport bytes differ: core/worldline-chain_authority_c_api.adb')

    def test_fail_closed_exception_return_cannot_be_success(self):
        self.change_function('core/worldline-c_api.adb', 'Owned_Chain_Replay',
                             'when others => return -1;', 'when others => return 0;')
        self.assert_refused('typed export raw transport bytes differ: core/worldline-c_api.adb')

    def test_layout_body_remains_bound(self):
        self.replace('core/worldline-recovery_protocol_c_api.adb',
                     "when 0 => return W.Raw_Request'Object_Size / System.Storage_Unit;",
                     'when 0 => return -1;')
        self.assert_refused('typed export raw transport bytes differ: core/worldline-recovery_protocol_c_api.adb')

    def test_finalization_full_data_copy_remains_bound(self):
        self.replace('core/evaluation_finalization_c.adb',
                     'Copy_Data (Input, Data_Length, A);', 'null;')
        self.assert_refused('typed export raw transport bytes differ: core/evaluation_finalization_c.adb')

    def test_partial_fixture_and_original_collapse_rebinding_fail_closed(self):
        # Retain the original test's minimal c_api.ads-only negative fixture.
        text = (ROOT / 'core/worldline-c_api.ads').read_text()
        with tempfile.TemporaryDirectory(prefix='worldline-export-negative-') as temporary:
            root = Path(temporary)
            (root / 'core').mkdir()
            marker = 'External_Name => "wl_collapse_decide"'
            changed = text.replace(marker, 'External_Name => "wl_collapse_decide_old"').replace(
                'External_Name => "wl_transaction_transition_allowed"', marker)
            (root / 'core/worldline-c_api.ads').write_text(changed)
            self.assertTrue(verifier.export_problems(root))


if __name__ == '__main__':
    unittest.main()
