"""Explicit qualified control-source observers; no startup/effect authority.

Registration is invoked by the selected isolated control entry, never by an
installation flag, environment fallback or ordinary runtime constructor. No
registration or attachment writes a file. The operator precreates output dirs.
"""
from pathlib import Path
import os
import sys
import types
from .protected_startup import require, exact_json

_ENROLLMENT = None
_SOURCE = None
_EXPORTER = None
_COMMAND = None
_RECORDERS = {}
_PUBLISHED = set()
_WORKER_CALLBACK = None
_WORKER_CALLBACK_PATH = None
_WORKER_CALLBACK_RAW = None


def register_from_source(path):
    global _ENROLLMENT, _SOURCE, _EXPORTER, _COMMAND
    require(_ENROLLMENT is None, 'CUSTODY_CONTROL_OBSERVER_ALREADY_REGISTERED')
    approved = sys.modules.get('_worldline_approved_source_loader')
    require(approved is not None, 'CUSTODY_CONTROL_EARLY_SOURCE_REQUIRED')
    source = approved.current()
    source.check()
    raw = source.file(str(path), ('DATA',))
    enrollment = exact_json(raw)
    require(type(enrollment) is dict and set(enrollment) == {
        'schema', 'installation', 'journal', 'export_directory', 'command_prefix', 'entry'}
        and enrollment['schema'] == 'worldline.custody-control-observer-enrollment-v2',
        'CUSTODY_CONTROL_OBSERVER_COMPLETE_ENROLLMENT_REQUIRED')
    require(enrollment['entry'] == str(Path(sys.argv[0]))
        and type(enrollment['command_prefix']) is list
        and enrollment['command_prefix']
        and all(type(value) is str for value in enrollment['command_prefix']),
        'CUSTODY_CONTROL_ACTUAL_ENTRY_COMMAND_REQUIRED')
    source.file(enrollment['entry'], ('ENTRY',))
    command_raw = Path('/proc/self/cmdline').read_bytes()
    require(command_raw.endswith(b'\0'), 'CUSTODY_CONTROL_KERNEL_ARGV_TERMINATOR_REQUIRED')
    command = [os.fsdecode(value) for value in command_raw[:-1].split(b'\0')]
    prefix = enrollment['command_prefix']
    require(command[:len(prefix)] == prefix, 'CUSTODY_CONTROL_ACTUAL_KERNEL_COMMAND_PREFIX_CHANGED')
    _COMMAND = command
    exporter_path = Path(__file__).parent.parent.parent / 'protected-root/custody_runtime_controls_v35.py'
    code = source.compile_source(str(exporter_path), '_worldline_custody_control_exporter')
    module = types.ModuleType('_worldline_custody_control_exporter')
    module.__file__ = str(exporter_path)
    module.__dict__['__builtins__'] = __builtins__
    exec(code, module.__dict__)
    source.check()
    _SOURCE, _EXPORTER, _ENROLLMENT = source, module, enrollment

def register_worker_control(callback):
    """Register one actual selected control-source callback, not a runtime flag."""
    global _WORKER_CALLBACK, _WORKER_CALLBACK_PATH, _WORKER_CALLBACK_RAW
    require(_ENROLLMENT is not None and _WORKER_CALLBACK is None
            and type(callback) is types.FunctionType,
            'CUSTODY_CONTROL_SELECTED_WORKER_CALLBACK_REQUIRED')
    _SOURCE.check()
    path = str(Path(callback.__code__.co_filename).resolve(strict=True))
    raw = _SOURCE.file(path, ('SOURCE', 'ENTRY'))
    _WORKER_CALLBACK, _WORKER_CALLBACK_PATH, _WORKER_CALLBACK_RAW = callback, path, raw


async def observe_admitted_worker(service, record, output_lock):
    """Expose actual admitted objects only to the explicitly enrolled control."""
    if _WORKER_CALLBACK is None:
        return
    _SOURCE.check()
    require(_SOURCE.file(_WORKER_CALLBACK_PATH, ('SOURCE', 'ENTRY')) == _WORKER_CALLBACK_RAW,
            'CUSTODY_CONTROL_WORKER_CALLBACK_SOURCE_CHANGED')
    journal = service.owner.custody_journal
    recorder = getattr(journal, '_control_capture', None)
    require(recorder is not None and recorder in _RECORDERS.values()
            and str(journal.path) == _ENROLLMENT['journal']
            and journal.spec['installation_id'] == _ENROLLMENT['installation'],
            'CUSTODY_CONTROL_ACTUAL_ADMITTED_WORKER_REQUIRED')
    await _WORKER_CALLBACK(service, record, output_lock)
    _SOURCE.check()




_FRONT_CALLBACK = None
_FRONT_CALLBACK_PATH = None
_FRONT_CALLBACK_RAW = None


def register_front_control(callback):
    """Enroll one callback from the actual selected isolated control source."""
    global _FRONT_CALLBACK, _FRONT_CALLBACK_PATH, _FRONT_CALLBACK_RAW
    require(_ENROLLMENT is not None and _FRONT_CALLBACK is None
            and type(callback) is types.FunctionType,
            'CUSTODY_CONTROL_SELECTED_FRONT_CALLBACK_REQUIRED')
    _SOURCE.check()
    path = str(Path(callback.__code__.co_filename).resolve(strict=True))
    raw = _SOURCE.file(path, ('SOURCE', 'ENTRY'))
    _FRONT_CALLBACK, _FRONT_CALLBACK_PATH, _FRONT_CALLBACK_RAW = callback, path, raw


async def observe_admitted_front(front, slot):
    """Call the enrolled producer before handoff, using actual admitted custody."""
    if _FRONT_CALLBACK is None:
        return
    _SOURCE.check()
    require(_SOURCE.file(_FRONT_CALLBACK_PATH, ('SOURCE', 'ENTRY')) == _FRONT_CALLBACK_RAW,
            'CUSTODY_CONTROL_FRONT_CALLBACK_SOURCE_CHANGED')
    from .protected_root_worker import RootWorkerFront, RootWorkerSlot
    require(type(front) is RootWorkerFront and type(slot) is RootWorkerSlot
            and slot.front is front and front.slots.get(slot.operation) is slot
            and front.phase == 'FRONT_OWNED' and slot.request is slot.owned.retained_peer,
            'CUSTODY_CONTROL_ACTUAL_ADMITTED_FRONT_SLOT_REQUIRED')
    slot.intact()
    journal = front.custody_journal
    recorder = getattr(journal, '_control_capture', None)
    require(recorder is not None and recorder in _RECORDERS.values()
            and str(journal.path) == _ENROLLMENT['journal']
            and journal.spec['installation_id'] == _ENROLLMENT['installation'],
            'CUSTODY_CONTROL_ACTUAL_ADMITTED_FRONT_REQUIRED')
    require(slot.owned.execution_ack is not None,
            'CUSTODY_CONTROL_ACTUAL_EXECUTION_ACK_REQUIRED')
    journal.require_event(slot.owned.execution_ack)
    await _FRONT_CALLBACK(front, slot)
    _SOURCE.check()


def attach_source_observer(journal):
    if _ENROLLMENT is None:
        return
    _SOURCE.check()
    require(journal.spec['installation_id'] == _ENROLLMENT['installation']
        and str(journal.path) == _ENROLLMENT['journal'],
        'CUSTODY_CONTROL_ACTUAL_JOURNAL_SOURCE_REQUIRED')
    key = _ENROLLMENT['export_directory']
    require(key not in _PUBLISHED, 'CUSTODY_CONTROL_OBSERVER_ALREADY_PUBLISHED')
    recorder = _RECORDERS.get(key)
    if recorder is None:
        recorder = _EXPORTER.ControlCapture(journal, key, _COMMAND)
        journal.output_observations = []
        _RECORDERS[key] = recorder
    else:
        require(recorder.journal.path == journal.path,
                'CUSTODY_CONTROL_RECONSTRUCTED_JOURNAL_PATH_CHANGED')
        recorder.journal = journal
        if not hasattr(journal, 'output_observations'):
            journal.output_observations = []
    require(getattr(journal, '_control_capture', None) in (None, recorder),
            'CUSTODY_CONTROL_JOURNAL_OBSERVER_CONFLICT')
    journal._control_capture = recorder


def source_observers():
    return tuple(_RECORDERS.values())


def operation_native_recorder(journal):
    """Only the actual already-enrolled custody owner may export native calls."""
    if _ENROLLMENT is None:return None
    _SOURCE.check()
    recorder=getattr(journal,'_control_capture',None)
    require(recorder is not None and recorder in _RECORDERS.values()
        and recorder.journal is journal and journal.source_lease is _SOURCE
        and journal.spec['installation_id']==_ENROLLMENT['installation']
        and str(journal.path)==_ENROLLMENT['journal'],
        'CUSTODY_CONTROL_ACTUAL_OPERATION_NATIVE_RECORDER_REQUIRED')
    return recorder.operation_native_call


def publish_source_observers():
    _SOURCE.check() if _SOURCE is not None else None
    for key, recorder in _RECORDERS.items():
        if key not in _PUBLISHED:
            recorder.publish()
            _PUBLISHED.add(key)
