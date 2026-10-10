"""Owned complete original startup inputs; native alone decides bootstrap actions."""
from __future__ import annotations
import ctypes as C
from dataclasses import dataclass
from .errors import CoreUnavailable
from .protected_startup import require
from .retained_chain_kernel import _mapped
from .root_worker_codec import archive

REFUSALS = {
    0: 'STARTUP_NATIVE_ADMISSION_REFUSED',
    1: 'STARTUP_CONSUMED_JOURNAL_MISSING',
    2: 'STARTUP_GENESIS_INTENT_MISSING_FILE_REVIEW_REQUIRED',
    3: 'STARTUP_GENESIS_INTENT_BYTES_CHANGED',
    4: 'STARTUP_PREEXISTING_GENESIS_DIFFERS',
    5: 'STARTUP_JOURNAL_INITIAL_ENVELOPE_CHANGED',
    6: 'STARTUP_AUTHORIZED_GENESIS_HEADS_CHANGED',
}

@dataclass(frozen=True)
class AdmissionObservation:
    status: int
    position: int
    envelope: bytes
    @property
    def refusal(self):
        return REFUSALS.get(self.position, 'STARTUP_NATIVE_ADMISSION_REFUSED')

def _bytes(value):
    require(type(value) is bytes and C.c_size_t(len(value)).value == len(value),
            'STARTUP_ADMISSION_OWNED_BYTE_EXTENT')
    return (C.c_ubyte * len(value)).from_buffer_copy(value)

def _function(native, name, transition=False):
    try: function = getattr(native, name)
    except AttributeError as error: raise CoreUnavailable(name + ' unavailable') from error
    arguments = [C.c_void_p, C.c_size_t]
    if transition: arguments += [C.c_void_p, C.c_size_t]
    arguments += [C.c_void_p, C.c_size_t]
    if transition: arguments += [C.c_uint64, C.c_uint64]
    function.argtypes = arguments + [C.POINTER(C.c_uint64), C.POINTER(C.c_uint64)]
    function.restype = C.c_int
    return function

def _decide(function, envelope, name):
    require(type(name) is str, 'STARTUP_ADMISSION_ACTUAL_NAME_REQUIRED')
    encoded = name.encode('utf-8'); data = _bytes(envelope); word = _bytes(encoded)
    status = C.c_uint64(); position = C.c_uint64()
    code = function(data, len(envelope), word, len(encoded), C.byref(status), C.byref(position))
    if code != 0: raise CoreUnavailable('startup admission native transport refused')
    return AdmissionObservation(status.value, position.value, envelope)

def _transition(function, before, after, name, before_action, after_action):
    require(type(name) is str, 'STARTUP_ADMISSION_ACTUAL_NAME_REQUIRED')
    require(type(before_action) is int and type(after_action) is int and
            C.c_uint64(before_action).value == before_action and
            C.c_uint64(after_action).value == after_action, 'STARTUP_ADMISSION_NATIVE_ACTION_EXTENT')
    encoded = name.encode('utf-8'); b = _bytes(before); a = _bytes(after); word = _bytes(encoded)
    status = C.c_uint64(); position = C.c_uint64()
    code = function(b, len(before), a, len(after), word, len(encoded), before_action,
                    after_action, C.byref(status), C.byref(position))
    if code != 0: raise CoreUnavailable('startup transition native transport refused')
    return status.value == 1 and position.value == 0

def decide_admission(journal, name, profile):
    from .root_worker_journal_v2 import RootCustodyJournalV2
    require(type(journal) is RootCustodyJournalV2, 'STARTUP_ADMISSION_REAL_CUSTODY_JOURNAL_REQUIRED')
    journal.intact()
    function = _function(journal.core._lib, 'wl_startup_admission_decide_v1')
    _mapped(journal, journal.core, (function,))
    db = journal.connect()
    try:
        db.execute('BEGIN')
        try: envelope = journal.capture(db, startup_admission=profile)
        finally: db.execute('ROLLBACK')
    finally: db.close()
    result = _decide(function, envelope, name)
    _mapped(journal, journal.core, (function,)); journal.intact()
    return result

def decide_owner(lease, core, name, roster):
    from .protected_startup import StartupLease
    require(type(lease) is StartupLease, 'STARTUP_ADMISSION_REAL_ORIGINAL_OWNER_REQUIRED')
    lease.intact()
    function = _function(core._lib, 'wl_startup_owner_admission_decide_v1')
    _mapped(lease, core, (function,))
    result = _decide(function, archive(roster), name)
    _mapped(lease, core, (function,)); lease.intact()
    return result

def transition_admission(journal, before, after, name, before_action, after_action):
    from .root_worker_journal_v2 import RootCustodyJournalV2
    require(type(journal) is RootCustodyJournalV2, 'STARTUP_ADMISSION_REAL_CUSTODY_JOURNAL_REQUIRED')
    function = _function(journal.core._lib, 'wl_startup_admission_transition_v1', True)
    _mapped(journal, journal.core, (function,))
    result = _transition(function, before, after, name, before_action, after_action)
    _mapped(journal, journal.core, (function,)); journal.intact()
    return result

def transition_owner(lease, core, before, after, name, before_action, after_action):
    from .protected_startup import StartupLease
    require(type(lease) is StartupLease, 'STARTUP_ADMISSION_REAL_ORIGINAL_OWNER_REQUIRED')
    function = _function(core._lib, 'wl_startup_owner_admission_transition_v1', True)
    _mapped(lease, core, (function,))
    result = _transition(function, before, after, name, before_action, after_action)
    _mapped(lease, core, (function,)); lease.intact()
    return result
