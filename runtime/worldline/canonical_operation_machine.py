"""Replay exact genuine original machine admission under protected custody."""
from .protected_startup import require
from .resource_ledger import compute_ledger
from .resource_policy import decide_policy

def restore(value):
    from .protected_resource_runtime import lossless_data
    def lower(v):
        require(type(v) is dict and type(v.get('kind')) is str,'OPERATION_MACHINE_ENCODING_INVALID')
        kind=v['kind']
        if kind=='int-magnitude':
            require(set(v)=={'kind','negative','magnitude'} and type(v['negative']) is bool and type(v['magnitude']) is str,'OPERATION_MACHINE_INTEGER_INVALID')
            raw=bytes.fromhex(v['magnitude']);require(raw.hex()==v['magnitude'],'OPERATION_MACHINE_INTEGER_ENCODING_INVALID')
            n=int.from_bytes(raw,'little');return -n if v['negative'] else n
        require(set(v)=={'kind','value'},'OPERATION_MACHINE_FIELD_ROSTER_INVALID');raw=v['value']
        if kind=='NoneType':require(raw is None,'OPERATION_MACHINE_ABSENCE_INVALID');return None
        if kind in ('str','bool'):
            require(type(raw) is (str if kind=='str' else bool),'OPERATION_MACHINE_ATOM_INVALID');return raw
        if kind=='bytes':
            require(type(raw) is str,'OPERATION_MACHINE_BYTES_INVALID');result=bytes.fromhex(raw)
            require(result.hex()==raw,'OPERATION_MACHINE_BYTES_ENCODING_INVALID');return result
        if kind in ('list','tuple'):
            require(type(raw) is list,'OPERATION_MACHINE_ROSTER_INVALID');result=[lower(item) for item in raw]
            return result if kind=='list' else tuple(result)
        if kind=='dict':
            require(type(raw) is dict and all(type(key) is str for key in raw),'OPERATION_MACHINE_MAP_INVALID')
            return {key:lower(item) for key,item in raw.items()}
        raise ValueError('unsupported original machine atom')
    answer=lower(value);require(lossless_data(answer)==value,'OPERATION_MACHINE_NONCANONICAL');return answer

def replay_machine(principal,record,policy,reservation):
    p=principal;require(record['schema']=='worldline.protected-machine-admission-v1' and record['stage']=='DISPATCH'
        and record['reservation']==reservation.hex(),'OPERATION_MACHINE_BOUNDARY_CHANGED')
    p.resources.journal.load()
    require(any(event['cause']=='MACHINE_ADMISSION' and event['reservation']==reservation.hex()
        and event['payload']==record for event in p.resources.journal.events),'OPERATION_MACHINE_PROTECTED_CAPTURE_ABSENT')
    require(restore(record['policy'])==policy.canonical(),'OPERATION_MACHINE_ORIGINAL_POLICY_CHANGED')
    ledger=compute_ledger(restore(record['ledger_input']),core=p.core)
    require(restore(record['ledger_result'])=={'total':ledger.total,'withheld':ledger.withheld},'OPERATION_MACHINE_FULL_LEDGER_REDECISION_CHANGED')
    inputs=restore(record['native_input']);require(inputs['withheld_memory']==ledger.total,'OPERATION_MACHINE_PROJECTED_WITHHELD_CHANGED')
    native=decide_policy(**inputs,core=p.core)
    require(record['native_output']=={'gate':native.gate,'disk_index':native.disk_index} and native.ready,
        'OPERATION_MACHINE_NATIVE_FLOOR_REFUSED')
    # Measurement-to-unit/full-row/parser/stability correspondence is retained
    # by the actual independent producer and remains a full proof obligation.
    return record
