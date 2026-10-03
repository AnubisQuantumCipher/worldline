"""Actual content-free acquisition followed by an external native seal.

No pending intent or preliminary ContentID is allocated for finalization.
Earlier observations keep their full original bytes. Only a native-admitted
post-recapture completion enters the immutable returned capture.
"""
from __future__ import annotations

from dataclasses import asdict
import hashlib
import os
from pathlib import Path
import uuid

from .core import hash_bytes_from_id
from .completion_kernel import EXECUTION
from .errors import WorldlineError
from .evaluation_pending import identity, text
from .evaluation_terminal import bytes_value, value_bytes
from .evaluation_wire import Authority, record
from .finalization_journal import FinalizationJournal, encode, decode, acquisitions_payload
from .finalization_values import (StartValue, InputValue, UnsealedResult,
    CaptureValue, ComponentsValue, SealValue)


def _owned(value):
    return bytes_value(value_bytes(value))


def _owned_acquisition(value):
    # Acquisition records include full bytes and tuple identities. Use the
    # journal's existing lossless grammar rather than the JSON result grammar.
    return decode(encode(value))


class EngineFinalizationWriter:
    def __init__(self, journal, core):
        if type(journal) is not FinalizationJournal:
            raise WorldlineError('FINALIZATION_AUTHORITY_UNAVAILABLE',
                                 'the real finalization journal is not provisioned')
        self.journal, self.core = journal, core
        self.start = self.input = self.capture = self.sealed = None
        self.invocations = {}
        self.invocation_order = []
        self.actual_returns = {}
        self.raw_observations = {}
        self.declarations = {}
        self.rows = []
        self.retained = False
        self.source = None
        self.header = None
        self.whole_run_observation = None
        self._agent_acquisitions = []
        self._raw_events = []
        self._acquisition_generation = None
        self._acquisition_failure = None

    def _require_acquisitions_open(self):
        if self._acquisition_generation is not None:
            raise WorldlineError('FINALIZATION_ACQUISITION_CLOSED',
                                 'the retained acquisition generation is already closed')

    def _register_agent_acquisition(self, owner):
        from .runner import _AgentAcquisition
        if type(owner) is not _AgentAcquisition or owner.writer is not self:
            raise WorldlineError('FINALIZATION_ACQUISITION_OWNER_INVALID',
                                 'the acquisition does not belong to this writer')
        with self.journal.lock:
            self._require_acquisitions_open()
            self._agent_acquisitions.append(owner)

    def _close_acquisitions(self):
        # Every asynchronous agent owner is registered before effects. Each
        # owner derives quiescence from actual thread/process/socket state; no
        # completion Boolean supplied by a check or a returned payload is used.
        with self.journal.lock:
            if self._acquisition_generation is not None:
                self._require_acquisitions_closed()
                return
            if self._acquisition_failure is not None:
                raise WorldlineError('FINALIZATION_ACQUISITION_RETENTION_FAILED',
                    'an actual raw acquisition was not retained') from self._acquisition_failure
            if any(not owner.finished or not owner.quiescent() for owner in self._agent_acquisitions):
                raise WorldlineError('FINALIZATION_ACQUISITION_NOT_QUIESCENT',
                    'an owned acquisition still lacks actual terminal cleanup')
            value = _owned_acquisition({'state': 'closed', 'run': self.start.run,
                'owners': [owner.quiescence_observation() for owner in self._agent_acquisitions],
                'rawEvents': self._raw_events})
            self.journal.observe(self.start, b'acquisition-generation-closed:' + self.start.run,
                self.start.run, 'acquisition-generation-closed', value)
            # Set only after durable retention. The same lock protects every
            # raw append, registration and the immutable generation frontier.
            self._acquisition_generation = value

    def _require_acquisitions_closed(self):
        with self.journal.lock:
            if (self._acquisition_generation is None or self._acquisition_failure is not None
                    or any(not owner.finished or not owner.quiescent()
                           for owner in self._agent_acquisitions)):
                raise WorldlineError('FINALIZATION_ACQUISITION_NOT_QUIESCENT',
                                     'capture and seal require the owned closed generation')

    def begin(self, *, world, roots, requirement, known_components, required_checks):
        from .finalize import (ENGINE_DECLARATIONS, CheckDeclaration,
                               check_declarations, required_roster)
        if self.start is not None:
            raise WorldlineError('FINALIZATION_WRITER_ALREADY_BEGUN', 'start is immutable')
        requirement = _owned(requirement)
        declarations = check_declarations(requirement)
        declarations['agent'] = ENGINE_DECLARATIONS['agent']
        if requirement['policy']['canonical'].get('protected'):
            declarations['protected-paths'] = ENGINE_DECLARATIONS['protected-paths']
        declarations['verifiers-modified'] = CheckDeclaration('engine', None, False, origin='engine')
        declarations['evaluation-complete'] = CheckDeclaration('engine', None, False, origin='engine')
        required, empty = required_roster(requirement)
        # Preserve the applicable policy roster, its order, and all engine-owned
        # required checks. The whole declaration is frozen before effects.
        for name in required_checks:
            if name not in required:
                required.append(name)
        if 'verifiers-modified' not in required:
            required.append('verifiers-modified')
        frozen_required = tuple((identity(name), value_bytes(
            None if declarations.get(name) is None else asdict(declarations[name])))
            for name in required)
        previous = self.journal.discover(world.instance_id)
        run = identity(str(uuid.uuid4())) if previous is None else previous.run
        self.source = identity('finalization:' + world.instance_id)
        start = StartValue(self.journal.store_id, identity(world.instance_id), run, b'',
            identity(requirement['requirementHash']), value_bytes(requirement),
            value_bytes(requirement.get('verifiers', [])),
            encode({'world': world.record(), 'roots': list(roots), 'captureSource': self.source}),
            hash_bytes_from_id(world.parent_content),
            hash_bytes_from_id(known_components['config']),
            hash_bytes_from_id(known_components['repository']), frozen_required,
            ('Explicit_Empty' if empty else 'Missing_Declaration') if not required else 'Required_Checks')
        if previous is not None and previous != start:
            raise WorldlineError('FINALIZATION_START_REPLAY_CONFLICT',
                                 'the existing intent has different full antecedent observations')
        self.start = self.journal.reserve(start)
        self.journal.observe(self.start, b'capture-header:' + self.start.run,
            self.start.run, 'capture-header', {'source': self.source, 'start': encode({
                'world': world.record(), 'roots': list(roots)})})
        self.journal.claim_execution(self.start)
        self.declarations = declarations
        return self.start

    def record_input(self, snapshot):
        from .manifest import Manifest
        if self.start is None or self.input is not None:
            raise WorldlineError('FINALIZATION_INPUT_STATE_INVALID', 'input is immutable')
        components = Manifest.component_roots(snapshot.manifests.values(), self.core)
        manifests = encode(tuple((key, item.canonical)
                                 for key, item in snapshot.manifests.items()))
        value = InputValue(self.start, identity(snapshot.root_hash), manifests,
            hash_bytes_from_id(components['filesystem']),
            hash_bytes_from_id(components['config']),
            hash_bytes_from_id(components['repository']))
        self.input = self.journal.record_input(self.start, value)
        antecedent = decode(self.start.base_context)
        world = antecedent['world']
        self.header = _owned({'source': text(self.source),
            'subject': {'instanceId': world['instance_id'], 'alias': world['alias'],
                        'baseRoot': world['base_root'], 'rootSetHash': world['root_set_hash'],
                        'missionHash': world['mission_hash']},
            'requirement': bytes_value(self.start.policy),
            'measurement': {'worldInstance': world['instance_id'],
                'storedRootSetHash': world['root_set_hash'],
                'observedContentRoot': snapshot.root_hash,
                'manifests': {key: item.value for key, item in snapshot.manifests.items()}},
            'run': text(self.start.run), 'evaluationEpoch': 0,
            'storeId': text(self.start.store_id)})
        self.journal.observe(self.start, b'input-header:' + self.start.run,
                             self.start.run, 'input-header', self.header)
        return self.input

    def invocation_started(self, *, world_instance, check, invocation,
                           candidate_snapshot, verifier_entries):
        if self.start is None or identity(world_instance) != self.start.subject:
            raise WorldlineError('FINALIZATION_INVOCATION_SUBJECT_MISMATCH', 'start is absent or belongs elsewhere')
        observed = _owned({'worldInstance': world_instance, 'checkId': check,
            'invocationId': invocation, 'candidateSnapshot': candidate_snapshot,
            'verifierEntries': list(verifier_entries), 'evaluationRun': text(self.start.run)})
        with self.journal.lock:
            self._require_acquisitions_open()
            self.invocations.pop((world_instance, check), None)
            self.journal.observe(self.start, b'start:' + identity(invocation),
                                 identity(invocation), 'invocation-start', observed)
            self.invocations[(world_instance, check)] = (invocation, observed)
            self.invocation_order.append((invocation, observed))

    def invocation_result(self, *, world_instance, check, result):
        item = self.invocations.get((world_instance, check))
        if item is None:
            raise WorldlineError('FINALIZATION_INVOCATION_START_MISSING', 'no actual retained invocation')
        invocation, started = item
        observed = _owned({'started': started, 'result': result})
        # Observe the returned argument before a possible persistence refusal.
        with self.journal.lock:
            self._require_acquisitions_open()
            self.actual_returns[invocation] = observed
            self.journal.observe(self.start, b'return:' + identity(invocation),
                                 identity(invocation), 'invocation-return', observed)

    def invocation_raw(self, *, world_instance, check, kind, observed, occurrence=None):
        item = self.invocations.get((world_instance, check))
        if item is None:
            raise WorldlineError('FINALIZATION_INVOCATION_START_MISSING', 'no actual retained invocation')
        invocation, _started = item
        value = _owned_acquisition({'kind': kind, 'observation': observed,
                        **({} if occurrence is None else {'occurrence': occurrence})})
        with self.journal.lock:
            self._require_acquisitions_open()
            self.raw_observations.setdefault(invocation, []).append(value)
            event = identity(str(uuid.uuid4()))
            try:
                self.journal.observe(self.start, event,
                                     identity(invocation), 'raw-acquisition', value)
            except BaseException as error:
                self._acquisition_failure = error
                raise
            self._raw_events.append((identity(invocation), event))

    def invocation_exception(self, *, world_instance, check, error):
        if (world_instance, check) not in self.invocations:
            return
        from .raw_observation import exception_observation
        self.invocation_raw(world_instance=world_instance, check=check,
                            kind='invocation-exception', observed=exception_observation(error))

    def _row(self, value):
        value = _owned(value)
        check = value.get('id')
        declared = self.declarations.get(str(check))
        wire = record(value, declared)
        execution, outcome, _bundle, _report, _admitted = Authority(self.core).evaluate(wire)
        names = {name.upper(): name for name in EXECUTION}
        if execution not in names:
            raise WorldlineError('FINALIZATION_CLASSIFICATION_UNKNOWN', 'actual native enum is not representable')
        invocation = value.get('engineInvocationObservation')
        boundary = value.get('evaluatorBoundary')
        observed_execution = (None if invocation is None and boundary is None else
                              {'engineInvocation': invocation, 'evaluatorBoundary': boundary})
        verifier = value.get('executedVerifierSet')
        return UnsealedResult(self.start,
            identity(check) if isinstance(check, str) else value_bytes(check),
            value_bytes(value.get('origin')),
            None if observed_execution is None else value_bytes(observed_execution),
            None if verifier is None else value_bytes(verifier), names[execution],
            None if outcome == 'NONE' else outcome, value_bytes(value),
            value_bytes(None if declared is None else asdict(declared)), wire)

    def finish_capture(self, *, context, results, post_snapshot):
        # Own the actual returned arguments before validation, classification,
        # or storage can refuse. This is not a completion observation.
        self.whole_run_observation = decode(encode({'returnedContext': context,
            'rawResults': list(results), 'postSnapshot': {
                'worldInstance': post_snapshot.world_instance,
                'directory': os.fsencode(post_snapshot.directory),
                'root': post_snapshot.root_hash,
                'manifests': tuple((key, item.canonical)
                                   for key, item in post_snapshot.manifests.items())}}))
        if self.start is None or self.input is None or self.capture is not None:
            raise WorldlineError('FINALIZATION_CAPTURE_STATE_INVALID', 'actual input is absent or capture returned')
        context = _owned(context)
        rows = _owned(list(results))
        # Each actual check return is preserved positionally. Additional owned
        # engine records do not erase an invocation or a duplicate check row.
        return_index = 0
        for row in rows:
            if return_index < len(self.invocation_order):
                invocation, started = self.invocation_order[return_index]
                returned = self.actual_returns.get(invocation)
                if returned is not None and row.get('id') == started['checkId']:
                    original = returned['result']
                    if any(key not in row or value_bytes(row[key]) != value_bytes(val)
                           for key, val in original.items()
                           if key not in ('executionBinding', 'evaluation')):
                        raise WorldlineError('FINALIZATION_RETURN_PREFIX_CHANGED', 'actual returned row was rewritten')
                    row['engineInvocationObservation'] = started
                    row['rawRunnerResult'] = original
                    row['engineRawObservations'] = acquisitions_payload(
                        self.raw_observations.get(invocation, []))
                    return_index += 1
        if return_index != len(self.invocation_order):
            raise WorldlineError('FINALIZATION_INVOCATION_HAS_NO_RETURN', 'the whole ordered invocation stream is incomplete')
        self._close_acquisitions()
        rows.append({'id': 'verifiers-modified', 'origin': 'engine', 'format': 'engine',
                     'required': True, 'status': 'FAIL' if context['verifiersModifiedByCandidate'] else 'PASS',
                     'modified': context['verifiersModifiedByCandidate']})
        typed = tuple(self._row(row) for row in rows)
        for row in typed:
            self.journal.record_result(self.start, identity(str(uuid.uuid4())), self.start.run, row)
        post_manifests = encode(tuple((key, item.canonical)
                                      for key, item in post_snapshot.manifests.items()))
        runner_results = [self.actual_returns[invocation]['result']
                          for invocation, _started in self.invocation_order]
        observed = {'source': 'finalization-return', 'returnedContext': context,
            'captureContext': self.header, 'runnerResults': runner_results,
            'postMeasurement': {'observedContentRoot': post_snapshot.root_hash,
                'manifests': {key: item.value for key, item in post_snapshot.manifests.items()}},
            'start': {'storeId': text(self.start.store_id), 'worldInstance': text(self.start.subject),
                      'run': text(self.start.run), 'evaluationEpoch': 0},
            'inputRoot': text(self.input.root), 'postRoot': post_snapshot.root_hash,
            'rawResults': rows}
        completion = {'id': 'evaluation-complete', 'origin': 'engine', 'format': 'engine',
            'status': 'PASS', 'required': True, 'epoch': 0,
            'validationId': text(self.start.run), 'requirementHash': text(self.start.requirement),
            'examinedContentRoot': text(self.input.root),
            'resultsDigest': hashlib.sha256(value_bytes(rows)).hexdigest(),
            'digestEncoding': 'worldline-lossless-capture-v1', 'captureObservation': observed}
        descriptor = (identity('evaluation-complete'),
                      value_bytes(asdict(self.declarations['evaluation-complete'])))
        proposed = CaptureValue(self.start, self.input, identity(post_snapshot.root_hash),
            post_manifests, value_bytes(context), self.source,
            typed + (self._row(completion),), descriptor)
        classification = self.journal.kernel.classify_capture(proposed)
        if classification.state == 'Completed':
            captured, retained_rows = proposed, rows + [completion]
        else:
            captured = CaptureValue(self.start, self.input, identity(post_snapshot.root_hash),
                post_manifests, value_bytes(context), self.source, typed, descriptor)
            retained_rows = rows
        actual = self.journal.retain_capture(captured)
        self.capture, self.rows = captured, retained_rows
        return actual

    def seal(self, world, evidence_path, environment_path):
        if self.capture is None or self.sealed is not None:
            raise WorldlineError('FINALIZATION_SEAL_STATE_INVALID', 'capture absent or immutable seal already returned')
        self._require_acquisitions_closed()
        # Read the actual frozen artifacts produced by the original algorithms.
        # Neither is rewritten to insert a future ContentID or this external seal.
        value = SealValue(self.capture, identity(world.content_id),
            ComponentsValue(hash_bytes_from_id(world.components['environment']),
                            hash_bytes_from_id(world.components['evidence'])),
            Path(evidence_path).read_bytes(), Path(environment_path).read_bytes())
        native = self.journal.kernel.seal(value)
        from .model import WorldState
        complete = (native.finalization_state == 'COMPLETED'
                    and native.finalization_outcome == 'PASS')
        world.risk = 'MEDIUM' if complete else 'HIGH'
        world.transition(WorldState.VALID if complete else WorldState.DEGRADED, self.core)
        self.sealed = self.journal.retain_seal(value, world.record())
        if self.sealed != native:
            raise WorldlineError('FINALIZATION_SEAL_CLASSIFICATION_CHANGED', 'native replay disagrees with the actual return')
        self.retained = True
        return self.sealed

    def interrupted(self, error):
        if self.start is None or self.retained:
            return
        from .raw_observation import exception_observation
        # This may be a provisional snapshot when an arbitrary in-process
        # provider has not ended. Its actual owner observations distinguish it
        # from a closed generation; no timeout is reported as termination.
        with self.journal.lock:
            returns = _owned(self.actual_returns)
            observation = _owned_acquisition({
                'phase': 'producer-interruption', 'exception': exception_observation(error),
                'inputReturned': self.input is not None, 'captureReturned': self.capture is not None,
                'actualInvocations': self.invocation_order, 'actualReturns': returns,
                'actualAcquisitions': self.raw_observations,
                'acquisitionGeneration': self._acquisition_generation,
                'acquisitionOwners': [owner.quiescence_observation()
                                      for owner in self._agent_acquisitions],
                'acquisitionsQuiescent': all(owner.finished and owner.quiescent()
                                             for owner in self._agent_acquisitions),
                'wholeRunReturnObserved': self.whole_run_observation})
        failures = []
        for invocation, observed in returns.items():
            try:
                self.journal.observe(self.start, b'return:' + identity(invocation),
                                     identity(invocation), 'invocation-return', observed)
            except BaseException as persistence_error:
                failures.append(persistence_error)
        observation['returnPersistenceRefusals'] = [exception_observation(item) for item in failures]
        self.journal.record_interruption(self.start, identity(str(uuid.uuid4())), observation)
        if failures:
            primary = failures[0]
            for additional in failures[1:]:
                primary.add_note('additional return persistence refusal: ' + repr(additional))
            raise primary
