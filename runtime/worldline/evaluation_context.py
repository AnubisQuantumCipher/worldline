"""Lossless context join for the raw default boundary.

Every named field retains both producer values. Ada compares them and the raw
request's actual rows/current binding before Collapse can use promotion. Legacy
hashes are recomputed as projections from these values, not used as substitutes
for full identities. JSON extraction, hash implementation, foreign allocation
custody and protected producer provenance remain explicit proof obligations.
"""
from dataclasses import dataclass, replace
import ctypes as C
from types import SimpleNamespace
from .completion_kernel import (Span, Optional_Span, Cursor, Binding, Check_Row,
    Required_Row, MAX_COUNT, KernelRefused)
from .core import CCollapseRequest
from .evaluation_wire import Raw
from .evaluation_pending import identity
from .evaluation_terminal import value_bytes
from .errors import WorldlineError

CONTEXT_FIELDS = ('capture_header', 'returned_context', 'full_policy',
    'candidate_record', 'root_manifests', 'effective_roster',
    'declared_verifiers', 'executed_verifiers', 'agent_record', 'source_id', 'examined_root',
    'invocation_stream', 'acquisition_stream', 'returned_rows')
ROW_FIELDS = ('invocation_start', 'invocation_return', 'raw_acquisitions',
    'invocation_binding', 'candidate_snapshot', 'invocation_verifiers',
    'verifier_members', 'verifier_identity')
class ContextRow(C.Structure):
    _fields_ = [('item', Check_Row), ('expected', Optional_Span * len(ROW_FIELDS)),
                ('observed', Optional_Span * len(ROW_FIELDS))]
class ContextInput(C.Structure):
    _fields_ = [('version', C.c_uint32), ('data', C.c_void_p), ('data_length', C.c_int64),
        ('expected_binding', Binding),
        ('expected_current', Cursor), ('prepared_current', Cursor), ('expected', Optional_Span * len(CONTEXT_FIELDS)),
        ('observed', Optional_Span * len(CONTEXT_FIELDS)), ('rows', C.c_void_p),
        ('row_count', C.c_int64), ('required', C.c_void_p), ('required_count', C.c_int64), ('policy', C.c_uint32),
        ('projection', CCollapseRequest), ('agent', Raw), ('agent_confinement', C.c_uint8)]

@dataclass(frozen=True)
class RowMetadata:
    check: bytes
    source: bytes
    payload: bytes
    execution: bytes | None
    verifier: bytes | None

class MetadataRow(C.Structure):
    _fields_ = [('check_id', Span), ('source_id', Span), ('payload', Span),
                ('execution', Optional_Span), ('verifier', Optional_Span)]

class MetadataContext(C.Structure):
    _fields_ = [('version', C.c_uint32), ('base', C.c_void_p),
                ('data', C.c_void_p), ('data_length', C.c_int64),
                ('rows', C.c_void_p), ('row_count', C.c_int64)]

def project_metadata(payload, *, capture_source, invocation=None):
    """Decode the original writer's complete field encodings independently.

    This function never receives CheckValue/Check_Row metadata. The regular
    encoding is EvaluationWriter._result; the nonreturn encoding is its
    interrupted branch, selected from the separately retained invocation, not
    a caller-supplied success flag or payload status. Neither proves custody.
    """
    if type(payload) is not dict:
        raise KernelRefused('CONTEXT_METADATA_PAYLOAD_INVALID')
    if invocation is not None and invocation[2] is None:
        invocation_id, started, _finished = invocation
        return RowMetadata(identity(started['checkId']), capture_source,
                           value_bytes(payload), identity(invocation_id), None)
    check = payload.get('id')
    execution = (None if payload.get('engineInvocationObservation') is None
                 and payload.get('evaluatorBoundary') is None else
                 {'engineInvocation': payload.get('engineInvocationObservation'),
                  'evaluatorBoundary': payload.get('evaluatorBoundary')})
    verifier = payload.get('executedVerifierSet')
    return RowMetadata(identity(check) if isinstance(check, str) else value_bytes(check),
        value_bytes(payload.get('origin')), value_bytes(payload),
        None if execution is None else value_bytes(execution),
        None if verifier is None else value_bytes(verifier))

def metadata_descriptor(core, request, rows, *, base=None):
    """Own independently decoded projections. No equality is decided in Python."""
    try:
        layout = core._lib.wl_completion_metadata_layout_v1
    except AttributeError as exc:
        raise KernelRefused('METADATA_ABI_UNAVAILABLE') from exc
    layout.argtypes = [C.c_uint32, C.c_uint32]; layout.restype = C.c_int64
    for kind, cls in ((1, MetadataContext), (2, MetadataRow)):
        if layout(kind, 0) != C.sizeof(cls) or layout(kind, 1) != C.alignment(cls):
            raise KernelRefused('METADATA_LAYOUT_MISMATCH')
        for field, (name, _ctype) in enumerate(cls._fields_, 2):
            if layout(kind, field) != getattr(cls, name).offset:
                raise KernelRefused('METADATA_OFFSET_MISMATCH')
    rows = tuple(rows)
    if len(rows) != request.captured_count:
        raise KernelRefused('METADATA_ROW_COUNT_MISMATCH')
    if len(rows) > MAX_COUNT // C.sizeof(MetadataRow):
        raise KernelRefused('METADATA_EXTENT_UNREPRESENTABLE')
    arena = bytearray()
    def span(value):
        if type(value) is not bytes: raise KernelRefused('METADATA_BYTES_REQUIRED')
        first = len(arena) + 1
        if first > MAX_COUNT or len(value) > MAX_COUNT - len(arena):
            raise KernelRefused('METADATA_EXTENT_UNREPRESENTABLE')
        arena.extend(value)
        return Span(first, len(value))
    def optional(value):
        return Optional_Span(0, Span(1, 0)) if value is None else Optional_Span(1, span(value))
    projected = (MetadataRow * len(rows))()
    for index, row in enumerate(rows):
        if type(row) is not RowMetadata: raise KernelRefused('METADATA_ROW_TYPE_INVALID')
        projected[index] = MetadataRow(span(row.check), span(row.source), span(row.payload),
                                       optional(row.execution), optional(row.verifier))
    data = (C.c_uint8 * len(arena)).from_buffer_copy(arena)
    descriptor = MetadataContext(1, None if base is None else C.cast(C.pointer(base), C.c_void_p),
        C.cast(data, C.c_void_p), len(arena), C.cast(projected, C.c_void_p), len(rows))
    return descriptor, (data, projected, descriptor, base)

def require_metadata(core, request, descriptor):
    try:
        call = core._lib.wl_completion_metadata_matches_v1
    except AttributeError as exc:
        raise KernelRefused('METADATA_ABI_UNAVAILABLE') from exc
    call.argtypes = [C.c_void_p, C.c_void_p]; call.restype = C.c_int
    code = call(C.byref(request), C.byref(descriptor))
    if code != 1:
        raise KernelRefused('METADATA_MISMATCH' if code == 0 else 'METADATA_NATIVE_REFUSED')

def attach(core, prepared, *, expected_binding, expected_current, prepared_current,
           expected, observed, row_pairs, required, policy, projection, agent, row_metadata):
    """Marshal full correspondence inputs into a separate owned context arena.

    No correspondence is decided here. The C/Ada join re-reads actual request
    rows, count, required declarations, binding and cursor independently.
    """
    if set(expected) != set(CONTEXT_FIELDS) or set(observed) != set(CONTEXT_FIELDS):
        raise KernelRefused('CONTEXT_FIELD_SET_INVALID')
    layout = core._lib.wl_completion_context_layout_v1
    layout.argtypes = [C.c_uint32, C.c_uint32]; layout.restype = C.c_int64
    for kind, cls in ((1, ContextInput), (2, ContextRow)):
        if layout(kind, 0) != C.sizeof(cls) or layout(kind, 1) != C.alignment(cls):
            raise KernelRefused('CONTEXT_LAYOUT_MISMATCH')
        for field, (name, _ctype) in enumerate(cls._fields_, 2):
            if layout(kind, field) != getattr(cls, name).offset:
                raise KernelRefused('CONTEXT_OFFSET_MISMATCH')
    request = prepared.request
    rows, required, row_pairs = tuple(prepared.owned[2]), tuple(required), tuple(row_pairs)
    if len(rows) != len(row_pairs): raise KernelRefused('CONTEXT_ROW_COUNT_MISMATCH')
    arena = bytearray()
    def span(value):
        if type(value) is not bytes: raise KernelRefused('CONTEXT_BYTES_REQUIRED')
        first = len(arena) + 1
        if first > MAX_COUNT or len(value) > MAX_COUNT - len(arena):
            raise KernelRefused('CONTEXT_EXTENT_UNREPRESENTABLE')
        arena.extend(value)
        return Span(first, len(value))
    def optional(value):
        return Optional_Span(0, Span(1, 0)) if value is None else Optional_Span(1, span(value))
    def bound(value):
        return Binding(span(value.store_id), span(value.subject), span(value.content),
            span(value.run), span(value.epoch), optional(value.requirement))
    def fields(names, value):
        if set(value) != set(names): raise KernelRefused('CONTEXT_ROW_FIELD_SET_INVALID')
        return (Optional_Span * len(names))(*(optional(value[name]) for name in names))
    if len(rows) > MAX_COUNT // C.sizeof(ContextRow) or len(required) > MAX_COUNT // C.sizeof(Required_Row):
        raise KernelRefused('CONTEXT_EXTENT_UNREPRESENTABLE')
    joined = (ContextRow * len(rows))(*(ContextRow(row, fields(ROW_FIELDS, pair[0]),
        fields(ROW_FIELDS, pair[1])) for row, pair in zip(rows, row_pairs)))
    qs = (Required_Row * len(required))(*(Required_Row(span(k), span(v)) for k, v in required))
    current = Cursor(0, Span(1, 0), Span(1, 0)) if expected_current is None else Cursor(
        1, span(expected_current[0]), span(expected_current[1]))
    prior = Cursor(0, Span(1, 0), Span(1, 0)) if prepared_current is None else Cursor(
        1, span(prepared_current[0]), span(prepared_current[1]))
    descriptor = ContextInput(1, None, 0, bound(expected_binding), current, prior,
        fields(CONTEXT_FIELDS, expected), fields(CONTEXT_FIELDS, observed),
        C.cast(joined, C.c_void_p), len(rows), C.cast(qs, C.c_void_p), len(required), policy,
        projection, agent.native(), agent.confinement)
    data = (C.c_uint8 * len(arena)).from_buffer_copy(arena)
    # Keep the raw arena and all original request fields unchanged. The typed
    # cross-arena relation avoids requiring raw_length + context_length to fit
    # one index range. Each owner survives the complete native decision call.
    descriptor.data = C.cast(data, C.c_void_p); descriptor.data_length = len(arena)
    prepared.context = descriptor
    prepared.context_owners = (data, joined, qs, descriptor)
    prepared.metadata_context, prepared.metadata_owners = metadata_descriptor(
        core, request, row_metadata, base=descriptor)
    return prepared

def _policy_value(value):
    # Exact existing requirement_hash semantic input: diagnostic-only policy
    # source digest/warnings are retained in the full capture header but are
    # not turned into new policy-equivalence refusal conditions.
    from .canonical import canonical_bytes
    item = {k: v for k, v in value.items() if k != 'requirementHash'}
    item['policy'] = {k: v for k, v in dict(value.get('policy') or {}).items()
                      if k not in ('sourceSha256', 'warnings')}
    return canonical_bytes(item)

def _legacy_triples(entries):
    return [(str(v.get('rootKey')), str(v.get('path')), str(v.get('sha256')))
            for v in entries]

def _required_value(pairs, empty):
    # value_bytes owns JSON-like values, not Python bytes objects. Hex is a
    # lossless spelling of each complete field (not an identity digest); the
    # independently marshalled Required_Row array is also checked by Ada.
    return value_bytes(([(check.hex(), declaration.hex())
                         for check, declaration in pairs], empty))

def _triples(entries):
    # Same legacy string conversion and sorted member semantics as the original
    # verifier identity producer. Keep complete source records elsewhere.
    def digest_spelling(value):
        # Preserve bundle_identity's full accepted hex syntax (including case
        # and whitespace), without conflating absent content with a present
        # zero digest. Full original member objects remain in retained payloads.
        value = str(value)
        raw = value.removeprefix('sha256:') if value else ''
        return 'sha256:' + bytes.fromhex(raw).hex() if raw else ''
    # Sort the original spellings at the original point in bundle_identity,
    # then expose its decoded byte sequence. Sorting normalized strings first
    # could reorder duplicate (root,path) members with distinct contents.
    return [(root, path, digest_spelling(content))
            for root, path, content in sorted(_legacy_triples(entries))]

def bind_selected(manager, selected, *, values, subject, candidate,
                  authoritative_requirement, authoritative_roots, agent,
                  agent_record, role, prepared_cursor):
    from dataclasses import asdict
    from .completion_kernel import BoundValue
    from .executed import bundle_identity, NO_BUNDLE_IDENTITY
    from .finalize import check_declarations, required_roster, CheckDeclaration
    from .validation import content_root_set
    from .canonical import canonical_bytes
    from .finalization_kernel import PreparedFinalization
    finalization = type(selected.raw) is PreparedFinalization
    if finalization:
        from .finalization_journal import (encode as acquisition_bytes,
                                          payload_acquisitions)
    else:
        acquisition_bytes = value_bytes
    def acquired(payload):
        value = payload.get('engineRawObservations')
        return payload_acquisitions(value) if finalization else value
    core = manager.core
    if selected.retained_stream is None:
        raise WorldlineError('EVALUATION_CAPTURE_INVALID', 'selected raw capture lacks its retained invocation stream')
    ((header, stream), acquisitions) = selected.retained_stream
    observed = selected.observed
    initial, context = observed['captureContext'], selected.context
    current = authoritative_requirement
    captured_policy = initial['requirement']
    required, empty = required_roster(current)
    declarations = check_declarations(current)
    if finalization:
        from .finalize import ENGINE_DECLARATIONS
        if 'agent' not in required:
            required = list(required) + ['agent']
        declarations['agent'] = ENGINE_DECLARATIONS['agent']
    if any(r.get('id') == 'verifiers-modified' and r.get('origin') == 'engine' for r in selected.results):
        required = list(required) + ['verifiers-modified']
        declarations['verifiers-modified'] = CheckDeclaration('engine', None, False, origin='engine')
    required = list(required)
    current_pairs = tuple((identity(k), value_bytes(None if declarations.get(k) is None
                         else asdict(declarations[k]))) for k in required)
    captured_required, captured_empty = required_roster(captured_policy)
    if finalization and 'agent' not in captured_required:
        captured_required = list(captured_required) + ['agent']
    if 'verifiers-modified' in required: captured_required = list(captured_required) + ['verifiers-modified']
    captured_declarations = check_declarations(captured_policy)
    if finalization:
        captured_declarations['agent'] = ENGINE_DECLARATIONS['agent']
    if 'verifiers-modified' in required: captured_declarations['verifiers-modified'] = declarations['verifiers-modified']
    captured_pairs = tuple((identity(k), value_bytes(None if captured_declarations.get(k) is None
                          else asdict(captured_declarations[k]))) for k in captured_required)
    planned = {}
    for member in current.get('verifiers') or ():
        planned.setdefault(str(member.get('checkId')), []).append(member)
    captured_planned = {}
    for member in captured_policy.get('verifiers') or ():
        captured_planned.setdefault(str(member.get('checkId')), []).append(member)
    by_invocation = {}
    for invocation, kind, occurrence, payload in acquisitions:
        by_invocation.setdefault(invocation, []).append({'kind': kind, 'observation': payload,
            **({} if occurrence is None else {'occurrence': occurrence})})
    # Independently retain complete source streams. The corresponding raw-row
    # projections below cannot omit an extra invocation or acquisition: the
    # kernel compares the entire ordered encodings, including duplicates.
    projected_stream, projected_acquisitions, projected_returns = [], [], []
    for payload in selected.results:
        start = payload.get('engineInvocationObservation')
        if start is not None:
            invocation = start['invocationId']
            returned = payload.get('rawRunnerResult')
            projected_stream.append((invocation, start, {'started': start, 'result': returned}))
            projected_returns.append(returned)
            for event in acquired(payload) or ():
                projected_acquisitions.append((invocation, event['kind'], event.get('occurrence'), event['observation']))
    row_pairs, effective = [], {}
    for index, payload in enumerate(selected.results):
        name = str(payload.get('id'))
        effective[name] = payload  # Same full-stream last matching row selection.
        if index < len(stream):
            invocation, started, finished = stream[index]
            if finished is None: raise WorldlineError('EVALUATION_CAPTURE_INVALID', 'retained invocation has no actual return')
            expected_start, observed_start = started, payload.get('engineInvocationObservation')
            expected_return, observed_return = finished['result'], payload.get('rawRunnerResult')
            expected_acquired, observed_acquired = by_invocation.get(invocation, []), acquired(payload)
            expected_bound = [selected.cursor['run'], name, invocation, started['worldInstance']]
            observed_bound = [started.get('evaluationRun'), started.get('checkId'),
                              started.get('invocationId'), (observed_start or {}).get('worldInstance')]
            expected_snapshot, observed_snapshot = started.get('candidateSnapshot'), expected_return.get('candidateSnapshot')
            invocation_members = _triples(started.get('verifierEntries') or ())
        else:
            expected_start = expected_return = expected_acquired = expected_bound = expected_snapshot = None
            observed_start, observed_return = payload.get('engineInvocationObservation'), payload.get('rawRunnerResult')
            observed_acquired = acquired(payload)
            observed_bound = observed_snapshot = None
            invocation_members = []
        executed = payload.get('executedVerifierSet')
        members = _triples(executed.get('members', ())) if isinstance(executed, dict) else []
        actual_identity = bundle_identity(_legacy_triples(executed.get('members', ()))) if isinstance(executed, dict) else NO_BUNDLE_IDENTITY
        recorded_identity = executed.get('identity') if isinstance(executed, dict) else NO_BUNDLE_IDENTITY
        wanted = _triples(planned.get(name, ()))
        def encode(value): return None if value is None else value_bytes(value)
        def fields(items):
            # The acquisition lane retains bytes and tuple/list distinctions;
            # every other field keeps its original result/policy encoding.
            return {name: (None if value is None else acquisition_bytes(value))
                    if name == 'raw_acquisitions' else encode(value)
                    for name, value in zip(ROW_FIELDS, items)}
        row_pairs.append((fields((
            expected_start, expected_return, expected_acquired, expected_bound,
            expected_snapshot, wanted, wanted, actual_identity)),
            fields((
            observed_start, observed_return, observed_acquired, observed_bound,
            observed_snapshot, invocation_members, members, recorded_identity))))
    expected_members, actual_members, actual_absent = [], [], False
    for check in required_roster(current)[0]:
        members = _triples(planned.get(check, ()))
        expected_members.append(('', check, bundle_identity(_legacy_triples(planned.get(check, ()))) if members else NO_BUNDLE_IDENTITY))
        payload = effective.get(check)
        if payload is None:
            actual_absent = True; continue
        executed = payload.get('executedVerifierSet')
        if isinstance(executed, dict):
            actual_members.append(('', check, bundle_identity(_legacy_triples(executed.get('members', ())))))
        elif ('executedVerifierSet' in payload and executed is None) or payload.get('origin') == 'engine':
            actual_members.append(('', check, NO_BUNDLE_IDENTITY))
        else: actual_absent = True
    declared = bundle_identity(expected_members)
    executed = None if actual_absent else bundle_identity(actual_members)
    # Hashes are recomputed from retained manifests and full member triples.
    manifests = {k: SimpleNamespace(value=v) for k, v in initial['measurement']['manifests'].items()}
    root = content_root_set(manifests, core)
    roots = sorted(({'rootKey': r['root_key'], 'path': __import__('os').fsdecode(bytes(r['path']))
        if isinstance(r['path'], (bytes, bytearray)) else str(r['path']), 'kind': r['kind']}
        for r in authoritative_roots), key=lambda r: r['rootKey'])
    expected_roots = [roots, subject.root_set_hash, root, root, root]
    observed_roots = [context['roots'], initial['measurement']['storedRootSetHash'],
        initial['measurement']['observedContentRoot'], observed['postMeasurement']['observedContentRoot'],
        context.get('examinedContentRoot')]
    if finalization:
        # Keep the inherited projection coordinate for Collapse separately
        # from the complete manifest coordinates checked by finalization.
        # The full originals are retained and compared, never silently reduced
        # to content_entries' intentionally smaller set of fields.
        value = selected.raw.seal_value.capture
        from .finalization_journal import encode as finalization_bytes
        post = {key: SimpleNamespace(value=item) for key, item in
                observed['postMeasurement']['manifests'].items()}
        post_projection = content_root_set(post, core)
        expected_roots = [roots, subject.root_set_hash, root, root, root,
            value.input.root.hex(), value.input.root.hex(), value.input.root.hex(),
            value.input.manifests.hex(), value.input.manifests.hex()]
        observed_roots = [context['roots'], initial['measurement']['storedRootSetHash'],
            root, post_projection, root,
            identity(initial['measurement']['observedContentRoot']).hex(),
            identity(observed['postMeasurement']['observedContentRoot']).hex(),
            identity(context.get('examinedContentRoot')).hex(),
            finalization_bytes(tuple((key, canonical_bytes(item)) for key, item in
                initial['measurement']['manifests'].items())).hex(),
            finalization_bytes(tuple((key, canonical_bytes(item)) for key, item in
                observed['postMeasurement']['manifests'].items())).hex()]
    expected = dict(zip(CONTEXT_FIELDS, (
        value_bytes(header), selected.capture.context, _policy_value(current),
        value_bytes(header['subject']), value_bytes(expected_roots), _required_value(current_pairs, empty),
        canonical_bytes(current.get('verifiers') or []), value_bytes(expected_members), value_bytes(agent_record),
        selected.capture.source, (selected.raw.seal_value.capture.input.root if finalization
                                  else identity(root)), value_bytes(tuple(stream)),
        acquisition_bytes(tuple(event for invocation, _started, _finished in stream
            for event in acquisitions if event[0] == invocation) +
            tuple(event for event in acquisitions if event[0] not in {item[0] for item in stream})),
        value_bytes(observed['runnerResults']))))
    actual = dict(zip(CONTEXT_FIELDS, (
        value_bytes(initial), value_bytes(observed['returnedContext']), _policy_value(captured_policy),
        value_bytes(context['candidate']), value_bytes(observed_roots), _required_value(captured_pairs, captured_empty),
        canonical_bytes(captured_policy.get('verifiers') or []), value_bytes(actual_members), value_bytes(agent_record),
        identity(header['source']), identity(initial['measurement']['observedContentRoot']),
        value_bytes(tuple(projected_stream)), acquisition_bytes(tuple(projected_acquisitions)),
        value_bytes(projected_returns))))
    binding = '' if subject.instance_id == candidate.instance_id else manager._return_binding(subject.instance_id)
    claimed_binding = '' if subject.instance_id == candidate.instance_id else (candidate.mission_hash or '')
    projection = replace(values,
        expected_subject=manager._identity(manager._subject_digest(subject.instance_id, binding)),
        evidence_subject=manager._identity(manager._subject_digest(context['candidate']['instanceId'], claimed_binding)),
        current_requirement=manager._identity(current['requirementHash']),
        declared_verifiers=manager._identity(declared),
        expected_root_set=manager._identity(manager.prime.root_set_hash(list(authoritative_roots))))
    if role == 'primary':
        projection = replace(projection, evaluated_requirement=manager._identity(context['requirementHash']),
            executed_verifiers=manager._identity(executed), tested_root=manager._identity(root))
    elif role == 'staged':
        projection = replace(projection, staged_evaluated_requirement=manager._identity(context['requirementHash']),
            staged_executed_verifiers=manager._identity(executed), staged_examined_root=manager._identity(root))
    else: raise WorldlineError('EVALUATION_CAPTURE_INVALID', 'unknown context role')
    epoch = selected.cursor['epoch']
    raw_epoch = epoch.to_bytes((epoch.bit_length() + 7) // 8, 'little')
    expected_binding = BoundValue((selected.raw.seal_value.capture.start.store_id if finalization
                                  else manager.store.evaluation_terminal.pending.store),
        identity(subject.instance_id), identity(subject.content_id), identity(selected.cursor['run']),
        raw_epoch, identity(current['requirementHash']))
    prior_epoch = prepared_cursor['epoch']
    if type(prior_epoch) is not int or prior_epoch < 0:
        raise WorldlineError('EVALUATION_CURSOR_INVALID', 'prepared cursor epoch is not a magnitude')
    prior = (prior_epoch.to_bytes((prior_epoch.bit_length() + 7) // 8, 'little'), identity(prepared_cursor['run']))
    return attach(core, selected.raw, expected_binding=expected_binding, prepared_current=prior,
        expected_current=(raw_epoch, identity(selected.cursor['run'])), expected=expected, observed=actual,
        row_pairs=row_pairs,
        row_metadata=tuple(project_metadata(item, capture_source=selected.capture.source,
            invocation=stream[index] if index < len(stream) else None)
            for index, item in enumerate(selected.results)),
        required=current_pairs,
        policy=(1 if empty else 0) if not required else 2,
        projection=core._raw_collapse_request(projection), agent=agent)
