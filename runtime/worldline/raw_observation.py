"""Owned raw-capture encoding, with no classification or provenance authority.

Only the explicit retained-evaluation path supplies observers. A successful
callback means these observations were retained, not that their source was
authenticated, a read was stable, or an evaluation completed.
"""
from __future__ import annotations

import base64
import subprocess
import time


class ObservationRetentionError(RuntimeError):
    pass


class ProcessAcquisitionCancelled(RuntimeError):
    """An owned query was cancelled, distinct from its original timeout."""
    def __init__(self, argv):
        super().__init__('OWNED_PROCESS_ACQUISITION_CANCELLED')
        self.argv = argv
        self.output = self.stderr = self.returncode = self.pid = None


def observed_process_run(
    argv, *, observer=None, details=None, stdin=subprocess.DEVNULL,
    stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    timeout=None, env=None, cwd=None, cancel_event=None,
):
    """Own a binary command and retain its complete observed completion.

    The caller's original timeout still governs communication. Cancellation
    addresses only this Popen child. Killing it is not an EOF or wait: those
    facts are recorded only after communication and the actual wait return.
    An uncompleted drain remains uncompleted; no finite cleanup, descendants,
    authentication or kernel-supervision guarantee follows from this helper.
    """
    process = None
    captured_stdout = captured_stderr = None
    communication_completed = wait_return_observed = False
    actual_wait_return = None
    metadata = dict(details or {})

    def note(primary, label, secondary):
        primary.add_note(label + ': ' + type(secondary).__qualname__ + ': ' + str(secondary))

    def close_streams(primary=None):
        if process is None:
            return
        for stream in (process.stdin, process.stdout, process.stderr):
            if stream is None:
                continue
            try:
                stream.close()
            except BaseException as failure:
                if primary is None:
                    raise
                note(primary, 'owned command stream close also failed', failure)

    def observation(returned, primary=None):
        return {
            **metadata, 'processReturnObserved': returned,
            'stdout': optional_bytes(captured_stdout),
            'stderr': optional_bytes(captured_stderr),
            'returncode': actual_wait_return if returned else None,
            'exception': None if primary is None else exception_observation(primary),
            'processCreatedObserved': process is not None,
            'processPidObserved': None if process is None else process.pid,
            'processWaitReturnObserved': wait_return_observed,
            'processWaitReturncode': actual_wait_return,
            'stdoutReachedEof': communication_completed and stdout == subprocess.PIPE,
            'stderrReachedEof': communication_completed and stderr == subprocess.PIPE,
            'cancellationObserved': isinstance(primary, ProcessAcquisitionCancelled),
        }

    try:
        process = subprocess.Popen(
            argv, stdin=stdin, stdout=stdout, stderr=stderr, env=env, cwd=cwd,
        )
        # Like subprocess.run, the communication timeout begins after Popen.
        deadline = None if cancel_event is None or timeout is None else time.monotonic() + timeout
        while True:
            remaining = None if deadline is None else deadline - time.monotonic()
            if remaining is not None and remaining <= 0:
                raise subprocess.TimeoutExpired(argv, timeout,
                    output=captured_stdout, stderr=captured_stderr)
            if cancel_event is not None and cancel_event.is_set():
                raise ProcessAcquisitionCancelled(argv)
            # Cancellation checks use the existing sampler polling interval;
            # these retries never extend the original communication deadline.
            # Without cancellation use the original communicate call exactly,
            # including TimeoutExpired.timeout and zero-timeout behavior.
            quantum = timeout
            if cancel_event is not None:
                quantum = 0.1 if remaining is None else min(remaining, 0.1)
            try:
                captured_stdout, captured_stderr = process.communicate(timeout=quantum)
                communication_completed = True
                break
            except subprocess.TimeoutExpired as poll:
                captured_stdout, captured_stderr = poll.output, poll.stderr
                if cancel_event is None:
                    raise
        actual_wait_return = process.wait()
        wait_return_observed = True
        result = subprocess.CompletedProcess(argv, actual_wait_return,
            captured_stdout, captured_stderr)
        if check:
            result.check_returncode()
        close_streams()
    except BaseException as primary:
        if process is not None:
            if not communication_completed:
                try:
                    if process.poll() is None:
                        process.kill()
                except BaseException as failure:
                    note(primary, 'owned command termination also failed', failure)
                try:
                    captured_stdout, captured_stderr = process.communicate()
                    communication_completed = True
                except BaseException as failure:
                    note(primary, 'owned command full drain also failed', failure)
            try:
                actual_wait_return = process.wait()
                wait_return_observed = True
            except BaseException as failure:
                note(primary, 'owned command wait also failed', failure)
            close_streams(primary)
        if isinstance(primary, (subprocess.TimeoutExpired, ProcessAcquisitionCancelled)):
            primary.output, primary.stderr = captured_stdout, captured_stderr
        if isinstance(primary, ProcessAcquisitionCancelled):
            primary.returncode = actual_wait_return
            primary.pid = None if process is None else process.pid
        if observer is not None:
            try:
                retain_observation(observer, observation(False, primary))
            except BaseException as secondary:
                note(primary, 'owned process observation retention also failed', secondary)
                primary._worldline_retention_failed = True
        raise
    if observer is not None:
        retain_observation(observer, observation(True))
    return result


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
