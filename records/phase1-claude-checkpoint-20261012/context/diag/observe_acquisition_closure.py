"""Acquisition-closure operand observer for the Source20 first original error.

External observation only. It runs the ORIGINAL diagnostic main
(tests/revalidation_diagnostic.py) on the exact selected original method and
additionally retains, at every EngineFinalizationWriter._native_acquisition_state
call, the complete operands the Python side hands to the native predicate
wl_evaluation_acquisitions_closed_v1 (subject, owners, acquisitions), the
native answer, and -- when the answer is False -- a set of offline re-evaluations
of the same pure native predicate over reduced operand sets (bisection), so the
exact rejecting record/predicate can be named.  No product source is modified,
no accepted case is changed, and no completion value is invented: every number
here is what the native library returned for the operands recorded beside it.
"""
import sys
sys.dont_write_bytecode = True
import datetime
import hashlib
import importlib.util
import json
import os
import time
import traceback
from pathlib import Path

W = Path('/home/sicarii/Work/worldline-phase1-claude-20261012')
S = W / 'source'
OUT = Path(sys.argv[1])
SELECTED = (sys.argv[2] if len(sys.argv) > 2 else
            'test_revalidation_binding.OneCoherentEvaluation.test_a_failed_revalidation_does_not_speak')
assert len(sys.argv) in (2, 3)
sys.path[:0] = [str(S / 'runtime'), str(S / 'tests')]
import diagnostic_value_stream as values  # noqa: E402
assert Path(values.__file__).resolve() == S / 'tests/diagnostic_value_stream.py'

OUT.mkdir(mode=0o700, parents=True, exist_ok=False)


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def new_file(path):
    return os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600), 'wb')


def write_typed(path, value):
    with new_file(path) as stream:
        values._owned(stream, value)
        stream.write(b'\n')
        stream.flush()
        os.fsync(stream.fileno())


def write_json(path, value):
    with new_file(path) as stream:
        stream.write((json.dumps(value, indent=1, ensure_ascii=True, default=repr) + '\n').encode())
        stream.flush()
        os.fsync(stream.fileno())


def write_bytes(path, blob):
    with new_file(path) as stream:
        stream.write(blob)
        stream.flush()
        os.fsync(stream.fileno())


observer_errors = []


def latch(site, error):
    row = {'at': now(), 'site': site, 'type': type(error).__name__,
           'message': str(error), 'traceback': traceback.format_exc()}
    observer_errors.append(row)
    try:
        write_json(OUT / ('observer-error-%d.json' % len(observer_errors)), row)
    except BaseException as retained:  # pragma: no cover
        observer_errors.append({'site': 'error-retention', 'type': type(retained).__name__, 'message': str(retained)})


from worldline import finalization_writer as fw  # noqa: E402
from worldline.evaluation_policy import acquisitions_closed  # noqa: E402
from worldline.finalization_journal import encode  # noqa: E402
from worldline.evaluation_pending import text  # noqa: E402
from worldline.runner_lifecycle import allowed  # noqa: E402

ORIGINAL_STATE = fw.EngineFinalizationWriter._native_acquisition_state
COUNTER = [0]
SUMMARY = []


def native(core, subject, owners, acquired):
    try:
        return acquisitions_closed(core, subject, owners, acquired)
    except BaseException as error:
        return 'REFUSED:' + type(error).__name__ + ':' + str(error)


def record_kind_site(item):
    kind = item.get('kind') if isinstance(item, dict) else None
    observation = item.get('observation') if isinstance(item, dict) else None
    site = observation.get('site') if isinstance(observation, dict) else None
    return kind, site


def patched_state(self):
    COUNTER[0] += 1
    number = COUNTER[0]
    closed, owners = ORIGINAL_STATE(self)
    try:
        acquired = [item for items in self.raw_observations.values() for item in items]
        subject = getattr(self.start, 'subject', None)
        subject_text = None if subject is None else text(subject)
        directory = OUT / ('acquisition-state-%d' % number)
        directory.mkdir(mode=0o700)
        # Exactly the bytes the Python side hands to the native predicate.
        for name, value in (('subject', subject_text), ('owners', owners), ('acquisitions', acquired)):
            blob = encode(value)
            write_bytes(directory / (name + '.encoded.bin'), blob)
        write_typed(directory / 'operands.typed.json',
                    {'subject': subject_text, 'owners': owners, 'acquisitions': acquired,
                     'native_closed': closed, 'at': now(), 'pid': os.getpid()})
        kinds = {}
        for item in acquired:
            kind, site = record_kind_site(item)
            kinds[str((kind, site))] = kinds.get(str((kind, site)), 0) + 1
        report = {'call': number, 'at': now(), 'native_closed': closed,
                  'owner_count': len(owners), 'acquisition_count': len(acquired),
                  'acquisition_kind_site_counts': kinds,
                  'owner_python_side_fields': [
                      {key: owner.get(key) for key in (
                          'cleanupStarted', 'launcherPresent', 'launcherWaitObserved', 'launcherStreamsClosed',
                          'streamEofObserved', 'guardPresent', 'guardReleased', 'guardOwned',
                          'guardDecisionPresent', 'guardReleaseReturnObserved', 'timerAlive', 'samplerAlive',
                          'proxyPresent', 'proxyClosed', 'actualUnit', 'launcherReturncode',
                          'launcherReturncodeCapture', 'subject', 'activeControllerCalls',
                          'controllerCallsAfterClosure', 'threadErrors', 'tailErrors')}
                      for owner in owners],
                  'owner_stream_threads': [owner.get('streams') for owner in owners],
                  'owner_tail_threads': [owner.get('tailDrains') for owner in owners],
                  'owner_launcher_streams': [owner.get('launcherStreams') for owner in owners],
                  'owner_unclosed_commands_count': [len(owner.get('unclosedCommands') or []) for owner in owners]}
        core = self.core
        actions = {}
        for owner_index, owner in enumerate(owners):
            per_owner = {}
            for action in ('quiescent', 'finished', 'drain-tails', 'close-streams', 'streams-closed',
                           'guard-released', 'forget-owner', 'observe-manager', 'release-guard'):
                try:
                    per_owner[action] = allowed(action, owner, core=core)
                except BaseException as error:
                    per_owner[action] = 'REFUSED:' + type(error).__name__ + ':' + str(error)
            actions[str(owner_index)] = per_owner
        report['owner_lifecycle_policy'] = actions
        if closed is False:
            bisect = {
                'owners_only_no_acquisitions': native(core, subject_text, owners, []),
                'acquisitions_only_no_owners': native(core, subject_text, [], acquired),
                'no_subject': native(core, None, owners, acquired),
            }
            removal = []
            for index, item in enumerate(acquired):
                rest = acquired[:index] + acquired[index + 1:]
                kind, site = record_kind_site(item)
                removal.append({'index': index, 'kind': kind, 'site': site,
                                'native_closed_without_this_record': native(core, subject_text, owners, rest)})
            bisect['single_record_removal'] = removal
            by_kind = {}
            for key in sorted({record_kind_site(item) for item in acquired}, key=str):
                rest = [item for item in acquired if record_kind_site(item) != key]
                by_kind[str(key)] = native(core, subject_text, owners, rest)
            bisect['kind_site_removal'] = by_kind
            # Which records does the native predicate need for closure? Keep one
            # kind at a time together with the owners.
            keep_only = {}
            for key in sorted({record_kind_site(item) for item in acquired}, key=str):
                only = [item for item in acquired if record_kind_site(item) == key]
                keep_only[str(key)] = native(core, subject_text, owners, only)
            bisect['kind_site_keep_only'] = keep_only
            report['bisection'] = bisect
        write_json(directory / 'report.json', report)
        SUMMARY.append(report)
    except BaseException as error:
        latch('acquisition-state-%d' % number, error)
    return closed, owners


fw.EngineFinalizationWriter._native_acquisition_state = patched_state

original_code = None
primary = None
try:
    original = S / 'tests/revalidation_diagnostic.py'
    spec = importlib.util.spec_from_file_location('revalidation_diagnostic', original)
    diagnostic = importlib.util.module_from_spec(spec)
    sys.modules['revalidation_diagnostic'] = diagnostic
    spec.loader.exec_module(diagnostic)
    assert Path(diagnostic.__file__).resolve() == original
    sys.argv = [str(original), '-v', SELECTED]
    write_json(OUT / 'entry.json', {'at': now(), 'pid': os.getpid(), 'argv': sys.argv,
                                    'cwd': os.getcwd(), 'selected': SELECTED,
                                    'python': sys.version, 'executable': sys.executable,
                                    'environment': {k: os.environ.get(k) for k in (
                                        'WORLDLINE_CORE_LIB', 'WORLDLINE_BUILD', 'WORLDLINE_DAEMON_UID', 'PYTHONPATH',
                                        'TMPDIR', 'XDG_RUNTIME_DIR', 'DBUS_SESSION_BUS_ADDRESS', 'PATH')},
                                    'library': os.environ.get('WORLDLINE_CORE_LIB'),
                                    'library_sha256': (hashlib.sha256(Path(os.environ['WORLDLINE_CORE_LIB']).read_bytes()).hexdigest()
                                                       if os.environ.get('WORLDLINE_CORE_LIB') else None)})
    try:
        diagnostic.main()
    except SystemExit as outcome:
        original_code = outcome.code
except BaseException as error:
    primary = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
    latch('driver', error)
finally:
    try:
        write_json(OUT / 'terminal.json', {'at': now(), 'original_main_SystemExit': original_code,
                                           'primary': primary, 'observer_errors': observer_errors,
                                           'acquisition_state_calls': len(SUMMARY),
                                           'summary': SUMMARY})
    except BaseException as error:
        latch('terminal-retention', error)
raise SystemExit(original_code if type(original_code) is int else 1)
