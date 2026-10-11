"""Existing-only original-owner observations for isolated admission controls.

This is not a Lease or principal. No authority/state/config/lock/journal is
created, no startup constructor is called, and observations convey no permission.
The caller releases this actual held-FD scope before invoking a denied constructor
so an artificial second-holder conflict cannot hide the original tested denial.
"""
from __future__ import annotations
import sys
_approved = sys.modules.get('_worldline_approved_source_loader')
if _approved is None:
    raise SystemExit('OFFLINE_GUARD_EARLY_SOURCE_REQUIRED')
_lease = _approved.current()
_lease.check()
import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat


def require(value, reason):
    if not value:
        raise RuntimeError(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


def protected(path, directory=False):
    path = Path(path)
    require(path.is_absolute(), 'OFFLINE_GUARD_ABSOLUTE_ORIGINAL_PATH_REQUIRED')
    for ancestor in reversed((path, *path.parents)):
        info = ancestor.lstat()
        require(not stat.S_ISLNK(info.st_mode) and info.st_uid == 0 and not info.st_mode & 0o022,
                'OFFLINE_GUARD_UNPROTECTED_ORIGINAL_PATH')
        if ancestor != path or directory:
            require(stat.S_ISDIR(info.st_mode), 'OFFLINE_GUARD_ORIGINAL_DIRECTORY_REQUIRED')
        else:
            require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1,
                    'OFFLINE_GUARD_ORIGINAL_PRIVATE_INODE_REQUIRED')
    return path


def observed_inode(info):
    return {'device': info.st_dev, 'inode': info.st_ino, 'mode': info.st_mode,
        'uid': info.st_uid, 'gid': info.st_gid, 'links': info.st_nlink,
        'size': info.st_size, 'mtime_ns': info.st_mtime_ns, 'ctime_ns': info.st_ctime_ns}


class OriginalOwnerGuard:
    def __init__(self, descriptor_path):
        self.descriptor_path = protected(descriptor_path)
        self.descriptor_raw = _lease.file(str(self.descriptor_path), ('DATA',))
        self.spec = json.loads(self.descriptor_raw)
        self.root = protected(self.spec['paths']['authority_root'], True)
        require(self.root.parent == Path('/srv')
                and self.root.name.startswith('cosmogony-canonical-v1.control-'),
                'OFFLINE_GUARD_EXCLUSIVE_DISPOSABLE_ORIGINAL_FIXTURE_REQUIRED')
        self.genesis_raw = _lease.file(self.spec['genesis'], ('DATA',))
        self.genesis = json.loads(self.genesis_raw)
        require(self.genesis['installation_id'] == self.spec['installation_id'],
                'OFFLINE_GUARD_ACTUAL_OWNER_BINDING_CHANGED')
        marker_path = self.root / 'initialized.json'
        marker_raw = _lease.file(str(marker_path), ('DATA',))
        marker = json.loads(marker_raw)
        require(marker['schema'] == 'worldline.original-custody-fixture-created-v2'
                and marker['stage'] == 'initialize', 'OFFLINE_GUARD_ORIGINAL_OWNER_CREATION_EVIDENCE_REQUIRED')
        original_plan = bytes.fromhex(marker['original_plan_hex'])
        require(hashlib.sha256(original_plan).hexdigest() == marker['plan_sha256'],
                'OFFLINE_GUARD_CREATION_PLAN_PREIMAGE_CHANGED')
        plan = json.loads(original_plan)
        from construction_registry import bind
        require(plan['schema'] == 'worldline.original-custody-fixture-construction-v2'
                and [row['original_action'] for row in marker['actions']] ==
                    [action for action in bind(plan['owner_inputs']) if action['kind'] != 'owner-entry'],
                'OFFLINE_GUARD_COMMITTED_ORIGINAL_CREATOR_TOPOLOGY_CHANGED')
        require(plan['root'] == str(self.root)
                and plan['operator_authorization'] == 'EXCLUSIVE OFFLINE DISPOSABLE ' + str(self.root),
                'OFFLINE_GUARD_ACTUAL_DISPOSABLE_OPERATOR_SCOPE_CHANGED')
        guard = json.loads(_lease.file(plan['guard'], ('DATA',)))
        require(guard['root'] == str(self.root) and guard['plan_sha256'] == marker['plan_sha256']
                and Path('/proc/self/cgroup').read_text() == guard['cgroup'],
                'OFFLINE_GUARD_CURRENT_ORIGINAL_OPERATOR_CGROUP_CHANGED')
        stores = [row['result'] for row in marker['actions']
                  if row['original_action']['kind'] == 'startup-genesis']
        require(len(stores) == 1, 'OFFLINE_GUARD_EXACT_ORIGINAL_INITIAL_STORE_REQUIRED')
        self.store_initial_snapshot = stores[0]['store_initial_snapshot']
        self.store_initial_snapshot_raw = canonical(self.store_initial_snapshot)
        self.store_initial_head = hashlib.sha256(self.store_initial_snapshot_raw).hexdigest()
        require(stores[0]['store_initial_head'] == self.store_initial_head
                == self.genesis['store']['initial_head'],
                'OFFLINE_GUARD_GENUINE_RETAINED_INITIAL_STORE_CHANGED')
        self.issuer_state = self.root / 'authority/issuer/state'
        self.fds = {}
        self.namespaces = {}
        self.pidfd = None

    def __enter__(self):
        state = Path(self.spec['paths']['state'])
        actuator = protected(self.root / 'canonical/actuator', True)
        transactions = self.spec['actuator_transactions']
        require(len(set(transactions)) == len(transactions) and all(type(name) is str
                and name and '/' not in name and name not in ('.', '..') for name in transactions),
                'OFFLINE_GUARD_FULL_ORIGINAL_ACTUATOR_ROSTER_REQUIRED')
        require(sorted(path.name for path in actuator.iterdir()) == sorted(transactions),
                'OFFLINE_GUARD_ORIGINAL_ACTUATOR_DOMAIN_CHANGED')
        paths = [state / 'worldline-store.lock', self.root / 'authority/gate/state/gate.lock',
            self.root / 'authority/state/broker.lock',
            *(actuator / name / 'service.lock' for name in transactions),
            self.issuer_state / 'issuer.lock', self.root / 'authority/universe/root/universe.lock']
        if 'root_worker' in self.spec:
            plan_raw = _lease.file(self.spec['root_worker']['owner_plan'], ('DATA',))
            plan = json.loads(plan_raw)
            require(plan['installation'] == self.spec['installation_id'],
                    'OFFLINE_GUARD_ORIGINAL_CUSTODY_PLAN_INSTALLATION_CHANGED')
            paths.extend((self.root / 'authority/resource/run-state-v1/instance.lock',
                self.root / 'authority/resource/run-state-v1/launch.lock',
                self.root / 'authority/resource/run-scoped-state-v1/instance.lock',
                self.root / 'authority/resource/run-scoped-state-v1/observations.lock',
                Path(plan['handoff_journal'] + '.lock')))
        require(len(paths) == len(set(paths)), 'OFFLINE_GUARD_ORIGINAL_LOCK_ROSTER_ALIAS')
        try:
            for path in paths:
                protected(path)
                fd = os.open(path, os.O_RDWR | os.O_NOFOLLOW | os.O_CLOEXEC)
                self.fds[path] = fd
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.pidfd = os.pidfd_open(os.getpid(), 0)
            for path in Path('/proc/self/ns').iterdir():
                self.namespaces[path.name] = os.open(path, os.O_RDONLY | os.O_CLOEXEC)
            return self
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def readfacts(self):
        require(self.fds and self.pidfd is not None, 'OFFLINE_GUARD_ACTUAL_HELD_SCOPE_REQUIRED')
        held = []
        for path, fd in self.fds.items():
            named = protected(path).stat()
            inode = os.fstat(fd)
            require((named.st_dev, named.st_ino) == (inode.st_dev, inode.st_ino),
                    'OFFLINE_GUARD_ACTUAL_HELD_LOCK_REPLACED')
            held.append({'path': os.fsencode(path), 'fd': fd,
                'named': observed_inode(named), 'held': observed_inode(inode),
                'fdinfo': Path('/proc/self/fdinfo/' + str(fd)).read_bytes(),
                'raw': os.pread(fd, inode.st_size, 0),
                'descriptor_link': os.fsencode(os.readlink('/proc/self/fd/' + str(fd)))})
        caller = {'pid': os.getpid(), 'ppid': os.getppid(), 'resuid': os.getresuid(),
            'resgid': os.getresgid(), 'groups': tuple(os.getgroups()),
            'pidfd': self.pidfd, 'pidfd_info': Path('/proc/self/fdinfo/' + str(self.pidfd)).read_bytes(),
            'executable': os.fsencode(os.readlink('/proc/self/exe')),
            'proc': {name: Path('/proc/self/' + name).read_bytes()
                     for name in ('stat', 'status', 'cgroup', 'maps', 'mountinfo')},
            'namespaces': {name: {'fd': fd, 'inode': observed_inode(os.fstat(fd)),
                'link': os.fsencode(os.readlink('/proc/self/ns/' + name))}
                for name, fd in self.namespaces.items()}}
        from worldline.root_worker_current_state import _database
        databases = [path for path in self.spec['provisioned_state']
                     if path.endswith(('.db', '.sqlite', '.sqlite3'))]
        if self.spec['bootstrap_ledger'] not in databases:
            databases.append(self.spec['bootstrap_ledger'])
        logical = {}
        for path in databases:
            try:
                logical[os.fsencode(path)] = {'snapshot': _database(Path(path)), 'error': None}
            except BaseException as error:
                logical[os.fsencode(path)] = {'snapshot': None, 'error': {
                    'type': type(error).__qualname__, 'module': type(error).__module__,
                    'message': str(error), 'args': tuple(error.args), 'errno': getattr(error, 'errno', None)}}
        _lease.check()
        return {'spec': self.spec, 'genesis': self.genesis, 'descriptor_path': self.descriptor_path,
            'descriptor_raw': self.descriptor_raw, 'genesis_raw': self.genesis_raw,
            'issuer_state': self.issuer_state, 'source_lease': _lease, 'held_fds': dict(self.fds),
            'held_lock_sources': held, 'store_initial_snapshot': self.store_initial_snapshot,
            'store_initial_snapshot_raw': self.store_initial_snapshot_raw,
            'store_initial_head': self.store_initial_head, 'caller': caller, 'logical_sql': logical}

    def admission_profiles(self, initial_envelopes=None):
        from worldline.custody_startup_capture import capture_admission_profiles_from_sources
        return capture_admission_profiles_from_sources(spec=self.spec, genesis=self.genesis,
            descriptor_path=self.descriptor_path, issuer_state=self.issuer_state,
            source_lease=_lease, store_initial_snapshot=self.store_initial_snapshot,
            store_initial_snapshot_raw=self.store_initial_snapshot_raw,
            store_initial_head=self.store_initial_head, initial_envelopes=initial_envelopes)

    def __exit__(self, kind, error, traceback):
        for fd in reversed(tuple(self.fds.values())):
            os.close(fd)
        self.fds.clear()
        for fd in self.namespaces.values():
            os.close(fd)
        self.namespaces.clear()
        if self.pidfd is not None:
            os.close(self.pidfd)
            self.pidfd = None
