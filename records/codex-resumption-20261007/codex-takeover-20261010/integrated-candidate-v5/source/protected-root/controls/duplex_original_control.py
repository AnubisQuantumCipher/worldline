"""Operator-enrolled controls over actual admitted Worker/Relay objects only."""
import asyncio
import ctypes
import json
import os
from pathlib import Path
import socket
import stat
import sys

SCHEMA = 'worldline.original-custody-worker-duplex-control-v1'
MODES = {'gap-write', 'shutdown-held', 'eof-held'}
_PLAN = None
_PLAN_RAW = None
_USED = False


def require(value, reason):
    if not value:
        raise RuntimeError(reason)


def configure_from_source(path):
    global _PLAN, _PLAN_RAW
    require(_PLAN is None, 'DUPLEX_CONTROL_ALREADY_ENROLLED')
    approved = sys.modules.get('_worldline_approved_source_loader')
    require(approved is not None, 'DUPLEX_CONTROL_ACTUAL_SOURCE_LEASE_REQUIRED')
    source = approved.current()
    raw = source.file(str(path), ('DATA',))
    plan = json.loads(raw)
    require(set(plan) == {'schema', 'request_id', 'mode', 'timeout', 'progress', 'result_path'}
            and plan['schema'] == SCHEMA and plan['mode'] in MODES,
            'DUPLEX_CONTROL_EXACT_SELECTED_PLAN_REQUIRED')
    require(type(plan['request_id']) is str and plan['request_id']
            and type(plan['timeout']) in (int, float) and plan['timeout'] > 0
            and type(plan['progress']) is list and len(plan['progress']) == 2
            and all(type(value) is dict and set(value) == {'event', 'data'} for value in plan['progress']),
            'DUPLEX_CONTROL_ORIGINAL_REQUEST_PROGRESS_TIMEOUT_REQUIRED')
    target = Path(plan['result_path'])
    require(target.is_absolute() and any(parent.parent == Path('/srv')
            and parent.name.startswith('cosmogony-canonical-v1.control-') for parent in target.parents),
            'DUPLEX_CONTROL_DISPOSABLE_RESULT_REQUIRED')
    info = target.parent.lstat()
    require(stat.S_ISDIR(info.st_mode) and info.st_uid == 0 and not info.st_mode & 0o077
            and not os.path.lexists(target), 'DUPLEX_CONTROL_PRECREATED_EXCLUSIVE_PRIVATE_OUTPUT_REQUIRED')
    source.check()
    _PLAN_RAW, _PLAN = raw, plan


def failure(error):
    return {'module': type(error).__module__, 'type': type(error).__qualname__,
            'message': str(error), 'errno': getattr(error, 'errno', None), 'repr': repr(error)}


def ticket_observation(ticket):
    # The actual ticket's output.record points back to the service record;
    # archive the actual packet/native values, not that object-reference cycle.
    value = {key: ticket[key] for key in ('kind', 'request', 'reply', 'result', 'complete')}
    for key in ('frame', 'send'):
        if key in ticket:
            value[key] = ticket[key]
    value['failure'] = None if ticket['failure'] is None else failure(ticket['failure'])
    if ticket['output'] is not None:
        value['produced'] = ticket['output']['produced']
        value['worker_native'] = ticket['output']['native']
    return value


def publish(path, value):
    from worldline.root_worker_codec import raw_archive
    path = Path(path)
    raw = raw_archive(value)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    try:
        with os.fdopen(os.dup(fd), 'wb') as stream:
            stream.write(raw); stream.flush(); os.fsync(stream.fileno())
        os.fsync(fd)
    finally:
        os.close(fd)
    directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    require(path.read_bytes() == raw, 'DUPLEX_CONTROL_ACTUAL_RESULT_READBACK_CHANGED')


def validate_front_observations(observed, plan):
    """Check actual clientwriter decisions, never Worker Relay delivery status."""
    from worldline.client_peer import validate_observation
    from worldline.root_worker_codec import raw_restore_archive, scoped_restore_archive
    from worldline.root_worker_output_kernel import ReplayDisposition
    request = observed['request']
    validate_observation(request)
    require(request['requestId'] == plan['request_id']
            and observed['actual_original']['original_request'] == request,
            'DUPLEX_CONTROL_AUTHENTIC_PUBLIC_REQUEST_JOIN_REQUIRED')
    observation_id = request['observationId']
    queries = []
    for row in observed['actual_native_output_queries']:
        if not row['entry'].endswith('.replay_output') or row['error'] is not None:
            continue
        raw = scoped_restore_archive(row['raw'])
        require(raw['schema'] == 'worldline.custody-mutation-v2',
                'DUPLEX_CONTROL_FRONT_ACTUAL_MUTATION_INPUT_REQUIRED')
        candidate = raw['candidate']
        original = raw_restore_archive(candidate['record']['original'])
        document = original['original_request']
        validate_observation(document)
        if document['requestId'] == plan['request_id']:
            require(document == request and original == observed['actual_original']
                    and candidate['subject_kind'] == 'REQUEST' and candidate['subject'] == observation_id,
                    'DUPLEX_CONTROL_FRONT_AUTHENTIC_OBSERVATION_SUBJECT_JOIN_REQUIRED')
            queries.append(row)
    held = [index for index, row in enumerate(queries)
            if row['result']['disposition'] == ReplayDisposition.HOLD.value
            and row['result']['ordinal'] == b'\x01']
    require(held, 'DUPLEX_CONTROL_ACTUAL_FRONT_CLIENTWRITER_HOLD_REQUIRED')
    records = [record for record in observed['actual_relay_records']
               if record.get('body', {}).get('request') == observation_id]
    require(records and all(record['body']['admission_head'] == observed['actual_intake']['event_id']
                            for record in records),
            'DUPLEX_CONTROL_FRONT_ACTUAL_INTAKE_RELAY_JOIN_REQUIRED')
    require(any(record.get('prefix_query', {}).get('quantity') == b'\x00'
                for record in records), 'DUPLEX_CONTROL_ACTUAL_FRONT_EMPTY_PREFIX_REQUIRED')
    if plan['mode'] == 'gap-write':
        dropped = [index for index, row in enumerate(queries)
                   if row['result']['disposition'] == ReplayDisposition.DROP.value
                   and row['result']['ordinal'] == b'\x01']
        require(any(index > held[0] for index in dropped),
                'DUPLEX_CONTROL_ACTUAL_FRONT_CLIENTWRITER_DROP_REQUIRED')
        for ordinal in ('0', '1'):
            written = [record for record in records
                       if record['body'].get('payload', {}).get('out_seq') == ordinal
                       and 'written' in record]
            require(len(written) == 1 and written[0]['writes'],
                    'DUPLEX_CONTROL_ACTUAL_FRONT_SINGLE_ORIGINAL_WRITE_REQUIRED_' + ordinal)
        require(any(record.get('native_drop', {}).get('disposition') == ReplayDisposition.DROP.name
                    and record['body']['payload']['out_seq'] == '1' and 'writes' not in record
                    for record in records),
                'DUPLEX_CONTROL_ACTUAL_FRONT_DUPLICATE_NO_WRITE_REQUIRED')
    else:
        require(observed['actual_relay_failure'] is not None
                and any(part['call'] == 'recv' and part['raw'] == b''
                        and part['result'] == 0 and part['errno'] == 0
                        for receipt in observed['actual_relay_receives'] for part in receipt['parts']),
                'DUPLEX_CONTROL_ACTUAL_FRONT_PEER_EOF_RECEIPT_REQUIRED')
        require(not any('written' in record for record in records),
                'DUPLEX_CONTROL_ACTUAL_FRONT_WRITE_AFTER_HELD_EOF')


async def exercise(service, record, output_lock):
    global _USED
    require(_PLAN is not None, 'DUPLEX_CONTROL_NOT_SOURCE_ENROLLED')
    peer = record['peer']
    document = peer.observation()
    if document['requestId'] != _PLAN['request_id']:
        return
    require(not _USED, 'DUPLEX_CONTROL_ACTUAL_REQUEST_EXERCISED_TWICE')
    _USED = True
    emitter = record['emitter']
    journal = service.owner.custody_journal
    from worldline.root_worker_output_kernel import ReplayDisposition
    require(getattr(journal, '_control_capture', None) is not None,
            'DUPLEX_CONTROL_ACTUAL_NATIVE_QUERY_OBSERVER_REQUIRED')
    query_start = len(journal.output_observations)
    journal.require_event(service.owner.custody_ack)
    journal.require_event(record['intake'])
    require(peer.custody_mode == 'RELAY' and not emitter.records and not emitter.written,
            'DUPLEX_CONTROL_GENUINE_FRESH_RELAY_INTAKE_REQUIRED')
    observed = {'schema': SCHEMA, 'selected_plan_raw': _PLAN_RAW,
                'actual_pid': os.getpid(), 'actual_euid': os.geteuid(),
                'request': document, 'intake': record['intake'], 'mode': _PLAN['mode'],
                'source_before': service.owner.source_lease.check(), 'steps': [],
                'phase_acceptance': False}
    primary = None
    try:
        async with output_lock:
            values = [dict(value, id=document['requestId']) for value in _PLAN['progress']]
            zero = emitter.produce('PROGRESS_BYTES', values[0])
            one = emitter.produce('PROGRESS_BYTES', values[1])
            require(zero['out_seq'] == '0' and one['out_seq'] == '1',
                    'DUPLEX_CONTROL_ACTUAL_NATIVE_RESERVED_ORDINALS_CHANGED')
            observed['produced'] = (zero, one)
            # This original API sends the real frame/source and performs a real
            # PEER_HELD exchange. No held frame is given a fabricated ACK.
            await asyncio.wait_for(service._forward_output(record, one, []), _PLAN['timeout'])
            held = record['output_transports'][-1]
            require(held['output']['produced'] == one and not held['complete']
                    and held['result'] is None and held['reply'] is None and not emitter.written,
                    'DUPLEX_CONTROL_ACTUAL_ONE_NOT_HELD_WITHOUT_WRITE')
            require(record.get('peer_status'), 'DUPLEX_CONTROL_ACTUAL_PEER_HELD_RECEIPT_MISSING')
            require(record['replay_decisions'][-1]['disposition'] == ReplayDisposition.WRITE.name
                    and not record['peer_status'][-1]['written'],
                    'DUPLEX_CONTROL_WORKER_DELIVERY_AND_AUTHENTIC_EMPTY_PREFIX_REQUIRED')
            observed['steps'].append({'held_one': ticket_observation(held),
                                      'actual_peer_status': record['peer_status'][-1]})
            if _PLAN['mode'] == 'gap-write':
                await asyncio.wait_for(service._forward_output(record, zero, []), _PLAN['timeout'])
                zero_ticket = record['output_transports'][-1]
                require(zero_ticket is not held and zero_ticket['output']['produced'] == zero,
                        'DUPLEX_CONTROL_ACTUAL_ZERO_TICKET_REQUIRED')
                await asyncio.wait_for(asyncio.to_thread(service.relay_replies.wait, zero_ticket),
                                       _PLAN['timeout'])
                # Genuine fresh status after the zero ACK triggers native
                # redecision of the Front's pending one, not a control override.
                await asyncio.wait_for(asyncio.to_thread(service.peer_status, record), _PLAN['timeout'])
                await asyncio.wait_for(asyncio.to_thread(service.relay_replies.wait, held), _PLAN['timeout'])
                require(zero_ticket['complete'] and held['complete'] and zero_ticket['result'] is not None
                        and held['result'] is not None and tuple(value['out_seq'] for value in emitter.written) == ('0', '1'),
                        'DUPLEX_CONTROL_GENUINE_ORDERED_WRITTEN_ACKS_REQUIRED')
                replay = emitter.replay(one)
                require(replay.disposition is ReplayDisposition.WRITE,
                        'DUPLEX_CONTROL_GENUINE_WORKER_DUPLICATE_DELIVERY_REQUIRED')
                observed['duplicate_worker_delivery'] = {'ordinal': replay.ordinal,
                                                        'disposition': replay.disposition.name}
                await asyncio.wait_for(service._forward_output(record, one, []), _PLAN['timeout'])
                duplicate = record['output_transports'][-1]
                require(duplicate is not held and duplicate['output']['produced'] == one
                        and not duplicate['complete'] and duplicate['result'] is None
                        and record['replay_decisions'][-1]['disposition'] == ReplayDisposition.WRITE.name
                        and tuple(value['out_seq'] for value in emitter.written) == ('0', '1'),
                        'DUPLEX_CONTROL_ACTUAL_DUPLICATE_RELAY_WROTE_AGAIN')
                observed['steps'].append({'actual_duplicate_delivery': ticket_observation(duplicate)})
                observed['steps'].append({'zero_written': ticket_observation(zero_ticket),
                    'one_written': ticket_observation(held), 'actual_written': tuple(emitter.written),
                    'actual_peer_status': record['peer_status'][-1]})
            else:
                source = service.owner.source_lease.check()
                channel = service.relay_channel
                fd = channel.fileno()
                libc = ctypes.CDLL(None, use_errno=True)
                if _PLAN['mode'] == 'shutdown-held':
                    call, arguments = 'shutdown', (fd, socket.SHUT_RDWR)
                    function = libc.shutdown; function.argtypes = (ctypes.c_int, ctypes.c_int)
                else:
                    # Linux close alone does not interrupt another thread's blocked
                    # recv: that syscall retains the open file description. Release
                    # the real relay reader before disposing this channel descriptor.
                    shutdown = libc.shutdown
                    shutdown.argtypes = (ctypes.c_int, ctypes.c_int)
                    shutdown.restype = ctypes.c_int
                    ctypes.set_errno(0)
                    shutdown_result = shutdown(fd, socket.SHUT_RDWR)
                    shutdown_errno = ctypes.get_errno()
                    observed['steps'].append({'call': 'shutdown', 'args': (fd, socket.SHUT_RDWR),
                                              'source': source, 'result': shutdown_result,
                                              'errno': shutdown_errno})
                    if shutdown_result == -1:
                        raise OSError(shutdown_errno, 'actual EOF shutdown', fd)
                    require(shutdown_result == 0, 'DUPLEX_CONTROL_UNEXPECTED_ACTUAL_EOF_SHUTDOWN_RESULT')
                    source = service.owner.source_lease.check()
                    actual_detached = channel.detach()
                    require(actual_detached == fd, 'DUPLEX_CONTROL_ACTUAL_DETACHED_DESCRIPTOR_CHANGED')
                    call, arguments = 'close', (actual_detached,)
                    function = libc.close; function.argtypes = (ctypes.c_int,)
                function.restype = ctypes.c_int
                ctypes.set_errno(0)
                result = function(*arguments)
                actual_errno = ctypes.get_errno()
                observed['steps'].append({'call': call, 'args': arguments, 'source': source,
                                          'result': result, 'errno': actual_errno})
                if result == -1:
                    raise OSError(actual_errno, 'actual ' + call, fd)
                require(result == 0, 'DUPLEX_CONTROL_UNEXPECTED_ACTUAL_CLOSE_RESULT')
                try:
                    await asyncio.wait_for(asyncio.to_thread(service.relay_replies.wait, held), _PLAN['timeout'])
                except asyncio.TimeoutError:
                    raise
                except Exception as error:
                    observed['steps'].append({'actual_dispatcher_failure': failure(error)})
                    require(service.relay_replies.failure is error or held['failure'] is error,
                            'DUPLEX_CONTROL_ORIGINAL_DISPATCHER_FAILURE_REQUIRED')
                else:
                    raise RuntimeError('DUPLEX_CONTROL_HELD_FRAME_FABRICATED_WRITTEN_AFTER_EOF')
                require(not held['complete'] and held['result'] is None and not emitter.written,
                        'DUPLEX_CONTROL_ACTUAL_HELD_FRAME_WRITTEN_AFTER_CLOSE')
                observed['steps'].append({'held_after_eof': ticket_observation(held)})
            observed['actual_control_assertions_pass'] = True
    except BaseException as error:
        primary = error
        observed['actual_failure'] = failure(error)
        raise
    finally:
        observed['actual_output_retained'] = emitter.retained()
        observed['actual_native_output_queries'] = tuple(journal.output_observations[query_start:])
        observed['actual_dispatcher_failure'] = None if service.relay_replies.failure is None else failure(service.relay_replies.failure)
        try:
            observed['source_after'] = service.owner.source_lease.check()
            publish(_PLAN['result_path'], observed)
        except BaseException as error:
            if primary is None:
                raise
            primary.add_note('Actual duplex control publication failed: ' + repr(error))


def require_exercised():
    require(_PLAN is None or _USED, 'DUPLEX_CONTROL_SELECTED_ORIGINAL_REQUEST_NOT_ADMITTED')
