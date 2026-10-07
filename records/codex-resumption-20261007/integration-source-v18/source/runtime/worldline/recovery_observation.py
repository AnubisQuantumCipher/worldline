"""Complete owned collapse observation, separately from its native verdict.

This packet is a lossless archive of the values and their full retained raw
materials. Its custody must come from an actual protected producer; that integration is
open. The daemon's ability to produce/replay a packet cannot issue a witness.
Historical replay uses the retained inputs; fresh observation remains separate.
"""
from __future__ import annotations

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
                   resulting_requirement, authoritative_roots, current_requirement=None, owner=None):
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
    return archive(packet)


@dataclass(frozen=True, slots=True)
class CollapseObservation:
    values: CollapseInput
    primary: object
    staged: object
    agent: object
    packet: bytes | None
    owner: object = None

    def decide(self, core):
        if type(self.values) is not CollapseInput:
            raise WorldlineError('RECOVERY_OBSERVATION_INVALID', 'the complete owned observation is absent')
        # Keep this object, and every original prepared raw arena it references,
        # alive throughout the synchronous native call. No projected verdict.
        original=core.collapse_decide_with_evaluation(self.values,primary=self.primary,staged=self.staged,agent=self.agent)
        if original!='AUTHORIZED' or self.owner is None:return original
        if type(self.owner) is not OwnerCollapseData:raise WorldlineError('OWNER_PACKET_TYPE','owner conjunction data differs')
        reason=self.owner.decide(core,self.values)
        return 'AUTHORIZED' if reason=='READY' else 'OWNER_'+reason


_PACKET_FIELDS = frozenset(('schema', 'values', 'primary', 'staged', 'agent',
    'agentRecord', 'inputs', 'candidate', 'subject', 'witness',
    'authoritativeRequirement', 'currentRequirementArgument', 'resultingRequirement',
    'authoritativeRoots'))
_SELECTED_FIELDS = frozenset(('context', 'source', 'results', 'cursor', 'capture',
    'typedRows', 'retainedStream', 'observed', 'authorityMaterial'))


def restore_packet(raw, *, core):
    """Restore owned native arenas and replay the original complete decision.

    This API accepts data only. The caller must authenticate the complete packet
    and kernel mapping in protected custody before using this observation for
    recovery authority. It never reads today's policy, history, store or trees.
    """
    from .evaluation_authority import read_material
    from .evaluation_context import bind_retained
    from .evaluation_wire import record as raw_record
    from .finalize import ENGINE_DECLARATIONS, runner_agent_record
    from .pending_kernel import KernelRefused
    from .evaluation_terminal import TerminalRefused

    def invalid(detail):
        raise WorldlineError('RECOVERY_PACKET_SCHEMA', detail)

    try:
        packet = restore_archive(raw)
        if (type(packet) is not dict or not ((set(packet)==_PACKET_FIELDS and packet.get('schema')=='worldline-collapse-observation-v2') or
                (set(packet)==_PACKET_FIELDS|{'owner'} and packet.get('schema')=='worldline-collapse-observation-v3-owner' and type(packet['owner']) is OwnerCollapseData))):
            invalid('the complete recovery packet schema differs')
        values, inputs = packet['values'], packet['inputs']
        subject, candidate = packet['subject'], packet['candidate']
        if (type(values) is not CollapseInput or type(inputs) is not dict
                or type(subject) is not World or type(candidate) is not World
                or type(packet['authoritativeRequirement']) is not dict
                or type(packet['authoritativeRoots']) is not tuple):
            invalid('a complete recovery observation has an unexpected DTO type')
        needs = core.collapse_raw_dependencies(values)
        primary = inputs.get('primary') if isinstance(inputs.get('primary'), dict) else {}
        staged = inputs.get('staged') if isinstance(inputs.get('staged'), dict) else {}
        selections = {}
        for role, required, prepared in (
                ('primary', needs['primary'], primary),
                ('staged', needs['staged'] and staged.get('ran') is True, staged)):
            saved = packet[role]
            if not required:
                if saved is not None:
                    invalid('an unused evaluation was substituted into the original observation')
                selections[role] = None
                continue
            if (type(saved) is not dict or set(saved) != _SELECTED_FIELDS
                    or type(saved['authorityMaterial']) is not AuthorityMaterial):
                raise WorldlineError('RECOVERY_PACKET_MATERIAL',
                                    'complete retained raw authority material is absent')
            cursor = prepared.get('evaluationCursor')
            if cursor is None:
                raise WorldlineError('EVALUATION_CURSOR_ABSENT' if role == 'primary'
                                    else 'STAGED_EVALUATION_CURSOR_ABSENT',
                                    'the original prepared evidence cursor is absent')
            owner=packet.get('owner')
            if role=='primary' and type(owner) is OwnerCollapseData and owner.mode=='RETRY_EVALUATION':
                if owner.world!=subject or owner.after_material!=saved['authorityMaterial'] or owner.prepared!=cursor:
                    invalid('owner full retained material/subject/prepared cursor differs')
                selected=owner.selected(core)
            else:
                selected = read_material(subject, packet['currentRequirementArgument'],
                    saved['authorityMaterial'], prepared=cursor, core=core)
            replayed = {'context': selected.context, 'source': selected.source,
                'results': selected.results, 'cursor': selected.cursor,
                'capture': selected.capture, 'typedRows': selected.typed_rows,
                'retainedStream': selected.retained_stream, 'observed': selected.observed,
                'authorityMaterial': selected.authority_material}
            # This exact transport correspondence is not a Python permission
            # decision: the full native history/row/context gates still decide.
            if archive(replayed) != archive(saved):
                raise WorldlineError('RECOVERY_PACKET_SELECTION_CHANGED',
                                    'the complete retained selection differs on native replay')
            selections[role] = selected
        agent, actual_agent = None, None
        if needs['agent']:
            final = subject.evidence.get('checks') if isinstance(subject.evidence, dict) else None
            actual_agent = next((row for row in (final or ())
                if isinstance(row, dict) and row.get('id') == 'agent'), None)
            actual_agent, _legacy = runner_agent_record(actual_agent)
            if isinstance(actual_agent, dict) and actual_agent.get('origin') == 'agent':
                agent = raw_record(actual_agent, ENGINE_DECLARATIONS['agent'])
        if archive(agent) != archive(packet['agent']) or archive(actual_agent) != archive(packet['agentRecord']):
            raise WorldlineError('RECOVERY_PACKET_AGENT_CHANGED',
                                'the actual retained agent projection differs')
        if agent is not None:
            for role, prepared in (('primary', primary), ('staged', staged)):
                selected = selections[role]
                if selected is not None:
                    bind_retained(core, selected, values=values, subject=subject, candidate=candidate,
                        authoritative_requirement=packet['authoritativeRequirement'],
                        resulting_requirement=packet['resultingRequirement'],
                        authoritative_roots=packet['authoritativeRoots'], agent=agent,
                        agent_record=actual_agent, role=role,
                        prepared_cursor=prepared.get('evaluationCursor'),
                        pending_store=selected.authority_material.pending_store)
        return CollapseObservation(values,
            None if selections['primary'] is None else selections['primary'].raw,
            None if selections['staged'] is None else selections['staged'].raw, agent, raw, packet.get('owner'))
    except WorldlineError:
        raise
    except (KeyError, IndexError, AttributeError, TypeError, ValueError, OverflowError,
            KernelRefused, TerminalRefused) as exc:
        raise WorldlineError('RECOVERY_PACKET_MATERIAL_INVALID',
                            'complete retained raw authority could not be restored') from exc


def redecide_packet(raw, *, core):
    """Run the actual native full decision; this grants no protected custody."""
    return restore_packet(raw, core=core).decide(core)


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
