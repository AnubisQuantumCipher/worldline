"""Real isolated front/worker/original-client controls, under an explicit lease.

Each case uses its own exclusive offline builder output. No supplied root phase,
peer credential, SQL delta, native status, ECHILD, OFD identity or source receipt
is used as authority. The actual original registered daemon handles every line.
"""
from __future__ import annotations
import sys
_approved = sys.modules.get('_worldline_approved_source_loader')
if _approved is None:
    raise SystemExit('CAMPAIGN_EARLY_SOURCE_LEASE_REQUIRED')
_lease = _approved.current()
_lease.check()
import argparse
import asyncio
import hashlib
import json
import os
from pathlib import Path
import socket
import stat
import subprocess


def require(value, reason):
    if not value:
        raise RuntimeError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode('utf-8')


def selected_json(path):
    raw = _lease.file(str(path), ('DATA',))
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'CAMPAIGN_DUPLICATE_JSON_KEY')
            result[key] = value
        return result
    value = json.loads(raw, object_pairs_hook=pairs)
    require(raw in (canonical(value), canonical(value) + b'\n'), 'CAMPAIGN_CANONICAL_INPUT_REQUIRED')
    return value


def output(path, value):
    from custody_runtime_controls_v35 import durable
    durable(path, canonical(value) + b'\n')


def private_directory(path):
    path = Path(path)
    for part in (*reversed(path.parents), path):
        info = part.lstat()
        require(stat.S_ISDIR(info.st_mode) and info.st_uid == 0 and not info.st_mode & 0o022,
                'CAMPAIGN_PROTECTED_ANCESTRY_REQUIRED')
    require(not info.st_mode & 0o077, 'CAMPAIGN_PRECREATED_PRIVATE_OUTPUT_REQUIRED')
    return path


class Campaign:
    def __init__(self, plan_path, case):
        require(os.geteuid() == 0 and sys.flags.isolated and sys.flags.no_site
                and sys.dont_write_bytecode, 'CAMPAIGN_ROOT_I_S_B_REQUIRED')
        self.plan_path = plan_path
        self.plan = selected_json(plan_path)
        require(set(self.plan) == {'schema', 'runtime', 'capture_source_root', 'cases', 'case_envelopes'},
                'CAMPAIGN_COMPLETE_PLAN_KEYSET')
        require(self.plan['schema'] == 'worldline.original-custody-live-campaign-v2', 'CAMPAIGN_SCHEMA')
        require(case in self.plan['cases'], 'CAMPAIGN_EXACT_SELECTED_CASE_REQUIRED')
        self.name = case
        _lease.directory_or_absent(str(Path(__file__).parent))
        sys.path.insert(0, str(Path(__file__).parent))
        from campaign_registry import bind
        self.spec = bind(self.plan)[case]
        require(set(self.spec) == {'startup_descriptor', 'observer', 'result_directory', 'timeout',
                'actions', 'original_assertions', 'required_kinds', 'required_controls',
                'required_subject_cases', 'capture_paths', 'duplex_control'}, 'CAMPAIGN_COMPLETE_CASE_SCHEMA')
        _lease.directory_or_absent(self.plan['runtime'])
        _lease.directory_or_absent(self.plan['capture_source_root'])
        _lease.directory_or_absent(str(Path(__file__).parent))
        sys.path[:0] = [self.plan['runtime'], self.plan['capture_source_root'], str(Path(__file__).parent)]
        self.out = private_directory(self.spec['result_directory'])
        self.original_descriptor = selected_json(self.spec['startup_descriptor'])
        root = Path(self.original_descriptor['paths']['authority_root'])
        require(root.parent == Path('/srv') and root.name.startswith('cosmogony-canonical-v1.control-'),
                'CAMPAIGN_DISPOSABLE_OFFLINE_FIXTURE_REQUIRED')
        require((root / 'initialized.json').is_file(), 'CAMPAIGN_ACTUAL_OFFLINE_CONSTRUCTION_REQUIRED')
        self.records = []
        self.source_owners = []
        self.coverage = None
        self.children = []
        self.tasks = []
        self.leases = []
        self.server = None
        self.router = None
        self.duplex_service = None

    def journal(self):
        return self.router.front.custody_journal

    async def live_slot(self, timeout):
        deadline = asyncio.get_running_loop().time() + timeout
        while asyncio.get_running_loop().time() < deadline:
            front = self.router.front
            slots = tuple(front.slots.values())
            candidates = [slot for slot in slots if slot.owned.worker_pidfd is not None
                          and slot.owned.worker_host_pid is not None]
            if len(candidates) == 1:
                slot = candidates[0]
                slot.owned.intact()
                return slot
            require(len(candidates) <= 1, 'CAMPAIGN_EXACT_ORIGINAL_WORKER_SELECTION_REQUIRED')
            await asyncio.sleep(0.001)
        raise RuntimeError('CAMPAIGN_ORIGINAL_WORKER_NOT_ESTABLISHED_BEFORE_DEADLINE')

    async def subject_service(self, timeout):
        deadline = asyncio.get_running_loop().time() + timeout
        while asyncio.get_running_loop().time() < deadline:
            front = self.router.front
            offer = getattr(front, 'current_offer', None)
            if offer is not None and getattr(offer, 'ack_event', None) is not None:
                front.custody_journal.require_event(offer.ack_event)
                return offer.subject_service
            await asyncio.sleep(0.001)
        raise RuntimeError('CAMPAIGN_NATIVE_CUSTODY_ACK_NOT_ESTABLISHED_BEFORE_DEADLINE')

    async def client(self, action):
        selected = selected_json(action['request'])
        require(selected['endpoint'] == self.original_descriptor['endpoint']['path'],
                'CAMPAIGN_ORIGINAL_ENDPOINT_SPLIT')
        require(selected['uid'] == self.original_descriptor['endpoint']['requester_uid']
                and selected['gid'] == self.original_descriptor['endpoint']['requester_gid'],
                'CAMPAIGN_ORIGINAL_ACTOR_DOMAIN_CHANGED')
        entry = str(Path(__file__).with_name('original_client.py'))
        owner_path = action['request'] + '.source-owner.json'
        owner = selected_json(owner_path)
        require(owner['schema'] == 'worldline.fixed-original-client-source-owner-v1'
                and owner['request'] == action['request'] and owner['entry'] == entry
                and owner['descriptor'] == self.spec['startup_descriptor']
                and owner['timeout'] == action['timeout'],
                'CAMPAIGN_FIXED_SOURCE_OWNER_ORIGINAL_BINDING_REQUIRED')
        owner_output = private_directory(owner['retention_directory'])
        require(not any(owner_output.iterdir()), 'CAMPAIGN_SOURCE_OWNER_OUTPUT_ALREADY_USED')
        _lease.file(entry, ('ENTRY',))
        _lease.file(action['early_envelope'], ('DATA',))
        command = [_lease.interpreter, '-I', '-S', '-B', _lease.helper_path,
                   '--bootstrap-envelope', action['early_envelope'], '--entry', entry,
                   '--request', action['request']]
        index = len(self.children)
        stdout = self.out / ('client-' + str(index) + '.stdout')
        stderr = self.out / ('client-' + str(index) + '.stderr')
        with stdout.open('xb') as out, stderr.open('xb') as err:
            child = subprocess.Popen(command, env=action['environment'], stdout=out, stderr=err)
            self.children.append(child)
            ownership = {'action': action, 'argv': command, 'pid': child.pid, 'actual_wait': None,
                         'owner_birth': None, 'stdout': str(stdout), 'stderr': str(stderr),
                         'source_owner_selection': owner_path, 'source_owner_retention': str(owner_output),
                         'actual_actor_custody': 'INNER_ARCHIVE_AND_MAIN_COLLECTOR_REQUIRED'}
            self.source_owners.append(ownership)
            ownership['owner_birth'] = _approved.process_facts(child.pid)
            wait = await asyncio.to_thread(child.wait, timeout=action['timeout'])
            ownership['actual_wait'] = wait
            out.flush(); err.flush(); os.fsync(out.fileno()); os.fsync(err.fileno())
        row = {**ownership, 'stdout_sha256': sha(stdout.read_bytes()), 'stderr_sha256': sha(stderr.read_bytes()),
               'source_owner_archive_sha256': sha((owner_output / 'source-owner.archive').read_bytes())}
        row['source_owner_retained_files'] = [
            {'path': str(path), 'sha256': sha(path.read_bytes()),
             'stat': {'device': path.stat(follow_symlinks=False).st_dev,
                      'inode': path.stat(follow_symlinks=False).st_ino,
                      'mode': path.stat(follow_symlinks=False).st_mode,
                      'uid': path.stat(follow_symlinks=False).st_uid,
                      'gid': path.stat(follow_symlinks=False).st_gid,
                     'size': path.stat(follow_symlinks=False).st_size},
             'bytes': path.stat(follow_symlinks=False).st_size,
             'mode': stat.S_IMODE(path.stat(follow_symlinks=False).st_mode)}
            for path in sorted(owner_output.iterdir())]
        self.records.append(row)
        footer_marker = b'SOURCE_OWNER_FINAL_CLOSE '
        owner_stderr = stderr.read_bytes()
        marker = owner_stderr.rfind(footer_marker)
        require(marker >= 0 and owner_stderr[marker:].count(footer_marker) == 1,
                'CAMPAIGN_ACTUAL_SOURCE_OWNER_FINAL_CLOSE_MISSING')
        row['source_owner_final_close'] = json.loads(owner_stderr[marker + len(footer_marker):].split(b'\n', 1)[0])
        ownership['source_owner_final_close'] = row['source_owner_final_close']
        if 'expected_error' in action:
            require(wait == 1 and ('RuntimeError: ' + action['expected_error']).encode() in stderr.read_bytes(),
                    'CAMPAIGN_ORIGINAL_TRANSPORT_EOF_REFUSAL_CHANGED')
        else:
            require(wait == 0, 'CAMPAIGN_ACTUAL_ORIGINAL_CLIENT_FAILED')
        return row

    async def abandon_request(self, action):
        service = await self.subject_service(action['timeout'])
        deadline = asyncio.get_running_loop().time() + action['timeout']
        while asyncio.get_running_loop().time() < deadline:
            for identifier, escrow in tuple(service.escrows.items()):
                if escrow.peer.observation()['requestId'] != action['request_id'] or escrow.subject is None:
                    continue
                event = escrow.subject.last_event
                if event is None or event['kind'] != 'REQUEST_TRANSFER_INTENT':
                    continue
                self.journal().require_event(event)
                result = service.abandon_request(identifier)
                self.records.append({'action': action, 'actual_observation_id': identifier,
                    'actual_intent': event, 'actual_event': result})
                return
            await asyncio.sleep(0)
        raise RuntimeError('CAMPAIGN_ACTUAL_REQUEST_TRANSFER_WINDOW_NOT_OBSERVED')

    async def abandon_reader(self, action):
        service = await self.subject_service(action['timeout'])
        transfer = asyncio.create_task(service.transfer_readers())
        self.tasks.append(transfer)
        deadline = asyncio.get_running_loop().time() + action['timeout']
        while asyncio.get_running_loop().time() < deadline:
            pump = service.owner.subject_pumps[action['role']]
            event = pump.subject.last_event
            if event is not None and event['kind'] == 'DRAIN_OFD_EVIDENCE':
                self.journal().require_event(event)
                result = service.abandon_reader(action['role'])
                self.records.append({'action': action, 'actual_ofd_event': event, 'actual_event': result})
                return
            if transfer.done():
                await transfer
                raise RuntimeError('CAMPAIGN_ACTUAL_DRAIN_TRANSFER_WINDOW_ALREADY_CLOSED')
            await asyncio.sleep(0)
        raise RuntimeError('CAMPAIGN_ACTUAL_DRAIN_TRANSFER_WINDOW_NOT_OBSERVED')
    async def fault(self, action):
        target = action['target']
        require(target in ('front', 'worker'), 'CAMPAIGN_ORIGINAL_PROCESS_ROLE_REQUIRED')
        slot = None if target == 'front' else await self.live_slot(action['timeout'])
        pid = os.getpid() if slot is None else slot.owned.worker_host_pid
        injector = action['injector']
        raw = _lease.file(injector, ('DATA',))
        require(sha(raw) == action['injector_sha256'], 'CAMPAIGN_REAL_SYSCALL_INJECTOR_CHANGED')
        path = Path(action['path'])
        root = Path(self.original_descriptor['paths']['authority_root'])
        require(path.is_relative_to(root), 'CAMPAIGN_FAULT_MUST_TARGET_DISPOSABLE_ARTIFACT')
        pidfd = os.pidfd_open(pid) if slot is None else os.dup(slot.owned.worker_pidfd)
        try:
            command = [injector, str(pid), str(pidfd), action['syscall'],
                       str(path), str(action['occurrence']), action['effect']]
            index = len(self.children)
            stdout = self.out / ('fault-' + str(index) + '.stdout')
            stderr = self.out / ('fault-' + str(index) + '.stderr')
            with stdout.open('xb') as out, stderr.open('xb') as err:
                child = subprocess.Popen(command, env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'},
                                         pass_fds=(pidfd,), stdout=out, stderr=err)
                self.children.append(child)
                wait = await asyncio.to_thread(child.wait, timeout=action['timeout'])
                out.flush(); err.flush(); os.fsync(out.fileno()); os.fsync(err.fileno())
            self.records.append({'action': action, 'original_operation': None if slot is None else slot.operation,
                'argv': command, 'pid': child.pid, 'actual_wait': wait,
                'stdout_sha256': sha(stdout.read_bytes()), 'stderr_sha256': sha(stderr.read_bytes())})
            require(wait == 0 and b'ACTUAL_SYSCALL_FAULT_APPLIED' in stderr.read_bytes(),
                    'CAMPAIGN_GENUINE_FILE_IO_OR_CRASH_INJECTION_NOT_EXERCISED')
        finally:
            os.close(pidfd)

    def retry(self, action):
        journal = self.journal()
        matches = [event for event in journal.history() if event['kind'] == action['event_kind']
                   and event['subject_kind'] == action['subject_kind'] and event['actor'] == 'FRONT']
        require(matches, 'CAMPAIGN_ORIGINAL_COMMITTED_RETRY_EVENT_REQUIRED')
        event = matches[-1]
        from worldline.root_worker_codec import raw_archive
        before = raw_archive(journal.history())
        result = journal.append(event['operation'], event['kind'], event['record'], actor=event['actor'],
            subject_kind=event['subject_kind'], subject=event['subject'],
            evidence={'retained_record': event['retained_record']})
        require(raw_archive(result) == raw_archive(event) and raw_archive(journal.history()) == before,
                'CAMPAIGN_EXACT_RETRY_MUST_NOT_APPEND_OR_CHANGE_BYTES')
        observer = journal._control_capture
        require(observer.pending['expected_status'] == 1, 'CAMPAIGN_ORIGINAL_NATIVE_RETRY_NOT_REPLAY')
        observer.label('retry')
        self.records.append({'action': action, 'original_event': event['event_id'], 'native_replay': True})

    def stale(self, action):
        # Keep the candidate from a genuine rolled-back original append. Only
        # substitute a freshly captured actual full ledger as the CAS comparator.
        # Do not alter the candidate's raw owner/evidence/source/primitive joins.
        journal = self.journal()
        from worldline.root_worker_codec import scoped_restore_archive, scoped_archive
        from worldline.custody_mutation_kernel import decide_journal, mutation_input
        from worldline.custody_context_kernel import capture_context_input
        actual = _lease.file(action['original_failed_input'], ('DATA',))
        original = scoped_restore_archive(actual)
        candidate = original['candidate']
        require(not any(event['operation'] == candidate['operation'] and event['kind'] == candidate['kind']
                        and event['retained_record'] == candidate['record'] for event in journal.history()),
                'CAMPAIGN_STALE_CANDIDATE_MUST_BE_REAL_UNCOMMITTED_APPEND')
        db = journal.connect()
        try:
            db.execute('BEGIN')
            before, load = journal._accepted_capture(db)
            require(scoped_archive(original['before']) != before, 'CAMPAIGN_CAS_HEAD_MUST_ACTUALLY_CHANGE')
            inputs = mutation_input(before, candidate['operation'], candidate['kind'], candidate['actor'],
                                    candidate['subject_kind'], candidate['subject'], candidate['record'])
            context = capture_context_input(journal, inputs)
            decision = decide_journal(journal, inputs)
            require(decision.status not in (0, 1) and decision.delta is None,
                    'CAMPAIGN_ACTUAL_STALE_CAS_NOT_REFUSED')
            journal._control_capture.observe(candidate['operation'], candidate['kind'], inputs, decision,
                                            before, before_load=load, context=context)
            journal._control_capture.label('cas-stale')
            db.rollback()
        finally:
            db.close()
        self.records.append({'action': action, 'native_status': decision.status,
                             'native_position': decision.position, 'original_input_sha256': sha(actual)})

    async def original_assertions(self):
        from assertion_registry import require_campaign, validate
        assertions = [selected_json(record['spec']) for record in self.spec['original_assertions']]
        if self.name == 'retained-original-startup-resource-assertions':
            require_campaign(assertions, lambda path: _lease.file(path, ('SOURCE',)))
        else:
            for assertion in assertions:
                validate(assertion, _lease.file(assertion['source'], ('SOURCE',)))
        for record in self.spec['original_assertions']:
            entry = str(Path(__file__).with_name('original_assertion_entry.py'))
            _lease.file(entry, ('SOURCE', 'ENTRY'))
            assertion = selected_json(record['spec'])
            source = _lease.file(assertion['source'], ('SOURCE',))
            require(sha(source) == assertion['sha256'], 'CAMPAIGN_ORIGINAL_ASSERTION_PREIMAGE_CHANGED')
            command = [_lease.interpreter, '-I', '-S', '-B', _lease.helper_path,
                '--bootstrap-envelope', record['early_envelope'], '--entry', entry,
                '--spec', record['spec']]
            _lease.file(record['early_envelope'], ('DATA',))
            index = len(self.children)
            stdout = self.out / ('assertions-' + str(index) + '.stdout')
            stderr = self.out / ('assertions-' + str(index) + '.stderr')
            with stdout.open('xb') as out, stderr.open('xb') as err:
                child = subprocess.Popen(command, env={'PATH': '/usr/bin:/bin', 'HOME': str(self.out),
                    'TMPDIR': str(self.out), 'LC_ALL': 'C'}, stdout=out, stderr=err)
                self.children.append(child)
                wait = await asyncio.to_thread(child.wait, timeout=record['timeout'])
                out.flush(); err.flush(); os.fsync(out.fileno()); os.fsync(err.fileno())
            require(wait == 0, 'CAMPAIGN_COMPLETE_ORIGINAL_ASSERTIONS_FAILED')
            self.records.append({'action': 'original-assertions', 'actual_wait': wait,
                'original_command': command, 'stdout_sha256': sha(stdout.read_bytes()),
                'stderr_sha256': sha(stderr.read_bytes())})
            self.records.append({'original_assertions': assertion, 'original_command': command})

    async def run(self):
        from worldline.custody_control_registration import register_from_source, source_observers, publish_source_observers
        register_from_source(self.spec['observer'])
        from worldline.protected_startup import StartupLease
        from worldline.protected_root_worker import RootWorkerFront
        from worldline.daemon import WorldlineDaemon, _MAX_REQUEST_BYTES
        from worldline.status import StatusPublisher
        from worldline.root_worker_endpoint_router import RootEndpointRouter
        lease = StartupLease(self.spec['startup_descriptor'])
        self.leases.append(lease)
        lease.construct()
        lease.require_front_startup()
        principal = lease.canonical_operation_principal
        daemon = WorldlineDaemon(lease.controller.paths, lease.store,
                                 StatusPublisher(lease.controller.paths, lease.store))
        lease.controller.register(daemon)
        front = RootWorkerFront(principal, lease.spec['root_worker']['owner_plan'])
        front.daemon = daemon
        if self.spec['duplex_control'] is not None:
            from campaign_registry import DUPLEX_CASES
            control = selected_json(self.spec['duplex_control'])
            require(str(Path(front.plan['entry']).with_suffix('.duplex.json')) == self.spec['duplex_control']
                    and control['mode'] == DUPLEX_CASES[self.name]
                    and control['timeout'] == self.spec['timeout'],
                    'CAMPAIGN_ACTUAL_WORKER_DUPLEX_ENTRY_MODE_TIMEOUT_BINDING_REQUIRED')
        self.router = RootEndpointRouter(front, daemon)
        path = Path(lease.spec['endpoint']['path'])
        require(not os.path.lexists(path), 'CAMPAIGN_ORIGINAL_ENDPOINT_MUST_BE_EXCLUSIVE')
        self.server = await asyncio.start_unix_server(daemon._handle_client, path=str(path),
                                                    limit=_MAX_REQUEST_BYTES + 1)
        os.chown(path, 0, lease.spec['endpoint']['requester_gid']); os.chmod(path, 0o660)
        named = path.stat(); principal.endpoint_identity = (named.st_dev, named.st_ino)
        lease.intact(); lease.loaded()
        try:
            for action in self.spec['actions']:
                kind = action['kind']
                if kind in ('client', 'fault'):
                    task = asyncio.create_task(getattr(self, kind)(action))
                    self.tasks.append(task)
                    if action['wait']: await task
                elif kind == 'wait-clients':
                    await asyncio.gather(*self.tasks)
                elif kind == 'wait-custody-ack':
                    service = await self.subject_service(action['timeout'])
                    if self.spec['duplex_control'] is not None:
                        require(self.duplex_service is None or self.duplex_service is service,
                                'CAMPAIGN_ACTUAL_DUPLEX_SERVICE_CHANGED')
                        self.duplex_service = service
                    self.records.append({'action': action, 'actual_service_class': type(service).__qualname__})
                elif kind == 'abandon-request':
                    await self.abandon_request(action)
                elif kind == 'abandon-reader':
                    await self.abandon_reader(action)
                elif kind == 'transfer-readers':
                    service = await self.subject_service(action['timeout'])
                    events = await service.transfer_readers()
                    self.records.append({'action': action, 'actual_intake_events':
                        {role: event['event_id'] for role, event in events.items()}})
                elif kind == 'close-live-channel':
                    service = await self.subject_service(action['timeout'])
                    fd = service.channel.fileno()
                    import ctypes
                    libc = ctypes.CDLL(None, use_errno=True)
                    shutdown = libc.shutdown
                    shutdown.argtypes = (ctypes.c_int, ctypes.c_int)
                    shutdown.restype = ctypes.c_int
                    source = service.owner.source_lease.check()
                    ctypes.set_errno(0)
                    result = shutdown(fd, socket.SHUT_RDWR)
                    actual_errno = ctypes.get_errno()
                    receipt = {'action': action, 'actual_shutdown_descriptor': fd,
                        'syscall': {'call': 'shutdown', 'args': [fd, socket.SHUT_RDWR],
                            'source': source, 'result': result, 'errno': actual_errno}}
                    self.records.append(receipt)
                    receipt['source_after'] = service.owner.source_lease.check()
                    if result == -1:
                        raise OSError(actual_errno, 'actual shutdown', fd)
                    require(result == 0, 'CAMPAIGN_UNEXPECTED_ACTUAL_SHUTDOWN_RESULT')
                elif kind == 'retry': self.retry(action)
                elif kind == 'cas-stale': self.stale(action)
                elif kind == 'wait-root-closure':
                    await asyncio.wait_for(asyncio.gather(*tuple(self.router.front.collectors.values())),
                                           timeout=action['timeout'])
                else:
                    raise RuntimeError('CAMPAIGN_UNKNOWN_GENUINE_ACTION_' + kind)
            await asyncio.gather(*self.tasks)
            await self.original_assertions()
            from observed_controls import assert_recorders
            assert_recorders(source_observers(), (), (), ())
        finally:
            self.server.close(); await self.server.wait_closed()
            # Authentic unfinished worker/root escrows and their descriptor
            # owners are retained; endpoint EOF never fabricates settlement.
            primary = sys.exc_info()[1]
            errors = []
            try:
                if self.spec['duplex_control'] is not None:
                    from duplex_original_control import failure, publish, validate_front_observations
                    require(self.duplex_service is not None, 'CAMPAIGN_ACTUAL_DUPLEX_FRONT_SERVICE_REQUIRED')
                    endpoint = self.duplex_service.relay_endpoint
                    require(endpoint is not None, 'CAMPAIGN_ACTUAL_DUPLEX_FRONT_RELAY_REQUIRED')
                    if control['mode'] != 'gap-write':
                        deadline = asyncio.get_running_loop().time() + self.spec['timeout']
                        while endpoint.failure is None and asyncio.get_running_loop().time() < deadline:
                            await asyncio.sleep(0.001)
                    escrows = [escrow for escrow in self.duplex_service.escrows.values()
                               if escrow.original is not None
                               and escrow.original['original_request']['requestId'] == control['request_id']]
                    require(len(escrows) == 1 and escrows[0].intake is not None,
                            'CAMPAIGN_ACTUAL_DUPLEX_AUTHENTIC_REQUEST_ESCROW_REQUIRED')
                    escrow = escrows[0]
                    archive = self.out / 'duplex-front-output.archive'
                    observed = {'schema': 'worldline.original-custody-live-duplex-front-outputs-v1',
                        'case': self.name, 'original_plan': self.plan_path,
                        'request': escrow.original['original_request'],
                        'actual_original': escrow.original,
                        'actual_intake': escrow.intake,
                        'actual_native_output_queries': tuple(self.journal().output_observations),
                        'actual_relay_records': tuple(endpoint.records),
                        'actual_relay_receives': tuple(endpoint.relay.received),
                        'actual_relay_failure': None if endpoint.failure is None else failure(endpoint.failure),
                        'source': _lease.check(), 'phase_acceptance': False}
                    publish(archive, observed)
                    validate_front_observations(observed, control)
                    self.records.append({'duplex_front_outputs': str(archive),
                        'sha256': sha(archive.read_bytes())})
            except BaseException as error:
                errors.append(error)
            try:
                publish_source_observers()
            except BaseException as error:
                errors.append(error)
            if errors:
                if primary is None:
                    raise errors[0]
                for error in errors:
                    primary.add_note('Actual control publication failed: ' + repr(error))
        from capture_coverage import check
        self.coverage = check(self.spec['capture_paths'], self.spec['required_kinds'],
                              self.spec['required_controls'], self.spec['required_subject_cases'])
        return self.records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', required=True)
    parser.add_argument('--case', required=True)
    args = parser.parse_args()
    campaign = Campaign(args.plan, args.case)
    failure = None
    try:
        asyncio.run(asyncio.wait_for(campaign.run(), timeout=campaign.spec['timeout']))
    except BaseException as error:
        failure = {'type': type(error).__name__, 'reason': str(error)}
        raise
    finally:
        live = [child.pid for child in campaign.children if child.returncode is None]
        output(campaign.out / 'result.json', {'schema': 'worldline.original-custody-live-case-result-v1',
            'case': campaign.name, 'original_plan': campaign.plan_path, 'records': campaign.records,
            'failure': failure, 'still_owned_child_pids': live, 'source': _lease.check(),
            'actual_produced_coverage': campaign.coverage,
            'source_owner_custody': campaign.source_owners,
            'source_owner_outer_collector_custody': 'AUTHENTIC_MAIN_FRAMED_PRODUCER_REQUIRED',
            'native_campaign_coverage_requires_exporter': True, 'phase_acceptance': False})


if __name__ == '__main__':
    main()
