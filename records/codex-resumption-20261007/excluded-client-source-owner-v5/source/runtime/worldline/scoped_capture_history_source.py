"""Factual retained closure and absence preimages; no classification or grant.

SOURCE_UNRUN. Call under the protected producer order. Owner SQL correspondence
must authenticate the complete event arrays. A missing slot never drops its row
or reuses a stored LIVE observation as current physical evidence.
"""
from dataclasses import fields
from .resource_os_observation import PhysicalFacts
import json
from . import resource_scoped_run_ledger as S, resource_run_ledger as L
from .protected_resource_runtime import canonical, lossless_data, require

OWNER_DOMAIN = 'worldline.scoped-history-owner-source-v1'
DERIVATION_DOMAIN = 'worldline.scoped-history-derivation-v1'


def capture_history_owner(producer, owner_state=None):
    producer.intact()
    producer.journal.load()
    producer.observations.load()
    captured = {'schema': OWNER_DOMAIN, 'launch_events': tuple(producer.journal.events),
        'launch_head': producer.journal.head,
        'observation_events': tuple(producer.observations.events),
        'observation_head': producer.observations.head,
        'owned_reservations': tuple(bytes.fromhex(key) for key in producer.slots),
        'binding': producer.binding, 'installation': producer.lease.spec}
    if owner_state is None:
        principal = getattr(producer.lease, 'canonical_operation_principal', None)
        root_owner = getattr(principal, 'root_worker', None)
        if root_owner is None:
            root_owner = getattr(principal, 'root_worker_process', None)
        if root_owner is not None:
            from .root_worker_current_state import capture_startup_owner_state
            owner_state = capture_startup_owner_state(root_owner)
    if owner_state is not None:
        from .scoped_capture_owner_projection import owner_sql_history
        sql = owner_sql_history(owner_state)
        captured['root_events'] = sql['root_events']
        captured['root_owner_state'] = owner_state
    return captured


def _wire(raw):
    # Preserve the original producer's two raw grammars, not a normalized label.
    if type(raw) is bytes:
        return raw
    require(type(raw) is str, 'SCOPED_HISTORY_ORIGINAL_RAW_BYTES_REQUIRED')
    decoded = bytes.fromhex(raw)
    require(decoded.hex() == raw, 'SCOPED_HISTORY_ORIGINAL_RAW_HEX_CHANGED')
    return decoded


def _event_preimages(events):
    return tuple({'event': event, 'json': canonical(event)} for event in events)


def _original_projection(binding, resource_config, body):
    source = body['current_source']
    catalogue_encoded = json.loads(source['catalogue_raw'])
    catalogue = S.restore(catalogue_encoded)
    root_value = lossless_data({'store_genesis': source['actual_store_genesis'],
        'store_id': source['actual_store_id'], 'roots': source['actual_roots'],
        'prime': source['actual_prime']})
    return {'schema': 'worldline.complete-scoped-capture-source-v1',
        'current': body['packet'].current, 'source': source,
        'source_scoped': S.record(source), 'source_json': canonical(S.record(source)),
        'root_value': root_value, 'root_json': canonical(root_value),
        'catalogue': catalogue, 'catalogue_json': source['catalogue_raw'],
        'catalogue_encoded': catalogue_encoded,
        'gate_config': json.loads(source['gate_config_raw']),
        'binding': binding, 'binding_json': canonical(binding),
        'resource_config': resource_config}


def enrich_history_source(producer, row, fact, source, owner, actual_owner=None):
    """Add complete preimages to an original source without altering any fact."""
    require(owner['schema'] == OWNER_DOMAIN, 'SCOPED_HISTORY_OWNER_CAPTURE_REQUIRED')
    # Recapture transports wrap the exact old non-owned source; keep the wrapper.
    original = source.get('retained_original', source)
    derivation = {'schema': DERIVATION_DOMAIN,
        'launch_preimages': _event_preimages(owner['launch_events']),
        'prepared_rows': tuple({'event': event,
            'row': L.restore_dto(event['payload']['row'])}
            for event in owner['launch_events'] if event['cause'] == 'PREPARED')}
    historical = original.get('historical')
    if historical is not None and historical.get('schema') == 'worldline.genuine-retained-closed-projection-v1':
        witness = historical['witness']
        body = S.restore(witness['payload'])
        raw = body['source']['kernel']
        root = 'outer' in raw
        held = raw['held']
        closed = raw['closed']['record'] if root else raw['closed']
        retained_derivation = body['source'].get('history_derivation')
        sample_source = (retained_derivation['pre_enrichment_source']
                         if retained_derivation is not None and
                            'pre_enrichment_source' in retained_derivation else
                         {name: value for name, value in body['source'].items()
                          if name not in ('launch_prefix', 'history_derivation')})
        held_events = [event for event in body['source']['events'] if event['cause'] == 'HELD']
        require(len(held_events) == 1, 'SCOPED_HISTORY_FULL_HELD_EVENT_REQUIRED')
        held_event_json = canonical(held_events[0])
        import hashlib
        prepared_events = [event for event in original['events'] if event['cause'] == 'PREPARED']
        require(len(prepared_events) <= 1, 'SCOPED_HISTORY_FULL_PREPARATION_REQUIRED')
        blank_values = {field.name: None for field in fields(PhysicalFacts)}
        blank_values.update(current=fact.current, current_epoch=fact.current_epoch,
            current_universe_head=fact.current_universe_head,
            current_ledger_head=fact.current_ledger_head, retained=row.bound,
            observation_head=bytes.fromhex(original['challenge']), phase='UNAVAILABLE')
        if prepared_events:
            blank_values['intent'] = hashlib.sha256(canonical(prepared_events[0])).digest()
        blank = PhysicalFacts(**blank_values)
        derivation.update(witness_json=canonical(witness), witness_body=body,
            original_projection=_original_projection(owner['binding'],
                None if producer is None else producer.cfg, body),
            projection_scoped=S.record({'current': blank, 'witness': witness}),
            projection_value={'current': blank, 'witness': witness},
            projection_json=canonical(S.record({'current': blank, 'witness': witness})),
            original_source_json=canonical(S.record(body['source'])),
            original_source_value=body['source'],
            original_source_scoped=S.record(body['source']),
            held_event_json=held_event_json,
            held_event_value=held_events[0],
            held_event_digest=hashlib.sha256(held_event_json).digest(),
            sample_source=sample_source,
            sample_source_json=(retained_derivation['pre_enrichment_source_json']
                if retained_derivation is not None and
                   'pre_enrichment_source_json' in retained_derivation else
                None if sample_source.get('head_encoding') in ('OPERATION_ARCHIVE', 'ROOT_RAW_ARCHIVE')
                else canonical(sample_source)),
            manager_view={'stdout': _wire(raw['manager']['stdout']),
                'stderr': _wire(raw['manager']['stderr']),
                'returncode': raw['manager']['returncode']},
            closed_frame=_wire(closed['frame']), held_frame=_wire(held['frame']),
            namespace_wait=_wire(raw['namespace_wait']), helper_wait=_wire(raw['helper_wait']),
            original_launch_preimages=_event_preimages(body['launch_prefix']))
        if root:
            require(actual_owner is not None,
                    'SCOPED_HISTORY_ORIGINAL_ROOT_SOURCE_OWNER_REQUIRED')
            helper_path = actual_owner.plan['helper']
            derivation.update(dispatch_json=canonical(raw['dispatch']['resource_dispatch']),
                helper_path=helper_path,
                helper_image_bytes=actual_owner.source_lease.file(helper_path, ('EXECUTABLE',)))
    answer = dict(source)
    # Retain the original sample before typed derivation enrichment, independently
    # of the complete enriched witness; never change its observation head.
    if 'history_derivation' not in source and 'retained_original' not in source:
        derivation['pre_enrichment_source'] = source
        if 'historical' not in source:
            derivation['pre_enrichment_source_json'] = (
                None if source.get('head_encoding') in ('OPERATION_ARCHIVE', 'ROOT_RAW_ARCHIVE')
                else canonical(source))
    answer['history_derivation'] = derivation
    return answer


def capture_closed_receipt(slot):
    """Read original owned primitives only; does not poll/receive/send CLOSED.

    This optional supplemental receipt can be retained by the integration owner
    alongside the original witness before its descriptors close. It does not
    manufacture terminal status or replace the original complete closure packet.
    """
    import os, socket, struct, select
    from .protected_resource_runtime import identity_record, kernel_bytes
    def pidfd(fd):
        poll = select.poll()
        mask = select.POLLIN | select.POLLHUP | select.POLLERR
        poll.register(fd, mask)
        return {'fd': fd, 'identity': identity_record(os.fstat(fd)),
            'fdinfo': kernel_bytes('/proc/self/fdinfo/' + str(fd)),
            'poll': {'events': mask, 'timeout': 0, 'returned': tuple(poll.poll(0))}}
    return {'namespace_pidfd': pidfd(slot.namespace_pidfd),
        'helper_pidfd': pidfd(slot.helper_pidfd),
        'namespace_identity': identity_record(os.fstat(slot.namespace_fd)),
        'peer': slot.connection.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize('@iII')),
        'held': slot.held, 'closed': slot.closed,
        'closed_event': getattr(slot, 'closed_event', None), 'outer': getattr(slot, 'outer', None)}


def capture_receiver_history_owner(owner, owner_state, actual_roster):
    """Acquire full SQL history over the specific authentic owner's roster."""
    import os
    from .scoped_capture_owner_projection import owner_sql_history
    from .protected_resource_runtime import identity_record, kernel_bytes
    from .protected_root_worker import RootWorkerFront, RootWorkerProcess, RootWorkerIntake
    from .root_worker_closed import ClosedFrontEscrow
    from .root_owned_descriptor_roster import OwnedDescriptorRoster
    require(type(actual_roster) is OwnedDescriptorRoster and not actual_roster.closed,
            'SCOPED_HISTORY_ACTUAL_ROSTER_REQUIRED')
    roster = actual_roster
    if type(owner) in (RootWorkerProcess, RootWorkerIntake):
        custody = owner.custody
        require(custody is not None and custody.owned_roster is roster,
                'SCOPED_HISTORY_ACTUAL_CUSTODY_ROSTER_REQUIRED')
        if type(custody) is ClosedFrontEscrow:
            require(custody.intake is owner and custody.offer.owned_roster is roster
                    and custody.frame is custody.offer.frame,
                    'SCOPED_HISTORY_ACTUAL_CLOSED_INTAKE_REQUIRED')
    else:
        require(type(owner) is RootWorkerFront,
                'SCOPED_HISTORY_ACTUAL_FRONT_OR_CUSTODY_OWNER_REQUIRED')
        guard = getattr(owner.lease, 'exec_custody', None)
        offer = getattr(owner, 'current_offer', None)
        closed_guard = getattr(roster, 'closed_front_guard', None)
        closed_offer = getattr(roster, 'closed_front_offer', None)
        require(roster.front is owner or
                (type(guard) is ClosedFrontEscrow and guard.fresh_lease is owner.lease
                 and getattr(guard, 'reconstructed_roster', None) is roster
                 and roster.reconstruction_owner is owner) or
                (offer is not None and offer.p is owner.principal
                 and (offer.owned_roster is roster or
                      getattr(owner, '_retained_owned_roster', None) is roster)) or
                (type(closed_guard) is ClosedFrontEscrow and closed_guard.front is owner
                 and roster.reconstruction_owner is owner) or
                (closed_offer is not None and closed_offer.p is owner.principal
                 and closed_offer.owned_roster is roster
                 and roster.reconstruction_owner is owner),
                'SCOPED_HISTORY_ACTUAL_FRONT_ROSTER_REQUIRED')
    roster.intact(owner)
    captured = owner_sql_history(owner_state)
    inventory = tuple({'role': name, 'fd': fd,
        'identity': identity_record(os.fstat(fd)),
        'fdinfo': kernel_bytes('/proc/self/fdinfo/' + str(fd))}
        for name, fd in roster.fds.items())
    reservations = []
    for entry in inventory:
        parts = entry['role'].split('/')
        if len(parts) >= 3 and parts[0] == 'row':
            reservation = bytes.fromhex(parts[1])
            require(reservation.hex() == parts[1],
                    'SCOPED_HISTORY_FULL_RECEIVER_ROLE_INVALID')
            if reservation not in reservations:
                reservations.append(reservation)
    return {'schema': OWNER_DOMAIN, **captured,
        'owned_reservations': tuple(reservations),
        'descriptor_inventory': inventory,
        'installation': owner_state['installation']}


def recapture_unowned_source(owner, row, blank, stored_source, owner_state, actual_roster):
    """Project acquired SQL facts, never cached LIVE or a fabricated syscall.

    The complete receiver inventory is the original SCM/OFD acquisition, not an
    assertion that a reservation has no process anywhere on the machine. No
    cgroup absence, PID reuse or missing /proc entry licenses release.
    """
    import hashlib
    from dataclasses import replace
    history_owner = capture_receiver_history_owner(owner, owner_state, actual_roster)
    key = row.bound.reservation.hex()
    require(row.bound.reservation not in history_owner['owned_reservations'],
            'SCOPED_HISTORY_RECEIVER_ACTUAL_OWNED_ROW')
    selected = tuple(event for event in history_owner['launch_events']
        if event['reservation'] == key and event['cause'] != 'OBSERVATION')
    source = {'reservation': key, 'journal_head': history_owner['launch_head'],
        'challenge': blank.observation_head.hex(), 'events': selected, 'kernel': None}
    prepared = tuple(event for event in selected if event['cause'] == 'PREPARED')
    require(len(prepared) <= 1, 'SCOPED_HISTORY_DUPLICATE_ORIGINAL_PREPARATION')
    physical = blank
    if prepared:
        require(L.restore_dto(prepared[0]['payload']['row']).bound == row.bound,
                'SCOPED_HISTORY_ACTUAL_PREPARED_FULL_BINDING_CHANGED')
        physical = replace(physical,
            intent=hashlib.sha256(canonical(prepared[0])).digest())
        if all(event['cause'] in ('PREPARED', 'MACHINE_ADMISSION') for event in selected):
            physical = replace(physical, phase='NEVER_DISPATCHED')
            return physical, enrich_history_source(None, row, physical, source, history_owner)
    witnesses = tuple(event for event in history_owner['observation_events']
        if event['cause'] == 'CLOSED_NATIVE_WITNESS' and event['reservation'] == key)
    if witnesses:
        witness = witnesses[-1]
        body = S.restore(witness['payload'])
        packet = body['packet']
        require(type(packet) is S.ScopedPacket and
            packet.request.original.bound == row.bound and
            body['original_row'].bound == row.bound and
            body['original_row'].scope == row.scope,
            'SCOPED_HISTORY_ACTUAL_FULL_CLOSED_ORIGIN_CHANGED')
        matches = tuple(index for index, item in enumerate(packet.rows)
                        if item.bound == row.bound)
        require(len(matches) == 1, 'SCOPED_HISTORY_ACTUAL_WITNESS_MEMBERSHIP_CHANGED')
        old = packet.facts[matches[0]]
        require(old.phase == 'NAMESPACE_CLOSED',
                'SCOPED_HISTORY_RETAINED_LIVE_FACT_IS_NOT_CLOSURE')
        projection_blank = replace(blank, intent=physical.intent)
        physical = replace(old, current=blank.current, current_epoch=blank.current_epoch,
            current_universe_head=blank.current_universe_head,
            current_ledger_head=blank.current_ledger_head,
            observation_head=hashlib.sha256(canonical(S.record(
                {'current': projection_blank, 'witness': witness}))).digest())
        # Stored native bytes remain input data. Ada replays this exact complete
        # material before agreeing that any copied old field is a closed fact.
        source['historical'] = {
            'schema': 'worldline.genuine-retained-closed-projection-v1',
            'witness': witness, 'actual_native_redecision': S.record(body['native']),
            'original_physical': S.record(old)}
    else:
        source['historical'] = {
            'schema': 'worldline.missing-owned-closed-witness-v1', 'retained': 'UNKNOWN'}
    return physical, enrich_history_source(None, row, physical, source, history_owner,
                                          actual_owner=owner)


def owned_protocol_preimages(entry, source, history):
    """Complete original owned-protocol byte preimages, never a verdict.

    The caller inserts this value into the source before its original archive
    observation preimage is sealed. No descriptor is polled, message consumed,
    owner reconstructed or permission calculated by this encoder.
    """
    import hashlib
    import os
    raw = source['kernel']
    held = raw['held']
    root = entry['kind'] == 'ROOT'
    arguments = (entry['dispatch']['helper_arguments'] if root
                 else entry['dispatch']['payload']['helper_arguments'])
    initial_proc = held['helper_proc'] if root else held
    reservation = entry['row'].bound.reservation.hex()
    events = tuple(event for event in history['launch_events']
        if event['reservation'] == reservation and event['cause'] != 'OBSERVATION')
    def manager_view(manager):
        return {'stdout': _wire(manager['stdout']), 'stderr': _wire(manager['stderr']),
                'returncode': manager['returncode']}
    answer = {'schema': 'worldline.owned-scoped-protocol-preimages-v1',
        'reservation': reservation, 'events': events,
        'launch_preimages': _event_preimages(history['launch_events']),
        'prepared_rows': tuple({'event': event, 'row': L.restore_dto(event['payload']['row'])}
            for event in history['launch_events'] if event['cause'] == 'PREPARED'),
        'held_frame': _wire(held['frame']),
        'held_manager_view': manager_view(held['manager']),
        'manager_view': manager_view(raw['manager']),
        'argument_bytes': tuple(os.fsencode(word) for word in arguments),
        'held_command': _wire(initial_proc['cmdline']),
        'held_maps': _wire(initial_proc['maps']),
        'held_cgroup': _wire(initial_proc['cgroup'] if root else held['proc_cgroup'])}
    if raw['closed'] is not None:
        closed = raw['closed']['record'] if root else raw['closed']
        answer['closed_frame'] = _wire(closed['frame'])
    if not root:
        challenge = {'dispatch': entry['dispatch'], 'held_frame': held['frame'],
            'peer': held['peer'], 'namespace': held['namespace'], 'manager': held['manager'],
            'maps': held['maps'], 'proc_cgroup': held['proc_cgroup']}
        answer.update(held_challenge_value=challenge,
                      held_challenge_json=canonical(challenge))
        held_events = tuple(event for event in events if event['cause'] == 'HELD')
        require(len(held_events) == 1, 'SCOPED_OWNED_PROTOCOL_GENUINE_HELD_EVENT_REQUIRED')
        encoded = canonical(held_events[0])
        answer.update(held_event_value=held_events[0], held_event_json=encoded,
                      held_event_digest=hashlib.sha256(encoded).digest())
    return answer
