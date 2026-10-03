"""Owned D30 transport. Only the Ada wire decides classification/admission.

The observation mapping is a required unproved producer boundary. Missing
confinement remains unmeasured; audit cleanliness never creates confinement.
"""
from __future__ import annotations
import ctypes
from dataclasses import dataclass
from typing import Mapping
from .core import (EVALUATION_ORIGINS, EVALUATION_STATUSES, EVALUATION_CHANNELS,
    EVALUATION_STAGES, EVALUATION_SUPERVISION, EVALUATION_EXECUTIONS,
    EVALUATION_OUTCOMES, EVALUATION_REPORTS, ROSTER_MAX, COLLAPSE_DECISIONS)
from .errors import CoreUnavailable, WorldlineError

U8 = ctypes.c_uint8
class Raw(ctypes.Structure):
    _fields_ = [('observations', U8 * 14), ('report_based', U8),
                ('report_facts', U8 * 14), ('presence', U8 * 5)]
class Classified(ctypes.Structure):
    _fields_ = [('status', U8), ('execution', U8), ('outcome', U8), ('bundle', U8)]
BUNDLES = ('NOT_COVERED', 'VERIFIED', 'COMPROMISED', 'UNKNOWN', 'UNBOUND')
REPORTS = tuple(EVALUATION_REPORTS)

@dataclass(frozen=True)
class OwnedRecord:
    raw: bytes
    confinement: int
    def __post_init__(self):
        if type(self.raw) is not bytes or len(self.raw) != ctypes.sizeof(Raw):
            raise CoreUnavailable('raw evaluation has wrong owned extent')
        if type(self.confinement) is not int or self.confinement not in (0, 1, 2):
            raise CoreUnavailable('invalid confinement observation')
    def native(self): return Raw.from_buffer_copy(self.raw)
    def transport(self): return {'raw': list(self.raw), 'confinement': self.confinement}

class Authority:
    def __init__(self, core):
        self.lib = core._lib
        version = self.lib.wl_evaluation_wire_version
        version.argtypes = []; version.restype = U8
        if version() != 1: raise CoreUnavailable('evaluation wire ABI differs')
        layout = self.lib.wl_evaluation_wire_layout
        layout.argtypes = [U8, U8]; layout.restype = ctypes.c_size_t
        for kind, record in enumerate((Raw, Classified)):
            if layout(kind, 0) != ctypes.sizeof(record) or layout(kind, 1) != ctypes.alignment(record):
                raise CoreUnavailable('evaluation wire layout differs')
            for field, (name, _type) in enumerate(getattr(record, '_fields_', ()), 2):
                if layout(kind, field) != getattr(record, name).offset:
                    raise CoreUnavailable('evaluation wire offset differs')
        for name, args in (
            ('classify', [ctypes.c_void_p, ctypes.c_void_p]),
            ('admit', [ctypes.c_void_p, U8]), ('report', [ctypes.c_void_p])):
            f = getattr(self.lib, 'wl_evaluation_wire_' + name)
            f.argtypes = args; f.restype = U8

    @staticmethod
    def checked(code):
        if code not in (0, 1): raise CoreUnavailable('typed evaluation wire refused malformed transport')
        return code == 1
    def evaluate(self, item: OwnedRecord):
        raw, out = item.native(), Classified()
        status = self.lib.wl_evaluation_wire_classify(ctypes.byref(raw), ctypes.byref(out))
        if status != 0 or out.status != 0: raise CoreUnavailable('typed raw classification refused')
        report = self.lib.wl_evaluation_wire_report(ctypes.byref(raw))
        if report not in range(len(REPORTS)): raise CoreUnavailable('typed report derivation refused')
        try:
            execution, outcome, bundle = EVALUATION_EXECUTIONS[out.execution], EVALUATION_OUTCOMES[out.outcome], BUNDLES[out.bundle]
        except IndexError as exc: raise CoreUnavailable('typed classification code invalid') from exc
        admitted = self.checked(self.lib.wl_evaluation_wire_admit(ctypes.byref(raw), item.confinement))
        return execution, outcome, bundle, REPORTS[report], admitted
    @staticmethod
    def restore(value):
        if type(value) is not dict or set(value) != {'raw', 'confinement'} or type(value['raw']) is not list:
            raise CoreUnavailable('missing complete raw evaluation transport')
        if any(type(x) is not int or not 0 <= x <= 255 for x in value['raw']):
            raise CoreUnavailable('raw evaluation byte invalid')
        return OwnedRecord(bytes(value['raw']), value['confinement'])
    def dependencies(self, request):
        call = self.lib.wl_collapse_raw_dependencies_v1
        call.argtypes, call.restype = [ctypes.c_void_p], U8
        code = int(call(ctypes.byref(request)))
        plans = {
            0: (True, False, False, False),
            1: (True, True, False, True),
            2: (True, False, True, True),
            3: (True, True, True, True),
            255: (False, False, False, False),
        }
        if code not in plans:
            raise CoreUnavailable('raw collapse dependency code invalid')
        valid, primary, staged, agent = plans[code]
        return {'valid': valid, 'primary': primary, 'staged': staged, 'agent': agent}

    def decide(self, request, primary, staged, agent):
        from .finalization_kernel import PreparedFinalization, decide_mixed
        if type(primary) is PreparedFinalization or type(staged) is PreparedFinalization:
            return decide_mixed(self, request, primary, staged, agent)
        # PreparedRawEvaluation owns complete raw rows, full byte identities,
        # arena and original journal request. No fixed D30 roster-count cap.
        from .raw_completion_kernel import PreparedRawEvaluation
        def args(value):
            if value is None: return (None, None, None, None)
            if type(value) is not PreparedRawEvaluation:
                raise CoreUnavailable('complete owned raw evaluation absent')
            return (*value.arguments(), None if value.metadata_context is None else ctypes.byref(value.metadata_context))
        # Never fall back to v2: that compatibility API lacks the independent
        # metadata-to-payload relation required by the default authority path.
        try:
            call = self.lib.wl_collapse_decide_raw_evaluation_v3
        except AttributeError as exc:
            raise CoreUnavailable('independent row metadata ABI unavailable') from exc
        call.argtypes = [ctypes.c_void_p] * 10 + [U8]
        call.restype = U8
        needs = self.dependencies(request)
        primary = primary if needs['primary'] else None
        staged = staged if needs['staged'] else None
        agent = agent if needs['agent'] else None
        owned_agent = None if agent is None else agent.native()
        code = int(call(ctypes.byref(request), *args(primary), *args(staged),
            None if owned_agent is None else ctypes.byref(owned_agent),
            0 if agent is None else agent.confinement))
        return COLLAPSE_DECISIONS.get(code, 'INVALID_REQUEST')

def missing_record(): return OwnedRecord(bytes(ctypes.sizeof(Raw)), 0)

def record(result, declared):
    from .completion_observations import observations
    from .finalize import evaluation_presence
    from .report_facts import report_facts
    facts = observations(result)
    # D27: unknown agent ceiling measurement is not supervised success.
    supervisor, stopped = facts.supervisor, facts.supervisor_stopped
    if facts.source == 'agent':
        resource = result.get('resources')
        ceiling = resource.get('ceilingFired') if isinstance(resource, Mapping) else None
        if ceiling is True: stopped = True
        elif ceiling is not False: supervisor = 'OTHER'
    isolation = result.get('profile') == 'private-evaluator-v1' and isinstance(result.get('evaluatorBoundary'), Mapping)
    f = report_facts(result)
    presence = evaluation_presence(result, declared)
    raw = Raw((U8 * 14)(EVALUATION_ORIGINS[facts.source], EVALUATION_STATUSES[facts.status],
        EVALUATION_CHANNELS[facts.channel], EVALUATION_STAGES[facts.stage], int(facts.exit_present),
        int(facts.exit_integer), EVALUATION_SUPERVISION[supervisor], int(stopped), int(facts.bundle_present),
        int(facts.bundle_is_mapping), int(facts.bundle_stable), int(facts.bundle_changed),
        int(facts.unsatisfied_imports), int(isolation)),
        int(result.get('format') in ('junit', 'gnatprove', 'worldline-benchmark-v1')),
        (U8 * 14)(*(int(x) for x in f)),
        (U8 * 5)(*(int(getattr(presence, name)) for name in presence.__dataclass_fields__)))
    # No current producer establishes complete v6 confinement. Neither a
    # report/audit label nor observed namespace equality may invent it.
    # This explicit unmeasured value blocks External promotion until the
    # required custody/confinement producer is implemented and reviewed.
    return OwnedRecord(bytes(raw), 0)
