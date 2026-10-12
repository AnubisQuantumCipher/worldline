# Explicit full frozen ancestor source below; changed role headers/class only.
# A privileged root controller never satisfies confined Actor K.Check.
"""Complete owned-channel credential observations; never kernel permission.

The protected producer must own the fifth V2 HELD descriptor and retain the
actual native grant, Running decision, peer/pidfd/proc/namespace/helper sources,
complete dispatch and durable history before emitting an acknowledgement.
Parsing, a dataclass, matching bytes or an opaque witness cannot grant authority.
The old helper and producer interfaces are unchanged and remain required.
"""
from __future__ import annotations

import array
from dataclasses import dataclass
import fcntl
import os
import select
import socket
import struct
import termios

FRAME_HEADER = b'WL-ROOT-WORKER-CREDENTIALS-v1'
COMMIT_HEADER = b'WL-ROOT-WORKER-COMMIT-v1\n'
SUPERVISOR_HEADER = b'WL-ROOT-WORKER-SUPERVISOR-v1\n'
UCREDS = struct.Struct('@iII')


class CredentialObservationRefused(ValueError):
    """An incomplete/invalid observation, never a terminal owner verdict."""


def _require(condition, reason):
    if not condition:
        raise CredentialObservationRefused(reason)


def _number(raw):
    _require(type(raw) is bytes and raw and
             all(b'0'[0] <= item <= b'9'[0] for item in raw),
             'ACTOR_CREDENTIAL_DECIMAL_INVALID')
    _require(raw == b'0' or not raw.startswith(b'0'),
             'ACTOR_CREDENTIAL_DECIMAL_NOT_CANONICAL')
    # No host decimal-digit policy is applied to this complete wire grammar.
    value = 0
    for digit in raw:
        value = value * 10 + digit - b'0'[0]
    return value


class _Lines:
    def __init__(self, fields):
        self.fields, self.position = fields, 0

    def take(self):
        _require(self.position < len(self.fields), 'ACTOR_CREDENTIAL_FIELD_ABSENT')
        value = self.fields[self.position]
        self.position += 1
        return value

    def number(self):
        return _number(self.take())

    def count(self):
        count = self.number()
        # Bound only by the actually received complete field roster. This is
        # neither a group/capability nor a resource/quantity/epoch semantic cap.
        _require(count <= len(self.fields) - self.position,
                 'ACTOR_CREDENTIAL_DECLARED_ROSTER_ABSENT')
        return count


@dataclass(frozen=True)
class RootCredentialObservation:
    raw_frame: bytes
    raw_sender_credentials: bytes
    host_pid: int
    sender_real_uid: int
    sender_real_gid: int
    ticket: bytes
    namespace_pid: int
    uids: tuple[int, int, int]
    gids: tuple[int, int, int]
    capability_version: int
    capability_words: tuple[tuple[int, int, int], tuple[int, int, int]]
    securebits: int
    no_new_privs: int
    capabilities: tuple[tuple[int, int, int], ...]
    supplementary_groups: tuple[int, ...]

    def record(self):
        return {
            'schema': 'worldline.root-worker-credential-observation-v1',
            'raw_frame': self.raw_frame.hex(),
            'raw_sender_credentials': self.raw_sender_credentials.hex(),
            'host_pid': self.host_pid, 'sender_real_uid': self.sender_real_uid,
            'sender_real_gid': self.sender_real_gid, 'ticket': self.ticket.hex(),
            'namespace_pid': self.namespace_pid, 'uids': list(self.uids),
            'gids': list(self.gids), 'capability_version': self.capability_version,
            'capability_words': [list(row) for row in self.capability_words],
            'securebits': self.securebits, 'no_new_privs': self.no_new_privs,
            'capabilities': [list(row) for row in self.capabilities],
            'supplementary_groups': list(self.supplementary_groups),
        }


def parse_observation(raw_frame, raw_sender_credentials, expected_ticket):
    """Interpret complete measurement data; this does not authorize execution."""
    _require(type(raw_frame) is bytes and type(raw_sender_credentials) is bytes and
             type(expected_ticket) is bytes and expected_ticket and
             all(byte not in expected_ticket for byte in (b'\n', b'\r', b'\0')),
             'ACTOR_CREDENTIAL_COMPLETE_BYTES_REQUIRED')
    _require(len(raw_sender_credentials) == UCREDS.size,
             'ACTOR_CREDENTIAL_KERNEL_SENDER_SIZE_INVALID')
    host_pid, uid, gid = UCREDS.unpack(raw_sender_credentials)
    _require(host_pid > 0, 'ACTOR_CREDENTIAL_HOST_PID_ABSENT')
    _require(raw_frame.endswith(b'\n'), 'ACTOR_CREDENTIAL_FRAME_INCOMPLETE')
    fields = raw_frame.split(b'\n')
    _require(fields.pop() == b'', 'ACTOR_CREDENTIAL_FRAME_SUFFIX_INVALID')
    lines = _Lines(fields)
    _require(lines.take() == FRAME_HEADER, 'ACTOR_CREDENTIAL_VERSION_UNKNOWN')
    ticket = lines.take()
    _require(ticket == expected_ticket, 'ACTOR_CREDENTIAL_DISPATCH_TICKET_CHANGED')
    namespace_pid = lines.number()
    _require(namespace_pid > 0, 'ACTOR_CREDENTIAL_NAMESPACE_PID_ABSENT')
    uids = (lines.number(), lines.number(), lines.number())
    gids = (lines.number(), lines.number(), lines.number())
    version = lines.number()
    words = ((lines.number(), lines.number(), lines.number()),
             (lines.number(), lines.number(), lines.number()))
    securebits, no_new_privs = lines.number(), lines.number()
    count = lines.count()
    caps = tuple((lines.number(), lines.number(), lines.number())
                 for _index in range(count))
    _require(tuple(row[0] for row in caps) == tuple(range(count)),
             'ACTOR_CREDENTIAL_CAPABILITY_ROSTER_CONFLICT')
    group_count = lines.count()
    groups = tuple(lines.number() for _index in range(group_count))
    _require(lines.take() == b'END' and lines.position == len(fields),
             'ACTOR_CREDENTIAL_COMPLETE_ROSTER_REQUIRED')
    # Automatic SO_PASSCRED data carries actual sender real UID/GID, not a
    # post-fork SO_PEERCRED snapshot or an asserted effective identity.
    _require((uid, gid) == (uids[0], gids[0]),
             'ACTOR_CREDENTIAL_ACTUAL_SENDER_RECORD_CONFLICT')
    return RootCredentialObservation(raw_frame, raw_sender_credentials,
        host_pid, uid, gid, ticket, namespace_pid, uids, gids, version, words,
        securebits, no_new_privs, caps, groups)


def receive_observation(receiver, expected_ticket):
    """Receive the actual owned socket's complete packet and kernel credentials.

    The producer serializes use of this sole retained receiver. The actual
    FIONREAD extent is transport metadata; truncation/races/EOF refuse. No fixed
    frame cap, invented sender, resource domain change or missing-fact fallback.
    """
    _require(receiver.family == socket.AF_UNIX and
             receiver.getsockopt(socket.SOL_SOCKET, socket.SO_TYPE) == socket.SOCK_SEQPACKET and
             receiver.getsockopt(socket.SOL_SOCKET, socket.SO_PASSCRED) == 1,
             'ACTOR_CREDENTIAL_OWNED_SEQPACKET_REQUIRED')
    extent = array.array('i', [0])
    fcntl.ioctl(receiver.fileno(), termios.FIONREAD, extent, True)
    _require(extent[0] > 0, 'ACTOR_CREDENTIAL_COMPLETE_PENDING_PACKET_ABSENT')
    frame, ancillary, flags, _address = receiver.recvmsg(extent[0],
        socket.CMSG_SPACE(UCREDS.size), socket.MSG_CMSG_CLOEXEC)
    received_fds = []
    primary = None
    try:
        for level, kind, raw in ancillary:
            if level == socket.SOL_SOCKET and kind == socket.SCM_RIGHTS:
                rights = array.array('i')
                complete = len(raw) - len(raw) % rights.itemsize
                rights.frombytes(raw[:complete])
                received_fds.extend(rights)
        _require(not flags & (socket.MSG_TRUNC | socket.MSG_CTRUNC) and
                 len(frame) == extent[0], 'ACTOR_CREDENTIAL_PACKET_TRUNCATED_OR_CHANGED')
        _require(len(ancillary) == 1 and ancillary[0][:2] ==
                 (socket.SOL_SOCKET, socket.SCM_CREDENTIALS),
                 'ACTOR_CREDENTIAL_COMPLETE_KERNEL_CONTROL_REQUIRED')
        return parse_observation(frame, ancillary[0][2], expected_ticket)
    except BaseException as error:
        primary = error
        raise
    finally:
        # Even a refused message cannot leak an unexpected received descriptor.
        first = None
        for fd in received_fds:
            try:
                os.close(fd)
            except OSError as error:
                if first is None:
                    first = error
                else:
                    first.add_note('Additional received descriptor close failure: ' + repr(error))
        if first is not None:
            if primary is not None:
                primary.add_note('Received descriptor cleanup failed: ' + repr(first))
            else:
                raise first


def wait_observation(receiver, expected_ticket):
    """Wait for the owned channel; no elapsed-time or EOF completion claim."""
    poller = select.poll()
    poller.register(receiver.fileno(), select.POLLIN | select.POLLHUP | select.POLLERR)
    poller.poll()
    return receive_observation(receiver, expected_ticket)


def commit_ack_bytes(raw_frame, complete_durable_witness):
    """Data framing only. The protected caller must establish the native commit.

    Nothing about caller-provided witness bytes proves permission or durability.
    Their entire authentic source, native result and journal/head/dispatch join
    must already have been retained by the complete actual protected producer.
    """
    _require(type(raw_frame) is bytes and raw_frame and
             type(complete_durable_witness) is bytes and complete_durable_witness,
             'ACTOR_CREDENTIAL_COMPLETE_COMMIT_DATA_REQUIRED')
    return (COMMIT_HEADER + str(len(raw_frame)).encode('ascii') + b'\n' + raw_frame +
            str(len(complete_durable_witness)).encode('ascii') + b'\n')


def send_committed_ack(receiver, raw_frame, complete_durable_witness):
    """Send complete data on the already owned channel after native durable commit."""
    body = commit_ack_bytes(raw_frame, complete_durable_witness)
    current = UCREDS.pack(os.getpid(), os.geteuid(), os.getegid())
    fd = os.memfd_create('worldline-actor-complete-durable-witness',
                         os.MFD_CLOEXEC | os.MFD_ALLOW_SEALING)
    primary = None
    try:
        os.fchmod(fd, 0o600)
        written = 0
        view = memoryview(complete_durable_witness)
        while written < len(view):
            count = os.write(fd, view[written:])
            _require(count > 0, 'ACTOR_CREDENTIAL_WITNESS_WRITE_INCOMPLETE')
            written += count
        required = fcntl.F_SEAL_SEAL | fcntl.F_SEAL_SHRINK | fcntl.F_SEAL_GROW | fcntl.F_SEAL_WRITE
        fcntl.fcntl(fd, fcntl.F_ADD_SEALS, required)
        _require(os.fstat(fd).st_size == len(view) and
                 fcntl.fcntl(fd, fcntl.F_GET_SEALS) & required == required,
                 'ACTOR_CREDENTIAL_COMPLETE_WITNESS_SEALS_UNAVAILABLE')
        rights = array.array('i', [fd])
        sent = receiver.sendmsg([body], [(socket.SOL_SOCKET, socket.SCM_CREDENTIALS, current),
            (socket.SOL_SOCKET, socket.SCM_RIGHTS, rights)], socket.MSG_NOSIGNAL)
        _require(sent == len(body), 'ACTOR_CREDENTIAL_COMMIT_SEND_INCOMPLETE')
        return body
    except BaseException as error:
        primary = error
        raise
    finally:
        try:
            os.close(fd)
        except OSError as cleanup:
            if primary is None:
                raise
            primary.add_note('Complete witness descriptor cleanup failed: ' + repr(cleanup))
