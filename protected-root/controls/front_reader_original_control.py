"""Genuine subject input pipe owned by the actual admitted front.

Selected original request bytes are data, never subject custody or permissions.
The actual pump retains every read/pwrite/fsync interval. Original supervisor
streams retain their original owners and original full closure obligations.
"""
import asyncio
import errno
import hashlib
import os
from pathlib import Path
import stat
import sys

_PLAN = None
_PLAN_RAW = None
_PAYLOAD = None
_SOURCE = None
_USED = False
_OBSERVED = None
_HELD = None


def require(value, reason):
    if not value:
        raise RuntimeError(reason)


def configure_from_source(path, output_directory):
    global _PLAN, _PLAN_RAW, _PAYLOAD, _SOURCE
    require(_PLAN is None, 'FRONT_READER_CONTROL_ALREADY_ENROLLED')
    approved = sys.modules.get('_worldline_approved_source_loader')
    require(approved is not None, 'FRONT_READER_ACTUAL_SOURCE_LEASE_REQUIRED')
    source = approved.current()
    source.check()
    from worldline.protected_startup import exact_json
    raw = source.file(str(path), ('DATA',))
    plan = exact_json(raw)
    require(type(plan) is dict and set(plan) == {
        'schema', 'role', 'request_id', 'request_source', 'request_sha256',
        'spool_path', 'result_path', 'timeout'}
        and plan['schema'] == 'worldline.original-custody-front-reader-control-v1',
        'FRONT_READER_COMPLETE_SELECTED_PLAN_REQUIRED')
    require(type(plan['role']) is str and plan['role']
        and type(plan['request_id']) in (str, int)
        and type(plan['timeout']) in (int, float) and plan['timeout'] > 0,
        'FRONT_READER_ORIGINAL_ROLE_REQUEST_TIMEOUT_REQUIRED')
    payload = source.file(plan['request_source'], ('DATA',))
    require(payload.endswith(b'\n')
        and hashlib.sha256(payload).hexdigest() == plan['request_sha256'],
        'FRONT_READER_EXACT_ORIGINAL_REQUEST_BYTES_REQUIRED')
    output = Path(output_directory)
    targets = [Path(plan[name]) for name in ('spool_path', 'result_path')]
    require(output.is_absolute() and len(set(targets)) == len(targets)
        and all(target.is_absolute() and target.parent == output for target in targets),
        'FRONT_READER_EXACT_PRECREATED_CASE_OUTPUT_REQUIRED')
    for parent in (*reversed(output.parents), output):
        info = parent.lstat()
        require(stat.S_ISDIR(info.st_mode) and info.st_uid == 0 and not info.st_mode & 0o022,
                'FRONT_READER_PROTECTED_OUTPUT_ANCESTRY_REQUIRED')
    info = output.lstat()
    require(not info.st_mode & 0o077 and all(not os.path.lexists(p) for p in targets),
            'FRONT_READER_EXCLUSIVE_PRIVATE_OUTPUT_REQUIRED')
    source.check()
    _PLAN, _PLAN_RAW, _PAYLOAD, _SOURCE = plan, raw, payload, source


def failure(error):
    return {'module': type(error).__module__, 'type': type(error).__qualname__,
            'message': str(error), 'errno': getattr(error, 'errno', None), 'repr': repr(error)}


async def write_original(owner, fd, raw, receipts):
    from worldline.custody_subject_capture import syscall
    position = 0
    loop = asyncio.get_running_loop()
    while position < len(raw):
        offered = raw[position:]
        sent, receipt = syscall(owner, 'write', {'fd': fd, 'raw': offered},
                                lambda: os.write(fd, offered))
        receipts.append(receipt)
        if sent is None:
            if receipt['errno'] not in (errno.EAGAIN, errno.EWOULDBLOCK):
                raise OSError(receipt['errno'], 'actual subject input write', fd)
            wake = loop.create_future()
            def ready():
                if not wake.done():
                    wake.set_result(None)
            loop.add_writer(fd, ready)
            try:
                await wake
            finally:
                loop.remove_writer(fd)
            continue
        require(type(sent) is int and sent > 0,
                'FRONT_READER_ACTUAL_INPUT_WRITE_PROGRESS_REQUIRED')
        position += sent


def close_owned_once(front, fd, key, observed):
    from worldline.custody_subject_capture import close_descriptor
    require(key not in _HELD['close_states'], 'FRONT_READER_DESCRIPTOR_CLOSE_ALREADY_ATTEMPTED')
    source = front.source_lease.check()
    state = {'fd': fd, 'status': 'UNKNOWN_AFTER_CLOSE_ATTEMPT', 'receipt': None}
    # Publish uncertainty before entering the close helper. It may itself raise.
    # The numeric fd is never retried after this point without a new identity route.
    _HELD['close_states'][key] = state
    close = close_descriptor(fd, source)
    observed['closes'].append(close)
    state['receipt'] = close
    if close['result'] == 0 and close['readback']['result'] == -1 and close['readback']['errno'] == 9:
        state['status'] = 'CLOSED_WITH_EBADF_READBACK'
        _HELD[key] = None
    return close


async def exercise(front, slot):
    global _USED, _OBSERVED, _HELD
    require(_PLAN is not None, 'FRONT_READER_NOT_SOURCE_ENROLLED')
    _SOURCE.check()
    document = slot.request.observation()
    if document['requestId'] != _PLAN['request_id']:
        return
    require(not _USED and document['rawRequest'] == _PAYLOAD.hex(),
            'FRONT_READER_ACTUAL_SELECTED_ORIGINAL_REQUEST_REQUIRED')
    _USED = True
    from worldline.custody_subject_capture import syscall, fd_identity, close_descriptor, actor_identity
    front.custody_journal.require_event(slot.owned.execution_ack)
    observed = {'schema': 'worldline.original-custody-front-reader-observations-v1',
        'selected_plan_raw': _PLAN_RAW, 'request': document, 'root_operation': slot.operation,
        'actual_execution_ack': slot.owned.execution_ack, 'actor': actor_identity(),
        'source_before': front.source_lease.check(), 'creation': [], 'writes': [],
        'closes': [], 'phase_acceptance': False, 'failure': None}
    _OBSERVED = observed
    read_fd = write_fd = spool_fd = None
    pump = None
    _HELD = {'front': front, 'slot': slot, 'pump': None, 'writer_fd': None,
             'unregistered_read_fd': None, 'unregistered_spool_fd': None, 'close_states': {}}
    try:
        descriptors, receipt = syscall(front, 'pipe2',
            {'flags': os.O_NONBLOCK | os.O_CLOEXEC},
            lambda: os.pipe2(os.O_NONBLOCK | os.O_CLOEXEC))
        observed['creation'].append(receipt)
        require(descriptors is not None, 'FRONT_READER_ACTUAL_DISTINCT_PIPE_REQUIRED')
        read_fd, write_fd = descriptors
        _HELD['writer_fd'] = write_fd
        _HELD['unregistered_read_fd'] = read_fd
        flags = os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC
        spool_fd, receipt = syscall(front, 'open',
            {'path': _PLAN['spool_path'], 'flags': flags, 'mode': 0o600},
            lambda: os.open(_PLAN['spool_path'], flags, 0o600))
        observed['creation'].append(receipt)
        require(spool_fd is not None, 'FRONT_READER_ACTUAL_EXCLUSIVE_SPOOL_REQUIRED')
        _HELD['unregistered_spool_fd'] = spool_fd
        observed['descriptor_before'] = fd_identity(read_fd)
        observed['spool_before'] = fd_identity(spool_fd)
        pump = front.register_subject_reader(slot.operation, _PLAN['role'], read_fd, spool_fd,
                                            root_operation=slot.operation)
        _HELD['pump'] = pump
        _HELD['unregistered_read_fd'] = _HELD['unregistered_spool_fd'] = None
        require(front.subject_pumps[_PLAN['role']] is pump and pump.owner is front,
                'FRONT_READER_ACTUAL_REGISTERED_OWNER_REQUIRED')
        await asyncio.wait_for(write_original(front, write_fd, _PAYLOAD, observed['writes']),
                               timeout=_PLAN['timeout'])
        close = close_owned_once(front, write_fd, 'writer_fd', observed)
        require(close['result'] == 0 and close['readback']['result'] == -1
                and close['readback']['errno'] == 9, 'FRONT_READER_INPUT_CLOSE_AMBIGUOUS')
        write_fd = None
        _HELD['writer_fd'] = None
        await asyncio.wait_for(asyncio.shield(pump.task), timeout=_PLAN['timeout'])
        require(pump.finished and pump.task.done() and pump.task.exception() is None,
                'FRONT_READER_ACTUAL_ACQUISITION_COMPLETION_REQUIRED')
        spool = pump.spool.snapshot()
        require(spool['raw'] == _PAYLOAD,
                'FRONT_READER_COMPLETE_ORIGINAL_BYTES_DURABLE_READBACK_REQUIRED')
        observed['actual_acquisitions'] = tuple(pump.acquisitions)
        observed['actual_spool_before_handoff'] = spool
        observed['source_after'] = front.source_lease.check()
        _SOURCE.check()
    except BaseException as error:
        observed['failure'] = failure(error)
        raise
    finally:
        primary = sys.exc_info()[1]
        if pump is None:
            # register_reader stores the real pump before start. A start error
            # does not return it, but ownership has already been registered.
            actual = front.subject_pumps.get(_PLAN['role'])
            if actual is not None and actual.owner is front and actual.fd == read_fd and actual.spool_fd == spool_fd:
                pump = actual
                _HELD['pump'] = actual
                _HELD['unregistered_read_fd'] = _HELD['unregistered_spool_fd'] = None
        try:
            # A registered reader/spool stays with the genuine subject owner. Its
            # actual native transfer/release/closed collector owns subsequent close.
            # Never cancel its task or fabricate custody when this callback fails.
            if write_fd is not None and 'writer_fd' not in _HELD['close_states']:
                close_owned_once(front, write_fd, 'writer_fd', observed)
            if pump is None:
                for key, fd in (('unregistered_read_fd', read_fd), ('unregistered_spool_fd', spool_fd)):
                    if fd is not None and key not in _HELD['close_states']:
                        close_owned_once(front, fd, key, observed)
        except BaseException as cleanup_error:
            observed.setdefault('secondary_failures', []).append(failure(cleanup_error))
            if primary is None:
                observed['failure'] = failure(cleanup_error)
                raise
            primary.add_note('Actual subject input cleanup failed; descriptor ownership deficits retained: ' + repr(cleanup_error))


def publish_observations():
    require(_OBSERVED is not None and _HELD is not None,
            'FRONT_READER_ACTUAL_PRODUCER_REQUIRED')
    _SOURCE.check()
    front, slot, pump = _HELD['front'], _HELD['slot'], _HELD['pump']
    observed = dict(_OBSERVED)
    observed['actual_subject_history'] = tuple(event for event in
        front.custody_journal.history(slot.operation)
        if event['subject_kind'] == 'DESCRIPTOR' and event['subject'] == _PLAN['role'])
    for event in observed['actual_subject_history']:
        front.custody_journal.require_event(event)
    if pump is not None:
        require(pump.owner is front and pump.subject.root_operation == slot.operation,
                'FRONT_READER_ACTUAL_CUSTODY_OWNER_CHANGED')
    # None means an actual unavailable object, never successful settlement.
    observed['actual_frozen'] = None if pump is None else pump.frozen
    observed['actual_ofd'] = None if pump is None else pump.ofd
    observed['actual_intake'] = None if pump is None else pump.intake
    observed['actual_release'] = None if pump is None else pump.released
    observed['actual_descriptor_still_owned'] = None if pump is None else pump.fd
    # A numeric fd after an ambiguous close is an UNKNOWN identity, never current
    # close authority. Keep that number and actual receipt in the separate states.
    observed['descriptor_close_states'] = dict(_HELD['close_states'])
    observed['actual_writer_still_owned'] = _HELD['writer_fd'] if 'writer_fd' not in _HELD['close_states'] else None
    observed['actual_unregistered_read_still_owned'] = _HELD['unregistered_read_fd'] if 'unregistered_read_fd' not in _HELD['close_states'] else None
    observed['actual_unregistered_spool_still_owned'] = _HELD['unregistered_spool_fd'] if 'unregistered_spool_fd' not in _HELD['close_states'] else None
    observed['source_at_publication'] = _SOURCE.check()
    from duplex_original_control import publish
    publish(_PLAN['result_path'], observed)
