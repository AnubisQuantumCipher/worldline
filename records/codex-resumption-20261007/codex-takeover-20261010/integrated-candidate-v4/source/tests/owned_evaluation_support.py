"""Owned ordinary transaction setup using actual producers and native authority.

The temporary stores and processes exercise the current API. They do not
establish protected production custody, finalization-only admission, external
confinement, or the full Phase1 guarantee. No producer observation is mocked.
"""
from __future__ import annotations

import base64
from contextlib import ExitStack
import os
from pathlib import Path
import sys
import uuid

from worldline.admission import AdmissionAuthority, Gate, Ledger
from worldline.agents.generic import GenericAdapter
from worldline.config import GenericAgentCommand, GlobalConfig
from worldline.evaluation_authority import read
from worldline.evaluation_pending import PendingJournal
from worldline.evaluation_terminal import TerminalJournal
from worldline.evaluation_pending import text
from worldline.finalization_journal import FinalizationJournal
from worldline.linux.inotify import InotifyWatcher
from worldline.linux.namespaces import BubblewrapSandbox
from worldline.linux.systemd import SystemdAdapter
from worldline.model import WorldState
from worldline.project import ProjectConfig
from worldline.revalidate import Revalidator
from worldline.runner import AgentRunner
from worldline.store import StateStore
from worldline.transaction import CollapseTransaction
from worldline.validation import current_requirements


# The generic adapter's only workload writes this owned candidate file. Encoding
# the value keeps GenericAgentCommand's placeholder expansion away from its
# contents; Python/shell source is never constructed from the requested value.
WRITE_STATE = (
    "import base64, pathlib, sys; "
    "pathlib.Path('state.txt').write_text("
    "base64.b64decode(sys.argv[1], validate=True).decode('utf-8'), encoding='utf-8')"
)


class OwnedTransactionEvaluation:
    def __init__(self, case, paths, core):
        self.case, self.paths, self.core = case, paths, core
        self._owned = ExitStack()
        self.watcher = None
        self.watch_events = []
        self.retained_runs = []
        try:
            paths.ensure()
            directory = paths.runtime / 'ordinary-evaluation'
            directory.mkdir(mode=0o700)
            self.pending = PendingJournal(
                directory / 'pending-journal.db', directory / 'pending-target.db',
                store_id='ordinary-transaction:' + str(uuid.uuid4()),
                library=Path(core.library_path), create=True)
            self._owned.callback(self.pending.close)
            self.terminal = TerminalJournal(
                self.pending, directory / 'terminal-journal.db',
                directory / 'terminal-target.db', library=Path(core.library_path), create=True)
            self._owned.callback(self.terminal.close)
            self.finalization = FinalizationJournal(directory / 'finalization-journal.db',
                text(self.pending.store), library=Path(core.library_path), create=True)
            self._owned.callback(self.finalization.close)
            self.store = StateStore(paths, core, evaluation_terminal=self.terminal,
                                    evaluation_finalization=self.finalization)
            self._owned.callback(self.store.close)
            self.config = GlobalConfig.default(paths)
            self.sandbox = BubblewrapSandbox(paths)
            self.systemd = SystemdAdapter()
            self.gate = Gate(
                AdmissionAuthority(Ledger(paths.runtime), self.config.admission_floors,
                                   paths={'data': paths.data, 'state': paths.state}),
                self.config.resource_policy)
            self.runner = AgentRunner(paths, self.store, self.config, self.sandbox,
                                      self.systemd, self.gate, core=core)
            self.revalidator = Revalidator(paths, self.store, self.config,
                self.sandbox, self.runner.checks, core=core)
        except BaseException:
            self._owned.close()
            raise

    def transaction(self):
        self.case.assertIsNone(self.watcher)
        roots = [(root['root_key'], self.paths.root_source(root))
                 for root in self.store.roots()]
        self.watcher = InotifyWatcher(roots, self.watch_events.append)
        self._owned.callback(self.watcher.close)
        return CollapseTransaction(self.paths, self.store, core=self.core,
            config=self.config, watcher=self.watcher,
            validator=self.revalidator.validate_staged,
            staged_subject_validator=self.revalidator.validate_staged_for_subject)

    def finalize_and_revalidate(self, world, value):
        """Run the actual agent, then obtain a distinct real retained evaluation.

        The later revalidation is explicit: this is not finalization-only
        coverage and does not synthesize an epoch-zero finalization record.
        """
        primary = next(root for root in self.store.roots() if root['primary_root'])
        project = ProjectConfig.load(
            Path(os.fsdecode(self.paths.root_source(primary))), self.store)
        self.case.assertEqual(project.checks, ())
        encoded = base64.b64encode(value.encode('utf-8')).decode('ascii')
        command = GenericAgentCommand(
            name='ordinary-transaction', argv=(sys.executable, '-c', WRITE_STATE, encoded),
            credential_mounts=(), event_format='jsonl', network_hosts=())
        finalized = self.runner.run(world.alias, GenericAdapter(command), world.cause, project)
        self.case.assertEqual(finalized.state, WorldState.VALID)
        agent = next(item for item in finalized.evidence['checks'] if item['id'] == 'agent')
        self.case.assertEqual(agent['origin'], 'agent')
        self.case.assertEqual(agent['exitCode'], 0)
        self.case.assertEqual(agent['supervision']['kind'], 'SUPERVISED')
        self.case.assertIs(agent['resources']['ceilingFired'], False)
        # These are observations returned by the real runner, not fixture
        # assignments or a substitute for the actual raw Decide call below.
        answer = self.revalidator.revalidate(finalized.alias)
        requirement = current_requirements(self.store, self.config, self.core)
        selected = read(self.store, finalized, requirement['requirementHash'], core=self.core)
        self.case.assertEqual(answer['evaluationCursor'], selected.cursor)
        self.case.assertEqual(answer['evaluationState'], 'COMPLETED')
        self.case.assertEqual(answer['outcome'], 'PASS')
        self.case.assertEqual(selected.results[-1]['id'], 'evaluation-complete')
        self.case.assertEqual(selected.observed['captureContext']['measurement']['contentId'],
                              finalized.content_id)
        self.retained_runs.append((answer, selected))
        return finalized

    def finalize_and_revalidate_mutation(self, world, value, mutation_source):
        """Run the actual agent, then obtain a distinct real retained evaluation.

        The later revalidation is explicit: this is not finalization-only
        coverage and does not synthesize an epoch-zero finalization record.
        """
        primary = next(root for root in self.store.roots() if root['primary_root'])
        project = ProjectConfig.load(
            Path(os.fsdecode(self.paths.root_source(primary))), self.store)
        encoded = base64.b64encode(value.encode('utf-8')).decode('ascii')
        command = GenericAgentCommand(
            name='ordinary-transaction', argv=(sys.executable, '-c', WRITE_STATE + '\n' + mutation_source, encoded),
            credential_mounts=(), event_format='jsonl', network_hosts=())
        finalized = self.runner.run(world.alias, GenericAdapter(command), world.cause, project)
        self.case.assertEqual(finalized.state, WorldState.VALID)
        agent = next(item for item in finalized.evidence['checks'] if item['id'] == 'agent')
        self.case.assertEqual(agent['origin'], 'agent')
        self.case.assertEqual(agent['exitCode'], 0)
        self.case.assertEqual(agent['supervision']['kind'], 'SUPERVISED')
        self.case.assertIs(agent['resources']['ceilingFired'], False)
        # These are observations returned by the real runner, not fixture
        # assignments or a substitute for the actual raw Decide call below.
        answer = self.revalidator.revalidate(finalized.alias)
        requirement = current_requirements(self.store, self.config, self.core)
        selected = read(self.store, finalized, requirement['requirementHash'], core=self.core)
        self.case.assertEqual(answer['evaluationCursor'], selected.cursor)
        self.case.assertEqual(answer['evaluationState'], 'COMPLETED')
        self.case.assertEqual(answer['outcome'], 'PASS')
        self.case.assertEqual(selected.results[-1]['id'], 'evaluation-complete')
        self.case.assertEqual(selected.observed['captureContext']['measurement']['contentId'],
                              finalized.content_id)
        self.retained_runs.append((answer, selected))
        return finalized

    def close(self):
        self._owned.close()
