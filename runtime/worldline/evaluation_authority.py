"""Default raw history reader. Selection and classification are actual Ada calls.

The journal dependency is explicit. Provisioning protected custody, migrating
finalization, and establishing observed confinement remain required engineering
work; neither a second file nor this type check certifies those properties.
"""
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from .completion_kernel import BoundValue, CaptureValue
from .raw_completion_kernel import RawCompletionKernel
from .evaluation_wire import Authority, record
from .evaluation_history import EvaluationCursor, EvaluationRecord, EvaluationQuery, select_history
from .evaluation_pending import identity, text
from .evaluation_terminal import TerminalJournal, value_bytes, bytes_value
from .errors import WorldlineError
from .recovery_material import AuthorityMaterial

@dataclass
class SelectedEvaluation:
    context: dict
    source: str
    results: list
    cursor: dict
    raw: object
    capture: object
    typed_rows: tuple
    retained_stream: tuple
    observed: dict
    # Existing constructor fixtures remain accepted; packet capture refuses None.
    authority_material: object = None

def _refuse(code, detail):
    raise WorldlineError(code, detail)

def _cursor(value):
    if value is None: return None
    if type(value) is not dict or set(value) != {'epoch', 'run'}:
        _refuse('EVALUATION_CURSOR_INVALID', 'prepared cursor is not an exact record')
    return EvaluationCursor(value['epoch'], value['run'])

def _classify_finalization_material(found, world, core, kernel):
    """Replay the original full finalization path, with no live-store lookup."""
    from .finalization_journal import decode
    from .validation import verify_context
    if found is None:
        return None, None, None
    start, sealed, events = found
    cursor = EvaluationCursor(0, text(start.run))
    if sealed is None:
        # A real reserved intent without a seal remains an incomplete attempt;
        # it cannot manufacture final content or a completed finalization row.
        return None, None, cursor
    rows = [bytes_value(row.payload) for row in sealed.value.capture.results]
    if any(type(row) is not dict for row in rows):
        _refuse('FINALIZATION_CAPTURE_INVALID', 'a full retained finalization row is malformed')
    from .finalize import CheckDeclaration
    for retained_row, payload in zip(sealed.value.capture.results, rows):
        declaration_value = bytes_value(retained_row.declared)
        try:
            declaration = None if declaration_value is None else CheckDeclaration(**declaration_value)
        except (TypeError, ValueError) as exc:
            raise WorldlineError('FINALIZATION_CAPTURE_INVALID', 'the full retained declaration is malformed') from exc
        if record(payload, declaration) != retained_row.wire:
            _refuse('FINALIZATION_RAW_PROJECTION_CHANGED', 'the actual full raw projection differs from its retained bytes')
    prepared = kernel.prepare_finalization(sealed.value)
    headers, stream, acquisitions = [], [], []
    starts, returns = {}, {}
    for event in events:
        phase = event['phase']
        if phase not in ('input-header', 'invocation-start', 'invocation-return', 'raw-acquisition'):
            continue
        value = decode(event['payload'])
        invocation = text(event['invocation'])
        if phase == 'input-header':
            headers.append(value)
        elif phase == 'invocation-start':
            if invocation in starts:
                _refuse('FINALIZATION_INVOCATION_DUPLICATED', 'invocation identity was reused')
            starts[invocation] = value
        elif phase == 'invocation-return':
            if invocation in returns or invocation not in starts or value.get('started') != starts[invocation]:
                _refuse('FINALIZATION_INVOCATION_RETURN_INVALID', 'full start/return correspondence differs')
            returns[invocation] = value
        else:
            acquisitions.append((invocation, value['kind'], value.get('occurrence'), value['observation']))
    if len(headers) != 1:
        _refuse('FINALIZATION_INPUT_HEADER_INVALID', 'the actual retained input header is absent or duplicated')
    for invocation, value in starts.items():
        stream.append((invocation, value, returns.get(invocation)))
    if set(returns) != set(starts):
        _refuse('FINALIZATION_INVOCATION_INCOMPLETE', 'actual invocation stream has an unmatched return')
    context = bytes_value(sealed.value.capture.context)
    if type(context) is not dict:
        _refuse('FINALIZATION_CONTEXT_INVALID', 'the full returned context is malformed')
    context = verify_context(context, candidate_instance=world.instance_id, core=core)
    if context.get('requirementHash') != (None if start.requirement is None else text(start.requirement)):
        _refuse('FINALIZATION_REQUIREMENT_MISMATCH', 'the returned context differs from the frozen requirement')
    completion = rows[-1] if rows else None
    observed = (completion.get('captureObservation') if type(completion) is dict
                and completion.get('id') == 'evaluation-complete' else None)
    if sealed.finalization_state == 'COMPLETED':
        if (type(observed) is not dict or observed.get('captureContext') != headers[0]
                or value_bytes(observed.get('returnedContext')) != sealed.value.capture.context):
            _refuse('FINALIZATION_CAPTURE_INVALID', 'the full final engine observation differs from its retained inputs')
    final = EvaluationRecord(text(start.subject), text(sealed.value.content),
        None if start.requirement is None else text(start.requirement), text(start.run),
        0, sealed.finalization_state, sealed.finalization_outcome)
    values = (context, rows, prepared, prepared.capture, prepared.typed_rows,
              ((headers[0], tuple(stream)), tuple(acquisitions)), observed)
    return final, values, cursor


def _read_finalization_material(store, world, core):
    from .finalization_journal import FinalizationJournal
    journal = getattr(store, 'evaluation_finalization', None)
    if journal is None:
        return None, None, None, None
    if type(journal) is not FinalizationJournal:
        _refuse('FINALIZATION_AUTHORITY_UNAVAILABLE', 'the real finalization journal is not provisioned')
    found = journal.retained(world.instance_id)
    # Keep the original cursor validation before acknowledge, and acknowledge
    # before row/context classification. Malformed text must not publish first.
    # Unsealed starts retain their whole material without manufacturing a row.
    if found is not None:
        start, sealed, _events = found
        EvaluationCursor(int.from_bytes(start.epoch, 'little'), text(start.run))
        if sealed is not None:
            journal.acknowledge(store, world.instance_id)
    result = _classify_finalization_material(found, world, core, journal.kernel)
    return (*result, found)


def _read_finalization(store, world, core):
    """Preserve the original private three-value read interface."""
    return _read_finalization_material(store, world, core)[:3]

def _read_material(world, current_requirement, authority_material, *, prepared, core,
                   kernel=None, wire=None, finalization_values=None, _owner_collect=False):
    """The same native classification/selection path over retained full data.

    This is a replay consumer, not a TerminalJournal double or a protected
    producer. No live requirement, current cursor or history is substituted.
    """
    from .finalize import CheckDeclaration, check_declarations, required_roster
    from .validation import verify_context
    from .finalization_kernel import FinalizationKernel
    if type(authority_material) is not AuthorityMaterial:
        _refuse('RECOVERY_PACKET_MATERIAL', 'complete retained authority material is absent')
    terminal = authority_material.terminal
    if type(terminal) is not tuple or len(terminal) != 4:
        _refuse('RECOVERY_PACKET_MATERIAL', 'complete retained terminal schema differs')
    journal, actual_current, material, retained_streams = terminal
    kernel = RawCompletionKernel(Path(core.library_path)) if kernel is None else kernel
    wire = Authority(core) if wire is None else wire
    if finalization_values is None:
        found = authority_material.finalization
        finalization_kernel = (FinalizationKernel(Path(core.library_path))
                               if found is not None and found[1] is not None else None)
        finalization_values = _classify_finalization_material(
            found, world, core, finalization_kernel)
    finalization, finalization_values, finalization_cursor = finalization_values
    current = None if actual_current is None else EvaluationCursor(
        int.from_bytes(actual_current[0], 'little'), text(actual_current[1]))
    if current is None:
        current = finalization_cursor
    # At prepare this is the actual journal observation to retain. At commit
    # the old retained cursor is separate from this freshly read current one.
    prior = current if prepared is None else _cursor(prepared)
    records, values = [], []
    for summary, retained in material:
        subject, content = text(summary.subject), text(summary.content)
        requirement = None if summary.requirement is None else text(summary.requirement)
        run, epoch = text(summary.run), int.from_bytes(summary.epoch, 'little')
        state, outcome = summary.state, summary.outcome
        packed, context, raw_rows, observed = None, None, [], None
        capture, typed = None, ()
        if retained is not None:
            _stored_summary, capture, typed = retained
            raw_rows = [bytes_value(item.payload) for item in typed]
            if any(type(row) is not dict for row in raw_rows):
                _refuse('EVALUATION_CAPTURE_INVALID', 'a retained raw row is malformed')
            from .evaluation_context import project_metadata, metadata_descriptor, require_metadata
            retained_stream = retained_streams.get(summary.run)
            invocation_rows = () if retained_stream is None else retained_stream[0][1]
            metadata = tuple(project_metadata(payload, capture_source=capture.source,
                invocation=invocation_rows[index] if index < len(invocation_rows) else None)
                for index, payload in enumerate(raw_rows))
            # Marshal complete original rows for this comparison only. This
            # operation does not run Completion.Decide or invent a terminal.
            metadata_request, metadata_input_owners = kernel._owned(
                (), None, capture, tuple(typed), None, (), None, None, None,
                None, None, None)
            descriptor, metadata_owners = metadata_descriptor(core, metadata_request, metadata)
            require_metadata(core, metadata_request, descriptor)
            # All owners remain live through the synchronous native call.
            # Validate every raw record, including unrelated rows and ERROR
            # prefixes. Unknown/incomplete is data; malformed wire is refusal.
            owned, projected = [], []
            for item, payload in zip(typed, raw_rows):
                declaration_value = bytes_value(item.declared)
                try:
                    declaration = None if declaration_value is None else CheckDeclaration(**declaration_value)
                except (TypeError, ValueError) as exc:
                    raise WorldlineError('EVALUATION_CAPTURE_INVALID', 'retained declaration is malformed') from exc
                raw = record(payload, declaration)
                execution, verdict, _bundle, _report, _admitted = wire.evaluate(raw)
                from .completion_kernel import EXECUTION
                names = {name.upper(): name for name in EXECUTION}
                projected.append(replace(item, state=names[execution], outcome=None if verdict == 'NONE' else verdict))
                owned.append(raw)
            context = bytes_value(capture.context)
            # Stored lifecycle is a carried projection, not permission to skip
            # the whole raw stream. A partial capture without a final engine
            # observation stays ERROR; it does not manufacture absent D15 data.
            completion = raw_rows[-1] if raw_rows else None
            has_final = (type(completion) is dict
                and completion.get('id') == 'evaluation-complete'
                and completion.get('origin') == 'engine'
                and type(completion.get('captureObservation')) is dict)
            if not has_final:
                if state == 'COMPLETED':
                    _refuse('EVALUATION_CAPTURE_INVALID', 'completed capture lacks its final engine observation')
                state, outcome = 'ERROR', None
            else:
                observed = completion['captureObservation']
                returned_context = observed.get('returnedContext')
                if type(returned_context) is not dict:
                    _refuse('EVALUATION_CAPTURE_INVALID', 'final raw observation lacks the returned context')
                # The context observed at the actual return is checked directly,
                # including when the retained terminal carries ERROR. Preserve
                # original stored bytes; no derived summary rewrites the store.
                context = verify_context(returned_context, candidate_instance=subject, core=core)
                if context.get('requirementHash') != requirement:
                    _refuse('EVALUATION_CAPTURE_INVALID', 'context and retained requirement differ')
                if type(observed) is not dict or type(observed.get('captureContext')) is not dict:
                    _refuse('EVALUATION_CAPTURE_INVALID', 'engine capture provenance is absent')
                initial = observed['captureContext']
                post = observed.get('postMeasurement')
                if type(post) is not dict:
                    _refuse('EVALUATION_CAPTURE_INVALID', 'actual post-run observation is absent')
                policy = initial['requirement']
                if policy['requirementHash'] != requirement:
                    _refuse('EVALUATION_CAPTURE_INVALID', 'captured declaration belongs to another requirement')
                required, empty = required_roster(policy)
                declarations = check_declarations(policy)
                # Engine-owned additional required observations remain required.
                if any(row.get('id') == 'verifiers-modified' and row.get('origin') == 'engine' for row in raw_rows):
                    required = list(required) + ['verifiers-modified']
                    declarations['verifiers-modified'] = CheckDeclaration('engine', None, False, origin='engine')
                declarations['evaluation-complete'] = CheckDeclaration('engine', None, False, origin='engine')
                observed_epoch = initial['evaluationEpoch']
                if type(observed_epoch) is not int or observed_epoch < 0:
                    _refuse('EVALUATION_CAPTURE_INVALID', 'captured epoch is malformed')
                measured = BoundValue(identity(initial['storeId']), identity(initial['measurement']['worldInstance']),
                    identity(initial['measurement']['contentId']), identity(initial['run']),
                    observed_epoch.to_bytes((observed_epoch.bit_length() + 7) // 8, 'little'),
                    identity(policy['requirementHash']))
                packed = kernel.prepare(journal, current=actual_current, capture=capture,
                    results=projected, wire_records=owned,
                    required=tuple((identity(name), value_bytes(None if declarations.get(name) is None else asdict(declarations[name]))) for name in required),
                    policy=('Explicit_Empty' if empty else 'Missing_Declaration') if not required else 'Required_Checks',
                    measured_roots=(identity(initial['measurement']['observedContentRoot']), identity(post['observedContentRoot'])),
                    completion=(identity('evaluation-complete'), value_bytes(asdict(declarations['evaluation-complete']))),
                    measured_binding=measured)
                execution, outcome, _promotion = kernel.classify(packed)
                state = 'COMPLETED' if execution == 'Completed' else 'ERROR'
                if state != 'COMPLETED': outcome = None
        records.append(EvaluationRecord(subject, content, requirement, run, epoch, state, outcome))
        values.append((context, raw_rows, packed, capture, typed,
                       retained_streams.get(summary.run), observed))
    # The complete list is passed in original order. No requirement/verdict
    # filter precedes Head_Reference; any current-requirement FAIL is retained.
    if _owner_collect:
        # Full classification data only; no evidence selection or authority.
        return OwnerProjection(tuple(records), finalization, current, tuple(values),
                               finalization_values, authority_material)
    selected = select_history(tuple(records), finalization,
        EvaluationQuery(world.instance_id, world.content_id, current_requirement, current, prior), core=core)
    if selected.reason != 'READY':
        _refuse(selected.reason, 'complete retained history does not admit the current head')
    if selected.head.kind == 'FINALIZATION':
        if finalization is None or finalization_values is None:
            _refuse('EVALUATION_CAPTURE_INVALID', 'READY lacks its retained finalization')
        chosen, chosen_values = finalization, finalization_values
        source = 'finalization'
    elif selected.head.kind == 'HISTORY_ENTRY' and selected.head.index is not None:
        chosen, chosen_values = records[selected.head.index], values[selected.head.index]
        source = 'revalidation:' + chosen.run
    else:
        _refuse('EVALUATION_CAPTURE_INVALID', 'READY did not name a retained history row')
    context, rows, raw, capture, typed_rows, retained_stream, observed = chosen_values
    if type(context) is not dict or raw is None or current is None:
        _refuse('EVALUATION_CAPTURE_INVALID', 'READY lacks the corresponding complete raw capture')
    return SelectedEvaluation(context, source, rows,
        {'epoch': current.epoch, 'run': current.run}, raw, capture,
        tuple(typed_rows), retained_stream, observed, authority_material)



def _read(store, world, current_requirement, *, prepared=None, core=None):
    terminal = getattr(store, 'evaluation_terminal', None)
    if type(terminal) is not TerminalJournal:
        _refuse('EVALUATION_AUTHORITY_UNAVAILABLE', 'the durable evaluation producer is not provisioned')
    core = core or store.core
    # Preserve original ABI construction before finalization/history acquisition.
    kernel, wire = RawCompletionKernel(Path(core.library_path)), Authority(core)
    finalization, values, cursor, finalization_material = _read_finalization_material(store, world, core)
    full = terminal.authority_material_full(world.instance_id)
    # Full ordered material is retained even when finalization is unsealed and
    # history speaks. Every old failure, incomplete row, duplicate and raw byte
    # remains in the packet; this is data, not a provenance assertion.
    material = AuthorityMaterial(tuple(full), finalization_material,
                                 getattr(terminal.pending, 'store', None))
    return _read_material(world, current_requirement, material, prepared=prepared, core=core,
                          kernel=kernel, wire=wire,
                          finalization_values=(finalization, values, cursor))


def _replay_producer_gates(world, material, core):
    """Re-run original native producer relations before the raw reader replay.

    Durable SQLite acknowledgment/outbox/custody are not inferred from this
    DTO. Their authenticated retention remains the protected issuer's job.
    """
    from .completion_kernel import CompletionKernel, HistoryValue, CaptureValue, CheckValue
    from .pending_kernel_v2 import Intent
    from .finalization_kernel import FinalizationKernel
    from .finalization_values import StartValue, SealedValue, UnsealedResult
    from .finalization_journal import bytes_record
    if type(material) is not AuthorityMaterial or type(material.terminal) is not tuple or len(material.terminal) != 4:
        _refuse('RECOVERY_PACKET_MATERIAL', 'complete retained authority material is absent')
    journal, current, rows, streams = material.terminal
    if (type(journal) is not tuple or type(rows) is not tuple or type(streams) is not dict
            or len(journal) != len(rows)
            or (current is not None and (type(current) is not tuple or len(current) != 2
                or any(type(value) is not bytes for value in current)))):
        _refuse('RECOVERY_PACKET_MATERIAL', 'complete retained terminal shape differs')
    if journal and type(material.pending_store) is not bytes:
        _refuse('RECOVERY_PACKET_PENDING_STORE', 'the independent retained pending-store identity is absent')
    history, retained_runs = [], []
    for intent, row in zip(journal, rows):
        if (type(intent) is not Intent or type(row) is not tuple or len(row) != 2
                or type(row[0]) is not HistoryValue or intent.linked is not True
                or intent.store_id != material.pending_store):
            _refuse('RECOVERY_PACKET_MATERIAL', 'the complete pending/history correspondence differs')
        summary, retained = row
        if ((summary.subject, summary.content, summary.requirement, summary.run, summary.epoch)
                != (intent.subject, intent.content, intent.requirement, intent.run, intent.epoch)):
            _refuse('RECOVERY_PACKET_MATERIAL', 'a retained history identity differs from the original intent')
        if retained is None:
            if summary != HistoryValue(intent.subject, intent.content, intent.requirement,
                    intent.run, intent.epoch, 'PENDING', None):
                _refuse('RECOVERY_PACKET_MATERIAL', 'an unretained intent manufactures a terminal summary')
        else:
            if type(retained) is not tuple or len(retained) != 3:
                _refuse('RECOVERY_PACKET_MATERIAL', 'a retained terminal record is incomplete')
            stored, capture, results = retained
            if (type(capture) is not CaptureValue or type(results) is not tuple
                    or any(type(result) is not CheckValue for result in results)):
                _refuse('RECOVERY_PACKET_MATERIAL', 'a full terminal raw record has an unexpected DTO type')
            expected = HistoryValue(capture.bound.subject, capture.bound.content,
                capture.bound.requirement, capture.bound.run, capture.bound.epoch,
                'COMPLETED' if capture.state == 'Completed' else 'ERROR', capture.outcome)
            if summary != expected or stored != summary:
                _refuse('RECOVERY_PACKET_MATERIAL', 'the retained terminal summary differs from its full capture')
            retained_runs.append(summary.run)
        history.append(summary)
    if set(streams) != set(retained_runs):
        _refuse('RECOVERY_PACKET_MATERIAL', 'the full raw invocation-stream domain differs')
    producer = CompletionKernel(Path(core.library_path))
    for summary, retained in rows:
        if retained is None:
            continue
        _stored, capture, results = retained
        plan = producer.decide(journal, current=current, capture=capture,
            results=results, retained=capture, retained_results=results, history=tuple(history))
        if (plan.reason not in ('Retain_Terminal', 'Already_Retained')
                or plan.selected < 1 or plan.selected > len(journal)
                or journal[plan.selected - 1].run != summary.run or plan.summary != summary):
            _refuse('RECOVERY_PACKET_MATERIAL', 'the original native terminal relation refuses retained data')
    found = material.finalization
    if found is not None:
        if type(found) is not tuple or len(found) != 3:
            _refuse('RECOVERY_PACKET_MATERIAL', 'the complete retained finalization shape differs')
        start, sealed, events = found
        if type(start) is not StartValue or type(events) is not tuple or start.subject != identity(world.instance_id):
            _refuse('RECOVERY_PACKET_MATERIAL', 'the original finalization start differs')
        finalization = FinalizationKernel(Path(core.library_path))
        finalization.validate_start(start)
        if sealed is not None:
            if (type(sealed) is not SealedValue or sealed.value.capture.start != start
                    or finalization.seal(sealed.value) != sealed):
                _refuse('RECOVERY_PACKET_MATERIAL', 'the original native finalization seal differs')
            results = tuple(bytes_record(event['payload'], UnsealedResult)
                for event in events if event['phase'] == 'result')
            if results != sealed.value.capture.results:
                _refuse('RECOVERY_PACKET_MATERIAL', 'the full retained finalization result sequence differs')


def read_material(world, current_requirement, material, *, prepared, core):
    """Replay retained native inputs, keeping custody as an external obligation."""
    from .pending_kernel import KernelRefused
    from .evaluation_terminal import TerminalRefused
    try:
        _replay_producer_gates(world, material, core)
        return _read_material(world, current_requirement, material, prepared=prepared, core=core)
    except WorldlineError:
        raise
    except (KeyError, IndexError, AttributeError, TypeError, ValueError, OverflowError,
            KernelRefused, TerminalRefused) as exc:
        raise WorldlineError('RECOVERY_PACKET_MATERIAL_INVALID',
                            'complete retained raw authority could not be replayed') from exc


def read(store, world, current_requirement, *, prepared=None, core=None):
    from .pending_kernel import KernelRefused
    from .evaluation_terminal import TerminalRefused
    try:
        return _read(store, world, current_requirement, prepared=prepared, core=core)
    except WorldlineError:
        raise
    except (KeyError, TypeError, ValueError, OverflowError, KernelRefused, TerminalRefused) as exc:
        raise WorldlineError('EVALUATION_CAPTURE_INVALID', 'complete retained raw capture could not be validated') from exc

@dataclass(frozen=True)
class OwnerProjection:
    records: tuple
    finalization: object
    current: object
    values: tuple
    finalization_values: object
    authority_material: object

def owner_projection(store, world, requirement, *, core=None, material=None):
    """Replay every original producer/classifier without bypassing FAIL selection.
    This returns data for the separate owner rule, not default evidence.
    """
    core=core or store.core
    if material is None:
        terminal=getattr(store,'evaluation_terminal',None)
        if type(terminal) is not TerminalJournal:
            _refuse('OWNER_TERMINAL_CUSTODY_UNAVAILABLE','existing terminal journal required')
        _final,_values,_cursor,final=_read_finalization_material(store,world,core)
        material=AuthorityMaterial(tuple(terminal.authority_material_full(world.instance_id)),final,terminal.pending.store)
    _replay_producer_gates(world,material,core)
    return _read_material(world,requirement,material,prepared=None,core=core,_owner_collect=True)

def selected_owner_projection(world, projection):
    """Projection only after the protected owner consumer's native audit READY.
    Calling this data helper is not permission. Original context joins remain.
    """
    if type(projection) is not OwnerProjection or not projection.records or projection.current is None:
        _refuse('OWNER_RETRY_PROJECTION_INVALID','complete classified retry head required')
    chosen=projection.records[-1]
    context,rows,raw,capture,typed,stream,observed=projection.values[-1]
    if type(context) is not dict or raw is None:
        _refuse('OWNER_RETRY_CAPTURE_INVALID','complete original raw capture required')
    return SelectedEvaluation(context,'owner-retry:'+chosen.run,rows,
        {'epoch':projection.current.epoch,'run':projection.current.run},raw,capture,
        tuple(typed),stream,observed,projection.authority_material)
