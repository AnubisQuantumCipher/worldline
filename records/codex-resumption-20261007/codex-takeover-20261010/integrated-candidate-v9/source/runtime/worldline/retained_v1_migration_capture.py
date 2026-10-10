"""Read-only retained-v1 capture using the actual original schema/HMAC loader.

This produces full native operands. It neither judges operation closure nor
creates a v2 owner, supplies a native verdict, migrates, or grants startup.
"""
from dataclasses import dataclass
import fcntl
import os
from pathlib import Path
import sys
from .protected_startup import require, private_bytes, protected, exact_json, digest
from .root_worker_custody import identity
from .root_worker_journal import RetainedV1Reader
from .root_worker_current_state import _database
from .root_worker_codec import archive

def shared_identity(fd, path):
    named = protected(path); held = os.fstat(fd)
    require((named.st_dev, named.st_ino) == (held.st_dev, held.st_ino),
            'RETAINED_V1_SHARED_LOCK_REPLACED')
    fcntl.flock(fd, fcntl.LOCK_SH | fcntl.LOCK_NB)
    return identity(fd)

@dataclass(frozen=True)
class RetainedContext:
    descriptor_path: str
    descriptor_sha256: str
    plan_path: str
    plan_sha256: str
    genesis_path: str
    genesis_sha256: str
    journal_path: str
    journal_sha256: str
    head_event: str
    issuer_key_sha256: str
    installation: str

@dataclass(frozen=True)
class RetainedV1Capture:
    selected: RetainedContext
    descriptor_raw: bytes
    plan_raw: bytes
    genesis_raw: bytes
    journal_raw: bytes
    key_path: str
    key: bytes
    logical_database_archive: bytes
    genesis_archive: bytes
    head_archive: bytes
    # Original loader output is retained whole as an archive, never a selected
    # operation subset and never replaced with a Python-computed closed flag.
    original_events_archive: bytes
    observed_head: str
    source: object
    lock_fd: int
    def intact(self):
        require(self.lock_fd >= 0, 'RETAINED_V1_CAPTURE_CLOSED')
        self.source.check()
        shared_identity(self.lock_fd, self.selected.journal_path + '.lock')
        for path, raw in ((self.selected.descriptor_path, self.descriptor_raw),
                          (self.selected.plan_path, self.plan_raw),
                          (self.selected.genesis_path, self.genesis_raw),
                          (self.selected.journal_path, self.journal_raw)):
            require(private_bytes(path) == raw and self.source.file(path, ('DATA',)) == raw,
                    'RETAINED_V1_HELD_CONTEXT_CHANGED')
        require(private_bytes(self.key_path) == self.key, 'RETAINED_V1_HELD_KEY_CHANGED')
        database = _database(Path(self.selected.journal_path),
                            _OriginalLoaderContext(exact_json(self.genesis_raw), self.key))
        require(archive(database) == self.logical_database_archive,
                'RETAINED_V1_HELD_DATABASE_CHANGED')
        return self
    def close(self):
        if self.lock_fd >= 0:
            fd = self.lock_fd
            object.__setattr__(self, 'lock_fd', -1)
            os.close(fd)

class _OriginalLoaderContext:
    def __init__(self, genesis, key):
        self.genesis, self.key = genesis, key
    def _schema(self, db):
        return RetainedV1Reader._schema(self, db)
    def _load(self, db):
        return RetainedV1Reader._load(self, db)


def capture_retained_v1(source, selected):
    module = sys.modules.get('_worldline_approved_source_loader')
    require(type(module) is type(sys) and type(source) is module.ApprovedSourceLease,
            'RETAINED_V1_REAL_APPROVED_SOURCE_REQUIRED')
    require(type(selected) is RetainedContext, 'RETAINED_V1_COMPLETE_CONTEXT_REQUIRED')
    source.check()
    def bound(path, expected):
        require(type(path) is str and Path(path).is_absolute(), 'RETAINED_V1_ABSOLUTE_PATH_REQUIRED')
        raw = private_bytes(path)
        require(source.file(path, ('DATA',)) == raw and digest(raw) == expected,
                'RETAINED_V1_PRIOR_DATA_BINDING_CHANGED')
        return raw
    descriptor_raw = bound(selected.descriptor_path, selected.descriptor_sha256)
    plan_raw = bound(selected.plan_path, selected.plan_sha256)
    genesis_raw = bound(selected.genesis_path, selected.genesis_sha256)
    descriptor = exact_json(descriptor_raw)
    plan = exact_json(plan_raw)
    genesis = exact_json(genesis_raw)
    require(type(descriptor) is dict and type(plan) is dict and type(genesis) is dict,
            'RETAINED_V1_CONTEXT_SHAPE')
    require(set(genesis) == {'schema','installation','startup_descriptor_sha256',
            'owner_plan_sha256','issuer_key_sha256','initial_event'} and
            genesis['schema'] == 'worldline.owner-provisioned-root-custody-v1' and
            genesis['installation'] == descriptor['installation_id'] == selected.installation and
            genesis['startup_descriptor_sha256'] == digest(descriptor_raw) and
            genesis['owner_plan_sha256'] == digest(plan_raw), 'RETAINED_V1_ORIGINAL_GENESIS_CONTEXT')
    require(plan['schema'] == 'worldline.protected-root-worker-plan-v1' and
            plan['installation'] == selected.installation and
            plan['startup_descriptor'] == selected.descriptor_path and
            plan['handoff_genesis'] == selected.genesis_path and
            plan['handoff_journal'] == selected.journal_path,
            'RETAINED_V1_ORIGINAL_PLAN_PATHS')
    key_path = str(Path(descriptor['paths']['authority_root']) / 'authority/issuer/state/issuer-key.bin')
    key = private_bytes(key_path)
    require(digest(key) == genesis['issuer_key_sha256'] == selected.issuer_key_sha256,
            'RETAINED_V1_ORIGINAL_KEY_CHANGED')
    lock_path = selected.journal_path + '.lock'
    protected(lock_path)
    fd = os.open(lock_path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        fcntl.flock(fd, fcntl.LOCK_SH | fcntl.LOCK_NB)
        shared_identity(fd, lock_path)
        journal_raw = bound(selected.journal_path, selected.journal_sha256)
        database = _database(Path(selected.journal_path), _OriginalLoaderContext(genesis, key))
        require(database['authenticated_root_head'] == selected.head_event,
                'RETAINED_V1_PRIOR_HEAD_CHANGED')
        # Same retained context must still hold under the shared original lock.
        require(bound(selected.journal_path, selected.journal_sha256) == journal_raw and
                bound(selected.genesis_path, selected.genesis_sha256) == genesis_raw and
                bound(selected.descriptor_path, selected.descriptor_sha256) == descriptor_raw and
                bound(selected.plan_path, selected.plan_sha256) == plan_raw and
                private_bytes(key_path) == key, 'RETAINED_V1_CAPTURE_CHANGED')
        shared_identity(fd, lock_path)
        source.check()
        return RetainedV1Capture(selected, descriptor_raw, plan_raw, genesis_raw,
            journal_raw, key_path, key, archive(database), archive(genesis),
            archive({'head': selected.head_event, 'genesis': genesis}),
            archive(database['authenticated_root_events']), database['authenticated_root_head'], source, fd)
    except BaseException:
        os.close(fd)
        raise
