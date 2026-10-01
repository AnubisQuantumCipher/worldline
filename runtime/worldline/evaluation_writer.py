"""Explicit engine capture hook; default runtime callers do not instantiate it.

The hook is reached by the real evaluator after source recapture. The exact
kernel classifications and full bytes are retained together. This code does not
upgrade them to authenticated producer facts or permit promotion. Protected
custody, full raw policy/evaluation wire, anti-rollback and default migration
remain separate required engineering obligations.
"""
from __future__ import annotations
import hashlib
from dataclasses import asdict
from .completion_observations import observations
from .core import (EVALUATION_ORIGINS, EVALUATION_STATUSES, EVALUATION_CHANNELS, EVALUATION_STAGES, EVALUATION_SUPERVISION)
from .completion_kernel import BoundValue, CaptureValue, CheckValue, EXECUTION
from .evaluation_pending import identity, text
from .evaluation_terminal import TerminalRefused, value_bytes
from .finalize import evaluation_record, CheckDeclaration, evaluation_presence

EXECUTION_NAMES = {name.upper(): name for name in EXECUTION}

class EngineEvaluationWriter:
    def __init__(self, terminal, content_identity: str):
        self.terminal = terminal
        self.content_identity = content_identity
        self.handle = None
        self.bound = None
        self.source = None
        self.retained = False
        self.invocations = {}
        self.actual_returns = {}
        self.actual_exceptions = {}
        self.whole_run_observation = None
        self.declarations = {}
        self.core = None

    def begin(self, subject, current, source, *, measured, declarations, core):
        if self.handle is not None: raise TerminalRefused('ENGINE_WRITER_ALREADY_BEGUN')
        self.terminal.enable_raw_capture()
        # Called after the actual input-manifest capture, before checks execute.
        # Scratch directory IDs remain distinct from this full run identity.
        self.handle = self.terminal.pending.begin(subject['instanceId'], self.content_identity,
                                                  current['requirementHash'])
        epoch = self.handle.epoch
        self.bound = BoundValue(identity(self.handle.store_id), identity(self.handle.subject),
            identity(self.handle.content), identity(self.handle.run),
            epoch.to_bytes((epoch.bit_length() + 7) // 8, 'little'), identity(current['requirementHash']))
        self.source = identity(source)
        self.declarations = dict(declarations)
        self.core = core
        self.terminal.open_stream(self.bound, self.source, value_bytes({
            'subject': subject, 'requirement': current, 'measurement': measured,
            'source': source, 'run': self.handle.run, 'evaluationEpoch': self.handle.epoch,
            'storeId': self.handle.store_id}))

    def _result(self, item, declarations, core):
        # Recompute from complete raw observations at this producer boundary;
        # never consume a saved admissible/completed Boolean as authority.
        declaration = declarations.get(str(item.get('id')))
        evaluation = evaluation_record(item, declared=declaration, core=core)
        observed = observations(item)
        facts = (EVALUATION_ORIGINS[observed.source], EVALUATION_STATUSES[observed.status],
            EVALUATION_CHANNELS[observed.channel], EVALUATION_STAGES[observed.stage],
            int(observed.exit_present), int(observed.exit_integer), EVALUATION_SUPERVISION[observed.supervisor],
            int(observed.supervisor_stopped), int(observed.bundle_present), int(observed.bundle_is_mapping),
            int(observed.bundle_stable), int(observed.bundle_changed), int(observed.unsatisfied_imports))
        present = evaluation_presence(item, declaration)
        evidence = tuple(getattr(present, name) for name in present.__dataclass_fields__)
        state = EXECUTION_NAMES.get(evaluation['executionStatus'])
        if state is None: raise TerminalRefused('ENGINE_CLASSIFICATION_UNKNOWN')
        outcome = evaluation['evaluationOutcome']
        if outcome == 'NONE': outcome = None
        check = item.get('id')
        check_bytes = identity(check) if isinstance(check, str) else value_bytes(check)
        execution = (None if item.get('engineInvocationObservation') is None and item.get('evaluatorBoundary') is None else
                     {'engineInvocation': item.get('engineInvocationObservation'), 'evaluatorBoundary': item.get('evaluatorBoundary')})
        executed = item.get('executedVerifierSet')
        # Complete present objects remain present byte identities. No malformed
        # present value silently becomes an absent verifier/execution identity.
        return CheckValue(self.bound, check_bytes, value_bytes(item.get('origin')),
            None if execution is None else value_bytes(execution),
            None if executed is None else value_bytes(executed), state, outcome, value_bytes(item), facts, evaluation['reportIntegrity'], evidence,
            value_bytes(None if declaration is None else asdict(declaration)))

    def finish(self, entry, *, raw_results, runner_results, post_measurement, required, empty_declared, declarations, core):
        from .evaluation_terminal import bytes_value
        # These are the actual arguments already received from the evaluator,
        # independently of whether the journal can be read or the final stream
        # can be admitted. Own them before any store operation or refusal check.
        # This observation is neither a D15 record nor a completion claim.
        received = bytes_value(value_bytes({
            'kind': 'whole-run-return-and-post-recapture-observation',
            'returnedEntry': entry, 'postMeasurement': post_measurement,
            'rawResults': raw_results, 'runnerResults': runner_results,
        }))
        self.whole_run_observation = received
        if type(received['returnedEntry']) is dict and 'context' in received['returnedEntry']:
            received['returnedContext'] = bytes_value(value_bytes(received['returnedEntry']['context']))
        # Work on a separate owned value: later annotation and ERROR projection
        # must not rewrite the original argument observation or borrow caller
        # containers that may subsequently change.
        working = bytes_value(value_bytes(received))
        entry = working['returnedEntry']
        raw_results = working['rawResults']
        runner_results = working['runnerResults']
        post_measurement = working['postMeasurement']
        if self.handle is None or self.retained: raise TerminalRefused('ENGINE_WRITER_STATE_INVALID')
        if identity(entry['requirementHash']) != self.bound.requirement:
            raise TerminalRefused('ENGINE_REQUIREMENT_CHANGED')
        # Own the full returned value before deriving the transport. The lossless
        # encoder preserves numeric/string domains and dict/array order.
        captured = bytes_value(value_bytes(entry))
        rows = bytes_value(value_bytes(raw_results))
        declarations = dict(declarations)
        required = list(required)
        stream_context, stream = self.terminal.captured_stream(self.bound)
        raw_by_invocation = {}
        for invocation, kind, occurrence, observed in self.terminal.captured_observation_events(self.bound):
            raw_by_invocation.setdefault(invocation, []).append({'kind': kind, 'observation': observed,
                **({} if occurrence is None else {'occurrence': occurrence})})
        finished = [result for _invocation, _start, result in stream if result is not None]
        if len(finished) != len(runner_results) or any(value_bytes(item['result']) != value_bytes(row)
                for item, row in zip(finished, runner_results)):
            raise TerminalRefused('ENGINE_STREAM_RETURN_CONFLICT')
        if any(result is None for _invocation, _start, result in stream):
            raise TerminalRefused('ENGINE_INVOCATION_HAS_NO_RETURN')
        if len(rows) < len(runner_results): raise TerminalRefused('ENGINE_RESULT_PREFIX_MISSING')
        captured_context = captured['context']
        # A whole-run return and acquired post-run measurement are observations,
        # not an admitted D15 completion. Preserve them even if classification
        # refuses completion; this record never names evaluation-complete.
        engine_capture = bytes_value(value_bytes(received))
        engine_capture['captureContext'] = bytes_value(value_bytes(stream_context))
        engine_capture['returnedContext'] = bytes_value(value_bytes(captured_context))
        self.whole_run_observation = engine_capture
        for index, (original, observed_return) in enumerate(zip(runner_results, finished)):
            final = rows[index]
            if any(key not in final or value_bytes(final[key]) != value_bytes(value)
                   for key, value in original.items() if key not in ('executionBinding', 'evaluation')):
                raise TerminalRefused('ENGINE_RESULT_PREFIX_CHANGED')
            final['engineInvocationObservation'] = observed_return['started']
            final['rawRunnerResult'] = original
            invocation = stream[index][0]
            final['engineRawObservations'] = raw_by_invocation.get(invocation, [])
        if captured['verifiersModifiedByCandidate']:
            declarations['verifiers-modified'] = CheckDeclaration('engine', None, False, origin='engine')
            required.append('verifiers-modified')
            rows.append({'id': 'verifiers-modified', 'origin': 'engine', 'format': 'engine',
                         'required': True, 'status': 'FAIL',
                         'reason': 'observed verifier artifacts differ from current requirements'})
        # The uncommitted local proposal is not a retained/emitted engine row.
        # Actual checks have returned and post-run recapture is available; the
        # real typed classifier below must admit matching roots/binding and
        # completion before this proposal may become a final D15 record.
        complete = {'id': 'evaluation-complete', 'origin': 'engine', 'format': 'engine',
            'status': 'PASS', 'required': True, 'epoch': self.handle.epoch,
            'validationId': self.handle.run, 'requirementHash': text(self.bound.requirement),
            'examinedContentRoot': captured['examinedContentRoot'],
            'resultsDigest': hashlib.sha256(value_bytes(rows)).hexdigest(),
            'digestEncoding': 'worldline-lossless-capture-v1', 'captureObservation': engine_capture}
        declarations['evaluation-complete'] = CheckDeclaration('engine', None, False, origin='engine')
        proposed_rows = rows + [complete]
        proposed_typed = tuple(self._result(row, declarations, core) for row in proposed_rows)
        initial = CaptureValue(self.bound, self.source, value_bytes(captured_context), 'Incomplete_Unknown', None)
        observed_epoch = stream_context['evaluationEpoch']
        measured_binding = BoundValue(identity(stream_context['storeId']),
            identity(stream_context['measurement']['worldInstance']),
            identity(stream_context['measurement']['contentId']), identity(stream_context['run']),
            observed_epoch.to_bytes((observed_epoch.bit_length() + 7) // 8, 'little'),
            identity(stream_context['requirement']['requirementHash']))
        with self.terminal.pending.lock, self.terminal.lock, self.terminal._pending_view(self.bound.subject) as (journal, intents, current):
            plan = self.terminal.kernel.decide(intents, current=current, capture=initial, results=proposed_typed,
                required=tuple((identity(item), value_bytes(None if declarations.get(item) is None else asdict(declarations[item]))) for item in required),
                policy=('Explicit_Empty' if empty_declared else 'Missing_Declaration') if not required else 'Required_Checks',
                measured_roots=(identity(stream_context['measurement']['observedContentRoot']),
                                identity(post_measurement['observedContentRoot'])),
                completion=(identity('evaluation-complete'), value_bytes(asdict(declarations['evaluation-complete']))),
                measured_binding=measured_binding)
            self.terminal._admitted(plan, journal, self.bound.run)
        if plan.classification is None: raise TerminalRefused('ENGINE_TERMINAL_CLASSIFICATION_ABSENT')
        state, outcome, promotion = plan.classification
        if state == 'Completed':
            retained_rows, typed = proposed_rows, proposed_typed
            terminal_context = captured_context
        else:
            # No proposed D15 enters a partial/error payload or retained stream.
            # Keep every original row and the actual independent acquisition.
            retained_rows, typed = rows, proposed_typed[:-1]
            terminal_context = {'source': 'revalidation-incomplete',
                                'observedContext': captured_context,
                                'engineCapture': engine_capture}
            if 'contextHash' in captured:
                captured['observedContextHash'] = captured['contextHash']
                captured['contextHash'] = None
        captured['promotionRosterAdmitted'] = promotion
        captured['results'] = retained_rows if state == 'Completed' else []
        captured['partialResults'] = retained_rows if state != 'Completed' else []
        captured['context'] = terminal_context
        captured['engineCapture'] = engine_capture
        captured['validationId'] = self.handle.run
        captured['evaluationEpoch'] = self.handle.epoch
        captured['evaluationState'] = 'COMPLETED' if state == 'Completed' else 'ERROR'
        captured['terminalExecution'] = state
        # Preserve the old aggregate outcome as an observation; the typed
        # terminal result is independently produced by the new complete roster.
        captured['legacyObservedOutcome'] = captured['outcome']
        captured['outcome'] = outcome
        terminal = CaptureValue(self.bound, self.source, value_bytes(terminal_context), state, outcome)
        handle = self.terminal.retain(terminal, typed)
        self.retained = True
        self.terminal.replay(handle.run)
        return captured

    def invocation_started(self, *, world_instance, check, invocation, candidate_snapshot, verifier_entries):
        observed = {'worldInstance': world_instance, 'checkId': check, 'invocationId': invocation,
                    'candidateSnapshot': candidate_snapshot, 'verifierEntries': list(verifier_entries),
                    'evaluationRun': self.handle.run}
        # A failed new start must not attach its exception to a previous
        # same-check invocation that happened to occupy this convenience map.
        self.invocations.pop((world_instance, check), None)
        self.terminal.observe_start(self.bound, invocation, observed)
        self.invocations[(world_instance, check)] = (invocation, observed)

    def invocation_result(self, *, world_instance, check, result):
        item = self.invocations.get((world_instance, check))
        if item is None: raise TerminalRefused('ENGINE_INVOCATION_START_MISSING')
        invocation, started = item
        from .evaluation_terminal import bytes_value
        observed_return = {'started': started, 'result': result}
        # This callback is reached only after the actual check returned. Keep
        # that observation distinct from whether storage accepted its bytes.
        self.actual_returns[invocation] = observed_return
        owned_return = bytes_value(value_bytes(observed_return))
        self.actual_returns[invocation] = owned_return
        self.terminal.observe_result(self.bound, invocation, owned_return)

    def invocation_raw(self, *, world_instance, check, kind, observed, occurrence=None):
        item = self.invocations.get((world_instance, check))
        if item is None: raise TerminalRefused('ENGINE_INVOCATION_START_MISSING')
        invocation, _started = item
        self.terminal.observe_raw(self.bound, invocation, kind, observed, occurrence=occurrence)

    def invocation_exception(self, *, world_instance, check, error):
        # A start that itself failed retention has no committed invocation to
        # attach to. The outer interruption path still retains its own error.
        if (world_instance, check) not in self.invocations: return
        invocation, _started = self.invocations[(world_instance, check)]
        self.actual_exceptions[invocation] = error
        from .raw_observation import exception_observation
        self.invocation_raw(world_instance=world_instance, check=check,
                            kind='invocation-exception', observed=exception_observation(error))

    def interrupted(self, error):
        if self.handle is None or self.retained: return
        # Exact retry of values actually returned but not durably acknowledged.
        # Failure propagates to the original caller; it never proves nonreturn.
        for invocation, returned in self.actual_returns.items():
            self.terminal.observe_result(self.bound, invocation, returned)
        context, stream = self.terminal.captured_stream(self.bound)
        raw_by_invocation = {}
        for invocation, kind, occurrence, observed in self.terminal.captured_observation_events(self.bound):
            raw_by_invocation.setdefault(invocation, []).append({'kind': kind, 'observation': observed,
                **({} if occurrence is None else {'occurrence': occurrence})})
        captured = []
        for invocation, started, finished in stream:
            if finished is not None:
                row = dict(finished['result'])
                row['engineInvocationObservation'] = started
                row['engineRawObservations'] = raw_by_invocation.get(invocation, [])
                captured.append(self._result(row, self.declarations, self.core))
            else:
                row = {'id': started['checkId'], 'engineInvocationObservation': started,
                       'kind': ('invocation-did-not-return' if invocation in self.actual_exceptions
                                else 'invocation-return-not-retained'),
                       'checkReturnObserved': False if invocation in self.actual_exceptions else None,
                       'origin': 'engine-observer',
                       'engineRawObservations': raw_by_invocation.get(invocation, [])}
                captured.append(CheckValue(self.bound, identity(started['checkId']), self.source,
                    identity(invocation), None, 'Incomplete_Unknown', None, value_bytes(row)))
        from .raw_observation import exception_observation
        raw = value_bytes({'source': 'revalidation-incomplete', 'captureContext': context,
                          'engineCapture': self.whole_run_observation,
                          'exceptionObservation': exception_observation(error),
                          'exceptionType': type(error).__qualname__,
                          'exception': str(error),
                          'kind': ('engine-run-return-not-finalized' if self.whole_run_observation is not None
                                   else 'engine-run-return-not-observed'),
                          'engineRunReturnObserved': True if self.whole_run_observation is not None else None,
                          'partialResultEncoding': 'ordered-terminal-result-payloads'})
        capture = CaptureValue(self.bound, self.source, raw, 'Incomplete_Unknown', None)
        handle = self.terminal.retain(capture, captured)
        self.retained = True
        self.terminal.replay(handle.run)
