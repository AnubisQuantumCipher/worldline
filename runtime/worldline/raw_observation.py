"""Owned raw-capture encoding, with no classification or provenance authority.

Only the explicit retained-evaluation path supplies observers. A successful
callback means these observations were retained, not that their source was
authenticated, a read was stable, or an evaluation completed.
"""
from __future__ import annotations

import base64


class ObservationRetentionError(RuntimeError):
    pass


def optional_bytes(value):
    """Keep absent distinct from a present empty byte string."""
    if value is None:
        return None
    if type(value) not in (bytes, bytearray):
        raise ObservationRetentionError('RAW_OBSERVATION_BYTES_REQUIRED')
    return {'encoding': 'base64', 'payload': base64.b64encode(value).decode('ascii')}


def retain_observation(observer, record):
    """A capture failure must escape collector errors that become refusals."""
    try:
        observer(record)
    except BaseException as error:
        raise ObservationRetentionError('RAW_OBSERVATION_RETENTION_FAILED') from error


def retain_read(observer, payload, *, reached_eof, acquired, details=None):
    retain_observation(observer, {
        'schemaVersion': 1,
        'kind': 'raw-read',
        'bytes': optional_bytes(payload),
        'readReachedEof': reached_eof,
        'readReturned': acquired,
        'details': details,
    })


def exception_observation(error):
    # Retain the observed causal graph and notes, without recursive depth caps
    # or a claim that exception text authenticates the underlying producer.
    pending = [error]
    indexes = {id(error): 0}
    nodes = []
    for item in pending:
        links = {}
        for name in ('__cause__', '__context__'):
            linked = getattr(item, name, None)
            if linked is not None and id(linked) not in indexes:
                indexes[id(linked)] = len(pending)
                pending.append(linked)
            links[name] = None if linked is None else indexes[id(linked)]
        nodes.append({'exceptionType': type(item).__qualname__, 'exception': str(item),
                      'notes': list(getattr(item, '__notes__', ())),
                      'suppressContext': bool(item.__suppress_context__), **links})
    return {'schemaVersion': 1, 'kind': 'exception-observation',
            'exceptionType': type(error).__qualname__, 'exception': str(error),
            'exceptionGraph': nodes, 'root': 0}


def retention_failed(error):
    return isinstance(error, ObservationRetentionError) or getattr(
        error, '_worldline_retention_failed', False) is True


def retain_during_unwind(callback):
    """Keep a pending read error; mark any secondary capture failure to escape collectors."""
    import sys
    primary = sys.exception()
    try:
        return callback()
    except BaseException as secondary:
        if primary is None:
            raise
        primary.add_note('observation retention also failed: ' +
                         type(secondary).__qualname__ + ': ' + str(secondary))
        primary._worldline_retention_failed = True
        raise primary


def cleanup_call(callback):
    """Attempt cleanup without replacing the active read/retention exception."""
    import sys
    primary = sys.exception()
    try:
        return callback()
    except BaseException as secondary:
        if primary is None:
            raise
        primary.add_note('cleanup also failed: ' + type(secondary).__qualname__ +
                         ': ' + str(secondary))
        # The original exception remains active on leaving the finally block.
        return None


def observed_process_call(callback, observer, details):
    """Capture a subprocess result before a consumer parses or filters it."""
    try:
        result = callback()
    except BaseException as primary:
        try:
            retain_observation(observer, {
                **details, 'processReturnObserved': False,
                'stdout': optional_bytes(getattr(primary, 'output', None)),
                'stderr': optional_bytes(getattr(primary, 'stderr', None)),
                'returncode': None, 'exception': exception_observation(primary)})
        except BaseException as secondary:
            primary.add_note('available process observation retention also failed: ' +
                             type(secondary).__qualname__ + ': ' + str(secondary))
            primary._worldline_retention_failed = True
        raise
    retain_observation(observer, {
        **details, 'processReturnObserved': True,
        'stdout': optional_bytes(result.stdout), 'stderr': optional_bytes(result.stderr),
        'returncode': result.returncode, 'exception': None})
    return result


def cleanup_scope():
    from contextlib import contextmanager
    import sys
    @contextmanager
    def scope():
        primary = sys.exception()
        try:
            yield
        except BaseException as secondary:
            if primary is None:
                raise
            primary.add_note('cleanup also failed: ' + type(secondary).__qualname__ +
                             ': ' + str(secondary))
    return scope()


def guarded_cleanup(manager):
    """Wrap the known resource guard, whose exit never suppresses exceptions."""
    class Guard:
        def __enter__(self):
            return manager.__enter__()
        def __exit__(self, error_type, primary, traceback):
            if primary is None:
                return manager.__exit__(error_type, primary, traceback)
            try:
                manager.__exit__(error_type, primary, traceback)
            except BaseException as secondary:
                primary.add_note('resource guard cleanup also failed: ' +
                                 type(secondary).__qualname__ + ': ' + str(secondary))
            return False
    return Guard()


def private_return_observation(observed):
    """Encode the known backend Path field without changing its returned value."""
    import os
    from pathlib import Path
    result = {**observed, 'stdout': optional_bytes(observed.get('stdout')),
              'stderr': optional_bytes(observed.get('stderr'))}
    directory = observed.get('reportDirectory')
    if isinstance(directory, Path):
        result['reportDirectory'] = {'kind': 'filesystem-path-observation',
            'sourceType': type(directory).__qualname__,
            'bytes': optional_bytes(os.fsencode(directory))}
    return result
