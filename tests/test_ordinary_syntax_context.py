"""Pure context-transport controls; these do not execute or authorize an effect.

Uninitialized concrete handles exercise identity/refusal only. Original complete
recovery authority, packet producer and typed-absence production controls remain
required with their real owned resource handles and the same-source kernel.
"""
import unittest

from worldline.admission import Gate
from worldline.checks import CheckRunner
from worldline.linux.systemd import SystemdAdapter
from worldline.recovery_observation import ReadonlySyntaxContext
from worldline.revalidate import Revalidator
from worldline.transaction import CollapseTransaction


class OrdinarySyntaxContextTests(unittest.TestCase):
    def bindings(self):
        transaction = object.__new__(CollapseTransaction)
        owner = object.__new__(Revalidator)
        checks = object.__new__(CheckRunner)
        manager = object.__new__(SystemdAdapter)
        gate = object.__new__(Gate)
        for name in ('store', 'paths', 'core', 'config'):
            value = object()
            transaction.__dict__[name] = value
            owner.__dict__[name] = value
        checks.__dict__.update(paths=transaction.paths, systemd=manager, gate=gate)
        owner.__dict__['checks'] = checks
        transaction.__dict__.update(
            validator=owner.validate_staged,
            staged_subject_validator=owner.validate_staged_for_subject)
        return transaction, owner, checks, manager, gate

    def test_same_owner_borrows_the_existing_handles(self):
        transaction, owner, checks, manager, gate = self.bindings()
        context = transaction._ordinary_syntax_context()
        self.assertIs(type(context), ReadonlySyntaxContext)
        self.assertIs(context.core, transaction.core)
        self.assertIs(context.systemd, manager)
        self.assertIs(context.gate, gate)

    def test_legacy_selected_method_uses_its_own_handles(self):
        transaction, owner, checks, manager, gate = self.bindings()
        transaction.staged_subject_validator = None
        context = transaction._ordinary_syntax_context()
        self.assertIs(context.systemd, manager)
        self.assertIs(context.gate, gate)

    def test_equal_absences_never_form_a_context(self):
        for name in ('store', 'paths', 'core', 'config'):
            for absent in ('missing', 'none'):
                with self.subTest(name=name, absent=absent):
                    transaction, owner, checks, manager, gate = self.bindings()
                    if absent == 'missing':
                        del transaction.__dict__[name]
                        del owner.__dict__[name]
                    else:
                        transaction.__dict__[name] = None
                        owner.__dict__[name] = None
                    self.assertIsNone(transaction._ordinary_syntax_context())

    def test_missing_or_null_check_paths_stays_unavailable(self):
        for absent in ('missing', 'none'):
            with self.subTest(absent=absent):
                transaction, owner, checks, manager, gate = self.bindings()
                if absent == 'missing':
                    del checks.__dict__['paths']
                else:
                    checks.__dict__['paths'] = None
                self.assertIsNone(transaction._ordinary_syntax_context())

    def test_lookalike_identity_handles_do_not_join(self):
        for name in ('store', 'paths', 'core', 'config'):
            with self.subTest(name=name):
                transaction, owner, checks, manager, gate = self.bindings()
                owner.__dict__[name] = object()
                self.assertIsNone(transaction._ordinary_syntax_context())

    def test_different_known_validator_owners_do_not_join(self):
        transaction, owner, checks, manager, gate = self.bindings()
        other = object.__new__(Revalidator)
        transaction.validator = other.validate_staged
        self.assertIsNone(transaction._ordinary_syntax_context())

    def test_custom_subject_does_not_fall_back_or_execute(self):
        transaction, owner, checks, manager, gate = self.bindings()
        def custom(*args, **kwargs):
            self.fail('context discovery executed a callback')
        transaction.staged_subject_validator = custom
        self.assertIsNone(transaction._ordinary_syntax_context())

    def test_custom_legacy_method_is_not_executed(self):
        transaction, owner, checks, manager, gate = self.bindings()
        transaction.staged_subject_validator = None
        def custom(*args, **kwargs):
            self.fail('context discovery executed a callback')
        transaction.validator = custom
        self.assertIsNone(transaction._ordinary_syntax_context())

    def test_unrecognized_owner_subclass_stays_unavailable(self):
        transaction, owner, checks, manager, gate = self.bindings()
        class CustomRevalidator(Revalidator):
            pass
        other = object.__new__(CustomRevalidator)
        transaction.staged_subject_validator = other.validate_staged_for_subject
        self.assertIsNone(transaction._ordinary_syntax_context())

    def test_unknown_check_manager_or_gate_stays_unavailable(self):
        for name in ('checks', 'systemd', 'gate'):
            with self.subTest(name=name):
                transaction, owner, checks, manager, gate = self.bindings()
                target = owner if name == 'checks' else checks
                target.__dict__[name] = object()
                self.assertIsNone(transaction._ordinary_syntax_context())


if __name__ == '__main__':
    unittest.main()
