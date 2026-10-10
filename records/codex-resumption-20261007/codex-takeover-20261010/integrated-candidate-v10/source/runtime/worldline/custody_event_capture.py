"""Factual complete X5 joins; native owns quantities, chronology and mutation."""
from __future__ import annotations
import ctypes as C
from .protected_startup import require, exact_json
from .root_worker_codec import scoped_archive, scoped_restore_archive, raw_archive
from .retained_chain_kernel import _mapped


def successor(journal, raw):
    """Native encoding-only successor, never a Python lifecycle calculation."""
    require(type(raw) is bytes, 'CUSTODY_SUCCESSOR_ORIGINAL_BYTES_REQUIRED')
    function = journal.core._lib.wl_custody_successor_le_v2
    function.argtypes = [C.c_void_p, C.c_size_t, C.c_void_p, C.c_size_t, C.POINTER(C.c_uint64)]
    function.restype = C.c_int
    _mapped(journal, journal.core, (function,))
    data = (C.c_ubyte * len(raw)).from_buffer_copy(raw)
    needed = C.c_uint64()
    require(function(data if raw else None, len(raw), None, 0, C.byref(needed)) == 0,
            'CUSTODY_SUCCESSOR_NATIVE_SIZING_REFUSED')
    extent = needed.value
    require(C.c_size_t(extent).value == extent, 'CUSTODY_SUCCESSOR_HOST_EXTENT')
    output = (C.c_ubyte * extent)()
    require(function(data if raw else None, len(raw), output, len(output), C.byref(needed)) == 0
            and needed.value == extent, 'CUSTODY_SUCCESSOR_NATIVE_READBACK_REFUSED')
    _mapped(journal, journal.core, (function,))
    return bytes(output)


def quantity_scalar(raw):
    require(type(raw) is bytes, 'CUSTODY_RETAINED_QUANTITY_SQL_BLOB_REQUIRED')
    return raw


def root_state(journal, db, operation, before=None):
    from .custody_context_kernel import context_view
    if before is None:
        before, _ = journal._accepted_capture(db)
    view = context_view(journal, before, operation, 'UNKNOWN', 'RECONCILER', 'ROOT', '', None)
    return view['root']


def _profile(evidence):
    require(type(evidence) is dict, 'CUSTODY_ACTUAL_RAW_EVIDENCE_REQUIRED')
    root = evidence.get('root_evidence')
    subject = evidence.get('subject_evidence')
    if type(root) is dict:
        return root['source'], root['actor']
    require(type(subject) is dict and type(subject.get('binding')) is dict,
            'CUSTODY_ACTUAL_SUBJECT_EVIDENCE_REQUIRED')
    binding = subject['binding']
    return binding['source'], binding['actor']


def subject_context(journal, db, operation, subject_kind, subject, original, before, observed,
                    root_operation=None, kind=None, actor_role=None, query_purpose='MUTATION'):
    envelope = scoped_restore_archive(before)
    roster = envelope['owner_roster']
    require(root_operation is None or type(root_operation) is str,
            'CUSTODY_SUBJECT_ACTUAL_STARTER_OPERATION_DOMAIN')
    from .custody_context_kernel import context_view
    from .protected_root_worker import RootWorkerProcess
    if kind is None:
        kind = 'REQUEST_QUEUED' if subject_kind == 'REQUEST' else 'DRAIN_STOP_INTENT'
    if actor_role is None:
        actor_role = 'WORKER' if type(journal.owner) is RootWorkerProcess else 'FRONT'
    view = context_view(journal, before, operation, kind, actor_role, subject_kind, subject, original,
                        query_purpose=query_purpose)
    from .custody_subject_capture import actor_identity
    owner = journal.owner
    channel = getattr(owner, 'channel', None)
    if channel is None:
        slot = getattr(owner, 'slots', {}).get(root_operation)
        channel = None if slot is None else slot.channel
    require(root_operation is None or channel is not None, 'CUSTODY_SUBJECT_ACTUAL_CHANNEL_REQUIRED')
    actor = actor_identity(channel)
    source = roster['current']['source']
    context = roster['operation_context']
    binding = {'generation': view['event_generation'], 'operation': operation,
        'subject': subject, 'subgeneration': view['event_subgeneration'],
        'root_head': view['predecessor_root'], 'subject_head': view['predecessor_subject'],
        'source': source, 'actor': actor, 'original': raw_archive(original),
        'sender_credentials': actor['credentials']}
    return {'binding': binding, 'source_identity': source, 'actor_identity': actor,
        'operation_journal': _operation_raw(roster, context),
        'operation_journal_events': context['journal']['events'],
        'operation_authority_observations': context['operation_authority_observations'],
        'native_observations': tuple({'role': 'operation', 'material': item['material'],
            'observation': item['observation']} for item in context['operation_authority_observations']),
        'primitive_inputs': {key: int.from_bytes(value, 'little') for key, value in
            (('next_subgeneration', view['next_subgeneration']),
             ('reattach_epoch', view['next_reattach_epoch'])) if value is not None},
        'load_observation': observed, 'native_context': view}


def _operation_raw(roster, context):
    path = context['policy']['journal']
    values = [item['raw'] for item in roster['current']['paths'] if item['path'] == path]
    require(len(values) == 1 and type(values[0]) is bytes,
            'CUSTODY_OPERATION_ACTUAL_CURRENT_RAW_REQUIRED')
    return values[0]


def capture_event(journal, db, operation, kind, actor, subject_kind, subject, original, evidence, before, *,
                  query_purpose='MUTATION'):
    envelope = scoped_restore_archive(before)
    roster = envelope['owner_roster']
    context = roster['operation_context']
    if type(evidence) is dict and 'retained_record' in evidence:
        wrapper = evidence['retained_record']
        require(type(wrapper) is dict and set(wrapper) == {'original', 'x5'}
                and type(wrapper['original']) is bytes and wrapper['original'] == raw_archive(original),
                'CUSTODY_RETRY_EXACT_ORIGINAL_REQUIRED')
        rows = journal.capture_rows(db)['events']
        matches = [row for row in rows if row[4] == operation and row[5] == subject_kind
                   and row[6] == subject and row[8] == kind and row[10] == scoped_archive(wrapper)]
        require(len(matches) == 1, 'CUSTODY_RETRY_FULL_AUTHENTIC_WRAPPER_REQUIRED')
        selected_actor = matches[0][9] if actor is None else actor
        return selected_actor, wrapper
    source, actor_identity = _profile(evidence)
    require(source == roster['current']['source'], 'CUSTODY_EVENT_CURRENT_SOURCE_CHANGED')
    selected_actor = evidence.get('actor_role') if actor is None else actor
    require(type(selected_actor) is str, 'CUSTODY_EVENT_ACTUAL_ACTOR_ROLE_REQUIRED')
    from .custody_context_kernel import context_view
    root_generation = None
    root_profile = evidence.get('root_evidence')
    if kind in ('UNKNOWN', 'RECONCILED') and type(root_profile) is dict:
        uncertainty = root_profile.get('operands', {}).get('append_uncertainty')
        if type(uncertainty) is dict:
            root_generation = uncertainty['attempted_event']['generation']
    view = context_view(journal, before, operation, kind, selected_actor, subject_kind, subject, original,
                        query_purpose=query_purpose, root_generation=root_generation)
    primitives = dict(evidence.get('primitive_inputs', {}))
    for name, quantity in (('next_subgeneration', view['next_subgeneration']),
                           ('reattach_epoch', view['next_reattach_epoch'])):
        if quantity is not None:
            scalar = int.from_bytes(quantity, 'little')
            require(name not in primitives or primitives[name] == scalar,
                    'CUSTODY_EVENT_NATIVE_COUNTER_PROJECTION_CHANGED')
            primitives[name] = scalar
    x5 = {'schema': 'worldline.custody-x5-event-v2',
        'predecessor_root': view['predecessor_root'],
        'predecessor_subject': view['predecessor_subject'],
        'native_observations': raw_archive(evidence.get('native_observations', ())),
        'operation_journal': _operation_raw(roster, context),
        'operation_journal_events': context['journal']['events'],
        'operation_authority_observations': context['operation_authority_observations'],
        'source_identity': source, 'actor_identity': actor_identity,
        'primitive_inputs': primitives,
        'root_evidence': None if evidence.get('root_evidence') is None else raw_archive(evidence['root_evidence']),
        'subject_evidence': evidence.get('subject_evidence'),
        'subject_evidence_raw': None if evidence.get('subject_evidence') is None else raw_archive(evidence['subject_evidence'])}
    return selected_actor, {'original': raw_archive(original), 'x5': x5}
