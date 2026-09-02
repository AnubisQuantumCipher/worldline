from __future__ import annotations

import ctypes
from dataclasses import dataclass
import os
from pathlib import Path
from threading import Lock
from typing import Iterable, Mapping

from .errors import CoreUnavailable, WorldlineError

HASH_BYTES = 32

STATE_CODES: dict[str, int] = {
    "MUTABLE": 0,
    "FINALIZING": 1,
    "VALID": 2,
    "DEGRADED": 3,
    "DEAD": 4,
    "ARCHIVED": 5,
    "COLLAPSED": 6,
}

COLLAPSE_DECISIONS: dict[int, str] = {
    0: "AUTHORIZED",
    1: "INVALID_CANDIDATE",
    2: "PARENT_MISMATCH",
    3: "OWNER_MISMATCH",
    4: "BASE_MISMATCH",
    5: "DELTA_MISMATCH",
    6: "ROOT_SET_MISMATCH",
    7: "STAGED_ROOT_MISMATCH",
    8: "CONFLICT",
    9: "FOREIGN_MANAGED_WRITE",
    255: "INVALID_REQUEST",
}

_ERROR_NAMES = {
    1: "INVALID_ARGUMENT",
    2: "IO",
    3: "TOO_LARGE",
    4: "INTERNAL",
}

C_HASH = ctypes.c_uint8 * HASH_BYTES


class CCollapseRequest(ctypes.Structure):
    _fields_ = [
        ("candidate_state", ctypes.c_uint8),
        ("has_conflicts", ctypes.c_uint8),
        ("has_foreign_managed_writes", ctypes.c_uint8),
        ("reserved", ctypes.c_uint8),
        ("expected_parent", C_HASH),
        ("candidate_parent", C_HASH),
        ("expected_owner", C_HASH),
        ("candidate_owner", C_HASH),
        ("expected_base", C_HASH),
        ("candidate_base", C_HASH),
        ("expected_delta", C_HASH),
        ("candidate_delta", C_HASH),
        ("expected_root_set", C_HASH),
        ("candidate_root_set", C_HASH),
        ("expected_staged_root", C_HASH),
        ("actual_staged_root", C_HASH),
    ]


@dataclass(frozen=True, slots=True)
class CollapseInput:
    candidate_state: str
    has_conflicts: bool
    has_foreign_managed_writes: bool
    expected_parent: bytes
    candidate_parent: bytes
    expected_owner: bytes
    candidate_owner: bytes
    expected_base: bytes
    candidate_base: bytes
    expected_delta: bytes
    candidate_delta: bytes
    expected_root_set: bytes
    candidate_root_set: bytes
    expected_staged_root: bytes
    actual_staged_root: bytes


def _library_candidates() -> Iterable[Path]:
    configured = os.environ.get("WORLDLINE_CORE_LIB")
    if configured:
        yield Path(configured).expanduser()
    # Resolve relative to this module so an alternate HOME cannot hide the proved library:
    # runtime/worldline/core.py sits under the source tree (lib/ sibling of runtime/) and under
    # the installed tree (library beside runtime/).
    package_root = Path(__file__).resolve().parents[2]
    yield package_root / "lib/libworldline_core.so"
    yield package_root / "libworldline_core.so"
    yield Path.home() / ".local/lib/worldline/libworldline_core.so"


def hash_bytes_from_id(value: str) -> bytes:
    if not value.startswith("sha256:"):
        raise WorldlineError("INVALID_HASH", f"expected sha256 identity: {value}")
    try:
        result = bytes.fromhex(value.removeprefix("sha256:"))
    except ValueError as exc:
        raise WorldlineError("INVALID_HASH", f"invalid SHA-256 identity: {value}") from exc
    if len(result) != HASH_BYTES:
        raise WorldlineError("INVALID_HASH", f"invalid SHA-256 identity length: {value}")
    return result


def hash_id(value: bytes) -> str:
    if len(value) != HASH_BYTES:
        raise WorldlineError("INVALID_HASH", "digest is not 32 bytes")
    return f"sha256:{value.hex()}"


class Core:
    _shared: "Core | None" = None
    _shared_lock = Lock()

    def __init__(self, library: Path | None = None) -> None:
        selected = library
        if selected is None:
            selected = next((path for path in _library_candidates() if path.is_file()), None)
        if selected is None:
            raise CoreUnavailable(
                "libworldline_core.so was not found",
                searched=[str(path) for path in _library_candidates()],
            )
        try:
            self.library_path = selected.resolve(strict=True)
            self._lib = ctypes.CDLL(str(self.library_path), use_errno=True)
        except (OSError, RuntimeError) as exc:
            raise CoreUnavailable("libworldline_core.so could not be loaded", path=str(selected), error=str(exc)) from exc
        self._configure()

    @classmethod
    def shared(cls) -> "Core":
        with cls._shared_lock:
            if cls._shared is None:
                cls._shared = cls()
            return cls._shared

    def _configure(self) -> None:
        pointer = ctypes.c_void_p
        self._lib.wl_hash_file.argtypes = [pointer, ctypes.c_size_t, pointer]
        self._lib.wl_hash_file.restype = ctypes.c_int
        self._lib.wl_hash_bytes.argtypes = [pointer, ctypes.c_size_t, pointer]
        self._lib.wl_hash_bytes.restype = ctypes.c_int
        self._lib.wl_world_id.argtypes = [pointer] * 7
        self._lib.wl_world_id.restype = ctypes.c_int
        self._lib.wl_causal_link.argtypes = [pointer, pointer, pointer]
        self._lib.wl_causal_link.restype = ctypes.c_int
        self._lib.wl_receipt_link.argtypes = [pointer, pointer, pointer]
        self._lib.wl_receipt_link.restype = ctypes.c_int
        self._lib.wl_transition_allowed.argtypes = [ctypes.c_uint8, ctypes.c_uint8]
        self._lib.wl_transition_allowed.restype = ctypes.c_uint8
        self._lib.wl_collapse_decide.argtypes = [ctypes.POINTER(CCollapseRequest)]
        self._lib.wl_collapse_decide.restype = ctypes.c_uint8

    @staticmethod
    def _checked(code: int, operation: str) -> None:
        if code:
            name = _ERROR_NAMES.get(code, f"UNKNOWN_{code}")
            raise WorldlineError(f"CORE_{name}", f"proved core rejected {operation}", {"status": code})

    @staticmethod
    def _array(value: bytes) -> C_HASH:
        if len(value) != HASH_BYTES:
            raise WorldlineError("INVALID_HASH", "core input digest is not 32 bytes")
        return C_HASH.from_buffer_copy(value)

    def hash_bytes(self, data: bytes) -> bytes:
        output = C_HASH()
        if data:
            source = (ctypes.c_uint8 * len(data)).from_buffer_copy(data)
            address = ctypes.cast(source, ctypes.c_void_p)
        else:
            source = None
            address = ctypes.c_void_p()
        self._checked(self._lib.wl_hash_bytes(address, len(data), output), "byte hash")
        return bytes(output)

    def hash_file(self, path: str | bytes | os.PathLike[str] | os.PathLike[bytes]) -> bytes:
        encoded = os.fsencode(path)
        source = (ctypes.c_uint8 * len(encoded)).from_buffer_copy(encoded)
        output = C_HASH()
        self._checked(
            self._lib.wl_hash_file(ctypes.cast(source, ctypes.c_void_p), len(encoded), output),
            "file hash",
        )
        return bytes(output)

    def world_id(self, components: Mapping[str, bytes]) -> bytes:
        names = ("parent", "filesystem", "config", "repository", "environment", "evidence")
        arrays = [self._array(components[name]) for name in names]
        output = C_HASH()
        self._checked(self._lib.wl_world_id(*arrays, output), "world identity")
        return bytes(output)

    def causal_link(self, previous: bytes, event_root: bytes) -> bytes:
        output = C_HASH()
        self._checked(
            self._lib.wl_causal_link(self._array(previous), self._array(event_root), output),
            "causal link",
        )
        return bytes(output)

    def receipt_link(self, previous: bytes, receipt_root: bytes) -> bytes:
        output = C_HASH()
        self._checked(
            self._lib.wl_receipt_link(self._array(previous), self._array(receipt_root), output),
            "receipt link",
        )
        return bytes(output)

    def transition_allowed(self, from_state: str, to_state: str) -> bool:
        try:
            source = STATE_CODES[from_state]
            target = STATE_CODES[to_state]
        except KeyError as exc:
            raise WorldlineError("INVALID_STATE", f"unknown world state: {exc.args[0]}") from exc
        return bool(self._lib.wl_transition_allowed(source, target))

    def collapse_decide(self, value: CollapseInput) -> str:
        try:
            state = STATE_CODES[value.candidate_state]
        except KeyError as exc:
            raise WorldlineError("INVALID_STATE", f"unknown candidate state: {value.candidate_state}") from exc
        request = CCollapseRequest(
            state,
            int(value.has_conflicts),
            int(value.has_foreign_managed_writes),
            0,
            self._array(value.expected_parent),
            self._array(value.candidate_parent),
            self._array(value.expected_owner),
            self._array(value.candidate_owner),
            self._array(value.expected_base),
            self._array(value.candidate_base),
            self._array(value.expected_delta),
            self._array(value.candidate_delta),
            self._array(value.expected_root_set),
            self._array(value.candidate_root_set),
            self._array(value.expected_staged_root),
            self._array(value.actual_staged_root),
        )
        code = int(self._lib.wl_collapse_decide(ctypes.byref(request)))
        return COLLAPSE_DECISIONS.get(code, f"UNKNOWN_{code}")
