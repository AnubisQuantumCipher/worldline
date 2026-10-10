"""Lossless diagnostic encoding with incremental output and private row spooling.

This is an observer, never an authority producer. Owned ABI bytes are copied by
the same bytes(value) operation as the original observer; foreign pointer targets
are never read. Each such snapshot is encoded before the next value is visited.
Large byte/string values are encoded in chunks. No value, field or repetition is
omitted, replaced by a digest, deduplicated, capped or normalized.

The complete row is serialized into an anonymous private temporary file before
any row output. Thus unsupported values cannot emit a half-encoded row. The
writer still latches failures in its caller. Scratch space includes the current
owned ABI snapshot and scalar encoding, not a cloned tree or complete JSON row;
this does not establish a constant bound for arbitrary integers or ABI objects.
"""
from __future__ import annotations

import base64
import ctypes
import dataclasses
import json
import os
from pathlib import Path
import tempfile


# JACKAL exact parsed=3*16384 exact=49152, formal=false. This aligns intermediate
# Base64 chunks without imposing a limit on the captured value's full length.
_BYTE_BLOCK = 49152
_TEXT_BLOCK = 4096
_OUTPUT_BLOCK = 65536
_JSON = json.JSONEncoder(ensure_ascii=True, allow_nan=False, separators=(',', ':'))


def _literal(out, value):
    out.write(value)


def _string(out, value):
    _literal(out, b'"')
    for start in range(0, len(value), _TEXT_BLOCK):
        # Chunking Python characters never divides a Unicode code point. The
        # original encoder's ASCII escapes (including surrogate pairs) remain.
        encoded = _JSON.encode(value[start:start + _TEXT_BLOCK])
        _literal(out, encoded[1:-1].encode('ascii'))
    _literal(out, b'"')


def _bytes(out, value):
    _literal(out, b'{"type":"bytes","base64":"')
    for start in range(0, len(value), _BYTE_BLOCK):
        _literal(out, base64.b64encode(value[start:start + _BYTE_BLOCK]))
    _literal(out, b'"}')


def _owned(out, value):
    """Write the original typed grammar in original depth-first field order.

    Iterators keep the traversal independent of Python call-stack depth. Actual
    cyclic containers still refuse; there is no new finite depth/length ceiling.
    Dataclass field access and dict/list iteration remain real access to the
    named values, before the original observed runtime call can proceed.
    """
    tasks = [('value', value)]
    active = set()
    while tasks:
        task = tasks.pop()
        kind = task[0]
        if kind == 'literal':
            _literal(out, task[1])
            continue
        if kind in ('sequence', 'mapping', 'fields'):
            _, owner_id, iterator, first = task
            try:
                item = next(iterator)
            except StopIteration:
                _literal(out, b'}}' if kind == 'fields' else b']}')
                active.remove(owner_id)
                continue
            if not first:
                _literal(out, b',')
            tasks.append((kind, owner_id, iterator, False))
            if kind == 'sequence':
                tasks.append(('value', item))
            elif kind == 'mapping':
                key, val = item
                _literal(out, b'[')
                tasks.extend([('literal', b']'), ('value', val),
                              ('literal', b','), ('value', key)])
            else:
                owner, field = item
                _string(out, field.name)
                _literal(out, b':')
                tasks.append(('value', getattr(owner, field.name)))
            continue

        val = task[1]
        if val is None or type(val) in (bool, int, float):
            _literal(out, _JSON.encode(val).encode('ascii'))
        elif type(val) is str:
            _string(out, val)
        elif type(val) is bytes:
            _bytes(out, val)
        elif isinstance(val, Path):
            _literal(out, b'{"type":"path","pathBytes":')
            _bytes(out, os.fsencode(val))
            _literal(out, b'}')
        elif type(val) in (list, tuple, dict) or (
                dataclasses.is_dataclass(val) and not isinstance(val, type)):
            owner_id = id(val)
            if owner_id in active:
                raise RecursionError('diagnostic value contains a cycle')
            active.add(owner_id)
            _literal(out, b'{"type":')
            if type(val) in (list, tuple):
                _string(out, type(val).__name__)
                _literal(out, b',"items":[')
                tasks.append(('sequence', owner_id, iter(val), True))
            elif type(val) is dict:
                _string(out, 'dict')
                _literal(out, b',"items":[')
                tasks.append(('mapping', owner_id, iter(val.items()), True))
            else:
                _string(out, type(val).__module__ + '.' + type(val).__qualname__)
                _literal(out, b',"fields":{')
                fields = map(lambda field, owner=val: (owner, field),
                             dataclasses.fields(val))
                tasks.append(('fields', owner_id, iter(fields), True))
        elif isinstance(val, (ctypes.Structure, ctypes.Array)):
            _literal(out, b'{"type":')
            _string(out, type(val).__name__)
            _literal(out, b',"abiBytes":')
            # Retain the original full owned-object snapshot operation. This is
            # a single snapshot of the current object, not pointer traversal.
            raw = bytes(val)
            _bytes(out, raw)
            del raw
            _literal(out, b'}')
        else:
            raise TypeError('diagnostic value not covered: ' + type(val).__qualname__)


def write_record(stream, site, values):
    """Complete encode before output; propagate the first failure to the latch."""
    row = tempfile.TemporaryFile(mode='w+b')
    primary = None
    try:
        _literal(row, b'{"site":')
        if type(site) is str:
            _string(row, site)
        else:
            # Original fixed call sites pass literal strings. Preserve the
            # original JSON site's other accepted forms without a new gate.
            for chunk in _JSON.iterencode(site):
                _literal(row, chunk.encode('ascii'))
        _literal(row, b',"values":')
        _owned(row, values)
        _literal(row, b'}')
        row.flush()
        row.seek(0)
        stream.write('WORLDLINE_DIAGNOSTIC ')
        while True:
            chunk = row.read(_OUTPUT_BLOCK)
            if not chunk:
                break
            stream.write(chunk.decode('ascii'))
        stream.write('\n')
        stream.flush()
    except BaseException as error:
        primary = error
        raise
    finally:
        try:
            row.close()
        except BaseException as error:
            if primary is None:
                raise
            primary.add_note('diagnostic spool close failed: ' +
                             type(error).__qualname__ + ': ' + str(error))
