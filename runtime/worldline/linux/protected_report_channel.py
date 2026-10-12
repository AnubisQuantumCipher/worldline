"""Actual native-finalization report-FD transfer into daemon custody.

Only the kernel peer identity joins this endpoint to the observed examiner. The
message contains raw fstat cells, never a verdict or a claimed role. Descriptor
custody is acknowledged before the native sender closes its own original FD.
"""
from __future__ import annotations

import array
import errno
import os
from pathlib import Path
import socket
import struct
import threading
import time
import uuid

from ..raw_observation import optional_bytes

MOUNT = '/run/worldline-protected-report.sock'
_REPORT = struct.Struct('<8sQQQQQQqQqQQqqqq')
_CLOSE = struct.Struct('<8sqq')
_ERROR = struct.Struct('<8sqqq')


class ProtectedReportChannel:
    def __init__(self, provider):
        self.provider = provider
        self.stop = threading.Event()
        self.thread = None
        self.listener = None
        self.record = {'schema': 'worldline-native-report-fd-transfer-v1',
                       'fd': None, 'nativeBefore': None, 'daemonBefore': None,
                       'peerCredentials': None, 'peerPidfd': None,
                       'nativeClose': None, 'payload': None, 'ack': None,
                       'readEOF': False, 'exception': None}
        provider.record['reportTransfer'] = self.record

    def start(self):
        provider = self.provider
        directory = provider._directory(Path(provider.plan['runtime']))
        self.path = str(Path(provider.plan['runtime']) / 'protected-report.sock')
        self.listener = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        self.listener.bind('/proc/self/fd/' + str(directory) + '/protected-report.sock')
        os.chmod('protected-report.sock', 0o600, dir_fd=directory, follow_symlinks=False)
        self.listener.listen(1)
        self.listener.settimeout(0.1)
        provider.plan['protectedReportSocket'] = self.path
        self.thread = threading.Thread(target=self._serve, name='worldline-protected-report-receiver')
        self.thread.start()

    def _deadline(self):
        return self.provider.plan['bootstrapDeadlineMonotonic'] + self.provider.spec.timeout_seconds + 20

    def _read(self, connection, context, size, *, descriptors=False):
        api = 'socket.recvmsg' if descriptors else 'socket.recv'
        try:
            value = (connection.recvmsg(size, socket.CMSG_SPACE(2 * array.array('i').itemsize),
                                       socket.MSG_CMSG_CLOEXEC) if descriptors else connection.recv(size))
        except BaseException as error:
            from ..raw_observation import exception_observation
            self.provider.lifecycle_channel({**context, 'operation': 'read', 'api': api,
                'return': -1, 'errno': getattr(error, 'errno', None), 'returned': False,
                'bytes': optional_bytes(None), 'exception': exception_observation(error)})
            raise
        payload = value[0] if descriptors else value
        self.provider.lifecycle_channel({**context, 'operation': 'read', 'api': api,
            'return': len(payload), 'errno': 0, 'returned': True, 'bytes': optional_bytes(payload)})
        return value

    def _shutdown(self, connection, context):
        event = {**context, 'operation': 'shutdown', 'api': 'socket.shutdown', 'how': socket.SHUT_RD}
        try:
            returned = connection.shutdown(socket.SHUT_RD)
        except BaseException as error:
            from ..raw_observation import exception_observation
            self.provider.lifecycle_channel({**event, 'return': -1, 'returned': False,
                'errno': getattr(error, 'errno', None), 'exception': exception_observation(error)})
            raise
        self.provider.lifecycle_channel({**event, 'apiReturn': returned, 'return': 0,
                                         'errno': 0, 'returned': True})

    def _serve(self):
        provider = self.provider
        connection = None
        context = None
        try:
            while not self.stop.is_set():
                try:
                    connection, _address = self.listener.accept()
                    break
                except TimeoutError:
                    continue
                except OSError:
                    if self.stop.is_set():
                        return
                    raise
            if connection is None:
                return
            connection.settimeout(max(0.1, self._deadline() - time.monotonic()))
            credentials = struct.unpack('3i', connection.getsockopt(
                socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize('3i')))
            self.record['peerCredentials'] = dict(zip(('pid', 'uid', 'gid'), credentials))
            self.record['peerPidfd'] = provider._own(connection.getsockopt(socket.SOL_SOCKET, 77))
            channel = str(uuid.uuid4())
            self.record['channelId'] = channel
            context = {'channelId': channel, 'fd': connection.fileno(),
                       'peerCredentials': self.record['peerCredentials'],
                       'scope': 'native-original-report-transfer'}
            provider.lifecycle_channel({**context, 'operation': 'acquire',
                'api': 'socket.fileno', 'return': connection.fileno(), 'errno': 0, 'returned': True})
            with provider.lock:
                roles = [row for row in provider.record['roles'] if row.get('roleClaim') == 'examiner'
                         and row.get('peerCredentials') == self.record['peerCredentials']]
            if len(roles) != 1:
                raise OSError(errno.EPERM, 'protected report socket peer is not the observed examiner')
            context['startupRecordId'] = roles[0]['recordId']
            payload, ancillary, flags, _address = self._read(
                connection, context, _REPORT.size + 1, descriptors=True)
            descriptors = []
            for level, kind, content in ancillary:
                if level == socket.SOL_SOCKET and kind == socket.SCM_RIGHTS:
                    received = array.array('i')
                    received.frombytes(content[:len(content) - len(content) % received.itemsize])
                    descriptors.extend(provider._own(fd) for fd in received)
                else:
                    raise OSError(errno.EPROTO, 'unexpected protected report ancillary record')
            self.record['payload'] = optional_bytes(payload)
            if flags & (socket.MSG_TRUNC | socket.MSG_CTRUNC):
                raise OSError(errno.EMSGSIZE, 'truncated original report descriptor transfer')
            acquisition_error = None
            if payload.startswith(b'WLPEv001') and len(payload) == _ERROR.size and not descriptors:
                _magic, operation, returned, saved_errno = _ERROR.unpack(payload)
                self.record['nativeError'] = {'operation': operation, 'return': returned, 'errno': saved_errno}
                acquisition_error = OSError(saved_errno, 'native original report acquisition failed')
                provider._failure('native-report-acquisition', acquisition_error)
            else:
                if len(payload) != _REPORT.size or len(descriptors) != 1:
                    raise OSError(errno.EPROTO, 'original report descriptor frame differs')
                magic, *values = _REPORT.unpack(payload)
                if magic != b'WLPRv001':
                    raise OSError(errno.EPROTO, 'original report descriptor version differs')
                self.record['nativeBefore'] = dict(zip(('device', 'inode', 'mode', 'uid', 'gid', 'size'), values[:6]))
                self.record['nativeBefore'].update(mtime_ns=values[6] * 1_000_000_000 + values[7],
                    ctime_ns=values[8] * 1_000_000_000 + values[9], nlink=values[10])
                self.record.update(dict(zip(('nativeOpenReturn', 'nativeOpenErrno',
                    'nativeFstatReturn', 'nativeFstatErrno'), values[11:])))
                self.record['fd'] = descriptors[0]
                self.record['daemonBefore'] = provider._stat(descriptors[0])
            # Retain before acknowledging custody. A retention exception cannot
            # acknowledge an unowned descriptor or substitute another report path.
            if provider.observer is not None:
                from ..raw_observation import retain_observation
                retain_observation(lambda value: provider.observer(
                    'private-native-report-fd-receive', 0, value), dict(self.record))
            count = connection.send(b'WLPA')
            self.record['ack'] = {'bytes': optional_bytes(b'WLPA'), 'return': count, 'errno': 0}
            if count != 4:
                raise OSError(errno.EIO, 'incomplete original report descriptor acknowledgement')
            closing = self._read(connection, context, _CLOSE.size + 1)
            if closing:
                if len(closing) != _CLOSE.size:
                    raise OSError(errno.EPROTO, 'native original report close receipt is absent')
                magic, returned, saved_errno = _CLOSE.unpack(closing)
                if magic != b'WLPCv001':
                    raise OSError(errno.EPROTO, 'native original report close receipt differs')
                self.record['nativeClose'] = {'return': returned, 'errno': saved_errno,
                                              'bytes': optional_bytes(closing)}
                terminal = self._read(connection, context, 1)
            elif acquisition_error is None:
                raise OSError(errno.EPROTO, 'native original report close receipt is absent')
            else:
                terminal = closing
            self.record['readEOF'] = terminal == b''
            if terminal:
                raise OSError(errno.EPROTO, 'extra original report descriptor transfer data')
            self._shutdown(connection, context)
        except BaseException as error:
            from ..raw_observation import exception_observation
            self.record['exception'] = exception_observation(error)
            provider._failure('native-report-transfer', error)
        finally:
            if connection is not None:
                descriptor = connection.fileno()
                try:
                    connection.close()
                    if context is not None and context['channelId'] in provider.channel_handles:
                        provider.lifecycle_channel({**context, 'fd': descriptor, 'operation': 'close',
                            'api': 'socket.close', 'apiReturn': None, 'return': 0, 'errno': 0, 'returned': True})
                except BaseException as error:
                    if context is not None and context['channelId'] in provider.channel_handles:
                        from ..raw_observation import exception_observation
                        provider.lifecycle_channel({**context, 'fd': descriptor, 'operation': 'close',
                            'api': 'socket.close', 'return': -1, 'errno': getattr(error, 'errno', None),
                            'returned': False, 'exception': exception_observation(error)})
                    provider._failure('native-report-channel-close', error)

    def finish(self):
        # The actual executor has already waited for process death. A native
        # report sender cannot remain live; stop an unused listener immediately
        # instead of adding a new timeout to original missing-report precedence.
        self.close()

    def close(self):
        self.stop.set()
        if self.listener is not None:
            try:
                self.listener.close()
            except BaseException as error:
                self.provider._failure('native-report-listener-close', error)
        if self.thread is not None:
            self.thread.join()
