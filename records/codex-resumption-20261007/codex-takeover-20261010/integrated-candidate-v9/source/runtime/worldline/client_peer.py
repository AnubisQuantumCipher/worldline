"""Original daemon connection observations, never capability or protected authority.

The retained descriptor lets a separately authenticated protected relay re-read
the kernel's original SO_PEERCRED. Serialized observations cannot replace it.
"""
from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
import os
import socket
import stat
import struct
from typing import Iterator
import uuid

from .errors import WorldlineError

# Linux struct ucred: pid_t signed; uid_t and gid_t unsigned. Native layout,
# rather than three signed fields, preserves the entire original UID/GID domain.
UCRED = struct.Struct("@iII")
_READ_SOURCE: ContextVar[dict | None] = ContextVar("worldline_peer_read_source", default=None)

@contextmanager
def peer_read_source(source):
    token = _READ_SOURCE.set(source)
    try:
        yield
    finally:
        _READ_SOURCE.reset(token)


def decode_credentials(raw: bytes) -> tuple[int, int, int]:
    if type(raw) is not bytes or len(raw) != UCRED.size:
        raise WorldlineError("PEER_CREDENTIALS_UNAVAILABLE", "complete native ucred bytes are required")
    return UCRED.unpack(raw)


class KernelPeer:
    """Owns a duplicate of an actual connected Unix socket, not an asserted UID."""
    def __init__(self, transport: socket.socket) -> None:
        self._socket = transport
        self._closed = False
        self.read_receipts = []
        self.close_receipt = None
        try:
            if transport.family != socket.AF_UNIX or transport.getsockopt(socket.SOL_SOCKET, socket.SO_TYPE) != socket.SOCK_STREAM:
                raise WorldlineError("PEER_TRANSPORT_INVALID", "a connected Unix stream is required")
            transport.getpeername()
            self._initial = self._read()
        except BaseException:
            transport.close()
            self._closed = True
            raise

    @classmethod
    def capture_writer(cls, writer) -> KernelPeer:
        transport = writer.get_extra_info("socket")
        if transport is None:
            raise WorldlineError("PEER_CREDENTIALS_UNAVAILABLE", "original Unix client socket is unavailable")
        descriptor = os.dup(transport.fileno())
        try:
            owned = socket.socket(fileno=descriptor)
        except BaseException:
            os.close(descriptor)
            raise
        return cls(owned)

    @classmethod
    def capture_descriptor(cls, descriptor: int) -> KernelPeer:
        """Re-read a received fd. Caller must separately authenticate the relay.

        Receiving a connected fd alone does not establish who selected it, nor
        bind any operation, grant, request bytes, transaction or preparer.
        """
        owned_descriptor = os.dup(descriptor)
        try:
            owned = socket.socket(fileno=owned_descriptor)
        except BaseException:
            os.close(owned_descriptor)
            raise
        return cls(owned)

    def _read(self) -> dict:
        if self._closed:
            raise WorldlineError("PEER_TRANSPORT_CLOSED", "original peer descriptor has been released")
        fd = self._socket.fileno()
        source = _READ_SOURCE.get()
        trace = []
        self.read_receipts.append(trace)
        try:
            info = os.fstat(fd)
        except OSError as error:
            trace.append({"call": "fstat", "args": {"fd": fd}, "fd": fd,
                          "result": -1, "errno": error.errno, "source": source})
            raise
        trace.append({"call": "fstat", "args": {"fd": fd}, "fd": fd,
                      "result": 0, "errno": 0, "source": source,
                      "identity": {"device": info.st_dev, "inode": info.st_ino, "mode": info.st_mode}})
        if not stat.S_ISSOCK(info.st_mode):
            raise WorldlineError("PEER_TRANSPORT_INVALID", "original descriptor is no longer a socket")
        try:
            raw = self._socket.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, UCRED.size)
        except OSError as error:
            trace.append({"call": "getsockopt", "args": {"fd": fd, "level": socket.SOL_SOCKET,
                          "option": socket.SO_PEERCRED, "length": UCRED.size}, "fd": fd,
                          "result": -1, "errno": error.errno, "raw": None, "source": source})
            raise
        trace.append({"call": "getsockopt", "args": {"fd": fd, "level": socket.SOL_SOCKET,
                      "option": socket.SO_PEERCRED, "length": UCRED.size}, "fd": fd,
                      "result": 0, "errno": 0, "raw": raw, "source": source})
        pid, uid, gid = decode_credentials(raw)
        return {"source": "linux.SO_PEERCRED", "rawUcred": raw.hex(),
                "pid": pid, "uid": uid, "gid": gid,
                "socketIdentity": {"device": info.st_dev, "inode": info.st_ino,
                                   "mode": info.st_mode}}

    def observation(self) -> dict:
        now = self._read()
        if now != self._initial:
            raise WorldlineError("PEER_TRANSPORT_CHANGED", "retained original peer observation changed")
        return now

    def descriptor(self) -> int:
        self.observation()
        return self._socket.fileno()

    def duplicate(self) -> KernelPeer:
        result = self.capture_descriptor(self.descriptor())
        if result.observation() != self.observation():
            result.close()
            raise WorldlineError("PEER_TRANSPORT_CHANGED", "duplicate is not the retained connection")
        return result

    def close(self) -> None:
        if not self._closed:
            fd = self._socket.fileno()
            source = _READ_SOURCE.get()
            receipt = {"call": "close", "fd": fd, "args": {"fd": fd}, "source": source}
            self.close_receipt = receipt
            self._closed = True
            try:
                self._socket.close()
            except OSError as error:
                receipt.update(result=-1, errno=error.errno)
                raise
            receipt.update(result=0, errno=0)
            try:
                info = os.fstat(fd)
            except OSError as error:
                receipt["readback"] = {"call": "fstat", "fd": fd, "args": {"fd": fd},
                                       "result": -1, "errno": error.errno, "source": source}
            else:
                receipt["readback"] = {"call": "fstat", "fd": fd, "args": {"fd": fd},
                                       "result": 0, "errno": 0, "source": source,
                                       "identity": {"device": info.st_dev, "inode": info.st_ino, "mode": info.st_mode}}


class RequestPeer:
    def __init__(self, peer: KernelPeer, document: dict) -> None:
        self.peer = peer
        validate_observation(document)
        from .canonical import canonical_bytes
        import json
        self._document = json.loads(canonical_bytes(document))
        if self._document.get("peer") != peer.observation():
            raise WorldlineError("PEER_REQUEST_MISMATCH", "request observation is not this retained connection")

    @classmethod
    def capture(cls, writer, *, line: bytes, operation: str, request_id: str | int) -> RequestPeer:
        peer = KernelPeer.capture_writer(writer)
        try:
            return cls(peer, {"schema": "worldline.client-request-observation-v1",
                              "observationId": uuid.uuid4().hex, "requestId": request_id,
                              "operation": operation, "rawRequest": line.hex(),
                              "peer": peer.observation()})
        except BaseException:
            peer.close()
            raise

    def observation(self) -> dict:
        from .canonical import canonical_bytes
        import json
        if self.peer.observation() != self._document["peer"]:
            raise WorldlineError("PEER_REQUEST_MISMATCH", "request peer changed")
        # Caller mutation never modifies the retained request.
        return json.loads(canonical_bytes(self._document))

    def duplicate(self) -> RequestPeer:
        peer = self.peer.duplicate()
        try:
            return RequestPeer(peer, self.observation())
        except BaseException:
            peer.close()
            raise

    def close(self) -> None:
        self.peer.close()


_CURRENT: ContextVar[RequestPeer | None] = ContextVar("worldline_original_client", default=None)


def current_peer() -> RequestPeer | None:
    return _CURRENT.get()


@contextmanager
def request_scope(peer: RequestPeer | None) -> Iterator[None]:
    token = _CURRENT.set(peer)
    try:
        yield
    finally:
        _CURRENT.reset(token)


def current_observation() -> dict | None:
    peer = current_peer()
    return None if peer is None else peer.observation()


def validate_observation(document: dict) -> None:
    """Validate complete data, with no custody or authorization implication."""
    try:
        if (type(document) is not dict
                or set(document) != {"schema", "observationId", "requestId", "operation", "rawRequest", "peer"}
                or document["schema"] != "worldline.client-request-observation-v1"
                or type(document["observationId"]) is not str
                or uuid.UUID(hex=document["observationId"]).hex != document["observationId"]
                or type(document["requestId"]) not in (str, int)
                or type(document["operation"]) is not str):
            raise ValueError("request envelope")
        raw_request = bytes.fromhex(document["rawRequest"])
        if raw_request.hex() != document["rawRequest"]:
            raise ValueError("request raw bytes")
        peer = document["peer"]
        if (type(peer) is not dict or set(peer) != {"source", "rawUcred", "pid", "uid", "gid", "socketIdentity"}
                or peer["source"] != "linux.SO_PEERCRED"):
            raise ValueError("peer envelope")
        raw = bytes.fromhex(peer["rawUcred"])
        if raw.hex() != peer["rawUcred"] or any(type(peer[field]) is not int for field in ("pid", "uid", "gid")):
            raise ValueError("peer scalar types")
        if decode_credentials(raw) != (peer["pid"], peer["uid"], peer["gid"]):
            raise ValueError("peer raw bytes")
        identity = peer["socketIdentity"]
        if (type(identity) is not dict or set(identity) != {"device", "inode", "mode"}
                or any(type(value) is not int for value in identity.values())
                or not stat.S_ISSOCK(identity["mode"])):
            raise ValueError("socket identity")
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        raise WorldlineError("PREPARER_PEER_MALFORMED", "complete lossless original observation is required") from exc


def preparer_observations(record: dict) -> dict:
    """Lossless native-input pair. There is deliberately no Python verdict.

    The complete preparer observation and current original kernel requester are
    distinct facts. Absent fixture/legacy material remains typed absence; only
    the protected native authority path may classify it or decide same-owner.
    PID/GID/connection are retained but no new same-process requirement is added.
    """
    prepared = record.get("preparerPeer")
    current = current_observation()
    if prepared is not None:
        validate_observation(prepared)
    if current is not None:
        validate_observation(current)
    from .canonical import canonical_bytes
    import json
    return json.loads(canonical_bytes({"preparer": prepared, "requester": current}))
