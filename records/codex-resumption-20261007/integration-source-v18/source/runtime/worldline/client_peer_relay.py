"""Concrete original-fd SCM_RIGHTS transport; custody/grant admission stays separate.

This transport does not start a socket, install a daemon, or authorize an effect.
The protected receiver must hold the installed StartupLease, authenticate its
selected daemon independently, and bind this original requester to native grant,
use reservation, exact transaction and operation before forwarding a caller.
"""
from __future__ import annotations

import array
import json
import os
import socket

from .canonical import canonical_bytes
from .client_peer import KernelPeer, RequestPeer, UCRED, decode_credentials
from .errors import WorldlineError


def send_request_peer(channel: socket.socket, request: RequestPeer) -> None:
    """Caller serializes the channel; exactly one descriptor accompanies a frame."""
    payload = canonical_bytes(request.observation())
    # Variable-length decimal framing avoids inventing another field-width domain.
    frame = str(len(payload)).encode("ascii") + b"\n" + payload
    rights = array.array("i", [request.peer.descriptor()])
    sent = channel.sendmsg([frame], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, rights)])
    if sent <= 0:
        raise WorldlineError("PEER_RELAY_CLOSED", "peer relay did not accept the frame")
    channel.sendall(frame[sent:])


def receive_request_peer(channel: socket.socket, *, expected_daemon_uid: int,
                         frame_limit: int) -> RequestPeer:
    """Own received descriptor and re-read kernel facts; never trust DTO UID.

    expected_daemon_uid and frame_limit come from protected installation policy,
    not the incoming frame. UID equality alone is not daemon custody: the root
    principal must independently establish the exact installed endpoint/lease.
    Named refusal for unavailable custody remains that principal's obligation.
    """
    if type(frame_limit) is not int or frame_limit <= 0 or type(expected_daemon_uid) is not int:
        raise WorldlineError("PEER_RELAY_POLICY_INVALID", "protected framing and daemon policy are required")
    if channel.family != socket.AF_UNIX or channel.getsockopt(socket.SOL_SOCKET, socket.SO_TYPE) != socket.SOCK_STREAM:
        raise WorldlineError("PEER_RELAY_INVALID", "Unix stream relay is required")
    _pid, uid, _gid = decode_credentials(channel.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, UCRED.size))
    if uid != expected_daemon_uid:
        raise WorldlineError("PEER_RELAY_REQUESTER_MISMATCH", "kernel relay peer is not the configured daemon UID")
    descriptors: list[int] = []
    peer = None
    try:
        first, ancillary, flags, _address = channel.recvmsg(1, socket.CMSG_SPACE(array.array("i").itemsize))
        invalid_ancillary = False
        for level, kind, data in ancillary:
            if level != socket.SOL_SOCKET or kind != socket.SCM_RIGHTS:
                invalid_ancillary = True
                continue
            rights = array.array("i")
            complete_length = len(data) - len(data) % rights.itemsize
            rights.frombytes(data[:complete_length])
            descriptors.extend(rights)
            if complete_length != len(data):
                invalid_ancillary = True
        if invalid_ancillary:
            raise WorldlineError("PEER_RELAY_ANCILLARY_INVALID", "only complete original descriptor bytes are allowed")
        if flags & (socket.MSG_CTRUNC | socket.MSG_TRUNC) or len(descriptors) != 1:
            raise WorldlineError("PEER_RELAY_DESCRIPTOR_INVALID", "one complete original descriptor is required")
        os.set_inheritable(descriptors[0], False)
        header = bytearray(first)
        while not header.endswith(b"\n"):
            if len(header) > len(str(frame_limit)):
                raise WorldlineError("PEER_RELAY_FRAME_INVALID", "frame length header exceeds protected limit")
            part = channel.recv(1)
            if not part:
                raise WorldlineError("PEER_RELAY_CLOSED", "partial frame length header")
            header.extend(part)
        digits = bytes(header[:-1])
        if not digits or not digits.isdigit() or (len(digits) > 1 and digits.startswith(b"0")):
            raise WorldlineError("PEER_RELAY_FRAME_INVALID", "canonical decimal frame length required")
        length = int(digits)
        if length > frame_limit:
            raise WorldlineError("PEER_RELAY_FRAME_INVALID", "frame exceeds protected installation limit")
        payload = bytearray()
        while len(payload) < length:
            part = channel.recv(length - len(payload))
            if not part:
                raise WorldlineError("PEER_RELAY_CLOSED", "partial original request frame")
            payload.extend(part)
        def unique(pairs):
            value = {}
            for key, item in pairs:
                if key in value:
                    raise WorldlineError("PEER_RELAY_FRAME_INVALID", "duplicate field in request observation")
                value[key] = item
            return value
        document = json.loads(bytes(payload).decode("utf-8", "strict"), object_pairs_hook=unique)
        if (not isinstance(document, dict)
                or set(document) != {"schema", "observationId", "requestId", "operation", "rawRequest", "peer"}
                or document["schema"] != "worldline.client-request-observation-v1"
                or canonical_bytes(document) != bytes(payload)):
            raise WorldlineError("PEER_RELAY_FRAME_INVALID", "exact canonical original observation required")
        raw_request = bytes.fromhex(document["rawRequest"])
        original = json.loads(raw_request.decode("utf-8", "strict"))
        if (not isinstance(original, dict) or set(original) != {"id", "op", "args"}
                or type(original["id"]) not in (str, int)
                or type(original["id"]) is not type(document["requestId"])
                or original["id"] != document["requestId"] or original["op"] != document["operation"]
                or type(original["op"]) is not str or type(document["operation"]) is not str
                or not isinstance(original["args"], dict)
                or document["rawRequest"] != raw_request.hex()):
            raise WorldlineError("PEER_RELAY_FRAME_INVALID", "original request bytes do not bind the observation")
        peer = KernelPeer.capture_descriptor(descriptors[0])
        result = RequestPeer(peer, document)
        peer = None  # ownership transfers only on complete validation
        return result
    except (UnicodeError, ValueError, TypeError, KeyError) as exc:
        raise WorldlineError("PEER_RELAY_FRAME_INVALID", "malformed original observation") from exc
    finally:
        if peer is not None:
            peer.close()
        for descriptor in descriptors:
            os.close(descriptor)
