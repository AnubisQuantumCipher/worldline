"""Two actual failed transfers with an independently admitted owner resolution.

This selected original-case fixture caller transports real socket requests and
native tracer observations. No operation identity, disposition, journal event,
closed witness, source-owner receipt or successful result is supplied by DATA.
"""
import sys
_approved = sys.modules.get('_worldline_approved_source_loader')
if _approved is None:
    raise SystemExit('HANDOFF_SEQUENCE_EARLY_APPROVED_SOURCE_REQUIRED')
_lease = _approved.current()
_lease.check()
import asyncio
import json
import os
from pathlib import Path
import socket
import struct
import uuid

SCHEMA = 'worldline.original-handoff-two-history-control-v1'
KEYS = {'schema', 'first_request', 'second_client', 'owner_reason', 'timeout', 'result_path'}
PAYLOAD = '/memfd:worldline-handoff-transfer-payload (deleted)'
TRAILER = '/memfd:worldline-handoff-transfer-trailer (deleted)'


def require(value, reason):
    if not value:
        raise RuntimeError(reason)


def actual_failure(campaign, raw_request, expected_kind):
    front = campaign.router.front
    require(front.phase == 'RECONSTRUCTED_CLOSED', 'HANDOFF_SEQUENCE_ACTUAL_RECONSTRUCTION_REQUIRED')
    fresh = front.fresh_front
    require(fresh.prior_owner is front and fresh.phase == 'FRONT_OWNED',
            'HANDOFF_SEQUENCE_FRESH_OWNER_LINEAGE_REQUIRED')
    fresh.source_lease.check(); fresh.principal.intact()
    fresh.principal.journal.load()
    journal = fresh.custody_journal
    journal.intact()
    matches = []
    for event in journal.history():
        if event['kind'] != expected_kind:
            continue
        event = journal.require_event(event)
        row = fresh.principal.journal.rows.get(event['operation'])
        if row is not None and bytes.fromhex(row['capture']['request']['rawRequest']) == raw_request:
            matches.append((event, row))
    require(len(matches) == 1, 'HANDOFF_SEQUENCE_UNIQUE_AUTHENTIC_REQUEST_FAILURE_REQUIRED')
    event, row = matches[0]
    require(row['state'] == 'QUARANTINED' and event['operation'] in fresh.principal.unresolved,
            'HANDOFF_SEQUENCE_ACTUAL_NATIVE_QUARANTINE_REQUIRED')
    require(not fresh.slots,
            'HANDOFF_SEQUENCE_ACTUAL_FAILED_SLOTS_NOT_RELEASED')
    return fresh, event, row


async def closed_owner(campaign):
    # The enclosing original case cap owns this polling/wait; no fresh grace.
    while campaign.router.front.phase != 'RECONSTRUCTED_CLOSED':
        collectors = tuple(campaign.router.front.collectors.values())
        if collectors:
            await asyncio.gather(*collectors)
        else:
            await asyncio.sleep(0.001)


async def owner_request(campaign, operation, reason, observed):
    # This is an actual distinct owner socket request. The existing operation
    # policy/native grant/use/broker decides it, including any refusal.
    require(os.geteuid() == 0, 'HANDOFF_SEQUENCE_GENUINE_OWNER_PRINCIPAL_REQUIRED')
    from live_campaign import canonical
    request = {'id': str(uuid.uuid4()), 'op': 'quarantine.resolve',
               'args': {'operation': operation, 'reason': reason}}
    raw = canonical(request) + b'\n'
    attempt = {'request_hex': raw.hex(), 'peer_hex': None, 'send_completed': False,
               'response_chunks_hex': [], 'response_lines_hex': [], 'terminal': None,
               'closed': False, 'failure': None}
    observed['owner_request'] = attempt
    writer = None
    primary = None
    try:
        reader, writer = await asyncio.open_unix_connection(campaign.original_descriptor['endpoint']['path'])
        channel = writer.get_extra_info('socket')
        peer = channel.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize('@iII'))
        attempt['peer_hex'] = peer.hex()
        pid, uid, gid = struct.unpack('@iII', peer)
        require(pid == os.getpid() and uid == os.geteuid() and gid == os.getegid(),
                'HANDOFF_SEQUENCE_ACTUAL_OWNER_ENDPOINT_PEER_CHANGED')
        writer.write(raw); await writer.drain(); attempt['send_completed'] = True
        pending = b''
        while True:
            while b'\n' not in pending:
                chunk = await reader.read(65536)
                attempt['response_chunks_hex'].append(chunk.hex())
                require(chunk, 'HANDOFF_SEQUENCE_OWNER_EOF_WITHOUT_TERMINAL')
                pending += chunk
            line, pending = pending.split(b'\n', 1)
            attempt['response_lines_hex'].append((line + b'\n').hex())
            value = json.loads(line)
            require(type(value) is dict and value.get('id') == request['id'],
                    'HANDOFF_SEQUENCE_OWNER_RESPONSE_ID_CHANGED')
            if 'event' in value:
                continue
            attempt['terminal'] = value
            require(set(value) == {'id', 'ok', 'result', 'error'}
                    and value['ok'] is True and value['error'] is None,
                    'HANDOFF_SEQUENCE_ACTUAL_OWNER_RESOLUTION_REFUSED')
            return value
    except BaseException as error:
        primary = error
        attempt['failure'] = {'type': type(error).__qualname__, 'reason': str(error)}
        raise
    finally:
        if writer is not None:
            try:
                writer.close()
                await writer.wait_closed(); attempt['closed'] = True
            except BaseException as error:
                attempt['close_failure'] = {'type': type(error).__qualname__, 'reason': str(error)}
                if primary is None:
                    raise
                primary.add_note('Actual owner socket close failed: ' + repr(error))


async def run(campaign, action, armed):
    from live_campaign import selected_json, sha
    plan_raw = _lease.file(action['handoff_sequence'], ('DATA',))
    plan = selected_json(action['handoff_sequence'])
    original = campaign.plan['cases'][campaign.name]
    starter = selected_json(original['clients']['starter']['request'])
    require(set(plan) == KEYS and plan['schema'] == SCHEMA
            and campaign.name == 'original-root-handoff-abort'
            and plan['first_request'] in starter['requests']
            and plan['timeout'] == campaign.spec['timeout']
            and type(plan['owner_reason']) is str and plan['owner_reason']
            and Path(plan['result_path']).parent == campaign.out
            and Path(plan['result_path']).name == 'handoff-sequence-control.archive.stdout',
            'HANDOFF_SEQUENCE_COMPLETE_SELECTED_ORIGINAL_CASE_JOIN_REQUIRED')
    second = plan['second_client']
    require(type(second) is dict and set(second) == {'kind', 'request', 'early_envelope', 'environment', 'timeout', 'wait'}
            and second['kind'] == 'client' and second['wait'] is True
            and second['timeout'] == original['clients']['starter']['timeout'],
            'HANDOFF_SEQUENCE_ORIGINAL_SOURCE_OWNED_SECOND_CLIENT_REQUIRED')
    second_record = selected_json(second['request'])
    require(second_record['uid'] == starter['uid'] and second_record['gid'] == starter['gid']
            and second_record['groups'] == starter['groups'] and len(second_record['requests']) == 1,
            'HANDOFF_SEQUENCE_DISTINCT_ORIGINAL_REQUESTER_BINDING_REQUIRED')
    first_raw = _lease.file(plan['first_request'], ('DATA',))
    second_raw = _lease.file(second_record['requests'][0], ('DATA',))
    require(first_raw != second_raw, 'HANDOFF_SEQUENCE_DISTINCT_REAL_REQUESTS_REQUIRED')
    require(action['target'] == 'front' and action['path'] == PAYLOAD
            and action['syscall'] == 'fsync' and action['effect'] == 'eio'
            and action['wait'] is False and armed is not None,
            'HANDOFF_SEQUENCE_ORIGINAL_FRONT_FAULT_JOIN_REQUIRED')
    observed = {'schema': SCHEMA, 'plan_hex': plan_raw.hex(), 'first_fault': None,
                'first_failure': None, 'owner_request': None, 'second_fault': None,
                'second_client': None, 'second_failure': None, 'failure': None}
    async def execute():
        selected = dict(action); selected.pop('handoff_sequence')
        observed['first_fault'] = await campaign.fault(selected, armed)
        await closed_owner(campaign)
        fresh, event, row = actual_failure(campaign, first_raw, 'HANDOFF_ABORT')
        observed['first_failure'] = {'event': event, 'row_event': row['event'],
                                     'state': row['state'], 'operation': event['operation']}
        await owner_request(campaign, event['operation'], plan['owner_reason'], observed)
        # Router moved to the actual newly reconstructed owner on that socket.
        require(campaign.router.front is fresh, 'HANDOFF_SEQUENCE_ACTUAL_OWNER_ROUTING_CHANGED')
        fresh.principal.intact(); fresh.principal.journal.load()
        row = fresh.principal.journal.rows[event['operation']]
        observed['first_resolution'] = {'state': row['state'], 'event': row['event'],
                                        'native': row['native']}
        require(event['operation'] not in fresh.principal.unresolved
                and row['state'] in ('RESOLVED_NO_EFFECT', 'SETTLED'),
                'HANDOFF_SEQUENCE_NATIVE_OWNER_RESOLUTION_NOT_COMPLETE')
        selected['path'] = TRAILER
        second_arm = asyncio.get_running_loop().create_future()
        task = asyncio.create_task(campaign.fault(selected, second_arm))
        campaign.fault_tasks.append(task)
        campaign.tasks.append(task)
        await second_arm
        observed['second_client'] = await campaign.client(second)
        observed['second_fault'] = await task
        await closed_owner(campaign)
        _fresh, event, row = actual_failure(campaign, second_raw, 'FRONT_RETAINED_ESCROW')
        observed['second_failure'] = {'event': event, 'row_event': row['event'],
                                      'state': row['state'], 'operation': event['operation']}
        require(observed['first_failure']['operation'] != event['operation'],
                'HANDOFF_SEQUENCE_DISTINCT_AUTHENTIC_OPERATIONS_REQUIRED')
    primary = None
    try:
        await asyncio.wait_for(execute(), timeout=plan['timeout'])
        _lease.check()
        require(_lease.file(action['handoff_sequence'], ('DATA',)) == plan_raw,
                'HANDOFF_SEQUENCE_SELECTED_PLAN_CHANGED')
        return observed
    except BaseException as error:
        primary = error
        observed['failure'] = {'type': type(error).__qualname__, 'reason': str(error)}
        if not armed.done(): armed.set_exception(error)
        raise
    finally:
        try:
            # The original complete campaign collector retains every *.stdout
            # file in this exact private result directory. This is explicitly a
            # typed control archive, not a purported child stdout receipt.
            from worldline.root_worker_codec import raw_archive
            from custody_runtime_controls_v35 import durable
            raw = raw_archive(observed)
            durable(Path(plan['result_path']), raw)
            campaign.records.append({'action': {'kind': 'handoff-sequence-actual-observation'},
                'typed_control_archive': plan['result_path'], 'sha256': sha(raw),
                'primary_failure': observed['failure']})
        except BaseException as error:
            if primary is None: raise
            primary.add_note('Actual handoff sequence retention failed: ' + repr(error))
