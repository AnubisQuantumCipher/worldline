from __future__ import annotations

import ctypes
import errno
import os
from pathlib import Path
import tempfile
from typing import Any

from ..canonical import fsync_directory
from ..errors import WorldlineError

_AT_FDCWD = -100
_RENAME_EXCHANGE = 2


class AtomicExchange:
    def __init__(self) -> None:
        self._libc = ctypes.CDLL(None, use_errno=True)
        function = getattr(self._libc, "renameat2", None)
        if function is None:
            raise WorldlineError("RENAME_EXCHANGE_UNAVAILABLE", "libc does not expose renameat2")
        function.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        function.restype = ctypes.c_int
        self._renameat2 = function

    def exchange(
        self,
        first: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        second: str | bytes | os.PathLike[str] | os.PathLike[bytes],
    ) -> None:
        first_raw = os.fsencode(first)
        second_raw = os.fsencode(second)
        result = self._renameat2(_AT_FDCWD, first_raw, _AT_FDCWD, second_raw, _RENAME_EXCHANGE)
        if result != 0:
            error = ctypes.get_errno()
            code = "RENAME_EXCHANGE_UNAVAILABLE" if error in (errno.ENOSYS, errno.EINVAL, errno.EOPNOTSUPP) else "ATOMIC_EXCHANGE_FAILED"
            raise WorldlineError(
                code,
                f"renameat2(RENAME_EXCHANGE) failed: {os.strerror(error)}",
                {"errno": error, "first": os.fsdecode(first_raw), "second": os.fsdecode(second_raw)},
            )
        fsync_directory(Path(os.fsdecode(os.path.dirname(first_raw))))
        if os.path.dirname(second_raw) != os.path.dirname(first_raw):
            fsync_directory(Path(os.fsdecode(os.path.dirname(second_raw))))

    @classmethod
    def capability(cls, directory: Path | None = None) -> dict[str, Any]:
        try:
            adapter = cls()
            parent = directory or Path("/tmp")
            with tempfile.TemporaryDirectory(prefix="worldline-exchange-probe-", dir=parent) as temporary:
                first = Path(temporary) / "first"
                second = Path(temporary) / "second"
                first.write_bytes(b"first")
                second.write_bytes(b"second")
                adapter.exchange(first, second)
                if first.read_bytes() != b"second" or second.read_bytes() != b"first":
                    raise WorldlineError("ATOMIC_EXCHANGE_FAILED", "renameat2 probe did not exchange both paths")
        except (OSError, WorldlineError) as exc:
            reason = exc.message if isinstance(exc, WorldlineError) else str(exc)
            return {"state": "UNAVAILABLE", "reason": reason}
        return {"state": "AVAILABLE", "operation": "renameat2(RENAME_EXCHANGE)"}
