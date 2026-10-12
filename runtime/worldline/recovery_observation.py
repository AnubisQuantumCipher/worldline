"""Complete owned collapse observation, separately from its native verdict.

This packet is a lossless archive of the values and their full retained raw
materials. Its custody must come from an actual protected producer; that integration is
open. The daemon's ability to produce/replay a packet cannot issue a witness.
Historical replay uses the retained inputs; fresh observation remains separate.
"""
from __future__ import annotations
import threading

from dataclasses import dataclass, fields

from .core import CollapseInput
from .errors import WorldlineError
from .evaluation_wire import OwnedRecord
from .completion_kernel import BoundValue, CaptureValue, CheckValue, HistoryValue
from .pending_kernel_v2 import Intent
from .finalization_values import (StartValue, InputValue, UnsealedResult,
    CaptureValue as FinalCaptureValue, ComponentsValue, SealValue, ClassifiedValue, SealedValue)
from .finalization_journal import encode, decode
from .model import World, WorldState
from .recovery_material import AuthorityMaterial
from .evaluation_history import EvaluationRecord, EvaluationCursor
from .owner_transitions import OwnerGrant, OwnerRequest
from .owner_retry_audit import UseReceipt, RetryAudit, FullScope
from .owner_collapse_data import OwnerCollapseData

_RECORDS = (CollapseInput, OwnedRecord, BoundValue, CaptureValue, CheckValue,
            HistoryValue, Intent, StartValue, InputValue, UnsealedResult,
            FinalCaptureValue, ComponentsValue, SealValue, ClassifiedValue,
            SealedValue, World, AuthorityMaterial, EvaluationRecord, EvaluationCursor,
            OwnerGrant, OwnerRequest, UseReceipt, RetryAudit, FullScope, OwnerCollapseData)


def archive(value):
    """Explicit DTO tags retain bytes, tuple/list shape and every record field."""
    def lift(item):
        kind = type(item)
        if kind in _RECORDS:
            return ['record', kind.__module__, kind.__name__,
                    [[field.name, lift(getattr(item, field.name))] for field in fields(kind)]]
        if kind is WorldState:
            return ['world-state', item.value]
        if kind is dict:
            if any(type(key) not in (str, bytes) for key in item):
                raise WorldlineError('RECOVERY_PACKET_KEY', 'a full capture key has no original grammar')
            return ['object', [[lift(key), lift(val)] for key, val in item.items()]]
        if kind is tuple:
            return ['tuple', [lift(val) for val in item]]
        if kind is list:
            return ['list', [lift(val) for val in item]]
        if item is None or kind in (bytes, bool, int, float, str):
            return ['atom', item]
        raise WorldlineError('RECOVERY_PACKET_TYPE', 'a full capture value has no original DTO grammar',
                            {'type': kind.__name__})
    return encode(lift(value))


def restore_archive(raw):
    """Decode full DTO bytes without giving those bytes custody or authority.

    Only the explicit local data classes are constructible. No import, eval,
    defaulted field, duplicate key or projected decision is admitted.
    """
    records = {(kind.__module__, kind.__name__): kind for kind in _RECORDS}

    def invalid():
        raise WorldlineError('RECOVERY_PACKET_ENCODING', 'the full recovery DTO grammar differs')

    def lower(item):
        if type(item) is not list or not item or type(item[0]) is not str:
            invalid()
        tag = item[0]
        if tag == 'record' and len(item) == 4:
            if type(item[1]) is not str or type(item[2]) is not str:
                invalid()
            kind = records.get((item[1], item[2]))
            if kind is None or type(item[3]) is not list:
                invalid()
            names = [field.name for field in fields(kind)]
            pairs = item[3]
            if (any(type(pair) is not list or len(pair) != 2 or type(pair[0]) is not str
                    for pair in pairs) or [pair[0] for pair in pairs] != names):
                invalid()
            return kind(**{name: lower(pair[1]) for name, pair in zip(names, pairs)})
        if len(item) != 2:
            invalid()
        value = item[1]
        if tag == 'world-state' and type(value) is str:
            try:
                return WorldState(value)
            except ValueError:
                invalid()
        if tag == 'object' and type(value) is list:
            result = {}
            for pair in value:
                if type(pair) is not list or len(pair) != 2:
                    invalid()
                key = lower(pair[0])
                if type(key) not in (str, bytes) or key in result:
                    invalid()
                result[key] = lower(pair[1])
            return result
        if tag in ('list', 'tuple') and type(value) is list:
            items = [lower(child) for child in value]
            return items if tag == 'list' else tuple(items)
        if tag == 'atom' and (value is None or type(value) in (bytes, bool, int, float, str)):
            return value
        invalid()

    if type(raw) is not bytes:
        invalid()
    try:
        answer = lower(decode(raw))
        if archive(answer) != raw:
            invalid()
        return answer
    except WorldlineError:
        raise
    except (KeyError, IndexError, AttributeError, TypeError, ValueError, OverflowError) as exc:
        raise WorldlineError('RECOVERY_PACKET_ENCODING',
                            'the full recovery DTO grammar differs') from exc


def capture_packet(*, values, primary, staged, agent, agent_record, inputs,
                   candidate, subject, witness, authoritative_requirement,
                   resulting_requirement, authoritative_roots, current_requirement=None, owner=None,
                   core=None):
    if type(values) is not CollapseInput or 'resulting_requirement' not in CollapseInput.__slots__:
        raise WorldlineError('RECOVERY_PACKET_ABI', 'the original resulting requirement is not carried')
    def selected(value):
        if value is None:
            return None
        from .evaluation_authority import SelectedEvaluation
        if type(value) is not SelectedEvaluation:
            raise WorldlineError('RECOVERY_PACKET_MATERIAL', 'complete retained raw authority material is absent')
        # Optional constructor compatibility does not fabricate capture data.
        material = getattr(value, 'authority_material', None)
        if type(material) is not AuthorityMaterial:
            raise WorldlineError('RECOVERY_PACKET_MATERIAL', 'complete retained raw authority material is absent')
        return {'context': value.context, 'source': value.source,
                'results': value.results, 'cursor': value.cursor,
                'capture': value.capture, 'typedRows': value.typed_rows,
                'retainedStream': value.retained_stream, 'observed': value.observed,
                'authorityMaterial': material}
    packet={'schema': 'worldline-collapse-observation-v2',
                    'values': values, 'primary': selected(primary), 'staged': selected(staged),
                    'agent': agent, 'agentRecord': agent_record, 'inputs': inputs,
                    'candidate': candidate, 'subject': subject, 'witness': witness,
                    'authoritativeRequirement': authoritative_requirement,
                    'currentRequirementArgument': current_requirement,
                    'resultingRequirement': resulting_requirement,
                    'authoritativeRoots': tuple(authoritative_roots)}
    if owner is not None:
        if type(owner) is not OwnerCollapseData:raise WorldlineError('OWNER_PACKET_TYPE','owner conjunction data differs')
        packet['schema']='worldline-collapse-observation-v3-owner';packet['owner']=owner
    raw = archive(packet)
    # Capture retains refusals as observations. Native packet completeness,
    # not this marshaller, decides every source/selection/projection join.
    if core is None:
        from .core import Core
        core = Core.shared()
    _inspect_packet(raw, core=core)
    return raw


@dataclass(frozen=True, slots=True)
class CollapseObservation:
    values: CollapseInput
    primary: object
    staged: object
    agent: object
    packet: bytes | None
    owner: object = None
    syntax_facts: bytes | None = None

    def decide(self, core, *, principal=None, syntax_context=None):
        if self.packet is not None:
            _native_projection_matches(self.packet, archive(self.values), core=core)
            return _native_packet(self.packet, core=core, syntax_facts=self.syntax_facts,
                                  principal=principal, syntax_context=syntax_context)
        if type(self.values) is not CollapseInput:
            raise WorldlineError('RECOVERY_OBSERVATION_INVALID', 'the complete owned observation is absent')
        # Keep this object, and every original prepared raw arena it references,
        # alive throughout the synchronous native call. No projected verdict.
        original=core.collapse_decide_with_evaluation(self.values,primary=self.primary,staged=self.staged,agent=self.agent)
        if original!='AUTHORIZED' or self.owner is None:return original
        if type(self.owner) is not OwnerCollapseData:raise WorldlineError('OWNER_PACKET_TYPE','owner conjunction data differs')
        reason=self.owner.decide(core,self.values)
        return 'AUTHORIZED' if reason=='READY' else 'OWNER_'+reason


_OWNER_PACKET_REASONS = (
    'MALFORMED', 'MATERIAL_REFUSED', 'INPUT_INVALID', 'BEFORE_NOT_AUTHORIZED',
    'PREFIX_CHANGED', 'AFTER_INVALID', 'ATTEMPT_NOT_COMPLETED_PASS',
    'USE_NOT_CONSUMED', 'CURRENT_BINDING_CHANGED', 'ORIGINAL_COLLAPSE_DENIED',
    'RESULTING_REQUIREMENT_ABSENT', 'REQUIREMENT_CHANGED', 'OWNER_SCOPE_MISMATCH',
    'OWNER_NOT_AUTHORIZED', 'RETRY_NOT_ADMITTED', 'READY',
)


_NATIVE_STACK_LOCK = threading.Lock()


def _with_native_stack(function, *arguments, extent):
    """Run one native packet call on a thread whose stack covers its arenas.

    The packet kernels declare their working arenas on the stack, sized from the
    complete input (Recovery_Material_Replay.Rebuild's arena is the packet length
    plus the retained material). On the default 8 MiB main-thread stack an 11.8 MB
    packet raised Storage_Error inside the kernel, which the C boundary returns as
    a transport refusal. The stack grows with the input (no size cap); the caller
    waits for the result, so native calls stay serialized as before, and the
    native answer or exception is returned unchanged.
    """
    size = (64 << 20) + 4 * extent
    size += -size % (1 << 16)
    outcome = {}

    def body():
        try:
            outcome['value'] = function(*arguments)
        except BaseException as error:  # re-raised unchanged on the calling thread
            outcome['error'] = error

    with _NATIVE_STACK_LOCK:
        previous = threading.stack_size()
        threading.stack_size(size)
        try:
            worker = threading.Thread(target=body, name='worldline-native-packet')
            worker.start()
        finally:
            threading.stack_size(previous)
    worker.join()
    if 'error' in outcome:
        raise outcome['error']
    return outcome['value']


def _native_projection_matches(raw, values, *, core):
    import ctypes as C
    try:
        call = core._lib.wl_recovery_packet_projection_matches_v1
    except AttributeError as exc:
        raise WorldlineError('RECOVERY_PACKET_ABI', 'selected kernel lacks complete projection join') from exc
    call.argtypes = [C.c_void_p, C.c_size_t, C.c_void_p, C.c_size_t]
    call.restype = C.c_uint8
    packet_owner = (C.c_uint8 * len(raw)).from_buffer_copy(raw)
    values_owner = (C.c_uint8 * len(values)).from_buffer_copy(values)
    if _with_native_stack(call, packet_owner, len(raw), values_owner, len(values),
                          extent=len(raw) + len(values)) != 1:
        raise WorldlineError('RECOVERY_PACKET_PROJECTION_CHANGED',
                            'the exposed original 35-field projection differs from the full packet')


def _inspect_packet(raw, *, core, syntax_facts=None):
    """Inspect original full bytes as data, without treating any result as permission."""
    import ctypes as C
    if type(raw) is not bytes:
        raise WorldlineError('RECOVERY_PACKET_ENCODING', 'the full recovery DTO grammar differs')
    try:
        call = (core._lib.wl_recovery_packet_decide_v1 if syntax_facts is None
                else core._lib.wl_recovery_packet_decide_with_facts_v1)
    except AttributeError as exc:
        raise WorldlineError('RECOVERY_PACKET_ABI',
                            'selected kernel has no complete recovery packet relation') from exc
    call.argtypes = ([C.c_void_p, C.c_size_t] +
        ([] if syntax_facts is None else [C.c_void_p, C.c_size_t]) +
        [C.POINTER(C.c_uint8), C.POINTER(C.c_uint32)])
    call.restype = C.c_uint8
    owned = (C.c_uint8 * len(raw)).from_buffer_copy(raw)
    collapse, owner = C.c_uint8(255), C.c_uint32(0xffffffff)
    if syntax_facts is None:
        status = int(_with_native_stack(call, owned, len(raw), C.byref(collapse), C.byref(owner),
                                        extent=len(raw)))
    else:
        if type(syntax_facts) is not bytes:
            raise WorldlineError('RECOVERY_SYNTAX_SOURCE_ENCODING', 'complete native capsule bytes are absent')
        facts = (C.c_uint8 * len(syntax_facts)).from_buffer_copy(syntax_facts)
        status = int(_with_native_stack(call, owned, len(raw), facts, len(syntax_facts),
                                        C.byref(collapse), C.byref(owner),
                                        extent=len(raw) + len(syntax_facts)))
    if status not in range(7):
        raise WorldlineError('RECOVERY_PACKET_NATIVE_INVALID',
                            'complete packet inspection transport is unavailable', {'status': status})
    return status, collapse.value, owner.value


@dataclass(frozen=True, slots=True)
class ReadonlySyntaxContext:
    """Borrow actual source-only resource handles, never target-role permission."""
    core: object
    systemd: object
    gate: object


def acquire_readonly_syntax_context(*, core, source_lease, spec, qualification_path=None):
    """Load independently qualified source admission without creating any ledger."""
    import json
    import os
    import stat
    from pathlib import Path
    import fcntl
    import tempfile
    import time
    from .linux.atomic import AtomicExchange
    from .admission import AdmissionAuthority, Floors, Gate, Ledger, ResourcePolicy
    from .linux.systemd import SystemdAdapter
    from .report import _open_directory_no_symlinks
    selected = (Path(spec['paths']['config']) / 'source-syntax-admission.json'
                if qualification_path is None else Path(qualification_path))
    raw = source_lease.file(str(selected), ('DATA',))
    source_lease.check()
    declaration = json.loads(raw)
    if (type(declaration) is not dict or set(declaration) != {'schema', 'selection', 'resources'}
            or declaration['schema'] != 'worldline-readonly-syntax-admission-v1'
            or declaration['selection'] != {
                'installation_id': spec['installation_id'], 'runtime': spec['runtime']}
            or core.library_path != Path(spec['runtime']['native_library'])):
        raise WorldlineError('RECOVERY_SYNTAX_SOURCE_SELECTION',
                            'source admission is not tied to the complete selected runtime')
    resources = declaration['resources']
    if (type(resources) is not dict or
            set(resources) != {'ledgerDirectory', 'policy', 'floors', 'paths'}):
        raise WorldlineError('RECOVERY_SYNTAX_SOURCE_CONFIGURATION',
                            'the independent shared source admission declaration differs')
    directory = Path(resources['ledgerDirectory'])
    descriptor = _open_directory_no_symlinks(directory)
    try:
        info = os.fstat(descriptor)
        if info.st_uid != os.getuid() or info.st_mode & 0o022:
            raise WorldlineError('RECOVERY_SYNTAX_SOURCE_LEDGER',
                                'the existing shared source ledger directory is not owned')
        directory_identity = (info.st_dev, info.st_ino)
        identities = {}
        for name in ('admission-ledger.json', 'admission.lock'):
            fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=descriptor)
            try:
                info = os.fstat(fd)
                if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o022:
                    raise WorldlineError('RECOVERY_SYNTAX_SOURCE_LEDGER',
                                        'the existing shared source ledger file is not owned')
                identities[name] = (info.st_dev, info.st_ino)
            finally:
                os.close(fd)
    finally:
        os.close(descriptor)
    class ExistingSourceLedger(Ledger):
        def __init__(self, existing):
            self.directory = existing
            self.path = existing / 'admission-ledger.json'
            self.lock_path = existing / 'admission.lock'
            self._active = None

        def _directory(self):
            fd = _open_directory_no_symlinks(self.directory)
            info = os.fstat(fd)
            if ((info.st_dev, info.st_ino) != directory_identity
                    or info.st_uid != os.getuid() or info.st_mode & 0o022):
                os.close(fd)
                raise WorldlineError('RESOURCE_STATE_UNKNOWN', 'source admission directory changed')
            return fd

        def _open(self, directory_fd, name, expected=None, *, writable=False):
            fd = os.open(name, (os.O_RDWR if writable else os.O_RDONLY)
                         | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=directory_fd)
            try:
                info = os.fstat(fd)
                current = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
                identity = (info.st_dev, info.st_ino)
                if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
                        or info.st_mode & 0o022
                        or identity != (current.st_dev, current.st_ino)
                        or expected is not None and identity != expected):
                    raise WorldlineError('RESOURCE_STATE_UNKNOWN', 'source admission file changed')
                return fd, identity
            except BaseException:
                os.close(fd)
                raise

        class _Locked(Ledger._Locked):
            def __enter__(locked):
                ledger = locked.ledger
                if ledger._active is not None:
                    raise WorldlineError('RESOURCE_STATE_UNKNOWN', 'source admission lock is already held')
                directory_fd = ledger._directory()
                try:
                    fd, _ = ledger._open(directory_fd, 'admission.lock',
                                         identities['admission.lock'], writable=True)
                    locked.handle = os.fdopen(fd, 'r+b')
                    fcntl.flock(locked.handle.fileno(), fcntl.LOCK_EX)
                    check, _ = ledger._open(directory_fd, 'admission.lock',
                                            identities['admission.lock'])
                    os.close(check)
                    check, identity = ledger._open(directory_fd, 'admission-ledger.json')
                    os.close(check)
                    ledger._active = (directory_fd, identity)
                    return locked
                except BaseException:
                    if locked.handle is not None:
                        locked.handle.close()
                        locked.handle = None
                    os.close(directory_fd)
                    raise

            def __exit__(locked, *exc):
                ledger = locked.ledger
                directory_fd = ledger._active[0]
                try:
                    return super().__exit__(*exc)
                finally:
                    ledger._active = None
                    os.close(directory_fd)

        def locked(self):
            return self._Locked(self)

        def _check(self):
            if self._active is None:
                raise WorldlineError('RESOURCE_STATE_UNKNOWN', 'source admission state is not locked')
            directory_fd, identity = self._active
            fresh = self._directory()
            os.close(fresh)
            fd, _ = self._open(directory_fd, 'admission.lock', identities['admission.lock'])
            os.close(fd)
            return self._open(directory_fd, 'admission-ledger.json', identity)

        def _load(self):
            # Reuse every original reservation/quantity/duplicate validation on
            # the owned, stable descriptor. The original missing-path fallback
            # cannot run: this descriptor stays open throughout Ledger._load.
            fd, _ = self._check()
            try:
                borrowed = object.__new__(Ledger)
                borrowed.path = Path('/proc/self/fd') / str(fd)
                values = Ledger._load(borrowed)
                check, _ = self._check()
                os.close(check)
                return values
            finally:
                os.close(fd)

        def _store(self, reservations):
            content = json.dumps({'schemaVersion': 1, 'updatedAtMs': int(time.time() * 1000),
                                  'reservations': [item.as_dict() for item in reservations]},
                                 indent=2) + '\n'
            check, identity = self._check()
            os.close(check)
            fd, temporary = tempfile.mkstemp(prefix='.admission-ledger-', dir=self.directory)
            try:
                os.fchmod(fd, 0o600)
                with os.fdopen(fd, 'w', encoding='utf-8') as stream:
                    fd = None
                    stream.write(content)
                    stream.flush()
                    os.fsync(stream.fileno())
                check, _ = self._check()
                os.close(check)
                # EXCHANGE requires both names to exist. Unlike os.replace it
                # can never recreate a disappeared shared ledger.
                AtomicExchange().exchange(temporary, self.path)
                displaced = os.stat(temporary, follow_symlinks=False)
                if (displaced.st_dev, displaced.st_ino) != identity:
                    AtomicExchange().exchange(temporary, self.path)
                    raise WorldlineError('RESOURCE_STATE_UNKNOWN', 'source admission ledger was replaced')
                new = os.stat(self.path, follow_symlinks=False)
                self._active = (self._active[0], (new.st_dev, new.st_ino))
                check, _ = self._check()
                os.close(check)
            finally:
                if fd is not None:
                    os.close(fd)
                os.unlink(temporary)
    authority = AdmissionAuthority(ExistingSourceLedger(directory),
        Floors.from_mapping(resources['floors']),
        paths={name: Path(path) for name, path in resources['paths'].items()})
    return ReadonlySyntaxContext(core, SystemdAdapter(),
                                 Gate(authority, ResourcePolicy.from_mapping(resources['policy'])))


def _syntax_inputs(raw, *, core, operation):
    """Own native complete original inputs; JSON decoding here is transport only."""
    import ctypes as C
    import json
    if type(raw) is not bytes:
        raise WorldlineError('RECOVERY_SYNTAX_SOURCE_ENCODING', 'complete original source bytes are absent')
    try:
        call = core._lib.wl_recovery_syntax_inputs_v1
    except AttributeError as exc:
        raise WorldlineError('RECOVERY_SYNTAX_SOURCE_ABI',
                            'selected kernel lacks the full native source input decoder') from exc
    call.argtypes = [C.c_void_p, C.c_size_t, C.c_uint8, C.c_void_p, C.c_size_t]
    call.restype = C.c_size_t
    owned = (C.c_uint8 * len(raw)).from_buffer_copy(raw)
    needed = int(call(owned, len(raw), int(operation), None, 0))
    if needed == C.c_size_t(-1).value:
        raise WorldlineError('RECOVERY_SYNTAX_SOURCE_ENCODING', 'native full source grammar differs')
    output = (C.c_uint8 * needed)()
    written = int(call(owned, len(raw), int(operation), output, needed))
    if written != needed:
        raise WorldlineError('RECOVERY_SYNTAX_SOURCE_ENCODING', 'native source transport extent changed')
    values = json.loads(bytes(output).decode('utf-8'))
    if type(values) is not list or any(type(value) is not str for value in values):
        raise WorldlineError('RECOVERY_SYNTAX_SOURCE_ABI', 'native source input transport shape differs')
    return [value.encode('utf-8') for value in values]


def _acquire_syntax(raw, *, operation, principal, core, syntax_context):
    import tempfile
    from pathlib import Path
    from .core import Core
    from .evaluation_producer import acquire_syntax_capsules
    if syntax_context is None and principal is not None:
        syntax_context = ReadonlySyntaxContext(principal.core,
                                               principal.controller.systemd,
                                               principal.controller.gate)
    selected_core = (syntax_context.core if core is None and syntax_context is not None
                     else Core.shared() if core is None else core)
    original_results = _syntax_inputs(raw, core=selected_core, operation=operation)
    if not original_results:
        return []
    if syntax_context is None:
        raise WorldlineError('RECOVERY_SYNTAX_RESOURCE_CONTEXT',
                            'actual source-only admission context is required for primitive acquisition')
    if syntax_context.core is not selected_core:
        raise WorldlineError('RECOVERY_SYNTAX_SOURCE_SELECTION', 'source and packet kernels differ')
    with tempfile.TemporaryDirectory(prefix='worldline-readonly-syntax-') as directory:
        return acquire_syntax_capsules(original_results,
            systemd=syntax_context.systemd, gate=syntax_context.gate,
            work_directory=Path(directory),
            source_context={'originalOperation': raw})


def acquire_syntax_facts(packet, *, principal=None, core=None, syntax_context=None):
    """Acquire primitive facts from the full unchanged original recovery packet."""
    return _acquire_syntax(packet, operation=False, principal=principal,
                          core=core, syntax_context=syntax_context)


def acquire_syntax_facts_from_original(raw, *, principal=None, core=None, syntax_context=None):
    """Acquire all original owner/journal/material facts from the full Operation archive."""
    return _acquire_syntax(raw, operation=True, principal=principal,
                          core=core, syntax_context=syntax_context)


def _native_packet_result(raw, *, core, syntax_facts=None, principal=None, syntax_context=None):
    """Run the exact complete relation, retaining independently acquired facts."""
    from .core import COLLAPSE_DECISIONS
    status, collapse, owner = _inspect_packet(raw, core=core, syntax_facts=syntax_facts)
    if syntax_facts is None and status not in (0, 5, 6):
        capsules = acquire_syntax_facts(raw, principal=principal, core=core,
                                       syntax_context=syntax_context)
        if capsules:
            from .operation_capture import archive as original_archive
            syntax_facts = original_archive(capsules)
            status, collapse, owner = _inspect_packet(raw, core=core, syntax_facts=syntax_facts)
    if status not in (5, 6):
        errors = {
            0: 'RECOVERY_PACKET_SCHEMA',
            1: 'RECOVERY_PACKET_SOURCE_CHANGED',
            2: 'RECOVERY_PACKET_SELECTION_CHANGED',
            3: 'RECOVERY_PACKET_AGENT_CHANGED',
            4: 'RECOVERY_PACKET_OWNER_CHANGED',
        }
        raise WorldlineError(errors[status], 'the complete native recovery packet relation refused',
                            {'status': status, 'collapse': collapse, 'owner': owner})
    if owner != 0xffffffff:
        if owner >= len(_OWNER_PACKET_REASONS):
            raise WorldlineError('RECOVERY_PACKET_NATIVE_INVALID', 'native owner reason differs')
        if _OWNER_PACKET_REASONS[owner] != 'READY':
            return 'OWNER_' + _OWNER_PACKET_REASONS[owner], syntax_facts
    reason = COLLAPSE_DECISIONS.get(collapse)
    if reason is None:
        raise WorldlineError('RECOVERY_PACKET_NATIVE_INVALID', 'native collapse reason differs')
    return reason, syntax_facts


def _native_packet(raw, *, core, syntax_facts=None, principal=None, syntax_context=None):
    """Native data redecision only: no custody/current capability or effect grant."""
    return _native_packet_result(raw, core=core, syntax_facts=syntax_facts,
        principal=principal, syntax_context=syntax_context)[0]


def _restore_selection_transport(saved, *, core):
    """Reconstruct the original typed arenas after whole-packet native replay.

    All choices below choose a transport constructor for native-verified saved
    values. This helper does not select a history head, compare two projections,
    classify a terminal, or grant collapse/recovery/receipt authority.
    """
    from dataclasses import asdict, replace
    from pathlib import Path
    from .evaluation_authority import SelectedEvaluation
    from .evaluation_wire import Authority, record
    from .evaluation_terminal import bytes_value, value_bytes
    from .evaluation_pending import identity
    from .raw_completion_kernel import RawCompletionKernel
    from .finalization_kernel import FinalizationKernel
    from .finalize import CheckDeclaration, check_declarations, required_roster
    from .completion_kernel import EXECUTION
    if saved is None:
        return None
    material = saved['authorityMaterial']
    if saved['source'] == 'finalization':
        packed = FinalizationKernel(Path(core.library_path)).prepare_finalization(
            material.finalization[1].value)
    else:
        capture, typed = saved['capture'], saved['typedRows']
        observed = saved['observed']
        initial, post = observed['captureContext'], observed['postMeasurement']
        policy = initial['requirement']
        required, empty = required_roster(policy)
        declarations = check_declarations(policy)
        # These are the original transport slots already rederived and checked
        # by the complete native material relation, never permission flags.
        if any(row.get('id') == 'verifiers-modified' and row.get('origin') == 'engine'
               for row in saved['results']):
            required = list(required) + ['verifiers-modified']
            declarations['verifiers-modified'] = CheckDeclaration('engine', None, False, origin='engine')
        declarations['evaluation-complete'] = CheckDeclaration('engine', None, False, origin='engine')
        authority, wires, projected = Authority(core), [], []
        states = {name.upper(): name for name in EXECUTION}
        for row in typed:
            payload = bytes_value(row.payload)
            declaration = bytes_value(row.declared)
            wire = record(payload, None if declaration is None else CheckDeclaration(**declaration), core=core)
            execution, verdict, _bundle, _report, _admitted = authority.evaluate(wire)
            wires.append(wire)
            projected.append(replace(row, state=states[execution],
                                     outcome=None if verdict == 'NONE' else verdict))
        epoch = initial['evaluationEpoch']
        measured = BoundValue(identity(initial['storeId']),
            identity(initial['measurement']['worldInstance']),
            identity(initial['measurement']['contentId']), identity(initial['run']),
            epoch.to_bytes((epoch.bit_length() + 7) // 8, 'little'),
            identity(policy['requirementHash']))
        journal, current, _history, _streams = material.terminal
        packed = RawCompletionKernel(Path(core.library_path)).prepare(
            journal, current=current, capture=capture, results=projected, wire_records=wires,
            required=tuple((identity(name), value_bytes(None if declarations.get(name) is None
                else asdict(declarations[name]))) for name in required),
            policy=('Explicit_Empty' if empty else 'Missing_Declaration') if not required else 'Required_Checks',
            measured_roots=(identity(initial['measurement']['observedContentRoot']),
                            identity(post['observedContentRoot'])),
            completion=(identity('evaluation-complete'), value_bytes(asdict(declarations['evaluation-complete']))),
            measured_binding=measured)
    return SelectedEvaluation(saved['context'], saved['source'], saved['results'], saved['cursor'],
        packed, saved['capture'], saved['typedRows'], saved['retainedStream'], saved['observed'], material)


def restore_packet(raw, *, core, syntax_facts=None, principal=None, syntax_context=None):
    """Native-first full historical replay; reconstruct only original transports.

    No live requirement, store, history, trees or owner observation is read.
    The actual protected caller must separately authenticate full packet custody
    and exact kernel mapping before any recovery or receipt effect.
    """
    from .evaluation_context import bind_retained
    from .pending_kernel import KernelRefused
    from .evaluation_terminal import TerminalRefused
    _, syntax_facts = _native_packet_result(raw, core=core, syntax_facts=syntax_facts,
        principal=principal, syntax_context=syntax_context)
    try:
        packet = restore_archive(raw)
        selections = {role: _restore_selection_transport(packet[role], core=core)
                      for role in ('primary', 'staged')}
        agent = packet['agent']
        if agent is not None:
            for role, selected in selections.items():
                if selected is not None:
                    bind_retained(core, selected, values=packet['values'],
                        subject=packet['subject'], candidate=packet['candidate'],
                        authoritative_requirement=packet['authoritativeRequirement'],
                        resulting_requirement=packet['resultingRequirement'],
                        authoritative_roots=packet['authoritativeRoots'], agent=agent,
                        agent_record=packet['agentRecord'], role=role,
                        prepared_cursor=packet['inputs'][role]['evaluationCursor'],
                        pending_store=selected.authority_material.pending_store)
        return CollapseObservation(packet['values'],
            None if selections['primary'] is None else selections['primary'].raw,
            None if selections['staged'] is None else selections['staged'].raw,
            agent, raw, packet.get('owner'), syntax_facts)
    except WorldlineError:
        raise
    except (KeyError, IndexError, AttributeError, TypeError, ValueError, OverflowError,
            KernelRefused, TerminalRefused) as exc:
        raise WorldlineError('RECOVERY_PACKET_MATERIAL_INVALID',
                            'complete native-verified transport could not be restored') from exc


def redecide_packet(raw, *, core, syntax_facts=None, principal=None, syntax_context=None):
    """Run the actual native full decision; this grants no protected custody."""
    return _native_packet(raw, core=core, syntax_facts=syntax_facts,
                          principal=principal, syntax_context=syntax_context)


def protected_historical_authority(raw, *, core):
    """Named fail-closed boundary until the actual protected principal exists.

    A caller may inspect/redecide packet data with the APIs above. No supplied
    Boolean, signature-shaped DTO, native verdict or daemon-owned file can turn
    it into protected historical authority through this endpoint.
    """
    raise WorldlineError('RECOVERY_PROTECTED_AUTHORITY_UNAVAILABLE',
        'the actual protected packet-custody and complete binding interface is not provisioned',
        {'open': ['protected-requester-binding', 'protected-resource-epoch-and-reservation',
                  'protected-capability-and-one-shot-custody', 'authenticated-historical-packet',
                  'protected-exact-kernel-mapping-identity']})
