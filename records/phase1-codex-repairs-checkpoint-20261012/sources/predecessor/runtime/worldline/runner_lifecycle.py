"""Transport actual owned acquisition facts to the sole native lifecycle gate."""
from __future__ import annotations

import ctypes

from .core import Core
from .errors import CoreUnavailable
from .finalization_journal import encode

_ACTIONS = {
    'quiescent': 0, 'finished': 1, 'drain-tails': 2, 'close-streams': 3,
    'release-guard': 4, 'stop-launcher': 5, 'observe-manager': 6,
    'proxy-ended': 7, 'command-ended': 8, 'streams-closed': 9,
    'guard-released': 10, 'cancellation-complete': 11,
    'query-publication': 12, 'recover-run': 13, 'start-run': 14,
    'mark-world-dead': 15, 'mark-job-dead': 16, 'forget-owner': 17,
    'stopped': 18,
    'membership': 19, 'capture-membership-protocol': 20,
    'route-controller': 21,
    'activate-timer': 22, 'capture-timer-protocol': 23,
    'stop-controller': 24, 'capture-controller-stop-protocol': 25,
}


def allowed(action, observation, *, core=None):
    core = Core.shared() if core is None else core
    try:
        call = core._lib.wl_runner_lifecycle_allowed_v1
    except AttributeError as exc:
        raise CoreUnavailable('selected kernel lacks complete runner lifecycle policy') from exc
    raw = encode(observation)
    owner = ctypes.create_string_buffer(raw, len(raw) + 1)
    length = len(raw)
    if ctypes.c_size_t(length).value != length:
        raise CoreUnavailable('runner acquisition extent does not fit size_t')
    call.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_uint8]
    call.restype = ctypes.c_uint8
    code = int(call(ctypes.cast(owner, ctypes.c_void_p), length, _ACTIONS[action]))
    if code not in (0, 1):
        raise CoreUnavailable('complete runner lifecycle native transport refused', status=code)
    return code == 1


def membership_capture(roster, requested, *, core=None):
    values = list(roster)
    if type(roster) is set and type(requested) is str and all(type(item) is str for item in values):
        capture = {'profile': 'builtin-set-string-v1', 'requested': requested, 'roster': values}
    else:
        def reference(value):
            return {'reference': id(value), 'typeReference': id(type(value))}
        capture = {'profile': 'python-actual-protocol-v1',
                   'requested': reference(requested), 'roster': [reference(item) for item in values],
                   'rosterType': reference(type(roster))}
    if allowed('capture-membership-protocol', capture, core=core):
        capture['protocolObservation'] = {'operator': 'contains',
                                         'returnedTruth': requested in roster}
    return capture
