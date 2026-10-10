"""Exact owner-acquired operation snapshot -> original native DTO preparation.

This module makes no custody event, write, native call, or authorization verdict.
The acquisition function invokes the original full protected journal loader via
capture_prepared_inputs; standalone encoding is deliberately a value operation.
Native archive equality, complete X5 fold and sole-C_API entry remain OPEN.
"""
from dataclasses import dataclass
import ctypes as C
from .errors import WorldlineError
from .operation_capture import archive, restore_archive
from .operation_authority_kernel import OperationAuthorityKernel, Arena, keys
from .protected_startup import require, private_bytes
from .root_worker_prepared_inputs import PreparedInputs, capture_prepared_inputs

@dataclass(frozen=True)
class SnapshotWire:
    request: bytes
    # Native roster order is grants, uses, receipts, events; each count belongs
    # to its complete bytes, including empty rosters. No selected-tail removal.
    rosters: tuple[bytes, ...]
    counts: tuple[int, ...]

@dataclass(frozen=True)
class PreparedWire:
    retained: PreparedInputs
    arena: bytes
    reserve: SnapshotWire
    intent: SnapshotWire


def _snapshot(raw):
    require(type(raw) is bytes and bool(raw), 'PREPARED_SNAPSHOT_ABSENT')
    value = restore_archive(raw)
    keys(value, ('binding', 'grants', 'uses', 'now', 'evidence', 'receipts', 'events'))
    require(archive(value) == raw, 'PREPARED_SNAPSHOT_ARCHIVE_CHANGED')
    return value


def _prepare_pair(kernel, reserve_raw, intent_raw, custody_prefix):
    """Value-only encoder. A returned pair is NOT protected provenance."""
    require(type(kernel) is OperationAuthorityKernel, 'PREPARED_ORIGINAL_KERNEL_REQUIRED')
    require(type(custody_prefix) is bytes, 'PREPARED_ARENA_BYTES_REQUIRED')
    try:
        reserve, intent = _snapshot(reserve_raw), _snapshot(intent_raw)
        require(archive(reserve['binding']) == archive(intent['binding']),
                'PREPARED_OPERATION_BINDING_CHANGED')
        require(archive(reserve['grants']) == archive(intent['grants']),
                'PREPARED_OPERATION_GRANTS_CHANGED')
        # One original arena ensures both snapshots refer to the same bytes;
        # its explicit prefix preserves custody-event spans when the eventual
        # authenticated boundary enrolls them. No quantity is clipped/coerced.
        arena = Arena()
        arena.raw.extend(custody_prefix)
        def prepare(value):
            request, actual_arena, arrays = kernel.prepare(value, 'RESERVE_USE', arena=arena)
            require(actual_arena is arena, 'PREPARED_ARENA_IDENTITY_CHANGED')
            return SnapshotWire(C.string_at(C.byref(request), C.sizeof(request)),
                tuple(C.string_at(a, C.sizeof(a)) for a in arrays),
                tuple(len(a) for a in arrays))
        r = prepare(reserve)
        i = prepare(intent)
        return bytes(arena.raw), r, i
    except (ValueError, TypeError, KeyError, OverflowError) as exc:
        raise WorldlineError('PREPARED_SNAPSHOT_MALFORMED',
                            'the complete original native snapshot schema differs') from exc


def capture_prepared_wire(owner, operation, *, custody_prefix=b''):
    retained = capture_prepared_inputs(owner, operation)
    arena, reserve, intent = _prepare_pair(owner.principal.kernel,
        retained.reserved_snapshot, retained.effect_intent_snapshot, custody_prefix)
    owner.intact()
    journal = owner.principal.journal
    require(private_bytes(journal.path) == retained.journal_raw and
            tuple(journal.head_row()) == retained.admission_head,
            'PREPARED_OPERATION_CAPTURE_CHANGED')
    return PreparedWire(retained, arena, reserve, intent)
