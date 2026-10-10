"""Offline operator-only custody provisioning; never called by startup."""
from __future__ import annotations
import fcntl
import os
from pathlib import Path
import sys
from .protected_startup import require, protected, private_bytes, exact_json, digest
from .root_worker_custody import named_identity
from .retained_v1_migration_capture import RetainedContext, capture_retained_v1
from .custody_v2_provision_values import ExplicitInputs, Target, write_empty_artifacts
from .custody_provision_kernel import operands, decide_selected

PLAN_KEYS = frozenset(('schema', 'installation', 'startup_descriptor', 'entry', 'early_envelope',
                      'helper', 'sources', 'worker_policy', 'cost_key', 'native_components',
                      'handoff_genesis', 'handoff_journal', 'child_dispatch'))
PRIOR_KEYS = frozenset(('descriptor_path', 'descriptor_sha256', 'plan_path', 'plan_sha256',
                       'genesis_path', 'genesis_sha256', 'journal_path', 'journal_sha256',
                       'head_event', 'issuer_key_sha256'))
class OfflineCustodyProvisioner:
    def __init__(self, request_path):
        self.closed = False; self.written = False; self.poisoned = False
        self.fds = {}; self.directories = {}; self.prior = None; self.fixed = {}
        require(os.geteuid() == 0, 'CUSTODY_PROVISION_ROOT_REQUIRED')
        module = sys.modules.get('_worldline_approved_source_loader')
        require(type(module) is type(sys), 'CUSTODY_PROVISION_EARLY_SOURCE_REQUIRED')
        self.source_lease = module.current()
        require(type(self.source_lease) is module.ApprovedSourceLease,
                'CUSTODY_PROVISION_REAL_SOURCE_LEASE_REQUIRED')
        self.source_lease.check()
        require(sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
                and not any(key.startswith(('PYTHON', 'LD_')) for key in os.environ),
                'CUSTODY_PROVISION_ISOLATED_ENTRY_REQUIRED')
        self.request_raw = self._selected(request_path)
        self.request = exact_json(self.request_raw)
        require(type(self.request) is dict and set(self.request) ==
                {'schema', 'mode', 'descriptor', 'plan', 'genesis_input', 'prior'}
                and self.request['schema'] == 'worldline.custody-v2-provision-request-v1'
                and self.request['mode'] in ('NEW', 'MIGRATE'), 'CUSTODY_PROVISION_REQUEST_SCHEMA')
        self.descriptor_path = Path(self.request['descriptor'])
        self.plan_path = Path(self.request['plan'])
        self.descriptor_raw = self._selected(self.descriptor_path)
        self.plan_raw = self._selected(self.plan_path)
        self.genesis_raw = self._selected(self.request['genesis_input'])
        self.spec = exact_json(self.descriptor_raw); self.plan = exact_json(self.plan_raw)
        self.genesis = exact_json(self.genesis_raw)
        require(type(self.plan) is dict and set(self.plan) == PLAN_KEYS and
                self.plan['schema'] == 'worldline.protected-root-worker-plan-v1',
                'CUSTODY_PROVISION_COMPLETE_PLAN_REQUIRED')
        require(type(self.spec) is dict and type(self.spec.get('root_worker')) is dict and
                set(self.spec['root_worker']) == {'owner_plan'} and
                self.spec['root_worker']['owner_plan'] == str(self.plan_path),
                'CUSTODY_PROVISION_DESCRIPTOR_PLAN_SELECTION')
        entry = Path(self.spec['runtime']['worldline_source']) / 'protected-root/provision_root_custody_v2.py'
        require(Path(sys.argv[0]) == entry and self.source_lease.files.get(str(entry), (None,))[0] == 'ENTRY'
                and any(event['kind'] == 'ENTRY_COMPILED_BEFORE_EXEC' and event['path'] == str(entry)
                        for event in self.source_lease.events), 'CUSTODY_PROVISION_SELECTED_OPERATOR_ENTRY_REQUIRED')
        self.source_lease.file(str(entry), ('ENTRY',))
        self.key_path = Path(self.spec['paths']['authority_root']) / 'authority/issuer/state/issuer-key.bin'
        self.key = self._selected(self.key_path)
        require(self.genesis['prior_custody'] == self.request['prior'] and
                (self.request['prior'] is None) == (self.request['mode'] == 'NEW'),
                'CUSTODY_PROVISION_EXPLICIT_PRIOR_CHANGED')
        self.journal_path = Path(self.plan['handoff_journal'])
        self.genesis_path = Path(self.plan['handoff_genesis'])
        self.lock_path = Path(str(self.journal_path) + '.lock')
        outputs = (self.journal_path, self.genesis_path, self.lock_path)
        require(len(set(outputs)) == len(outputs) and all(path.is_absolute() for path in outputs)
                and not set(map(str, outputs)) & set(self.fixed), 'CUSTODY_PROVISION_EXACT_NEW_OUTPUTS_REQUIRED')
        for path in outputs:
            require(str(path) not in self.source_lease.files and str(path) not in self.source_lease.absent,
                    'CUSTODY_PROVISION_OUTPUT_NOT_FIXED_SOURCE_DATA')
        try:
            self._locks()
            if self.request['mode'] == 'MIGRATE':
                prior = self.request['prior']
                require(type(prior) is dict and set(prior) == PRIOR_KEYS, 'CUSTODY_PROVISION_PRIOR_KEYSET')
                self.prior = capture_retained_v1(self.source_lease,
                    RetainedContext(**prior, installation=self.spec['installation_id']))
                for path, expected in ((prior['descriptor_path'], prior['descriptor_sha256']),
                                       (prior['plan_path'], prior['plan_sha256']),
                                       (prior['genesis_path'], prior['genesis_sha256']),
                                       (prior['journal_path'], prior['journal_sha256'])):
                    require(self.spec['files'].get(path, {}).get('sha256') == expected,
                            'CUSTODY_PROVISION_RETAINED_DATA_NOT_IN_DESCRIPTOR')
            for path in outputs:
                parent = path.parent
                if parent not in self.directories:
                    protected(parent, directory=True)
                    self.directories[parent] = os.open(parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
            from .core import Core
            from .proof_manifest import contract_problems, manifest_problems
            runtime = self.spec['runtime']; library = Path(runtime['native_library'])
            self._selected(library, data_only=False)
            proof = exact_json(self._selected(runtime['proof_manifest']), canonical_required=False)
            summary = self._selected(runtime['proof_summary'])
            require(not contract_problems(Path(runtime['worldline_source'])) and
                    not manifest_problems(proof, Path(runtime['worldline_source']), library=library,
                                          summary=summary, require_summary=True),
                    'CUSTODY_PROVISION_EXACT_NATIVE_PROOF_REQUIRED')
            self.core = Core(library)
            self.intact()
        except BaseException:
            self.close(); raise
    def _selected(self, path, *, data_only=True):
        path = Path(path)
        require(path.is_absolute(), 'CUSTODY_PROVISION_ABSOLUTE_SELECTED_PATH_REQUIRED')
        raw = private_bytes(path)
        word = str(path)
        roles = ('DATA',) if data_only else (self.source_lease.files.get(word, (None,))[0],)
        require(self.source_lease.file(word, roles) == raw, 'CUSTODY_PROVISION_SELECTED_BYTES_CHANGED')
        self.fixed[word] = raw
        return raw
    def _lock_paths(self):
        root = Path(self.spec['paths']['authority_root']); state = Path(self.spec['paths']['state'])
        paths = [state / 'worldline-store.lock', root / 'authority/gate/state/gate.lock',
                 root / 'authority/state/broker.lock', root / 'authority/issuer/state/issuer.lock',
                 root / 'authority/universe/root/universe.lock', root / 'authority/evidence/state/evidence.lock',
                 Path(self.spec['paths']['runtime']) / 'admission.lock']
        transactions = self.spec['actuator_transactions']; actuator = root / 'canonical/actuator'
        require(type(transactions) is list and all(type(word) is str and word and '/' not in word
                and word not in ('.', '..') for word in transactions) and len(set(transactions)) == len(transactions),
                'CUSTODY_PROVISION_ACTUATOR_ROSTER_INVALID')
        protected(actuator, directory=True)
        require(sorted(path.name for path in actuator.iterdir()) == sorted(transactions),
                'CUSTODY_PROVISION_ACTUATOR_ROSTER_CHANGED')
        paths.extend(actuator / word / 'service.lock' for word in transactions)
        require(len(set(paths)) == len(paths), 'CUSTODY_PROVISION_LOCK_ALIAS')
        return tuple(paths)
    def _locks(self):
        for path in self._lock_paths():
            private_bytes(path)
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB); named_identity(fd, path)
            except BaseException:
                os.close(fd); raise
            self.fds[path] = fd
    def intact(self):
        require(not self.closed and not self.poisoned, 'CUSTODY_PROVISION_LEASE_UNAVAILABLE')
        self.source_lease.check()
        for path, raw in self.fixed.items():
            require(private_bytes(path) == raw, 'CUSTODY_PROVISION_AUTHENTIC_INPUT_CHANGED')
        require(set(self._lock_paths()) == set(self.fds), 'CUSTODY_PROVISION_LOCK_ROSTER_CHANGED')
        for path, fd in self.fds.items():
            named_identity(fd, path); fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        for path, fd in self.directories.items():
            held = os.fstat(fd); named = protected(path, directory=True)
            require((held.st_dev, held.st_ino) == (named.st_dev, named.st_ino),
                    'CUSTODY_PROVISION_RETAINED_DIRECTORY_REPLACED')
        if self.prior is not None: self.prior.intact()
    def native_inputs(self):
        self.intact()
        return operands(self.descriptor_raw, self.plan_raw, self.genesis_raw, str(self.descriptor_path),
                        str(self.plan_path), str(self.genesis_path), str(self.journal_path), self.key,
                        self.request['mode'], self.prior)
    def provision(self):
        require(not self.written, 'CUSTODY_PROVISION_ONCE_ONLY')
        decision = decide_selected(self)
        expected = 'New_Origin_Eligible' if self.request['mode'] == 'NEW' else 'Closed_V1_Migration_Eligible'
        require(decision.state == expected, 'CUSTODY_PROVISION_NATIVE_' + decision.state)
        self.intact()
        def target(path): return Target(self.directories[path.parent], path.name)
        try:
            # Last native redecision before the exclusive-create writer's first
            # effect. Original locks and read-only v1 capture remain held.
            require(decide_selected(self) == decision, 'CUSTODY_PROVISION_REDECISION_CHANGED')
            result = write_empty_artifacts(ExplicitInputs(self.descriptor_raw, self.plan_raw, self.genesis_raw, self.key),
                                          target(self.journal_path), target(self.genesis_path), target(self.lock_path))
            self.written = True
            self.intact()
            return result
        except BaseException:
            self.poisoned = True; raise
    def close(self):
        if self.closed: return
        self.closed = True
        failures = []
        if self.prior is not None:
            try: self.prior.close()
            except BaseException as error: failures.append(error)
        for fd in reversed(tuple(self.directories.values()) + tuple(self.fds.values())):
            try: os.close(fd)
            except BaseException as error: failures.append(error)
        self.directories.clear(); self.fds.clear()
        if failures:
            self.poisoned = True
            if sys.exc_info()[1] is None: raise failures[0]

def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description='Explicit protected offline custody-v2 provisioning')
    parser.add_argument('--request', required=True)
    args = parser.parse_args(argv)
    owner = OfflineCustodyProvisioner(args.request)
    try:
        result = owner.provision()
        from .protected_startup import canonical
        print(canonical({'state': result.state, 'genesis_sha256': result.genesis_sha256,
                         'journal_sha256': result.journal_sha256, 'origin': result.origin}).decode())
    finally: owner.close()
