"""Lossless explicit root/child DTOs; archive bytes confer no authority.

archive/restore_archive retain the original scoped root transport byte grammar.
The separate raw_archive/raw_restore_archive extend original operation-capture
tags, preserving raw snapshots and bytes dictionary keys without projection.
Native X5/load/mutation use scoped_archive/scoped_restore_archive explicitly.
No module or class named by a received record is ever imported.
"""
from dataclasses import fields
from .operation_capture import (
    _RECORDS as ORIGINAL_RECORDS,
    archive as original_archive,
    restore_archive as original_restore,
)
from .finalization_journal import encode, decode
from .model import WorldState
from .errors import WorldlineError
from .protected_startup import require


def _schema():
    # Fixed source dependencies only. Never derive this list from S._KNOWN:
    # extending the scoped registry cannot enroll an unknown root DTO.
    from . import resource_scoped_run_ledger as S
    from .resource_os_observation import PhysicalFacts
    from .resource_actor_admission import ActorNativeObservation, ActorCapability
    from .resource_actor_execution import ActorExecutionCrosswalk, ActorExecutionNativeDecision
    from .resource_child_schema import ProcessObservation, RootController, TaskOrigin, NamespaceObservation
    from .resource_child_execution import ResourceChildNativeObservation
    from .resource_actor_credentials import ActorCredentialObservation
    from .root_worker_credentials import RootCredentialObservation
    from .root_worker_prepared_inputs import PreparedInputs
    from .root_worker_prepared_wire import SnapshotWire, PreparedWire
    from .root_worker_retained_inputs import RetainedInputs
    from .protected_scoped_resource_service import ScopedSnapshot
    return (*ORIGINAL_RECORDS,
        S.ScopedState, S.ScopeFrame, S.PhysicalKey, S.PhysicalBucket,
        S.PhysicalProjection, S.CurrentObservation, S.ScopedIntent,
        S.ScopedPacket, S.ScopedNativeDecision, PhysicalFacts,
        ActorNativeObservation, ActorCapability, ActorExecutionCrosswalk,
        ActorExecutionNativeDecision, ProcessObservation, RootController,
        TaskOrigin, NamespaceObservation, ResourceChildNativeObservation,
        ActorCredentialObservation, RootCredentialObservation,
        PreparedInputs, SnapshotWire, PreparedWire, RetainedInputs, ScopedSnapshot)


def raw_archive(value):
    """Retain original raw tags plus the explicitly selected full root DTOs."""
    records = _schema()

    def lift(item):
        kind = type(item)
        if kind in records:
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
        if kind is int:
            magnitude = abs(item)
            return ['integer-magnitude', item < 0,
                    magnitude.to_bytes((magnitude.bit_length() + 7) // 8, 'little')]
        if item is None or kind in (bytes, bool, float, str):
            return ['atom', item]
        raise WorldlineError('RECOVERY_PACKET_TYPE', 'a full capture value has no original DTO grammar',
                            {'type': kind.__name__})

    return encode(lift(value))


def raw_restore_archive(raw):
    """Reconstruct only fixed local DTOs, requiring the entire canonical archive."""
    records = {(kind.__module__, kind.__name__): kind for kind in _schema()}

    def invalid():
        raise WorldlineError('ROOT_WORKER_COMPLETE_CODEC_ENCODING',
                            'the complete explicit root DTO grammar differs')

    def lower(item):
        if type(item) is not list or not item or type(item[0]) is not str:
            invalid()
        tag = item[0]
        if tag == 'integer-magnitude' and len(item) == 3:
            if type(item[1]) is not bool or type(item[2]) is not bytes:
                invalid()
            magnitude = int.from_bytes(item[2], 'little')
            return -magnitude if item[1] else magnitude
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
            return WorldState(value)
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
        if tag == 'atom' and (value is None or type(value) in (bytes, bool, float, str)):
            return value
        invalid()

    if type(raw) is not bytes:
        invalid()
    try:
        answer = lower(decode(raw))
        # Complete field order, object key order, integer magnitudes, nested
        # DTOs, byte contents and tuple/list distinctions must all survive.
        require(raw_archive(answer) == raw, 'ROOT_WORKER_COMPLETE_CODEC_ROUNDTRIP_DIFFERS')
        return answer
    except WorldlineError:
        raise
    except (KeyError, IndexError, AttributeError, TypeError, ValueError, OverflowError) as exc:
        raise WorldlineError('ROOT_WORKER_COMPLETE_CODEC_ENCODING',
                            'the complete explicit root DTO grammar differs') from exc


def scoped_archive(value):
    """Exact unchanged S tagged archive for native X5/load/mutation operands."""
    from . import resource_scoped_run_ledger as S
    # Load the fixed actor/child source declarations used by ordinary S callers.
    from . import resource_actor_execution, resource_child_execution
    return original_archive(S.record(value))


def scoped_restore_archive(raw):
    """Inverse native scoped transport; never reinterpret it as root DTO tags."""
    from . import resource_scoped_run_ledger as S
    from . import resource_actor_execution, resource_child_execution
    value = S.restore(original_restore(raw))
    require(scoped_archive(value) == raw, 'ROOT_WORKER_COMPLETE_CODEC_ROUNDTRIP_DIFFERS')
    return value


def archive(value):
    """Original root transport; complete raw operands must use raw_archive."""
    return scoped_archive(value)


def restore_archive(raw):
    """Original root transport inverse; no fallback to raw operation tags."""
    return scoped_restore_archive(raw)
