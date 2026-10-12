"""Acquire historical syntax in separate actual protected readonly examiner frames.

All returned values are primitive observations, not source cleanliness, runtime
compatibility, parser authority, or report admission. Native replay owns those joins.
The historical files are data: they are never imported or executed by this module.
"""
from __future__ import annotations

import base64
import copy
from contextlib import nullcontext
import hashlib
import os
from pathlib import Path, PurePosixPath
import stat
import threading

from ..examiner_audit import MAX_TREE_BYTES, MAX_TREE_ENTRIES, _relative, _directory
from ..raw_observation import exception_observation, optional_bytes, cleanup_call
from ..trusted import TRUSTED_INTERPRETER
from .private_evaluator import (PrivateEvaluationSpec, PrivateEvaluator,
                                VERIFIER_MOUNT, MAX_EVALUATOR_SECONDS,
                                _read_examiner_source)
from .protected_report_provider import ProtectedReportProvider

INPUT_MOUNT = '/logical/worldline-syntax-input'
HELPER_NAME = 'protected_syntax_helper.py'
_DIR = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
_FILE = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK


class ProtectedSyntaxProvider(ProtectedReportProvider):
    """Same descriptor custody, but syntax artifacts are not bounded reports."""
    def _report_maximum(self, stat_size):
        return stat_size

    def _additional_source_files(self):
        root = Path(self.plan['roots'][0]['frozen'])
        directory = _directory(root)
        answer = []
        try:
            def visit(fd, prefix):
                for name in sorted(os.listdir(fd)):
                    member = prefix + name
                    info = os.stat(name, dir_fd=fd, follow_symlinks=False)
                    if stat.S_ISDIR(info.st_mode):
                        child = os.open(name, _DIR, dir_fd=fd)
                        try:
                            visit(child, member + '/')
                        finally:
                            cleanup_call(lambda: os.close(child))
                    else:
                        answer.append((str(root / member), None,
                            {'kind': 'readonly-input', 'path': INPUT_MOUNT + '/' + member,
                             'historicalPath': member}))
            visit(directory, '')
        finally:
            cleanup_call(lambda: os.close(directory))
        return answer


def _inventory(snapshot):
    """Original inventory storage grammar, without running original audit policy."""
    directories = snapshot['directories']
    rows = snapshot['files']
    if (type(directories) is not list or type(rows) is not list or
            directories != sorted(set(directories)) or '' not in directories or
            any(not _relative(path) for path in directories if path)):
        raise ValueError('audit directory inventory is malformed')
    if len(directories) + len(rows) > MAX_TREE_ENTRIES:
        raise ValueError('audit inventory exceeds existing entry bound')
    files, total = {}, 0
    for row in rows:
        if type(row) is not dict or set(row) != {'path', 'payloadB64'} or not _relative(row['path']):
            raise ValueError('audit file entry is malformed')
        path, encoded = row['path'], row['payloadB64']
        if (path in files or path in directories or type(encoded) is not str or
                len(encoded) > ((MAX_TREE_BYTES + 2) // 3) * 4):
            raise ValueError('audit file is duplicated or over bound')
        payload = base64.b64decode(encoded, validate=True)
        if base64.b64encode(payload).decode('ascii') != encoded:
            raise ValueError('audit file has a noncanonical byte encoding')
        total += len(payload)
        if total > MAX_TREE_BYTES:
            raise ValueError('audit files exceed existing byte bound')
        parent = str(PurePosixPath(path).parent)
        if ('' if parent == '.' else parent) not in directories:
            raise ValueError('audit file parent is absent')
        files[path] = payload
    return directories, files


def _parent(root, parts):
    fd = os.dup(root)
    try:
        for part in parts:
            child = os.open(part, _DIR, dir_fd=fd)
            os.close(fd)
            fd = child
        return fd
    except BaseException:
        cleanup_call(lambda: os.close(fd))
        raise


def _write(parent, name, payload, record):
    row = {'name': name, 'parentFd': parent, 'fd': None, 'writes': [],
           'bytes': optional_bytes(payload), 'fsyncReturn': None, 'closeReturn': None}
    record.append(row)
    fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                 0o444, dir_fd=parent)
    row['fd'] = fd
    try:
        offset = 0
        while offset < len(payload):
            count = os.write(fd, payload[offset:])
            row['writes'].append({'offset': offset, 'return': count, 'errno': 0})
            if count <= 0:
                raise OSError('historical source write made no progress')
            offset += count
        os.fsync(fd)
        row['fsyncReturn'] = 0
    except BaseException as error:
        row['exception'] = exception_observation(error)
        raise
    finally:
        def close():
            os.close(fd)
            row['closeReturn'] = 0
        cleanup_call(close)


def _stage(snapshot, root, record):
    directories, files = _inventory(snapshot)
    root.mkdir(mode=0o700)
    fd = _directory(root)
    try:
        for path in sorted((item for item in directories if item),
                           key=lambda item: (len(item.split('/')), item)):
            parts = path.split('/')
            parent = _parent(fd, parts[:-1])
            try:
                os.mkdir(parts[-1], mode=0o755, dir_fd=parent)
            finally:
                cleanup_call(lambda: os.close(parent))
        for path, payload in files.items():
            parts = path.split('/')
            parent = _parent(fd, parts[:-1])
            try:
                _write(parent, parts[-1], payload, record)
            finally:
                cleanup_call(lambda: os.close(parent))
    finally:
        cleanup_call(lambda: os.close(fd))


def acquire_protected_source_ast(systemd, *, historical_audit, parser_declaration,
                                  phase_invocations, phase_reports, work_directory,
                                  resource_properties=(),
                                  timeout_seconds=MAX_EVALUATOR_SECONDS,
                                  bubblewrap_executable=None,
                                  acquisition_observer=None, admission_guards=None):
    """Return full raw controllers for independently acquired BEFORE and AFTER.

    phase_invocations are independently retained original invocation-start operands.
    phase_reports supply already prepared original private report directories and
    bindings: {phase: {'directory': Path, 'binding': original_binding}}. No caller
    callback selects a helper, parser, interpreter, path mapping, or provider type.
    The caller hands this capture to native SourceSyntax; no Python success grant.
    """
    work = Path(work_directory)
    work.mkdir(mode=0o700)
    helper_read = {}
    helper = _read_examiner_source(Path(__file__).with_name(HELPER_NAME), helper_read)
    controller = {'schema': 'worldline-protected-source-syntax-v1',
                  'historicalAudit': copy.deepcopy(historical_audit),
                  'priorExpectedDeclaration': copy.deepcopy(parser_declaration),
                  'parserSource': {'path': str(Path(__file__).with_name(HELPER_NAME)),
                                   'read': helper_read, 'sha256': hashlib.sha256(helper).hexdigest()},
                  'phases': {}}
    try:
        for phase in ('before', 'after'):
            location = work / phase
            location.mkdir(mode=0o700)
            row = {'request': {'phase': phase,
                    'historicalRuntime': copy.deepcopy(historical_audit[phase]['runtime']),
                    'historicalRoster': copy.deepcopy(historical_audit[phase]['files']),
                    'invocation': copy.deepcopy(phase_invocations[phase]),
                    'privateReportBinding': copy.deepcopy(phase_reports[phase]['binding'])},
                   'staging': [], 'helperWrites': [], 'privateBindingRead': {},
                   'acquisitions': [],
                   'result': None, 'artifact': None}
            controller['phases'][phase] = row
            input_root = location / 'input'
            _stage(historical_audit[phase], input_root, row['staging'])
            verifier = location / 'verifier'
            verifier.mkdir(mode=0o700)
            verifier_fd = _directory(verifier)
            try:
                _write(verifier_fd, HELPER_NAME, helper, row['helperWrites'])
            finally:
                cleanup_call(lambda: os.close(verifier_fd))
            report = Path(phase_reports[phase]['directory'])
            _read_examiner_source(report / '.binding', row['privateBindingRead'])
            spec = PrivateEvaluationSpec(
                run_id=phase_invocations[phase]['invocationId'],
                roots={INPUT_MOUNT: input_root}, verifier_directory=verifier,
                argv=(TRUSTED_INTERPRETER, VERIFIER_MOUNT + '/' + HELPER_NAME),
                cwd=INPUT_MOUNT, report_directory=report, runtime=location / 'runtime',
                timeout_seconds=timeout_seconds, bubblewrap_executable=bubblewrap_executable,
                verifier_digests={HELPER_NAME: hashlib.sha256(helper).hexdigest()},
                protected_invocation=copy.deepcopy(phase_invocations[phase]))
            from ..evaluation_producer import capture
            acquisition_lock = threading.RLock()
            def observe(kind, occurrence, observation):
                with acquisition_lock:
                    row['acquisitions'].append({'kind': kind, 'occurrence': occurrence,
                                                'observation': capture(observation)})
                    if acquisition_observer is not None:
                        acquisition_observer(kind, occurrence, observation)
            guard = None if admission_guards is None else admission_guards[phase]
            with (nullcontext() if guard is None else guard):
                row['result'] = PrivateEvaluator(systemd).run(
                    spec, resource_properties=resource_properties,
                    _acquisition_observer=observe,
                    _admission_guard=guard,
                    _protected_provider_type=ProtectedSyntaxProvider)
            from ..raw_observation import private_return_observation
            report_directory = row['result'].get('reportDirectory')
            returned_observation = private_return_observation(row['result'])
            # The observer receives a mutable projection; retain this field first.
            directory_observation = (copy.deepcopy(returned_observation['reportDirectory'])
                                     if isinstance(report_directory, Path) else None)
            observe('private-process-return', 0, returned_observation)
            row['artifact'] = copy.deepcopy(
                row['result']['protectedProviderCapture']['report']['sealed']['bytes'])
            row['artifactSha256'] = hashlib.sha256(base64.b64decode(
                row['artifact']['payload'], validate=True)).hexdigest()
            if (isinstance(report_directory, Path) and
                    row['result'].get('reportDirectory') is report_directory):
                row['result'] = {**row['result'],
                                 'reportDirectory': directory_observation}
    except BaseException as error:
        controller['exception'] = exception_observation(error)
        error.protected_source_syntax_capture = controller
        raise
    return controller
