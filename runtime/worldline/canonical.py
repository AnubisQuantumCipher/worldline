from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
from typing import Any

from .errors import WorldlineError

JsonValue = None | bool | int | str | list["JsonValue"] | dict[str, "JsonValue"]


def _validate(value: Any, location: str = "$") -> None:
    if value is None or isinstance(value, (bool, str)):
        if isinstance(value, str):
            try:
                value.encode("utf-8", "strict")
            except UnicodeEncodeError as exc:
                raise WorldlineError("NON_CANONICAL_JSON", f"invalid Unicode string at {location}") from exc
        return
    if isinstance(value, int):
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate(item, f"{location}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise WorldlineError("NON_CANONICAL_JSON", f"map key is not a string at {location}")
            _validate(key, f"{location}.<key>")
            _validate(item, f"{location}.{key}")
        return
    raise WorldlineError(
        "NON_CANONICAL_JSON",
        f"unsupported canonical JSON value at {location}: {type(value).__name__}",
    )


def canonical_bytes(value: JsonValue) -> bytes:
    _validate(value)
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8", "strict")


def parse_canonical(data: bytes) -> JsonValue:
    try:
        value = json.loads(data.decode("utf-8", "strict"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WorldlineError("INVALID_JSON", "invalid UTF-8 JSON") from exc
    _validate(value)
    if canonical_bytes(value) != data:
        raise WorldlineError("NON_CANONICAL_JSON", "JSON bytes are not canonical")
    return value


def fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def atomic_write(path: Path, data: bytes, *, mode: int = 0o600) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        os.fchmod(descriptor, mode)
        with os.fdopen(descriptor, "wb", closefd=True) as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        fsync_directory(path.parent)
    except BaseException:
        try:
            os.close(descriptor)
        except OSError:
            pass
        temporary.unlink(missing_ok=True)
        raise


def atomic_write_json(path: Path, value: JsonValue, *, mode: int = 0o600) -> None:
    atomic_write(path, canonical_bytes(value), mode=mode)
