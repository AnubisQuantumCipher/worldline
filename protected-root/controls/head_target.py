"""Full real syscall/SQL observations for the exclusive offline OJ creator.

No absent DB is projected into an empty authenticated head. A partially created
DB retains its real bytes/schema/error; only the native bootstrap/transition
boundary may authorize the next effect. This module supplies no permission.
"""
from __future__ import annotations
import errno
import os
from pathlib import Path
import stat
import sqlite3
from urllib.parse import quote


def identity(info):
    return {'device': info.st_dev, 'inode': info.st_ino, 'mode': info.st_mode,
        'uid': info.st_uid, 'gid': info.st_gid, 'links': info.st_nlink, 'size': info.st_size,
        'mtime_ns': info.st_mtime_ns, 'ctime_ns': info.st_ctime_ns}


class HeadTarget:
    def __init__(self, path, source_lease):
        from worldline.custody_subject_capture import syscall, fd_identity
        self.path = Path(path)
        self.source_lease = source_lease
        self.syscall = syscall
        self.fd_identity = fd_identity
        self.fd = None
        self.creation = None
        self.sync_receipt = None
        self.probe_fd = None
        self.read_connection = None
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
        self.parent_fd, receipt = syscall(self, 'open',
            {'path': os.fsencode(self.path.parent), 'flags': flags},
            lambda: os.open(self.path.parent, flags))
        if receipt['errno'] != 0:
            raise OSError(receipt['errno'], receipt['message'], str(self.path.parent))
        self.parent_open = receipt

    def capture(self, connection=None):
        self.release_capture()
        parent, parent_receipt = self.syscall(self, 'lstat',
            {'path': os.fsencode(self.path.parent)}, lambda: identity(self.path.parent.lstat()))
        if parent_receipt['errno'] != 0:
            raise OSError(parent_receipt['errno'], parent_receipt['message'], str(self.path.parent))
        named, named_receipt = self.syscall(self, 'lstat',
            {'path': os.fsencode(self.path)}, lambda: identity(self.path.lstat()))
        flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC
        self.probe_fd, probe = self.syscall(self, 'open',
            {'path': os.fsencode(self.path), 'flags': flags}, lambda: os.open(self.path, flags))
        raw = raw_after = logical = read_error = database_error = None
        probe_identity = probe_identity_after = probe_info = probe_link = None
        database_files = []
        database_list = None
        fd_before_sql = tuple(int(path.name) for path in Path('/proc/self/fd').iterdir())
        if self.probe_fd is not None:
            probe_identity = self.fd_identity(self.probe_fd)
            probe_info = Path('/proc/self/fdinfo/' + str(self.probe_fd)).read_bytes()
            probe_link = os.fsencode(os.readlink('/proc/self/fd/' + str(self.probe_fd)))
            try:
                with os.fdopen(os.dup(self.probe_fd), 'rb') as stream:
                    raw = stream.read()
            except OSError as error:
                read_error = {'type': type(error).__qualname__, 'message': str(error),
                              'args': tuple(error.args), 'errno': error.errno}
            if named is not None and stat.S_ISREG(named['mode']):
                from worldline.root_worker_current_state import _database_connection
                try:
                    if connection is None:
                        self.read_connection = sqlite3.connect('file:' + quote(str(self.path), safe='/') +
                            '?mode=ro', uri=True, isolation_level=None)
                        connection = self.read_connection
                        connection.execute('PRAGMA trusted_schema=OFF')
                        connection.execute('PRAGMA query_only=ON')
                        connection.execute('PRAGMA foreign_keys=ON')
                        connection.execute('BEGIN')
                    if not connection.in_transaction:
                        raise RuntimeError('OJ_OFFLINE_SQL_CAPTURE_MUST_HOLD_REAL_TRANSACTION')
                    logical = _database_connection(connection)
                    database_list = tuple(tuple(row) for row in connection.execute('PRAGMA database_list'))
                    targets = {os.fsencode(self.path), os.fsencode(str(self.path) + '-wal'),
                               os.fsencode(str(self.path) + '-shm')}
                    for candidate in Path('/proc/self/fd').iterdir():
                        try:
                            link = os.fsencode(os.readlink(candidate))
                            if link not in targets:
                                continue
                            fd = int(candidate.name)
                            database_files.append({'fd': fd, 'link': link,
                                'identity': self.fd_identity(fd),
                                'fdinfo': Path('/proc/self/fdinfo/' + str(fd)).read_bytes(),
                                'named': identity(Path(os.fsdecode(link)).lstat()),
                                'role': 'probe' if fd == self.probe_fd else
                                        'exclusive-open' if fd == self.fd else 'other-target-descriptor',
                                'present_before_sql_acquisition': fd in fd_before_sql})
                        except FileNotFoundError:
                            # /proc's enumeration FD itself can close before its
                            # name is examined. No vanished target FD is credited.
                            continue
                except BaseException as error:
                    database_error = {'type': type(error).__qualname__, 'module': type(error).__module__,
                        'message': str(error), 'args': tuple(error.args), 'errno': getattr(error, 'errno', None)}
            try:
                with os.fdopen(os.dup(self.probe_fd), 'rb') as stream:
                    stream.seek(0)
                    raw_after = stream.read()
            except OSError as error:
                read_error = {'type': type(error).__qualname__, 'message': str(error),
                              'args': tuple(error.args), 'errno': error.errno}
            probe_identity_after = self.fd_identity(self.probe_fd)
        _, named_after = self.syscall(self, 'lstat',
            {'path': os.fsencode(self.path)}, lambda: identity(self.path.lstat()))
        return {'path': os.fsencode(self.path), 'parent_path': os.fsencode(self.path.parent),
            'parent_fd': self.parent_fd, 'parent_held_identity': self.fd_identity(self.parent_fd),
            'parent_named_identity': parent, 'named': named_receipt, 'probe': probe,
            'raw': raw, 'logical_database': logical, 'raw_after': raw_after,
            'read_error': read_error, 'database_error': database_error,
            'probe_held_identity': probe_identity, 'probe_held_identity_after': probe_identity_after,
            'probe_fdinfo': probe_info, 'probe_link': probe_link, 'named_after': named_after,
            'database_files': tuple(database_files), 'database_list': database_list,
            'fd_before_sql': fd_before_sql, 'source_after': self.source_lease.check()}

    def release_capture(self):
        try:
            if self.read_connection is not None:
                connection = self.read_connection
                self.read_connection = None
                try:
                    if connection.in_transaction:
                        connection.rollback()
                finally:
                    connection.close()
        finally:
            if self.probe_fd is not None:
                os.close(self.probe_fd)
                self.probe_fd = None

    def exclusive_open(self, before_input, actual_artifact):
        self.release_capture()
        if self.fd is not None or self.creation is not None:
            raise RuntimeError('OJ_OFFLINE_EXCLUSIVE_OPEN_CANNOT_RETRY')
        if (actual_artifact['named']['errno'] != errno.ENOENT
                or actual_artifact['probe']['errno'] != errno.ENOENT):
            raise RuntimeError('OJ_OFFLINE_ACTUAL_ABSENCE_PREIMAGE_REQUIRED')
        flags = os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC
        self.fd, receipt = self.syscall(self, 'open',
            {'path': os.fsencode(self.path), 'flags': flags, 'mode': 0o600},
            lambda: os.open(self.path, flags, 0o600))
        if receipt['errno'] != 0:
            raise OSError(receipt['errno'], receipt['message'], str(self.path))
        self.creation = {'before': before_input, 'open': receipt, 'fd': self.fd,
            'held_identity': self.fd_identity(self.fd),
            'fdinfo': Path('/proc/self/fdinfo/' + str(self.fd)).read_bytes(),
            'link': os.fsencode(os.readlink('/proc/self/fd/' + str(self.fd)))}
        return self.creation

    def sync(self):
        if self.fd is None:
            raise RuntimeError('OJ_OFFLINE_ACTUAL_EXCLUSIVE_DESCRIPTOR_REQUIRED')
        held = self.fd_identity(self.fd)
        named = identity(self.path.lstat())
        if (held['device'], held['inode']) != (named['device'], named['inode']):
            raise RuntimeError('OJ_OFFLINE_DURABLE_HEAD_INODE_CHANGED')
        _, file_receipt = self.syscall(self, 'fsync', {'fd': self.fd}, lambda: os.fsync(self.fd))
        _, parent_receipt = self.syscall(self, 'fsync', {'fd': self.parent_fd},
            lambda: os.fsync(self.parent_fd))
        self.sync_receipt = {'file': file_receipt, 'parent': parent_receipt,
            'file_before': held, 'file_after': self.fd_identity(self.fd),
            'file_named_after': identity(self.path.lstat()),
            'parent_after': self.fd_identity(self.parent_fd)}
        for receipt in (file_receipt, parent_receipt):
            if receipt['errno'] != 0:
                raise OSError(receipt['errno'], receipt['message'])
        return self.sync_receipt

    def close(self):
        self.release_capture()
        try:
            if self.fd is not None:
                os.close(self.fd)
                self.fd = None
        finally:
            os.close(self.parent_fd)
