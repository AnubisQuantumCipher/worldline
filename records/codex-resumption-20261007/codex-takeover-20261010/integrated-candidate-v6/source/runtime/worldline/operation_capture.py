"""Lossless explicit canonical-operation DTOs; bytes alone confer no custody.

Original packet grammar/classes stay untouched. This additive grammar lists the
actual full resource records explicitly; no import/eval/default/coercion decoder.
"""
from dataclasses import fields
from .recovery_observation import _RECORDS as ORIGINAL_RECORDS
from .resource_run_ledger import (RunContext,RunBinding,RunState,RunRow,RunRequest,RunObservation)
from .recovery_authority_kernel_v3 import BoundUse,NativeObservation
from .model import WorldState
from .finalization_journal import encode,decode
from .errors import WorldlineError
_RECORDS=(*ORIGINAL_RECORDS,RunContext,RunBinding,RunState,RunRow,RunRequest,RunObservation,BoundUse,NativeObservation)

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
        if kind is int:
            magnitude=abs(item)
            return ['integer-magnitude',item<0,magnitude.to_bytes((magnitude.bit_length()+7)//8,'little')]
        if item is None or kind in (bytes, bool, float, str):
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
        if tag=='integer-magnitude' and len(item)==3:
            if type(item[1]) is not bool or type(item[2]) is not bytes:invalid()
            value=int.from_bytes(item[2],'little')
            answer=-value if item[1] else value
            if archive(answer)!=encode(item):invalid()
            return answer
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
        if tag == 'atom' and (value is None or type(value) in (bytes, bool, float, str)):
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

