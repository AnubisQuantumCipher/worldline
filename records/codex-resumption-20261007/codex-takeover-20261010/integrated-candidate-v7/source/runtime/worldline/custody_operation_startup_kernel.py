"""Original complete operation-journal startup authority over actual custody input."""
from __future__ import annotations
import ctypes as C
from dataclasses import dataclass
from .errors import CoreUnavailable
from .protected_startup import require
from .retained_chain_kernel import _mapped


def _startup_control_input(owner, envelope, word):
    observer = getattr(owner, '_startup_control_capture', None)
    if observer is not None and observer.name == word:
        observer.input(envelope, word)


def _startup_control_decision(owner, result):
    observer = getattr(owner, '_startup_control_capture', None)
    if observer is not None and observer.name == result.name:
        observer.decision(result)


@dataclass(frozen=True)
class OperationJournalStartupObservation:
    status: int
    position: int
    envelope: bytes

    @property
    def state(self):
        require(self.status in (0, 1, 2), 'OPERATION_JOURNAL_NATIVE_STATUS_INVALID')
        return ('Refused', 'Stable', 'Finalize_Surviving_Next')[self.status]


def decide_journal(journal):
    from .root_worker_journal_v2 import RootCustodyJournalV2
    require(type(journal) is RootCustodyJournalV2,
            'OPERATION_JOURNAL_STARTUP_ACTUAL_CUSTODY_REQUIRED')
    journal.intact()
    try:
        function = journal.core._lib.wl_custody_operation_startup_decide_v2
    except AttributeError as error:
        raise CoreUnavailable('native complete operation-journal startup unavailable') from error
    function.argtypes = [C.c_void_p, C.c_size_t, C.POINTER(C.c_uint64), C.POINTER(C.c_uint64)]
    function.restype = C.c_int
    _mapped(journal, journal.core, (function,))
    with journal.lock:
        db = journal.connect()
        try:
            db.execute('BEGIN')
            envelope = journal.capture(db)
            require(type(envelope) is bytes and C.c_size_t(len(envelope)).value == len(envelope),
                    'OPERATION_JOURNAL_STARTUP_FULL_OWNED_ENVELOPE_REQUIRED')
            data = (C.c_ubyte * len(envelope)).from_buffer_copy(envelope)
            status = C.c_uint64(); position = C.c_uint64()
            code = function(data, len(envelope), C.byref(status), C.byref(position))
            if code != 0:
                raise CoreUnavailable('native operation-journal startup transport refused')
            result = OperationJournalStartupObservation(status.value, position.value, envelope)
            require(result.state != 'Refused', 'OPERATION_JOURNAL_COMPLETE_NATIVE_STARTUP_REFUSED')
            db.rollback()
        finally:
            db.close()
    _mapped(journal, journal.core, (function,))
    journal.intact()
    return result


@dataclass(frozen=True)
class OperationRecoveryObservation:
    status: int
    position: int
    envelope: bytes
    operation: str

    @property
    def state(self):
        require(self.status in range(7), 'OPERATION_RECOVERY_NATIVE_STATUS_INVALID')
        return ('Refused', 'NoRecovery', 'RetainUnresolved', 'RecoverCommitted',
                'RecoverOwnerResolution', 'RecoverFullBroker', 'RecoverK4')[self.status]


def decide_recovery_operation(journal, operation):
    """Native original route only; actual effect authorizers remain mandatory."""
    from .root_worker_journal_v2 import RootCustodyJournalV2
    require(type(journal) is RootCustodyJournalV2 and type(operation) is str,
            'OPERATION_RECOVERY_ACTUAL_CUSTODY_AND_TARGET_REQUIRED')
    journal.intact()
    try:
        function = journal.core._lib.wl_custody_operation_recovery_decide_v2
    except AttributeError as error:
        raise CoreUnavailable('native original operation recovery route unavailable') from error
    function.argtypes = [C.c_void_p, C.c_size_t, C.POINTER(C.c_uint64), C.POINTER(C.c_uint64)]
    function.restype = C.c_int
    _mapped(journal, journal.core, (function,))
    with journal.lock:
        db = journal.connect()
        try:
            db.execute('BEGIN')
            envelope = journal.capture(db, recovery_operation=operation)
            require(type(envelope) is bytes and C.c_size_t(len(envelope)).value == len(envelope),
                    'OPERATION_RECOVERY_FULL_OWNED_ENVELOPE_REQUIRED')
            data = (C.c_ubyte * len(envelope)).from_buffer_copy(envelope)
            status = C.c_uint64(); position = C.c_uint64()
            code = function(data, len(envelope), C.byref(status), C.byref(position))
            if code != 0:
                raise CoreUnavailable('native operation recovery route transport refused')
            result = OperationRecoveryObservation(status.value, position.value, envelope, operation)
            _mapped(journal, journal.core, (function,))
            repeated_status = C.c_uint64(); repeated_position = C.c_uint64()
            code = function(data, len(envelope), C.byref(repeated_status), C.byref(repeated_position))
            if code != 0:
                raise CoreUnavailable('native operation recovery route readback transport refused')
            require((repeated_status.value, repeated_position.value) == (result.status, result.position),
                    'OPERATION_RECOVERY_NATIVE_IMMUTABLE_INPUT_CHANGED')
            require(result.state != 'Refused', 'OPERATION_RECOVERY_COMPLETE_NATIVE_ROUTE_REFUSED')
            db.rollback()
        finally:
            db.close()
    _mapped(journal, journal.core, (function,))
    journal.intact()
    return result


@dataclass(frozen=True)
class StartupAdmissionObservation:
    status: int
    position: int
    envelope: bytes
    name: bytes

    @property
    def state(self):
        require(self.status in (0, 1, 2, 3), 'STARTUP_ADMISSION_NATIVE_STATUS_INVALID')
        return ('Refused', 'AlreadyConsumed', 'ConsumeUnusedExisting',
                'CompleteIntentExisting')[self.status]


def decide_admission(journal, name, profile):
    from .root_worker_journal_v2 import RootCustodyJournalV2
    require(type(journal) is RootCustodyJournalV2 and type(name) is str,
            'STARTUP_ADMISSION_ACTUAL_CUSTODY_AND_NAME_REQUIRED')
    journal.intact()
    word = name.encode('utf-8')
    require(C.c_size_t(len(word)).value == len(word), 'STARTUP_ADMISSION_NAME_HOST_EXTENT')
    try:
        function = journal.core._lib.wl_startup_admission_decide_v1
    except AttributeError as error:
        raise CoreUnavailable('native complete startup admission unavailable') from error
    function.argtypes = [C.c_void_p, C.c_size_t, C.c_void_p, C.c_size_t,
                         C.POINTER(C.c_uint64), C.POINTER(C.c_uint64)]
    function.restype = C.c_int
    _mapped(journal, journal.core, (function,))
    with journal.lock:
        db = journal.connect()
        try:
            db.execute('BEGIN')
            envelope = journal.capture(db, startup_admission=profile)
            require(type(envelope) is bytes and C.c_size_t(len(envelope)).value == len(envelope),
                    'STARTUP_ADMISSION_FULL_OWNED_ENVELOPE_REQUIRED')
            data = (C.c_ubyte * len(envelope)).from_buffer_copy(envelope)
            selected = (C.c_ubyte * len(word)).from_buffer_copy(word)
            status = C.c_uint64(); position = C.c_uint64()
            _startup_control_input(journal, envelope, word)
            code = function(data, len(envelope), selected, len(word),
                            C.byref(status), C.byref(position))
            if code != 0:
                raise CoreUnavailable('native startup admission transport refused')
            result = StartupAdmissionObservation(status.value, position.value, envelope, word)
            _startup_control_decision(journal, result)
            require(result.status in (0, 1, 2, 3), 'STARTUP_ADMISSION_NATIVE_STATUS_INVALID')
            db.rollback()
        finally:
            db.close()
    _mapped(journal, journal.core, (function,))
    journal.intact()
    return result


@dataclass(frozen=True)
class OperationAppendObservation:
    status: int
    position: int
    envelope: bytes
    candidate: bytes

    @property
    def state(self):
        require(self.status in (0, 1), 'OPERATION_APPEND_NATIVE_STATUS_INVALID')
        return ('Refused', 'AppendAllowed')[self.status]


def decide_append(journal, candidate):
    from .root_worker_journal_v2 import RootCustodyJournalV2
    require(type(journal) is RootCustodyJournalV2,
            'OPERATION_APPEND_ACTUAL_CUSTODY_REQUIRED')
    journal.intact()
    try:
        function = journal.core._lib.wl_custody_operation_append_decide_v2
    except AttributeError as error:
        raise CoreUnavailable('native complete operation append unavailable') from error
    function.argtypes = [C.c_void_p, C.c_size_t, C.POINTER(C.c_uint64), C.POINTER(C.c_uint64)]
    function.restype = C.c_int
    _mapped(journal, journal.core, (function,))
    with journal.lock:
        db = journal.connect()
        try:
            db.execute('BEGIN')
            envelope = journal.capture(db, operation_append_candidate=candidate)
            require(type(envelope) is bytes and C.c_size_t(len(envelope)).value == len(envelope),
                    'OPERATION_APPEND_FULL_OWNED_ENVELOPE_REQUIRED')
            data = (C.c_ubyte * len(envelope)).from_buffer_copy(envelope)
            status = C.c_uint64(); position = C.c_uint64()
            code = function(data, len(envelope), C.byref(status), C.byref(position))
            if code != 0:
                raise CoreUnavailable('native operation append transport refused')
            result = OperationAppendObservation(status.value, position.value, envelope, candidate['raw'])
            require(result.state == 'AppendAllowed', 'OPERATION_COMPLETE_NATIVE_APPEND_REFUSED')
            db.rollback()
        finally:
            db.close()
    _mapped(journal, journal.core, (function,))
    journal.intact()
    return result


@dataclass(frozen=True)
class StartupOwnerAdmissionObservation:
    status: int
    position: int
    envelope: bytes
    name: bytes

    @property
    def state(self):
        require(self.status in (0, 1, 2, 3, 4), 'STARTUP_OWNER_ADMISSION_NATIVE_STATUS_INVALID')
        return ('Refused', 'AlreadyConsumed', 'ConsumeUnusedExisting',
                'CompleteIntentExisting', 'Create_Unused_Offline')[self.status]


def admission_refusal(result):
    require(result.state == 'Refused', 'STARTUP_ADMISSION_REFUSAL_OBSERVATION_REQUIRED')
    reasons = ('STARTUP_NATIVE_ADMISSION_REFUSED', 'STARTUP_CONSUMED_JOURNAL_MISSING',
               'STARTUP_GENESIS_INTENT_MISSING_FILE_REVIEW_REQUIRED',
               'STARTUP_GENESIS_INTENT_BYTES_CHANGED', 'STARTUP_PREEXISTING_GENESIS_DIFFERS',
               'STARTUP_JOURNAL_INITIAL_ENVELOPE_CHANGED', 'STARTUP_AUTHORIZED_GENESIS_HEADS_CHANGED')
    require(result.position < len(reasons), 'STARTUP_ADMISSION_NATIVE_REASON_INVALID')
    return reasons[result.position]


def decide_owner_admission(lease, name, initial_envelope):
    from .protected_startup import StartupLease
    from .root_worker_codec import scoped_archive
    require(type(lease) is StartupLease and type(name) is str,
            'STARTUP_OWNER_ADMISSION_ACTUAL_LEASE_AND_NAME_REQUIRED')
    core = lease._owner_admission_core()
    try:
        function = core._lib.wl_startup_owner_admission_decide_v1
    except AttributeError as error:
        raise CoreUnavailable('native original owner admission unavailable') from error
    function.argtypes = [C.c_void_p, C.c_size_t, C.c_void_p, C.c_size_t,
                         C.POINTER(C.c_uint64), C.POINTER(C.c_uint64)]
    function.restype = C.c_int
    _mapped(lease, core, (function,))
    envelope = scoped_archive(lease._owner_admission_roster(name, initial_envelope))
    word = name.encode('utf-8')
    require(C.c_size_t(len(envelope)).value == len(envelope) and
            C.c_size_t(len(word)).value == len(word), 'STARTUP_OWNER_ADMISSION_HOST_EXTENT')
    data = (C.c_ubyte * len(envelope)).from_buffer_copy(envelope)
    selected = (C.c_ubyte * len(word)).from_buffer_copy(word)
    status = C.c_uint64(); position = C.c_uint64()
    _startup_control_input(lease, envelope, word)
    code = function(data, len(envelope), selected, len(word), C.byref(status), C.byref(position))
    if code != 0:
        raise CoreUnavailable('native original owner admission transport refused')
    result = StartupOwnerAdmissionObservation(status.value, position.value, envelope, word)
    _startup_control_decision(lease, result)
    require(result.status in (0, 1, 2, 3, 4), 'STARTUP_OWNER_ADMISSION_NATIVE_STATUS_INVALID')
    _mapped(lease, core, (function,))
    return result


@dataclass(frozen=True)
class StartupAdmissionTransitionObservation:
    status: int
    position: int
    before: object
    after: object


def verify_admission_transition(owner, before, after):
    from .protected_startup import StartupLease
    from .root_worker_journal_v2 import RootCustodyJournalV2
    if type(before) is StartupOwnerAdmissionObservation:
        require(type(after) is StartupOwnerAdmissionObservation and type(owner) is StartupLease,
                'STARTUP_OWNER_TRANSITION_ACTUAL_OBSERVATIONS_REQUIRED')
        core = owner._owner_admission_core()
        symbol = 'wl_startup_owner_admission_transition_v1'
    else:
        require(type(before) is StartupAdmissionObservation and
                type(after) is StartupAdmissionObservation and type(owner) is RootCustodyJournalV2,
                'STARTUP_TRANSITION_ACTUAL_OBSERVATIONS_REQUIRED')
        core = owner.core
        symbol = 'wl_startup_admission_transition_v1'
    require(before.name == after.name, 'STARTUP_TRANSITION_ACTUAL_NAME_CHANGED')
    try:
        function = getattr(core._lib, symbol)
    except AttributeError as error:
        raise CoreUnavailable('native complete startup admission transition unavailable') from error
    function.argtypes = [C.c_void_p, C.c_size_t, C.c_void_p, C.c_size_t,
                         C.c_void_p, C.c_size_t, C.c_uint64, C.c_uint64,
                         C.POINTER(C.c_uint64), C.POINTER(C.c_uint64)]
    function.restype = C.c_int
    _mapped(owner, core, (function,))
    old = (C.c_ubyte * len(before.envelope)).from_buffer_copy(before.envelope)
    new = (C.c_ubyte * len(after.envelope)).from_buffer_copy(after.envelope)
    name = (C.c_ubyte * len(before.name)).from_buffer_copy(before.name)
    status = C.c_uint64(); position = C.c_uint64()
    code = function(old, len(before.envelope), new, len(after.envelope), name, len(before.name),
                    before.status, after.status, C.byref(status), C.byref(position))
    if code != 0:
        raise CoreUnavailable('native startup admission transition transport refused')
    require(status.value in (0, 1), 'STARTUP_TRANSITION_NATIVE_STATUS_INVALID')
    result = StartupAdmissionTransitionObservation(status.value, position.value, before, after)
    observer = getattr(owner, '_startup_control_capture', None)
    if observer is not None and observer.name == before.name:
        observer.transition(result)
    _mapped(owner, core, (function,))
    return result
